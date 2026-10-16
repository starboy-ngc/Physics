# Cartes de notions : ue9-02 (Le plan comptable et la partie double)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `data/ue9/ue9-02.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte de la fiche (champs `t` et `cite`). Elle a vérifié que la carte reprenait les mêmes conditions, les mêmes exceptions et le même vocabulaire. Elle n'a fait aucune recherche web. Comme il s'agissait d'une reprise, elle a aussi relu trois modifications d'une passe précédente interrompue, qui n'étaient pas encore enregistrées dans git. Elle les a gardées :
   - k07 recentrée sur les comptes 70 à 72 ;
   - « en principe » ajouté à la question de k16 ;
   - k34 créée pour les comptes 74 et 75.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a contrôlé les 32 cartes issues de la première relecture sous quatre angles :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, et PCG modifié par les règlements ANC n° 2022-06, 2024-07 et 2026-03 ;
   - l'ambiguïté pédagogique : la réponse est-elle celle qu'attendrait un correcteur du DCG, et une autre réponse juste serait-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle n'a fait aucune recherche web (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-02.cartes.json` répond « ✓ data/ue9/ue9-02.cartes.json (cartes, 30 (10 déf.)) ».

## Bilan

- **Nombre de cartes : 30.** La première relecture en avait laissé 32 ; la relecture d'exactitude en a supprimé 2.
- **Répartition : 10 cartes `def` et 20 cartes `comp`.** Les questions font de 10 à 26 mots, les réponses de 12 à 58 mots.
- **Identifiants vides.** Ils ne seront jamais réutilisés : k08, k30 et k33 viennent d'une passe antérieure, k34 et k35 de cette relecture.
- **Couverture de la fiche.**
  - Chaque item de « Définitions » a au moins une carte : #0 k01, #1 k04 et k05, #2 k13, #3 k14, #4 k22.
  - Les 15 « Règles essentielles », les 3 « Chiffres et seuils » (règles stables) et les 5 « Points de vigilance » sont tous couverts.
  - Dans « Ce qui a changé récemment », les items #0 (k27), #1 (k28) et #2 (k29) sont couverts.
- **Item de fiche sans carte : Ce qui a changé récemment#3.** Il porte sur le règlement ANC n° 2026-03 et l'intitulé du compte 6454. Sa carte k35 a été supprimée (voir plus bas). Le contrat n'impose une carte par item que pour la section « Définitions ».
- **Ni calcul ni chiffre millésimé.**
  - Les seules dates sont des dates d'entrée en vigueur de réformes : décret de 2015, règlements n° 2022-06 et n° 2024-07.
  - Les autres nombres sont des chiffres stables qui font partie de la règle : dix ans, douze mois, une fois par mois, tous les trois mois.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-02-k06 | La réponse commençait par le contexte (« La classe 6 regroupe… charges par nature ») au lieu de l'élément demandé, la répartition par comptes. Or le contrat (§ 8) veut que la réponse commence par l'élément essentiel. | Réponse réordonnée : « Les charges d'exploitation normale et courante aux comptes 60 à 65, les charges financières au compte 66 ; la classe 6 regroupe les comptes destinés à enregistrer, dans l'exercice, les charges par nature. » Le contenu reste celui de Règles essentielles#7. |
| ue9-02-k29 | Le type `comp` était inexact. La question porte sur la composition de la rubrique « Autres fonds propres », donc sur sa définition, non sur une condition, un effet ou une distinction. | Type passé de `comp` à `def`. La question et la réponse, fidèles à Ce qui a changé récemment#2 (extrait cité), ne changent pas. |
| ue9-02-k35 (ajoutée) | L'item Ce qui a changé récemment#3 (règlement ANC n° 2026-03, intitulé du compte 6454) n'avait aucune carte. | Carte créée. Q : « Quelle modification le règlement ANC n° 2026-03 apporte-t-il à l'intitulé du compte 6454 du PCG ? » R : il remplace « Pôle emploi » par « France Travail », pour les exercices ouverts à compter du 1er janvier 2027, avec application anticipée possible. Les identifiants k08, k30 et k33 n'ont pas été réutilisés. |

La première relecture n'a supprimé aucune carte. Elle a conservé les trois modifications de la passe interrompue, qu'elle a jugées fidèles à la fiche : k07, k16 et k34.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-02-k07 et ue9-02-k34 (supprimée) | Les deux cartes coupaient en deux une seule règle : les produits d'exploitation normale et courante vont aux comptes 70, 71, 72, 74 et 75. Le texte n'appuie pas cette coupure entre 70-72 et 74-75. La question de k34 (« outre les ventes et la production (comptes 70 à 72)… ») donnait la réponse de k07. k07 répétait aussi la règle « hors taxes collectées », déjà portée par k09. | Fusion dans **k07**, carte `comp` qui fait pendant à k06 pour la classe 6. Q : « Dans la classe 7 du PCG, quels comptes enregistrent les produits d'exploitation normale et courante ? » R : « Les comptes 70, 71, 72, 74 et 75 : ventes (70), production stockée (71), production immobilisée (72), subventions (74) et autres produits de gestion courante (75). » **k34 est supprimée.** | PCG au 1er janvier 2026, classe 7 (Règles essentielles#8) |
| ue9-02-k35 (supprimée) | Carte sans intérêt pour la révision. La réponse, « Pôle emploi » remplacé par « France Travail », se devine sans connaître le règlement ; ce qu'il reste à retenir est une date d'application (exercices ouverts à compter du 1er janvier 2027). La carte fait aussi doublon avec la révision du compte 6454 du plan comptable (`data/pcg/classe6b.json`), dont la note signale déjà l'écart entre l'intitulé « Cotisations à Pôle emploi » et le nom actuel de l'opérateur. Une passe antérieure l'avait supprimée pour la même raison (ancienne k30). | Supprimée. La section « Ce qui a changé récemment » reste couverte par k27, k28 et k29. | Règlement ANC n° 2026-03 du 6 mars 2026, art. 6 (Ce qui a changé récemment#3) |

Les 28 autres cartes ont été jugées exactes au 15 octobre 2026. Aucune ambiguïté n'y justifiait de retouche. Points contrôlés :
- **Code de commerce.**
  - L. 123-12 : enregistrement chronologique, inventaire au moins tous les douze mois.
  - L. 123-22 : euros et langue française, documents tenus sans blanc ni altération, conservation pendant dix ans.
  - L. 123-23 : force probante, communication en justice limitée aux cas énumérés.
  - L. 123-25 (réel simplifié) et L. 123-28 (régime micro).
  - R. 123-173 à R. 123-177, R. 123-203 et R. 123-204.
- **PCG.**
  - Art. 513-1 : le résultat.
  - Art. 1121-1 : plan de comptes commun au système de base et au système abrégé, plan de comptes minimal, subdivisions.
  - Classe 6 : comptes 60 à 65 et 66.
  - Classe 7 : produits enregistrés hors taxes collectées, TVA collectée au compte 4457.
- **Réformes.**
  - Suppression des comptes 791, 796 et 797 par le règlement n° 2022-06, et exception du logement social prévue par le règlement n° 2025-05.
  - Composition des autres fonds propres selon le règlement n° 2024-07.
  - Maintien du système abrégé.

Remarques sans retouche :
- **k06.** La carte suit fidèlement la fiche. Elle ne dit rien des dotations du compte 68 (voir « Points à reprendre dans la fiche », point 2).
- **k09.** Un correcteur accepterait aussi la subdivision 44571 ; la réponse attendue, au niveau du compte 4457, reste juste.
- **k11 et k24.** Elles se recoupent sur la dérogation de L. 123-25 (créances et dettes enregistrées à la clôture), mais leurs questions diffèrent : principe chronologique d'un côté, liste des allègements de l'autre. Les deux sont conservées.

## Recherches

Aucune recherche web n'a été faite. Plusieurs points pouvaient faire douter, mais la relecture finale de la fiche (`rapports/ue9-02.md`) les avait déjà confirmés par des recherches limitées à legifrance.gouv.fr et à anc.gouv.fr :
- les dérogations de R. 123-203 et R. 123-204 ;
- le plan de comptes minimal et les comptes en italique ;
- le contenu des classes 6 et 7 ;
- les règlements n° 2024-07, n° 2025-05 et n° 2026-03.

Les cartes ne sortent pas du texte de ces items. Le quota de recherche, partagé, a donc été épargné.

## Points à reprendre dans la fiche

1. **Partie double absente.** Aucun item ne porte sur le mécanisme de la partie double (débit et crédit, égalité des totaux), sur l'analyse des opérations en flux et en stocks ni sur la balance. Ces points figurent pourtant dans `programme.points` et dans le titre du chapitre. Les deux items rattachés à l'ancien art. 921-1 ont été retirés faute de source confirmée. Aucune carte ne peut donc porter ce cœur du chapitre. Il faudrait retrouver le fondement officiel de la partie double dans le PCG en vigueur et rétablir au moins un item.
2. **Règles essentielles#7 (classe 6).** La répartition « comptes 60 à 65 pour l'exploitation normale et courante, compte 66 pour les charges financières » paraît exhaustive. Or les dotations passent par le compte 68, ventilé en 681 (exploitation), 686 (financier) et 687 (exceptionnel). Au compte de résultat, les charges d'exploitation comprennent donc aussi le 681, et les charges financières le 686. Il faudrait compléter l'item d'après le texte de la classe 6 du PCG au 1er janvier 2026 (comptes 67, 68 et 69).
3. **Règles essentielles#14 (C. com., art. R. 123-203).** Le champ `t` parle de la « date figurant sur le relevé », alors que l'extrait cité dit « la date de l'opération figurant sur le relevé ». Il faudrait aligner `t` sur l'extrait ; la carte k26 suit déjà l'extrait.
4. **Points de vigilance#0.** Le `src` cite R. 123-173 et R. 123-177, mais l'`url` ne renvoie qu'à R. 123-173 (LEGIARTI000030927447). C'est une remarque de forme : le contenu est juste.

## Classement des exercices

Résultat du classement automatique des exercices QCM, QCM multiples et de classement du chapitre :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 17 | oui |
| `calcul` | 1 | non |
| `chiffre` | 1 | non |

Les classements ont divergé sur un exercice, noté « #4 : null / notion → chiffre ». Selon notre lecture de cette notation, l'exercice #4 n'avait reçu aucune nature d'un côté et « notion » de l'autre ; la nature retenue est « chiffre ». Seuls les 17 exercices de nature `notion` entrent dans les révisions espacées, avec les 30 cartes ci-dessus et les comptes du plan comptable. Les exercices de nature `calcul` et `chiffre` restent dans le chapitre, mais ne sont pas proposés en révision.
