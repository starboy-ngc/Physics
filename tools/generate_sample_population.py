#!/usr/bin/env python3
"""Généré une population fictive pour les tests et les demonstrations.

Aucune donnée RH reelle n'est utilisée : tout est produit par un generateur
pseudo-aleatoire a graine fixe, donc reproductible.

    python3 tools/generate_sample_population.py --rows 2000 --output data/population_demo.xlsx
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.io.xlsx_writer import write_workbook  # noqa: E402

HEADERS = [
    "Matricule", "Nom", "Prénom", "Sexe", "Date de naissance", "Date d'entrée",
    "Date de sortie", "BU", "Pays", "Établissement", "Métier", "Poste",
    "Famille métier", "Grade", "Coefficient", "Statut", "Temps de travail",
    "Salaire de base", "Variable", "Rémunération totale",
]


def column(name: str) -> int:
    """Position d'une colonne, par son nom.

    Les defauts volontaires visaient des indices ecrits en dur : inserer une
    colonne les decalait tous, et le generateur corrompait silencieusement
    la mauvaise. Ce detour rend l'ordre des colonnes libre.
    """
    return HEADERS.index(name)

BUSINESS_UNITS = ["France", "Iberia", "Benelux", "DACH", "Nordics", "Corporate"]
COUNTRIES = {
    "France": "France", "Iberia": "Espagne", "Benelux": "Belgique",
    "DACH": "Allemagne", "Nordics": "Suede", "Corporate": "France",
}
SITES = ["Siège", "Site Nord", "Site Sud", "Site Est", "Centre de services"]
JOB_FAMILIES = {
    "Finance": ["Controleur de gestion", "Comptable", "Analyste financier"],
    "RH": ["Chargé de recrutement", "HRBP", "Gestionnaire paie"],
    "IT": ["Developpeur", "Administrateur systeme", "Chef de projet SI"],
    "Production": ["Operateur", "Technicien", "Responsable production"],
    "Commerce": ["Commercial", "Key account manager", "Assistant commercial"],
}
GRADES = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
GRADE_BASE = {
    "G1": 24000, "G2": 28000, "G3": 33000, "G4": 39000,
    "G5": 47000, "G6": 58000, "G7": 74000, "G8": 96000,
}
COUNTRY_FACTOR = {
    "France": 1.00, "Espagne": 0.82, "Belgique": 1.06,
    "Allemagne": 1.12, "Suede": 1.09,
}
STATUSES = ["Non cadre", "Agent de maitrise", "Cadre"]

#: Le poste precise le metier d'un niveau de responsabilite. C'est l'axe de
#: comparaison le plus courant en remuneration : deux "Comptable" de grades
#: eloignes n'occupent pas le meme poste et ne se comparent pas.
POSITION_LEVELS = ((2, "junior"), (5, ""), (8, "senior"))


def position_for(job: str, grade_index: int) -> str:
    for ceiling, level in POSITION_LEVELS:
        if grade_index < ceiling:
            return f"{job} {level}".strip()
    return job


def build_rows(count: int, seed: int, reference: _dt.date, defects: bool):
    rng = random.Random(seed)
    rows = []
    for index in range(1, count + 1):
        business_unit = rng.choice(BUSINESS_UNITS)
        country = COUNTRIES[business_unit]
        family = rng.choice(list(JOB_FAMILIES))
        job = rng.choice(JOB_FAMILIES[family])
        grade = rng.choices(GRADES, weights=[10, 16, 18, 18, 14, 12, 8, 4])[0]
        grade_index = GRADES.index(grade)
        status = STATUSES[min(2, grade_index // 3)]
        gender = rng.choice(["F", "H"])

        age = round(rng.triangular(22, 62, 39), 0)
        birth = reference - _dt.timedelta(days=int(age * 365.2425))
        max_tenure = min(age - 20, 35)
        tenure = round(rng.triangular(0, max(max_tenure, 1), 5), 1)
        hire = reference - _dt.timedelta(days=int(tenure * 365.2425))

        base = GRADE_BASE[grade] * COUNTRY_FACTOR[country]
        base *= 1 + 0.012 * tenure                      # effet anciennete
        base *= 1 + rng.gauss(0, 0.09)                  # dispersion individuelle
        if gender == "F":
            base *= 1 - abs(rng.gauss(0.02, 0.02))      # ecart a analyser
        fte = rng.choices([1.0, 0.8, 0.5], weights=[88, 9, 3])[0]
        base = round(base * fte, 0)
        variable = round(base * max(0.0, rng.gauss(0.06 + 0.02 * grade_index, 0.04)), 0)

        rows.append([
            f"E{index:06d}",
            f"NOM{index:05d}", f"PRENOM{index:05d}", gender,
            birth, hire, "",
            business_unit, country, rng.choice(SITES), job,
            position_for(job, grade_index), family, grade,
            100 + grade_index * 25, status, fte, base, variable, base + variable,
        ])

    if defects and len(rows) > 30:
        # Defauts volontaires pour exercer le controle qualite. Les colonnes
        # sont designees par leur nom : leur ordre peut changer sans que ces
        # lignes visent soudain autre chose.
        salary = column("Salaire de base")
        birth_date = column("Date de naissance")
        hire_date = column("Date d'entrée")
        leave_date = column("Date de sortie")
        rows[3][salary] = ""                                    # salaire manquant
        rows[5][salary] = -1500                                 # salaire negatif
        rows[7][birth_date] = reference + _dt.timedelta(days=400)
        rows[9][leave_date] = rows[9][hire_date] - _dt.timedelta(days=30)
        rows[11][salary] = 950000                               # valeur extreme
        rows.append(list(rows[13]))                             # doublon
    return rows


def write_population(output: str, rows: int = 2000, seed: int = 20240101,
                     clean: bool = True,
                     reference: "_dt.date | None" = None) -> str:
    """Ecrit une population fictive, et rend le chemin produit.

    Extrait de la ligne de commande pour que la construction de l'archive
    genere ses jeux de demonstration plutot que d'en copier : aucune donnee
    RH reelle ne peut ainsi se retrouver dans un livrable.
    """
    reference = reference or _dt.date.today()
    lines = build_rows(rows, seed, reference, defects=not clean)
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    if output.lower().endswith(".csv"):
        import csv
        with open(output, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter=";", lineterminator="\n")
            writer.writerow(HEADERS)
            for line in lines:
                writer.writerow([
                    value.isoformat() if isinstance(value, _dt.date) else value
                    for value in line
                ])
    else:
        write_workbook(output, [("Population", [HEADERS] + lines)])
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20240101)
    parser.add_argument("--output", default="data/population_demo.xlsx")
    parser.add_argument("--reference-date", default="")
    parser.add_argument("--clean", action="store_true",
                        help="généré une population sans defaut volontaire")
    args = parser.parse_args()

    reference = (
        _dt.date.fromisoformat(args.reference_date)
        if args.reference_date else _dt.date.today()
    )
    write_population(args.output, rows=args.rows, seed=args.seed,
                     clean=args.clean, reference=reference)
    count = len(build_rows(args.rows, args.seed, reference,
                           defects=not args.clean))
    print(f"{count} salariés fictifs écrits dans {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
