"""Ecriture de classeurs XLSX minimalistes (zipfile + XML standard).

Volontairement limite a ce dont la restitution a besoin : plusieurs onglets,
en-tetes en gras, nombres et textes. Cela evite d'embarquer une bibliotheque
tierce pour l'export.
"""

from __future__ import annotations

import datetime as _dt
import zipfile
from typing import Any, Iterable, List, Sequence, Tuple

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


def _escape(text: str) -> str:
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


def _cell_xml(reference: str, value: Any, style: int) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return f'<c r="{reference}" s="{style}" t="b"><v>{int(value)}</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{reference}" s="{style}"><v>{value!r}</v></c>'
    if isinstance(value, _dt.datetime):
        serial = (value.date() - _EXCEL_EPOCH).days
        return f'<c r="{reference}" s="2"><v>{serial}</v></c>'
    if isinstance(value, _dt.date):
        serial = (value - _EXCEL_EPOCH).days
        return f'<c r="{reference}" s="2"><v>{serial}</v></c>'
    text = _escape(str(value))
    return f'<c r="{reference}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'


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
