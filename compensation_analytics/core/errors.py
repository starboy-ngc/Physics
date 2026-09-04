"""Erreurs applicatives.

Regle : le message porte par l'exception est destine a l'utilisateur RH.
Il ne doit jamais contenir de donnee personnelle (nom, salaire individuel,
matricule). Le detail technique est passe dans `technical` et n'est ecrit
que dans le log technique.
"""


class CompensationError(Exception):
    """Erreur metier presentable a l'utilisateur."""

    def __init__(self, message: str, technical: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.technical = technical


class ImportError_(CompensationError):
    """Echec de lecture d'un fichier de population."""


class MappingError(CompensationError):
    """Colonne obligatoire non identifiee dans le mapping."""


class ConfigError(CompensationError):
    """Configuration invalide."""


class DataQualityError(CompensationError):
    """Anomalie critique bloquant la poursuite de l'analyse."""
