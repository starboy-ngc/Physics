# Cartes de notions : ue9-06 (Stocks, dépréciations et provisions)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-06.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte des items de la fiche, sans recherche web. Elle a contrôlé 35 cartes et en a corrigé quatre (k06, k11, k31, k33). Elle a aussi relu et gardé k35, une carte qui venait d'une passe précédente interrompue.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, CGI, BOFiP, PCG modifié par le règlement ANC n° 2022-06) ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ou purement mécaniques.

   Elle a aussi vérifié qu'aucune carte ne demande de calcul, d'écriture chiffrée ni de chiffre millésimé. Une seule recherche WebSearch a été faite, limitée à legifrance.gouv.fr (voir « Recherches »). Les autres points de fond s'appuient sur les recherches déjà consignées dans `rapports/ue9-06.md`, `data/FAITS-CONFIRMES.md`, `data/POINTS-OUVERTS.md` et dans les rapports de cartes ue9-07, ue9-08 et ue6-01.
4. **Validation.** `node validate.js data/ue9/ue9-06.cartes.json` : ✓ (35 cartes, 9 déf.).

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. Aucune carte n'a été supprimée ni ajoutée dans cette relecture, et aucun identifiant n'a été renuméroté.
- **Répartition : 9 cartes `def`, 26 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte.
  - Les 20 « Règles essentielles » ont toutes au moins une carte.
  - Les 5 « Points de vigilance » ont chacun leur carte de compréhension.
  - Dans « Ce qui a changé récemment », les items #0, #1, #2 et #4 ont leur carte.
- **Items de fiche sans carte :**
  - **Chiffres et seuils#2** (taux normal de TVA, passage du TTC au HT). L'item est millésimé et appelle un calcul.
  - **Chiffres et seuils#3** (demande de restitution au plus tard le 31 décembre de la deuxième année). C'est un délai à décompter, rattaché à un article abrogé au 1er janvier 2027.
  - **Ce qui a changé récemment#3** (règlement ANC n° 2026-03). Il porte sur les produits des ventes et la renumérotation de l'article sur le résultat exceptionnel, pour des exercices ouverts à compter de 2027. Aucune règle du chapitre n'en dépend.
- **Chiffres et dates.** Les seuls chiffres sont stables et font partie d'une règle : douze mois et dix ans. Les dates citées sont des dates d'entrée en vigueur (exercices ouverts depuis le 1er janvier 2025, abrogation au 1er janvier 2027).

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-06-k31 | La réponse attribuait à l'ordonnance la règle selon laquelle les références aux anciennes dispositions du CGI renvoient au code des impositions sur les biens et services. Or la fiche (Ce qui a changé récemment#4) l'attribue au BOFiP. La question présentait aussi l'art. 272 comme « relatif aux créances irrécouvrables », alors que la fiche dit « TVA sur créances irrécouvrables ». | q : « … sur l'article 272 du CGI relatif à la TVA sur créances irrécouvrables ? ». r : « L'article 272 du CGI est abrogé à compter du 1er janvier 2027, l'ordonnance transférant la TVA dans le code des impositions sur les biens et services. Selon le BOFiP, les références aux anciennes dispositions du CGI s'entendent de celles de ce code qui les reprennent. » |
| ue9-06-k33 | La question omettait « jugée ». La fiche (Points de vigilance#3, qui cite R. 123-178, 5°) parle d'une valeur d'inventaire « pas jugée notablement inférieure » : c'est une appréciation, pas un simple constat. | q : « … lorsque la valeur d'inventaire n'est pas jugée notablement inférieure ? » |
| ue9-06-k06 | Dans « obtenu de sa vente », le possessif était ambigu : il suivait « l'utilité du bien pour l'entreprise » et pouvait renvoyer à autre chose que l'actif. | Remplacé par « obtenu de la vente de l'actif à la clôture », mot pour mot comme dans Définitions#4 (réponse de 68 mots). |
| ue9-06-k11 | Contexte incomplet : « selon le plan de comptes » ne disait pas quel plan. | q : « … pour comptabiliser les stocks selon le plan de comptes du PCG ? » |
| ue9-06-k35 (gardée) | Carte venue d'une passe précédente interrompue, avec des modifications non commitées. | Relue et gardée. Elle couvre Chiffres et seuils#1 : conservation des données d'inventaire dans les conditions de L. 123-22 (dix ans, chiffre stable) et organisation pour justifier chaque poste du bilan. Elle est fidèle, et `src` et `url` sont identiques à ceux de l'item. |

La première relecture n'a supprimé aucune carte.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-06-k30 | **Inexact par excès.** « Le résultat exceptionnel ne comprend plus que » les produits et charges liés à un événement majeur et inhabituel « ainsi que les écritures d'origine purement fiscale » : cette liste est présentée comme complète. Or le règlement n° 2022-06 classe aussi en résultat exceptionnel certaines corrections d'erreurs et les changements de méthode comptabilisés en résultat pour des raisons fiscales. | r : « **Dans le résultat d'exploitation (6815 / 7815).** Une dotation n'est exceptionnelle (6875 / 7875) que si elle se rattache directement à un événement majeur et inhabituel : le résultat exceptionnel est recentré sur ces événements et sur les écritures d'origine purement fiscale. » La réponse ne prétend plus être exhaustive et reprend la phrase de la fiche sur les dotations. Base, `src` et `url` sont inchangés. | PCG, art. 513-5 (règlement ANC n° 2022-06), citation de la fiche ; recherches anc.gouv.fr des relectures ue9-07 et ue6-01 |
| ue9-06-k34 | **Quasi-doublon et réponse incomplète.** La réponse reprenait presque mot pour mot la définition du passif de k03. Elle ne donnait qu'une condition, alors qu'un correcteur du DCG attend aussi, pour la constitution d'une provision, un montant évaluable de façon fiable. Cette condition est dans la fiche (Règles essentielles#15, cas exceptionnel du montant non évaluable). | q : « Selon le PCG, à quelles conditions une provision est-elle, en principe, comptabilisée à la clôture de l'exercice ? ». r : obligation à la clôture à l'égard d'un tiers, sortie de ressources probable ou certaine sans contrepartie au moins équivalente ; « **son montant peut en outre être évalué avec une fiabilité suffisante.** » k25 garde la conséquence du défaut de fiabilité (aucun passif, information en annexe). | PCG, art. 322-1, 322-2 et 322-4 (Règles essentielles#15) |
| ue9-06-k28 | **Ambiguïté.** « Comment les provisions sont-elles suivies d'une clôture à l'autre ? » admettait une autre bonne réponse : « dans le tableau des provisions de l'annexe ». | q : « Selon le PCG, que doit-on faire des provisions déjà constituées à chaque date d'établissement des comptes ? ». La réponse (revue et ajustement à la meilleure estimation) est inchangée. | PCG, art. 323-10, citation de la fiche (Règles essentielles#19) |
| ue9-06-k19 | **Formulation trop absolue.** « Seulement une fois la créance devenue définitivement irrécouvrable » excluait la récupération en cas d'annulation de l'opération, possible pour une créance litigieuse. La carte reprenait aussi la règle de la liquidation judiciaire, déjà donnée par k21. | r : « **Lorsque la créance est devenue définitivement irrécouvrable**, ce qu'il doit pouvoir démontrer (en cas de liquidation judiciaire, dès la date du jugement qui la prononce), et non au stade de la dépréciation. Celle-ci se calcule pourtant sur le hors taxes : déprécier le TTC est une erreur classique. » | CGI, art. 272 ; BOI-TVA-DED-40-10-20 (Points de vigilance#0, Règles essentielles#11) |
| ue9-06-k21 | **Doublon partiel avec k19.** Les deux cartes donnaient la même précision sur la liquidation judiciaire. | La précision est retirée de k21, qui garde sa question propre : les trois cas d'imputation ou de remboursement (résiliation, annulation, irrécouvrabilité définitive) et la rectification préalable de la facture. k19 garde la question du moment. | CGI, art. 272 (Règles essentielles#11) |
| ue9-06-k31 | **Question de pure mémoire d'une référence.** « Quel est l'effet de l'ordonnance n° 2025-1247 du 17 décembre 2025… ? » obligeait à retenir le numéro et la date de l'ordonnance pour comprendre la question. | q : « Que devient, à compter du 1er janvier 2027, l'article 272 du CGI relatif à la TVA sur créances irrécouvrables ? ». r : « **Il est abrogé** : l'ordonnance n° 2025-1247 du 17 décembre 2025 transfère la TVA dans le code des impositions sur les biens et services. Selon le BOFiP, les références… » La correction de fidélité de la première relecture (BOFiP) est conservée. | Recherche 1 (l'ordonnance existe sous ce numéro, JORFTEXT000053091516) ; fiche, textes (CGI, art. 272) |
| ue9-06-k09 | **Vrai dans le cas général seulement.** L'article L. 123-18 prévoit lui-même une exception à la non-comptabilisation de la plus-value : la réévaluation de l'ensemble des immobilisations corporelles et financières. La fiche n'en parle pas ; la carte ne peut donc pas l'ajouter. | La question délimite son champ : « … comment traite-t-on **en principe**, à la clôture, la plus-value constatée… ? ». La réponse est inchangée. | C. com., art. L. 123-18 |

Aucune carte n'a été supprimée ni ajoutée dans cette relecture. Les 28 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche.

Cartes examinées sans être modifiées :
- **k02** (inventaire). La définition « contrôle annuel de l'existence et de la valeur… » reprend la substance de L. 123-12, al. 2. Elle est juste, même si l'article R. 123-177 définit l'inventaire en d'autres termes (voir « Points à reprendre dans la fiche »).
- **k03 et k34** (passif, conditions de la provision). Après la correction de k34, les deux cartes se recoupent sur l'obligation envers un tiers, mais les questions sont distinctes : la définition d'un côté, les conditions de comptabilisation de l'autre.
- **k07 et k28** (la reprise est un produit). La dernière phrase de k28 redit k07, mais les questions sont distinctes : le classement au compte de résultat d'un côté, la révision des provisions de l'autre.
- **k18 et k19** (dépréciation sur le hors taxes). Les deux réponses se recoupent. k18 porte toutefois le traitement comptable (virement en 416, dépréciation 68174 / 491), et k19 le moment où la TVA est récupérée.
- **k17** (dépréciation des stocks). La phrase fiscale (BOFiP) suit une question posée « selon le PCG ». Elle complète la réponse sans la contredire.
- **k20** (compte 654). La perte est portée pour le hors taxes dans le cas, général, où la TVA est récupérable. La suppression du 6714 est conforme au plan de comptes 2026 (recherche 9 du rapport de la fiche).
- **k26, k27, k16, k22** (comptes 151, 152, 15, 39, 29, 59, 68173, 6815, 6865, 6875, 6866 et reprises). Ils sont conformes au plan de comptes 2026 restitué par les recherches 7 et 8 du rapport de la fiche.

## Recherches

Une seule recherche WebSearch a été faite, limitée à `legifrance.gouv.fr`.

1. **« ordonnance n° 2025-1247 du 17 décembre 2025 code des impositions sur les biens et services taxe sur la valeur ajoutée »** (legifrance.gouv.fr). Les résultats confirment que l'ordonnance existe : [Ordonnance n° 2025-1247 du 17 décembre 2025 portant recodification de la taxe sur la valeur ajoutée et diverses modifications du code des impositions sur les biens et services](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053091516), avec son [rapport au Président de la République](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053091491). Elle intègre la TVA au livre II de ce code. Sur le calendrier, la synthèse de la recherche indique que [l'article 49](https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000053091763) fixe l'entrée en vigueur au 1er septembre 2026, sauf pour certains articles qui ont leur propre date. Elle ne restitue pas la date propre à l'abrogation de l'art. 272. La date du 1er janvier 2027 retenue par la fiche (et par `POINTS-OUVERTS.md`, ue9-04) n'est donc pas contredite, mais elle n'est pas confirmée mot pour mot.

La lecture directe de l'article 49 n'a pas abouti : l'accès réseau à legifrance.gouv.fr est refusé depuis cet environnement. Aucune autre recherche n'a été jugée nécessaire. Le périmètre du résultat exceptionnel (k30) avait déjà été établi par les recherches des relectures ue9-07 et ue6-01 sur anc.gouv.fr.

## Points à reprendre dans la fiche

1. **Ce qui a changé récemment#1 (résultat exceptionnel).** « Il ne comprend plus que les produits et charges directement liés à un événement majeur et inhabituel, ainsi que les écritures d'origine purement fiscale » est trop absolu. Le règlement ANC n° 2022-06 y classe aussi certaines corrections d'erreurs (sauf celles qui corrigent une écriture imputée directement sur les capitaux propres) et les changements de méthode comptabilisés en résultat pour des raisons fiscales. Le même point a été relevé pour les fiches ue9-07, ue9-08 et ue6-01.
2. **Ce qui a changé récemment#4 et `textes` (CGI, art. 272 et 278) : calendrier de la recodification.** D'après la recherche 1 et `POINTS-OUVERTS.md` (ue9-04), l'article 49 de l'ordonnance fixe son entrée en vigueur au 1er septembre 2026, avec des dates propres à certains articles. La fiche date du 1er janvier 2027 l'abrogation de l'art. 272. Il faut vérifier sur le texte consolidé de l'article 49 que cette date est bien celle de l'abrogation de l'art. 272. `POINTS-OUVERTS.md` (ue4-05) mentionne aussi une période transitoire prolongée par l'ordonnance n° 2026-671, dont la fiche ne parle pas.
3. **Définitions#1 (inventaire) : citation à vérifier.** La citation « L'inventaire est le contrôle annuel de l'existence et de la valeur de tous les éléments d'actif et de passif à la date de clôture » est présentée comme tirée de L. 123-12 et R. 123-177. Or, à ma connaissance, R. 123-177 définit l'inventaire comme « un relevé de tous les éléments d'actif et de passif au regard desquels sont mentionnées la quantité et la valeur de chacun d'eux à la date d'inventaire ». L'idée de contrôle de l'existence et de la valeur vient de L. 123-12, al. 2. Ce point n'a pas fait l'objet d'une recherche : il faut relire R. 123-177 et remplacer la citation par le texte exact.
4. **Règles essentielles#2 (plus-value non comptabilisée).** L'article L. 123-18 prévoit lui-même la réévaluation de l'ensemble des immobilisations corporelles et financières. Sans cette réserve, l'item se lit comme une règle sans exception ; la carte k09 la délimite par « en principe ».
5. **Règles essentielles#9 et #10, Points de vigilance#0 (TVA sur créances douteuses).** L'item suppose que la TVA a déjà été collectée et reversée, ce qui est le cas des livraisons de biens. Pour les prestations de services, la TVA est exigible à l'encaissement (sauf option pour les débits) : sur une créance impayée, elle n'a pas été reversée et il n'y a rien à récupérer. La fiche ne le précise pas.
6. **Points de la première relecture, repris tels qu'ils ont été transmis** (le texte reçu s'interrompt au troisième point) :
   - Définitions#2, Définitions#5 et Points de vigilance#4 : l'URL du PCG est « …/Reglements/Recueils/PCG_janvier2026/PCG--1er-janvier-2026.pdf », alors que les autres items citent le même PCG à « …/Plans%20comptables/2026/PCG--1er-janvier-2026.pdf ». Deux URL pour un même document : il faut vérifier que les deux répondent et n'en garder qu'une.
   - Règles essentielles#18 : la `src` principale est « PCG, art. 323-2 et 323-3 », mais l'URL pointe vers une note pédagogique de l'ANC sur la durabilité (février 2025), pas vers le PCG. Ce n'est pas le texte officiel de la règle d'évaluation des provisions.
   - Règles essentielles#8 : la `src` « règles d'évaluation des stocks à la clôture » est vague et ne cite pas d'article précis (texte reçu tronqué à cet endroit).

## Classement des exercices

Le classement automatique des 16 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 9 | oui |
| `calcul` | 7 | non |
| `chiffre` | 0 | — |

Les classeurs ont été en désaccord sur trois exercices, chaque fois entre `notion` et `calcul`. Les trois ont été tranchés en `calcul` :
- **#11** : variation du stock de produits finis (Télia), à chiffrer pour la présenter au compte de résultat ;
- **#18** : montant de la dépréciation globale d'un portefeuille de VMP (Gamma en plus-value latente, Bêta en moins-value latente), à chiffrer sans compenser les deux lignes ;
- **#19** : écriture de clôture sur la provision pour litige, après le paiement d'un montant différent de celui qui avait été provisionné.

Les 9 exercices de nature `notion` entrent dans les révisions espacées avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 7 exercices de nature `calcul` restent dans le chapitre mais ne sont pas proposés en révision.
