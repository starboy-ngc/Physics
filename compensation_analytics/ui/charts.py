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
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Sequence

from ..core.axes import nice_ticks
from ..core.reporting import format_money, format_number, format_years
from . import raster
from . import theme
from .theme import SIZE_LABEL, SIZE_SMALL, _rgb, pick_family

# Les filets du fond, la droite de tendance et les deux ailes de la pyramide
# ne sont plus decrits ici : ils viennent de la palette, qui sert aussi les
# documents. `theme.GRID`, `theme.FEMALE` et `theme.MALE` sont relus a chaque
# trace, donc un changement de theme n'oblige a rien reimporter.

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


#: Delai avant de retracer apres un redimensionnement. Assez court pour que
#: le trace paraisse suivre la fenetre, assez long pour absorber une rafale.
RESIZE_DELAY = 60


def redraw_on_resize(chart: tk.Frame, canvas: tk.Canvas) -> None:
    """Retrace quand le redimensionnement s'arrete, et non a chaque pixel.

    Tk envoie un « Configure » par pixel parcouru. Le nuage de deux mille
    points met 129 ms a se tracer — mesure — : le suivre pixel par pixel
    transforme un redimensionnement de fenetre, ou le repli de la colonne de
    gauche, en diaporama. Seul le dernier evenement d'une rafale est donc
    honore.
    """
    pending: Dict[str, Any] = {"job": None}

    def fire() -> None:
        pending["job"] = None
        if chart.winfo_exists():
            chart.redraw()

    def cancel(_event=None) -> None:
        if pending["job"] is not None:
            try:
                chart.after_cancel(pending["job"])
            except tk.TclError:
                pass
            pending["job"] = None

    def schedule(_event=None) -> None:
        cancel()
        pending["job"] = chart.after(RESIZE_DELAY, fire)

    canvas.bind("<Configure>", schedule)
    # Un trace en attente survit au widget : Tk tente alors d'appeler une
    # commande supprimee et ecrit « invalid command name » sur la sortie
    # d'erreur. Fermer la fenetre avec un redimensionnement en cours suffisait
    # a le declencher.
    chart.bind("<Destroy>", cancel, add="+")


def _shorten(widget: tk.Misc, text: str, limit: float) -> str:
    """Tronque un libelle a la largeur donnee, en mesurant plutot qu'en devinant."""
    import tkinter.font as tkfont

    font = tkfont.Font(root=widget, font=axis_font())
    if font.measure(text) <= limit:
        return text
    while text and font.measure(text + "…") > limit:
        text = text[:-1]
    return text + "…"


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
                self.window, justify="left", background=theme.INK, foreground="white",
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
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS, highlightthickness=0)
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

        redraw_on_resize(self, self.canvas)
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
                or "Aucun point a afficher", fill=theme.MUTED, font=note_font())
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
            self.canvas.create_line(pad_l, y, pad_l + plot_w, y, fill=theme.GRID)
            self.canvas.create_text(
                pad_l - 8, y, anchor="e", fill=theme.MUTED, font=axis_font(),
                text=format_money(value, self.currency))
        for value in nice_ticks(x_min, x_max):
            x = pad_l + (value - x_min) / x_span * plot_w
            self.canvas.create_text(
                x, pad_t + plot_h + 14, fill=theme.MUTED, font=axis_font(),
                text=format_number(value, 0))
        self.canvas.create_line(pad_l, pad_t + plot_h, pad_l + plot_w,
                                pad_t + plot_h, fill=theme.LINE_STRONG)
        self.canvas.create_text(pad_l + plot_w / 2, pad_t + plot_h + 32,
                                text="Ancienneté (années)", fill=theme.MUTED,
                                font=axis_font())

        groups = self.dataset.get("groups") or []
        # La serie vient du theme actif et non d'une copie prise a
        # l'import : figee, elle gardait les couleurs du theme par defaut.
        colours = {g: theme.ACTIVE.series_for(i) for i, g in enumerate(groups)}

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
            colour = colours.get(point["group"], theme.ACCENT)
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
                                    fill=theme.CRIT, width=2, dash=(6, 4))

        total = len(self.points)
        note = f"{shown} points affichés sur {total}"
        if self.hidden:
            note += f" · {len(self.hidden)} population(s) masquée(s)"
        if self._view != self._bounds:
            note += " · zoom actif, double-clic pour réinitialiser"
        self.canvas.create_text(pad_l, pad_t - 6, anchor="sw", text=note,
                                fill=theme.MUTED, font=axis_font())

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
                data = raster.disc(self.DOT_SELECTED, _rgb(theme.CRIT),
                                   ring=_rgb(theme.INK), ring_width=2.0)
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
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self.bins: List[Dict[str, float]] = []
        self.currency = "EUR"
        self.warning = ""
        self._items: Dict[int, Dict[str, float]] = {}
        redraw_on_resize(self, self.canvas)
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
                width / 2, height / 2, fill=theme.MUTED, font=note_font(),
                text=self.warning or "Aucune distribution à afficher")
            return

        pad_l, pad_r, pad_t, pad_b = 60, 20, 18, 46
        plot_w = max(width - pad_l - pad_r, 10)
        plot_h = max(height - pad_t - pad_b, 10)
        peak = max(item["count"] for item in self.bins) or 1
        bar_w = plot_w / len(self.bins)

        for value in nice_ticks(0, peak):
            y = pad_t + plot_h - value / peak * plot_h
            self.canvas.create_line(pad_l, y, pad_l + plot_w, y, fill=theme.GRID)
            self.canvas.create_text(pad_l - 8, y, anchor="e", fill=theme.MUTED,
                                    font=axis_font(),
                                    text=format_number(value, 0))
        for index, item in enumerate(self.bins):
            bar_h = plot_h * item["count"] / peak
            x = pad_l + index * bar_w
            handle = self.canvas.create_rectangle(
                # Un filet d'air entre les barres : accolees, l'histogramme
                # se lit comme un aplat.
                x + 2, pad_t + plot_h - bar_h, x + bar_w - 2, pad_t + plot_h,
                fill=theme.ACCENT, outline="")
            self._items[handle] = item
        self.canvas.create_line(pad_l, pad_t + plot_h, pad_l + plot_w,
                                pad_t + plot_h, fill=theme.LINE_STRONG)
        # Les deux bornes exactes cedent la place a des graduations rondes :
        # « 9 391 EUR » et « 137 074 EUR » ne se lisaient pas d'un coup d'oeil.
        low = self.bins[0]["lower"]
        high = self.bins[-1]["upper"]
        span = (high - low) or 1.0
        for value in nice_ticks(low, high, 5):
            self.canvas.create_text(
                pad_l + (value - low) / span * plot_w, pad_t + plot_h + 14,
                fill=theme.MUTED, font=axis_font(),
                text=format_money(value, self.currency))
        self.canvas.create_text(pad_l + plot_w / 2, pad_t + plot_h + 32, fill=theme.MUTED,
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


class BoxPlotChart(tk.Frame):
    """Boites a moustaches : une par segment, couchees.

    Un tableau de medianes cache l'essentiel : deux postes de meme mediane
    peuvent avoir des grilles sans rapport, l'un resserre, l'autre ouvert du
    simple au triple. La boite montre les deux d'un regard — P10 et P90 aux
    extremites, le coeur de l'effectif entre Q1 et Q3, la mediane en trait.

    Couchees, et non dressees : un libelle de poste tient a gauche sans etre
    incline, la ou vingt libelles dresses seraient illisibles.
    """

    #: Hauteur d'une ligne. On la reduit jusqu'au plancher pour faire tenir
    #: le plus de segments possible, sans jamais coller les boites entre elles.
    ROW_MAX, ROW_MIN = 40, 17
    LABEL_MAX = 190

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        # Deux canevas : les lignes defilent, l'axe et la cle restent. Tout
        # faire defiler ferait sortir la graduation de l'ecran au moment
        # precis ou l'on regarde une boite lointaine, et une boite sans
        # graduation ne dit plus rien.
        self.footer = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0,
                                height=self.FOOTER_HEIGHT)
        self.footer.pack(side="bottom", fill="x")
        self.bar = ttk.Scrollbar(self, orient="vertical",
                                 style="Flat.Vertical.TScrollbar")
        self.canvas = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0)
        self.bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.bar.configure(command=self.canvas.yview)
        theme.attach_scrollbar(self.canvas, self.bar, side="right", fill="y",
                               before=self.canvas)
        self.tooltip = Tooltip(self.canvas)
        self.rows: List[Dict[str, Any]] = []
        self.currency = "EUR"
        self.warning = ""
        self.reference: Optional[float] = None
        self.order = "dimension"
        self._items: Dict[int, Dict[str, Any]] = {}
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())
        # La molette sur le graphique : atteindre le vingtieme metier a
        # l'ascenseur seulement serait une corvee. Le rappel est annule a la
        # destruction : sans cela, un graphique ferme avant le premier temps
        # mort laissait Tk executer un rappel sur un widget disparu.
        wheel = self.after_idle(lambda: theme.bind_wheel(
            self.canvas, self.winfo_toplevel()))
        self.bind("<Destroy>", lambda event, job=wheel: self._forget(event,
                                                                    job),
                  add="+")

    def _forget(self, event, job: str) -> None:
        """Annule le rappel en attente quand le graphique disparait."""
        if event.widget is not self:
            return
        try:
            self.after_cancel(job)
        except tk.TclError:
            pass

    #: Tris proposes. La cle est technique, l'intitule s'affiche.
    ORDERS = (("dimension", "Ordre de la dimension"),
              ("median", "Médiane décroissante"),
              ("headcount", "Effectif décroissant"))

    def set_order(self, key: str) -> None:
        """Change l'ordre des boites sans recalculer quoi que ce soit."""
        self.order = key if key in dict(self.ORDERS) else "dimension"
        self.redraw()

    def _sorted(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ordre demande. « dimension » est celui qu'a etabli le moteur —
        alphabetique, ou celui des grades — et sert de reference commune avec
        l'onglet Segments."""
        if self.order == "median":
            return sorted(rows, key=lambda row: -(row["salary"]["median"] or 0))
        if self.order == "headcount":
            return sorted(rows, key=lambda row: -(row.get("headcount") or 0))
        return rows

    def set_rows(self, rows: Sequence[Dict[str, Any]], currency: str = "EUR",
                 warning: str = "", reference: Optional[float] = None) -> None:
        """Lignes de segment, dans l'ordre etabli par le moteur.

        `reference` est la mediane de l'ensemble analyse : tracee en repere,
        elle rend lisible d'un regard ce qui est au-dessus et au-dessous,
        sans avoir a comparer des montants de tete.
        """
        self.rows = [dict(row) for row in rows or []]
        self.currency = currency
        self.warning = warning
        self.reference = reference
        self.redraw()

    def _withheld(self) -> int:
        """Segments publiables mais trop peu nombreux pour etre traces."""
        return sum(1 for row in self.rows
                   if not row.get("masked") and row.get("chartable") is not True)

    def _drawable(self) -> List[Dict[str, Any]]:
        """Segments que l'on a le droit de tracer.

        Le drapeau vient du moteur, et son absence vaut refus : une regle de
        confidentialite ne se decide pas ici, et une donnee arrivee sans son
        drapeau ne doit pas etre dessinee par defaut.
        """
        ready = []
        for row in self.rows:
            salary = row.get("salary") or {}
            if row.get("masked") or row.get("chartable") is not True:
                continue
            if any(salary.get(key) is None for key in ("p25", "p75", "median")):
                continue
            ready.append(row)
        return self._sorted(ready)

    def _refusal(self) -> str:
        """Ce que l'on dit quand rien n'est tracable."""
        if any(not row.get("masked") for row in self.rows):
            return ("Effectif par segment insuffisant pour tracer une "
                    "dispersion. Les valeurs restent lisibles dans l'onglet "
                    "Segments.")
        return "Aucun segment publiable sur cette dimension."

    def redraw(self) -> None:
        self.canvas.delete("all")
        self.footer.delete("all")
        self._items.clear()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 120 or height < 60:
            return
        drawable = self._drawable()
        if not drawable:
            self.canvas.configure(scrollregion=(0, 0, width, height))
            self.canvas.create_text(
                width / 2, height / 2, fill=theme.MUTED, font=note_font(),
                text=self.warning or self._refusal(), width=max(width - 60, 80),
                justify="center")
            return

        label_width = self._label_width(drawable)
        count_width = self._count_width(drawable)
        # Une colonne pour l'effectif entre le libelle et le trace : une boite
        # dessinee sur douze salaries a la meme allure qu'une boite dessinee
        # sur quatre cents, et rien ne le disait hors du survol.
        pad_l = label_width + 12 + count_width + 14
        # De la place en haut pour l'intitule du repere, et seulement quand
        # il y a un repere a poser.
        pad_r = 30
        pad_t = 26 if self.reference is not None else 12
        plot_w = max(width - pad_l - pad_r, 20)
        plot_h = max(height - pad_t - 10, 20)

        # Plus de troncature : la ligne s'etire jusqu'a son confort maximal
        # quand les segments tiennent, et se pose sur son plancher quand ils
        # ne tiennent pas — la page defile alors. Ecarter des segments faute
        # de place revenait a cacher une partie de la reponse.
        row_height = min(self.ROW_MAX, max(plot_h / len(drawable),
                                           self.ROW_MIN))
        low, high = self._span(drawable)
        span = (high - low) or 1.0
        base = pad_t + len(drawable) * row_height

        def to_x(value: float) -> float:
            return pad_l + (value - low) / span * plot_w

        # La zone defilante couvre toutes les lignes, jamais moins que la
        # fenetre : sinon un graphique court se recadrerait tout seul.
        self.canvas.configure(scrollregion=(0, 0, width,
                                            max(base + 10, height)))

        for value in self._ticks(low, high, plot_w):
            x = to_x(value)
            self.canvas.create_line(x, pad_t, x, base, fill=theme.GRID)

        # Le repere d'ensemble, trace avant les boites pour passer dessous.
        if self.reference is not None and low <= self.reference <= high:
            x = to_x(self.reference)
            self.canvas.create_line(x, pad_t - 4, x, base, fill=theme.ACCENT,
                                    dash=(4, 3))
            self.canvas.create_text(x + 5, pad_t - 8, anchor="sw",
                                    fill=theme.ACCENT, font=axis_font(),
                                    text="Médiane d'ensemble : "
                                         f"{format_money(self.reference, self.currency)}")

        for index, row in enumerate(drawable):
            self._draw_box(row, index, row_height, pad_l, label_width, to_x)

        self._draw_footer(label_width, pad_l, plot_w, to_x, low, high)

    #: Hauteur du pied fixe : graduations, puis cle de lecture.
    FOOTER_HEIGHT = 74
    #: Hauteur reservee sous les graduations pour la cle de lecture.
    LEGEND_HEIGHT = 46
    #: Largeur du schema explicatif. Assez large pour que les cinq intitules
    #: tiennent sans se chevaucher — mesure faite a la chasse des axes.
    LEGEND_WIDTH = 190

    def _draw_footer(self, label_width: float, pad_l: float, plot_w: float,
                     to_x, low: float, high: float) -> None:
        """Graduations et cle de lecture, hors de la zone qui defile."""
        for value in self._ticks(low, high, plot_w):
            self.footer.create_text(to_x(value), 12, fill=theme.MUTED,
                                    font=axis_font(),
                                    text=format_money(value, self.currency))
        self._draw_key(label_width, 26, plot_w)

    def _draw_key(self, x: float, y: float, available: float) -> None:
        """Cle de lecture : une boite miniature, legendee, puis une phrase.

        Une boite a moustaches ne se devine pas. « P10, Q1, mediane, Q3,
        P90 » en pied de graphique ne l'explique pas davantage : c'est une
        liste de sigles. Le schema montre a quoi chaque trait correspond, et
        la phrase dit ce que la boite contient — sans quoi le graphique le
        plus utile de l'outil reste le plus opaque.
        """
        wide = self.LEGEND_WIDTH
        left, mid = x, y + 6
        canvas = self.footer
        q1, q3 = left + wide * 0.25, left + wide * 0.75
        median = left + wide * 0.5
        thickness = 9
        canvas.create_line(left, mid, left + wide, mid,
                                fill=theme.LINE_STRONG)
        for edge in (left, left + wide):
            canvas.create_line(edge, mid - thickness / 2, edge,
                                    mid + thickness / 2, fill=theme.LINE_STRONG)
        canvas.create_rectangle(q1, mid - thickness / 2, q3,
                                     mid + thickness / 2,
                                     fill=theme.ACCENT_SOFT, outline=theme.ACCENT)
        canvas.create_line(median, mid - thickness / 2 - 2, median,
                                mid + thickness / 2 + 2, fill=theme.INK, width=2)
        for position, text in ((left, "P10"), (q1, "Q1"), (median, "Médiane"),
                               (q3, "Q3"), (left + wide, "P90")):
            canvas.create_text(position, mid + 14, fill=theme.MUTED,
                                    font=axis_font(), text=text)

        # La phrase demande de la place : dans un bloc etroit, le schema
        # legende suffit, et une phrase coupee en trois mots par ligne
        # n'explique plus rien.
        room = available - wide - 40
        if room < 190:
            return
        phrase = ("La boîte contient la moitié des salariés du segment ; "
                  "le trait, la médiane. Les moustaches vont du 10e au 90e "
                  "centile.")
        withheld = self._withheld()
        if withheld:
            phrase += (f" {withheld} segment(s) trop peu nombreux pour être "
                       "tracés — voir l'onglet Segments.")
        canvas.create_text(left + wide + 30, mid - 5, anchor="nw",
                                fill=theme.MUTED, font=axis_font(),
                                width=room, text=phrase)

    def _label_width(self, rows: Sequence[Dict[str, Any]]) -> float:
        """Gouttiere des libelles, mesuree et non devinee."""
        import tkinter.font as tkfont

        font = tkfont.Font(root=self, font=axis_font())
        widest = max((font.measure(str(row.get("segment", ""))) for row in rows),
                     default=60)
        return min(max(widest, 60), self.LABEL_MAX)

    def _ticks(self, low: float, high: float, plot_w: float) -> List[float]:
        """Graduations qui tiennent cote a cote, mesurees et non estimees.

        Le nombre demande a `nice_ticks` n'est qu'un souhait : la fonction
        rend le pas rond le plus proche, quitte a poser une graduation de
        plus. Dans une demi-page, trois montants a six chiffres se
        chevauchaient. On en retire donc une sur deux tant qu'ils ne tiennent
        pas cote a cote.
        """
        import tkinter.font as tkfont

        font = tkfont.Font(root=self, font=axis_font())
        values = list(nice_ticks(low, high, 5))
        while len(values) > 2:
            largest = max(font.measure(format_money(value, self.currency))
                          for value in values)
            if (largest + 16) * len(values) <= plot_w:
                break
            values = values[::2]
        return values

    def _count_width(self, rows: Sequence[Dict[str, Any]]) -> float:
        """Colonne des effectifs, a la chasse du plus grand nombre."""
        import tkinter.font as tkfont

        font = tkfont.Font(root=self, font=axis_font())
        return max((font.measure(str(row.get("headcount", 0))) for row in rows),
                   default=24)

    def _span(self, rows: Sequence[Dict[str, Any]]):
        """Etendue commune a toutes les boites : sans elle, rien ne se compare."""
        lows, highs = [], []
        for row in rows:
            salary = row["salary"]
            lows.append(self._whisker(salary, "p10", "p25"))
            highs.append(self._whisker(salary, "p90", "p75"))
        low, high = min(lows), max(highs)
        # Le repere fait partie de l'echelle : hors d'elle, il se tracerait
        # au bord du cadre et mentirait sur sa position.
        if self.reference is not None:
            low, high = min(low, self.reference), max(high, self.reference)
        margin = (high - low) * 0.04 or 1.0
        return low - margin, high + margin

    @staticmethod
    def _whisker(salary: Dict[str, Any], preferred: str, fallback: str) -> float:
        value = salary.get(preferred)
        return float(value if value is not None else salary[fallback])

    def _draw_box(self, row, index: int, row_height: float, pad_l: float,
                  label_width: float, to_x) -> None:
        salary = row["salary"]
        centre = 14 + index * row_height + row_height / 2
        thickness = min(max(row_height * 0.42, 5.0), 15.0)
        p10 = self._whisker(salary, "p10", "p25")
        p90 = self._whisker(salary, "p90", "p75")
        q1, q3 = float(salary["p25"]), float(salary["p75"])
        median = float(salary["median"])

        # Moustaches d'abord : la boite les recouvre, ce qui evite un trait
        # qui depasserait a l'interieur.
        self.canvas.create_line(to_x(p10), centre, to_x(p90), centre,
                                fill=theme.LINE_STRONG)
        for value in (p10, p90):
            self.canvas.create_line(to_x(value), centre - thickness / 2,
                                    to_x(value), centre + thickness / 2,
                                    fill=theme.LINE_STRONG)
        handle = self.canvas.create_rectangle(
            to_x(q1), centre - thickness / 2, to_x(q3), centre + thickness / 2,
            fill=theme.ACCENT_SOFT, outline=theme.ACCENT)
        # La mediane est le chiffre que l'on cite : elle est le seul trait
        # dense de la boite.
        self.canvas.create_line(to_x(median), centre - thickness / 2 - 2,
                                to_x(median), centre + thickness / 2 + 2,
                                fill=theme.INK, width=2)
        self.canvas.create_text(label_width, centre, anchor="e",
                                fill=theme.INK_SOFT, font=axis_font(),
                                text=_shorten(self, str(row.get("segment", "")),
                                              self.LABEL_MAX))
        # L'effectif : une boite tracee sur douze salaries a la meme allure
        # qu'une boite tracee sur quatre cents.
        self.canvas.create_text(pad_l - 14, centre, anchor="e",
                                fill=theme.FAINT, font=axis_font(),
                                text=str(row.get("headcount", 0)))
        self._items[handle] = row

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y,
                                                 event.x, event.y):
            if item in self._items:
                row = self._items[item]
                salary = row["salary"]
                lines = [f'{row.get("segment", "")} · {row.get("headcount", 0)} salariés']
                for label, key in (("P90", "p90"), ("Q3", "p75"),
                                   ("Médiane", "median"), ("Q1", "p25"),
                                   ("P10", "p10")):
                    if salary.get(key) is not None:
                        lines.append(
                            f'{label} : {format_money(salary[key], self.currency)}')
                self.tooltip.show("\n".join(lines),
                                  self.canvas.winfo_rootx() + event.x,
                                  self.canvas.winfo_rooty() + event.y)
                return
        self.tooltip.hide()


class GapChart(tk.Frame):
    """Ecarts de remuneration par categorie, de part et d'autre d'un zero.

    Dix pourcentages signes dans un tableau demandent d'etre lus un par un
    pour reperer les deux qui sortent. Poses autour d'un axe zero, tries par
    ampleur, ils se hierarchisent d'eux-memes — et le seuil de la directive,
    trace en pointille, dit d'un regard qui le franchit.

    Convention de signe, la meme que partout : un ecart positif signifie que
    les femmes sont moins remunerees.
    """

    ROW_MAX, ROW_MIN = 30, 16
    LABEL_MAX = 170

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self.rows: List[Dict[str, Any]] = []
        self.threshold = 0.0
        self.warning = ""
        self._items: Dict[int, Dict[str, Any]] = {}
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())

    def set_rows(self, rows: Sequence[Dict[str, Any]], threshold: float = 0.0,
                 warning: str = "") -> None:
        self.rows = [dict(row) for row in rows or []]
        self.threshold = float(threshold or 0.0)
        self.warning = warning
        self.redraw()

    def _drawable(self) -> List[Dict[str, Any]]:
        """Categories dont l'ecart a ete publie par le moteur."""
        return [row for row in self.rows
                if row.get("published") and row.get("mean_gap") is not None]

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 120 or height < 60:
            return
        drawable = self._drawable()
        if not drawable:
            self.canvas.create_text(
                width / 2, height / 2, fill=theme.MUTED, font=note_font(),
                width=max(width - 60, 80), justify="center",
                text=self.warning or "Aucune catégorie ne réunit assez de "
                                     "femmes et d'hommes pour publier un écart.")
            return

        label_width = self._label_width(drawable)
        pad_l = label_width + 16
        pad_r, pad_t, pad_b = 46, 12, 34
        plot_w = max(width - pad_l - pad_r, 20)
        plot_h = max(height - pad_t - pad_b, 20)
        row_height = min(self.ROW_MAX, plot_h / len(drawable))
        shown = drawable
        if row_height < self.ROW_MIN:
            row_height = self.ROW_MIN
            shown = drawable[:max(int(plot_h // row_height), 1)]

        # Echelle symetrique : sans elle, un ecart de +6 % et un de -6 %
        # n'auraient pas la meme longueur, et la comparaison serait faussee.
        reach = max(max(abs(row["mean_gap"]) for row in shown),
                    self.threshold, 1.0) * 1.15
        zero = pad_l + plot_w / 2

        def to_x(value: float) -> float:
            return zero + value / reach * (plot_w / 2)

        base = pad_t + len(shown) * row_height
        for sign in (-1, 1):
            if self.threshold > 0:
                x = to_x(sign * self.threshold)
                self.canvas.create_line(x, pad_t, x, base, fill=theme.WARN,
                                        dash=(3, 3))
        self.canvas.create_line(zero, pad_t, zero, base, fill=theme.LINE_STRONG)

        for index, row in enumerate(shown):
            gap = float(row["mean_gap"])
            centre = pad_t + index * row_height + row_height / 2
            thickness = min(max(row_height * 0.5, 5.0), 14.0)
            # Au-dela du seuil, la barre passe en teinte de vigilance : c'est
            # le seul endroit ou la couleur porte un jugement, et il vient du
            # seuil parametre, pas d'une appreciation.
            colour = theme.WARN if row.get("above_threshold") else theme.ACCENT
            handle = self.canvas.create_rectangle(
                min(zero, to_x(gap)), centre - thickness / 2,
                max(zero, to_x(gap)), centre + thickness / 2,
                fill=colour, outline="")
            self._items[handle] = row
            self.canvas.create_text(pad_l - 10, centre, anchor="e",
                                    fill=theme.INK_SOFT, font=axis_font(),
                                    text=_shorten(self, str(row.get("category", "")),
                                                  self.LABEL_MAX))
            # La valeur au bout de la barre : on lit l'ordre sur le graphique
            # et le chiffre sans survoler.
            end = to_x(gap)
            self.canvas.create_text(
                end + (6 if gap >= 0 else -6), centre,
                anchor="w" if gap >= 0 else "e", fill=theme.MUTED,
                font=axis_font(), text=f"{gap:+.1f} %".replace(".", ","))

        legend = "Écart positif : les femmes sont moins rémunérées"
        if self.threshold > 0:
            legend += f" · seuil {self.threshold:.0f} %".replace(".", ",")
        hidden = len(drawable) - len(shown)
        if hidden:
            legend += f" · {hidden} catégorie(s) non affichée(s)"
        self.canvas.create_text(pad_l - label_width, base + 18, anchor="w",
                                fill=theme.MUTED, font=axis_font(), text=legend)

    def _label_width(self, rows: Sequence[Dict[str, Any]]) -> float:
        import tkinter.font as tkfont

        font = tkfont.Font(root=self, font=axis_font())
        widest = max((font.measure(str(row.get("category", ""))) for row in rows),
                     default=60)
        return min(max(widest, 60), self.LABEL_MAX)

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y,
                                                 event.x, event.y):
            if item in self._items:
                row = self._items[item]
                lines = [f'{row.get("category", "")} · {row.get("headcount", 0)} salariés',
                         f'{row.get("female_count", 0)} femmes, '
                         f'{row.get("male_count", 0)} hommes']
                for label, key in (("Écart moyen", "mean_gap"),
                                   ("Écart médian", "median_gap")):
                    value = row.get(key)
                    if value is not None:
                        lines.append(f'{label} : {value:+.1f} %'.replace(".", ","))
                self.tooltip.show("\n".join(lines),
                                  self.canvas.winfo_rootx() + event.x,
                                  self.canvas.winfo_rooty() + event.y)
                return
        self.tooltip.hide()


class QuartileChart(tk.Frame):
    """Part de chaque sexe dans chaque quartile de remuneration.

    Indicateur f) de la directive. Quatre barres empilees disent en un
    regard ce qu'un tableau de quatre lignes demande de comparer de tete :
    si la part des femmes s'effrite en montant dans les quartiles, le
    plafond est la, dessine.
    """

    ROW = 34

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0, height=4 * self.ROW + 34)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self.rows: List[Dict[str, Any]] = []
        self._items: Dict[int, Dict[str, Any]] = {}
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())

    def set_rows(self, rows: Sequence[Dict[str, Any]]) -> None:
        self.rows = [dict(row) for row in rows or []]
        self.redraw()

    def _drawable(self) -> List[Dict[str, Any]]:
        return [row for row in self.rows if row.get("female_share") is not None]

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        width = self.canvas.winfo_width()
        if width < 120:
            return
        drawable = self._drawable()
        if not drawable:
            self.canvas.create_text(
                width / 2, 30, fill=theme.MUTED, font=note_font(),
                text="Effectif par quartile insuffisant pour publier une "
                     "répartition.")
            return
        pad_l, pad_r, pad_t = 116, 20, 8
        plot_w = max(width - pad_l - pad_r, 40)
        for index, row in enumerate(drawable):
            y = pad_t + index * self.ROW
            female = float(row.get("female_share") or 0.0)
            cut = pad_l + female / 100.0 * plot_w
            left = self.canvas.create_rectangle(pad_l, y, cut, y + self.ROW - 12,
                                                fill=theme.FEMALE, outline="")
            right = self.canvas.create_rectangle(cut, y, pad_l + plot_w,
                                                 y + self.ROW - 12,
                                                 fill=theme.MALE, outline="")
            self._items[left] = self._items[right] = row
            rank = row.get("quartile", index + 1)
            edge = {1: " · le plus bas", len(drawable): " · le plus haut"}.get(rank, "")
            self.canvas.create_text(pad_l - 10, y + (self.ROW - 12) / 2,
                                    anchor="e", fill=theme.INK_SOFT,
                                    font=axis_font(), text=f"Q{rank}{edge}")
            # La part est ecrite dans la barre quand elle y tient : lire un
            # plafond de verre demande le chiffre, pas seulement la longueur.
            if female >= 12:
                self.canvas.create_text(
                    pad_l + 8, y + (self.ROW - 12) / 2, anchor="w",
                    fill=theme.CANVAS, font=axis_font(),
                    text=f"{female:.0f} %".replace(".", ","))
            male = float(row.get("male_share") or 0.0)
            if male >= 12:
                self.canvas.create_text(
                    pad_l + plot_w - 8, y + (self.ROW - 12) / 2, anchor="e",
                    fill=theme.CANVAS, font=axis_font(),
                    text=f"{male:.0f} %".replace(".", ","))
        base = pad_t + len(drawable) * self.ROW
        self.canvas.create_text(pad_l, base + 4, anchor="w", fill=theme.FEMALE,
                                font=axis_font(), text="FEMMES")
        self.canvas.create_text(pad_l + plot_w, base + 4, anchor="e",
                                fill=theme.MALE, font=axis_font(), text="HOMMES")

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y,
                                                 event.x, event.y):
            if item in self._items:
                row = self._items[item]
                self.tooltip.show(
                    f'Quartile {row.get("quartile")} · '
                    f'{row.get("headcount", 0)} salariés\n'
                    f'{row.get("female_count", 0)} femmes '
                    f'({row.get("female_share", 0):.1f} %)\n'
                    f'{row.get("male_count", 0)} hommes '
                    f'({row.get("male_share", 0):.1f} %)'.replace(".", ","),
                    self.canvas.winfo_rootx() + event.x,
                    self.canvas.winfo_rooty() + event.y)
                return
        self.tooltip.hide()


class PyramidChart(tk.Frame):
    """Pyramide : femmes a gauche, hommes a droite, tranches empilees.

    C'est la lecture classique d'une structure de population, et elle dit en
    un regard ce qu'un tableau demande de reconstituer : ou se concentrent
    les effectifs, et si la repartition entre les sexes bascule d'une
    tranche a l'autre.

    Les deux cotes partagent la meme echelle — sans quoi une aile deux fois
    plus courte pourrait representer le meme effectif.
    """

    ROW = 26
    #: Gouttiere centrale reservee aux libelles de tranche, et colonnes de
    #: chiffres aux extremites. Sans cette reserve, les barres recouvraient
    #: les libelles.
    GUTTER = 84
    COUNTS = 46

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.rows: List[Dict[str, Any]] = []
        self.tooltip = Tooltip(self.canvas)
        self._items: Dict[int, str] = {}
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())

    def set_rows(self, rows: Sequence[Dict[str, Any]]) -> None:
        # La plus jeune tranche en bas : une pyramide se lit de bas en haut.
        self.rows = list(reversed([dict(row) for row in rows]))
        self.configure(height=max(len(self.rows), 1) * self.ROW + 26)
        self.pack_propagate(False)
        self.redraw()

    def has_split(self) -> bool:
        """Vrai si le sexe est renseigne : sans lui, pas de pyramide."""
        return any(row.get("female") or row.get("male") for row in self.rows)

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        width = self.canvas.winfo_width()
        if width < 200 or not self.rows:
            return
        peak = max(max(row.get("female") or 0, row.get("male") or 0)
                   for row in self.rows) or 1
        # Les deux ailes partagent la meme echelle : sans quoi une aile deux
        # fois plus courte pourrait representer le meme effectif.
        wing = max((width - self.GUTTER - 2 * self.COUNTS) / 2, 20)
        centre = self.COUNTS + wing + self.GUTTER / 2
        left = centre - self.GUTTER / 2
        right = centre + self.GUTTER / 2

        self.canvas.create_text(left, 8, anchor="e", fill=theme.FEMALE,
                                font=axis_font(), text="FEMMES")
        self.canvas.create_text(right, 8, anchor="w", fill=theme.MALE,
                                font=axis_font(), text="HOMMES")
        for index, row in enumerate(self.rows):
            y = index * self.ROW + self.ROW / 2 + 20
            female = row.get("female") or 0
            male = row.get("male") or 0
            if female:
                item = self.canvas.create_rectangle(
                    left - wing * female / peak, y - 8, left, y + 8,
                    fill=theme.FEMALE, outline="")
                self._items[item] = f'{row["label"]} · {female} femmes'
                self.canvas.create_text(left - wing - 6, y, anchor="e",
                                        fill=theme.MUTED, font=axis_font(),
                                        text=str(female))
            if male:
                item = self.canvas.create_rectangle(
                    right, y - 8, right + wing * male / peak, y + 8,
                    fill=theme.MALE, outline="")
                self._items[item] = f'{row["label"]} · {male} hommes'
                self.canvas.create_text(right + wing + 6, y, anchor="w",
                                        fill=theme.MUTED, font=axis_font(),
                                        text=str(male))
            self.canvas.create_text(centre, y, fill=theme.INK, font=axis_font(),
                                    text=row.get("label", ""))

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y,
                                                 event.x, event.y):
            if item in self._items:
                self.tooltip.show(self._items[item],
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
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.rows: List[Dict[str, Any]] = []
        redraw_on_resize(self, self.canvas)

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
            self.canvas.create_text(0, middle, anchor="w", fill=theme.INK,
                                    font=note_font(), text=row.get("label", ""))
            share = row.get("share") or 0.0
            # La barre est proportionnee a la tranche la plus fournie, non a
            # 100 % : sur une repartition ecrasee, tout serait illisible.
            length = max(track * share / peak, 1.0)
            self.canvas.create_rectangle(
                self.LABEL, middle - 7, self.LABEL + length, middle + 7,
                fill=theme.ACCENT, outline="")
            self.canvas.create_text(
                width, middle, anchor="e", fill=theme.MUTED, font=note_font(),
                text=f'{row.get("count", 0)}   {format_number(share, 1)} %')
