"""Export des resultats (Excel multi-onglets, CSV).

L'export des donnees individuelles est desactive par defaut
(`export_parameters.include_individual_data`) : il faut une action explicite
de parametrage pour sortir de la donnee nominative.
"""

from __future__ import annotations

import csv
import os
from typing import Any, Dict, List, Sequence, Tuple

from ..io.xlsx_writer import write_workbook
from . import segmentation
from .config import Configuration
from .normalize import Population


def _rows_quality(quality: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [["Indicateur", "Valeur"]]
    for key in ("lignes_importees", "lignes_retenues", "salaries_uniques",
                "doublons", "salaires_manquants", "dates_invalides",
                "anomalies_critiques", "avertissements", "statut"):
        rows.append([key.replace("_", " ").capitalize(), quality.get(key)])
    rows.append([])
    rows.append(["Severite", "Code", "Constat", "Lignes concernees"])
    for item in quality.get("constats", []):
        rows.append([item["severite"], item["code"], item["message"],
                     item["lignes_concernees"]])
    return rows


def _rows_population(population: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [["Indicateur", "Valeur"]]
    for label, key in (
        ("Effectif", "headcount"), ("Age moyen", "age_mean"),
        ("Age median", "age_median"), ("Anciennete moyenne", "tenure_mean"),
        ("Anciennete mediane", "tenure_median"),
    ):
        rows.append([label, population.get(key)])
    for title, key in (("Tranche d'age", "age_bands"),
                       ("Tranche d'anciennete", "tenure_bands")):
        rows.append([])
        rows.append([title, "Effectif", "Part (%)"])
        for band in population.get(key, []) or []:
            rows.append([band["label"], band["count"], band["share"]])
    return rows


def _rows_salary(salary: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [["Indicateur", "Valeur"]]
    for label, key in (
        ("Effectif valorise", "valued_headcount"), ("Masse salariale", "payroll"),
        ("Moyenne", "mean"), ("Mediane", "median"), ("Minimum", "min"),
        ("Maximum", "max"), ("P10", "p10"), ("Q1 (P25)", "p25"),
        ("P50", "p50"), ("Q3 (P75)", "p75"), ("P90", "p90"),
        ("Ecart-type (technique)", "std_dev"),
    ):
        if key in salary:
            rows.append([label, salary.get(key)])
    dispersion = salary.get("dispersion") or {}
    if dispersion:
        rows.append([])
        rows.append(["Dispersion", "Valeur"])
        for label, key in (
            ("Q3 - Q1", "interquartile_range"), ("Q3 / Q1", "q3_over_q1"),
            ("P90 / P10", "p90_over_p10"), ("Moyenne / Mediane", "mean_over_median"),
            ("Coefficient de variation", "coefficient_of_variation"),
        ):
            rows.append([label, dispersion.get(key)])
    return rows


def _rows_segment(segment: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [[
        segment["label"], "Effectif", "Moyenne", "Mediane", "P10", "Q1", "Q3",
        "P90", "P90/P10", "Age median", "Anciennete mediane",
    ]]
    for row in segment["rows"]:
        salary = row["salary"]
        if row["masked"]:
            rows.append([row["segment"], row["headcount"]] + ["masque"] * 9)
            continue
        dispersion = salary.get("dispersion") or {}
        rows.append([
            row["segment"], row["headcount"], salary.get("mean"), salary.get("median"),
            salary.get("p10"), salary.get("p25"), salary.get("p75"), salary.get("p90"),
            dispersion.get("p90_over_p10"), row.get("age_median"),
            row.get("tenure_median"),
        ])
    return rows


def _rows_distribution(distribution: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [["Borne basse", "Borne haute", "Effectif"]]
    for item in distribution.get("bins", []) or []:
        rows.append([item["lower"], item["upper"], item["count"]])
    outliers = distribution.get("outliers") or []
    if outliers:
        rows.append([])
        rows.append([distribution.get("outlier_label", "Situation atypique a analyser")])
        rows.append(["Reference", "BU", "Grade", "Famille metier", "Anciennete",
                     "Valeur", "Position"])
        for item in outliers:
            rows.append([
                item["reference"], item.get("business_unit"), item.get("grade"),
                item.get("job_family"), item.get("tenure_years"), item["value"],
                item["position"],
            ])
    return rows


def _rows_comparison(comparison: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [[
        "Indicateur", comparison["left_label"], comparison["right_label"],
        "Ecart", "Ecart (%)",
    ]]
    for row in comparison["rows"]:
        rows.append([row["indicator"], row["left"], row["right"], row["gap"],
                     row["gap_percent"]])
    return rows


def _rows_individual(
    population: Population, config: Configuration
) -> List[List[Any]]:
    """Colonnes derivees des dimensions declarees, pas d'une liste figee.

    Une dimension ajoutee par configuration se retrouve donc dans l'export
    au lieu d'en disparaitre en silence.
    """
    dimensions = segmentation.dimensions(config)
    headers = (["Reference"]
               + [entry["label"] for entry in dimensions]
               + ["Age", "Anciennete", "Salaire de base", "Variable",
                  "Remuneration totale"])
    rows: List[List[Any]] = [headers]
    for employee in population:
        rows.append(
            [employee.anonymous_id or employee.employee_id]
            + [employee.value(entry["field"]) for entry in dimensions]
            + [employee.age_years, employee.tenure_years, employee.base_salary,
               employee.variable_pay, employee.total_compensation]
        )
    return rows


def build_sheets(
    analysis: Dict[str, Any],
    population: Population,
    config: Configuration,
) -> List[Tuple[str, Sequence[Sequence[Any]]]]:
    """Compose les onglets du classeur d'export."""
    sheets: List[Tuple[str, Sequence[Sequence[Any]]]] = [
        ("Synthese", _rows_manifest(analysis.get("manifest", {}))),
        ("Qualite des donnees", _rows_quality(analysis.get("quality", {}))),
        ("Population", _rows_population(analysis.get("population", {}))),
        ("Remuneration", _rows_salary(analysis.get("salary", {}))),
    ]
    distribution = analysis.get("distribution") or {}
    if distribution.get("available"):
        sheets.append(("Distribution", _rows_distribution(distribution)))
    for segment in analysis.get("segments", []) or []:
        sheets.append((f"Seg {segment['label']}", _rows_segment(segment)))
    if analysis.get("comparison"):
        sheets.append(("Comparaison", _rows_comparison(analysis["comparison"])))
    if config.get("export_parameters.include_individual_data", False):
        sheets.append(
            ("Donnees individuelles", _rows_individual(population, config))
        )
    return sheets


def _rows_manifest(manifest: Dict[str, Any]) -> List[List[Any]]:
    return [
        ["Element", "Valeur"],
        ["Moteur", manifest.get("moteur")],
        ["Version", manifest.get("version")],
        ["Date d'analyse", manifest.get("date_analyse")],
        ["Fichier source", manifest.get("fichier_source")],
        ["Empreinte source (SHA-256)", manifest.get("empreinte_source")],
        ["Effectif analyse", manifest.get("effectif_analyse")],
        ["Filtres", manifest.get("filtres")],
    ]


def export_excel(
    analysis: Dict[str, Any],
    population: Population,
    config: Configuration,
    path: str,
) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    write_workbook(path, build_sheets(analysis, population, config))
    return path


def export_csv(rows: Sequence[Sequence[Any]], path: str, delimiter: str = ";") -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
        writer.writerows(rows)
    return path
