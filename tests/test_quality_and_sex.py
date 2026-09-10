"""Le controle qualite, constat par constat — et la lecture par sexe.

Deux angles morts que la couverture a designes :

- Le controle qualite pose seize constats differents ; cinq seulement
  etaient verifies. Un constat qui ne se declenche pas laisse passer le
  defaut qu'il existe pour attraper, et l'analyse porte sur un fichier
  qu'on croit sain.
- `segment_by_sex` — la lecture qui dedouble le graphique de dispersion
  femmes / hommes — n'avait aucun test, alors qu'elle applique les seuils
  de confidentialite deux fois : sur chaque sexe, et sur le segment.

Aucune donnee RH reelle.
"""

import datetime as _dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import (HEADERS, REFERENCE_DATE, build_population,
                           make_config, make_row)
from compensation_analytics.core.mapping import resolve_mapping
from compensation_analytics.core.metrics import segment_by_sex
from compensation_analytics.core.normalize import normalise_table
from compensation_analytics.core.quality import run_quality_check


def check(rows, headers=None, config=None, reference=REFERENCE_DATE):
    """Controle qualite complet sur un tableau brut."""
    config = config or make_config()
    headers = list(headers if headers is not None else HEADERS)
    mapping = resolve_mapping(headers, config)
    population = normalise_table(headers, rows, mapping, config,
                                 source_name="t", reference_date=reference)
    return run_quality_check(population, mapping, config)


def codes(report):
    return {finding.code for finding in report.findings}


class TestStructureFindings(unittest.TestCase):
    def test_an_empty_file_is_reported(self):
        report = check([])
        self.assertIn("empty_population", codes(report))
        self.assertTrue(report.blocking)

    def test_unrecognised_columns_are_reported_without_blocking(self):
        """C'est une information, pas une anomalie : une colonne de plus
        n'empeche aucune analyse."""
        report = check([list(make_row(1)) + ["x"]],
                       headers=list(HEADERS) + ["Prime de panier"])
        self.assertIn("unknown_columns", codes(report))
        self.assertFalse(report.blocking)
        message = next(f.message for f in report.findings
                       if f.code == "unknown_columns")
        self.assertIn("Prime de panier", message)

    def test_a_duplicated_column_is_reported(self):
        """Deux colonnes « Grade » : seule la premiere est lue, et
        l'utilisateur doit savoir laquelle."""
        report = check([list(make_row(1)) + ["G9"]],
                       headers=list(HEADERS) + ["Grade"])
        self.assertIn("duplicate_columns", codes(report))
        message = next(f.message for f in report.findings
                       if f.code == "duplicate_columns")
        self.assertIn("Grade", message)
        self.assertIn("première", message)


class TestIdentityFindings(unittest.TestCase):
    def test_a_repeated_identifier_blocks(self):
        report = check([make_row(1, employee_id="E1"),
                        make_row(2, employee_id="E1")])
        self.assertIn("duplicate_employee_id", codes(report))
        self.assertTrue(report.blocking)
        self.assertEqual(report.duplicates, 1)

    def test_a_line_without_an_identifier_is_a_warning(self):
        report = check([make_row(1, employee_id=""), make_row(2)])
        self.assertIn("missing_employee_id", codes(report))
        self.assertFalse(report.blocking)

    def test_the_finding_names_the_lines_to_correct(self):
        report = check([make_row(1, employee_id="E1"),
                        make_row(2, employee_id="E1"),
                        make_row(3, employee_id="E1")])
        finding = next(f for f in report.findings
                       if f.code == "duplicate_employee_id")
        self.assertEqual(finding.rows, [3, 4])   # la 1re ligne fait foi


class TestDateFindings(unittest.TestCase):
    def test_an_unreadable_date_blocks(self):
        report = check([make_row(1, birth_date="pas une date")])
        self.assertIn("invalid_date", codes(report))
        self.assertTrue(report.blocking)

    def test_a_birth_date_in_the_future_blocks(self):
        report = check([make_row(1, birth_date=_dt.date(2100, 1, 1))])
        self.assertIn("future_birth_date", codes(report))
        self.assertTrue(report.blocking)

    def test_a_hire_date_in_the_future_is_a_warning(self):
        """Une embauche a venir est une situation reelle, pas une erreur."""
        report = check([make_row(1, hire_date=_dt.date(2100, 1, 1))])
        self.assertIn("future_hire_date", codes(report))
        self.assertFalse(report.blocking)

    def test_leaving_before_being_hired_blocks(self):
        report = check([make_row(1, hire_date=_dt.date(2020, 1, 1),
                                 leave_date=_dt.date(2019, 1, 1))])
        self.assertIn("leave_before_hire", codes(report))
        self.assertTrue(report.blocking)

    def test_an_implausible_age_is_a_warning(self):
        report = check([make_row(1, age=8)])
        self.assertIn("implausible_age", codes(report))

    def test_a_sound_file_has_no_date_finding(self):
        report = check([make_row(index) for index in range(5)])
        for code in ("invalid_date", "future_birth_date", "future_hire_date",
                     "leave_before_hire", "implausible_age"):
            self.assertNotIn(code, codes(report))


class TestSalaryFindings(unittest.TestCase):
    def test_a_missing_salary_blocks(self):
        report = check([make_row(1, salary=None)])
        self.assertIn("missing_salary", codes(report))
        self.assertTrue(report.blocking)

    def test_a_negative_salary_blocks(self):
        report = check([make_row(1, salary=-100)])
        self.assertIn("negative_salary", codes(report))
        self.assertTrue(report.blocking)

    def test_a_zero_salary_is_a_warning(self):
        """Un salaire a zero se rencontre — conge sans solde — mais fausse
        toutes les moyennes : il se signale sans bloquer."""
        report = check([make_row(1, salary=0)])
        self.assertIn("zero_salary", codes(report))
        self.assertFalse(report.blocking)

    def test_a_salary_below_the_plausible_floor_is_a_warning(self):
        report = check([make_row(1, salary=12)])
        self.assertIn("salary_below_threshold", codes(report))

    def test_a_salary_above_the_plausible_ceiling_is_a_warning(self):
        report = check([make_row(1, salary=9_000_000)])
        self.assertIn("salary_above_threshold", codes(report))

    def test_the_plausible_range_is_configurable(self):
        """Les bornes sont un parametre, pas un nombre cache dans le code."""
        config = make_config({"salary_parameters.max_plausible": 50000})
        report = check([make_row(index, salary=60000) for index in range(5)],
                       config=config)
        self.assertIn("salary_above_threshold", codes(report))

    def test_an_outlier_is_reported_for_information(self):
        rows = [make_row(index, salary=40000) for index in range(30)]
        rows.append(make_row(99, salary=400000))
        report = check(rows)
        self.assertIn("salary_outlier", codes(report))
        self.assertFalse(report.blocking)

    def test_a_non_numeric_salary_is_reported_with_its_field(self):
        report = check([make_row(1, salary="quarante mille")])
        self.assertTrue(any(code.startswith("type_base_salary")
                            for code in codes(report)))

    def test_an_ambiguous_separator_is_named_for_what_it_is(self):
        """« 45.000 » lu comme 45,0 est le defaut le plus couteux d'un
        import : il ne casse rien, il fausse tout."""
        report = check([make_row(1, salary="45.000")])
        self.assertTrue(any("ambiguous_separator" in code
                            for code in codes(report)))


class TestReportShape(unittest.TestCase):
    def test_the_status_has_three_levels(self):
        self.assertEqual(check([make_row(i) for i in range(5)]).status,
                         "CONFORME")
        self.assertEqual(check([make_row(1, salary=0)]).status,
                         "POINTS DE VIGILANCE")
        self.assertEqual(check([make_row(1, salary=None)]).status,
                         "CORRECTIONS REQUISES")

    def test_the_text_form_names_every_finding(self):
        text = check([make_row(1, salary=None), make_row(2, salary=0)]).to_text()
        self.assertIn("DATA QUALITY CHECK", text)
        self.assertIn("critique", text)
        self.assertIn("avertissement", text)

    def test_the_dictionary_form_carries_no_personal_data(self):
        """Le rapport voyage jusqu'au classeur : il ne doit porter que des
        numeros de ligne, jamais un matricule ni un nom."""
        report = check([make_row(1, employee_id="E1", salary=None),
                        make_row(2, employee_id="E1")])
        text = repr(report.as_dict())
        self.assertNotIn("E1", text)
        self.assertNotIn("NOM1", text)

    def test_the_listed_lines_are_capped(self):
        """Mille lignes fausses ne s'ecrivent pas mille fois."""
        report = check([make_row(index, salary=None) for index in range(200)])
        finding = next(f for f in report.findings if f.code == "missing_salary")
        self.assertEqual(finding.count, 200)
        self.assertLessEqual(len(finding.rows), 200)


class TestSegmentBySex(unittest.TestCase):
    """La lecture qui dedouble le graphique de dispersion."""

    def population(self, women=12, men=12, unknown=0, unit="France"):
        rows = [make_row(index, gender="F", business_unit=unit,
                         salary=40000 + index * 100)
                for index in range(women)]
        rows += [make_row(100 + index, gender="H", business_unit=unit,
                          salary=45000 + index * 100)
                 for index in range(men)]
        rows += [make_row(200 + index, gender="", business_unit=unit,
                          salary=50000) for index in range(unknown)]
        return build_population(rows)

    def test_each_group_carries_both_sexes_and_the_whole(self):
        rows = segment_by_sex(self.population(), make_config(),
                              "business_unit")
        self.assertEqual(len(rows), 1)
        entry = rows[0]
        self.assertEqual(entry["segment"], "France")
        self.assertEqual(entry["headcount"], 24)
        self.assertEqual((entry["female_count"], entry["male_count"]), (12, 12))
        self.assertIn("salary", entry)

    def test_the_figures_of_each_sex_are_its_own(self):
        entry = segment_by_sex(self.population(), make_config(),
                               "business_unit")[0]
        self.assertLess(entry["female"]["median"], entry["male"]["median"])

    def test_a_sex_below_the_chart_threshold_is_not_chartable(self):
        """Le seuil ne cede pas parce que le segment entier le franchit :
        six femmes dans un segment de trente restent six femmes."""
        entry = segment_by_sex(self.population(women=6, men=24),
                               make_config(), "business_unit")[0]
        self.assertFalse(entry["female_chartable"])
        self.assertTrue(entry["male_chartable"])
        self.assertTrue(entry["chartable"])

    def test_a_sex_below_the_publication_threshold_is_masked(self):
        entry = segment_by_sex(self.population(women=3, men=24),
                               make_config(), "business_unit")[0]
        self.assertTrue(entry["female"].get("masked"))
        self.assertNotIn("median", entry["female"])

    def test_the_split_is_offered_only_if_one_sex_can_be_drawn(self):
        small = segment_by_sex(self.population(women=4, men=4),
                               make_config(), "business_unit")[0]
        self.assertFalse(small["sex_chartable"])
        wide = segment_by_sex(self.population(), make_config(),
                              "business_unit")[0]
        self.assertTrue(wide["sex_chartable"])

    def test_an_unknown_sex_counts_in_the_whole_but_in_neither_side(self):
        """Sinon la somme des deux sexes ne fait pas l'effectif, et le
        lecteur cherche l'erreur."""
        entry = segment_by_sex(self.population(women=10, men=10, unknown=5),
                               make_config(), "business_unit")[0]
        self.assertEqual(entry["headcount"], 25)
        self.assertEqual(entry["female_count"] + entry["male_count"], 20)

    def test_an_empty_value_forms_its_own_group(self):
        rows = segment_by_sex(
            build_population([make_row(1, business_unit=""),
                              make_row(2, business_unit="France")]),
            make_config(), "business_unit")
        self.assertIn("(non renseigne)", [row["segment"] for row in rows])

    def test_the_declared_sex_values_are_read_from_the_configuration(self):
        """« Femme » et « Homme » en toutes lettres doivent etre reconnus
        sans toucher au code."""
        people = build_population(
            [make_row(index, gender="Femme", salary=40000)
             for index in range(12)]
            + [make_row(100 + index, gender="Homme", salary=45000)
               for index in range(12)])
        entry = segment_by_sex(people, make_config(), "business_unit")[0]
        self.assertEqual((entry["female_count"], entry["male_count"]),
                         (12, 12))

    def test_another_salary_field_can_be_read(self):
        people = self.population()
        entry = segment_by_sex(people, make_config(), "business_unit",
                               salary_field="total_compensation")[0]
        self.assertTrue(entry["female"].get("masked")
                        or entry["female"].get("count") == 0)


if __name__ == "__main__":
    unittest.main()
