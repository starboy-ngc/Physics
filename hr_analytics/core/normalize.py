"""Couche NORMALIZED DATA : pivot entre l'import et le moteur statistique.

RAW -> MAPPING -> NORMALIZED -> ANALYTICS DATASET

Toute la suite du moteur ne connait que `Employee` / `Population`. Changer de
format d'import n'impacte donc que `io.tabular` et `core.mapping`.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import math
import re
import secrets
import unicodedata
from dataclasses import dataclass, field, fields
from typing import Any, ClassVar, Dict, Iterable, List, Optional

from .config import Configuration
from .mapping import MappingResult

#: Symboles monetaires, apostrophes de groupement et espaces, retires sans
#: discussion. Tout le reste — une lettre en particulier — fait refuser la
#: cellule plutot que de la raboter jusqu'a en tirer un nombre.
_CURRENCY_RE = re.compile(r"[\u20ac$\u00a3\u00a5\u20a3\u20b9\u20bd\u00a4"
                          r"\u00a0\u202f\s'\u2019]")
#: Codes devise usuels, toleres en tete ou en fin de cellule.
_CODES = ("eur|usd|gbp|chf|cad|aud|jpy|cny|sek|nok|dkk|pln|czk|huf|ron|bgn|"
          "try|brl|mxn|inr|zar|sgd|hkd|aed|mad|tnd|xof|xaf")
_CODE_LEADING_RE = re.compile(rf"(?i)^(?:{_CODES})\s*")
_CODE_TRAILING_RE = re.compile(rf"(?i)\s*(?:{_CODES})$")
#: Forme acceptee apres nettoyage. Un separateur repete ne peut etre que
#: celui des milliers, et il ne groupe alors que par trois : « 1.234.567 »
#: est un nombre, « 1.2.3.4 » n'en est pas un. La forme precedente acceptait
#: n'importe quel groupement, et retirait ensuite les points : un numero de
#: version lu dans une colonne de salaires devenait 1 234, sans la moindre
#: alerte — precisement la corruption silencieuse que ce controle existe
#: pour empecher.
_NUMBER_SHAPE_RE = re.compile(r"""^[+-]?(?:
      \d+(?:[.,]\d+)?                  # 45000  45000.50  45000,50
    | \d{1,3}(?:\.\d{3})+(?:,\d+)?     # 45.000  45.000,50
    | \d{1,3}(?:,\d{3})+(?:\.\d+)?     # 45,000  45,000.50
    )$""", re.VERBOSE)
#: Nombre deja ecrit sans fioriture. La grande majorite des cellules d'un
#: fichier de paie en sont : les traiter sans passer par le nettoyage evite
#: d'en payer le cout cinq fois, a chaque champ et pour chaque salarie.
_PLAIN_NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
_DATE_FORMATS = (
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d",
    "%d.%m.%Y", "%m/%d/%Y", "%Y%m%d",
)
_DAYS_PER_YEAR = 365.2425

@dataclass
class Employee:
    """Salarie normalise. Les champs derives sont calcules une seule fois."""

    row_number: int
    employee_id: str = ""
    anonymous_id: str = ""
    last_name: str = ""
    first_name: str = ""
    gender: str = ""
    birth_date: Optional[_dt.date] = None
    hire_date: Optional[_dt.date] = None
    leave_date: Optional[_dt.date] = None
    business_unit: str = ""
    country: str = ""
    site: str = ""
    job: str = ""
    job_family: str = ""
    #: Classification conventionnelle : annexe, groupe, coefficient. Ce
    #: sont les trois mots d'une convention collective francaise, et non
    #: un « grade » d'entreprise qui ne se retrouve pas d'un fichier a
    #: l'autre. Le coefficient est un nombre ; les deux autres non — un
    #: groupe s'ecrit « B » ou « 3 bis » aussi souvent qu'un entier.
    annexe: str = ""
    groupe: str = ""
    coefficient: Optional[float] = None
    status: str = ""
    fte: Optional[float] = None
    base_salary: Optional[float] = None
    variable_pay: Optional[float] = None
    total_compensation: Optional[float] = None
    age_years: Optional[float] = None
    tenure_years: Optional[float] = None
    age_band: str = ""
    tenure_band: str = ""
    #: Periode d'observation, telle qu'ecrite dans le fichier. Vide quand la
    #: colonne n'existe pas : le fichier est alors un instantane.
    period: str = ""
    #: Matricule du responsable hierarchique. Vide au sommet de l'arbre.
    manager: str = ""
    issues: List[str] = field(default_factory=list)
    #: Champs declares au mapping mais absents du modele (ex. une notion
    #: metier ajoutee par configuration). Ils sont filtrables et
    #: segmentables au meme titre que les champs natifs.
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def identity(self) -> str:
        """Identite lisible, pour l'ecran de l'analyste et lui seul.

        Elle n'entre jamais dans le resultat d'analyse : c'est ce qui
        garantit qu'aucun document produit, aucun export et aucun journal ne
        peut en porter, quel que soit le reglage. L'interface la reconstruit
        depuis la population qu'elle a deja en memoire.
        """
        name = " ".join(part for part in (self.last_name.upper(),
                                          self.first_name) if part).strip()
        return name or self.employee_id

    def value(self, name: str) -> Any:
        if name in self.extra:
            return self.extra[name]
        return getattr(self, name, None)

    #: Les champs reellement declares par le modele. C'est a eux, et a eux
    #: seuls, qu'un nom venant du parametrage a le droit d'ecrire.
    #: `ClassVar` et non un champ : annote autrement, il deviendrait une
    #: donnee de salarie, chaque instance en recevrait une copie vide, et
    #: le controle ne porterait plus sur rien.
    _NATIFS: ClassVar[frozenset] = frozenset()

    def assign(self, name: str, value: Any) -> None:
        """Ecrit un champ natif, ou le range dans `extra` sinon.

        Le test portait sur `hasattr`, et non sur la liste des champs : un
        fichier dont une colonne s'appelle « Value » ou « Assign », declaree
        comme nouveau champ a l'ecran, recevait le nom technique « value »
        ou « assign » et ecrasait la methode du meme nom. L'analyse tombait
        ensuite sur « 'str' object is not callable », sans que rien ne
        designe la colonne en cause. Les noms reserves — `identity`,
        `__class__` — levaient une autre erreur, tout aussi obscure.

        Rien de tout cela n'executait du code : le modele n'appelle jamais
        ce qu'il recoit. Mais une colonne nommee « Value » n'est pas exotique
        dans un export anglophone, et un outil ne doit pas tomber dessus.
        """
        if name in self._NATIFS:
            setattr(self, name, value)
        else:
            self.extra[name] = value


#: Pose apres la definition : `fields()` demande une classe achevee.
Employee._NATIFS = frozenset(champ.name for champ in fields(Employee))


@dataclass
class Population:
    """Ensemble de salaries normalises + metadonnees de tracabilite."""

    employees: List[Employee] = field(default_factory=list)
    source_name: str = ""
    reference_date: Optional[_dt.date] = None
    mapped_fields: List[str] = field(default_factory=list)
    raw_row_count: int = 0
    #: Tranches effectivement posees sur cette population. Elles peuvent
    #: differer de la configuration, la derniere tranche ouverte etant
    #: prolongee selon les valeurs observees : tout ce qui les affiche doit
    #: donc les lire ici, et non relire le fichier de parametres.
    age_bands: List[Dict[str, Any]] = field(default_factory=list)
    tenure_bands: List[Dict[str, Any]] = field(default_factory=list)
    #: Libelles regroupes a la lecture parce qu'ils ne differaient que par
    #: la casse ou les accents. La liste est publiee : une fusion change
    #: des effectifs et des medianes, elle ne se fait pas en silence.
    merged_labels: List[Dict[str, Any]] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.employees)

    def __iter__(self) -> Iterable[Employee]:
        return iter(self.employees)

    def filtered(self, employees: List[Employee]) -> "Population":
        return Population(
            employees=employees,
            source_name=self.source_name,
            reference_date=self.reference_date,
            mapped_fields=list(self.mapped_fields),
            age_bands=list(self.age_bands),
            tenure_bands=list(self.tenure_bands),
            raw_row_count=self.raw_row_count,
            merged_labels=list(self.merged_labels),
        )


# --------------------------------------------------------------- conversions


def parse_number(value: Any) -> Optional[float]:
    """Convertit une cellule en nombre. Retourne None si non convertible.

    Gere les formats francais ("45 000,50", "45 000 €") et anglo-saxons
    ("45,000.50"), ainsi que la notation comptable entre parentheses
    ("(1 200)" vaut -1 200). Aucune evaluation dynamique n'est utilisee.

    Une cellule qui n'est pas un nombre est refusee, et non rabotee jusqu'a
    en devenir un. La version precedente supprimait tout caractere non
    chiffre : "1E+05" devenait 105, "50k" devenait 50, "12 mois" devenait 12
    et "5O000" — la lettre O frappee a la place du zero — devenait 5 000.
    La cellule passait alors pour un montant plausible, sans la moindre
    alerte. Refusee, elle est comptee « non numerique » par le controle
    qualite, qui la signale avec son numero de ligne.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    if _PLAIN_NUMBER_RE.match(text):
        return float(text)

    # Notation comptable : le signe est porte par les parentheses.
    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative, text = True, text[1:-1].strip()

    text = _strip_currency(text)
    if not _NUMBER_SHAPE_RE.match(text):
        return None
    number = _resolve_separators(text)
    if number is None:
        return None
    return -number if negative else number


def _strip_currency(text: str) -> str:
    """Retire symboles, espaces et code devise ; le reste doit se suffire."""
    text = _CODE_LEADING_RE.sub("", text.strip())
    text = _CODE_TRAILING_RE.sub("", text)
    return _CURRENCY_RE.sub("", text)


def _resolve_separators(text: str) -> Optional[float]:
    """Tranche entre separateur decimal et separateur de milliers.

    Deux separateurs differents : le dernier rencontre est le decimal.
    Un meme separateur repete ("1.234.567") ne peut etre que le separateur
    de milliers. Un separateur unique suivi de trois chiffres reste
    ambigu — la lecture decimale est retenue, et `has_ambiguous_separator`
    la signale au controle qualite plutot que de deviner en silence.
    """
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif text.count(",") > 1:
        text = text.replace(",", "")
    elif text.count(".") > 1:
        text = text.replace(".", "")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


_AMBIGUOUS_RE = re.compile(r"^-?[1-9]\d{0,2}[.,]\d{3}$")
#: Periode ecrite au mois : « 2026-12 », « 2026/12 ».
_MONTH_RE = re.compile(r"^(\d{4})[-/](\d{2})$")


def has_ambiguous_separator(value: Any) -> bool:
    """Detecte une ecriture dont le separateur est ambigu.

    "45.000" vaut 45 000 dans un fichier francais et 45,0 en lecture
    anglo-saxonne. Le moteur retient la lecture standard (separateur
    decimal) mais signale le cas au controle qualite plutot que de deviner
    en silence. Les valeurs commencant par 0 ("0,800") sont exclues : ce
    sont des decimales sans ambiguite.
    """
    if isinstance(value, (int, float)) or value is None:
        return False
    return bool(_AMBIGUOUS_RE.match(str(value).strip().replace(" ", "")))


def parse_date(value: Any) -> Optional[_dt.date]:
    """Convertit une cellule en date. Retourne None si non convertible."""
    if value is None or value == "":
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        # Serie Excel eventuellement transmise en nombre brut.
        try:
            return _dt.date(1899, 12, 30) + _dt.timedelta(days=float(value))
        except (OverflowError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    text = text.split("T")[0].split(" ")[0]
    # Chemin rapide : la forme ISO est de loin la plus frequente, et
    # « fromisoformat » est ecrit en C la ou « strptime » recompile son
    # analyseur a chaque appel. Deux dates par salarie, cent mille salaries :
    # la difference se compte en secondes.
    try:
        return _dt.date.fromisoformat(text)
    except ValueError:
        pass
    for fmt in _DATE_FORMATS:
        try:
            return _dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def years_between(start: _dt.date, end: _dt.date) -> float:
    return (end - start).days / _DAYS_PER_YEAR


def period_key(label: str):
    """Cle de tri d'une periode, sans imposer d'ecriture au fichier.

    Une periode s'ecrit « 2026 », « 2026-12 », « 2026-12-31 » ou
    « Decembre 2026 » selon l'outil qui a produit l'export. Les trois
    premieres se trient comme des dates ; la derniere se trie comme du
    texte. On tente donc la lecture de date, et l'on retombe sur l'ordre
    alphabetique — qui, sur des periodes ecrites de la meme facon dans un
    meme fichier, donne le bon ordre.
    """
    texte = (label or "").strip()
    date = parse_date(texte)
    if date is not None:
        return (0, date.isoformat())
    # « 2026 » et « 2026-12 » ne sont pas des dates completes mais
    # s'ordonnent comme telles. Sans cela elles tombaient dans le tri
    # textuel, et un fichier melangeant les deux ecritures se serait
    # ordonne de travers.
    if texte.isdigit() and len(texte) == 4:
        return (0, f"{int(texte):04d}-12-31")
    mois = _MONTH_RE.match(texte)
    if mois:
        return (0, f"{mois.group(1)}-{mois.group(2)}-31")
    return (1, texte.lower())


def periods_of(population: "Population") -> List[str]:
    """Periodes presentes, de la plus ancienne a la plus recente."""
    return sorted({employee.period for employee in population
                   if employee.period}, key=period_key)


def band_for(value: Optional[float], bands: List[Dict[str, Any]]) -> str:
    """Tranche parametree contenant `value`.

    La borne basse est toujours incluse. La borne haute est exclue par defaut
    (`<2 ans` = anciennete strictement inferieure a 2). Une tranche peut
    declarer `"max_inclusive": true` pour une lecture en unites revolues :
    la tranche d'age `20-29` couvre alors les ages de 20,0 a 29,99 an.
    """
    if value is None:
        return ""
    for band in bands:
        low = band.get("min")
        high = band.get("max")
        if low is not None and value < low:
            continue
        if high is not None:
            if band.get("max_inclusive", False):
                if math.floor(value) > high:
                    continue
            elif value >= high:
                continue
        return str(band.get("label", ""))
    return ""


def extend_open_band(bands: List[Dict[str, Any]], observed_max: Optional[float],
                     step: float, closed_label: str, open_label: str,
                     limit: int = 10) -> List[Dict[str, Any]]:
    """Prolonge la derniere tranche ouverte jusqu'a la valeur observee.

    Une derniere tranche « > 10 ans » range ensemble un salarie de 11 ans
    d'anciennete et un autre de 30 : la comparaison n'a plus de sens des que
    la population contient des carrieres longues. Les tranches suivantes
    sont donc engendrees au pas configure, jusqu'a couvrir le maximum
    reellement present.

    Rien n'est engendre quand la population ne va pas plus loin que la
    tranche ouverte : le decoupage configure reste alors intact.
    """
    if not bands or observed_max is None or step <= 0:
        return bands
    last = bands[-1]
    if last.get("max") is not None:
        return bands            # decoupage entierement borne : rien a prolonger
    floor = last.get("min")
    if floor is None:
        return bands
    extended = list(bands[:-1])
    low = float(floor)
    added = 0
    while low + step < observed_max and added < limit:
        high = low + step
        extended.append({
            "label": closed_label.format(low=_band_number(low),
                                         high=_band_number(high)),
            "min": low, "max": high,
        })
        low = high
        added += 1
    extended.append({"label": open_label.format(low=_band_number(low)),
                     "min": low, "max": None})
    return extended


def _band_number(value: float) -> str:
    """Une borne de tranche s'ecrit sans decimale inutile."""
    return str(int(value)) if float(value).is_integer() else str(value)


def close_the_bottom(bands: List[Dict[str, Any]],
                     label: str = "<{high}") -> List[Dict[str, Any]]:
    """Ajoute la tranche du bas quand le decoupage ne part pas de zero.

    Un decoupage qui commence a 20 ans range un apprenti de 19 ans dans
    « (non renseigne) » : il a un age, et le tableau disait qu'il n'en
    avait pas. Le haut du decoupage se prolonge deja jusqu'a la valeur
    observee ; le bas se ferme de la meme facon, par une tranche « <20 »
    qui tient tout ce qui est en dessous.

    Un fichier de parametres anterieur a cette tranche la retrouve donc
    sans qu'on le retouche : les reglages survivent aux mises a jour, et
    c'est ici, et non dans le fichier, qu'une tranche manquante se
    complete.
    """
    planchers = [float(band["min"]) for band in bands
                 if isinstance(band, dict) and band.get("min") is not None]
    if not planchers or min(planchers) <= 0:
        return list(bands)
    bas = min(planchers)
    return [{"label": label.format(high=_band_number(bas)),
             "min": 0, "max": bas}] + list(bands)


def resolve_bands(config: Configuration, section: str,
                  observed_max: Optional[float]) -> List[Dict[str, Any]]:
    """Tranches d'une section, fermees en bas et prolongees en haut."""
    bands = close_the_bottom(
        config.get(f"{section}.bands", []) or [],
        str(config.get(f"{section}.below_label", "<{high}")))
    if not config.get(f"{section}.auto_extend", False):
        return bands
    return extend_open_band(
        bands, observed_max,
        config.number(f"{section}.extend_step", 5, minimum=0.1),
        str(config.get(f"{section}.band_label", "{low}-{high}")),
        str(config.get(f"{section}.open_band_label", ">{low}")),
        config.number(f"{section}.extend_max_bands", 10, minimum=1,
                      maximum=200, integer=True),
    )


#: Au-dela de cette valeur, une colonne de temps de travail ne peut plus se
#: lire comme un ratio : personne ne travaille a 50 fois le temps plein.
#: C'est donc une echelle en pourcentage.
FTE_RATIO_LIMIT = 1.5

#: Nom du champ de temps de travail. Il est ecrit une fois : le mapping le
#: relie a la colonne du fichier, mais le calcul, lui, a besoin de savoir
#: lequel des champs numeriques porte un temps de travail.
FTE_FIELD = "fte"


def parse_fte(value: Any) -> tuple:
    """Rend (nombre, ecrit_en_pourcent) pour une cellule de temps de travail.

    « 50 % » ne se lit pas comme un montant : le signe est refuse par
    `parse_number`, qui a raison de le refuser pour un salaire. Ici il
    porte une information — l'echelle — et on la retient au lieu de rendre
    la cellule illisible.
    """
    if value is None:
        return None, False
    text = str(value).strip()
    percent = text.endswith("%")
    if percent:
        text = text[:-1].strip()
    return parse_number(text), percent


def apply_fte_scale(employees: List["Employee"], any_percent: bool) -> None:
    """Ramene la colonne de temps de travail a un ratio, ou la refuse.

    La meme notion s'ecrit « 0,8 », « 80 » ou « 80 % » selon le SIRH. Tant
    que rien ne calculait avec elle, l'ecriture n'avait pas d'importance.
    Des qu'on divise un salaire par elle, un « 80 » pris pour 80 divise le
    salaire par quatre-vingts.

    L'echelle se deduit de la colonne entiere, non de la cellule : un
    maximum au-dela de 1,5, ou un seul pourcentage ecrit explicitement,
    et toute la colonne est en pourcentage. Une valeur impossible apres
    mise a l'echelle — nulle, negative, au-dela du temps plein — n'est pas
    une valeur : elle est retiree et la ligne marquee, comme l'est une
    date impossible.
    """
    values = [item.fte for item in employees if item.fte is not None]
    if not values:
        return
    en_pourcent = any_percent or max(values) > FTE_RATIO_LIMIT
    for item in employees:
        if item.fte is None:
            continue
        if en_pourcent:
            # Dans une colonne en pourcentage, un « 1 » vaut 1 % de temps
            # de travail. C'est presque toujours un temps plein mal ecrit,
            # et le diviser par cent multiplierait son salaire par cent.
            if item.fte <= FTE_RATIO_LIMIT:
                item.issues.append("fte:ambiguous_scale")
                item.fte = None
                continue
            item.fte = item.fte / 100.0
        if item.fte is not None and not 0 < item.fte <= 1:
            item.issues.append("fte:out_of_range")
            item.fte = None


def full_time_amount(employee: "Employee", field_name: str) -> Optional[float]:
    """Montant ramene au temps plein, ou None s'il ne peut pas l'etre.

    Les fichiers de paie portent le montant *verse*, non le taux plein :
    un salarie a 80 % y figure pour 80 % de son salaire. Comparer tel quel
    une population feminine plus souvent a temps partiel a une population
    masculine plus souvent a temps plein mesure d'abord la difference de
    temps de travail, et seulement ensuite la difference de remuneration.
    Diviser par le temps de travail les met sur la meme base.

    Un temps de travail inconnu ne se suppose pas egal a un : ce serait
    compter un temps partiel comme un temps plein, c'est-a-dire l'erreur
    meme que ce calcul corrige. Le montant est alors absent, et la
    couverture le dit.
    """
    value = employee.value(field_name)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    if employee.fte is None or not 0 < employee.fte <= 1:
        return None
    return float(value) / employee.fte


def _observed_max(employees: Iterable["Employee"], field_name: str) -> Optional[float]:
    values = [getattr(item, field_name) for item in employees
              if getattr(item, field_name) is not None]
    return max(values) if values else None


def anonymise(identifier: str, salt: str) -> str:
    """Reference stable pour un matricule, irreversible sans le sel.

    Le sel est obligatoire, et c'est tout l'objet de cette fonction. Il
    valait auparavant une constante ecrite dans le code : la reference
    n'etait alors anonyme pour personne. Un matricule vit dans un espace
    minuscule — « E00001 » a « E99999 » —, et quiconque detient l'outil
    detient le sel : retrouver le matricule derriere une reference publiee
    demandait un centieme de seconde et quatre mille essais. Le rapport
    circule, lui.
    """
    digest = hashlib.sha256(f"{salt}:{identifier}".encode("utf-8")).hexdigest()
    return digest[:12].upper()


def anonymisation_salt(config: Configuration) -> str:
    """Sel employe pour cette execution.

    Vide en configuration — le cas par defaut —, il est tire au hasard a
    chaque analyse : les references ne valent alors que dans les documents
    d'une meme execution, et rien ne les relie a un matricule. Renseigne en
    configuration, il rend les references stables d'une analyse a l'autre
    sur ce poste, et seul celui qui detient cette configuration peut les
    rapprocher d'un matricule. Le sel n'entre dans aucun document produit.
    """
    declared = str(config.get("privacy_parameters.anonymisation_salt", "")
                   or "").strip()
    return declared or secrets.token_hex(16)


# ---------------------------------------------------------------- pipeline


def fold_label(texte: Any) -> str:
    """Minuscules sans accent : la cle sous laquelle deux ecritures se
    rejoignent.

    C'est la meme reduction que la recherche des listes deroulantes, et
    c'est voulu : ce que l'utilisateur tient pour un seul libelle quand il
    cherche doit etre un seul libelle quand il compte.
    """
    decompose = unicodedata.normalize("NFD", str(texte).strip())
    return "".join(c for c in decompose
                   if unicodedata.category(c) != "Mn").lower()


def unify_case_variants(employees: List["Employee"],
                        fields: Iterable[str]) -> List[Dict[str, Any]]:
    """Deux ecritures d'un meme libelle n'en font qu'une.

    « RELIURE » saisi une fois et « Reliure » saisi deux cent soixante-cinq
    fois sont le meme metier. Les laisser cote a cote donne deux modalites :
    deux lignes dans la segmentation, deux effectifs, deux medianes, deux
    entrees dans la liste deroulante — et le metier de deux cent
    soixante-six personnes se lit en deux morceaux dont l'un est sous le
    seuil de publication.

    L'ecriture retenue est la plus frequente, et non la premiere vue : une
    faute de frappe est rare par definition, et c'est l'orthographe que la
    paie emploie tous les jours qui doit rester a l'ecran. A egalite
    stricte, la premiere rencontree l'emporte — il faut bien trancher, et
    l'ordre du fichier est le seul depart que l'outil connaisse.

    Rien n'est devine au-dela de ca : « Cadre » et « Cadres » restent deux
    libelles, parce que ce ne sont pas les memes caracteres.
    """
    fusions: List[Dict[str, Any]] = []
    for field_name in fields:
        # cle repliee -> ecriture -> [rang de premiere vue, effectif]
        vus: Dict[str, Dict[str, List[int]]] = {}
        # cle repliee -> salaries concernes, pour ne pas relire la colonne
        # entiere une fois par collision : sur un gros fichier, cela faisait
        # autant de parcours que de libelles a regrouper.
        porteurs: Dict[str, List["Employee"]] = {}
        for rang, employee in enumerate(employees):
            valeur = employee.value(field_name)
            if not isinstance(valeur, str):
                continue
            valeur = valeur.strip()
            if not valeur:
                continue
            cle = fold_label(valeur)
            trace = vus.setdefault(cle, {}).setdefault(valeur, [rang, 0])
            trace[1] += 1
            porteurs.setdefault(cle, []).append(employee)
        for cle, ecritures in vus.items():
            if len(ecritures) < 2:
                continue
            retenue = max(ecritures,
                          key=lambda nom: (ecritures[nom][1],
                                           -ecritures[nom][0]))
            lignes = []
            for employee in porteurs[cle]:
                if str(employee.value(field_name)).strip() != retenue:
                    employee.assign(field_name, retenue)
                    lignes.append(employee.row_number)
            fusions.append({
                "field": field_name,
                "kept": retenue,
                "replaced": sorted(
                    (nom for nom in ecritures if nom != retenue),
                    key=lambda nom: -ecritures[nom][1]),
                "rows": lignes,
            })
    return fusions


def normalise_table(
    headers: List[str],
    rows: List[List[Any]],
    mapping: MappingResult,
    config: Configuration,
    source_name: str = "",
    reference_date: Optional[_dt.date] = None,
) -> Population:
    """Construit la population normalisee a partir du tableau brut."""
    section = config.section("population_mapping")
    numeric_fields = set(section.get("numeric", []))
    date_fields = set(section.get("date", []))
    reference = reference_date or _configured_reference_date(config) or _dt.date.today()

    anonymise_ids = bool(config.get("privacy_parameters.anonymise_identifiers", True))
    # Un seul sel pour toute la population : les documents d'une meme
    # execution se lisent ensemble, et une reference y designe la meme
    # personne d'un onglet a l'autre.
    salt = anonymisation_salt(config)

    employees: List[Employee] = []
    #: Un seul pourcentage ecrit dans la colonne suffit a fixer l'echelle
    #: de toute la colonne : personne ne melange « 0,8 » et « 80 % ».
    fte_en_pourcent = False
    for offset, row in enumerate(rows):
        if all(str(cell).strip() == "" for cell in row):
            continue
        employee = Employee(row_number=offset + 2)  # +2 : en-tete + base 1
        for field_name, index in mapping.field_to_index.items():
            if index >= len(row):
                continue
            raw = row[index]
            if field_name in numeric_fields:
                if field_name == FTE_FIELD:
                    number, ecrit_en_pourcent = parse_fte(raw)
                    fte_en_pourcent = fte_en_pourcent or ecrit_en_pourcent
                else:
                    number = parse_number(raw)
                if number is None and str(raw).strip() != "":
                    employee.issues.append(f"{field_name}:not_numeric")
                elif has_ambiguous_separator(raw):
                    employee.issues.append(f"{field_name}:ambiguous_separator")
                employee.assign(field_name, number)
            elif field_name in date_fields:
                date_value = parse_date(raw)
                if date_value is None and str(raw).strip() != "":
                    employee.issues.append(f"{field_name}:invalid_date")
                employee.assign(field_name, date_value)
            else:
                employee.assign(
                    field_name, str(raw).strip() if raw is not None else ""
                )

        # Un age ou une anciennete negatifs n'existent pas : une date de
        # naissance dans le futur, une sortie anterieure a l'entree. Les
        # calculer quand meme les faisait entrer dans les moyennes publiees,
        # ou ils passaient inapercus — le controle qualite les signale, mais
        # rien n'empechait le chiffre de sortir. Une valeur impossible n'est
        # pas une valeur : elle est absente, et la ligne est marquee.
        if employee.birth_date:
            if employee.birth_date > reference:
                employee.issues.append("birth_date:after_reference")
            else:
                employee.age_years = years_between(employee.birth_date,
                                                   reference)
        end_date = employee.leave_date or reference
        if employee.hire_date:
            if end_date < employee.hire_date:
                employee.issues.append("tenure:end_before_hire")
            else:
                employee.tenure_years = years_between(employee.hire_date,
                                                      end_date)
        employee.anonymous_id = (
            anonymise(employee.employee_id, salt)
            if (anonymise_ids and employee.employee_id)
            else employee.employee_id
        )
        employees.append(employee)

    # Le temps de travail se met a l'echelle en second temps, pour la meme
    # raison que les tranches : son echelle se lit sur la colonne entiere.
    apply_fte_scale(employees, fte_en_pourcent)

    # Les variantes d'ecriture se reduisent de meme en second temps : savoir
    # laquelle est la plus frequente demande la colonne entiere.
    #
    # Les identifiants en sont exclus. Un matricule sert de cle — jointure
    # hierarchique, detection des doublons — et deux cles qui ne different
    # que par la casse peuvent parfaitement designer deux personnes ; les
    # rapprocher serait une decision sur l'identite, pas sur un libelle.
    # Les noms le sont pour la meme raison.
    fusionnables = [
        name for name in mapping.field_to_index
        if name not in numeric_fields and name not in date_fields
        and name not in set(section.get("personal", []))
        and name not in ("employee_id", "manager")
    ]
    merged_labels = (
        unify_case_variants(employees, fusionnables)
        if config.get("population_mapping.merge_case_variants", True)
        else []
    )

    # Les tranches sont posees en second temps : prolonger la derniere
    # tranche ouverte suppose de connaitre le maximum de la population, qui
    # n'est etabli qu'une fois toutes les lignes lues.
    age_bands = resolve_bands(config, "age_parameters",
                              _observed_max(employees, "age_years"))
    tenure_bands = resolve_bands(config, "tenure_parameters",
                                 _observed_max(employees, "tenure_years"))
    for employee in employees:
        employee.age_band = band_for(employee.age_years, age_bands)
        employee.tenure_band = band_for(employee.tenure_years, tenure_bands)

    return Population(
        employees=employees,
        source_name=source_name,
        reference_date=reference,
        mapped_fields=sorted(mapping.field_to_index),
        raw_row_count=len(rows),
        age_bands=age_bands,
        tenure_bands=tenure_bands,
        merged_labels=merged_labels,
    )


def _configured_reference_date(config: Configuration) -> Optional[_dt.date]:
    for path in ("age_parameters.reference_date", "tenure_parameters.reference_date"):
        value = config.get(path)
        if value:
            parsed = parse_date(value)
            if parsed:
                return parsed
    return None
