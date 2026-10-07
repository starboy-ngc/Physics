"""Graphiques interactifs dessines sur un canevas tkinter.

Le nuage de points est l'ecran d'exploration : survol pour identifier un
salarie, molette pour zoomer, glisser pour se deplacer, clic sur la legende
pour isoler une population. Rien de tout cela n'est possible dans un document
imprime — c'est la raison d'etre de l'interface.

Les couleurs et les regles de lecture sont celles des restitutions, pour que
l'ecran et le document racontent la meme chose.
"""

from __future__ import annotations

import math
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Sequence

from ..core import palette
from ..core.axes import nice_ticks
from ..core.reporting import (format_money, format_number,
                              format_percent, format_years)
from . import raster
from . import theme
from .theme import (SIZE_LABEL, SIZE_SECTION, SIZE_SMALL, _rgb,
                    pick_family)

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


#: Famille a chasse fixe du systeme, relevee une fois. On retient la
#: famille et non la police : une police appartient a l'interpreteur Tk
#: qui l'a creee, une famille est un nom.
_fixed_family = None


def table_font():
    """Police a chasse fixe : trois colonnes de montants ne s'alignent pas
    avec une police proportionnelle, et des colonnes qui ne s'alignent pas
    ne se comparent pas.

    « TkFixedFont » est le nom d'une police, pas celui d'une famille :
    passe dans un tuple, Tk n'y reconnait aucune famille et retombe sur
    celle par defaut — proportionnelle. La bulle s'affichait donc en
    colonnes decalees, et un essai qui lisait le nom au lieu du rendu n'y
    voyait rien.

    On demande donc a la police nommee, dont Tk garantit la chasse fixe
    sur chaque systeme, de quelle famille elle est.
    """
    global _fixed_family
    if _fixed_family is None:
        _fixed_family = tkfont.nametofont("TkFixedFont").actual("family")
    return (_fixed_family, SIZE_SMALL)


def _font(size: int, weight: str = "normal"):
    """Police du module a une taille donnee, pour les canevas qui en
    melangent plusieurs sur une meme ligne."""
    return (_family, size, weight) if weight != "normal" else (_family, size)


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


def _text_width(widget: tk.Misc, text: str) -> float:
    """Largeur d'un libelle a la chasse des axes."""
    import tkinter.font as tkfont

    return tkfont.Font(root=widget, font=axis_font()).measure(text)


def _axis_bounds(low: float, high: float, margin: float = 0.04):
    """Bornes d'un axe : une marge, mais jamais de l'autre cote de zero.

    La marge evite que les points extremes collent aux bords. Appliquee sans
    reserve, elle ouvrait le cadre sous zero : une remuneration ou une
    anciennete ne sont jamais negatives, et un repere qui commence a
    -320 EUR montre un quart de cadre ou aucune donnee ne peut exister.

    La regle ne vaut que pour franchir zero. Elle ne cale pas l'origine a
    zero pour autant : sur des salaires de 25 000 a 80 000, un axe partant
    de zero ecraserait tout le nuage dans son tiers superieur, et c'est
    justement l'ecart entre ces salaires qu'on vient regarder.
    """
    pad = (high - low) * margin or 1
    bas, haut = low - pad, high + pad
    if low >= 0:
        bas = max(0.0, bas)
    if high <= 0:
        haut = min(0.0, haut)
    return bas, haut


def _shorten(widget: tk.Misc, text: str, limit: float, police=None) -> str:
    """Tronque un libelle a la largeur donnee, en mesurant plutot qu'en devinant.

    `police` sert aux libelles qui ne sont pas a la chasse des axes : un
    titre en gras est plus large a nombre de lettres egal, et compter les
    lettres le ferait deborder de sa case.
    """
    import tkinter.font as tkfont

    text = str(text or "")
    font = tkfont.Font(root=widget, font=police or axis_font())
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

    def show(self, text: str, x: int, y: int, tableau: bool = False) -> None:
        if self.window is None:
            self.window = tk.Toplevel(self.widget)
            self.window.wm_overrideredirect(True)
            self.window.attributes("-topmost", True)
            self.label = tk.Label(
                self.window, justify="left", background=theme.INK, foreground="white",
                padx=8, pady=5, font=note_font(),
            )
            self.label.pack()
        self.label.configure(text=text,
                             font=table_font() if tableau else note_font())
        self.window.wm_geometry(f"+{x + 16}+{y + 16}")
        self.window.deiconify()

    def hide(self) -> None:
        if self.window is not None:
            self.window.withdraw()


class ScatterChart(tk.Frame):
    """Nuage de points, explorable, sur deux axes au choix.

    Le zoom et le deplacement ne changent que la fenetre affichee : les
    donnees ne sont jamais filtrees a l'insu de l'utilisateur, et le compteur
    de points visibles le rappelle en permanence.
    """

    def __init__(self, master: tk.Widget, on_select: Optional[Callable] = None):
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        #: Couleurs imposees par la page, s'il y a lieu : {modalite: teinte}.
        self.series: Optional[Dict[str, str]] = None
        self.tooltip = Tooltip(self.canvas)
        self.on_select = on_select
        # Resolveur d'identite, pose par la fenetre : il rend « DUPONT
        # Marie » pour un numero de ligne, ou rien. Le graphique ne detient
        # aucune identite et n'en recoit aucune dans son jeu de donnees ;
        # il en demande une au moment de l'afficher.
        self.identify: Optional[Callable[[Any], str]] = None

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
        #: Plancher de chaque axe : le deplacement et le zoom ne descendent
        #: pas en dessous. None quand la grandeur peut etre negative.
        self._floors = (None, None)
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

    #: Unite par defaut d'un axe que le jeu de donnees ne decrit pas.
    AXIS_FALLBACK = {"label": "", "kind": "number"}

    def _axis(self, which: str) -> Dict[str, Any]:
        return self.dataset.get(f"{which}_axis") or self.AXIS_FALLBACK

    def _value(self, which: str, value: float) -> str:
        """Un nombre dans l'unite de son axe.

        Les deux axes se choisissent : la meme abscisse peut porter des
        euros, des annees ou un taux, et un montant annonce en annees ne se
        lit pas.
        """
        kind = self._axis(which).get("kind")
        if kind == "money":
            return format_money(value, self.currency)
        if kind == "years":
            return format_years(value)
        if kind == "ratio":
            return format_number(value, 2)
        return format_number(value, 0)

    def _tick(self, which: str, value: float) -> str:
        """Graduation : la meme unite, sans le suffixe qui alourdit."""
        kind = self._axis(which).get("kind")
        if kind == "money":
            return format_money(value, self.currency)
        if kind == "years":
            return format_years(value, suffix=False)
        if kind == "ratio":
            return format_number(value, 2)
        return format_number(value, 0)

    def _axis_title(self, which: str) -> str:
        axis = self._axis(which)
        unite = {"years": " (années)", "ratio": " (ETP)"}.get(
            axis.get("kind"), "")
        return f'{axis.get("label", "")}{unite}'

    def set_series(self, colours: Optional[Dict[str, str]]) -> None:
        """Impose la couleur de chaque modalite, ou rend la main a la serie."""
        self.series = dict(colours) if colours else None
        self.redraw()

    def set_dataset(self, dataset: Dict[str, Any], currency: str = "EUR") -> None:
        self.dataset = dataset or {}
        self.currency = currency
        self.points = list(self.dataset.get("points") or [])
        self.hidden.clear()
        self.selected = None
        self._bounds = self._compute_bounds(self.points)
        self._floors = self._compute_floors(self.points)
        self._view = self._bounds
        self.redraw()

    @staticmethod
    def _compute_bounds(points: Sequence[Dict[str, Any]]):
        if not points:
            return None
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        return (*_axis_bounds(min(xs), max(xs)),
                *_axis_bounds(min(ys), max(ys)))

    def _compute_floors(self, points: Sequence[Dict[str, Any]]):
        """Plancher de chaque axe, ou None s'il n'y en a pas.

        Le cadrage d'origine ne franchit pas zero, mais le deplacement et le
        zoom, eux, promenaient la fenetre ou ils voulaient : on se retrouvait
        a regarder des anciennetes negatives. Un plancher par axe suffit a
        l'interdire — et il n'existe que si la grandeur elle-meme ne descend
        jamais sous zero.
        """
        if not points:
            return (None, None)
        return (0.0 if min(p["x"] for p in points) >= 0 else None,
                0.0 if min(p["y"] for p in points) >= 0 else None)

    def _clamp_view(self, view):
        """Ramene la fenetre au-dessus des planchers, sans changer sa taille.

        On translate plutot qu'on ne rogne : rogner changerait le niveau de
        zoom sous les doigts de l'utilisateur, ce qui se lit comme un defaut.
        """
        x_min, x_max, y_min, y_max = view
        x_floor, y_floor = getattr(self, "_floors", (None, None))
        if x_floor is not None and x_min < x_floor:
            decalage = x_floor - x_min
            x_min, x_max = x_min + decalage, x_max + decalage
        if y_floor is not None and y_min < y_floor:
            decalage = y_floor - y_min
            y_min, y_max = y_min + decalage, y_max + decalage
        return (x_min, x_max, y_min, y_max)

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
                text=self._tick("y", value))
        for value in nice_ticks(x_min, x_max):
            x = pad_l + (value - x_min) / x_span * plot_w
            self.canvas.create_text(
                x, pad_t + plot_h + 14, fill=theme.MUTED, font=axis_font(),
                text=self._tick("x", value))
        self.canvas.create_line(pad_l, pad_t + plot_h, pad_l + plot_w,
                                pad_t + plot_h, fill=theme.LINE_STRONG)
        # Le titre de l'axe vient du jeu de donnees : les deux axes se
        # changent en cours de route, et « Anciennete (annees) » ecrit en
        # dur aurait annonce une chose pendant qu'on en regardait une autre.
        self.canvas.create_text(pad_l + plot_w / 2, pad_t + plot_h + 32,
                                text=self._axis_title("x"), fill=theme.MUTED,
                                font=axis_font())
        # Et le meme titre pour l'ordonnee, a la verticale contre le bord :
        # l'abscisse etait nommee, l'ordonnee ne l'etait pas, et c'est elle
        # qui porte la remuneration dans la lecture par defaut.
        self.canvas.create_text(14, pad_t + plot_h / 2, angle=90,
                                text=self._axis_title("y"), fill=theme.MUTED,
                                font=axis_font())

        # La serie vient du theme actif et non d'une copie prise a
        # l'import : figee, elle gardait les couleurs du theme par defaut.
        #
        # Une page peut imposer la sienne : sur un comparatif femmes /
        # hommes, les deux teintes sont celles que la pyramide et les
        # boites emploient dix centimetres plus haut, et non les deux
        # premieres d'une serie categorielle.
        colours = self.series or palette.series_map(
            self.dataset.get("groups") or [], theme.ACTIVE.series,
            other=self.dataset.get("other_label"), neutral=theme.FAINT)

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

    #: Diametre des points, en pixels. Le point choisi est le meme point,
    #: en plus gros : il garde sa couleur, qui dit a quelle population il
    #: appartient. Il portait un cerne noir et virait au rouge — deux
    #: signaux pour dire une chose, et le rouge mentait sur son groupe.
    DOT = 8
    DOT_SELECTED = 14
    #: Lissage des points. Un disque de huit pixels n'a qu'une trentaine de
    #: pixels de bord : quatre sous-echantillons y font un escalier, et le
    #: rond se lit comme un octogone. Le disque est calcule une fois par
    #: couleur et garde en cache — la finesse ne coute rien a l'affichage.
    DOT_SAMPLES = 16

    def _dot(self, colour: str, selected: bool) -> tk.PhotoImage:
        """Image d'un point, mise en cache par couleur et par etat."""
        key = (colour, selected)
        image = self._dots.get(key)
        if image is None:
            data = raster.disc(
                self.DOT_SELECTED if selected else self.DOT, _rgb(colour),
                samples=self.DOT_SAMPLES)
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
            f'{self._label_of(point)}\n'
            f'{point.get("group_label") or point["group"]}\n'
            f'{self._axis("x")["label"]} : {self._value("x", point["x"])}\n'
            f'{self._axis("y")["label"]} : {self._value("y", point["y"])}',
            self.canvas.winfo_rootx() + event.x,
            self.canvas.winfo_rooty() + event.y)

    def _label_of(self, point: Dict[str, Any]) -> str:
        """Identite si l'ecran en fournit une, reference anonyme sinon."""
        if self.identify is not None:
            name = self.identify(point.get("row"))
            if name:
                return name
        return str(point.get("reference", ""))

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
        self._view = self._clamp_view(
            (x_min - dx, x_max - dx, y_min + dy, y_max + dy))
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
        self._view = self._clamp_view(
            (cx - fx * new_x, cx + (1 - fx) * new_x,
             cy - fy * new_y, cy + (1 - fy) * new_y))
        self.redraw()


class HistogramChart(tk.Frame):
    """Distribution des remunerations. Survol pour lire une classe.

    Deux lectures sur les memes classes : la population entiere d'un bloc,
    ou les deux sexes dos a dos. La seconde repond a une question que la
    premiere ne pose pas — un ecart de mediane dit *de combien*, la forme des
    deux distributions dit *ou* : classes hautes desertees, ou entassement
    dans les basses.
    """

    #: Filet entre les deux moitiees en mode dos a dos. Sans lui, les deux
    #: premieres barres se touchent et l'axe median disparait dessous.
    MID_GAP = 3

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.canvas = tk.Canvas(self, background=theme.CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self.bins: List[Dict[str, float]] = []
        self.sexes: Dict[str, Any] = {}
        self.label = "Rémunération"
        self.split = False
        self.currency = "EUR"
        self.warning = ""
        self._items: Dict[int, Dict[str, Any]] = {}
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())

    def set_distribution(self, distribution: Dict[str, Any],
                         currency: str = "EUR") -> None:
        self.bins = list((distribution or {}).get("bins") or [])
        self.sexes = dict((distribution or {}).get("sex_split") or {})
        # Le titre de l'axe vient du mapping : « Salaire de base », ou le nom
        # que le fichier donne a la colonne analysee.
        self.label = (distribution or {}).get("label") or "Rémunération"
        self.warning = (distribution or {}).get("warning") or ""
        self.currency = currency
        self.redraw()

    def set_split(self, flag: bool) -> None:
        """Dos a dos, ou d'un bloc."""
        flag = bool(flag)
        if flag == self.split:
            return
        self.split = flag
        self.redraw()

    def may_split(self) -> bool:
        """Vrai si le moteur a juge les deux cotes publiables."""
        return bool(self.sexes.get("available"))

    def split_warning(self) -> str:
        """Pourquoi le dos a dos est refuse, tel que le moteur le dit."""
        return "" if self.may_split() else (self.sexes.get("warning") or "")

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
        if self.split and self.may_split():
            self._draw_sexes(width, height)
        else:
            self._draw_whole(width, height)

    # -- geometrie commune ------------------------------------------------

    def _frame(self, width: int, height: int, pad_t: int):
        # La marge de gauche loge les graduations d'effectif et, plus a
        # gauche encore, le titre de l'axe pose a la verticale.
        pad_l, pad_r, pad_b = 74, 20, 46
        return (pad_l, pad_t,
                max(width - pad_l - pad_r, 10),
                max(height - pad_t - pad_b, 10))

    def _footer(self, pad_l: int, pad_t: int, plot_w: float,
                plot_h: float) -> None:
        """Graduations et titres des deux axes.

        Les deux bornes exactes cedent la place a des graduations rondes :
        « 9 391 EUR » et « 137 074 EUR » ne se lisaient pas d'un coup d'oeil.

        Sous le cadre, le titre de l'axe nomme la grandeur — et rien de
        plus. Une phrase decrivant le graphique (« effectif par classe de
        remuneration, femmes au-dessus, hommes au-dessous ») occupait cette
        place : elle redisait la legende posee en haut et laissait les deux
        axes anonymes.
        """
        low = self.bins[0]["lower"]
        high = self.bins[-1]["upper"]
        span = (high - low) or 1.0
        base = pad_t + plot_h
        for value in nice_ticks(low, high, 5):
            self.canvas.create_text(
                pad_l + (value - low) / span * plot_w, base + 14,
                fill=theme.MUTED, font=axis_font(),
                text=format_money(value, self.currency))
        self.canvas.create_text(pad_l + plot_w / 2, base + 32, fill=theme.MUTED,
                                font=axis_font(), text=self.label)
        self.canvas.create_text(14, pad_t + plot_h / 2, angle=90,
                                fill=theme.MUTED, font=axis_font(),
                                text="Effectif")

    def _x_of(self, pad_l: int, plot_w: float, value: float) -> float:
        low = self.bins[0]["lower"]
        high = self.bins[-1]["upper"]
        return pad_l + (value - low) / ((high - low) or 1.0) * plot_w

    # -- population entiere ------------------------------------------------

    def _draw_whole(self, width: int, height: int) -> None:
        pad_l, pad_t, plot_w, plot_h = self._frame(width, height, 18)
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
            self._items[handle] = dict(item)
        self.canvas.create_line(pad_l, pad_t + plot_h, pad_l + plot_w,
                                pad_t + plot_h, fill=theme.LINE_STRONG)
        self._footer(pad_l, pad_t, plot_w, plot_h)

    # -- femmes et hommes dos a dos ----------------------------------------

    def _draw_sexes(self, width: int, height: int) -> None:
        # L'en-tete porte la cle de lecture : sans elle, rien ne dit quelle
        # moitie est laquelle, et la couleur seule ne suffit pas.
        pad_l, pad_t, plot_w, plot_h = self._frame(width, height, 32)
        female = list(self.sexes.get("female_counts") or [])
        male = list(self.sexes.get("male_counts") or [])
        peak = max([*female, *male, 1])
        # La hauteur se partage entre les deux moities : la calculer sur le
        # cadre entier faisait deborder les barres hautes hors du cadre.
        half = max((plot_h - self.MID_GAP) / 2, 8)
        mid = pad_t + plot_h / 2
        bar_w = plot_w / len(self.bins)

        self.canvas.create_text(pad_l, 12, anchor="w", fill=theme.FEMALE,
                                font=axis_font(), text="FEMMES ▲")
        self.canvas.create_text(pad_l + 76, 12, anchor="w", fill=theme.MALE,
                                font=axis_font(), text="HOMMES ▼")
        for value in nice_ticks(0, peak):
            offset = value / peak * half
            for y in (mid - self.MID_GAP / 2 - offset,
                      mid + self.MID_GAP / 2 + offset):
                self.canvas.create_line(pad_l, y, pad_l + plot_w, y,
                                        fill=theme.GRID)
                self.canvas.create_text(pad_l - 8, y, anchor="e",
                                        fill=theme.MUTED, font=axis_font(),
                                        text=format_number(value, 0))
        for index, item in enumerate(self.bins):
            x = pad_l + index * bar_w
            for counts, sex, colour, up in (
                (female, "femmes", theme.FEMALE, True),
                (male, "hommes", theme.MALE, False),
            ):
                count = counts[index] if index < len(counts) else 0
                if not count:
                    continue
                bar_h = half * count / peak
                near = mid - self.MID_GAP / 2 if up else mid + self.MID_GAP / 2
                far = near - bar_h if up else near + bar_h
                handle = self.canvas.create_rectangle(
                    x + 2, min(near, far), x + bar_w - 2, max(near, far),
                    fill=colour, outline="")
                self._items[handle] = dict(item, count=count, sex=sex)
        # Les deux medianes, chacune dans sa moitie : c'est le chiffre que
        # l'ecart global annonce, remis a sa place sur l'echelle.
        for key, colour, up in (("female_median", theme.FEMALE, True),
                                ("male_median", theme.MALE, False)):
            value = self.sexes.get(key)
            if value is None:
                continue
            x = self._x_of(pad_l, plot_w, float(value))
            end = mid - half if up else mid + half
            self.canvas.create_line(x, mid, x, end, fill=colour, dash=(3, 3))
            self._plate(x, end + (10 if up else -10), colour,
                        f"méd. {format_money(value, self.currency)}",
                        pad_l, plot_w)
        self.canvas.create_line(pad_l, mid, pad_l + plot_w, mid,
                                fill=theme.LINE_STRONG)
        self._footer(pad_l, pad_t, plot_w, plot_h)

    def _plate(self, x: float, y: float, colour: str, text: str,
               pad_l: int, plot_w: float) -> None:
        """Etiquette posee sur un fond plein, et maintenue dans le cadre.

        La mediane tombe la ou la population se concentre, c'est-a-dire sur
        les barres les plus hautes : sans fond, le montant se lisait sur un
        aplat de sa propre couleur. Et une mediane proche d'un bord faisait
        sortir le texte du cadre.
        """
        anchor = "center"
        if x - 55 < pad_l:
            anchor, x = "w", max(x, pad_l)
        elif x + 55 > pad_l + plot_w:
            anchor, x = "e", min(x, pad_l + plot_w)
        label = self.canvas.create_text(x, y, fill=colour, font=axis_font(),
                                        anchor=anchor, text=text)
        box = self.canvas.bbox(label)
        if box:
            plate = self.canvas.create_rectangle(
                box[0] - 3, box[1] - 1, box[2] + 3, box[3] + 1,
                fill=theme.CANVAS, outline="", tags=("plate",))
            self.canvas.tag_lower(plate, label)

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
            if item in self._items:
                data = self._items[item]
                self.tooltip.show(
                    f'{format_money(data["lower"], self.currency)} — '
                    f'{format_money(data["upper"], self.currency)}\n'
                    f'{int(data["count"])} {data.get("sex") or "salariés"}',
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
    #: Hauteur de ligne minimale en mode dedouble. Dix-sept pixels ont ete
    #: mesures pour *une* boite : deux boites et leurs effectifs n'y tiennent
    #: pas, les boites se touchent et les nombres se chevauchent. La ligne
    #: s'agrandit donc, quitte a faire defiler — ce que le graphique sait
    #: faire depuis toujours.
    ROW_SPLIT_MIN = 36
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
        self.bar = ttk.Scrollbar(self, orient="vertical",
                                 style="Flat.Vertical.TScrollbar")
        self.canvas = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0)
        # Un bandeau d'en-tete, fixe comme le pied : il nomme les colonnes.
        # « 1,20 » tout seul, a droite d'une boite, n'est pas une donnee —
        # c'est une enigme. Dans la zone qui defile, son intitule serait
        # parti des la premiere ligne cachee.
        self.header = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0,
                                height=self.HEADER_HEIGHT)
        self.header.pack(side="top", fill="x")
        self.bar.pack(side="right", fill="y")
        # Le pied vient sous le canevas et non au bas du cadre : ancre en
        # bas, il restait a sa place quand le canevas se reduisait au trace,
        # et la graduation flottait deux cents pixels sous la derniere
        # boite.
        self.canvas.pack(side="top", fill="both", expand=True)
        self.footer.pack(side="top", fill="x")
        self.bar.configure(command=self.canvas.yview)
        theme.attach_scrollbar(self.canvas, self.bar, side="right", fill="y",
                               before=self.canvas)
        self.tooltip = Tooltip(self.canvas)
        self.rows: List[Dict[str, Any]] = []
        self.currency = "EUR"
        self.warning = ""
        self.reference: Optional[float] = None
        self.order = self.ORDERS[0][0]
        self._items: Dict[int, Dict[str, Any]] = {}
        #: Dernier ajustement du canevas a son contenu : (expansion, hauteur).
        self._fitted: Optional[tuple] = None
        #: Deux boites par segment, femmes et hommes, plutot qu'une seule.
        self.split = False
        #: Seuil d'alerte de l'ecart, pose par la fenetre depuis la
        #: configuration.
        self.alert = 5.0
        #: Seuils d'ouverture de grille (Q3/Q1), poses de meme. Ils ne sont
        #: pas ecrits ici : une regle de lecture se parametre, elle ne se
        #: code pas dans un graphique.
        self.spread_alert = 1.40
        self.spread_critical = 1.80
        #: Abscisses des colonnes chiffrees, posees au trace.
        self._value_cols: tuple = ()
        #: Hauteur reelle du pied, mesuree sur son contenu a chaque trace.
        self._footer_height = self.FOOTER_HEIGHT
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
    #: « Ordre de la dimension » a ete retire : un classement alphabetique
    #: ne repond a aucune question qu'on se pose devant une dispersion, et
    #: il occupait la premiere place, donc l'ordre par defaut.
    #: L'effectif vient en premier, et c'est l'ordre par defaut : devant une
    #: dimension a quarante postes, la premiere question est « lesquels
    #: pesent », pas « lesquels paient le mieux ». Un poste de six personnes
    #: en tete de liste met en avant ce qui compte le moins.
    #: Trier, c'est repondre a une autre question avec les memes chiffres.
    #: « Ouverture » ne vaut qu'en mode simple, « ecart F/H » qu'en mode
    #: dedouble : proposer l'un dans l'autre mode offrirait un tri sans
    #: colonne pour le verifier.
    ORDERS = (("headcount", "Effectif décroissant"),
              ("median", "Médiane décroissante"),
              ("spread", "Ouverture décroissante"))
    SPLIT_ORDERS = (("headcount", "Effectif décroissant"),
                    ("median", "Médiane décroissante"),
                    ("gap", "Écart F/H décroissant"))

    #: Hauteur du bandeau d'en-tete : une ligne d'intitules.
    HEADER_HEIGHT = 26
    #: Blanc entre les deux colonnes chiffrees de droite.
    VALUE_GAP = 20

    def orders(self):
        """Tris applicables au mode courant."""
        return self.SPLIT_ORDERS if self.split else self.ORDERS

    def set_split(self, split: bool) -> None:
        """Une boite par segment, ou deux : femmes et hommes."""
        self.split = bool(split)
        self.redraw()

    def set_order(self, key: str) -> None:
        """Change l'ordre des boites sans recalculer quoi que ce soit."""
        self.order = key if key in dict(self.ORDERS) else self.ORDERS[0][0]
        self.redraw()

    def _sorted(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ordre demande, mediane decroissante par defaut : c'est la
        question qu'on se pose devant une dispersion — qui gagne le plus, et
        de combien l'ecart se creuse."""
        if self.order == "median":
            return sorted(rows, key=lambda row: -(row["salary"]["median"] or 0))
        if self.order == "headcount":
            return sorted(rows, key=lambda row: -(row.get("headcount") or 0))
        if self.order == "spread":
            # Les segments sans ouverture calculable ferment la marche :
            # les mettre en tete reviendrait a classer en premier ce qu'on
            # ne sait pas mesurer.
            return sorted(rows, key=lambda row: -(self._spread(row) or -1))
        if self.order == "gap":
            return sorted(rows, key=lambda row: -(row.get("median_gap")
                                                  if row.get("median_gap")
                                                  is not None else -1e9))
        return rows

    @staticmethod
    def _spread(row) -> Optional[float]:
        """Ouverture de la grille sur le segment : Q3/Q1, telle que le
        moteur la publie. Le graphique ne refait pas la division."""
        dispersion = ((row.get("salary") or {}).get("dispersion") or {})
        value = dispersion.get("q3_over_q1")
        return float(value) if value is not None else None

    def set_rows(self, rows: Sequence[Dict[str, Any]], currency: str = "EUR",
                 warning: str = "", reference: Optional[float] = None,
                 alert: float = 5.0, spread_alert: float = 1.40,
                 spread_critical: float = 1.80) -> None:
        """Lignes de segment, dans l'ordre etabli par le moteur.

        `reference` est la mediane de l'ensemble analyse : tracee en repere,
        elle rend lisible d'un regard ce qui est au-dessus et au-dessous,
        sans avoir a comparer des montants de tete.
        """
        self.rows = [dict(row) for row in rows or []]
        self.currency = currency
        self.warning = warning
        # Seuil d'alerte de l'ecart, tel que la configuration le fixe. Il
        # etait ecrit en dur ici alors qu'il existe deja en parametre : deux
        # endroits pour une meme regle, c'est un des deux qui finit faux.
        self.alert = alert
        self.spread_alert = spread_alert
        self.spread_critical = spread_critical
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
            # Dedouble, un segment n'a sa place que si l'un des deux sexes
            # au moins atteint le seuil graphique : une ligne sans boite
            # occuperait la place d'un resultat qu'elle n'a pas.
            if self.split and row.get("sex_chartable") is not True:
                continue
            ready.append(row)
        return self._sorted(ready)

    def _refusal(self) -> str:
        """Ce que l'on dit quand rien n'est tracable."""
        if any(not row.get("masked") for row in self.rows):
            return ("Effectif par segment insuffisant pour tracer une "
                    "dispersion. Les valeurs restent lisibles dans le "
                    "rapport et dans le classeur.")
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
        # il y a un repere a poser. A droite, une gouttiere pour l'ecart
        # femmes / hommes : c'est ce qu'on vient chercher en dedoublant, et
        # il n'etait chiffre nulle part — il fallait comparer deux traits a
        # l'oeil.
        value_width = self._value_width(drawable)
        pad_r = self.GAP_COLUMN if self.split else value_width
        # Le repere d'ensemble s'intitule desormais dans le bandeau fixe :
        # la grille n'a plus a lui reserver une bande en haut du trace.
        pad_t = 12
        plot_w = max(width - pad_l - pad_r, 20)
        plot_h = max(height - pad_t - 10, 20)

        # Plus de troncature : la ligne s'etire jusqu'a son confort maximal
        # quand les segments tiennent, et se pose sur son plancher quand ils
        # ne tiennent pas — la page defile alors. Ecarter des segments faute
        # de place revenait a cacher une partie de la reponse.
        plancher = self.ROW_SPLIT_MIN if self.split else self.ROW_MIN
        row_height = min(self.ROW_MAX, max(plot_h / len(drawable), plancher))
        low, high = self._span(drawable)
        span = (high - low) or 1.0
        base = pad_t + len(drawable) * row_height

        def to_x(value: float) -> float:
            return pad_l + (value - low) / span * plot_w

        # La zone defilante couvre toutes les lignes, jamais moins que la
        # fenetre : sinon un graphique court se recadrerait tout seul.

        for value in self._ticks(low, high, plot_w):
            x = to_x(value)
            self.canvas.create_line(x, pad_t, x, base, fill=theme.GRID)

        # Le repere d'ensemble, trace avant les boites pour passer dessous.
        if self.reference is not None and low <= self.reference <= high:
            self.canvas.create_line(to_x(self.reference), pad_t - 4,
                                    to_x(self.reference), base,
                                    fill=theme.ACCENT, dash=(4, 3))

        # Un fond une ligne sur deux, dans les deux modes. Il n'existait
        # qu'en mode dedouble, au motif que le mode simple a moins de
        # lignes : avec deux colonnes chiffrees a l'autre bout de l'ecran,
        # c'est pourtant la qu'un oeil perd sa ligne entre le libelle et le
        # nombre.
        for index in range(0, len(drawable), 2):
            haut = pad_t + index * row_height
            self.canvas.create_rectangle(0, haut, width, haut + row_height,
                                         fill=theme.STRIPE, outline="")

        # Abscisses des deux colonnes chiffrees, calees a droite. Elles
        # servent au trace comme au bandeau : un intitule qui ne tombe pas
        # au-dessus de sa colonne ne l'intitule pas.
        self._value_cols = ((width - value_width + self._spread_width(drawable),
                             width - 10) if not self.split else ())
        for index, row in enumerate(drawable):
            self._draw_box(row, index, row_height, pad_l, label_width, to_x,
                           width, pad_t)

        self._draw_header(label_width, pad_l, width, to_x, low, high)
        self._draw_footer(label_width, pad_l, plot_w, to_x, low, high)
        self._fit_to_content(width, base + 10)

    def _fit_to_content(self, width: float, needed: float) -> None:
        """Le pied suit le trace au lieu de rester colle au bas du cadre.

        Six segments dessines occupent deux cent soixante-huit pixels dans
        un canevas qui en fait quatre cent quatre-vingt-neuf : la graduation
        se retrouvait deux cent vingt pixels sous la derniere boite, trop
        loin pour qu'on la rapporte a ce qu'on lit. Le canevas se reduit
        donc au trace tant que celui-ci tient, et ne reprend toute la place
        que lorsqu'il faut faire defiler.
        """
        available = (self.winfo_height() - self._footer_height
                     - self.HEADER_HEIGHT)
        if available <= 0:
            return
        expand = needed >= available
        height = available if expand else int(needed)
        # La zone de defilement suit la hauteur retenue : la laisser a la
        # taille d'avant faisait apparaitre un ascenseur pour un trace qui
        # tenait desormais en entier.
        self.canvas.configure(scrollregion=(0, 0, width, max(needed, height)))
        if self._fitted == (expand, height):
            return
        self._fitted = (expand, height)
        # « expand » commande seul la hauteur reelle : une hauteur demandee
        # est ignoree tant qu'il vaut vrai.
        self.canvas.pack_configure(expand=expand)
        self.canvas.configure(height=height)

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
        # Le pied suit son contenu au lieu d'une hauteur constante. La
        # phrase de lecture se renvoie a la ligne quand la fenetre se
        # resserre, et quand on dedouble — la legende des deux teintes lui
        # prend de la largeur : mesure faite, jusqu'a vingt-trois pixels de
        # texte etaient coupes par le bas, c'est-a-dire la phrase qui
        # explique le graphique.
        contenu = self.footer.bbox("all")
        self._footer_height = max(self.FOOTER_HEIGHT,
                                  int(contenu[3]) + 6 if contenu else 0)
        if self.footer.winfo_height() != self._footer_height:
            self.footer.configure(height=self._footer_height)

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

        offset = 30
        # La cle passe a la ligne quand elle ne tient pas a cote du schema :
        # collee a droite, elle sortait du cadre et « Hommes » se coupait au
        # milieu.
        etroit = available - wide - 30 < 150
        if etroit and self.split:
            mid += 0
        if self.split:
            # Deux teintes qui ne se legendent pas ne sont qu'un decor : la
            # cle dit laquelle est laquelle, la ou on la lit.
            ligne = mid + 26 if etroit else mid
            depart = left if etroit else left + wide + offset
            for teinte, aplat, texte in (
                    (theme.FEMALE, theme.FEMALE_SOFT, "Femmes"),
                    (theme.MALE, theme.MALE_SOFT, "Hommes")):
                canvas.create_rectangle(depart, ligne - 5, depart + 18,
                                        ligne + 5, fill=aplat, outline=teinte)
                canvas.create_text(depart + 24, ligne, anchor="w",
                                   fill=theme.MUTED, font=axis_font(),
                                   text=texte)
                largeur = 24 + 18 + _text_width(self, texte)
                depart += largeur
                if not etroit:
                    offset += largeur

        # La phrase demande de la place : dans un bloc etroit, le schema
        # legende suffit, et une phrase coupee en trois mots par ligne
        # n'explique plus rien.
        room = available - wide - offset - 10
        if room < 190:
            return
        phrase = ("La boîte contient la moitié des salariés du segment ; "
                  "le trait, la médiane. Les moustaches vont du 10e au 90e "
                  "centile.")
        withheld = self._withheld()
        if withheld:
            # L'onglet Segments a disparu : la phrase renvoyait a un
            # endroit qui n'existe plus. Le rapport et le classeur, eux,
            # listent ces segments avec leur effectif.
            phrase += (f" {withheld} segment(s) trop peu nombreux pour être "
                       "tracés — le rapport et le classeur les listent.")
        canvas.create_text(left + wide + offset, mid - 5, anchor="nw",
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

    def _spread_width(self, rows: Sequence[Dict[str, Any]]) -> float:
        """Colonne de l'ouverture, a la chasse de la plus large valeur."""
        import tkinter.font as tkfont

        font = tkfont.Font(root=self, font=axis_font())
        return max((font.measure(self._spread_text(row)) for row in rows),
                   default=font.measure("× 1,00"))

    def _value_width(self, rows: Sequence[Dict[str, Any]]) -> float:
        """Place prise a droite par les deux colonnes chiffrees."""
        import tkinter.font as tkfont

        font = tkfont.Font(root=self, font=axis_font())
        medianes = max(
            (font.measure(format_money((row.get("salary") or {}).get("median"),
                                       self.currency)) for row in rows),
            default=60)
        return self._spread_width(rows) + self.VALUE_GAP + medianes + 20

    def _spread_text(self, row) -> str:
        """« × 1,20 » plutot que « 1,20 ».

        Le rapport Q3/Q1 nu se lit comme un montant, un rang ou un indice.
        Le signe de multiplication dit ce qu'il est : le quart superieur
        commence a 1,2 fois la ou le quart inferieur s'arrete.
        """
        value = self._spread(row)
        return "—" if value is None else f"× {format_number(value, 2)}"

    def _draw_header(self, label_width: float, pad_l: float, width: float,
                     to_x, low: float, high: float) -> None:
        """Intitules des colonnes, hors de la zone qui defile."""
        self.header.delete("all")
        y = self.HEADER_HEIGHT - 9
        # Un seul intitule a gauche. Le nom de la dimension y figurait
        # aussi, et il s'ecrivait par-dessus celui-ci des que les libelles
        # de segment etaient courts — « Lyon », « Lille » donnent une
        # colonne etroite. Il n'y manque pas : le selecteur DIMENSION,
        # quarante pixels plus haut, porte deja ce mot.
        self.header.create_text(pad_l - 14, y, anchor="e", fill=theme.FAINT,
                                font=axis_font(),
                                text="FEMMES / HOMMES" if self.split else "EFF.")
        if self.reference is not None and low <= self.reference <= high:
            # Dans une colonne etroite, l'intitule du repere venait buter
            # sur celui de la colonne de droite. Il cede la place : le trait
            # pointille reste, et c'est lui qui porte l'information.
            import tkinter.font as tkfont

            police = tkfont.Font(root=self, font=axis_font())
            texte = ("Médiane d'ensemble · "
                     f"{format_money(self.reference, self.currency)}")
            depart = to_x(self.reference) + 5
            bord = width - (self.GAP_COLUMN if self.split
                            else (self._value_cols[1] - self._value_cols[0]
                                  + 90 if self._value_cols else 30))
            if depart + police.measure(texte) <= bord:
                self.header.create_text(depart, y, anchor="w",
                                        fill=theme.ACCENT, font=axis_font(),
                                        text=texte)
        if self.split:
            self.header.create_text(width - 8, y, anchor="e", fill=theme.FAINT,
                                    font=axis_font(), text="ÉCART F/H")
            return
        if not self._value_cols:
            return
        spread_x, median_x = self._value_cols
        self.header.create_text(spread_x, y, anchor="e", fill=theme.FAINT,
                                font=axis_font(), text="OUVERTURE Q3/Q1")
        self.header.create_text(median_x, y, anchor="e", fill=theme.FAINT,
                                font=axis_font(), text="MÉDIANE")

    def _draw_values(self, row, centre: float) -> None:
        """Les deux chiffres de droite : ouverture de grille, et mediane.

        La place existait deja — elle etait vide. Or la largeur d'une boite
        ne dit pas l'ouverture de la grille : une boite haute dans l'echelle
        parait large sans l'etre, et personne ne divise Q3 par Q1 de tete.
        """
        if not self._value_cols:
            return
        spread_x, median_x = self._value_cols
        value = self._spread(row)
        self.canvas.create_text(
            spread_x, centre, anchor="e", font=axis_font(),
            fill=theme.CRIT if value is not None and value >= self.spread_critical
            else (theme.WARN if value is not None and value >= self.spread_alert
                  else theme.MUTED),
            text=self._spread_text(row))
        self.canvas.create_text(
            median_x, centre, anchor="e", fill=theme.INK_SOFT, font=axis_font(),
            text=format_money((row.get("salary") or {}).get("median"),
                              self.currency))

    def _count_width(self, rows: Sequence[Dict[str, Any]]) -> float:
        """Colonne des effectifs, a la chasse du plus grand nombre."""
        import tkinter.font as tkfont

        font = tkfont.Font(root=self, font=axis_font())
        if self.split:
            # « 178 / 111 » demande plus de place qu'un effectif seul.
            return max((font.measure(f"{row.get('female_count', 0)} / "
                                     f"{row.get('male_count', 0)}")
                        for row in rows), default=48)
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

    #: Gouttiere de droite reservee a l'ecart, en mode dedouble. Assez pour
    #: « -12,3 % » a la chasse des axes, et un peu d'air avant le bord.
    GAP_COLUMN = 64

    def _draw_box(self, row, index: int, row_height: float, pad_l: float,
                  label_width: float, to_x, width: float,
                  top: float) -> None:
        # L'origine verticale est celle de la grille. Elle valait 14 en dur,
        # quand la grille part de « pad_t » — 26 des qu'un repere d'ensemble
        # est pose : les boites etaient tracees douze pixels au-dessus des
        # traits qu'elles sont censees couper. Invisible tant que le fond
        # etait uni, evident des qu'une bande vient marquer la ligne.
        centre = top + index * row_height + row_height / 2
        self.canvas.create_text(label_width, centre, anchor="e",
                                fill=theme.INK_SOFT, font=axis_font(),
                                text=_shorten(self, str(row.get("segment", "")),
                                              self.LABEL_MAX))
        if not self.split:
            # L'effectif : une boite tracee sur douze salaries a la meme
            # allure qu'une boite tracee sur quatre cents.
            self.canvas.create_text(pad_l - 14, centre, anchor="e",
                                    fill=theme.FAINT, font=axis_font(),
                                    text=str(row.get("headcount", 0)))
            self._draw_one(row, row["salary"], centre, row_height * 0.42,
                           theme.ACCENT_SOFT, theme.ACCENT, to_x)
            self._draw_values(row, centre)
            return

        # Deux demi-boites, femmes au-dessus : deux medianes proches peuvent
        # recouvrir deux distributions tres differentes, et un ecart de
        # mediane nul n'exclut pas que les femmes soient absentes du haut de
        # la fourchette.
        #
        # L'ecartement de la paire vaut moins que le blanc qui la separe du
        # segment suivant, et c'est ce qui la fait lire comme une paire : a
        # 0,22 de la hauteur de ligne, les deux boites d'un segment etaient
        # aussi eloignees l'une de l'autre que de celles du voisin, et
        # l'oeil ne groupait plus rien.
        # A 0,17, les deux boites se touchaient presque. A 0,22, le blanc
        # qui les separe reste nettement plus petit que celui qui separe la
        # paire du segment suivant — c'est ce rapport, et lui seul, qui fait
        # lire une paire plutot que deux lignes voisines.
        ecart = row_height * 0.22
        self._draw_counts(row, pad_l - 14, centre)
        for sex, decalage, teinte, aplat in (
                ("female", -ecart, theme.FEMALE, theme.FEMALE_SOFT),
                ("male", ecart, theme.MALE, theme.MALE_SOFT)):
            if not row.get(f"{sex}_chartable"):
                continue
            salary = row.get(sex) or {}
            if salary.get("masked") or salary.get("median") is None:
                continue
            # La ligne entiere est passee, et non la seule moitie : la
            # bulle montre les trois colonnes, et il lui faut l'ensemble
            # comme les deux sexes. `moitie` dit laquelle est survolee.
            self._draw_one(row, salary, centre + decalage,
                           row_height * 0.24, aplat, teinte, to_x,
                           moitie=sex)

        self._draw_gap(row, centre, width)

    def _draw_counts(self, row, droite: float, centre: float) -> None:
        """« 178 / 111 » : l'effectif de chaque sexe, dans sa teinte.

        Cinq femmes en face de cent vingt hommes ne se lisent pas comme deux
        boites de meme poids, et l'effectif du segment entier ne le disait
        pas. Les deux nombres tiennent sur une seule ligne, a la hauteur de
        la paire : empiles a la hauteur de chaque boite, ils se chevauchaient
        des que la ligne se resserrait.
        """
        import tkinter.font as tkfont

        police = tkfont.Font(root=self, font=axis_font())
        hommes = str(row.get("male_count", 0))
        femmes = str(row.get("female_count", 0))
        x = droite
        self.canvas.create_text(x, centre, anchor="e", fill=theme.MALE,
                                font=axis_font(), text=hommes)
        x -= police.measure(hommes)
        self.canvas.create_text(x, centre, anchor="e", fill=theme.FAINT,
                                font=axis_font(), text=" / ")
        x -= police.measure(" / ")
        self.canvas.create_text(x, centre, anchor="e", fill=theme.FEMALE,
                                font=axis_font(), text=femmes)

    def _draw_gap(self, row, centre: float, width: float) -> None:
        """L'ecart de mediane, a droite de la paire.

        C'est ce qu'on vient chercher en cochant la case. Il n'etait chiffre
        nulle part : il fallait comparer deux traits verticaux a l'oeil, ce
        que personne ne fait a un pour cent pres. Le calcul vient du moteur
        et non d'ici — un graphique qui ferait sa propre soustraction
        finirait par annoncer un chiffre que le document contredit.
        """
        ecart = row.get("median_gap")
        if ecart is None:
            # Un cote retenu par le seuil : « rien » et non « zero ». Un
            # zero se lirait « pas de difference », quand la verite est
            # « on n'a pas le droit de le dire ».
            self.canvas.create_text(width - 8, centre, anchor="e",
                                    fill=theme.FAINT, font=axis_font(),
                                    text="—")
            return
        # Un ecart negatif — les femmes payees davantage — reste en teinte
        # neutre : c'est une situation a regarder, ce n'est pas celle que la
        # directive fait surveiller. La couleur ne decide de rien et ne
        # modifie aucun chiffre ; elle ne fait que signaler ce que le moteur
        # a deja publie.
        self.canvas.create_text(
            width - 8, centre, anchor="e", font=axis_font(),
            fill=theme.CRIT if ecart >= self.alert * 2 else (
                theme.WARN if ecart >= self.alert else theme.MUTED),
            text=f"{ecart:+.1f} %".replace(".", ","))

    def _draw_one(self, row, salary, centre: float, span: float,
                  fill: str, outline: str, to_x, moitie=None) -> None:
        """Une boite : moustaches, quartiles, mediane.

        `moitie` dit de quelle demi-population elle est — « female »,
        « male », ou rien pour le groupe entier. La bulle en a besoin :
        sans elle, survoler un cote donnait les chiffres de l'ensemble.
        """
        thickness = min(max(span, 5.0), 15.0)
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
            fill=fill, outline=outline)
        # La mediane est le chiffre que l'on cite : elle est le seul trait
        # dense de la boite.
        self.canvas.create_line(to_x(median), centre - thickness / 2 - 2,
                                to_x(median), centre + thickness / 2 + 2,
                                fill=theme.INK, width=2)
        self._items[handle] = (row, moitie)

    #: Les colonnes de la bulle, et la clef ou chacune se lit dans la ligne.
    #: `None` designe le groupe entier.
    COLONNES = (("Ensemble", None), ("Femmes", "female"), ("Hommes", "male"))

    #: Les bornes montrees, du haut de la distribution vers le bas : c'est
    #: le sens de lecture d'une boite couchee regardee de droite a gauche.
    BORNES = (("P90", "p90"), ("Q3", "p75"), ("Médiane", "median"),
              ("Q1", "p25"), ("P10", "p10"))

    def _bulle(self, row, moitie) -> str:
        """Le contenu de la bulle : les trois colonnes, cote a cote.

        Survoler la boite des femmes donnait les chiffres de l'ensemble :
        la boite ne retenait pas de quelle moitie elle etait. On lisait
        donc, sous le curseur pose sur une moitie, les bornes de l'autre
        plus les siennes melangees — et il fallait deviner.

        Les trois colonnes repondent a la question qu'on se pose vraiment
        en survolant : non pas « combien vaut ce quartile », mais « de
        combien les deux cotes different ici ». La colonne survolee porte
        une marque : sans elle, trois colonnes identiques ne diraient plus
        laquelle on montre.
        """
        def publiable(bloc) -> bool:
            """Un cote retenu par le seuil n'a pas de colonne : une colonne
            de tirets laisserait croire qu'on a mesure et qu'on ne dit
            rien, alors qu'on n'a pas le droit de mesurer."""
            return bool(bloc) and not bloc.get("masked") \
                and bloc.get("median") is not None

        presentes = [(titre, cle) for titre, cle in self.COLONNES
                     if publiable(row.get("salary") if cle is None
                                  else row.get(cle))]
        if not presentes:
            return ""
        largeur = 11
        entete = "".join(
            (("▸ " if cle == moitie else "  ") + titre).rjust(largeur)
            for titre, cle in presentes)
        lignes = [f'{row.get("segment", "")} · '
                  f'{row.get("headcount", 0)} salariés',
                  "".ljust(9) + entete]
        for intitule, clef in self.BORNES:
            cellules = []
            for _titre, cle in presentes:
                bloc = row.get("salary") if cle is None else row.get(cle)
                valeur = (bloc or {}).get(clef)
                cellules.append(
                    ("—" if valeur is None
                     else format_money(valeur, self.currency)).rjust(largeur))
            lignes.append(intitule.ljust(9) + "".join(cellules))
        effectifs = []
        for _titre, cle in presentes:
            nombre = (row.get("headcount", 0) if cle is None
                      else row.get(f"{cle}_count"))
            effectifs.append(("—" if nombre is None
                              else str(nombre)).rjust(largeur))
        lignes.append("Effectif".ljust(9) + "".join(effectifs))
        return "\n".join(lignes)

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y,
                                                 event.x, event.y):
            if item in self._items:
                row, moitie = self._items[item]
                texte = self._bulle(row, moitie)
                if not texte:
                    break
                self.tooltip.show(texte,
                                  self.canvas.winfo_rootx() + event.x,
                                  self.canvas.winfo_rooty() + event.y,
                                  tableau=True)
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

    #: Hauteur d'une tranche. A vingt-six, dix tranches d'anciennete
    #: prenaient trois cents pixels a elles seules et la page ne tenait plus
    #: sur un ecran ; a vingt et un, la barre garde sa hauteur et son
    #: nombre reste lisible.
    ROW = 21
    #: Colonne des tranches, a gauche. Elles occupaient la gouttiere
    #: centrale, ou elles separaient les deux ailes au lieu de les laisser
    #: se repondre ; une pyramide se lit mieux quand ses deux moities se
    #: touchent, et quand ses tranches s'enumerent au meme bord qu'un
    #: tableau.
    LABELS = 92
    #: Blanc reserve en bout d'aile pour l'effectif, desormais pose au bout
    #: de chaque barre plutot qu'a une colonne fixe : lu loin d'une barre
    #: courte, le nombre ne s'y rapportait plus.
    COUNTS = 34
    #: Blanc entre deux barres. Quatre pixels separent sans eloigner : la
    #: barre occupe alors la plus grande part de sa tranche, et deux
    #: tranches voisines se comparent en masse plutot qu'en longueur.
    GOUTTIERE = 4

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
        # L'ordre vient du moteur, qui publie les tranches de la plus agee
        # a la plus jeune. Le renversement se faisait ici, et seule cette
        # pyramide-ci en profitait : les tableaux de l'ecran, le PDF, le
        # HTML et le classeur lisaient l'ordre inverse.
        self.rows = [dict(row) for row in rows]
        self._fit()
        self.pack_propagate(False)
        self.redraw()

    def set_row_height(self, value: int) -> None:
        """Hauteur d'une tranche, posee par la page.

        La page connait la hauteur dont elle dispose, le graphique non :
        c'est elle qui decide si les tranches peuvent respirer. Une valeur
        fixe laissait un grand vide sous une page courte.
        """
        value = int(value)
        if value == self.ROW:
            return
        self.ROW = value
        self._fit()
        self.redraw()

    def _fit(self) -> None:
        # Le cadre porte les tranches, plus la bande de legende du bas.
        self.configure(height=max(len(self.rows), 1) * self.ROW + 22)

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
        # Les tranches tiennent une colonne a gauche ; le reste se partage
        # entre les deux ailes, qui se rejoignent au centre.
        wing = max((width - self.LABELS - 2 * self.COUNTS) / 2, 20)
        centre = self.LABELS + self.COUNTS + wing

        # La barre remplit sa tranche au lieu de flotter au milieu : a sept
        # pixels de demi-hauteur pour une tranche de vingt et un, un tiers
        # de la pyramide etait du blanc entre les barres, et l'oeil
        # comparait des traits au lieu de masses.
        barre = max((self.ROW - self.GOUTTIERE) / 2, 4)
        for index, row in enumerate(self.rows):
            y = index * self.ROW + self.ROW / 2
            female = row.get("female") or 0
            male = row.get("male") or 0
            self.canvas.create_text(4, y, anchor="w", fill=theme.INK,
                                    font=axis_font(),
                                    text=_shorten(self, row.get("label", ""),
                                                  self.LABELS - 10))
            if female:
                bout = centre - wing * female / peak
                item = self.canvas.create_rectangle(bout, y - barre, centre,
                                                    y + barre,
                                                    fill=theme.FEMALE,
                                                    outline="")
                self._items[item] = f'{row["label"]} · {female} femmes'
                # L'effectif au bout de sa barre : a une colonne fixe, il
                # flottait loin d'une barre courte, et rien ne disait a
                # laquelle il se rapportait.
                self.canvas.create_text(bout - 5, y, anchor="e",
                                        fill=theme.MUTED, font=axis_font(),
                                        text=str(female))
            if male:
                bout = centre + wing * male / peak
                item = self.canvas.create_rectangle(centre, y - barre, bout,
                                                    y + barre,
                                                    fill=theme.MALE,
                                                    outline="")
                self._items[item] = f'{row["label"]} · {male} hommes'
                self.canvas.create_text(bout + 5, y, anchor="w",
                                        fill=theme.MUTED, font=axis_font(),
                                        text=str(male))
        # La legende ferme le dessin au lieu de l'ouvrir. En tete, elle
        # separait le titre de la premiere tranche ; en pied, elle se lit
        # au moment ou l'on a vu les deux ailes et ou l'on demande
        # laquelle est laquelle.
        bas = len(self.rows) * self.ROW + 12
        self.canvas.create_text(centre - 8, bas, anchor="e",
                                fill=theme.FEMALE, font=axis_font(),
                                text="FEMMES")
        self.canvas.create_text(centre + 8, bas, anchor="w", fill=theme.MALE,
                                font=axis_font(), text="HOMMES")

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










class OrgChart(tk.Frame):
    """L'organigramme d'une equipe, en cases reliees.

    Seuls les responsables ont une case. Ceux qui n'encadrent personne sont
    comptes sous celle de leur responsable, dans une case plus discrete :
    « 7 collaborateurs ». Un organigramme ou chaque salarie aurait sa case
    deviendrait illisible passe trente personnes, et la structure — ce qu'on
    vient precisement y lire — y disparaitrait. La liste nominative est a
    cote, c'est elle qui nomme.

    Chaque case porte l'effectif qu'elle encadre et, quand le seuil de
    publication est atteint, la mediane de son equipe. Une equipe de trois
    affiche sa taille et jamais sa remuneration : l'organigramme serait
    sinon le chemin le plus court vers le salaire du voisin.

    L'identite n'est pas dans les donnees : la case porte un matricule, et
    la fenetre y rapproche un nom si le parametrage l'y autorise.
    """

    # Compact, et c'est une contrainte de lecture, pas d'economie : un
    # organigramme qui s'etend sur trois ecrans ne se lit plus, on le
    # parcourt. Trois lignes dans la case — le nom, le poste, le salaire de
    # base — et rien de plus ; la mediane de l'equipe et les effectifs
    # tiennent dans l'info-bulle.
    BOX_W, BOX_H = 148, 46
    #: La case des collaborateurs sans equipe : plus basse, elle se
    #: distingue d'un rattachement nomme au premier coup d'oeil.
    CHIP_H = 24
    GAP_X, GAP_Y = 14, 28
    MARGIN = 16
    #: Place reservee a l'ascenseur du bas quand le cadre prend la hauteur
    #: du dessin : sans elle, il recouvre la derniere rangee de cases.
    SCROLLBAR_ROOM = 16

    def __init__(self, master: tk.Widget, on_select: Optional[Callable] = None,
                 grows: bool = False):
        """`grows` : le dessin prend la hauteur qu'il lui faut.

        Pose dans une page qui defile, un organigramme ne doit pas avoir son
        propre ascenseur vertical — deux zones defilantes imbriquees rendent
        la molette imprevisible, et l'on se retrouve a faire defiler l'une
        en croyant bouger l'autre. Il s'etend donc, et c'est la page qui
        defile. En largeur, en revanche, il garde le sien : c'est la
        dimension par laquelle un organigramme deborde.
        """
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.grows = grows
        self.bar_x = ttk.Scrollbar(self, orient="horizontal",
                                   style="Flat.Horizontal.TScrollbar")
        self.bar_y = ttk.Scrollbar(self, orient="vertical",
                                   style="Flat.Vertical.TScrollbar")
        self.canvas = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0)
        if not grows:
            self.bar_y.pack(side="right", fill="y")
        self.bar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.bar_x.configure(command=self.canvas.xview)
        self.bar_y.configure(command=self.canvas.yview)
        if not grows:
            theme.attach_scrollbar(self.canvas, self.bar_y, axis="y",
                                   side="right", fill="y", before=self.canvas)
        theme.attach_scrollbar(self.canvas, self.bar_x, axis="x",
                               side="bottom", fill="x", before=self.canvas)
        self.tooltip = Tooltip(self.canvas)
        self.root: Optional[Dict[str, Any]] = None
        self.currency = "EUR"
        self.warning = ""
        #: Rappel qui rend un nom lisible depuis un matricule. Vide quand le
        #: parametrage cache les identites : la case porte alors le
        #: matricule, qui suffit a retrouver la personne dans son fichier.
        self.identify: Optional[Callable[[str], str]] = None
        #: Matricule mis en evidence, pose par la fenetre quand une ligne de
        #: la liste est choisie. Le lien entre les deux lectures passe par
        #: la : sans lui, trouver dans le dessin la personne qu'on vient de
        #: selectionner dans la liste demande de parcourir quarante cases.
        self.selected: Optional[str] = None
        self._on_select = on_select
        self._items: Dict[int, Dict[str, Any]] = {}
        #: Derniere hauteur imposee au cadre. Sans ce garde, demander une
        #: hauteur depuis le trace declenche un <Configure>, donc un
        #: nouveau trace, donc une nouvelle demande : la fenetre tourne.
        self._fitted: Optional[int] = None
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())
        self.canvas.bind("<Button-1>", self._on_click)

    # ------------------------------------------------------------ donnees

    def set_tree(self, root: Optional[Dict[str, Any]], currency: str = "EUR",
                 warning: str = "") -> None:
        self.root = root
        self.currency = currency
        self.warning = warning
        self.redraw()

    def select(self, manager: Optional[str]) -> None:
        """Met une case en evidence, sans rien changer d'autre."""
        if manager == self.selected:
            return
        self.selected = manager
        self.redraw()

    # ------------------------------------------------------------ souris

    def _at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        # Les coordonnees de l'evenement sont celles de la fenetre ; le
        # canevas defile, donc elles ne sont pas celles du dessin.
        x, y = int(self.canvas.canvasx(x)), int(self.canvas.canvasy(y))
        for item in self.canvas.find_overlapping(x, y, x, y):
            if item in self._items:
                return self._items[item]
        return None

    def _on_motion(self, event) -> None:
        node = self._at(event.x, event.y)
        if node is None or node.get("chip"):
            self.tooltip.hide()
            self.canvas.configure(cursor="")
            return
        self.canvas.configure(cursor="hand2")
        self.tooltip.show(self._label(node),
                          self.canvas.winfo_rootx() + event.x,
                          self.canvas.winfo_rooty() + event.y)

    def _on_click(self, event) -> None:
        node = self._at(event.x, event.y)
        if node is not None and not node.get("chip") and self._on_select:
            self._on_select(node)

    def _display(self, manager: str) -> str:
        """Nom lisible d'un matricule. Le methode ne s'appelle pas `_name` :
        tkinter range deja le nom Tcl du widget sous cet attribut, et le
        redefinir remplace une chaine par une methode au milieu de la
        machinerie de Tk."""
        if self.identify is not None:
            return self.identify(manager) or manager
        return manager

    def _label(self, node: Dict[str, Any]) -> str:
        """Ce que dit une case au survol : qui, combien, et a quel niveau."""
        morceaux = [self._display(node.get("manager", ""))]
        if node.get("job"):
            morceaux.append(str(node["job"]))
        if node.get("own_amount") is not None:
            morceaux.append(format_money(node["own_amount"], self.currency))
        morceaux.append(f"{node.get('direct', 0)} en direct · "
                        f"{node.get('total', 0)} au total")
        if node.get("amount") is not None:
            morceaux.append("médiane de l'équipe : "
                            + format_money(node["amount"], self.currency))
        else:
            morceaux.append("médiane masquée : effectif sous le seuil")
        return "  ·  ".join(morceaux)

    # ------------------------------------------------------------ disposition

    def _layout(self, node: Dict[str, Any], x: int, level: int,
                out: List[Dict[str, Any]]) -> int:
        """Pose une case et sa descendance, et rend la largeur occupee.

        Disposition classique : chaque case est centree sur ses enfants, et
        la largeur d'une branche est la somme de celles de ses enfants. Elle
        se calcule en un seul parcours, l'enfant etant pose avant que son
        parent ne sache ou se centrer.
        """
        enfants = list(node.get("children") or [])
        curseur = x
        for enfant in enfants:
            curseur += self._layout(enfant, curseur, level + 1,
                                    out) + self.GAP_X
        # Les collaborateurs sans equipe font une case comptee, posee apres
        # les rattachements nommes — mais seulement quand il y a des cases
        # a cote : seul sous son responsable, le compte est deja dans la
        # case du dessus.
        chip = None
        if enfants and node.get("individuals"):
            chip = {"chip": True, "individuals": node["individuals"],
                    "x": curseur, "y": self._y(level + 1),
                    "width": self.BOX_W}
            curseur += self.BOX_W + self.GAP_X
            out.append(chip)
        largeur = max(curseur - self.GAP_X - x, self.BOX_W)
        centre = x + largeur / 2 - self.BOX_W / 2
        node["x"], node["y"] = centre, self._y(level)
        node["width"] = self.BOX_W
        out.append(node)
        node["_chip"] = chip
        return largeur

    def _y(self, level: int) -> float:
        return self.MARGIN + level * (self.BOX_H + self.GAP_Y)

    # ------------------------------------------------------------ trace

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        width = self.canvas.winfo_width()
        if width < 200:
            return
        if not self.root:
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            self.canvas.create_text(
                self.MARGIN, 40, anchor="w",
                text=self.warning or "Choisissez une équipe à l'étape 3 pour "
                                     "voir son organigramme.",
                font=note_font(), fill=theme.MUTED)
            return

        posees: List[Dict[str, Any]] = []
        largeur = self._layout(self.root, self.MARGIN, 0, posees)
        for node in posees:
            if node.get("chip"):
                self._draw_chip(node)
            else:
                self._draw_node(node)
        hauteur = max((node["y"] + self.BOX_H for node in posees),
                      default=self.BOX_H) + self.MARGIN
        if self.grows:
            # Le cadre prend la hauteur du dessin : c'est la page qui
            # defile, et elle ne peut le faire que si le dessin annonce ce
            # qu'il occupe.
            voulue = int(hauteur) + self.SCROLLBAR_ROOM
            if voulue != self._fitted:
                self._fitted = voulue
                self.pack_propagate(False)
                self.configure(height=voulue)
        # Le dessin se centre dans les deux sens quand il tient dans la
        # fenetre : cale en haut a gauche, un organigramme de deux cases
        # flotte au bord d'une grande zone vide. Le centrage passe par la
        # zone de defilement, qu'on etend symetriquement — deplacer les
        # cases elles-memes fausserait les coordonnees du survol.
        étendue = largeur + 2 * self.MARGIN
        gauche = min((étendue - width) / 2, 0)
        haut = (0 if self.grows
                else min((hauteur - self.canvas.winfo_height()) / 2, 0))
        self.canvas.configure(
            scrollregion=(gauche, haut,
                          max(étendue, width + gauche),
                          max(hauteur, self.canvas.winfo_height() + haut)))

    def _draw_node(self, node: Dict[str, Any]) -> None:
        x, y = node["x"], node["y"]
        choisi = node.get("manager") and node["manager"] == self.selected
        fond = theme.ACCENT_SOFT if choisi else theme.GROUND
        bord = theme.ACCENT if choisi else theme.LINE_STRONG
        case = self.canvas.create_rectangle(
            x, y, x + self.BOX_W, y + self.BOX_H,
            fill=fond, outline=bord, width=2 if choisi else 1)
        self._items[case] = node
        # Trois lignes, et trois seulement : le nom, le poste, le salaire
        # de base. Les effectifs et la mediane de l'equipe sont dans
        # l'info-bulle — une quatrieme ligne obligerait a agrandir la case,
        # donc le dessin, donc a le parcourir au lieu de le lire.
        nom = self._display(node.get("manager", ""))
        titre = self.canvas.create_text(
            x + 8, y + 11, anchor="w",
            text=_shorten(self, nom, self.BOX_W - 16,
                          _font(SIZE_SMALL, "bold")),
            font=_font(SIZE_SMALL, "bold"), fill=theme.INK)
        self._items[titre] = node
        poste = self.canvas.create_text(
            x + 8, y + 24, anchor="w",
            text=_shorten(self, node.get("job") or "—", self.BOX_W - 16),
            font=note_font(), fill=theme.MUTED)
        self._items[poste] = node
        # Le salaire du responsable, et non la mediane de son equipe : c'est
        # de lui qu'on parle en regardant sa case.
        propre = node.get("own_amount")
        valeur = self.canvas.create_text(
            x + 8, y + 37, anchor="w",
            text=(format_money(propre, self.currency) if propre is not None
                  else "montant masqué"),
            font=note_font(),
            fill=theme.INK_SOFT if propre is not None else theme.FAINT)
        self._items[valeur] = node
        for enfant in (list(node.get("children") or [])
                       + ([node["_chip"]] if node.get("_chip") else [])):
            self._connect(node, enfant)

    def _draw_chip(self, node: Dict[str, Any]) -> None:
        x, y = node["x"], node["y"]
        # Calee sur le bas de la rangee : alignee en haut, elle laissait
        # croire a un niveau hierarchique de plus.
        y += self.BOX_H - self.CHIP_H
        case = self.canvas.create_rectangle(
            x, y, x + self.BOX_W, y + self.CHIP_H,
            fill=theme.CANVAS, outline=theme.LINE, dash=(3, 2))
        self._items[case] = node
        nombre = node["individuals"]
        texte = f"{nombre} collaborateur{'s' if nombre > 1 else ''}"
        self.canvas.create_text(x + self.BOX_W / 2, y + self.CHIP_H / 2,
                                text=texte, font=note_font(),
                                fill=theme.MUTED)

    def _connect(self, parent: Dict[str, Any], enfant: Dict[str, Any]) -> None:
        """Trait coude entre deux cases : vertical, horizontal, vertical.

        Le trait droit en diagonale se croise avec ses voisins des trois
        rattachements, et l'oeil ne sait plus lequel descend ou.
        """
        haut = parent["y"] + self.BOX_H
        bas = enfant["y"]
        if enfant.get("chip"):
            bas += self.BOX_H - self.CHIP_H
        milieu = (haut + bas) / 2
        x1 = parent["x"] + self.BOX_W / 2
        x2 = enfant["x"] + self.BOX_W / 2
        self.canvas.create_line(x1, haut, x1, milieu, x2, milieu, x2, bas,
                                fill=theme.LINE_STRONG)


class PieChart(tk.Frame):
    """Repartition d'un effectif par modalite, en anneau.

    Un anneau plutot qu'un disque plein : le centre rend l'effectif total,
    qu'il faudrait sinon chercher ailleurs, et la comparaison de deux parts
    se fait sur la longueur d'arc dans les deux cas.

    La legende porte le nombre et la part. Lus dans le camembert ils se
    devinent ; ecrits, ils se citent — et c'est ce qu'on fait d'une
    repartition par CSP.

    Au-dela du nombre de parts qu'autorise le parametrage, la queue est
    regroupee dans un neutre qui ne ressemble a aucune modalite : un
    camembert a quinze parts ne se lit plus, et les plus petites n'ont meme
    plus la place d'un libelle.
    """

    RADIUS = 50
    HOLE = 29
    ROW = 20
    #: Place reservee a l'effectif et a la part, a droite de la legende.
    VALUES = 86

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=theme.CANVAS)
        _fonts(self)
        self.pack_propagate(False)
        self.slices: List[tuple] = []
        self.total = 0
        self.other = ""
        self.canvas = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self._items: Dict[int, str] = {}
        #: L'anneau, dessine une fois en image lissee. Tk ne lisse pas ses
        #: arcs : les bords d'un camembert y deviennent un escalier, et
        #: c'est la premiere chose qu'on voit d'une page. L'image est
        #: recalculee quand les donnees ou le theme changent, jamais a
        #: chaque redimensionnement.
        self._image: Optional[tk.PhotoImage] = None
        # Au premier trace, la colonne n'a pas encore sa largeur : la legende
        # se calait sur une largeur deux fois trop grande, et les libelles
        # s'ecrivaient par-dessus les effectifs.
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())
        # Une image que plus personne ne reference disparait du canevas
        # sans bruit : on la lache explicitement, et seulement a la
        # destruction de ce cadre-ci.
        self.bind("<Destroy>", self._forget_image, add="+")

    def _forget_image(self, event) -> None:
        if event.widget is self:
            self._image = None

    def set_parts(self, parts: Sequence[Dict[str, Any]], total: int,
                  maximum: int = 6) -> None:
        """`parts` : des entrees {label, count}, dans l'ordre voulu."""
        entrees = [(str(p.get("label", "")), int(p.get("count") or 0))
                   for p in parts if (p.get("count") or 0) > 0]
        entrees.sort(key=lambda couple: (-couple[1], couple[0]))
        self.other = ""
        if len(entrees) > maximum:
            queue = entrees[maximum:]
            self.other = f"Autres ({len(queue)} valeurs)"
            entrees = entrees[:maximum] + [(self.other,
                                            sum(n for _l, n in queue))]
        self.slices = entrees
        self.total = total
        self._image = None
        # Le cadre prend la hauteur du plus grand des deux — l'anneau ou la
        # legende : fixe, il laissait un trou sous un camembert a trois
        # parts, et aurait rogne une legende a sept.
        self._fit()
        self.redraw()

    def set_radius(self, value: int) -> None:
        """Rayon de l'anneau, pose par la page selon la place dont elle
        dispose. L'image est relachee : elle se recalcule a la taille
        demandee."""
        value = int(value)
        if value == self.RADIUS:
            return
        self.RADIUS = value
        self.HOLE = round(value * 0.58)
        self._image = None
        self._fit()
        self.redraw()

    def _fit(self) -> None:
        self.configure(height=max(2 * self.RADIUS + 16,
                                  len(self.slices) * self.ROW + 16))

    def _slice_at(self, x: float, y: float) -> Optional[tuple]:
        """La part survolee, retrouvee par l'angle.

        L'anneau est une seule image : le survol ne peut plus se lire sur
        l'objet pointe, il se calcule. C'est la meme trigonometrie que le
        trace, donc la meme part.
        """
        if not self.slices:
            return None
        cx = 4 + self.RADIUS
        cy = self.winfo_height() / 2 or self.RADIUS
        dx, dy = x - cx, y - cy
        distance = math.hypot(dx, dy)
        if not self.HOLE <= distance <= self.RADIUS:
            return None
        tour = (math.atan2(dx, -dy) / (2 * math.pi)) % 1.0
        total = sum(n for _l, n in self.slices) or 1
        position = 0.0
        for libelle, nombre in self.slices:
            position += nombre / total
            if tour < position:
                return libelle, nombre
        return self.slices[-1]

    def _on_motion(self, event) -> None:
        part = self._slice_at(event.x, event.y)
        if part is None:
            self.tooltip.hide()
            return
        libelle, nombre = part
        total = sum(n for _l, n in self.slices) or 1
        self.tooltip.show(f"{libelle}  ·  {nombre}  ·  "
                          f"{format_percent(100.0 * nombre / total, digits=0)}",
                          self.canvas.winfo_rootx() + event.x,
                          self.canvas.winfo_rooty() + event.y)

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        largeur = self.canvas.winfo_width()
        if largeur < 180:
            return
        if not self.slices:
            self.canvas.create_text(4, self.RADIUS, anchor="w",
                                    text="Aucune valeur renseignée.",
                                    font=note_font(), fill=theme.MUTED)
            return
        total = sum(n for _l, n in self.slices) or 1
        couleurs = palette.series_map([l for l, _n in self.slices],
                                      theme.ACTIVE.series,
                                      other=self.other or None,
                                      neutral=theme.FAINT)
        cx = 4 + self.RADIUS
        cy = self.winfo_height() / 2 or self.RADIUS
        if self._image is None:
            # `master` est indispensable : sans lui, l'image s'attache a la
            # racine Tk par defaut et non a cet interpreteur. Une seconde
            # fenetre fait alors disparaitre les images de la premiere —
            # « image pyimageN doesn't exist » au trace suivant.
            self._image = tk.PhotoImage(master=self.canvas, data=raster.ring(
                2 * self.RADIUS, self.HOLE,
                [(nombre / total, _rgb(couleurs.get(libelle, theme.ACCENT)))
                 for libelle, nombre in self.slices]))
        self.canvas.create_image(cx, cy, image=self._image)
        self.canvas.create_text(cx, cy - 6, text=format_number(self.total, 0),
                                font=_font(SIZE_SECTION + 1, "bold"),
                                fill=theme.INK)
        self.canvas.create_text(cx, cy + 10, text="salariés",
                                font=axis_font(), fill=theme.MUTED)

        x = 2 * self.RADIUS + 20
        y = cy - (len(self.slices) * self.ROW) / 2 + self.ROW / 2
        for libelle, nombre in self.slices:
            self.canvas.create_rectangle(
                x, y - 5, x + 10, y + 5,
                fill=couleurs.get(libelle, theme.ACCENT), outline="")
            self.canvas.create_text(
                x + 16, y, anchor="w", font=_font(SIZE_SMALL),
                fill=theme.INK_SOFT,
                text=_shorten(self, libelle, largeur - x - self.VALUES,
                              _font(SIZE_SMALL)))
            # Sans decimale : une part d'effectif a 65,6 % suggere une
            # exactitude que l'arrondi d'un comptage n'a pas.
            self.canvas.create_text(
                largeur - 2, y, anchor="e", font=axis_font(), fill=theme.MUTED,
                text=f"{nombre}   "
                     f"{format_percent(100.0 * nombre / total, digits=0)}")
            y += self.ROW


class ScaleChart(tk.Frame):
    """L'echelle de remuneration : une boite, plutot que sept lignes.

    Les percentiles alignes dans un tableau donnaient les chiffres sans
    donner la forme — la grille est-elle resserree ou ouverte, la mediane
    est-elle au milieu ou tiree vers le bas. La boite le montre d'un regard,
    et les chiffres restent : elle les accompagne, elle ne les remplace pas.

    Le cadrage s'arrete a P10 et P90. Le minimum et le maximum se lisent aux
    deux bouts, en retrait : une remuneration a zero ou un contrat
    d'expatrie commanderait sinon l'echelle entiere, et les neuf dixiemes de
    l'effectif se tasseraient sur un centimetre.
    """

    HEIGHT = 128
    PAD = 48

    def __init__(self, master: tk.Widget):
        super().__init__(master, background=theme.CANVAS, height=self.HEIGHT)
        _fonts(self)
        self.pack_propagate(False)
        self.salary: Dict[str, Any] = {}
        self.currency = "EUR"
        self.canvas = tk.Canvas(self, background=theme.CANVAS,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tooltip = Tooltip(self.canvas)
        self._items: Dict[int, str] = {}
        redraw_on_resize(self, self.canvas)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", lambda _e: self.tooltip.hide())

    def set_salary(self, salary: Dict[str, Any], currency: str = "EUR") -> None:
        self.salary = dict(salary or {})
        self.currency = currency
        self.redraw()

    def set_height(self, value: int) -> None:
        """Hauteur du cadre, posee par la page. Le trace reste centre."""
        value = int(value)
        if value == self.HEIGHT:
            return
        self.HEIGHT = value
        self.configure(height=value)
        self.redraw()

    def _on_motion(self, event) -> None:
        for item in self.canvas.find_overlapping(event.x, event.y,
                                                 event.x, event.y):
            if item in self._items:
                self.tooltip.show(self._items[item],
                                  self.canvas.winfo_rootx() + event.x,
                                  self.canvas.winfo_rooty() + event.y)
                return
        self.tooltip.hide()

    def points(self) -> List[tuple]:
        """Les percentiles **publies**, du plus bas au plus haut.

        Pas les cinq habituels : le moteur calcule toujours P10 a P90 pour
        les ratios de dispersion, mais l'utilisateur decide lesquels sont
        publies. Les tracer tous reviendrait a publier ce qu'il a retire.
        """
        rendus = []
        for entry in self.salary.get("published_percentiles") or []:
            valeur = self.salary.get(entry.get("key"))
            if valeur is not None:
                rendus.append((entry.get("key"), entry.get("label", ""),
                               float(valeur)))
        rendus.sort(key=lambda point: point[2])
        return rendus

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._items.clear()
        largeur = self.canvas.winfo_width()
        if largeur < 200:
            return
        rendus = self.points()
        if len(rendus) < 2:
            self.canvas.create_text(
                self.PAD, self.HEIGHT / 2, anchor="w", font=note_font(),
                fill=theme.MUTED,
                text="Les percentiles ne sont pas publiés pour cet effectif.")
            return
        bas, haut = rendus[0][2], rendus[-1][2]
        # La boite ne se dessine que si les deux quartiles sont publies :
        # une boite a un seul bord ne veut rien dire.
        valeurs = {clef: valeur for clef, _l, valeur in rendus}
        q1, q3 = valeurs.get("p25"), valeurs.get("p75")
        med = valeurs.get("p50", valeurs.get("median"))
        gauche, droite = self.PAD, largeur - self.PAD
        étendue = (haut - bas) or 1
        x_de = lambda v: gauche + (droite - gauche) * (v - bas) / étendue
        # Le trace occupe quatre-vingts pixels — les intitules au-dessus,
        # les deux rangees de montants en dessous — et se centre dans la
        # hauteur recue : posee a un tiers, la boite laissait un grand vide
        # sous elle des que la page lui donnait de la place.
        hauteur = self.canvas.winfo_height() or self.HEIGHT
        y = max(48, (hauteur - 82) / 2 + 30)
        self.canvas.create_line(x_de(bas), y, x_de(haut), y,
                                fill=theme.LINE_STRONG)
        for valeur in (bas, haut):
            self.canvas.create_line(x_de(valeur), y - 7, x_de(valeur), y + 7,
                                    fill=theme.LINE_STRONG)
        if q1 is not None and q3 is not None:
            boite = self.canvas.create_rectangle(
                x_de(q1), y - 14, x_de(q3), y + 14,
                fill=theme.ACCENT_SOFT, outline=theme.ACCENT)
            self._items[boite] = (
                f"La moitié centrale de l'effectif : "
                f"{format_money(q1, self.currency)} à "
                f"{format_money(q3, self.currency)}")
        if med is not None:
            self.canvas.create_line(x_de(med), y - 16, x_de(med), y + 16,
                                    fill=theme.ACCENT, width=3)
        # Une rangee de montants sur deux : sur une grille resserree, deux
        # percentiles voisins tombent a quelques pixels l'un de l'autre et
        # leurs montants s'ecrivent l'un sur l'autre.
        for index, (clef, libelle, valeur) in enumerate(rendus):
            fort = valeur == med
            self.canvas.create_text(
                x_de(valeur), y - 28, text=libelle.split(" (")[0],
                font=axis_font(),
                fill=theme.ACCENT if fort else theme.FAINT)
            self.canvas.create_text(
                x_de(valeur), y + (24 if index % 2 == 0 else 46),
                text=format_money(valeur, self.currency),
                font=_font(SIZE_SMALL, "bold") if fort else axis_font(),
                fill=theme.INK if fort else theme.MUTED)
        # Le minimum et le maximum passent au-dessus, sur leur propre
        # rangee. Poses a la hauteur du trait, aux deux bouts, ils
        # s'ecrivaient par-dessus l'echelle des que celle-ci atteignait le
        # bord — et c'est le cas des que la fenetre se resserre.
        rangee = max(y - 46, 10)
        for valeur, nom, x, ancre in (
                (self.salary.get("min"), "min", 2, "w"),
                (self.salary.get("max"), "max", largeur - 2, "e")):
            if valeur is None:
                continue
            self.canvas.create_text(
                x, rangee, anchor=ancre, font=axis_font(), fill=theme.FAINT,
                text=f"{nom} {format_money(valeur, self.currency)}")
