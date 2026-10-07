"""Restitutions au format paysage 16:9.

Deux sorties, construites sur les memes donnees que le rapport detaille :

* `synthese`  — une page unique, pour un comite ou une note de cadrage ;
* `complete`  — un jeu de slides, une idee par page.

Le decoupage produit ici est neutre : il decrit *ce que contient* chaque page,
pas *comment* elle est peinte. Le rendu HTML et le rendu PDF consomment donc
la meme liste de slides, ce qui garantit que les deux formats disent la meme
chose.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .axes import nice_ticks
from . import palette
from . import reporting
from .segmentation import UNKNOWN_LABEL
from ..io import restrict_to_owner
from .reporting import (boxplot_svg, donut_svg, format_money, format_number,
                        format_percent, format_years, histogram_svg,
                        pyramid_svg, scatter_svg)

@dataclass
class Block:
    """Element de contenu d'une slide, independant du format de sortie."""

    kind: str                      # kpis | table | chart | note | text | legend
    payload: Any = None
    title: str = ""
    width: str = "full"            # full | half | third


@dataclass
class Slide:
    """Une page paysage."""

    title: str
    subtitle: str = ""
    blocks: List[Block] = field(default_factory=list)
    kind: str = "content"          # cover | content | closing


# ------------------------------------------------------------------ decoupage


def _kpi_block(pairs: Sequence[Sequence[str]], width: str = "full",
               compact: bool = False, forts: int = 0) -> Block:
    """Un bandeau d'indicateurs. `forts` en met N en avant, les premiers.

    Tous de la meme teinte, un bandeau n'a pas de sommet : l'oeil se pose
    au hasard. Deux ou trois chiffres portent la lecture d'une page, et
    ce sont ceux-la qui prennent la couleur.
    """
    return Block("kpis",
                 {"items": [{"label": label, "value": value,
                             "fort": rang < forts}
                            for rang, (label, value) in enumerate(pairs)],
                  "compact": compact},
                 width=width)


#: Dit a defaut de mieux, quand le moteur n'a pas publie sa raison.
_MASQUE = "Résultat masqué pour préserver la confidentialité."


def _table_block(headers, rows, title="", width="full", compact=False) -> Block:
    return Block("table",
                 {"headers": list(headers), "rows": [list(r) for r in rows],
                  "compact": compact},
                 title=title, width=width)


def _population_kpis(population: Dict[str, Any]) -> List[List[str]]:
    return [
        ["Effectif", f'{population.get("headcount", 0):,}'.replace(",", " ")],
        ["Âge moyen", format_years(population.get("age_mean"))],
        ["Âge médian", format_years(population.get("age_median"))],
        ["Ancienneté moyenne", format_years(population.get("tenure_mean"))],
        ["Ancienneté médiane", format_years(population.get("tenure_median"))],
    ]


def _salary_kpis(salary: Dict[str, Any], currency: str) -> List[List[str]]:
    return [
        [reporting.payroll_label(salary),
         format_money(salary.get("payroll"), currency)],
        ["Salaire moyen", format_money(salary.get("mean"), currency)],
        ["Salaire médian", format_money(salary.get("median"), currency)],
        ["Minimum", format_money(salary.get("min"), currency)],
        ["Maximum", format_money(salary.get("max"), currency)],
    ]


def _percentile_rows(salary: Dict[str, Any], currency: str) -> List[List[str]]:
    return [
        [entry["label"], format_money(salary.get(entry["key"]), currency)]
        for entry in salary.get("published_percentiles", [])
        if salary.get(entry["key"]) is not None
    ]


def _dispersion_rows(salary: Dict[str, Any], currency: str) -> List[List[str]]:
    dispersion = salary.get("dispersion") or {}
    variation = dispersion.get("coefficient_of_variation")
    return [
        ["Q3 - Q1", format_money(dispersion.get("interquartile_range"), currency)],
        ["Q3 / Q1", format_number(dispersion.get("q3_over_q1"), 2)],
        ["P90 / P10", format_number(dispersion.get("p90_over_p10"), 2)],
        ["Moyenne / Médiane", format_number(dispersion.get("mean_over_median"), 2)],
        ["Coefficient de variation",
         format_percent(None if variation is None else variation * 100)],
    ]


def _cover(analysis: Dict[str, Any]) -> Slide:
    manifest = analysis.get("manifest", {})
    return Slide(
        title=analysis.get("title", "Analyse de rémunération"),
        subtitle=f'{manifest.get("effectif_analyse", "—")} salariés analysés',
        kind="cover",
        blocks=[Block("text", [
            f'Périmètre : {manifest.get("filtres", "Aucun filtre")}',
            f'Fichier source : {manifest.get("fichier_source", "—")}',
            f'Date d\'analyse : {manifest.get("date_analyse", "—")}',
        ])],
    )


#: Les bornes de la dispersion, et le nom de leur ecart a la mediane dans
#: le bloc que publie le moteur. La mediane n'a pas d'ecart a elle-meme.
_BORNES = (("P10", "p10", "p10_to_median"),
           ("Q1 (P25)", "p25", "q1_to_median"),
           ("Médiane", "median", None),
           ("Q3 (P75)", "p75", "q3_to_median"),
           ("P90", "p90", "p90_to_median"))


def _median_gap_header(bounds: Dict[str, Any]) -> List[str]:
    """Les intitules de colonnes du tableau de dispersion."""
    if not bounds:
        return ["Niveau", "Valeur", "Écart à la médiane"]
    return ["Niveau", "Femmes", "Hommes", "Ensemble", "Écart à la médiane"]


def _sex_bounds(pay_equity: Dict[str, Any]) -> Dict[str, Any]:
    """Les bornes des deux sexes, ou rien du tout.

    Rien du tout dans trois cas, et c'est voulu : pas de champ de sexe
    exploitable, un des deux groupes sous le seuil de publication, ou un
    des deux sans assez de montants connus. Une colonne « Femmes » remplie
    de tirets ne dirait pas laquelle de ces trois raisons s'applique ; le
    tableau a deux colonnes, lui, ne promet rien qu'il ne tienne.
    """
    bloc = (pay_equity or {}).get("bounds_by_sex") or {}
    femmes, hommes = bloc.get("female") or {}, bloc.get("male") or {}
    if not femmes or not hommes:
        return {}
    if femmes.get("masked") or hommes.get("masked"):
        return {}
    return {"female": femmes, "male": hommes}


def _median_gap_rows(salary: Dict[str, Any], currency: str,
                     bounds: Optional[Dict[str, Any]] = None
                     ) -> List[List[str]]:
    """Dispersion de base : les bornes, et leur ecart a la mediane.

    Les bornes et l'ecart tiennent dans le meme tableau parce qu'ils se
    lisent ensemble : « Q1 a 31 500 EUR » ne dit rien sans la mediane, et
    « Q1 a 12 % sous la mediane » ne dit rien sans le montant. Les deux
    colonnes cote a cote evitent au lecteur de faire la division.

    Quand les deux sexes sont publiables, chaque borne se lit sur trois
    colonnes. C'est la seule facon de voir qu'un ecart de medianes
    modeste peut cacher deux distributions de formes differentes : deux
    groupes peuvent se croiser a la mediane et diverger aux extremes.
    L'ecart, lui, reste celui de l'ensemble — c'est de sa mediane qu'on
    parle.

    Les ratios experts (Q3/Q1, P90/P10, coefficient de variation) n'y sont
    pas : c'est la synthese, pas le dossier d'analyse. Ils restent dans la
    vue detaillee et dans le classeur.
    """
    dispersion = salary.get("dispersion") or {}
    rows: List[List[str]] = []
    for libelle, cle, ecart in _BORNES:
        valeur = salary.get(cle)
        if valeur is None:
            continue
        part = None if ecart is None else dispersion.get(ecart)
        ligne = [libelle]
        if bounds:
            for sexe in ("female", "male"):
                montant = bounds[sexe].get(cle)
                ligne.append("—" if montant is None
                             else format_money(montant, currency))
        ligne.append(format_money(valeur, currency))
        # La mediane ne s'ecarte pas d'elle-meme : elle est la reference.
        # Un tiret au milieu de la colonne se lisait comme une donnee
        # manquante.
        ligne.append("référence" if cle == "median"
                     else ("—" if part is None else _signed_percent(part)))
        rows.append(ligne)
    return rows


def _signed_percent(fraction: float) -> str:
    """Un ecart relatif, signe. Le signe est l'information : sans lui, on
    ne sait pas de quel cote de la mediane se trouve la borne."""
    texte = format_percent(abs(fraction) * 100, digits=0)
    return texte if fraction == 0 else f'{"+" if fraction > 0 else "−"}{texte}'


def _csp_parts(population: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Repartition par CSP, la plus nombreuse d'abord.

    Au-dela du nombre de modalites declare en configuration, la queue se
    regroupe : une synthese d'une page n'a pas la hauteur de quinze
    lignes, et les plus petites parts n'apprennent rien qu'un « autres »
    ne dise aussi bien. Le seuil est celui que le moteur publie, donc
    celui du camembert a l'ecran — le meme « Autres » des deux cotes.
    """
    limite = int(population.get("csp_max_slices") or 6)
    parts = sorted(population.get("csp_split") or [],
                   key=lambda item: -item["count"])
    if not parts:
        return []
    # Une colonne absente du fichier donnait un anneau d'un seul arc,
    # « (non renseigné) 100 % » : un tiers de page pour dire qu'on ne sait
    # rien. Un camembert a une part n'est pas une repartition.
    if len(parts) == 1 and parts[0]["label"] == UNKNOWN_LABEL:
        return []
    retenues, reste = parts[:limite], parts[limite:]
    morceaux = [{"label": item["label"], "count": item["count"],
                 "share": item["share"]} for item in retenues]
    if reste:
        morceaux.append({"label": f"Autres ({len(reste)})",
                         "count": sum(item["count"] for item in reste),
                         "share": sum(item["share"] for item in reste)})
    return morceaux


def build_summary(analysis: Dict[str, Any]) -> List[Slide]:
    """Synthese simplifiee : une seule page paysage.

    Composition demandee : les effectifs et les moyennes d'age et
    d'anciennete en bandeau, puis les deux pyramides et la repartition par
    CSP, puis la dispersion de base a cote de sa boite a moustaches.

    Pas de nuage de points ici : il demande de la hauteur pour que la
    dispersion verticale se lise, et la page n'en a plus. Il reste dans la
    vue detaillee, ou il a sa propre planche.
    """
    salary = analysis.get("salary", {})
    population = analysis.get("population", {})
    currency = salary.get("currency", "EUR")
    manifest = analysis.get("manifest", {})

    blocks: List[Block] = [
        # Les medianes seules. Une moyenne d'age posee a cote de sa mediane
        # fait deux chiffres a deux ans l'un de l'autre, et le lecteur
        # arbitre entre les deux au lieu de lire la page. La mediane est
        # celle qui tient devant une population deformee par quelques
        # anciennetes tres longues ; les moyennes restent dans la vue
        # detaillee, ou il y a la place de les comparer.
        _kpi_block([
            ["Effectif", f'{population.get("headcount", 0):,}'.replace(",", " ")],
            ["Âge médian", format_years(population.get("age_median"))],
            ["Ancienneté médiane",
             format_years(population.get("tenure_median"))],
            ["Salaire médian", format_money(salary.get("median"), currency)],
        ], compact=True, forts=1),
    ]

    # Les deux pyramides et la CSP, sur une rangee de trois. Une pyramide
    # dont aucune tranche n'est ventilee par sexe ne se dessine pas : le
    # trace se retire de lui-meme et la rangee se recompose.
    csp = _csp_parts(population)
    # Deux pyramides et un anneau font trois colonnes ; sans anneau, les
    # deux pyramides prennent chacune une moitie plutot que de laisser un
    # tiers de page blanc a leur droite.
    largeur = "third" if csp else "half"
    for cle, titre in (("age_bands", "Pyramide des âges"),
                       ("tenure_bands", "Pyramide des anciennetés")):
        rangs = population.get(cle) or []
        if not any(row.get("female") or row.get("male") for row in rangs):
            continue
        blocks.append(Block(
            "chart", {"type": "pyramid", "rows": rangs, "label": titre},
            title=titre, width=largeur))
    # La repartition en anneau plutot qu'en tableau. Trois modalites sur
    # sept se lisent d'un coup d'oeil quand elles sont des arcs ; en
    # colonne, il faut comparer des pourcentages deux a deux. Le nombre et
    # la part restent ecrits dans la legende : le dessin range la meme
    # information, il n'en retire aucune.
    if csp:
        intitule = population.get("csp_label") or "CSP"
        blocks.append(Block(
            "chart", {"type": "donut", "parts": csp, "label": intitule,
                      "total": population.get("headcount")},
            title=f'Répartition par {intitule}', width="third"))

    # La dispersion et sa boite, cote a cote : le tableau donne les
    # montants, le dessin donne la forme.
    bornes = _sex_bounds(analysis.get("pay_equity") or {})
    dispersion_rows = _median_gap_rows(salary, currency, bornes)
    # Le tableau prend toute la largeur des qu'il porte les deux sexes :
    # cinq colonnes sur une demi-page se lisaient a l'etroit, et c'est le
    # tableau qui porte l'histoire de l'ecart.
    if dispersion_rows:
        blocks.append(_table_block(
            _median_gap_header(bornes), dispersion_rows,
            title="Dispersion des rémunérations",
            width="full" if bornes else "half", compact=True))
    # La boite se pose a sa propre condition et non a celle du tableau :
    # celui-ci se contente de la mediane, la boite a besoin de ses cinq
    # reperes. Posee sans eux, elle laissait une colonne titree et vide.
    #
    # Et elle ne se pose pas du tout sous le tableau a trois colonnes :
    # elle y redessinerait la seule colonne « Ensemble », que le lecteur
    # vient de lire chiffre par chiffre, au prix d'un tiers de la page.
    # Sans ventilation par sexe, le tableau est maigre et la forme, elle,
    # apprend quelque chose : la boite se pose a cote.
    if not bornes and all(salary.get(cle) is not None
                          for cle in ("p10", "p25", "median", "p75", "p90")):
        blocks.append(Block(
            "chart", {"type": "boxplot", "salary": salary},
            title="Boîte à moustaches", width="half"))

    subtitle = (f'{manifest.get("effectif_analyse", "—")} salariés · '
                f'{manifest.get("filtres", "Aucun filtre")}')
    coverage = salary.get("coverage")
    if coverage is not None and coverage < 99.95:
        # Une couverture incomplete change la lecture de tous les montants :
        # elle est dite en clair, en tete de page. A 100 % elle n'apprend rien.
        subtitle += f' · {format_percent(coverage)} des rémunérations renseignées'

    return [Slide(
        title=analysis.get("title", "Analyse de rémunération"),
        subtitle=subtitle,
        blocks=blocks,
    )]


def _scatter_title(analysis: Dict[str, Any]) -> str:
    """Titre du nuage : les deux axes, tels que le moteur les declare.

    Ecrit en dur, il annoncait « Anciennete et remuneration » quel que soit
    ce que le dessin montrait — les deux axes se parametrent.
    """
    from .reporting import axis_label

    dataset = analysis.get("scatter", {})
    return (f'{axis_label(dataset, "y")} et '
            f'{axis_label(dataset, "x").lower()}'
            ).strip(" et") or "Nuage de points"


def build_deck(analysis: Dict[str, Any]) -> List[Slide]:
    """Vision complete : un jeu de slides, une idee par page."""
    salary = analysis.get("salary", {})
    population = analysis.get("population", {})
    currency = salary.get("currency", "EUR")
    slides: List[Slide] = [_cover(analysis)]

    # Pas de planche « Qualite des donnees ». Le controle se lit a l'ecran,
    # avant de produire quoi que ce soit : c'est le travail de celui qui
    # analyse, et il est fait quand le document part. Le lecteur du
    # document, lui, n'a pas a arbitrer sur un encodage ou un doublon ; une
    # page d'autocritique en tete ne lui apprend rien et jette un doute sur
    # tout ce qui suit.

    # Population
    if population.get("masked"):
        # Une planche qui disparait laisse un document dont le lecteur ne
        # sait pas s'il manque un chiffre ou s'il n'y en avait pas. Elle
        # reste, et porte la raison.
        slides.append(Slide("Population", "", blocks=[
            Block("text", [population.get("warning") or _MASQUE])]))
    else:
        blocs = [
            _kpi_block(_population_kpis(population)),
            _table_block(["Tranche d'âge", "Effectif", "Part"],
                         [[row["label"], str(row["count"]), format_percent(row["share"])]
                          for row in population.get("age_bands", [])],
                         title="Âge", width="half"),
            _table_block(["Ancienneté", "Effectif", "Part"],
                         [[row["label"], str(row["count"]), format_percent(row["share"])]
                          for row in population.get("tenure_bands", [])],
                         title="Ancienneté", width="half"),
        ]
        slides.append(Slide("Population", "Structure d'âge et d'ancienneté",
                            blocks=blocs))
        # Les pyramides sur leurs propres planches, une par grandeur. Le
        # tableau donne les effectifs, le dessin donne la forme — un creux
        # au milieu, une base large, un sommet qui part a la retraite se
        # voient d'un coup d'oeil et ne se lisent pas dans une colonne de
        # nombres. Deux pyramides ajoutees sous les deux tableaux ne
        # tenaient pas dans la page : la seconde en sortait entierement.
        #
        # Une pyramide dont aucune tranche n'est ventilee par sexe ne se
        # dessine pas : elle n'aurait qu'une moitie, et sa planche ne
        # s'ouvre pas.
        for cle, titre in (("age_bands", "Pyramide des âges"),
                           ("tenure_bands", "Pyramide des anciennetés")):
            rangs = population.get(cle) or []
            if not any(row.get("female") or row.get("male") for row in rangs):
                continue
            slides.append(Slide(titre, "Femmes et hommes, tranche par tranche",
                                blocks=[Block(
                                    "chart",
                                    {"type": "pyramid", "rows": rangs,
                                     "label": titre}, width="full")]))

    # Remuneration
    if salary.get("masked"):
        slides.append(Slide(salary.get("field_label") or "Rémunération", "",
                            blocks=[Block("text",
                                          [salary.get("warning") or _MASQUE])]))
    else:
        slides.append(Slide("Rémunération",
                            f'Champ analyse : {salary.get("field_label") or salary.get("field", "")}',
                            blocks=[
            _kpi_block(_salary_kpis(salary, currency)),
            _table_block(["Percentile", "Valeur"], _percentile_rows(salary, currency),
                         title="Percentiles", width="half"),
            _table_block(["Indicateur", "Valeur"], _dispersion_rows(salary, currency),
                         title="Dispersion", width="half"),
        ]))
        # La meme dispersion, en image, sous les deux tableaux : les cinq
        # reperes chiffres juste au-dessus prennent une forme, et la page
        # ne se termine plus sur une demi-hauteur vide.
        if all(salary.get(cle) is not None
               for cle in ("p10", "p25", "median", "p75", "p90")):
            slides[-1].blocks.append(Block(
                "chart", {"type": "boxplot", "salary": salary},
                title="Boîte à moustaches", width="full"))

    # Distribution
    distribution = analysis.get("distribution", {})
    if distribution.get("available"):
        slides.append(Slide("Distribution des rémunérations", blocks=[
            Block("chart", {"type": "histogram", "bins": distribution.get("bins", [])}),
        ]))
    # Anciennete x remuneration
    scatter = analysis.get("scatter", {})
    if scatter.get("available"):
        subtitle = ""
        blocks = [Block("legend", scatter), Block("chart", {"type": "scatter",
                                                            "dataset": scatter})]
        slides.append(Slide(_scatter_title(analysis), subtitle, blocks=blocks))

    # Segments : une slide par dimension
    for segment in analysis.get("segments", []) or []:
        rows = []
        for row in segment["rows"][:12]:
            if row["masked"]:
                rows.append([row["segment"], str(row["headcount"]),
                             "—", "—", "—", "—"])
                continue
            item = row["salary"]
            rows.append([
                row["segment"], str(row["headcount"]),
                format_money(item.get("mean"), currency),
                format_money(item.get("median"), currency),
                format_money(item.get("p25"), currency),
                format_money(item.get("p75"), currency),
            ])
        slide = Slide(f'Analyse par {segment["label"].lower()}')
        slide.blocks = [_table_block(
            [segment["label"], "Effectif", "Moyenne", "Médiane", "Q1", "Q3"], rows)]
        slides.append(slide)

    # Pay Transparency : deux slides, l'ecart et son detail par poste
    equity = analysis.get("pay_equity") or {}
    if equity.get("available"):
        label = (equity.get("category_label") or "poste").lower()
        slides.append(Slide(
            "Écarts femmes / hommes",
            "Un écart positif signifie que les femmes sont moins rémunérées",
            blocks=[
                _kpi_block([
                    ["Écart global", format_percent(
                        equity.get("pay", {}).get("mean_gap"))],
                    [f"À {label} comparable",
                     format_percent(equity.get("comparable_gap"))],
                    ["Effet de structure",
                     format_percent(equity.get("structure_gap"))],
                    ["Rattrapage", format_money(equity.get("at_stake_total"),
                                                currency)],
                    # La couverture etait dite en toutes lettres sous le
                    # bandeau. Un document ne commente pas ses chiffres :
                    # elle en devient un.
                    ["Couverture",
                     format_percent(equity.get("comparable_coverage"))],
                ], forts=2),
                _table_block(["Quartile", "Part femmes", "Part hommes"],
                             [[f'Q{item["quartile"]}',
                               format_percent(item.get("female_share")),
                               format_percent(item.get("male_share"))]
                              for item in equity.get("quartiles", [])],
                             title="Répartition par quartile"),
            ]))
        # Les categories ou l'enjeu est le plus fort : c'est la que se
        # decide un plan de rattrapage.
        retenues = sorted(equity.get("categories", []),
                          key=lambda item: (not item.get("published"),
                                            -(item.get("at_stake") or 0.0)))[:12]
        if retenues:
            rows = []
            for item in retenues:
                if not item.get("published"):
                    rows.append([item["category"], str(item["female_count"]),
                                 str(item["male_count"]), "masqué", "—"])
                    continue
                rows.append([item["category"], str(item["female_count"]),
                             str(item["male_count"]),
                             format_percent(item.get("mean_gap")),
                             format_money(item.get("at_stake"), currency)])
            slide = Slide(f"Écart par {label}",
                          "Classé par enjeu de rattrapage")
            slide.blocks = [_table_block(
                [equity.get("category_label") or "Catégorie", "Femmes",
                 "Hommes", "Écart moyen", "Rattrapage"], rows)]
            slides.append(slide)

    # Comparaison
    comparison = analysis.get("comparison")
    if comparison:
        rows = reporting.comparison_rows(comparison, currency)
        slides.append(Slide("Comparaison de populations", blocks=[_table_block(
            ["Indicateur", comparison["left_label"], comparison["right_label"], "Écart"],
            rows)]))

    # Pas de diapositive de tracabilite. Le fichier source, la date et le
    # perimetre sont deja sur la garde, qui est la premiere chose que le
    # lecteur voit ; l'empreinte et la version du moteur appartiennent au
    # manifeste, qui est ecrit a cote des documents et fait pour ca. Une
    # page de fin qui les repete ne sert qu'a allonger le jeu.
    return slides


# ----------------------------------------------------------------- rendu HTML

#: Palette du jeu de slides en cours de rendu, HTML comme PDF. Voir la note
#: de `reporting.ACTIVE` : un document se rend d'un seul tenant.
ACTIVE: palette.Palette = palette.by_name(palette.DEFAULT_THEME)


def use(analysis) -> palette.Palette:
    """Fixe la palette du rendu qui commence, pour les deux formats.

    Le rapport est teinte en meme temps : une restitution complete produit
    un rapport et un jeu de slides du meme theme, et l'un des deux ne doit
    pas rester sur les couleurs du precedent.
    """
    global ACTIVE
    ACTIVE = palette.from_analysis(analysis)
    reporting.use(analysis)
    _publish_pdf_colours()
    return ACTIVE


def _variables() -> str:
    """Les couleurs du theme, en variables CSS."""
    pairs = (
        ("ink", ACTIVE.ink), ("muted", ACTIVE.muted), ("faint", ACTIVE.faint),
        ("line", ACTIVE.line), ("line-strong", ACTIVE.line_strong),
        ("grid", ACTIVE.grid), ("panel", ACTIVE.panel),
        ("bg", ACTIVE.canvas), ("accent", ACTIVE.accent),
        ("accent-deep", ACTIVE.accent_deep),
        ("accent-soft", ACTIVE.accent_soft),
        # Le fond de la planche : un gris a peine plus dense que les pages,
        # pour que chaque slide se detache sans cadre.
        ("deck", palette.mix(ACTIVE.ink, palette.WHITE, 0.90)),
        ("cover-sub", palette.mix(ACTIVE.accent, palette.WHITE, 0.68)),
        ("cover-line", palette.mix(ACTIVE.accent, palette.WHITE, 0.52)),
        ("cover-page", palette.mix(ACTIVE.accent, palette.WHITE, 0.45)),
        ("warn", ACTIVE.warn), ("warn-bg", ACTIVE.warn_soft),
        ("female", ACTIVE.female), ("male", ACTIVE.male),
    )
    return ":root{" + ";".join(f"--{n}:{v}" for n, v in pairs) + "}"


def _slide_css() -> str:
    return _variables() + _SLIDE_CSS


_SLIDE_CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--deck);color:var(--ink);
font:15px/1.45 "Segoe UI",Calibri,Arial,sans-serif}
.deck{display:flex;flex-direction:column;align-items:center;gap:20px;padding:24px}
/* La page garde une geometrie fixe (1280x720), decidee ici et nulle part
   ailleurs — le PDF a la sienne, PDF_WIDTH et PDF_HEIGHT. C'est ce qui
   garantit que
   l'ecran, l'impression et le PDF montrent exactement la meme chose. Pour
   tenir sur un ecran plus etroit, elle est mise à l'echelle plutot que
   reagencee. `--slide-scale` est calculé au chargement et au redimensionnement ;
   sans JavaScript il vaut 1 et le comportement est celui d'avant. */
/* La planche grandit si son contenu depasse, elle ne le coupe pas. Une
   hauteur fixe et « overflow:hidden » faisaient disparaitre le bas des
   tableaux longs : le lecteur voyait une page propre, sans savoir qu'il
   lui manquait quatre lignes. La hauteur du cadre est ajustee par le
   script, qui connait l'echelle ; 720px reste le minimum, et le repli
   sans script. */
.frame{width:100%;max-width:1280px;min-height:calc(720px * var(--slide-scale,1))}
.slide{position:relative;width:1280px;min-height:720px;background:#fff;
transform:scale(var(--slide-scale,1));transform-origin:top left;
border:1px solid var(--line);border-radius:4px;padding:44px 56px 56px;
display:flex;flex-direction:column}
.slide h1{font-size:34px;margin:0 0 6px;font-weight:600;
letter-spacing:-.012em}
.kpi .value{font-variant-numeric:tabular-nums}
td,th{font-variant-numeric:tabular-nums}
.slide .sub{color:var(--muted);font-size:16px;margin-bottom:22px}
.slide.cover{justify-content:center;background:linear-gradient(135deg,var(--accent),var(--accent-deep));
color:#fff;border:none}
.slide.cover h1{font-size:46px;max-width:80%}
.slide.cover .sub{color:var(--cover-sub);font-size:22px;margin-bottom:34px}
.slide.cover .lines div{color:var(--cover-sub);font-size:15px;margin-bottom:7px}
.rule{height:3px;width:90px;background:var(--accent);margin-bottom:20px}
.slide.cover .rule{background:var(--cover-line);width:120px}
.body{flex:1;display:flex;flex-wrap:wrap;gap:22px;align-content:flex-start;
min-height:0;overflow:hidden}
.full{flex:1 1 100%}
.half{flex:1 1 calc(50% - 11px);min-width:0}
.third{flex:1 1 calc(33.333% - 15px);min-width:0}
/* Tableaux resserres : une page dense doit tenir sans reduire la
   taille du texte sous le seuil de lisibilite en projection. */
.compact th,.compact td{padding:4px 8px}
.compact table{font-size:13px}
.kpis{display:flex;gap:14px;width:100%}
.kpi{flex:1;background:var(--panel);border:1px solid var(--line);
border-radius:8px;padding:14px 16px;position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;
background:var(--line)}
.kpi.fort{background:var(--accent-soft);border-color:var(--accent-soft)}
.kpi.fort::before{background:var(--accent)}
.kpi.fort .value{color:var(--accent-deep)}
.kpi.fort .label{color:var(--accent-deep);opacity:.75}
.kpi .label{font-size:11px;color:var(--muted);text-transform:uppercase;
letter-spacing:.05em}
.kpi .value{font-size:23px;font-weight:600;margin-top:6px;white-space:nowrap}
/* Bandeau resserre : sert de pied de page chiffre sous les colonnes. */
.kpis.compact .kpi{padding:8px 12px}
.kpis.compact .label{font-size:10px}
.kpis.compact .value{font-size:15px;margin-top:2px}
.block-title{font-size:12px;color:var(--muted);text-transform:uppercase;
letter-spacing:.05em;margin-bottom:8px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:7px 10px;text-align:right}
th:first-child,td:first-child{text-align:left}
thead th{background:var(--panel);color:var(--muted);text-transform:uppercase;
font-size:11px;letter-spacing:.04em;font-weight:600}
.note{border-left:3px solid var(--warn);background:var(--warn-bg);color:var(--warn);
padding:10px 14px;font-size:13px;width:100%}
.lines div{margin-bottom:6px;color:var(--muted);font-size:14px}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:13px;width:100%}
.legend span{display:inline-flex;align-items:center;gap:5px}
.dot{width:10px;height:10px;border-radius:50%}
svg{display:block;width:100%;height:auto}
.chart-fit{min-height:0}
.pagenum{position:absolute;right:56px;bottom:22px;color:var(--muted);font-size:12px}
.slide.cover .pagenum{color:var(--cover-page)}
.hint{position:fixed;left:50%;transform:translateX(-50%);bottom:14px;
background:var(--ink);color:var(--bg);padding:7px 14px;border-radius:16px;font-size:12px;
opacity:.85}
@media print{
  @page{size:1280px 720px;margin:0}
  body{background:#fff}
  .deck{padding:0;gap:0}
  .hint{display:none}
  /* A l'impression, la page reprend sa taille reelle : la mise à l'echelle
     d'ecran ne doit jamais alterer le rendu papier ni le PDF. */
  :root{--slide-scale:1 !important}
  .frame{width:1280px;min-height:720px;height:auto;max-width:none}
  .slide{border:none;border-radius:0;page-break-after:always;break-after:page}
  .frame:last-child .slide{page-break-after:auto;break-after:auto}
}
"""

# Navigation clavier. Aucun code externe, aucun chargement reseau.
_SLIDE_JS = """
(function(){
  // Echelle = largeur disponible / largeur de page, plafonnee a 1 : on réduit
  // pour tenir, jamais on n'agrandit (le texte deviendrait disproportionne).
  function fit(){
    var frame=document.querySelector('.frame');
    if(!frame)return;
    var scale=Math.min(1,frame.clientWidth/1280);
    document.documentElement.style.setProperty('--slide-scale',scale);
    // Le cadre reserve la hauteur reelle de sa planche, mise a l'echelle :
    // une planche plus haute que 720px pousse la suivante au lieu d'etre
    // recouverte par elle.
    [].forEach.call(document.querySelectorAll('.frame'),function(f){
      var s=f.querySelector('.slide');
      if(s)f.style.height=(s.offsetHeight*scale)+'px';
    });
  }
  fit();
  window.addEventListener('resize',fit);
  if(window.ResizeObserver){
    var deck=document.querySelector('.deck');
    if(deck)new ResizeObserver(fit).observe(deck);
  }

  var slides=[].slice.call(document.querySelectorAll('.frame'));
  if(!slides.length)return;
  var index=0;
  function show(i){
    index=Math.max(0,Math.min(slides.length-1,i));
    slides[index].scrollIntoView({behavior:'smooth',block:'center'});
  }
  document.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key==='PageDown'||e.key===' ')  {show(index+1);e.preventDefault();}
    if(e.key==='ArrowLeft' ||e.key==='PageUp')                 {show(index-1);e.preventDefault();}
    if(e.key==='Home'){show(0);e.preventDefault();}
    if(e.key==='End'){show(slides.length-1);e.preventDefault();}
  });
  var tip=document.createElement('div');
  tip.style.cssText='position:fixed;display:none;background:var(--ink);color:var(--bg);'+
    'padding:6px 9px;border-radius:4px;font:12px/1.4 Segoe UI,Arial,sans-serif;'+
    'pointer-events:none;z-index:9';
  document.body.appendChild(tip);
  document.addEventListener('mouseover',function(e){
    var t=e.target;
    if(!t||!t.getAttribute||!t.getAttribute('data-tip'))return;
    tip.textContent=t.getAttribute('data-tip');
    tip.style.display='block';
    tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px';
  });
  document.addEventListener('mouseout',function(e){
    if(e.target&&e.target.getAttribute&&e.target.getAttribute('data-tip'))
      tip.style.display='none';
  });
})();
"""


def _html_escape(value: Any) -> str:
    import html as _html
    return _html.escape("" if value is None else str(value), quote=True)


#: Hauteur de trace par defaut, par type de graphique et par largeur de
#: bloc. Un nuage a besoin de hauteur pour montrer sa dispersion verticale ;
#: une boite a moustaches est horizontale et n'en tire rien.
_CHART_HEIGHTS = {
    "histogram": {"full": 330, "half": 260, "third": 200},
    "scatter": {"full": 430, "half": 300, "third": 220},
    # « full » ne sert qu'a une pyramide seule sur sa planche : elle y a
    # toute la hauteur, et des barres qui se comparent de loin.
    "pyramid": {"full": 440, "half": 180, "third": 165},
    "boxplot": {"full": 150, "half": 150, "third": 145},
    # L'anneau est aussi haut que large : sa hauteur est ce qui fixe sa
    # taille, pas la place restante.
    "donut": {"full": 190, "half": 180, "third": 165},
}


def _render_block(block: Block, currency: str) -> str:
    title = (f'<div class="block-title">{_html_escape(block.title)}</div>'
             if block.title else "")
    if block.kind == "kpis":
        cells = "".join(
            f'<div class="kpi{" fort" if item.get("fort") else ""}">'
            f'<div class="label">{_html_escape(item["label"])}</div>'
            f'<div class="value">{_html_escape(item["value"])}</div></div>'
            for item in block.payload["items"]
        )
        variant = " compact" if block.payload.get("compact") else ""
        return (f'<div class="{block.width}">'
                f'<div class="kpis{variant}">{cells}</div></div>')
    if block.kind == "table":
        head = "".join(f"<th>{_html_escape(h)}</th>" for h in block.payload["headers"])
        body = "".join(
            "<tr>" + "".join(f"<td>{_html_escape(c)}</td>" for c in row) + "</tr>"
            for row in block.payload["rows"]
        )
        compact = " compact" if block.payload.get("compact") else ""
        return (f'<div class="{block.width}{compact}">{title}'
                f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
    if block.kind == "chart":
        spec = block.payload
        # Dessiner large puis reduire par CSS ecraserait les libelles d'axe
        # (7 px reduits de moitie deviennent illisibles) : le SVG est produit
        # a la largeur reelle de son conteneur.
        canvas = {"full": 1160, "half": 560, "third": 365}[block.width]
        height = spec.get("height") or _CHART_HEIGHTS.get(
            spec["type"], _CHART_HEIGHTS["scatter"])[block.width]
        if spec["type"] == "histogram":
            svg = histogram_svg(spec["bins"], currency, width=canvas, height=height)
        elif spec["type"] == "pyramid":
            svg = pyramid_svg(spec["rows"], width=canvas, height=height,
                              label=spec.get("label", ""))
        elif spec["type"] == "boxplot":
            svg = boxplot_svg(spec["salary"], currency, width=canvas,
                              height=height)
        elif spec["type"] == "donut":
            svg = donut_svg(spec["parts"], width=canvas, height=height,
                            label=spec.get("label", ""),
                            total=spec.get("total"))
        else:
            svg = scatter_svg(spec["dataset"], currency, width=canvas, height=height)
        if not svg:
            return ""
        # `chart-fit` borne le graphique a la place restante : une hauteur mal
        # estimee ne peut plus deborder du bas de la page.
        return f'<div class="{block.width} chart-fit">{title}{svg}</div>'
    if block.kind == "legend":
        dataset = block.payload
        groups = dataset.get("groups") or []
        if not groups or len(groups) > 14:
            return ""
        colors = palette.series_map(groups, ACTIVE.series,
                                     other=dataset.get("other_label"),
                                     neutral=ACTIVE.muted)
        items = "".join(
            f'<span><i class="dot" style="background:'
            f'{colors[g]}"></i>{_html_escape(g)}</span>'
            for g in groups
        )
        label = dataset.get("color_label") or ""
        return (f'<div class="full"><div class="legend">'
                f'<strong>{_html_escape(label)} :</strong>{items}</div></div>')
    if block.kind == "note":
        if not block.payload:
            return ""
        return f'<div class="full"><div class="note">{_html_escape(block.payload)}</div></div>'
    if block.kind == "text":
        lines = "".join(f"<div>{_html_escape(line)}</div>" for line in block.payload)
        return f'<div class="full lines">{lines}</div>'
    return ""


def render_slides_html(slides: Sequence[Slide], analysis: Dict[str, Any]) -> str:
    """Jeu de slides paysage dans un fichier HTML autoportant."""
    use(analysis)
    currency = analysis.get("salary", {}).get("currency", "EUR")
    title = analysis.get("title", "Analyse de rémunération")
    rendered = []
    for number, slide in enumerate(slides, start=1):
        blocks = "".join(_render_block(block, currency) for block in slide.blocks)
        subtitle = (f'<div class="sub">{_html_escape(slide.subtitle)}</div>'
                    if slide.subtitle else "")
        page = (f'<div class="pagenum">{number} / {len(slides)}</div>'
                if slide.kind != "cover" or len(slides) > 1 else "")
        rendered.append(
            f'<div class="frame"><section class="slide {slide.kind}">'
            f'<h1>{_html_escape(slide.title)}</h1>{subtitle}'
            f'<div class="rule"></div>'
            f'<div class="body">{blocks}</div>{page}</section></div>'
        )
    hint = ('<div class="hint">← → pour naviguer · Ctrl+P pour imprimer en PDF paysage</div>'
            if len(slides) > 1 else "")
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html_escape(title)}</title>
<style>{_slide_css()}</style>
</head>
<body>
<div class="deck">{''.join(rendered)}</div>
{hint}
<script>{_SLIDE_JS}</script>
</body>
</html>
"""


def write_slides_html(slides: Sequence[Slide], analysis: Dict[str, Any],
                      path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_slides_html(slides, analysis))
    return restrict_to_owner(path)


# ------------------------------------------------------------------ rendu PDF

# A4 paysage : le format le plus sur a l'impression et a la projection.
PDF_WIDTH, PDF_HEIGHT = 841.89, 595.28
_MARGIN = 38.0

def _rgb(hex_color: str) -> tuple:
    """Teinte en composantes de 0 a 1, comme les attend le generateur PDF."""
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# Le PDF n'a pas de variables : ses couleurs sont des triplets, poses ici et
# relus par les fonctions de trace. `_publish_pdf_colours()` les recalcule
# quand le theme change — c'est le pendant du bloc `:root` du HTML.
_INK = _MUTED = _ACCENT = _LINE = _PANEL = _WARN = _WARN_BG = (0.0, 0.0, 0.0)
_FEMALE = _MALE = (0.0, 0.0, 0.0)
_ACCENT_SOFT = _ACCENT_DEEP = (0.0, 0.0, 0.0)
_WHITE = (1.0, 1.0, 1.0)
_PDF_PALETTE: List[tuple] = []


def _publish_pdf_colours() -> None:
    global _INK, _MUTED, _ACCENT, _LINE, _PANEL, _WARN, _WARN_BG, _PDF_PALETTE
    global _FEMALE, _MALE, _ACCENT_SOFT, _ACCENT_DEEP
    _INK, _MUTED = _rgb(ACTIVE.ink), _rgb(ACTIVE.muted)
    _ACCENT_SOFT, _ACCENT_DEEP = (_rgb(ACTIVE.accent_soft),
                                  _rgb(ACTIVE.accent_deep))
    _FEMALE, _MALE = _rgb(ACTIVE.female), _rgb(ACTIVE.male)
    _ACCENT, _LINE = _rgb(ACTIVE.accent), _rgb(ACTIVE.line)
    _PANEL = _rgb(ACTIVE.panel)
    _WARN, _WARN_BG = _rgb(ACTIVE.warn), _rgb(ACTIVE.warn_soft)
    _PDF_PALETTE = [_rgb(colour) for colour in ACTIVE.series]


_publish_pdf_colours()


def _draw_kpis(page, payload, x, y, width) -> float:
    """Bandeau d'indicateurs. Retourne la hauteur consommee."""
    items = payload["items"]
    compact = bool(payload.get("compact"))
    height = 34.0 if compact else 52.0
    label_size, value_size = (5.8, 9.0) if compact else (6.5, 13.0)
    label_y, value_y = (12, 25) if compact else (18, 39)
    gap = 9.0
    count = max(len(items), 1)
    cell = (width - gap * (count - 1)) / count
    for index, item in enumerate(items):
        left = x + index * (cell + gap)
        fort = bool(item.get("fort"))
        page.rect(left, y - height, cell, height,
                  fill=_ACCENT_SOFT if fort else _PANEL, stroke=_LINE)
        # Un filet vertical a gauche : il marque l'indicateur sans lui
        # donner une taille differente, ce qui romprait l'alignement du
        # bandeau.
        page.rect(left, y - height, 2.4, height,
                  fill=_ACCENT if fort else _LINE)
        page.text(left + 9, y - label_y, str(item["label"]).upper(),
                  size=label_size, color=_ACCENT_DEEP if fort else _MUTED,
                  max_width=cell - 18)
        page.text(left + 9, y - value_y, str(item["value"]), size=value_size,
                  bold=True, color=_ACCENT_DEEP if fort else _INK,
                  max_width=cell - 18)
    return height


def _draw_table(page, payload, x, y, width, max_height) -> float:
    headers = payload["headers"]
    rows = payload["rows"]
    if not headers:
        return 0.0
    compact = bool(payload.get("compact"))
    row_height = 13.0 if compact else 16.0
    header_height = 15.0 if compact else 17.0
    available = max(0, int((max_height - header_height) // row_height))
    rows = rows[:available]

    # Premiere colonne plus large : elle porte les libelles.
    columns = len(headers)
    first = width * (0.34 if columns > 2 else 0.62)
    other = (width - first) / max(columns - 1, 1)
    positions = [x] + [x + first + i * other for i in range(columns - 1)]

    page.rect(x, y - header_height, width, header_height, fill=_PANEL)
    for index, header in enumerate(headers):
        cell_width = first if index == 0 else other
        if index == 0:
            page.text(positions[index] + 7, y - 12, str(header).upper(), size=6.5,
                      bold=True, color=_MUTED, max_width=cell_width - 14)
        else:
            page.text(positions[index] + cell_width - 7, y - 12, str(header).upper(),
                      size=6.5, bold=True, color=_MUTED, align="right",
                      max_width=cell_width - 14)
    cursor = y - header_height
    for row in rows:
        cursor -= row_height
        for index, value in enumerate(row[:columns]):
            cell_width = first if index == 0 else other
            if index == 0:
                page.text(positions[index] + 7, cursor + 5, value, size=8.5,
                          color=_INK, max_width=cell_width - 14)
            else:
                page.text(positions[index] + cell_width - 7, cursor + 5, value,
                          size=8.5, color=_INK, align="right",
                          max_width=cell_width - 14)
        page.line(x, cursor, x + width, cursor, color=_LINE, width=0.4)
    return y - cursor


#: Place reservee a gauche pour les libelles de l'axe des ordonnees. Sans
#: elle, un montant a six chiffres depassait de la page et etait tronque.
_AXIS_GUTTER = 62.0


def _draw_histogram(page, bins, currency, x, y, width, height) -> float:
    if not bins:
        return 0.0
    axis = 30.0
    x = x + _AXIS_GUTTER
    width = width - _AXIS_GUTTER
    plot_height = height - axis
    peak = max(item["count"] for item in bins) or 1
    bar_width = width / len(bins)
    base = y - height + axis
    for value in nice_ticks(0, peak):
        level = base + value / peak * plot_height
        page.line(x, level, x + width, level, color=_LINE, width=0.4)
        page.text(x - 5, level - 2.5, f"{value:.0f}", size=6.5,
                  color=_MUTED, align="right")
    for index, item in enumerate(bins):
        bar = plot_height * item["count"] / peak
        page.rect(x + index * bar_width + 0.8, base, max(bar_width - 1.6, 0.5), bar,
                  fill=_ACCENT)
    page.line(x, base, x + width, base, color=_MUTED, width=0.5)
    low, high = bins[0]["lower"], bins[-1]["upper"]
    span = (high - low) or 1.0
    for value in nice_ticks(low, high, 4):
        page.text(x + (value - low) / span * width, base - 12,
                  format_money(value, currency), size=7, color=_MUTED,
                  align="center")
    page.text(x + width / 2, base - 23, "Effectif par classe de rémunération",
              size=7, color=_MUTED, align="center")
    return height


def _draw_scatter(page, dataset, currency, x, y, width, height) -> float:
    points = dataset.get("points") or []
    if not points:
        return 0.0
    axis = 30.0
    x = x + _AXIS_GUTTER
    width = width - _AXIS_GUTTER
    plot_height = height - axis
    base = y - height + axis
    xs = [point["x"] for point in points]
    ys = [point["y"] for point in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_span = (x_max - x_min) or 1.0
    y_span = (y_max - y_min) or 1.0

    def to_x(value):
        return x + (value - x_min) / x_span * width

    def to_y(value):
        return base + (value - y_min) / y_span * plot_height

    for value in nice_ticks(y_min, y_max):
        level = to_y(value)
        page.line(x, level, x + width, level, color=_LINE, width=0.4)
        page.text(x - 5, level - 2.5, format_money(value, currency),
                  size=6.5, color=_MUTED, align="right")
    colors = palette.series_map(dataset.get("groups") or [], _PDF_PALETTE,
                                other=dataset.get("other_label"),
                                neutral=_MUTED)
    for point in points:
        page.circle(to_x(point["x"]), to_y(point["y"]), 1.8,
                    colors.get(point["group"], _ACCENT), alpha_state="GA")
    trend = dataset.get("trend")
    if trend:
        start = min(max(trend["intercept"] + trend["slope"] * x_min, y_min), y_max)
        end = min(max(trend["intercept"] + trend["slope"] * x_max, y_min), y_max)
        page.line(to_x(x_min), to_y(start), to_x(x_max), to_y(end),
                  color=(0.690, 0.271, 0.247), width=1.4, dash=(5, 3))
    for value in nice_ticks(x_min, x_max):
        page.text(to_x(value), base - 12, format_number(value, 0),
                  size=6.5, color=_MUTED, align="center")
    # Le titre d'axe est place sous les graduations, pas a leur hauteur :
    # il chevauchait la premiere valeur.
    page.text(x + width / 2, base - 23, "Ancienneté (années)", size=7,
              color=_MUTED, align="center")
    return height


#: Hauteur de trace par defaut dans le PDF, par type et par largeur. Les
#: points du PDF ne sont pas les pixels du HTML : les memes valeurs y
#: donneraient un nuage qui depasse de la page.
_PDF_CHART_HEIGHTS = {
    "histogram": {"full": 420, "half": 250, "third": 200},
    "scatter": {"full": 420, "half": 250, "third": 200},
    "pyramid": {"full": 420, "half": 220, "third": 200},
    "boxplot": {"full": 210, "half": 200, "third": 190},
    "donut": {"full": 190, "half": 180, "third": 165},
}


def _draw_pyramid(page, rows, x, y, width, height, label="") -> float:
    """Pyramide femmes / hommes. Pendant PDF de `pyramid_svg`."""
    rows = [row for row in (rows or []) if row.get("count")]
    if not rows:
        return 0.0
    gouttiere, bout = 62.0, 24.0
    aile = (width - gouttiere - 2 * bout - 8) / 2
    if aile <= 8:
        return 0.0
    # La legende ferme le dessin au lieu de l'ouvrir : elle se lit au
    # moment ou l'on demande laquelle des deux ailes est laquelle.
    pied = 12.0 if label else 0.0
    # La tranche ne s'etire pas sans fin : au-dela, six tranches sur une
    # pleine page donnaient six barres fines separees par du vide, et la
    # forme de la pyramide — ce qu'on vient y chercher — disparaissait.
    ligne = min(max((height - pied) / len(rows), 7.0), 46.0)
    height = ligne * len(rows) + pied
    # La barre remplit sa tranche : deux tranches voisines se comparent
    # alors en masse plutot qu'en longueur.
    barre = min(ligne - 2.5, 15.0)
    sommet = max(max(row.get("female", 0), row.get("male", 0))
                 for row in rows) or 1
    centre = x + gouttiere + bout + aile + 4
    haut = y
    for index, row in enumerate(rows):
        milieu = haut - index * ligne - ligne / 2
        page.text(x, milieu - 2.2, str(row.get("label", "")), size=6.5,
                  color=_MUTED, max_width=gouttiere - 3)
        for cle, couleur, gauche in (("female", _FEMALE, True),
                                     ("male", _MALE, False)):
            valeur = int(row.get(cle, 0) or 0)
            if not valeur:
                continue
            longueur = max(aile * valeur / sommet, 0.6)
            if gauche:
                page.rect(centre - 4 - longueur, milieu - barre / 2, longueur,
                          barre, fill=couleur)
                page.text(centre - 7 - longueur, milieu - 2.2, str(valeur),
                          size=6.5, color=_INK, align="right")
            else:
                page.rect(centre + 4, milieu - barre / 2, longueur, barre,
                          fill=couleur)
                page.text(centre + 7 + longueur, milieu - 2.2, str(valeur),
                          size=6.5, color=_INK)
    page.line(centre, haut, centre, haut - len(rows) * ligne, color=_LINE,
              width=0.4)
    if label:
        bas = haut - len(rows) * ligne - 8
        page.text(centre - 7, bas, "Femmes", size=6.5, color=_FEMALE,
                  align="right")
        page.text(centre + 7, bas, "Hommes", size=6.5, color=_MALE)
    return height


def _draw_donut(page, parts, x, y, width, height, label="",
                total=None) -> float:
    """Repartition par modalite, en anneau.

    Pendant PDF de `donut_svg` : meme ordre des parts, memes couleurs,
    meme legende. Les deux formats du meme document ne doivent pas
    raconter deux repartitions differentes.

    Le repere du PDF part du bas a gauche, celui du SVG part du haut :
    les angles tournent donc dans l'autre sens pour que les parts se
    suivent dans le meme ordre a l'oeil, du haut vers la droite.
    """
    parts = [item for item in (parts or []) if item.get("count")]
    if not parts:
        return 0.0
    effectif = total if total is not None else sum(int(item["count"])
                                                   for item in parts)
    if effectif <= 0:
        return 0.0
    rayon = min(height / 2.0 - 2.0, (width - 150.0) / 2.0)
    if rayon < 24.0:
        return 0.0
    trou = rayon * 0.58
    cx, cy = x + rayon + 3.0, y - height / 2.0
    couleurs = palette.series_map([str(item["label"]) for item in parts],
                                  ACTIVE.series, neutral=ACTIVE.muted)
    debut = math.pi / 2.0
    for item in parts:
        portion = int(item["count"]) / effectif
        fin = debut - portion * 2 * math.pi
        page.wedge(cx, cy, rayon, trou, fin, debut,
                   _rgb(couleurs[str(item["label"])]))
        debut = fin
    page.text(cx, cy - 1, format_number(effectif, 0), size=13, bold=True,
              color=_INK, align="center")
    page.text(cx, cy - 13, "salariés", size=7, color=_MUTED, align="center")

    ligne = 14.0
    gauche = cx + rayon + 14.0
    haut = y - max(6.0, (height - len(parts) * ligne) / 2.0) - 8.0
    for rang, item in enumerate(parts):
        ligne_y = haut - rang * ligne
        page.rect(gauche, ligne_y - 1, 7, 7,
                  fill=_rgb(couleurs[str(item["label"])]))
        page.text(gauche + 12, ligne_y, str(item["label"]), size=8,
                  color=_INK, max_width=width - 150.0)
        page.text(x + width - 44, ligne_y, str(int(item["count"])), size=8,
                  color=_INK, align="right")
        page.text(x + width - 2, ligne_y, format_percent(item.get("share")),
                  size=8, color=_MUTED, align="right")
    return height


def _draw_boxplot(page, salary, currency, x, y, width, height) -> float:
    """Boite a moustaches P10 - Q1 - mediane - Q3 - P90.

    Pendant PDF de `boxplot_svg` : meme echelle, meme regle de placement
    des etiquettes. Les deux formats du meme document ne doivent pas
    raconter deux dispersions differentes.
    """
    bornes = {cle: salary.get(cle)
              for cle in ("min", "p10", "p25", "median", "p75", "p90", "max")}
    if any(bornes[cle] is None
           for cle in ("p10", "p25", "median", "p75", "p90")):
        return 0.0
    bas, haut = bornes["p10"], bornes["p90"]
    if haut <= bas:
        marge = abs(haut) * 0.1 or 1.0
        bas, haut = bas - marge, haut + marge
    cote = 26.0
    plot = width - 2 * cote
    if plot <= 20:
        return 0.0
    etendue = haut - bas

    def to_x(valeur: float) -> float:
        return x + cote + (valeur - bas) / etendue * plot

    legende_h, etiquette_h = 30.0, 22.0
    hauteur_boite = min(max(height - legende_h - 2 * etiquette_h - 4, 16.0), 40.0)
    # Le trace s'accroche au haut de la bande et rend la hauteur qu'il a
    # reellement prise. Cale sur le bas, il laissait entre son titre et
    # lui un blanc de la taille de ce qu'il n'avait pas consomme.
    height = legende_h + 2 * etiquette_h + hauteur_boite
    pied = y - height
    axe = pied + legende_h
    base = axe + etiquette_h
    milieu = base + hauteur_boite / 2
    x10, x25 = to_x(bornes["p10"]), to_x(bornes["p25"])
    x50, x75 = to_x(bornes["median"]), to_x(bornes["p75"])
    x90 = to_x(bornes["p90"])
    page.line(x10, milieu, x25, milieu, color=_MUTED, width=0.6)
    page.line(x75, milieu, x90, milieu, color=_MUTED, width=0.6)
    for borne in (x10, x90):
        page.line(borne, base + 4, borne, base + hauteur_boite - 4,
                  color=_MUTED, width=0.6)
    page.rect(x25, base, max(x75 - x25, 0.6), hauteur_boite, fill=_PANEL)
    page.rect(x25, base, max(x75 - x25, 0.6), 0.6, fill=_ACCENT)
    page.rect(x25, base + hauteur_boite, max(x75 - x25, 0.6), 0.6, fill=_ACCENT)
    page.line(x50, base, x50, base + hauteur_boite, color=_ACCENT, width=1.6)
    reperes = (("P10", x10, bornes["p10"]), ("Q1", x25, bornes["p25"]),
               ("Médiane", x50, bornes["median"]), ("Q3", x75, bornes["p75"]),
               ("P90", x90, bornes["p90"]))
    for (nom, abscisse, valeur), ligne in zip(
            reperes, reporting._mark_rows([p for _, p, _ in reperes])):
        if ligne == 0:
            y_nom, y_valeur = base + hauteur_boite + 12, base + hauteur_boite + 3
        else:
            y_nom, y_valeur = base - 15, base - 7
        page.text(abscisse, y_nom, nom, size=6, color=_MUTED, align="center")
        page.text(abscisse, y_valeur, format_money(valeur, currency),
                  size=6.5, color=_INK, align="center")
    page.line(x, axe, x + width, axe, color=_LINE, width=0.4)
    extremes = []
    if bornes["min"] is not None:
        extremes.append(f'minimum {format_money(bornes["min"], currency)}')
    if bornes["max"] is not None:
        extremes.append(f'maximum {format_money(bornes["max"], currency)}')
    legende = " · ".join(extremes)
    if legende:
        page.text(x, axe - 10, legende, size=6.5, color=_MUTED, max_width=width)
    return height


def _draw_legend(page, dataset, x, y, width) -> float:
    groups = dataset.get("groups") or []
    if not groups or len(groups) > 14:
        return 0.0
    from ..io.pdf_writer import text_width as _width
    cursor = x
    line_y = y - 9
    label = dataset.get("color_label") or ""
    if label:
        page.text(cursor, line_y, f"{label} :", size=7.5, bold=True, color=_MUTED)
        cursor += _width(f"{label} :", 7.5, True) + 10
    colors = palette.series_map(groups, _PDF_PALETTE,
                                other=dataset.get("other_label"),
                                neutral=_MUTED)
    for group in groups:
        entry = str(group)
        needed = _width(entry, 7.5) + 20
        if cursor + needed > x + width:
            break
        page.circle(cursor + 3, line_y + 2.5, 3, colors[group])
        page.text(cursor + 9, line_y, entry, size=7.5, color=_MUTED)
        cursor += needed
    return 16.0


def _draw_note(page, message, x, y, width) -> float:
    from ..io.pdf_writer import truncate
    height = 26.0
    page.rect(x, y - height, width, height, fill=_WARN_BG)
    page.rect(x, y - height, 2.5, height, fill=(0.788, 0.573, 0.184))
    page.text(x + 10, y - 16, truncate(str(message), 8, width - 22), size=8,
              color=_WARN)
    return height


def _draw_slide(page, slide: Slide, number: int, total: int, currency: str) -> None:
    width = PDF_WIDTH - 2 * _MARGIN
    if slide.kind == "cover":
        page.rect(0, 0, PDF_WIDTH, PDF_HEIGHT, fill=_ACCENT)
        page.text(_MARGIN + 12, PDF_HEIGHT / 2 + 60, slide.title, size=30,
                  bold=True, color=_WHITE, max_width=width - 24)
        if slide.subtitle:
            page.text(_MARGIN + 12, PDF_HEIGHT / 2 + 30, slide.subtitle, size=14,
                      color=(0.784, 0.847, 0.910))
        page.rect(_MARGIN + 12, PDF_HEIGHT / 2 + 10, 90, 3,
                  fill=(0.561, 0.714, 0.847))
        cursor = PDF_HEIGHT / 2 - 16
        for block in slide.blocks:
            if block.kind == "text":
                for line in block.payload:
                    page.text(_MARGIN + 12, cursor, line, size=10,
                              color=(0.859, 0.902, 0.941), max_width=width - 24)
                    cursor -= 16
        return

    page.text(_MARGIN, PDF_HEIGHT - _MARGIN - 18, slide.title, size=21, bold=True,
              color=_INK, max_width=width)
    cursor = PDF_HEIGHT - _MARGIN - 34
    if slide.subtitle:
        page.text(_MARGIN, cursor, slide.subtitle, size=9.5, color=_MUTED,
                  max_width=width)
        cursor -= 12
    page.rect(_MARGIN, cursor - 6, 56, 2.5, fill=_ACCENT)
    cursor -= 20

    floor = _MARGIN + 20
    gap = 20.0
    columns = {"half": 2, "third": 3}
    pending: List = []

    def flush_row() -> None:
        """Les blocs d'une meme rangee occupent la meme bande verticale."""
        nonlocal cursor
        if not pending:
            return
        count = columns.get(pending[0].width, 1)
        column_width = (width - gap * (count - 1)) / count
        used = 0.0
        for index, block in enumerate(pending[:count]):
            left = _MARGIN + index * (column_width + gap)
            top = cursor
            if block.title:
                page.text(left, top - 8, block.title.upper(), size=6.5, color=_MUTED)
                top -= 15
            used = max(used, cursor - top + _draw_block(
                block, left, top, column_width, top - floor))
        cursor -= used
        pending.clear()

    def _draw_block(block: Block, left: float, top: float,
                    block_width: float, room: float) -> float:
        if block.kind == "kpis":
            return _draw_kpis(page, block.payload, left, top, block_width)
        if block.kind == "table":
            return _draw_table(page, block.payload, left, top, block_width, room)
        if block.kind == "chart":
            spec = block.payload
            # Un graphique seul sur sa page occupe la hauteur disponible ;
            # place a cote d'un tableau, il reste dans une bande raisonnable.
            cap = spec.get("height") or _PDF_CHART_HEIGHTS.get(
                spec["type"], _PDF_CHART_HEIGHTS["scatter"])[block.width]
            # La hauteur ne depasse jamais la place restante : un plancher
            # de cent vingt points faisait deborder la boite a moustaches
            # sous le filet de pied de page, ou le lecteur recevait un
            # trace coupe et une legende posee dans la marge.
            height = min(room - 8, cap)
            if spec["type"] == "histogram":
                return _draw_histogram(page, spec["bins"], currency, left, top,
                                       block_width, height)
            if spec["type"] == "pyramid":
                return _draw_pyramid(page, spec["rows"], left, top,
                                     block_width, height,
                                     label=spec.get("label", ""))
            if spec["type"] == "boxplot":
                return _draw_boxplot(page, spec["salary"], currency, left, top,
                                     block_width, height)
            if spec["type"] == "donut":
                return _draw_donut(page, spec["parts"], left, top,
                                   block_width, height,
                                   label=spec.get("label", ""),
                                   total=spec.get("total"))
            return _draw_scatter(page, spec["dataset"], currency, left, top,
                                 block_width, height)
        if block.kind == "legend":
            return _draw_legend(page, block.payload, left, top, block_width)
        if block.kind == "note":
            return _draw_note(page, block.payload, left, top, block_width) if block.payload else 0.0
        if block.kind == "text":
            used = 0.0
            for line in block.payload:
                page.text(left, top - used - 9, line, size=9, color=_MUTED,
                          max_width=block_width)
                used += 15
            return used
        return 0.0

    for block in slide.blocks:
        if block.width in columns:
            if pending and pending[0].width != block.width:
                flush_row()
            pending.append(block)
            if len(pending) == columns[block.width]:
                flush_row()
            continue
        flush_row()
        top = cursor
        if block.title:
            page.text(_MARGIN, top - 8, block.title.upper(), size=6.5, color=_MUTED)
            top -= 15
        used = _draw_block(block, _MARGIN, top, width, top - floor)
        cursor = top - used - 16
    flush_row()

    # Le pied ne porte que la pagination. Le nom de l'outil et sa version
    # appartiennent au manifeste, ecrit a cote des documents : un document
    # remis a un CSE ou a une direction parle de la population, pas du
    # logiciel qui l'a mise en page.
    page.line(_MARGIN, _MARGIN + 6, PDF_WIDTH - _MARGIN, _MARGIN + 6,
              color=_LINE, width=0.4)
    page.text(PDF_WIDTH - _MARGIN, _MARGIN - 6, f"{number} / {total}", size=7,
              color=_MUTED, align="right")


def write_slides_pdf(slides: Sequence[Slide], analysis: Dict[str, Any],
                     path: str) -> str:
    """Ecrit le jeu de slides en PDF paysage, sans navigateur ni dependance."""
    use(analysis)
    from ..io.pdf_writer import Document

    currency = analysis.get("salary", {}).get("currency", "EUR")
    document = Document(PDF_WIDTH, PDF_HEIGHT)
    for number, slide in enumerate(slides, start=1):
        _draw_slide(document.add_page(), slide, number, len(slides), currency)
    return document.save(path)
