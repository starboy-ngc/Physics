# Architecture : HR Analytics

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
| Restitution HTML | HTML autoportant (rapport + slides paysage) | - |
| Restitution PDF | Generateur PDF ecrit dans `io/pdf_writer.py` | wkhtmltopdf, reportlab, WeasyPrint |
| Configuration | JSON (`config/*.json`) | YAML (dépendance), SQLite (binaire) |

Conséquences : aucune DLL tierce, aucun binaire à faire homologuer, aucune
chaîne d'approvisionnement logicielle à surveiller, packaging trivial.

## 3. Modules

```
hr_analytics/
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
    ├── statistics_engine.py Formules, source unique de vérité
    ├── metrics.py          Indicateurs métier + règles de confidentialité
    ├── segmentation.py     Filtres combinables, découpage par dimension
    ├── hierarchy.py        Arbre déduit de la colonne manager (équipes)
    ├── org.py              Organigramme d'une équipe : structure + montants
    ├── reporting.py        Restitution HTML + SVG
    ├── export.py           Export Excel / CSV
    ├── formulas.py         Écriture tableur des calculs (onglets de contrôle)
    ├── logging_setup.py    Log technique sans donnée personnelle
    ├── traceability.py     Manifeste de reproductibilité
    └── pipeline.py         Orchestration
```

`hierarchy` ne calcule aucune rémunération : il rend des ensembles de
salariés, que le reste du moteur analyse comme n'importe quelle population.
L'arbre se construit sur tout le fichier de la période retenue et non sur la
population déjà filtrée, sans quoi un filtre amputerait la branche d'un
responsable ; et il est lu par itération, jamais par récursion : une chaîne
hiérarchique de mille niveaux dépasserait la pile. Un fichier incohérent
(cycle, manager absent, matricule en double) ne fait pas lever : il rend un
arbre amputé et le dit.

`org` fait ce que `hierarchy` s'interdit : rapprocher la structure et la
rémunération. Il rend trois lectures : l'équipe par poste (effectif,
minimum, médiane, moyenne, maximum, dans l'ordre de la hiérarchie), la liste
nominative avec le rang de rémunération dans l'équipe, et les cases du
dessin. Il rend deux lectures d'une même équipe : les cases du dessin
(responsables seuls ; ceux qui n'encadrent personne sont comptés sous leur
responsable) et la liste nominative, et les fait porter sur **la population
analysée**, filtres compris. Un salarié dont le responsable a été écarté par
un filtre se rattache au premier responsable restant au-dessus de lui : sans
ce rattrapage, un filtre qui retire un chef de service détacherait son
service entier, et le dessin perdrait des personnes que les autres onglets
comptent toujours. Le seuil de publication, lui, **n'y vaut pas par défaut**
(`privacy_parameters.mask_in_org_chart`, faux) : cette page ne sort jamais de
l'écran, aucun document, aucun export, aucun journal, et elle porte sur une
équipe que son lecteur vient de désigner. Masquée, elle serait inutilisable :
un poste tenu par trois personnes n'aurait ni minimum, ni médiane, ni
maximum. Un test vérifie que `reporting`, `export` et `slides` n'importent
pas ce module : le jour où l'un d'eux le ferait, l'exemption devrait être
rediscutée avant publication. La base est le temps
plein, avec le même repli sur le montant versé que la page des écarts quand
le fichier ne porte aucun temps de travail.

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
| Données personnelles | Jamais dans les logs ni dans les messages d'erreur ; identifiants hachés SHA-256 ; le classeur porte les valeurs individuelles sous référence anonyme, et le dit en tête de sa Synthèse |
| Dépendances | Zéro. `pip install` n'est jamais requis |

## 6. Confidentialité : petits effectifs

`privacy_parameters.json`, appliqué dans `metrics.py` (donc impossible à
contourner depuis un écran) :

| Paramètre | Défaut | Effet |
|---|---|---|
| `min_headcount_publish` | 5 | En deçà, les indicateurs sont masqués |
| `min_headcount_warning` | 10 | En deçà, avertissement d'interprétation |
| `min_headcount_chart` | 10 | En deçà, graphiques désactivés |
| `anonymise_identifiers` | true | Matricule remplacé par une empreinte SHA-256 tronquée |

### La vue d'ensemble tient sur un écran

Trois colonnes, et non deux. À deux, la colonne de population portait la
liste, le camembert et les deux pyramides, neuf cents pixels, pendant que
celle de rémunération s'arrêtait à cinq cents : la page débordait par
déséquilibre, non par excès de contenu. Les pyramides, qui sont le bloc le
plus haut, prennent donc une colonne à elles. Sous `OVERVIEW_COLUMN` × 3, la
disposition revient à deux colonnes et la page défile : mieux vaut défiler
que rogner.

La tranche **fourre-tout** d'une pyramide, valeur absente, ou hors des
bornes déclarées : un âge de douze ans, une ancienneté vide, garde sa
ventilation par sexe et se reconnaît à `catch_all`. Elle posait auparavant
« femmes : 0, hommes : 0 » et rangeait tout le monde sous `unknown_sex` : la
même clé portait deux notions, et la fenêtre annonçait « sexe non renseigné »
des salariés qui en avaient un. Les deux populations absentes du dessin se
comptent désormais séparément : celles qu'aucune tranche n'accueille, et
celles dont le sexe est inconnu, qui ont une tranche mais aucune aile.

La page **rend la hauteur dont elle dispose**. Dimensionnée pour le pire
cas, une fenêtre basse, ou un affichage Windows à 150 % qui grossit les
polices, elle laissait un tiers de hauteur vide sur un grand écran.
`_fit_overview` mesure la place offerte et la restitue : d'abord aux
graphiques, qui se lisent d'autant mieux qu'ils sont grands (chacun borné :
`PYRAMID_ROW_MAX`, `PIE_RADIUS_MAX`, `SCALE_HEIGHT_MAX`), puis en écartant
les blocs les uns des autres, un vide réparti se lit comme une respiration,
le même vide massé sous le dernier bloc comme une page inachevée. L'écart de
départ est retenu au premier passage, sans quoi il grandirait à chaque
redimensionnement. L'ajustement est différé, il mesure, donc la géométrie
doit être posée, et porte la génération qui l'a demandé : recomposée
entre-temps, la page a jeté les cadres que cet appel allait mesurer.

Le nombre de colonnes **suit la largeur** et n'est pas décidé une fois pour
toutes : un onglet qui n'a jamais été affiché mesure un pixel de large, et la
page se figeait alors à deux colonnes pour le reste de la session, y compris
en plein écran. `_on_overview_resize` relaie chaque changement de largeur et
redispose la page quand le compte change : la condition ne bascule qu'une
fois par franchissement, et redisposer ne change pas la largeur, donc ni
rafale ni boucle. Tant que la largeur est inconnue, la page part sur trois
colonnes : mieux vaut partir de la disposition qui tient sur un écran que
s'y figer à deux.

L'anneau du camembert est une **image antialiasée** produite par `raster`,
et non un `create_arc` : le canevas Tk ne lisse pas ses arcs, et les bords en
escalier étaient la première chose qu'on voyait de la page. Un seul passage
d'échantillonnage pour tout l'anneau, chaque échantillon décide de quelle
part il relève, environ 90 ms pour 100 pixels de diamètre, mis en cache et
recalculé seulement quand les données ou le thème changent. Le survol ne peut
donc plus se lire sur l'objet pointé : il retrouve la part par l'angle, avec
la même trigonométrie que le tracé.

`PieChart` et `ScaleChart` suivent la règle des autres graphiques : ils se
retracent au redimensionnement, mesurent leurs libellés plutôt que de compter
les lettres, et ne décident d'aucun seuil, `ScaleChart` lit les percentiles
que le moteur déclare publiés et ne trace que ceux-là. La répartition par CSP
est calculée par `metrics`, dans le résultat d'analyse : un écran qui
parcourrait lui-même la population finirait par compter autrement que le
moteur, et deux chiffres du même nom se contrediraient.

### Les deux boîtes à moustaches

Elles partagent `_Boxes`, qui porte ce dont elles répondent toutes deux :
le choix des lignes traçables, le tri, l'étendue commune et le contenu de
la bulle. `BoxPlotChart` les couche, une ligne par segment, l'intitulé à
gauche sans inclinaison, quarante postes sur une page, et
`VerticalBoxPlotChart` les dresse : la rémunération en ordonnée, les
catégories côte à côte. Deux copies des règles de confidentialité auraient
fini par diverger, et c'est la confidentialité qui en aurait fait les
frais : un segment sous le seuil graphique ne se trace sur aucune des deux.

La **bulle** de survol rend une structure, titre, colonnes, lignes,
colonne marquée, et `Tooltip.show_table` la pose en grille de `Label`.
Elle était composée en texte à chasse fixe, blanche sur fond sombre et en
petit corps : trois colonnes alignées que personne ne lisait sans se
pencher. C'est la grille qui aligne, la police peut donc être celle de la
fenêtre, et la bulle est sombre sur fond clair. Elle n'est reconstruite
que si son contenu change : le survol envoie un événement par pixel. Et
elle se place à gauche du curseur quand elle ne tient pas à sa droite.

Les **tranches d'âge se ferment en bas** (`close_the_bottom`) : un
découpage qui commence à 20 reçoit « <20 », sinon un apprenti de 19 ans
tombait dans le fourre-tout. C'est le symétrique de la prolongation du
haut, et c'est ce qui rend la tranche à un fichier de paramètres
antérieur à elle sans le retoucher.

La version dressée **ne plafonne pas la largeur de ses colonnes** : elles
se partagent la place offerte, et ne se posent sur leur plancher que
lorsqu'elles ne tiennent plus, la zone défile alors, plutôt que d'écarter
des catégories. La boîte, elle, est plafonnée : une boîte large comme un
quart d'écran n'est plus une boîte à moustaches. Les intitulés se mesurent
avant de choisir leur inclinaison : droits tant qu'ils tiennent sous leur
colonne, inclinés à 45° sinon, dressés à la verticale, on lit un nom à la
fois en tournant la tête.

L'**ordre de l'abscisse** se choisit, et son défaut diffère d'une
présentation à l'autre : la couchée s'ouvre sur l'effectif, quarante
postes empilés, on cherche d'abord ce qui pèse, la dressée sur l'ordre
que le moteur a posé. Lui seul sait de quoi la dimension est faite :
tranches d'âge et d'ancienneté dans l'ordre déclaré, échelles chiffrées
dans l'ordre des nombres, le reste selon `chart_parameters.segment_order`.
« Ordre de la dimension » ne trie donc pas : il rend les lignes telles
qu'elles sont arrivées. Le défaut vit dans `DEFAUT`, et non au premier
rang d'`ORDERS` : une entrée ajoutée en tête changeait sinon le défaut, et
le repli d'un tri devenu inapplicable, sans que personne le décide.

Au-dessus de tous ces ordres, un **rangement posé à la main**
(`chart_parameters.segment_manual_order`, une liste de valeurs par
dimension) : il a été décidé, les autres sont déduits. Il vit dans le
moteur et non dans la fenêtre, de sorte qu'il vaut aussi pour les tableaux
et les documents. Ce qu'il ne nomme pas prend la clé que l'ordre calculé
aurait donnée, précédée d'un rang qui la place en fin : une valeur
nouvelle ne disparaît pas et ne s'invite pas au milieu. La correspondance
se fait sur le libellé plié (casse et accents indifférents), comme partout
ailleurs. `reorder_segments` range un bloc déjà calculé sur place :
changer un ordre ne change aucun chiffre, et relancer l'analyse
recalculerait ce qui est juste.

Une **échelle chiffrée** est reconnue avant le motif ordinal `G1..G8` :
celui-ci ne reconnaît pas « 106,5 », et l'échelle retombait alors sur
l'ordre alphabétique, qui range 100 avant 99. Une valeur non renseignée
ne participe plus au choix de l'ordre, une seule suffisait à faire
retomber l'échelle entière, et se range en fin.

Enfin, une valeur de dimension **s'écrit sans décimale inutile**
(`segment_label`) : un coefficient est déclaré numérique, et revenait
« 230.0 » sur l'abscisse, dans les filtres, dans les tableaux et dans les
documents. C'est la règle déjà appliquée aux bornes de tranche.

L'ordonnée porte le **champ d'analyse**, nommé par le moteur
(`value_label` dans le bloc de segments) et non par le graphique : écrit
dans la fenêtre, le libellé aurait annoncé « Salaire de base » sur un axe
réglé sur autre chose (§7).

### Les axes du nuage

Le cadrage garde une marge autour des points extrêmes, **mais ne franchit
jamais zéro** quand les données ne le franchissent pas : une rémunération,
une ancienneté, un âge ne sont pas négatifs, et un repère ouvert à −320 EUR
montre un quart de cadre où aucune donnée ne peut exister. La règle ne cale
pas l'origine à zéro pour autant : sur des salaires de 25 000 à 80 000, un
axe partant de zéro écraserait le nuage dans son tiers supérieur, et c'est
justement leur écart qu'on vient regarder.

Le **déplacement et le zoom** s'y tiennent aussi : un plancher par axe,
posé à zéro quand la grandeur ne descend jamais en dessous, et la fenêtre y
est ramenée par translation, rogner changerait le niveau de zoom sous les
doigts de l'utilisateur, ce qui se lit comme un défaut. Sans ce plancher, le
cadrage d'origine respectait zéro mais un glissement promenait la fenêtre où
il voulait.

Ils sont lus dans `pay_equity_parameters.profile_fields`, qui les déclare
déjà, champ, libellé et unité, pour la page des écarts. Une seconde liste
aurait fini par en différer : une prime maison ajoutée au paramétrage serait
apparue d'un côté et pas de l'autre. Les champs nominatifs en sont exclus :
un nuage dont l'axe porte un matricule n'est pas un nuage, et sa légende
entrerait dans les documents.

Le jeu de données porte `x_axis` et `y_axis` (libellé + unité) : l'écran, la
restitution et les slides les lisent plutôt que de les déduire du nom du
champ, qui ne dit ni « EUR » ni « ans ». Changer d'axe depuis la fenêtre
repasse par `scatter_dataset`, jamais par un recalcul local, pour que
l'échantillonnage et le regroupement des couleurs restent ceux du moteur.

## 7. Formulation des résultats

Une valeur hors bornes interquartiles est présentée comme
Ces situations paraissent à l'écran, dans l'export Excel et dans le support
de présentation, jamais dans la restitution HTML : celle-ci s'arrête à
l'histogramme. Un document qui circule n'a pas à porter de ligne
nominative, et une liste de cas sans leur contexte se lit comme un verdict.
`_distribution_section` ne rend donc que le graphique.

La distribution porte aussi un **découpage par sexe** (`sex_split`), calculé
par le moteur et non par la fenêtre : un écran qui parcourt la population
pour son propre compte finit par compter autrement que le moteur, et par
afficher un effectif que le document contredit. Les deux ventilations sont
posées sur les **classes de la population entière**
(`statistics_engine.histogram_like`) : deux histogrammes aux classes
différentes ne se comparent pas. Chaque côté porte son propre droit au tracé,
comme les demi-segments de `segment_by_sex`, et le dos à dos n'est offert que
si les deux l'ont, une seule distribution ne se comparant à rien.

L'écart-type reste calculé et exporté comme statistique technique, mais n'est
pas présenté en KPI de pilotage : les ratios de dispersion (Q3/Q1, P90/P10,
moyenne/médiane) sont les indicateurs mis en avant.

## 8. Percentiles

Méthode inclusive à interpolation linéaire (type 7), identique à
`PERCENTILE.INCLUSIVE` d'Excel et au défaut de numpy : un contrôle refait sous
Excel par l'équipe C&B donne exactement la même valeur. Les valeurs de
référence sont figées dans `tests/test_statistics.py`.

## 8 bis. Temps de travail et rémunération à temps plein

Un fichier de paie porte le montant **versé**, non le taux plein : un
salarié à 80 % y figure pour 80 % de son salaire. Dans une population où le
temps partiel est majoritairement féminin, le cas ordinaire, un écart
femmes/hommes calculé sur ces montants mesure d'abord une différence de
temps de travail, et publie comme écart de rémunération ce qui n'en est
pas un.

L'outil publie donc **les deux** : l'écart versé et l'écart à temps de
travail égal, avec la différence entre eux, ce que le temps partiel
explique. Jamais l'un à la place de l'autre : ils répondent à deux
questions, et le lecteur doit savoir laquelle il cite.

**La colonne d'abord.** La même notion s'écrit « 0,8 », « 80 » ou « 80 % »
selon le SIRH. Tant que rien ne calculait avec elle, l'écriture n'avait pas
d'importance ; dès qu'on divise un salaire par elle, un « 80 » pris pour 80
divise le salaire par quatre-vingts. L'échelle se déduit donc de la
**colonne entière**, jamais de la cellule : un maximum au-delà de 1,5, ou
un seul pourcentage écrit explicitement, et toute la colonne est en
pourcentage.

Ce qui ne peut pas se trancher est refusé plutôt que deviné :

| Cas | Traitement |
|---|---|
| « 1 » dans une colonne en pourcentage | ligne écartée, `fte:ambiguous_scale`, un temps plein mal écrit vaudrait 1 % |
| ETP nul, négatif, au-delà du temps plein | ligne écartée, `fte:out_of_range` |
| ETP inconnu | exclu du calcul à temps plein : le supposer plein serait l'erreur même que ce calcul corrige |

Les deux premiers cas remontent au contrôle qualité avec leurs numéros de
ligne. La **couverture** est publiée avec l'indicateur : un temps plein
calculé sur la moitié de la population ne se lit pas comme un temps plein
calculé sur toute la population, et le seuil de confidentialité s'y
applique comme ailleurs.

**Le calcul est refaisable.** L'onglet Contrôle porte la formule, qui
divise ligne à ligne :
`AVERAGE(IF((salaire<>"")*(etp<>"")*(etp>0), salaire/etp))`. La colonne
« Temps de travail » figure pour cela dans les données individuelles : un
indicateur publié sans le moyen de le refaire n'a pas sa place dans ce
classeur.

## 8 ter. La base de comparaison de l'égalité professionnelle

Les indicateurs de la directive se publient sur les montants versés : c'est
ce qu'un employeur paie, et c'est ce qu'il doit publier. La comparaison
femmes / hommes **poste par poste** répond à une autre question, deux
personnes qui font le même travail sont-elles payées pareil, et elle se
fait donc sur une autre base, la même partout sur la page :

`analysis_field` (salaire de base par défaut), **ramené au temps plein**.

Une base ne se devine pas : `pay_equity.basis_description(population,
config)` la nomme en clair, l'écran et les documents affichent cette phrase
telle quelle. Ils ne peuvent donc pas annoncer une base que le moteur
n'applique pas.

Elle porte une clause de repli, et une seule : si **personne** n'a de temps
de travail renseigné, rien ne peut être ramené à rien. Plutôt qu'une page
vide, ou, pire, l'hypothèse tacite que tout le monde est à temps plein, la
comparaison porte alors sur les montants versés et le dit. Un temps de
travail inconnu **au cas par cas** sort du calcul, avec la couverture pour
le signaler.

Le masquage suit la base : il porte sur le nombre de salariés **dont le
calcul est possible**, non sur l'effectif du groupe. Un poste de trente
personnes dont deux ont un temps de travail connu publierait la rémunération
de ces deux-là.

### La significativité

Un écart se lit avec sa fiabilité. 30 % d'écart entre trois femmes et quatre
hommes est un tirage, pas un fait ; 4 % entre deux cents personnes n'en est
probablement pas un. Sans cette mesure, un classement par ampleur met en
tête les postes les moins peuplés : ceux dont l'écart est le moins sûr.

Le test est celui de **Welch** (`statistics_engine.welch_comparison`) : il ne
suppose pas que les deux sexes ont la même dispersion de salaire, ce qui n'a
aucune raison d'être vrai. La loi de Student est évaluée par la fonction bêta
incomplète régularisée, écrite dans le moteur : la bibliothèque standard ne
la fournit pas, et aucune dépendance externe n'est admise (§34). Elle est
vérifiée contre des valeurs de table **et** par intégration numérique de sa
propre densité.

Deux cas ne se remplacent pas par un chiffre inventé :

| Cas | Traitement |
|---|---|
| Moins de deux montants d'un côté | aucun test : `p_value` vaut `None`, le poste n'est pas mis en tête |
| Les deux séries sans aucune dispersion (grille salariale) | le *t* est infini : probabilité nulle si les deux montants diffèrent, totale s'ils sont égaux |

Le seuil (`significance_level`, 5 %) ne masque rien et ne change aucun
calcul : il commande le classement et la mention affichée. Le logiciel ne
décide pas : un écart significatif peut être justifié par des critères
objectifs, un écart non significatif reste un écart.

### Ce que la page montre

Une seule page, trois temps : les groupes classés, le groupe retenu en trois
colonnes, les personnes qui décrochent. Rien ne s'ouvre, rien ne se replie :
les trois blocs se répondent, et choisir un groupe ne fait pas disparaître le
classement dont il vient.

**Le groupe de comparaison se construit.** Jusqu'à trois dimensions déclarées
se composent (`cross_key`, `split_by` acceptent une suite de champs depuis
l'origine) ; une quatrième, dite « de lecture », ne change aucun calcul et
n'ajoute qu'une colonne à côté de chaque personne. C'est là que se branche
une revue du personnel, « talent », « performance », « en décalage », sans
une ligne de code, comme n'importe quelle dimension (§7).

**Les personnes n'ont pas de nom dans le moteur.** `lagging_members` et
`group_positions` rendent, pour chaque salarié, son numéro de ligne dans le
fichier et sa référence anonyme : jamais son identité. C'est la fenêtre qui
rapproche un nom, depuis la population qu'elle détient déjà, et seulement si
`show_identities_on_screen` l'y autorise. Le §6 l'exige : l'identité ne
transite pas par le résultat d'analyse, donc aucun document produit ne peut
en porter.

**Le repère est la médiane du groupe**, sur la base de comparaison de la
page, et il n'existe que si le groupe atteint le seuil de publication : une
médiane établie sur trois personnes désignerait ces trois-là, et situer
quelqu'un par rapport à elle n'apprendrait rien. Les groupes sans repère sont
comptés et annoncés, jamais tus.

**Un seul sens pour tous les écarts.** Positif veut dire que les femmes sont
en dessous : sur un pourcentage comme sur une différence d'années. La page
pose côte à côte des écarts de nature différente ; deux conventions de signe
y auraient fait lire « +8,6 % » et « −0,4 an » pour dire deux fois la même
chose.

**Tout se refait.** Le classeur porte, poste par poste, le bloc à temps
plein : moyennes, médianes, écarts, effectifs portant l'écart et couverture,
chacun en formule sur les données individuelles. Vérifié en exécutant ces
formules sous LibreOffice, valeurs en cache retirées.

## 9. Traçabilité

La ligne de commande produit un manifeste JSON : moteur, version, date,
nom et empreinte SHA-256 du fichier source, effectif, filtres, intégralité
des paramètres. Il contient l'empreinte du fichier, jamais son contenu :
donc aucune donnée personnelle. C'est sa seule sortie qu'un programme peut
relire, et elle sert à enchaîner des analyses.

La fenêtre, elle, ne l'écrit pas : ce qu'il porte de lisible, fichier
source, périmètre, date, effectif, est déjà en tête de la restitution et
sur la garde de la synthèse, et le reste était du JSON qu'aucun
destinataire de ces documents n'ouvre.

## 10. Performance

Mesures sur population fictive (`python3 tools/benchmark.py`), poste Linux
conteneurisé, secondes :

| Effectif | Import | Normalisation | Qualité | Calculs | Restitution | Total | HTML | RAM |
|---|---|---|---|---|---|---|---|---|
| 1 000 | 0,07 | 0,01 | 0,00 | 0,03 | 0,00 | **0,12** | 0,2 Mo | 26 Mo |
| 10 000 | 0,82 | 0,12 | 0,01 | 0,45 | 0,02 | **1,43** | 0,7 Mo | 55 Mo |
| 50 000 | 4,68 | 0,59 | 0,20 | 2,99 | 0,02 | **8,47** | 0,7 Mo | 178 Mo |
| 100 000 | 9,93 | 1,39 | 0,16 | 7,17 | 0,02 | **18,68** | 0,7 Mo | 335 Mo |

Le banc mesurait moins que ce que l'outil execute : il omettait l'equite
salariale, presente dans toute analyse reelle. Elle y est desormais, et la
colonne « Calculs » a donc grossi de ce qu'elle cachait.

Trois chemins chauds ont ete corriges apres profilage : la comparaison des
ecritures du sexe redecomposait en Unicode les memes libelles a chaque
salarie (trente-huit pour cent du temps de calcul), la lecture des dates
recompilait un analyseur `strptime` la ou `fromisoformat` suffit, et le
nettoyage des valeurs convertissait des flottants deja flottants. Sur ce
banc, la colonne « Calculs » passe de 9,00 s a 7,17 s a cent mille
salaries ; sur une entree CSV, ou les dates arrivent en texte et non deja
typees, l'analyse complete passe de 9,8 s a 2,8 s a trente-deux mille
salaries.

Comportement linéaire (cout unitaire stable a ±16 % de mille a cent mille).
**Seuil identifié** : au-delà de ~50 000 salariés, l'import XLSX (parsing
XML) domine et l'analyse dépasse les 10 secondes ; au-delà de ~200 000, la
population entièrement en mémoire deviendrait contraignante sur un poste à
8 Go.

### Un plafond pour ce que l'archive annonce

Un `.xlsx` est une archive : trois mégaoctets sur le disque peuvent en
annoncer trois mille une fois décompressés. Lus tels quels, ils ne
produisent pas une erreur mais une mort : le système tue le processus avant
que l'outil ait pu dire quoi que ce soit, et une fenêtre qui disparaît ne
laisse personne comprendre.

Chaque morceau lu (l'onglet, les chaînes partagées, les styles) est donc
comparé à un plafond **avant** d'être lu, puis la lecture elle-même est
bornée, au cas où l'en-tête mentirait. Le plafond est mesuré : un onglet de
200 000 salariés pèse 149 Mio décompressé ; il est fixé à 512 Mio, et il se
règle, `population_mapping.max_uncompressed_mb`, pour un poste qui a la
mémoire de lire plus.

### Le mapping se règle dans la fenêtre

Le paragraphe 7 veut un mapping configurable ; il l'était, dans un fichier
JSON. Une notion propre à l'entreprise, direction, revue du personnel,
convention, demandait donc d'ouvrir `population_mapping.json` au
bloc-notes, d'y ajouter un champ, ses alias, puis une entrée dans
`dimensions`. Peu d'utilisateurs le feront, et aucun ne devrait avoir à le
faire.

L'écran d'association tient en une ligne par colonne : son intitulé, ses
premières valeurs, son rôle, et une case « filtre et axe ». Le rôle
« Organisation » fait les trois gestes d'un coup, créer le champ à partir
de l'intitulé, en faire l'alias de la colonne, le déclarer comme
dimension, parce que c'est le cas courant.

Trois règles tiennent cet écran :

- **Un seul état par décision.** Les cases des colonnes et le panneau des
  champs sans colonne écrivent dans le même dictionnaire (`rows`), et c'est
  lui que `collect()` traduit. Deux jeux de cases pour une même vérité
  finissaient par se contredire : l'écran disait « proposé », le fichier
  disait non.
- **Le libellé se montre, le nom technique s'enregistre.** La liste propose
  « Salaire de base » ; le fichier garde `base_salary`, qui s'écrit aussi en
  ligne de commande. `_field_of` accepte les deux, le libellé d'abord, car un
  fichier de paramètres se corrige aussi à la main.
- **Une colonne ne rejoint un champ que par une orthographe écrite dans sa
  liste.** `resolve_mapping` a deux rangs : l'alias principal de chaque champ
  (la colonne que l'écran lui a attachée), puis les autres orthographes. Le
  nom technique ne vaut pas orthographe : un troisième rang le faisait valoir
  pour un champ sans alias, et il reprenait la colonne « Manager » que l'on
  venait d'ignorer. Une liste vide veut dire « aucune colonne ». Les défauts
  livrés écrivent donc le nom technique parmi les orthographes là où un
  fichier aux en-têtes techniques doit être lu.
- **Le modèle ne connaît que ce avec quoi il calcule.** `Employee` n'a plus
  de champ d'organisation : BU, établissement, métier, poste, statut vivent
  dans `extra`, comme toute notion déclarée, et `value()` les lit pareil.
  Les quatre noms internes du modèle (`row_number`, `issues`,
  `anonymous_id`, `extra`) sont refusés au mapping avec un message qui les
  nomme, et `assign` ne les écrit jamais.
- **La fenêtre entière défile.** Empilé entre des sections de hauteur fixe,
  le bloc des colonnes tombait à deux pixels de haut sur un écran
  ordinaire : la fonction existait et restait introuvable. Un test mesure
  désormais sa hauteur.

### Une seule racine Tk par processus

Deux interpréteurs Tk dans un même processus, plus des objets Tk libérés
tardivement, font écrire à Tcl `async handler deleted by the wrong thread`,
et **terminer le processus**, sans exception ni trace Python. L'outil
n'ouvre qu'un interpréteur : l'écran d'accueil et la fenêtre des paramètres
sont des `Toplevel` de la fenêtre principale. Les tests doivent tenir la
même règle ; celui du panneau d'attente utilise la fenêtre de l'outil, et
non une racine à lui.

Même famille : **aucun passage du ramasse-miettes depuis le fil de
calcul.** Un objet Tk libéré par le ramasseur (une image, une variable)
appelle Tcl dans son `__del__`, et un appel Tcl venu d'un autre fil que
celui de la fenêtre attend que celle-ci le serve ; si elle est elle-même
en train de ramasser, les deux fils s'attendent et l'analyse ne rend
jamais la main. `_without_cycle_collection` ne collecte donc qu'en fil
principal, et c'est la fenêtre qui fait le passage à la réception du
résultat.

Un premier plafond a déjà été traité : sans garde-fou, le nuage de points
produisait 100 000 cercles SVG et un HTML de 12,8 Mo (navigateur inutilisable).
`chart_parameters.scatter_max_points` (5 000 par défaut) applique un
échantillonnage systématique à pas constant, déterministe, donc reproductible
et traçable, et l'échantillonnage est signalé dans la restitution.

Leviers si le seuil doit être repoussé (V3) : import CSV plutôt que XLSX
(mesuré : 0,93 s contre 9,38 s pour 100 000 salariés, soit 10,1×), lecture
en flux sans matérialiser le tableau brut, pré-agrégation par segment.

## 10 bis. Empreinte des livrables

Le manifeste reste de taille modeste quel que soit l'effectif. Le classeur,
lui, porte la population : c'est ce qui permet d'en refaire les calculs. Deux
seuils l'empêchent de devenir inouvrable : `source_max_rows` (50 000) au-delà
duquel le fichier importé n'est plus recopié, et `control_max_rows` (20 000)
au-delà duquel le contrôle par segment n'est plus posé, chacune de ses
formules relisant toute la population. À 60 000 lignes, le classeur se
construit en 3 secondes.

Deux réglages rendent le classeur purement agrégé :
`export_parameters.include_individual_data` et `include_source_file`.

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
au-dessus et se lisait comme un remplissage. Ces parts, moins de 30 ans,
30 a 49 ans, 50 ans et plus, anciennete inferieure a 2 ans, superieure a
10 ans, sont desormais portees par l'onglet Population de l'export Excel, ou
la densite ne coute rien. Elles restent calculees sur les valeurs reelles et
non sur les libelles de tranches : elles ne deviennent pas fausses si
l'utilisateur reparametre ses tranches.

Le taux de donnees valorisees n'apparait qu'en sous-titre, et seulement s'il
est inferieur a 100 % : une couverture partielle change la lecture de tous les
montants, une couverture complete n'apprend rien.

Les blocs se declarent en trois largeurs, `full`, `half`, `third`, et les
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
`Block` : un descriptif de contenu independant du format. Le rendu HTML et le
rendu PDF consomment la meme liste : les deux formats ne peuvent pas diverger.

### Adaptation a l'ecran

La page garde une **geometrie fixe** de 1280 x 720 : c'est ce qui garantit que
l'ecran, l'impression et le PDF montrent exactement la meme chose. Pour tenir
sur un ecran plus etroit, elle est **mise a l'echelle** (`transform: scale`)
plutot que reagencee, un reagencement ferait diverger le rendu ecran du rendu
papier.

Le facteur `--slide-scale` est calcule au chargement et au redimensionnement,
plafonne a 1 (on reduit pour tenir, on n'agrandit jamais). A l'impression il
est remis a 1 pour que le papier ne soit pas affecte. Sans JavaScript, la
valeur de repli est 1 : la page s'affiche a sa taille reelle.

Mesure du debordement horizontal (largeur de contenu / largeur de fenetre) :

| Fenetre | Avant | Apres |
|---|---|---|
| 768 px | 1017 / 753, deborde | 753 / 753, echelle 0,55 |
| 1024 px | 1145 / 1009, deborde | 1009 / 1009, echelle 0,75 |
| 1440 px | ok | ok, echelle 1 |

Le **rapport detaille**, lui, est fluide : grille de KPI en `auto-fill`,
tableaux larges dans un conteneur a defilement propre, SVG en `max-width:100%`.
Verifie sans debordement jusqu'a 390 px de large.

### Le PDF est genere, pas imprime

`io/pdf_writer.py` ecrit le PDF octet par octet : objets numerotes, table de
references croisees, flux de contenu compresses. Aucun navigateur a piloter,
aucun moteur de rendu, aucune dependance : le meme parti pris que pour le
XLSX.

Ce qui rend l'exercice tenable :

* seules les **14 polices de base** du format PDF sont utilisees (Helvetica),
  donc rien a embarquer ni a licencier, et aucune table `/FontFile` ;
* les **largeurs de glyphes** Helvetica sont tabulees, ce qui permet de
  centrer, aligner a droite et tronquer proprement ;
* le dessin se limite aux primitives dont les graphiques ont besoin,
  rectangles, lignes, cercles de Bezier, texte, exactement ce que produit
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
  {"field": "direction", "label": "Direction"},
  {"field": "groupe",        "label": "Groupe"}
]
```

Ajouter une notion metier (equipe, manager, direction) demande deux lignes de
configuration, un alias dans `fields`, une entree dans `dimensions`, et rien
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
| V0 : PoC | Import, contrôle, KPI, tableau | ✅ |
| V1 : MVP | Paramétrage, filtres, percentiles, ratios, nuage de points, export Excel | ✅ |
| V2 : Enterprise | Logs, versioning, tests, traçabilité, packaging, PDF | 🟡 partiel (logs, versioning, tests, traçabilité et **PDF natif** faits ; packaging à faire) |
| V3 : Optimisation | Performance, IHM, segmentation avancée, automatisation | ⬜ |

### Extensions prévues sans réécriture du cœur

Chacune s'ajoute comme fonction de `metrics.py` + section de `reporting.py` +
paramètres dédiés, sans toucher au pipeline : égalité salariale, promotions,
augmentations, variable, compa-ratio, positionnement en grille, budget
salarial, évolution N/N-1.

## 10 quinquies. Statistiques techniques non publiées

Deux statistiques sont calculées et restent accessibles au moteur, sans
figurer dans les restitutions :

* l'**ecart-type**, disponible dans l'export Excel mais jamais presente en
  indicateur de pilotage : ce sont les ratios de dispersion qui le sont ;
* le **R2** de la droite de tendance du nuage, retire des documents. Il
  demandait une explication pour etre lu, et sans cette explication il
  n'apportait rien. La pente chiffree est partie avec lui : annoncee seule,
  sur une population melangeant tous les groupes, elle affirmerait un lien que
  rien n'etaye. La droite reste tracee comme repere visuel.

`statistics_engine.linear_regression` continue de retourner les deux, ce qui
laisse la porte ouverte a un usage ulterieur : par exemple un R2 par segment,
la ou la lecture a un sens.

## 11 bis. Libellés et interface

Les libellés affichés, titres de section, en-têtes de tableaux, messages du
contrôle qualité, noms d'onglets Excel, sont accentués. Le PDF les rend sans
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
   lancé par un raccourci : aucune installation, aucune écriture registre ;
3. PyInstaller `--onedir` si un exécutable unique est exigé : à évaluer avec
   l'IT, un binaire non signé étant souvent plus suspect qu'un dossier de
   fichiers lisibles.

L'option 2 est recommandée : rien à compiler, contenu auditable par l'IT.

## 13. Interface graphique

`hr_analytics/ui/`, tkinter, livre avec Python : aucune
dependance, aucun telechargement, aucun droit administrateur.

    app.py       fenetre unique, parcours en quatre etapes
    charts.py    nuage et histogramme dessines sur un canevas
    progress.py  barre de chargement, animee sur l'horloge
    splash.py    ecran d'accueil du demarrage
    logo.py      la galaxie, calculee plutot que livree en image

**L'analyse tourne sur un fil separe** et rapporte son avancement par
`AnalysisRequest.progress` : le moteur annonce une étape et une part faite,
sans rien savoir de ce qui l'affiche. Le rappel est appelé depuis le fil de
calcul et ne fait que déposer dans une file ; c'est la fenêtre qui la relève
et dessine, Tk n'étant pas sûr pour deux fils.

Deux mesures gouvernent cette partie, toutes deux prises sur cent mille
salariés :

- **Le ramasse-miettes cyclique est suspendu le temps de l'analyse**
  (`_without_cycle_collection`) : 25,3 s avec, 21,5 s sans, pour un pic de
  mémoire identique. L'analyse construit des centaines de milliers d'objets
  qui vivent tous jusqu'à la fin ; le ramasseur les reparcourait à chaque
  passage sans jamais rien avoir à libérer, et figeait le fil d'affichage
  par tranches de deux cents millisecondes.
- **La tranche d'exécution des fils est réduite le temps de l'analyse**
  (`sys.setswitchinterval`) : le fil qui dessine passe de 37 à 41 images par
  seconde et d'une image sur dix en retard de plus de cent millisecondes à
  une seule sur l'analyse entière.

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

Les filtres, les valeurs des boîtes et les postes de la page des écarts
passent par la même fenêtre à cocher, `ValuePicker`, alimentée par le
fichier chargé : l'utilisateur choisit parmi ce qui existe, sans syntaxe à
taper et sans pouvoir inventer une valeur absente. `open_alone` (theme.py)
ne tient qu'une fenêtre secondaire à la fois : la même demande ramène la
fenêtre déjà ouverte au premier plan, une autre demande ferme la précédente.
Deux listes empilées appliquaient chacune son choix par-dessus l'autre.

`CheckRow` retire son écoute de la variable quand la case est détruite. Un
panneau qui se repose (les champs sans colonne, l'ordre des filtres) détruit
ses cases et garde ses variables : le clic suivant faisait dessiner une case
disparue, et Tk l'annonçait dans une fenêtre d'erreur.

**Aucun champ d'organisation n'est livré d'office.** `DEFAULTS` et
`config/` ne portent que les champs avec lesquels le moteur calcule
(identité, sexe, dates, temps de travail, salaire de base, rémunération
totale, manager) et les trois dimensions qu'il sait calculer (sexe,
tranches d'âge et d'ancienneté). Deux champs du modèle restent connus du
moteur sans être livrés, `period` et `variable_pay` : ils encombraient la
liste des rôles, et les ajouter à `population_mapping.json` suffit à les
faire revenir. Cette liste (`settings.candidate_fields`) ne propose que
les champs que la configuration déclare, moins les champs calculés : elle
unissait les champs du modèle, et un champ retiré du paramétrage y
revenait. BU, établissement, métier, poste, statut naissent de l'écran
« Associer les colonnes », rôle « Organisation », et
`segmentation.organisational_dimensions` les liste dans leur ordre. Les
réglages qui nomment un champ sont vides à la livraison et se replient
dessus : `pay_equity.category_field` prend la première notion déclarée que
le fichier renseigne (le métier d'abord), `metrics.default_colour_field`
la première déclarée sinon le sexe, le camembert ne se trace que sur un
champ choisi, et `people_columns` ajoute les notions déclarées avant les
montants. La section Analyse de la fenêtre des paramètres règle ces trois
champs parmi les notions déclarées ; la page des écarts enregistre aussi
son « Comparer par ». Les essais déclarent leurs notions dans
`tests/config_essai`, comme un utilisateur l'aurait fait ;
`tests/test_no_standard_field.py` garde la configuration livrée.

`SettingsWindow.restore_defaults` réécrit `config/*.json` depuis `DEFAULTS`
(`write_default_configuration`) après une question qui dit ce qui sera
perdu, puis la fenêtre principale relit le fichier avec ces réglages. Les
fichiers livrés dans `config/` sont identiques à `DEFAULTS`, et un test le
vérifie : « usine » n'a qu'un sens.

L'écart F/H de la boîte dédoublée s'explique au survol de sa colonne et de
son en-tête, avec le texte du glossaire (`median_gap`) : l'écran et le
rapport décrivent le même calcul.

Aucun tiret cadratin dans ce que l'outil montre ou livre : chaînes de
l'interface et des documents produits, guides, configuration.
`tests/test_no_em_dash.py` le garde ; les commentaires du code ne sont pas
concernés.

L'analyse tourne dans un fil separe, avec une barre de progression : sur
100 000 salaries elle prend une quinzaine de secondes, et une fenetre figee
passerait pour un plantage.

### Identifier un salarie a l'ecran, jamais dans un document

Le paragraphe 6 du cahier des charges exige des identifiants
*anonymisables* : une capacite, pas une obligation. Identifier un salarie a
l'ecran est le geste meme de l'analyse : un point du nuage a trente pour
cent sous la mediane ne veut rien dire tant qu'on ne sait pas de qui il
s'agit. La fenetre le nomme donc, et le reglage
`privacy_parameters.show_identities_on_screen` permet de s'en tenir a la
reference anonyme.

**La separation est structurelle, pas conditionnelle.** L'identite n'entre
jamais dans le resultat d'analyse : le jeu de points ne porte qu'un numero
de ligne (`row`), cle technique deja publiee par le controle qualite.
L'interface tient un index `numero de ligne -> identite`, construit depuis
la population qu'elle detient deja, et le consulte au moment d'afficher une
info-bulle. Aucun reglage, present ou futur, ne peut donc faire porter un
nom a une restitution, a un export ou au journal technique, puisque le nom
n'est jamais entre dans ce qui sert a les produire. Un test le verifie sur
tous les fichiers produits, reglage active.

### Tests

Les tests d'interface qui exigent un affichage sont ignores automatiquement
lorsqu'il n'y en a pas : le moteur reste testable sur un serveur sans ecran.
Le developpement s'est fait sur un affichage virtuel (Xvfb), chaque ecran
etant capture et relu : c'est ainsi qu'a ete vu que la liste des filtres
poussait le bouton "Analyser" hors du cadre.
