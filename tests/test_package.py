"""Le package de rémunération : période, natures, rapprochement.

Ces essais portent sur la règle qui décide de tout le module : un salaire
est un état, une prime est un flux, et c'est le salaire qu'on ramène à la
période — jamais la prime qu'on annualise.

Aucune donnée réelle : les populations sont construites ici.
"""

import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_analytics.core.config import load_configuration
from hr_analytics.core.errors import ConfigError
from hr_analytics.core.normalize import Employee, Population
from hr_analytics.core.package import (COMPTEES, NATURES, Line, Period,
                                       aggregate, classify, employee_package,
                                       labels_of, nature_rules)


def salarie(matricule, salaire, entree, fte=1.0):
    return Employee(row_number=0, employee_id=matricule, base_salary=salaire,
                    hire_date=entree, fte=fte)


class TestThePeriod(unittest.TestCase):
    def test_a_period_counts_its_last_day(self):
        """Du 1er au 31 janvier, c'est un mois, pas trente jours."""
        janvier = Period(dt.date(2026, 1, 1), dt.date(2026, 1, 31))
        self.assertEqual(janvier.days, 31)
        self.assertAlmostEqual(janvier.months, 1.0, places=1)

    def test_a_single_day_is_not_nothing(self):
        jour = Period(dt.date(2026, 1, 1), dt.date(2026, 1, 1))
        self.assertEqual(jour.days, 1)

    def test_a_period_cannot_end_before_it_starts(self):
        with self.assertRaises(ConfigError) as refus:
            Period(dt.date(2026, 6, 1), dt.date(2026, 1, 1))
        self.assertIn("avant", refus.exception.message)

    def test_a_year_is_twelve_months_not_three_hundred_and_sixty(self):
        """Trente jours par mois perdent cinq jours sur l'année, soit un
        sixième de mois de salaire au dénominateur."""
        an = Period(dt.date(2025, 1, 1), dt.date(2025, 12, 31))
        self.assertAlmostEqual(an.months, 12.0, places=1)

    def test_the_rolling_year_stops_at_the_last_closed_month(self):
        """Une extraction du 8 septembre ne porte pas la paie de
        septembre : la période s'arrête au 31 août."""
        periode = Period.twelve_months_to(dt.date(2026, 9, 8))
        self.assertEqual(periode.start, dt.date(2025, 9, 1))
        self.assertEqual(periode.end, dt.date(2026, 8, 31))
        self.assertTrue(periode.complete)

    def test_the_rolling_year_holds_at_the_turn_of_the_year(self):
        periode = Period.twelve_months_to(dt.date(2026, 1, 15))
        self.assertEqual(periode.start, dt.date(2025, 1, 1))
        self.assertEqual(periode.end, dt.date(2025, 12, 31))

    def test_a_short_period_says_it_is_short(self):
        """En deçà de douze mois, une prime annuelle versée hors de la
        fenêtre n'apparaît pas : le taux de service se lirait comme une
        décision alors qu'il n'est qu'un effet du découpage."""
        neuf_mois = Period(dt.date(2026, 1, 1), dt.date(2026, 9, 30))
        self.assertFalse(neuf_mois.complete)
        self.assertAlmostEqual(neuf_mois.months, 9.0, places=0)


class TestTheNatures(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration()

    def test_an_unclassified_element_is_seen_not_lost(self):
        """Un élément qu'on oublie de classer doit se voir dans les
        chiffres, pas disparaître d'eux."""
        self.assertEqual(classify("Prime inconnue", {}), "variable")

    def test_accents_and_case_do_not_make_two_elements(self):
        regles = {"prime qualite": "variable"}
        self.assertEqual(classify("Prime Qualité", regles), "variable")
        self.assertEqual(classify("PRIME QUALITE", regles), "variable")

    def test_the_excluded_nature_counts_nowhere(self):
        """Un remboursement de frais n'est pas une rémunération :
        l'additionner gonflerait chaque écart sans que rien ne le dise."""
        self.assertIn("exclu", NATURES)
        self.assertNotIn("exclu", COMPTEES)

    def test_an_unknown_nature_is_refused_by_name(self):
        config = load_configuration()
        config._data.setdefault("package_parameters", {})["natures"] = {
            "Prime": "fantaisie"}
        with self.assertRaises(ConfigError) as refus:
            nature_rules(config)
        self.assertIn("fantaisie", refus.exception.message)
        self.assertIn("Prime", refus.exception.message)

    def test_the_labels_of_a_file_are_offered_in_order(self):
        """On ne demande pas à l'utilisateur d'inventer les intitulés de
        son fichier : on les lui montre."""
        lignes = [Line("1", "Prime de résultat", 100.0),
                  Line("2", "Prime qualité", 50.0),
                  Line("3", "PRIME DE RESULTAT", 80.0)]
        self.assertEqual(labels_of(lignes),
                         ["Prime de résultat", "Prime qualité"])


class TestAggregating(unittest.TestCase):
    def setUp(self):
        self.periode = Period(dt.date(2025, 1, 1), dt.date(2025, 12, 31))
        self.population = Population([
            salarie("A", 2000.0, dt.date(2020, 1, 1)),
            salarie("B", 2500.0, dt.date(2020, 1, 1)),
            # Entré en cours de période.
            salarie("C", 2200.0, dt.date(2025, 6, 1)),
        ])
        self.regles = {"prime de resultat": "variable",
                       "indemnites de deplacement": "exclu"}

    def test_several_lines_for_one_person_add_up(self):
        """Une prime trimestrielle donne quatre lignes : c'est la règle,
        pas l'exception."""
        lignes = [Line("A", "Prime de résultat", 250.0) for _ in range(4)]
        totaux, _compte = aggregate(lignes, self.population, self.regles,
                                    self.periode)
        self.assertEqual(totaux["A"]["variable"], 1000.0)

    def test_someone_who_arrived_mid_period_is_set_aside_and_counted(self):
        """Il n'a pas « rien touché » : il n'était pas là. L'inclure
        ferait baisser le taux de service sans qu'aucune décision de
        l'entreprise soit en cause."""
        lignes = [Line("A", "Prime de résultat", 500.0),
                  Line("C", "Prime de résultat", 300.0)]
        totaux, compte = aggregate(lignes, self.population, self.regles,
                                   self.periode)
        self.assertNotIn("C", totaux)
        self.assertEqual(compte.late_entrants, 1)
        self.assertEqual(compte.population, 2)

    def test_an_unknown_payroll_number_is_named_not_swallowed(self):
        lignes = [Line("ZZZ", "Prime de résultat", 400.0)]
        _totaux, compte = aggregate(lignes, self.population, self.regles,
                                    self.periode)
        self.assertEqual(compte.orphans, 1)
        self.assertEqual(compte.orphan_ids, ["ZZZ"])

    def test_the_count_says_who_has_nothing(self):
        lignes = [Line("A", "Prime de résultat", 400.0)]
        _totaux, compte = aggregate(lignes, self.population, self.regles,
                                    self.periode)
        self.assertEqual(compte.matched, 1)
        self.assertEqual(compte.without_lines, 1)

    def test_a_line_outside_the_period_is_set_aside(self):
        lignes = [Line("A", "Prime de résultat", 400.0,
                       dt.date(2024, 11, 30)),
                  Line("A", "Prime de résultat", 600.0,
                       dt.date(2025, 3, 15))]
        totaux, compte = aggregate(lignes, self.population, self.regles,
                                   self.periode)
        self.assertEqual(totaux["A"]["variable"], 600.0)
        self.assertEqual(compte.out_of_period, 1)

    def test_a_line_without_a_date_is_trusted_to_the_declared_period(self):
        """Un fichier sans colonne de date est le cas courant : c'est la
        période déclarée qui fait foi, sinon rien ne serait retenu."""
        lignes = [Line("A", "Prime de résultat", 400.0)]
        totaux, compte = aggregate(lignes, self.population, self.regles,
                                   self.periode)
        self.assertEqual(totaux["A"]["variable"], 400.0)
        self.assertEqual(compte.out_of_period, 0)

    def test_an_unreadable_line_is_counted_apart(self):
        lignes = [Line("", "Prime de résultat", 400.0),
                  Line("A", "Prime de résultat", None)]
        _totaux, compte = aggregate(lignes, self.population, self.regles,
                                    self.periode)
        self.assertEqual(compte.unreadable, 2)


class TestThePackageOfOnePerson(unittest.TestCase):
    def setUp(self):
        self.an = Period(dt.date(2025, 1, 1), dt.date(2025, 12, 31))
        self.regles = {"prime de resultat": "variable",
                       "indemnites": "exclu"}

    def test_the_salary_comes_down_to_the_period_the_bonus_never_goes_up(self):
        """C'est la règle du module. Une prime versée une fois l'an et vue
        dans une fenêtre de neuf mois deviendrait, multipliée par 12/9,
        une prime et demie — un chiffre que personne n'a versé."""
        personne = salarie("A", 2000.0, dt.date(2020, 1, 1))
        douze = employee_package(personne, {"variable": 3000.0},
                                 "base_salary", self.an)
        neuf = employee_package(
            personne, {"variable": 3000.0}, "base_salary",
            Period(dt.date(2025, 1, 1), dt.date(2025, 9, 30)))
        # Le variable est le même des deux côtés : il n'est jamais mis à
        # l'échelle. C'est la base qui suit la fenêtre.
        self.assertEqual(douze["variable"], 3000.0)
        self.assertEqual(neuf["variable"], 3000.0)
        # Neuf mois civils de 2025 font 273 jours, un peu moins que neuf
        # mois moyens : l'écart est réel, pas une approximation.
        self.assertAlmostEqual(douze["base"], 24000.0, delta=60)
        self.assertAlmostEqual(neuf["base"], 17939.0, delta=60)
        self.assertGreater(neuf["variable_share"], douze["variable_share"])

    def test_the_share_is_of_the_whole_not_of_the_base(self):
        personne = salarie("A", 1000.0, dt.date(2020, 1, 1))
        package = employee_package(personne, {"variable": 1200.0},
                                   "base_salary", self.an)
        # 12 000 de base, 1 200 de variable : 1 200 / 13 200.
        self.assertAlmostEqual(package["variable_share"], 9.09, places=1)

    def test_an_excluded_element_enters_nothing(self):
        personne = salarie("A", 2000.0, dt.date(2020, 1, 1))
        package = employee_package(personne,
                                   {"variable": 500.0, "exclu": 4000.0},
                                   "base_salary", self.an)
        self.assertEqual(package["added"], 500.0)
        self.assertNotIn("exclu", package["by_nature"])

    def test_a_part_time_salary_is_brought_to_full_time(self):
        """Sinon on mesure d'abord une différence de temps de travail."""
        mi_temps = salarie("A", 1000.0, dt.date(2020, 1, 1), fte=0.5)
        package = employee_package(mi_temps, {}, "base_salary", self.an)
        self.assertAlmostEqual(package["base"], 24000.0, delta=60)

    def test_without_a_salary_there_is_no_share_only_an_amount(self):
        """Un pourcentage sans dénominateur serait une invention."""
        sans = salarie("A", None, dt.date(2020, 1, 1))
        package = employee_package(sans, {"variable": 800.0},
                                   "base_salary", self.an)
        self.assertIsNone(package["base"])
        self.assertIsNone(package["total"])
        self.assertIsNone(package["variable_share"])
        self.assertEqual(package["variable"], 800.0)

    def test_someone_served_nothing_is_not_someone_served_zero(self):
        personne = salarie("A", 2000.0, dt.date(2020, 1, 1))
        self.assertFalse(
            employee_package(personne, {}, "base_salary", self.an)["served"])
        self.assertTrue(
            employee_package(personne, {"variable": 1.0}, "base_salary",
                             self.an)["served"])


if __name__ == "__main__":
    unittest.main()
