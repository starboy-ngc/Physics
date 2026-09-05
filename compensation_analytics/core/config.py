"""Chargement et fusion des parametres.

Les parametres vivent dans des fichiers JSON locaux (`config/`), jamais dans
le code. JSON est retenu plutot que YAML/SQLite : lisible par un RH, editable
sans outil, parse par la bibliotheque standard (aucune dependance a installer,
aucun binaire a faire valider par l'IT).

Toute valeur absente d'un fichier utilisateur retombe sur le defaut embarque :
le logiciel demarre donc meme sans dossier `config/`.
"""

from __future__ import annotations

import copy
import json
import os
from typing import Any, Dict, List

from .errors import ConfigError

CONFIG_FILES = (
    "population_mapping",
    "age_parameters",
    "tenure_parameters",
    "percentile_parameters",
    "salary_parameters",
    "privacy_parameters",
    "chart_parameters",
    "export_parameters",
)

DEFAULTS: Dict[str, Any] = {
    "population_mapping": {
        # champ normalise -> libelles acceptes dans le fichier source
        "fields": {
            "employee_id": ["Matricule", "Employee ID", "ID"],
            "last_name": ["Nom", "Last name"],
            "first_name": ["Prénom", "First name"],
            "gender": ["Sexe", "Genre", "Gender"],
            "birth_date": ["Date de naissance", "Birth date"],
            "hire_date": ["Date d'entrée", "Hire date"],
            "leave_date": ["Date de sortie", "Leave date"],
            "business_unit": ["BU", "Business Unit"],
            "country": ["Pays", "Country"],
            "site": ["Établissement", "Site"],
            "job": ["Métier", "Job"],
            "job_family": ["Famille métier", "Job family"],
            "grade": ["Grade"],
            "coefficient": ["Coefficient"],
            "status": ["Statut", "Status"],
            "fte": ["Temps de travail", "FTE"],
            "base_salary": ["Salaire de base", "Base salary"],
            "variable_pay": ["Variable", "Variable pay"],
            "total_compensation": ["Rémunération totale"],
        },
        # Dimensions d'analyse : segmentation, filtres, coloration des
        # graphiques. Ajouter une notion metier (equipe, manager, direction)
        # se fait ici et dans "fields", sans modification du code.
        #
        # Chaque entree accepte deux drapeaux optionnels, vrais par defaut :
        #   "filter"  : proposee comme critere de selection
        #   "segment" : proposee comme axe d'analyse
        # Les omettre revient a activer les deux, comme avant leur existence.
        "dimensions": [
            {"field": "business_unit", "label": "BU"},
            {"field": "country", "label": "Pays"},
            {"field": "site", "label": "Établissement"},
            {"field": "job", "label": "Métier"},
            {"field": "job_family", "label": "Famille métier"},
            {"field": "grade", "label": "Grade"},
            {"field": "status", "label": "Statut"},
            {"field": "gender", "label": "Sexe"},
            {"field": "age_band", "label": "Tranche d'âge"},
            {"field": "tenure_band", "label": "Tranche d'ancienneté"},
        ],
        "required": ["employee_id", "base_salary"],
        "numeric": ["coefficient", "fte", "base_salary", "variable_pay", "total_compensation"],
        "date": ["birth_date", "hire_date", "leave_date"],
        "personal": ["last_name", "first_name", "birth_date", "employee_id"],
        # Au-dela de ce nombre de valeurs distinctes, une liste deroulante
        # n'est plus utilisable : la dimension reste analysable, mais n'est
        # pas proposee comme filtre dans l'interface.
        "max_filter_values": 60,
    },
    "age_parameters": {
        "bands": [
            {"label": "20-29", "min": 20, "max": 29, "max_inclusive": True},
            {"label": "30-39", "min": 30, "max": 39, "max_inclusive": True},
            {"label": "40-49", "min": 40, "max": 49, "max_inclusive": True},
            {"label": "50-59", "min": 50, "max": 59, "max_inclusive": True},
            {"label": "60+", "min": 60, "max": None},
        ],
        "reference_date": None,
    },
    "tenure_parameters": {
        "bands": [
            {"label": "<2 ans", "min": 0, "max": 2},
            {"label": "2-5 ans", "min": 2, "max": 5},
            {"label": "5-10 ans", "min": 5, "max": 10},
            {"label": ">10 ans", "min": 10, "max": None},
        ],
        "reference_date": None,
    },
    "percentile_parameters": {
        "percentiles": [10, 25, 50, 75, 90],
        "method": "linear",
    },
    "salary_parameters": {
        "analysis_field": "base_salary",
        "annualise_on_fte": False,
        "currency": "EUR",
        "outlier_method": "iqr",
        "outlier_factor": 1.5,
        "min_plausible": 1000.0,
        "max_plausible": 1000000.0,
    },
    "privacy_parameters": {
        "min_headcount_publish": 5,
        "min_headcount_warning": 10,
        "min_headcount_chart": 10,
        "anonymise_identifiers": True,
        "log_personal_data": False,
    },
    "chart_parameters": {
        "histogram_bins": 20,
        "scatter_x": "tenure_years",
        "scatter_y": "base_salary",
        "scatter_color_by": "business_unit",
        "scatter_max_points": 5000,
        "show_trend_line": True,
    },
    "export_parameters": {
        "output_directory": "output",
        "excel_enabled": True,
        "html_report_enabled": True,
        # Restitutions paysage : synthese d'une page et jeu de slides.
        "slides_html_enabled": True,
        "slides_pdf_enabled": True,
        "summary_enabled": True,
        "include_individual_data": False,
    },
}


class Configuration:
    """Vue en lecture sur l'ensemble des parametres charges."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def section(self, name: str) -> Dict[str, Any]:
        if name not in self._data:
            raise ConfigError(
                f"La section de configuration \"{name}\" est introuvable.",
                technical=f"unknown config section: {name}",
            )
        return self._data[name]

    def get(self, path: str, default: Any = None) -> Any:
        """Acces pointe : `config.get("salary_parameters.currency")`."""
        node: Any = self._data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def as_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)


def analysis_field(config: "Configuration") -> str:
    """Champ de remuneration analyse, valide contre le mapping.

    Sans ce controle, pointer `analysis_field` sur une colonne texte faisait
    echouer le controle qualite sur une comparaison str/int — une trace
    technique illisible pour un utilisateur RH.
    """
    field_name = config.get("salary_parameters.analysis_field", "base_salary")
    numeric = config.get("population_mapping.numeric", []) or []
    if field_name not in numeric:
        raise ConfigError(
            f"Le champ d'analyse \"{field_name}\" n'est pas un champ "
            "numérique. Corrigez \"analysis_field\" dans "
            "salary_parameters.json. Champs numériques disponibles : "
            f"{', '.join(numeric)}.",
            technical=f"analysis_field not numeric: {field_name}",
        )
    return field_name


def percentiles(config: "Configuration") -> List[float]:
    """Percentiles a publier, valides."""
    configured = config.get("percentile_parameters.percentiles", []) or []
    result: List[float] = []
    for entry in configured:
        try:
            rank = float(entry)
        except (TypeError, ValueError):
            raise ConfigError(
                f"La valeur de percentile \"{entry}\" n'est pas un nombre. "
                "Corrigez percentile_parameters.json.",
                technical=f"non numeric percentile: {entry!r}",
            ) from None
        if not 0 <= rank <= 100:
            raise ConfigError(
                f"Le percentile {entry} est hors de la plage 0-100. "
                "Corrigez percentile_parameters.json.",
                technical=f"percentile out of range: {rank}",
            )
        result.append(rank)
    return result or [10.0, 25.0, 50.0, 75.0, 90.0]


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_configuration(config_dir: str | None = None) -> Configuration:
    """Charge `config/*.json` en surcharge des defauts embarques."""
    data = copy.deepcopy(DEFAULTS)
    if not config_dir:
        return Configuration(data)
    for name in CONFIG_FILES:
        path = os.path.join(config_dir, f"{name}.json")
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (OSError, ValueError) as exc:
            raise ConfigError(
                f"Le fichier de configuration \"{name}.json\" n'a pas pu être lu. "
                "Vérifiez qu'il s'agit d'un fichier JSON valide.",
                technical=f"{type(exc).__name__}: {exc}",
            ) from exc
        if not isinstance(loaded, dict):
            raise ConfigError(
                f"Le fichier de configuration \"{name}.json\" doit contenir un objet.",
                technical=f"config {name} is {type(loaded).__name__}",
            )
        data[name] = _deep_merge(data.get(name, {}), loaded)
    return Configuration(data)


def write_configuration(config_dir: str, section: str, data: Dict[str, Any]) -> str:
    """Ecrit une section de configuration, et rend le chemin du fichier.

    L'ecriture passe par un fichier temporaire du meme dossier, renomme
    ensuite : une interruption en cours d'ecriture laisserait sinon une
    configuration tronquee, que le chargement suivant refuserait.
    """
    if section not in CONFIG_FILES:
        raise ConfigError(
            f"La section de configuration \"{section}\" n'existe pas.",
            technical=f"unknown config section: {section}",
        )
    try:
        os.makedirs(config_dir, exist_ok=True)
        path = os.path.join(config_dir, f"{section}.json")
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except OSError as exc:
        raise ConfigError(
            f"Les paramètres n'ont pas pu être enregistrés dans "
            f"\"{config_dir}\". Vérifiez que le dossier est accessible en "
            "écriture, ou choisissez-en un autre.",
            technical=f"{type(exc).__name__}: {exc}",
        ) from exc
    return path


def write_default_configuration(config_dir: str) -> None:
    """Materialise les defauts sur disque, pour edition par l'utilisateur."""
    os.makedirs(config_dir, exist_ok=True)
    for name in CONFIG_FILES:
        path = os.path.join(config_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(DEFAULTS[name], handle, ensure_ascii=False, indent=2)
            handle.write("\n")
