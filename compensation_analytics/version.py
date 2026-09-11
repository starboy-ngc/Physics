"""Identite du produit et version (MAJOR.MINOR.PATCH).

Le nom sert partout : titre de la fenetre, ecran d'accueil, pied des
documents produits et manifeste de tracabilite. Il est ecrit ici une seule
fois — un document qui nommerait l'outil autrement que le manifeste rendrait
la tracabilite douteuse.
"""

__version__ = "1.0.0"

ENGINE_NAME = "HR Insight"

#: Maison d'edition, affichee sur l'ecran d'accueil.
PUBLISHER = "Pulsar Analytics"


def engine_signature() -> str:
    """Signature portee par toute restitution, pour la tracabilite."""
    return f"{ENGINE_NAME} v{__version__}"
