"""La galaxie de l'outil, dessinee point par point.

Un logo est un fichier image dans la plupart des logiciels. Ici il n'en est
pas question : embarquer un binaire opaque dans une archive que le service
informatique doit pouvoir relire irait contre tout le reste. La galaxie est
donc *calculee* — quelques centaines d'etoiles posees sur deux bras en
spirale, un bulbe au centre, et une rotation d'ensemble — puis encodee en
PNG par le module « raster », qui sait deja le faire pour les points du
nuage.

Le tirage est deterministe : la meme galaxie a chaque ouverture. Un logo qui
changerait de forme d'un lancement a l'autre ne serait pas un logo.
"""

from __future__ import annotations

import math
import random
from typing import List, Sequence, Tuple

from . import raster

RGB = Tuple[int, int, int]

#: Graine du tirage. Elle fixe la forme de la galaxie une fois pour toutes.
SEED = 20260911

#: Nombre d'etoiles a la taille de reference. Assez pour que les bras se
#: lisent, assez peu pour que la rotation entiere se calcule en un quart de
#: seconde.
STARS = 3200

#: Taille pour laquelle ce nombre a ete choisi, en pixels. Au-dela, la
#: densite suit la surface et le point grossit : sans cela, une galaxie
#: agrandie se defait en grains isoles — les bras ne tiennent que par le
#: nombre d'etoiles au centimetre carre.
REFERENCE = 156

#: Bras de la spirale, et enroulement (en tours du centre au bord).
ARMS = 2
WINDING = 1.0

#: Part des etoiles rassemblees dans le bulbe central.
BULGE = 0.18


def _stars(count: int) -> List[Tuple[float, float, float, float]]:
    """Etoiles en coordonnees polaires : rayon, angle, eclat, chaleur.

    La chaleur va de 0 (bleu des bras, jeunes etoiles) a 1 (or du bulbe) :
    c'est ce degrade qui fait lire une galaxie plutot qu'un tourbillon.
    """
    tirage = random.Random(SEED)
    etoiles: List[Tuple[float, float, float, float]] = []
    bulbe = int(count * BULGE)
    for _ in range(bulbe):
        rayon = abs(tirage.gauss(0.0, 0.075))
        # Les etoiles du bulbe sont volontairement discretes : c'est le
        # halo qui fait la lumiere du centre. Trop vives, elles donnaient
        # une boule grumeleuse plutot qu'un noyau.
        etoiles.append((min(rayon, 0.24), tirage.uniform(0, 2 * math.pi),
                        tirage.uniform(0.30, 0.60),
                        tirage.uniform(0.80, 1.0)))
    for index in range(count - bulbe):
        rayon = 0.10 + 0.88 * math.sqrt(tirage.random())
        bras = (index % ARMS) * (2 * math.pi / ARMS)
        # Spirale : l'angle croit avec le rayon. L'ecart au bras s'ouvre
        # vers l'exterieur — un bras parfaitement net ferait un dessin, pas
        # une galaxie.
        ouverture = 0.07 + 0.26 * rayon
        if index % 4 == 0:
            # Une etoile sur quatre s'ecarte franchement : c'est ce voile
            # entre les bras qui empeche la spirale de ressembler a deux
            # rubans peints. Sans lui, la galaxie tient en vignette et se
            # defait des qu'on l'agrandit.
            ouverture *= 2.6
        angle = bras + WINDING * 2 * math.pi * rayon + tirage.gauss(0, ouverture)
        eclat = max(0.15, (1.0 - rayon) ** 0.9) * tirage.uniform(0.35, 1.0)
        # Le bleu des bras gagne vite : au tiers du rayon, plus rien d'or.
        chaleur = max(0.0, 1.0 - rayon / 0.42) * tirage.uniform(0.6, 1.1)
        etoiles.append((rayon * tirage.uniform(0.97, 1.03), angle, eclat,
                        min(chaleur, 1.0)))
    return etoiles


def _weight(kernel) -> float:
    """Lumiere totale d'un point, tous ses pixels additionnes."""
    return sum(poids for _dx, _dy, poids in kernel)


def _kernel(radius: int):
    """Noyau du point : une etoile n'est pas un pixel.

    Un seul pixel ferait scintiller la galaxie au lieu de la faire tourner,
    et l'agrandir la reduirait a de la poussiere. Le rayon suit donc la
    taille de l'image, et la lumiere y decroit en cloche.
    """
    noyau = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            distance = math.hypot(dx, dy)
            if distance > radius + 0.5:
                continue
            noyau.append((dx, dy, math.exp(-(distance / (radius * 0.85)) ** 2)))
    return tuple(noyau)


def _mix(cold: RGB, warm: RGB, part: float) -> RGB:
    return tuple(int(round(c + (w - c) * part)) for c, w in zip(cold, warm))


class Galaxy:
    """Une galaxie et sa rotation, image par image.

    Les images se calculent une a une : la premiere suffit a afficher
    l'ecran d'accueil, les suivantes arrivent pendant qu'il est deja la.
    Une rotation complete pese un quart de seconde de calcul — ce n'est pas
    un temps qu'on fait attendre avant d'afficher quoi que ce soit.
    """

    def __init__(self, size: int, count: int, cold: RGB, warm: RGB,
                 flatten: float = 1.0):
        self.size = size
        self.count = count
        self.cold = cold
        self.warm = warm
        self.flatten = flatten
        # Densite et grosseur du point suivent la taille demandee : la
        # galaxie doit se tenir aussi bien en vignette qu'en grand.
        echelle = size / REFERENCE
        self.stars = _stars(max(240, int(STARS * echelle * echelle)))
        # Le point grossit moins vite que l'image : a taille de logo il
        # tient en trois pixels, et une galaxie rendue en grand garde des
        # etoiles piquees plutot que des taches floues.
        self.kernel = _kernel(max(1, round(math.sqrt(echelle))))
        # La lumiere s'ajoute : deux fois plus d'etoiles, chacune deux fois
        # plus large, et la galaxie vire au ruban blanc. L'eclat de chaque
        # etoile est donc divise par ce que le point a gagne en surface —
        # la meme galaxie, simplement plus fine.
        self.gain = _weight(_kernel(1)) / _weight(self.kernel)
        self._centre = size / 2.0
        self._radius = self._centre * 0.92

    def frame(self, index: int) -> bytes:
        """Image `index` de la rotation, prete pour PhotoImage."""
        tour = 2 * math.pi * index / self.count
        size = self.size
        toile = [[0.0] * (size * 3) for _ in range(size)]
        for rayon, angle, eclat, chaleur in self.stars:
            theta = angle + tour
            x = self._centre + math.cos(theta) * rayon * self._radius
            y = (self._centre
                 + math.sin(theta) * rayon * self._radius * self.flatten)
            rouge, vert, bleu = _mix(self.cold, self.warm, chaleur)
            _pose(toile, size, x, y, eclat * self.gain, rouge, vert, bleu,
                  self.kernel)
        # Deux halos : un noyau franc, et un voile trois fois plus large
        # qui l'adoucit. Un seul halo assez fort pour se voir saturait au
        # centre et donnait, en grand, un disque jaune parfaitement plat.
        _glow(toile, size, self._centre, self._radius * 0.17, self.warm, 0.62)
        _glow(toile, size, self._centre, self._radius * 0.44, self.warm, 0.16)
        # Compression rapide : l'image vit une seconde a l'ecran, elle n'a
        # pas a etre compacte.
        return raster.image_data(size, size, _to_rows(toile, size), 1)


def _pose(toile, size: int, x: float, y: float, eclat: float,
          rouge: int, vert: int, bleu: int, noyau) -> None:
    base_x, base_y = int(x), int(y)
    for dx, dy, poids in noyau:
        px, py = base_x + dx, base_y + dy
        if not (0 <= px < size and 0 <= py < size):
            continue
        force = eclat * poids
        ligne = toile[py]
        index = px * 3
        # Somme des lumieres : deux etoiles voisines font un point plus
        # clair, comme dans le ciel.
        ligne[index] += rouge * force
        ligne[index + 1] += vert * force
        ligne[index + 2] += bleu * force


def _glow(toile, size: int, centre: float, rayon: float, warm: RGB,
          force_max: float) -> None:
    """Halo du bulbe : la lumiere du centre deborde sur ses voisins."""
    portee = int(rayon * 3)
    for y in range(max(0, int(centre - portee)), min(size, int(centre + portee))):
        ligne = toile[y]
        for x in range(max(0, int(centre - portee)),
                       min(size, int(centre + portee))):
            distance = math.hypot(x - centre, y - centre)
            force = math.exp(-(distance / rayon) ** 2) * force_max
            if force < 0.004:
                continue
            index = x * 3
            ligne[index] += warm[0] * force
            ligne[index + 1] += warm[1] * force
            ligne[index + 2] += warm[2] * force


def _to_rows(toile, size: int) -> List[bytearray]:
    """Lignes RVBA. L'opacite suit la lumiere : le logo se pose alors sur
    n'importe quel fond sans rectangle autour de lui.

    Ecrit dans des octets plutot que dans des listes d'entiers : c'est la
    moitie du temps de calcul d'une image, et il y en a vingt-quatre.
    """
    rows: List[bytearray] = []
    for y in range(size):
        source = toile[y]
        ligne = bytearray(size * 4)
        for x in range(size):
            index = x * 3
            rouge = source[index]
            vert = source[index + 1]
            bleu = source[index + 2]
            clarte = rouge if rouge > vert else vert
            if bleu > clarte:
                clarte = bleu
            if clarte <= 0.5:
                continue
            if clarte > 255.0:
                # Sature : on garde la teinte, on ramene l'intensite.
                facteur = 255.0 / clarte
                rouge *= facteur
                vert *= facteur
                bleu *= facteur
                clarte = 255.0
            sortie = x * 4
            ligne[sortie] = int(rouge)
            ligne[sortie + 1] = int(vert)
            ligne[sortie + 2] = int(bleu)
            ligne[sortie + 3] = int(clarte)
        rows.append(ligne)
    return rows
