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
    "exclu": "Exclu",
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
    #: Matricules portes par plusieurs salaries : la jointure y serait
    #: ambigue, ils sont ecartes des deux cotes.
    duplicate_ids: List[str] = _field(default_factory=list)
    #: Effectif sur lequel portent les chiffres.
    population: int = 0

    @property
    def orphans(self) -> int:
        return len(self.orphan_ids)

    @property
    def duplicates(self) -> int:
        return len(self.duplicate_ids)


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


def present_throughout(population: Population,
                       period: Period,
                       id_field: str = "employee_id",
                       hire_field: str = "hire_date",
                       ) -> Tuple[Dict[str, Any], set, int, List[str]]:
    """Les salaries presents sur toute la periode, et ceux qui ne le sont pas.

    Rend quatre choses : les retenus par matricule, les matricules entres
    en cours de periode, le nombre de salaries dont la date d'entree est
    absente ou illisible, et les matricules portes par plusieurs
    salaries.

    Ces derniers rendent la jointure ambigue : a quel salarie rattacher
    une prime portant ce matricule ? Les garder en silence reviendrait a
    choisir le dernier lu, c'est-a-dire a laisser l'ordre des lignes
    decider d'une remuneration. Ils sont ecartes et nommes.

    Ce dernier compte n'est pas un detail. Tant que la colonne de date
    d'entree n'est pas associee, personne ne peut etre ecarte — le
    garde-fou est inerte, et le taux de service se lit comme une
    politique alors qu'il n'est qu'un effet du calendrier. L'ecran doit
    le dire plutot que de rendre un chiffre faux sans prevenir.
    """
    connus: Dict[str, Any] = {}
    tardifs: set = set()
    doublons: Dict[str, None] = {}
    sans_date = 0
    for employee in population:
        matricule = _identity(employee, id_field)
        if not matricule:
            continue
        if matricule in connus or matricule in tardifs:
            doublons.setdefault(matricule, None)
            continue
        entree = parse_date(employee.value(hire_field))
        if entree is None:
            sans_date += 1
        elif entree > period.start:
            tardifs.add(matricule)
            continue
        connus[matricule] = employee
    for matricule in doublons:
        connus.pop(matricule, None)
        tardifs.discard(matricule)
    return connus, tardifs, sans_date, list(doublons)


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
    connus, tardifs, sans_date, doublons = present_throughout(
        population, period, id_field, hire_field)

    totaux: Dict[str, Dict[str, float]] = {}
    compte = Reconciliation(lines=len(lines),
                            late_entrants=len(tardifs),
                            unknown_entry=sans_date,
                            duplicate_ids=doublons,
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


# --------------------------------------------------------------- lecture

#: Champs sans lesquels un fichier d'elements n'est pas exploitable. La
#: date n'en est pas : la plupart des extractions de paie n'en portent
#: pas, et c'est la periode declaree qui fait foi.
REQUIRED_FIELDS: Tuple[str, ...] = ("employee_id", "label", "amount")


def resolve_package_mapping(headers: Sequence[str], config):
    """Associe les en-tetes du fichier d'elements a ses quatre champs.

    Le meme travail que pour la population, sur un vocabulaire bien plus
    court : qui, quoi, combien, et quand si le fichier le dit.
    """
    from .mapping import MappingResult, normalise_label

    champs: Dict[str, Sequence[str]] = config.get(
        "package_parameters.fields", {}) or {}
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
        if nom is None:
            resultat.unknown_columns.append(entete)
            continue
        if nom in resultat.field_to_index:
            resultat.duplicate_columns.append(entete)
            continue
        resultat.field_to_column[nom] = entete
        resultat.field_to_index[nom] = index
    resultat.missing_required = [
        nom for nom in REQUIRED_FIELDS if nom not in resultat.field_to_index]
    return resultat


def ensure_package_mapping(mapping, source: str = "") -> None:
    """Refuse un fichier d'elements auquel il manque l'essentiel.

    Le message nomme ce qui manque et ce que l'outil a vu a la place :
    « colonne obligatoire absente » laisse chercher.
    """
    if not mapping.missing_required:
        return
    noms = {"employee_id": "le matricule",
            "label": "l'intitulé de l'élément",
            "amount": "le montant"}
    manque = ", ".join(noms[nom] for nom in mapping.missing_required)
    vues = ", ".join(f"« {c} »" for c in mapping.unknown_columns[:8]) or "aucune"
    raise ConfigError(
        f"Ce fichier d'éléments variables n'est pas exploitable : "
        f"{manque} ne s'y trouve pas. Colonnes lues : {vues}. "
        "Associez-les dans « Éléments variables… ».",
        technical=("package mapping missing: "
                   f"{','.join(mapping.missing_required)}"),
    )


def read_lines(table, config) -> Tuple[List[Line], Any]:
    """Transforme un tableau brut en lignes d'elements.

    Les lignes illisibles ne sont pas rejetees ici : elles traversent avec
    un montant absent, et c'est le rapprochement qui les compte. Un
    fichier de paie en porte toujours quelques-unes — un total, une ligne
    de separation — et s'arreter a la premiere ferait d'un detail un
    echec.
    """
    from .normalize import parse_number

    mapping = resolve_package_mapping(table.headers, config)
    ensure_package_mapping(mapping, table.source_name)
    i_id = mapping.field_to_index["employee_id"]
    i_label = mapping.field_to_index["label"]
    i_amount = mapping.field_to_index["amount"]
    i_day = mapping.field_to_index.get("day")

    lignes: List[Line] = []
    for row in table.rows:
        def cellule(index):
            return row[index] if index is not None and index < len(row) else None

        matricule = str(cellule(i_id) or "").strip()
        intitule = str(cellule(i_label) or "").strip()
        montant = parse_number(cellule(i_amount))
        if not matricule and not intitule and montant is None:
            # Ligne vide : un classeur en porte souvent en pied.
            continue
        lignes.append(Line(employee_id=matricule, label=intitule,
                           amount=montant,
                           day=parse_date(cellule(i_day))))
    return lignes, mapping


def observed_period(lines: Sequence[Line]) -> Optional[Period]:
    """Les bornes que portent les dates du fichier, s'il en porte.

    Ce n'est qu'une *proposition* : un fichier ne sait pas ce qu'il ne
    contient pas. Si aucune prime n'a ete versee en janvier, ses bornes
    commencent en fevrier, et la periode reelle commence pourtant en
    janvier. C'est a un humain de trancher.
    """
    jours = [ligne.day for ligne in lines if ligne.day is not None]
    if not jours:
        return None
    return Period(min(jours), max(jours))


# ---------------------------------------------------------------- analyse

def _median(valeurs: Sequence[float]) -> Optional[float]:
    from . import statistics_engine as stats
    return stats.median(list(valeurs)) if valeurs else None


def _gap(hommes: Optional[float], femmes: Optional[float]) -> Optional[float]:
    """Ecart femmes/hommes, rapporte au montant masculin.

    Meme convention que partout ailleurs dans l'outil : un nombre negatif
    dit que les femmes touchent moins.
    """
    if hommes is None or femmes is None or not hommes:
        return None
    return 100.0 * (femmes - hommes) / hommes


def packages_of(population: Population,
                totals: Dict[str, Dict[str, float]],
                config,
                period: Period,
                ) -> List[Tuple[Any, Dict[str, Any]]]:
    """Le package de chaque salarie retenu, salarie par salarie.

    Seuls les presents sur toute la periode en ont un : c'est la meme
    regle qu'au rapprochement, et il serait incomprehensible que les deux
    ne portent pas sur les memes gens.
    """
    from .config import analysis_field

    salary_field = analysis_field(config)
    connus, _tardifs, _sans, _doubles = present_throughout(
        population, period)
    return [(employee,
             employee_package(employee, totals.get(matricule, {}),
                              salary_field, period))
            for matricule, employee in connus.items()]


def _sex_of(employee: Any, config) -> str:
    from .pay_equity import classify as classify_sex

    section = config.section("pay_equity_parameters")
    return classify_sex(employee.value(section.get("gender_field", "gender")),
                        tuple(section.get("female_values") or ()),
                        tuple(section.get("male_values") or ()))


def coverage(packages: Sequence[Tuple[Any, Dict[str, Any]]]
             ) -> Dict[str, int]:
    """Sur combien de salaries une *part* peut se calculer.

    Une part suppose un denominateur : le salaire ramene au temps plein.
    Un temps de travail inconnu ne se suppose pas egal a un — ce serait
    compter un temps partiel pour un temps plein —, donc ces salaries
    n'ont pas de part du tout.

    Sans ce compte, un fichier dont la colonne de temps de travail n'est
    pas reconnue donnerait un ecran entierement vide, et rien n'en
    dirait la raison. C'est arrive, et c'est pour ca que la fonction
    existe.
    """
    avec = sum(1 for _e, p in packages if p["base"] is not None)
    return {"with_base": avec, "without_base": len(packages) - avec,
            "total": len(packages)}


def segment_rows(packages: Sequence[Tuple[Any, Dict[str, Any]]],
                 config,
                 dimension: str,
                 ) -> List[Dict[str, Any]]:
    """Une ligne par valeur de la dimension : la table de l'ecran.

    Les montants sont des medianes et non des moyennes : une prime
    exceptionnelle versee a trois personnes deplacerait une moyenne sans
    rien dire de ce que touche le metier.

    Le taux de service se compte sur l'effectif retenu, pas sur
    l'effectif du fichier — c'est la seule facon qu'il mesure une
    politique et non un calendrier.
    """
    from .metrics import PrivacyRules

    rules = PrivacyRules.from_config(config)
    groupes: Dict[str, List[Tuple[Any, Dict[str, Any]]]] = {}
    for employee, package in packages:
        valeur = str(employee.value(dimension) or "").strip()
        if not valeur:
            continue
        groupes.setdefault(valeur, []).append((employee, package))

    lignes = [_segment_row(valeur, membres, rules, config)
              for valeur, membres in groupes.items()]
    # La part du variable d'abord, la plus forte en tete : c'est la
    # question posee a cet ecran. Ce qui ne se publie pas va en bas.
    lignes.sort(key=lambda row: (row["variable_share"] is None,
                                 -(row["variable_share"] or 0.0)))
    return lignes


def _segment_row(valeur, membres, rules, config) -> Dict[str, Any]:
    from .pay_equity import FEMALE, MALE

    bases = [p["base"] for _e, p in membres if p["base"] is not None]
    variables = [p["variable"] for _e, p in membres if p["served"]]
    parts = [p["variable_share"] for _e, p in membres
             if p["variable_share"] is not None]

    servis: Dict[str, List[float]] = {FEMALE: [], MALE: []}
    effectif: Dict[str, int] = {FEMALE: 0, MALE: 0}
    for employee, package in membres:
        sexe = _sex_of(employee, config)
        if sexe not in effectif:
            continue
        effectif[sexe] += 1
        if package["served"]:
            servis[sexe].append(package["variable"])

    publiable = len(variables) >= rules.min_publish
    # L'ecart se masque sur les *servis* de chaque sexe, non sur
    # l'effectif : un metier de quarante femmes dont dix sont servies
    # publierait sinon la prime de dix personnes.
    comparable = (len(servis[FEMALE]) >= rules.min_publish
                  and len(servis[MALE]) >= rules.min_publish)
    return {
        "segment": valeur,
        "headcount": len(membres),
        "base_median": (_median(bases)
                        if len(bases) >= rules.min_publish else None),
        "served": len(variables),
        "served_share": 100.0 * len(variables) / len(membres),
        "variable_median": _median(variables) if publiable else None,
        "variable_share": (_median(parts)
                           if len(parts) >= rules.min_publish else None),
        "variable_gap": (_gap(_median(servis[MALE]), _median(servis[FEMALE]))
                         if comparable else None),
        "published": publiable,
        #: Salaries du segment pour lesquels une part se calcule. Une
        #: part absente partout n'est pas un segment sans variable :
        #: c'est un denominateur manquant, et les deux se distinguent.
        "base_known": len(bases),
        "by_sex": {
            "female": {"headcount": effectif[FEMALE],
                       "served": len(servis[FEMALE])},
            "male": {"headcount": effectif[MALE],
                     "served": len(servis[MALE])},
        },
    }


def composition(membres: Sequence[Tuple[Any, Dict[str, Any]]],
                config) -> List[Dict[str, Any]]:
    """La composition de la remuneration, pour l'ensemble puis par sexe.

    Trois lignes empilables : ce qui vient de la base, des primes fixes,
    du variable, des avantages. Les medianes sont prises nature par
    nature, de sorte qu'une ligne ne depend pas de l'autre — leur somme
    n'est donc pas la mediane du total, et ce n'est pas ce qu'elle
    pretend etre.
    """
    from .metrics import PrivacyRules
    from .pay_equity import FEMALE, MALE

    rules = PrivacyRules.from_config(config)
    groupes = [("Ensemble", None), ("Femmes", FEMALE), ("Hommes", MALE)]
    lignes: List[Dict[str, Any]] = []
    for intitule, sexe in groupes:
        retenus = [(e, p) for e, p in membres
                   if sexe is None or _sex_of(e, config) == sexe]
        if len(retenus) < rules.min_publish:
            lignes.append({"label": intitule, "headcount": len(retenus),
                           "published": False, "parts": {}, "base": None,
                           "total": None})
            continue
        bases = [p["base"] for _e, p in retenus if p["base"] is not None]
        parts = {nature: _median([p["by_nature"].get(nature, 0.0)
                                  for _e, p in retenus])
                 for nature in COMPTEES}
        base = _median(bases)
        lignes.append({
            "label": intitule,
            "headcount": len(retenus),
            "published": True,
            "base": base,
            "parts": parts,
            "total": (None if base is None
                      else base + sum(v or 0.0 for v in parts.values())),
        })
    return lignes


def spread(membres: Sequence[Tuple[Any, Dict[str, Any]]],
           config) -> Optional[Dict[str, Optional[float]]]:
    """La dispersion du variable a l'interieur d'un metier.

    Sur les seuls servis : y compter ceux qui n'ont rien touche ecraserait
    le premier quartile a zero et ferait passer une question de
    distribution — « combien touchent ceux qui touchent » — pour une
    question de couverture, qui se lit ailleurs.
    """
    from . import statistics_engine as stats
    from .metrics import PrivacyRules

    rules = PrivacyRules.from_config(config)
    montants = [p["variable"] for _e, p in membres if p["served"]]
    if len(montants) < rules.min_publish:
        return None
    return {
        "min": stats.minimum(montants),
        "q1": stats.percentile(montants, 25),
        "median": stats.median(montants),
        "q3": stats.percentile(montants, 75),
        "max": stats.maximum(montants),
        "count": len(montants),
    }


def element_rows(lines: Sequence[Line],
                 membres: Sequence[Tuple[Any, Dict[str, Any]]],
                 config,
                 period: Period,
                 rules_by_label: Dict[str, str],
                 ) -> List[Dict[str, Any]]:
    """Les elements verses sur un metier, intitule par intitule.

    C'est la vue qui rend le parametrage visible : on y lit la nature de
    chaque intitule, et la ligne « exclu » montre noir sur blanc ce que
    l'outil ne compte pas. Sans elle, le classement des intitules serait
    un reglage dont personne ne verrait jamais l'effet.
    """
    from .metrics import PrivacyRules
    from .pay_equity import FEMALE, MALE

    seuils = PrivacyRules.from_config(config)
    sexes = {_identity(e, "employee_id"): _sex_of(e, config)
             for e, _p in membres}
    par_intitule: Dict[str, Dict[str, Any]] = {}
    for ligne in lines:
        matricule = str(ligne.employee_id or "").strip()
        if matricule not in sexes or ligne.amount is None:
            continue
        if ligne.day is not None and not period.contains(ligne.day):
            continue
        cle = _sans_accent(ligne.label)
        entree = par_intitule.setdefault(cle, {
            "label": ligne.label.strip(),
            "nature": classify(ligne.label, rules_by_label),
            "amounts": {},
        })
        # Plusieurs versements d'un meme element pour une meme personne
        # s'additionnent avant d'entrer dans la mediane : sinon une prime
        # trimestrielle paraitrait quatre fois plus petite qu'une prime
        # annuelle de meme total.
        entree["amounts"][matricule] = (
            entree["amounts"].get(matricule, 0.0) + float(ligne.amount))

    sorties: List[Dict[str, Any]] = []
    for entree in par_intitule.values():
        montants = entree["amounts"]
        femmes = [m for mat, m in montants.items()
                  if sexes.get(mat) == FEMALE]
        hommes = [m for mat, m in montants.items()
                  if sexes.get(mat) == MALE]
        comparable = (len(femmes) >= seuils.min_publish
                      and len(hommes) >= seuils.min_publish)
        exclu = entree["nature"] == "exclu"
        sorties.append({
            "label": entree["label"],
            "nature": entree["nature"],
            "nature_label": NATURE_LABELS[entree["nature"]],
            "beneficiaries": len(montants),
            # Un element exclu n'a ni mediane ni ecart : le montrer
            # chiffre laisserait croire qu'il compte quelque part.
            "median": (None if exclu or len(montants) < seuils.min_publish
                       else _median(list(montants.values()))),
            "gap": (None if exclu or not comparable
                    else _gap(_median(hommes), _median(femmes))),
            "counted": not exclu,
        })
    # Les elements comptes d'abord, du plus repandu au moins repandu ; les
    # exclus en bas, puisqu'ils ne participent a rien.
    sorties.sort(key=lambda row: (not row["counted"], -row["beneficiaries"]))
    return sorties


def load_elements(source_path: str, config, sheet: Optional[str] = None,
                  progress=None) -> Tuple[List[Line], Any, Any]:
    """Lit un fichier d'elements variables : import, mapping, lignes.

    Meme chemin que la population — memes gardes sur le classeur, meme
    plafond de decompression — parce qu'un second fichier n'est pas un
    second niveau de confiance.
    """
    from ..io.tabular import read_table
    from .logging_setup import log_event
    from .pipeline import _uncompressed_limit

    table = read_table(source_path, sheet,
                       progress.within if progress else None,
                       max_uncompressed=_uncompressed_limit(config),
                       encodings=config.get("population_mapping.encodings")
                       or None)
    lignes, mapping = read_lines(table, config)
    log_event("package", "read_elements",
              detail=f"rows={table.row_count};lines={len(lignes)}")
    return lignes, mapping, table
