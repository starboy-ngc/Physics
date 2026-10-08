"""Tests de l'interface graphique.

Ceux qui exigent un affichage sont ignores automatiquement : le moteur doit
rester testable sur un serveur sans ecran, et une installation de Python
depourvue de tkinter doit continuer de fonctionner en ligne de commande.
"""

import ast
import glob
import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import fresh_config
from tests.support import CONFIG_DIR
from tests.support import HEADERS, REFERENCE_DATE, make_row
from hr_analytics.io.xlsx_writer import write_workbook

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
                os.path.join(ROOT, "hr_analytics", folder, "*.py"))
        yield os.path.join(ROOT, "hr_analytics", "version.py")

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
        from hr_analytics.cli import build_parser
        parser = build_parser()
        commands = [a.choices for a in parser._actions if a.choices][0]
        self.assertIn("interface", commands)

    def test_missing_tkinter_gives_a_readable_message(self):
        """Sans tkinter, l'outil explique et renvoie a la ligne de commande
        plutot que d'echouer sur une trace technique."""
        import argparse
        import io
        import contextlib
        from hr_analytics import cli

        blocked = dict(sys.modules)
        blocked["hr_analytics.ui.app"] = None  # force l'ImportError
        saved = sys.modules.get("hr_analytics.ui.app", "absent")
        sys.modules["hr_analytics.ui.app"] = None
        try:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = cli.command_interface(argparse.Namespace())
            self.assertEqual(code, 3)
            self.assertIn("tkinter", stderr.getvalue())
            self.assertIn("--help", stderr.getvalue())
        finally:
            if saved == "absent":
                sys.modules.pop("hr_analytics.ui.app", None)
            else:
                sys.modules["hr_analytics.ui.app"] = saved


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestScatterGeometry(unittest.TestCase):
    """Le calcul de cadrage ne demande pas d'affichage."""

    def test_bounds_add_a_margin(self):
        from hr_analytics.ui.charts import ScatterChart
        bounds = ScatterChart._compute_bounds(
            [{"x": 2, "y": 10}, {"x": 10, "y": 20}])
        self.assertIsNotNone(bounds)
        x_min, x_max, y_min, y_max = bounds
        # Sans marge, les points extremes collent aux axes.
        self.assertLess(x_min, 2)
        self.assertGreater(x_max, 10)
        self.assertLess(y_min, 10)
        self.assertGreater(y_max, 20)

    def test_the_margin_never_opens_below_zero(self):
        """Une anciennete a zero ouvrait le cadre a -0,4 an : un quart de
        repere ou aucune donnee ne peut exister."""
        from hr_analytics.ui.charts import ScatterChart
        x_min, _x_max, y_min, _y_max = ScatterChart._compute_bounds(
            [{"x": 0, "y": 0}, {"x": 10, "y": 20}])
        self.assertEqual(x_min, 0.0)
        self.assertEqual(y_min, 0.0)

    def test_bounds_of_an_empty_cloud(self):
        from hr_analytics.ui.charts import ScatterChart
        self.assertIsNone(ScatterChart._compute_bounds([]))

    def test_a_single_point_still_has_a_frame(self):
        from hr_analytics.ui.charts import ScatterChart
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
                         groupe=["G3", "G5", "G7"][i % 3],
                         age=28 + i % 30, tenure=i % 18)
                for i in range(120)]
        write_workbook(cls.source, [("Population", [HEADERS] + rows)])

    def setUp(self):
        from hr_analytics.ui.app import Application
        self.app = Application(config_dir=fresh_config())
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

        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        self._load()
        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
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
        from hr_analytics.core.pipeline import load_population
        population, mapping, _ = load_population(
            self.source, self.app.configuration, reference_date=REFERENCE_DATE)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app._populate_filters()
        self.app.update()

    def test_the_window_opens_with_the_expected_steps(self):
        self.assertEqual(self.app.title(),
                         "HR Analytics 1.0.0")
        from hr_analytics.ui.app import TABS

        self.assertEqual(len(self.app.tabs), len(TABS))
        self.assertEqual([key for key, _label in TABS],
                         ["population", "organigramme", "graphique",
                          "equite", "qualite"])
        # « Graphique » en porte plusieurs : la barre principale ne dit plus
        # a elle seule tout ce que l'outil sait montrer.
        self.assertEqual(self.app.chartbar.visible_keys(),
                         ["nuage", "distribution", "boites", "colonnes"])

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
        from hr_analytics.ui import charts

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
        champ = next(iter(self.app.filter_values))
        self.app.set_filter(champ, ["France"])
        self.app.toggle_sidebar()
        self._settle()
        self.app.toggle_sidebar()
        self._settle()
        self.assertEqual(self.app.filter_values[champ], ["France"])

    def test_actions_are_disabled_until_a_file_is_loaded(self):
        self.assertIn("disabled", self.app.analyse_button.state())
        self.assertIn("disabled", self.app.export_button.state())

    def test_filters_are_populated_from_the_file(self):
        """L'utilisateur choisit parmi ce que contient son fichier : aucune
        syntaxe a taper, aucune valeur inventee."""
        self._load()
        self.assertIn("business_unit", self.app.filter_values)
        self.assertIn("France", self.app._filter_choices["business_unit"])
        # Sans filtre, le bouton dit « toutes », et combien.
        bouton = self.app._filter_buttons["business_unit"]
        self.assertEqual(
            bouton.cget("text"),
            f"Toutes ({len(self.app._filter_choices['business_unit'])})")

    def test_a_filter_narrows_the_analysis(self):
        self._load()
        self.app.set_filter("business_unit", ["France"])
        definitions = self.app._current_filters()
        self.assertEqual(definitions,
                         [{"field": "business_unit", "operator": "eq",
                           "value": "France"}])
        self.assertEqual(
            self.app._filter_buttons["business_unit"].cget("text"), "France")

    def test_unselected_filters_are_ignored(self):
        self._load()
        self.assertEqual(self.app._current_filters(), [])

    def test_a_filter_retains_several_values(self):
        """La question posée à un fichier de paie est rarement « ce
        poste-ci » : c'est « ces trois postes-là »."""
        self._load()
        champ, toutes = next(
            (champ, valeurs)
            for champ, valeurs in self.app._filter_choices.items()
            if len(valeurs) > 2)
        valeurs = toutes[:2]
        self.app.set_filter(champ, valeurs)
        self.assertEqual(self.app._current_filters(),
                         [{"field": champ, "operator": "in",
                           "value": valeurs}])
        self.assertIn(f"2 valeurs sur {len(toutes)}",
                      self.app._filter_buttons[champ].cget("text"))

    def test_retaining_everything_is_no_filter_at_all(self):
        """Et retenir zéro valeur non plus : un filtre vide porterait sur
        zéro salarié, ce qui n'est la réponse à aucune question."""
        self._load()
        toutes = self.app._filter_choices["business_unit"]
        self.app.set_filter("business_unit", list(toutes))
        self.assertEqual(self.app._current_filters(), [])
        self.app.set_filter("business_unit", [])
        self.assertEqual(self.app._current_filters(), [])
        self.assertIn("Toutes",
                      self.app._filter_buttons["business_unit"].cget("text"))

    def test_the_values_keep_the_order_of_the_file(self):
        """Pour que « 2 valeurs » soient les mêmes deux à chaque lecture,
        quel que soit l'ordre des clics dans le sélecteur."""
        self._load()
        champ, toutes = next(
            (champ, valeurs)
            for champ, valeurs in self.app._filter_choices.items()
            if len(valeurs) > 2)
        self.app.set_filter(champ, list(reversed(toutes[:2])))
        self.assertEqual(self.app.filter_values[champ], list(toutes[:2]))

    def test_a_long_value_is_cut_on_the_button(self):
        """La colonne est étroite : un intitulé de poste entier s'y ferait
        rogner sans prévenir, ce qui se lirait comme une valeur tronquée
        par l'outil."""
        self._load()
        champ = next(iter(self.app._filter_choices))
        long = "Responsable du développement commercial international"
        self.app._filter_choices[champ].append(long)
        self.app.set_filter(champ, [long])
        texte = self.app._filter_buttons[champ].cget("text")
        self.assertTrue(texte.endswith("…"), texte)
        self.assertLessEqual(len(texte), self.app.FILTER_LABEL_MAX)
        self.assertTrue(long.startswith(texte[:-1]))

    def test_an_unknown_value_is_not_retained(self):
        """Filtrer sur une valeur que le fichier ne porte pas donnerait une
        analyse sur zéro salarié sans que rien ne le dise."""
        self._load()
        self.app.set_filter("business_unit", ["France", "Pays imaginaire"])
        self.assertEqual(self.app.filter_values["business_unit"], ["France"])


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestTheIndicatorTablesAreBuiltOnce(unittest.TestCase):
    """L'echelle et la dispersion se construisent en un seul endroit.

    Elles ont ete ecrites en double le temps qu'un second ecran les montre,
    et elles se seraient ecartees : retirer un percentile de la
    configuration n'aurait tenu qu'a l'un des deux. Le second ecran a
    disparu, la regle reste — c'est elle qui garantit que l'echelle affichee
    suit les percentiles publies, et rien d'autre."""

    def setUp(self):
        from hr_analytics.ui import app
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
        """Le moteur calcule toujours P10 a P90 — les ratios de dispersion
        en ont besoin — mais l'utilisateur decide lesquels sont publies.
        L'echelle trace ceux-la, et pas les cinq habituels : les tracer tous
        reviendrait a publier ce qu'il a retire."""
        from hr_analytics.ui.charts import ScaleChart

        chart = ScaleChart.__new__(ScaleChart)
        chart.salary, chart.currency = self.salary, "EUR"
        self.assertEqual([label for _k, label, _v in chart.points()],
                         ["Q1 (P25)", "Médiane (P50)", "Q3 (P75)"])

        chart.salary = dict(self.salary, published_percentiles=[
            {"key": "median", "label": "Médiane (P50)"}])
        self.assertEqual([label for _k, label, _v in chart.points()],
                         ["Médiane (P50)"])

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


@needs_display
class TestTheScreenPrivacySetting(unittest.TestCase):
    """La case « Afficher les noms » n'engage que l'ecran."""

    def setUp(self):
        import shutil
        from hr_analytics.ui.app import Application
        self.directory = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.directory, "config")
        shutil.copytree(CONFIG_DIR, self.config_dir)
        self.app = Application(config_dir=self.config_dir)
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _window(self):
        from hr_analytics.ui.settings import SettingsWindow
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




@needs_display
class TestThePeriodSelector(unittest.TestCase):
    """Le reglage ne parait que s'il a une raison d'etre."""

    def setUp(self):
        from hr_analytics.ui.app import Application

        self.directory = tempfile.mkdtemp()
        self.app = Application(config_dir=fresh_config())
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _load(self, periods):
        import csv

        from hr_analytics.core.pipeline import load_population

        headers = list(HEADERS) + (["Période"] if periods else [])
        path = os.path.join(self.directory, f"p{len(periods)}.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(headers)
            for period in periods or [None]:
                for number in range(30):
                    row = list(make_row(number, salary=40000 + number * 60))
                    writer.writerow(row + ([period] if period else []))
        population, mapping, _table = load_population(path,
                                                      self.app.configuration)
        self.app.source_path = path
        self.app.population = population
        self.app.mapping = mapping
        self.app._populate_filters()
        self.app.update()

    def test_a_snapshot_file_shows_no_period_setting(self):
        """Un reglage qui ne sert a rien encombre le parcours."""
        self._load([])
        self.assertFalse(self.app.period_block.winfo_manager())
        self.assertEqual(self.app._periods, [])

    def test_several_periods_bring_the_setting_out(self):
        self._load(["2024", "2025", "2026"])
        self.assertEqual(self.app.period_block.winfo_manager(), "pack")
        self.assertEqual(self.app._periods, ["2024", "2025", "2026"])
        # La plus recente est proposee : c'est celle qu'on regarde.
        self.assertEqual(self.app.period_var.get(), "2026")
        self.assertEqual(list(self.app.period_choice.cget("values")),
                         ["2024", "2025", "2026"])

    def test_the_setting_disappears_again_with_a_snapshot_file(self):
        """Charger un second fichier ne doit pas laisser le reglage du
        premier."""
        self._load(["2024", "2025"])
        self.assertTrue(self.app.period_block.winfo_manager())
        self._load([])
        self.assertFalse(self.app.period_block.winfo_manager())


@needs_display
class TestTheTeamSelector(unittest.TestCase):
    """Choisir une equipe avant d'analyser.

    La colonne « manager » n'est pas obligatoire : le reglage ne parait que
    si le fichier permet d'en deduire un arbre.
    """

    def setUp(self):
        from hr_analytics.ui.app import Application

        self.directory = tempfile.mkdtemp()
        self.app = Application(config_dir=fresh_config())
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _load(self, with_manager=True, periods=(), broken=False):
        """DG > 2 directeurs > 2 managers chacun > 5 salaries chacun."""
        import csv

        from hr_analytics.core.pipeline import load_population

        links = [("DG", "")]
        for direction in range(2):
            links.append((f"D{direction}", "DG"))
            for team in range(2):
                links.append((f"M{direction}{team}", f"D{direction}"))
                for member in range(5):
                    links.append((f"E{direction}{team}{member}",
                                  f"M{direction}{team}"))
        if broken:
            links += [("X", "Y"), ("Y", "X"), ("Z", "ABSENT")]
        headers = list(HEADERS) + (["Manager"] if with_manager else [])
        headers += ["Période"] if periods else []
        path = os.path.join(self.directory,
                            f"t{int(with_manager)}{len(periods)}{int(broken)}.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(headers)
            for index, period in enumerate(periods or [None]):
                for number, (key, manager) in enumerate(links):
                    row = list(make_row(number, employee_id=key,
                                        salary=40000 + index * 1000
                                        + number * 50))
                    writer.writerow(row + ([manager] if with_manager else [])
                                    + ([period] if period else []))
        population, mapping, _table = load_population(path,
                                                      self.app.configuration)
        self.app.source_path = path
        self.app.population = population
        self.app.mapping = mapping
        self.app._populate_filters()
        self.app.update()
        return path

    def _label(self, key):
        return next(label for label, other in self.app._team_keys.items()
                    if other == key)

    def test_a_file_without_the_column_shows_no_team_setting(self):
        """La colonne n'est pas obligatoire : sans elle, pas de reglage."""
        self._load(with_manager=False)
        self.assertFalse(self.app.team_block.winfo_manager())
        self.assertEqual(self.app._team_keys, {})

    def test_a_manager_column_brings_the_setting_out(self):
        self._load()
        self.assertEqual(self.app.team_block.winfo_manager(), "pack")
        self.assertEqual(len(self.app._team_keys), 7)

    def test_the_whole_file_is_the_default_choice(self):
        self._load()
        self.assertEqual(self.app.team_var.get(), "(tout le périmètre)")

    def test_the_list_reads_from_the_top_down(self):
        self._load()
        keys = list(self.app._team_keys.values())
        self.assertEqual(keys[0], "DG")
        self.assertEqual(sorted(keys[1:3]), ["D0", "D1"])

    def test_deeper_managers_are_set_back(self):
        """L'indentation est ce qui fait lire une liste plate comme un
        organigramme."""
        self._load()
        self.assertFalse(self._label("DG").startswith("·"))
        self.assertTrue(self._label("D0").startswith("· "))
        self.assertTrue(self._label("M00").startswith("· · "))

    def test_the_label_carries_no_headcount(self):
        """Mesure faite, « NOM PRENOM - 10 direct(s), 10 au total » demande
        262 px, 420 avec un patronyme reel, quand la liste en offre 237 :
        les effectifs se lisent sous la liste, ou rien ne les rogne."""
        self._load()
        for label in self.app._team_keys:
            self.assertNotIn("direct", label)
            self.assertNotIn("total", label)

    def test_the_note_gives_both_headcounts(self):
        self._load()
        self.app.team_var.set(self._label("D0"))
        self.app.update()
        note = self.app.team_note.cget("text")
        self.assertIn("12", note)                 # 2 managers et leurs 10
        self.assertIn("2 en direct", note)

    def test_the_note_follows_the_direct_team_setting(self):
        self._load()
        self.app.team_var.set(self._label("D0"))
        self.app.team_direct_var.set(True)
        self.app.update()
        self.assertIn("Équipe directe : 2", self.app.team_note.cget("text"))

    def test_homonyms_are_told_apart_by_their_identifier(self):
        """Deux « MARTIN Jean » dans la liste sont indiscernables : le
        matricule tranche, et seulement quand le nom ne suffit pas."""
        self._load()
        labels = list(self.app._team_keys)
        self.assertEqual(len(labels), len(set(labels)))

    def test_a_broken_tree_is_reported_by_the_numbers(self):
        """Jamais par les matricules : la colonne designe des personnes."""
        self._load(broken=True)
        note = self.app.team_note.cget("text")
        self.assertIn("Arbre incomplet", note)
        self.assertIn("responsable introuvable", note)
        self.assertIn("boucle", note)
        for identifier in ("ABSENT", "X", "Y", "Z"):
            self.assertNotIn(identifier, note)

    def test_changing_the_period_rebuilds_the_tree(self):
        """L'organigramme de 2024 n'est pas celui de 2026 : une liste
        laissee en place proposerait des equipes disparues."""
        self._load(periods=("2024", "2025"))
        self.assertEqual(self.app.period_var.get(), "2025")
        before = list(self.app._team_keys)
        self.app.team_var.set(self._label("D0"))
        self.app.period_var.set("2024")
        self.app.update()
        self.assertEqual(list(self.app._team_keys), before)
        self.assertEqual(len(self.app._team_keys), 7)

    def test_the_setting_disappears_again_without_the_column(self):
        self._load()
        self.assertTrue(self.app.team_block.winfo_manager())
        self._load(with_manager=False)
        self.assertFalse(self.app.team_block.winfo_manager())

    def test_the_request_carries_the_chosen_team(self):
        """Ce que la fenetre demande au moteur, sans lancer l'analyse."""
        self._load()
        self.app.team_var.set(self._label("D0"))
        self.app.team_direct_var.set(True)
        self.app.update()
        self.assertEqual(
            self.app._team_keys[self.app.team_var.get()], "D0")
        self.assertTrue(self.app.team_direct_var.get())


@needs_display
class TestTheDispersionSplitBySex(unittest.TestCase):
    """Deux medianes proches peuvent recouvrir deux distributions tres
    differentes : une seule boite par segment ne dit pas si les deux sexes
    s'y etalent pareil."""

    def setUp(self):
        from hr_analytics.ui import theme
        from hr_analytics.ui.charts import BoxPlotChart
        from hr_analytics.core.config import load_configuration

        self.root = tkinter.Tk()
        self.root.geometry("900x500")
        theme.load(load_configuration(CONFIG_DIR))
        theme.Fonts(self.root)
        self.chart = BoxPlotChart(self.root)
        self.chart.pack(fill="both", expand=True)
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def _rows(self, female_chartable=True, male_chartable=True):
        stats = {"p10": 30000.0, "p25": 35000.0, "median": 40000.0,
                 "p75": 45000.0, "p90": 50000.0, "masked": False}
        return [{
            "segment": "France", "headcount": 60, "masked": False,
            "chartable": True, "sex_chartable": female_chartable or male_chartable,
            "salary": dict(stats),
            "female": dict(stats, median=38000.0),
            "male": dict(stats, median=42000.0),
            "female_count": 30, "male_count": 30,
            "female_chartable": female_chartable,
            "male_chartable": male_chartable,
        }]

    def test_two_boxes_are_drawn_instead_of_one(self):
        self.chart.set_rows(self._rows(), "EUR")
        self.root.update()
        simple = len(self.chart._items)
        self.chart.set_split(True)
        self.root.update()
        self.assertEqual(len(self.chart._items), simple * 2)

    def test_a_sex_below_the_chart_threshold_is_not_drawn(self):
        """Un segment de cinquante personnes dont quatre femmes ne donne pas
        le droit de dessiner les percentiles de ces quatre-la."""
        self.chart.split = True
        self.chart.set_rows(self._rows(female_chartable=False), "EUR")
        self.root.update()
        self.assertEqual(len(self.chart._items), 1)
        # La ligne entiere est desormais retenue, et la moitie a part :
        # la bulle montre les trois colonnes et a besoin des deux.
        dessinees = {moitié for _row, moitié in self.chart._items.values()}
        self.assertEqual(dessinees, {"male"})

    def test_a_segment_with_neither_sex_drawable_leaves_the_list(self):
        self.chart.split = True
        self.chart.set_rows(self._rows(False, False), "EUR")
        self.root.update()
        self.assertEqual(self.chart._drawable(), [])

    def test_the_dimension_order_is_offered_again(self):
        """Il avait ete retire comme ordre par defaut, et c'etait la bonne
        decision — mais il avait ete retire tout court, ce qui laissait
        sans recours une dimension qui *a* un ordre propre.

        Un coefficient se lit dans l'ordre des nombres, une tranche d'age
        dans celui des tranches : les ranger par effectif defait la
        progression meme qu'on vient lire, et aucune entree de la liste ne
        permettait de la retrouver.
        """
        from hr_analytics.ui.charts import BoxPlotChart

        self.assertIn("moteur", dict(BoxPlotChart.ORDERS))

    def test_the_headcount_comes_first(self):
        """Devant une dimension a quarante postes, la premiere question est
        « lesquels pesent », pas « lesquels paient le mieux » : un poste de
        six personnes en tete de liste met en avant ce qui compte le
        moins.

        C'est l'ordre d'ouverture de cette presentation-ci, et il ne tient
        plus au rang dans la liste : une entree ajoutee en tete changeait
        le defaut sans que personne le decide.
        """
        from hr_analytics.ui.charts import BoxPlotChart

        self.assertEqual(BoxPlotChart.DEFAUT, "headcount")
        self.assertEqual(BoxPlotChart(self.root).order, "headcount")

    def test_the_axis_follows_the_boxes_instead_of_the_frame(self):
        """La graduation flottait deux cents pixels sous la derniere boite."""
        self.chart.set_rows(self._rows(), "EUR")
        self.root.update()
        dessine = self.chart.canvas.bbox("all")
        self.assertIsNotNone(dessine)
        # Le canevas se reduit au trace tant que celui-ci tient.
        self.assertLess(self.chart.canvas.winfo_height(),
                        self.root.winfo_height() - self.chart.FOOTER_HEIGHT)


@needs_display
class TestACriticalQualityFindingIsSaidWhereOneLooks(unittest.TestCase):
    """Un fichier qui porte des anomalies critiques produit quand meme une
    analyse — mais l'utilisateur doit l'apprendre sans avoir a penser a
    ouvrir l'onglet « Qualite ». Un chiffre faux qui a l'air juste est le
    pire des resultats."""

    @classmethod
    def setUpClass(cls):
        import datetime as _dt

        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "douteux.xlsx")
        rows = [make_row(index, salary=30000 + index * 500)
                for index in range(40)]
        # Une sortie anterieure a l'entree : critique, et signalee comme
        # telle par le controle qualite.
        rows[0] = make_row(0, hire_date=_dt.date(2020, 1, 1),
                           leave_date=_dt.date(2015, 1, 1))
        write_workbook(cls.source, [("Population", [HEADERS] + rows)])

    def setUp(self):
        import time

        from hr_analytics.ui.app import Application
        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          load_population,
                                                          run_analysis)

        self.app = Application(config_dir=fresh_config())
        self.app.update()
        population, mapping, table = load_population(
            self.source, self.app.configuration, reference_date=REFERENCE_DATE)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app.headers = list(table.headers)
        self.app._populate_filters()
        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=self.source, reference_date=REFERENCE_DATE,
            ignore_quality_errors=True))
        self.app._render_results()
        self.app.update()
        self.addCleanup(self.app.destroy)

    def test_the_status_line_counts_them(self):
        self.assertIn("critique", self.app.status.cget("text"))

    def test_a_banner_points_at_the_quality_tab(self):
        self.assertTrue(self.app.notice.winfo_ismapped())
        texte = str(self.app.notice.cget("text"))
        self.assertIn("Qualité", texte)
        self.assertIn("critique", texte)

    def test_a_clean_file_says_nothing_of_the_sort(self):
        """Le bandeau ne doit pas devenir un decor permanent."""
        import time

        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)

        propre = os.path.join(self.directory, "propre.xlsx")
        write_workbook(propre, [("Population",
                                 [HEADERS] + [make_row(i, salary=30000 + i * 400)
                                              for i in range(40)])])
        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=propre, reference_date=REFERENCE_DATE))
        self.app._render_results()
        self.app.update()
        self.assertNotIn("critique", self.app.status.cget("text"))


@needs_display
class TestTheScatterLegendWhenTheDimensionIsLong(unittest.TestCase):
    """Colorer par « Poste » demande quarante couleurs a une serie qui en
    compte dix. La legende, elle, disparaissait au-dela de seize entrees :
    le nuage restait colore, mais plus rien ne disait de quoi."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "postes.xlsx")
        # Quinze modalites d'effectifs differents : de quoi depasser la
        # serie de couleurs et faire jouer le regroupement.
        rows = [make_row(i, salary=30000 + (i % 40) * 800,
                         business_unit=f"BU{i % 15:02d}",
                         age=28 + i % 30, tenure=i % 18)
                for i in range(300)]
        write_workbook(cls.source, [("Population", [HEADERS] + rows)])

    def setUp(self):
        from hr_analytics.ui.app import Application

        self.app = Application(config_dir=fresh_config())
        self.app.geometry("1400x900")
        self.app.update()
        self._analyse()
        self.app.tabbar.select("graphique")
        self.app.chartbar.select("nuage")
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _analyse(self):
        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          load_population,
                                                          run_analysis)

        population, mapping, _ = load_population(
            self.source, self.app.configuration, reference_date=REFERENCE_DATE)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app._populate_filters()
        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=self.source, reference_date=REFERENCE_DATE,
            segments=[]))
        self.app._render_results()
        self.app.update()

    def _chips(self):
        """Intitules des pastilles, toutes lignes confondues."""
        import tkinter as tk

        textes = []
        for ligne in self.app.legend_frame.winfo_children():
            for chip in ligne.winfo_children():
                for widget in chip.winfo_children():
                    if isinstance(widget, tk.Label):
                        textes.append(widget.cget("text"))
        return textes

    def test_every_modality_of_the_chart_is_in_the_legend(self):
        groups = self.app.scatter.dataset.get("groups")
        self.assertTrue(groups)
        for group in groups:
            self.assertIn(group, self._chips())

    def test_the_legend_folds_instead_of_being_cut(self):
        """« Responsable administratif et financier » occupe le quart d'une
        ligne a lui seul : la legende tient sur plusieurs lignes, mesurees
        et non estimees."""
        self.app.geometry("900x820")
        self.app.update()
        self.app._flow_legend()
        self.app.update()
        lignes = self.app.legend_frame.winfo_children()
        self.assertGreater(len(lignes), 1)
        droite = self.app.legend_frame.winfo_rootx() + \
            self.app.legend_frame.winfo_width()
        for ligne in lignes:
            for chip in ligne.winfo_children():
                self.assertLessEqual(chip.winfo_rootx() + chip.winfo_width(),
                                     droite)

    def test_the_grouping_never_wears_a_series_colour(self):
        """Un regroupement de la couleur d'un vrai poste se lirait comme ce
        poste."""
        from hr_analytics.ui import theme

        autres = self.app.scatter.dataset.get("other_label")
        self.assertIsNotNone(autres)
        pastille = self._dot_of(autres)
        self.assertEqual(pastille, theme.FAINT)
        self.assertNotIn(pastille, theme.ACTIVE.series)

    def _dot_of(self, group):
        import tkinter as tk

        for ligne in self.app.legend_frame.winfo_children():
            for chip in ligne.winfo_children():
                labels = [w for w in chip.winfo_children()
                          if isinstance(w, tk.Label)]
                if labels and labels[0].cget("text") == group:
                    canvas = [w for w in chip.winfo_children()
                              if isinstance(w, tk.Canvas)][0]
                    return canvas.itemcget(canvas.find_all()[0], "fill")
        return None

    def test_the_legend_colours_are_those_of_the_points(self):
        """La pastille doit etre exactement la couleur du point."""
        from hr_analytics.core import palette
        from hr_analytics.ui import theme

        dataset = self.app.scatter.dataset
        couleurs = palette.series_map(
            dataset["groups"], theme.ACTIVE.series,
            other=dataset.get("other_label"), neutral=theme.FAINT)
        for group in dataset["groups"]:
            self.assertEqual(self._dot_of(group), couleurs[group])

    def test_hiding_the_grouping_leaves_the_named_modalities(self):
        """Masquer « Autres » est la facon de ne garder que les modalites
        nommees."""
        dataset = self.app.scatter.dataset
        autres = dataset["other_label"]
        self.app.scatter.toggle_group(autres)
        self.app.update()
        restants = {point["group"]
                    for point in self.app.scatter.visible_points()}
        self.assertNotIn(autres, restants)
        self.assertTrue(restants)


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestDrawnImages(unittest.TestCase):
    """Le canevas Tk ne lisse pas ses traces : les formes fines sont des
    images antialiasees, produites sans la moindre dependance."""

    def test_a_disc_is_round_and_not_square(self):
        """Le defaut corrige : create_oval rendait des carres a coins
        ronges. Un coin de l'image doit donc etre transparent, et son
        centre opaque."""
        from hr_analytics.ui.raster import Raster, _circle
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
        from hr_analytics.ui.raster import Raster, _circle
        size = 9
        raster = Raster(size).paint(_circle(size / 2.0, size / 2.0 - 0.5),
                                    (0, 0, 0))
        alphas = {pixel[3] for row in raster.pixels for pixel in row}
        partial = [value for value in alphas if 0.0 < value < 1.0]
        self.assertTrue(partial, "aucun pixel de bord adouci")

    def _ring_pixels(self, diameter=40, hole=12, parts=None):
        """L'anneau relu pixel par pixel, en RVBA."""
        import base64
        import zlib

        from hr_analytics.ui import raster

        parts = parts or [(0.5, (0, 0, 0)), (0.5, (255, 255, 255))]
        png = base64.b64decode(raster.ring(diameter, hole, parts))
        # IHDR fait 25 octets apres la signature ; vient ensuite IDAT.
        donnees = png[8 + 25:]
        taille = int.from_bytes(donnees[:4], "big")
        brut = zlib.decompress(donnees[8:8 + taille])
        lignes = []
        pas = diameter * 4 + 1
        for y in range(diameter):
            debut = y * pas + 1
            lignes.append(brut[debut:debut + diameter * 4])
        return lignes

    def test_the_ring_is_hollow_and_bounded(self):
        """Le centre doit etre transparent — c'est le trou qui porte
        l'effectif — et les coins aussi : un anneau carre serait un
        rectangle."""
        diameter = 40
        lignes = self._ring_pixels(diameter)
        centre = diameter // 2
        self.assertEqual(lignes[centre][centre * 4 + 3], 0)
        self.assertEqual(lignes[0][3], 0)

    def test_the_ring_edges_are_softened(self):
        """Sans pixel a opacite intermediaire, le bord est un escalier —
        c'est le defaut qui se voyait en premier sur la page."""
        lignes = self._ring_pixels()
        alphas = {ligne[x * 4 + 3] for ligne in lignes
                  for x in range(len(ligne) // 4)}
        partiels = [value for value in alphas if 0 < value < 255]
        self.assertTrue(partiels, "aucun bord adouci")

    def test_each_part_takes_its_colour(self):
        """Deux moities, deux couleurs, et la coupure entre elles."""
        diameter = 40
        lignes = self._ring_pixels(diameter)
        milieu = lignes[diameter // 2]
        # A gauche du centre, la seconde part ; a droite, la premiere.
        gauche = milieu[2 * 4:2 * 4 + 4]
        droite = milieu[(diameter - 3) * 4:(diameter - 3) * 4 + 4]
        self.assertEqual(gauche[3], 255)
        self.assertEqual(droite[3], 255)
        self.assertNotEqual(gauche[:3], droite[:3])

    def test_a_ring_is_computed_once(self):
        """Quatre-vingts millisecondes par anneau : il ne se recalcule pas
        a chaque redimensionnement."""
        from hr_analytics.ui import raster
        parts = [(0.3, (1, 2, 3)), (0.7, (4, 5, 6))]
        first = raster.ring(30, 10, parts)
        self.assertIs(first, raster.ring(30, 10, parts))

    def test_the_images_are_valid_png(self):
        from hr_analytics.ui import raster
        import base64
        for data in (raster.disc(7, (47, 93, 138)),
                     raster.checkbox(15, True, (47, 93, 138), (47, 93, 138))):
            self.assertTrue(base64.b64decode(data).startswith(b"\x89PNG\r\n\x1a\n"))

    def test_images_are_computed_once_per_appearance(self):
        """Un nuage de 2 000 points ne doit pas recalculer 2 000 images."""
        from hr_analytics.ui import raster
        first = raster.disc(7, (10, 20, 30))
        self.assertIs(first, raster.disc(7, (10, 20, 30)))

    def test_a_checked_box_differs_from_an_unchecked_one(self):
        from hr_analytics.ui import raster
        colour, border = (47, 93, 138), (207, 215, 223)
        self.assertNotEqual(raster.checkbox(15, True, colour, border),
                            raster.checkbox(15, False, colour, border))


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestScrollbarsAreUsable(unittest.TestCase):
    def test_the_scrollbar_is_wide_enough_to_grab(self):
        """Le defaut corrige : "arrowsize=0" reduisait l'ascenseur a un
        pixel de large. Il defilait, mais aucun curseur ne l'attrapait."""
        from hr_analytics.ui.theme import SCROLLBAR_WIDTH
        self.assertGreaterEqual(SCROLLBAR_WIDTH, 10)


@needs_display
class TestScrollbarPlacement(unittest.TestCase):
    def test_a_hidden_scrollbar_comes_back_at_its_full_width(self):
        """Reempile apres la zone defilante, qui est en expansion,
        l'ascenseur ne recuperait aucune largeur : il revenait invisible."""
        import tkinter as tk
        from tkinter import ttk
        from hr_analytics.ui import theme

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
        from hr_analytics.ui import theme

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
        from hr_analytics.ui.app import TABS
        self.assertEqual(TABS[-1][0], "qualite")
        self.assertEqual(TABS[0][0], "population")
        self.assertEqual(TABS[0][1], "Vue d'ensemble")

    def test_population_and_pay_share_one_page(self):
        """Un salaire median ne veut rien dire sans l'age et l'anciennete de
        la population qui le porte : les separer obligeait a garder un
        chiffre en tete en changeant d'onglet."""
        from hr_analytics.ui.app import TABS
        self.assertNotIn("remuneration", [key for key, _label in TABS])


@needs_display
class TestTabsFollowWhatCanBePublished(unittest.TestCase):
    """Un onglet dont le contenu est masque n'a rien a montrer.

    Les seuils ne sont pas re-evalues dans l'interface : elle lit ce que le
    moteur a decide. Ce qui garantit qu'une regle de confidentialite reste
    definie a un seul endroit.
    """

    def _analysed(self, count, **row_options):
        from hr_analytics.ui.app import Application
        from hr_analytics.core.pipeline import (AnalysisRequest,
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
        app = Application(config_dir=fresh_config())
        app.update()
        app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=source, reference_date=REFERENCE_DATE,
            segments=[]))
        app._render_results()
        app.update()
        return app

    def test_the_banner_never_passes_the_headcount_off_as_a_threshold(self):
        """Le défaut qui a fait chercher un réglage inexistant.

        Le bandeau disait « les seuils de confidentialité s'appliquent à 8
        salariés ». Deux nombres de nature différente — l'effectif analysé
        et le seuil requis — tenaient la même place dans la phrase, et le
        premier se lisait comme le second : on cherchait alors où l'outil
        était réglé sur huit. Il ne l'a jamais été.
        """
        app = self._analysed(8)
        try:
            texte = app.notice.cget("text")
            self.assertIn("La sélection analysée compte 8 salarié(s)", texte)
            # Le seuil, lui, est celui que le moteur a appliqué, et il est
            # écrit à côté de la vue qu'il retire.
            self.assertIn("minimum paramétré : 10 salariés", texte)
            self.assertNotIn("seuils de confidentialité s'appliquent à 8",
                             texte)
        finally:
            app.destroy()

    def test_each_hidden_view_carries_its_own_reason(self):
        """Les seuils ne sont pas les mêmes : dix pour un graphique, cinq de
        chaque sexe pour un écart. Une phrase commune en annonçait un seul,
        donc un faux pour l'autre."""
        app = self._analysed(8)
        try:
            texte = app.notice.cget("text")
            self.assertIn("Graphiques :", texte)
            self.assertIn("Écarts F/H :", texte)
            self.assertIn("5 salariés de chaque sexe", texte)
            self.assertIn("Confidentialité", texte)
        finally:
            app.destroy()

    def test_the_reason_is_the_engine_own_words(self):
        """Recomposée dans la fenêtre, elle finirait par annoncer un seuil
        que le calcul n'emploie pas."""
        app = self._analysed(8)
        try:
            attendu = app.result.payload["pay_equity"]["warning"]
            self.assertIn(attendu, app.notice.cget("text"))
        finally:
            app.destroy()

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
                             ["distribution", "boites", "colonnes"])  # plus de nuage
            # Le graphique retire s'explique, comme un onglet retire — et
            # il nomme l'axe qui manque. Le nuage s'appelait
            # « Remuneration/Anciennete » et son titre disait pourquoi ; il
            # s'appelle « Nuage de points », c'est donc au message de le
            # dire.
            texte = app.notice.cget("text")
            self.assertIn("Nuage de points", texte)
            self.assertIn("Ancienneté", texte)
            self.assertIn("aucun salarié", texte)
            self.assertTrue(app.notice.winfo_ismapped())
        finally:
            app.destroy()

    def test_a_large_enough_population_keeps_every_tab(self):
        """Tous, sauf ceux qui ne paraissent que sur demande : l'absence de
        l'organigramme ne tient pas a un seuil mais au fait que personne
        n'a choisi d'equipe."""
        from hr_analytics.ui.app import ON_DEMAND

        app = self._analysed(40)
        try:
            self.assertEqual(sorted(app.tabbar.visible_keys()),
                             sorted(key for key in app.tabs
                                    if key not in ON_DEMAND))
            for key in ON_DEMAND:
                self.assertNotIn(key, app.tabbar.visible_keys())
        finally:
            app.destroy()

    def test_a_box_needs_more_people_than_a_table_row(self):
        """Tracer une dispersion en demande plus que la publier.

        Une boite dessine P10 et P90 : sur un segment de cinq salaries, ce
        sont deux remunerations individuelles pointees a l'ecran. Le segment
        garde donc sa ligne de tableau, mais pas sa boite.
        """
        from hr_analytics.core.metrics import PrivacyRules
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
        for canvas in (chart.canvas, getattr(chart, "footer", None),
                       getattr(chart, "header", None)):
            if canvas is None:
                continue
            textes += [canvas.itemcget(item, "text")
                       for item in canvas.find_all()
                       if canvas.type(item) == "text"]
        return textes

    def test_the_boxes_carry_their_reading_key(self):
        """Une boite a moustaches ne se devine pas : sans cle de lecture, le
        graphique le plus utile de l'outil reste le plus opaque."""
        from hr_analytics.ui.charts import BoxPlotChart

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
            phrase = [x for x in textes if "L'encadrement contient" in x]
            self.assertEqual(len(phrase), 1, textes)
            self.assertIn("10e et le 90e centile", phrase[0])
        finally:
            app.destroy()

    def test_the_boxes_show_the_overall_median_and_the_headcounts(self):
        """Un repere dessine se lit mieux qu'un montant a comparer de tete, et
        une boite tracee sur douze salaries a la meme allure que sur quatre
        cents."""
        from hr_analytics.ui.charts import BoxPlotChart

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
        from hr_analytics.ui.charts import BoxPlotChart

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
        from hr_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            chart.pack(fill="both", expand=True)
            chart.configure(width=900, height=380)
            app.update()

            def boites():
                # Le fond d'une ligne sur deux est un rectangle lui aussi,
                # et il part du bord gauche : il ne se compte pas.
                return sum(1 for item in chart.canvas.find_all()
                           if chart.canvas.type(item) == "rectangle"
                           and chart.canvas.coords(item)[0] > 0)

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
        from hr_analytics.ui.charts import BoxPlotChart

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
        from hr_analytics.ui.charts import BoxPlotChart

        app = self._analysed(40)
        try:
            chart = BoxPlotChart(app)
            rows = self._fake_rows(5)
            chart.set_rows(rows, "EUR")
            ordre = [row["segment"] for row in chart._drawable()]
            # L'ordre d'ouverture est la mediane decroissante : c'est la
            # question qu'on se pose devant une dispersion. Le classement
            # alphabetique a ete retire, il ne repondait a aucune.
            self.assertEqual(
                ordre,
                [row["segment"] for row in
                 sorted(rows, key=lambda r: -(r["salary"]["median"] or 0))])

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
        from hr_analytics.ui.charts import BoxPlotChart
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


    def test_the_status_line_says_what_was_filtered(self):
        """Le perimetre gouverne tous les onglets : il se lit dans la barre
        d'etat, visible quel que soit l'onglet ouvert, et non en tete d'une
        seule page."""
        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        from hr_analytics.core.segmentation import build_filters
        app = self._analysed(40)
        try:
            # Sans filtre, aucun critere dans la barre : ce serait du bruit.
            self.assertIn("40 salariés", app.status.cget("text"))
            self.assertNotIn("BU = ", app.status.cget("text"))

            app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
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
            # La raison est celle du moteur, qui la commence par une
            # majuscule : c'est le debut d'une phrase a lui.
            self.assertIn("effectif insuffisant", text.lower())
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
        from hr_analytics.ui.app import Application
        from hr_analytics.core.pipeline import load_population
        self.directory = tempfile.mkdtemp()
        source = os.path.join(self.directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, business_unit=["France", "DACH"][index % 2],
                     groupe=["G3", "G5", "G7"][index % 3])
            for index in range(60)])])
        self.app = Application(config_dir=fresh_config())
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
        self.app.set_filter("business_unit", ["France"])
        self.app.set_filter("groupe", ["G5"])
        self.assertEqual(len(self.app._current_filters()), 2)
        self.app.reset_filters()
        self.assertEqual(self.app._current_filters(), [])

    def test_the_number_of_active_criteria_is_recalled(self):
        """Les filtres defilent hors du champ visible : sans rappel, un
        critere pose puis oublie fausse la lecture de toute l'analyse."""
        self.assertEqual(self.app.filter_summary.cget("text"), "")
        self.app.set_filter("business_unit", ["France"])
        self.app.update()
        self.assertIn("1", self.app.filter_summary.cget("text"))

    def test_the_reset_link_keeps_its_place_and_its_label(self):
        """Le defaut signale : l'action disparaissait sous le curseur au
        moment ou l'on cliquait, ce qui se lit comme un bouton instable."""
        from hr_analytics.ui.theme import ACCENT, FAINT

        link = self.app.reset_filters_link
        self.assertEqual(link.cget("text"), "Réinitialiser")
        self.assertEqual(link.cget("foreground"), FAINT)
        self.assertFalse(link.enabled)

        self.app.set_filter("business_unit", ["France"])
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
        self.app.set_filter("business_unit", ["France"])
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
class TestTheMergedOverview(unittest.TestCase):
    """Population et remuneration sur une seule page.

    Les deux se lisent ensemble : un salaire median ne veut rien dire sans
    l'age et l'anciennete de la population qui le porte.
    """

    def setUp(self):
        from hr_analytics.ui.app import Application
        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        # Conserve : un test compose la page une seconde fois, sur une
        # fenetre qui n'a pas encore de taille.
        source = self.source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, salary=25000 + (index % 50) * 2000,
                     age=25 + index % 38, tenure=index % 32,
                     gender=["F", "H"][index % 2])
            for index in range(200)])])
        self.app = Application(config_dir=fresh_config())
        # Une page qui se dispose en colonnes et des graphiques qui se
        # tracent a la largeur de leur colonne ont besoin d'une fenetre qui
        # en ait une : sans geometrie, les canevas restent vides et le test
        # ne verifie plus rien.
        self.app.geometry("1500x1000+0+0")
        self.app.update()
        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=source, reference_date=REFERENCE_DATE))
        self.app._render_results()
        for _ in range(10):
            self.app.update()
            time.sleep(0.01)

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
                         "Pyramide des âges", "Pyramide d'ancienneté"):
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

        from hr_analytics.core import palette

        def taille(widget):
            return tkfont.Font(root=self.app,
                               font=widget.cget("font")).cget("size")

        labels = self._all_labels(self.app.overview_frame)
        titre = next(w for w in labels if w.cget("text") == "Dispersion")
        entete = next(w for w in labels if w.cget("text") == "INDICATEUR")
        ligne = next(w for w in labels if w.cget("text") == "Q3 / Q1")
        self.assertGreater(taille(titre), taille(ligne))
        self.assertGreater(taille(titre), taille(entete))
        blanc = palette.by_name(None).canvas
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
        # « Champ analysé » touchait le titre dans une colonne etroite : le
        # mot qui porte le sens est « Champ », et la valeur le precise.
        self.assertIn(f"Champ : {field}", texts)

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

    def _scale(self):
        from hr_analytics.ui.charts import ScaleChart  # noqa: F401

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        charts = [item for item in walk(self.app.overview_frame)
                  if isinstance(item, ScaleChart)]
        self.assertEqual(len(charts), 1, "échelle de rémunération introuvable")
        return charts[0]

    def _scale_texts(self):
        chart = self._scale()
        canvas = chart.canvas
        return [canvas.itemcget(item, "text") for item in canvas.find_all()
                if canvas.type(item) == "text"]

    def test_the_pay_ladder_runs_from_minimum_to_maximum(self):
        """Minimum et maximum se lisent aux deux bouts de l'échelle, en
        retrait : ils ne commandent plus le cadrage — une rémunération à
        zéro écraserait les neuf dixièmes de l'effectif sur un centimètre —
        mais ils restent lisibles."""
        from hr_analytics.core.reporting import format_money

        textes = self._scale_texts()
        salary = self.app.result.payload["salary"]
        bas = [t for t in textes if t.startswith("min")]
        haut = [t for t in textes if t.startswith("max")]
        self.assertTrue(bas and haut)
        self.assertIn(format_money(salary["min"], "EUR"), bas[0])
        self.assertIn(format_money(salary["max"], "EUR"), haut[0])
        # Et le cadrage, lui, s'arrete aux percentiles publies.
        points = self._scale().points()
        self.assertLess(points[0][2], points[-1][2])
        self.assertGreater(points[0][2], salary["min"])

    def test_the_median_is_set_apart(self):
        """Le chiffre que l'on cherche en premier est mis en avant, plutot
        que signale par une couleur de fond."""
        import tkinter.font as tkfont
        from hr_analytics.core.reporting import format_money
        from hr_analytics.ui.theme import ACCENT, INK

        chart = self._scale()
        canvas = chart.canvas
        mediane = self.app.result.payload["salary"]["median"]
        attendu = format_money(mediane, "EUR")
        for item in canvas.find_all():
            if canvas.type(item) != "text":
                continue
            if canvas.itemcget(item, "text") != attendu:
                continue
            self.assertEqual(canvas.itemcget(item, "fill"), INK)
            weight = tkfont.Font(root=self.app,
                                 font=canvas.itemcget(item, "font")
                                 ).actual("weight")
            self.assertEqual(weight, "bold")
            break
        else:
            self.fail("médiane introuvable dans l'échelle")
        # Son intitule porte la couleur d'accent, les autres le gris.
        self.assertIn(ACCENT, [canvas.itemcget(item, "fill")
                               for item in canvas.find_all()
                               if canvas.type(item) == "text"])

    def test_the_page_holds_three_columns_when_it_can(self):
        """Le desequilibre, et non le contenu, faisait deborder la page : la
        colonne de population portait la liste, le camembert et les deux
        pyramides pendant que celle de remuneration s'arretait au tiers de
        la hauteur. Les pyramides prennent donc une colonne a elles."""
        from hr_analytics.ui.charts import PyramidChart, PieChart, ScaleChart

        def colonne(widget):
            """Le cadre de premier rang qui porte ce widget."""
            colonnes = self.app.overview_frame.winfo_children()[-1]
            parent = widget
            while parent is not None and parent.master is not colonnes:
                parent = parent.master
            return parent

        def premier(classe):
            def walk(widget):
                yield widget
                for child in widget.winfo_children():
                    yield from walk(child)
            return next(item for item in walk(self.app.overview_frame)
                        if isinstance(item, classe))

        pyramide = colonne(premier(PyramidChart))
        camembert = colonne(premier(PieChart))
        echelle = colonne(premier(ScaleChart))
        self.assertIsNotNone(pyramide)
        # Trois colonnes distinctes : population, remuneration, structures.
        self.assertNotEqual(str(pyramide), str(camembert))
        self.assertNotEqual(str(pyramide), str(echelle))
        self.assertNotEqual(str(camembert), str(echelle))
        # Et dans cet ordre : les pyramides au bout, parce qu'elles sont le
        # bloc le plus haut.
        colonnes = self.app.overview_frame.winfo_children()[-1]
        posees = [str(enfant) for enfant in colonnes.winfo_children()
                  if enfant.winfo_manager()]
        self.assertEqual(posees.index(str(camembert)), 0)
        self.assertEqual(posees.index(str(echelle)), 1)
        self.assertEqual(posees.index(str(pyramide)), 2)

    def _column_heights(self):
        colonnes = self.app.overview_frame.winfo_children()[-1]
        return [enfant.winfo_reqheight()
                for enfant in colonnes.winfo_children()
                if enfant.winfo_manager()]

    def test_the_whole_page_fits_without_scrolling(self):
        """La demande meme : tenir sur un ecran, sans descendre."""
        offert = self.app.overview_canvas.winfo_height()
        hauteurs = self._column_heights()
        self.assertTrue(hauteurs)
        self.assertLessEqual(max(hauteurs), offert)

    def test_the_page_uses_the_height_it_has(self):
        """L'autre moitie de la demande : dimensionnee pour le pire cas, la
        page laissait un tiers de hauteur vide sur un grand ecran. Elle rend
        cette place a ses graphiques, puis l'ecarte entre les blocs."""
        offert = self.app.overview_canvas.winfo_height()
        self.assertGreater(max(self._column_heights()), offert * 0.75)

    def test_breathing_is_bounded(self):
        """Rendre la place ne veut pas dire un anneau de la taille d'une
        assiette : chaque respiration a sa borne."""
        from hr_analytics.ui.charts import PieChart, PyramidChart, ScaleChart

        self.app.geometry("1600x1600+0+0")
        for _ in range(20):
            self.app.update()
            time.sleep(0.01)
        anneaux = self.app._of_type(self.app.overview_frame, PieChart)
        pyramides = self.app._of_type(self.app.overview_frame, PyramidChart)
        echelles = self.app._of_type(self.app.overview_frame, ScaleChart)
        self.assertTrue(anneaux and pyramides and echelles)
        self.assertLessEqual(anneaux[0].RADIUS, self.app.PIE_RADIUS_MAX)
        self.assertLessEqual(pyramides[0].ROW, self.app.PYRAMID_ROW_MAX)
        self.assertLessEqual(echelles[0].HEIGHT, self.app.SCALE_HEIGHT_MAX)

    def test_the_spacing_never_accumulates(self):
        """Ajoute a l'ecart precedent, il grandirait a chaque
        redimensionnement jusqu'a disloquer la page."""
        for largeur in (1500, 1600, 1500, 1600):
            self.app.geometry(f"{largeur}x1000+0+0")
            for _ in range(12):
                self.app.update()
                time.sleep(0.01)
        premier = max(self._column_heights())
        for _ in range(3):
            self.app._fit_overview()
            self.app.update()
        self.assertEqual(max(self._column_heights()), premier)

    def test_the_csp_breakdown_names_the_column_it_used(self):
        """« CSP » est le mot du metier, « Statut » la colonne du fichier :
        sans les deux, on ne sait pas ce qu'on regarde."""
        texts = [item.cget("text")
                 for item in self._all_labels(self.app.overview_frame)]
        self.assertIn("Répartition par CSP", texts)
        label = self.app.result.payload["population"]["csp_label"]
        self.assertIn(f"Champ : {label}", texts)

    def test_the_csp_breakdown_counts_what_the_engine_counted(self):
        """Un ecran qui parcourt lui-meme la population finit par compter
        autrement que le moteur, et deux chiffres du meme nom se
        contredisent."""
        from hr_analytics.ui.charts import PieChart

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        chart = next(item for item in walk(self.app.overview_frame)
                     if isinstance(item, PieChart))
        self.assertEqual(sum(n for _l, n in chart.slices),
                         self.app.result.payload["population"]["headcount"])

    def test_a_page_composed_before_it_had_a_width_still_gets_three_columns(self):
        """Le defaut signale en plein ecran : la page se composait pendant
        que son onglet n'avait jamais ete affiche — donc un pixel de large —
        et se figeait a deux colonnes pour le reste de la session.

        Elle suit desormais la largeur : composee sans la connaitre, elle se
        redispose au premier redimensionnement.
        """
        from hr_analytics.ui.app import Application
        from hr_analytics.core.pipeline import AnalysisRequest, run_analysis

        app = Application(config_dir=fresh_config())
        app.update()
        app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=self.source, reference_date=REFERENCE_DATE))
        try:
            # Compose alors que rien n'a de taille : c'est le cas reel d'un
            # resultat rendu avant que l'onglet ait ete ouvert.
            app._show_overview(app.result.payload)
            app.geometry("1600x1000+0+0")
            for _ in range(15):
                app.update()
                time.sleep(0.01)
            colonnes = app.overview_frame.winfo_children()[-1]
            posees = [enfant for enfant in colonnes.winfo_children()
                      if enfant.winfo_manager()]
            self.assertEqual(len(posees), 3)
            self.assertEqual(app._overview_columns, 3)
        finally:
            app.destroy()

    def test_the_layout_follows_the_window_both_ways(self):
        """Elargir doit rendre la troisieme colonne, retrecir la reprendre."""
        self.app.geometry("900x1000+0+0")
        for _ in range(15):
            self.app.update()
            time.sleep(0.01)
        self.assertEqual(self.app._overview_columns, 2)
        self.app.geometry("1600x1000+0+0")
        for _ in range(15):
            self.app.update()
            time.sleep(0.01)
        self.assertEqual(self.app._overview_columns, 3)

    def test_a_narrow_window_falls_back_to_two_columns(self):
        """Une colonne a besoin d'environ 330 px pour que la pyramide garde
        des ailes et l'echelle ses graduations. En dessous, mieux vaut deux
        colonnes et une page qui defile que trois colonnes rognees."""
        from hr_analytics.ui.charts import PyramidChart, ScaleChart

        self.app.geometry("900x1000+0+0")
        for _ in range(15):
            self.app.update()
            time.sleep(0.01)
        colonnes = self.app.overview_frame.winfo_children()[-1]
        posees = [enfant for enfant in colonnes.winfo_children()
                  if enfant.winfo_manager()]
        self.assertEqual(len(posees), 2)

        def colonne(classe):
            def walk(widget):
                yield widget
                for child in widget.winfo_children():
                    yield from walk(child)
            widget = next(item for item in walk(self.app.overview_frame)
                          if isinstance(item, classe))
            while widget is not None and widget.master is not colonnes:
                widget = widget.master
            return str(widget)

        # Les pyramides rejoignent la population ; la remuneration garde la
        # sienne.
        self.assertNotEqual(colonne(PyramidChart), colonne(ScaleChart))

    def test_the_coverage_is_said_when_something_is_missing(self):
        """Sur un fichier ou un quart des dates d'entree manque, la mediane
        affichee ne porte pas sur la population annoncee."""
        texts = [item.cget("text")
                 for item in self._all_labels(self.app.overview_frame)]
        population = self.app.result.payload["population"]
        if population["tenure_known"] >= population["headcount"]:
            # Couverture complete : la ligne n'apprend rien et ne doit pas
            # occuper une place.
            self.assertFalse(any("Ancienneté connue pour" in texte
                                 for texte in texts))
        else:
            self.assertTrue(any("Ancienneté connue pour" in texte
                                for texte in texts))

    def _pyramids(self):
        from hr_analytics.ui.charts import PyramidChart

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
        """La plus jeune tranche en bas, la plus agee au sommet : c'est la
        lecture attendue, et c'est le moteur qui publie cet ordre — tous
        les tableaux et tous les documents le partagent."""
        pyramid = self._pyramids()[0]
        self.assertTrue(pyramid.rows[-1]["label"].startswith("<"))
        self.assertTrue(pyramid.rows[0]["label"].startswith("6"))

    def _panel_texts(self, bandes, measure=""):
        import tkinter as tk

        cadre = tk.Frame(self.app)
        self.app._pyramid_panel(cadre, "Essai", bandes, None,
                                measure=measure)
        self.app.update()

        def walk(widget):
            yield widget
            for child in widget.winfo_children():
                yield from walk(child)
        textes = [item.cget("text") for item in walk(cadre)
                  if isinstance(item, tk.Label)]
        pyramides = [item for item in walk(cadre)
                     if type(item).__name__ == "PyramidChart"]
        cadre.destroy()
        return textes, pyramides

    def test_the_catch_all_band_leaves_the_pyramid_and_says_why(self):
        """Elle reservait une ligne et n'y dessinait rien. Et la fenetre
        annoncait « sexe non renseigne » des salaries qui en avaient un :
        ce qui leur manque, c'est une tranche — un age hors bornes, une
        anciennete absente —, pas un sexe."""
        bandes = [{"label": "20-29", "count": 10, "female": 6, "male": 4,
                   "unknown_sex": 0, "catch_all": False},
                  {"label": "(non renseigne)", "count": 3, "female": 2,
                   "male": 1, "unknown_sex": 0, "catch_all": True}]
        textes, pyramides = self._panel_texts(bandes, measure="d'âge")
        self.assertEqual([row["label"] for row in pyramides[0].rows],
                         ["20-29"])
        self.assertTrue(any("3 salariés sans tranche d'âge" in texte
                            for texte in textes))
        self.assertFalse(any("sexe non renseigné" in texte
                             for texte in textes))

    def test_an_unknown_sex_is_said_as_such_and_separately(self):
        """Ceux-la ont bien une tranche, mais aucune aile : ils sont dans le
        graphique sans y etre dessines."""
        bandes = [{"label": "20-29", "count": 12, "female": 6, "male": 4,
                   "unknown_sex": 2, "catch_all": False}]
        textes, _pyramides = self._panel_texts(bandes)
        self.assertTrue(any("2 salariés au sexe non renseigné" in texte
                            for texte in textes))
        self.assertFalse(any("sans tranche" in texte for texte in textes))

    def test_nothing_is_said_when_there_is_nothing_to_say(self):
        """La ligne ne parait que lorsqu'elle a quelque chose a dire."""
        textes, _pyramides = self._panel_texts(
            [{"label": "20-29", "count": 10, "female": 6, "male": 4,
              "unknown_sex": 0, "catch_all": False}])
        self.assertFalse(any("sexe non renseigné" in texte
                             for texte in textes))
        self.assertFalse(any("sans tranche" in texte for texte in textes))

    def test_every_tenure_band_is_present(self):
        """Le decoupage s'etend selon les carrieres presentes."""
        labels = [row["label"] for row in self._pyramids()[-1].rows]
        self.assertGreater(len(labels), 5)
        # La plus longue anciennete au sommet, comme l'age.
        self.assertTrue(labels[0].startswith(">"))
        self.assertTrue(labels[-1].startswith("<"))

    def test_a_file_without_sex_falls_back_to_plain_bars(self):
        """Sans la colonne « Sexe », une pyramide n'aurait qu'une aile."""
        from hr_analytics.ui.charts import PyramidChart

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

    Un filtre ne remplace pas cette comparaison : filtrer sur un groupe donne
    la population d'un groupe, pas l'ecart entre les huit.
    """

    def setUp(self):
        from hr_analytics.ui.app import Application
        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, business_unit=["France", "DACH"][index % 2],
                     groupe=["G3", "G5", "G7"][index % 3],
                     gender=["F", "H"][index % 2],
                     age=28 + index % 30, tenure=index % 15)
            for index in range(120)])])
        self.app = Application(config_dir=fresh_config())
        self.app.update()
        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
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
        for expected in ("business_unit", "groupe", "gender", "age_band",
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
                  if block["field"] == "groupe"][0]
        self.assertGreater(len(grades["rows"]), 1)
        self.assertIsNotNone(grades["reference_median"])




@needs_display
class TestTheOverviewLeavesNoGapInTheMiddle(unittest.TestCase):
    """Le bloc court ne doit pas creuser un trou au milieu de la page.

    Dans une grille, la rangee prend la hauteur du plus grand des deux
    blocs : la pyramide des ages, plus courte que l'echelle de
    remuneration, laissait un vide sous elle et repoussait la structure
    d'anciennete vers le bas. Les colonnes sont empilees separement.
    """

    def setUp(self):
        from hr_analytics.ui.app import Application
        from hr_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        directory = tempfile.mkdtemp()
        # Conserve : un test compose la page une seconde fois, sur une
        # fenetre qui n'a pas encore de taille.
        source = self.source = os.path.join(directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, salary=25000 + (index % 50) * 2000,
                     age=25 + index % 38, tenure=index % 32,
                     gender=["F", "H"][index % 2])
            for index in range(200)])])
        self.app = Application(config_dir=fresh_config())
        self.app.update()
        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=source, reference_date=REFERENCE_DATE))
        self.app._render_results()
        self.app.update_idletasks()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _panels(self):
        from hr_analytics.ui.charts import PyramidChart

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


@needs_display
class TestNoTkCallbackEverRaises(unittest.TestCase):
    """Aucun rappel Tk ne doit lever, sur tout le parcours.

    Tk attrape l'exception d'un rappel et l'imprime : la fenetre continue
    de repondre, et rien n'echoue. C'est exactement ce qui rend cette
    famille de defauts invisible — un parcours automatise peut annoncer
    « zero exception » pendant que la console de l'utilisateur se remplit de
    traces. Le parcours d'audit de ce projet l'a fait.

    Ce test ecoute donc le canal ou ces traces partent, et non le
    deroulement du parcours. Le premier cas connu : la molette tournee
    alors qu'une liste deroulante est ouverte.
    """

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "population.xlsx")
        rows = [make_row(i, salary=30000 + (i % 40) * 800,
                         business_unit=["France", "DACH"][i % 2],
                         groupe=["G3", "G5", "G7"][i % 3])
                for i in range(80)]
        write_workbook(cls.source, [("Population", [HEADERS] + rows)])

    def setUp(self):
        from hr_analytics.ui.app import Application

        self.app = Application(config_dir=fresh_config())
        self.traces = []
        self.app.report_callback_exception = (
            lambda *infos: self.traces.append(infos))
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _listes(self):
        """Les listes deroulantes de la fenetre, a plat."""
        from tkinter import ttk

        trouvees = []
        a_voir = [self.app]
        while a_voir:
            widget = a_voir.pop()
            a_voir.extend(widget.winfo_children())
            if isinstance(widget, ttk.Combobox):
                trouvees.append(widget)
        return trouvees

    def test_the_wheel_raises_nothing_over_an_open_list(self):
        listes = self._listes()
        self.assertTrue(listes, "la fenêtre doit proposer des listes")
        for liste in listes[:4]:
            with self.subTest(liste=str(liste)):
                popdown = self.app.tk.call(
                    "ttk::combobox::PopdownWindow", liste)
                self.app.tk.call("wm", "deiconify", popdown)
                self.app.update()
                x = int(self.app.tk.call("winfo", "rootx", popdown)) + 5
                y = int(self.app.tk.call("winfo", "rooty", popdown)) + 5
                for delta in (-120, 120):
                    self.app.event_generate("<MouseWheel>", delta=delta,
                                            x=5, y=5, rootx=x, rooty=y)
                self.app.update()
                self.app.tk.call("wm", "withdraw", popdown)
        self.assertEqual(
            [f"{t[0].__name__}: {t[1]}" for t in self.traces], [],
            "un rappel Tk a levé : la console de l'utilisateur porterait "
            "une trace à chaque cran de molette")

    def test_the_wheel_raises_nothing_anywhere_on_the_window(self):
        """La molette promenee sur toute la fenetre, liste fermee."""
        self.app.update()
        largeur = max(self.app.winfo_width(), 200)
        hauteur = max(self.app.winfo_height(), 200)
        base_x, base_y = self.app.winfo_rootx(), self.app.winfo_rooty()
        for fraction_x in (0.1, 0.4, 0.7, 0.95):
            for fraction_y in (0.1, 0.4, 0.7, 0.95):
                self.app.event_generate(
                    "<MouseWheel>", delta=-120, x=5, y=5,
                    rootx=base_x + int(largeur * fraction_x),
                    rooty=base_y + int(hauteur * fraction_y))
        self.app.update()
        self.assertEqual([f"{t[0].__name__}: {t[1]}" for t in self.traces], [])


@needs_display
class TestTheWholeWindowAnswersWithoutRaising(unittest.TestCase):
    """Toute la fenetre parcourue, reglage par reglage.

    Tk attrape l'exception d'un rappel et l'imprime : la fenetre continue de
    repondre, et aucun test ne le voit. Ce parcours ecoute donc le canal ou
    ces traces partent, et il touche a tout ce qui se touche — les quatre
    onglets, les trois graphiques, chaque liste deroulante a chacune de ses
    valeurs, chaque case, le repli de la colonne de gauche.

    Il ne verifie aucun chiffre : d'autres tests s'en chargent. Il verifie
    qu'aucun geste ne laisse une trace dans la console de l'utilisateur.
    """

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "population.xlsx")
        rows = [make_row(index, salary=30000 + (index % 40) * 800,
                         business_unit=["France", "DACH"][index % 2],
                         groupe=["G3", "G5", "G7"][index % 3],
                         gender="F" if index % 2 else "H",
                         age=25 + index % 35, tenure=(index % 18) / 1.4)
                for index in range(90)]
        write_workbook(cls.source, [("Population", [HEADERS] + rows)])

    def setUp(self):
        from hr_analytics.core.pipeline import load_population
        from hr_analytics.ui.app import Application

        self.app = Application(config_dir=fresh_config())
        self.traces = []
        self.app.report_callback_exception = (
            lambda *infos: self.traces.append(infos))
        population, mapping, table = load_population(self.source,
                                                     self.app.configuration)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app.headers = list(table.headers)
        self.app._populate_filters()
        self.app.run_analysis()
        limite = time.time() + 120
        while self.app.result is None and time.time() < limite:
            self.app.update()
            time.sleep(0.01)
        for _ in range(5):
            self.app.update()
            time.sleep(0.01)

    def tearDown(self):
        self.app.destroy()

    def _sans_trace(self, geste):
        self.assertEqual(
            [f"{t[0].__name__}: {t[1]}" for t in self.traces], [], geste)

    def _combos(self):
        from tkinter import ttk

        trouvees = []
        a_voir = [self.app]
        while a_voir:
            widget = a_voir.pop()
            a_voir.extend(widget.winfo_children())
            if isinstance(widget, ttk.Combobox):
                trouvees.append(widget)
        return trouvees

    def test_every_tab_and_every_chart_holds(self):
        from hr_analytics.ui.app import CHARTS, TABS

        for clef, _label in TABS:
            if clef not in self.app.tabbar.visible_keys():
                continue
            self.app.tabbar.select(clef)
            self.app.update()
            self._sans_trace(f"onglet {clef}")
        self.app.tabbar.select("graphique")
        for clef, _label in CHARTS:
            self.app.chartbar.select(clef)
            self.app.update()
            self._sans_trace(f"graphique {clef}")

    def test_every_value_of_every_list_holds(self):
        """Chaque liste, a chacune de ses valeurs."""
        for liste in self._combos():
            valeurs = list(liste.cget("values"))
            if not valeurs:
                continue
            initiale = liste.get()
            # Au plus six valeurs par liste : au-dela, c'est la meme
            # mecanique qui se repete, et le parcours durerait des minutes.
            for valeur in valeurs[:6]:
                liste.set(valeur)
                liste.event_generate("<<ComboboxSelected>>")
                self.app.update()
                self._sans_trace(f"{liste} = {valeur}")
            liste.set(initiale)
            liste.event_generate("<<ComboboxSelected>>")
            self.app.update()

    def test_folding_the_sidebar_holds(self):
        for _ in range(2):
            self.app.toggle_sidebar()
            limite = time.time() + 5
            while getattr(self.app, "_fold_job", None) and time.time() < limite:
                self.app.update()
                time.sleep(0.01)
            self.app.update()
            self._sans_trace("repli de la colonne de gauche")

    def test_resizing_holds(self):
        for largeur, hauteur in ((1000, 700), (1600, 1000), (860, 620)):
            self.app.geometry(f"{largeur}x{hauteur}+0+0")
            self.app.update()
            time.sleep(0.12)
            self.app.update()
            self._sans_trace(f"fenêtre {largeur}×{hauteur}")


@needs_display
class TestChoosingValuesInsideTheDispersionDimension(unittest.TestCase):
    """Choisir la dimension ne suffit pas. Trente-six établissements
    tiennent dans le graphique, mais la question posée à une dispersion
    est rarement « tous » : c'est « ces quatre-là, côte à côte », parce
    que c'est en les mettant côte à côte qu'on voit lequel a la grille la
    plus ouverte."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "population.xlsx")
        rows = [make_row(index, salary=30000 + (index % 40) * 800,
                         business_unit=["France", "DACH", "Iberia"][index % 3],
                         groupe=["G3", "G5", "G7"][index % 3],
                         age=28 + index % 30, tenure=index % 18)
                for index in range(120)]
        write_workbook(cls.source, [("Population", [HEADERS] + rows)])

    def setUp(self):
        from hr_analytics.ui.app import Application

        self.app = Application(config_dir=fresh_config())
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _prepare(self):
        """Une analyse, et l'onglet des boîtes au premier plan."""
        from hr_analytics.core.pipeline import AnalysisRequest, run_analysis

        self.app.result = run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
            source_path=self.source, reference_date=REFERENCE_DATE,
            segments=[]))
        self.app._render_results()
        self.app.tabbar.select("graphique")
        self.app.update()
        for rang, _bloc in enumerate(self.app._segments):
            self.app.box_choice.current(rang)
            self.app._change_box_dimension()
            self.app.update()
            if len(self.app._box_values_available()) >= 2:
                return self.app._box_values_available()
        self.skipTest("aucune dimension à plusieurs valeurs")

    def test_by_default_every_value_is_drawn(self):
        valeurs = self._prepare()
        self.assertIsNone(self.app.box_values)
        self.assertIn("toutes", self.app.box_values_button.cget("text"))
        self.assertEqual(len(self.app.boxplot.rows), len(valeurs))

    def test_retaining_two_values_draws_two(self):
        valeurs = self._prepare()
        self.app._apply_box_values(valeurs[:2])
        self.app.update()
        tracés = {str(row.get("segment")) for row in self.app.boxplot.rows}
        self.assertEqual(tracés, set(valeurs[:2]))
        self.assertIn("2 sur", self.app.box_values_button.cget("text"))

    def test_retaining_none_draws_nothing_and_says_so(self):
        """Ne rien retenir n'est pas « tout retenir » : c'est un graphique
        vide, et c'est ce qui a été demandé. Le bouton le dit, de sorte
        qu'un graphique vide ne passe pas pour une panne."""
        self._prepare()
        self.app._apply_box_values([])
        self.app.update()
        self.assertEqual(self.app.boxplot.rows, [])
        self.assertIn("0 sur", self.app.box_values_button.cget("text"))

    def test_changing_the_dimension_clears_the_selection(self):
        """Les postes retenus ne sont pas des établissements : garder la
        sélection viderait le graphique sans que rien ne le dise."""
        valeurs = self._prepare()
        self.app._apply_box_values(valeurs[:1])
        self.app.update()
        self.assertIsNotNone(self.app.box_values)
        self.app._change_box_dimension()
        self.app.update()
        self.assertIsNone(self.app.box_values)

    def test_the_picker_hands_back_none_when_everything_is_kept(self):
        """Tout retenir, c'est ne rien filtrer : le sélecteur rend None
        plutôt qu'une liste complète, pour que l'appelant n'ait pas à
        comparer."""
        from hr_analytics.ui.theme import ValuePicker

        valeurs = self._prepare()
        rendu = []
        choix = ValuePicker(self.app, self.app.fonts, "Essai", valeurs,
                            None, rendu.append)
        self.app.update()
        try:
            choix._valider()
        finally:
            if choix.winfo_exists():
                choix.destroy()
        self.assertEqual(rendu, [None])

    def test_the_picker_unchecks_everything_at_once(self):
        """Décocher trente valeurs une par une est le geste que cette
        fenêtre doit épargner : deux boutons, et non deux mots soulignés
        dont il faut deviner qu'ils agissent."""
        from hr_analytics.ui.theme import ValuePicker

        valeurs = self._prepare()
        choix = ValuePicker(self.app, self.app.fonts, "Essai", valeurs,
                            None, lambda _r: None)
        self.app.update()
        try:
            self.assertEqual(choix._boutons[False].winfo_class(), "TButton")
            self.assertEqual(choix._boutons[False].cget("text"),
                             "Tout décocher")
            choix._boutons[False].invoke()
            self.app.update()
            self.assertEqual(choix._retenues(), [])
            choix._boutons[True].invoke()
            self.app.update()
            self.assertEqual(choix._retenues(), list(valeurs))
        finally:
            if choix.winfo_exists():
                choix.destroy()

    def test_the_buttons_say_they_only_touch_what_shows(self):
        """« Tout cocher » ne coche que ce que la recherche laisse voir :
        le bouton le dit, sinon l'action paraît porter sur la liste
        entière."""
        from hr_analytics.ui.theme import ValuePicker

        valeurs = self._prepare()
        choix = ValuePicker(self.app, self.app.fonts, "Essai", valeurs,
                            None, lambda _r: None)
        self.app.update()
        try:
            choix._cherche.set(valeurs[0][:3])
            self.app.update()
            self.assertEqual(choix._boutons[False].cget("text"),
                             "Décocher ce qui s'affiche")
            choix._boutons[False].invoke()
            self.app.update()
            # Ce que la recherche cache n'a pas bougé.
            self.assertNotIn(valeurs[0], choix._retenues())
            choix._cherche.set("")
            self.app.update()
            self.assertEqual(choix._boutons[False].cget("text"),
                             "Tout décocher")
        finally:
            if choix.winfo_exists():
                choix.destroy()

    def test_the_picker_searches_without_accents(self):
        from hr_analytics.ui.theme import ValuePicker

        valeurs = self._prepare()
        choix = ValuePicker(self.app, self.app.fonts, "Essai", valeurs,
                            None, lambda _r: None)
        self.app.update()
        try:
            cible = valeurs[0]
            choix._cherche.set(cible.lower()[:3])
            self.app.update()
            visibles = [v for v, ligne in choix._lignes.items()
                        if ligne.winfo_manager()]
            self.assertIn(cible, visibles)
            choix._cherche.set("zzzz-introuvable")
            self.app.update()
            self.assertEqual([v for v, ligne in choix._lignes.items()
                              if ligne.winfo_manager()], [])
        finally:
            if choix.winfo_exists():
                choix.destroy()
