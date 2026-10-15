# Cartes de notions : ue9-02 (Le plan comptable et la partie double)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-02.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle n'a fait aucune recherche web.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, PCG modifié par les règlements ANC n° 2022-06, 2024-07 et 2026-03) ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt.

   Elle a aussi vérifié l'absence de calcul et de chiffre millésimé. Une seule recherche a été faite, limitée à anc.gouv.fr (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-02.cartes.json` : ✓ (30 cartes, 9 déf.).

## Bilan

- **Nombre de cartes : 30.** Il y en avait 33 au départ. Trois ont été supprimées (k08, k30, k33), sans renumérotation : les identifiants k08, k30 et k33 restent vides.
- **Répartition : 9 cartes `def` et 21 cartes `comp`.**
- **Couverture de la fiche.** Les 5 items de « Définitions » ont chacun au moins une carte. Les 15 « Règles essentielles », les 3 « Chiffres et seuils » (règles stables, sans chiffre millésimé) et les 5 « Points de vigilance » sont tous couverts.
- **Item de fiche sans carte : « Ce qui a changé récemment#3 »** (règlement ANC n° 2026-03 : compte 6454 renommé « France Travail »). Sa carte k30 a été supprimée, car elle était anecdotique et faisait doublon avec la révision du compte 6454 dans le plan comptable.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les dates d'application des règlements (2025, 2026) sont des dates d'entrée en vigueur, pas des chiffres annuels.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-02-k06 | Le verso (« La classe 6 enregistre les charges de l'exercice par nature ») s'écartait du texte de la fiche. | Verso repris au plus près de Règles essentielles#7 : la classe 6 regroupe les comptes destinés à enregistrer, dans l'exercice, les charges par nature. Les charges d'exploitation normale et courante vont aux comptes 60 à 65, les charges financières au compte 66. |
| ue9-02-k11 | La question présentait l'enregistrement chronologique comme une règle sans exception. Elle oubliait la dérogation de L. 123-25 : les personnes physiques au réel simplifié peuvent n'enregistrer les créances et les dettes qu'à la clôture. | La question délimite son champ (« en principe »). Le verso ajoute la dérogation. La base devient [Règles essentielles#0, Règles essentielles#12]. |
| ue9-02-k12 | La question ne délimitait pas son champ. Les micro-entrepreneurs relèvent d'un régime dérogatoire (L. 123-28 : livre des recettes, registre des achats). | La question est rattachée à l'article R. 123-173 du Code de commerce. Le verso est inchangé. |
| ue9-02-k27 | La question (« Pourquoi est-il inexact d'affirmer que le PCG 2025 a supprimé le système abrégé ? ») donnait la réponse et ressemblait à une question piège. | Nouvelle question ouverte : « Qu'est devenu le système abrégé du PCG après la réécriture du plan de comptes par le règlement ANC n° 2022-06 ? ». Verso : il n'a pas été supprimé. |

La première relecture n'a fait ni suppression ni ajout.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-02-k07 et ue9-02-k08 | Les deux cartes se partageaient l'item Règles essentielles#8 et ne demandaient que les intitulés des comptes 70, 71, 72, 74 et 75. Ces intitulés sont déjà révisés avec les comptes du plan comptable (contrat, § 8). Les deux cartes devenaient de purs exercices de mémoire sur des numéros. | Fusion dans **k07**, qui passe en `comp` pour faire pendant à k06 sur la classe 6. Question : « Dans la classe 7 du PCG, quels comptes enregistrent les produits d'exploitation normale et courante ? ». Verso : 70 ventes, 71 production stockée, 72 production immobilisée, 74 subventions, 75 autres produits de gestion courante. **k08 est supprimée.** | PCG au 1er janvier 2026, classe 7 (Règles essentielles#8) |
| ue9-02-k20 | La question (« Quelles règles de forme le Code de commerce impose-t-il… ») admettait d'autres réponses justes : documents électroniques identifiés et datés (R. 123-173), mention de la pièce justificative (R. 123-174), conservation pendant dix ans. | Question resserrée sur sa source : « Selon l'article L. 123-22 du Code de commerce, quelles règles de forme s'imposent aux documents comptables d'un commerçant ? ». Le verso est inchangé. | C. com., art. L. 123-22 |
| ue9-02-k30 (supprimée) | Carte anecdotique : elle porte sur le changement d'intitulé du compte 6454 (« Pôle emploi » remplacé par « France Travail ») et n'appelle ni définition ni compréhension. Elle faisait aussi doublon avec la révision du compte 6454 du plan comptable. | Supprimée. L'item « Ce qui a changé récemment#3 » reste sans carte, ce que le contrat permet. | Règlement ANC n° 2026-03 (Ce qui a changé récemment#3) |
| ue9-02-k33 (supprimée) | Doublon : « Quelle différence entre le livre-journal et le grand livre ? ». Son verso juxtaposait mot pour mot ceux de k13 (livre-journal, opération par opération et jour par jour) et de k14 (grand livre, écritures ventilées selon le plan comptable, mouvements compte par compte). | Supprimée. k13 et k14 sont conservées, et k14 porte seule l'item Définitions#3. | C. com., art. R. 123-173 à R. 123-175 |

Les 26 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- L. 123-12, L. 123-22, L. 123-23, L. 123-25 et L. 123-28 ;
- R. 123-173 à R. 123-177, R. 123-203 et R. 123-204 ;
- PCG, art. 513-1 et art. 1121-1 (plan de comptes minimal, subdivisions) ;
- suppression des comptes 791, 796 et 797 ;
- règlement n° 2024-07 (autres fonds propres) ;
- maintien du système abrégé.

## Recherches

Une seule recherche WebSearch a été faite, limitée à `anc.gouv.fr`. La question était : le PCG range-t-il les charges d'exploitation normale et courante aux comptes 60 à 65 et les charges financières au compte 66 (carte k06, Règles essentielles#7) ?

Résultat : un document de l'ANC (annexe d'une consultation publique, qui reprend la présentation du PCG) range bien les charges d'exploitation normale et courante aux comptes 60 (achats), 61/62 (autres charges externes), 63 (impôts, taxes et versements assimilés), 64 (charges de personnel) et 65 (autres charges de gestion courante). Il range les charges de la gestion financière au compte 66. Le PCG au 1er janvier 2026 (classe 6) figure aussi parmi les résultats. La carte k06 est donc conservée telle quelle.

Aucune autre recherche n'a été jugée nécessaire. Les autres points étaient établis par les extraits officiels déjà portés dans la fiche ou par le rapport de relecture finale de la fiche (`rapports/ue9-02.md`).

## Points à reprendre dans la fiche

1. **Point de la première relecture, que je partage.** Aucun item ne porte sur le mécanisme de la partie double (débit et crédit, égalité des totaux, emplois et ressources), sur l'analyse des opérations en flux et en stocks ni sur la balance. Ces points figurent pourtant dans `programme.points` et dans le titre du chapitre. Faute d'item, aucune carte ne peut les porter. Les deux items rattachés à l'ancien art. 921-1 ont été retirés faute de source confirmée (voir `rapports/ue9-02.md`). Il faudrait retrouver le fondement officiel de la partie double dans le PCG en vigueur et rétablir au moins un item sur ce mécanisme.
2. **Règles essentielles#7 (classe 6).** La répartition « comptes 60 à 65 pour l'exploitation, compte 66 pour le financier » laisse croire qu'elle est exhaustive. Or les dotations de fin d'exercice passent par le compte 68, ventilé en 681 (exploitation), 686 (financier) et 687 (exceptionnel). Il faudrait compléter l'item d'après le texte de la classe 6 du PCG au 1er janvier 2026, sans quoi une carte fidèle à la fiche reste incomplète pour un correcteur.
3. **Remarque sur le contrat (§ 4), sans effet sur les cartes.** La formule « Un seul plan de comptes […] remplace les systèmes abrégé/développé » vise le plan de comptes. La fiche (Points de vigilance#3) précise à juste titre que le système abrégé de présentation des comptes subsiste (art. 822-1, modifié par le règlement n° 2024-07). Les deux énoncés sont compatibles, mais la formule du contrat gagnerait à être précisée pour éviter qu'une leçon ou une carte annonce la disparition du système abrégé.

## Classement des exercices

Le classement automatique des 18 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 17 | oui |
| `calcul` | 1 | non |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé entre les classeurs. Les 17 exercices de nature `notion` entrent dans les révisions espacées avec les 30 cartes ci-dessus et les comptes du plan comptable. L'exercice de nature `calcul` reste dans le chapitre mais n'est pas proposé en révision.
