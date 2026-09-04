"""Moteur statistique central. Aucune formule n'est dupliquee ailleurs.

Toutes les fonctions sont robustes aux valeurs manquantes : elles filtrent les
`None` en amont et retournent `None` plutot que de lever une exception quand
l'effectif est insuffisant.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence


def clean(values: Iterable[Optional[float]]) -> List[float]:
    """Ne conserve que les nombres finis exploitables."""
    result: List[float] = []
    for value in values:
        if value is None or isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isnan(number) or math.isinf(number):
            continue
        result.append(number)
    return result


def count(values: Sequence[float]) -> int:
    return len(values)


def total(values: Sequence[float]) -> Optional[float]:
    return float(sum(values)) if values else None


def mean(values: Sequence[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def percentile(values: Sequence[float], rank: float) -> Optional[float]:
    """Percentile par interpolation lineaire (methode inclusive, type 7).

    Identique a PERCENTILE.INCLUSIVE d'Excel et a numpy.percentile par defaut,
    ce qui garantit la coherence avec les controles faits sous Excel par les
    equipes RH.
    """
    if not values:
        return None
    if not 0 <= rank <= 100:
        raise ValueError("le percentile doit etre compris entre 0 et 100")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * (rank / 100.0)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def median(values: Sequence[float]) -> Optional[float]:
    return percentile(values, 50)


def minimum(values: Sequence[float]) -> Optional[float]:
    return min(values) if values else None


def maximum(values: Sequence[float]) -> Optional[float]:
    return max(values) if values else None


def standard_deviation(values: Sequence[float]) -> Optional[float]:
    """Ecart-type d'echantillon. Statistique technique, jamais un KPI principal."""
    if len(values) < 2:
        return None
    average = mean(values) or 0.0
    variance = sum((value - average) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)


def ratio(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def describe(
    values: Sequence[float], percentiles: Sequence[float] = (10, 25, 50, 75, 90)
) -> Dict[str, Optional[float]]:
    """Bloc statistique de reference utilise par tous les ecrans."""
    cleaned = clean(values)
    result: Dict[str, Optional[float]] = {
        "count": count(cleaned),
        "sum": total(cleaned),
        "mean": mean(cleaned),
        "median": median(cleaned),
        "min": minimum(cleaned),
        "max": maximum(cleaned),
        "std_dev": standard_deviation(cleaned),
    }
    for rank in percentiles:
        label = f"p{int(rank)}" if float(rank).is_integer() else f"p{rank}"
        result[label] = percentile(cleaned, float(rank))
    return result


def dispersion(stats: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    """Indicateurs de dispersion attendus par les equipes C&B.

    L'ecart-type reste disponible dans `describe` mais n'apparait pas ici :
    ce ne sont pas des KPI de pilotage.
    """
    q1, q3 = stats.get("p25"), stats.get("p75")
    p10, p90 = stats.get("p10"), stats.get("p90")
    mean_value, median_value = stats.get("mean"), stats.get("median")
    std = stats.get("std_dev")
    interquartile = (q3 - q1) if (q1 is not None and q3 is not None) else None
    return {
        "interquartile_range": interquartile,
        "q3_over_q1": ratio(q3, q1),
        "p90_over_p10": ratio(p90, p10),
        "mean_over_median": ratio(mean_value, median_value),
        "coefficient_of_variation": ratio(std, mean_value),
    }


def histogram(
    values: Sequence[float], bins: int = 20
) -> List[Dict[str, float]]:
    """Repartition en classes de largeur egale."""
    cleaned = clean(values)
    if not cleaned or bins < 1:
        return []
    low, high = min(cleaned), max(cleaned)
    if low == high:
        return [{"lower": low, "upper": high, "count": len(cleaned)}]
    width = (high - low) / bins
    counts = [0] * bins
    for value in cleaned:
        index = int((value - low) / width)
        if index >= bins:
            index = bins - 1
        counts[index] += 1
    return [
        {"lower": low + i * width, "upper": low + (i + 1) * width, "count": counts[i]}
        for i in range(bins)
    ]


def linear_regression(
    xs: Sequence[float], ys: Sequence[float]
) -> Optional[Dict[str, float]]:
    """Droite de tendance et R2. Retourne None si le calcul n'a pas de sens."""
    pairs = [
        (x, y)
        for x, y in zip(xs, ys)
        if x is not None and y is not None
    ]
    if len(pairs) < 3:
        return None
    x_values = [pair[0] for pair in pairs]
    y_values = [pair[1] for pair in pairs]
    x_mean = mean(x_values) or 0.0
    y_mean = mean(y_values) or 0.0
    sxx = sum((x - x_mean) ** 2 for x in x_values)
    if sxx == 0:
        return None
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    syy = sum((y - y_mean) ** 2 for y in y_values)
    r_squared = 0.0 if syy == 0 else (sxy ** 2) / (sxx * syy)
    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "count": len(pairs),
    }


def iqr_outlier_bounds(
    values: Sequence[float], factor: float = 1.5
) -> Optional[Dict[str, float]]:
    """Bornes de detection des points atypiques (methode de Tukey)."""
    cleaned = clean(values)
    if len(cleaned) < 4:
        return None
    q1 = percentile(cleaned, 25)
    q3 = percentile(cleaned, 75)
    if q1 is None or q3 is None:
        return None
    spread = q3 - q1
    return {"lower": q1 - factor * spread, "upper": q3 + factor * spread}
