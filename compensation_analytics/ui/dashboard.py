"""Page composee par l'utilisateur : blocs choisis, ordonnes, enregistres.

Les onglets de l'outil repondent chacun a une question que nous avons
choisie. Celui-ci ne choisit rien : il expose tout ce que l'analyse produit
— indicateurs, tableaux, graphiques — et laisse composer la page dont on a
besoin, une fois pour toutes.

Le catalogue vit ici, dans l'interface, et non dans le moteur : un « bloc »
est une facon d'afficher, pas une facon de calculer. Ce qui est enregistre
en configuration se reduit donc a des identifiants et a un ordre — jamais a
des chiffres, jamais a des donnees RH.

Un identifiant inconnu, dans une configuration ecrite a la main ou heritee
d'une version anterieure, est ignore avec une trace au journal technique :
la page s'ouvre amputee plutot que pas du tout.
"""

from __future__ import annotations

from typing import Any, Dict, List, NamedTuple, Optional, Sequence

from ..core.logging_setup import log_event


class Block(NamedTuple):
    """Un element composable.

    `kind` dit comment le rendre : « indicator » lit une valeur du resultat,
    « table » et « chart » instancient un affichage. `source` designe la
    section du resultat, `key` la valeur ou le trace, et `needs_field` dit si
    le bloc reclame une dimension — la dispersion se lit par metier ou par
    grade, et ce choix appartient a l'utilisateur.
    """

    ident: str
    label: str
    family: str
    kind: str
    source: str = ""
    key: str = ""
    needs_field: bool = False


#: Familles, dans l'ordre ou elles sont proposees.
FAMILIES = ("Population", "Rémunération", "Dispersion", "Pay Transparency",
            "Graphiques")


def _indicator(ident: str, label: str, family: str, source: str,
               key: str) -> Block:
    return Block(ident, label, family, "indicator", source, key)


CATALOGUE: Dict[str, Block] = {block.ident: block for block in (
    # ----------------------------------------------------------- population
    _indicator("headcount", "Effectif", "Population", "population",
               "headcount"),
    _indicator("age_median", "Âge médian", "Population", "population",
               "age_median"),
    _indicator("age_mean", "Âge moyen", "Population", "population",
               "age_mean"),
    _indicator("tenure_median", "Ancienneté médiane", "Population",
               "population", "tenure_median"),
    _indicator("tenure_mean", "Ancienneté moyenne", "Population",
               "population", "tenure_mean"),

    # -------------------------------------------------------- remuneration
    _indicator("payroll", "Masse salariale", "Rémunération", "salary",
               "payroll"),
    _indicator("mean", "Salaire moyen", "Rémunération", "salary", "mean"),
    _indicator("median", "Salaire médian", "Rémunération", "salary",
               "median"),
    _indicator("min", "Rémunération minimale", "Rémunération", "salary",
               "min"),
    _indicator("max", "Rémunération maximale", "Rémunération", "salary",
               "max"),
    _indicator("p10", "P10", "Rémunération", "salary", "p10"),
    _indicator("p25", "Q1 (P25)", "Rémunération", "salary", "p25"),
    _indicator("p75", "Q3 (P75)", "Rémunération", "salary", "p75"),
    _indicator("p90", "P90", "Rémunération", "salary", "p90"),

    # ----------------------------------------------------------- dispersion
    _indicator("interquartile_range", "Q3 − Q1", "Dispersion", "dispersion",
               "interquartile_range"),
    _indicator("q3_over_q1", "Q3 / Q1", "Dispersion", "dispersion",
               "q3_over_q1"),
    _indicator("p90_over_p10", "P90 / P10", "Dispersion", "dispersion",
               "p90_over_p10"),
    _indicator("mean_over_median", "Moyenne / Médiane", "Dispersion",
               "dispersion", "mean_over_median"),
    _indicator("coefficient_of_variation", "Coefficient de variation",
               "Dispersion", "dispersion", "coefficient_of_variation"),

    # ------------------------------------------------------ pay transparency
    _indicator("mean_gap", "Écart moyen H/F", "Pay Transparency", "pay",
               "mean_gap"),
    _indicator("median_gap", "Écart médian H/F", "Pay Transparency", "pay",
               "median_gap"),
    _indicator("female_count", "Effectif femmes", "Pay Transparency",
               "pay_equity", "female_count"),
    _indicator("male_count", "Effectif hommes", "Pay Transparency",
               "pay_equity", "male_count"),

    # ------------------------------------------------------------ tableaux
    Block("salary_scale", "Échelle de rémunération", "Rémunération", "table",
          key="salary_scale"),
    Block("dispersion_table", "Tableau de dispersion", "Dispersion", "table",
          key="dispersion"),

    # ----------------------------------------------------------- graphiques
    Block("age_pyramid", "Pyramide des âges", "Graphiques", "chart",
          key="age_pyramid"),
    Block("tenure_pyramid", "Structure d'ancienneté", "Graphiques", "chart",
          key="tenure_pyramid"),
    Block("histogram", "Distribution des rémunérations", "Graphiques",
          "chart", key="histogram"),
    Block("scatter", "Rémunération / Ancienneté", "Graphiques", "chart",
          key="scatter"),
    Block("boxes", "Dispersion par segment", "Graphiques", "chart",
          key="boxes", needs_field=True),
    Block("quartiles", "Répartition H/F par quartile", "Graphiques", "chart",
          key="quartiles"),
    Block("gaps", "Écarts H/F par catégorie", "Graphiques", "chart",
          key="gaps", needs_field=True),
)}


def families() -> List[tuple]:
    """Blocs groupes par famille, dans l'ordre d'affichage."""
    grouped = []
    for family in FAMILIES:
        blocks = [block for block in CATALOGUE.values()
                  if block.family == family]
        if blocks:
            grouped.append((family, blocks))
    return grouped


def load(config) -> List[Dict[str, Any]]:
    """Composition enregistree, debarrassee de ce qui n'existe plus.

    Une configuration se modifie au bloc-notes et survit aux versions : un
    identifiant inconnu ne doit pas empecher la page de s'ouvrir.
    """
    saved = config.get("dashboard_parameters.blocks", []) or []
    kept: List[Dict[str, Any]] = []
    unknown: List[str] = []
    for entry in saved:
        if not isinstance(entry, dict):
            continue
        ident = str(entry.get("block", ""))
        if ident not in CATALOGUE:
            unknown.append(ident)
            continue
        kept.append({"block": ident, "field": entry.get("field") or ""})
    if unknown:
        log_event("interface", "dashboard_load", status="INCONNU",
                  detail=f"blocs ignores={len(unknown)}")
    return kept


def dump(blocks: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Section a enregistrer : des identifiants et un ordre, rien d'autre."""
    return {"blocks": [
        {"block": entry["block"],
         **({"field": entry["field"]} if entry.get("field") else {})}
        for entry in blocks if entry.get("block") in CATALOGUE
    ]}
