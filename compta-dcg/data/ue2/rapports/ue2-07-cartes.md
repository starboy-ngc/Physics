# Cartes de notions : ue2-07 (Le commerçant, le fonds de commerce et le bail commercial)

16 octobre 2026. Fichier : `data/ue2/ue2-07.cartes.json`. Fiche de référence : `data/ue2/ue2-07.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Deux passes successives ont confronté les 35 cartes au texte de leurs items de base, sans recherche web. La première a corrigé 9 cartes (k01, k04, k07, k10, k14, k28, k32, k33, k34). La seconde en a corrigé 8 (k28, k30, k08, k18, k24, k27, k33, k01), surtout pour intégrer des règles de la fiche restées sans carte. Aucune suppression ni aucun ajout : le jeu était au plafond de 35 cartes.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 16 octobre 2026 : Code de commerce (livre I, titre IV, et statut de l'entrepreneur individuel), Code civil, CGI. Il a vérifié que chaque question n'appelle qu'une seule réponse, celle qu'attendrait un correcteur du DCG, et il a cherché les doublons et les cartes sans intérêt. Bilan : 6 cartes corrigées (k07, k09, k18, k25, k31, k34), 1 fusion (k15 fondue dans k10, qui est réécrite), 1 suppression (k15) et 1 ajout (k36).
4. **Recherches.** 3 recherches WebSearch sur les 3 autorisées, toutes limitées à legifrance.gouv.fr (voir plus bas) : deux sur la loi n° 2026-403 du 26 mai 2026 et l'article L. 145-40, une sur l'ancienne rédaction de l'article L. 141-6.

`node validate.js data/ue2/ue2-07.cartes.json` : ✓ (35 cartes, 9 déf.).

## Bilan

- **35 cartes**, soit le maximum prévu par le contrat : 9 de définition (`def`) et 26 de compréhension (`comp`). Les identifiants vont de k01 à k36 ; **k15 est supprimée** et laisse un trou, qui ne sera pas réutilisé.
- Chaque item des sections « Définitions » (#0 à #6) et « Règles essentielles » (#0 à #17) a au moins une carte. Tous les items de « Ce qui a changé récemment » ont une carte de compréhension, ainsi que les « Points de vigilance » #1 à #5.
- **Items de la fiche sans carte :**
  - **Chiffres et seuils#0** : droits d'enregistrement de 2026. L'item est millésimé et ne donne donc pas de carte.
  - **Chiffres et seuils#4** : durées du brevet et de la marque. Ce sont des chiffres accessoires au chapitre ; l'exercice #26 les teste déjà.
  - **Points de vigilance#0** : périmètre des programmes 2019 et 2025. Il n'y a rien à mémoriser sous forme de carte.
  - Les items Chiffres et seuils #1, #2 et #3 ne sont cités qu'en second item de base (k31, k18, k08). Leurs délais stables sont repris dans les cartes de règle.
- **Contenus couverts en partie** (le plafond de 35 cartes impose une suppression pour tout ajout) :
  - l'interdiction de conclure un nouveau bail dérogatoire pour le même fonds dans les mêmes locaux (Règles essentielles#13) ;
  - la saisie du patrimoine professionnel par les créanciers personnels, dans la limite du dernier bénéfice (Points de vigilance#4) ;
  - la clause qui limite la variation de l'indice (art. L. 145-38-1, Ce qui a changé récemment#0) ;
  - la déclaration des créanciers non inscrits en cas d'apport du fonds (Règles essentielles#9) ;
  - le plafond de 10 % sur la hausse annuelle du loyer renouvelé déplafonné (Règles essentielles#15).

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | k01 | Seconde phrase maladroite, éloignée de la fiche (« Les actes de commerce sont notamment ceux que l'article L. 110-1 répute tels »). | Reformulée selon Définitions#0 : « L'article L. 110-1 répute notamment actes de commerce tout achat de biens meubles pour les revendre. » |
| 1 | k04 | « Quelle est la situation… » était trop vague : on pouvait répondre juste en parlant de sanctions. | Question délimitée : « Au regard de la qualité de commerçant, quelle est la situation d'une personne physique non immatriculée au RCS dans les quinze jours du début de son activité ? » |
| 1 | k07 | L'obligation bancaire de Règles essentielles#2 n'était couverte par aucune carte. | Question sur les obligations « comptables et bancaires » ; réponse complétée par l'obligation d'ouvrir un compte dans un établissement de crédit ou un bureau de chèques postaux. |
| 1 | k10 | La réponse laissait croire que le mobilier, le matériel, les brevets, les marques… entrent d'office dans le nantissement, sans la condition de désignation expresse et précise. | Question : « quels éléments du fonds de commerce peuvent être compris dans son nantissement ? » ; ajout de la condition de désignation et du caractère limitatif de la liste de L. 142-2. |
| 1 | k14 | « Solidaire du cédant » allait plus loin que la fiche (« peut être tenu solidairement »). | « Qui peut être tenu solidairement avec le cédant au paiement de l'impôt sur le revenu dû au titre des bénéfices de l'exploitation, dans la limite du prix du fonds ». |
| 1 | k28 | Congé « avant le terme des neuf ans » alors que neuf ans est une durée minimale. | « Avant le terme du bail ». |
| 1 | k32 | « Le locataire ne peut être obligé de quitter les lieux avant de l'avoir reçue » généralisait la règle. | « Le locataire qui peut y prétendre ne peut être obligé de quitter les lieux avant de l'avoir reçue ». |
| 1 | k33 | La forme de la notification au bailleur manquait. | Ajout de « par acte extrajudiciaire ou lettre recommandée avec avis de réception » ; fin reformulée (« suppose en revanche d'y être autorisé »). |
| 1 | k34 | Le paiement mensuel était ouvert à « tout preneur », alors que la fiche le réserve au preneur de locaux à usage commercial ou artisanal. | « Le preneur de locaux à usage commercial ou artisanal peut aussi obtenir de droit, sur sa demande et s'il n'a pas d'arriéré, le paiement mensuel du loyer. » |
| 2 | k28 | La durée minimale de neuf ans (Règles essentielles#12) n'était couverte par aucune carte. | Question : « Quelle durée minimale le Code de commerce impose-t-il au bail commercial, et quand le preneur peut-il donner congé ? » ; réponse ouverte par « Neuf ans ». |
| 2 | k30 | L'effet du déplafonnement (hausse limitée à 10 % par an) manquait : la hausse semblait sans limite. | Ajout de « l'augmentation est alors limitée, pour une année, à 10 % du loyer acquitté l'année précédente ». |
| 2 | k08 | La preuve par tous moyens des actes de commerce (Règles essentielles#3) n'avait pas de carte ; une parenthèse répétait `src`. | Ajout de la règle de preuve ; parenthèse retirée. |
| 2 | k18 | L'exigibilité immédiate des dettes à la fin de la location-gérance (Règles essentielles#8) n'avait pas de carte. | Règle ajoutée ; délai de publication intégré à la première phrase. |
| 2 | k24 | La dénomination « EI » (Règles essentielles#11) n'était couverte nulle part. | Phrase ajoutée sur la dénomination ; parenthèse sur le décret retirée. |
| 2 | k27 | La question énonçait elle-même les deux clauses visées ; la réponse la répétait. | Question limitée à la clause qui fait échec au droit au renouvellement ; la clause interdisant la cession du bail à l'acquéreur du fonds passe au verso. |
| 2 | k33 | « Il suffit au locataire de faire connaître son intention » ajoutait une idée absente de la fiche. | « Le locataire peut adjoindre… en faisant connaître son intention au bailleur… ». |
| 2 | k01 | Les cautionnements de dettes commerciales, actes de commerce depuis le 1er janvier 2022 (Ce qui a changé récemment#3), n'avaient pas de carte. | Lettres de change et cautionnements de dettes commerciales ajoutés ; « Ce qui a changé récemment#3 » en second item de base. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k34 | « Quelles règles encadrent le dépôt de garantie d'un bail commercial ? » appliquait à tout bail commercial le plafond d'un trimestre de loyer et l'absence d'intérêts. Le nouvel alinéa de l'article L. 145-40 ne vise que le preneur d'un local mentionné à l'article L. 145-32-1 (commerce de détail ou de gros, prestations de services à caractère commercial ou artisanal). Un bail de bureaux, par exemple, n'est pas visé. La réponse traitait en outre le paiement mensuel, que la question ne demandait pas. | Question : « Qu'a changé la loi du 26 mai 2026 pour le dépôt de garantie et le paiement du loyer du preneur d'un local à usage commercial ou artisanal ? ». Réponse : dépôt plafonné au loyer d'un trimestre et sans intérêt pour les baux conclus ou renouvelés depuis la promulgation, restitution dans les trois mois de la remise des clés, paiement mensuel de droit « y compris dans les baux en cours ». 70 mots. | Loi n° 2026-403 du 26 mai 2026, art. 62 ; C. com., art. L. 145-32-1 et L. 145-40 ; recherches n° 1 et 2 (Ce qui a changé récemment#0) |
| k10 + k15 | Doublon croisé. Le recto de k10 (« Outre l'enseigne, le nom commercial, le droit au bail, la clientèle et l'achalandage… ») donnait la réponse de k15, et le verso de k15 renvoyait aux éléments de k10. Les deux cartes énonçaient une seule règle : la liste limitative de l'article L. 142-2 et la condition de désignation. | **Fusion dans k10**, qui garde son identifiant et son type `def`. Question : « Quels éléments du fonds de commerce son nantissement comprend-il, selon que l'acte constitutif les désigne ou non de façon expresse et précise ? ». Réponse : à défaut de désignation, les quatre éléments ; s'ils sont désignés, les autres éléments de L. 142-2 ; marchandises exclues. Base : Définitions#3 et Règles essentielles#7. **k15 supprimée.** | C. com., art. L. 142-2 (Définitions#3, Règles essentielles#7) |
| k36 (ajout) | La place libérée par k15 permet de couvrir une condition centrale du renouvellement, absente des cartes (Règles essentielles#16) : qui peut invoquer le droit au renouvellement. | Nouvelle carte `comp` : « Qui peut invoquer le droit au renouvellement d'un bail commercial ? » ; réponse : seul le propriétaire du fonds qui est exploité dans les lieux. Le bailleur qui refuse doit en principe payer au locataire évincé une indemnité d'éviction égale au préjudice causé. | C. com., art. L. 145-8 et L. 145-14 (Règles essentielles#16) |
| k25 | « Par quel moyen » l'entrepreneur individuel peut-il écarter la séparation au profit d'un créancier ? Une autre réponse juste était possible : l'article L. 526-22 réserve, à côté de la renonciation, les sûretés conventionnelles qu'il consent. | Question : « Par quel acte unilatéral un entrepreneur individuel peut-il écarter, au profit d'un créancier, la séparation de ses patrimoines personnel et professionnel ? ». Réponse inchangée (renonciation sur demande écrite, pour un engagement spécifique). | C. com., art. L. 526-22 et L. 526-25 (Points de vigilance#4) |
| k07 | « Quelles obligations… à toute personne physique ou morale ayant la qualité de commerçant » énonçait sans réserve l'article L. 123-12. Les articles L. 123-25 à L. 123-28 allègent ces obligations pour certains commerçants personnes physiques. Le micro-entrepreneur, par exemple, peut ne pas établir de comptes annuels. | Question ouverte par « En principe ». Réponse inchangée. | C. com., art. L. 123-12 et L. 123-25 à L. 123-28 (Règles essentielles#2) |
| k31 | « Comment le loyer d'un bail commercial renouvelé est-il plafonné ? » présentait le plafonnement comme général. Le loyer des locaux monovalents, des locaux à usage exclusif de bureaux et des terrains obéit à des règles propres (art. R. 145-9 à R. 145-11) et échappe au plafonnement. | Question ouverte par « En principe ». Réponse inchangée. | C. com., art. L. 145-34 et R. 145-9 à R. 145-11 (Règles essentielles#15) |
| k18 | « Jusqu'à quand le loueur… est-il solidairement responsable des dettes du locataire-gérant ? » visait toutes les dettes. La réponse ne vaut que pour la solidarité de l'article L. 144-7, limitée aux dettes nées de l'exploitation ; d'autres textes, fiscaux notamment, peuvent organiser une solidarité distincte. | Question : « Selon le Code de commerce, jusqu'à quand le loueur… est-il solidairement responsable des dettes d'exploitation du locataire-gérant ? ». Réponse inchangée. | C. com., art. L. 144-7 (Règles essentielles#8) |
| k09 | « Tribunaux des activités économiques expérimentés » se lit aussi « tribunaux chevronnés ». | « Mis en place à titre expérimental depuis le 1er janvier 2025 ». Réponse inchangée. | Loi n° 2023-1059 du 20 novembre 2023, art. 26 (Ce qui a changé récemment#1) |

Les 27 autres cartes ont été contrôlées sans changement : k01 à k06, k08, k11 à k14, k16, k17, k19 à k24, k26 à k30, k32, k33 et k35. En particulier :
- **k01** : l'article L. 110-1, 11°, range bien les cautionnements de dettes commerciales parmi les actes de commerce entre toutes personnes depuis le 1er janvier 2022.
- **k02** : l'autorisation du juge des tutelles ou du président du tribunal judiciaire suit l'article L. 121-2 dans sa rédaction en vigueur depuis le 1er janvier 2020.
- **k04** reprend exactement les articles L. 123-7 (présomption simple) et L. 123-8 (défaut d'immatriculation).
- **k11 et k12** se recoupent sur l'opposition des créanciers, mais la première porte sur la publicité de la vente et la seconde sur le risque d'un paiement prématuré. Elles sont gardées.
- **k13** : l'article L. 141-5 en vigueur depuis le 1er janvier 2023 fait de l'inscription une condition d'opposabilité du privilège, non plus d'existence. La recherche n° 3 confirme le rappel historique de Points de vigilance#3 : de 2015 à 2022, l'inscription devait être prise, à peine de nullité, dans les trente jours de l'acte.
- **k14** ne porte que sur le point de départ du délai (déclaration de l'article 201 du CGI). Les délais de quatre-vingt-dix et trente jours n'y figurent pas.
- **k16** : la nullité du nantissement non inscrit dans les trente jours suit l'article L. 142-4.
- **k19** : la loi n° 2019-744 a bien abrogé l'ancien article L. 141-1 et l'ancien article L. 144-3. La table du titre IV commence désormais à l'article L. 141-2, comme le montre la recherche n° 3.
- **k28, k29, k30 et k33** suivent la lettre des articles L. 145-4, L. 145-5, L. 145-38, L. 145-47 et L. 145-48.

## Recherches faites

3 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr.

1. Requête « loi n° 2026-403 du 26 mai 2026 simplification bail commercial dépôt de garantie L. 145-40 paiement mensuel loyer ».
   - **Confirmé.** L'article 62 de la loi n° 2026-403 rend le paiement mensuel de droit pour le preneur d'un local de commerce de détail ou de gros ou de prestations de services à caractère commercial ou artisanal (art. L. 145-32-1). Le preneur doit le demander et ne pas avoir d'arriéré, et la règle vaut pour les baux en cours à la promulgation. Il plafonne au loyer d'un trimestre les sommes versées à titre de garantie par le preneur d'un local mentionné à l'article L. 145-32-1, pour les baux conclus ou renouvelés à compter de la promulgation.
   - Effet : k34 délimitée au local à usage commercial ou artisanal ; Ce qui a changé récemment#0 et Chiffres et seuils#1 à reprendre.
   - Sources : https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000054131669 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054137998
2. Requête « Article L145-40 Code de commerce version en vigueur 2026 "remise des clés" trimestre sommes payées à titre de garantie L. 145-32-1 ».
   - **Confirmé.** L'article L. 145-40, modifié par la loi n° 2026-403 et en vigueur depuis le 28 mai 2026, limite le dépôt au loyer d'un trimestre pour les locaux de l'article L. 145-32-1. Ce dépôt ne porte pas intérêt. Le bailleur le restitue dans un délai maximal de trois mois à compter de la remise des clés, déduction faite des sommes restant dues. Pour les baux en cours, la règle de restitution s'applique lorsque les clés sont remises trois mois ou plus après la promulgation.
   - **Non confirmé dans le détail.** La rédaction exacte de la restitution (local de l'article L. 145-32-1 ou tout bail commercial) n'a pas été lue en entier. k34 ne l'énonce que pour les baux qu'elle vise, ce qui reste exact dans les deux lectures.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054142450 ; https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000005634379/LEGISCTA000006161267/
3. Requête « article L141-6 code de commerce version antérieure 2023 "L'inscription doit être prise, à peine de nullité, dans la quinzaine de la date de l'acte de vente" ».
   - **Confirmé.** La quinzaine valait du 21 septembre 2000 au 8 août 2015. La loi n° 2015-990 du 6 août 2015 l'a portée à trente jours, à peine de nullité, du 8 août 2015 au 1er janvier 2023, avant la rédaction issue de l'ordonnance n° 2021-1192. Points de vigilance#3 est donc exact.
   - Aucune carte modifiée.
   - Sources : https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000031010599&cidTexte=LEGITEXT000005634379&dateTexte=20150808 ; https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000005634379/LEGISCTA000006161258/

Aucune recherche n'a été faite pour k07, k09, k18, k25 et k31. Ces corrections ne font que délimiter la question (« en principe », « selon le Code de commerce », « acte unilatéral ») ou lever une ambiguïté de vocabulaire ; aucune réponse n'est modifiée.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Ce qui a changé récemment#0** (loi n° 2026-403), et par voie de conséquence **Chiffres et seuils#1**. « Le dépôt de garantie ne peut excéder le loyer d'un trimestre et ne porte pas intérêt » vaut pour le preneur d'un local mentionné à l'article L. 145-32-1 (commerce de détail ou de gros, prestations de services à caractère commercial ou artisanal), non pour tout bail commercial. Il faut le préciser. La restitution dans les trois mois de la remise des clés s'applique aussi aux baux en cours lorsque les clés sont remises trois mois ou plus après la promulgation (A du II de l'article 62). La rédaction « pour les baux conclus ou renouvelés depuis la promulgation… il est restitué » le laisse ignorer. Le paiement mensuel gagnerait à reprendre la définition légale du local (art. L. 145-32-1).
2. **Règles essentielles#2** (obligations comptables). L'item énonce l'article L. 123-12 sans réserve. Les articles L. 123-25 à L. 123-28 allègent ces obligations pour certains commerçants personnes physiques ; le micro-entrepreneur peut notamment ne pas établir de comptes annuels. Il faut ajouter « en principe » et renvoyer à ces dérogations, après lecture de leur rédaction consolidée.
3. **Règles essentielles#15** (loyer du bail renouvelé), précision facultative. Le loyer des terrains, des locaux monovalents et des locaux à usage exclusif de bureaux est fixé selon des règles propres (art. R. 145-9 à R. 145-11) et échappe au plafonnement. On peut l'indiquer.
4. **Lacune** (Définitions). La fiche ne définit pas le fonds de commerce lui-même : aucun texte n'en donne de définition, c'est un bien meuble incorporel et la clientèle en est l'élément essentiel. Elle ne le présente qu'à travers la liste de l'article L. 142-2. Le programme 2025 (3.1) porte pourtant sur la « notion » de fonds de commerce, et les exercices #11 et #13 testent ces points. Un item sourcé (C. com., art. L. 141-5 et L. 142-2 ; jurisprudence sur la clientèle) permettrait une carte de définition.

## Classement des exercices

Le chapitre compte 30 exercices. Le classement automatique porte sur les 26 QCM, QCM multiples et classements : **24 de nature `notion`**, **2 de nature `calcul`**, **aucun de nature `chiffre`**. Aucun désaccord n'a été relevé entre les classements.

- Les 2 QCM de nature `calcul` sont l'exercice #16 (date limite d'opposition des créanciers à décompter depuis la publication au BODACC) et l'exercice #20 (deux baux dérogatoires successifs de deux ans, dont il faut additionner les durées pour les comparer au maximum de trois ans).
- Les 4 exercices à saisie numérique (`calc`) sont des calculs par nature et restent hors révisions : #5 (année de prescription), #14 et #15 (droits d'enregistrement sur une cession de fonds) et #19 (loyer révisé selon l'ILC).
- Seuls les 24 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes.
