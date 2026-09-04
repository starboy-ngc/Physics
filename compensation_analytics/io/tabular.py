"""Lecture de populations depuis CSV / XLSX / XLSM.

Le resultat est toujours la meme structure neutre :

    Table(headers=[...], rows=[[cell, ...], ...], source_name="...")

ce qui isole completement le reste du moteur du format d'entree.
"""

from __future__ import annotations

import csv
import datetime as _dt
import io
import os
import re
import zipfile
from dataclasses import dataclass, field
from typing import Any, List, Sequence
from xml.etree import ElementTree

from ..core.errors import ImportError_

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_CELL_RE = re.compile(r"^([A-Z]+)(\d+)$")

# Formats numeriques Excel consideres comme des dates (codes integres).
_BUILTIN_DATE_FORMATS = set(range(14, 23)) | set(range(45, 48)) | {27, 30, 36, 50, 57}
_EXCEL_EPOCH = _dt.date(1899, 12, 30)

MAX_CSV_SNIFF_BYTES = 8192


@dataclass
class Table:
    """Tableau brut issu d'un fichier, avant tout mapping."""

    headers: List[str]
    rows: List[List[Any]] = field(default_factory=list)
    source_name: str = ""

    @property
    def row_count(self) -> int:
        return len(self.rows)


def read_table(path: str, sheet: str | None = None) -> Table:
    """Point d'entree unique d'import."""
    if not os.path.isfile(path):
        raise ImportError_(
            "Le fichier de population est introuvable. "
            "Verifiez le chemin indique.",
            technical=f"missing file: {path}",
        )
    extension = os.path.splitext(path)[1].lower()
    if extension in (".csv", ".txt"):
        return _read_csv(path)
    if extension in (".xlsx", ".xlsm"):
        return _read_xlsx(path, sheet)
    raise ImportError_(
        "Format de fichier non pris en charge. "
        "Formats acceptes : Excel (.xlsx, .xlsm) et CSV (.csv).",
        technical=f"unsupported extension: {extension}",
    )


# --------------------------------------------------------------------------- CSV


def _read_csv(path: str) -> Table:
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(MAX_CSV_SNIFF_BYTES)
            handle.seek(0)
            delimiter = _sniff_delimiter(sample)
            reader = csv.reader(handle, delimiter=delimiter)
            rows = [row for row in reader]
    except OSError as exc:
        raise ImportError_(
            "Le fichier CSV n'a pas pu etre ouvert.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    except UnicodeDecodeError as exc:
        raise ImportError_(
            "Le fichier CSV n'est pas encode en UTF-8. "
            "Enregistrez-le au format \"CSV UTF-8\" depuis Excel.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    if not rows:
        raise ImportError_(
            "Le fichier importe est vide.",
            technical="csv file has no rows",
        )
    headers = [str(cell).strip() for cell in rows[0]]
    body = [_pad(row, len(headers)) for row in rows[1:]]
    return Table(headers=headers, rows=body, source_name=os.path.basename(path))


def _sniff_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
    except csv.Error:
        # Heuristique de repli : le separateur le plus frequent sur la 1ere ligne.
        first = sample.splitlines()[0] if sample else ""
        counts = {sep: first.count(sep) for sep in ";,\t|"}
        best = max(counts, key=lambda key: counts[key])
        return best if counts[best] else ","


def _pad(row: Sequence[Any], width: int) -> List[Any]:
    values = list(row[:width])
    values.extend([""] * (width - len(values)))
    return values


# -------------------------------------------------------------------------- XLSX


def _read_xlsx(path: str, sheet: str | None) -> Table:
    try:
        with zipfile.ZipFile(path) as archive:
            shared = _read_shared_strings(archive)
            date_styles = _read_date_styles(archive)
            sheet_path = _resolve_sheet_path(archive, sheet)
            rows = _read_sheet(archive, sheet_path, shared, date_styles)
    except zipfile.BadZipFile as exc:
        raise ImportError_(
            "Le fichier Excel est illisible ou endommage. "
            "Ouvrez-le dans Excel puis enregistrez-le a nouveau au format .xlsx.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    except (OSError, ElementTree.ParseError, KeyError) as exc:
        raise ImportError_(
            "Le contenu du fichier Excel n'a pas pu etre lu.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc

    rows = _drop_trailing_empty(rows)
    if not rows:
        raise ImportError_(
            "L'onglet importe ne contient aucune donnee.",
            technical="xlsx sheet has no rows",
        )
    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    width = len(headers)
    body = [_pad(row, width) for row in rows[1:]]
    return Table(headers=headers, rows=body, source_name=os.path.basename(path))


def _read_shared_strings(archive: zipfile.ZipFile) -> List[str]:
    name = "xl/sharedStrings.xml"
    if name not in archive.namelist():
        return []
    root = ElementTree.fromstring(archive.read(name))
    values: List[str] = []
    for item in root.findall(f"{_NS}si"):
        values.append("".join(node.text or "" for node in item.iter(f"{_NS}t")))
    return values


def _read_date_styles(archive: zipfile.ZipFile) -> set:
    """Indices de style dont le format numerique correspond a une date."""
    name = "xl/styles.xml"
    if name not in archive.namelist():
        return set()
    root = ElementTree.fromstring(archive.read(name))
    custom_date_ids = set()
    for fmt in root.iter(f"{_NS}numFmt"):
        code = (fmt.get("formatCode") or "").lower()
        stripped = re.sub(r"\[[^\]]*\]|\"[^\"]*\"", "", code)
        if any(token in stripped for token in ("yy", "dd", "mm", "hh")):
            custom_date_ids.add(int(fmt.get("numFmtId", "-1")))
    date_styles = set()
    cell_xfs = root.find(f"{_NS}cellXfs")
    if cell_xfs is None:
        return date_styles
    for index, xf in enumerate(cell_xfs.findall(f"{_NS}xf")):
        num_fmt_id = int(xf.get("numFmtId", "0"))
        if num_fmt_id in _BUILTIN_DATE_FORMATS or num_fmt_id in custom_date_ids:
            date_styles.add(index)
    return date_styles


def _resolve_sheet_path(archive: zipfile.ZipFile, sheet: str | None) -> str:
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    rels_xml = archive.read("xl/_rels/workbook.xml.rels")
    rels_root = ElementTree.fromstring(rels_xml)
    targets = {
        node.get("Id"): node.get("Target", "")
        for node in rels_root
    }
    sheets = workbook.find(f"{_NS}sheets")
    entries = list(sheets or [])
    if not entries:
        raise ImportError_(
            "Le classeur Excel ne contient aucun onglet.",
            technical="workbook has no sheets",
        )
    chosen = None
    for node in entries:
        if sheet is None or node.get("name") == sheet:
            chosen = node
            break
    if chosen is None:
        names = ", ".join(node.get("name", "?") for node in entries)
        raise ImportError_(
            f"L'onglet \"{sheet}\" est introuvable dans le classeur. "
            f"Onglets disponibles : {names}.",
            technical=f"sheet not found: {sheet}",
        )
    target = targets.get(chosen.get(f"{_REL_NS}id"), "worksheets/sheet1.xml")
    target = target.lstrip("/")
    return target if target.startswith("xl/") else f"xl/{target}"


def _read_sheet(
    archive: zipfile.ZipFile,
    sheet_path: str,
    shared: List[str],
    date_styles: set,
) -> List[List[Any]]:
    rows: List[List[Any]] = []
    with archive.open(sheet_path) as stream:
        for _, element in ElementTree.iterparse(stream, events=("end",)):
            if element.tag != f"{_NS}row":
                continue
            values: List[Any] = []
            for cell in element.findall(f"{_NS}c"):
                index = _column_index(cell.get("r"))
                if index is None:
                    index = len(values)
                while len(values) < index:
                    values.append("")
                values.append(_cell_value(cell, shared, date_styles))
            rows.append(values)
            element.clear()
    width = max((len(row) for row in rows), default=0)
    return [_pad(row, width) for row in rows]


def _column_index(reference: str | None) -> int | None:
    if not reference:
        return None
    match = _CELL_RE.match(reference)
    if not match:
        return None
    letters = match.group(1)
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def _cell_value(cell: ElementTree.Element, shared: List[str], date_styles: set) -> Any:
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        node = cell.find(f"{_NS}is")
        return "".join(part.text or "" for part in node.iter(f"{_NS}t")) if node is not None else ""
    value_node = cell.find(f"{_NS}v")
    if value_node is None or value_node.text is None:
        return ""
    raw = value_node.text
    if cell_type == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return ""
    if cell_type in ("str", "e"):
        return raw
    if cell_type == "b":
        return raw == "1"
    try:
        number = float(raw)
    except ValueError:
        return raw
    style = cell.get("s")
    if style is not None and int(style) in date_styles:
        return _excel_serial_to_date(number)
    if number.is_integer():
        return int(number)
    return number


def _excel_serial_to_date(serial: float) -> Any:
    try:
        return _EXCEL_EPOCH + _dt.timedelta(days=float(serial))
    except (OverflowError, ValueError):
        return serial


def _drop_trailing_empty(rows: List[List[Any]]) -> List[List[Any]]:
    while rows and all(str(cell).strip() == "" for cell in rows[-1]):
        rows.pop()
    return rows


def table_to_csv_text(table: Table, delimiter: str = ";") -> str:
    """Serialisation utilitaire (tests, export intermediaire)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, lineterminator="\n")
    writer.writerow(table.headers)
    writer.writerows(table.rows)
    return buffer.getvalue()
