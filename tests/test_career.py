"""La fiche d'un salarié : sa place parmi ses pairs, et son historique.

Aucune donnée réelle : les populations et les historiques sont fabriqués
ici.
"""

import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_analytics.core.career import (Entry, ROLES, column_roles, evolution,
                                      organise, parse_period, read_history,
                                      role_of, standing)
from hr_analytics.core.config import load_configuration
from hr_analytics.core.errors import ConfigError
from hr_analytics.core.normalize import Employee, Population


def salarie(matricule, salaire, poste="Exploitant", fte=1.0):
    # « job_title » n'est pas un champ natif : il se range dans `extra`,
    # comme toute notion declaree par la configuration.
    personne = Employee(row_number=0, employee_id=matricule,
                        base_salary=salaire, fte=fte)
    personne.assign("job_title", poste)
    return personne


def table(headers, rows):
    from hr_analytics.io.tabular import Table

    return Table(headers=list(headers), rows=[list(r) for r in rows])


class TestThePeriod(unittest.TestCase):
    def test_a_year_becomes_its_last_day(self):
        """Un historique annuel donne l'état en fin d'exercice : choisir
        le 1er janvier ferait remonter chaque point d'un an."""
        jour, libelle = parse_period("2024")
        self.assertEqual(jour, dt.date(2024, 12, 31))
        self.assertEqual(libelle, "2024")

    def test_the_label_keeps_what_the_file_wrote(self):
        """Afficher « 31/12/2024 » là où le fichier dit « 2024 » ferait
        croire à une précision qu'il n'a pas."""
        self.assertEqual(parse_period("2024")[1], "2024")
        self.assertEqual(parse_period("30/06/2024")[1], "30/06/2024")

    def test_the_three_usual_forms_are_read(self):
        for ecrit, attendu in (("2024-06-30", dt.date(2024, 6, 30)),
                               ("30/06/2024", dt.date(2024, 6, 30)),
                               ("2024", dt.date(2024, 12, 31))):
            self.assertEqual(parse_period(ecrit)[0], attendu, ecrit)

    def test_an_unreadable_period_says_so_without_losing_the_text(self):
        jour, libelle = parse_period("T4")
        self.assertIsNone(jour)
        self.assertEqual(libelle, "T4")

    def test_a_number_that_is_not_a_year_is_not_a_period(self):
        self.assertIsNone(parse_period("12")[0])
        self.assertIsNone(parse_period("3000000")[0])


class TestTheRoles(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration()

    def test_an_unclassified_column_is_ignored_not_summed(self):
        """Additionner une colonne qu'on n'a pas regardée fausserait une
        rémunération ; l'oublier se voit — la courbe manque."""
        self.assertEqual(role_of("Colonne inconnue", {}), "ignoree")

    def test_accents_and_case_do_not_make_two_columns(self):
        regles = {"remuneration totale": "ignoree"}
        self.assertEqual(role_of("Rémunération Totale", regles), "ignoree")

    def test_an_unknown_role_is_refused_by_name(self):
        self.config._data["career_parameters"]["columns"] = {
            "Prime": "bonus"}
        with self.assertRaises(ConfigError) as refus:
            column_roles(self.config)
        self.assertIn("bonus", refus.exception.message)
        self.assertIn("Prime", refus.exception.message)

    def test_the_two_roles_are_those_the_screen_offers(self):
        """La fiche ne traite que de rémunération : ce qui est un
        montant, et ce dont on n'a rien à faire."""
        self.assertEqual(ROLES, ("montant", "ignoree"))

    def test_a_role_from_a_previous_version_does_not_block_the_start(self):
        """Un fichier de paramètres écrit avant le retrait des
        appréciations ne doit pas empêcher l'outil de démarrer : la
        colonne cesse de compter, ce qui est ce que le retrait veut
        dire."""
        self.config._data["career_parameters"]["columns"] = {
            "Performance": "appreciation"}
        self.assertEqual(column_roles(self.config),
                         {"performance": "ignoree"})


class TestReadingTheHistory(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration()
        self.config._data["career_parameters"]["columns"] = {
            "Salaire de base": "montant",
            "Avantage en nature": "montant",
            "Primes": "montant",
            "Performance": "ignoree",
        }

    def test_the_free_columns_are_offered_in_the_order_of_the_file(self):
        """On ne demande à personne d'écrire le nom de ses propres
        colonnes."""
        _e, _m, libres = read_history(
            table(["Matricule", "Période", "Salaire de base", "Primes",
                   "Performance"],
                  [["A1", "2024", "2000", "300", "B"]]), self.config)
        self.assertEqual(libres, ["Salaire de base", "Primes", "Performance"])

    def test_only_the_declared_amounts_are_kept(self):
        entries, _m, _l = read_history(
            table(["Matricule", "Période", "Salaire de base", "Performance"],
                  [["A1", "2024", "2 000,50", "B"]]), self.config)
        self.assertEqual(entries[0].amounts, {"Salaire de base": 2000.50})

    def test_an_unclassified_column_enters_neither(self):
        entries, _m, _l = read_history(
            table(["Matricule", "Période", "Salaire de base", "Commentaire"],
                  [["A1", "2024", "2000", "RAS"]]), self.config)
        self.assertEqual(entries[0].amounts, {"Salaire de base": 2000.0})

    def test_a_file_without_a_period_is_refused_by_name(self):
        with self.assertRaises(ConfigError) as refus:
            read_history(table(["Matricule", "Salaire de base"],
                               [["A1", "2000"]]), self.config)
        self.assertIn("période", refus.exception.message)
        self.assertIn("Salaire de base", refus.exception.message)

    def test_no_amount_at_all_is_a_hole_not_a_zero(self):
        """Une période sans aucun montant lisible est un trou dans
        l'historique, et un trou ne se trace pas comme un zéro."""
        entries, _m, _l = read_history(
            table(["Matricule", "Période", "Salaire de base"],
                  [["A1", "2024", ""]]), self.config)
        self.assertIsNone(entries[0].total)
        self.assertEqual(Entry("A", None, "2024", {"x": 0.0}).total, 0.0)


class TestOrganisingTheHistory(unittest.TestCase):
    def setUp(self):
        self.population = Population([salarie("A", 2000.0),
                                      salarie("B", 2400.0)])

    def test_the_periods_come_back_in_order(self):
        entries = [Entry("A", dt.date(2025, 12, 31), "2025"),
                   Entry("A", dt.date(2023, 12, 31), "2023"),
                   Entry("A", dt.date(2024, 12, 31), "2024")]
        par_salarie, compte = organise(entries, self.population)
        self.assertEqual([e.label for e in par_salarie["A"]],
                         ["2023", "2024", "2025"])
        self.assertEqual(compte.periods, ["2023", "2024", "2025"])

    def test_an_unknown_payroll_number_is_named_not_swallowed(self):
        entries = [Entry("ZZZ", dt.date(2024, 12, 31), "2024")]
        _par, compte = organise(entries, self.population)
        self.assertEqual(compte.orphan_ids, ["ZZZ"])
        self.assertEqual(compte.matched, 0)

    def test_an_unreadable_period_is_counted_not_dropped_in_silence(self):
        """Un historique dont un dixième des dates ne se lit pas rendrait
        une courbe à trous dont personne ne saurait d'où viennent les
        trous."""
        entries = [Entry("A", None, "T4"),
                   Entry("A", dt.date(2024, 12, 31), "2024")]
        par_salarie, compte = organise(entries, self.population)
        self.assertEqual(compte.unreadable, 1)
        self.assertEqual(len(par_salarie["A"]), 1)


class TestTheEvolution(unittest.TestCase):
    def test_the_change_is_given_in_amount_and_in_share(self):
        """Trente euros sur mille cinq cents n'est pas trente euros sur
        six mille, et deux pour cent ne disent pas s'il s'agit de trente
        euros ou de trois cents."""
        lignes = evolution([
            Entry("A", dt.date(2023, 12, 31), "2023", {"Base": 2000.0}),
            Entry("A", dt.date(2024, 12, 31), "2024", {"Base": 2100.0})])
        self.assertIsNone(lignes[0]["change"])
        self.assertEqual(lignes[1]["change"], 100.0)
        self.assertAlmostEqual(lignes[1]["change_share"], 5.0)

    def test_a_period_without_an_amount_does_not_break_the_series(self):
        """Elle n'a pas d'écart, et la suivante se compare à la dernière
        période chiffrée."""
        lignes = evolution([
            Entry("A", dt.date(2023, 12, 31), "2023", {"Base": 2000.0}),
            Entry("A", dt.date(2024, 12, 31), "2024", {}),
            Entry("A", dt.date(2025, 12, 31), "2025", {"Base": 2200.0})])
        self.assertIsNone(lignes[1]["change"])
        self.assertEqual(lignes[2]["change"], 200.0)

    def test_the_amounts_of_a_period_travel_with_it(self):
        lignes = evolution([
            Entry("A", dt.date(2024, 12, 31), "2024",
                  {"Base": 2000.0, "Primes": 300.0})])
        self.assertEqual(lignes[0]["amounts"],
                         {"Base": 2000.0, "Primes": 300.0})
        self.assertEqual(lignes[0]["total"], 2300.0)


class TestWhereSomeoneStands(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration()

    def _groupe(self, montants, poste="Exploitant"):
        return Population([salarie(f"M{rang}", montant, poste)
                           for rang, montant in enumerate(montants)])

    def test_the_ratio_compares_two_jobs_that_pay_differently(self):
        """0,92 veut dire « huit pour cent sous ses pairs », que le métier
        paie mille cinq cents ou six mille."""
        petit = self._groupe([1000, 1200, 1250, 1300, 1400, 1500])
        grand = self._groupe([5000, 6000, 6250, 6500, 7000, 7500])
        a = standing(list(petit)[2], petit, self.config, "job_title")
        b = standing(list(grand)[2], grand, self.config, "job_title")
        self.assertAlmostEqual(a["ratio"], b["ratio"], places=6)

    def test_a_group_too_small_publishes_nothing(self):
        """Comparer quelqu'un à trois collègues, c'est publier la
        rémunération de ces trois-là à travers la sienne."""
        groupe = self._groupe([2000, 2100, 2200])
        place = standing(list(groupe)[0], groupe, self.config, "job_title")
        self.assertFalse(place["published"])
        self.assertEqual(place["headcount"], 3)
        self.assertNotIn("median", place)

    def test_the_gap_and_the_rank_say_two_different_things(self):
        groupe = self._groupe([1000, 2000, 2000, 2000, 2000, 9000])
        milieu = standing(list(groupe)[1], groupe, self.config, "job_title")
        self.assertEqual(milieu["median"], 2000.0)
        self.assertEqual(milieu["gap"], 0.0)
        # À la médiane, mais il dépasse déjà cinq pairs sur six.
        self.assertAlmostEqual(milieu["rank"], 500.0 / 6, places=3)

    def test_the_lowest_paid_is_not_below_himself(self):
        groupe = self._groupe([2000, 2100, 2200, 2300, 2400, 2500])
        place = standing(list(groupe)[0], groupe, self.config, "job_title")
        self.assertGreater(place["rank"], 0.0)

    def test_a_part_time_salary_is_compared_at_full_time(self):
        """Sinon on compare d'abord un temps de travail."""
        gens = [salarie(f"M{r}", 2000.0) for r in range(5)]
        gens.append(salarie("X", 1000.0, fte=0.5))
        groupe = Population(gens)
        place = standing(gens[-1], groupe, self.config, "job_title")
        self.assertEqual(place["amount"], 2000.0)
        self.assertEqual(place["gap"], 0.0)

    def test_without_a_salary_there_is_nothing_to_situate(self):
        groupe = self._groupe([2000, 2100, 2200, 2300, 2400, 2500])
        sans = salarie("X", None)
        self.assertIsNone(standing(sans, groupe, self.config, "job_title"))


if __name__ == "__main__":
    unittest.main()
