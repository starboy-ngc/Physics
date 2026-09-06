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
    #: Taille propre au bloc : largeur en douziemes, hauteur en pixels.
    #: Elle est fixee ici parce qu'elle depend de ce que le bloc montre —
    #: un chiffre tient dans un quart de largeur, un nuage de points a
    #: besoin des deux tiers — et non de ce que l'utilisateur en fait.
    span: int = 3
    height: int = 92


#: Familles, dans l'ordre ou elles sont proposees.
FAMILIES = ("Population", "Rémunération", "Dispersion", "Pay Transparency",
            "Graphiques")


#: Tailles de reference, mesurees a l'ecran. Un indicateur loge son
#: en-tete, son filet et son chiffre ; un tableau ses lignes ; un
#: graphique ses axes et sa legende.
QUARTER, THIRD, HALF, TWO_THIRDS, FULL = 3, 4, 6, 8, 12


def _indicator(ident: str, label: str, family: str, source: str,
               key: str) -> Block:
    # Le tiers plutot que le quart : mesure faite sur une fenetre de
    # 1360 px, onze des vingt-trois intitules etaient tronques au quart
    # contre trois au tiers, et le chiffre — qui est le contenu du bloc —
    # y garde une chasse de titre au lieu de retomber au corps du texte.
    # Trois indicateurs par rangee tombent juste sur les douze colonnes.
    return Block(ident, label, family, "indicator", source, key,
                 span=THIRD, height=92)


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
          key="salary_scale", span=THIRD, height=250),
    Block("dispersion_table", "Tableau de dispersion", "Dispersion", "table",
          key="dispersion", span=THIRD, height=210),

    # ----------------------------------------------------------- graphiques
    Block("age_pyramid", "Pyramide des âges", "Graphiques", "chart",
          key="age_pyramid", span=HALF, height=300),
    Block("tenure_pyramid", "Structure d'ancienneté", "Graphiques", "chart",
          key="tenure_pyramid", span=HALF, height=300),
    Block("histogram", "Distribution des rémunérations", "Graphiques",
          "chart", key="histogram", span=HALF, height=280),
    # Le nuage porte deux axes chiffres et une legende : plus etroit, ses
    # graduations se chevauchent.
    Block("scatter", "Rémunération / Ancienneté", "Graphiques", "chart",
          key="scatter", span=TWO_THIRDS, height=340),
    Block("boxes", "Dispersion par segment", "Graphiques", "chart",
          key="boxes", needs_field=True, span=TWO_THIRDS, height=330),
    Block("quartiles", "Répartition H/F par quartile", "Graphiques", "chart",
          key="quartiles", span=HALF, height=280),
    Block("gaps", "Écarts H/F par catégorie", "Graphiques", "chart",
          key="gaps", needs_field=True, span=HALF, height=300),
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
        # Une taille enregistree du temps ou elle se tirait a la souris est
        # ignoree : c'est le catalogue qui la donne desormais.
        kept.append(normalise({"block": ident,
                               "field": entry.get("field") or ""}))
    if unknown:
        log_event("interface", "dashboard_load", status="INCONNU",
                  detail=f"blocs ignores={len(unknown)}")
    return kept


def dump(blocks: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Section a enregistrer : des identifiants et un ordre, rien d'autre.

    Ni chiffre, ni donnee RH — et plus aucune taille : elle appartient au
    bloc, pas a la page. Une page composee sur un grand ecran s'ouvre donc
    juste sur un petit, et un bloc dont la taille de reference est corrigee
    dans une version ulterieure la prend sans que personne ait a refaire sa
    page.
    """
    saved = []
    for entry in blocks:
        if entry.get("block") not in CATALOGUE:
            continue
        item = {"block": entry["block"]}
        if entry.get("field"):
            item["field"] = entry["field"]
        saved.append(item)
    return {"blocks": saved}


# ------------------------------------------------------------- disposition

#: Largeur de la page, en colonnes. Douze se divise par deux, trois et
#: quatre : toutes les largeurs utiles tombent juste.
COLUMNS = 12

def normalise(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Complete un bloc avec la taille de sa nature.

    La taille vient du catalogue et non de la configuration : elle depend
    de ce que le bloc montre — un chiffre tient dans un quart de largeur,
    un nuage de points a besoin des deux tiers — et non de ce que
    l'utilisateur en a fait. Une page composee du temps ou les tailles se
    tiraient a la souris s'ouvre donc a la bonne taille, et non a celle
    qu'on lui avait donnee.
    """
    block = CATALOGUE[entry["block"]]
    return {"block": entry["block"], "field": entry.get("field", ""),
            "span": block.span, "height": block.height}



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
        #: Bloc du catalogue en cours de depot depuis la palette.
        self._incoming: Optional[str] = None
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
        self._raise_ghost(CATALOGUE[self.blocks[position]["block"]].label)
        self.holders[position].configure(background=theme.STRIPE)
        self._move_ghost(event)

    def _raise_ghost(self, label: str) -> None:
        """Etiquette qui suit le curseur, dans sa propre fenetre.

        Une fenetre plutot qu'un cadre pose dans le plan de travail : le
        bloc peut venir de la palette, a gauche, et un cadre ne se dessine
        pas hors de son parent — le fantome disparaissait tant que le
        curseur n'avait pas atteint la page.
        """
        self._drop_ghost()
        self._ghost = tk.Toplevel(self)
        self._ghost.wm_overrideredirect(True)
        self._ghost.attributes("-topmost", True)
        self._ghost.configure(background=theme.ACCENT)
        tk.Label(self._ghost, text=label, background=theme.ACCENT_SOFT,
                 foreground=theme.ACCENT, font=self.fonts.body_bold,
                 padx=10, pady=6).pack(padx=1, pady=1)

    def _drop_ghost(self) -> None:
        if self._ghost is not None:
            self._ghost.destroy()
            self._ghost = None

    def _move_ghost(self, _event=None) -> None:
        if self._ghost is None:
            return
        self._ghost.wm_geometry(f"+{self.winfo_pointerx() + 14}"
                                f"+{self.winfo_pointery() + 12}")
        self._ghost.lift()
        x, y = self._local_pointer()
        if self._inside(x, y):
            self._show_marker(x, y)
        else:
            self._hide_marker()

    def _local_pointer(self) -> tuple:
        return (self.winfo_pointerx() - self.winfo_rootx(),
                self.winfo_pointery() - self.winfo_rooty())

    def _inside(self, x: float, y: float) -> bool:
        """Le curseur est-il au-dessus du plan de travail ?"""
        return 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height()

    def _drag(self, event) -> None:
        self._move_ghost(event)

    # ------------------------------------------- depot venu de la palette

    def start_external(self, ident: str) -> None:
        """Un bloc du catalogue commence sa course vers la page."""
        if ident not in CATALOGUE:
            return
        self._incoming = ident
        self._raise_ghost(CATALOGUE[ident].label)
        self._move_ghost()

    def drag_external(self) -> None:
        if self._incoming is not None:
            self._move_ghost()

    def finish_external(self) -> bool:
        """Depose le bloc a l'endroit lache. Rend False si c'etait hors page.

        Lacher a cote n'ajoute rien : un geste interrompu doit pouvoir
        l'etre, sinon la page se remplit de blocs qu'on n'a pas voulus.
        """
        ident, self._incoming = self._incoming, None
        x, y = self._local_pointer()
        self._drop_ghost()
        self._hide_marker()
        if ident is None or not self._inside(x, y):
            return False
        self.insert(ident, self._target(x, y))
        return True

    def insert(self, ident: str, position: int) -> None:
        """Ajoute un bloc du catalogue au rang demande."""
        if ident not in CATALOGUE:
            return
        position = max(0, min(position, len(self.blocks)))
        self.blocks.insert(position, normalise({"block": ident}))
        self._rebuild()
        self._changed()

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

    def _hide_marker(self) -> None:
        if self._marker is not None:
            self._marker.place_forget()

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
        x, y = self._local_pointer()
        source, self._dragging = self._dragging, None
        self._drop_ghost()
        self._hide_marker()
        # Lache hors de la page, le bloc revient a sa place : c'est ce qu'on
        # attend d'un geste interrompu.
        if self._inside(x, y):
            self.move(source, self._target(x, y))
        else:
            self._rebuild()

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

    def _changed(self) -> None:
        if self.on_change:
            self.on_change()
