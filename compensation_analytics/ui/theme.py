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

from . import raster

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

#: Epaisseur des ascenseurs. Assez large pour se saisir a la souris.
SCROLLBAR_WIDTH = 12

_PREFERRED = ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter",
              "Noto Sans", "DejaVu Sans", "Liberation Sans", "Arial")


def _rgb(colour: str) -> "tuple[int, int, int]":
    """Traduit une couleur "#rrggbb" en triplet, pour les images."""
    value = colour.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


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
    # Dans clam, c'est "arrowsize" qui donne son epaisseur a l'ascenseur, y
    # compris sans fleche : a zero il tombait a un pixel de large. Il
    # fonctionnait, mais aucun curseur ne pouvait l'attraper.
    style.configure("Flat.Vertical.TScrollbar", background=LINE_STRONG,
                    troughcolor=GROUND, borderwidth=0, relief="flat",
                    arrowsize=SCROLLBAR_WIDTH, bordercolor=GROUND,
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


def attach_scrollbar(widget: tk.Misc, bar: ttk.Scrollbar, **packing) -> None:
    """Relie un ascenseur, et ne l'affiche que s'il sert.

    Une gouttiere permanente sur une zone qui tient entierement a l'ecran
    est du bruit, et laisse croire qu'il reste quelque chose a voir.

    `before` est indispensable : reempile apres la zone defilante, qui est
    en expansion, l'ascenseur ne recupere aucune largeur et reapparait
    invisible. On le remet donc a sa place d'origine.
    """
    if "before" not in packing:
        raise ValueError("attach_scrollbar exige \"before\" pour rendre "
                         "l'ascenseur a sa place dans l'empilement")

    def scrolled(first: str, last: str) -> None:
        if float(first) <= 0.0 and float(last) >= 1.0:
            bar.pack_forget()
        elif not bar.winfo_ismapped():
            bar.pack(**packing)
        bar.set(first, last)

    widget.configure(yscrollcommand=scrolled)


def bind_wheel(canvas: tk.Canvas, root: tk.Misc) -> None:
    """Fait defiler `canvas` a la molette quand le curseur le survole.

    La liaison est globale — sans quoi elle ne repondrait que si le canevas
    lui-meme a le focus, jamais quand le curseur est sur un champ qu'il
    contient — et le survol est verifie a chaque evenement.
    """

    def scroll(event) -> None:
        widget = root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if widget is canvas:
                break
            widget = getattr(widget, "master", None)
        else:
            return
        first, last = canvas.yview()
        if first <= 0.0 and last >= 1.0:
            return
        step = -1 if getattr(event, "delta", 0) > 0 or event.num == 4 else 1
        canvas.yview_scroll(step, "units")

    for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        canvas.bind_all(sequence, scroll, add="+")


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
        """Le canevas Tk ne lisse pas ses traces : la coche tracee a la ligne
        montrait ses marches. L'indicateur est donc une image antialiasee."""
        self.box.delete("all")
        checked = bool(self.variable.get())
        data = raster.checkbox(
            self.BOX, checked,
            fill=_rgb(ACCENT if checked else CANVAS),
            border=_rgb(ACCENT if checked else LINE_STRONG))
        # La reference doit survivre a l'appel : Tk ne retient pas l'image.
        self._image = tk.PhotoImage(master=self.box, data=data)
        self.box.create_image(0, 0, anchor="nw", image=self._image)
