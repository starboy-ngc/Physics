"""Indicateurs metier, construits exclusivement sur `statistics_engine`.

Les regles de confidentialite (petits effectifs) sont appliquees ici, au plus
pres du calcul, pour qu'aucun ecran ne puisse les contourner.
"""

from __future__ import annotations

import operator
import re

from dataclasses import dataclass, fields as _dataclass_fields
from typing import Any, Dict, List, Optional, Sequence

from .config import Configuration, analysis_field, percentiles as configured_percentiles
from .normalize import Employee, Population
from .segmentation import dimension_fields, dimension_label, split_by
from . import statistics_engine as stats

MASK_REASON = "Effectif insuffisant : résultat masqué pour préserver la confidentialité."


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
            return "Population vide : aucun indicateur ne peut être calculé."
        if not self.may_publish(headcount):
            return MASK_REASON
        if headcount < self.min_warning:
            return (
                f"Effectif réduit ({headcount} salariés) : les indicateurs sont "
                "à interpréter avec prudence."
            )
        return None


#: Champs portes par le modele lui-meme. Un champ declare au mapping mais
#: absent du modele est range dans `extra` ; `assign` n'y met jamais un
#: champ natif, si bien qu'un nom de cette liste se lit toujours en
#: attribut.
_MODEL_FIELDS = frozenset(field.name
                          for field in _dataclass_fields(Employee))


def _values(population: Population, field_name: str) -> List[float]:
    """Valeurs exploitables d'un champ, sur toute la population.

    L'analyse relit chaque champ une fois par dimension : sur 50 000
    salaries, cette fonction porte plusieurs millions de lectures. Un champ
    natif est donc lu par `attrgetter`, deux fois plus rapide qu'un appel de
    methode, et la liste est construite par comprehension plutot que par
    generateur — la boucle reste alors du cote de l'interpreteur.
    """
    if field_name in _MODEL_FIELDS:
        read = operator.attrgetter(field_name)
        return stats.clean([read(employee) for employee in population])
    return stats.clean([employee.value(field_name) for employee in population])


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
    result.update(_key_shares(population))
    return result


def _key_shares(population: Population) -> Dict[str, Any]:
    """Parts remarquables demandees par le cahier des charges.

    Calculees sur les valeurs reelles et non sur les libelles de tranches :
    elles restent justes si l'utilisateur reparametre les tranches.
    """
    ages = _values(population, "age_years")
    tenures = _values(population, "tenure_years")
    return {
        "share_under_30": _share(sum(1 for a in ages if a < 30), len(ages)),
        "share_30_to_49": _share(sum(1 for a in ages if 30 <= a < 50), len(ages)),
        "share_50_plus": _share(sum(1 for a in ages if a >= 50), len(ages)),
        "share_tenure_under_2": _share(sum(1 for t in tenures if t < 2), len(tenures)),
        "share_tenure_over_10": _share(sum(1 for t in tenures if t >= 10), len(tenures)),
    }


def calculate_age_metrics(
    population: Population, config: Configuration
) -> Dict[str, Any]:
    ages = _values(population, "age_years")
    bands = population.age_bands or config.get("age_parameters.bands", [])
    return {
        "age_mean": stats.mean(ages),
        "age_median": stats.median(ages),
        "age_known": len(ages),
        "age_bands": _band_share(population, "age_band", bands,
                                 len(population), config),
    }


def calculate_tenure_metrics(
    population: Population, config: Configuration
) -> Dict[str, Any]:
    tenures = _values(population, "tenure_years")
    bands = population.tenure_bands or config.get("tenure_parameters.bands", [])
    return {
        "tenure_mean": stats.mean(tenures),
        "tenure_median": stats.median(tenures),
        "tenure_known": len(tenures),
        "tenure_bands": _band_share(population, "tenure_band", bands,
                                    len(population), config),
    }


def _sex_of(employee, config: Optional[Configuration]) -> str:
    """« female », « male » ou « unknown », selon les ecritures declarees."""
    if config is None:
        return "unknown"
    from .pay_equity import FEMALE, classify

    section = config.section("pay_equity_parameters")
    value = employee.value(section.get("gender_field", "gender"))
    found = classify(value, section.get("female_values", []) or [],
                     section.get("male_values", []) or [])
    if not found:
        return "unknown"
    return "female" if found == FEMALE else "male"


def _band_share(
    population: Population,
    field_name: str,
    bands: Sequence[Dict[str, Any]],
    headcount: int,
    config: Optional[Configuration] = None,
) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {str(band.get("label", "")): 0 for band in bands}
    # Ventilation par sexe : c'est elle qui fait une pyramide plutot qu'un
    # simple histogramme. Elle reste vide si la colonne n'est pas renseignee.
    split: Dict[str, Dict[str, int]] = {
        label: {"female": 0, "male": 0, "unknown": 0} for label in counts
    }
    unknown = 0
    for employee in population:
        label = str(employee.value(field_name) or "")
        if label in counts:
            counts[label] += 1
            split[label][_sex_of(employee, config)] += 1
        else:
            unknown += 1
    rows = [
        {"label": label, "count": value, "share": _share(value, headcount),
         "female": split[label]["female"], "male": split[label]["male"],
         "unknown_sex": split[label]["unknown"]}
        for label, value in counts.items()
    ]
    if unknown:
        rows.append(
            {"label": "(non renseigne)", "count": unknown,
             "share": _share(unknown, headcount),
             "female": 0, "male": 0, "unknown_sex": unknown}
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
        "field_label": _field_label(config, field_name),
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


def _field_label(config: Configuration, field_name: str) -> str:
    """Libelle metier d'un champ : le premier alias declare au mapping.

    Un ecran RH ne doit jamais afficher "base_salary" mais "Salaire de base".
    """
    aliases = (config.get("population_mapping.fields", {}) or {}).get(field_name)
    return aliases[0] if aliases else field_name


def _percentile_key(rank: float) -> str:
    return f"p{int(rank)}" if float(rank).is_integer() else f"p{rank}"


def _percentile_label(rank: float) -> str:
    """Libelle usuel : les quartiles sont nommes, les autres numerotes."""
    usual = {25.0: "Q1 (P25)", 50.0: "Médiane (P50)", 75.0: "Q3 (P75)"}
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
                f"(minimum paramètre : {rules.min_chart} salariés)."
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
    ordered_outliers = sorted(outliers, key=lambda item: item["value"])
    return {
        "field": field_name,
        "available": True,
        "warning": None,
        "dimension_labels": _discriminating_dimensions(population, config),
        "bins": stats.histogram(values, bins),
        "bounds": bounds,
        # La liste complete porte le comptage annonce ; seule la selection
        # mise en avant est tronquee, sinon la restitution annoncerait moins
        # de situations qu'il n'y en a.
        "outliers": ordered_outliers,
        "outliers_highlighted": _extremes(ordered_outliers),
        # Libelle impose : jamais "anomalie RH", qui prejugerait du contexte.
        "outlier_label": "Situation atypique à analyser",
    }


def _discriminating_dimensions(
    population: Population, config: Configuration
) -> List[Dict[str, str]]:
    """Dimensions qui varient reellement dans la population analysee.

    Sous un filtre "BU = France", les colonnes BU et Pays sont constantes :
    les afficher gaspille la place sans rien apprendre.
    """
    useful: List[Dict[str, str]] = []
    for name in dimension_fields(config):
        values = {str(employee.value(name) or "") for employee in population}
        values.discard("")
        if len(values) > 1:
            useful.append({"field": name, "label": dimension_label(config, name)})
    return useful


def _extremes(ordered: List[Dict[str, Any]], per_side: int = 8) -> List[Dict[str, Any]]:
    """Selection mise en avant : les cas les plus bas et les plus hauts.

    Tronquer la liste triee ne montrerait que les remunerations basses et
    masquerait completement les hautes — ou l'inverse.
    """
    if len(ordered) <= 2 * per_side:
        return ordered
    return ordered[:per_side] + ordered[-per_side:]


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


def segment_by_sex(population: Population, config: Configuration,
                   field_name: str,
                   salary_field: Optional[str] = None) -> List[Dict[str, Any]]:
    """Chaque segment coupe en deux : ce que touchent les femmes, les hommes.

    Une boite a moustaches par segment dit comment la remuneration s'etale ;
    elle ne dit pas si les deux sexes s'y etalent pareil. Or c'est la que la
    question se pose vraiment : deux medianes proches peuvent recouvrir deux
    distributions tres differentes, et un ecart de mediane nul n'exclut pas
    que les femmes soient absentes du haut de la fourchette.

    Chaque demi-segment porte son propre droit au trace : un segment de
    cinquante personnes dont quatre femmes ne donne pas le droit de dessiner
    les percentiles de ces quatre-la.
    """
    rules = PrivacyRules.from_config(config)
    groups = split_by(population, field_name, include_empty=True)
    rows: List[Dict[str, Any]] = []
    for label, group in groups.items():
        parts = {"female": [], "male": []}
        for employee in group:
            sex = _sex_of(employee, config)
            if sex in parts:
                parts[sex].append(employee)
        entry: Dict[str, Any] = {"segment": label, "headcount": len(group)}
        for sex, members in parts.items():
            subset = Population(employees=members,
                                age_bands=population.age_bands,
                                tenure_bands=population.tenure_bands)
            entry[sex] = calculate_salary_metrics(subset, config, salary_field)
            entry[f"{sex}_count"] = len(members)
            entry[f"{sex}_chartable"] = rules.may_chart(len(members))
        # Le segment entier est fourni aussi : le graphique s'en sert pour
        # l'echelle et pour le tri, et la ligne reste comparable a celle du
        # mode simple.
        overall = calculate_salary_metrics(group, config, salary_field)
        entry["salary"] = overall
        entry["masked"] = overall.get("masked", False)
        entry["chartable"] = rules.may_chart(len(group))
        entry["sex_chartable"] = (entry["female_chartable"]
                                  or entry["male_chartable"])
        # L'ecart est ce qu'on vient chercher en dedoublant : il se calcule
        # ici, du meme cote que tout le reste, et non dans la vue. Un
        # graphique qui ferait sa propre soustraction finirait par annoncer
        # un chiffre que le document contredit. Formule de la directive
        # 2023/970 : (hommes - femmes) / hommes.
        entry["median_gap"] = _sex_gap(entry, "median")
        entry["mean_gap"] = _sex_gap(entry, "mean")
        rows.append(entry)
    return rows


def _sex_gap(entry: Dict[str, Any], key: str) -> Optional[float]:
    """Ecart relatif entre les deux sexes, ou rien.

    Rien, et non zero, des qu'un des deux cotes est retenu par le seuil de
    publication : un ecart de zero se lirait « pas de difference », quand la
    verite est « on n'a pas le droit de le dire ».
    """
    femmes = (entry.get("female") or {}).get(key)
    hommes = (entry.get("male") or {}).get(key)
    if femmes is None or hommes is None or not hommes:
        return None
    return (hommes - femmes) / hommes * 100.0


def calculate_segment_metrics(
    population: Population,
    config: Configuration,
    field_name: str,
    salary_field: Optional[str] = None,
) -> Dict[str, Any]:
    """Recalcule les indicateurs de remuneration pour chaque valeur d'un segment."""
    groups = split_by(population, field_name, include_empty=True)
    rules = PrivacyRules.from_config(config)
    # Mediane de l'ensemble analyse : c'est a elle que chaque segment se
    # compare. Une mediane de segment prise isolement ne dit pas si le
    # segment est au-dessus ou au-dessous, ce qui est pourtant la question.
    reference = calculate_salary_metrics(population, config, salary_field)
    reference_median = None if reference.get("masked") else reference.get("median")
    total = len(population)
    rows: List[Dict[str, Any]] = []
    for label, group in groups.items():
        salary = calculate_salary_metrics(group, config, salary_field)
        ages = _values(group, "age_years")
        tenures = _values(group, "tenure_years")
        published = rules.may_publish(len(group))
        median = None if salary.get("masked") else salary.get("median")
        rows.append({
            "segment": label,
            "headcount": len(group),
            "share": (len(group) / total * 100.0) if total else None,
            "masked": salary.get("masked", False),
            "salary": salary,
            # Ecart relatif a la mediane de reference, en points de
            # pourcentage. Nul quand l'un des deux termes est masque : on ne
            # publie pas un ecart calcule sur un chiffre qu'on a refuse de
            # montrer.
            "median_gap": (
                (median - reference_median) / reference_median * 100.0
                if median is not None and reference_median else None
            ),
            "age_median": stats.median(ages) if published else None,
            "tenure_median": stats.median(tenures) if published else None,
            # Publier et tracer ne demandent pas le meme effectif. Une boite
            # a moustaches dessine P10 et P90 : sur cinq salaries, ce sont
            # deux remunerations individuelles pointees a l'ecran. Le seuil
            # graphique, plus haut, decide donc separement.
            "chartable": rules.may_chart(len(group)),
        })
    rows.sort(key=_segment_sort_key(field_name, config,
                                    [r["segment"] for r in rows], population))
    return {
        "field": field_name,
        "label": dimension_label(config, field_name),
        "rows": rows,
        "reference_median": reference_median,
        "currency": reference.get("currency", "EUR"),
        "masked_segments": sum(1 for row in rows if row["masked"]),
    }


_ORDINAL_LABEL = re.compile(r"^([^\d]*)(\d+)([^\d]*)$")


def _segment_sort_key(field_name: str, config: Configuration,
                      labels: List[str], population: Population):
    """Ordre de presentation d'un segment.

    Une echelle se lit dans son ordre, pas par effectif : trier les grades
    G1..G8 par population rend illisible la progression salariale. Trois cas :

    * tranches d'age et d'anciennete -> l'ordre declare en configuration ;
    * libelles ordinaux (G1..G8, N1..N5) -> l'ordre numerique ;
    * tout le reste (BU, metier, statut) -> effectif decroissant.
    """
    # Les tranches posees sur la population priment sur celles declarees :
    # la derniere tranche ouverte a pu etre prolongee, et l'ordre doit
    # suivre le decoupage reellement affiche.
    bands = {
        "age_band": population.age_bands or config.get("age_parameters.bands", []),
        "tenure_band": (population.tenure_bands
                        or config.get("tenure_parameters.bands", [])),
    }.get(field_name)
    if bands:
        order = {str(band.get("label", "")): index for index, band in enumerate(bands)}
        return lambda item: (order.get(item["segment"], len(order)), item["segment"])

    matches = [_ORDINAL_LABEL.match(label) for label in labels if label]
    if matches and all(matches) and len({m.group(1) for m in matches}) == 1:
        def ordinal(item):
            match = _ORDINAL_LABEL.match(item["segment"])
            return (0, int(match.group(2))) if match else (1, 0)
        return ordinal

    return lambda item: (-item["headcount"], item["segment"])


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
        ("Âge médian", left_pop.get("age_median"), right_pop.get("age_median"), "years"),
        ("Ancienneté médiane", left_pop.get("tenure_median"),
         right_pop.get("tenure_median"), "years"),
        ("Salaire moyen", left_pay.get("mean"), right_pay.get("mean"), "money"),
        ("Salaire médian", left_pay.get("median"), right_pay.get("median"), "money"),
        ("P10", left_pay.get("p10"), right_pay.get("p10"), "money"),
        ("Q1 (P25)", left_pay.get("p25"), right_pay.get("p25"), "money"),
        ("Q3 (P75)", left_pay.get("p75"), right_pay.get("p75"), "money"),
        ("P90", left_pay.get("p90"), right_pay.get("p90"), "money"),
        ("Q3 / Q1", _dispersion_of(left_pay, "q3_over_q1"),
         _dispersion_of(right_pay, "q3_over_q1"), "ratio"),
        ("P90 / P10", _dispersion_of(left_pay, "p90_over_p10"),
         _dispersion_of(right_pay, "p90_over_p10"), "ratio"),
        ("Moyenne / Médiane", _dispersion_of(left_pay, "mean_over_median"),
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


#: Au-dela, les modalites les moins nombreuses sont regroupees. La serie
#: categorielle compte dix couleurs (« palette.SERIES_COUNT ») : neuf
#: modalites nommees et un regroupement en gris les occupent exactement.
DEFAULT_MAX_GROUPS = 9


def _collapse_groups(points: List[Dict[str, Any]], max_groups: int):
    """Classe les modalites par effectif et regroupe la queue.

    Colorier par « Poste » demandait trente-huit couleurs a une serie qui
    en compte dix : la dixieme modalite reprenait la couleur de la
    premiere, et deux postes sans rapport devenaient indiscernables. La
    legende, elle, disparaissait purement et simplement au-dela de seize
    entrees — le nuage restait colore, mais plus rien ne disait de quoi.

    Le remede n'est pas d'interdire les dimensions nombreuses : « Poste »
    est precisement celle qu'on veut regarder. Ce sont les modalites les
    plus nombreuses qui portent une couleur ; les autres, prises ensemble,
    en portent une seule, neutre. Aucun point ne disparait, et le nuage ne
    ment plus sur ce qu'il montre.

    Rend la liste des modalites — effectif decroissant, regroupement en
    dernier —, le nom du regroupement, et l'effectif de chacune.
    """
    counts: Dict[str, int] = {}
    for point in points:
        counts[point["group"]] = counts.get(point["group"], 0) + 1
    # A effectif egal, l'ordre alphabetique : deux analyses du meme fichier
    # doivent rendre les memes couleurs.
    classees = sorted(counts, key=lambda name: (-counts[name], name))
    if not max_groups or len(classees) <= max_groups:
        return classees, None, counts

    gardees = classees[:max_groups]
    regroupees = set(classees[max_groups:])
    other = f"Autres ({len(regroupees)} valeurs)"
    while other in counts:
        # Une modalite du fichier porte deja ce nom : le regroupement doit
        # rester distinct d'elle, sinon il l'absorbe en silence.
        other += " "
    for point in points:
        if point["group"] in regroupees:
            # L'identite de la modalite n'est pas perdue : elle reste
            # lisible au survol du point, seule la couleur est mise en
            # commun.
            point["group_label"] = point["group"]
            point["group"] = other
    # Le regroupement passe devant : quatre cents points gris traces apres
    # les autres les recouvriraient, et c'est justement sur les modalites
    # nommees que le regard doit pouvoir se poser. Le tri est stable, donc
    # l'ordre des points d'une meme modalite ne change pas.
    points.sort(key=lambda point: 0 if point["group"] == other else 1)
    retenus = {name: counts[name] for name in gardees}
    retenus[other] = sum(counts[name] for name in regroupees)
    return gardees + [other], other, retenus


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
            # Cle de jointure technique — un numero de ligne, jamais un nom.
            # Elle permet a l'ecran de retrouver le salarie dans la
            # population qu'il detient, sans qu'aucune identite ne transite
            # par le resultat d'analyse.
            "row": employee.row_number,
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

    groups, other_label, group_counts = _collapse_groups(
        points, int(config.get("chart_parameters.scatter_max_groups",
                       DEFAULT_MAX_GROUPS) or 0))

    if not rules.may_chart(len(points)):
        return {
            "available": False,
            "warning": (
                "Effectif insuffisant pour afficher le nuage de points "
                f"(minimum paramètre : {rules.min_chart} salariés)."
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
            f"Nuage échantillonné : {len(points)} points affichés sur "
            f"{total_points} salariés. La droite de tendance et le R2 portent "
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
        "groups": groups,
        # Nom du regroupement, ou None si toutes les modalites tiennent.
        # Les quatre supports s'en servent pour lui donner un neutre.
        "other_label": other_label,
        "group_counts": group_counts,
    }
