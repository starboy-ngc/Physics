# Cartes de notions : ue2-05 (Opérations sur le capital, transformation, fusion, dissolution et contrôle)

16 octobre 2026. Fichier : `data/ue2/ue2-05.cartes.json`. Fiche de référence : `data/ue2/ue2-05.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Deux passes successives ont confronté les 35 cartes au texte (`t` et `cite`) de leurs items de base, sans recherche web : la consigne de ces passes l'interdisait.
   - La première passe a corrigé 12 cartes (k05, k06, k10, k11, k12, k15, k16, k19, k20, k25, k28, k29).
   - La seconde en a corrigé 2 (k01, k35).
   - Aucune n'a supprimé ni ajouté de carte.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 16 octobre 2026 : Code de commerce, Code civil, PCG modifié par le règlement ANC n° 2022-06, loi n° 2023-171 et décret n° 2023-657, ordonnances n° 2023-393, n° 2023-1142 et n° 2025-229. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse et il a recherché les doublons. Bilan : 6 cartes corrigées (k02, k10, k15, k23, k29, k34), aucune suppression et aucun ajout.
4. **Recherches.** Le second relecteur a fait 3 recherches WebSearch, le maximum autorisé, toutes limitées à legifrance.gouv.fr. Elles portaient sur les articles L. 225-147, L. 225-248 et L. 223-7 du Code de commerce (détail plus bas).

`node validate.js data/ue2/ue2-05.cartes.json` : ✓ (cartes, 35 (8 déf.)). Toutes les questions font 6 à 30 mots et toutes les réponses 8 à 70 mots.

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

| cible | problème | correction | source |
|---|---|---|---|
| k02 | Dans « l'assemblée générale extraordinaire, seule compétente pour décider l'augmentation, fixe la durée de la délégation », l'apposition laissait croire que, même après une délégation de compétence, l'assemblée décide encore l'augmentation. C'est l'inverse : elle a transféré au conseil ou au directoire le pouvoir de la décider. | « l'assemblée générale extraordinaire, seule compétente **en principe** pour décider l'augmentation, fixe la durée de la délégation, 26 mois au plus, et le plafond global ». Question inchangée. | C. com., art. L. 225-129 et L. 225-129-2 (Règles essentielles#2) |
| k10 | « Quelle limite absolue s'impose à toute réduction de capital » admettait une autre réponse juste pour la SA : le capital ne peut être réduit sous le minimum légal, sauf sous la condition suspensive d'une augmentation qui le porte au moins à ce minimum. Un correcteur ne pourrait pas refuser cette réponse. | Question délimitée : « Quelle limite, tenant aux droits des associés entre eux, s'impose dans tous les cas à une réduction de capital d'une société anonyme (SA) ou d'une SARL ? ». Réponse inchangée (égalité des actionnaires ou des associés). | C. com., art. L. 225-204, L. 223-34 et L. 224-2 |
| k15 | La question visait la SARL et la SA, et la réponse disait que les associés décident « dans les quatre mois » s'il y a lieu à dissolution anticipée. C'est exact pour la SARL (art. L. 223-42). Dans la SA, en revanche, le texte oblige le conseil d'administration ou le directoire à **convoquer** l'assemblée générale extraordinaire dans les quatre mois ; il ne fixe pas de délai à la décision (art. L. 225-248, al. 1, vérifié). | Question limitée à la SARL : « Que doivent faire les associés d'une SARL dont les comptes approuvés font apparaître des capitaux propres inférieurs à la moitié du capital social ? ». Réponse inchangée. k16 et k17 traitent toujours la SA et la SARL ensemble. | C. com., art. L. 223-42 et L. 225-248 (recherche 2) |
| k23 | La question visait « les sociétés commerciales », mais la réponse décrit la procédure propre à la SA : l'approbation par l'assemblée générale extraordinaire de chaque société participante (art. L. 236-9). Dans la SARL, la fusion est décidée par les associés aux conditions de modification des statuts. | Question : « Quelles sont les étapes principales de la procédure de fusion de sociétés anonymes (SA) prévue par le Code de commerce ? ». Réponse inchangée. | C. com., art. L. 236-9, L. 236-10 et L. 236-23 (Règles essentielles#12) |
| k29 | Une seule puce réunissait deux cas de l'article 1844-7 : le 5° (justes motifs, à la demande d'un associé) et le 6° (réunion de toutes les parts en une seule main). La tournure faisait de la demande d'un associé une condition commune aux deux. Or, dans le second cas, la dissolution peut être demandée par **tout intéressé** (art. 1844-5, al. 1). | Deux puces distinctes : « la dissolution anticipée prononcée par le tribunal à la demande d'un associé pour justes motifs » ; « la dissolution anticipée prononcée par le tribunal en cas de réunion de toutes les parts en une seule main ». | C. civ., art. 1844-7, 5° et 6°, et 1844-5, al. 1 |
| k34 | « Inviter le conseil ou le directoire à délibérer » est inexact pour la SA à directoire. L'article L. 234-1 dit que le commissaire invite le président du conseil d'administration ou le directoire à **faire délibérer** le conseil d'administration ou le conseil de surveillance. Dans la forme dualiste, c'est le conseil de surveillance qui délibère, pas le directoire. | « inviter le président du conseil d'administration ou le directoire à faire délibérer le conseil d'administration ou de surveillance ». Les autres étapes sont inchangées. La réponse fait 70 mots. | C. com., art. L. 234-1, al. 2 (Règles essentielles#18) |

Les 29 autres cartes ont été contrôlées sans changement : k01, k03 à k09, k11 à k14, k16 à k22, k24 à k28, k30 à k33 et k35. En particulier :
- **k09** (commissaires aux apports désignés à l'unanimité des actionnaires ou, à défaut, en justice ; réduction de leur évaluation subordonnée à l'approbation expresse des apporteurs) est conforme à l'article L. 225-147 en vigueur (recherche 1).
- **k06** est à jour : la nullité de l'augmentation de capital de SARL décidée alors que le capital ancien n'est pas intégralement libéré figure toujours au dernier alinéa de l'article L. 223-7, rendu applicable par l'article L. 223-32 (recherche 3). Pour la SA, la carte n'affirme aucune nullité.
- **k15 et k16** : la seconde étape issue de la loi du 9 mars 2023, réduire le capital au plus jusqu'au seuil réglementaire, est correctement articulée avec la première, qui consiste à reconstituer les capitaux propres ou à réduire le capital.
- **k05** : le compte 1041 Primes d'émission subsiste dans la liste des comptes du PCG modifiée par le règlement ANC n° 2022-06.
- **k33** : l'article L. 821-53, issu de l'ordonnance n° 2023-1142, est bien le siège actuel de la certification.
- **k35** est conforme au régime issu de l'ordonnance n° 2025-229, applicable depuis le 1er octobre 2025 : prescription de deux ans (C. civ., art. 1844-14) et délai de trois mois propre aux décisions d'augmentation de capital (C. com., art. L. 225-149-4).
- **Doublons.** Aucun doublon n'a été trouvé, pour les raisons suivantes :
  - k26 et k27 opposent l'associé unique personne morale (TUP) à l'associé unique personne physique (liquidation), comme Points de vigilance#1 ;
  - k28 et k29 se partagent la liste de l'article 1844-7, découpage utile pour la mémorisation ;
  - k13 définit le coup d'accordéon ; k14 donne les conditions de l'arrêt Usinor ;
  - k06 porte sur la libération préalable du capital existant ; k07 sur les quotités minimales de libération.

## Recherches faites

3 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr.

1. Requête « article L. 225-147 code de commerce commissaires aux apports désignés à l'unanimité des actionnaires augmentation de capital ».
   - **Confirmé.** Selon la version en vigueur, un ou plusieurs commissaires aux apports sont désignés à l'unanimité des actionnaires ou, à défaut, par décision de justice. Ils apprécient sous leur responsabilité la valeur des apports en nature et les avantages particuliers. Si l'assemblée réduit l'évaluation, l'approbation expresse des apporteurs est requise ; à défaut, l'augmentation n'est pas réalisée.
   - Effet : k09 est exacte.
   - Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048539465
2. Requête « article L. 225-248 code de commerce capitaux propres inférieurs moitié capital convoquer assemblée générale extraordinaire quatre mois réduire son capital ».
   - **Confirmé.** Dans la SA, le conseil d'administration ou le directoire « est tenu dans les quatre mois qui suivent l'approbation des comptes ayant fait apparaître cette perte, de convoquer l'assemblée générale extraordinaire à l'effet de décider s'il y a lieu à dissolution anticipée ». À défaut de dissolution, la société doit, au plus tard à la clôture du deuxième exercice suivant, reconstituer ses capitaux propres à hauteur de la moitié au moins du capital ou, sous réserve de l'article L. 224-2, réduire son capital. Dans la SARL (art. L. 223-42), ce sont les associés qui décident dans les quatre mois.
   - Effet : k15 a été limitée à la SARL ; k16 et k17 sont exactes.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000047292156 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000047292166
3. Requête « article L. 223-7 code de commerce capital social intégralement libéré avant toute souscription de nouvelles parts sociales à libérer en numéraire à peine de nullité ».
   - **Confirmé.** Le dernier alinéa de l'article L. 223-7 prévoit toujours que le capital social doit être intégralement libéré avant toute souscription de nouvelles parts sociales à libérer en numéraire, « à peine de nullité de l'opération ». L'article L. 223-32 le rend applicable aux augmentations de capital.
   - Effet : k06 est exacte.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006222923 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000025559543

Aucune recherche n'a été faite pour les corrections de k02, k10, k23, k29 et k34. Elles reposent sur des textes stables et connus : C. com., art. L. 225-129-2, L. 224-2, L. 236-9 et L. 234-1 ; C. civ., art. 1844-5 et 1844-7. Elles délimitent la question ou corrigent une tournure, sans rien ajouter au verso qui sorte des items de base.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#9** (capitaux propres inférieurs à la moitié du capital), avec **Chiffres et seuils#2** (« consultation des associés dans les quatre mois »). La règle « dans les quatre mois …, les associés décident s'il y a lieu à dissolution anticipée » est celle de la SARL (art. L. 223-42). Dans la SA, l'article L. 225-248, alinéa 1, oblige le conseil d'administration ou le directoire à **convoquer l'assemblée générale extraordinaire** dans les quatre mois de l'approbation des comptes. L'item pourrait aussi préciser que, dans la SA, la réduction de capital se fait « sous réserve de l'article L. 224-2 » (capital minimal).
2. **Règles essentielles#18** (procédure d'alerte dans la SA). « Il invite le conseil ou le directoire à délibérer » est à remplacer par la formule de l'article L. 234-1 : le commissaire invite le président du conseil d'administration ou le directoire à faire délibérer le conseil d'administration ou le conseil de surveillance sur les faits relevés.
3. **Règles essentielles#14** (causes de dissolution). La formule « dissolution anticipée prononcée par le tribunal à la demande d'un associé pour justes motifs, ou dans le cas de réunion de toutes les parts en une seule main » réunit deux cas distincts de l'article 1844-7 (5° et 6°). Dans le second, la dissolution peut être demandée par tout intéressé (art. 1844-5, al. 1). Il vaut mieux les séparer.
4. **Règles essentielles#12** (procédure de fusion). L'approbation « par l'assemblée générale extraordinaire de chaque société participante » est la règle de la SA (art. L. 236-9). L'item gagnerait à porter la mention « (SA) » ou à rappeler que, dans la SARL, la fusion est décidée par les associés aux conditions de modification des statuts.

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
