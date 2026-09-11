"""L'écran d'accueil, son aurore et son nom.

Un logo calculé plutôt que livré en fichier image : c'est la même exigence
que partout ailleurs — rien d'opaque dans l'archive, aucune dépendance. Ce
qui se vérifie ici : que le symbole soit le même à chaque ouverture et à
toutes les tailles (un logo qui change de forme n'est pas un logo), que la
lueur le parcoure sans le déformer, et que l'écran ne retarde ni la fenêtre
ni les tests.

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

def pixels(data: bytes, largeur: int, hauteur: int):
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
    ligne = largeur * 4 + 1
    return [brut[y * ligne + 1:(y + 1) * ligne] for y in range(hauteur)]


def encre(lignes):
    """Silhouette : l'opacite de chaque pixel, la couleur mise de cote."""
    return [bytes(ligne[3::4]) for ligne in lignes]


class TestTheSymbol(unittest.TestCase):
    """Un rideau d'aurore : un bord ondulant, des rais qui s'en elevent.

    Ce qui compte pour un logo n'est pas qu'il soit joli — c'est qu'il soit
    toujours le meme, qu'il tienne a toutes les tailles, et qu'il se
    reconnaisse a vingt-quatre pixels.
    """

    LARGEUR, HAUTEUR = 240, 163

    def symbole(self, largeur=None, hauteur=None, count=1):
        return logo.Aurora(largeur or self.LARGEUR, count,
                           height=hauteur or self.HAUTEUR)

    def test_a_frame_is_a_readable_image_of_the_right_size(self):
        lignes = pixels(self.symbole().frame(0), self.LARGEUR, self.HAUTEUR)
        self.assertEqual(len(lignes), self.HAUTEUR)
        self.assertEqual(len(lignes[0]), self.LARGEUR * 4)

    def test_the_same_symbol_comes_back_every_time(self):
        """Rien n'est tire au hasard : le dessin vient d'une formule."""
        self.assertEqual(self.symbole().frame(0), self.symbole().frame(0))

    def test_the_shape_never_changes_from_one_frame_to_the_next(self):
        """L'animation est une lueur qui parcourt le symbole, pas une
        deformation : un logo qui change de forme n'est plus un logo."""
        symbole = self.symbole(count=8)
        silhouettes = {
            bytes(b"".join(encre(pixels(symbole.frame(index), self.LARGEUR,
                                        self.HAUTEUR))))
            for index in range(8)}
        self.assertEqual(len(silhouettes), 1)

    def test_the_light_does_travel(self):
        symbole = self.symbole(count=8)
        self.assertNotEqual(symbole.frame(0), symbole.frame(4))

    def test_the_drawing_is_the_same_at_any_size(self):
        """Decrit par une formule et non par des pixels : la silhouette
        agrandie doit recouvrir la petite, a l'echelle pres."""
        petit = pixels(self.symbole(120, 82).frame(0), 120, 82)
        grand = pixels(self.symbole(480, 326).frame(0), 480, 326)
        part_petit = sum(sum(1 for valeur in ligne[3::4] if valeur > 127)
                         for ligne in petit) / (120 * 82)
        part_grand = sum(sum(1 for valeur in ligne[3::4] if valeur > 127)
                         for ligne in grand) / (480 * 326)
        self.assertAlmostEqual(part_petit, part_grand, delta=0.02)

    def test_it_never_touches_the_edge_of_its_frame(self):
        """Un symbole coupe au bord parait coupe des qu'on le pose contre
        autre chose."""
        lignes = pixels(self.symbole().frame(0), self.LARGEUR, self.HAUTEUR)
        self.assertEqual(max(lignes[0][3::4]), 0)
        self.assertEqual(max(lignes[-1][3::4]), 0)
        self.assertEqual(max(ligne[3] for ligne in lignes), 0)
        self.assertEqual(max(ligne[-1] for ligne in lignes), 0)

    def test_it_survives_at_the_size_of_an_icon(self):
        lignes = pixels(self.symbole(32, 22).frame(0), 32, 22)
        encres = sum(1 for ligne in lignes for valeur in ligne[3::4]
                     if valeur > 60)
        self.assertGreater(encres, 40)

    def test_it_goes_from_green_below_to_violet_above(self):
        """Les deux teintes d'une aurore. Elles ne suivent pas le theme :
        une marque qui change de couleur n'est plus une marque."""
        lignes = pixels(self.symbole().frame(0), self.LARGEUR, self.HAUTEUR)
        milieu = self.LARGEUR // 2

        def couleur(rangs):
            """Premier pixel franc rencontre en parcourant ces lignes."""
            for y in rangs:
                r, v, b, a = lignes[y][milieu * 4:milieu * 4 + 4]
                if a > 200:
                    return r, v, b
            return None

        haut = couleur(range(0, self.HAUTEUR))
        bas = couleur(range(self.HAUTEUR - 1, -1, -1))
        self.assertIsNotNone(haut)
        self.assertIsNotNone(bas)
        self.assertGreater(haut[2], haut[1],
                           "la pointe des rais tire au violet")
        self.assertGreater(bas[1], bas[2], "le bord du bas tire au vert")

    def test_one_frame_costs_nothing(self):
        """L'ecran d'accueil les calcule pendant qu'il est deja affiche :
        aucune ne doit bloquer l'affichage."""
        import time

        symbole = logo.Aurora(236, 24, height=160)
        debut = time.perf_counter()
        symbole.frame(0)
        self.assertLess(time.perf_counter() - debut, 0.12)


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

    def test_the_animation_is_computed_beat_by_beat(self):
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
