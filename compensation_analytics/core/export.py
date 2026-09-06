"""Export des resultats (Excel multi-onglets, CSV).

L'export des donnees individuelles est desactive par defaut
(`export_parameters.include_individual_data`) : il faut une action explicite
de parametrage pour sortir de la donnee nominative.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..io.xlsx_writer import Formula, write_workbook
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
    rows.append(["Sévérité", "Code", "Constat", "Lignes concernees"])
    for item in quality.get("constats", []):
        rows.append([item["severite"], item["code"], item["message"],
                     item["lignes_concernees"]])
    return rows


def _rows_population(population: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [["Indicateur", "Valeur"]]
    for label, key in (
        ("Effectif", "headcount"), ("Âge moyen", "age_mean"),
        ("Âge médian", "age_median"), ("Ancienneté moyenne", "tenure_mean"),
        ("Ancienneté médiane", "tenure_median"),
    ):
        rows.append([label, population.get(key)])
    effectif = 1  # ligne de l'effectif total, cite par les parts
    for title, key in (("Tranche d'âge", "age_bands"),
                       ("Tranche d'ancienneté", "tenure_bands")):
        rows.append([])
        rows.append([title, "Effectif", "Part (%)"])
        for band in population.get(key, []) or []:
            ligne = len(rows) + 1
            rows.append([band["label"], band["count"],
                         # La part se verifie d'un coup d'oeil : l'effectif
                         # de la tranche rapporte a celui de la population.
                         Formula(f"B{ligne}/B{effectif + 1}*100",
                                 band["share"])])

    # Parts remarquables du chapitre 11. Leur place est ici, dans le tableur :
    # sur la fiche standard elles repetaient la structure par tranches.
    rows.append([])
    rows.append(["Part remarquable", "Valeur (%)"])
    for label, key in (
        ("Moins de 30 ans", "share_under_30"),
        ("30 à 49 ans", "share_30_to_49"),
        ("50 ans et plus", "share_50_plus"),
        ("Ancienneté inférieure à 2 ans", "share_tenure_under_2"),
        ("Ancienneté supérieure à 10 ans", "share_tenure_over_10"),
    ):
        rows.append([label, population.get(key)])
    return rows


def _rows_salary(salary: Dict[str, Any]) -> List[List[Any]]:
    """Indicateurs de remuneration, les derives portes par leur formule.

    Un classeur d'agregats demande de croire l'outil sur parole. Les cinq
    indicateurs de dispersion se deduisent des percentiles ecrits juste
    au-dessus : ils sont ecrits en formules, qui citent les cellules dont
    ils sortent. On clique, on lit « =B11-B9 », et l'on sait d'ou vient le
    chiffre.
    """
    rows: List[List[Any]] = [["Indicateur", "Valeur"]]
    #: Ligne du tableur ou se trouve chaque cle, pour que les formules
    #: puissent la citer. La ligne 1 porte les en-tetes.
    ligne: Dict[str, int] = {}
    for label, key in (
        ("Effectif valorisé", "valued_headcount"), ("Masse salariale", "payroll"),
        ("Moyenne", "mean"), ("Médiane", "median"), ("Minimum", "min"),
        ("Maximum", "max"), ("P10", "p10"), ("Q1 (P25)", "p25"),
        ("P50", "p50"), ("Q3 (P75)", "p75"), ("P90", "p90"),
        ("Écart-type (technique)", "std_dev"),
    ):
        if key in salary:
            rows.append([label, salary.get(key)])
            ligne[key] = len(rows)
    dispersion = salary.get("dispersion") or {}
    if dispersion:
        rows.append([])
        rows.append(["Dispersion", "Valeur"])
        for label, key, expression in (
            ("Q3 - Q1", "interquartile_range", "B{p75}-B{p25}"),
            ("Q3 / Q1", "q3_over_q1", "B{p75}/B{p25}"),
            ("P90 / P10", "p90_over_p10", "B{p90}/B{p10}"),
            ("Moyenne / Médiane", "mean_over_median", "B{mean}/B{median}"),
            ("Coefficient de variation", "coefficient_of_variation",
             "B{std_dev}/B{mean}"),
        ):
            rows.append([label, _derived(expression, ligne,
                                         dispersion.get(key))])
    return rows


def _derived(expression: str, ligne: Dict[str, int],
             value: Optional[float]) -> Any:
    """Formule citant les cellules dont l'indicateur est tire.

    Si l'une des cellules citees n'a pas ete ecrite — un percentile retire
    de la configuration —, la valeur est ecrite telle quelle : une formule
    qui pointe une case vide afficherait une erreur la ou le chiffre est
    parfaitement connu.
    """
    try:
        return Formula(expression.format(**ligne), value)
    except KeyError:
        return value


def _rows_segment(segment: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [[
        segment["label"], "Effectif", "Moyenne", "Médiane", "P10", "Q1", "Q3",
        "P90", "P90/P10", "Âge médian", "Ancienneté médiane",
    ]]
    for row in segment["rows"]:
        salary = row["salary"]
        if row["masked"]:
            rows.append([row["segment"], row["headcount"]] + ["masqué"] * 9)
            continue
        dispersion = salary.get("dispersion") or {}
        ligne = len(rows) + 1
        rows.append([
            row["segment"], row["headcount"], salary.get("mean"), salary.get("median"),
            salary.get("p10"), salary.get("p25"), salary.get("p75"), salary.get("p90"),
            # P90/P10 se lit sur la ligne meme : la formule cite les deux
            # colonnes voisines plutot que de reciter un resultat.
            Formula(f"H{ligne}/E{ligne}", dispersion.get("p90_over_p10")),
            row.get("age_median"), row.get("tenure_median"),
        ])
    return rows


def _rows_distribution(distribution: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [["Borne basse", "Borne haute", "Effectif"]]
    for item in distribution.get("bins", []) or []:
        rows.append([item["lower"], item["upper"], item["count"]])
    outliers = distribution.get("outliers") or []
    if outliers:
        rows.append([])
        rows.append([distribution.get("outlier_label", "Situation atypique à analyser")])
        rows.append(["Référence", "BU", "Grade", "Famille métier", "Ancienneté",
                     "Valeur", "Position"])
        for item in outliers:
            rows.append([
                item["reference"], item.get("business_unit"), item.get("grade"),
                item.get("job_family"), item.get("tenure_years"), item["value"],
                item["position"],
            ])
    return rows


def _rows_pay_equity(equity: Dict[str, Any]) -> List[List[Any]]:
    """Ecarts femmes / hommes, chaque ecart porte par sa formule.

    C'est la feuille ou la verification compte le plus : un ecart publie au
    titre de la directive 2023/970 doit pouvoir se refaire. Chaque ligne
    porte les deux moyennes, les deux medianes et les effectifs ; l'ecart et
    le rattrapage sont des formules qui les citent.
    """
    label = equity.get("category_label") or "Catégorie"
    rows: List[List[Any]] = [[
        label, "Effectif femmes", "Effectif hommes", "Moyenne femmes",
        "Moyenne hommes", "Médiane femmes", "Médiane hommes",
        "Écart moyen (%)", "Écart médian (%)", "Rattrapage",
    ]]
    for item in sorted(equity.get("categories", []),
                       key=lambda entry: (not entry.get("published"),
                                          -(entry.get("at_stake") or 0.0))):
        if not item.get("published"):
            rows.append([item["category"], item["female_count"],
                         item["male_count"]] + ["masqué"] * 7)
            continue
        n = len(rows) + 1
        rows.append([
            item["category"], item["female_count"], item["male_count"],
            item.get("female_mean"), item.get("male_mean"),
            item.get("female_median"), item.get("male_median"),
            # Formule de la directive : (moyenne H - moyenne F) / moyenne H.
            Formula(f"(E{n}-D{n})/E{n}*100", item.get("mean_gap")),
            Formula(f"(G{n}-F{n})/G{n}*100", item.get("median_gap")),
            # Rattrapage : l'ecart de moyenne, multiplie par l'effectif du
            # sexe le moins remunere.
            Formula(f"ABS(E{n}-D{n})*IF(E{n}>D{n},B{n},C{n})",
                    item.get("at_stake")),
        ])

    rows.append([])
    rows.append(["Ensemble", "Valeur", "Formule"])
    total = len(rows) + 1
    detail = f"J2:J{total - 3}" if total > 4 else "J2:J2"
    rows.append(["Écart global (%)", equity.get("pay", {}).get("mean_gap"),
                 "(moyenne hommes − moyenne femmes) / moyenne hommes"])
    rows.append([f"À {label.lower()} comparable (%)",
                 equity.get("comparable_gap"),
                 "moyenne des écarts, pondérée par l'effectif comparable"])
    rows.append(["Effet de structure (%)", equity.get("structure_gap"),
                 "écart global − écart à catégorie comparable"])
    rows.append(["Rattrapage total",
                 Formula(f"SUM({detail})", equity.get("at_stake_total")),
                 "somme des rattrapages ci-dessus"])
    rows.append(["Couverture (%)", equity.get("comparable_coverage"),
                 "part de l'effectif où les deux sexes atteignent le seuil"])

    rows.append([])
    rows.append(["Quartile", "Effectif", "Part femmes (%)",
                 "Part hommes (%)"])
    for item in equity.get("quartiles", []) or []:
        rows.append([f'Q{item["quartile"]}', item.get("headcount"),
                     item.get("female_share"), item.get("male_share")])
    return rows


def _rows_comparison(comparison: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = [[
        "Indicateur", comparison["left_label"], comparison["right_label"],
        "Écart", "Écart (%)",
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
    headers = (["Référence"]
               + [entry["label"] for entry in dimensions]
               + ["Âge", "Ancienneté", "Salaire de base", "Variable",
                  "Rémunération totale"])
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
        ("Synthèse", _rows_manifest(analysis.get("manifest", {}))),
        ("Qualité des données", _rows_quality(analysis.get("quality", {}))),
        ("Population", _rows_population(analysis.get("population", {}))),
        ("Rémunération", _rows_salary(analysis.get("salary", {}))),
    ]
    distribution = analysis.get("distribution") or {}
    if distribution.get("available"):
        sheets.append(("Distribution", _rows_distribution(distribution)))
    for segment in analysis.get("segments", []) or []:
        sheets.append((f"Seg {segment['label']}", _rows_segment(segment)))
    equity = analysis.get("pay_equity") or {}
    if equity.get("available"):
        sheets.append(("Pay Transparency", _rows_pay_equity(equity)))
    if analysis.get("comparison"):
        sheets.append(("Comparaison", _rows_comparison(analysis["comparison"])))
    if config.get("export_parameters.include_individual_data", False):
        individual = _rows_individual(population, config)
        sheets.append(("Données individuelles", individual))
        # Les indicateurs de base — mediane, percentiles, ecart-type — ne se
        # deduisent d'aucun autre chiffre du classeur : les verifier demande
        # les valeurs. L'onglet ne parait donc que lorsque celles-ci sont
        # exportees, ce qui reste un choix explicite.
        sheets.append(("Contrôle", _rows_control(individual,
                                                 analysis.get("salary", {}))))
    return sheets


def _rows_control(individual: Sequence[Sequence[Any]],
                  salary: Dict[str, Any]) -> List[List[Any]]:
    """Les indicateurs de base, recalcules par le tableur lui-meme.

    Les indicateurs derives portent deja leur formule, mais une mediane ne
    se deduit de rien : elle se recalcule sur les valeurs. Cet onglet pose
    donc, cote a cote, ce que l'outil a calcule et ce que le tableur trouve
    sur la colonne des remunerations de l'onglet « Donnees individuelles ».
    Les deux colonnes doivent coincider a l'affichage pres — c'est la
    verification que l'on ne peut pas faire autrement.

    Les fonctions employees sont les formes historiques (PERCENTILE, STDEV)
    et non leurs variantes recentes : celles-ci exigent dans le fichier un
    prefixe technique que tous les tableurs n'interpretent pas.
    """
    en_tetes = list(individual[0]) if individual else []
    try:
        colonne = _column_letter(en_tetes.index("Salaire de base"))
    except ValueError:
        return [["La colonne des rémunérations est absente de l'export : "
                 "le contrôle ne peut pas être posé."]]
    plage = f"'Données individuelles'!{colonne}2:{colonne}{len(individual)}"
    rows: List[List[Any]] = [[
        "Indicateur", "Calculé par l'outil", "Recalculé par le tableur",
        "Formule",
    ]]
    for label, key, expression in (
        ("Effectif valorisé", "valued_headcount", f"COUNT({plage})"),
        ("Masse salariale", "payroll", f"SUM({plage})"),
        ("Moyenne", "mean", f"AVERAGE({plage})"),
        ("Médiane", "median", f"MEDIAN({plage})"),
        ("Minimum", "min", f"MIN({plage})"),
        ("Maximum", "max", f"MAX({plage})"),
        ("P10", "p10", f"PERCENTILE({plage},0.1)"),
        ("Q1 (P25)", "p25", f"PERCENTILE({plage},0.25)"),
        ("Q3 (P75)", "p75", f"PERCENTILE({plage},0.75)"),
        ("P90", "p90", f"PERCENTILE({plage},0.9)"),
        ("Écart-type", "std_dev", f"STDEV({plage})"),
    ):
        if key not in salary:
            continue
        rows.append([label, salary.get(key),
                     Formula(expression, salary.get(key)), expression])
    rows.append([])
    rows.append(["Les percentiles suivent la méthode inclusive (type 7), "
                 "identique à PERCENTILE d'Excel : les deux colonnes doivent "
                 "coïncider."])
    return rows


def _column_letter(index: int) -> str:
    """Lettre de colonne d'un tableur, a partir de zero."""
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


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
