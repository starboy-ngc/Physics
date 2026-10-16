# Cartes de notions : ue4-05 (La taxe sur la valeur ajoutée)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-05.fiche.json` et d'elle seule. Elles respectent le contrat (section 8) : une question par carte, aucun calcul, aucun chiffre millésimé, et chaque carte s'appuie sur un ou deux items de fiche (`base`) dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : un premier relecteur a contrôlé les 35 cartes. Il a vérifié que chaque carte dit ce que dit la fiche, sans plus, et qu'elle respecte la forme exigée par le contrat. Il n'a fait aucune recherche : son seul juge était le texte (`t` et `cite`) des items de la fiche.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a vérifié les points suivants :
   - **Exactitude** : chaque carte est-elle juste au regard du droit en vigueur au 15 octobre 2026 (CGI et annexe II, BOFiP, CIBS) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne dit pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle qu'attendrait un correcteur du DCG, et la seule réponse juste possible ?
   - **Doublons et cartes triviales.**
   - **Absence de calcul et de chiffre millésimé.**
   - **Durée de vie** : la personne prépare la session 2027 et révisera ces cartes après le 1er janvier 2027, date à laquelle les articles législatifs du CGI relatifs à la TVA sont abrogés au profit du CIBS. Une carte ne doit pas devenir fausse à cette date.
4. **Recherches** : 3 recherches, le maximum permis, limitées à impots.gouv.fr, bofip.impots.gouv.fr et legifrance.gouv.fr (détail plus bas). Elles confirment la fiche sur les trois points vérifiés.

Validation : `node validate.js data/ue4/ue4-05.cartes.json` renvoie « ✓ data/ue4/ue4-05.cartes.json (cartes, 35 (8 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k36, sans k21) |
| Définition (`def`) | 8 (k01 à k06, k18, k24) |
| Compréhension (`comp`) | 27 |
| Cartes corrigées par la relecture de fidélité | 2 (k06, k34) |
| Cartes corrigées par la relecture d'exactitude | 13 (k01, k02, k03, k08, k09, k10, k12, k13, k15, k17, k18, k19, k24) |
| Cartes supprimées | 0 |
| Cartes ajoutées | 0 |

Le numéro k21 est vacant : la carte a été retirée avant les deux relectures. Elle portait sur l'exigibilité de la TVA à l'encaissement d'un acompte sur une livraison de biens, règle reprise dans k20. Conformément au contrat, les cartes ne sont pas renumérotées.

**Items de la fiche sans carte** :

- **Items millésimés**, qui ne peuvent pas donner de carte :
  - Règles essentielles#13 (régime simplifié : seuils 2026 et acomptes) ;
  - Chiffres et seuils#1 (seuils 2026 du régime simplifié), #2 (seuils 2025-2026 de la franchise en base), #4 (périodicité des CA3, seuils 2026 et 2027) et #5 (acomptes du régime simplifié) ;
  - Ce qui a changé récemment#1 (abandon du seuil unique de la franchise) et #3 (nouvelles mentions des factures au 1er septembre 2026) ;
  - Points de vigilance#2 (franchise et micro-BIC) et #4 (sortie de la franchise en base).
- **Chiffres et seuils#3** (crédit de TVA) : l'item est stable, mais il ne contient que des montants (760 € et 150 €). Une carte serait du par-cœur sur des chiffres.

Chaque item des Définitions (5 sur 5) et chaque item stable des Règles essentielles (15 sur 15) a au moins une carte. C'est aussi le cas des items stables de « Ce qui a changé récemment » (#0, #2, #4, #5 et #6) et des Points de vigilance (#0, #1, #3 et #5).

Le jeu atteint le plafond de 35 cartes fixé par le contrat. Aucun ajout n'était possible sans suppression, et aucune carte n'était assez faible pour céder sa place.

## Corrections de la première relecture (fidélité)

Le premier relecteur a contrôlé 35 cartes et en a corrigé deux.

| Cible | Problème | Correction |
|---|---|---|
| k06 | La question « Quels sont les trois régimes de déclaration de la TVA prévus par le CGI ? » était au présent, sans limite de temps. Or la fiche annonce la suppression du régime simplifié au 1er janvier 2027 (Définitions#4, Ce qui a changé récemment#4) et l'abrogation des articles du CGI relatifs à la TVA au profit du CIBS (Points de vigilance#5). À partir de 2027, la question attendrait donc trois régimes du CGI qui n'existeront plus. | La question devient « Jusqu'au 31 décembre 2026, quels sont les trois régimes de déclaration de la TVA ? ». La réponse, la base (Définitions#4), `src` et `url` ne changent pas. |
| k34 | La fiche donne les mentions de la facture avec « notamment » (Règles essentielles#14) : la liste n'est pas complète. La question les demandait pourtant comme une liste fermée. Une personne qui citait une autre mention liée à la TVA, par exemple l'option pour les débits (obligatoire depuis le 1er septembre 2026), se serait crue en erreur. | La question devient « …, quelles mentions liées à la TVA une facture doit-elle notamment comporter ? » (28 mots). La réponse, la base, `src` et `url` ne changent pas. |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k09 | La réponse disait seulement que les locations nues de **logements** sont exonérées et que le bailleur de locaux nus **professionnels** « peut opter ». Le régime par défaut de ces locaux n'était pas dit, et la personne pouvait croire qu'ils sont imposables sans option. Or l'article 261 D, 2° exonère toutes les locations de locaux nus : l'option sert justement à sortir de cette exonération. | Seconde phrase : « Les locations nues de locaux professionnels sont aussi exonérées, sauf si le bailleur opte pour l'imposition à la TVA, ce qu'il peut faire lorsque les locaux servent à l'activité d'un preneur assujetti. » Bases inchangées (Règles essentielles#0 et #1) : la possibilité d'opter suppose l'exonération par défaut. | CGI, art. 261 D, 2° et 260, 2° ; fiche, Règles essentielles#1 (`cite`) |
| k19 | « Les débours remboursés à l'euro » est une formule tronquée, déjà relevée par la première relecture. Le critère légal n'est pas un remboursement « à l'euro », mais des dépenses engagées au nom et pour le compte du client et remboursées pour leur montant exact. La question demandait en outre « quels éléments sont exclus », comme si la liste était fermée, alors que l'article 267, II en vise d'autres (sommes consignées pour les emballages, par exemple). | Question : « …, quels sont les **principaux** éléments exclus de la base d'imposition d'une opération imposable ? ». Réponse : « …, ainsi que les débours, c'est-à-dire les dépenses engagées au nom et pour le compte du client et remboursées pour leur montant exact. » Base inchangée (Règles essentielles#7). | CGI, art. 267, II, 1° à 3° |
| k24 | La réponse disait « chaque coefficient est arrondi au centième supérieur ». La recherche n° 2 montre que l'article 206, V vise les **quatre** coefficients : les trois facteurs, puis leur produit, qui est lui-même arrondi par excès à la deuxième décimale. La question citait par ailleurs « l'article 206 de l'annexe II au CGI », numérotation appelée à disparaître avec la recodification. | Question : « En matière de TVA, qu'est-ce que le coefficient de déduction ? ». Dernière phrase : « Chacun de ces coefficients, comme leur produit, est arrondi au centième supérieur. » Base inchangée (Règles essentielles#10). | CGI, ann. II, art. 206, V ; BOI-TVA-DED-20-10-40 (recherche n° 2) |
| k13 | Dans « la sortie physique du bien et sa mention dans l'état récapitulatif », « sa » renvoie grammaticalement au bien. Or c'est la **livraison** qui doit figurer dans l'état récapitulatif des clients. La destination du bien n'était pas précisée non plus : une sortie vers un pays tiers relève de l'exportation. | « …, la sortie physique du bien de France vers un autre État membre et la mention de la livraison dans l'état récapitulatif. » La seconde phrase (acquéreur assujetti identifié dans un autre État membre) est conservée. | CGI, art. 262 ter, I ; fiche, Règles essentielles#3 |
| k12 | La seconde phrase de la réponse (« La livraison intracommunautaire doit être faite à un assujetti identifié dans un autre État membre ») répétait mot pour mot une condition de k13. La notion propre à k12, le maintien du droit à déduction, n'était pas expliquée. | Seconde phrase : « Le vendeur ne facture pas de TVA mais conserve le droit de déduire celle qui grève ses achats. » Bases inchangées (Règles essentielles#3, Points de vigilance#0). | CGI, art. 262, I et 271 ; fiche, Points de vigilance#0 |
| k17 | « La TVA de l'État de consommation s'applique et est déclarée via le guichet unique (OSS) » présentait le guichet unique comme obligatoire. C'est une simplification facultative : le vendeur peut aussi s'identifier dans chaque État de consommation. | « …, la TVA de l'État de consommation s'applique ; elle **peut** être déclarée via le guichet unique (OSS). » | CGI, art. 298 sexdecies G (régime facultatif) |
| k18 | « Toutes les sommes, valeurs, biens ou services reçus en contrepartie » omettait les sommes **à recevoir**. La base d'imposition comprend le prix convenu, qu'il soit déjà encaissé ou non. | « …reçus **ou à recevoir** en contrepartie de l'opération… » | CGI, art. 266, 1-a |
| k10 | La question qualifiait « l'activité d'un médecin » comme exonérée. Seuls les **soins** dispensés par les professions médicales réglementées sont exonérés. Certains actes d'un médecin sans finalité thérapeutique sont imposables. | « Au regard de la TVA, comment qualifier l'activité de soins d'un médecin ou celle d'un bailleur de logement nu ? » | CGI, art. 261, 4-1° |
| k08 | « Quelles grandes catégories d'opérations sont exonérées » appelait une liste fermée. Une personne pouvait citer, sans se tromper, d'autres exonérations (organismes sans but lucratif, ventes d'immeubles achevés depuis plus de cinq ans, etc.) et se croire en erreur. | « …, quelles sont les **principales** catégories d'opérations exonérées de TVA ? ». La réponse ne change pas. | CGI, art. 261 et suivants |
| k01, k02, k15 | Les questions renvoyaient à des articles du CGI : « selon l'article 256 du CGI », « au sens de l'article 256 A du CGI », « de l'article 259 du CGI ». Ces articles législatifs sont abrogés au 1er janvier 2027 au profit du livre II du CIBS (recherche n° 3). Révisée en 2027, la carte renverrait à un article abrogé, alors que la règle demandée ne change pas. | « Quelles opérations sont imposables à la TVA par nature ? » ; « Qui a la qualité d'assujetti à la TVA ? » ; « Selon les règles générales de territorialité, où une prestation de services est-elle imposable à la TVA ? ». Les réponses, `src` et `url` ne changent pas (les références restent dans `src`). | Ordonnance n° 2025-1247 du 17 décembre 2025, modifiée par l'ordonnance n° 2026-671 du 27 juillet 2026 (art. 17) ; fiche, Points de vigilance#5 |
| k03 | Même raison : la réponse truffait la règle de numéros d'articles du CGI (« (CGI, art. 257) », « (art. 256 bis) », « (art. 291) »), qui seront abrogés au 1er janvier 2027. Ils alourdissaient aussi la réponse à mémoriser. | « Les livraisons à soi-même de biens ou d'immeubles et les livraisons de terrains à bâtir et d'immeubles neufs. S'y ajoutent les acquisitions intracommunautaires et les importations. » Les références restent dans `src`. | Mêmes textes que ci-dessus |

**Cartes contrôlées et maintenues** :

- **Régime simplifié (k06, k32)** : la recherche n° 1 confirme la suppression du régime simplifié d'imposition à la TVA au 1er janvier 2027 (LF 2025, art. 38). Elle confirme aussi la bascule automatique au réel normal, avec des CA3 trimestrielles ou mensuelles selon le chiffre d'affaires, et la dernière CA12 due le 4 mai 2027 pour un exercice clos le 31 décembre 2026. Les deux cartes sont exactes ; k06 est bornée au 31 décembre 2026 depuis la première relecture.
- **Recodification (k33)** : la recherche n° 3 confirme le transfert de la TVA vers le livre II du CIBS par l'ordonnance n° 2025-1247 et le report de son entrée en vigueur du 1er septembre 2026 au 1er janvier 2027 (ordonnance n° 2026-671, BOFiP ACTU-2026-00126). La carte est exacte.
- **Mentions de facture (k34)** : la mention « TVA non applicable, art. 293 B du CGI » est exacte aujourd'hui. Le rapport au Président de la République sur l'ordonnance n° 2026-671 indique que les anciennes références au CGI peuvent encore être utilisées jusqu'au 30 juin 2028. La carte reste donc juste pendant toute la préparation de la session 2027. Elle est signalée pour une mise à jour de la fiche (voir plus bas).
- **Autres cartes de fond** : les cartes suivantes sont conformes aux textes :
  - k04, k05 (fait générateur, exigibilité) ;
  - k11, k14, k16 (territorialité, autoliquidation à l'importation depuis 2022) ;
  - k20, k22, k23 (exigibilité et droit à déduction) ;
  - k25, k35 (exclusions et carburants à 80 % ou 100 %, règle alignée pour l'essence et le gazole) ;
  - k26 (régularisations sur 5 ou 20 ans, seuil d'un dixième) ;
  - k27, k28 (TVA facturée à tort, sous-traitance du bâtiment) ;
  - k29, k36 (champ des taux de 10 %, 5,5 % et 2,1 %) ;
  - k30, k31 (déchets à 5,5 %, calendrier de la facturation électronique).
- **Doublons apparents** : plusieurs paires de cartes portent sur les mêmes items, mais chacune interroge un angle distinct. k12 et k13 ont été réécrites pour ne plus partager de phrase.
  - k04 et k05 : fait générateur et exigibilité ;
  - k06 et k07 : les trois régimes et les effets de la franchise, avec l'option ;
  - k12 et k13 : traitement des opérations et conditions de l'exonération intracommunautaire ;
  - k15 et k16 : règle générale et dérogations ;
  - k18 et k19 : éléments inclus et exclus de la base ;
  - k20 et k23 : exigibilité, puis naissance du droit à déduction chez le client ;
  - k25 et k35 : exclusions et carburants ;
  - k29 et k36 : taux de 10 %, puis taux de 5,5 % et 2,1 %.
- **Chiffres stables** : les chiffres cités sont fixés par la loi ou par la directive, sans indexation annuelle. Dans chaque cas, la question porte sur la règle, ce que le contrat (section 8) admet :
  - k17 : seuil de 10 000 € ;
  - k26 : 5 et 20 ans, un dixième ;
  - k29, k30, k36 : taux de 20 %, 10 %, 5,5 % et 2,1 % ;
  - k35 : 80 % et 100 %.

  Aucune carte ne cite un seuil millésimé (franchise, régime simplifié, CA3, micro-BIC).

## Recherches faites

1. **Suppression du régime simplifié de TVA** (domaine impots.gouv.fr ; actualité « Le régime simplifié d'imposition à la TVA est supprimé à compter du 1er janvier 2027 »).
   - Confirmé : la loi de finances pour 2025 (art. 38) supprime le régime au 1er janvier 2027 et les redevables basculent automatiquement au réel normal.
   - La CA3 est trimestrielle si le chiffre d'affaires n'excède pas 1 M€ l'année précédente et 1,1 M€ l'année en cours, une option pour le mensuel restant possible. La dernière CA12 est due le 4 mai 2027 pour un exercice clos le 31 décembre 2026.
   - Le régime simplifié agricole (RSA) n'est pas concerné.
   - Conséquence : k06 et k32 sont maintenues.
2. **Arrondi du coefficient de déduction** (domaines bofip.impots.gouv.fr et legifrance.gouv.fr ; BOI-TVA-DED-20-10-40, CGI, ann. II, art. 206).
   - Confirmé : en vertu du 2 du V de l'article 206, chacun des trois coefficients est arrondi par excès à la deuxième décimale avant le calcul du produit. Le produit est lui-même arrondi par excès à la deuxième décimale (exemple du BOFiP : 0,66 × 0,84 × 1 = 0,5544, arrondi à 0,56).
   - Les pages consultées sont en partie anciennes (version de 2012 du BOFiP). La règle est confirmée, sous réserve de la version en ligne.
   - Conséquence : k24 est corrigée.
3. **Recodification de la TVA dans le CIBS** (domaines bofip.impots.gouv.fr et legifrance.gouv.fr ; ordonnance n° 2025-1247, ordonnance n° 2026-671 du 27 juillet 2026 et rapport au Président de la République, ACTU-2026-00126, BOI-RES-TVA-000253-20261007).
   - Confirmé : le transfert de la TVA au livre II du CIBS, prévu au 1er septembre 2026, est reporté au 1er janvier 2027. L'ordonnance n° 2026-671 remplace la date dans l'article 49 de l'ordonnance n° 2025-1247.
   - Les anciennes références au CGI peuvent continuer à être utilisées jusqu'au 30 juin 2028 (au lieu du 31 décembre 2027).
   - Conséquence : k33 est maintenue ; les questions k01, k02, k15 et k24, ainsi que la réponse k03, ne citent plus de numéro d'article du CGI.

## Points à reprendre dans la fiche

Points relevés par la relecture d'exactitude :

- **Règles essentielles#10 (coefficient de déduction)** : « chaque coefficient est arrondi au centième supérieur » est incomplet. Les trois coefficients **et leur produit** sont arrondis par excès à la deuxième décimale (CGI, ann. II, art. 206, V ; BOI-TVA-DED-20-10-40, recherche n° 2).
- **Règles essentielles#7 (base d'imposition)** :
  - « les débours remboursés à l'euro » est à remplacer par « les débours, c'est-à-dire les dépenses engagées au nom et pour le compte du client et remboursées pour leur montant exact » (CGI, art. 267, II, 2°) ;
  - « reçues » est à compléter par « ou à recevoir » (CGI, art. 266, 1-a).
- **Règles essentielles#0 (exonérations)** : l'item ne cite que les locations nues « à usage d'habitation ou de terres agricoles ». Or l'article 261 D, 2° exonère toutes les locations de locaux nus, y compris professionnels, sous réserve de l'option de l'article 260, 2°. La formulation actuelle laisse croire que les locaux professionnels nus sont imposables par défaut.
- **Règles essentielles#6 (ventes à distance)** : « TVA de l'État de consommation déclarée via le guichet unique (OSS) » devrait devenir « … qui peut être déclarée via le guichet unique (OSS) ». Le guichet unique est facultatif.
- **Points de vigilance#0 (médecin)** : « un médecin … est dans le champ mais exonéré » est à limiter aux **soins** dispensés par le médecin (CGI, art. 261, 4-1°). Certains actes sans finalité thérapeutique sont imposables. Ce point vient de connaissances générales et n'a pas été recherché.
- **Ce qui a changé récemment#5 et Points de vigilance#5 (recodification)** : il faudrait ajouter que les anciennes références au CGI peuvent continuer à être utilisées jusqu'au 30 juin 2028 (rapport au Président de la République sur l'ordonnance n° 2026-671, recherche n° 3).
- **Règles essentielles#14 (facturation)** : la mention « TVA non applicable, art. 293 B du CGI » renvoie à un article abrogé au 1er janvier 2027. La fiche devrait indiquer la référence qui le remplace dans le CIBS, ou rappeler que l'ancienne référence reste utilisable jusqu'au 30 juin 2028.
- **Ce qui a changé récemment#4 (suppression du régime simplifié)** : on peut préciser que le régime simplifié agricole n'est pas concerné et que l'option pour des CA3 mensuelles reste ouverte (impots.gouv.fr, recherche n° 1).

Points déjà relevés par la première relecture, toujours valables pour la fiche :

- **Règles essentielles#3** : dans « la sortie physique du bien et sa mention dans l'état récapitulatif », « sa » renvoie au bien, alors que c'est la livraison qui doit figurer dans l'état récapitulatif. Il faudrait écrire « la sortie physique du bien de France vers un autre État membre et la mention de la livraison dans l'état récapitulatif ». La carte k13 est corrigée.
- **Règles essentielles#7** : « débours remboursés à l'euro », traité ci-dessus. La carte k19 est corrigée.
- **Règles essentielles#10** : l'arrondi des coefficients, vérifié par la recherche n° 2 et traité ci-dessus. La carte k24 est corrigée.

## Classement des exercices

Classement automatique des exercices QCM, QCM multiples et classements (tri) du chapitre selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 19 |
| `calcul` (montant, taux, prorata, délai) | 2 |
| `chiffre` (rappel d'un chiffre millésimé) | 2 |
| **Total** | 23 |

Deux désaccords entre les classements ont été tranchés :

| Exercice | Classements en désaccord | Nature retenue |
|---|---|---|
| #11 | `notion` / `calcul` | `calcul` |
| #14 | `notion` / `chiffre` | `chiffre` |

Seuls les 19 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
