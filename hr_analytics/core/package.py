"""Le package de remuneration : ce qui s'ajoute au salaire de base.

Le fichier de population porte un salaire de base. C'est un *etat* : ce
que touche un salarie au moment de l'extraction. Les primes, elles, sont
un *flux* : ce qui a ete verse pendant une periode. Les additionner sans
precaution est l'erreur qui fausse tout le reste — une prime annuelle
versee en mars n'a pas de sens rapportee a un salaire de septembre.

Ce module tient donc trois regles, et elles sont le coeur du sujet.

1. **La periode est declaree, jamais devinee.** Un fichier de primes ne
   dit pas de lui-meme ce qu'il couvre. Si une colonne de date s'y
   trouve, on en propose les bornes ; c'est un humain qui les confirme.

2. **On ne multiplie jamais une prime pour l'annualiser.** C'est le
   salaire qu'on ramene a la periode. Une prime versee une fois l'an et
   vue dans une fenetre de neuf mois deviendrait, multipliee par 12/9,
   une prime et demie — un chiffre que personne n'a jamais verse. Le
   salaire, lui, est recurrent par nature : le ramener a la periode ne
   suppose rien.

3. **Qui n'etait pas la toute la periode n'est pas compte.** Un salarie
   entre en cours de periode n'a pas « rien touche » : il n'etait pas
   la. L'inclure ferait baisser le taux de service sans qu'aucune
   decision de l'entreprise soit en cause. Il est mis de cote, et
   compte.

Une hypothese reste, et elle s'ecrit ici plutot que de se decouvrir plus
tard : le salaire employe est celui de l'extraction, pas celui qui avait
cours quand la prime a ete versee. Pour une *part* du variable, l'ecart
est du second ordre ; pour un montant, il ne se pose pas.
"""

from __future__ import annotations

import datetime as _dt
import unicodedata
from dataclasses import dataclass, field as _field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .errors import ConfigError
from .normalize import Population, full_time_amount, parse_date

#: Natures d'un element de paie. L'ordre est celui de la lecture : du
#: plus certain au plus accessoire, « exclu » en dernier parce qu'il ne
#: compte nulle part.
NATURES: Tuple[str, ...] = ("fixe", "variable", "exceptionnel",
                            "avantage", "exclu")

#: Intitules affiches. Separes des cles : les cles sont ecrites dans la
#: configuration et ne doivent pas bouger avec la langue de l'ecran.
NATURE_LABELS: Dict[str, str] = {
    "fixe": "Fixe récurrent",
    "variable": "Variable",
    "exceptionnel": "Exceptionnel",
    "avantage": "Avantage en nature",
    "exclu": "Exclu du calcul",
}

#: Natures qui entrent dans la remuneration totale. « exclu » n'y est
#: pas : un remboursement de frais n'est pas une remuneration, et
#: l'additionner gonflerait chaque ecart sans que rien ne le dise.
COMPTEES: Tuple[str, ...] = ("fixe", "variable", "exceptionnel", "avantage")

#: Natures qui forment « le variable » au sens de l'analyse. Un
#: exceptionnel en fait partie : il est discretionnaire, c'est meme ce
#: qui le rend interessant a regarder.
VARIABLES: Tuple[str, ...] = ("variable", "exceptionnel")

#: Nature retenue quand aucune regle ne reconnait un intitule. Variable
#: plutot qu'exclu : un element qu'on oublie de classer doit se voir
#: dans les chiffres, pas disparaitre d'eux.
NATURE_PAR_DEFAUT = "variable"

#: Duree moyenne d'un mois, en jours. La moyenne gregorienne —
#: 365,2425 / 12 — et non 30 : sur douze mois, trente jours par mois
#: perdent cinq jours, soit un sixieme de mois de salaire.
JOURS_PAR_MOIS = 365.2425 / 12.0


def _sans_accent(texte: str) -> str:
    """Forme comparable d'un intitule : sans accent, sans casse."""
    decompose = unicodedata.normalize("NFD", str(texte))
    return "".join(c for c in decompose
                   if unicodedata.category(c) != "Mn").strip().lower()


@dataclass(frozen=True)
class Period:
    """La periode couverte par un fichier d'elements variables.

    Bornes incluses : du premier au dernier jour. Une periode d'un seul
    jour couvre un jour, pas zero.
    """

    start: _dt.date
    end: _dt.date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ConfigError(
                "La période se termine avant d'avoir commencé : "
                f"du {self.start:%d/%m/%Y} au {self.end:%d/%m/%Y}.",
                technical=f"period end {self.end} before start {self.start}",
            )

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def months(self) -> float:
        """Nombre de mois couverts, en decimal.

        C'est ce nombre qui ramene le salaire a la periode. Il n'arrondit
        pas : une fenetre de dix mois et demi vaut 10,5, et le salaire
        suit.
        """
        return self.days / JOURS_PAR_MOIS

    @property
    def complete(self) -> bool:
        """Vrai si la periode couvre au moins douze mois.

        En deca, une prime annuelle versee hors de la fenetre n'apparait
        pas, et le taux de service se lit comme une decision alors qu'il
        n'est qu'un effet du decoupage.
        """
        return self.months >= 11.5

    @property
    def label(self) -> str:
        return f"du {self.start:%d/%m/%Y} au {self.end:%d/%m/%Y}"

    def contains(self, day: Optional[_dt.date]) -> bool:
        return day is not None and self.start <= day <= self.end

    @classmethod
    def twelve_months_to(cls, fin: _dt.date) -> "Period":
        """Les douze mois glissants qui s'achevent la veille d'une date.

        C'est la periode a recommander quand on a le choix : elle se
        termine au plus pres de l'extraction du salaire, donc la
        population des deux fichiers est presque la meme. Une annee
        civile comparee a une extraction de septembre laisse neuf mois
        de derive, et autant d'entrants qui paraitront n'avoir rien
        touche.
        """
        # On s'arrete au dernier mois *clos* : une extraction du 8
        # septembre ne porte pas la paie de septembre, et une periode qui
        # finirait le 7 compterait un mois pour un tiers de mois de prime.
        debut = _dt.date(fin.year - 1, fin.month, 1)
        return cls(debut, _dt.date(fin.year, fin.month, 1)
                   - _dt.timedelta(days=1))


@dataclass(frozen=True)
class Line:
    """Une ligne du fichier d'elements : qui, quoi, combien, quand."""

    employee_id: str
    label: str
    amount: float
    day: Optional[_dt.date] = None


@dataclass
class Reconciliation:
    """Ce que le rapprochement des deux fichiers a donne.

    Sans ce compte, un total de primes est un chiffre dont on ignore sur
    qui il porte. C'est lui qui rend le reste croyable, et c'est pour ca
    qu'il parait a l'ecran plutot que de rester dans un journal.
    """

    lines: int = 0
    #: Salaries de la population ayant au moins une ligne retenue.
    matched: int = 0
    #: Salaries de la population sans aucune ligne.
    without_lines: int = 0
    #: Matricules du fichier d'elements absents de la population.
    orphan_ids: List[str] = _field(default_factory=list)
    #: Lignes ecartees parce que leur date sort de la periode.
    out_of_period: int = 0
    #: Lignes ecartees faute de matricule ou de montant lisible.
    unreadable: int = 0
    #: Salaries mis de cote parce qu'entres apres le debut de la periode.
    late_entrants: int = 0
    #: Salaries dont la date d'entree est illisible ou absente.
    unknown_entry: int = 0
    #: Effectif sur lequel portent les chiffres.
    population: int = 0

    @property
    def orphans(self) -> int:
        return len(self.orphan_ids)


def nature_rules(config) -> Dict[str, str]:
    """Regles « intitule -> nature », telles que la configuration les porte.

    Les cles sont comparees sans accent ni casse : « Prime qualité » et
    « PRIME QUALITE » sont le meme element, et un fichier de paie n'est
    pas regulier sur ce point.
    """
    brut = config.get("package_parameters.natures", {}) or {}
    if not isinstance(brut, dict):
        raise ConfigError(
            "Les natures des éléments de paie doivent être une liste "
            "d'intitulés associés à une nature.",
            technical=f"package natures is {type(brut).__name__}",
        )
    regles: Dict[str, str] = {}
    for intitule, nature in brut.items():
        texte = str(nature).strip().lower()
        if texte not in NATURES:
            raise ConfigError(
                f"La nature \"{nature}\" de l'élément « {intitule} » n'est "
                f"pas reconnue. Natures possibles : {', '.join(NATURES)}.",
                technical=f"unknown nature: {nature!r}",
            )
        regles[_sans_accent(intitule)] = texte
    return regles


def classify(label: str, rules: Dict[str, str]) -> str:
    """Nature d'un intitule, ou la nature par defaut."""
    return rules.get(_sans_accent(label), NATURE_PAR_DEFAUT)


def labels_of(lines: Iterable[Line]) -> List[str]:
    """Intitules distincts rencontres, dans l'ordre d'apparition.

    C'est la liste que l'ecran de parametrage propose a classer : on ne
    demande pas a l'utilisateur d'inventer les intitules de son fichier,
    on les lui montre.
    """
    vus: Dict[str, str] = {}
    for ligne in lines:
        cle = _sans_accent(ligne.label)
        if cle and cle not in vus:
            vus[cle] = ligne.label.strip()
    return list(vus.values())


def _identity(employee: Any, field_name: str) -> str:
    return str(employee.value(field_name) or "").strip()


def aggregate(lines: Sequence[Line],
              population: Population,
              rules: Dict[str, str],
              period: Period,
              id_field: str = "employee_id",
              hire_field: str = "hire_date",
              ) -> Tuple[Dict[str, Dict[str, float]], Reconciliation]:
    """Somme les elements par salarie et par nature, et rend le compte.

    Plusieurs lignes par salarie et par intitule sont la regle, pas
    l'exception : une prime trimestrielle en donne quatre. Elles
    s'additionnent.

    Ne sont retenus que les salaries presents sur toute la periode. Les
    autres ne sont pas absents du resultat par negligence : ils en sont
    retires parce que les compter donnerait un taux de service faux, et
    le rapprochement dit combien ils sont.
    """
    connus: Dict[str, Any] = {}
    tardifs: set = set()
    sans_date = 0
    for employee in population:
        matricule = _identity(employee, id_field)
        if not matricule:
            continue
        entree = parse_date(employee.value(hire_field))
        if entree is None:
            sans_date += 1
        elif entree > period.start:
            tardifs.add(matricule)
            continue
        connus[matricule] = employee

    totaux: Dict[str, Dict[str, float]] = {}
    compte = Reconciliation(lines=len(lines),
                            late_entrants=len(tardifs),
                            unknown_entry=sans_date,
                            population=len(connus))
    orphelins: Dict[str, None] = {}
    for ligne in lines:
        matricule = str(ligne.employee_id or "").strip()
        if not matricule or ligne.amount is None:
            compte.unreadable += 1
            continue
        if ligne.day is not None and not period.contains(ligne.day):
            compte.out_of_period += 1
            continue
        if matricule in tardifs:
            continue
        if matricule not in connus:
            orphelins.setdefault(matricule, None)
            continue
        nature = classify(ligne.label, rules)
        part = totaux.setdefault(matricule, {})
        part[nature] = part.get(nature, 0.0) + float(ligne.amount)

    compte.orphan_ids = list(orphelins)
    compte.matched = len(totaux)
    compte.without_lines = len(connus) - len(totaux)
    return totaux, compte


def _base_over_period(employee: Any, salary_field: str,
                      period: Period) -> Optional[float]:
    """Le salaire de base ramene a la periode, a temps plein.

    C'est ici que la deuxieme regle du module s'applique : on descend le
    salaire vers la periode plutot que de monter la prime vers l'annee.
    """
    mensuel = full_time_amount(employee, salary_field)
    if mensuel is None:
        return None
    return mensuel * period.months


def employee_package(employee: Any,
                     totals: Dict[str, float],
                     salary_field: str,
                     period: Period) -> Dict[str, Any]:
    """Le package d'un salarie sur la periode.

    Rend les montants par nature, le total, et la part du variable. Une
    part n'est calculee que si le salaire de base est connu : sans
    denominateur, un pourcentage serait une invention.
    """
    base = _base_over_period(employee, salary_field, period)
    par_nature = {nature: float(totals.get(nature, 0.0))
                  for nature in COMPTEES}
    variable = sum(par_nature[nature] for nature in VARIABLES)
    ajouts = sum(par_nature.values())
    total = None if base is None else base + ajouts
    return {
        "base": base,
        "by_nature": par_nature,
        "variable": variable,
        "added": ajouts,
        "total": total,
        "variable_share": (None if not total else 100.0 * variable / total),
        "served": variable > 0,
    }
