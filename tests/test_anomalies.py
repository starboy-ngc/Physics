"""Tests des anomalies a echec silencieux identifiees a l'audit.

Chacune renvoyait un resultat plausible mais faux, ou une trace technique,
la ou l'utilisateur attendait une reponse claire. Ces tests empechent leur
reapparition.
"""

import os
import tempfile
import unittest

from tests.support import HEADERS, build_population, make_config, make_row
from hr_insight.core import metrics
from hr_insight.core.config import analysis_field, percentiles
from hr_insight.core.errors import ConfigError
from hr_insight.core.mapping import resolve_mapping
from hr_insight.core.normalize import has_ambiguous_separator
from hr_insight.core.quality import run_quality_check
from hr_insight.core.segmentation import apply_filters, build_filters
from hr_insight.io.tabular import read_table
from hr_insight.io.xlsx_writer import write_workbook


class TestNumericEqualityFilter(unittest.TestCase):
    """Un filtre d'egalite sur un champ numerique comparait les ecritures :
    "50000" ne retrouvait pas la valeur 50000.0 et renvoyait zero salarie."""

    def setUp(self):
        self.config = make_config()
        self.population = build_population(
            [make_row(i, salary=50000) for i in range(10)]
            + [make_row(50 + i, salary=61000) for i in range(4)],
            self.config,
        )

    def _count(self, definition):
        return len(apply_filters(self.population, build_filters([definition])))

    def test_equality_on_numeric_field_as_text(self):
        self.assertEqual(
            self._count({"field": "base_salary", "operator": "eq", "value": "50000"}), 10
        )

    def test_equality_on_numeric_field_as_number(self):
        self.assertEqual(
            self._count({"field": "base_salary", "operator": "eq", "value": 50000}), 10
        )

    def test_equality_accepts_french_writing(self):
        self.assertEqual(
            self._count({"field": "base_salary", "operator": "eq", "value": "50 000"}), 10
        )

    def test_in_operator_on_numeric_field(self):
        self.assertEqual(
            self._count({"field": "base_salary", "operator": "in",
                         "value": ["50000", "61000"]}), 14
        )

    def test_not_equal_on_numeric_field(self):
        self.assertEqual(
            self._count({"field": "base_salary", "operator": "ne", "value": "50000"}), 4
        )

    def test_equality_on_text_field_unchanged(self):
        self.assertEqual(
            self._count({"field": "business_unit", "operator": "eq", "value": "france"}), 14
        )

    def test_non_numeric_comparison_value_is_rejected(self):
        with self.assertRaises(ConfigError) as caught:
            self._count({"field": "base_salary", "operator": "gte", "value": "beaucoup"})
        self.assertIn("n'est pas un nombre", caught.exception.message)


class TestDispersionAlwaysComputed(unittest.TestCase):
    """Retirer P25 de la configuration faisait disparaitre Q3/Q1 et P90/P10
    de la restitution, sans explication."""

    def test_ratios_survive_a_reduced_percentile_configuration(self):
        config = make_config({"percentile_parameters.percentiles": [10, 50, 90]})
        population = build_population(
            [make_row(i, salary=30000 + i * 1000) for i in range(30)], config
        )
        result = metrics.calculate_salary_metrics(population, config)
        dispersion = result["dispersion"]
        self.assertIsNotNone(dispersion["q3_over_q1"])
        self.assertIsNotNone(dispersion["p90_over_p10"])
        self.assertIsNotNone(dispersion["interquartile_range"])

    def test_only_configured_percentiles_are_published(self):
        config = make_config({"percentile_parameters.percentiles": [10, 50, 90]})
        population = build_population(
            [make_row(i, salary=30000 + i * 1000) for i in range(30)], config
        )
        result = metrics.calculate_salary_metrics(population, config)
        published = [entry["key"] for entry in result["published_percentiles"]]
        self.assertEqual(published, ["p10", "p50", "p90"])

    def test_quartile_labels_are_business_readable(self):
        config = make_config()
        population = build_population(
            [make_row(i, salary=30000 + i * 1000) for i in range(30)], config
        )
        result = metrics.calculate_salary_metrics(population, config)
        labels = {entry["label"] for entry in result["published_percentiles"]}
        self.assertIn("Q1 (P25)", labels)
        self.assertIn("Médiane (P50)", labels)

    def test_invalid_percentile_is_rejected(self):
        for value in ([120], ["beaucoup"]):
            with self.assertRaises(ConfigError):
                percentiles(make_config({"percentile_parameters.percentiles": value}))


class TestAnalysisFieldValidation(unittest.TestCase):
    """Pointer analysis_field sur une colonne texte levait un TypeError brut."""

    def test_text_field_is_rejected_with_a_readable_message(self):
        config = make_config({"salary_parameters.analysis_field": "grade"})
        with self.assertRaises(ConfigError) as caught:
            analysis_field(config)
        message = caught.exception.message
        self.assertIn("grade", message)
        self.assertIn("numérique", message)
        self.assertNotIn("TypeError", message)

    def test_quality_check_no_longer_crashes(self):
        config = make_config({"salary_parameters.analysis_field": "grade"})
        population = build_population([make_row(i) for i in range(10)], config)
        with self.assertRaises(ConfigError):
            run_quality_check(population, resolve_mapping(HEADERS, config), config)

    def test_alternative_numeric_field_is_accepted(self):
        config = make_config({"salary_parameters.analysis_field": "total_compensation"})
        self.assertEqual(analysis_field(config), "total_compensation")


class TestAmbiguousSeparator(unittest.TestCase):
    """"45.000" vaut 45 000 en France et 45,0 ailleurs : le moteur retient la
    lecture standard mais doit signaler l'ambiguite au lieu de deviner."""

    def test_detection(self):
        for value in ("45.000", "1,234", "-12.500"):
            self.assertTrue(has_ambiguous_separator(value), value)
        for value in ("0,800", "45000", "1.234.567,89", "1 234", 45000, None):
            self.assertFalse(has_ambiguous_separator(value), str(value))

    def test_quality_check_reports_it(self):
        config = make_config()
        rows = [make_row(i, salary=40000) for i in range(10)]
        rows.append(make_row(99, salary="45.000"))
        population = build_population(rows, config)
        report = run_quality_check(population, resolve_mapping(HEADERS, config), config)
        codes = {finding.code for finding in report.findings}
        self.assertIn("ambiguous_separator_base_salary", codes)
        finding = next(f for f in report.findings
                       if f.code == "ambiguous_separator_base_salary")
        self.assertIn("45.000", finding.message)
        self.assertNotIn("non numériques", finding.message)


class TestWorkbookNumberWriting(unittest.TestCase):
    """inf et la notation scientifique produisaient un classeur illisible."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def test_non_finite_values_do_not_corrupt_the_file(self):
        path = os.path.join(self.directory, "extreme.xlsx")
        write_workbook(path, [("Test", [
            ["Libelle", "Valeur"],
            ["infini", float("inf")],
            ["nan", float("nan")],
            ["très grand", 1e20],
            ["normal", 40000.5],
        ])])
        table = read_table(path)  # relu par notre propre importeur
        values = {row[0]: row[1] for row in table.rows}
        self.assertEqual(values["infini"], "inf")
        self.assertAlmostEqual(values["normal"], 40000.5)
        self.assertAlmostEqual(float(values["très grand"]), 1e20)

    def test_no_scientific_notation_in_the_xml(self):
        import zipfile
        path = os.path.join(self.directory, "big.xlsx")
        write_workbook(path, [("Test", [["a"], [1e20]])])
        with zipfile.ZipFile(path) as archive:
            content = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertNotIn("e+", content)

if __name__ == "__main__":
    unittest.main()


class TestImpossibleDatesNeverEnterAnAverage(unittest.TestCase):
    """Une sortie anterieure a l'entree donne une anciennete negative.

    Le controle qualite la signale depuis toujours ; rien n'empechait pour
    autant le chiffre d'entrer dans l'« anciennete moyenne » publiee, ou
    il ne se voyait plus. Une valeur impossible n'est pas une valeur : elle
    est absente, et la ligne est marquee.
    """

    def _population(self):
        import datetime as _dt

        lignes = [make_row(0, hire_date=_dt.date(2020, 1, 1),
                           leave_date=_dt.date(2015, 1, 1)),
                  make_row(1, birth_date=_dt.date(2090, 1, 1))]
        lignes += [make_row(index, tenure=5, age=40)
                   for index in range(2, 14)]
        return build_population(lignes)

    def test_a_departure_before_the_arrival_leaves_no_seniority(self):
        salaries = list(self._population())
        self.assertIsNone(salaries[0].tenure_years)
        self.assertIn("tenure:end_before_hire", salaries[0].issues)

    def test_a_birth_date_in_the_future_leaves_no_age(self):
        salaries = list(self._population())
        self.assertIsNone(salaries[1].age_years)
        self.assertIn("birth_date:after_reference", salaries[1].issues)

    def test_the_published_averages_are_those_of_the_others(self):
        config = make_config()
        population = self._population()
        anciennete = metrics.calculate_tenure_metrics(population, config)
        age = metrics.calculate_age_metrics(population, config)
        self.assertAlmostEqual(anciennete["tenure_mean"], 5.0, places=2)
        self.assertAlmostEqual(age["age_mean"], 40.0, places=1)
        # Les deux lignes restent comptees dans l'effectif : elles existent.
        # Treize anciennetes connues sur quatorze : seule la ligne dont la
        # sortie precede l'entree n'en a pas.
        self.assertEqual(anciennete["tenure_known"], 13)
        self.assertEqual(age["age_known"], 13)
        self.assertEqual(len(population), 14)

    def test_the_quality_report_still_names_the_lines(self):
        """La valeur disparait du calcul, pas du rapport : c'est le controle
        qualite qui dit quoi corriger."""
        config = make_config()
        population = self._population()
        mapping = resolve_mapping(list(HEADERS), config)
        rapport = run_quality_check(population, mapping, config).as_dict()
        codes = {constat["code"] for constat in rapport["constats"]}
        self.assertIn("leave_before_hire", codes)


class TestTheSexIsReadFromOneFieldOnly(unittest.TestCase):
    """Un SIRH range parfois le sexe dans une colonne a lui.

    « gender_field » existe pour cela. Encore faut-il que tout le monde le
    lise : la repartition affichee sur l'ecran Population l'ignorait et
    retombait sur le champ natif. Sur un fichier ainsi configure, l'outil
    annoncait « 100 % non renseigne » a gauche et un ecart femmes/hommes
    calcule a droite — deux reponses contradictoires a la meme question,
    dans la meme analyse.
    """

    def _population_et_config(self):
        from hr_insight.core.config import Configuration

        population = build_population([make_row(i) for i in range(40)])
        for rang, salarie in enumerate(population.employees):
            salarie.extra["sexe_sirh"] = "F" if rang % 2 else "H"
            salarie.gender = ""
        donnees = make_config().as_dict()
        donnees["pay_equity_parameters"]["gender_field"] = "sexe_sirh"
        return population, Configuration(donnees)

    def test_the_population_split_follows_the_configured_field(self):
        population, config = self._population_et_config()
        parts = metrics.calculate_population_metrics(population, config)
        repartition = {item["label"]: item["count"]
                       for item in parts["gender_split"]}
        self.assertEqual(repartition, {"F": 20, "H": 20})

    def test_the_split_and_the_gap_speak_of_the_same_field(self):
        from hr_insight.core import pay_equity

        population, config = self._population_et_config()
        parts = metrics.calculate_population_metrics(population, config)
        ecarts = pay_equity.calculate_pay_equity(population, config)
        femmes = {item["label"]: item["count"]
                  for item in parts["gender_split"]}.get("F")
        self.assertEqual(femmes, ecarts["female_count"])
