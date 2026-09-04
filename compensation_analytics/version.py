"""Version du moteur d'analyse de remuneration (MAJOR.MINOR.PATCH)."""

__version__ = "1.0.0"

ENGINE_NAME = "Compensation Analytics Engine"


def engine_signature() -> str:
    """Signature portee par toute restitution, pour la tracabilite."""
    return f"{ENGINE_NAME} v{__version__}"
