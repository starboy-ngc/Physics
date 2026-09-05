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
from typing import Callable, Dict, List, Optional, Sequence

from . import raster

# --------------------------------------------------------------- palette

INK = "#111c26"          # texte principal
INK_SOFT = "#3d4b59"     # texte courant
MUTED = "#6b7885"        # texte secondaire
FAINT = "#9aa5b1"        # texte tertiaire
LINE = "#e4e9ee"         # filets
LINE_STRONG = "#cfd7df"
CANVAS = "#ffffff"       # fond des contenus
#: Une seule teinte de fond pour toute la fenetre. Les zones se distinguent
#: par l'espace et par un filet, jamais par un aplat ou un cadre : c'est ce
#: qui fait la difference entre une interface unie et un empilement de
#: boites.
GROUND = CANVAS
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
        self._visible: Dict[str, bool] = getattr(self, "_visible", {})
        self._visible[key] = True
        label = tk.Label(holder, text=text, background=CANVAS, foreground=MUTED,
                         font=self.fonts.body, padx=16, pady=10, cursor="hand2")
        label.pack()
        underline = tk.Frame(holder, height=2, background=CANVAS)
        underline.pack(fill="x")
        label.bind("<Button-1>", lambda _e, k=key: self.select(k))
        label.bind("<Enter>", lambda _e, k=key: self._hover(k, True))
        label.bind("<Leave>", lambda _e, k=key: self._hover(k, False))
        self._tabs[key] = {"label": label, "underline": underline,
                           "holder": holder}
        self._order.append(key)
        if self.active is None:
            self.select(key)

    def _hover(self, key: str, entering: bool) -> None:
        if key == self.active:
            return
        self._tabs[key]["label"].configure(
            foreground=INK if entering else MUTED)

    def set_visible(self, key: str, visible: bool) -> None:
        """Affiche ou retire une entree, sans changer l'ordre des autres.

        Un onglet dont le contenu ne peut pas etre publie — effectif trop
        faible — n'a rien a montrer : le laisser affiche promet un resultat
        qui n'existe pas.
        """
        if self._visible.get(key) == visible:
            return
        self._visible[key] = visible
        for name in self._order:
            self._tabs[name]["holder"].pack_forget()
        for name in self._order:
            if self._visible.get(name, True):
                self._tabs[name]["holder"].pack(side="left")
        if not self._visible.get(self.active, True):
            for name in self._order:
                if self._visible.get(name, True):
                    self.select(name)
                    break

    def visible_keys(self) -> List[str]:
        return [key for key in self._order if self._visible.get(key, True)]

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
    """Zone de contenu, sans cadre.

    Le cadre a disparu : sur une interface unie, ce sont l'espace et les
    intertitres qui separent, pas un filet autour de chaque bloc. La classe
    reste, car elle porte la marge interieure et evite d'eparpiller des
    valeurs de padding dans tous les ecrans.
    """

    def __init__(self, master: tk.Widget, **kwargs):
        padding = kwargs.pop("padding", 14)
        super().__init__(master, background=CANVAS, highlightthickness=0,
                         **kwargs)
        self.inner = tk.Frame(self, background=CANVAS)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)


def rule(master: tk.Widget, vertical: bool = False) -> tk.Frame:
    """Filet d'un pixel : la seule separation admise."""
    if vertical:
        return tk.Frame(master, width=1, background=LINE)
    return tk.Frame(master, height=1, background=LINE)


#: Teintes du texte des info-bulles, sur fond INK.
HINT_TEXT = "#e7ecf1"
HINT_FAINT = "#a8b5c2"


class Hints:
    """Info-bulles d'explication, une seule fenetre pour tout l'ecran.

    Une page de restitution porte une trentaine de chiffres. Leur donner a
    chacun sa fenetre en couterait autant au demarrage ; il n'y en a donc
    qu'une, deplacee et remplie au survol.

    L'apparition est retardee : une bulle qui surgit des que le curseur
    traverse un tableau se lit comme une gene, pas comme une aide. Et le
    texte garde sa hierarchie — intitule, definition, formule — plutot que
    de former un bloc ou l'oeil ne sait pas ou entrer.
    """

    #: Delai avant l'apparition. Assez long pour ignorer un passage de
    #: curseur, assez court pour repondre a une hesitation.
    DELAY = 450
    #: Largeur de renvoi a la ligne. Une bulle plus large se lit mal.
    WRAP = 320

    def __init__(self, root: tk.Misc, fonts: Fonts):
        self.root = root
        self.fonts = fonts
        self.window: Optional[tk.Toplevel] = None
        self.body: Optional[tk.Frame] = None
        self.lines: List[tk.Label] = []
        self._pending: Optional[str] = None

    def attach(self, widget: tk.Widget, hint: Optional[Sequence[str]],
               anchor: Optional[tk.Widget] = None):
        """Associe une explication a un widget. Sans texte, ne fait rien.

        `hint` se lit comme des paragraphes : le premier est l'intitule.

        `anchor` designe ce sous quoi la bulle se pose. Un indicateur ecrit
        sur deux lignes — son intitule, puis son chiffre — se survole souvent
        par l'intitule : posee sous lui, la bulle masquerait le chiffre que
        l'on cherche justement a comprendre. On l'ancre alors sous le bloc
        entier.
        """
        if not hint:
            return widget
        paragraphs = tuple(hint)
        under = anchor if anchor is not None else widget
        widget.bind("<Enter>",
                    lambda _e, w=under: self._schedule(w, paragraphs), add="+")
        widget.bind("<Leave>", lambda _e: self.hide(), add="+")
        # Un clic veut dire que l'utilisateur a autre chose en tete : la bulle
        # s'efface au lieu de rester posee sur ce qu'il vient d'ouvrir.
        widget.bind("<Button-1>", lambda _e: self.hide(), add="+")
        return widget

    # ------------------------------------------------------------ mecanique

    def _schedule(self, widget: tk.Widget, paragraphs) -> None:
        self._cancel()
        self._pending = self.root.after(
            self.DELAY, lambda: self._show(widget, paragraphs))

    def _cancel(self) -> None:
        if self._pending is not None:
            try:
                self.root.after_cancel(self._pending)
            except tk.TclError:
                pass
            self._pending = None

    def _build(self) -> None:
        self.window = tk.Toplevel(self.root)
        self.window.wm_overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(background=INK)
        # Marge interieure portee par un cadre, et non par chaque ligne :
        # l'ecart sous le dernier paragraphe vaut alors celui du haut, quel
        # que soit le nombre de paragraphes affiches.
        self.body = tk.Frame(self.window, background=INK)
        self.body.pack(fill="both", expand=True, padx=12, pady=(10, 3))

    def _line(self, index: int) -> tk.Label:
        """Ligne de rang `index`, creee au besoin puis reutilisee."""
        while len(self.lines) <= index:
            rank = len(self.lines)
            label = tk.Label(
                self.body, justify="left", background=INK,
                wraplength=self.WRAP, anchor="w",
                # Intitule en gras, definition en clair, formule en retrait :
                # trois niveaux, pour entrer par le nom de l'indicateur.
                font=self.fonts.body_bold if rank == 0 else self.fonts.small,
                foreground=(CANVAS if rank == 0
                            else HINT_TEXT if rank == 1 else HINT_FAINT))
            self.lines.append(label)
        return self.lines[index]

    def _show(self, widget: tk.Widget, paragraphs) -> None:
        self._pending = None
        # La page se reconstruit a chaque calcul : le widget survole peut
        # avoir ete detruit entre le survol et l'echeance.
        if not widget.winfo_exists():
            return
        if self.window is None:
            self._build()
        for index, paragraph in enumerate(paragraphs):
            line = self._line(index)
            line.configure(text=paragraph)
            if not line.winfo_manager():
                line.pack(anchor="w", fill="x", pady=(0, 7))
        for surplus in self.lines[len(paragraphs):]:
            surplus.pack_forget()
        self.window.update_idletasks()
        self._place(widget)
        self.window.deiconify()

    def _place(self, widget: tk.Widget) -> None:
        """Sous le champ survole, sans sortir de l'ecran.

        Aligne a gauche sur lui : la bulle ne recouvre pas la valeur que
        l'on est en train de lire.
        """
        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = max(0, min(widget.winfo_rootx(), screen_w - width - 4))
        y = widget.winfo_rooty() + widget.winfo_height() + 6
        if y + height > screen_h:
            y = max(0, widget.winfo_rooty() - height - 6)
        self.window.wm_geometry(f"+{int(x)}+{int(y)}")

    def hide(self) -> None:
        self._cancel()
        if self.window is not None:
            self.window.withdraw()


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
        # winfo_ismapped repond « visible a l'ecran » : il vaut faux des que
        # l'onglet parent n'est pas affiche, et l'ascenseur serait alors
        # reempile a chaque rafraichissement. winfo_manager repond bien a la
        # question posee : ce widget est-il pris en charge par le paquetage ?
        elif not bar.winfo_manager():
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
