# Compensation Analytics Engine

Logiciel **local, hors ligne et sans dépendance** d'analyse de rémunération,
destiné aux équipes RH / Compensation & Benefits en environnement d'entreprise
sécurisé.

> **Zéro dépendance** : le moteur n'utilise que la bibliothèque standard Python.
> Pas de `pip install`, pas de DLL tierce, pas d'accès Internet, pas de droits
> administrateur, aucun appel Shell ou PowerShell, aucun code dynamique.

## Pipeline

```
IMPORT ─▶ CONTRÔLE QUALITÉ ─▶ NORMALISATION ─▶ PARAMÉTRAGE ─▶ MOTEUR STATISTIQUE
      ─▶ ANALYSE ─▶ VISUALISATION ─▶ RESTITUTION ─▶ EXPORT
```

## Interface graphique

```bash
python3 -m compensation_analytics.cli interface     # ou sans argument
```

Fenêtre unique, `tkinter` livré avec Python — aucune dépendance. Parcours
Importer → Filtrer → Analyser → Restituer, filtres alimentés par le fichier
chargé, et un nuage ancienneté × rémunération **explorable** : survol pour
identifier, molette pour zoomer, clic sur la légende pour isoler une
population.

Le moteur n'importe jamais l'interface : il reste utilisable en ligne de
commande sur une installation dépourvue de tkinter.

## Démarrage

```bash
# Jeu de démonstration fictif (2 000 salariés)
python3 tools/generate_sample_population.py --rows 2000 --output data/demo.xlsx

# Contrôle qualité
python3 -m compensation_analytics.cli controle data/demo.xlsx

# Analyse complète
python3 -m compensation_analytics.cli analyse data/demo.xlsx \
    --filtre "business_unit=France" \
    --segment grade --segment gender \
    --sortie resultats --ignorer-anomalies
```

Produit cinq livrables : un rapport HTML détaillé, une **synthèse d'une page
paysage** et un **jeu de slides paysage** (chacun en HTML et en PDF), un
classeur Excel et un manifeste de traçabilité.

```bash
# Ne produire que le jeu de slides
python3 -m compensation_analytics.cli analyse data/demo.xlsx --restitution slides
```

Le PDF est **généré par l'outil**, pas imprimé depuis un navigateur : aucune
dépendance, aucun binaire tiers.

## Fonctions couvertes (v1.0.0)

- **Import** XLSX / XLSM / CSV, mapping de colonnes configurable, tolérant à la
  casse et aux accents.
- **Contrôle qualité** : structure, doublons, dates incohérentes, salaires
  manquants/négatifs/extrêmes, seuils de plausibilité — rapport hiérarchisé.
- **Indicateurs population** : effectif, âge et ancienneté (moyenne, médiane),
  répartition par tranches paramétrables.
- **Indicateurs rémunération** : masse salariale, moyenne, médiane, P10, Q1,
  P50, Q3, P90, min, max, robustes aux valeurs manquantes.
- **Dispersion** : Q3−Q1, Q3/Q1, P90/P10, moyenne/médiane, coefficient de
  variation. L'écart-type reste une statistique technique, pas un KPI.
- **Distribution** : histogramme, situations atypiques (méthode interquartile).
- **Nuage de points** ancienneté × rémunération : coloration par dimension,
  info-bulles, droite de tendance, échantillonnage au-delà d'un seuil.
- **Segmentation** : dimensions **declarees en configuration** (ajouter une
  notion metier ne demande aucune modification du code), filtres combinables,
  comparaison de deux populations.
- **Petits effectifs** : masquage, avertissement et désactivation des
  graphiques, sur seuils paramétrables.
- **Traçabilité** : manifeste versionné avec empreinte du fichier source et
  intégralité des paramètres.

## Configuration

Tout est paramétrable hors du code, dans `config/*.json` :

```
population_mapping · age_parameters · tenure_parameters · percentile_parameters
salary_parameters · privacy_parameters · chart_parameters · export_parameters
```

```bash
python3 -m compensation_analytics.cli config --dossier config
```

## Tests

```bash
python3 -m unittest discover -s tests -t .     # 186 tests
python3 tools/benchmark.py                     # 1k → 100k salariés
```

Couverture : statistiques (valeurs de référence alignées sur
`PERCENTILE.INCLUSIVE` d'Excel), contrôle qualité, petits effectifs,
import/export, confidentialité, absence de référence réseau dans la
restitution, et non-régression sur jeu de référence figé.

Aucune donnée RH réelle n'est utilisée : les jeux de test sont générés par un
générateur pseudo-aléatoire à graine fixe.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — modules, décisions,
  sécurité, performance, feuille de route.
- [`docs/GUIDE_UTILISATEUR.md`](docs/GUIDE_UTILISATEUR.md) — guide RH.

## Prérequis

Python 3.9 ou supérieur. Rien d'autre.
