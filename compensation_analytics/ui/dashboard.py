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

import tkinter as tk
from typing import Any, Dict, List, NamedTuple, Optional, Sequence

from ..core.logging_setup import log_event
from . import theme


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
        kept.append(normalise({"block": ident,
                               "field": entry.get("field") or "",
                               "span": entry.get("span"),
                               "height": entry.get("height")}))
    if unknown:
        log_event("interface", "dashboard_load", status="INCONNU",
                  detail=f"blocs ignores={len(unknown)}")
    return kept


def dump(blocks: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Section a enregistrer : identifiants, ordre et tailles, rien d'autre.

    La largeur part en colonnes et non en pixels : une page composee sur un
    grand ecran doit s'ouvrir juste sur un petit.
    """
    saved = []
    for entry in blocks:
        if entry.get("block") not in CATALOGUE:
            continue
        complete = normalise(entry)
        item = {"block": complete["block"], "span": complete["span"],
                "height": complete["height"]}
        if complete["field"]:
            item["field"] = complete["field"]
        saved.append(item)
    return {"blocks": saved}


# ------------------------------------------------------------- disposition

#: Largeur de la page, en colonnes. Douze se divise par deux, trois et
#: quatre : toutes les largeurs utiles tombent juste.
COLUMNS = 12

#: Largeurs proposees, en colonnes, avec leur nom.
SIZES = ((3, "Quart"), (4, "Tiers"), (6, "Moitié"), (12, "Pleine largeur"))

#: Hauteurs de depart, par nature de bloc. Assez generreuses pour que rien
#: ne soit rogne avant que l'on y touche.
#: L'indicateur doit loger son en-tete, son filet et son chiffre au corps
#: des indicateurs — mesure faite, quatre-vingt-douze pixels.
DEFAULT_HEIGHT = {"indicator": 92, "table": 230, "chart": 280}

#: Bornes du redimensionnement vertical. Le plancher est celui d'un bloc
#: dont l'en-tete reste lisible.
MIN_HEIGHT, MAX_HEIGHT = 70, 700


def normalise(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Complete un bloc enregistre avec sa taille, si elle manque.

    Une page composee avant que les tailles existent doit s'ouvrir : ses
    blocs prennent alors la largeur pleine et la hauteur de leur nature.
    """
    block = CATALOGUE[entry["block"]]
    span = entry.get("span")
    if span not in [size for size, _label in SIZES]:
        span = COLUMNS
    height = entry.get("height")
    if not isinstance(height, int) or not MIN_HEIGHT <= height <= MAX_HEIGHT:
        height = DEFAULT_HEIGHT.get(block.kind, 260)
    return {"block": entry["block"], "field": entry.get("field", ""),
            "span": span, "height": height}


def snap_span(wanted: float) -> int:
    """Palier de largeur le plus proche d'une largeur voulue.

    La largeur se pose sur un palier : une page dont les blocs font cinq
    douziemes et sept douziemes ne s'aligne plus avec rien.
    """
    return min((size for size, _label in SIZES),
               key=lambda size: abs(size - wanted))


def clamp_height(wanted: float) -> int:
    """Hauteur ramenee entre le plancher lisible et le plafond utile."""
    return int(max(MIN_HEIGHT, min(MAX_HEIGHT, wanted)))


def flow(blocks: Sequence[Dict[str, Any]], width: float,
         gap: int = 18) -> List[Dict[str, Any]]:
    """Place les blocs de gauche a droite, en passant a la ligne.

    C'est la disposition de tous les composeurs de tableau de bord, et la
    seule qui survive a un redimensionnement de fenetre : une position
    absolue en pixels serait juste sur l'ecran ou elle a ete posee, et
    fausse partout ailleurs.

    Retourne, pour chaque bloc, sa boite en pixels.
    """
    placed: List[Dict[str, Any]] = []
    unit = (width - gap * (COLUMNS - 1)) / COLUMNS
    column, top, row_height = 0, 0.0, 0.0
    for entry in blocks:
        span = min(entry["span"], COLUMNS)
        if column + span > COLUMNS:
            top += row_height + gap
            column, row_height = 0, 0.0
        placed.append({
            "x": column * (unit + gap),
            "y": top,
            "width": span * unit + gap * (span - 1),
            "height": entry["height"],
        })
        row_height = max(row_height, entry["height"])
        column += span
    return placed


def page_height(placed: Sequence[Dict[str, Any]], gap: int = 18) -> float:
    """Hauteur totale occupee, marge du bas comprise."""
    if not placed:
        return 0.0
    return max(box["y"] + box["height"] for box in placed) + gap


class Board(tk.Frame):
    """Plan de travail : on y depose, on y deplace, on y redimensionne.

    Les blocs sont poses en pixels — c'est ce qu'exige un glisser-deposer —
    mais leurs coordonnees sont recalculees a chaque mise en page a partir
    d'une grille en douziemes. La position enregistree est donc un rang et
    une largeur en colonnes, jamais des pixels : une page composee sur un
    grand ecran s'ouvre juste sur un petit.

    Pendant un deplacement, seul un fantome suit le curseur. Deplacer le
    bloc lui-meme ferait repeindre son contenu a chaque pixel parcouru, et
    le nuage de points met cent vingt-neuf millisecondes a se tracer.
    """

    GAP = 18
    HEADER = 26
    GRIP = 14
    #: Place reservee a la croix de retrait, marges comprises.
    CLOSE = 28

    def __init__(self, master: tk.Widget, fonts, build, on_change=None):
        super().__init__(master, background=theme.CANVAS)
        self.fonts = fonts
        self.build = build
        self.on_change = on_change
        self.blocks: List[Dict[str, Any]] = []
        self.holders: List[tk.Frame] = []
        self.boxes: List[Dict[str, Any]] = []
        self._ghost: Optional[tk.Frame] = None
        self._marker: Optional[tk.Frame] = None
        self._dragging: Optional[int] = None
        self._sizing: Optional[int] = None
        self.bind("<Configure>", lambda _e: self.layout())

    # ------------------------------------------------------------ contenu

    def set_blocks(self, blocks: Sequence[Dict[str, Any]]) -> None:
        """Remplace la composition et remonte les blocs."""
        self.blocks = [normalise(entry) for entry in blocks]
        self._rebuild()

    def _rebuild(self) -> None:
        # La mise en page est calculee avant de monter les blocs : un bloc
        # doit connaitre sa largeur pour choisir la chasse de son chiffre,
        # et « winfo_width » ne la donnerait qu'apres coup.
        self.boxes = flow(self.blocks, max(self.winfo_width(), 200), self.GAP)
        for holder in self.holders:
            holder.destroy()
        self.holders = []
        for position, entry in enumerate(self.blocks):
            width = self.boxes[position]["width"] if position < len(self.boxes) \
                else 200
            self.holders.append(self._holder(position, entry, width))
        self.layout()

    def _holder(self, position: int, entry: Dict[str, Any],
                width: float) -> tk.Frame:
        block = CATALOGUE[entry["block"]]
        holder = tk.Frame(self, background=theme.CANVAS)
        head = tk.Frame(holder, background=theme.CANVAS, height=self.HEADER)
        head.pack(fill="x")
        head.pack_propagate(False)
        # La croix est posee avant l'intitule : un intitule qui reclame
        # toute la place la chassait du cadre, et le bloc devenait
        # irretirable dans une colonne etroite.
        close = tk.Label(head, text="✕", background=theme.CANVAS,
                         foreground=theme.FAINT, font=self.fonts.body,
                         cursor="hand2", padx=6)
        close.pack(side="right")
        close.bind("<Button-1>", lambda _e, p=position: self.remove(p))
        title = tk.Label(head, text=self._fit(block.label,
                                              width - self.CLOSE),
                         background=theme.CANVAS,
                         foreground=theme.INK, font=self.fonts.body_bold,
                         cursor="fleur", anchor="w")
        title.pack(side="left", fill="x", expand=True)
        for widget in (head, title):
            widget.bind("<Button-1>",
                        lambda e, p=position: self._grab(p, e))
            widget.bind("<B1-Motion>", self._drag)
            widget.bind("<ButtonRelease-1>", self._drop)
        theme.rule(holder).pack(fill="x", pady=(2, 6))

        content = tk.Frame(holder, background=theme.CANVAS)
        content.pack(fill="both", expand=True)
        self.build(content, entry, position, width)

        grip = tk.Label(holder, text="◢", background=theme.CANVAS,
                        foreground=theme.LINE_STRONG, font=self.fonts.small,
                        cursor="bottom_right_corner")
        grip.place(relx=1.0, rely=1.0, anchor="se")
        grip.bind("<Button-1>", lambda e, p=position: self._grab_size(p, e))
        grip.bind("<B1-Motion>", self._resize)
        grip.bind("<ButtonRelease-1>", self._release_size)
        return holder

    def _fit(self, text: str, limit: float) -> str:
        """Intitule ramene a la largeur disponible, mesure a l'appui.

        Un intitule coupe net se lit comme un defaut d'affichage ; coupe sur
        des points de suspension, il se lit comme un intitule abrege.
        """
        font = self.fonts.body_bold
        if limit <= 0 or font.measure(text) <= limit:
            return text
        while text and font.measure(text + "…") > limit:
            text = text[:-1]
        return text + "…"

    # -------------------------------------------------------- mise en page

    def layout(self) -> None:
        width = max(self.winfo_width(), 200)
        self.boxes = flow(self.blocks, width, self.GAP)
        for holder, box in zip(self.holders, self.boxes):
            holder.place(x=box["x"], y=box["y"], width=box["width"],
                         height=box["height"])
        self.configure(height=max(page_height(self.boxes, self.GAP), 1))

    # ------------------------------------------------------- deplacement

    def _grab(self, position: int, event) -> None:
        if position >= len(self.blocks):
            return
        self._dragging = position
        block = CATALOGUE[self.blocks[position]["block"]]
        self._ghost = tk.Frame(self, background=theme.ACCENT_SOFT,
                               highlightthickness=1,
                               highlightbackground=theme.ACCENT)
        tk.Label(self._ghost, text=block.label, background=theme.ACCENT_SOFT,
                 foreground=theme.ACCENT, font=self.fonts.body_bold).pack(
                     padx=10, pady=6)
        self.holders[position].configure(background=theme.STRIPE)
        self._move_ghost(event)

    def _move_ghost(self, event) -> None:
        if self._ghost is None:
            return
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        self._ghost.place(x=x + 12, y=y + 10)
        self._ghost.lift()
        self._show_marker(x, y)

    def _drag(self, event) -> None:
        self._move_ghost(event)

    def _show_marker(self, x: float, y: float) -> None:
        """Trait d'insertion : sans lui, on lache a l'aveugle."""
        target = self._target(x, y)
        if self._marker is None:
            self._marker = tk.Frame(self, background=theme.ACCENT, width=3)
        if target < len(self.boxes):
            box = self.boxes[target]
            self._marker.place(x=max(box["x"] - self.GAP / 2, 0), y=box["y"],
                               width=3, height=box["height"])
        elif self.boxes:
            box = self.boxes[-1]
            self._marker.place(x=box["x"] + box["width"] + self.GAP / 4,
                               y=box["y"], width=3, height=box["height"])
        self._marker.lift()

    def _target(self, x: float, y: float) -> int:
        """Rang ou le bloc atterrirait, en ordre de lecture."""
        for index, box in enumerate(self.boxes):
            if y < box["y"]:
                return index
            middle = box["y"] + box["height"] / 2
            if abs(y - middle) <= box["height"] / 2:
                if x < box["x"] + box["width"] / 2:
                    return index
        return len(self.blocks)

    def _drop(self, _event=None) -> None:
        if self._dragging is None:
            return
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        target = self._target(x, y)
        source = self._dragging
        self._dragging = None
        if self._ghost is not None:
            self._ghost.destroy()
            self._ghost = None
        if self._marker is not None:
            self._marker.destroy()
            self._marker = None
        self.move(source, target)

    def move(self, source: int, target: int) -> None:
        """Deplace un bloc au rang demande, et remonte la page."""
        if not 0 <= source < len(self.blocks):
            return
        entry = self.blocks.pop(source)
        if target > source:
            target -= 1
        self.blocks.insert(max(0, min(target, len(self.blocks))), entry)
        self._rebuild()
        self._changed()

    def remove(self, position: int) -> None:
        if 0 <= position < len(self.blocks):
            del self.blocks[position]
            self._rebuild()
            self._changed()

    def add(self, ident: str) -> None:
        if ident in CATALOGUE:
            self.blocks.append(normalise({"block": ident}))
            self._rebuild()
            self._changed()

    def clear(self) -> None:
        self.blocks = []
        self._rebuild()
        self._changed()

    # ---------------------------------------------------- redimensionnement

    def _grab_size(self, position: int, _event) -> None:
        self._sizing = position

    def _resize(self, _event) -> None:
        if self._sizing is None or self._sizing >= len(self.boxes):
            return
        entry = self.blocks[self._sizing]
        box = self.boxes[self._sizing]
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        width = max(self.winfo_width(), 200)
        unit = (width - self.GAP * (COLUMNS - 1)) / COLUMNS
        wanted = (x - box["x"] + self.GAP) / (unit + self.GAP)
        entry["span"] = snap_span(wanted)
        entry["height"] = clamp_height(y - box["y"])
        self.layout()

    def _release_size(self, _event=None) -> None:
        """Le contenu est remonte a la largeur obtenue, pas a l'ancienne.

        Un indicateur choisit la chasse de son chiffre d'apres la largeur
        qu'on lui donne : passer d'un quart a la pleine largeur sans
        remonter le bloc laisserait le chiffre a la taille du quart.
        """
        if self._sizing is not None:
            self._sizing = None
            self._rebuild()
            self._changed()

    def _changed(self) -> None:
        if self.on_change:
            self.on_change()
