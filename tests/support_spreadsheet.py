"""Un tableur minimal, pour relire les formules que l'export ecrit.

Le classeur de controle promet qu'un tableur, en refaisant les calculs,
retrouve les chiffres de l'outil. Cette promesse ne se verifie pas en
relisant le texte des formules : il faut les executer. Ce module est donc
un evaluateur du sous-ensemble exact de fonctions que l'export emploie —
COUNTIFS, AVERAGEIFS, MEDIAN(IF(...)), PERCENTILE, STDEV et l'arithmetique
qui les relie.

Il est ecrit ici, dans les tests, et non dans l'outil : il ne sert qu'a
prouver que les formules produites disent bien ce qu'elles pretendent. Sans
dependance, comme le reste.

Les conventions suivies sont celles d'un tableur :
— une plage est une liste de valeurs, les cellules vides comprises ;
— les fonctions statistiques ignorent le texte, les vides et les FAUX ;
— un critere texte se compare sans casse, un critere « >=1000 » se compare
  numeriquement ;
— PERCENTILE est la methode inclusive de type 7.
"""

from __future__ import annotations

import datetime as _dt
import math
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from compensation_analytics.io.xlsx_writer import Formula


class FormulaError(Exception):
    """Formule que cet evaluateur ne sait pas lire."""


# --------------------------------------------------------------- lexique

_TOKEN_RE = re.compile(r"""
      (?P<space>\s+)
    | (?P<string>"(?:[^"]|"")*")
    | (?P<ref>(?:'(?:[^']|'')*'|[A-Za-z_À-ÿ][\w.À-ÿ]*)!\$?[A-Z]+\$?\d+
              (?::\$?[A-Z]+\$?\d+)?)
    | (?P<local>\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)
    | (?P<name>[A-Za-z][A-Za-z0-9.]*)
    | (?P<number>\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)
    | (?P<operator><>|<=|>=|[-+*/^()<>=,&])
""", re.VERBOSE)


def _tokens(text: str) -> List[Tuple[str, str]]:
    result: List[Tuple[str, str]] = []
    position = 0
    while position < len(text):
        match = _TOKEN_RE.match(text, position)
        if match is None:
            raise FormulaError(f"caractère inattendu : {text[position:][:20]!r}")
        position = match.end()
        kind = match.lastgroup
        if kind != "space":
            result.append((kind, match.group()))
    return result


class Workbook:
    """Les onglets tels que `build_sheets` les rend, lus comme un tableur."""

    def __init__(self, sheets: Sequence[Tuple[str, Sequence[Sequence[Any]]]]):
        self.sheets: Dict[str, Sequence[Sequence[Any]]] = {
            name: rows for name, rows in sheets}

    # -------------------------------------------------------- lecture

    def cell(self, sheet: str, column: int, row: int) -> Any:
        rows = self.sheets.get(sheet)
        if rows is None:
            raise FormulaError(f"onglet inconnu : {sheet}")
        if row - 1 >= len(rows):
            return None
        ligne = rows[row - 1]
        if column - 1 >= len(ligne):
            return None
        value = ligne[column - 1]
        if isinstance(value, Formula):
            return value.value
        return _serial(value)

    def evaluate(self, expression: str, sheet: str) -> Any:
        return _Parser(self, sheet, _tokens(expression)).parse()


#: Origine des dates d'un tableur. Une date y est un nombre de jours :
#: l'age se calcule par soustraction, et l'evaluateur doit lire les dates
#: comme le tableur les lit.
_EPOCH = _dt.date(1899, 12, 30)


def _serial(value: Any) -> Any:
    if isinstance(value, _dt.datetime):
        return (value.date() - _EPOCH).days
    if isinstance(value, _dt.date):
        return (value - _EPOCH).days
    return value


def _column_index(letters: str) -> int:
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index


def _split_reference(text: str, default_sheet: str) -> Tuple[str, str]:
    if "!" not in text:
        return default_sheet, text
    sheet, rest = text.split("!", 1)
    if sheet.startswith("'"):
        sheet = sheet[1:-1].replace("''", "'")
    return sheet, rest


class _Parser:
    """Descente recursive sur la grammaire d'une formule."""

    def __init__(self, workbook: Workbook, sheet: str,
                 tokens: List[Tuple[str, str]]):
        self.workbook = workbook
        self.sheet = sheet
        self.tokens = tokens
        self.position = 0

    # ------------------------------------------------------ mecanique

    def _peek(self) -> Optional[Tuple[str, str]]:
        return (self.tokens[self.position]
                if self.position < len(self.tokens) else None)

    def _take(self) -> Tuple[str, str]:
        token = self._peek()
        if token is None:
            raise FormulaError("formule tronquée")
        self.position += 1
        return token

    def _expect(self, text: str) -> None:
        kind, value = self._take()
        if value != text:
            raise FormulaError(f"attendu {text!r}, trouvé {value!r}")

    def parse(self) -> Any:
        value = self._comparison()
        if self._peek() is not None:
            raise FormulaError(f"reste à lire : {self.tokens[self.position:]}")
        return value

    # ------------------------------------------------------ grammaire

    def _comparison(self) -> Any:
        left = self._sum()
        while True:
            token = self._peek()
            if token is None or token[1] not in ("=", "<>", "<", "<=", ">", ">="):
                return left
            operator = self._take()[1]
            right = self._sum()
            left = _compare(operator, left, right)

    def _sum(self) -> Any:
        left = self._product()
        while True:
            token = self._peek()
            if token is None or token[1] not in ("+", "-"):
                return left
            operator = self._take()[1]
            right = self._product()
            left = _arithmetic(operator, left, right)

    def _product(self) -> Any:
        left = self._unary()
        while True:
            token = self._peek()
            if token is None or token[1] not in ("*", "/"):
                return left
            operator = self._take()[1]
            right = self._unary()
            left = _arithmetic(operator, left, right)

    def _unary(self) -> Any:
        token = self._peek()
        if token and token[1] == "-":
            self._take()
            return _arithmetic("-", 0.0, self._unary())
        return self._atom()

    def _atom(self) -> Any:
        kind, value = self._take()
        if kind == "number":
            return float(value)
        if kind == "string":
            return value[1:-1].replace('""', '"')
        if kind in ("ref", "local"):
            return self._range(value)
        if kind == "name":
            return self._call(value.upper())
        if value == "(":
            inner = self._comparison()
            self._expect(")")
            return inner
        raise FormulaError(f"élément inattendu : {value!r}")

    def _range(self, text: str) -> Any:
        sheet, rest = _split_reference(text, self.sheet)
        parts = rest.split(":")
        coordinates = []
        for part in parts:
            match = re.fullmatch(r"\$?([A-Z]{1,3})\$?(\d+)", part)
            if match is None:
                raise FormulaError(f"référence illisible : {text!r}")
            coordinates.append((_column_index(match.group(1)),
                                int(match.group(2))))
        if len(coordinates) == 1:
            return self.workbook.cell(sheet, *coordinates[0])
        (col1, row1), (col2, row2) = coordinates
        return [self.workbook.cell(sheet, column, row)
                for column in range(col1, col2 + 1)
                for row in range(row1, row2 + 1)]

    def _call(self, name: str) -> Any:
        self._expect("(")
        arguments: List[Any] = []
        if self._peek() and self._peek()[1] == ")":
            self._take()
        else:
            while True:
                arguments.append(self._comparison())
                kind, value = self._take()
                if value == ")":
                    break
                if value != ",":
                    raise FormulaError(f"séparateur attendu, trouvé {value!r}")
        return _apply(name, arguments)


# ------------------------------------------------------------- operations


def _numbers(values: Any) -> List[float]:
    """Valeurs numeriques d'une plage : ni texte, ni vide, ni booleen."""
    if not isinstance(values, list):
        values = [values]
    kept: List[float] = []
    for value in values:
        if isinstance(value, bool) or value is None or value == "":
            continue
        if isinstance(value, (int, float)):
            kept.append(float(value))
    return kept


def _arithmetic(operator: str, left: Any, right: Any) -> Any:
    if isinstance(left, list) or isinstance(right, list):
        gauche = left if isinstance(left, list) else [left] * len(right)
        droite = right if isinstance(right, list) else [right] * len(gauche)
        return [_arithmetic(operator, a, b) for a, b in zip(gauche, droite)]
    a, b = _scalar(left), _scalar(right)
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if b == 0:
        raise FormulaError("division par zéro")
    return a / b


def _scalar(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if value is None or value == "":
        return 0.0
    raise FormulaError(f"nombre attendu, trouvé {value!r}")


def _compare(operator: str, left: Any, right: Any) -> Any:
    if isinstance(left, list):
        return [_compare(operator, item, right) for item in left]
    if operator == "=":
        return _same(left, right)
    if operator == "<>":
        return not _same(left, right)
    a, b = _scalar(left), _scalar(right)
    return {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[operator]


def _same(left: Any, right: Any) -> bool:
    if isinstance(left, str) or isinstance(right, str):
        return (str(left or "").strip().casefold()
                == str(right or "").strip().casefold())
    return _scalar(left) == _scalar(right)


_CRITERION_RE = re.compile(r"^(<>|<=|>=|<|>|=)?(.*)$", re.DOTALL)


def _matches(value: Any, criterion: Any) -> bool:
    """Critere d'un COUNTIFS : comparaison, joker echappe, ou egalite."""
    if not isinstance(criterion, str):
        return _same(value, criterion)
    operator, reste = _CRITERION_RE.match(criterion).groups()
    if operator in ("<>", None, "=") and reste == "":
        vide = value is None or value == ""
        return not vide if operator == "<>" else vide
    attendu: Any = reste
    try:
        attendu = float(reste)
    except ValueError:
        pass
    if operator in (None, "="):
        return _same(value, _unescape(attendu))
    if operator == "<>":
        return not _same(value, _unescape(attendu))
    if value is None or value == "" or isinstance(value, str):
        return False
    return _compare(operator, value, attendu)


def _unescape(value: Any) -> Any:
    """Jokers neutralises par l'export : « ~* » vaut une etoile litterale."""
    if not isinstance(value, str):
        return value
    return value.replace("~*", "*").replace("~?", "?").replace("~~", "~")


def _conditions(arguments: Sequence[Any], start: int) -> List[Tuple[List, Any]]:
    pairs: List[Tuple[List, Any]] = []
    index = start
    while index + 1 < len(arguments) + 1 and index + 1 <= len(arguments) - 1:
        pairs.append((arguments[index], arguments[index + 1]))
        index += 2
    return pairs


def _kept(pairs: Sequence[Tuple[List, Any]]) -> List[int]:
    """Indices des lignes qui remplissent tous les criteres."""
    if not pairs:
        return []
    longueur = len(pairs[0][0])
    return [index for index in range(longueur)
            if all(_matches(plage[index], critere) for plage, critere in pairs)]


def _percentile(values: Sequence[float], rank: float) -> float:
    """Methode inclusive dite de type 7, celle de PERCENTILE."""
    ordered = sorted(values)
    if not ordered:
        raise FormulaError("percentile sur une plage vide")
    if len(ordered) == 1:
        return ordered[0]
    position = rank * (len(ordered) - 1)
    bas = int(math.floor(position))
    haut = min(bas + 1, len(ordered) - 1)
    return ordered[bas] + (position - bas) * (ordered[haut] - ordered[bas])


def _apply(name: str, arguments: List[Any]) -> Any:
    if name == "IF":
        condition = arguments[0]
        if isinstance(condition, list):
            valeurs = arguments[1]
            autre = arguments[2] if len(arguments) > 2 else False
            return [(valeurs[index] if isinstance(valeurs, list) else valeurs)
                    if _truth(item) else autre
                    for index, item in enumerate(condition)]
        return arguments[1] if _truth(condition) else (
            arguments[2] if len(arguments) > 2 else False)
    if name == "OR":
        return any(_truth(item) for item in _flat(arguments))
    if name == "ISBLANK":
        value = arguments[0]
        return value is None or value == ""
    if name == "ABS":
        return abs(_scalar(arguments[0]))
    if name == "DATE":
        import datetime as _dt
        return (_dt.date(int(arguments[0]), int(arguments[1]),
                         int(arguments[2])) - _dt.date(1899, 12, 30)).days
    if name == "COUNT":
        return float(len(_numbers(arguments[0])))
    if name == "COUNTA":
        return float(sum(1 for value in arguments[0]
                         if value is not None and value != ""))
    if name in ("COUNTIFS", "SUMIFS", "AVERAGEIFS"):
        decalage = 1 if name != "COUNTIFS" else 0
        pairs = [(arguments[index], arguments[index + 1])
                 for index in range(decalage, len(arguments) - 1, 2)]
        lignes = _kept(pairs)
        if name == "COUNTIFS":
            return float(len(lignes))
        valeurs = _numbers([arguments[0][index] for index in lignes])
        if name == "SUMIFS":
            return float(sum(valeurs))
        if not valeurs:
            raise FormulaError("moyenne sur une plage vide")
        return sum(valeurs) / len(valeurs)
    if name == "SUM":
        return float(sum(_numbers(_flat(arguments))))
    if name == "AVERAGE":
        valeurs = _numbers(_flat(arguments))
        return sum(valeurs) / len(valeurs)
    if name == "MEDIAN":
        return _percentile(_numbers(_flat(arguments)), 0.5)
    if name == "PERCENTILE":
        return _percentile(_numbers(arguments[0]), _scalar(arguments[1]))
    if name == "STDEV":
        valeurs = _numbers(_flat(arguments))
        moyenne = sum(valeurs) / len(valeurs)
        return math.sqrt(sum((item - moyenne) ** 2 for item in valeurs)
                         / (len(valeurs) - 1))
    if name == "MIN":
        return min(_numbers(_flat(arguments)))
    if name == "MAX":
        return max(_numbers(_flat(arguments)))
    if name == "SUMPRODUCT":
        total = 0.0
        for index in range(len(arguments[0])):
            produit = 1.0
            for argument in arguments:
                produit *= _scalar(argument[index])
            total += produit
        return total
    raise FormulaError(f"fonction non gérée : {name}")


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def _flat(arguments: Sequence[Any]) -> List[Any]:
    values: List[Any] = []
    for argument in arguments:
        if isinstance(argument, list):
            values.extend(argument)
        else:
            values.append(argument)
    return values
