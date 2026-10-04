"""La marque de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : une boite a moustaches. L'etendue d'une population, la
boite des deux quartiles du milieu, et la mediane qui la partage — l'objet
meme que l'outil produit, reduit a sa silhouette.

Le choix n'est pas qu'esthetique. Une etoile dit « cinq etoiles », une
coche dit « conforme », une balance dit « justice » : un outil qui mesure
des ecarts de remuneration ne doit porter aucun de ces jugements sur sa
porte. Une boite a moustaches ne dit rien d'autre que ce que fait l'outil :
elle montre une distribution, sans la noter.

Sa teinte ne suit pas le theme et ne change pas avec le fond : un bleu
d'acier, assez clair pour se detacher d'un ecran sombre, assez dense pour
tenir sur un fond blanc. Elle se lit donc aussi bien a l'accueil, sur
l'encre, que pendant une analyse, sur la page.

Tout est analytique. Chaque piece est decrite par sa *distance signee* —
negative dedans, positive dehors —, les pieces se reunissent en prenant la
plus petite, la mediane se creuse en prenant la plus grande de l'une et de
l'opposee de l'autre, et l'opacite d'un pixel se deduit de la distance
finale : un demi-pixel de part et d'autre du bord. Il n'y a donc ni tirage
aleatoire, ni echantillonnage, ni surechantillonnage a payer : le meme
dessin exactement a toutes les tailles, en un seul passage.
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

#: Proportion du cadre : la marque est couchee, comme l'objet qu'elle
#: represente. Un cadre carre lui laisserait deux bandes vides.
RATIO = 0.52

#: Les moustaches : de ou a ou elles vont, leur epaisseur, et le petit
#: trait qui les termine. Sans ces bouts, la marque se lit comme un
#: interrupteur ; avec eux, c'est une etendue bornee.
MOUSTACHE = (0.07, 0.93)
MOUSTACHE_TRAIT = 0.022
BOUT_LARGEUR = 0.050
BOUT_HAUTEUR = 0.105

#: La boite des deux quartiles du milieu : sa demi-largeur, sa
#: demi-hauteur, et l'arrondi de ses coins.
BOITE_DEMI = 0.200
BOITE_HAUTEUR = 0.155
BOITE_COIN = 0.045

#: La mediane. Elle est *creusee* et non posee : un trait d'une autre
#: couleur supposerait un fond connu, alors que la marque se pose aussi
#: bien sur l'encre que sur la page.
MEDIANE_DEMI = 0.018

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


def _barre(x: float, y: float, debut: float, fin: float,
           rayon: float) -> float:
    """Distance signee a un trait horizontal a bouts ronds."""
    place = min(max(x, debut), fin)
    return math.hypot(x - place, y - 0.5) - rayon


def _boite(x: float, y: float, demi_large: float, demi_haut: float,
           coin: float, centre: float = 0.5) -> float:
    """Distance signee a un rectangle a coins arrondis, centre sur la
    ligne mediane du cadre."""
    dx = abs(x - centre) - (demi_large - coin)
    dy = abs(y - 0.5) - (demi_haut - coin)
    dehors = math.hypot(max(dx, 0.0), max(dy, 0.0))
    return dehors + min(max(dx, dy), 0.0) - coin


def distance(x: float, y: float) -> float:
    """Distance signee a la marque : negative dedans, positive dehors.

    Publique parce que l'icone Windows s'en sert : elle dessine la meme
    marque, en blanc sur un jeton rond. Un outil n'a qu'une identite.
    """
    moustaches = _barre(x, y, MOUSTACHE[0], MOUSTACHE[1], MOUSTACHE_TRAIT)
    gauche = _boite(x, y, BOUT_LARGEUR / 2, BOUT_HAUTEUR, MOUSTACHE_TRAIT,
                    MOUSTACHE[0])
    droite = _boite(x, y, BOUT_LARGEUR / 2, BOUT_HAUTEUR, MOUSTACHE_TRAIT,
                    MOUSTACHE[1])
    caisse = _boite(x, y, BOITE_DEMI, BOITE_HAUTEUR, BOITE_COIN)
    forme = min(moustaches, gauche, droite, caisse)
    mediane = _boite(x, y, MEDIANE_DEMI, BOITE_HAUTEUR + BOITE_COIN, 0.0)
    return max(forme, -mediane)
