"""Graphiques interactifs dessines sur un canevas tkinter.

Le nuage de points est l'ecran d'exploration : survol pour identifier un
salarie, molette pour zoomer, glisser pour se deplacer, clic sur la legende
pour isoler une population. Rien de tout cela n'est possible dans un document
imprime — c'est la raison d'etre de l'interface.

Les couleurs et les regles de lecture sont celles des restitutions, pour que
l'ecran et le document racontent la meme chose.
"""

from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Dict, List, Optional, Sequence

from ..core.axes import nice_ticks
from ..core.reporting import (_PALETTE, format_money, format_number,
                              format_years)
from . import raster
from .theme import (ACCENT, CANVAS, FAINT, INK, LINE, MUTED, SIZE_LABEL,
                    SIZE_SMALL, _rgb, pick_family)

#: Les filets du fond doivent se deviner, pas se lire.
GRID = "#eef2f6"
TREND = "#b0453f"

_family: str = "TkDefaultFont"


def _fonts(widget: tk.Misc) -> None:
    """Aligne les canevas sur la typographie de la fenetre."""
    global _family
    if _family == "TkDefaultFont":
        _family = pick_family(widget)


def axis_font():
    return (_family, SIZE_LABEL)


def note_font():
    return (_family, SIZE_SMALL)


class Tooltip:
    """Info-bulle suivant le curseur, dessinee dans une fenetre sans bordure."""

    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.window: Optional[tk.Toplevel] = None
        self.label: Optional[tk.Label] = None

    def show(self, text: str, x: int, y: int) -> None:
        if self.window is None:
            self.window = tk.Toplevel(self.widget)
            self.window.wm_overrideredirect(True)
            self.window.attributes("-topmost", True)
            self.label = tk.Label(
                self.window, justify="left", background=INK, foreground="white",
                padx=8, pady=5, font=note_font(),
            )
            self.label.pack()
        self.label.configure(text=text)
        self.window.wm_geometry(f"+{x + 16}+{y + 16}")
        self.window.deiconify()

    def hide(self) -> None:
        if self.window is not None:
            self.window.withdraw()


class ScatterChart(tk.Frame):
    """Nuage anciennete x remuneration, explorable.

    Le zoom et le deplacement ne changent que la fenetre affichee : les
    donnees ne sont jamais filtrees a l'insu de l'utilisateur, et le compteur
    de points visibles le rappelle en permanence.
    """

    def __init__(self, master: tk.Widget, on_select: Optional[Callable] = None):
        super().__init__(master, background=CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self.on_select = on_select

        self.dataset: Dict[str, Any] = {}
        self.currency = "EUR"
        self.points: List[Dict[str, Any]] = []
        self.hidden: set = set()
        self.selected: Optional[Dict[str, Any]] = None
        self._items: Dict[int, Dict[str, Any]] = {}
        # Les images des points, gardees ici : Tk ne retient pas ses images,
        # et un ramassage les ferait disparaitre du canevas.
        self._dots: Dict[Any, tk.PhotoImage] = {}
        self._view = None            # (x_min, x_max, y_min, y_max) affichee
        self._bounds = None          # etendue complete des donnees
        self._drag = None

        self.canvas.bind("<Configure>", lambda _e: self.redraw())
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda _e: setattr(self, "_drag", None))
        self.canvas.bind("<Double-Button-1>", lambda _e: self.reset_view())
        # Molette : Windows et Mac envoient <MouseWheel>, X11 des boutons 4 et 5.
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom(e.x, e.y, 1 / 1.2))
        self.canvas.bind("<Button-5>", lambda e: self._zoom(e.x, e.y, 1.2))

    # ------------------------------------------------------------- donnees

    def set_dataset(self, dataset: Dict[str, Any], currency: str = "EUR") -> None:
        self.dataset = dataset or {}
        self.currency = currency
        self.points = list(self.dataset.get("points") or [])
        self.hidden.clear()
        self.selected = None
        self._bounds = self._compute_bounds(self.points)
        self._view = self._bounds
        self.redraw()

    @staticmethod
    def _compute_bounds(points: Sequence[Dict[str, Any]]):
        if not points:
            return None
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        # Une marge evite que les points extremes collent aux axes.
        x_pad = (x_max - x_min) * 0.04 or 1
        y_pad = (y_max - y_min) * 0.04 or 1
        return (x_min - x_pad, x_max + x_pad, y_min - y_pad, y_max + y_pad)

    def visible_points(self) -> List[Dict[str, Any]]:
        return [p for p in self.points if p["group"] not in self.hidden]

    def toggle_group(self, group: str) -> None:
        self.hidden.symmetric_difference_update({group})
        self.redraw()

    def reset_view(self) -> None:
        self._view = self._bounds
        self.redraw()

    # ------------------------------------------------------------- dessin

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 60 or height < 60:
            return
        if not self.points or not self._view:
            self.canvas.create_text(
                width / 2, height / 2, text=self.dataset.get("warning")
                or "Aucun point a afficher", fill=MUTED, font=note_font())
            return

        pad_l, pad_r, pad_t, pad_b = 88, 20, 18, 46
        plot_w = max(width - pad_l - pad_r, 10)
        plot_h = max(height - pad_t - pad_b, 10)
        x_min, x_max, y_min, y_max = self._view
        x_span = (x_max - x_min) or 1.0
        y_span = (y_max - y_min) or 1.0

        def to_px(x, y):
            return (pad_l + (x - x_min) / x_span * plot_w,
                    pad_t + plot_h - (y - y_min) / y_span * plot_h)

        # Graduations posees sur des valeurs rondes, jamais sur les bornes de
        # l'etendue : celles-ci donnaient « 4 284 EUR » ou « -0,6 an ».
        for value in nice_ticks(y_min, y_max):
            y = pad_t + plot_h - (value - y_min) / y_span * plot_h
            self.canvas.create_line(pad_l, y, pad_l + plot_w, y, fill=GRID)
            self.canvas.create_text(
                pad_l - 8, y, anchor="e", fill=MUTED, font=axis_font(),
                text=format_money(value, self.currency))
        for value in nice_ticks(x_min, x_max):
            x = pad_l + (value - x_min) / x_span * plot_w
            self.canvas.create_text(
                x, pad_t + plot_h + 14, fill=MUTED, font=axis_font(),
                text=format_number(value, 0))
        self.canvas.create_line(pad_l, pad_t + plot_h, pad_l + plot_w,
                                pad_t + plot_h, fill="#9aa7b4")
        self.canvas.create_text(pad_l + plot_w / 2, pad_t + plot_h + 32,
                                text="Ancienneté (années)", fill=MUTED,
                                font=axis_font())

        groups = self.dataset.get("groups") or []
        colours = {g: _PALETTE[i % len(_PALETTE)] for i, g in enumerate(groups)}

        shown = 0
        for point in self.points:
            if point["group"] in self.hidden:
                continue
            px, py = to_px(point["x"], point["y"])
            if not (pad_l - 4 <= px <= pad_l + plot_w + 4):
                continue
            if not (pad_t - 4 <= py <= pad_t + plot_h + 4):
                continue
            shown += 1
            colour = colours.get(point["group"], ACCENT)
            selected = self.selected is point
            # create_oval ne lisse pas ses bords : a cette taille les points
            # devenaient des carres a coins ronges. Une image antialiasee,
            # calculee une fois par couleur, donne de vrais ronds.
            item = self.canvas.create_image(
                px, py, image=self._dot(colour, selected))
            self._items[item] = point

        trend = self.dataset.get("trend")
        if trend and self.visible_points():
            y_start = trend["intercept"] + trend["slope"] * x_min
            y_end = trend["intercept"] + trend["slope"] * x_max
            self.canvas.create_line(*to_px(x_min, y_start), *to_px(x_max, y_end),
                                    fill=TREND, width=2, dash=(6, 4))

        total = len(self.points)
        note = f"{shown} points affichés sur {total}"
        if self.hidden:
            note += f" · {len(self.hidden)} population(s) masquée(s)"
        if self._view != self._bounds:
            note += " · zoom actif, double-clic pour réinitialiser"
        self.canvas.create_text(pad_l, pad_t - 6, anchor="sw", text=note,
                                fill=MUTED, font=axis_font())

    # --------------------------------------------------------- interaction

    #: Diametre des points, en pixels. Le point selectionne est plus gros et
    #: porte un cerne, pour rester reperable au milieu du nuage.
    DOT = 7
    DOT_SELECTED = 13

    def _dot(self, colour: str, selected: bool) -> tk.PhotoImage:
        """Image d'un point, mise en cache par couleur et par etat."""
        key = (colour, selected)
        image = self._dots.get(key)
        if image is None:
            if selected:
                data = raster.disc(self.DOT_SELECTED, _rgb(TREND),
                                   ring=_rgb(INK), ring_width=2.0)
            else:
                data = raster.disc(self.DOT, _rgb(colour))
            image = tk.PhotoImage(master=self.canvas, data=data)
            self._dots[key] = image
        return image

    def _nearest(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        for item in self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5):
            if item in self._items:
                return self._items[item]
        return None

    def _on_motion(self, event) -> None:
        if self._drag:
            return
        point = self._nearest(event.x, event.y)
        if point is None:
            self.tooltip.hide()
            self.canvas.configure(cursor="")
            return
        self.canvas.configure(cursor="hand2")
        self.tooltip.show(
            f'{point["reference"]}\n{point["group"]}\n'
            f'Ancienneté : {format_years(point["x"])}\n'
            f'Rémunération : {format_money(point["y"], self.currency)}',
            self.canvas.winfo_rootx() + event.x,
            self.canvas.winfo_rooty() + event.y)

    def _on_click(self, event) -> None:
        point = self._nearest(event.x, event.y)
        if point is None:
            self._drag = (event.x, event.y, self._view)
            return
        self.selected = None if self.selected is point else point
        self.redraw()
        if self.on_select:
            self.on_select(self.selected)

    def _on_drag(self, event) -> None:
        if not self._drag or not self._view:
            return
        start_x, start_y, view = self._drag
        width = max(self.canvas.winfo_width() - 108, 10)
        height = max(self.canvas.winfo_height() - 64, 10)
        x_min, x_max, y_min, y_max = view
        dx = (event.x - start_x) / width * (x_max - x_min)
        dy = (event.y - start_y) / height * (y_max - y_min)
        self._view = (x_min - dx, x_max - dx, y_min + dy, y_max + dy)
        self.redraw()

    def _on_wheel(self, event) -> None:
        self._zoom(event.x, event.y, 1 / 1.2 if event.delta > 0 else 1.2)

    def _zoom(self, px: int, py: int, factor: float) -> None:
        if not self._view or not self._bounds:
            return
        pad_l, pad_t = 88, 18
        width = max(self.canvas.winfo_width() - 108, 10)
        height = max(self.canvas.winfo_height() - 64, 10)
        x_min, x_max, y_min, y_max = self._view
        # Le point sous le curseur reste immobile : c'est ce qui rend le zoom
        # previsible.
        fx = min(max((px - pad_l) / width, 0.0), 1.0)
        fy = 1 - min(max((py - pad_t) / height, 0.0), 1.0)
        cx = x_min + fx * (x_max - x_min)
        cy = y_min + fy * (y_max - y_min)
        new_x = (x_max - x_min) * factor
        new_y = (y_max - y_min) * factor
        full_x = self._bounds[1] - self._bounds[0]
        full_y = self._bounds[3] - self._bounds[2]
        if new_x > full_x and new_y > full_y:
            self.reset_view()
            return
        if new_x < full_x / 200 or new_y < full_y / 200:
            return
        self._view = (cx - fx * new_x, cx + (1 - fx) * new_x,
                      cy - fy * new_y, cy + (1 - fy) * new_y)
        self.redraw()


class HistogramChart(tk.Frame):
    """Distribution des remunerations. Survol pour lire une classe."""

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self.bins: List[Dict[str, float]] = []
        self.currency = "EUR"
        self.warning = ""
        self._items: Dict[int, Dict[str, float]] = {}
        self.canvas.bind("<Configure>", lambda _e: self.redraw())
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())

    def set_distribution(self, distribution: Dict[str, Any],
                         currency: str = "EUR") -> None:
        self.bins = list((distribution or {}).get("bins") or [])
        self.warning = (distribution or {}).get("warning") or ""
        self.currency = currency
        self.redraw()

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 60 or height < 60:
            return
        if not self.bins:
            self.canvas.create_text(
                width / 2, height / 2, fill=MUTED, font=note_font(),
                text=self.warning or "Aucune distribution à afficher")
            return

        pad_l, pad_r, pad_t, pad_b = 60, 20, 18, 46
        plot_w = max(width - pad_l - pad_r, 10)
        plot_h = max(height - pad_t - pad_b, 10)
        peak = max(item["count"] for item in self.bins) or 1
        bar_w = plot_w / len(self.bins)

        for value in nice_ticks(0, peak):
            y = pad_t + plot_h - value / peak * plot_h
            self.canvas.create_line(pad_l, y, pad_l + plot_w, y, fill=GRID)
            self.canvas.create_text(pad_l - 8, y, anchor="e", fill=MUTED,
                                    font=axis_font(),
                                    text=format_number(value, 0))
        for index, item in enumerate(self.bins):
            bar_h = plot_h * item["count"] / peak
            x = pad_l + index * bar_w
            handle = self.canvas.create_rectangle(
                # Un filet d'air entre les barres : accolees, l'histogramme
                # se lit comme un aplat.
                x + 2, pad_t + plot_h - bar_h, x + bar_w - 2, pad_t + plot_h,
                fill=ACCENT, outline="")
            self._items[handle] = item
        self.canvas.create_line(pad_l, pad_t + plot_h, pad_l + plot_w,
                                pad_t + plot_h, fill="#9aa7b4")
        # Les deux bornes exactes cedent la place a des graduations rondes :
        # « 9 391 EUR » et « 137 074 EUR » ne se lisaient pas d'un coup d'oeil.
        low = self.bins[0]["lower"]
        high = self.bins[-1]["upper"]
        span = (high - low) or 1.0
        for value in nice_ticks(low, high, 5):
            self.canvas.create_text(
                pad_l + (value - low) / span * plot_w, pad_t + plot_h + 14,
                fill=MUTED, font=axis_font(),
                text=format_money(value, self.currency))
        self.canvas.create_text(pad_l + plot_w / 2, pad_t + plot_h + 32, fill=MUTED,
                                font=axis_font(),
                                text="Effectif par classe de rémunération")

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
            if item in self._items:
                data = self._items[item]
                self.tooltip.show(
                    f'{format_money(data["lower"], self.currency)} — '
                    f'{format_money(data["upper"], self.currency)}\n'
                    f'{int(data["count"])} salariés',
                    self.canvas.winfo_rootx() + event.x,
                    self.canvas.winfo_rooty() + event.y)
                return
        self.tooltip.hide()


class BandChart(tk.Frame):
    """Repartition par tranche, en barres horizontales.

    Un tableau donne les chiffres, une barre donne la forme. Pour une
    structure d'age ou d'anciennete, c'est la forme qui se lit d'abord :
    savoir que 38 % des salaries ont entre cinq et dix ans d'anciennete
    demande un effort de lecture qu'une barre epargne.

    Les chiffres restent affiches — la barre les accompagne, elle ne les
    remplace pas.
    """

    ROW = 26
    LABEL = 118
    VALUE = 96

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.rows: List[Dict[str, Any]] = []
        self.canvas.bind("<Configure>", lambda _e: self.redraw())

    def set_rows(self, rows: Sequence[Dict[str, Any]]) -> None:
        self.rows = [dict(row) for row in rows]
        self.configure(height=max(len(self.rows), 1) * self.ROW + 6)
        self.pack_propagate(False)
        self.redraw()

    def redraw(self) -> None:
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        if width < 80 or not self.rows:
            return
        peak = max((row.get("share") or 0.0) for row in self.rows) or 1.0
        track = max(width - self.LABEL - self.VALUE - 12, 20)
        for index, row in enumerate(self.rows):
            middle = index * self.ROW + self.ROW / 2 + 3
            self.canvas.create_text(0, middle, anchor="w", fill=INK,
                                    font=note_font(), text=row.get("label", ""))
            share = row.get("share") or 0.0
            # La barre est proportionnee a la tranche la plus fournie, non a
            # 100 % : sur une repartition ecrasee, tout serait illisible.
            length = max(track * share / peak, 1.0)
            self.canvas.create_rectangle(
                self.LABEL, middle - 7, self.LABEL + length, middle + 7,
                fill=ACCENT, outline="")
            self.canvas.create_text(
                width, middle, anchor="e", fill=MUTED, font=note_font(),
                text=f'{row.get("count", 0)}   {format_number(share, 1)} %')
