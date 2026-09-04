"""Tests du controle qualite des donnees."""

import datetime as _dt
import unittest

from tests.support import HEADERS, REFERENCE_DATE, build_population, make_config, make_row
from compensation_analytics.core.mapping import resolve_mapping
from compensation_analytics.core.quality import CRITICAL, run_quality_check


def check(rows, overrides=None):
    config = make_config(overrides)
    population = build_population(rows, config)
    mapping = resolve_mapping(HEADERS, config)
    return run_quality_check(population, mapping, config), population


def codes(report):
    return {finding.code for finding in report.findings}


class TestPopulationChecks(unittest.TestCase):
    def test_clean_population_is_compliant(self):
        report, _ = check([make_row(i) for i in range(20)])
        self.assertEqual(report.critical_count, 0)
        self.assertEqual(report.status, "CONFORME")
        self.assertFalse(report.blocking)

    def test_duplicate_employee_id_is_critical(self):
        rows = [make_row(i) for i in range(10)]
        rows.append(make_row(0))
        report, _ = check(rows)
        self.assertEqual(report.duplicates, 1)
        self.assertIn("duplicate_employee_id", codes(report))
        self.assertTrue(report.blocking)

    def test_empty_population_is_critical(self):
        report, _ = check([])
        self.assertIn("empty_population", codes(report))

    def test_blank_rows_are_ignored(self):
        rows = [make_row(i) for i in range(5)] + [[""] * len(HEADERS)]
        report, population = check(rows)
        self.assertEqual(len(population), 5)
        self.assertEqual(report.imported_rows, 6)
        self.assertEqual(report.retained_rows, 5)

    def test_missing_employee_id_is_reported(self):
        report, _ = check([make_row(0), make_row(1, employee_id="")])
        self.assertIn("missing_employee_id", codes(report))


class TestSalaryChecks(unittest.TestCase):
    def test_missing_salary(self):
        report, _ = check([make_row(i) for i in range(5)] + [make_row(9, salary=None)])
        self.assertEqual(report.missing_salary, 1)
        self.assertIn("missing_salary", codes(report))

    def test_negative_salary(self):
        report, _ = check([make_row(0, salary=-100)] + [make_row(i) for i in range(1, 5)])
        self.assertIn("negative_salary", codes(report))

    def test_zero_salary_is_a_warning_not_critical(self):
        report, _ = check([make_row(0, salary=0)] + [make_row(i) for i in range(1, 5)])
        self.assertIn("zero_salary", codes(report))
        finding = next(f for f in report.findings if f.code == "zero_salary")
        self.assertNotEqual(finding.severity, CRITICAL)

    def test_salary_as_text_is_converted(self):
        report, population = check([make_row(0, salary="45 000,50")] +
                                   [make_row(i) for i in range(1, 5)])
        self.assertAlmostEqual(population.employees[0].base_salary, 45000.5)
        self.assertEqual(report.missing_salary, 0)

    def test_unconvertible_salary_is_flagged(self):
        report, _ = check([make_row(0, salary="a definir")] +
                          [make_row(i) for i in range(1, 5)])
        self.assertTrue(any(code.startswith("type_base_salary") for code in codes(report)))

    def test_plausibility_thresholds_are_configurable(self):
        report, _ = check(
            [make_row(0, salary=500)] + [make_row(i) for i in range(1, 5)],
            overrides={"salary_parameters.min_plausible": 1000},
        )
        self.assertIn("salary_below_threshold", codes(report))


class TestDateChecks(unittest.TestCase):
    def test_invalid_date_is_critical(self):
        report, _ = check([make_row(0, birth_date="32/13/2000")] +
                          [make_row(i) for i in range(1, 5)])
        self.assertIn("invalid_date", codes(report))
        self.assertEqual(report.invalid_dates, 1)

    def test_future_birth_date(self):
        future = REFERENCE_DATE + _dt.timedelta(days=365)
        report, _ = check([make_row(0, birth_date=future)] +
                          [make_row(i) for i in range(1, 5)])
        self.assertIn("future_birth_date", codes(report))

    def test_leave_before_hire(self):
        hire = _dt.date(2020, 1, 1)
        report, _ = check(
            [make_row(0, hire_date=hire, leave_date=_dt.date(2019, 6, 1))] +
            [make_row(i) for i in range(1, 5)]
        )
        self.assertIn("leave_before_hire", codes(report))

    def test_multiple_date_formats_are_accepted(self):
        _, population = check([make_row(0, birth_date="1980-05-04",
                                        hire_date="04/05/2010")] +
                              [make_row(i) for i in range(1, 5)])
        self.assertEqual(population.employees[0].birth_date, _dt.date(1980, 5, 4))
        self.assertEqual(population.employees[0].hire_date, _dt.date(2010, 5, 4))


class TestReportRendering(unittest.TestCase):
    def test_text_report_contains_no_personal_data(self):
        rows = [make_row(i, salary=40000 + i) for i in range(10)]
        report, _ = check(rows)
        text = report.to_text()
        self.assertNotIn("NOM0", text)
        self.assertNotIn("PRENOM0", text)
        self.assertNotIn("E00000", text)

    def test_dict_report_exposes_counters_only(self):
        report, _ = check([make_row(i) for i in range(10)])
        payload = report.as_dict()
        self.assertIn("lignes_importees", payload)
        self.assertIn("statut", payload)


if __name__ == "__main__":
    unittest.main()
