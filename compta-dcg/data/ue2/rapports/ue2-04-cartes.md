# Cartes de notions : ue2-04 (Sociétés de personnes, sociétés civiles et autres groupements)

15 octobre 2026. Fichier : `data/ue2/ue2-04.cartes.json`. Fiche de référence : `data/ue2/ue2-04.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Le premier relecteur a confronté les 35 cartes au texte de leurs items de base. Il en a corrigé 3 (k01, k06, k07), sans suppression ni ajout, et sans recherche web : la consigne de cette passe l'interdisait.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code de commerce, Code civil, CGI et BOFiP, ordonnances n° 2023-77 et n° 2025-229, lois de 1901, 1947, 1978, 1987, 2008 et 2014. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse et il a recherché les doublons. Bilan : 4 cartes corrigées (k10, k18, k30, k33), aucune suppression et aucun ajout.
4. **Recherches.** 2 recherches WebSearch sur les 3 autorisées, toutes sur legifrance.gouv.fr. Elles portaient sur l'ordonnance n° 2025-229 (nullités) et sur l'ordonnance n° 2023-77 (familles de professions). Elles confirment toutes deux les cartes concernées (k20 et k27).

`node validate.js data/ue2/ue2-04.cartes.json` : ✓ (35 cartes, 12 déf.).

## Bilan

- **35 cartes**, soit le maximum prévu par le contrat : 12 de définition (`def`) et 23 de compréhension (`comp`). Les identifiants k01 à k35 se suivent sans trou.
- Chaque item des sections « Définitions » (#0 à #7), « Règles essentielles » (#0 à #14) et « Points de vigilance » (#0 à #4) a au moins une carte.
- **Items de la fiche sans carte :**
  - **Chiffres et seuils#4** (seuils du commissaire aux comptes de la SNC) et **Ce qui a changé récemment#3** (décret n° 2024-152 qui relève ces seuils) : items millésimés ou réduits à des seuils annuels, exclus des cartes.
  - **Chiffres et seuils#0** (nombre minimal d'associés, au moins trois commanditaires dans la SCA, absence de capital minimal) : le GIE « constitué sans capital » figure dans k24, sans que l'item soit cité dans `base`. Le reste relève de la SCA ou de règles générales sur la société.
  - **Chiffres et seuils#5** (commissaire aux comptes du GIE : cent salariés ou émission d'obligations, mandat de six exercices) : pas de carte, car le jeu atteint le plafond de 35.
- **Contenus couverts en partie :**
  - la révocation du gérant de SNC non désigné par les statuts (Règles essentielles#1) ;
  - la continuation de la SCS malgré le décès d'un commanditaire (Règles essentielles#5) ;
  - l'immixtion de l'associé d'une société en participation (Règles essentielles#9) ;
  - la franchise des activités lucratives accessoires des associations (Points de vigilance#4).

  Aucun de ces points n'a de carte propre ; en ajouter un imposerait une suppression.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la première relecture est tronqué au milieu de son contrôle de couverture (« Poi… »). Les trois corrections qu'il décrit sont complètes et ont été vérifiées dans le fichier.

| cible | problème | correction |
|---|---|---|
| k01 | Deux questions en une (« Quelle qualité et quelle responsabilité… »), alors que le contrat demande une seule question pour une carte de définition. | Question unique : « Quel statut l'article L. 221-1 du Code de commerce attribue-t-il aux associés d'une société en nom collectif (SNC) ? ». Réponse inchangée, fidèle à Définitions#0 et à Chiffres et seuils#3. |
| k06 | La réponse disait « ni commandité » sans nommer la forme sociale. La déduction tirée de Points de vigilance#1 (associé de SNC ou commandité = commerçant ; or le mineur non émancipé ne peut pas être commerçant) n'était pas présentée comme une conséquence. | « ne peut donc pas être associé de SNC ni commandité de SCS » : le lien logique est explicite et la forme sociale est nommée. |
| k07 | « même par ces actes » renvoyait, par la grammaire, aux « actes entrant dans l'objet social » de la phrase précédente : le sens devenait faux ou ambigu pour la SARL, la SA et la SAS. La question était mal tournée (« Quelle différence sépare… »). | Réponse : « la société est engagée même par les actes étrangers à l'objet social, sauf si elle prouve que le tiers savait que l'acte dépassait cet objet ou ne pouvait l'ignorer, la seule publication des statuts ne suffisant pas » (Points de vigilance#2). Question : « Qu'est-ce qui distingue la SNC de la SARL, de la SA et de la SAS quant aux actes du dirigeant dépassant l'objet social ? ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k10 | La seconde phrase disait que les statuts peuvent assouplir la règle de cession unanime « pour les parts des commanditaires ». Elle laissait croire que les parts des commandités restent toujours soumises à l'unanimité. Or l'article L. 222-8, II, 3° permet aussi aux statuts d'autoriser un commandité à céder une partie de ses parts à un commanditaire ou à un tiers, avec le consentement de tous les commandités et de la majorité en nombre et en capital des commanditaires. La fiche ne mentionne pas ce cas. | « les statuts peuvent **notamment** rendre celles des commanditaires librement cessibles entre associés, ou cessibles à des tiers avec ce même accord ». Ce sont les deux facultés que donne la fiche, sans les présenter comme les seules. La question et la règle de modification des statuts sont inchangées. | C. com., art. L. 222-8 et L. 222-9 (Règles essentielles#5) |
| k18 | « Chaque associé est personnellement soumis à l'impôt sur le revenu » n'est vrai que pour l'associé personne physique. Lorsque l'associé de la SNC est une société soumise à l'IS, sa quote-part de bénéfices est déterminée et imposée selon les règles de l'IS. La question, posée pour toute SNC, appelait donc une réponse incomplète. | Question délimitée : « En l'absence d'option pour l'IS, comment sont imposés les bénéfices d'une société en nom collectif (SNC) dont tous les associés sont des personnes physiques ? ». Réponse inchangée (imposition personnelle à l'IR, option pour l'IS et renonciation jusqu'au cinquième exercice). | CGI, art. 8 et 239 (Points de vigilance#3) ; CGI, art. 238 bis K et 218 bis |
| k30 | « Exonéré d'IS » est inexact. Un organisme sans but lucratif dont la gestion est désintéressée n'est pas soumis aux impôts commerciaux, mais il reste imposable à l'IS à taux réduits sur certains revenus patrimoniaux. La réponse employait d'ailleurs déjà la notion d'« impôts commerciaux », qui est celle de la doctrine administrative. | Question : « À quelles conditions un organisme sans but lucratif, comme une association, échappe-t-il aux impôts commerciaux (IS, TVA et CET) ? ». Réponse inchangée (gestion désintéressée, absence de concurrence ou conditions différentes selon la règle des « 4 P »). | CGI, art. 206, 1 et 5 ; BOI-IS-CHAMP-10-50-10 (Points de vigilance#4) |
| k33 | La capacité juridique « à compter de l'entrée en vigueur du décret en Conseil d'État accordant la reconnaissance d'utilité publique » est la règle générale de l'article 18. La fondation d'entreprise, régie par les articles 19 et suivants de la même loi, acquiert la personnalité morale autrement (autorisation administrative publiée). Présentée sans réserve, la phrase était trop générale. | « celle-ci n'a **en principe** la capacité juridique qu'à compter de l'entrée en vigueur du décret en Conseil d'État… ». La définition (affectation irrévocable de biens, droits ou ressources à une œuvre d'intérêt général et à but non lucratif) est inchangée. | Loi n° 87-571 du 23 juillet 1987, art. 18 et 19 (Définitions#7) |

Les 31 autres cartes ont été contrôlées sans changement : k01 à k09, k11 à k17, k19 à k29, k31, k32, k34 et k35. En particulier :
- **k20** (ordonnance n° 2025-229) et **k27** (ordonnance n° 2023-77) sont confirmées par les recherches.
- **k06** est à jour : depuis la loi du 15 juin 2010, le mineur émancipé peut être commerçant sur autorisation du juge (C. com., art. L. 121-2).
- **k01** et **k05** ne font pas doublon. La première porte sur le statut de l'associé de SNC, la seconde sur le sens de la solidarité, par opposition à l'obligation conjointe des associés de société civile.
- Les cartes **k12**, **k13**, **k14**, **k15** et **k16** reprennent exactement les articles 1846, 1846-1, 1851, 1857, 1858, 1861, 1869 et 1870 du Code civil.

## Recherches faites

2 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr.

1. Requête « ordonnance n° 2025-229 du 12 mars 2025 nullités sociétés article 1844-14 code civil actions en nullité se prescrivent par deux ans ».
   - **Confirmé.** L'article 1844-14 du Code civil, dans sa rédaction en vigueur au 1er octobre 2025, soumet à une prescription de deux ans les actions en nullité de la société, des actes et des décisions. Ce délai court à compter du jour où la nullité est encourue, avec des règles propres aux fusions, aux scissions et aux opérations sur le capital. Selon le rapport au Président de la République, ce délai remplace celui de trois ans.
   - **Confirmé.** L'article 1844-12-1 subordonne l'annulation d'une décision à un « triple test » : grief subi par le demandeur, influence de l'irrégularité sur le sens de la décision, absence de conséquences excessives de l'annulation.
   - **Confirmé.** L'ordonnance s'applique à compter du 1er octobre 2025, sauf son article 67 (1er janvier 2027).
   - Effet : k20 est exacte.
   - Sources : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316108 ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316022 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051322348/2025-10-01/ ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051317310/2025-10-27
2. Requête « ordonnance n° 2023-77 du 8 février 2023 exercice en société professions libérales réglementées article 2 professions de santé juridiques ou judiciaires techniques et du cadre de vie ».
   - **Confirmé.** L'article 2 répartit les professions libérales réglementées en trois familles : professions de santé ; professions juridiques ou judiciaires, dont la liste est fixée par le décret n° 2023-1165 du 9 novembre 2023 ; professions techniques et du cadre de vie.
   - Effet : k27 est exacte.
   - Sources : https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000047106127 ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048550790

Aucune recherche n'a été faite pour les corrections de k10, k18, k30 et k33. Elles reposent sur des règles connues et stables (C. com., art. L. 222-8 ; CGI, art. 238 bis K et 206, 5 ; loi du 23 juillet 1987, art. 19). Ces corrections se bornent à délimiter la question ou à nuancer la réponse, sans rien ajouter au verso que la fiche ne dise.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Points de vigilance#3** (fiscalité par défaut). L'item dit que les associés de SNC, les commandités et les associés de sociétés civiles sont « personnellement soumis à l'impôt sur le revenu ». C'est vrai pour les associés personnes physiques. Lorsque l'associé est une entreprise soumise à l'IS, sa quote-part est déterminée et imposée selon les règles de l'IS (CGI, art. 238 bis K et 218 bis). L'item devrait le préciser ; la carte k18 a été délimitée en conséquence.
2. **Règles essentielles#5** (SCS : cessions). Il manque le 3° du II de l'article L. 222-8 : les statuts peuvent stipuler qu'un associé commandité peut céder une partie de ses parts à un commanditaire ou à un tiers, avec le consentement de tous les commandités et de la majorité en nombre et en capital des commanditaires.
3. **Points de vigilance#4** (associations et impôts commerciaux). Plusieurs points sont à revoir :
   - **Vocabulaire.** « Exonéré d'IS, de TVA et de CET » est approximatif : l'organisme sans but lucratif n'est pas soumis aux impôts commerciaux. Il reste passible de l'IS à taux réduits sur certains revenus patrimoniaux (CGI, art. 206, 5).
   - **Franchise des activités lucratives accessoires.** Elle porte aussi sur la TVA et la CFE, pas seulement sur l'IS. Ce point est à vérifier sur bofip.impots.gouv.fr avant de compléter l'item.
4. **Définitions#7** (fondation et fonds de dotation). Deux points sont à vérifier avant de compléter l'item :
   - **Fondation d'entreprise.** La règle de capacité (décret de reconnaissance d'utilité publique) est celle de l'article 18. La fondation d'entreprise (art. 19 et suivants de la loi du 23 juillet 1987) relève d'un régime propre d'autorisation administrative ; l'item pourrait le signaler.
   - **Fonds de dotation.** La définition omet une seconde affectation possible des revenus : l'article 140 de la loi du 4 août 2008 permet aussi au fonds de les redistribuer pour assister une personne morale à but non lucratif dans ses œuvres et missions d'intérêt général.

## Classement des exercices

Le classement automatique porte sur les 25 exercices QCM, QCM multiples et classements du chapitre (22 QCM, 2 QCM multiples, 1 classement) :

| nature | nombre |
|---|---|
| notion | 25 |
| calcul | 0 |
| chiffre | 0 |

Les classements ne divergent sur aucun exercice. Les 25 exercices sont de nature notion et entrent tous dans les révisions espacées, avec les 35 cartes. Les 3 exercices de calcul du chapitre (type `calc`) ne relèvent pas de ce classement et restent hors des révisions espacées.
