# Cartes de notions : ue3-04 (Rupture du contrat de travail)

15 octobre 2026. Fichier : `data/ue3/ue3-04.cartes.json`. Fiche de référence : `data/ue3/ue3-04.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`) et reprend leurs `src` et `url`. Une passe antérieure (commit 609a3b1) a supprimé k05 et k19 et ajouté k36 et k37. k05 portait sur l'homologation de la rupture conventionnelle, déjà traitée par k04 et k17. k19 portait sur la prescription de l'indemnité compensatrice de préavis. Leurs identifiants ne sont pas réutilisés.
2. **Relecture de fidélité.** Le premier relecteur a contrôlé les 35 cartes au regard de la fiche, seul juge pour cette passe. Il en a corrigé 6 (k06, k16, k25, k29, k31, k36), sans suppression ni ajout.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code du travail, Code civil, Code de la sécurité sociale et jurisprudence de la chambre sociale. Il a vérifié trois points :
   - chaque question n'appelle qu'une seule réponse ;
   - une règle qui connaît des exceptions est délimitée ;
   - le jeu ne contient ni doublon ni carte triviale.

   Bilan : 6 cartes corrigées, aucune suppression, aucun ajout.
4. **Recherches.** Aucune recherche WebSearch. Les six corrections reposent sur des articles stables du Code du travail et sur une jurisprudence constante, sans doute réel sur le fond (voir « Recherches faites »).

`node validate.js data/ue3/ue3-04.cartes.json` : ✓ (35 cartes, 7 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 7 de définition (`def` : k01, k02, k04, k06, k07, k25, k27) et 28 de compréhension (`comp`). Les identifiants k05 et k19 restent libres.
- **Définitions** : les 5 items ont chacun au moins une carte (k01 ; k02 et k03 ; k04 ; k06 ; k07 et k08).
- **Règles essentielles** : les 17 items ont chacun au moins une carte. Certains points de ces items n'ont pas de carte :
  - **#0** : la demande de précisions sur les motifs dans les quinze jours de la notification ;
  - **#2** : la priorité de réembauche pendant un an ;
  - **#4** : la contribution de l'employeur quand il ne propose pas le CSP ;
  - **#7** : l'indemnité compensatrice due en cas d'inexécution du préavis du fait de l'employeur.

  Les montants de l'indemnité légale (#8) et les bornes du barème (#10) relèvent du calcul ou du par cœur chiffré : ils n'ont pas de carte.
- **Ce qui a changé récemment** : 3 items sur 5 ont une carte (#0 : k06, k28, k29 ; #2 : k25, k30 ; #4 : k31). **#1** (contribution patronale spécifique portée à 40 %) et **#3** (durée d'indemnisation chômage après rupture conventionnelle) sont millésimés 2026 : ils sont exclus par le contrat.
- **Points de vigilance** : 4 items sur 5 ont une carte (#0 : k32 ; #1 : k33 ; #2 : k16 et k18 ; #3 : k34). **#4** (lien avec l'assurance chômage, différé d'indemnisation) est millésimé 2026 : il n'a pas de carte.
- **Chiffres et seuils** : aucun des 8 items n'est cité dans `base`.
  - Les délais stables de **#0, #1, #2, #3 et #6** figurent déjà dans les cartes tirées des Règles essentielles (k09, k13, k14, k16 à k18, k20, k36, k37).
  - **#4** (délai général de douze mois pour contester la rupture, L. 1471-1) n'a pas de carte.
  - **#5** (taux de ressort du conseil de prud'hommes) n'a pas de carte : c'est un chiffre à apprendre par cœur.
  - **#7** (prescription triennale de l'indemnité compensatrice de préavis) avait une carte, k19, supprimée lors de la passe antérieure.
- **Doublons.** Le jeu est au plafond de 35 cartes et aucune carte n'a été supprimée. Trois groupes de cartes se recoupent sans faire doublon :
  - **k25 et k30** se recoupent sur le contrat de valorisation de l'expérience. k25 définit la mise à la retraite, k30 dit ce que permet ce contrat et à qui il s'adresse.
  - **k06, k28 et k29** traitent chacune d'une facette de la présomption de démission : la définition, la mise en demeure, le motif légitime.
  - **k02 et k03** séparent la définition du licenciement économique de ses causes.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la première relecture est tronqué au milieu de la correction de k36. Pour k36, la correction ci-dessous a été constatée dans le fichier (comparaison avec le commit 95746d3).

| cible | problème | correction |
|---|---|---|
| k06 | La définition de la présomption de démission était présentée comme absolue. Or la fiche (Ce qui a changé récemment#0) précise qu'un motif légitime fait obstacle à la présomption. La réponse était donc fausse pour un salarié absent pour raisons médicales, droit de retrait ou grève. | Ajout de « sauf motif légitime faisant obstacle à la présomption » à la fin de la réponse (51 mots). « Ce qui a changé récemment#0 » est ajouté en second item de base. `src` et `url` restent ceux de Définitions#3. |
| k16 | La question « De quel droit chaque partie dispose-t-elle… » affirmait que chaque partie dispose du droit de rétractation. La fiche ne le dit pas : Règles essentielles#5 parle seulement d'un « délai de rétractation ». C'était une connaissance extérieure. | Question : « Quel délai s'ouvre à compter de la signature d'une convention de rupture conventionnelle par l'employeur et le salarié ? ». La réponse commence par « Un délai de rétractation de quinze jours calendaires » ; le reste est inchangé. |
| k25 | La définition de la mise à la retraite ne visait que le salarié ayant atteint 67 ans. Or, selon la fiche (Ce qui a changé récemment#2), dans le contrat de valorisation de l'expérience, l'employeur peut mettre le salarié à la retraite dès qu'il remplit les conditions du taux plein, donc parfois avant 67 ans. L'exception était oubliée. | Réponse complétée : « …(67 ans), ou, dans le contrat expérimental de valorisation de l'expérience, dès qu'il remplit les conditions d'une pension à taux plein » (66 mots). « Ce qui a changé récemment#2 » est ajouté en second item de base. `src` et `url` restent ceux de Règles essentielles#13. |
| k29 | La question « Qu'est-ce qui fait obstacle à la présomption de démission ? » admettait d'autres réponses justes tirées du cours, comme une mise en demeure irrégulière ou un délai inférieur à quinze jours. Or la réponse attendue est le motif légitime. | Question : « Quelle raison d'absence fait obstacle à la présomption de démission du salarié ayant abandonné son poste ? ». La réponse est inchangée. |
| k31 | La réponse rendait le licenciement sans cause réelle et sérieuse dès que l'accord « comportait » des dispositions étrangères à ses objets. La citation de la fiche (Ce qui a changé récemment#4) exige en outre que ces dispositions modifient le contrat du salarié. | « si l'accord modifiait son contrat par des dispositions étrangères à la durée du travail, à la rémunération et à la mobilité professionnelle ou géographique interne » (52 mots). |
| k36 | La procédure d'interrogation écrite préalable à la mise à la retraite ne s'applique pas au contrat de valorisation de l'expérience. Dans ce contrat, l'employeur met le salarié à la retraite sans recueillir son accord (Ce qui a changé récemment#2). La suite du résultat transmis est tronquée. | Question délimitée : « En principe, quelle procédure préalable encadre la mise à la retraite d'un salarié par l'employeur selon le Code du travail ? ». La réponse est inchangée. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k04 | Selon la réponse, toute rupture conventionnelle n'est valable qu'après homologation par l'autorité administrative. Or l'article L. 1237-15 prévoit une dérogation pour le salarié protégé : sa rupture conventionnelle est soumise à l'autorisation de l'inspecteur du travail. La fiche ne mentionne pas cette exception. | « …et n'est valable, en principe, qu'après homologation par l'autorité administrative » (48 mots). | C. trav., art. L. 1237-14 et L. 1237-15 |
| k10 | L'article L. 1233-3 caractérise les difficultés économiques de deux façons. La première est l'évolution significative d'au moins un indicateur économique « tel qu' » une baisse des commandes ou du chiffre d'affaires, etc. La seconde est « tout autre élément de nature à justifier de ces difficultés ». La réponse présentait la liste des indicateurs comme fermée et l'indicateur comme le seul moyen de caractériser les difficultés. | « <b>Notamment par l'évolution significative d'au moins un indicateur économique</b>, tel qu'une baisse des commandes ou du chiffre d'affaires, des pertes d'exploitation ou une dégradation de la trésorerie ou de l'excédent brut d'exploitation. » La phrase sur les groupes est inchangée (53 mots). La seconde branche n'étant pas dans la fiche, elle est seulement signalée par « notamment » et « tel qu' ». | C. trav., art. L. 1233-3, 1°, a |
| k11 | La réponse ajoutait : « Il doit aussi consulter le CSE et informer l'administration. » Or la consultation du CSE ne vise que le licenciement collectif, et seulement dans les entreprises d'au moins onze salariés (L. 1233-8 pour moins de dix licenciements). Elle n'existe pas pour le licenciement économique d'un seul salarié. Cette phrase sortait en outre de la question, qui porte sur les efforts dus « à l'égard du salarié ». | Phrase supprimée. La réponse se limite aux efforts de formation et d'adaptation et à la recherche de reclassement (25 mots). | C. trav., art. L. 1233-4 et L. 1233-8 |
| k12 | La question « Quels critères déterminent l'ordre des licenciements… » faisait des quatre critères une liste limitative qui s'imposerait toujours. Or, selon l'article L. 1233-5, à défaut d'accord collectif, c'est l'employeur qui définit les critères, et ceux-ci « prennent notamment en compte » les quatre éléments. | Question : « Quels critères le Code du travail énumère-t-il pour fixer l'ordre des licenciements pour motif économique ? ». La réponse est inchangée. | C. trav., art. L. 1233-5 |
| k26 | La règle de l'arrêt de 2003 (licenciement sans cause réelle et sérieuse ou démission) est le principe. Si les faits reprochés à l'employeur justifient la prise d'acte et relèvent d'une nullité, celle-ci produit les effets d'un licenciement nul : violation du statut protecteur d'un salarié protégé, harcèlement, discrimination. La fiche ne mentionne pas ce cas. | Question délimitée : « En principe, quels effets produit la prise d'acte de la rupture de son contrat de travail par un salarié ? ». La réponse est inchangée. | Cass. soc., 25 juin 2003, n° 01-42.679 (principe) ; jurisprudence constante de la chambre sociale sur la prise d'acte justifiée d'un salarié protégé ; C. trav., art. L. 1235-3-1 |
| k35 | La question appelait tous les cas de rupture anticipée du CDD. Or le CDD peut aussi être rompu librement pendant la période d'essai (L. 1242-10 et L. 1221-25). Le CDD à objet défini peut en outre être rompu pour un motif réel et sérieux dix-huit mois après sa conclusion, puis à chaque date anniversaire (L. 1243-1, al. 2). Aucun de ces deux cas n'est dans la fiche. | Question : « Hors période d'essai, dans quels cas un contrat à durée déterminée (CDD) peut-il en principe être rompu avant l'échéance de son terme ? ». La réponse est inchangée. | C. trav., art. L. 1242-10, L. 1221-25 et L. 1243-1 |

Les 29 autres cartes ont été contrôlées sans changement : k01 à k03, k06 à k09, k13 à k18, k20 à k25, k27 à k34, k36 et k37. Aucune ne contient de calcul ni de chiffre millésimé.
- Les chiffres présents font partie d'une règle stable : 67 ans, 60 et 57 ans, 50 salariés, 10 licenciements sur 30 jours, huit mois d'ancienneté, quinze jours, douze mois.
- Les dates de k28 et k30 situent une réforme ; ce ne sont pas des chiffres annuels.
- L'âge du taux plein automatique (67 ans, CSS, art. L. 351-8, 1°) n'a pas été touché par la suspension de la réforme des retraites décidée fin 2025, qui porte sur l'âge légal et la durée d'assurance.

## Recherches faites

Aucune recherche WebSearch (0 sur les 3 autorisées). Les six corrections reposent sur des dispositions anciennes et stables du Code du travail, sans doute réel sur leur contenu :
- L. 1233-3, 1°, a, dans sa rédaction issue de la loi n° 2016-1088, et L. 1233-5 ;
- L. 1233-8, dans sa rédaction issue des ordonnances de 2017 ;
- L. 1237-15, L. 1242-10, L. 1221-25 et L. 1243-1 ;
- la jurisprudence constante sur la prise d'acte.

Aucune correction ne dépend d'un texte postérieur à 2025.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#1** (difficultés économiques). Ajouter la seconde branche de l'article L. 1233-3, 1°, a : les difficultés peuvent aussi être caractérisées « par tout autre élément de nature à justifier de ces difficultés ». Indiquer aussi que la liste des indicateurs n'est pas limitative (« tel qu' »).
2. **Règles essentielles#2** (obligations préalables au licenciement économique). Deux précisions :
   - La « consultation du CSE » ne concerne que le licenciement collectif, dans les entreprises d'au moins onze salariés (L. 1233-8 ; L. 1233-28 et suivants à partir de dix licenciements). Il n'y a pas de consultation pour le licenciement économique d'un seul salarié.
   - Les critères d'ordre s'appliquent à défaut d'accord collectif, et la loi dit qu'ils « prennent notamment en compte » les quatre éléments cités (L. 1233-5).
3. **Définitions#2 et Règles essentielles#6** (rupture conventionnelle). Ajouter la dérogation de l'article L. 1237-15 : la rupture conventionnelle d'un salarié protégé est soumise à l'autorisation de l'inspecteur du travail, et non à l'homologation.
4. **Règles essentielles#15** (prise d'acte). Il s'agit d'un complément. La prise d'acte justifiée produit les effets d'un licenciement nul lorsque les faits relèvent d'une nullité (statut protecteur, harcèlement, discrimination). Cette règle est à rattacher à un arrêt publié de la chambre sociale avant d'être écrite.
5. **Règles essentielles#14** (fin du CDD). Il s'agit d'un complément. La fiche peut signaler deux cas :
   - la rupture pendant la période d'essai (L. 1242-10) ;
   - la rupture du CDD à objet défini pour un motif réel et sérieux, dix-huit mois après sa conclusion puis à chaque date anniversaire (L. 1243-1, al. 2).
6. **Ce qui a changé récemment#4** (accord de performance collective). Il s'agit d'un complément. Le `t` dit « si l'accord comportait des dispositions étrangères à ces objets ». Il pourrait reprendre la condition « et modifiant son contrat de travail », qui ne figure que dans la citation. La même remarque a été faite dans `ue3-03-cartes.md`.

## Classement des exercices

Le classement automatique porte sur les 23 exercices QCM, QCM multiples et classements du chapitre : 20 QCM, 2 QCM multiples et 1 classement. Les 5 exercices de calcul (`calc`, #19 à #23) n'en font pas partie.

| nature | nombre |
|---|---|
| notion | 21 |
| calcul | 2 |
| chiffre | 0 |

Aucun désaccord entre les classements. Les deux QCM de nature calcul sortent des révisions espacées :
- **#5** : date à laquelle l'entretien préalable peut se tenir au plus tôt, à décompter en jours ouvrables. La règle des cinq jours ouvrables reste révisée par la carte k09.
- **#13** : date limite de rétractation d'une convention de rupture conventionnelle. La règle des quinze jours calendaires reste révisée par la carte k16.

Les 21 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes.
