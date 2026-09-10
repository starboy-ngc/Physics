"""Les criteres de filtre, un par un, et l'ecriture qui les produit.

Le LISEZ-MOI annonce sept ecritures — =, !=, >, >=, <, <=, ~= — et deux
formes de liste. Aucune n'etait verifiee : un operateur qui se tromperait de
sens ne rendrait pas d'erreur, il rendrait une population fausse, et rien ne
le dirait. C'est le pire des defauts pour un outil d'analyse.

Aucune donnee RH reelle.
"""

import datetime as _dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, REFERENCE_DATE, build_population, make_config, make_row
from compensation_analytics.cli import parse_filter
from compensation_analytics.core.errors import CompensationError, ConfigError
from compensation_analytics.core.segmentation import (
    CORE_FIELDS, Filter, apply_filters, build_filters, cross_key,
    describe_filters, split_by,
)


def population():
    """Six salaries, tous differents sur chaque axe utile."""
    return build_population([
        make_row(1, salary=30000, business_unit="France", grade="G3",
                 gender="F", age=25, tenure=1),
        make_row(2, salary=45000, business_unit="France", grade="G5",
                 gender="H", age=35, tenure=5),
        make_row(3, salary=50000, business_unit="Iberia", grade="G5",
                 gender="F", age=45, tenure=10),
        make_row(4, salary=60000, business_unit="Iberia", grade="G7",
                 gender="H", age=55, tenure=20),
        make_row(5, salary=None, business_unit="Benelux", grade="G4",
                 gender="F", age=30, tenure=2),
        make_row(6, salary=90000, business_unit="Benelux", grade="G9",
                 gender="H", age=60, tenure=30),
    ])


def kept(criterion, people=None):
    people = people if people is not None else population()
    return sorted(employee.employee_id
                  for employee in apply_filters(people, [criterion]))


class TestEachOperator(unittest.TestCase):
    def test_equality_on_text(self):
        self.assertEqual(kept(Filter("business_unit", "eq", "France")),
                         ["E00001", "E00002"])

    def test_inequality_on_text(self):
        self.assertEqual(kept(Filter("business_unit", "ne", "France")),
                         ["E00003", "E00004", "E00005", "E00006"])

    def test_membership(self):
        self.assertEqual(
            kept(Filter("grade", "in", ["G5", "G7"])),
            ["E00002", "E00003", "E00004"])

    def test_exclusion(self):
        self.assertEqual(
            kept(Filter("grade", "not_in", ["G5", "G7"])),
            ["E00001", "E00005", "E00006"])

    def test_greater_than_is_strict(self):
        self.assertEqual(kept(Filter("base_salary", "gt", 50000)),
                         ["E00004", "E00006"])

    def test_greater_or_equal_includes_the_bound(self):
        self.assertEqual(kept(Filter("base_salary", "gte", 50000)),
                         ["E00003", "E00004", "E00006"])

    def test_less_than_is_strict(self):
        self.assertEqual(kept(Filter("base_salary", "lt", 45000)),
                         ["E00001"])

    def test_less_or_equal_includes_the_bound(self):
        self.assertEqual(kept(Filter("base_salary", "lte", 45000)),
                         ["E00001", "E00002"])

    def test_contains_ignores_case(self):
        self.assertEqual(kept(Filter("business_unit", "contains", "FRAN")),
                         ["E00001", "E00002"])

    def test_between_includes_both_bounds(self):
        self.assertEqual(
            kept(Filter("base_salary", "between", [45000, 60000])),
            ["E00002", "E00003", "E00004"])

    def test_between_needs_exactly_two_bounds(self):
        """Trois bornes ne sont pas un intervalle : personne n'est retenu,
        et surtout rien ne leve au milieu d'une analyse."""
        self.assertEqual(kept(Filter("base_salary", "between", [1, 2, 3])), [])

    def test_an_unknown_operator_is_refused_at_use(self):
        with self.assertRaises(ConfigError):
            kept(Filter("base_salary", "environ", 45000))


class TestMissingValues(unittest.TestCase):
    """Un salaire absent ne doit jamais passer pour zero."""

    def test_a_comparison_excludes_an_empty_value(self):
        for operator, value in (("gt", 0), ("gte", 0), ("lt", 999999),
                                ("lte", 999999)):
            self.assertNotIn("E00005", kept(
                Filter("base_salary", operator, value)), operator)

    def test_between_excludes_an_empty_value(self):
        self.assertNotIn("E00005",
                         kept(Filter("base_salary", "between", [0, 999999])))

    def test_equality_on_an_empty_value_finds_it(self):
        """Chercher les lignes sans salaire est un usage legitime."""
        self.assertEqual(kept(Filter("base_salary", "eq", "")), ["E00005"])


class TestTypedComparison(unittest.TestCase):
    """Comparer les ecritures rendrait zero salarie, sans le moindre message."""

    def test_a_number_written_as_text_finds_the_number(self):
        self.assertEqual(kept(Filter("base_salary", "eq", "45000")),
                         ["E00002"])

    def test_a_french_written_number_finds_the_number(self):
        self.assertEqual(kept(Filter("base_salary", "eq", "45 000,00")),
                         ["E00002"])

    def test_a_date_written_as_text_finds_the_date(self):
        people = population()
        birth = people.employees[1].birth_date
        self.assertEqual(kept(Filter("birth_date", "eq", birth.isoformat()),
                              people), ["E00002"])

    def test_a_text_value_never_matches_a_number(self):
        self.assertEqual(kept(Filter("base_salary", "eq", "quarante mille")),
                         [])

    def test_a_comparison_against_text_is_refused_with_a_reason(self):
        with self.assertRaises(ConfigError) as caught:
            kept(Filter("base_salary", "gt", "beaucoup"))
        self.assertIn("numérique", caught.exception.message)

    def test_the_refusal_carries_no_personal_data(self):
        """La valeur saisie peut etre un nom : le journal n'en retient que
        le type et la longueur."""
        with self.assertRaises(ConfigError) as caught:
            kept(Filter("base_salary", "gt", "DUPONT"))
        self.assertNotIn("DUPONT", caught.exception.technical)
        self.assertIn("len=6", caught.exception.technical)


class TestCombination(unittest.TestCase):
    def test_several_criteria_combine_by_and(self):
        people = population()
        selected = apply_filters(people, [
            Filter("grade", "in", ["G5", "G7"]),
            Filter("business_unit", "eq", "Iberia"),
        ])
        self.assertEqual(sorted(e.employee_id for e in selected),
                         ["E00003", "E00004"])

    def test_no_criterion_returns_the_same_population(self):
        people = population()
        self.assertIs(apply_filters(people, []), people)

    def test_the_filtered_population_keeps_its_bands(self):
        """Les tranches posees a l'import doivent survivre au filtre :
        sinon les pyramides changent de decoupage selon le filtre."""
        people = population()
        narrowed = apply_filters(people, [Filter("grade", "eq", "G5")])
        self.assertEqual(narrowed.age_bands, people.age_bands)
        self.assertEqual(narrowed.tenure_bands, people.tenure_bands)


class TestWrittenExpressions(unittest.TestCase):
    """Ce que le LISEZ-MOI promet en ligne de commande."""

    def test_every_documented_token(self):
        for expression, expected in (
                ("business_unit=France", ("business_unit", "eq", "France")),
                ("business_unit!=France", ("business_unit", "ne", "France")),
                ("base_salary>=50000", ("base_salary", "gte", "50000")),
                ("base_salary<=50000", ("base_salary", "lte", "50000")),
                ("base_salary>50000", ("base_salary", "gt", "50000")),
                ("base_salary<50000", ("base_salary", "lt", "50000")),
                ("job~=technicien", ("job", "contains", "technicien")),
        ):
            parsed = parse_filter(expression)
            self.assertEqual(
                (parsed["field"], parsed["operator"], parsed["value"]),
                expected, expression)

    def test_a_list_keeps_the_meaning_of_the_sign(self):
        """« != » sur une liste doit exclure. Le traduire en « in » ferait
        dire a l'expression exactement l'inverse, sans message."""
        self.assertEqual(parse_filter("grade=G5|G6")["operator"], "in")
        self.assertEqual(parse_filter("grade!=G5|G6")["operator"], "not_in")
        self.assertEqual(parse_filter("grade=G5|G6")["value"], ["G5", "G6"])

    def test_a_list_with_a_comparison_is_refused(self):
        with self.assertRaises(CompensationError) as caught:
            parse_filter("base_salary>=1|2")
        self.assertIn("valeur unique", caught.exception.message)

    def test_spaces_around_the_sign_are_tolerated(self):
        parsed = parse_filter("  business_unit = France  ")
        self.assertEqual((parsed["field"], parsed["value"]),
                         ("business_unit", "France"))

    def test_a_value_containing_a_sign_stays_whole(self):
        parsed = parse_filter("job=Chef d'équipe > 10 personnes")
        self.assertEqual(parsed["operator"], "eq")
        self.assertEqual(parsed["value"], "Chef d'équipe > 10 personnes")

    def test_an_expression_without_a_sign_is_refused(self):
        with self.assertRaises(CompensationError) as caught:
            parse_filter("business_unit France")
        self.assertIn("mal écrit", caught.exception.message)

    def test_the_refusal_carries_no_personal_data(self):
        with self.assertRaises(CompensationError) as caught:
            parse_filter("DUPONT Jean")
        self.assertNotIn("DUPONT", caught.exception.technical)


class TestBuildingFilters(unittest.TestCase):
    def setUp(self):
        self.config = make_config()

    def test_an_unknown_field_is_refused_with_the_list(self):
        with self.assertRaises(ConfigError) as caught:
            build_filters([{"field": "salaire", "value": 1}], self.config)
        self.assertIn("salaire", caught.exception.message)
        self.assertIn("base_salary", caught.exception.message)

    def test_a_filter_without_a_field_is_refused(self):
        with self.assertRaises(ConfigError) as caught:
            build_filters([{"value": "France"}], self.config)
        self.assertIn("incomplet", caught.exception.message)

    def test_an_unknown_operator_is_refused_before_running(self):
        with self.assertRaises(ConfigError) as caught:
            build_filters([{"field": "grade", "operator": "environ",
                            "value": "G5"}], self.config)
        self.assertIn("environ", caught.exception.message)

    def test_the_default_operator_is_equality(self):
        built = build_filters([{"field": "grade", "value": "G5"}], self.config)
        self.assertEqual(built[0].operator, "eq")

    def test_no_definition_gives_no_filter(self):
        self.assertEqual(build_filters([], self.config), [])
        self.assertEqual(build_filters(None, self.config), [])

    def test_every_core_field_is_filterable(self):
        """Le LISEZ-MOI promet le filtre sur n'importe quel champ."""
        for name in CORE_FIELDS:
            build_filters([{"field": name, "operator": "ne", "value": "zzz"}],
                          self.config)

    def test_technical_fields_are_never_offered(self):
        for name in ("row_number", "issues", "extra"):
            with self.assertRaises(ConfigError, msg=name):
                build_filters([{"field": name, "value": 1}], self.config)


class TestDescription(unittest.TestCase):
    """Ce que la barre d'etat et le manifeste affichent."""

    def test_each_operator_has_a_readable_sign(self):
        for operator, sign in (("eq", "="), ("ne", "≠"), ("in", "∈"),
                               ("not_in", "∉"), ("gt", ">"), ("gte", "≥"),
                               ("lt", "<"), ("lte", "≤"),
                               ("contains", "contient")):
            described = Filter("grade", operator, ["G5"]).describe()
            self.assertIn(sign, described, operator)

    def test_a_list_is_written_out(self):
        self.assertIn("G5, G6",
                      Filter("grade", "in", ["G5", "G6"]).describe())

    def test_the_field_takes_its_declared_label(self):
        described = Filter("grade", "eq", "G5").describe({"grade": "Niveau"})
        self.assertIn("Niveau", described)

    def test_no_filter_is_said_plainly(self):
        self.assertEqual(describe_filters([]), "Aucun filtre")

    def test_several_filters_are_joined(self):
        text = describe_filters([Filter("grade", "eq", "G5"),
                                 Filter("business_unit", "eq", "France")])
        self.assertIn(" + ", text)


class TestSplitting(unittest.TestCase):
    """Le decoupage par dimension, simple et croise."""

    def test_a_dimension_gives_one_group_per_value(self):
        groups = split_by(population(), "business_unit")
        self.assertEqual(sorted(groups), ["Benelux", "France", "Iberia"])
        self.assertEqual(len(groups["France"]), 2)

    def test_groups_are_sorted_by_label(self):
        self.assertEqual(list(split_by(population(), "grade")),
                         ["G3", "G4", "G5", "G7", "G9"])

    def test_an_empty_value_is_left_out_by_default(self):
        people = build_population([make_row(1, business_unit=""),
                                   make_row(2, business_unit="France")])
        self.assertEqual(list(split_by(people, "business_unit")), ["France"])

    def test_an_empty_value_can_be_kept_apart(self):
        people = build_population([make_row(1, business_unit=""),
                                   make_row(2, business_unit="France")])
        groups = split_by(people, "business_unit", include_empty=True)
        self.assertEqual(sorted(groups), ["(non renseigne)", "France"])

    def test_two_dimensions_cross(self):
        groups = split_by(population(), ["business_unit", "grade"])
        self.assertIn("France · G5", groups)
        self.assertEqual(len(groups["France · G5"]), 1)

    def test_a_missing_value_empties_the_crossed_key(self):
        """Un salarie sans grade ne doit pas former la categorie
        « France · » : confondre les deux diluerait l'ecart cherche."""
        people = build_population([make_row(1, business_unit="France",
                                            grade="")])
        self.assertEqual(cross_key(people.employees[0],
                                   ["business_unit", "grade"]), "")


if __name__ == "__main__":
    unittest.main()
