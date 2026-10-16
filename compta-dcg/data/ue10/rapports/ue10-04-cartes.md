# Cartes de notions : ue10-04 (Stocks, contrats à long terme et opérations en devises)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-04.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle n'a fait aucune recherche web.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante de la première, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, CGI et BOFiP, PCG modifié par les règlements ANC n° 2018-01, 2022-06 et 2023-03, et règlement ANC n° 2026-03, applicable aux exercices ouverts à compter du 1er janvier 2027 ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Cette relecture s'est faite en deux temps. Le premier passage a corrigé k26, k28 et k33 et supprimé k34. Après la reprise du traitement, le second passage a relu de nouveau les 34 cartes restantes une à une, en les confrontant à la fiche et aux textes. Il n'a trouvé aucune autre erreur et n'a rien changé.
4. **Recherches.** Aucune recherche web n'a été faite pendant la relecture des cartes (voir « Recherches »).
5. **Validation.** La commande `node validate.js data/ue10/ue10-04.cartes.json` renvoie ✓ : 34 cartes, dont 11 définitions.

## Bilan

- **Nombre de cartes : 34.** Le jeu en comptait 35 au départ. La carte k34 a été supprimée, et rien n'a été renuméroté : l'identifiant k34 reste donc libre.
- **Répartition : 11 cartes `def` et 23 cartes `comp`.**
- **Couverture de la fiche :**
  - les 5 items de « Définitions » ont chacun au moins une carte ;
  - les 18 « Règles essentielles » et les 8 « Points de vigilance » sont tous couverts ;
  - dans « Chiffres et seuils », les items #0 (exécution d'un contrat à long terme sur au moins deux exercices) et #3 (cours de conversion) sont couverts ;
  - dans « Ce qui a changé récemment », les items #2 et #3 (règlement ANC n° 2026-03) sont couverts, par la carte k24.
- **Items de fiche sans carte :**
  - **Chiffres et seuils#1 et #2.** Ce sont des listes de numéros de comptes (stocks et variations, opérations en devises). Ces comptes sont déjà révisés avec le plan comptable.
  - **Ce qui a changé récemment#0** (règlement ANC n° 2022-06, comptes 151 et 152). Sa carte k34 a été supprimée.
  - **Ce qui a changé récemment#1** (règlement ANC n° 2023-03). Il n'a pas eu de carte dès la rédaction. Son seul apport au chapitre est le compte 756, que la carte k30 reprend.

  Le contrat n'exige une carte que pour chaque item de « Définitions ».
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les dates citées sont des dates de textes ou d'entrée en vigueur, pas des chiffres annuels : règlements n° 2018-01 et 2026-03, exercices ouverts à compter du 1er janvier 2027.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue10-04-k03 | L'item de base (Règles essentielles#0) cite la règle d'entrée du C. com., art. L. 123-18 : les biens produits sont enregistrés à leur coût de production, les biens acquis à titre gratuit à leur valeur vénale. La réponse n'en disait rien. Aucune autre carte ne couvrait cette règle, et le plafond de 35 cartes empêchait d'en ajouter une. | Ajout d'une phrase de contraste : « Les biens produits sont, eux, enregistrés à leur coût de production et les biens acquis à titre gratuit à leur valeur vénale. » La réponse compte désormais 56 mots. |
| ue10-04-k27 | La carte écrivait « sous réserve de l'article 420-6 », alors que la fiche écrit « sous réserve des dispositions particulières de l'article 420-6 ». | La formulation de la fiche est reprise : « sous réserve des dispositions particulières de l'article 420-6 ». |
| ue10-04-k29 | Rien dans la question ne situait le référentiel. Elle n'était donc pas entièrement compréhensible sans contexte. | La question commence désormais par « Selon le PCG, ». Elle compte 28 mots. |
| ue10-04-k32 | Dans la réponse, « de façon extra-comptable » ne portait que sur la réintégration des gains latents. Or la fiche (Points de vigilance#3) applique ce traitement à tout l'écart entre résultat comptable et résultat fiscal, donc aussi à la déduction des pertes latentes. | Nouvelle formulation : « Ils sont pris en compte dans le résultat imposable de l'exercice, de façon extra-comptable : déduction des pertes latentes (476) et réintégration des gains latents (477), qui ne sont jamais portés en résultat comptable. » La phrase sur la réintégration de la provision est conservée. |

La première relecture n'a supprimé ni ajouté aucune carte. Elle a porté la date `maj` au 2026-10-16.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-04-k26 | La règle du cours du jour de l'opération a une exception : une acquisition couverte relève de la comptabilité de couverture (art. 628-1 et suivants), que l'item de base mentionne. La question ne délimitait pas son champ, si bien qu'un correcteur pouvait aussi attendre le cours de couverture. | La question délimite désormais son champ : « Hors opération couverte, à quel cours le PCG convertit-il en euros le coût d'entrée des stocks et immobilisations acquis en devises ? ». La réponse est inchangée. | PCG, art. 420-1 et 420-5 ; règlement ANC n° 2015-05 (Règles essentielles#12) |
| ue10-04-k28 | « Une perte latente qualifiée d'instrument de couverture » est inexact. C'est l'opération en devise qui porte la perte qui est qualifiée d'instrument de couverture, pas la perte elle-même. | Nouvelle formulation, reprise de Règles essentielles#14 (dans la base de la carte) : « une opération en devise en perte latente qualifiée d'instrument de couverture ne donne lieu à aucune provision ». | PCG, art. 420-6 et 628-7 (Règles essentielles#14) |
| ue10-04-k33 | « Le PCG seul » pouvait se lire comme excluant le Code de commerce. Or celui-ci régit aussi ces opérations dans les comptes individuels (art. L. 123-18 et R. 123-178, cités par k02, k03, k08 et k12 à k14). Une réponse juste comme « le Code de commerce et le PCG » aurait été contredite au verso. | La réponse commence désormais par « <b>Le PCG, et non les normes IFRS</b> ». La suite ne change pas : l'art. L. 233-24 ne vise que les comptes consolidés ; IAS 2, IFRS 15 et IAS 21 s'appliquent en consolidé IFRS. | C. com., art. L. 233-24 (Points de vigilance#5) |
| ue10-04-k34 (supprimée) | Carte de pure mémoire sur des numéros de comptes : « Sous quel compte le règlement ANC n° 2022-06 range-t-il les provisions pour pertes de change et pour pertes sur contrats ? ». Les cartes k20, k21 et k27 donnent déjà les comptes 1515 et 1516 dans leur contexte, et ces comptes sont révisés avec le plan comptable (contrat, § 8). Le regroupement des provisions pour charges sous la racine 152 est exact, mais étranger au chapitre. | Supprimée. L'item « Ce qui a changé récemment#0 » reste sans carte, ce que le contrat permet. | Règlement ANC n° 2022-06 ; plan de comptes 2026, comptes 151 et 152 (Ce qui a changé récemment#0) |

Le second passage n'a apporté aucune correction de plus. Il a jugé les 31 cartes non retouchées exactes au 15 octobre 2026, sans ambiguïté qui justifie une retouche et sans doublon. Il a notamment vérifié :

- **Code de commerce.**
  - Art. L. 123-18 : coût d'entrée ; coût moyen pondéré ou PEPS seulement, donc pas de « dernier entré, premier sorti » ; dépréciation, que la dépréciation soit définitive ou non ; plus-value non comptabilisée.
  - Art. R. 123-178, 2°, 4° et 5° : coût de production, valeur actuelle, valeur d'inventaire. La tolérance « pas notablement inférieure » est réservée aux immobilisations non financières.
- **PCG, art. 211-7, 213-9 et 213-30 à 213-35 :** définition des stocks, coûts d'emprunt des actifs éligibles, capacité normale et sous-activité, coûts administratifs, méthodes de sortie, identification spécifique.
- **CGI, art. 38, 3 et 4, et BOFiP :**
  - stocks au prix de revient, ou au cours du jour de la clôture s'il est inférieur ;
  - refus de considérer systématiquement comme sortis les articles entrés en dernier ;
  - écarts de conversion compris dans le résultat imposable, de façon extra-comptable ;
  - réintégration de la provision pour pertes de change.
- **Contrats à long terme (PCG, art. 121-5, 122-2 à 122-5 et 622-1 et suivants) :**
  - définition (exécution sur au moins deux exercices) ;
  - méthode à l'achèvement et méthode à l'avancement ; la seconde est méthode de référence depuis le règlement ANC n° 2018-01 ;
  - marge nulle quand le résultat à terminaison ne peut être estimé de façon fiable ;
  - perte à terminaison provisionnée en 1516 dès qu'elle est probable, sous déduction des pertes déjà constatées ; à l'achèvement, dépréciation des en-cours d'abord, puis provision pour le complément ;
  - passage à l'avancement irréversible, son effet étant imputé en report à nouveau ;
  - révision des estimations avec effet prospectif.
- **Règlement ANC n° 2026-03 :** transfert des contrats à long terme aux art. 523-1 à 523-8 pour les exercices ouverts à compter du 1er janvier 2027, avec application anticipée possible. Le rapport `rapports/ue10-04.md` l'atteste (recherches 10, 11 et 16).
- **Opérations en devises (PCG, art. 420-1 à 420-8 et 628-11) :**
  - comptes 476 et 477 ;
  - provision 1515 ;
  - position globale de change ;
  - symétrie de la couverture (4768 et 4778) ;
  - liquidités en devises en résultat ;
  - écarts réalisés en 656 et 756 (opérations commerciales) ou en 666 et 766 (opérations financières).

## Recherches

Aucune recherche WebSearch n'a été faite, ni au premier passage ni au second, faute de doute réel sur le fond.

Les points sensibles avaient déjà été établis par recherche lors de la relecture de la fiche (`rapports/ue10-04.md`, passe du 14 octobre 2026, 16 recherches). Ils sont aussi consignés dans `data/FAITS-CONFIRMES.md` :
- règlement ANC n° 2026-03 et art. 523-1 à 523-8 ;
- art. 420-1, 420-6 et 420-7 dans leur version 2026 ;
- art. 213-32 à 213-35 ;
- CGI, art. 38, 4 ;
- comptes 152x du plan de comptes 2026.

Un point a été examiné sans recherche : à l'achèvement, la dépréciation des en-cours absorbe-t-elle la perte à terminaison « à hauteur des coûts engagés » (carte k21, Points de vigilance#2) ? Cette lecture est celle de la fiche et de la doctrine courante : la perte est d'abord constatée par une dépréciation des en-cours, dans la limite de leur montant, et le complément est provisionné. La carte est donc conservée telle quelle.

## Points à reprendre dans la fiche

1. **Règles essentielles#17.** Point relevé par la première relecture et partagé par la seconde. La source citée, « BOI-BIC-CHG-50-70 » (url BOFiP 1413-PGP), manque dans la liste « textes » de la fiche. Il faudrait l'y ajouter pour garder la traçabilité.
2. **Points de vigilance#2.** Point relevé par la première relecture et partagé par la seconde. L'url de l'item est celle du C. com., art. L. 123-18 (Légifrance). Or l'essentiel de son contenu vient du PCG, art. 622-1 et suivants : produit de l'exercice à l'avancement, couverture de la perte à terminaison à l'achèvement. La carte k21, dont c'est le premier item de base, hérite donc d'une url peu pertinente. Il faudrait citer le PCG en premier dans la source et prendre l'url du recueil PCG au 1er janvier 2026.
3. **Points de vigilance#5.** « En comptes individuels, seul le PCG s'applique » peut se lire comme excluant le Code de commerce, qui s'applique aussi (art. L. 123-18 et R. 123-178). Il faudrait écrire : « en comptes individuels, les règles françaises (Code de commerce et PCG) s'appliquent, et non les IFRS ».
4. **Points de vigilance#4.** La fiche écrit : « une perte latente qualifiée d'instrument de couverture ne donne lieu à aucune provision ». Or c'est l'opération en devise qui porte la perte latente qui est qualifiée d'instrument de couverture (PCG, art. 420-6). Il faudrait reprendre la formulation exacte de Règles essentielles#14.
5. **Chiffres et seuils#3.** La fiche écrit « cours du jour de l'opération pour le coût d'entrée des actifs acquis en devises ». Contrairement à Règles essentielles#12, l'item ne rappelle pas que les acquisitions couvertes relèvent de la comptabilité de couverture. Il faudrait ajouter « hors opérations couvertes ».

## Classement des exercices

Le chapitre compte 18 exercices QCM, QCM multiples ou de classement. Leur classement automatique donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 15 | oui |
| `calcul` | 3 | non |
| `chiffre` | 0 | — |

Les classeurs n'ont relevé aucun désaccord. Les 15 exercices de nature `notion` entrent dans les révisions espacées, avec les 34 cartes ci-dessus et les comptes du plan comptable. Les 3 exercices de nature `calcul` restent dans le chapitre, mais ne sont pas proposés en révision.
