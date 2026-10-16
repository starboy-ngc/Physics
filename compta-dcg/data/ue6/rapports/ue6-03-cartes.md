# Cartes de notions : ue6-03 (Tableaux de flux : tableau de financement et flux de trésorerie)

*15 octobre 2026*

Fichier : `data/ue6/ue6-03.cartes.json`. Fiche de référence : `data/ue6/ue6-03.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 32 cartes (k01 à k32) ont été écrites à partir de la seule fiche documentaire. Elles suivent la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité.** Un premier relecteur vérifie que chaque carte dit ce que dit la fiche, sans rien ajouter, et qu'elle respecte la forme exigée.
3. **Relecture d'exactitude.** Un second relecteur, indépendant, contrôle chaque carte sur quatre points :
   - **Exactitude** : la carte est-elle juste au regard du droit et des normes en vigueur au 15 octobre 2026 (Code de commerce, CGI, PCG modifié par le règlement ANC n° 2022-06, règlement ANC n° 2020-01) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne précise pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse, juste, serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Aucun calcul, aucun chiffre millésimé.**

   Quand l'item de fiche lui-même est en cause, la fiche n'est pas modifiée. La carte est corrigée pour rester à la fois exacte et portée par ses items de base, et l'item est signalé plus bas.
4. **Deux cycles de relecture.**
   - **Cycle précédent.** La relecture de fidélité a corrigé k04, k16 et k31. La relecture d'exactitude a corrigé huit cartes, dont deux fusions, et supprimé k10, k27 et k31. Elle n'a fait aucune recherche web. Il restait 29 cartes (rappel plus bas).
   - **Reprise (ce rapport).** Une nouvelle relecture de fidélité a contrôlé les 29 cartes et corrigé k18. La relecture d'exactitude a ensuite recontrôlé les 29 cartes : elle en a corrigé quatre (k03, k18, k21, k23), sans suppression ni ajout.
5. **Recherches.** Deux recherches lors de la reprise, limitées au site anc.gouv.fr (détail plus bas). Le plan comptable du dépôt (`data/pcg/`), déjà vérifié, a servi pour les comptes 131, 441, 481, 512, 519, 1648, 1688, 657, 757 et 6862.

Validation : `node validate.js data/ue6/ue6-03.cartes.json` renvoie « ✓ (cartes, 29 (11 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées (reprise) | 29 |
| Cartes au final | 29 (k01 à k32 ; k10, k27 et k31 supprimées lors du cycle précédent) |
| Définition (`def`) | 11 |
| Compréhension (`comp`) | 18 |
| Corrigées par la relecture de fidélité (reprise) | 1 (k18) |
| Corrigées par la relecture d'exactitude (reprise) | 4 (k03, k18, k21, k23) |
| Supprimées / ajoutées (reprise) | 0 / 0 |

Les sept items de la section « Définitions » et les quinze « Règles essentielles » ont tous au moins une carte. Les points de vigilance #0 à #3 et le changement récent #0 donnent des cartes de compréhension (k16, k18, k29, k30).

**Items de la fiche sans carte**, tous écartés volontairement :

- **Chiffres et seuils#0** (taux normal de l'IS) et **#2** (taux réduit des PME, millésimé 2025) : taux fixés par la loi de finances, exclus des révisions espacées.
- **Ce qui a changé récemment#1** (règlement ANC n° 2023-03, intitulé du compte 757) : simple rappel de référence, sans notion propre ; l'intitulé donné est en outre incomplet (voir plus bas).
- **Ce qui a changé récemment#2** et **Points de vigilance#4** (règlement ANC n° 2024-05, lien DSCG) : la carte k31 qui les portait doublait k02 ; elle a été supprimée lors du cycle précédent.
- **Ce qui a changé récemment#3** (calendrier d'application du programme) : aucune notion à retenir.

## Corrections de la première relecture (fidélité à la fiche, reprise)

Résultat : 29 cartes contrôlées, 1 corrigée, aucune supprimée ni ajoutée.

| cible | problème | correction |
|---|---|---|
| k18 | La réponse contredisait ses deux items de base. Elle disait que la subvention est une ressource durable « dès l'exercice de son octroi, même si elle n'est pas encore encaissée », alors que Règles essentielles#6 dit « l'année de son encaissement » et Points de vigilance#2 parle de « subvention d'investissement encaissée ». Le relecteur n'est pas revenu pour autant à la formule de la fiche : selon le plan comptable du dépôt (`data/pcg/classe1.json`), le compte 131 est crédité à l'octroi, et la formule de la fiche est donc douteuse. | La réponse ne dit plus rien du moment où la subvention est prise en compte. Elle ne garde que ce sur quoi la fiche et l'exactitude s'accordent : « <b>Comme une ressource durable (compte 131).</b> Il ne faut pas la confondre avec sa quote-part virée au résultat (compte 747), produit calculé sans flux, qui est retranché dans la CAF additive. » La question, la base, `src` et `url` ne changent pas. |

Ce relecteur n'a fait aucune recherche web. Il a relu `data/pcg/classe1.json`, `classe5.json` et `classe7b.json`, qui confirment les restrictions déjà portées par k07, k15, k16 et k20 : elles restreignent la fiche sans la contredire.

## Corrections de la relecture d'exactitude (reprise)

| cible | problème | correction | source |
|---|---|---|---|
| k03 | Vraie seulement dans un cas non dit. Le règlement ANC n° 2020-01 prévoit deux modèles de tableau des flux de trésorerie. Celui de l'article 282-44, établi à partir du résultat d'exploitation des entités intégrées, comporte lui aussi une ligne « marge brute d'autofinancement des sociétés intégrées ». Dans ce modèle, la marge n'est donc pas « obtenue à partir du résultat net ». | Question restreinte au modèle visé par la fiche (art. 282-43) : « Dans le modèle de tableau des flux de trésorerie du règlement ANC n° 2020-01 établi à partir du résultat net, qu'est-ce que la marge brute d'autofinancement des sociétés intégrées ? ». La réponse commence désormais par le contenu de la ligne : « <b>Le résultat net des sociétés intégrées corrigé des charges et produits sans incidence sur la trésorerie ou non liés à l'activité</b> (amortissements et provisions, plus-values de cession). » La suite ne change pas. | Règlement ANC n° 2020-01, art. 282-43 et 282-44 (recherche n° 1) ; fiche, Définitions#2 (`src` : modèle « établi à partir du résultat net ») |
| k18 | Doublon partiel. Après la correction de fidélité, la réponse se terminait par « qui est retranché dans la CAF additive » : c'est mot pour mot la réponse de k17, qui porte sur le traitement de la quote-part virée au résultat. Revoir k18 donnait donc la réponse de k17. | La fin de phrase est retirée. Réponse : « <b>Comme une ressource durable (compte 131).</b> Il ne faut pas la confondre avec sa quote-part virée au résultat (compte 747), produit calculé sans flux. » La carte reste muette sur le moment (octroi ou encaissement), comme l'a voulu la relecture de fidélité. | Contrat §8 (doublons) ; fiche, Points de vigilance#2 |
| k21 | Vocabulaire périmé. La question parlait de frais d'émission « portés en charges à répartir » et la réponse renvoyait au compte 481. Or, depuis le règlement ANC n° 2022-06, ce compte s'intitule « Frais d'émission des emprunts ». L'étalement passe par une dotation au compte 6862 (et non plus 6812), sans transfert de charges. | Question : « Comment les frais d'émission d'emprunt inscrits à l'actif pour être étalés (compte 481) sont-ils traités dans le tableau de financement du PCG ? ». Réponse : « <b>Ils constituent un emploi stable de l'exercice de leur engagement.</b> Leur étalement ultérieur est une dotation, neutralisée dans la CAF. » La règle est inchangée. | Plan de comptes PCG 2025, comptes 481 et 6862 (`data/pcg/classe4.json`, `classe6b.json`) ; PCG, art. 212-11 |
| k23 | Vraie seulement dans un cas non dit. L'article L. 232-13 du Code de commerce fixe le délai de neuf mois pour la mise en paiement des « dividendes en numéraire ». Le paiement en actions obéit à ses propres règles (art. L. 232-18 et suivants). | Question : « Selon le Code de commerce, dans quel délai maximal les dividendes en numéraire doivent-ils être mis en paiement ? ». Réponse inchangée. | C. com., art. L. 232-13, al. 2 |

**Cartes contrôlées et maintenues sans changement** : k01, k02, k04 à k09, k11 à k17, k19, k20, k22, k24 à k26, k28 à k30 et k32 (25 cartes). Quatre d'entre elles appellent une remarque :

- **k09** cite les « charges à répartir sur plusieurs exercices » parmi les emplois stables. C'est le libellé du modèle du PCG repris par la fiche. La recherche n° 2 n'a pas permis de vérifier si le modèle 2025 l'a remplacé par « frais d'émission des emprunts ». La carte est gardée, et le point est signalé dans la fiche.
- **k20** : on pourrait citer d'autres retraitements des dettes financières, comme les primes de remboursement des obligations. Mais ceux-ci ne portent pas sur la reconstitution des remboursements, et la fiche ne les mentionne pas. La réponse attendue au DCG reste « concours bancaires courants et intérêts courus ».
- **k28** : dans les modèles de l'OEC et de l'ANC, l'impôt sur la plus-value suit la cession, présentée « nette d'impôt ». La carte ne peut pas le dire, car la fiche est muette. Comme elle a perdu son « jamais » lors du cycle précédent, elle reste juste en principe ; l'item de fiche est signalé.
- **k32** reprend ce que disent k01 et k02. Elle est gardée parce qu'elle est la seule à opposer les deux tableaux : c'est la question classique de l'épreuve.

## Rappel du cycle précédent

| cible | correction |
|---|---|
| k04 | Ajout, pris dans la fiche, de la définition de la CAF : « produits encaissables moins charges décaissables, hors cessions ». |
| k07 | Le compte 519 est rattaché aux seuls concours bancaires courants ; les soldes créditeurs de banques sont des comptes 512 créditeurs. |
| k09 et k10 | Fusion des deux moitiés de la liste des emplois stables dans k09 ; k10 supprimée. |
| k15 | Question restreinte aux immobilisations corporelles et incorporelles (compte 757). |
| k16 | Date d'application du règlement ANC n° 2022-06 précisée (exercices ouverts à compter du 1er janvier 2025). |
| k20 | Comptes d'intérêts courus cités à titre d'exemple (1648, 1638), la liste n'étant pas fermée. |
| k22 | Question limitée au cas sans acompte sur dividende ; formule réservée à l'absence d'autre mouvement sur les réserves et le report à nouveau. |
| k26 et k27 | Fusion des flux de financement « en plus » et « en moins » dans k26 ; k27 supprimée. |
| k28 | « Jamais en investissement ni en financement » retiré. |
| k31 | D'abord resserrée, puis supprimée comme doublon de k02. |

## Recherches faites

Deux recherches sur les trois autorisées, toutes deux limitées à anc.gouv.fr.

1. **`règlement ANC 2020-01 tableau des flux de trésorerie "marge brute d'autofinancement" sociétés intégrées 282-43`**
   - **Confirmé.** Le règlement ANC n° 2020-01 consacre une section au tableau des flux de trésorerie, dans sa version consolidée (recueil 2026 compris). Le modèle de l'article 282-44 est établi à partir du résultat d'exploitation des entités intégrées. Lui aussi fait apparaître une ligne « marge brute d'autofinancement des sociétés intégrées », suivie du flux net de trésorerie généré par l'activité.
   - **Non lu.** Le texte même de l'article 282-43.
   - **Conséquence.** k03 est restreinte au modèle établi à partir du résultat net.
   - Sources : [Règlement ANC n° 2020-01, version recueil](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2020/Reglt_2020_01/Reglt_2020_01_version_recueil.pdf) ; [Règlement ANC n° 2020-01, version recueil 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/recueil/REGLT-2020_01-VERSION-RECUEIL2026.pdf) ; [Règlement ANC n° 2020-01, version recueil 2024](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/Recueils/Comptes%20consolid%C3%A9s/2024/Reglt_2020_01_version_recueil2024.pdf) ; [Règlement ANC n° 2024-05](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2024/R2024_05/REGLT_2024_05_Recueil.pdf).
2. **`PCG 2025 tableau de financement emplois "charges à répartir sur plusieurs exercices" "distributions mises en paiement au cours de l'exercice"`**
   - **Confirmé.** Les versions du PCG au 1er janvier 2025 et au 1er janvier 2026 comportent toujours un chapitre I « Tableau de financement ».
   - **Non confirmé.** Le libellé exact des emplois dans le modèle 2025 (« charges à répartir sur plusieurs exercices » ou « frais d'émission des emprunts »).
   - **Conséquence.** k09 garde le libellé de la fiche. k21 ne parle plus de « charges à répartir » pour le compte 481, dont l'intitulé est « Frais d'émission des emprunts » dans le plan de comptes 2025.
   - Sources : [PCG, version au 1er janvier 2025](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/PCG--1er-janvier-2025.pdf) ; [PCG, version au 1er janvier 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/PCG--1er-janvier-2026.pdf) ; [Plan de comptes PCG 2025](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/Plan-de-comptes-PCG-2025.pdf).

Les autres points ont été vérifiés sans recherche :

- **Plan comptable du dépôt.**
  - `classe1.json` : 131 « Subventions d'investissement octroyées », crédité à l'octroi par le débit du 441 ou du 512 ; 1648 et 1688 sont des comptes d'intérêts courus.
  - `classe4.json` : 481 « Frais d'émission des emprunts » ; 441 pour les subventions accordées non encaissées.
  - `classe5.json` : 519 « Concours bancaires courants », le découvert étant un solde créditeur du 512.
  - `classe6b.json` et `classe7b.json` : 657 et 757 pour les seules immobilisations incorporelles et corporelles ; 6862 pour l'étalement des frais d'émission.
- **Connaissance des textes.** C. com., art. L. 232-12 (acomptes), L. 232-13 (dividendes en numéraire), L. 232-18 (paiement en actions) et L. 123-13.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#6 et Points de vigilance#2** (première relecture, confirmé). La subvention d'investissement (131) y est présentée comme une ressource durable « l'année de son encaissement ». Or le compte 131 est crédité à l'octroi, éventuellement par le débit du 441, et le tableau de financement part des variations du bilan. Seul le tableau des flux de trésorerie retient la subvention à l'encaissement (« subventions d'investissement reçues »).
2. **Définitions#3** (première relecture). La parenthèse « (produits encaissables moins charges décaissables, hors cessions) » suit « EBE » alors qu'elle définit la CAF. Il faut la rattacher explicitement à la CAF.
3. **Définitions#6 et Règles essentielles#14** (première relecture). Le compte « (519) » est accolé aux « concours bancaires courants et soldes créditeurs de banques ». Le 519 ne contient que les concours bancaires courants ; les soldes créditeurs de banques sont des comptes 512 créditeurs.
4. **Règles essentielles#5 et Points de vigilance#1** (première relecture). Le compte 757 et le classement de la plus-value en résultat d'exploitation ne visent que les immobilisations incorporelles et corporelles. Les cessions d'immobilisations financières passent en 6671 et 7671.
5. **Ce qui a changé récemment#1** (première relecture). L'intitulé du compte 757 est incomplet : l'intitulé exact est « Produits des cessions d'immobilisations incorporelles et corporelles ».
6. **Règles essentielles#10** (première relecture ; son texte a été tronqué dans la transmission, complété ici). La formule des dividendes (résultat N−1 − variation des réserves − variation du report à nouveau) ne vaut qu'en l'absence d'acompte sur dividende prélevé sur le résultat N (C. com., art. L. 232-12, al. 2). Elle suppose aussi qu'aucun autre mouvement n'affecte les réserves (incorporation au capital, par exemple).
7. **Chiffres et seuils#1 et Règles essentielles#10** (nouveau). L'article L. 232-13 ne fixe le délai de neuf mois que pour la mise en paiement des « dividendes en numéraire ». Il faut le préciser.
8. **Définitions#2** (nouveau). La définition de la marge brute d'autofinancement « à partir du résultat net » ne vaut que pour le modèle de l'article 282-43. Le modèle de l'article 282-44, établi à partir du résultat d'exploitation, comporte aussi cette ligne. Deux autres remarques :
   - l'item écrit « sociétés intégrées » alors que son `src` parle d'« entités intégrées » ;
   - Définitions#1 et Points de vigilance#4 parlent d'« un modèle », alors que le règlement en prévoit deux, tous deux en trois fonctions.
9. **Règles essentielles#9** (`t` et `src`). Le compte 481 y est désigné comme « Charges à répartir sur plusieurs exercices ». Avec le plan de comptes 2025, il s'intitule « Frais d'émission des emprunts », et l'étalement passe par le compte 6862 (au lieu de 6812). Il faudrait aussi vérifier si le modèle 2025 du tableau de financement (Règles essentielles#1) garde le libellé « charges à répartir sur plusieurs exercices ».
10. **Règles essentielles#13.** « Jamais en investissement ni en financement » est trop absolu. Dans les modèles de l'OEC et du règlement ANC n° 2020-01, les cessions sont présentées « nettes d'impôt » : l'impôt afférent à la plus-value suit la cession dans les flux d'investissement. Mieux vaut écrire « en principe ».
11. **Chiffres et seuils#0.** Le taux normal de l'IS est fixé par la loi de finances. Il devrait être marqué millésimé, et non `stable`.

## Classement des exercices

Les exercices QCM, QCM multiples et de classement (tri) du chapitre ont été classés automatiquement selon leur nature.

| nature | nombre |
|---|---|
| `notion` (définition, règle, qualification, choix d'un compte, sans calcul) | 14 |
| `calcul` (montant, taux, prorata, délai à décompter) | 3 |
| `chiffre` (rappel d'un chiffre millésimé) | 0 |

Les trois exercices de nature `calcul` sont #3, #14 et #24.

**Un désaccord, tranché en `calcul`.** Il porte sur l'exercice #3 : « Une immobilisation de valeur nette comptable 20 000 € est cédée pour 35 000 €. Pour quel montant la cession figure-t-elle dans les ressources durables du tableau de financement ? ». Un classement le donnait en `notion`, l'autre en `calcul`. Il est retenu en `calcul`, car il faut identifier un montant, et il sort donc des révisions espacées. La règle qu'il illustre reste révisée par la carte k15 : la cession figure pour son prix, la valeur comptable étant neutralisée.

Les 14 exercices de nature `notion` entrent dans les révisions espacées, avec les 29 cartes.
