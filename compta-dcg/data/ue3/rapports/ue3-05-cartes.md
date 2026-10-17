# Cartes de notions : ue3-05 (Relations collectives : représentation, négociation, conflits)

16 octobre 2026. Fichier : `data/ue3/ue3-05.cartes.json`. Fiche de référence : `data/ue3/ue3-05.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`) dont elle reprend `src` et `url`. Des passes antérieures ont supprimé k11 (masse salariale du CSE), k26 (révision d'un accord d'entreprise), k29 (valeur du droit de grève) et k35 (parties à la convention collective). Ces identifiants ne sont pas réutilisés.
2. **Relecture de fidélité.** Trois passes successives ont contrôlé les cartes au regard de la fiche seule, sans recherche web :
   - 1re passe : 10 corrections et 2 ajouts (k34, k35) ;
   - 2e passe : 5 corrections ;
   - 3e passe : 3 corrections.

   Aucune de ces passes n'a supprimé de carte. Le détail figure dans le tableau ci-dessous.
3. **Relecture d'exactitude** (la présente passe). Les 35 cartes ont été contrôlées au regard du droit en vigueur au 16 octobre 2026 : Code du travail, Préambule de 1946, lois n° 2023-1107, 2025-989 et 2026-403, jurisprudence de la chambre sociale. Les points vérifiés :
   - l'exactitude de chaque réponse, y compris les cas particuliers non dits ;
   - l'unicité de la réponse attendue par un correcteur du DCG ;
   - l'absence de doublon, de carte triviale et de chiffre millésimé.

   Bilan : 10 cartes corrigées, 1 supprimée (k37), 1 ajoutée (k40).
4. **Recherches.** 3 recherches WebSearch, limitées à legifrance.gouv.fr (voir « Recherches faites »).

`node validate.js data/ue3/ue3-05.cartes.json` : ✓ (35 cartes, 8 déf.).

## Bilan

- **35 cartes**, soit le plafond du contrat : 8 de définition (`def` : k01, k06, k07, k13, k15, k16, k25, k27) et 27 de compréhension (`comp`). Les identifiants k11, k26, k29, k35 et k37 restent libres et ne seront pas réutilisés ; le prochain identifiant disponible est k41.
- **Définitions** : les 6 items ont chacun au moins une carte (k01 ; k02 et k36 ; k15 ; k16 ; k07 et k08 ; k30).
- **Règles essentielles** : 16 items sur 17 ont une carte. #9 (révision) a retrouvé une carte avec k40. Restent sans carte :
  - **#12** (moyens du CSE : heures de délégation, subvention de fonctionnement, CSSCT à partir de 300 salariés) ;
  - deux points d'items couverts : les parties à la convention ou à l'accord (Définitions#2, 2e phrase) et la charge de la preuve pesant sur celui qui conteste un accord (Règles essentielles#16, 1re phrase).
- **Ce qui a changé récemment** : 5 items sur 6 ont une carte (#0 : k07 ; #2 : k33 ; #3 : k08 et k22 ; #4 : k12 ; #5 : k23). **#1** (conservation du document unique d'évaluation des risques pendant quarante ans) n'a pas de carte : il relève de la santé au travail plus que des relations collectives.
- **Points de vigilance** : les 6 items ont une carte (k03, k28, k05, k38, k39, k14).
- **Chiffres et seuils** : seul #1 est cité dans `base` (k03). Les seuils et délais stables des items #0, #2, #3 et #4 figurent déjà dans les cartes tirées des Règles essentielles (k04, k07, k17, k18, k22, k24, k28). Les taux de subvention du CSE n'ont pas de carte.
- **Doublons.** Deux paires de cartes découpent un même item en deux listes complémentaires :
  - **k02 et k36** : les sept critères de représentativité. Ce découpage est conservé, car une liste de sept éléments se retient mal sur une seule carte.
  - **k34 et k37** : les thèmes de la négociation de branche. Chacune des deux cartes répétait la réponse de l'autre, et k37 était devenue incomplète (voir ci-dessous). k37 est supprimée, k34 conservée.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | k02 | La carte ne donnait que 4 critères sur 7. Sa question citait les 3 autres, qui formaient la réponse de k03 : les deux cartes se donnaient mutuellement la réponse. | La question porte sur tous les critères, la réponse donne les sept critères cumulatifs, et le type passe à `comp`. Une passe ultérieure a de nouveau réparti les critères entre k02 et k36. |
| 1 | k03 | La carte doublait k02 ; il manquait « quel que soit le nombre de votants ». | La carte est recentrée sur l'audience : 10 % dans l'entreprise, 8 % dans la branche et au niveau national et interprofessionnel. La décision du Conseil constitutionnel est ajoutée. Base : Chiffres et seuils#1 et Points de vigilance#0. |
| 1 | k04 | Question mal formulée (« Parmi qui »). | « Parmi quelles personnes… ». |
| 1 | k07 | « du personnel » ajouté au texte de la fiche. | « L'institution représentative unique ». |
| 1 | k14 | Le montant de l'amende pour entrave au fonctionnement manquait. | Ajout de « de 7 500 € ». |
| 1 | k17 | Une condition était oubliée : huit jours après la demande, d'autres signatures n'ont pas permis d'atteindre 50 %. | La réponse est réécrite et donne toute la procédure de consultation des salariés. |
| 1 | k19 | « Employeur dépourvu de délégué syndical ». | « Entreprise dépourvue de délégué syndical ». |
| 1 | k23 | Il manquait une condition de l'arrêt : l'APC modifie le contrat. | Ajout de « et modifiant son contrat ». |
| 1 | k28 | Le délai visé par l'exception n'était pas clair. | « Le délai de deux mois ne s'applique pas… ». |
| 1 | k29 | La question appelait aussi une définition de la grève, que la fiche ne donne pas. | La question porte sur la valeur juridique du droit de grève. La carte a ensuite été supprimée lors d'une passe antérieure. |
| 1 | k34 (ajout) | Règles essentielles#6 n'avait pas de carte. | La carte porte sur les négociations périodiques de branche. |
| 1 | k35 (ajout) | Les parties à la convention collective (Définitions#2) n'avaient pas de carte. | Carte `def` ajoutée, puis supprimée lors d'une passe antérieure. |
| 2 | k12 | La question admettait plusieurs réponses justes. | « Qu'est-ce qui remplace l'information directe des salariés… ? ». |
| 2 | k17 | L'assiette du seuil de 30 % n'était pas précisée. | « …des suffrages exprimés en faveur des organisations représentatives ». |
| 2 | k19 | La réponse ne disait pas qui propose l'accord dans les entreprises de moins de onze salariés. | « L'employeur peut proposer un projet d'accord ratifié à la majorité des deux tiers du personnel ». |
| 2 | k20 | « Dans quelles matières l'accord d'entreprise prévaut-il ? » admettait plusieurs réponses. | La question porte sur l'articulation des trois blocs, et la réponse les reprend tous les trois. |
| 2 | k21 | Le champ de la question n'était pas fixé (risque de confusion avec k22), et la réponse ne commençait pas par l'essentiel. | La question vise les deux négociations communes, qui ouvrent désormais la réponse. |
| 3 | k38 | « Entre en vigueur un mois après » pouvait se lire comme une entrée en vigueur automatique. | « Il ne peut entrer en vigueur qu'un mois après… ». |
| 3 | k17 | « Puis, passé ce délai, par l'employeur » laissait croire que l'employeur demande toujours la consultation. | « …ou, passé ce délai, par l'employeur, sauf opposition de toutes ces organisations ». |
| 3 | k01 | Minuscule à « préambule ». | « Préambule de la Constitution de 1946 ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k04 | La carte présentait « ses adhérents ou ses anciens élus » comme seule solution subsidiaire. Or, dans sa version en vigueur depuis le 26 octobre 2025, L. 2143-3 prévoit d'abord la désignation parmi les autres candidats, et seulement à défaut parmi les adhérents ou les anciens élus. | Question : « En principe, parmi quelles personnes… ». Réponse : le principe des 10 %, puis « À défaut seulement, d'autres désignations sont possibles, notamment parmi ses adhérents ou ses anciens élus. » (49 mots). | C. trav., art. L. 2143-3 (modifié par la loi n° 2025-989) |
| k05 | Une autre réponse juste était possible : une convention ou un accord peut abaisser l'effectif à partir duquel des délégués syndicaux sont désignés. C'est une matière du bloc 2. | Question : « Quelle possibilité le Code du travail donne-t-il aux syndicats représentatifs pour disposer d'un délégué syndical dans un établissement de moins de cinquante salariés ? ». La réponse est inchangée. | C. trav., art. L. 2143-6 et L. 2253-2 |
| k06 | « Il ne peut pas négocier d'accords collectifs » était présenté comme absolu. Or, en l'absence de délégué syndical, le représentant de la section syndicale peut négocier et conclure un accord s'il est mandaté par son organisation. | « … ; en principe, il ne peut pas négocier d'accords collectifs. » | C. trav., art. L. 2142-1-1 et L. 2143-23 |
| k09 | « Quelles sont les attributions » appelait une liste complète. Or la délégation exerce aussi le droit d'alerte et réalise les enquêtes AT/MP. La formule « contribue à la santé et à la sécurité » abrégeait le texte, et celui-ci vise les réclamations « individuelles ou collectives ». | Question : « Quelles sont les principales attributions… ». Réponse : « Il présente à l'employeur les réclamations individuelles ou collectives des salariés et contribue à promouvoir la santé et la sécurité au travail. » | C. trav., art. L. 2312-5 |
| k20 | Dans le bloc 2, la carte donnait à la branche une primauté absolue lorsqu'elle le stipule. Or L. 2253-2 réserve, comme pour le bloc 1, le cas où l'accord d'entreprise assure des garanties au moins équivalentes. | « … ; dans ces deux blocs, sauf garanties au moins équivalentes de l'accord d'entreprise. » (49 mots). | C. trav., art. L. 2253-1 et L. 2253-2 |
| k24 | La survie d'un an et le maintien de la rémunération ne jouent que si la dénonciation émane de la totalité des signataires employeurs ou des signataires salariés. Une dénonciation partielle laisse l'accord en vigueur entre les autres signataires. | Question : « Que devient un accord collectif à durée indéterminée dénoncé par la totalité des signataires employeurs ou des signataires salariés ? ». La réponse est inchangée. | C. trav., art. L. 2261-10, L. 2261-11 et L. 2261-13 |
| k25 | La définition confondait la mise en cause (une situation) avec son effet, et la liste des causes était présentée comme fermée, alors que le texte dit « notamment ». | « La remise en cause de son application dans une entreprise, en raison notamment d'une fusion, d'une cession, d'une scission ou d'un changement d'activité. » La suite de la réponse est inchangée (58 mots). | C. trav., art. L. 2261-14 |
| k33 | La mention « pendant cinq ans » était rattachée aux exercices ouverts à compter de 2025. Or l'article 5, I, de la loi fait courir les cinq ans de l'expérimentation à compter de sa promulgation. Ce point n'a pas été vérifié par une recherche. | La mention est retirée. La question dit déjà « à titre expérimental », et la réponse reste juste quelle que soit la lecture retenue. | Loi n° 2023-1107 du 29 novembre 2023, art. 5 |
| k38 | « Depuis la loi n° 2026-403 » présentait le délai d'un mois comme nouveau. Or ce délai figurait déjà à l'article R. 1321-2, compté depuis le dépôt et la publicité. La loi de 2026 (art. 5, V) l'a inscrit à l'article L. 1321-4 : le règlement indique sa date d'entrée en vigueur, postérieure d'un mois à l'accomplissement des formalités de publicité. | « Il ne peut entrer en vigueur qu'un mois au moins après l'accomplissement des formalités de publicité (art. L. 1321-4, dans sa rédaction issue de la loi n° 2026-403 du 26 mai 2026). » | C. trav., art. L. 1321-4 (version en vigueur depuis le 28 mai 2026) et R. 1321-2 |
| k39 | Pour le harcèlement, la partie défenderesse doit prouver deux choses : que les agissements ne sont pas constitutifs d'un harcèlement et que sa décision est justifiée par des éléments objectifs. La carte ne donnait que le second volet. | Ajout de « et, pour le harcèlement, que les agissements n'en sont pas constitutifs » (59 mots). | C. trav., art. L. 1154-1 et L. 1134-1 |
| k37 (supprimée) | k37 demandait les thèmes de la négociation de branche au moins quadriennale, « outre les salaires et l'égalité professionnelle ». Depuis le 26 octobre 2025, L. 2241-1 comporte un 5° bis (emploi et travail des salariés expérimentés), absent de la réponse. L'item de base (Règles essentielles#6) ne le mentionne pas, donc la carte ne pouvait pas être complétée. Elle répétait en outre la réponse de k34. | Carte supprimée. k34 reste exacte : classifications et épargne salariale au moins tous les cinq ans, et « les autres négociations […] au moins une fois tous les quatre ans ». | C. trav., art. L. 2241-1 (5° bis) et L. 2241-14-1, issus de la loi n° 2025-989 |
| k40 (ajoutée) | Règles essentielles#9 (révision d'un accord d'entreprise) n'avait plus de carte depuis la suppression de k26. | Carte `comp` : « Quelles organisations syndicales sont habilitées à engager la procédure de révision d'un accord d'entreprise ? ». Jusqu'à la fin du cycle électoral, les organisations représentatives signataires ou adhérentes ; ensuite, toutes les organisations représentatives. Le verbe « engager la procédure de révision » est celui de L. 2261-7-1. | C. trav., art. L. 2261-7-1 |

Les 24 autres cartes ont été contrôlées sans changement : k01 à k03, k07, k08, k10, k12 à k19, k21 à k23, k27, k28, k30 à k32, k34 et k36. Les chiffres qu'elles contiennent font partie d'une règle stable : 10 % et 8 %, 30 % et 50 %, onze, cinquante et trois cents salariés, quatre ans, deux mois, cinq jours francs, 7 500 €. Les dates de k08, k12, k22, k23 et k33 situent une réforme ; ce ne sont pas des chiffres annuels.

## Recherches faites

Les 3 recherches autorisées ont été faites, toutes avec `allowed_domains: ["legifrance.gouv.fr"]`.

1. **Négociation de branche et salariés expérimentés** (article L. 2241-1, loi n° 2025-989). La loi a inséré un 5° bis à l'article L. 2241-1 (emploi et travail des salariés expérimentés, en considération de leur âge). Elle a aussi créé L. 2241-14-1, qui prévoit une négociation triennale précédée d'un diagnostic. Conséquence : suppression de k37. Pages : [L. 2241-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000052437017), [L. 2241-14-1 et L. 2241-14-2](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000052432444/), [loi n° 2025-989](https://www.legifrance.gouv.fr/loda/id/LEGIARTI000052432349/2025-10-26).
2. **Désignation du délégué syndical** (article L. 2143-3). La version en vigueur depuis le 26 octobre 2025 a été modifiée par la loi n° 2025-989. À défaut de candidat ayant obtenu 10 %, la désignation se fait parmi les autres candidats, puis, à défaut, parmi les adhérents ou les anciens élus. Conséquence : correction de k04. Page : [L. 2143-3](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000036761993).
3. **Règlement intérieur** (article L. 1321-4, loi n° 2026-403). La version en vigueur depuis le 28 mai 2026 a été modifiée par l'article 5, V, de la loi. Elle dispose que le règlement « indique la date de son entrée en vigueur. Cette date doit être postérieure d'un mois à l'accomplissement des formalités de publicité ». Conséquence : correction de k38. Page : [L. 1321-4](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054140230).

Les autres corrections (k05, k06, k09, k20, k24, k25, k33, k39) reposent sur des articles anciens et stables du Code du travail : L. 2143-23, L. 2253-2, L. 2261-10, L. 2261-11, L. 2261-14, L. 2312-5 et L. 1154-1. Pour k33, la correction retire une mention douteuse sans en affirmer une autre.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#6** (négociation de branche) : **item périmé**. Depuis le 26 octobre 2025, l'article L. 2241-1 comporte un 5° bis : la négociation sur l'emploi et le travail des salariés expérimentés, au moins tous les quatre ans, et tous les trois ans à défaut d'accord, après diagnostic (L. 2241-14-1). « Ce qui a changé récemment#3 » ne vise que les entreprises d'au moins 300 salariés et devrait mentionner aussi les branches.
2. **Règles essentielles#13** (délégué syndical). L'article L. 2143-3, modifié par la loi n° 2025-989, prévoit trois étapes successives :
   - les candidats ayant obtenu 10 % ;
   - à défaut, les autres candidats ;
   - à défaut, les adhérents ou les anciens élus.

   La fiche saute l'étape intermédiaire. Elle pourrait aussi signaler qu'un représentant de la section syndicale peut, sur mandatement, négocier un accord en l'absence de délégué syndical (L. 2143-23).
3. **Règles essentielles#3** (articulation branche / entreprise). Dans le bloc 2 aussi, l'accord d'entreprise conclu postérieurement peut déroger à la branche s'il assure des garanties au moins équivalentes (L. 2253-2).
4. **Règles essentielles#7** (dénonciation). La survie et le maintien de la rémunération supposent une dénonciation par la totalité des signataires employeurs ou des signataires salariés (L. 2261-10). Une dénonciation partielle laisse l'accord en vigueur entre les autres signataires (L. 2261-11). La durée d'un an vaut « sauf clause prévoyant une durée déterminée supérieure ».
5. **Règles essentielles#8** (mise en cause). La liste des causes n'est pas limitative : le texte dit « en raison notamment d'une fusion… » (L. 2261-14).
6. **Règles essentielles#11** (attributions du CSE de 11 à 49 salariés). L'article L. 2312-5 vise les réclamations « individuelles ou collectives ». La délégation « contribue à promouvoir la santé, la sécurité et l'amélioration des conditions de travail », réalise les enquêtes AT/MP et exerce le droit d'alerte. La fiche abrège ces attributions.
7. **Points de vigilance#3** (règlement intérieur). Le délai d'un mois n'est pas une nouveauté de la loi n° 2026-403 : il figurait déjà à l'article R. 1321-2, compté depuis le dépôt et la publicité. Depuis le 28 mai 2026, l'article L. 1321-4 dispose que le règlement indique sa date d'entrée en vigueur, postérieure d'un mois à l'accomplissement des formalités de publicité. Formulation à reprendre.
8. **Points de vigilance#4** (harcèlement). Selon l'article L. 1154-1, la partie défenderesse prouve que les agissements ne sont pas constitutifs d'un harcèlement **et** que sa décision est justifiée par des éléments objectifs étrangers à tout harcèlement. La fiche ne retient que le second volet.
9. **Ce qui a changé récemment#2** (partage de la valeur). À vérifier sur l'article 5, I, de la loi n° 2023-1107 : la durée de cinq ans de l'expérimentation y court, semble-t-il, « à compter de la promulgation de la présente loi ». Elle ne courrait donc pas à compter des exercices ouverts en 2025.
10. **Ce qui a changé récemment#4** (cession, loi n° 2026-403, art. 22). L'information directe des salariés prévue par la loi Hamon (C. com., art. L. 141-28 et L. 23-10-7) ne concernait que les PME de moins de 250 salariés. Par ailleurs, la consultation du CSE existait déjà. « Remplacée » serait donc plus exactement : « supprimée, seule demeurant l'information-consultation du CSE ». À vérifier sur le texte de l'article 22.
11. **URL**, constat repris des passes de fidélité :
    - Définitions#2 et Règles essentielles#15 n'ont pas d'URL officielle ;
    - Règles essentielles#9 (L. 2261-7-1) et #10 (L. 2261-15) partagent la même URL de section, à contrôler.

## Classement des exercices

Le chapitre compte 30 exercices. Le classement automatique porte sur les 24 QCM, QCM multiples et classements : 19 QCM, 4 QCM multiples et 1 classement. Les 6 exercices de calcul (`calc`) sont de nature `calcul` par construction et n'en font pas partie.

| nature | nombre |
|---|---|
| notion | 24 |
| calcul | 0 |
| chiffre | 0 |

Aucun désaccord entre les classements. Les 24 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes.

Remarque hors classement : l'exercice #4 dit du représentant de la section syndicale qu'il « ne peut pas négocier ». Il porte la même nuance que la carte k06, puisque l'article L. 2143-23 permet le mandatement en l'absence de délégué syndical. La bonne réponse reste juste dans le contexte de l'énoncé.
