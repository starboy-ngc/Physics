# Cartes de notions : ue2-05 (Opérations sur le capital, transformation, fusion, dissolution et contrôle)

16 octobre 2026. Fichier : `data/ue2/ue2-05.cartes.json`. Fiche de référence : `data/ue2/ue2-05.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Deux passes successives ont confronté les 35 cartes au texte (`t` et `cite`) de leurs items de base, sans recherche web, comme leur consigne le prévoyait.
   - La première passe a corrigé 12 cartes (k05, k06, k10, k11, k12, k15, k16, k19, k20, k25, k28, k29).
   - La seconde en a corrigé 2 (k01, k35).
   - Aucune passe n'a supprimé ni ajouté de carte.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 16 octobre 2026 : Code de commerce, Code civil, PCG modifié par le règlement ANC n° 2022-06, loi n° 2023-171 et décret n° 2023-657, ordonnances n° 2023-393, n° 2023-1142 et n° 2025-229. Il a vérifié aussi que chaque question n'appelle qu'une seule réponse et il a recherché les doublons. Cette relecture s'est faite en deux temps :
   - une première exécution, interrompue avant l'enregistrement de son résultat, a corrigé 6 cartes (k02, k10, k15, k23, k29, k34). Ses corrections figuraient déjà dans le fichier et ont été recontrôlées ;
   - la reprise a corrigé 3 cartes de plus (k08, k19, k22).
   - Aucune carte n'a été supprimée ni ajoutée.
4. **Recherches.** Chaque exécution de la relecture d'exactitude a fait 3 recherches WebSearch, le maximum autorisé, toutes limitées à legifrance.gouv.fr (détail plus bas).

`node validate.js data/ue2/ue2-05.cartes.json` : ✓ (cartes, 35 (8 déf.)). Toutes les questions font 6 à 30 mots et toutes les réponses 8 à 70 mots, signes de ponctuation isolés non comptés.

## Bilan

- **35 cartes**, soit le maximum prévu par le contrat : 8 de définition (`def`) et 27 de compréhension (`comp`). Les identifiants k01 à k35 se suivent sans trou.
- **Définitions** : les 6 items ont chacun au moins une carte (#0 k01 ; #1 k03, k04 ; #2 k05 ; #3 k21, k22 ; #4 k26 ; #5 k32).
- **Règles essentielles** : 18 items sur 19 ont une carte.
- **Ce qui a changé récemment** : #0 a une carte (k16), de même que #2 (k35).
- **Points de vigilance** : #0 à #3 ont une carte (k17, k27, k13 et k14, k07).
- **Items de la fiche sans carte :**
  - **Règles essentielles#16** (dépôt des comptes au greffe) : pas de carte, car le jeu atteint le plafond de 35.
  - **Chiffres et seuils#0 à #5** : ces items sont des rappels de chiffres. Les chiffres stables utiles figurent dans les cartes des règles qu'ils servent (26 mois, un quart, 10 %, 5 %, deux ans, quinze jours, 1 %). Les items #4 (taux du droit de partage) et #5 (seuils du commissaire aux comptes) sont exclus : ce sont un taux fiscal et des seuils réglementaires relevés en 2024.
  - **Ce qui a changé récemment#1** (ordonnance n° 2023-393 : intitulé du chapitre et date d'application) et **#3** (décret n° 2024-152 : seuils du commissaire aux comptes) : la date d'application et les seuils sont des données datées, exclues des cartes.
  - **Points de vigilance#4** (renumérotation des articles relatifs au commissaire aux comptes) : simple table de concordance, sans notion à mémoriser.
- **Contenus couverts en partie**, sans carte propre faute de place :
  - le commissaire à la transformation (Règles essentielles#11) : seule l'attestation du commissaire aux comptes dans la SA figure en k19 ;
  - le régime de fusion à 90 % des droits de vote (Règles essentielles#13, seconde partie) ;
  - la date d'effet de la fusion (Règles essentielles#12) ;
  - le régime SARL des apports en nature et la libération intégrale des titres d'apport (Règles essentielles#5) ;
  - l'unanimité pour une majoration du nominal hors incorporation (Règles essentielles#4) ;
  - le compte définitif, le quitus et la clôture de la liquidation (Règles essentielles#15) ;
  - le « triple test » de l'article 1844-12-1 du Code civil (Ce qui a changé récemment#2).

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | k05 | La réponse rattachait l'inscription au compte 1041 au seul cas de l'augmentation en numéraire, alors que Définitions#2 l'énonce sans cette restriction. | Phrase scindée : « Lors d'une augmentation de capital en numéraire, elle est libérée en totalité dès la souscription ; elle est portée au compte 1041 Primes d'émission. » |
| 1 | k06 | Question trop ouverte (« Quelle condition préalable ») : la décision de l'AGE était aussi une réponse juste. | « Quelle condition tenant au capital existant doit être remplie avant une augmentation de capital en numéraire dans une société anonyme (SA) ou une SARL ? » |
| 1 | k10 | La tournure prêtait à la SARL la formule « autorisée ou décidée », propre à la SA. Règles essentielles#8 dit seulement « autorisée ». | « dans la SARL, elle est autorisée par l'assemblée des associés statuant dans les conditions exigées pour la modification des statuts ». |
| 1 | k11 | Phrase tronquée : « avant qu'il ait été statué en première instance », sans objet. | Ajout de « sur cette opposition », conformément à la citation de Règles essentielles#7. |
| 1 | k12 | Question ambiguë : l'achat par le gérant à titre personnel était une lecture possible, alors que la règle porte sur l'achat par la société de ses propres parts. | « Dans quel cas l'achat par une SARL de ses propres parts sociales est-il admis ? ». La réponse nomme le gérant et dit « par la société ». |
| 1 | k15 | Dernière phrase sans verbe ; réponse à 69 mots. | Même substance, reformulée : « décision qui est publiée. Sinon, … Ces règles ne s'appliquent pas en sauvegarde ou en redressement judiciaire. » |
| 1 | k16 | Le « à défaut » se lisait comme « à défaut de seuil ». | « Si ces dispositions ne sont pas respectées, la dissolution judiciaire reste encourue. » |
| 1 | k19 | Question trop ouverte (les règles de vote répondaient aussi) ; il manquait « au moment de la transformation ». | « Quelles conditions tenant à son ancienneté et à ses comptes une société anonyme (SA) doit-elle remplir pour se transformer en société d'une autre forme ? ». La réponse ajoute « au moment de la transformation ». |
| 1 | k20 | « Quelle majorité » était impropre, puisque la réponse est l'unanimité. | « Selon quelle règle de vote est décidée la transformation d'une société en société en nom collectif (SNC) ou en société par actions simplifiée (SAS) ? » |
| 1 | k25 | La question omettait la condition de durée de la détention totale. | « … détient en permanence la totalité des actions de l'absorbée, du dépôt du projet de fusion au greffe jusqu'à sa réalisation ? » |
| 1 | k28 | La question annonçait presque la réponse. | « Hors dissolution anticipée et liquidation judiciaire, quelles causes de fin d'une société l'article 1844-7 du Code civil énumère-t-il ? » |
| 1 | k29 | « ou d'un jugement » couvrait aussi l'annulation du contrat de société, qui figure sur k28. | « Selon l'article 1844-7 du Code civil, dans quels cas de dissolution anticipée ou de liquidation judiciaire une société prend-elle fin ? » |
| 2 | k01 | Un étudiant pouvait répondre par les modes d'apport (numéraire, nature, incorporation) au lieu des deux procédés attendus. | « Indépendamment de la nature des apports, par quels deux procédés le capital social d'une société anonyme (SA) peut-il être augmenté ? » Réponse inchangée. |
| 2 | k35 | Le champ de la règle n'était donné que dans la réponse ; « depuis l'ordonnance du 12 mars 2025 » était imprécis (application au 1er octobre 2025). | « Selon l'ordonnance du 12 mars 2025, par quel délai se prescrit, hors cas réservés, l'action en nullité d'une décision d'augmentation de capital d'une société par actions ? ». Mention redondante retirée de la réponse. |

## Corrections de la relecture d'exactitude

Les six premières lignes viennent de l'exécution interrompue ; les trois dernières (k08, k19, k22) viennent de la reprise.

| cible | problème | correction | source |
|---|---|---|---|
| k02 | Dans « l'assemblée générale extraordinaire, seule compétente pour décider l'augmentation, fixe la durée de la délégation », l'apposition laissait croire que, même après une délégation de compétence, l'assemblée décide encore l'augmentation. C'est l'inverse : elle a transféré au conseil ou au directoire le pouvoir de la décider. | « l'assemblée générale extraordinaire, seule compétente **en principe** pour décider l'augmentation, fixe la durée de la délégation, 26 mois au plus, et le plafond global ». Question inchangée. | C. com., art. L. 225-129 et L. 225-129-2 (Règles essentielles#2) |
| k10 | « Quelle limite absolue s'impose à toute réduction de capital » admettait une autre réponse juste pour la SA : le capital ne peut être réduit sous le minimum légal, sauf sous la condition suspensive d'une augmentation qui le porte au moins à ce minimum. | Question délimitée : « Quelle limite, tenant aux droits des associés entre eux, s'impose dans tous les cas à une réduction de capital d'une société anonyme (SA) ou d'une SARL ? ». Réponse inchangée (égalité des actionnaires ou des associés). | C. com., art. L. 225-204, L. 223-34 et L. 224-2 |
| k15 | La question visait la SARL et la SA ; or la décision des associés « dans les quatre mois » est la règle de la SARL (L. 223-42). Dans la SA, le conseil d'administration ou le directoire doit **convoquer** l'assemblée générale extraordinaire dans les quatre mois (L. 225-248, al. 1). | Question limitée à la SARL : « Que doivent faire les associés d'une SARL dont les comptes approuvés font apparaître des capitaux propres inférieurs à la moitié du capital social ? ». Réponse inchangée ; k16 et k17 traitent toujours la SA et la SARL ensemble. | C. com., art. L. 223-42 et L. 225-248 |
| k23 | La question visait « les sociétés commerciales », mais la réponse décrit la procédure propre à la SA : approbation par l'assemblée générale extraordinaire de chaque société participante (L. 236-9). | « Quelles sont les étapes principales de la procédure de fusion de sociétés anonymes (SA) prévue par le Code de commerce ? ». Réponse inchangée. | C. com., art. L. 236-9, L. 236-10 et L. 236-23 (Règles essentielles#12) |
| k29 | Une seule puce réunissait le 5° (justes motifs, à la demande d'un associé) et le 6° (réunion de toutes les parts en une seule main) de l'article 1844-7 ; or, dans le second cas, la dissolution peut être demandée par tout intéressé (art. 1844-5, al. 1). | Deux puces distinctes : dissolution prononcée par le tribunal à la demande d'un associé pour justes motifs ; dissolution prononcée par le tribunal en cas de réunion de toutes les parts en une seule main. | C. civ., art. 1844-7, 5° et 6°, et 1844-5, al. 1 |
| k34 | « Inviter le conseil ou le directoire à délibérer » est inexact pour la SA à directoire : le commissaire invite le président du conseil d'administration ou le directoire à **faire délibérer** le conseil d'administration ou le conseil de surveillance. | « inviter le président du conseil d'administration ou le directoire à faire délibérer le conseil d'administration ou de surveillance ». Autres étapes inchangées. | C. com., art. L. 234-1, al. 2 (Règles essentielles#18) |
| k08 | « Comment est décidée une augmentation de capital par incorporation… » admettait une autre réponse juste (« par l'assemblée générale, sur le rapport du conseil »), alors que la carte attend les conditions de vote. La question visait aussi les « primes » pour la SARL, alors que l'article L. 223-30 ne parle que de bénéfices ou de réserves. | « Quelles conditions de vote s'appliquent à la décision d'augmenter le capital par incorporation de réserves ou de bénéfices dans une SA, puis dans une SARL ? ». Réponse inchangée (quorum et majorité des assemblées ordinaires dans la SA ; associés représentant au moins la moitié des parts dans la SARL). | C. com., art. L. 225-130 et L. 223-30 (Règles essentielles#4) |
| k19 | La carte présentait l'existence depuis deux ans, les deux bilans approuvés et le rapport du commissaire aux comptes comme exigés de toute SA qui se transforme. Or la transformation d'une SA en SNC, qui requiert l'accord de tous les associés, est dispensée des conditions des articles L. 225-243 et L. 225-244 (L. 225-245, al. 1). | Question délimitée : « Hors transformation en société en nom collectif (SNC), quelles conditions tenant à son ancienneté et à ses comptes une société anonyme (SA) doit-elle remplir pour changer de forme ? ». Réponse inchangée. | C. com., art. L. 225-243, L. 225-244 et L. 225-245, al. 1 (texte cité par Règles essentielles#10) |
| k22 | La réponse présentait la remise de parts ou d'actions des sociétés bénéficiaires comme systématique. Or il n'y a pas d'échange de titres lorsque l'absorbante détient la totalité du capital de l'absorbée, ni dans les autres cas d'opérations intragroupe prévus par l'article L. 236-3, II. | « **En principe**, par des parts ou des actions des sociétés bénéficiaires et, éventuellement, par une soulte en espèces… ». Le reste est inchangé. | C. com., art. L. 236-1 et L. 236-3, II (Définitions#3) |

Les 26 autres cartes ont été contrôlées sans changement : k01, k03 à k07, k09, k11 à k14, k16 à k18, k20, k21, k24 à k28, k30 à k33 et k35. En particulier :
- **k06** est à jour. Pendant la reprise, la page Légifrance de l'article L. 223-7 n'affiche aucune modification par l'ordonnance n° 2025-229. Les articles L. 223-43 et L. 224-3 du même titre ont, eux, été modifiés par cette ordonnance. La nullité de l'augmentation de capital de SARL décidée alors que le capital ancien n'est pas intégralement libéré figure donc toujours au dernier alinéa de L. 223-7, rendu applicable par L. 223-32. Pour la SA, la carte n'affirme aucune nullité.
- **k35** est conforme à l'article 1844-14 du Code civil dans sa rédaction issue de l'article 6 de l'ordonnance n° 2025-229, en vigueur depuis le 1er octobre 2025. La prescription de droit commun des actions en nullité de la société, d'apport ou de décisions sociales passe de trois à deux ans, sous réserve des règles propres aux fusions, scissions et modifications du capital. C'est l'une de ces règles, le délai de trois mois de L. 225-149-4, que la carte interroge.
- **k25.** Le droit des actionnaires de l'absorbante réunissant 5 % du capital de demander la convocation de son assemblée a été conservé. Il conditionne la dispense d'approbation de la fusion par l'assemblée de l'absorbante prévue par la directive (UE) 2017/1132. Aucune recherche n'a été faite ; le point reste inscrit dans `POINTS-OUVERTS.md`.
- **k09** est conforme à l'article L. 225-147 en vigueur (recherche 1 de l'exécution interrompue).
- **k05** : le compte 1041 Primes d'émission subsiste dans la liste des comptes du PCG modifiée par le règlement ANC n° 2022-06 (plan local `data/pcg/classe1.json`).
- **k33** : l'article L. 821-53, issu de l'ordonnance n° 2023-1142, est bien le siège actuel de la certification.
- **Doublons.** Aucun doublon n'a été trouvé, pour les raisons suivantes :
  - k26 et k27 opposent l'associé unique personne morale (TUP) à l'associé unique personne physique (liquidation), comme Points de vigilance#1 ;
  - k28 et k29 se partagent la liste de l'article 1844-7, découpage utile pour la mémorisation ;
  - k13 définit le coup d'accordéon ; k14 donne les conditions de l'arrêt Usinor ;
  - k06 porte sur la libération préalable du capital existant ; k07 sur les quotités minimales de libération ;
  - k15 (procédure dans la SARL), k16 (seconde étape issue de la loi du 9 mars 2023) et k17 (sanction) ne se recouvrent pas.

## Recherches faites

**Reprise** : 3 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr.

1. Requête « ordonnance n° 2025-229 du 12 mars 2025 article L. 223-7 code de commerce « à peine de nullité de l'opération » supprimés ».
   - **Non concluant.** Les résultats montrent que l'ordonnance abroge d'autres articles en matière de nullité, par exemple L. 235-7. La page de L. 223-7 contient toujours la formule « à peine de nullité de l'opération ».
   - Sources : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316108 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006222923
2. Requête « Article L223-7 Code de commerce version en vigueur depuis le 1er octobre 2025 modifié par Ordonnance n°2025-229 capital social intégralement libéré avant toute souscription de nouvelles parts sociales ».
   - **Confirmé.** La page Légifrance de L. 223-7 ne porte aucune modification par l'ordonnance n° 2025-229, contrairement à L. 223-43 (LEGIARTI000051322366) et à L. 224-3 (LEGIARTI000051322376), modifiés par elle.
   - Effet : k06 est maintenue telle quelle.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006222923 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051322366
3. Requête « Article 1844-14 Code civil version en vigueur ordonnance 2025-229 actions en nullité de la société se prescrivent par deux ans ».
   - **Confirmé.** L'article 1844-14, modifié par l'article 6 de l'ordonnance et en vigueur depuis le 1er octobre 2025, ramène de trois à deux ans la prescription des actions en nullité de la société, d'apport ou de décisions sociales, à compter du jour où la nullité est encourue. Les règles propres aux fusions, scissions et modifications du capital sont réservées. Le rapport au Président de la République le confirme.
   - Effet : k35 est exacte.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006444195 ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316022

**Exécution interrompue** : 3 recherches, toutes limitées à legifrance.gouv.fr.

1. Article L. 225-147 (commissaires aux apports désignés à l'unanimité des actionnaires ou, à défaut, en justice ; approbation expresse des apporteurs si l'assemblée réduit l'évaluation). Confirmé : k09 est exacte. Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048539465
2. Article L. 225-248 (dans la SA, convocation de l'AGE dans les quatre mois). Confirmé : k15 a été limitée à la SARL ; k16 et k17 sont exactes. Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000047292156 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000047292166
3. Article L. 223-7, dernier alinéa (nullité de l'augmentation en numéraire de SARL si le capital n'est pas intégralement libéré). Confirmé, et recoupé par la reprise. Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006222923

Aucune recherche n'a été faite pour les corrections de k02, k08, k10, k19, k22, k23, k29 et k34. Elles reposent sur des textes stables, cités par les items de base ou voisins de ceux-ci : C. com., art. L. 225-129-2, L. 225-130, L. 223-30, L. 224-2, L. 225-243 à L. 225-245, L. 236-3, L. 236-9 et L. 234-1 ; C. civ., art. 1844-5 et 1844-7. Elles délimitent la question ou nuancent la réponse, sans rien ajouter au verso qui sorte des items de base.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#9** (capitaux propres inférieurs à la moitié du capital), avec **Chiffres et seuils#2** (« consultation des associés dans les quatre mois »). La règle « dans les quatre mois …, les associés décident s'il y a lieu à dissolution anticipée » est celle de la SARL (art. L. 223-42). Dans la SA, l'article L. 225-248, alinéa 1, oblige le conseil d'administration ou le directoire à **convoquer l'assemblée générale extraordinaire** dans les quatre mois de l'approbation des comptes. L'item pourrait aussi préciser que, dans la SA, la réduction de capital se fait « sous réserve de l'article L. 224-2 » (capital minimal).
2. **Règles essentielles#18** (procédure d'alerte dans la SA). « Il invite le conseil ou le directoire à délibérer » est à remplacer par la formule de l'article L. 234-1 : le commissaire invite le président du conseil d'administration ou le directoire à faire délibérer le conseil d'administration ou le conseil de surveillance sur les faits relevés.
3. **Règles essentielles#14** (causes de dissolution). La formule « dissolution anticipée prononcée par le tribunal à la demande d'un associé pour justes motifs, ou dans le cas de réunion de toutes les parts en une seule main » réunit deux cas distincts de l'article 1844-7 (5° et 6°). Dans le second, la dissolution peut être demandée par tout intéressé (art. 1844-5, al. 1). Il vaut mieux les séparer.
4. **Règles essentielles#12** (procédure de fusion). L'approbation « par l'assemblée générale extraordinaire de chaque société participante » est la règle de la SA (art. L. 236-9). L'item gagnerait à porter la mention « (SA) » ou à rappeler que, dans la SARL, la fusion est décidée par les associés aux conditions de modification des statuts.
5. **Règles essentielles#10** (transformation). « Une SA ne peut se transformer que si … elle existe depuis deux ans au moins et a établi et fait approuver … le bilan de ses deux premiers exercices » est trop général. La transformation d'une SA en SNC, qui requiert l'accord de tous les associés, n'est pas soumise aux conditions des articles L. 225-243 et L. 225-244 (art. L. 225-245, al. 1, cité par l'item). Par ailleurs, l'article L. 223-43, également cité, a été modifié par l'ordonnance n° 2025-229 : sa rédaction en vigueur depuis le 1er octobre 2025 est à relire, en particulier la sanction de la transformation irrégulière. L'item #11 cite L. 224-3, lui aussi modifié par cette ordonnance.
6. **Définitions#3** (fusion et scission). L'item gagnerait à préciser que la remise de parts ou d'actions aux associés des sociétés qui disparaissent est le principe. Il n'y a pas d'échange de titres lorsque l'absorbante détient la totalité du capital de l'absorbée, ni dans les autres cas prévus par l'article L. 236-3, II.

## Classement des exercices

Le classement automatique porte sur les 24 exercices QCM, QCM multiples et classements du chapitre (22 QCM, 1 QCM multiple, 1 classement) :

| nature | nombre |
|---|---|
| notion | 21 |
| calcul | 2 |
| chiffre | 1 |

Les classements ne divergent sur aucun exercice. Les 21 exercices de nature notion (19 QCM, le QCM multiple et le classement) entrent dans les révisions espacées, avec les 35 cartes. Les autres restent hors des révisions espacées :
- **Les 2 QCM de nature calcul.** Le premier demande une date limite de reconstitution des capitaux propres à décompter à partir de dates données. Le second demande le seuil de capital d'une SA à partir de son total de bilan.
- **Le QCM de nature chiffre.** Il porte sur les seuils de désignation du commissaire aux comptes applicables depuis 2024.
- **Les 6 exercices de calcul du chapitre** (type `calc`). Ils ne relèvent pas de ce classement.
