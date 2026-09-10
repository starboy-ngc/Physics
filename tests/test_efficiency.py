"""Ce que l'outil coute, et ce qu'il ne doit pas se remettre a couter.

Un outil local tourne sur le portable d'un analyste, pas sur un serveur :
une paie de 50 000 lignes doit passer, et le cout par salarie ne doit pas
grimper avec l'effectif. Les tests qui suivent ne chronometrent presque
rien — une machine chargee rendrait la suite capricieuse. Ils comptent les
operations, ce qui est reproductible : c'est le nombre de tris et de
lectures qui decide du temps, pas l'horloge.

Aucune donnee RH reelle.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from compensation_analytics.core import metrics
from compensation_analytics.core import statistics_engine as stats


class CountingSort:
    """Remplace `sorted` dans un module, et compte les appels."""

    def __init__(self, module):
        self.module = module
        self.calls = 0

    def __enter__(self):
        self.original = getattr(self.module, "sorted", sorted)

        def counted(values, **kwargs):
            self.calls += 1
            return self.original(values, **kwargs)

        self.module.sorted = counted
        return self

    def __exit__(self, *_exception):
        if hasattr(self.module, "__dict__") and "sorted" in self.module.__dict__:
            del self.module.sorted


class TestSortingOnce(unittest.TestCase):
    """Le tri est le seul cout d'un percentile : il ne se paie qu'une fois."""

    VALUES = [float(value) for value in range(1000)]

    def test_describe_sorts_a_single_time(self):
        """Mediane, minimum, maximum et cinq percentiles se lisent tous sur
        la meme liste ordonnee. Les calculer separement triait sept fois de
        suite, ce qui rendait l'analyse sensiblement plus que lineaire."""
        with CountingSort(stats) as counter:
            stats.describe(self.VALUES)
        self.assertEqual(counter.calls, 1)

    def test_a_longer_list_of_percentiles_still_sorts_once(self):
        with CountingSort(stats) as counter:
            stats.describe(self.VALUES, percentiles=(1, 5, 10, 25, 50, 75,
                                                     90, 95, 99))
        self.assertEqual(counter.calls, 1)

    def test_the_figures_are_exactly_those_of_the_separate_calls(self):
        """L'optimisation ne doit rien changer au resultat, pas meme au
        dernier chiffre."""
        values = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0, 5.0, 3.0, 5.0]
        described = stats.describe(values)
        self.assertEqual(described["median"], stats.median(values))
        self.assertEqual(described["min"], stats.minimum(values))
        self.assertEqual(described["max"], stats.maximum(values))
        for rank in (10, 25, 50, 75, 90):
            self.assertEqual(described[f"p{rank}"],
                             stats.percentile(values, rank))

    def test_the_public_percentile_still_accepts_an_unsorted_list(self):
        self.assertEqual(stats.percentile([9.0, 1.0, 5.0], 50), 5.0)

    def test_an_impossible_rank_is_still_refused(self):
        with self.assertRaises(ValueError):
            stats.percentile([1.0, 2.0], 150)
        with self.assertRaises(ValueError):
            stats.describe([1.0, 2.0], percentiles=(150,))


class TestReadingFields(unittest.TestCase):
    """L'analyse relit chaque champ une fois par dimension."""

    def test_a_model_field_and_an_extra_field_read_alike(self):
        """Le chemin rapide ne doit valoir que pour les champs natifs, et
        rendre exactement ce que rendait l'appel de methode."""
        people = build_population([make_row(index, salary=40000 + index)
                                   for index in range(10)])
        for employee in people:
            employee.assign("prime", 100.0 + employee.row_number)
        self.assertEqual(metrics._values(people, "base_salary"),
                         [float(40000 + index) for index in range(10)])
        self.assertEqual(len(metrics._values(people, "prime")), 10)

    def test_an_unknown_field_gives_nothing_rather_than_raising(self):
        people = build_population([make_row(1)])
        self.assertEqual(metrics._values(people, "inexistant"), [])

    def test_a_missing_value_is_left_out_and_not_counted_as_zero(self):
        people = build_population([make_row(1, salary=40000),
                                   make_row(2, salary=None)])
        self.assertEqual(metrics._values(people, "base_salary"), [40000.0])


class TestCleaning(unittest.TestCase):
    """Le nettoyage des valeurs est traverse plusieurs millions de fois."""

    def test_it_keeps_only_usable_numbers(self):
        self.assertEqual(
            stats.clean([1.0, None, "2", True, float("nan"), float("inf"),
                         "x", 3]),
            [1.0, 2.0, 3.0])

    def test_a_boolean_is_never_a_number(self):
        """Sinon « Cadre = Oui » vaudrait 1 dans une moyenne de salaires."""
        self.assertEqual(stats.clean([True, False]), [])

    def test_an_empty_list_stays_empty(self):
        self.assertEqual(stats.clean([]), [])


class TestWholeRunStaysLinear(unittest.TestCase):
    """Un garde-fou large contre une regression en n².

    Le seuil est genereux a dessein : ce test doit attraper un changement
    d'ordre de grandeur, jamais une machine chargee.
    """

    def _population(self, count):
        return build_population([
            make_row(index, salary=30000 + (index % 500) * 90,
                     business_unit=["France", "Iberia", "Benelux"][index % 3],
                     grade=f"G{3 + index % 6}",
                     gender="F" if index % 2 else "H")
            for index in range(count)])

    def _measure(self, count):
        config = make_config()
        people = self._population(count)
        started = time.perf_counter()
        metrics.calculate_salary_metrics(people, config)
        metrics.calculate_population_metrics(people, config)
        for field_name in ("business_unit", "grade"):
            metrics.calculate_segment_metrics(people, config, field_name)
        return time.perf_counter() - started

    def test_four_times_the_headcount_costs_far_less_than_sixteen_times(self):
        small = self._measure(1000)
        large = self._measure(4000)
        # Un cout quadratique donnerait 16 ; un cout lineaire, 4. La borne
        # laisse toute la place au bruit de mesure sans laisser passer un
        # changement d'ordre de grandeur.
        self.assertLess(large, max(small, 0.01) * 9,
                        f"{small:.3f}s pour 1 000 puis {large:.3f}s pour "
                        "4 000 : le cout n'est plus lineaire")


if __name__ == "__main__":
    unittest.main()
