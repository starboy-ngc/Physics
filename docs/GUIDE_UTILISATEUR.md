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

## 5 ter. Lire l'onglet Pay Transparency

La directive 2023/970 demande l'écart de rémunération **par catégorie de
travailleurs accomplissant un travail de même valeur**. Le poste est cette
catégorie : l'onglet s'organise donc autour du couple **poste × sexe**.

### Trois chiffres, pas un

| | ce qu'il dit |
|---|---|
| **Écart global** | (moyenne hommes − moyenne femmes) / moyenne hommes. C'est le chiffre publiable. |
| **À poste comparable** | La moyenne des écarts de chaque poste, pondérée par leur effectif. C'est l'écart « à travail égal ». |
| **Effet de structure** | Le reste. Ce que le poste occupé explique de l'écart global. |

Un écart global faible peut cacher un écart à poste comparable élevé : il
suffit que les femmes soient plus nombreuses sur les postes les mieux
rémunérés. Les deux appellent des réponses opposées — une revalorisation
individuelle dans un cas, une politique de mobilité dans l'autre.

L'écart à poste comparable n'est calculé que sur les postes où **les deux
sexes** atteignent le seuil de publication ; le pourcentage d'effectif
couvert est indiqué.

### La page : une liste, une fiche

À gauche, **les postes**, classés par ce qui est en jeu. À droite, **la fiche
du poste retenu** : les deux sexes comparés variable par variable.

| | Femmes | Hommes | Écart |
|---|---|---|---|
| Salaire de base | 64 985 EUR | 80 898 EUR | +19,7 % |
| Part variable | 11 137 EUR | 15 188 EUR | +26,7 % |
| Rémunération totale | 76 122 EUR | 96 086 EUR | +20,8 % |
| Ancienneté | 7 ans | 9 ans | −1,8 an |
| Âge | 40 ans | 43 ans | −2,8 ans |
| Temps de travail | 0,93 | 0,99 | −0,06 |

Un écart de rémunération ne se lit pas seul : +19,7 % sur un poste où les
hommes comptent deux ans d'ancienneté de plus n'appelle pas la même réponse
que le même écart à ancienneté égale. Le premier interroge la grille
d'ancienneté, le second la rémunération elle-même.

**Sur les montants**, l'écart suit la formule de la directive. **Sur les
autres variables**, c'est une différence dans l'unité de la variable — un
pourcentage s'y lirait comme un écart de rémunération.

Les variables comparées sont **déclarées** dans
`config/pay_equity_parameters.json` (`profile_fields`) : une prime propre à
votre entreprise s'ajoute à la liste sans toucher au logiciel.

Rien n'est affiché si l'un des deux sexes est sous le seuil de publication :
une médiane calculée sur trois personnes les désigne.

### Le rattrapage

Ce que coûterait l'alignement du sexe le moins rémunéré sur l'autre, poste
par poste. C'est la question qui suit l'écart : un écart de 20 % sur quatre
personnes ne pèse pas ce que pèse 6 % sur cent vingt. Le tableau est trié
par cet enjeu par défaut — **Trier par** permet de passer à l'écart, à
l'effectif ou au nom.

### Changer d'axe, ou en croiser deux

**Comparer par** remplace le poste par le grade, l'établissement, le pays…
La même question, lue autrement.

**Croiser avec** ajoute un second axe : « Poste + Grade » traite « Comptable
senior · G5 » et « Comptable senior · G7 » comme deux catégories distinctes.
Un comptable senior au G5 et un comptable senior au G7 ne font pas le même
travail, et les confondre dilue l'écart que l'on cherche.

Croiser découpe plus fin, donc masque davantage : la couverture affichée dans
la note dit sur quelle part de l'effectif l'écart à catégorie comparable est
encore calculable. Un salarié dont l'un des deux axes n'est pas renseigné
n'entre dans aucune catégorie croisée.

Tout le bloc — les trois chiffres compris — se recalcule sur l'axe choisi.

## 5 quater. Dispersion : distinguer femmes et hommes

Dans **Graphique → Dispersion**, la case **Distinguer femmes / hommes** trace
deux boîtes par segment au lieu d'une : les femmes en rouge au-dessus, les
hommes en bleu au-dessous.

Deux médianes proches peuvent recouvrir deux distributions très différentes,
et un écart de médiane nul n'exclut pas que les femmes soient absentes du
haut de la fourchette.

Chaque demi-boîte a son propre droit au tracé : un segment de cinquante
personnes dont quatre femmes ne donne pas le droit de dessiner les
percentiles de ces quatre-là — cette moitié-là n'est simplement pas tracée.

## 5 quinquies. Vérifier les calculs dans le classeur Excel

Le classeur ne se contente pas d'afficher des résultats : **les indicateurs
dérivés portent leur formule**. Cliquez sur la cellule « Q3 − Q1 », vous lisez
`=B11-B9` — les deux cellules d'où le chiffre sort.

Sont écrits en formules :

| Onglet | Ce qui se recalcule |
|---|---|
| Rémunération | Q3 − Q1, Q3/Q1, P90/P10, Moyenne/Médiane, coefficient de variation |
| Population | la part de chaque tranche, rapportée à l'effectif total |
| Seg … | P90/P10, sur les deux colonnes de la même ligne |
| Pay Transparency | écart moyen, écart médian et rattrapage de chaque catégorie, et leur total |

Chaque cellule porte **aussi** sa valeur calculée : Excel la recalcule à
l'ouverture, mais un lecteur qui ne recalcule pas affiche le bon chiffre
quand même.

### Vérifier les indicateurs de base

Une médiane ne se déduit d'aucun autre chiffre : la vérifier demande les
valeurs. Activez `export_parameters.include_individual_data` et le classeur
gagne un onglet **Contrôle** qui pose côte à côte ce que l'outil a calculé et
ce que le tableur trouve sur la colonne des rémunérations :

```
Indicateur   Calculé par l'outil   Recalculé par le tableur   Formule
Médiane      40 642                40 642                     MEDIAN(...)
Q1 (P25)     31 386,25             31 386,25                  PERCENTILE(...;0,25)
```

Les percentiles suivent la méthode inclusive (type 7), identique à
`PERCENTILE` d'Excel : **les deux colonnes doivent coïncider à l'affichage
près**. Cet onglet n'apparaît qu'avec les données individuelles, car il ne
peut pas exister sans elles.

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
