# Cartes de notions : ue10-05 (Actifs financiers, passifs financiers et provisions)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-05.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items. Un cycle antérieur de relectures (commit `95746d3`) avait déjà supprimé la carte k25, doublon de k24, et ajouté la carte k36. La présente reprise part de cet état.
2. **Relecture de fidélité.** Une première relecture a contrôlé les 35 cartes au regard du seul texte de la fiche, sans recherche web. Elle a corrigé deux cartes (k07 et k08) et signalé trois items de fiche à reprendre.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, CGI et BOFiP, PCG modifié par les règlements ANC n° 2018-01 et 2022-06, règlement ANC n° 2026-03 (exercices ouverts à compter du 1er janvier 2027) ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a fait une seule recherche WebSearch, limitée au domaine anc.gouv.fr (voir « Recherches »).
4. **Validation.** `node validate.js data/ue10/ue10-05.cartes.json` : ✓ (35 cartes, 11 déf.).

## Bilan

- **Nombre de cartes : 35.** La reprise n'a supprimé ni ajouté aucune carte. L'identifiant k25, supprimé lors du cycle antérieur, reste vide : rien n'a été renuméroté.
- **Répartition : 11 cartes `def` et 24 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 7 items de « Définitions » ont chacun au moins une carte.
  - Les 18 « Règles essentielles » et les 7 « Points de vigilance » sont tous couverts.
  - Dans « Chiffres et seuils », seul l'item #1 (cours moyen du dernier mois) est couvert, par k11.
  - Dans « Ce qui a changé récemment », les items #0 et #1 (règlement ANC n° 2022-06) sont couverts, par k14, k21 et k33.
- **Items de fiche sans carte :**
  - Chiffres et seuils#0 (présomption au-delà de 10 % du capital) : la règle est déjà portée par k02, qui repose sur Règles essentielles#0 ;
  - Chiffres et seuils#2 (comptes de titres et de dépréciation) : c'est une liste de numéros de comptes, déjà révisée avec le plan comptable ;
  - Chiffres et seuils#3 (montant de la prime de remboursement) : c'est une formule de calcul, que le contrat exclut des cartes. La règle du compte 163 crédité du prix de remboursement est portée par k20 ;
  - Chiffres et seuils#4 (régime des sociétés mères) : c'est une règle fiscale chiffrée qui relève de l'UE 4, à la marge de ce chapitre ;
  - Ce qui a changé récemment#2 (règlement ANC n° 2026-03) : il porte surtout sur les produits des ventes. Pour ce chapitre, son seul apport est le transfert de l'art. 513-5 vers l'art. 531-5, qui figure dans la source de k34.

  Le contrat n'impose une carte que pour chaque item de « Définitions ».
- **Aucun calcul, aucun chiffre millésimé.** Les dates citées sont des dates de textes ou d'entrée en vigueur, pas des chiffres annuels : « PCG 2025 », « depuis 2025 », règlement ANC n° 2018-01. Le seuil de 10 % (k02) est un chiffre stable qui fait partie de la règle.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue10-05-k07 | La règle « le résultat fiscal suit le choix comptable » était donnée sans aucune réserve. La fiche (Points de vigilance#0) l'énonce bien ainsi, mais une exception existe hors fiche : pour les titres de participation à l'IS, l'art. 209, VII du CGI impose d'incorporer les frais au prix de revient et de les déduire sur cinq ans. Pour ces titres, la réponse devenait fausse. La question avait déjà été rendue ouverte (elle n'était plus du type oui/non) avant cette passe. | La règle reste celle de la fiche, mais elle est posée comme un principe, sans rien ajouter de la règle extérieure. Question : « Pour les frais d'acquisition des titres, quelle option l'entreprise doit-elle en principe retenir pour déterminer son résultat fiscal ? » Réponse : « **En principe, celle retenue en comptabilité : le résultat fiscal suit le choix comptable.** L'option s'exerce par la seule comptabilisation des frais en immobilisation ou en charges ; il n'est pas possible d'exercer une option fiscale différente. » Le point de fiche concerné est signalé à reprendre. |
| ue10-05-k08 | « On ramène la valeur nette comptable à la valeur d'inventaire » était présenté comme absolu. Or Règles essentielles#4, dans la même fiche, prévoit une exception : en cas de baisse anormale et momentanée des cours, l'entité n'est pas obligée de déprécier à concurrence des plus-values latentes sur d'autres titres. C'est le cas qu'enseigne la carte k12, et la carte k13 dit déjà « en principe ». | La réponse commence désormais par « **En principe, on ramène la valeur nette comptable à la valeur d'inventaire** par une dépréciation… ». Le reste est inchangé : comptes 6866 et 7866, calcul ligne de titres par ligne de titres. |

La première relecture n'a fait ni suppression ni ajout. Elle a porté la date `maj` au 2026-10-16.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-05-k10 | « Elle s'apprécie d'après la rentabilité et ses perspectives, les capitaux propres… » présentait les critères comme une liste fermée et cumulative. Or le PCG les donne comme des éléments qui « peuvent être pris en considération ». Une réponse juste qui n'en citait que quelques-uns aurait paru incomplète. | « Pour l'estimer, peuvent notamment être pris en considération la rentabilité et ses perspectives, les capitaux propres, les perspectives de réalisation, la conjoncture économique, les cours moyens de bourse du dernier mois et les motifs de l'acquisition. » La définition elle-même est inchangée. | PCG, art. 221-3 (Règles essentielles#3) |
| ue10-05-k30 | « Le provisionnement de la totalité des engagements est la méthode de référence depuis le règlement ANC n° 2018-01 » laissait croire que ce provisionnement n'est privilégié que depuis 2018. Or c'était déjà la « méthode préférentielle » : le règlement n° 2018-01 n'a fait que la renommer, comme le dit la fiche (« auparavant méthode préférentielle »). | « Le provisionnement de la totalité des engagements est la méthode de référence (appelée « méthode préférentielle » avant le règlement ANC n° 2018-01). » | C. com., art. L. 123-13 ; PCG, art. 324-1 ; règlement ANC n° 2018-01 (Règles essentielles#15) |
| ue10-05-k35 | « Aux comptes 6872 (dotations) et 7872 (reprises) » présentait ces comptes comme ceux de toutes les provisions réglementées du compte 14. Or 6872 et 7872 ne visent que les provisions réglementées relatives aux immobilisations. La provision pour hausse des prix (143) est dotée au compte 6873 et reprise au compte 7873, et les autres provisions réglementées (148) passent par 6874 et 7874 (recherche 1). La réponse était donc fausse pour le compte 143, que cite la carte k34. | La réponse ne retient que ce qui est vrai pour toutes ces provisions et l'exemple que donne la fiche : « **En résultat exceptionnel** : ce sont des écritures d'origine purement fiscale, que le PCG classe dans ce résultat. Les amortissements dérogatoires, par exemple, sont dotés au compte 68725 et repris au compte 78725. » | PCG, plan de comptes 2026, comptes 687 et 787 ; PCG, art. 513-5 (Points de vigilance#4, Définitions#6) |
| ue10-05-k36 | La question « quelles normes régissent les instruments financiers et les provisions ? » admettait une autre réponse juste : IAS 32 (présentation) et IFRS 7 (informations à fournir) régissent aussi les instruments financiers. Une réponse « IAS 32, IFRS 7 et IFRS 9 » aurait été exacte mais différente du verso. | La question est resserrée : « Dans des comptes consolidés établis selon les normes IFRS adoptées par l'Union européenne, quelle norme régit la comptabilisation et l'évaluation des instruments financiers, et laquelle les provisions ? » La réponse (IFRS 9 et IAS 37) est inchangée. | C. com., art. L. 233-24 (Points de vigilance#6) |

Les 31 autres cartes ont été jugées exactes au 15 octobre 2026, et aucune ne présente d'ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- **k07, telle que corrigée par la première relecture.** Le « en principe » suffit à couvrir l'exception de l'art. 209, VII du CGI. Cette exception n'est pas une option fiscale : c'est une règle impérative. La phrase « il n'est pas possible d'exercer une option fiscale différente » reste donc exacte. La carte est maintenue sans retouche.
- **k08** : le « en principe » ajouté est conforme à l'art. 221-7 du PCG.
- **Classement et définitions des titres** (C. com., art. R. 123-184 ; comptes 26, 27 et 50) : participation, présomption au-delà de 10 %, titres immobilisés 271 et 272, TIAP, VMP (503 actions, 506 obligations, 501 supprimé en 2025).
- **Évaluation des titres** (PCG, art. 221-1, 221-6, 221-7 et 222-1) :
  - option sur les frais d'acquisition, indépendante de celle des immobilisations corporelles et incorporelles ;
  - cours moyen du dernier mois et valeur probable de négociation ;
  - exception de la baisse anormale et momentanée ;
  - tolérance « pas notablement inférieure » réservée aux immobilisations non financières (C. com., art. R. 123-178, 5°).
- **Cessions** (règlement ANC n° 2022-06) : brut en 6671 et 7671 pour les immobilisations financières autres que les TIAP, net en 6672 et 7672 pour les TIAP, net en 6673 et 7673 pour les VMP, 675 et 775 supprimés. Ces intitulés sont concordants avec le plan comptable du projet (`data/pcg`).
- **Coût d'entrée des titres cédés** : coût moyen pondéré ou PEPS (C. com., art. L. 123-18).
- **Produits** : intérêts courus en 2768 et 5088 ; dividendes en 761, 762 et 764 (C. com., art. L. 232-12).
- **Emprunts** (PCG, art. 212-10 et 212-11) : compte 163 crédité du prix de remboursement, prime 169, frais d'émission en 481 et 6862, intérêts courus en 1618, 1638 et 1648 (contrat, § 6).
- **Passifs et provisions** (PCG, art. 321-1 et s. ; C. com., art. L. 123-20) : passif, dette, provision, passif éventuel (avec « notamment »), conditions de comptabilisation, meilleure estimation.
- **Fiscalité des provisions** : CGI, art. 39, 1-5° et art. 38, 4.
- **Comptes de provisions** : 151 et 152 ; provisions réglementées en capitaux propres (C. com., art. R. 123-190).

**Doublons.** Aucun doublon n'a été relevé. Les paires proches posent des questions distinctes : k08 et k09 (dépréciation, plus-value latente), k24, k26 et k28 (provision, passif éventuel, passif non évaluable), k34 et k35 (définition, résultat d'imputation).

## Recherches

Une seule recherche WebSearch a été faite, limitée au domaine `anc.gouv.fr`.

1. **« plan de comptes 2026 "6873" dotations aux provisions réglementées stocks "6874" autres provisions réglementées »**.
   - Les résultats indiquent que le [plan de comptes 2026 de l'ANC](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/Plan-de-comptes-2026.pdf) comporte, parmi les charges exceptionnelles, les comptes 6873 « Dotations aux provisions réglementées (stocks) » et 6874 « Dotations aux autres provisions réglementées ». Les reprises correspondantes sont 7873 et 7874.
   - Le [plan de comptes 2024](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/Recueils/PCG_Janvier2024/Plan-de_comptes_PCG-2024.pdf) les comportait déjà.
   - Ces comptes sont aussi décrits dans le plan comptable du projet (`data/pcg`, comptes 143, 148, 687 et 787).
   - Cela confirme que 6872 et 7872 ne couvrent pas toutes les provisions réglementées : correction de k35 et point de fiche n° 4.

Aucune autre recherche n'a paru nécessaire : les autres points relèvent de textes stables (Code de commerce, PCG) ou ont été vérifiés lors du cycle antérieur (comptes 501, 481 et 6862).

## Points à reprendre dans la fiche

1. **Points de vigilance#0** (signalé par la première relecture, confirmé). « Le résultat fiscal suit le choix comptable » n'est pas assorti de l'exception de l'art. 209, VII du CGI. À l'IS, les frais d'acquisition des titres de participation sont obligatoirement incorporés au prix de revient fiscal et déduits par fractions égales sur cinq ans. Ils le sont par amortissement dérogatoire s'ils ont été immobilisés, ou par réintégration puis déductions extra-comptables s'ils ont été passés en charges. Il faut ajouter cette exception.
2. **Règles essentielles#7** (signalé par la première relecture et par le cycle antérieur, confirmé). « Pour le calcul des plus-values imposables » élargit l'art. 39 duodecies, 6 du CGI, qui joue « pour l'application des 1 à 3 », c'est-à-dire pour qualifier les plus-values à court ou à long terme. Il serait plus juste d'écrire : « pour l'application du régime des plus-values à court et à long terme ».
3. **Points de vigilance#6** (signalé par la première relecture ; le résultat relayé s'arrête au milieu de ce point). « En comptes individuels, les plus-values latentes sur titres ne sont jamais comptabilisées » est trop absolu. Deux cas le contredisent :
   - la réévaluation de l'ensemble des immobilisations corporelles et financières, dont l'écart est inscrit au passif (C. com., art. L. 123-18, al. 4) ;
   - la mise en équivalence des titres de participation de sociétés contrôlées de manière exclusive (C. com., art. L. 232-5).

   Il faudrait écrire « ne sont pas comptabilisées, sauf réévaluation ou mise en équivalence ». La carte k36 ne reprend pas cette phrase.
4. **Points de vigilance#4** (nouveau). « Dotées et reprises en résultat exceptionnel (6872 et 7872, dont 68725 et 78725 pour les amortissements dérogatoires) » présente 6872 et 7872 comme les comptes de toutes les provisions réglementées. Or :
   - 6872 et 7872 ne visent que les provisions réglementées relatives aux immobilisations ;
   - la provision pour hausse des prix (143) passe par 6873 et 7873 ;
   - les autres provisions réglementées (148) passent par 6874 et 7874.

   Il faudrait écrire « (6872 à 6874 et 7872 à 7874, dont 68725 et 78725 pour les amortissements dérogatoires) ». La mention « 6872 et 7872 » de la source de l'item serait à compléter de même.
5. **Définitions#4** (signalé lors du cycle antérieur, toujours d'actualité). La définition du passif éventuel ne reprend que le premier cas de l'art. 321-6 du PCG (obligation potentielle née d'événements incertains). Le second cas manque : une obligation dont il n'est pas probable ou certain qu'elle provoquera une sortie de ressources sans contrepartie au moins équivalente. C'est pourquoi la carte k26 garde « notamment ».

## Classement des exercices

Le classement automatique des 20 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 16 | oui |
| `calcul` | 3 | non |
| `chiffre` | 1 | non |

Les classeurs ont été en désaccord sur trois exercices (numérotés à partir de 0 dans `ue10-05.json`) :
- **#10** (cession d'une participation dépréciée, montants à l'appui) : notion / calcul → `calcul`. Les options sont des écritures chiffrées, ce que le contrat range hors des notions.
- **#12** (compte de dépréciation d'actions cotées classées en VMP) : notion / null → `chiffre`. **Ce classement paraît à revoir.** La question porte sur le choix d'un compte (590), que le contrat (§ 8) range expressément dans les `notion`. Elle ne fait appel à aucun chiffre millésimé. Au moment de la relecture, `ue10-05.json` porte d'ailleurs encore `nature: "notion"` pour cet exercice.
- **#13** (obligation acquise coupon couru inclus) : notion / calcul → `calcul`. L'énoncé et l'explication sont chiffrés, même si la réponse attendue est un traitement comptable.

Les 16 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 3 exercices de nature `calcul` (#10, #13 et #18) et l'exercice de nature `chiffre` (#12) restent dans le chapitre, mais ils ne sont pas proposés en révision.
