"""Parametrage des champs, depuis l'interface.

La configuration a toujours ete un fichier JSON editable au bloc-notes : ce
qui garantit qu'aucune regle n'est codee en dur, et que l'IT peut auditer
l'integralite du parametrage. Mais demander a un utilisateur RH d'ouvrir un
JSON pour declarer sa colonne "Direction" revient a lui fermer la porte.

Cette fenetre ecrit ce meme fichier, sans le remplacer : ce qu'elle produit
reste lisible, versionnable et modifiable a la main. Elle n'invente aucun
parametre — elle expose ceux qui existent.

Rien n'y est calcule : elle lit les en-tetes du fichier charge et ecrit
`population_mapping.json`. Aucune donnee individuelle ne la traverse, et
aucune valeur de cellule n'est enregistree.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any, Dict, List, Optional, Sequence

from ..core.config import Configuration, write_configuration
from ..core.errors import CompensationError
from ..core import palette
from ..core.mapping import normalise_label
from ..core.segmentation import CORE_FIELDS, max_filter_values
from . import theme
from .theme import (Card, CheckRow, Fonts, TabBar, attach_scrollbar,
                    bind_wheel)

#: Champ conserve mais jamais associe a une colonne.
IGNORED = "(ignorée)"

#: Entree de liste ouvrant la creation d'un champ absent du modele.
NEW_FIELD = "+ nouveau champ…"

#: Entree de liste qui fait d'une colonne un axe d'analyse et un filtre,
#: sans rien demander : c'est le cas courant — direction, etablissement,
#: revue du personnel, convention. Le nom technique se deduit de
#: l'intitule, et l'intitule reste celui du fichier.
ORGANISATION = "Organisation (axe et filtre)"

#: Entree de liste qui fait d'une colonne un montant : une prime maison,
#: un treizieme mois, une indemnite. Elle devient une colonne du classeur,
#: ecrite en monnaie, et peut servir de champ d'analyse. Sans elle, une
#: colonne creee depuis l'ecran devenait toujours un axe de texte, et une
#: prime ne pouvait se declarer qu'au bloc-notes.
MONTANT = "Montant (rémunération, prime…)"

#: Les entrees qui ne designent pas un champ existant : elles commandent
#: quelque chose au lieu de nommer.
_COMMANDES = (IGNORED, NEW_FIELD, ORGANISATION, MONTANT)

#: Champs calcules a partir des dates : aucune colonne du fichier ne les
#: porte, les proposer a l'association n'aurait pas de sens.
DERIVED_FIELDS = ("age_years", "age_band", "tenure_years", "tenure_band")

#: Les champs calcules n'ont pas d'alias dans le mapping : leur libelle par
#: defaut ne peut venir que d'ici.
_DERIVED_LABELS = {
    "age_years": "Âge",
    "age_band": "Tranche d'âge",
    "tenure_years": "Ancienneté",
    "tenure_band": "Tranche d'ancienneté",
}


def candidate_fields(config: Configuration) -> List[str]:
    """Champs auxquels une colonne du fichier peut etre associee."""
    declared = list(config.get("population_mapping.fields", {}) or {})
    return sorted((set(declared) | set(CORE_FIELDS)) - set(DERIVED_FIELDS))


def default_label(config: Configuration, field_name: str) -> str:
    """Libelle lisible d'un champ non encore declare comme dimension.

    Le premier alias du mapping est le nom que l'utilisateur emploie dans
    son fichier : c'est le meilleur libelle par defaut disponible, et il
    evite d'afficher un nom technique dans une liste de parametres.
    """
    aliases = (config.get("population_mapping.fields", {}) or {}).get(field_name)
    if aliases:
        return aliases[0]
    return _DERIVED_LABELS.get(field_name, field_name)


def candidate_dimensions(config: Configuration) -> List[str]:
    """Champs pouvant servir de critere ou d'axe.

    Les champs nominatifs en sont exclus : segmenter par nom produirait des
    groupes d'une personne et ferait entrer une identite dans une
    restitution, ce que le traitement des donnees RH interdit. Ils restent
    associables a une colonne — ils servent au controle des doublons — mais
    ne sont jamais proposes comme axe.
    """
    personal = set(config.get("population_mapping.personal", []) or [])
    available = set(candidate_fields(config)) | set(DERIVED_FIELDS)
    return sorted(available - personal)


def suggest_field_name(header: str, taken: Sequence[str]) -> str:
    """Nom de champ technique deduit d'un en-tete, sans collision.

    Les noms de champ restent ASCII : ils s'ecrivent en ligne de commande
    (--filtre "direction=Nord"), ou un accent serait une source d'erreur de
    saisie plutot qu'un confort.
    """
    base = normalise_label(header).replace(" ", "_").strip("_") or "champ"
    if base[0].isdigit():
        base = f"c_{base}"
    name, suffix = base, 2
    while name in taken:
        name, suffix = f"{base}_{suffix}", suffix + 1
    return name


def build_mapping_section(current: Dict[str, Any],
                          assignments: Dict[str, str],
                          dimension_flags: Dict[str, Dict[str, Any]],
                          limit: int,
                          money: Optional[Sequence[str]] = None
                          ) -> Dict[str, Any]:
    """Compose la section a ecrire, a partir des choix de la fenetre.

    Fonction pure : c'est elle que les tests exercent, sans ouvrir de
    fenetre. L'ecran ne fait que l'alimenter.

    `money` liste les champs que l'ecran vient de declarer comme montants.
    Ils entrent dans « numeric » et dans « money » : un montant se lit en
    nombre et s'ecrit en monnaie, et l'un sans l'autre ne veut rien dire.
    """
    section = {key: value for key, value in current.items()}
    fields: Dict[str, List[str]] = {
        name: list(aliases)
        for name, aliases in (current.get("fields") or {}).items()
    }

    # Une colonne mise a « ignoree » cesse d'etre un alias, de ce champ
    # comme de tout autre. Sans cela, l'ecran disait « ignoree » et la
    # colonne restait declaree dans les parametres : l'analyse suivante la
    # relisait, sans que rien ne le signale. Une fenetre de reglage qui
    # n'obtient pas ce qu'elle affiche ne sert a rien.
    ignored = {normalise_label(header)
               for header, field_name in assignments.items()
               if field_name == IGNORED}
    if ignored:
        fields = {name: [alias for alias in aliases
                         if normalise_label(alias) not in ignored]
                  for name, aliases in fields.items()}
        # Un champ dont il ne reste aucun alias n'est plus associe a rien :
        # le retirer est ce qui permet au controle des champs obligatoires
        # de s'apercevoir qu'il manque.
        fields = {name: aliases for name, aliases in fields.items() if aliases}

    # Une colonne associee a un champ en devient l'alias principal : c'est ce
    # qui rend l'association durable d'un fichier a l'autre.
    for header, field_name in assignments.items():
        if field_name == IGNORED:
            continue
        aliases = fields.setdefault(field_name, [])
        others = [alias for alias in aliases
                  if normalise_label(alias) != normalise_label(header)]
        fields[field_name] = [header] + others
    section["fields"] = fields

    ordered: List[Dict[str, Any]] = []
    # Une dimension declaree a la main mais absente de l'ecran — un champ
    # nominatif, que la fenetre refuse de proposer — est reconduite telle
    # quelle : la fenetre ne doit pas supprimer en silence ce qu'elle
    # n'affiche pas.
    for entry in current.get("dimensions") or []:
        name = entry.get("field") if isinstance(entry, dict) else entry
        if name and name not in dimension_flags:
            ordered.append(entry)
    for field_name, flags in dimension_flags.items():
        if not flags.get("declared"):
            continue
        ordered.append({"field": field_name,
                        "label": flags.get("label") or field_name})
    section["dimensions"] = ordered

    # Un champ qui n'a plus aucune colonne n'est plus ni un nombre ni un
    # montant : l'y laisser aurait pose au classeur une colonne titree et
    # vide. Les champs que l'ecran ne connait pas — declares a la main
    # pour un autre fichier — sont reconduits tels quels.
    perdus = {name for name in (current.get("fields") or {})
              if name not in fields}
    nouveaux = [name for name in (money or []) if name in fields]
    for clé in ("numeric", "money"):
        retenus = [name for name in (current.get(clé) or [])
                   if name not in perdus]
        retenus += [name for name in nouveaux if name not in retenus]
        section[clé] = retenus

    section["max_filter_values"] = limit
    return section


class SettingsWindow(tk.Toplevel):
    """Fenetre de parametrage des colonnes, filtres et axes d'analyse."""

    def __init__(self, master: tk.Misc, configuration: Configuration,
                 config_dir: str, fonts: Fonts,
                 headers: Optional[Sequence[str]] = None,
                 on_saved=None, samples: Optional[Sequence[Sequence[Any]]] = None):
        super().__init__(master, background=theme.GROUND)
        self.title("Paramètres")
        self.configuration = configuration
        self.config_dir = config_dir
        self.fonts = fonts
        self.headers = list(headers or [])
        self.on_saved = on_saved
        #: Quelques lignes du fichier : voir ce que porte une colonne vaut
        #: mieux que lire son intitule. « Direction » peut contenir des
        #: noms de region comme des noms de personnes.
        self.samples = [list(ligne) for ligne in (samples or [])]
        #: Une case par colonne : « proposé comme filtre et comme axe ».
        self.dimension_vars: Dict[str, tk.BooleanVar] = {}
        #: L'intitule de chaque colonne, pour en eteindre l'alerte.
        self._labels_widgets: Dict[str, tk.Label] = {}
        self.assignments: Dict[str, tk.StringVar] = {}
        self.rows: Dict[str, Dict[str, Any]] = {}
        #: Champs que l'ecran vient de declarer comme montants. Ceux que la
        #: configuration porte deja n'y figurent pas : `build_mapping_section`
        #: part d'elle, et cet ensemble ne fait qu'ajouter.
        self._money: set = set()
        self._boxes: List[ttk.Combobox] = []
        self.transient(master)
        # La fenetre s'ouvre sur ce qu'elle nomme — les colonnes — et non
        # sur l'apparence : c'est la premiere chose qu'on vient y faire.
        self.geometry("1060x760")
        self.minsize(820, 480)
        self._build()
        self.grab_set()

    # ------------------------------------------------------------- montage

    #: Les quatre sujets de cette fenetre, dans l'ordre ou l'on s'en sert :
    #: on associe d'abord ses colonnes, puis on regle ce qui se publie, ce
    #: qui s'exporte, et enfin l'apparence.
    SECTIONS = (("colonnes", "Colonnes du fichier"),
                ("confidentialite", "Confidentialité"),
                ("export", "Export"),
                ("apparence", "Apparence"))

    #: Ce que chaque section enregistre. La phrase se lit sous la barre :
    #: savoir ou part un reglage fait partie du reglage.
    FICHIERS = {
        "colonnes": "population_mapping.json",
        "confidentialite": "privacy_parameters.json",
        "export": "export_parameters.json",
        "apparence": "theme_parameters.json",
    }

    def _build(self) -> None:
        """Quatre sujets, quatre pages.

        Les cinq sections s'empilaient dans une seule colonne defilante :
        pour changer un seuil de confidentialite, il fallait traverser
        vingt-deux lignes de colonnes et deux paragraphes sur l'export. On
        ne cherchait pas un reglage, on le retrouvait.
        """
        head = tk.Frame(self, background=theme.CANVAS)
        head.pack(fill="x")
        tk.Label(head, text="Paramètres", background=theme.CANVAS,
                 foreground=theme.INK,
                 font=self.fonts.title).pack(anchor="w", padx=22,
                                             pady=(18, 10))
        self.tabbar = TabBar(head, self.fonts, on_change=self._show_section)
        self.tabbar.pack(fill="x", padx=22)
        self.origin = tk.Label(head, text="", background=theme.CANVAS,
                               foreground=theme.FAINT, font=self.fonts.small,
                               justify="left")
        self.origin.pack(anchor="w", padx=22, pady=(8, 10))

        actions = tk.Frame(self, background=theme.GROUND)
        actions.pack(side="bottom", fill="x", padx=22, pady=16)
        ttk.Button(actions, text="Enregistrer", style="Primary.TButton",
                   command=self.save).pack(side="right")
        ttk.Button(actions, text="Annuler", style="GhostGround.TButton",
                   command=self.destroy).pack(side="right", padx=(0, 10))
        self.feedback = tk.Label(actions, text="", background=theme.GROUND,
                                 foreground=theme.MUTED, font=self.fonts.small,
                                 justify="left", wraplength=520)
        self.feedback.pack(side="left")

        # Le corps : un cadre par section, un seul empile a la fois. Chacun
        # defile pour son compte, et la barre d'onglets reste visible.
        self.body = tk.Frame(self, background=theme.GROUND)
        self.body.pack(fill="both", expand=True)
        self.pages: Dict[str, tk.Frame] = {}
        for clef, intitule in self.SECTIONS:
            self.pages[clef] = tk.Frame(self.body, background=theme.GROUND)
            self.tabbar.add(clef, intitule)

        self._prepare_dimensions()
        colonnes = self._scrollable(self.pages["colonnes"],
                                    background=theme.GROUND)
        self._build_columns(colonnes)
        self._build_dimensions(colonnes)
        self._build_privacy(self._scrollable(self.pages["confidentialite"],
                                             background=theme.GROUND))
        self._build_export(self._scrollable(self.pages["export"],
                                            background=theme.GROUND))
        self._build_theme(self._scrollable(self.pages["apparence"],
                                           background=theme.GROUND))
        self.tabbar.select(self.SECTIONS[0][0])

    def _show_section(self, key: str) -> None:
        for nom, cadre in self.pages.items():
            cadre.pack_forget()
        self.pages[key].pack(fill="both", expand=True)
        self.origin.configure(
            text=f"Enregistré dans {self.FICHIERS.get(key, '')} — "
                 "modifiable au bloc-notes.")

    def _build_theme(self, parent: tk.Widget) -> None:
        """Choix du theme, montre plutot que decrit.

        Les couleurs ne se saisissent pas une par une : quatre jeux complets
        sont proposes, tous verifies en contraste. On ne peut donc pas rendre
        l'outil illisible depuis cet ecran, ni donner du vert a « critique ».
        Chaque jeu montre ses teintes : c'est plus court a lire qu'un nom.
        """
        band = tk.Frame(parent, background=theme.GROUND)
        band.pack(fill="x", padx=22, pady=(4, 0))
        tk.Frame(band, height=1, background=theme.LINE).pack(fill="x",
                                                             pady=(0, 12))
        tk.Label(band, text="Le thème colore la fenêtre et les documents "
                            "produits. Les documents en tiennent compte dès "
                            "l'enregistrement ; la fenêtre, au prochain "
                            "démarrage.",
                 background=theme.GROUND, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=880,
                 justify="left").pack(anchor="w", pady=(2, 10))

        row = tk.Frame(band, background=theme.GROUND)
        row.pack(fill="x", pady=(0, 4))
        self.theme_var = tk.StringVar(
            value=str(self.configuration.get("theme_parameters.theme",
                                             palette.DEFAULT_THEME)))
        self._theme_cards: Dict[str, Dict[str, Any]] = {}
        for entry in palette.THEMES.values():
            self._theme_card(row, entry)
        self._show_theme()

    def _build_privacy(self, parent: tk.Widget) -> None:
        """Ce que l'ecran a le droit de montrer — et lui seul.

        Le paragraphe 6 exige des identifiants *anonymisables*, pas
        anonymises : identifier un salarie a l'ecran est le geste meme de
        l'analyse. Ce reglage ne porte que sur la fenetre. Les documents
        produits, les exports et le journal technique n'en dependent pas :
        l'identite ne transite jamais par le resultat d'analyse, elle est
        reconstruite a l'ecran depuis le fichier charge.
        """
        band = tk.Frame(parent, background=theme.GROUND)
        band.pack(fill="x", padx=22, pady=(4, 0))
        tk.Frame(band, height=1, background=theme.LINE).pack(fill="x",
                                                             pady=(0, 12))
        # Le seuil de publication : le nombre en deca duquel aucun calcul
        # n'est pose. Il etait dans un fichier JSON, ou personne ne va le
        # chercher, alors que c'est le reglage qui decide de ce que la
        # page des ecarts affiche ou tait.
        # Trois seuils, et non un seul affiche sur trois en service. Un
        # utilisateur qui pose « 5 » ici et voit un groupe de huit sans
        # boite a moustaches ne peut pas deviner qu'un second seuil, a dix,
        # gouverne les graphiques : il conclut que le reglage ne marche pas.
        # Ils sont donc tous les trois ici, nommes par ce qu'ils decident.
        self.threshold_var = self._threshold(
            band, "Ne rien calculer en dessous de",
            "privacy_parameters.min_headcount_publish", 5,
            "Un groupe plus petit serait identifiable : rien n'est publié pour lui, ni à l'écran ni dans les documents.")
        self.warning_var = self._threshold(
            band, "Avertir sur l'interprétation en dessous de",
            "privacy_parameters.min_headcount_warning", 10,
            "Les chiffres restent publiés, avec une mise en garde : sur un petit effectif, une médiane bouge d'un recrutement.")
        self.chart_var = self._threshold(
            band, "Ne pas tracer de graphique en dessous de",
            "privacy_parameters.min_headcount_chart", 10,
            "Une boîte à moustaches dessine la position de chaque salarié : elle en demande plus qu'un tableau.")
        tk.Label(band,
                 text="Une comparaison femmes / hommes demande le seuil de "
                      "publication DE CHAQUE CÔTÉ : avec 5, il faut 5 femmes "
                      "et 5 hommes, donc au moins 10 personnes, et un groupe "
                      "de 8 reste sans écart publié. L'onglet "
                      "« Organigramme » fait exception et ne masque rien : "
                      "il ne sort pas de l'écran, et porte sur une équipe "
                      "que vous venez de désigner.",
                 background=theme.GROUND, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=880,
                 justify="left").pack(anchor="w", pady=(2, 10))

        self.identities_var = tk.BooleanVar(
            value=bool(self.configuration.get(
                "privacy_parameters.show_identities_on_screen", True)))
        CheckRow(band, "Afficher les noms des salariés à l'écran",
                 self.identities_var, self.fonts).pack(anchor="w",
                                                       pady=(6, 2))
        tk.Label(band,
                 text="Décochée, la fenêtre s'en tient à la référence "
                      "anonyme. Dans les deux cas, les documents produits et "
                      "le journal technique restent sans nom ni prénom : ce "
                      "réglage ne porte que sur l'écran. Seul le classeur "
                      "peut en porter, et seulement si vous y joignez le "
                      "fichier importé (ci-dessus).",
                 background=theme.GROUND, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=880,
                 justify="left").pack(anchor="w", pady=(0, 8))

    def _threshold(self, parent: tk.Widget, label: str, path: str,
                   default: int, note: str) -> tk.StringVar:
        """Un seuil d'effectif : son libelle, son compteur, sa portee.

        La portee est ecrite sous chacun, et c'est elle qui compte : trois
        nombres sans leur portee se confondent.
        """
        ligne = tk.Frame(parent, background=theme.GROUND)
        ligne.pack(anchor="w", pady=(6, 0))
        tk.Label(ligne, text=label, background=theme.GROUND,
                 foreground=theme.INK,
                 font=self.fonts.body).pack(side="left", padx=(0, 8))
        variable = tk.StringVar(
            value=str(self.configuration.number(path, default,
                                                minimum=1, integer=True)))
        ttk.Spinbox(ligne, from_=1, to=200, width=5, increment=1,
                    textvariable=variable,
                    font=self.fonts.body).pack(side="left")
        tk.Label(ligne, text="salariés", background=theme.GROUND,
                 foreground=theme.INK,
                 font=self.fonts.body).pack(side="left", padx=(8, 0))
        tk.Label(parent, text=note, background=theme.GROUND,
                 foreground=theme.MUTED, font=self.fonts.small,
                 wraplength=880, justify="left").pack(anchor="w",
                                                      pady=(1, 0))
        return variable

    def _build_export(self, parent: tk.Widget) -> None:
        """Ce que le classeur emporte — et ce que cela implique.

        Verifier un calcul demande les valeurs sur lesquelles il porte :
        un controle ne se fait pas sur des agregats. Le classeur peut donc
        emporter les salaries retenus, le fichier importe tel qu'il a ete
        lu, et des onglets qui refont chaque chiffre en formules. C'est de
        la donnee nominative, et c'est pourquoi le reglage est ici, decoche,
        et dit ce qu'il fait.
        """
        band = tk.Frame(parent, background=theme.GROUND)
        band.pack(fill="x", padx=22, pady=(4, 0))
        tk.Frame(band, height=1, background=theme.LINE).pack(fill="x",
                                                             pady=(0, 12))
        self.individual_var = tk.BooleanVar(
            value=bool(self.configuration.get(
                "export_parameters.include_individual_data", False)))
        self.audit_var = tk.BooleanVar(
            value=bool(self.configuration.get(
                "export_parameters.include_source_file", False)))
        CheckRow(band, "Exporter les données individuelles dans le classeur",
                 self.individual_var, self.fonts).pack(anchor="w",
                                                       pady=(6, 2))
        CheckRow(band, "Joindre le fichier importé et les onglets de "
                       "contrôle", self.audit_var,
                 self.fonts).pack(anchor="w", pady=(2, 2))
        tk.Label(band,
                 text="Les onglets de contrôle refont chaque chiffre publié "
                      "en formules, à partir des données individuelles : la "
                      "colonne « Écart » doit valoir zéro partout. Ils "
                      "supposent donc l'export des données individuelles, "
                      "qui portent la référence de chaque salarié et, avec "
                      "le fichier importé, son identité. Décochées, ces deux "
                      "cases laissent le classeur aux seuls agrégats.",
                 background=theme.GROUND, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=880,
                 justify="left").pack(anchor="w", pady=(0, 8))
        # Le controle ne peut pas se poser sans les valeurs : les deux
        # reglages se suivent plutot que de laisser une case cochee sans
        # effet.
        self.audit_var.trace_add("write", self._follow_audit)
        self.individual_var.trace_add("write", self._follow_individual)

    def _follow_audit(self, *_args) -> None:
        if self.audit_var.get():
            self.individual_var.set(True)

    def _follow_individual(self, *_args) -> None:
        if not self.individual_var.get():
            self.audit_var.set(False)

    def _theme_card(self, parent: tk.Widget, entry) -> None:
        card = tk.Frame(parent, background=theme.GROUND, cursor="hand2")
        card.pack(side="left", padx=(0, 26))
        chips = tk.Frame(card, background=theme.GROUND)
        chips.pack(anchor="w")
        # Les teintes montrees sont celles qui portent la lecture : l'accent,
        # l'encre, le gris secondaire, puis le couple femmes / hommes.
        shown = (entry.palette.accent, entry.palette.ink, entry.palette.muted,
                 entry.palette.female, entry.palette.male)
        for colour in shown:
            chip = tk.Frame(chips, background=colour, width=17, height=17)
            chip.pack_propagate(False)
            chip.pack(side="left", padx=(0, 3))
        name = tk.Label(card, text=entry.label, background=theme.GROUND,
                        foreground=theme.INK, font=self.fonts.body_bold)
        name.pack(anchor="w", pady=(6, 0))
        mark = tk.Frame(card, height=2, background=theme.GROUND)
        mark.pack(fill="x", pady=(4, 0))
        self._theme_cards[entry.key] = {"name": name, "mark": mark,
                                        "help": entry.description}
        for widget in (card, chips, name, *chips.winfo_children()):
            widget.bind("<Button-1>",
                        lambda _e, key=entry.key: self._choose_theme(key))
        self._describe_on_hover(card, entry)

    def _describe_on_hover(self, card: tk.Widget, entry) -> None:
        """Le detail du theme s'affiche au survol, pres des boutons.

        Quatre descriptions ecrites en toutes lettres tiendraient plus
        de place que la bande entiere.
        """
        for widget in [card] + list(card.winfo_children()):
            widget.bind("<Enter>",
                        lambda _e, text=entry.description:
                        self.feedback.configure(text=text), add="+")
            widget.bind("<Leave>",
                        lambda _e: self.feedback.configure(text=""), add="+")

    def _choose_theme(self, key: str) -> None:
        self.theme_var.set(key)
        self._show_theme()

    def _show_theme(self) -> None:
        """Marque le theme retenu d'un filet, sans cadre ni case a cocher."""
        chosen = self.theme_var.get()
        for key, card in self._theme_cards.items():
            selected = key == chosen
            card["name"].configure(
                foreground=theme.INK if selected else theme.MUTED)
            card["mark"].configure(
                background=theme.ACCENT if selected else theme.GROUND)

    def _scrollable(self, parent: tk.Widget,
                    background: Optional[str] = None) -> tk.Frame:
        background = background or theme.CANVAS
        canvas = tk.Canvas(parent, background=background,
                           highlightthickness=0)
        bar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview,
                            style="Flat.Vertical.TScrollbar")
        bar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        attach_scrollbar(canvas, bar, side="right", fill="y",
                         before=canvas)
        inner = tk.Frame(canvas, background=background)
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(window, width=e.width))
        bind_wheel(canvas, self)
        return inner

    def _build_columns(self, parent: tk.Widget) -> None:
        """Une ligne par colonne du fichier : ce qu'elle porte, ce qu'elle
        devient.

        Le geste que l'on vient faire ici est simple et tient en une phrase :
        « cette colonne-la, c'est le salaire ; celles-ci, ce sont mes axes
        d'analyse ; le reste, je n'en veux pas ». Il se faisait en deux
        endroits — associer la colonne a un champ ici, cocher le champ
        comme dimension la-bas — et il fallait avoir compris que les deux
        listes parlaient de la meme chose. Une ligne par colonne, avec sa
        case au bout, dit la meme chose en un seul geste.

        Les premieres valeurs du fichier sont montrees : « Direction » peut
        contenir des regions comme des noms de personnes, et l'intitule seul
        ne permet pas de trancher.
        """
        card = Card(parent, padding=0)
        card.pack(fill="x", padx=22, pady=(16, 0))
        #: Retenu pour ce qu'il a coute : empile parmi des sections de
        #: hauteur fixe, ce bloc tombait a deux pixels de haut et la
        #: fonction devenait introuvable. Un test mesure sa hauteur.
        self._columns_card = card
        header = tk.Frame(card.inner, background=theme.CANVAS)
        header.pack(fill="x", padx=16, pady=(14, 8))
        if not self.headers:
            tk.Label(card.inner,
                     text="Chargez un fichier pour associer ses colonnes.",
                     background=theme.CANVAS, foreground=theme.MUTED,
                     font=self.fonts.body).pack(anchor="w", padx=16, pady=8)
            return
        tk.Label(header,
                 text="Chaque colonne reçoit un rôle. « Organisation » en "
                      "fait un axe d'analyse et un filtre — direction, "
                      "établissement, revue du personnel, ce que votre "
                      "fichier porte. Une colonne ignorée n'est pas lue.",
                 background=theme.CANVAS, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=900,
                 justify="left").pack(anchor="w", pady=(2, 0))

        légende = tk.Frame(card.inner, background=theme.CANVAS)
        légende.pack(fill="x", padx=16, pady=(8, 2))
        for texte, largeur in (("COLONNE", 22), ("PREMIÈRES VALEURS", 34),
                               ("RÔLE", 26)):
            tk.Label(légende, text=texte, background=theme.CANVAS,
                     foreground=theme.FAINT, font=self.fonts.label,
                     width=largeur, anchor="w").pack(side="left")
        tk.Label(légende, text="FILTRE ET AXE", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")

        # Pas de defilement ici : la fenetre entiere defile. Deux
        # ascenseurs imbriques obligent a viser le bon, et le geste rate
        # fait bouger l'autre.
        inner = tk.Frame(card.inner, background=theme.CANVAS)
        inner.pack(fill="x", padx=16, pady=(0, 14))

        from ..core.mapping import resolve_mapping
        resolved = resolve_mapping(self.headers, self.configuration)
        column_to_field = {column: name
                           for name, column in resolved.field_to_column.items()}
        # La liste montre des libelles — « Salaire de base », et non
        # « base_salary ». Le nom technique reste ce qui est enregistre, et
        # il reste accepte tel quel : un reglage se lit aussi au bloc-notes.
        self._labels = {name: self._label_of(name)
                        for name in candidate_fields(self.configuration)}
        choices = ([IGNORED, ORGANISATION, MONTANT, NEW_FIELD]
                   + sorted(self._labels.values(), key=str.lower))

        for index, header_name in enumerate(self.headers):
            if not str(header_name).strip():
                continue
            row = tk.Frame(inner, background=theme.CANVAS)
            row.pack(fill="x", pady=3)
            known = column_to_field.get(header_name)
            étiquette = tk.Label(
                row, text=header_name, background=theme.CANVAS,
                foreground=theme.INK_SOFT if known else theme.WARN,
                font=self.fonts.body, width=22, anchor="w")
            étiquette.pack(side="left")
            # L'ambre dit « cette colonne n'est rattachee a rien ». Elle
            # doit s'eteindre des qu'on la rattache, sinon l'ecran continue
            # d'alerter sur ce qui vient d'etre regle.
            self._labels_widgets[header_name] = étiquette
            tk.Label(row, text=self._sample_of(index), background=theme.CANVAS,
                     foreground=theme.FAINT, font=self.fonts.small, width=34,
                     anchor="w").pack(side="left")
            var = tk.StringVar(value=self._label_of(known) if known
                               else IGNORED)
            box = ttk.Combobox(row, textvariable=var, values=choices,
                               state="readonly", font=self.fonts.small,
                               width=24)
            box.pack(side="left", padx=(0, 16))
            box.bind("<<ComboboxSelected>>",
                     lambda _e, h=header_name, w=box: self._chose(h, w))
            self.assignments[header_name] = var
            self._boxes.append(box)

            coché = tk.BooleanVar(value=self._is_dimension(known))
            self.dimension_vars[header_name] = coché
            case = CheckRow(row, "", coché, self.fonts, ground=theme.CANVAS)
            case.pack(side="left")
            coché.trace_add(
                "write", lambda *_a, h=header_name: self._follow_dimension(h))

    def _label_of(self, field_name: Optional[str]) -> str:
        """Libelle lisible d'un champ. « base_salary » -> « Salaire de base »."""
        if not field_name:
            return IGNORED
        état = self.rows.get(field_name)
        if état is not None and état["label"].get().strip():
            return état["label"].get().strip()
        return default_label(self.configuration, field_name)

    def _field_of(self, value: str) -> str:
        """Champ designe par une valeur de liste.

        Accepte le libelle — c'est ce que la liste montre — comme le nom
        technique, qu'un fichier de parametres ecrit a la main peut porter
        et qu'un test peut poser directement.
        """
        if value in _COMMANDES:
            return value
        for name, libellé in getattr(self, "_labels", {}).items():
            if value == libellé:
                return name
        return value

    def _sample_of(self, index: int) -> str:
        """Les premieres valeurs distinctes d'une colonne, abregees."""
        vues: List[str] = []
        for ligne in self.samples:
            if index >= len(ligne):
                continue
            valeur = str(ligne[index] if ligne[index] is not None else "").strip()
            if valeur and valeur not in vues:
                vues.append(valeur)
            if len(vues) == 3:
                break
        texte = " · ".join(vues)
        return texte if len(texte) <= 44 else texte[:43] + "…"

    def _is_dimension(self, field_name: Optional[str]) -> bool:
        """Ce champ est-il deja propose comme filtre et comme axe ?"""
        if not field_name:
            return False
        ligne = self.rows.get(field_name)
        return bool(ligne and ligne["declared"].get())

    def _follow_dimension(self, header: str) -> None:
        """La case d'une colonne ecrit dans le champ qu'elle porte.

        Les deux etats ne sont pas dupliques : la case de la ligne est une
        commande, l'etat vit dans `rows`, qui est ce que `collect` lit. Une
        colonne ignoree n'a pas de champ ou ecrire, et sa case ne fait rien.
        """
        field_name = self._field_of(self.assignments[header].get())
        if field_name in _COMMANDES:
            return
        coché = self.dimension_vars[header].get()
        ligne = self.rows.get(field_name)
        if ligne is None:
            self.add_dimension_row(field_name, header, coché)
            return
        if ligne["declared"].get() != coché:
            ligne["declared"].set(coché)

    def _prepare_dimensions(self) -> None:
        """L'etat de chaque champ, avant tout affichage.

        Les cases des colonnes le lisent, et le panneau du dessous l'ecrit :
        il n'y a donc qu'un seul etat, et c'est lui que `collect` traduit.
        Deux jeux de cases pour une meme verite finissaient par se
        contredire — l'ecran disait « proposé », le fichier disait non.
        """
        from ..core.segmentation import dimensions as declared_dimensions

        current = {entry["field"]: entry
                   for entry in declared_dimensions(self.configuration)}
        allowed = candidate_dimensions(self.configuration)
        listed = ([name for name in current if name in allowed]
                  + [name for name in allowed if name not in current])
        for field_name in listed:
            entry = current.get(field_name)
            libellé = ((entry or {}).get("label")
                       or default_label(self.configuration, field_name))
            self.rows[field_name] = {
                "label": tk.StringVar(value=libellé),
                "declared": tk.BooleanVar(value=entry is not None),
            }

    def _build_dimensions(self, parent: tk.Widget) -> None:
        """Les champs qu'aucune colonne de ce fichier ne porte.

        L'age et l'anciennete se calculent, ils n'ont pas de colonne ; un
        fichier peut aussi ne pas porter une notion declaree pour un autre.
        Ces champs-la n'ont pas de ligne plus haut : ils se reglent ici.

        Aucun salarie n'est retire ici : ces cases decident du contenu des
        listes, pas de la population analysee.
        """
        card = Card(parent, padding=0)
        card.pack(fill="x", padx=22, pady=(14, 0))
        header = tk.Frame(card.inner, background=theme.CANVAS)
        header.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(header, text="CHAMPS SANS COLONNE",
                 background=theme.CANVAS, foreground=theme.FAINT,
                 font=self.fonts.label).pack(anchor="w")
        tk.Label(header,
                 text="L'âge et l'ancienneté se calculent à partir des "
                      "dates : aucune colonne ne les porte. Un champ coché "
                      "est proposé partout — dans « Filtrer », dans "
                      "« Comparer par », dans « Colorer par ». Cet écran ne "
                      "filtre rien et ne retire aucun salarié.",
                 background=theme.CANVAS, foreground=theme.MUTED,
                 font=self.fonts.small, wraplength=900,
                 justify="left").pack(anchor="w", pady=(2, 0))

        legend = tk.Frame(card.inner, background=theme.CANVAS)
        legend.pack(fill="x", padx=16)
        tk.Label(legend, text="CHAMP", background=theme.CANVAS,
                 foreground=theme.FAINT, font=self.fonts.label, width=22,
                 anchor="w").pack(side="left")
        tk.Label(legend, text="PROPOSÉ", background=theme.CANVAS,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")

        self._dimension_area = tk.Frame(card.inner, background=theme.CANVAS)
        self._dimension_area.pack(fill="x", padx=16, pady=(6, 10))

        # Les champs portes par une colonne se reglent sur leur ligne, plus
        # haut : les reproposer ici ferait deux cases pour une decision.
        portés = {self._field_of(var.get())
                  for var in self.assignments.values()}
        for field_name in list(self.rows):
            if field_name in portés:
                continue
            self._dimension_widget(field_name)

        foot = tk.Frame(card.inner, background=theme.CANVAS)
        foot.pack(fill="x", padx=16, pady=(0, 14))
        tk.Label(foot, text="Ne pas proposer de filtre au-delà de",
                 background=theme.CANVAS, foreground=theme.MUTED,
                 font=self.fonts.small).pack(side="left")
        self.limit_var = tk.StringVar(
            value=str(max_filter_values(self.configuration)))
        tk.Entry(foot, textvariable=self.limit_var, width=5, relief="flat",
                 background=theme.CANVAS, foreground=theme.INK_SOFT,
                 font=self.fonts.small, highlightthickness=1,
                 highlightbackground=theme.LINE,
                 highlightcolor=theme.ACCENT).pack(side="left", padx=6,
                                                   ipady=2)
        tk.Label(foot, text="valeurs distinctes", background=theme.CANVAS,
                 foreground=theme.MUTED, font=self.fonts.small).pack(side="left")

    def _dimension_widget(self, field_name: str) -> None:
        """La ligne visible d'un champ : son libelle, et sa case."""
        état = self.rows[field_name]
        row = tk.Frame(self._dimension_area, background=theme.CANVAS)
        row.pack(fill="x", pady=2)
        tk.Entry(row, textvariable=état["label"], background=theme.CANVAS,
                 foreground=theme.INK_SOFT, font=self.fonts.body, width=26,
                 relief="flat", highlightthickness=1,
                 highlightbackground=theme.CANVAS,
                 highlightcolor=theme.ACCENT).pack(side="left", ipady=3)
        CheckRow(row, "", état["declared"], self.fonts,
                 ground=theme.CANVAS).pack(side="left", padx=(12, 0))

    def _chose(self, header: str, box: "ttk.Combobox") -> None:
        """Reagit au choix d'un role pour une colonne.

        Trois cas. Un champ connu : la case de la ligne se met a l'etat de
        ce champ, et il n'y a rien d'autre a faire. « Organisation » :
        le champ est cree a partir de l'intitule, sans rien demander, et
        propose aussitot comme filtre et comme axe — c'est le cas courant.
        « Nouveau champ » : il faut un nom technique, et lui seul se
        demande, parce qu'il s'ecrit aussi en ligne de commande.
        """
        variable = self.assignments[header]
        self._repaint(header)
        if variable.get() == ORGANISATION:
            self._declare(header, box,
                          suggest_field_name(header, self._taken()))
            return
        if variable.get() == MONTANT:
            self._declare(header, box,
                          suggest_field_name(header, self._taken()),
                          montant=True)
            return
        if variable.get() != NEW_FIELD:
            # Un champ connu : la case suit l'etat de ce champ.
            case = self.dimension_vars.get(header)
            if case is not None:
                case.set(self._is_dimension(self._field_of(variable.get())))
            return
        variable.set(IGNORED)
        taken = self._taken()
        proposed = simpledialog.askstring(
            "Nouveau champ",
            f"Nom technique du champ porté par la colonne « {header} ».\n"
            "Sans accent ni espace : il s'écrit aussi en ligne de commande.",
            initialvalue=suggest_field_name(header, taken), parent=self)
        if not proposed:
            return
        name = suggest_field_name(proposed, [])
        if name in taken:
            messagebox.showwarning(
                "Nouveau champ",
                f"Le champ « {name} » existe déjà : choisissez-le dans la "
                "liste plutôt que d'en créer un second.", parent=self)
            return
        self._declare(header, box, name)

    def _repaint(self, header: str) -> None:
        """Rallume ou eteint l'alerte d'une colonne, selon son role."""
        étiquette = self._labels_widgets.get(header)
        if étiquette is None:
            return
        rattachée = self.assignments[header].get() not in (IGNORED, NEW_FIELD,
                                                            MONTANT)
        étiquette.configure(foreground=theme.INK_SOFT if rattachée
                            else theme.WARN)

    def _taken(self) -> set:
        """Noms de champ deja pris : ceux du modele et ceux de l'ecran."""
        return set(candidate_fields(self.configuration)) | set(self.rows)

    def _declare(self, header: str, box: "ttk.Combobox", name: str,
                 montant: bool = False) -> None:
        """Cree le champ porte par une colonne et l'offre a toutes les autres.

        Sans cette derniere partie, une notion declaree sur une colonne
        restait invisible pour les suivantes : deux colonnes d'un meme
        fichier ne pouvaient pas parler de la meme chose.

        Un montant ne devient pas un axe : segmenter par « prime » ferait
        une modalite par valeur distincte, soit une ligne par salarie. Il
        devient une colonne chiffree du classeur, et un champ d'analyse
        possible.
        """
        self._labels[name] = header
        values = [valeur for valeur in box.cget("values")] + [header]
        for other in self._boxes:
            other.configure(values=values)
        self.assignments[header].set(header)
        self._repaint(header)
        if montant:
            self._money.add(name)
            case = self.dimension_vars.get(header)
            if case is not None:
                case.set(False)
            return
        self._money.discard(name)
        self.add_dimension_row(name, header, True)
        case = self.dimension_vars.get(header)
        if case is not None:
            case.set(True)

    def add_dimension_row(self, field_name: str, label: str,
                          declared: bool) -> None:
        """Declare un champ, et le montre s'il n'a pas de colonne.

        Un champ cree depuis une colonne se regle sur sa ligne : lui donner
        en plus une ligne ici ferait deux cases pour une decision.
        """
        état = self.rows.get(field_name)
        if état is None:
            état = {"label": tk.StringVar(value=label),
                    "declared": tk.BooleanVar(value=declared)}
            self.rows[field_name] = état
        else:
            état["label"].set(label)
            état["declared"].set(declared)
        if field_name in {self._field_of(var.get())
                          for var in self.assignments.values()}:
            return
        if getattr(self, "_dimension_area", None) is not None:
            self._dimension_widget(field_name)

    # ---------------------------------------------------------- validation

    def collect(self) -> Dict[str, Any]:
        """Traduit l'ecran en section de configuration, ou leve."""
        try:
            limit = int(self.limit_var.get().strip())
        except ValueError:
            raise CompensationError(
                "Le nombre de valeurs distinctes doit être un entier.",
                technical=f"non integer limit: {self.limit_var.get()!r}",
            ) from None
        if limit < 1:
            raise CompensationError(
                "Le nombre de valeurs distinctes doit valoir au moins 1 : "
                "à zéro, aucun filtre ne serait jamais proposé.",
                technical=f"limit out of range: {limit}",
            )

        assignments = {header: self._field_of(var.get())
                       for header, var in self.assignments.items()}
        used: Dict[str, str] = {}
        for header, field_name in assignments.items():
            if field_name == IGNORED:
                continue
            if field_name in used:
                # Deux colonnes sur un meme champ : l'une ecraserait l'autre
                # en silence, et l'analyse porterait sur la mauvaise.
                raise CompensationError(
                    f"Les colonnes \"{used[field_name]}\" et \"{header}\" "
                    f"sont toutes deux associées au champ \"{field_name}\". "
                    "Un champ ne peut recevoir qu'une colonne.",
                    technical=f"duplicate field assignment: {field_name}",
                )
            used[field_name] = header

        flags = {name: {"label": row["label"].get().strip(),
                        "declared": row["declared"].get()}
                 for name, row in self.rows.items()}
        section = build_mapping_section(
            self.configuration.section("population_mapping"),
            assignments, flags, limit, money=sorted(self._money))

        # La meme regle que le moteur, et non la liste brute : celle-ci est
        # vide par defaut, et l'ecran aurait laisse detacher la colonne de
        # remuneration pour n'echouer qu'a l'analyse suivante.
        from ..core.mapping import required_fields

        données = self.configuration.as_dict()
        données["population_mapping"] = section
        required = required_fields(Configuration(données))
        # Ce qui compte est qu'une colonne *de ce fichier* porte le champ,
        # et non qu'il subsiste une orthographe dans les parametres : un
        # champ obligatoire garde volontiers d'autres alias, prevus pour
        # d'autres fichiers, et le controle ne s'apercevait alors de rien.
        # Sans fichier charge, il n'y a rien a controler.
        missing = ([name for name in required if name not in used]
                   if self.headers else [])
        if missing:
            # Le libelle, jamais le nom technique : « base_salary » ne dit
            # rien a qui cherche sa colonne dans un fichier de paie.
            noms = ", ".join(f"« {self._label_of(name)} »" for name in missing)
            raise CompensationError(
                "L'analyse a besoin de ces champs, et plus aucune colonne "
                f"ne les porte : {noms}.",
                technical=f"required fields unmapped: {missing}",
            )
        return section

    def save(self) -> None:
        try:
            section = self.collect()
        except CompensationError as error:
            messagebox.showwarning("Paramètres", str(error), parent=self)
            return
        directory = self.config_dir
        while True:
            try:
                path = write_configuration(directory, "population_mapping",
                                           section)
            except CompensationError as error:
                # Un dossier de configuration en lecture seule est un cas
                # normal d'installation : on propose d'en choisir un autre
                # plutot que de perdre la saisie.
                if not messagebox.askretrycancel(
                        "Paramètres",
                        f"{error}\n\nChoisir un autre dossier ?", parent=self):
                    return
                chosen = filedialog.askdirectory(
                    parent=self, title="Dossier de configuration")
                if not chosen:
                    return
                directory = chosen
                continue
            break
        # Le theme part dans son propre fichier : une section par sujet, et
        # un utilisateur qui l'ouvre au bloc-notes y trouve une seule ligne.
        # Elle est relue puis completee, et non remplacee par la seule
        # valeur que l'ecran connait : ecrite en dur, elle effacait les
        # autres reglages du fichier — la duree de l'ecran d'accueil
        # disparaissait a chaque enregistrement des colonnes. La page
        # invite a editer ces fichiers au bloc-notes ; elle ne peut pas
        # effacer ensuite ce qu'on y a ecrit.
        theme = dict(self.configuration.section("theme_parameters"))
        theme["theme"] = self.theme_var.get()
        write_configuration(directory, "theme_parameters", theme)
        # La section est reecrite entiere : les seuils d'effectif qui la
        # partagent doivent survivre a l'enregistrement du reglage d'ecran.
        privacy = dict(self.configuration.section("privacy_parameters"))
        privacy["show_identities_on_screen"] = bool(self.identities_var.get())
        # Une saisie illisible garde la valeur en place : le seuil protege
        # des personnes, il ne se perd pas sur une frappe.
        for clef, variable in (
                ("min_headcount_publish", self.threshold_var),
                ("min_headcount_warning", self.warning_var),
                ("min_headcount_chart", self.chart_var)):
            try:
                saisi = int(str(variable.get()).strip())
            except ValueError:
                continue
            if saisi >= 1:
                privacy[clef] = saisi
        write_configuration(directory, "privacy_parameters", privacy)
        export = dict(self.configuration.section("export_parameters"))
        export["include_individual_data"] = bool(self.individual_var.get())
        export["include_source_file"] = bool(self.audit_var.get())
        write_configuration(directory, "export_parameters", export)
        if self.on_saved:
            self.on_saved(directory, path)
        self.destroy()
