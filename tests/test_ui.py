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
        self.assertEqual(TABS[0][1], "Vue d'ensemble")

    def test_population_and_pay_share_one_page(self):
        """Un salaire median ne veut rien dire sans l'age et l'anciennete de
        la population qui le porte : les separer obligeait a garder un
        chiffre en tete en changeant d'onglet."""
        from compensation_analytics.ui.app import TABS
        self.assertNotIn("remuneration", [key for key, _label in TABS])


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
            segments=[]))
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

    def test_the_reset_link_keeps_its_place_and_its_label(self):
        """Le defaut signale : l'action disparaissait sous le curseur au
        moment ou l'on cliquait, ce qui se lit comme un bouton instable."""
        from compensation_analytics.ui.theme import ACCENT, FAINT

        link = self.app.reset_filters_link
        self.assertEqual(link.cget("text"), "Réinitialiser")
        self.assertEqual(link.cget("foreground"), FAINT)
        self.assertFalse(link.enabled)

        self.app.filter_vars["business_unit"].set("France")
        self.app.update()
        self.assertEqual(link.cget("text"), "Réinitialiser")
        self.assertEqual(link.cget("foreground"), ACCENT)
        self.assertTrue(link.enabled)

        self.app.reset_filters()
        self.app.update()
        self.assertEqual(link.cget("text"), "Réinitialiser")
        self.assertEqual(link.cget("foreground"), FAINT)

    def test_an_extinguished_action_does_nothing_when_clicked(self):
        link = self.app.reset_filters_link
        self.app.filter_vars["business_unit"].set("France")
        self.app.update()
        link.event_generate("<Button-1>")
        self.app.update()
        self.assertEqual(self.app._current_filters(), [])
        # Eteinte, elle ne rappelle plus l'action.
        link.event_generate("<Button-1>")
        self.app.update()
        self.assertEqual(self.app._current_filters(), [])

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


@needs_display
class TestTheMergedOverview(unittest.TestCase):
    """Population et remuneration sur une seule page.

    Les deux se lisent ensemble : un salaire median ne veut rien dire sans
    l'age et l'anciennete de la population qui le porte.
    """

    def setUp(self):
        from compensation_analytics.ui.app import Application
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, salary=25000 + (index % 50) * 2000,
                     age=25 + index % 38, tenure=index % 32,
                     gender=["F", "H"][index % 2])
            for index in range(200)])])
        self.app = Application()
        self.app.update()
        self.app.result = run_analysis(AnalysisRequest(
            source_path=source, reference_date=REFERENCE_DATE))
        self.app._render_results()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _trees(self):
        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        return [item for item in walk(self.app.overview_frame)
                if item.winfo_class() == "Treeview"]

    def test_the_page_carries_both_subjects(self):
        titles = [item.cget("text")
                  for item in self._all_labels(self.app.overview_frame)]
        for expected in ("ÉCHELLE DE RÉMUNÉRATION", "DISPERSION",
                         "STRUCTURE D'ÂGE", "STRUCTURE D'ANCIENNETÉ"):
            self.assertIn(expected, titles)
        for expected in ("MASSE SALARIALE", "ÂGE MÉDIAN",
                         "ANCIENNETÉ MÉDIANE", "EFFECTIF"):
            self.assertIn(expected, titles)

    def test_the_indicators_are_grouped_under_their_subject(self):
        """Huit chiffres alignes se valent tous ; groupes sous leur sujet,
        ils se cherchent du regard."""
        titles = [item.cget("text")
                  for item in self._all_labels(self.app.overview_frame)]
        self.assertIn("RÉMUNÉRATION", titles)
        self.assertIn("POPULATION", titles)

    def _all_labels(self, root):
        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        return [item for item in walk(root) if item.winfo_class() == "Label"]

    def test_neither_label_nor_value_is_clipped(self):
        """Une masse salariale a huit chiffres depassait sa colonne, et
        « Ancienneté médiane » aussi : les deux sont mesures."""
        import tkinter.font as tkfont

        band = self.app.overview_frame.winfo_children()[0]
        checked = 0
        for cell in band.winfo_children():
            parts = cell.winfo_children()
            if len(parts) != 2:
                continue
            for widget in parts:
                measured = tkfont.Font(
                    root=self.app, font=widget.cget("font")).measure(
                        widget.cget("text"))
                self.assertLessEqual(measured, cell.winfo_width(),
                                     widget.cget("text"))
                checked += 1
        self.assertGreaterEqual(checked, 8)

    def test_the_pay_ladder_runs_from_minimum_to_maximum(self):
        """Minimum et maximum sont a leur place dans l'echelle, pas en
        indicateurs isoles."""
        ladder = self._trees()[0]
        labels = [ladder.item(row)["values"][0]
                  for row in ladder.get_children()]
        self.assertEqual(labels[0], "Minimum")
        self.assertEqual(labels[-1], "Maximum")

    def test_the_distributions_are_drawn_as_bars(self):
        """Un tableau donne les chiffres, une barre donne la forme — et
        c'est la forme d'une structure d'age qui se lit d'abord."""
        from compensation_analytics.ui.charts import BandChart

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        charts = [item for item in walk(self.app.overview_frame)
                  if isinstance(item, BandChart)]
        self.assertEqual(len(charts), 2)
        for chart in charts:
            self.assertTrue(chart.rows)
            self.assertIn("share", chart.rows[0])

    def test_every_tenure_band_is_present(self):
        """Le decoupage s'etend selon les carrieres presentes."""
        from compensation_analytics.ui.charts import BandChart

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        charts = [item for item in walk(self.app.overview_frame)
                  if isinstance(item, BandChart)]
        labels = [row["label"] for row in charts[-1].rows]
        self.assertGreater(len(labels), 5)
        self.assertTrue(labels[-1].startswith(">"))


@needs_display
class TestEverySegmentIsComputed(unittest.TestCase):
    """L'etape « Analyser par » a disparu.

    Choisir a l'avance les dimensions a comparer faisait doublon avec la
    liste de l'onglet Segments, qui permet d'en changer apres coup — et
    limitait cette liste a ce qui avait ete coche. Le moteur segmente
    desormais sur toutes les dimensions reellement renseignees.

    Un filtre ne remplace pas cette comparaison : filtrer sur un grade donne
    la population d'un grade, pas l'ecart entre les huit.
    """

    def setUp(self):
        from compensation_analytics.ui.app import Application
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, business_unit=["France", "DACH"][index % 2],
                     grade=["G3", "G5", "G7"][index % 3],
                     gender=["F", "H"][index % 2],
                     age=28 + index % 30, tenure=index % 15)
            for index in range(120)])])
        self.app = Application()
        self.app.update()
        self.app.result = run_analysis(AnalysisRequest(
            source_path=source, reference_date=REFERENCE_DATE, segments=[]))
        self.app._render_results()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def test_the_step_is_gone_from_the_sidebar(self):
        self.assertFalse(hasattr(self.app, "segment_vars"))
        self.assertFalse(hasattr(self.app, "segments_frame"))

    def test_every_populated_dimension_is_comparable(self):
        computed = {block["field"] for block in self.app.result.payload["segments"]}
        for expected in ("business_unit", "grade", "gender", "age_band",
                         "tenure_band"):
            self.assertIn(expected, computed)

    def test_the_segments_tab_offers_them_all(self):
        offered = list(self.app.segment_choice.cget("values"))
        self.assertEqual(len(offered),
                         len(self.app.result.payload["segments"]))
        self.assertGreater(len(offered), 3)

    def test_a_comparison_is_not_reachable_by_filtering(self):
        """La distinction qui justifie de garder la segmentation : une
        comparaison porte sur plusieurs valeurs a la fois."""
        grades = [block for block in self.app.result.payload["segments"]
                  if block["field"] == "grade"][0]
        self.assertGreater(len(grades["rows"]), 1)
        self.assertIsNotNone(grades["reference_median"])


@needs_display
class TestRecoveringFromAnEmptySelection(unittest.TestCase):
    """Un filtre qui ne laisse personne doit pouvoir se defaire.

    Le defaut : les onglets etaient masques, puis la reinitialisation ne les
    ramenait pas. Le rendu levait une erreur en remontant le bloc des
    quartiles devant un widget qu'il avait lui-meme depaquete, et
    l'exception interrompait la suite — dont le calcul des onglets a
    afficher. La fenetre restait figee sur « Analyse en cours ».
    """

    def setUp(self):
        from compensation_analytics.ui.app import Application
        from compensation_analytics.core.pipeline import load_population
        directory = tempfile.mkdtemp()
        self.source = os.path.join(directory, "population.xlsx")
        # Les grades sont lies a la BU : « France + G5 » ne designe donc
        # personne, ce qu'aucun filtre pris isolement ne ferait.
        write_workbook(self.source, [("Population", [HEADERS] + [
            make_row(index,
                     business_unit="France" if index % 2 else "DACH",
                     grade="G3" if index % 2 else "G5",
                     gender=["F", "H"][index % 2],
                     age=28 + index % 30, tenure=index % 15)
            for index in range(120)])])
        self.app = Application()
        self.app.update()
        population, mapping, table = load_population(
            self.source, self.app.configuration, reference_date=REFERENCE_DATE)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app.headers = list(table.headers)
        self.app._populate_filters()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _analyse(self):
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        from compensation_analytics.core.segmentation import build_filters
        self.app.result = run_analysis(AnalysisRequest(
            source_path=self.source, reference_date=REFERENCE_DATE,
            filters=build_filters(self.app._current_filters(),
                                  self.app.configuration)))
        self.app._render_results()
        self.app.update()

    def test_tabs_come_back_after_resetting_an_impossible_filter(self):
        self._analyse()
        complete = self.app.tabbar.visible_keys()
        self.assertGreater(len(complete), 1)

        self.app.filter_vars["business_unit"].set("France")
        self.app.filter_vars["grade"].set("G5")
        self._analyse()
        self.assertEqual(self.app.result.payload["population"]["headcount"], 0)
        self.assertEqual(self.app.tabbar.visible_keys(), ["qualite"])

        self.app.reset_filters()
        self._analyse()
        self.assertEqual(self.app.tabbar.visible_keys(), complete)

    def test_the_quartile_block_survives_being_hidden_and_shown(self):
        """Le geste exact qui levait l'erreur."""
        self._analyse()
        self.app.filter_vars["business_unit"].set("France")
        self.app.filter_vars["grade"].set("G5")
        self._analyse()
        # winfo_manager dit si le widget est empaquete, independamment de
        # l'onglet actif : winfo_ismapped repondrait « non » simplement
        # parce que la page n'est pas au premier plan.
        self.assertFalse(self.app.quartile_block.winfo_manager())
        self.app.reset_filters()
        self._analyse()
        self.assertEqual(self.app.quartile_block.winfo_manager(), "pack")

    def test_a_rendering_failure_is_reported_instead_of_freezing(self):
        """Le calcul avait abouti, seul le rendu avait echoue : la fenetre
        restait sur « Analyse en cours » sans rien dire."""
        from compensation_analytics.ui import app as module
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)

        result = run_analysis(AnalysisRequest(
            source_path=self.source, reference_date=REFERENCE_DATE))
        raised = []
        original_error = module.messagebox.showerror
        module.messagebox.showerror = lambda *a, **k: raised.append(a)
        original_render = self.app._render_results
        self.app._render_results = lambda: (_ for _ in ()).throw(
            RuntimeError("rendu casse"))
        try:
            self.app._queue.put(("resultat", result))
            self.app._set_state("Analyse en cours…")
            self.app._poll()
            self.app.update()
        finally:
            module.messagebox.showerror = original_error
            self.app._render_results = original_render
        self.assertTrue(raised, "aucun message d'erreur")
        self.assertNotIn("en cours", self.app.status.cget("text"))
