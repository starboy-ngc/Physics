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


class TestReadingTheElementsFile(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration()

    def _table(self, headers, rows):
        from hr_analytics.io.tabular import Table
        return Table(headers=list(headers), rows=[list(r) for r in rows])

    def test_the_three_columns_that_matter_are_recognised(self):
        from hr_analytics.core.package import read_lines

        table = self._table(["Matricule", "Libellé", "Montant"],
                            [["A1", "Prime de résultat", "1 200,50 €"]])
        lignes, mapping = read_lines(table, self.config)
        self.assertEqual(len(lignes), 1)
        self.assertEqual(lignes[0].employee_id, "A1")
        self.assertEqual(lignes[0].amount, 1200.50)
        self.assertIsNone(lignes[0].day)
        self.assertEqual(sorted(mapping.field_to_index),
                         ["amount", "employee_id", "label"])

    def test_a_file_without_a_payroll_number_is_refused_by_name(self):
        """« Colonne obligatoire absente » laisse chercher : le message
        nomme ce qui manque et ce que l'outil a vu à la place."""
        from hr_analytics.core.package import read_lines

        table = self._table(["Nom", "Libellé", "Montant"],
                            [["Dupont", "Prime", "100"]])
        with self.assertRaises(ConfigError) as refus:
            read_lines(table, self.config)
        self.assertIn("matricule", refus.exception.message)
        self.assertIn("Nom", refus.exception.message)

    def test_an_unreadable_amount_travels_and_is_counted_later(self):
        """Un fichier de paie porte toujours quelques lignes de total ou
        de séparation : s'arrêter à la première ferait d'un détail un
        échec."""
        from hr_analytics.core.package import read_lines

        table = self._table(["Matricule", "Libellé", "Montant"],
                            [["A1", "Prime", "n/a"],
                             ["A2", "Prime", "300"]])
        lignes, _m = read_lines(table, self.config)
        self.assertEqual(len(lignes), 2)
        self.assertIsNone(lignes[0].amount)

    def test_an_empty_row_is_skipped(self):
        from hr_analytics.core.package import read_lines

        table = self._table(["Matricule", "Libellé", "Montant"],
                            [["A1", "Prime", "300"], ["", "", ""]])
        lignes, _m = read_lines(table, self.config)
        self.assertEqual(len(lignes), 1)

    def test_the_observed_dates_are_a_proposal_not_a_truth(self):
        """Si aucune prime n'a été versée en janvier, les bornes observées
        commencent en février — et la période réelle commence pourtant en
        janvier. C'est à un humain de trancher."""
        from hr_analytics.core.package import observed_period

        lignes = [Line("A", "Prime", 100.0, dt.date(2025, 2, 10)),
                  Line("B", "Prime", 200.0, dt.date(2025, 11, 4))]
        propose = observed_period(lignes)
        self.assertEqual(propose.start, dt.date(2025, 2, 10))
        self.assertEqual(propose.end, dt.date(2025, 11, 4))
        self.assertIsNone(observed_period([Line("A", "Prime", 100.0)]))


def gens(nombre, sexe_de, salaire=2000.0, metier="Conducteur",
         entree=dt.date(2015, 1, 1), prefixe="M"):
    return [Employee(row_number=rang, employee_id=f"{prefixe}{rang}",
                     base_salary=salaire, hire_date=entree, fte=1.0,
                     gender=sexe_de(rang), job=metier)
            for rang in range(nombre)]


def peuple(nombre, sexe_de, salaire=2000.0, metier="Conducteur",
           entree=dt.date(2015, 1, 1), prefixe="M"):
    return Population(gens(nombre, sexe_de, salaire, metier, entree, prefixe))


class TestTheTableOfSegments(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration()
        self.an = Period(dt.date(2025, 1, 1), dt.date(2025, 12, 31))

    def _packages(self, population, totaux):
        from hr_analytics.core.package import packages_of
        return packages_of(population, totaux, self.config, self.an)

    def test_a_segment_reports_who_is_served_not_only_how_much(self):
        from hr_analytics.core.package import segment_rows

        population = peuple(20, lambda r: "H")
        totaux = {f"M{r}": {"variable": 1200.0} for r in range(12)}
        lignes = segment_rows(self._packages(population, totaux),
                              self.config, "job")
        self.assertEqual(len(lignes), 1)
        ligne = lignes[0]
        self.assertEqual(ligne["headcount"], 20)
        self.assertEqual(ligne["served"], 12)
        self.assertEqual(ligne["served_share"], 60.0)
        self.assertEqual(ligne["variable_median"], 1200.0)

    def test_a_small_segment_publishes_nothing(self):
        from hr_analytics.core.package import segment_rows

        population = peuple(3, lambda r: "H")
        totaux = {f"M{r}": {"variable": 900.0} for r in range(3)}
        ligne = segment_rows(self._packages(population, totaux),
                             self.config, "job")[0]
        self.assertFalse(ligne["published"])
        self.assertIsNone(ligne["variable_median"])
        # L'effectif, lui, se dit : c'est le masquage qui s'explique.
        self.assertEqual(ligne["headcount"], 3)

    def test_the_gap_is_masked_on_the_served_not_on_the_headcount(self):
        """Un métier de quarante femmes dont trois sont servies
        publierait sinon la prime de trois personnes."""
        from hr_analytics.core.package import segment_rows

        population = peuple(40, lambda r: "F" if r < 20 else "H")
        totaux = {f"M{r}": {"variable": 1000.0} for r in range(3)}
        totaux.update({f"M{r}": {"variable": 1000.0} for r in range(20, 30)})
        ligne = segment_rows(self._packages(population, totaux),
                             self.config, "job")[0]
        self.assertEqual(ligne["by_sex"]["female"]["served"], 3)
        self.assertEqual(ligne["by_sex"]["male"]["served"], 10)
        self.assertIsNone(ligne["variable_gap"])

    def test_the_gap_is_negative_when_women_receive_less(self):
        from hr_analytics.core.package import segment_rows

        population = peuple(40, lambda r: "F" if r < 20 else "H")
        totaux = {f"M{r}": {"variable": 800.0} for r in range(10)}
        totaux.update({f"M{r}": {"variable": 1000.0} for r in range(20, 30)})
        ligne = segment_rows(self._packages(population, totaux),
                             self.config, "job")[0]
        self.assertAlmostEqual(ligne["variable_gap"], -20.0, places=1)

    def test_the_strongest_share_comes_first(self):
        from hr_analytics.core.package import segment_rows

        population = Population(
            gens(12, lambda r: "H", metier="Commercial", prefixe="C")
            + gens(12, lambda r: "H", metier="Cariste", prefixe="K"))
        totaux = {}
        for rang, personne in enumerate(population):
            montant = 3000.0 if personne.value("job") == "Commercial" else 200.0
            totaux[str(personne.value("employee_id"))] = {"variable": montant}
        lignes = segment_rows(self._packages(population, totaux),
                              self.config, "job")
        self.assertEqual(lignes[0]["segment"], "Commercial")


    def test_a_payroll_number_held_twice_is_set_aside_not_silently_merged(self):
        """À quel salarié rattacher une prime portant ce matricule ? Les
        garder reviendrait à laisser l'ordre des lignes décider d'une
        rémunération."""
        from hr_analytics.core.package import aggregate

        population = Population(
            gens(3, lambda r: "H", prefixe="M")
            + gens(1, lambda r: "F", prefixe="M"))
        _totaux, compte = aggregate([Line("M0", "Prime", 500.0)], population,
                                    {}, self.an)
        self.assertEqual(compte.duplicate_ids, ["M0"])
        self.assertEqual(compte.population, 2)
        self.assertEqual(compte.matched, 0)


class TestTheDetailOfOneSegment(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration()
        self.an = Period(dt.date(2025, 1, 1), dt.date(2025, 12, 31))
        self.population = peuple(40, lambda r: "F" if r < 20 else "H")
        self.totaux = {f"M{r}": {"variable": 1000.0, "fixe": 150.0}
                       for r in range(30)}

    def _membres(self):
        from hr_analytics.core.package import packages_of
        return packages_of(self.population, self.totaux, self.config, self.an)

    def test_the_composition_is_given_for_the_whole_and_each_sex(self):
        from hr_analytics.core.package import composition

        lignes = composition(self._membres(), self.config)
        self.assertEqual([l["label"] for l in lignes],
                         ["Ensemble", "Femmes", "Hommes"])
        self.assertTrue(all(l["published"] for l in lignes))
        self.assertAlmostEqual(lignes[0]["base"], 24000.0, delta=60)

    def test_a_sex_below_the_threshold_publishes_nothing(self):
        from hr_analytics.core.package import composition

        population = peuple(20, lambda r: "F" if r < 2 else "H")
        from hr_analytics.core.package import packages_of
        membres = packages_of(population, {}, self.config, self.an)
        femmes = composition(membres, self.config)[1]
        self.assertFalse(femmes["published"])
        self.assertIsNone(femmes["base"])

    def test_the_spread_covers_the_served_only(self):
        """Y compter ceux qui n'ont rien touché écraserait le premier
        quartile à zéro, et ferait passer une question de distribution
        pour une question de couverture."""
        from hr_analytics.core.package import spread

        bornes = spread(self._membres(), self.config)
        self.assertEqual(bornes["count"], 30)
        self.assertEqual(bornes["min"], 1000.0)

    def test_the_spread_is_absent_below_the_threshold(self):
        from hr_analytics.core.package import packages_of, spread

        population = peuple(20, lambda r: "H")
        membres = packages_of(population, {"M0": {"variable": 10.0}},
                              self.config, self.an)
        self.assertIsNone(spread(membres, self.config))

    def test_the_elements_name_their_nature_and_the_excluded_shows(self):
        """Sans cette ligne, le classement des intitulés serait un réglage
        dont personne ne verrait jamais l'effet."""
        from hr_analytics.core.package import element_rows

        lignes = []
        for rang in range(20):
            lignes.append(Line(f"M{rang}", "Prime de résultat", 600.0))
            lignes.append(Line(f"M{rang}", "Indemnités", 90.0))
        rows = element_rows(lignes, self._membres(), self.config, self.an,
                            {"indemnites": "exclu"})
        par_nom = {row["label"]: row for row in rows}
        self.assertEqual(par_nom["Prime de résultat"]["nature"], "variable")
        self.assertEqual(par_nom["Indemnités"]["nature"], "exclu")
        # Un élément exclu n'a ni médiane ni écart : le montrer chiffré
        # laisserait croire qu'il compte quelque part.
        self.assertIsNone(par_nom["Indemnités"]["median"])
        self.assertFalse(par_nom["Indemnités"]["counted"])
        self.assertEqual(rows[-1]["label"], "Indemnités")

    def test_several_payments_of_one_element_add_up_before_the_median(self):
        """Sinon une prime trimestrielle paraîtrait quatre fois plus
        petite qu'une prime annuelle de même total."""
        from hr_analytics.core.package import element_rows

        lignes = []
        for rang in range(20):
            for _ in range(4):
                lignes.append(Line(f"M{rang}", "Prime trimestrielle", 250.0))
        row = element_rows(lignes, self._membres(), self.config, self.an, {})[0]
        self.assertEqual(row["beneficiaries"], 20)
        self.assertEqual(row["median"], 1000.0)


class TestWhenTheWorkingTimeIsMissing(unittest.TestCase):
    """Un fichier dont la colonne de temps de travail n'est pas reconnue
    donnait un écran entièrement vide, et rien n'en disait la raison."""

    def setUp(self):
        self.config = load_configuration()
        self.an = Period(dt.date(2025, 1, 1), dt.date(2025, 12, 31))

    def test_without_working_time_there_is_no_share_and_the_count_says_so(self):
        from hr_analytics.core.package import (coverage, packages_of,
                                               segment_rows)

        sans_temps = Population([
            Employee(row_number=r, employee_id=f"M{r}", base_salary=2000.0,
                     hire_date=dt.date(2015, 1, 1), gender="H",
                     job="Conduite", fte=None) for r in range(20)])
        totaux = {f"M{r}": {"variable": 900.0} for r in range(20)}
        paquets = packages_of(sans_temps, totaux, self.config, self.an)

        compte = coverage(paquets)
        self.assertEqual(compte["with_base"], 0)
        self.assertEqual(compte["without_base"], 20)

        ligne = segment_rows(paquets, self.config, "job")[0]
        self.assertIsNone(ligne["variable_share"])
        self.assertEqual(ligne["base_known"], 0)
        # Le montant, lui, reste connu : c'est la part qui manque, pas le
        # variable.
        self.assertEqual(ligne["variable_median"], 900.0)

    def test_with_working_time_the_share_is_there(self):
        from hr_analytics.core.package import (coverage, packages_of,
                                               segment_rows)

        population = peuple(20, lambda r: "H")
        totaux = {f"M{r}": {"variable": 2400.0} for r in range(20)}
        paquets = packages_of(population, totaux, self.config, self.an)
        self.assertEqual(coverage(paquets)["without_base"], 0)
        ligne = segment_rows(paquets, self.config, "job")[0]
        self.assertEqual(ligne["base_known"], 20)
        self.assertAlmostEqual(ligne["variable_share"], 9.09, places=1)
