"""Indicateurs d'ecart de remuneration entre les sexes.

Le decoupage suit celui exige des employeurs par la directive europeenne
2023/970 sur la transparence des remunerations :

    a) ecart de remuneration, en moyenne ;
    b) ecart de remuneration, en mediane ;
    c) ecart sur les composantes variables, en moyenne ;
    d) ecart sur les composantes variables, en mediane ;
    e) part des salaries de chaque sexe percevant une composante variable ;
    f) part de chaque sexe dans chaque quartile de remuneration ;
    g) ecart par categorie de salaries exercant un travail de meme valeur.

Convention de signe, la meme partout : un ecart positif signifie que les
femmes sont moins remunerees. La formule est celle de la directive,
(moyenne des hommes - moyenne des femmes) / moyenne des hommes.

Deux precautions tiennent a la nature de la donnee. Les valeurs designant
le sexe sont declarees en configuration et non codees ici — un fichier RH
ecrit « F/H », « F/M » ou « Femme/Homme » selon l'outil qui l'a produit.
Et les seuils de confidentialite s'appliquent categorie par categorie : un
ecart calcule sur une seule femme reviendrait a publier sa remuneration.

Ce module ne decide rien : il calcule. L'interpretation d'un ecart — et sa
justification par des criteres objectifs — n'appartient pas au logiciel.
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence

from . import statistics_engine as stats
from .config import Configuration, analysis_field
from .normalize import Population
from .metrics import PrivacyRules
from .segmentation import dimension_label, split_by

FEMALE = "F"
MALE = "H"


@lru_cache(maxsize=4096)
def _normalise(text: str) -> str:
    """Forme comparable d'une ecriture : sans casse, sans accent, sans espace.

    Le resultat est memorise : un fichier de cent mille salaries ne contient
    qu'une poignee d'ecritures distinctes du sexe, mais la comparaison les
    redecomposait toutes a chaque appel. La decomposition Unicode pesait a
    elle seule trente-huit pour cent du temps d'analyse.
    """
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def _key(value: Any) -> str:
    """Comparaison insensible a la casse, aux accents et aux espaces."""
    return _normalise("" if value is None else str(value).strip())


def classify(value: Any, female: Sequence[str], male: Sequence[str]) -> str:
    """Rend FEMALE, MALE, ou une chaine vide si la valeur n'est pas reconnue.

    Une valeur inconnue n'est jamais rattachee a l'un des deux groupes : la
    ranger arbitrairement fausserait l'ecart sans que rien ne le montre.
    """
    key = _key(value)
    if not key:
        return ""
    # Les ecritures declarees en configuration sont normalisees une fois par
    # jeu, et non a chaque salarie : elles ne changent pas d'un appel a
    # l'autre. Les tuples servent de cle de memorisation.
    # Les ecritures sont converties en texte avant de servir de cle : une
    # configuration ecrite a la main peut contenir n'importe quoi, y compris
    # une liste imbriquee, et une cle non hachable ferait lever la ou la
    # version precedente se contentait de ne pas reconnaitre la valeur.
    if key in _declared(tuple(str(item) for item in female)):
        return FEMALE
    if key in _declared(tuple(str(item) for item in male)):
        return MALE
    return ""


@lru_cache(maxsize=64)
def _declared(values: tuple) -> frozenset:
    """Formes comparables d'une liste d'ecritures declaree en configuration."""
    return frozenset(_key(item) for item in values)


def _gap(male_value: Optional[float], female_value: Optional[float]) -> Optional[float]:
    """Ecart relatif, en pourcentage de la valeur masculine."""
    if male_value is None or female_value is None or not male_value:
        return None
    return (male_value - female_value) / male_value * 100.0


def _split(population: Population, config: Configuration):
    section = config.section("pay_equity_parameters")
    field_name = section.get("gender_field", "gender")
    female = section.get("female_values", []) or []
    male = section.get("male_values", []) or []
    groups: Dict[str, List[Any]] = {FEMALE: [], MALE: [], "": []}
    for employee in population:
        groups[classify(employee.value(field_name), female, male)].append(employee)
    return groups


def _amounts(employees: Sequence[Any], field_name: str) -> List[float]:
    values = []
    for employee in employees:
        value = employee.value(field_name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))
    return values


def _pair(women: List[float], men: List[float],
          rules: PrivacyRules) -> Dict[str, Any]:
    """Moyennes, medianes et ecarts d'un couple de series.

    Rien n'est publie si l'un des deux groupes est sous le seuil : un ecart
    calcule sur une poignee de personnes les designe.
    """
    publishable = (rules.may_publish(len(women)) and rules.may_publish(len(men)))
    if not publishable:
        return {"published": False, "female_count": len(women),
                "male_count": len(men), "mean_gap": None, "median_gap": None,
                "female_mean": None, "male_mean": None,
                "female_median": None, "male_median": None}
    female_mean, male_mean = stats.mean(women), stats.mean(men)
    female_median, male_median = stats.median(women), stats.median(men)
    return {
        "published": True,
        "female_count": len(women), "male_count": len(men),
        "female_mean": female_mean, "male_mean": male_mean,
        "female_median": female_median, "male_median": male_median,
        "mean_gap": _gap(male_mean, female_mean),
        "median_gap": _gap(male_median, female_median),
    }


def _quartiles(population: Population, config: Configuration, field_name: str,
               groups: Dict[str, List[Any]], count: int,
               rules: PrivacyRules) -> List[Dict[str, Any]]:
    """Part de chaque sexe dans chaque quartile de remuneration.

    Les salaries sont ordonnes par remuneration puis decoupes en `count`
    tranches d'effectif egal. Une repartition desequilibree entre le
    quartile bas et le quartile haut est le signal le plus direct d'un
    plafond de verre.
    """
    ranked = sorted(
        (employee for employee in population
         if isinstance(employee.value(field_name), (int, float))),
        key=lambda employee: employee.value(field_name))
    if not ranked or count < 2:
        return []
    female = {id(item) for item in groups[FEMALE]}
    male = {id(item) for item in groups[MALE]}
    total = len(ranked)
    result: List[Dict[str, Any]] = []
    for index in range(count):
        start = total * index // count
        stop = total * (index + 1) // count
        slice_ = ranked[start:stop]
        women = sum(1 for item in slice_ if id(item) in female)
        men = sum(1 for item in slice_ if id(item) in male)
        known = women + men
        result.append({
            "quartile": index + 1,
            "headcount": len(slice_),
            "female_count": women,
            "male_count": men,
            # Les parts ne sont publiees que si le quartile compte assez de
            # monde pour ne designer personne.
            "female_share": (women / known * 100.0
                             if known and rules.may_publish(len(slice_)) else None),
            "male_share": (men / known * 100.0
                           if known and rules.may_publish(len(slice_)) else None),
        })
    return result


def calculate_pay_equity(population: Population,
                         config: Configuration) -> Dict[str, Any]:
    """Tableau complet des ecarts, pret a etre affiche ou exporte."""
    section = config.section("pay_equity_parameters")
    rules = PrivacyRules.from_config(config)
    salary_field = analysis_field(config)
    variable_field = section.get("variable_field", "variable_pay")
    category_field = section.get("category_field", "job_title")
    threshold = float(section.get("gap_alert_threshold", 5.0) or 0.0)

    groups = _split(population, config)
    women, men, unknown = groups[FEMALE], groups[MALE], groups[""]
    result: Dict[str, Any] = {
        "available": False,
        "warning": None,
        "gender_field": section.get("gender_field", "gender"),
        "female_count": len(women),
        "male_count": len(men),
        "unknown_count": len(unknown),
        "headcount": len(population),
        "threshold": threshold,
        "currency": config.get("salary_parameters.currency", "EUR"),
        "category_field": category_field,
        "category_label": dimension_label(config, category_field),
        "categories": [],
        "category_warning": None,
        "quartiles": [],
    }
    if not (rules.may_publish(len(women)) and rules.may_publish(len(men))):
        result["warning"] = (
            "Effectif insuffisant dans l'un des deux groupes pour publier un "
            f"écart (minimum paramétré : {rules.min_publish} "
            "salariés de chaque sexe).")
        return result

    result["available"] = True
    result["pay"] = _pair(_amounts(women, salary_field),
                          _amounts(men, salary_field), rules)
    result["variable"] = _pair(_amounts(women, variable_field),
                               _amounts(men, variable_field), rules)

    # Part de chaque sexe percevant une composante variable.
    def _receiving(employees: Sequence[Any]) -> Optional[float]:
        if not employees:
            return None
        paid = sum(1 for item in employees
                   if isinstance(item.value(variable_field), (int, float))
                   and item.value(variable_field) > 0)
        return paid / len(employees) * 100.0

    result["variable_coverage"] = {
        "female_share": _receiving(women),
        "male_share": _receiving(men),
    }

    result["quartiles"] = _quartiles(
        population, config, salary_field, groups,
        int(section.get("quartile_count", 4) or 4), rules)

    result.update(calculate_category_gaps(population, config, category_field))
    return result


def calculate_category_gaps(population: Population, config: Configuration,
                            field_name: str) -> Dict[str, Any]:
    """Ecarts par categorie, sur l'axe demande.

    Fonction distincte pour que l'axe puisse changer sans tout recalculer :
    « travail de meme valeur » se lit selon le poste, mais aussi selon le
    grade, l'etablissement ou la BU, et l'analyse ne vaut que si l'on peut
    passer de l'un a l'autre.
    """
    section = config.section("pay_equity_parameters")
    rules = PrivacyRules.from_config(config)
    salary_field = analysis_field(config)
    threshold = float(section.get("gap_alert_threshold", 5.0) or 0.0)
    label = dimension_label(config, field_name)

    groups_by_category = split_by(population, field_name)
    if not groups_by_category:
        # Sans ce message, la table resterait vide et laisserait croire a une
        # absence d'ecart, alors que le champ n'existe simplement pas dans
        # le fichier.
        return {
            "category_field": field_name,
            "category_label": label,
            "categories": [],
            "categories_above_threshold": 0,
            "category_warning": (
                f"Le champ « {label} » n'est renseigné pour aucun salarié de "
                "ce fichier : l'écart par catégorie ne peut pas être "
                "calculé."),
        }
    categories: List[Dict[str, Any]] = []
    for name, group in groups_by_category.items():
        members = _split(group, config)
        pair = _pair(_amounts(members[FEMALE], salary_field),
                     _amounts(members[MALE], salary_field), rules)
        pair["category"] = name
        pair["headcount"] = len(group)
        gap = pair.get("mean_gap")
        # Le seuil de la directive porte sur l'ecart absolu : un ecart
        # marque en faveur des hommes comme des femmes appelle un examen.
        pair["above_threshold"] = (gap is not None and threshold > 0
                                   and abs(gap) >= threshold)
        categories.append(pair)
    categories.sort(key=lambda item: (
        item["mean_gap"] is None, -abs(item["mean_gap"] or 0.0)))
    return {
        "category_field": field_name,
        "category_label": label,
        "categories": categories,
        "category_warning": None,
        "categories_above_threshold": sum(
            1 for item in categories if item["above_threshold"]),
    }
