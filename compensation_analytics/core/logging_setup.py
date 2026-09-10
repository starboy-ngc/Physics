"""Log technique, strictement separe des donnees RH.

Format : timestamp | module | action | statut | duree | erreur technique.
Aucun nom, prenom, matricule, salaire individuel ou adresse n'y est ecrit :
les fonctions n'acceptent que des compteurs et des libelles techniques.
"""

from __future__ import annotations

import logging
import re
import os
from typing import Optional

LOGGER_NAME = "compensation_analytics"
_FORMAT = "%(asctime)s | %(module_name)s | %(action)s | %(status)s | %(duration)s | %(detail)s"


class _TechnicalFilter(logging.Filter):
    """Garantit la presence des champs du format, meme sur un log tiers."""

    def filter(self, record: logging.LogRecord) -> bool:
        for field in ("module_name", "action", "status", "duration", "detail"):
            if not hasattr(record, field):
                setattr(record, field, "-")
        return True


def configure_logging(
    log_directory: Optional[str] = None, level: int = logging.INFO
) -> logging.Logger:
    """Initialise le log technique (console + fichier local optionnel)."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    # Les gestionnaires precedents sont fermes avant d'etre oublies : les
    # vider sans les fermer laissait le fichier de log ouvert a chaque
    # reconfiguration, et une session d'interface en enchaine plusieurs.
    for handler in list(logger.handlers):
        handler.close()
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(_FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.addFilter(_TechnicalFilter())
    logger.addHandler(console)

    if log_directory:
        os.makedirs(log_directory, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_directory, "technical.log"), encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(_TechnicalFilter())
        logger.addHandler(file_handler)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


#: Tout ce qui pourrait couper une ligne ou en fabriquer une autre.
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


def _one_line(value: str) -> str:
    """Ramene un champ a une seule ligne.

    Un journal se lit une ligne par evenement, et souvent a la machine. Une
    valeur venue du fichier — un libelle de periode, le detail technique
    d'une erreur — pouvait porter un retour a la ligne et fabriquer ainsi
    des evenements qui n'ont jamais eu lieu. Un journal auquel on peut faire
    dire n'importe quoi ne prouve plus rien.
    """
    return _CONTROL_RE.sub(" ", str(value))


def log_event(
    module: str,
    action: str,
    status: str = "OK",
    duration: Optional[float] = None,
    detail: str = "-",
    level: int = logging.INFO,
) -> None:
    """Ecrit un evenement technique. `detail` ne doit contenir aucune donnee RH."""
    get_logger().log(
        level,
        "",
        extra={
            "module_name": _one_line(module),
            "action": _one_line(action),
            "status": _one_line(status),
            "duration": f"{duration:.3f}s" if duration is not None else "-",
            "detail": _one_line(detail or "-"),
        },
    )
