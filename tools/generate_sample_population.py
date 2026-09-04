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
    "Date de sortie", "BU", "Pays", "Établissement", "Métier", "Famille métier",
    "Grade", "Coefficient", "Statut", "Temps de travail", "Salaire de base",
    "Variable", "Rémunération totale",
]

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
            business_unit, country, rng.choice(SITES), job, family, grade,
            100 + grade_index * 25, status, fte, base, variable, base + variable,
        ])

    if defects and len(rows) > 30:
        # Defauts volontaires pour exercer le controle qualite.
        rows[3][16] = ""                                   # salaire manquant
        rows[5][16] = -1500                                # salaire negatif
        rows[7][4] = reference + _dt.timedelta(days=400)   # naissance future
        rows[9][6] = rows[9][5] - _dt.timedelta(days=30)   # sortie avant entree
        rows[11][16] = 950000                              # valeur extreme
        rows.append(list(rows[13]))                        # doublon de matricule
    return rows


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
    rows = build_rows(args.rows, args.seed, reference, defects=not args.clean)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    if args.output.lower().endswith(".csv"):
        import csv
        with open(args.output, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter=";", lineterminator="\n")
            writer.writerow(HEADERS)
            for row in rows:
                writer.writerow([
                    value.isoformat() if isinstance(value, _dt.date) else value
                    for value in row
                ])
    else:
        write_workbook(args.output, [("Population", [HEADERS] + rows)])
    print(f"{len(rows)} salariés fictifs écrits dans {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
