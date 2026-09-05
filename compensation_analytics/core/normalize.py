"""Couche NORMALIZED DATA : pivot entre l'import et le moteur statistique.

RAW -> MAPPING -> NORMALIZED -> ANALYTICS DATASET

Toute la suite du moteur ne connait que `Employee` / `Population`. Changer de
format d'import n'impacte donc que `io.tabular` et `core.mapping`.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from .config import Configuration
from .mapping import MappingResult

_NUMBER_CLEAN_RE = re.compile(r"[^\d,.\-]")
_DATE_FORMATS = (
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d",
    "%d.%m.%Y", "%m/%d/%Y", "%Y%m%d",
)
_DAYS_PER_YEAR = 365.2425

TEXT_FIELDS = (
    "gender", "business_unit", "country", "site", "job",
    "job_family", "grade", "status",
)


@dataclass
class Employee:
    """Salarie normalise. Les champs derives sont calcules une seule fois."""

    row_number: int
    employee_id: str = ""
    anonymous_id: str = ""
    last_name: str = ""
    first_name: str = ""
    gender: str = ""
    birth_date: Optional[_dt.date] = None
    hire_date: Optional[_dt.date] = None
    leave_date: Optional[_dt.date] = None
    business_unit: str = ""
    country: str = ""
    site: str = ""
    job: str = ""
    job_family: str = ""
    grade: str = ""
    coefficient: Optional[float] = None
    status: str = ""
    fte: Optional[float] = None
    base_salary: Optional[float] = None
    variable_pay: Optional[float] = None
    total_compensation: Optional[float] = None
    age_years: Optional[float] = None
    tenure_years: Optional[float] = None
    age_band: str = ""
    tenure_band: str = ""
    issues: List[str] = field(default_factory=list)
    #: Champs declares au mapping mais absents du modele (ex. une notion
    #: metier ajoutee par configuration). Ils sont filtrables et
    #: segmentables au meme titre que les champs natifs.
    extra: Dict[str, Any] = field(default_factory=dict)

    def value(self, name: str) -> Any:
        if name in self.extra:
            return self.extra[name]
        return getattr(self, name, None)

    def assign(self, name: str, value: Any) -> None:
        """Ecrit un champ natif, ou le range dans `extra` s'il n'existe pas."""
        if hasattr(self, name):
            setattr(self, name, value)
        else:
            self.extra[name] = value


@dataclass
class Population:
    """Ensemble de salaries normalises + metadonnees de tracabilite."""

    employees: List[Employee] = field(default_factory=list)
    source_name: str = ""
    reference_date: Optional[_dt.date] = None
    mapped_fields: List[str] = field(default_factory=list)
    raw_row_count: int = 0
    #: Tranches effectivement posees sur cette population. Elles peuvent
    #: differer de la configuration, la derniere tranche ouverte etant
    #: prolongee selon les valeurs observees : tout ce qui les affiche doit
    #: donc les lire ici, et non relire le fichier de parametres.
    age_bands: List[Dict[str, Any]] = field(default_factory=list)
    tenure_bands: List[Dict[str, Any]] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.employees)

    def __iter__(self) -> Iterable[Employee]:
        return iter(self.employees)

    def filtered(self, employees: List[Employee]) -> "Population":
        return Population(
            employees=employees,
            source_name=self.source_name,
            reference_date=self.reference_date,
            mapped_fields=list(self.mapped_fields),
            age_bands=list(self.age_bands),
            tenure_bands=list(self.tenure_bands),
            raw_row_count=self.raw_row_count,
        )


# --------------------------------------------------------------- conversions


def parse_number(value: Any) -> Optional[float]:
    """Convertit une cellule en nombre. Retourne None si non convertible.

    Gere les formats francais ("45 000,50", "45 000 €") et anglo-saxons
    ("45,000.50"). Aucune evaluation dynamique n'est utilisee.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(" ", "").replace(" ", "")
    text = _NUMBER_CLEAN_RE.sub("", text)
    if not text or text in ("-", ".", ","):
        return None
    if "," in text and "." in text:
        # Le dernier separateur rencontre est le separateur decimal.
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


_AMBIGUOUS_RE = re.compile(r"^-?[1-9]\d{0,2}[.,]\d{3}$")


def has_ambiguous_separator(value: Any) -> bool:
    """Detecte une ecriture dont le separateur est ambigu.

    "45.000" vaut 45 000 dans un fichier francais et 45,0 en lecture
    anglo-saxonne. Le moteur retient la lecture standard (separateur
    decimal) mais signale le cas au controle qualite plutot que de deviner
    en silence. Les valeurs commencant par 0 ("0,800") sont exclues : ce
    sont des decimales sans ambiguite.
    """
    if isinstance(value, (int, float)) or value is None:
        return False
    return bool(_AMBIGUOUS_RE.match(str(value).strip().replace(" ", "")))


def parse_date(value: Any) -> Optional[_dt.date]:
    """Convertit une cellule en date. Retourne None si non convertible."""
    if value is None or value == "":
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        # Serie Excel eventuellement transmise en nombre brut.
        try:
            return _dt.date(1899, 12, 30) + _dt.timedelta(days=float(value))
        except (OverflowError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    text = text.split("T")[0].split(" ")[0]
    for fmt in _DATE_FORMATS:
        try:
            return _dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def years_between(start: _dt.date, end: _dt.date) -> float:
    return (end - start).days / _DAYS_PER_YEAR


def band_for(value: Optional[float], bands: List[Dict[str, Any]]) -> str:
    """Tranche parametree contenant `value`.

    La borne basse est toujours incluse. La borne haute est exclue par defaut
    (`<2 ans` = anciennete strictement inferieure a 2). Une tranche peut
    declarer `"max_inclusive": true` pour une lecture en unites revolues :
    la tranche d'age `20-29` couvre alors les ages de 20,0 a 29,99 an.
    """
    if value is None:
        return ""
    for band in bands:
        low = band.get("min")
        high = band.get("max")
        if low is not None and value < low:
            continue
        if high is not None:
            if band.get("max_inclusive", False):
                if math.floor(value) > high:
                    continue
            elif value >= high:
                continue
        return str(band.get("label", ""))
    return ""


def extend_open_band(bands: List[Dict[str, Any]], observed_max: Optional[float],
                     step: float, closed_label: str, open_label: str,
                     limit: int = 10) -> List[Dict[str, Any]]:
    """Prolonge la derniere tranche ouverte jusqu'a la valeur observee.

    Une derniere tranche « > 10 ans » range ensemble un salarie de 11 ans
    d'anciennete et un autre de 30 : la comparaison n'a plus de sens des que
    la population contient des carrieres longues. Les tranches suivantes
    sont donc engendrees au pas configure, jusqu'a couvrir le maximum
    reellement present.

    Rien n'est engendre quand la population ne va pas plus loin que la
    tranche ouverte : le decoupage configure reste alors intact.
    """
    if not bands or observed_max is None or step <= 0:
        return bands
    last = bands[-1]
    if last.get("max") is not None:
        return bands            # decoupage entierement borne : rien a prolonger
    floor = last.get("min")
    if floor is None:
        return bands
    extended = list(bands[:-1])
    low = float(floor)
    added = 0
    while low + step < observed_max and added < limit:
        high = low + step
        extended.append({
            "label": closed_label.format(low=_band_number(low),
                                         high=_band_number(high)),
            "min": low, "max": high,
        })
        low = high
        added += 1
    extended.append({"label": open_label.format(low=_band_number(low)),
                     "min": low, "max": None})
    return extended


def _band_number(value: float) -> str:
    """Une borne de tranche s'ecrit sans decimale inutile."""
    return str(int(value)) if float(value).is_integer() else str(value)


def resolve_bands(config: Configuration, section: str,
                  observed_max: Optional[float]) -> List[Dict[str, Any]]:
    """Tranches d'une section, prolongees si la configuration le demande."""
    bands = config.get(f"{section}.bands", []) or []
    if not config.get(f"{section}.auto_extend", False):
        return bands
    return extend_open_band(
        bands, observed_max,
        float(config.get(f"{section}.extend_step", 5) or 5),
        str(config.get(f"{section}.band_label", "{low}-{high}")),
        str(config.get(f"{section}.open_band_label", ">{low}")),
        int(config.get(f"{section}.extend_max_bands", 10) or 10),
    )


def _observed_max(employees: Iterable["Employee"], field_name: str) -> Optional[float]:
    values = [getattr(item, field_name) for item in employees
              if getattr(item, field_name) is not None]
    return max(values) if values else None


def anonymise(identifier: str, salt: str = "compensation-analytics") -> str:
    """Identifiant stable non reversible sans le sel, pour affichage/logs."""
    digest = hashlib.sha256(f"{salt}:{identifier}".encode("utf-8")).hexdigest()
    return digest[:12].upper()


# ---------------------------------------------------------------- pipeline


def normalise_table(
    headers: List[str],
    rows: List[List[Any]],
    mapping: MappingResult,
    config: Configuration,
    source_name: str = "",
    reference_date: Optional[_dt.date] = None,
) -> Population:
    """Construit la population normalisee a partir du tableau brut."""
    section = config.section("population_mapping")
    numeric_fields = set(section.get("numeric", []))
    date_fields = set(section.get("date", []))
    reference = reference_date or _configured_reference_date(config) or _dt.date.today()

    anonymise_ids = bool(config.get("privacy_parameters.anonymise_identifiers", True))

    employees: List[Employee] = []
    for offset, row in enumerate(rows):
        if all(str(cell).strip() == "" for cell in row):
            continue
        employee = Employee(row_number=offset + 2)  # +2 : en-tete + base 1
        for field_name, index in mapping.field_to_index.items():
            if index >= len(row):
                continue
            raw = row[index]
            if field_name in numeric_fields:
                number = parse_number(raw)
                if number is None and str(raw).strip() != "":
                    employee.issues.append(f"{field_name}:not_numeric")
                elif has_ambiguous_separator(raw):
                    employee.issues.append(f"{field_name}:ambiguous_separator")
                employee.assign(field_name, number)
            elif field_name in date_fields:
                date_value = parse_date(raw)
                if date_value is None and str(raw).strip() != "":
                    employee.issues.append(f"{field_name}:invalid_date")
                employee.assign(field_name, date_value)
            else:
                employee.assign(
                    field_name, str(raw).strip() if raw is not None else ""
                )

        if employee.birth_date:
            employee.age_years = years_between(employee.birth_date, reference)
        end_date = employee.leave_date or reference
        if employee.hire_date:
            employee.tenure_years = years_between(employee.hire_date, end_date)
        employee.anonymous_id = (
            anonymise(employee.employee_id) if (anonymise_ids and employee.employee_id)
            else employee.employee_id
        )
        employees.append(employee)

    # Les tranches sont posees en second temps : prolonger la derniere
    # tranche ouverte suppose de connaitre le maximum de la population, qui
    # n'est etabli qu'une fois toutes les lignes lues.
    age_bands = resolve_bands(config, "age_parameters",
                              _observed_max(employees, "age_years"))
    tenure_bands = resolve_bands(config, "tenure_parameters",
                                 _observed_max(employees, "tenure_years"))
    for employee in employees:
        employee.age_band = band_for(employee.age_years, age_bands)
        employee.tenure_band = band_for(employee.tenure_years, tenure_bands)

    return Population(
        employees=employees,
        source_name=source_name,
        reference_date=reference,
        mapped_fields=sorted(mapping.field_to_index),
        raw_row_count=len(rows),
        age_bands=age_bands,
        tenure_bands=tenure_bands,
    )


def _configured_reference_date(config: Configuration) -> Optional[_dt.date]:
    for path in ("age_parameters.reference_date", "tenure_parameters.reference_date"):
        value = config.get(path)
        if value:
            parsed = parse_date(value)
            if parsed:
                return parsed
    return None
