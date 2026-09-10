"""Le classeur Excel, onglet par onglet — et ses formules.

Un classeur d'agregats demande de croire l'outil sur parole. C'est pourquoi
les indicateurs derives portent leur formule et qu'un onglet « Controle »
recalcule mediane et percentiles par le tableur lui-meme. Encore faut-il que
ces formules citent les bonnes cellules : une formule fausse est pire qu'une
valeur nue, parce qu'elle a l'air d'une preuve.

Le classeur produit est relu ici comme Excel le lirait — par son XML — et
non par le lecteur de l'outil : sinon on ne verifierait que l'accord de
l'ecrivain avec lui-meme.

Aucune donnee RH reelle.
"""

import os
import re
import sys
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, REFERENCE_DATE, build_population, make_config, make_row
from compensation_analytics.core.export import build_sheets, export_excel
from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.io.xlsx_writer import Formula, write_workbook

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_workbook(path):
    """Relit un classeur comme Excel le ferait : noms d'onglets, cellules,
    formules et valeurs en cache."""
    sheets = {}
    with zipfile.ZipFile(path) as archive:
        book = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        names = [node.get("name") for node in book.iter(f"{NS}sheet")]
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            table = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(part.text or "" for part in item.iter(f"{NS}t"))
                      for item in table.findall(f"{NS}si")]
        for index, name in enumerate(names, start=1):
            sheet = ElementTree.fromstring(
                archive.read(f"xl/worksheets/sheet{index}.xml"))
            cells = {}
            for cell in sheet.iter(f"{NS}c"):
                reference = cell.get("r")
                formula = cell.find(f"{NS}f")
                value = cell.find(f"{NS}v")
                raw = value.text if value is not None else None
                if cell.get("t") == "s" and raw is not None:
                    raw = shared[int(raw)]
                elif cell.get("t") == "inlineStr":
                    node = cell.find(f"{NS}is")
                    raw = "".join(part.text or ""
                                  for part in node.iter(f"{NS}t")) \
                        if node is not None else ""
                cells[reference] = (
                    formula.text if formula is not None else None, raw)
            sheets[name] = cells
    return sheets


def column_values(cells, letter):
    """Valeurs d'une colonne, dans l'ordre des lignes."""
    rows = sorted((int(reference[len(letter):]), value)
                  for reference, (_f, value) in cells.items()
                  if reference.startswith(letter)
                  and reference[len(letter):].isdigit())
    return [value for _number, value in rows]


class WorkbookCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def analyse(self, rows=60, overrides=None, filters=None, comparison=None):
        import csv

        path = os.path.join(self.directory, "p.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste"])
            for index in range(rows):
                writer.writerow(list(make_row(
                    index, salary=30000 + index * 900,
                    business_unit=["France", "Iberia"][index % 2],
                    grade=f"G{3 + index % 4}",
                    gender="F" if index % 2 else "H"))
                    # Le poste ne suit pas le sexe : sinon chaque poste
                    # n'aurait qu'un seul sexe et aucun ecart ne serait
                    # publiable.
                    + [["Comptable", "Technicien"][(index // 2) % 2]])
        self.config_dir = os.path.join(self.directory, "config")
        from compensation_analytics.core.config import write_default_configuration
        write_default_configuration(self.config_dir)
        if overrides:
            import json

            for name, values in overrides.items():
                target = os.path.join(self.config_dir, f"{name}.json")
                with open(target, encoding="utf-8") as handle:
                    data = __import__("json").load(handle)
                data.update(values)
                with open(target, "w", encoding="utf-8") as handle:
                    json.dump(data, handle, ensure_ascii=False)
        request = AnalysisRequest(source_path=path, config_dir=self.config_dir,
                                  filters=filters or [],
                                  comparison_filters=comparison or [])
        return run_analysis(request)

    def workbook(self, result, name="c.xlsx"):
        path = os.path.join(self.directory, name)
        export_excel(result.payload, result.filtered, result.config, path)
        return read_workbook(path)


class TestSheetSet(WorkbookCase):
    def test_the_standard_sheets_are_always_there(self):
        sheets = self.workbook(self.analyse())
        for name in ("Synthèse", "Qualité des données", "Population",
                     "Rémunération"):
            self.assertIn(name, sheets)

    def test_one_sheet_per_analysed_dimension(self):
        sheets = self.workbook(self.analyse())
        self.assertIn("Seg Grade", sheets)
        self.assertIn("Seg BU", sheets)

    def test_the_pay_transparency_sheet_is_there_when_sex_is_known(self):
        self.assertIn("Pay Transparency", self.workbook(self.analyse()))

    def test_the_comparison_sheet_appears_only_when_asked(self):
        from compensation_analytics.core.segmentation import Filter

        self.assertNotIn("Comparaison", self.workbook(self.analyse()))
        sheets = self.workbook(self.analyse(
            filters=[Filter("business_unit", "eq", "France")],
            comparison=[Filter("business_unit", "eq", "Iberia")]), "c2.xlsx")
        self.assertIn("Comparaison", sheets)

    def test_individual_data_is_withheld_by_default(self):
        """Le reglage par defaut ne sort aucune ligne nominative."""
        sheets = self.workbook(self.analyse())
        self.assertNotIn("Données individuelles", sheets)
        self.assertNotIn("Contrôle", sheets)

    def test_individual_data_appears_only_on_an_explicit_setting(self):
        sheets = self.workbook(self.analyse(overrides={
            "export_parameters": {"include_individual_data": True}}))
        self.assertIn("Données individuelles", sheets)
        self.assertIn("Contrôle", sheets)

    def test_no_sheet_name_breaks_excel_rules(self):
        """31 caracteres au plus, et aucun des caracteres interdits."""
        for name in self.workbook(self.analyse()):
            self.assertLessEqual(len(name), 31, name)
            self.assertFalse(set(name) & set("[]:*?/\\"), name)


class TestFormulas(WorkbookCase):
    """Les indicateurs derives citent les cellules dont ils sortent."""

    def setUp(self):
        super().setUp()
        self.sheets = self.workbook(self.analyse())

    def _find(self, sheet, label):
        cells = self.sheets[sheet]
        for reference, (_formula, value) in cells.items():
            if reference.startswith("A") and value == label:
                number = reference[1:]
                return cells.get(f"B{number}", (None, None)), number
        self.fail(f"« {label} » introuvable dans l'onglet {sheet}")

    def test_the_interquartile_range_is_a_formula(self):
        (formula, value), _row = self._find("Rémunération", "Q3 - Q1")
        self.assertIsNotNone(formula)
        self.assertRegex(formula, r"^B\d+-B\d+$")
        self.assertIsNotNone(value)

    def test_a_formula_points_at_the_right_rows(self):
        """« Q3 - Q1 » doit citer les lignes de Q3 et de Q1, et pas
        d'autres : une formule fausse a l'air d'une preuve."""
        (formula, _value), _row = self._find("Rémunération", "Q3 - Q1")
        (_f1, q3), row_q3 = self._find("Rémunération", "Q3 (P75)")
        (_f2, q1), row_q1 = self._find("Rémunération", "Q1 (P25)")
        self.assertEqual(formula, f"B{row_q3}-B{row_q1}")

    def test_the_cached_value_matches_what_the_formula_computes(self):
        """Le tableur affiche le cache avant de recalculer : les deux
        doivent dire la meme chose."""
        (formula, cached), _row = self._find("Rémunération", "Q3 - Q1")
        (_f, q3), _r3 = self._find("Rémunération", "Q3 (P75)")
        (_g, q1), _r1 = self._find("Rémunération", "Q1 (P25)")
        self.assertAlmostEqual(float(cached), float(q3) - float(q1), places=6)

    def test_every_dispersion_indicator_carries_its_formula(self):
        for label in ("Q3 - Q1", "Q3 / Q1", "P90 / P10", "Moyenne / Médiane"):
            (formula, _value), _row = self._find("Rémunération", label)
            self.assertIsNotNone(formula, label)

    def test_the_pay_gap_follows_the_directive(self):
        """(moyenne H - moyenne F) / moyenne H, et non l'inverse."""
        cells = self.sheets["Pay Transparency"]
        formulas = [formula for (formula, _value) in cells.values()
                    if formula and formula.startswith("(E")]
        self.assertTrue(formulas)
        for formula in formulas:
            self.assertRegex(formula, r"^\(E(\d+)-D\1\)/E\1\*100$")

    def test_the_catch_up_cost_uses_the_smaller_paid_headcount(self):
        cells = self.sheets["Pay Transparency"]
        formulas = [formula for (formula, _value) in cells.values()
                    if formula and formula.startswith("ABS(")]
        self.assertTrue(formulas)
        for formula in formulas:
            self.assertRegex(
                formula, r"^ABS\(E(\d+)-D\1\)\*IF\(E\1>D\1,B\1,C\1\)$")

    def test_a_formula_is_never_written_without_its_cached_value(self):
        """Un classeur ouvert en lecture seule n'evalue rien : sans cache,
        toutes les cellules derivees paraissent vides."""
        for name, cells in self.sheets.items():
            for reference, (formula, value) in cells.items():
                if formula:
                    self.assertIsNotNone(value, f"{name}!{reference}")


class TestControlSheet(WorkbookCase):
    """L'onglet qui recalcule tout par le tableur."""

    def setUp(self):
        super().setUp()
        self.sheets = self.workbook(self.analyse(overrides={
            "export_parameters": {"include_individual_data": True}}))

    def test_it_uses_the_historic_function_names(self):
        """PERCENTILE et STDEV, comprises par toutes les versions
        d'Excel et par LibreOffice."""
        formulas = " ".join(
            formula for (formula, _value) in self.sheets["Contrôle"].values()
            if formula)
        self.assertIn("MEDIAN(", formulas)
        self.assertIn("PERCENTILE(", formulas)
        self.assertIn("STDEV(", formulas)

    def test_it_points_at_the_individual_sheet(self):
        formulas = " ".join(
            formula for (formula, _value) in self.sheets["Contrôle"].values()
            if formula)
        self.assertIn("'Données individuelles'!", formulas)

    def test_the_range_covers_every_exported_row(self):
        individual = self.sheets["Données individuelles"]
        lines = max(int(reference[1:]) for reference in individual
                    if reference.startswith("A") and reference[1:].isdigit())
        formulas = " ".join(
            formula for (formula, _value) in self.sheets["Contrôle"].values()
            if formula)
        found = re.search(r"!([A-Z]+)2:[A-Z]+(\d+)", formulas)
        self.assertIsNotNone(found)
        self.assertEqual(int(found.group(2)), lines)

    def test_the_percentile_argument_is_written_with_a_comma(self):
        """« 0,25 » separe par une virgule serait lu comme deux arguments
        par un Excel francais : le point est la seule ecriture sure."""
        formulas = " ".join(
            formula for (formula, _value) in self.sheets["Contrôle"].values()
            if formula)
        self.assertIn("0.25", formulas)
        self.assertNotIn("0,25", formulas)


class TestMaskedContent(WorkbookCase):
    """Les seuils de confidentialite valent aussi pour le classeur."""

    def test_a_small_population_is_masked_in_the_workbook(self):
        sheets = self.workbook(self.analyse(rows=4))
        values = [value for (_f, value) in sheets["Rémunération"].values()]
        self.assertNotIn("Médiane", values)

    def test_a_masked_segment_writes_the_word_and_not_a_number(self):
        sheets = self.workbook(self.analyse(rows=12))
        rows = [value for (_f, value) in sheets["Seg Grade"].values()]
        self.assertIn("masqué", rows)


class TestUnusualWorkbooks(WorkbookCase):
    """Ce que le classeur devient quand le fichier n'est pas parfait."""

    def test_the_quality_findings_are_written_line_by_line(self):
        """Le classeur porte le controle qualite : c'est lui qu'on envoie a
        qui doit corriger le fichier."""
        result = self.analyse(overrides={
            "salary_parameters": {"max_plausible": 40000}})
        sheets = self.workbook(result, "qualite.xlsx")
        values = [value for (_f, value)
                  in sheets["Qualité des données"].values()]
        self.assertIn("Sévérité", values)
        self.assertTrue(any(isinstance(value, str)
                            and "seuil" in value.lower() for value in values),
                        values)

    def test_the_outliers_are_listed_with_their_reference(self):
        import csv

        path = os.path.join(self.directory, "atypiques.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(HEADERS)
            for index in range(40):
                writer.writerow(list(make_row(index, salary=40000 + index * 50)))
            for index in (900, 901):
                writer.writerow(list(make_row(index, salary=400000)))
        from compensation_analytics.core.config import write_default_configuration

        config_dir = os.path.join(self.directory, "config-atypiques")
        write_default_configuration(config_dir)
        result = run_analysis(AnalysisRequest(source_path=path,
                                              config_dir=config_dir))
        self.assertTrue(result.payload["distribution"]["outliers"])
        sheets = self.workbook(result, "atypiques.xlsx")
        values = [value for (_f, value) in sheets["Distribution"].values()]
        self.assertIn("Référence", values)
        self.assertIn("Position", values)
        matricules = {employee.employee_id for employee in result.filtered}
        for value in values:
            self.assertNotIn(value, matricules)

    def test_a_missing_cell_leaves_a_plain_value_instead_of_a_formula(self):
        """Une formule qui pointe une case vide afficherait une erreur la ou
        le chiffre est parfaitement connu.

        Le pipeline ne produit pas ce cas — P10 et P90 sont toujours
        calcules, la dispersion en depend, et « percentiles » ne decide que
        de ce qui est *publie*. C'est donc un garde-fou, et il se verifie
        la ou il vit.
        """
        from compensation_analytics.core.export import _derived

        complete = _derived("B{p90}/B{p10}", {"p90": 12, "p10": 8}, 1.5)
        self.assertEqual(complete.expression, "B12/B8")
        self.assertEqual(complete.value, 1.5)
        partial = _derived("B{p90}/B{p10}", {"p90": 12}, 1.5)
        self.assertEqual(partial, 1.5)

    def test_every_published_percentile_keeps_its_row(self):
        result = self.analyse(overrides={
            "percentile_parameters": {"percentiles": [25, 50, 75]}})
        sheets = self.workbook(result, "trois-percentiles.xlsx")
        values = [value for (_f, value) in sheets["Rémunération"].values()]
        self.assertIn("Q1 (P25)", values)
        self.assertIn("Q3 (P75)", values)

    def test_a_workbook_without_a_salary_column_says_so(self):
        """L'onglet « Controle » ne peut pas etre pose sans la colonne des
        remunerations : il le dit plutot que d'ecrire des formules vides."""
        from compensation_analytics.core.export import _rows_control

        rows = _rows_control([["Référence", "BU"], ["R1", "France"]],
                             {"median": 40000})
        self.assertIn("absente", rows[0][0])

    def test_the_control_sheet_skips_what_the_engine_withheld(self):
        from compensation_analytics.core.export import _rows_control

        rows = _rows_control([["Salaire de base"], [40000], [42000]],
                             {"median": 41000})
        labels = [row[0] for row in rows[1:] if row]
        self.assertIn("Médiane", labels)
        self.assertNotIn("P90", labels)


class TestWriterItself(unittest.TestCase):
    """Le redacteur XLSX, sur ses cas limites."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def write(self, sheets, name="w.xlsx"):
        path = os.path.join(self.directory, name)
        write_workbook(path, sheets)
        return read_workbook(path)

    def test_a_control_character_does_not_break_the_workbook(self):
        """Un caractere de controle rend le fichier inouvrable : il vient
        d'un copier-coller, et l'utilisateur ne le voit pas."""
        cells = self.write([("P", [["Poste"], ["Chef\x07 de projet"]])])
        self.assertEqual(column_values(cells["P"], "A"),
                         ["Poste", "Chef  de projet"])

    def test_the_five_xml_characters_survive(self):
        cells = self.write([("P", [["Poste"], ["R&D <\"tous\"> 'chefs'"]])])
        self.assertIn("R&D <\"tous\"> 'chefs'", column_values(cells["P"], "A"))

    def test_a_none_becomes_an_empty_cell(self):
        cells = self.write([("P", [["A", "B"], [None, 1]])])
        self.assertNotIn("A2", cells["P"])

    def test_a_boolean_is_written_as_a_boolean(self):
        """Et non comme un 1, qu'un tableur additionnerait."""
        path = os.path.join(self.directory, "bool.xlsx")
        write_workbook(path, [("P", [["Cadre"], [True], [False]])])
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn('t="b"', xml)

    def test_a_date_is_written_as_a_real_excel_date(self):
        """Un texte « 2026-01-31 » ne se trie ni ne se filtre comme une
        date : la cellule porte le numero de serie et un style de date,
        et l'outil la relit bien comme une date."""
        import datetime as _dt

        from compensation_analytics.io.tabular import read_table

        path = os.path.join(self.directory, "date.xlsx")
        write_workbook(path, [("P", [["Date"], [_dt.date(2026, 1, 31)]])])
        self.assertEqual(read_table(path).rows[0][0], _dt.date(2026, 1, 31))

    def test_a_ragged_sheet_is_accepted(self):
        cells = self.write([("P", [["A", "B", "C"], [1], [], [1, 2, 3]])])
        self.assertIn("A2", cells["P"])

    def test_an_empty_sheet_is_accepted(self):
        self.assertIn("Vide", self.write([("Vide", [])]))

    def test_a_formula_without_a_value_is_still_written(self):
        cells = self.write([("P", [["A"], [Formula("1+1", None)]])])
        self.assertEqual(cells["P"]["A2"][0], "1+1")

    def test_a_long_sheet_name_is_cut_to_what_excel_accepts(self):
        cells = self.write([("Un nom d'onglet vraiment tres long", [["A"]])])
        self.assertTrue(all(len(name) <= 31 for name in cells))


if __name__ == "__main__":
    unittest.main()
