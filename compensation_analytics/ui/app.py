"""Fenetre principale de l'interface graphique.

Elle suit le parcours attendu par un utilisateur RH :

    Importer -> Verifier -> Parametrer -> Analyser -> Explorer -> Restituer

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
from ..core.config import load_configuration
from ..core.errors import CompensationError
from ..core.export import export_excel
from ..core.mapping import resolve_mapping
from ..core.pipeline import AnalysisRequest, load_population, run_analysis
from ..core.quality import run_quality_check
from ..core.reporting import (format_money, format_number, format_percent,
                              write_report)
from ..core.segmentation import (apply_filters, build_filters, dimension_fields,
                                 dimension_label, split_by)
from ..core.slides import (build_deck, build_summary, write_slides_html,
                           write_slides_pdf)
from ..core.traceability import write_manifest
from .charts import ACCENT, INK, LINE, MUTED, PANEL, HistogramChart, ScatterChart

WINDOW_TITLE = f"{ENGINE_NAME} {__version__}"
_ALL = "(toutes)"


class Application(tk.Tk):
    """Fenetre unique de l'outil."""

    def __init__(self) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("1360x860")
        self.minsize(1100, 700)
        self.configure(background="white")

        self.config_dir = "config"
        self.configuration = load_configuration(self.config_dir)
        self.source_path: Optional[str] = None
        self.population = None
        self.mapping = None
        self.result = None
        self.filter_vars: Dict[str, tk.StringVar] = {}
        self.segment_vars: Dict[str, tk.BooleanVar] = {}
        self.output_vars: Dict[str, tk.BooleanVar] = {}
        self._queue: queue.Queue = queue.Queue()

        self._build_style()
        self._build_layout()
        self._set_state("Choisissez un fichier de population pour commencer.")

    # --------------------------------------------------------------- style

    def _build_style(self) -> None:
        style = ttk.Style(self)
        # "clam" est le seul theme dont les couleurs se laissent piloter de la
        # meme facon sur Windows, macOS et Linux.
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", background="white", foreground=INK)
        style.configure("TFrame", background="white")
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background="white", foreground=INK)
        style.configure("Panel.TLabel", background=PANEL, foreground=INK)
        style.configure("Muted.TLabel", background="white", foreground=MUTED)
        style.configure("MutedPanel.TLabel", background=PANEL, foreground=MUTED)
        style.configure("Title.TLabel", background="white", foreground=INK,
                        font=("TkDefaultFont", 15, "bold"))
        style.configure("Step.TLabel", background=PANEL, foreground=MUTED,
                        font=("TkDefaultFont", 8, "bold"))
        style.configure("Kpi.TLabel", background=PANEL, foreground=INK,
                        font=("TkDefaultFont", 15, "bold"))
        style.configure("TButton", padding=(12, 6))
        style.configure("Accent.TButton", padding=(14, 8))
        style.map("Accent.TButton",
                  background=[("!disabled", ACCENT), ("disabled", "#b8c4d0")],
                  foreground=[("!disabled", "white"), ("disabled", "#e8eef4")])
        style.configure("TCheckbutton", background=PANEL, foreground=INK)
        style.configure("Treeview", background="white", fieldbackground="white",
                        rowheight=22)
        style.configure("Treeview.Heading", background=PANEL, foreground=MUTED,
                        font=("TkDefaultFont", 8, "bold"))
        style.configure("TNotebook", background="white", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8))

    # -------------------------------------------------------------- layout

    def _build_layout(self) -> None:
        header = ttk.Frame(self, padding=(18, 14, 18, 10))
        header.pack(fill="x")
        ttk.Label(header, text="Analyse de rémunération",
                  style="Title.TLabel").pack(side="left")
        self.source_label = ttk.Label(header, text="Aucun fichier chargé",
                                      style="Muted.TLabel")
        self.source_label.pack(side="left", padx=16)
        tk.Frame(self, height=2, background=ACCENT).pack(fill="x", padx=18)

        body = ttk.Frame(self, padding=(18, 12, 18, 0))
        body.pack(fill="both", expand=True)
        self.sidebar = ttk.Frame(body, style="Panel.TFrame", padding=14, width=320)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(side="left", fill="both", expand=True, padx=(16, 0))
        self._build_tabs()

        footer = ttk.Frame(self, padding=(18, 8))
        footer.pack(fill="x")
        self.status = ttk.Label(footer, text="", style="Muted.TLabel")
        self.status.pack(side="left")
        ttk.Label(footer, text="Traitement local · aucune donnée ne quitte ce poste",
                  style="Muted.TLabel").pack(side="right")

    def _step(self, parent, number: int, text: str) -> None:
        ttk.Label(parent, text=f"{number}. {text.upper()}",
                  style="Step.TLabel").pack(anchor="w", pady=(14, 6))

    def _build_sidebar(self) -> None:
        # Les boutons d'action sont ancres en bas et ne bougent jamais : sur un
        # ecran peu haut, la liste des filtres poussait "Analyser" hors du
        # cadre, rendant l'outil inutilisable.
        actions = ttk.Frame(self.sidebar, style="Panel.TFrame")
        actions.pack(side="bottom", fill="x", pady=(12, 0))
        self.analyse_button = ttk.Button(actions, text="Analyser",
                                         style="Accent.TButton",
                                         command=self.run_analysis)
        self.analyse_button.pack(fill="x", pady=(0, 6))
        self.analyse_button.state(["disabled"])
        self.export_button = ttk.Button(actions, text="Produire les documents",
                                        command=self.export_documents)
        self.export_button.pack(fill="x")
        self.export_button.state(["disabled"])
        self.progress = ttk.Progressbar(actions, mode="indeterminate")

        # Le reste defile : le nombre de filtres depend du fichier charge.
        outer = tk.Canvas(self.sidebar, background=PANEL, highlightthickness=0,
                          width=290)
        bar = ttk.Scrollbar(self.sidebar, orient="vertical", command=outer.yview)
        outer.configure(yscrollcommand=bar.set)
        outer.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        steps = ttk.Frame(outer, style="Panel.TFrame")
        window = outer.create_window((0, 0), window=steps, anchor="nw", width=286)
        steps.bind("<Configure>",
                   lambda _e: outer.configure(scrollregion=outer.bbox("all")))
        outer.bind("<Configure>",
                   lambda e: outer.itemconfigure(window, width=e.width - 4))
        self.scroll_canvas = outer
        self.sidebar = steps

        self._step(self.sidebar, 1, "Importer")
        ttk.Button(self.sidebar, text="Choisir un fichier…",
                   command=self.choose_file).pack(fill="x")
        self.mapping_label = ttk.Label(self.sidebar, text="", style="MutedPanel.TLabel",
                                       wraplength=280, justify="left")
        self.mapping_label.pack(anchor="w", pady=(6, 0))

        self._step(self.sidebar, 2, "Filtrer")
        self.filters_frame = ttk.Frame(self.sidebar, style="Panel.TFrame")
        self.filters_frame.pack(fill="x")
        ttk.Label(self.filters_frame, text="Chargez un fichier pour voir les filtres.",
                  style="MutedPanel.TLabel", wraplength=280).pack(anchor="w")

        self._step(self.sidebar, 3, "Analyser par")
        self.segments_frame = ttk.Frame(self.sidebar, style="Panel.TFrame")
        self.segments_frame.pack(fill="x")

        self._step(self.sidebar, 4, "Restituer")
        self.outputs_frame = ttk.Frame(self.sidebar, style="Panel.TFrame")
        self.outputs_frame.pack(fill="x")
        for key, label, default in (
            ("rapport", "Rapport détaillé (HTML)", True),
            ("synthese", "Fiche standard (PDF)", True),
            ("slides", "Jeu de slides (PDF)", True),
            ("excel", "Classeur Excel", True),
        ):
            var = tk.BooleanVar(value=default)
            self.output_vars[key] = var
            ttk.Checkbutton(self.outputs_frame, text=label, variable=var,
                            style="TCheckbutton").pack(anchor="w")


    def _build_tabs(self) -> None:
        self.tabs: Dict[str, ttk.Frame] = {}
        for key, label in (("qualite", "Qualité des données"),
                           ("population", "Population"),
                           ("remuneration", "Rémunération"),
                           ("distribution", "Distribution"),
                           ("nuage", "Ancienneté × rémunération"),
                           ("segments", "Segments")):
            frame = ttk.Frame(self.notebook, padding=12)
            self.notebook.add(frame, text=label)
            self.tabs[key] = frame

        self.quality_summary = ttk.Frame(self.tabs["qualite"])
        self.quality_summary.pack(fill="x", pady=(0, 10))
        self.quality_tree = self._tree(self.tabs["qualite"],
                                       ("Sévérité", "Constat", "Lignes"),
                                       (110, 620, 80))

        self.population_frame = ttk.Frame(self.tabs["population"])
        self.population_frame.pack(fill="both", expand=True)
        self.salary_frame = ttk.Frame(self.tabs["remuneration"])
        self.salary_frame.pack(fill="both", expand=True)

        self.histogram = HistogramChart(self.tabs["distribution"])
        self.histogram.pack(fill="both", expand=True)

        nuage = self.tabs["nuage"]
        controls = ttk.Frame(nuage)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Label(controls, text="Colorer par", style="Muted.TLabel").pack(side="left")
        self.colour_choice = ttk.Combobox(controls, state="readonly", width=22)
        self.colour_choice.pack(side="left", padx=8)
        self.colour_choice.bind("<<ComboboxSelected>>", lambda _e: self._recolour())
        ttk.Button(controls, text="Réinitialiser le zoom",
                   command=lambda: self.scatter.reset_view()).pack(side="left")
        self.selection_label = ttk.Label(controls, text="", style="Muted.TLabel")
        self.selection_label.pack(side="right")

        self.scatter = ScatterChart(nuage, on_select=self._on_point_selected)
        self.scatter.pack(fill="both", expand=True)
        self.legend_frame = ttk.Frame(nuage)
        self.legend_frame.pack(fill="x", pady=(8, 0))

        self.segment_choice = ttk.Combobox(self.tabs["segments"], state="readonly",
                                           width=26)
        self.segment_choice.pack(anchor="w", pady=(0, 8))
        self.segment_choice.bind("<<ComboboxSelected>>",
                                 lambda _e: self._show_segment())
        self.segment_tree = self._tree(
            self.tabs["segments"],
            ("Segment", "Effectif", "Moyenne", "Médiane", "Q1", "Q3"),
            (220, 90, 130, 130, 130, 130))

    def _tree(self, parent, columns, widths) -> ttk.Treeview:
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrapper, columns=columns, show="headings")
        for name, width in zip(columns, widths):
            tree.heading(name, text=name)
            tree.column(name, width=width,
                        anchor="w" if width > 200 else "e")
        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    # ----------------------------------------------------------- etat / etapes

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
            population, mapping, _table = load_population(path, self.configuration)
        except CompensationError as error:
            messagebox.showerror("Import impossible", error.message)
            return
        self.source_path = path
        self.population = population
        self.mapping = mapping
        self.source_label.configure(
            text=f"{os.path.basename(path)} · {len(population)} salariés")
        unknown = len(mapping.unknown_columns)
        self.mapping_label.configure(
            text=f"{len(mapping.field_to_index)} colonnes reconnues"
                 + (f", {unknown} ignorée(s)" if unknown else ""))
        self._populate_filters()
        self._populate_segments()
        self.analyse_button.state(["!disabled"])
        self.export_button.state(["disabled"])
        self._show_quality()
        self._set_state("Fichier chargé. Vérifiez la qualité des données, "
                        "puis lancez l'analyse.")

    def _populate_filters(self) -> None:
        for child in self.filters_frame.winfo_children():
            child.destroy()
        self.filter_vars.clear()
        # Les listes sont alimentees par le fichier : l'utilisateur choisit
        # parmi ce qui existe, il n'a aucune syntaxe a taper.
        for field in dimension_fields(self.configuration):
            values = sorted({str(e.value(field) or "").strip()
                             for e in self.population} - {""})
            if not values or len(values) > 60:
                continue
            row = ttk.Frame(self.filters_frame, style="Panel.TFrame")
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=dimension_label(self.configuration, field),
                      style="MutedPanel.TLabel", width=18).pack(side="left")
            var = tk.StringVar(value=_ALL)
            ttk.Combobox(row, textvariable=var, values=[_ALL] + values,
                         state="readonly", width=14).pack(side="left", fill="x",
                                                          expand=True)
            self.filter_vars[field] = var

    def _populate_segments(self) -> None:
        for child in self.segments_frame.winfo_children():
            child.destroy()
        self.segment_vars.clear()
        for field in dimension_fields(self.configuration):
            if not any(str(e.value(field) or "").strip() for e in self.population):
                continue
            var = tk.BooleanVar(value=field in ("grade", "business_unit"))
            self.segment_vars[field] = var
            ttk.Checkbutton(self.segments_frame,
                            text=dimension_label(self.configuration, field),
                            variable=var, style="TCheckbutton").pack(anchor="w")

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
        self._set_state(f"Analyse terminée · {len(self.result.filtered)} salariés "
                        "· explorez les onglets ou produisez les documents.")

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

    def _kpis(self, parent, pairs) -> None:
        for child in parent.winfo_children():
            child.destroy()
        band = ttk.Frame(parent)
        band.pack(fill="x", pady=(0, 12))
        for label, value in pairs:
            cell = ttk.Frame(band, style="Panel.TFrame", padding=10)
            cell.pack(side="left", fill="both", expand=True, padx=(0, 8))
            ttk.Label(cell, text=label.upper(), style="Step.TLabel").pack(anchor="w")
            ttk.Label(cell, text=value, style="Kpi.TLabel").pack(anchor="w")

    def _fill(self, tree: ttk.Treeview, rows) -> None:
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

    def _show_quality(self, quality: Optional[Dict[str, Any]] = None) -> None:
        if quality is None:
            if self.population is None or self.mapping is None:
                return
            report = run_quality_check(self.population, self.mapping,
                                       self.configuration)
            quality = report.as_dict()
        self._kpis(self.quality_summary, [
            ("Lignes importées", str(quality.get("lignes_importees", 0))),
            ("Salariés uniques", str(quality.get("salaries_uniques", 0))),
            ("Doublons", str(quality.get("doublons", 0))),
            ("Salaires manquants", str(quality.get("salaires_manquants", 0))),
            ("Anomalies critiques", str(quality.get("anomalies_critiques", 0))),
            ("Statut", quality.get("statut", "")),
        ])
        self._fill(self.quality_tree,
                   [(item["severite"].capitalize(), item["message"],
                     item["lignes_concernees"])
                    for item in quality.get("constats", [])])

    def _show_population(self, population: Dict[str, Any]) -> None:
        for child in self.population_frame.winfo_children():
            child.destroy()
        if population.get("masked"):
            ttk.Label(self.population_frame, text=population.get("warning", ""),
                      style="Muted.TLabel").pack(anchor="w")
            return
        self._kpis(self.population_frame, [
            ("Effectif", str(population.get("headcount", 0))),
            ("Âge moyen", format_number(population.get("age_mean")) + " ans"),
            ("Âge médian", format_number(population.get("age_median")) + " ans"),
            ("Ancienneté moyenne",
             format_number(population.get("tenure_mean")) + " ans"),
            ("Ancienneté médiane",
             format_number(population.get("tenure_median")) + " ans"),
        ])
        columns = ttk.Frame(self.population_frame)
        columns.pack(fill="both", expand=True)
        for title, key in (("Tranche d'âge", "age_bands"),
                           ("Tranche d'ancienneté", "tenure_bands")):
            side = ttk.Frame(columns)
            side.pack(side="left", fill="both", expand=True, padx=(0, 12))
            ttk.Label(side, text=title.upper(), style="Step.TLabel").pack(anchor="w")
            tree = ttk.Treeview(side, columns=("Tranche", "Effectif", "Part"),
                                show="headings", height=7)
            for name, width in (("Tranche", 160), ("Effectif", 80), ("Part", 80)):
                tree.heading(name, text=name)
                tree.column(name, width=width, anchor="w" if width > 100 else "e")
            tree.pack(fill="both", expand=True)
            self._fill(tree, [(row["label"], row["count"],
                               format_percent(row["share"]))
                              for row in population.get(key, [])])

    def _show_salary(self, salary: Dict[str, Any]) -> None:
        for child in self.salary_frame.winfo_children():
            child.destroy()
        currency = salary.get("currency", "EUR")
        if salary.get("masked"):
            ttk.Label(self.salary_frame, text=salary.get("warning", ""),
                      style="Muted.TLabel").pack(anchor="w")
            return
        self._kpis(self.salary_frame, [
            ("Masse salariale", format_money(salary.get("payroll"), currency)),
            ("Salaire moyen", format_money(salary.get("mean"), currency)),
            ("Salaire médian", format_money(salary.get("median"), currency)),
            ("Minimum", format_money(salary.get("min"), currency)),
            ("Maximum", format_money(salary.get("max"), currency)),
        ])
        columns = ttk.Frame(self.salary_frame)
        columns.pack(fill="both", expand=True)
        left = ttk.Frame(columns)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        ttk.Label(left, text="PERCENTILES", style="Step.TLabel").pack(anchor="w")
        tree = ttk.Treeview(left, columns=("Percentile", "Valeur"),
                            show="headings", height=7)
        for name, width, anchor in (("Percentile", 180, "w"), ("Valeur", 140, "e")):
            tree.heading(name, text=name)
            tree.column(name, width=width, anchor=anchor)
        tree.pack(fill="both", expand=True)
        self._fill(tree, [(entry["label"],
                           format_money(salary.get(entry["key"]), currency))
                          for entry in salary.get("published_percentiles", [])])

        right = ttk.Frame(columns)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, text="DISPERSION", style="Step.TLabel").pack(anchor="w")
        spread = salary.get("dispersion") or {}
        variation = spread.get("coefficient_of_variation")
        tree2 = ttk.Treeview(right, columns=("Indicateur", "Valeur"),
                             show="headings", height=7)
        for name, width, anchor in (("Indicateur", 220, "w"), ("Valeur", 140, "e")):
            tree2.heading(name, text=name)
            tree2.column(name, width=width, anchor=anchor)
        tree2.pack(fill="both", expand=True)
        self._fill(tree2, [
            ("Q3 - Q1", format_money(spread.get("interquartile_range"), currency)),
            ("Q3 / Q1", format_number(spread.get("q3_over_q1"), 2)),
            ("P90 / P10", format_number(spread.get("p90_over_p10"), 2)),
            ("Moyenne / Médiane", format_number(spread.get("mean_over_median"), 2)),
            ("Coefficient de variation",
             format_percent(None if variation is None else variation * 100)),
        ])

    def _show_scatter(self, dataset: Dict[str, Any], currency: str) -> None:
        fields = dimension_fields(self.configuration)
        labels = [dimension_label(self.configuration, f) for f in fields]
        self._colour_fields = fields
        self.colour_choice.configure(values=labels)
        current = dataset.get("color_field")
        if current in fields:
            self.colour_choice.current(fields.index(current))
        elif labels:
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
        from ..core.config import Configuration
        dataset = metrics.scatter_dataset(self.result.filtered, Configuration(data))
        self.scatter.set_dataset(dataset,
                                 self.result.payload["salary"].get("currency", "EUR"))
        self._build_legend()

    def _build_legend(self) -> None:
        for child in self.legend_frame.winfo_children():
            child.destroy()
        groups = self.scatter.dataset.get("groups") or []
        if not groups or len(groups) > 16:
            return
        ttk.Label(self.legend_frame, text="Cliquez une population pour la masquer :",
                  style="Muted.TLabel").pack(side="left", padx=(0, 10))
        from .charts import _PALETTE
        for index, group in enumerate(groups):
            colour = _PALETTE[index % len(_PALETTE)]
            chip = tk.Label(self.legend_frame, text=f"  {group}  ", background="white",
                            foreground=INK, font=("TkDefaultFont", 9),
                            highlightthickness=2, highlightbackground=colour,
                            cursor="hand2", padx=4)
            chip.pack(side="left", padx=3)
            chip.bind("<Button-1>",
                      lambda _e, g=group, c=chip: self._toggle_group(g, c))

    def _toggle_group(self, group: str, chip: tk.Label) -> None:
        self.scatter.toggle_group(group)
        masked = group in self.scatter.hidden
        chip.configure(foreground=MUTED if masked else INK,
                       background=PANEL if masked else "white")

    def _on_point_selected(self, point: Optional[Dict[str, Any]]) -> None:
        if not point:
            self.selection_label.configure(text="")
            return
        currency = self.result.payload["salary"].get("currency", "EUR")
        self.selection_label.configure(
            text=f'{point["reference"]} · {point["group"]} · '
                 f'{format_number(point["x"], 1)} ans · '
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
                    summary, payload, os.path.join(directory, f"synthese-{stamp}.html")))
                produced.append(write_slides_pdf(
                    summary, payload, os.path.join(directory, f"synthese-{stamp}.pdf")))
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
                payload["manifest"], os.path.join(directory, f"manifeste-{stamp}.json")))
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


def main() -> int:
    """Ouvre l'interface. Retourne un code de sortie."""
    Application().mainloop()
    return 0
