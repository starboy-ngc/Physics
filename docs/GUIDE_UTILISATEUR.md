# Guide utilisateur

Logiciel **local et hors ligne** : aucune donnée ne quitte votre poste.
Vous pouvez couper Internet avant de l'utiliser.

## 1. Préparer le fichier

Un onglet, une ligne par salarié, une ligne d'en-têtes. Colonnes reconnues
d'office : Matricule, Nom, Prénom, Sexe, Date de naissance, Date d'entrée,
Date de sortie, BU, Pays, Établissement, Métier, Famille métier, Grade,
Coefficient, Statut, Temps de travail, Salaire de base, Variable,
Rémunération totale.

Seules **Matricule** et **Salaire de base** sont obligatoires. La casse et les
accents n'ont pas d'importance. Si vos en-têtes diffèrent, ajoutez-les dans
`config/population_mapping.json` — sans toucher au logiciel.

## 2. Vérifier que les colonnes sont reconnues

```
python3 -m compensation_analytics.cli mapping population.xlsx
```

## 3. Contrôler la qualité des données

```
python3 -m compensation_analytics.cli controle population.xlsx
```

Trois niveaux : **critique** (bloque l'analyse), **avertissement**,
**information**. Le rapport indique les numéros de ligne à corriger.

## 4. Lancer l'analyse

```
python3 -m compensation_analytics.cli analyse population.xlsx --sortie resultats
```

Les fichiers produits dans `resultats/` :

| Fichier | Usage |
|---|---|
| `restitution-*.html` | Rapport détaillé, à lire à l'écran |
| `synthese-*.pdf` / `.html` | **Fiche standard, une page paysage** : indicateurs, percentiles, structure de la population et nuage ancienneté × rémunération |
| `slides-*.pdf` / `.html` | **Jeu de slides paysage** : pour une présentation |
| `analyse-*.xlsx` | Indicateurs par onglet, pour retravailler les chiffres |
| `manifeste-*.json` | Paramètres utilisés, pour refaire l'analyse à l'identique |

Les PDF sont générés directement par l'outil — pas besoin d'imprimer depuis le
navigateur. Dans la version HTML des slides, les flèches ← → font défiler les
pages et les info-bulles restent actives au survol des graphiques.

Les slides s'adaptent à la taille de la fenêtre : sur un écran étroit la page
se réduit proportionnellement, sans jamais imposer de défilement horizontal.
Le rapport détaillé, lui, se réorganise (les indicateurs passent sur une
colonne) et reste lisible sur téléphone.

Pour ne produire qu'une sortie :

```
--restitution slides
--restitution synthese
--restitution rapport
--restitution excel
```

### Filtrer

```
--filtre "business_unit=France"
--filtre "grade=G5|G6|G7"
--filtre "base_salary>=50000"
```

Les filtres se cumulent (ET logique).

### Analyser par segment

```
--segment grade --segment gender --segment job_family
```

Dimensions livrees : `business_unit`, `country`, `site`, `job`, `job_family`,
`grade`, `status`, `gender`, `age_band`, `tenure_band`.

Un champ mal orthographie est refuse avec la liste des champs valides — l'outil
ne renvoie jamais une population vide en silence.

Pour ajouter une dimension propre a votre organisation, declarez-la dans
`config/population_mapping.json` : un alias dans `fields`, une entree dans
`dimensions`. Elle devient filtrable, segmentable et exportable.

### Comparer deux populations

```
--filtre "business_unit=France" --comparer "business_unit!=France" \
  --libelle-comparaison "Hors France"
```

## 5. Adapter les paramètres

```
python3 -m compensation_analytics.cli config --dossier config
```

Puis éditez les fichiers JSON : tranches d'âge et d'ancienneté, percentiles,
seuils de confidentialité, devise, seuils de plausibilité, graphiques, export.
Aucune modification du logiciel n'est nécessaire.

## 6. Protection des données

- Les résultats sont masqués sous 5 salariés, signalés sous 10, les graphiques
  désactivés sous 10 (seuils modifiables).
- Les matricules sont remplacés par une référence anonyme dans les
  restitutions.
- L'export des données individuelles est **désactivé par défaut**.
- Le journal technique ne contient ni nom, ni matricule, ni salaire individuel.

## 7. Lire les « situations atypiques »

Ces situations sont repérées par un **critère statistique** (méthode
interquartile), pas par un jugement RH. Une rémunération haute avec faible
ancienneté peut refléter un recrutement en tension ; une rémunération faible
avec forte ancienneté peut refléter un changement de métier. Elles sont à
analyser, pas à corriger mécaniquement.

## 8. Messages d'erreur

Les messages sont rédigés en langage métier. Exemple :

> La colonne « Salaire de base » n'a pas pu être identifiée. Veuillez vérifier
> le mapping des colonnes d'import.

Le détail technique va dans le journal (`--logs <dossier>`), séparé des données.

## 9. Jeu de démonstration

```
python3 tools/generate_sample_population.py --rows 2000 --output data/demo.xlsx
```

Population entièrement fictive (générateur à graine fixe). Aucune donnée réelle.
