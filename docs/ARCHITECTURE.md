# Architecture — Compensation Analytics Engine

Version du moteur : **1.0.0** (V1 / MVP).

## 1. Principe directeur

Le logiciel est un **moteur d'analyse paramétrable**, pas un fichier Excel figé.
Chaque étape du pipeline est un module découplé qui ne connaît que la structure
de données produite par l'étape précédente.

```
IMPORT ─▶ CONTRÔLE ─▶ NORMALISATION ─▶ PARAMÉTRAGE ─▶ MOTEUR DE CALCUL
      ─▶ ANALYSE ─▶ VISUALISATION ─▶ RESTITUTION ─▶ EXPORT
```

## 2. Décision structurante : zéro dépendance externe

Le moteur n'importe **que la bibliothèque standard Python**. En particulier :

| Besoin | Solution retenue | Solution écartée |
|---|---|---|
| Lecture XLSX/XLSM | `zipfile` + `xml.etree` (`io/tabular.py`) | openpyxl, pandas |
| Écriture XLSX | Génération OOXML directe (`io/xlsx_writer.py`) | xlsxwriter |
| Statistiques | `statistics_engine.py` | numpy, scipy |
| Graphiques | SVG généré côté moteur | matplotlib, plotly, Chart.js |
| Restitution HTML | HTML autoportant (rapport + slides paysage) | — |
| Restitution PDF | Generateur PDF ecrit dans `io/pdf_writer.py` | wkhtmltopdf, reportlab, WeasyPrint |
| Configuration | JSON (`config/*.json`) | YAML (dépendance), SQLite (binaire) |

Conséquences : aucune DLL tierce, aucun binaire à faire homologuer, aucune
chaîne d'approvisionnement logicielle à surveiller, packaging trivial.

## 3. Modules

```
compensation_analytics/
├── version.py              Version MAJOR.MINOR.PATCH portée par les restitutions
├── cli.py                  Pilotage (une IHM utiliserait les mêmes appels)
├── io/
│   ├── tabular.py          Lecture CSV / XLSX / XLSM → Table (brut)
│   └── xlsx_writer.py      Écriture XLSX multi-onglets
└── core/
    ├── errors.py           Erreurs métier (message utilisateur / détail technique)
    ├── config.py           Chargement + fusion des paramètres
    ├── mapping.py          Colonnes source → champs normalisés
    ├── normalize.py        Table → Population (Employee)
    ├── quality.py          Data Quality Check
    ├── statistics_engine.py Formules — source unique de vérité
    ├── metrics.py          Indicateurs métier + règles de confidentialité
    ├── segmentation.py     Filtres combinables, découpage par dimension
    ├── reporting.py        Restitution HTML + SVG
    ├── export.py           Export Excel / CSV
    ├── logging_setup.py    Log technique sans donnée personnelle
    ├── traceability.py     Manifeste de reproductibilité
    └── pipeline.py         Orchestration
```

**Règle de dépendance** : `io` ne connaît pas `core` ; `core.statistics_engine`
ne connaît rien ; `metrics` ne connaît que `statistics_engine`, `normalize` et
`config` ; `reporting` et `export` ne connaissent que le dictionnaire de
résultat. Aucune formule n'est dupliquée hors de `statistics_engine`.

## 4. Couche pivot

```
Fichier RH ─▶ Table (brut) ─▶ MappingResult ─▶ Population[Employee] ─▶ payload
```

`Employee` est le contrat interne. Changer de format d'import n'affecte que
`io/tabular.py` et `config/population_mapping.json` ; ajouter une analyse
n'affecte que `metrics.py`.

## 5. Sécurité et conformité IT

| Contrainte | Mise en œuvre |
|---|---|
| Aucune sortie réseau | Aucun `socket`, `urllib`, `requests` dans le code ; restitution HTML sans `http://`, `<script src>`, `<link>` ni `@import` (vérifié par test) |
| Aucun processus enfant | Aucun `subprocess`, `os.system`, Shell ou PowerShell |
| Aucun code dynamique | Aucun `eval`/`exec` ; les filtres sont des structures de données interprétées par comparaison |
| Aucun droit administrateur | Écriture limitée au dossier de sortie choisi par l'utilisateur ; aucune écriture registre |
| Fichiers temporaires | Le moteur n'en crée pas ; il écrit uniquement les livrables demandés |
| Données personnelles | Jamais dans les logs ni dans les messages d'erreur ; export individuel désactivé par défaut ; identifiants hachés SHA-256 |
| Dépendances | Zéro. `pip install` n'est jamais requis |

## 6. Confidentialité — petits effectifs

`privacy_parameters.json`, appliqué dans `metrics.py` (donc impossible à
contourner depuis un écran) :

| Paramètre | Défaut | Effet |
|---|---|---|
| `min_headcount_publish` | 5 | En deçà, les indicateurs sont masqués |
| `min_headcount_warning` | 10 | En deçà, avertissement d'interprétation |
| `min_headcount_chart` | 10 | En deçà, graphiques désactivés |
| `anonymise_identifiers` | true | Matricule remplacé par une empreinte SHA-256 tronquée |

## 7. Formulation des résultats

Une valeur hors bornes interquartiles est présentée comme
**« Situation atypique à analyser »**, jamais comme une anomalie RH : le
critère est statistique, la lecture est contextuelle (marché, métier,
historique, performance). Un test vérifie que la chaîne « anomalie RH »
n'apparaît pas dans la restitution.

L'écart-type reste calculé et exporté comme statistique technique, mais n'est
pas présenté en KPI de pilotage : les ratios de dispersion (Q3/Q1, P90/P10,
moyenne/médiane) sont les indicateurs mis en avant.

## 8. Percentiles

Méthode inclusive à interpolation linéaire (type 7), identique à
`PERCENTILE.INCLUSIVE` d'Excel et au défaut de numpy : un contrôle refait sous
Excel par l'équipe C&B donne exactement la même valeur. Les valeurs de
référence sont figées dans `tests/test_statistics.py`.

## 9. Traçabilité

Chaque analyse produit un manifeste JSON : moteur, version, date, nom et
empreinte SHA-256 du fichier source, effectif, filtres, intégralité des
paramètres. Il contient l'empreinte du fichier, jamais son contenu — donc
aucune donnée personnelle.

## 10. Performance

Mesures sur population fictive (`python3 tools/benchmark.py`), poste Linux
conteneurisé, secondes :

| Effectif | Import | Normalisation | Qualité | Calculs | Restitution | Total | HTML | RAM |
|---|---|---|---|---|---|---|---|---|
| 1 000 | 0,09 | 0,01 | 0,00 | 0,03 | 0,01 | **0,14** | 0,2 Mo | 24 Mo |
| 10 000 | 1,02 | 0,14 | 0,02 | 0,36 | 0,04 | **1,58** | 0,7 Mo | 51 Mo |
| 50 000 | 5,80 | 0,90 | 0,12 | 2,23 | 0,02 | **9,07** | 0,7 Mo | 165 Mo |
| 100 000 | 11,72 | 2,11 | 0,35 | 5,09 | 0,03 | **19,31** | 0,7 Mo | 310 Mo |

Comportement linéaire. **Seuil identifié** : au-delà de ~50 000 salariés,
l'import XLSX (parsing XML) domine et l'analyse dépasse les 10 secondes ;
au-delà de ~200 000, la population entièrement en mémoire deviendrait
contraignante sur un poste à 8 Go.

Un premier plafond a déjà été traité : sans garde-fou, le nuage de points
produisait 100 000 cercles SVG et un HTML de 12,8 Mo (navigateur inutilisable).
`chart_parameters.scatter_max_points` (5 000 par défaut) applique un
échantillonnage systématique à pas constant — déterministe, donc reproductible
et traçable — et l'échantillonnage est signalé dans la restitution.

Leviers si le seuil doit être repoussé (V3) : import CSV plutôt que XLSX
(≈10× plus rapide), lecture en flux sans matérialiser le tableau brut,
pré-agrégation par segment.

## 10 bis. Empreinte des livrables

L'export Excel et le manifeste restent de taille modeste quel que soit
l'effectif : ils contiennent des agrégats, pas la population — sauf activation
explicite de `export_parameters.include_individual_data`.

## 9 bis. Restitutions paysage

Trois sorties construites sur les memes donnees :

| Sortie | Contenu | Formats |
|---|---|---|
| `rapport` | Document detaille, defilant | HTML |
| `synthese` | Une page paysage : indicateurs, niveaux de remuneration, structure de la population, nuage | HTML + PDF |
| `slides` | Un jeu de pages paysage, une idee par page | HTML + PDF |

La fiche standard est organisee en un bandeau de six indicateurs puis trois
colonnes : niveaux de remuneration (percentiles), structure de la population
(tranches d'age et d'anciennete), et nuage anciennete x remuneration. Le nuage
occupe une colonne plutot qu'une bande horizontale : il a besoin de hauteur
pour que la dispersion verticale se lise.

La page ne cherche pas a remplir sa hauteur. Une bande de parts remarquables
l'a fermee un temps : elle repetait le tableau de structure place juste
au-dessus et se lisait comme un remplissage. Ces parts — moins de 30 ans,
30 a 49 ans, 50 ans et plus, anciennete inferieure a 2 ans, superieure a
10 ans — sont desormais portees par l'onglet Population de l'export Excel, ou
la densite ne coute rien. Elles restent calculees sur les valeurs reelles et
non sur les libelles de tranches : elles ne deviennent pas fausses si
l'utilisateur reparametre ses tranches.

Le taux de donnees valorisees n'apparait qu'en sous-titre, et seulement s'il
est inferieur a 100 % : une couverture partielle change la lecture de tous les
montants, une couverture complete n'apprend rien.

Les blocs se declarent en trois largeurs — `full`, `half`, `third` — et les
tableaux comme les bandeaux d'indicateurs en version resserree (`compact`),
ce qui permet de densifier une page sans reduire le texte sous le seuil de
lisibilite en projection.

La fiche standard ne porte pas les ratios de dispersion (Q3/Q1, P90/P10,
coefficient de variation) : ils demandent une lecture experte et trouvent leur
place dans le jeu de slides complet et dans l'export Excel. Elle privilegie le
nuage anciennete x remuneration, qui se lit sans grille de lecture prealable.
Si l'effectif est sous le seuil qui desactive le nuage, la page se rabat sur
l'histogramme, puis sur un message explicite.

Le decoupage (`core/slides.py`) produit une liste de `Slide` composees de
`Block` — un descriptif de contenu independant du format. Le rendu HTML et le
rendu PDF consomment la meme liste : les deux formats ne peuvent pas diverger.

### Adaptation a l'ecran

La page garde une **geometrie fixe** de 1280 x 720 : c'est ce qui garantit que
l'ecran, l'impression et le PDF montrent exactement la meme chose. Pour tenir
sur un ecran plus etroit, elle est **mise a l'echelle** (`transform: scale`)
plutot que reagencee — un reagencement ferait diverger le rendu ecran du rendu
papier.

Le facteur `--slide-scale` est calcule au chargement et au redimensionnement,
plafonne a 1 (on reduit pour tenir, on n'agrandit jamais). A l'impression il
est remis a 1 pour que le papier ne soit pas affecte. Sans JavaScript, la
valeur de repli est 1 : la page s'affiche a sa taille reelle.

Mesure du debordement horizontal (largeur de contenu / largeur de fenetre) :

| Fenetre | Avant | Apres |
|---|---|---|
| 768 px | 1017 / 753 — deborde | 753 / 753 — echelle 0,55 |
| 1024 px | 1145 / 1009 — deborde | 1009 / 1009 — echelle 0,75 |
| 1440 px | ok | ok — echelle 1 |

Le **rapport detaille**, lui, est fluide : grille de KPI en `auto-fill`,
tableaux larges dans un conteneur a defilement propre, SVG en `max-width:100%`.
Verifie sans debordement jusqu'a 390 px de large.

### Le PDF est genere, pas imprime

`io/pdf_writer.py` ecrit le PDF octet par octet : objets numerotes, table de
references croisees, flux de contenu compresses. Aucun navigateur a piloter,
aucun moteur de rendu, aucune dependance — le meme parti pris que pour le
XLSX.

Ce qui rend l'exercice tenable :

* seules les **14 polices de base** du format PDF sont utilisees (Helvetica),
  donc rien a embarquer ni a licencier, et aucune table `/FontFile` ;
* les **largeurs de glyphes** Helvetica sont tabulees, ce qui permet de
  centrer, aligner a droite et tronquer proprement ;
* le dessin se limite aux primitives dont les graphiques ont besoin —
  rectangles, lignes, cercles de Bezier, texte — exactement ce que produit
  deja le SVG.

Les accents passent sans repli (`WinAnsiEncoding` les couvre) ; seuls les
caracteres typographiques hors jeu (apostrophe courbe, tiret cadratin) sont
remplaces par un equivalent imprimable.

Format : **A4 paysage** (841,89 x 595,28 points), le plus sur a l'impression
comme a la projection.

### Verification

Un PDF invalide ne s'ouvre pas du tout : la structure est donc testee et non
supposee. `tests/test_slides.py` verifie que chaque offset de la table xref
pointe sur un objet reel, que le nombre de pages correspond au decoupage, que
le MediaBox est bien paysage, que les flux se decompressent et contiennent le
texte attendu, et qu'aucune donnee personnelle n'y figure.

## 10 ter. Dimensions declaratives

Les dimensions d'analyse (segmentation, filtres, coloration du nuage, colonnes
de l'export individuel) sont declarees dans `population_mapping.json` :

```json
"dimensions": [
  {"field": "business_unit", "label": "BU"},
  {"field": "grade",         "label": "Grade"}
]
```

Ajouter une notion metier (equipe, manager, direction) demande deux lignes de
configuration — un alias dans `fields`, une entree dans `dimensions` — et rien
d'autre. Les champs absents du modele `Employee` sont ranges dans
`Employee.extra` et restent filtrables, segmentables et exportables au meme
titre que les champs natifs.

C'est la condition posee par le chapitre 20 du cahier des charges : les
analyses a venir se branchent sans reecrire le coeur.

## 10 quater. Anomalies a echec silencieux

Un audit du code a recherche les cas ou le moteur renvoyait un resultat
plausible mais faux, plutot qu'une erreur. Sept ont ete corriges et sont
verrouilles par `tests/test_anomalies.py` :

| Anomalie | Symptome | Correction |
|---|---|---|
| Champ de filtre inconnu | `gade=G5` renvoyait 0 salarie sans message | Erreur listant les champs disponibles |
| Egalite sur champ numerique | `base_salary=50000` ne trouvait pas 50000.0 | Comparaison sur la valeur, pas sur l'ecriture |
| Percentiles configures sans P25/P75 | Q3/Q1 et P90/P10 disparaissaient sans explication | Percentiles de dispersion toujours calcules, publication restant configurable |
| `analysis_field` sur une colonne texte | `TypeError` brut | Erreur metier nommant les champs numeriques |
| Separateur ambigu (`45.000`) | Valeur lue 45,0 en silence | Signale au controle qualite |
| `inf` / notation scientifique en export | Classeur qu'Excel refuse d'ouvrir | Ecriture en texte ou en notation fixe |
| Export individuel a colonnes figees | Une dimension declaree en disparaissait | Colonnes derivees des dimensions |

Le principe retenu : **face a une incoherence, echouer visiblement plutot que
produire un resultat plausible**. Un chiffre faux dans une analyse de
remuneration coute plus cher qu'un message d'erreur.

## 11. Feuille de route

| Version | Périmètre | État |
|---|---|---|
| V0 — PoC | Import, contrôle, KPI, tableau | ✅ |
| V1 — MVP | Paramétrage, filtres, percentiles, ratios, nuage de points, export Excel | ✅ |
| V2 — Enterprise | Logs, versioning, tests, traçabilité, packaging, PDF | 🟡 partiel (logs, versioning, tests, traçabilité et **PDF natif** faits ; packaging à faire) |
| V3 — Optimisation | Performance, IHM, segmentation avancée, automatisation | ⬜ |

### Extensions prévues sans réécriture du cœur

Chacune s'ajoute comme fonction de `metrics.py` + section de `reporting.py` +
paramètres dédiés, sans toucher au pipeline : égalité salariale, promotions,
augmentations, variable, compa-ratio, positionnement en grille, budget
salarial, évolution N/N-1.

## 10 quinquies. Statistiques techniques non publiées

Deux statistiques sont calculées et restent accessibles au moteur, sans
figurer dans les restitutions :

* l'**ecart-type**, disponible dans l'export Excel mais jamais presente en
  indicateur de pilotage — ce sont les ratios de dispersion qui le sont ;
* le **R2** de la droite de tendance du nuage, retire des documents. Il
  demandait une explication pour etre lu, et sans cette explication il
  n'apportait rien. La pente chiffree est partie avec lui : annoncee seule,
  sur une population melangeant tous les grades, elle affirmerait un lien que
  rien n'etaye. La droite reste tracee comme repere visuel.

`statistics_engine.linear_regression` continue de retourner les deux, ce qui
laisse la porte ouverte a un usage ulterieur — par exemple un R2 par segment,
la ou la lecture a un sens.

## 11 bis. Libellés et interface

Les libellés affichés — titres de section, en-têtes de tableaux, messages du
contrôle qualité, noms d'onglets Excel — sont accentués. Le PDF les rend sans
repli : `WinAnsiEncoding` couvre le latin-1, et les largeurs de glyphes se
déduisent de la lettre de base, ce qui garde le centrage et la troncature
justes. Seuls les caractères hors jeu (apostrophe courbe, tiret cadratin) sont
remplacés par un équivalent imprimable.

En revanche, **l'interface reste en ASCII** : noms d'options
(`--date-reference`), sous-commandes (`controle`), valeurs acceptées
(`synthese`), noms de fichiers produits et clés du manifeste JSON. Une option
accentuée obligerait à taper un accent dans un terminal, casserait les scripts
existants et dépendrait de la configuration clavier du poste.
`tests/test_security.py` vérifie cette séparation.

## 12. Packaging (V2, à faire)

Cible : dossier autonome, sans installation ni droits administrateur, sans
Python sur le poste. Le choix zéro-dépendance rend l'exercice simple :

1. `python -m zipapp` → un `.pyz` unique (nécessite encore un interpréteur) ;
2. distribution Windows embarquable (`python-x.y.z-embed-amd64`) + le `.pyz`,
   lancé par un raccourci — aucune installation, aucune écriture registre ;
3. PyInstaller `--onedir` si un exécutable unique est exigé — à évaluer avec
   l'IT, un binaire non signé étant souvent plus suspect qu'un dossier de
   fichiers lisibles.

L'option 2 est recommandée : rien à compiler, contenu auditable par l'IT.

## 13. Interface graphique

`compensation_analytics/ui/` — tkinter, livre avec Python : aucune
dependance, aucun telechargement, aucun droit administrateur.

    app.py        fenetre unique, parcours en quatre etapes
    charts.py     nuage et histogramme dessines sur un canevas
    dashboard.py  catalogue et grille de la page composee par l'utilisateur

**Regle de dependance** : l'interface importe le moteur, jamais l'inverse.
Un test le verifie par analyse syntaxique sur `core/` et `io/`. C'est ce qui
garantit que le moteur tourne en ligne de commande sur une installation de
Python depourvue de tkinter, et qu'il reste automatisable.

Aucune regle de calcul n'est dupliquee : chaque action appelle
`pipeline.run_analysis`, `metrics.*` ou `slides.*`, exactement comme la ligne
de commande. Changer la dimension de couleur du nuage refait passer le
regroupement par `metrics.scatter_dataset` plutot que de recolorer dans
l'interface : l'ecran et le document ne peuvent pas diverger.

### Ce que l'interface apporte, qu'un document ne peut pas

Le nuage est explorable : survol pour identifier un salarie par sa reference
anonyme, clic pour le selectionner, molette pour zoomer autour du curseur,
glisser pour se deplacer, clic sur la legende pour masquer une population.
Le compteur de points affiches rappelle en permanence ce qui est visible,
pour qu'un zoom ne se confonde jamais avec un filtre.

Les filtres sont des listes deroulantes alimentees par le fichier charge :
l'utilisateur choisit parmi ce qui existe, sans syntaxe a taper et sans
pouvoir inventer une valeur absente.

L'analyse tourne dans un fil separe, avec une barre de progression : sur
100 000 salaries elle prend une quinzaine de secondes, et une fenetre figee
passerait pour un plantage.

### « Ma page » — composition par l'utilisateur

Les autres onglets repondent chacun a une question que nous avons choisie.
Celui-la ne choisit rien : `ui/dashboard.py` expose le catalogue de tout ce
que l'analyse produit — indicateurs, tableaux, graphiques — et laisse
composer la page dont on a besoin.

Le catalogue vit dans l'interface et non dans le moteur : un « bloc » est
une facon d'afficher, pas une facon de calculer. Chaque bloc lit le meme
resultat que les autres onglets ; aucune valeur n'y est recalculee.

**Disposition en douziemes, jamais en pixels.** Les blocs sont poses a la
souris, mais ce qui est retenu d'un deplacement est un rang, et ce qui est
retenu d'un redimensionnement est une largeur en colonnes (quart, tiers,
moitie, pleine largeur) plus une hauteur bornee. `flow()` recalcule les
pixels a chaque mise en page. Une position absolue serait juste sur l'ecran
ou elle a ete posee et fausse partout ailleurs : une page composee sur un
grand ecran doit s'ouvrir droite sur un petit.

**Pendant un deplacement, seul un fantome suit le curseur**, double d'un
trait d'insertion qui montre ou le bloc atterrira. Deplacer le bloc lui-meme
ferait repeindre son contenu a chaque pixel parcouru : le nuage de points
met 129 ms a se tracer.

**Ce qui part en configuration** (`dashboard_parameters.blocks`) se reduit a
des identifiants, un ordre et des tailles — jamais un chiffre, jamais une
donnee RH. Un identifiant inconnu, dans une configuration ecrite a la main
ou heritee d'une version anterieure, est ignore avec une trace au journal
technique : la page s'ouvre amputee plutot que pas du tout. Une hauteur ou
une largeur hors bornes est ramenee a sa valeur par defaut.

Les regles de confidentialite ne sont pas rejouees ici : un bloc affiche ce
que le moteur a marque publiable, et se tait sinon — la dispersion par
segment exige le drapeau `chartable`, faute de quoi elle ne trace rien.

### Tests

Les tests d'interface qui exigent un affichage sont ignores automatiquement
lorsqu'il n'y en a pas — le moteur reste testable sur un serveur sans ecran.
Le developpement s'est fait sur un affichage virtuel (Xvfb), chaque ecran
etant capture et relu : c'est ainsi qu'a ete vu que la liste des filtres
poussait le bouton "Analyser" hors du cadre.
