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
    isfinite = math.isfinite
    for value in values:
        # Chemin rapide : les champs numeriques sont deja des flottants une
        # fois normalises, et c'est le cas de la quasi-totalite des valeurs.
        if type(value) is float:
            if isfinite(value):
                result.append(value)
            continue
        if value is None or isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not isfinite(number):
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
        raise ValueError("le percentile doit être compris entre 0 et 100")
    return _percentile_sorted(sorted(values), rank)


def _percentile_sorted(ordered: Sequence[float], rank: float) -> Optional[float]:
    """Percentile d'une liste deja triee.

    Le tri est le seul cout d'un percentile ; le calcul qui suit est de
    quelques operations. Separer les deux permet a `describe` de trier une
    fois pour les sept indicateurs qu'il rend, la ou il triait sept fois.
    """
    if not ordered:
        return None
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
    # Un seul tri pour tout le bloc. Mediane, minimum, maximum et les cinq
    # percentiles se lisent tous sur la meme liste ordonnee : les calculer
    # separement triait sept fois de suite, ce qui rendait l'analyse
    # sensiblement plus que lineaire — 98 microsecondes par salarie sur
    # 2 000, 166 sur 50 000.
    ordered = sorted(clean(values))
    result: Dict[str, Optional[float]] = {
        "count": len(ordered),
        "sum": total(ordered),
        "mean": mean(ordered),
        "median": _percentile_sorted(ordered, 50.0),
        "min": ordered[0] if ordered else None,
        "max": ordered[-1] if ordered else None,
        "std_dev": standard_deviation(ordered),
    }
    for rank in percentiles:
        if not 0 <= rank <= 100:
            raise ValueError("le percentile doit être compris entre 0 et 100")
        label = f"p{int(rank)}" if float(rank).is_integer() else f"p{rank}"
        result[label] = _percentile_sorted(ordered, float(rank))
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


# --------------------------------------------------------------- comparaison
#
# Un ecart se lit avec sa fiabilite. Trente pour cent d'ecart entre trois
# femmes et quatre hommes peut n'etre qu'un effet du hasard du recrutement ;
# quatre pour cent entre deux cents personnes de chaque sexe n'en est
# probablement pas un. Sans cette mesure, un classement par ampleur met en
# tete les postes les moins peuplés — ceux ou l'ecart est le moins sur.
#
# Le test retenu est celui de Welch : il ne suppose pas que les deux groupes
# ont la meme dispersion, ce qui n'a aucune raison d'etre vrai d'une
# remuneration. La loi de Student est evaluee par la fonction beta
# incomplete, ecrite ici : la bibliotheque standard ne la fournit pas, et
# aucune dependance externe n'est admise.


def _log_beta(a: float, b: float) -> float:
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _beta_fraction(a: float, b: float, x: float) -> float:
    """Fraction continue de la beta incomplete, evaluee par Lentz."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    result = d
    for index in range(1, 301):
        even = 2 * index
        # Termes pairs puis impairs : la fraction alterne les deux.
        for numerator in (
                index * (b - index) * x / ((qam + even) * (a + even)),
                -(a + index) * (qab + index) * x / ((a + even) * (qap + even))):
            d = 1.0 + numerator * d
            if abs(d) < tiny:
                d = tiny
            c = 1.0 + numerator / c
            if abs(c) < tiny:
                c = tiny
            d = 1.0 / d
            result *= d * c
        if abs(d * c - 1.0) < 1e-14:
            break
    return result


def regularised_beta(a: float, b: float, x: float) -> Optional[float]:
    """Beta incomplete regularisee I_x(a, b), pour a, b > 0 et 0 <= x <= 1."""
    if a <= 0 or b <= 0 or not 0.0 <= x <= 1.0:
        return None
    if x in (0.0, 1.0):
        return x
    front = math.exp(math.log(x) * a + math.log1p(-x) * b - _log_beta(a, b))
    # La fraction ne converge vite que du cote ou x est petit devant la
    # moyenne de la loi ; de l'autre, on passe par la symetrie.
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _beta_fraction(a, b, x) / a
    return 1.0 - front * _beta_fraction(b, a, 1.0 - x) / b


def student_two_sided(t: float, degrees_of_freedom: float) -> Optional[float]:
    """Probabilite bilaterale d'un t de Student au moins aussi grand."""
    if degrees_of_freedom <= 0 or not math.isfinite(t):
        return None
    return regularised_beta(degrees_of_freedom / 2.0, 0.5,
                            degrees_of_freedom / (degrees_of_freedom + t * t))


def welch_comparison(left: Sequence[float],
                     right: Sequence[float]) -> Dict[str, Optional[float]]:
    """Compare deux series : difference, t de Welch, probabilite du hasard.

    Rend un dictionnaire dont les valeurs sont `None` des que le test n'a
    pas de sens — moins de deux valeurs d'un cote. Un test impossible se
    dit ; il ne se remplace pas par un chiffre.

    Deux series sans aucune dispersion sont le cas particulier qui compte :
    une grille salariale ou tous les hommes d'un poste touchent le meme
    montant et toutes les femmes un autre. Le t de Welch y est infini, et le
    refus de conclure serait le pire des verdicts — c'est la situation la
    plus nette qui se puisse lire. La probabilite du hasard est alors nulle
    si les deux montants different, totale s'ils sont egaux.
    """
    first, second = clean(left), clean(right)
    empty = {"difference": None, "t": None, "degrees_of_freedom": None,
             "p_value": None}
    if len(first) < 2 or len(second) < 2:
        return empty
    mean_left, mean_right = mean(first), mean(second)
    var_left = (standard_deviation(first) or 0.0) ** 2 / len(first)
    var_right = (standard_deviation(second) or 0.0) ** 2 / len(second)
    spread = var_left + var_right
    if spread <= 0:
        return {"difference": mean_left - mean_right, "t": None,
                "degrees_of_freedom": None,
                "p_value": 0.0 if mean_left != mean_right else 1.0}
    t = (mean_left - mean_right) / math.sqrt(spread)
    degrees = spread ** 2 / (
        var_left ** 2 / (len(first) - 1) + var_right ** 2 / (len(second) - 1))
    return {"difference": mean_left - mean_right, "t": t,
            "degrees_of_freedom": degrees,
            "p_value": student_two_sided(t, degrees)}
