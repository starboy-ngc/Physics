"""Rémunération ramenée au temps plein.

Un fichier de paie porte le montant *verse* : un salarie a 80 % y figure
pour 80 % de son salaire. Comparer tel quel une population feminine plus
souvent a temps partiel a une population masculine plus souvent a temps
plein mesure d'abord le temps de travail, et seulement ensuite la
remuneration — et publie comme ecart de salaire ce qui n'en est pas un.

Deux choses doivent tenir : la colonne de temps de travail, qui s'ecrit de
trois facons selon le SIRH ; et le calcul, qui n'a de sens que si l'on sait
sur combien de monde il porte.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from hr_insight.core import metrics, pay_equity
from hr_insight.core.config import Configuration
from hr_insight.core.normalize import (Employee, apply_fte_scale,
                                       full_time_amount, parse_fte)


def _avec_fte(valeurs):
    gens = [Employee(row_number=rang + 2) for rang in range(len(valeurs))]
    for salarie, valeur in zip(gens, valeurs):
        salarie.fte = valeur
    return gens


class TestTheWorkingTimeColumnIsMadeTrustworthy(unittest.TestCase):
    """Tant que rien ne calculait avec elle, son ecriture n'importait pas.
    Des qu'on divise un salaire par elle, « 80 » pris pour 80 divise le
    salaire par quatre-vingts."""

    def test_a_percent_sign_is_read_and_remembered(self):
        self.assertEqual(parse_fte("80 %"), (80.0, True))
        self.assertEqual(parse_fte("0,8"), (0.8, False))
        self.assertEqual(parse_fte(""), (None, False))

    def test_a_ratio_column_is_left_alone(self):
        gens = _avec_fte([1.0, 0.8, 0.5])
        apply_fte_scale(gens, False)
        self.assertEqual([item.fte for item in gens], [1.0, 0.8, 0.5])

    def test_a_percentage_column_is_brought_back_to_a_ratio(self):
        gens = _avec_fte([100.0, 80.0, 50.0])
        apply_fte_scale(gens, False)
        self.assertEqual([item.fte for item in gens], [1.0, 0.8, 0.5])

    def test_an_explicit_percent_is_never_read_as_a_ratio(self):
        """Une colonne ecrite « 80 % » est en pourcentage, meme si ses
        valeurs ressemblent a des ratios. Plutot que de les diviser par
        cent en silence — un 0,8 deviendrait 0,008, soit un salaire
        multiplie par cent vingt-cinq —, ces lignes sont refusees."""
        gens = _avec_fte([1.0, 0.8])
        apply_fte_scale(gens, True)
        self.assertEqual([item.fte for item in gens], [None, None])
        for item in gens:
            self.assertIn("fte:ambiguous_scale", item.issues)

    def test_an_explicit_percent_column_scales_normally(self):
        gens = _avec_fte([100.0, 80.0])
        apply_fte_scale(gens, True)
        self.assertEqual([item.fte for item in gens], [1.0, 0.8])

    def test_an_ambiguous_row_is_dropped_and_flagged(self):
        """Dans une colonne en pourcentage, « 1 » vaut 1 % : c'est presque
        toujours un temps plein mal ecrit, et le garder multiplierait son
        salaire par cent."""
        gens = _avec_fte([1.0, 50.0, 100.0])
        apply_fte_scale(gens, False)
        self.assertIsNone(gens[0].fte)
        self.assertIn("fte:ambiguous_scale", gens[0].issues)
        self.assertEqual([gens[1].fte, gens[2].fte], [0.5, 1.0])

    def test_an_impossible_working_time_is_not_a_working_time(self):
        gens = _avec_fte([1.0, 0.0, -0.5, 1.2])
        apply_fte_scale(gens, False)
        self.assertEqual([item.fte for item in gens][1:], [None, None, None])
        for item in gens[1:]:
            self.assertIn("fte:out_of_range", item.issues)

    def test_an_empty_column_changes_nothing(self):
        gens = _avec_fte([None, None])
        apply_fte_scale(gens, False)
        self.assertEqual([item.fte for item in gens], [None, None])


class TestTheAmountIsBroughtBackToFullTime(unittest.TestCase):

    def test_a_part_time_is_scaled_up(self):
        salarie = Employee(row_number=2)
        salarie.base_salary, salarie.fte = 32000.0, 0.8
        self.assertEqual(full_time_amount(salarie, "base_salary"), 40000.0)

    def test_an_unknown_working_time_gives_no_amount(self):
        """Le supposer plein compterait un temps partiel comme un temps
        plein — l'erreur meme que ce calcul corrige."""
        salarie = Employee(row_number=2)
        salarie.base_salary, salarie.fte = 32000.0, None
        self.assertIsNone(full_time_amount(salarie, "base_salary"))


class TestTheTwoIndicatorsAreShownTogether(unittest.TestCase):

    def _population(self):
        """Memes salaires a temps plein ; le temps partiel est feminin."""
        population = build_population([make_row(i) for i in range(60)])
        for rang, salarie in enumerate(population.employees):
            salarie.gender = "F" if rang % 2 else "H"
            salarie.fte = 0.8 if (rang % 2 and rang % 3) else 1.0
            salarie.base_salary = 40000.0 * salarie.fte
        return population

    def test_the_raw_gap_is_entirely_explained_by_working_time(self):
        equite = pay_equity.calculate_pay_equity(self._population(),
                                                 make_config())
        self.assertGreater(equite["pay"]["mean_gap"], 10.0)
        self.assertAlmostEqual(equite["full_time"]["mean_gap"], 0.0, places=6)
        self.assertAlmostEqual(equite["full_time"]["explained_gap"],
                               round(equite["pay"]["mean_gap"], 2), places=2)

    def test_the_raw_gap_is_never_replaced(self):
        """Les deux chiffres repondent a deux questions. Publier l'un a la
        place de l'autre serait aussi faux dans un sens que dans l'autre."""
        equite = pay_equity.calculate_pay_equity(self._population(),
                                                 make_config())
        self.assertIn("mean_gap", equite["pay"])
        self.assertIsNotNone(equite["pay"]["mean_gap"])

    def test_the_coverage_is_published_with_the_figure(self):
        """Un temps plein calcule sur la moitie de la population ne se lit
        pas comme un temps plein calcule sur toute la population."""
        population = self._population()
        for salarie in population.employees[:30]:
            salarie.fte = None
        equite = pay_equity.calculate_pay_equity(population, make_config())
        self.assertEqual(equite["full_time"]["coverage"], 50.0)

    def test_salary_metrics_carry_the_same_block(self):
        population = self._population()
        bloc = metrics.calculate_salary_metrics(
            population, make_config())["full_time"]
        self.assertAlmostEqual(bloc["mean"], 40000.0, places=6)
        self.assertEqual(bloc["coverage"], 100.0)

    def test_too_few_known_working_times_masks_the_figure(self):
        population = self._population()
        for salarie in population.employees[:58]:
            salarie.fte = None
        bloc = metrics.calculate_salary_metrics(
            population, make_config())["full_time"]
        self.assertTrue(bloc["masked"])
        self.assertNotIn("mean", bloc)


class TestTheControlWorkbookCarriesTheFormula(unittest.TestCase):
    """Un indicateur publie sans sa formule n'a rien a faire dans ce
    classeur : c'est toute la raison d'etre de l'onglet Contrôle."""

    def test_the_full_time_mean_is_written_as_a_formula(self):
        from hr_insight.core import formulas as fx

        ledger = fx.Ledger("Données individuelles",
                           ["Salaire de base", "Temps de travail"], 80)
        expression = ledger.per_full_time("Salaire de base",
                                          "Temps de travail", "AVERAGE")
        self.assertIn("AVERAGE(IF(", expression)
        # Chaque test parenthese : sans cela le masque est faux partout et
        # la formule rend un tableau de zeros.
        self.assertIn('<>"")*(', expression)

    def test_the_formula_recomputes_the_published_value(self):
        from tests.support_spreadsheet import Workbook
        from hr_insight.core import formulas as fx

        lignes = [["Salaire de base", "Temps de travail"],
                  [32000, 0.8], [45000, 1.0], [45000, 1.0], [22500, 0.5]]
        ledger = fx.Ledger("Données", ["Salaire de base", "Temps de travail"],
                           4)
        classeur = Workbook([("Données", lignes)])
        obtenu = classeur.evaluate(
            ledger.per_full_time("Salaire de base", "Temps de travail"),
            "Données")
        self.assertAlmostEqual(float(obtenu), 43750.0, places=6)


if __name__ == "__main__":
    unittest.main()
