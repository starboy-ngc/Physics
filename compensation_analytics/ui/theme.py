"""Systeme visuel de l'interface.

L'aspect date d'une fenetre tkinter vient de trois choses : les bordures en
relief, les onglets a languettes et une typographie sans hierarchie. Ce
module traite les trois — a plat, avec une echelle de tailles explicite et
une palette restreinte — sans ajouter la moindre dependance.

La palette est celle des documents produits : l'ecran et le PDF appartiennent
a la meme famille visuelle.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Callable, Dict, List, Optional

# --------------------------------------------------------------- palette

INK = "#111c26"          # texte principal
INK_SOFT = "#3d4b59"     # texte courant
MUTED = "#6b7885"        # texte secondaire
FAINT = "#9aa5b1"        # texte tertiaire
LINE = "#e4e9ee"         # filets
LINE_STRONG = "#cfd7df"
CANVAS = "#ffffff"       # fond des contenus
GROUND = "#f7f9fb"       # fond de la fenetre
ACCENT = "#2f5d8a"
ACCENT_HOVER = "#26496d"
ACCENT_SOFT = "#eaf0f6"
WARN = "#8a5a12"
WARN_SOFT = "#fdf4e3"
CRIT = "#8f2f2f"
CRIT_SOFT = "#fbeded"
OK = "#2f6b4f"
DISABLED = "#c3ccd6"
STRIPE = "#fafbfc"   # alternance de lignes, a peine perceptible

#: Une seule echelle de tailles, du plus grand au plus petit.
SIZE_TITLE = 17
SIZE_KPI = 20
SIZE_BODY = 10
SIZE_SMALL = 9
SIZE_LABEL = 8

_PREFERRED = ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter",
              "Noto Sans", "DejaVu Sans", "Liberation Sans", "Arial")


def pick_family(root: tk.Misc) -> str:
    """Premiere police disponible parmi celles qui rendent bien a l'ecran."""
    available = set(tkfont.families(root))
    for family in _PREFERRED:
        if family in available:
            return family
    return tkfont.nametofont("TkDefaultFont").actual("family")


class Fonts:
    """Echelle typographique, construite une fois pour toute la fenetre."""

    def __init__(self, root: tk.Misc):
        family = pick_family(root)
        self.family = family
        self.title = tkfont.Font(root=root, family=family, size=SIZE_TITLE,
                                 weight="bold")
        self.kpi = tkfont.Font(root=root, family=family, size=SIZE_KPI,
                               weight="bold")
        self.body = tkfont.Font(root=root, family=family, size=SIZE_BODY)
        self.body_bold = tkfont.Font(root=root, family=family, size=SIZE_BODY,
                                     weight="bold")
        self.small = tkfont.Font(root=root, family=family, size=SIZE_SMALL)
        self.label = tkfont.Font(root=root, family=family, size=SIZE_LABEL,
                                 weight="bold")


def apply(root: tk.Misc, fonts: Fonts) -> ttk.Style:
    """Applique le theme. Tout est plat : aucune bordure en relief."""
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(".", background=CANVAS, foreground=INK_SOFT,
                    font=fonts.body, borderwidth=0, focuscolor=CANVAS)
    style.configure("TFrame", background=CANVAS)
    style.configure("Ground.TFrame", background=GROUND)
    style.configure("Card.TFrame", background=CANVAS)

    style.configure("TLabel", background=CANVAS, foreground=INK_SOFT)
    style.configure("Ground.TLabel", background=GROUND, foreground=INK_SOFT)
    style.configure("Title.TLabel", background=CANVAS, foreground=INK,
                    font=fonts.title)
    style.configure("Muted.TLabel", background=CANVAS, foreground=MUTED,
                    font=fonts.small)
    style.configure("MutedGround.TLabel", background=GROUND, foreground=MUTED,
                    font=fonts.small)
    style.configure("Label.TLabel", background=GROUND, foreground=FAINT,
                    font=fonts.label)
    style.configure("CardLabel.TLabel", background=CANVAS, foreground=FAINT,
                    font=fonts.label)
    style.configure("Kpi.TLabel", background=CANVAS, foreground=INK,
                    font=fonts.kpi)

    # Boutons plats : un plein pour l'action principale, un contour pour le
    # reste. Le theme clam dessine ses bordures avec trois couleurs (contour,
    # biseau clair, biseau sombre) : les egaliser supprime le relief tout en
    # gardant un filet visible.
    style.configure("Primary.TButton", background=ACCENT, foreground="white",
                    font=fonts.body_bold, borderwidth=0, padding=(16, 11),
                    relief="flat", anchor="center",
                    bordercolor=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT)
    style.map("Primary.TButton",
              background=[("disabled", DISABLED), ("pressed", ACCENT_HOVER),
                          ("active", ACCENT_HOVER)],
              bordercolor=[("disabled", DISABLED), ("pressed", ACCENT_HOVER),
                           ("active", ACCENT_HOVER)],
              lightcolor=[("disabled", DISABLED), ("pressed", ACCENT_HOVER),
                          ("active", ACCENT_HOVER)],
              darkcolor=[("disabled", DISABLED), ("pressed", ACCENT_HOVER),
                         ("active", ACCENT_HOVER)],
              foreground=[("disabled", "#f2f5f8")])

    for name, ground in (("Ghost.TButton", CANVAS),
                         ("GhostGround.TButton", GROUND)):
        style.configure(name, background=ground, foreground=ACCENT,
                        font=fonts.body, borderwidth=1, padding=(14, 9),
                        relief="solid", anchor="center",
                        bordercolor=LINE_STRONG, lightcolor=ground,
                        darkcolor=ground)
        style.map(name,
                  background=[("active", ACCENT_SOFT), ("disabled", ground)],
                  lightcolor=[("active", ACCENT_SOFT), ("disabled", ground)],
                  darkcolor=[("active", ACCENT_SOFT), ("disabled", ground)],
                  foreground=[("disabled", FAINT)],
                  bordercolor=[("active", ACCENT), ("disabled", LINE)])

    # Cases a cocher : un carre clair a filet fin, coche a l'accent.
    style.configure("TCheckbutton", background=GROUND, foreground=INK_SOFT,
                    font=fonts.body, focuscolor=GROUND, indicatorsize=13,
                    indicatormargin=(0, 2, 8, 2), padding=(0, 3),
                    indicatorbackground=CANVAS, indicatorforeground=ACCENT,
                    bordercolor=LINE_STRONG, upperbordercolor=LINE_STRONG,
                    lowerbordercolor=LINE_STRONG)
    style.map("TCheckbutton",
              background=[("active", GROUND)],
              indicatorbackground=[("disabled", GROUND), ("pressed", ACCENT_SOFT),
                                   ("active", ACCENT_SOFT)],
              upperbordercolor=[("selected", ACCENT), ("active", ACCENT)],
              lowerbordercolor=[("selected", ACCENT), ("active", ACCENT)])

    # Champs : un filet fin, pas de cadre creuse ni de bouton en relief.
    style.configure("TCombobox", fieldbackground=CANVAS, background=CANVAS,
                    foreground=INK_SOFT, arrowcolor=MUTED, arrowsize=13,
                    borderwidth=1, relief="solid", padding=(9, 7),
                    bordercolor=LINE_STRONG, lightcolor=CANVAS, darkcolor=CANVAS)
    style.map("TCombobox",
              fieldbackground=[("readonly", CANVAS), ("disabled", GROUND)],
              background=[("readonly", CANVAS), ("active", CANVAS)],
              arrowcolor=[("active", ACCENT), ("disabled", FAINT)],
              bordercolor=[("focus", ACCENT), ("hover", LINE_STRONG)],
              lightcolor=[("focus", CANVAS)], darkcolor=[("focus", CANVAS)])

    # Tableaux : les lignes se separent par l'espacement et une alternance
    # discrete, pas par une grille.
    style.configure("Treeview", background=CANVAS, fieldbackground=CANVAS,
                    foreground=INK_SOFT, rowheight=30, borderwidth=0,
                    relief="flat", font=fonts.body,
                    bordercolor=CANVAS, lightcolor=CANVAS, darkcolor=CANVAS)
    style.configure("Treeview.Heading", background=CANVAS, foreground=FAINT,
                    font=fonts.label, relief="flat", borderwidth=0,
                    padding=(8, 6, 8, 10))
    style.map("Treeview.Heading", background=[("active", CANVAS)],
              foreground=[("active", MUTED)])
    style.map("Treeview", background=[("selected", ACCENT_SOFT)],
              foreground=[("selected", INK)])

    # Ascenseur sans fleches : un simple curseur dans une gouttiere claire.
    style.layout("Flat.Vertical.TScrollbar", [
        ("Vertical.Scrollbar.trough", {
            "sticky": "ns",
            "children": [("Vertical.Scrollbar.thumb",
                          {"expand": "1", "sticky": "nswe"})]})])
    style.configure("Flat.Vertical.TScrollbar", background=LINE_STRONG,
                    troughcolor=GROUND, borderwidth=0, relief="flat",
                    arrowsize=0, width=8, bordercolor=GROUND,
                    lightcolor=LINE_STRONG, darkcolor=LINE_STRONG)
    style.map("Flat.Vertical.TScrollbar",
              background=[("active", MUTED), ("pressed", MUTED)],
              lightcolor=[("active", MUTED)], darkcolor=[("active", MUTED)])

    style.configure("TProgressbar", background=ACCENT, troughcolor=LINE,
                    borderwidth=0, thickness=3, bordercolor=LINE,
                    lightcolor=ACCENT, darkcolor=ACCENT)
    return style


class TabBar(tk.Frame):
    """Navigation soulignee, a la place des onglets a languettes.

    Les languettes en relief sont le detail qui date le plus une fenetre. Une
    barre de libelles avec un trait d'accent sous l'element actif se lit mieux
    et supporte davantage d'entrees.
    """

    def __init__(self, master: tk.Widget, fonts: Fonts,
                 on_change: Optional[Callable[[str], None]] = None):
        super().__init__(master, background=CANVAS)
        self.fonts = fonts
        self.on_change = on_change
        self._tabs: Dict[str, Dict[str, tk.Widget]] = {}
        self._order: List[str] = []
        self.active: Optional[str] = None
        self._row = tk.Frame(self, background=CANVAS)
        self._row.pack(fill="x")
        tk.Frame(self, height=1, background=LINE).pack(fill="x")

    def add(self, key: str, text: str) -> None:
        holder = tk.Frame(self._row, background=CANVAS)
        holder.pack(side="left")
        label = tk.Label(holder, text=text, background=CANVAS, foreground=MUTED,
                         font=self.fonts.body, padx=16, pady=10, cursor="hand2")
        label.pack()
        underline = tk.Frame(holder, height=2, background=CANVAS)
        underline.pack(fill="x")
        label.bind("<Button-1>", lambda _e, k=key: self.select(k))
        label.bind("<Enter>", lambda _e, k=key: self._hover(k, True))
        label.bind("<Leave>", lambda _e, k=key: self._hover(k, False))
        self._tabs[key] = {"label": label, "underline": underline}
        self._order.append(key)
        if self.active is None:
            self.select(key)

    def _hover(self, key: str, entering: bool) -> None:
        if key == self.active:
            return
        self._tabs[key]["label"].configure(
            foreground=INK if entering else MUTED)

    def select(self, key: str) -> None:
        for name, parts in self._tabs.items():
            chosen = name == key
            parts["label"].configure(
                foreground=ACCENT if chosen else MUTED,
                font=self.fonts.body_bold if chosen else self.fonts.body)
            parts["underline"].configure(background=ACCENT if chosen else CANVAS)
        self.active = key
        if self.on_change:
            self.on_change(key)


class Card(tk.Frame):
    """Bloc de contenu : fond blanc, filet fin, pas d'ombre ni de relief."""

    def __init__(self, master: tk.Widget, **kwargs):
        padding = kwargs.pop("padding", 14)
        super().__init__(master, background=CANVAS, highlightthickness=1,
                         highlightbackground=LINE, highlightcolor=LINE, **kwargs)
        self.inner = tk.Frame(self, background=CANVAS)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)


def separator(master: tk.Widget, ground: str = CANVAS) -> tk.Frame:
    frame = tk.Frame(master, height=1, background=LINE)
    return frame


class CheckRow(tk.Frame):
    """Case a cocher dessinee, plutot que l'indicateur du theme.

    L'indicateur natif est le dernier element en relief de la fenetre : un
    carre a filet et une coche tracee a la main tiennent la meme place et se
    lisent mieux.
    """

    BOX = 15

    def __init__(self, master: tk.Widget, text: str, variable: tk.BooleanVar,
                 fonts: Fonts, ground: str = GROUND):
        super().__init__(master, background=ground)
        self.variable = variable
        self.ground = ground
        self.box = tk.Canvas(self, width=self.BOX, height=self.BOX,
                             background=ground, highlightthickness=0)
        self.box.pack(side="left", pady=1)
        self.text = tk.Label(self, text=text, background=ground,
                             foreground=INK_SOFT, font=fonts.body, padx=8,
                             cursor="hand2")
        self.text.pack(side="left")
        for widget in (self, self.box, self.text):
            widget.bind("<Button-1>", self._toggle)
        self.box.configure(cursor="hand2")
        variable.trace_add("write", lambda *_: self._draw())
        self._draw()

    def _toggle(self, _event=None) -> None:
        self.variable.set(not self.variable.get())

    def _draw(self) -> None:
        self.box.delete("all")
        edge = self.BOX - 1
        checked = bool(self.variable.get())
        self.box.create_rectangle(
            0, 0, edge, edge,
            outline=ACCENT if checked else LINE_STRONG,
            fill=ACCENT if checked else CANVAS)
        if checked:
            self.box.create_line(3, 8, 6, 11, 12, 4, fill="white", width=2,
                                 capstyle="round", joinstyle="round")
