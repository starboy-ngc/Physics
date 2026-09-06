"""Fenetre principale de l'interface graphique.

Elle suit le parcours attendu par un utilisateur RH :

    Importer -> Filtrer -> Analyser -> Explorer -> Restituer

Aucune regle de calcul n'y figure : chaque etape appelle le pipeline, comme
la ligne de commande. Ce qui est propre a l'interface, c'est l'exploration —
survoler un point, isoler une population, zoomer — qu'un document imprime ne
peut pas offrir.

L'analyse tourne dans un fil separe : sur 100 000 salaries elle prend une
quinzaine de secondes, et une fenetre figee pendant ce temps passerait pour
un plantage.
"""

from __future__ import annotations

import datetime as _dt
import os
import queue
import threading
import time as _time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from ..version import ENGINE_NAME, __version__
from ..core import metrics
from ..core.config import (Configuration, default_config_dir,
                           load_configuration)
from ..core.errors import CompensationError
from ..core.export import export_excel
from ..core.glossary import describe as define
from ..core.logging_setup import log_event
from ..core.pay_equity import calculate_category_gaps
from ..core.pipeline import AnalysisRequest, load_population, run_analysis
from ..core.quality import run_quality_check
from ..core.reporting import (format_money, format_number, format_percent,
                              format_years,
                              write_report)
from ..core.segmentation import (build_filters, dimension_fields,
                                 dimension_label, max_filter_values)
from ..core.slides import (build_deck, build_summary, write_slides_html,
                           write_slides_pdf)
from ..core.traceability import write_manifest
from . import theme
from .charts import (BandChart, BoxPlotChart, GapChart,
                     HistogramChart, PyramidChart, QuartileChart,
                     ScatterChart)
from .theme import Card, CheckRow, Fonts, TabBar

WINDOW_TITLE = f"{ENGINE_NAME} {__version__}"
#: Les parentheses distinguent l'absence de filtre d'une valeur qui,
#: elle, existerait vraiment dans le fichier.
_ALL = "(toutes)"

#: Les resultats d'abord, le controle qualite en dernier : on y revient
#: quand un chiffre surprend, on ne commence pas par lui.
TABS = (("population", "Vue d'ensemble"), ("graphique", "Graphique"),
        ("equite", "Pay Transparency"),
        ("qualite", "Qualité"))

#: Graphiques proposes dans l'onglet « Graphique », dans l'ordre d'affichage.
#: Les onglets de premier rang repondent a une question — qui, combien, quel
#: ecart — la ou ceux-ci repondaient tous les deux a « a quoi cela
#: ressemble-t-il ». Les reunir laisse la place d'en ajouter d'autres sans
#: allonger la barre principale : une entree de plus ici suffit.
#: Tris du tableau des postes. L'enjeu vient en premier : c'est la question
#: qui suit l'ecart — combien pour le refermer, et ou en priorite. Trier par
#: ampleur d'ecart seul met en tete des postes de quatre personnes.
CATEGORY_ORDERS = (("stake", "Enjeu"), ("gap", "Écart"),
                   ("headcount", "Effectif"), ("name", "Nom"))

CHARTS = (("nuage", "Rémunération/Ancienneté"),
          ("distribution", "Distribution"),
          ("boites", "Dispersion"))


def _hint(key: Optional[str], title: str):
    """Explication d'un indicateur, en paragraphes : intitule, sens, calcul.

    Les textes viennent du moteur : la formule affichee est celle qui est
    appliquee. Un indicateur sans entree ne recoit pas d'info-bulle plutot
    qu'une bulle vide.
    """
    entry = define(key) if key else None
    if entry is None:
        return None
    return (title, entry.definition, f"Calcul : {entry.formula}")


def _packed(widget, **packing):
    """Empile un widget et le rend. `pack` renvoie None et coupe l'enchainement."""
    widget.pack(**packing)
    return widget


def _signed_percent(value: Optional[float]) -> str:
    """Ecart relatif, signe explicite : « +12,4 % » se lit sans hesitation."""
    if value is None:
        return "—"
    return f"{value:+.1f} %".replace(".", ",")


def salary_scale_rows(salary: Dict[str, Any], currency: str) -> List[tuple]:
    """Echelle de remuneration : minimum, percentiles publies, maximum.

    Ecrite ici plutot qu'a chaque endroit qui l'affiche. La vue d'ensemble
    et la page composee la montraient toutes deux, avec leur propre copie du
    meme code : retirer un percentile de la configuration ou changer un
    libelle n'aurait tenu qu'a un seul des deux ecrans, et le meme fichier
    aurait porte deux echelles differentes selon l'onglet ouvert.
    """
    return ([("Minimum", format_money(salary.get("min"), currency), "min")]
            + [(entry["label"],
                format_money(salary.get(entry["key"]), currency), entry["key"])
               for entry in salary.get("published_percentiles", [])]
            + [("Maximum", format_money(salary.get("max"), currency), "max")])


def dispersion_rows(spread: Dict[str, Any], currency: str) -> List[tuple]:
    """Indicateurs de dispersion, avec la mise en forme propre a chacun.

    Meme raison : deux copies s'ecartent, une seule se corrige. La cle
    portee par chaque ligne est celle du glossaire, qui en donne la
    definition et la formule au survol.
    """
    variation = spread.get("coefficient_of_variation")
    return [
        ("Q3 - Q1", format_money(spread.get("interquartile_range"), currency),
         "interquartile_range"),
        ("Q3 / Q1", format_number(spread.get("q3_over_q1"), 2), "q3_over_q1"),
        ("P90 / P10", format_number(spread.get("p90_over_p10"), 2),
         "p90_over_p10"),
        ("Moyenne / Médiane", format_number(spread.get("mean_over_median"), 2),
         "mean_over_median"),
        ("Coefficient de variation",
         format_percent(None if variation is None else variation * 100),
         "coefficient_of_variation"),
    ]


class Application(tk.Tk):
    """Fenetre unique de l'outil."""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("1380x880")
        self.minsize(1120, 720)

        # La configuration est lue en premier : c'est elle qui porte le
        # theme, et un widget prend sa couleur a la construction. Tout ce qui
        # suit — le fond de la fenetre, les styles ttk, les graphiques — lit
        # la palette une fois qu'elle est posee.
        self.config_dir = config_dir or default_config_dir()
        self.configuration = load_configuration(self.config_dir)
        theme.load(self.configuration)

        self.configure(background=theme.GROUND)
        self.fonts = Fonts(self)
        theme.apply(self, self.fonts)
        # Une seule fenetre d'info-bulle pour toute l'application.
        self.hints = theme.Hints(self, self.fonts)

        self.source_path: Optional[str] = None
        self.population = None
        self.mapping = None
        self.headers: List[str] = []
        self.result = None
        self.filter_vars: Dict[str, tk.StringVar] = {}
        self.output_vars: Dict[str, tk.BooleanVar] = {}
        self._segments: List[Dict[str, Any]] = []
        # Numero de ligne -> identite. Vide tant qu'aucune analyse n'a
        # tourne, et vide aussi si le reglage d'ecran l'interdit.
        self._identities: Dict[int, str] = {}
        self._colour_fields: List[str] = []
        self._queue: queue.Queue = queue.Queue()

        self._build_layout()
        # La composition enregistree est relue avant le premier affichage :
        # c'est la promesse du bouton « Enregistrer », et elle ne tient que
        # si la page survit a la fermeture.
        self._set_state("Choisissez un fichier de population pour commencer.")

    # -------------------------------------------------------------- layout

    def _build_layout(self) -> None:
        header = tk.Frame(self, background=theme.CANVAS)
        header.pack(fill="x")
        inner = tk.Frame(header, background=theme.CANVAS)
        inner.pack(fill="x", padx=26, pady=(20, 16))
        tk.Label(inner, text="Analyse de rémunération", background=theme.CANVAS,
                 foreground=theme.INK, font=self.fonts.title).pack(side="left")
        self.source_label = tk.Label(inner, text="Aucun fichier chargé",
                                     background=theme.CANVAS, foreground=theme.FAINT,
                                     font=self.fonts.small)
        self.source_label.pack(side="left", padx=14, pady=(6, 0))
        ttk.Button(inner, text="Paramètres", style="Ghost.TButton",
                   command=self.open_settings).pack(side="right")
        theme.rule(header).pack(fill="x")

        # Le pied de page se reserve sa place avant le corps : empile apres
        # une zone en expansion, il n'obtiendrait aucune hauteur.
        footer = tk.Frame(self, background=theme.GROUND)
        footer.pack(side="bottom", fill="x", padx=26, pady=14)
        theme.rule(self).pack(side="bottom", fill="x")
        self.status = tk.Label(footer, text="", background=theme.GROUND,
                               foreground=theme.MUTED, font=self.fonts.small)
        self.status.pack(side="left")

        body = tk.Frame(self, background=theme.GROUND)
        body.pack(fill="both", expand=True)

        self.sidebar_card = Card(body, padding=0)
        self.sidebar_card.pack(side="left", fill="y")
        self.sidebar_card.configure(width=self.SIDEBAR_WIDTH)
        self.sidebar_card.pack_propagate(False)
        self._build_sidebar(self.sidebar_card.inner)
        self._build_sidebar_handle(body)
        theme.rule(body, vertical=True).pack(side="left", fill="y")

        content = Card(body, padding=0)
        content.pack(side="left", fill="both", expand=True, padx=(26, 8))
        self.tabbar = TabBar(content.inner, self.fonts, on_change=self._show_tab)
        # De l'air sous le filet : colle a lui, le contenu donnait une page
        # entassee en haut. La marge est posee une fois ici plutot que dans
        # chacune des pages, qui n'avaient d'ailleurs pas la meme.
        self.tabbar.pack(fill="x", pady=(0, 10))
        # Un onglet retire doit s'expliquer la ou l'utilisateur regarde,
        # au-dessus des pages, et non dans le pied de page ou l'oeil ne va
        # pas le chercher.
        self.notice = tk.Label(content.inner, background=theme.WARN_SOFT,
                               foreground=theme.WARN, font=self.fonts.small,
                               justify="left", anchor="w", padx=14, pady=9,
                               wraplength=900)
        self.pages = tk.Frame(content.inner, background=theme.CANVAS)
        self.pages.pack(fill="both", expand=True)
        self._build_pages()



    #: Largeur de la poignee de repli. Assez large pour se viser a la souris,
    #: assez etroite pour ne rien prendre a l'analyse.
    HANDLE_WIDTH = 24

    #: Largeur deployee de la colonne de gauche.
    SIDEBAR_WIDTH = 326
    #: Repli anime : duree totale et cadence visee. Une transition trop
    #: longue se subit ; trop courte, elle ne dit plus d'ou vient ni ou va la
    #: colonne. Un cinquieme de seconde est le compromis usuel pour un
    #: panneau lateral.
    FOLD_MS = 200
    #: Echeance entre deux images, soit soixante images par seconde. C'est un
    #: objectif, pas une garantie : une image trop lente est sautee, jamais
    #: attendue.
    FOLD_FRAME_MS = 16

    def _build_sidebar_handle(self, parent: tk.Frame) -> None:
        """Poignee de repli de la colonne de gauche.

        Une fois les filtres poses, ils n'ont plus besoin d'etre a l'ecran :
        replier la colonne rend deux cent quatre-vingt-dix pixels a la
        lecture, ce qui compte sur une pyramide ou un nuage. La poignee reste
        toujours visible — replier sans laisser de quoi deplier serait un
        piege.
        """
        self.sidebar_open = True
        self._fold_job = None
        self._fold_width = self.SIDEBAR_WIDTH
        self._frozen: List[tk.Widget] = []
        self.sidebar_handle = tk.Frame(parent, background=theme.GROUND,
                                       width=self.HANDLE_WIDTH, cursor="hand2")
        self.sidebar_handle.pack(side="left", fill="y")
        self.sidebar_handle.pack_propagate(False)
        # Le chevron du corps courant faisait six pixels de large : present,
        # mais introuvable. Il est trace ici a la chasse d'un titre.
        import tkinter.font as tkfont

        self._chevron = tkfont.Font(root=self, family=self.fonts.family,
                                    size=theme.SIZE_TITLE + 4)
        self.sidebar_arrow = tk.Label(self.sidebar_handle, text="‹",
                                      background=theme.GROUND,
                                      foreground=theme.MUTED,
                                      font=self._chevron, cursor="hand2")
        self.sidebar_arrow.pack(expand=True)
        for widget in (self.sidebar_handle, self.sidebar_arrow):
            widget.bind("<Button-1>", lambda _e: self.toggle_sidebar())
            widget.bind("<Enter>", lambda _e: self._hover_handle(True), add="+")
            widget.bind("<Leave>", lambda _e: self._hover_handle(False), add="+")
        # Un chevron seul ne dit pas ce qu'il fait : l'info-bulle le dit, et
        # son texte vaut dans les deux etats, sans avoir a le reecrire.
        self.hints.attach(self.sidebar_arrow,
                          ("Colonne des filtres",
                           "Masquer ou afficher la colonne de gauche."),
                          anchor=self.sidebar_handle)

    def _hover_handle(self, entering: bool) -> None:
        self.sidebar_arrow.configure(
            foreground=theme.ACCENT if entering else theme.MUTED)

    def toggle_sidebar(self) -> None:
        """Replie ou deplie la colonne de gauche, en glissant.

        La colonne ne disparait pas d'un coup : elle se retire, et le
        contenu prend la place laissee. Une apparition instantanee oblige a
        relire la page pour comprendre ce qui a bouge ; un glissement la
        raconte.

        Le chevron, lui, bascule des le clic : c'est l'accuse de reception
        du geste, il n'a pas a attendre la fin du mouvement.
        """
        self.sidebar_open = not getattr(self, "sidebar_open", True)
        self.sidebar_arrow.configure(text="‹" if self.sidebar_open else "›")
        if self.sidebar_open and not self.sidebar_card.winfo_manager():
            # « sidebar_handle » n'est jamais depaquete : c'est un repere sur
            # pour rendre la colonne a sa place dans l'empilement.
            self.sidebar_card.configure(width=1)
            self.sidebar_card.pack(side="left", fill="y",
                                   before=self.sidebar_handle)
        self._slide_sidebar()

    def _slide_sidebar(self) -> None:
        """Anime la largeur de la colonne jusqu'a son etat cible.

        La largeur courante est tenue ici plutot que relue sur le widget :
        « winfo_width » rend la derniere largeur mise en page, pas celle que
        l'on vient de demander. Au depliage, elle valait donc deja celle
        d'arrivee — depart et cible confondus, aucun mouvement. La tenir
        permet aussi de repartir de la position exacte quand on rebascule au
        milieu d'un glissement.
        """
        self._cancel_fold()
        self._freeze_charts()
        start = self._fold_width
        target = self.SIDEBAR_WIDTH if self.sidebar_open else 1
        if start == target:
            self._end_fold()
            return
        began = _time.perf_counter()

        def step() -> None:
            self._fold_job = None
            if not self.sidebar_card.winfo_exists():
                return
            # L'avancement se lit sur l'horloge, jamais sur un compteur
            # d'images. Compte, l'animation durait le temps que la machine
            # mettait a la dessiner : chaque image coute de 4 a 12 ms selon
            # l'onglet, et s'ajoutait au delai au lieu de s'y fondre — d'ou
            # une cadence qui changeait d'un onglet a l'autre, et s'effondrait
            # sur un poste lent. A l'horloge, le glissement dure toujours un
            # cinquieme de seconde : ce sont les images qui manquent, pas le
            # temps qui s'etire.
            elapsed = (_time.perf_counter() - began) * 1000.0
            if elapsed >= self.FOLD_MS:
                self._end_fold()
                return
            # Sortie amortie : le mouvement part vite et se pose, ce qui se
            # lit comme un objet qui glisse plutot que comme un saut decoupe.
            eased = 1 - (1 - elapsed / self.FOLD_MS) ** 3
            width = int(round(start + (target - start) * eased))
            if width != self._fold_width:
                self._fold_width = width
                self.sidebar_card.configure(width=width)
            # Prochaine echeance calee sur le debut du mouvement, et non sur
            # la fin de cette image : une image lente rattrape son retard au
            # lieu de le reporter sur toutes les suivantes.
            now = (_time.perf_counter() - began) * 1000.0
            due = (int(now // self.FOLD_FRAME_MS) + 1) * self.FOLD_FRAME_MS
            self._fold_job = self.after(max(int(round(due - now)), 1), step)

        step()

    def _end_fold(self) -> None:
        """Pose l'etat final exact.

        Une animation ne doit rien laisser en chemin : ni largeur approchee,
        ni colonne repliee mais toujours empilee.
        """
        self._fold_width = self.SIDEBAR_WIDTH if self.sidebar_open else 1
        self.sidebar_card.configure(width=self._fold_width)
        # Le degel attend que Tk ait refait sa mise en page : un graphique se
        # trace d'apres la largeur de son canevas, et celle-ci n'est a jour
        # qu'apres. Retrace trop tot, il restait vide.
        self._fold_job = self.after_idle(self._thaw_charts)
        if not self.sidebar_open:
            self.sidebar_card.pack_forget()
            # La colonne repart de sa pleine largeur au prochain depliage :
            # c'est la largeur d'arrivee qui est animee, pas la largeur nulle.
            self.sidebar_card.configure(width=1)

    def _page_charts(self) -> List[tk.Widget]:
        """Graphiques affiches sur l'onglet courant.

        On reconnait un graphique a ce qu'il sait se retracer et porte son
        canevas. On ne descend pas a l'interieur : le canevas d'un graphique
        est son enfant, et surtout le conteneur defilant d'une page est lui
        aussi un canevas — le vider supprimerait la page entiere.
        """
        found: List[tk.Widget] = []

        def walk(widget: tk.Misc) -> None:
            for child in widget.winfo_children():
                if hasattr(child, "redraw") and hasattr(child, "canvas"):
                    if child.winfo_manager():
                        found.append(child)
                else:
                    walk(child)

        page = self.tabs.get(self.tabbar.active)
        if page is not None:
            walk(page)
        return found

    def _freeze_charts(self) -> None:
        """Vide les graphiques de la page le temps du glissement.

        Tk repeint le contenu d'un canevas a chaque changement de geometrie,
        et ce cout n'est pas celui de notre trace : mesure, une image de
        glissement passe de 124 ms a 4,6 ms sur le nuage de deux mille points
        une fois son canevas vide. Un graphique que l'on comprime n'apprend
        de toute facon rien.

        On vide plutot que de depaqueter : le widget garde sa place dans
        l'empilement. Depaqueter puis repaqueter est la manoeuvre qui a deja
        produit deux defauts d'ordre dans cette fenetre.
        """
        if self._frozen:
            return
        self._frozen = self._page_charts()
        for chart in self._frozen:
            chart.canvas.delete("all")

    def _thaw_charts(self) -> None:
        self._fold_job = None
        for chart in self._frozen:
            if chart.winfo_exists():
                chart.redraw()
        self._frozen = []

    def _cancel_fold(self) -> None:
        job = getattr(self, "_fold_job", None)
        if job is not None:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self._fold_job = None

    def _section(self, parent, number: int, text: str,
                 action: Optional[str] = None, command=None) -> Optional[tk.Label]:
        """Intertitre numerote, avec une action facultative a sa droite."""
        row = tk.Frame(parent, background=theme.GROUND)
        row.pack(fill="x", pady=(18, 8))
        tk.Label(row, text=f"{number}", background=theme.ACCENT, foreground="white",
                 font=self.fonts.label, width=2, pady=1).pack(side="left")
        # Ancre a gauche : quand la colonne se replie, un libelle plus large
        # que la place restante est rogne par le milieu — « IMPORTER »
        # devenait « PORT ». Ancre, il se coupe par la fin, comme un mot que
        # l'on cesse de lire.
        tk.Label(row, text=text.upper(), background=theme.GROUND,
                 foreground=theme.FAINT, font=self.fonts.label,
                 anchor="w").pack(side="left", padx=8)
        if action is None:
            return None
        link = tk.Label(row, text=action, background=theme.GROUND, foreground=theme.ACCENT,
                        font=self.fonts.small, cursor="hand2")
        link.pack(side="right", padx=(0, 4))
        # L'action garde toujours sa place et son libelle. Elle s'eteint
        # quand elle n'a rien a faire : la faire disparaitre sous le curseur
        # au moment ou l'on clique donne l'impression d'un bouton instable.
        link.enabled = True

        def clic(_event) -> None:
            if link.enabled:
                command()

        def survol(_event) -> None:
            if link.enabled:
                link.configure(foreground=theme.ACCENT_HOVER)

        def sortie(_event) -> None:
            link.configure(foreground=theme.ACCENT if link.enabled else theme.FAINT)

        link.bind("<Button-1>", clic)
        link.bind("<Enter>", survol)
        link.bind("<Leave>", sortie)
        return link

    @staticmethod
    def _set_action_enabled(link: Optional[tk.Label], enabled: bool) -> None:
        """Allume ou eteint une action, sans jamais la retirer de l'ecran."""
        if link is None:
            return
        link.enabled = enabled
        link.configure(foreground=theme.ACCENT if enabled else theme.FAINT,
                       cursor="hand2" if enabled else "")

    def _build_sidebar(self, parent: tk.Widget) -> None:
        parent.configure(background=theme.GROUND)
        actions = tk.Frame(parent, background=theme.GROUND)
        actions.pack(side="bottom", fill="x", padx=(26, 22), pady=(18, 24))
        # Ancrees en bas : sur un ecran peu haut, la liste des filtres poussait
        # "Analyser" hors du cadre.
        self.analyse_button = ttk.Button(actions, text="Analyser",
                                         style="Primary.TButton",
                                         command=self.run_analysis)
        self.analyse_button.pack(fill="x")
        self.analyse_button.state(["disabled"])
        self.progress = ttk.Progressbar(actions, mode="indeterminate")
        self.export_button = ttk.Button(actions, text="Produire les documents",
                                        style="GhostGround.TButton",
                                        command=self.export_documents)
        self.export_button.pack(fill="x", pady=(8, 0))
        self.export_button.state(["disabled"])

        outer = tk.Canvas(parent, background=theme.GROUND, highlightthickness=0)
        bar = ttk.Scrollbar(parent, orient="vertical", command=outer.yview,
                            style="Flat.Vertical.TScrollbar")
        # L'ascenseur se reserve sa place en premier : empile apres une zone
        # en expansion, il n'obtenait aucune largeur et restait invisible.
        bar.pack(side="right", fill="y", padx=(0, 8), pady=4)
        outer.pack(side="left", fill="both", expand=True, padx=(26, 0))
        theme.attach_scrollbar(outer, bar, side="right", fill="y",
                               padx=(0, 8), pady=4, before=outer)
        steps = tk.Frame(outer, background=theme.GROUND)
        window = outer.create_window((0, 0), window=steps, anchor="nw")
        steps.bind("<Configure>",
                   lambda _e: outer.configure(scrollregion=outer.bbox("all")))
        outer.bind("<Configure>",
                   lambda e: outer.itemconfigure(window, width=e.width - 14))

        # La molette sur la colonne : sans elle, les dernieres dimensions et
        # les etapes 3 et 4 n'etaient atteignables qu'a l'ascenseur.
        theme.bind_wheel(outer, self)

        self._section(steps, 1, "Importer")
        ttk.Button(steps, text="Choisir un fichier…", style="GhostGround.TButton",
                   command=self.choose_file).pack(fill="x")
        self.mapping_label = tk.Label(steps, text="", background=theme.GROUND,
                                      foreground=theme.MUTED, font=self.fonts.small,
                                      wraplength=250, justify="left")
        self.mapping_label.pack(anchor="w", pady=(8, 0))

        self.reset_filters_link = self._section(
            steps, 2, "Filtrer", "Réinitialiser", self.reset_filters)
        # Eteinte tant qu'aucun critere n'est pose.
        self._set_action_enabled(self.reset_filters_link, False)
        self.filter_summary = tk.Label(steps, text="", background=theme.GROUND,
                                       foreground=theme.ACCENT, font=self.fonts.small)
        self.filter_summary.pack(anchor="w", pady=(0, 4))
        self.filters_frame = tk.Frame(steps, background=theme.GROUND)
        self.filters_frame.pack(fill="x")
        tk.Label(self.filters_frame, text="Chargez un fichier pour voir les filtres.",
                 background=theme.GROUND, foreground=theme.FAINT, font=self.fonts.small,
                 wraplength=250, justify="left").pack(anchor="w")

        self._section(steps, 3, "Restituer", "Tout / aucun",
                      self.toggle_outputs)
        self.outputs_frame = tk.Frame(steps, background=theme.GROUND)
        self.outputs_frame.pack(fill="x", pady=(0, 8))
        for key, label, default in (("rapport", "Rapport détaillé (HTML)", True),
                                    ("synthese", "Fiche standard (PDF)", True),
                                    ("slides", "Jeu de slides (PDF)", True),
                                    ("excel", "Classeur Excel", True)):
            var = tk.BooleanVar(value=default)
            self.output_vars[key] = var
            CheckRow(self.outputs_frame, label, var,
                     self.fonts).pack(anchor="w", pady=2)

    def reset_filters(self) -> None:
        """Ramene tous les criteres a « aucun filtre »."""
        for variable in self.filter_vars.values():
            variable.set(_ALL)
        self._update_filter_summary()

    def toggle_outputs(self) -> None:
        self._toggle_all(self.output_vars)

    @staticmethod
    def _toggle_all(variables: Dict[str, tk.BooleanVar]) -> None:
        """Tout cocher, ou tout decocher si tout l'etait deja."""
        if not variables:
            return
        target = not all(variable.get() for variable in variables.values())
        for variable in variables.values():
            variable.set(target)

    def _update_filter_summary(self) -> None:
        """Rappelle combien de criteres sont actifs.

        Les filtres se trouvent dans une colonne qui defile : sans ce
        rappel, un critere pose puis sorti du champ visible s'oublie, et
        l'analyse porte sur une population qu'on ne croit plus filtrer.
        """
        active = len(self._current_filters())
        self._set_action_enabled(self.reset_filters_link, bool(active))
        self.filter_summary.configure(
            text="" if not active
            else f"{active} critère(s) actif(s)")

    def _build_pages(self) -> None:
        self.tabs: Dict[str, tk.Frame] = {}
        for key, label in TABS:
            frame = tk.Frame(self.pages, background=theme.CANVAS)
            self.tabs[key] = frame
            self.tabbar.add(key, label)

        self.quality_summary = tk.Frame(self.tabs["qualite"], background=theme.CANVAS)
        self.quality_summary.pack(fill="x", padx=18, pady=(18, 12))
        # Tant qu'aucun fichier n'est charge, un tableau vide n'apprend rien :
        # la page dit ce qu'elle attend. _kpis vide ce cadre au premier calcul.
        tk.Label(self.quality_summary,
                 text="Aucun fichier chargé.\nChoisissez une population dans la "
                      "colonne de gauche pour lancer le contrôle qualité.",
                 background=theme.CANVAS, foreground=theme.MUTED, font=self.fonts.body,
                 justify="left").pack(anchor="w", pady=(40, 0))
        self.quality_tree = self._tree(self.tabs["qualite"],
                                       ("Sévérité", "Constat", "Lignes"),
                                       (120, 640, 90))
        self.quality_tree.master.pack_forget()

        # La page defile : le decoupage de l'anciennete s'etend selon les
        # carrieres presentes, et peut compter dix tranches. Sans cela, les
        # dernieres se retrouvaient coupees en bas de fenetre.
        overview = tk.Canvas(self.tabs["population"], background=theme.CANVAS,
                             highlightthickness=0)
        overview_bar = ttk.Scrollbar(self.tabs["population"], orient="vertical",
                                     command=overview.yview,
                                     style="Flat.Vertical.TScrollbar")
        overview_bar.pack(side="right", fill="y", padx=(0, 8), pady=4)
        overview.pack(side="left", fill="both", expand=True)
        theme.attach_scrollbar(overview, overview_bar, side="right", fill="y",
                               padx=(0, 8), pady=4, before=overview)
        theme.bind_wheel(overview, self)
        self.overview_frame = tk.Frame(overview, background=theme.CANVAS)
        window = overview.create_window((18, 18), window=self.overview_frame,
                                        anchor="nw")
        # « bbox("all") » commence au premier element, soit (18, 18) : la
        # zone de defilement demarrait donc apres la marge, qui disparaissait
        # des le premier affichage — le titre venait coller au filet des
        # onglets. On ancre la zone a l'origine, et on rend la marge du bas.
        self.overview_frame.bind(
            "<Configure>",
            lambda _e: self._scroll_region(overview))
        overview.bind("<Configure>",
                      lambda e: overview.itemconfigure(window,
                                                       width=e.width - 36))
        # Premier onglet de la barre, donc premier ecran vu : il doit dire ce
        # qu'il attend. _show_overview vide ce cadre au premier calcul.
        tk.Label(self.overview_frame,
                 text="Aucune analyse.\nChoisissez une population dans la "
                      "colonne de gauche, puis « Analyser ».",
                 background=theme.CANVAS, foreground=theme.MUTED, font=self.fonts.body,
                 justify="left").pack(anchor="w", pady=(40, 0))
        self._build_charts(self.tabs["graphique"])

        distribution = self.chart_pages["distribution"]
        self.histogram = HistogramChart(distribution)
        self.histogram.pack(fill="both", expand=True, padx=18, pady=(8, 18))

        boites = self.chart_pages["boites"]
        box_head = tk.Frame(boites, background=theme.CANVAS)
        box_head.pack(fill="x", padx=18, pady=(10, 0))
        tk.Label(box_head, text="DIMENSION", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")
        self.box_choice = ttk.Combobox(box_head, state="readonly", width=24,
                                       font=self.fonts.small)
        self.box_choice.pack(side="left", padx=10)
        self.box_choice.bind("<<ComboboxSelected>>", lambda _e: self._show_boxes())
        # Trier, c'est repondre a une autre question avec les memes chiffres :
        # « quels metiers paient le mieux » plutot que « comment se situe
        # celui-ci ». Le tri ne recalcule rien, il reordonne.
        tk.Label(box_head, text="TRIER PAR", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left", padx=(22, 0))
        self.box_order = ttk.Combobox(box_head, state="readonly", width=22,
                                      font=self.fonts.small,
                                      values=[label for _key, label
                                              in BoxPlotChart.ORDERS])
        self.box_order.current(0)
        self.box_order.pack(side="left", padx=10)
        self.box_order.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.boxplot.set_order(
                BoxPlotChart.ORDERS[self.box_order.current()][0]))
        self.boxplot = BoxPlotChart(boites)
        self.boxplot.pack(fill="both", expand=True, padx=18, pady=(6, 10))

        nuage = self.chart_pages["nuage"]
        controls = tk.Frame(nuage, background=theme.CANVAS)
        controls.pack(fill="x", padx=18, pady=(8, 4))
        tk.Label(controls, text="COLORER PAR", background=theme.CANVAS, foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")
        self.colour_choice = ttk.Combobox(controls, state="readonly", width=20,
                                          font=self.fonts.small)
        self.colour_choice.pack(side="left", padx=10)
        self.colour_choice.bind("<<ComboboxSelected>>", lambda _e: self._recolour())
        ttk.Button(controls, text="Réinitialiser le cadrage", style="Ghost.TButton",
                   command=lambda: self.scatter.reset_view()).pack(side="left")
        self.selection_label = tk.Label(controls, text="", background=theme.CANVAS,
                                        foreground=theme.INK, font=self.fonts.small)
        self.selection_label.pack(side="right")

        self.scatter = ScatterChart(nuage, on_select=self._on_point_selected)
        self.scatter.identify = self._identity_of
        self.scatter.pack(fill="both", expand=True, padx=18, pady=(4, 4))
        self.legend_frame = tk.Frame(nuage, background=theme.CANVAS)
        self.legend_frame.pack(fill="x", padx=18, pady=(0, 14))

        # La page defile : les indicateurs de la directive, la repartition
        # par quartile, le graphique des ecarts et son tableau ne tiennent
        # plus en un ecran — le tableau se retrouvait ecrase a un pixel.
        # La page est ordonnee par ce qu'elle sert a decider, et non par
        # l'ordre des indicateurs de la directive : d'abord de quoi est fait
        # l'ecart, puis ou il se loge poste par poste, et enfin les chiffres
        # a publier. La page defile : les trois blocs ne tiennent pas en un
        # ecran.
        equite = self._scrolling_page(self.tabs["equite"])

        # 1. De quoi l'ecart est fait -------------------------------------
        self.equity_frame = tk.Frame(equite, background=theme.CANVAS)
        self.equity_frame.pack(fill="x", pady=(18, 0))
        self.equity_note = tk.Label(equite, text="", background=theme.CANVAS,
                                    foreground=theme.MUTED, font=self.fonts.small,
                                    justify="left", anchor="w",
                                    wraplength=880)
        self.equity_note.pack(anchor="w", padx=18, pady=(0, 16))

        # 2. Poste par poste, le coeur de la page -------------------------
        self.category_head = tk.Frame(equite, background=theme.CANVAS)
        self.category_head.pack(fill="x", padx=18, pady=(4, 2))
        self.category_heading = tk.Label(
            self.category_head, text="Écart par poste",
            background=theme.CANVAS, foreground=theme.INK,
            font=self.fonts.section)
        self.category_heading.pack(side="left")
        # Le « travail de meme valeur » se lit d'abord par le poste — c'est
        # l'unite de la directive — mais un grade ou un etablissement
        # eclairent la meme question : l'axe doit pouvoir changer.
        tk.Label(self.category_head, text="COMPARER PAR", background=theme.CANVAS,
                 foreground=theme.FAINT, font=self.fonts.label).pack(
                     side="left", padx=(18, 0))
        self.category_choice = ttk.Combobox(self.category_head, state="readonly",
                                            width=20, font=self.fonts.small)
        self.category_choice.pack(side="left", padx=10)
        self.category_choice.bind("<<ComboboxSelected>>",
                                  lambda _e: self._show_categories())
        tk.Label(self.category_head, text="TRIER PAR", background=theme.CANVAS,
                 foreground=theme.FAINT, font=self.fonts.label).pack(
                     side="left", padx=(12, 0))
        self.category_order = ttk.Combobox(self.category_head, state="readonly",
                                           width=16, font=self.fonts.small,
                                           values=[label for _key, label
                                                   in CATEGORY_ORDERS])
        self.category_order.current(0)
        self.category_order.pack(side="left", padx=10)
        self.category_order.bind("<<ComboboxSelected>>",
                                 lambda _e: self._show_categories())
        self.category_title = tk.Label(equite, text="",
                                       background=theme.CANVAS, foreground=theme.FAINT,
                                       font=self.fonts.label,
                                       wraplength=880, justify="left")
        self.category_title.pack(anchor="w", padx=18, pady=(0, 6))
        # Le graphique porte la lecture, le tableau garde les chiffres
        # exacts : sur un indicateur reglementaire, on ne remplace pas les
        # seconds par la premiere.
        self.gap_chart = GapChart(equite)
        self.gap_chart.configure(height=196)
        self.gap_chart.pack_propagate(False)
        self.gap_chart.pack(fill="x", padx=18, pady=(0, 4))
        # Le rattrapage repond a la question qui vient apres l'ecart :
        # combien pour le refermer, et ou en priorite.
        self.category_tree = self._tree(
            equite,
            ("Poste", "Femmes", "Hommes", "Médiane femmes", "Médiane hommes",
             "Écart moyen", "Rattrapage"),
            (240, 80, 80, 130, 130, 110, 130))

        # 3. Les indicateurs a publier ------------------------------------
        self.quartile_block = tk.Frame(equite, background=theme.CANVAS)
        self.quartile_block.pack(fill="x", pady=(16, 0))
        tk.Label(self.quartile_block,
                 text="Répartition par quartile de rémunération",
                 background=theme.CANVAS, foreground=theme.INK,
                 font=self.fonts.section).pack(anchor="w", padx=18,
                                               pady=(2, 8))
        # Quatre barres empilees a la place des quatre lignes du tableau :
        # meme information, moins de hauteur, et le plafond de verre se voit
        # au lieu de se calculer.
        self.quartile_chart = QuartileChart(self.quartile_block)
        self.quartile_chart.pack(fill="x", padx=18, pady=(0, 10))
        self.compliance_note = tk.Label(
            equite, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, justify="left", anchor="w", wraplength=880)
        self.compliance_note.pack(anchor="w", padx=18, pady=(0, 16))

    @staticmethod
    def _scroll_region(canvas: tk.Canvas) -> None:
        """Zone de defilement ancree a l'origine, marges comprises."""
        box = canvas.bbox("all")
        if box:
            canvas.configure(scrollregion=(0, 0, box[2] + 18, box[3] + 18))

    def _scrolling_page(self, parent: tk.Frame) -> tk.Frame:
        """Rend `parent` defilant et retourne le cadre ou empiler le contenu.

        Meme montage que la vue d'ensemble : l'ascenseur se reserve sa place
        avant la zone en expansion, sans quoi il n'obtient aucune largeur, et
        la molette est liee pour que le bas de page soit atteignable sans
        viser la gouttiere.
        """
        canvas = tk.Canvas(parent, background=theme.CANVAS, highlightthickness=0)
        bar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview,
                            style="Flat.Vertical.TScrollbar")
        bar.pack(side="right", fill="y", padx=(0, 8), pady=4)
        canvas.pack(side="left", fill="both", expand=True)
        theme.attach_scrollbar(canvas, bar, side="right", fill="y",
                               padx=(0, 8), pady=4, before=canvas)
        theme.bind_wheel(canvas, self)
        inner = tk.Frame(canvas, background=theme.CANVAS)
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda _e: self._scroll_region(canvas))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(window, width=e.width))
        return inner

    def _build_charts(self, parent: tk.Frame) -> None:
        """Un onglet, plusieurs graphiques, choisis dans une barre subordonnee.

        Empiler les graphiques les uns sous les autres aurait tenu a deux ;
        au cinquieme, chacun serait devenu une vignette au bout d'un long
        defilement. Un seul a la fois, en pleine page, garde le zoom et le
        survol utilisables — et ajouter un graphique n'est qu'une entree de
        plus dans `CHARTS`.
        """
        head = tk.Frame(parent, background=theme.CANVAS)
        head.pack(fill="x", padx=18, pady=(14, 0))
        # Pas d'intertitre « GRAPHIQUE » : l'onglet porte deja ce nom quinze
        # pixels plus haut. La chasse plus petite suffit a dire que cette
        # barre est subordonnee a l'autre.
        self.chartbar = TabBar(head, self.fonts, on_change=self._show_chart,
                               secondary=True)
        self.chartbar.pack(side="left")
        theme.rule(parent).pack(fill="x", padx=18, pady=(6, 0))

        holder = tk.Frame(parent, background=theme.CANVAS)
        holder.pack(fill="both", expand=True)
        self.chart_pages: Dict[str, tk.Frame] = {}
        for key, label in CHARTS:
            self.chart_pages[key] = tk.Frame(holder, background=theme.CANVAS)
            self.chartbar.add(key, label)

    def _show_chart(self, key: str) -> None:
        for name, frame in getattr(self, "chart_pages", {}).items():
            frame.pack_forget()
        self.chart_pages[key].pack(fill="both", expand=True)

    def _show_tab(self, key: str) -> None:
        for name, frame in getattr(self, "tabs", {}).items():
            frame.pack_forget()
        self.tabs[key].pack(fill="both", expand=True)

    def _tree(self, parent, columns, widths, expand: bool = True,
              height: Optional[int] = None) -> ttk.Treeview:
        wrapper = tk.Frame(parent, background=theme.CANVAS)
        wrapper.pack(fill="both" if expand else "x", expand=expand,
                     padx=18, pady=(0, 18 if expand else 10))
        options = {"height": height} if height else {}
        tree = ttk.Treeview(wrapper, columns=columns, show="headings", **options)
        for name, width in zip(columns, widths):
            tree.heading(name, text=name.upper())
            tree.column(name, width=width, anchor="w" if width > 200 else "e")
        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview,
                               style="Flat.Vertical.TScrollbar")
        tree.pack(side="left", fill="both", expand=True)
        theme.attach_scrollbar(tree, scroll, side="right", fill="y",
                               pady=(30, 0), before=tree)
        return tree

    # ------------------------------------------------------- etapes

    def _set_state(self, message: str) -> None:
        self.status.configure(text=message)

    def choose_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Choisir un fichier de population",
            filetypes=[("Fichiers de population", "*.xlsx *.xlsm *.csv"),
                       ("Tous les fichiers", "*.*")])
        if not path:
            return
        try:
            self.configuration = load_configuration(self.config_dir)
            population, mapping, table = load_population(path, self.configuration)
        except CompensationError as error:
            messagebox.showerror("Import impossible", error.message)
            return
        self.source_path = path
        self.population = population
        self.mapping = mapping
        self.headers = list(table.headers)
        self.source_label.configure(
            text=f"{os.path.basename(path)} · {len(population)} salariés")
        unknown = len(mapping.unknown_columns)
        self.mapping_label.configure(
            text=f"{len(mapping.field_to_index)} colonnes reconnues"
                 + (f", {unknown} non reconnue(s) — voir Paramètres"
                    if unknown else ""))
        self._populate_filters()
        self.analyse_button.state(["!disabled"])
        self.export_button.state(["disabled"])
        self._show_quality()
        self.tabbar.select("qualite")
        self._set_state("Fichier chargé. Vérifiez la qualité, puis lancez l'analyse.")

    def open_settings(self) -> None:
        """Parametrage des champs : colonnes, filtres, axes d'analyse."""
        from .settings import SettingsWindow

        SettingsWindow(self, self.configuration, self.config_dir, self.fonts,
                       headers=getattr(self, "headers", None),
                       on_saved=self._settings_saved)

    def _settings_saved(self, directory: str, path: str) -> None:
        """Applique les nouveaux parametres sans redemarrer.

        Le fichier est relu : une colonne qui vient d'etre declaree n'a
        jamais ete lue, et ses valeurs manqueraient sinon jusqu'a la
        prochaine ouverture.
        """
        self.config_dir = directory
        try:
            self.configuration = load_configuration(directory)
            if self.source_path:
                population, mapping, table = load_population(
                    self.source_path, self.configuration)
                self.population, self.mapping = population, mapping
                self.headers = list(table.headers)
        except CompensationError as error:
            messagebox.showerror("Paramètres", error.message)
            return
        if self.population is not None:
            self._populate_filters()
            self._show_quality()
        self._set_state(f"Paramètres enregistrés dans {path}. "
                        "Relancez l'analyse pour les appliquer.")

    def _populate_filters(self) -> None:
        for child in self.filters_frame.winfo_children():
            child.destroy()
        self.filter_vars.clear()
        # Les listes sont alimentees par le fichier : l'utilisateur choisit
        # parmi ce qui existe, il n'a aucune syntaxe a taper.
        limit = max_filter_values(self.configuration)
        for field in dimension_fields(self.configuration):
            values = sorted({str(e.value(field) or "").strip()
                             for e in self.population} - {""})
            # Le seuil est un parametre, plus un nombre cache ici : au-dela,
            # une liste deroulante cesse d'etre utilisable.
            if not values or len(values) > limit:
                continue
            block = tk.Frame(self.filters_frame, background=theme.GROUND)
            block.pack(fill="x", pady=(0, 8))
            tk.Label(block, text=dimension_label(self.configuration, field),
                     background=theme.GROUND, foreground=theme.MUTED,
                     font=self.fonts.small).pack(anchor="w")
            var = tk.StringVar(value=_ALL)
            var.trace_add("write", lambda *_: self._update_filter_summary())
            ttk.Combobox(block, textvariable=var, values=[_ALL] + values,
                         state="readonly", font=self.fonts.small).pack(fill="x",
                                                                       pady=(2, 0))
            self.filter_vars[field] = var
        self._update_filter_summary()

    def _current_filters(self) -> List[Dict[str, Any]]:
        return [{"field": field, "operator": "eq", "value": var.get()}
                for field, var in self.filter_vars.items() if var.get() != _ALL]

    # ------------------------------------------------------------- analyse

    def run_analysis(self) -> None:
        if not self.source_path:
            return
        self.analyse_button.state(["disabled"])
        self.progress.pack(fill="x", pady=(8, 0))
        self.progress.start(12)
        self._set_state("Analyse en cours…")
        request = AnalysisRequest(
            source_path=self.source_path,
            config_dir=self.config_dir,
            filters=build_filters(self._current_filters(), self.configuration),
            # Aucune liste n'est imposee : le moteur segmente sur toutes les
            # dimensions reellement renseignees. Choisir a l'avance faisait
            # doublon avec la liste de l'onglet Segments, qui permet d'en
            # changer apres coup.
            segments=[],
            title="Analyse de rémunération",
            ignore_quality_errors=True,
        )
        threading.Thread(target=self._worker, args=(request,), daemon=True).start()
        self.after(80, self._poll)

    def _worker(self, request: AnalysisRequest) -> None:
        try:
            self._queue.put(("ok", run_analysis(request)))
        except CompensationError as error:
            self._queue.put(("erreur", error.message))
        except Exception as error:                      # garde-fou d'interface
            # Seul le type est remonte : le texte d'une exception Python peut
            # citer la cellule qui l'a provoquee, donc une donnee RH, et rien
            # de ce qui s'affiche ou se journalise ne doit en porter.
            log_event("interface", "analyse", status="ERREUR",
                      detail=type(error).__name__)
            self._queue.put(
                ("erreur", "L'analyse a échoué pour une raison technique "
                           f"({type(error).__name__}). Le détail figure dans "
                           "le journal technique."))

    def _poll(self) -> None:
        try:
            kind, payload = self._queue.get_nowait()
        except queue.Empty:
            self.after(80, self._poll)
            return
        self.progress.stop()
        self.progress.pack_forget()
        self.analyse_button.state(["!disabled"])
        if kind == "erreur":
            messagebox.showerror("Analyse impossible", payload)
            self._set_state("L'analyse n'a pas abouti.")
            return
        self.result = payload
        self.export_button.state(["!disabled"])
        try:
            self._render_results()
        except Exception as error:              # noqa: BLE001
            # Une erreur d'affichage laissait la fenetre figee sur « Analyse
            # en cours », onglets masques, sans rien dire : le calcul avait
            # abouti, seul le rendu avait echoue. Elle doit se voir.
            log_event("interface", "render", status="ERREUR",
                      detail=type(error).__name__)
            messagebox.showerror(
                "Affichage impossible",
                "Les résultats ont été calculés mais n'ont pas pu être "
                f"affichés ({type(error).__name__}). Les documents restent "
                "productibles.")
            self._set_state("Analyse terminée · affichage incomplet.")

    # ------------------------------------------------------------ affichage

    def _render_results(self) -> None:
        payload = self.result.payload
        currency = payload["salary"].get("currency", "EUR")
        self._index_identities()
        self._show_quality(payload["quality"])
        self._show_overview(payload)
        self.histogram.set_distribution(payload["distribution"], currency)
        self._show_scatter(payload["scatter"], currency)
        self._show_segments(payload["segments"])
        self._show_pay_equity(payload["pay_equity"])
        self._apply_eligibility(payload)

    def _apply_eligibility(self, payload: Dict[str, Any]) -> None:
        """Retire les onglets dont le contenu ne peut pas etre publie.

        Les seuils ne sont pas re-evalues ici : on lit ce que le moteur a
        deja decide. Un onglet vide, ou porteur d'un seul avertissement,
        promet un resultat qui n'existe pas — mais le retirer en silence
        laisserait croire a une disparition inexpliquee, d'ou le message.
        """
        segments = payload.get("segments") or []
        publishable = any(any(not row.get("masked") for row in block.get("rows", []))
                          for block in segments)
        # Les deux graphiques ont leur propre seuil : l'un peut disparaitre
        # sans l'autre, et l'onglet ne tombe que si les deux tombent.
        charts = {
            "distribution": bool(payload["distribution"].get("available")),
            # Les boites suivent le seuil graphique, plus exigeant que le
            # seuil de publication : un segment peut figurer dans le tableau
            # des segments sans qu'on ait le droit d'en tracer la dispersion.
            "boites": any(row.get("chartable")
                          for block in segments
                          for row in block.get("rows", [])),
            "nuage": bool(payload["scatter"].get("available")),
        }
        eligible = {
            "population": not (payload["population"].get("masked")
                               and payload["salary"].get("masked")),
            "graphique": any(charts.values()),
            "equite": bool(payload.get("pay_equity", {}).get("available")),
            "qualite": True,
        }
        for key, allowed in charts.items():
            self.chartbar.set_visible(key, allowed)
        for key, allowed in eligible.items():
            self.tabbar.set_visible(key, allowed)

        hidden = [label for key, label in TABS if not eligible[key]]
        # Un graphique retire alors que son onglet reste ouvert doit
        # s'expliquer autant qu'un onglet disparu : sans cela, il manque une
        # entree dans la barre et rien ne dit pourquoi.
        if eligible["graphique"]:
            hidden += [label for key, label in CHARTS if not charts[key]]
        headcount = payload["population"].get("headcount", 0)
        scope = payload.get("scope") or {}
        # Les filtres se lisent la plutot qu'en tete d'un onglet : ils
        # gouvernent toutes les pages, et la barre d'etat est la seule zone
        # visible quel que soit l'onglet ouvert.
        state = f"Analyse terminée · {headcount} salariés"
        if scope.get("filtered") and scope.get("description"):
            state += f" · {scope['description']}"
        if hidden:
            state += f" · {len(hidden)} vue(s) masquée(s)"
        self._set_state(state)
        if not hidden:
            self.notice.pack_forget()
            return
        listed = ", ".join(hidden)
        self.notice.configure(
            text=f"{listed} : effectif insuffisant pour publier ces résultats. "
                 f"Les seuils de confidentialité s'appliquent à {headcount} "
                 "salariés ; élargissez le filtre pour les afficher.")
        self.notice.pack(fill="x", after=self.tabbar)

    def _kpi_font(self, values, width: int, per_row: int,
                  floor: int = 600, smallest: int = 12):
        """Plus grande taille a laquelle aucune valeur n'est rognee.

        Une masse salariale a huit chiffres depasse la largeur d'une colonne
        et se retrouvait tronquee des deux cotes, le fond n'ayant aucune
        marge a rendre. Plutot que de reduire le nombre de colonnes — ce qui
        allongerait la page —, on mesure et on ajuste.

        `floor` protege du cas ou la largeur est demandee avant la mise en
        page et vaut alors presque rien. Un bloc du plan de travail, lui,
        connait sa largeur exacte : il passe zero, sinon un bloc au quart de
        page serait traite comme s'il en faisait six cents pixels.
        """
        import tkinter.font as tkfont

        # La marge absorbe l'ecart entre la largeur mesuree avant mise en
        # page et celle que la cellule recevra reellement.
        column = (max(width, floor) - 24 * (per_row - 1)) / per_row - 16
        for size in range(theme.SIZE_KPI, smallest, -1):
            candidate = tkfont.Font(root=self, family=self.fonts.family,
                                    size=size, weight="bold")
            if all(candidate.measure(value) <= column for value in values):
                return candidate
        return self.fonts.body_bold

    #: Nombre maximal d'indicateurs par rangee.
    KPI_MAX_PER_ROW = 4

    def _kpis(self, parent, pairs) -> None:
        for child in parent.winfo_children():
            child.destroy()
        band = tk.Frame(parent, background=theme.CANVAS)
        band.pack(fill="x", pady=(0, 16))
        parent.update_idletasks()
        # Une grille a colonnes egales, quatre au plus par rangee : au-dela,
        # la colonne devient trop etroite pour une valeur monetaire et le
        # chiffre est rogne des deux cotes. Les rangees sont equilibrees.
        rows_needed = -(-len(pairs) // self.KPI_MAX_PER_ROW) or 1
        per_row = -(-len(pairs) // rows_needed)
        font = self._kpi_font([pair[1] for pair in pairs],
                              band.winfo_width(), per_row)
        for index, pair in enumerate(pairs):
            # La cle du glossaire est facultative : un compteur qui se lit
            # tout seul n'a pas besoin d'etre explique.
            label, value = pair[0], pair[1]
            note = _hint(pair[2] if len(pair) > 2 else None, label)
            row, column = divmod(index, per_row)
            cell = tk.Frame(band, background=theme.CANVAS)
            span = per_row - column if index == len(pairs) - 1 else 1
            cell.grid(row=row, column=column, columnspan=span, sticky="nsew",
                      padx=(0, 24) if column + span < per_row else 0,
                      pady=(0, 20) if row == 0 else 0)
            band.grid_columnconfigure(column, weight=1, uniform="kpi")
            self.hints.attach(
                _packed(tk.Label(cell, text=label.upper(), background=theme.CANVAS,
                                 foreground=theme.FAINT, font=self.fonts.label),
                        anchor="w"), note, anchor=cell)
            self.hints.attach(
                _packed(tk.Label(cell, text=value, background=theme.CANVAS,
                                 foreground=theme.INK, font=font),
                        anchor="w", pady=(1, 0)), note, anchor=cell)

    def _fill(self, tree: ttk.Treeview, rows, flagged=None) -> None:
        tree.tag_configure("pair", background=theme.STRIPE)
        tree.tag_configure("alerte", background=theme.WARN_SOFT, foreground=theme.WARN)
        tree.delete(*tree.get_children())
        for index, row in enumerate(rows):
            tags = ["pair"] if index % 2 else []
            if flagged is not None and flagged(index):
                tags = ["alerte"]
            tree.insert("", "end", values=row, tags=tuple(tags))

    def _show_quality(self, quality: Optional[Dict[str, Any]] = None) -> None:
        if quality is None:
            if self.population is None or self.mapping is None:
                return
            quality = run_quality_check(self.population, self.mapping,
                                        self.configuration).as_dict()
        self._kpis(self.quality_summary, [
            ("Lignes importées", str(quality.get("lignes_importees", 0))),
            ("Salariés uniques", str(quality.get("salaries_uniques", 0))),
            ("Doublons", str(quality.get("doublons", 0))),
            ("Salaires manquants", str(quality.get("salaires_manquants", 0))),
            ("Anomalies critiques", str(quality.get("anomalies_critiques", 0))),
        ])
        statut = quality.get("statut", "")
        colour = {"CONFORME": theme.OK, "POINTS DE VIGILANCE": theme.WARN}.get(statut, theme.CRIT)
        banner = tk.Frame(self.quality_summary, background=theme.CANVAS)
        banner.pack(fill="x")
        tk.Label(banner, text=f"  {statut}", background=theme.CANVAS, foreground=colour,
                 font=self.fonts.body_bold).pack(anchor="w")
        constats = quality.get("constats", [])
        wrapper = self.quality_tree.master
        if constats and not wrapper.winfo_manager():
            wrapper.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        elif not constats and wrapper.winfo_manager():
            wrapper.pack_forget()
        self._fill(self.quality_tree,
                   [(item["severite"].capitalize(), item["message"],
                     item["lignes_concernees"])
                    for item in constats])

    def _show_scope(self, scope: Dict[str, Any], population, salary) -> None:
        """Avec quelle prudence lire la page.

        Le moteur demande de la prudence sous un certain effectif ; le
        rapport le disait, l'ecran ne le montrait que si tout etait masque —
        c'est-a-dire quand il n'y avait plus rien a lire.

        Le perimetre, lui, n'est plus ici : il vaut pour tous les onglets et
        non pour cette seule page, et il se lit donc dans la barre d'etat.
        """
        caution = population.get("warning") or salary.get("warning")
        if caution and not (population.get("masked") and salary.get("masked")):
            tk.Label(self.overview_frame, text=caution,
                     background=theme.WARN_SOFT, foreground=theme.WARN,
                     font=self.fonts.small, anchor="w", justify="left",
                     padx=12, pady=8, wraplength=900).pack(fill="x",
                                                           pady=(0, 14))

    def _show_overview(self, payload: Dict[str, Any]) -> None:
        """Population et remuneration sur une seule page, en deux colonnes.

        Le bandeau d'indicateurs qui coiffait la page a disparu : il posait
        six chiffres au-dessus de deux colonnes qui parlaient deja d'eux, et
        repetait la mediane que l'echelle affiche trois centimetres plus bas.
        Chaque colonne porte donc les siens, en tete, sous la meme forme que
        les tableaux qui suivent.

        Rien n'y figure deux fois. Les scalaires de population — effectif,
        ages, anciennetes — sont reunis dans une seule liste au lieu d'etre
        partages entre un bandeau et les en-tetes des deux pyramides ; et la
        liste de remuneration ne reprend ni la mediane ni les percentiles,
        qui sont l'echelle elle-meme.
        """
        population = payload["population"]
        salary = payload["salary"]
        for child in self.overview_frame.winfo_children():
            child.destroy()
        currency = salary.get("currency", "EUR")
        self._show_scope(payload.get("scope") or {}, population, salary)
        if population.get("masked") and salary.get("masked"):
            tk.Label(self.overview_frame,
                     text=population.get("warning") or salary.get("warning", ""),
                     background=theme.CANVAS, foreground=theme.WARN,
                     font=self.fonts.body, wraplength=760,
                     justify="left").pack(anchor="w")
            return

        # Deux colonnes independantes, et non une grille : dans une grille,
        # la rangee prend la hauteur du plus grand des deux blocs, et le bloc
        # court laisse un trou au milieu de la page. Empilees, chaque colonne
        # se referme sur son contenu et le vide tombe en bas.
        columns = tk.Frame(self.overview_frame, background=theme.CANVAS)
        columns.pack(fill="both", expand=True)
        left = tk.Frame(columns, background=theme.CANVAS)
        left.pack(side="left", fill="both", expand=True, padx=(0, 36))
        right = tk.Frame(columns, background=theme.CANVAS)
        right.pack(side="left", fill="both", expand=True)

        if not population.get("masked"):
            self._ruled_panel(
                left, "Population", (), [
                    ("Effectif", str(population.get("headcount", 0)),
                     "headcount"),
                    ("Âge médian", format_years(population.get("age_median")),
                     "age_median"),
                    ("Âge moyen", format_years(population.get("age_mean")),
                     "age_mean"),
                    ("Ancienneté médiane",
                     format_years(population.get("tenure_median")),
                     "tenure_median"),
                    ("Ancienneté moyenne",
                     format_years(population.get("tenure_mean")),
                     "tenure_mean"),
                ], emphasis="Effectif", key="population_summary")
            # Les pyramides n'ont plus de chiffre en tete : leurs moyennes
            # sont juste au-dessus, dans la liste.
            self._pyramid_panel(left, "Pyramide des âges",
                                population.get("age_bands", []), None,
                                key="age_bands")
            self._pyramid_panel(left, "Structure d'ancienneté",
                                population.get("tenure_bands", []), None,
                                key="tenure_bands")

        if not salary.get("masked"):
            spread = salary.get("dispersion") or {}
            variation = spread.get("coefficient_of_variation")
            # Ni la mediane ni un percentile ici : ils sont l'echelle, juste
            # en dessous. Ne restent que les deux chiffres qui n'y figurent
            # pas.
            # Le meme ecran veut dire deux choses differentes selon le champ
            # analyse : « Salaire de base » ou « Remuneration totale ». Il le
            # dit desormais, comme le font l'onglet Segments et le rapport.
            self._ruled_panel(
                right, "Rémunération", (), [
                    ("Masse salariale",
                     format_money(salary.get("payroll"), currency), "payroll"),
                    ("Salaire moyen",
                     format_money(salary.get("mean"), currency), "mean"),
                ], key="salary_summary",
                extra=("Champ analysé",
                       salary.get("field_label") or salary.get("field", ""),
                       "analysis_field"))
            self._ruled_panel(
                right, "Échelle de rémunération", ("Percentile", "Valeur"),
                salary_scale_rows(salary, currency),
                emphasis="Médiane (P50)", key="salary_scale")
            self._ruled_panel(
                right, "Dispersion", ("Indicateur", "Valeur"),
                dispersion_rows(spread, currency), key="dispersion")

    def _panel_head(self, parent, title: str, extra=None,
                    key: Optional[str] = None) -> tk.Frame:
        """Intitule, chiffre d'appoint a droite, filet. Chacun s'explique."""
        cell = tk.Frame(parent, background=theme.CANVAS)
        cell.pack(fill="x", pady=(0, 26))
        head = tk.Frame(cell, background=theme.CANVAS)
        head.pack(fill="x", pady=(0, 8))
        # Un intertitre doit primer sur ce qu'il introduit. Il partageait la
        # chasse, la casse et la teinte des en-tetes de colonne — 2,5:1, moins
        # lisible que ses propres lignes a 8,9:1. Il passe donc en corps 12
        # gras, encre pleine, et en casse normale : les petites majuscules
        # restent aux en-tetes de colonne, un rang plus bas.
        self.hints.attach(
            _packed(tk.Label(head, text=title, background=theme.CANVAS,
                             foreground=theme.INK, font=self.fonts.section),
                    side="left"),
            _hint(key, title))
        if extra:
            label, value = extra[0], extra[1]
            self.hints.attach(
                _packed(tk.Label(head, text=f"{label} : {value}",
                                 background=theme.CANVAS, foreground=theme.MUTED,
                                 font=self.fonts.small), side="right"),
                _hint(extra[2] if len(extra) > 2 else None, label))
        theme.rule(cell).pack(fill="x", pady=(0, 6))
        return cell

    def _ruled_panel(self, parent, title, headers, rows,
                     emphasis: Optional[str] = None,
                     key: Optional[str] = None, extra=None) -> None:
        """Tableau a l'anglaise : aucune grille, des filets aux articulations.

        Un tableau se lit d'autant mieux qu'il porte peu de traits. On garde
        un filet sous l'en-tete et un a la fin, l'alignement fait le reste :
        les libelles a gauche, les valeurs a droite, sur une chasse
        reguliere. La ligne remarquable est mise en avant plutot que
        signalee par une couleur de fond.
        """
        cell = self._panel_head(parent, title, extra, key=key)
        table = tk.Frame(cell, background=theme.CANVAS)
        table.pack(fill="x")
        table.grid_columnconfigure(0, weight=1)

        # En-tetes facultatifs : sur une liste de deux colonnes, « Indicateur »
        # et « Valeur » ne disent rien que la lecture n'ait deja compris. Ils
        # ne servent que la ou plusieurs tableaux se suivent et se comparent.
        columns = max(len(headers), 2)
        for index, name in enumerate(headers):
            # Un rang plus bas que l'intertitre, mais lisible : a 2,5:1 les
            # petites majuscules se devinaient plus qu'elles ne se lisaient.
            tk.Label(table, text=name.upper(), background=theme.CANVAS,
                     foreground=theme.MUTED, font=self.fonts.label,
                     anchor="w" if index == 0 else "e").grid(
                         row=0, column=index, sticky="ew", pady=(0, 7))
        if headers:
            theme.rule(table).grid(row=1, column=0, columnspan=columns,
                                   sticky="ew")

        for position, (label, value, entry_key) in enumerate(rows):
            highlighted = emphasis is not None and label == emphasis
            note = _hint(entry_key, label)
            for index, text in enumerate((label, value)):
                widget = tk.Label(
                    table, text=str(text), background=theme.CANVAS,
                    foreground=theme.INK if highlighted else theme.INK_SOFT,
                    font=self.fonts.body_bold if highlighted else self.fonts.body,
                    anchor="w" if index == 0 else "e")
                widget.grid(row=2 + position, column=index, sticky="ew",
                            pady=6, padx=(0, 0) if index else (0, 24))
                self.hints.attach(widget, note)
        theme.rule(table).grid(row=2 + len(rows), column=0,
                               columnspan=columns, sticky="ew", pady=(4, 0))

    def _pyramid_panel(self, parent, title, bands, extra,
                       key: Optional[str] = None) -> None:
        """Pyramide si le sexe est renseigne, barres simples sinon."""
        cell = self._panel_head(parent, title, extra, key=key)
        pyramid = PyramidChart(cell)
        pyramid.set_rows(bands)
        if pyramid.has_split():
            pyramid.pack(fill="x")
            return
        # Sans la colonne « Sexe », une pyramide n'aurait qu'une aile : on
        # retombe sur la lecture en barres plutot que d'afficher un demi
        # graphique.
        pyramid.destroy()
        chart = BandChart(cell)
        chart.pack(fill="x")
        chart.set_rows(bands)

    def _show_pay_equity(self, equity: Dict[str, Any]) -> None:
        """Ecarts de remuneration entre les sexes.

        La population est celle qu'ont retenue les filtres de la colonne de
        gauche, comme pour tous les autres onglets : l'outil n'a qu'un seul
        endroit ou l'on restreint, et ce qui s'affiche est ce qui s'exporte.
        """
        gender_field = equity.get("gender_field", "gender")
        # Le champ du sexe est ecarte des axes : croiser l'ecart H/F par sexe
        # donnerait des categories d'un seul sexe, toutes masquees.
        self._category_fields = [field for field
                                 in dimension_fields(self.configuration)
                                 if field != gender_field]
        self.category_choice.configure(values=[
            dimension_label(self.configuration, field)
            for field in self._category_fields])
        configured = equity.get("category_field")
        if configured in self._category_fields:
            self.category_choice.current(self._category_fields.index(configured))
        elif self._category_fields:
            self.category_choice.current(0)

        for child in self.equity_frame.winfo_children():
            child.destroy()
        if not equity.get("available"):
            tk.Label(self.equity_frame, text=equity.get("warning", ""),
                     background=theme.CANVAS, foreground=theme.WARN, font=self.fonts.body,
                     wraplength=760, justify="left").pack(anchor="w", padx=18,
                                                          pady=(8, 0))
            self.equity_note.configure(text="")
            self.compliance_note.configure(text="")
            self.quartile_block.pack_forget()
            self.category_title.configure(text="")
            self.quartile_chart.set_rows([])
            self._fill(self.category_tree, [])
            return

        pay = equity["pay"]
        variable = equity["variable"]
        coverage = equity["variable_coverage"]
        # Le bandeau ne repete plus le meme ecart sous trois formes : il
        # montre de quoi l'ecart global est fait. Un ecart global melange
        # deux faits opposes — des femmes moins payees sur le meme poste, et
        # des femmes plus nombreuses sur les postes les moins payes — qui
        # appellent l'un une revalorisation, l'autre une politique de
        # mobilite. Additionnes, ils sont indecidables.
        self._decomposed = self._category_block()
        block = self._decomposed
        self._kpis(self.equity_frame, [
            ("Écart global", _signed_percent(pay.get("mean_gap")), "mean_gap"),
            ("À poste comparable",
             _signed_percent((block or {}).get("comparable_gap")),
             "comparable_gap"),
            ("Effet de structure",
             _signed_percent((block or {}).get("structure_gap")),
             "structure_gap"),
            ("Rattrapage",
             format_money((block or {}).get("at_stake_total"),
                          self.result.payload["salary"].get("currency", "EUR")),
             "at_stake_total"),
            ("Effectif F / H",
             f'{equity["female_count"]} / {equity["male_count"]}',
             "female_count"),
        ])
        self.equity_frame.pack_configure(padx=18)
        self.equity_note.configure(text=self._decomposition_note(equity, block))

        if not self.quartile_block.winfo_manager():
            # « compliance_note » n'est jamais depaquetee : c'est un repere
            # sur pour rendre le bloc a sa place apres l'avoir masque.
            self.quartile_block.pack(fill="x", pady=(16, 0),
                                     before=self.compliance_note)
        self.quartile_chart.set_rows(equity["quartiles"])
        unknown = equity.get("unknown_count", 0)
        publication = (
            "Indicateurs publiables au titre de la directive 2023/970 : "
            f"écart médian {_signed_percent(pay.get('median_gap'))}, "
            "écart moyen sur la rémunération variable "
            f"{_signed_percent(variable.get('mean_gap'))}, part percevant "
            f"une rémunération variable {format_percent(coverage.get('female_share'))} "
            f"des femmes et {format_percent(coverage.get('male_share'))} des "
            "hommes.")
        if unknown:
            publication += (f" {unknown} salarié(s) dont le sexe n'est pas "
                            "renseigné sont exclus de tous les écarts.")
        self.compliance_note.configure(text=publication)
        self._show_categories()

    def _decomposition_note(self, equity: Dict[str, Any],
                            block: Optional[Dict[str, Any]]) -> str:
        """Ce qu'il faut savoir pour lire les trois chiffres du bandeau."""
        note = ("Un écart positif signifie que les femmes sont moins "
                "rémunérées. Écart global : (moyenne des hommes − moyenne "
                "des femmes) / moyenne des hommes, formule de la directive "
                "2023/970.")
        if not block or block.get("comparable_gap") is None:
            return note + (" L'écart à poste comparable n'a pas pu être "
                           "calculé : aucun poste ne réunit assez de femmes "
                           "et d'hommes.")
        label = (block.get("category_label") or "poste").lower()
        return note + (
            f" À {label} comparable : moyenne des écarts de chaque {label}, "
            "pondérée par leur effectif, sur les "
            f"{format_percent(block.get('comparable_coverage'))} de "
            "l'effectif où les deux sexes atteignent le seuil de "
            f"publication. Effet de structure : le reste — ce que le {label} "
            "occupé explique de l'écart global, et non la rémunération à "
            f"{label} égal. Rattrapage : coût de l'alignement du sexe le "
            "moins rémunéré sur l'autre, poste par poste.")

    def _category_block(self) -> Optional[Dict[str, Any]]:
        """Ecarts sur l'axe choisi, recalcules pour la population filtree."""
        index = self.category_choice.current()
        if self.result is None or index < 0:
            return None
        return calculate_category_gaps(self.result.filtered,
                                       self.result.config,
                                       self._category_fields[index])

    def _show_categories(self) -> None:
        """Le coeur de la page : un poste, deux sexes, un ecart, un cout."""
        block = self._category_block()
        if block is None:
            return
        self._decomposed = block
        label = block.get("category_label") or "poste"
        self.category_heading.configure(text=f"Écart par {label.lower()}")
        self.category_tree.heading("#1", text=label)
        threshold = self.result.payload["pay_equity"]["threshold"]
        currency = self.result.payload["salary"].get("currency", "EUR")

        warning = block.get("category_warning")
        if warning:
            self.category_title.configure(text=warning)
            self._fill(self.category_tree, [])
            # Le titre porte deja l'explication : un graphique vide qui la
            # repeterait mot pour mot ferait doublon.
            if self.gap_chart.winfo_manager():
                self.gap_chart.pack_forget()
            self.gap_chart.set_rows([])
            return

        categories = block["categories"]
        above = block.get("categories_above_threshold", 0)
        masked = sum(1 for item in categories if not item.get("published"))
        titre = (f"· {above} {label.upper()}(S) SUR {len(categories)} "
                 f"AU-DELÀ DE {format_percent(threshold)}")
        if masked:
            # Un poste masque n'est pas un poste sans ecart : le dire evite
            # de lire le tableau comme un solde de tout compte.
            titre += (f" · {masked} MASQUÉ(S), EFFECTIF INSUFFISANT POUR "
                      "PUBLIER")
        self.category_title.configure(text=titre)

        ordered = self._ordered_categories(categories)
        rows = []
        for item in ordered:
            if not item["published"]:
                rows.append((item["category"], item["female_count"],
                             item["male_count"], "masqué", "masqué",
                             "masqué", "—"))
                continue
            rows.append((item["category"], item["female_count"],
                         item["male_count"],
                         format_money(item.get("female_median"), currency),
                         format_money(item.get("male_median"), currency),
                         _signed_percent(item.get("mean_gap")),
                         format_money(item.get("at_stake"), currency)))
        self._fill(self.category_tree, rows,
                   flagged=lambda position: ordered[position]["above_threshold"])
        # Le graphique lit la meme liste, dans le meme ordre : une barre et
        # une ligne qui ne se suivent pas se lisent comme deux resultats.
        if not self.gap_chart.winfo_manager():
            # « category_tree.master » n'est jamais depaquete : c'est un
            # repere sur pour rendre le graphique a sa place.
            self.gap_chart.pack(fill="x", padx=18, pady=(0, 4),
                                before=self.category_tree.master)
        self.gap_chart.set_rows(ordered, threshold)

    def _ordered_categories(self, categories):
        """Classe les postes selon le tri demande.

        Les postes masques restent en fin de liste quel que soit le tri :
        leur place dans un classement par ecart serait arbitraire, puisque
        l'ecart n'est precisement pas connu.
        """
        key = CATEGORY_ORDERS[max(self.category_order.current(), 0)][0]
        rangs = {
            "stake": lambda item: -(item.get("at_stake") or 0.0),
            "gap": lambda item: -abs(item.get("mean_gap") or 0.0),
            "headcount": lambda item: -(item["female_count"]
                                        + item["male_count"]),
            "name": lambda item: str(item["category"]).lower(),
        }
        return sorted(categories,
                      key=lambda item: (not item.get("published"),
                                        rangs[key](item)))

    def _show_scatter(self, dataset: Dict[str, Any], currency: str) -> None:
        fields = dimension_fields(self.configuration)
        self._colour_fields = fields
        self.colour_choice.configure(
            values=[dimension_label(self.configuration, f) for f in fields])
        current = dataset.get("color_field")
        if current in fields:
            self.colour_choice.current(fields.index(current))
        elif fields:
            self.colour_choice.current(0)
        self.scatter.set_dataset(dataset, currency)
        self._build_legend()

    def _recolour(self) -> None:
        """Recalcule le nuage avec une autre dimension de couleur.

        Le regroupement est refait par le moteur, pas par l'interface : les
        couleurs de l'ecran et celles du document restent identiques.
        """
        if not self.result:
            return
        index = self.colour_choice.current()
        if index < 0:
            return
        data = self.configuration.as_dict()
        data["chart_parameters"]["scatter_color_by"] = self._colour_fields[index]
        dataset = metrics.scatter_dataset(self.result.filtered, Configuration(data))
        self.scatter.set_dataset(
            dataset, self.result.payload["salary"].get("currency", "EUR"))
        self._build_legend()

    def _build_legend(self) -> None:
        for child in self.legend_frame.winfo_children():
            child.destroy()
        groups = self.scatter.dataset.get("groups") or []
        if not groups or len(groups) > 16:
            return
        tk.Label(self.legend_frame, text="MASQUER", background=theme.CANVAS,
                 foreground=theme.FAINT, font=self.fonts.label).pack(side="left",
                                                               padx=(0, 10))
        for index, group in enumerate(groups):
            # Meme serie que le nuage, prise au theme actif : la pastille de
            # la legende doit etre exactement la couleur du point.
            colour = theme.ACTIVE.series_for(index)
            chip = tk.Frame(self.legend_frame, background=theme.CANVAS, cursor="hand2")
            chip.pack(side="left", padx=(0, 14))
            dot = tk.Canvas(chip, width=9, height=9, background=theme.CANVAS,
                            highlightthickness=0)
            dot.create_oval(1, 1, 8, 8, fill=colour, outline="")
            dot.pack(side="left", pady=(1, 0))
            text = tk.Label(chip, text=group, background=theme.CANVAS, foreground=theme.INK_SOFT,
                            font=self.fonts.small)
            text.pack(side="left", padx=(5, 0))
            for widget in (chip, dot, text):
                widget.bind("<Button-1>", lambda _e, g=group, t=text, d=dot:
                            self._toggle_group(g, t, d))

    def _toggle_group(self, group: str, text: tk.Label, dot: tk.Canvas) -> None:
        self.scatter.toggle_group(group)
        masked = group in self.scatter.hidden
        text.configure(foreground=theme.FAINT if masked else theme.INK_SOFT)
        dot.configure(state="disabled" if masked else "normal")

    # ------------------------------------------------------------ identites

    def _index_identities(self) -> None:
        """Table numero de ligne -> identite, tenue par l'ecran seul.

        Identifier un salarie est le geste meme de l'analyse : un point a
        trente pour cent sous la mediane ne veut rien dire tant qu'on ne
        sait pas de qui il s'agit. Le paragraphe 6 exige des identifiants
        *anonymisables*, pas anonymises — le reglage existe, et il ne porte
        que sur l'ecran.

        L'index est construit ici, depuis la population que la fenetre
        detient deja, et non transporte par le resultat d'analyse : c'est ce
        qui garantit qu'aucun document produit, aucun export et aucun
        journal ne peut porter un nom, quel que soit le reglage.
        """
        self._identities = {}
        if not self.result:
            return
        if not self.configuration.get(
                "privacy_parameters.show_identities_on_screen", True):
            return
        for employee in self.result.filtered:
            identity = employee.identity
            if identity:
                self._identities[employee.row_number] = identity

    def _identity_of(self, row: Optional[int]) -> str:
        return self._identities.get(row, "") if row is not None else ""

    def _on_point_selected(self, point: Optional[Dict[str, Any]]) -> None:
        if not point:
            self.selection_label.configure(text="")
            return
        currency = self.result.payload["salary"].get("currency", "EUR")
        label = (self._identity_of(point.get("row"))
                 or str(point.get("reference", "")))
        self.selection_label.configure(
            text=f'{label} · {point["group"]} · '
                 f'{format_years(point["x"])} · '
                 f'{format_money(point["y"], currency)}')

    def _show_segments(self, segments: List[Dict[str, Any]]) -> None:
        """Range les blocs de segments : la dispersion et le tableau de bord
        y puisent tous deux leurs dimensions."""
        self._segments = segments or []
        labels = [segment["label"] for segment in self._segments]
        self.box_choice.configure(values=labels)
        if labels:
            self.box_choice.current(0)
            self._show_boxes()
        else:
            self.boxplot.set_rows([])

    def _show_boxes(self) -> None:
        """Boites a moustaches de la dimension choisie.

        Elles lisent le meme bloc que l'onglet Segments : les percentiles par
        segment sont deja calcules, et un chiffre affiche a deux endroits
        doit venir du meme calcul.
        """
        index = self.box_choice.current()
        if index < 0 or index >= len(self._segments):
            self.boxplot.set_rows([])
            return
        block = self._segments[index]
        currency = block.get("currency", "EUR")
        # La mediane d'ensemble n'est pas repetee en tete : le graphique la
        # trace, et un repere dessine se lit mieux qu'un montant a comparer
        # de tete avec seize boites.
        self.boxplot.set_rows(block["rows"], currency,
                              reference=block.get("reference_median"))

    # -------------------------------------------------------------- export

    def export_documents(self) -> None:
        if not self.result:
            return
        directory = filedialog.askdirectory(title="Où enregistrer les documents ?")
        if not directory:
            return
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        payload = self.result.payload
        produced: List[str] = []
        try:
            if self.output_vars["rapport"].get():
                produced.append(write_report(
                    payload, os.path.join(directory, f"restitution-{stamp}.html")))
            if self.output_vars["synthese"].get():
                summary = build_summary(payload)
                produced.append(write_slides_html(
                    summary, payload,
                    os.path.join(directory, f"synthese-{stamp}.html")))
                produced.append(write_slides_pdf(
                    summary, payload,
                    os.path.join(directory, f"synthese-{stamp}.pdf")))
            if self.output_vars["slides"].get():
                deck = build_deck(payload)
                produced.append(write_slides_html(
                    deck, payload, os.path.join(directory, f"slides-{stamp}.html")))
                produced.append(write_slides_pdf(
                    deck, payload, os.path.join(directory, f"slides-{stamp}.pdf")))
            if self.output_vars["excel"].get():
                produced.append(export_excel(
                    payload, self.result.filtered, self.result.config,
                    os.path.join(directory, f"analyse-{stamp}.xlsx")))
            produced.append(write_manifest(
                payload["manifest"],
                os.path.join(directory, f"manifeste-{stamp}.json")))
        except OSError as error:
            messagebox.showerror(
                "Enregistrement impossible",
                "Les documents n'ont pas pu être écrits dans ce dossier. "
                "Vérifiez que vous avez le droit d'y écrire.\n\n"
                f"Détail technique : {error}")
            return
        self._set_state(f"{len(produced)} fichiers écrits dans {directory}")
        messagebox.showinfo(
            "Documents produits",
            f"{len(produced)} fichiers ont été écrits dans :\n{directory}")


def main(config_dir: Optional[str] = None) -> int:
    """Ouvre l'interface. Retourne un code de sortie."""
    Application(config_dir).mainloop()
    return 0
