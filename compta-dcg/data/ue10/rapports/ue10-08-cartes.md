# Cartes de notions : ue10-08 (Entités spécifiques, groupes et contrôle des comptes)

Date : 16 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-08.fiche.json` (maj du 15 octobre 2026), selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`) ; `src` et `url` sont copiés depuis le premier de ces items.
2. **Relectures de fidélité à la fiche.** Trois passes successives, sans recherche web, ont comparé chaque carte au texte (`t`) et à la citation (`cite`) de ses items de base. Elles ont corrigé 13 cartes. Une passe antérieure interrompue avait supprimé k31 et ajouté k36 ; la troisième passe a supprimé k10 et ajouté k37 pour couvrir la NEP 500. Les identifiants k10 et k31 restent vides, sans renumérotation.
3. **Relectures d'exactitude.** Deux relectures indépendantes, par un expert-comptable et juriste, au regard du droit et des normes en vigueur au 16 octobre 2026 (Code de commerce, Code civil, CGI et BOFiP, règlements ANC n° 2018-06 et n° 2020-01, NEP). Chacune a vérifié quatre points :
   - l'exactitude : rien de faux, de périmé, ou de vrai seulement dans un cas particulier non dit ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   La première relecture d'exactitude a fait 3 recherches et corrigé 6 cartes (k03, k20, k21, k24, k33, k35). La seconde, la présente, a fait 3 recherches restreintes à legifrance.gouv.fr et à anc.gouv.fr (voir « Recherches ») et corrigé 4 cartes (k01, k18, k26, k36). Aucune des deux n'a supprimé ni ajouté de carte.
4. **Validation.** `node validate.js data/ue10/ue10-08.cartes.json` : ✓ (35 cartes, dont 11 déf.).

## Bilan

- **Nombre de cartes : 35** (plafond du contrat). Les identifiants k10 et k31 restent vides.
- **Répartition : 11 cartes `def` et 24 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 7 items de « Définitions » ont chacun au moins une carte : #0 k01, #1 k02, #2 k04 et k05, #3 k15, k16 et k17, #4 k23 et k24, #5 k27, #6 k28.
  - 19 des 20 « Règles essentielles » servent de base à au moins une carte.
  - « Points de vigilance » : #0, #1, #2 et #5 sont couverts (k23, k24, k18, k29, k33).
  - « Ce qui a changé récemment » : #0, #1 et #2 sont couverts (k33, k21, k09).
  - « Chiffres et seuils » : #1 est couvert (k14).
- **Items de fiche sans carte :**
  - Règles essentielles#18 (conservation des documents). L'item mêle une règle stable (dix ans, C. com., art. L. 123-22) et un délai fiscal donné « rédaction en vigueur en 2026 » : voir « Points à reprendre dans la fiche ».
  - Points de vigilance#3 (erreurs délibérées, erreur répétée) et #4 (dépréciation et article 38 quater).
  - Ce qui a changé récemment #3 à #6 (NEP révisées, règlements ANC n° 2024-05, 2024-07 et 2026-01, NEP 600 révisée) : ce sont des dates d'homologation et d'application, sans règle de fond propre au chapitre.
  - Chiffres et seuils #0, #2, #5 et #6 : leurs chiffres stables sont repris par les cartes qui portent la règle (k06, k07, k17, k18, k30, k35). Chiffres et seuils #3 et #4 sont millésimés : le contrat leur interdit de donner une carte.

  Le jeu étant au plafond de 35 cartes et aucune carte n'étant fausse ou redondante au point d'être supprimée, ces items n'ont pas reçu de carte.
- **Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé.** Les chiffres présents sont stables et font partie d'une règle : 153 000 € (D. 612-5), cent salariés et six exercices (GIE), le cinquième et 40 % des droits de vote, le dixième du capital, quinze jours, sept ans, cinq ans d'emprisonnement et 75 000 € d'amende. Les dates citées sont celles de textes ou de leur entrée en vigueur.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | ue10-08-k03 | La question contenait la réponse (ressource « destinée à renforcer ses fonds propres » → « en fonds propres »). | Question portée sur la distinction fonds propres / fonds dédiés ; réponse reprenant Règles essentielles#2. |
| 1 | ue10-08-k04 | Contexte « association ou fondation » non porté par Définitions#2 ; exemples détachés de leur catégorie. | Question recadrée sur le règlement ANC n° 2018-06 ; chaque exemple rattaché au travail, aux biens ou aux services. |
| 1 | ue10-08-k06 | « plus de 153 000 € de subventions » au lieu du « montant global supérieur à 153 000 € » de la fiche. | Texte de la fiche repris. |
| 1 | ue10-08-k11 | Les allègements du régime réel simplifié étaient présentés comme des obligations, alors que la fiche dit « ils peuvent ». | Réponse formulée en facultés. |
| 1 | ue10-08-k17 | La question portait sur le chiffre (« à partir de quelle fraction ») et non sur la règle. | Question sur la condition de la présomption d'influence notable ; base Définitions#3 et Règles essentielles#10. |
| 1 | ue10-08-k19 | Les exemptions de Règles essentielles#9 étaient ignorées. | Question « sont en principe tenues » ; réponse « sauf exemption (notamment…) » ; base Règles essentielles#8 et #9. |
| 1 | ue10-08-k21 | Notion de grand groupe incomplète (deux des trois critères). | Critères ajoutés ; « entité d'intérêt public » au singulier. |
| 2 | ue10-08-k08 | La question contenait la réponse (« reddition de comptes »). | Question sur l'obligation d'information des associés (C. civ., art. 1856). |
| 2 | ue10-08-k09 | Question ambiguë (« effet de l'option ») et EARL omise. | Question sur les conséquences fiscales de l'option pour l'assimilation à une EURL ou à une EARL. |
| 2 | ue10-08-k12 | Option de l'article 93 A présentée comme ouverte à tous les titulaires de BNC ; formulation éloignée de la fiche. | Champ délimité à la déclaration contrôlée ; réponse reprenant la fiche (créances acquises, dépenses engagées, option avant le 1er février). |
| 2 | ue10-08-k31 (supprimée, passe antérieure interrompue) | Suite de la procédure d'alerte, en partie redondante avec k30. | Suppression confirmée ; identifiant laissé vide. |
| 2 | ue10-08-k36 (ajoutée, passe antérieure interrompue) | Règles essentielles#11 (référentiel des comptes consolidés) sans carte. | Carte IFRS / règlement ANC n° 2020-01 (L. 233-24), relue et jugée fidèle. |
| 3 | ue10-08-k14 | La question admettait une autre réponse juste (le contrat du groupement peut prévoir un commissaire aux comptes). | Question limitée aux cas où le commissaire aux comptes « doit » contrôler les comptes. |
| 3 | ue10-08-k22 | Question au singulier pour trois méthodes attendues. | « Quelles méthodes… respectivement au contrôle exclusif, au contrôle conjoint et à l'influence notable ? » |
| 3 | ue10-08-k09 | Après la suppression de k10, Ce qui a changé récemment#2 n'était plus couvert. | Base [Règles essentielles#3, Ce qui a changé récemment#2]. |
| 3 | ue10-08-k10 (supprimée) | Carte fidèle (extinction de l'EIRL), supprimée pour libérer une place sous le plafond de 35 cartes. | Identifiant laissé vide. |
| 3 | ue10-08-k37 (ajoutée) | Règles essentielles#14 (NEP 500, éléments probants) sans carte. | Carte : éléments suffisants (quantité) et appropriés (qualité : fiabilité et pertinence) ; à défaut, réserve ou impossibilité de certifier. |

## Corrections de la relecture d'exactitude

### Seconde relecture d'exactitude (la présente)

| cible | problème | correction | source |
|---|---|---|---|
| ue10-08-k18 | La question (« Pour qualifier le contrôle exclusif en consolidation, quelle est la portée de la détention de la majorité des droits de vote ? ») ne disait pas quel texte fonde la réponse « simple présomption ». Or, selon l'article L. 233-16, II, 1° du Code de commerce, le contrôle exclusif « résulte » de la détention de la majorité des droits de vote, comme le dit k15. Les deux cartes paraissaient se contredire, et « elle caractérise le contrôle exclusif » était une réponse juste au regard du Code. La présomption réfragable (pacte d'actionnaires) vient du règlement ANC n° 2020-01. | Question : « Selon le règlement ANC n° 2020-01, quelle est la portée de la détention de la majorité des droits de vote pour qualifier le contrôle exclusif ? ». Réponse, base, `src` et `url` inchangés. | C. com., art. L. 233-16, II ; règlement ANC n° 2020-01 (citation de Points de vigilance#1) |
| ue10-08-k36 | « Quels référentiels comptables une société peut-elle appliquer pour établir ses comptes consolidés ? » laissait croire à un libre choix entre IFRS et règlement ANC n° 2020-01. Or le règlement (CE) n° 1606/2002 (art. 4) impose les IFRS adoptées par l'Union aux comptes consolidés des sociétés dont les titres sont admis aux négociations sur un marché réglementé : la réponse n'était vraie que pour les autres sociétés, sans le dire. L'article L. 233-24 n'organise que la dispense qui en découle. | Question recentrée sur l'objet de l'article : « Selon l'article L. 233-24 du Code de commerce, quel référentiel comptable dispense une société de certaines règles de consolidation de ce code ? ». Réponse : les IFRS adoptées par règlement de la Commission européenne (règlement (CE) n° 1606/2002), dont l'application dispense des articles L. 233-17-2 à L. 233-23 et L. 233-25 ; à défaut, le règlement ANC n° 2020-01. 49 mots. Base, `src` et `url` inchangés. | C. com., art. L. 233-24 (recherche 3) ; règlement (CE) n° 1606/2002, art. 4 ; Règles essentielles#11 |
| ue10-08-k26 | « impossibilité : limitations trop étendues ou multiples incertitudes » ne donnait pas le critère de la NEP 700 qui sépare la réserve pour limitation de l'impossibilité de certifier : une limitation dont l'incidence ne peut être clairement circonscrite. Un correcteur du DCG attend ce critère, symétrique de celui du refus. | « impossibilité : limitation dont les effets ne peuvent être circonscrits, ou multiples incertitudes ». La carte reste fidèle à Règles essentielles#13 (réserve lorsque les effets sont clairement circonscrits). 55 mots. | NEP 700 (formes de l'opinion) ; Règles essentielles#13 |
| ue10-08-k01 | « le bien étant repris par l'apporteur lorsque survient l'événement prévu » s'écartait du règlement n° 2018-06, qui fait jouer la reprise quand la condition cesse d'être remplie : « Ce bien est repris par l'apporteur lorsque la condition n'est plus remplie par le bénéficiaire. » | « le bien étant repris par l'apporteur lorsque la condition n'est plus remplie par le bénéficiaire (par exemple en cas de cessation de l'activité concernée ou de dissolution de l'entité) ». 56 mots. Question, base, `src` et `url` inchangés. | Règlement ANC n° 2018-06, art. 131-2 (recherche 2) ; Définitions#0 |

Les 31 autres cartes ont été jugées exactes au 16 octobre 2026, sans ambiguïté qui justifie une retouche. Points contrôlés :

- **Secteur non lucratif et entités spécifiques.** k02 et k03 : fonds dédiés (comptes 689 et 789) et frontière avec les fonds propres ; le règlement ANC n° 2024-07 crée une rubrique « autres fonds propres » sans reclasser les fonds propres avec droit de reprise (recherche 2). k04 et k05 : contributions volontaires en nature, classe 8, comptes 86 et 87. k06 et k07 : C. com., art. L. 612-1, L. 612-4, L. 612-5, R. 612-1 et D. 612-5. k08 : C. civ., art. 1856. k09 : CGI, art. 1655 sexies (option irrévocable valant option pour l'IS, renonciation à l'IS possible jusqu'au cinquième exercice). k11 : C. com., art. L. 123-25 à L. 123-27. k12 : CGI, art. 93 A. k13 et k14 : GIE, C. com., art. L. 251-1 et L. 251-12.
- **Consolidation.** k15, k16 et k17 : C. com., art. L. 233-16 et L. 233-17-2. k19, k20 et k21 : C. com., art. L. 233-17 dans sa rédaction applicable depuis le 1er janvier 2025 (sous-groupe sauf opposition du dixième du capital ; ensemble ne constituant pas un grand groupe au sens de L. 230-2 lorsqu'aucune société ne relève de L. 123-16-2), confirmé par la recherche 1. k22 : L. 233-18 ; en règles françaises, le contrôle conjoint relève toujours de l'intégration proportionnelle. k23 et k24 : pourcentages de contrôle et d'intérêt (règlement ANC n° 2020-01).
- **Audit et fiscalité.** k25 : L. 821-53. k27 : NEP 320. k28 : cadre de référence de l'AMF. k29 : NEP 265. k30 : L. 234-1 et R. 234-2. k32 : révélation des faits délictueux et sanction (cinq ans, 75 000 €). k33 : ordonnance n° 2023-1142 (recodification au 1er janvier 2024, H3C devenu H2A). k34 : CGI, ann. III, art. 38 quater. k35 : CGI, art. 38, 4 bis. k37 : NEP 500.

**Doublons.** Plusieurs cartes se recouvrent en partie, mais chacune pose une question distincte : k15 et k18 (les trois sources du contrôle exclusif selon le Code, puis la portée de la majorité selon le règlement ANC n° 2020-01) ; k17 et k22 (présomption d'influence notable, puis les trois méthodes) ; k23 et k24 (deux définitions de Définitions#4) ; k02 et k03 (définition des fonds dédiés, puis frontière avec les fonds propres) ; k19, k20 et k21 (principe, exemption de sous-groupe, exemption de taille) ; k25 et k33 (objet de la certification, puis recodification). Aucune carte triviale ou purement mécanique n'a été relevée. Aucune n'a été supprimée.

### Première relecture d'exactitude (antérieure)

| cible | problème | correction | source |
|---|---|---|---|
| ue10-08-k20 | La réponse se présentait comme exhaustive. Or l'article L. 233-17 exclut aussi de l'exemption de sous-groupe la société qui a émis des titres de créances négociables, pas seulement des valeurs mobilières admises aux négociations sur un marché réglementé. La fiche omet ce cas. | Réponse ouverte par « Notamment ». La carte reste fidèle à Règles essentielles#9 sans se dire complète. | C. com., art. L. 233-17 ; Règles essentielles#9 |
| ue10-08-k21 | « aucune de ses sociétés n'est une entité d'intérêt public de l'article L. 123-16-2 » : l'article L. 123-16-2 énumère des catégories, il ne définit pas les entités d'intérêt public. | « lorsqu'aucune de ses sociétés ne relève des catégories de l'article L. 123-16-2 (entités d'intérêt public) », formulation de la fiche et de la loi. | C. com., art. L. 233-17 ; Règles essentielles#9 |
| ue10-08-k35 | « Sont exclues les erreurs intervenues plus de sept ans avant… » pouvait se lire « exclues de la correction », soit l'inverse de la règle. | « La règle ne s'applique pas (la correction reste possible) aux erreurs intervenues plus de sept ans avant l'ouverture de cet exercice… » | CGI, art. 38, 4 bis ; Règles essentielles#19 |
| ue10-08-k24 | « produit des pourcentages de capital le long de chaque chaîne » laissait croire à un seul produit, alors que les chaînes multiples s'additionnent. | « …le long de chaque chaîne de participations, les chaînes s'additionnant ». | Règlement ANC n° 2020-01 ; Points de vigilance#0 |
| ue10-08-k33 | La question « Qu'a changé l'ordonnance n° 2023-1142… ? » admettait d'autres réponses justes (transposition de la directive CSRD, certification des informations en matière de durabilité). | Question resserrée sur les changements de codification et d'autorité de supervision. | Ce qui a changé récemment#0 ; Points de vigilance#5 |
| ue10-08-k03 | « Quelle ressource est inscrite en fonds propres… plutôt qu'en fonds dédiés ? » admettait d'autres réponses justes (apports des membres, legs). | Question limitée aux ressources reçues d'un tiers financeur selon le règlement ANC n° 2018-06. | Règlement ANC n° 2018-06 ; Règles essentielles#2 |

## Recherches

### Seconde relecture d'exactitude (la présente)

Trois recherches WebSearch, restreintes aux sites officiels :

1. **legifrance.gouv.fr : « Code de commerce article L. 233-17 exemptées comptes consolidés "grand groupe" L. 230-2 ».**
   - L'article L. 233-17, dans sa version en vigueur depuis le 1er janvier 2025, prévoit deux exemptions : 1° la société contrôlée par une entreprise qui l'inclut dans ses comptes consolidés publiés, sauf opposition d'associés représentant au moins le dixième du capital ; 2° l'ensemble qui ne constitue pas un grand groupe au sens de l'article L. 230-2, lorsqu'aucune de ses sociétés ne relève des catégories de l'article L. 123-16-2.
   - Cela confirme k19, k20 et k21, y compris la date du 1er janvier 2025.
   - Source : [C. com., art. L. 233-17](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000030927218).
2. **anc.gouv.fr, legifrance.gouv.fr : « règlement ANC 2024-07 règlement 2018-06 fonds propres avec droit de reprise dettes ».**
   - Le règlement n° 2024-07 du 6 décembre 2024 fait des « autres fonds propres » une rubrique à part entière du passif et modifie en conséquence le modèle de bilan du règlement n° 2018-06 ; rien n'indique qu'il reclasse les fonds propres avec droit de reprise, qui restent dans les fonds propres.
   - Le règlement n° 2018-06 définit les fonds propres avec droit de reprise comme la mise à disposition conditionnelle d'un bien ou de numéraire : « Ce bien est repris par l'apporteur lorsque la condition n'est plus remplie par le bénéficiaire. » La condition porte sur la cessation de l'activité concernée ou sur la dissolution de l'entité.
   - Conséquences : k01 retouchée (formulation de la reprise) ; k03 confirmée.
   - Sources : [règlement ANC n° 2024-07, version commentée](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2024/R2024-07/REGLT_2024_07_version-commentee-def.pdf), [règlement ANC n° 2018-06](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2018/Reglt_2018_06/Reglt_2018-06_Association.pdf).
3. **legifrance.gouv.fr : « Code de commerce article L233-24 normes comptables internationales dispensées de se conformer aux règles comptables comptes consolidés ».**
   - Dans sa rédaction issue de l'ordonnance n° 2015-900 (en vigueur depuis le 1er janvier 2016), l'article L. 233-24 dispense les sociétés qui appliquent les normes comptables internationales adoptées par règlement de la Commission européenne des règles des articles L. 233-17-2 à L. 233-23 et L. 233-25 (avant 2016 : L. 233-18 à L. 233-23).
   - Cela confirme la liste d'articles de k36, dont la question a été recentrée sur cette dispense.
   - Source : [C. com., section des comptes consolidés (art. L. 233-16 et s.)](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000005634379/LEGISCTA000006161295/).

### Première relecture d'exactitude (antérieure)

1. anc.gouv.fr : règlement ANC n° 2024-07 et fonds propres avec droit de reprise. Résultat : définition du règlement n° 2018-06 maintenue ; date d'application des exercices ouverts à compter du 1er janvier 2025 (voir « Points à reprendre dans la fiche », point 5).
2. legifrance.gouv.fr : article L. 233-17 (exemptions, grand groupe, L. 123-16-2, dixième du capital). Résultat : k19 et k21 confirmées, formulation de k21 retouchée.
3. legifrance.gouv.fr : exclusion de l'exemption de sous-groupe (« valeurs mobilières admises aux négociations sur un marché réglementé ou des titres de créances négociables »). Résultat : k20 corrigée.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Les points 1 à 3 viennent de la présente relecture ; les points 4 à 6, de la première relecture d'exactitude ; les points 7 à 10, des relectures de fidélité. Tous restent d'actualité.

1. **Règles essentielles#11 (référentiel des comptes consolidés).** L'item présente les IFRS comme une simple faculté assortie d'une dispense. Il faudrait préciser que les normes IFRS adoptées par l'Union européenne sont **obligatoires** pour les comptes consolidés des sociétés dont les titres sont admis aux négociations sur un marché réglementé (règlement (CE) n° 1606/2002, art. 4) et optionnelles pour les autres ; l'article L. 233-24 n'organise que la dispense des règles françaises. La carte k36 a été recentrée sur cette dispense.
2. **Règles essentielles#13 (formes de l'opinion, NEP 700).** « Impossibilité de certifier en cas de limitations trop étendues » : le critère de la NEP 700 est que l'incidence des limitations sur les comptes ne peut être clairement circonscrite (les multiples incertitudes visées étant, elles aussi, celles dont les incidences ne peuvent être circonscrites). La carte k26 reprend ce critère.
3. **Définitions#0 (fonds propres avec droit de reprise).** « Lorsque survient l'événement prévu » est à aligner sur le texte du règlement n° 2018-06 : « lorsque la condition n'est plus remplie par le bénéficiaire » (recherche 2). La carte k01 reprend le texte.
4. **Règles essentielles#9 (et l'entrée « textes » L. 233-17).** L'exemption de la société contrôlée incluse dans des comptes consolidés publiés est exclue lorsqu'elle a émis des valeurs mobilières admises aux négociations sur un marché réglementé **ou des titres de créances négociables**. L'item ne mentionne que le premier cas. La carte k20 dit « notamment ».
5. **Ce qui a changé récemment#5 (et l'entrée « textes » du règlement ANC n° 2018-06).** Le site de l'ANC indique que le règlement n° 2024-07 s'applique aux exercices ouverts à compter du **1er janvier 2025**, et non 2026. La date d'homologation (« arrêté du 26 décembre 2025 ») est donc à vérifier. Ce constat rejoint celui de la relecture de ue10-06. Aucune carte ne repose sur cet item.
6. **Points de vigilance#0 (et Définitions#4).** Préciser que le pourcentage d'intérêt est la **somme** des produits obtenus sur chaque chaîne lorsqu'il en existe plusieurs.
7. **Chiffres et seuils#3 (grands groupes, millésimé 2026), à vérifier.** La fiche donne 30 000 000 € de total du bilan et 60 000 000 € de chiffre d'affaires net, alors que la directive déléguée (UE) 2023/2775 porte les seuils des grands groupes à 25 000 000 € et 50 000 000 €. Aucune carte n'utilise ces chiffres ; à confirmer sur l'article D. 230-2.
8. **Règles essentielles#18 et Chiffres et seuils#6.** Les items sont marqués « stable », mais le délai fiscal de six ans y est donné « LPF, rédaction en vigueur en 2026 ». Il faudrait séparer la règle stable (dix ans, C. com., art. L. 123-22) du délai fiscal daté, ou marquer l'item millésimé.
9. **Règles essentielles#15 (procédure d'alerte).** « Une assemblée générale est convoquée » ne dit pas par qui. Le commissaire aux comptes présente son rapport spécial à la prochaine assemblée ou, en cas d'urgence, à une assemblée qu'il convoque lui-même (L. 234-1).
10. **Définitions#6 (contrôle interne).** L'item annonce « cinq composantes intégrées, dont » quatre seulement. La cinquième (les activités de contrôle) manque.

## Classement des exercices

Le classement automatique des exercices du chapitre (QCM, QCM multiples et classements) donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 21 | oui |
| `calcul` | 0 | non |
| `chiffre` | 0 | non |

Les classeurs n'ont relevé aucun désaccord. Les 21 exercices, tous de nature `notion`, entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable.
