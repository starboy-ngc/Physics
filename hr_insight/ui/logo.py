"""L'etoile de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : une etoile a cinq branches sur un jeton rond. C'est la
meme marque que celle de l'icone Windows (« packaging/windows/etoile.ico »)
— un outil n'a qu'une identite, et celle-ci se redessine de memoire. Le
jeton porte un degrade, un filet de lumiere sur son arete haute et une
lueur posee autour de lui ; l'etoile, un halo pale au ras de ses branches.
Sans cela le symbole serait un pictogramme, pas une marque.

Tout est analytique. Le contour de l'etoile est donne par sa *distance
signee* — negative dedans, positive dehors —, et l'opacite d'un pixel se
deduit de cette distance : un demi-pixel de part et d'autre du bord. Il n'y
a donc ni tirage aleatoire, ni echantillonnage, ni surechantillonnage a
payer : le meme dessin exactement a toutes les tailles, et le calcul d'un
seul passage.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from . import raster

RGB = Tuple[int, int, int]

#: Couleurs du symbole. Elles ne suivent pas le theme de la fenetre : une
#: marque qui change de couleur avec un reglage d'affichage n'est plus une
#: marque. Ce sont celles de l'icone : le bleu d'ardoise de l'outil, et le
#: blanc.
JETON_HAUT = (47, 86, 124)          # le haut du jeton, vers la lumiere
JETON_BAS = (14, 32, 50)            # son bas, dans l'ombre
ARETE = (112, 162, 208)             # le filet pose sur son bord haut
ETOILE = (255, 255, 255)            # l'etoile elle-meme
HALO = (118, 170, 214)              # ce qu'elle eclaire autour d'elle
LUEUR = (62, 116, 170)              # ce que le jeton pose sur le fond

#: Rayon du jeton et rayon de l'etoile, en parts de la largeur du cadre.
#: L'etoile occupe les deux tiers du jeton : plus grande, ses pointes
#: viennent toucher l'arete ; plus petite, le jeton se lit avant elle.
JETON = 0.385
RAYON = 0.266

#: La lueur posee autour du jeton : de combien elle teinte le fond au ras
#: du bord, et sur quelle distance. Elle a une portee *finie* — elle vaut
#: exactement zero au-dela — pour que le symbole ne touche jamais le bord
#: de son cadre : il paraitrait coupe des qu'on le pose contre autre chose.
LUEUR_FORCE = 0.13
LUEUR_PORTEE = 0.085
LUEUR_CHUTE = 3.0

#: Rayon interne de l'etoile, en part du rayon externe. 0,382 est le
#: rapport de l'etoile a cinq branches reguliere — celle qu'on dessine d'un
#: trait sans lever la main. Plus grand, les branches s'epaississent et le
#: dessin perd sa pointe ; plus petit, elles deviennent des aiguilles
#: illisibles a seize pixels.
CREUX = 0.382

#: Le filet de lumiere sur l'arete du jeton : sa largeur, la direction d'ou
#: vient la lumiere, et la vitesse a laquelle il s'eteint en tournant. Un
#: jeton sans arete est un rond plat ; une arete tout autour est un cerne.
ARETE_LARGEUR = 0.013
ARETE_SOURCE = (-0.31, -0.95)
ARETE_CHUTE = 1.3

#: La lueur pale autour de l'etoile : de combien elle eclaircit le jeton au
#: ras des branches, et sur quelle distance elle se dissipe.
HALO_FORCE = 0.13
HALO_PORTEE = 0.032

#: Le reflet qui traverse le jeton, image par image : de combien il
#: eclaircit, sur quelle largeur, et son inclinaison. Il ne touche jamais
#: au trace — seulement a sa couleur.
REFLET_FORCE = 0.55
REFLET_LARGEUR = 0.26
REFLET_PENTE = 0.85
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
    """Le symbole, et le reflet qui le traverse, image par image."""

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

        Le dessin ne bouge pas : c'est un reflet qui le traverse, et
        revient. Un logo qui change de forme au fil des images n'est plus
        un logo — mais une marque parfaitement immobile pendant un
        demarrage se lit comme un ecran fige.

        Le trace, lui, n'est calcule qu'une fois : les images ne font que le
        colorer. C'est ce qui permet de le calculer *bien* sans le payer
        vingt-quatre fois.
        """
        carte = self._map()
        part = (index % self.count) / self.count
        passage = REFLET_COURSE * (1 - abs(1 - 2 * part)) - REFLET_MARGE
        # Le reflet est incline : son eclat ne depend que de « x + pente*y ».
        # Une ligne retrouve donc les valeurs de la precedente, decalees —
        # elles sont calculees une fois pour toutes, et tranchees ligne a
        # ligne.
        glissement = max(1, int(round(REFLET_PENTE * self.height)))
        etendue = self.size + glissement + 1
        eclats = [self._reflet((colonne - glissement + 0.5) / self.size,
                               passage)
                  for colonne in range(etendue)]
        toile: List[bytearray] = []
        for ligne, source in enumerate(carte):
            depart = int(round(glissement * (1 - ligne / max(1, self.height))))
            tranche = eclats[depart:depart + self.size]
            rendu = bytearray(source)
            for colonne, eclat in enumerate(tranche):
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
        """Le trace, sans le reflet. Calcule a la premiere demande."""
        if self._carte is None:
            self._carte = self._trace()
        return self._carte

    def _trace(self) -> List[bytearray]:
        """Pose le jeton, son arete, la lueur et l'etoile, en un passage.

        Tout est mesure en parts de la largeur, y compris a la verticale :
        un cadre plus bas que large recadre le dessin, il ne l'aplatit pas.
        """
        size = self.size
        hauteur = self.height
        haut = (size - hauteur) / 2.0
        pixel = 1.0 / size
        rayon = JETON
        sommet = 0.5 - rayon
        diametre = 2 * rayon
        toile: List[bytearray] = []
        for ligne in range(hauteur):
            rendu = bytearray(size * 4)
            y = (ligne + haut + 0.5) / size
            dy = y - 0.5
            for colonne in range(size):
                x = (colonne + 0.5) / size
                dx = x - 0.5
                loin = math.hypot(dx, dy)
                jeton = _couverture(loin - rayon, pixel)
                if jeton <= 0.0:
                    # Hors du jeton : il ne reste que la lueur.
                    lueur = _lueur(loin - rayon)
                    if lueur <= 0.0:
                        continue
                    position = colonne * 4
                    rendu[position] = LUEUR[0]
                    rendu[position + 1] = LUEUR[1]
                    rendu[position + 2] = LUEUR[2]
                    rendu[position + 3] = int(lueur * 255 + 0.5)
                    continue
                couleur = _melange(JETON_HAUT, JETON_BAS,
                                   min(1.0, max(0.0, (y - sommet) / diametre)))
                # L'arete : un filet a l'interieur du bord, eteint du cote
                # oppose a la lumiere.
                anneau = jeton - _couverture(
                    loin - (rayon - ARETE_LARGEUR), pixel)
                if anneau > 0.0 and loin > 0.0:
                    face = (dx * ARETE_SOURCE[0] + dy * ARETE_SOURCE[1]) / loin
                    if face > 0.0:
                        couleur = _melange(couleur, ARETE,
                                           anneau * face ** ARETE_CHUTE)
                etoile = _etoile(dx, dy, pixel)
                if etoile < 1.0:
                    dehors = _distance(dx, dy)
                    if dehors < HALO_PORTEE * 3:
                        part = dehors / HALO_PORTEE
                        couleur = _melange(
                            couleur, HALO,
                            HALO_FORCE * math.exp(-part * part))
                if etoile > 0.0:
                    couleur = _melange(couleur, ETOILE, etoile)
                position = colonne * 4
                rendu[position] = couleur[0]
                rendu[position + 1] = couleur[1]
                rendu[position + 2] = couleur[2]
                rendu[position + 3] = min(255, int(jeton * 255 + 0.5))
            toile.append(rendu)
        return toile

    @staticmethod
    def _reflet(x: float, passage: float) -> float:
        """Eclaircissement du au reflet, a cette abscisse."""
        ecart = (x - passage) / REFLET_LARGEUR
        return 1.0 + REFLET_FORCE * math.exp(-ecart * ecart)


def _couverture(distance: float, pixel: float) -> float:
    """Part d'un pixel couverte par une forme, d'apres sa distance au bord.

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


def _lueur(ecart: float) -> float:
    """Opacite de la lueur, a cette distance du bord du jeton."""
    if ecart >= LUEUR_PORTEE:
        return 0.0
    reste = 1.0 - max(0.0, ecart) / LUEUR_PORTEE
    return LUEUR_FORCE * reste ** LUEUR_CHUTE


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


def _etoile(dx: float, dy: float, pixel: float) -> float:
    """Part du pixel couverte par l'etoile."""
    return _couverture(_distance(dx, dy), pixel)


def _melange(first: RGB, second: RGB, part: float) -> RGB:
    if part <= 0.0:
        return first
    if part >= 1.0:
        return second
    return tuple(int(round(a + (b - a) * part))
                 for a, b in zip(first, second))
