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


def _png(width: int, height: int, pixels: Sequence[Sequence[int]]) -> bytes:
    """Encode une image RVBA en PNG, sans filtrage de ligne."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        payload = tag + data
        return (struct.pack(">I", len(data)) + payload
                + struct.pack(">I", zlib.crc32(payload)))

    body = b"".join(b"\x00" + bytes(row) for row in pixels)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(body, 9))
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


# ------------------------------------------------------------------ images

_cache: Dict[Tuple, bytes] = {}


def disc(diameter: int, colour: RGB, ring: RGB = None,
         ring_width: float = 0.0) -> bytes:
    """Disque plein, avec un cerne optionnel pour le point selectionne."""
    key = ("disc", diameter, colour, ring, ring_width)
    if key not in _cache:
        centre = diameter / 2.0
        raster = Raster(diameter)
        raster.paint(_circle(centre, centre - 0.5), colour)
        if ring and ring_width:
            outer, inner = centre - 0.5, centre - 0.5 - ring_width
            outside_inner = _circle(centre, inner)
            circle = _circle(centre, outer)
            raster.paint(lambda x, y: circle(x, y) and not outside_inner(x, y),
                         ring)
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
