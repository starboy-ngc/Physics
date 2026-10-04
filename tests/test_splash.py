"""L'écran d'accueil, son étoile et son nom.

Un logo calculé plutôt que livré en fichier image : c'est la même exigence
que partout ailleurs — rien d'opaque dans l'archive, aucune dépendance. Ce
qui se vérifie ici : que le symbole soit le même à chaque ouverture et à
toutes les tailles (un logo qui change de forme n'est pas un logo), que la
lumière le traverse sans le déformer, que ce soit bien la marque de l'icône
Windows — un outil n'a qu'une identité —, et que l'écran ne retarde ni la
fenêtre ni les tests.

Aucune donnée RH réelle.
"""

import base64
import os
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_insight.ui import logo
from hr_insight.version import ENGINE_NAME, PUBLISHER, __version__

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
    """Une etoile a cinq branches, pleine, d'une seule teinte.

    Ce qui compte pour un logo n'est pas qu'il soit joli — c'est qu'il soit
    toujours le meme, qu'il tienne a toutes les tailles, et qu'il se
    reconnaisse a vingt-quatre pixels.
    """

    COTE = 240

    def symbole(self, cote=None, hauteur=None, count=1):
        return logo.Star(cote or self.COTE, count, height=hauteur)

    def test_a_frame_is_a_readable_image_of_the_right_size(self):
        lignes = pixels(self.symbole().frame(0), self.COTE, self.COTE)
        self.assertEqual(len(lignes), self.COTE)
        self.assertEqual(len(lignes[0]), self.COTE * 4)

    def test_a_lower_frame_crops_the_drawing_without_flattening_it(self):
        """« height » cadre le dessin : il ne l'ecrase pas."""
        lignes = pixels(self.symbole(240, 160).frame(0), 240, 160)
        self.assertEqual(len(lignes), 160)
        self.assertEqual(len(lignes[0]), 240 * 4)

    def test_the_same_symbol_comes_back_every_time(self):
        """Rien n'est tire au hasard : le dessin vient d'une formule."""
        self.assertEqual(self.symbole().frame(0), self.symbole().frame(0))

    def test_the_shape_never_changes_from_one_frame_to_the_next(self):
        """L'animation est une lumiere qui traverse le symbole, pas une
        deformation : un logo qui change de forme n'est plus un logo."""
        symbole = self.symbole(count=8)
        silhouettes = {
            bytes(b"".join(encre(pixels(symbole.frame(index), self.COTE,
                                        self.COTE))))
            for index in range(8)}
        self.assertEqual(len(silhouettes), 1)

    def test_the_light_does_travel(self):
        symbole = self.symbole(count=8)
        self.assertNotEqual(symbole.frame(0), symbole.frame(4))

    def test_the_drawing_is_the_same_at_any_size(self):
        """Decrit par une formule et non par des pixels : la silhouette
        agrandie doit recouvrir la petite, a l'echelle pres."""
        petit = pixels(self.symbole(120).frame(0), 120, 120)
        grand = pixels(self.symbole(480).frame(0), 480, 480)
        part_petit = sum(sum(1 for valeur in ligne[3::4] if valeur > 127)
                         for ligne in petit) / (120 * 120)
        part_grand = sum(sum(1 for valeur in ligne[3::4] if valeur > 127)
                         for ligne in grand) / (480 * 480)
        self.assertAlmostEqual(part_petit, part_grand, delta=0.01)

    def test_it_never_touches_the_edge_of_its_frame(self):
        """Un symbole coupe au bord parait coupe des qu'on le pose contre
        autre chose. La lueur elle-meme a une portee finie."""
        lignes = pixels(self.symbole().frame(0), self.COTE, self.COTE)
        self.assertEqual(max(lignes[0][3::4]), 0)
        self.assertEqual(max(lignes[-1][3::4]), 0)
        self.assertEqual(max(ligne[3] for ligne in lignes), 0)
        self.assertEqual(max(ligne[-1] for ligne in lignes), 0)

    def test_it_survives_at_the_size_of_an_icon(self):
        """Une etoile reguliere couvre environ le quart de son cadre : a
        trente-deux pixels, il doit en rester de quoi la reconnaitre."""
        lignes = pixels(self.symbole(32).frame(0), 32, 32)
        encres = sum(1 for ligne in lignes for valeur in ligne[3::4]
                     if valeur > 60)
        self.assertGreater(encres, 150)

    def test_the_mark_is_one_steel_blue_star_and_nothing_else(self):
        """Une seule teinte, pas de jeton, pas de degrade : une marque n'a
        pas a se faire remarquer. Et elle ne suit pas le theme — une marque
        qui change de couleur avec un reglage d'affichage n'est plus une
        marque."""
        lignes = pixels(self.symbole().frame(0), self.COTE, self.COTE)
        milieu = self.COTE // 2

        def couleur(x, y):
            return tuple(lignes[y][x * 4:x * 4 + 4])

        # Le centre de l'etoile : la teinte de la marque, pleinement opaque.
        rouge, vert, bleu, alpha = couleur(milieu, milieu)
        self.assertEqual(alpha, 255)
        # A quelques unites pres : la lumiere qui traverse le symbole
        # eclaircit sa teinte, elle ne la remplace pas.
        for mesure, attendue in zip((rouge, vert, bleu), logo.ETOILE):
            self.assertAlmostEqual(mesure, attendue, delta=8)
        # Un bleu d'acier : il se detache d'un ecran sombre comme d'une
        # page blanche.
        self.assertGreater(bleu, rouge)
        self.assertLess(max(logo.ETOILE), 200)
        self.assertGreater(min(logo.ETOILE), 80)
        # Entre deux branches, au ras du bord : rien. Pas de jeton.
        self.assertEqual(couleur(int(self.COTE * 0.06), milieu)[3], 0)

    def test_the_first_point_looks_up(self):
        """Une etoile posee de travers se remarque immediatement, meme de
        qui ne saurait pas dire pourquoi.

        Une pointe en haut, deux en bas : la premiere ligne pleine est un
        seul trait, centre ; la derniere en compte deux, les jambes.
        """
        lignes = encre(pixels(self.symbole().frame(0), self.COTE, self.COTE))

        def traits(y):
            """Suites de pixels pleins sur cette ligne, en abscisses."""
            ligne = lignes[y]
            suites, courante = [], None
            for x in range(self.COTE):
                if ligne[x] > 200:
                    courante = [x, x] if courante is None else [courante[0], x]
                elif courante is not None:
                    suites.append(courante)
                    courante = None
            if courante is not None:
                suites.append(courante)
            return suites

        pleines = [y for y in range(self.COTE) if traits(y)]
        self.assertTrue(pleines)
        premiere = traits(pleines[0])
        self.assertEqual(len(premiere), 1, "une seule pointe en haut")
        self.assertAlmostEqual(sum(premiere[0]) / 2, self.COTE / 2,
                               delta=self.COTE * 0.02)
        # Au ras du bas de l'etoile : les deux jambes, separees. La
        # derniere ligne elle-meme ne vaut rien — a un pixel pres, un bord
        # adouci tombe d'un cote ou de l'autre du seuil.
        bas = pleines[0] + int(0.95 * (pleines[-1] - pleines[0]))
        self.assertEqual(len(traits(bas)), 2, "deux pointes en bas")

    def test_it_is_the_same_mark_as_the_windows_icon(self):
        """Un outil n'a qu'une identite : l'ecran d'accueil et l'icone du
        raccourci portent la meme etoile, au meme rapport de branches."""
        chemin = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "tools", "render_icon.py")
        with open(chemin, encoding="utf-8") as fichier:
            source = fichier.read()
        self.assertIn(f"CREUX = {logo.CREUX}", source)

    def test_the_drawing_is_computed_once_and_only_once(self):
        """Le trace est calcule une fois, les images ne font que le
        colorer. L'ecran d'accueil les calcule pendant qu'il est deja
        affiche : aucune ne doit bloquer l'affichage."""
        import time

        symbole = logo.Star(150, 24)
        debut = time.perf_counter()
        symbole.frame(0)
        trace = time.perf_counter() - debut
        debut = time.perf_counter()
        symbole.frame(7)
        suivante = time.perf_counter() - debut
        self.assertLess(trace, 0.8)
        self.assertLess(suivante, 0.06)
        self.assertLess(suivante, trace, "le trace doit etre garde")


@needs_display
class TestTheSplash(unittest.TestCase):

    def setUp(self):
        import tkinter as tk

        from hr_insight.ui import splash, theme
        from hr_insight.core.config import load_configuration

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
        """La barre rejoint ce que le moteur annonce.

        Elle se place sur l'horloge et non sur le nombre d'images — une
        image tardive fait un pas plus grand, pas un arret. Le test attend
        donc le temps qu'il faut, et non un nombre de battements.
        """
        import time

        self.ecran.announce("Pages et graphiques", 0.68)
        limite = time.perf_counter() + 2.0
        while self.ecran.bar.shown <= 0.5 and time.perf_counter() < limite:
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

    def test_the_click_is_caught_wherever_it_lands(self):
        """Le nom et la marque sont poses dans un cadre : un clic sur eux
        ne remonte pas jusqu'a la fenetre."""
        import tkinter as tk

        def descendre(widget):
            trouves = [widget]
            for enfant in widget.winfo_children():
                trouves += descendre(enfant)
            return trouves

        for widget in descendre(self.ecran):
            if isinstance(widget, tk.Canvas):
                continue        # la barre dessine, elle ne se clique pas
            self.assertTrue(widget.bind("<Button-1>"),
                            f"{widget} ne passe pas l'ecran")


@needs_display
class TestTheStartup(unittest.TestCase):
    """L'écran appartient au lancement, pas à la fenêtre."""

    def _app(self, **kwargs):
        from hr_insight.ui.app import Application

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

        from hr_insight.core.config import write_default_configuration

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
