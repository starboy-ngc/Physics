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

def _display_answers() -> bool:
    """DISPLAY renseigne ne veut pas dire affichage joignable.

    Un serveur X arrete laissait la suite tomber en erreur au lieu d'ignorer
    les tests d'interface : la seule reponse fiable est d'essayer d'ouvrir
    une fenetre.
    """
    if not (HAS_TK and os.environ.get("DISPLAY")):
        return False
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        return False
    root.destroy()
    return True


HAS_DISPLAY = _display_answers()
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
        self.assertEqual(len(self.app.tabs), 7)

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


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestDrawnImages(unittest.TestCase):
    """Le canevas Tk ne lisse pas ses traces : les formes fines sont des
    images antialiasees, produites sans la moindre dependance."""

    def test_a_disc_is_round_and_not_square(self):
        """Le defaut corrige : create_oval rendait des carres a coins
        ronges. Un coin de l'image doit donc etre transparent, et son
        centre opaque."""
        from compensation_analytics.ui.raster import Raster, _circle
        size = 9
        raster = Raster(size).paint(_circle(size / 2.0, size / 2.0 - 0.5),
                                    (0, 0, 0))
        corner_alpha = raster.pixels[0][0][3]
        centre_alpha = raster.pixels[size // 2][size // 2][3]
        self.assertEqual(corner_alpha, 0.0)
        self.assertEqual(centre_alpha, 1.0)

    def test_edges_are_partially_transparent(self):
        """C'est la definition de l'antialiasing : sans pixel a opacite
        intermediaire, le bord est un escalier."""
        from compensation_analytics.ui.raster import Raster, _circle
        size = 9
        raster = Raster(size).paint(_circle(size / 2.0, size / 2.0 - 0.5),
                                    (0, 0, 0))
        alphas = {pixel[3] for row in raster.pixels for pixel in row}
        partial = [value for value in alphas if 0.0 < value < 1.0]
        self.assertTrue(partial, "aucun pixel de bord adouci")

    def test_the_images_are_valid_png(self):
        from compensation_analytics.ui import raster
        import base64
        for data in (raster.disc(7, (47, 93, 138)),
                     raster.checkbox(15, True, (47, 93, 138), (47, 93, 138))):
            self.assertTrue(base64.b64decode(data).startswith(b"\x89PNG\r\n\x1a\n"))

    def test_images_are_computed_once_per_appearance(self):
        """Un nuage de 2 000 points ne doit pas recalculer 2 000 images."""
        from compensation_analytics.ui import raster
        first = raster.disc(7, (10, 20, 30))
        self.assertIs(first, raster.disc(7, (10, 20, 30)))

    def test_a_checked_box_differs_from_an_unchecked_one(self):
        from compensation_analytics.ui import raster
        colour, border = (47, 93, 138), (207, 215, 223)
        self.assertNotEqual(raster.checkbox(15, True, colour, border),
                            raster.checkbox(15, False, colour, border))


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestScrollbarsAreUsable(unittest.TestCase):
    def test_the_scrollbar_is_wide_enough_to_grab(self):
        """Le defaut corrige : "arrowsize=0" reduisait l'ascenseur a un
        pixel de large. Il defilait, mais aucun curseur ne l'attrapait."""
        from compensation_analytics.ui.theme import SCROLLBAR_WIDTH
        self.assertGreaterEqual(SCROLLBAR_WIDTH, 10)


@needs_display
class TestScrollbarPlacement(unittest.TestCase):
    def test_a_hidden_scrollbar_comes_back_at_its_full_width(self):
        """Reempile apres la zone defilante, qui est en expansion,
        l'ascenseur ne recuperait aucune largeur : il revenait invisible."""
        import tkinter as tk
        from tkinter import ttk
        from compensation_analytics.ui import theme

        root = tk.Tk()
        fonts = theme.Fonts(root)
        theme.apply(root, fonts)
        parent = tk.Frame(root, width=200, height=100)
        parent.pack(fill="both", expand=True)
        canvas = tk.Canvas(parent)
        bar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview,
                            style="Flat.Vertical.TScrollbar")
        bar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        theme.attach_scrollbar(canvas, bar, side="right", fill="y",
                               before=canvas)
        root.update()
        bar.pack_forget()
        root.update()
        bar.pack(side="right", fill="y", before=canvas)
        root.update()
        self.assertGreaterEqual(bar.winfo_width(), 10)
        root.destroy()

    def test_the_placement_argument_is_mandatory(self):
        """L'oubli doit echouer a l'ecriture du code, pas a l'ecran."""
        import tkinter as tk
        from tkinter import ttk
        from compensation_analytics.ui import theme

        root = tk.Tk()
        canvas = tk.Canvas(root)
        bar = ttk.Scrollbar(root, orient="vertical")
        with self.assertRaises(ValueError):
            theme.attach_scrollbar(canvas, bar, side="right", fill="y")
        root.destroy()


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestTabOrder(unittest.TestCase):
    def test_quality_comes_last(self):
        """Les resultats d'abord : on revient au controle qualite quand un
        chiffre surprend, on ne commence pas par lui."""
        from compensation_analytics.ui.app import TABS
        self.assertEqual(TABS[-1][0], "qualite")
        self.assertEqual(TABS[0][0], "population")


@needs_display
class TestTabsFollowWhatCanBePublished(unittest.TestCase):
    """Un onglet dont le contenu est masque n'a rien a montrer.

    Les seuils ne sont pas re-evalues dans l'interface : elle lit ce que le
    moteur a decide. Ce qui garantit qu'une regle de confidentialite reste
    definie a un seul endroit.
    """

    def _analysed(self, count):
        from compensation_analytics.ui.app import Application
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, age=30 + index % 25, tenure=index % 20,
                     business_unit=["France", "DACH"][index % 2],
                     # Population mixte : sans les deux sexes, l'onglet des
                     # ecarts n'a rien a publier — et disparait a bon droit.
                     gender=["F", "H"][index % 2])
            for index in range(count)])])
        app = Application()
        app.update()
        app.result = run_analysis(AnalysisRequest(
            source_path=source, reference_date=REFERENCE_DATE,
            segments=["business_unit"]))
        app._render_results()
        app.update()
        return app

    def test_a_population_below_the_publication_threshold_keeps_only_quality(self):
        app = self._analysed(3)
        try:
            self.assertEqual(app.tabbar.visible_keys(), ["qualite"])
        finally:
            app.destroy()

    def test_charts_disappear_below_the_chart_threshold(self):
        """Entre les deux seuils, les tableaux restent publiables mais pas
        les graphiques."""
        app = self._analysed(7)
        try:
            visible = app.tabbar.visible_keys()
            self.assertIn("remuneration", visible)
            self.assertIn("population", visible)
            self.assertNotIn("distribution", visible)
            self.assertNotIn("nuage", visible)
        finally:
            app.destroy()

    def test_a_large_enough_population_keeps_every_tab(self):
        app = self._analysed(40)
        try:
            self.assertEqual(len(app.tabbar.visible_keys()), len(app.tabs))
        finally:
            app.destroy()

    def test_the_reason_is_written_out(self):
        """Retirer un onglet en silence laisserait croire a une disparition
        inexpliquee."""
        app = self._analysed(7)
        try:
            self.assertTrue(app.notice.winfo_ismapped())
            text = app.notice.cget("text")
            self.assertIn("Distribution", text)
            self.assertIn("effectif insuffisant", text)
            self.assertIn("masqué", app.status.cget("text"))
        finally:
            app.destroy()

    def test_no_notice_when_everything_is_published(self):
        app = self._analysed(40)
        try:
            self.assertFalse(app.notice.winfo_ismapped())
        finally:
            app.destroy()

    def test_the_active_tab_never_stays_hidden(self):
        """Selectionner un onglet retire laisserait une page vide."""
        app = self._analysed(3)
        try:
            self.assertIn(app.tabbar.active, app.tabbar.visible_keys())
        finally:
            app.destroy()


@needs_display
class TestResettingTheChoices(unittest.TestCase):
    """Poser un critere doit pouvoir se defaire aussi vite que se faire."""

    def setUp(self):
        from compensation_analytics.ui.app import Application
        from compensation_analytics.core.pipeline import load_population
        self.directory = tempfile.mkdtemp()
        source = os.path.join(self.directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, business_unit=["France", "DACH"][index % 2],
                     grade=["G3", "G5", "G7"][index % 3])
            for index in range(60)])])
        self.app = Application()
        self.app.update()
        population, mapping, table = load_population(
            source, self.app.configuration, reference_date=REFERENCE_DATE)
        self.app.source_path = source
        self.app.population = population
        self.app.mapping = mapping
        self.app.headers = list(table.headers)
        self.app._populate_filters()
        self.app._populate_segments()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def test_resetting_clears_every_criterion(self):
        self.app.filter_vars["business_unit"].set("France")
        self.app.filter_vars["grade"].set("G5")
        self.assertEqual(len(self.app._current_filters()), 2)
        self.app.reset_filters()
        self.assertEqual(self.app._current_filters(), [])

    def test_the_number_of_active_criteria_is_recalled(self):
        """Les filtres defilent hors du champ visible : sans rappel, un
        critere pose puis oublie fausse la lecture de toute l'analyse."""
        self.assertEqual(self.app.filter_summary.cget("text"), "")
        self.app.filter_vars["business_unit"].set("France")
        self.app.update()
        self.assertIn("1", self.app.filter_summary.cget("text"))

    def test_the_reset_link_only_shows_when_it_can_do_something(self):
        self.assertEqual(self.app.reset_filters_link.cget("text"), "")
        self.app.filter_vars["business_unit"].set("France")
        self.app.update()
        self.assertEqual(self.app.reset_filters_link.cget("text"),
                         "Réinitialiser")

    def test_toggling_axes_selects_all_then_none(self):
        self.app.toggle_segments()
        self.assertTrue(all(v.get() for v in self.app.segment_vars.values()))
        self.app.toggle_segments()
        self.assertFalse(any(v.get() for v in self.app.segment_vars.values()))

    def test_toggling_outputs_selects_none_then_all(self):
        """Les sorties sont toutes cochees au depart : la bascule decoche."""
        self.app.toggle_outputs()
        self.assertFalse(any(v.get() for v in self.app.output_vars.values()))
        self.app.toggle_outputs()
        self.assertTrue(all(v.get() for v in self.app.output_vars.values()))


@needs_display
class TestThePayGapAxis(unittest.TestCase):
    def setUp(self):
        from compensation_analytics.ui.app import Application
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, gender=["F", "H"][index % 2],
                     grade=["G3", "G5", "G7"][index % 3],
                     business_unit=["France", "DACH"][index % 2],
                     salary=40000 + (index % 7) * 1500)
            for index in range(90)])])
        self.app = Application()
        self.app.update()
        self.app.result = run_analysis(AnalysisRequest(
            source_path=source, reference_date=REFERENCE_DATE))
        self.app._render_results()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def test_the_gender_field_is_never_offered_as_an_axis(self):
        """Croiser l'ecart H/F par sexe donnerait des categories d'un seul
        sexe, toutes masquees."""
        self.assertNotIn("Sexe", self.app.category_choice.cget("values"))

    def test_changing_the_axis_changes_the_table(self):
        values = list(self.app.category_choice.cget("values"))
        self.assertIn("Grade", values)
        self.assertIn("BU", values)
        self.app.category_choice.current(values.index("Grade"))
        self.app._show_categories()
        self.app.update()
        by_grade = {self.app.category_tree.item(row)["values"][0]
                    for row in self.app.category_tree.get_children()}
        self.app.category_choice.current(values.index("BU"))
        self.app._show_categories()
        self.app.update()
        by_unit = {self.app.category_tree.item(row)["values"][0]
                   for row in self.app.category_tree.get_children()}
        self.assertTrue(by_grade & {"G3", "G5", "G7"})
        self.assertTrue(by_unit & {"France", "DACH"})
        self.assertNotEqual(by_grade, by_unit)
