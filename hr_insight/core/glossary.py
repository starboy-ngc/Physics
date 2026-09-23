"""Definitions et formules des indicateurs publies.

Un indicateur de remuneration se lit rarement seul : « P90 / P10 » ne dit
rien a qui n'a pas la definition en tete, et une mediane obtenue par
interpolation lineaire ne donne pas toujours le meme chiffre qu'une
mediane calculee autrement. Ces textes accompagnent donc les valeurs
partout ou elles s'affichent.

Ils vivent ici, avec le moteur, et non dans l'interface : la formule
enoncee doit etre celle qui est calculee. Toute modification d'une regle
dans `statistics_engine` doit se retrouver ici, et un test verifie que les
deux ne divergent pas silencieusement.
"""

from __future__ import annotations

from typing import Dict, NamedTuple, Optional

#: Formulation commune des percentiles, pour ne pas la repeter sept fois.
_PERCENTILE_METHOD = ("Interpolation linéaire inclusive (type 7), identique "
                      "à PERCENTILE.INCLUSIVE d'Excel.")


class Entry(NamedTuple):
    """Ce qu'un indicateur mesure, et comment il est obtenu."""

    definition: str
    formula: str


GLOSSARY: Dict[str, Entry] = {
    # ------------------------------------------------------------ population
    "headcount": Entry(
        "Nombre de salariés retenus après application des filtres.",
        "Comptage des lignes conservées."),
    "age_median": Entry(
        "Âge qui partage la population en deux moitiés égales.",
        f"Percentile 50 des âges. {_PERCENTILE_METHOD}"),
    "age_mean": Entry(
        "Âge moyen de la population analysée.",
        "Somme des âges divisée par l'effectif."),
    "tenure_median": Entry(
        "Ancienneté qui partage la population en deux moitiés égales.",
        f"Percentile 50 des anciennetés. {_PERCENTILE_METHOD}"),
    "tenure_mean": Entry(
        "Ancienneté moyenne de la population analysée.",
        "Somme des anciennetés divisée par l'effectif."),
    "age_bands": Entry(
        "Répartition de l'effectif par tranche d'âge, ventilée femmes / "
        "hommes lorsque la colonne du sexe est renseignée. Les deux ailes "
        "partagent la même échelle : leurs longueurs se comparent.",
        "Comptage des salariés par tranche ; la part est rapportée à "
        "l'effectif total. Le découpage des tranches est paramétrable."),
    "tenure_bands": Entry(
        "Répartition de l'effectif par tranche d'ancienneté, ventilée "
        "femmes / hommes lorsque la colonne du sexe est renseignée.",
        "Comptage des salariés par tranche ; la part est rapportée à "
        "l'effectif total. La dernière tranche est prolongée jusqu'à "
        "l'ancienneté maximale observée quand le paramétrage le demande."),

    # --------------------------------------------------------- remuneration
    "payroll": Entry(
        "Somme des rémunérations analysées sur la population filtrée.",
        "Somme du champ d'analyse, salariés sans valeur exclus."),
    "mean": Entry(
        "Rémunération moyenne. Sensible aux valeurs extrêmes : quelques "
        "hautes rémunérations la tirent vers le haut.",
        "Somme des rémunérations divisée par le nombre de salariés valorisés."),
    "median": Entry(
        "Rémunération qui partage la population en deux : la moitié gagne "
        "moins, la moitié gagne plus. Insensible aux valeurs extrêmes.",
        f"Percentile 50. {_PERCENTILE_METHOD}"),
    "min": Entry("Rémunération la plus basse de la population analysée.",
                 "Minimum des valeurs."),
    "max": Entry("Rémunération la plus haute de la population analysée.",
                 "Maximum des valeurs."),
    "p10": Entry("10 % des salariés sont rémunérés en dessous de ce montant.",
                 f"Percentile 10. {_PERCENTILE_METHOD}"),
    "p25": Entry("Premier quartile : 25 % des salariés sont en dessous.",
                 f"Percentile 25. {_PERCENTILE_METHOD}"),
    "p50": Entry("Médiane : la moitié des salariés sont en dessous.",
                 f"Percentile 50. {_PERCENTILE_METHOD}"),
    "p75": Entry("Troisième quartile : 75 % des salariés sont en dessous.",
                 f"Percentile 75. {_PERCENTILE_METHOD}"),
    "p90": Entry("90 % des salariés sont rémunérés en dessous de ce montant.",
                 f"Percentile 90. {_PERCENTILE_METHOD}"),

    "population_summary": Entry(
        "Qui l'on analyse : l'effectif retenu par les filtres, et la façon "
        "dont son âge et son ancienneté se situent.",
        "Médiane et moyenne des âges et des anciennetés de la population "
        "filtrée."),
    "analysis_field": Entry(
        "La colonne du fichier sur laquelle portent tous les montants de "
        "cette page. Changer de champ — salaire de base, rémunération "
        "totale — change tous les chiffres qui suivent.",
        "Champ déclaré au paramétrage (salary_parameters.analysis_field), "
        "vérifié contre les colonnes numériques reconnues."),
    "salary_summary": Entry(
        "Les deux montants qui ne figurent pas dans l'échelle ci-dessous : "
        "ce que pèse la population, et sa moyenne.",
        "Somme et moyenne du champ d'analyse sur les salariés valorisés."),
    "salary_scale": Entry(
        "Les niveaux de rémunération observés, du plus bas au plus haut. La "
        "médiane est mise en avant : c'est elle qui sert de référence de "
        "comparaison, et non la moyenne.",
        "Minimum, percentiles retenus au paramétrage, maximum du champ "
        "analysé."),

    # ------------------------------------------------------------ dispersion
    "dispersion": Entry(
        "Étalement des rémunérations autour du centre. Une même médiane peut "
        "recouvrir une grille resserrée ou très ouverte : ces rapports le "
        "disent.",
        "Rapports établis à partir des percentiles, de la moyenne et de "
        "l'écart-type."),
    "interquartile_range": Entry(
        "Étendue de la moitié centrale des rémunérations, hors extrêmes.",
        "Q3 − Q1."),
    "q3_over_q1": Entry(
        "Rapport interquartile : combien de fois le troisième quartile vaut "
        "le premier. Mesure l'étalement du cœur de la population.",
        "Q3 / Q1."),
    "p90_over_p10": Entry(
        "Rapport inter-décile : écart entre le haut et le bas de la "
        "distribution, extrêmes exclus.",
        "P90 / P10."),
    "mean_over_median": Entry(
        "Asymétrie de la distribution. Au-dessus de 1, quelques hautes "
        "rémunérations tirent la moyenne au-dessus de la médiane.",
        "Moyenne / Médiane."),
    "coefficient_of_variation": Entry(
        "Dispersion relative : elle se compare d'une population à l'autre, "
        "quel que soit le niveau de rémunération.",
        "Écart-type / Moyenne, en pourcentage. Écart-type sur échantillon "
        "(dénominateur n − 1)."),
    "std_dev": Entry(
        "Écart moyen à la moyenne. Statistique technique, sensible aux "
        "valeurs extrêmes.",
        "Racine de la somme des écarts au carré divisée par n − 1."),

    # ------------------------------------------------------- pay transparency
    # Formules de la directive 2023/970. La convention de signe y est
    # unique : un écart positif signifie que les femmes sont moins
    # rémunérées.
    "mean_gap": Entry(
        "Écart de rémunération moyenne entre femmes et hommes, indicateur a) "
        "de la directive 2023/970. Un écart positif signifie que les femmes "
        "sont moins rémunérées.",
        "(Moyenne des hommes − Moyenne des femmes) / Moyenne des hommes, en "
        "pourcentage."),
    "median_gap": Entry(
        "Écart de rémunération médiane, indicateur b) de la directive "
        "2023/970. Moins sensible aux rémunérations extrêmes que l'écart "
        "moyen.",
        "(Médiane des hommes − Médiane des femmes) / Médiane des hommes, en "
        "pourcentage."),
    "variable_mean_gap": Entry(
        "Écart sur les composantes variables — primes, bonus, "
        "intéressement —, indicateur c) de la directive 2023/970.",
        "(Moyenne des hommes − Moyenne des femmes) / Moyenne des hommes sur "
        "le champ variable, en pourcentage."),
    "female_count": Entry(
        "Nombre de femmes dans la population filtrée.",
        "Comptage des salariés dont la valeur du champ « sexe » figure parmi "
        "les écritures déclarées au paramétrage."),
    "male_count": Entry(
        "Nombre d'hommes dans la population filtrée.",
        "Comptage des salariés dont la valeur du champ « sexe » figure parmi "
        "les écritures déclarées au paramétrage."),
}


def describe(key: str) -> Optional[Entry]:
    """Definition et formule d'un indicateur, ou None s'il n'en a pas.

    La mise en forme — gras, ordre, ponctuation — appartient a qui affiche :
    une info-bulle et une note de bas de page n'en font pas le meme usage.
    """
    return GLOSSARY.get(key)
