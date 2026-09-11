"""La barre de chargement, et l'avancement qui la nourrit.

Une barre saccadee n'est pas un defaut d'esthetique : pendant une analyse
de trente secondes, elle est le seul signe que l'outil travaille. Ce qui se
verifie ici n'est donc pas qu'elle s'affiche, mais qu'elle *bouge* — qu'une
image tardive ne la fasse pas ralentir, qu'une etape muette ne la fige pas,
et qu'aucune annonce ne la fasse reculer.

Aucune donnee RH reelle.
"""

import csv
import gc
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, make_row
from compensation_analytics.core.pipeline import (AnalysisRequest, _STAGES,
                                                  run_analysis)
from compensation_analytics.io.tabular import read_table
from compensation_analytics.io.xlsx_writer import write_workbook

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


class Horloge:
    """Horloge menee a la main : le temps d'un test ne doit pas dependre
    de la charge de la machine qui le joue."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def avance(self, secondes: float) -> None:
        self.now += secondes


@needs_display
class TestTheBarMovesOnTheClock(unittest.TestCase):

    def setUp(self):
        import tkinter as tk

        from compensation_analytics.ui import theme
        from compensation_analytics.ui.progress import LoadingBar
        from compensation_analytics.core.config import load_configuration

        self.root = tk.Tk()
        self.root.geometry("400x120")
        theme.load(load_configuration())
        theme.Fonts(self.root)
        self.horloge = Horloge()
        self.bar = LoadingBar(self.root, clock=self.horloge)
        self.bar.pack(fill="x")
        self.root.update()
        # L'animation est menee image par image dans les tests : la boucle
        # de Tk n'y a pas sa place.
        self.bar.start("Lecture")
        self.bar.stop()

    def tearDown(self):
        self.root.destroy()

    def images(self, duree, cadence):
        for _ in range(int(duree / cadence)):
            self.horloge.avance(cadence)
            self.bar.step()

    def test_a_late_frame_lands_where_the_clock_says(self):
        """Le defaut corrige : une barre qui avance d'un cran par image
        ralentit quand le fil principal est preempte. Dix images de dix
        millisecondes et une seule de cent doivent mener au meme endroit."""
        self.bar.announce("Lecture", 0.5)
        self.images(0.1, 0.01)
        fluide = self.bar.shown

        self.horloge.avance(-0.1)
        self.bar._shown = 0.0
        self.bar._last = self.horloge()
        self.horloge.avance(0.1)
        self.bar.step()
        # Tolerance : un demi-pixel sur une barre de trois cents, soit bien
        # moins que ce qu'un ecran sait montrer.
        self.assertLess(abs(fluide - self.bar.shown), 0.5 / 300)

    def test_it_never_goes_backwards(self):
        """Une annonce en retrait de ce qui est deja montre ne doit pas
        faire reculer le trait : la barre attend que le calcul la
        rattrape."""
        self.bar.announce("Lecture", 0.6)
        self.images(2.0, 0.016)
        haut = self.bar.shown
        self.bar.announce("Normalisation", 0.55)
        self.images(0.5, 0.016)
        self.assertGreaterEqual(self.bar.shown, haut)

    def test_a_silent_stage_still_advances(self):
        """Sans cette avance, la normalisation figeait la barre deux
        secondes et demie."""
        self.bar.announce("Normalisation", 0.5)
        positions = []
        for _ in range(120):                       # deux secondes a 60 Hz
            self.horloge.avance(0.016)
            self.bar.step()
            positions.append(self.bar.shown)
        # Strictement croissante, jamais immobile.
        for avant, apres in zip(positions, positions[1:]):
            self.assertGreater(apres, avant)
        self.assertGreater(positions[-1], 0.5)

    def test_the_lookahead_never_overtakes_the_next_stage(self):
        """Deviner trop loin ferait attendre la barre a chaque annonce."""
        self.bar.announce("Normalisation", 0.50)
        self.images(60.0, 0.016)
        self.assertLessEqual(self.bar.shown, 0.50 + self.bar.LOOKAHEAD + 1e-6)

    def test_it_stops_short_of_the_end_until_the_end(self):
        """Une barre pleine depuis trois secondes est un outil qui a l'air
        bloque."""
        self.bar.announce("Segments", 0.99)
        self.images(30.0, 0.016)
        self.assertLess(self.bar.shown, 1.0)
        self.bar.finish()
        self.assertEqual(self.bar.shown, 1.0)

    def test_an_announcement_is_joined_briskly(self):
        """Une annonce est un fait : la barre la rejoint sans trainer."""
        self.bar.announce("Lecture", 0.30)
        self.images(1.0, 0.016)
        self.assertGreater(self.bar.shown, 0.28)

    def test_stopping_cancels_the_animation(self):
        self.bar.start("Lecture")
        self.assertIsNotNone(self.bar._job)
        self.bar.stop()
        self.assertIsNone(self.bar._job)


class TestTheReaderReportsItsProgress(unittest.TestCase):
    """La lecture pese la moitie du temps d'une analyse : sans annonce, la
    barre reste immobile pendant dix secondes sur un gros fichier."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        lignes = [list(HEADERS)] + [make_row(index) for index in range(3000)]
        cls.xlsx = os.path.join(cls.directory, "p.xlsx")
        write_workbook(cls.xlsx, [("Population", lignes)])
        cls.csv = os.path.join(cls.directory, "p.csv")
        with open(cls.csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            for ligne in lignes:
                writer.writerow([str(cell) for cell in ligne])

    def _fractions(self, path):
        vues = []
        table = read_table(path, progress=vues.append)
        return table, vues

    def test_an_xlsx_reports_a_growing_fraction(self):
        table, vues = self._fractions(self.xlsx)
        self.assertEqual(table.row_count, 3000)
        self.assertTrue(vues)
        self.assertEqual(vues, sorted(vues))
        self.assertTrue(all(0.0 <= part <= 1.0 for part in vues))

    def test_a_csv_reports_a_growing_fraction(self):
        table, vues = self._fractions(self.csv)
        self.assertEqual(table.row_count, 3000)
        self.assertTrue(vues)
        self.assertEqual(vues, sorted(vues))
        self.assertTrue(all(0.0 <= part <= 1.0 for part in vues))

    def test_the_table_is_the_same_watched_or_not(self):
        """Le moteur lit un fichier de la meme facon, qu'une fenetre
        regarde ou non."""
        for path in (self.xlsx, self.csv):
            observee, _ = self._fractions(path)
            seule = read_table(path)
            self.assertEqual(observee.headers, seule.headers)
            self.assertEqual(observee.rows, seule.rows)


class TestTheAnalysisReportsItsStages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "p.csv")
        with open(cls.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS))
            for index in range(60):
                writer.writerow(make_row(index, salary=30000 + index * 700,
                                         gender="F" if index % 2 else "H"))

    def _run(self, report=None):
        return run_analysis(AnalysisRequest(source_path=self.source,
                                            progress=report))

    def test_the_weights_of_the_stages_make_a_whole(self):
        """Un total different de un ferait une barre qui n'atteint pas le
        bout, ou qui le depasse."""
        self.assertAlmostEqual(sum(weight for _k, _l, weight in _STAGES), 1.0)

    def test_the_fractions_only_ever_grow_and_end_at_one(self):
        vues = []
        self._run(lambda label, part: vues.append((label, part)))
        parts = [part for _label, part in vues]
        self.assertEqual(parts, sorted(parts))
        self.assertGreaterEqual(parts[0], 0.0)
        self.assertEqual(parts[-1], 1.0)

    def test_every_stage_names_itself(self):
        vues = []
        self._run(lambda label, part: vues.append(label))
        for _key, label, _weight in _STAGES:
            self.assertIn(label, vues)

    def test_a_broken_reporter_never_costs_the_analysis(self):
        """Un defaut d'affichage ne doit pas faire perdre un calcul de
        trente secondes."""
        def casse(_label, _part):
            raise RuntimeError("l'écran a disparu")

        result = self._run(casse)
        self.assertEqual(len(result.filtered), 60)
        self.assertIn("salary", result.payload)

    def test_an_analysis_without_a_reporter_is_unchanged(self):
        temoin = self._run()
        observee = self._run(lambda _label, _part: None)
        self.assertEqual(temoin.payload["salary"]["median"],
                         observee.payload["salary"]["median"])


class TestTheCycleCollectorIsSuspended(unittest.TestCase):
    """Mesure : 29,2 s avec, 22,1 s sans, pour un pic de memoire identique.
    Et surtout vingt-sept arrets visibles de la barre, contre un."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "p.csv")
        with open(cls.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS))
            for index in range(40):
                writer.writerow(make_row(index))

    def test_it_is_suspended_during_the_analysis(self):
        etats = []
        run_analysis(AnalysisRequest(
            source_path=self.source,
            progress=lambda _l, _p: etats.append(gc.isenabled())))
        self.assertTrue(etats)
        self.assertFalse(any(etats))

    def test_it_is_given_back_afterwards(self):
        actif = gc.isenabled()
        run_analysis(AnalysisRequest(source_path=self.source))
        self.assertEqual(gc.isenabled(), actif)

    def test_it_is_given_back_even_when_the_analysis_fails(self):
        actif = gc.isenabled()
        with self.assertRaises(Exception):
            run_analysis(AnalysisRequest(source_path=self.source + ".absent"))
        self.assertEqual(gc.isenabled(), actif)

    def test_a_disabled_collector_stays_disabled(self):
        """L'etat d'origine est restaure, pas un etat suppose."""
        gc.disable()
        try:
            run_analysis(AnalysisRequest(source_path=self.source))
            self.assertFalse(gc.isenabled())
        finally:
            gc.enable()


@needs_display
class TestTheWindowDrivesTheBar(unittest.TestCase):
    """Le fil de calcul annonce, le fil qui dessine releve : Tk n'est pas
    sur pour deux fils, et une barre touchee depuis le calcul ferait tomber
    la fenetre sans rien dire."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "p.xlsx")
        lignes = [list(HEADERS)] + [
            make_row(index, salary=30000 + index * 500,
                     gender="F" if index % 2 else "H")
            for index in range(400)]
        write_workbook(cls.source, [("Population", lignes)])

    def setUp(self):
        import time

        from compensation_analytics.ui.app import Application
        from compensation_analytics.ui.progress import LoadingBar
        from compensation_analytics.core.pipeline import load_population

        self.annonces = []
        self.originale = LoadingBar.announce

        def espion(bar, label, part):
            self.annonces.append((label, part))
            self.originale(bar, label, part)

        LoadingBar.announce = espion
        self.addCleanup(setattr, LoadingBar, "announce", self.originale)
        self.app = Application()
        self.app.update()
        population, mapping, table = load_population(
            self.source, self.app.configuration)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app.headers = list(table.headers)
        self.app._populate_filters()
        self.app.analyse_button.state(["!disabled"])
        self.attendre = time
        self.addCleanup(self.app.destroy)

    def _analyser(self):
        import time

        self.app.run_analysis()
        limite = time.time() + 60
        while self.app.result is None and time.time() < limite:
            self.app.update()
            time.sleep(0.005)
        self.app.update()

    def test_the_bar_shows_itself_and_then_steps_aside(self):
        self.app.run_analysis()
        self.assertTrue(self.app.progress.winfo_manager())
        self.attendre.sleep(0.01)
        limite = self.attendre.time() + 60
        while self.app.result is None and self.attendre.time() < limite:
            self.app.update()
            self.attendre.sleep(0.005)
        self.app.update()
        self.assertFalse(self.app.progress.winfo_manager())

    def test_the_stages_reach_the_bar(self):
        self._analyser()
        libelles = [label for label, _part in self.annonces]
        self.assertIn("Lecture du fichier", libelles)
        self.assertIn("Segments", libelles)
        parts = [part for _label, part in self.annonces]
        self.assertEqual(parts, sorted(parts))
        self.assertEqual(parts[-1], 1.0)

    def test_the_bar_ends_full(self):
        self._analyser()
        self.assertEqual(self.app.progress.shown, 1.0)

    def test_the_thread_slice_is_given_back(self):
        """Elle n'est reduite que le temps de l'analyse : une fenetre au
        repos n'a aucune raison de faire basculer les fils plus souvent."""
        avant = sys.getswitchinterval()
        self._analyser()
        self.assertEqual(sys.getswitchinterval(), avant)

    def test_the_bar_sits_under_the_button_that_started_it(self):
        self.app.run_analysis()
        self.app.update()
        self.assertLess(self.app.analyse_button.winfo_rooty(),
                        self.app.progress.winfo_rooty())
        self.assertLess(self.app.progress.winfo_rooty(),
                        self.app.export_button.winfo_rooty())


if __name__ == "__main__":
    unittest.main()
