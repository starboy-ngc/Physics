"""L'écran d'accueil, sa galaxie et son nom.

Un logo calculé plutôt que livré en fichier image : c'est la même exigence
que partout ailleurs — rien d'opaque dans l'archive, aucune dépendance. Ce
qui se vérifie ici : que la galaxie soit la même à chaque ouverture (un logo
qui change de forme n'est pas un logo), qu'elle tourne vraiment, et que
l'écran ne retarde ni la fenêtre ni les tests.

Aucune donnée RH réelle.
"""

import base64
import os
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.ui import logo
from compensation_analytics.version import ENGINE_NAME, PUBLISHER, __version__

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

COLD = (96, 160, 235)
WARM = (255, 226, 170)


def pixels(data: bytes, size: int):
    """Relit le PNG produit : RVBA, ligne par ligne, sans filtrage."""
    png = base64.b64decode(data)
    corps = b""
    position = 8
    while position < len(png):
        taille = int.from_bytes(png[position:position + 4], "big")
        if png[position + 4:position + 8] == b"IDAT":
            corps += png[position + 8:position + 8 + taille]
        position += 12 + taille
    brut = zlib.decompress(corps)
    largeur = size * 4 + 1
    return [brut[y * largeur + 1:(y + 1) * largeur] for y in range(size)]


class TestTheGalaxy(unittest.TestCase):

    SIZE = 64

    def galaxy(self):
        return logo.Galaxy(self.SIZE, 12, cold=COLD, warm=WARM)

    def test_a_frame_is_a_readable_image_of_the_right_size(self):
        lignes = pixels(self.galaxy().frame(0), self.SIZE)
        self.assertEqual(len(lignes), self.SIZE)
        self.assertEqual(len(lignes[0]), self.SIZE * 4)

    def test_the_same_galaxy_comes_back_every_time(self):
        """Un logo qui changerait de forme d'un lancement à l'autre ne
        serait pas un logo."""
        self.assertEqual(self.galaxy().frame(3), self.galaxy().frame(3))

    def test_the_core_shines_and_the_corners_stay_clear(self):
        lignes = pixels(self.galaxy().frame(0), self.SIZE)
        milieu = self.SIZE // 2
        centre = lignes[milieu][milieu * 4:milieu * 4 + 4]
        self.assertGreater(centre[3], 200, "le bulbe doit être lumineux")
        # Le coin doit rester transparent : sans quoi le logo poserait un
        # rectangle sur le fond au lieu de s'y fondre.
        self.assertEqual(lignes[0][3], 0)
        self.assertEqual(lignes[-1][-1], 0)

    def test_the_core_is_warm_and_the_arms_are_cold(self):
        lignes = pixels(self.galaxy().frame(0), self.SIZE)
        milieu = self.SIZE // 2
        rouge, _vert, bleu, _alpha = lignes[milieu][milieu * 4:milieu * 4 + 4]
        self.assertGreater(rouge, bleu, "le bulbe tire vers l'or")

    def test_it_really_turns(self):
        galaxie = self.galaxy()
        self.assertNotEqual(galaxie.frame(0), galaxie.frame(3))

    def test_a_full_turn_comes_back_to_the_start(self):
        """Douze images pour un tour : la treizième est la première, sans
        quoi la rotation sauterait à chaque boucle."""
        galaxie = self.galaxy()
        self.assertEqual(galaxie.frame(0), galaxie.frame(12))

    def test_the_density_follows_the_surface(self):
        """Quatre fois plus large, seize fois plus d'etoiles : c'est ce qui
        fait tenir les bras. A nombre constant, une galaxie agrandie se
        defait en grains isoles."""
        petite = logo.Galaxy(78, 12, cold=COLD, warm=WARM)
        grande = logo.Galaxy(312, 12, cold=COLD, warm=WARM)
        rapport = len(grande.stars) / len(petite.stars)
        self.assertAlmostEqual(rapport, 16.0, delta=1.0)

    def test_the_dot_grows_slower_than_the_image(self):
        """Sinon une galaxie rendue en grand n'est plus qu'un amas de
        taches floues : le point doit perdre en taille relative."""
        petite = logo.Galaxy(156, 12, cold=COLD, warm=WARM)
        grande = logo.Galaxy(624, 12, cold=COLD, warm=WARM)
        self.assertGreater(len(grande.kernel), len(petite.kernel))
        # Quatre fois plus large, mais le point n'a pas quadruple.
        self.assertLess(len(grande.kernel), len(petite.kernel) * 16)

    def test_the_light_does_not_depend_on_the_size(self):
        """La lumiere s'ajoute : deux fois plus d'etoiles, chacune plus
        large, et la galaxie vire au ruban blanc. L'eclat de chaque etoile
        est donc divise par ce que le point a gagne."""
        def clarte(taille):
            galaxie = logo.Galaxy(taille, 12, cold=COLD, warm=WARM)
            lignes = pixels(galaxie.frame(0), taille)
            total = sum(sum(ligne[3::4]) for ligne in lignes)
            return total / (taille * taille)

        self.assertAlmostEqual(clarte(78), clarte(312), delta=12)

    def test_the_whole_rotation_is_affordable(self):
        """Elle est calculée pendant que l'écran est déjà là, image par
        image : aucune ne doit bloquer l'affichage."""
        import time

        galaxie = logo.Galaxy(156, 24, cold=COLD, warm=WARM)
        debut = time.perf_counter()
        galaxie.frame(0)
        self.assertLess(time.perf_counter() - debut, 0.25)


@needs_display
class TestTheSplash(unittest.TestCase):

    def setUp(self):
        import tkinter as tk

        from compensation_analytics.ui import splash, theme
        from compensation_analytics.core.config import load_configuration

        self.root = tk.Tk()
        self.root.withdraw()
        theme.load(load_configuration())
        self.fonts = theme.Fonts(self.root)
        self.module = splash
        self.ecran = splash.show(self.root, self.fonts)
        self.addCleanup(self.root.destroy)

    def _textes(self):
        import tkinter as tk

        trouves = []

        def descendre(widget):
            for enfant in widget.winfo_children():
                if isinstance(enfant, tk.Label):
                    trouves.append(str(enfant.cget("text")))
                descendre(enfant)

        descendre(self.ecran)
        return trouves

    def test_it_names_the_product_the_publisher_and_the_version(self):
        textes = self._textes()
        self.assertIn(ENGINE_NAME, textes)
        self.assertIn(PUBLISHER.upper(), textes)
        self.assertIn(f"Version {__version__}", textes)

    def test_the_name_is_not_written_twice_in_the_code(self):
        """La fenêtre, les documents et le manifeste doivent nommer l'outil
        de la même façon : le nom est écrit dans « version.py », et nulle
        part ailleurs."""
        self.assertEqual(self.module.PRODUCT, ENGINE_NAME)

    def test_a_stage_moves_the_bar(self):
        self.ecran.announce("Pages et graphiques", 0.68)
        for _ in range(60):
            self.ecran.tick()
        self.assertGreater(self.ecran.bar.shown, 0.5)

    def test_the_rotation_is_computed_beat_by_beat(self):
        """La première image suffit à afficher l'écran ; les autres
        arrivent pendant qu'il est déjà là."""
        self.assertEqual(len(self.ecran._images), 1)
        for _ in range(self.ecran.FRAMES):
            self.ecran.tick()
        self.assertEqual(len(self.ecran._images), self.ecran.FRAMES)

    def test_a_click_passes_it(self):
        self.assertFalse(self.ecran.skipped)
        self.ecran.skip()
        self.assertTrue(self.ecran.skipped)


@needs_display
class TestTheStartup(unittest.TestCase):
    """L'écran appartient au lancement, pas à la fenêtre."""

    def _app(self, **kwargs):
        from compensation_analytics.ui.app import Application

        app = Application(**kwargs)
        self.addCleanup(app.destroy)
        return app

    def test_the_window_opens_without_a_splash_by_default(self):
        """Un test qui construit la fenêtre pour lire un widget ne doit pas
        l'attendre une seconde et demie."""
        import time

        debut = time.perf_counter()
        app = self._app()
        self.assertIsNone(app._splash)
        self.assertLess(time.perf_counter() - debut, 1.5)

    def test_the_window_is_shown_once_built(self):
        app = self._app()
        app.update()
        self.assertEqual(app.state(), "normal")

    def test_the_splash_is_gone_when_the_window_appears(self):
        import time

        debut = time.perf_counter()
        app = self._app(splash=True)
        duree = time.perf_counter() - debut
        app.update()
        self.assertIsNone(app._splash)
        self.assertEqual(app.state(), "normal")
        # Il est resté affiché le temps qu'on le voie.
        self.assertGreater(duree, app._splash_seconds() * 0.8)

    def test_a_duration_of_zero_skips_it_entirely(self):
        import json
        import tempfile

        from compensation_analytics.core.config import write_default_configuration

        dossier = tempfile.mkdtemp()
        write_default_configuration(dossier)
        chemin = os.path.join(dossier, "theme_parameters.json")
        with open(chemin, encoding="utf-8") as fichier:
            reglages = json.load(fichier)
        reglages["splash_seconds"] = 0
        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(reglages, fichier)
        app = self._app(config_dir=dossier, splash=True)
        self.assertIsNone(app._splash)


if __name__ == "__main__":
    unittest.main()
