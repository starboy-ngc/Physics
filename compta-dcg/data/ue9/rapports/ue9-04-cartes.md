# Cartes de notions : ue9-04 (Trésorerie, charges courantes et paie)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `data/ue9/ue9-04.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Passes antérieures.** Une première série de relectures (fidélité puis exactitude) a déjà eu lieu. Elle a supprimé cinq cartes : k12, k16, k28, k31 (fusionnée dans k30) et k35. Ces identifiants restent vides.
3. **Relecture de fidélité (cette passe).** Une première relecture a comparé les 30 cartes au seul texte de la fiche. Elle a vérifié les conditions, les exceptions et le vocabulaire. Elle a corrigé quatre cartes (k08, k15, k20, k24), sans rien supprimer ni ajouter.
4. **Relecture d'exactitude (cette passe).** Une seconde relecture, indépendante, a contrôlé les 30 cartes sous quatre angles :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, Code du travail, Code de la sécurité sociale, CGI, BOFiP, PCG modifié par le règlement ANC n° 2022-06 ;
   - l'ambiguïté pédagogique : la réponse est-elle celle qu'attendrait un correcteur du DCG, et une autre réponse juste serait-elle possible ?
   - les doublons et les cartes sans intérêt, dans le chapitre et avec les cartes des autres chapitres, puisque les révisions espacées les mélangent ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a corrigé quatre cartes (k07, k08, k24, k25) et en a supprimé une (k30). Elle n'en a ajouté aucune.
5. **Recherches.** Une seule recherche WebSearch a été faite, limitée à legifrance.gouv.fr (voir « Recherches »).
6. **Validation.** `node validate.js data/ue9/ue9-04.cartes.json` répond « ✓ data/ue9/ue9-04.cartes.json (cartes, 29 (7 déf.)) ».

## Bilan

- **Nombre de cartes : 29.** Il y en avait 30 avant cette passe.
- **Répartition : 7 cartes `def` et 22 cartes `comp`.** Les questions font de 12 à 30 mots, les réponses de 19 à 70 mots.
- **Identifiants vides.** k12, k16, k28, k31 et k35 ont été supprimés par la passe antérieure, k30 par celle-ci. Ils ne seront jamais réutilisés. Aucune carte n'a été renumérotée.
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte : #0 k01, #1 k05, #2 k10, #3 k15, #4 k18, #5 k26.
  - 14 des 16 « Règles essentielles » sont couvertes.
  - Les 6 « Points de vigilance » sont tous couverts : #0 k22, #1 k07 à k09, #2 k33 et k34, #3 k11, #4 k14, #5 k03.
  - « Chiffres et seuils#0 » est couvert par k19 : une fois par mois, la moitié pour une quinzaine. Ce sont des chiffres stables qui font partie d'une règle.
  - Dans « Ce qui a changé récemment », #0 (k17) et #6 (k08) sont couverts.
- **Items de fiche sans carte.**
  - **Règles essentielles#5** (redevables de la CFE). La carte k12 doublait ue4-06-k03. Le classement de la CFE au compte 6351 reste porté par k11.
  - **Règles essentielles#13 et Ce qui a changé récemment#1** (intérêts courus, compte 1648). La carte k30 a été supprimée par cette passe (voir plus bas). Le point reste porté par ue9-08-k09 et ue9-08-k10, ainsi que par ue9-07-k14.
  - **Chiffres et seuils#1** (centralisation mensuelle des journaux auxiliaires). La règle a ses cartes en ue9-02 et ue9-09.
  - **Chiffres et seuils#2** (conservation pendant dix ans). La carte k35 était la troisième copie de cette question, avec ue9-01-k36 et ue9-02-k21.
  - **Chiffres et seuils#3 et #4** (Smic et plafond de la sécurité sociale 2026). Ils sont millésimés.
  - **Ce qui a changé récemment#2** (compte 6454 « France Travail »). La réponse se devine, et la note du compte 6454 du plan comptable signale déjà le changement d'intitulé.
  - **Ce qui a changé récemment#3** (RGDU). Il est millésimé.
  - **Ce qui a changé récemment#4** (taux individualisé du prélèvement à la source). La carte k28 doublait ue4-01-k30.
  - **Ce qui a changé récemment#5** (rédaction 2026 de l'article 1447 du CGI). Le point est porté par ue4-06-k06.
- **Ni calcul ni chiffre millésimé.** Les seuls chiffres sont stables et font partie d'une règle (un acompte pour une quinzaine égal à la moitié de la rémunération mensuelle). Les dates citées (1er janvier 2025, 1er janvier 2027) sont des dates d'application de textes. Les cartes k04 et k24 demandent le schéma d'une écriture, sans montant. Il s'agit d'un choix de comptes : le contrat n'interdit que l'écriture chiffrée.

## Corrections de la première relecture (fidélité à la fiche)

La relecture a contrôlé 30 cartes.

| cible | problème | correction |
|---|---|---|
| ue9-04-k08 | La question dit que l'article 261 C du CGI exonère de TVA « notamment les intérêts et les assurances ». Le seul item de base (Ce qui a changé récemment#6) ne parle que de l'exonération des opérations d'assurance. Pour les intérêts, la question s'appuyait donc sur une affirmation absente de sa base. | La base devient [Ce qui a changé récemment#6, Points de vigilance#1]. Points de vigilance#1 dit bien que les intérêts et agios (octroi de crédits) et les primes d'assurance sont exonérés par l'article 261 C. La question et la réponse n'ont pas changé. `src` et `url` restent ceux du premier item. |
| ue9-04-k15 | 1) La question demandait le compte des « rémunérations » sans préciser « du personnel ». Une personne qui connaît son cours pouvait aussi répondre 644 (rémunération du travail de l'exploitant), alors que la fiche ne vise que le 641. 2) Le verso énumérait les subdivisions du compte 645 comme une liste complète (URSSAF, mutuelles, caisses de retraites, autres organismes sociaux). Or il omettait le 6454, que Définitions#3 cite. | Nouvelle question (30 mots) : « Parmi les charges de personnel (compte 64 du PCG), quels comptes enregistrent les rémunérations du personnel, les charges de sécurité sociale et de prévoyance, et les remboursements de charges ? ». Dernière phrase du verso : « Le compte 645 se subdivise par organisme (URSSAF, mutuelles, caisses de retraites, etc.). » La liste n'est plus présentée comme complète, et la carte ne fait plus apprendre l'intitulé « Pôle emploi », qui change en 2027. La réponse (641, 645, 649) n'a pas changé. |
| ue9-04-k20 | Une condition manquait. Le verso disait « En sont notamment exclus les remboursements de frais professionnels ». Règles essentielles#8 limite cette exclusion aux remboursements effectués « dans les conditions fixées par arrêté ». Sans cette condition, on pouvait croire que tout remboursement de frais échappe aux cotisations. | Fin du verso : « En sont notamment exclus l'intéressement, la participation et, dans les conditions fixées par arrêté, les remboursements de frais professionnels. » Pour rester sous 70 mots, « l'exercice d'un mandat » devient « d'un mandat », sans changer le sens. La mention « quelles qu'en soient la dénomination et la qualité de celui qui les attribue » est conservée. Le verso fait 69 mots. |
| ue9-04-k24 | La réponse attendue (le compte 645 pour les charges de sécurité sociale et de prévoyance) était déjà celle de k15, qui demande les comptes 641, 645 et 649. La question reprenait en outre presque mot pour mot l'intitulé du compte demandé. La carte doublait k15 sans faire travailler l'apport de Règles essentielles#10 : la contrepartie aux comptes 431 et 437. | La carte porte désormais sur l'écriture, sans chiffre ni calcul. Question : « Selon le PCG, quelle écriture constate, lors de la paie, les charges patronales de sécurité sociale et de prévoyance ? ». Verso : « Débit du compte 645 « Charges de sécurité sociale et de prévoyance », crédit des comptes 431 « Sécurité sociale » et 437 « Autres organismes sociaux ». La charge de personnel de la période est la somme des comptes 641 et 645. » La dernière phrase a été modifiée par la relecture d'exactitude (voir plus bas). |

Le résultat transmis de la première relecture s'arrête au milieu de la correction de k24. La fin de la ligne ci-dessus a été reconstituée à partir de l'état du fichier. Si ce résultat contenait aussi des points de fiche, ils n'ont pas été reçus.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-04-k07 | **Règle présentée comme absolue.** « Les frais et commissions bancaires ne supportent la TVA que si l'établissement a opté pour la taxation » est trop large. L'exonération du 1° de l'article 261 C exclut elle-même le recouvrement des créances (c) ainsi que la garde et la gestion des titres (e). Certains services rangés au compte 627 sont donc taxables de plein droit, sans option : droits de garde (6271), location de coffres (6276). | Dernière phrase : « Les frais et commissions bancaires (compte 627) peuvent, eux, supporter la TVA, par exemple lorsque l'établissement a opté pour la taxation des opérations qu'il désigne (CGI, art. 260 B). » La phrase reste compatible avec Points de vigilance#1 et n'affirme plus que l'option est le seul cas de taxation. La première phrase, la question et la base n'ont pas changé. | CGI, art. 261 C, 1°, c et e, et art. 260 B ; plan de comptes 2026, compte 627 (Points de vigilance#1) |
| ue9-04-k08 | **Formulation à corriger.** « Selon Légifrance, cette abrogation prend effet le 1er janvier 2027 » : une carte n'a pas à attribuer une date d'effet à une base de données. Cette formule prudente se justifiait tant que la date n'était pas établie : l'article 49 de l'ordonnance n° 2025-1247 retenait le 1er septembre 2026. La recherche n° 1 confirme le report au 1er janvier 2027. | « Cette abrogation prend effet le 1er janvier 2027 ; l'exonération des opérations d'assurance figure alors aux articles L. 213-129 à L. 213-131 du CIBS. » La date figure dans la fiche (Ce qui a changé récemment#6). La carte ne cite pas l'ordonnance de report, que la fiche ne mentionne pas. | Rapport au Président de la République relatif à l'ordonnance n° 2026-671 du 27 juillet 2026 (recherche n° 1) |
| ue9-04-k24 | **Phrase en double et trop absolue.** Depuis la première relecture, le verso finissait par « La charge de personnel de la période est la somme des comptes 641 et 645 ». C'était mot pour mot la dernière phrase de k25. Cette phrase n'est en outre exacte que pour le coût de la paie : le compte 64 comprend aussi les comptes 644, 646, 647 et 648, diminués du compte 649. | La phrase est remplacée par la répartition des cotisations entre les deux comptes crédités : « Le compte 431 reçoit les cotisations dues à l'URSSAF, le compte 437 celles de la retraite complémentaire et de la prévoyance. » La base devient [Règles essentielles#10, Règles essentielles#9]. Règles essentielles#9 donne cette répartition. `src` et `url` sont inchangés. | Plan de comptes 2026, comptes 431, 437 et 645 (Règles essentielles#9 et #10) |
| ue9-04-k25 | **Vrai seulement dans le cas de la paie.** « La charge de personnel de la période est la somme des comptes 641 et 645 » laisse croire que le compte 64 se limite à ces deux comptes. Or Définitions#3 cite le compte 649, et le plan de comptes comprend aussi les comptes 644, 646, 647 et 648. | « Pour l'employeur, la paie coûte donc le salaire brut (641) augmenté des charges patronales (645). » La carte garde la règle de la fiche, mais la limite à la paie. Les cotisations salariales y sont comprises dans le brut et ne sont pas une charge supplémentaire. | Plan de comptes 2026, compte 64 (Définitions#3, Règles essentielles#10) |
| ue9-04-k30 (supprimée) | **Doublon avec un autre chapitre.** « Pour quelle raison rattache-t-on à l'exercice les intérêts courus non échus d'un emprunt bancaire ? » avait la même réponse que ue9-08-k09 : charges de l'exercice indépendamment de leur date de paiement, compte 1648, avant 2025 : 16884. Le compte 1648 a déjà quatre autres cartes : ue9-08-k10, ue9-07-k14, ue6-05-k17 et ue6-06-k19. Les intérêts courus relèvent de la clôture et du chapitre ue9-08, dont le plan les cite. Le programme de ce chapitre ne vise que les échéances d'emprunt. | Supprimée, sans renumérotation. Les échéances d'emprunt restent couvertes ici par k29. | C. com., art. L. 123-13 ; plan de comptes 2026, compte 1648 (Règles essentielles#13, Ce qui a changé récemment#1) |

Les corrections de la première relecture ont été revues et jugées exactes. Pour k24, seule la dernière phrase a été reprise (voir le tableau).

Les 25 cartes que cette relecture n'a pas retouchées ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche : k01 à k06, k09 à k11, k13 à k15, k17 à k23, k26, k27, k29 et k32 à k34. Points contrôlés :

- **Code de commerce.** Art. L. 123-13 ; R. 123-174 (opération par opération et jour par jour, pièce justificative) ; R. 123-176 (journaux auxiliaires) ; R. 123-177 (justification des postes du bilan) ; R. 123-203 (date du relevé, réservée aux personnes physiques des art. L. 123-25 et L. 123-28).
- **Code du travail.** Art. L. 3242-1 (paiement mensuel, acompte pour une quinzaine, salariés exclus) et L. 3243-2 (bulletin de paie, remise électronique sauf opposition).
- **Code de la sécurité sociale.** Art. L. 242-1 et L. 136-1-1 (revenus d'activité ; frais professionnels, intéressement et participation hors assiette).
- **CGI.** Art. 204 A et 1671 (retenue à la source) ; art. 260 B et 261 C (en vigueur jusqu'au 31 décembre 2026) ; art. 1400 et 1415 (taxe foncière due en principe par le propriétaire, ou par l'usufruitier, d'après les faits au 1er janvier).
- **Plan de comptes 2026.** Comptes 164, 421, 425, 431, 437, 4421, 444, 44566, 512, 53, 58, 61/62, 63, 6351, 63512, 641, 645, 649, 658, 6582 (avant 2025 : 6712), 661, 6611, 6616, 627 et 695.

Cartes examinées et conservées :

- **k33 et ue9-09-k21.** Les deux cartes posent presque la même question : quelles opérations enregistrer lors d'un rapprochement bancaire ? La carte est pourtant conservée. Le rapprochement bancaire figure dans les points du programme de ce chapitre (`programme.points`) comme dans le plan de ue9-09. Le chapitre ue9-09 est relu en parallèle : supprimer la carte des deux côtés ferait disparaître la notion. Ce doublon est à trancher une fois les deux chapitres arrêtés : il faudra garder une seule des deux cartes.
- **k29** (composition de l'échéance d'un emprunt). Elle recoupe ue9-08-k01 et ue9-08-k08. Elle est conservée, parce qu'elle porte sur un point du programme de ce chapitre (opérations de financement : échéances d'emprunt). Sa question (de quoi se compose l'échéance) diffère de celle de ue9-08-k08 (quelle part est une charge).
- **k02 et k03.** Elles se recoupent sur la dérogation de l'article R. 123-203. k02 demande le principe (« En principe »), k03 qui bénéficie de la dérogation.
- **k20 et k21.** Elles reposent toutes deux sur Règles essentielles#8. k20 demande l'assiette, k21 pourquoi les frais professionnels en sortent : ils ne sont pas un revenu d'activité, alors que l'intéressement et la participation sont exclus par une disposition expresse.
- **k26 et k27.** k26 définit le prélèvement à la source, k27 explique pourquoi il n'est pas une charge de l'employeur.
- **k06, k07 et k09.** Elles citent les articles 260 B et 261 C du CGI. C'est exact au 15 octobre 2026. Les anciennes références au CGI resteront en outre utilisables jusqu'au 30 juin 2028 (recherche n° 1). Il faudra reprendre ces références en même temps que la fiche.

## Recherches

Une seule recherche WebSearch a été faite, limitée à legifrance.gouv.fr.

1. **« ordonnance n° 2026-671 du 27 juillet 2026 report entrée en vigueur recodification TVA 1er janvier 2027 »** (legifrance.gouv.fr).
   - Résultats : l'[ordonnance n° 2026-671 du 27 juillet 2026 portant divers ajustements du code des impositions sur les biens et services](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054497160), son [rapport au Président de la République](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054497139) et son [article 17](https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000054497326).
   - Le rapport indique « le décalage du 1er septembre 2026 au 1er janvier 2027 de l'entrée en vigueur du transfert des dispositions régissant la TVA au sein du CIBS ». Motif : la coïncidence avec le passage obligatoire à la facturation électronique.
   - Le rapport reporte aussi du 31 décembre 2027 au 30 juin 2028 la date jusqu'à laquelle les anciennes références au CGI peuvent être utilisées.
   - L'article 17 maintient l'opposabilité de la doctrine administrative relative aux dispositions de TVA transférées (LPF, art. L. 80 A et L. 80 B).
   - Conclusion : la date du 1er janvier 2027 de k08 est confirmée, et la mention « Selon Légifrance » est retirée. Au 15 octobre 2026, les articles 260 B et 261 C du CGI restent applicables (k06, k07, k09). L'article de l'ordonnance qui fixe la nouvelle date n'a pas été restitué. Une table de concordance de Légifrance renvoie encore au 1er septembre 2026, parce qu'elle reprend l'ordonnance n° 2025-1247.

Aucune autre recherche n'a été jugée nécessaire :

- **k07.** Les exclusions du 1° de l'article 261 C (recouvrement des créances ; garde et gestion des titres) relèvent du texte constant du CGI. La correction de k07 se borne à ne plus présenter l'option comme le seul cas de taxation.
- **Autres points.** Ils relèvent de textes constants (Code de commerce, Code du travail, articles 1400 et 1415 du CGI) ou du plan de comptes 2026. Ils ont été vérifiés pour la fiche (rapport `ue9-04.md`) et dans `FAITS-CONFIRMES.md`.
- **Passe antérieure.** Elle avait fait une recherche sur l'ordonnance n° 2025-1247 et ses articles 9 et 49 (legifrance.gouv.fr). Ses résultats restent valables.

## Points à reprendre dans la fiche

1. **Ce qui a changé récemment#6 (recodification de la TVA).**
   - « Légifrance fixe au 1er janvier 2027 l'abrogation » est à reformuler : Légifrance publie le droit, il ne fixe pas de date.
   - Le report du 1er septembre 2026 (art. 49 de l'ordonnance n° 2025-1247) au 1er janvier 2027 résulte de l'ordonnance n° 2026-671 du 27 juillet 2026. Son rapport au Président de la République le confirme (JORFTEXT000054497139, recherche n° 1).
   - Il faudrait ajouter cette ordonnance à l'item et à la liste des textes, ainsi que la tolérance d'usage des anciennes références au CGI jusqu'au 30 juin 2028.
   - Le point correspondant de `POINTS-OUVERTS.md` (ue9-04, calendrier) peut être mis à jour. Seul le numéro de l'article qui fixe la date reste à confirmer (art. 19, I, selon les tables de concordance citées par la passe antérieure).
2. **Points de vigilance#1 (frais bancaires et TVA).** « Ils ne supportent la TVA que si l'établissement a opté pour la taxation (CGI, art. 260 B) » est trop absolu. Le 1° de l'article 261 C exclut de l'exonération le recouvrement des créances (c) ainsi que la garde et la gestion des titres (e). Les droits de garde (6271) et la location de coffres (6276) sont donc taxables sans option. Il faudrait écrire : « peuvent supporter la TVA, notamment lorsque l'établissement a opté… », avec un extrait de l'article à l'appui. La carte k07 a été corrigée en conséquence.
3. **Règles essentielles#10 (charges patronales).** « La charge de personnel de la période est la somme des comptes 641 et 645 » n'est exact que pour le coût de la paie. Le compte 64 comprend aussi les comptes 644, 646, 647 et 648, diminués du compte 649 que Définitions#3 cite. Il faudrait écrire « le coût de la paie pour l'employeur (salaire brut et charges patronales) est la somme des comptes 641 et 645 ». Les cartes k24 et k25 ont été corrigées en conséquence.
4. **Points de vigilance#2 (rapprochement).** Ce point vient de la passe antérieure et n'a pas été corrigé. « Seules les opérations connues par le relevé et absentes de la comptabilité sont enregistrées » est trop absolu : lors du rapprochement, l'entreprise corrige aussi ses propres erreurs d'enregistrement. Il faut retirer « Seules ». La carte k33 ne reprend pas ce mot.
5. **Règles essentielles#2 et #3, Points de vigilance#1 et liste des textes (CGI, art. 260 B et 261 C).** Ces références restent exactes jusqu'au 31 décembre 2026. À compter du 1er janvier 2027, il faudra les remplacer par celles du CIBS. Les numéros ne sont connus que pour l'assurance (art. L. 213-129 à L. 213-131). Les cartes k06, k07 et k09, qui copient ces `src`, seront à reprendre en même temps.
6. **Définitions#3 (compte 6454 « Pôle emploi »).** L'intitulé est exact pour le plan de comptes 2026. Un renvoi à Ce qui a changé récemment#2 serait utile : « France Travail » pour les exercices ouverts à compter du 1er janvier 2027.

## Classement des exercices

Le classement automatique porte sur les 15 exercices `qcm`, `multi` et `tri` du chapitre : 12 `qcm`, 3 `multi` et aucun `tri`. Le chapitre compte 24 exercices.

| nature | nombre | exercices (index dans `exercices`) | révisions espacées |
|---|---|---|---|
| `notion` | 13 | n° 4, 7, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20 et 21 | oui |
| `calcul` | 2 | n° 18 (annuité d'un emprunt à amortissements constants) et n° 22 (solde rapproché du compte 512) | non |
| `chiffre` | 0 | — | non |

Aucun désaccord n'a été relevé. Les natures enregistrées dans `data/ue9/ue9-04.json` concordent avec ce classement. Seuls les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 29 cartes et les comptes du plan comptable.
