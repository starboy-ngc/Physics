# Cartes de notions : ue10-05 (Actifs financiers, passifs financiers et provisions)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-05.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle a contrôlé les 35 cartes et n'a fait aucune recherche web.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, CGI et BOFiP, PCG modifié par les règlements ANC n° 2018-01 et 2022-06, règlement ANC n° 2026-03 (exercices ouverts à compter du 1er janvier 2027) ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a fait 2 recherches WebSearch, limitées au domaine anc.gouv.fr (voir « Recherches »).
4. **Validation.** `node validate.js data/ue10/ue10-05.cartes.json` : ✓ (35 cartes, 11 déf.).

## Bilan

- **Nombre de cartes : 35.** Il y en avait 35 au départ. La carte k25 a été supprimée (doublon de k24) et la carte k36 a été ajoutée. Rien n'a été renuméroté : l'identifiant k25 reste vide.
- **Répartition : 11 cartes `def` et 24 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 7 items de « Définitions » ont chacun au moins une carte.
  - Les 18 « Règles essentielles » et les 7 « Points de vigilance » sont tous couverts. Points de vigilance#6 l'est par la nouvelle carte k36.
  - Dans « Chiffres et seuils », seul l'item #1 (cours moyen du dernier mois) est couvert, par k11.
  - Dans « Ce qui a changé récemment », les items #0 et #1 (règlement ANC n° 2022-06) sont couverts, par k14, k21 et k33.
- **Items de fiche sans carte :**
  - Chiffres et seuils#0 (présomption au-delà de 10 % du capital) : la règle est déjà portée par k02, qui repose sur Règles essentielles#0 ;
  - Chiffres et seuils#2 (comptes de titres et de dépréciation) : c'est une liste de numéros de comptes, déjà révisée avec le plan comptable ;
  - Chiffres et seuils#3 (montant de la prime de remboursement) : c'est une formule de calcul, que le contrat exclut des cartes. La règle du compte 163 crédité du prix de remboursement est portée par k20 ;
  - Chiffres et seuils#4 (régime des sociétés mères) : c'est une règle fiscale chiffrée qui relève de l'UE 4, à la marge de ce chapitre ;
  - Ce qui a changé récemment#2 (règlement ANC n° 2026-03) : il porte surtout sur les produits des ventes. Pour ce chapitre, son seul apport est le transfert de l'art. 513-5 vers l'art. 531-5, qui figure dans la source de k34.

  Le contrat n'impose une carte que pour chaque item de « Définitions ».
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les dates citées sont des dates de textes ou d'entrée en vigueur, pas des chiffres annuels : « PCG 2025 », « depuis 2025 », règlement ANC n° 2018-01, exercices ouverts à compter du 1er janvier 2027. Le seuil de 10 % (k02) est un chiffre stable qui fait partie de la règle.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue10-05-k08 | La question disait « Selon le Code de commerce », alors que la réponse cite les comptes 6866 et 7866, qui viennent du plan de comptes du PCG (Règles essentielles#3). L'attribution était donc inexacte. | « Selon le Code de commerce » a été retiré. Nouvelle question : « Que fait-on à la clôture lorsque la valeur d'inventaire de titres détenus devient inférieure à leur valeur nette comptable ? » |
| ue10-05-k09 | La réponse tournait en rond (« elle n'est pas comptabilisée : la plus-value… n'est jamais enregistrée ») et ne donnait aucune précision pour aider à retenir. | La réponse oppose désormais les deux cas, selon Règles essentielles#2 : seule une valeur d'inventaire inférieure à la valeur nette comptable est constatée, par une dépréciation. La plus-value n'est jamais enregistrée en comptes individuels. |
| ue10-05-k16 | La règle fiscale de priorité aux titres les plus anciens était étendue à toutes les cessions. Or la fiche la limite aux « cessions de titres du portefeuille ». | Rétabli : « les cessions de titres du portefeuille sont réputées porter par priorité… ». |
| ue10-05-k17 | La réponse ajoutait « débit du compte 2768/5088 », un sens d'écriture que la fiche ne formule pas. La fiche dit : « constatés (2768…, 5088…) par le crédit de 762 ou 764 ». | La réponse reprend la formulation de la fiche : « au compte 2768 pour les titres immobilisés ou 5088 pour les VMP, par le crédit du compte 762 ou 764 ». |
| ue10-05-k20 | Phrase bancale : « Pour le prix de remboursement total, ni le nominal ni le prix d'émission ». | Corrigé en « Pour le prix de remboursement total, et non pour le nominal ni pour le prix d'émission ». Le reste est inchangé. |
| ue10-05-k21 | Construction mal accordée : « Soit en charges, soit répartis… ». | Corrigé en « Soit comptabilisés en charges, soit répartis sur la durée de l'emprunt… », comme dans la fiche. Le reste est inchangé. |
| ue10-05-k22 | La question « comment les intérêts courus sur emprunts sont-ils rattachés à l'exercice ? » admettait d'autres réponses justes (charge financière, constatation à la clôture…) que la ventilation par nature attendue. | Nouvelle question : « Selon le PCG 2025, dans quels comptes enregistre-t-on à la clôture les intérêts courus sur emprunts ? ». La réponse commence par « Dans un compte propre à chaque nature d'emprunt » (1618, 1638, 1648 ; 1688 limité aux autres emprunts). |
| ue10-05-k26 | La mise en gras coupait la phrase de définition (« Il s'agit notamment d'<b>une obligation…</b> »). | Toute la phrase de définition est mise en gras. Le contenu est inchangé et fidèle à Définitions#4. |
| ue10-05-k27 | « La réponse oubliait une condition donnée par Règles essentielles#13 : si le montant ne pe… » (le résultat relayé s'arrête à cet endroit). | D'après la version d'origine : la question passe de « À quelle condition » à « à quelles conditions ». La condition de fiabilité de l'évaluation est intégrée à la phrase principale, et la réponse ajoute « Elle est évaluée à la meilleure estimation de la sortie de ressources ». |

Le résultat relayé de la première relecture s'arrête au milieu de k27. On l'a comparé à la version d'origine des cartes (commit `f3776ee`). Cette comparaison montre six autres retouches de la même passe :
- **k13** : la question commence par « Selon le Code de commerce, ».
- **k19** : la mention « par le compte 6861 » est remplacée par la règle du remboursement partiel ou anticipé (Points de vigilance#1), et la base devient Définitions#5 et Points de vigilance#1.
- **k28** : la réponse se limite au traitement du passif non évaluable (mention en annexe, comme un passif éventuel). La phrase sur la meilleure estimation passe dans k27.
- **k29** : la question devient « Selon le Code de commerce, quelle règle s'applique… ». La réponse ne commence plus par « Aucune ».
- **k30** : la question devient « Selon le Code de commerce et le PCG, comment les engagements de retraite… sont-ils traduits… ».
- **k35** : la question précise « Selon le PCG » et « (compte 14) ». La réponse distingue 6872 (dotations) et 7872 (reprises).

La première relecture n'a fait ni suppression ni ajout. Elle a porté la date `maj` au 2026-10-16.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-05-k01 | La question « au sens du Code de commerce et du Plan comptable général » admettait une autre réponse juste : la définition du PCG (titres dont la possession durable est estimée utile à l'activité, notamment pour exercer une influence ou un contrôle), différente de celle donnée au verso. | La question devient « Selon le Code de commerce, qu'est-ce qu'une participation ? ». La réponse reste celle de l'art. R. 123-184 et finit par « En comptabilité, ils sont inscrits au compte 261 ». | C. com., art. R. 123-184 (Définitions#0) |
| ue10-05-k07 | La question « Quel lien existe entre l'option comptable… et le résultat fiscal ? » était trop ouverte. Un candidat pouvait répondre juste par une autre règle, absente de la fiche : l'étalement fiscal sur cinq ans des frais d'acquisition incorporés au coût des titres de participation (CGI, art. 209, VII). | La question devient fermée : « Peut-on retenir, pour le résultat fiscal, une option différente de celle choisie en comptabilité pour les frais d'acquisition des titres ? ». La réponse commence par « Non : le résultat fiscal suit le choix comptable ». | BOI-BIC-CHG-20-20-10 (Points de vigilance#0) |
| ue10-05-k09 | « La plus-value… n'est jamais enregistrée en comptes individuels » est faux dans deux cas que la carte ne disait pas. La réévaluation de l'ensemble des immobilisations corporelles et financières inscrit l'écart de réévaluation au passif (C. com., art. L. 123-18, al. 4). L'évaluation par équivalence des titres de participation de sociétés contrôlées de manière exclusive est aussi permise (C. com., art. L. 232-5). | La question porte sur le principe : « Quel principe le Code de commerce pose-t-il pour une plus-value latente constatée sur des titres à la clôture ? ». La réponse suit l'art. L. 123-18 : « Elle n'est pas comptabilisée », sans « jamais ». La base est réduite à Règles essentielles#2. | C. com., art. L. 123-18 (Règles essentielles#2) |
| ue10-05-k13 | « Pour les titres, toute baisse… est dépréciée » ignorait l'exception de la baisse anormale et momentanée des cours (carte k12). | Ajout de « en principe ». Règles essentielles#4 est ajouté en seconde base. | PCG, art. 221-7 et 222-1 (Règles essentielles#4) |
| ue10-05-k16 | La phrase fiscale (« pour le calcul des plus-values imposables, les cessions… sont réputées porter… sur les titres… les plus anciens ») élargissait l'art. 39 duodecies, 6 du CGI. Ce texte vaut « pour l'application des 1 à 3 », c'est-à-dire pour le régime des plus-values à court ou à long terme. Sa portée sur le prix de revient des titres cédés n'est pas établie par la fiche. La question, elle, ne porte que sur la règle comptable du Code de commerce. | La phrase fiscale est retirée. Réponse : « Au coût moyen pondéré d'acquisition ou selon la méthode « premier entré, premier sorti », les deux méthodes que le Code de commerce prévoit pour les biens fongibles. » | C. com., art. L. 123-18 (Règles essentielles#7) |
| ue10-05-k24 et k25 (k25 supprimée) | Doublon : la réponse de k25 (« Qu'est-ce qui distingue une dette d'une provision ? ») contenait mot pour mot celle de k24 (« Qu'est-ce qu'une provision ? »). | k24 reçoit le contraste avec la dette : « C'est ce qui la distingue d'une dette (fournisseurs, emprunts), passif certain dont l'échéance et le montant sont fixés de façon précise ». Sa base devient Définitions#4 et Points de vigilance#2. k25 est supprimée. | PCG, art. 321-1 et s. (Définitions#4, Points de vigilance#2) |
| ue10-05-k27 | Doublon partiel : la parenthèse « (sinon, simple mention en annexe) » donnait au verso la réponse de k28. | La parenthèse est retirée. La condition de fiabilité de l'évaluation reste dans la réponse. | PCG, art. 321-1, 322-1 et s. (Règles essentielles#13) |
| ue10-05-k31 | « Ne sont pas déductibles les provisions… de départ à la retraite » présentait cette exclusion comme la seule. Or l'art. 39, 1-5° du CGI en prévoit d'autres. | Remplacé par « Le texte exclut notamment les provisions constituées en vue du versement d'allocations en raison du départ à la retraite ou en préretraite ». | CGI, art. 39, 1-5° (Règles essentielles#16) |
| ue10-05-k36 (ajoutée) | Après la correction de k09, Points de vigilance#6 (lien DSCG) n'avait plus de carte. Or le contrat demande que les points de vigilance donnent des cartes de compréhension. | Nouvelle carte `comp` : « Dans des comptes consolidés établis selon les normes IFRS adoptées par l'Union européenne, quelles normes régissent les instruments financiers et les provisions ? ». Réponse : IFRS 9 et IAS 37, avec la dispense des règles françaises de consolidation. | C. com., art. L. 233-24 (Points de vigilance#6) |

Les 26 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- **Classement des titres** (C. com., art. R. 123-184 ; comptes 26, 27 et 50) : la finalité de la détention, la présomption au-delà de 10 %, les définitions des titres immobilisés, des TIAP et des VMP. Le compte 501 est supprimé depuis 2025 (recherche 1).
- **Évaluation des titres** (PCG, art. 221-1, 221-3, 221-6, 221-7 et 222-1) :
  - frais d'acquisition sur option, indépendante de celle des immobilisations corporelles et incorporelles ;
  - valeur d'utilité ;
  - cours moyen du dernier mois ;
  - valeur probable de négociation ;
  - exception de la baisse anormale et momentanée.
- **Dépréciation** (C. com., art. L. 123-18 et R. 123-178, 5°) : la dépréciation est dotée en 6866 et reprise en 7866 ; la tolérance « pas notablement inférieure » est réservée aux immobilisations non financières.
- **Cessions** (règlement ANC n° 2022-06) : cessions d'immobilisations financières en brut en 6671/7671 ; cessions de TIAP en net en 6672/7672 ; cessions de VMP en net en 6673/7673 ; suppression de 675/775.
- **Produits financiers** : intérêts courus en 2768 et 5088 ; dividendes en 761, 762 et 764 (C. com., art. L. 232-12).
- **Emprunts** (PCG, art. 212-10 et 212-11) :
  - 163 crédité du prix de remboursement ;
  - prime 169 amortie au prorata des intérêts ou par fractions égales ;
  - frais d'émission en charges ou étalés, en 481 et 6862 (recherche 2) ;
  - intérêts courus en 1618, 1638 et 1648, comme le confirme le contrat, § 6.
- **Passifs et provisions** (PCG, art. 321-1 et s.) : définitions du passif, de la provision et du passif éventuel ; conditions de comptabilisation ; meilleure estimation ; mention en annexe du passif non évaluable de façon fiable.
- **Obligation de provisionner** : elle s'applique même sans bénéfice (C. com., art. L. 123-20).
- **Engagements de retraite** (C. com., art. L. 123-13 ; PCG, art. 324-1) : mention en annexe, provision facultative au compte 1521, méthode de référence depuis le règlement ANC n° 2018-01.
- **Fiscalité des provisions** : conditions de déduction (CGI, art. 39, 1-5°) ; réintégration de la provision pour pertes de change (CGI, art. 38, 4).
- **Comptes de provisions** : comptes 151 et 152 (contrat, § 6) ; provisions réglementées en capitaux propres, dotées et reprises en résultat exceptionnel en 6872 et 7872 (PCG, art. 513-5).

## Recherches

Deux recherches WebSearch ont été faites, limitées au domaine `anc.gouv.fr`. Une troisième n'a pas paru nécessaire.

1. **« règlement ANC 2022-06 compte 501 « Parts dans des entreprises liées » supprimé valeurs mobilières de placement »**.
   - Le plan de comptes du PCG de janvier 2024 comporte encore le compte 501 « Parts dans des entreprises liées ». Dans le plan de comptes PCG 2025, la classe 50 commence directement au compte 502 « Actions propres ».
   - Les extraits ne montrent pas de mention expresse de la suppression dans le texte du règlement. La comparaison des deux plans suffit toutefois à confirmer la carte k05 (Définitions#2), qui est maintenue.
2. **« plan de comptes 2026 « 6862 » dotations aux amortissements des frais d'émission des emprunts compte 481 »**.
   - Le plan de comptes 2026 comporte le compte 481 « Frais d'émission des emprunts ». Il comporte aussi le compte 6862 « Dotations aux amortissements des frais d'émission des emprunts », à côté du 6861.
   - En 2024, ces frais figuraient au compte 4816, sous 481 « Charges à répartir sur plusieurs exercices ».
   - Le recueil PCG 2026 admet la répartition linéaire lorsque les résultats ne sont pas sensiblement différents.
   - Ces résultats confirment la carte k21 (Règles essentielles#11, Ce qui a changé récemment#1), qui est maintenue.

## Points à reprendre dans la fiche

1. **Points de vigilance#6.** « En comptes individuels, les plus-values latentes sur titres ne sont jamais comptabilisées » est trop absolu, pour deux raisons :
   - la réévaluation de l'ensemble des immobilisations corporelles et financières inscrit l'écart de réévaluation au passif (C. com., art. L. 123-18, al. 4) ;
   - les titres de participation de sociétés contrôlées de manière exclusive peuvent être évalués par équivalence (C. com., art. L. 232-5).

   Il faudrait écrire : « ne sont pas comptabilisées (C. com., art. L. 123-18), sauf réévaluation ou évaluation par équivalence ». La carte k09 ne s'appuie plus sur cet item.
2. **Règles essentielles#7.** « Pour le calcul des plus-values imposables » élargit l'art. 39 duodecies, 6 du CGI, qui vaut « pour l'application des 1 à 3 », c'est-à-dire pour le régime des plus-values à court ou à long terme. Il faudrait reprendre la formule du texte. Avant toute carte sur ce point, il faudrait aussi vérifier dans le BOFiP la règle applicable au prix de revient fiscal des titres cédés (coût moyen pondéré admis ou non). La carte k16 ne reprend plus cette phrase.
3. **Définitions#4.** La définition du passif éventuel ne reprend que le premier cas de l'art. 321-6 du PCG (obligation potentielle née d'événements incertains). Le second cas manque : une obligation dont il n'est pas probable ou certain qu'elle provoquera une sortie de ressources sans contrepartie au moins équivalente. C'est pourquoi la carte k26 doit garder « notamment ». Il faudrait compléter l'item.

## Classement des exercices

Le classement automatique des 20 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 17 | oui |
| `calcul` | 3 | non |
| `chiffre` | 0 | — |

Les classeurs ont été en désaccord sur deux exercices (numérotés à partir de 0 dans `ue10-05.json`), tous deux classés finalement en `calcul` :
- **#10** (cession d'une participation dépréciée, montants à l'appui) : notion / calcul → `calcul`. Il faut chiffrer les écritures de cession et de reprise.
- **#13** (obligation acquise coupon couru inclus) : notion / calcul → `calcul`. Il faut calculer le coupon couru.

Les 17 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 3 exercices de nature `calcul` (#10, #13 et #18) restent dans le chapitre, mais ils ne sont pas proposés en révision.
