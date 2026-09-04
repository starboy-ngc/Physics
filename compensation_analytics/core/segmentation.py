"""Filtres combinables et decoupage de la population par dimension.

Les filtres sont declaratifs (structure de donnees), jamais du code evalue :
aucun `eval`/`exec` n'intervient dans la selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .errors import ConfigError
from .normalize import Employee, Population

SEGMENT_FIELDS = (
    "business_unit", "country", "site", "job", "job_family",
    "grade", "status", "gender", "age_band", "tenure_band",
)

SEGMENT_LABELS = {
    "business_unit": "BU",
    "country": "Pays",
    "site": "Etablissement",
    "job": "Metier",
    "job_family": "Famille metier",
    "grade": "Grade",
    "status": "Statut",
    "gender": "Sexe",
    "age_band": "Tranche d'age",
    "tenure_band": "Tranche d'anciennete",
}

_OPERATORS = ("eq", "ne", "in", "not_in", "gt", "gte", "lt", "lte", "contains", "between")


@dataclass
class Filter:
    """Critere unitaire : champ, operateur, valeur."""

    field: str
    operator: str = "eq"
    value: Any = None

    def matches(self, employee: Employee) -> bool:
        actual = employee.value(self.field)
        operator = self.operator
        if operator == "eq":
            return _text(actual) == _text(self.value)
        if operator == "ne":
            return _text(actual) != _text(self.value)
        if operator == "in":
            return _text(actual) in {_text(item) for item in _as_list(self.value)}
        if operator == "not_in":
            return _text(actual) not in {_text(item) for item in _as_list(self.value)}
        if operator == "contains":
            return _text(self.value) in _text(actual)
        if operator == "between":
            bounds = _as_list(self.value)
            if len(bounds) != 2 or actual is None:
                return False
            return _number(bounds[0]) <= actual <= _number(bounds[1])
        if actual is None:
            return False
        threshold = _number(self.value)
        if operator == "gt":
            return actual > threshold
        if operator == "gte":
            return actual >= threshold
        if operator == "lt":
            return actual < threshold
        if operator == "lte":
            return actual <= threshold
        raise ConfigError(
            f"Le critere de filtre \"{operator}\" n'est pas reconnu.",
            technical=f"unsupported operator: {operator}",
        )

    def describe(self) -> str:
        label = SEGMENT_LABELS.get(self.field, self.field)
        if self.operator in ("in", "not_in", "between"):
            rendered = ", ".join(str(item) for item in _as_list(self.value))
        else:
            rendered = str(self.value)
        symbol = {
            "eq": "=", "ne": "≠", "in": "∈", "not_in": "∉", "gt": ">",
            "gte": "≥", "lt": "<", "lte": "≤", "contains": "contient",
            "between": "entre",
        }[self.operator]
        return f"{label} {symbol} {rendered}"


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip().casefold()


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(
            "La valeur du filtre numerique n'est pas un nombre.",
            technical=f"non numeric filter value: {value!r}",
        ) from exc


def build_filters(definitions: Sequence[Dict[str, Any]]) -> List[Filter]:
    """Construit des filtres a partir d'une definition JSON/CLI."""
    filters: List[Filter] = []
    for definition in definitions or []:
        field_name = definition.get("field")
        if not field_name:
            raise ConfigError(
                "Un filtre est incomplet : le champ a filtrer n'est pas indique.",
                technical=f"filter without field: {definition!r}",
            )
        operator = definition.get("operator", "eq")
        if operator not in _OPERATORS:
            raise ConfigError(
                f"Le critere de filtre \"{operator}\" n'est pas reconnu.",
                technical=f"unsupported operator: {operator}",
            )
        filters.append(Filter(field_name, operator, definition.get("value")))
    return filters


def apply_filters(population: Population, filters: Sequence[Filter]) -> Population:
    """Intersection de tous les criteres (ET logique)."""
    if not filters:
        return population
    selected = [
        employee for employee in population
        if all(criterion.matches(employee) for criterion in filters)
    ]
    return population.filtered(selected)


def describe_filters(filters: Sequence[Filter]) -> str:
    return " + ".join(criterion.describe() for criterion in filters) or "Aucun filtre"


def split_by(
    population: Population, field_name: str, include_empty: bool = False
) -> Dict[str, Population]:
    """Decoupe la population par valeur d'une dimension."""
    groups: Dict[str, List[Employee]] = {}
    for employee in population:
        key = employee.value(field_name)
        key = "" if key is None else str(key).strip()
        if not key:
            if not include_empty:
                continue
            key = "(non renseigne)"
        groups.setdefault(key, []).append(employee)
    return {
        key: population.filtered(members)
        for key, members in sorted(groups.items(), key=lambda item: item[0])
    }


def available_segments(population: Population) -> List[str]:
    """Dimensions reellement exploitables dans la population chargee."""
    usable: List[str] = []
    for field_name in SEGMENT_FIELDS:
        if any(str(employee.value(field_name) or "").strip() for employee in population):
            usable.append(field_name)
    return usable
