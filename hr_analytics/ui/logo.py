"""La marque de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : une galaxie, reduite a ce qui la fait reconnaitre — un
noyau et deux bras. Les bras sont des *spirales logarithmiques*, qui est
la forme que prennent reellement les galaxies spirales : leur rayon suit
« r = depart·e^(croissance·theta) ». Le logarithme n'est donc pas un
ornement — c'est aussi l'echelle sur laquelle une distribution de
remunerations se lit, parce que les ecarts y sont multiplicatifs et non
additifs.

Le choix n'est pas qu'esthetique. Une etoile dit « cinq etoiles », une
coche dit « conforme », une balance dit « justice » : un outil qui mesure
des ecarts de remuneration ne doit porter aucun de ces jugements sur sa
porte. Une galaxie ne juge personne : elle montre une population
nombreuse, dense au centre et clairsemee aux bords — ce qu'est une
distribution.

Les bras s'affinent en s'eloignant du noyau. Une spirale d'epaisseur
constante se lit comme un ressort ; celle-ci se lit comme un bras.

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

La distance a un bras ne se cherche pas point par point. Pour un point
donne, l'angle auquel la spirale atteint son rayon se calcule
directement ; on retient le tour dont l'angle tombe le plus pres, et
l'ecart restant est radial. La pente d'une spirale logarithmique etant
constante, cet ecart se ramene a une distance perpendiculaire par un
facteur fixe. Cela coute une exponentielle par pixel, la ou un decoupage
du bras en segments en couterait cent.
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

#: Le noyau : son rayon, en parts de la largeur du cadre.
NOYAU = 0.075

#: Les bras : rayon de depart, rayon d'arrivee, et nombre de tours. Le
#: facteur de croissance s'en deduit — c'est le « b » de la spirale
#: logarithmique, et il n'a donc pas a etre devine.
BRAS_DEPART = 0.145
BRAS_FIN = 0.445
TOURS = 0.85

#: Demi-epaisseur d'un bras, a son depart et a son extremite.
TRAIT_DEPART = 0.046
TRAIT_FIN = 0.022

#: Nombre de bras, repartis sur le tour. Deux : c'est ce qui fait une
#: spirale plutot qu'une rosace.
BRAS = 2

#: Proportion du cadre : une galaxie s'inscrit dans un carre.
RATIO = 1.0

#: Croissance de la spirale, et sa pente. Le facteur de correction est
#: constant le long d'une spirale logarithmique : c'est ce qui permet de
#: ramener un ecart radial a une distance perpendiculaire sans chercher
#: le vrai point le plus proche.
_ANGLE = TOURS * 2 * math.pi
_CROISSANCE = math.log(BRAS_FIN / BRAS_DEPART) / _ANGLE
_PENTE = math.sqrt(1.0 + _CROISSANCE * _CROISSANCE)
_PAS = 2 * math.pi / BRAS

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


def _epaisseur(part: float) -> float:
    """Demi-epaisseur du bras a cette part du parcours, du noyau au bout."""
    return TRAIT_DEPART + (TRAIT_FIN - TRAIT_DEPART) * part


def _bras(dx: float, dy: float, rayon: float, angle: float,
          decalage: float) -> float:
    """Distance signee a un bras, noyau exclu."""
    # L'angle auquel la spirale passe a ce rayon, puis le tour dont la
    # direction tombe le plus pres de celle du point.
    vise = math.log(rayon / BRAS_DEPART) / _CROISSANCE
    direction = angle - decalage
    tours = round((vise - direction) / (2 * math.pi))
    theta = direction + tours * 2 * math.pi
    borne = 0.0 if theta < 0.0 else (_ANGLE if theta > _ANGLE else theta)
    sur_bras = BRAS_DEPART * math.exp(_CROISSANCE * borne)
    epaisseur = _epaisseur(borne / _ANGLE)
    if borne != theta:
        # Hors du parcours : la distance au bout, bout rond compris.
        pose = borne + decalage
        return math.hypot(dx - sur_bras * math.cos(pose),
                          dy - sur_bras * math.sin(pose)) - epaisseur
    # Dans le parcours : l'ecart est radial, et la pente constante de la
    # spirale le ramene a une distance perpendiculaire.
    return abs(rayon - sur_bras) / _PENTE - epaisseur


def distance(x: float, y: float) -> float:
    """Distance signee a la marque : negative dedans, positive dehors.

    Publique parce que l'icone Windows s'en sert : elle dessine la meme
    marque, en blanc sur un jeton rond. Un outil n'a qu'une identite.
    """
    dx, dy = x - 0.5, y - 0.5
    rayon = math.hypot(dx, dy)
    plus_proche = rayon - NOYAU
    if rayon > 0.0:
        angle = math.atan2(dy, dx)
        for rang in range(BRAS):
            valeur = _bras(dx, dy, rayon, angle, rang * _PAS)
            if valeur < plus_proche:
                plus_proche = valeur
    return plus_proche


#: Le jeton : la meme galaxie, blanche sur un disque bleu d'ardoise. C'est
#: sous cette forme que l'outil se montre partout ou il n'a pas choisi son
#: fond — l'icone du raccourci, celle de la barre des taches, celle du
#: coin de la fenetre. Un raccourci se pose sur le fond d'ecran de
#: l'utilisateur, qui peut etre de n'importe quelle teinte : une marque
#: posee a nu y disparait un poste sur deux. Le disque lui donne son fond.
JETON_FOND = (0x1F, 0x3A, 0x55)
JETON_MARQUE = (0xFF, 0xFF, 0xFF)

#: Part du jeton occupee par la marque, en largeur. L'air autour fait
#: autant que la marque elle-meme : une icone qui remplit son jeton se lit
#: comme une pastille, pas comme un symbole.
JETON_EMPRISE = 0.70

#: Amincissement du trace, en parts de la largeur de la marque. Une forme
#: claire sur un fond sombre parait plus epaisse qu'elle ne l'est — l'oeil
#: deborde sur le fond, et un trait blanc gagne visuellement ce que le
#: meme trait en bleu sur l'ecran d'accueil n'a pas. On lui retire donc ce
#: qu'il gagne, pour que les deux dessins se ressemblent vraiment.
JETON_CORRECTION = 0.004

#: Echantillons par cote d'un pixel pour le bord du disque. Quatre par
#: quatre suffisent — a huit la difference ne se voit plus, et le calcul
#: quadruple. La marque, elle, a sa distance signee : son bord est exact.
JETON_FINESSE = 4


def jeton_pixels(taille: int) -> bytes:
    """Le jeton a cette taille, en pixels RGBA bruts.

    Un disque plutot qu'un carre : une icone carree se confond avec les
    tuiles du bureau, un disque se reconnait de loin.
    """
    centre = taille / 2.0
    rayon = centre - max(taille * 0.02, 0.5)
    emprise = taille * JETON_EMPRISE
    pixel = 1.0 / emprise
    pas = 1.0 / JETON_FINESSE
    total = JETON_FINESSE * JETON_FINESSE
    pixels = bytearray()
    for y in range(taille):
        for x in range(taille):
            dedans = 0
            for sy in range(JETON_FINESSE):
                for sx in range(JETON_FINESSE):
                    px = x + (sx + 0.5) * pas - centre
                    py = y + (sy + 0.5) * pas - centre
                    if px * px + py * py <= rayon * rayon:
                        dedans += 1
            if dedans == 0:
                pixels += bytes((0, 0, 0, 0))
                continue
            # La marque vit dans un cadre de largeur 1 dont la ligne
            # mediane est a 0,5 : on y ramene le point avant de lui
            # demander sa distance.
            part = _couverture(
                distance((x + 0.5 - centre) / emprise + 0.5,
                         (y + 0.5 - centre) / emprise + 0.5)
                + JETON_CORRECTION, pixel)
            pixels += bytes(round(JETON_FOND[canal] * (1 - part)
                                  + JETON_MARQUE[canal] * part)
                            for canal in range(3))
            pixels += bytes((round(255 * dedans / total),))
    return bytes(pixels)


def jeton(taille: int) -> bytes:
    """Le jeton a cette taille, en PNG, pret pour PhotoImage."""
    brut = jeton_pixels(taille)
    largeur = taille * 4
    lignes = [bytearray(brut[y * largeur:(y + 1) * largeur])
              for y in range(taille)]
    niveau = 6 if taille <= RAPIDE_AU_DELA else 1
    return raster.image_data(taille, taille, lignes, niveau)
