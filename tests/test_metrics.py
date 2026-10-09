"""Tests des indicateurs metier et des regles de petits effectifs."""

import unittest

from tests.support import HEADERS, build_population, make_config, make_row
from hr_analytics.core import metrics
from hr_analytics.core.segmentation import build_filters, apply_filters, split_by


class TestPopulationMetrics(unittest.TestCase):
    def test_age_and_tenure_bands(self):
        rows = [
            make_row(0, age=25, tenure=1), make_row(1, age=35, tenure=3),
            make_row(2, age=45, tenure=7), make_row(3, age=55, tenure=12),
            make_row(4, age=65, tenure=20), make_row(5, age=29, tenure=1.9),
        ]
        config = make_config()
        population = build_population(rows, config)
        result = metrics.calculate_population_metrics(population, config)
        bands = {item["label"]: item["count"] for item in result["age_bands"]}
        self.assertEqual(bands["20-29"], 2)
        self.assertEqual(bands["60+"], 1)
        tenure = {item["label"]: item["count"] for item in result["tenure_bands"]}
        self.assertEqual(tenure["<2 ans"], 2)
        # L'anciennete maximale vaut 20 ans : le decoupage se prolonge, et
        # ne range plus 12 ans et 20 ans dans une meme tranche « > 10 ans ».
        self.assertEqual(tenure["10-15 ans"], 1)
        self.assertEqual(tenure[">15 ans"], 1)
        self.assertNotIn(">10 ans", tenure)

    def test_short_careers_keep_the_configured_bands(self):
        """Rien n'est engendre quand la population ne depasse pas la derniere
        tranche : le decoupage configure reste intact."""
        rows = [make_row(index, age=30 + index, tenure=tenure)
                for index, tenure in enumerate([0.5, 1, 3, 4, 7, 8, 11])]
        result = metrics.calculate_population_metrics(
            build_population(rows, make_config()), make_config())
        labels = [item["label"] for item in result["tenure_bands"]]
        # De la plus longue anciennete a la plus courte : c'est l'ordre que
        # le moteur publie, et que la pyramide comme les tableaux suivent.
        self.assertEqual(labels, [">10 ans", "5-10 ans", "2-5 ans", "<2 ans"])

    def test_the_extension_can_be_switched_off(self):
        config = make_config({"tenure_parameters.auto_extend": False})
        rows = [make_row(index, age=40, tenure=tenure)
                for index, tenure in enumerate([1, 3, 6, 9, 12, 20, 30])]
        result = metrics.calculate_population_metrics(
            build_population(rows, config), config)
        tenure = {item["label"]: item["count"] for item in result["tenure_bands"]}
        self.assertEqual(tenure[">10 ans"], 3)

    def test_the_step_is_configurable(self):
        config = make_config({"tenure_parameters.extend_step": 10})
        rows = [make_row(index, age=50, tenure=tenure)
                for index, tenure in enumerate([1, 4, 7, 11, 15, 25, 33])]
        result = metrics.calculate_population_metrics(
            build_population(rows, config), config)
        labels = [item["label"] for item in result["tenure_bands"]]
        self.assertIn("10-20 ans", labels)
        self.assertIn("20-30 ans", labels)
        self.assertIn(">30 ans", labels)

    def test_shares_sum_to_one_hundred(self):
        rows = [make_row(i, age=30 + i % 30) for i in range(50)]
        config = make_config()
        result = metrics.calculate_population_metrics(build_population(rows, config), config)
        total = sum(item["share"] for item in result["age_bands"])
        self.assertAlmostEqual(total, 100.0, places=6)

    def test_configurable_bands_are_honoured(self):
        config = make_config({"age_parameters.bands": [
            {"label": "moins de 40", "min": 0, "max": 39},
            {"label": "40 et plus", "min": 40, "max": None},
        ]})
        rows = [make_row(0, age=30), make_row(1, age=50)]
        population = build_population(rows, config)
        result = metrics.calculate_age_metrics(population, config)
        labels = {item["label"] for item in result["age_bands"]}
        self.assertEqual(labels, {"moins de 40", "40 et plus"})


class TestSalaryMetrics(unittest.TestCase):
    def test_payroll_and_central_tendency(self):
        config = make_config()
        rows = [make_row(i, salary=salary) for i, salary in
                enumerate([30000, 40000, 50000, 60000, 70000])]
        result = metrics.calculate_salary_metrics(build_population(rows, config), config)
        self.assertEqual(result["payroll"], 250000)
        self.assertEqual(result["mean"], 50000)
        self.assertEqual(result["median"], 50000)
        self.assertEqual(result["valued_headcount"], 5)

    def test_missing_salaries_reduce_coverage_only(self):
        config = make_config()
        rows = [make_row(i, salary=40000) for i in range(8)]
        rows += [make_row(90 + i, salary=None) for i in range(2)]
        result = metrics.calculate_salary_metrics(build_population(rows, config), config)
        self.assertEqual(result["headcount"], 10)
        self.assertEqual(result["valued_headcount"], 8)
        self.assertAlmostEqual(result["coverage"], 80.0)
        self.assertEqual(result["mean"], 40000)


class TestSmallHeadcountRules(unittest.TestCase):
    def test_results_masked_below_publication_threshold(self):
        config = make_config({"privacy_parameters.min_headcount_publish": 5})
        population = build_population([make_row(i) for i in range(3)], config)
        result = metrics.calculate_salary_metrics(population, config)
        self.assertTrue(result["masked"])
        self.assertIsNone(result.get("mean"))
        self.assertIsNotNone(result["warning"])

    def test_warning_between_thresholds(self):
        config = make_config({"privacy_parameters.min_headcount_publish": 5,
                              "privacy_parameters.min_headcount_warning": 10})
        population = build_population([make_row(i) for i in range(7)], config)
        result = metrics.calculate_salary_metrics(population, config)
        self.assertFalse(result["masked"])
        self.assertIn("prudence", result["warning"])

    def test_charts_disabled_below_chart_threshold(self):
        config = make_config({"privacy_parameters.min_headcount_chart": 10})
        population = build_population([make_row(i) for i in range(6)], config)
        distribution = metrics.calculate_distribution_metrics(population, config)
        self.assertFalse(distribution["available"])
        self.assertEqual(distribution["bins"], [])
        scatter = metrics.scatter_dataset(population, config)
        self.assertFalse(scatter["available"])

    def test_threshold_is_configurable(self):
        config = make_config({"privacy_parameters.min_headcount_publish": 2,
                              "privacy_parameters.min_headcount_warning": 2})
        population = build_population([make_row(i) for i in range(3)], config)
        result = metrics.calculate_salary_metrics(population, config)
        self.assertFalse(result["masked"])

    def test_small_segments_are_masked_in_segment_table(self):
        config = make_config({"privacy_parameters.min_headcount_publish": 5})
        rows = [make_row(i, business_unit="France") for i in range(20)]
        rows += [make_row(100 + i, business_unit="Nordics") for i in range(3)]
        population = build_population(rows, config)
        segment = metrics.calculate_segment_metrics(population, config, "business_unit")
        by_name = {row["segment"]: row for row in segment["rows"]}
        self.assertFalse(by_name["France"]["masked"])
        self.assertTrue(by_name["Nordics"]["masked"])
        self.assertIsNone(by_name["Nordics"]["salary"].get("mean"))
        self.assertEqual(segment["masked_segments"], 1)


class TestDistributionAndScatter(unittest.TestCase):
    def test_scatter_trend_line_and_grouping(self):
        config = make_config()
        rows = [make_row(i, tenure=i % 20, salary=30000 + (i % 20) * 1000)
                for i in range(40)]
        population = build_population(rows, config)
        dataset = metrics.scatter_dataset(population, config)
        self.assertTrue(dataset["available"])
        self.assertEqual(len(dataset["points"]), 40)
        # La droite de tendance n'est plus tracee par defaut : elle vient de
        # la meme regression que le R2, retire parce qu'il n'apprenait rien.
        self.assertIsNone(dataset["trend"])

    def test_the_trend_line_can_be_switched_back_on(self):
        config = make_config({"chart_parameters.show_trend_line": True})
        rows = [make_row(i, tenure=i % 20, salary=30000 + (i % 20) * 1000)
                for i in range(40)]
        dataset = metrics.scatter_dataset(build_population(rows, config), config)
        self.assertGreater(dataset["trend"]["r_squared"], 0.9)


class TestTheDistributionSplitsBySex(unittest.TestCase):
    """Deux distributions dos a dos, decoupees par le moteur.

    La fenetre ne doit pas parcourir la population pour son propre compte :
    elle finirait par compter autrement que le moteur.
    """

    def _population(self, femmes: int, hommes: int, config=None):
        config = config or make_config()
        rows = [make_row(index, gender="F", salary=30000 + index * 500)
                for index in range(femmes)]
        rows += [make_row(1000 + index, gender="M", salary=35000 + index * 500)
                 for index in range(hommes)]
        return build_population(rows, config), config

    def test_the_two_sides_share_the_classes_of_the_whole(self):
        population, config = self._population(20, 20)
        distribution = metrics.calculate_distribution_metrics(population, config)
        split = distribution["sex_split"]
        self.assertTrue(split["available"])
        self.assertIsNone(split["warning"])
        self.assertEqual(len(split["female_counts"]), len(distribution["bins"]))
        self.assertEqual(len(split["male_counts"]), len(distribution["bins"]))
        # Chaque classe accueille les deux cotes et rien de plus : le total
        # des deux ventilations est celui de l'histogramme d'ensemble.
        for index, item in enumerate(distribution["bins"]):
            self.assertEqual(
                split["female_counts"][index] + split["male_counts"][index],
                int(item["count"]))
        self.assertEqual(split["female_count"], 20)
        self.assertEqual(split["male_count"], 20)
        self.assertEqual(split["unknown_count"], 0)

    def test_each_side_carries_its_own_median(self):
        population, config = self._population(20, 20)
        split = metrics.calculate_distribution_metrics(
            population, config)["sex_split"]
        # 30 000 a 39 500 par pas de 500 : mediane a mi-chemin.
        self.assertAlmostEqual(split["female_median"], 34750.0)
        self.assertAlmostEqual(split["male_median"], 39750.0)

    def test_a_side_below_the_chart_threshold_refuses_the_split(self):
        """Trente hommes ne donnent pas le droit de dessiner la distribution
        de trois femmes."""
        config = make_config({"privacy_parameters.min_headcount_chart": 10})
        population, config = self._population(3, 30, config)
        split = metrics.calculate_distribution_metrics(
            population, config)["sex_split"]
        self.assertFalse(split["available"])
        self.assertFalse(split["female_chartable"])
        self.assertTrue(split["male_chartable"])
        self.assertEqual(split["female_counts"], [])
        self.assertIn("10", split["warning"])

    def test_the_threshold_of_the_warning_is_the_configured_one(self):
        config = make_config({"privacy_parameters.min_headcount_chart": 4,
                              "privacy_parameters.min_headcount_publish": 2})
        population, config = self._population(3, 30, config)
        split = metrics.calculate_distribution_metrics(
            population, config)["sex_split"]
        self.assertIn("4 salariés", split["warning"])
        # Sous le seuil de publication, pas de mediane : trois salaries ne
        # se resument pas par un chiffre... mais le seuil est a deux ici.
        self.assertIsNotNone(split["female_median"])

    def test_a_side_below_the_publication_threshold_has_no_median(self):
        config = make_config({"privacy_parameters.min_headcount_publish": 5,
                              "privacy_parameters.min_headcount_chart": 2})
        population, config = self._population(3, 30, config)
        split = metrics.calculate_distribution_metrics(
            population, config)["sex_split"]
        self.assertIsNone(split["female_median"])
        self.assertIsNotNone(split["male_median"])

    def test_employees_without_a_sex_are_counted_apart(self):
        config = make_config()
        rows = [make_row(index, gender="F") for index in range(12)]
        rows += [make_row(100 + index, gender="M") for index in range(12)]
        rows += [make_row(200 + index, gender="") for index in range(4)]
        population = build_population(rows, config)
        split = metrics.calculate_distribution_metrics(
            population, config)["sex_split"]
        self.assertEqual(split["unknown_count"], 4)
        self.assertEqual(split["female_count"], 12)
        self.assertEqual(split["male_count"], 12)

    def test_an_unavailable_distribution_still_carries_the_split_shape(self):
        """La vue lit une seule forme de bloc : sans quoi elle doit tester
        l'existence de chaque cle avant de la lire."""
        config = make_config({"privacy_parameters.min_headcount_chart": 10})
        population, config = self._population(2, 2, config)
        distribution = metrics.calculate_distribution_metrics(population, config)
        self.assertFalse(distribution["available"])
        self.assertFalse(distribution["sex_split"]["available"])
        self.assertEqual(distribution["sex_split"]["female_counts"], [])


class TestSegmentationAndComparison(unittest.TestCase):
    def test_filters_are_combinable(self):
        config = make_config()
        rows = [make_row(0, business_unit="France", groupe="G5"),
                make_row(1, business_unit="France", groupe="G2"),
                make_row(2, business_unit="DACH", groupe="G5")]
        population = build_population(rows, config)
        filters = build_filters([
            {"field": "business_unit", "operator": "eq", "value": "France"},
            {"field": "groupe", "operator": "in", "value": ["G5", "G6"]},
        ], config=make_config())
        self.assertEqual(len(apply_filters(population, filters)), 1)

    def test_numeric_filter(self):
        config = make_config()
        rows = [make_row(i, salary=30000 + i * 10000) for i in range(4)]
        population = build_population(rows, config)
        filters = build_filters([
            {"field": "base_salary", "operator": "gte", "value": 50000}
        ], config=make_config())
        self.assertEqual(len(apply_filters(population, filters)), 2)

    def test_filter_matching_is_case_insensitive(self):
        config = make_config()
        population = build_population([make_row(0, business_unit="France")], config)
        filters = build_filters([
            {"field": "business_unit", "operator": "eq", "value": "france"}
        ], config=make_config())
        self.assertEqual(len(apply_filters(population, filters)), 1)

    def test_split_by_dimension(self):
        config = make_config()
        rows = ([make_row(i, business_unit="France") for i in range(3)] +
                [make_row(10 + i, business_unit="DACH") for i in range(2)])
        groups = split_by(build_population(rows, config), "business_unit")
        self.assertEqual({key: len(value) for key, value in groups.items()},
                         {"France": 3, "DACH": 2})

    def test_comparison_reports_gaps(self):
        config = make_config()
        left = build_population([make_row(i, salary=50000) for i in range(10)], config)
        right = build_population([make_row(i, salary=40000) for i in range(10)], config)
        comparison = metrics.compare_populations(left, right, config)
        row = next(item for item in comparison["rows"] if item["indicator"] == "Salaire moyen")
        self.assertEqual(row["gap"], 10000)
        self.assertAlmostEqual(row["gap_percent"], 25.0)


class TestScatterSampling(unittest.TestCase):
    """Au-dela du seuil parametre, le nuage est echantillonne de facon
    deterministe pour rester exploitable dans le navigateur."""

    def _dataset(self, count, maximum):
        config = make_config({"chart_parameters.scatter_max_points": maximum})
        rows = [make_row(i, tenure=i % 25, salary=30000 + i) for i in range(count)]
        return metrics.scatter_dataset(build_population(rows, config), config)

    def test_no_sampling_below_threshold(self):
        dataset = self._dataset(100, 500)
        self.assertFalse(dataset["sampled"])
        self.assertEqual(len(dataset["points"]), 100)
        self.assertIsNone(dataset["warning"])

    def test_sampling_above_threshold_is_capped_and_signalled(self):
        dataset = self._dataset(1000, 200)
        self.assertTrue(dataset["sampled"])
        self.assertEqual(len(dataset["points"]), 200)
        self.assertEqual(dataset["total_points"], 1000)
        self.assertIn("échantillonné", dataset["warning"])

    def test_sampling_is_deterministic(self):
        first = self._dataset(1000, 200)["points"]
        second = self._dataset(1000, 200)["points"]
        self.assertEqual([point["y"] for point in first],
                         [point["y"] for point in second])

    def test_sampling_can_be_disabled(self):
        dataset = self._dataset(1000, 0)
        self.assertFalse(dataset["sampled"])
        self.assertEqual(len(dataset["points"]), 1000)


class TestUnknownFilterField(unittest.TestCase):
    """Un champ de filtre inexistant doit lever une erreur explicite, jamais
    renvoyer une population vide en silence."""

    def test_unknown_field_raises_readable_error(self):
        from hr_analytics.core.errors import ConfigError
        with self.assertRaises(ConfigError) as caught:
            build_filters([{"field": "team", "operator": "eq", "value": "Alpha"}], config=make_config())
        message = caught.exception.message
        self.assertIn("team", message)
        self.assertIn("n'existe pas", message)
        self.assertIn("business_unit", message)  # liste les champs valides

    def test_misspelled_field_is_caught(self):
        from hr_analytics.core.errors import ConfigError
        with self.assertRaises(ConfigError):
            build_filters([{"field": "gade", "operator": "eq", "value": "G5"}], config=make_config())

    def test_valid_fields_still_pass(self):
        filters = build_filters([
            {"field": "business_unit", "operator": "eq", "value": "France"},
            {"field": "base_salary", "operator": "gte", "value": 50000},
            {"field": "tenure_band", "operator": "eq", "value": "<2 ans"},
        ], config=make_config())
        self.assertEqual(len(filters), 3)


class TestKeyShares(unittest.TestCase):
    """Parts remarquables du chapitre 11, calculees sur les valeurs reelles.

    Les deriver des libelles de tranches les rendrait fausses des que
    l'utilisateur reparametre ses tranches.
    """

    def test_shares_are_computed_from_actual_values(self):
        config = make_config()
        rows = ([make_row(i, age=25, tenure=1) for i in range(10)]
                + [make_row(50 + i, age=55, tenure=12) for i in range(10)])
        result = metrics.calculate_population_metrics(build_population(rows, config), config)
        self.assertAlmostEqual(result["share_under_30"], 50.0)
        self.assertAlmostEqual(result["share_50_plus"], 50.0)
        self.assertAlmostEqual(result["share_tenure_under_2"], 50.0)
        self.assertAlmostEqual(result["share_tenure_over_10"], 50.0)

    def test_shares_survive_a_reparametrised_band_configuration(self):
        config = make_config({"age_parameters.bands": [
            {"label": "moins de 40", "min": 0, "max": 39, "max_inclusive": True},
            {"label": "40 et plus", "min": 40, "max": None},
        ]})
        rows = [make_row(i, age=25) for i in range(10)] + [make_row(50 + i, age=45)
                                                           for i in range(10)]
        result = metrics.calculate_population_metrics(build_population(rows, config), config)
        self.assertAlmostEqual(result["share_under_30"], 50.0)

    def test_shares_reach_the_spreadsheet(self):
        from hr_analytics.core.export import _rows_population
        config = make_config()
        rows = [make_row(i, age=25) for i in range(10)]
        population = metrics.calculate_population_metrics(
            build_population(rows, config), config)
        labels = [row[0] for row in _rows_population(population) if row]
        self.assertIn("Moins de 30 ans", labels)
        self.assertIn("Ancienneté supérieure à 10 ans", labels)


class TestSegmentComparison(unittest.TestCase):
    """Une mediane de segment prise isolement ne dit pas si le segment est
    au-dessus ou au-dessous : c'est pourtant la question posee."""

    def _segment(self, **overrides):
        config = make_config(overrides)
        rows = [make_row(index, groupe=["G3", "G7"][index % 2],
                         salary=30000 if index % 2 == 0 else 60000)
                for index in range(40)]
        return metrics.calculate_segment_metrics(
            build_population(rows, config), config, "groupe")

    def test_each_segment_carries_its_share_of_headcount(self):
        block = self._segment()
        shares = {row["segment"]: row["share"] for row in block["rows"]}
        self.assertAlmostEqual(sum(shares.values()), 100.0, places=6)
        self.assertAlmostEqual(shares["G3"], 50.0, places=6)

    def test_the_gap_is_measured_against_the_reference_median(self):
        block = self._segment()
        self.assertIsNotNone(block["reference_median"])
        gaps = {row["segment"]: row["median_gap"] for row in block["rows"]}
        self.assertLess(gaps["G3"], 0)
        self.assertGreater(gaps["G7"], 0)

    def test_a_masked_segment_publishes_no_gap(self):
        """On ne publie pas un ecart calcule sur un chiffre qu'on a refuse
        de montrer."""
        config = make_config()
        rows = ([make_row(index, groupe="G3", salary=30000) for index in range(20)]
                + [make_row(20 + index, groupe="G9", salary=90000)
                   for index in range(2)])
        block = metrics.calculate_segment_metrics(
            build_population(rows, config), config, "groupe")
        small = [row for row in block["rows"] if row["segment"] == "G9"][0]
        self.assertTrue(small["masked"])
        self.assertIsNone(small["median_gap"])
        self.assertIsNotNone(small["share"])

    def test_the_gap_is_zero_for_a_single_segment(self):
        config = make_config()
        rows = [make_row(index, groupe="G4", salary=40000 + index * 100)
                for index in range(20)]
        block = metrics.calculate_segment_metrics(
            build_population(rows, config), config, "groupe")
        self.assertAlmostEqual(block["rows"][0]["median_gap"], 0.0, places=6)

if __name__ == "__main__":
    unittest.main()


class TestTheCatchAllBandKeepsItsSexes(unittest.TestCase):
    """Un salarié qu'aucune tranche n'accueille garde son sexe.

    La tranche fourre-tout — valeur absente, ou hors des bornes déclarées :
    un âge de douze ans, une ancienneté vide — posait « femmes : 0,
    hommes : 0 » et rangeait tout le monde sous « unknown_sex ». La même clé
    portait deux notions différentes, et la fenêtre annonçait « sexe non
    renseigné » des salariés qui en avaient un.
    """

    def population(self, rows):
        return build_population(rows)

    def bands(self, rows, field="age_band"):
        from hr_analytics.core.metrics import calculate_population_metrics

        payload = calculate_population_metrics(self.population(rows),
                                               make_config())
        return payload["age_bands" if field == "age_band" else "tenure_bands"]

    def test_someone_outside_every_band_still_counts_as_a_woman(self):
        # Sans date de naissance, aucune tranche d'âge ne l'accueille. Douze
        # ans ne suffit plus : la tranche « <20 » couvre les mineurs et les
        # apprentis, qui tombaient jusqu'ici dans le fourre-tout, à côté de
        # ceux dont l'âge est inconnu.
        rows = [make_row(index, gender="F" if index % 2 else "H")
                for index in range(20)]
        rows.append(make_row(99, birth_date="", gender="F"))
        fourre_tout = [band for band in self.bands(rows)
                       if band.get("catch_all")]
        self.assertEqual(len(fourre_tout), 1)
        self.assertEqual(fourre_tout[0]["count"], 1)
        self.assertEqual(fourre_tout[0]["female"], 1)
        self.assertEqual(fourre_tout[0]["male"], 0)
        self.assertEqual(fourre_tout[0]["unknown_sex"], 0)

    def test_unknown_sex_means_unknown_sex_and_nothing_else(self):
        rows = [make_row(index, gender="F" if index % 2 else "H")
                for index in range(20)]
        rows.append(make_row(98, gender=""))
        bandes = self.bands(rows)
        self.assertEqual(sum(band["unknown_sex"] for band in bandes), 1)
        # Et il reste dans sa tranche : son age est connu.
        self.assertFalse([band for band in bandes if band.get("catch_all")])

    def test_every_band_says_whether_it_is_the_catch_all(self):
        """La fenêtre ne doit pas avoir à reconnaître le fourre-tout à son
        libellé : un libellé se traduit, un drapeau non."""
        rows = [make_row(index) for index in range(20)]
        for band in self.bands(rows):
            self.assertIn("catch_all", band)
            self.assertFalse(band["catch_all"])

    def test_the_counts_still_add_up(self):
        rows = [make_row(index, gender="F" if index % 2 else "H")
                for index in range(20)]
        rows.append(make_row(99, age=12, gender="H"))
        rows.append(make_row(98, gender=""))
        bandes = self.bands(rows)
        self.assertEqual(sum(band["count"] for band in bandes), 22)
        self.assertEqual(
            sum(band["female"] + band["male"] + band["unknown_sex"]
                for band in bandes), 22)


class TestTheScatterAxesAreConfigurable(unittest.TestCase):
    """Le nuage n'est plus « rémunération × ancienneté » mais un nuage.

    Les deux axes se choisissent, et tout ce qui les nomme — l'écran, la
    restitution, les slides — doit les lire plutôt que les supposer.
    """

    def population(self):
        return build_population([
            make_row(index, salary=30000 + index * 500, age=30 + index % 20,
                     tenure=index % 15)
            for index in range(40)])

    def dataset(self, **chart):
        from hr_analytics.core.metrics import scatter_dataset

        reglages = {f"chart_parameters.{clef}": valeur
                    for clef, valeur in chart.items()}
        return scatter_dataset(self.population(), make_config(reglages))

    def test_the_axes_come_from_the_declared_fields(self):
        """La même liste que la page des écarts : une seconde ici aurait
        fini par en différer, et une prime maison serait apparue d'un côté
        et pas de l'autre."""
        from hr_analytics.core.metrics import scatter_axes

        axes = scatter_axes(make_config())
        champs = [axis["field"] for axis in axes]
        self.assertIn("base_salary", champs)
        self.assertIn("age_years", champs)
        self.assertIn("tenure_years", champs)
        for axis in axes:
            self.assertTrue(axis["label"])
            self.assertIn(axis["kind"], {"money", "years", "ratio", "number"})

    def test_no_personal_field_can_carry_an_axis(self):
        """Un nuage dont l'axe porte un matricule n'est pas un nuage, et sa
        légende entrerait dans les documents."""
        from hr_analytics.core.metrics import scatter_axes
        from hr_analytics.core.segmentation import personal_fields

        config = make_config()
        interdits = set(personal_fields(config))
        for axis in scatter_axes(config):
            self.assertNotIn(axis["field"], interdits)

    def test_the_dataset_follows_the_chosen_axes(self):
        données = self.dataset(scatter_x="age_years",
                               scatter_y="variable_pay")
        self.assertEqual(données["x_field"], "age_years")
        self.assertEqual(données["y_field"], "variable_pay")

    def test_each_axis_carries_its_label_and_its_unit(self):
        """« EUR » ou « ans » ne se devinent pas d'un nom de champ."""
        données = self.dataset(scatter_x="age_years", scatter_y="base_salary")
        self.assertEqual(données["x_axis"]["label"], "Âge")
        self.assertEqual(données["x_axis"]["kind"], "years")
        self.assertEqual(données["y_axis"]["label"], "Salaire de base")
        self.assertEqual(données["y_axis"]["kind"], "money")

    def test_an_axis_nobody_fills_says_so_rather_than_blaming_the_headcount(self):
        """Le nuage s'appelait « Rémunération/Ancienneté » et son titre
        disait pourquoi il disparaissait ; il s'appelle « Nuage de points »,
        c'est donc au message de le dire."""
        from hr_analytics.core.metrics import scatter_dataset

        population = build_population([
            make_row(index, salary=30000 + index * 100, hire_date="")
            for index in range(40)])
        données = scatter_dataset(population, make_config())
        self.assertFalse(données["available"])
        self.assertIn("Ancienneté", données["warning"])
        self.assertIn("aucun salarié", données["warning"])
        self.assertNotIn("Effectif insuffisant", données["warning"])

    def test_a_small_population_still_blames_the_headcount(self):
        population = build_population([
            make_row(index, salary=30000) for index in range(4)])
        from hr_analytics.core.metrics import scatter_dataset

        données = scatter_dataset(population, make_config())
        self.assertFalse(données["available"])
        self.assertIn("Effectif insuffisant", données["warning"])

    def test_the_axes_are_named_even_when_nothing_can_be_drawn(self):
        """La fenêtre remplit ses deux listes depuis le jeu de données :
        vide, il doit quand même dire sur quoi il portait."""
        population = build_population([
            make_row(index, salary=30000) for index in range(4)])
        from hr_analytics.core.metrics import scatter_dataset

        données = scatter_dataset(population, make_config())
        self.assertEqual(données["x_axis"]["label"], "Ancienneté")
        self.assertEqual(données["y_axis"]["label"], "Salaire de base")


class TestAHalfPublishedOverview(unittest.TestCase):
    """Deux moitiés, deux seuils : l'une peut tomber quand l'autre tient.

    La population se masque sur l'effectif, la rémunération sur le nombre
    de montants connus. Une équipe de neuf dont trois salaires sont
    renseignés publie donc la première et masque la seconde — et il faut
    que la raison le dise, sans quoi « effectif insuffisant » devant neuf
    salariés se lit comme une erreur de l'outil.
    """

    def _population(self, effectif=9, renseignes=3):
        rows = [make_row(index,
                         salary=40000 + index * 500 if index < renseignes
                         else None)
                for index in range(effectif)]
        return build_population(rows)

    def test_the_population_half_is_published(self):
        config = make_config()
        bloc = metrics.calculate_population_metrics(self._population(), config)
        self.assertFalse(bloc["masked"])
        self.assertEqual(bloc["headcount"], 9)

    def test_the_salary_half_is_masked(self):
        config = make_config()
        bloc = metrics.calculate_salary_metrics(self._population(), config)
        self.assertTrue(bloc["masked"])
        self.assertEqual(bloc["valued_headcount"], 3)
        self.assertEqual(bloc["headcount"], 9)

    def test_the_reason_blames_the_values_and_not_the_headcount(self):
        """« Effectif insuffisant » devant neuf salariés envoie chercher un
        seuil réglé sur neuf. Il ne l'a jamais été."""
        config = make_config()
        bloc = metrics.calculate_salary_metrics(self._population(), config)
        raison = bloc["warning"]
        self.assertIn("3", raison)
        self.assertIn("9", raison)
        self.assertIn("colonne analysée", raison)
        self.assertNotIn("Effectif insuffisant", raison)

    def test_an_empty_column_says_so(self):
        config = make_config()
        bloc = metrics.calculate_salary_metrics(
            self._population(renseignes=0), config)
        self.assertTrue(bloc["masked"])
        self.assertIn("Aucune valeur", bloc["warning"])

    def test_a_small_team_still_blames_the_headcount(self):
        """Quand l'effectif ne suffit pas non plus, c'est lui qu'on nomme."""
        config = make_config()
        bloc = metrics.calculate_salary_metrics(
            self._population(effectif=3, renseignes=3), config)
        self.assertTrue(bloc["masked"])
        self.assertIn("Effectif insuffisant", bloc["warning"])


class TestAScaleIsReadInItsOwnOrder(unittest.TestCase):
    """Un coefficient se lit dans l'ordre des nombres.

    L'outil savait ranger « G1..G8 » et les tranches d'âge, mais pas une
    échelle décimale : le motif ordinal ne reconnaît pas « 106,5 », et
    l'ordre alphabétique range 100, 1000, 110. Sur une abscisse de boîtes
    à moustaches, cela défait la progression même qu'on vient lire.
    """

    def ordre(self, valeurs, **reglages):
        from hr_analytics.core.metrics import calculate_segment_metrics

        config = make_config(reglages or None)
        lignes = [make_row(index, groupe=valeurs[index % len(valeurs)])
                  for index in range(len(valeurs) * 8)]
        bloc = calculate_segment_metrics(build_population(lignes, config),
                                         config, "groupe")
        return [ligne["segment"] for ligne in bloc["rows"]]

    def test_numbers_are_ordered_as_numbers(self):
        """Le témoin de l'ancien défaut : 1000 se rangeait entre 100 et
        110."""
        self.assertEqual(self.ordre(["110", "1000", "100"]),
                         ["100", "110", "1000"])

    def test_a_decimal_scale_is_ordered_too(self):
        """Le motif ordinal ne reconnaît pas « 99.5 » : l'échelle retombait
        alors sur l'alphabétique, qui range 100 avant 99."""
        self.assertEqual(self.ordre(["100", "99.5", "106.5"]),
                         ["99.5", "100", "106.5"])

    def test_a_comma_is_a_decimal_point(self):
        """Une colonne saisie à la main porte volontiers « 132,5 »."""
        self.assertEqual(self.ordre(["100", "99,5", "106,5"]),
                         ["99,5", "100", "106,5"])

    def test_an_unfilled_value_does_not_undo_the_scale(self):
        """Une seule valeur vide suffisait à faire retomber l'échelle
        entière sur l'ordre alphabétique."""
        from hr_analytics.core.segmentation import UNKNOWN_LABEL

        rangs = self.ordre(["110", "1000", "100", ""])
        self.assertEqual(rangs[:3], ["100", "110", "1000"])
        self.assertEqual(rangs[-1], UNKNOWN_LABEL)

    def test_named_scales_still_work(self):
        self.assertEqual(self.ordre(["G10", "G2", "G1"]), ["G1", "G2", "G10"])

    def test_plain_labels_keep_the_configured_order(self):
        """Une dimension sans échelle propre suit le réglage d'Apparence,
        et non un ordre décidé ici."""
        self.assertEqual(self.ordre(["Nord", "Est", "Ouest"]),
                         ["Est", "Nord", "Ouest"])


class TestAWholeNumberIsWrittenWhole(unittest.TestCase):
    """« 230.0 » n'est pas un coefficient.

    Un coefficient est déclaré numérique — il se compare, il se trie — et
    il revenait donc avec une décimale que personne n'a saisie : sur
    l'abscisse des boîtes, dans les listes de filtres, dans les tableaux
    et dans les documents.
    """

    def test_a_whole_number_loses_its_decimal(self):
        from hr_analytics.core.segmentation import segment_label

        self.assertEqual(segment_label(230.0), "230")

    def test_a_real_decimal_keeps_it(self):
        from hr_analytics.core.segmentation import segment_label

        self.assertEqual(segment_label(106.5), "106.5")

    def test_a_text_value_is_untouched(self):
        from hr_analytics.core.segmentation import segment_label

        self.assertEqual(segment_label("  Nord  "), "Nord")

    def test_the_segments_of_a_numeric_field_read_whole(self):
        """Le vrai juge : ce que le découpage publie."""
        from hr_analytics.core.segmentation import split_by

        config = make_config({"population_mapping.numeric":
                              ["base_salary", "coefficient"]})
        lignes = [make_row(index, groupe=str(100 + index % 3 * 10))
                  for index in range(30)]
        cles = list(split_by(build_population(lignes, config), "groupe"))
        self.assertEqual(sorted(cles), ["100", "110", "120"])


class TestAnArrangementPutByHand(unittest.TestCase):
    """Un rangement posé à la main prime sur tous les ordres calculés.

    Alphabetique, effectif, mediane, echelle : chacun repond a une
    question, mais aucun ne connait la convention d'une maison. Un metier
    se lit parfois dans l'ordre d'une grille, une filiale dans celui d'un
    organigramme — ce sont des decisions, pas des deductions, et l'outil
    ne les retrouvera jamais tout seul.
    """

    def bloc(self, valeurs, rangement=None, champ="groupe"):
        from hr_analytics.core.metrics import calculate_segment_metrics

        reglages = {}
        if rangement is not None:
            reglages["chart_parameters.segment_manual_order"] = {champ: rangement}
        config = make_config(reglages)
        lignes = [make_row(index, groupe=valeurs[index % len(valeurs)])
                  for index in range(len(valeurs) * 8)]
        return calculate_segment_metrics(build_population(lignes, config),
                                         config, champ)

    def ordre(self, valeurs, rangement=None):
        return [ligne["segment"] for ligne in self.bloc(valeurs, rangement)["rows"]]

    def test_without_an_arrangement_nothing_changes(self):
        self.assertEqual(self.ordre(["Nord", "Est", "Ouest"]),
                         ["Est", "Nord", "Ouest"])

    def test_the_arrangement_decides_the_order(self):
        self.assertEqual(
            self.ordre(["Nord", "Est", "Ouest"], ["Ouest", "Nord", "Est"]),
            ["Ouest", "Nord", "Est"])

    def test_it_beats_a_numbered_scale(self):
        """Le cas le plus fort : même une échelle, que l'outil sait pourtant
        ranger, cède à une décision explicite."""
        self.assertEqual(self.ordre(["100", "110", "120"], ["120", "100"]),
                         ["120", "100", "110"])

    def test_what_it_does_not_name_goes_last_in_its_usual_order(self):
        """Un métier apparu ce mois-ci ne disparaît pas, et ne s'invite pas
        au milieu."""
        self.assertEqual(
            self.ordre(["Nord", "Est", "Ouest", "Sud"], ["Ouest"]),
            ["Ouest", "Est", "Nord", "Sud"])

    def test_an_arranged_value_absent_from_the_file_is_ignored(self):
        """Le rangement garde la trace d'un métier que la population du
        mois ne porte pas : il ne doit rien décaler."""
        self.assertEqual(
            self.ordre(["Nord", "Est"], ["Disparu", "Est", "Nord"]),
            ["Est", "Nord"])

    def test_it_matches_without_case_or_accents(self):
        """La casse et les accents sont déjà indifférents partout ailleurs
        dans l'outil : un rangement saisi au bloc-notes ne doit pas être le
        seul endroit où « RELIURE » ne retrouve pas « Reliure »."""
        # « Reliure » vient après « Édition » dans l'ordre alphabétique :
        # s'il passe en tête, c'est que la casse et les accents ont bien
        # été ignorés, et non que le hasard a bien fait.
        self.assertEqual(
            self.ordre(["Édition", "Reliure"], ["RELIURE"]),
            ["Reliure", "Édition"])

    def test_a_malformed_setting_is_ignored_rather_than_fatal(self):
        """Le fichier s'édite au bloc-notes : une faute de frappe ne doit
        pas empêcher l'analyse."""
        from hr_analytics.core.metrics import manual_order

        for valeur in ("Nord", 42, None, ["Nord", "", "  "]):
            config = make_config(
                {"chart_parameters.segment_manual_order": valeur})
            self.assertIsInstance(manual_order(config, "groupe"), list)

    def test_an_existing_block_can_be_rearranged_without_recomputing(self):
        """Changer un ordre ne change aucun chiffre : relancer l'analyse
        entière ferait recalculer ce qui est juste."""
        from hr_analytics.core.config import Configuration
        from hr_analytics.core.metrics import reorder_segments

        valeurs = ["Nord", "Est", "Ouest"]
        bloc = self.bloc(valeurs)
        avant = {ligne["segment"]: ligne["salary"]["median"]
                 for ligne in bloc["rows"]}
        données = make_config().as_dict()
        données["chart_parameters"]["segment_manual_order"] = {
            "groupe": ["Ouest", "Nord"]}
        lignes = [make_row(index, groupe=valeurs[index % 3])
                  for index in range(24)]
        reorder_segments(bloc, Configuration(données),
                         build_population(lignes))
        self.assertEqual([ligne["segment"] for ligne in bloc["rows"]],
                         ["Ouest", "Nord", "Est"])
        self.assertEqual({ligne["segment"]: ligne["salary"]["median"]
                          for ligne in bloc["rows"]}, avant)


class TestTheBottomBandIsNeverMissing(unittest.TestCase):
    """Un découpage qui commence à 20 ans range un apprenti de 19 ans dans
    « (non renseigné) » : il a un âge, et le tableau disait qu'il n'en
    avait pas.

    Le haut du découpage se prolonge déjà jusqu'à la valeur observée ; le
    bas se ferme de la même façon. Un fichier de paramètres antérieur à la
    tranche « <20 » la retrouve donc sans qu'on le retouche : les réglages
    survivent aux mises à jour, et c'est ici qu'une tranche manquante se
    complète.
    """

    SANS_BAS = [{"label": "20-29", "min": 20, "max": 29, "max_inclusive": True},
                {"label": "30+", "min": 30, "max": None}]

    def test_a_band_set_starting_above_zero_gets_its_floor(self):
        from hr_analytics.core.normalize import close_the_bottom

        bandes = close_the_bottom(self.SANS_BAS)
        self.assertEqual(bandes[0], {"label": "<20", "min": 0, "max": 20.0})
        self.assertEqual(bandes[1:], self.SANS_BAS)

    def test_a_band_set_already_closed_is_left_alone(self):
        from hr_analytics.core.normalize import close_the_bottom

        bandes = [{"label": "<20", "min": 0, "max": 20}] + self.SANS_BAS
        self.assertEqual(close_the_bottom(bandes), bandes)

    def test_the_label_follows_the_setting(self):
        from hr_analytics.core.normalize import close_the_bottom

        self.assertEqual(close_the_bottom(self.SANS_BAS, "moins de {high}")[0]["label"],
                         "moins de 20")

    def test_a_nineteen_year_old_lands_in_it(self):
        """Le vrai juge : la pyramide d'un fichier dont les réglages
        n'ont jamais connu la tranche."""
        from hr_analytics.core.metrics import calculate_population_metrics
        import datetime as dt

        config = make_config({"age_parameters.bands": self.SANS_BAS})
        jeune = make_row(0, birth_date=dt.date(2007, 6, 1))
        lignes = [jeune] + [make_row(index) for index in range(1, 30)]
        bloc = calculate_population_metrics(build_population(lignes, config),
                                            config)
        tranches = {ligne["label"]: ligne for ligne in bloc["age_bands"]}
        self.assertIn("<20", tranches)
        self.assertEqual(tranches["<20"]["count"], 1)
        self.assertFalse(any(ligne.get("catch_all") and ligne["count"]
                             for ligne in bloc["age_bands"]))


class TestADeclaredNumberBecomesAnAxis(unittest.TestCase):
    """Les listes X et Y du nuage ne proposaient que les grandeurs du
    moteur : un montant déclaré depuis « Associer les colonnes » (rôle
    « Montant ») n'apparaissait nulle part, alors que le rôle promettait un
    champ d'analyse. Les autres listes suivent ce qui est déclaré ; celles-ci
    aussi."""

    def _config(self):
        données = make_config().as_dict()
        mapping = données["population_mapping"]
        mapping["fields"]["prime_de_panier"] = ["Prime de panier"]
        mapping["numeric"] = list(mapping["numeric"]) + ["prime_de_panier"]
        mapping["money"] = list(mapping["money"]) + ["prime_de_panier"]
        from hr_analytics.core.config import Configuration

        return Configuration(données)

    def test_a_declared_amount_is_offered_as_money(self):
        from hr_analytics.core.metrics import scatter_axes

        axes = {axis["field"]: axis for axis in scatter_axes(self._config())}
        self.assertIn("prime_de_panier", axes)
        self.assertEqual(axes["prime_de_panier"]["label"], "Prime de panier")
        self.assertEqual(axes["prime_de_panier"]["kind"], "money")

    def test_a_declared_number_is_offered_as_a_number(self):
        """Le coefficient de la configuration d'essai est numérique sans
        être un montant : il se porte en axe, sans symbole monétaire."""
        from hr_analytics.core.metrics import scatter_axes

        axes = {axis["field"]: axis for axis in scatter_axes(make_config())}
        self.assertIn("coefficient", axes)
        self.assertEqual(axes["coefficient"]["kind"], "number")

    def test_the_engine_quantities_come_first_and_once(self):
        from hr_analytics.core.metrics import scatter_axes

        champs = [axis["field"] for axis in scatter_axes(self._config())]
        self.assertEqual(len(champs), len(set(champs)))
        self.assertEqual(champs[0], "base_salary")
        self.assertLess(champs.index("fte"), champs.index("prime_de_panier"))

    def test_the_cloud_can_be_drawn_on_it(self):
        from hr_analytics.core.metrics import scatter_dataset
        from hr_analytics.core.mapping import resolve_mapping
        from hr_analytics.core.normalize import normalise_table

        config = self._config()
        en_têtes = list(HEADERS) + ["Prime de panier"]
        lignes = [list(make_row(i, salary=30000 + i * 500)) + [100 + i]
                  for i in range(40)]
        population = normalise_table(en_têtes, lignes,
                                     resolve_mapping(en_têtes, config), config)
        données = config.as_dict()
        données["chart_parameters"]["scatter_y"] = "prime_de_panier"
        from hr_analytics.core.config import Configuration

        nuage = scatter_dataset(population, Configuration(données))
        self.assertEqual(nuage["y_field"], "prime_de_panier")
        self.assertEqual(len(nuage["points"]), 40)


class TestTheAxesOfferedAreThoseTheFileCarries(unittest.TestCase):
    """Les listes X et Y proposaient « Rémunération totale » ou « Temps de
    travail » à qui n'a aucune de ces colonnes, et les choisir donnait un
    nuage vide. Un axe est proposé si au moins un salarié y porte un
    nombre."""

    def _population(self, **extra):
        from hr_analytics.core.config import Configuration
        from hr_analytics.core.mapping import resolve_mapping
        from hr_analytics.core.normalize import normalise_table

        données = make_config().as_dict()
        mapping = données["population_mapping"]
        en_têtes = list(HEADERS)
        lignes = [list(make_row(i, salary=30000 + i * 500)) for i in range(20)]
        for champ, (intitulé, valeurs) in extra.items():
            mapping["fields"][champ] = [intitulé]
            mapping["numeric"] = list(mapping["numeric"]) + [champ]
            mapping["money"] = list(mapping["money"]) + [champ]
            en_têtes.append(intitulé)
            for rang, ligne in enumerate(lignes):
                ligne.append(valeurs(rang))
        config = Configuration(données)
        population = normalise_table(en_têtes, lignes,
                                     resolve_mapping(en_têtes, config), config)
        return population, config

    def test_a_quantity_without_a_column_is_not_offered(self):
        from hr_analytics.core.metrics import available_axes, scatter_axes

        population, config = self._population()
        offerts = [a["field"] for a in available_axes(population, config)]
        self.assertIn("base_salary", offerts)
        self.assertIn("tenure_years", offerts)
        self.assertIn("age_years", offerts)
        self.assertNotIn("total_compensation", offerts)
        self.assertNotIn("fte", offerts)
        # Le témoin : la configuration, elle, les permet toujours.
        self.assertIn("total_compensation",
                      [a["field"] for a in scatter_axes(config)])

    def test_a_declared_amount_the_file_fills_is_offered(self):
        from hr_analytics.core.metrics import available_axes

        population, config = self._population(
            prime=("Prime", lambda rang: 100 + rang))
        self.assertIn("prime", [a["field"] for a in available_axes(population, config)])

    def test_a_declared_amount_nobody_fills_is_not(self):
        from hr_analytics.core.metrics import available_axes

        population, config = self._population(
            prime=("Prime", lambda rang: ""))
        self.assertNotIn("prime", [a["field"] for a in available_axes(population, config)])

    def test_the_order_of_the_configuration_is_kept(self):
        from hr_analytics.core.metrics import available_axes, scatter_axes

        population, config = self._population()
        tous = [a["field"] for a in scatter_axes(config)]
        offerts = [a["field"] for a in available_axes(population, config)]
        self.assertEqual(offerts, [c for c in tous if c in offerts])
