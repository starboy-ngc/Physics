# Cartes de notions : ue9-02 (Le plan comptable et la partie double)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `data/ue9/ue9-02.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé les 30 cartes au seul texte de la fiche (champs `t` et `cite`). Elle a vérifié que chaque carte reprenait les mêmes conditions, les mêmes exceptions et le même vocabulaire. Elle a corrigé trois questions (k04, k05, k26), sans rien supprimer ni ajouter, et n'a fait aucune recherche web.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a contrôlé les 30 cartes sous quatre angles :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, Code civil, PCG modifié par les règlements ANC n° 2022-06, n° 2024-07 et n° 2026-03 ;
   - l'ambiguïté pédagogique : la réponse est-elle celle qu'attendrait un correcteur du DCG, et une autre réponse juste serait-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a corrigé deux cartes (k06, k07). Elle n'en a ni supprimé ni ajouté.
4. **Recherches.** Aucune recherche web n'a été faite pendant ces deux relectures (voir « Recherches »).
5. **Validation.** `node validate.js data/ue9/ue9-02.cartes.json` répond « ✓ data/ue9/ue9-02.cartes.json (cartes, 30 (10 déf.)) ».

## Bilan

- **Nombre de cartes : 30**, comme avant les deux relectures.
- **Répartition : 10 cartes `def` et 20 cartes `comp`.** Les questions font de 10 à 28 mots, les réponses de 12 à 58 mots.
- **Identifiants vides.** k08, k30, k33, k34 et k35 ont été supprimés par des passes antérieures. Ils ne seront jamais réutilisés. Aucune carte n'a été renumérotée.
- **Couverture de la fiche.**
  - Chaque item de « Définitions » a au moins une carte : #0 k01, #1 k04 et k05, #2 k13, #3 k14, #4 k22.
  - Les 15 « Règles essentielles », les 3 « Chiffres et seuils » et les 5 « Points de vigilance » sont tous couverts. Les « Chiffres et seuils » sont des chiffres stables qui font partie d'une règle : une fois par mois, tous les trois mois, douze mois, dix ans.
  - Dans « Ce qui a changé récemment », les items #0 (k27), #1 (k28) et #2 (k29) sont couverts.
- **Item de fiche sans carte : Ce qui a changé récemment#3.** Cet item porte sur le règlement ANC n° 2026-03 et l'intitulé du compte 6454 (« France Travail »). Deux passes antérieures ont supprimé la carte qui le couvrait (ancienne k30, puis k35), pour deux raisons :
  - la réponse se devine ;
  - la carte ferait doublon avec la révision du compte 6454 du plan comptable.

  Le contrat n'impose une carte par item que pour la section « Définitions ».
- **Ni calcul ni chiffre millésimé.** Les seules dates sont des dates d'application de réformes : 1er janvier 2016 pour le décret n° 2015-903, et les règlements n° 2022-06 et n° 2024-07.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-02-k04 | La question « Quels comptes regroupent les classes 1, 2 et 3… ? » est ambiguë en français. On peut la lire comme « quels comptes regroupent les classes », soit l'inverse du sens voulu. La réponse attendue est une catégorie de comptes par classe. | Nouvelle question : « Quelles catégories de comptes les classes 1, 2 et 3 du plan de comptes du PCG regroupent-elles ? ». La réponse, fidèle à Définitions#1, n'a pas changé. |
| ue9-02-k05 | Même ambiguïté que k04, avec « Quels comptes regroupent les classes 4, 5, 6 et 7… ? ». | Nouvelle question : « Quelles catégories de comptes les classes 4, 5, 6 et 7 du plan de comptes du PCG regroupent-elles ? ». La réponse n'a pas changé. |
| ue9-02-k26 | La question « à quelle date… peuvent-ils enregistrer leurs encaissements et paiements ? » admettait une autre réponse juste. Le principe (la date de l'opération, jour par jour) y répondait aussi, pas seulement la dérogation de R. 123-203. | Nouvelle question : « Selon le Code de commerce, quelle date dérogatoire les commerçants personnes physiques au réel simplifié ou au régime micro peuvent-ils retenir pour enregistrer leurs encaissements et paiements ? » (28 mots). La réponse n'a pas changé : la date de l'opération figurant sur le relevé de l'établissement de crédit. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-02-k06 | La question « Comment la classe 6 du PCG répartit-elle les charges d'exploitation normale et courante et les charges financières ? » appelait une répartition complète. La réponse, « comptes 60 à 65 » et « compte 66 », est alors incomplète. Les dotations passent par le compte 68 : 681 pour l'exploitation, 686 pour le financier. Au compte de résultat, les charges d'exploitation comprennent donc aussi le 681, et les charges financières le 686. Un correcteur du DCG accepterait « 60 à 65 et 681 ; 66 et 686 », réponse plus juste que celle de la carte. | La question part maintenant du compte. Q : « Dans la classe 6 du PCG, quelles charges les comptes 60 à 65, d'une part, et le compte 66, d'autre part, enregistrent-ils ? ». R : « **Comptes 60 à 65 : les charges d'exploitation normale et courante ; compte 66 : les charges financières.** La classe 6 regroupe les comptes destinés à enregistrer, dans l'exercice, les charges par nature. » Dans ce sens, l'énoncé est exact sans être exhaustif, et il reste fidèle à Règles essentielles#7, sans rien ajouter à la fiche. | PCG au 1er janvier 2026, classe 6 (Règles essentielles#7) ; structure du compte 68 du plan de comptes (681, 686, 687) |
| ue9-02-k07 | Même défaut que k06, pour les produits. La question « quels comptes enregistrent les produits d'exploitation normale et courante ? » appelait une liste fermée : 70, 71, 72, 74 et 75. Or les reprises sur amortissements, dépréciations et provisions d'exploitation (compte 781) sont aussi des produits d'exploitation. | La question part maintenant des comptes. Q : « Selon le PCG, quelle catégorie de produits les comptes 70, 71, 72, 74 et 75 de la classe 7 enregistrent-ils ? ». R : « **Les produits d'exploitation normale et courante** : ventes (70), production stockée (71), production immobilisée (72), subventions (74) et autres produits de gestion courante (75). » La carte reste portée par Règles essentielles#8 et fait toujours pendant à k06. | PCG au 1er janvier 2026, classe 7 (Règles essentielles#8) ; structure du compte 78 du plan de comptes (781, 786, 787) |

Les 28 autres cartes ont été jugées exactes au 15 octobre 2026. Aucune ambiguïté n'y justifiait de retouche. Points contrôlés :

- **Code de commerce.**
  - L. 123-12 : enregistrement chronologique (k11), inventaire au moins tous les douze mois (k22).
  - L. 123-22 : euros et langue française, documents tenus sans blanc ni altération (k20), conservation pendant dix ans (k21).
  - L. 123-23 : force probante (k31), communication en justice limitée aux affaires de succession, de communauté et de partage de société, et aux procédures de redressement ou de liquidation judiciaires (k32).
  - L. 123-25 : régime réel simplifié (k24). La dérogation porte bien sur les alinéas 1 et 3 de L. 123-12.
  - L. 123-28 : régime micro de l'article 50-0 du CGI (k25). Le texte de la carte suit celui de l'article : livre des recettes, et registre des achats pour les activités de vente ou de logement.
  - R. 123-173 : livre-journal et grand livre obligatoires, documents électroniques, fin du livre d'inventaire obligatoire depuis le décret n° 2015-903 (k12, k17).
  - R. 123-174 : origine, contenu et imputation de chaque donnée, pièce justificative (k18) ; pièce récapitulative unique (k19).
  - R. 123-175 à R. 123-177 (k13 à k16, k22, k23).
  - R. 123-203 (k26) et R. 123-204 (k16).
- **PCG.**
  - Art. 513-1 : le résultat (k10).
  - Art. 1121-1 : plan de comptes commun aux deux systèmes, plan de comptes minimal, subdivisions (k01 à k03) ; intitulés des classes 1 à 7 (k04, k05).
  - Produits enregistrés hors taxes collectées, TVA collectée au compte 4457 (k09).
- **Réformes.**
  - Suppression des comptes 791, 796 et 797 par le règlement n° 2022-06 (k28).
  - Maintien du système abrégé (k27). C'est le système développé qui a disparu.
  - Composition des autres fonds propres selon le règlement n° 2024-07 (k29).

Remarques sans retouche :

- **k09.** Un correcteur accepterait aussi la subdivision 44571. La réponse attendue, au niveau du compte 4457, reste juste.
- **k11 et k24.** Elles se recoupent sur la dérogation de L. 123-25 (créances et dettes enregistrées à la clôture). Leurs questions diffèrent toutefois : le principe chronologique pour k11, la liste des allègements pour k24. Les deux sont conservées.
- **k31.** Le Code civil (art. 1378) donne aussi force probante aux registres des professionnels contre leur auteur. La question, limitée au Code de commerce, exclut cette autre réponse.
- **k01 et k27.** Toutes deux rappellent que le plan de comptes est commun au système de base et au système abrégé. Leurs questions diffèrent : définition du plan de comptes pour k01, sort du système abrégé pour k27. Ce n'est pas un doublon.

## Recherches

Aucune recherche web n'a été faite.

- **Première relecture.** La consigne excluait toute recherche : seul le texte de la fiche servait de juge.
- **Relecture d'exactitude.** Le seul doute de fond portait sur la répartition des comptes des classes 6 et 7 (k06, k07). Il a été levé sans recherche : les questions partent maintenant des comptes, ce qui rend les réponses exactes quel que soit le libellé exact du PCG sur les comptes 68 et 78.
- **Points déjà confirmés.** Les autres points sensibles avaient été confirmés par la relecture finale de la fiche (`rapports/ue9-02.md`), avec des recherches limitées à legifrance.gouv.fr et à anc.gouv.fr :
  - les dérogations de R. 123-203 et R. 123-204 ;
  - le plan de comptes minimal et les comptes en italique ;
  - le contenu des classes 6 et 7 ;
  - les règlements n° 2024-07, n° 2025-05 et n° 2026-03.

Le quota de recherche, partagé, a donc été épargné.

## Points à reprendre dans la fiche

1. **Partie double absente.** La fiche ne contient rien sur la partie double, qui figure pourtant dans le titre du chapitre et dans `programme.points` : « le mécanisme de la partie double », « analyse des opérations en flux et en stocks », contrôles par la balance. Aucun item ne porte sur le débit et le crédit, l'égalité des débits et des crédits ou la balance. Aucune carte ne peut couvrir ces notions tant que la fiche n'est pas complétée. Les exercices du chapitre, eux, les traitent (sens des soldes, balance équilibrée).
2. **Règles essentielles#7 (classe 6) et #8 (classe 7).** Les répartitions « comptes 60 à 65 pour l'exploitation, compte 66 pour le financier » et « comptes 70, 71, 72, 74 et 75 pour les produits d'exploitation » paraissent exhaustives. Elles omettent les dotations (681, 686, 687) et les reprises (781, 786, 787). Il faudrait compléter ces deux items d'après le texte des classes 6 et 7 du PCG au 1er janvier 2026, en citant ce texte mot pour mot (comptes 67 à 69 et 77 à 79). Les cartes k06 et k07 ont été tournées pour rester exactes en attendant.
3. **Ce qui a changé récemment#3** (règlement ANC n° 2026-03, compte 6454 « France Travail »). L'item est juste mais n'a pas de carte, par choix (voir « Bilan »). Il n'y a rien à corriger dans la fiche ; ce point est signalé pour mémoire.
4. **Règles essentielles#14 (C. com., art. R. 123-203).** Le champ `t` parle de la « date figurant sur le relevé », alors que l'extrait cité dit « la date de l'opération figurant sur le relevé ». Il faudrait aligner `t` sur l'extrait. La carte k26 suit déjà l'extrait.
5. **Points de vigilance#0.** Le `src` cite R. 123-173 et R. 123-177, mais l'`url` ne renvoie qu'à R. 123-173 (LEGIARTI000030927447). C'est une remarque de forme : le contenu est juste.

## Classement des exercices

Voici le résultat du classement automatique des exercices QCM, QCM multiples et de classement du chapitre.

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 11 | oui |
| `calcul` | 2 | non |
| `chiffre` | 10 | non |

Douze exercices ont donné lieu à un désaccord. La notation « a / b → c » se lit ainsi : les deux classements ont proposé a et b (`null` : aucune nature proposée), et c est la nature retenue.

| exercice | classements | nature retenue |
|---|---|---|
| #4, #5, #6, #9, #12 | notion / null | chiffre |
| #10 | calcul / notion | calcul |
| #15 | notion / calcul | calcul |
| #19, #20, #21, #22, #23 | null / notion | chiffre |

Seuls les exercices de nature `notion` entrent dans les révisions espacées, avec les 30 cartes ci-dessus et les comptes du plan comptable. Les exercices de nature `calcul` et `chiffre` restent dans le chapitre, mais ne sont pas proposés en révision.

**Réserve.** Ce résultat ne concorde pas avec le fichier `data/ue9/ue9-02.json` actuel. Ce fichier compte 24 exercices : 18 QCM, QCM multiples et classements, ainsi que 6 écritures ou calculs. Leurs natures enregistrées sont 17 `notion` et 7 `calcul`, et aucune n'est `chiffre`. Plusieurs natures retenues contredisent aussi la définition du contrat (« `chiffre` : rappel d'un chiffre millésimé ») :

- **#4, #5, #6, #9 et #12** sont des écritures ou des calculs chiffrés. Ils relèvent de `calcul`.
- **#19 à #23** portent sur le fonctionnement des comptes, les mentions du livre-journal, les journaux auxiliaires et le classement d'un solde. Ils relèvent de `notion`.
- **#10** (le compte 44566 est une subdivision de…) relève de `notion`, non de `calcul`.

Le chapitre ne contient aucun chiffre millésimé. Il faudrait revérifier la numérotation des exercices utilisée par le classement avant d'écrire ces natures dans le chapitre.
