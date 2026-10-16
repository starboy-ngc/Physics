# Cartes de notions : ue6-05 (Financement : modes, coût du capital et plan de financement)

*15 octobre 2026*

Fichier : `data/ue6/ue6-05.cartes.json`. Fiche de référence : `data/ue6/ue6-05.fiche.json` (non modifiée, mise à jour du 14 octobre 2026). Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir de la seule fiche du chapitre. Elles respectent la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité.** Un premier relecteur a contrôlé les 35 cartes par rapport à la fiche, sans recherche web. Il en a corrigé 8, sans suppression ni ajout (tableau plus bas).
3. **Relecture d'exactitude.** C'est la présente relecture, faite par un second relecteur indépendant. Il a contrôlé les 35 cartes sur quatre points :
   - **Exactitude** au 15 octobre 2026 : Code de commerce, Code monétaire et financier, CGI, PCG modifié par le règlement ANC n° 2022-06.
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse juste serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand l'item de fiche était lui-même en cause, la fiche n'a pas été touchée. La carte a été corrigée pour rester exacte tout en restant portée par ses items de base, et l'item est signalé plus bas. Bilan : 9 cartes corrigées, aucune suppression, aucun ajout.
4. **Recherches.** Une seule recherche web a été faite, limitée à legifrance.gouv.fr (détail plus bas). Les comptes ont été vérifiés avec le plan comptable du dépôt (`data/pcg/`) : 131, 138, 139, 169, 481, 612, 747, 1638, 1648, 1688.

Validation : `node validate.js data/ue6/ue6-05.cartes.json` renvoie « ✓ data/ue6/ue6-05.cartes.json (cartes, 35 (13 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées | 35 |
| Cartes au final | 35 |
| Définition (`def`) | 13 |
| Compréhension (`comp`) | 22 |
| Corrigées par la relecture de fidélité | 8 (k03, k08, k11, k13, k24, k29, k31, k32) |
| Corrigées par la relecture d'exactitude | 9 (k02, k03, k07, k10, k19, k22, k23, k25, k35) |
| Supprimées | 0 |
| Ajoutées | 0 |
| Identifiants libres | aucun |

Chacun des dix items de la section « Définitions » a au moins une carte. Les seize « Règles essentielles » sont toutes couvertes, de même que les cinq « Points de vigilance ».

**Items de la fiche sans carte :**

- **Chiffres et seuils#0** (taux normal de l'IS) et **#1** (taux réduit des PME, millésimé 2025) : ce sont des taux fixés par la loi de finances, exclus des révisions. La règle du coût de la dette après impôt est portée par k25, qui est écrite avec un taux d'IS littéral (t).
- **Chiffres et seuils#3** (plafond de l'article 212 bis) : le contenu est le même que celui de Règles essentielles#7, déjà porté par k26.
- **Ce qui a changé récemment#1** (calendrier du programme) : aucune notion à retenir.
- **Ce qui a changé récemment#2** (contribution exceptionnelle, millésimé 2025) et **#3** (loi de finances pour 2026, millésimé 2026) : ce sont des items millésimés, qui ne donnent pas de carte.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis de la première relecture s'interrompt au milieu de l'entrée k31. Les entrées k31 (fin), k24 et k32 ont donc été reconstituées d'après l'écart entre la version rédigée et la version relue du fichier.

| cible | problème | correction |
|---|---|---|
| k03 | La seconde phrase reprenait « l'autofinancement ne peut donc pas devenir négatif par distribution excessive ». La fiche (Points de vigilance#2) dit « être négatif », pas « devenir ». L'affirmation est douteuse : les dividendes mis en paiement peuvent dépasser la CAF de l'année sans être fictifs. | Phrase supprimée. Réponse : « De dividende fictif. C'est aussi le cas d'une distribution qui ramène les capitaux propres sous le capital et les réserves indisponibles. » Le point est signalé pour la fiche. |
| k08 | La question « Qu'est-ce qu'un prêt participatif dans le financement des entreprises ? » était trop ouverte : on pouvait y répondre juste autrement (prêt à long terme, rémunération liée aux résultats…), alors que la fiche ne retient que l'assimilation à des fonds propres. Le type `def` ne convenait pas non plus : il s'agit de l'effet d'une règle légale. | Type passé à `comp`. Question : « Selon le Code monétaire et financier, à quoi les prêts participatifs sont-ils assimilés pour l'appréciation de la situation financière des entreprises qui en bénéficient ? » Réponse : « À des fonds propres. Le prêt participatif est ainsi classé parmi les quasi-fonds propres. » |
| k11 | La question « comment s'opère l'augmentation de capital d'une SA ? » admettait d'autres réponses justes (en numéraire, par incorporation de réserves, par apport en nature, par conversion de créances), alors que la carte n'attendait que les deux procédés de l'article L. 225-127. | Question : « Selon le Code de commerce, par quels deux procédés portant sur les actions s'opère l'augmentation de capital d'une société anonyme ? » Réponse inchangée. |
| k13 | La question « comment les actions nouvelles sont-elles libérées ? » était imprécise : « en numéraire » ou « par versement » auraient été des réponses justes. Elle ne visait pas non plus la prime d'émission, pourtant traitée dans la réponse. | Question : « Lors d'une augmentation de capital en numéraire d'une société anonyme, quelles règles de libération s'appliquent aux actions nouvelles et à la prime d'émission ? » Réponse inchangée. |
| k24 | La réponse reprenait Règles essentielles#15 (capacité de remboursement, autonomie financière), ce qui faisait doublon avec k35. | Réponse : « Parce que la Banque de France et les banques le comptent comme une dette, alors qu'il n'alourdit pas le bilan comptable : les redevances sont des charges externes (compte 612) et le bien n'est pas à l'actif. » Base : Points de vigilance#1 et Règles essentielles#5. |
| k29 | La phrase « Il pondère le coût des capitaux propres et le coût de la dette après impôt, en principe en valeurs de marché » omettait l'objet de la pondération. Sa lecture était approximative au regard de la formule de Règles essentielles#14. | « Il pondère le coût des capitaux propres et le coût de la dette après impôt par leur part dans le financement (CP + D), en principe en valeurs de marché. » |
| k31 | La fiche donne la liste des ressources entre parenthèses, sans dire qu'elle est complète. Or la question appelait une liste fermée. | Question : « Outre la capacité d'autofinancement, quelles sont les principales ressources retenues dans le plan de financement d'une entreprise ? » Réponse inchangée. |
| k32 | Même défaut pour la liste des emplois. | Question : « Quels sont les principaux emplois que le plan de financement d'une entreprise confronte, année par année, aux ressources ? » Dans la réponse, « Le plan suit ainsi » devient « Le plan suit en outre ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k02 | La seconde phrase présente la réserve légale comme une règle générale, alors qu'elle n'est imposée que dans les SARL et les sociétés par actions. Elle ne s'applique ni aux SNC ni aux sociétés civiles. | « Dans les SARL et les sociétés par actions, la réserve légale reçoit au moins 5 % du bénéfice, diminué des pertes antérieures, jusqu'à atteindre 10 % du capital social. » La définition du bénéfice distribuable est inchangée. | C. com., art. L. 232-10 |
| k03 | La question est fausse en droit. Un dividende versé sans bénéfice distribuable n'est pas fictif s'il est prélevé sur des réserves disponibles, ce que permet l'article L. 232-11, al. 3. Le dividende est fictif quand il n'existe pas de **sommes distribuables** (art. L. 232-12), ou quand la distribution méconnaît la limite des capitaux propres (art. L. 232-11, al. 2). | Question : « Comment qualifie-t-on un dividende mis en distribution alors que la société n'a ni bénéfice distribuable ni réserves disponibles ? » Réponse : « De dividende fictif. C'est aussi le cas d'une distribution qui ramène les capitaux propres sous le montant du capital augmenté des réserves que la loi ou les statuts ne permettent pas de distribuer. » | C. com., art. L. 232-11 (al. 2 et 3) et L. 232-12 |
| k07 | « Selon le CGI » ouvrait une seconde réponse juste. Pour les entreprises liées, l'article 212, I-a admet un taux plus élevé si l'entreprise justifie du taux qu'elle aurait obtenu d'un établissement financier indépendant. La carte n'attend que la règle de l'article 39, 1-3°. | Question : « Selon l'article 39, 1-3° du CGI, à quelles conditions les intérêts servis aux associés sur leurs comptes courants sont-ils déductibles ? » Réponse inchangée. | CGI, art. 39, 1-3° et 212, I-a |
| k10 | « Les plateformes de financement participatif sont des prestataires européens… agréés » est trop général. Le statut de prestataire de services de financement participatif (règlement (UE) 2020/1503) ne couvre que les services de prêts et de titres aux porteurs de projets professionnels. Le statut national d'intermédiaire en financement participatif (C. mon. fin., art. L. 548-1, que la fiche cite) subsiste, notamment pour les dons et les prêts sans intérêt. | Question : « Depuis l'ordonnance du 22 décembre 2021, quel statut européen peuvent obtenir les plateformes de financement participatif ? » Réponse : « Celui de prestataire européen de services de financement participatif, agréé selon le règlement (UE) 2020/1503. Le financement participatif devient ainsi un mode de financement reconnu des PME ; le statut national d'intermédiaire en financement participatif (C. mon. fin., art. L. 548-1) subsiste à côté. » Base complétée par Définitions#9 ; `src` et `url` inchangés. | Ordonnance n° 2021-1735 ; C. mon. fin., art. L. 547-1 et L. 548-1 ; règlement (UE) 2020/1503 |
| k19 | « Sauf disposition contraire des statuts » est incomplet. L'article L. 228-40 réserve aussi le cas où l'assemblée générale décide d'exercer elle-même ce pouvoir. | « L'émission elle-même relève du conseil d'administration ou du directoire, sauf si les statuts réservent ce pouvoir à l'assemblée générale ou si celle-ci décide de l'exercer. » | C. com., art. L. 228-40 |
| k22 | Deux écarts avec la définition légale. Le crédit-bail immobilier ne porte que sur des biens immobiliers **à usage professionnel**. Le prix de levée tient compte des loyers « au moins pour partie ». | « Une location d'un bien d'équipement ou d'un bien immobilier à usage professionnel, assortie d'une promesse unilatérale de vente permettant au locataire d'acquérir le bien pour un prix convenu tenant compte, au moins pour partie, des loyers versés. » | C. mon. fin., art. L. 313-7 |
| k23 | « Dans ses comptes » : la règle (redevances en charges, bien hors de l'actif) ne vaut que pour les comptes annuels. Dans les comptes consolidés, les contrats de location-financement sont retraités (règlement ANC n° 2020-01). | Question : « … traite-t-elle les redevances dans ses comptes annuels ? » Réponse inchangée. | Plan de comptes PCG 2025, compte 612 ; règlement ANC n° 2020-01 |
| k25 | La réponse donnait un chiffre fixé par la loi de finances (« au taux normal de l'IS de 25 %… i × (1 − 0,25) »). Ce taux n'est en outre pas le taux effectif des grandes entreprises soumises à la contribution exceptionnelle (Ce qui a changé récemment#2). | « … un emprunt à i % coûte i × (1 − t) après impôt, t étant le taux d'IS. » La suite (résultat imposable suffisant, article 212 bis, cas du déficit) est inchangée. La formule reste celle de Règles essentielles#6 et #14. | CGI, art. 39, 1-1° et 219, I ; contrat §8 (pas de chiffre millésimé) |
| k35 | « Quelles contraintes de financement faut-il apprécier ? » admettait d'autres réponses justes (équilibre financier, capacité d'endettement, ratio d'endettement…). Or la carte n'attend que les deux contraintes nommées par le programme. | Question : « Selon le programme de l'UE6 du DCG, quelles sont les deux contraintes de financement à apprécier dans l'étude de la structure financière ? » Réponse inchangée. | Arrêté du 13 février 2019, annexe 1, programme de l'UE6, partie 3 |

Les 26 autres cartes ont été contrôlées sans changement : k01, k04 à k06, k08, k09, k11 à k18, k20, k21, k24, k26 à k34.

Doublons examinés et conservés, parce que les questions diffèrent :

- k04/k05 : définition, puis reprise d'une subvention finançant un bien non amortissable ;
- k15/k16 : suppression du DPS, puis valeur théorique du DPS ;
- k23/k24 : traitement comptable du crédit-bail, puis capacité d'endettement ;
- k28/k29 : définition du CMPC, puis son usage ;
- k30, k31 et k32 : définition du plan de financement, ses ressources, ses emplois.

## Recherches faites

1. **WebSearch** (legifrance.gouv.fr) : « taux effectif global R. 314-2 "méthode des intérêts composés" sommes prêtées versements dus par l'emprunteur ».
   - **Ce qui est confirmé.** Le taux effectif global relève du Code de la consommation, sous-section « Taux effectif global », articles R. 314-1 à R. 314-14 ([Légifrance](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006069565/LEGISCTA000032807602/)). L'article R. 314-2 de ce code y figure ([Légifrance](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000032807606)). Le principe de l'égalité actuarielle selon la méthode des intérêts composés est également repris par l'article R. 313-1 du Code monétaire et financier ([Légifrance](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000047256405)).
   - **Conséquence pour la carte k21.** Son contenu (définition du coût actuariel) est exact et n'a pas changé. En revanche, la référence « C. mon. fin., art. R. 314-2 » de la fiche paraît erronée (voir plus bas). La carte la recopie, comme le contrat l'exige.

Aucune autre recherche (1 sur 3 autorisées). Les autres points ont été tranchés sans recherche, à partir des textes cités par la fiche (C. com., art. L. 228-40, L. 232-10 à L. 232-12 ; C. mon. fin., art. L. 313-7 ; CGI, art. 39 et 212) et du plan comptable du dépôt.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Points de vigilance#2** :
   - « Un dividende distribué sans bénéfice distribuable […] est un dividende fictif » est trop large. Une distribution prélevée sur les réserves disponibles est licite (C. com., art. L. 232-11, al. 3). Le critère légal est l'absence de **sommes distribuables** (art. L. 232-12), c'est-à-dire de bénéfice distribuable et de réserves disponibles.
   - Relevé aussi par la première relecture : la fin de l'item (« l'autofinancement ne peut pas être négatif par distribution excessive ») est douteuse. Les dividendes mis en paiement peuvent dépasser la CAF de l'exercice sans être fictifs.
2. **Ce qui a changé récemment#4** : « les plateformes sont des prestataires européens de services de financement participatif agréés » est trop général. Ce statut ne vise que les services de prêts et de titres relevant du règlement (UE) 2020/1503. Le statut d'intermédiaire en financement participatif (C. mon. fin., art. L. 548-1) demeure, notamment pour les dons et les prêts sans intérêt.
3. **Règles essentielles#2** : l'émission d'obligations relève du conseil d'administration, du directoire ou des gérants, « sauf si les statuts réservent ce pouvoir à l'assemblée générale ou si celle-ci décide de l'exercer » (C. com., art. L. 228-40). « Sauf disposition contraire des statuts » est incomplet.
4. **Règles essentielles#10 (src)** : la référence « C. mon. fin., art. R. 314-2 » paraît erronée. Le taux effectif global et la méthode des intérêts composés relèvent du Code de la consommation (art. R. 314-1 et suivants), et le principe est repris à l'article R. 313-1 du Code monétaire et financier. La référence est à vérifier, puis à corriger.
5. **Règles essentielles#6, Chiffres et seuils#0 et Points de vigilance#0** : le taux normal de l'IS (25 %) est un taux fixé par la loi de finances. Il est marqué `stable` alors qu'il devrait être traité comme millésimé. Pour les grandes entreprises redevables de la contribution exceptionnelle, le taux effectif est en outre supérieur. Mieux vaut écrire la règle avec un taux littéral : i × (1 − t).
6. **Chiffres et seuils#2 et Règles essentielles#12** : la dotation à la réserve légale n'est obligatoire que dans les SARL et les sociétés par actions (C. com., art. L. 232-10). La fiche ne le dit pas.
7. **Définitions#4** : la définition du crédit-bail est incomplète sur deux points. Le crédit-bail immobilier porte sur des biens immobiliers « à usage professionnel ». Le prix convenu tient compte des loyers « au moins pour partie » (C. mon. fin., art. L. 313-7).
8. **Règles essentielles#5** : la règle (redevances au compte 612, bien hors de l'actif) vaut pour les comptes annuels. Dans les comptes consolidés, les contrats de location-financement sont retraités (règlement ANC n° 2020-01). À préciser.
9. **Définitions#6** (point mineur) : le PCG range aussi parmi les subventions d'investissement celles qui financent des activités à long terme (compte 138). Ce sont les « autres subventions d'investissement » : la définition de la fiche ne vise que l'acquisition ou la création d'immobilisations.
10. **Règles essentielles#0** (point mineur) : l'assemblée générale extraordinaire est « seule compétente », mais elle peut déléguer sa compétence ou ses pouvoirs au conseil d'administration ou au directoire (C. com., art. L. 225-129-1 et L. 225-129-2). La mention éviterait une lecture trop absolue.

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
