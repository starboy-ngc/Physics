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

import collections
import datetime as _dt
import logging
import os
import queue
import sys
import threading
import time as _time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from ..version import ENGINE_NAME, __version__
from ..core import metrics, org as org_view, palette
from ..core.config import (Configuration, default_config_dir,
                           load_configuration)
from ..core.errors import CompensationError, ConfigError
from ..core.export import export_excel
from ..core.glossary import describe as define
from ..core.logging_setup import log_event
from ..core.pay_equity import (calculate_category_gaps, category_breakdown,
                               category_members, people_rows,
                               population_breakdown)
from ..core.pipeline import (AnalysisRequest, load_population, run_analysis,
                             stage_labels)
from ..core.quality import run_quality_check
from ..core.reporting import (format_money, format_number, format_percent,
                              format_years,
                              write_report)
from ..core.segmentation import (build_filters, dimension_fields,
                                 dimension_label, max_filter_values)
from ..core.slides import (build_deck, build_summary, write_slides_html,
                           write_slides_pdf)
from . import logo as marque
from . import theme
from .charts import (BandChart, BoxPlotChart, HistogramChart, OrgChart,
                     PieChart, PyramidChart, ScaleChart, ScatterChart,
                     VerticalBoxPlotChart)
from .progress import LoadingBar
from .working import WorkPanel
from . import splash as accueil_module
from .theme import Card, CheckRow, Fonts, TabBar, ValuePicker

WINDOW_TITLE = f"{ENGINE_NAME} {__version__}"
#: Les parentheses distinguent l'absence de choix d'une valeur qui, elle,
#: existerait vraiment dans le fichier.
_WHOLE_FILE = "(tout le périmètre)"

#: Les resultats d'abord, le controle qualite en dernier : on y revient
#: quand un chiffre surprend, on ne commence pas par lui.
TABS = (("population", "Vue d'ensemble"), ("organigramme", "Organigramme"),
        ("graphique", "Graphiques"),
        ("equite", "Écarts F/H"),
        ("qualite", "Qualité"))

#: Onglets qui ne paraissent que si l'on a demande ce qu'ils montrent, et
#: non parce que l'effectif le permet. Les retirer ne s'explique pas : il n'y
#: a rien a expliquer tant que personne n'a choisi d'equipe, et un message
#: « effectif insuffisant » serait faux.
ON_DEMAND = ("organigramme",)

#: Graphiques proposes dans l'onglet « Graphique », dans l'ordre d'affichage.
#: Les onglets de premier rang repondent a une question — qui, combien, quel
#: ecart — la ou ceux-ci repondaient tous les deux a « a quoi cela
#: ressemble-t-il ». Les reunir laisse la place d'en ajouter d'autres sans
#: allonger la barre principale : une entree de plus ici suffit.
#: Tris du tableau des postes. L'enjeu vient en premier : c'est la question
#: qui suit l'ecart — combien pour le refermer, et ou en priorite. Trier par
#: ampleur d'ecart seul met en tete des postes de quatre personnes.
#: Entree « pas de croisement » de la seconde liste.

#: Premiere entree du choix de poste : elle ouvre la vue d'ensemble plutot
#: qu'une fiche. Sans elle, on ne pourrait plus revenir a la question
#: « ou faut-il regarder ? » une fois un poste ouvert.

#: Les ordres de lecture de la vue d'ensemble. « Significativite » vient en
#: premier parce que c'est la question posee : quels postes s'ecartent
#: au-dela de ce que le hasard explique. Classer par ampleur seule met en
#: tete les postes les moins peuples, ou un grand ecart est le plus facile.

#: Les lectures de la page des ecarts, dans l'ordre ou l'on s'en sert : ou
#: regarder, ce qui s'y passe, comment les deux sexes s'y repartissent,
#: comment leurs remunerations s'etalent, et la repartition par quartile que
#: la directive fait publier.

CHARTS = (("nuage", "Nuage de points"),
          ("distribution", "Distribution"),
          ("boites", "Dispersion"),
          ("colonnes", "Boîtes à moustaches"))


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
        # Sans decimale, comme toutes les parts de la vue d'ensemble : un
        # coefficient de variation a 31,9 % affiche une precision que la
        # lecture n'emploie pas.
        ("Coefficient de variation",
         format_percent(None if variation is None else variation * 100,
                        digits=0),
         "coefficient_of_variation"),
    ]


class Application(tk.Tk):
    """Fenetre unique de l'outil."""

    #: Duree minimale d'affichage de l'ecran d'accueil, si la
    #: configuration n'en dit rien. La construction de la fenetre est trop
    #: rapide pour qu'on ait le temps de lire quoi que ce soit : ce temps-la
    #: est assume, et se regle a zero.
    SPLASH_SECONDS = 3.0

    def __init__(self, config_dir: Optional[str] = None,
                 splash: bool = False) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self._pose_icone()
        self.geometry("1380x880")
        self.minsize(1120, 720)
        # Retiree de l'ecran le temps de la construction : une fenetre qui
        # se remplit widget par widget sous les yeux de l'utilisateur fait
        # plus desordre que d'attendre.
        self.withdraw()

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

        # L'ecran d'accueil appartient au lancement, pas a la fenetre :
        # « main » le demande, un test qui construit la fenetre pour lire un
        # widget ne l'attend pas une seconde et demie.
        #: Instant d'ouverture de l'ecran d'accueil.
        self._splash_started = 0.0
        self._splash = self._open_splash() if splash else None
        #: Ce qui annonce l'avancement du demarrage. Sans ecran d'accueil,
        #: il n'annonce a personne — le reste du code n'a pas a le savoir.
        self._startup = (self._splash.announce if self._splash
                         else lambda _label, _part: None)
        self._startup("Paramètres et thème", 0.18)

        self.source_path: Optional[str] = None
        self.population = None
        self.mapping = None
        self.headers: List[str] = []
        self.result = None
        #: Par dimension, les valeurs retenues — None pour « toutes ».
        #: Un filtre retient plusieurs valeurs : la question posee a un
        #: fichier de paie est rarement « ce poste-ci », c'est « ces
        #: trois postes-la ».
        self.filter_values: Dict[str, Optional[List[str]]] = {}
        #: Les valeurs que chaque dimension porte, et le bouton qui les
        #: ouvre. Separes de la selection pour que le libelle puisse dire
        #: « 3 sur 24 » sans recompter le fichier.
        self._filter_choices: Dict[str, List[str]] = {}
        self._filter_buttons: Dict[str, ttk.Button] = {}
        self.filter_labels: Dict[str, str] = {}
        self.output_vars: Dict[str, tk.BooleanVar] = {}
        self._segments: List[Dict[str, Any]] = []
        # Numero de ligne -> identite. Vide tant qu'aucune analyse n'a
        # tourne, et vide aussi si le reglage d'ecran l'interdit.
        self._identities: Dict[int, str] = {}
        #: Libelle affiche -> matricule du responsable, pour la liste des
        #: equipes. Vide tant qu'aucun fichier n'est charge.
        self._team_keys: Dict[str, str] = {}
        #: Matricule -> ligne de « team_rows », pour dire sous la liste ce
        #: que vaut l'equipe choisie.
        self._team_rows: Dict[str, Dict[str, Any]] = {}
        self._team_anomalies: List[str] = []
        #: Periodes presentes dans le fichier charge.
        self._periods: List[str] = []
        self._colour_fields: List[str] = []
        self._queue: queue.Queue = queue.Queue()
        #: Tranche d'execution d'un fil telle qu'elle etait avant l'analyse.
        #: Retenue des la construction : un releve de file peut survenir
        #: sans qu'aucune analyse n'ait ete lancee.
        self._switch_interval = sys.getswitchinterval()
        #: Releve de file en attente, pour l'annuler a la fermeture : une
        #: fenetre fermee pendant une analyse laissait Tk executer un
        #: rappel dont le widget n'existait plus.
        self._poll_job: Optional[str] = None
        #: Apparition differee du panneau d'attente, annulable de meme.
        self._work_job: Optional[str] = None

        self._build_layout()
        # Un vrai redimensionnement de la fenetre efface la memoire des
        # accords deja faits : sans cela, revenir a une taille deja visitee
        # rendait la page telle qu'elle etait a l'autre taille.
        self.bind("<Configure>", self._on_window_resize, add="+")
        # La composition enregistree est relue avant le premier affichage :
        # c'est la promesse du bouton « Enregistrer », et elle ne tient que
        # si la page survit a la fermeture.
        self._set_state("Choisissez un fichier de population pour commencer.")
        self._startup("Prêt", 1.0)
        self._close_splash()
        self.deiconify()

    # ------------------------------------------------------------ accueil

    def _splash_seconds(self) -> float:
        """Duree de l'ecran d'accueil, lue sans jamais empecher l'ouverture.

        Ailleurs un parametre illisible arrete l'analyse, et c'est voulu :
        un seuil faux fausse un resultat. Ici non. Une duree d'accueil est
        cosmetique, et refuser d'ouvrir la fenetre parce qu'un fichier de
        theme porte un texte a la place d'un nombre couterait plus a
        l'utilisateur que le defaut ne lui coute.
        """
        try:
            return self.configuration.number(
                "theme_parameters.splash_seconds", self.SPLASH_SECONDS,
                minimum=0.0, maximum=60.0)
        except ConfigError:
            return float(self.SPLASH_SECONDS)

    def _open_splash(self):
        """Ouvre l'ecran d'accueil, sauf si la configuration l'a mis a zero."""
        if self._splash_seconds() <= 0:
            return None
        # L'horloge part de l'ouverture de l'ecran, non de la fin de la
        # construction : les trois secondes demandees sont celles que
        # l'utilisateur attend, pas celles qui s'y ajoutent.
        self._splash_started = _time.perf_counter()
        return accueil_module.show(self, self.fonts)

    def _close_splash(self) -> None:
        """Laisse l'ecran le temps d'etre vu, puis le retire.

        La boucle est ici, avant « mainloop », et c'est voulu : le demarrage
        est lineaire, et un enchainement de rappels pour attendre une
        seconde et demie serait plus difficile a suivre qu'a ecrire.
        """
        ecran = self._splash
        self._splash = None
        if ecran is None:
            return
        limite = self._splash_started + self._splash_seconds()
        while _time.perf_counter() < limite and not ecran.skipped:
            ecran.tick()
            self.update()
            _time.sleep(0.008)
        ecran.close()

    # -------------------------------------------------------------- layout

    #: Tailles de l'icone de fenetre. Windows prend la premiere pour la
    #: barre des taches et la seconde pour le coin du titre ; les autres
    #: systemes choisissent. Deux suffisent : au-dela, chaque taille coute
    #: son dessin au demarrage.
    ICONE_TAILLES = (32, 16)

    def _pose_icone(self) -> None:
        """Pose la marque sur la fenetre et dans la barre des taches.

        Sans elle, la fenetre porte l'icone du programme qui l'a ouverte —
        sous Windows, celle de l'interpreteur, puisque le lanceur demarre
        « pythonw.exe ». L'utilisateur voit alors une icone qui n'est pas
        celle de l'outil, et qu'aucune reprise de la marque ne change.

        C'est le jeton, pas la marque nue : une barre des taches a son
        propre fond, clair ou sombre selon le theme du poste.

        Un echec ici ne doit pas empecher l'outil de s'ouvrir : une icone
        est un confort, pas une fonction. Certains gestionnaires de
        fenetres refusent « iconphoto », et aucun ne le dit a l'avance.
        """
        try:
            self._icones = [tk.PhotoImage(data=marque.jeton(taille))
                            for taille in self.ICONE_TAILLES]
            self.iconphoto(True, *self._icones)
        except tk.TclError:
            self._icones = []

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

        self._startup("Colonne de gauche", 0.42)
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
                               wraplength=1100)
        self.pages = tk.Frame(content.inner, background=theme.CANVAS)
        self.pages.pack(fill="both", expand=True)
        # Le panneau d'attente prend la place des pages le temps du calcul.
        # Les etapes qu'il annonce viennent du moteur : les recopier ici
        # aurait garanti qu'un jour elles different de ce qui est calcule.
        self.work_panel = WorkPanel(content.inner, self.fonts, stage_labels())
        self._startup("Pages et graphiques", 0.68)
        self._build_pages()
        # L'organigramme n'existe qu'une fois une equipe choisie : la barre
        # ne doit pas en porter l'entree avant la premiere analyse, sans
        # quoi on ouvre un onglet vide sans savoir ce qu'il attend.
        for key in ON_DEMAND:
            self.tabbar.set_visible(key, False)



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

    def readprofile(self, baseName: str, className: str) -> None:
        """Neutralise les « profils » de Tk. C'est une porte d'entree.

        A la creation de sa fenetre, Tk lit dans le repertoire personnel
        « .Tk.py », « .Tk.tcl » et leurs equivalents au nom du programme —
        et les *execute*, l'un comme code Python, l'autre comme code Tcl.
        Quiconque peut deposer un fichier dans le profil de l'utilisateur
        fait donc executer ce qu'il veut au demarrage de l'outil.

        CPython connait le defaut (issue 16248) et ne l'evite qu'avec le
        drapeau « -E » de l'interpreteur — inutilisable ici, l'outil se
        lancant d'un double-clic. La parade tient dans cette methode vide :
        « tkinter.Tk.__init__ » appelle celle de la classe, donc celle-ci.

        Verifie a l'execution : un « .Tk.py » depose dans un faux repertoire
        personnel s'executait avant, ne s'execute plus.
        """

    def destroy(self) -> None:
        """Ferme proprement : un releve de file encore en attente
        s'executerait apres la fenetre, et Tk se plaindrait d'une commande
        qui n'existe plus. Le fil de calcul, lui, est demon : il s'arrete
        avec le programme."""
        self._cancel_fold()
        # Deux rappels peuvent etre en attente : le releve de la file, et
        # l'apparition differee du panneau d'attente. Tous deux
        # s'executeraient apres la fenetre.
        for nom in ("_poll_job", "_work_job"):
            job = getattr(self, nom, None)
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
                setattr(self, nom, None)
        super().destroy()

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
        # Une barre dessinee et animee sur l'horloge, et non sur le nombre
        # d'images : pendant une analyse, le fil principal est preempte par
        # le calcul, et une barre qui avance d'un cran par image se fige
        # avec lui. Voir « ui/progress.py ».
        self.progress = LoadingBar(actions, ground=theme.GROUND)
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
        # Associer les colonnes se fait la ou l'on vient de charger le
        # fichier. Renvoye aux « Paramètres », ce geste n'etait pas
        # trouve : la colonne que l'outil ne reconnait pas est justement
        # celle sur laquelle on veut travailler.
        self.columns_button = ttk.Button(
            steps, text="Associer les colonnes…", style="GhostGround.TButton",
            command=self.open_settings)
        self.columns_button.pack(fill="x", pady=(8, 0))
        self.columns_button.state(["disabled"])

        # La periode precede les filtres : sur un fichier pluriannuel, elle
        # decide de quel instantane on parle, et tout le reste s'y applique.
        # Le bloc reste cache tant que le fichier n'en porte qu'une.
        self.period_block = tk.Frame(steps, background=theme.GROUND)
        self._section(self.period_block, 2, "Période")
        self.period_var = tk.StringVar()
        self.period_choice = ttk.Combobox(self.period_block, state="readonly",
                                          textvariable=self.period_var,
                                          font=self.fonts.small)
        self.period_choice.pack(fill="x")
        # L'organigramme de 2024 n'est pas celui de 2026 : la liste des
        # equipes se refait a chaque changement de periode.
        self.period_var.trace_add("write", lambda *_: self._populate_teams())
        tk.Label(self.period_block,
                 text="Une seule période à la fois : mélangées, les "
                      "rémunérations de trois années ne veulent rien dire.",
                 background=theme.GROUND, foreground=theme.FAINT,
                 font=self.fonts.small, wraplength=250,
                 justify="left").pack(anchor="w", pady=(4, 0))

        # L'equipe precede les filtres pour la meme raison que la periode :
        # elle designe la population, les filtres ne font que la restreindre.
        # Le bloc reste cache tant que le fichier ne porte pas de colonne
        # manager exploitable — la colonne n'est pas obligatoire.
        self.team_block = tk.Frame(steps, background=theme.GROUND)
        self._section(self.team_block, 3, "Équipe")
        self.team_var = tk.StringVar(value=_WHOLE_FILE)
        self.team_choice = ttk.Combobox(self.team_block, state="readonly",
                                        textvariable=self.team_var,
                                        font=self.fonts.small)
        self.team_choice.pack(fill="x")
        self.team_var.trace_add("write", lambda *_: self._update_team_note())
        self.team_direct_var = tk.BooleanVar(value=False)
        self.team_direct_var.trace_add(
            "write", lambda *_: self._update_team_note())
        CheckRow(self.team_block, "Équipe directe seulement",
                 self.team_direct_var, self.fonts).pack(anchor="w",
                                                        pady=(6, 0))
        self.team_note = tk.Label(
            self.team_block,
            text="Par défaut, l'équipe descend jusqu'au dernier niveau : "
                 "c'est celle dont un responsable répond.",
            background=theme.GROUND, foreground=theme.FAINT,
            font=self.fonts.small, wraplength=250, justify="left")
        self.team_note.pack(anchor="w", pady=(4, 0))

        self.reset_filters_link = self._section(
            steps, 4, "Filtrer", "Réinitialiser", self.reset_filters)
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

        self._section(steps, 5, "Restituer", "Tout / aucun",
                      self.toggle_outputs)
        self.outputs_frame = tk.Frame(steps, background=theme.GROUND)
        self.outputs_frame.pack(fill="x", pady=(0, 8))
        for key, label, default in (("rapport", "Rapport détaillé (HTML)", True),
                                    ("synthese", "Synthèse 1 page (PDF)", True),
                                    ("slides", "Vue détaillée (PDF)", True),
                                    ("excel", "Classeur Excel", True)):
            var = tk.BooleanVar(value=default)
            self.output_vars[key] = var
            CheckRow(self.outputs_frame, label, var,
                     self.fonts).pack(anchor="w", pady=2)

    def reset_filters(self) -> None:
        """Ramene tous les criteres a « aucun filtre »."""
        for field in self.filter_values:
            self.filter_values[field] = None
            self._refresh_filter_button(field)
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
        self._overview_window = window
        #: Nombre de colonnes avec lequel la page a ete composee.
        self._overview_columns: Optional[int] = None
        # « bbox("all") » commence au premier element, soit (18, 18) : la
        # zone de defilement demarrait donc apres la marge, qui disparaissait
        # des le premier affichage — le titre venait coller au filet des
        # onglets. On ancre la zone a l'origine, et on rend la marge du bas.
        self.overview_frame.bind(
            "<Configure>",
            lambda _e: self._scroll_region(overview))
        # La largeur disponible decide du nombre de colonnes. Elle n'est pas
        # connue au moment ou la page se compose — un onglet qui n'a jamais
        # ete affiche mesure un pixel de large —, et la page se figeait alors
        # a deux colonnes pour le reste de la session, meme en plein ecran.
        # On relaie donc chaque changement de largeur, et la page se
        # redispose si le compte de colonnes change.
        self.overview_canvas = overview
        overview.bind("<Configure>", self._on_overview_resize)
        # Premier onglet de la barre, donc premier ecran vu : il doit dire ce
        # qu'il attend. _show_overview vide ce cadre au premier calcul.
        tk.Label(self.overview_frame,
                 text="Aucune analyse.\nChoisissez une population dans la "
                      "colonne de gauche, puis « Analyser ».",
                 background=theme.CANVAS, foreground=theme.MUTED, font=self.fonts.body,
                 justify="left").pack(anchor="w", pady=(40, 0))
        self._build_org(self.tabs["organigramme"])
        self._build_charts(self.tabs["graphique"])

        distribution = self.chart_pages["distribution"]
        dist_head = tk.Frame(distribution, background=theme.CANVAS)
        dist_head.pack(fill="x", padx=18, pady=(10, 0))
        # L'ecart global dit de combien les deux sexes sont payes
        # differemment ; il ne dit pas ou. Deux distributions dos a dos le
        # disent : classes hautes desertees, ou entassement dans les basses.
        self.dist_split = tk.BooleanVar(value=False)
        self.dist_split_row = CheckRow(dist_head, "Séparer H/F",
                                       self.dist_split, self.fonts,
                                       ground=theme.CANVAS)
        self.dist_split_row.pack(side="left")
        # Quand le dedoublement est refuse, la place du bouton dit pourquoi :
        # un bouton absent sans explication passe pour un oubli.
        self.dist_split_note = tk.Label(dist_head, text="",
                                        background=theme.CANVAS,
                                        foreground=theme.MUTED,
                                        font=self.fonts.small)
        self.dist_split_note.pack(side="left")
        self.dist_split.trace_add("write", lambda *_: self._show_distribution())
        self.histogram = HistogramChart(distribution)
        self.histogram.pack(fill="both", expand=True, padx=18, pady=(6, 18))

        boites = self.chart_pages["boites"]
        box_head = tk.Frame(boites, background=theme.CANVAS)
        box_head.pack(fill="x", padx=18, pady=(10, 0))
        tk.Label(box_head, text="DIMENSION", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")
        self.box_choice = ttk.Combobox(box_head, state="readonly", width=24,
                                       font=self.fonts.small)
        self.box_choice.pack(side="left", padx=10)
        self.box_choice.bind("<<ComboboxSelected>>",
                             lambda _e: self._change_box_dimension())
        # Choisir la dimension ne suffit pas : trente-six etablissements
        # tiennent dans le graphique, mais la question est rarement
        # « tous » — c'est « ces quatre-la, cote a cote ».
        #: Valeurs retenues dans la dimension, ou None pour toutes.
        self.box_values = None
        self.box_values_button = ttk.Button(
            box_head, text="Valeurs : toutes", style="Ghost.TButton",
            command=self._choose_box_values)
        self.box_values_button.pack(side="left")
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
        self.box_order.bind("<<ComboboxSelected>>", lambda _e: self._reorder())
        # Deux medianes proches peuvent recouvrir deux distributions tres
        # differentes : une seule boite par segment ne dit pas si les deux
        # sexes s'y etalent pareil.
        self.box_split = tk.BooleanVar(value=False)
        CheckRow(box_head, "Distinguer femmes / hommes", self.box_split,
                 self.fonts, ground=theme.CANVAS).pack(side="left",
                                                       padx=(22, 0))
        self.box_split.trace_add("write", lambda *_: self._show_boxes())
        self.boxplot = BoxPlotChart(boites)
        self.boxplot.pack(fill="both", expand=True, padx=18, pady=(6, 10))

        # Les memes chiffres, dresses : la remuneration en ordonnee, les
        # categories cote a cote. La page couchee classe quarante postes et
        # porte leurs intitules sans les incliner ; celle-ci repond a
        # l'autre question — comment ces quelques categories se
        # comparent-elles —, et c'est pour cela qu'elle a sa propre page
        # plutot qu'une case a cocher sur la precedente.
        colonnes = self.chart_pages["colonnes"]
        col_head = tk.Frame(colonnes, background=theme.CANVAS)
        col_head.pack(fill="x", padx=18, pady=(10, 0))
        tk.Label(col_head, text="EN ABSCISSE", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")
        self.col_choice = ttk.Combobox(col_head, state="readonly", width=24,
                                       font=self.fonts.small)
        self.col_choice.pack(side="left", padx=10)
        self.col_choice.bind("<<ComboboxSelected>>",
                             lambda _e: self._change_col_dimension())
        # Quarante-huit metiers dresses cote a cote demandent de faire
        # defiler tout le graphique pour en comparer deux. La question est
        # rarement « tous » : c'est « ces quatre-la, cote a cote ».
        #: Valeurs retenues dans la dimension, ou None pour toutes.
        self.col_values = None
        self.col_values_button = ttk.Button(
            col_head, text="Valeurs : toutes", style="Ghost.TButton",
            command=self._choose_col_values)
        self.col_values_button.pack(side="left")
        tk.Label(col_head, text="TRIER PAR", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left", padx=(22, 0))
        self.col_order = ttk.Combobox(
            col_head, state="readonly", width=22, font=self.fonts.small,
            values=[label for _key, label in VerticalBoxPlotChart.ORDERS])
        self.col_order.current(0)
        self.col_order.pack(side="left", padx=10)
        self.col_order.bind("<<ComboboxSelected>>",
                            lambda _e: self._reorder_columns())
        self.column_boxes = VerticalBoxPlotChart(colonnes)
        self.column_boxes.pack(fill="both", expand=True, padx=18, pady=(6, 10))

        nuage = self.chart_pages["nuage"]
        controls = tk.Frame(nuage, background=theme.CANVAS)
        controls.pack(fill="x", padx=18, pady=(8, 4))
        # Les deux axes se choisissent : le nuage n'est plus « remuneration
        # x anciennete » mais un nuage, et c'est a l'utilisateur de dire ce
        # qu'il compare — l'age et le salaire, la part variable et l'ETP,
        # une prime maison et l'anciennete.
        self.x_choice = self._axis_box(controls, "EN ABSCISSE")
        self.y_choice = self._axis_box(controls, "EN ORDONNÉE")
        tk.Label(controls, text="COLORER PAR", background=theme.CANVAS, foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left", padx=(16, 0))
        self.colour_choice = ttk.Combobox(controls, state="readonly", width=18,
                                          font=self.fonts.small)
        self.colour_choice.pack(side="left", padx=10)
        self.colour_choice.bind("<<ComboboxSelected>>", lambda _e: self._recolour())
        # « Le cadrage » ne disait qu'une partie : les deux axes et la
        # couleur se changent aussi, et il faut pouvoir revenir au nuage
        # d'origine sans se souvenir de ce qu'il portait.
        ttk.Button(controls, text="Réinitialiser le graphique",
                   style="Ghost.TButton",
                   command=self._reset_scatter).pack(side="left")
        self.selection_label = tk.Label(controls, text="", background=theme.CANVAS,
                                        foreground=theme.INK, font=self.fonts.small)
        self.selection_label.pack(side="right")

        self.scatter = ScatterChart(nuage, on_select=self._on_point_selected)
        self.scatter.identify = self._identity_of
        self.scatter.pack(fill="both", expand=True, padx=18, pady=(4, 4))
        self.legend_frame = tk.Frame(nuage, background=theme.CANVAS)
        self.legend_frame.pack(fill="x", padx=18, pady=(0, 14))
        self.legend_frame.bind("<Configure>", self._on_legend_resize)

        self._build_equity(self.tabs["equite"])




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

    def _build_org(self, parent: tk.Frame) -> None:
        """L'equipe choisie, de la vue d'ensemble au dessin.

        Trois lectures d'une meme population, du general au particulier, et
        aucune ne se suffit.

        L'equipe **par poste** vient en premier : devant cinquante
        personnes, la question n'est pas « qui gagne combien » mais « quels
        postes la composent, combien chacun, dans quelle fourchette ». Un
        poste du simple au double n'appelle pas la meme conversation qu'un
        poste resserre, et aucune moyenne ne le dirait.

        La liste **nominative** ensuite : c'est celle qu'on lit pour
        preparer un entretien, et le rang de remuneration y repond a la
        question qui suit un montant — « ou se situe-t-elle dans l'equipe ».

        Le **dessin** en dernier : la structure, compacte. Il repond a « qui
        depend de qui », ce qu'aucun tableau ne montre.

        La page defile d'un bloc. Le dessin, lui, prend la hauteur qu'il
        lui faut et ne garde que son ascenseur horizontal — c'est la
        dimension par laquelle un organigramme deborde. Deux zones
        defilantes verticales imbriquees rendraient la molette
        imprevisible : on ferait defiler l'une en croyant bouger l'autre.
        """
        parent = self._scrolling_page(parent)
        self.org_frame = tk.Frame(parent, background=theme.CANVAS)
        self.org_frame.pack(fill="x", padx=24, pady=(16, 0))
        self.org_note = tk.Label(parent, text="", background=theme.CANVAS,
                                 foreground=theme.MUTED,
                                 font=self.fonts.small, justify="left",
                                 anchor="w", wraplength=1100)
        self.org_note.pack(anchor="w", padx=24, pady=(0, 10))

        self._org_title(parent, "L'ÉQUIPE PAR POSTE")
        self.org_jobs = self._tree(
            parent,
            ("Poste", "Niveau", "Effectif", "Minimum", "Médiane", "Moyenne",
             "Maximum"),
            (300, 70, 80, 120, 120, 120, 120),
            expand=False, height=5)

        self._org_title(parent, "LES SALARIÉS")
        self.org_tree = self._tree(
            parent,
            ("Salarié", "Poste", "Niveau", "Rattaché à", "Âge", "Ancienneté",
             "Rémunération", "Rang"),
            (230, 190, 70, 190, 80, 100, 130, 90),
            expand=False, height=8)
        self.org_tree.bind("<<TreeviewSelect>>", self._on_org_row)

        self._org_title(parent, "ORGANIGRAMME")
        self.org_chart = OrgChart(parent, on_select=self._on_org_node,
                                  grows=True)
        self.org_chart.identify = self._identity
        self.org_chart.pack(fill="x", padx=18, pady=(0, 10))
        #: Matricules par ligne du tableau — le salarie, et la case qui le
        #: porte — pour relier les deux lectures sans faire entrer un
        #: matricule dans le libelle affiche.
        self._org_keys: Dict[str, tuple] = {}

    def _org_title(self, parent: tk.Frame, text: str) -> None:
        """Un intertitre, precede de son filet.

        Trois blocs empiles sans rien entre eux se lisent comme un seul long
        tableau : le filet porte la structure de la page a lui seul.
        """
        tk.Frame(parent, background=theme.LINE, height=1).pack(
            fill="x", padx=24, pady=(0, 8))
        tk.Label(parent, text=text, background=theme.CANVAS,
                 foreground=theme.FAINT, font=self.fonts.label).pack(
            anchor="w", padx=24, pady=(0, 6))

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
              height: Optional[int] = None, anchors=None) -> ttk.Treeview:
        wrapper = tk.Frame(parent, background=theme.CANVAS)
        wrapper.pack(fill="both" if expand else "x", expand=expand,
                     padx=18, pady=(0, 18 if expand else 10))
        options = {"height": height} if height else {}
        tree = ttk.Treeview(wrapper, columns=columns, show="headings", **options)
        # La hauteur demandee devient un plafond, non une taille : un
        # tableau d'une ligne gardait douze lignes de blanc sous elle, et la
        # page s'etirait autour d'un vide. `_fill` la ramene a son contenu.
        tree.plafond = height or 0
        for rang, (name, width) in enumerate(zip(columns, widths)):
            # L'en-tete suit l'alignement de sa colonne. Centre par defaut,
            # il flottait au-dessus de valeurs calees a gauche ou a droite,
            # et l'oeil ne retrouvait plus quelle colonne il coiffait.
            #
            # La largeur sert de regle par defaut — un libelle long tient a
            # gauche, un nombre se cale a droite — mais une colonne peut
            # imposer la sienne : « Nom » est un mot, meme court.
            alignement = ("w" if width > 200 else "e") if anchors is None \
                else anchors[rang]
            tree.heading(name, text=name.upper(), anchor=alignement)
            tree.column(name, width=width, anchor=alignement)
        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview,
                               style="Flat.Vertical.TScrollbar")
        tree.pack(side="left", fill="both", expand=True)
        theme.attach_scrollbar(tree, scroll, side="right", fill="y",
                               pady=(30, 0), before=tree)
        return tree

    # ------------------------------------------------------- etapes

    def report_callback_exception(self, genre, valeur, trace) -> None:
        """Montre ce qu'une erreur imprevue faisait disparaitre.

        Tk confie les erreurs de rappel a cette methode, dont la version
        d'origine les ecrit sur la sortie d'erreur. L'outil tourne sous
        « pythonw.exe », qui n'en a pas : une exception dans un bouton
        n'allait donc nulle part. On cliquait « Enregistrer », rien ne se
        passait, et aucune trace ne disait pourquoi — l'ecran avait l'air
        de ne pas enregistrer.

        Le message ne porte ni valeur ni libelle venu du fichier : le
        paragraphe 6 interdit la moindre donnee RH dans un message
        technique, et le texte d'une exception levee au milieu du
        traitement en contient volontiers une. Le type et la ligne
        suffisent a situer la panne, et ne disent rien de personne.
        """
        import traceback

        cadres = traceback.extract_tb(trace)
        paquet = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Le code de l'outil d'abord : c'est lui qu'on corrigera. A defaut
        # — une erreur levee avant d'y entrer — le cadre le plus profond,
        # quel qu'il soit : un repere vide ne sert personne.
        choisi = next((cadre for cadre in reversed(cadres)
                       if os.path.abspath(cadre.filename).startswith(paquet)),
                      cadres[-1] if cadres else None)
        ou = (f"{os.path.basename(choisi.filename)}:{choisi.lineno}"
              if choisi is not None else "-")
        technique = f"{genre.__name__} at {ou}"
        log_event("interface", "rappel", status="ERREUR", detail=technique,
                  level=logging.ERROR)
        messagebox.showerror(
            "HR Analytics",
            "Une erreur imprévue a interrompu l'action en cours. Rien n'a "
            "été perdu : reprenez-la, et si elle se répète, signalez le "
            "repère ci-dessous.\n\n"
            f"{technique}")

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
            self._offrir_association(error)
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
                 + (f", {unknown} non reconnue(s) — associez-les ci-dessous"
                    if unknown else ""),
            foreground=theme.WARN if unknown else theme.MUTED)
        self.columns_button.state(["!disabled"])
        # Quelques lignes du fichier, pour l'ecran d'association : voir ce
        # que porte une colonne vaut mieux que lire son intitule.
        self._samples = [list(ligne) for ligne in table.rows[:40]]
        self._populate_filters()
        self.analyse_button.state(["!disabled"])
        self.export_button.state(["disabled"])
        self._show_quality()
        self.tabbar.select("qualite")
        self._set_state("Fichier chargé. Vérifiez la qualité, puis lancez l'analyse.")

    def _offrir_association(self, error: CompensationError) -> None:
        """Ouvre l'ecran d'association quand c'est lui qui debloque.

        Un fichier dont la colonne de salaire porte un autre intitule etait
        refuse, et le bouton « Associer les colonnes… » restait grise : il
        ne s'active qu'une fois un fichier charge, et justement ce
        fichier-la ne l'etait pas. Le message renvoyait aux parametres, ou
        l'ecran d'association ne connaissait aucune des colonnes du fichier
        — il fallait les retaper a la main, apres les avoir relevees dans
        Excel.

        Le fichier a pourtant bien ete lu : ce sont ses colonnes qu'on n'a
        pas su nommer. Le refus les emporte donc avec lui, et l'ecran
        s'ouvre sur celles-la, avec quelques lignes pour voir ce que chacune
        contient.

        Seulement dans ce cas : un fichier illisible ou vide n'a aucune
        colonne a associer, et ouvrir l'ecran n'y servirait a rien.
        """
        entetes = getattr(error, "headers", None)
        if not entetes:
            return
        self.headers = list(entetes)
        self._samples = [list(ligne) for ligne in getattr(error, "samples", [])]
        self.columns_button.state(["!disabled"])
        self._set_state("Associez la colonne manquante, puis rouvrez le "
                        "fichier.")
        self.open_settings()

    def open_settings(self) -> None:
        """Parametrage des champs : colonnes, filtres, axes d'analyse."""
        from .settings import SettingsWindow

        SettingsWindow(self, self.configuration, self.config_dir, self.fonts,
                       headers=getattr(self, "headers", None),
                       on_saved=self._settings_saved,
                       samples=getattr(self, "_samples", None))

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
                self._samples = [list(ligne) for ligne in table.rows[:40]]
                # Le compte des colonnes suit ce qui vient d'etre associe :
                # laisser « 3 non reconnues » apres les avoir associees
                # ferait douter de l'enregistrement.
                inconnues = len(mapping.unknown_columns)
                self.mapping_label.configure(
                    text=f"{len(mapping.field_to_index)} colonnes reconnues"
                         + (f", {inconnues} non reconnue(s) — associez-les "
                            "ci-dessous" if inconnues else ""),
                    foreground=theme.WARN if inconnues else theme.MUTED)
        except CompensationError as error:
            # Les fichiers sont ecrits : le dire, sinon l'echec de la
            # relecture passe pour un echec de l'enregistrement, et on
            # recommence une saisie qui est deja sur le disque.
            self._set_state(f"Paramètres enregistrés dans {path}.")
            messagebox.showerror(
                "Paramètres",
                "Les paramètres sont enregistrés, mais le fichier n'a pas "
                f"pu être relu avec eux.\n\n{error.message}")
            return
        except Exception:
            # Toute autre panne de relecture laisse elle aussi les
            # parametres enregistres : la barre doit le dire avant que
            # l'erreur ne remonte a l'ecran des erreurs imprevues.
            self._set_state(f"Paramètres enregistrés dans {path}.")
            raise
        if self.population is not None:
            self._populate_filters()
            self._show_quality()
        self._set_state(f"Paramètres enregistrés dans {path}. "
                        "Relancez l'analyse pour les appliquer.")

    def _populate_periods(self) -> None:
        """Periodes du fichier, la plus recente en premier choix.

        Le bloc ne parait que s'il y a matiere : un fichier instantane — le
        cas courant — n'a pas a montrer un reglage qui ne sert a rien.
        """
        from ..core.normalize import periods_of

        periods = periods_of(self.population) if self.population else []
        self._periods = periods
        if len(periods) < 2:
            self.period_block.pack_forget()
            self.period_var.set("")
            return
        self.period_choice.configure(values=periods)
        if self.period_var.get() not in periods:
            self.period_var.set(periods[-1])
        if not self.period_block.winfo_manager():
            # « reset_filters_link » n'est jamais depaquete : c'est un
            # repere sur pour poser le bloc juste avant l'etape suivante.
            self.period_block.pack(
                fill="x", pady=(0, 14),
                before=(self.team_block if self.team_block.winfo_manager()
                        else self.reset_filters_link.master))

    def _populate_teams(self) -> None:
        """Responsables du fichier, du sommet vers le bas.

        L'arbre se reconstruit a chaque importation et a chaque changement
        de periode : l'organigramme de 2024 n'est pas celui de 2026, et une
        liste laissee en place proposerait des equipes qui n'existent plus.
        """
        from ..core.hierarchy import Tree, team_rows

        self._team_keys, self._team_rows = {}, {}
        rows, summary = [], {}
        if self.population is not None and len(self.population):
            period = self.period_var.get()
            observed = self.population
            if period:
                observed = observed.filtered(
                    [employee for employee in observed
                     if employee.period == period])
            tree = Tree(observed)
            rows = team_rows(observed, tree)
            summary = tree.summary()
        if not rows:
            self.team_block.pack_forget()
            self.team_var.set(_WHOLE_FILE)
            return
        # Le libelle ne porte que le nom. Les deux effectifs y tenaient, et
        # ils s'y lisaient : mesure faite, « · · NOM PRENOM — 10 direct(s),
        # 10 au total » demande 262 px, 420 avec un patronyme reel, quand la
        # liste en offre 237. Ils passent donc sous la liste, ou rien ne les
        # rogne — et ou ils se lisent au moment de decider.
        homonymes = collections.Counter(self._identity(row["manager"])
                                        for row in rows)
        labels = [_WHOLE_FILE]
        for row in rows:
            identity = self._identity(row["manager"])
            # Deux homonymes : le matricule tranche. Il n'apparait que la,
            # et seulement quand le nom ne suffit pas.
            if homonymes[identity] > 1 and identity != row["manager"]:
                identity = f"{identity} ({row['manager']})"
            label = f"{'· ' * (row['depth'] - 1)}{identity}"
            while label in self._team_keys:
                label += " "
            self._team_keys[label] = row["manager"]
            self._team_rows[row["manager"]] = row
            labels.append(label)
        self.team_choice.configure(values=labels)
        if self.team_var.get() not in labels:
            self.team_var.set(_WHOLE_FILE)
        # Les anomalies de l'arbre se disent en nombre et jamais en
        # matricules : la colonne designe des personnes.
        self._team_anomalies = []
        for count, single, plural in (
                (len(summary.get("unknown_managers", [])),
                 "responsable introuvable", "responsables introuvables"),
                (len(summary.get("cycles", [])),
                 "salarié dans une boucle", "salariés dans une boucle"),
                (len(summary.get("duplicates", [])),
                 "matricule en double", "matricules en double")):
            if count:
                self._team_anomalies.append(
                    f"{count} {single if count == 1 else plural}")
        self._update_team_note()
        if not self.team_block.winfo_manager():
            self.team_block.pack(fill="x", pady=(0, 14),
                                 before=self.reset_filters_link.master)

    def _update_team_note(self) -> None:
        """Ce que vaut le choix courant, sous la liste.

        Les deux effectifs decident de la lecture : une equipe directe de
        quatre personnes et une equipe totale de quarante ne donnent pas la
        meme page. Le seuil de publication, lui, n'est pas rejoue ici — il
        appartient au moteur, et la vue ne fait que rapporter ce qu'il
        renvoie.
        """
        key = self._team_keys.get(self.team_var.get())
        row = self._team_rows.get(key or "")
        if row is None:
            text = ("Par défaut, l'équipe descend jusqu'au dernier niveau : "
                    "c'est celle dont un responsable répond.")
        elif self.team_direct_var.get():
            text = (f"Équipe directe : {row['direct']} "
                    f"{'salarié' if row['direct'] < 2 else 'salariés'}, "
                    f"le responsable en plus.")
        else:
            text = (f"Équipe totale : {row['total']} "
                    f"{'salarié' if row['total'] < 2 else 'salariés'} dont "
                    f"{row['direct']} en direct, le responsable en plus.")
        if self._team_anomalies:
            text += f"\nArbre incomplet : {', '.join(self._team_anomalies)}."
        self.team_note.configure(
            text=text,
            foreground=theme.WARN if self._team_anomalies else theme.FAINT)

    def _populate_filters(self) -> None:
        self._populate_periods()
        self._populate_teams()
        for child in self.filters_frame.winfo_children():
            child.destroy()
        self.filter_values.clear()
        self._filter_choices.clear()
        self._filter_buttons.clear()
        self.filter_labels.clear()
        # Les listes sont alimentees par le fichier : l'utilisateur choisit
        # parmi ce qui existe, il n'a aucune syntaxe a taper.
        limit = max_filter_values(self.configuration)
        #: Les dimensions ecartees pour avoir trop de valeurs distinctes,
        #: et ce nombre. Elles l'etaient en silence : on cochait
        #: « Qualification » dans les parametres, on enregistrait, et aucun
        #: filtre n'apparaissait. Rien ne reliait la cause a l'effet, et le
        #: reglage qui l'explique est a l'autre bout de l'ecran.
        ecartees: List[tuple] = []
        for field in dimension_fields(self.configuration):
            values = sorted({str(e.value(field) or "").strip()
                             for e in self.population} - {""})
            # Le seuil est un parametre, plus un nombre cache ici : une
            # colonne qui porte une valeur par salarie n'est pas un axe.
            if not values:
                continue
            if len(values) > limit:
                ecartees.append(
                    (dimension_label(self.configuration, field), len(values)))
                continue
            block = tk.Frame(self.filters_frame, background=theme.GROUND)
            block.pack(fill="x", pady=(0, 8))
            tk.Label(block, text=dimension_label(self.configuration, field),
                     background=theme.GROUND, foreground=theme.MUTED,
                     font=self.fonts.small).pack(anchor="w")
            # Un bouton plutot qu'une liste deroulante : la liste ne
            # retenait qu'une valeur, et il fallait taper dans la zone
            # elle-meme — une frappe qui ne correspondait a rien se
            # rattrapait toute seule, ce qui se lit comme une panne. Le
            # bouton ouvre une liste ou l'on cherche d'un cote et coche de
            # l'autre : les deux gestes ne se marchent plus dessus.
            self.filter_values[field] = None
            self._filter_choices[field] = values
            self.filter_labels[field] = dimension_label(
                self.configuration, field)
            bouton = ttk.Button(
                block, style="Filter.GhostGround.TButton",
                command=lambda f=field: self._choose_filter_values(f))
            bouton.pack(fill="x", pady=(2, 0))
            self._filter_buttons[field] = bouton
            self._refresh_filter_button(field)
        self._dire_les_filtres_ecartes(ecartees, limit)
        self._update_filter_summary()

    def _dire_les_filtres_ecartes(self, ecartees, limit: int) -> None:
        """Nomme les dimensions trop riches pour etre un critere.

        Le seuil existe pour une bonne raison : une colonne qui porte une
        valeur par salarie n'est pas un axe d'analyse, et deux mille
        matricules ne deviennent pas un critere parce qu'on peut y
        chercher. Mais l'ecarter en silence laissait l'utilisateur devant
        un reglage qui semblait ne rien faire — il avait coche la bonne
        case, et c'est ailleurs que son filtre se perdait.

        La ligne dit laquelle, combien de valeurs elle porte, et ou se
        releve le seuil. Elle ne parait que s'il y a quelque chose a dire.
        """
        if not ecartees:
            return
        noms = ", ".join(f"{nom} ({nombre})" for nom, nombre in ecartees)
        tk.Label(
            self.filters_frame,
            text=f"Pas proposé en filtre, au-delà de {limit} valeurs "
                 f"distinctes : {noms}. Le seuil se relève dans "
                 "« Associer les colonnes… », en bas.",
            background=theme.GROUND, foreground=theme.WARN,
            font=self.fonts.small, wraplength=250,
            justify="left").pack(anchor="w", pady=(2, 6))

    def _choose_filter_values(self, field: str) -> None:
        """Ouvre la liste des valeurs d'une dimension."""
        valeurs = self._filter_choices.get(field) or []
        if not valeurs:
            return
        intitule = self.filter_labels.get(field, field)
        ValuePicker(self, self.fonts, f"Filtre — {intitule}", valeurs,
                    self.filter_values.get(field),
                    lambda retenues, f=field: self.set_filter(f, retenues))

    def set_filter(self, field: str, retenues) -> None:
        """Retient des valeurs pour une dimension.

        Ne rien retenir et tout retenir sont la meme chose — aucun filtre —
        et c'est volontaire : un filtre vide donnerait une analyse sur zero
        salarie, ce qui n'est la reponse a aucune question.
        """
        if field not in self.filter_values:
            return
        if retenues is not None:
            retenues = [v for v in self._filter_choices.get(field, [])
                        if v in set(retenues)]
            if len(retenues) == len(self._filter_choices.get(field, [])):
                retenues = None
        self.filter_values[field] = retenues or None
        self._refresh_filter_button(field)
        self._update_filter_summary()

    def _refresh_filter_button(self, field: str) -> None:
        """Dit sur le bouton ce que le filtre retient.

        Les filtres defilent hors du champ visible : le libelle est le seul
        endroit ou se lit la selection sans rouvrir la liste.
        """
        bouton = self._filter_buttons.get(field)
        if bouton is None:
            return
        retenues = self.filter_values.get(field)
        total = len(self._filter_choices.get(field, []))
        if not retenues:
            bouton.configure(
                text=f"Toutes ({total})" if total else "Toutes")
        elif len(retenues) == 1:
            bouton.configure(text=self._ecourte(retenues[0]))
        else:
            bouton.configure(text=f"{len(retenues)} valeurs sur {total}")

    #: Longueur au-dela de laquelle un intitule est coupe sur le bouton
    #: d'un filtre. La colonne est etroite : un intitule de poste entier
    #: s'y ferait rogner sans prevenir, ce qui se lit comme une valeur
    #: tronquee par l'outil.
    FILTER_LABEL_MAX = 26

    @classmethod
    def _ecourte(cls, texte: str) -> str:
        return (texte if len(texte) <= cls.FILTER_LABEL_MAX
                else texte[:cls.FILTER_LABEL_MAX - 1].rstrip() + "…")

    def _current_filters(self) -> List[Dict[str, Any]]:
        """Traduit la selection en criteres pour le moteur.

        Une seule valeur devient une egalite, plusieurs une appartenance :
        le moteur sait faire les deux, et une egalite reste ce qui se relit
        le plus simplement dans un rapport.
        """
        criteres: List[Dict[str, Any]] = []
        for field, retenues in self.filter_values.items():
            if not retenues:
                continue
            if len(retenues) == 1:
                criteres.append({"field": field, "operator": "eq",
                                 "value": retenues[0]})
            else:
                criteres.append({"field": field, "operator": "in",
                                 "value": list(retenues)})
        return criteres

    # ------------------------------------------------------------- analyse

    #: Intervalle de relevé de la file du fil de calcul. Plus court que
    #: l'image de la barre : un avancement releve en retard se verrait.
    POLL_MS = 30
    #: Tranche d'execution d'un fil, le temps de l'analyse. Voir la mesure
    #: citee dans « run_analysis ».
    SWITCH_INTERVAL = 0.001
    #: Delai avant que le panneau d'attente ne prenne la place des pages.
    #: Trois cents millisecondes : au-dela, l'attente se voit ; en deca,
    #: c'est le panneau qui se verrait, et pour rien.
    WORK_PANEL_DELAY_MS = 300

    def run_analysis(self) -> None:
        if not self.source_path:
            return
        self.analyse_button.state(["disabled"])
        # Sous « Analyser », et non sous le bouton d'export : la barre
        # repond au geste qu'on vient de faire, elle doit paraitre ou le
        # regard est.
        self.progress.pack(fill="x", pady=(10, 2), before=self.export_button)
        self.progress.start("Préparation")
        self._set_state("Analyse en cours…")
        # Le panneau ne parait qu'apres un court delai : sur un petit
        # fichier l'analyse dure moins qu'un clignement, et un panneau qui
        # apparaitrait pour disparaitre aussitot serait un defaut
        # d'affichage, pas une information.
        self.work_panel.start()
        self._work_job = self.after(self.WORK_PANEL_DELAY_MS,
                                    self._show_work_panel)
        # Le fil de calcul garde le verrou global de Python par tranches de
        # cinq millisecondes : le fil qui dessine n'obtenait la main que
        # trente-sept fois par seconde, et une image sur dix arrivait avec
        # plus de cent millisecondes de retard. Reduire la tranche le temps
        # de l'analyse coute cinq pour cent sur le calcul et rend la barre
        # regulierement animee.
        self._switch_interval = sys.getswitchinterval()
        #: Releve de file en attente, pour l'annuler a la fermeture : une
        #: fenetre fermee pendant une analyse laissait Tk executer un
        #: rappel dont le widget n'existait plus.
        self._poll_job: Optional[str] = None
        sys.setswitchinterval(self.SWITCH_INTERVAL)
        request = AnalysisRequest(
            source_path=self.source_path,
            config_dir=self.config_dir,
            filters=build_filters(self._current_filters(), self.configuration),
            period=self.period_var.get() or None,
            team=self._team_keys.get(self.team_var.get()),
            team_direct_only=bool(self.team_direct_var.get()),
            # Aucune liste n'est imposee : le moteur segmente sur toutes les
            # dimensions reellement renseignees. Choisir a l'avance faisait
            # doublon avec la liste de l'onglet Segments, qui permet d'en
            # changer apres coup.
            segments=[],
            title="Analyse de rémunération",
            ignore_quality_errors=True,
            # Appele depuis le fil de calcul : il ne touche a rien de la
            # fenetre, il depose. Tk n'est pas sur pour deux fils.
            progress=lambda label, part: self._queue.put(
                ("avancement", (label, part))),
        )
        threading.Thread(target=self._worker, args=(request,), daemon=True).start()
        self._poll_job = self.after(self.POLL_MS, self._poll)

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

    def _show_work_panel(self) -> None:
        """Le panneau prend la place des pages, et la barre des onglets se
        tait : rien a cliquer tant qu'il n'y a rien a lire."""
        self._work_job = None
        if self.result is not None and not self.analyse_button.instate(
                ["disabled"]):
            return
        if not self.work_panel.winfo_manager():
            self.pages.pack_forget()
            self.work_panel.pack(fill="both", expand=True)

    def _hide_work_panel(self) -> None:
        """Les pages reprennent leur place."""
        if getattr(self, "_work_job", None) is not None:
            self.after_cancel(self._work_job)
            self._work_job = None
        if self.work_panel.winfo_manager():
            self.work_panel.pack_forget()
        if not self.pages.winfo_manager():
            self.pages.pack(fill="both", expand=True)

    def _poll(self) -> None:
        """Releve ce que le fil de calcul a depose, sans jamais l'attendre.

        La file est videe entierement a chaque passage : un seul message par
        passage ferait prendre a la barre un retard qu'elle ne rattraperait
        plus sur un gros fichier, ou l'avancement s'annonce toutes les
        soixante millisecondes.
        """
        resultat = None
        while True:
            try:
                kind, payload = self._queue.get_nowait()
            except queue.Empty:
                break
            if kind == "avancement":
                self.progress.announce(*payload)
                self.work_panel.announce(*payload)
                continue
            resultat = (kind, payload)
        if resultat is None:
            # Le battement du panneau vit sur ce meme releve : une image de
            # plus, le chronometre, et rien de plus — le fil de calcul garde
            # la main.
            self.work_panel.tick()
            self._poll_job = self.after(self.POLL_MS, self._poll)
            return
        self._poll_job = None
        kind, payload = resultat
        sys.setswitchinterval(self._switch_interval)
        self.progress.stop()
        self.work_panel.finish()
        self._hide_work_panel()
        if kind == "ok":
            # Le trait se termine, puis reste le temps que les resultats
            # s'affichent : c'est la seule seconde ou il est plein.
            self.progress.finish()
        self.analyse_button.state(["!disabled"])
        if kind == "erreur":
            self.progress.pack_forget()
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
            # Un bandeau dans la fenetre, non une boite modale. Elle
            # bloquait tout jusqu'a ce que quelqu'un clique : sur un poste
            # sans personne devant — un banc d'essai, une session laissee
            # ouverte — plus rien n'avancait, et le defaut d'affichage se
            # muait en outil fige. Le bandeau dit la meme chose, reste
            # visible, et laisse la fenetre repondre.
            self.notice.configure(
                text="Les résultats ont été calculés mais n'ont pas pu être "
                     f"affichés ({type(error).__name__}). Les documents "
                     "restent productibles : utilisez « Produire les "
                     "documents ».",
                background=theme.CRIT_SOFT, foreground=theme.CRIT)
            if not self.notice.winfo_manager():
                self.notice.pack(fill="x", after=self.tabbar)
            self._set_state("Analyse terminée · affichage incomplet.")
        # La barre s'efface une fois les resultats poses, et non avant : la
        # derniere chose qu'on voit d'elle est un trait plein.
        self.progress.pack_forget()

    # ------------------------------------------------------------ affichage

    def _render_results(self) -> None:
        payload = self.result.payload
        currency = payload["salary"].get("currency", "EUR")
        self._index_identities()
        self._show_quality(payload["quality"])
        self._show_overview(payload)
        self.histogram.set_distribution(payload["distribution"], currency)
        self._show_distribution()
        self._show_scatter(payload["scatter"], currency)
        self._show_segments(payload["segments"])
        self._show_pay_equity(payload["pay_equity"])
        self._org_available = self._show_org(payload)
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
            # Les deux pages tracent les memes boites : ce qui ouvre l'une
            # ouvre l'autre.
            "colonnes": any(row.get("chartable")
                            for block in segments
                            for row in block.get("rows", [])),
            "nuage": bool(payload["scatter"].get("available")),
        }
        eligible = {
            "population": not (payload["population"].get("masked")
                               and payload["salary"].get("masked")),
            # Sur demande : il n'y a d'organigramme que si l'on a choisi une
            # equipe a l'etape 3. Son absence ne s'explique donc pas comme
            # celle des autres — voir ON_DEMAND.
            "organigramme": bool(getattr(self, "_org_available", False)),
            "graphique": any(charts.values()),
            "equite": bool(payload.get("pay_equity", {}).get("available")),
            "qualite": True,
        }
        for key, allowed in charts.items():
            self.chartbar.set_visible(key, allowed)
        for key, allowed in eligible.items():
            self.tabbar.set_visible(key, allowed)

        # Chaque vue retiree est accompagnee de la raison que le moteur a
        # deja ecrite pour elle. Un message commun — « effectif insuffisant,
        # les seuils s'appliquent a 8 salaries » — melait deux nombres de
        # nature differente : l'effectif analyse et le seuil requis. Lu vite,
        # le premier passait pour le second, et l'on cherchait ou l'outil
        # etait regle sur huit. Il ne l'a jamais ete : huit etait le nombre
        # de salaries retenus.
        raisons = self._hidden_reasons(payload, charts)
        hidden = [label for key, label in TABS
                  if not eligible[key] and key not in ON_DEMAND]
        # Un graphique retire alors que son onglet reste ouvert doit
        # s'expliquer autant qu'un onglet disparu : sans cela, il manque une
        # entree dans la barre et rien ne dit pourquoi.
        if eligible["graphique"]:
            hidden += [label for key, label in CHARTS if not charts[key]]
        manquantes = [(label, raisons.get(key, ""))
                      for key, label in TABS
                      if not eligible[key] and key not in ON_DEMAND]
        if eligible["graphique"]:
            manquantes += [(label, raisons.get(key, ""))
                           for key, label in CHARTS if not charts[key]]
        # La vue d'ensemble a deux moities, et deux seuils : l'une peut
        # tomber quand l'autre tient. L'onglet reste alors ouvert, et c'est
        # a ce titre-la qu'il faut annoncer la moitie absente — sans quoi
        # la page montre un vide que rien n'explique.
        if eligible["population"]:
            for cle, titre in (("population", "Vue d'ensemble — population"),
                               ("salary", "Vue d'ensemble — rémunération")):
                bloc = payload.get(cle) or {}
                if bloc.get("masked"):
                    hidden.append(titre)
                    manquantes.append((titre, bloc.get("warning", "")))
        headcount = payload["population"].get("headcount", 0)
        scope = payload.get("scope") or {}
        # Les filtres se lisent la plutot qu'en tete d'un onglet : ils
        # gouvernent toutes les pages, et la barre d'etat est la seule zone
        # visible quel que soit l'onglet ouvert.
        state = f"Analyse terminée · {headcount} salariés"
        # La periode se lit la aussi : sur un fichier de trois ans,
        # « 100 salaries » ne dit pas de quelle annee il s'agit.
        if scope.get("period"):
            state += f" · période {scope['period']}"
        # L'equipe se lit avant les filtres : elle designe la population,
        # les filtres ne font que la restreindre.
        team = scope.get("team") or {}
        if team.get("manager"):
            state += (" · équipe directe de " if team.get("direct_only")
                      else " · équipe de ") + self._identity(team["manager"])
        if scope.get("filtered") and scope.get("description"):
            state += f" · {scope['description']}"
        if hidden:
            state += f" · {len(hidden)} vue(s) masquée(s)"
        # Le controle qualite se lit la aussi. Un fichier qui porte des
        # anomalies critiques — une sortie avant l'entree, un salaire
        # absent — produit quand meme une analyse, mais l'utilisateur doit
        # l'apprendre sans avoir a penser a ouvrir l'onglet « Qualite » :
        # un chiffre faux qui a l'air juste est le pire des resultats.
        critiques = (payload.get("quality") or {}).get("anomalies_critiques", 0)
        if critiques:
            state += f" · {critiques} anomalie(s) critique(s)"
        self._set_state(state)

        messages = []
        if critiques:
            messages.append(
                f"{critiques} anomalie(s) critique(s) dans le fichier : les "
                "indicateurs sont calculés sur des données que le contrôle "
                "qualité signale. Ouvrez l'onglet « Qualité » avant de les "
                "publier.")
        if manquantes:
            # L'effectif analyse d'abord, et nomme comme tel : c'est lui
            # qu'on reconnait, et il ne doit pas pouvoir se lire comme un
            # seuil. Puis une ligne par vue, portant le seuil qui lui
            # manque — ils ne sont pas tous les memes.
            lignes = [f"La sélection analysée compte {headcount} salarié(s). "
                      f"{len(manquantes)} vue(s) en demandent davantage :"]
            for label, raison in manquantes:
                lignes.append(f"    • {label} — "
                              + (raison or "effectif insuffisant pour "
                                           "publier ces résultats."))
            lignes.append("Élargissez le filtre, ou ajustez les seuils dans "
                          "« Paramètres » → Confidentialité.")
            messages.append("\n".join(lignes))
        if not messages:
            self.notice.pack_forget()
            return
        self.notice.configure(
            text="\n".join(messages),
            background=theme.CRIT_SOFT if critiques else theme.WARN_SOFT,
            foreground=theme.CRIT if critiques else theme.WARN)
        self.notice.pack(fill="x", after=self.tabbar)

    def _hidden_reasons(self, payload: Dict[str, Any],
                        charts: Dict[str, bool]) -> Dict[str, str]:
        """La raison propre a chaque vue retiree.

        Elle est relue dans le resultat d'analyse, jamais reecrite ici : le
        moteur sait quel seuil il a applique — dix pour un graphique, cinq
        de chaque sexe pour un ecart —, et une phrase recomposee dans la
        fenetre finirait par annoncer un seuil que le calcul n'emploie pas.
        """
        rules = metrics.PrivacyRules.from_config(self.configuration)
        distribution = (payload.get("distribution") or {}).get("warning", "")
        nuage = (payload.get("scatter") or {}).get("warning", "")
        boites = (f"Effectif insuffisant pour tracer une dispersion "
                  f"(minimum paramétré : {rules.min_chart} salariés).")
        return {
            "population": ((payload.get("salary") or {}).get("warning")
                           or (payload.get("population") or {}).get("warning")
                           or ""),
            # L'onglet ne tombe que si les trois graphiques tombent : la
            # raison du premier d'entre eux vaut pour l'onglet.
            "graphique": next((raison for actif, raison in
                               ((charts.get("distribution"), distribution),
                                (charts.get("nuage"), nuage),
                                (charts.get("boites"), boites))
                               if not actif and raison), ""),
            "equite": (payload.get("pay_equity") or {}).get("warning", ""),
            "distribution": distribution,
            "nuage": nuage,
            "boites": boites,
            "colonnes": boites,
        }

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

    def _kpis(self, parent, pairs, per_row: Optional[int] = None) -> None:
        for child in parent.winfo_children():
            child.destroy()
        band = tk.Frame(parent, background=theme.CANVAS)
        band.pack(fill="x", pady=(0, 16))
        parent.update_idletasks()
        # Une grille a colonnes egales, quatre au plus par rangee : au-dela,
        # la colonne devient trop etroite pour une valeur monetaire et le
        # chiffre est rogne des deux cotes. Les rangees sont equilibrees.
        # `per_row` impose : un bandeau pose dans une colonne etroite doit
        # pouvoir tenir sur une rangee sans que la regle generale l'y force.
        if per_row is None:
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
        plafond = getattr(tree, "plafond", 0)
        if plafond:
            # Au moins une ligne : a zero, Tk reduit le tableau a ses
            # en-tetes et la page se referme sur rien.
            tree.configure(height=max(min(len(rows), plafond), 1))

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

    #: Largeur minimale d'une colonne de la vue d'ensemble. En dessous, la
    #: pyramide perd ses ailes et l'echelle ses graduations : mieux vaut
    #: alors deux colonnes et une page qui defile que trois colonnes
    #: rognees.
    OVERVIEW_COLUMN = 330

    def _show_overview(self, payload: Dict[str, Any]) -> None:
        """Population et remuneration sur une seule page, en trois colonnes.

        Le bandeau d'indicateurs qui coiffait la page a disparu : il posait
        six chiffres au-dessus de colonnes qui parlaient deja d'eux, et
        repetait la mediane que l'echelle affiche trois centimetres plus bas.
        Chaque colonne porte donc les siens, en tete, sous la meme forme que
        les tableaux qui suivent.

        Trois colonnes et non deux : a deux, la colonne de population portait
        la liste, le camembert et les deux pyramides — neuf cents pixels —
        pendant que celle de remuneration s'arretait a cinq cents. La page
        debordait par desequilibre, et non par exces de contenu. Les
        pyramides, qui sont le bloc le plus haut, prennent donc une colonne a
        elles, et l'ensemble tient sur un ecran. Sous la largeur necessaire,
        on revient a deux colonnes et la page defile : mieux vaut defiler que
        rogner.

        Rien n'y figure deux fois. Les scalaires de population sont reunis
        dans une seule liste au lieu d'etre partages entre un bandeau et les
        en-tetes des pyramides ; et la liste de remuneration ne reprend ni la
        mediane ni les percentiles, qui sont l'echelle elle-meme.
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

        # Des colonnes independantes, et non une grille : dans une grille, la
        # rangee prend la hauteur du plus grand des blocs, et le bloc court
        # laisse un trou au milieu de la page. Empilees, chaque colonne se
        # referme sur son contenu et le vide tombe en bas.
        columns = tk.Frame(self.overview_frame, background=theme.CANVAS)
        columns.pack(fill="both", expand=True)
        self._overview_columns = self._overview_column_count()
        wide = self._overview_columns >= 3
        left = tk.Frame(columns, background=theme.CANVAS)
        left.pack(side="left", fill="both", expand=True, padx=(0, 26))
        middle = tk.Frame(columns, background=theme.CANVAS)
        if wide:
            middle.pack(side="left", fill="both", expand=True, padx=(0, 26))
        right = tk.Frame(columns, background=theme.CANVAS)
        right.pack(side="left", fill="both", expand=True)
        if not wide:
            # Deux colonnes : les pyramides rejoignent la population.
            middle.destroy()
            middle = left
        # L'ordre de lecture : qui compose la population, ce qu'elle est
        # payee, comment elle se structure. Les pyramides passent en
        # troisieme colonne — elles sont le bloc le plus haut, et une page
        # se lit mieux quand sa colonne la plus longue est au bout.
        self._overview_frames = [left, middle, right] if wide else [left, right]

        # La colonne des structures : la troisieme quand il y en a trois, la
        # premiere sinon — a deux colonnes, les pyramides rejoignent la
        # population, dont elles sont le detail.
        structures = right if wide else left
        pay = middle if wide else right
        if population.get("masked"):
            # Une colonne vide au milieu d'une page se lit comme un defaut
            # d'affichage, pas comme un masquage : la raison prend la place
            # du contenu absent.
            self._masked_panel(left, "Population",
                               population.get("warning"), "population_summary")
        else:
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
            self._coverage_note(left, population)
            self._csp_panel(left, population)
            # Les pyramides n'ont plus de chiffre en tete : leurs moyennes
            # sont juste au-dessus, dans la liste.
            self._pyramid_panel(structures, "Pyramide des âges",
                                population.get("age_bands", []), None,
                                key="age_bands", measure="d'âge")
            self._pyramid_panel(structures, "Structure d'ancienneté",
                                population.get("tenure_bands", []), None,
                                key="tenure_bands", measure="d'ancienneté")

        if salary.get("masked"):
            self._masked_panel(
                pay, salary.get("field_label") or "Rémunération",
                salary.get("warning"), "salary_summary")
        else:
            spread = salary.get("dispersion") or {}
            # Ni la mediane ni un percentile ici : ils sont l'echelle, juste
            # en dessous. Ne restent que les deux chiffres qui n'y figurent
            # pas.
            # Le meme ecran veut dire deux choses differentes selon le champ
            # analyse : « Salaire de base » ou « Remuneration totale ». Il le
            # dit, comme le font l'onglet Segments et le rapport.
            self._ruled_panel(
                pay, "Rémunération", (), [
                    ("Masse salariale",
                     format_money(salary.get("payroll"), currency), "payroll"),
                    ("Salaire moyen",
                     format_money(salary.get("mean"), currency), "mean"),
                ], key="salary_summary",
                extra=("Champ",
                       salary.get("field_label") or salary.get("field", ""),
                       "analysis_field"))
            cell = self._panel_head(pay, "Échelle de rémunération", None,
                                    key="salary_scale")
            scale = ScaleChart(cell)
            scale.pack(fill="x")
            scale.set_salary(salary, currency)
            self._ruled_panel(
                pay, "Dispersion", ("Indicateur", "Valeur"),
                dispersion_rows(spread, currency), key="dispersion")
        # La page connait maintenant son contenu : elle peut l'accorder a la
        # hauteur dont elle dispose. L'ajustement est differe — il mesure, il
        # faut donc que la geometrie soit posee — et marque de la generation
        # qui l'a demande : recomposee entre-temps, la page a jete les cadres
        # que cet appel-ci allait mesurer.
        generation = self._overview_build = object()
        self.after_idle(lambda: self._fit_overview(generation))

    #: Bornes de respiration : la page ne grandit pas au-dela, sous peine
    #: d'un anneau de la taille d'une assiette et de pyramides etirees.
    PYRAMID_ROW_MAX = 32
    PIE_RADIUS_MAX = 78
    SCALE_HEIGHT_MAX = 176
    #: Ecart maximal ajoute entre deux blocs d'une meme colonne.
    PANEL_GAP_MAX = 30

    def _fit_overview(self, generation: Optional[object] = None) -> None:
        """Accorde la page a la hauteur dont elle dispose.

        Dimensionnee pour le pire cas — une fenetre basse, ou un affichage
        Windows a 150 % qui grossit les polices —, la page laissait un tiers
        de hauteur vide sur un grand ecran. Elle mesure donc la place
        offerte et la rend a son contenu : d'abord aux graphiques, qui se
        lisent d'autant mieux qu'ils sont grands, puis en ecartant les blocs
        les uns des autres.

        Grandir ne change pas la largeur de la page — mais grandir peut
        faire apparaitre l'ascenseur, et l'ascenseur, lui, prend seize
        pixels de large. La page se reaccordait alors, rendait ce qu'elle
        venait de prendre, l'ascenseur disparaissait, et tout recommencait :
        un tremblement gauche-droite, une centaine d'aller-retours par
        seconde. Deux verrous l'empechent.

        Le premier est dans `_grow_column`, qui mesure desormais la place
        libre sur une colonne ramenee a sa taille de base : pour une hauteur
        donnee, il rend toujours le meme resultat. Le second est ici : un
        accord deja fait pour cette page, cette hauteur et cette largeur
        n'est pas refait. Une recomposition change la generation et le
        libere.
        """
        if generation is not None and generation is not getattr(
                self, "_overview_build", None):
            return
        # L'accord mesure, et mesurer demande de vider la file d'attente
        # d'affichage : un « <Configure> » peut donc arriver au milieu et
        # rappeler l'accord par-dessus celui qui court. Tant qu'il court,
        # il ne se rappelle pas.
        if getattr(self, "_overview_fitting", False):
            return
        self._overview_fitting = True
        try:
            frames = [frame for frame in getattr(self, "_overview_frames", [])
                      if frame.winfo_exists() and frame.winfo_manager()]
            if not frames:
                return
            self.overview_frame.update_idletasks()
            available = self.overview_canvas.winfo_height() - 40
            if available < 200:
                return
            # Les empreintes deja accordees pour CETTE page, et non la
            # derniere seulement : l'ascenseur fait alterner la largeur
            # entre deux valeurs, et une memoire d'une seule empreinte se
            # laisse contourner par un aller-retour. Les accords possibles
            # sont en nombre fini ; chacun n'est fait qu'une fois, et la
            # page finit donc toujours par se poser.
            generation_courante = getattr(self, "_overview_build", None)
            faits = getattr(self, "_overview_fitted", None)
            if not faits or faits[0] is not generation_courante:
                faits = (generation_courante, set())
                self._overview_fitted = faits
            empreinte = (available, self.overview_canvas.winfo_width())
            if empreinte in faits[1]:
                return
            faits[1].add(empreinte)
            for frame in frames:
                self._grow_column(frame, available)
            self.overview_frame.update_idletasks()
            for frame in frames:
                self._space_column(frame, available)
        except tk.TclError:
            # Un widget detruit entre la mesure et l'ajustement : la page
            # vient d'etre recomposee, et c'est elle qui fait foi.
            return
        finally:
            self._overview_fitting = False

    def _grow_column(self, frame: tk.Frame, available: int) -> None:
        """Rend la place libre aux graphiques de la colonne.

        La mesure part toujours de la taille de base. Elle partait de la
        taille courante : au deuxieme passage, la colonne etait deja
        agrandie, la place libre valait zero, et les graphiques rendaient
        tout ce que le premier passage leur avait donne. La page oscillait
        alors entre deux hauteurs — et comme l'une des deux fait apparaitre
        l'ascenseur, elle oscillait aussi entre deux largeurs.
        """
        pyramids = self._of_type(frame, PyramidChart)
        pies = self._of_type(frame, PieChart)
        scales = self._of_type(frame, ScaleChart)
        if not (pyramids or pies or scales):
            return
        for chart in pyramids:
            chart.set_row_height(PyramidChart.ROW)
        for chart in pies:
            chart.set_radius(PieChart.RADIUS)
        for chart in scales:
            chart.set_height(ScaleChart.HEIGHT)
        frame.update_idletasks()
        rows = sum(max(len(chart.rows), 1) for chart in pyramids)
        if pyramids and rows:
            slack = available - frame.winfo_reqheight()
            extra = max(0, min(self.PYRAMID_ROW_MAX - PyramidChart.ROW,
                               slack // rows))
            for chart in pyramids:
                chart.set_row_height(PyramidChart.ROW + extra)
            frame.update_idletasks()
        for chart in pies:
            slack = available - frame.winfo_reqheight()
            extra = max(0, min(self.PIE_RADIUS_MAX - PieChart.RADIUS,
                               slack // 2))
            chart.set_radius(PieChart.RADIUS + extra)
            frame.update_idletasks()
        for chart in scales:
            slack = available - frame.winfo_reqheight()
            extra = max(0, min(self.SCALE_HEIGHT_MAX - ScaleChart.HEIGHT,
                               slack))
            chart.set_height(ScaleChart.HEIGHT + extra)
            frame.update_idletasks()

    def _space_column(self, frame: tk.Frame, available: int) -> None:
        """Repartit ce qui reste entre les blocs, plutot qu'en bas de page.

        Un vide reparti se lit comme une respiration ; le meme vide massé
        sous le dernier bloc se lit comme une page inachevee.
        """
        blocks = [child for child in frame.winfo_children()
                  if child.winfo_manager()]
        if len(blocks) < 2:
            return
        # Les ecarts reviennent a leur valeur de depart avant la mesure.
        # L'ecart de depart est retenu au premier passage : ajoute au
        # precedent, il grandirait a chaque redimensionnement. Mais le
        # retenir ne suffisait pas : la place libre se mesurait sur une
        # colonne portant encore les ecarts du passage precedent, si bien
        # que le resultat dependait du chemin — une fenetre agrandie puis
        # ramenee a sa taille ne retrouvait pas sa page.
        for block in blocks:
            base = getattr(block, "_base_gap", None)
            if base is None:
                info = block.pack_info()
                base = int(str(info.get("pady", 0)).split()[-1].strip("()"))
                block._base_gap = base
            block.pack_configure(pady=(0, base))
        frame.update_idletasks()
        slack = available - frame.winfo_reqheight()
        if slack <= 0:
            return
        extra = min(self.PANEL_GAP_MAX, slack // (len(blocks) - 1))
        if extra <= 0:
            return
        for block in blocks[:-1]:
            block.pack_configure(pady=(0, block._base_gap + extra))

    @staticmethod
    def _of_type(widget: tk.Misc, kind) -> List[tk.Misc]:
        found = []

        def walk(current: tk.Misc) -> None:
            for child in current.winfo_children():
                if isinstance(child, kind):
                    found.append(child)
                else:
                    walk(child)

        walk(widget)
        return found

    def _overview_width(self) -> int:
        """Largeur offerte a la page, mesuree la ou elle est connue.

        Le cadre lui-meme repond un pixel tant qu'il n'a jamais ete
        affiche : c'est le canevas qui le porte qui sait, et lui le sait des
        que la fenetre a une taille.
        """
        for widget in (getattr(self, "overview_canvas", None),
                       self.overview_frame):
            if widget is not None and widget.winfo_width() > 1:
                return widget.winfo_width()
        return 0

    def _overview_column_count(self) -> int:
        """Trois colonnes si la largeur le permet, deux sinon.

        Tant que la largeur est inconnue, on repond trois : la page se
        redispose au premier redimensionnement, et il vaut mieux partir de
        la disposition qui tient sur un ecran que de s'y figer a deux.
        """
        width = self._overview_width()
        if not width:
            return 3
        return 3 if width >= 3 * self.OVERVIEW_COLUMN + 52 else 2

    def _on_window_resize(self, event) -> None:
        """Oublie les accords deja faits quand la fenetre change de taille.

        La memoire des accords existe pour couper une boucle : l'ascenseur
        qui apparait change la largeur, qui redemande un accord, qui le
        fait disparaitre. Elle ne doit pas aller plus loin que cela. Sans
        cet oubli, revenir a une taille deja visitee laissait la page telle
        qu'elle etait a l'autre taille — des graphiques dimensionnes pour
        une fenetre qui n'est plus la.

        Les evenements des enfants passent aussi par la fenetre : seuls les
        siens comptent.
        """
        if event.widget is not self:
            return
        taille = (event.width, event.height)
        if taille != getattr(self, "_window_size", None):
            self._window_size = taille
            self._overview_fitted = None

    def _on_overview_resize(self, event) -> None:
        """Suit la largeur, et redispose la page si le compte change.

        Le trace coute une poignee de millisecondes, et la condition ne
        bascule qu'une fois par franchissement : il n'y a ni rafale ni
        boucle — redisposer ne change pas la largeur.
        """
        self.overview_canvas.itemconfigure(self._overview_window,
                                           width=event.width - 36)
        if self.result is None:
            return
        if self._overview_column_count() == self._overview_columns:
            # Meme disposition, mais peut-etre pas la meme hauteur : la page
            # se reaccorde sans se recomposer.
            generation = getattr(self, "_overview_build", None)
            self.after_idle(lambda: self._fit_overview(generation))
            return
        try:
            self._show_overview(self.result.payload)
        except Exception as error:              # noqa: BLE001
            # Un redimensionnement ne doit jamais faire tomber la fenetre :
            # la page garde alors la disposition qu'elle avait.
            log_event("interface", "overview_resize", status="ERREUR",
                      detail=type(error).__name__)

    def _coverage_note(self, parent, population: Dict[str, Any]) -> None:
        """Sur quelle part de l'effectif l'anciennete est etablie.

        Elle ne parait que lorsqu'il manque quelque chose : a couverture
        complete, la ligne n'apprend rien et prend une place. Sur un fichier
        ou un quart des dates d'entree manque, la mediane affichee ne porte
        pas sur la population annoncee, et la page doit le dire.
        """
        known = population.get("tenure_known")
        headcount = population.get("headcount", 0)
        if known is None or known >= headcount:
            return
        # Une ligne, et non deux : trois reserves de deux lignes chacune
        # coutaient cinquante pixels a une page qui doit tenir sur un ecran.
        self._note(parent,
                   f"Ancienneté connue pour {known} salariés sur {headcount}.")

    def _note(self, parent, text: str) -> tk.Label:
        """Une reserve sous un bloc, dans la chasse des mentions."""
        label = tk.Label(parent, text=text, background=theme.CANVAS,
                         foreground=theme.MUTED, font=self.fonts.small,
                         wraplength=self.OVERVIEW_COLUMN, justify="left")
        label.pack(anchor="w", pady=(0, 14))
        return label

    def _csp_panel(self, parent, population: Dict[str, Any]) -> None:
        """La repartition par CSP, en camembert.

        « CSP » est le mot du metier ; la colonne qui la porte est declaree
        en configuration et s'appelle « Statut » dans la plupart des exports.
        Les deux se lisent — le titre et, a sa droite, le champ employe —,
        sans quoi on ne sait pas ce qu'on regarde.
        """
        parts = population.get("csp_split") or []
        if not parts:
            return
        cell = self._panel_head(
            parent, "Répartition par CSP",
            ("Champ", population.get("csp_label")
             or population.get("csp_field", ""), "csp_split"),
            key="csp_split")
        chart = PieChart(cell)
        chart.pack(fill="x")
        chart.set_parts(parts, population.get("headcount", 0),
                        maximum=population.get("csp_max_slices", 6))

    def _masked_panel(self, parent, title: str, reason: Optional[str],
                      key: Optional[str] = None) -> None:
        """Un bloc qui dit pourquoi il n'a rien a montrer.

        La vue d'ensemble a deux moities independantes — qui compose la
        population, ce qu'elle est payee — et deux seuils independants :
        celle de remuneration tombe des que les montants connus sont trop
        peu nombreux, meme quand l'effectif suffit largement. Sans ce bloc,
        sa colonne disparaissait sans un mot et la page paraissait cassee.
        """
        self._panel_head(parent, title, key=key)
        tk.Label(parent,
                 text=reason or "Résultat masqué pour préserver la "
                                "confidentialité.",
                 background=theme.CANVAS, foreground=theme.WARN,
                 font=self.fonts.body, anchor="w", justify="left",
                 wraplength=self.OVERVIEW_COLUMN - 20).pack(anchor="w",
                                                            pady=(0, 16))

    def _panel_head(self, parent, title: str, extra=None,
                    key: Optional[str] = None) -> tk.Frame:
        """Intitule, chiffre d'appoint a droite, filet. Chacun s'explique."""
        # Vingt-six pixels sous chaque bloc, sept blocs : cent quatre-vingts
        # pixels de blanc pour une page qui doit tenir sur un ecran. Seize
        # separent encore nettement deux blocs.
        cell = tk.Frame(parent, background=theme.CANVAS)
        cell.pack(fill="x", pady=(0, 16))
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
                            pady=4, padx=(0, 0) if index else (0, 24))
                self.hints.attach(widget, note)
        theme.rule(table).grid(row=2 + len(rows), column=0,
                               columnspan=columns, sticky="ew", pady=(4, 0))

    def _pyramid_panel(self, parent, title, bands, extra,
                       key: Optional[str] = None,
                       measure: str = "") -> None:
        """Pyramide si le sexe est renseigne, barres simples sinon.

        Deux populations n'y figurent pas, et pour deux raisons qu'il ne
        faut pas confondre — la fenetre les a confondues, et annoncait
        « sexe non renseigne » des salaries qui en avaient un.

        Les salaries qu'aucune tranche n'accueille — valeur absente, ou hors
        des bornes declarees — n'ont pas de place sur l'axe : la pyramide se
        lit du plus jeune au plus age, et ils ne sont ni l'un ni l'autre.

        Ceux dont le sexe est inconnu, eux, ont bien une tranche mais aucune
        aile : ils sont dans le graphique sans y etre dessines.

        Les deux se comptent sous le graphique, chacun sous son motif.
        """
        drawn = [band for band in bands if not band.get("catch_all")]
        outside = sum(band.get("count") or 0 for band in bands
                      if band.get("catch_all"))
        sexless = sum(band.get("unknown_sex") or 0 for band in drawn)
        cell = self._panel_head(parent, title, extra, key=key)
        pyramid = PyramidChart(cell)
        pyramid.set_rows(drawn if drawn else bands)
        if pyramid.has_split():
            pyramid.pack(fill="x")
            if outside:
                self._note(parent,
                           f"{outside} salarié{'s' if outside > 1 else ''} "
                           f"sans tranche{' ' + measure if measure else ''} "
                           f"— valeur absente ou hors bornes —, "
                           f"hors pyramide.")
            if sexless:
                self._note(parent,
                           f"{sexless} salarié{'s' if sexless > 1 else ''} au "
                           f"sexe non renseigné : compté"
                           f"{'s' if sexless > 1 else ''} dans l'effectif, "
                           f"sans aile dans la pyramide.")
            return
        # Sans la colonne « Sexe », une pyramide n'aurait qu'une aile : on
        # retombe sur la lecture en barres plutot que d'afficher un demi
        # graphique.
        pyramid.destroy()
        chart = BandChart(cell)
        chart.pack(fill="x")
        chart.set_rows(bands)

    def _show_org(self, payload: Dict[str, Any]) -> bool:
        """L'organigramme de l'equipe analysee. Rend vrai s'il y a a montrer.

        L'arbre se reconstruit sur le fichier de la periode, jamais sur la
        population deja filtree : un filtre « France » couperait la branche
        d'un responsable dont une partie de l'equipe est ailleurs, et le
        rattachement affiche serait faux. Les filtres s'appliquent ensuite,
        en retirant des salaries de l'arbre ainsi construit — c'est le meme
        ordre que celui du moteur, et c'est ce qui fait que cet onglet
        compte exactement ce que les autres comptent.
        """
        from ..core.hierarchy import Tree

        self._org_keys = {}
        scope = payload.get("scope") or {}
        team = scope.get("team") or {}
        key = team.get("manager") or ""
        if self.population is None:
            self._clear_org("Chargez un fichier pour voir l'organigramme.")
            return False
        if not key:
            # La page vide se taisait. L'utilisateur ouvrait l'onglet,
            # n'y voyait rien, et rien ne lui disait que le dessin attend
            # qu'on designe une equipe — ni que son fichier peut
            # simplement ne pas porter de colonne « Manager ».
            self._clear_org(
                "Choisissez un responsable dans « Analyser une équipe », à "
                "gauche : l'organigramme dessine son équipe."
                if self._team_keys else
                "Aucun rattachement hiérarchique n'a été lu dans ce "
                "fichier. Déclarez une colonne « Manager » portant le "
                "matricule du responsable pour voir l'organigramme.")
            return False
        observed = self.population
        if scope.get("period"):
            observed = observed.filtered(
                [employee for employee in observed
                 if employee.period == scope["period"]])
        tree = Tree(observed)
        if key not in tree.employees:
            self._clear_org(
                "Le responsable choisi ne figure pas dans le périmètre "
                "analysé : l'organigramme de son équipe ne peut pas être "
                "dessiné.")
            return False
        keep = {employee.employee_id for employee in self.result.filtered}
        direct = bool(team.get("direct_only"))
        nodes = org_view.chart_nodes(tree, key, self.configuration,
                                     keep=keep, direct_only=direct)
        rows = org_view.member_rows(tree, key, self.configuration,
                                    keep=keep, direct_only=direct)
        jobs = org_view.job_rows(tree, key, self.configuration,
                                 keep=keep, direct_only=direct)
        resume = org_view.summary(nodes, rows)
        currency = payload["salary"].get("currency", "EUR")

        # Six chiffres sur une seule ligne : ce sont les six qu'on lit avant
        # d'entrer dans un tableau, et les repartir sur deux rangees ferait
        # chercher le sixieme.
        self._kpis(self.org_frame, [
            # Des comptes de personnes : sans decimale. « 47,0 salaries »
            # affiche une precision que la donnee n'a pas.
            ("Effectif", format_number(resume["headcount"], 0), "effectif"),
            ("Responsables", format_number(resume["managers"], 0)),
            ("Ancienneté moyenne", format_years(resume.get("tenure_mean"))),
            ("Niveaux", format_number(resume["levels"], 0)),
            ("Salaire médian", format_money(resume.get("median"), currency)
             if resume.get("median") is not None else "masqué"),
            ("Salaire moyen", format_money(resume.get("mean"), currency)
             if resume.get("mean") is not None else "masqué"),
        ], per_row=6)

        self._fill(self.org_jobs, [
            (row["job"],
             format_number(row["level"] + 1, 0),
             format_number(row["headcount"], 0),
             format_money(row["minimum"], currency)
             if row["minimum"] is not None else "—",
             format_money(row["median"], currency)
             if row["median"] is not None else "—",
             format_money(row["mean"], currency)
             if row["mean"] is not None else "—",
             format_money(row["maximum"], currency)
             if row["maximum"] is not None else "—")
            for row in jobs])

        self.org_chart.set_tree(nodes, currency)
        self.org_chart.select(None)
        lignes = []
        for row in rows:
            identité = self._identity(row["employee_id"])
            if row.get("out_of_scope"):
                # Le responsable choisi que les filtres ont retire : il
                # reste la racine du dessin, mais il n'est pas dans la
                # population analysee, et la ligne doit le dire.
                identité += "  (hors filtre)"
            rattachement = (self._identity(row["manager"])
                            if row.get("manager") else "—")
            lignes.append((
                "· " * row["level"] + identité,
                row.get("job") or "—",
                format_number(row["level"] + 1, 0),
                rattachement,
                format_years(row.get("age_years")),
                format_years(row.get("tenure_years")),
                format_money(row["amount"], currency)
                if row.get("amount") is not None else "masquée",
                # Le rang seul ne se lit pas : « 4 » ne dit rien, « 4 / 57 »
                # situe la personne dans son equipe.
                f'{row["rank"]} / {row["ranked"]}'
                if row.get("rank") else "—",
            ))
            # Deux matricules par ligne : celui du salarie, et celui de la
            # case qui le porte — un salarie sans equipe n'a pas de case a
            # lui, il est compte sous celle de son responsable.
            self._org_keys[str(len(lignes) - 1)] = (
                row["employee_id"],
                row["employee_id"] if row["manages"] else row.get("manager"))
        self._fill(self.org_tree, lignes)

        explication = ("Le rang classe la rémunération dans l'équipe, 1 pour "
                       "la plus élevée. Dans l'organigramme, seuls les "
                       "responsables ont une case ; ceux qui n'encadrent "
                       "personne sont comptés sous celle de leur responsable. "
                       "Cliquez une case pour retrouver la personne dans la "
                       "liste, et l'inverse.")
        # La base de comparaison s'annonce, elle ne se devine pas : les
        # montants d'une page a temps plein et ceux d'une page qui retombe
        # sur le verse ne se lisent pas de la meme facon.
        explication += (" Les rémunérations sont ramenées au temps plein."
                        if resume.get("full_time") else
                        " Le temps de travail n'est renseigné pour personne : "
                        "les rémunérations sont celles qui sont versées, et "
                        "un temps partiel y compte pour ce qu'il perçoit.")
        if scope.get("filtered"):
            explication += (" Les filtres s'appliquent ici comme ailleurs : "
                            "les salariés écartés ne sont plus comptés, et "
                            "ceux dont le responsable l'a été se rattachent "
                            "au premier responsable restant au-dessus d'eux.")
        if resume.get("masked"):
            explication += (" Les médianes sont masquées : l'effectif dont la "
                            "rémunération est calculable n'atteint pas le "
                            "seuil de publication.")
        self.org_note.configure(text=explication)
        return True

    def _clear_org(self, raison: str = "") -> None:
        """Vide la page, en disant pourquoi.

        Une analyse sans equipe ne doit pas laisser en place
        l'organigramme de la precedente a cote de chiffres qui ne sont
        plus les siens. Mais une page vide sans un mot ne se distingue pas
        d'une page en panne : la raison s'ecrit a la place du dessin.
        """
        self.org_chart.set_tree(None)
        self._fill(self.org_jobs, [])
        self._fill(self.org_tree, [])
        self.org_note.configure(text=raison)

    def _on_org_node(self, node: Dict[str, Any]) -> None:
        """Une case choisie dans le dessin : la ligne correspondante se
        selectionne dans la liste, et la liste s'y rend."""
        self.org_chart.select(node.get("manager"))
        for item, (key, _case) in self._org_keys.items():
            if key == node.get("manager"):
                enfants = self.org_tree.get_children()
                index = int(item)
                if index < len(enfants):
                    cible = enfants[index]
                    self.org_tree.selection_set(cible)
                    self.org_tree.see(cible)
                return

    def _on_org_row(self, _event=None) -> None:
        """Une ligne choisie dans la liste : la case de son responsable
        s'allume. Un salarie sans equipe n'a pas de case a lui — c'est
        celle sous laquelle il est compte que l'on cherche."""
        selection = self.org_tree.selection()
        if not selection:
            return
        enfants = list(self.org_tree.get_children())
        try:
            index = enfants.index(selection[0])
        except ValueError:
            return
        self.org_chart.select(self._org_keys.get(str(index), (None, None))[1])

    # --------------------------------------------- comparatif femmes / hommes

    #: Premiere entree du selecteur de poste : la page porte alors sur toute
    #: la population analysee. Sans elle, on ne pourrait plus revenir a la
    #: comparaison d'ensemble une fois un poste ouvert.
    EQUITY_ALL = "(tous les postes)"

    #: Lignes du tableau de gauche : intitule, cle du moteur, nature.
    EQUITY_ROWS = (
        ("Effectif comparé", "valued_headcount", "count"),
        ("Minimum", "min", "money"),
        ("P10", "p10", "money"),
        ("Q1 (P25)", "p25", "money"),
        ("Médiane (P50)", "median", "money"),
        ("Moyenne", "mean", "money"),
        ("Q3 (P75)", "p75", "money"),
        ("P90", "p90", "money"),
        ("Maximum", "max", "money"),
    )

    def _build_equity(self, parent: tk.Frame) -> None:
        """Le comparatif femmes / hommes, de haut en bas.

        Un poste en tete, puis cinq blocs qui en decoulent : qui compose la
        population, comment elle se repartit sur deux axes au choix, ce que
        disent les quartiles de chaque sexe, ou se situe chaque poste, et
        enfin qui decroche de la mediane de son groupe.
        """
        self.equity_page = self._scrolling_page(parent)
        page = self.equity_page

        # --- Le poste ----------------------------------------------------
        tete = tk.Frame(page, background=theme.CANVAS)
        tete.pack(fill="x", padx=24, pady=(18, 4))
        tk.Label(tete, text="POSTE", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")
        self.equity_job = ttk.Combobox(tete, state="readonly", width=34,
                                       font=self.fonts.small)
        self.equity_job.pack(side="left", padx=10)
        self.equity_job.bind("<<ComboboxSelected>>",
                             lambda _e: self._show_equity_scope())
        self.equity_scope_note = tk.Label(
            tete, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small)
        self.equity_scope_note.pack(side="left", padx=(16, 0))

        self.equity_warning = tk.Label(
            page, text="", background=theme.CANVAS, foreground=theme.WARN,
            font=self.fonts.body, justify="left", anchor="w", wraplength=900)

        # --- 1. L'effectif, et la pyramide des ages ----------------------
        self._equity_rule()
        haut = tk.Frame(page, background=theme.CANVAS)
        haut.pack(fill="x", padx=24)
        # Trois colonnes egales, et non trois colonnes qui se partagent le
        # surplus : « pack » donne a chacune la largeur de son contenu puis
        # repartit le reste, et la pyramide des ages — six tranches contre
        # dix — heritait d'une colonne trop etroite pour etre tracee.
        # Le tableau des effectifs porte quatre colonnes chiffrees et
        # demande deux fois la place d'une pyramide : des tiers stricts le
        # rabotaient — « Ancienneté médian… », « ENSEM… ». Les poids
        # disent ce que chacun reclame.
        for colonne, poids in enumerate((2, 1, 1)):
            haut.columnconfigure(colonne, weight=poids, uniform="equite")
        gauche = tk.Frame(haut, background=theme.CANVAS)
        gauche.grid(row=0, column=0, sticky="nsew")
        milieu = tk.Frame(haut, background=theme.CANVAS)
        milieu.grid(row=0, column=1, sticky="nsew", padx=(24, 0))
        droite = tk.Frame(haut, background=theme.CANVAS)
        droite.grid(row=0, column=2, sticky="nsew", padx=(24, 0))
        self._equity_title(gauche, "Effectifs")
        self.equity_people = self._tree(
            gauche, ("Indicateur", "Femmes", "Hommes", "Ensemble"),
            (190, 95, 95, 95), expand=False, height=5)
        # Deux pyramides et non une : l'age dit qui est la, l'anciennete dit
        # depuis quand. Un ecart de remuneration ne se lit pas pareil selon
        # que les deux sexes ont la meme anciennete ou non — le premier cas
        # appelle une revalorisation, le second une revue de la grille.
        self._equity_title(milieu, "Pyramide des âges")
        self.equity_pyramid = PyramidChart(milieu)
        self.equity_pyramid.pack(fill="x", padx=18, pady=(0, 10))
        self.equity_pyramid_note = tk.Label(
            milieu, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, justify="left", anchor="w", wraplength=380)
        self.equity_pyramid_note.pack(anchor="w", padx=18, pady=(0, 8))
        self._equity_title(droite, "Structure d'ancienneté")
        self.equity_tenure = PyramidChart(droite)
        self.equity_tenure.pack(fill="x", padx=18, pady=(0, 10))
        self.equity_tenure_note = tk.Label(
            droite, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, justify="left", anchor="w", wraplength=380)
        self.equity_tenure_note.pack(anchor="w", padx=18, pady=(0, 8))

        # --- 2. Le nuage, sur deux axes au choix -------------------------
        self._equity_rule()
        self._equity_title(page, "Nuage de points")
        axes = tk.Frame(page, background=theme.CANVAS)
        axes.pack(fill="x", padx=24, pady=(0, 4))
        self.equity_x = self._axis_box(axes, "EN ABSCISSE",
                                       command=self._reaxis_equity)
        self.equity_y = self._axis_box(axes, "EN ORDONNÉE",
                                       command=self._reaxis_equity)
        ttk.Button(axes, text="Réinitialiser le graphique",
                   style="Ghost.TButton",
                   command=self._reset_equity_scatter).pack(side="left")
        self.equity_scatter = ScatterChart(page)
        self.equity_scatter.identify = self._identity_of
        self.equity_scatter.configure(height=self.EQUITY_SCATTER_HEIGHT)
        self.equity_scatter.pack_propagate(False)
        self.equity_scatter.pack(fill="x", padx=24, pady=(0, 4))
        self.equity_legend = tk.Frame(page, background=theme.CANVAS)
        self.equity_legend.pack(fill="x", padx=24, pady=(0, 2))
        self.equity_scatter_note = tk.Label(
            page, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, justify="left", anchor="w", wraplength=980)
        self.equity_scatter_note.pack(anchor="w", padx=24, pady=(0, 8))

        # --- 3. Les quartiles, et la boite a moustaches ------------------
        self._equity_rule()
        bas = tk.Frame(page, background=theme.CANVAS)
        bas.pack(fill="x", padx=24)
        for colonne in range(2):
            bas.columnconfigure(colonne, weight=1, uniform="equite-bas")
        colonne_g = tk.Frame(bas, background=theme.CANVAS)
        colonne_g.grid(row=0, column=0, sticky="nsew")
        colonne_d = tk.Frame(bas, background=theme.CANVAS)
        colonne_d.grid(row=0, column=1, sticky="nsew", padx=(24, 0))
        self._equity_title(colonne_g, "Rémunération comparée")
        self.equity_stats = self._tree(
            colonne_g, ("Indicateur", "Femmes", "Hommes", "Ensemble"),
            (220, 110, 110, 110), expand=False, height=10)
        self.equity_stats_note = tk.Label(
            colonne_g, text="", background=theme.CANVAS,
            foreground=theme.MUTED, font=self.fonts.small, justify="left",
            anchor="w", wraplength=460)
        self.equity_stats_note.pack(anchor="w", padx=18, pady=(0, 8))
        self._equity_title(colonne_d, "Dispersion")
        self.equity_box = BoxPlotChart(colonne_d)
        # Une seule paire de boites a tracer : la ligne peut s'etaler, et
        # c'est tout l'interet d'un gros trace — les moustaches se lisent.
        self.equity_box.ROW_MAX = self.EQUITY_BOX_ROW
        self.equity_box.ROW_SPLIT_MIN = self.EQUITY_BOX_ROW
        self.equity_box.pack(fill="both", expand=True, padx=18, pady=(0, 10))

        # --- 4. Le recapitulatif par poste -------------------------------
        self._equity_rule()
        self._equity_title(page, "Récapitulatif par poste")
        self.equity_recap = self._tree(
            page, ("Poste", "Femmes", "Hommes", "Médiane femmes",
                   "Médiane hommes", "Écart"),
            (260, 90, 90, 150, 150, 110), expand=False, height=12)
        self.equity_recap_note = tk.Label(
            page, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, justify="left", anchor="w", wraplength=980)
        self.equity_recap_note.pack(anchor="w", padx=24, pady=(0, 8))

        # --- 5. Les salaries sous la mediane de leur poste ---------------
        self._equity_rule()
        self._equity_title(page, "Population analysée")
        # Le tableau se construit a l'analyse : ses colonnes sont declarees
        # au parametrage, et elles changent d'un fichier a l'autre.
        self.equity_people_frame = tk.Frame(page, background=theme.CANVAS)
        self.equity_people_frame.pack(fill="x")
        self.equity_list = None
        self._equity_columns: List[str] = []
        self.equity_lagging_note = tk.Label(
            page, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, justify="left", anchor="w", wraplength=980)
        self.equity_lagging_note.pack(anchor="w", padx=24, pady=(2, 24))

    #: Hauteur du nuage de cette page. Il est « petit » : la page en porte
    #: cinq autres, et un nuage pleine page les renverrait sous la ligne de
    #: flottaison.
    EQUITY_SCATTER_HEIGHT = 300
    #: Hauteur de la ligne du gros trace.
    EQUITY_BOX_ROW = 120

    def _equity_title(self, parent: tk.Widget, texte: str) -> None:
        tk.Label(parent, text=texte, background=theme.CANVAS,
                 foreground=theme.INK, font=self.fonts.section).pack(
                     anchor="w", padx=18, pady=(0, 8))

    def _equity_rule(self) -> None:
        """Un filet entre deux blocs : sans lui, cinq blocs empiles se
        lisent comme une seule longue page."""
        tk.Frame(self.equity_page, background=theme.LINE, height=1).pack(
            fill="x", padx=24, pady=(14, 12))

    def _show_pay_equity(self, equity: Dict[str, Any]) -> None:
        """Remplit la page : la liste des postes, puis les cinq blocs."""
        self._equity_field = equity.get("category_field") or "job_title"
        if not equity.get("available"):
            self.equity_warning.configure(text=equity.get("warning") or "")
            self.equity_warning.pack(anchor="w", padx=24, pady=(8, 0))
            self.equity_job.configure(values=[self.EQUITY_ALL])
            self.equity_job.current(0)
            self._clear_equity()
            return
        self.equity_warning.pack_forget()
        postes = sorted({str(employee.value(self._equity_field) or "")
                         for employee in self.result.filtered} - {""})
        self.equity_job.configure(values=[self.EQUITY_ALL] + postes)
        if self.equity_job.get() not in [self.EQUITY_ALL] + postes:
            self.equity_job.current(0)
        self._scatter_axes = metrics.scatter_axes(self.configuration)
        self._fill_axis_box(self.equity_x, self.configuration.get(
            "chart_parameters.scatter_x", "tenure_years"))
        self._fill_axis_box(self.equity_y, self.configuration.get(
            "chart_parameters.scatter_y", "base_salary"))
        self._show_equity_recap()
        self._show_equity_scope()

    def _equity_choice(self) -> Optional[str]:
        """Le poste retenu, ou rien si la page porte sur l'ensemble."""
        choix = self.equity_job.get()
        return None if not choix or choix == self.EQUITY_ALL else choix

    def _equity_population(self):
        """La population sur laquelle portent les blocs du haut.

        Les bandes d'age et d'anciennete sont celles de la population
        entiere : recoupees sur un poste, elles changeraient d'un poste a
        l'autre et deux pyramides ne se compareraient plus.
        """
        from ..core.normalize import Population

        entiere = self.result.filtered
        poste = self._equity_choice()
        if poste is None:
            return entiere
        gens = category_members(entiere, self._equity_field, poste)
        return Population(employees=list(gens),
                          age_bands=entiere.age_bands,
                          tenure_bands=entiere.tenure_bands)

    def _clear_equity(self) -> None:
        """Vide les cinq blocs d'un coup."""
        arbres = [self.equity_people, self.equity_stats, self.equity_recap]
        # La liste nominative n'existe qu'une fois les colonnes connues :
        # elle se construit a l'analyse, et il n'y a rien a vider avant.
        if self.equity_list is not None:
            arbres.append(self.equity_list)
        for arbre in arbres:
            self._fill(arbre, [])
        self.equity_pyramid.set_rows([])
        self.equity_tenure.set_rows([])
        self.equity_box.set_rows([])
        self.equity_scatter.set_dataset({})
        for child in self.equity_legend.winfo_children():
            child.destroy()
        for note in (self.equity_scope_note, self.equity_pyramid_note,
                     self.equity_tenure_note, self.equity_scatter_note,
                     self.equity_stats_note, self.equity_recap_note,
                     self.equity_lagging_note):
            note.configure(text="")

    def _show_equity_scope(self) -> None:
        """Rejoue les quatre blocs qui dependent du poste retenu.

        Le recapitulatif, lui, ne bouge pas : il porte sur tous les postes,
        et c'est ce qui permet de situer celui qu'on regarde.
        """
        if self.result is None:
            return
        population = self._equity_population()
        poste = self._equity_choice()
        self.equity_scope_note.configure(
            text=f"{len(population)} salariés"
                 + ("" if poste else " · toute la population analysée"))
        self._show_equity_people(population)
        self._reaxis_equity()
        self._show_equity_stats(poste)
        self._show_equity_lagging(poste)

    def _show_equity_people(self, population) -> None:
        """Effectifs et pyramide des ages, femmes et hommes cote a cote."""
        from ..core.normalize import Population

        devise = self.result.payload["salary"].get("currency", "EUR")
        parts = {"female": [], "male": []}
        for employee in population:
            sexe = metrics._sex_of(employee, self.result.config)
            if sexe in parts:
                parts[sexe].append(employee)

        def bloc(gens):
            sous = Population(employees=list(gens),
                              age_bands=population.age_bands,
                              tenure_bands=population.tenure_bands)
            return metrics.calculate_population_metrics(sous,
                                                        self.result.config)

        femmes, hommes = bloc(parts["female"]), bloc(parts["male"])
        ensemble = bloc(list(population))
        total = len(population) or 1
        self._fill(self.equity_people, [
            ("Effectif", str(len(parts["female"])), str(len(parts["male"])),
             str(len(population))),
            ("Part", format_percent(len(parts["female"]) / total * 100, 0),
             format_percent(len(parts["male"]) / total * 100, 0), "100 %"),
            ("Âge médian", format_years(femmes.get("age_median")),
             format_years(hommes.get("age_median")),
             format_years(ensemble.get("age_median"))),
            ("Ancienneté médiane", format_years(femmes.get("tenure_median")),
             format_years(hommes.get("tenure_median")),
             format_years(ensemble.get("tenure_median"))),
        ])
        self.equity_pyramid.set_rows(ensemble.get("age_bands", []))
        self.equity_tenure.set_rows(ensemble.get("tenure_bands", []))
        inconnus = len(population) - len(parts["female"]) - len(parts["male"])
        avis = (f"{inconnus} salarié(s) sans sexe renseigné, hors pyramide."
                if inconnus else "")
        self.equity_pyramid_note.configure(text=avis)
        self.equity_tenure_note.configure(text=avis)

    def _reaxis_equity(self) -> None:
        """Recalcule le nuage de cette page, sur les deux axes choisis.

        Le calcul est refait par le moteur, jamais par l'ecran. La couleur,
        elle, est imposee : c'est le sexe — un comparatif femmes / hommes
        colorie par business unit ne comparerait rien.
        """
        if self.result is None or not getattr(self, "_scatter_axes", None):
            return
        champs = [axis["field"] for axis in self._scatter_axes]
        data = self.configuration.as_dict()
        for box, clef in ((self.equity_x, "scatter_x"),
                          (self.equity_y, "scatter_y")):
            index = box.current()
            if 0 <= index < len(champs):
                data["chart_parameters"][clef] = champs[index]
        data["chart_parameters"]["scatter_color_by"] = \
            self.configuration.get("pay_equity_parameters.gender_field",
                                   "gender")
        dataset = metrics.scatter_dataset(self._equity_population(),
                                          Configuration(data))
        self.equity_scatter.set_dataset(
            dataset, self.result.payload["salary"].get("currency", "EUR"))
        self.equity_scatter.set_series(self._equity_colours(dataset))
        self._equity_legend_row(dataset)
        # Un nuage vide sans un mot passe pour une panne. Le moteur dit
        # pourquoi il refuse — l'effectif du poste, le plus souvent.
        self.equity_scatter_note.configure(
            text="" if dataset.get("available")
                 else (dataset.get("warning") or ""))

    def _equity_colours(self, dataset: Dict[str, Any]) -> Dict[str, str]:
        """Les teintes du nuage : celles des femmes et des hommes.

        Les modalites sont les ecritures du fichier — « F », « Femme »,
        « M »... — et c'est le moteur qui sait les lire. La fenetre ne
        redecide pas de ce qu'est une femme.
        """
        from ..core.pay_equity import FEMALE, MALE, classify

        section = self.configuration.section("pay_equity_parameters")
        femmes = section.get("female_values", []) or []
        hommes = section.get("male_values", []) or []
        teintes = {}
        for groupe in dataset.get("groups") or []:
            trouve = classify(groupe, femmes, hommes)
            teintes[groupe] = (theme.FEMALE if trouve == FEMALE else
                               theme.MALE if trouve == MALE else theme.FAINT)
        return teintes

    def _equity_legend_row(self, dataset: Dict[str, Any]) -> None:
        """Deux pastilles sous le nuage. Sans elles, deux couleurs ne
        disent rien — et celles-ci sont le sujet de la page."""
        for child in self.equity_legend.winfo_children():
            child.destroy()
        from ..core.pay_equity import FEMALE, MALE, classify

        section = self.configuration.section("pay_equity_parameters")
        femmes = section.get("female_values", []) or []
        hommes = section.get("male_values", []) or []
        teintes = self._equity_colours(dataset)
        # « F » et « H » sont les écritures du fichier ; la page dit
        # « Femmes » et « Hommes » partout ailleurs, et les femmes y passent
        # en premier. Une légende qui emploie un autre vocabulaire que le
        # graphique d'à côté fait douter qu'il s'agisse de la même chose.
        rang = {FEMALE: 0, MALE: 1}
        groupes = sorted(dataset.get("groups") or [],
                         key=lambda g: rang.get(classify(g, femmes, hommes), 2))
        for groupe in groupes:
            trouve = classify(groupe, femmes, hommes)
            libelle = {FEMALE: "Femmes", MALE: "Hommes"}.get(trouve,
                                                            str(groupe))
            case = tk.Frame(self.equity_legend, background=theme.CANVAS)
            case.pack(side="left", padx=(0, 18))
            tk.Frame(case, background=teintes.get(groupe, theme.FAINT),
                     width=12, height=12).pack(side="left", pady=2)
            tk.Label(case, text=libelle, background=theme.CANVAS,
                     foreground=theme.MUTED,
                     font=self.fonts.small).pack(side="left", padx=(6, 0))

    def _reset_equity_scatter(self) -> None:
        """Rend au nuage ses axes d'origine, ceux du parametrage."""
        if self.result is None:
            return
        self._fill_axis_box(self.equity_x, self.configuration.get(
            "chart_parameters.scatter_x", "tenure_years"))
        self._fill_axis_box(self.equity_y, self.configuration.get(
            "chart_parameters.scatter_y", "base_salary"))
        self._reaxis_equity()
        self.equity_scatter.reset_view()

    def _show_equity_stats(self, poste: Optional[str]) -> None:
        """Les quartiles des deux sexes, et le gros trace en regard.

        Les deux lisent le meme decoupage : un tableau et un graphique qui
        se contrediraient a l'ecran seraient pires que l'un des deux seul.
        """
        devise = self.result.payload["salary"].get("currency", "EUR")
        bloc = (population_breakdown(self.result.filtered, self.result.config)
                if poste is None
                else category_breakdown(self.result.filtered,
                                        self.result.config,
                                        self._equity_field, poste))
        colonnes = {c["key"]: c for c in bloc["columns"]}

        def valeur(cle, mesure, nature):
            colonne = colonnes.get(cle) or {}
            if colonne.get("masked"):
                return "masqué"
            montant = (colonne.get("salary") or {}).get(mesure)
            if montant is None:
                return "—"
            return (str(int(montant)) if nature == "count"
                    else format_money(montant, devise))

        self._fill(self.equity_stats, [
            (libelle, valeur("female", mesure, nature),
             valeur("male", mesure, nature), valeur("all", mesure, nature))
            for libelle, mesure, nature in self.EQUITY_ROWS])
        # Une seule ligne sous le tableau. Les trois phrases s'y
        # repliaient sur deux ou trois lignes dans une demi-colonne, et le
        # tableau se mettait a flotter au-dessus d'un paragraphe. Les
        # separateurs remplacent les points : c'est la meme information,
        # dans la place d'un intitule.
        notes = []
        if bloc.get("mean_gap") is not None:
            notes.append(f'Écart moyenne {_signed_percent(bloc["mean_gap"])}'
                         f' · médiane {_signed_percent(bloc["median_gap"])}')
        base = (bloc.get("basis") or {}).get("label") or ""
        if base:
            notes.append(base)
        if bloc.get("warning"):
            notes.append(bloc["warning"])
        self.equity_stats_note.configure(text=" · ".join(notes))

        # Une seule ligne, toujours : la paire du poste retenu, ou celle de
        # toute la population. Tracer les trente-neuf postes a cote d'un
        # tableau qui n'en decrit qu'un ferait lire deux choses differentes
        # dans deux colonnes voisines.
        if poste is None:
            lignes = metrics.sex_pair(self.result.filtered, self.result.config,
                                      label="Toute la population")
        else:
            lignes = [ligne for ligne
                      in metrics.segment_by_sex(self.result.filtered,
                                                self.result.config,
                                                self._equity_field)
                      if str(ligne.get("segment")) == str(poste)]
        self.equity_box.set_split(True)
        self.equity_box.set_rows(
            lignes, devise,
            reference=self.result.payload["salary"].get("median"),
            alert=self.configuration.number(
                "pay_equity_parameters.gap_alert_threshold", 5.0,
                minimum=0.0, maximum=100.0))

    def _show_equity_recap(self) -> None:
        """Un poste par ligne : effectifs, les deux medianes, l'ecart."""
        devise = self.result.payload["salary"].get("currency", "EUR")
        bloc = calculate_category_gaps(self.result.filtered,
                                       self.result.config,
                                       self._equity_field)
        lignes = []
        retenus = 0
        for item in sorted(bloc.get("categories", []),
                           key=lambda c: -(c.get("median_gap") or -1e9)):
            if not item.get("published"):
                retenus += 1
                lignes.append((item["category"], str(item.get("female_count", 0)),
                               str(item.get("male_count", 0)), "masqué",
                               "masqué", "—"))
                continue
            lignes.append((
                item["category"], str(item.get("female_count", 0)),
                str(item.get("male_count", 0)),
                format_money(item.get("female_median"), devise),
                format_money(item.get("male_median"), devise),
                _signed_percent(item.get("median_gap"))))
        self._fill(self.equity_recap, lignes)
        note = ["Écart de médiane, positif quand les hommes sont mieux "
                "rémunérés. Classement par écart décroissant."]
        if retenus:
            note.append(f"{retenus} poste(s) sans écart publiable : effectif "
                        "insuffisant d'un côté au moins.")
        self.equity_recap_note.configure(text=" ".join(note))

    def _show_equity_lagging(self, poste: Optional[str]) -> None:
        """La population analysée, une ligne par salarié.

        Les colonnes viennent du paramétrage : ajouter « Direction » ou
        retirer l'établissement ne demande aucune modification ici. Les
        champs nominatifs font exception — le moteur n'en transporte
        jamais, et c'est la fenêtre qui les résout, sous le réglage
        d'affichage des identités.
        """
        devise = self.result.payload["salary"].get("currency", "EUR")
        bloc = people_rows(self.result.filtered, self.result.config,
                           self._equity_field, poste)
        colonnes = bloc["columns"]
        if self.equity_list is None or self._equity_columns != [
                colonne["field"] for colonne in colonnes]:
            self._equity_columns = [colonne["field"] for colonne in colonnes]
            for child in self.equity_people_frame.winfo_children():
                child.destroy()
            montants = {axis["field"] for axis in metrics.scatter_axes(
                self.configuration)}
            self.equity_list = self._tree(
                self.equity_people_frame,
                tuple(colonne["label"] for colonne in colonnes),
                tuple(colonne["width"] for colonne in colonnes),
                expand=False, height=self.EQUITY_LIST_ROWS,
                # Un nombre se cale a droite, un libelle a gauche : « Nom »
                # est un mot, et sa largeur ne dit rien de sa nature.
                anchors=tuple("e" if colonne["field"] in montants else "w"
                              for colonne in colonnes))
        personnels = set(bloc["personal_fields"])
        montants = {axis["field"] for axis in metrics.scatter_axes(
            self.configuration) if axis.get("kind") == "money"}

        def cellule(ligne, colonne):
            champ = colonne["field"]
            if champ in personnels:
                # Resolu par la fenetre, jamais par le moteur.
                return self._identity_part(ligne["row"], champ)
            valeur = ligne["values"].get(champ)
            if valeur is None or valeur == "":
                return "—"
            if champ in montants:
                return format_money(valeur, devise)
            return str(valeur)

        self._fill(self.equity_list, [
            tuple(cellule(ligne, colonne) for colonne in colonnes)
            for ligne in bloc["rows"][:self.EQUITY_LIST_MAX]])
        note = [f'{bloc["headcount"]} salariés dans le périmètre analysé.']
        if bloc["headcount"] > self.EQUITY_LIST_MAX:
            note.append(f"Les {self.EQUITY_LIST_MAX} premiers sont affichés.")
        # Le chemin du reglage ne figure plus ici : « Paramètres →
        # pay_equity_parameters.people_columns » s'adressait a qui edite un
        # JSON, pas a qui lit une liste de salaries.
        #
        # La mention « ces noms restent a l'ecran » non plus. La regle n'a
        # pas bouge — aucun document, aucun export, aucun journal n'en
        # porte, et les tests le tiennent —, mais elle se rappelait sous
        # chaque analyse a quelqu'un qui la connait, et une garantie
        # repetee finit par ressembler a un avertissement.
        self.equity_lagging_note.configure(text=" ".join(note))

    #: Hauteur maximale de la liste, en lignes, et nombre de lignes au-dela
    #: duquel on cesse d'en poser dans le tableau : trente mille lignes
    #: dans un Treeview prennent huit secondes a inserer — mesure faite.
    EQUITY_LIST_ROWS = 18
    EQUITY_LIST_MAX = 500

    def _identity_part(self, row: Optional[int], field: str) -> str:
        """Un champ nominatif, resolu depuis la population detenue.

        Sous le reglage « ne pas montrer les identites », la reference
        anonyme prend la place du nom — une seule fois, sur la colonne qui
        vient en premier, pour ne pas la repeter sur chaque champ.
        """
        if row is None or self.population is None:
            return "—"
        montrer = self.configuration.get(
            "privacy_parameters.show_identities_on_screen", True)
        for employee in self.population:
            if employee.row_number != row:
                continue
            if not montrer:
                return (employee.anonymous_id or str(row)
                        if field == self._equity_columns[0] else "—")
            return str(employee.value(field) or "—")
        return "—"














    # ------------------------------------------------ fiche d'un groupe











    #: Les lignes du tableau : intitule, cle de la mesure, nature.

    #: Les rapports de dispersion, qui vivent dans un sous-dictionnaire.




    def _axis_box(self, parent: tk.Frame, label: str,
                  command=None) -> ttk.Combobox:
        """Un selecteur d'axe : son intitule, sa liste.

        Le rappel se passe en argument : deux pages portent un nuage, et
        chacune recalcule le sien. Une seconde liste de champs aurait fini
        par differer de celle-ci.
        """
        tk.Label(parent, text=label, background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left", padx=(0, 0))
        box = ttk.Combobox(parent, state="readonly", width=18,
                           font=self.fonts.small)
        box.pack(side="left", padx=(10, 16))
        rappel = command or self._reaxis
        box.bind("<<ComboboxSelected>>", lambda _e: rappel())
        return box

    def _fill_axis_box(self, box: ttk.Combobox, field: str) -> None:
        box.configure(values=[axis["label"] for axis in self._scatter_axes])
        champs = [axis["field"] for axis in self._scatter_axes]
        if field in champs:
            box.current(champs.index(field))
        elif champs:
            box.current(0)

    def _reset_scatter(self) -> None:
        """Rend au nuage ses axes, sa couleur et son cadrage d'origine.

        Les trois viennent du parametrage — `chart_parameters` —, jamais de
        valeurs ecrites ici : un fichier qui declare d'autres axes par
        defaut doit les retrouver, et non l'anciennete et le salaire de base
        de la configuration livree.
        """
        if not self.result:
            return
        defauts = (
            (self.x_choice, self.configuration.get(
                "chart_parameters.scatter_x", "tenure_years")),
            (self.y_choice, self.configuration.get(
                "chart_parameters.scatter_y", "base_salary")),
        )
        for boite, champ in defauts:
            self._fill_axis_box(boite, champ)
        couleur = self.configuration.get("chart_parameters.scatter_color_by",
                                         "business_unit")
        champs = getattr(self, "_colour_fields", [])
        if couleur in champs:
            self.colour_choice.current(champs.index(couleur))
        self._reaxis()
        self.scatter.reset_view()

    def _reaxis(self) -> None:
        """Recalcule le nuage sur les deux axes choisis.

        Le calcul est refait par le moteur, jamais par l'ecran : les points
        affiches et ceux des documents viennent du meme endroit, et
        l'echantillonnage comme le regroupement des couleurs restent les
        memes.
        """
        if not self.result or not getattr(self, "_scatter_axes", None):
            return
        champs = [axis["field"] for axis in self._scatter_axes]
        data = self.configuration.as_dict()
        for box, clef in ((self.x_choice, "scatter_x"),
                          (self.y_choice, "scatter_y")):
            index = box.current()
            if 0 <= index < len(champs):
                data["chart_parameters"][clef] = champs[index]
        index = self.colour_choice.current()
        if 0 <= index < len(getattr(self, "_colour_fields", [])):
            data["chart_parameters"]["scatter_color_by"] = \
                self._colour_fields[index]
        dataset = metrics.scatter_dataset(self.result.filtered,
                                          Configuration(data))
        self.scatter.set_dataset(
            dataset, self.result.payload["salary"].get("currency", "EUR"))
        self._build_legend()

    def _show_scatter(self, dataset: Dict[str, Any], currency: str) -> None:
        self._scatter_axes = metrics.scatter_axes(self.configuration)
        self._fill_axis_box(self.x_choice, dataset.get("x_field", ""))
        self._fill_axis_box(self.y_choice, dataset.get("y_field", ""))
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

        Meme chemin que le changement d'axe : un seul calcul, trois
        entrees. Deux chemins auraient fini par ne plus poser les memes
        parametres, et le nuage aurait change de forme en changeant de
        couleur.
        """
        self._reaxis()

    #: Largeur reservee a une pastille et a ses marges, en pixels. Mesuree
    #: sur la legende : 9 px de rond, 5 d'ecart, 14 de separation.
    LEGEND_CHIP_PADDING = 28

    def _build_legend(self) -> None:
        """Legende du nuage : une pastille par modalite, repliee si besoin.

        Elle disparaissait au-dela de seize modalites — le nuage restait
        colore, mais plus rien ne disait de quoi. Le moteur en limite
        desormais le nombre ; il reste a ne pas dependre d'une seule ligne,
        car « Responsable administratif et financier » en occupe le quart a
        lui seul. Les pastilles sont donc reparties sur autant de lignes
        que la largeur en impose, mesurees et non estimees.
        """
        self._legend_groups = self.scatter.dataset.get("groups") or []
        self._legend_width = 0
        self._flow_legend()

    def _flow_legend(self) -> None:
        for child in self.legend_frame.winfo_children():
            child.destroy()
        groups = getattr(self, "_legend_groups", [])
        if not groups:
            return
        available = self.legend_frame.winfo_width()
        if available < 60:
            # Avant le premier calcul de geometrie, Tk annonce un pixel : on
            # depose tout sur une ligne, le « Configure » qui suit repliera.
            available = 10 ** 6
        self._legend_width = available
        colours = palette.series_map(
            groups, theme.ACTIVE.series,
            other=self.scatter.dataset.get("other_label"), neutral=theme.FAINT)
        ligne = tk.Frame(self.legend_frame, background=theme.CANVAS)
        ligne.pack(fill="x", anchor="w")
        tk.Label(ligne, text="MASQUER", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left", padx=(0, 10))
        reste = available - self.fonts.label.measure("MASQUER") - 10
        for group in groups:
            largeur = self.fonts.small.measure(group) + self.LEGEND_CHIP_PADDING
            if largeur > reste and ligne.winfo_children():
                ligne = tk.Frame(self.legend_frame, background=theme.CANVAS)
                ligne.pack(fill="x", anchor="w", pady=(4, 0))
                reste = available
            reste -= largeur
            chip = tk.Frame(ligne, background=theme.CANVAS, cursor="hand2")
            chip.pack(side="left", padx=(0, 14))
            dot = tk.Canvas(chip, width=9, height=9, background=theme.CANVAS,
                            highlightthickness=0)
            dot.create_oval(1, 1, 8, 8, fill=colours[group], outline="")
            dot.pack(side="left", pady=(1, 0))
            text = tk.Label(chip, text=group, background=theme.CANVAS,
                            foreground=theme.INK_SOFT, font=self.fonts.small)
            text.pack(side="left", padx=(5, 0))
            for widget in (chip, dot, text):
                widget.bind("<Button-1>", lambda _e, g=group, t=text, d=dot:
                            self._toggle_group(g, t, d))

    def _on_legend_resize(self, event) -> None:
        """Replie la legende quand la fenetre change de largeur.

        Le repli detruit et recree les pastilles, ce qui provoque un
        « Configure » : sans la comparaison de largeur, la legende se
        reconstruirait sans fin.
        """
        if abs(event.width - getattr(self, "_legend_width", 0)) > 2:
            self._flow_legend()

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

    def _identity(self, employee_id: str) -> str:
        """Identite lisible d'un matricule, pour l'ecran et lui seul.

        Elle se lit dans la population que la fenetre detient deja : le
        resultat d'analyse n'en porte aucune, et c'est ce qui garantit
        qu'aucun document produit ne peut en porter non plus. A defaut, le
        matricule tel qu'il a ete saisi.
        """
        if not employee_id or self.population is None:
            return employee_id
        if not self.configuration.get(
                "privacy_parameters.show_identities_on_screen", True):
            return employee_id
        for employee in self.population:
            if employee.employee_id == employee_id:
                return employee.identity or employee_id
        return employee_id

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
        self.col_choice.configure(values=labels)
        if labels:
            self.box_choice.current(self._default_dimension())
            self.col_choice.current(self._default_dimension())
            self._show_boxes()
            self._show_columns()
        else:
            self.boxplot.set_rows([])
            self.column_boxes.set_rows([])

    def _default_dimension(self) -> int:
        """Dimension proposee d'emblee sur la dispersion : le poste.

        C'est l'axe sur lequel une comparaison de remuneration se fait le
        plus souvent — « travail de meme valeur » se lit d'abord la. La BU
        arrivait en tete parce qu'elle est declaree en premier, ce qui n'est
        pas une raison.

        Le champ n'est pas ecrit en dur : c'est celui que la configuration
        designe deja comme categorie de comparaison. Un fichier sans colonne
        de poste retombe sur la premiere dimension disponible.
        """
        voulu = self.configuration.get(
            "pay_equity_parameters.category_field", "job_title")
        for index, segment in enumerate(self._segments):
            if segment.get("field") == voulu:
                return index
        return 0

    def _show_distribution(self) -> None:
        """Histogramme d'un bloc, ou les deux sexes dos a dos.

        Le decoupage par sexe vient du moteur, avec le reste de la
        distribution : une fenetre qui parcourt la population pour son
        propre compte finit par compter autrement que lui.
        """
        allowed = self.histogram.may_split()
        if not allowed and self.dist_split.get():
            # Repasser la variable a faux avant de rendre : le bouton ne doit
            # pas rester coche sur un graphique qui n'est pas dedouble.
            self.dist_split.set(False)
            return
        self.histogram.set_split(bool(self.dist_split.get()))
        if allowed:
            self.dist_split_row.pack(side="left")
            self.dist_split_note.configure(text="")
            self.dist_split_note.pack_forget()
        else:
            self.dist_split_row.pack_forget()
            self.dist_split_note.configure(text=self.histogram.split_warning())
            self.dist_split_note.pack(side="left")

    def _reorder(self) -> None:
        """Applique le tri choisi, dans la liste du mode courant."""
        choix = self.boxplot.orders()
        index = max(self.box_order.current(), 0)
        self.boxplot.set_order(choix[min(index, len(choix) - 1)][0])

    def _refill_orders(self) -> None:
        """Remplit la liste des tris selon le mode.

        « Ouverture décroissante » n'a pas de colonne pour se verifier en
        mode dedouble, et « Écart F/H » n'existe pas en mode simple : un
        tri qu'aucune colonne ne montre se lit comme un desordre.
        """
        choix = self.boxplot.orders()
        voulu = self.boxplot.order
        self.box_order.configure(values=[label for _key, label in choix])
        cles = [key for key, _label in choix]
        self.box_order.current(cles.index(voulu) if voulu in cles else 0)
        self.boxplot.set_order(cles[self.box_order.current()])

    def _change_box_dimension(self) -> None:
        """Changer de dimension remet les valeurs a toutes.

        Garder la selection n'aurait aucun sens : les postes retenus ne
        sont pas des etablissements, et le graphique se serait vide sans
        que rien ne le dise.
        """
        self.box_values = None
        self._show_boxes()

    def _box_values_available(self) -> List[str]:
        """Les valeurs que la dimension choisie porte, dans l'ordre du
        moteur."""
        index = self.box_choice.current()
        if index < 0 or index >= len(self._segments):
            return []
        return [str(row.get("segment", ""))
                for row in self._segments[index].get("rows", [])
                if row.get("segment") is not None]

    def _choose_box_values(self) -> None:
        """Ouvre le choix des valeurs de la dimension."""
        valeurs = self._box_values_available()
        if not valeurs:
            return
        intitule = self.box_choice.get() or "la dimension"
        ValuePicker(self, self.fonts, f"Valeurs — {intitule}", valeurs,
                    self.box_values, self._apply_box_values)

    def _apply_box_values(self, retenues) -> None:
        self.box_values = retenues
        self._show_boxes()

    def _retain_box_values(self, rows):
        """Ne garde que les segments retenus, et met a jour le bouton.

        Ne rien retenir n'est pas « tout retenir » : c'est un graphique
        vide, et c'est ce que l'utilisateur a demande. Le bouton le dit,
        de sorte qu'un graphique vide ne passe pas pour une panne.
        """
        total = len(self._box_values_available())
        if self.box_values is None:
            self.box_values_button.configure(
                text=f"Valeurs : toutes ({total})" if total
                else "Valeurs : toutes")
            return rows
        retenues = set(self.box_values)
        self.box_values_button.configure(
            text=f"Valeurs : {len(retenues)} sur {total}")
        return [row for row in rows
                if str(row.get("segment", "")) in retenues]

    def _change_col_dimension(self) -> None:
        """Changer d'abscisse remet les valeurs a toutes : les postes
        retenus ne sont pas des etablissements, et le graphique se serait
        vide sans que rien ne le dise."""
        self.col_values = None
        self._show_columns()

    def _col_values_available(self) -> List[str]:
        """Les valeurs que l'abscisse choisie porte, dans l'ordre du moteur."""
        index = self.col_choice.current()
        if index < 0 or index >= len(self._segments):
            return []
        return [str(row.get("segment", ""))
                for row in self._segments[index].get("rows", [])
                if row.get("segment") is not None]

    def _choose_col_values(self) -> None:
        """Ouvre le choix des valeurs portees en abscisse."""
        valeurs = self._col_values_available()
        if not valeurs:
            return
        intitule = self.col_choice.get() or "la dimension"
        ValuePicker(self, self.fonts, f"Valeurs — {intitule}", valeurs,
                    self.col_values, self._apply_col_values)

    def _apply_col_values(self, retenues) -> None:
        self.col_values = retenues
        self._show_columns()

    def _retain_col_values(self, rows):
        """Ne garde que les categories retenues, et met a jour le bouton.

        Ne rien retenir n'est pas « tout retenir » : c'est un graphique
        vide, et c'est ce que l'utilisateur a demande. Le bouton le dit, de
        sorte qu'un graphique vide ne passe pas pour une panne.
        """
        total = len(self._col_values_available())
        if self.col_values is None:
            self.col_values_button.configure(
                text=f"Valeurs : toutes ({total})" if total
                else "Valeurs : toutes")
            return rows
        retenues = set(self.col_values)
        self.col_values_button.configure(
            text=f"Valeurs : {len(retenues)} sur {total}")
        return [row for row in rows
                if str(row.get("segment", "")) in retenues]

    def _reorder_columns(self) -> None:
        """Applique le tri choisi aux boites dressees."""
        choix = self.column_boxes.orders()
        index = max(self.col_order.current(), 0)
        self.column_boxes.set_order(choix[min(index, len(choix) - 1)][0])

    def _show_columns(self) -> None:
        """Boites dressees de l'abscisse choisie.

        Elles lisent le meme bloc que la dispersion couchee : les
        percentiles par segment sont deja calcules, et un chiffre affiche a
        deux endroits doit venir du meme calcul.
        """
        index = self.col_choice.current()
        if index < 0 or index >= len(self._segments):
            self.column_boxes.set_rows([])
            return
        block = self._segments[index]
        rows = self._retain_col_values(block["rows"])
        self.column_boxes.set_rows(
            rows, block.get("currency", "EUR"),
            reference=block.get("reference_median"),
            alert=self.configuration.number(
                "pay_equity_parameters.gap_alert_threshold",
                5.0, minimum=0.0, maximum=100.0),
            # Le nom de l'ordonnee vient du moteur, donc de la
            # configuration : ecrit ici, il annoncerait « salaire de base »
            # sur un axe qui porte ce que le parametrage y a mis.
            value_label=block.get("value_label", ""))

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
        split = bool(self.box_split.get())
        # Par la methode, non par l'attribut : elle existe pour cela, et un
        # chemin que les tests parcourent sans que l'outil l'emprunte n'est
        # pas un chemin teste.
        self.boxplot.set_split(split)
        self._refill_orders()
        # Dedouble, les lignes viennent d'un autre calcul : le meme segment,
        # coupe en deux. Elles portent aussi le segment entier, pour que
        # l'echelle et le tri restent ceux du mode simple.
        rows = (metrics.segment_by_sex(self.result.filtered,
                                       self.result.config,
                                       block["field"])
                if split else block["rows"])
        rows = self._retain_box_values(rows)
        # La mediane d'ensemble n'est pas repetee en tete : le graphique la
        # trace, et un repere dessine se lit mieux qu'un montant a comparer
        # de tete avec seize boites.
        self.boxplot.set_rows(
            rows, currency, reference=block.get("reference_median"),
            # Le seuil qui met un ecart en evidence est celui de la
            # configuration, pas un nombre ecrit dans le graphique.
            alert=self.configuration.number(
                "pay_equity_parameters.gap_alert_threshold",
                5.0, minimum=0.0, maximum=100.0))

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
                    deck, payload, os.path.join(directory, f"vue-detaillee-{stamp}.html")))
                produced.append(write_slides_pdf(
                    deck, payload, os.path.join(directory, f"vue-detaillee-{stamp}.pdf")))
            if self.output_vars["excel"].get():
                produced.append(export_excel(
                    payload, self.result.filtered, self.result.config,
                    os.path.join(directory, f"analyse-{stamp}.xlsx"),
                    table=self.result.table, mapping=self.result.mapping))
            # Pas de manifeste JSON. Ce qu'il portait de lisible — fichier
            # source, perimetre, date, effectif — est deja en tete de la
            # restitution et sur la garde de la synthese ; le reste etait
            # du JSON qu'aucun des destinataires de ces documents n'ouvre.
            # La ligne de commande, elle, l'ecrit toujours : c'est sa seule
            # sortie exploitable par un programme.
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
    Application(config_dir, splash=True).mainloop()
    return 0
