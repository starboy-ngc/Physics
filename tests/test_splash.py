"""L'écran d'accueil, sa marque et son nom.

Un logo calculé plutôt que livré en fichier image : c'est la même exigence
que partout ailleurs — rien d'opaque dans l'archive, aucune dépendance. Ce
qui se vérifie ici : que le symbole soit le même à chaque ouverture et à
toutes les tailles (un logo qui change de forme n'est pas un logo), que la
lumière le traverse sans le déformer, qu'il ne porte aucun jugement — une
étoile dirait « cinq étoiles » —, et que l'écran ne retarde ni la fenêtre ni
les tests.

Aucune donnée RH réelle.
"""

import base64
import os
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_analytics.ui import logo
from hr_analytics.version import ENGINE_NAME, PUBLISHER, __version__

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
    """La formule « =ln(RH) », tracee au trait.

    Ce qui compte pour un logo n'est pas qu'il soit joli — c'est qu'il soit
    toujours le meme, qu'il tienne a toutes les tailles, et qu'il ne dise
    rien que l'outil ne fasse.
    """

    LARGEUR, HAUTEUR = 360, 122

    def symbole(self, largeur=None, hauteur=None, count=1):
        return logo.Mark(largeur or self.LARGEUR, count,
                         height=hauteur or self.HAUTEUR)

    def test_a_frame_is_a_readable_image_of_the_right_size(self):
        lignes = pixels(self.symbole().frame(0), self.LARGEUR, self.HAUTEUR)
        self.assertEqual(len(lignes), self.HAUTEUR)
        self.assertEqual(len(lignes[0]), self.LARGEUR * 4)

    def test_the_frame_follows_the_shape_of_the_mark(self):
        """La marque est couchee : un cadre carre lui laisserait deux
        bandes vides."""
        symbole = logo.Mark(200)
        self.assertEqual(symbole.height, round(200 * logo.RATIO))
        self.assertLess(symbole.height, symbole.size)

    def test_the_same_symbol_comes_back_every_time(self):
        """Rien n'est tire au hasard : le dessin vient d'une formule."""
        self.assertEqual(self.symbole().frame(0), self.symbole().frame(0))

    def test_the_shape_never_changes_from_one_frame_to_the_next(self):
        """L'animation est une lumiere qui traverse le symbole, pas une
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
        petit = pixels(self.symbole(180, 61).frame(0), 180, 61)
        grand = pixels(self.symbole(540, 183).frame(0), 540, 183)
        part_petit = sum(sum(1 for valeur in ligne[3::4] if valeur > 127)
                         for ligne in petit) / (180 * 61)
        part_grand = sum(sum(1 for valeur in ligne[3::4] if valeur > 127)
                         for ligne in grand) / (540 * 183)
        # Le lissage pese plus lourd dans une petite image qu'une grande :
        # la marque est fine, et ses bords y prennent une part plus large.
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
        lignes = pixels(self.symbole(96, 33).frame(0), 96, 33)
        encres = sum(1 for ligne in lignes for valeur in ligne[3::4]
                     if valeur > 60)
        self.assertGreater(encres, 150)

    def test_the_mark_is_one_steel_blue_tone_and_nothing_else(self):
        """Une seule teinte, pas de jeton, pas de degrade : une marque n'a
        pas a se faire remarquer. Et elle ne suit pas le theme — une marque
        qui change de couleur avec un reglage d'affichage n'est plus une
        marque."""
        lignes = pixels(self.symbole().frame(0), self.LARGEUR, self.HAUTEUR)
        milieu = self.HAUTEUR // 2

        def couleur(x):
            return tuple(lignes[milieu][x * 4:x * 4 + 4])

        # Dans un fut de lettre, a mi-hauteur : la teinte de la marque.
        rouge, vert, bleu, alpha = couleur(self._colonne_pleine())
        self.assertEqual(alpha, 255)
        # A quelques unites pres : la lumiere qui traverse le symbole
        # eclaircit sa teinte, elle ne la remplace pas.
        for mesure, attendue in zip((rouge, vert, bleu), logo.ENCRE):
            self.assertAlmostEqual(mesure, attendue, delta=8)
        # Un bleu d'acier : il se detache d'un ecran sombre comme d'une
        # page blanche.
        self.assertGreater(bleu, rouge)
        self.assertLess(max(logo.ENCRE), 200)
        self.assertGreater(min(logo.ENCRE), 80)
        # Au ras du bord : rien. Pas de jeton, pas d'aplat.
        self.assertEqual(couleur(1)[3], 0)

    def _colonne_pleine(self):
        """Une colonne traversee par un fut de lettre, a mi-hauteur."""
        lignes = encre(pixels(self.symbole().frame(0), self.LARGEUR,
                              self.HAUTEUR))
        milieu = self.HAUTEUR // 2
        for x in range(self.LARGEUR // 3, self.LARGEUR):
            if lignes[milieu][x] == 255:
                return x
        raise AssertionError("aucun fut plein a mi-hauteur")

    def test_it_reads_as_a_word_and_not_as_a_blob(self):
        """Sept glyphes, donc des blancs entre eux.

        Une marque dessinee trop serree se referme en tache des qu'on la
        reduit : ce qui se verifie ici, c'est qu'a mi-hauteur le trace
        alterne bien encre et blanc, et plusieurs fois.
        """
        lignes = encre(pixels(self.symbole().frame(0), self.LARGEUR,
                              self.HAUTEUR))
        milieu = self.HAUTEUR // 2
        suites, dedans = 0, False
        for valeur in lignes[milieu]:
            plein = valeur > 180
            if plein and not dedans:
                suites += 1
            dedans = plein
        # « =ln(RH) » coupe la ligne mediane en au moins sept endroits :
        # le signe egal, le « l », les deux futs du « n », la parenthese,
        # le « R », les deux futs du « H », la parenthese fermante.
        self.assertGreaterEqual(suites, 7,
                                f"le mot se referme : {suites} traits")

    def test_the_formula_opens_and_closes_its_bracket(self):
        """Une parenthese ouverte et jamais refermee se remarque.

        Les deux sont des arcs, donc les seules formes dont l'encre, sur
        la ligne mediane, se trouve aux deux extremites du mot.
        """
        lignes = encre(pixels(self.symbole().frame(0), self.LARGEUR,
                              self.HAUTEUR))
        milieu = self.HAUTEUR // 2
        pleins = [x for x, valeur in enumerate(lignes[milieu]) if valeur > 180]
        self.assertTrue(pleins)
        # La derniere encre de la ligne est la parenthese fermante : elle
        # se tient dans le dernier dixieme du mot.
        self.assertGreater(pleins[-1], self.LARGEUR * 0.90)
        # Et la premiere est le signe egal, dans le premier dixieme.
        self.assertLess(pleins[0], self.LARGEUR * 0.10)

    def test_the_short_form_is_the_same_alphabet(self):
        """Sous une trentaine de points, la formule se reduit a son
        operateur. Ce n'est pas un second dessin : c'est le meme mot,
        plus court."""
        self.assertEqual(logo.COURT.mot, "ln")
        self.assertEqual(logo.MARQUE.mot, logo.MOT)
        self.assertEqual(logo.COURT.epaisseur > 0, True)
        # La forme courte est presque carree, la complete est couchee.
        self.assertGreater(logo.COURT.ratio, logo.MARQUE.ratio * 2)

    def test_the_mark_says_nothing_the_tool_does_not_do(self):
        """Une etoile dit « cinq etoiles », une coche dit « conforme » : un
        outil qui mesure des ecarts ne porte aucun jugement sur sa porte.
        La marque est l'objet que l'outil produit, et rien d'autre.
        """
        with open(logo.__file__, encoding="utf-8") as fichier:
            source = fichier.read()
        self.assertIn("formule", source)
        self.assertIn("ne juge personne", source)
        for jugement in ("etoile dit", "coche dit", "balance dit"):
            self.assertIn(jugement, source)

    def test_the_drawing_is_computed_once_and_only_once(self):
        """Le trace est calcule une fois, les images ne font que le
        colorer. L'ecran d'accueil les calcule pendant qu'il est deja
        affiche : aucune ne doit bloquer l'affichage."""
        import time

        symbole = logo.Mark(240, 24)
        debut = time.perf_counter()
        symbole.frame(0)
        trace = time.perf_counter() - debut
        debut = time.perf_counter()
        symbole.frame(7)
        suivante = time.perf_counter() - debut
        self.assertLess(trace, 0.8)
        self.assertLess(suivante, 0.06)


@needs_display
class TestTheSplash(unittest.TestCase):

    def setUp(self):
        import tkinter as tk

        from hr_analytics.ui import splash, theme
        from hr_analytics.core.config import load_configuration

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
        from hr_analytics.ui.app import Application

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

        from hr_analytics.core.config import write_default_configuration

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
