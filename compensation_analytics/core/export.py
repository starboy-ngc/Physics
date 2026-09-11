"""Export des resultats (Excel multi-onglets, CSV).

L'export des donnees individuelles est desactive par defaut
(`export_parameters.include_individual_data`) : il faut une action explicite
de parametrage pour sortir de la donnee nominative.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..io.tabular import Table
from ..io.xlsx_writer import Formula, write_workbook
from . import formulas as fx
from . import segmentation
from .config import Configuration, analysis_field
from .mapping import MappingResult
from .normalize import Population
from .segmentation import UNKNOWN_LABEL


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
    #: Vrai des qu'au moins une categorie a ete ecrite au-dessus. Sans
    #: categorie — un fichier sans colonne de poste —, il n'y a rien a
    #: sommer : ecrire « SUM(J2:J2) » ferait additionner la ligne vide, et
    #: la formule n'aurait aucune valeur en cache a afficher tant que le
    #: tableur ne recalcule pas.
    detailed = total > 4
    rows.append(["Écart global (%)", equity.get("pay", {}).get("mean_gap"),
                 "(moyenne hommes − moyenne femmes) / moyenne hommes"])
    rows.append([f"À {label.lower()} comparable (%)",
                 equity.get("comparable_gap"),
                 "moyenne des écarts, pondérée par l'effectif comparable"])
    rows.append(["Effet de structure (%)", equity.get("structure_gap"),
                 "écart global − écart à catégorie comparable"])
    rows.append(["Rattrapage total",
                 Formula(f"SUM(J2:J{total - 3})", equity.get("at_stake_total"))
                 if detailed else equity.get("at_stake_total"),
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


#: Colonnes de l'onglet des donnees individuelles qui ne viennent d'aucune
#: dimension declaree. Elles sont nommees ici parce que les formules de
#: controle les citent : renommer l'une d'elles sans renommer l'autre
#: casserait le controle, et c'est justement ce qu'on veut interdire.
SOURCE_ROW = "Ligne source"
SEX_COLUMN = "Sexe retenu"
BIRTH_COLUMN = "Date de naissance"
HIRE_COLUMN = "Date d'entrée"
LEAVE_COLUMN = "Date de sortie"
AGE_COLUMN = "Âge"
TENURE_COLUMN = "Ancienneté"

#: Libelles des colonnes de remuneration, par champ du modele.
_MONEY_COLUMNS = (("base_salary", "Salaire de base"),
                  ("variable_pay", "Variable"),
                  ("total_compensation", "Rémunération totale"))


def _sex_label(employee, config: Configuration) -> str:
    """Sexe tel que le moteur l'a retenu, et non tel qu'il est ecrit.

    La directive se calcule sur une classification : « F », « Femme »,
    « female » designent le meme groupe, une ecriture inconnue n'en designe
    aucun. La colonne brute reste dans l'onglet du fichier importe ; celle-ci
    montre ce que le moteur en a fait, ce qui rend la classification
    verifiable au lieu de la laisser implicite.
    """
    from .pay_equity import FEMALE, MALE, classify

    section = config.section("pay_equity_parameters")
    found = classify(employee.value(section.get("gender_field", "gender")),
                     section.get("female_values", []) or [],
                     section.get("male_values", []) or [])
    return {FEMALE: "Femme", MALE: "Homme"}.get(found, "")


def _rows_individual(
    population: Population, config: Configuration,
    derived_as_formulas: bool = True
) -> List[List[Any]]:
    """Donnees individuelles, avec de quoi remonter et de quoi verifier.

    Trois ajouts par rapport a un simple export : le numero de ligne du
    fichier importe, qui permet de revenir a la source de chaque salarie ;
    les dates retenues apres lecture, qui montrent ce que la normalisation a
    compris ; et l'age comme l'anciennete ecrits en formules, qui montrent
    comment elle les a deduites. Les colonnes de dimension portent le
    libelle exact sur lequel le moteur a regroupe — sans quoi un controle
    par « (non renseigne) » ne trouverait rien.

    Les colonnes derivees des dimensions declarees, et non d'une liste
    figee : une dimension ajoutee par configuration se retrouve donc dans
    l'export au lieu d'en disparaitre en silence.
    """
    dimensions = segmentation.dimensions(config)
    reference = population.reference_date
    headers = ([SOURCE_ROW, "Référence"]
               + [entry["label"] for entry in dimensions]
               + [SEX_COLUMN, BIRTH_COLUMN, HIRE_COLUMN, LEAVE_COLUMN,
                  AGE_COLUMN, TENURE_COLUMN]
               + [label for _, label in _MONEY_COLUMNS])
    rows: List[List[Any]] = [headers]
    naissance = fx.column_letter(len(dimensions) + 3)
    entree = fx.column_letter(len(dimensions) + 4)
    sortie = fx.column_letter(len(dimensions) + 5)
    for employee in population:
        ligne = len(rows) + 1
        rows.append(
            [employee.row_number, employee.anonymous_id or employee.employee_id]
            + [_dimension_value(employee, entry["field"])
               for entry in dimensions]
            + [_sex_label(employee, config), employee.birth_date,
               employee.hire_date, employee.leave_date,
               _age_cell(employee, reference, f"{naissance}{ligne}")
               if derived_as_formulas else employee.age_years,
               _tenure_cell(employee, reference, f"{entree}{ligne}",
                            f"{sortie}{ligne}")
               if derived_as_formulas else employee.tenure_years]
            + [employee.value(field) for field, _ in _MONEY_COLUMNS]
        )
    return rows


def _dimension_value(employee, field_name: str) -> Any:
    """Valeur d'une dimension, ecrite comme le decoupage l'a lue."""
    value = employee.value(field_name)
    if isinstance(value, str) or value is None:
        return str(value or "").strip() or UNKNOWN_LABEL
    return value


def _age_cell(employee, reference, cellule: str) -> Any:
    """Age : le nombre de jours ecoules, divise par la duree de l'annee."""
    if not employee.birth_date or reference is None:
        return employee.age_years
    return fx.cell(f"({_date_call(reference)}-{cellule})"
                   f"/{fx.number_literal(fx.DAYS_PER_YEAR)}",
                   employee.age_years)


def _tenure_cell(employee, reference, entree: str, sortie: str) -> Any:
    """Anciennete : jusqu'a la sortie si elle existe, sinon jusqu'a la date
    de reference. La formule porte la regle plutot que son resultat."""
    if not employee.hire_date or reference is None:
        return employee.tenure_years
    fin = f'IF({sortie}="",{_date_call(reference)},{sortie})'
    return fx.cell(f"({fin}-{entree})"
                   f"/{fx.number_literal(fx.DAYS_PER_YEAR)}",
                   employee.tenure_years)


def _date_call(value) -> str:
    return f"DATE({value.year},{value.month},{value.day})"


# ----------------------------------------------------------- fichier source


#: Au-dela, le fichier importe n'est pas recopie dans le classeur : un
#: tableau de plusieurs centaines de milliers de lignes produirait un
#: classeur que le tableur met plusieurs minutes a ouvrir, pour une
#: verification que personne ne fera a la main. Le seuil est un parametre.
SOURCE_MAX_ROWS = 50000

#: Au-dela, le controle par segment n'est plus pose : il tient en formules
#: matricielles qui relisent chacune toute la population, et le produit du
#: nombre de segments par l'effectif finit par se compter en centaines de
#: millions de lectures a chaque ouverture du classeur.
CONTROL_MAX_ROWS = 20000


def _rows_source(table: Table, config: Configuration) -> List[List[Any]]:
    """Le fichier importe, recopie tel qu'il a ete lu.

    C'est le debut de la chaine : sans lui, le classeur demande de croire
    non seulement les calculs, mais aussi la lecture du fichier. Les lignes
    et les colonnes gardent leur place — la ligne 7 de cet onglet est la
    ligne 7 du fichier —, si bien que la colonne « Ligne source » des
    donnees individuelles y renvoie directement.

    Rien n'est reformate : ni les dates, ni les nombres, ni les colonnes que
    le mapping ignore. Une valeur mal lue doit se voir ici telle qu'elle
    etait.
    """
    limite = int(config.get("export_parameters.source_max_rows",
                            SOURCE_MAX_ROWS) or 0)
    rows: List[List[Any]] = [list(table.headers)]
    if limite and table.row_count > limite:
        return [[f"Le fichier importé compte {table.row_count} lignes ; "
                 f"au-delà de {limite}, il n'est pas recopié dans le "
                 "classeur (paramètre export_parameters.source_max_rows). "
                 "Les données individuelles retenues par l'analyse figurent "
                 "dans leur onglet, avec leur numéro de ligne d'origine."]]
    for row in table.rows:
        rows.append(list(row))
    return rows


def _rows_columns(mapping: MappingResult,
                  config: Configuration) -> List[List[Any]]:
    """Ce que le mapping a fait de chaque colonne du fichier.

    Le mapping n'est pas ecrit dans le code : il se declare, et il se
    trompe donc de la meme facon qu'une configuration se trompe. L'onglet
    dit, colonne par colonne, laquelle a ete lue comme quoi — et lesquelles
    ont ete ignorees, ce qui est la moitie de l'information.
    """
    rows: List[List[Any]] = [[
        "Champ du modèle", "Colonne du fichier", "Colonne dans « Fichier "
        "importé »", "Premier alias déclaré",
    ]]
    aliases = (config.get("population_mapping.fields", {}) or {})
    for field_name in sorted(mapping.field_to_index):
        index = mapping.field_to_index[field_name]
        declares = aliases.get(field_name) or []
        rows.append([field_name, mapping.field_to_column.get(field_name, ""),
                     fx.column_letter(index),
                     declares[0] if declares else ""])
    if mapping.unknown_columns:
        rows.append([])
        rows.append(["Colonnes ignorées (aucun alias ne les désigne)"])
        for column in mapping.unknown_columns:
            rows.append([column])
    if mapping.duplicate_columns:
        rows.append([])
        rows.append(["Colonnes en double (la première a été retenue)"])
        for column in mapping.duplicate_columns:
            rows.append([column])
    if mapping.missing_required:
        rows.append([])
        rows.append(["Champs obligatoires absents"])
        for field_name in mapping.missing_required:
            rows.append([field_name])
    return rows


# --------------------------------------------------------------- controles


#: Trois colonnes pour un controle : ce que l'outil a calcule, ce que le
#: tableur retrouve, et l'ecart entre les deux. La quatrieme porte la
#: formule en clair, pour qu'elle se lise sans cliquer.
_CONTROL_HEADERS = ["Indicateur", "Calculé par l'outil",
                    "Recalculé par le tableur", "Écart", "Formule"]


def _control_row(label: str, value: Any, expression: Optional[str],
                 ligne: int, comment: str = "") -> List[Any]:
    """Une ligne de controle : valeur, recalcul, ecart, formule en clair.

    Quand le recalcul n'est pas exprimable — un decoupage par rang, un
    ex aequo departage par l'ordre de lecture —, la colonne du recalcul
    porte l'explication plutot qu'une formule approchante : un controle qui
    signale un ecart la ou l'outil a raison est pire que pas de controle.
    """
    if expression is None:
        return [label, value, "", "", comment]
    return [label, value, fx.cell(expression, _number(value)),
            fx.cell(fx.difference(f"B{ligne}", f"C{ligne}"), 0.0),
            expression]


def _number(value: Any) -> Optional[float]:
    return float(value) if isinstance(value, (int, float)) and not isinstance(
        value, bool) else None


def _rows_control(ledger: fx.Ledger, analysis: Dict[str, Any],
                  config: Configuration) -> List[List[Any]]:
    """Chaque indicateur d'ensemble, refait par le tableur.

    Les indicateurs derives portent deja leur formule sur leur propre
    onglet ; ceux-la ne se deduisent de rien — une mediane se recalcule sur
    les valeurs. L'onglet pose donc, cote a cote, ce que l'outil a calcule
    et ce que le tableur trouve sur les donnees individuelles. Les deux
    colonnes doivent coincider a l'affichage pres, et la colonne « Écart »
    le dit d'un coup d'oeil.
    """
    salaire = _salary_column(analysis, config, ledger)
    rows: List[List[Any]] = [list(_CONTROL_HEADERS)]

    def poser(label: str, value: Any, expression: Optional[str],
              comment: str = "") -> None:
        rows.append(_control_row(label, value, expression, len(rows) + 1,
                                 comment))

    population = analysis.get("population") or {}
    rows.append(["POPULATION"])
    poser("Effectif analysé", population.get("headcount"),
          ledger.rows_matching([]))
    if ledger.has(AGE_COLUMN):
        poser("Âge moyen", population.get("age_mean"),
              ledger.average(AGE_COLUMN))
        poser("Âge médian", population.get("age_median"),
              ledger.median(AGE_COLUMN))
    if ledger.has(TENURE_COLUMN):
        poser("Ancienneté moyenne", population.get("tenure_mean"),
              ledger.average(TENURE_COLUMN))
        poser("Ancienneté médiane", population.get("tenure_median"),
              ledger.median(TENURE_COLUMN))

    for titre, cle, colonne in (("Tranche d'âge", "age_bands", "age_band"),
                                ("Tranche d'ancienneté", "tenure_bands",
                                 "tenure_band")):
        bandes = population.get(cle) or []
        libelle = _dimension_column(config, colonne, ledger)
        if not bandes or libelle is None:
            continue
        rows.append([])
        rows.append([titre.upper()])
        for bande in bandes:
            poser(f'{bande["label"]} — effectif', bande.get("count"),
                  ledger.rows_matching([(libelle, bande["label"])]))
            poser(f'{bande["label"]} — part (%)', bande.get("share"),
                  f'{ledger.rows_matching([(libelle, bande["label"])])}'
                  f"/{ledger.rows_matching([])}*100")

    if ledger.has(AGE_COLUMN) and ledger.has(TENURE_COLUMN):
        rows.append([])
        rows.append(["PARTS REMARQUABLES"])
        for label, key, expression in (
            ("Moins de 30 ans (%)", "share_under_30",
             ledger.share_below(AGE_COLUMN, 30)),
            ("30 à 49 ans (%)", "share_30_to_49",
             ledger.share_between(AGE_COLUMN, 30, 50)),
            ("50 ans et plus (%)", "share_50_plus",
             ledger.share_from(AGE_COLUMN, 50)),
            ("Ancienneté inférieure à 2 ans (%)", "share_tenure_under_2",
             ledger.share_below(TENURE_COLUMN, 2)),
            ("Ancienneté supérieure à 10 ans (%)", "share_tenure_over_10",
             ledger.share_from(TENURE_COLUMN, 10)),
        ):
            poser(label, population.get(key), expression)

    salary = analysis.get("salary") or {}
    if salaire and not salary.get("masked"):
        rows.append([])
        rows.append([f'RÉMUNÉRATION — {salary.get("field_label", "")}'])
        for label, key, expression in (
            ("Effectif valorisé", "valued_headcount", ledger.count(salaire)),
            ("Masse salariale", "payroll", ledger.total(salaire)),
            ("Moyenne", "mean", ledger.average(salaire)),
            ("Médiane", "median", ledger.median(salaire)),
            ("Minimum", "min", ledger.extremum(salaire, False)),
            ("Maximum", "max", ledger.extremum(salaire, True)),
            ("Écart-type (échantillon)", "std_dev", ledger.deviation(salaire)),
        ):
            if key in salary:
                poser(label, salary.get(key), expression)
        for rang in _percentile_ranks(salary):
            cle = f"p{int(rang)}"
            if cle in salary:
                poser(f"P{int(rang)}", salary.get(cle),
                      ledger.percentile(salaire, rang))
        dispersion = salary.get("dispersion") or {}
        for label, key, expression in (
            ("Q3 - Q1", "interquartile_range",
             f"{ledger.percentile(salaire, 75)}-"
             f"{ledger.percentile(salaire, 25)}"),
            ("Q3 / Q1", "q3_over_q1",
             f"{ledger.percentile(salaire, 75)}/"
             f"{ledger.percentile(salaire, 25)}"),
            ("P90 / P10", "p90_over_p10",
             f"{ledger.percentile(salaire, 90)}/"
             f"{ledger.percentile(salaire, 10)}"),
            ("Moyenne / Médiane", "mean_over_median",
             f"{ledger.average(salaire)}/{ledger.median(salaire)}"),
            ("Coefficient de variation", "coefficient_of_variation",
             f"{ledger.deviation(salaire)}/{ledger.average(salaire)}"),
        ):
            if key in dispersion:
                poser(label, dispersion.get(key), expression)

    distribution = analysis.get("distribution") or {}
    if salaire and distribution.get("available"):
        rows.append([])
        rows.append(["DISTRIBUTION"])
        bounds = distribution.get("bounds") or {}
        if bounds:
            ecart = (f"{ledger.percentile(salaire, 75)}-"
                     f"{ledger.percentile(salaire, 25)}")
            facteur = fx.number_literal(
                float(config.get("salary_parameters.outlier_factor", 1.5)))
            poser("Borne basse (Q1 − facteur × (Q3−Q1))", bounds.get("lower"),
                  f"{ledger.percentile(salaire, 25)}-{facteur}*({ecart})")
            poser("Borne haute (Q3 + facteur × (Q3−Q1))", bounds.get("upper"),
                  f"{ledger.percentile(salaire, 75)}+{facteur}*({ecart})")
            poser("Situations atypiques",
                  len(distribution.get("outliers") or []),
                  f'COUNTIFS({ledger.range(salaire)},'
                  f'"<{fx.number_literal(bounds["lower"])}")'
                  f'+COUNTIFS({ledger.range(salaire)},'
                  f'">{fx.number_literal(bounds["upper"])}")')
        bins = distribution.get("bins") or []
        for index, item in enumerate(bins):
            poser(f'Classe {index + 1} — de {item["lower"]:.0f} '
                  f'à {item["upper"]:.0f}', item.get("count"),
                  ledger.bin_count(salaire, item["lower"], item["upper"],
                                   index == len(bins) - 1))

    rows.append([])
    rows.append(["Les percentiles suivent la méthode inclusive (type 7), "
                 "identique à PERCENTILE ; l'écart-type est celui d'un "
                 "échantillon (n−1), identique à STDEV. La colonne « Écart » "
                 "doit valoir zéro partout."])
    return rows


def _percentile_ranks(salary: Dict[str, Any]) -> List[float]:
    """Rangs effectivement presents dans le resultat, dans l'ordre."""
    rangs: List[float] = []
    for key in salary:
        if len(key) > 1 and key[0] == "p" and key[1:].isdigit():
            rangs.append(float(key[1:]))
    return sorted(rangs)


def _salary_column(analysis: Dict[str, Any], config: Configuration,
                   ledger: fx.Ledger) -> Optional[str]:
    """Colonne du classeur qui porte la remuneration analysee.

    Le champ analyse est un parametre : le controle doit pointer la colonne
    que l'analyse a reellement employee, et non le salaire de base par
    habitude.
    """
    champ = (analysis.get("salary") or {}).get("field") or analysis_field(config)
    for field_name, label in _MONEY_COLUMNS:
        if field_name == champ and ledger.has(label):
            return label
    return None


def _dimension_column(config: Configuration, field_name: str,
                      ledger: fx.Ledger) -> Optional[str]:
    """Libelle de colonne d'une dimension, s'il figure dans le classeur."""
    for entry in segmentation.dimensions(config):
        if entry["field"] == field_name and ledger.has(entry["label"]):
            return entry["label"]
    return None


def _rows_control_segments(ledger: fx.Ledger, analysis: Dict[str, Any],
                           config: Configuration) -> List[List[Any]]:
    """Chaque ligne de chaque segment, refaite par le tableur.

    C'est le controle le plus long et le plus utile : un ecart de mediane
    entre deux postes est le chiffre sur lequel une decision se prend. Les
    segments masques n'y figurent pas avec leurs valeurs — un controle qui
    recalculerait un segment que l'outil a refuse de publier le
    publierait.
    """
    salaire = _salary_column(analysis, config, ledger)
    rows: List[List[Any]] = [["Dimension", "Segment", "Indicateur",
                              "Calculé par l'outil",
                              "Recalculé par le tableur", "Écart", "Formule"]]
    if salaire is None:
        return rows
    for segment in analysis.get("segments") or []:
        colonne = _dimension_column(config, segment["field"], ledger)
        if colonne is None:
            continue
        for row in segment["rows"]:
            critere = [(colonne, row["segment"])]
            if row.get("masked"):
                rows.append([segment["label"], row["segment"], "Effectif",
                             row["headcount"],
                             fx.cell(ledger.rows_matching(critere),
                                     float(row["headcount"])),
                             fx.cell(fx.difference(f"D{len(rows) + 1}",
                                                   f"E{len(rows) + 1}"), 0.0),
                             ledger.rows_matching(critere)])
                rows.append([segment["label"], row["segment"],
                             "Indicateurs masqués (effectif sous le seuil de "
                             "publication)"])
                continue
            salary = row["salary"]
            indicateurs: List[Tuple[str, Any, str]] = [
                ("Effectif", row["headcount"], ledger.rows_matching(critere)),
                ("Moyenne", salary.get("mean"),
                 ledger.average(salaire, critere)),
                ("Médiane", salary.get("median"),
                 ledger.median(salaire, critere)),
                ("P10", salary.get("p10"),
                 ledger.percentile(salaire, 10, critere)),
                ("Q1 (P25)", salary.get("p25"),
                 ledger.percentile(salaire, 25, critere)),
                ("Q3 (P75)", salary.get("p75"),
                 ledger.percentile(salaire, 75, critere)),
                ("P90", salary.get("p90"),
                 ledger.percentile(salaire, 90, critere)),
            ]
            if ledger.has(AGE_COLUMN):
                indicateurs.append(("Âge médian", row.get("age_median"),
                                    ledger.median(AGE_COLUMN, critere)))
            if ledger.has(TENURE_COLUMN):
                indicateurs.append(("Ancienneté médiane",
                                    row.get("tenure_median"),
                                    ledger.median(TENURE_COLUMN, critere)))
            for label, value, expression in indicateurs:
                ligne = len(rows) + 1
                rows.append([segment["label"], row["segment"], label, value,
                             fx.cell(expression, _number(value)),
                             fx.cell(fx.difference(f"D{ligne}", f"E{ligne}"),
                                     0.0),
                             expression])
    return rows


def _rows_control_equity(ledger: fx.Ledger, analysis: Dict[str, Any],
                         config: Configuration) -> List[List[Any]]:
    """Les ecarts de la directive, refaits categorie par categorie.

    C'est ici que la verification compte le plus : un ecart publie au titre
    de la directive 2023/970 doit pouvoir se refaire, sur les memes
    salaries et avec la meme definition du sexe — celle que porte la
    colonne « Sexe retenu », et non l'ecriture brute du fichier.
    """
    equity = analysis.get("pay_equity") or {}
    salaire = _salary_column(analysis, config, ledger)
    rows: List[List[Any]] = [["Catégorie", "Indicateur",
                              "Calculé par l'outil",
                              "Recalculé par le tableur", "Écart", "Formule"]]
    if not equity.get("available") or salaire is None \
            or not ledger.has(SEX_COLUMN):
        return rows
    colonne = _dimension_column(config, equity.get("category_field", ""),
                                ledger)

    def poser(categorie: str, label: str, value: Any,
              expression: Optional[str], comment: str = "") -> None:
        ligne = len(rows) + 1
        if expression is None:
            rows.append([categorie, label, value, comment])
            return
        rows.append([categorie, label, value,
                     fx.cell(expression, _number(value)),
                     fx.cell(fx.difference(f"C{ligne}", f"D{ligne}"), 0.0),
                     expression])

    femme, homme = (SEX_COLUMN, "Femme"), (SEX_COLUMN, "Homme")
    ensemble = equity.get("pay") or {}
    poser("Ensemble", "Moyenne femmes", ensemble.get("female_mean"),
          ledger.average(salaire, [femme]))
    poser("Ensemble", "Moyenne hommes", ensemble.get("male_mean"),
          ledger.average(salaire, [homme]))
    poser("Ensemble", "Écart moyen (%)", ensemble.get("mean_gap"),
          f"({ledger.average(salaire, [homme])}"
          f"-{ledger.average(salaire, [femme])})"
          f"/{ledger.average(salaire, [homme])}*100")
    poser("Ensemble", "Médiane femmes", ensemble.get("female_median"),
          ledger.median(salaire, [femme]))
    poser("Ensemble", "Médiane hommes", ensemble.get("male_median"),
          ledger.median(salaire, [homme]))
    poser("Ensemble", "Écart médian (%)", ensemble.get("median_gap"),
          f"({ledger.median(salaire, [homme])}"
          f"-{ledger.median(salaire, [femme])})"
          f"/{ledger.median(salaire, [homme])}*100")

    if colonne is not None:
        for item in equity.get("categories", []) or []:
            nom = item["category"]
            critere_f = [(colonne, nom), femme]
            critere_h = [(colonne, nom), homme]
            poser(nom, "Effectif femmes", item.get("female_count"),
                  ledger.rows_matching(critere_f))
            poser(nom, "Effectif hommes", item.get("male_count"),
                  ledger.rows_matching(critere_h))
            if not item.get("published"):
                poser(nom, "Indicateurs masqués (un sexe sous le seuil de "
                           "publication)", "", None)
                continue
            poser(nom, "Moyenne femmes", item.get("female_mean"),
                  ledger.average(salaire, critere_f))
            poser(nom, "Moyenne hommes", item.get("male_mean"),
                  ledger.average(salaire, critere_h))
            poser(nom, "Médiane femmes", item.get("female_median"),
                  ledger.median(salaire, critere_f))
            poser(nom, "Médiane hommes", item.get("male_median"),
                  ledger.median(salaire, critere_h))
            poser(nom, "Écart moyen (%)", item.get("mean_gap"),
                  f"({ledger.average(salaire, critere_h)}"
                  f"-{ledger.average(salaire, critere_f)})"
                  f"/{ledger.average(salaire, critere_h)}*100")
            poser(nom, "Écart médian (%)", item.get("median_gap"),
                  f"({ledger.median(salaire, critere_h)}"
                  f"-{ledger.median(salaire, critere_f)})"
                  f"/{ledger.median(salaire, critere_h)}*100")
            poser(nom, "Rattrapage", item.get("at_stake"),
                  f"ABS({ledger.average(salaire, critere_h)}"
                  f"-{ledger.average(salaire, critere_f)})"
                  f"*IF({ledger.average(salaire, critere_h)}>"
                  f"{ledger.average(salaire, critere_f)},"
                  f"{ledger.rows_matching(critere_f)},"
                  f"{ledger.rows_matching(critere_h)})")

    rows.append([])
    poser("Ensemble", "À catégorie comparable (%)",
          equity.get("comparable_gap"), None,
          "moyenne des écarts de catégorie, pondérée par leur effectif "
          "comparable ; elle se refait sur l'onglet « Pay Transparency », "
          "colonnes des écarts et des effectifs")
    poser("Ensemble", "Effet de structure (%)", equity.get("structure_gap"),
          None, "écart global − écart à catégorie comparable")
    poser("Ensemble", "Couverture (%)", equity.get("comparable_coverage"),
          None, "part de l'effectif où les deux sexes atteignent le seuil")
    for item in equity.get("quartiles", []) or []:
        poser(f'Quartile {item["quartile"]}', "Part femmes (%)",
              item.get("female_share"), None,
              "le découpage se fait par rang de rémunération, à effectifs "
              "égaux ; les ex æquo y sont départagés par l'ordre de lecture, "
              "ce qu'une formule ne reproduit pas")
    return rows


def build_sheets(
    analysis: Dict[str, Any],
    population: Population,
    config: Configuration,
    table: Optional[Table] = None,
    mapping: Optional[MappingResult] = None,
) -> List[Tuple[str, Sequence[Sequence[Any]]]]:
    """Compose les onglets du classeur d'export.

    Les onglets de resultat viennent d'abord ; le dossier de verification
    vient ensuite, dans l'ordre de la chaine : le fichier importe, ce que le
    mapping en a lu, les salaries retenus, puis les controles qui refont
    chaque chiffre a partir d'eux. On peut donc descendre le classeur de
    gauche a droite comme on remonte un calcul.

    Ce dossier ne parait que si les donnees individuelles sont exportees :
    un controle se fait sur des valeurs, et les valeurs sont nominatives.
    C'est un choix explicite de parametrage, jamais un defaut.
    """
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
    sheets.append(("Formules", _rows_method(analysis, config)))

    if not config.get("export_parameters.include_individual_data", False):
        return sheets

    if table is not None and config.get(
            "export_parameters.include_source_file", False):
        sheets.append(("Fichier importé", _rows_source(table, config)))
        if mapping is not None:
            sheets.append(("Colonnes lues", _rows_columns(mapping, config)))
    limite = int(config.get("export_parameters.control_max_rows",
                            CONTROL_MAX_ROWS) or 0)
    detaille = not limite or len(population) <= limite
    individual = _rows_individual(population, config,
                                  derived_as_formulas=detaille)
    sheets.append(("Données individuelles", individual))
    ledger = fx.Ledger("Données individuelles", individual[0],
                       len(individual) - 1)
    if ledger.empty:
        return sheets
    sheets.append(("Contrôle", _rows_control(ledger, analysis, config)))
    if not detaille:
        # Le controle d'ensemble reste : une centaine de formules sur une
        # colonne, que le tableur refait instantanement. Le controle par
        # segment, lui, poserait un millier de formules matricielles lisant
        # chacune toute la population : le classeur mettrait des minutes a
        # s'ouvrir, et l'outil aurait l'air en panne.
        sheets.append(("Contrôle segments", [
            [f"Le contrôle par segment n'est pas posé au-delà de {limite} "
             "salariés (paramètre export_parameters.control_max_rows) : "
             "chaque formule y relit toute la population, et le tableur "
             "mettrait plusieurs minutes à ouvrir le classeur. Le contrôle "
             "d'ensemble, lui, reste posé dans l'onglet « Contrôle »."]]))
        return sheets
    sheets.append(("Contrôle segments",
                   _rows_control_segments(ledger, analysis, config)))
    equity_rows = _rows_control_equity(ledger, analysis, config)
    if len(equity_rows) > 1:
        sheets.append(("Contrôle Pay Transparency", equity_rows))
    return sheets


def _rows_method(analysis: Dict[str, Any],
                 config: Configuration) -> List[List[Any]]:
    """Toutes les regles de calcul de l'outil, en clair.

    Les onglets de controle prouvent que l'implementation et le tableur
    disent la meme chose ; celui-ci dit ce qu'ils calculent. Les deux sont
    necessaires : une formule juste appliquee a la mauvaise definition
    reste une erreur, et c'est la definition qui se discute en comite.
    """
    rules = config.section("privacy_parameters")
    facteur = config.get("salary_parameters.outlier_factor", 1.5)
    classes = config.get("chart_parameters.histogram_bins", 20)
    reference = (analysis.get("manifest") or {}).get("date_reference", "")
    rows: List[List[Any]] = [["Indicateur", "Règle appliquée",
                              "Écriture dans un tableur", "Où le vérifier"]]
    for indicateur, regle, ecriture, ou in (
        ("Âge",
         "nombre de jours entre la date de naissance et la date de "
         f"référence ({reference}), divisé par {fx.DAYS_PER_YEAR}",
         "(date de référence − date de naissance)/365,2425",
         "Données individuelles, colonne Âge"),
        ("Ancienneté",
         "nombre de jours entre la date d'entrée et la date de sortie si "
         "elle existe, la date de référence sinon",
         "(date de fin − date d'entrée)/365,2425",
         "Données individuelles, colonne Ancienneté"),
        ("Sexe retenu",
         "classification sur les écritures déclarées en configuration ; une "
         "écriture inconnue n'entre dans aucun des deux groupes",
         "—",
         "Données individuelles, colonne Sexe retenu"),
        ("Médiane, percentiles",
         "méthode inclusive dite de type 7, identique à PERCENTILE.INCLUSIVE",
         "PERCENTILE(plage;rang)",
         "Contrôle"),
        ("Écart-type",
         "écart-type d'échantillon (division par n−1)",
         "STDEV(plage)",
         "Contrôle"),
        ("Masse salariale", "somme des rémunérations connues",
         "SUM(plage)", "Contrôle"),
        ("Coefficient de variation", "écart-type rapporté à la moyenne",
         "STDEV(plage)/AVERAGE(plage)", "Rémunération"),
        ("Rapport interdécile", "P90 rapporté à P10",
         "PERCENTILE(plage;0,9)/PERCENTILE(plage;0,1)", "Rémunération"),
        ("Histogramme",
         f"{classes} classes de largeur égale entre le minimum et le "
         "maximum ; chaque classe est fermée à gauche et ouverte à droite, "
         "la dernière exceptée",
         "COUNTIFS(plage;\">=borne basse\";plage;\"<borne haute\")",
         "Contrôle"),
        ("Situation atypique",
         f"valeur hors de [Q1 − {facteur} × (Q3−Q1) ; "
         f"Q3 + {facteur} × (Q3−Q1)]",
         f"Q1-{facteur}*(Q3-Q1) et Q3+{facteur}*(Q3-Q1)",
         "Contrôle"),
        ("Écart de rémunération femmes / hommes",
         "(moyenne hommes − moyenne femmes) / moyenne hommes, en pourcentage "
         "— définition de la directive (UE) 2023/970",
         "(moyenne H − moyenne F)/moyenne H*100",
         "Pay Transparency, Contrôle Pay Transparency"),
        ("Rattrapage",
         "écart de moyenne multiplié par l'effectif du sexe le moins "
         "rémunéré : ce que coûterait l'alignement",
         "ABS(moyenne H − moyenne F)*effectif du sexe le moins rémunéré",
         "Pay Transparency"),
        ("Écart à catégorie comparable",
         "moyenne des écarts de catégorie, pondérée par l'effectif "
         "comparable de chacune ; les catégories dont un sexe est sous le "
         "seuil n'y entrent pas",
         "SOMMEPROD(écarts;effectifs)/SOMME(effectifs)",
         "Pay Transparency"),
        ("Effet de structure",
         "écart global moins écart à catégorie comparable : ce que l'écart "
         "doit à la répartition entre catégories",
         "écart global − écart à catégorie comparable",
         "Pay Transparency"),
        ("Quartiles de rémunération",
         "population ordonnée par rémunération puis découpée en tranches "
         "d'effectif égal ; les ex æquo sont départagés par l'ordre de "
         "lecture, ce qu'une formule ne reproduit pas",
         "—", "Pay Transparency"),
        ("Seuil de publication",
         f'un indicateur n\'est publié qu\'à partir de '
         f'{rules.get("min_headcount_publish", 5)} salariés ; un graphique '
         f'à partir de {rules.get("min_headcount_chart", 10)}',
         "—", "partout, mention « masqué »"),
    ):
        rows.append([indicateur, regle, ecriture, ou])
    return rows


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
    table: Optional[Table] = None,
    mapping: Optional[MappingResult] = None,
) -> str:
    """Ecrit le classeur. Le tableau importe et le mapping sont facultatifs :
    sans eux, le classeur reste celui des resultats ; avec eux, il porte de
    quoi remonter de chaque chiffre jusqu'a la ligne du fichier."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    write_workbook(path, build_sheets(analysis, population, config,
                                      table=table, mapping=mapping))
    return path
