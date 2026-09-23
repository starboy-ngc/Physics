"""Ecriture de classeurs XLSX minimalistes (zipfile + XML standard).

Volontairement limite a ce dont la restitution a besoin : plusieurs onglets,
en-tetes en gras, nombres et textes. Cela evite d'embarquer une bibliotheque
tierce pour l'export.
"""

from __future__ import annotations

import datetime as _dt
import math
import re
import zipfile
from typing import (Any, Iterable, List, NamedTuple, Optional,
                    Sequence, Tuple)

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
{sheets}
</Types>"""

_ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

_STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="3">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="14" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""

_EXCEL_EPOCH = _dt.date(1899, 12, 30)
_MAX_SHEET_NAME = 31


#: Caracteres interdits par XML 1.0. Une cellule RH venue d'un export
#: mainframe peut en porter (tabulation verticale, saut de page) : ecrits
#: tels quels, ils produisaient un classeur qu'Excel declare illisible dans
#: son integralite. Ils sont remplaces par une espace, ce qui abime une
#: cellule au lieu de perdre le fichier.
_FORBIDDEN_RE = re.compile(
    "[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f\ufffe\uffff]")


def _escape(text: str) -> str:
    text = _FORBIDDEN_RE.sub(" ", text)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _column_letter(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def _sanitize_sheet_name(name: str, used: set) -> str:
    cleaned = "".join(char for char in name if char not in "[]:*?/\\") or "Feuille"
    cleaned = cleaned[:_MAX_SHEET_NAME]
    candidate, suffix = cleaned, 1
    while candidate.lower() in used:
        suffix += 1
        candidate = f"{cleaned[:_MAX_SHEET_NAME - 2]}_{suffix}"
    used.add(candidate.lower())
    return candidate


class Formula(NamedTuple):
    """Cellule calculee par le tableur, et non par nous.

    Un classeur d'agregats demande de croire l'outil sur parole. Une
    cellule qui porte sa formule se verifie : on clique dessus, on lit
    « =B10-B8 », et l'on sait d'ou vient le chiffre. C'est la difference
    entre un resultat et un resultat verifiable.

    La valeur calculee est ecrite en meme temps que la formule : Excel la
    recalcule a l'ouverture, mais un lecteur qui ne recalcule pas — un
    convertisseur, un import automatise — afficherait des zeros sans elle.
    """

    expression: str
    value: Optional[float] = None
    #: Formule matricielle. « MEDIAN(IF(...)) » n'a de sens que validee par
    #: Ctrl+Maj+Entree : ecrite en formule ordinaire, elle rend la mediane
    #: de la premiere cellule au lieu de celle de la selection. Le format
    #: le note dans le fichier, et le tableur la valide seul a l'ouverture.
    array: bool = False


def _formula_xml(reference: str, formula: "Formula", style: int) -> str:
    cached = ""
    if formula.value is not None and math.isfinite(formula.value):
        cached = f"<v>{formula.value!r}</v>"
    attributs = f' t="array" ref="{reference}"' if formula.array else ""
    return (f'<c r="{reference}" s="{style}">'
            f"<f{attributs}>{_escape(formula.expression)}</f>{cached}</c>")


def _cell_xml(reference: str, value: Any, style: int) -> str:
    if isinstance(value, Formula):
        return _formula_xml(reference, value, style)
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return f'<c r="{reference}" s="{style}" t="b"><v>{int(value)}</v></c>'
    if isinstance(value, (int, float)):
        # inf et nan n'ont pas de representation numerique valide en OOXML :
        # les ecrire tels quels produisait un classeur qu'Excel refuse
        # d'ouvrir. Ils sont ecrits en texte, visibles et sans corruption.
        if not math.isfinite(value):
            return _inline_string(reference, style, str(value))
        text = repr(value)
        if "e" in text or "E" in text:
            # OOXML n'accepte pas la notation scientifique produite par repr()
            # sur les grands nombres ("1e+20").
            text = f"{value:f}"
        return f'<c r="{reference}" s="{style}"><v>{text}</v></c>'
    if isinstance(value, _dt.datetime):
        serial = (value.date() - _EXCEL_EPOCH).days
        return f'<c r="{reference}" s="2"><v>{serial}</v></c>'
    if isinstance(value, _dt.date):
        serial = (value - _EXCEL_EPOCH).days
        return f'<c r="{reference}" s="2"><v>{serial}</v></c>'
    return _inline_string(reference, style, str(value))


def _inline_string(reference: str, style: int, value: str) -> str:
    text = _escape(value)
    return (f'<c r="{reference}" s="{style}" t="inlineStr">'
            f'<is><t xml:space="preserve">{text}</t></is></c>')


def _sheet_xml(rows: Iterable[Sequence[Any]], header: bool) -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>',
    ]
    for row_index, row in enumerate(rows, start=1):
        style = 1 if (header and row_index == 1) else 0
        cells = "".join(
            _cell_xml(f"{_column_letter(col)}{row_index}", value, style)
            for col, value in enumerate(row)
        )
        parts.append(f'<row r="{row_index}">{cells}</row>')
    parts.append("</sheetData></worksheet>")
    return "".join(parts)


def write_workbook(
    path: str,
    sheets: Sequence[Tuple[str, Sequence[Sequence[Any]]]],
    header: bool = True,
) -> str:
    """Ecrit un classeur `path` compose de `(nom_onglet, lignes)`."""
    if not sheets:
        raise ValueError("au moins un onglet est requis")

    used: set = set()
    names: List[str] = [_sanitize_sheet_name(name, used) for name, _ in sheets]

    overrides = "\n".join(
        f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(len(sheets))
    )
    workbook_sheets = "".join(
        f'<sheet name="{_escape(name)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>'
        for i, name in enumerate(names)
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{workbook_sheets}</sheets></workbook>"
    )
    relationships = "".join(
        f'<Relationship Id="rId{i + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{i + 1}.xml"/>'
        for i in range(len(sheets))
    )
    relationships += (
        f'<Relationship Id="rId{len(sheets) + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{relationships}</Relationships>"
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES.format(sheets=overrides))
        archive.writestr("_rels/.rels", _ROOT_RELS)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/styles.xml", _STYLES)
        for index, (_, rows) in enumerate(sheets, start=1):
            archive.writestr(
                f"xl/worksheets/sheet{index}.xml", _sheet_xml(rows, header)
            )
    return path
