# Cartes de notions : ue9-01 (Le bilan et le compte de résultat)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-01.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle a contrôlé 35 cartes et en a corrigé trois (k16, k24, k31). Elle n'en a ni supprimé ni ajouté.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, PCG modifié par le règlement ANC n° 2022-06) ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt.

   Elle a aussi vérifié qu'aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Trois recherches ont été faites sur des sites officiels (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-01.cartes.json` : ✓ (35 cartes, 14 déf.).

## Bilan

- **Nombre de cartes : 35.** Il y en avait 35 après la première relecture. La seconde relecture a fusionné k26 dans k24, puis l'a supprimée. Elle a ensuite ajouté k36. Rien n'a été renuméroté : l'identifiant k26 reste vide.
- **Répartition : 14 cartes `def` et 21 cartes `comp`.** k05 est passée de `def` à `comp`.
- **Couverture de la fiche.**
  - Les 9 items de « Définitions » ont chacun au moins une carte.
  - Les 16 items de « Règles essentielles » sont tous couverts.
  - Le seul item stable de « Chiffres et seuils » sans carte (#4, conservation pendant dix ans) en a maintenant une : k36.
  - Les items stables de « Ce qui a changé récemment » sont tous couverts.
  - Quatre des cinq « Points de vigilance » sont couverts.
- **Items de fiche sans carte :**
  - **Chiffres et seuils#0, #1 et #2** (seuils des micro, petites et moyennes entreprises). Ils sont millésimés. La règle stable des deux exercices consécutifs reste portée par k28.
  - **Ce qui a changé récemment#3** (décret n° 2024-152 relevant les seuils). Il est millésimé.
  - **Points de vigilance#3** (lien DSCG : renvoi de L. 233-21 à L. 123-14 pour les comptes consolidés). La recherche n° 3 l'a confirmé. Une carte ferait presque doublon avec k16 et k17, et apporterait peu au niveau du DCG.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres qui restent sont stables et font partie d'une règle : douze mois pour l'inventaire, deux exercices consécutifs, dix ans de conservation. Les dates citées (1er janvier 2025, 1er janvier 2027) sont des dates d'application de règlements.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-01-k24 | La réponse disait « Les produits et charges directement liés à un événement majeur et inhabituel », ce qui en faisait une condition suffisante. La fiche dit « les seuls produits et charges… » (Règles essentielles#13), donc une condition nécessaire. La formulation contredisait aussi l'exception de Ce qui a changé récemment#2 : les aides, remboursements et indemnités liés à l'événement qui compensent des charges d'exploitation vont en résultat d'exploitation. | La réponse commence désormais par « <b>Seuls les produits et charges directement liés à un événement majeur et inhabituel</b> », comme dans la fiche. Les écritures d'origine fiscale y « restent toutefois ». La phrase qui reprend la définition du Code de commerce (Règles essentielles#12) est conservée. |
| ue9-01-k31 | La réponse reprenait le renvoi « à l'article 531-5 du PCG » de Ce qui a changé récemment#4. Partout ailleurs, la fiche situe la définition du résultat exceptionnel à l'article 513-5 (Règles essentielles#13, Ce qui a changé récemment#2). Le renvoi est donc probablement une coquille de la fiche, et la carte ferait retenir un numéro d'article douteux. | Le numéro d'article est retiré. La réponse dit seulement que le règlement « reprend aussi la définition du résultat exceptionnel (événement majeur et inhabituel) ». Elle reste fidèle à la fiche, en moins précis. Le reste est inchangé : produits des ventes, application aux exercices ouverts à compter du 1er janvier 2027, application anticipée possible. |
| ue9-01-k16 | La question « Quelles qualités le Code de commerce exige-t-il des comptes annuels ? » admettait une autre réponse juste : la prudence, que les comptes annuels « doivent respecter » (Règles essentielles#8). | La question devient « Quelles trois qualités le Code de commerce exige-t-il des comptes annuels d'un commerçant ? ». Elle désigne ainsi sans ambiguïté le trio réguliers, sincères, image fidèle. La réponse est inchangée. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-01-k05 | **Définition tronquée.** La carte donnait comme définition du stock « un actif détenu pour être vendu dans le cours normal de l'activité, ou en cours de production ». Le texte de l'article 211-7 du PCG continue : « pour une telle vente, ou destiné à être consommé dans le processus de production ou de prestation de services, sous forme de matières premières ou de fournitures ». Avec cette carte, l'étudiant aurait retenu une définition qui exclut les matières premières et les fournitures. La fiche ne donne pas la suite du texte, et la carte ne peut pas l'ajouter. | La carte devient une carte de compréhension (`comp`) sur ce qui distingue un stock d'une immobilisation : leur destination. L'immobilisation sert de façon durable à l'activité. Le stock est « notamment » détenu pour être vendu ou en cours de production, et il relève de l'actif circulant. La base devient [Définitions#4, Définitions#3] ; `src` et `url` sont inchangés. | PCG, art. 211-7 (règlement ANC n° 2014-03 ; PCG consolidé 2016) ; recherche n° 1 |
| ue9-01-k06 | **Définition présentée comme exhaustive.** Pour l'article 511-2 du PCG, les sommes versées en contrepartie de consommations comprennent aussi « des avantages qui lui ont été consentis », que la fiche omet. La fiche ne dit pas non plus si l'article vise d'autres éléments (dotations, par symétrie avec les reprises citées pour les produits). | La réponse commence par « <b>Notamment comme les sommes ou valeurs versées ou à verser</b> ». Le reste est inchangé, et la carte reste juste sans rien ajouter à la fiche. | PCG, art. 511-2 (PCG au 1er janvier 2026) ; recherche n° 2 |
| ue9-01-k02 | **Simplification inexacte.** Pour l'article 211-1 du PCG, l'actif est « un élément générant une ressource » que l'entité contrôle. Ce n'est pas la ressource elle-même. La citation de la fiche (Définitions#1) le dit. | « c'est-à-dire un élément générant une ressource qu'elle contrôle du fait d'événements passés… » : la réponse est alignée sur la citation verbatim de la fiche. | PCG, art. 211-1 (citation de Définitions#1) |
| ue9-01-k21 | **Règle présentée comme absolue.** L'alinéa 2 de L. 123-21 admet, après inventaire, le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, lorsque sa réalisation est certaine et que le bénéfice global peut être évalué avec une sécurité suffisante. | La question délimite son champ : « En principe, selon le Code de commerce, quels bénéfices peuvent être inscrits dans les comptes annuels d'un exercice ? ». Le verso, fidèle à la fiche, est inchangé. La correction est la même que pour ue9-07-k11. | C. com., art. L. 123-21 |
| ue9-01-k27 | **Ambiguïté.** À « Où le résultat de l'exercice figure-t-il… ? », « dans le compte de résultat » était une réponse juste mais incomplète, que la personne aurait pu juger suffisante. | La question devient « Dans quels deux documents des comptes annuels le résultat de l'exercice apparaît-il ? ». Le verso est inchangé. | C. com., art. R. 123-190 ; PCG, art. 513-1 |
| ue9-01-k34 | **Imprécision.** « Un manuel antérieur peut encore classer cette opération en 67/77. » La quote-part de subvention virée au résultat est un produit : seule la classe 77 a pu la recevoir. La mention « 67/77 » de la fiche vise l'ensemble des opérations citées, cessions comprises. | « Un manuel antérieur à la réforme peut encore classer ce produit en 77, parmi les produits exceptionnels. » | Règlement ANC n° 2022-06 ; plan de comptes 2026 (compte 747) |
| ue9-01-k24 et k26 (k26 supprimée) | **Doublon.** Depuis la première relecture, la réponse de k24 comporte la réserve des écritures d'origine purement fiscale. Cette réserve est nécessaire pour que « seuls » soit exact. k26 demandait précisément le classement de ces écritures : connaître k24, c'était connaître k26. | Fusion : k24 précise désormais « aux comptes 687 et 787 ». k26 est supprimée, sans renumérotation. Ce qui a changé récemment#0 reste couvert par k29. | PCG, art. 513-5 (règlement ANC n° 2022-06) ; plan de comptes 2026, comptes 687 et 787 |
| ue9-01-k36 (ajoutée) | Chiffres et seuils#4 (C. com., art. L. 123-22 : conservation des documents comptables et des pièces justificatives pendant dix ans) est une règle stable, souvent demandée au DCG, et n'avait pas de carte. | Question : « Selon le Code de commerce, pendant combien de temps un commerçant conserve-t-il ses documents comptables et ses pièces justificatives ? ». Verso : pendant dix ans, qu'il s'agisse des documents comptables ou des pièces justificatives. « Selon le Code de commerce » écarte le délai fiscal, qui est différent. | C. com., art. L. 123-22 |

Les 27 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- C. com., art. L. 123-12, L. 123-13, L. 123-14, L. 123-16 à L. 123-16-2, L. 123-17, L. 123-19, L. 123-20, R. 123-181, R. 123-190, R. 123-192 et R. 123-195 ;
- PCG, art. 121-1, 122-1, 122-2, 321-1, 511-1, 512-1, 513-1 et 513-5 ;
- comptes 120, 129, 657, 757, 6671, 7671, 687, 787 et 747 du plan de comptes 2026.

Deux cartes ont été examinées sans être modifiées :
- **k29.** « Ils disparaissent » est aussitôt nuancé par le maintien du compte 791 pour les concessions d'aménagement (règlement ANC n° 2025-05). La carte reste donc exacte.
- **k31.** Elle porte sur un règlement applicable en 2027. Elle est conservée pour la session 2027 et ne cite plus de numéro d'article.

## Recherches

Trois recherches WebSearch ont été faites, limitées à des sites officiels.

1. **Définition du stock, PCG art. 211-7** (anc.gouv.fr). Le PCG consolidé de 2016 et le règlement ANC n° 2014-03 le confirment : « Un stock est un actif détenu pour être vendu dans le cours normal de l'activité, ou en cours de production pour une telle vente, ou destiné à être consommé dans le processus de production ou de prestation de services, sous forme de matières premières ou de fournitures. » La citation de la fiche est donc tronquée. Les extraits des versions consolidées de 2025 et 2026 étaient trop fragmentaires pour confirmer que la définition y porte toujours le numéro 211-7. Cette recherche fonde la correction de k05.
2. **Définition des charges, PCG art. 511-2** (anc.gouv.fr). Le PCG au 1er janvier 2026 vise les sommes ou valeurs versées ou à verser en contrepartie de marchandises, approvisionnements, travaux et services consommés « ainsi que des avantages » consentis à l'entité, puis en exécution d'une obligation légale. Les extraits ne donnent pas tout le texte. Cette recherche fonde la correction de k06. Elle montre aussi que le règlement ANC n° 2026-03 du 6 mars 2026 réécrit le titre V du PCG (« Charges et produits ») et renumérote ses articles : la définition des produits passe de l'article 512-1 à l'article 521-1.
3. **Renvoi de L. 233-21 à L. 123-14** (legifrance.gouv.fr). Le texte confirme, verbatim : « Il est fait application, le cas échéant, des dispositions prévues aux premier et deuxième alinéas de l'article L. 123-14. » L'article n'a pas été modifié depuis le 21 septembre 2000. Points de vigilance#3 est donc exact. Aucune carte n'en a été tirée (voir « Bilan »).

Aucune autre recherche n'a été jugée nécessaire. L'alinéa 2 de L. 123-21 (k21) et la durée de conservation de L. 123-22 (k36) relèvent du texte constant du Code de commerce.

## Points à reprendre dans la fiche

Points relevés par la première relecture :

1. **Ce qui a changé récemment#4 (« article 531-5 »).** La première relecture y voyait probablement une coquille pour 513-5. La recherche n° 2 nuance ce diagnostic. Le règlement ANC n° 2026-03 réécrit le titre V du PCG et renumérote ses articles (produits : 512-1 devient 521-1). « 531-5 » est donc vraisemblablement le **nouveau numéro**, à compter des exercices ouverts le 1er janvier 2027, de l'actuel article 513-5. La fiche devrait le dire explicitement : « futur article 531-5, actuel article 513-5 ». Le numéro reste à confirmer sur le texte du règlement.
2. **Points de vigilance#4 (comptes supprimés).** La parenthèse ne cite que « anciens comptes 675 et 775 supprimés ». Elle omet l'ancien compte 777, par lequel passait la quote-part de subvention d'investissement virée au résultat. Il faut aussi préciser que « 67/77 » ne vaut que pour l'ensemble des opérations citées : la quote-part de subvention, qui est un produit, n'a jamais été classée qu'en 77.
3. Le résultat transmis de la première relecture s'arrête au début d'un troisième point (« Ce qui a changé récemm… ») ; son contenu n'a pas été reçu.

Points relevés par la relecture d'exactitude :

4. **Définitions#4 (stock).** La définition et la citation sont tronquées. Il faut reprendre le texte complet de l'article 211-7 : « …ou en cours de production pour une telle vente, ou destiné à être consommé dans le processus de production ou de prestation de services, sous forme de matières premières ou de fournitures ». Il faut aussi vérifier le numéro d'article dans la version du PCG au 1er janvier 2026.
5. **Définitions#5 (charges).** Il faut compléter d'après le texte de l'article 511-2 : « ainsi que des avantages qui lui ont été consentis ». Il faut aussi vérifier si l'article vise d'autres éléments (dotations aux amortissements, dépréciations et provisions), par symétrie avec Définitions#6 qui cite les reprises.
6. **Définitions#1 (actif).** Le texte (`t`) écrit « une ressource qu'elle contrôle », alors que la citation de l'article 211-1 dit « un élément générant une ressource que l'entité contrôle ». Il faut aligner `t` sur la citation.
7. **Règles essentielles#9 (bénéfices réalisés).** L'item omet l'alinéa 2 de L. 123-21 : le bénéfice réalisé sur une opération partiellement exécutée peut être inscrit à certaines conditions. La parenthèse « (un gain latent n'est pas un produit) » se lit alors comme une règle sans exception. La même remarque a été faite pour ue9-07 (Règles essentielles#7).

## Classement des exercices

Le classement automatique des 20 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 19 | oui |
| `calcul` | 1 | non |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé entre les classeurs. Les 19 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Ce sont 13 QCM, 4 QCM multiples et 2 classements. Le seul exercice de nature `calcul` est le QCM sur les capitaux propres de la société Alcor, qu'il faut calculer à partir du total du bilan et des dettes. Il reste dans le chapitre mais n'est pas proposé en révision.
