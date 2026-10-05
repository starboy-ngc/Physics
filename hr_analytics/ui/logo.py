"""La marque de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : « =ln(RH) ». Une formule de tableur — tout tableur
commence une formule par un signe egal — appliquee a la matiere de
l'outil. Le logarithme n'est pas un ornement : c'est l'echelle sur
laquelle une distribution de remunerations se lit, parce que les ecarts
y sont multiplicatifs et non additifs.

Le choix n'est pas qu'esthetique. Une etoile dit « cinq etoiles », une
coche dit « conforme », une balance dit « justice » : un outil qui mesure
des ecarts de remuneration ne doit porter aucun de ces jugements sur sa
porte. Une formule ne juge personne : elle dit ce qu'on calcule.

Les lettres sont tracees, pas composees : aucune police n'est embarquee,
et le dessin ne depend donc d'aucune fonte installee sur le poste. Chaque
glyphe est une poignee de traits et d'arcs, decrits en cadratin — hauteur
de capitale valant un — puis mis a l'echelle du cadre.

Sa teinte ne suit pas le theme et ne change pas avec le fond : un bleu
d'acier, assez clair pour se detacher d'un ecran sombre, assez dense pour
tenir sur un fond blanc. Elle se lit donc aussi bien a l'accueil, sur
l'encre, que pendant une analyse, sur la page.

Tout est analytique. Chaque piece est decrite par sa *distance signee* —
negative dedans, positive dehors —, les pieces se reunissent en prenant la
plus petite, et l'opacite d'un pixel se deduit de la distance finale : un
demi-pixel de part et d'autre du bord. Il n'y a donc ni tirage aleatoire,
ni echantillonnage, ni surechantillonnage a payer : le meme dessin
exactement a toutes les tailles, en un seul passage.

Deux primitives suffisent a tout ecrire : le trait a bouts ronds et l'arc
de cercle. Leurs distances sont exactes, et le dessin entier est leur
minimum.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from . import raster

RGB = Tuple[int, int, int]

#: La teinte de la marque. Elle ne suit pas le theme de la fenetre : une
#: marque qui change de couleur avec un reglage d'affichage n'est plus une
#: marque.
ENCRE = (110, 148, 186)

#: Demi-epaisseur du trait, en cadratin. Monoline : toutes les lettres ont
#: la meme chasse, ce qui tient a toutes les tailles la ou un contraste
#: plein-delie se referme des que le dessin rapetisse.
TRAIT = 0.088

#: Chasse entre deux glyphes, en cadratin.
CHASSE = 0.105

#: Marge laissee autour de la marque, en parts de la largeur du cadre.
INSET = 0.035

#: Les glyphes, en cadratin : hauteur de capitale valant un, ligne de base
#: a zero, les ordonnees negatives montent. Deux primitives seulement :
#:
#:   ("trait", x1, y1, x2, y2)      un segment a bouts ronds
#:   ("arc", cx, cy, rayon, a0, a1) un arc, en degres, zero a droite et
#:                                  croissant vers le bas
#:
#: Aucune chasse n'est donnee a la main : l'encombrement reel de chaque
#: lettre — epaisseur du trait comprise — est calcule depuis ses
#: primitives, et c'est lui qui pousse la suivante. Des chasses ecrites a
#: l'oeil laissaient les lettres se chevaucher.
HAUTEUR_X = 0.60
GLYPHES = {
    "=": (("trait", 0.00, -0.30, 0.44, -0.30),
          ("trait", 0.00, -0.56, 0.44, -0.56)),
    # Le « l » porte une queue : en lineale, un « l » droit est un « I »
    # majuscule, et « =In(RH) » ne veut rien dire.
    "l": (("trait", 0.00, -1.00, 0.00, -0.14),
          ("arc", 0.14, -0.14, 0.14, 90.0, 180.0)),
    "n": (("trait", 0.00, -HAUTEUR_X, 0.00, 0.00),
          ("arc", 0.25, -HAUTEUR_X, 0.25, 180.0, 360.0),
          ("trait", 0.50, -HAUTEUR_X, 0.50, 0.00)),
    # La parenthese : un arc dont on choisit la profondeur et la hauteur,
    # le rayon et les angles s'en deduisant. Les poser a l'oeil donnait un
    # arc qui sortait du mot.
    "(": (("arc", 0.7733, -0.50, 0.7733, 133.6, 226.4),),
    ")": (("arc", -0.5333, -0.50, 0.7733, -46.4, 46.4),),
    "R": (("trait", 0.00, -1.00, 0.00, 0.00),
          ("trait", 0.00, -1.00, 0.24, -1.00),
          ("arc", 0.24, -0.76, 0.24, 270.0, 450.0),
          ("trait", 0.24, -0.52, 0.00, -0.52),
          ("trait", 0.22, -0.52, 0.54, 0.00)),
    "H": (("trait", 0.00, -1.00, 0.00, 0.00),
          ("trait", 0.50, -1.00, 0.50, 0.00),
          ("trait", 0.00, -0.52, 0.50, -0.52)),
}

#: Ce qui est ecrit. Le signe egal d'abord : c'est lui qui fait la formule.
MOT = "=ln(RH)"


def _bornes(forme):
    """Encombrement d'une primitive, epaisseur du trait comprise."""
    if forme[0] == "trait":
        gauche, droite = min(forme[1], forme[3]), max(forme[1], forme[3])
        haut, bas = min(forme[2], forme[4]), max(forme[2], forme[4])
    else:
        _genre, cx, cy, rayon, a0, a1 = forme
        points = [(cx + rayon * math.cos(math.radians(a)),
                   cy + rayon * math.sin(math.radians(a))) for a in (a0, a1)]
        # Les quarts de tour compris dans l'arc en sont les extremes.
        milieu = math.radians((a0 + a1) / 2.0)
        demi = math.radians(abs(a1 - a0) / 2.0)
        for quart in range(-4, 8):
            angle = math.radians(quart * 90.0)
            ecart = (angle - milieu + math.pi) % (2 * math.pi) - math.pi
            if abs(ecart) <= demi:
                points.append((cx + rayon * math.cos(angle),
                               cy + rayon * math.sin(angle)))
        gauche = min(point[0] for point in points)
        droite = max(point[0] for point in points)
        haut = min(point[1] for point in points)
        bas = max(point[1] for point in points)
    return (gauche - TRAIT, droite + TRAIT, haut - TRAIT, bas + TRAIT)


def _decaler(forme, pas: float):
    return (("trait", forme[1] + pas, forme[2], forme[3] + pas, forme[4])
            if forme[0] == "trait"
            else ("arc", forme[1] + pas, forme[2], forme[3], forme[4],
                  forme[5]))


def _composer(mot: str):
    """Place les glyphes, et rend le trace en parts de la largeur du cadre.

    Le mot est d'abord assemble en cadratin — chaque lettre posee contre la
    precedente, a une chasse pres —, puis l'ensemble est mis a l'echelle du
    cadre et centre. Compose une fois pour toutes a l'import : c'est le
    meme mot a chaque ouverture et a toutes les tailles.
    """
    pieces, curseur = [], 0.0
    for lettre in mot:
        primitives = GLYPHES[lettre]
        bornes = [_bornes(forme) for forme in primitives]
        gauche = min(borne[0] for borne in bornes)
        droite = max(borne[1] for borne in bornes)
        pas = curseur - gauche
        pieces.extend(_decaler(forme, pas) for forme in primitives)
        curseur += (droite - gauche) + CHASSE
    largeur = curseur - CHASSE
    bornes = [_bornes(forme) for forme in pieces]
    haut = min(borne[2] for borne in bornes)
    bas = max(borne[3] for borne in bornes)
    echelle = (1.0 - 2 * INSET) / largeur
    milieu = (haut + bas) / 2.0
    posees = []
    for forme in pieces:
        if forme[0] == "trait":
            posees.append(("trait",
                           INSET + forme[1] * echelle,
                           0.5 + (forme[2] - milieu) * echelle,
                           INSET + forme[3] * echelle,
                           0.5 + (forme[4] - milieu) * echelle))
        else:
            posees.append(("arc",
                           INSET + forme[1] * echelle,
                           0.5 + (forme[2] - milieu) * echelle,
                           forme[3] * echelle, forme[4], forme[5]))
    return posees, TRAIT * echelle, (bas - haut) * echelle


class Trace:
    """Un mot compose, et la distance signee a son trace.

    La marque complete et sa forme courte sont deux traces du meme
    alphabet : rien n'est redessine, seule la chaine change.
    """

    def __init__(self, mot: str):
        self.mot = mot
        self.pieces, self.epaisseur, hauteur = _composer(mot)
        #: Proportion du cadre : celle du mot, epaisseur comprise, plus la
        #: meme marge en haut et en bas qu'a gauche et a droite.
        self.ratio = hauteur + 2 * INSET

    def distance(self, x: float, y: float) -> float:
        """Distance signee au trace : negative dedans, positive dehors."""
        plus_proche = 9.9
        for forme in self.pieces:
            if forme[0] == "trait":
                valeur = _trait(x, y, forme[1], forme[2], forme[3], forme[4],
                                self.epaisseur)
            else:
                valeur = _arc(x, y, forme[1], forme[2], forme[3], forme[4],
                              forme[5], self.epaisseur)
            if valeur < plus_proche:
                plus_proche = valeur
        return plus_proche


#: La marque, et sa forme courte.
#:
#: Sous une trentaine de points, sept glyphes ne font plus qu'une tache :
#: l'icone de la barre des taches, celle de l'explorateur en liste, celle
#: du cadre de la fenetre. La formule se reduit alors a son operateur —
#: « ln » tient a seize points la ou « =ln(RH) » ne tient pas. Ce qui ne
#: se lit pas ne vaut pas d'etre dessine.
MARQUE = Trace(MOT)
COURT = Trace("ln")

#: Proportion du cadre de la marque complete, pour qui compose une page
#: autour d'elle.
RATIO = MARQUE.ratio

#: Le passage de lumiere, image par image : de combien il eclaircit, sur
#: quelle largeur, son inclinaison, et jusqu'ou il voyage de part et
#: d'autre du cadre. Il ne touche jamais au trace — seulement a sa
#: couleur. Discret : un logo qui clignote pendant un demarrage se regarde
#: au lieu de se laisser oublier.
REFLET_FORCE = 0.34
REFLET_LARGEUR = 0.30
REFLET_PENTE = 0.80
REFLET_COURSE = 1.9
REFLET_MARGE = 0.45

#: Taille au-dela de laquelle l'encodage PNG passe en compression rapide :
#: une planche de mille pixels prend une seconde a compresser au maximum,
#: pour quelques kilooctets gagnes que personne ne transporte.
RAPIDE_AU_DELA = 420


class Mark:
    """Le symbole, et la lumiere qui le traverse, image par image."""

    def __init__(self, size: int, count: int = 1,
                 height: Optional[int] = None):
        """`size` est la largeur ; `height` cadre le dessin plus bas que
        large. Par defaut, la proportion de la marque."""
        self.size = size
        self.height = height or max(1, int(round(size * RATIO)))
        self.count = max(1, count)
        self._carte: Optional[List[bytearray]] = None

    # ---------------------------------------------------------- images

    def frame(self, index: int = 0) -> bytes:
        """Image `index` de l'animation, prete pour PhotoImage.

        Le dessin ne bouge pas : c'est une lumiere qui le traverse, et
        revient. Un logo qui change de forme au fil des images n'est plus
        un logo — mais une marque parfaitement immobile pendant un
        demarrage se lit comme un ecran fige.

        Le trace, lui, n'est calcule qu'une fois : les images ne font que le
        colorer.
        """
        carte = self._map()
        part = (index % self.count) / self.count
        passage = REFLET_COURSE * (1 - abs(1 - 2 * part)) - REFLET_MARGE
        # Le passage est incline : son eclat ne depend que de
        # « x + pente*y ». Une ligne retrouve donc les valeurs de la
        # precedente, decalees — elles sont calculees une fois pour toutes,
        # et tranchees ligne a ligne.
        glissement = max(1, int(round(REFLET_PENTE * self.height)))
        eclats = [self._reflet((colonne - glissement + 0.5) / self.size,
                               passage)
                  for colonne in range(self.size + glissement + 1)]
        toile: List[bytearray] = []
        for ligne, source in enumerate(carte):
            depart = int(round(glissement * (1 - ligne / max(1, self.height))))
            rendu = bytearray(source)
            for colonne, eclat in enumerate(
                    eclats[depart:depart + self.size]):
                position = colonne * 4
                if not rendu[position + 3] or eclat <= 1.004:
                    continue
                rendu[position] = min(255, int(rendu[position] * eclat))
                rendu[position + 1] = min(255,
                                          int(rendu[position + 1] * eclat))
                rendu[position + 2] = min(255,
                                          int(rendu[position + 2] * eclat))
            toile.append(rendu)
        niveau = 6 if self.size <= RAPIDE_AU_DELA else 1
        return raster.image_data(self.size, self.height, toile, niveau)

    def _map(self) -> List[bytearray]:
        """Le trace, sans la lumiere. Calcule a la premiere demande."""
        if self._carte is None:
            self._carte = self._trace()
        return self._carte

    def _trace(self) -> List[bytearray]:
        """Pose la marque.

        Tout est mesure en parts de la largeur, y compris a la verticale :
        un cadre plus bas que large recadre le dessin, il ne l'aplatit pas.
        """
        size = self.size
        haut = (size - self.height) / 2.0
        pixel = 1.0 / size
        toile: List[bytearray] = []
        for ligne in range(self.height):
            rendu = bytearray(size * 4)
            y = (ligne + haut + 0.5) / size
            for colonne in range(size):
                x = (colonne + 0.5) / size
                couverture = _couverture(distance(x, y), pixel)
                if couverture <= 0.0:
                    continue
                position = colonne * 4
                rendu[position] = ENCRE[0]
                rendu[position + 1] = ENCRE[1]
                rendu[position + 2] = ENCRE[2]
                rendu[position + 3] = min(255, int(couverture * 255 + 0.5))
            toile.append(rendu)
        return toile

    @staticmethod
    def _reflet(x: float, passage: float) -> float:
        """Eclaircissement du au passage de lumiere, a cette abscisse."""
        ecart = (x - passage) / REFLET_LARGEUR
        return 1.0 + REFLET_FORCE * math.exp(-ecart * ecart)


def _couverture(distance: float, pixel: float) -> float:
    """Part d'un pixel couverte par la forme, d'apres sa distance au bord.

    Negative dedans, positive dehors : un bord passe d'opaque a transparent
    sur l'epaisseur d'un pixel, centre sur lui. C'est l'antialiasing — sans
    echantillonner quoi que ce soit.
    """
    part = 0.5 - distance / pixel
    if part <= 0.0:
        return 0.0
    if part >= 1.0:
        return 1.0
    return part


def _trait(x: float, y: float, x1: float, y1: float,
           x2: float, y2: float, epaisseur: float) -> float:
    """Distance signee a un segment a bouts ronds."""
    dx, dy = x2 - x1, y2 - y1
    carre = dx * dx + dy * dy
    if carre <= 0.0:
        place = 0.0
    else:
        place = ((x - x1) * dx + (y - y1) * dy) / carre
        place = 0.0 if place < 0.0 else (1.0 if place > 1.0 else place)
    return math.hypot(x - (x1 + place * dx),
                      y - (y1 + place * dy)) - epaisseur


def _arc(x: float, y: float, cx: float, cy: float, rayon: float,
         debut: float, fin: float, epaisseur: float) -> float:
    """Distance signee a un arc de cercle a bouts ronds.

    Dans le secteur, c'est l'ecart au cercle ; au-dela, c'est la distance
    au bout le plus proche. L'angle se compare au milieu de l'arc, replie
    dans un demi-tour : c'est ce qui evite d'avoir a traiter les arcs qui
    enjambent le zero.
    """
    milieu = math.radians((debut + fin) / 2.0)
    demi = math.radians(abs(fin - debut) / 2.0)
    ecart = math.atan2(y - cy, x - cx) - milieu
    ecart = (ecart + math.pi) % (2 * math.pi) - math.pi
    if abs(ecart) <= demi:
        return abs(math.hypot(x - cx, y - cy) - rayon) - epaisseur
    proche = 9.9
    for angle in (math.radians(debut), math.radians(fin)):
        proche = min(proche, math.hypot(x - (cx + rayon * math.cos(angle)),
                                        y - (cy + rayon * math.sin(angle))))
    return proche - epaisseur


def distance(x: float, y: float) -> float:
    """Distance signee a la marque complete.

    Publique parce que l'icone Windows s'en sert : elle dessine la meme
    marque, en blanc sur un jeton rond. Un outil n'a qu'une identite.
    """
    return MARQUE.distance(x, y)
