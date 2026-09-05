"""Les themes ne doivent pas pouvoir degrader l'outil.

L'utilisateur ne saisit aucune couleur : il choisit un jeu dans une liste
fermee. Encore faut-il que chaque jeu tienne ses promesses — un contraste
suffisant pour lire, des severites qui gardent leur sens, un couple femmes
/ hommes qui reste distinguable. Ces tests le verifient theme par theme,
pour qu'un jeu ajoute demain ne passe pas sans etre mesure.

Aucune donnee RH reelle n'est utilisee.
"""

import datetime as _dt
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, REFERENCE_DATE, make_row
from tests.test_ui import needs_display
from compensation_analytics.core import palette, reporting, slides
from compensation_analytics.core.config import (CONFIG_FILES, DEFAULTS,
                                                load_configuration)
from compensation_analytics.io.xlsx_writer import write_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Seuils WCAG. AAA pour le texte courant, AA pour le secondaire.
BODY_CONTRAST = 7.0
SECONDARY_CONTRAST = 4.5


class TestEveryThemeStaysReadable(unittest.TestCase):

    def themes(self):
        return palette.THEMES.values()

    def test_the_text_contrasts_enough_with_the_background(self):
        for theme in self.themes():
            pal = theme.palette
            with self.subTest(theme=theme.key):
                self.assertGreaterEqual(
                    palette.contrast(pal.ink, pal.canvas), BODY_CONTRAST)
                self.assertGreaterEqual(
                    palette.contrast(pal.ink_soft, pal.canvas), BODY_CONTRAST)
                self.assertGreaterEqual(
                    palette.contrast(pal.muted, pal.canvas), SECONDARY_CONTRAST)

    def test_white_stays_legible_on_the_accent(self):
        """Le bouton principal ecrit en blanc sur l'accent."""
        for theme in self.themes():
            with self.subTest(theme=theme.key):
                self.assertGreaterEqual(
                    palette.contrast(theme.palette.canvas, theme.palette.accent),
                    SECONDARY_CONTRAST)
                self.assertGreaterEqual(
                    palette.contrast(theme.palette.canvas,
                                     theme.palette.accent_hover),
                    SECONDARY_CONTRAST)

    def test_the_severities_never_follow_the_theme(self):
        """Du vert sur « critique » serait un contresens, pas une preference."""
        for theme in self.themes():
            with self.subTest(theme=theme.key):
                self.assertEqual(theme.palette.warn, palette.WARN)
                self.assertEqual(theme.palette.crit, palette.CRIT)
                self.assertEqual(theme.palette.ok, palette.OK)

    def test_the_two_sexes_stay_the_same_distinguishable_pair(self):
        """Bleu et orange : le seul couple sur lequel un deutan ne se trompe pas."""
        for theme in self.themes():
            with self.subTest(theme=theme.key):
                self.assertEqual(theme.palette.female, palette.FEMALE)
                self.assertEqual(theme.palette.male, palette.MALE)
        self.assertGreater(palette.distance(palette.FEMALE, palette.MALE), 100)

    def test_the_series_never_repeat_the_accent(self):
        for theme in self.themes():
            series = theme.palette.series
            with self.subTest(theme=theme.key):
                self.assertGreaterEqual(len(series), 8)
                self.assertEqual(series[0], theme.palette.accent)
                self.assertGreaterEqual(
                    min(palette.distance(series[0], other)
                        for other in series[1:]), palette.SERIES_GAP)

    def test_the_neutrals_go_from_dense_to_light_without_crossing(self):
        """Une hierarchie de lecture inversee ferait ressortir l'accessoire."""
        for theme in self.themes():
            pal = theme.palette
            ordered = (pal.ink, pal.ink_soft, pal.muted, pal.faint,
                       pal.disabled, pal.line_strong, pal.line, pal.grid,
                       pal.panel, pal.stripe, pal.canvas)
            contrasts = [palette.contrast(colour, pal.canvas)
                         for colour in ordered]
            with self.subTest(theme=theme.key):
                self.assertEqual(contrasts, sorted(contrasts, reverse=True))


class TestChoosingAThemeCannotBreakTheTool(unittest.TestCase):

    def test_an_unknown_name_falls_back_instead_of_failing(self):
        """La configuration se modifie au bloc-notes : une faute de frappe
        ne doit pas empecher l'outil de s'ouvrir."""
        for name in ("bleu-ciel", "", None, "ARDOISE ", 42):
            with self.subTest(name=name):
                self.assertIsInstance(palette.by_name(name), palette.Palette)
        self.assertEqual(palette.by_name("inconnu").theme,
                         palette.DEFAULT_THEME)
        # Une casse ou un espace de trop restent compris.
        self.assertEqual(palette.by_name("ARDOISE ").theme, "ardoise")

    def test_the_shipped_configuration_names_a_real_theme(self):
        self.assertIn("theme_parameters", CONFIG_FILES)
        configured = DEFAULTS["theme_parameters"]["theme"]
        self.assertIn(configured, palette.THEMES)
        path = os.path.join(ROOT, "config", "theme_parameters.json")
        self.assertTrue(os.path.isfile(path), "theme_parameters.json absent")
        self.assertIn(load_configuration(os.path.join(ROOT, "config"))
                      .get("theme_parameters.theme"), palette.THEMES)

    def test_every_theme_key_is_ascii(self):
        """Les valeurs ecrites en configuration restent tapables partout."""
        for key in palette.THEMES:
            with self.subTest(key=key):
                self.assertTrue(key.isascii() and key.islower(), key)


class TestTheDocumentsFollowTheTheme(unittest.TestCase):
    """Une seule palette pour l'ecran et les documents, sans rien en dur."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        source = os.path.join(cls.directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS] + [
            make_row(index, salary=30000 + index * 41,
                     business_unit=["France", "DACH"][index % 2],
                     age=28 + index % 30, tenure=index % 18,
                     gender=["F", "H"][index % 2])
            for index in range(80)])])
        from compensation_analytics.core.pipeline import (AnalysisRequest,
                                                          run_analysis)
        cls.payload = run_analysis(AnalysisRequest(
            source_path=source, reference_date=REFERENCE_DATE,
            segments=[])).payload

    def _payload(self, theme_name):
        payload = dict(self.payload)
        payload["theme"] = theme_name
        return payload

    def test_the_analysis_carries_the_configured_theme(self):
        self.assertIn(self.payload["theme"], palette.THEMES)

    def test_the_report_is_tinted_by_the_theme(self):
        for name in palette.THEMES:
            html = reporting.render_report(self._payload(name))
            with self.subTest(theme=name):
                self.assertIn(f"--accent:{palette.by_name(name).accent}", html)

    def test_no_colour_is_written_outside_the_theme(self):
        """Toute teinte du rapport vient de la palette, sans exception.

        C'est ce test qui empeche la derive d'avant : quatre modules
        decrivaient leur propre bleu, et ils avaient fini par ne plus etre
        le meme.
        """
        for name in palette.THEMES:
            pal = palette.by_name(name)
            html = reporting.render_report(self._payload(name))
            variables = re.search(r":root\{[^}]*\}", html).group(0)
            body = html.replace(variables, "")
            known = {colour.lower() for colour in pal.series}
            stray = {found.lower() for found in re.findall(r"#[0-9a-fA-F]{6}", body)
                     if found.lower() not in known}
            with self.subTest(theme=name):
                self.assertEqual(stray, set(),
                                 "teintes ecrites hors du theme")

    def test_the_slides_are_tinted_in_html_and_in_pdf(self):
        from compensation_analytics.core.slides import (build_deck,
                                                        render_slides_html,
                                                        write_slides_pdf)
        for name in ("ardoise", "prune"):
            payload = self._payload(name)
            deck = build_deck(payload)
            html = render_slides_html(deck, payload)
            expected = palette.by_name(name)
            with self.subTest(theme=name, format="html"):
                self.assertIn(f"--accent:{expected.accent}", html)
            path = os.path.join(self.directory, f"{name}.pdf")
            write_slides_pdf(deck, payload, path)
            with self.subTest(theme=name, format="pdf"):
                # Les couleurs du PDF sont recalculees a chaque rendu : sans
                # cela, le second document garderait celles du premier.
                self.assertEqual(slides._ACCENT,
                                 slides._rgb(expected.accent))
                self.assertTrue(os.path.getsize(path) > 1000)

    def test_rendering_one_theme_then_another_leaves_no_trace(self):
        reporting.render_report(self._payload("prune"))
        html = reporting.render_report(self._payload("ardoise"))
        self.assertIn(f"--accent:{palette.by_name('ardoise').accent}", html)
        self.assertNotIn(palette.by_name("prune").accent, html)


@needs_display
class TestChoosingAThemeFromTheWindow(unittest.TestCase):
    """La bande « Apparence » enregistre le theme et rien d'autre."""

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

    def test_the_window_offers_every_theme_and_marks_the_current_one(self):
        window = self._window()
        try:
            self.assertEqual(set(window._theme_cards), set(palette.THEMES))
            self.assertEqual(window.theme_var.get(),
                             self.app.configuration.get(
                                 "theme_parameters.theme"))
        finally:
            window.destroy()

    def test_choosing_and_saving_writes_the_theme(self):
        window = self._window()
        try:
            window._choose_theme("foret")
            self.app.update()
            window.save()
            self.app.update()
        finally:
            if window.winfo_exists():
                window.destroy()
        reloaded = load_configuration(self.config_dir)
        self.assertEqual(reloaded.get("theme_parameters.theme"), "foret")
        # Le mapping n'a pas ete abime au passage : les deux sections sont
        # ecrites, pas l'une a la place de l'autre.
        self.assertTrue(reloaded.get("population_mapping.fields"))

    def test_the_window_opens_under_every_theme(self):
        """Un theme ne doit pas seulement s'enregistrer : il doit s'ouvrir."""
        import json
        from compensation_analytics.ui import theme as ui_theme
        from compensation_analytics.ui.app import Application
        for name in palette.THEMES:
            with self.subTest(theme=name):
                with open(os.path.join(self.config_dir,
                                       "theme_parameters.json"),
                          "w", encoding="utf-8") as handle:
                    json.dump({"theme": name}, handle)
                app = Application(config_dir=self.config_dir)
                try:
                    app.update()
                    self.assertEqual(ui_theme.ACTIVE.theme, name)
                    self.assertEqual(ui_theme.ACCENT,
                                     palette.by_name(name).accent)
                finally:
                    app.destroy()


if __name__ == "__main__":
    unittest.main()
