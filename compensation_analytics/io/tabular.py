"""Lecture de populations depuis CSV / XLSX / XLSM.

Le resultat est toujours la meme structure neutre :

    Table(headers=[...], rows=[[cell, ...], ...], source_name="...")

ce qui isole completement le reste du moteur du format d'entree.
"""

from __future__ import annotations

import csv
import datetime as _dt
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
            "Vérifiez le chemin indique.",
            technical=f"missing file: {path}",
        )
    extension = os.path.splitext(path)[1].lower()
    if extension in (".csv", ".txt"):
        return _read_csv(path)
    if extension in (".xlsx", ".xlsm"):
        return _read_xlsx(path, sheet)
    raise ImportError_(
        "Format de fichier non pris en charge. "
        "Formats acceptés : Excel (.xlsx, .xlsm) et CSV (.csv).",
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
            "Le fichier CSV n'a pas pu être ouvert.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    except UnicodeDecodeError as exc:
        raise ImportError_(
            "Le fichier CSV n'est pas encodé en UTF-8. "
            "Enregistrez-le au format \"CSV UTF-8\" depuis Excel.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    if not rows:
        raise ImportError_(
            "Le fichier importe est vide.",
            technical="csv file has no rows",
        )
    keep = _named_columns(rows[0])
    headers = [str(rows[0][index]).strip() for index in keep]
    body = _select(rows[1:], keep)
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
            "Le fichier Excel est illisible ou endommagé. "
            "Ouvrez-le dans Excel puis enregistrez-le à nouveau au format .xlsx.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    except (OSError, ElementTree.ParseError, KeyError) as exc:
        raise ImportError_(
            "Le contenu du fichier Excel n'a pas pu être lu.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc

    rows = _drop_trailing_empty(rows)
    if not rows:
        raise ImportError_(
            "L'onglet importe ne contient aucune donnée.",
            technical="xlsx sheet has no rows",
        )
    keep = _named_columns(rows[0])
    headers = [str(rows[0][index]).strip() for index in keep]
    body = _select(rows[1:], keep)
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
    # « sheets or [] » testait la valeur de verite d'un Element : Python la
    # deprecie et la fera lever. L'absence de nœud se teste explicitement.
    entries = list(sheets) if sheets is not None else []
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
            # Excel omet les lignes vides du fichier : sans les restituer, la
            # troisieme ligne lue pouvait etre la septieme du classeur, et le
            # controle qualite renvoyait l'utilisateur a une ligne qui n'est
            # pas celle a corriger.
            _restore_gap(rows, element.get("r"))
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
    # Les lignes sont rendues telles quelles, sans etre alignees sur la plus
    # large. Les aligner ici materialisait toutes les cellules vides jusqu'a
    # la derniere colonne rencontree : une seule cellule egaree en XFD — une
    # ligne mise en forme jusqu'au bout de la feuille, ce qu'un export RH
    # comporte souvent — portait un fichier de 5 000 lignes a 16 384
    # colonnes, soit 82 millions de cellules, 1,3 Go de memoire et dix
    # secondes de lecture. C'est l'en-tete qui decide de la largeur utile,
    # et lui seul.
    return rows


def _named_columns(header_row: Sequence[Any]) -> List[int]:
    """Indices des colonnes portant un intitule.

    Une colonne sans intitule ne peut correspondre a aucun champ : le
    mapping l'ignore de toute facon. La retirer des l'import evite d'en
    porter le poids d'un bout a l'autre de la chaine — et surtout de
    materialiser des millions de cellules vides.
    """
    return [index for index, cell in enumerate(header_row)
            if str(cell if cell is not None else "").strip()]


def _select(rows: List[List[Any]], keep: List[int]) -> List[List[Any]]:
    """Ne conserve que les colonnes retenues, en comblant les manquantes."""
    return [[row[index] if index < len(row) else "" for index in keep]
            for row in rows]


#: Au-dela de cet ecart, la ligne annoncee releve du fichier fabrique et
#: non de lignes vides : mieux vaut une numerotation decalee qu'un million
#: de lignes vides en memoire.
_MAX_ROW_GAP = 50_000


def _restore_gap(rows: List[List[Any]], reference: str | None) -> None:
    """Reinsere les lignes vides qu'Excel n'a pas ecrites."""
    if not reference or not reference.isdigit():
        return
    expected = int(reference) - 1
    missing = expected - len(rows)
    if 0 < missing <= _MAX_ROW_GAP:
        rows.extend([] for _ in range(missing))


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
