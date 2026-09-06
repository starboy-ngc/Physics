"""Tests des anomalies a echec silencieux identifiees a l'audit.

Chacune renvoyait un resultat plausible mais faux, ou une trace technique,
la ou l'utilisateur attendait une reponse claire. Ces tests empechent leur
reapparition.
"""

import os
import tempfile
import unittest

from tests.support import HEADERS, build_population, make_config, make_row
from compensation_analytics.core import metrics
from compensation_analytics.core.config import analysis_field, percentiles
from compensation_analytics.core.errors import ConfigError
from compensation_analytics.core.mapping import resolve_mapping
from compensation_analytics.core.normalize import has_ambiguous_separator
from compensation_analytics.core.quality import run_quality_check
from compensation_analytics.core.segmentation import apply_filters, build_filters
from compensation_analytics.io.tabular import read_table
from compensation_analytics.io.xlsx_writer import write_workbook


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
