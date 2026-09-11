"""L'aurore de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : un rideau d'aurore. Un bord vif, ondulant, et des rais qui
s'en elevent et se dissipent — du vert des basses couches au violet des
hautes, dans cet ordre-la, qui est celui du ciel. Onze traits suffisent. Un
symbole n'a pas a etre une illustration : il doit se reconnaitre a
vingt-quatre pixels comme a deux mille, et l'on doit pouvoir le redessiner
de memoire.

Tout est analytique : pour chaque pixel, sa position dans le rai et la
couverture s'en deduit. Il n'y a ni tirage aleatoire, ni echantillonnage —
donc aucun grain a faire grossir quand l'image grandit, et le meme dessin
exactement a toutes les tailles.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from . import raster

RGB = Tuple[int, int, int]

#: Couleurs du symbole, du bas vers le haut. Elles ne suivent pas le theme
#: de la fenetre : une marque qui change de couleur avec un reglage
#: d'affichage n'est plus une marque. Le vert des basses couches, le violet
#: des hautes — l'ordre qu'a le ciel.
GREEN = (74, 201, 150)
TEAL = (72, 168, 196)
VIOLET = (126, 98, 208)

#: Nombre de rais. Cinq font une main, onze font un peigne : neuf se
#: comptent d'un coup d'oeil sans que le rideau paraisse ajoure.
RAYS = 11

#: Le rai : largeur et ecart, en parts de la largeur de l'image.
RAY_WIDTH = 0.056
RAY_GAP = 0.028

#: L'onde qui porte le rideau : le bord *inferieur* la suit, et les rais
#: s'en elevent. C'est le bas d'une aurore qui est vif et net ; le haut se
#: dissipe. Une periode sur la largeur : une crete et un creux.
PERIODS = 1.0
AMPLITUDE = 0.10
TOP = 0.682

#: Le bord inferieur : un trait fin, qui relie les rais entre eux. Sans
#: lui, onze traits verticaux font un diagramme en batons.
EDGE = 0.034

#: Longueur des rais. Elle varie d'un rai a l'autre, sans quoi leurs pieds
#: s'alignent et le rideau retombe sur une ligne de base.
LENGTH = 0.40
LENGTH_SWING = 0.42

#: Part franche d'un rai avant l'extinction. Courte : c'est l'extinction
#: qui fait une lumiere suspendue plutot qu'un baton.
SOLID = 0.10

#: Douceur des bords lateraux, en parts de la largeur du rai.
SOFTNESS = 0.45

#: Inclinaison des rais : ils ne tombent pas d'aplomb mais penchent tous du
#: meme cote, comme pousses. Des traits parfaitement verticaux font un
#: diagramme en batons ; ceux-la font un rideau.
TILT = 0.17

#: De combien un rai s'affine en descendant : la lumiere s'amincit en
#: s'eteignant.
NARROWING = 0.32

#: Marge laissee tout autour : le symbole ne touche jamais le bord de son
#: cadre, sans quoi il parait coupe des qu'on le pose contre autre chose.
INSET = 0.055

#: La lueur qui parcourt le rideau : de combien elle eclaircit, sur quelle
#: largeur, et jusqu'ou elle voyage de part et d'autre du cadre. Elle ne
#: touche jamais au trace — seulement a sa couleur.
GLOW_STRENGTH = 0.45
GLOW_WIDTH = 0.22
GLOW_TRAVEL = 1.5
GLOW_MARGIN = 0.25


class Aurora:
    """Le symbole, et la lueur qui le parcourt, image par image."""

    def __init__(self, size: int, count: int = 1,
                 height: Optional[int] = None):
        """`size` est la largeur ; `height` permet un cadre plus bas que
        large. Le dessin n'est pas etire pour autant : il est cadre."""
        self.size = size
        self.height = height or size
        self.count = max(1, count)
        self.rays = self._rays()

    # ------------------------------------------------------------- rais

    def _rays(self) -> List[Tuple[float, float, float]]:
        """Abscisse, sommet et longueur de chaque rai.

        Les rais sont poses une fois pour toutes : ils ne dependent ni de
        la taille demandee, ni de l'image en cours. C'est la meme aurore a
        chaque ouverture et a toutes les echelles.
        """
        utile = 1.0 - 2 * INSET
        pas = RAY_WIDTH + RAY_GAP
        largeur_totale = RAYS * RAY_WIDTH + (RAYS - 1) * RAY_GAP
        depart = INSET + (utile - largeur_totale) / 2 + RAY_WIDTH / 2
        rais: List[Tuple[float, float, float]] = []
        for rang in range(RAYS):
            x = depart + rang * pas
            # La longueur suit sa propre onde, plus lente que celle du
            # bord : deux rais voisins ne descendent jamais a la meme
            # profondeur, et le rideau n'a pas de pied.
            # La hauteur suit une arche : haute au milieu, basse aux
            # extremites. Un rideau dont les rais monteraient tous a la
            # meme hauteur serait une grille ; un rideau dont les hauteurs
            # seraient tirees au hasard n'aurait pas de silhouette.
            place = rang / (RAYS - 1)
            arche = math.sin(math.pi * place) ** 0.75
            # Un leger desordre, pour que l'arche ne soit pas un compas.
            desordre = 1.0 + LENGTH_SWING * 0.35 * math.sin(
                2 * math.pi * (2.3 * place + 0.15))
            rais.append((x, _wave(x),
                         LENGTH * (0.30 + 0.70 * arche) * desordre))
        return rais

    # ---------------------------------------------------------- images

    def frame(self, index: int = 0) -> bytes:
        """Image `index` de l'animation, prete pour PhotoImage.

        Le dessin ne bouge pas : c'est une lueur qui le parcourt, de gauche
        a droite, et revient. Un logo qui change de forme au fil des images
        n'est plus un logo — mais une aurore immobile n'est pas une aurore.
        """
        size = self.size
        part = (index % self.count) / self.count
        lueur = GLOW_TRAVEL * (1 - abs(1 - 2 * part)) - GLOW_MARGIN
        toile = [bytearray(size * 4) for _ in range(self.height)]
        # Tout est mesure en parts de la largeur, y compris a la verticale :
        # un cadre plus bas que large recadre le dessin, il ne l'aplatit pas.
        haut = (size * (1.0) - self.height) / 2.0
        self._draw_rays(toile, size, haut, lueur)
        self._draw_edge(toile, size, haut, lueur)
        return raster.image_data(size, self.height, toile, 6)

    def _draw_edge(self, toile, size: int, haut: float,
                   lueur: float) -> None:
        """Le bord inferieur, d'un bout a l'autre du rideau.

        Il relie les rais : sans lui, onze traits ne sont qu'un diagramme en
        batons. Il s'affine aux deux extremites, comme un trait de pinceau.
        """
        demi_base = EDGE / 2.0
        premier = self.rays[0][0]
        dernier = self.rays[-1][0]
        etendue = dernier - premier
        for colonne in range(size):
            x = (colonne + 0.5) / size
            position = (x - premier) / etendue
            if position < -0.06 or position > 1.06:
                continue
            bout = min(1.0, max(0.0, (0.5 - abs(position - 0.5)) / 0.22))
            demi = demi_base * bout * bout * (3 - 2 * bout)
            if demi <= 0.0:
                continue
            onde = _wave(x)
            correction = math.sqrt(1.0 + _slope(x) ** 2)
            douceur = demi * 0.7
            eclat = self._glow(x, lueur)
            portee = (demi + douceur) * correction
            debut = max(0, int((onde - portee) * size - haut))
            fin = min(self.height - 1, int((onde + portee) * size - haut) + 1)
            for ligne in range(debut, fin + 1):
                y = (ligne + haut + 0.5) / size
                couverture = self._across(abs(y - onde) / correction, demi,
                                          douceur)
                if couverture <= 0.004:
                    continue
                self._pose(toile, ligne, colonne, couverture,
                           self._colour(y), eclat)

    def _draw_rays(self, toile, size: int, haut: float,
                   lueur: float) -> None:
        """Les rais, en un seul passage.

        Un rai n'est pas dessine pour lui-meme : pour chaque point, on
        regarde a quelle profondeur sous le bord il se trouve, puis de quel
        rai il releve une fois l'inclinaison defaite. C'est ce qui permet
        aux rais de pencher et de s'affiner sans rien couter de plus.
        """
        pas = RAY_WIDTH + RAY_GAP
        premier = self.rays[0][0]
        profond = max(longueur for _x, _s, longueur in self.rays)
        for colonne in range(size):
            x = (colonne + 0.5) / size
            eclat = self._glow(x, lueur)
            onde = _wave(x)
            debut = max(0, int((onde - profond) * size - haut))
            fin = min(self.height - 1, int(onde * size - haut) + 1)
            for ligne in range(debut, fin + 1):
                y = (ligne + haut + 0.5) / size
                creux = onde - y
                if creux < 0.0:
                    continue
                # L'inclinaison se defait : on revient a l'abscisse du rai
                # au moment ou il quitte le bord.
                origine = x - TILT * creux
                rang = int(round((origine - premier) / pas))
                if rang < 0 or rang >= RAYS:
                    continue
                centre, _sommet, longueur = self.rays[rang]
                if creux > longueur:
                    continue
                part = creux / longueur
                demi = RAY_WIDTH / 2.0 * (1.0 - NARROWING * part)
                douceur = demi * SOFTNESS
                lateral = self._across(abs(origine - centre), demi, douceur)
                if lateral <= 0.0:
                    continue
                couverture = lateral * self._along(part)
                if couverture <= 0.004:
                    continue
                self._pose(toile, ligne, colonne, couverture,
                           self._colour(y), eclat)

    @staticmethod
    def _glow(x: float, lueur: float) -> float:
        """Eclaircissement du a la lueur, a cette abscisse."""
        ecart = (x - lueur) / GLOW_WIDTH
        return 1.0 + GLOW_STRENGTH * math.exp(-ecart * ecart)

    @staticmethod
    def _pose(toile, ligne: int, colonne: int, couverture: float,
              couleur: RGB, eclat: float) -> None:
        """Pose un point, le plus opaque l'emportant.

        Les rais et le bord se recouvrent au sommet : melanger leurs
        couvertures y ferait une tache plus claire que partout ailleurs.
        """
        position = colonne * 4
        cible = toile[ligne]
        opacite = min(255, int(couverture * 255))
        if opacite <= cible[position + 3]:
            return
        rouge, vert, bleu = couleur
        cible[position] = min(255, int(rouge * eclat))
        cible[position + 1] = min(255, int(vert * eclat))
        cible[position + 2] = min(255, int(bleu * eclat))
        cible[position + 3] = opacite

    @staticmethod
    def _across(distance: float, demi: float, douceur: float) -> float:
        """Profil en travers du rai : plein au milieu, adouci aux bords."""
        if distance >= demi + douceur:
            return 0.0
        if distance <= demi - douceur:
            return 1.0
        part = (demi + douceur - distance) / (2 * douceur)
        return part * part * (3 - 2 * part)

    @staticmethod
    def _along(position: float) -> float:
        """Profil le long du rai : franc sous le sommet, eteint au bas."""
        if position <= SOLID:
            return 1.0
        reste = (1.0 - position) / (1.0 - SOLID)
        # Extinction douce plutot que carree : les pointes restent visibles
        # sur un fond clair, ou une opacite de dix pour cent ne se voit pas.
        return reste ** 1.45

    @staticmethod
    def _colour(y: float) -> RGB:
        """Vert au bord, violet en haut des rais, quelle que soit la
        longueur de chacun : les bandes de couleur appartiennent au ciel,
        pas au trait."""
        part = min(max((TOP + AMPLITUDE - y) / (LENGTH * 0.82), 0.0), 1.0)
        if part < 0.5:
            return _mix(GREEN, TEAL, part * 2)
        return _mix(TEAL, VIOLET, (part - 0.5) * 2)


def _wave(x: float) -> float:
    """Hauteur du bord superieur du rideau, a cette abscisse."""
    return TOP + AMPLITUDE * math.sin(2 * math.pi * PERIODS * x)


def _slope(x: float) -> float:
    """Pente de ce bord : elle corrige la distance quand il est incline."""
    return AMPLITUDE * 2 * math.pi * PERIODS * math.cos(
        2 * math.pi * PERIODS * x)


def _mix(first: RGB, second: RGB, part: float) -> RGB:
    return tuple(int(round(a + (b - a) * part)) for a, b in zip(first, second))
