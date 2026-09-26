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
from .normalize import FTE_FIELD, Population, full_time_amount
from .metrics import PrivacyRules
from .segmentation import cross_key, dimension_label, split_by

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


def _full_time_amounts(employees: Sequence[Any], field_name: str) -> List[float]:
    """Memes montants, ramenes au temps plein. Les ETP inconnus sortent."""
    values = []
    for employee in employees:
        amount = full_time_amount(employee, field_name)
        if amount is not None:
            values.append(amount)
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


def _significance(women: List[float], men: List[float],
                  level: float) -> Dict[str, Any]:
    """Un ecart, et la chance qu'il ne soit qu'un effet du hasard.

    Sans cette mesure, un classement par ampleur met en tete les postes les
    moins peuples : c'est la ou un ecart de vingt pour cent se produit le
    plus facilement sans qu'aucune decision de remuneration ne l'explique.
    Le test est celui de Welch — il ne suppose pas que les deux sexes ont la
    meme dispersion de salaire, ce qui n'a aucune raison d'etre vrai.

    Rien n'est decide ici : un ecart non significatif reste un ecart, et un
    ecart significatif n'est pas pour autant injustifie. La mesure dit
    seulement lequel merite d'etre regarde d'abord.
    """
    comparaison = stats.welch_comparison(men, women)
    probabilite = comparaison.get("p_value")
    return {
        "t": comparaison.get("t"),
        "degrees_of_freedom": comparaison.get("degrees_of_freedom"),
        "p_value": probabilite,
        "level": level,
        "significant": (probabilite is not None and probabilite <= level),
        # La confiance est ce qui se dit a l'oral : « significatif a 95 % ».
        "confidence": (None if probabilite is None
                       else (1.0 - probabilite) * 100.0),
    }


def comparison_amounts(employees: Sequence[Any], field_name: str,
                       full_time: bool) -> List[float]:
    """Les montants a comparer, sur la base retenue pour la page."""
    if full_time:
        return _full_time_amounts(employees, field_name)
    return _amounts(employees, field_name)


def comparison_pair(employees_female: Sequence[Any],
                    employees_male: Sequence[Any], config: Configuration,
                    field_name: str, rules: PrivacyRules,
                    full_time: bool = True) -> Dict[str, Any]:
    """Le couple femmes / hommes sur la base de comparaison de la page.

    A temps de travail egal des que le temps de travail est connu : les
    salaries dont il ne l'est pas sortent du calcul, et la couverture le
    dit. Un ecart etabli sur la moitie d'un poste ne se lit pas comme un
    ecart etabli sur le poste entier.
    """
    femmes = comparison_amounts(employees_female, field_name, full_time)
    hommes = comparison_amounts(employees_male, field_name, full_time)
    bloc = _pair(femmes, hommes, rules)
    verses = (len(_amounts(employees_female, field_name))
              + len(_amounts(employees_male, field_name)))
    bloc["coverage"] = (((len(femmes) + len(hommes)) / verses * 100.0)
                        if verses else None)
    bloc["at_stake"] = _comparable_at_stake(
        bloc, employees_female, employees_male, field_name, full_time)
    niveau = config.number("pay_equity_parameters.significance_level", 0.05,
                           minimum=0.0, maximum=1.0)
    bloc["significance"] = _significance(femmes, hommes, niveau)
    return bloc


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
    threshold = config.number("pay_equity_parameters.gap_alert_threshold",
                              5.0, minimum=0.0, maximum=100.0)

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

    # Le meme ecart, une fois les temps partiels ramenes au temps plein.
    # Il ne remplace pas le precedent : les deux ensemble disent ce que le
    # temps de travail explique de l'ecart, et ce qu'il n'explique pas.
    # Publie seulement si l'ETP est connu pour assez de monde des deux
    # cotes — un ecart a temps plein calcule sur trois femmes n'est pas un
    # ecart a temps plein.
    femmes_etp = _full_time_amounts(women, salary_field)
    hommes_etp = _full_time_amounts(men, salary_field)
    result["full_time"] = _pair(femmes_etp, hommes_etp, rules)
    valorises = len(_amounts(women, salary_field)) + len(_amounts(men, salary_field))
    # Sans arrondi : le moteur rend la valeur, la restitution la formate.
    # Arrondie ici, elle ne coincidait plus avec la formule du classeur de
    # controle, qui affichait alors un ecart de quelques millièmes sur la
    # feuille meme qui sert a prouver qu'il n'y en a pas.
    result["full_time"]["coverage"] = (
        100.0 * (len(femmes_etp) + len(hommes_etp)) / valorises
        if valorises else None)
    result["full_time"]["explained_gap"] = (
        result["pay"]["mean_gap"] - result["full_time"]["mean_gap"]
        if result["pay"].get("mean_gap") is not None
        and result["full_time"].get("mean_gap") is not None else None)
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
        config.number("pay_equity_parameters.quartile_count", 4,
                      minimum=2, maximum=10, integer=True), rules)

    result.update(calculate_category_gaps(population, config, category_field))
    return result


def _axis_label(config: Configuration, field_name) -> str:
    """Intitule d'un axe, simple ou croise."""
    if isinstance(field_name, str):
        return dimension_label(config, field_name)
    return " + ".join(dimension_label(config, name) for name in field_name)


def basis_description(population: Population,
                      config: Configuration) -> Dict[str, Any]:
    """La base de comparaison, dite en clair une fois pour toutes.

    L'egalite professionnelle se compare a temps de travail egal : deux
    personnes au meme poste dont l'une travaille a 80 % ne touchent pas la
    meme somme sans qu'aucune inegalite ne soit en cause. Chaque montant est
    donc ramene au temps plein avant comparaison.

    Encore faut-il que le temps de travail soit connu. Un fichier sans
    colonne de temps de travail ne peut rien ramener a rien : plutot que de
    rendre une page vide — ou, pire, de supposer tout le monde a temps
    plein —, la comparaison porte alors sur les montants verses, et le dit.

    Un ecart n'a de sens qu'avec la mention de ce qu'il compare : l'ecran et
    les documents affichent cette phrase telle quelle, ils ne la
    reconstruisent pas, et ne peuvent donc pas annoncer une base que le
    moteur n'applique pas.
    """
    from .metrics import _field_label

    field_name = analysis_field(config)
    label = _field_label(config, field_name)
    connu = any(full_time_amount(employee, field_name) is not None
                for employee in population)
    return {
        "field": field_name,
        "field_label": label,
        "full_time": connu,
        "label": (f"{label.lower()}, ramené au temps plein" if connu else
                  f"{label.lower()} versé — le temps de travail n'est "
                  "renseigné pour personne, les montants ne peuvent pas être "
                  "ramenés au temps plein"),
    }


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
    threshold = config.number("pay_equity_parameters.gap_alert_threshold",
                              5.0, minimum=0.0, maximum=100.0)
    label = _axis_label(config, field_name)
    base = basis_description(population, config)

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
            "basis": base,
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
        pair["at_stake"] = _at_stake(pair)
        # Le meme couple sur la base de comparaison de la page, et la chance
        # que son ecart ne soit qu'un effet du hasard. Les montants verses
        # melent l'inegalite au temps partiel : l'egalite professionnelle se
        # compare a temps de travail egal.
        comparaison = comparison_pair(members[FEMALE], members[MALE], config,
                                      salary_field, rules,
                                      full_time=base["full_time"])
        ecart_comparable = comparaison.get("mean_gap")
        comparaison["above_threshold"] = (
            ecart_comparable is not None and threshold > 0
            and abs(ecart_comparable) >= threshold)
        pair["comparison"] = comparaison
        categories.append(pair)
    categories.sort(key=lambda item: (
        item["mean_gap"] is None, -abs(item["mean_gap"] or 0.0)))
    result = {
        "category_field": field_name,
        "category_label": label,
        "categories": categories,
        "category_warning": None,
        "basis": base,
        "categories_above_threshold": sum(
            1 for item in categories if item["above_threshold"]),
        "at_stake_total": sum(item["at_stake"] or 0.0 for item in categories),
        # Le meme total sur la base de comparaison de la page : c'est celui
        # qu'un service C&B peut budgeter, parce qu'il ne compte pas un
        # mi-temps comme un temps plein.
        "comparable_at_stake_total": sum(
            (item["comparison"].get("at_stake") or 0.0)
            for item in categories),
    }
    result.update(_decomposition(categories, population, config))
    return result


def category_members(population: Population, field_name,
                     value: str) -> List[Any]:
    """Les salaries d'une categorie, axe simple ou croise."""
    if isinstance(field_name, str):
        return [employee for employee in population
                if str(employee.value(field_name) or "") == str(value)]
    return [employee for employee in population
            if cross_key(employee, field_name) == str(value)]


#: Les trois colonnes de la fiche. L'ordre est celui de la lecture : les
#: deux groupes qu'on compare, puis l'ensemble auquel ils appartiennent.
BREAKDOWN_COLUMNS = (("female", "Femmes"), ("male", "Hommes"),
                     ("all", "Global"))


def category_breakdown(population: Population, config: Configuration,
                       field_name, value: str) -> Dict[str, Any]:
    """Toute la remuneration d'une categorie, en trois colonnes.

    La fiche comparait deux moyennes par variable. Ce qu'on vient chercher
    est plus simple et plus complet : la meme analyse de remuneration que
    pour la population entiere — minimum, moyenne, mediane, quartiles,
    maximum, dispersion — mais posee trois fois, pour les femmes, pour les
    hommes, et pour l'ensemble. La troisieme colonne n'est pas decorative :
    sans elle, on ne sait pas si un ecart tient a un groupe tire vers le
    bas ou l'autre vers le haut.

    Chaque colonne est masquee pour elle-meme. Un poste ou vingt hommes
    cotoient trois femmes publie la colonne des hommes et celle de
    l'ensemble, et tait celle des femmes : c'est la seule qui designerait
    quelqu'un. Le seuil est celui du parametrage, et il vaut ici ce qu'il
    vaut partout.
    """
    from . import metrics as _metrics

    rules = PrivacyRules.from_config(config)
    salary_field = analysis_field(config)
    # La base se decide sur la population entiere, jamais sur la categorie :
    # un poste dont personne n'a de temps de travail renseigne ne doit pas
    # changer en silence la base de comparaison de la page.
    base = basis_description(population, config)
    members = category_members(population, field_name, value)
    groups = _split_members(members, config)
    séries = {"female": groups[FEMALE], "male": groups[MALE],
              "all": members}

    colonnes = []
    montants: Dict[str, List[float]] = {}
    for cle, libelle in BREAKDOWN_COLUMNS:
        gens = séries[cle]
        # Chaque colonne est calculee sur la base de comparaison de la
        # page : des montants ramenes au temps plein, ou un temps partiel
        # compte pour ce qu'il serait a temps complet. Les salaries dont le
        # temps de travail est inconnu sortent du calcul, et la couverture
        # le dit.
        série = comparison_amounts(gens, salary_field, base["full_time"])
        montants[cle] = série
        colonne: Dict[str, Any] = {
            "key": cle, "label": libelle, "headcount": len(gens),
            # Le masquage porte sur les montants exploitables, non sur
            # l'effectif : un poste de vingt personnes dont trois ont un
            # temps de travail connu publierait ces trois-la.
            "masked": not rules.may_publish(len(série)),
        }
        if not colonne["masked"]:
            colonne["salary"] = _metrics.calculate_amount_metrics(
                série, config, salary_field, headcount=len(gens))
        colonnes.append(colonne)

    femmes = next(c for c in colonnes if c["key"] == "female")
    hommes = next(c for c in colonnes if c["key"] == "male")
    publiable = not femmes["masked"] and not hommes["masked"]
    niveau = config.number("pay_equity_parameters.significance_level", 0.05,
                           minimum=0.0, maximum=1.0)
    verses = (len(_amounts(groups[FEMALE], salary_field))
              + len(_amounts(groups[MALE], salary_field)))
    comparables = len(montants["female"]) + len(montants["male"])
    return {
        "category": value,
        "columns": colonnes,
        "published": publiable,
        "headcount": len(members),
        "unknown_count": len(groups[""]),
        "basis": base,
        "coverage": (comparables / verses * 100.0) if verses else None,
        "compared_headcount": comparables,
        "mean_gap": (_gap(hommes["salary"].get("mean"),
                          femmes["salary"].get("mean"))
                     if publiable else None),
        "median_gap": (_gap(hommes["salary"].get("median"),
                            femmes["salary"].get("median"))
                       if publiable else None),
        "significance": (_significance(montants["female"], montants["male"],
                                       niveau) if publiable else None),
        "warning": None if publiable else (
            "Effectif insuffisant dans l'un des deux groupes : l'écart "
            f"n'est pas publié (minimum {rules.min_publish} salariés de "
            "chaque sexe" + (" dont le temps de travail est connu"
                             if base["full_time"] else "") + ")."),
        "threshold": rules.min_publish,
    }


def sexes_of(members: Sequence[Any],
             config: Configuration) -> Dict[int, str]:
    """Le sexe retenu de chaque salarie, par identite d'objet.

    La cle est `id(salarie)` et non le matricule : rien de nominatif ne
    circule, et le rapprochement ne vaut que le temps du calcul.
    """
    groupes = _split_members(list(members), config)
    table: Dict[int, str] = {}
    for sexe in (FEMALE, MALE):
        for salarié in groupes[sexe]:
            table[id(salarié)] = sexe
    return table


def group_positions(population: Population, config: Configuration,
                    field_name, value: str,
                    explain_field: Optional[str] = None) -> Dict[str, Any]:
    """Tous les salaries d'un groupe, situes par rapport a sa mediane.

    Le repere est la mediane du groupe, sur la base de comparaison de la
    page — meme poste, meme etablissement, meme ce que l'utilisateur a mis
    dans son regroupement. Il n'est calcule que si le groupe atteint le
    seuil de publication : une mediane etablie sur trois personnes
    designerait ces trois-la, et situer quelqu'un par rapport a elle
    n'apprendrait rien.

    Aucune identite ne sort d'ici. Chaque ligne porte le numero de ligne du
    fichier et la reference anonyme ; c'est la fenetre qui rapproche, si le
    parametrage l'y autorise, et seulement a l'ecran. Le paragraphe 6 le
    demande : l'identite ne transite pas par le resultat d'analyse.
    """
    rules = PrivacyRules.from_config(config)
    base = basis_description(population, config)
    champ = base["field"]
    membres = category_members(population, field_name, value)
    montants = comparison_amounts(membres, champ, base["full_time"])
    bloc: Dict[str, Any] = {
        "group": str(value), "basis": base, "rows": [],
        "reference": None, "threshold": rules.min_publish,
        "comparable": len(montants), "warning": None,
    }
    if not rules.may_publish(len(montants)):
        bloc["warning"] = (
            f"Ce groupe réunit moins de {rules.min_publish} salariés "
            "comparables : il ne fournit pas de repère, et personne ne peut "
            "y être situé.")
        return bloc
    repère = stats.median(montants)
    if not repère:
        return bloc
    bloc["reference"] = float(repère)
    appartenance = sexes_of(membres, config)
    for salarié in membres:
        montant = (full_time_amount(salarié, champ) if base["full_time"]
                   else salarié.value(champ))
        if not isinstance(montant, (int, float)) or isinstance(montant, bool):
            continue
        écart = (repère - float(montant)) / repère * 100.0
        bloc["rows"].append({
            # Cle de jointure technique — un numero de ligne, jamais un nom.
            # La fenetre retrouve le salarie dans la population qu'elle
            # detient deja.
            "row": salarié.row_number,
            "reference": salarié.anonymous_id or str(salarié.row_number),
            "group": str(value),
            "sex": appartenance.get(id(salarié), ""),
            "amount": float(montant),
            "group_reference": float(repère),
            # « Decrochage » n'est pas « ecart » : seul compte ce qui manque
            # pour rejoindre le repere. Au-dessus, l'ecart est nul.
            "gap": écart if écart > 0 else 0.0,
            "shortfall": (repère - float(montant)) if écart > 0 else 0.0,
            "lagging": écart > 0,
            "fte": salarié.value(FTE_FIELD),
            "explain": (str(salarié.value(explain_field) or "")
                        if explain_field else ""),
        })
    bloc["rows"].sort(key=lambda ligne: ligne["amount"])
    return bloc


def lagging_members(population: Population, config: Configuration,
                    field_name, value: Optional[str] = None,
                    explain_field: Optional[str] = None) -> Dict[str, Any]:
    """Les salaries qui decrochent de leur groupe de comparaison.

    Un ecart de groupe dit qu'il se passe quelque chose ; il ne dit pas a
    qui. Or une revalorisation se decide personne par personne, et la
    premiere question qui suit « ce poste presente un ecart de douze pour
    cent » est « lesquels sont en dessous, et de combien ».

    Sans groupe retenu, la recherche porte sur tous les groupes a la fois :
    c'est la liste par laquelle on commence quand on ne sait pas encore ou
    regarder.
    """
    rules = PrivacyRules.from_config(config)
    base = basis_description(population, config)
    noms = [str(nom) for nom in split_by(population, field_name)]
    if value is not None:
        noms = [nom for nom in noms if nom == str(value)]

    lignes: List[Dict[str, Any]] = []
    retenus = 0
    for nom in noms:
        bloc = group_positions(population, config, field_name, nom,
                               explain_field)
        if bloc["reference"] is None:
            # Le groupe existe, mais il ne peut pas fournir de repere : le
            # dire, plutot que de laisser croire que personne n'y decroche.
            retenus += 1
            continue
        lignes.extend(ligne for ligne in bloc["rows"] if ligne["lagging"])
    lignes.sort(key=lambda ligne: -ligne["gap"])
    return {
        "basis": base,
        "rows": lignes,
        "groups": len(noms),
        "withheld_groups": retenus,
        "explain_field": explain_field,
        "threshold": rules.min_publish,
        "reference_label": "médiane du groupe",
    }


def calculate_category_profile(population: Population, config: Configuration,
                               field_name: str,
                               value: str) -> Dict[str, Any]:
    """Fiche d'une categorie : les deux sexes, sur plusieurs variables.

    Un ecart de remuneration ne se lit pas seul. Vingt pour cent d'ecart sur
    un poste ou les hommes comptent neuf ans d'anciennete et les femmes
    quatre ne dit pas la meme chose que le meme ecart a anciennete egale :
    le premier appelle une revue de la grille d'anciennete, le second une
    revalorisation. La fiche pose donc cote a cote ce que touche chaque sexe
    et ce qui l'entoure — anciennete, age, temps de travail, part variable.

    Les variables comparees sont declarees en configuration : une prime
    propre a l'entreprise s'ajoute a la liste sans toucher au moteur.

    Rien n'est publie si l'un des deux sexes est sous le seuil : une
    mediane calculee sur trois personnes les designe.
    """
    section = config.section("pay_equity_parameters")
    rules = PrivacyRules.from_config(config)
    if isinstance(field_name, str):
        members = [employee for employee in population
                   if str(employee.value(field_name) or "") == str(value)]
    else:
        members = [employee for employee in population
                   if cross_key(employee, field_name) == str(value)]
    groups = _split_members(members, config)
    women, men = groups[FEMALE], groups[MALE]
    published = (rules.may_publish(len(women)) and rules.may_publish(len(men)))
    profile: Dict[str, Any] = {
        "category": value,
        "category_field": field_name,
        "female_count": len(women),
        "male_count": len(men),
        "unknown_count": len(groups[""]),
        "headcount": len(members),
        "published": published,
        "rows": [],
        "variable_share": {},
    }
    if not published:
        profile["warning"] = (
            "Effectif insuffisant : cette catégorie ne réunit pas assez de "
            "femmes et d'hommes pour publier une comparaison.")
        return profile

    for entry in section.get("profile_fields", []) or []:
        name = str(entry.get("field", ""))
        if not name:
            continue
        female = _amounts(women, name)
        male = _amounts(men, name)
        if not female and not male:
            # Une colonne absente du fichier n'a pas a occuper une ligne :
            # elle ferait croire a une donnee manquante plutot qu'a un
            # champ non renseigne.
            continue
        profile["rows"].append(_profile_row(entry, name, female, male))

    # Part de chaque sexe percevant une remuneration variable : indicateur
    # de la directive, et il se lit au niveau du poste comme au global.
    variable_field = section.get("variable_field", "variable_pay")
    profile["variable_share"] = {
        "female_share": _share_with_variable(women, variable_field),
        "male_share": _share_with_variable(men, variable_field),
    }
    salary_field = analysis_field(config)
    pair = _pair(_amounts(women, salary_field), _amounts(men, salary_field),
                 rules)
    profile["at_stake"] = _at_stake(pair)
    profile["mean_gap"] = pair.get("mean_gap")
    profile["median_gap"] = pair.get("median_gap")
    threshold = config.number("pay_equity_parameters.gap_alert_threshold",
                              5.0, minimum=0.0, maximum=100.0)
    profile["above_threshold"] = (profile["mean_gap"] is not None
                                  and threshold > 0
                                  and abs(profile["mean_gap"]) >= threshold)
    return profile


def _profile_row(entry: Dict[str, Any], name: str, female: Sequence[float],
                 male: Sequence[float]) -> Dict[str, Any]:
    """Une variable, les deux sexes, et l'ecart dans l'unite qui convient.

    Un pourcentage sur une anciennete se lirait comme un ecart de
    remuneration : sur les variables qui ne sont pas des montants, l'ecart
    est une difference, dans l'unite de la variable.
    """
    kind = str(entry.get("kind", "money"))
    female_mean, male_mean = stats.mean(female), stats.mean(male)
    row = {
        "field": name,
        "label": str(entry.get("label", name)),
        "kind": kind,
        "female_count": len(female),
        "male_count": len(male),
        "female_mean": female_mean,
        "male_mean": male_mean,
        "female_median": stats.median(female),
        "male_median": stats.median(male),
        "gap": None,
        "difference": None,
    }
    if female_mean is not None and male_mean is not None:
        row["difference"] = female_mean - male_mean
        if kind == "money":
            row["gap"] = _gap(male_mean, female_mean)
    return row


def _share_with_variable(employees: Sequence[Any],
                         field_name: str) -> Optional[float]:
    if not employees:
        return None
    touched = sum(1 for employee in employees
                  if isinstance(employee.value(field_name), (int, float))
                  and not isinstance(employee.value(field_name), bool)
                  and employee.value(field_name) > 0)
    return touched / len(employees) * 100.0


def _split_members(members: Sequence[Any], config: Configuration):
    """Repartit une liste de salaries entre les deux sexes."""
    section = config.section("pay_equity_parameters")
    field_name = section.get("gender_field", "gender")
    female = section.get("female_values", []) or []
    male = section.get("male_values", []) or []
    groups: Dict[str, List[Any]] = {FEMALE: [], MALE: [], "": []}
    for employee in members:
        groups[classify(employee.value(field_name), female, male)].append(
            employee)
    return groups


def _worked_time(employees: Sequence[Any], field_name: str) -> float:
    """Somme des temps de travail des salaries dont le montant est exploitable.

    Deux mi-temps ne coutent pas ce que coutent deux temps pleins : c'est
    cette somme, et non l'effectif, qui convertit un ecart a temps plein en
    euros reellement verses.
    """
    total = 0.0
    for employee in employees:
        if full_time_amount(employee, field_name) is None:
            continue
        ratio = employee.value(FTE_FIELD)
        if isinstance(ratio, (int, float)) and not isinstance(ratio, bool):
            total += float(ratio)
    return total


def _comparable_at_stake(pair: Dict[str, Any],
                         employees_female: Sequence[Any],
                         employees_male: Sequence[Any], field_name: str,
                         full_time: bool) -> Optional[float]:
    """Ce que couterait, en euros verses, la fermeture de l'ecart comparable.

    L'ecart se mesure a temps plein ; le rattrapage se paie au prorata du
    temps travaille. Aligner les montants verses reviendrait a payer un
    mi-temps comme un temps plein — ce n'est pas ce que demande l'egalite,
    et le chiffre serait sans rapport avec la decision a prendre.
    """
    if not pair.get("published"):
        return None
    if not full_time:
        return _at_stake(pair)
    femme, homme = pair.get("female_mean"), pair.get("male_mean")
    if femme is None or homme is None:
        return 0.0
    if homme > femme:
        return (homme - femme) * _worked_time(employees_female, field_name)
    return (femme - homme) * _worked_time(employees_male, field_name)


def _at_stake(pair: Dict[str, Any]) -> Optional[float]:
    """Cout de rattrapage d'une categorie : ce que couterait l'alignement.

    C'est la question que pose un service C&B apres avoir vu un ecart :
    combien pour le refermer. Un ecart de vingt pour cent sur quatre
    personnes ne pese pas ce que pese un ecart de six pour cent sur cent
    vingt, et un classement par ampleur d'ecart seul met les premiers en
    tete. On aligne le sexe le moins remunere sur la moyenne de l'autre.
    """
    if not pair.get("published"):
        return None
    female, male = pair.get("female_mean"), pair.get("male_mean")
    if female is None or male is None:
        return 0.0
    if male > female:
        return (male - female) * pair["female_count"]
    return (female - male) * pair["male_count"]


def _decomposition(categories: Sequence[Dict[str, Any]],
                   population: Population,
                   config: Configuration) -> Dict[str, Any]:
    """Partage l'ecart global entre ce qui tient au poste et au reste.

    Un ecart global melange deux faits que rien ne distingue une fois
    additionnes : des femmes moins payees que des hommes *sur le meme
    poste*, et des femmes plus nombreuses *sur les postes les moins
    payes*. Les deux appellent des reponses opposees — une revalorisation
    individuelle dans un cas, une politique de mobilite dans l'autre — et
    c'est pourquoi la directive fait publier le detail par categorie.

    L'ecart a poste comparable est la moyenne des ecarts de categorie,
    ponderee par l'effectif comparable de chacune. L'effet de structure est
    ce qui reste : un residu, pas une cause demontree.

    Il n'est calcule que sur les categories ou les deux sexes atteignent le
    seuil de publication ; la couverture dit sur quelle part de l'effectif
    il porte, faute de quoi un chiffre calcule sur un dixieme de la
    population passerait pour l'image de l'ensemble.
    """
    salary_field = analysis_field(config)
    groups = _split(population, config)
    overall = _gap(stats.mean(_amounts(groups[MALE], salary_field)),
                   stats.mean(_amounts(groups[FEMALE], salary_field)))
    retained = [item for item in categories
                if item.get("published") and item.get("mean_gap") is not None]
    comparable_headcount = sum(item["female_count"] + item["male_count"]
                               for item in retained)
    total = len(groups[FEMALE]) + len(groups[MALE])
    if not comparable_headcount or overall is None:
        return {"overall_gap": overall, "comparable_gap": None,
                "structure_gap": None, "comparable_headcount": 0,
                "comparable_coverage": None}
    comparable = sum(item["mean_gap"] * (item["female_count"]
                                         + item["male_count"])
                     for item in retained) / comparable_headcount
    return {
        "overall_gap": overall,
        "comparable_gap": comparable,
        "structure_gap": overall - comparable,
        "comparable_headcount": comparable_headcount,
        "comparable_coverage": (comparable_headcount / total * 100.0
                                if total else None),
    }
