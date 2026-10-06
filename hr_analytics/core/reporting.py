"""Restitution HTML autoportante.

Contraintes respectees : aucun appel reseau, aucune police distante, aucune
bibliotheque JavaScript externe. Les graphiques sont du SVG genere cote
moteur ; le fichier produit s'ouvre hors ligne dans le navigateur du poste et
s'imprime en PDF via la fonction d'impression standard (aucun binaire tiers).
"""

from __future__ import annotations

import datetime as _dt
import html
import math
import os
from typing import Any, Dict, List, Optional, Sequence

from ..version import ENGINE_NAME, __version__
from . import palette
from .axes import nice_ticks
from ..io import restrict_to_owner

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
        ("accent-deep", ACTIVE.accent_deep),
        ("accent-soft", ACTIVE.accent_soft),
        # Le fond sur lequel la feuille est posee, et le texte secondaire
        # du bandeau colore : deux teintes deduites du theme, pour que le
        # document entier suive la couleur choisie.
        ("deck", palette.mix(ACTIVE.ink, palette.WHITE, 0.92)),
        ("header-soft", palette.mix(ACTIVE.accent, palette.WHITE, 0.72)),
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
body{margin:0;background:var(--deck);color:var(--ink);
font:14px/1.55 "Segoe UI",Calibri,Arial,sans-serif;
-webkit-font-smoothing:antialiased}

/* La page est une feuille posee sur un fond : elle a un bord, et le bord
   dit ou elle s'arrete. Sans lui, le document flottait d'un cote a l'autre
   de l'ecran sans qu'on sache ce qui en faisait partie. */
.wrap{max-width:1140px;margin:28px auto;background:var(--bg);
border:1px solid var(--line);border-radius:10px;overflow:hidden}

/* --- bandeau de tete ---------------------------------------------------
   Il porte la couleur du theme sur toute sa largeur. C'est le seul aplat
   colore du document, et c'est ce qui lui donne un haut : la ou tout est
   blanc, l'oeil ne sait pas par ou commencer. */
header{background:linear-gradient(135deg,var(--accent),var(--accent-deep));
color:#fff;padding:30px 36px 26px}
h1{font-size:27px;margin:0 0 10px;font-weight:600;letter-spacing:-.01em}
.meta{display:flex;flex-wrap:wrap;gap:0 30px;font-size:12.5px;
color:var(--header-soft)}
.meta b{display:block;font-weight:600;color:#fff;font-size:13.5px;
margin-top:2px}

.corps{padding:4px 36px 40px}

/* Une section masquee : elle garde son titre et dit pourquoi elle est
   vide. Un document d'ou une section disparait sans un mot laisse son
   lecteur se demander s'il manque un chiffre. */
p.masque{margin:0 0 8px;padding:12px 14px;border-radius:6px;
background:var(--warn-bg);color:var(--warn);font-size:13px}

/* --- titres ------------------------------------------------------------
   Le numero de section est un jeton, pas un prefixe de texte : il se
   repere en descendant la page sans lire. */
h2{font-size:17.5px;margin:38px 0 16px;font-weight:600;
display:flex;align-items:center;gap:11px}
h2 .num{display:inline-flex;align-items:center;justify-content:center;
width:26px;height:26px;border-radius:7px;background:var(--accent-soft);
color:var(--accent-deep);font-size:13px;font-weight:700;flex:none}
h2::after{content:"";flex:1;height:1px;background:var(--line)}
h3{font-size:11.5px;margin:26px 0 9px;color:var(--faint);
text-transform:uppercase;letter-spacing:.09em;font-weight:600}

/* --- indicateurs -------------------------------------------------------
   Deux rangs : les quatre premiers portent la lecture, les suivants la
   completent. Tous de la meme taille, la page n'avait pas de sommet. */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));
gap:12px;margin-bottom:4px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:9px;
padding:14px 16px;position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;
background:var(--line-strong)}
.kpi .label{font-size:10.5px;color:var(--faint);text-transform:uppercase;
letter-spacing:.07em;font-weight:600}
.kpi .value{font-size:21px;font-weight:600;margin-top:5px;
font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.kpi.fort{background:var(--accent-soft);border-color:var(--accent-soft)}
.kpi.fort::before{background:var(--accent)}
.kpi.fort .value{color:var(--accent-deep);font-size:23px}
.kpi.fort .label{color:var(--accent-deep);opacity:.75}

/* --- tableaux ----------------------------------------------------------
   Chiffres en chasse fixe : une colonne de montants doit s'aligner sur
   l'unite, sinon on compare des longueurs au lieu de comparer des
   valeurs. */
table{border-collapse:separate;border-spacing:0;width:100%;font-size:13px}
th,td{padding:9px 12px;text-align:right}
th:first-child,td:first-child{text-align:left}
td{border-bottom:1px solid var(--grid);
font-variant-numeric:tabular-nums}
tbody tr:last-child td{border-bottom:none}
thead th{background:var(--panel);color:var(--faint);text-transform:uppercase;
font-size:10.5px;letter-spacing:.07em;font-weight:600;
border-bottom:1px solid var(--line);white-space:nowrap}
thead th:first-child{border-top-left-radius:8px}
thead th:last-child{border-top-right-radius:8px}
tbody tr:nth-child(even){background:var(--stripe)}
tbody tr:hover{background:var(--accent-soft)}
td:first-child{font-weight:500}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:9px}

/* --- la part, en barre -------------------------------------------------
   Une colonne de pourcentages se lit ligne a ligne ; une barre se lit
   d'un seul regard, et c'est la forme de la repartition qu'on cherche. */
.part{display:flex;align-items:center;justify-content:flex-end;gap:10px}
.part i{display:block;height:7px;border-radius:4px;background:var(--accent);
opacity:.85;flex:none;min-width:2px}
.part span{font-variant-numeric:tabular-nums;min-width:54px;text-align:right}
th:last-child,td:last-child{padding-right:16px}
.scroll table td:last-child{min-width:230px}

figure{margin:0 0 10px}
svg{max-width:100%;height:auto;background:var(--bg);
border:1px solid var(--line);border-radius:9px}
.legend{display:flex;flex-wrap:wrap;gap:8px 14px;margin:12px 0;font-size:12px;
color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}

footer{margin:0;padding:18px 36px 22px;border-top:1px solid var(--line);
background:var(--panel);color:var(--faint);font-size:11px}

@media print{
  body{background:#fff}
  .wrap{max-width:none;margin:0;border:none;border-radius:0}
  header{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .kpi,.part i,h2 .num,thead th{-webkit-print-color-adjust:exact;
  print-color-adjust:exact}
  h2{page-break-after:avoid}
  figure,table,.kpis{page-break-inside:avoid}
}
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


def comparison_rows(comparison: Dict[str, Any], currency: str) -> List[List[str]]:
    """Lignes d'une comparaison de populations, mises en forme.

    La regle vit ici et non dans chaque restitution : la meme comparaison
    doit se lire a l'identique dans le rapport et dans les slides. Ecrite en
    double, l'ajout d'une nature de valeur par le moteur n'aurait ete
    honoree que d'un cote, et le meme fichier aurait produit deux tableaux
    differents selon le support.
    """
    mise_en_forme = {
        "money": lambda value: format_money(value, currency),
        "int": lambda value: str(value or 0),
        "years": format_number,
    }
    rows = []
    for row in comparison["rows"]:
        rendu = mise_en_forme.get(row["kind"],
                                  lambda value: format_number(value, 2))
        rows.append([row["indicator"], rendu(row["left"]), rendu(row["right"]),
                     format_percent(row["gap_percent"])])
    return rows


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


def format_percent(value: Optional[float], digits: int = 1) -> str:
    """Un pourcentage, a la precision demandee.

    Une decimale par defaut : un ecart de remuneration de 5,2 % ne se dit
    pas « 5 % ». Mais une part d'effectif, elle, se lit sans decimale — la
    precision affichee y suggere une exactitude que l'arrondi d'un
    comptage n'a pas.
    """
    return ("—" if value is None
            else f"{value:.{digits}f} %".replace(".", ","))


def _kpi(label: str, value: str, fort: bool = False) -> str:
    """Un indicateur. `fort` le met en avant.

    Tous de la meme taille, un bandeau d'indicateurs n'a pas de sommet :
    l'oeil se pose au hasard. Deux ou trois chiffres portent la lecture
    d'une section — l'effectif, la mediane, l'ecart —, et ce sont ceux-la
    qui prennent la couleur.
    """
    classe = "kpi fort" if fort else "kpi"
    return (f'<div class="{classe}"><div class="label">{_e(label)}</div>'
            f'<div class="value">{_e(value)}</div></div>')


#: Longueur de la plus grande barre d'un tableau, en pixels.
PART_PISTE = 150.0


def _part_cell(part: Optional[float], texte: str,
               sommet: float = 100.0) -> str:
    """Une part, en barre et en chiffre.

    Une colonne de pourcentages se lit ligne a ligne, en comparant des
    nombres de tete. La meme colonne en barres donne la forme de la
    repartition d'un seul regard — et le chiffre reste, pour qui veut la
    valeur exacte.

    L'echelle est celle de la plus grande part du tableau, non celle de
    cent pour cent. Une repartition dont le maximum est a quarante pour
    cent n'aurait occupe, sinon, que les deux cinquiemes de la place —
    des barres timides ou l'on cherche a nouveau les nombres.
    """
    if part is None:
        return f'<td><span>{_e(texte)}</span></td>'
    largeur = max(0.0, float(part)) / (sommet or 1.0) * PART_PISTE
    return (f'<td><div class="part">'
            f'<i style="width:{max(largeur, 2.0):.1f}px"></i>'
            f'<span>{_e(texte)}</span></div></td>')


def _table(headers: Sequence[str], rows: Sequence[Sequence[str]],
           parts: Optional[Sequence[Optional[float]]] = None,
           colonne_part: int = -1) -> str:
    """Un tableau. `parts` donne, ligne a ligne, la part a dessiner dans la
    colonne `colonne_part` — la derniere par defaut."""
    head = "".join(f"<th>{_e(item)}</th>" for item in headers)
    sommet = max([abs(float(part)) for part in (parts or [])
                  if part is not None] or [100.0])
    corps = []
    for rang, row in enumerate(rows):
        cellules = []
        index_part = colonne_part % len(row) if row else -1
        for colonne, cell in enumerate(row):
            if parts is not None and colonne == index_part:
                cellules.append(_part_cell(
                    parts[rang] if rang < len(parts) else None, str(cell),
                    sommet))
            else:
                cellules.append(f"<td>{_e(cell)}</td>")
        corps.append("<tr>" + "".join(cellules) + "</tr>")
    return (f'<div class="scroll"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(corps)}</tbody></table></div>')


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

    colors = palette.series_map(
        dataset.get("groups") or [], _PALETTE,
        other=dataset.get("other_label"), neutral="var(--muted)")

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
        modalite = point.get("group_label") or point["group"]
        tip = (f'{point["reference"]} | {modalite} | ancienneté '
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
    # Le titre de l'axe vient du jeu de donnees : les deux axes se
    # parametrent, et « Anciennete (annees) » ecrit en dur aurait annonce
    # une chose pendant que le dessin en montrait une autre.
    parts.append(f'<text x="{pad_left}" y="{height - 8}" font-size="11" '
                 f'fill="var(--muted)">{_e(axis_title(dataset, "x"))}</text>')
    parts.append("</svg>")
    return "".join(parts)


def pyramid_svg(rows: Sequence[Dict[str, Any]], width: int = 360,
                height: int = 240, label: str = "") -> str:
    """Pyramide femmes / hommes : deux ailes se rejoignant au centre.

    Les tranches se lisent a gauche et les effectifs en bout d'aile, comme
    a l'ecran : une pyramide dont les nombres sont au centre fait lire
    chaque ligne deux fois, une fois pour la tranche et une fois pour le
    chiffre, sans jamais les voir ensemble.

    Les deux ailes partagent la meme echelle, sinon la comparaison qui
    fait tout l'interet du dessin serait fausse.
    """
    rows = [row for row in (rows or []) if row.get("count")]
    if not rows:
        return ""
    gouttiere, bout = 86.0, 34.0
    aile = (width - gouttiere - 2 * bout - 10) / 2
    if aile <= 10:
        return ""
    # La legende ferme le dessin au lieu de l'ouvrir : en tete, elle
    # separait le titre de la premiere tranche ; en pied, elle se lit au
    # moment ou l'on demande laquelle des deux ailes est laquelle.
    haut = 4.0
    bas = 14.0 if label else 6.0
    ligne = max((height - haut - bas) / len(rows), 9.0)
    # La barre remplit sa tranche : quatre pixels separent sans eloigner,
    # et deux tranches voisines se comparent alors en masse plutot qu'en
    # longueur.
    barre = min(ligne - 4.0, 20.0)
    sommet = max(max(row.get("female", 0), row.get("male", 0))
                 for row in rows) or 1
    centre = gouttiere + bout + aile + 5
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="Pyramide {_e(label) or "des effectifs"}">']

    for index, row in enumerate(rows):
        y = haut + index * ligne
        milieu = y + ligne / 2
        parts.append(
            f'<text x="0" y="{milieu + 3:.1f}" font-size="9" '
            f'fill="var(--muted)">{_e(str(row.get("label", "")))}</text>')
        for cle, couleur, gauche in (("female", "var(--female)", True),
                                     ("male", "var(--male)", False)):
            valeur = int(row.get(cle, 0) or 0)
            longueur = aile * valeur / sommet
            if gauche:
                x = centre - 5 - longueur
                texte_x, ancrage = centre - 10 - longueur, "end"
            else:
                x = centre + 5
                texte_x, ancrage = centre + 10 + longueur, "start"
            if valeur:
                parts.append(
                    f'<rect x="{x:.1f}" y="{milieu - barre / 2:.1f}" '
                    f'width="{max(longueur, 1.0):.1f}" height="{barre:.1f}" '
                    f'fill="{couleur}" opacity="0.88"/>')
                parts.append(
                    f'<text x="{texte_x:.1f}" y="{milieu + 3:.1f}" '
                    f'text-anchor="{ancrage}" font-size="9" '
                    f'fill="var(--ink)">{valeur}</text>')
    parts.append(f'<line x1="{centre:.1f}" y1="{haut}" x2="{centre:.1f}" '
                 f'y2="{haut + len(rows) * ligne:.1f}" stroke="var(--line)"/>')
    if label:
        pied = haut + len(rows) * ligne + 10
        parts.append(
            f'<text x="{centre - 8:.1f}" y="{pied:.1f}" text-anchor="end" '
            f'font-size="9" fill="var(--female)">Femmes</text>'
            f'<text x="{centre + 8:.1f}" y="{pied:.1f}" text-anchor="start" '
            f'font-size="9" fill="var(--male)">Hommes</text>')
    parts.append("</svg>")
    return "".join(parts)


#: Rayon de l'anneau et de son trou, en parts de la hauteur disponible.
#: Le trou fait un peu moins des trois cinquiemes : plus etroit, l'anneau
#: redevient un disque ou l'effectif total n'a plus de place ; plus large,
#: les parts deviennent des filets ou l'oeil ne compare plus rien.
_DONUT_TROU = 0.58


def donut_svg(parts: Sequence[Dict[str, Any]], width: int = 360,
              height: int = 180, label: str = "",
              total: Optional[int] = None) -> str:
    """Repartition d'un effectif par modalite, en anneau.

    Le meme dessin qu'a l'ecran, et pour les memes raisons : un anneau
    plutot qu'un disque plein, parce que le centre rend l'effectif total
    qu'il faudrait sinon chercher ailleurs, et parce que deux parts se
    comparent sur leur arc dans les deux cas.

    La legende porte le nombre et la part. Lus dans le camembert ils se
    devinent ; ecrits, ils se citent — et c'est ce qu'on fait d'une
    repartition. Le dessin ne remplace donc pas le tableau qu'il
    remplace : il le range autrement.
    """
    parts = [item for item in (parts or []) if item.get("count")]
    if not parts:
        return ""
    effectif = total if total is not None else sum(int(item["count"])
                                                   for item in parts)
    if effectif <= 0:
        return ""
    ligne = 14.0
    # L'anneau prend la hauteur, la legende prend ce qui reste en largeur.
    rayon = min(height, max(height - 6.0, 0.0)) / 2.0 - 2.0
    rayon = min(rayon, (width - 150.0) / 2.0)
    if rayon < 24.0:
        return ""
    trou = rayon * _DONUT_TROU
    cx, cy = rayon + 3.0, height / 2.0
    colors = palette.series_map([str(item["label"]) for item in parts],
                                _PALETTE, neutral="var(--muted)")
    morceaux = [f'<svg viewBox="0 0 {width} {height}" role="img" '
                f'aria-label="Répartition {_e(label)}">']
    debut = -math.pi / 2.0

    def point(rayon_: float, angle: float) -> str:
        return (f"{cx + rayon_ * math.cos(angle):.2f},"
                f"{cy + rayon_ * math.sin(angle):.2f}")

    for item in parts:
        portion = int(item["count"]) / effectif
        fin = debut + portion * 2 * math.pi
        couleur = colors[str(item["label"])]
        if portion >= 0.9999:
            # Une part unique fait un tour complet : un arc de 360 degres
            # n'a pas de corde, et le chemin se refermerait sur rien. Deux
            # cercles concentriques, perces l'un dans l'autre, le disent
            # sans cas particulier a la lecture.
            morceaux.append(
                f'<path d="M {cx - rayon:.2f},{cy:.2f} '
                f'a {rayon:.2f},{rayon:.2f} 0 1,0 {2 * rayon:.2f},0 '
                f'a {rayon:.2f},{rayon:.2f} 0 1,0 {-2 * rayon:.2f},0 '
                f'M {cx - trou:.2f},{cy:.2f} '
                f'a {trou:.2f},{trou:.2f} 0 1,1 {2 * trou:.2f},0 '
                f'a {trou:.2f},{trou:.2f} 0 1,1 {-2 * trou:.2f},0 Z" '
                f'fill="{couleur}" fill-rule="evenodd"/>')
        else:
            grand = 1 if portion > 0.5 else 0
            morceaux.append(
                f'<path d="M {point(rayon, debut)} '
                f'A {rayon:.2f},{rayon:.2f} 0 {grand},1 {point(rayon, fin)} '
                f'L {point(trou, fin)} '
                f'A {trou:.2f},{trou:.2f} 0 {grand},0 {point(trou, debut)} Z" '
                f'fill="{couleur}"/>')
        debut = fin
    morceaux.append(
        f'<text x="{cx:.2f}" y="{cy + 1:.2f}" text-anchor="middle" '
        f'font-size="15" font-weight="600" fill="var(--ink)">'
        f'{_e(format_number(effectif, 0))}</text>'
        f'<text x="{cx:.2f}" y="{cy + 14:.2f}" text-anchor="middle" '
        f'font-size="8" fill="var(--muted)">salariés</text>')

    # La legende : une pastille, le libelle, puis le nombre et la part
    # alignes a droite, comme a l'ecran.
    gauche = cx + rayon + 14.0
    haut = max(6.0, (height - len(parts) * ligne) / 2.0 + 9.0)
    for rang, item in enumerate(parts):
        y = haut + rang * ligne
        couleur = colors[str(item["label"])]
        morceaux.append(
            f'<rect x="{gauche:.1f}" y="{y - 7:.1f}" width="7" height="7" '
            f'rx="1.5" fill="{couleur}"/>'
            f'<text x="{gauche + 12:.1f}" y="{y:.1f}" font-size="9" '
            f'fill="var(--ink)">{_e(str(item["label"]))}</text>'
            f'<text x="{width - 44:.1f}" y="{y:.1f}" text-anchor="end" '
            f'font-size="9" fill="var(--ink)">{int(item["count"])}</text>'
            f'<text x="{width - 2:.1f}" y="{y:.1f}" text-anchor="end" '
            f'font-size="9" fill="var(--muted)">'
            f'{_e(format_percent(item.get("share")))}</text>')
    morceaux.append("</svg>")
    return "".join(morceaux)


#: Place qu'il faut a un repere de boite a moustaches pour ne pas marcher
#: sur son voisin : le montant le plus long, plus un blanc.
_MARK_ROOM = 64.0


def _mark_rows(positions: Sequence[float]) -> List[int]:
    """Repartit les reperes sur deux lignes, au-dessus et en dessous.

    Tout va au-dessus tant que les montants ne se touchent pas. Des que
    deux reperes sont trop proches, le second bascule en dessous : les
    alterner systematiquement ecartait des etiquettes qui tenaient tres
    bien cote a cote, et faisait lire la boite en zigzag.
    """
    rows: List[int] = []
    derniers = {0: None, 1: None}
    for x in positions:
        ligne = 0
        if derniers[0] is not None and x - derniers[0] < _MARK_ROOM:
            ligne = 1
        rows.append(ligne)
        derniers[ligne] = x
    return rows


def boxplot_svg(salary: Dict[str, Any], currency: str, width: int = 360,
                height: int = 200) -> str:
    """Boite a moustaches : P10 - Q1 - mediane - Q3 - P90, bornee min / max.

    Les moustaches s'arretent a P10 et P90 et non au minimum et au maximum :
    une seule remuneration aberrante etirerait le dessin jusqu'a aplatir la
    boite, et le lecteur ne verrait plus rien de la dispersion reelle. Les
    deux extremes restent ecrits sous l'axe, en clair.
    """
    bornes = {cle: salary.get(cle)
              for cle in ("min", "p10", "p25", "median", "p75", "p90", "max")}
    if any(bornes[cle] is None for cle in ("p10", "p25", "median", "p75", "p90")):
        return ""
    # L'echelle s'arrete aux moustaches : c'est la boite qui doit remplir
    # le dessin. Minimum et maximum sont dits en texte, pas dessines.
    bas, haut = bornes["p10"], bornes["p90"]
    if haut <= bas:
        marge = abs(haut) * 0.1 or 1.0
        bas, haut = bas - marge, haut + marge
    cote = 34.0
    plot = width - 2 * cote
    if plot <= 20:
        return ""
    etendue = haut - bas

    def to_x(valeur: float) -> float:
        return cote + (valeur - bas) / etendue * plot

    # La page se partage du bas vers le haut : la legende, l'axe, la
    # rangee basse d'etiquettes, la boite, la rangee haute.
    legende_h, etiquette_h = 34.0, 26.0
    axe = height - legende_h
    hauteur_boite = min(max(height - legende_h - 2 * etiquette_h - 4, 22.0), 58.0)
    sommet = axe - etiquette_h - hauteur_boite
    milieu = sommet + hauteur_boite / 2
    x10, x25 = to_x(bornes["p10"]), to_x(bornes["p25"])
    x50, x75 = to_x(bornes["median"]), to_x(bornes["p75"])
    x90 = to_x(bornes["p90"])
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" '
             'aria-label="Boîte à moustaches des rémunérations">']
    parts.append(f'<line x1="{x10:.1f}" y1="{milieu:.1f}" x2="{x25:.1f}" '
                 f'y2="{milieu:.1f}" stroke="var(--line-strong)"/>')
    parts.append(f'<line x1="{x75:.1f}" y1="{milieu:.1f}" x2="{x90:.1f}" '
                 f'y2="{milieu:.1f}" stroke="var(--line-strong)"/>')
    for x in (x10, x90):
        parts.append(f'<line x1="{x:.1f}" y1="{sommet + 5:.1f}" x2="{x:.1f}" '
                     f'y2="{sommet + hauteur_boite - 5:.1f}" '
                     'stroke="var(--line-strong)"/>')
    parts.append(f'<rect x="{x25:.1f}" y="{sommet:.1f}" '
                 f'width="{max(x75 - x25, 1.0):.1f}" '
                 f'height="{hauteur_boite:.1f}" fill="var(--accent)" '
                 'opacity="0.18" stroke="var(--accent)"/>')
    parts.append(f'<line x1="{x50:.1f}" y1="{sommet:.1f}" x2="{x50:.1f}" '
                 f'y2="{sommet + hauteur_boite:.1f}" stroke="var(--accent)" '
                 'stroke-width="2.5"/>')
    reperes = (("P10", x10, bornes["p10"]), ("Q1", x25, bornes["p25"]),
               ("Médiane", x50, bornes["median"]), ("Q3", x75, bornes["p75"]),
               ("P90", x90, bornes["p90"]))
    lignes = _mark_rows([x for _, x, _ in reperes])
    for (nom, x, valeur), ligne in zip(reperes, lignes):
        if ligne == 0:
            y_nom, y_valeur = sommet - 15, sommet - 5
        else:
            y_nom, y_valeur = sommet + hauteur_boite + 12, sommet + hauteur_boite + 22
        ancrage = "middle"
        if x < cote + 10:
            ancrage = "start"
        elif x > width - cote - 10:
            ancrage = "end"
        parts.append(f'<text x="{x:.1f}" y="{y_nom:.1f}" text-anchor="{ancrage}" '
                     f'font-size="8.5" fill="var(--muted)">{nom}</text>')
        parts.append(
            f'<text x="{x:.1f}" y="{y_valeur:.1f}" text-anchor="{ancrage}" '
            f'font-size="9.5" fill="var(--ink)">'
            f'{_e(format_money(valeur, currency))}</text>')
    parts.append(f'<line x1="4" y1="{axe:.1f}" x2="{width - 4}" '
                 f'y2="{axe:.1f}" stroke="var(--line)"/>')
    extremes = []
    if bornes["min"] is not None:
        extremes.append(f'minimum {format_money(bornes["min"], currency)}')
    if bornes["max"] is not None:
        extremes.append(f'maximum {format_money(bornes["max"], currency)}')
    if extremes:
        parts.append(f'<text x="4" y="{axe + 14:.1f}" font-size="9" '
                     f'fill="var(--muted)">{_e(" · ".join(extremes))}</text>')
    parts.append("</svg>")
    return "".join(parts)


#: Unite ajoutee au titre d'un axe. Un nombre sans unite se lit toujours ;
#: un montant annonce en annees, non.
AXIS_UNITS = {"years": " (années)", "ratio": " (ETP)"}


def axis_label(dataset: Dict[str, Any], which: str) -> str:
    """Libelle d'un axe du nuage, tel que le moteur l'a declare."""
    axis = (dataset or {}).get(f"{which}_axis") or {}
    return str(axis.get("label") or "")


def axis_title(dataset: Dict[str, Any], which: str) -> str:
    """Le meme, avec son unite."""
    axis = (dataset or {}).get(f"{which}_axis") or {}
    return f'{axis_label(dataset, which)}{AXIS_UNITS.get(axis.get("kind"), "")}'


def _legend(dataset: Dict[str, Any]) -> str:
    groups = dataset.get("groups") or []
    if not groups or len(groups) > 14:
        return ""
    colors = palette.series_map(groups, _PALETTE,
                                other=dataset.get("other_label"),
                                neutral="var(--muted)")
    items = "".join(
        f'<span><i class="dot" style="background:{colors[group]}"></i>'
        f'{_e(group)}</span>'
        for group in groups
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
    # Le detail des constats a quitte le document. Il y tenait une pleine
    # page — onze lignes de « avertissement / valeurs non numeriques dans
    # le champ tenure / 2 » — la ou un lecteur de restitution veut savoir
    # une chose : le fichier est-il assez propre pour qu'on lise la suite.
    # Le statut et les six chiffres le disent. Le detail, lui, sert a
    # corriger le fichier, et il reste la ou l'on corrige : l'onglet
    # Qualite de la fenetre, et « controle --json » en ligne de commande.
    return (
        '<h2>Contrôle qualité des données</h2>'
        f'<div class="kpis">{_kpi("Statut", status, fort=True)}{kpis}</div>'
    )


#: Dit a defaut de mieux, quand le moteur n'a pas publie sa raison.
_MASQUE = "Résultat masqué pour préserver la confidentialité."


def _masquee(titre: str, raison: str) -> str:
    """Une section qui dit pourquoi elle n'a rien a montrer.

    Une section qui disparait sans un mot laisse un document dont le
    lecteur ne sait pas s'il manque un chiffre ou s'il n'y en avait pas.
    Ce n'est pas un commentaire : c'est l'etat de la donnee, au meme titre
    que le « masque » des tableaux.
    """
    return f'<h2>{_e(titre)}</h2><p class="masque">{_e(raison)}</p>'


def _population_section(population: Dict[str, Any]) -> str:
    if population.get("masked"):
        return _masquee("Population", population.get("warning") or _MASQUE)
    kpis = "".join([
        _kpi("Effectif", f'{population.get("headcount", 0):,}'.replace(",", " "),
             fort=True),
        _kpi("Âge médian", format_years(population.get("age_median")),
             fort=True),
        _kpi("Ancienneté médiane",
             format_years(population.get("tenure_median")), fort=True),
        _kpi("Âge moyen", format_years(population.get("age_mean"))),
        _kpi("Ancienneté moyenne", format_years(population.get("tenure_mean"))),
    ])

    def bandes(clef):
        rangs = population.get(clef, []) or []
        return ([(row["label"], str(row["count"]), format_percent(row["share"]))
                 for row in rangs],
                [row["share"] for row in rangs])

    age_rows, age_parts = bandes("age_bands")
    tenure_rows, tenure_parts = bandes("tenure_bands")
    return (
        '<h2>Population</h2>'
        f'<div class="kpis">{kpis}</div>'
        f"<h3>Répartition par tranche d'âge</h3>"
        f'{_table(["Tranche", "Effectif", "Part"], age_rows, age_parts)}'
        f"<h3>Répartition par tranche d'ancienneté</h3>"
        f'{_table(["Tranche", "Effectif", "Part"], tenure_rows, tenure_parts)}'
    )


def _salary_section(salary: Dict[str, Any]) -> str:
    currency = salary.get("currency", "EUR")
    if salary.get("masked"):
        return _masquee(salary.get("field_label") or "Rémunération",
                        salary.get("warning") or _MASQUE)
    kpis = "".join([
        _kpi("Masse salariale", format_money(salary.get("payroll"), currency),
             fort=True),
        _kpi("Salaire médian", format_money(salary.get("median"), currency),
             fort=True),
        _kpi("Salaire moyen", format_money(salary.get("mean"), currency)),
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
    # L'ecart-type fermait la section par une phrase. Il y a sa place en
    # ligne, avec les autres mesures de dispersion : un chiffre se range,
    # il ne se commente pas.
    if salary.get("std_dev") is not None:
        dispersion_rows.append(
            ("Écart-type", format_money(salary.get("std_dev"), currency)))
    return (
        f"<h2>Rémunération — {_e(field_label)}</h2>"
        f'<div class="kpis">{kpis}</div>'
        f'<h3>Percentiles</h3>{_table(["Indicateur", "Valeur"], percentile_rows)}'
        f'<h3>Dispersion</h3>{_table(["Indicateur", "Valeur"], dispersion_rows)}'
        f"{_full_time_section(salary, currency)}"
    )


def _full_time_section(salary: Dict[str, Any], currency: str) -> str:
    """Les memes montants a temps de travail egal.

    Place sous les indicateurs verses, jamais a leur place : le lecteur
    doit voir les deux, et savoir lequel il cite.
    """
    bloc = salary.get("full_time") or {}
    if not bloc:
        return ""
    if bloc.get("masked"):
        return ""
    rows = [
        ("Moyenne à temps plein", format_money(bloc.get("mean"), currency)),
        ("Médiane à temps plein", format_money(bloc.get("median"), currency)),
        ("Salariés au temps de travail connu",
         f'{format_number(bloc.get("known_headcount"), 0)} '
         f'({format_percent(bloc.get("coverage"))} des rémunérations)'),
    ]
    return (
        "<h3>À temps plein</h3>"
        + _table(["Indicateur", "Valeur"], rows)
    )


def _distribution_section(distribution: Dict[str, Any], currency: str) -> str:
    if not distribution.get("available"):
        return ""
    chart = histogram_svg(distribution.get("bins", []), currency)
    return (
        "<h2>Distribution</h2>"
        f"<figure>{chart}</figure>"
    )


def _scatter_section(dataset: Dict[str, Any], currency: str) -> str:
    titre = (f'5. {axis_label(dataset, "y")} et '
             f'{axis_label(dataset, "x").lower()}')
    if not dataset.get("available"):
        return ""
    return (
        f"<h2>{_e(titre)}</h2>"
        f"{_legend(dataset)}"
        f"<figure>{scatter_svg(dataset, currency)}</figure>"
    )


def _segments_section(segments: List[Dict[str, Any]], currency: str) -> str:
    if not segments:
        return ""
    blocks = ["<h2>Analyses par segment</h2>"]
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
    return "".join(blocks)


def _comparison_section(comparison: Optional[Dict[str, Any]], currency: str) -> str:
    if not comparison:
        return ""
    rows = [tuple(row) for row in comparison_rows(comparison, currency)]
    return (
        "<h2>Comparaison de populations</h2>"
        + _table([
            "Indicateur", comparison["left_label"], comparison["right_label"], "Écart"
        ], rows)
    )


def _pay_equity_section(equity: Dict[str, Any], currency: str) -> str:
    """Ecarts femmes / hommes, poste par poste.

    La section manquait : l'analyse d'equite n'existait qu'a l'ecran, alors
    que la directive 2023/970 porte precisement sur la *publication* de ces
    indicateurs. Ce qui se voit doit pouvoir se transmettre.
    """
    if not equity or not equity.get("available"):
        return ""
    pay = equity.get("pay", {})
    variable = equity.get("variable", {})
    coverage = equity.get("variable_coverage", {})
    label = (equity.get("category_label") or "poste").lower()

    kpis = "".join([
        _kpi("Écart global", format_percent(pay.get("mean_gap")), fort=True),
        _kpi(f"À {label} comparable",
             format_percent(equity.get("comparable_gap")), fort=True),
        _kpi("Effet de structure",
             format_percent(equity.get("structure_gap"))),
        _kpi("Rattrapage", format_money(equity.get("at_stake_total"),
                                        currency), fort=True),
        _kpi("Effectif femmes", str(equity.get("female_count", 0))),
        _kpi("Effectif hommes", str(equity.get("male_count", 0))),
    ])

    # L'ecart a temps de travail egal, a cote de l'ecart global. Une
    # population feminine plus souvent a temps partiel fait un ecart global
    # qui mesure d'abord le temps de travail : le dire evite de publier
    # comme ecart de remuneration ce qui n'en est pas un.
    plein = equity.get("full_time") or {}
    if plein.get("published"):
        kpis += "".join([
            _kpi("Écart à temps plein", format_percent(plein.get("mean_gap"))),
            _kpi("Expliqué par le temps de travail",
                 format_percent(plein.get("explained_gap"))),
        ])

    rows = []
    for item in sorted(equity.get("categories", []),
                       key=lambda entry: (not entry.get("published"),
                                          -(entry.get("at_stake") or 0.0))):
        if not item.get("published"):
            rows.append((item["category"], str(item["female_count"]),
                         str(item["male_count"]), "masqué", "masqué",
                         "masqué", "—"))
            continue
        rows.append((item["category"], str(item["female_count"]),
                     str(item["male_count"]),
                     format_money(item.get("female_median"), currency),
                     format_money(item.get("male_median"), currency),
                     format_percent(item.get("mean_gap")),
                     format_money(item.get("at_stake"), currency)))
    table = _table([equity.get("category_label") or "Catégorie", "Femmes",
                    "Hommes", "Médiane femmes", "Médiane hommes",
                    "Écart moyen", "Rattrapage"], rows) if rows else ""

    quartiles = [(f'Q{item["quartile"]}', str(item["headcount"]),
                  format_percent(item.get("female_share")),
                  format_percent(item.get("male_share")))
                 for item in equity.get("quartiles", [])]
    quartile_table = _table(["Quartile", "Effectif", "Part femmes",
                             "Part hommes"], quartiles) if quartiles else ""

    # Un paragraphe de quinze lignes fermait cette section : ce que chaque
    # ecart signifie, ce qu'il commande, d'ou viennent les formules. Les
    # chiffres qu'il portait — ecart median, ecart sur le variable, parts
    # qui le percoivent, couverture, sexe non renseigne — n'etaient
    # lisibles qu'en lisant la phrase. Ils se rangent ici en tableau, ou
    # on les trouve sans lire. Ce qu'ils signifient appartient a qui les
    # lit, non a l'outil qui les calcule.
    détail = [("Écart médian", format_percent(pay.get("median_gap")))]
    if variable.get("mean_gap") is not None:
        détail += [
            ("Écart sur la rémunération variable",
             format_percent(variable.get("mean_gap"))),
            ("Femmes percevant une part variable",
             format_percent(coverage.get("female_share"))),
            ("Hommes percevant une part variable",
             format_percent(coverage.get("male_share"))),
        ]
    if plein.get("published"):
        détail += [
            ("Écart à temps plein", format_percent(plein.get("mean_gap"))),
            ("Couverture du temps plein",
             format_percent(plein.get("coverage"))),
        ]
    détail.append(("Couverture de la décomposition",
                   format_percent(equity.get("comparable_coverage"))))
    unknown = equity.get("unknown_count", 0)
    if unknown:
        détail.append(("Sexe non renseigné, exclus des écarts",
                       format_number(unknown, 0)))

    return (
        "<h2>Écarts de rémunération femmes / hommes</h2>"
        f'<div class="kpis">{kpis}</div>'
        f'<h3>Détail</h3>{_table(["Indicateur", "Valeur"], détail)}'
        f"<h3>Écart par {label}</h3>{table}"
        f"<h3>Répartition par quartile de rémunération</h3>{quartile_table}"
    )


def _numeroter(sections: Sequence[str]) -> List[str]:
    """Numerote les sections effectivement rendues.

    Les numeros etaient ecrits dans chaque section. Une section qui ne
    pouvait rien publier laissait alors un trou dans la suite — le lecteur
    passait de 4 a 6 et cherchait ce qu'il avait manque. Ils se posent
    donc ici, sur ce qui parait.
    """
    rendues: List[str] = []
    numero = 0
    for section in sections:
        if not section:
            continue
        numero += 1
        rendues.append(section.replace(
            "<h2>", f'<h2><span class="num">{numero}</span>', 1))
    return rendues


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
        _pay_equity_section(analysis.get("pay_equity", {}), currency),
        _comparison_section(analysis.get("comparison"), currency),
    ]
    sections = _numeroter(sections)
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
<div>Fichier source<b>{_e(manifest.get("fichier_source", "—"))}</b></div>
<div>Effectif analysé<b>{_e(manifest.get("effectif_analyse", "—"))}</b></div>
<div>Périmètre<b>{_e(manifest.get("filtres", "Aucun filtre"))}</b></div>
<div>Date d'analyse<b>{_e(generated)}</b></div>
</div>
</header>
<div class="corps">
{''.join(sections)}
</div>
<footer>
{_e(ENGINE_NAME)} v{_e(__version__)}
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
    return restrict_to_owner(path)
