# Cartes de notions : ue10-08 (Entités spécifiques, groupes et contrôle des comptes)

Date : 16 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-08.fiche.json` (maj du 15 octobre 2026), selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`) ; `src` et `url` sont copiés depuis le premier de ces items.
2. **Relectures de fidélité à la fiche.** Trois passes successives, sans recherche web, ont comparé chaque carte au texte (`t`) et à la citation (`cite`) de ses items de base. Elles ont corrigé 13 cartes. Une passe antérieure interrompue avait supprimé k31 et ajouté k36 ; la troisième passe a supprimé k10 et ajouté k37 pour couvrir la NEP 500. Les identifiants k10 et k31 restent vides, sans renumérotation.
3. **Relecture d'exactitude (la présente).** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 16 octobre 2026 : Code de commerce, Code civil, CGI et BOFiP, règlements ANC n° 2018-06 et n° 2020-01, NEP ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a fait 3 recherches, restreintes à anc.gouv.fr et à legifrance.gouv.fr (voir « Recherches »), et corrigé 6 cartes. Elle n'a rien supprimé ni ajouté.
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

  Le jeu étant au plafond de 35 cartes et aucune carte n'étant fausse au point d'être supprimée, ces items n'ont pas reçu de carte.
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

| cible | problème | correction | source |
|---|---|---|---|
| ue10-08-k20 | La réponse se présentait comme exhaustive. Or l'article L. 233-17 exclut aussi de l'exemption de sous-groupe la société qui a émis des titres de créances négociables, pas seulement des valeurs mobilières admises aux négociations sur un marché réglementé. La fiche omet ce cas. | Réponse ouverte par « Notamment » : « Notamment lorsque des actionnaires ou associés représentant au moins le dixième de son capital s'opposent à l'exemption, ou lorsqu'elle a émis des titres admis aux négociations sur un marché réglementé. » La carte reste fidèle à Règles essentielles#9 sans se dire complète. Question, base, `src` et `url` inchangés. | C. com., art. L. 233-17 (recherches 2 et 3) ; Règles essentielles#9 |
| ue10-08-k21 | « aucune de ses sociétés n'est une entité d'intérêt public de l'article L. 123-16-2 » : l'article L. 123-16-2 énumère des catégories (établissements de crédit, assurances, sociétés cotées…), il ne définit pas les entités d'intérêt public. | « lorsqu'aucune de ses sociétés ne relève des catégories de l'article L. 123-16-2 (entités d'intérêt public) », formulation de la fiche et de la loi. 58 mots. | C. com., art. L. 233-17 (recherche 2) ; Règles essentielles#9 |
| ue10-08-k35 | « Sont exclues les erreurs intervenues plus de sept ans avant… » pouvait se lire « exclues de la correction », soit l'inverse de la règle : ces erreurs échappent à l'intangibilité et peuvent être corrigées. | « La règle ne s'applique pas (la correction reste possible) aux erreurs intervenues plus de sept ans avant l'ouverture de cet exercice, aux amortissements excessifs… ni aux dépenses déduites en charges qui auraient dû être immobilisées. » 68 mots. | CGI, art. 38, 4 bis ; Règles essentielles#19 |
| ue10-08-k24 | « produit des pourcentages de capital le long de chaque chaîne » laissait croire à un seul produit. Lorsque le groupe détient une société par plusieurs chaînes (directe et indirecte), le pourcentage d'intérêt est la somme des produits obtenus sur chaque chaîne. | « produit des pourcentages de capital le long de chaque chaîne de participations, les chaînes s'additionnant ». Aucun calcul n'est demandé. 59 mots. | Règlement ANC n° 2020-01 ; Points de vigilance#0 |
| ue10-08-k33 | La question « Qu'a changé l'ordonnance n° 2023-1142… pour le commissariat aux comptes ? » admettait d'autres réponses justes : l'ordonnance transpose la directive CSRD et ouvre la certification des informations en matière de durabilité aux commissaires aux comptes et aux organismes tiers indépendants. | Question resserrée : « Quels changements de codification et d'autorité de supervision du commissariat aux comptes l'ordonnance n° 2023-1142 du 6 décembre 2023 a-t-elle opérés ? ». La date du 1er janvier 2024 passe au verso (69 mots). Base inchangée. | Ce qui a changé récemment#0 ; Points de vigilance#5 |
| ue10-08-k03 | « Quelle ressource est inscrite en fonds propres… plutôt qu'en fonds dédiés ? » admettait d'autres réponses justes, comme les apports des membres ou les legs. | Question limitée aux ressources reçues d'un tiers financeur selon le règlement ANC n° 2018-06. Le verso précise « avec ou sans droit de reprise » (50 mots). | Règlement ANC n° 2018-06 (recherche 1) ; Règles essentielles#2 |

Les 29 autres cartes ont été jugées exactes au 16 octobre 2026, sans ambiguïté qui justifie une retouche. Les points contrôlés sont les suivants.

**Secteur non lucratif et entités spécifiques**
- k01 et k02 : fonds propres avec ou sans droit de reprise, fonds dédiés et comptes 689 et 789. La définition est confirmée par le recueil du secteur non lucratif 2026 (recherche 1).
- k04 et k05 : contributions volontaires en nature, classe 8, comptes 86 et 87.
- k06 et k07 : C. com., art. L. 612-1, L. 612-4, L. 612-5, R. 612-1 et D. 612-5.
- k08 : C. civ., art. 1856.
- k09 : CGI, art. 1655 sexies. L'assimilation est irrévocable, mais l'option pour l'IS peut être abandonnée jusqu'au cinquième exercice (art. 239).
- k11 : C. com., art. L. 123-25 à L. 123-27.
- k12 : CGI, art. 93 A.
- k13 et k14 : GIE, C. com., art. L. 251-1 et L. 251-12.

**Consolidation**
- k15, k16, k17 et k18 : C. com., art. L. 233-16 et L. 233-17-2, et présomption réfragable du règlement ANC n° 2020-01.
- k19 : L. 233-16. La réponse dit « notamment » pour les exemptions.
- k22 : L. 233-18. En règles françaises, le contrôle conjoint relève toujours de l'intégration proportionnelle.
- k23 : pourcentage de contrôle.
- k36 : L. 233-24. Les IFRS sont obligatoires pour les sociétés cotées en vertu du règlement (CE) n° 1606/2002, ce que la carte ne contredit pas.

**Audit et fiscalité**
- k25 : L. 821-53.
- k26 : NEP 700.
- k27 : NEP 320.
- k28 : cadre de référence de l'AMF.
- k29 : NEP 265.
- k30 : L. 234-1.
- k32 : révélation des faits délictueux et sanction.
- k34 : CGI, ann. III, art. 38 quater.
- k37 : NEP 500.

**Doublons.** Plusieurs cartes se recouvrent en partie, mais chacune pose une question distincte :
- k15 et k18 : les trois sources du contrôle exclusif, puis la portée de la présomption ;
- k17 et k22 : la présomption d'influence notable, puis les trois méthodes ;
- k23 et k24 : deux définitions de Définitions#4 ;
- k02 et k03 : la définition des fonds dédiés, puis la frontière avec les fonds propres ;
- k25 et k33 : l'objet de la certification, puis la recodification.

Aucune n'a été supprimée.

## Recherches

Trois recherches WebSearch, restreintes aux sites officiels :

1. **anc.gouv.fr : « règlement ANC 2024-07 secteur non lucratif fonds propres avec droit de reprise dettes ».**
   - Le règlement ANC n° 2024-07, adopté le 6 décembre 2024, modifie notamment le règlement n° 2018-06. Il s'applique aux exercices ouverts à compter du 1er janvier 2025.
   - Il fait des « autres fonds propres » une rubrique distincte des fonds propres et des dettes, sans toucher à la définition des fonds propres avec droit de reprise. Le recueil 2026 maintient cette définition : mise à disposition conditionnelle, reprise lors de la cessation de l'activité concernée ou de la dissolution.
   - k01 et k03 sont donc confirmées ; la date d'application de la fiche est contredite (voir « Points à reprendre dans la fiche »).
   - Sources : [Règlement ANC n° 2024-07](https://www.anc.gouv.fr/reglement-anc-ndeg2024-07), [rapport d'activité 2024 de l'ANC](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Rapports/ANC-Rapport-activite-2024.pdf), [recueil du secteur non lucratif 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/Recueil-non-lucratif-2026.pdf).
2. **legifrance.gouv.fr : « article L233-17 code de commerce exemption comptes consolidés grand groupe L. 230-2 L. 123-16-2 dixième capital ».**
   - L'article L. 233-17 dans sa rédaction issue de l'ordonnance n° 2023-1142, applicable depuis le 1er janvier 2025, prévoit deux exemptions.
   - 1° : la société contrôlée incluse dans les comptes consolidés publiés d'une entreprise, sauf opposition d'associés représentant au moins le dixième du capital.
   - 2° : l'ensemble qui ne constitue pas un grand groupe au sens de L. 230-2, lorsqu'aucune société ne relève des catégories de L. 123-16-2.
   - Cela confirme k19 et k21 (date du 1er janvier 2025) et a conduit à retoucher la formulation de k21.
   - Source : [C. com., art. L. 233-17](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048535260).
3. **legifrance.gouv.fr : phrase exacte « à l'exception de celles qui ont émis des valeurs mobilières admises aux négociations sur un marché réglementé ou des titres de créances négociables ».**
   - L'exclusion de l'exemption de sous-groupe porte sur ces deux catégories de titres.
   - k20 est corrigée et Règles essentielles#9 signalée.
   - Source : [C. com., art. L. 233-17](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048535260).

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Les points 1 à 3 sont nouveaux ; les points 4 à 7 viennent des relectures de fidélité et restent d'actualité.

1. **Règles essentielles#9 (et l'entrée « textes » L. 233-17).** L'exemption de la société contrôlée incluse dans des comptes consolidés publiés est exclue lorsqu'elle a émis des valeurs mobilières admises aux négociations sur un marché réglementé **ou des titres de créances négociables** (L. 233-17, recherche 3). L'item ne mentionne que le premier cas. La carte k20 dit désormais « notamment ».
2. **Ce qui a changé récemment#5 (et l'entrée « textes » du règlement ANC n° 2018-06).** Le site de l'ANC (recherche 1) indique que le règlement n° 2024-07 s'applique aux exercices ouverts à compter du **1er janvier 2025**, et non 2026. La date d'homologation (« arrêté du 26 décembre 2025 ») est donc à vérifier, puisqu'elle serait postérieure à la date d'application. Ce constat rejoint celui de la relecture de ue10-06. Aucune carte ne repose sur cet item.
3. **Points de vigilance#0 (et Définitions#4).** « Produit des pourcentages de capital le long de chaque chaîne » : il faudrait préciser que le pourcentage d'intérêt est la **somme** des produits obtenus sur chaque chaîne lorsqu'il en existe plusieurs.
4. **Règles essentielles#18 et Chiffres et seuils#6.** Les items sont marqués « stable », mais le délai fiscal de six ans y est donné « LPF, rédaction en vigueur en 2026 ». Il faudrait séparer la règle stable (dix ans, C. com., art. L. 123-22) du délai fiscal daté, ou marquer l'item millésimé.
5. **Règles essentielles#15 (procédure d'alerte).** « Une assemblée générale est convoquée » ne dit pas par qui. Le commissaire aux comptes présente son rapport spécial à la prochaine assemblée ou, en cas d'urgence, à une assemblée qu'il convoque lui-même (L. 234-1).
6. **Définitions#6 (contrôle interne).** L'item annonce « cinq composantes intégrées, dont » quatre seulement. La cinquième (les activités de contrôle) manque.
7. **Chiffres et seuils#3 (grands groupes, millésimé 2026), à vérifier.** La fiche donne 30 000 000 € de total du bilan et 60 000 000 € de chiffre d'affaires net. La directive déléguée (UE) 2023/2775, que le décret n° 2024-152 transpose, porte les seuils des grandes entreprises et des grands groupes à 25 000 000 € et 50 000 000 €. Ce point n'a pas été vérifié par une recherche (plafond de trois atteint) et aucune carte n'utilise ces chiffres ; il est à confirmer sur l'article D. 230-2.

## Classement des exercices

Le classement automatique des exercices du chapitre (QCM, QCM multiples et classements) donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 21 | oui |
| `calcul` | 0 | non |
| `chiffre` | 0 | non |

Les classeurs n'ont relevé aucun désaccord. Les 21 exercices, tous de nature `notion`, entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable.
