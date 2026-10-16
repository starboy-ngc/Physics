# Cartes de notions : ue3-02 (Formation du contrat de travail et contrats particuliers)

15 octobre 2026. Fichier : `data/ue3/ue3-02.cartes.json`. Fiche de référence : `data/ue3/ue3-02.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`) et reprend le `src` et l'`url` du premier.
2. **Relecture de fidélité.** Le premier relecteur a confronté les 35 cartes au seul texte (`t` et `cite`) de leurs items de base. Il a corrigé 3 cartes (k03, k12, k27), sans suppression ni ajout, et sans recherche web.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code du travail, Code de la sécurité sociale et jurisprudence de la Cour de cassation. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse et il a recherché les doublons. Bilan : 10 cartes corrigées, aucune suppression, aucun ajout.
4. **Recherches.** Une seule recherche WebSearch a été faite, sur les 3 autorisées, limitée à urssaf.fr et service-public.fr. Elle portait sur l'exonération des apprentis (k28). L'arrêt du 28 mai 2026 (k29) n'a pas été recherché à nouveau : il est confirmé par la recherche n° 4 du rapport `data/ue3/rapports/ue3-03.md`, avec son URL et sa citation.

`node validate.js data/ue3/ue3-02.cartes.json` : ✓ (35 cartes, 6 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 6 de définition (`def`) et 29 de compréhension (`comp`). Aucun identifiant libre.
- Chaque item des sections « Définitions », « Règles essentielles », « Ce qui a changé récemment » et « Points de vigilance » a au moins une carte.
- **Items de la fiche sans carte** (tous dans « Chiffres et seuils ») :
  - **#3** (rémunération minimale de l'apprenti) : barème de pourcentages du SMIC fixé par décret. Une carte se réduirait au rappel d'un barème.
  - **#4** (apprenti en 2026) : montants millésimés, exclus par le contrat.
  - **#5** (prescriptions de 2 ans et de 12 mois), **#6** (discrimination, 5 ans) et **#7** (salaires, 3 ans) : délais de contentieux, en marge de la formation du contrat. Le jeu atteint déjà le plafond de 35 cartes : en ajouter une imposerait une suppression.
- La règle de la période d'essai du CDD (un jour par semaine, dans la limite de deux semaines ou d'un mois), qui figure dans Règles essentielles#0, n'a pas de carte propre. Elle sert surtout au décompte (voir l'exercice #7 dans « Classement des exercices »).

## Corrections de la première relecture (fidélité à la fiche)

Ces lignes reprennent le résultat transmis par la première relecture. Sa ligne de validation est tronquée dans ce résultat. Le fichier qu'elle a laissé passe le validateur.

| cible | problème | correction |
|---|---|---|
| k03 | La question « De quoi dépend la qualification d'une relation en contrat de travail ? » admettait d'autres réponses justes : l'existence d'un lien de subordination, la réunion des trois éléments. La réponse attendue n'était donc pas la seule possible. | Nouvelle question : « Quelle incidence la volonté des parties et la dénomination du contrat ont-elles sur la qualification de contrat de travail ? ». Nouvelle réponse : « Aucune : la qualification ne dépend ni de la volonté des parties ni de la dénomination du contrat, mais des conditions de fait d'exécution du travail. » La réponse est unique et reste fidèle à Définitions#0. |
| k12 | La question écartait le CDD à objet défini. La réponse affirmait ensuite « ces cas de recours sont limitatifs » sur une liste de quatre cas. Or la fiche range le CDD à objet défini parmi les cas limitatifs : la carte laissait croire que la liste de quatre était exhaustive. | Question réécrite : « Quels sont les cas de recours au contrat à durée déterminée (CDD) prévus par le Code du travail ? ». Le CDD à objet défini est ajouté à la réponse, qui reprend ainsi les cinq cas de Règles essentielles#2 (43 mots). La relecture d'exactitude a ensuite revu cette carte (voir ci-dessous). |
| k27 | La réponse renvoyait à des CDI refusés « dans ces conditions » sans dire lesquelles. La carte ne se suffisait pas à elle-même et il lui manquait la condition essentielle : même emploi ou emploi similaire, rémunération au moins équivalente, etc. | Les conditions de la fiche sont reprises : même emploi ou emploi similaire, rémunération au moins équivalente, durée du travail équivalente, même classification, même lieu de travail. La réponse garde la règle des deux refus en douze mois et l'information de France Travail dans le délai d'un mois (64 mots). Question reformulée : « … quelle conséquence sur l'assurance chômage peut avoir le refus par le salarié d'un CDI proposé à l'issue de son CDD ? ». La relecture d'exactitude a ensuite revu cette carte (voir ci-dessous). |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k07 | Le délai de trois mois après la prise de poste était présenté comme absolu. Or le travailleur de nuit et le travailleur de moins de 18 ans passent la visite avant leur affectation. Pour le salarié en suivi individuel renforcé, un examen médical d'aptitude remplace la visite d'information et de prévention. | « en principe » ajouté devant le délai de trois mois. La définition est inchangée. | C. trav., art. R. 4624-10, R. 4624-18 et R. 4624-24 |
| k09 | « Durée maximale » pouvait s'entendre renouvellement compris : la réponse « 4, 6 et 8 mois » était alors juste aussi. | Question : « Hors renouvellement, quelle est la durée maximale de la période d'essai d'un CDI selon la catégorie du salarié ? ». La réponse est inchangée. | C. trav., art. L. 1221-19 et L. 1221-21 |
| k10 | La question visait aussi le contrat de mission. Pour ce contrat, l'article L. 2253-1 range encore dans le bloc 1 les cas de mise à disposition de l'article L. 1251-7 (12°), que la réponse ne donne pas : celle-ci était donc incomplète. | Question limitée à la période d'essai et au CDD. La réponse précise que la durée totale du contrat de mission relève aussi du bloc 1 (« la durée totale du CDD (comme celle du contrat de mission) »). | C. trav., art. L. 2253-1 (7°, 10° et 12°) |
| k12 | Après la première relecture, la question demandait « les cas de recours prévus par le Code du travail » et la réponse les disait « limitatifs ». La liste de cinq cas passait donc pour complète. Or elle omet le remplacement d'un chef d'entreprise ou d'exploitation agricole et de son conjoint collaborateur, ainsi que les CDD liés à la politique de l'emploi ou à la formation. | Question : « Quels sont les **principaux** cas de recours au CDD prévus par le Code du travail ? ». Dernière phrase : « Le recours au CDD n'est permis que dans les cas limitativement énumérés par la loi. » La carte n'ajoute pas les cas absents de la fiche (voir les points à reprendre). | C. trav., art. L. 1242-2 (4° et 5°) et L. 1242-3 |
| k13 | « Dans quelles situations le recours à un CDD est-il interdit ? » admettait une autre réponse juste : pour pourvoir durablement un emploi lié à l'activité normale et permanente. C'est la réponse de k11, d'où un doublon. | Question : « Dans quels cas le Code du travail interdit-il **expressément** de conclure un contrat à durée déterminée (CDD) ? ». Elle vise les interdictions des articles L. 1242-5 et L. 1242-6. La réponse est inchangée. | C. trav., art. L. 1242-1, L. 1242-5 et L. 1242-6 |
| k16 | Deux défauts. Les exceptions à la durée minimale de 24 heures étaient présentées comme complètes, alors que la durée minimale ne s'applique pas non plus aux contrats de sept jours au plus ni aux CDD et missions de remplacement. Et « s'il s'agit d'un étudiant de moins de 26 ans » laissait croire à une dérogation automatique, alors que la durée inférieure est fixée de droit à la demande de l'étudiant. | Réponse : « 24 heures par semaine. Une durée inférieure peut notamment être fixée à la demande écrite et motivée du salarié, ou à la demande d'un étudiant de moins de 26 ans. » | C. trav., art. L. 3123-7 et L. 3123-27 |
| k17 | Les limites d'âge et la liste des dérogations étaient présentées comme complètes. Un jeune d'au moins 15 ans qui a achevé le premier cycle de l'enseignement secondaire peut aussi débuter un apprentissage. La limite de 29 ans connaît d'autres dérogations, notamment pour un contrat qui suit un précédent contrat. | « ouvert en principe » et « notamment » ajoutés. La définition (contrat de travail de type particulier) est inchangée. | C. trav., art. L. 6222-1 et L. 6222-2 |
| k19 | La réponse donne le cadre ordinaire. En cas de circonstances exceptionnelles (menace d'épidémie, force majeure), l'employeur peut imposer le télétravail sans accord collectif, charte ni accord du salarié. | Question délimitée : « Hors circonstances exceptionnelles, dans quel cadre le télétravail est-il mis en place dans une entreprise ? ». La réponse est inchangée. | C. trav., art. L. 1222-9 et L. 1222-11 |
| k24 | « Comment est fixée l'indemnité de fin de contrat ? » admettait d'autres réponses justes : versée à l'issue du contrat avec le dernier salaire, destinée à compenser la précarité. | Question : « Comment le **montant** de l'indemnité de fin de contrat due au salarié en CDD est-il déterminé ? ». Le verso commence par « Il est égal à 10 % de la rémunération totale brute… ». | C. trav., art. L. 1243-8 et L. 1243-9 |
| k27 | « ne peut pas être accordée » présentait la privation d'allocation comme automatique. Or la règle cesse de jouer notamment si le demandeur a été employé en CDI au cours de la même période. | « ne peut **en principe** pas être accordée » (65 mots). | C. trav., art. L. 5422-1 (connaissances générales, non vérifié par recherche) |

Les autres cartes ont été contrôlées sans changement : k01 à k06, k08, k11, k14, k15, k18, k20 à k23, k25, k26 et k28 à k35. Deux points ont été examinés sans donner lieu à correction :
- **k20, k29 et k32** traitent tous trois de l'accord de performance collective, sous trois angles : la limite au principe de faveur, les objets qui peuvent s'imposer au contrat, la substitution et le refus. Il n'y a pas de doublon : aucune de ces cartes ne pose la même question.
- **k25** : la fiche dit « refus d'un CDI pour le même emploi ». La carte suit cette formulation, qui reste vraie sans être complète (voir les points à reprendre).

## Recherches faites

1 recherche sur les 3 autorisées.

1. WebSearch, `allowed_domains` : urssaf.fr, service-public.fr, requête « apprenti exonération cotisations salariales 50 % SMIC CSG CRDS contrats 2026 LFSS 2026 ».
   - **Confirmé.** Pour les contrats d'apprentissage conclus à partir du 1er mars 2025, l'exonération des cotisations et contributions salariales, CSG-CRDS comprises, est limitée à la part de rémunération n'excédant pas 50 % du SMIC. Les contrats conclus avant cette date restent soumis à l'ancien régime (79 % du SMIC), même s'ils font l'objet d'un avenant. La page Urssaf, mise à jour il y a environ trois mois, ne signale aucune modification par la LFSS 2026 (loi n° 2025-1403 du 30 décembre 2025). La carte k28 est exacte.
   - Sources : [Urssaf, Embaucher un alternant en contrat d'apprentissage](https://www.urssaf.fr/accueil/employeur/embaucher-gerer-salaries/embaucher/contrat-apprentissage.html) ; [Urssaf, Exonération (contrat d'apprentissage)](https://www.urssaf.fr/portail/home/administration-et-collectivite-t/beneficier-dune-exoneration/le-contrat-dapprentissage-dans-l/exoneration.html).

Vérification faite sans recherche, avec des données du dépôt : rapport `data/ue3/rapports/ue3-03.md`, recherche n° 4. L'arrêt Cass. soc., 28 mai 2026, n° 24-19.461 et s., y est confirmé avec son URL (JURITEXT000054167543) et sa citation mot pour mot. Les cartes k20 et k29 sont exactes.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Ces constats viennent de connaissances générales et n'ont pas été vérifiés sur le web dans cette passe.

1. **Règles essentielles#2** (CDD, cas de recours). Ce point était déjà signalé par la première relecture et il est confirmé ici. La liste est présentée comme « cas limitatifs », mais elle omet :
   - le remplacement d'un chef d'entreprise artisanale, industrielle ou commerciale, d'un professionnel libéral, de son conjoint collaborateur ou d'un associé non salarié (L. 1242-2, 4°) ;
   - le remplacement d'un chef d'exploitation agricole ou d'un aide familial (5°) ;
   - les CDD liés à la politique de l'emploi ou à la formation (L. 1242-3) ;
   - deux sous-cas du remplacement d'un salarié : le passage provisoire à temps partiel et le départ définitif qui précède la suppression du poste (1°).

   Il faut compléter la liste ou écrire « notamment ».
2. **Règles essentielles#6** (temps partiel). « Sauf demande écrite et motivée du salarié ou étudiant de moins de 26 ans » est incomplet. La durée minimale ne s'applique pas aux contrats de sept jours au plus, ni aux CDD et missions de remplacement (L. 3123-7). Pour l'étudiant de moins de 26 ans, la durée inférieure est fixée de droit à sa demande : la demande écrite et motivée vise les autres salariés.
3. **Règles essentielles#7** (apprentissage). Il faut ajouter l'entrée possible dès 15 ans pour le jeune qui a achevé le premier cycle de l'enseignement secondaire (L. 6222-1), et écrire « notamment » devant les dérogations à la limite de 29 ans, qui comprennent aussi les cas de L. 6222-2 (contrat qui suit un précédent contrat, rupture pour une cause indépendante de la volonté de l'apprenti).
4. **Définitions#3** (visite d'information et de prévention). Le délai de trois mois vaut en principe :
   - le travailleur de nuit et le travailleur de moins de 18 ans passent la visite avant leur affectation (R. 4624-18) ;
   - pour le salarié en suivi individuel renforcé, un examen médical d'aptitude remplace la visite (R. 4624-24) ;
   - la périodicité est de trois ans au plus pour certains salariés (R. 4624-17).
5. **Chiffres et seuils#2** (indemnité de fin de contrat). L'exclusion « refus d'un CDI pour le même emploi » est à compléter en « pour occuper le même emploi ou un emploi similaire, assorti d'une rémunération au moins équivalente » (L. 1243-10, 3°). Deux autres précisions sont à ajouter : l'exclusion des contrats saisonniers ou d'usage joue « sauf dispositions conventionnelles plus favorables », et les contrats de l'article L. 1242-3 sont aussi exclus.
6. **Ce qui a changé récemment#1** (refus d'un CDI). La privation de l'allocation d'assurance chômage après deux refus en douze mois comporte des exceptions. Elle ne joue pas notamment si le demandeur a été employé en CDI au cours de la même période (L. 5422-1). L'item gagnerait à le dire.
7. **Règles essentielles#8** (télétravail). L'item ne mentionne pas la mise en œuvre imposée par l'employeur en cas de circonstances exceptionnelles (L. 1222-11), alors que l'article figure dans les `textes` de la fiche.
8. **Règles essentielles#1** (bloc 1), complément. Pour le travail temporaire, l'article L. 2253-1 range aussi dans le bloc 1 les cas de mise à disposition d'un salarié temporaire de l'article L. 1251-7 (12°).

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

À la date de ce rapport, l'exercice #24 porte encore `"nature": "notion"` dans `data/ue3/ue3-02.json` : il reste à l'aligner sur le classement. Les 19 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes.
