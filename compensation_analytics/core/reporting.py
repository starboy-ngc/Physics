"""Restitution HTML autoportante.

Contraintes respectees : aucun appel reseau, aucune police distante, aucune
bibliotheque JavaScript externe. Les graphiques sont du SVG genere cote
moteur ; le fichier produit s'ouvre hors ligne dans le navigateur du poste et
s'imprime en PDF via la fonction d'impression standard (aucun binaire tiers).
"""

from __future__ import annotations

import datetime as _dt
import html
import os
from typing import Any, Dict, List, Optional, Sequence

from ..version import ENGINE_NAME, __version__
from . import palette
from .axes import nice_ticks

#: Palette du document en cours de rendu. `use()` la fixe au debut de chaque
#: rendu, a partir du theme porte par l'analyse. Un document se rend d'un
#: seul tenant, du premier caractere au dernier : il n'y a jamais deux
#: rendus en cours, et les fonctions de trace la lisent sans se la passer de
#: main en main sur quinze signatures.
ACTIVE: palette.Palette = palette.by_name(palette.DEFAULT_THEME)


def use(analysis) -> palette.Palette:
    """Fixe la palette du rendu qui commence."""
    global ACTIVE, _PALETTE
    ACTIVE = palette.from_analysis(analysis)
    _PALETTE = list(ACTIVE.series)
    return ACTIVE


_PALETTE = list(ACTIVE.series)


def _variables() -> str:
    """Les couleurs du theme, en variables CSS.

    Seule cette ligne depend du theme : le reste de la feuille de style
    ne nomme plus une seule teinte, il ne cite que ces variables — les
    traces SVG compris.
    """
    pairs = (
        ("ink", ACTIVE.ink), ("muted", ACTIVE.muted), ("faint", ACTIVE.faint),
        ("line", ACTIVE.line), ("line-strong", ACTIVE.line_strong),
        ("grid", ACTIVE.grid), ("bg", ACTIVE.canvas), ("panel", ACTIVE.panel),
        ("stripe", ACTIVE.stripe), ("accent", ACTIVE.accent),
        ("warn", ACTIVE.warn), ("warn-bg", ACTIVE.warn_soft),
        ("crit", ACTIVE.crit), ("crit-bg", ACTIVE.crit_soft),
        ("female", ACTIVE.female), ("male", ACTIVE.male),
    )
    return ":root{" + ";".join(f"--{name}:{value}" for name, value in pairs) + "}"


def _css() -> str:
    """Feuille de style complete : les variables du theme, puis la mise en page."""
    return _variables() + _CSS


_CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 "Segoe UI",Calibri,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:32px 24px 64px}
header{border-bottom:2px solid var(--accent);padding-bottom:16px;margin-bottom:28px}
h1{font-size:24px;margin:0 0 4px}
h2{font-size:17px;margin:36px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:14px;margin:20px 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.meta{color:var(--muted);font-size:12px}
.kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:12px 14px}
.kpi .label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.kpi .value{font-size:20px;font-weight:600;margin-top:4px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:7px 10px;text-align:right}
th:first-child,td:first-child{text-align:left}
thead th{background:var(--panel);font-weight:600;color:var(--muted);text-transform:uppercase;font-size:11px;letter-spacing:.04em}
tbody tr:hover{background:var(--stripe)}
.scroll{overflow-x:auto}
.note{border-left:3px solid var(--accent);background:var(--panel);padding:10px 14px;margin:12px 0;font-size:13px}
.note.warn{border-color:var(--warn);background:var(--warn-bg);color:var(--warn)}
.note.crit{border-color:var(--crit);background:var(--crit-bg);color:var(--crit)}
.legend{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0;font-size:12px}
.legend span{display:inline-flex;align-items:center;gap:5px}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
figure{margin:0 0 8px}
svg{max-width:100%;height:auto;background:var(--bg);border:1px solid var(--line);border-radius:6px}
footer{margin-top:48px;padding-top:14px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}
@media print{.wrap{max-width:none;padding:0}h2{page-break-after:avoid}figure,table{page-break-inside:avoid}}
"""

# Interaction minimale : survol des points du nuage. Aucun code externe.
_JS = """
(function(){
  var tip=document.createElement('div');
  tip.style.cssText='position:fixed;display:none;background:var(--ink);color:var(--bg);padding:6px 9px;'+
    'border-radius:4px;font:12px/1.4 Segoe UI,Arial,sans-serif;pointer-events:none;z-index:9';
  document.body.appendChild(tip);
  document.addEventListener('mouseover',function(e){
    var t=e.target;
    if(!t||!t.getAttribute||!t.getAttribute('data-tip'))return;
    tip.textContent=t.getAttribute('data-tip');
    tip.style.display='block';
    tip.style.left=(e.clientX+14)+'px';
    tip.style.top=(e.clientY+14)+'px';
  });
  document.addEventListener('mouseout',function(e){
    if(e.target&&e.target.getAttribute&&e.target.getAttribute('data-tip'))tip.style.display='none';
  });
})();
"""


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def format_money(value: Optional[float], currency: str = "EUR") -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}".replace(",", " ") + f" {currency}"


def format_number(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


def format_years(value: Optional[float], suffix: bool = True) -> str:
    """Une duree en annees s'ecrit sans decimale.

    « 8,0 ans » affiche une precision que la donnee n'a pas, et « 9,4 ans »
    une precision que personne n'emploie : une anciennete se compte en
    annees. La regle vaut pour l'ecran comme pour les documents, d'ou ce
    formateur unique.

    `suffix` se desactive dans une colonne de tableau, ou l'unite est deja
    portee par l'en-tete : la regle d'arrondi, elle, reste la meme.
    """
    if value is None:
        return "—"
    return f"{format_number(value, 0)} ans" if suffix else format_number(value, 0)


def format_percent(value: Optional[float]) -> str:
    return "—" if value is None else f"{value:.1f} %".replace(".", ",")


def _kpi(label: str, value: str) -> str:
    return f'<div class="kpi"><div class="label">{_e(label)}</div><div class="value">{_e(value)}</div></div>'


def _note(text: Optional[str], kind: str = "") -> str:
    if not text:
        return ""
    css = f"note {kind}".strip()
    return f'<div class="{css}">{_e(text)}</div>'


def _table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    head = "".join(f"<th>{_e(item)}</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_e(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


# ------------------------------------------------------------------ graphiques


def histogram_svg(bins: List[Dict[str, float]], currency: str,
                  width: int = 900, height: int = 300) -> str:
    if not bins:
        return ""
    pad_left, pad_bottom, pad_top, pad_right = 60, 46, 16, 16
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    peak = max(item["count"] for item in bins) or 1
    bar_w = plot_w / len(bins)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Distribution des rémunérations">']
    for value in nice_ticks(0, peak):
        y = pad_top + plot_h - value / peak * plot_h
        parts.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{pad_left - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="10" fill="var(--muted)">{value:.0f}</text>')
    for index, item in enumerate(bins):
        bar_h = plot_h * item["count"] / peak
        x = pad_left + index * bar_w
        y = pad_top + plot_h - bar_h
        tip = (f'{format_money(item["lower"], currency)} - {format_money(item["upper"], currency)} : '
               f'{int(item["count"])} salariés')
        parts.append(
            f'<rect x="{x + 1:.1f}" y="{y:.1f}" width="{max(bar_w - 2, 1):.1f}" '
            f'height="{bar_h:.1f}" fill="var(--accent)" opacity="0.85" data-tip="{_e(tip)}"/>'
        )
    low = bins[0]["lower"]
    high = bins[-1]["upper"]
    span = (high - low) or 1.0
    base_y = pad_top + plot_h
    parts.append(f'<line x1="{pad_left}" y1="{base_y}" x2="{width - pad_right}" y2="{base_y}" stroke="var(--line-strong)"/>')
    for value in nice_ticks(low, high, 5):
        x = pad_left + (value - low) / span * plot_w
        parts.append(f'<text x="{x:.1f}" y="{base_y + 18}" text-anchor="middle" font-size="11" fill="var(--muted)">{_e(format_money(value, currency))}</text>')
    parts.append(f'<text x="{pad_left}" y="{base_y + 34}" font-size="11" fill="var(--muted)">Effectif par classe de rémunération</text>')
    parts.append("</svg>")
    return "".join(parts)


def scatter_svg(dataset: Dict[str, Any], currency: str,
                width: int = 900, height: int = 420) -> str:
    points = dataset.get("points") or []
    if not points:
        return ""
    pad_left, pad_bottom, pad_top, pad_right = 70, 48, 16, 16
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    xs = [point["x"] for point in points]
    ys = [point["y"] for point in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_span = (x_max - x_min) or 1.0
    y_span = (y_max - y_min) or 1.0

    def to_x(value: float) -> float:
        return pad_left + (value - x_min) / x_span * plot_w

    def to_y(value: float) -> float:
        return pad_top + plot_h - (value - y_min) / y_span * plot_h

    groups = dataset.get("groups") or []
    colors = {group: _PALETTE[index % len(_PALETTE)] for index, group in enumerate(groups)}

    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Nuage de points ancienneté / rémunération">']
    # Graduations rondes, comme a l'ecran et dans le PDF : le meme graphique
    # doit se lire de la meme facon sur les trois supports.
    for value in nice_ticks(y_min, y_max):
        y = to_y(value)
        parts.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{pad_left - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="10" fill="var(--muted)">{_e(format_money(value, currency))}</text>')
    for value in nice_ticks(x_min, x_max):
        x = to_x(value)
        parts.append(f'<text x="{x:.1f}" y="{pad_top + plot_h + 18:.1f}" text-anchor="middle" font-size="10" fill="var(--muted)">{format_number(value, 0)}</text>')
    for point in points:
        color = colors.get(point["group"], ACTIVE.accent)
        tip = (f'{point["reference"]} | {point["group"]} | ancienneté '
               f'{format_years(point["x"])} | {format_money(point["y"], currency)}')
        parts.append(
            f'<circle cx="{to_x(point["x"]):.1f}" cy="{to_y(point["y"]):.1f}" r="3" '
            f'fill="{color}" opacity="0.7" data-tip="{_e(tip)}"/>'
        )
    trend = dataset.get("trend")
    if trend:
        y_start = trend["intercept"] + trend["slope"] * x_min
        y_end = trend["intercept"] + trend["slope"] * x_max
        y_start = min(max(y_start, y_min), y_max)
        y_end = min(max(y_end, y_min), y_max)
        parts.append(
            f'<line x1="{to_x(x_min):.1f}" y1="{to_y(y_start):.1f}" '
            f'x2="{to_x(x_max):.1f}" y2="{to_y(y_end):.1f}" '
            'stroke="var(--crit)" stroke-width="2" stroke-dasharray="6 4"/>'
        )
    parts.append(f'<text x="{pad_left}" y="{height - 8}" font-size="11" fill="var(--muted)">Ancienneté (années)</text>')
    parts.append("</svg>")
    return "".join(parts)


def _legend(dataset: Dict[str, Any]) -> str:
    groups = dataset.get("groups") or []
    if not groups or len(groups) > 14:
        return ""
    items = "".join(
        f'<span><i class="dot" style="background:{_PALETTE[index % len(_PALETTE)]}"></i>{_e(group)}</span>'
        for index, group in enumerate(groups)
    )
    label = dataset.get("color_label") or dataset.get("color_field", "")
    return f'<div class="legend"><strong>{_e(label)} :</strong>{items}</div>'


# ------------------------------------------------------------------- sections


def _quality_section(quality: Dict[str, Any]) -> str:
    status = quality.get("statut", "")
    kind = "crit" if status == "CORRECTIONS REQUISES" else ("warn" if status == "POINTS DE VIGILANCE" else "")
    kpis = "".join([
        _kpi("Lignes importées", f'{quality.get("lignes_importees", 0):,}'.replace(",", " ")),
        _kpi("Salariés uniques", f'{quality.get("salaries_uniques", 0):,}'.replace(",", " ")),
        _kpi("Doublons", str(quality.get("doublons", 0))),
        _kpi("Salaires manquants", str(quality.get("salaires_manquants", 0))),
        _kpi("Dates invalides", str(quality.get("dates_invalides", 0))),
        _kpi("Anomalies critiques", str(quality.get("anomalies_critiques", 0))),
    ])
    rows = [
        (item["severite"].capitalize(), item["message"], str(item["lignes_concernees"]))
        for item in quality.get("constats", [])
    ]
    table = _table(["Sévérité", "Constat", "Lignes"], rows) if rows else "<p>Aucun constat.</p>"
    return (
        f'<h2>1. Contrôle qualité des données</h2>'
        f'{_note("Statut : " + status, kind)}'
        f'<div class="kpis">{kpis}</div>'
        f'<h3>Detail des constats</h3>{table}'
    )


def _population_section(population: Dict[str, Any]) -> str:
    if population.get("masked"):
        return f'<h2>2. Population</h2>{_note(population.get("warning"), "warn")}'
    kpis = "".join([
        _kpi("Effectif", f'{population.get("headcount", 0):,}'.replace(",", " ")),
        _kpi("Âge moyen", format_years(population.get("age_mean"))),
        _kpi("Âge médian", format_years(population.get("age_median"))),
        _kpi("Ancienneté moyenne", format_years(population.get("tenure_mean"))),
        _kpi("Ancienneté médiane", format_years(population.get("tenure_median"))),
    ])
    age_rows = [
        (row["label"], str(row["count"]), format_percent(row["share"]))
        for row in population.get("age_bands", [])
    ]
    tenure_rows = [
        (row["label"], str(row["count"]), format_percent(row["share"]))
        for row in population.get("tenure_bands", [])
    ]
    return (
        "<h2>2. Population</h2>"
        f'{_note(population.get("warning"), "warn")}'
        f'<div class="kpis">{kpis}</div>'
        f"<h3>Répartition par tranche d'âge</h3>"
        f'{_table(["Tranche", "Effectif", "Part"], age_rows)}'
        f"<h3>Répartition par tranche d'ancienneté</h3>"
        f'{_table(["Tranche", "Effectif", "Part"], tenure_rows)}'
    )


def _salary_section(salary: Dict[str, Any]) -> str:
    currency = salary.get("currency", "EUR")
    if salary.get("masked"):
        return f"<h2>3. Rémunération</h2>{_note(salary.get('warning'), 'warn')}"
    kpis = "".join([
        _kpi("Masse salariale", format_money(salary.get("payroll"), currency)),
        _kpi("Salaire moyen", format_money(salary.get("mean"), currency)),
        _kpi("Salaire médian", format_money(salary.get("median"), currency)),
        _kpi("Minimum", format_money(salary.get("min"), currency)),
        _kpi("Maximum", format_money(salary.get("max"), currency)),
        _kpi("Couverture", format_percent(salary.get("coverage"))),
    ])
    percentile_rows = [
        (entry["label"], format_money(salary.get(entry["key"]), currency))
        for entry in salary.get("published_percentiles", [])
        if salary.get(entry["key"]) is not None
    ]
    dispersion = salary.get("dispersion", {}) or {}
    dispersion_rows = [
        ("Q3 - Q1", format_money(dispersion.get("interquartile_range"), currency)),
        ("Q3 / Q1", format_number(dispersion.get("q3_over_q1"), 2)),
        ("P90 / P10", format_number(dispersion.get("p90_over_p10"), 2)),
        ("Moyenne / Médiane", format_number(dispersion.get("mean_over_median"), 2)),
        ("Coefficient de variation", format_percent(
            None if dispersion.get("coefficient_of_variation") is None
            else dispersion["coefficient_of_variation"] * 100)),
    ]
    field_label = salary.get("field_label") or salary.get("field", "")
    technical_note = _note(
        "L'écart-type est disponible comme statistique technique ("
        + format_number(salary.get("std_dev"), 0)
        + ") mais n'est pas un indicateur de pilotage."
    )
    return (
        f"<h2>3. Rémunération — {_e(field_label)}</h2>"
        f'{_note(salary.get("warning"), "warn")}'
        f'<div class="kpis">{kpis}</div>'
        f'<h3>Percentiles</h3>{_table(["Indicateur", "Valeur"], percentile_rows)}'
        f'<h3>Dispersion</h3>{_table(["Indicateur", "Valeur"], dispersion_rows)}'
        f"{technical_note}"
    )


def _distribution_section(distribution: Dict[str, Any], currency: str) -> str:
    if not distribution.get("available"):
        return f"<h2>4. Distribution</h2>{_note(distribution.get('warning'), 'warn')}"
    chart = histogram_svg(distribution.get("bins", []), currency)
    outliers = distribution.get("outliers", [])
    highlighted = distribution.get("outliers_highlighted") or outliers
    # Colonnes derivees des dimensions declarees en configuration : les trois
    # premieres suffisent a situer le cas sans surcharger le tableau.
    shown = (distribution.get("dimension_labels") or [])[:3]
    rows = [
        tuple(
            [item["reference"]]
            + [str(item.get("dimensions", {}).get(entry["field"]) or "—")
               for entry in shown]
            + [
                format_years(item.get("tenure_years"), suffix=False),
                format_money(item["value"], currency),
                f'Position {item["position"]}',
            ]
        )
        for item in highlighted
    ]
    label = distribution.get("outlier_label", "Situation atypique à analyser")
    headers = (["Référence"] + [entry["label"] for entry in shown]
               + ["Ancienneté", "Rémunération", "Lecture"])
    table = _table(headers, rows) if rows else "<p>Aucune situation atypique détectée.</p>"
    if len(highlighted) < len(outliers):
        table += _note(
            f"Tableau limite aux {len(highlighted)} situations les plus "
            f"extrêmes sur {len(outliers)}. La liste complete figure dans "
            "l'export Excel."
        )
    return (
        "<h2>4. Distribution</h2>"
        f"<figure>{chart}</figure>"
        f"<h3>{_e(label)} ({len(outliers)})</h3>"
        f'{_note("Ces situations sont signalées par un critère statistique (méthode interquartile). Elles ne constituent pas un constat RH : elles doivent être analysées au regard du contexte (métier, marché, historique, performance).")}'
        f"{table}"
    )


def _scatter_section(dataset: Dict[str, Any], currency: str) -> str:
    if not dataset.get("available"):
        return f"<h2>5. Ancienneté et rémunération</h2>{_note(dataset.get('warning'), 'warn')}"
    commentary = ""
    return (
        "<h2>5. Ancienneté et rémunération</h2>"
        f'{_note(dataset.get("warning"), "warn")}'
        f"{_legend(dataset)}"
        f"<figure>{scatter_svg(dataset, currency)}</figure>"
        f"{commentary}"
    )


def _segments_section(segments: List[Dict[str, Any]], currency: str) -> str:
    if not segments:
        return ""
    blocks = ["<h2>6. Analyses par segment</h2>"]
    for segment in segments:
        rows = []
        for row in segment["rows"]:
            salary = row["salary"]
            if row["masked"]:
                rows.append((row["segment"], str(row["headcount"]),
                             "—", "—", "—", "—", "Masqué (effectif insuffisant)"))
                continue
            dispersion = salary.get("dispersion", {}) or {}
            rows.append((
                row["segment"], str(row["headcount"]),
                format_money(salary.get("mean"), currency),
                format_money(salary.get("median"), currency),
                format_money(salary.get("p25"), currency),
                format_money(salary.get("p75"), currency),
                format_number(dispersion.get("p90_over_p10"), 2),
            ))
        blocks.append(f'<h3>{_e(segment["label"])}</h3>')
        blocks.append(_table(
            ["Segment", "Effectif", "Moyenne", "Médiane", "Q1", "Q3", "P90/P10"], rows
        ))
        if segment.get("masked_segments"):
            blocks.append(_note(
                f'{segment["masked_segments"]} segment(s) masqué(s) : effectif '
                "inférieur au seuil de confidentialité paramètre.", "warn"))
    return "".join(blocks)


def _comparison_section(comparison: Optional[Dict[str, Any]], currency: str) -> str:
    if not comparison:
        return ""
    rows = []
    for row in comparison["rows"]:
        kind = row["kind"]
        if kind == "money":
            left, right = format_money(row["left"], currency), format_money(row["right"], currency)
        elif kind == "int":
            left, right = str(row["left"] or 0), str(row["right"] or 0)
        elif kind == "years":
            left, right = format_number(row["left"]), format_number(row["right"])
        else:
            left, right = format_number(row["left"], 2), format_number(row["right"], 2)
        rows.append((row["indicator"], left, right, format_percent(row["gap_percent"])))
    return (
        "<h2>7. Comparaison de populations</h2>"
        + _table([
            "Indicateur", comparison["left_label"], comparison["right_label"], "Écart"
        ], rows)
    )


def render_report(analysis: Dict[str, Any]) -> str:
    """Assemble la restitution complete en un fichier HTML autonome."""
    # Le theme est fixe avant le premier caractere : tout ce qui suit, mise
    # en page comme traces, lit la meme palette.
    use(analysis)
    manifest = analysis.get("manifest", {})
    currency = analysis.get("salary", {}).get("currency", "EUR")
    generated = manifest.get("date_analyse", _dt.datetime.now().isoformat(timespec="seconds"))
    title = analysis.get("title", "Analyse de rémunération")
    sections = [
        _quality_section(analysis.get("quality", {})),
        _population_section(analysis.get("population", {})),
        _salary_section(analysis.get("salary", {})),
        _distribution_section(analysis.get("distribution", {}), currency),
        _scatter_section(analysis.get("scatter", {}), currency),
        _segments_section(analysis.get("segments", []), currency),
        _comparison_section(analysis.get("comparison"), currency),
    ]
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(title)}</title>
<style>{_css()}</style>
</head>
<body>
<div class="wrap">
<header>
<h1>{_e(title)}</h1>
<div class="meta">
Fichier source : {_e(manifest.get("fichier_source", "—"))} &nbsp;·&nbsp;
Effectif analysé : {_e(manifest.get("effectif_analyse", "—"))} &nbsp;·&nbsp;
Filtres : {_e(manifest.get("filtres", "Aucun filtre"))} &nbsp;·&nbsp;
Généré le {_e(generated)}
</div>
</header>
{''.join(sections)}
<footer>
{_e(ENGINE_NAME)} v{_e(__version__)} — traitement local, hors ligne.
Empreinte du fichier source : {_e((manifest.get("empreinte_source") or "—")[:16])}.
Aucune donnée n'a quitté ce poste.
</footer>
</div>
<script>{_JS}</script>
</body>
</html>
"""


def write_report(analysis: Dict[str, Any], path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_report(analysis))
    return path
