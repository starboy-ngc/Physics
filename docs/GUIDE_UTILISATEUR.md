# Guide utilisateur — HR Insight

Logiciel **local et hors ligne** : aucune donnée ne quitte votre poste.
Vous pouvez couper Internet avant de l'utiliser.

## 0. L'écran d'accueil

À l'ouverture, **HR Insight** affiche son aurore, son nom et l'étape en
cours : lecture des paramètres, thème, colonne de gauche, pages et
graphiques. Ces étapes sont réelles — construire la fenêtre demande deux
dixièmes de seconde ici, davantage sur un poste chargé.

L'écran reste ensuite affiché **trois secondes**, pour qu'on ait le temps de
le lire : cette attente-là est délibérée. Elle se règle dans
`config/theme_parameters.json` :

```json
{ "theme": "ardoise", "splash_seconds": 3.0 }
```

À **0**, pas d'écran d'accueil du tout : la fenêtre s'ouvre directement. Et
un clic sur l'écran le passe sans attendre.

Le logo n'est pas un fichier image : il est **calculé** à chaque ouverture —
un rideau : un bord ondulant, et onze rais qui s'en élèvent et se dissipent, du vert au violet — puis encodé en PNG
par le même module qui dessine les points du nuage. Rien d'opaque dans
l'archive, et rien de tiré au hasard : le même symbole à chaque fois, et le
même dessin exactement à toutes les tailles, de l'icône à l'affiche.

Pour en tirer une image — une présentation, un intranet, une icône :

```
python3 tools/render_logo.py --largeur 1024 --sortie logo.png
python3 tools/render_logo.py --largeur 256 --fond "#141f2a"
```

Sans `--fond`, le fond reste transparent.

Une lueur parcourt le symbole pendant le chargement. Elle n'en change jamais
la forme : un logo qui se déforme n'est plus un logo.

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

### Pendant l'analyse

La barre sous « Analyser » nomme l'étape en cours et la part faite. Sur un
gros fichier, **la lecture pèse la moitié du temps** : c'est normal que la
barre y passe la moitié de son parcours. Les étapes suivantes —
normalisation, contrôle qualité, indicateurs, écarts femmes / hommes,
segments — sont bien plus rapides.

La barre ne recule jamais et ne s'arrête pas : entre deux annonces du moteur
elle continue d'avancer, de plus en plus lentement, jusqu'à la suivante.

Ordre de grandeur, sur un fichier Excel de cent mille lignes : une vingtaine
de secondes au total, dont une dizaine pour la seule lecture. Neuf cents
salariés s'analysent en deux dixièmes de seconde.

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

### Le dossier de vérification : le fichier importé et tous les calculs

Une médiane ne se déduit d'aucun autre chiffre : la vérifier demande les
valeurs. Et vérifier une valeur demande de pouvoir remonter jusqu'à la ligne
du fichier dont elle sort.

Dans **Paramètres → Export**, deux cases :

1. **Exporter les données individuelles dans le classeur.**
2. **Joindre le fichier importé et les onglets de contrôle** (elle suppose la
   première, et la coche automatiquement).

Le classeur gagne alors cinq onglets, dans l'ordre de la chaîne :

| Onglet | Ce qu'il contient |
|---|---|
| **Fichier importé** | le fichier tel qu'il a été lu, ligne pour ligne et colonne pour colonne — la ligne 7 de l'onglet est la ligne 7 du fichier |
| **Colonnes lues** | ce que le mapping a fait de chaque colonne, et lesquelles il a ignorées |
| **Données individuelles** | les salariés retenus, avec leur **ligne source**, le **sexe retenu** par la classification, les dates comprises à la lecture, et l'âge comme l'ancienneté **écrits en formules** |
| **Contrôle** | chaque indicateur d'ensemble refait par le tableur : effectif, âge, ancienneté, tranches, parts remarquables, tous les percentiles, écart-type, dispersion, bornes atypiques, chaque classe de l'histogramme |
| **Contrôle segments** | chaque ligne de chaque segment : effectif, moyenne, médiane, P10, Q1, Q3, P90, âge et ancienneté médians |
| **Contrôle Pay Transparency** | chaque catégorie : effectifs, moyennes, médianes, écarts et rattrapage |

Chaque ligne de contrôle a quatre colonnes : ce que **l'outil** a calculé, ce
que le **tableur** retrouve, l'**écart** entre les deux, et la **formule** en
clair.

```
Indicateur   Calculé par l'outil   Recalculé par le tableur   Écart   Formule
Médiane      40 642                40 642                     0       MEDIAN(...)
Q1 (P25)     31 386,25             31 386,25                  0       PERCENTILE(...;0,25)
```

**La colonne « Écart » doit valoir zéro partout.** C'est la vérification, et
elle se fait d'un coup d'œil — sans lire une ligne de code.

Un onglet **Formules**, lui, est toujours présent, données individuelles ou
non : il dit en français ce que chaque indicateur calcule, avec son écriture
dans un tableur et l'endroit où le vérifier. Les deux se complètent — une
formule juste appliquée à la mauvaise définition reste une erreur.

### Ce que le contrôle ne fait pas

- **Il ne franchit jamais un seuil de confidentialité.** Un segment masqué
  garde son effectif vérifiable et rien d'autre : recalculer sa médiane
  reviendrait à la publier.
- **Le découpage en quartiles n'est pas refait en formule.** Il se fait par
  rang, à effectifs égaux, et les ex æquo y sont départagés par l'ordre de
  lecture : aucune formule ne reproduit cet arbitrage. La règle est écrite
  dans l'onglet « Formules » plutôt que faussement recalculée.
- **Au-delà de 20 000 salariés** (`export_parameters.control_max_rows`), le
  contrôle par segment n'est plus posé : chaque formule y relit toute la
  population, et le classeur mettrait plusieurs minutes à s'ouvrir. Le
  contrôle d'ensemble, lui, reste posé.
- **Au-delà de 50 000 lignes** (`export_parameters.source_max_rows`), le
  fichier importé n'est plus recopié.

**Ces onglets portent de la donnée nominative** : le fichier importé porte les
noms, et les données individuelles la référence de chaque salarié. C'est
pourquoi les deux cases sont décochées au départ et le restent tant qu'on ne
les coche pas.

## 5 sexies. Plusieurs périodes dans un même fichier

Déclarez une colonne **Période** (« Periode », « Date d'effet », « Mois »,
« Année »… — les intitulés acceptés sont dans `population_mapping.json`) et
le fichier peut porter plusieurs années : une ligne par salarié et par
période.

Ce qui change :

- **L'identité devient (matricule + période).** Un matricule répété sur deux
  années n'est plus un doublon — c'est l'intention du fichier. Répété **deux
  fois sur la même période**, c'en est toujours un, et le contrôle qualité le
  signale comme avant.
- **Une seule période est analysée à la fois**, la plus récente par défaut.
  Mélangées, les rémunérations de trois années ne veulent rien dire : sur un
  fichier de 100 salariés sur 3 ans, l'effectif afficherait 300 et la médiane
  tomberait entre deux années sans correspondre à aucune.
- Un bloc **Période** apparaît dans la colonne de gauche, avant les filtres.
  Il reste caché si le fichier n'en porte qu'une.
- La période analysée figure dans la barre d'état, et **dans le manifeste** :
  refaire l'analyse à l'identique exige de savoir laquelle a servi.

En ligne de commande : `--periode 2025`. Une période absente du fichier est
refusée avec la liste de celles qui existent — une faute de frappe rendrait
sinon l'analyse de la dernière période en la faisant passer pour celle qu'on
visait.

## 5 septies. Analyser une équipe

Un fichier de paie porte rarement l'organigramme. Il porte en revanche, dans
la plupart des exports, le **matricule du responsable** de chaque salarié —
et c'est tout ce qu'il faut : l'arbre se déduit du rapprochement entre ce
matricule et celui des autres lignes.

Déclarez une colonne **Manager** (« Responsable », « N+1 », « Matricule
manager »… — les intitulés acceptés sont dans `population_mapping.json`).
Elle n'est pas obligatoire : sans elle, l'outil se comporte exactement comme
avant, et le réglage reste caché.

Deux populations en découlent :

- **l'équipe directe** : celle qu'un responsable voit tous les jours ;
- **l'équipe totale** : tous les niveaux en dessous, jusqu'au dernier. C'est
  celle dont il répond, et elle ne se lit sur aucune colonne. C'est le choix
  par défaut.

Le responsable est compté dans son équipe : une équipe sans son manager
n'est pas l'objet dont on parle quand on demande « la rémunération de
l'équipe de X ».

Ce qui apparaît :

- Un bloc **Équipe** dans la colonne de gauche, entre la période et les
  filtres — l'équipe désigne la population, les filtres ne font que la
  restreindre. La liste se lit du sommet vers le bas, chaque niveau décalé.
- Sous la liste, **les deux effectifs** de l'équipe choisie : une équipe
  directe de 4 personnes et une équipe totale de 40 ne donnent pas la même
  page.
- L'équipe analysée figure dans la barre d'état et **dans le manifeste**.

En ligne de commande : `--equipe M0042`, et `--equipe-directe` pour s'arrêter
au premier niveau. Un matricule absent du fichier est refusé : sans refus,
l'analyse porterait sur une population vide sans que rien ne le dise.

**L'arbre se construit sur tout le fichier de la période, jamais sur la
population déjà filtrée.** Un filtre « France » couperait sinon la branche
d'un responsable dont une partie de l'équipe est ailleurs, et l'équipe totale
ne serait plus totale. Les filtres s'appliquent ensuite, sur les membres
ainsi trouvés.

### Trois ans de données, la même équipe

La période et l'équipe se combinent : la même branche à deux dates, seules
les rémunérations changent. C'est ainsi qu'on suit l'évolution d'une équipe
année par année.

### Quand le fichier est incohérent

Un export mal tenu ne fait jamais lever, mais il le dit, sous la liste :

- **responsable introuvable** : le matricule ne correspond à personne. Le
  subordonné devient une racine — mieux vaut un arbre à plusieurs racines
  qu'un salarié perdu.
- **salarié dans une boucle** : « A encadre B qui encadre A ». Les membres du
  cycle deviennent des racines. Sans cette rupture, toute descente dans
  l'arbre tournerait sans fin.
- **matricule en double** : l'arbre ne peut pas trancher, la première ligne
  fait foi.

Ces anomalies sont annoncées **en nombre et jamais en matricules** : la
colonne désigne des personnes.

### Ce que l'équipe ne change pas

Les seuils de confidentialité ne cèdent pas devant une équipe : sous 5
salariés, les résultats sont masqués, équipe ou pas. Et le résultat d'analyse
ne porte que le matricule — le nom du responsable est reconstruit à l'écran
depuis le fichier chargé, et ne peut donc entrer dans aucun document produit
ni dans aucun journal.

## 6. Protection des données

- Les résultats sont masqués sous 5 salariés, signalés sous 10, les graphiques
  désactivés sous 10 (seuils modifiables).
- Les matricules sont remplacés par une référence anonyme dans les
  restitutions.

### Ce que vaut la référence anonyme

Une référence est le condensé du matricule et d'un **sel**. Le sel décide de
tout : un matricule vit dans un espace minuscule — « E00001 » à « E99999 » —,
et si le sel est connu, retrouver le matricule derrière une référence publiée
demande quelques milliers d'essais, soit un centième de seconde. Le rapport
circule, lui.

Par défaut, `anonymisation_salt` est vide : **un sel est tiré au hasard à
chaque analyse.** Les références ne valent alors que dans les documents d'une
même exécution, et rien ne les relie à un matricule — pas même pour vous.

Renseignez `privacy_parameters.anonymisation_salt` avec une phrase de votre
choix si vous voulez **suivre une situation d'une période à la suivante** : les
références deviennent stables d'une analyse à l'autre sur ce poste. Seul celui
qui détient ce fichier de paramètres peut alors les rapprocher d'un matricule.

**Ne communiquez pas ce fichier avec les documents produits.** Le manifeste
recopie toute la configuration — c'est ce qui permet de refaire une analyse à
l'identique — mais le sel en est retiré et remplacé par « (non publié) ».

### Voir qui se cache derrière un point

Dans la fenêtre, le nuage de points **nomme le salarié survolé** (« DUPONT
Marie »), et la bannière de sélection le reprend. C'est le geste même de
l'analyse : un point à 30 % sous la médiane ne veut rien dire tant qu'on ne
sait pas de qui il s'agit.

Le réglage se trouve dans **Paramètres → Confidentialité** (« Afficher les noms
des salariés à l'écran »). Décoché, la fenêtre s'en tient à la référence
anonyme.

**Dans les deux cas, les documents produits (HTML, PDF, synthèse) et le
journal technique restent sans nom ni prénom.** Ce n'est pas une question de
réglage : l'identité n'entre jamais dans le résultat d'analyse — la fenêtre la
reconstruit depuis le fichier qu'elle a chargé, au moment de l'afficher. Rien
de ce qui circule ne peut donc en porter.

**Une seule exception, et elle se coche à la main** : l'onglet « Fichier
importé » du classeur recopie votre fichier tel quel, noms compris. Il
n'apparaît que si vous cochez « Joindre le fichier importé et les onglets de
contrôle » (Paramètres → Export), et les onglets de contrôle ne peuvent pas
exister sans lui — on ne vérifie pas un calcul sans ses valeurs.
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
