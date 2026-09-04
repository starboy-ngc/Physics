#!/usr/bin/env python3
"""Banc de performance du moteur, sur population fictive.

    python3 tools/benchmark.py --sizes 1000 10000 50000 100000

Mesure separement import, normalisation, controle qualite et calculs, afin
d'identifier le seuil ou l'architecture actuelle devient insuffisante.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import resource
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.core import metrics
from compensation_analytics.core.config import load_configuration
from compensation_analytics.core.mapping import resolve_mapping
from compensation_analytics.core.normalize import normalise_table
from compensation_analytics.core.quality import run_quality_check
from compensation_analytics.core.reporting import render_report
from compensation_analytics.core.segmentation import available_segments
from compensation_analytics.io.tabular import read_table
from compensation_analytics.io.xlsx_writer import write_workbook
from tools.generate_sample_population import HEADERS, build_rows

REFERENCE = _dt.date(2025, 1, 1)


def peak_memory_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return usage / 1024.0 if sys.platform != "darwin" else usage / (1024.0 * 1024.0)


def measure(size: int, directory: str) -> dict:
    source = os.path.join(directory, f"pop_{size}.xlsx")
    rows = build_rows(size, seed=42, reference=REFERENCE, defects=False)
    started = time.perf_counter()
    write_workbook(source, [("Population", [HEADERS] + rows)])
    write_seconds = time.perf_counter() - started
    file_mb = os.path.getsize(source) / (1024 * 1024)

    config = load_configuration()
    timings = {}

    started = time.perf_counter()
    table = read_table(source)
    timings["import"] = time.perf_counter() - started

    mapping = resolve_mapping(table.headers, config)
    started = time.perf_counter()
    population = normalise_table(table.headers, table.rows, mapping, config,
                                 reference_date=REFERENCE)
    timings["normalisation"] = time.perf_counter() - started

    started = time.perf_counter()
    run_quality_check(population, mapping, config)
    timings["qualite"] = time.perf_counter() - started

    started = time.perf_counter()
    payload = {
        "title": "benchmark",
        "quality": {},
        "population": metrics.calculate_population_metrics(population, config),
        "salary": metrics.calculate_salary_metrics(population, config),
        "distribution": metrics.calculate_distribution_metrics(population, config),
        "scatter": metrics.scatter_dataset(population, config),
        "manifest": {},
    }
    payload["segments"] = [
        metrics.calculate_segment_metrics(population, config, field_name)
        for field_name in available_segments(population, config)
    ]
    timings["calculs"] = time.perf_counter() - started

    started = time.perf_counter()
    html = render_report(payload)
    timings["restitution"] = time.perf_counter() - started

    return {
        "effectif": size,
        "fichier_mo": file_mb,
        "ecriture_s": write_seconds,
        "html_mo": len(html.encode("utf-8")) / (1024 * 1024),
        "memoire_mo": peak_memory_mb(),
        **timings,
        "total_s": sum(timings.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+",
                        default=[1000, 10000, 50000, 100000])
    args = parser.parse_args()

    directory = tempfile.mkdtemp()
    header = (f"{'Effectif':>9} {'Import':>8} {'Normal.':>8} {'Qualite':>8} "
              f"{'Calculs':>8} {'Restit.':>8} {'Total':>8} {'HTML Mo':>8} {'RAM Mo':>8}")
    print(header)
    print("-" * len(header))
    for size in args.sizes:
        row = measure(size, directory)
        print(f"{row['effectif']:>9,} {row['import']:>8.2f} "
              f"{row['normalisation']:>8.2f} {row['qualite']:>8.2f} "
              f"{row['calculs']:>8.2f} {row['restitution']:>8.2f} "
              f"{row['total_s']:>8.2f} {row['html_mo']:>8.1f} "
              f"{row['memoire_mo']:>8.0f}".replace(",", " "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
