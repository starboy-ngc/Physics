"""La marque de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : une courbe de distribution et sa mediane. La silhouette
d'une population — beaucoup de monde autour du milieu, de moins en moins
en s'en eloignant — et le trait qui la partage en deux moities egales.
C'est l'objet meme que l'outil produit, reduit a sa silhouette.

Le choix n'est pas qu'esthetique. Une etoile dit « cinq etoiles », une
coche dit « conforme », une balance dit « justice » : un outil qui mesure
des ecarts de remuneration ne doit porter aucun de ces jugements sur sa
porte. Une courbe de distribution ne dit rien d'autre que ce que fait
l'outil : elle montre une population, sans la noter.

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

La distance a la courbe se mesure a la perpendiculaire : l'ecart vertical
au trace, rapporte a la pente. C'est exact pour une droite et juste a la
courbure pres pour une cloche — l'erreur vaut quelques centiemes de pixel,
la ou chercher le vrai point le plus proche couterait cent fois le prix
pour le meme dessin.
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

#: Proportion du cadre : celle de la courbe, median compris. Un cadre
#: carre lui laisserait deux bandes vides.
RATIO = 0.70

#: La cloche : la ligne de base ou retombent ses queues, la hauteur du
#: sommet au-dessus d'elle, et sa largeur. Ces trois nombres suffisent a
#: la decrire entierement — c'est la meme courbe a toutes les echelles.
BASE = 0.648
AMPLITUDE = 0.42
LARGEUR = 0.185

#: De ou a ou la courbe est tracee, et la demi-epaisseur du trait. Au-dela
#: de ces bornes, ses queues seraient confondues avec la ligne de base.
COURBE = (0.06, 0.94)
TRAIT = 0.038

#: La mediane : de la pointe du sommet jusque sous la ligne de base, et sa
#: demi-epaisseur. Elle part de l'interieur du trait — un trait qui
#: s'arreterait au ras du sommet laisserait un interstice visible des
#: qu'on agrandit.
MEDIANE = (0.262, 0.784)
MEDIANE_TRAIT = 0.026

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


def _cloche(x: float) -> float:
    """Hauteur de la courbe a cette abscisse. Plus c'est haut sur l'ecran,
    plus la valeur est petite : l'ordonnee descend."""
    ecart = (x - 0.5) / LARGEUR
    return BASE - AMPLITUDE * math.exp(-ecart * ecart)


def _pente(x: float) -> float:
    """Pente de la courbe : elle corrige la distance la ou elle est
    raide."""
    ecart = (x - 0.5) / LARGEUR
    return AMPLITUDE * 2 * ecart / LARGEUR * math.exp(-ecart * ecart)


def _trait_courbe(x: float, y: float) -> float:
    """Distance signee au trait de la courbe, bouts arrondis compris."""
    debut, fin = COURBE
    if x < debut:
        return math.hypot(x - debut, y - _cloche(debut)) - TRAIT
    if x > fin:
        return math.hypot(x - fin, y - _cloche(fin)) - TRAIT
    pente = _pente(x)
    return abs(y - _cloche(x)) / math.sqrt(1.0 + pente * pente) - TRAIT


def _trait_mediane(x: float, y: float) -> float:
    """Distance signee au trait vertical de la mediane."""
    haut, bas = MEDIANE
    return math.hypot(x - 0.5, y - min(max(y, haut), bas)) - MEDIANE_TRAIT


def distance(x: float, y: float) -> float:
    """Distance signee a la marque : negative dedans, positive dehors.

    Publique parce que l'icone Windows s'en sert : elle dessine la meme
    marque, en blanc sur un jeton rond. Un outil n'a qu'une identite.
    """
    return min(_trait_courbe(x, y), _trait_mediane(x, y))
