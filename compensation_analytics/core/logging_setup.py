"""Log technique, strictement separe des donnees RH.

Format : timestamp | module | action | statut | duree | erreur technique.
Aucun nom, prenom, matricule, salaire individuel ou adresse n'y est ecrit :
les fonctions n'acceptent que des compteurs et des libelles techniques.
"""

from __future__ import annotations

import logging
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
            "module_name": module,
            "action": action,
            "status": status,
            "duration": f"{duration:.3f}s" if duration is not None else "-",
            "detail": detail or "-",
        },
    )
