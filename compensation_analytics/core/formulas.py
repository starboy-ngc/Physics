"""Refaire les calculs dans le tableur, plutot que de les croire sur parole.

Un classeur d'agregats demande de croire l'outil. Ce module ecrit, a cote
de chaque chiffre publie, la formule qui le refait a partir des donnees
individuelles exportees : le lecteur clique sur la cellule, lit
« =MEDIAN(IF('Donnees individuelles'!$D$2:$D$901="Comptable",...)) », et
verifie l'implementation sans lire une ligne de Python.

Trois regles gouvernent ce qui est ecrit ici.

1. *La formule doit dire ce que le moteur fait, et non ce qu'on aimerait
   qu'il fasse.* Les percentiles sont de type 7 inclusif, donc PERCENTILE ;
   l'ecart-type est celui d'un echantillon, donc STDEV ; l'age est un
   nombre de jours divise par 365,2425, comme dans `normalize`.
2. *Les fonctions employees sont les formes historiques* (PERCENTILE,
   STDEV, et non PERCENTILE.INC ou STDEV.S) : les variantes recentes
   exigent dans le fichier un prefixe technique que tous les tableurs
   n'interpretent pas.
3. *Un critere venu du fichier RH n'est jamais concatene tel quel.* Un
   poste nomme « Chargé d'"affaires" » ou « Chef* » casserait la formule ou
   la transformerait en joker silencieux : les guillemets sont doubles et
   les jokers echappes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..io.xlsx_writer import Formula

#: Duree de l'annee employee par la normalisation pour convertir un nombre
#: de jours en annees. Elle est ecrite dans la formule, en toutes lettres :
#: c'est la convention qu'on veut pouvoir contester.
DAYS_PER_YEAR = 365.2425


def column_letter(index: int) -> str:
    """Lettre de colonne d'un tableur, a partir de zero."""
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def sheet_reference(name: str) -> str:
    """Nom d'onglet cite dans une formule.

    Un onglet dont le nom porte une espace ou un accent se cite entre
    apostrophes ; une apostrophe dans le nom se double.
    """
    return "'" + str(name).replace("'", "''") + "'"


def text_literal(value: Any) -> str:
    """Chaine citee dans une formule, guillemets doubles."""
    return '"' + str(value).replace('"', '""') + '"'


def number_literal(value: float) -> str:
    """Nombre ecrit dans une formule : point decimal, jamais d'exposant.

    Le format de fichier n'est pas localise — la virgue decimale et le
    point-virgule sont l'affaire du tableur qui affiche, pas du fichier qui
    stocke.
    """
    texte = repr(float(value))
    if "e" in texte or "E" in texte:
        texte = f"{float(value):f}"
    return texte


class Ledger:
    """L'onglet des donnees individuelles, tel qu'une formule le cite.

    Toutes les formules de controle partent de lui : c'est le seul endroit
    du classeur ou figurent les valeurs, et donc le seul a partir duquel un
    agregat peut etre refait.
    """

    def __init__(self, sheet: str, headers: Sequence[str], row_count: int):
        self.sheet = sheet
        self.headers = [str(header) for header in headers]
        self.row_count = row_count
        self.first_row = 2
        self.last_row = row_count + 1

    # ------------------------------------------------------------ colonnes

    @property
    def empty(self) -> bool:
        """Sans ligne, aucune formule n'a de sens : « SUM(A2:A1) » leve."""
        return self.row_count <= 0

    def has(self, label: str) -> bool:
        return label in self.headers

    def column(self, label: str) -> str:
        return column_letter(self.headers.index(label))

    def range(self, label: str) -> str:
        """Plage absolue d'une colonne, onglet compris."""
        letter = self.column(label)
        return (f"{sheet_reference(self.sheet)}!"
                f"${letter}${self.first_row}:${letter}${self.last_row}")

    # ------------------------------------------------------------ criteres

    def _tests(self, criteria: Sequence[Tuple[str, Any]],
               value_label: Optional[str] = None) -> List[str]:
        """Conditions terme a terme d'un critere.

        Les criteres ne passent jamais par la forme « COUNTIFS(plage,
        critere) ». Cette forme lit son critere : une tranche nommee
        « <2 ans » y devient « moins de 2 », et le tableur compte alors
        trois cent vingt-sept salaries la ou l'outil en voit quarante-quatre.
        Le defaut est silencieux — il ressemble a une erreur de l'outil — et
        aucune convention d'ecriture ne met le libelle a l'abri. La
        comparaison terme a terme, elle, compare un texte a un texte.

        Quand l'agregat porte sur des valeurs, la condition « la valeur est
        renseignee » s'ajoute : sans elle, un salarie sans remuneration
        entrerait dans la moyenne pour zero, alors que le moteur l'ecarte.
        """
        tests = [f"({self.range(label)}={text_literal(value)})"
                 for label, value in criteria]
        if value_label is not None:
            tests.append(f"({self.range(value_label)}<>\"\")")
        return tests

    def _mask(self, criteria: Sequence[Tuple[str, Any]],
              value_label: Optional[str] = None) -> str:
        """Condition d'une formule matricielle : les tests se multiplient."""
        return "*".join(self._tests(criteria, value_label))

    def _tally(self, tests: Sequence[str]) -> str:
        """Comptage des lignes qui remplissent des conditions."""
        return "SUMPRODUCT(" + ",".join(f"--{test}" for test in tests) + ")"

    # ------------------------------------------------------------ agregats

    def count(self, value_label: str,
              criteria: Sequence[Tuple[str, Any]] = ()) -> str:
        if not criteria:
            return f"COUNT({self.range(value_label)})"
        return self._tally(self._tests(criteria, value_label))

    def rows_matching(self, criteria: Sequence[Tuple[str, Any]]) -> str:
        """Effectif d'un segment : les lignes, valorisees ou non."""
        if not criteria:
            return f"COUNTA({self.range(self.headers[0])})"
        return self._tally(self._tests(criteria))

    def total(self, value_label: str,
              criteria: Sequence[Tuple[str, Any]] = ()) -> str:
        if not criteria:
            return f"SUM({self.range(value_label)})"
        tests = self._tests(criteria, value_label)
        return ("SUMPRODUCT(" + ",".join(f"--{test}" for test in tests)
                + f",{self.range(value_label)})")

    def average(self, value_label: str,
                criteria: Sequence[Tuple[str, Any]] = ()) -> str:
        if not criteria:
            return f"AVERAGE({self.range(value_label)})"
        return (f"AVERAGE(IF({self._mask(criteria, value_label)},"
                f"{self.range(value_label)}))")

    def extremum(self, value_label: str, highest: bool,
                 criteria: Sequence[Tuple[str, Any]] = ()) -> str:
        fonction = "MAX" if highest else "MIN"
        if not criteria:
            return f"{fonction}({self.range(value_label)})"
        return (f"{fonction}(IF({self._mask(criteria, value_label)},"
                f"{self.range(value_label)}))")

    def median(self, value_label: str,
               criteria: Sequence[Tuple[str, Any]] = ()) -> str:
        if not criteria:
            return f"MEDIAN({self.range(value_label)})"
        return (f"MEDIAN(IF({self._mask(criteria, value_label)},"
                f"{self.range(value_label)}))")

    def percentile(self, value_label: str, rank: float,
                   criteria: Sequence[Tuple[str, Any]] = ()) -> str:
        part = number_literal(rank / 100.0)
        if not criteria:
            return f"PERCENTILE({self.range(value_label)},{part})"
        return (f"PERCENTILE(IF({self._mask(criteria, value_label)},"
                f"{self.range(value_label)}),{part})")

    def deviation(self, value_label: str,
                  criteria: Sequence[Tuple[str, Any]] = ()) -> str:
        if not criteria:
            return f"STDEV({self.range(value_label)})"
        return (f"STDEV(IF({self._mask(criteria, value_label)},"
                f"{self.range(value_label)}))")

    def share_below(self, value_label: str, bound: float) -> str:
        """Part de la population sous un seuil, en pourcentage."""
        plage = self.range(value_label)
        return (f"COUNTIFS({plage},\"<{number_literal(bound)}\")"
                f"/COUNT({plage})*100")

    def share_between(self, value_label: str, low: float, high: float) -> str:
        plage = self.range(value_label)
        return (f"COUNTIFS({plage},\">={number_literal(low)}\","
                f"{plage},\"<{number_literal(high)}\")"
                f"/COUNT({plage})*100")

    def share_from(self, value_label: str, bound: float) -> str:
        plage = self.range(value_label)
        return (f"COUNTIFS({plage},\">={number_literal(bound)}\")"
                f"/COUNT({plage})*100")

    def bin_count(self, value_label: str, lower: float, upper: float,
                  last: bool) -> str:
        """Effectif d'une classe de l'histogramme.

        Les classes sont fermees a gauche et ouvertes a droite, la derniere
        exceptee — c'est la convention de `statistics_engine.histogram`, et
        une classe de plus ou de moins a la borne suffirait a faire croire
        a un ecart.
        """
        plage = self.range(value_label)
        haut = "<=" if last else "<"
        return (f"COUNTIFS({plage},\">={number_literal(lower)}\","
                f"{plage},\"{haut}{number_literal(upper)}\")")


#: Constructions qui exigent une validation matricielle : une fonction
#: statistique appliquee a un IF terme a terme. La liste est nommee plutot
#: que devinee sur la presence d'un « IF » — l'anciennete en porte un,
#: parfaitement scalaire, et le marquer matriciel serait une approximation
#: la ou tout ce module vise l'exactitude.
_ARRAY_MARKERS = ("MEDIAN(IF(", "PERCENTILE(IF(", "STDEV(IF(",
                  "MAX(IF(", "MIN(IF(", "SUM(IF(", "COUNT(IF(",
                  "AVERAGE(IF(")


def needs_array(expression: str) -> bool:
    return any(marker in expression for marker in _ARRAY_MARKERS)


def cell(expression: str, value: Optional[float]) -> Formula:
    """Formule prete a ecrire, matricielle si son ecriture l'exige."""
    return Formula(expression, value, needs_array(expression))


def difference(left: str, right: str) -> str:
    """Ecart entre la valeur de l'outil et celle du tableur.

    C'est la cellule qui porte la verification : elle vaut zero quand
    l'implementation et le tableur disent la meme chose.
    """
    return f"IF(OR(ISBLANK({left}),ISBLANK({right})),\"\",{right}-{left})"
