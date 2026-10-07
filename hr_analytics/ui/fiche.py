"""La fiche d'un salarie : ou il se situe, et d'ou il vient.

Deux moities. A gauche l'etat du jour et la place parmi les pairs — le
rapport a la mediane du poste est le seul chiffre qui compare deux
personnes de deux metiers differents. A droite l'historique, qui demande
un troisieme fichier parce que le fichier de population est un
instantane.

La fiche ne traite que de remuneration. Les appreciations de people
review y ont figure le temps d'un essai, et elles en sont retirees :
deux choses posees cote a cote finissent par s'expliquer l'une l'autre
dans la tete du lecteur, et rien ici ne le permet.

Une fiche est nominative : elle vit a l'ecran, et rien n'en sort.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Sequence

from ..core import career as cr
from . import theme
from .theme import Card, Fonts


class HistoryWindow(tk.Toplevel):
    """Classer les colonnes d'un historique : montant, ou rien.

    Le meme geste que pour les natures d'elements, sur une autre
    question. Les colonnes sont celles du fichier : on les montre, on ne
    demande a personne de les ecrire.

    Deux roles seulement, parce que la fiche ne traite que de
    remuneration : ce qui est un montant, et ce dont on n'a rien a faire.
    """

    LABEL_WIDTH = 34

    def __init__(self, master: tk.Misc, fonts: Fonts,
                 colonnes: Sequence[str], roles: Dict[str, str], on_valide):
        super().__init__(master, background=theme.GROUND)
        self.title("Historique des rémunérations")
        self.transient(master)
        self.fonts = fonts
        self._colonnes = list(colonnes)
        self._on_valide = on_valide

        self._roles = {
            colonne: tk.StringVar(
                value=roles.get(cr._sans_accent(colonne), cr.ROLE_PAR_DEFAUT))
            for colonne in self._colonnes}
        self._par_intitule = {cr.ROLE_LABELS[r]: r for r in cr.ROLES}

        self._build_actions()
        self._build_columns()
        self.minsize(620, 460)

    def _build_columns(self) -> None:
        card = Card(self, padding=0)
        card.pack(fill="both", expand=True, padx=22, pady=(18, 0))
        entete = tk.Frame(card.inner, background=theme.CANVAS)
        entete.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(entete, text="COLONNES DE L'HISTORIQUE",
                 background=theme.CANVAS, foreground=theme.FAINT,
                 font=self.fonts.label).pack(anchor="w")
        tk.Label(entete,
                 text="Les montants s'additionnent pour faire la "
                      "rémunération de la période : une colonne qui porte "
                      "déjà un total se classe « ignorée », sinon elle "
                      "compterait deux fois. Tout ce qui n'est pas un "
                      "montant se classe « ignorée ».",
                 background=theme.CANVAS, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=600,
                 justify="left").pack(anchor="w", pady=(3, 0))

        corps = tk.Frame(card.inner, background=theme.CANVAS)
        corps.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        canvas = tk.Canvas(corps, background=theme.CANVAS,
                           highlightthickness=0, height=250)
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

        if not self._colonnes:
            tk.Label(liste, text="Ce fichier ne porte que le matricule et "
                                 "la période.",
                     background=theme.CANVAS, foreground=theme.FAINT,
                     font=self.fonts.small).pack(anchor="w")
            return
        choix = [cr.ROLE_LABELS[role] for role in cr.ROLES]
        for colonne in self._colonnes:
            ligne = tk.Frame(liste, background=theme.CANVAS)
            ligne.pack(fill="x", pady=2)
            tk.Label(ligne, text=colonne, background=theme.CANVAS,
                     foreground=theme.INK_SOFT, font=self.fonts.body,
                     width=self.LABEL_WIDTH, anchor="w").pack(side="left")
            affiche = tk.StringVar(
                value=cr.ROLE_LABELS[self._roles[colonne].get()])
            ttk.Combobox(ligne, textvariable=affiche, values=choix,
                         state="readonly", width=16,
                         font=self.fonts.small).pack(side="left")
            affiche.trace_add(
                "write",
                lambda *_a, c=colonne, v=affiche: self._set_role(c, v))
            self._roles[colonne].trace_add(
                "write",
                lambda *_a, c=colonne, v=affiche: self._show_role(c, v))

    def _set_role(self, colonne: str, affiche: tk.StringVar) -> None:
        voulu = self._par_intitule.get(affiche.get())
        if voulu and self._roles[colonne].get() != voulu:
            self._roles[colonne].set(voulu)

    def _show_role(self, colonne: str, affiche: tk.StringVar) -> None:
        texte = cr.ROLE_LABELS.get(self._roles[colonne].get())
        if texte and affiche.get() != texte:
            affiche.set(texte)

    def _build_actions(self) -> None:
        pied = tk.Frame(self, background=theme.GROUND)
        pied.pack(side="bottom", fill="x", padx=22, pady=16)
        ttk.Button(pied, text="Appliquer", style="Primary.TButton",
                   command=self.save).pack(side="right")
        ttk.Button(pied, text="Annuler", style="GhostGround.TButton",
                   command=self.destroy).pack(side="right", padx=(0, 8))

    def collect(self) -> Dict[str, str]:
        return {colonne: variable.get()
                for colonne, variable in self._roles.items()}

    def save(self) -> None:
        self._on_valide(self.collect())
        self.destroy()

class PersonPicker(tk.Frame):
    """Chercher un salarie parmi plusieurs milliers.

    Une liste deroulante de deux mille entrees ne se parcourt pas. On
    tape, les correspondances paraissent, on en choisit une. La recherche
    porte sur tout ce que la ligne affiche — matricule compris — parce
    qu'on cherche aussi bien « Dupont » qu'un numero lu sur un bulletin.
    """

    #: Nombre de correspondances montrees. Au-dela, affiner la recherche
    #: va plus vite que lire la liste.
    MONTREES = 12

    def __init__(self, master: tk.Widget, fonts: Fonts, on_choix):
        super().__init__(master, background=theme.CANVAS)
        self.fonts = fonts
        self._on_choix = on_choix
        self._entrees: List[tuple] = []
        self._vus: List[tuple] = []

        tete = tk.Frame(self, background=theme.CANVAS)
        tete.pack(fill="x")
        tk.Label(tete, text="SALARIÉ", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=fonts.label).pack(side="left")
        self._cherche = tk.StringVar()
        self.entry = tk.Entry(tete, textvariable=self._cherche,
                              font=fonts.body, background=theme.CANVAS,
                              foreground=theme.INK, relief="flat",
                              highlightthickness=1,
                              highlightbackground=theme.LINE_STRONG,
                              highlightcolor=theme.ACCENT, width=34)
        self.entry.pack(side="left", padx=10, ipady=3)
        self._cherche.trace_add("write", lambda *_: self._filtrer())
        self.chosen = tk.Label(tete, text="", background=theme.CANVAS,
                               foreground=theme.INK_SOFT,
                               font=fonts.body_bold)
        self.chosen.pack(side="left", padx=(8, 0))
        self.count = tk.Label(tete, text="", background=theme.CANVAS,
                              foreground=theme.MUTED, font=fonts.small)
        self.count.pack(side="left", padx=(10, 0))

        # La liste appartient a la page et non a cette barre : posee
        # dans la barre, elle en aurait ete rognee ; packee, elle
        # poussait l'ecran entier vers le bas a chaque frappe. Elle se
        # pose donc par-dessus, comme toute liste de saisie.
        self.liste = tk.Listbox(master, height=0, font=fonts.small,
                                background=theme.STRIPE, foreground=theme.INK,
                                relief="flat", highlightthickness=1,
                                highlightbackground=theme.LINE,
                                selectbackground=theme.ACCENT_SOFT,
                                selectforeground=theme.INK,
                                activestyle="none", exportselection=False)
        self.liste.bind("<<ListboxSelect>>", lambda _e: self._prendre())
        self.liste.lift()

    def fill(self, entrees: Sequence[tuple]) -> None:
        """`entrees` : des couples (libelle, salarie), deja ordonnes."""
        self._entrees = list(entrees)
        self._cherche.set("")
        self._filtrer()

    def _filtrer(self) -> None:
        tape = theme._sans_accent(self._cherche.get())
        if not tape:
            self._vus = []
            self.liste.place_forget()
            self.count.configure(
                text=f"{len(self._entrees)} salariés — tapez pour chercher"
                     if self._entrees else "")
            return
        trouves = [(libelle, personne) for libelle, personne in self._entrees
                   if tape in theme._sans_accent(libelle)]
        self._vus = trouves[:self.MONTREES]
        self.liste.delete(0, "end")
        for libelle, _personne in self._vus:
            self.liste.insert("end", libelle)
        self.liste.configure(height=max(len(self._vus), 1))
        if self._vus:
            self.liste.place(in_=self.entry, relx=0, rely=1.0, y=4,
                             relwidth=1.0, anchor="nw")
            self.liste.lift()
        else:
            self.liste.place_forget()
        reste = len(trouves) - len(self._vus)
        self.count.configure(
            text=f"{len(trouves)} trouvé(s)" + (f", {reste} non montrés"
                                                if reste else "")
            if trouves else "aucune correspondance")

    def _prendre(self) -> None:
        rangs = self.liste.curselection()
        if not rangs or rangs[0] >= len(self._vus):
            return
        libelle, personne = self._vus[rangs[0]]
        self.chosen.configure(text=libelle)
        self._cherche.set("")
        self.liste.place_forget()
        self._on_choix(personne)


class FichePage(tk.Frame):
    """L'onglet « Fiche salarié ».

    A gauche l'etat du jour et la place parmi les pairs ; a droite
    l'historique de sa remuneration. Rien n'en sort : la page ne propose
    aucun export, et c'est voulu.
    """

    #: Hauteur de la reglette de position. Assez haute pour qu'un repere
    #: s'y distingue d'un quartile, assez basse pour tenir sous un bloc
    #: de chiffres.
    REGLETTE = 76

    def __init__(self, master: tk.Widget, fonts: Fonts):
        super().__init__(master, background=theme.CANVAS)
        self.fonts = fonts
        self._population = None
        self._config = None
        self._history: Dict[str, List] = {}
        self._person = None

        self.source = tk.Label(self, text="", background=theme.GROUND,
                               foreground=theme.INK_SOFT,
                               font=fonts.small, anchor="w", padx=18, pady=8)

        self.picker = PersonPicker(self, fonts, self._choisir)
        self.picker.pack(fill="x", padx=18, pady=(14, 0))

        self.identity = tk.Label(self, text="", background=theme.CANVAS,
                                 foreground=theme.MUTED, font=fonts.small,
                                 anchor="w")
        self.identity.pack(fill="x", padx=18, pady=(10, 0))

        corps = tk.Frame(self, background=theme.CANVAS)
        # Pas encore pose : sans personne choisie, l'ecran montrait deux
        # intertitres surmontant du vide, ce qui se lit comme une panne.
        self.body = corps
        corps.columnconfigure(0, weight=1, uniform="moities")
        corps.columnconfigure(1, weight=1, uniform="moities")
        corps.rowconfigure(0, weight=1)

        gauche = tk.Frame(corps, background=theme.CANVAS)
        gauche.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self._build_state(gauche)
        self._build_standing(gauche)

        droite = tk.Frame(corps, background=theme.CANVAS)
        droite.grid(row=0, column=1, sticky="nsew")
        self._build_history(droite)

    def _title(self, parent, texte, pady=(0, 6)) -> None:
        tk.Label(parent, text=texte, background=theme.CANVAS,
                 foreground=theme.INK, font=self.fonts.section,
                 anchor="w").pack(fill="x", pady=pady)

    # -------------------------------------------------------- etat du jour

    def _build_state(self, parent) -> None:
        self._title(parent, "Son état aujourd'hui")
        self.state = ttk.Treeview(parent, columns=("Champ", "Valeur"),
                                  show="headings", height=6)
        for nom, largeur, cote in (("Champ", 205, "w"), ("Valeur", 150, "e")):
            self.state.heading(nom, text=nom.upper(), anchor=cote)
            self.state.column(nom, width=largeur, anchor=cote,
                              stretch=(nom == "Valeur"))
        self.state.pack(fill="x")

    def _build_standing(self, parent) -> None:
        self._title(parent, "Sa place parmi ses pairs", pady=(22, 2))
        self.standing_note = tk.Label(parent, text="",
                                      background=theme.CANVAS,
                                      foreground=theme.MUTED,
                                      font=self.fonts.small, anchor="w",
                                      justify="left", wraplength=420)
        self.standing_note.pack(fill="x", pady=(0, 8))
        self.ruler = tk.Canvas(parent, background=theme.CANVAS,
                               highlightthickness=0, height=self.REGLETTE)
        self.ruler.pack(fill="x")
        self.standing_figures = tk.Label(
            parent, text="", background=theme.GROUND,
            foreground=theme.INK_SOFT, font=self.fonts.small, anchor="w",
            justify="left", padx=14, pady=11, wraplength=420)
        self.standing_figures.pack(fill="x", pady=(14, 0))

    # --------------------------------------------------------- historique

    def _build_history(self, parent) -> None:
        self._title(parent, "L'évolution de sa rémunération")
        self.history_note = tk.Label(parent, text="", background=theme.CANVAS,
                                     foreground=theme.MUTED,
                                     font=self.fonts.small, anchor="w",
                                     justify="left", wraplength=430)
        self.history_note.pack(fill="x", pady=(0, 8))
        self.curve = tk.Canvas(parent, background=theme.CANVAS,
                               highlightthickness=0, height=190)
        self.curve.pack(fill="x")
        self.history = ttk.Treeview(
            parent, columns=("Période", "Total", "Écart", "Part"),
            show="headings", height=8)
        for nom, largeur, cote in (("Période", 110, "w"), ("Total", 110, "e"),
                                   ("Écart", 100, "e"), ("Part", 80, "e")):
            self.history.heading(nom, text=nom.upper(), anchor=cote)
            self.history.column(nom, width=largeur, anchor=cote,
                                stretch=(nom == "Période"))
        self.history.pack(fill="x", pady=(10, 0))

    # ------------------------------------------------------------ donnees

    def show(self, population, config, history=None, report=None,
             source: str = "") -> None:
        """Repose l'ecran. L'historique est facultatif : la fiche vaut
        sans lui, elle est seulement plus courte."""
        self._population = population
        self._config = config
        self._history = dict(history or {})
        self._report = report
        if report is not None:
            self.source.configure(text=self._summary(report, source))
            if not self.source.winfo_manager():
                self.source.pack(fill="x", before=self.picker)
        self.picker.fill(self._entries())
        if self._person is not None:
            self._choisir(self._person)
        else:
            self.body.pack_forget()
            self.identity.configure(
                text="Cherchez un salarié par son nom ou son matricule : "
                     "la fiche se remplit quand vous en choisissez un.")

    def _summary(self, report, source: str) -> str:
        morceaux = [source, f"{report.rows} lignes",
                    f"{report.matched} salariés",
                    f"{len(report.periods)} périodes"]
        if report.periods:
            morceaux.append(f"de {report.periods[0]} à {report.periods[-1]}")
        for nombre, mot in ((report.orphans, "matricules inconnus"),
                            (report.unreadable, "lignes illisibles")):
            if nombre:
                morceaux.append(f"{nombre} {mot}")
        return " · ".join(m for m in morceaux if m)

    def _entries(self) -> List[tuple]:
        """Les salaries, dans l'ordre du fichier, avec ce qui les nomme.

        Le nom ne parait que si le parametrage l'autorise. Sinon le
        matricule suffit a retrouver quelqu'un, et c'est tout ce dont
        l'ecran a besoin.
        """
        if not self._population:
            return []
        nommer = bool(self._config.get(
            "privacy_parameters.show_identities_on_screen", True))
        sorties = []
        for personne in self._population:
            matricule = str(personne.value("employee_id") or "").strip()
            morceaux = [matricule] if matricule else []
            if nommer:
                nom = " ".join(
                    str(personne.value(champ) or "").strip()
                    for champ in ("last_name", "first_name")).strip()
                if nom:
                    morceaux.insert(0, nom)
            poste = str(personne.value(self._comparison_field()) or "").strip()
            if poste:
                morceaux.append(poste)
            if morceaux:
                sorties.append((" · ".join(morceaux), personne))
        return sorties

    def _identity(self, personne) -> str:
        """La ligne sous la recherche : de qui parle la fiche.

        Le matricule y figure toujours. C'est lui qui fait le lien avec
        l'historique, et c'est par lui qu'on verifie qu'on regarde bien
        la bonne personne.
        """
        matricule = str(personne.value("employee_id") or "").strip()
        morceaux = [f"Matricule {matricule}" if matricule
                    else "Sans matricule"]
        for nom in ("site", "job"):
            valeur = str(personne.value(nom) or "").strip()
            if valeur:
                morceaux.append(valeur)
        return " · ".join(morceaux)

    def _comparison_field(self) -> str:
        champ = str(self._config.get("career_parameters.comparison_field",
                                     "job_title") or "job_title")
        # Un poste non renseigne ne compare rien : on retombe sur le
        # metier, qui l'est presque toujours.
        if any(str(p.value(champ) or "").strip() for p in self._population):
            return champ
        return "job"

    def _choisir(self, personne) -> None:
        self._person = personne
        self.identity.configure(text=self._identity(personne))
        if not self.body.winfo_manager():
            self.body.pack(fill="both", expand=True, padx=18, pady=(12, 18))
        self._fill_state(personne)
        self._fill_standing(personne)
        self._fill_history(personne)

    # -------------------------------------------------------------- trace

    def _fill_state(self, personne) -> None:
        from ..core.reporting import format_money, format_number

        self.state.delete(*self.state.get_children())
        config = self._config
        devise = config.get("salary_parameters.currency", "EUR")
        champ = _analysis_field(config)
        plein = _full_time(personne, champ)
        lignes = [("Rémunération (temps plein)", format_money(plein, devise))]
        temps = personne.value("fte")
        if isinstance(temps, (int, float)):
            lignes.append(("Temps de travail",
                           f"{format_number(100.0 * temps, 0)} %"))
        for titre, nom in (("Poste", self._comparison_field()),
                           ("Métier", "job"),
                           ("Établissement", "site"),
                           ("Coefficient", "coefficient"),
                           ("Date d'entrée", "hire_date")):
            valeur = personne.value(nom)
            if valeur in (None, ""):
                continue
            if hasattr(valeur, "strftime"):
                valeur = f"{valeur:%d/%m/%Y}"
            elif isinstance(valeur, float) and valeur.is_integer():
                valeur = str(int(valeur))
            lignes.append((titre, str(valeur)))
        self.state.configure(height=max(len(lignes), 3))
        for titre, valeur in lignes:
            self.state.insert("", "end", values=(titre, valeur))

    def _fill_standing(self, personne) -> None:
        from ..core.reporting import format_money

        self.ruler.delete("all")
        place = cr.standing(personne, self._population, self._config,
                            self._comparison_field())
        if place is None:
            self.standing_note.configure(
                text="Sa rémunération ou son temps de travail n'est pas "
                     "connu : il n'y a rien à situer.")
            self.standing_figures.configure(text="")
            return
        if not place["published"]:
            self.standing_note.configure(
                text=f"« {place['segment']} » ne compte que "
                     f"{place['headcount']} salarié(s) : comparer "
                     "quelqu'un à si peu de collègues reviendrait à "
                     "publier leur rémunération à travers la sienne.")
            self.standing_figures.configure(text="")
            return
        devise = self._config.get("salary_parameters.currency", "EUR")
        self.standing_note.configure(
            text=f"« {place['segment']} » — {place['compared']} salariés "
                 "comparés, à temps plein.")
        self._draw_ruler(place)
        ratio = f"{place['ratio']:.2f}".replace(".", ",")
        self.standing_figures.configure(
            text=f"Rapport à la médiane du poste : {ratio}  "
                 f"({_signed(place['gap'])}).\n"
                 f"Il devance {place['rank']:.0f} % de ses pairs. "
                 f"Médiane du poste : {format_money(place['median'], devise)}.")

    def _draw_ruler(self, place) -> None:
        """La boite du poste, et le repere du salarie dessus.

        Un rapport a la mediane dit de combien il s'ecarte ; il ne dit
        pas si le poste est resserre ou ouvert. La meme difference de
        huit pour cent n'a pas le meme sens dans une grille qui tient en
        dix pour cent et dans une qui s'etale sur soixante.
        """
        from ..core.reporting import format_money

        canvas = self.ruler
        largeur = max(canvas.winfo_width(), 420)
        gauche, droite = 14, 14
        utile = max(largeur - gauche - droite, 60)
        bas, haut = place["min"], place["max"]
        etendue = (haut - bas) or 1.0
        devise = self._config.get("salary_parameters.currency", "EUR")

        def x_de(valeur):
            return gauche + utile * (valeur - bas) / etendue

        milieu = 32
        canvas.create_line(x_de(bas), milieu, x_de(haut), milieu,
                           fill=theme.LINE_STRONG)
        canvas.create_rectangle(x_de(place["q1"]), milieu - 10,
                                x_de(place["q3"]), milieu + 10,
                                outline=theme.LINE_STRONG, width=1,
                                fill=theme.GRID)
        canvas.create_line(x_de(place["median"]), milieu - 10,
                           x_de(place["median"]), milieu + 10,
                           fill=theme.MUTED, width=2)
        # Le repere est plus haut que la boite : il doit se voir meme
        # pose sur la mediane.
        x = x_de(place["amount"])
        canvas.create_line(x, milieu - 15, x, milieu + 15,
                           fill=theme.ACCENT, width=3)
        canvas.create_text(x, milieu + 26,
                           text=format_money(place["amount"], devise),
                           anchor="center", font=self.fonts.small_bold,
                           fill=theme.ACCENT)
        for valeur, ancre in ((bas, "w"), (haut, "e")):
            canvas.create_text(x_de(valeur), milieu - 22,
                               text=format_money(valeur, devise), anchor=ancre,
                               font=self.fonts.small, fill=theme.MUTED)

    def _fill_history(self, personne) -> None:
        from ..core.reporting import format_money

        self.history.delete(*self.history.get_children())
        self.curve.delete("all")
        matricule = str(personne.value("employee_id") or "").strip()
        lignes = cr.evolution(self._history.get(matricule, []))
        if not lignes:
            self.history_note.configure(
                text="Aucun historique pour ce matricule."
                     if self._history else
                     "Aucun historique chargé — « Historique… » dans la "
                     "colonne de gauche.")
            self.history.configure(height=3)
            return
        devise = self._config.get("salary_parameters.currency", "EUR")
        montants = sorted({cle for ligne in lignes for cle in ligne["amounts"]})
        self.history_note.configure(
            text=f"{len(lignes)} périodes · " + (", ".join(montants)
                                                 if montants else
                                                 "aucun montant déclaré"))
        self.history.configure(height=max(len(lignes), 3))
        for ligne in lignes:
            self.history.insert("", "end", values=(
                ligne["label"],
                format_money(ligne["total"], devise)
                if ligne["total"] is not None else "—",
                (f"{ligne['change']:+,.0f} {devise}".replace(",", " ")
                 if ligne["change"] is not None else "—"),
                _signed(ligne["change_share"])))
        self._draw_curve(lignes)

    def _draw_curve(self, lignes) -> None:
        """La remuneration periode par periode.

        L'echelle suit les donnees, et ses deux bornes sont ecrites.
        Partir de zero etait le premier choix, par prudence ; sur une
        remuneration de vingt-deux mille euros, quatre annees
        d'augmentation donnaient une droite horizontale, c'est-a-dire un
        graphique qui cache ce qu'on lui demande de montrer. Une echelle
        resserree exagere une pente — d'ou les bornes ecrites, et le
        pourcentage dans le tableau juste dessous, qui lui ne depend
        d'aucune echelle.
        """
        canvas = self.curve
        points = [(rang, ligne) for rang, ligne in enumerate(lignes)
                  if ligne["total"] is not None]
        if len(points) < 2:
            return
        largeur = max(canvas.winfo_width(), 420)
        gauche, droite, haut, bas = 16, 16, 16, 30
        utile = max(largeur - gauche - droite, 60)
        hauteur = 190 - haut - bas
        montants = [ligne["total"] for _r, ligne in points]
        bas_echelle, haut_echelle = min(montants), max(montants)
        marge = (haut_echelle - bas_echelle) * 0.25 or max(haut_echelle * 0.02,
                                                           1.0)
        bas_echelle -= marge
        haut_echelle += marge
        etendue = (haut_echelle - bas_echelle) or 1.0
        pas = utile / max(len(lignes) - 1, 1)

        def xy(rang, total):
            return (gauche + pas * rang,
                    haut + hauteur * (1 - (total - bas_echelle) / etendue))

        canvas.create_line(gauche, haut + hauteur, gauche + utile,
                           haut + hauteur, fill=theme.LINE)
        from ..core.reporting import format_money

        devise = self._config.get("salary_parameters.currency", "EUR")
        for valeur, y in ((haut_echelle, haut),
                          (bas_echelle, haut + hauteur)):
            canvas.create_text(gauche + utile, y - 7,
                               text=format_money(valeur, devise), anchor="e",
                               font=self.fonts.small, fill=theme.FAINT)
        trace = []
        for rang, ligne in points:
            trace.extend(xy(rang, ligne["total"]))
        canvas.create_line(*trace, fill=theme.ACCENT, width=2)
        for rang, ligne in points:
            x, y = xy(rang, ligne["total"])
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=theme.ACCENT,
                               outline=theme.CANVAS, width=1)
        for rang, ligne in enumerate(lignes):
            canvas.create_text(gauche + pas * rang, haut + hauteur + 14,
                               text=ligne["label"], anchor="center",
                               font=self.fonts.small, fill=theme.MUTED)


def _analysis_field(config) -> str:
    from ..core.config import analysis_field

    return analysis_field(config)


def _full_time(personne, champ) -> Optional[float]:
    from ..core.normalize import full_time_amount

    return full_time_amount(personne, champ)


def _signed(valeur) -> str:
    if valeur is None:
        return "—"
    return f"{valeur:+.1f} %".replace(".", ",")
