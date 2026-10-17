# Cartes de notions : ue6-06 (Trésorerie et marchés financiers)

*16 octobre 2026*

Fichier : `data/ue6/ue6-06.cartes.json`. Fiche de référence : `data/ue6/ue6-06.fiche.json` (non modifiée, mise à jour du 14 octobre 2026). Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les 34 cartes d'origine (k01 à k34) ont été rédigées à partir de la seule fiche du chapitre. Elles respectent la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.
2. **Relectures de fidélité.** Trois passes successives ont contrôlé les cartes au regard de la seule fiche, sans recherche web :
   - la première a corrigé 6 cartes (k01, k03, k14, k15, k22, k28) ;
   - la deuxième en a corrigé 3 (k10, k28, k31) ;
   - la troisième en a corrigé 3 (k28, k30, k32) et a ajouté k35 pour couvrir les comptes 5186 et 5187 de Règles essentielles#8.

   Le jeu comptait alors 35 cartes. Le détail figure dans le tableau plus bas.
3. **Relecture d'exactitude.** C'est la présente relecture, faite par un second relecteur indépendant. Il a contrôlé les 35 cartes sur quatre points :
   - **Exactitude** au 16 octobre 2026 : Code de commerce, Code monétaire et financier, CGI, CSS, PCG modifié par le règlement ANC n° 2022-06.
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse juste serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand l'item de fiche était lui-même en cause, la fiche n'a pas été touchée. La correction a resserré la question, retiré ou nuancé la proposition inexacte, ou supprimé la carte quand elle ne pouvait pas rester exacte tout en restant portée par ses items de base. Chaque item en cause est signalé plus bas. Bilan : 11 cartes corrigées, 2 supprimées (k32 fusionnée dans k30, k35 fausse), aucun ajout.
4. **Recherches.** Trois recherches web ont été faites : une sur anc.gouv.fr et deux sur legifrance.gouv.fr (détail plus bas). Les comptes ont aussi été vérifiés avec le plan comptable du dépôt (`data/pcg/classe5.json`, `data/pcg/classe4.json`, `data/pcg/classe1.json`) et la section 6 du contrat (compte 1648).

Validation : `node validate.js data/ue6/ue6-06.cartes.json` renvoie « ✓ data/ue6/ue6-06.cartes.json (cartes, 33 (14 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées | 35 |
| Cartes au final | 33 |
| Définition (`def`) | 14 |
| Compréhension (`comp`) | 19 |
| Corrigées par les relectures de fidélité | 12 corrections sur 10 cartes (k01, k03, k10, k14, k15, k22, k28 trois fois, k30, k31, k32) et 1 ajout (k35) |
| Corrigées par la relecture d'exactitude | 11 (k05, k08, k09, k11, k12, k16, k17, k21, k27, k30, k33) |
| Supprimées | 2 (k32, k35) |
| Ajoutées | 0 |
| Identifiants libres (à ne jamais réutiliser) | k32, k35 |

Les questions font de 8 à 27 mots, les réponses de 19 à 46 mots.

**Couverture de la fiche.**

- **Définitions** : chacun des neuf items a au moins une carte (k01, k09, k13, k14, k15, k20, k22, k23, k26).
- **Règles essentielles** : les seize items sont couverts.
- **Points de vigilance** : #0 à #3 ont chacun une carte de compréhension (k02, k10, k24, k11). #4 est la base secondaire de k27.
- **Ce qui a changé récemment** : #0 est couvert par k19, #2 par k30 (base secondaire, après la fusion de k32).
- **Chiffres et seuils** : #0, #1 et #2 sont portés par k12, k21 et k04.

**Items de la fiche sans carte :**

- **Chiffres et seuils#3** (épreuve de l'UE6) et **Ce qui a changé récemment#1** (calendrier des programmes) : aucune notion à réviser.
- **Définitions#8, seconde phrase** : elle renvoie au Code monétaire et financier pour le marché réglementé et le système multilatéral de négociation, sans en donner de définition.
- **Règles essentielles#8, partie « 5186 / 5187 »** : ces numéros de comptes sont faux (voir le point de fiche n° 1). La carte k35 qui les reprenait a été supprimée. Le reste de l'item (coupon couru, compte 5088) reste porté par k18.

## Corrections des relectures de fidélité

Le tableau reprend les trois passes dans l'ordre. Certaines corrections ont ensuite été reprises ou annulées par la relecture d'exactitude : k30 (seconde phrase remplacée lors de la fusion), k32 et k35 (supprimées).

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | k01 | La fiche dit que la construction du budget et son équilibrage relèvent de la partie « la gestion de la trésorerie » du programme. La réponse en faisait une affirmation de fond. | Seconde phrase réécrite : « … relèvent, dans le programme, de la gestion de la trésorerie ». |
| 1 | k03 | « Quels éléments, bien qu'enregistrés en charges ou en produits, ne figurent pas dans le budget ? » appelait une liste ouverte, avec plusieurs réponses justes possibles. | Question de compréhension : « Pourquoi les dotations, les variations de stocks et la quote-part de subvention (747) ne figurent-elles pas dans le budget de trésorerie ? ». La réponse s'appuie sur Règles essentielles#3. |
| 1 | k14 | La question (« cession Dailly de créances professionnelles ») contenait une partie de la définition. | « Qu'est-ce que la cession Dailly prévue par le Code monétaire et financier ? ». Réponse inchangée. |
| 1 | k15 | La question (« affacturage comme mode de financement des créances commerciales ») contenait une partie de la réponse. | « Qu'est-ce que l'affacturage dans le financement à court terme de l'entreprise ? ». Réponse inchangée. |
| 1 | k22 | La question affirmait que la SICAV et le FCP sont « les deux formes d'OPCVM », ce que la fiche ne dit pas. | « Parmi les OPCVM, qu'est-ce qui distingue une SICAV d'un fonds commun de placement ? ». |
| 1 | k28 | « Comment se détermine » le droit de vote présentait comme absolue une règle de principe (art. L. 225-122), qui connaît des exceptions. | « Selon le Code de commerce, quel principe détermine le droit de vote attaché aux actions ? ». La réponse commence par « Le droit de vote est proportionnel… ». |
| 2 | k10 | La question qualifiait le découvert permanent de « signal d'alerte ». La fiche dit seulement qu'il masque un besoin de financement stable. | « Que masque un découvert bancaire permanent dans le financement d'une entreprise ? ». Réponse : « Un besoin de financement stable. … ». |
| 2 | k28 | « Selon le Code de commerce, … actions » faisait d'une règle de la SA une règle générale pour toutes les actions. | La question est limitée à l'article L. 225-122. |
| 2 | k31 | « D'une durée de 1 semaine à 12 mois » laissait croire que l'Euribor lui-même a une durée. | « Décliné sur des durées de 1 semaine à 12 mois ». |
| 3 | k28 | La question invitait encore à étendre à la SAS une règle propre à la SA. | « Dans une société anonyme, quel principe l'article L. 225-122 du Code de commerce pose-t-il pour le droit de vote attaché aux actions ? ». |
| 3 | k30 | « Indexés sur ce type de taux de référence » généralisait la fiche. | « Avec l'Euribor, c'est un taux de référence auquel sont indexés les placements monétaires et les crédits à taux variable. » (phrase remplacée ensuite lors de la fusion avec k32) |
| 3 | k32 | « Quel taux a remplacé l'Eonia » affirmait un remplacement que la fiche ne formule pas. La réponse répétait la question. | « Depuis la disparition de l'Eonia, quel est le seul taux de référence au jour le jour de la zone euro ? » (carte supprimée ensuite comme doublon de k30) |
| 3 | k35 (ajout) | Le rattachement des intérêts courus sur concours bancaires (Règles essentielles#8) n'avait pas de carte. | Carte `comp` ajoutée sur les comptes 5186 et 5187 (supprimée ensuite : numéros de comptes faux). |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k35 (supprimée) | Les comptes 5186 et 5187 n'existent pas dans le plan de comptes. Le compte 518 « Intérêts courus » se subdivise en 5181 « Intérêts courus à payer » et 5188 « Intérêts courus à recevoir » ; les intérêts courus sur concours bancaires courants vont en 5198. La carte était fausse. Corrigée en 5181/5188, elle n'aurait plus été portée par son item de base (Règles essentielles#8). | Carte supprimée ; l'identifiant k35 reste libre. Le reste de l'item (coupon couru, 5088) est porté par k18, exact. | Plan de comptes PCG 2025 et 2026 (ANC), comptes 518, 5181, 5188, 519, 5198 ; `data/pcg/classe5.json` |
| k32 (supprimée, fusionnée dans k30) | Doublon inversé de k30 : « Qu'est-ce que l'€STR ? » et « Quel est le seul taux au jour le jour ? → l'€STR » testent le même fait. | Carte supprimée. Son contenu (disparition de l'Eonia, seul taux de référence au jour le jour, comparaison des OPCVM monétaires) est repris dans k30. | Orientation (UE) 2019/1265 de la BCE |
| k30 | Fusion avec k32. La seconde phrase (indexation, avec l'Euribor) faisait aussi doublon avec k31. | Réponse : « Le taux au jour le jour en euros administré par la Banque centrale européenne. Depuis la disparition de l'Eonia, le 3 janvier 2022, c'est le seul taux de référence au jour le jour de la zone euro ; les OPCVM monétaires s'y comparent. » `base` : Règles essentielles#15 et Ce qui a changé récemment#2. | Orientation (UE) 2019/1265 de la BCE |
| k09 | « Les soldes créditeurs de banques (découvert, facilité de caisse), enregistrés au compte 519 » est inexact. Le découvert est le solde créditeur du compte 512 lui-même, présenté au passif. Le compte 519 enregistre les concours distincts du compte courant : 5191 (CMCC), 5193, 5198. | Q : « Que désignent les concours bancaires courants dans la trésorerie d'une entreprise ? ». R : « Les financements bancaires courants, tels le découvert et la facilité de caisse : ils forment la trésorerie passive, et non des dettes financières. Le compte 519 « Concours bancaires courants » suit notamment le crédit de mobilisation de créances commerciales (5191). » | Plan de comptes PCG 2025, comptes 512, 519, 5191, 5198 ; PCG, tableau de financement |
| k08 | Même erreur : « (519) » était rattaché aux soldes créditeurs de banques. Par ailleurs, « Comment le PCG définit-il la trésorerie nette ? » admettait d'autres réponses justes (FRNG − BFR ; trésorerie active − trésorerie passive). | Q : « Selon le tableau de financement du PCG, de quoi se compose la trésorerie nette d'une entreprise ? ». R : « Des disponibilités (512, 53) diminuées des concours bancaires courants (519) et des soldes créditeurs de banques. … » | PCG, chapitre « Tableau de financement » ; plan de comptes PCG 2025 |
| k05 | « À la livraison pour les ventes de biens » n'est que le principe. Depuis le 1er janvier 2023, les acomptes encaissés sur une livraison de biens rendent la TVA exigible dès leur encaissement. | La question délimite le champ : « … quand la TVA devient-elle **en principe** exigible … ? ». Réponse inchangée. | CGI, art. 269, 2, a (rédaction issue de la loi de finances pour 2022) |
| k11 | « À quel risque juridique s'expose… » admettait plusieurs réponses justes (redressement ou liquidation judiciaire, sanctions des dirigeants). | Q : « Quelle situation, définie par le Code de commerce, menace une entreprise dont le déficit de trésorerie n'est pas financé ? ». Réponse inchangée (cessation des paiements). | C. com., art. L. 631-1 |
| k12 | L'article L. 313-12 ne vise que les concours consentis à une entreprise. La question ne le disait pas. | « … un concours à durée indéterminée, autre qu'occasionnel, consenti à une entreprise ? ». | C. mon. fin., art. L. 313-12 |
| k16 | « Se calcule actuariellement » est inexact pour un crédit professionnel. Le TEG y est un taux annuel **proportionnel** au taux de période, et seul ce taux de période est calculé actuariellement. | « … et repose sur un calcul actuariel. » Le reste est inchangé. | C. consom., art. R. 314-2, applicable aux crédits professionnels (renvoi de C. mon. fin., art. L. 313-4 et R. 313-1) |
| k17 | « Les commissions bancaires sont des charges externes (627) » n'est vrai que des commissions qui rémunèrent un service. La commission d'endos, calculée en fonction de la durée, est traitée comme des intérêts (6616). | Q : « Selon le PCG 2025, comment classe-t-on les intérêts d'escompte ou de découvert et les commissions rémunérant des services bancaires ? ». R : « … ; ces commissions sont des charges externes (627 …) ». | Plan de comptes PCG 2025, comptes 627, 6275, 6616 |
| k21 | Depuis la réforme de 2016, les « certificats de dépôt » ne sont plus une catégorie juridique distincte. Les titres de créances négociables comprennent les titres négociables à court terme (NEU CP, qui regroupent les anciens certificats de dépôt et billets de trésorerie) et à moyen terme (NEU MTN). | Q : « Pourquoi les titres négociables à court terme (NEU CP) sont-ils réservés aux trésoreries importantes ? ». R : « Parce que leur montant unitaire est au moins égal à 150 000 € (ou à sa contre-valeur en devises). » `base` complétée par Définitions#5. | C. mon. fin., art. D. 213-1 ; décret n° 2016-707 et arrêté du 30 mai 2016 |
| k27 | « Les contrats financiers servent à couvrir les risques… » : ils servent aussi à spéculer ou à arbitrer, la couverture n'est qu'un usage. | « … peuvent servir à couvrir les risques de taux et de change. » | C. mon. fin., art. L. 211-1 |
| k33 | « Comment traite-t-on les créances et dettes en devises et leurs écarts ? » appelait une réponse plus large que la carte : un correcteur attend aussi la provision pour perte de change (1515). Par ailleurs, « dernier cours de change » n'était pas situé à la clôture. | Q : « Selon le PCG, où inscrit-on les écarts de conversion constatés à la clôture sur les créances et dettes en monnaies étrangères ? ». R : « En comptes transitoires : 476 pour une perte latente, 477 pour un gain latent. Ces écarts résultent de la conversion des créances et dettes au dernier cours de change. » | PCG, art. 420-5 ; plan de comptes PCG 2025, comptes 476, 477, 1515 |

Les 22 autres cartes ont été contrôlées sans changement : k01 à k04, k06, k07, k10, k13 à k15, k18 à k20, k22 à k26, k28, k29, k31 et k34. En particulier :

- **k04** : l'option trimestrielle quand la TVA exigible annuelle est inférieure à 4 000 € est celle de l'article 287, 2 du CGI. Ce seuil est stable (non revalorisé chaque année).
- **k06** : 5 ou 15 du mois suivant selon l'effectif et la date de paie, conforme à l'article R. 243-6 du CSS.
- **k07** : neuf mois après la clôture, sauf prolongation par décision de justice, conforme à l'article L. 232-13.
- **k13** : la question précise « d'un effet de commerce auprès d'une banque », ce qui écarte l'escompte de règlement (réduction financière).
- **k18** : le coupon couru payé à l'achat et les intérêts courus sur obligations détenues vont bien en 5088. Le `src` recopie la mention des comptes 5186 et 5187, comme le contrat l'exige (voir le point de fiche n° 1).
- **k19** : le compte 1648 est confirmé par la section 6 du contrat.
- **k28** : la question, limitée à la SA et au principe de l'article L. 225-122, est exacte. Le droit de vote double et la limitation du nombre de voix sont des exceptions que la question n'exclut pas.

Doublons examinés et conservés, parce que les questions diffèrent :

- k02/k03 : TTC et dates de règlement, puis éléments sans flux ;
- k09/k10 : définition des concours bancaires courants, puis découvert permanent ;
- k13/k14 : escompte, puis cession Dailly (qui ne nécessite pas d'effet) ;
- k20/k21 : définition des TCN, puis montant unitaire minimal ;
- k30/k31 : €STR, puis Euribor ;
- k33/k34 : écarts de conversion, puis couverture à terme.

Aucune carte ne demande de calcul. Les seuls chiffres conservés sont stables et font partie d'une règle : 60 jours (k12), 150 000 € (k21), 4 000 € (k04), neuf mois (k07), le 5 ou le 15 du mois (k06) et la date de disparition de l'Eonia (k30).

## Recherches faites

1. **WebSearch** (anc.gouv.fr) : « plan de comptes PCG 2025 518 intérêts courus 5181 intérêts courus à payer 5188 intérêts courus à recevoir 5198 ».
   - **Doute de départ.** Le plan du dépôt (`data/pcg/classe5.json`) numérote 5181 et 5188 ; la fiche et k35 écrivent 5186 et 5187.
   - **Ce qui est confirmé.** Les plans de comptes 2024, 2025 et 2026 de l'ANC donnent tous 518 « Intérêts courus », 5181 « Intérêts courus à payer », 5188 « Intérêts courus à recevoir », et 5198 « Intérêts courus sur concours bancaires courants » sous le 519 ([plan de comptes PCG 2025](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/Plan-de-comptes-PCG-2025.pdf) ; [plan de comptes 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/Plan-de-comptes-2026.pdf) ; [plan de comptes 2024](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/Recueils/PCG_Janvier2024/Plan-de_comptes_PCG-2024.pdf)).
   - **Conséquence.** k35 supprimée ; point de fiche n° 1.
2. **WebSearch** (legifrance.gouv.fr) : « Code monétaire et financier article R. 314-2 taux effectif global taux annuel proportionnel au taux de période calculé actuariellement ».
   - **Doute de départ.** Pour un crédit de trésorerie d'entreprise, le TEG est-il « calculé actuariellement », comme le disent la fiche et k16 ?
   - **Ce qui est confirmé.** Pour les crédits destinés à une activité professionnelle, le TEG est un taux annuel proportionnel au taux de période, à terme échu ; le taux de période est calculé actuariellement. Ces règles figurent dans le Code de la consommation (art. L. 314-1 et R. 314-1 et suivants), auquel renvoie le Code monétaire et financier (art. R. 313-1) ([C. consom., sous-section « Taux effectif global », art. R. 314-1 à R. 314-14](https://www.legifrance.gouv.fr/codes/id/LEGISCTA000032807602) ; [C. consom., sous-section « Taux effectif global », art. L. 314-1 à L. 314-5](https://www.legifrance.gouv.fr/codes/id/LEGISCTA000032228043/2020-12-29) ; [C. mon. fin., paragraphe « Taux effectif global », art. R. 313-1](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000006194110/2025-02-20)).
   - **Conséquence.** k16 corrigée ; point de fiche n° 3.
3. **WebSearch** (legifrance.gouv.fr) : « Code monétaire et financier D. 213-1 titres de créances négociables titres négociables à court terme titres négociables à moyen terme montant unitaire 150 000 euros ».
   - **Doute de départ.** Les « certificats de dépôt » existent-ils encore comme catégorie ? D'où vient le seuil de 150 000 € ?
   - **Ce qui est confirmé.** L'article D. 213-1 range les TCN en deux catégories : titres négociables à court terme (durée initiale d'un an au plus) et à moyen terme (plus d'un an). Le montant unitaire minimal de 150 000 € (ou sa contre-valeur) est fixé par l'arrêté du 30 mai 2016. Pour les titres à moyen terme, il connaît une exception pour une catégorie d'émetteurs ([C. mon. fin., art. D. 213-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051377824) ; [section « Les titres de créances négociables »](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000006169748/) ; [arrêté du 30 mai 2016](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000032611052) ; [décret n° 2016-707 du 30 mai 2016](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000032611011)).
   - **Conséquence.** k21 corrigée ; point de fiche n° 6.

Trois recherches sur trois autorisées. Les autres points ont été tranchés sans recherche, à partir des textes cités par la fiche et du plan comptable du dépôt :

- CGI, art. 269 et 287 ;
- CSS, art. R. 243-6 ;
- C. com., art. L. 225-122, L. 232-13 et L. 631-1 ;
- C. mon. fin., art. L. 211-1, L. 313-12 et L. 313-23 ;
- PCG, art. 420-5.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#8 (et textes#2, objet)** : les comptes 5186 et 5187 n'existent pas. Le plan de comptes PCG 2025 donne 5181 « Intérêts courus à payer » et 5188 « Intérêts courus à recevoir » (compte 518) ; les intérêts courus sur concours bancaires courants vont en 5198. La carte k35 a été supprimée pour cette raison ; k18 recopie le `src` erroné.
2. **Définitions#1 et Règles essentielles#4** (déjà signalé par la première relecture de fidélité, confirmé ici) : les soldes créditeurs de banques ne sont pas enregistrés au compte 519. Le découvert est le solde créditeur du compte 512, présenté au passif. Le compte 519 enregistre les concours bancaires courants distincts du compte courant (5191, 5193, 5198). Écrire par exemple : « concours bancaires courants (compte 519) et soldes créditeurs de banques (compte 512 créditeur) ».
3. **Règles essentielles#6 (src et texte)** : la référence « C. mon. fin., art. L. 314-1 et R. 314-2 » paraît erronée. L'article L. 314-1 du Code monétaire et financier porte sur les services de paiement. Le TEG est défini par le Code de la consommation (art. L. 314-1 et R. 314-1 et suivants), applicable par renvoi des articles L. 313-4 et R. 313-1 du Code monétaire et financier. Pour un crédit professionnel, le TEG est un taux annuel proportionnel au taux de période, ce dernier étant calculé actuariellement. « Il est calculé actuariellement » est donc à nuancer.
4. **Règles essentielles#1** : la TVA sur les livraisons de biens est exigible à la livraison **en principe**. Depuis le 1er janvier 2023, les acomptes encaissés avant la livraison rendent la TVA exigible dès leur encaissement (CGI, art. 269, 2, a). Ajouter « en principe » ou mentionner les acomptes, qui comptent dans un budget de TVA.
5. **Règles essentielles#13** :
   - préciser que la conversion au dernier cours de change se fait à la date de clôture, ou d'arrêté des comptes (déjà signalé par la première relecture) ;
   - mentionner que la perte latente (476) est couverte par une provision pour pertes de change (1515), ce qu'un correcteur attend.
6. **Chiffres et seuils#1** :
   - « NEU CP et certificats de dépôt » est daté. Depuis la réforme de 2016 (décret n° 2016-707 et arrêté du 30 mai 2016), les certificats de dépôt et les billets de trésorerie sont regroupés dans les titres négociables à court terme (NEU CP) ;
   - le seuil de 150 000 € est fixé par l'arrêté du 30 mai 2016, auquel le `src` devrait renvoyer à côté de l'article D. 213-1 ;
   - pour les titres à moyen terme, le seuil connaît une exception pour une catégorie d'émetteurs.
7. **Règles essentielles#12** (point mineur) : « ces derniers servent à couvrir les risques de taux et de change » est trop fermé. Les contrats financiers peuvent servir à la couverture, mais aussi à la spéculation ou à l'arbitrage. Écrire « peuvent servir ».
8. **Règles essentielles#7** (point mineur) : « les commissions bancaires sont des charges externes (627) » vaut pour les commissions qui rémunèrent un service. La commission d'endos, calculée en fonction de la durée, est traitée comme des intérêts (6616).
9. **Règles essentielles#9** (déjà signalé par les trois relectures de fidélité) :
   - l'article L. 225-122 est une règle de la SA, posée « sous réserve » d'exceptions (droit de vote double, art. L. 225-123 ; limitation du nombre de voix, art. L. 225-125) ;
   - l'url de l'item (LEGIARTI000006229031) semble viser l'article L. 232-12 et non l'article L. 225-122.
10. **Règles essentielles#0 et Chiffres et seuils#2** (déjà signalé) : harmoniser. La déclaration trimestrielle est une **option**, ouverte lorsque la TVA **exigible** annuelle est inférieure à 4 000 €.
11. **Définitions#8** (déjà signalé) : la seconde phrase ne définit ni le marché réglementé ni le système multilatéral de négociation, qui ne peuvent donc pas donner de carte.

## Classement des exercices

Le chapitre compte 26 exercices. Le classement automatique porte sur les 17 qui peuvent entrer dans les révisions espacées (QCM, QCM multiples et classements) :

| nature | nombre |
|---|---|
| notion | 15 (12 QCM, 2 QCM multiples, 1 classement) |
| calcul | 2 |
| chiffre | 0 |

Les deux exercices de nature calcul sont :

- **#17** : rendement d'une action à partir de son cours et de son dividende ;
- **#19** : prix payé pour une obligation à partir du cours au pied du coupon et du coupon couru.

Les 9 autres exercices sont des exercices de calcul rédigés (budget de trésorerie, TVA à décaisser, agios de découvert et d'escompte, affacturage, PER, valeur d'une obligation). Ils restent hors des révisions espacées.

Aucun désaccord n'a été relevé entre les classements. Les 15 exercices de nature notion entrent dans les révisions espacées, avec les 33 cartes. L'exercice #13 (« Les NEU CP (anciens billets de trésorerie) ») est cohérent avec la réforme de 2016 relevée au point de fiche n° 6.
