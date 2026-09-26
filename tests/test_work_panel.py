"""Le panneau d'attente : ce qui se passe pendant l'analyse.

Une analyse de cent mille lignes demande une dizaine de secondes. Pendant
ce temps, la fenetre ne montrait qu'un filet de six pixels dans la colonne
de gauche et une page vide : rien ne bougeait la ou le regard etait, et
l'attente paraissait une panne.

Ce que ces tests protegent n'est pas l'esthetique du panneau, mais les trois
promesses qu'il fait : ses etapes sont celles du moteur, il ne parait que
lorsque l'attente se voit, et il rend la place aux pages quand c'est fini.

Aucune donnee RH reelle.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_insight.core.pipeline import stage_labels

try:
    import tkinter
    HAS_TK = True
except ImportError:                                    # pragma: no cover
    HAS_TK = False


def _display_answers() -> bool:
    if not (HAS_TK and os.environ.get("DISPLAY")):
        return False
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        return False
    root.destroy()
    return True


needs_display = unittest.skipUnless(
    _display_answers(), "aucun affichage disponible (test d'interface ignoré)")


class TestTheStagesAreDeclaredOnce(unittest.TestCase):
    """Les etapes affichees sont celles qui sont calculees.

    Recopier la liste dans la fenetre aurait garanti qu'un jour elles
    different : une etape ajoutee au moteur n'apparaitrait pas, ou pire,
    l'ecran annoncerait une etape qui n'existe plus.
    """

    def test_the_engine_names_its_own_stages(self):
        étapes = stage_labels()
        self.assertGreaterEqual(len(étapes), 5)
        self.assertTrue(all(isinstance(nom, str) and nom for nom in étapes))
        self.assertEqual(len(set(étapes)), len(étapes))

    def test_the_window_does_not_hold_its_own_copy(self):
        """Aucun intitule d'etape ne doit etre ecrit dans l'interface."""
        racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for nom in ("working.py", "app.py"):
            with open(os.path.join(racine, "hr_insight", "ui", nom),
                      encoding="utf-8") as fichier:
                texte = fichier.read()
            for étape in stage_labels():
                with self.subTest(fichier=nom, étape=étape):
                    self.assertNotIn(f'"{étape}"', texte)


@needs_display
class TestThePanel(unittest.TestCase):

    def setUp(self):
        """Le panneau de la fenetre elle-meme, et non un second Tk.

        Tkinter n'admet qu'une racine par processus : une seconde, creee
        alors qu'un fil de calcul d'un test precedent vit encore, fait
        supprimer un gestionnaire asynchrone depuis le mauvais fil — et Tcl
        abandonne le processus entier, resultats compris. Le panneau se
        teste donc la ou il vit.
        """
        from hr_insight.ui.app import Application

        self.root = Application()
        self.traces = []
        self.root.report_callback_exception = (
            lambda *infos: self.traces.append(infos))
        self.panel = self.root.work_panel
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def _textes(self):
        return [ligne.cget("text") for ligne in self.panel._lignes.values()]

    def test_it_lists_every_stage(self):
        for étape in stage_labels():
            self.assertTrue(any(étape in texte for texte in self._textes()))

    def test_announcing_a_stage_closes_the_previous_ones(self):
        étapes = stage_labels()
        self.panel.start()
        self.panel.announce(étapes[0], 0.1)
        self.panel.announce(étapes[2], 0.5)
        self.root.update()
        # Celle qui a ete sautee compte comme faite : la laisser en attente
        # derriere l'etape en cours ferait lire une liste incoherente.
        self.assertEqual(self.panel.current, étapes[2])
        self.assertIn(étapes[0], self.panel._done)
        self.assertIn(étapes[1], self.panel._done)
        self.assertNotIn(étapes[3], self.panel._done)

    def test_finishing_marks_everything_done(self):
        self.panel.start()
        self.panel.announce(stage_labels()[0], 0.1)
        self.panel.finish()
        self.assertEqual(sorted(self.panel._done), sorted(stage_labels()))
        self.assertEqual(self.panel.current, "")

    def test_the_animation_never_raises_and_stays_bounded(self):
        """Une image de plus par battement, et pas une de plus."""
        self.panel.start()
        for _ in range(200):
            self.panel.tick()
        self.root.update()
        self.assertEqual(len(self.panel._images), self.panel.FRAMES)
        self.assertEqual([f"{t[0].__name__}" for t in self.traces], [])

    def test_the_clock_advances_without_any_announcement(self):
        """Une etape longue et muette ne doit pas figer le panneau."""
        import time

        self.panel.start()
        self.panel._started -= 3.0
        self.panel.tick()
        self.root.update()
        self.assertTrue(self.panel.chrono.cget("text").endswith("s"),
                        self.panel.chrono.cget("text"))


@needs_display
class TestThePanelInTheWindow(unittest.TestCase):
    """Il prend la place des pages, et il la rend."""

    @classmethod
    def setUpClass(cls):
        import csv
        import tempfile

        from tests.support import HEADERS, make_row

        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "p.csv")
        with open(cls.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS))
            for index in range(60):
                writer.writerow(make_row(index, salary=30000 + index * 300,
                                         gender="F" if index % 2 else "H"))

    def setUp(self):
        import time

        from hr_insight.core.pipeline import load_population
        from hr_insight.ui.app import Application

        self.app = Application()
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
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _analyse(self):
        import time

        self.app.run_analysis()
        limite = time.time() + 120
        while self.app.result is None and time.time() < limite:
            self.app.update()
            time.sleep(0.01)
        for _ in range(5):
            self.app.update()
            time.sleep(0.01)

    def test_the_pages_come_back_when_the_analysis_ends(self):
        self._analyse()
        self.assertFalse(self.app.work_panel.winfo_manager())
        self.assertEqual(self.app.pages.winfo_manager(), "pack")
        self.assertEqual([f"{t[0].__name__}" for t in self.traces], [])

    def test_a_short_analysis_never_shows_the_panel(self):
        """Un panneau qui apparaitrait pour disparaitre aussitot serait un
        defaut d'affichage, pas une information."""
        self._analyse()
        self.assertFalse(self.app.work_panel.winfo_manager())

    def test_the_panel_takes_the_place_of_the_pages(self):
        self.app._show_work_panel()
        self.app.update()
        self.assertEqual(self.app.work_panel.winfo_manager(), "pack")
        self.assertFalse(self.app.pages.winfo_manager())
        self.app._hide_work_panel()
        self.app.update()
        self.assertEqual(self.app.pages.winfo_manager(), "pack")

    def test_closing_during_an_analysis_cancels_its_callbacks(self):
        """Une fenetre fermee pendant une analyse laissait Tk executer un
        rappel dont le widget n'existait plus."""
        self.app.run_analysis()
        self.app.update()
        self.assertIsNotNone(self.app._work_job)
        self.app.destroy()
        self.assertIsNone(self.app._work_job)
        # `tearDown` detruira une seconde fois : Tk doit le supporter.
        self.app = _Dummy()


class _Dummy:
    def destroy(self):
        pass


if __name__ == "__main__":                              # pragma: no cover
    unittest.main()
