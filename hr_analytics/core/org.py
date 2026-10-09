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

Le seuil de publication, lui, **ne s'applique pas ici par defaut**, et c'est
une decision, pas un oubli. Cette page ne sort jamais de l'ecran : elle ne
figure dans aucun document produit, dans aucun export, dans aucun journal.
Elle porte sur une equipe que son lecteur vient de designer et, dans l'usage,
encadre deja — un responsable qui prepare ses augmentations connait les
remunerations de ses six collaborateurs, et une page qui les masquerait ne
protegerait personne tout en la rendant inutilisable : passe le seuil, un
poste tenu par trois personnes n'aurait ni minimum, ni mediane, ni maximum.

Le seuil reste disponible pour qui en a besoin — une installation partagee,
un poste consulte par plusieurs personnes : `privacy_parameters.mask_in_org_chart`
a vrai le retablit, et la page se masque alors comme les autres. Partout
ailleurs, le seuil continue de s'appliquer sans discussion : ce qui circule
reste protege.
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
        # Le seuil de publication s'applique ici, ou non, selon le
        # parametrage — et par defaut il ne s'applique pas. Voir `masking`
        # en tete de module : cette page ne sort pas de l'ecran, et elle
        # porte sur une equipe que son lecteur encadre deja.
        self.masking = bool(config.get(
            "privacy_parameters.mask_in_org_chart", False))
        # Le poste, au sens ou la page des ecarts l'entend : « travail de
        # meme valeur ». C'est le meme champ, declare au meme endroit, et
        # deux pages qui nommeraient « poste » deux colonnes differentes se
        # contrediraient sous le meme mot. Le metier sert de repli quand la
        # colonne du poste n'est renseignee pour personne — un fichier qui
        # ne porte que « Metier » ne doit pas afficher une page vide.
        from .segmentation import organisational_dimensions

        # Le reglage d'abord, puis les notions declarees dans leur ordre :
        # la premiere que l'equipe renseigne. C'est la regle de la page des
        # ecarts (`pay_equity.category_field`), posee ici sur l'equipe et
        # non sur la population entiere.
        regle = str(config.get("pay_equity_parameters.category_field", "")
                    or "")
        self._job_candidates = [regle] + [
            nom for nom in organisational_dimensions(config) if nom != regle]
        self.job_field = ""
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
        connus = ([key] if key in tree.employees else []) + self.members
        for candidat in self._job_candidates:
            if candidat and any(
                    str(tree.employees[membre].value(candidat) or "").strip()
                    for membre in connus):
                self.job_field = candidat
                break
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

    def job_of(self, key: str) -> str:
        employee = self.tree.employees.get(key)
        if employee is None:
            return ""
        return str(employee.value(self.job_field) or "").strip()

    def may_publish(self, count: int) -> bool:
        """Le seuil, quand il s'applique a cette page."""
        return (not self.masking) or self.rules.may_publish(count)

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
        publiable = scope.may_publish(len(montants))
        # Deux montants, qui ne disent pas la meme chose : celui du
        # responsable — c'est lui que la case affiche, et c'est de lui qu'on
        # parle en regardant une case — et la mediane de son equipe, qui
        # situe ce qu'il encadre. La seconde tient dans l'info-bulle : trois
        # lignes dans une case en font deja une de trop.
        propre = scope.amount_of(courant)
        return {
            "manager": courant,
            "row": employee.row_number,
            "job": scope.job_of(courant),
            "level": niveau,
            "direct": len(directs),
            "total": len(totale),
            "individuals": len(directs) - len(encadrants),
            "amount": stats.median(montants) if publiable else None,
            "own_amount": propre if publiable else None,
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
    publiable = scope.may_publish(len(scope.amounts(comptes)))
    # Rang de remuneration dans l'equipe, 1 pour le mieux remunere. C'est la
    # lecture qui manque a un montant seul : « 31 400 EUR » ne dit rien,
    # « 31 400 EUR, 4e sur 57 » situe la personne dans son equipe. Les
    # ex aequo partagent leur rang, et le suivant saute d'autant — deux
    # premiers, puis un troisieme.
    classement: Dict[str, int] = {}
    if publiable:
        notes = sorted(((scope.amount_of(membre), membre)
                        for membre in comptes
                        if scope.amount_of(membre) is not None),
                       key=lambda couple: (-couple[0], couple[1]))
        précédent, rang = None, 0
        for position, (montant, membre) in enumerate(notes, start=1):
            if montant != précédent:
                rang, précédent = position, montant
            classement[membre] = rang
    total_classés = len(classement)
    lignes: List[Dict[str, Any]] = []

    def descendre(courant: str, niveau: int) -> None:
        employee = tree.employees[courant]
        directs = scope.children.get(courant, [])
        amount = scope.amount_of(courant)
        lignes.append({
            "employee_id": courant,
            "row": employee.row_number,
            "job": scope.job_of(courant),
            # Niveau relatif a l'equipe : le responsable choisi vaut 0,
            # quelle que soit sa place dans l'organigramme complet.
            "level": niveau,
            "manager": "" if niveau == 0 else scope.parents.get(courant, ""),
            "manages": len(directs),
            "team": len(scope.descendants(courant)),
            "sex": employee.gender,
            "age_years": employee.age_years,
            "tenure_years": employee.tenure_years,
            "amount": amount if publiable else None,
            "rank": classement.get(courant),
            "ranked": total_classés,
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
    anciennetés = [row["tenure_years"] for row in comptes
                   if row.get("tenure_years") is not None]
    montants = [row["amount"] for row in comptes
                if row.get("amount") is not None]
    return {
        "headcount": len(comptes),
        "levels": (max((row["level"] for row in comptes), default=-1) + 1),
        "managers": len(responsables),
        "tenure_mean": stats.mean(anciennetés) if anciennetés else None,
        # La mediane et la moyenne de l'equipe entiere : la premiere dit ou
        # se tient le milieu, la seconde ce que l'ecart entre les deux
        # revele d'une remuneration tiree par le haut.
        "median": stats.median(montants) if montants else None,
        "mean": stats.mean(montants) if montants else None,
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


def job_rows(tree: Tree, key: str, config: Configuration,
             keep: Optional[Iterable[str]] = None,
             direct_only: bool = False) -> List[Dict[str, Any]]:
    """L'equipe vue par poste : une ligne par metier, du haut vers le bas.

    C'est la lecture qui precede la liste nominative. Devant une equipe de
    cinquante personnes, la premiere question n'est pas « qui gagne combien »
    mais « quels postes la composent, combien de personnes chacun, et dans
    quelle fourchette ». Un poste dont le minimum et le maximum vont du
    simple au double n'appelle pas la meme conversation qu'un poste
    resserre, et aucune moyenne ne le dirait.

    L'ordre suit la hierarchie, pas l'alphabet : le poste du responsable
    choisi ouvre la liste, puis ceux du niveau en dessous, et ainsi de
    suite. Un poste tenu a deux niveaux differents est classe au plus haut
    des deux — c'est la qu'il entre dans l'organisation.
    """
    lignes = member_rows(tree, key, config, keep=keep, direct_only=direct_only)
    groupes: Dict[str, Dict[str, Any]] = {}
    for ligne in lignes:
        if ligne.get("out_of_scope"):
            continue
        nom = str(ligne.get("job") or "").strip() or "(poste non renseigné)"
        groupe = groupes.setdefault(nom, {"job": nom, "level": ligne["level"],
                                          "headcount": 0, "amounts": []})
        groupe["headcount"] += 1
        groupe["level"] = min(groupe["level"], ligne["level"])
        if ligne.get("amount") is not None:
            groupe["amounts"].append(ligne["amount"])

    rendues: List[Dict[str, Any]] = []
    for groupe in groupes.values():
        montants = sorted(groupe.pop("amounts"))
        groupe.update({
            "known": len(montants),
            "minimum": montants[0] if montants else None,
            "maximum": montants[-1] if montants else None,
            "median": stats.median(montants) if montants else None,
            "mean": stats.mean(montants) if montants else None,
        })
        rendues.append(groupe)
    # Le niveau d'abord, puis l'effectif : a niveau egal, le poste le plus
    # nombreux est celui qui porte l'equipe, et il se lit en premier.
    rendues.sort(key=lambda row: (row["level"], -row["headcount"], row["job"]))
    return rendues
