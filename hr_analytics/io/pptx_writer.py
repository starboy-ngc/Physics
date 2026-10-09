"""Ecriture de presentations PowerPoint (.pptx), sans aucune dependance.

Un .pptx est une archive zip de fichiers XML (Office Open XML), comme le
classeur Excel que l'outil ecrit deja. Rien n'est installe, rien n'est
telecharge : la bibliotheque standard suffit, exactement comme pour le
PDF et le classeur.

La presentation n'a qu'une disposition, vierge. Chaque planche est
dessinee avec les memes gestes que le PDF, et par le meme code : un
rectangle, un trait, un cercle, un secteur d'anneau, un texte. C'est ce
qui garantit que le PowerPoint et le PDF montrent la meme chose. Mais ici
tout reste modifiable : les textes sont des zones de texte, les
graphiques des formes. On corrige un libelle ou on supprime une planche
avant un comite, sans revenir a l'outil.

Les graphiques ne sont donc pas des graphiques PowerPoint relies a des
donnees : ce sont des dessins, fideles au pixel pres a ce que l'outil a
calcule et publie. La police est Arial, que tout poste possede ; ses
largeurs sont celles d'Helvetica, avec lesquelles le PDF aligne et
tronque, de sorte que la mise en page est la meme.

Unite d'entree : le point, origine en bas a gauche, comme le PDF. A
l'ecriture, les points deviennent des EMU (12 700 par point) et l'origine
passe en haut a gauche.
"""
from __future__ import annotations

import math
import os
import zipfile
from typing import List, Optional, Sequence, Tuple

from . import restrict_to_owner
from .pdf_writer import text_width, truncate

#: English Metric Units par point : l'unite des coordonnees Office.
EMU_PER_POINT = 12700

#: Police des planches. Ses largeurs sont celles d'Helvetica, que le PDF
#: tabule : les deux documents alignent et tronquent pareil.
FONT = "Arial"

#: Part de la taille de police au-dessus de la ligne de base (Arial :
#: 1854/2048) et hauteur d'une ligne, pour placer une zone de texte dont
#: la ligne de base tombe la ou le PDF pose la sienne.
_ASCENT = 0.905
_LINE = 1.2

#: Opacite du seul etat de transparence que le PDF connait (« GA »).
_ALPHA = 0.65

_NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
       'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
       'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"

#: Un groupe vide, racine obligatoire de toute arborescence de formes.
_EMPTY_TREE = (
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
    '</p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/>'
    '<a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>'
    '</a:xfrm></p:grpSpPr>')


def _emu(points: float) -> int:
    return int(round(points * EMU_PER_POINT))


def _hex(color: Tuple[float, float, float]) -> str:
    """Un triplet 0..1 en « RRGGBB »."""
    return "".join(f"{max(0, min(255, int(round(part * 255)))):02X}"
                   for part in color)


def _escape(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _angle(radians: float) -> int:
    """Un angle en 60 000es de degre, dans [0, 360°[."""
    degrees = math.degrees(radians) % 360.0
    return int(round(degrees * 60000)) % 21600000


def _fill(color: Optional[Tuple[float, float, float]],
          alpha: Optional[float] = None) -> str:
    if color is None:
        return "<a:noFill/>"
    inner = (f'<a:alpha val="{int(round(alpha * 100000))}"/>'
             if alpha is not None else "")
    return f'<a:solidFill><a:srgbClr val="{_hex(color)}">{inner}</a:srgbClr></a:solidFill>'


def _outline(color: Optional[Tuple[float, float, float]], width: float,
             dash: Optional[Sequence[float]] = None) -> str:
    if color is None:
        return "<a:ln><a:noFill/></a:ln>"
    pattern = '<a:prstDash val="dash"/>' if dash else ""
    return f'<a:ln w="{_emu(width)}">{_fill(color)}{pattern}</a:ln>'


class Page:
    """Une planche. Origine en bas a gauche, unite : le point."""

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self._shapes: List[str] = []
        self._next_id = 2

    def _id(self) -> int:
        self._next_id += 1
        return self._next_id - 1

    def _top(self, y: float, height: float = 0.0) -> int:
        """L'ordonnee Office (vers le bas) du bord haut d'une boite dont
        le bord bas est a `y` points du bas de la planche."""
        return _emu(self.height - y - height)

    # -- primitives geometriques ------------------------------------------

    def rect(self, x: float, y: float, width: float, height: float,
             fill: Optional[Tuple[float, float, float]] = None,
             stroke: Optional[Tuple[float, float, float]] = None,
             line_width: float = 0.6) -> None:
        if fill is None and stroke is None:
            return
        if width < 0:
            x, width = x + width, -width
        if height < 0:
            y, height = y + height, -height
        identifier = self._id()
        self._shapes.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{identifier}" '
            f'name="Rectangle {identifier}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{_emu(x)}" y="{self._top(y, height)}"/>'
            f'<a:ext cx="{_emu(width)}" cy="{_emu(height)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'{_fill(fill)}{_outline(stroke, line_width)}</p:spPr></p:sp>')

    def line(self, x1: float, y1: float, x2: float, y2: float,
             color: Tuple[float, float, float] = (0, 0, 0),
             width: float = 0.6,
             dash: Optional[Sequence[float]] = None) -> None:
        top1, top2 = self._top(y1), self._top(y2)
        left, top = _emu(min(x1, x2)), min(top1, top2)
        # Un connecteur va du coin haut-gauche de sa boite au coin
        # bas-droit ; s'il monte vers la droite, on le retourne.
        flip = ' flipV="1"' if (x2 - x1) * (top2 - top1) < 0 else ""
        identifier = self._id()
        self._shapes.append(
            f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{identifier}" '
            f'name="Trait {identifier}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm{flip}><a:off x="{left}" y="{top}"/>'
            f'<a:ext cx="{abs(_emu(x2) - _emu(x1))}" cy="{abs(top2 - top1)}"/>'
            f'</a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'{_outline(color, width, dash)}</p:spPr></p:cxnSp>')

    def circle(self, x: float, y: float, radius: float,
               fill: Tuple[float, float, float],
               alpha_state: Optional[str] = None) -> None:
        identifier = self._id()
        self._shapes.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{identifier}" '
            f'name="Point {identifier}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{_emu(x - radius)}" '
            f'y="{self._top(y - radius, 2 * radius)}"/>'
            f'<a:ext cx="{_emu(2 * radius)}" cy="{_emu(2 * radius)}"/></a:xfrm>'
            f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
            f'{_fill(fill, _ALPHA if alpha_state else None)}'
            f'<a:ln><a:noFill/></a:ln></p:spPr></p:sp>')

    def wedge(self, x: float, y: float, outer: float, inner: float,
              start: float, end: float,
              fill: Tuple[float, float, float]) -> None:
        """Secteur d'anneau, du rayon `inner` au rayon `outer`.

        Office sait tracer un arc d'ellipse : le secteur est un chemin
        ferme, arc exterieur, rayon, arc interieur a rebours. Les angles
        du PDF tournent dans le sens direct, ordonnee vers le haut ; ceux
        d'Office tournent dans le sens horaire, ordonnee vers le bas. Le
        meme point du cercle a donc l'angle oppose.
        """
        if end <= start or outer <= inner:
            return
        size = _emu(2 * outer)
        centre = _emu(outer)

        def point(rayon: float, angle: float) -> str:
            return (f'<a:pt x="{int(round(centre + _emu(rayon) * math.cos(angle)))}" '
                    f'y="{int(round(centre + _emu(rayon) * math.sin(angle)))}"/>')

        depart, balayage = -end, end - start
        identifier = self._id()
        self._shapes.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{identifier}" '
            f'name="Secteur {identifier}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{_emu(x - outer)}" '
            f'y="{self._top(y - outer, 2 * outer)}"/>'
            f'<a:ext cx="{size}" cy="{size}"/></a:xfrm>'
            f'<a:custGeom><a:avLst/><a:pathLst><a:path w="{size}" h="{size}">'
            f'<a:moveTo>{point(outer, depart)}</a:moveTo>'
            f'<a:arcTo wR="{_emu(outer)}" hR="{_emu(outer)}" '
            f'stAng="{_angle(depart)}" swAng="{_angle(balayage)}"/>'
            f'<a:lnTo>{point(inner, -start)}</a:lnTo>'
            f'<a:arcTo wR="{_emu(inner)}" hR="{_emu(inner)}" '
            f'stAng="{_angle(-start)}" swAng="-{_angle(balayage)}"/>'
            f'<a:close/></a:path></a:pathLst></a:custGeom>'
            f'{_fill(fill)}<a:ln><a:noFill/></a:ln></p:spPr></p:sp>')

    # -- texte -------------------------------------------------------------

    def text(self, x: float, y: float, content: str, size: float = 11,
             bold: bool = False, color: Tuple[float, float, float] = (0, 0, 0),
             align: str = "left", max_width: Optional[float] = None) -> None:
        content = str(content)
        if max_width is not None:
            content = truncate(content, size, max_width, bold)
        if not content:
            return
        width = text_width(content, size, bold)
        if align == "right":
            x -= width
        elif align == "center":
            x -= width / 2.0
        # La boite est posee pour que la ligne de base tombe en `y` ; elle
        # ne coupe pas le texte (wrap="none") si Arial deborde d'un rien.
        top = _emu(self.height - y - _ASCENT * size)
        identifier = self._id()
        self._shapes.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{identifier}" '
            f'name="Texte {identifier}"/><p:cNvSpPr txBox="1"/><p:nvPr/>'
            f'</p:nvSpPr><p:spPr><a:xfrm><a:off x="{_emu(x)}" y="{top}"/>'
            f'<a:ext cx="{_emu(width + 2)}" cy="{_emu(_LINE * size)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>'
            f'</p:spPr><p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" '
            f'rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr>'
            f'<a:lstStyle/><a:p><a:pPr algn="l"/><a:r><a:rPr lang="fr-FR" '
            f'sz="{int(round(size * 100))}" b="{1 if bold else 0}" dirty="0">'
            f'{_fill(color)}<a:latin typeface="{FONT}"/><a:cs typeface="{FONT}"/>'
            f'</a:rPr><a:t>{_escape(content)}</a:t></a:r></a:p></p:txBody></p:sp>')

    def xml(self) -> str:
        return (f'{_XML}<p:sld {_NS}><p:cSld><p:spTree>{_EMPTY_TREE}'
                f'{"".join(self._shapes)}</p:spTree></p:cSld>'
                '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


def _content_types(count: int) -> str:
    slides = "".join(
        f'<Override PartName="/ppt/slides/slide{index}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.'
        'presentationml.slide+xml"/>' for index in range(1, count + 1))
    return (
        f'{_XML}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        f'{slides}</Types>')


def _relationships(entries: Sequence[Tuple[str, str, str]]) -> str:
    body = "".join(f'<Relationship Id="{identifier}" Type="{kind}" Target="{target}"/>'
                   for identifier, kind, target in entries)
    return f'{_XML}<Relationships xmlns="{_PKG}">{body}</Relationships>'


_ROOT_RELS = _relationships((
    ("rId1", f"{_REL}/officeDocument", "ppt/presentation.xml"),
    ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties",
     "docProps/core.xml"),
    ("rId3", f"{_REL}/extended-properties", "docProps/app.xml"),
))

_LAYOUT_RELS = _relationships((
    ("rId1", f"{_REL}/slideMaster", "../slideMasters/slideMaster1.xml"),
))

_MASTER_RELS = _relationships((
    ("rId1", f"{_REL}/slideLayout", "../slideLayouts/slideLayout1.xml"),
    ("rId2", f"{_REL}/theme", "../theme/theme1.xml"),
))

_SLIDE_RELS = _relationships((
    ("rId1", f"{_REL}/slideLayout", "../slideLayouts/slideLayout1.xml"),
))

_LAYOUT = (
    f'{_XML}<p:sldLayout {_NS} type="blank" preserve="1">'
    f'<p:cSld name="Vierge"><p:spTree>{_EMPTY_TREE}</p:spTree></p:cSld>'
    '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')

_MASTER = (
    f'{_XML}<p:sldMaster {_NS}><p:cSld><p:bg><p:bgPr>'
    '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/>'
    f'</p:bgPr></p:bg><p:spTree>{_EMPTY_TREE}</p:spTree></p:cSld>'
    '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" '
    'accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" '
    'accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
    '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/>'
    '</p:sldLayoutIdLst><p:txStyles>'
    f'<p:titleStyle><a:lvl1pPr><a:defRPr sz="2100"><a:latin typeface="{FONT}"/>'
    '</a:defRPr></a:lvl1pPr></p:titleStyle>'
    f'<p:bodyStyle><a:lvl1pPr><a:defRPr sz="1100"><a:latin typeface="{FONT}"/>'
    '</a:defRPr></a:lvl1pPr></p:bodyStyle>'
    f'<p:otherStyle><a:lvl1pPr><a:defRPr sz="1100"><a:latin typeface="{FONT}"/>'
    '</a:defRPr></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>')


def _theme() -> str:
    colours = (("dk1", "000000"), ("lt1", "FFFFFF"), ("dk2", "1F2A37"),
               ("lt2", "EEEEEE"), ("accent1", "0F6E8C"), ("accent2", "2E86AB"),
               ("accent3", "F18F01"), ("accent4", "C73E1D"),
               ("accent5", "3B1F2B"), ("accent6", "6C757D"),
               ("hlink", "0563C1"), ("folHlink", "954F72"))
    scheme = "".join(f'<a:{name}><a:srgbClr val="{value}"/></a:{name}>'
                     for name, value in colours)
    fonts = (f'<a:latin typeface="{FONT}"/><a:ea typeface=""/>'
             '<a:cs typeface=""/>')
    fill = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    line = f'<a:ln w="6350">{fill}</a:ln>'
    effect = '<a:effectStyle><a:effectLst/></a:effectStyle>'
    return (
        f'{_XML}<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'name="HR Analytics"><a:themeElements>'
        f'<a:clrScheme name="HR Analytics">{scheme}</a:clrScheme>'
        f'<a:fontScheme name="HR Analytics"><a:majorFont>{fonts}</a:majorFont>'
        f'<a:minorFont>{fonts}</a:minorFont></a:fontScheme>'
        f'<a:fmtScheme name="HR Analytics"><a:fillStyleLst>{fill * 3}</a:fillStyleLst>'
        f'<a:lnStyleLst>{line * 3}</a:lnStyleLst>'
        f'<a:effectStyleLst>{effect * 3}</a:effectStyleLst>'
        f'<a:bgFillStyleLst>{fill * 3}</a:bgFillStyleLst></a:fmtScheme>'
        '</a:themeElements></a:theme>')


class Document:
    """Assemble les planches en un fichier .pptx."""

    def __init__(self, width: float = 841.89, height: float = 595.28,
                 title: str = "HR Analytics"):
        # Defaut : la planche a le format du PDF, A4 paysage.
        self.width = width
        self.height = height
        self.title = title
        self.pages: List[Page] = []

    def add_page(self) -> Page:
        page = Page(self.width, self.height)
        self.pages.append(page)
        return page

    def _presentation(self) -> str:
        identifiers = "".join(
            f'<p:sldId id="{255 + index}" r:id="rId{2 + index}"/>'
            for index in range(1, len(self.pages) + 1))
        return (
            f'{_XML}<p:presentation {_NS} saveSubsetFonts="1">'
            '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/>'
            f'</p:sldMasterIdLst><p:sldIdLst>{identifiers}</p:sldIdLst>'
            f'<p:sldSz cx="{_emu(self.width)}" cy="{_emu(self.height)}"/>'
            '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>')

    def _presentation_rels(self) -> str:
        # Le masque en rId1, le theme en rId2, puis une planche par
        # identifiant : la liste des planches de presentation.xml les
        # cite par ces memes identifiants, qui ne doivent jamais se
        # croiser, sinon une planche disparait au profit du theme.
        entries = [("rId1", f"{_REL}/slideMaster",
                    "slideMasters/slideMaster1.xml"),
                   ("rId2", f"{_REL}/theme", "theme/theme1.xml")]
        entries += [(f"rId{2 + index}", f"{_REL}/slide", f"slides/slide{index}.xml")
                    for index in range(1, len(self.pages) + 1)]
        return _relationships(entries)

    def _core(self) -> str:
        # Un titre et le nom de l'outil : ni auteur, ni date, ni poste. Un
        # document qui circule ne dit pas qui l'a produit (§6).
        return (
            f'{_XML}<cp:coreProperties '
            'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{_escape(self.title)}</dc:title>'
            '<dc:creator>HR Analytics</dc:creator></cp:coreProperties>')

    def _app(self) -> str:
        return (
            f'{_XML}<Properties '
            'xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            f'<Application>HR Analytics</Application><Slides>{len(self.pages)}</Slides>'
            '</Properties>')

    def save(self, path: str) -> str:
        if not self.pages:
            raise ValueError("au moins une planche est requise")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", _content_types(len(self.pages)))
            archive.writestr("_rels/.rels", _ROOT_RELS)
            archive.writestr("docProps/core.xml", self._core())
            archive.writestr("docProps/app.xml", self._app())
            archive.writestr("ppt/presentation.xml", self._presentation())
            archive.writestr("ppt/_rels/presentation.xml.rels",
                             self._presentation_rels())
            archive.writestr("ppt/slideMasters/slideMaster1.xml", _MASTER)
            archive.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels",
                             _MASTER_RELS)
            archive.writestr("ppt/slideLayouts/slideLayout1.xml", _LAYOUT)
            archive.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels",
                             _LAYOUT_RELS)
            archive.writestr("ppt/theme/theme1.xml", _theme())
            for index, page in enumerate(self.pages, start=1):
                archive.writestr(f"ppt/slides/slide{index}.xml", page.xml())
                archive.writestr(f"ppt/slides/_rels/slide{index}.xml.rels",
                                 _SLIDE_RELS)
        return restrict_to_owner(path)
