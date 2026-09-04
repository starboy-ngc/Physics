"""Utilitaires de test. Aucune donnee RH reelle n'est utilisee."""

from __future__ import annotations

import datetime as _dt
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.core.config import Configuration, load_configuration
from compensation_analytics.core.mapping import resolve_mapping
from compensation_analytics.core.normalize import Population, normalise_table

REFERENCE_DATE = _dt.date(2025, 1, 1)

HEADERS = [
    "Matricule", "Nom", "Prénom", "Sexe", "Date de naissance", "Date d'entrée",
    "Date de sortie", "BU", "Pays", "Grade", "Statut", "Salaire de base",
]


def make_row(
    index: int,
    salary: Optional[float] = 40000,
    business_unit: str = "France",
    grade: str = "G4",
    gender: str = "F",
    age: float = 40,
    tenure: float = 5,
    employee_id: Optional[str] = None,
    birth_date: Any = None,
    hire_date: Any = None,
    leave_date: Any = "",
) -> List[Any]:
    birth = birth_date if birth_date is not None else (
        REFERENCE_DATE - _dt.timedelta(days=int(age * 365.2425))
    )
    hire = hire_date if hire_date is not None else (
        REFERENCE_DATE - _dt.timedelta(days=int(tenure * 365.2425))
    )
    return [
        employee_id if employee_id is not None else f"E{index:05d}",
        f"NOM{index}", f"PRENOM{index}", gender, birth, hire, leave_date,
        business_unit, "France", grade, "Cadre",
        "" if salary is None else salary,
    ]


def build_population(
    rows: List[List[Any]],
    config: Optional[Configuration] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Population:
    config = config or make_config(overrides)
    mapping = resolve_mapping(HEADERS, config)
    return normalise_table(
        HEADERS, rows, mapping, config,
        source_name="test", reference_date=REFERENCE_DATE,
    )


def make_config(overrides: Optional[Dict[str, Any]] = None) -> Configuration:
    config = load_configuration()
    data = config.as_dict()
    for path, value in (overrides or {}).items():
        node = data
        parts = path.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return Configuration(data)
