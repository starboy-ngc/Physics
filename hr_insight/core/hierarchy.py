"""Arbre hierarchique reconstruit a partir d'une seule colonne : le manager.

Un fichier de paie porte rarement l'organigramme. Il porte en revanche, dans
la plupart des exports, le matricule du responsable de chaque salarie —
c'est tout ce qu'il faut : l'arbre se deduit du rapprochement entre ce
matricule et celui des autres lignes.

De la decoulent deux populations que l'outil ne savait pas nommer :
l'*equipe directe* d'un manager, et son *equipe totale*, qui descend jusqu'au
dernier niveau. La seconde est celle dont un responsable repond ; la
premiere est celle qu'il voit tous les jours.

Le module ne calcule aucune remuneration : il rend des ensembles de
salaries, que le reste du moteur analyse comme n'importe quelle population.
Un fichier hierarchiquement incoherent — un cycle, un manager absent — ne
doit pas faire lever : il rend un arbre ampute et le dit.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .normalize import Employee, Population


class Tree:
    """Arbre d'une population, a une periode donnee.

    L'arbre se construit sur les matricules : le manager d'un salarie est
    l'employe dont le matricule figure dans sa colonne « manager ». Un
    matricule qui ne correspond a personne fait de son subordonne une
    racine — il vaut mieux un arbre a plusieurs racines qu'un salarie
    perdu.
    """

    def __init__(self, population: Population):
        self.employees: Dict[str, Employee] = {}
        self.duplicates: List[str] = []
        for employee in population:
            key = (employee.employee_id or "").strip()
            if not key:
                continue
            if key in self.employees:
                # Deux lignes pour un meme matricule : l'arbre ne peut pas
                # trancher. La premiere fait foi, la seconde est signalee.
                self.duplicates.append(key)
                continue
            self.employees[key] = employee
        self.children: Dict[str, List[str]] = {key: [] for key in
                                               self.employees}
        self.roots: List[str] = []
        self.unknown_managers: List[str] = []
        for key, employee in self.employees.items():
            parent = (employee.manager or "").strip()
            if not parent:
                self.roots.append(key)
                continue
            if parent == key or parent not in self.employees:
                if parent and parent not in self.employees:
                    self.unknown_managers.append(parent)
                self.roots.append(key)
                continue
            self.children[parent].append(key)
        self.cycles = self._break_cycles()
        # Lien de rattachement effectivement retenu, cycles rompus et
        # managers absents deja ecartes. Toute lecture de l'arbre passe par
        # lui : suivre la colonne du fichier ferait dire « niveau 2 » a un
        # salarie que la construction vient de declarer racine.
        self.parents: Dict[str, str] = {}
        for parent, enfants in self.children.items():
            for enfant in enfants:
                self.parents[enfant] = parent

    def _break_cycles(self) -> List[str]:
        """Detache les salaries pris dans un cycle et les rend racines.

        « A encadre B qui encadre A » se rencontre dans un export mal tenu.
        Sans traitement, toute descente dans l'arbre y tournerait sans fin :
        l'outil se figerait sur un fichier, ce qu'aucun message d'erreur ne
        rattrape. Les membres du cycle deviennent des racines, et l'anomalie
        est nommee.
        """
        etat: Dict[str, int] = {}
        pris: List[str] = []
        for depart in self.employees:
            if etat.get(depart):
                continue
            chemin: List[str] = []
            courant: Optional[str] = depart
            while courant and etat.get(courant, 0) == 0:
                etat[courant] = 1
                chemin.append(courant)
                courant = (self.employees[courant].manager or "").strip()
                if courant not in self.employees:
                    courant = None
            if courant and etat.get(courant) == 1:
                # On est retombe sur un noeud du chemin courant : cycle.
                depuis = chemin.index(courant)
                for membre in chemin[depuis:]:
                    pris.append(membre)
                    parent = (self.employees[membre].manager or "").strip()
                    if parent in self.children and membre in self.children[parent]:
                        self.children[parent].remove(membre)
                    if membre not in self.roots:
                        self.roots.append(membre)
            for membre in chemin:
                etat[membre] = 2
        return sorted(set(pris))

    # ------------------------------------------------------------ lecture

    def managers(self) -> List[str]:
        """Matricules encadrant au moins une personne."""
        return sorted(key for key, enfants in self.children.items() if enfants)

    def direct(self, key: str) -> List[Employee]:
        """Equipe directe : celle qu'un responsable voit tous les jours."""
        return [self.employees[child] for child in self.children.get(key, [])]

    def total(self, key: str) -> List[Employee]:
        """Equipe totale : tous les descendants, jusqu'au dernier niveau.

        C'est la population dont un responsable repond, et elle ne se lit pas
        sur une colonne : il faut descendre l'arbre.
        """
        membres: List[Employee] = []
        a_voir = list(self.children.get(key, []))
        vus = {key}
        while a_voir:
            courant = a_voir.pop()
            if courant in vus:
                continue
            vus.add(courant)
            membres.append(self.employees[courant])
            a_voir.extend(self.children.get(courant, []))
        return membres

    def depth(self, key: str) -> int:
        """Niveau hierarchique, la racine valant 1. Zero si inconnu."""
        if key not in self.employees:
            return 0
        return len(self.line(key))

    def line(self, key: str) -> List[str]:
        """Chaine de responsabilite, du sommet jusqu'a l'interesse."""
        chaine: List[str] = []
        courant: Optional[str] = key
        vus: set = set()
        while courant in self.employees and courant not in vus:
            vus.add(courant)
            chaine.append(courant)
            courant = self.parents.get(courant)
        return list(reversed(chaine))

    def summary(self) -> Dict[str, Any]:
        """Ce qu'il faut dire de l'arbre avant de s'en servir."""
        return {
            "employees": len(self.employees),
            "managers": len(self.managers()),
            "roots": len(self.roots),
            "depth": max((self.depth(key) for key in self.employees),
                         default=0),
            "unknown_managers": sorted(set(self.unknown_managers)),
            "cycles": self.cycles,
            "duplicates": sorted(set(self.duplicates)),
        }


def team_rows(population: Population, tree: Tree,
              keys: Optional[Sequence[str]] = None) -> List[Dict[str, Any]]:
    """Une ligne par manager : effectifs direct et total, niveau.

    Le tableau qui sert a choisir une equipe avant de l'analyser.
    """
    rows: List[Dict[str, Any]] = []
    for key in (keys if keys is not None else tree.managers()):
        manager = tree.employees.get(key)
        if manager is None:
            continue
        rows.append({
            "manager": key,
            "identity": manager.identity,
            "job": manager.job,
            "depth": tree.depth(key),
            "direct": len(tree.children.get(key, [])),
            "total": len(tree.total(key)),
        })
    rows.sort(key=lambda row: (row["depth"], -row["total"], row["manager"]))
    return rows


def team_population(population: Population, tree: Tree, key: str,
                    include_manager: bool = True,
                    direct_only: bool = False) -> Population:
    """Population d'une equipe, prete a etre analysee comme une autre.

    Le responsable y est compte par defaut : une equipe sans son manager
    n'est pas l'objet dont on parle quand on demande « la remuneration de
    l'equipe de X ».
    """
    membres = (tree.direct(key) if direct_only else tree.total(key))
    if include_manager and key in tree.employees:
        membres = [tree.employees[key]] + list(membres)
    return population.filtered(membres)
