# Cartes de notions : ue10-06 (Capitaux propres : constitution, augmentation, réduction, affectation)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-06.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle n'a fait aucune recherche web.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, Code civil, CGI et BOFiP, PCG modifié par les règlements ANC n° 2018-01, 2018-02, 2022-06 et 2024-07) ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a fait 3 recherches WebSearch restreintes à anc.gouv.fr (voir « Recherches »).
4. **Validation.** `node validate.js data/ue10/ue10-06.cartes.json` : ✓ (34 cartes, 6 déf.).

## Bilan

- **Nombre de cartes : 34.** Il y en avait 35 au départ. Une carte a été supprimée (k25), sans renumérotation : l'identifiant k25 reste vide.
- **Répartition : 6 cartes `def` et 28 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 5 items de « Définitions » ont chacun au moins une carte.
  - 18 des 19 « Règles essentielles » sont dans la base d'au moins une carte. Règles essentielles#2 (augmentation de capital en numéraire dans la SA) n'est la base d'aucune carte, mais tout son contenu est porté par k11 (Chiffres et seuils#0, Points de vigilance#0) et k12 (Points de vigilance#1).
  - Les 6 « Points de vigilance » sont tous couverts. Points de vigilance#2 l'est désormais par k24, après la fusion de k25.
  - Dans « Chiffres et seuils », les items #0, #1 et #2 sont couverts (k11, k05, k21).
  - Dans « Ce qui a changé récemment », les items #0, #1, #3 et #4 sont couverts (k22, k17, k34, k03).
- **Items de fiche sans carte :**
  - Chiffres et seuils#3 (PFU et seuils de dispense, « millésimé 2025 ») ;
  - Chiffres et seuils#4 (taux limite des intérêts de comptes courants, « millésimé 2026 ») ;
  - Ce qui a changé récemment#2 (prélèvements sociaux 2026, « millésimé 2026 »).

  Ce sont des items millésimés : le contrat exclut qu'ils donnent une carte.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres présents sont stables et font partie d'une règle : fractions de libération (1/5, 1/2, 1/4), 30 000 € (D. 223-6-1, fixé depuis 2010), 1 % du total du bilan (décret n° 2023-657), 5 % et 10 % de la réserve légale, délais légaux (cinq ans, quatre mois, neuf mois, trois mois). Les dates citées (ordonnance n° 2025-229, loi n° 2023-171, loi n° 2026-103, règlements ANC n° 2018-01 et 2024-07) sont des dates de textes ou d'entrée en vigueur.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la première relecture est tronqué après k16. Les lignes marquées (*) ont été reconstituées d'après l'historique git du fichier (commit 609a3b1 par rapport au commit f3776ee).

| cible | problème | correction |
|---|---|---|
| ue10-06-k03 | La réponse ne faisait que reformuler la question (« distinctes des dettes ») et n'apportait rien de plus que ce qu'elle disait déjà. | Ajout d'un élément porté par « Ce qui a changé récemment#4 » : la version commentée du règlement précise que le compte 109 est débité en contrepartie de la subdivision « capital souscrit non appelé » du compte 101. |
| ue10-06-k06 | La réponse oubliait que les fondateurs d'une SA peuvent se dispenser de commissaire aux apports (L. 225-8-1, Règles essentielles#5). Cette dispense n'apparaissait sur aucune carte. | Ajout des deux cas de dispense prévus par la fiche : valeurs mobilières ou instruments du marché monétaire évalués au cours moyen pondéré des trois mois précédant l'apport, ou actifs évalués à la juste valeur par un commissaire aux apports dans les six mois. Le premier mot devient « Apprécier » pour rester sous 70 mots. |
| ue10-06-k11 | La réponse étendait à la SARL la libération de la totalité de la prime d'émission, alors que « Chiffres et seuils#0 » réserve cette règle à la SA. De plus, le délai de cinq ans n'était porté par la base que pour la SARL (Règles essentielles#3). | Nouvelle formulation : « le quart au moins du nominal dans la SA comme dans la SARL et, dans la SA, la totalité de la prime d'émission », avec à la constitution « un cinquième des apports en SARL et la moitié du nominal en SA ». La base devient [Points de vigilance#0, Chiffres et seuils#0], qui porte tous les éléments. `src` et `url` ne changent pas. |
| ue10-06-k12 | La carte ne couvrait que la SA. La règle propre à la SARL (capital intégralement libéré avant toute souscription de nouvelles parts en numéraire, Règles essentielles#3) n'était plus couverte après la modification de k11. | La question vise désormais la SA ou la SARL (« quelle condition commune subordonne l'émission de titres nouveaux à libérer en numéraire et la déduction fiscale des intérêts… »). La réponse cite les deux formes. La base devient [Points de vigilance#1, Règles essentielles#3]. Le contenu de Règles essentielles#2 reste couvert par Points de vigilance#1 (k12) et Chiffres et seuils#0 (k11). |
| ue10-06-k14 | La réponse oubliait une règle importante de la base (Règles essentielles#6) qu'aucune autre carte ne couvrait : si l'assemblée réduit l'évaluation, l'approbation expresse des apporteurs est requise, sinon l'augmentation n'est pas réalisée. | Ajout de cette condition et réorganisation : libération intégrale et compte 1043 d'abord, puis désignation du commissaire aux apports et approbation des apporteurs. |
| ue10-06-k16 | La question laissait croire que les traitements admis dataient du règlement ANC n° 2018-01, alors que ce règlement n'a changé que la qualification (« méthode préférentielle »). | Nouvelle question : « Selon l'article 212-9 du PCG, quels traitements comptables sont admis pour les frais d'augmentation de capital d'une société ? ». La réponse précise : « Depuis le règlement ANC n° 2018-01, l'imputation sur la prime n'est plus qualifiée de « méthode préférentielle » ». |
| ue10-06-k20 (*) | « Créanciers antérieurs » ne reprenait pas la précision de la fiche (Règles essentielles#10). | « Créanciers dont la créance est antérieure au dépôt au greffe du procès-verbal ». |
| ue10-06-k22 (*) | La question (« dans le délai de deux exercices ») ne disait pas quels capitaux propres devaient être reconstitués. | « … n'ayant pas reconstitué dans le délai légal ses capitaux propres inférieurs à la moitié du capital ? ». |
| ue10-06-k25 (*) | La question ne nommait pas la forme sociale. | « … pour doter la réserve légale d'une SARL ou d'une société par actions dont le report à nouveau est débiteur ? ». |
| ue10-06-k27 (*) | « L'assemblée générale » sans contexte. | « L'assemblée générale d'une société ». |
| ue10-06-k32 (*) | Question tournée en négatif (« Que ne couvre pas la dispense… ? »). | « Quels prélèvements restent retenus à la source sur les dividendes d'une personne physique dispensée du prélèvement forfaitaire non libératoire ? ». La réponse commence par « Les prélèvements sociaux ». |

L'historique montre aussi une retouche de k15 : la phrase « Les réserves, le report à nouveau ou les primes sont simplement virés au capital (compte 1013) » devient « Comptablement, le compte 106 (ou 104, 110) est débité par le crédit du compte 1013 ». Elle n'apparaît pas dans la partie transmise du résultat. La première relecture n'a fait ni suppression ni ajout. Elle a porté la date `maj` au 2026-10-16.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-06-k03 | La question datait l'application du règlement (« exercices ouverts à compter du 1er janvier 2026 »), alors que le résultat de recherche sur anc.gouv.fr indique les exercices ouverts à compter du 1er janvier 2025. « Deviennent une rubrique » exagérait aussi la nouveauté : la rubrique « autres fonds propres » est déjà prévue par l'article R. 123-190 du Code de commerce, et le règlement en « affirme le statut » comme rubrique à part entière. Enfin, la phrase sur le compte 109, ajoutée à la première relecture, était sans rapport avec la question : c'est l'écriture ordinaire de souscription. | Question sans date : « Quelle rubrique du bilan le règlement ANC n° 2024-07 consacre-t-il comme rubrique à part entière, distincte des dettes ? ». Réponse : les « autres fonds propres », distincts des dettes, qui n'entrent pas non plus dans les capitaux propres définis par le PCG et sont exclus de la situation nette. La base devient [Ce qui a changé récemment#4, Définitions#0]. `src` et `url` ne changent pas. | Règlement ANC n° 2024-07 (page ANC, texte publié au JO, version commentée) ; Définitions#0 |
| ue10-06-k13 | « Quelle procédure une SA peut-elle engager… ? » admettait une autre réponse juste : l'action en paiement de droit commun contre l'actionnaire, que la société conserve à côté de la vente forcée. | La question délimite son champ : « Quelle procédure spécifique le Code de commerce ouvre-t-il à une SA contre l'actionnaire qui ne paie pas les sommes appelées sur ses actions ? ». La réponse est inchangée. | C. com., art. L. 228-27 et L. 228-28 (Règles essentielles#7) |
| ue10-06-k16 | « Quels traitements comptables sont admis » appelait, chez un correcteur du DCG, trois réponses : charges, frais d'établissement, imputation sur la prime. C'est la solution de l'exercice 12 du chapitre. Or le verso n'en donnait que deux, et les charges seulement « en cas d'insuffisance de la prime ». L'article 212-9 dit que ces frais « peuvent » être inscrits en frais d'établissement ou imputés : ce sont des options, et la comptabilisation en charges reste possible. | La question porte sur les options prévues par le texte : « Selon l'article 212-9 du PCG, quelles options s'offrent à une société pour ses frais d'augmentation de capital, plutôt que de les comptabiliser en charges ? ». Réponse : les inscrire en frais d'établissement ou les imputer sur les primes d'émission et de fusion ; en cas d'insuffisance de la prime, ils sont comptabilisés en charges. Le piège de la « méthode préférentielle » est conservé. | PCG, art. 212-9 (recherche 3) ; règlement ANC n° 2018-01 (Points de vigilance#5, Règles essentielles#18) |
| ue10-06-k17 | « Trois mois » était présenté comme le délai de toute action en nullité d'une augmentation de capital. Or l'article L. 225-149-4 réserve d'autres cas : la citation de la fiche commence par « dans tous les autres cas ». | Question : « … dans quel délai se prescrit en règle générale… ». Réponse : « Trois mois à compter de la date à laquelle la décision contestée a été prise (C. com., art. L. 225-149-4), sous réserve des cas particuliers que ce texte prévoit ». La phrase sur la prescription de deux ans est inchangée. | C. com., art. L. 225-149-4 ; ordonnance n° 2025-229 (Ce qui a changé récemment#1) |
| ue10-06-k20 | Doublon partiel avec k19 : les deux cartes donnaient au verso la même liste des titulaires du droit d'opposition (représentant de la masse, créanciers antérieurs au dépôt du procès-verbal). | Le verso de k20 porte sur la distinction et sur l'issue de l'opposition. Seule la réduction non motivée par des pertes ouvre le droit d'opposition, contrairement à la réduction motivée par des pertes (débit 1013, crédit 119). Le juge rejette l'opposition ou ordonne le remboursement ou des garanties. Les titulaires et le délai restent sur k19. | C. com., art. L. 225-205, L. 223-34 (Règles essentielles#10) |
| ue10-06-k21 | « Dans les quatre mois…, les associés décident s'il y a lieu à dissolution anticipée » n'est exact que dans la SARL (L. 223-42). Dans la SA (L. 225-248), c'est la convocation de l'assemblée générale extraordinaire par le conseil d'administration ou le directoire qui doit intervenir dans les quatre mois. La question visait les deux formes. | Début de la réponse : « Consulter les associés sur une éventuelle dissolution anticipée, dans les quatre mois suivant l'approbation des comptes ayant fait apparaître la perte », formulation exacte pour les deux formes et reprise de Chiffres et seuils#2 (« consultation des associés dans les 4 mois »). La base devient [Règles essentielles#11, Chiffres et seuils#2]. | C. com., art. L. 225-248 et L. 223-42 |
| ue10-06-k24 | La carte faisait doublon avec k25 : le verso de k24 (bénéfice « diminué le cas échéant des pertes antérieures », plafond du dixième du capital) contenait déjà toute la réponse de k25. | Fusion : k24 précise « (report à nouveau débiteur) » et ajoute « il faut contrôler le plafond restant avant de doter 5 % en totalité ». La base devient [Règles essentielles#12, Points de vigilance#2]. | C. com., art. L. 232-10 |
| ue10-06-k25 (supprimée) | Doublon de k24 (voir ci-dessus). | Supprimée. Points de vigilance#2 reste couvert par k24. | C. com., art. L. 232-10 (Points de vigilance#2) |
| ue10-06-k31 | L'intitulé « 442 État – impôts et taxes recouvrables sur des tiers » est périmé. Dans les plans de comptes 2025 et 2026, le compte 442 regroupe les impôts recouvrés pour le compte de l'État, avec les subdivisions 4421 (prélèvement à la source de l'impôt sur le revenu), 4422 (prélèvements forfaitaires non libératoires) et 4423 (retenues et prélèvements sur les distributions), issues du règlement ANC n° 2018-02. | Intitulé retiré : « Au crédit du compte 442, jusqu'à son versement au Trésor. » La suite est inchangée. Aucune subdivision n'est citée, car la fiche n'en cite pas. | Plan de comptes 2026 et PCG 2025 (recherche 2) ; Règles essentielles#16 |

Les 25 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- définition des capitaux propres et de la situation nette ; comptes 1011, 1012, 1013 et 109 ;
- libération à la constitution : C. com., art. L. 223-7 et L. 225-3 ;
- commissaire aux apports :
  - SARL : L. 223-9 et D. 223-6-1 (30 000 €, moitié du capital, responsabilité de cinq ans à l'égard des tiers) ;
  - SA : L. 225-8 et L. 225-8-1 ;
- frais de constitution : charges comme méthode de référence (PCG, art. 212-9, confirmé par la recherche 3) ;
- prime d'émission et DPS : L. 225-132, L. 225-135 et L. 225-144 ;
- augmentation de capital :
  - libération du quart et de la totalité de la prime : L. 225-144 et L. 223-32 ;
  - libération préalable du capital : L. 225-131 et L. 223-7 ;
  - apport en nature : L. 225-147 ;
  - incorporation : L. 225-130 et L. 223-30, avec unanimité pour la majoration du nominal hors incorporation ;
- actionnaire défaillant : L. 228-27 et L. 228-28 ;
- réduction du capital : L. 225-204 (égalité des actionnaires), L. 225-205, R. 225-152 (vingt jours) et R. 223-35 (un mois) ;
- capitaux propres inférieurs à la moitié du capital, réduction au seuil réglementaire (loi n° 2023-171, décret n° 2023-657) ;
- affectation du résultat :
  - bénéfice distribuable, dividende fictif, postes de réserve, protection du capital : L. 232-11 et L. 232-12 ;
  - acomptes : L. 232-12 et R. 232-17 ;
  - délai de neuf mois : L. 232-13 ;
- fiscalité :
  - prélèvement de l'article 117 quater et prélèvements sociaux ;
  - déduction des intérêts de comptes courants (CGI, art. 39, 1-3°) et extension de l'article 212 par la loi n° 2026-103.

## Recherches

Trois recherches WebSearch ont été faites, toutes restreintes à `anc.gouv.fr` :

1. **« règlement ANC 2024-07 autres fonds propres dettes rubrique bilan ».** Le règlement existe. Il est daté du 6 décembre 2024 et sa version commentée est en ligne. Il affirme le statut de la rubrique « autres fonds propres », déjà prévue par l'article R. 123-190 du Code de commerce, comme rubrique à part entière du passif. Cette rubrique est placée entre les capitaux propres et les provisions. Elle regroupe les fonds non remboursables, les avances conditionnées et les droits du concédant. La date d'application ne concorde pas : le résultat indique les exercices ouverts à compter du 1er janvier 2025, la fiche le 1er janvier 2026. Ce point a conduit à corriger k03. Sources : [page ANC du règlement](https://www.anc.gouv.fr/reglement-anc-ndeg2024-07), [texte publié au JO](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2024/R2024-07/REGLT_2024_07_JO.pdf), [version commentée](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2024/R2024-07/REGLT_2024_07_version-commentee-def.pdf).
2. **« plan de comptes 442 … 4422 prélèvements forfaitaires non libératoires ».** Le résultat confirme que, dans les plans de comptes 2025 et 2026, le compte 442 regroupe les impôts recouvrés pour le compte de l'État. Ses subdivisions sont 4421, 4422 (prélèvements forfaitaires non libératoires) et 4423 (retenues et prélèvements sur les distributions), introduites par le règlement ANC n° 2018-02. L'intitulé « État – impôts et taxes recouvrables sur des tiers » est donc périmé, ce qui a conduit à corriger k31. Sources : [plan de comptes 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/Plan-de-comptes-2026.pdf), [plan de comptes PCG 2025](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/Plan-de-comptes-PCG-2025.pdf), [note de présentation du règlement n° 2018-02](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2018/Reglt_2018_02/Reglt_2018_02_Note-de-presentation.pdf).
3. **« PCG article 212-9 frais d'augmentation de capital … ».** Le résultat confirme la rédaction de la fiche. Les frais d'augmentation de capital peuvent être inscrits en frais d'établissement ou imputés sur les primes d'émission et de fusion ; en cas d'insuffisance, ils sont comptabilisés en charges. Pour les frais de constitution, la méthode de référence est la comptabilisation en charges. L'édition 2014 qualifiait l'imputation sur les primes de « méthode préférentielle », ce que les versions récentes ne font plus. Ce point a conduit à corriger la question de k16. Sources : [PCG au 1er janvier 2025](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/PCG--1er-janvier-2025.pdf), [recueil au 1er janvier 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/recueil/2026/Recueil-PCG-Janvier-2026.pdf), [règlement ANC n° 2014-03, version initiale](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2014/Reglt2014-03/Reglt%202014-03_Plan%20comptable%20general.pdf).

Aucune autre recherche n'a été faite. Les autres points (Code de commerce, CGI, ordonnance n° 2025-229, loi n° 2026-103) avaient déjà été établis par recherche lors de la relecture de la fiche (`rapports/ue10-06.md`, 50 recherches du 14 octobre 2026). Ils n'appelaient pas de doute réel. Le seul doute restant porte sur les cas réservés par l'article L. 225-149-4. Il a été neutralisé en délimitant la question de k17 à la règle générale.

## Points à reprendre dans la fiche

1. **Ce qui a changé récemment#4, et l'entrée « textes » du PCG.**
   - Date d'application : la fiche indique le 1er janvier 2026, le résultat de recherche sur anc.gouv.fr le 1er janvier 2025. Il faut vérifier sur le texte publié au JO (REGLT_2024_07_JO.pdf) et sur l'arrêté d'homologation, dont la date (26 décembre 2025 dans la fiche) doit être confirmée.
   - « Qui deviennent une rubrique à part entière du bilan » : il faudrait écrire que le règlement affirme le statut de la rubrique « autres fonds propres », déjà prévue par l'article R. 123-190, et en préciser la composition (fonds non remboursables, avances conditionnées, droits du concédant).
2. **Règles essentielles#16.** L'intitulé « 442 État – impôts et taxes recouvrables sur des tiers » est périmé. Le compte 442 regroupe les impôts recouvrés pour le compte de l'État, avec les subdivisions 4421, 4422 (prélèvements forfaitaires non libératoires) et 4423 (retenues et prélèvements sur les distributions), issues du règlement ANC n° 2018-02. Il faut reprendre l'intitulé exact sur le plan de comptes 2026. Hors fiche, le même intitulé périmé figure dans `data/pcg/classe4.json` (compte 442, dont l'explication cite aussi les anciennes subdivisions 4424 et 4425).
3. **Règles essentielles#11 (et Chiffres et seuils#2).** « Dans les quatre mois…, les associés décident s'il y a lieu à dissolution anticipée » ne vaut que pour la SARL (L. 223-42). Dans la SA (L. 225-248), le conseil d'administration ou le directoire est tenu de convoquer l'AGE dans les quatre mois qui suivent l'approbation des comptes. Il faudrait distinguer les deux formes, citation de L. 225-248 à l'appui.
4. **Ce qui a changé récemment#1.** La citation de L. 225-149-4 commence par « dans tous les autres cas » : les cas réservés par le texte ne sont pas décrits, ce que `POINTS-OUVERTS.md` signale déjà. Il faudrait les rechercher et les ajouter.
5. **Règles essentielles#18 et Points de vigilance#5 (précision).** La fiche reproduit fidèlement l'article 212-9, mais elle gagnerait à dire, comme l'exercice 12 du chapitre, que la comptabilisation directe en charges des frais d'augmentation de capital reste possible (« peuvent être inscrits… ou imputés »). Un lecteur pourrait sinon croire que les charges ne sont admises qu'en cas d'insuffisance de la prime.

## Classement des exercices

Le classement automatique des 19 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 18 | oui |
| `calcul` | 1 | non |
| `chiffre` | 0 | — |

Les classeurs n'ont relevé aucun désaccord. Les 18 exercices de nature `notion` entrent dans les révisions espacées, avec les 34 cartes ci-dessus et les comptes du plan comptable. L'exercice de nature `calcul` reste dans le chapitre, mais il n'est pas proposé en révision.
