"""L'etoile de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : une etoile a cinq branches, pleine, d'une seule teinte.
Rien d'autre — pas de jeton, pas de degrade, pas de vernis. Une marque n'a
pas a se faire remarquer : elle se pose a cote du nom, petite, et c'est le
nom qu'on lit. C'est la meme etoile que celle de l'icone Windows
(« packaging/windows/etoile.ico ») — un outil n'a qu'une identite, et
celle-ci se redessine de memoire.

Sa teinte ne suit pas le theme et ne change pas avec le fond : un bleu
d'acier, assez clair pour se detacher d'un ecran sombre, assez dense pour
tenir sur un fond blanc. Elle se lit donc aussi bien a l'accueil, sur
l'encre, que pendant une analyse, sur la page.

Tout est analytique. Le contour est donne par la *distance signee* a
l'etoile — negative dedans, positive dehors —, et l'opacite d'un pixel s'en
deduit : un demi-pixel de part et d'autre du bord. Il n'y a donc ni tirage
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
ETOILE = (110, 148, 186)

#: Rayon de l'etoile, en parts de la largeur du cadre. Le symbole ne touche
#: jamais le bord : il paraitrait coupe des qu'on le pose contre autre
#: chose.
RAYON = 0.455

#: Rayon interne de l'etoile, en part du rayon externe. 0,382 est le
#: rapport de l'etoile a cinq branches reguliere — celle qu'on dessine d'un
#: trait sans lever la main. Plus grand, les branches s'epaississent et le
#: dessin perd sa pointe ; plus petit, elles deviennent des aiguilles
#: illisibles a seize pixels.
CREUX = 0.382

#: Le passage de lumiere, image par image : de combien il eclaircit, sur
#: quelle largeur, son inclinaison, et jusqu'ou il voyage de part et
#: d'autre du cadre. Il ne touche jamais au trace — seulement a sa couleur.
#: Discret : un logo qui clignote pendant un demarrage se regarde au lieu
#: de se laisser oublier.
REFLET_FORCE = 0.34
REFLET_LARGEUR = 0.30
REFLET_PENTE = 0.80
REFLET_COURSE = 1.9
REFLET_MARGE = 0.45

#: Taille au-dela de laquelle l'encodage PNG passe en compression rapide :
#: une planche de mille pixels prend une seconde a compresser au maximum,
#: pour quelques kilooctets gagnes que personne ne transporte.
RAPIDE_AU_DELA = 420

#: Cosinus et sinus de trente-six degres : les deux normales qui replient
#: le plan sur un dixieme de tour. L'etoile a cinq branches est symetrique
#: dix fois ; la distance ne se calcule donc que sur un seul secteur.
_PLI = (0.8090169943749475, -0.5877852522924731)


class Star:
    """Le symbole, et la lumiere qui le traverse, image par image."""

    def __init__(self, size: int, count: int = 1,
                 height: Optional[int] = None):
        """`size` est la largeur ; `height` permet un cadre plus bas que
        large. Le dessin n'est pas etire pour autant : il est cadre."""
        self.size = size
        self.height = height or size
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
        """Pose l'etoile.

        Tout est mesure en parts de la largeur, y compris a la verticale :
        un cadre plus bas que large recadre le dessin, il ne l'aplatit pas.
        """
        size = self.size
        haut = (size - self.height) / 2.0
        pixel = 1.0 / size
        toile: List[bytearray] = []
        for ligne in range(self.height):
            rendu = bytearray(size * 4)
            dy = (ligne + haut + 0.5) / size - 0.5
            for colonne in range(size):
                dx = (colonne + 0.5) / size - 0.5
                couverture = _couverture(_distance(dx, dy), pixel)
                if couverture <= 0.0:
                    continue
                position = colonne * 4
                rendu[position] = ETOILE[0]
                rendu[position + 1] = ETOILE[1]
                rendu[position + 2] = ETOILE[2]
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


def _distance(dx: float, dy: float) -> float:
    """Distance signee a l'etoile : negative dedans, positive dehors.

    Le plan est replie deux fois sur la premiere branche — l'etoile est
    symetrique dix fois —, puis la distance se mesure au seul cote qui
    reste. La premiere pointe regarde vers le haut : une etoile posee de
    travers se remarque immediatement, meme de qui ne saurait pas dire
    pourquoi.
    """
    x, y = abs(dx), -dy
    produit = x * _PLI[0] + y * _PLI[1]
    if produit > 0.0:
        x -= 2 * produit * _PLI[0]
        y -= 2 * produit * _PLI[1]
    produit = -x * _PLI[0] + y * _PLI[1]
    if produit > 0.0:
        x += 2 * produit * _PLI[0]
        y -= 2 * produit * _PLI[1]
    x = abs(x)
    y -= RAYON
    cote = (-_PLI[1] * CREUX, _PLI[0] * CREUX - 1.0)
    longueur = cote[0] * cote[0] + cote[1] * cote[1]
    place = max(0.0, min(RAYON, (x * cote[0] + y * cote[1]) / longueur))
    reste = math.hypot(x - cote[0] * place, y - cote[1] * place)
    return reste if y * cote[0] - x * cote[1] > 0 else -reste
