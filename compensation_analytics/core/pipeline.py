"""Orchestration du pipeline complet.

IMPORT -> CONTROLE -> NORMALISATION -> PARAMETRAGE -> MOTEUR -> ANALYSE
-> VISUALISATION -> RESTITUTION -> EXPORT

Aucune etape ne contient de formule : elles delegent toutes aux modules
specialises, ce qui permet d'ajouter une analyse (egalite salariale,
compa-ratio, N/N-1) sans toucher au coeur.
"""

from __future__ import annotations

import datetime as _dt
import os
import time as _time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from ..io.tabular import Table, read_table
from . import metrics
from .config import Configuration, load_configuration
from .errors import DataQualityError
from . import palette
from .logging_setup import log_event
from .mapping import MappingResult, ensure_required, resolve_mapping
from .normalize import Population, normalise_table
from .pay_equity import calculate_pay_equity
from .quality import QualityReport, run_quality_check
from .segmentation import (Filter, apply_filters, available_segments,
                           describe_filters, validate_segments)
from .traceability import build_manifest


@dataclass
class AnalysisRequest:
    """Parametres d'une execution d'analyse."""

    source_path: str
    sheet: Optional[str] = None
    config_dir: Optional[str] = None
    filters: List[Filter] = field(default_factory=list)
    segments: List[str] = field(default_factory=list)
    comparison_filters: List[Filter] = field(default_factory=list)
    comparison_label: str = "Population B"
    reference_date: Optional[_dt.date] = None
    title: str = "Analyse de rémunération"
    ignore_quality_errors: bool = False


@dataclass
class AnalysisResult:
    """Resultat complet, consommable par la restitution et l'export."""

    population: Population
    filtered: Population
    quality: QualityReport
    mapping: MappingResult
    config: Configuration
    payload: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return self.payload


def load_population(
    source_path: str,
    config: Configuration,
    sheet: Optional[str] = None,
    reference_date: Optional[_dt.date] = None,
) -> tuple[Population, MappingResult, Table]:
    """IMPORT + MAPPING + NORMALISATION."""
    started = _time.perf_counter()
    table = read_table(source_path, sheet)
    log_event("import", "read_table", duration=_time.perf_counter() - started,
              detail=f"rows={table.row_count}")

    mapping = resolve_mapping(table.headers, config)
    ensure_required(mapping, config)
    log_event(
        "mapping", "resolve",
        detail=f"mapped={len(mapping.field_to_index)};unknown={len(mapping.unknown_columns)}",
    )

    started = _time.perf_counter()
    population = normalise_table(
        table.headers, table.rows, mapping, config,
        source_name=table.source_name, reference_date=reference_date,
    )
    log_event("normalize", "normalise_table",
              duration=_time.perf_counter() - started,
              detail=f"employees={len(population)}")
    return population, mapping, table


def run_analysis(request: AnalysisRequest) -> AnalysisResult:
    """Execute le pipeline de bout en bout et retourne le resultat structure."""
    config = load_configuration(request.config_dir)
    population, mapping, _table = load_population(
        request.source_path, config, request.sheet, request.reference_date
    )

    quality = run_quality_check(population, mapping, config)
    log_event(
        "quality", "run_check", status=quality.status,
        detail=(f"critical={quality.critical_count};warnings={quality.warning_count}"),
    )
    if quality.blocking and not request.ignore_quality_errors:
        raise DataQualityError(
            "Le contrôle qualité a détecté des anomalies critiques. "
            "Corrigez le fichier source, ou relancez l'analyse en acceptant "
            "explicitement de poursuivre malgré ces anomalies.\n\n"
            + quality.to_text(),
            technical=f"blocking quality findings: {quality.critical_count}",
        )

    filtered = apply_filters(population, request.filters)
    log_event("segmentation", "apply_filters",
              detail=f"in={len(population)};out={len(filtered)}")

    started = _time.perf_counter()
    payload: Dict[str, Any] = {
        "title": request.title,
        # Le theme suit l'analyse : les documents se colorent sans avoir a
        # relire la configuration, et un resultat rejoue garde ses couleurs.
        "theme": palette.resolve(config).theme,
        "quality": quality.as_dict(),
        "population": metrics.calculate_population_metrics(filtered, config),
        "salary": metrics.calculate_salary_metrics(filtered, config),
        "distribution": metrics.calculate_distribution_metrics(filtered, config),
        "scatter": metrics.scatter_dataset(filtered, config),
        "pay_equity": calculate_pay_equity(filtered, config),
    }
    # Le perimetre voyage avec le resultat. Sans lui, une page de chiffres
    # ne dit pas sur qui elle porte : « 412 salaries » se lit tout autrement
    # selon qu'il s'agit de tout le fichier ou d'un filtre. L'effectif n'y
    # figure pas — il est deja au manifeste et en tete de la page.
    payload["scope"] = {
        "filtered": bool(request.filters),
        "description": describe_filters(request.filters, config),
    }
    segment_fields = (validate_segments(request.segments, config)
                      or available_segments(filtered, config))
    payload["segments"] = [
        metrics.calculate_segment_metrics(filtered, config, field_name)
        for field_name in segment_fields
    ]
    if request.comparison_filters:
        other = apply_filters(population, request.comparison_filters)
        payload["comparison"] = metrics.compare_populations(
            filtered, other, config,
            left_label=describe_filters(request.filters, config) or "Population A",
            right_label=request.comparison_label,
        )

    log_event("metrics", "compute", duration=_time.perf_counter() - started,
              detail=f"segments={len(payload['segments'])}")

    payload["manifest"] = build_manifest(
        source_path=request.source_path,
        config=config,
        filters_description=describe_filters(request.filters, config),
        headcount=len(filtered),
        extra={"segments_analyses": segment_fields},
    )
    log_event("pipeline", "run_analysis", detail=f"headcount={len(filtered)}")
    return AnalysisResult(
        population=population, filtered=filtered, quality=quality,
        mapping=mapping, config=config, payload=payload,
    )
