# Cartes de notions : ue4-03 (Les bénéfices industriels et commerciaux)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-03.fiche.json` et d'elle seule. Elles respectent le contrat (section 8) : une question par carte, aucun calcul, aucun chiffre millésimé, et chaque carte s'appuie sur un ou deux items de fiche (`base`) dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : un premier relecteur a contrôlé les 35 cartes. Il a vérifié que chaque carte dit ce que dit la fiche, sans plus, et qu'elle respecte la forme exigée par le contrat. Il n'a fait aucune recherche : son seul juge était le texte (`t` et `cite`) des items de la fiche.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a vérifié les points suivants :
   - **Exactitude** : chaque carte est-elle juste au regard du droit en vigueur au 15 octobre 2026 (CGI, BOFiP, PCG modifié par le règlement ANC 2022-06) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne dit pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle qu'attendrait un correcteur du DCG, et la seule réponse juste possible ?
   - **Doublons et cartes triviales.**
   - **Absence de calcul et de chiffre millésimé.**
4. **Recherches** : 3 recherches, le maximum permis, limitées à bofip.impots.gouv.fr et legifrance.gouv.fr (détail plus bas).

Validation : `node validate.js data/ue4/ue4-03.cartes.json` renvoie ✓ (35 cartes, dont 6 de définition).

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k35, sans trou) |
| Définition (`def`) | 6 |
| Compréhension (`comp`) | 29 |
| Cartes corrigées par la relecture d'exactitude | 4 (k02, k05, k16, k31) |
| Cartes supprimées | 0 |
| Cartes ajoutées | 0 |

**Items de la fiche sans carte** :

- **Items millésimés**, qui ne peuvent pas donner de carte :
  - Définitions#3 (régime simplifié d'imposition, avec les seuils 2025 et 2026-2028) ;
  - Chiffres et seuils#0 (seuils des régimes BIC) et #2 (plus-values professionnelles, avec le taux 2025 des prélèvements sociaux) ;
  - Ce qui a changé récemment#0 (seuils 2026-2028), #1 (loi du 19 novembre 2024 sur les meublés de tourisme), #3 (fonds commerciaux), #4 (LFSS 2026 et plus-values à long terme) et #5 (assiette sociale des indépendants).
- **Chiffres et seuils#1** (plafonds d'amortissement des véhicules de tourisme) : l'item est stable, mais il ne contient que des montants par tranche d'émissions. Une carte serait du par-cœur sur des chiffres. La règle elle-même est couverte par k13 et k14.

Chaque item stable des Définitions, des Règles essentielles (17 sur 17) et des Points de vigilance (6 sur 6) a au moins une carte, de même que le seul item stable de « Ce qui a changé récemment » (#2).

Le jeu atteint le plafond de 35 cartes fixé par le contrat. Aucun ajout n'était possible sans suppression, et aucune carte n'était assez faible pour céder sa place.

## Corrections de la première relecture (fidélité)

Le premier relecteur a contrôlé 35 cartes et en a corrigé une.

| Cible | Problème | Correction |
|---|---|---|
| k10 | La réponse rappelait un montant périmé : « l'ancienne limite de 17 500 € ». C'est un chiffre daté (version de l'art. 154 en vigueur de 2016 à 2018), ce qui va contre la règle « aucun chiffre millésimé ». La carte faisait donc mémoriser un montant abrogé. | La phrase devient « L'ancienne limite de montant, qui visait les exploitants non adhérents d'un organisme de gestion agréé, ne figure plus dans le texte en vigueur. » Le sens reste fidèle à Règles essentielles#2, sans le chiffre. Le champ `maj` du fichier passe à 2026-10-16. |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k31 | La carte affirmait, pour tout « loueur en meublé relevant du micro-BIC », que la plus-value de cession de l'immeuble relève du court terme à hauteur des amortissements réputés compris dans l'abattement. Cette règle ne vaut que pour le **loueur professionnel**. Les plus-values du loueur non professionnel (LMNP), cas le plus courant, sont soumises au régime des plus-values des particuliers (CGI, art. 150 U et 150 VH) et non au régime professionnel. La carte faisait donc apprendre une règle fausse pour la plupart des loueurs en meublé. | Le champ de la question est délimité : « Pour un loueur en meublé professionnel relevant du micro-BIC, comment les amortissements sont-ils pris en compte, y compris lors de la cession de l'immeuble ? ». La réponse précise « la plus-value professionnelle ». Le reste est inchangé, et la base reste Ce qui a changé récemment#2. | BOI-BIC-CHAMP-40-20 (version du 14 février 2024), qui réserve la règle au loueur professionnel et renvoie le LMNP aux art. 150 U et 150 VH (recherche n° 2) |
| k05 | La réponse « 71 % pour les ventes et 50 % pour les prestations de services » omettait la **fourniture de logement**, qui relève de la catégorie à 71 % de l'article 50-0, 1. Un hôtelier au micro-BIC, prestataire de services, en aurait déduit à tort un abattement de 50 %. À l'inverse, la location meublée est exclue de cette catégorie : depuis la loi du 19 novembre 2024, les meublés de tourisme classés et les chambres d'hôtes relèvent de l'abattement de 50 % (fiche, Ce qui a changé récemment#1). Ajouter seulement « fourniture de logement » aurait fait revivre l'ancien régime, où les meublés classés bénéficiaient de 71 %. | « 71 % pour les ventes et la fourniture de logement hors location meublée, 50 % pour les prestations de services et la location meublée, sauf 30 % pour les meublés de tourisme non classés. Chaque abattement ne peut être inférieur à 305 €. » La base reste Définitions#2. Les autres précisions figurent déjà dans la fiche (Définitions#3, Chiffres et seuils#0, Ce qui a changé récemment#1), mais dans des items millésimés, qui ne peuvent pas servir de base. | CGI, art. 50-0, 1 (recherche n° 3 : la catégorie à 71 % vise les entreprises dont le commerce principal est de vendre des marchandises ou de fournir le logement, à l'exclusion de la location de locaux d'habitation meublés) ; fiche, Ce qui a changé récemment#1 |
| k02 | La seconde phrase, « Pour les prestations de services, le produit n'est imposable que si la créance est acquise et la prestation achevée », était présentée comme absolue. Or les prestations continues (loyers, intérêts) et les prestations discontinues à échéances successives sont rattachées au fur et à mesure de leur exécution, sans attendre leur achèvement (CGI, art. 38, 2 bis, b). | « Pour les prestations de services, le produit n'est **en principe** imposable que si la créance est acquise et la prestation achevée ; les prestations continues sont rattachées au fur et à mesure de leur exécution. » La base Règles essentielles#0 est ajoutée. `src` et `url` sont inchangés : ce sont ceux du premier item de base, Définitions#1. | CGI, art. 38, 2 bis ; BOI-BIC-BASE-20-10 ; fiche, Règles essentielles#0 |
| k16 | La réponse s'ouvrait sur « Les biens d'équipement normalement utilisés dans les entreprises industrielles ». On pouvait comprendre que le dégressif est réservé aux entreprises industrielles. Or le critère décisif est l'appartenance aux catégories de l'annexe II (art. 22), qui couvrent aussi des biens utilisés hors de l'industrie. Le critère réel n'apparaissait qu'en fin de réponse, parmi les exclusions. | « Les biens d'équipement acquis neufs, dont la durée normale d'utilisation est d'au moins trois ans et qui figurent dans les catégories de l'annexe II (matériels et outillages industriels notamment). Sont donc exclus les biens d'occasion, ceux dont la durée normale d'utilisation est inférieure à trois ans et ceux hors de ces catégories, comme les véhicules de tourisme ou le mobilier de bureau. » Les bases restent Règles essentielles#6 et Points de vigilance#2. | CGI, art. 39 A, 1 ; CGI, ann. II, art. 22 ; fiche, Points de vigilance#2 |

**Cartes contrôlées et maintenues** :

- **Provision pour licenciement (k22)** : la recherche n° 1 confirme que les provisions pour indemnités de licenciement pour motif économique ne sont pas déductibles (art. 39, 1-5°), que le licenciement soit individuel ou collectif. Celles qui couvrent un licenciement pour un autre motif le sont, dans les conditions de droit commun. La carte est exacte.
- **Doublons apparents** : k04/k05, k06/k07, k13/k14, k16/k17/k35, k18/k19, k23/k24 et k25/k26 portent sur les mêmes items, mais chacune interroge un angle distinct :
  - champ du micro-BIC et abattements ;
  - méthode du 2058-A et exigence de comptabilisation ;
  - véhicule acquis et véhicule loué ;
  - biens éligibles au dégressif, comptabilisation du dérogatoire et coefficients ;
  - règle de l'amortissement minimal et sanction ;
  - reprise d'une provision déduite et d'une provision réintégrée ;
  - plus-values et moins-values à court terme.
- **Chiffres stables** : plusieurs cartes citent des chiffres fixés par la loi ou par la doctrine, sans indexation annuelle. Dans chaque cas, la question porte sur la règle, ce que le contrat (section 8) admet :
  - k05 : abattements de 71, 50 et 30 % et minimum de 305 € ;
  - k15 : seuil de 500 € ;
  - k28 : taux de 12,8 % ;
  - k29 : seuils de l'article 151 septies ;
  - k30 : seuils de l'article 238 quindecies ;
  - k34 : fraction de 6,8 points ;
  - k35 : coefficients du dégressif.

  Aucune carte ne cite le taux des prélèvements sociaux, qui est millésimé.
- **Rémunération de l'exploitant (k09)** : la carte reste exacte. L'entrepreneur individuel qui a opté pour l'assimilation à une EURL relève de l'IS et sort du champ de la question, qui vise le bénéfice BIC.
- **Déficits (k33)** : la carte est exacte, mais elle ne précise pas la durée de report des déficits BIC non professionnels autres que ceux de la location meublée. Ce point est signalé par la première relecture.

## Recherches faites

1. **Provisions pour indemnités de licenciement économique** (domaine bofip.impots.gouv.fr, BOI-BIC-PROV-30-20-10-20).
   - Confirmé : les provisions pour indemnités de licenciement pour motif économique ne sont pas déductibles (art. 39, 1-5°), que le licenciement soit individuel ou collectif.
   - L'exclusion vise toutes les indemnités directement liées au licenciement économique, légales comme conventionnelles. Les provisions pour préavis et pour mesures d'accompagnement social restent déductibles selon le droit commun.
   - Les résultats ne donnaient que des versions de 2012 de la page : le point est confirmé, sous réserve de la version en ligne.
   - Conséquence : k22 est maintenue.
2. **Location meublée au micro-BIC : amortissements et plus-value** (domaine bofip.impots.gouv.fr, BOI-BIC-CHAMP-40-20 du 14 février 2024).
   - Confirmé : l'abattement forfaitaire est réputé tenir compte des amortissements linéaires, et la plus-value est à court terme à hauteur de ces amortissements. Le BOFiP présente cette règle pour le loueur professionnel.
   - Les plus-values des loueurs qui ne remplissent pas les conditions du loueur professionnel relèvent des articles 150 U et 150 VH (plus-values des particuliers). Elles ne relèvent pas du régime professionnel et n'ouvrent pas droit à l'exonération de l'article 151 septies.
   - Conséquence : k31 est corrigée.
3. **CGI, art. 50-0 : catégories et abattements du micro-BIC** (domaine legifrance.gouv.fr).
   - Confirmé : le texte en vigueur prévoit trois abattements (71 %, 50 % et 30 %) et un minimum de 305 €.
   - Les versions de 2016 et 2020 définissent la catégorie à 71 % : entreprises dont le commerce principal est de vendre des marchandises, objets, fournitures et denrées, ou de fournir le logement, « à l'exclusion de la location directe ou indirecte de locaux d'habitation meublés ».
   - L'extrait de la version en vigueur ne montrait pas cette phrase. Le classement des meublés de tourisme classés et des chambres d'hôtes à 50 % repose donc sur la fiche (Ce qui a changé récemment#1, sources BOFiP ACTU-2025-00127 et impots.gouv.fr).
   - Conséquence : k05 est corrigée.

## Points à reprendre dans la fiche

Points relevés par la relecture d'exactitude :

- **Ce qui a changé récemment#2 (location meublée et amortissements)** : l'item doit préciser que la règle (plus-value à court terme à hauteur des amortissements réputés compris dans l'abattement) ne vaut que pour le **loueur en meublé professionnel**. Les plus-values du loueur non professionnel relèvent des articles 150 U et 150 VH (BOI-BIC-CHAMP-40-20).
  - La section pourrait aussi signaler la réforme de la loi de finances pour 2025 (loi n° 2025-127 du 14 février 2025). Pour le loueur non professionnel au régime réel, les amortissements déduits sont désormais pris en compte dans le calcul de la plus-value privée, hors résidences de services visées par le texte. Ce point vient de connaissances générales et n'a pas été recherché : article et exceptions à vérifier.
- **Définitions#2 (micro-BIC)** : l'abattement de 71 % vise les ventes **et la fourniture de logement** (hors location meublée). Celui de 50 % vise les **autres activités**, y compris la location meublée (meublés de tourisme classés, chambres d'hôtes), et pas seulement les prestations de services. Ces précisions ne figurent aujourd'hui que dans des items millésimés (Définitions#3, Chiffres et seuils#0, Ce qui a changé récemment#1). Il faudrait les reprendre dans cet item stable.
- **Règles essentielles#6 (dégressif)** : la formule « réservé aux biens d'équipement normalement utilisés dans les entreprises industrielles » peut laisser croire à une restriction par secteur. Le critère est l'appartenance aux catégories limitatives de l'article 22 de l'annexe II. De mémoire, ces catégories comprennent aussi des biens utilisés hors de l'industrie, comme les machines de bureau ou les immeubles et matériels des entreprises hôtelières : liste à vérifier sur Légifrance.
- **Définitions#1 (créance acquise)** : « pour les prestations de services, le produit n'est imposable que si la créance est acquise et la prestation achevée » devrait être nuancé par « en principe ». Les prestations continues et les prestations discontinues à échéances successives sont rattachées au fur et à mesure de leur exécution (Règles essentielles#0).

Points déjà relevés par la première relecture, toujours valables :

- **Définitions#3 (régime simplifié d'imposition)** : l'item mêle une définition stable et des seuils millésimés. Il faudrait le scinder en deux :
  - un item stable : le RSI s'applique au-delà des seuils du micro-BIC et jusqu'aux limites de l'article 302 septies A bis, révisées tous les trois ans ; au-delà, régime réel normal ;
  - les montants, qui figurent déjà dans Chiffres et seuils#0.
- **Règles essentielles#14 (déficit BIC)** : l'item ne précise pas la durée de report des déficits BIC non professionnels autres que ceux de la location meublée non professionnelle. Il s'agit, semble-t-il, de l'année et des six années suivantes (art. 156, I-1° bis) : à vérifier sur Légifrance.
- **Points de vigilance#5 (renvoi de l'article 209, I)** : il n'est couvert qu'en partie, par k09, faute de place dans un jeu déjà à 35 cartes.

## Classement des exercices

Classement automatique des exercices QCM, QCM multiples et classements (tri) du chapitre selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 15 |
| `calcul` (montant, taux, prorata, délai) | 3 |
| `chiffre` (rappel d'un chiffre millésimé) | 3 |
| **Total** | 21 |

Aucun désaccord n'a été relevé. Seuls les 15 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
