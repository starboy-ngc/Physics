"""L'organigramme tel qu'on le regarde : la structure, et ce qu'elle porte.

`hierarchy` rend l'arbre et des ensembles de salaries ; il ne calcule aucune
remuneration, et c'est bien ainsi. Mais un organigramme regarde dans un outil
d'analyse de remuneration n'est pas un trombinoscope : la question posee
devant une case n'est pas « qui est-ce », c'est « combien sont-ils, et a quel
niveau de remuneration ». Ce module fait ce rapprochement, et lui seul.

Deux lectures, qui ne se remplacent pas :

    chart_nodes   la structure d'encadrement, en cases emboitees. Seuls les
                  responsables y ont une case ; ceux qui n'encadrent
                  personne sont comptes sous celle de leur responsable. Un
                  organigramme ou chaque salarie serait une case devient
                  illisible passe trente personnes, et la structure — ce
                  qu'on vient precisement y lire — y disparait.

    member_rows   la liste nominative des salaries concernes, une ligne
                  chacun. C'est celle qu'on lit pour preparer un entretien.

Les deux portent sur **la population analysee**, et non sur l'equipe telle
que le fichier la decrit. Un filtre — « France », « cadres » — retire des
salaries de tous les autres onglets : un organigramme qui les montrerait
encore ferait mentir l'effectif affiche a cote. Les salaries ecartes
disparaissent donc, et ceux dont le responsable a ete ecarte se rattachent au
premier responsable encore present au-dessus d'eux. L'arbre reste un arbre,
et ce qu'il totalise est ce que l'analyse totalise.

L'identite n'entre dans aucune des deux lectures : les lignes portent un
matricule et un numero de ligne, et la fenetre y rapproche un nom si le
parametrage l'y autorise — a l'ecran seulement. C'est la discipline de tout
l'outil, et c'est elle qui garantit qu'aucun document produit ne peut porter
un nom.

Les seuils de confidentialite valent ici comme ailleurs : une mediane
d'equipe n'est rendue que si l'effectif dont le montant est calculable
atteint le seuil de publication. Une case de trois personnes affiche sa
taille, jamais sa remuneration — sans quoi l'organigramme serait le chemin le
plus court vers le salaire du voisin.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set

from . import statistics_engine as stats
from .config import Configuration, analysis_field
from .hierarchy import Tree
from .metrics import PrivacyRules
from .normalize import full_time_amount


class _Scope:
    """L'equipe retenue, re-rattachee aux seuls salaries qui y restent.

    Objet de travail des deux lectures : elles ont besoin des memes trois
    choses — qui est retenu, qui depend de qui une fois les absents retires,
    et combien chacun porte.
    """

    def __init__(self, tree: Tree, key: str, config: Configuration,
                 keep: Optional[Iterable[str]] = None,
                 direct_only: bool = False):
        self.tree = tree
        self.root = key
        self.rules = PrivacyRules.from_config(config)
        self.field = analysis_field(config)
        gardes: Optional[Set[str]] = None if keep is None else set(keep)

        # Perimetre de l'equipe, avant filtres : exactement celui que le
        # moteur analyse, « equipe directe » comprise.
        if direct_only:
            candidats = list(tree.children.get(key, []))
        else:
            candidats = [membre.employee_id for membre in tree.total(key)]
        self.members: List[str] = [membre for membre in candidats
                                   if gardes is None or membre in gardes]
        # Le responsable choisi fait toujours la racine du dessin, meme si un
        # filtre l'a retire de la population : c'est l'equipe qu'on a
        # demandee. Il n'est compte dans les effectifs que s'il y reste.
        self.root_kept = gardes is None or key in gardes
        retenus = set(self.members)

        # Re-rattachement : le premier responsable encore present au-dessus.
        # Sans lui, un filtre qui retire un chef de service detacherait son
        # service entier, et l'organigramme perdrait trente personnes que
        # les autres onglets comptent toujours.
        self.children: Dict[str, List[str]] = {key: []}
        for membre in self.members:
            self.children.setdefault(membre, [])
        for membre in self.members:
            parent = tree.parents.get(membre)
            while parent is not None and parent != key and parent not in retenus:
                parent = tree.parents.get(parent)
            self.children[parent if parent in self.children else key].append(
                membre)
        for enfants in self.children.values():
            enfants.sort()
        # Base de comparaison de la page, decidee une fois sur l'equipe
        # entiere : un calcul par case ferait cohabiter deux bases dans un
        # meme dessin, et deux medianes qui ne se comparent pas.
        self.full_time = any(
            full_time_amount(self.tree.employees[membre], self.field)
            is not None
            for membre in ([key] if key in tree.employees else []) + self.members)
        # Rattachement effectif, dans l'autre sens. Le reconstruire a chaque
        # ligne demanderait de parcourir tout l'arbre par ligne, soit le
        # carre de l'effectif sur une page qui peut en porter deux mille.
        self.parents: Dict[str, str] = {
            enfant: parent for parent, enfants in self.children.items()
            for enfant in enfants}

    # ------------------------------------------------------------ lecture

    def descendants(self, key: str) -> List[str]:
        """Tous les subordonnes d'un matricule, re-rattachements compris."""
        trouves: List[str] = []
        a_voir = list(self.children.get(key, []))
        vus = {key}
        while a_voir:
            courant = a_voir.pop()
            if courant in vus:
                continue
            vus.add(courant)
            trouves.append(courant)
            a_voir.extend(self.children.get(courant, []))
        return trouves

    def amount_of(self, key: str) -> Optional[float]:
        """Montant d'un salarie sur la base retenue pour la page.

        A temps plein, comme partout ailleurs dans l'outil : la mediane
        d'une equipe ou trois personnes sont a 80 % ne veut rien dire
        autrement. Mais la colonne du temps de travail n'est pas
        obligatoire : quand elle n'est renseignee pour personne, tout
        serait masque faute d'une donnee que le fichier ne porte pas. On
        retombe alors sur le montant verse, et `full_time` le dit — c'est
        la regle de la page des ecarts, et elle doit etre la meme ici.
        """
        employee = self.tree.employees.get(key)
        if employee is None:
            return None
        if self.full_time:
            return full_time_amount(employee, self.field)
        value = employee.value(self.field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return None
        return float(value)

    def amounts(self, keys: Iterable[str]) -> List[float]:
        """Les montants calculables parmi ceux-la, les autres ecartes."""
        montants = []
        for key in keys:
            amount = self.amount_of(key)
            if amount is not None:
                montants.append(amount)
        return montants

    def headcount(self) -> int:
        return len(self.members) + (1 if self.root_kept else 0)


def chart_nodes(tree: Tree, key: str, config: Configuration,
                keep: Optional[Iterable[str]] = None,
                direct_only: bool = False) -> Optional[Dict[str, Any]]:
    """Structure d'encadrement de l'equipe, en arbre de cases.

    Chaque case porte son responsable, le nombre de personnes qu'il encadre
    en direct et au total, le nombre de ses rattaches directs qui n'encadrent
    personne, et la mediane de son equipe quand elle est publiable.

    « Equipe directe seulement » rend une case unique : il n'y a alors qu'un
    niveau, et dessiner des cases pour des subordonnes que l'analyse ne
    retient pas tromperait sur la population analysee.
    """
    if key not in tree.employees:
        return None
    scope = _Scope(tree, key, config, keep, direct_only)

    def construire(courant: str, niveau: int) -> Dict[str, Any]:
        employee = tree.employees[courant]
        directs = scope.children.get(courant, [])
        # Les responsables font une case, les autres un compte sous la case.
        encadrants = [enfant for enfant in directs if scope.children.get(enfant)]
        totale = scope.descendants(courant)
        montants = scope.amounts([courant] + totale)
        publiable = scope.rules.may_publish(len(montants))
        return {
            "manager": courant,
            "row": employee.row_number,
            "job": employee.job,
            "level": niveau,
            "direct": len(directs),
            "total": len(totale),
            "individuals": len(directs) - len(encadrants),
            "amount": stats.median(montants) if publiable else None,
            "masked": not publiable,
            "full_time": scope.full_time,
            "children": [construire(enfant, niveau + 1)
                         for enfant in encadrants],
        }

    return construire(key, 0)


def member_rows(tree: Tree, key: str, config: Configuration,
                keep: Optional[Iterable[str]] = None,
                direct_only: bool = False) -> List[Dict[str, Any]]:
    """Un salarie par ligne : la liste des gens concernes par l'equipe.

    L'ordre suit l'arbre — le responsable, puis ses rattaches, chacun suivi
    de sa propre equipe — et non l'alphabet : c'est l'ordre dans lequel se
    lit un organigramme, et il porte le rattachement sans qu'on ait a le
    relire colonne par colonne.

    Les montants individuels ne sont rendus que si l'equipe entiere est
    publiable. Sous le seuil, la liste garde ses lignes — savoir qui compose
    une equipe de trois n'est un secret pour personne qui l'analyse — mais
    ses montants tombent.
    """
    if key not in tree.employees:
        return []
    scope = _Scope(tree, key, config, keep, direct_only)
    comptes = ([key] + scope.members) if scope.root_kept else scope.members
    publiable = scope.rules.may_publish(len(scope.amounts(comptes)))
    lignes: List[Dict[str, Any]] = []

    def descendre(courant: str, niveau: int) -> None:
        employee = tree.employees[courant]
        directs = scope.children.get(courant, [])
        amount = scope.amount_of(courant)
        lignes.append({
            "employee_id": courant,
            "row": employee.row_number,
            "job": employee.job,
            # Niveau relatif a l'equipe : le responsable choisi vaut 0,
            # quelle que soit sa place dans l'organigramme complet.
            "level": niveau,
            "manager": "" if niveau == 0 else scope.parents.get(courant, ""),
            "manages": len(directs),
            "team": len(scope.descendants(courant)),
            "sex": employee.gender,
            "tenure_years": employee.tenure_years,
            "amount": amount if publiable else None,
            "masked": not publiable,
            # Le responsable retire par un filtre reste la racine du dessin :
            # la ligne le dit plutot que de le compter en silence.
            "out_of_scope": niveau == 0 and not scope.root_kept,
        })
        for enfant in directs:
            descendre(enfant, niveau + 1)

    descendre(key, 0)
    return lignes


def summary(nodes: Optional[Dict[str, Any]],
            rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Les quelques chiffres qui coiffent la page.

    Ils repondent aux questions qu'on se pose devant un organigramme avant
    d'en lire une case : combien de personnes, sur combien de niveaux,
    encadrees par combien de responsables, et combien chacun en porte.
    """
    comptes = [row for row in rows if not row.get("out_of_scope")]
    responsables = [row for row in comptes if row["manages"]]
    return {
        "headcount": len(comptes),
        "levels": (max((row["level"] for row in comptes), default=-1) + 1),
        "managers": len(responsables),
        # Taille moyenne d'une equipe directe, responsables seuls comptes :
        # la rapporter a l'effectif entier donnerait un chiffre que personne
        # ne saurait lire.
        "span": (sum(row["manages"] for row in responsables)
                 / len(responsables)) if responsables else None,
        "amount": (nodes or {}).get("amount"),
        "masked": bool((nodes or {}).get("masked", True)),
        # Base sur laquelle les montants de la page sont comparables : la
        # fenetre l'annonce, elle ne la devine pas.
        "full_time": bool((nodes or {}).get("full_time", True)),
    }
