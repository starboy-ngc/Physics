"""Tracabilite : toute analyse doit pouvoir etre reproduite a l'identique.

Le manifeste conserve la version du moteur, la date d'analyse, l'empreinte du
fichier source, les filtres et les parametres. Il ne contient aucune donnee
individuelle.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from typing import Any, Dict, Optional

from ..version import ENGINE_NAME, __version__
from .config import Configuration


def file_fingerprint(path: str) -> str:
    """Empreinte SHA-256 du fichier source (identifie la population sans la copier)."""
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
    except OSError:
        return ""
    return digest.hexdigest()


def build_manifest(
    source_path: str,
    config: Configuration,
    filters_description: str,
    headcount: int,
    analysis_date: Optional[_dt.datetime] = None,
    reference_date: Optional[_dt.date] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    moment = analysis_date or _dt.datetime.now()
    manifest: Dict[str, Any] = {
        "moteur": ENGINE_NAME,
        "version": __version__,
        "date_analyse": moment.isoformat(timespec="seconds"),
        "fichier_source": os.path.basename(source_path) if source_path else "",
        "empreinte_source": file_fingerprint(source_path) if source_path else "",
        # La date de reference decide de tous les ages et de toutes les
        # anciennetes : sans elle au manifeste, une analyse rejouee un an
        # plus tard donne d'autres tranches et personne ne sait pourquoi.
        "date_reference": (reference_date.isoformat() if reference_date
                           else "date d'exécution"),
        "effectif_analyse": headcount,
        "filtres": filters_description,
        "parametres": _publishable(config.as_dict()),
    }
    if extra:
        manifest.update(extra)
    return manifest


#: Reglages qui ne doivent jamais quitter le poste. Le manifeste porte
#: toute la configuration — c'est ce qui permet de refaire une analyse a
#: l'identique — et il accompagne les documents produits : un secret qui y
#: figure est un secret publie.
_SECRET_SETTINGS = (("privacy_parameters", "anonymisation_salt"),)


def _publishable(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Configuration debarrassee de ce qui ne se publie pas.

    Le sel d'anonymisation est ce qui rend une reference irreversible : le
    joindre au manifeste rendrait tous les matricules retrouvables, et la
    reference anonyme redeviendrait un matricule en clair.
    """
    cleaned = {section: dict(values) if isinstance(values, dict) else values
               for section, values in parameters.items()}
    for section, key in _SECRET_SETTINGS:
        if isinstance(cleaned.get(section), dict) and key in cleaned[section]:
            cleaned[section][key] = "(non publié)" if cleaned[section][key] \
                else ""
    return cleaned


def write_manifest(manifest: Dict[str, Any], path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, default=str)
        handle.write("\n")
    return path
