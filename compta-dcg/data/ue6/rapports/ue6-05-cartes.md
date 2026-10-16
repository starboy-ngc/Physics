# Cartes de notions : ue6-05 (Financement : modes, coût du capital et plan de financement)

*15 octobre 2026*

Fichier : `data/ue6/ue6-05.cartes.json`. Fiche de référence : `data/ue6/ue6-05.fiche.json` (non modifiée, mise à jour du 14 octobre 2026). Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les 35 cartes (k01 à k35) ont été rédigées à partir de la seule fiche du chapitre. Elles respectent la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.

   Le jeu avait déjà fait l'objet d'un premier cycle de relectures, enregistré dans le dépôt. Le présent rapport porte sur la reprise de ce jeu.
2. **Relecture de fidélité.** Un premier relecteur a contrôlé les 35 cartes au regard de la seule fiche, sans recherche web. Il a corrigé 7 cartes, sans suppression ni ajout (tableau plus bas). Il a notamment retiré quatre précisions apportées au cycle précédent parce qu'elles ne figuraient pas dans la fiche (k02, k10, k19, k22).
3. **Relecture d'exactitude.** C'est la présente relecture, faite par un second relecteur indépendant. Il a contrôlé les 35 cartes sur quatre points :
   - **Exactitude** au 15 octobre 2026 : Code de commerce, Code monétaire et financier, CGI, PCG modifié par le règlement ANC n° 2022-06.
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse juste serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand l'item de fiche était lui-même en cause, la fiche n'a pas été touchée. Pour que la carte reste exacte sans s'écarter de la fiche, la correction a d'abord resserré la question ou retiré la proposition inexacte. Une précision extérieure à la fiche n'a été ajoutée que pour k22 (« à usage professionnel »), faute d'autre moyen de rendre la définition légale exacte. Dans tous les cas, la carte reste portée par ses items de base et l'item est signalé plus bas. Bilan : 8 cartes corrigées, aucune suppression, aucun ajout.
4. **Recherches.** Une seule recherche web a été faite, limitée à anc.gouv.fr (détail plus bas). Les comptes ont été vérifiés avec le plan comptable du dépôt (`data/pcg/`) : 131, 138, 161, 1618, 163, 1638, 164, 1648, 1688, 169, 455, 481, 612, 747, 777.

Validation : `node validate.js data/ue6/ue6-05.cartes.json` renvoie « ✓ data/ue6/ue6-05.cartes.json (cartes, 35 (13 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées | 35 |
| Cartes au final | 35 |
| Définition (`def`) | 13 |
| Compréhension (`comp`) | 22 |
| Corrigées par la relecture de fidélité | 7 (k02, k03, k10, k13, k19, k22, k29) |
| Corrigées par la relecture d'exactitude | 8 (k02, k14, k15, k17, k19, k22, k25, k26) |
| Supprimées | 0 |
| Ajoutées | 0 |
| Identifiants libres | aucun |

Chacun des dix items de la section « Définitions » a au moins une carte. Les seize « Règles essentielles » et les cinq « Points de vigilance » sont tous couverts. Pour « Ce qui a changé récemment », les items #0 (comptes du PCG 2025) et #4 (financement participatif) sont couverts.

**Items de la fiche sans carte :**

- **Chiffres et seuils#0** (taux normal de l'IS) et **#1** (taux réduit des PME, millésimé 2025) : ce sont des taux fixés par la loi de finances, exclus des révisions. La règle du coût de la dette après impôt est portée par k25, qui l'écrit avec un taux d'IS littéral (t).
- **Chiffres et seuils#3** (plafond de l'article 212 bis) : il reprend Règles essentielles#7, déjà porté par k26.
- **Ce qui a changé récemment#1** (calendrier du programme) : aucune notion à retenir.
- **Ce qui a changé récemment#2** (contribution exceptionnelle, millésimé 2025) et **#3** (loi de finances pour 2026, millésimé 2026) : ce sont des items millésimés, qui ne donnent pas de carte.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| k02 | La réponse limitait la réserve légale « aux SARL et sociétés par actions ». Ce champ d'application ne figure ni dans Règles essentielles#12 ni dans Chiffres et seuils#2 : c'est une connaissance extérieure à la fiche. | La seconde phrase devient « La réserve légale est dotée d'au moins 5 % du bénéfice de l'exercice, diminué des pertes antérieures, jusqu'à ce qu'elle atteigne 10 % du capital social. » |
| k03 | La formule « réserves que la loi ou les statuts ne permettent pas de distribuer » reprenait le texte légal au lieu du vocabulaire de la fiche (Points de vigilance#2 : « réserves indisponibles »). | Remplacée par « sous le montant du capital augmenté des réserves indisponibles ». |
| k10 | La réponse ajoutait que le statut national d'intermédiaire en financement participatif (C. mon. fin., art. L. 548-1) subsiste à côté. Ni Ce qui a changé récemment#4 ni Définitions#9 ne le disent : c'est une connaissance extérieure. | Proposition supprimée. La réponse s'arrête à « … un mode de financement reconnu des PME. » |
| k13 | La réponse commençait par « Du quart au moins de leur nominal… » sans sujet. Elle était mal construite pour répondre à « quelles règles de libération s'appliquent ». | La réponse commence par « Les actions nouvelles sont libérées du quart au moins de leur nominal à la souscription, le surplus dans les cinq ans. » Le contenu de Chiffres et seuils#4 est inchangé. |
| k19 | L'exception « sauf si les statuts réservent ce pouvoir à l'assemblée générale ou si celle-ci décide de l'exercer » vient du texte de l'article L. 228-40, pas de la fiche. Règles essentielles#2 dit seulement « sauf disposition contraire des statuts ». | Réécrite en « L'émission elle-même relève du conseil d'administration ou du directoire, sauf disposition contraire des statuts. » |
| k22 | La définition du crédit-bail ajoutait « à usage professionnel » et « au moins pour partie » (des loyers versés). Ces deux précisions ne figurent pas dans Définitions#4. | Les deux précisions sont retirées : « Une location d'un bien d'équipement ou immobilier, assortie d'une promesse unilatérale de vente permettant au locataire d'acquérir le bien pour un prix convenu tenant compte des loyers versés. Le bien reste la propriété du bailleur. » |
| k29 | « Par leur part dans le financement (CP + D) » était ambigu par rapport à la formule de Règles essentielles#14, qui pondère par CP/(CP + D) et D/(CP + D). | Remplacé par « par leur poids dans le financement total (CP + D) ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k02 | Une fois la précision retirée par la relecture de fidélité, la carte présentait la dotation à la réserve légale comme une règle applicable à toute société. Elle n'est imposée que dans les SARL et les sociétés par actions. Elle ne s'applique ni aux SNC ni aux sociétés civiles. | Le champ est délimité dans la question, pas dans la réponse : « Selon le Code de commerce, de quoi est constitué le bénéfice distribuable d'une SARL ou d'une société par actions ? » La réponse reste celle de la fiche. | C. com., art. L. 232-10 et L. 232-11 |
| k14 | La réponse « Un droit de souscription aux augmentations de capital… » omettait la priorité, qui est l'essence du DPS et la réponse qu'attend un correcteur (souscrire en priorité). | « Un droit de souscrire par préférence aux augmentations de capital en numéraire, proportionnellement au montant des actions détenues. » La seconde phrase (négociabilité) est inchangée. | C. com., art. L. 225-132 |
| k15 | « Chaque actionnaire exerce ou cède son droit » présente une alternative fermée. L'actionnaire peut aussi renoncer individuellement à son droit ou le laisser perdre. | « À défaut de suppression, chaque actionnaire peut exercer ou céder son droit. » (Même formulation que k16.) | C. com., art. L. 225-132 |
| k17 | « 1638 pour les emprunts obligataires (163) » est inexact pour les obligations convertibles. Le compte 163 ne vise que les autres emprunts obligataires ; les emprunts obligataires convertibles sont au compte 161, leurs intérêts courus au compte 1618. | La seconde phrase devient « Le PCG 2025 enregistre les intérêts courus par nature d'emprunt : 1618, 1638 ou 1648. » Cette liste est celle de Ce qui a changé récemment#0. | Plan de comptes PCG 2025, comptes 161, 1618, 163, 1638, 164, 1648 |
| k19 | « Sauf disposition contraire des statuts » est incomplet : l'article L. 228-40 réserve aussi le cas où l'assemblée générale décide d'exercer elle-même ce pouvoir. Par ailleurs, la question vise toute société par actions, où l'organe compétent n'est pas toujours un conseil d'administration ou un directoire (gérants d'une SCA). La relecture de fidélité ayant retiré la formule légale, la carte est corrigée par restriction et non par ajout. | « Dans une société anonyme, l'émission elle-même relève en principe du conseil d'administration ou du directoire. » | C. com., art. L. 228-40 |
| k22 | La question porte sur la définition « selon le Code monétaire et financier », mais la réponse retenait le crédit-bail sur tout bien immobilier. L'article L. 313-7, 2° ne vise que les biens immobiliers **à usage professionnel** : sans cette condition, une location-accession à un logement entrerait dans la définition. « Tenant compte des loyers versés » n'est pas inexact et est conservé. | « Une location d'un bien d'équipement ou d'un bien immobilier à usage professionnel, assortie d'une promesse unilatérale de vente… » La suite est inchangée. | C. mon. fin., art. L. 313-7, 1° et 2° |
| k25 | La question vise une entreprise bénéficiaire. La dernière proposition (« en déficit, coûts avant et après impôt se confondent ») sortait de ce champ, et n'est vraie que si le déficit n'est jamais imputé. La charge d'intérêts accroît en effet le déficit reportable : l'économie d'impôt est différée, pas perdue, si l'entreprise redevient bénéficiaire. | Proposition supprimée. La réponse s'arrête à « Cette économie suppose un résultat imposable suffisant et le respect de l'article 212 bis. » | CGI, art. 39, 1-1°, 209, I et 219, I |
| k26 | Le plafond du plus élevé de 3 M€ et de 30 % de l'EBITDA fiscal est le principe, pas la seule limite. L'article 212 bis prévoit aussi une déduction complémentaire pour les entreprises non membres d'un groupe consolidé, une clause de sauvegarde pour les membres d'un groupe et le report des charges non déduites. | La réponse commence par « En principe, dans la limite du plus élevé de 3 millions d'euros ou de 30 % de l'EBITDA fiscal… » | CGI, art. 212 bis |

Les 27 autres cartes ont été contrôlées sans changement : k01, k03 à k13, k16, k18, k20, k21, k23, k24 et k27 à k35. En particulier :

- **k01 et k33** : la notion de tableau de financement du PCG reste d'actualité. La recherche faite sur anc.gouv.fr le confirme (voir plus bas).
- **k03** : la question délimitée au cycle précédent (« ni bénéfice distribuable ni réserves disponibles ») est exacte au regard des articles L. 232-11 et L. 232-12. « Réserves indisponibles » est l'équivalent exact de la formule légale.
- **k10** : la question (« quel statut européen **peuvent obtenir** les plateformes ») délimite le champ. Sans la mention du statut national, la réponse reste exacte.
- **k12** : « seule compétente » est la formule de l'article L. 225-129. La faculté de délégation n'est pas mentionnée, mais la carte n'est pas fausse (voir le point de fiche n° 10).

Doublons examinés et conservés, parce que les questions diffèrent :

- k04/k05 : définition, puis reprise d'une subvention finançant un bien non amortissable ;
- k15/k16 : suppression du DPS, puis valeur théorique du DPS ;
- k23/k24 : traitement comptable du crédit-bail, puis capacité d'endettement ;
- k25/k26 : raison de l'économie d'impôt, puis plafond de l'article 212 bis ;
- k28/k29 : définition du CMPC, puis son usage ;
- k30, k31 et k32 : définition du plan de financement, ses ressources, ses emplois.

Aucune carte ne demande de calcul. Les seuls chiffres conservés sont des chiffres stables qui font partie d'une règle : 5 % et 10 % (k02), quart et cinq ans (k13), dix ans (k05), 3 M€ et 30 % (k26), neuf mois (k34). Le taux d'IS n'apparaît nulle part : k25 l'écrit sous la forme littérale t.

## Recherches faites

1. **WebSearch** (anc.gouv.fr) : « règlement ANC 2022-06 tableau de financement système développé supprimé PCG ».
   - **Doute de départ.** Il fallait savoir si le PCG modifié par le règlement ANC n° 2022-06 comporte encore un tableau de financement. Les cartes k01 (« au sens du tableau de financement du PCG ») et k33 en dépendent.
   - **Ce qui est confirmé.** Le PCG consolidé au 1er janvier 2026 comporte toujours un chapitre « Tableau de financement » ([recueil PCG 1er janvier 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/PCG--1er-janvier-2026.pdf)). Le règlement n° 2022-06 vise ce tableau pour les entités relevant des articles L. 232-2 et L. 612-2 du Code de commerce ([règlement ANC n° 2022-06](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2022/R2022_06/R2022_06.pdf) ; [page du règlement](https://www.anc.gouv.fr/reglement-ndeg-2022-06-du-4-novembre-2022)).
   - **Ce qui n'a pas été tranché.** Les extraits ne disent pas si le « système développé » a été supprimé. Ce point est sans incidence sur les cartes.
   - **Conséquence.** k01 et k33 sont conservées.

Aucune autre recherche (1 sur 3 autorisées). Les autres points ont été tranchés à partir des textes cités par la fiche, sans recherche : C. com., art. L. 225-129, L. 225-132, L. 228-40, L. 232-10 à L. 232-13 ; C. mon. fin., art. L. 313-7 ; CGI, art. 39, 209, 212 bis et 219. Le plan comptable du dépôt a servi pour les comptes.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Chiffres et seuils#2 et Règles essentielles#12** : la dotation à la réserve légale n'est obligatoire que dans les SARL et les sociétés par actions (C. com., art. L. 232-10). La fiche ne le dit pas, ce qui oblige la carte k02 à délimiter son champ dans la question.
2. **Points de vigilance#2** :
   - « Un dividende distribué sans bénéfice distribuable […] est un dividende fictif » est trop large. Une distribution prélevée sur des réserves disponibles est licite (C. com., art. L. 232-11, al. 3). Le critère légal est l'absence de sommes distribuables (art. L. 232-12).
   - La fin de l'item (« l'autofinancement ne peut pas être négatif par distribution excessive ») est douteuse. Les dividendes mis en paiement peuvent dépasser la CAF de l'exercice sans être fictifs.
3. **Règles essentielles#2** : l'émission d'obligations relève du conseil d'administration, du directoire ou du ou des gérants, « sauf si les statuts réservent ce pouvoir à l'assemblée générale ou si celle-ci décide de l'exercer » (C. com., art. L. 228-40). « Sauf disposition contraire des statuts » est incomplet.
4. **Définitions#4** : le crédit-bail immobilier ne porte que sur des biens immobiliers « à usage professionnel ». Le prix convenu tient compte des loyers « au moins pour partie » (C. mon. fin., art. L. 313-7).
5. **Règles essentielles#4** : « emprunts obligataires en 163 (intérêts courus 1638) » est imprécis. Le compte 163 vise les autres emprunts obligataires ; les emprunts obligataires convertibles sont au compte 161 (intérêts courus 1618), comme l'indique d'ailleurs Ce qui a changé récemment#0.
6. **Points de vigilance#0** (et Règles essentielles#6) : « en déficit, le coût de la dette avant et après impôt se confondent » est une simplification. Les intérêts accroissent le déficit reportable (CGI, art. 209, I) : l'économie d'impôt est différée et non perdue si l'entreprise redevient bénéficiaire.
7. **Règles essentielles#6, Chiffres et seuils#0 et Points de vigilance#0** : le taux normal de l'IS (25 %) est un taux fixé par la loi de finances. Il est marqué `stable` alors qu'il devrait être traité comme millésimé. Pour les grandes entreprises redevables de la contribution exceptionnelle, le taux effectif est d'ailleurs supérieur. Mieux vaut écrire la règle avec un taux littéral : i × (1 − t).
8. **Règles essentielles#7 et Chiffres et seuils#3** : le plafond de l'article 212 bis (plus élevé de 3 M€ et de 30 % de l'EBITDA fiscal) est le principe. L'article prévoit aussi une déduction complémentaire pour les entreprises non membres d'un groupe consolidé, une clause de sauvegarde pour les membres d'un groupe et le report des charges non déduites. Ajouter « en principe ».
9. **Règles essentielles#10 (src)** : la référence « C. mon. fin., art. R. 314-2 » paraît erronée. Le taux effectif global et la méthode des intérêts composés relèvent du Code de la consommation (art. R. 314-1 et suivants), et le principe est repris à l'article R. 313-1 du Code monétaire et financier. Ce point a été relevé au cycle précédent, après une recherche sur Légifrance ; il n'a pas été revérifié ici. La carte k21 recopie la référence, comme le contrat l'exige.
10. **Règles essentielles#0** (point mineur) : l'assemblée générale extraordinaire est « seule compétente », mais elle peut déléguer sa compétence ou ses pouvoirs au conseil d'administration ou au directoire (C. com., art. L. 225-129-1 et L. 225-129-2).
11. **Règles essentielles#1** (point mineur) : « chaque actionnaire exerce ou cède son droit » est trop fermé. L'actionnaire peut aussi renoncer individuellement à son DPS ou ne pas l'exercer. Écrire « peut exercer ou céder ».
12. **Ce qui a changé récemment#4** : « les plateformes sont des prestataires européens de services de financement participatif agréés » est trop général. Ce statut ne vise que les services relevant du règlement (UE) 2020/1503. Le statut d'intermédiaire en financement participatif (C. mon. fin., art. L. 548-1, cité par Définitions#9) demeure, notamment pour les dons et les prêts sans intérêt.
13. **Définitions#6** (point mineur) : le PCG range aussi parmi les subventions d'investissement celles qui financent des activités à long terme (« autres subventions d'investissement », compte 138). La définition de la fiche ne vise que l'acquisition ou la création d'immobilisations.

## Classement des exercices

Le classement automatique porte sur les 18 exercices QCM, QCM multiples et de classement du chapitre :

| nature | nombre |
|---|---|
| notion | 15 |
| calcul | 3 |
| chiffre | 0 |

Les trois exercices de nature calcul sont :

- **#5** : dilution d'un actionnaire lors d'une augmentation de capital ;
- **#10** : prime d'émission d'une obligation ;
- **#22** : capacité d'endettement à partir d'un ratio bancaire.

Aucun désaccord n'a été relevé entre les classements. Les 15 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes.
