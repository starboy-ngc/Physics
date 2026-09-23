"""HR Insight — moteur local, offline, sans dependance externe.

Le paquet n'importe que la bibliotheque standard Python : aucun appel reseau,
aucun processus enfant, aucune DLL tierce.
"""

from .version import __version__, engine_signature

__all__ = ["__version__", "engine_signature"]
