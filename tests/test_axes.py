"""Graduations d'axes et ecriture des durees.

Un axe gradue par simple division de l'etendue affiche les valeurs qui
tombent — « 4 284 EUR », une anciennete de « -0,6 an ». Ces tests fixent la
regle : des valeurs rondes, entieres, et les memes sur les trois supports.
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.core.axes import nice_step, nice_ticks, positions
from compensation_analytics.core.reporting import format_years


class TestTickValues(unittest.TestCase):
    def test_tenure_is_graduated_by_tens(self):
        """Le cas qui a motive la correction : l'axe affichait
        -0,6 / 6,7 / 14,1 / 21,4 / 28,7 / 36,0."""
        self.assertEqual(nice_ticks(-0.6, 36.0), [0.0, 10.0, 20.0, 30.0])

    def test_pay_is_graduated_by_round_amounts(self):
        self.assertEqual(nice_ticks(4284, 142181),
                         [25000.0, 50000.0, 75000.0, 100000.0, 125000.0])

    def test_headcount_starts_at_zero(self):
        self.assertEqual(nice_ticks(0, 373), [0.0, 100.0, 200.0, 300.0])

    def test_no_tick_ever_carries_a_decimal(self):
        """Sur toutes les etendues plausibles, et a tout niveau de zoom."""
        spans = [(0, 1), (0, 7), (0, 36), (-0.6, 36), (5.2, 8.4), (5.2, 5.4),
                 (0, 373), (4284, 142181), (30000, 34000), (0, 1_000_000),
                 (19_999, 20_003)]
        for low, high in spans:
            for value in nice_ticks(low, high):
                self.assertEqual(value, round(value), f"{low}-{high}: {value}")

    def test_ticks_stay_inside_the_range(self):
        """Rien n'est extrapole hors des donnees affichees."""
        for low, high in [(-0.6, 36.0), (4284, 142181), (0, 7)]:
            for value in nice_ticks(low, high):
                self.assertGreaterEqual(value, low)
                self.assertLessEqual(value, high)

    def test_a_range_narrower_than_the_step_still_gets_one_tick(self):
        """Un axe sans aucune graduation ne se lit pas."""
        self.assertEqual(len(nice_ticks(5.2, 5.4)), 1)
        self.assertEqual(len(nice_ticks(3.0, 3.0)), 1)

    def test_the_step_is_the_closest_round_value(self):
        """Arrondir systematiquement vers le haut donnait deux graduations
        la ou il en fallait cinq."""
        self.assertEqual(nice_step(142181 - 4284), 25000)
        self.assertEqual(nice_step(36.6), 10)

    def test_a_degenerate_range_does_not_raise(self):
        for low, high in [(0, 0), (5, 5), (-3, -3), (10, 4)]:
            self.assertTrue(nice_ticks(low, high))

    def test_positions_map_ticks_onto_the_axis(self):
        placed = positions([0.0, 10.0, 20.0], 0.0, 20.0, 100.0)
        self.assertEqual(placed, [0.0, 50.0, 100.0])


class TestYears(unittest.TestCase):
    def test_a_duration_has_no_decimal(self):
        self.assertEqual(format_years(8.0), "8 ans")
        self.assertEqual(format_years(9.4), "9 ans")
        self.assertEqual(format_years(41.7), "42 ans")

    def test_a_missing_duration_stays_readable(self):
        self.assertEqual(format_years(None), "—")

    def test_a_table_column_drops_the_unit_but_keeps_the_rule(self):
        """L'en-tete porte deja « Ancienneté » : la repeter ligne a ligne
        prend de la place sans rien apprendre."""
        self.assertEqual(format_years(10.4, suffix=False), "10")


class TestTheThreeRenderersAgree(unittest.TestCase):
    """L'ecran, le rapport et le PDF doivent graduer de la meme facon : le
    meme graphique ne peut pas se lire differemment selon le support."""

    def _sources(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for path in ("compensation_analytics/core/reporting.py",
                     "compensation_analytics/core/slides.py",
                     "compensation_analytics/ui/charts.py"):
            yield path, open(os.path.join(root, path), encoding="utf-8").read()

    def test_every_renderer_uses_the_shared_ticks(self):
        for path, source in self._sources():
            self.assertIn("nice_ticks", source, path)

    def test_no_renderer_divides_the_range_by_hand(self):
        """La forme « span * step / 4 » est celle qui produisait les
        etiquettes illisibles : elle ne doit reapparaitre nulle part."""
        pattern = re.compile(r"(?:x|y)_span\s*\*\s*step\s*/|peak\s*\*\s*step\s*/")
        for path, source in self._sources():
            self.assertIsNone(pattern.search(source), path)


if __name__ == "__main__":
    unittest.main()
