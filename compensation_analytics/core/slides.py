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

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from ..version import ENGINE_NAME, __version__
from .reporting import (_PALETTE, format_money, format_number, format_percent,
                        histogram_svg, scatter_svg)

SLIDE_WIDTH = 1280
SLIDE_HEIGHT = 720


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
               compact: bool = False) -> Block:
    return Block("kpis",
                 {"items": [{"label": label, "value": value}
                            for label, value in pairs],
                  "compact": compact},
                 width=width)


def _table_block(headers, rows, title="", width="full", compact=False) -> Block:
    return Block("table",
                 {"headers": list(headers), "rows": [list(r) for r in rows],
                  "compact": compact},
                 title=title, width=width)


def _population_kpis(population: Dict[str, Any]) -> List[List[str]]:
    return [
        ["Effectif", f'{population.get("headcount", 0):,}'.replace(",", " ")],
        ["Âge moyen", format_number(population.get("age_mean")) + " ans"],
        ["Âge médian", format_number(population.get("age_median")) + " ans"],
        ["Ancienneté moyenne", format_number(population.get("tenure_mean")) + " ans"],
        ["Ancienneté médiane", format_number(population.get("tenure_median")) + " ans"],
    ]


def _salary_kpis(salary: Dict[str, Any], currency: str) -> List[List[str]]:
    return [
        ["Masse salariale", format_money(salary.get("payroll"), currency)],
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
            f'{ENGINE_NAME} v{__version__} — traitement local, hors ligne',
        ])],
    )


def _structure_rows(population: Dict[str, Any]) -> List[List[str]]:
    """Structure d'age et d'anciennete dans un seul tableau.

    Les deux series sont prefixees, ce qui evite deux blocs distincts et
    libere une colonne pour le graphique.
    """
    rows: List[List[str]] = []
    for prefix, key in (("Âge", "age_bands"), ("Anc.", "tenure_bands")):
        for row in population.get(key) or []:
            rows.append([f'{prefix} {row["label"]}', str(row["count"]),
                         format_percent(row["share"])])
    return rows


def build_summary(analysis: Dict[str, Any]) -> List[Slide]:
    """Fiche standard : une seule page paysage.

    Composition : un bandeau d'indicateurs, puis trois colonnes — niveaux de
    remuneration, structure de la population, et nuage anciennete x
    remuneration. Le nuage occupe une colonne plutot qu'une bande : il a
    besoin de hauteur pour que la dispersion verticale se lise.

    Les ratios de dispersion (Q3/Q1, P90/P10) n'y figurent pas : ils demandent
    une lecture experte et trouvent leur place dans le jeu de slides complet
    et dans l'export Excel.
    """
    salary = analysis.get("salary", {})
    population = analysis.get("population", {})
    currency = salary.get("currency", "EUR")
    manifest = analysis.get("manifest", {})

    blocks: List[Block] = [
        _kpi_block(
            [["Effectif", f'{population.get("headcount", 0):,}'.replace(",", " ")],
             ["Masse salariale", format_money(salary.get("payroll"), currency)],
             ["Salaire moyen", format_money(salary.get("mean"), currency)],
             ["Salaire médian", format_money(salary.get("median"), currency)],
             ["Âge médian", format_number(population.get("age_median")) + " ans"],
             ["Ancienneté médiane",
              format_number(population.get("tenure_median")) + " ans"]]
        ),
        _table_block(["Percentile", "Valeur"], _percentile_rows(salary, currency),
                     title="Niveaux de rémunération", width="third", compact=True),
        _table_block(["Structure", "Effectif", "Part"], _structure_rows(population),
                     title="Structure de la population", width="third", compact=True),
    ]

    scatter = analysis.get("scatter", {})
    distribution = analysis.get("distribution", {})
    if scatter.get("available"):
        # Le R2 est deja porte par le graphique : ne pas le repeter dans le
        # titre du bloc.
        blocks.append(Block(
            "chart", {"type": "scatter", "dataset": scatter, "height": 345},
            title="Ancienneté et rémunération", width="third"))
    elif distribution.get("available"):
        # Repli : sous le seuil d'effectif, le nuage est desactive mais la
        # distribution reste publiable.
        blocks.append(Block(
            "chart", {"type": "histogram", "bins": distribution.get("bins", []),
                      "height": 345},
            title="Distribution des rémunérations", width="third"))
    elif scatter.get("warning"):
        blocks.append(Block("note", scatter["warning"], width="third"))

    if salary.get("warning"):
        blocks.append(Block("note", salary["warning"]))

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


def build_deck(analysis: Dict[str, Any]) -> List[Slide]:
    """Vision complete : un jeu de slides, une idee par page."""
    salary = analysis.get("salary", {})
    population = analysis.get("population", {})
    quality = analysis.get("quality", {})
    currency = salary.get("currency", "EUR")
    slides: List[Slide] = [_cover(analysis)]

    # Qualite des donnees
    constats = [
        [item["severite"].capitalize(), item["message"],
         str(item["lignes_concernees"])]
        for item in quality.get("constats", [])[:8]
    ]
    quality_slide = Slide("Qualité des données", f'Statut : {quality.get("statut", "")}')
    quality_slide.blocks = [
        _kpi_block([
            ["Lignes importées", f'{quality.get("lignes_importees", 0):,}'.replace(",", " ")],
            ["Salariés uniques", f'{quality.get("salaries_uniques", 0):,}'.replace(",", " ")],
            ["Doublons", str(quality.get("doublons", 0))],
            ["Salaires manquants", str(quality.get("salaires_manquants", 0))],
            ["Dates invalides", str(quality.get("dates_invalides", 0))],
            ["Anomalies critiques", str(quality.get("anomalies_critiques", 0))],
        ]),
    ]
    if constats:
        quality_slide.blocks.append(
            _table_block(["Sévérité", "Constat", "Lignes"], constats))
    slides.append(quality_slide)

    # Population
    if not population.get("masked"):
        slides.append(Slide("Population", "Structure d'âge et d'ancienneté", blocks=[
            _kpi_block(_population_kpis(population)),
            _table_block(["Tranche d'âge", "Effectif", "Part"],
                         [[row["label"], str(row["count"]), format_percent(row["share"])]
                          for row in population.get("age_bands", [])],
                         title="Âge", width="half"),
            _table_block(["Ancienneté", "Effectif", "Part"],
                         [[row["label"], str(row["count"]), format_percent(row["share"])]
                          for row in population.get("tenure_bands", [])],
                         title="Ancienneté", width="half"),
        ]))

    # Remuneration
    if not salary.get("masked"):
        slides.append(Slide("Rémunération",
                            f'Champ analyse : {salary.get("field_label") or salary.get("field", "")}',
                            blocks=[
            _kpi_block(_salary_kpis(salary, currency)),
            _table_block(["Percentile", "Valeur"], _percentile_rows(salary, currency),
                         title="Percentiles", width="half"),
            _table_block(["Indicateur", "Valeur"], _dispersion_rows(salary, currency),
                         title="Dispersion", width="half"),
        ]))

    # Distribution
    distribution = analysis.get("distribution", {})
    if distribution.get("available"):
        slides.append(Slide("Distribution des rémunérations", blocks=[
            Block("chart", {"type": "histogram", "bins": distribution.get("bins", [])}),
        ]))
        outliers = distribution.get("outliers", [])
        highlighted = (distribution.get("outliers_highlighted") or outliers)[:10]
        if outliers:
            shown = (distribution.get("dimension_labels") or [])[:3]
            headers = (["Référence"] + [entry["label"] for entry in shown]
                       + ["Ancienneté", "Rémunération", "Lecture"])
            rows = [
                [item["reference"]]
                + [str(item.get("dimensions", {}).get(entry["field"]) or "—")
                   for entry in shown]
                + [format_number(item.get("tenure_years")),
                   format_money(item["value"], currency),
                   f'Position {item["position"]}']
                for item in highlighted
            ]
            slides.append(Slide(
                distribution.get("outlier_label", "Situations atypiques"),
                f'{len(outliers)} situations repérées — '
                f'{len(highlighted)} cas les plus extrêmes',
                blocks=[
                    Block("note", "Repéré par un critère statistique, pas par un "
                                  "jugement RH. A analyser au regard du contexte "
                                  "(marché, métier, historique, performance)."),
                    _table_block(headers, rows),
                ]))

    # Anciennete x remuneration
    scatter = analysis.get("scatter", {})
    if scatter.get("available"):
        trend = scatter.get("trend")
        subtitle = ""
        if trend:
            subtitle = (f'Tendance : {format_money(trend["slope"], currency)} par année '
                        f'd\'ancienneté — R2 = {trend["r_squared"]:.3f}')
        blocks = [Block("legend", scatter), Block("chart", {"type": "scatter",
                                                            "dataset": scatter})]
        if scatter.get("warning"):
            blocks.insert(0, Block("note", scatter["warning"]))
        slides.append(Slide("Ancienneté et rémunération", subtitle, blocks=blocks))

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
        if segment.get("masked_segments"):
            slide.blocks.append(Block(
                "note", f'{segment["masked_segments"]} segment(s) masqué(s) : '
                        "effectif sous le seuil de confidentialité."))
        slides.append(slide)

    # Comparaison
    comparison = analysis.get("comparison")
    if comparison:
        rows = []
        for row in comparison["rows"]:
            kind = row["kind"]
            if kind == "money":
                left = format_money(row["left"], currency)
                right = format_money(row["right"], currency)
            elif kind == "int":
                left, right = str(row["left"] or 0), str(row["right"] or 0)
            elif kind == "years":
                left, right = format_number(row["left"]), format_number(row["right"])
            else:
                left, right = format_number(row["left"], 2), format_number(row["right"], 2)
            rows.append([row["indicator"], left, right,
                         format_percent(row["gap_percent"])])
        slides.append(Slide("Comparaison de populations", blocks=[_table_block(
            ["Indicateur", comparison["left_label"], comparison["right_label"], "Écart"],
            rows)]))

    # Methodologie
    manifest = analysis.get("manifest", {})
    slides.append(Slide("Méthodologie et traçabilité", kind="closing", blocks=[
        Block("text", [
            f'Moteur : {manifest.get("moteur", ENGINE_NAME)} v{manifest.get("version", __version__)}',
            f'Date d\'analyse : {manifest.get("date_analyse", "—")}',
            f'Fichier source : {manifest.get("fichier_source", "—")}',
            f'Empreinte SHA-256 : {(manifest.get("empreinte_source") or "—")[:32]}...',
            f'Périmètre : {manifest.get("filtres", "Aucun filtre")}',
            "Percentiles : méthode inclusive à interpolation linéaire, "
            "identique a PERCENTILE.INCLUSIVE d'Excel.",
            "Situations atypiques : méthode interquartile (Tukey).",
            "Les résultats portant sur un effectif insuffisant sont masqués.",
            "Traitement local et hors ligne : aucune donnée n'a quitté ce poste.",
        ]),
    ]))
    return slides


# ----------------------------------------------------------------- rendu HTML

_SLIDE_CSS = """
:root{--ink:#1b2733;--muted:#5d6b7a;--line:#d9e0e7;--panel:#f5f7f9;--accent:#2f5d8a;
--warn:#8a5a12;--warn-bg:#fdf3e0}
*{box-sizing:border-box}
body{margin:0;background:#e8ecf0;color:var(--ink);
font:15px/1.45 "Segoe UI",Calibri,Arial,sans-serif}
.deck{display:flex;flex-direction:column;align-items:center;gap:20px;padding:24px}
/* La page garde une geometrie fixe (1280x720) : c'est ce qui garantit que
   l'ecran, l'impression et le PDF montrent exactement la meme chose. Pour
   tenir sur un ecran plus etroit, elle est mise à l'echelle plutot que
   reagencee. `--slide-scale` est calculé au chargement et au redimensionnement ;
   sans JavaScript il vaut 1 et le comportement est celui d'avant. */
.frame{width:100%;max-width:1280px;height:calc(720px * var(--slide-scale,1));
overflow:hidden}
.slide{position:relative;width:1280px;height:720px;background:#fff;
transform:scale(var(--slide-scale,1));transform-origin:top left;
border:1px solid var(--line);border-radius:4px;padding:44px 56px 56px;
display:flex;flex-direction:column;overflow:hidden}
.slide h1{font-size:34px;margin:0 0 6px;font-weight:600}
.slide .sub{color:var(--muted);font-size:16px;margin-bottom:22px}
.slide.cover{justify-content:center;background:linear-gradient(135deg,#2f5d8a,#24486b);
color:#fff;border:none}
.slide.cover h1{font-size:46px;max-width:80%}
.slide.cover .sub{color:#c8d8e8;font-size:22px;margin-bottom:34px}
.slide.cover .lines div{color:#dbe6f0;font-size:15px;margin-bottom:7px}
.rule{height:3px;width:90px;background:var(--accent);margin-bottom:20px}
.slide.cover .rule{background:#8fb6d8;width:120px}
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
.kpi{flex:1;background:var(--panel);border:1px solid var(--line);border-radius:6px;
padding:14px 16px}
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
.note{border-left:3px solid #c9922f;background:var(--warn-bg);color:var(--warn);
padding:10px 14px;font-size:13px;width:100%}
.lines div{margin-bottom:6px;color:var(--muted);font-size:14px}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:13px;width:100%}
.legend span{display:inline-flex;align-items:center;gap:5px}
.dot{width:10px;height:10px;border-radius:50%}
svg{display:block;width:100%;height:auto}
.chart-fit{min-height:0}
.pagenum{position:absolute;right:56px;bottom:22px;color:var(--muted);font-size:12px}
.slide.cover .pagenum{color:#9dbad6}
.hint{position:fixed;left:50%;transform:translateX(-50%);bottom:14px;
background:#1b2733;color:#fff;padding:7px 14px;border-radius:16px;font-size:12px;
opacity:.85}
@media print{
  @page{size:1280px 720px;margin:0}
  body{background:#fff}
  .deck{padding:0;gap:0}
  .hint{display:none}
  /* A l'impression, la page reprend sa taille reelle : la mise à l'echelle
     d'ecran ne doit jamais alterer le rendu papier ni le PDF. */
  :root{--slide-scale:1 !important}
  .frame{width:1280px;height:720px;max-width:none}
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
  tip.style.cssText='position:fixed;display:none;background:#1b2733;color:#fff;'+
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


def _render_block(block: Block, currency: str) -> str:
    title = (f'<div class="block-title">{_html_escape(block.title)}</div>'
             if block.title else "")
    if block.kind == "kpis":
        cells = "".join(
            f'<div class="kpi"><div class="label">{_html_escape(item["label"])}</div>'
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
        default = {"full": 330, "half": 260, "third": 200}[block.width]
        height = spec.get("height", default if spec["type"] == "histogram"
                          else {"full": 430, "half": 300, "third": 220}[block.width])
        if spec["type"] == "histogram":
            svg = histogram_svg(spec["bins"], currency, width=canvas, height=height)
        else:
            svg = scatter_svg(spec["dataset"], currency, width=canvas, height=height)
        # `chart-fit` borne le graphique a la place restante : une hauteur mal
        # estimee ne peut plus deborder du bas de la page.
        return f'<div class="{block.width} chart-fit">{title}{svg}</div>'
    if block.kind == "legend":
        dataset = block.payload
        groups = dataset.get("groups") or []
        if not groups or len(groups) > 14:
            return ""
        items = "".join(
            f'<span><i class="dot" style="background:'
            f'{_PALETTE[i % len(_PALETTE)]}"></i>{_html_escape(g)}</span>'
            for i, g in enumerate(groups)
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
<style>{_SLIDE_CSS}</style>
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
    return path


# ------------------------------------------------------------------ rendu PDF

# A4 paysage : le format le plus sur a l'impression et a la projection.
PDF_WIDTH, PDF_HEIGHT = 841.89, 595.28
_MARGIN = 38.0

_INK = (0.106, 0.153, 0.200)
_MUTED = (0.365, 0.420, 0.478)
_ACCENT = (0.184, 0.365, 0.541)
_LINE = (0.851, 0.878, 0.906)
_PANEL = (0.961, 0.969, 0.976)
_WARN = (0.541, 0.353, 0.071)
_WARN_BG = (0.992, 0.953, 0.878)
_WHITE = (1.0, 1.0, 1.0)


def _rgb(hex_color: str) -> tuple:
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


_PDF_PALETTE = [_rgb(color) for color in _PALETTE]


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
        page.rect(left, y - height, cell, height, fill=_PANEL, stroke=_LINE)
        page.text(left + 9, y - label_y, str(item["label"]).upper(),
                  size=label_size, color=_MUTED, max_width=cell - 18)
        page.text(left + 9, y - value_y, str(item["value"]), size=value_size,
                  bold=True, color=_INK, max_width=cell - 18)
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
    for step in range(5):
        level = base + plot_height * step / 4
        page.line(x, level, x + width, level, color=_LINE, width=0.4)
        page.text(x - 5, level - 2.5, f"{peak * step / 4:.0f}", size=6.5,
                  color=_MUTED, align="right")
    for index, item in enumerate(bins):
        bar = plot_height * item["count"] / peak
        page.rect(x + index * bar_width + 0.8, base, max(bar_width - 1.6, 0.5), bar,
                  fill=_ACCENT)
    page.line(x, base, x + width, base, color=_MUTED, width=0.5)
    page.text(x, base - 12, format_money(bins[0]["lower"], currency), size=7,
              color=_MUTED)
    page.text(x + width, base - 12, format_money(bins[-1]["upper"], currency),
              size=7, color=_MUTED, align="right")
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

    for step in range(5):
        level = base + plot_height * step / 4
        page.line(x, level, x + width, level, color=_LINE, width=0.4)
        page.text(x - 5, level - 2.5,
                  format_money(y_min + y_span * step / 4, currency),
                  size=6.5, color=_MUTED, align="right")
    groups = dataset.get("groups") or []
    colors = {group: _PDF_PALETTE[index % len(_PDF_PALETTE)]
              for index, group in enumerate(groups)}
    for point in points:
        page.circle(to_x(point["x"]), to_y(point["y"]), 1.8,
                    colors.get(point["group"], _ACCENT), alpha_state="GA")
    trend = dataset.get("trend")
    if trend:
        start = min(max(trend["intercept"] + trend["slope"] * x_min, y_min), y_max)
        end = min(max(trend["intercept"] + trend["slope"] * x_max, y_min), y_max)
        page.line(to_x(x_min), to_y(start), to_x(x_max), to_y(end),
                  color=(0.690, 0.271, 0.247), width=1.4, dash=(5, 3))
        page.text(x + width, base + plot_height - 9,
                  f'R2 = {trend["r_squared"]:.3f}', size=8,
                  color=(0.690, 0.271, 0.247), align="right")
    for step in range(6):
        value = x_min + x_span * step / 5
        page.text(x + width * step / 5, base - 12, format_number(value, 1),
                  size=6.5, color=_MUTED, align="center")
    # Le titre d'axe est place sous les graduations, pas a leur hauteur :
    # il chevauchait la premiere valeur.
    page.text(x + width / 2, base - 23, "Ancienneté (années)", size=7,
              color=_MUTED, align="center")
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
    for index, group in enumerate(groups):
        entry = str(group)
        needed = _width(entry, 7.5) + 20
        if cursor + needed > x + width:
            break
        page.circle(cursor + 3, line_y + 2.5, 3,
                    _PDF_PALETTE[index % len(_PDF_PALETTE)])
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
            cap = spec.get("height") or {"full": 420, "half": 250,
                                         "third": 200}[block.width]
            height = max(min(room - 8, cap), 120)
            if spec["type"] == "histogram":
                return _draw_histogram(page, spec["bins"], currency, left, top,
                                       block_width, height)
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

    page.line(_MARGIN, _MARGIN + 6, PDF_WIDTH - _MARGIN, _MARGIN + 6,
              color=_LINE, width=0.4)
    page.text(_MARGIN, _MARGIN - 6, f"{ENGINE_NAME} v{__version__}", size=7,
              color=_MUTED)
    page.text(PDF_WIDTH - _MARGIN, _MARGIN - 6, f"{number} / {total}", size=7,
              color=_MUTED, align="right")


def write_slides_pdf(slides: Sequence[Slide], analysis: Dict[str, Any],
                     path: str) -> str:
    """Ecrit le jeu de slides en PDF paysage, sans navigateur ni dependance."""
    from ..io.pdf_writer import Document

    currency = analysis.get("salary", {}).get("currency", "EUR")
    document = Document(PDF_WIDTH, PDF_HEIGHT)
    for number, slide in enumerate(slides, start=1):
        _draw_slide(document.add_page(), slide, number, len(slides), currency)
    return document.save(path)
