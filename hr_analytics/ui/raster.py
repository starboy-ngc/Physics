"""Petites images antialiasees, dessinees a la main.

Le canevas Tk ne lisse pas ses traces : un disque de cinq pixels y devient
un carre a coins ronges, et une coche tracee a la ligne un escalier. Il
sait en revanche afficher des images PNG avec transparence.

Ce module produit donc ces images, en echantillonnant la couverture de
chaque pixel : une forme est decrite par un predicat "ce point est-il a
l'interieur", et l'opacite d'un pixel vaut la proportion de ses
echantillons qui repondent oui. C'est de l'antialiasing par supersampling,
en une trentaine de lignes et sans la moindre dependance — aucune
bibliotheque d'images n'est installee sur le poste, et il n'est pas
question d'en exiger une.

Les images sont minuscules (moins de 200 octets) et mises en cache : elles
sont calculees une fois par couleur, pas une fois par point.
"""

from __future__ import annotations

import base64
import math
import struct
import zlib
from typing import Callable, Dict, Sequence, Tuple

RGB = Tuple[int, int, int]

#: Echantillons par cote et par pixel. 4 (soit 16 par pixel) suffit : au-dela
#: la difference n'est plus visible a l'ecran, et le cout croit au carre.
SAMPLES = 4


def _png(width: int, height: int, pixels: Sequence[Sequence[int]],
         level: int = 9) -> bytes:
    """Encode une image RVBA en PNG, sans filtrage de ligne."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        payload = tag + data
        return (struct.pack(">I", len(data)) + payload
                + struct.pack(">I", zlib.crc32(payload)))

    body = b"".join(b"\x00" + bytes(row) for row in pixels)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(body, level))
            + chunk(b"IEND", b""))


class Raster:
    """Grille RVBA sur laquelle on pose des formes, par couverture."""

    def __init__(self, size: int):
        self.size = size
        # (rouge, vert, bleu, alpha) en flottants 0-1, pour composer sans
        # accumuler les arrondis.
        self.pixels = [[(0.0, 0.0, 0.0, 0.0)] * size for _ in range(size)]

    def paint(self, inside: Callable[[float, float], bool], colour: RGB,
              samples: int = SAMPLES) -> "Raster":
        """Pose une forme, l'opacite suivant la couverture de chaque pixel."""
        red, green, blue = (channel / 255.0 for channel in colour)
        step = 1.0 / samples
        for y in range(self.size):
            row = self.pixels[y]
            for x in range(self.size):
                hits = 0
                for sub_y in range(samples):
                    point_y = y + (sub_y + 0.5) * step
                    for sub_x in range(samples):
                        if inside(x + (sub_x + 0.5) * step, point_y):
                            hits += 1
                if not hits:
                    continue
                coverage = hits / (samples * samples)
                base_r, base_g, base_b, base_a = row[x]
                alpha = coverage + base_a * (1 - coverage)
                # Composition "source over", en couleurs pre-multipliees.
                row[x] = (
                    (red * coverage + base_r * base_a * (1 - coverage)) / alpha,
                    (green * coverage + base_g * base_a * (1 - coverage)) / alpha,
                    (blue * coverage + base_b * base_a * (1 - coverage)) / alpha,
                    alpha,
                )
        return self

    def to_png(self) -> bytes:
        rows = []
        for line in self.pixels:
            row = []
            for red, green, blue, alpha in line:
                row += [round(red * 255), round(green * 255),
                        round(blue * 255), round(alpha * 255)]
            rows.append(row)
        return _png(self.size, self.size, rows)

    def to_data(self) -> bytes:
        """Forme attendue par tkinter.PhotoImage(data=...)."""
        return base64.b64encode(self.to_png())


# ------------------------------------------------------------------ formes


def _circle(centre: float, radius: float) -> Callable[[float, float], bool]:
    def inside(x: float, y: float) -> bool:
        dx, dy = x - centre, y - centre
        return dx * dx + dy * dy <= radius * radius

    return inside


def _rounded_box(low: float, high: float,
                 corner: float) -> Callable[[float, float], bool]:
    """Carre a coins arrondis, par distance signee."""

    def inside(x: float, y: float) -> bool:
        dx = max(low + corner - x, x - (high - corner), 0.0)
        dy = max(low + corner - y, y - (high - corner), 0.0)
        if x < low or x > high or y < low or y > high:
            return False
        return dx * dx + dy * dy <= corner * corner

    return inside


def _segments(points: Sequence[Tuple[float, float]],
              width: float) -> Callable[[float, float], bool]:
    """Ligne brisee epaisse, extremites et coins arrondis."""
    half = width / 2.0

    def inside(x: float, y: float) -> bool:
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            dx, dy = x2 - x1, y2 - y1
            length = dx * dx + dy * dy
            if length == 0:
                position = 0.0
            else:
                position = max(0.0, min(1.0,
                                        ((x - x1) * dx + (y - y1) * dy) / length))
            near_x, near_y = x1 + position * dx, y1 + position * dy
            if math.hypot(x - near_x, y - near_y) <= half:
                return True
        return False

    return inside


def image_data(width: int, height: int,
               rows: Sequence[Sequence[int]], level: int = 9) -> bytes:
    """Forme attendue par PhotoImage, pour une image RVBA deja composee.

    « Raster » compose par couverture, une forme apres l'autre : c'est ce
    qu'il faut pour un disque de sept pixels, pas pour un millier d'etoiles
    dont la lumiere s'ajoute. Celles-la arrivent ici deja calculees.
    """
    return base64.b64encode(_png(width, height, rows, level))


# ------------------------------------------------------------------ images

_cache: Dict[Tuple, bytes] = {}


def disc(diameter: int, colour: RGB, ring: RGB = None,
         ring_width: float = 0.0, samples: int = SAMPLES) -> bytes:
    """Disque plein, avec un cerne optionnel pour le point selectionne.

    `samples` commande la finesse du lissage. Le defaut suffit a une case a
    cocher de quinze pixels ; a sept pixels, un disque n'a qu'une vingtaine
    de pixels de bord, et quatre sous-echantillons y laissent un escalier
    visible — le rond se lit alors comme un octogone. Le calcul etant fait
    une fois par couleur et garde en cache, monter l'echantillonnage sur les
    petits disques ne coute rien a l'affichage.
    """
    key = ("disc", diameter, colour, ring, ring_width, samples)
    if key not in _cache:
        centre = diameter / 2.0
        raster = Raster(diameter)
        raster.paint(_circle(centre, centre - 0.5), colour, samples=samples)
        if ring and ring_width:
            outer, inner = centre - 0.5, centre - 0.5 - ring_width
            outside_inner = _circle(centre, inner)
            circle = _circle(centre, outer)
            raster.paint(lambda x, y: circle(x, y) and not outside_inner(x, y),
                         ring, samples=samples)
        _cache[key] = raster.to_data()
    return _cache[key]


def checkbox(size: int, checked: bool, fill: RGB, border: RGB,
             mark: RGB = (255, 255, 255)) -> bytes:
    """Case a cocher : carre a coins arrondis, coche tracee au trait."""
    key = ("check", size, checked, fill, border, mark)
    if key not in _cache:
        raster = Raster(size)
        corner = max(2.0, size / 6.0)
        box = _rounded_box(0.5, size - 0.5, corner)
        raster.paint(box, fill)
        inner = _rounded_box(1.5, size - 1.5, max(1.0, corner - 1.0))
        raster.paint(lambda x, y: box(x, y) and not inner(x, y), border)
        if checked:
            scale = size / 15.0
            raster.paint(_segments([(4.0 * scale, 8.0 * scale),
                                    (6.4 * scale, 10.6 * scale),
                                    (11.2 * scale, 4.6 * scale)],
                                   2.0 * scale), mark)
        _cache[key] = raster.to_data()
    return _cache[key]


def ring(diameter: int, hole: float, parts: Sequence[Tuple[float, RGB]],
         gap: float = 1.6) -> bytes:
    """Anneau a secteurs, antialiase.

    Le canevas Tk sait dessiner un arc, mais sans lissage : les bords d'un
    camembert y deviennent un escalier, et c'est la premiere chose qu'on
    voit d'une page. On le dessine donc ici, comme les disques du nuage de
    points, en echantillonnant la couverture de chaque pixel.

    Un seul passage, et non un par secteur : chaque echantillon decide
    lui-meme de quelle part il releve. A seize echantillons par pixel et
    trois parts, un passage par part couterait trois fois le prix pour le
    meme resultat.

    `parts` donne les fractions du tour — elles somment a un — et leur
    couleur. `gap` est la coupure entre deux parts, en pixels : elle les
    separe mieux qu'un filet, qui serait lui-meme a lisser.
    """
    key = ("ring", diameter, round(hole, 2), tuple(parts), gap)
    if key in _cache:
        return _cache[key]
    size = int(diameter)
    centre = size / 2.0
    outer, inner = centre - 0.5, float(hole)
    # Bornes angulaires cumulees, en tours (0 a 1), depuis midi et dans le
    # sens des aiguilles — celui dans lequel on lit un camembert.
    bornes, total = [], 0.0
    for fraction, colour in parts:
        bornes.append((total, total + fraction, colour))
        total += fraction
    step = 1.0 / SAMPLES
    weight = 1.0 / (SAMPLES * SAMPLES)
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            couverture: Dict[int, float] = {}
            for sub_y in range(SAMPLES):
                py = y + (sub_y + 0.5) * step - centre
                for sub_x in range(SAMPLES):
                    px = x + (sub_x + 0.5) * step - centre
                    distance = math.hypot(px, py)
                    if not inner <= distance <= outer:
                        continue
                    # Angle depuis midi, croissant dans le sens horaire.
                    tour = (math.atan2(px, -py) / (2 * math.pi)) % 1.0
                    for index, (debut, fin, _colour) in enumerate(bornes):
                        if debut <= tour < fin or (index == len(bornes) - 1
                                                   and tour >= fin):
                            # La coupure se mesure en pixels le long de
                            # l'arc : constante en angle, elle serait large
                            # au bord et nulle au centre.
                            if distance * 2 * math.pi * min(
                                    tour - debut, fin - tour) < gap / 2:
                                break
                            couverture[index] = couverture.get(index,
                                                               0.0) + weight
                            break
            if not couverture:
                row += [0, 0, 0, 0]
                continue
            alpha = sum(couverture.values())
            red = green = blue = 0.0
            for index, part in couverture.items():
                colour = bornes[index][2]
                red += colour[0] * part
                green += colour[1] * part
                blue += colour[2] * part
            row += [round(red / alpha), round(green / alpha),
                    round(blue / alpha), round(alpha * 255)]
        rows.append(row)
    _cache[key] = image_data(size, size, rows)
    return _cache[key]
