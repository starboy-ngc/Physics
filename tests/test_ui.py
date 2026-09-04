"""Tests de l'interface graphique.

Ceux qui exigent un affichage sont ignores automatiquement : le moteur doit
rester testable sur un serveur sans ecran, et une installation de Python
depourvue de tkinter doit continuer de fonctionner en ligne de commande.
"""

import ast
import datetime as _dt
import glob
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, REFERENCE_DATE, make_row
from compensation_analytics.io.xlsx_writer import write_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter
    HAS_TK = True
except ImportError:
    HAS_TK = False

HAS_DISPLAY = bool(os.environ.get("DISPLAY")) and HAS_TK
needs_display = unittest.skipUnless(
    HAS_DISPLAY, "aucun affichage disponible (test d'interface ignoré)")


class TestEngineStaysIndependent(unittest.TestCase):
    """Le moteur ne doit jamais importer l'interface, ni tkinter.

    C'est ce qui garantit qu'il tourne en ligne de commande sur un poste ou
    une installation de Python sans tkinter, et qu'il reste automatisable.
    """

    def _engine_files(self):
        for folder in ("core", "io"):
            yield from glob.glob(
                os.path.join(ROOT, "compensation_analytics", folder, "*.py"))
        yield os.path.join(ROOT, "compensation_analytics", "version.py")

    def test_no_tkinter_in_the_engine(self):
        for path in self._engine_files():
            tree = ast.parse(open(path, encoding="utf-8").read())
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".")[0]]
                for name in names:
                    self.assertNotEqual(name, "tkinter", os.path.basename(path))

    def test_no_ui_import_in_the_engine(self):
        for path in self._engine_files():
            source = open(path, encoding="utf-8").read()
            self.assertNotIn("from ..ui", source, os.path.basename(path))
            self.assertNotIn("from .ui", source, os.path.basename(path))


class TestLaunching(unittest.TestCase):
    def test_interface_is_an_explicit_subcommand(self):
        from compensation_analytics.cli import build_parser
        parser = build_parser()
        commands = [a.choices for a in parser._actions if a.choices][0]
        self.assertIn("interface", commands)

    def test_missing_tkinter_gives_a_readable_message(self):
        """Sans tkinter, l'outil explique et renvoie a la ligne de commande
        plutot que d'echouer sur une trace technique."""
        import argparse
        import io
        import contextlib
        from compensation_analytics import cli

        blocked = dict(sys.modules)
        blocked["compensation_analytics.ui.app"] = None  # force l'ImportError
        saved = sys.modules.get("compensation_analytics.ui.app", "absent")
        sys.modules["compensation_analytics.ui.app"] = None
        try:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = cli.command_interface(argparse.Namespace())
            self.assertEqual(code, 3)
            self.assertIn("tkinter", stderr.getvalue())
            self.assertIn("--help", stderr.getvalue())
        finally:
            if saved == "absent":
                sys.modules.pop("compensation_analytics.ui.app", None)
            else:
                sys.modules["compensation_analytics.ui.app"] = saved


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestScatterGeometry(unittest.TestCase):
    """Le calcul de cadrage ne demande pas d'affichage."""

    def test_bounds_add_a_margin(self):
        from compensation_analytics.ui.charts import ScatterChart
        bounds = ScatterChart._compute_bounds(
            [{"x": 0, "y": 10}, {"x": 10, "y": 20}])
        self.assertIsNotNone(bounds)
        x_min, x_max, y_min, y_max = bounds
        # Sans marge, les points extremes collent aux axes.
        self.assertLess(x_min, 0)
        self.assertGreater(x_max, 10)
        self.assertLess(y_min, 10)
        self.assertGreater(y_max, 20)

    def test_bounds_of_an_empty_cloud(self):
        from compensation_analytics.ui.charts import ScatterChart
        self.assertIsNone(ScatterChart._compute_bounds([]))

    def test_a_single_point_still_has_a_frame(self):
        from compensation_analytics.ui.charts import ScatterChart
        x_min, x_max, y_min, y_max = ScatterChart._compute_bounds([{"x": 5, "y": 5}])
        self.assertLess(x_min, x_max)
        self.assertLess(y_min, y_max)


@needs_display
class TestWindow(unittest.TestCase):
    """Parcours complet, sur un affichage virtuel."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "population.xlsx")
        rows = [make_row(i, salary=30000 + (i % 40) * 800,
                         business_unit=["France", "DACH"][i % 2],
                         grade=["G3", "G5", "G7"][i % 3],
                         age=28 + i % 30, tenure=i % 18)
                for i in range(120)]
        write_workbook(cls.source, [("Population", [HEADERS] + rows)])

    def setUp(self):
        from compensation_analytics.ui.app import Application
        self.app = Application()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _load(self):
        from compensation_analytics.core.pipeline import load_population
        population, mapping, _ = load_population(
            self.source, self.app.configuration, reference_date=REFERENCE_DATE)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app._populate_filters()
        self.app._populate_segments()
        self.app.update()

    def test_the_window_opens_with_the_expected_steps(self):
        self.assertEqual(self.app.title(),
                         "Compensation Analytics Engine 1.0.0")
        self.assertEqual(len(self.app.tabs), 6)

    def test_actions_are_disabled_until_a_file_is_loaded(self):
        self.assertIn("disabled", self.app.analyse_button.state())
        self.assertIn("disabled", self.app.export_button.state())

    def test_filters_are_populated_from_the_file(self):
        """L'utilisateur choisit parmi ce que contient son fichier : aucune
        syntaxe a taper, aucune valeur inventee."""
        self._load()
        self.assertIn("business_unit", self.app.filter_vars)
        combobox = None
        for child in self.app.filters_frame.winfo_children():
            for widget in child.winfo_children():
                if widget.winfo_class() == "TCombobox":
                    combobox = widget
                    break
            if combobox:
                break
        self.assertIsNotNone(combobox)
        values = combobox.cget("values")
        self.assertIn("France", values)
        self.assertIn("(toutes)", values)

    def test_a_filter_narrows_the_analysis(self):
        self._load()
        self.app.filter_vars["business_unit"].set("France")
        definitions = self.app._current_filters()
        self.assertEqual(definitions,
                         [{"field": "business_unit", "operator": "eq",
                           "value": "France"}])

    def test_unselected_filters_are_ignored(self):
        self._load()
        self.assertEqual(self.app._current_filters(), [])


if __name__ == "__main__":
    unittest.main()
