"""Dimensions d'analyse, filtres combinables et decoupage de la population.

Les dimensions ne sont pas codees en dur : elles sont declarees dans
`population_mapping.json`. Ajouter une notion metier (equipe, manager,
direction) est donc une ligne de configuration, jamais une modification du
code — conformement au principe "le mapping ne doit pas etre hardcode".

Les filtres sont declaratifs (structure de donnees), jamais du code evalue :
aucun `eval`/`exec` n'intervient dans la selection.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .config import Configuration
from .errors import ConfigError
from .normalize import Employee, Population

_OPERATORS = ("eq", "ne", "in", "not_in", "gt", "gte", "lt", "lte",
              "contains", "between")

# Champs techniques du modele normalise, jamais exposes comme critere.
_INTERNAL_FIELDS = {"row_number", "issues", "anonymous_id", "extra"}

# Champs numeriques et dates : la comparaison d'egalite doit se faire sur la
# valeur, pas sur son ecriture ("50000" doit trouver 50000.0).
_TYPED_FIELDS = {
    field.name: field.type
    for field in dataclasses.fields(Employee)
    if field.name not in _INTERNAL_FIELDS
}

#: Champs du modele normalise, disponibles quelle que soit la configuration.
CORE_FIELDS = tuple(sorted(_TYPED_FIELDS))


@dataclass
class Filter:
    """Critere unitaire : champ, operateur, valeur."""

    field: str
    operator: str = "eq"
    value: Any = None

    def matches(self, employee: Employee) -> bool:
        actual = employee.value(self.field)
        operator = self.operator
        if operator in ("eq", "ne", "in", "not_in"):
            return self._matches_equality(actual, operator)
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
            f"Le critère de filtre \"{operator}\" n'est pas reconnu.",
            technical=f"unsupported operator: {operator}",
        )

    def _matches_equality(self, actual: Any, operator: str) -> bool:
        """Egalite tolerante au type.

        Un salaire saisi "50000" doit retrouver la valeur 50000.0, et une
        date "2020-01-01" la date correspondante : comparer les ecritures
        renverrait zero salarie sans le moindre message.
        """
        candidates = _as_list(self.value) if operator in ("in", "not_in") else [self.value]
        found = any(_equivalent(actual, candidate) for candidate in candidates)
        return found if operator in ("eq", "in") else not found

    def describe(self, labels: Optional[Dict[str, str]] = None) -> str:
        label = (labels or {}).get(self.field, self.field)
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


def _equivalent(actual: Any, expected: Any) -> bool:
    """Compare d'abord numeriquement, puis textuellement."""
    if isinstance(actual, (int, float)) and not isinstance(actual, bool):
        expected_number = _optional_number(expected)
        if expected_number is not None:
            return float(actual) == expected_number
        return False
    return _text(actual) == _text(expected)


def _optional_number(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    from .normalize import parse_number  # import local : evite un cycle

    return parse_number(value)


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _number(value: Any) -> float:
    number = _optional_number(value)
    if number is None:
        raise ConfigError(
            f"La valeur de filtre \"{value}\" n'est pas un nombre. "
            "Les critères de comparaison (>, >=, <, <=, entre) attendent "
            "une valeur numérique.",
            technical=f"non numeric filter value: {value!r}",
        )
    return number


# ---------------------------------------------------------------- dimensions


def dimensions(config: Configuration) -> List[Dict[str, str]]:
    """Dimensions d'analyse declarees en configuration."""
    declared = config.get("population_mapping.dimensions", []) or []
    result: List[Dict[str, str]] = []
    for entry in declared:
        if isinstance(entry, str):
            result.append({"field": entry, "label": entry})
        elif isinstance(entry, dict) and entry.get("field"):
            result.append({
                "field": entry["field"],
                "label": entry.get("label") or entry["field"],
            })
    return result


def dimension_fields(config: Configuration) -> List[str]:
    return [entry["field"] for entry in dimensions(config)]


def dimension_labels(config: Configuration) -> Dict[str, str]:
    return {entry["field"]: entry["label"] for entry in dimensions(config)}


def dimension_label(config: Configuration, field_name: str) -> str:
    return dimension_labels(config).get(field_name, field_name)


def filterable_fields(config: Optional[Configuration] = None) -> List[str]:
    """Champs sur lesquels un filtre a un sens.

    Champs du modele normalise, plus tout champ declare au mapping (une
    colonne metier ajoutee par configuration est donc filtrable sans
    modification du code).
    """
    fields = set(CORE_FIELDS)
    if config is not None:
        fields.update(config.get("population_mapping.fields", {}) or {})
        fields.update(dimension_fields(config))
        fields.discard("")
    return sorted(fields)


def _ensure_known_field(field_name: str, allowed: Sequence[str], usage: str) -> None:
    if field_name in allowed:
        return
    # Sans ce controle, un champ mal orthographie ne remonterait aucun
    # salarie sans le moindre message : l'utilisateur conclurait a une
    # population vide plutot qu'a une erreur de saisie.
    raise ConfigError(
        f"Le champ \"{field_name}\" n'existe pas et ne peut pas être {usage}. "
        f"Champs disponibles : {', '.join(allowed)}.",
        technical=f"unknown field: {field_name}",
    )


# ------------------------------------------------------------------- filtres


def build_filters(
    definitions: Sequence[Dict[str, Any]],
    config: Optional[Configuration] = None,
) -> List[Filter]:
    """Construit des filtres a partir d'une definition JSON/CLI."""
    allowed = filterable_fields(config)
    filters: List[Filter] = []
    for definition in definitions or []:
        field_name = definition.get("field")
        if not field_name:
            raise ConfigError(
                "Un filtre est incomplet : le champ a filtrer n'est pas indique.",
                technical=f"filter without field: {definition!r}",
            )
        _ensure_known_field(field_name, allowed, "filtre")
        operator = definition.get("operator", "eq")
        if operator not in _OPERATORS:
            raise ConfigError(
                f"Le critère de filtre \"{operator}\" n'est pas reconnu.",
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


def describe_filters(
    filters: Sequence[Filter], config: Optional[Configuration] = None
) -> str:
    labels = dimension_labels(config) if config is not None else {}
    return " + ".join(criterion.describe(labels) for criterion in filters) or "Aucun filtre"


# -------------------------------------------------------------- segmentation


def validate_segments(
    fields: Sequence[str], config: Configuration
) -> List[str]:
    """Verifie que chaque dimension demandee existe."""
    allowed = filterable_fields(config)
    for field_name in fields:
        _ensure_known_field(field_name, allowed, "utilisé comme segment")
    return list(fields)


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


def available_segments(population: Population, config: Configuration) -> List[str]:
    """Dimensions declarees et reellement renseignees dans la population."""
    usable: List[str] = []
    for field_name in dimension_fields(config):
        if any(str(employee.value(field_name) or "").strip() for employee in population):
            usable.append(field_name)
    return usable
