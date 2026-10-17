# Cartes de notions : ue3-06 (Protection sociale : cotisations, prestations et contrôle)

16 octobre 2026. Fichier : `data/ue3/ue3-06.cartes.json`. Fiche de référence : `data/ue3/ue3-06.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les 32 premières cartes (k01 à k32) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`) et reprend à l'identique le `src` et l'`url` du premier.
2. **Relectures de fidélité.** Trois passes successives ont contrôlé les cartes au regard de la fiche, seul juge pour ces passes, sans recherche web :
   - 1re passe : 32 cartes contrôlées, 7 corrigées, 2 ajoutées (k33, k34), soit 34 cartes ;
   - 2e passe : 34 cartes contrôlées, 6 corrigées, 1 ajoutée (k35), soit 35 cartes ;
   - 3e passe : 35 cartes contrôlées, 2 corrigées, aucun ajout ni suppression.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les cartes au regard du droit en vigueur au 16 octobre 2026 : Constitution, Code de la sécurité sociale, Code du travail, Code de l'organisation judiciaire et PCG modifié. Il a vérifié trois points :
   - chaque carte est juste aujourd'hui, et pas seulement dans un cas particulier non dit ;
   - la question n'appelle qu'une seule réponse, celle qu'attendrait un correcteur du DCG ;
   - le jeu ne contient ni doublon, ni carte triviale, ni calcul, ni chiffre millésimé.

   Cette passe s'est faite en deux temps. Une première session, interrompue avant la rédaction du rapport, a corrigé 10 cartes, supprimé k06 (fusionnée dans k05) et ajouté k36 ; son état a été enregistré au commit ead9157. La reprise a relu les 35 cartes, corrigé 8 cartes (dont k14, k18, k26 et k36 une seconde fois) et rédigé ce rapport. Au total, 14 cartes existantes ont été corrigées, une supprimée et une ajoutée.
4. **Recherches.** 3 recherches WebSearch sur des sites officiels (voir « Recherches faites »).

`node validate.js data/ue3/ue3-06.cartes.json` : ✓ (35 cartes, 9 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 9 de définition (`def` : k01, k03, k04, k05, k12, k18, k22, k23, k29) et 26 de compréhension (`comp`). L'identifiant k06 reste libre et ne sera pas réutilisé.
- **Définitions** : les 4 items ont chacun au moins une carte (#0 : k01, k02 ; #1 : k03 ; #2 : k04, k33 ; #3 : k05, k07, k08).
- **Règles essentielles** : les 10 items stables ont chacun au moins une carte (#0 : k09, k10 ; #1 : k11 ; #2 : k12, k13 ; #5 : k14, k15 ; #6 : k16, k17, k34 ; #7 : k18 à k20 ; #8 : k21, k22, k24, k35, k36 ; #9 : k23 à k25 ; #10 : k26 ; #12 : k27 à k29). Les items **#3** (taux 2026), **#4** (RGDU) et **#11** (retraite de base) sont millésimés 2026 : le contrat les exclut. Certains points des items stables n'ont pas de carte :
  - **#0** : la compétence du pôle social pour l'admission à l'aide sociale et certains litiges du Code du travail ;
  - **#2** : les taux de la CSG et de la CRDS, qui seraient des chiffres à apprendre par cœur ;
  - **#9** : le salaire journalier AT du mensualisé (salaire du mois précédent divisé par 30,42), qui relève du calcul ;
  - **#10** : le détail de la condition d'affiliation (130 jours ou 910 heures) et le calendrier de la convention de 2024, qui sont des données conventionnelles temporaires.
- **Chiffres et seuils** : les 4 items sont millésimés 2026 et n'ont pas de carte.
- **Ce qui a changé récemment** : **#0** a une carte (k30). **#1** est stable mais n'a pas de carte : il ne nomme ni l'organisme ni les décisions visées et ne renvoie qu'à des numéros d'articles. **#2 à #5** sont millésimés 2026.
- **Points de vigilance** : **#0** (k25, k31) et **#2** (k32) ont des cartes ; **#1** (barème 2025 ou 2026) est millésimé.
- **Doublons.** k05 et k06 se donnaient mutuellement la réponse ; elles ont été fusionnées dans k05. Plusieurs cartes se recoupent sans faire doublon :
  - **k09 et k30** : la juridiction compétente aujourd'hui, et l'histoire de la réforme de 2019-2020 ;
  - **k25 et k31** : l'effet de la faute inexcusable, et la répartition des litiges entre le pôle social et le conseil de prud'hommes ;
  - **k21, k22 et k24** : le point de départ des IJ maladie, leur base, et la comparaison avec les IJ AT ;
  - **k15 et k19** : la prescription quinquennale en cas de travail dissimulé est rappelée dans les deux, k19 traitant de l'ensemble des conséquences.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1re | k04 | La réponse mêlait la LFSS et la compétence du législateur, qui relève d'une autre règle. | Réponse limitée à la définition de la LFSS donnée par la fiche. |
| 1re | k05 | La question donnait presque la réponse et la réponse ne citait que deux branches sur cinq. | Question sur les cinq branches ; la réponse les énumère selon la fiche (art. L. 200-2). |
| 1re | k06 | La question reprenait la réponse de k05. | Question sur la branche créée par la loi n° 2020-992 (réponse : autonomie). La carte a ensuite été supprimée par la relecture d'exactitude. |
| 1re | k11 | Question fermée et binaire (branche ou entreprise ?). | Question ouverte sur l'articulation des deux accords. |
| 1re | k13 | L'exception de la contribution patronale à la complémentaire santé (CSG-CRDS sans abattement) manquait. | Exception ajoutée ; règle de l'abattement limité à quatre plafonds reformulée. |
| 1re | k17 | L'agent n'est tenu de répondre que si le cotisant répond dans le délai. | Condition ajoutée. |
| 1re | k31 | Question fermée et binaire. | Question de distinction entre le pôle social et le conseil de prud'hommes, fidèle à Points de vigilance#0. |
| 1re | k33 (ajout) | La compétence du législateur (Définitions#2) n'avait pas de carte. | Carte `comp` sur l'article 34 de la Constitution. |
| 1re | k34 (ajout) | La durée maximale du contrôle URSSAF (Règles essentielles#6) n'avait pas de carte. | Carte `comp` : trois mois, prorogeables une fois. |
| 2e | k01 | Question alambiquée ; la réponse se terminait par une parenthèse qui répétait la source. | Question : « Selon l'alinéa 11 du Préambule… que la Nation garantit-elle à tous ? » ; la parenthèse est remplacée par le rôle de fondement constitutionnel. |
| 2e | k06 | Intitulés des branches raccourcis au-delà de la fiche. | Intitulés exacts de l'art. L. 200-2. |
| 2e | k07 | « Quel organisme » au singulier, alors que la réponse est « les URSSAF » ; l'Acoss seule pouvait être répondue. | « Quels organismes… ». |
| 2e | k15 | La formulation ne disait pas qu'on attend un délai. | « Quel est le délai de prescription… ». |
| 2e | k24 | La question admettait d'autres réponses justes (base de calcul différente, par exemple). | Question bornée au délai de carence et au taux. |
| 2e | k25 | La réponse ne rattachait pas la faute inexcusable à sa juridiction. | Ajout « Ce litige relève du tribunal judiciaire (pôle social), et non du conseil de prud'hommes » ; Points de vigilance#0 en second item de base. |
| 2e | k35 (ajout) | Les conditions d'ouverture des IJ maladie (Règles essentielles#8) n'avaient pas de carte. | Carte `comp` : 150 heures sur trois mois ou 1 015 SMIC horaires sur six mois. |
| 3e | k06 | La réponse pouvait laisser croire que l'art. L. 200-2 n'énumère que quatre branches. | Réponse présentant la branche autonomie comme cinquième branche énumérée par l'art. L. 200-2. |
| 3e | k24 | « En maladie, l'IJ est de 50 % » ne disait pas sur quelle base. | « 50 % du salaire journalier de base ». |

La 3e passe a noté qu'il ne restait plus de place pour le plafond de 360 IJ (Règles essentielles#8). La suppression de k06 par la relecture d'exactitude a libéré cette place (k36).

## Corrections de la relecture d'exactitude

Les onze premières lignes viennent de la première session, les huit dernières de la reprise.

| cible | problème | correction | source |
|---|---|---|---|
| k05 et k06 | Doublon : la question de k05 (« Outre la branche autonomie, quelles sont les quatre branches… ») donnait la réponse de k06 (« Quelle branche la loi n° 2020-992 a-t-elle créée ? »), et la réponse de k06 énumérait celle de k05. | Fusion dans k05 : « Quelles sont les cinq branches du régime général… ? ». La réponse énumère les cinq branches et rappelle que la branche autonomie a été créée par la loi n° 2020-992. **k06 est supprimée** et son identifiant n'est pas réutilisé. | CSS, art. L. 200-2 |
| k08 | « De quel régime relèvent les travailleurs indépendants… ? » : la réponse « du régime général » ne vaut pas pour tous les indépendants. Les non-salariés agricoles relèvent de la MSA ; les professions libérales conservent leurs caisses de retraite propres. Seuls les anciens ressortissants du RSI ont été transférés. | Question : « Quel régime a repris la protection sociale des travailleurs indépendants qui relevaient du régime social des indépendants (RSI), aujourd'hui supprimé ? » ; la réponse est inchangée sur le fond. | Loi n° 2017-1836 du 30 décembre 2017, art. 15 ; C. rur., art. L. 722-1 ; CSS, art. L. 640-1 |
| k09 | La question présentait le pôle social comme la juridiction du premier degré pour tout le contentieux de la sécurité sociale. Or le contentieux de la tarification AT/MP est jugé en premier et dernier ressort par une cour d'appel spécialement désignée. | « En principe, quelle juridiction… ? ». La réponse est inchangée. | C. org. jud., art. L. 311-16 ; décret n° 2018-772 du 4 septembre 2018 |
| k10 | « Avant tout recours contentieux contre une décision d'un organisme de sécurité sociale » : ce n'est pas vrai pour toutes les décisions. Les décisions d'ordre médical relèvent d'une commission médicale de recours amiable, et l'opposition à contrainte est portée directement devant le tribunal. | Question limitée aux décisions de l'URSSAF et portant aussi sur le délai. La réponse ajoute que le pôle social ne peut être saisi qu'après ce recours préalable. | CSS, art. R. 142-1, R. 142-8 et R. 133-3 |
| k13 | « Pour les revenus d'activité des salariés » : ces revenus comprennent des éléments soumis à la CSG sans abattement (contributions patronales de prévoyance, intéressement, participation). La réponse « 98,25 % » ne vaut que pour le salaire. Le « y » de la dernière phrase était ambigu. | Question : « Quelle est l'assiette de la CSG et de la CRDS dues sur le salaire d'un salarié ? ». Dernière phrase : « est en revanche soumise à la CSG-CRDS sans abattement ». | CSS, art. L. 136-1-1 |
| k14 | Les employeurs de moins de onze salariés peuvent opter pour un versement trimestriel. Les dates du 5 et du 15 ne valent que pour le versement mensuel. | « Quelle est la date limite du versement mensuel à l'URSSAF… ? ». | CSS, art. R. 243-6 et s. |
| k18 | « Qu'est-ce que le travail dissimulé ? » appelait une définition, mais la réponse n'était qu'une liste d'exemples. Le Code du travail définit le travail dissimulé par ses deux formes. | Question : « Quelles sont les deux formes de travail dissimulé définies par le Code du travail ? ». Réponse : la dissimulation d'activité et la dissimulation d'emploi salarié, avec les exemples de la seconde. | C. trav., art. L. 8221-1, L. 8221-3 et L. 8221-5 |
| k22 | Le diviseur 91,25 ne vaut que pour une paie mensuelle ; d'autres diviseurs s'appliquent selon la périodicité de la paie. | « … d'un salarié mensualisé ? ». | CSS, art. R. 323-4 |
| k26 | La réponse donnait une condition d'affiliation de « six mois au cours des 24 derniers mois (36 mois pour les plus âgés) ». C'est une donnée conventionnelle temporaire, qui n'est pas uniforme : les primo-entrants bénéficient d'une condition réduite, agréée par l'arrêté du 28 mars 2026. | « … qui justifient d'une durée minimale d'affiliation fixée par le règlement d'assurance chômage ». | Convention du 15 novembre 2024 et règlement annexé ; arrêté du 28 mars 2026 |
| k34 | La limitation à trois mois ne s'applique pas en cas de travail dissimulé, d'obstacle à contrôle, d'abus de droit, de comptabilité insuffisante ou de documentation inexploitable. | « En principe, quelle est la durée maximale… ? ». | CSS, art. L. 243-13 |
| k36 (ajout) | Le plafond de 360 IJ sur trois ans (Règles essentielles#8) n'avait pas de carte ; la suppression de k06 a libéré une place. | Carte `comp` : « Quel plafond limite le nombre d'indemnités journalières maladie… ? ». `src` et `url` copiés de l'item. | CSS, art. R. 323-1 |
| k04 | « Selon la Constitution de 1958… » avec une réponse « chaque année » : la Constitution ne prévoit pas un vote annuel. C'est la loi organique qui organise la LFSS de l'année, à côté de la LFSS rectificative et de la loi d'approbation des comptes. | Question : « Qu'est-ce que la loi de financement de la sécurité sociale (LFSS) de l'année ? ». La réponse est inchangée. | Constitution, art. 34 et 47-1 ; CSS, art. L.O. 111-3 et s. (loi organique n° 2022-354 du 14 mars 2022) |
| k14 | « supportent une majoration de retard de 5 % » est incomplet. Une majoration complémentaire, due par mois ou fraction de mois de retard, s'y ajoute. | « supportent notamment une majoration de retard de 5 % ». | CSS, art. R. 243-18 |
| k18 | La dissimulation d'emploi salarié suppose que l'employeur se soustraie intentionnellement à ses obligations. Sans l'élément intentionnel, la réponse qualifiait de travail dissimulé toute omission, même involontaire. | « La seconde suppose un manquement intentionnel de l'employeur, notamment l'absence de déclaration préalable à l'embauche… » (41 mots). | C. trav., art. L. 8221-3 et L. 8221-5 |
| k19 | Dans certains cas prévus par la loi, l'annulation des réductions et exonérations n'est que partielle. | « En principe, quelles conséquences… ? ». La réponse est inchangée. | CSS, art. L. 133-4-2 |
| k20 | « trois ans d'emprisonnement et 45 000 € d'amende » est la peine de base. Les peines sont aggravées si l'infraction vise un mineur ou une personne vulnérable, plusieurs personnes, ou en bande organisée. | « la personne physique encourt, hors circonstances aggravantes, trois ans d'emprisonnement et 45 000 € d'amende ». | C. trav., art. L. 8224-1 et L. 8224-2 |
| k21 | Le délai de carence connaît d'autres exceptions que les AT/MP et les ALD : il ne joue pas pour la prolongation d'un arrêt, ni, depuis 2024, pour l'arrêt lié à une interruption spontanée de grossesse. | « En principe, à partir de quand… ? ». La réponse est inchangée. | CSS, art. R. 323-1 ; loi n° 2023-567 du 7 juillet 2023 |
| k26 | « Quels travailleurs peuvent bénéficier de l'ARE ? » : la loi l'ouvre aussi, sous conditions, au salarié démissionnaire qui poursuit un projet de reconversion professionnelle. Ce cas n'est pas dans la fiche. | « En principe, quels travailleurs… ? ». La réponse est inchangée. | C. trav., art. L. 5422-1, II (loi n° 2018-771 du 5 septembre 2018) |
| k36 | « Les arrêts liés à une ALD ne sont pas soumis à ce plafond » pouvait faire croire à une indemnisation illimitée. Or les arrêts en ALD ont leur propre durée maximale : trois ans, ramenés à un an pour les ALD non exonérantes, pour les arrêts prescrits à compter du 15 octobre 2026. | « Ce plafond ne s'applique pas aux arrêts liés à une affection de longue durée, soumis à une durée maximale d'indemnisation propre. » | CSS, art. R. 323-1, version issue du décret n° 2026-866 du 16 septembre 2026 (recherches 1 et 3) |

Les 20 autres cartes ont été contrôlées sans changement : k01 à k03, k07, k11, k12, k15 à k17, k23 à k25, k27 à k33 et k35.
- Les chiffres présents font partie d'une règle stable : 98,25 % et quatre plafonds, 25 et 40 %, six mois de salaire, 150 heures et 1 015 SMIC horaires, 91,25 et 1,4 SMIC, 60 et 80 %, 360 IJ, 1,50 %, trente et soixante jours, trois mois.
- k32 (compte 6454 « Cotisations à France Travail ») a été vérifiée sur le règlement ANC n° 2026-03 (recherche 2).
- Le plafond de 360 IJ (k36) et le délai de carence en ALD (k21) ne sont pas modifiés par le décret n° 2026-866 (recherche 3).

## Recherches faites

Trois recherches WebSearch sur les trois autorisées. Les pages Légifrance et ameli.fr n'ont pas pu être ouvertes directement (hôtes injoignables depuis l'environnement) : seuls les extraits renvoyés par la recherche ont été lus.

1. **Décret n° 2026-866 du 16 septembre 2026** (domaines legifrance.gouv.fr, ameli.fr, service-public.fr). Le décret ramène à un an la durée maximale dérogatoire d'indemnisation des arrêts liés à une ALD non exonérante. Les ALD exonérantes (CSS, art. L. 160-14, 3° et 4°) conservent trois ans. Ces règles s'appliquent aux arrêts prescrits à compter du 15 octobre 2026. Le décret prévoit aussi une sanction des abus. Conséquence : correction de k36. Sources : [décret n° 2026-866 (Légifrance)](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054855169), [article 3 du décret](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000054855996).
2. **Règlement ANC n° 2026-03 et compte 6454** (domaines anc.gouv.fr, legifrance.gouv.fr). Le règlement remplace « Pôle emploi » par « France Travail » dans l'intitulé du compte 6454, pour les exercices ouverts à compter du 1er janvier 2027, avec application anticipée possible. Il a été homologué par l'arrêté du 12 août 2026. Le plan de comptes 2026 publié par l'ANC porte encore « Cotisations à Pôle emploi ». k32 est exacte. Sources : [règlement ANC n° 2026-03](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2026/2026%20homologu%C3%A9/2026_03-JO.pdf), [arrêté du 12 août 2026](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054791025).
3. **Article R. 323-1 du CSS après le décret n° 2026-866** (domaines legifrance.gouv.fr, ameli.fr, service-public.fr). La version en vigueur depuis le 19 septembre 2026 maintient le plafond de 360 IJ pour une période quelconque de trois ans, hors ALD. Elle fixe la durée maximale en ALD à trois ans (participation de l'assuré limitée ou supprimée) ou à un an (ALD non exonérante). Selon ameli.fr, le délai de carence en ALD ne joue que pour le premier arrêt sur trois ans. Conséquence : k21 et le plafond de k36 sont confirmés ; la phrase de k36 sur les ALD est corrigée. Sources : [CSS, art. R. 323-1 (Légifrance)](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054856818), [ameli.fr, IJ maladie du salarié](https://www.ameli.fr/assure/remboursements/indemnites-journalieres-maladie-maternite-paternite/arret-maladie-salarie).

Les autres corrections reposent sur des dispositions anciennes et stables, sans doute réel sur leur contenu. Les articles concernés sont L. 8221-3 et L. 8221-5, L. 8224-2 et L. 5422-1, II du Code du travail, et R. 142-8, R. 243-18, L. 243-13 et L. 133-4-2 du CSS.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#8 et Ce qui a changé récemment#4** (IJ maladie). Le décret n° 2026-866 du 16 septembre 2026 n'est cité que par son titre. Il faudrait écrire son contenu : pour les arrêts prescrits à compter du 15 octobre 2026, la durée maximale d'indemnisation est de trois ans en ALD exonérante et d'un an en ALD non exonérante (CSS, art. R. 323-1). Le plafond de 360 IJ sur trois ans, hors ALD, est inchangé ; cela répond au doute émis par la 3e relecture de fidélité. On peut aussi ajouter deux exceptions au délai de carence : la prolongation d'arrêt et l'interruption spontanée de grossesse (loi n° 2023-567).
2. **Règles essentielles#7** (travail dissimulé). Ajouter l'élément intentionnel : la dissimulation d'activité comme la dissimulation d'emploi salarié supposent que l'on se soustraie intentionnellement à ses obligations (C. trav., art. L. 8221-3 et L. 8221-5). Deux précisions peuvent suivre :
   - l'annulation des réductions et exonérations peut n'être que partielle dans certains cas (CSS, art. L. 133-4-2) ;
   - les peines sont aggravées en cas de circonstances aggravantes (C. trav., art. L. 8224-2).
3. **Règles essentielles#10** (ARE). Deux points :
   - « Réservée aux travailleurs involontairement privés d'emploi » est trop absolu. Le salarié démissionnaire qui poursuit un projet de reconversion professionnelle peut aussi en bénéficier, sous conditions (C. trav., art. L. 5422-1, II).
   - La condition de six mois (130 jours ou 910 heures) est une donnée conventionnelle temporaire (convention 2025-2028), qui ne vaut pas pour les primo-entrants (arrêté du 28 mars 2026). L'item est classé `stable` ; cette partie mériterait d'être signalée comme conventionnelle et datée.
4. **Règles essentielles#5** (paiement). Deux compléments :
   - la majoration complémentaire de retard, due par mois ou fraction de mois (CSS, art. R. 243-18), déjà signalée par la 2e relecture de fidélité et confirmée ici ;
   - l'option de versement trimestriel ouverte aux employeurs de moins de onze salariés (CSS, art. R. 243-6 et s.).
5. **Règles essentielles#0** (recours préalable). Le doute de la 2e relecture de fidélité est confirmé. Les décisions d'ordre médical relèvent d'une commission médicale de recours amiable (CSS, art. R. 142-8 et s.), et non de la commission de recours amiable. Préciser « décisions d'ordre non médical ».
6. **Définitions#2** (LFSS). « Chaque année » ne vient pas de la Constitution (art. 34 et 47-1) mais de la loi organique (CSS, art. L.O. 111-3 et s., loi organique n° 2022-354). Celle-ci distingue la LFSS de l'année, la LFSS rectificative et la loi d'approbation des comptes. On peut aussi reprendre « compte tenu de leurs prévisions de recettes ».

Les autres points déjà signalés par les relectures de fidélité restent à examiner :
- Ce qui a changé récemment#1, inexploitable en l'état ;
- les seuils 2026 des taux réduits (Règles essentielles#3, millésimé) ;
- la génération 1965 dans Règles essentielles#11 (millésimé).

## Classement des exercices

Le classement automatique porte sur les 20 exercices QCM, QCM multiples et classements du chapitre : 16 QCM, 3 QCM multiples et 1 classement. Les 8 exercices de calcul (`calc` : #4, #5, #7, #10, #11, #14, #18, #20) n'en font pas partie.

| nature | nombre | exercices |
|---|---|---|
| notion | 14 | #0, #1, #3, #9, #12, #13, #15, #16, #17, #22, #24, #25, #26, #27 |
| calcul | 1 | #8 |
| chiffre | 5 | #2, #6, #19, #21, #23 |

Deux désaccords entre classements ont été tranchés en faveur de `chiffre` :
- **#6** : seuil de 1,6 SMIC de la réduction générale en 2025, remplacée depuis par la RGDU ;
- **#19** : âge légal de 64 ans prévu par la réforme de 2023, dont la montée en charge est suspendue par la LFSS pour 2026.

Les exercices qui ne sont pas de nature notion sortent des révisions espacées :
- **#8** (calcul) : date d'expiration du délai de prescription des cotisations de 2022, à décompter. La règle des trois ans reste révisée par k15.
- **#2, #21 et #23** (chiffre) : PASS 2025, condition d'affiliation et durée d'indemnisation de l'ARE en 2025.

Les 14 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes. Une remarque hors du champ de cette relecture : l'explication de #24 limite l'exclusion de la prolongation de la période contradictoire au travail dissimulé, alors que la fiche (Règles essentielles#6) et k17 visent l'abus de droit et le travail illégal. Les deux sont à harmoniser.
