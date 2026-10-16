# Cartes de notions : ue3-02 (Formation du contrat de travail et contrats particuliers)

15 octobre 2026. Fichier : `data/ue3/ue3-02.cartes.json`. Fiche de référence : `data/ue3/ue3-02.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`) et reprend le `src` et l'`url` du premier.
2. **Premier tour de relecture (rappel).** Une relecture de fidélité a corrigé k03, k12 et k27. Une relecture d'exactitude a ensuite corrigé 10 cartes : k07, k09, k10, k12, k13, k16, k17, k19, k24 et k27. Elle a ajouté des réserves (« en principe », « notamment », « Hors circonstances exceptionnelles »), délimité des questions et fait une recherche sur l'exonération des apprentis (k28). Ces corrections sont conservées.
3. **Relecture de fidélité (reprise).** Le premier relecteur a confronté les 35 cartes au seul texte (`t` et `cite`) de la fiche, sans recherche web. Il a corrigé 3 cartes (k10, k13, k34), sans suppression ni ajout. Le détail figure ci-dessous.
4. **Relecture d'exactitude (reprise).** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code du travail, Code de la sécurité sociale et jurisprudence de la Cour de cassation. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse, celle qu'attendrait un correcteur du DCG, et il a recherché les doublons et les cartes sans intérêt. Bilan : 4 cartes corrigées (k13, k14, k17, k25), aucune suppression, aucun ajout.
5. **Recherches.** Aucune recherche WebSearch dans cette reprise : les points corrigés reposent sur des articles du Code du travail dont la rédaction est connue et stable (voir « Recherches faites »).

`node validate.js data/ue3/ue3-02.cartes.json` : ✓ (35 cartes, 5 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 5 de définition (`def`) et 30 de compréhension (`comp`). k17 est passée de `def` à `comp` dans cette reprise. Aucun identifiant libre.
- Chaque item des sections « Définitions », « Règles essentielles », « Ce qui a changé récemment » et « Points de vigilance » a au moins une carte.
- **Items de la fiche sans carte** (tous dans « Chiffres et seuils ») :
  - **#3** (rémunération minimale de l'apprenti) : barème de pourcentages du SMIC fixé par décret. Une carte se réduirait au rappel d'un barème.
  - **#4** (apprenti en 2026) : montants millésimés, exclus par le contrat.
  - **#5** (prescriptions de 2 ans et de 12 mois), **#6** (discrimination, 5 ans) et **#7** (salaires, 3 ans) : délais de contentieux, en marge de la formation du contrat. Le jeu atteint déjà le plafond de 35 cartes : en ajouter une imposerait une suppression.
- Deux règles de la fiche n'ont pas de carte propre :
  - la période d'essai du CDD (un jour par semaine, dans la limite de deux semaines ou d'un mois), dans Règles essentielles#0. Elle sert surtout au décompte (voir l'exercice #7 dans « Classement des exercices ») ;
  - la présomption d'accident du travail pour l'accident survenu sur le lieu de télétravail, dans Règles essentielles#8.

## Corrections de la relecture de fidélité (reprise)

Ces lignes reprennent le résultat transmis par la première relecture. Ce résultat est tronqué dans sa liste « fiche_a_reprendre » ; les points qu'il signale (Règles essentielles#2 et #6) figurent ci-dessous dans « Points à reprendre dans la fiche ».

| cible | problème | correction |
|---|---|---|
| k10 | Couverture : la durée maximale du CDD et le nombre de renouvellements prévus par la loi (Règles essentielles#3), règle importante, n'avaient aucune carte. Le jeu compte déjà 35 cartes, le plafond du validateur, et aucune carte ne remplit la condition de suppression : on ne pouvait donc pas ajouter de carte. | La règle supplétive de la fiche est ajoutée en fin de réponse, dans la logique du bloc 1 que traite la carte : « à défaut d'accord de branche, la loi limite en principe le CDD à 18 mois, renouvellements compris, et à deux renouvellements » (68 mots). « en principe » renvoie aux durées de 9 et 24 mois de la fiche. La base passe à [Règles essentielles#1, Règles essentielles#3]. Question, `src` et `url` sont inchangés (ceux de Règles essentielles#1). |
| k13 | Forme : la deuxième phrase « Il l'est aussi pour un accroissement temporaire d'activité… » n'avait pas d'antécédent grammatical, puisque la première phrase ne contient ni « CDD » ni « interdit ». | Nouvelle formulation : « Le CDD est aussi interdit pour un accroissement temporaire d'activité dans les six mois suivant un licenciement économique sur le poste, sauf contrat de trois mois au plus non renouvelable ou commande exceptionnelle à l'exportation. » Le fond ne change pas. |
| k34 | Question : « Quelle est la portée de la règle légale fixant le délai de carence… ? » admettait d'autres réponses justes, par exemple son champ (deux CDD successifs sur le même poste) ou ses exceptions, au lieu de la seule réponse attendue (« supplétive »). | Nouvelle question : « Quelle place la règle légale fixant le délai de carence entre deux CDD sur le même poste laisse-t-elle à l'accord de branche ? » (23 mots). Elle appelle la seule réponse de la carte : règle supplétive, qui ne s'applique qu'à défaut de stipulation de la branche. La réponse est inchangée. |

## Corrections de la relecture d'exactitude (reprise)

| cible | problème | correction | source |
|---|---|---|---|
| k13 | « pour des travaux particulièrement dangereux » laissait croire que tout travail dangereux interdit le CDD. L'interdiction ne vise que certains travaux particulièrement dangereux, inscrits sur une liste réglementaire, et l'autorité administrative peut exceptionnellement y déroger. | « pour **certains** travaux particulièrement dangereux ». Simple réserve : la liste réglementaire et la dérogation, absentes de la fiche, ne sont pas ajoutées (voir les points à reprendre). | C. trav., art. L. 1242-6, 2° |
| k14 | La question « En dehors de l'accord des parties, dans quels cas un CDD peut-il être rompu avant l'échéance du terme ? » admettait une autre réponse juste : pendant la période d'essai, chaque partie peut rompre librement. Cette réponse n'est pas celle de la carte. | Question délimitée : « En dehors de l'accord des parties **et de la période d'essai**, dans quels cas un CDD peut-il être rompu avant l'échéance du terme ? » (24 mots). La réponse et la base sont inchangées. La période d'essai du CDD figure dans Règles essentielles#0. | C. trav., art. L. 1242-10 et L. 1243-1 |
| k17 | « Qu'est-ce que le contrat d'apprentissage au sens du Code du travail ? » appelle, pour un correcteur du DCG, la définition de l'article L. 6221-1 : un contrat de travail de type particulier par lequel l'employeur s'engage, outre le versement d'un salaire, à assurer à l'apprenti une formation professionnelle complète, en entreprise et en CFA. La carte répondait par la limite d'âge, que la question ne demandait pas, et elle ne pouvait pas donner l'élément de formation, absent de la fiche. | La question porte désormais sur ce que la carte enseigne : « Quelle limite d'âge le Code du travail fixe-t-il, en principe, pour être engagé en contrat d'apprentissage ? ». Réponse : « De 16 ans à 29 ans révolus au début de l'apprentissage. » Les dérogations (« notamment ») sont conservées, et la nature du contrat (contrat de travail de type particulier) devient la phrase de rappel. Type `def` → `comp` (5 `def` restent, le minimum). L'absence de la définition de L. 6221-1 dans la fiche est signalée ci-dessous. | C. trav., art. L. 6221-1, L. 6222-1 et L. 6222-2 |
| k25 | « Le refus d'un CDI pour le même emploi » n'est une cause de perte de l'indemnité de fin de contrat que si le CDI proposé, pour le même emploi ou un emploi similaire, est assorti d'une rémunération au moins équivalente. Sans cette condition, la carte était vraie seulement dans un cas non dit. « La faute grave », isolée, pouvait aussi viser une faute de l'employeur, alors que seule la faute grave du salarié prive de l'indemnité. | Réponse : « Le refus d'un CDI pour occuper le même emploi ou un emploi similaire, avec une rémunération au moins équivalente, la rupture anticipée due à l'initiative du salarié, à sa faute grave ou à la force majeure, et la poursuite de la relation en CDI. » (44 mots). Les conditions du CDI sont celles de Ce qui a changé récemment#1, ajouté en seconde base ; `src` et `url` restent ceux de Chiffres et seuils#2. | C. trav., art. L. 1243-8 et L. 1243-10, 3° et 4° |

Les autres cartes ont été contrôlées sans changement : k01 à k12, k15, k16, k18 à k24 et k26 à k35. Points examinés sans correction :
- **k10** (ajout de la reprise de fidélité) : la règle supplétive est exacte. À défaut de stipulation de l'accord de branche étendu, le CDD ne peut excéder dix-huit mois, renouvellements compris, et il est renouvelable deux fois (L. 1242-8-1 et L. 1243-13-1). « en principe » couvre les durées de 9 et 24 mois, le CDD à objet défini (18 à 36 mois, non renouvelable) et les CDD sans terme précis.
- **k34** (nouvelle question) : la règle du tiers ou de la moitié ne s'applique qu'à défaut de stipulation de la branche (L. 1244-3-1 et L. 1244-4-1). La réponse est unique et exacte.
- **k20, k29 et k32** traitent tous trois de l'accord de performance collective, sous trois angles : la limite au principe de faveur, les objets qui peuvent s'imposer au contrat, la substitution et le refus. La seconde phrase de k20 annonce la réponse de k29, mais les questions diffèrent : ce n'est pas un doublon.
- **k21** : le contrôle des clauses par le juge s'appuie sur le critère général de l'article L. 1121-1 (justification et proportionnalité). Les conditions propres à chaque clause (zone géographique définie pour la mobilité, par exemple) ne sont pas dans la fiche ; la question, centrée sur les critères communs, reste juste.
- **k04** : la directive (UE) 2024/2831 sur le travail de plateforme, à transposer au plus tard le 2 décembre 2026, prévoit une présomption légale d'emploi pour les travailleurs de plateforme. Elle ne modifie pas la règle générale de l'article L. 8221-6 sur laquelle porte la carte.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les seuils cités (24 heures, 10 % et 6 %, 50 % et 79 % du SMIC, 16 et 29 ans) sont des éléments stables de règles.

## Recherches faites

Aucune recherche WebSearch dans cette reprise (0 sur les 3 autorisées). Les quatre corrections reposent sur des articles du Code du travail dont la rédaction n'a pas changé depuis l'ordonnance n° 2017-1387 ou la loi n° 2018-771 (L. 1242-6, L. 1242-10, L. 1243-1, L. 1243-10, L. 6221-1, L. 6222-1). Aucun doute réel ne justifiait d'entamer le quota partagé.

Rappel du premier tour (toujours valable) :
- une recherche limitée à urssaf.fr et service-public.fr a confirmé que, pour les contrats d'apprentissage conclus à partir du 1er mars 2025, l'exonération des cotisations et contributions salariales est limitée à la part de rémunération n'excédant pas 50 % du SMIC, les contrats antérieurs restant soumis à l'ancien régime (k28) ;
- l'arrêt Cass. soc., 28 mai 2026, n° 24-19.461 et s. (k20, k29) est confirmé par la recherche n° 4 du rapport `data/ue3/rapports/ue3-03.md`.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Ces constats viennent de connaissances générales et n'ont pas été vérifiés sur le web.

1. **Règles essentielles#7** (apprentissage), nouveau. L'item ne donne pas la définition légale du contrat d'apprentissage (L. 6221-1) : contrat de travail de type particulier par lequel l'employeur s'engage, outre le versement d'un salaire, à assurer à l'apprenti une formation professionnelle complète, dispensée pour partie en entreprise et pour partie en CFA. Il faudrait l'ajouter, ce qui permettrait de rétablir une carte de définition. Points déjà signalés : l'entrée possible dès 15 ans pour le jeune qui a achevé le premier cycle de l'enseignement secondaire (L. 6222-1), et « notamment » devant les dérogations à la limite de 29 ans, qui comprennent aussi les cas de L. 6222-2 (contrat qui suit un précédent contrat, rupture pour une cause indépendante de la volonté de l'apprenti).
2. **Règles essentielles#2** (CDD, cas de recours et interdictions). Point signalé par les deux relectures. La liste est présentée comme « cas limitatifs », mais elle omet :
   - le remplacement d'un chef d'entreprise artisanale, industrielle ou commerciale, d'un professionnel libéral, de son conjoint collaborateur ou d'un associé non salarié (L. 1242-2, 4°) ;
   - le remplacement d'un chef d'exploitation agricole ou d'un aide familial (5°) ;
   - les CDD liés à la politique de l'emploi ou à la formation (L. 1242-3) ;
   - deux sous-cas du remplacement d'un salarié : le passage provisoire à temps partiel et le départ définitif qui précède la suppression du poste (1°).

   Il faut compléter la liste ou écrire « notamment ». Nouveau : l'interdiction vise « certains travaux particulièrement dangereux figurant sur une liste établie par voie réglementaire », avec dérogation possible de l'autorité administrative (L. 1242-6, 2°).
3. **Chiffres et seuils#2** (indemnité de fin de contrat). L'exclusion « refus d'un CDI pour le même emploi » est à compléter en « pour occuper le même emploi ou un emploi similaire, assorti d'une rémunération au moins équivalente » (L. 1243-10, 3°) ; la carte k25 a dû emprunter ces conditions à Ce qui a changé récemment#1. Deux autres précisions sont à ajouter : l'exclusion des contrats saisonniers ou d'usage joue « sauf dispositions conventionnelles plus favorables », et les contrats de l'article L. 1242-3 sont aussi exclus.
4. **Règles essentielles#6** (temps partiel). « Sauf demande écrite et motivée du salarié ou étudiant de moins de 26 ans » est incomplet. La durée minimale ne s'applique pas aux contrats de sept jours au plus, ni aux CDD et missions de remplacement (L. 3123-7). Pour l'étudiant de moins de 26 ans, la durée inférieure est fixée de droit à sa demande : la demande écrite et motivée vise les autres salariés.
5. **Définitions#3** (visite d'information et de prévention). Le délai de trois mois vaut en principe :
   - le travailleur de nuit et le travailleur de moins de 18 ans passent la visite avant leur affectation (R. 4624-18) ;
   - pour le salarié en suivi individuel renforcé, un examen médical d'aptitude remplace la visite (R. 4624-24) ;
   - la périodicité est de trois ans au plus pour certains salariés (R. 4624-17).
6. **Ce qui a changé récemment#1** (refus d'un CDI). La privation de l'allocation d'assurance chômage après deux refus en douze mois comporte des exceptions. Elle ne joue pas notamment si le demandeur a été employé en CDI au cours de la même période (L. 5422-1). L'item gagnerait à le dire.
7. **Règles essentielles#8** (télétravail). L'item ne mentionne pas la mise en œuvre imposée par l'employeur en cas de circonstances exceptionnelles (L. 1222-11), alors que l'article figure dans les `textes` de la fiche.
8. **Règles essentielles#1** (bloc 1), complément. Pour le travail temporaire, l'article L. 2253-1 range aussi dans le bloc 1 les cas de mise à disposition d'un salarié temporaire de l'article L. 1251-7 (12°). Les durées et renouvellements du CDD relèvent d'une convention ou d'un accord de branche **étendu** (L. 1242-8, L. 1243-13, L. 1244-3) : l'item et Règles essentielles#3 pourraient le préciser.

## Classement des exercices

Le classement automatique porte sur les 22 exercices QCM, QCM multiples et classements du chapitre (18 QCM, 3 QCM multiples, 1 classement). Les numéros des exercices partent de 0.

| nature | nombre |
|---|---|
| notion | 19 |
| calcul | 3 |
| chiffre | 0 |

Les deux classements ont divergé sur deux exercices (notion / calcul). Les deux ont été tranchés en calcul :
- **#19** (rupture anticipée d'un CDD de 12 mois par un salarié qui a trouvé un CDI) : il faut décompter le préavis d'un jour par semaine, dans la limite de deux semaines. La notion reste révisée par la carte k14.
- **#24** (salarié à temps partiel de 30 heures porté à 35 heures par des heures complémentaires) : il faut rapprocher le volume d'heures complémentaires du dixième et de la durée légale. La notion reste révisée par la carte k33.

Le troisième exercice de nature calcul est le **#7** : la durée maximale de la période d'essai d'un CDD de quatre mois, à décompter à raison d'un jour par semaine.

À la date de ce rapport, l'exercice #24 porte encore `"nature": "notion"` dans `data/ue3/ue3-02.json` (20 notion, 2 calcul dans le fichier) : il reste à l'aligner sur le classement. Une fois aligné, les 19 exercices de nature notion entreront dans les révisions espacées, avec les 35 cartes.
