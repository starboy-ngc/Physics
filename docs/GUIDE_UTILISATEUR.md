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
**information**. Le rapport indique les numéros de ligne à corriger — ce sont
les numéros de ligne de votre fichier, lignes vides comprises.

### Écriture des montants

Sont lus : `45000`, `45000.75`, `45 000,50`, `45,000.50`, `1.234.567,89`,
`1 200 €`, `1200 EUR`, et la notation comptable `(1 200)` qui vaut −1 200.

**Une cellule qui n'est pas un nombre est refusée**, jamais rabotée jusqu'à en
devenir un : `1E+05`, `50k`, `12 mois` ou `5O000` (la lettre O à la place du
zéro) sont comptés « non numériques » et signalés avec leur numéro de ligne,
plutôt que lus comme 105, 50, 12 et 5 000.

Reste ambiguë une écriture comme `45.000` : elle vaut 45 000 en France et 45,0
ailleurs. La lecture décimale est retenue **et l'ambiguïté est signalée** au
contrôle qualité — l'outil ne devine pas en silence.

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

### Couleurs

Cinq thèmes, dans **Paramètres → Apparence** : **Ardoise** (d'origine),
**Graphite** (neutre, le meilleur rendu à l'impression en noir et blanc),
**Forêt**, **Prune** et **Auroral** (bleu-vert lumineux sur nuit polaire,
l'accent le plus contrasté — pour un écran très éclairé).

Le thème colore la fenêtre **et** les documents produits. Trois teintes n'en
dépendent jamais : le rouge de « critique », l'orange d'« avertissement » et
le couple femmes/hommes du nuage et des pyramides — les changer serait un
contresens, pas une préférence.

## 5 bis. Composer sa propre page (« Ma page »)

L'onglet **Ma page** part vide et propose, a gauche, tous les indicateurs,
tableaux et graphiques que l'analyse produit. Un clic les ajoute a la page.

- **Deplacer** : attraper un bloc par son titre et le faire glisser. Un trait
  vertical montre ou il atterrira.
- **Redimensionner** : tirer le coin en bas a droite. La largeur se pose sur
  un palier — quart, tiers, moitie, pleine largeur — pour que les blocs
  restent alignes ; la hauteur est libre entre deux bornes.
- **Retirer** : la croix en haut a droite du bloc. « Tout retirer » vide la
  page.
- **Enregistrer la page** : la composition est retrouvee a la prochaine
  ouverture.

Ce qui est enregistre se reduit a la liste des blocs, a leur ordre et a leur
taille : aucun chiffre, aucune donnee de votre fichier n'est ecrit dans la
configuration. La largeur y est notee en colonnes et non en pixels — une page
composee sur un grand ecran s'ouvre droite sur un petit.

Les regles de confidentialite s'appliquent ici comme partout : un bloc dont
l'effectif est trop faible n'affiche rien.

## 6. Protection des données

- Les résultats sont masqués sous 5 salariés, signalés sous 10, les graphiques
  désactivés sous 10 (seuils modifiables).
- Les matricules sont remplacés par une référence anonyme dans les
  restitutions.

### Voir qui se cache derrière un point

Dans la fenêtre, le nuage de points **nomme le salarié survolé** (« DUPONT
Marie »), et la bannière de sélection le reprend. C'est le geste même de
l'analyse : un point à 30 % sous la médiane ne veut rien dire tant qu'on ne
sait pas de qui il s'agit.

Le réglage se trouve dans **Paramètres → Confidentialité** (« Afficher les noms
des salariés à l'écran »). Décoché, la fenêtre s'en tient à la référence
anonyme.

**Dans les deux cas, les documents produits, les exports et le journal
technique restent sans nom ni prénom.** Ce n'est pas une question de réglage :
l'identité n'entre jamais dans le résultat d'analyse — la fenêtre la
reconstruit depuis le fichier qu'elle a chargé, au moment de l'afficher. Rien
de ce qui circule ne peut donc en porter.
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
