"""Tests du moteur statistique : valeurs de reference calculees a la main.

Les percentiles sont alignes sur PERCENTILE.INCLUSIVE d'Excel, afin que les
controles faits par les equipes RH sous Excel donnent le meme resultat.
"""

import unittest

from tests.support import *  # noqa: F401,F403  (chemin d'import)
from compensation_analytics.core import statistics_engine as stats


class TestDescriptiveStatistics(unittest.TestCase):
    def setUp(self):
        self.values = [30000, 32000, 35000, 38000, 41000, 45000, 52000, 60000,
                       75000, 95000]

    def test_mean(self):
        self.assertAlmostEqual(stats.mean(self.values), 50300.0)

    def test_median_even_sample(self):
        self.assertAlmostEqual(stats.median(self.values), 43000.0)

    def test_median_odd_sample(self):
        self.assertAlmostEqual(stats.median([1, 2, 3]), 2.0)

    def test_percentiles_match_excel_inclusive(self):
        # Verifie contre PERCENTILE.INC : positions interpolees lineairement.
        self.assertAlmostEqual(stats.percentile(self.values, 10), 31800.0)
        self.assertAlmostEqual(stats.percentile(self.values, 25), 35750.0)
        self.assertAlmostEqual(stats.percentile(self.values, 50), 43000.0)
        self.assertAlmostEqual(stats.percentile(self.values, 75), 58000.0)
        self.assertAlmostEqual(stats.percentile(self.values, 90), 77000.0)

    def test_percentile_single_value(self):
        self.assertEqual(stats.percentile([42000], 90), 42000)

    def test_percentile_empty(self):
        self.assertIsNone(stats.percentile([], 50))

    def test_percentile_out_of_range(self):
        with self.assertRaises(ValueError):
            stats.percentile(self.values, 120)

    def test_clean_removes_missing_and_non_numeric(self):
        self.assertEqual(stats.clean([1, None, "x", 2, True, float("nan")]), [1.0, 2.0])

    def test_standard_deviation_requires_two_values(self):
        self.assertIsNone(stats.standard_deviation([42000]))

    def test_describe_is_robust_to_missing_values(self):
        described = stats.describe([40000, None, 60000, None])
        self.assertEqual(described["count"], 2)
        self.assertAlmostEqual(described["mean"], 50000.0)


class TestDispersion(unittest.TestCase):
    def test_ratios(self):
        described = stats.describe([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        spread = stats.dispersion(described)
        self.assertAlmostEqual(spread["interquartile_range"], 45.0)
        self.assertAlmostEqual(spread["q3_over_q1"], 77.5 / 32.5)
        self.assertAlmostEqual(spread["p90_over_p10"], 91.0 / 19.0)
        self.assertAlmostEqual(spread["mean_over_median"], 1.0)

    def test_ratios_none_when_denominator_is_zero(self):
        spread = stats.dispersion({"p25": 0, "p75": 10, "p10": 0, "p90": 5,
                                   "mean": 5, "median": 0, "std_dev": 1})
        self.assertIsNone(spread["q3_over_q1"])
        self.assertIsNone(spread["p90_over_p10"])
        self.assertIsNone(spread["mean_over_median"])


class TestDistributionTools(unittest.TestCase):
    def test_histogram_bin_counts(self):
        bins = stats.histogram([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], bins=5)
        self.assertEqual([item["count"] for item in bins], [2, 2, 2, 2, 2])
        self.assertEqual(sum(item["count"] for item in bins), 10)

    def test_histogram_constant_values(self):
        bins = stats.histogram([5, 5, 5], bins=4)
        self.assertEqual(len(bins), 1)
        self.assertEqual(bins[0]["count"], 3)

    def test_histogram_empty(self):
        self.assertEqual(stats.histogram([], bins=5), [])

    def test_linear_regression_perfect_fit(self):
        trend = stats.linear_regression([0, 1, 2, 3], [1000, 2000, 3000, 4000])
        self.assertAlmostEqual(trend["slope"], 1000.0)
        self.assertAlmostEqual(trend["intercept"], 1000.0)
        self.assertAlmostEqual(trend["r_squared"], 1.0)

    def test_linear_regression_needs_three_points(self):
        self.assertIsNone(stats.linear_regression([1, 2], [1, 2]))

    def test_linear_regression_flat_x(self):
        self.assertIsNone(stats.linear_regression([5, 5, 5], [1, 2, 3]))

    def test_outlier_bounds(self):
        bounds = stats.iqr_outlier_bounds([10, 12, 14, 16, 18, 20, 100], 1.5)
        self.assertLess(bounds["upper"], 100)
        self.assertIsNotNone(bounds["lower"])

    def test_outlier_bounds_small_sample(self):
        self.assertIsNone(stats.iqr_outlier_bounds([10, 20, 30], 1.5))


if __name__ == "__main__":
    unittest.main()
