"""Le glossaire doit dire ce que le moteur calcule.

Une info-bulle qui enonce une formule differente de celle appliquee est pire
que pas d'info-bulle : elle fait valider un chiffre pour de mauvaises
raisons. Ces tests confrontent donc chaque formule annoncee au resultat du
moteur sur des series connues, et verifient qu'aucun champ affiche a l'ecran
ne reste sans explication.

Aucune donnee RH reelle n'est utilisee.
"""

import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, REFERENCE_DATE, make_row
from tests.test_ui import needs_display
from compensation_analytics.core import glossary
from compensation_analytics.core import statistics_engine as stats
from compensation_analytics.core.pay_equity import _gap
from compensation_analytics.io.xlsx_writer import write_workbook


class TestTheGlossaryIsWellFormed(unittest.TestCase):

    def test_every_entry_carries_a_definition_and_a_formula(self):
        for key, entry in glossary.GLOSSARY.items():
            with self.subTest(key=key):
                self.assertTrue(entry.definition.strip(), key)
                self.assertTrue(entry.formula.strip(), key)
                # Une phrase finie : ces textes s'affichent tels quels.
                self.assertTrue(entry.definition.rstrip().endswith("."), key)
                self.assertTrue(entry.formula.rstrip().endswith("."), key)

    def test_an_unknown_key_gives_nothing_rather_than_a_wrong_answer(self):
        self.assertIsNone(glossary.describe("indicateur_inexistant"))


class TestTheFormulasMatchTheEngine(unittest.TestCase):
    """Chaque formule annoncee est verifiee sur une serie connue."""

    SERIES = [1.0, 2.0, 3.0, 4.0]

    def test_percentiles_are_the_inclusive_method_that_is_announced(self):
        for key in ("median", "p10", "p25", "p50", "p75", "p90", "age_median",
                    "tenure_median"):
            with self.subTest(key=key):
                self.assertIn("inclusive", glossary.describe(key).formula)
                self.assertIn("PERCENTILE.INCLUSIVE",
                              glossary.describe(key).formula)
        # Interpolation lineaire de type 7 : sur 1,2,3,4 le premier quartile
        # vaut 1,75 — la valeur que renvoie PERCENTILE.INCLUSIVE d'Excel.
        self.assertAlmostEqual(stats.percentile(self.SERIES, 25), 1.75)
        self.assertAlmostEqual(stats.percentile(self.SERIES, 50), 2.5)
        self.assertAlmostEqual(stats.percentile(self.SERIES, 90), 3.7)

    def test_the_standard_deviation_uses_the_announced_denominator(self):
        self.assertIn("n − 1", glossary.describe("std_dev").formula)
        self.assertIn("n − 1",
                      glossary.describe("coefficient_of_variation").formula)
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        # Sur echantillon : 4,571… de variance, et non 4 comme sur population.
        self.assertAlmostEqual(stats.standard_deviation(values),
                               2.13808993529939, places=10)

    def test_the_dispersion_ratios_are_those_that_are_announced(self):
        described = stats.describe(self.SERIES)
        spread = stats.dispersion(described)
        self.assertAlmostEqual(spread["interquartile_range"],
                               described["p75"] - described["p25"])
        self.assertAlmostEqual(spread["q3_over_q1"],
                               described["p75"] / described["p25"])
        self.assertAlmostEqual(spread["p90_over_p10"],
                               described["p90"] / described["p10"])
        self.assertAlmostEqual(spread["mean_over_median"],
                               described["mean"] / described["median"])
        self.assertAlmostEqual(spread["coefficient_of_variation"],
                               described["std_dev"] / described["mean"])

    def test_the_dispersion_panel_no_longer_publishes_the_standard_deviation(self):
        """L'ecart-type reste calcule et exporte, mais n'est plus un KPI."""
        self.assertNotIn("std_dev", stats.dispersion(
            stats.describe(self.SERIES)))
        self.assertIsNotNone(stats.describe(self.SERIES)["std_dev"])

    def test_the_pay_gap_sign_is_the_one_the_glossary_announces(self):
        """Ecart positif = femmes moins remunerees, comme la directive."""
        pattern = re.compile(
            r"\((Moyenne|Médiane) des hommes − \1 des femmes\) / \1 des hommes")
        for key in ("mean_gap", "median_gap", "variable_mean_gap"):
            with self.subTest(key=key):
                self.assertRegex(glossary.describe(key).formula, pattern)
        self.assertGreater(_gap(50000, 45000), 0)      # femmes en dessous
        self.assertLess(_gap(45000, 50000), 0)
        self.assertAlmostEqual(_gap(50000, 45000), 10.0)


#: Libelles qui ne designent pas un indicateur : titres de groupe et
#: en-tetes de colonne. Tout le reste doit s'expliquer au survol.
STRUCTURE = {"POPULATION", "RÉMUNÉRATION", "PERCENTILE", "VALEUR",
             "INDICATEUR", "FEMMES", "HOMMES"}


@needs_display
class TestEveryFieldOnScreenIsExplained(unittest.TestCase):
    """Aucun chiffre de la vue d'ensemble ne reste sans definition.

    Le test parcourt la page rendue plutot qu'une liste tenue a la main :
    un indicateur ajoute demain sans info-bulle fait tomber ce test.
    """

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "population.xlsx")
        write_workbook(cls.source, [("Population", [HEADERS] + [
            make_row(index, salary=30000 + index * 37,
                     age=28 + index % 30, tenure=index % 18,
                     gender=["F", "H"][index % 2])
            for index in range(120)])])

    def setUp(self):
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        from compensation_analytics.ui.app import Application
        self.app = Application()
        self.app.update()
        self.app.result = run_analysis(AnalysisRequest(
            source_path=self.source, reference_date=REFERENCE_DATE,
            segments=[]))
        self.app._render_results()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _labels(self, frame):
        import tkinter as tk

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)

        return [widget for widget in walk(frame) if isinstance(widget, tk.Label)]

    def test_each_field_answers_to_a_hover(self):
        unexplained = [
            widget.cget("text") for widget in self._labels(self.app.overview_frame)
            if widget.cget("text") not in STRUCTURE
            and not widget.bind("<Enter>")
        ]
        self.assertEqual(unexplained, [], "champs sans info-bulle")

    def test_the_hover_gives_a_definition_and_a_formula(self):
        for widget in self._labels(self.app.overview_frame):
            if widget.cget("text") != "Coefficient de variation":
                continue
            widget.event_generate("<Enter>")
            self.app.hints._cancel()
            self.app.hints._show(widget, ("Coefficient de variation",)
                                 + glossary.describe(
                                     "coefficient_of_variation"))
            self.app.update()
            texts = [line.cget("text") for line in self.app.hints.lines
                     if line.winfo_manager()]
            self.assertEqual(len(texts), 3)
            self.assertIn("Dispersion relative", texts[1])
            self.assertIn("Écart-type / Moyenne", texts[2])
            return
        self.fail("« Coefficient de variation » absent de la page")

    def test_the_standard_deviation_has_left_the_page(self):
        shown = [widget.cget("text")
                 for widget in self._labels(self.app.overview_frame)]
        self.assertNotIn("Écart-type", shown)

    def test_the_bubble_is_shared_by_every_field(self):
        """Une seule fenetre, quel que soit le nombre d'indicateurs."""
        labels = [widget for widget in self._labels(self.app.overview_frame)
                  if widget.bind("<Enter>")]
        self.assertGreater(len(labels), 20)
        for widget in labels[:5]:
            self.app.hints._show(widget, ("Titre", "Definition."))
            self.app.update()
        windows = [child for child in self.app.winfo_children()
                   if child.winfo_class() == "Toplevel"]
        self.assertEqual(len(windows), 1)


if __name__ == "__main__":
    unittest.main()
