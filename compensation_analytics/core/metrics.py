"""Indicateurs metier, construits exclusivement sur `statistics_engine`.

Les regles de confidentialite (petits effectifs) sont appliquees ici, au plus
pres du calcul, pour qu'aucun ecran ne puisse les contourner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .config import Configuration, analysis_field, percentiles as configured_percentiles
from .normalize import Employee, Population
from .segmentation import dimension_fields, dimension_label, split_by
from . import statistics_engine as stats

MASKED = None
MASK_REASON = "Effectif insuffisant : resultat masque pour preserver la confidentialite."


@dataclass
class PrivacyRules:
    """Seuils de prudence appliques aux petits effectifs."""

    min_publish: int = 5
    min_warning: int = 10
    min_chart: int = 10

    @classmethod
    def from_config(cls, config: Configuration) -> "PrivacyRules":
        return cls(
            min_publish=int(config.get("privacy_parameters.min_headcount_publish", 5)),
            min_warning=int(config.get("privacy_parameters.min_headcount_warning", 10)),
            min_chart=int(config.get("privacy_parameters.min_headcount_chart", 10)),
        )

    def may_publish(self, headcount: int) -> bool:
        return headcount >= self.min_publish

    def may_chart(self, headcount: int) -> bool:
        return headcount >= self.min_chart

    def warning_for(self, headcount: int) -> Optional[str]:
        if headcount == 0:
            return "Population vide : aucun indicateur ne peut etre calcule."
        if not self.may_publish(headcount):
            return MASK_REASON
        if headcount < self.min_warning:
            return (
                f"Effectif reduit ({headcount} salaries) : les indicateurs sont "
                "a interpreter avec prudence."
            )
        return None


def _values(population: Population, field_name: str) -> List[float]:
    return stats.clean(employee.value(field_name) for employee in population)


def _share(part: int, whole: int) -> Optional[float]:
    return (part / whole * 100.0) if whole else None


def calculate_population_metrics(
    population: Population, config: Configuration
) -> Dict[str, Any]:
    """Effectif, structure d'age et d'anciennete."""
    headcount = len(population)
    rules = PrivacyRules.from_config(config)
    result: Dict[str, Any] = {
        "headcount": headcount,
        "warning": rules.warning_for(headcount),
        "masked": not rules.may_publish(headcount),
    }
    if result["masked"]:
        return result
    result.update(calculate_age_metrics(population, config))
    result.update(calculate_tenure_metrics(population, config))
    result["gender_split"] = _distribution_share(population, "gender", headcount)
    return result


def calculate_age_metrics(
    population: Population, config: Configuration
) -> Dict[str, Any]:
    ages = _values(population, "age_years")
    bands = config.get("age_parameters.bands", [])
    return {
        "age_mean": stats.mean(ages),
        "age_median": stats.median(ages),
        "age_known": len(ages),
        "age_bands": _band_share(population, "age_band", bands, len(population)),
    }


def calculate_tenure_metrics(
    population: Population, config: Configuration
) -> Dict[str, Any]:
    tenures = _values(population, "tenure_years")
    bands = config.get("tenure_parameters.bands", [])
    return {
        "tenure_mean": stats.mean(tenures),
        "tenure_median": stats.median(tenures),
        "tenure_known": len(tenures),
        "tenure_bands": _band_share(population, "tenure_band", bands, len(population)),
    }


def _band_share(
    population: Population,
    field_name: str,
    bands: Sequence[Dict[str, Any]],
    headcount: int,
) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {str(band.get("label", "")): 0 for band in bands}
    unknown = 0
    for employee in population:
        label = str(employee.value(field_name) or "")
        if label in counts:
            counts[label] += 1
        else:
            unknown += 1
    rows = [
        {"label": label, "count": value, "share": _share(value, headcount)}
        for label, value in counts.items()
    ]
    if unknown:
        rows.append(
            {"label": "(non renseigne)", "count": unknown,
             "share": _share(unknown, headcount)}
        )
    return rows


def _distribution_share(
    population: Population, field_name: str, headcount: int
) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for employee in population:
        key = str(employee.value(field_name) or "").strip() or "(non renseigne)"
        counts[key] = counts.get(key, 0) + 1
    return [
        {"label": key, "count": value, "share": _share(value, headcount)}
        for key, value in sorted(counts.items())
    ]


def calculate_salary_metrics(
    population: Population, config: Configuration, field_name: Optional[str] = None
) -> Dict[str, Any]:
    """Masse salariale, moyenne, mediane, percentiles, dispersion."""
    field_name = field_name or analysis_field(config)
    published = configured_percentiles(config)
    # Les ratios de dispersion ont besoin de P10/P25/P75/P90 : on les calcule
    # toujours, meme si l'utilisateur ne publie qu'une partie des percentiles.
    # Sans cela, retirer P25 de la configuration faisait disparaitre Q3/Q1 et
    # P90/P10 de la restitution sans la moindre explication.
    computed = sorted(set(published) | {10.0, 25.0, 50.0, 75.0, 90.0})
    rules = PrivacyRules.from_config(config)

    values = _values(population, field_name)
    headcount = len(population)
    result: Dict[str, Any] = {
        "field": field_name,
        "currency": config.get("salary_parameters.currency", "EUR"),
        "headcount": headcount,
        "valued_headcount": len(values),
        "coverage": _share(len(values), headcount),
        "warning": rules.warning_for(len(values)),
        "masked": not rules.may_publish(len(values)),
    }
    if result["masked"]:
        return result
    described = stats.describe(values, computed)
    result.update(described)
    result["payroll"] = described.get("sum")
    result["dispersion"] = stats.dispersion(described)
    result["published_percentiles"] = [
        {"key": _percentile_key(rank), "label": _percentile_label(rank)}
        for rank in published
    ]
    return result


def _percentile_key(rank: float) -> str:
    return f"p{int(rank)}" if float(rank).is_integer() else f"p{rank}"


def _percentile_label(rank: float) -> str:
    """Libelle usuel : les quartiles sont nommes, les autres numerotes."""
    usual = {25.0: "Q1 (P25)", 50.0: "Mediane (P50)", 75.0: "Q3 (P75)"}
    return usual.get(float(rank), f"P{_percentile_key(rank)[1:]}")


def calculate_distribution_metrics(
    population: Population, config: Configuration, field_name: Optional[str] = None
) -> Dict[str, Any]:
    """Histogramme et points atypiques, sous reserve de l'effectif minimal."""
    field_name = field_name or analysis_field(config)
    rules = PrivacyRules.from_config(config)
    bins = int(config.get("chart_parameters.histogram_bins", 20))
    factor = float(config.get("salary_parameters.outlier_factor", 1.5))

    values = _values(population, field_name)
    if not rules.may_chart(len(values)):
        return {
            "field": field_name,
            "available": False,
            "warning": (
                "Effectif insuffisant pour produire une distribution "
                f"(minimum parametre : {rules.min_chart} salaries)."
            ),
            "bins": [],
            "outliers": [],
        }
    bounds = stats.iqr_outlier_bounds(values, factor)
    outliers: List[Dict[str, Any]] = []
    if bounds:
        for employee in population:
            value = employee.value(field_name)
            if value is None:
                continue
            if value < bounds["lower"] or value > bounds["upper"]:
                outliers.append(
                    _atypical_entry(employee, field_name, value, bounds, config)
                )
    return {
        "field": field_name,
        "available": True,
        "warning": None,
        "dimension_labels": [
            {"field": name, "label": dimension_label(config, name)}
            for name in dimension_fields(config)
        ],
        "bins": stats.histogram(values, bins),
        "bounds": bounds,
        "outliers": sorted(outliers, key=lambda item: item["value"]),
        # Libelle impose : jamais "anomalie RH", qui prejugerait du contexte.
        "outlier_label": "Situation atypique a analyser",
    }


def _atypical_entry(
    employee: Employee,
    field_name: str,
    value: float,
    bounds: Dict[str, float],
    config: Configuration,
) -> Dict[str, Any]:
    return {
        "reference": employee.anonymous_id or str(employee.row_number),
        "row": employee.row_number,
        "value": value,
        "field": field_name,
        "position": "basse" if value < bounds["lower"] else "haute",
        "tenure_years": employee.tenure_years,
        # Dimensions declarees en configuration, pas une liste codee en dur.
        "dimensions": {
            name: employee.value(name) or ""
            for name in dimension_fields(config)
        },
    }


def calculate_segment_metrics(
    population: Population,
    config: Configuration,
    field_name: str,
    salary_field: Optional[str] = None,
) -> Dict[str, Any]:
    """Recalcule les indicateurs de remuneration pour chaque valeur d'un segment."""
    groups = split_by(population, field_name, include_empty=True)
    rules = PrivacyRules.from_config(config)
    rows: List[Dict[str, Any]] = []
    for label, group in groups.items():
        salary = calculate_salary_metrics(group, config, salary_field)
        ages = _values(group, "age_years")
        tenures = _values(group, "tenure_years")
        rows.append({
            "segment": label,
            "headcount": len(group),
            "masked": salary.get("masked", False),
            "salary": salary,
            "age_median": stats.median(ages) if rules.may_publish(len(group)) else None,
            "tenure_median": stats.median(tenures) if rules.may_publish(len(group)) else None,
        })
    rows.sort(key=lambda item: (-item["headcount"], item["segment"]))
    return {
        "field": field_name,
        "label": dimension_label(config, field_name),
        "rows": rows,
        "masked_segments": sum(1 for row in rows if row["masked"]),
    }


def compare_populations(
    left: Population,
    right: Population,
    config: Configuration,
    left_label: str = "Population A",
    right_label: str = "Population B",
) -> Dict[str, Any]:
    """Comparaison terme a terme de deux populations."""
    left_pop = calculate_population_metrics(left, config)
    right_pop = calculate_population_metrics(right, config)
    left_pay = calculate_salary_metrics(left, config)
    right_pay = calculate_salary_metrics(right, config)

    indicators = [
        ("Effectif", left_pop.get("headcount"), right_pop.get("headcount"), "int"),
        ("Age median", left_pop.get("age_median"), right_pop.get("age_median"), "years"),
        ("Anciennete mediane", left_pop.get("tenure_median"),
         right_pop.get("tenure_median"), "years"),
        ("Salaire moyen", left_pay.get("mean"), right_pay.get("mean"), "money"),
        ("Salaire median", left_pay.get("median"), right_pay.get("median"), "money"),
        ("P10", left_pay.get("p10"), right_pay.get("p10"), "money"),
        ("Q1 (P25)", left_pay.get("p25"), right_pay.get("p25"), "money"),
        ("Q3 (P75)", left_pay.get("p75"), right_pay.get("p75"), "money"),
        ("P90", left_pay.get("p90"), right_pay.get("p90"), "money"),
        ("Q3 / Q1", _dispersion_of(left_pay, "q3_over_q1"),
         _dispersion_of(right_pay, "q3_over_q1"), "ratio"),
        ("P90 / P10", _dispersion_of(left_pay, "p90_over_p10"),
         _dispersion_of(right_pay, "p90_over_p10"), "ratio"),
        ("Moyenne / Mediane", _dispersion_of(left_pay, "mean_over_median"),
         _dispersion_of(right_pay, "mean_over_median"), "ratio"),
    ]
    rows = []
    for name, left_value, right_value, kind in indicators:
        gap = None
        gap_pct = None
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            gap = left_value - right_value
            gap_pct = (gap / right_value * 100.0) if right_value else None
        rows.append({
            "indicator": name, "kind": kind,
            "left": left_value, "right": right_value,
            "gap": gap, "gap_percent": gap_pct,
        })
    return {
        "left_label": left_label,
        "right_label": right_label,
        "rows": rows,
        "left_warning": left_pay.get("warning"),
        "right_warning": right_pay.get("warning"),
    }


def _dispersion_of(metrics: Dict[str, Any], key: str) -> Optional[float]:
    return (metrics.get("dispersion") or {}).get(key)


def scatter_dataset(
    population: Population, config: Configuration
) -> Dict[str, Any]:
    """Jeu de points anciennete x remuneration, avec droite de tendance et R2."""
    x_field = config.get("chart_parameters.scatter_x", "tenure_years")
    y_field = config.get("chart_parameters.scatter_y", "base_salary")
    color_field = config.get("chart_parameters.scatter_color_by", "business_unit")
    rules = PrivacyRules.from_config(config)

    points: List[Dict[str, Any]] = []
    for employee in population:
        x_value = employee.value(x_field)
        y_value = employee.value(y_field)
        if x_value is None or y_value is None:
            continue
        points.append({
            "x": float(x_value),
            "y": float(y_value),
            "group": str(employee.value(color_field) or "(non renseigne)"),
            "reference": employee.anonymous_id or str(employee.row_number),
            "grade": employee.grade,
            "job_family": employee.job_family,
        })
    total_points = len(points)
    sampled = False
    max_points = int(config.get("chart_parameters.scatter_max_points", 5000) or 0)
    if max_points and total_points > max_points:
        # Echantillonnage systematique a pas constant : deterministe (donc
        # reproductible et tracable) et sans dependance a un generateur
        # aleatoire. Preserve la forme du nuage au-dela du seuil ou le SVG
        # devient trop lourd pour le navigateur.
        step = total_points / max_points
        points = [points[int(index * step)] for index in range(max_points)]
        sampled = True

    if not rules.may_chart(len(points)):
        return {
            "available": False,
            "warning": (
                "Effectif insuffisant pour afficher le nuage de points "
                f"(minimum parametre : {rules.min_chart} salaries)."
            ),
            "points": [], "trend": None,
            "x_field": x_field, "y_field": y_field, "color_field": color_field,
            "color_label": dimension_label(config, color_field),
        }
    trend = None
    if config.get("chart_parameters.show_trend_line", True):
        trend = stats.linear_regression(
            [point["x"] for point in points], [point["y"] for point in points]
        )
    return {
        "available": True,
        "warning": (
            f"Nuage echantillonne : {len(points)} points affiches sur "
            f"{total_points} salaries. La droite de tendance et le R2 portent "
            "sur l'echantillon affiche."
        ) if sampled else None,
        "sampled": sampled,
        "total_points": total_points,
        "points": points,
        "trend": trend,
        "x_field": x_field,
        "y_field": y_field,
        "color_field": color_field,
        "color_label": dimension_label(config, color_field),
        "groups": sorted({point["group"] for point in points}),
    }
