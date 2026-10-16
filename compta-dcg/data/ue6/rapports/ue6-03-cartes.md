# Cartes de notions : ue6-03 (Tableaux de flux : tableau de financement et flux de trésorerie)

15 octobre 2026. Fichier : `data/ue6/ue6-03.cartes.json`. Fiche de référence : `data/ue6/ue6-03.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 32 cartes (k01 à k32) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Le premier relecteur a vérifié les 32 cartes contre la fiche, sans recherche web. Il en a corrigé 3 (k04, k16, k31), sans suppression ni ajout.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 32 cartes au regard du droit et des normes en vigueur au 15 octobre 2026 : Code de commerce, PCG modifié par le règlement ANC n° 2022-06, règlement ANC n° 2020-01 et modèle de l'OEC pour le tableau des flux de trésorerie. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse, et il a écarté les doublons. Bilan : 8 cartes corrigées, dont 2 fusions, et 3 supprimées, sans ajout.
4. **Recherches.** Aucune recherche web n'a été faite. Les points de doute ont été tranchés avec le plan comptable du dépôt (`data/pcg/`), déjà vérifié : comptes 131, 441, 481, 512/519, 1638, 1648, 1688, 657, 757, 6671, 7671, 6862.

`node validate.js data/ue6/ue6-03.cartes.json` : ✓ (29 cartes, 11 déf.).

## Bilan

- **29 cartes** : 11 de définition (`def`) et 18 de compréhension (`comp`). Les identifiants k10, k27 et k31 sont libres : ces cartes ont été supprimées, et rien n'a été renuméroté.
- Chaque item des sections « Définitions » (7 items) et « Règles essentielles » (15 items) a au moins une carte.
- **Items de la fiche sans carte :**
  - Chiffres et seuils#0 (taux normal de l'IS) et #2 (taux réduit des PME, millésimé 2025) : ce sont des taux fixés par la loi de finances, exclus des révisions.
  - Ce qui a changé récemment#1 (règlement ANC n° 2023-03, intitulé du compte 757) : simple rappel de référence, sans notion propre. L'intitulé donné par la fiche est en outre incomplet (voir plus bas).
  - Ce qui a changé récemment#2 et Points de vigilance#4 (lien DSCG, règlement ANC n° 2024-05) : la carte k31, qui les portait, doublait k02 et a été supprimée.
  - Ce qui a changé récemment#3 (calendrier du programme) : aucune notion à retenir.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| k04 | La réponse à « Qu'est-ce que la CAF ? » ne donnait que sa place dans le tableau (« première ressource durable »). Le contenu de la notion, que la fiche donne entre parenthèses (Définitions#3), manquait. | Ajout, repris de la fiche : « produits encaissables moins charges décaissables, hors cessions ». La suite est inchangée : déterminée à partir de l'EBE, vérifiée à partir du résultat de l'exercice. |
| k16 | « Depuis le règlement ANC n° 2022-06 » laissait croire à une application dès 2022. La fiche (Ce qui a changé récemment#0) vise les exercices ouverts à compter du 1er janvier 2025. | « Dans le résultat d'exploitation. Avec le règlement ANC n° 2022-06 (exercices ouverts à compter du 1er janvier 2025), la CAF neutralise les comptes 657 et 757 ; les sujets antérieurs à 2025 neutralisaient 675 et 775. » |
| k31 | La question « quel modèle […] le règlement ANC n° 2020-01 prévoit-il ? » admettait plusieurs réponses : la fiche cite deux modèles (art. 282-43 et 282-44). | Question : « Pour les comptes consolidés, abordés au DSCG, comment le règlement ANC n° 2020-01 organise-t-il le tableau des flux de trésorerie ? » Réponse : « En trois fonctions… ». (La carte a ensuite été supprimée par la relecture d'exactitude.) |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k07 | « Concours bancaires courants et soldes créditeurs de banques (compte 519) » : le compte 519 ne contient que les concours bancaires courants. Les soldes créditeurs de banques sont des comptes 512 à solde créditeur. | « Les disponibilités diminuées des concours bancaires courants (compte 519) et des soldes créditeurs de banques. » | Plan de comptes PCG 2025, comptes 512 et 519 |
| k09 et k10 (k10 supprimée) | Les deux cartes coupaient en deux la liste des emplois stables, et chaque question contenait la réponse de l'autre (« Hormis les distributions… » / « Hormis les acquisitions… »). | Fusion dans k09 : « Quels sont les emplois stables de la première partie du tableau de financement du PCG ? ». La réponse donne les cinq emplois et les met en regard des ressources durables (acquisitions/cessions, réduction/augmentation des capitaux propres, remboursements/augmentation des dettes financières). Base : Règles essentielles#1 et #0. k10 est supprimée. | PCG, chapitre « Tableau de financement », première partie |
| k15 | Question posée pour « une cession d'immobilisation » en général, alors que la réponse cite le compte 757. Avec le PCG 2025, ce compte ne reçoit que les cessions d'immobilisations incorporelles et corporelles ; les cessions d'immobilisations financières passent en 7671/6671. | Question restreinte : « Pour quelle valeur la cession d'une immobilisation corporelle ou incorporelle figure-t-elle dans les ressources… ? ». Réponse inchangée. | Plan de comptes PCG 2025, comptes 657, 757, 6671 et 7671 |
| k18 | « Ressource durable l'année de son encaissement » : le compte 131 est crédité à l'octroi de la subvention (notification), par le débit du 441 si elle n'est pas encore versée. Le tableau de financement, qui part des variations du bilan, retient donc la subvention l'exercice de son octroi. La créance éventuelle figure en « hors exploitation ». | Question : « Comment la subvention d'investissement obtenue par l'entreprise apparaît-elle… ? » Réponse : « Comme une ressource durable (compte 131), dès l'exercice de son octroi, même si elle n'est pas encore encaissée. » La mise en garde sur le compte 747 est conservée. | PCG, art. 312-1 ; plan de comptes PCG 2025, comptes 131 et 441 |
| k20 | « Les intérêts courus (comptes 1648, 1638) » : présentée ainsi, la liste paraît fermée. Or il existe d'autres comptes d'intérêts courus (1688, par exemple). | « … les intérêts courus (par exemple comptes 1648 ou 1638)… ». | Plan de comptes PCG 2025, comptes 1638, 1648 et 1688 |
| k22 | Réponse vraie seulement dans un cas particulier non dit. Un acompte sur dividende versé en N est prélevé sur le résultat N, et non sur N−1. Quant à la formule « résultat N−1 − variation des réserves − variation du report à nouveau », elle devient fausse dès que les réserves bougent pour une autre raison, par exemple une incorporation au capital. | Question : « Hors acompte sur dividende, de quel résultat proviennent les dividendes mis en paiement au cours de l'exercice N dans le tableau de financement du PCG ? » La formule est précédée de « En l'absence d'autre mouvement sur les réserves et le report à nouveau ». | C. com., art. L. 232-12 (al. 2 : acomptes) et L. 232-13 |
| k26 et k27 (k27 supprimée) | k27 (« en diminution des flux de financement ») reprenait dans sa réponse toute la réponse de k26 (« augmentent les flux de financement ») : deux cartes pour une seule liste. | Fusion dans k26 : « Quels flux composent les flux de financement du tableau des flux de trésorerie ? » Réponse : en plus, l'augmentation de capital en numéraire, les subventions d'investissement reçues et les emprunts nouveaux ; en moins, les dividendes versés et les remboursements d'emprunts. k27 est supprimée. | Règlement ANC n° 2020-01, art. 282-43 et 282-44 ; OEC, avis n° 30 |
| k28 | « Jamais en investissement ni en financement » est trop absolu. Dans les modèles de l'OEC et de l'ANC, les plus-values et les cessions figurent « nettes d'impôt » : l'impôt afférent à la plus-value suit donc la cession dans les flux d'investissement. | Réponse : « Dans les flux liés à l'activité, comme dans la CAF qui les déduit : ce sont des charges décaissables du compte de résultat. » La réponse attendue au DCG ne change pas. | OEC, avis n° 30 ; règlement ANC n° 2020-01, modèles de tableau des flux de trésorerie |
| k31 (supprimée) | Doublon de k02 : la réponse de k02 dit déjà que le tableau des flux de trésorerie classe les flux en trois fonctions et que c'est le modèle du règlement ANC n° 2020-01 pour les comptes consolidés. Le reste de k31 se réduisait à des numéros d'articles et de règlement à apprendre par cœur. | Carte supprimée. | Contrat §8 (doublons, cartes sans intérêt) |

Les 21 autres cartes ont été contrôlées sans changement : k01 à k06, k08, k11 à k14, k16, k17, k19, k21, k23 à k25, k29, k30 et k32.

## Recherches faites

Aucune (0 sur 3 autorisées). Les points vérifiés l'ont été avec le plan comptable du dépôt, déjà vérifié :

- `data/pcg/classe1.json` :
  - 131 est crédité à la date d'octroi (notification définitive), par le débit du 441 ou du 512 ;
  - 1638, 1648 et 1688 sont tous des comptes d'intérêts courus ;
  - 169 est le compte des primes de remboursement.
- `data/pcg/classe4.json` : 481 s'intitule « Frais d'émission des emprunts » depuis le règlement ANC n° 2022-06 ; 441 enregistre les subventions accordées non encore encaissées.
- `data/pcg/classe5.json` : 519 « Concours bancaires courants ».
- `data/pcg/classe6b.json` et `classe7b.json` :
  - 657/757 visent les seules immobilisations incorporelles et corporelles, et 6671/7671 les immobilisations financières ;
  - 6862 remplace 6812 pour l'étalement des frais d'émission d'emprunt.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Définitions#3 (CAF)** (relevé par la première relecture) : la parenthèse « (produits encaissables moins charges décaissables, hors cessions) » suit « EBE ». Elle devient ainsi ambiguë, car « hors cessions » ne se comprend que pour la CAF. Mieux vaut la rattacher explicitement à la CAF.
2. **Points de vigilance#1** (relevé par la première relecture, confirmé ici) : « la plus-value de cession est dans le résultat d'exploitation » n'est vrai que pour les immobilisations incorporelles et corporelles (657/757). Les cessions d'immobilisations financières relèvent du résultat financier (6671/7671). Même restriction pour Règles essentielles#5, qui cite le compte 757 pour toutes les cessions.
3. **Ce qui a changé récemment#1** (relevé par la première relecture ; son texte a été tronqué dans la transmission, complété ici) : l'intitulé du compte 757 donné par la fiche (« produits des cessions d'immobilisations ») est incomplet. L'intitulé exact est « Produits des cessions d'immobilisations incorporelles et corporelles ».
4. **Règles essentielles#6 et Points de vigilance#2** : la subvention d'investissement n'est pas une ressource durable « l'année de son encaissement ». Elle l'est l'exercice de son octroi, quand le compte 131 est crédité, éventuellement par le débit du 441. Seul le tableau des flux de trésorerie la retient à l'encaissement (« subventions d'investissement reçues »).
5. **Règles essentielles#13** : « jamais en investissement ni en financement » est trop absolu. Dans les modèles de l'OEC et du règlement ANC n° 2020-01, plus-values et cessions sont présentées « nettes d'impôt » : l'impôt afférent à la plus-value suit la cession dans les flux d'investissement. Mieux vaut écrire « en principe » ou mentionner cette exception.
6. **Règles essentielles#10** : la formule des dividendes (résultat N−1 − variation des réserves − variation du report à nouveau) ne vaut qu'en l'absence d'acompte sur dividende prélevé sur le résultat N (C. com., art. L. 232-12, al. 2). Elle suppose aussi qu'aucun autre mouvement n'affecte les réserves (incorporation au capital, par exemple). À préciser.
7. **Définitions#6 et Règles essentielles#14** : « concours bancaires courants et soldes créditeurs de banques (519) ». Le compte 519 ne couvre que les concours bancaires courants ; les soldes créditeurs de banques sont des comptes 512 créditeurs.
8. **Règles essentielles#9 (src)** : le compte 481 y est cité sous son ancien intitulé « Charges à répartir sur plusieurs exercices ». Avec le plan de comptes 2025, il s'intitule « Frais d'émission des emprunts », et l'étalement passe par le compte 6862 (au lieu de 6812).
9. **Chiffres et seuils#0** : le taux normal de l'IS est un taux fixé par la loi de finances, susceptible de changer. Il devrait être marqué millésimé, et non `stable`.

## Classement des exercices

Le classement automatique porte sur les 17 exercices QCM, QCM multiples et de classement du chapitre :

| nature | nombre |
|---|---|
| notion | 14 |
| calcul | 3 |
| chiffre | 0 |

Les trois exercices de nature calcul sont #3, #14 et #24.

Un désaccord a été tranché : **#3** (« Une immobilisation de valeur nette comptable 20 000 € est cédée pour 35 000 €. Pour quel montant la cession figure-t-elle dans les ressources durables du tableau de financement ? »). Un classement le donnait en notion, l'autre en calcul ; il est retenu en **calcul**, car il faut identifier un montant. Il sort donc des révisions espacées. La règle qu'il illustre (la cession figure pour son prix de cession, la valeur comptable étant neutralisée) reste révisée par la carte k15.

Les 14 exercices de nature notion entrent dans les révisions espacées, avec les 29 cartes.
