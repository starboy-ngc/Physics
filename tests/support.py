"""Utilitaires de test. Aucune donnee RH reelle n'est utilisee.

Une regle vaut pour tous les tests d'interface, et elle ne se rattrape pas :
**une seule racine Tk par processus**. Une seconde `tkinter.Tk()`, creee
alors que des fenetres precedentes ont lance des analyses — donc des fils de
calcul —, fait ecrire a Tcl « async handler deleted by the wrong thread » et
**terminer le processus** : pas d'exception, pas de trace, pas de decompte
final. Une suite verte peut ainsi disparaitre sans laisser de resultat.

Un test qui a besoin d'un widget isole le construit donc sur la fenetre de
l'outil (`Application`), et non sur une racine a lui. Les sondes
`_display_answers()` font exception : elles creent une racine et la
detruisent aussitot, avant qu'aucun fil n'existe.
"""

from __future__ import annotations

import datetime as _dt
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_analytics.core.config import Configuration, load_configuration
from hr_analytics.core.mapping import resolve_mapping
from hr_analytics.core.normalize import Population, normalise_table

REFERENCE_DATE = _dt.date(2025, 1, 1)

#: La configuration des essais : celle de l'outil, plus les champs
#: d'organisation qu'un fichier de paie porte d'ordinaire (BU, pays,
#: etablissement, metier, poste, famille, annexe, groupe, coefficient,
#: statut). L'outil n'en livre aucun d'office : c'est a l'utilisateur de
#: declarer les siens. Les essais, eux, en ont besoin de quelques-uns
#: pour filtrer, segmenter et comparer ; ils les declarent ici, comme un
#: utilisateur l'aurait fait.
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "config_essai")

HEADERS = [
    "Matricule", "Nom", "Prénom", "Sexe", "Date de naissance", "Date d'entrée",
    "Date de sortie", "BU", "Pays", "Groupe", "Statut", "Salaire de base",
]


def make_row(
    index: int,
    salary: Optional[float] = 40000,
    business_unit: str = "France",
    groupe: str = "G4",
    status: str = "Cadre",
    gender: str = "F",
    age: float = 40,
    tenure: float = 5,
    employee_id: Optional[str] = None,
    birth_date: Any = None,
    hire_date: Any = None,
    leave_date: Any = "",
) -> List[Any]:
    birth = birth_date if birth_date is not None else (
        REFERENCE_DATE - _dt.timedelta(days=int(age * 365.2425))
    )
    hire = hire_date if hire_date is not None else (
        REFERENCE_DATE - _dt.timedelta(days=int(tenure * 365.2425))
    )
    return [
        employee_id if employee_id is not None else f"E{index:05d}",
        f"NOM{index}", f"PRENOM{index}", gender, birth, hire, leave_date,
        business_unit, "France", groupe, status,
        "" if salary is None else salary,
    ]


def build_population(
    rows: List[List[Any]],
    config: Optional[Configuration] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Population:
    config = config or make_config(overrides)
    mapping = resolve_mapping(HEADERS, config)
    return normalise_table(
        HEADERS, rows, mapping, config,
        source_name="test", reference_date=REFERENCE_DATE,
    )


def fresh_config() -> str:
    """Une copie neuve de la configuration des essais, pour une fenetre.

    La fenetre enregistre dans son dossier de configuration (un rangement,
    une categorie de comparaison) : lui donner le dossier partage des
    essais, c'est laisser un essai en modifier un autre.
    """
    import shutil
    import tempfile

    copie = os.path.join(tempfile.mkdtemp(prefix="config-"), "config")
    shutil.copytree(CONFIG_DIR, copie)
    return copie


def write_test_configuration(directory: str) -> None:
    """Pose la configuration des essais dans un dossier, fichier par fichier.

    Les essais qui veulent un dossier a eux pour y changer un seuil
    partaient de la configuration livree. Elle ne declare plus aucune
    notion d'organisation : ils partent donc de celle des essais, qui les
    declare comme un utilisateur l'aurait fait.
    """
    import shutil

    os.makedirs(directory, exist_ok=True)
    for name in os.listdir(CONFIG_DIR):
        if name.endswith(".json"):
            shutil.copy(os.path.join(CONFIG_DIR, name),
                        os.path.join(directory, name))


def make_config(overrides: Optional[Dict[str, Any]] = None) -> Configuration:
    config = load_configuration(CONFIG_DIR)
    data = config.as_dict()
    for path, value in (overrides or {}).items():
        node = data
        parts = path.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return Configuration(data)
