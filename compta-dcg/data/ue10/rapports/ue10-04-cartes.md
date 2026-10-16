# Cartes de notions : ue10-04 (Stocks, contrats à long terme et opérations en devises)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-04.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle n'a fait aucune recherche web.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, CGI et BOFiP, PCG modifié par les règlements ANC n° 2018-01, 2022-06 et 2023-03, règlement ANC n° 2026-03 applicable aux exercices ouverts à compter du 1er janvier 2027) ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle n'a fait aucune recherche web (voir « Recherches »).
4. **Validation.** `node validate.js data/ue10/ue10-04.cartes.json` : ✓ (34 cartes, 11 déf.).

## Bilan

- **Nombre de cartes : 34.** Il y en avait 35 au départ. Une carte a été supprimée (k34), sans renumérotation : l'identifiant k34 reste vide.
- **Répartition : 11 cartes `def` et 23 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 5 items de « Définitions » ont chacun au moins une carte.
  - Les 18 « Règles essentielles » et les 8 « Points de vigilance » sont tous couverts.
  - Dans « Chiffres et seuils », les items #0 (contrat à long terme sur au moins deux exercices) et #3 (cours de conversion) sont couverts.
  - Dans « Ce qui a changé récemment », les items #2 et #3 (règlement ANC n° 2026-03) sont couverts.
- **Items de fiche sans carte :**
  - Chiffres et seuils#1 et #2 : ce sont des listes de numéros de comptes (stocks et variations, opérations en devises). Ces comptes sont déjà révisés avec le plan comptable ;
  - Ce qui a changé récemment#0 (règlement ANC n° 2022-06, comptes 151 et 152) : sa carte k34 a été supprimée ;
  - Ce qui a changé récemment#1 (règlement ANC n° 2023-03) : il est sans carte depuis la rédaction. Son seul apport pour le chapitre, le compte 756, est porté par k30.

  Le contrat n'impose une carte que pour chaque item de « Définitions ».
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les dates citées (règlements 2018-01 et 2026-03, exercices ouverts à compter du 1er janvier 2027) sont des dates de textes ou d'entrée en vigueur, pas des chiffres annuels.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue10-04-k03 | La réponse omettait la règle d'entrée du C. com., art. L. 123-18, pourtant citée dans l'item de base (Règles essentielles#0) : les biens produits sont enregistrés à leur coût de production et les biens acquis à titre gratuit à leur valeur vénale. Aucune autre carte ne couvrait cette règle, et le plafond de 35 cartes empêchait d'en ajouter une. | Ajout d'une phrase de contraste : « Les biens produits sont, eux, enregistrés à leur coût de production et les biens acquis à titre gratuit à leur valeur vénale. » La réponse passe à 56 mots. |
| ue10-04-k27 | « sous réserve de l'article 420-6 » ne reprenait pas exactement la fiche, qui écrit « sous réserve des dispositions particulières de l'article 420-6 ». | Remplacé par la formulation de la fiche : « sous réserve des dispositions particulières de l'article 420-6 ». |
| ue10-04-k29 | La question ne disait pas de quel référentiel elle relevait. Elle n'était donc pas entièrement compréhensible sans contexte. | La question commence désormais par « Selon le PCG, » (28 mots). |
| ue10-04-k32 | Dans la réponse, « de façon extra-comptable » ne portait que sur la réintégration des gains latents. Or la fiche (Points de vigilance#3) applique le traitement extra-comptable à tout l'écart entre résultat comptable et résultat fiscal, donc aussi à la déduction des pertes latentes. | Nouvelle formulation : « Ils sont pris en compte dans le résultat imposable de l'exercice, de façon extra-comptable : déduction des pertes latentes (476) et réintégration des gains latents (477), qui ne sont jamais portés en résultat comptable. » La phrase sur la réintégration de la provision est conservée. |

La première relecture n'a fait ni suppression ni ajout. Elle a porté la date `maj` au 2026-10-16.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-04-k26 | La question ne délimitait pas son champ. Or la règle du cours du jour de l'opération a une exception : une acquisition couverte relève de la comptabilité de couverture (art. 628-1 et suivants), que l'item de base mentionne. Un correcteur pouvait aussi attendre le cours de couverture. | La question délimite son champ : « Hors opération couverte, à quel cours le PCG convertit-il en euros le coût d'entrée des stocks et immobilisations acquis en devises ? ». La réponse est inchangée. | PCG, art. 420-1 et 420-5 ; règlement ANC n° 2015-05 (Règles essentielles#12) |
| ue10-04-k28 | « Une perte latente qualifiée d'instrument de couverture » est une formulation inexacte : ce n'est pas la perte que l'on qualifie d'instrument de couverture, c'est l'opération en devise qui la porte. | Remplacé par « une opération en devise en perte latente qualifiée d'instrument de couverture ne donne lieu à aucune provision », la formulation de Règles essentielles#14, qui figure dans la base de la carte. | PCG, art. 420-6 et 628-7 (Règles essentielles#14) |
| ue10-04-k33 | La réponse « Le PCG seul » pouvait se lire comme excluant le Code de commerce, qui régit lui aussi ces opérations dans les comptes individuels (art. L. 123-18, R. 123-178, cités par les cartes k02, k03, k08, k12 à k14). Une réponse juste comme « le Code de commerce et le PCG » aurait été contredite au verso. | Début de la réponse : « <b>Le PCG, et non les normes IFRS</b> ». La suite est inchangée : L. 233-24 ne vise que les comptes consolidés ; IAS 2, IFRS 15 et IAS 21 en consolidé IFRS. | C. com., art. L. 233-24 (Points de vigilance#5) |
| ue10-04-k34 (supprimée) | Carte de pure mémoire sur des numéros de comptes : « Sous quel compte le règlement ANC n° 2022-06 range-t-il les provisions pour pertes de change et pour pertes sur contrats ? ». Les comptes 1515 et 1516 sont déjà donnés, dans leur contexte, par k20, k21 et k27, et ils sont révisés avec le plan comptable (contrat, § 8). Le regroupement des provisions pour charges sous la racine 152 est exact, mais il est étranger au chapitre. | Supprimée. L'item « Ce qui a changé récemment#0 » reste sans carte, ce que le contrat permet. | Règlement ANC n° 2022-06 ; plan de comptes 2026, comptes 151 et 152 (Ce qui a changé récemment#0) |

Les 31 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- C. com., art. L. 123-18 : coût d'entrée, CMP ou PEPS seulement, dépréciation que la dépréciation soit définitive ou non, plus-value non comptabilisée ;
- C. com., art. R. 123-178, 2°, 4° et 5° : la tolérance « pas notablement inférieure » est réservée aux immobilisations non financières ;
- PCG, art. 211-7, 213-9 et 213-30 à 213-35 : définition des stocks, coûts d'emprunt, capacité normale et sous-activité, coûts administratifs, identification spécifique ;
- CGI, art. 38, 3 et 4, et BOFiP : cours du jour s'il est inférieur au prix de revient, refus du « dernier entré, premier sorti », écarts de conversion compris dans le résultat imposable, réintégration de la provision pour pertes de change ;
- contrats à long terme (PCG, art. 121-5, 122-2 à 122-5, 622-1 et suivants) :
  - achèvement et avancement ;
  - méthode de référence depuis le règlement ANC n° 2018-01 ;
  - marge nulle si le résultat à terminaison n'est pas fiable ;
  - perte à terminaison provisionnée en 1516 dès qu'elle est probable, sous déduction des pertes déjà constatées ;
  - passage à l'avancement irréversible et imputé en report à nouveau ;
  - révision des estimations avec effet prospectif ;
- règlement ANC n° 2026-03 : transfert des contrats à long terme aux art. 523-1 à 523-8 pour les exercices ouverts à compter du 1er janvier 2027. Le rapport `rapports/ue10-04.md` (recherches 10, 11 et 16) l'atteste ;
- opérations en devises (PCG, art. 420-1 à 420-8 et 628-11) :
  - comptes 476 et 477 ;
  - provision 1515 ;
  - position globale de change ;
  - symétrie de la couverture (4768 et 4778) ;
  - liquidités en devises en résultat ;
  - écarts réalisés en 656/756 (commercial) ou 666/766 (financier).

## Recherches

Aucune recherche WebSearch n'a été faite. Aucun point n'appelait de doute réel. Les points sensibles avaient déjà été établis par recherche lors de la relecture de la fiche (`rapports/ue10-04.md`, passe de recherche du 14 octobre 2026, 16 recherches). Ils sont aussi consignés dans `data/FAITS-CONFIRMES.md` :
- règlement ANC n° 2026-03 et art. 523-1 à 523-8 ;
- art. 420-1, 420-6 et 420-7 dans leur version 2026 ;
- art. 213-32 à 213-35 ;
- CGI, art. 38, 4 ;
- comptes 152x du plan de comptes 2026.

## Points à reprendre dans la fiche

1. **Règles essentielles#17 (point de la première relecture, partagé).** La source citée, « BOI-BIC-CHG-50-70 » (url BOFiP 1413-PGP), ne figure pas dans la liste « textes » de la fiche. Il faudrait l'y ajouter pour garder la traçabilité.
2. **Points de vigilance#2 (point de la première relecture, partagé).** L'url de l'item est celle du C. com., art. L. 123-18 (Légifrance). Or l'essentiel de son contenu vient du PCG, art. 622-1 et suivants : produit de l'exercice à l'avancement, couverture de la perte à terminaison à l'achèvement. La carte k21, dont c'est le premier item de base, hérite donc d'une url peu pertinente. Il faudrait placer le PCG en premier dans la source et prendre l'url du recueil PCG au 1er janvier 2026.
3. **Points de vigilance#5.** « En comptes individuels, seul le PCG s'applique » peut se lire comme excluant le Code de commerce (L. 123-18, R. 123-178), qui s'applique aussi. Il faudrait écrire « en comptes individuels, les règles françaises (Code de commerce et PCG) s'appliquent, et non les IFRS ».
4. **Points de vigilance#4.** « Une perte latente qualifiée d'instrument de couverture ne donne lieu à aucune provision » : c'est l'opération en devise portant la perte latente qui est qualifiée d'instrument de couverture (PCG, art. 420-6). Il faudrait reprendre la formulation exacte de Règles essentielles#14.
5. **Chiffres et seuils#3.** « Cours du jour de l'opération pour le coût d'entrée des actifs acquis en devises » ne rappelle pas que les acquisitions couvertes relèvent de la comptabilité de couverture, contrairement à Règles essentielles#12. Il faudrait ajouter « hors opérations couvertes ».

## Classement des exercices

Le classement automatique des 18 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 15 | oui |
| `calcul` | 3 | non |
| `chiffre` | 0 | — |

Les classeurs n'ont relevé aucun désaccord. Les 15 exercices de nature `notion` entrent dans les révisions espacées, avec les 34 cartes ci-dessus et les comptes du plan comptable. Les 3 exercices de nature `calcul` restent dans le chapitre, mais ils ne sont pas proposés en révision.
