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
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from ..version import ENGINE_NAME, __version__
from ..core import metrics
from ..core.config import (Configuration, default_config_dir,
                           load_configuration)
from ..core.errors import CompensationError
from ..core.export import export_excel
from ..core.pipeline import AnalysisRequest, load_population, run_analysis
from ..core.quality import run_quality_check
from ..core.reporting import (format_money, format_number, format_percent,
                              format_years,
                              write_report)
from ..core.segmentation import (build_filters, dimension_label,
                                 filter_fields, max_filter_values,
                                 segment_fields)
from ..core.slides import (build_deck, build_summary, write_slides_html,
                           write_slides_pdf)
from ..core.traceability import write_manifest
from . import theme
from .charts import HistogramChart, ScatterChart
from .theme import (ACCENT, CANVAS, CRIT, FAINT, GROUND, INK, INK_SOFT, LINE,
                    MUTED, OK, STRIPE, WARN, WARN_SOFT, Card, CheckRow, Fonts,
                    TabBar)

WINDOW_TITLE = f"{ENGINE_NAME} {__version__}"
#: Les parentheses distinguent l'absence de filtre d'une valeur qui,
#: elle, existerait vraiment dans le fichier.
_ALL = "(toutes)"

#: Les resultats d'abord, le controle qualite en dernier : on y revient
#: quand un chiffre surprend, on ne commence pas par lui.
TABS = (("population", "Population"), ("remuneration", "Rémunération"),
        ("distribution", "Distribution"),
        ("nuage", "Ancienneté × rémunération"), ("segments", "Segments"),
        ("qualite", "Qualité"))


class Application(tk.Tk):
    """Fenetre unique de l'outil."""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("1380x880")
        self.minsize(1120, 720)
        self.configure(background=GROUND)

        self.fonts = Fonts(self)
        theme.apply(self, self.fonts)

        self.config_dir = config_dir or default_config_dir()
        self.configuration = load_configuration(self.config_dir)
        self.source_path: Optional[str] = None
        self.population = None
        self.mapping = None
        self.headers: List[str] = []
        self.result = None
        self.filter_vars: Dict[str, tk.StringVar] = {}
        self.segment_vars: Dict[str, tk.BooleanVar] = {}
        self.output_vars: Dict[str, tk.BooleanVar] = {}
        self._segments: List[Dict[str, Any]] = []
        self._colour_fields: List[str] = []
        self._queue: queue.Queue = queue.Queue()

        self._build_layout()
        self._set_state("Choisissez un fichier de population pour commencer.")

    # -------------------------------------------------------------- layout

    def _build_layout(self) -> None:
        header = tk.Frame(self, background=CANVAS)
        header.pack(fill="x")
        inner = tk.Frame(header, background=CANVAS)
        inner.pack(fill="x", padx=26, pady=(20, 16))
        tk.Label(inner, text="Analyse de rémunération", background=CANVAS,
                 foreground=INK, font=self.fonts.title).pack(side="left")
        self.source_label = tk.Label(inner, text="Aucun fichier chargé",
                                     background=CANVAS, foreground=FAINT,
                                     font=self.fonts.small)
        self.source_label.pack(side="left", padx=14, pady=(6, 0))
        ttk.Button(inner, text="Paramètres", style="Ghost.TButton",
                   command=self.open_settings).pack(side="right")
        theme.rule(header).pack(fill="x")

        # Le pied de page se reserve sa place avant le corps : empile apres
        # une zone en expansion, il n'obtiendrait aucune hauteur.
        footer = tk.Frame(self, background=GROUND)
        footer.pack(side="bottom", fill="x", padx=26, pady=14)
        theme.rule(self).pack(side="bottom", fill="x")
        self.status = tk.Label(footer, text="", background=GROUND,
                               foreground=MUTED, font=self.fonts.small)
        self.status.pack(side="left")
        tk.Label(footer, text="Traitement local · aucune donnée ne quitte ce poste",
                 background=GROUND, foreground=FAINT,
                 font=self.fonts.small).pack(side="right")

        body = tk.Frame(self, background=GROUND)
        body.pack(fill="both", expand=True)

        self.sidebar_card = Card(body, padding=0)
        self.sidebar_card.pack(side="left", fill="y")
        self.sidebar_card.configure(width=326)
        self.sidebar_card.pack_propagate(False)
        self._build_sidebar(self.sidebar_card.inner)
        theme.rule(body, vertical=True).pack(side="left", fill="y")

        content = Card(body, padding=0)
        content.pack(side="left", fill="both", expand=True, padx=(26, 8))
        self.tabbar = TabBar(content.inner, self.fonts, on_change=self._show_tab)
        self.tabbar.pack(fill="x")
        # Un onglet retire doit s'expliquer la ou l'utilisateur regarde. Le
        # pied de page ne convient pas : la phrase y chevauchait la mention
        # de traitement local.
        self.notice = tk.Label(content.inner, background=WARN_SOFT,
                               foreground=WARN, font=self.fonts.small,
                               justify="left", anchor="w", padx=14, pady=9,
                               wraplength=900)
        self.pages = tk.Frame(content.inner, background=CANVAS)
        self.pages.pack(fill="both", expand=True)
        self._build_pages()



    def _section(self, parent, number: int, text: str) -> None:
        row = tk.Frame(parent, background=GROUND)
        row.pack(fill="x", pady=(18, 8))
        tk.Label(row, text=f"{number}", background=ACCENT, foreground="white",
                 font=self.fonts.label, width=2, pady=1).pack(side="left")
        tk.Label(row, text=text.upper(), background=GROUND, foreground=FAINT,
                 font=self.fonts.label).pack(side="left", padx=8)

    def _build_sidebar(self, parent: tk.Widget) -> None:
        parent.configure(background=GROUND)
        actions = tk.Frame(parent, background=GROUND)
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

        outer = tk.Canvas(parent, background=GROUND, highlightthickness=0)
        bar = ttk.Scrollbar(parent, orient="vertical", command=outer.yview,
                            style="Flat.Vertical.TScrollbar")
        # L'ascenseur se reserve sa place en premier : empile apres une zone
        # en expansion, il n'obtenait aucune largeur et restait invisible.
        bar.pack(side="right", fill="y", padx=(0, 8), pady=4)
        outer.pack(side="left", fill="both", expand=True, padx=(26, 0))
        theme.attach_scrollbar(outer, bar, side="right", fill="y",
                               padx=(0, 8), pady=4, before=outer)
        steps = tk.Frame(outer, background=GROUND)
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
        self.mapping_label = tk.Label(steps, text="", background=GROUND,
                                      foreground=MUTED, font=self.fonts.small,
                                      wraplength=250, justify="left")
        self.mapping_label.pack(anchor="w", pady=(8, 0))

        self._section(steps, 2, "Filtrer")
        self.filters_frame = tk.Frame(steps, background=GROUND)
        self.filters_frame.pack(fill="x")
        tk.Label(self.filters_frame, text="Chargez un fichier pour voir les filtres.",
                 background=GROUND, foreground=FAINT, font=self.fonts.small,
                 wraplength=250, justify="left").pack(anchor="w")

        self._section(steps, 3, "Analyser par")
        self.segments_frame = tk.Frame(steps, background=GROUND)
        self.segments_frame.pack(fill="x")

        self._section(steps, 4, "Restituer")
        self.outputs_frame = tk.Frame(steps, background=GROUND)
        self.outputs_frame.pack(fill="x", pady=(0, 8))
        for key, label, default in (("rapport", "Rapport détaillé (HTML)", True),
                                    ("synthese", "Fiche standard (PDF)", True),
                                    ("slides", "Jeu de slides (PDF)", True),
                                    ("excel", "Classeur Excel", True)):
            var = tk.BooleanVar(value=default)
            self.output_vars[key] = var
            CheckRow(self.outputs_frame, label, var,
                     self.fonts).pack(anchor="w", pady=2)

    def _build_pages(self) -> None:
        self.tabs: Dict[str, tk.Frame] = {}
        for key, label in TABS:
            frame = tk.Frame(self.pages, background=CANVAS)
            self.tabs[key] = frame
            self.tabbar.add(key, label)

        self.quality_summary = tk.Frame(self.tabs["qualite"], background=CANVAS)
        self.quality_summary.pack(fill="x", padx=18, pady=(18, 12))
        # Tant qu'aucun fichier n'est charge, un tableau vide n'apprend rien :
        # la page dit ce qu'elle attend. _kpis vide ce cadre au premier calcul.
        tk.Label(self.quality_summary,
                 text="Aucun fichier chargé.\nChoisissez une population dans la "
                      "colonne de gauche pour lancer le contrôle qualité.",
                 background=CANVAS, foreground=MUTED, font=self.fonts.body,
                 justify="left").pack(anchor="w", pady=(40, 0))
        self.quality_tree = self._tree(self.tabs["qualite"],
                                       ("Sévérité", "Constat", "Lignes"),
                                       (120, 640, 90))
        self.quality_tree.master.pack_forget()

        self.population_frame = tk.Frame(self.tabs["population"], background=CANVAS)
        self.population_frame.pack(fill="both", expand=True, padx=18, pady=18)
        # Premier onglet de la barre, donc premier ecran vu : il doit dire ce
        # qu'il attend. _show_population vide ce cadre au premier calcul.
        tk.Label(self.population_frame,
                 text="Aucune analyse.\nChoisissez une population dans la "
                      "colonne de gauche, puis « Analyser ».",
                 background=CANVAS, foreground=MUTED, font=self.fonts.body,
                 justify="left").pack(anchor="w", pady=(40, 0))
        self.salary_frame = tk.Frame(self.tabs["remuneration"], background=CANVAS)
        self.salary_frame.pack(fill="both", expand=True, padx=18, pady=18)

        self.histogram = HistogramChart(self.tabs["distribution"])
        self.histogram.pack(fill="both", expand=True, padx=18, pady=18)

        nuage = self.tabs["nuage"]
        controls = tk.Frame(nuage, background=CANVAS)
        controls.pack(fill="x", padx=18, pady=(16, 4))
        tk.Label(controls, text="COLORER PAR", background=CANVAS, foreground=FAINT,
                 font=self.fonts.label).pack(side="left")
        self.colour_choice = ttk.Combobox(controls, state="readonly", width=20,
                                          font=self.fonts.small)
        self.colour_choice.pack(side="left", padx=10)
        self.colour_choice.bind("<<ComboboxSelected>>", lambda _e: self._recolour())
        ttk.Button(controls, text="Réinitialiser le cadrage", style="Ghost.TButton",
                   command=lambda: self.scatter.reset_view()).pack(side="left")
        self.selection_label = tk.Label(controls, text="", background=CANVAS,
                                        foreground=INK, font=self.fonts.small)
        self.selection_label.pack(side="right")

        self.scatter = ScatterChart(nuage, on_select=self._on_point_selected)
        self.scatter.pack(fill="both", expand=True, padx=18, pady=(4, 4))
        self.legend_frame = tk.Frame(nuage, background=CANVAS)
        self.legend_frame.pack(fill="x", padx=18, pady=(0, 14))

        head = tk.Frame(self.tabs["segments"], background=CANVAS)
        head.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(head, text="DIMENSION", background=CANVAS, foreground=FAINT,
                 font=self.fonts.label).pack(side="left")
        self.segment_choice = ttk.Combobox(head, state="readonly", width=24,
                                           font=self.fonts.small)
        self.segment_choice.pack(side="left", padx=10)
        self.segment_choice.bind("<<ComboboxSelected>>",
                                 lambda _e: self._show_segment())
        self.segment_tree = self._tree(
            self.tabs["segments"],
            ("Segment", "Effectif", "Moyenne", "Médiane", "Q1", "Q3"),
            (220, 90, 140, 140, 140, 140))

    def _show_tab(self, key: str) -> None:
        for name, frame in getattr(self, "tabs", {}).items():
            frame.pack_forget()
        self.tabs[key].pack(fill="both", expand=True)

    def _tree(self, parent, columns, widths) -> ttk.Treeview:
        wrapper = tk.Frame(parent, background=CANVAS)
        wrapper.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        tree = ttk.Treeview(wrapper, columns=columns, show="headings")
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
        self._populate_segments()
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
            self._populate_segments()
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
        for field in filter_fields(self.configuration):
            values = sorted({str(e.value(field) or "").strip()
                             for e in self.population} - {""})
            # Le seuil est un parametre, plus un nombre cache ici : au-dela,
            # une liste deroulante cesse d'etre utilisable.
            if not values or len(values) > limit:
                continue
            block = tk.Frame(self.filters_frame, background=GROUND)
            block.pack(fill="x", pady=(0, 8))
            tk.Label(block, text=dimension_label(self.configuration, field),
                     background=GROUND, foreground=MUTED,
                     font=self.fonts.small).pack(anchor="w")
            var = tk.StringVar(value=_ALL)
            ttk.Combobox(block, textvariable=var, values=[_ALL] + values,
                         state="readonly", font=self.fonts.small).pack(fill="x",
                                                                       pady=(2, 0))
            self.filter_vars[field] = var

    def _populate_segments(self) -> None:
        for child in self.segments_frame.winfo_children():
            child.destroy()
        self.segment_vars.clear()
        for field in segment_fields(self.configuration):
            if not any(str(e.value(field) or "").strip() for e in self.population):
                continue
            # Coches d'emblee : les axes sur lesquels une comparaison de
            # remuneration se fait le plus souvent.
            var = tk.BooleanVar(value=field in ("job_title", "grade",
                                                "business_unit"))
            self.segment_vars[field] = var
            CheckRow(self.segments_frame,
                     dimension_label(self.configuration, field), var,
                     self.fonts).pack(anchor="w", pady=2)

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
            segments=[f for f, v in self.segment_vars.items() if v.get()],
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
            self._queue.put(("erreur", f"L'analyse a échoué : {error}"))

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
        self._render_results()

    # ------------------------------------------------------------ affichage

    def _render_results(self) -> None:
        payload = self.result.payload
        currency = payload["salary"].get("currency", "EUR")
        self._show_quality(payload["quality"])
        self._show_population(payload["population"])
        self._show_salary(payload["salary"])
        self.histogram.set_distribution(payload["distribution"], currency)
        self._show_scatter(payload["scatter"], currency)
        self._show_segments(payload["segments"])
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
        eligible = {
            "population": not payload["population"].get("masked"),
            "remuneration": not payload["salary"].get("masked"),
            "distribution": bool(payload["distribution"].get("available")),
            "nuage": bool(payload["scatter"].get("available")),
            "segments": publishable,
            "qualite": True,
        }
        for key, allowed in eligible.items():
            self.tabbar.set_visible(key, allowed)

        hidden = [label for key, label in TABS if not eligible[key]]
        headcount = payload["population"].get("headcount", 0)
        self._set_state(f"Analyse terminée · {headcount} salariés"
                        + (f" · {len(hidden)} onglet(s) masqué(s)" if hidden else ""))
        if not hidden:
            self.notice.pack_forget()
            return
        listed = ", ".join(hidden)
        self.notice.configure(
            text=f"{listed} : effectif insuffisant pour publier ces résultats. "
                 f"Les seuils de confidentialité s'appliquent à {headcount} "
                 "salariés ; élargissez le filtre pour les afficher.")
        self.notice.pack(fill="x", after=self.tabbar)

    def _kpis(self, parent, pairs) -> None:
        for child in parent.winfo_children():
            child.destroy()
        band = tk.Frame(parent, background=CANVAS)
        band.pack(fill="x", pady=(0, 16))
        # Une grille a colonnes egales, sur deux rangees au-dela de quatre
        # indicateurs : alignes sur une seule ligne, le dernier sortait du
        # cadre des que la valeur etait longue.
        per_row = len(pairs) if len(pairs) <= 4 else -(-len(pairs) // 2)
        for index, (label, value) in enumerate(pairs):
            row, column = divmod(index, per_row)
            cell = tk.Frame(band, background=CANVAS)
            span = per_row - column if index == len(pairs) - 1 else 1
            cell.grid(row=row, column=column, columnspan=span, sticky="nsew",
                      padx=(0, 24) if column + span < per_row else 0,
                      pady=(0, 20) if row == 0 else 0)
            band.grid_columnconfigure(column, weight=1, uniform="kpi")
            tk.Label(cell, text=label.upper(), background=CANVAS, foreground=FAINT,
                     font=self.fonts.label).pack(anchor="w")
            tk.Label(cell, text=value, background=CANVAS, foreground=INK,
                     font=self.fonts.kpi).pack(anchor="w", pady=(1, 0))

    def _fill(self, tree: ttk.Treeview, rows) -> None:
        tree.tag_configure("pair", background=STRIPE)
        tree.delete(*tree.get_children())
        for index, row in enumerate(rows):
            tree.insert("", "end", values=row,
                        tags=("pair",) if index % 2 else ())

    def _panel(self, parent, title: str, first: bool) -> tk.Frame:
        """Bloc cote a cote : un intertitre et de l'espace, sans cadre."""
        side = tk.Frame(parent, background=CANVAS)
        side.pack(side="left", fill="both", expand=True,
                  padx=(0, 36) if first else 0)
        tk.Label(side, text=title.upper(), background=CANVAS,
                 foreground=FAINT, font=self.fonts.label).pack(anchor="w",
                                                               pady=(0, 6))
        return side

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
        colour = {"CONFORME": OK, "POINTS DE VIGILANCE": WARN}.get(statut, CRIT)
        banner = tk.Frame(self.quality_summary, background=CANVAS)
        banner.pack(fill="x")
        tk.Label(banner, text=f"  {statut}", background=CANVAS, foreground=colour,
                 font=self.fonts.body_bold).pack(anchor="w")
        constats = quality.get("constats", [])
        wrapper = self.quality_tree.master
        if constats and not wrapper.winfo_ismapped():
            wrapper.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        elif not constats and wrapper.winfo_ismapped():
            wrapper.pack_forget()
        self._fill(self.quality_tree,
                   [(item["severite"].capitalize(), item["message"],
                     item["lignes_concernees"])
                    for item in constats])

    def _show_population(self, population: Dict[str, Any]) -> None:
        for child in self.population_frame.winfo_children():
            child.destroy()
        if population.get("masked"):
            tk.Label(self.population_frame, text=population.get("warning", ""),
                     background=CANVAS, foreground=WARN,
                     font=self.fonts.body).pack(anchor="w")
            return
        self._kpis(self.population_frame, [
            ("Effectif", str(population.get("headcount", 0))),
            ("Âge moyen", format_years(population.get("age_mean"))),
            ("Âge médian", format_years(population.get("age_median"))),
            ("Ancienneté moyenne",
             format_years(population.get("tenure_mean"))),
            ("Ancienneté médiane",
             format_years(population.get("tenure_median"))),
        ])
        columns = tk.Frame(self.population_frame, background=CANVAS)
        columns.pack(fill="both", expand=True)
        for index, (title, key) in enumerate((("Tranche d'âge", "age_bands"),
                                              ("Tranche d'ancienneté",
                                               "tenure_bands"))):
            side = self._panel(columns, title, index == 0)
            tree = ttk.Treeview(side, columns=("Tranche", "Effectif", "Part"),
                                show="headings", height=7)
            for name, width in (("Tranche", 170), ("Effectif", 90), ("Part", 90)):
                tree.heading(name, text=name.upper())
                tree.column(name, width=width, anchor="w" if width > 150 else "e")
            tree.pack(fill="both", expand=True)
            self._fill(tree, [(row["label"], row["count"],
                               format_percent(row["share"]))
                              for row in population.get(key, [])])

    def _show_salary(self, salary: Dict[str, Any]) -> None:
        for child in self.salary_frame.winfo_children():
            child.destroy()
        currency = salary.get("currency", "EUR")
        if salary.get("masked"):
            tk.Label(self.salary_frame, text=salary.get("warning", ""),
                     background=CANVAS, foreground=WARN,
                     font=self.fonts.body).pack(anchor="w")
            return
        self._kpis(self.salary_frame, [
            ("Masse salariale", format_money(salary.get("payroll"), currency)),
            ("Salaire moyen", format_money(salary.get("mean"), currency)),
            ("Salaire médian", format_money(salary.get("median"), currency)),
            ("Minimum", format_money(salary.get("min"), currency)),
            ("Maximum", format_money(salary.get("max"), currency)),
        ])
        columns = tk.Frame(self.salary_frame, background=CANVAS)
        columns.pack(fill="both", expand=True)
        spread = salary.get("dispersion") or {}
        variation = spread.get("coefficient_of_variation")
        blocks = (
            ("Percentiles", ("Percentile", "Valeur"),
             [(entry["label"], format_money(salary.get(entry["key"]), currency))
              for entry in salary.get("published_percentiles", [])]),
            ("Dispersion", ("Indicateur", "Valeur"), [
                ("Q3 - Q1", format_money(spread.get("interquartile_range"), currency)),
                ("Q3 / Q1", format_number(spread.get("q3_over_q1"), 2)),
                ("P90 / P10", format_number(spread.get("p90_over_p10"), 2)),
                ("Moyenne / Médiane",
                 format_number(spread.get("mean_over_median"), 2)),
                ("Coefficient de variation",
                 format_percent(None if variation is None else variation * 100)),
            ]),
        )
        for index, (title, headers, rows) in enumerate(blocks):
            side = self._panel(columns, title, index == 0)
            tree = ttk.Treeview(side, columns=headers, show="headings", height=7)
            for name, width, anchor in ((headers[0], 220, "w"),
                                        (headers[1], 150, "e")):
                tree.heading(name, text=name.upper())
                tree.column(name, width=width, anchor=anchor)
            tree.pack(fill="both", expand=True)
            self._fill(tree, rows)

    def _show_scatter(self, dataset: Dict[str, Any], currency: str) -> None:
        fields = segment_fields(self.configuration)
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
        tk.Label(self.legend_frame, text="MASQUER", background=CANVAS,
                 foreground=FAINT, font=self.fonts.label).pack(side="left",
                                                               padx=(0, 10))
        from .charts import _PALETTE
        for index, group in enumerate(groups):
            colour = _PALETTE[index % len(_PALETTE)]
            chip = tk.Frame(self.legend_frame, background=CANVAS, cursor="hand2")
            chip.pack(side="left", padx=(0, 14))
            dot = tk.Canvas(chip, width=9, height=9, background=CANVAS,
                            highlightthickness=0)
            dot.create_oval(1, 1, 8, 8, fill=colour, outline="")
            dot.pack(side="left", pady=(1, 0))
            text = tk.Label(chip, text=group, background=CANVAS, foreground=INK_SOFT,
                            font=self.fonts.small)
            text.pack(side="left", padx=(5, 0))
            for widget in (chip, dot, text):
                widget.bind("<Button-1>", lambda _e, g=group, t=text, d=dot:
                            self._toggle_group(g, t, d))

    def _toggle_group(self, group: str, text: tk.Label, dot: tk.Canvas) -> None:
        self.scatter.toggle_group(group)
        masked = group in self.scatter.hidden
        text.configure(foreground=FAINT if masked else INK_SOFT)
        dot.configure(state="disabled" if masked else "normal")

    def _on_point_selected(self, point: Optional[Dict[str, Any]]) -> None:
        if not point:
            self.selection_label.configure(text="")
            return
        currency = self.result.payload["salary"].get("currency", "EUR")
        self.selection_label.configure(
            text=f'{point["reference"]} · {point["group"]} · '
                 f'{format_years(point["x"])} · '
                 f'{format_money(point["y"], currency)}')

    def _show_segments(self, segments: List[Dict[str, Any]]) -> None:
        self._segments = segments or []
        labels = [segment["label"] for segment in self._segments]
        self.segment_choice.configure(values=labels)
        if labels:
            self.segment_choice.current(0)
            self._show_segment()
        else:
            self._fill(self.segment_tree, [])

    def _show_segment(self) -> None:
        index = self.segment_choice.current()
        if index < 0 or index >= len(self._segments):
            return
        currency = self.result.payload["salary"].get("currency", "EUR")
        rows = []
        for row in self._segments[index]["rows"]:
            if row["masked"]:
                rows.append((row["segment"], row["headcount"],
                             "masqué", "masqué", "masqué", "masqué"))
                continue
            item = row["salary"]
            rows.append((row["segment"], row["headcount"],
                         format_money(item.get("mean"), currency),
                         format_money(item.get("median"), currency),
                         format_money(item.get("p25"), currency),
                         format_money(item.get("p75"), currency)))
        self._fill(self.segment_tree, rows)

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
