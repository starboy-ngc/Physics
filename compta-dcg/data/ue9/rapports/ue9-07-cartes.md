# Cartes de notions : ue9-07 (Clôture : régularisations et résultat)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-07.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte (`t` et `cite`) des items de la fiche : mêmes conditions, mêmes exceptions, même vocabulaire juridique. Elle n'a fait aucune recherche web. Elle a contrôlé 34 cartes, en a corrigé trois et en a ajouté une (k36).
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, CGI, BOFiP, PCG modifié par les règlements ANC n° 2022-06 et 2026-04) ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ou purement mécaniques.

   Elle a aussi vérifié l'absence de calcul, d'écriture chiffrée et de chiffre millésimé. Une seule recherche a été faite, limitée à anc.gouv.fr (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-07.cartes.json` : ✓ (35 cartes, 10 déf.).

Ce jeu en est à sa deuxième passe de relecture. La passe précédente avait notamment supprimé k13 (écriture des produits à recevoir, doublon de k04 et k12), ajouté k35 (mise en paiement des dividendes) et corrigé k26 (solde de l'IS au 15 mai, présenté comme une exception). Ces corrections sont conservées.

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. L'identifiant k13, supprimé lors de la passe précédente, reste vide (pas de renumérotation).
- **Répartition : 10 cartes `def` et 25 cartes `comp`.**
- **Couverture de la fiche.** Les 6 items de « Définitions » ont chacun au moins une carte. Les 17 « Règles essentielles » sont toutes couvertes sauf une (voir ci-dessous). Les 5 « Points de vigilance » ont chacun leur carte de compréhension. Dans « Ce qui a changé récemment », les items #0, #1, #2 et #4 ont leur carte.
- **Items de fiche sans carte :**
  - **Règles essentielles#3** (écriture des produits à recevoir). Son contenu est révisé par k04 (comptes 4181, 4482, 439, 467) et par k12 (TVA au compte 44587).
  - **Chiffres et seuils#0** (réserve légale : un vingtième, un dixième). C'est la même règle que Règles essentielles#13, déjà portée par k27.
  - **Chiffres et seuils#2 et #3** (taux de l'IS, plafond du taux réduit et son prorata). Ils sont millésimés et appellent un calcul : ils ne donnent pas de carte.
  - **Ce qui a changé récemment#3, #5 et #6** (règlement ANC n° 2026-04, contribution exceptionnelle des grandes entreprises, seuils des petites entreprises). Ils sont millésimés. La règle stable de l'article 515-1 du PCG reste portée par k23 et k24.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres qui restent sont stables et font partie d'une règle : un vingtième, un dixième, neuf mois, dates d'échéance de l'IS. Les années citées (2024, 2025, ordonnance de 2025, CE 2025) sont des dates d'entrée en vigueur, de plan de comptes ou de décision.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-07-k14 | La réponse disait « en contrepartie de la charge d'intérêts (661) ». La fiche (Règles essentielles#4) donne seulement « débit 661 / crédit 1648 » et ne nomme pas le compte 661 : l'intitulé venait d'ailleurs. | Remplacé par « par le débit du compte 661 », qui reprend exactement la fiche. |
| ue9-07-k23 | La question « quel taux applique-t-on pour comptabiliser l'impôt sur les bénéfices ? » admettait une autre bonne réponse, « 25 % », qui est un chiffre millésimé. Or la règle de Règles essentielles#11 porte sur la date à laquelle on retient le taux. | Nouvelle question : « Selon l'article 515-1 du PCG, à quelle date s'apprécie le taux à appliquer pour comptabiliser l'impôt sur les bénéfices de l'exercice ? ». Nouvelle réponse : « À la date de clôture : on applique le taux en vigueur à cette date. », suivie du rattachement à la rubrique « Impôts sur les bénéfices » de l'exercice au titre duquel l'entreprise est redevable. |
| ue9-07-k32 | La réponse parlait de « fixation par l'assemblée », alors que la fiche (Règles essentielles#16) écrit que les dividendes « sont déterminés par l'assemblée ». | Remplacé par « dividendes déterminés par l'assemblée après approbation des comptes et constatation de sommes distribuables », pour garder le même vocabulaire juridique que la fiche. |
| ue9-07-k36 (ajoutée) | Aucune carte ne couvrait l'item « Ce qui a changé récemment#2 » (recodification du plan de comptes). Il contient pourtant un piège important : le compte 4482 désignait les charges fiscales sur congés à payer dans le plan 2024 et désigne désormais « État – Produits à recevoir ». Les charges fiscales sur congés à payer sont maintenant en 44811. | Carte ajoutée sur le compte 44811 et le changement de sens du 4482. Elle complète aussi Règles essentielles#2 (comptes de charges à payer). Base : Ce qui a changé récemment#2 et Règles essentielles#2 ; `src` et `url` copiés depuis Ce qui a changé récemment#2. Avec elle, le jeu atteint 35 cartes, le maximum prévu. |

La première relecture n'a supprimé aucune carte.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-07-k19 | **Inexact.** La réponse disait que relèvent du résultat exceptionnel « seulement » les produits et charges directement liés à un événement majeur et inhabituel, avec une seule exception (écritures d'origine fiscale). Or le règlement n° 2022-06 classe aussi en résultat exceptionnel les corrections d'erreurs, sauf celles qui corrigent une écriture imputée directement sur les capitaux propres. La fiche n'en parle pas : la carte ne peut donc pas l'ajouter. | La question porte désormais sur le critère de principe : « Depuis le règlement ANC n° 2022-06, quel est en principe le critère de classement d'un produit ou d'une charge en résultat exceptionnel ? ». Réponse : « Un lien direct avec un événement majeur et inhabituel. Par exception, restent notamment en résultat exceptionnel les écritures d'origine purement fiscale (amortissements dérogatoires, provisions réglementées), en 687 / 787. » La carte ne prétend plus être exhaustive. Base, `src` et `url` sont inchangés. | Règlement ANC n° 2022-06 (texte et version commentée, anc.gouv.fr) |
| ue9-07-k33 | **Vrai seulement dans un cas non dit.** La question portait sur toute affectation du bénéfice, et la réponse (réserves, 457, 110) se présentait comme complète. Mais lorsqu'il existe un report à nouveau débiteur, le bénéfice sert aussi à l'apurer (crédit 119), puisque la base de la réserve légale et le bénéfice distribuable sont diminués des pertes antérieures. | La question délimite son champ : « Lors de l'affectation du bénéfice d'une société sans report à nouveau débiteur, entre quels comptes le solde du compte 120 est-il réparti ? ». La réponse, fidèle à Règles essentielles#15, est inchangée. | C. com., art. L. 232-10 et L. 232-11 ; plan de comptes 2026, comptes 110 et 119 |
| ue9-07-k36 | **Ambiguïté.** La parenthèse « (plan 2024 : 4482) » suivait l'intitulé de 4481 « État – Charges à payer ». On pouvait donc croire que 4482 était l'ancien numéro de 4481, alors que c'est l'ancien numéro de 44811. | Parenthèse déplacée juste après 44811 : « Sur le compte 44811 « Charges fiscales sur congés à payer » (plan 2024 : 4482), subdivision de 4481 « État – Charges à payer ». » Le reste de la carte est inchangé. | Ce qui a changé récemment#2 ; plans de comptes 2024 et 2026 (voir `data/pcg/RAPPORT-comptes-tiers.md`) |
| ue9-07-k14 | **Imprécision sur le sens.** « Sur le compte 1648 […], par le débit du compte 661 » ne disait pas que 1648 est crédité. | « Au crédit du compte 1648 (avant 2025 : 16884), par le débit du compte 661. » La formule reprend la fiche (« débit 661 / crédit 1648 »). | Règles essentielles#4 ; plan de comptes 2026, compte 1648 |

Aucune carte n'a été supprimée ni ajoutée dans cette relecture.

Les 31 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- Code de commerce : L. 123-12, L. 123-13, L. 123-20, L. 123-21 (k11 délimitée par « en principe »), L. 232-10 (y compris la suppression de la nullité textuelle par l'ordonnance n° 2025-229), L. 232-11, L. 232-12, L. 232-13, L. 241-3, 2° et L. 242-6, 1° ;
- CGI : art. 38, 2 bis (k17) et art. 1668 (k26 : acomptes au plus tard les 15 mars, 15 juin, 15 septembre et 15 décembre ; solde au 15 du quatrième mois, ou au 15 mai pour une clôture au 31 décembre) ;
- PCG : art. 513-1, 513-2 et 515-1 dans la rédaction du règlement n° 2026-04 (k23 et k24 se complètent sans se répéter) ;
- comptes de régularisation du plan 2026 (408, 4282, 4286, 4382, 4386, 4481, 44811, 468, 4181, 4482, 439, 467, 486, 487, 44586, 44587, 1648) et comptes d'affectation (120, 129, 1061, 1063, 1068, 110, 119, 457, 444, 695).

Cartes examinées sans être modifiées :
- **k25** (CE, 13 mars 2025, Sté TDA). La réponse reprend mot pour mot l'actualité d'impots.gouv.fr citée par la fiche : on retient le chiffre d'affaires de l'ensemble du groupe, fiscalement intégré ou non. L'article 219 du CGI a été modifié par la loi n° 2026-103 (version du 21 février 2026). La relecture finale de la fiche a confirmé dans cette version les conditions du taux réduit, et rien n'indique que cette loi soit revenue sur l'interprétation du Conseil d'État. Aucune recherche n'a été jugée nécessaire.
- **k27 et k28** (réserve légale). La seconde phrase de k28 redit la base du prélèvement déjà donnée par k27. Mais k28 porte une règle distincte, le plafonnement de la dotation, et la redite aide à retenir le piège.
- **k31 et k32** (limite des distributions, dividende fictif). Les deux réponses se recoupent, mais les questions sont distinctes : une condition d'un côté, la définition d'une notion de l'autre.
- **k34** (traitement d'une perte). Si un report à nouveau créditeur existe, la perte s'y impute d'abord (débit 110). La réponse « compte 119 ou imputation sur les réserves » reste celle qu'attend un correcteur du DCG. Le point est signalé dans la fiche (voir ci-dessous).
- **k36** (compte 44811). Elle recoupe les cartes du plan comptable des comptes 44811 et 4482, qui portent le même piège dans leur champ « Piège ». Elle est conservée parce que c'est la seule carte du chapitre sur la recodification (Ce qui a changé récemment#2), et que le provisionnement des congés payés (4282, 4382, 44811) est un classique des sujets d'inventaire.
- **k15 et k16** (charges et produits constatés d'avance). Elles citent les comptes mouvementés, mais sans montant : ce sont des cartes de compréhension, pas des écritures chiffrées.

## Recherches

Une seule recherche WebSearch a été faite, limitée à `anc.gouv.fr`.

1. **« règlement ANC 2022-06 résultat exceptionnel événement majeur et inhabituel corrections d'erreurs amortissements dérogatoires »** (anc.gouv.fr). Résultats : le règlement n° 2022-06 (PDF officiel, R2022_06.pdf) et sa version commentée (R2022_06_version-commentee.pdf). Ils confirment trois points :
   - le résultat exceptionnel regroupe, en principe, les produits et charges directement liés à un événement majeur et inhabituel ;
   - les écritures d'origine purement fiscale (provisions réglementées, amortissements dérogatoires) y restent ;
   - les corrections d'erreurs y sont aussi classées, sauf lorsqu'elles corrigent une écriture imputée directement sur les capitaux propres.

   Ce dernier point fonde la correction de k19 et le premier point à reprendre dans la fiche. La carte k20 (présomption d'événement inhabituel, citation de la fiche) n'est pas remise en cause.

Aucune autre recherche n'a été jugée nécessaire. Les autres points étaient établis par les citations officielles de la fiche, par le rapport de relecture finale de la fiche (`rapports/ue9-07.md`) et par celui des comptes de tiers (`data/pcg/RAPPORT-comptes-tiers.md`).

## Points à reprendre dans la fiche

1. **Ce qui a changé récemment#0 (résultat exceptionnel).** « Le résultat exceptionnel ne comprend plus que les produits et charges directement liés à un événement majeur et inhabituel, les écritures d'origine purement fiscale […] restant en 687 / 787 » est trop absolu. Le règlement ANC n° 2022-06 classe aussi en résultat exceptionnel les corrections d'erreurs, sauf celles qui corrigent une écriture imputée directement sur les capitaux propres. L'item devrait le dire, d'après le texte du règlement (article à citer après lecture du PDF officiel).
2. **Règles essentielles#15 (écriture d'affectation).** L'item ne prévoit pas l'apurement d'un report à nouveau débiteur par le bénéfice (crédit 119). Il ne prévoit pas non plus l'imputation d'une perte sur un report à nouveau créditeur (débit 110). Ces deux cas sont courants dans les sujets d'affectation et découlent de L. 232-10 et L. 232-11 (bénéfice diminué des pertes antérieures).
3. **Règles essentielles#12 (paiement de l'IS), point de la première relecture que je partage, déjà relevé lors de la passe précédente.** Pour un exercice clos le 31 décembre, le 15 du quatrième mois serait le 15 avril. Le 15 mai n'est donc pas une illustration de la règle mais une dérogation (CGI, art. 1668, 2 : exercice clos le 31 décembre, ou aucun exercice clos dans l'année). Il faudrait la formuler comme telle (« par exception, … »). La carte k26 la présente déjà ainsi.
4. **Règles essentielles#12 (acomptes), relevé lors de la passe précédente et toujours en attente.** « Calculés sur le bénéfice du dernier exercice clos » n'est pas exact pour les grandes entreprises. Leur dernier acompte est modulé selon l'impôt estimé de l'exercice en cours (CGI, art. 1668, 1). L'item devrait réserver ce cas, ou s'en tenir au calendrier.
5. **Règles essentielles#7 (C. com., art. L. 123-21), point de la première relecture que je partage.** La fiche ne mentionne pas l'exception légale de l'alinéa 2. Après inventaire, on peut inscrire le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, lorsque sa réalisation est certaine et que le bénéfice global peut être évalué avec une sécurité suffisante. Sans cette précision, l'item se lit comme une règle sans exception ; la carte k11 la délimite par « en principe ». Le résultat transmis de la première relecture s'interrompt au milieu de ce point : le texte reçu s'arrête sur « Ce n'est pas faux, mais c'est ».

## Classement des exercices

Le classement automatique des 16 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 10 | oui |
| `calcul` | 6 | non |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé entre les classeurs. Les 10 exercices de nature `notion` entrent dans les révisions espacées avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 6 exercices de nature `calcul` restent dans le chapitre mais ne sont pas proposés en révision.
