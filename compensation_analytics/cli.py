"""Interface en ligne de commande du moteur.

C'est la couche de pilotage du V1 : elle enchaine le pipeline et produit la
restitution. Une interface graphique pourra s'appuyer sur les memes appels
(`pipeline.run_analysis`), sans dupliquer la moindre regle.

    python3 -m compensation_analytics.cli analyse data/population.xlsx \
        --filtre "business_unit=France" --segment grade --sortie output
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from typing import Any, Dict, List, Optional

from .core.config import load_configuration, write_default_configuration
from .core.errors import CompensationError
from .core.export import export_excel
from .core.logging_setup import configure_logging, log_event
from .core.mapping import resolve_mapping
from .core.pipeline import AnalysisRequest, load_population, run_analysis
from .core.quality import run_quality_check
from .core.reporting import write_report
from .core.slides import (build_deck, build_summary, write_slides_html,
                          write_slides_pdf)
from .core.segmentation import build_filters, dimensions
from .core.traceability import write_manifest
from .io.tabular import read_table
from .version import ENGINE_NAME, __version__

_OPERATOR_TOKENS = (
    (">=", "gte"), ("<=", "lte"), ("!=", "ne"), ("~=", "contains"),
    ("=", "eq"), (">", "gt"), ("<", "lt"),
)


def parse_filter(expression: str) -> Dict[str, Any]:
    """Traduit "business_unit=France|Iberia" en definition de filtre.

    L'expression est decoupee par comparaison de chaines : aucun `eval`,
    aucune construction de code dynamique.
    """
    for token, operator in _OPERATOR_TOKENS:
        if token in expression:
            field_name, _, raw = expression.partition(token)
            field_name = field_name.strip()
            raw = raw.strip()
            if "|" in raw:
                # Une liste garde le sens de l'operateur ecrit : "!=" exclut.
                # Le traduire en "in" ferait dire a l'expression exactement
                # l'inverse, sans le moindre message.
                listed = {"eq": "in", "ne": "not_in"}.get(operator)
                if listed is None:
                    raise CompensationError(
                        f"Le filtre \"{expression}\" combine une liste de "
                        f"valeurs et l'opérateur \"{token}\", qui attend une "
                        "valeur unique. Utilisez \"=\" pour retenir plusieurs "
                        "valeurs, \"!=\" pour les exclure.",
                        technical=f"list value with operator {operator}",
                    )
                return {
                    "field": field_name, "operator": listed,
                    "value": [item.strip() for item in raw.split("|")],
                }
            return {"field": field_name, "operator": operator, "value": raw}
    raise CompensationError(
        f"Le filtre \"{expression}\" est mal écrit. "
        "Format attendu : champ=valeur (ex. business_unit=France).",
        technical=f"unparsable filter: {expression}",
    )


def _date(value: str) -> Optional[_dt.date]:
    return _dt.date.fromisoformat(value) if value else None


def command_analyse(args: argparse.Namespace) -> int:
    # La configuration porte les dimensions declarees : elle est donc
    # necessaire pour valider les filtres avant de lancer l'analyse.
    config = load_configuration(args.config)
    request = AnalysisRequest(
        source_path=args.fichier,
        sheet=args.onglet,
        config_dir=args.config,
        filters=build_filters(
            [parse_filter(item) for item in args.filtre or []], config
        ),
        segments=args.segment or [],
        comparison_filters=build_filters(
            [parse_filter(item) for item in args.comparer or []], config
        ),
        comparison_label=args.libelle_comparaison,
        reference_date=_date(args.date_reference),
        title=args.titre,
        ignore_quality_errors=args.ignorer_anomalies,
    )
    result = run_analysis(request)
    output_dir = args.sortie or result.config.get(
        "export_parameters.output_directory", "output"
    )
    os.makedirs(output_dir, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    produced: List[str] = []
    wanted = set(args.restitution or []) or None

    def requested(name: str, setting: str) -> bool:
        """Une sortie est produite si elle est demandee, ou activee par defaut."""
        if wanted is not None:
            return name in wanted
        return bool(result.config.get(f"export_parameters.{setting}", True))

    if requested("rapport", "html_report_enabled"):
        produced.append(write_report(
            result.payload, os.path.join(output_dir, f"restitution-{stamp}.html")
        ))
    if requested("synthese", "summary_enabled"):
        summary = build_summary(result.payload)
        produced.append(write_slides_html(
            summary, result.payload, os.path.join(output_dir, f"synthese-{stamp}.html")
        ))
        produced.append(write_slides_pdf(
            summary, result.payload, os.path.join(output_dir, f"synthese-{stamp}.pdf")
        ))
    if requested("slides", "slides_html_enabled"):
        deck = build_deck(result.payload)
        produced.append(write_slides_html(
            deck, result.payload, os.path.join(output_dir, f"slides-{stamp}.html")
        ))
        if result.config.get("export_parameters.slides_pdf_enabled", True):
            produced.append(write_slides_pdf(
                deck, result.payload, os.path.join(output_dir, f"slides-{stamp}.pdf")
            ))
    if requested("excel", "excel_enabled"):
        produced.append(export_excel(
            result.payload, result.filtered, result.config,
            os.path.join(output_dir, f"analyse-{stamp}.xlsx"),
        ))
    produced.append(write_manifest(
        result.payload["manifest"], os.path.join(output_dir, f"manifeste-{stamp}.json")
    ))

    print(result.quality.to_text())
    print()
    print(f"Effectif analysé : {len(result.filtered)} salariés")
    for path in produced:
        print(f"  - {path}")
    return 0


def command_controle(args: argparse.Namespace) -> int:
    config = load_configuration(args.config)
    population, mapping, _ = load_population(
        args.fichier, config, args.onglet, _date(args.date_reference)
    )
    report = run_quality_check(population, mapping, config)
    if args.json:
        print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(report.to_text())
    return 1 if report.blocking else 0


def command_mapping(args: argparse.Namespace) -> int:
    config = load_configuration(args.config)
    table = read_table(args.fichier, args.onglet)
    mapping = resolve_mapping(table.headers, config)
    print("Dimensions declarees (F = filtre, A = axe d'analyse) :")
    for entry in dimensions(config):
        name = entry["field"]
        marker = "ok" if name in mapping.field_to_index or name in (
            "age_band", "tenure_band") else "absente du fichier"
        usage = ("F" if entry["filter"] else "-") + \
                ("A" if entry["segment"] else "-")
        print(f"  {name:<20} {usage:<4} {marker}")
    print()
    print("Colonnes identifiées :")
    for field_name, column in sorted(mapping.field_to_column.items()):
        print(f"  {field_name:<20} <- \"{column}\"")
    if mapping.unknown_columns:
        print("\nColonnes non reconnues (ignorées) :")
        for column in mapping.unknown_columns:
            print(f"  \"{column}\"")
    if mapping.missing_required:
        print("\nColonnes obligatoires manquantes :")
        for field_name in mapping.missing_required:
            print(f"  {field_name}")
        return 1
    return 0


def command_config(args: argparse.Namespace) -> int:
    write_default_configuration(args.dossier)
    print(f"Configuration par défaut écrite dans {args.dossier}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compensation-analytics",
        description=f"{ENGINE_NAME} v{__version__} — analyse locale, hors ligne.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--logs", default="", help="dossier du log technique")
    sub = parser.add_subparsers(dest="commande", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("fichier", help="fichier de population (.xlsx, .xlsm, .csv)")
    common.add_argument("--onglet", default=None, help="onglet Excel a lire")
    common.add_argument("--config", default="config", help="dossier de configuration")
    common.add_argument("--date-reference", default="",
                        help="date d'analyse (AAAA-MM-JJ), par defaut aujourd'hui")

    analyse = sub.add_parser("analyse", parents=[common],
                             help="analyse complete et restitution")
    analyse.add_argument("--filtre", action="append",
                         help="critère, ex. business_unit=France ou grade=G5|G6")
    analyse.add_argument("--segment", action="append",
                         help="dimension d'analyse declaree en configuration "
                              "(repetable)")
    analyse.add_argument("--comparer", action="append",
                         help="filtre definissant la population de comparaison")
    analyse.add_argument("--libelle-comparaison", default="Population B")
    analyse.add_argument("--restitution", action="append",
                         choices=["rapport", "synthese", "slides", "excel"],
                         help="sortie a produire (repetable). Par defaut : "
                              "celles activees dans export_parameters.json")
    analyse.add_argument("--sortie", default="", help="dossier de sortie")
    analyse.add_argument("--titre", default="Analyse de rémunération")
    analyse.add_argument("--ignorer-anomalies", action="store_true",
                         help="poursuivre malgré les anomalies critiques")
    analyse.set_defaults(handler=command_analyse)

    controle = sub.add_parser("controle", parents=[common],
                              help="contrôle qualité seul")
    controle.add_argument("--json", action="store_true")
    controle.set_defaults(handler=command_controle)

    mapping = sub.add_parser("mapping", parents=[common],
                             help="vérifier l'identification des colonnes")
    mapping.set_defaults(handler=command_mapping)

    interface = sub.add_parser("interface",
                               help="ouvrir l'interface graphique")
    interface.add_argument("--config", default="config",
                           help="dossier de configuration")
    interface.set_defaults(handler=command_interface)

    config = sub.add_parser("config", help="écrire la configuration par défaut")
    config.add_argument("--dossier", default="config")
    config.set_defaults(handler=command_config)
    return parser


def command_interface(args: argparse.Namespace) -> int:
    """Ouvre l'interface graphique."""
    try:
        from .ui.app import main as ui_main
    except ImportError:
        print("L'interface graphique necessite tkinter, absent de cette "
              "installation de Python.\n"
              "Les commandes en ligne restent disponibles : "
              "compensation-analytics --help", file=sys.stderr)
        return 3
    return ui_main(getattr(args, "config", None) or "config")


def main(argv: Optional[List[str]] = None) -> int:
    # Sans argument, on ouvre l'interface : c'est ce qui se passe quand
    # l'utilisateur double-clique sur le fichier.
    if not (argv if argv is not None else sys.argv[1:]):
        return command_interface(argparse.Namespace())
    args = build_parser().parse_args(argv)
    configure_logging(args.logs or None)
    try:
        return args.handler(args)
    except CompensationError as error:
        # L'utilisateur lit un message metier ; le detail part dans le log.
        log_event("cli", args.commande, status="ERREUR",
                  detail=error.technical or type(error).__name__)
        print(f"\n{error.message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
