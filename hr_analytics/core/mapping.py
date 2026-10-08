"""Resolution du mapping colonnes source -> champs normalises.

Le mapping n'est jamais code en dur : il vient de
`config/population_mapping.json`. La resolution est tolerante (casse,
accents, espaces, ponctuation) pour absorber les variations de fichiers RH.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List

from .config import Configuration
from .errors import MappingError

_PUNCT_RE = re.compile(r"[^a-z0-9]+")


def normalise_label(label: str) -> str:
    """Cle de comparaison insensible a la casse, aux accents et a la ponctuation."""
    decomposed = unicodedata.normalize("NFKD", str(label))
    ascii_only = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _PUNCT_RE.sub(" ", ascii_only.lower()).strip()


@dataclass
class MappingResult:
    """Correspondance resolue entre colonnes du fichier et champs normalises."""

    field_to_column: Dict[str, str] = field(default_factory=dict)
    field_to_index: Dict[str, int] = field(default_factory=dict)
    unknown_columns: List[str] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    duplicate_columns: List[str] = field(default_factory=list)

    def has(self, field_name: str) -> bool:
        return field_name in self.field_to_index


def required_fields(config: Configuration) -> List[str]:
    """Les colonnes sans lesquelles l'analyse n'a pas d'objet.

    Il y en a une, et elle n'est pas nommee ici : c'est le champ de
    remuneration que la configuration designe comme champ d'analyse. Un
    outil d'analyse de remuneration sans remuneration n'analyse rien.

    Elle etait ecrite en dur — « base_salary » — a cote d'un reglage qui
    permettait d'analyser un autre champ. Un fichier ne portant que la
    remuneration totale etait refuse au motif qu'il manquait « Salaire de
    base », une colonne dont son auteur n'avait jamais entendu parler. La
    contrainte suit desormais le reglage au lieu de le contredire.

    Tout le reste s'ajoute par declaration : `population_mapping.required`
    reste lu, pour une organisation qui veut imposer sa propre discipline
    — un matricule, un etablissement. L'outil, lui, n'en impose aucune :
    il signale ce qui manque et continue avec ce qu'il a.
    """
    section = config.section("population_mapping")
    declarees = [str(nom) for nom in (section.get("required") or [])]
    analyse = str(config.get("salary_parameters.analysis_field",
                             "base_salary"))
    if analyse and analyse not in declarees:
        declarees.append(analyse)
    return declarees


def resolve_mapping(headers: List[str], config: Configuration) -> MappingResult:
    """Associe chaque en-tete du fichier a un champ normalise."""
    section = config.section("population_mapping")
    fields: Dict[str, List[str]] = section.get("fields", {})
    required: List[str] = required_fields(config)

    # Trois rangs, et le premier arrive garde la colonne. Un seul
    # dictionnaire les melangeait, et c'est l'ordre des champs dans le
    # fichier de parametres qui tranchait : le nom technique d'un champ
    # valait alias, si bien qu'une colonne « Coefficient » retournait au
    # champ « coefficient » quelle que soit la colonne que l'ecran venait
    # de lui attacher. On associait une colonne a un champ, le fichier
    # l'enregistrait fidelement, et la lecture suivante l'ignorait : le
    # parametrage semblait ne pas s'enregistrer.
    #
    # 1. L'alias principal — la colonne que l'ecran a attachee au champ.
    # 2. Les autres orthographes declarees, prevues pour d'autres fichiers.
    # 3. Le nom technique d'un champ sans aucun alias, pour un fichier de
    #    parametres ecrit au bloc-notes. Il ne s'ajoute pas a une liste
    #    d'alias : avec les defauts livres, le nom technique de chaque
    #    champ figure deja parmi ses propres orthographes, et l'y ajouter
    #    ne servait qu'a reprendre une colonne que l'ecran venait de
    #    donner a un autre champ — « Annexe » et « Coefficient »
    #    retournaient ainsi a « annexe » et « coefficient » quoi qu'on
    #    ait regle.
    alias_to_field: Dict[str, str] = {}

    def revendique(label: str, field_name: str) -> None:
        key = normalise_label(label)
        if key and key not in alias_to_field:
            alias_to_field[key] = field_name

    for field_name, aliases in fields.items():
        if aliases:
            revendique(aliases[0], field_name)
    for field_name, aliases in fields.items():
        for alias in aliases[1:]:
            revendique(alias, field_name)
    for field_name, aliases in fields.items():
        if not aliases:
            revendique(field_name, field_name)

    result = MappingResult()
    seen_labels: Dict[str, int] = {}
    for index, header in enumerate(headers):
        key = normalise_label(header)
        if not key:
            continue
        if key in seen_labels:
            result.duplicate_columns.append(header)
            continue
        seen_labels[key] = index
        field_name = alias_to_field.get(key)
        if field_name is None:
            result.unknown_columns.append(header)
            continue
        if field_name in result.field_to_index:
            result.duplicate_columns.append(header)
            continue
        result.field_to_column[field_name] = header
        result.field_to_index[field_name] = index

    result.missing_required = [
        name for name in required if name not in result.field_to_index
    ]
    return result


def ensure_required(result: MappingResult, config: Configuration) -> None:
    """Leve une erreur lisible si une colonne obligatoire manque."""
    if not result.missing_required:
        return
    fields: Dict[str, List[str]] = config.get("population_mapping.fields", {})
    labels = []
    for name in result.missing_required:
        aliases = fields.get(name) or [name]
        # Toutes les ecritures acceptees, et jamais le nom technique du
        # champ : « base_salary » n'apprend rien a qui cherche sa colonne
        # dans un fichier de paie. L'utilisateur voit du premier coup
        # d'oeil s'il lui suffit de renommer la sienne.
        principal = f"« {aliases[0]} »"
        autres = ", ".join(f"« {alias} »" for alias in aliases[1:])
        labels.append(f"{principal} (ou {autres})" if autres else principal)
    listed = " ; ".join(labels)
    raise MappingError(
        "L'analyse a besoin d'une colonne qui n'a pas été reconnue dans "
        f"votre fichier : {listed}.\n\n"
        "L'écran « Colonnes du fichier » s'ouvre : désignez-y la colonne "
        "correspondante, enregistrez, puis rouvrez le fichier. Vous pouvez "
        "aussi simplement renommer la colonne dans votre fichier.",
        technical=f"missing required fields: {result.missing_required}",
    )
