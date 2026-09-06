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
                                                    calculate_category_gaps,
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


class TestFiltersReachTheGap(unittest.TestCase):
    """Les criteres de la colonne de gauche portent aussi sur les ecarts.

    Un ecart calcule sur la population entiere alors qu'un filtre est pose
    repondrait a une autre question que celle de l'utilisateur.
    """

    def _analysed(self, expression=None):
        import tempfile
        from compensation_analytics.cli import parse_filter
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        from compensation_analytics.core.segmentation import build_filters
        from compensation_analytics.io.xlsx_writer import write_workbook
        from tests.support import HEADERS, REFERENCE_DATE

        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "population.xlsx")
        rows = []
        for index in range(60):
            french = index % 2 == 0
            female = index % 4 < 2
            rows.append(make_row(
                index, gender="F" if female else "H",
                business_unit="France" if french else "DACH",
                # En France l'ecart est nul, hors de France il est marque :
                # un filtre sur la BU doit donc changer le resultat.
                salary=40000 if french else (40000 if not female else 30000)))
        write_workbook(source, [("Population", [HEADERS] + rows)])
        config = make_config()
        filters = (build_filters([parse_filter(expression)], config)
                   if expression else [])
        return run_analysis(AnalysisRequest(
            source_path=source, reference_date=REFERENCE_DATE,
            filters=filters)).payload["pay_equity"]

    def test_a_filter_changes_the_gap(self):
        everyone = self._analysed()
        france = self._analysed("business_unit=France")
        self.assertAlmostEqual(france["pay"]["mean_gap"], 0.0, places=6)
        self.assertGreater(everyone["pay"]["mean_gap"], 0.0)

    def test_a_filter_leaving_one_sex_publishes_nothing(self):
        """Filtrer sur un seul sexe ne peut pas produire d'ecart."""
        only_women = self._analysed("gender=F")
        self.assertFalse(only_women["available"])
        self.assertIn("Effectif insuffisant", only_women["warning"])


class TestTheCategoryAxisCanChange(unittest.TestCase):
    """« Travail de meme valeur » se lit selon le poste, mais aussi selon le
    grade ou l'etablissement : l'axe doit pouvoir changer sans relancer
    toute l'analyse."""

    def setUp(self):
        from compensation_analytics.core.pay_equity import calculate_category_gaps
        self.compute = calculate_category_gaps
        self.config = make_config()
        rows = []
        for index in range(60):
            senior = index % 3 == 0
            female = index % 2 == 0
            rows.append(make_row(
                index, gender="F" if female else "H",
                grade="G7" if senior else "G3",
                business_unit=["France", "DACH"][index % 2],
                salary=(60000 if senior else 40000) - (4000 if female else 0)))
        self.population = build_population(rows, self.config)

    def test_the_same_population_reads_differently_on_two_axes(self):
        by_grade = self.compute(self.population, self.config, "grade")
        by_unit = self.compute(self.population, self.config, "business_unit")
        self.assertEqual({item["category"] for item in by_grade["categories"]},
                         {"G3", "G7"})
        self.assertEqual({item["category"] for item in by_unit["categories"]},
                         {"France", "DACH"})

    def test_the_axis_is_named_in_the_result(self):
        block = self.compute(self.population, self.config, "grade")
        self.assertEqual(block["category_field"], "grade")
        self.assertEqual(block["category_label"], "Grade")

    def test_an_axis_absent_from_the_file_says_so(self):
        block = self.compute(self.population, self.config, "job_title")
        self.assertEqual(block["categories"], [])
        self.assertIn("n'est renseigné", block["category_warning"])

class TestTheSexComparisonIsMemoisedWithoutChangingIt(unittest.TestCase):
    """La memorisation ne doit rien changer au resultat, ni rien casser.

    La decomposition Unicode des ecritures du sexe pesait trente-huit pour
    cent du temps d'analyse : les memes libelles etaient redecomposes a
    chaque salarie. La memorisation les normalise une fois — encore
    faut-il qu'elle reste insensible a la casse et aux accents, et qu'elle
    survive a une configuration ecrite a la main.
    """

    def test_the_reading_is_unchanged(self):
        femmes, hommes = ["F", "Femme", "Mme"], ["H", "M", "Homme"]
        for valeur, attendu in (("F", FEMALE), ("f", FEMALE),
                                ("FEMME", FEMALE), (" Mme ", FEMALE),
                                ("H", MALE), ("homme", MALE),
                                ("X", ""), ("", ""), (None, "")):
            self.assertEqual(classify(valeur, femmes, hommes), attendu,
                             repr(valeur))

    def test_accents_and_case_are_ignored_on_both_sides(self):
        self.assertEqual(classify("FÉMININ", ["féminin"], ["masculin"]), FEMALE)
        self.assertEqual(classify("feminin", ["Féminin"], ["Masculin"]), FEMALE)

    def test_two_different_configurations_do_not_share_a_cache_entry(self):
        """Deux fichiers RH n'ecrivent pas le sexe pareil : la memorisation
        est portee par la liste declaree, pas par le moteur."""
        self.assertEqual(classify("W", ["W"], ["M"]), FEMALE)
        self.assertEqual(classify("W", ["F"], ["W"]), MALE)

    def test_a_hand_written_configuration_never_raises(self):
        """Une valeur non hachable dans la configuration ne doit pas faire
        lever : la valeur n'est simplement pas reconnue."""
        for declaree in ([["F"]], [None], [12], [{"a": 1}], []):
            self.assertEqual(classify("F", declaree, ["H"]), "")
        self.assertEqual(classify("F", ["F", ["imbrique"]], ["H"]), FEMALE)


class TestWhatTheOverallGapIsMadeOf(unittest.TestCase):
    """Un ecart global melange deux faits opposes.

    Des femmes moins payees *sur le meme poste* appellent une
    revalorisation ; des femmes plus nombreuses *sur les postes les moins
    payes* appellent une politique de mobilite. Additionnes, les deux sont
    indecidables — et c'est pourquoi la directive fait publier le detail par
    categorie.
    """

    def _population(self, lignes):
        """`lignes` : (categorie, sexe, salaire) repete autant que voulu.

        La categorie est portee par le grade : le jeu de test n'a pas de
        colonne « Poste », et le calcul est le meme quel que soit l'axe —
        c'est precisement ce qui permet de comparer par poste, par grade ou
        par etablissement.
        """
        config = make_config()
        rows = [make_row(index, salary=salaire, gender=sexe, grade=categorie)
                for index, (categorie, sexe, salaire) in enumerate(lignes)]
        return build_population(rows, config), config

    def test_a_gap_hidden_by_the_structure_is_brought_out(self):
        """Le cas qui justifie tout : a poste egal les femmes sont moins
        payees, mais elles occupent les postes les mieux payes, et l'ecart
        global s'en trouve minore."""
        lignes = ([("Cadre", "F", 90000)] * 20 + [("Cadre", "H", 100000)] * 5
                  + [("Employe", "F", 45000)] * 5
                  + [("Employe", "H", 50000)] * 20)
        population, config = self._population(lignes)
        block = calculate_category_gaps(population, config, "grade")

        # A poste egal, les femmes touchent 10 % de moins dans les deux cas.
        self.assertAlmostEqual(block["comparable_gap"], 10.0, places=6)
        # L'ecart global, lui, est bien plus faible : les femmes sont
        # surrepresentees sur le poste le mieux paye.
        self.assertLess(block["overall_gap"], block["comparable_gap"])
        # L'effet de structure porte la difference, et il est negatif.
        self.assertAlmostEqual(
            block["structure_gap"],
            block["overall_gap"] - block["comparable_gap"], places=6)
        self.assertLess(block["structure_gap"], 0)

    def test_without_structure_effect_the_two_gaps_agree(self):
        """Repartition identique sur les deux postes : il ne reste que
        l'ecart a poste comparable."""
        lignes = ([("Cadre", "F", 90000)] * 10 + [("Cadre", "H", 100000)] * 10
                  + [("Employe", "F", 45000)] * 10
                  + [("Employe", "H", 50000)] * 10)
        population, config = self._population(lignes)
        block = calculate_category_gaps(population, config, "grade")
        self.assertAlmostEqual(block["comparable_gap"], 10.0, places=6)
        self.assertAlmostEqual(block["structure_gap"], 0.0, places=6)

    def test_the_coverage_says_on_what_the_comparable_gap_is_computed(self):
        """Un ecart calcule sur un dixieme de la population passerait pour
        l'image de l'ensemble : la couverture doit le dire."""
        lignes = ([("Cadre", "F", 90000)] * 10 + [("Cadre", "H", 100000)] * 10
                  # Poste trop petit pour publier : hors du calcul.
                  + [("Rare", "F", 40000)] * 2 + [("Rare", "H", 80000)] * 2)
        population, config = self._population(lignes)
        block = calculate_category_gaps(population, config, "grade")
        self.assertEqual(block["comparable_headcount"], 20)
        self.assertAlmostEqual(block["comparable_coverage"],
                               20 / 24 * 100.0, places=6)
        self.assertAlmostEqual(block["comparable_gap"], 10.0, places=6)

    def test_the_catch_up_cost_weighs_the_gap_by_the_headcount(self):
        """Vingt pour cent sur quatre personnes ne pese pas ce que pese six
        pour cent sur cent vingt : c'est la question qui suit l'ecart."""
        lignes = ([("Petit", "F", 80000)] * 5 + [("Petit", "H", 100000)] * 5
                  + [("Grand", "F", 94000)] * 100
                  + [("Grand", "H", 100000)] * 100)
        population, config = self._population(lignes)
        block = calculate_category_gaps(population, config, "grade")
        cout = {item["category"]: item["at_stake"]
                for item in block["categories"]}
        self.assertAlmostEqual(cout["Petit"], (100000 - 80000) * 5)
        self.assertAlmostEqual(cout["Grand"], (100000 - 94000) * 100)
        self.assertGreater(cout["Grand"], cout["Petit"])
        self.assertAlmostEqual(block["at_stake_total"],
                               cout["Petit"] + cout["Grand"])

    def test_a_masked_category_costs_nothing_it_is_simply_unknown(self):
        """Un poste masque n'a pas un rattrapage nul : il est inconnu."""
        lignes = [("Rare", "F", 40000)] * 2 + [("Rare", "H", 80000)] * 2
        population, config = self._population(lignes)
        block = calculate_category_gaps(population, config, "grade")
        self.assertIsNone(block["categories"][0]["at_stake"])
        self.assertIsNone(block["comparable_gap"])
        self.assertIsNone(block["structure_gap"])

    def test_the_men_are_realigned_when_they_are_the_ones_behind(self):
        """L'outil ne presume pas du sens de l'ecart."""
        lignes = ([("Poste", "F", 100000)] * 10
                  + [("Poste", "H", 90000)] * 10)
        population, config = self._population(lignes)
        block = calculate_category_gaps(population, config, "grade")
        item = block["categories"][0]
        self.assertLess(item["mean_gap"], 0)
        self.assertAlmostEqual(item["at_stake"], (100000 - 90000) * 10)


if __name__ == "__main__":
    unittest.main()
