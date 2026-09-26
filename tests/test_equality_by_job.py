"""L'egalite professionnelle : comparer femmes et hommes sur un meme poste.

Le brief est simple, et tout est dans ses termes. On compare *a poste egal*,
sur le *salaire de base*, *a temps plein*. Sans poste choisi, la page doit
designer les postes ou l'ecart est majeur — « les plus significatifs ».

Trois exigences en decoulent, et chacune a son test ici.

La base d'abord : un temps partiel touche moins sans qu'aucune inegalite ne
soit en cause. Comparer les montants verses fait donc passer pour une
inegalite ce qui n'est qu'une difference de temps de travail — et, dans
l'autre sens, masque une inegalite reelle chez une population feminine plus
souvent a temps partiel. Chaque montant est ramene au temps plein.

Le hasard ensuite : trente pour cent d'ecart entre trois femmes et quatre
hommes n'est pas un fait, c'est un tirage. Un classement par ampleur seule
met ces postes en tete — exactement ceux dont l'ecart est le moins sur. Le
test de Welch les remet a leur place.

La prudence enfin : ce qu'on ne peut pas calculer ne se remplace pas par un
chiffre. Un temps de travail inconnu sort du calcul et la couverture le dit ;
un fichier sans aucun temps de travail ne rend pas une page vide, il compare
les montants verses et l'annonce.

Aucune donnee RH reelle.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from hr_insight.core import statistics_engine as stats
from hr_insight.core.pay_equity import (basis_description,
                                        calculate_category_gaps,
                                        category_breakdown)


def _population(taille=60, **kwargs):
    """Une population dont on regle sexe, poste, salaire et temps partiel."""
    population = build_population([make_row(rang) for rang in range(taille)])
    postes = kwargs.get("postes", ("Comptable", "Technicien"))
    for rang, salarie in enumerate(population.employees):
        salarie.gender = "F" if rang % 2 else "H"
        salarie.job_title = postes[rang % len(postes)]
        salarie.fte = 1.0
        salarie.base_salary = 40000.0
    return population


class TestTheWelchTest(unittest.TestCase):
    """La probabilite affichee doit etre la bonne, pas une approximation.

    La loi de Student est ecrite ici — la bibliotheque standard ne la
    fournit pas et aucune dependance externe n'est admise. Elle est donc
    verifiee contre des valeurs de table, et par integration numerique de sa
    propre densite dans le test suivant.
    """

    def test_the_probability_matches_the_table(self):
        for t, degres, attendu in ((2.0, 10, 0.073388),
                                   (3.1, 7, 0.017322),
                                   (1.0, 1, 0.500000),
                                   (0.0, 5, 1.000000)):
            with self.subTest(t=t, degres=degres):
                self.assertAlmostEqual(stats.student_two_sided(t, degres),
                                       attendu, places=6)

    def test_the_probability_matches_its_own_density(self):
        """Verification independante : l'aire des deux queues, integree."""
        import math

        def densité(x, v):
            return (math.gamma((v + 1) / 2)
                    / (math.sqrt(v * math.pi) * math.gamma(v / 2))
                    * (1 + x * x / v) ** (-(v + 1) / 2))

        for t, v in ((2.0, 10), (1.2, 25)):
            pas, aire, borne = 0.001, 0.0, 60.0
            x = t
            while x < borne:
                aire += (densité(x, v) + densité(x + pas, v)) / 2 * pas
                x += pas
            self.assertAlmostEqual(stats.student_two_sided(t, v), 2 * aire,
                                   places=5)

    def test_two_series_without_dispersion_are_read_as_certain(self):
        """Une grille salariale : chaque sexe a un montant, toujours le meme.

        Le t est infini et le refus de conclure serait le pire des
        verdicts — c'est la situation la plus nette qui se puisse lire.
        """
        égales = stats.welch_comparison([50.0] * 8, [50.0] * 8)
        self.assertEqual(égales["p_value"], 1.0)
        différentes = stats.welch_comparison([50.0] * 8, [45.0] * 8)
        self.assertEqual(différentes["p_value"], 0.0)
        self.assertIsNone(différentes["t"])

    def test_one_value_on_a_side_is_not_enough(self):
        self.assertIsNone(stats.welch_comparison([1.0], [1.0, 2.0, 3.0])
                          ["p_value"])

    def test_the_comparison_does_not_depend_on_the_order(self):
        gauche, droite = [10.0, 12.0, 9.0, 11.0], [14.0, 15.0, 13.0, 16.0]
        self.assertAlmostEqual(stats.welch_comparison(gauche, droite)["p_value"],
                               stats.welch_comparison(droite, gauche)["p_value"])

    def test_the_same_gap_is_surer_on_more_people(self):
        """Le point de tout l'exercice, ecrit comme une propriete."""
        petit = stats.welch_comparison([100.0, 110.0, 90.0],
                                       [120.0, 130.0, 110.0])
        grand = stats.welch_comparison([100.0, 110.0, 90.0] * 20,
                                       [120.0, 130.0, 110.0] * 20)
        self.assertLess(grand["p_value"], petit["p_value"])


class TestTheComparisonIsFullTimeBaseSalary(unittest.TestCase):
    """Ce que la page compare : le salaire de base, ramene au temps plein."""

    def setUp(self):
        self.config = make_config()

    def _part_time_women(self):
        """Memes salaires a temps plein ; les femmes a 80 %, payees 80 %."""
        population = _population(60, postes=("Comptable",))
        for salarie in population.employees:
            if salarie.gender == "F":
                salarie.fte = 0.8
                salarie.base_salary = 32000.0
        return population

    def test_a_part_time_gap_is_not_an_inequality(self):
        population = self._part_time_women()
        bloc = calculate_category_gaps(population, self.config, "job_title")
        poste = bloc["categories"][0]
        # Sur les montants verses, vingt pour cent d'ecart : c'est ce que la
        # directive fait publier, et ce n'est pas une inegalite.
        self.assertAlmostEqual(poste["mean_gap"], 20.0, places=6)
        # A temps de travail egal, aucun ecart. C'est la base de la page.
        self.assertAlmostEqual(poste["comparison"]["mean_gap"], 0.0, places=6)
        self.assertFalse(poste["comparison"]["significance"]["significant"])

    def test_a_real_inequality_survives_the_change_of_basis(self):
        population = self._part_time_women()
        for salarie in population.employees:
            if salarie.gender == "F":
                # Dix pour cent de moins, a temps de travail egal.
                salarie.base_salary = 32000.0 * 0.9
        poste = calculate_category_gaps(population, self.config,
                                        "job_title")["categories"][0]
        self.assertAlmostEqual(poste["comparison"]["mean_gap"], 10.0, places=6)
        self.assertTrue(poste["comparison"]["significance"]["significant"])

    def test_the_card_reads_full_time_amounts(self):
        """Mediane, quartiles, minimum : la fiche entiere sur la meme base."""
        population = self._part_time_women()
        fiche = category_breakdown(population, self.config, "job_title",
                                   "Comptable")
        femmes = next(c for c in fiche["columns"] if c["key"] == "female")
        self.assertAlmostEqual(femmes["salary"]["median"], 40000.0, places=6)
        self.assertAlmostEqual(femmes["salary"]["min"], 40000.0, places=6)
        self.assertTrue(fiche["basis"]["full_time"])

    def test_an_unknown_working_time_leaves_the_comparison(self):
        """Il sort du calcul, et la couverture le dit plutot que de le taire."""
        population = self._part_time_women()
        for salarie in population.employees[:20]:
            salarie.fte = None
        fiche = category_breakdown(population, self.config, "job_title",
                                   "Comptable")
        self.assertLess(fiche["coverage"], 100.0)
        self.assertEqual(fiche["compared_headcount"], 40)
        self.assertEqual(fiche["headcount"], 60)

    def test_a_column_is_masked_when_too_few_working_times_are_known(self):
        """Le seuil porte sur ce qui est calculable, non sur l'effectif.

        Un poste de trente personnes dont deux ont un temps de travail connu
        publierait la remuneration de ces deux-la.
        """
        population = _population(60, postes=("Comptable",))
        for rang, salarie in enumerate(population.employees):
            if salarie.gender == "F" and rang > 3:
                salarie.fte = None
        fiche = category_breakdown(population, self.config, "job_title",
                                   "Comptable")
        femmes = next(c for c in fiche["columns"] if c["key"] == "female")
        self.assertTrue(femmes["masked"])
        self.assertGreater(femmes["headcount"], 20)
        self.assertFalse(fiche["published"])
        self.assertIn("minimum", fiche["warning"].lower())

    def test_without_any_working_time_the_page_still_compares(self):
        """Un fichier sans temps de travail ne rend pas une page vide.

        Il ne permet pas non plus de supposer tout le monde a temps plein :
        la page compare alors les montants verses, et l'ecrit.
        """
        population = _population(60, postes=("Comptable",))
        for salarie in population.employees:
            salarie.fte = None
            if salarie.gender == "F":
                salarie.base_salary = 36000.0
        base = basis_description(population, self.config)
        self.assertFalse(base["full_time"])
        self.assertIn("temps de travail", base["label"])
        poste = calculate_category_gaps(population, self.config,
                                        "job_title")["categories"][0]
        self.assertAlmostEqual(poste["comparison"]["mean_gap"], 10.0, places=6)
        self.assertTrue(poste["comparison"]["published"])

    def test_the_basis_is_the_configured_analysis_field(self):
        """« Salaire de base » est un defaut, pas une regle codee."""
        données = make_config().as_dict()
        données["salary_parameters"]["analysis_field"] = "total_compensation"
        from hr_insight.core.config import Configuration

        population = _population(60, postes=("Comptable",))
        for salarie in population.employees:
            salarie.total_compensation = 50000.0
        base = basis_description(population, Configuration(données))
        self.assertEqual(base["field"], "total_compensation")


class TestTheCatchUpIsPaidAtTheWorkedTime(unittest.TestCase):
    """Ce que coute l'alignement, en euros reellement verses.

    L'ecart se mesure a temps plein ; le rattrapage se paie au prorata du
    temps travaille. Aligner les montants verses reviendrait a payer un
    mi-temps comme un temps plein : le chiffre n'aurait aucun rapport avec
    la decision a prendre, et il serait toujours trop haut.
    """

    def setUp(self):
        self.config = make_config()

    def test_a_half_time_costs_half(self):
        population = _population(40, postes=("Comptable",))
        for salarie in population.employees:
            if salarie.gender == "F":
                salarie.fte = 0.5
                # 18 000 verses pour un mi-temps, soit 36 000 a temps
                # plein : 4 000 de moins que les hommes.
                salarie.base_salary = 18000.0
        poste = calculate_category_gaps(population, self.config,
                                        "job_title")["categories"][0]
        comparaison = poste["comparison"]
        self.assertAlmostEqual(comparaison["mean_gap"], 10.0, places=6)
        # Vingt femmes a mi-temps : dix temps pleins, 4 000 chacun.
        self.assertAlmostEqual(comparaison["at_stake"], 4000.0 * 10, places=6)
        # Le rattrapage de la directive, sur les montants verses, compte
        # vingt personnes et un ecart de 22 000 : il ne dit pas la meme
        # chose, et c'est pourquoi les deux coexistent.
        self.assertGreater(poste["at_stake"], comparaison["at_stake"] * 4)

    def test_the_total_is_the_sum_of_the_jobs(self):
        # Trois postes pour deux sexes : avec deux, le poste et le sexe
        # alternent ensemble et chaque poste n'a qu'un seul sexe.
        population = _population(90, postes=("Comptable", "Technicien",
                                             "Ingénieur"))
        for salarie in population.employees:
            if salarie.gender == "F":
                salarie.base_salary = 36000.0
        bloc = calculate_category_gaps(population, self.config, "job_title")
        self.assertAlmostEqual(
            bloc["comparable_at_stake_total"],
            sum(item["comparison"].get("at_stake") or 0.0
                for item in bloc["categories"]), places=6)
        self.assertGreater(bloc["comparable_at_stake_total"], 0.0)


class TestTheMostSignificantJobsComeFirst(unittest.TestCase):
    """Sans selection, la page doit designer ou regarder d'abord."""

    def setUp(self):
        self.config = make_config()

    def test_a_handful_with_a_huge_gap_is_less_sure_than_many_with_a_small_one(self):
        lignes = []
        # Un poste nombreux, ecart modeste et regulier.
        for rang in range(120):
            lignes.append(make_row(rang))
        population = build_population(lignes)
        for rang, salarie in enumerate(population.employees):
            salarie.fte = 1.0
            if rang < 100:
                salarie.job_title = "Technicien"
                salarie.gender = "F" if rang % 2 else "H"
                # Une dispersion reelle dans chaque sexe : sans elle, le
                # test n'aurait pas a travailler.
                salarie.base_salary = (40000.0 * (0.94 if rang % 2 else 1.0)
                                       + (rang % 7) * 400)
            else:
                # Un poste de vingt personnes, ecart enorme mais disperse.
                salarie.job_title = "Chef de projet"
                salarie.gender = "F" if rang % 2 else "H"
                salarie.base_salary = (30000.0 + rang * 900 if rang % 2
                                       else 70000.0 - rang * 300)
        blocs = {item["category"]: item for item in calculate_category_gaps(
            population, self.config, "job_title")["categories"]}
        petit = blocs["Chef de projet"]["comparison"]
        grand = blocs["Technicien"]["comparison"]
        self.assertGreater(abs(petit["mean_gap"]), abs(grand["mean_gap"]))
        # Et pourtant c'est le second qu'il faut regarder d'abord.
        self.assertLess(grand["significance"]["p_value"],
                        petit["significance"]["p_value"])

    def test_the_significance_level_is_configurable(self):
        from hr_insight.core.config import Configuration

        population = _population(60, postes=("Comptable",))
        for rang, salarie in enumerate(population.employees):
            salarie.base_salary = 40000.0 + (rang % 9) * 500
            if salarie.gender == "F":
                salarie.base_salary -= 1000.0
        données = make_config().as_dict()
        # Un seuil a zero n'admet aucun ecart comme significatif : le
        # reglage commande, et il n'est pas decoratif.
        données["pay_equity_parameters"]["significance_level"] = 0.0
        poste = calculate_category_gaps(population, Configuration(données),
                                        "job_title")["categories"][0]
        self.assertFalse(poste["comparison"]["significance"]["significant"])
        self.assertEqual(poste["comparison"]["significance"]["level"], 0.0)


if __name__ == "__main__":                              # pragma: no cover
    unittest.main()
