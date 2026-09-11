"""L'aurore de l'outil, dessinee a la formule.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. Le symbole est
donc *calcule*, puis encode en PNG par le module « raster », qui sait deja
le faire pour les points du nuage.

Ce qu'il montre : une aurore, c'est-a-dire un ruban de lumiere qui ondule et
se dissipe vers le haut. Deux formes suffisent — le ruban et son echo —,
decrites par une seule onde. Un symbole n'a pas a etre une illustration : il
doit se reconnaitre a vingt-quatre pixels comme a deux mille, et l'on doit
pouvoir le redessiner de memoire.

Tout est analytique : pour chaque pixel on calcule sa distance a l'onde, et
la couverture s'en deduit. Il n'y a ni tirage aleatoire, ni echantillonnage
— donc aucun grain a faire grossir quand l'image grandit, et le meme dessin
exactement a toutes les tailles.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from . import raster

RGB = Tuple[int, int, int]

#: Couleurs du symbole. Elles ne suivent pas le theme de la fenetre : une
#: marque qui change de couleur avec un reglage d'affichage n'est plus une
#: marque. Du vert au violet, les deux teintes que prend une aurore.
GREEN = (74, 201, 150)
TEAL = (72, 168, 196)
VIOLET = (146, 120, 214)

#: L'onde : une periode dans la largeur, soit une crete et un creux — un S,
#: plus franc a lire qu'une bosse.
PERIODS = 1.0
AMPLITUDE = 0.17

#: Les trois rubans, du plus bas au plus haut. Pour chacun : hauteur au
#: repos, epaisseur, opacite, couleur. Un ruban de plus serait un dessin ;
#: un de moins, un trait ondule.
#: Chaque ruban est aussi plus court que celui d'en dessous : c'est ce
#: retrait qui fait un rideau plutot que trois traits paralleles.
#: Chacun porte aussi un leger decalage d'onde : les rubans se suivent au
#: lieu de se superposer, et le rideau parait derive par le vent solaire.
RIBBONS = (
    (0.615, 0.135, 1.00, 0.38, 0.000, GREEN),
    (0.460, 0.075, 0.92, 0.44, 0.035, TEAL),
    (0.340, 0.045, 0.80, 0.50, 0.070, VIOLET),
)

#: Marge laissee de chaque cote : les pointes ne touchent pas le bord de
#: l'image, sans quoi le symbole parait coupe des qu'on le pose contre autre
#: chose.
INSET = 0.06

#: La lueur qui parcourt le symbole : de combien elle eclaircit, sur quelle
#: largeur, et jusqu'ou elle voyage de part et d'autre du cadre. Elle ne
#: touche jamais au trace — seulement a sa couleur.
GLOW_STRENGTH = 0.42
GLOW_WIDTH = 0.26
GLOW_TRAVEL = 1.5
GLOW_MARGIN = 0.25

#: Douceur du bord, en parts de l'epaisseur. Assez pour qu'une aurore n'ait
#: pas de contour, assez peu pour que le symbole reste franc a vingt-quatre
#: pixels.
SOFTNESS = 0.12


class Aurora:
    """Le symbole, et son ondulation lente, image par image."""

    def __init__(self, size: int, count: int = 1,
                 height: Optional[int] = None):
        """`size` est la largeur ; `height` permet un cadre plus bas que
        large — une aurore s'inscrit mal dans un carre, ou elle laisse deux
        bandes vides. Le dessin n'est pas etire pour autant : il est cadre."""
        self.size = size
        self.height = height or size
        self.count = max(1, count)

    # ---------------------------------------------------------- lecture

    def frame(self, index: int = 0) -> bytes:
        """Image `index` de l'animation, prete pour PhotoImage.

        Le dessin ne bouge pas : c'est une lueur qui le parcourt, de gauche
        a droite, et revient. Un logo qui change de forme au fil des images
        n'est plus un logo — mais une aurore immobile n'est pas une aurore.

        Le trace se fait colonne par colonne et ruban par ruban : pour une
        abscisse donnee, un ruban n'occupe qu'une poignee de lignes. Balayer
        l'image entiere pour chacun couterait dix fois plus, et l'ecran
        d'accueil calcule ces images pendant qu'il est deja affiche.
        """
        size = self.size
        # La lueur traverse le cadre puis reprend : l'aller-retour boucle
        # sans saut, contrairement a un simple defilement.
        part = (index % self.count) / self.count
        lueur = GLOW_TRAVEL * (1 - abs(1 - 2 * part)) - GLOW_MARGIN
        toile = [bytearray(size * 4) for _ in range(self.height)]
        for base, epaisseur, force, bord, decalage, couleur in RIBBONS:
            self._draw(toile, size, decalage, base, epaisseur, force,
                       bord, couleur, lueur)
        return raster.image_data(size, self.height, toile, 6)

    def _draw(self, toile, size: int, phase: float, base: float,
              epaisseur: float, opacite: float, bord: float,
              couleur: RGB, lueur: float) -> None:
        """Pose un ruban sur la toile, colonne par colonne."""
        rouge, vert, bleu = couleur
        # Tout est mesure en parts de la largeur, y compris a la verticale :
        # un cadre plus bas que large recadre le dessin, il ne l'aplatit pas.
        haut = (size - self.height) / 2.0
        for colonne in range(size):
            x = (colonne + 0.5) / size
            demi = epaisseur * self._taper(x, bord) / 2.0
            if demi <= 0.0:
                continue
            angle = 2 * math.pi * (PERIODS * x + phase)
            onde = base + AMPLITUDE * math.sin(angle)
            pente = AMPLITUDE * 2 * math.pi * PERIODS * math.cos(angle)
            correction = math.sqrt(1.0 + pente * pente)
            douceur = demi * SOFTNESS
            # Lueur : elle eclaircit la couleur sans toucher au trace.
            ecart_lueur = (x - lueur) / GLOW_WIDTH
            eclat = 1.0 + GLOW_STRENGTH * math.exp(-ecart_lueur * ecart_lueur)
            rouge_x = min(255, int(rouge * eclat))
            vert_x = min(255, int(vert * eclat))
            bleu_x = min(255, int(bleu * eclat))
            portee = (demi + douceur) * correction
            premiere = max(0, int((onde - portee) * size - haut))
            derniere = min(self.height - 1,
                           int((onde + portee) * size - haut) + 1)
            for ligne in range(premiere, derniere + 1):
                y = (ligne + haut + 0.5) / size
                couverture = self._coverage(y, onde, demi, douceur, correction)
                if couverture <= 0.004:
                    continue
                couverture *= opacite
                cible = toile[ligne]
                position = colonne * 4
                ancienne = cible[position + 3] / 255.0
                melange = couverture + ancienne * (1 - couverture)
                cible[position] = int(
                    (rouge_x * couverture
                     + cible[position] * ancienne * (1 - couverture)) / melange)
                cible[position + 1] = int(
                    (vert_x * couverture
                     + cible[position + 1] * ancienne * (1 - couverture))
                    / melange)
                cible[position + 2] = int(
                    (bleu_x * couverture
                     + cible[position + 2] * ancienne * (1 - couverture))
                    / melange)
                cible[position + 3] = min(255, int(melange * 255))

    @staticmethod
    def _coverage(y: float, onde: float, demi: float, douceur: float,
                  correction: float) -> float:
        """Part du pixel couverte par le ruban, bord adouci.

        La distance a une courbe qui est le graphe d'une fonction se calcule
        sans chercher le point le plus proche : l'ecart vertical, corrige de
        la pente. C'est exact au premier ordre, et une onde de cette
        amplitude n'en demande pas plus.
        """
        ecart = abs(y - onde) / correction
        if ecart >= demi + douceur:
            return 0.0
        if ecart <= demi - douceur:
            couverture = 1.0
        else:
            part = (demi + douceur - ecart) / (2 * douceur)
            couverture = part * part * (3 - 2 * part)
        # La lumiere monte et se dissipe : le bord superieur s'efface, le
        # bord inferieur reste franc. C'est ce desequilibre qui distingue
        # une aurore d'un simple trait ondule.
        if y < onde:
            couverture *= 1.0 - 0.18 * (onde - y) / (demi + douceur)
        return couverture

    @staticmethod
    def _taper(x: float, bord: float) -> float:
        """Affinement aux deux extremites, de zero a l'epaisseur pleine.

        Il occupe plus d'un tiers de la longueur : un affinement bref donne
        une pointe coupee au couteau, la ou l'on attend un trait de pinceau.
        """
        utile = 1.0 - 2 * INSET
        position = (x - INSET) / utile
        if position <= 0.0 or position >= 1.0:
            return 0.0
        if position < bord:
            part = position / bord
        elif position > 1 - bord:
            part = (1 - position) / bord
        else:
            return 1.0
        return part * part * (3 - 2 * part)
