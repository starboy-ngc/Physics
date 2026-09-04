"""Ecriture de PDF, sans aucune dependance externe.

Le PDF est un format texte structure : objets numerotes, table de references
croisees, flux de contenu en operateurs graphiques. Tout est produit ici avec
la bibliotheque standard — pas de moteur de rendu, pas de binaire, pas de
navigateur a piloter.

Choix qui rendent l'exercice tenable :

* seules les 14 polices de base du format PDF sont utilisees (Helvetica), donc
  aucune police a embarquer ni a licencier ;
* les largeurs de glyphes Helvetica sont tabulees ici, ce qui permet de
  centrer, aligner a droite et tronquer proprement ;
* le dessin se limite aux primitives dont les graphiques ont besoin :
  rectangles, lignes, cercles, texte — exactement ce que produit deja le SVG.
"""

from __future__ import annotations

import os
import zlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Largeurs Helvetica (unites de 1/1000 em) pour les caracteres imprimables
# latin-1. Table officielle des metriques Adobe (AFM).
_HELVETICA_WIDTHS = {
    32: 278, 33: 278, 34: 355, 35: 556, 36: 556, 37: 889, 38: 667, 39: 191,
    40: 333, 41: 333, 42: 389, 43: 584, 44: 278, 45: 333, 46: 278, 47: 278,
    48: 556, 49: 556, 50: 556, 51: 556, 52: 556, 53: 556, 54: 556, 55: 556,
    56: 556, 57: 556, 58: 278, 59: 278, 60: 584, 61: 584, 62: 584, 63: 556,
    64: 1015, 65: 667, 66: 667, 67: 722, 68: 722, 69: 667, 70: 611, 71: 778,
    72: 722, 73: 278, 74: 500, 75: 667, 76: 556, 77: 833, 78: 722, 79: 778,
    80: 667, 81: 778, 82: 722, 83: 667, 84: 611, 85: 722, 86: 667, 87: 944,
    88: 667, 89: 667, 90: 611, 91: 278, 92: 278, 93: 278, 94: 469, 95: 556,
    96: 333, 97: 556, 98: 556, 99: 500, 100: 556, 101: 556, 102: 278,
    103: 556, 104: 556, 105: 222, 106: 222, 107: 500, 108: 222, 109: 833,
    110: 556, 111: 556, 112: 556, 113: 556, 114: 333, 115: 500, 116: 278,
    117: 556, 118: 500, 119: 722, 120: 500, 121: 500, 122: 500, 123: 334,
    124: 260, 125: 334, 126: 584,
}
_BOLD_WIDTHS = {
    32: 278, 39: 238, 40: 333, 41: 333, 44: 278, 45: 333, 46: 278, 47: 278,
    48: 556, 49: 556, 50: 556, 51: 556, 52: 556, 53: 556, 54: 556, 55: 556,
    56: 556, 57: 556, 58: 333, 59: 333, 65: 722, 66: 722, 67: 722, 68: 722,
    69: 667, 70: 611, 71: 778, 72: 722, 73: 278, 74: 556, 75: 722, 76: 611,
    77: 833, 78: 722, 79: 778, 80: 667, 81: 778, 82: 722, 83: 667, 84: 611,
    85: 722, 86: 667, 87: 944, 88: 667, 89: 667, 90: 611, 97: 556, 98: 611,
    99: 556, 100: 611, 101: 556, 102: 333, 103: 611, 104: 611, 105: 278,
    106: 278, 107: 556, 108: 278, 109: 889, 110: 611, 111: 611, 112: 611,
    113: 611, 114: 389, 115: 556, 116: 333, 117: 611, 118: 556, 119: 778,
    120: 556, 121: 556, 122: 500, 37: 889, 38: 722,
}
_DEFAULT_WIDTH = 556

FONT_REGULAR = "F1"
FONT_BOLD = "F2"


def text_width(text: str, size: float, bold: bool = False) -> float:
    """Largeur d'une chaine, en points, pour la police et la taille donnees."""
    table = _BOLD_WIDTHS if bold else _HELVETICA_WIDTHS
    fallback = _HELVETICA_WIDTHS if bold else None
    total = 0
    for char in text:
        code = ord(char)
        width = table.get(code)
        if width is None and fallback is not None:
            width = fallback.get(code)
        total += width if width is not None else _DEFAULT_WIDTH
    return total * size / 1000.0


def truncate(text: str, size: float, maximum: float, bold: bool = False) -> str:
    """Tronque a la largeur disponible, avec des points de suite."""
    if text_width(text, size, bold) <= maximum:
        return text
    ellipsis = "..."
    budget = maximum - text_width(ellipsis, size, bold)
    if budget <= 0:
        return ""
    kept = ""
    for char in text:
        if text_width(kept + char, size, bold) > budget:
            break
        kept += char
    return kept + ellipsis


def _pdf_string(text: str) -> str:
    """Chaine litterale PDF, encodee WinAnsi."""
    escaped = text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
    return escaped


def encode_text(text: str) -> str:
    """Replie les caracteres hors WinAnsi vers un equivalent imprimable.

    Le moteur ecrit ses libelles en ASCII ; cette repli evite qu'un accent
    venu d'un fichier RH produise un caractere illisible dans le PDF.
    """
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "…": "...", " ": " ",
        " ": " ", "−": "-", "≤": "<=", "≥": ">=",
        "≠": "!=", "∈": "dans", "∉": "hors", "·": "-",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return "".join(char if ord(char) < 256 else "?" for char in text)


class Page:
    """Flux de contenu d'une page. Origine en bas a gauche, unite : le point."""

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self._parts: List[str] = []

    # -- primitives geometriques ------------------------------------------

    def rect(self, x: float, y: float, width: float, height: float,
             fill: Optional[Tuple[float, float, float]] = None,
             stroke: Optional[Tuple[float, float, float]] = None,
             line_width: float = 0.6) -> None:
        if fill is None and stroke is None:
            return
        if fill:
            self._parts.append(f"{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg")
        if stroke:
            self._parts.append(f"{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG")
            self._parts.append(f"{line_width:.2f} w")
        self._parts.append(f"{x:.2f} {y:.2f} {width:.2f} {height:.2f} re")
        if fill and stroke:
            self._parts.append("B")
        elif fill:
            self._parts.append("f")
        else:
            self._parts.append("S")

    def line(self, x1: float, y1: float, x2: float, y2: float,
             color: Tuple[float, float, float] = (0, 0, 0),
             width: float = 0.6,
             dash: Optional[Sequence[float]] = None) -> None:
        self._parts.append(f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} RG")
        self._parts.append(f"{width:.2f} w")
        if dash:
            pattern = " ".join(f"{value:.1f}" for value in dash)
            self._parts.append(f"[{pattern}] 0 d")
        self._parts.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")
        if dash:
            self._parts.append("[] 0 d")

    def circle(self, x: float, y: float, radius: float,
               fill: Tuple[float, float, float],
               alpha_state: Optional[str] = None) -> None:
        """Cercle approxime par quatre courbes de Bezier."""
        k = radius * 0.5523
        if alpha_state:
            self._parts.append(f"/{alpha_state} gs")
        self._parts.append(f"{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg")
        self._parts.append(f"{x + radius:.2f} {y:.2f} m")
        self._parts.append(f"{x + radius:.2f} {y + k:.2f} {x + k:.2f} {y + radius:.2f} "
                           f"{x:.2f} {y + radius:.2f} c")
        self._parts.append(f"{x - k:.2f} {y + radius:.2f} {x - radius:.2f} {y + k:.2f} "
                           f"{x - radius:.2f} {y:.2f} c")
        self._parts.append(f"{x - radius:.2f} {y - k:.2f} {x - k:.2f} {y - radius:.2f} "
                           f"{x:.2f} {y - radius:.2f} c")
        self._parts.append(f"{x + k:.2f} {y - radius:.2f} {x + radius:.2f} {y - k:.2f} "
                           f"{x + radius:.2f} {y:.2f} c")
        self._parts.append("f")

    # -- texte -------------------------------------------------------------

    def text(self, x: float, y: float, content: str, size: float = 11,
             bold: bool = False, color: Tuple[float, float, float] = (0, 0, 0),
             align: str = "left", max_width: Optional[float] = None) -> None:
        content = encode_text(str(content))
        if max_width is not None:
            content = truncate(content, size, max_width, bold)
        if not content:
            return
        width = text_width(content, size, bold)
        if align == "right":
            x -= width
        elif align == "center":
            x -= width / 2.0
        font = FONT_BOLD if bold else FONT_REGULAR
        self._parts.append("BT")
        self._parts.append(f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg")
        self._parts.append(f"/{font} {size:.2f} Tf")
        self._parts.append(f"{x:.2f} {y:.2f} Td")
        self._parts.append(f"({_pdf_string(content)}) Tj")
        self._parts.append("ET")

    def content(self) -> bytes:
        return "\n".join(self._parts).encode("latin-1", "replace")


class Document:
    """Assemble les pages en un fichier PDF."""

    def __init__(self, width: float = 841.89, height: float = 595.28):
        # Defaut : A4 paysage.
        self.width = width
        self.height = height
        self.pages: List[Page] = []

    def add_page(self) -> Page:
        page = Page(self.width, self.height)
        self.pages.append(page)
        return page

    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(self._build())
        return path

    def _build(self) -> bytes:
        objects: List[bytes] = []

        def add(payload: bytes) -> int:
            objects.append(payload)
            return len(objects)

        font_regular = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                           b"/Encoding /WinAnsiEncoding >>")
        font_bold = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
                        b"/Encoding /WinAnsiEncoding >>")
        alpha = add(b"<< /Type /ExtGState /ca 0.65 >>")
        resources = add(
            f"<< /Font << /{FONT_REGULAR} {font_regular} 0 R "
            f"/{FONT_BOLD} {font_bold} 0 R >> "
            f"/ExtGState << /GA {alpha} 0 R >> >>".encode("latin-1")
        )

        pages_id = len(objects) + 1 + 2 * len(self.pages) + 1
        page_ids: List[int] = []
        for page in self.pages:
            stream = zlib.compress(page.content())
            content_id = add(
                b"<< /Length " + str(len(stream)).encode() + b" /Filter /FlateDecode >>"
                b"\nstream\n" + stream + b"\nendstream"
            )
            page_ids.append(add(
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {self.width:.2f} {self.height:.2f}] "
                f"/Resources {resources} 0 R /Contents {content_id} 0 R >>"
                .encode("latin-1")
            ))
        kids = " ".join(f"{identifier} 0 R" for identifier in page_ids)
        pages_object = add(
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")
        )
        catalog = add(f"<< /Type /Catalog /Pages {pages_object} 0 R >>".encode("latin-1"))

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, payload in enumerate(objects, start=1):
            offsets.append(len(out))
            out += f"{index} 0 obj\n".encode("latin-1") + payload + b"\nendobj\n"
        xref_position = len(out)
        out += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
        out += b"0000000000 65535 f \n"
        for offset in offsets[1:]:
            out += f"{offset:010d} 00000 n \n".encode("latin-1")
        out += (f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R >>\n"
                f"startxref\n{xref_position}\n%%EOF\n").encode("latin-1")
        return bytes(out)
