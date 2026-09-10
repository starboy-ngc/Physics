"""Jeu d'essai realiste : noms plausibles, anomalies non bloquantes.

Le jeu de demonstration ordinaire porte des matricules et des « NOM00042 » :
il sert a verifier des chiffres, pas a juger un ecran. Celui-ci sert a
l'autre chose — regarder l'outil comme on le regardera en vrai, avec des
patronymes qui ressemblent a des patronymes, une grille de remuneration qui
tient debout, et les anomalies qu'un vrai fichier de paie comporte.

Aucune personne reelle. Les noms sont des combinaisons tirees au hasard
parmi des patronymes et des prenoms courants : le rapprochement d'un nom et
d'un prenom ne designe personne, et le tirage est a graine fixe.

Toutes les anomalies posees ici sont *non bloquantes* : le controle qualite
rend « POINTS DE VIGILANCE », et l'analyse se lance. C'est tout l'objet du
fichier — voir ce que l'outil signale sans qu'il refuse de travailler.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.io.xlsx_writer import write_workbook

HEADERS = [
    "Matricule", "Nom", "Prénom", "Sexe", "Date de naissance", "Date d'entrée",
    "Date de sortie", "BU", "Pays", "Établissement", "Métier", "Poste",
    "Famille métier", "Grade", "Coefficient", "Statut", "Temps de travail",
    "Salaire de base", "Variable", "Rémunération totale", "Manager",
    # Deux colonnes de trop, volontaires : l'une n'est pas reconnue (simple
    # information), l'autre fait doublon avec « Grade » (avertissement).
    "Prime de panier", "Grade",
]

PATRONYMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier", "Morel",
    "Girard", "André", "Lefèvre", "Mercier", "Dupont", "Lambert", "Bonnet",
    "François", "Martinez", "Legrand", "Garnier", "Faure", "Rousseau",
    "Blanc", "Guérin", "Muller", "Henry", "Roussel", "Nicolas", "Perrin",
    "Morin", "Mathieu", "Clément", "Gauthier", "Dumont", "Lopez", "Fontaine",
    "Chevalier", "Robin", "Masson", "Sanchez", "Gérard", "Nguyen", "Boyer",
    "Denis", "Lemaire", "Duval", "Joly", "Gautier", "Roger", "Roche",
    "Roy", "Noël", "Meyer", "Lucas", "Meunier", "Jean", "Perez", "Marchand",
    "Dufour", "Blanchard", "Marie", "Barbier", "Brun", "Dumas", "Brunet",
    "Schmitt", "Leroux", "Colin", "Fernandez", "Pierre", "Renard", "Arnaud",
    "Rolland", "Caron", "Aubert", "Giraud", "Leclerc", "Vidal", "Bourgeois",
    "Renaud", "Lemoine", "Picard", "Gaillard", "Philippe", "Leclercq",
    "Lacroix", "Fabre", "Dupuis", "Olivier", "Rodriguez", "Da Silva",
    "Benali", "Traoré", "Diallo", "Cohen", "Le Gall", "Le Roux", "Kaczmarek",
]

PRENOMS_F = [
    "Marie", "Nathalie", "Isabelle", "Sylvie", "Catherine", "Françoise",
    "Martine", "Christine", "Monique", "Valérie", "Sandrine", "Céline",
    "Stéphanie", "Véronique", "Anne", "Julie", "Aurélie", "Émilie", "Laura",
    "Camille", "Sarah", "Manon", "Chloé", "Léa", "Marine", "Charlotte",
    "Pauline", "Amandine", "Claire", "Élodie", "Justine", "Mathilde",
    "Caroline", "Delphine", "Laëtitia", "Audrey", "Virginie", "Karine",
    "Fatima", "Aminata", "Inès", "Lucie", "Alice", "Clara", "Jeanne",
]

PRENOMS_H = [
    "Jean", "Pierre", "Michel", "Philippe", "Alain", "Nicolas", "Christophe",
    "Patrick", "Daniel", "Bernard", "Éric", "Frédéric", "Laurent", "David",
    "Stéphane", "Pascal", "Olivier", "Sébastien", "Julien", "Thomas",
    "Alexandre", "Vincent", "Guillaume", "Maxime", "Antoine", "Romain",
    "Kévin", "Florian", "Mathieu", "Benjamin", "Clément", "Hugo", "Lucas",
    "Théo", "Adrien", "Damien", "Cédric", "Fabien", "Karim", "Mehdi",
    "Yann", "Bruno", "Serge", "Didier", "Marc",
]

#: BU, etablissements, et poids d'effectif.
UNITES = [
    ("Siège", ["Paris La Défense"], 0.12),
    ("Commerce France", ["Lyon", "Lille", "Bordeaux", "Paris La Défense"], 0.30),
    ("Industrie", ["Valenciennes", "Saint-Étienne"], 0.28),
    ("Supply Chain", ["Orléans", "Valenciennes"], 0.18),
    ("R&D", ["Grenoble", "Paris La Défense"], 0.12),
]
PAYS = "France"

#: Famille metier -> metiers -> postes par niveau croissant.
FAMILLES = {
    "Finance": {
        "Comptabilité": ["Comptable", "Comptable senior", "Chef comptable"],
        "Contrôle de gestion": ["Contrôleur de gestion junior",
                                "Contrôleur de gestion",
                                "Responsable contrôle de gestion"],
    },
    "Ressources humaines": {
        "Paie": ["Gestionnaire de paie", "Gestionnaire de paie senior",
                 "Responsable paie"],
        "Développement RH": ["Chargé de recrutement", "Chargé RH",
                             "Responsable développement RH"],
    },
    "Commerce": {
        "Vente": ["Attaché commercial", "Ingénieur d'affaires",
                  "Directeur de secteur"],
        "Marketing": ["Chargé de marketing", "Chef de produit",
                      "Responsable marketing"],
    },
    "Production": {
        "Fabrication": ["Opérateur de production", "Technicien de production",
                        "Chef d'équipe production"],
        "Qualité": ["Technicien qualité", "Ingénieur qualité",
                    "Responsable qualité"],
        "Maintenance": ["Technicien de maintenance",
                        "Technicien de maintenance senior",
                        "Responsable maintenance"],
    },
    "Logistique": {
        "Entreposage": ["Préparateur de commandes", "Agent logistique",
                        "Chef d'équipe logistique"],
        "Transport": ["Affréteur", "Chargé de transport",
                      "Responsable transport"],
    },
    "Technique": {
        "Études": ["Ingénieur d'études junior", "Ingénieur d'études",
                   "Ingénieur d'études senior"],
        "Informatique": ["Technicien support", "Développeur",
                         "Architecte technique"],
    },
}

#: Metiers par BU : une usine n'emploie pas de chef de produit.
METIERS_PAR_UNITE = {
    "Siège": ["Comptabilité", "Contrôle de gestion", "Paie",
              "Développement RH", "Informatique"],
    "Commerce France": ["Vente", "Marketing", "Comptabilité"],
    "Industrie": ["Fabrication", "Qualité", "Maintenance"],
    "Supply Chain": ["Entreposage", "Transport", "Qualité"],
    "R&D": ["Études", "Informatique", "Qualité"],
}

#: Part de femmes par metier. Une ligne de production et un service paie
#: n'ont pas la meme composition : c'est de la que vient l'« effet de
#: structure » que la directive demande de distinguer de l'ecart a poste
#: comparable. Une mixite uniforme rendrait cet indicateur muet.
PROPENSION_F = {
    "Paie": 0.80, "Développement RH": 0.76, "Comptabilité": 0.68,
    "Contrôle de gestion": 0.52, "Marketing": 0.63, "Vente": 0.36,
    "Fabrication": 0.28, "Qualité": 0.47, "Maintenance": 0.16,
    "Entreposage": 0.31, "Transport": 0.34, "Études": 0.30,
    "Informatique": 0.27,
}

GRADES = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
#: Salaire median a temps plein, par grade.
BASE_PAR_GRADE = {
    "G1": 23500, "G2": 26500, "G3": 30000, "G4": 34500, "G5": 41000,
    "G6": 50000, "G7": 63000, "G8": 82000,
}
STATUTS = ["Ouvrier / Employé", "Agent de maîtrise", "Cadre"]


def _prefixe(unite: str) -> str:
    """Deux lettres tirees du nom de la BU, sans ponctuation.

    « R&D » donnait des matricules « R&0001 » : une esperluette au milieu
    d'un identifiant se retrouve echappee dans tous les formats, et se lit
    mal partout.
    """
    lettres = [caractere for caractere in unite.upper() if caractere.isalpha()]
    return "".join(lettres[:2])


def _grade_du_poste(rang: int, tirage: random.Random) -> str:
    """Un poste junior n'est pas au meme grade qu'un poste senior."""
    plancher = [0, 2, 4][rang]
    return GRADES[min(len(GRADES) - 1,
                      plancher + tirage.choices([0, 1, 2],
                                                weights=[55, 33, 12])[0])]


def _statut(grade: str) -> str:
    index = GRADES.index(grade)
    return STATUTS[0] if index <= 2 else (STATUTS[1] if index <= 4
                                          else STATUTS[2])


def construire(effectif: int, graine: int, reference: _dt.date):
    tirage = random.Random(graine)
    unites = [nom for nom, _sites, _poids in UNITES]
    poids = [poids for _nom, _sites, poids in UNITES]
    salaries = []

    for numero in range(1, effectif + 1):
        unite = tirage.choices(unites, weights=poids)[0]
        sites = next(s for n, s, _p in UNITES if n == unite)
        site = tirage.choice(sites)
        metier = tirage.choice(METIERS_PAR_UNITE[unite])
        famille = next(f for f, m in FAMILLES.items() if metier in m)
        postes = FAMILLES[famille][metier]
        rang = tirage.choices([0, 1, 2], weights=[45, 38, 17])[0]
        poste = postes[rang]
        grade = _grade_du_poste(rang, tirage)

        femme = tirage.random() < PROPENSION_F[metier]
        sexe = "F" if femme else "H"
        prenom = tirage.choice(PRENOMS_F if femme else PRENOMS_H)
        nom = tirage.choice(PATRONYMES)

        age = round(tirage.triangular(21, 63, 39 + rang * 4))
        naissance = reference - _dt.timedelta(days=int(age * 365.2425)
                                              + tirage.randrange(365))
        anciennete = round(tirage.triangular(0, max(age - 21, 1),
                                             min(6 + rang * 2, age - 21)), 1)
        entree = reference - _dt.timedelta(days=int(anciennete * 365.2425))

        base = BASE_PAR_GRADE[grade]
        base *= 1 + 0.010 * min(anciennete, 25)        # effet anciennete
        base *= 1 + tirage.gauss(0, 0.055)             # dispersion
        if unite == "Siège":
            base *= 1.06
        if site == "Paris La Défense":
            base *= 1.04
        if femme:
            # L'ecart que l'outil doit retrouver : environ 5 % a poste egal.
            base *= 1 - abs(tirage.gauss(0.05, 0.015))
        temps = tirage.choices([1.0, 0.8, 0.5], weights=[87, 10, 3])[0]
        if femme and temps == 1.0 and tirage.random() < 0.06:
            temps = 0.8
        base = round(base * temps / 100) * 100

        part = tirage.choices([0.0, 0.03, 0.06, 0.10, 0.15],
                              weights=[30, 25, 22, 15, 8])[0]
        part += GRADES.index(grade) * 0.01
        variable = round(base * max(0.0, part + tirage.gauss(0, 0.02)) / 50) * 50

        sortie = ""
        if tirage.random() < 0.03:
            sortie = entree + _dt.timedelta(days=int(anciennete * 365.2425)
                                            - tirage.randrange(1, 120))

        salaries.append({
            "matricule": f"{_prefixe(unite)}{numero:04d}",
            "nom": nom.upper(), "prenom": prenom, "sexe": sexe,
            "naissance": naissance, "entree": entree, "sortie": sortie,
            "unite": unite, "site": site, "metier": metier, "poste": poste,
            "famille": famille, "grade": grade,
            "coefficient": 100 + GRADES.index(grade) * 30,
            "statut": _statut(grade), "temps": temps,
            "base": base, "variable": variable, "rang": rang,
            "manager": "",
        })

    _rattacher(salaries, tirage)
    lignes = [_ligne(salarie) for salarie in salaries]
    anomalies = _poser_anomalies(lignes, tirage)
    return lignes, anomalies


def _rattacher(salaries, tirage, encadrement: int = 7) -> None:
    """Un organigramme par BU : le plus gradé en haut, encadrement borné."""
    par_unite = {}
    for salarie in salaries:
        par_unite.setdefault(salarie["unite"], []).append(salarie)
    for membres in par_unite.values():
        tirage.shuffle(membres)
        membres.sort(key=lambda s: -GRADES.index(s["grade"]))
        for position, salarie in enumerate(membres):
            if position:
                salarie["manager"] = membres[(position - 1)
                                             // encadrement]["matricule"]


def _ligne(s) -> list:
    return [
        s["matricule"], s["nom"], s["prenom"], s["sexe"], s["naissance"],
        s["entree"], s["sortie"], s["unite"], PAYS, s["site"], s["metier"],
        s["poste"], s["famille"], s["grade"], s["coefficient"], s["statut"],
        s["temps"], s["base"], s["variable"], s["base"] + s["variable"],
        s["manager"],
        # Prime de panier : colonne non reconnue, volontaire.
        s["coefficient"] // 10,
        # Seconde colonne « Grade » : doublon volontaire.
        s["grade"],
    ]


def colonne(nom: str) -> int:
    return HEADERS.index(nom)


def _poser_anomalies(lignes, tirage):
    """Anomalies volontaires, toutes non bloquantes.

    Aucune n'empeche l'analyse : le controle rend « POINTS DE VIGILANCE ».
    C'est l'objet du fichier — voir ce que l'outil signale sans qu'il
    refuse de travailler.
    """
    matricule = colonne("Matricule")
    salaire = colonne("Salaire de base")
    variable = colonne("Variable")
    total = colonne("Rémunération totale")
    naissance = colonne("Date de naissance")
    entree = colonne("Date d'entrée")

    posees = []

    def poser(index, libelle):
        posees.append((index + 2, libelle))       # +2 : en-tete et base 1

    # Conge sans solde : salaire a zero.
    poser(5, "salaire de base à zéro (congé sans solde)")
    lignes[5][salaire] = 0
    lignes[5][total] = lignes[5][variable]

    # Salaire hors plage basse : une saisie en centaines d'euros.
    poser(11, "salaire de base sous le seuil plausible (saisie mensuelle ?)")
    lignes[11][salaire] = 2450
    lignes[11][total] = 2450 + lignes[11][variable]

    # Salaire hors plage haute. La ligne porte aussi un sexe non renseigne,
    # et ce n'est pas un hasard : une valeur pareille tire a elle seule la
    # moyenne du sexe auquel elle appartient — posee sur une femme, elle
    # faisait lire un ecart global de -16 %, les femmes payees davantage ;
    # posee sur un homme, +43 %. Sans sexe, elle reste hors de la
    # comparaison, la mediane n'en bouge pas, et la moyenne s'en trouve
    # visiblement tiree : c'est exactement pourquoi l'outil met la mediane
    # en avant. Un fichier mal rempli l'est rarement sur une seule colonne.
    sexe = colonne("Sexe")
    poser(19, "salaire hors plage haute et sexe non renseigné "
              "(ligne mal saisie)")
    lignes[19][salaire] = 1050000
    lignes[19][total] = 1050000
    lignes[19][sexe] = ""

    # Separateur ambigu : « 45.000 » se lit 45,0 ou 45 000.
    poser(27, "séparateur ambigu dans le salaire (« 52.000 »)")
    lignes[27][salaire] = "52.000"

    # Part variable non numerique.
    poser(34, "part variable non numérique (« NC »)")
    lignes[34][variable] = "NC"

    # Age invraisemblable : un apprenti mal saisi.
    poser(42, "âge hors de la plage plausible (date de naissance erronée)")
    lignes[42][naissance] = _dt.date(2014, 6, 12)

    # Embauches a venir : situation reelle, pas une erreur.
    for index in (58, 59):
        poser(index, "date d'entrée à venir (embauche signée)")
        lignes[index][entree] = _dt.date.today() + _dt.timedelta(days=45)

    # Ligne sans matricule.
    poser(71, "ligne sans matricule")
    lignes[71][matricule] = ""

    # Valeurs atypiques : deux remunerations tres au-dessus de leur poste.
    for index in (88, 103):
        poser(index, "rémunération atypique pour le poste (écart interquartile)")
        lignes[index][salaire] = round(lignes[index][salaire] * 3.4 / 100) * 100
        lignes[index][total] = lignes[index][salaire] + lignes[index][variable]

    posees.append(("colonne", '« Prime de panier » : colonne non reconnue'))
    posees.append(("colonne", '« Grade » présent deux fois'))
    return posees


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lignes", type=int, default=900)
    parser.add_argument("--graine", type=int, default=20260910)
    parser.add_argument("--sortie", default="population-realiste.xlsx")
    parser.add_argument("--date-reference", default="")
    arguments = parser.parse_args()

    reference = (_dt.date.fromisoformat(arguments.date_reference)
                 if arguments.date_reference else _dt.date.today())
    lignes, anomalies = construire(arguments.lignes, arguments.graine,
                                   reference)
    write_workbook(arguments.sortie, [("Population", [HEADERS] + lignes)])
    print(f"{len(lignes)} salariés fictifs écrits dans {arguments.sortie}")
    print("\nAnomalies volontaires, toutes non bloquantes :")
    for repere, libelle in anomalies:
        marque = f"ligne {repere}" if isinstance(repere, int) else repere
        print(f"  {marque:>10} : {libelle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
