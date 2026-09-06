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
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    moment = analysis_date or _dt.datetime.now()
    manifest: Dict[str, Any] = {
        "moteur": ENGINE_NAME,
        "version": __version__,
        "date_analyse": moment.isoformat(timespec="seconds"),
        "fichier_source": os.path.basename(source_path) if source_path else "",
        "empreinte_source": file_fingerprint(source_path) if source_path else "",
        "effectif_analyse": headcount,
        "filtres": filters_description,
        "parametres": config.as_dict(),
    }
    if extra:
        manifest.update(extra)
    return manifest


def write_manifest(manifest: Dict[str, Any], path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, default=str)
        handle.write("\n")
    return path
