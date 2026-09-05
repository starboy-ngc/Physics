"""Tests des indicateurs metier et des regles de petits effectifs."""

import unittest

from tests.support import build_population, make_config, make_row
from compensation_analytics.core import metrics
from compensation_analytics.core.segmentation import build_filters, apply_filters, split_by


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
        self.assertEqual(labels, ["<2 ans", "2-5 ans", "5-10 ans", ">10 ans"])

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
    def test_atypical_situations_use_neutral_wording(self):
        config = make_config()
        rows = [make_row(i, salary=40000 + i * 100) for i in range(30)]
        rows.append(make_row(99, salary=500000))
        population = build_population(rows, config)
        distribution = metrics.calculate_distribution_metrics(population, config)
        self.assertTrue(distribution["available"])
        self.assertEqual(distribution["outlier_label"], "Situation atypique à analyser")
        self.assertTrue(any(item["value"] == 500000 for item in distribution["outliers"]))

    def test_outliers_reference_anonymous_identifier(self):
        config = make_config({"privacy_parameters.anonymise_identifiers": True})
        rows = [make_row(i, salary=40000 + i * 100) for i in range(30)]
        rows.append(make_row(99, salary=500000))
        population = build_population(rows, config)
        outliers = metrics.calculate_distribution_metrics(population, config)["outliers"]
        self.assertTrue(all(not item["reference"].startswith("E0") for item in outliers))

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


class TestSegmentationAndComparison(unittest.TestCase):
    def test_filters_are_combinable(self):
        config = make_config()
        rows = [make_row(0, business_unit="France", grade="G5"),
                make_row(1, business_unit="France", grade="G2"),
                make_row(2, business_unit="DACH", grade="G5")]
        population = build_population(rows, config)
        filters = build_filters([
            {"field": "business_unit", "operator": "eq", "value": "France"},
            {"field": "grade", "operator": "in", "value": ["G5", "G6"]},
        ])
        self.assertEqual(len(apply_filters(population, filters)), 1)

    def test_numeric_filter(self):
        config = make_config()
        rows = [make_row(i, salary=30000 + i * 10000) for i in range(4)]
        population = build_population(rows, config)
        filters = build_filters([
            {"field": "base_salary", "operator": "gte", "value": 50000}
        ])
        self.assertEqual(len(apply_filters(population, filters)), 2)

    def test_filter_matching_is_case_insensitive(self):
        config = make_config()
        population = build_population([make_row(0, business_unit="France")], config)
        filters = build_filters([
            {"field": "business_unit", "operator": "eq", "value": "france"}
        ])
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


if __name__ == "__main__":
    unittest.main()


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
        from compensation_analytics.core.errors import ConfigError
        with self.assertRaises(ConfigError) as caught:
            build_filters([{"field": "team", "operator": "eq", "value": "Alpha"}])
        message = caught.exception.message
        self.assertIn("team", message)
        self.assertIn("n'existe pas", message)
        self.assertIn("business_unit", message)  # liste les champs valides

    def test_misspelled_field_is_caught(self):
        from compensation_analytics.core.errors import ConfigError
        with self.assertRaises(ConfigError):
            build_filters([{"field": "gade", "operator": "eq", "value": "G5"}])

    def test_valid_fields_still_pass(self):
        filters = build_filters([
            {"field": "business_unit", "operator": "eq", "value": "France"},
            {"field": "base_salary", "operator": "gte", "value": 50000},
            {"field": "tenure_band", "operator": "eq", "value": "<2 ans"},
        ])
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
        from compensation_analytics.core.export import _rows_population
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
        rows = [make_row(index, grade=["G3", "G7"][index % 2],
                         salary=30000 if index % 2 == 0 else 60000)
                for index in range(40)]
        return metrics.calculate_segment_metrics(
            build_population(rows, config), config, "grade")

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
        rows = ([make_row(index, grade="G3", salary=30000) for index in range(20)]
                + [make_row(20 + index, grade="G9", salary=90000)
                   for index in range(2)])
        block = metrics.calculate_segment_metrics(
            build_population(rows, config), config, "grade")
        small = [row for row in block["rows"] if row["segment"] == "G9"][0]
        self.assertTrue(small["masked"])
        self.assertIsNone(small["median_gap"])
        self.assertIsNotNone(small["share"])

    def test_the_gap_is_zero_for_a_single_segment(self):
        config = make_config()
        rows = [make_row(index, grade="G4", salary=40000 + index * 100)
                for index in range(20)]
        block = metrics.calculate_segment_metrics(
            build_population(rows, config), config, "grade")
        self.assertAlmostEqual(block["rows"][0]["median_gap"], 0.0, places=6)
