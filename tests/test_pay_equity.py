"""Ecarts de remuneration entre les sexes.

Le decoupage suit la directive europeenne 2023/970. Les tests fixent trois
choses : la convention de signe, la tolerance aux ecritures du fichier
source, et le refus de publier un ecart calcule sur trop peu de monde — un
ecart etabli sur une seule femme reviendrait a afficher sa remuneration.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from compensation_analytics.core.pay_equity import (FEMALE, MALE, classify,
                                                    calculate_pay_equity)


def population(entries, config):
    """entries : liste de (sexe, salaire, poste)."""
    rows = [make_row(index, gender=gender, salary=salary, grade="G4")
            for index, (gender, salary, _job) in enumerate(entries)]
    return build_population(rows, config)


class TestReadingTheGenderColumn(unittest.TestCase):
    def test_the_accepted_spellings_come_from_the_configuration(self):
        """Un fichier RH ecrit « F/H », « F/M » ou « Femme/Homme » selon
        l'outil qui l'a produit : rien de tout cela n'est code en dur."""
        female = ["F", "Femme", "Female"]
        male = ["H", "M", "Homme"]
        for value in ("F", "f", "Femme", "FEMME", " female "):
            self.assertEqual(classify(value, female, male), FEMALE, value)
        for value in ("H", "m", "Homme", "HOMME"):
            self.assertEqual(classify(value, female, male), MALE, value)

    def test_accents_do_not_matter(self):
        self.assertEqual(classify("FEMME", ["Femme"], ["Homme"]), FEMALE)

    def test_an_unknown_value_joins_neither_group(self):
        """La ranger arbitrairement fausserait l'ecart sans que rien ne le
        montre."""
        for value in ("", "N/R", "Autre", None, "X"):
            self.assertEqual(classify(value, ["F"], ["H"]), "")


class TestTheGap(unittest.TestCase):
    def setUp(self):
        self.config = make_config()

    def test_a_positive_gap_means_women_are_paid_less(self):
        entries = ([("F", 40000, "A")] * 10) + ([("H", 50000, "A")] * 10)
        result = calculate_pay_equity(population(entries, self.config),
                                      self.config)
        self.assertTrue(result["available"])
        # (50000 - 40000) / 50000 = 20 %
        self.assertAlmostEqual(result["pay"]["mean_gap"], 20.0, places=6)
        self.assertAlmostEqual(result["pay"]["median_gap"], 20.0, places=6)

    def test_a_negative_gap_means_men_are_paid_less(self):
        entries = ([("F", 50000, "A")] * 10) + ([("H", 40000, "A")] * 10)
        result = calculate_pay_equity(population(entries, self.config),
                                      self.config)
        self.assertLess(result["pay"]["mean_gap"], 0)

    def test_equal_pay_gives_no_gap(self):
        entries = ([("F", 45000, "A")] * 10) + ([("H", 45000, "A")] * 10)
        result = calculate_pay_equity(population(entries, self.config),
                                      self.config)
        self.assertAlmostEqual(result["pay"]["mean_gap"], 0.0, places=6)

    def test_unknown_sexes_are_counted_but_excluded_from_the_gap(self):
        entries = (([("F", 40000, "A")] * 10) + ([("H", 50000, "A")] * 10)
                   + ([("X", 90000, "A")] * 4))
        result = calculate_pay_equity(population(entries, self.config),
                                      self.config)
        self.assertEqual(result["unknown_count"], 4)
        self.assertAlmostEqual(result["pay"]["mean_gap"], 20.0, places=6)


class TestPrivacy(unittest.TestCase):
    def setUp(self):
        self.config = make_config()

    def test_no_gap_is_published_when_one_group_is_too_small(self):
        """Un ecart etabli sur une seule femme afficherait sa remuneration."""
        entries = ([("F", 40000, "A")] * 2) + ([("H", 50000, "A")] * 30)
        result = calculate_pay_equity(population(entries, self.config),
                                      self.config)
        self.assertFalse(result["available"])
        self.assertIn("Effectif insuffisant", result["warning"])
        self.assertNotIn("pay", result)

    def test_a_small_category_is_masked_but_still_counted(self):
        config = make_config()
        rows = ([make_row(index, gender="F", salary=40000, grade="G4")
                 for index in range(10)]
                + [make_row(10 + index, gender="H", salary=50000, grade="G4")
                   for index in range(10)]
                + [make_row(20 + index, gender="F", salary=90000, grade="G8")
                   for index in range(2)]
                + [make_row(22 + index, gender="H", salary=95000, grade="G8")
                   for index in range(2)])
        config = make_config({"pay_equity_parameters.category_field": "grade"})
        result = calculate_pay_equity(build_population(rows, config), config)
        small = [item for item in result["categories"]
                 if item["category"] == "G8"][0]
        self.assertFalse(small["published"])
        self.assertIsNone(small["mean_gap"])
        self.assertEqual(small["headcount"], 4)


class TestQuartiles(unittest.TestCase):
    def test_the_lowest_quartile_comes_first(self):
        """Une repartition desequilibree entre le quartile bas et le
        quartile haut est le signal le plus direct d'un plafond de verre."""
        config = make_config()
        entries = ([("F", 30000, "A")] * 20) + ([("H", 60000, "A")] * 20)
        result = calculate_pay_equity(population(entries, config), config)
        quartiles = result["quartiles"]
        self.assertEqual(len(quartiles), 4)
        self.assertEqual(quartiles[0]["quartile"], 1)
        self.assertAlmostEqual(quartiles[0]["female_share"], 100.0, places=6)
        self.assertAlmostEqual(quartiles[-1]["male_share"], 100.0, places=6)

    def test_the_number_of_quartiles_is_configurable(self):
        config = make_config({"pay_equity_parameters.quartile_count": 5})
        entries = ([("F", 30000, "A")] * 25) + ([("H", 60000, "A")] * 25)
        result = calculate_pay_equity(population(entries, config), config)
        self.assertEqual(len(result["quartiles"]), 5)


class TestCategories(unittest.TestCase):
    def test_a_gap_above_the_threshold_is_flagged(self):
        """Au-dela du seuil, la directive impose une evaluation conjointe
        faute de justification objective."""
        config = make_config({"pay_equity_parameters.category_field": "grade",
                              "pay_equity_parameters.gap_alert_threshold": 5.0})
        rows = ([make_row(index, gender="F", salary=40000, grade="G4")
                 for index in range(10)]
                + [make_row(10 + index, gender="H", salary=50000, grade="G4")
                   for index in range(10)]
                + [make_row(20 + index, gender="F", salary=45000, grade="G6")
                   for index in range(10)]
                + [make_row(30 + index, gender="H", salary=45100, grade="G6")
                   for index in range(10)])
        result = calculate_pay_equity(build_population(rows, config), config)
        flagged = {item["category"]: item["above_threshold"]
                   for item in result["categories"]}
        self.assertTrue(flagged["G4"])
        self.assertFalse(flagged["G6"])
        self.assertEqual(result["categories_above_threshold"], 1)

    def test_a_gap_favouring_women_is_flagged_too(self):
        """Le seuil porte sur l'ecart absolu : un desequilibre marque
        appelle un examen dans les deux sens."""
        config = make_config({"pay_equity_parameters.category_field": "grade"})
        rows = ([make_row(index, gender="F", salary=60000, grade="G4")
                 for index in range(10)]
                + [make_row(10 + index, gender="H", salary=40000, grade="G4")
                   for index in range(10)])
        result = calculate_pay_equity(build_population(rows, config), config)
        self.assertTrue(result["categories"][0]["above_threshold"])
        self.assertLess(result["categories"][0]["mean_gap"], 0)

    def test_an_absent_category_field_says_so(self):
        """Une table vide laisserait croire a une absence d'ecart, alors que
        le champ n'existe pas dans le fichier."""
        config = make_config(
            {"pay_equity_parameters.category_field": "job_title"})
        entries = ([("F", 40000, "A")] * 10) + ([("H", 50000, "A")] * 10)
        result = calculate_pay_equity(population(entries, config), config)
        self.assertEqual(result["categories"], [])
        self.assertIn("n'est renseigné", result["category_warning"])

    def test_the_widest_gaps_come_first(self):
        config = make_config({"pay_equity_parameters.category_field": "grade"})
        rows = []
        for index, (grade, female_pay) in enumerate(
                (("G3", 49000), ("G5", 30000), ("G7", 45000))):
            rows += [make_row(index * 100 + step, gender="F",
                              salary=female_pay, grade=grade)
                     for step in range(10)]
            rows += [make_row(index * 100 + 50 + step, gender="H",
                              salary=50000, grade=grade) for step in range(10)]
        result = calculate_pay_equity(build_population(rows, config), config)
        gaps = [abs(item["mean_gap"]) for item in result["categories"]]
        self.assertEqual(gaps, sorted(gaps, reverse=True))


if __name__ == "__main__":
    unittest.main()
