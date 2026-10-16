# Cartes de notions : ue9-04 (Trésorerie, charges courantes et paie)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-04.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle a contrôlé 35 cartes et en a corrigé quatre (k04, k17, k20, k21). Elle n'en a ni supprimé ni ajouté. Elle n'a fait aucune recherche web.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, Code du travail, Code de la sécurité sociale, CGI, BOFiP, PCG modifié par le règlement ANC n° 2022-06) ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt, dans le chapitre et avec les cartes des autres chapitres, puisque les révisions espacées les mélangent.

   Elle a aussi vérifié qu'aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Une seule recherche a été faite sur un site officiel (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-04.cartes.json` : ✓ (30 cartes, 7 déf.).

## Bilan

- **Nombre de cartes : 30.** Il y en avait 35 après la première relecture. La seconde relecture en a supprimé cinq (k12, k16, k28, k31 fusionnée dans k30, k35). Elle n'en a ajouté aucune. Rien n'a été renuméroté : les identifiants supprimés restent vides.
- **Répartition : 7 cartes `def` et 23 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte.
  - 15 des 16 items de « Règles essentielles » sont couverts.
  - 3 des 7 items de « Ce qui a changé récemment » sont couverts (#0, #1 et #6).
  - Les 6 « Points de vigilance » sont tous couverts.
- **Items de fiche sans carte :**
  - **Règles essentielles#5** (redevables de la CFE). La carte k12 doublait ue4-06-k03 mot pour mot. Le traitement comptable de la CFE (compte 6351) reste porté par k11.
  - **Chiffres et seuils#1** (centralisation mensuelle des journaux auxiliaires). La règle a déjà ses cartes en ue9-02 et ue9-09.
  - **Chiffres et seuils#2** (conservation pendant dix ans). La carte k35 était la troisième copie de cette question (ue9-01-k36, ue9-02-k21).
  - **Chiffres et seuils#3 et #4** (Smic et plafond de la sécurité sociale 2026). Ils sont millésimés.
  - **Ce qui a changé récemment#2** (règlement ANC n° 2026-03, intitulé du compte 6454). La carte k16 a été supprimée pour la raison retenue en ue9-02 (k35).
  - **Ce qui a changé récemment#3** (RGDU). Il est millésimé.
  - **Ce qui a changé récemment#4** (taux individualisé du prélèvement à la source). La carte k28 doublait ue4-01-k30 et n'avait aucun angle comptable.
  - **Ce qui a changé récemment#5** (rédaction 2026 de l'article 1447 du CGI). Le point est porté par ue4-06-k06.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres restants sont stables et font partie d'une règle : un acompte pour une quinzaine égal à la moitié de la rémunération mensuelle. Les dates citées (1er janvier 2025, 1er janvier 2027) sont des dates d'application de textes.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-04-k04 | La question parlait d'un virement « entre la caisse et la banque », mais la réponse ne donnait que les écritures d'un virement de la caisse vers la banque. Pour un virement de la banque vers la caisse, les débits et crédits sont inversés, donc la réponse devenait fausse. | La question vise la règle générale de la fiche (Règles essentielles#1) : « virement entre deux comptes de trésorerie tenus dans des journaux auxiliaires différents ». La réponse commence par le compte 58 « Virements internes » et précise ensuite : « Pour un virement de la caisse vers la banque : débit 58 / crédit 53 au journal de caisse, puis débit 512 / crédit 58 au journal de banque ; le compte 58 est soldé une fois les deux écritures passées. » |
| ue9-04-k17 | La réponse disait que le règlement 2022-06 avait retiré « la technique » du transfert de charges de la liste des produits. La fiche dit qu'il retire « les transferts de charges » de la liste des produits de l'article 512-1. | La réponse reprend le texte de la fiche : « le règlement ANC n° 2022-06 a retiré les transferts de charges de la liste des produits de l'article 512-1 ». |
| ue9-04-k20 | La réponse donnait l'assiette des cotisations (« toutes les sommes… ») sans les exclusions que Règles essentielles#8 indique. Sans elles, on peut croire que toutes les sommes versées sont soumises à cotisations. | Phrase ajoutée, tirée de Règles essentielles#8 : « En sont notamment exclus les remboursements de frais professionnels, l'intéressement et la participation. » Le début a été légèrement condensé (« toutes les sommes, avantages et accessoires »), sans rien perdre : la mention « de l'exercice d'un mandat ou d'une fonction élective » reste. La réponse fait 67 mots. |
| ue9-04-k21 | La question « quelles sommes ne constituent pas un revenu d'activité » appelait plusieurs réponses. On pouvait citer l'intéressement ou la participation, que l'article L. 242-1 exclut aussi de l'assiette, alors que la réponse attendue ne visait que les frais professionnels. La question soufflait aussi la condition « dans les conditions fixées par arrêté ». | La question devient une question de raison : « pourquoi les remboursements de frais professionnels, dans les conditions fixées par arrêté, échappent-ils aux cotisations de sécurité sociale ? ». Réponse : « Parce qu'ils ne constituent pas un revenu d'activité, alors que les cotisations de sécurité sociale sont calculées sur les revenus d'activité retenus pour l'assiette de la CSG. L'article L. 242-1 exclut en outre de cette assiette notamment l'intéressement et la participation. » |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-04-k04 | **Doublon avec k01.** Depuis la première relecture, la question demandait seulement « quel compte sert de passage » pour un virement interne. La réponse, « 58 « Virements internes » », était déjà celle de k01, qui demande les numéros des comptes Banques, Caisse et Virements internes. La carte ne faisait donc plus travailler le mécanisme, qui est ce que le DCG évalue. | La question porte désormais sur le mécanisme, avec un sens de virement fixé pour que la réponse soit unique : « Comment enregistre-t-on un virement de fonds de la caisse vers la banque lorsque chacune est tenue dans son propre journal auxiliaire ? ». Verso : passage par le compte 58 ; débit 58 / crédit 53 au journal de caisse, puis débit 512 / crédit 58 au journal de banque ; le compte 58 est soldé une fois les deux écritures passées. | C. com., art. R. 123-176 ; plan de comptes 2026, compte 58 (Règles essentielles#1) |
| ue9-04-k08 | **Doublon et formulation inexacte.** La question (« dans quel code l'ordonnance n° 2025-1247 transfère-t-elle la TVA ? ») reprenait ue9-03-k34 et ue4-05-k33. Le verso disait aussi que « Légifrance fixe » la date d'abrogation : une base de données publie le droit, elle ne fixe aucune date. | La carte porte sur ce que la réforme change pour ce chapitre, c'est-à-dire l'article 261 C du CGI, qui fonde les exonérations des intérêts et des assurances. Question : « Que devient, avec l'ordonnance n° 2025-1247 du 17 décembre 2025, l'article 261 C du CGI, qui exonère de TVA notamment les intérêts et les assurances ? ». Verso : il est abrogé par l'article 9 de l'ordonnance, qui transfère la TVA au livre II du CIBS. « Selon Légifrance, cette abrogation prend effet le 1er janvier 2027. » L'exonération des opérations d'assurance figure alors aux articles L. 213-129 à L. 213-131 du CIBS. | Ordonnance n° 2025-1247, art. 9 et 49 ; recherche n° 1 |
| ue9-04-k13 | **Règle présentée comme absolue.** L'article 1400 du CGI prévoit des cas où la taxe foncière n'est pas due par le propriétaire : emphytéose, bail à construction, etc. La fiche cite elle-même la réserve des articles 1403 et 1404. | La question délimite son champ : « Selon le CGI, qui doit **en principe** la taxe foncière sur une propriété bâtie ? ». Le verso, fidèle à la fiche, est inchangé. | CGI, art. 1400 (« Sous réserve des dispositions des articles 1403 et 1404… ») |
| ue9-04-k15 | **Intitulé appelé à changer.** Le verso énumérait les subdivisions du compte 645, dont « 6454 Pôle emploi ». C'est bien l'intitulé du plan de comptes 2026, mais il devient « France Travail » pour les exercices ouverts à compter du 1er janvier 2027 (règlement ANC n° 2026-03). La carte, revue pendant des mois, aurait vite fait retenir un intitulé périmé. Ces numéros n'étaient d'ailleurs pas demandés par la question. | La phrase devient « Le compte 645 se subdivise par organisme : URSSAF, mutuelles, caisses de retraites, autres organismes sociaux. » La réponse à la question (641, 645, 649) est inchangée. | Plan de comptes 2026, compte 64 (Définitions#3) ; règlement ANC n° 2026-03 (Ce qui a changé récemment#2) |
| ue9-04-k17 | **Doublon avec k15.** La question (« dans quel compte enregistre-t-on les remboursements de charges de personnel ? ») avait pour réponse 649, déjà donnée par k15, qui demande les comptes des rémunérations, des charges sociales et des remboursements. | La carte porte sur le changement lui-même : « Pour les exercices ouverts depuis le 1er janvier 2025, pourquoi un remboursement de charges de personnel ne passe-t-il plus par un compte de transfert de charges ? ». Verso : le PCG ne prévoit plus cette technique, puisque le règlement ANC n° 2022-06 a retiré les transferts de charges de la liste des produits de l'article 512-1. Le remboursement va au compte 649. | Règlement ANC n° 2022-06, art. 1 (Ce qui a changé récemment#0) |
| ue9-04-k23 | **Plusieurs réponses justes possibles.** « Les retenues sur le salaire brut » englobent aussi des retenues que la carte ne vise pas, comme les oppositions sur salaire (compte 427). Une réponse juste mais différente était donc possible. | La question énumère ce qu'elle vise : « Dans l'écriture de paie, quels comptes du PCG sont crédités pour les cotisations salariales, le prélèvement à la source et les acomptes déjà versés ? ». Le verso (431, 437, 4421, 425) est inchangé. | Plan de comptes 2026, comptes 425, 427, 431, 437 et 4421 (Règles essentielles#9) |
| ue9-04-k30 et k31 (k31 supprimée) | **Doublon.** k31 (« qu'a changé le PCG 2025 pour les intérêts courus ? » : ventilation par nature, 1648, ancien 16884) reprenait presque mot pour mot ue9-08-k10. Dans le chapitre, k30 donnait déjà le compte 1648. | Fusion : le verso de k30 se termine par « Depuis 2025, ces intérêts sont inscrits au compte 1648 « Intérêts courus sur emprunts auprès des établissements de crédit » (avant 2025 : 16884, subdivision du compte 1688). » Cela suit le contrat (section 6 : signaler « avant 2025 : 1688 »). La base de k30 devient [Règles essentielles#13, Ce qui a changé récemment#1]. k31 est supprimée. | C. com., art. L. 123-13 ; règlement ANC n° 2022-06 ; plan de comptes 2026, comptes 1648 et 1688 |
| ue9-04-k33 | **Règle présentée comme absolue.** « Les seules opérations figurant sur le relevé mais absentes de la comptabilité » : lors d'un rapprochement, l'entreprise corrige aussi les erreurs qu'elle découvre dans ses propres écritures. « Seules » n'est donc vrai que si sa comptabilité ne contient aucune erreur. | « Seules » est retiré : « <b>Les opérations figurant sur le relevé mais absentes de la comptabilité</b> (frais, agios, virements reçus). » La carte reste fidèle à Règles essentielles#14. | C. com., art. R. 123-174 et R. 123-177 |
| ue9-04-k12 (supprimée) | **Doublon.** Les redevables de la CFE (« personnes physiques ou morales, entités non dotées de la personnalité morale ou fiduciaires… ») reprenaient mot pour mot ue4-06-k03. La rédaction issue de la loi de finances pour 2026 est l'objet de ue4-06-k06. La carte n'avait aucun angle comptable. | Supprimée. Le classement comptable de la CFE (compte 6351, impôt direct autre que l'impôt sur les bénéfices) reste porté par k11. | CGI, art. 1447, I (Règles essentielles#5, Ce qui a changé récemment#5) |
| ue9-04-k16 (supprimée) | **Carte sans intérêt et doublon.** La réponse, « Pôle emploi » remplacé par « France Travail », se devine sans connaître le règlement : il ne reste à retenir qu'une date d'application. La même carte existe en ue3-06-k32, et la note du compte 6454 du plan comptable (`data/pcg/classe6b.json`) signale déjà l'écart d'intitulé. ue9-02 a supprimé sa carte jumelle pour la même raison. | Supprimée. | Règlement ANC n° 2026-03, art. 6 (Ce qui a changé récemment#2) |
| ue9-04-k28 (supprimée) | **Doublon hors du champ comptable.** La question sur le taux individualisé du prélèvement à la source (depuis le 1er septembre 2025) était celle de ue4-01-k30. La réforme ne change rien à l'écriture de paie : l'employeur applique le taux transmis et crédite le compte 4421, comme le disent k26 et k27. | Supprimée. | Loi n° 2023-1322, art. 19 ; CGI, art. 204 E et 204 M (Ce qui a changé récemment#4) |
| ue9-04-k35 (supprimée) | **Doublon.** « Selon le Code de commerce, pendant combien de temps les documents comptables et les pièces justificatives doivent-ils être conservés ? » (dix ans) était la troisième copie de la même question, avec ue9-01-k36 et ue9-02-k21. | Supprimée. | C. com., art. L. 123-22 (Chiffres et seuils#2) |

Les 22 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche : k01 à k03, k05 à k07, k09 à k11, k14, k18 à k22, k24 à k27, k29, k32 et k34. Les points vérifiés sont les suivants :
- C. com., art. L. 123-13, R. 123-174, R. 123-176, R. 123-177 et R. 123-203 ;
- C. trav., art. L. 3242-1 et L. 3243-2 ;
- CSS, art. L. 242-1 et L. 136-1-1 ;
- CGI, art. 204 A, 260 B, 261 C, 1400, 1415, 1447 et 1671 ;
- comptes 164, 1648, 421, 425, 431, 437, 4421, 444, 44566, 512, 53, 58, 61/62, 63, 6351, 6582, 641, 645, 649, 661 et 695 du plan de comptes 2026.

Plusieurs cartes ont été examinées et conservées :
- **k07 et k09.** Elles citent l'article 261 C (et l'article 260 B) du CGI. C'est exact au 15 octobre 2026, puisque l'abrogation prend effet le 1er janvier 2027. À cette date, il faudra reprendre leurs références, en même temps que la fiche (voir « Points à reprendre »).
- **k20 et k21.** Elles reposent toutes deux sur Règles essentielles#8, mais ne demandent pas la même chose : l'assiette d'un côté, la raison de l'exclusion des frais professionnels de l'autre.
- **k02 et k03.** Elles se recoupent sur la dérogation de l'article R. 123-203. k02 demande le principe, k03 qui en bénéficie : les questions sont distinctes.
- **Recoupements avec d'autres chapitres, conservés.** Ces cartes portent sur des points du programme de ce chapitre : trésorerie, échéances d'emprunt, rapprochement bancaire.
  - k03 est la question inverse de ue9-02-k26.
  - k17 recoupe ue9-01-k29 et ue9-02-k28, mais sous l'angle propre à la paie (compte 649).
  - k29 et k30 recoupent ue9-08-k08 et k09.
  - k33 et k34 recoupent ue9-09-k21.
  - k11 recoupe en partie ue10-07-k01 et garde la distinction avec la CFE et la CVAE.

## Recherches

Une seule recherche WebSearch a été faite, limitée à legifrance.gouv.fr.

1. **« ordonnance n° 2025-1247 recodification TVA entrée en vigueur report 1er janvier 2027 »** (legifrance.gouv.fr).
   - Résultats : l'ordonnance (JORFTEXT000053091516), son rapport au Président de la République, et son article 49, qui fixe l'entrée en vigueur au 1er septembre 2026 sous réserve des dates propres à certaines dispositions.
   - Légifrance indique aussi, dans une note sur l'article 272 du CGI, que les dispositions TVA du CGI sont abrogées à compter du 1er janvier 2027.
   - Pour plusieurs articles du CIBS, les tables de concordance renvoient, pour une entrée en vigueur au 1er janvier 2027, à l'article 19, I, de l'ordonnance n° 2026-671 du 27 juillet 2026.
   - Conclusion : au 15 octobre 2026, l'article 261 C du CGI reste la référence applicable. k07 et k09 sont donc exactes. La date du 1er janvier 2027 de k08 est confirmée, et les cartes ue9-03-k34 et ue4-05-k33 parlent elles aussi d'un report au 1er janvier 2027. Le texte de l'ordonnance n° 2026-671 n'a pas été restitué : la recherche ne dit pas quelles dispositions il reporte.

Aucune autre recherche n'a été jugée nécessaire, pour deux raisons :
- les autres points relèvent de textes constants (Code de commerce, Code du travail, articles 1400 et 1415 du CGI) ou du plan de comptes 2026, déjà vérifiés pour la fiche (rapport `ue9-04.md`, recherches 1 à 13) ;
- la rédaction 2026 de l'article 1447 du CGI est confirmée par ue4-06-k06.

## Points à reprendre dans la fiche

1. **Ce qui a changé récemment#6 (recodification de la TVA).**
   - « Légifrance fixe au 1er janvier 2027 l'abrogation » est à reformuler : Légifrance publie le droit, il ne fixe pas de date.
   - La fiche devrait concilier deux dates : l'article 49 de l'ordonnance (entrée en vigueur au 1er septembre 2026) et l'abrogation au 1er janvier 2027.
   - Elle devrait aussi nommer le texte du report, peut-être l'ordonnance n° 2026-671 du 27 juillet 2026 (art. 19, I), cité par les tables de concordance de Légifrance. C'est à confirmer.
2. **Règles essentielles#2 et #3, Points de vigilance#1 et liste des textes (CGI, art. 260 B et 261 C).** Ces références restent exactes jusqu'au 31 décembre 2026. À compter du 1er janvier 2027, il faudra les remplacer par celles du CIBS. Seule l'assurance a des numéros connus (art. L. 213-129 à L. 213-131). Les numéros pour l'octroi de crédits, les timbres-poste et l'option de l'article 260 B restent à trouver. Les cartes k06, k07 et k09, qui copient ces `src`, seront à reprendre en même temps.
3. **Points de vigilance#2 (rapprochement).** « Seules les opérations connues par le relevé et absentes de la comptabilité sont enregistrées » est trop absolu : lors du rapprochement, l'entreprise corrige aussi ses propres erreurs d'enregistrement. Il faut retirer « Seules », ou compléter la phrase avec un texte à l'appui. La carte k33 a été corrigée en conséquence.
4. **Définitions#3 (compte 6454 « Pôle emploi »).** L'intitulé est exact pour le plan de comptes 2026. Un renvoi à Ce qui a changé récemment#2 serait utile : « France Travail » pour les exercices ouverts à compter du 1er janvier 2027.
5. **Point de la première relecture.** Le résultat transmis de la première relecture s'arrête au début de son premier point de fiche (« Définitions#… ») : son contenu n'a pas été reçu.

## Classement des exercices

Le classement automatique porte sur les 15 exercices `qcm`, `multi` et `tri` du chapitre : 12 `qcm`, 3 `multi` et aucun `tri`.

| nature | nombre | exercices |
|---|---|---|
| `notion` | 13 | n° 4, 7, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20 et 21 (index dans `exercices`) |
| `calcul` | 2 | n° 18 (intérêts d'un emprunt à amortissements constants) et n° 22 (solde rapproché du compte 512) |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé. Seuls les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 30 cartes.
