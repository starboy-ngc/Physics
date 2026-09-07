"""Data Quality Check execute avant tout calcul.

Chaque constat est un `Finding` : severite, code technique, libelle utilisateur
et nombre de lignes concernees. Les numeros de ligne sont conserves (ils aident
la correction) mais aucune donnee personnelle n'est stockee dans le rapport.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import Configuration, analysis_field
from .mapping import MappingResult
from .normalize import Population
from .statistics_engine import clean, iqr_outlier_bounds

CRITICAL = "critique"
WARNING = "avertissement"
INFO = "information"

_SEVERITY_ORDER = {CRITICAL: 0, WARNING: 1, INFO: 2}


@dataclass
class Finding:
    """Constat unitaire du controle qualite."""

    code: str
    severity: str
    message: str
    count: int = 0
    rows: List[int] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "code": self.code,
            "severite": self.severity,
            "message": self.message,
            "lignes_concernees": self.count,
            "exemples_lignes": self.rows[:20],
        }


@dataclass
class QualityReport:
    """Synthese du controle qualite."""

    imported_rows: int = 0
    retained_rows: int = 0
    unique_employees: int = 0
    duplicates: int = 0
    #: Nombre de periodes distinctes. Zero quand le fichier est un instantane.
    periods: int = 0
    missing_salary: int = 0
    invalid_dates: int = 0
    findings: List[Finding] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == WARNING)

    @property
    def status(self) -> str:
        if self.critical_count:
            return "CORRECTIONS REQUISES"
        if self.warning_count:
            return "POINTS DE VIGILANCE"
        return "CONFORME"

    @property
    def blocking(self) -> bool:
        return self.critical_count > 0

    def sorted_findings(self) -> List[Finding]:
        return sorted(self.findings, key=lambda item: _SEVERITY_ORDER[item.severity])

    def as_dict(self) -> Dict[str, object]:
        return {
            "lignes_importees": self.imported_rows,
            "lignes_retenues": self.retained_rows,
            "salaries_uniques": self.unique_employees,
            "periodes": self.periods,
            "doublons": self.duplicates,
            "salaires_manquants": self.missing_salary,
            "dates_invalides": self.invalid_dates,
            "anomalies_critiques": self.critical_count,
            "avertissements": self.warning_count,
            "statut": self.status,
            "constats": [item.as_dict() for item in self.sorted_findings()],
        }

    def to_text(self) -> str:
        lines = [
            "DATA QUALITY CHECK",
            f"Lignes importées       : {self.imported_rows:,}".replace(",", " "),
            f"Salariés uniques       : {self.unique_employees:,}".replace(",", " "),
            f"Périodes               : {self.periods or 'aucune (instantané)'}",
            f"Doublons               : {self.duplicates}",
            f"Salaires manquants     : {self.missing_salary}",
            f"Dates invalides        : {self.invalid_dates}",
            f"Anomalies critiques    : {self.critical_count}",
            f"STATUT : {self.status}",
        ]
        for finding in self.sorted_findings():
            lines.append(f"  [{finding.severity}] {finding.message} ({finding.count})")
        return "\n".join(lines)


def run_quality_check(
    population: Population,
    mapping: MappingResult,
    config: Configuration,
) -> QualityReport:
    """Execute l'ensemble des controles structure / dates / remuneration."""
    report = QualityReport(
        imported_rows=population.raw_row_count,
        retained_rows=len(population),
    )
    _check_structure(population, mapping, report)
    _check_population(population, report)
    _check_dates(population, report)
    _check_salary(population, config, report)
    return report


def _add(report: QualityReport, code: str, severity: str, message: str,
         rows: List[int]) -> None:
    if not rows:
        return
    report.findings.append(
        Finding(code=code, severity=severity, message=message,
                count=len(rows), rows=sorted(rows))
    )


def _check_structure(
    population: Population, mapping: MappingResult, report: QualityReport
) -> None:
    if not population.employees:
        report.findings.append(
            Finding(
                code="empty_population",
                severity=CRITICAL,
                message="Le fichier importe ne contient aucun salarié exploitable.",
                count=0,
            )
        )
    if mapping.unknown_columns:
        report.findings.append(
            Finding(
                code="unknown_columns",
                severity=INFO,
                message=(
                    "Colonnes non reconnues, ignorées par l'analyse : "
                    + ", ".join(f'"{name}"' for name in mapping.unknown_columns[:10])
                ),
                count=len(mapping.unknown_columns),
            )
        )
    if mapping.duplicate_columns:
        report.findings.append(
            Finding(
                code="duplicate_columns",
                severity=WARNING,
                message=(
                    "Colonnes en double dans le fichier, seule la première est "
                    "utilisée : "
                    + ", ".join(f'"{name}"' for name in mapping.duplicate_columns[:10])
                ),
                count=len(mapping.duplicate_columns),
            )
        )
    type_issues: Dict[str, List[int]] = {}
    for employee in population:
        for issue in employee.issues:
            type_issues.setdefault(issue, []).append(employee.row_number)
    for issue, rows in type_issues.items():
        field_name, kind = issue.split(":", 1)
        if kind == "invalid_date":
            continue  # traite dans _check_dates pour un message unique
        if kind == "ambiguous_separator":
            _add(
                report, f"ambiguous_separator_{field_name}", WARNING,
                f'Séparateur ambigu dans le champ "{field_name}" : une '
                'écriture du type "45.000" a été lue comme 45,0 et non comme '
                "45 000. Vérifiez le format des nombres à l'export du fichier.",
                rows,
            )
            continue
        _add(
            report, f"type_{issue}", WARNING,
            f"Valeurs non numériques dans le champ \"{field_name}\".", rows,
        )


def _check_population(population: Population, report: QualityReport) -> None:
    """Unicite des salaries, periode par periode s'il y en a une.

    Un fichier de trois ans porte trois lignes par salarie : c'est
    l'intention, pas une erreur. L'identite est donc le couple matricule +
    periode des lors que la colonne existe. Sans colonne de periode, un
    matricule repete reste ce qu'il a toujours ete — un doublon.
    """
    dated = any(employee.period for employee in population)
    seen: Dict[tuple, int] = {}
    duplicate_rows: List[int] = []
    missing_id_rows: List[int] = []
    for employee in population:
        identifier = (employee.employee_id or "").strip()
        if not identifier:
            missing_id_rows.append(employee.row_number)
            continue
        key = (identifier, employee.period) if dated else (identifier, "")
        if key in seen:
            duplicate_rows.append(employee.row_number)
        else:
            seen[key] = employee.row_number
    report.duplicates = len(duplicate_rows)
    report.unique_employees = (len({key[0] for key in seen})
                               + len(missing_id_rows))
    report.periods = len({employee.period for employee in population
                          if employee.period})
    _add(
        report, "duplicate_employee_id", CRITICAL,
        ("Matricules présents plusieurs fois sur une même période."
         if dated else "Matricules présents plusieurs fois dans le fichier."),
        duplicate_rows,
    )
    _add(
        report, "missing_employee_id", WARNING,
        "Lignes sans matricule : le suivi des doublons est impossible pour "
        "ces salariés.", missing_id_rows,
    )


def _check_dates(population: Population, report: QualityReport) -> None:
    reference = population.reference_date
    invalid: List[int] = []
    future_birth: List[int] = []
    future_hire: List[int] = []
    leave_before_hire: List[int] = []
    implausible_age: List[int] = []
    for employee in population:
        if any(issue.endswith(":invalid_date") for issue in employee.issues):
            invalid.append(employee.row_number)
        if employee.birth_date and reference and employee.birth_date > reference:
            future_birth.append(employee.row_number)
        if employee.hire_date and reference and employee.hire_date > reference:
            future_hire.append(employee.row_number)
        if employee.hire_date and employee.leave_date and (
            employee.leave_date < employee.hire_date
        ):
            leave_before_hire.append(employee.row_number)
        if employee.age_years is not None and not (14 <= employee.age_years <= 80):
            implausible_age.append(employee.row_number)
    report.invalid_dates = len(invalid)
    _add(report, "invalid_date", CRITICAL,
         "Dates illisibles : le format n'a pas pu être interprété.", invalid)
    _add(report, "future_birth_date", CRITICAL,
         "Date de naissance postérieure à la date d'analyse.", future_birth)
    _add(report, "future_hire_date", WARNING,
         "Date d'entrée postérieure à la date d'analyse.", future_hire)
    _add(report, "leave_before_hire", CRITICAL,
         "Date de sortie antérieure à la date d'entrée.", leave_before_hire)
    _add(report, "implausible_age", WARNING,
         "Âge hors de la plage plausible (14-80 ans).", implausible_age)


def _check_salary(
    population: Population, config: Configuration, report: QualityReport
) -> None:
    field_name = analysis_field(config)
    minimum = config.get("salary_parameters.min_plausible")
    maximum = config.get("salary_parameters.max_plausible")
    factor = float(config.get("salary_parameters.outlier_factor", 1.5))

    missing: List[int] = []
    negative: List[int] = []
    zero: List[int] = []
    below: List[int] = []
    above: List[int] = []
    values: List[Optional[float]] = []
    row_by_value: List[tuple] = []

    for employee in population:
        value = employee.value(field_name)
        if value is None:
            missing.append(employee.row_number)
            continue
        if value < 0:
            negative.append(employee.row_number)
            continue
        if value == 0:
            zero.append(employee.row_number)
            continue
        if minimum is not None and value < float(minimum):
            below.append(employee.row_number)
        if maximum is not None and value > float(maximum):
            above.append(employee.row_number)
        values.append(value)
        row_by_value.append((value, employee.row_number))

    report.missing_salary = len(missing)
    _add(report, "missing_salary", CRITICAL,
         "Salaire de base absent : ces salariés sont exclus des statistiques "
         "de rémunération.", missing)
    _add(report, "negative_salary", CRITICAL, "Salaire de base négatif.", negative)
    _add(report, "zero_salary", WARNING, "Salaire de base a zéro.", zero)
    _add(report, "salary_below_threshold", WARNING,
         "Salaire inférieur au seuil de plausibilité paramètre.", below)
    _add(report, "salary_above_threshold", WARNING,
         "Salaire supérieur au seuil de plausibilité paramètre.", above)

    bounds = iqr_outlier_bounds(clean(values), factor)
    if bounds:
        extreme = [
            row for value, row in row_by_value
            if value < bounds["lower"] or value > bounds["upper"]
        ]
        _add(report, "salary_outlier", INFO,
             "Valeurs de rémunération atypiques à analyser (méthode "
             "interquartile).", extreme)
