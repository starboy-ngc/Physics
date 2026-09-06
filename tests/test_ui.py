"""Tests de l'interface graphique.

Ceux qui exigent un affichage sont ignores automatiquement : le moteur doit
rester testable sur un serveur sans ecran, et une installation de Python
depourvue de tkinter doit continuer de fonctionner en ligne de commande.
"""

import ast
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
            with open(path, encoding="utf-8") as handle:
                tree = ast.parse(handle.read())
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
            with open(path, encoding="utf-8") as handle:
                source = handle.read()
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

    def _analyse(self):
        """Charge, analyse, et laisse les graphiques se tracer.

        Le trace attend la fin d'une rafale de redimensionnements : juste
        apres l'analyse, un canevas est encore vide. Un test qui n'attend pas
        mesure cette latence, pas le resultat.
        """
        import time

        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        self._load()
        self.app.result = run_analysis(AnalysisRequest(
            source_path=self.source, reference_date=REFERENCE_DATE,
            segments=[]))
        self.app._render_results()
        self.app.update()
        limite = time.time() + 2
        while time.time() < limite:
            self.app.update()
            time.sleep(0.02)
            if self.app.histogram.canvas.find_all():
                break

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
        self.assertEqual(len(self.app.tabs), 5)
        # « Graphique » en porte plusieurs : la barre principale ne dit plus
        # a elle seule tout ce que l'outil sait montrer.
        self.assertEqual(self.app.chartbar.visible_keys(),
                         ["nuage", "distribution", "boites"])

    def _settle(self, app=None):
        """Laisse le glissement aller a son terme, comme le ferait l'oeil."""
        import time

        app = app or self.app
        limite = time.time() + 5
        while app._fold_job is not None and time.time() < limite:
            app.update()
            time.sleep(0.005)
        app.update()

    def test_the_filter_column_folds_and_unfolds(self):
        """Une fois les filtres poses, la colonne peut rendre sa place a la
        lecture — mais la poignee reste, sinon replier serait un piege."""
        self.assertTrue(self.app.sidebar_card.winfo_manager())
        largeur = self.app.sidebar_card.winfo_width()

        self.app.toggle_sidebar()
        # Le chevron bascule des le clic, sans attendre la fin du mouvement.
        self.assertEqual(self.app.sidebar_arrow.cget("text"), "›")
        self.assertFalse(self.app.sidebar_open)
        self._settle()
        self.assertFalse(self.app.sidebar_card.winfo_manager())
        self.assertTrue(self.app.sidebar_handle.winfo_manager())

        self.app.toggle_sidebar()
        self._settle()
        self.assertTrue(self.app.sidebar_card.winfo_manager())
        self.assertEqual(self.app.sidebar_arrow.cget("text"), "‹")
        # Repliee puis depliee, la colonne retrouve sa place et sa largeur :
        # un widget rendu apres coup se retrouvait sinon a la fin de la pile,
        # et une animation mal fermee la laissait a une largeur approchee.
        self.assertEqual(self.app.sidebar_card.winfo_width(), largeur)
        self.assertLess(self.app.sidebar_card.winfo_rootx(),
                        self.app.sidebar_handle.winfo_rootx())

    def test_the_column_really_slides(self):
        """Sans largeurs intermediaires, il n'y a pas d'animation mais un
        basculement — c'est ce qu'il y avait avant."""
        largeurs = set()
        self.app.toggle_sidebar()
        import time

        limite = time.time() + 5
        while self.app._fold_job is not None and time.time() < limite:
            self.app.update()
            largeurs.add(self.app._fold_width)
            time.sleep(0.005)
        self.app.update()
        intermediaires = {w for w in largeurs
                          if 1 < w < self.app.SIDEBAR_WIDTH}
        self.assertGreaterEqual(len(intermediaires), 4, largeurs)

    def test_the_charts_are_emptied_during_the_slide_and_come_back(self):
        """Tk repeint le contenu d'un canevas a chaque changement de
        geometrie ; garder les deux mille points du nuage pendant le
        glissement le figeait."""
        import time

        self._analyse()
        self.app.tabbar.select("graphique")
        self.app.chartbar.select("nuage")
        limite = time.time() + 2
        while not self.app.scatter.canvas.find_all() and time.time() < limite:
            self.app.update()
            time.sleep(0.02)
        self.assertTrue(self.app.scatter.canvas.find_all())

        self.app.toggle_sidebar()
        # Vide des le premier pas, et non a la fin.
        self.assertIn(self.app.scatter, self.app._frozen)
        self.assertEqual(self.app.scatter.canvas.find_all(), ())
        # Vide, mais toujours en place : on ne depaquete rien.
        self.assertTrue(self.app.scatter.winfo_manager())
        self._settle()
        self.assertEqual(self.app._frozen, [])
        self.assertTrue(self.app.scatter.canvas.find_all())
        self.assertLess(self.app.scatter.winfo_rooty(),
                        self.app.legend_frame.winfo_rooty())

    def test_the_scrolling_container_is_never_emptied(self):
        """Le conteneur defilant d'une page est lui aussi un canevas : le
        vider supprimerait la page entiere."""
        import tkinter as tk

        self._analyse()
        self.app.tabbar.select("population")
        self.app.update()
        self.app.toggle_sidebar()
        self._settle()

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)

        # La page est toujours la, avec ses libelles.
        textes = [w.cget("text") for w in walk(self.app.overview_frame)
                  if isinstance(w, tk.Label)]
        self.assertIn("Population", textes)

    def test_a_chart_redraw_waits_for_the_resizing_to_stop(self):
        """Un trace par pixel parcouru transformait un redimensionnement en
        diaporama : seule la fin d'une rafale est honoree."""
        from compensation_analytics.ui import charts

        self._load()
        self.app.tabbar.select("graphique")
        self.app.chartbar.select("distribution")
        self.app.update()
        appels = []
        brut = charts.HistogramChart.redraw
        charts.HistogramChart.redraw = lambda self: appels.append(1) or brut(self)
        try:
            for largeur in range(900, 940, 4):
                self.app.histogram.canvas.event_generate(
                    "<Configure>", width=largeur, height=400)
            self.app.update()
            # Dix evenements, aucun trace tant que la rafale n'est pas finie.
            self.assertEqual(appels, [])
            self._wait(lambda: appels, seconds=2)
            self.assertEqual(len(appels), 1, appels)
        finally:
            charts.HistogramChart.redraw = brut

    def _wait(self, condition, seconds=2):
        import time

        limite = time.time() + seconds
        while not condition() and time.time() < limite:
            self.app.update()
            time.sleep(0.01)
        self.app.update()

    def test_toggling_mid_slide_does_not_strand_the_column(self):
        """Rebasculer en plein mouvement doit rendre un etat propre, et non
        une colonne figee a mi-largeur."""
        self.app.toggle_sidebar()
        self.app.update()
        self.app.toggle_sidebar()      # on se ravise avant la fin
        self._settle()
        self.assertTrue(self.app.sidebar_open)
        self.assertTrue(self.app.sidebar_card.winfo_manager())
        self.assertEqual(self.app._fold_width, self.app.SIDEBAR_WIDTH)

    def test_the_filters_survive_folding(self):
        """Replier masque, ne remet a zero ni ne relance quoi que ce soit."""
        self._load()
        champ = next(iter(self.app.filter_vars))
        self.app.filter_vars[champ].set("France")
        self.app.toggle_sidebar()
        self._settle()
        self.app.toggle_sidebar()
        self._settle()
        self.assertEqual(self.app.filter_vars[champ].get(), "France")

    def test_the_page_is_composed_reordered_and_emptied(self):
        """« Ma page » n'impose rien : elle empile ce qu'on lui donne, dans
        l'ordre ou on le donne."""
        self.assertEqual(self.app._workshop_blocks, [])
        for ident in ("headcount", "median", "age_pyramid"):
            self.app.add_block(ident)
        self.app.update()
        self.assertEqual([b["block"] for b in self.app._workshop_blocks],
                         ["headcount", "median", "age_pyramid"])

        self.app.move_block(2, -1)
        self.assertEqual([b["block"] for b in self.app._workshop_blocks],
                         ["headcount", "age_pyramid", "median"])
        # Un deplacement hors des bornes ne fait rien plutot que de lever.
        self.app.move_block(0, -1)
        self.app.move_block(2, 1)
        self.assertEqual(len(self.app._workshop_blocks), 3)

        self.app.remove_block(1)
        self.assertEqual([b["block"] for b in self.app._workshop_blocks],
                         ["headcount", "median"])
        self.app.clear_workshop()
        self.assertEqual(self.app._workshop_blocks, [])

    def test_an_unknown_block_is_refused(self):
        """Le catalogue fait foi : rien d'autre n'entre dans la page."""
        self.app.add_block("bloc_qui_n_existe_pas")
        self.assertEqual(self.app._workshop_blocks, [])

    def test_the_composed_page_is_saved_and_found_again(self):
        """C'est la promesse du bouton : la page survit a la fermeture."""
        import shutil
        import tempfile

        from compensation_analytics.core.config import load_configuration
        from compensation_analytics.ui import dashboard
        from compensation_analytics.ui.app import Application

        directory = tempfile.mkdtemp()
        config_dir = os.path.join(directory, "config")
        shutil.copytree(os.path.join(ROOT, "config"), config_dir)
        app = Application(config_dir=config_dir)
        app.update()
        try:
            for ident in ("payroll", "boxes", "histogram"):
                app.add_block(ident)
            app._workshop_blocks[1]["field"] = "grade"
            app.save_workshop()
            app.update()
            self.assertIn("enregistrée", app.workshop_state.cget("text"))
        finally:
            app.destroy()

        # Relue depuis le disque : identifiants et ordre, rien d'autre.
        saved = dashboard.load(load_configuration(config_dir))
        self.assertEqual([entry["block"] for entry in saved],
                         ["payroll", "boxes", "histogram"])
        self.assertEqual(saved[1]["field"], "grade")

        repris = Application(config_dir=config_dir)
        try:
            repris.update()
            self.assertEqual([b["block"] for b in repris._workshop_blocks],
                             ["payroll", "boxes", "histogram"])
        finally:
            repris.destroy()

    def test_a_saved_page_survives_a_block_that_no_longer_exists(self):
        """Une configuration se modifie au bloc-notes et survit aux versions :
        un identifiant inconnu ampute la page, il ne l'empeche pas."""
        from compensation_analytics.ui import dashboard

        class FausseConfig:
            def get(self, path, default=None):
                return [{"block": "headcount"}, {"block": "disparu"},
                        {"block": "median"}, "pas un bloc"]

        gardes = dashboard.load(FausseConfig())
        self.assertEqual([entry["block"] for entry in gardes],
                         ["headcount", "median"])

    def test_the_saved_page_never_carries_figures(self):
        """Ce qui part en configuration se reduit a des identifiants, un
        ordre et des tailles : jamais un chiffre, jamais une donnee RH. La
        largeur y est en colonnes et non en pixels, faute de quoi une page
        composee sur un grand ecran s'ouvrirait de travers sur un petit."""
        from compensation_analytics.ui import dashboard

        section = dashboard.dump([{"block": "median", "field": "", "span": 3},
                                  {"block": "boxes", "field": "grade"},
                                  {"block": "inconnu", "field": ""}])
        self.assertEqual(section["blocks"][0],
                         {"block": "median", "span": 3,
                          "height": dashboard.DEFAULT_HEIGHT["indicator"]})
        self.assertEqual(section["blocks"][1]["block"], "boxes")
        self.assertEqual(section["blocks"][1]["field"], "grade")
        self.assertEqual(len(section["blocks"]), 2)
        for entry in section["blocks"]:
            self.assertLessEqual(entry["span"], dashboard.COLUMNS)
            self.assertIn(entry["span"],
                          [size for size, _label in dashboard.SIZES])

    def test_the_screen_names_the_employee_behind_a_point(self):
        """Un point a trente pour cent sous la mediane ne veut rien dire
        tant qu'on ne sait pas de qui il s'agit : c'est le geste meme de
        l'analyse. Le paragraphe 6 exige des identifiants *anonymisables*,
        pas anonymises."""
        self._analyse()
        self.assertTrue(self.app._identities)
        point = self.app.result.payload["scatter"]["points"][0]
        self.assertEqual(self.app.scatter._label_of(point),
                         self.app._identities[point["row"]])
        self.assertTrue(self.app.scatter._label_of(point).startswith("NOM"))

        self.app._on_point_selected(point)
        self.assertIn("NOM", self.app.selection_label.cget("text"))

    def test_the_identity_is_rebuilt_on_screen_and_never_carried(self):
        """L'ecran reconstruit l'identite depuis le fichier qu'il detient.

        Si elle voyageait dans le jeu de donnees du graphique, elle entrerait
        par construction dans tout ce qui en derive.
        """
        self._analyse()
        for point in self.app.result.payload["scatter"]["points"]:
            self.assertNotIn("name", point)
            self.assertNotIn("identity", point)

    def test_unticking_the_setting_brings_back_the_anonymous_reference(self):
        """Le reglage doit se voir immediatement, sans relancer l'analyse."""
        self._analyse()
        point = self.app.result.payload["scatter"]["points"][0]
        self.assertTrue(self.app.scatter._label_of(point).startswith("NOM"))

        data = self.app.configuration.as_dict()
        data["privacy_parameters"]["show_identities_on_screen"] = False
        from compensation_analytics.core.config import Configuration
        self.app.configuration = Configuration(data)
        self.app._index_identities()

        self.assertEqual(self.app._identities, {})
        self.assertEqual(self.app.scatter._label_of(point), point["reference"])
        self.assertFalse(self.app.scatter._label_of(point).startswith("NOM"))

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


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestTheIndicatorTablesAreBuiltOnce(unittest.TestCase):
    """Deux ecrans montrent l'echelle et la dispersion : un seul code les
    construit. Ecrites en double, elles se seraient ecartees — retirer un
    percentile de la configuration n'aurait tenu qu'a l'un des deux, et le
    meme fichier aurait porte deux echelles selon l'onglet ouvert."""

    def setUp(self):
        from compensation_analytics.ui import app
        self.app_module = app
        self.salary = {
            "min": 30000.0, "max": 90000.0, "p25": 42000.0, "median": 50000.0,
            "p75": 61000.0,
            "published_percentiles": [{"key": "p25", "label": "Q1 (P25)"},
                                      {"key": "median",
                                       "label": "Médiane (P50)"},
                                      {"key": "p75", "label": "Q3 (P75)"}],
            "dispersion": {"interquartile_range": 19000.0,
                           "q3_over_q1": 1.452, "p90_over_p10": 2.03,
                           "mean_over_median": 1.04,
                           "coefficient_of_variation": 0.2718},
        }

    def test_the_scale_follows_the_published_percentiles(self):
        rows = self.app_module.salary_scale_rows(self.salary, "EUR")
        self.assertEqual([label for label, _v, _k in rows],
                         ["Minimum", "Q1 (P25)", "Médiane (P50)", "Q3 (P75)",
                          "Maximum"])
        self.assertEqual(rows[0][2], "min")
        self.assertIn("30", rows[0][1])

        restreint = dict(self.salary, published_percentiles=[
            {"key": "median", "label": "Médiane (P50)"}])
        self.assertEqual(
            [label for label, _v, _k in
             self.app_module.salary_scale_rows(restreint, "EUR")],
            ["Minimum", "Médiane (P50)", "Maximum"])

    def test_each_dispersion_indicator_keeps_its_own_formatting(self):
        rows = self.app_module.dispersion_rows(self.salary["dispersion"],
                                               "EUR")
        valeurs = {key: value for _label, value, key in rows}
        self.assertIn("EUR", valeurs["interquartile_range"])
        self.assertEqual(valeurs["q3_over_q1"], "1,45")
        self.assertIn("%", valeurs["coefficient_of_variation"])
        self.assertEqual([key for _l, _v, key in rows],
                         ["interquartile_range", "q3_over_q1", "p90_over_p10",
                          "mean_over_median", "coefficient_of_variation"])

    def test_an_absent_indicator_does_not_break_the_table(self):
        rows = self.app_module.dispersion_rows({}, "EUR")
        self.assertEqual(len(rows), 5)
        self.assertEqual(len(self.app_module.salary_scale_rows({}, "EUR")), 2)


@needs_display
class TestTheScreenPrivacySetting(unittest.TestCase):
    """La case « Afficher les noms » n'engage que l'ecran."""

    def setUp(self):
        import shutil
        from compensation_analytics.ui.app import Application
        self.directory = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.directory, "config")
        shutil.copytree(os.path.join(ROOT, "config"), self.config_dir)
        self.app = Application(config_dir=self.config_dir)
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _window(self):
        from compensation_analytics.ui.settings import SettingsWindow
        window = SettingsWindow(self.app, self.app.configuration,
                                self.config_dir, self.app.fonts,
                                headers=list(HEADERS))
        self.app.update()
        return window

    def test_saving_keeps_the_other_privacy_settings(self):
        """La section est reecrite entiere : les seuils d'effectif qui la
        partagent doivent survivre a l'enregistrement du reglage d'ecran.
        Les perdre remettrait la confidentialite a ses valeurs par defaut
        sans que personne ne l'ait demande."""
        import json

        window = self._window()
        try:
            self.assertTrue(window.identities_var.get())
            window.identities_var.set(False)
            window.save()
        finally:
            if window.winfo_exists():
                window.destroy()
        self.app.update()

        path = os.path.join(self.config_dir, "privacy_parameters.json")
        with open(path, encoding="utf-8") as handle:
            section = json.load(handle)
        self.assertIs(section["show_identities_on_screen"], False)
        self.assertEqual(section["min_headcount_publish"], 5)
        self.assertEqual(section["min_headcount_chart"], 10)
        self.assertIs(section["anonymise_identifiers"], True)


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestTheLayoutOfTheComposedPage(unittest.TestCase):
    """La disposition se calcule sans ecran : c'est de l'arithmetique sur
    une grille en douziemes, et c'est la qu'elle doit etre verifiee."""

    def setUp(self):
        from compensation_analytics.ui import dashboard
        self.dashboard = dashboard

    def _page(self, *spans):
        return [self.dashboard.normalise({"block": "median", "span": span})
                for span in spans]

    def test_blocks_fill_a_row_before_starting_the_next(self):
        """Quatre quarts tiennent sur une ligne ; le cinquieme passe a la
        ligne suivante. Sans cela la page se lirait en colonne unique."""
        boxes = self.dashboard.flow(self._page(3, 3, 3, 3, 3), 1000)
        premiers = boxes[:4]
        self.assertEqual(len({round(box["y"]) for box in premiers}), 1)
        self.assertGreater(boxes[4]["y"], premiers[0]["y"])
        for gauche, droite in zip(premiers, premiers[1:]):
            self.assertGreater(droite["x"], gauche["x"])

    def test_no_block_overflows_the_page(self):
        """Le debordement a droite est invisible tant qu'on ne mesure pas :
        la derniere colonne doit tomber juste sur le bord."""
        for width in (600, 900, 1440):
            boxes = self.dashboard.flow(self._page(6, 6, 12, 4, 4, 4), width)
            for box in boxes:
                self.assertGreaterEqual(box["x"], -0.01)
                self.assertLessEqual(box["x"] + box["width"], width + 0.01)
            pleine = boxes[2]
            self.assertAlmostEqual(pleine["width"], width, places=6)

    def test_the_page_is_as_tall_as_its_tallest_row(self):
        """Une ligne vaut son bloc le plus haut : c'est ce qui evite qu'un
        graphique chevauche la ligne suivante."""
        page = self._page(6, 6, 12)
        page[0]["height"] = 300
        page[1]["height"] = 120
        page[2]["height"] = 200
        boxes = self.dashboard.flow(page, 1000)
        self.assertEqual(boxes[0]["y"], boxes[1]["y"])
        self.assertGreaterEqual(boxes[2]["y"], 300)
        self.assertGreaterEqual(self.dashboard.page_height(boxes), 500)
        self.assertEqual(self.dashboard.page_height([]), 0.0)

    def test_a_width_always_lands_on_a_step(self):
        """Cinq douziemes et sept douziemes ne s'alignent avec rien : la
        largeur tiree a la souris se pose sur un palier."""
        paliers = [size for size, _label in self.dashboard.SIZES]
        for wanted in (-3, 0.4, 2.6, 5, 7, 9.9, 40):
            self.assertIn(self.dashboard.snap_span(wanted), paliers)
        self.assertEqual(self.dashboard.snap_span(3.4), 3)
        self.assertEqual(self.dashboard.snap_span(5), 4)
        self.assertEqual(self.dashboard.snap_span(11), 12)

    def test_a_height_stays_between_the_two_bounds(self):
        """En dessous du plancher l'en-tete devient illisible ; au dessus du
        plafond le bloc ne tient plus dans une page."""
        clamp = self.dashboard.clamp_height
        self.assertEqual(clamp(-200), self.dashboard.MIN_HEIGHT)
        self.assertEqual(clamp(10 ** 6), self.dashboard.MAX_HEIGHT)
        self.assertEqual(clamp(211.7), 211)

    def test_a_size_taken_by_hand_survives_the_round_trip(self):
        """Ce que l'on regle a la souris doit se retrouver a la reouverture :
        c'est toute la promesse de la page composee."""
        compose = [{"block": "boxes", "field": "grade", "span": 6,
                    "height": 340},
                   {"block": "median", "span": 3, "height": 92}]
        section = self.dashboard.dump(compose)

        class Config:
            def get(self, path, default=None):
                return section["blocks"]

        relu = self.dashboard.load(Config())
        self.assertEqual([(e["block"], e["span"], e["height"], e["field"])
                          for e in relu],
                         [("boxes", 6, 340, "grade"), ("median", 3, 92, "")])

    def test_a_size_written_by_hand_out_of_range_is_brought_back(self):
        """Une configuration se modifie au bloc-notes : une hauteur absurde
        ou une largeur hors palier ne doit pas casser la page."""
        entry = self.dashboard.normalise({"block": "median", "span": 5,
                                          "height": 4000})
        self.assertEqual(entry["span"], self.dashboard.COLUMNS)
        self.assertEqual(entry["height"],
                         self.dashboard.DEFAULT_HEIGHT["indicator"])


@needs_display
class TestTheBoardMovesAndResizes(unittest.TestCase):
    """Le plan de travail est la seule piece qui ait besoin d'un ecran :
    on y verifie qu'un deplacement reordonne, et qu'une taille se propage."""

    def setUp(self):
        from compensation_analytics.ui import dashboard, theme
        self.dashboard = dashboard
        self.root = tkinter.Tk()
        self.root.geometry("1000x700")
        self.built = []
        self.changes = []
        self.board = dashboard.Board(
            self.root, theme.Fonts(self.root),
            build=lambda content, entry, position, width:
                self.built.append((entry["block"], width)),
            on_change=lambda: self.changes.append(True))
        self.board.pack(fill="both", expand=True)
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def _compose(self, *idents):
        self.board.set_blocks([{"block": ident} for ident in idents])
        self.root.update()

    def _order(self):
        return [entry["block"] for entry in self.board.blocks]

    def test_moving_a_block_reorders_the_page(self):
        self._compose("headcount", "median", "payroll")
        self.board.move(2, 0)
        self.assertEqual(self._order(), ["payroll", "headcount", "median"])
        self.board.move(0, 3)
        self.assertEqual(self._order(), ["headcount", "median", "payroll"])
        self.assertEqual(len(self.changes), 2)

    def test_moving_a_block_that_is_not_there_changes_nothing(self):
        """Un relachement hors de la page ne doit rien deranger."""
        self._compose("headcount", "median")
        self.board.move(7, 0)
        self.assertEqual(self._order(), ["headcount", "median"])
        self.assertEqual(self.changes, [])

    def test_a_resized_block_is_rebuilt_at_its_new_width(self):
        """Un indicateur choisit la chasse de son chiffre d'apres la largeur
        recue : sans remontage, un quart passe en pleine largeur garderait
        le corps du quart, et le chiffre resterait minuscule."""
        self._compose("median")
        self.board.blocks[0]["span"] = 3
        self.board._rebuild()
        self.root.update()
        etroit = self.built[-1][1]

        self.board.blocks[0]["span"] = 12
        self.board._sizing = 0
        self.board._release_size()
        self.root.update()
        large = self.built[-1][1]
        self.assertGreater(large, etroit * 2)
        self.assertEqual(self.changes, [True])

    def test_the_page_is_exactly_as_tall_as_its_blocks(self):
        """La hauteur du plan de travail commande la barre de defilement :
        trop courte, le dernier bloc devient inatteignable."""
        self._compose("scatter", "boxes")
        self.root.update()
        attendu = self.dashboard.page_height(self.board.boxes, self.board.GAP)
        self.assertEqual(self.board.winfo_reqheight(), int(attendu))

    def test_removing_and_clearing_leave_the_page_consistent(self):
        self._compose("headcount", "median", "payroll")
        self.board.remove(1)
        self.assertEqual(self._order(), ["headcount", "payroll"])
        self.assertEqual(len(self.board.holders), 2)
        self.board.add("min")
        self.assertEqual(self._order(), ["headcount", "payroll", "min"])
        self.board.add("bloc_inexistant")
        self.assertEqual(len(self.board.blocks), 3)
        self.board.clear()
        self.assertEqual(self.board.holders, [])


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

    def _analysed(self, count, **row_options):
        from compensation_analytics.ui.app import Application
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        # Conserve : un test qui rejoue l'analyse avec un filtre en a besoin.
        source = self.source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, age=30 + index % 25, tenure=index % 20,
                     business_unit=["France", "DACH"][index % 2],
                     # Population mixte : sans les deux sexes, l'onglet des
                     # ecarts n'a rien a publier — et disparait a bon droit.
                     gender=["F", "H"][index % 2], **row_options)
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
            # Aucun des deux graphiques n'est publiable : l'onglet tombe.
            self.assertNotIn("graphique", visible)
            self.assertEqual(app.chartbar.visible_keys(), [])
        finally:
            app.destroy()

    def test_one_chart_can_go_while_the_tab_stays(self):
        """Sans date d'entree, le nuage n'a aucun point — mais l'histogramme
        des remunerations, lui, reste parfaitement publiable."""
        app = self._analysed(40, hire_date="")
        try:
            self.assertIn("graphique", app.tabbar.visible_keys())
            self.assertEqual(app.chartbar.visible_keys(),
                             ["distribution", "boites"])   # le nuage est parti
            # Le graphique retire s'explique, comme un onglet retire.
            self.assertIn("Ancienneté", app.notice.cget("text"))
            self.assertTrue(app.notice.winfo_ismapped())
        finally:
            app.destroy()

    def test_a_large_enough_population_keeps_every_tab(self):
        app = self._analysed(40)
        try:
            self.assertEqual(len(app.tabbar.visible_keys()), len(app.tabs))
        finally:
            app.destroy()

    def test_a_box_needs_more_people_than_a_table_row(self):
        """Tracer une dispersion en demande plus que la publier.

        Une boite dessine P10 et P90 : sur un segment de cinq salaries, ce
        sont deux remunerations individuelles pointees a l'ecran. Le segment
        garde donc sa ligne de tableau, mais pas sa boite.
        """
        from compensation_analytics.core.metrics import PrivacyRules
        app = self._analysed(40)
        try:
            rules = PrivacyRules.from_config(app.result.config)
            rows = [row for block in app.result.payload["segments"]
                    for row in block["rows"]]
            petits = [row for row in rows
                      if not row["masked"] and row["headcount"] < rules.min_chart]
            self.assertTrue(petits, "aucun segment entre les deux seuils")
            for row in petits:
                with self.subTest(segment=row["segment"]):
                    # Publiable — il a sa ligne — mais pas tracable.
                    self.assertFalse(row["chartable"])
            self.assertTrue(any(row["chartable"] for row in rows))
        finally:
            app.destroy()

    def _canvas_texts(self, chart):
        """Textes des deux canevas : les lignes defilent, le pied ne bouge
        pas, mais tout est du meme graphique."""
        textes = []
        for canvas in (chart.canvas, getattr(chart, "footer", None)):
            if canvas is None:
                continue
            textes += [canvas.itemcget(item, "text")
                       for item in canvas.find_all()
                       if canvas.type(item) == "text"]
        return textes

    def test_the_boxes_carry_their_reading_key(self):
        """Une boite a moustaches ne se devine pas : sans cle de lecture, le
        graphique le plus utile de l'outil reste le plus opaque."""
        from compensation_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            chart.pack(fill="both", expand=True)
            chart.configure(width=900, height=420)
            app.update()
            block = app.result.payload["segments"][0]
            chart.set_rows(block["rows"], "EUR",
                           reference=block.get("reference_median"))
            chart.redraw()
            app.update()
            textes = self._canvas_texts(chart)
            for part in ("P10", "Q1", "Médiane", "Q3", "P90"):
                self.assertIn(part, textes)
            phrase = [x for x in textes if "moitié des salariés" in x]
            self.assertEqual(len(phrase), 1, textes)
            self.assertIn("10e au 90e centile", phrase[0])
        finally:
            app.destroy()

    def test_the_boxes_show_the_overall_median_and_the_headcounts(self):
        """Un repere dessine se lit mieux qu'un montant a comparer de tete, et
        une boite tracee sur douze salaries a la meme allure que sur quatre
        cents."""
        from compensation_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            chart.pack(fill="both", expand=True)
            chart.configure(width=900, height=420)
            app.update()
            block = app.result.payload["segments"][0]
            reference = block.get("reference_median")
            self.assertIsNotNone(reference)
            chart.set_rows(block["rows"], "EUR", reference=reference)
            chart.redraw()
            app.update()
            textes = self._canvas_texts(chart)
            self.assertTrue([x for x in textes if "Médiane d'ensemble" in x])
            # Le repere doit tomber dans l'echelle, sinon il se tracerait au
            # bord du cadre en mentant sur sa position.
            low, high = chart._span(chart._drawable())
            self.assertLessEqual(low, reference)
            self.assertLessEqual(reference, high)
            for row in chart._drawable():
                self.assertIn(str(row["headcount"]), textes)
        finally:
            app.destroy()

    def test_the_key_says_when_segments_are_withheld(self):
        """Un segment publiable mais trop peu nombreux pour etre trace ne doit
        pas disparaitre en silence."""
        from compensation_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            chart.pack(fill="both", expand=True)
            chart.configure(width=900, height=420)
            app.update()
            block = app.result.payload["segments"][0]
            rows = [dict(row) for row in block["rows"]]
            traçables = [row for row in rows if row.get("chartable")]
            self.assertTrue(traçables)
            traçables[-1]["chartable"] = False       # publiable, pas tracable
            chart.set_rows(rows, "EUR")
            chart.redraw()
            app.update()
            phrase = [x for x in self._canvas_texts(chart)
                      if "trop peu nombreux" in x]
            self.assertEqual(len(phrase), 1)
            self.assertIn("1 segment", phrase[0])
        finally:
            app.destroy()

    def _fake_rows(self, count):
        return [{"segment": f"Poste {index:02}", "headcount": 40 + index,
                 "masked": False, "chartable": True,
                 "salary": {"p10": 20000 + index * 300,
                            "p25": 25000 + index * 300,
                            "median": 30000 + index * 300,
                            "p75": 36000 + index * 300,
                            "p90": 44000 + index * 300}}
                for index in range(count)]

    def test_every_segment_is_drawn_and_the_page_scrolls(self):
        """Ecarter des segments faute de place revenait a cacher une partie
        de la reponse : ils sont tous traces, et la page defile."""
        from compensation_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            chart.pack(fill="both", expand=True)
            chart.configure(width=900, height=380)
            app.update()

            def boites():
                return sum(1 for item in chart.canvas.find_all()
                           if chart.canvas.type(item) == "rectangle")

            def hauteur_zone():
                region = chart.canvas.cget("scrollregion").split()
                return float(region[3]) if len(region) == 4 else 0.0

            chart.set_rows(self._fake_rows(6), "EUR")
            chart.redraw()
            app.update()
            self.assertEqual(boites(), 6)
            # Ce qui tient ne fait pas defiler : pas d'ascenseur inutile.
            self.assertFalse(chart.bar.winfo_manager())

            chart.set_rows(self._fake_rows(40), "EUR")
            chart.redraw()
            app.update()
            self.assertEqual(boites(), 40)
            self.assertGreater(hauteur_zone(), chart.canvas.winfo_height())
            self.assertTrue(chart.bar.winfo_manager())
        finally:
            app.destroy()

    def test_the_axis_stays_put_while_the_boxes_scroll(self):
        """Une boite sans graduation ne dit plus rien : l'axe et la cle sont
        hors de la zone qui defile."""
        from compensation_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            chart.pack(fill="both", expand=True)
            chart.configure(width=900, height=380)
            app.update()
            chart.set_rows(self._fake_rows(40), "EUR")
            chart.redraw()
            app.update()
            pied = [chart.footer.itemcget(item, "text")
                    for item in chart.footer.find_all()
                    if chart.footer.type(item) == "text"]
            self.assertIn("Médiane", pied)
            self.assertTrue([x for x in pied if "EUR" in x])
            # Rien de tout cela ne bouge quand on descend.
            avant = chart.footer.bbox("all")
            chart.canvas.yview_moveto(1.0)
            app.update()
            self.assertEqual(chart.footer.bbox("all"), avant)
        finally:
            app.destroy()

    def test_the_boxes_can_be_sorted_without_recomputing(self):
        """Trier repond a une autre question avec les memes chiffres."""
        from compensation_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            rows = self._fake_rows(5)
            chart.set_rows(rows, "EUR")
            ordre = [row["segment"] for row in chart._drawable()]
            self.assertEqual(ordre, [row["segment"] for row in rows])

            chart.set_order("median")
            medianes = [row["salary"]["median"] for row in chart._drawable()]
            self.assertEqual(medianes, sorted(medianes, reverse=True))

            chart.set_order("headcount")
            effectifs = [row["headcount"] for row in chart._drawable()]
            self.assertEqual(effectifs, sorted(effectifs, reverse=True))

            # Un tri inconnu retombe sur l'ordre du moteur plutot que de lever.
            chart.set_order("n'importe quoi")
            self.assertEqual([row["segment"] for row in chart._drawable()],
                             ordre)
        finally:
            app.destroy()

    def test_a_box_is_never_drawn_without_the_engine_flag(self):
        """Le refus est l'etat par defaut : une ligne arrivee sans drapeau
        n'est pas dessinee « au cas ou »."""
        from compensation_analytics.ui.charts import BoxPlotChart
        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            complete = {"segment": "X", "headcount": 99, "masked": False,
                        "salary": {"p10": 1.0, "p25": 2.0, "median": 3.0,
                                   "p75": 4.0, "p90": 5.0}}
            chart.set_rows([complete])
            self.assertEqual(chart._drawable(), [])
            chart.set_rows([dict(complete, chartable=True)])
            self.assertEqual(len(chart._drawable()), 1)
        finally:
            app.destroy()

    def test_the_directive_charts_only_draw_what_the_engine_published(self):
        """Un ecart ou une part que le moteur a refuse de publier ne doit pas
        reapparaitre sous forme de barre."""
        from compensation_analytics.ui.charts import GapChart, QuartileChart
        app = self._analysed(40)
        try:
            gaps = GapChart(app)
            gaps.set_rows([
                {"category": "publie", "published": True, "mean_gap": 3.0},
                {"category": "sous le seuil", "published": False,
                 "mean_gap": 12.0},
                # Publie, mais l'ecart n'a pas pu etre calcule.
                {"category": "sans ecart", "published": True, "mean_gap": None},
            ])
            self.assertEqual([row["category"] for row in gaps._drawable()],
                             ["publie"])
            quartiles = QuartileChart(app)
            quartiles.set_rows([
                {"quartile": 1, "female_share": 60.0, "male_share": 40.0},
                {"quartile": 2, "female_share": None, "male_share": None},
            ])
            self.assertEqual([row["quartile"] for row in quartiles._drawable()],
                             [1])
        finally:
            app.destroy()

    def test_the_status_line_says_what_was_filtered(self):
        """Le perimetre gouverne tous les onglets : il se lit dans la barre
        d'etat, visible quel que soit l'onglet ouvert, et non en tete d'une
        seule page."""
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        from compensation_analytics.core.segmentation import build_filters
        app = self._analysed(40)
        try:
            # Sans filtre, aucun critere dans la barre : ce serait du bruit.
            self.assertIn("40 salariés", app.status.cget("text"))
            self.assertNotIn("BU = ", app.status.cget("text"))

            app.result = run_analysis(AnalysisRequest(
                source_path=self.source, reference_date=REFERENCE_DATE,
                segments=[],
                filters=build_filters([{"field": "business_unit",
                                        "operator": "eq",
                                        "value": "France"}],
                                      app.configuration)))
            app._render_results()
            app.update()
            state = app.status.cget("text")
            self.assertIn("BU = France", state)
            self.assertIn("20 salariés", state)
            # Et nulle part ailleurs : le perimetre a quitte la page.
            import tkinter as tk

            def walk(widget):
                yield widget
                for child in widget.winfo_children():
                    yield from walk(child)

            texts = [item.cget("text") for item in walk(app.overview_frame)
                     if isinstance(item, tk.Label)]
            self.assertFalse([text for text in texts if "BU = " in text])
        finally:
            app.destroy()

    def test_a_small_population_is_flagged_on_screen(self):
        """Le moteur demande de la prudence : l'ecran le disait moins que le
        rapport, il le dit maintenant aussi."""
        import tkinter as tk

        app = self._analysed(8)
        try:
            def walk(widget):
                yield widget
                for child in widget.winfo_children():
                    yield from walk(child)

            warning = app.result.payload["salary"]["warning"]
            self.assertTrue(warning, "le moteur devrait avertir a 8 salaries")
            shown = [item.cget("text") for item in walk(app.overview_frame)
                     if isinstance(item, tk.Label)]
            self.assertIn(warning, shown)
        finally:
            app.destroy()

    def test_the_reason_is_written_out(self):
        """Retirer un onglet en silence laisserait croire a une disparition
        inexpliquee."""
        app = self._analysed(7)
        try:
            self.assertTrue(app.notice.winfo_ismapped())
            text = app.notice.cget("text")
            self.assertIn("Graphique", text)
            self.assertIn("effectif insuffisant", text)
            self.assertIn("masquée", app.status.cget("text"))
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
        # Les intertitres sont en casse normale : les petites majuscules
        # sont descendues d'un rang, aux en-tetes de colonne.
        for expected in ("Échelle de rémunération", "Dispersion",
                         "Pyramide des âges", "Structure d'ancienneté"):
            self.assertIn(expected, titles)
        # Les indicateurs ne coiffent plus la page : ils sont en tete de leur
        # colonne, sous la meme forme que les tableaux qui suivent.
        for expected in ("Masse salariale", "Âge médian",
                         "Ancienneté médiane", "Effectif"):
            self.assertIn(expected, titles)

    def test_the_indicators_are_grouped_under_their_subject(self):
        """Huit chiffres alignes se valent tous ; groupes sous leur sujet,
        ils se cherchent du regard."""
        titles = [item.cget("text")
                  for item in self._all_labels(self.app.overview_frame)]
        self.assertIn("Rémunération", titles)
        self.assertIn("Population", titles)

    def _all_labels(self, root):
        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        return [item for item in walk(root) if item.winfo_class() == "Label"]

    def test_no_figure_is_shown_twice(self):
        """Aucun chiffre ne doit figurer deux fois sur la page.

        La mediane s'affichait en indicateur et, trois centimetres plus bas,
        en ligne de l'echelle ; les moyennes d'age et d'anciennete etaient
        partagees entre un bandeau et les en-tetes des pyramides. Ce test
        empeche la redondance de revenir.
        """
        texts = [item.cget("text")
                 for item in self._all_labels(self.app.overview_frame)]
        # C'est le libelle qui identifie une information, pas sa valeur :
        # « Âge médian » et « Âge moyen » peuvent tomber sur le meme nombre
        # sans que rien ne soit redondant. En revanche un meme libelle a deux
        # endroits, c'est la meme information affichee deux fois.
        entetes = {"INDICATEUR", "VALEUR", "PERCENTILE", "FEMMES", "HOMMES"}
        libelles = [text for text in texts
                    if text.upper() not in entetes
                    and not any(char.isdigit() for char in text)
                    and text.strip()]
        doublons = {name for name in libelles if libelles.count(name) > 1}
        self.assertEqual(doublons, set(), "information affichée deux fois")
        self.assertGreaterEqual(len(libelles), 15)

    def test_a_section_title_outranks_what_it_introduces(self):
        """Il partageait la chasse et la teinte des en-tetes de colonne, et
        se lisait moins bien que ses propres lignes."""
        import tkinter.font as tkfont

        from compensation_analytics.core import palette

        def taille(widget):
            return tkfont.Font(root=self.app,
                               font=widget.cget("font")).cget("size")

        labels = self._all_labels(self.app.overview_frame)
        titre = next(w for w in labels if w.cget("text") == "Dispersion")
        entete = next(w for w in labels if w.cget("text") == "INDICATEUR")
        ligne = next(w for w in labels if w.cget("text") == "Q3 / Q1")
        self.assertGreater(taille(titre), taille(ligne))
        self.assertGreater(taille(titre), taille(entete))
        blanc = palette.by_name("ardoise").canvas
        contraste = lambda w: palette.contrast(w.cget("foreground"), blanc)
        self.assertGreater(contraste(titre), contraste(ligne))
        self.assertGreater(contraste(titre), contraste(entete))
        # L'en-tete de colonne reste lisible : sous 3:1 il se devinait.
        self.assertGreater(contraste(entete), 3.0)

    def test_the_analysed_field_is_named(self):
        """Le meme ecran veut dire deux choses selon le champ analyse."""
        texts = [item.cget("text")
                 for item in self._all_labels(self.app.overview_frame)]
        field = self.app.result.payload["salary"]["field_label"]
        self.assertIn(f"Champ analysé : {field}", texts)

    def test_the_population_figures_sit_in_one_place(self):
        """Mediane et moyenne d'age se lisent l'une sous l'autre, et non de
        part et d'autre de la page."""
        texts = [item.cget("text")
                 for item in self._all_labels(self.app.overview_frame)]
        for expected in ("Âge médian", "Âge moyen", "Ancienneté médiane",
                         "Ancienneté moyenne"):
            self.assertIn(expected, texts)
        self.assertLess(texts.index("Âge moyen"),
                        texts.index("Pyramide des âges"))

    def test_the_pay_ladder_runs_from_minimum_to_maximum(self):
        """Minimum et maximum sont a leur place dans l'echelle, pas en
        indicateurs isoles."""
        texts = [item.cget("text")
                 for item in self._all_labels(self.app.overview_frame)]
        self.assertIn("Minimum", texts)
        self.assertIn("Maximum", texts)
        self.assertLess(texts.index("Minimum"), texts.index("Maximum"))

    def test_the_median_row_is_set_apart(self):
        """La ligne que l'on cherche en premier est mise en avant, plutot
        que signalee par une couleur de fond."""
        import tkinter.font as tkfont
        from compensation_analytics.ui.theme import INK

        for item in self._all_labels(self.app.overview_frame):
            if item.cget("text") == "Médiane (P50)":
                self.assertEqual(item.cget("foreground"), INK)
                # La police est un objet nomme : il faut la resoudre pour
                # connaitre sa graisse.
                weight = tkfont.Font(root=self.app,
                                     font=item.cget("font")).actual("weight")
                self.assertEqual(weight, "bold")
                return
        self.fail("ligne médiane introuvable")

    def _pyramids(self):
        from compensation_analytics.ui.charts import PyramidChart

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        return [item for item in walk(self.app.overview_frame)
                if isinstance(item, PyramidChart)]

    def test_the_structures_are_drawn_as_pyramids(self):
        """Une pyramide dit en un regard ou se concentrent les effectifs et
        si la repartition entre les sexes bascule d'une tranche a l'autre."""
        pyramids = self._pyramids()
        self.assertEqual(len(pyramids), 2)
        for pyramid in pyramids:
            self.assertTrue(pyramid.rows)
            self.assertTrue(pyramid.has_split())

    def test_a_pyramid_reads_from_the_bottom_up(self):
        """La plus jeune tranche en bas : c'est la lecture attendue."""
        pyramid = self._pyramids()[0]
        self.assertTrue(pyramid.rows[-1]["label"].startswith("2"))

    def test_every_tenure_band_is_present(self):
        """Le decoupage s'etend selon les carrieres presentes."""
        labels = [row["label"] for row in self._pyramids()[-1].rows]
        self.assertGreater(len(labels), 5)
        # Les tranches sont renversees pour la lecture de bas en haut.
        self.assertTrue(labels[0].startswith(">"))

    def test_a_file_without_sex_falls_back_to_plain_bars(self):
        """Sans la colonne « Sexe », une pyramide n'aurait qu'une aile."""
        from compensation_analytics.ui.charts import PyramidChart

        pyramid = PyramidChart(self.app)
        pyramid.set_rows([{"label": "20-29", "count": 4, "share": 100.0,
                           "female": 0, "male": 0, "unknown_sex": 4}])
        self.assertFalse(pyramid.has_split())
        pyramid.destroy()


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

    def test_every_dimension_is_offered_to_the_dispersion(self):
        """L'onglet Segments a disparu ; ses dimensions restent celles que la
        dispersion propose, sans en perdre une."""
        offered = list(self.app.box_choice.cget("values"))
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


@needs_display
class TestTheOverviewLeavesNoGapInTheMiddle(unittest.TestCase):
    """Le bloc court ne doit pas creuser un trou au milieu de la page.

    Dans une grille, la rangee prend la hauteur du plus grand des deux
    blocs : la pyramide des ages, plus courte que l'echelle de
    remuneration, laissait un vide sous elle et repoussait la structure
    d'anciennete vers le bas. Les colonnes sont empilees separement.
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
        self.app.update_idletasks()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _panels(self):
        from compensation_analytics.ui.charts import PyramidChart

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        return [item for item in walk(self.app.overview_frame)
                if isinstance(item, PyramidChart)]

    def test_the_second_chart_follows_the_first_closely(self):
        first, second = self._panels()[:2]
        gap = second.winfo_rooty() - (first.winfo_rooty() + first.winfo_height())
        # Le titre du second bloc et sa marge occupent quelques dizaines de
        # pixels ; au-dela, c'est un trou.
        self.assertLess(gap, 90, f"écart de {gap} px entre les deux blocs")

    def test_the_two_columns_are_independent(self):
        """Chaque colonne se referme sur son contenu : le vide tombe en bas
        de page, pas entre deux graphiques."""
        pyramids = self._panels()
        columns = {item.master.master for item in pyramids}
        self.assertEqual(len(columns), 1, "les deux blocs doivent partager "
                                          "la meme colonne")

if __name__ == "__main__":
    unittest.main()
