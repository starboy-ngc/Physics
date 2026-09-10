"""Les garde-fous du moteur, un par un.

Ce sont les lignes qui ne servent jamais — jusqu'au jour ou elles servent :
une population vide, un quartile impossible a poser, deux onglets de meme
nom, une etendue nulle sur un axe. Aucune ne portait de test, et un
garde-fou sans test est un garde-fou qu'on supprime un jour par
inadvertance, en le prenant pour du code mort.

Aucune donnee RH reelle.
"""

import datetime as _dt
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from compensation_analytics.core import axes, metrics
from compensation_analytics.core import statistics_engine as stats
from compensation_analytics.core.hierarchy import Tree
from compensation_analytics.core.mapping import resolve_mapping
from compensation_analytics.core.normalize import Employee, Population
from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.core.segmentation import _as_list
from compensation_analytics.io.xlsx_writer import write_workbook


class TestStatisticsOnNothing(unittest.TestCase):
    """Une population vide ne doit rien rendre, et surtout pas zero."""

    def test_every_indicator_answers_nothing(self):
        for function in (stats.total, stats.mean, stats.median,
                         stats.minimum, stats.maximum,
                         stats.standard_deviation):
            self.assertIsNone(function([]), function.__name__)

    def test_a_single_value_has_no_standard_deviation(self):
        """L'ecart-type d'echantillon divise par n-1 : sur une valeur, il
        n'existe pas. Rendre zero ferait croire a une population homogene."""
        self.assertIsNone(stats.standard_deviation([42.0]))

    def test_a_single_value_is_its_own_percentile(self):
        self.assertEqual(stats.percentile([42.0], 10), 42.0)
        self.assertEqual(stats.percentile([42.0], 90), 42.0)

    def test_counting_is_counting(self):
        self.assertEqual(stats.count([]), 0)
        self.assertEqual(stats.count([1.0, 2.0]), 2)

    def test_a_ratio_over_nothing_is_nothing(self):
        self.assertIsNone(stats.ratio(1.0, 0))
        self.assertIsNone(stats.ratio(1.0, None))
        self.assertIsNone(stats.ratio(None, 1.0))

    def test_outlier_bounds_need_enough_values(self):
        """Sous quatre valeurs, un quartile ne veut rien dire : mieux vaut
        ne rien reperer que designer un salarie sur trois."""
        self.assertIsNone(stats.iqr_outlier_bounds([]))
        self.assertIsNone(stats.iqr_outlier_bounds([1.0, 2.0, 3.0]))
        bounds = stats.iqr_outlier_bounds([1.0, 2.0, 3.0, 4.0])
        self.assertIsNotNone(bounds)
        self.assertLess(bounds["lower"], bounds["upper"])

    def test_the_outlier_factor_widens_the_bounds(self):
        values = [float(index) for index in range(20)]
        narrow = stats.iqr_outlier_bounds(values, 1.5)
        wide = stats.iqr_outlier_bounds(values, 3.0)
        self.assertLess(wide["lower"], narrow["lower"])
        self.assertGreater(wide["upper"], narrow["upper"])

    def test_an_infinite_value_is_left_out(self):
        """Elle vient d'une division par zero dans le tableur source, et
        une moyenne qui la contient vaut l'infini."""
        self.assertEqual(stats.clean([1.0, float("inf"), float("-inf"), 2.0]),
                         [1.0, 2.0])


class TestAxes(unittest.TestCase):
    def test_a_range_of_nothing_still_gives_a_step(self):
        """Une population dont tous les salaires sont egaux : l'axe doit
        quand meme se graduer."""
        self.assertGreater(axes.nice_step(0, 4), 0)
        self.assertGreater(axes.nice_step(-5, 4), 0)

    def test_no_tick_is_asked_for_no_tick(self):
        self.assertGreater(axes.nice_step(100, 0), 0)

    def test_equal_bounds_give_usable_ticks(self):
        ticks = axes.nice_ticks(1000, 1000)
        self.assertIsInstance(ticks, list)


class TestSegmentationHelpers(unittest.TestCase):
    def test_a_lone_value_becomes_a_list_of_one(self):
        self.assertEqual(_as_list("G5"), ["G5"])
        self.assertEqual(_as_list(5), [5])

    def test_a_list_stays_a_list(self):
        self.assertEqual(_as_list(["G5", "G6"]), ["G5", "G6"])
        self.assertEqual(sorted(_as_list({"G5"})), ["G5"])


class TestMappingHelpers(unittest.TestCase):
    def test_a_field_is_known_or_it_is_not(self):
        from tests.support import HEADERS

        mapping = resolve_mapping(list(HEADERS), make_config())
        self.assertTrue(mapping.has("base_salary"))
        self.assertFalse(mapping.has("inexistant"))

    def test_a_column_without_a_name_is_skipped(self):
        mapping = resolve_mapping(["Matricule", "", "   ", "Salaire de base"],
                                  make_config())
        self.assertTrue(mapping.has("employee_id"))
        self.assertEqual(mapping.unknown_columns, [])


class TestMetricsGuards(unittest.TestCase):
    def test_the_sex_of_nobody_is_unknown(self):
        self.assertEqual(metrics._sex_of(Employee(row_number=1), None),
                         "unknown")

    def test_a_missing_salary_is_never_an_outlier(self):
        """Elle ne vaut pas zero : elle ne vaut rien."""
        config = make_config()
        rows = [make_row(index, salary=40000 + index * 10) for index in range(30)]
        rows.append(make_row(99, salary=None))
        distribution = metrics.calculate_distribution_metrics(
            build_population(rows, config), config)
        references = [item["reference"] for item in distribution["outliers"]]
        self.assertNotIn("E00099", references)


class TestHierarchyGuards(unittest.TestCase):
    def test_an_unknown_identifier_has_no_level(self):
        tree = Tree(Population([Employee(row_number=1, employee_id="A")]))
        self.assertEqual(tree.depth("INCONNU"), 0)
        self.assertEqual(tree.line("INCONNU"), [])

    def test_a_diamond_counts_each_person_once(self):
        """Deux chemins vers la meme personne — un export incoherent la
        rattache deux fois — ne doivent pas la compter deux fois dans
        l'equipe totale, sinon l'effectif depasse le fichier."""
        people = Population([
            Employee(row_number=1, employee_id="A"),
            Employee(row_number=2, employee_id="B", manager="A"),
            Employee(row_number=3, employee_id="C", manager="A"),
            Employee(row_number=4, employee_id="D", manager="B"),
        ])
        tree = Tree(people)
        tree.children["C"].append("D")          # second rattachement
        total = tree.total("A")
        self.assertEqual(len(total), len({person.employee_id
                                          for person in total}))


class TestWorkbookGuards(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def test_two_sheets_of_the_same_name_are_told_apart(self):
        """Excel refuse d'ouvrir un classeur a deux onglets homonymes."""
        path = os.path.join(self.directory, "double.xlsx")
        write_workbook(path, [("Seg Grade", [["A"]]), ("Seg Grade", [["B"]]),
                              ("Seg Grade", [["C"]])])
        import zipfile
        from xml.etree import ElementTree

        with zipfile.ZipFile(path) as archive:
            book = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        names = [node.get("name") for node in book.iter(
            "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet")]
        self.assertEqual(len(names), 3)
        self.assertEqual(len(set(names)), 3)

    def test_a_workbook_without_a_sheet_is_refused(self):
        with self.assertRaises(ValueError):
            write_workbook(os.path.join(self.directory, "vide.xlsx"), [])

    def test_a_datetime_is_written_like_a_date(self):
        from compensation_analytics.io.tabular import read_table

        path = os.path.join(self.directory, "horodate.xlsx")
        write_workbook(path, [("P", [["Quand"],
                                     [_dt.datetime(2026, 1, 31, 9, 30)]])])
        self.assertEqual(read_table(path).rows[0][0], _dt.date(2026, 1, 31))


class TestResultShape(unittest.TestCase):
    def test_the_result_hands_out_its_payload(self):
        directory = tempfile.mkdtemp()
        path = os.path.join(directory, "p.csv")
        import csv

        from tests.support import HEADERS

        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(HEADERS)
            for index in range(10):
                writer.writerow(list(make_row(index)))
        result = run_analysis(AnalysisRequest(source_path=path))
        self.assertIs(result.as_dict(), result.payload)


if __name__ == "__main__":
    unittest.main()
