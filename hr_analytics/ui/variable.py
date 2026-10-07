"""L'ecran des elements variables : la periode, puis les natures.

Deux reglages, et un seul des deux se devine. Les intitules, le fichier
les porte — on les montre, on ne demande a personne de les ecrire. La
periode, non : un fichier de primes ne dit pas de lui-meme ce qu'il
couvre, et une date de versement n'est pas une periode. Si janvier n'a
porte aucune prime, les bornes observees commencent en fevrier, et la
periode reelle commence pourtant en janvier.

L'ecran propose donc, et c'est un humain qui tranche.
"""

from __future__ import annotations

import datetime as _dt
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Sequence

from ..core import package as pk
from ..core.errors import ConfigError
from . import theme
from .theme import Card, Fonts


class ElementsWindow(tk.Toplevel):
    """Declarer la periode d'un fichier d'elements et classer ses intitules."""

    #: Largeur de la liste des intitules. Un intitule de paie depasse
    #: rarement trente caracteres ; au-dela, la colonne des natures
    #: partirait hors de l'ecran.
    LABEL_WIDTH = 34

    def __init__(self, master: tk.Misc, fonts: Fonts,
                 labels: Sequence[str],
                 natures: Dict[str, str],
                 period: Optional[pk.Period],
                 proposed: Optional[pk.Period],
                 extraction: Optional[_dt.date],
                 on_valide):
        super().__init__(master, background=theme.GROUND)
        self.title("Éléments variables")
        self.transient(master)
        self.fonts = fonts
        self._labels = list(labels)
        self._on_valide = on_valide
        self._proposed = proposed
        self._extraction = extraction
        self._erreur: Optional[str] = None

        depart = period or self._default_period()
        self._du = tk.StringVar(value=f"{depart.start:%d/%m/%Y}")
        self._au = tk.StringVar(value=f"{depart.end:%d/%m/%Y}")
        self._natures = {
            intitule: tk.StringVar(
                value=natures.get(pk._sans_accent(intitule),
                                  pk.NATURE_PAR_DEFAUT))
            for intitule in self._labels}

        self._build_period()
        # Le pied est pose avant la liste : « pack » empile dans l'ordre,
        # et une liste qui s'etire poussait les deux boutons hors de la
        # fenetre des que le fichier portait quinze intitules.
        self._build_actions()
        self._build_labels()
        self._refresh_note()
        self.minsize(640, 520)

    # ------------------------------------------------------------ periode

    def _default_period(self) -> pk.Period:
        """Les douze mois glissants, plutot que les bornes observees.

        Les bornes observees sont celles des versements, pas celles de la
        periode : elles sous-estiment presque toujours. Les douze mois
        qui precedent l'extraction sont le choix le plus souvent juste,
        et c'est celui qui laisse le moins de salaries de cote.
        """
        if self._extraction is not None:
            return pk.Period.twelve_months_to(self._extraction)
        if self._proposed is not None:
            return self._proposed
        return pk.Period.twelve_months_to(_dt.date.today())

    def _build_period(self) -> None:
        card = Card(self, padding=0)
        card.pack(fill="x", padx=22, pady=(18, 0))
        corps = tk.Frame(card.inner, background=theme.CANVAS)
        corps.pack(fill="x", padx=18, pady=16)
        tk.Label(corps, text="PÉRIODE COUVERTE", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(anchor="w")
        tk.Label(corps,
                 text="Un salaire est un état, une prime est un flux : "
                      "c'est la période qui les met sur la même base. Le "
                      "salaire y est ramené — une prime n'est jamais "
                      "multipliée pour faire une année.",
                 background=theme.CANVAS, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=620,
                 justify="left").pack(anchor="w", pady=(3, 12))

        ligne = tk.Frame(corps, background=theme.CANVAS)
        ligne.pack(anchor="w")
        for intitule, variable in (("du", self._du), ("au", self._au)):
            tk.Label(ligne, text=intitule, background=theme.CANVAS,
                     foreground=theme.MUTED,
                     font=self.fonts.body).pack(side="left", padx=(0, 7))
            champ = tk.Entry(ligne, textvariable=variable, width=12,
                             font=self.fonts.body, background=theme.CANVAS,
                             foreground=theme.INK, relief="flat",
                             highlightthickness=1,
                             highlightbackground=theme.LINE_STRONG,
                             highlightcolor=theme.ACCENT, justify="center")
            champ.pack(side="left", padx=(0, 18), ipady=3)
            variable.trace_add("write", lambda *_: self._refresh_note())

        raccourcis = tk.Frame(corps, background=theme.CANVAS)
        raccourcis.pack(anchor="w", pady=(10, 0))
        for intitule, fabrique in self._shortcuts():
            ttk.Button(raccourcis, text=intitule, style="Ghost.TButton",
                       command=lambda f=fabrique: self._apply(f())
                       ).pack(side="left", padx=(0, 8))

        self.note = tk.Label(corps, text="", background=theme.CANVAS,
                             foreground=theme.MUTED, font=self.fonts.small,
                             wraplength=620, justify="left")
        self.note.pack(anchor="w", pady=(12, 0))

    def _shortcuts(self):
        """Les periodes qu'on choisit neuf fois sur dix."""
        fin = self._extraction or _dt.date.today()
        sorties = [("12 mois glissants",
                    lambda: pk.Period.twelve_months_to(fin)),
                   (f"Année {fin.year - 1}",
                    lambda: pk.Period(_dt.date(fin.year - 1, 1, 1),
                                      _dt.date(fin.year - 1, 12, 31)))]
        if self._proposed is not None:
            sorties.append(("Bornes du fichier", lambda: self._proposed))
        return sorties

    def _apply(self, period: pk.Period) -> None:
        self._du.set(f"{period.start:%d/%m/%Y}")
        self._au.set(f"{period.end:%d/%m/%Y}")

    def _read_period(self) -> Optional[pk.Period]:
        debut = _parse_jour(self._du.get())
        fin = _parse_jour(self._au.get())
        if debut is None or fin is None:
            self._erreur = ("Les deux dates se saisissent au format "
                            "jj/mm/aaaa.")
            return None
        try:
            periode = pk.Period(debut, fin)
        except ConfigError as refus:
            self._erreur = refus.message
            return None
        self._erreur = None
        return periode

    def _refresh_note(self) -> None:
        periode = self._read_period()
        if periode is None:
            self.note.configure(text=self._erreur or "", foreground=theme.CRIT)
            return
        texte = _mois(periode) + "."
        couleur = theme.MUTED
        if not periode.complete:
            # Le dire ici plutot que de laisser lire une part de
            # beneficiaires comme une politique alors qu'elle n'est qu'un
            # decoupage.
            texte += (" En deçà de douze mois, une prime annuelle versée "
                      "hors de cette fenêtre n'apparaît pas : la part de "
                      "bénéficiaires est à lire avec cette réserve.")
            couleur = theme.WARN
        if self._proposed is not None:
            texte += (f"\nLe fichier porte des versements "
                      f"{self._proposed.label}.")
        self.note.configure(text=texte, foreground=couleur)

    # ----------------------------------------------------------- natures

    def _build_labels(self) -> None:
        card = Card(self, padding=0)
        card.pack(fill="both", expand=True, padx=22, pady=(14, 0))
        entete = tk.Frame(card.inner, background=theme.CANVAS)
        entete.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(entete, text="NATURE DES ÉLÉMENTS", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(anchor="w")
        tk.Label(entete,
                 text="Un intitulé ne dit pas à lui seul s'il faut "
                      "l'additionner. Un remboursement de frais n'est pas "
                      "une rémunération : classé « exclu », il ne compte "
                      "nulle part.",
                 background=theme.CANVAS, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=620,
                 justify="left").pack(anchor="w", pady=(3, 0))

        corps = tk.Frame(card.inner, background=theme.CANVAS)
        corps.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        canvas = tk.Canvas(corps, background=theme.CANVAS,
                           highlightthickness=0, height=260)
        barre = ttk.Scrollbar(corps, orient="vertical", command=canvas.yview,
                              style="Flat.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        liste = tk.Frame(canvas, background=theme.CANVAS)
        fenetre = canvas.create_window((0, 0), window=liste, anchor="nw")
        liste.bind("<Configure>",
                   lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(fenetre, width=e.width))
        theme.bind_wheel(canvas, self)

        if not self._labels:
            tk.Label(liste, text="Aucun intitulé dans ce fichier.",
                     background=theme.CANVAS, foreground=theme.FAINT,
                     font=self.fonts.small).pack(anchor="w")
            return
        choix = [pk.NATURE_LABELS[nature] for nature in pk.NATURES]
        self._par_intitule = {pk.NATURE_LABELS[n]: n for n in pk.NATURES}
        for intitule in self._labels:
            ligne = tk.Frame(liste, background=theme.CANVAS)
            ligne.pack(fill="x", pady=2)
            tk.Label(ligne, text=intitule, background=theme.CANVAS,
                     foreground=theme.INK_SOFT, font=self.fonts.body,
                     width=self.LABEL_WIDTH, anchor="w").pack(side="left")
            affiche = tk.StringVar(
                value=pk.NATURE_LABELS[self._natures[intitule].get()])
            boite = ttk.Combobox(ligne, textvariable=affiche, values=choix,
                                 state="readonly", width=20,
                                 font=self.fonts.small)
            boite.pack(side="left")
            # Les deux variables se suivent dans les deux sens : la liste
            # affiche un intitule, la nature retenue est une cle, et une
            # liaison a sens unique laissait la liste montrer « Variable »
            # sur un element qu'on venait de classer autrement.
            # La comparaison avant ecriture coupe la boucle.
            affiche.trace_add(
                "write",
                lambda *_a, i=intitule, v=affiche: self._set_nature(i, v))
            self._natures[intitule].trace_add(
                "write",
                lambda *_a, i=intitule, v=affiche: self._show_nature(i, v))

    def _set_nature(self, intitule: str, affiche: tk.StringVar) -> None:
        voulue = self._par_intitule.get(affiche.get())
        if voulue and self._natures[intitule].get() != voulue:
            self._natures[intitule].set(voulue)

    def _show_nature(self, intitule: str, affiche: tk.StringVar) -> None:
        texte = pk.NATURE_LABELS.get(self._natures[intitule].get())
        if texte and affiche.get() != texte:
            affiche.set(texte)

    # ----------------------------------------------------------- actions

    def _build_actions(self) -> None:
        pied = tk.Frame(self, background=theme.GROUND)
        pied.pack(side="bottom", fill="x", padx=22, pady=16)
        self.feedback = tk.Label(pied, text="", background=theme.GROUND,
                                 foreground=theme.CRIT, font=self.fonts.small,
                                 wraplength=420, justify="left")
        self.feedback.pack(side="left")
        ttk.Button(pied, text="Appliquer", style="Primary.TButton",
                   command=self.save).pack(side="right")
        ttk.Button(pied, text="Annuler", style="GhostGround.TButton",
                   command=self.destroy).pack(side="right", padx=(0, 8))

    def collect(self) -> Dict[str, str]:
        """Les natures telles qu'elles seront ecrites, par intitule."""
        return {intitule: variable.get()
                for intitule, variable in self._natures.items()}

    def save(self) -> None:
        periode = self._read_period()
        if periode is None:
            self.feedback.configure(text=self._erreur or "Période illisible.")
            return
        self._on_valide(periode, self.collect())
        self.destroy()


def _parse_jour(texte: str) -> Optional[_dt.date]:
    """Lit une date saisie a la main, en francais puis en ISO.

    Les deux formes sont acceptees parce que les deux se tapent : on
    affiche jj/mm/aaaa, et quelqu'un qui colle une date depuis un tableur
    colle souvent de l'ISO.
    """
    texte = str(texte or "").strip()
    for forme in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return _dt.datetime.strptime(texte, forme).date()
        except ValueError:
            continue
    return None


class VariablePage(tk.Frame):
    """L'onglet « Variable » : une valeur a la fois, en profondeur.

    L'ecran repond a une question de preparation — « que verse-t-on ici,
    a qui, et dans quelle dispersion ». Il ne classe pas les groupes
    entre eux : c'est le role du tableau, et deux reponses a deux
    questions ne tiennent pas sur la meme page sans que l'une desserve
    l'autre.

    La maille se choisit. Le metier est celle a laquelle une prime se
    decide le plus souvent, mais une prime d'etablissement se lit par
    etablissement et une prime de coefficient par coefficient : imposer
    une seule maille, c'est imposer une seule question.
    """

    #: Hauteur des barres empilees. Trois barres : assez epaisses pour
    #: qu'un segment de 3 % reste visible, assez fines pour tenir avec le
    #: reste.
    BARRE = 34
    #: Natures tracees, dans l'ordre d'empilement, avec leur couleur de
    #: serie. La base vient en premier : c'est elle qu'on lit en partant
    #: du bord gauche.
    SEGMENTS = (("base", "Base", 0), ("fixe", "Primes fixes", 2),
                ("variable", "Variable", 1), ("exceptionnel", "Exceptionnel", 3),
                ("avantage", "Avantages", 4))

    def __init__(self, master: tk.Widget, fonts: Fonts, on_change=None):
        super().__init__(master, background=theme.CANVAS)
        self.fonts = fonts
        self._on_change = on_change
        self._packages: List = []
        self._lines: List = []
        self._config = None
        self._period = None
        self._natures: Dict[str, str] = {}
        #: Dimension de decoupage, et les champs proposes. « job » tant
        #: qu'aucun fichier n'est charge : il sera remplace par la
        #: premiere dimension declaree si celle-la n'existe pas.
        self.dimension = "job"
        self._dimensions: List[str] = []

        self._build_head()
        self._build_body()

    # -------------------------------------------------------------- tete

    def _build_head(self) -> None:
        self.source = tk.Label(self, text="", background=theme.GROUND,
                               foreground=theme.INK_SOFT,
                               font=self.fonts.small, anchor="w",
                               padx=18, pady=8)
        self.source.pack(fill="x")

        tete = tk.Frame(self, background=theme.CANVAS)
        tete.pack(fill="x", padx=18, pady=(14, 0))
        tk.Label(tete, text="ANALYSER PAR", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")
        self.dimension_choice = ttk.Combobox(tete, state="readonly", width=22,
                                             font=self.fonts.small)
        self.dimension_choice.pack(side="left", padx=10)
        self.dimension_choice.bind("<<ComboboxSelected>>",
                                   lambda _e: self._change_dimension())
        tk.Label(tete, text="VALEUR", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left", padx=(18, 0))
        self.choice = ttk.Combobox(tete, state="readonly", width=30,
                                   font=self.fonts.small)
        self.choice.pack(side="left", padx=10)
        self.choice.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self.headcount = tk.Label(tete, text="", background=theme.CANVAS,
                                  foreground=theme.MUTED,
                                  font=self.fonts.small)
        self.headcount.pack(side="left", padx=(8, 0))

        self.warning = tk.Label(self, text="", background=theme.CANVAS,
                                foreground=theme.WARN, font=self.fonts.small,
                                wraplength=900, justify="left", anchor="w")

    def _build_body(self) -> None:
        corps = tk.Frame(self, background=theme.CANVAS)
        corps.pack(fill="both", expand=True, padx=18, pady=(12, 18))
        corps.columnconfigure(0, weight=1, uniform="moities")
        corps.columnconfigure(1, weight=1, uniform="moities")
        corps.rowconfigure(0, weight=1)

        gauche = tk.Frame(corps, background=theme.CANVAS)
        gauche.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self._title(gauche, "Ce que gagne un salarié")
        # Le libelle se recrit a chaque periode : il disait « mensuelle »
        # et montrait douze mois de salaire, ce qui faisait lire un
        # salaire annuel comme un salaire de mois.
        self.composition_note = tk.Label(
            gauche, text="", background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, anchor="w", justify="left")
        self.composition_note.pack(fill="x", pady=(0, 10))
        self.composition = tk.Canvas(gauche, background=theme.CANVAS,
                                     highlightthickness=0, height=150)
        self.composition.pack(fill="x")
        self.legend = tk.Frame(gauche, background=theme.CANVAS)
        self.legend.pack(fill="x", pady=(10, 0))

        self._title(gauche, "Comment le variable se répartit", pady=(22, 0))
        self.spread_note = tk.Label(gauche, text="", background=theme.CANVAS,
                                    foreground=theme.MUTED,
                                    font=self.fonts.small, anchor="w")
        self.spread_note.pack(fill="x", pady=(0, 8))
        self.spread = tk.Canvas(gauche, background=theme.CANVAS,
                                highlightthickness=0, height=86)
        self.spread.pack(fill="x")

        droite = tk.Frame(corps, background=theme.CANVAS)
        droite.grid(row=0, column=1, sticky="nsew")
        self._title(droite, "Les éléments versés")
        self.elements = ttk.Treeview(
            droite, columns=("Intitulé", "Nature", "Bénéf.", "Médiane", "F/H"),
            show="headings", height=8)
        for nom, largeur, cote, elastique in (
                ("Intitulé", 184, "w", True), ("Nature", 100, "w", False),
                ("Bénéf.", 58, "e", False), ("Médiane", 84, "e", False),
                ("F/H", 72, "e", False)):
            self.elements.heading(nom, text=nom.upper(), anchor=cote)
            # Seul l'intitule s'etire : sans cela, les colonnes de nombres
            # grandissaient avec la fenetre et l'ecart finissait hors
            # champ, ecrit « -1 » au lieu de « -11,4 % ».
            self.elements.column(nom, width=largeur, minwidth=largeur,
                                 anchor=cote, stretch=elastique)
        self.elements.pack(fill="x", pady=(0, 6))
        self.elements_note = tk.Label(
            droite,
            text="Les éléments « exclu » ne comptent nulle part : "
                 "ce sont des remboursements, pas une rémunération. Leur "
                 "nature se règle dans « Éléments variables… ».",
            background=theme.CANVAS, foreground=theme.MUTED,
            font=self.fonts.small, wraplength=430, justify="left", anchor="w")
        self.elements_note.pack(fill="x")

        self._title(droite, "Qui en bénéficie, qui n'en bénéficie pas",
                    pady=(22, 0))
        self.served = tk.Canvas(droite, background=theme.CANVAS,
                                highlightthickness=0, height=74)
        self.served.pack(fill="x")
        self.summary = tk.Label(droite, text="", background=theme.GROUND,
                                foreground=theme.INK_SOFT,
                                font=self.fonts.small, anchor="w",
                                justify="left", padx=14, pady=11,
                                wraplength=420)
        self.summary.pack(fill="x", pady=(16, 0))

    def _title(self, parent, texte, pady=(0, 2)) -> None:
        tk.Label(parent, text=texte, background=theme.CANVAS,
                 foreground=theme.INK, font=self.fonts.section,
                 anchor="w").pack(fill="x", pady=pady)

    # ------------------------------------------------------------ donnees

    def show(self, packages, lines, config, period, natures) -> None:
        """Recoit les paquets deja calcules et repose l'ecran.

        La page ne calcule rien d'elle-meme : les memes chiffres servent
        au classeur et au rapport, et deux chemins de calcul auraient fini
        par diverger.
        """
        self._packages = list(packages)
        self._lines = list(lines)
        self._config = config
        self._period = period
        self._natures = dict(natures or {})
        self._populate_dimensions()
        self._populate_values()
        self._say_coverage()
        self.refresh()

    def _populate_dimensions(self) -> None:
        """Les dimensions declarees, et celle qui ouvre l'ecran.

        Le metier ouvre par defaut parce que c'est la maille a laquelle
        une prime se decide le plus souvent. S'il n'est pas declare, la
        premiere dimension qui porte quelque chose prend sa place : un
        ecran vide par defaut ne se comprend pas.
        """
        from ..core.segmentation import dimension_fields, dimension_label

        champs = [champ for champ in dimension_fields(self._config)
                  if any(str(e.value(champ) or "").strip()
                         for e, _p in self._packages)]
        self._dimensions = champs
        self.dimension_choice.configure(
            values=[dimension_label(self._config, champ) for champ in champs])
        if self.dimension not in champs:
            self.dimension = champs[0] if champs else self.dimension
        if self.dimension in champs:
            self.dimension_choice.current(champs.index(self.dimension))

    def _change_dimension(self) -> None:
        """Changer de maille remet le choix de valeur a la plus peuplee.

        Garder la valeur n'aurait aucun sens : un metier n'est pas un
        etablissement, et l'ecran se viderait sans que rien ne le dise.
        """
        rang = self.dimension_choice.current()
        if 0 <= rang < len(self._dimensions):
            self.dimension = self._dimensions[rang]
        self._populate_values()
        self.refresh()

    def _populate_values(self) -> None:
        valeurs = sorted({self._segment_of(employee)
                          for employee, _p in self._packages} - {""})
        self.choice.configure(values=valeurs)
        if valeurs and self.choice.get() not in valeurs:
            self.choice.set(self._biggest(valeurs))
        elif not valeurs:
            self.choice.set("")

    def _biggest(self, valeurs: Sequence[str]) -> str:
        """La valeur la plus peuplee ouvre l'ecran : c'est celle dont la
        reponse interesse le plus de monde, et elle publie toujours."""
        compte: Dict[str, int] = {}
        for employee, _p in self._packages:
            cle = self._segment_of(employee)
            compte[cle] = compte.get(cle, 0) + 1
        return max(valeurs, key=lambda nom: compte.get(nom, 0))

    def _segment_of(self, employee) -> str:
        return str(employee.value(self.dimension) or "").strip()

    def _say_coverage(self) -> None:
        """Dit, s'il y a lieu, pourquoi les parts manquent.

        Un fichier dont la colonne de temps de travail n'est pas reconnue
        donnait un ecran sans aucun pourcentage, et rien n'en disait la
        raison.
        """
        compte = pk.coverage(self._packages)
        if not compte["without_base"]:
            self.warning.pack_forget()
            return
        self.warning.configure(
            text=f"La part du variable ne se calcule pas pour "
                 f"{compte['without_base']} salarié(s) sur {compte['total']} : "
                 "leur salaire ou leur temps de travail n'est pas connu. "
                 "Les montants, eux, restent justes.")
        self.warning.pack(fill="x", padx=18, pady=(10, 0))

    def refresh(self) -> None:
        if self._config is None:
            return
        valeur = self.choice.get()
        membres = [(e, p) for e, p in self._packages
                   if self._segment_of(e) == valeur]
        beneficiaires = sum(1 for _e, p in membres if p["beneficiary"])
        part = (f" ({100.0 * beneficiaires / len(membres):.0f} %)"
                if membres else "")
        self.headcount.configure(
            text=f"{len(membres)} salariés · {beneficiaires} bénéficiaires"
                 f"{part}" if membres else "")
        self.composition_note.configure(
            text=f"Rémunération médiane sur la période — {_mois(self._period)}"
                 " —, ramenée au temps plein.")
        self._draw_composition(membres)
        self._draw_spread(membres)
        self._fill_elements(membres)
        self._draw_beneficiaries(membres)
        self._say_summary(membres, beneficiaires)
        if self._on_change:
            self._on_change(metier)

    # -------------------------------------------------------------- trace

    def _colours(self) -> Dict[str, str]:
        serie = theme.ACTIVE.series
        return {cle: serie[rang % len(serie)]
                for cle, _intitule, rang in self.SEGMENTS}

    def _draw_composition(self, membres) -> None:
        canvas = self.composition
        canvas.delete("all")
        for enfant in self.legend.winfo_children():
            enfant.destroy()
        lignes = pk.composition(membres, self._config) if membres else []
        if not lignes:
            return
        largeur = max(canvas.winfo_width(), 420)
        # La place du montant se mesure sur le plus long qu'on va ecrire :
        # une marge fixe le rognait des que les salaires passaient cinq
        # chiffres, et « 25 446 EUR » s'affichait « 25 446 EU ».
        gauche = 92
        droite = 16 + max(
            self.fonts.small_bold.measure(_money(l["total"], self._config))
            for l in lignes if l["total"] is not None) if any(
                l["total"] is not None for l in lignes) else 86
        utile = max(largeur - gauche - droite, 60)
        maximum = max((l["total"] or 0.0) for l in lignes) or 1.0
        couleurs = self._colours()

        y = 10
        for ligne in lignes:
            # L'effectif est colle au libelle : une barre « Femmes » batie
            # sur cinq personnes ne se lit pas comme une batie sur cinq
            # cents, et le rappeler ici evite de remonter le chercher.
            canvas.create_text(0, y + self.BARRE / 2 - 6,
                               text=ligne["label"], anchor="w",
                               font=self.fonts.small, fill=theme.INK_SOFT)
            canvas.create_text(0, y + self.BARRE / 2 + 8,
                               text=f"{ligne['headcount']} salariés",
                               anchor="w", font=self.fonts.small,
                               fill=theme.MUTED)
            if not ligne["published"] or ligne["base"] is None:
                # Un cote retenu par le seuil n'a pas de barre du tout :
                # une barre vide laisserait croire a une remuneration nulle.
                canvas.create_text(
                    gauche, y + self.BARRE / 2,
                    text=f"masqué — {ligne['headcount']} salarié(s)",
                    anchor="w", font=self.fonts.small, fill=theme.FAINT)
                y += self.BARRE + 12
                continue
            x = gauche
            for cle, _intitule, _rang in self.SEGMENTS:
                montant = (ligne["base"] if cle == "base"
                           else ligne["parts"].get(cle) or 0.0)
                if not montant:
                    continue
                largeur_segment = utile * montant / maximum
                canvas.create_rectangle(x, y, x + largeur_segment,
                                        y + self.BARRE, width=0,
                                        fill=couleurs[cle])
                x += largeur_segment
            canvas.create_text(x + 8, y + self.BARRE / 2,
                               text=_money(ligne["total"], self._config),
                               anchor="w", font=self.fonts.small_bold,
                               fill=theme.INK)
            y += self.BARRE + 12
        canvas.configure(height=y)

        # La legende ne nomme que ce qui est trace : une case « Avantages »
        # devant un metier qui n'en verse aucun ferait chercher un segment
        # qui n'existe pas.
        presents = set()
        for ligne in lignes:
            if not ligne["published"] or ligne["base"] is None:
                continue
            presents.add("base")
            presents.update(cle for cle, montant in ligne["parts"].items()
                            if montant)
        for cle, intitule, _rang in self.SEGMENTS:
            if cle not in presents:
                continue
            case = tk.Frame(self.legend, background=theme.CANVAS)
            case.pack(side="left", padx=(0, 16))
            tk.Frame(case, background=couleurs[cle], width=11, height=11
                     ).pack(side="left", padx=(0, 6))
            tk.Label(case, text=intitule, background=theme.CANVAS,
                     foreground=theme.MUTED,
                     font=self.fonts.small).pack(side="left")

    def _draw_spread(self, membres) -> None:
        canvas = self.spread
        canvas.delete("all")
        bornes = pk.spread(membres, self._config) if membres else None
        if bornes is None:
            self.spread_note.configure(
                text="Trop peu de bénéficiaires pour publier une "
                     "dispersion.")
            return
        self.spread_note.configure(
            text=f"Parmi les {bornes['count']} bénéficiaires.")
        largeur = max(canvas.winfo_width(), 420)
        gauche, droite = 14, 14
        utile = max(largeur - gauche - droite, 60)
        bas, haut = bornes["min"], bornes["max"]
        etendue = (haut - bas) or 1.0

        def x_de(valeur):
            return gauche + utile * (valeur - bas) / etendue

        milieu = 30
        canvas.create_line(x_de(bas), milieu, x_de(haut), milieu,
                           fill=theme.LINE_STRONG)
        for borne in (bas, haut):
            canvas.create_line(x_de(borne), milieu - 9, x_de(borne),
                               milieu + 9, fill=theme.MUTED)
        couleur = self._colours()["variable"]
        canvas.create_rectangle(x_de(bornes["q1"]), milieu - 13,
                                x_de(bornes["q3"]), milieu + 13,
                                outline=couleur, width=1,
                                fill=theme.ACCENT_SOFT)
        canvas.create_line(x_de(bornes["median"]), milieu - 13,
                           x_de(bornes["median"]), milieu + 13,
                           fill=couleur, width=3)
        for valeur, ancre in ((bas, "w"), (haut, "e")):
            canvas.create_text(x_de(valeur), milieu + 24,
                               text=_money(valeur, self._config), anchor=ancre,
                               font=self.fonts.small, fill=theme.MUTED)
        canvas.create_text(
            x_de(bornes["median"]), milieu + 44,
            text=f"médiane {_money(bornes['median'], self._config)}",
            anchor="center", font=self.fonts.small_bold, fill=theme.INK)

    def _fill_elements(self, membres) -> None:
        self.elements.delete(*self.elements.get_children())
        if not membres:
            return
        rows = pk.element_rows(self._lines, membres, self._config,
                               self._period, self._natures)
        # La hauteur suit le contenu : trois elements ne gardent pas cinq
        # lignes de blanc sous eux.
        self.elements.configure(height=max(len(rows), 3))
        for row in rows:
            self.elements.insert(
                "", "end",
                values=(row["label"], row["nature_label"],
                        row["beneficiaries"],
                        _money(row["median"], self._config)
                        if row["median"] is not None else "—",
                        _signed(row["gap"])))

    def _draw_beneficiaries(self, membres) -> None:
        from ..core.pay_equity import FEMALE, MALE

        canvas = self.served
        canvas.delete("all")
        if not membres:
            return
        compte = {FEMALE: [0, 0], MALE: [0, 0]}
        for employee, package in membres:
            sexe = pk._sex_of(employee, self._config)
            if sexe not in compte:
                continue
            compte[sexe][1] += 1
            if package["beneficiary"]:
                compte[sexe][0] += 1

        largeur = max(canvas.winfo_width(), 420)
        gauche, droite = 68, 96
        utile = max(largeur - gauche - droite, 60)
        y = 8
        for sexe, intitule, couleur in ((FEMALE, "Femmes", theme.FEMALE),
                                        (MALE, "Hommes", theme.MALE)):
            beneficiaires, total = compte[sexe]
            canvas.create_text(0, y + 11, text=intitule, anchor="w",
                               font=self.fonts.small, fill=couleur)
            canvas.create_rectangle(gauche, y, gauche + utile, y + 22,
                                    width=0, fill=theme.GRID)
            if total:
                part = beneficiaires / total
                canvas.create_rectangle(gauche, y, gauche + utile * part,
                                        y + 22, width=0, fill=couleur)
                canvas.create_text(
                    gauche + utile + 8, y + 11,
                    text=f"{beneficiaires} sur {total}", anchor="w",
                    font=self.fonts.small, fill=theme.INK_SOFT)
            else:
                canvas.create_text(gauche + 8, y + 11, text="aucun",
                                   anchor="w", font=self.fonts.small,
                                   fill=theme.FAINT)
            y += 32
        canvas.configure(height=y)

    def _say_summary(self, membres, beneficiaires) -> None:
        """Les deux ecarts cote a cote, et sur quoi porte le second.

        Separes, ils se lisent comme deux mesures sans rapport ; ensemble,
        ils disent ou se joue l'ecart de ce metier — et l'effectif du
        second empeche de le lire comme s'il portait sur tout le monde.
        """
        if not membres:
            self.summary.configure(text="")
            return
        rows = pk.segment_rows(membres, self._config, self.dimension)
        if not rows:
            self.summary.configure(text="")
            return
        row = rows[0]
        ecart = row["variable_gap"]
        if ecart is None:
            texte = ("L'écart F/H sur le variable n'est pas publié : l'un "
                     "des deux sexes compte trop peu de bénéficiaires.")
        else:
            texte = (f"Écart F/H sur le variable versé : {_signed(ecart)}. "
                     f"Il porte sur les {beneficiaires} bénéficiaires, sur "
                     f"{len(membres)} salariés.")
        if row["variable_share"] is not None:
            part = f"{row['variable_share']:.1f}".replace(".", ",")
            texte += (f"\nLe variable pèse {part} % de la rémunération, "
                      "en médiane.")
        self.summary.configure(text=texte)


def _money(valeur, config) -> str:
    from ..core.reporting import format_money

    devise = config.get("salary_parameters.currency", "EUR") if config else "EUR"
    return format_money(valeur, devise)


def _mois(period) -> str:
    """La duree d'une periode, en mois entiers.

    Sans decimale : « 12,0 mois » se lit comme une precision que la
    mesure n'a pas, et « 11,99 » n'a jamais interesse personne. Le calcul,
    lui, garde ses decimales — c'est l'affichage qui arrondit.
    """
    return f"{round(period.months)} mois"


def _signed(valeur) -> str:
    """Un ecart s'ecrit avec son signe : « 11 % » ne dit pas dans quel sens."""
    if valeur is None:
        return "—"
    return f"{valeur:+.1f} %".replace(".", ",")
