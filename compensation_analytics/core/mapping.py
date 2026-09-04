"""Resolution du mapping colonnes source -> champs normalises.

Le mapping n'est jamais code en dur : il vient de
`config/population_mapping.json`. La resolution est tolerante (casse,
accents, espaces, ponctuation) pour absorber les variations de fichiers RH.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List

from .config import Configuration
from .errors import MappingError

_PUNCT_RE = re.compile(r"[^a-z0-9]+")


def normalise_label(label: str) -> str:
    """Cle de comparaison insensible a la casse, aux accents et a la ponctuation."""
    decomposed = unicodedata.normalize("NFKD", str(label))
    ascii_only = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _PUNCT_RE.sub(" ", ascii_only.lower()).strip()


@dataclass
class MappingResult:
    """Correspondance resolue entre colonnes du fichier et champs normalises."""

    field_to_column: Dict[str, str] = field(default_factory=dict)
    field_to_index: Dict[str, int] = field(default_factory=dict)
    unknown_columns: List[str] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    duplicate_columns: List[str] = field(default_factory=list)

    def has(self, field_name: str) -> bool:
        return field_name in self.field_to_index


def resolve_mapping(headers: List[str], config: Configuration) -> MappingResult:
    """Associe chaque en-tete du fichier a un champ normalise."""
    section = config.section("population_mapping")
    fields: Dict[str, List[str]] = section.get("fields", {})
    required: List[str] = section.get("required", [])

    alias_to_field: Dict[str, str] = {}
    for field_name, aliases in fields.items():
        alias_to_field[normalise_label(field_name)] = field_name
        for alias in aliases:
            alias_to_field[normalise_label(alias)] = field_name

    result = MappingResult()
    seen_labels: Dict[str, int] = {}
    for index, header in enumerate(headers):
        key = normalise_label(header)
        if not key:
            continue
        if key in seen_labels:
            result.duplicate_columns.append(header)
            continue
        seen_labels[key] = index
        field_name = alias_to_field.get(key)
        if field_name is None:
            result.unknown_columns.append(header)
            continue
        if field_name in result.field_to_index:
            result.duplicate_columns.append(header)
            continue
        result.field_to_column[field_name] = header
        result.field_to_index[field_name] = index

    result.missing_required = [
        name for name in required if name not in result.field_to_index
    ]
    return result


def ensure_required(result: MappingResult, config: Configuration) -> None:
    """Leve une erreur lisible si une colonne obligatoire manque."""
    if not result.missing_required:
        return
    fields: Dict[str, List[str]] = config.get("population_mapping.fields", {})
    labels = []
    for name in result.missing_required:
        aliases = fields.get(name) or [name]
        labels.append(f'"{aliases[0]}"')
    listed = ", ".join(labels)
    raise MappingError(
        f"Les colonnes suivantes n'ont pas pu etre identifiees : {listed}. "
        "Veuillez verifier le mapping des colonnes d'import "
        "(config/population_mapping.json).",
        technical=f"missing required fields: {result.missing_required}",
    )
