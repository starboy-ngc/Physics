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
from .theme import (Card, CheckRow, Fonts, attach_scrollbar,
                    bind_wheel)

#: Champ conserve mais jamais associe a une colonne.
IGNORED = "(ignorée)"

#: Entree de liste ouvrant la creation d'un champ absent du modele.
NEW_FIELD = "+ nouveau champ…"

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
                          limit: int) -> Dict[str, Any]:
    """Compose la section a ecrire, a partir des choix de la fenetre.

    Fonction pure : c'est elle que les tests exercent, sans ouvrir de
    fenetre. L'ecran ne fait que l'alimenter.
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
    section["max_filter_values"] = limit
    return section


class SettingsWindow(tk.Toplevel):
    """Fenetre de parametrage des colonnes, filtres et axes d'analyse."""

    def __init__(self, master: tk.Misc, configuration: Configuration,
                 config_dir: str, fonts: Fonts,
                 headers: Optional[Sequence[str]] = None,
                 on_saved=None):
        super().__init__(master, background=theme.GROUND)
        self.title("Paramètres")
        self.configuration = configuration
        self.config_dir = config_dir
        self.fonts = fonts
        self.headers = list(headers or [])
        self.on_saved = on_saved
        self.assignments: Dict[str, tk.StringVar] = {}
        self.rows: Dict[str, Dict[str, Any]] = {}
        self._boxes: List[ttk.Combobox] = []
        self.transient(master)
        self.geometry("980x720")
        self.minsize(760, 520)
        self._build()
        self.grab_set()

    # ------------------------------------------------------------- montage

    def _build(self) -> None:
        head = tk.Frame(self, background=theme.CANVAS)
        head.pack(fill="x")
        tk.Label(head, text="Champs, filtres et affichage",
                 background=theme.CANVAS,
                 foreground=theme.INK, font=self.fonts.title).pack(anchor="w",
                                                             padx=22, pady=(18, 2))
        tk.Label(head, text="Ces réglages décident de ce qui vous sera "
                            "proposé dans la fenêtre principale ; ils ne "
                            "retirent aucun salarié. Ils sont enregistrés "
                            "dans population_mapping.json, "
                            "privacy_parameters.json, export_parameters.json "
                            "et theme_parameters.json, et restent "
                            "modifiables au bloc-notes.",
                 background=theme.CANVAS, foreground=theme.MUTED, font=self.fonts.small,
                 wraplength=900, justify="left").pack(anchor="w", padx=22,
                                                      pady=(0, 16))
        tk.Frame(head, height=1, background=theme.LINE).pack(fill="x")

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

        self._build_theme(self)
        self._build_privacy(self)
        self._build_export(self)

        body = tk.Frame(self, background=theme.GROUND)
        body.pack(fill="both", expand=True, padx=22, pady=(16, 0))
        self._build_columns(body)
        self._build_dimensions(body)

    def _build_theme(self, parent: tk.Widget) -> None:
        """Choix du theme, montre plutot que decrit.

        Les couleurs ne se saisissent pas une par une : quatre jeux complets
        sont proposes, tous verifies en contraste. On ne peut donc pas rendre
        l'outil illisible depuis cet ecran, ni donner du vert a « critique ».
        Chaque jeu montre ses teintes : c'est plus court a lire qu'un nom.
        """
        band = tk.Frame(parent, background=theme.GROUND)
        band.pack(side="bottom", fill="x", padx=22, pady=(4, 0))
        tk.Frame(band, height=1, background=theme.LINE).pack(fill="x",
                                                             pady=(0, 12))
        tk.Label(band, text="APPARENCE", background=theme.GROUND,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(anchor="w")
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
        band.pack(side="bottom", fill="x", padx=22, pady=(4, 0))
        tk.Frame(band, height=1, background=theme.LINE).pack(fill="x",
                                                             pady=(0, 12))
        tk.Label(band, text="CONFIDENTIALITÉ", background=theme.GROUND,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(anchor="w")
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
        band.pack(side="bottom", fill="x", padx=22, pady=(4, 0))
        tk.Frame(band, height=1, background=theme.LINE).pack(fill="x",
                                                             pady=(0, 12))
        tk.Label(band, text="EXPORT", background=theme.GROUND,
                 foreground=theme.FAINT,
                 font=self.fonts.label).pack(anchor="w")
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

    def _scrollable(self, parent: tk.Widget) -> tk.Frame:
        canvas = tk.Canvas(parent, background=theme.CANVAS, highlightthickness=0)
        bar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview,
                            style="Flat.Vertical.TScrollbar")
        bar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        attach_scrollbar(canvas, bar, side="right", fill="y",
                         before=canvas)
        inner = tk.Frame(canvas, background=theme.CANVAS)
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(window, width=e.width))
        bind_wheel(canvas, self)
        return inner

    def _build_columns(self, parent: tk.Widget) -> None:
        card = Card(parent, padding=0)
        card.pack(side="left", fill="both", expand=True, padx=(0, 14))
        header = tk.Frame(card.inner, background=theme.CANVAS)
        header.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(header, text="COLONNES DU FICHIER", background=theme.CANVAS,
                 foreground=theme.FAINT, font=self.fonts.label).pack(anchor="w")
        if not self.headers:
            tk.Label(card.inner,
                     text="Chargez un fichier pour associer ses colonnes.",
                     background=theme.CANVAS, foreground=theme.MUTED,
                     font=self.fonts.body).pack(anchor="w", padx=16, pady=8)
            return
        tk.Label(header,
                 text="Une colonne non reconnue reste inutilisable tant "
                      "qu'aucun champ ne lui est associé.",
                 background=theme.CANVAS, foreground=theme.MUTED, font=self.fonts.small,
                 wraplength=380, justify="left").pack(anchor="w", pady=(2, 0))

        area = tk.Frame(card.inner, background=theme.CANVAS)
        area.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        inner = self._scrollable(area)

        from ..core.mapping import resolve_mapping
        resolved = resolve_mapping(self.headers, self.configuration)
        column_to_field = {column: name
                           for name, column in resolved.field_to_column.items()}
        choices = [IGNORED, NEW_FIELD] + candidate_fields(self.configuration)

        for header_name in self.headers:
            if not str(header_name).strip():
                continue
            row = tk.Frame(inner, background=theme.CANVAS)
            row.pack(fill="x", pady=3)
            known = column_to_field.get(header_name)
            tk.Label(row, text=header_name, background=theme.CANVAS,
                     foreground=theme.INK_SOFT if known else theme.WARN,
                     font=self.fonts.body, width=22, anchor="w").pack(side="left")
            var = tk.StringVar(value=known or IGNORED)
            box = ttk.Combobox(row, textvariable=var, values=choices,
                               state="readonly", font=self.fonts.small)
            box.pack(side="left", fill="x", expand=True)
            box.bind("<<ComboboxSelected>>",
                     lambda _e, h=header_name, w=box: self._chose(h, w))
            self.assignments[header_name] = var
            self._boxes.append(box)

    def _build_dimensions(self, parent: tk.Widget) -> None:
        """Colonnes du fichier -> ou chaque champ sera propose.

        Aucun salarie n'est retire ici : ces cases decident du contenu des
        listes, pas de la population analysee. Le filtrage lui-meme se fait
        dans la fenetre principale, sur le fichier charge.
        """
        card = Card(parent, padding=0)
        card.pack(side="left", fill="both", expand=True)
        header = tk.Frame(card.inner, background=theme.CANVAS)
        header.pack(fill="x", padx=16, pady=(14, 8))
        # « Filtres et axes » se lisait comme si l'on filtrait ici meme.
        # Cet ecran ne retire aucun salarie : il dit seulement quels champs
        # apparaissent dans les listes de la fenetre principale.
        tk.Label(header, text="DIMENSIONS D'ANALYSE", background=theme.CANVAS,
                 foreground=theme.FAINT, font=self.fonts.label).pack(anchor="w")
        tk.Label(header,
                 text="Cet écran ne filtre rien et ne retire aucun salarié. "
                      "Un champ coché est proposé partout : dans la liste "
                      "« Filtrer » de la colonne de gauche, dans « Analyser "
                      "par », dans les onglets Segments et Pay Transparency, "
                      "et dans « Colorer par ».",
                 background=theme.CANVAS, foreground=theme.MUTED, font=self.fonts.small,
                 wraplength=380, justify="left").pack(anchor="w", pady=(2, 0))

        legend = tk.Frame(card.inner, background=theme.CANVAS)
        legend.pack(fill="x", padx=16)
        tk.Label(legend, text="CHAMP", background=theme.CANVAS, foreground=theme.FAINT,
                 font=self.fonts.label, width=22, anchor="w").pack(side="left")
        tk.Label(legend, text="PROPOSÉ", background=theme.CANVAS, foreground=theme.FAINT,
                 font=self.fonts.label).pack(side="left")

        area = tk.Frame(card.inner, background=theme.CANVAS)
        area.pack(fill="both", expand=True, padx=16, pady=(6, 10))
        inner = self._scrollable(area)

        from ..core.segmentation import dimensions as declared_dimensions
        current = {entry["field"]: entry
                   for entry in declared_dimensions(self.configuration)}
        self._dimension_area = inner
        allowed = candidate_dimensions(self.configuration)
        listed = [name for name in current if name in allowed] + \
                 [name for name in allowed if name not in current]
        for field_name in listed:
            entry = current.get(field_name)
            self.add_dimension_row(
                field_name,
                (entry or {}).get("label") or default_label(self.configuration,
                                                            field_name),
                entry is not None)

        foot = tk.Frame(card.inner, background=theme.CANVAS)
        foot.pack(fill="x", padx=16, pady=(0, 14))
        tk.Label(foot, text="Ne pas proposer de filtre au-delà de",
                 background=theme.CANVAS, foreground=theme.MUTED,
                 font=self.fonts.small).pack(side="left")
        self.limit_var = tk.StringVar(
            value=str(max_filter_values(self.configuration)))
        tk.Entry(foot, textvariable=self.limit_var, width=5, relief="flat",
                 background=theme.CANVAS, foreground=theme.INK_SOFT, font=self.fonts.small,
                 highlightthickness=1, highlightbackground=theme.LINE,
                 highlightcolor=theme.ACCENT).pack(side="left", padx=6, ipady=2)
        tk.Label(foot, text="valeurs distinctes", background=theme.CANVAS,
                 foreground=theme.MUTED, font=self.fonts.small).pack(side="left")

    def _chose(self, header: str, box: "ttk.Combobox") -> None:
        """Reagit au choix d'un champ pour une colonne.

        Seul "nouveau champ" demande quelque chose : declarer une notion
        absente du modele — direction, manager, convention — sans quoi la
        fenetre ne saurait que redistribuer des champs existants.
        """
        variable = self.assignments[header]
        if variable.get() != NEW_FIELD:
            return
        variable.set(IGNORED)
        taken = set(candidate_fields(self.configuration)) | set(self.rows)
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
        values = list(box.cget("values")) + [name]
        for other in self._boxes:
            other.configure(values=values)
        variable.set(name)
        self.add_dimension_row(name, header, True)

    def add_dimension_row(self, field_name: str, label: str,
                          declared: bool) -> None:
        row = tk.Frame(self._dimension_area, background=theme.CANVAS)
        row.pack(fill="x", pady=2)
        label_var = tk.StringVar(value=label)
        declared_var = tk.BooleanVar(value=declared)
        tk.Entry(row, textvariable=label_var, background=theme.CANVAS,
                 foreground=theme.INK_SOFT, font=self.fonts.body, width=26,
                 relief="flat", highlightthickness=1,
                 highlightbackground=theme.CANVAS,
                 highlightcolor=theme.ACCENT).pack(side="left", ipady=3)
        CheckRow(row, "", declared_var, self.fonts,
                 ground=theme.CANVAS).pack(side="left", padx=(12, 0))
        self.rows[field_name] = {"label": label_var, "declared": declared_var}

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

        assignments = {header: var.get()
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
            assignments, flags, limit)

        required = section.get("required") or []
        # Ce qui compte est qu'une colonne *de ce fichier* porte le champ,
        # et non qu'il subsiste une orthographe dans les parametres : un
        # champ obligatoire garde volontiers d'autres alias, prevus pour
        # d'autres fichiers, et le controle ne s'apercevait alors de rien.
        # Sans fichier charge, il n'y a rien a controler.
        missing = ([name for name in required if name not in used]
                   if self.headers else [])
        if missing:
            raise CompensationError(
                "Les champs obligatoires suivants ne sont plus associés à "
                f"aucune colonne : {', '.join(missing)}.",
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
        write_configuration(directory, "theme_parameters",
                            {"theme": self.theme_var.get()})
        # La section est reecrite entiere : les seuils d'effectif qui la
        # partagent doivent survivre a l'enregistrement du reglage d'ecran.
        privacy = dict(self.configuration.section("privacy_parameters"))
        privacy["show_identities_on_screen"] = bool(self.identities_var.get())
        write_configuration(directory, "privacy_parameters", privacy)
        export = dict(self.configuration.section("export_parameters"))
        export["include_individual_data"] = bool(self.individual_var.get())
        export["include_source_file"] = bool(self.audit_var.get())
        write_configuration(directory, "export_parameters", export)
        if self.on_saved:
            self.on_saved(directory, path)
        self.destroy()
