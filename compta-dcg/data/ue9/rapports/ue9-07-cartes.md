# Cartes de notions : ue9-07 (Clôture : régularisations et résultat)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-07.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte (`t` et `cite`) des items de la fiche : mêmes conditions, mêmes exceptions, même vocabulaire juridique. Elle n'a fait aucune recherche web. Elle a contrôlé 34 cartes, en a corrigé trois (k14, k23, k32) et en a ajouté une (k36).
3. **Relecture d'exactitude (reprise).** Une seconde relecture, indépendante, a repris les 35 cartes une à une, sous l'angle d'un expert-comptable et juriste au 15 octobre 2026. Elle a vérifié trois points :
   - l'exactitude en droit et en comptabilité (Code de commerce, CGI, BOFiP, PCG modifié par les règlements ANC n° 2022-06 et 2026-04) : rien de faux, de périmé, ou de vrai seulement dans un cas particulier non dit ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ou purement mécaniques.

   Elle a aussi vérifié qu'aucune carte ne demande de calcul, d'écriture chiffrée ni de chiffre millésimé. Elle a fait une seule recherche WebSearch, limitée à impots.gouv.fr, bofip.impots.gouv.fr et legifrance.gouv.fr (voir « Recherches »). Les autres points de fond s'appuient sur les citations officielles de la fiche, sur `rapports/ue9-07.md`, `data/FAITS-CONFIRMES.md`, `data/POINTS-OUVERTS.md` et sur le plan de comptes local (`data/pcg/`).
4. **Validation.** `node validate.js data/ue9/ue9-07.cartes.json` : ✓ (35 cartes, 10 déf.).

**Historique.** Ce jeu a déjà connu plusieurs passes. Une passe antérieure a supprimé k13 (écriture des produits à recevoir, doublon de k04 et k12), ajouté k35 (mise en paiement des dividendes) et présenté le 15 mai de k26 comme une exception. Une relecture d'exactitude interrompue avait ensuite corrigé k19 (résultat exceptionnel : critère de principe, liste non exhaustive), k33 (champ limité à l'absence de report à nouveau débiteur), k36 (place de la parenthèse « plan 2024 : 4482 ») et k14 (« au crédit du compte 1648 »). Ces corrections sont présentes dans le fichier. La présente reprise les a relues et les conserve.

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. Aucune carte n'a été supprimée ni ajoutée dans cette reprise. L'identifiant k13, supprimé lors d'une passe antérieure, reste vide (pas de renumérotation).
- **Répartition : 10 cartes `def` et 25 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte.
  - Les 17 « Règles essentielles » sont toutes couvertes sauf une (voir ci-dessous).
  - Les 5 « Points de vigilance » ont chacun leur carte de compréhension (k12, k28, k25, k24, k17).
  - Dans « Ce qui a changé récemment », les items #0, #1, #2 et #4 ont leur carte (k19 et k20, k14, k36, k29).
- **Items de fiche sans carte :**
  - **Règles essentielles#3** (écriture des produits à recevoir). Son contenu est révisé par k04 (comptes 4181, 4482, 439, 467) et par k12 (TVA au compte 44587).
  - **Chiffres et seuils#0** (réserve légale : un vingtième, un dixième). C'est la même règle que Règles essentielles#13, déjà portée par k27.
  - **Chiffres et seuils#2 et #3** (taux de l'IS, plafond du taux réduit et son prorata). Ils sont millésimés et appellent un calcul.
  - **Ce qui a changé récemment#3, #5 et #6** (règlement ANC n° 2026-04, contribution exceptionnelle des grandes entreprises, seuils des petites entreprises). Ils sont millésimés. La règle stable de l'article 515-1 du PCG reste portée par k23 et k24.
- **Chiffres et dates.** Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres qui restent sont stables et font partie d'une règle : un vingtième, un dixième, neuf mois, douze mois, dates d'échéance de l'IS. Les années citées (2024, 2025, ordonnance de 2025, CE 2025) sont des dates d'entrée en vigueur, de plan de comptes ou de décision.

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
| ue9-07-k32 | **Vrai seulement dans un cas non dit.** « Sa répartition par les dirigeants est pénalement sanctionnée » présente toute répartition d'un dividende fictif comme un délit. Or le délit suppose une répartition opérée « en l'absence d'inventaire ou au moyen d'inventaires frauduleux », et de mauvaise foi. Une distribution irrégulière faite de bonne foi, sur un inventaire régulier, est un dividende fictif sans être un délit. La fiche ne donne pas ces conditions : la carte ne peut pas les ajouter. | Dernière phrase remplacée par « Sa répartition par les dirigeants peut être pénalement sanctionnée. » Le reste de la réponse, la base, `src` et `url` sont inchangés. | C. com., art. L. 241-3, 2° (SARL) et L. 242-6, 1° (SA) |
| ue9-07-k26 | **Vrai seulement dans un cas non dit.** « Quatre acomptes » vaut pour un exercice de douze mois. Pour un exercice plus court ou plus long, le nombre d'acomptes dépend des échéances comprises dans l'exercice. | Question délimitée : « Hors cas de dispense d'acomptes, selon quel calendrier une société soumise à l'impôt sur les sociétés (IS) paie-t-elle l'impôt d'un exercice de douze mois ? ». Réponse inchangée. | CGI, art. 1668, 1 ; BOI-IS-DECLA-20-10 |
| ue9-07-k18 | **Ambiguïté.** « Comment les produits et les charges sont-ils classés au compte de résultat ? » admettait une autre bonne réponse, attendue dans d'autres chapitres : « par nature ». La règle de Règles essentielles#8 porte sur ce que le classement doit faire apparaître. | Nouvelle question : « Selon le Plan comptable général (PCG), que doit faire apparaître le classement des produits et des charges au compte de résultat ? ». Réponse : « Les différents niveaux de résultat : exploitation, financier et exceptionnel, puis participation des salariés et impôt sur les bénéfices. » | PCG, art. 513-2 (citation de la fiche) |
| ue9-07-k34 | **Ambiguïté, vrai seulement dans un cas non dit.** Lorsqu'un report à nouveau créditeur existe, la perte s'y impute d'abord (débit 110) : c'était une autre bonne réponse, que la carte ne donnait pas. La carte k33, sa voisine, délimite déjà son champ de la même façon pour le bénéfice. | Question délimitée : « Lors de l'affectation du résultat d'une société sans report à nouveau créditeur, comment une perte de l'exercice est-elle traitée ? ». La réponse, fidèle à Règles essentielles#15, est inchangée. | Plan de comptes 2026, comptes 110 et 119 ; C. com., art. L. 232-11 |

Aucune carte n'a été supprimée ni ajoutée dans cette relecture.

Les 31 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Points vérifiés :
- **Code de commerce** : L. 123-12, L. 123-13, L. 123-20, L. 123-21 (k11 délimitée par « en principe », l'alinéa 2 ouvrant une exception), L. 232-10 (y compris la suppression de la formule de nullité par l'ordonnance n° 2025-229, applicable depuis le 1er octobre 2025), L. 232-11, L. 232-12, L. 232-13.
- **CGI** : art. 38, 2 bis (k17), art. 1668 (k26 : acomptes au plus tard les 15 mars, 15 juin, 15 septembre et 15 décembre ; solde au 15 du quatrième mois, ou au 15 mai pour une clôture au 31 décembre) et art. 219, I-b avec l'arrêt TDA (k25, voir « Recherches »).
- **PCG** : art. 513-1, 513-2, 513-5 (résultat exceptionnel, k19 et k20) et 515-1 dans la rédaction du règlement n° 2026-04 (k23 et k24 se complètent sans se répéter).
- **Plan de comptes 2026**, recoupé avec `data/pcg/` et `data/FAITS-CONFIRMES.md` :
  - comptes de régularisation : 408, 4282, 4286, 4382, 4386, 439, 4481, 44811, 4482, 467, 468, 4181, 486, 487, 44586, 44587 ;
  - intérêts courus : 1648 (ancien 16884) et 1688 ;
  - comptes de résultat et d'affectation : 120, 129, 1061, 1063, 1068, 110, 119, 457, 444, 695, 687, 787.

Cartes examinées sans être modifiées :
- **k25** (CE, 13 mars 2025, Sté TDA). La recherche confirme la position du Conseil d'État reprise par impots.gouv.fr. Elle ne montre aucune modification du I-b de l'article 219 par la loi n° 2026-103 sur ce point. La fiche ue4-04 retient la même règle.
- **k05 et k15, k06 et k16** (charges et produits constatés d'avance). Les questions sont distinctes : la définition d'un côté, le traitement à la clôture (fraction retirée, hors taxes) de l'autre. Les comptes sont cités sans montant : ce ne sont pas des écritures chiffrées.
- **k27 et k28** (réserve légale). La seconde phrase de k28 redit la base du prélèvement déjà donnée par k27. Mais k28 est la seule carte de Points de vigilance#1 et porte une règle distincte, le plafonnement de la dotation.
- **k31 et k32** (limite des distributions, dividende fictif). Les réponses se recoupent, mais les questions sont distinctes : une condition d'un côté, la définition d'une notion de l'autre.
- **k04** (produit à recevoir). La définition parle de facture « pas encore établie », ce qui convient mal aux produits à recevoir de l'État (4482) et des organismes sociaux (439). La carte reprend fidèlement la fiche : le point est signalé ci-dessous.
- **k23 et k24** (article 515-1 du PCG). La date d'application du règlement n° 2026-04 n'est pas tranchée (`data/POINTS-OUVERTS.md`). Les deux cartes ne la mentionnent pas et énoncent le contenu de l'article tel qu'il est rédigé : elles restent exactes.
- **k36** (compte 44811). Elle recoupe les cartes du plan comptable des comptes 44811 et 4482. Elle est conservée parce que c'est la seule carte du chapitre sur la recodification (Ce qui a changé récemment#2).

## Recherches

Une seule recherche WebSearch a été faite, limitée à impots.gouv.fr, bofip.impots.gouv.fr et legifrance.gouv.fr.

1. **« taux réduit impôt sur les sociétés chiffre d'affaires ensemble du groupe société TDA article 219 I-b loi de finances 2026 »**. Résultats :
   - l'actualité d'impots.gouv.fr citée par la fiche : selon le CE (13 mars 2025, n° 481538, Sté TDA), on retient le chiffre d'affaires de l'ensemble du groupe détenant la société, fiscalement intégré ou non, avec régularisation sans pénalité jusqu'au 20 mai 2026 ;
   - l'article 219 du CGI sur Légifrance (LEGIARTI000046868562) : il garde la somme des chiffres d'affaires pour la société mère d'un groupe intégré ;
   - la loi n° 2026-103 du 19 février 2026 (JORFTEXT000053508155) : aucun extrait ne montre une modification du I-b de l'article 219 sur le chiffre d'affaires des groupes.

   La carte k25 est confirmée.

Aucune autre recherche n'a été jugée nécessaire. Les textes des articles L. 241-3, 2° et L. 242-6, 1° du Code de commerce (conditions du délit de répartition de dividendes fictifs) et de l'article 1668 du CGI sont connus et stables.

## Points à reprendre dans la fiche

1. **Règles essentielles#16 (dividende fictif)**, point nouveau. « Tout dividende distribué en violation de ces règles est un dividende fictif, dont la répartition par les dirigeants est pénalement sanctionnée » est trop absolu. Les articles L. 241-3, 2° (SARL) et L. 242-6, 1° (SA) ne punissent la répartition de dividendes fictifs que si elle est opérée « en l'absence d'inventaire ou au moyen d'inventaires frauduleux », ce qui suppose aussi la mauvaise foi. L'item devrait reprendre ces conditions, avec une citation de l'article.
2. **Règles essentielles#12 (paiement de l'IS)**, trois points :
   - **le 15 mai** (point de la première relecture, que je partage) : pour un exercice clos le 31 décembre, le 15 du quatrième mois serait le 15 avril. Le 15 mai n'est donc pas une illustration de la règle mais une dérogation (CGI, art. 1668, 2 : exercice clos le 31 décembre, ou aucun exercice clos dans l'année). Il faudrait la formuler comme telle (« par exception, … »). La carte k26 la présente déjà ainsi ;
   - **les acomptes** (point d'une passe antérieure, toujours en attente) : « calculés sur le bénéfice du dernier exercice clos » n'est pas exact pour les grandes entreprises, dont le dernier acompte est modulé selon l'impôt estimé de l'exercice en cours (CGI, art. 1668, 1). L'item devrait réserver ce cas, ou s'en tenir au calendrier ;
   - **les quatre acomptes** (point nouveau) : ce nombre vaut pour un exercice de douze mois. L'item devrait le préciser, comme le fait désormais la question de k26.
3. **Règles essentielles#7 (C. com., art. L. 123-21)**, point de la première relecture, que je partage. La fiche ne mentionne pas l'exception légale de l'alinéa 2 : après inventaire, on peut inscrire le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, lorsque sa réalisation est certaine et que le bénéfice global peut être évalué avec une sécurité suffisante. Sans cette précision, l'item se lit comme une règle sans exception ; la carte k11 la délimite par « en principe ». Le résultat transmis de la première relecture s'interrompt au milieu de ce point (« Ce n'est pas faux, mais c'est »).
4. **Ce qui a changé récemment#0 (résultat exceptionnel)**, point d'une passe antérieure, toujours en attente. « Le résultat exceptionnel ne comprend plus que les produits et charges directement liés à un événement majeur et inhabituel, les écritures d'origine purement fiscale […] restant en 687 / 787 » est trop absolu. Le règlement ANC n° 2022-06 classe aussi en résultat exceptionnel les corrections d'erreurs, sauf celles qui corrigent une écriture imputée directement sur les capitaux propres.
5. **Règles essentielles#15 (écriture d'affectation)**, point d'une passe antérieure, toujours en attente. L'item ne prévoit pas deux cas courants dans les sujets d'affectation, qui découlent de L. 232-10 et L. 232-11 (bénéfice diminué des pertes antérieures) :
   - l'apurement d'un report à nouveau débiteur par le bénéfice (crédit 119) ;
   - l'imputation d'une perte sur un report à nouveau créditeur (débit 110).

   Les cartes k33 et k34 délimitent désormais leur champ en conséquence.
6. **Définitions#2 (produit à recevoir)**, point nouveau et mineur. « Dont la facture n'est pas encore établie à la clôture » décrit les factures à établir (4181). Mais l'item range sous la même définition les produits à recevoir de l'État (4482) et des organismes sociaux (439), pour lesquels il n'y a pas de facture. Une formule plus générale serait plus juste : produit acquis à l'exercice, non encore facturé ou dont la pièce justificative n'est pas encore reçue.
7. **Ce qui a changé récemment#3 (règlement ANC n° 2026-04)**, rappel de `data/POINTS-OUVERTS.md`. La date d'application du règlement n'est pas indiquée : exercices en cours au 4 septembre 2026, ou ouverts à compter du 1er janvier 2027 ? Les cartes k23 et k24 n'en dépendent pas, mais l'item gagnerait à la préciser.

## Classement des exercices

Le classement automatique des 16 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 10 | oui |
| `calcul` | 6 | non |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé entre les classeurs. Les 10 exercices de nature `notion` entrent dans les révisions espacées avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 6 exercices de nature `calcul` restent dans le chapitre mais ne sont pas proposés en révision.
