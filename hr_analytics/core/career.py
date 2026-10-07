"""La fiche d'un salarie : ou il se situe, et d'ou il vient.

Deux questions, et elles n'ont pas la meme nature.

« Ou se situe-t-il » se repond avec le fichier de population : on compare
sa remuneration a celle de ses pairs — meme poste, meme maille — et l'on
rend un rapport a la mediane. Ce rapport est le seul chiffre qui permette
de comparer deux personnes de deux metiers differents : 0,92 veut dire
« huit pour cent sous ses pairs », quel que soit le metier.

« D'ou vient-il » demande un troisieme fichier, parce que le fichier de
population est un instantane : il ne porte qu'un salaire, celui
d'aujourd'hui. L'historique est en lignes — une par salarie et par
periode — et ses colonnes se declarent : montants d'un cote, appreciations
de l'autre.

Cette distinction-la n'est pas decorative. Un montant se trace, se
soustrait, se compare. Une appreciation de people review est un *avis* :
elle se date et se montre, elle ne se moyenne pas, elle ne se correle a
rien, et l'outil n'en tire aucune conclusion. Mettre « payee huit pour
cent sous ses pairs » a cote de « notee B » invite a lire une causalite
que personne n'a demontree, dans un sens comme dans l'autre. La fiche
juxtapose ; elle ne commente pas.

Enfin, une fiche est nominative. Elle vit a l'ecran, et ce qui en sort
sort par un geste distinct.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field as _field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .errors import ConfigError
from .normalize import Population, full_time_amount, parse_date, parse_number

#: Roles qu'une colonne de l'historique peut tenir. « ignoree » existe
#: pour qu'un fichier riche n'oblige pas a tout classer : une colonne
#: dont on n'a rien a faire se range quelque part plutot que de forcer
#: un choix faux.
ROLES: Tuple[str, ...] = ("montant", "appreciation", "ignoree")

ROLE_LABELS: Dict[str, str] = {
    "montant": "Montant",
    "appreciation": "Appréciation",
    "ignoree": "Ignorée",
}

#: Role retenu quand rien n'est declare. « ignoree » et non « montant » :
#: additionner une colonne qu'on n'a pas regardee fausserait une
#: remuneration, tandis que l'oublier se voit — la courbe manque.
ROLE_PAR_DEFAUT = "ignoree"

#: Champs que l'historique doit porter pour etre exploitable.
REQUIRED_FIELDS: Tuple[str, ...] = ("employee_id", "period")


def _sans_accent(texte: str) -> str:
    import unicodedata

    decompose = unicodedata.normalize("NFD", str(texte))
    return "".join(c for c in decompose
                   if unicodedata.category(c) != "Mn").strip().lower()


def parse_period(value: Any) -> Tuple[Optional[_dt.date], str]:
    """Rend (date de fin de periode, libelle affiche).

    Une periode s'ecrit de trois facons dans un fichier de paie : une
    date complete, un mois, ou une annee seule. Les trois sont acceptees
    parce que les trois se rencontrent.

    Une annee seule devient son dernier jour. Ce n'est pas arbitraire :
    un historique annuel donne l'etat en fin d'exercice, et choisir le
    1er janvier ferait remonter chaque point d'un an.

    Le libelle garde ce que le fichier a ecrit. Afficher « 31/12/2024 »
    la ou le fichier dit « 2024 » ferait croire a une precision qu'il
    n'a pas.
    """
    if value is None or str(value).strip() == "":
        return None, ""
    texte = str(value).strip()
    if isinstance(value, (_dt.date, _dt.datetime)):
        jour = parse_date(value)
        return jour, f"{jour:%m/%Y}" if jour else texte
    # Une annee seule : quatre chiffres, et rien d'autre.
    if texte.isdigit() and len(texte) == 4:
        annee = int(texte)
        if 1900 <= annee <= 2200:
            return _dt.date(annee, 12, 31), texte
    jour = parse_date(texte)
    if jour is not None:
        return jour, texte
    return None, texte


@dataclass(frozen=True)
class Entry:
    """Un salarie, une periode, et ce que le fichier en dit."""

    employee_id: str
    period: Optional[_dt.date]
    label: str
    amounts: Dict[str, float] = _field(default_factory=dict)
    appraisals: Dict[str, str] = _field(default_factory=dict)

    @property
    def total(self) -> Optional[float]:
        """Somme des montants de la ligne, ou None s'il n'y en a aucun.

        Zero et « aucun montant » ne sont pas la meme chose : une periode
        sans aucun montant lisible est un trou dans l'historique, et un
        trou ne se trace pas comme un zero.
        """
        if not self.amounts:
            return None
        return sum(self.amounts.values())


@dataclass
class HistoryReport:
    """Ce que la lecture de l'historique a donne."""

    rows: int = 0
    #: Salaries de la population ayant au moins une periode.
    matched: int = 0
    #: Matricules de l'historique absents de la population.
    orphan_ids: List[str] = _field(default_factory=list)
    #: Lignes sans matricule, ou dont la periode est illisible.
    unreadable: int = 0
    #: Periodes distinctes rencontrees, de la plus ancienne a la plus
    #: recente.
    periods: List[str] = _field(default_factory=list)

    @property
    def orphans(self) -> int:
        return len(self.orphan_ids)


def column_roles(config) -> Dict[str, str]:
    """Roles declares, par libelle de colonne, compares sans accent."""
    brut = config.get("career_parameters.columns", {}) or {}
    if not isinstance(brut, dict):
        raise ConfigError(
            "Les colonnes de l'historique doivent être une liste de "
            "libellés associés à un rôle.",
            technical=f"career columns is {type(brut).__name__}",
        )
    roles: Dict[str, str] = {}
    for libelle, role in brut.items():
        texte = str(role).strip().lower()
        if texte not in ROLES:
            raise ConfigError(
                f"Le rôle \"{role}\" de la colonne « {libelle} » n'est pas "
                f"reconnu. Rôles possibles : {', '.join(ROLES)}.",
                technical=f"unknown career role: {role!r}",
            )
        roles[_sans_accent(libelle)] = texte
    return roles


def role_of(label: str, roles: Dict[str, str]) -> str:
    return roles.get(_sans_accent(label), ROLE_PAR_DEFAUT)


def resolve_history_mapping(headers: Sequence[str], config):
    """Associe les en-tetes de l'historique a ses deux champs obligatoires.

    Tout le reste n'est pas « inconnu » : ce sont les colonnes que
    l'utilisateur va classer. Elles reviennent dans `unknown_columns`,
    et c'est l'ecran qui en fait une liste a renseigner.
    """
    from .mapping import MappingResult, normalise_label

    champs: Dict[str, Sequence[str]] = config.get(
        "career_parameters.fields", {}) or {}
    alias: Dict[str, str] = {}
    for nom, libelles in champs.items():
        alias[normalise_label(nom)] = nom
        for libelle in libelles:
            alias[normalise_label(libelle)] = nom

    resultat = MappingResult()
    for index, entete in enumerate(headers):
        cle = normalise_label(entete)
        if not cle:
            continue
        nom = alias.get(cle)
        if nom is None or nom in resultat.field_to_index:
            resultat.unknown_columns.append(str(entete))
            continue
        resultat.field_to_column[nom] = str(entete)
        resultat.field_to_index[nom] = index
    resultat.missing_required = [
        nom for nom in REQUIRED_FIELDS if nom not in resultat.field_to_index]
    return resultat


def ensure_history_mapping(mapping) -> None:
    """Refuse un historique auquel il manque de quoi situer une ligne."""
    if not mapping.missing_required:
        return
    noms = {"employee_id": "le matricule", "period": "la période"}
    manque = ", ".join(noms[nom] for nom in mapping.missing_required)
    vues = ", ".join(f"« {c} »" for c in mapping.unknown_columns[:8]) or "aucune"
    raise ConfigError(
        f"Cet historique n'est pas exploitable : {manque} ne s'y trouve "
        f"pas. Colonnes lues : {vues}.",
        technical=("history mapping missing: "
                   f"{','.join(mapping.missing_required)}"),
    )


def read_history(table, config) -> Tuple[List[Entry], Any, List[str]]:
    """Lit un historique : les lignes, le mapping, et ses colonnes libres.

    Les colonnes libres sont rendues telles quelles, dans l'ordre du
    fichier : c'est la liste que l'ecran propose a classer. On ne demande
    a personne d'ecrire le nom de ses propres colonnes.
    """
    mapping = resolve_history_mapping(table.headers, config)
    ensure_history_mapping(mapping)
    roles = column_roles(config)
    i_id = mapping.field_to_index["employee_id"]
    i_period = mapping.field_to_index["period"]
    libres = [(index, str(entete))
              for index, entete in enumerate(table.headers)
              if index not in mapping.field_to_index.values()
              and str(entete).strip()]

    entries: List[Entry] = []
    for row in table.rows:
        def cellule(index):
            return row[index] if index < len(row) else None

        matricule = str(cellule(i_id) or "").strip()
        jour, libelle = parse_period(cellule(i_period))
        if not matricule and not libelle:
            continue
        montants: Dict[str, float] = {}
        avis: Dict[str, str] = {}
        for index, entete in libres:
            brut = cellule(index)
            role = role_of(entete, roles)
            if role == "montant":
                nombre = parse_number(brut)
                if nombre is not None:
                    montants[entete] = nombre
            elif role == "appreciation":
                texte = str(brut or "").strip()
                if texte:
                    avis[entete] = texte
        entries.append(Entry(employee_id=matricule, period=jour,
                             label=libelle, amounts=montants,
                             appraisals=avis))
    return entries, mapping, [entete for _i, entete in libres]


def load_history(source_path: str, config, sheet: Optional[str] = None,
                 progress=None):
    """Import, mapping et lecture d'un fichier d'historique.

    Memes gardes que les deux autres fichiers : un troisieme fichier
    n'est pas un troisieme niveau de confiance.
    """
    from ..io.tabular import read_table
    from .logging_setup import log_event
    from .pipeline import _uncompressed_limit

    table = read_table(source_path, sheet,
                       progress.within if progress else None,
                       max_uncompressed=_uncompressed_limit(config),
                       encodings=config.get("population_mapping.encodings")
                       or None)
    entries, mapping, libres = read_history(table, config)
    log_event("career", "read_history",
              detail=f"rows={table.row_count};entries={len(entries)}")
    return entries, mapping, libres, table


def organise(entries: Sequence[Entry], population: Population,
             id_field: str = "employee_id",
             ) -> Tuple[Dict[str, List[Entry]], HistoryReport]:
    """Range l'historique par salarie, du plus ancien au plus recent.

    Une periode illisible n'est pas jetee en silence : elle est comptee.
    Un historique dont un dixieme des dates ne se lit pas rendrait une
    courbe a trous dont personne ne saurait d'ou viennent les trous.
    """
    connus = {str(e.value(id_field) or "").strip() for e in population}
    connus.discard("")
    par_salarie: Dict[str, List[Entry]] = {}
    compte = HistoryReport(rows=len(entries))
    orphelins: Dict[str, None] = {}
    periodes: Dict[str, Optional[_dt.date]] = {}
    for entry in entries:
        if not entry.employee_id or entry.period is None:
            compte.unreadable += 1
            continue
        periodes.setdefault(entry.label, entry.period)
        if entry.employee_id not in connus:
            orphelins.setdefault(entry.employee_id, None)
            continue
        par_salarie.setdefault(entry.employee_id, []).append(entry)
    for lignes in par_salarie.values():
        lignes.sort(key=lambda item: item.period)
    compte.orphan_ids = list(orphelins)
    compte.matched = len(par_salarie)
    compte.periods = [libelle for libelle, _d in
                      sorted(periodes.items(), key=lambda item: item[1])]
    return par_salarie, compte


def evolution(entries: Sequence[Entry]) -> List[Dict[str, Any]]:
    """L'historique d'un salarie, avec l'ecart d'une periode a la suivante.

    L'ecart se dit en montant et en pourcentage. Ni l'un ni l'autre ne
    suffit : trente euros sur mille cinq cents n'est pas trente euros sur
    six mille, et deux pour cent ne disent pas s'il s'agit de trente
    euros ou de trois cents.

    Une periode sans montant ne rompt pas la serie : elle n'a pas
    d'ecart, et la suivante se compare a la derniere periode chiffree.
    """
    sorties: List[Dict[str, Any]] = []
    precedent: Optional[float] = None
    for entry in entries:
        total = entry.total
        ecart = None if (total is None or precedent is None) else total - precedent
        part = (None if (ecart is None or not precedent)
                else 100.0 * ecart / precedent)
        sorties.append({
            "label": entry.label,
            "period": entry.period,
            "amounts": dict(entry.amounts),
            "total": total,
            "change": ecart,
            "change_share": part,
            "appraisals": dict(entry.appraisals),
        })
        if total is not None:
            precedent = total
    return sorties


def standing(employee: Any, population: Population, config,
             dimension: str) -> Optional[Dict[str, Any]]:
    """Ou se situe un salarie parmi ses pairs, sur la maille donnee.

    Le rapport a la mediane — le « compa-ratio » des analystes — est le
    seul chiffre qui compare deux personnes de deux metiers differents :
    0,92 veut dire « huit pour cent sous ses pairs », que le metier paie
    mille cinq cents ou six mille.

    Rien n'est rendu si le groupe est trop petit : comparer quelqu'un a
    trois collegues, c'est publier la remuneration de ces trois-la a
    travers la sienne.
    """
    from . import statistics_engine as stats
    from .config import analysis_field
    from .metrics import PrivacyRules

    champ = analysis_field(config)
    rules = PrivacyRules.from_config(config)
    valeur = str(employee.value(dimension) or "").strip()
    sien = full_time_amount(employee, champ)
    if not valeur or sien is None:
        return None
    pairs = [full_time_amount(autre, champ) for autre in population
             if str(autre.value(dimension) or "").strip() == valeur]
    montants = [m for m in pairs if m is not None]
    if len(montants) < rules.min_publish:
        return {"segment": valeur, "headcount": len(pairs),
                "published": False}
    mediane = stats.median(montants)
    ordonnes = sorted(montants)
    # Rang centesimal : la part des pairs qu'il depasse. Compte en
    # « inferieurs ou egaux » pour qu'un salarie au minimum du groupe ne
    # paraisse pas au-dessous de lui-meme.
    dessous = sum(1 for m in ordonnes if m <= sien)
    return {
        "segment": valeur,
        "headcount": len(pairs),
        "published": True,
        "amount": sien,
        "median": mediane,
        "ratio": (None if not mediane else sien / mediane),
        "gap": (None if not mediane else 100.0 * (sien - mediane) / mediane),
        "q1": stats.percentile(montants, 25),
        "q3": stats.percentile(montants, 75),
        "min": ordonnes[0],
        "max": ordonnes[-1],
        "rank": 100.0 * dessous / len(ordonnes),
        "compared": len(montants),
    }
