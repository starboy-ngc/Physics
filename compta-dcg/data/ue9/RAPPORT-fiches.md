# Rapport de relecture finale des fiches documentaires — UE9 Comptabilité

Relecture adversariale du 14 octobre 2026 (fiches `ue9-01` à `ue9-09`). Vérifications par WebSearch restreint à legifrance.gouv.fr (18 recherches abouties ; quota de recherche épuisé ensuite, les autres contrôles reposent sur les résultats déjà obtenus et sur le plan de comptes local `data/pcg`). Aucune URL ni citation n'a été écrite sans être apparue dans un résultat de recherche.

## Corrections apportées aux fiches (résumé)

| Point | Fiches | Erreur | Correction | Source |
|---|---|---|---|---|
| C. com., art. L. 123-13 | 01, 07, 09 | URL de la version 2000-2016 (LEGIARTI000006219305) | URL de la version en vigueur depuis le 1er janvier 2016 (LEGIARTI000030927169) | Légifrance, art. L. 123-13 |
| C. com., art. L. 123-17 | 01, 09 | Texte et citation de la version 2011-2016 (« A moins qu'un changement exceptionnel… ») | Texte en vigueur (ordonnance n° 2015-900) : « Sauf dans des cas exceptionnels… les méthodes comptables retenues et la structure du bilan et du compte de résultat ne peuvent être modifiées… » ; URL LEGIARTI000030927173 | Légifrance, art. L. 123-17 |
| C. com., art. L. 123-19 | 01, 06, 08, 09 | URL de la version 2000 et citation d'une phrase dont la rédaction a changé en 2016 (exception par règlement ANC) | URL de la version en vigueur (LEGIARTI000030927177) ; citation retirée | Légifrance, art. L. 123-19 |
| C. com., art. L. 123-20 | 01, 06, 07, 09 | URL de la version 2000 | URL de la version en vigueur (LEGIARTI000030927181) ; ajout de la règle « même en cas d'absence ou d'insuffisance du bénéfice… » (05, 06) | Légifrance, art. L. 123-20 |
| C. com., art. R. 123-177 | 02, 04, 06, 09 | URL de la version 2007 (« relevé … livre d'inventaire ») alors que la citation est celle de 2016 | URL de la version en vigueur (LEGIARTI000030927443) | Légifrance, art. R. 123-177 |
| C. com., art. L. 123-23 | 09 | url null, pas de citation | URL confirmée et citation verbatim | Légifrance, art. L. 123-23 |
| C. com., art. R. 123-203 | 02, 04, 09 | Numéro d'article non confirmé (l'ancre de la page officielle vise un autre article de la sous-section) | src élargie à la sous-section R. 123-203 à R. 123-208, citation et URL de section conservées | Légifrance, sous-section 2 |
| Résultat exceptionnel (règlement ANC 2022-06) | 01, 07 | Mention des « corrections d'erreurs » non vérifiable | Définition limitée à l'événement majeur et inhabituel ; écritures d'origine fiscale en 687/787 | Règlement ANC n° 2022-06 |
| TVA sur acomptes (CGI, art. 269) | 03 | Règle 2023 absente (acompte sur livraison de biens) | Item d'exigibilité complété et item « Ce qui a changé » ajouté (LF 2022, art. 30) | CGI, art. 269, 2-a |
| Cession de VMP | 08 | Présentation brute attribuée aux comptes 6673/7673 | Présentation nette (charges nettes / produits nets sur cessions de VMP), conforme au plan de comptes PCG 2025 | Plan de comptes PCG 2025, comptes 6673 et 7673 |
| Subvention d'investissement (PCG, art. 312-1) | 08 | Étalement présenté comme obligatoire | Option entre rapport immédiat au résultat et étalement (131/139/747) | PCG, art. 312-1 |
| Homologation des règlements ANC | 09 | Formule « arrêté conjoint » non vérifiée | Reformulé : homologation par arrêté ministériel et publication au JO (ex. : arrêté du 26 décembre 2023) | Ordonnance n° 2009-79, art. 4 |
| Acomptes d'IS | 07 | Dates attribuées à l'art. 1668 seul | Précision « dates fixées par décret », solde au 15 du quatrième mois | CGI, art. 1668 |

## Corrections apportées aux chapitres (leçons et exercices)

| Fichier | Cible | Erreur | Correction | Source |
|---|---|---|---|---|
| ue9-02.json | lecon[0] et sources[4] | « fin des systèmes abrégé et développé » contredit le plan de comptes PCG 2025/2026, « commun au système de base et au système abrégé » (cite de la fiche ue9-02) | Plan de comptes recodifié à l'art. 1121-1, commun au système de base et au système abrégé | Plan de comptes PCG 2025 (PCG, art. 1121-1) |
| ue9-07.json | lecon[0] | « risques et pertes » (rédaction 2000 de L. 123-20) | « passifs nés au cours de l'exercice, même connus entre la clôture et l'établissement des comptes » | C. com., art. L. 123-20 (version 2016) |
| ue9-08.json | lecon[3] | Subvention d'investissement présentée comme jamais rapportée immédiatement au résultat | Mention de l'option de l'art. 312-1 (rapport immédiat ou étalement, méthode retenue à l'examen) | PCG, art. 312-1 |
| ue9-09.json | lecon[1], lecon[5], sources[5] | « plan de comptes unique à la place des systèmes abrégé, de base et développé » ; « a remplacé les trois systèmes de présentation » | Plan de comptes recodifié (commun au système de base et au système abrégé) ; nouveaux modèles avec présentations simplifiées selon la taille | Plan de comptes PCG 2025 (PCG, art. 1121-1) |
| ue9-09.json | exercices[5] (multi) | Option correcte « Un plan de comptes unique remplace les systèmes abrégé, de base et développé » | Remplacée par « La quote-part de subvention d'investissement virée au résultat passe en 747 » (toujours correcte, indices inchangés) ; `why` ajusté | Règlement ANC n° 2022-06 ; plan de comptes PCG 2025, compte 747 |
| ue9-09.json | lecon[2] | Indépendance des exercices rattachée à L. 123-20 | Rattachée à L. 123-13, al. 2 | C. com., art. L. 123-13 |

## Points non tranchés (à vérifier quand le quota de recherche le permettra)

- Règlements ANC n° 2026-03 (France Travail, compte 6454), n° 2025-05 (compte 791 et concessions d'aménagement), n° 2024-07 (bons de souscription), n° 2023-03 (coordination) et arrêté du 12 août 2026 (JORFTEXT000054791025) : cités dans plusieurs fiches (UE6, UE9, UE10) par des rédacteurs différents, non recontrôlés dans cette passe.
- Numéro exact de l'article du Code de commerce autorisant l'enregistrement à la date du relevé bancaire (R. 123-205 ou R. 123-206 selon l'ancre de la page officielle) : src élargie à la sous-section.
- PCG 2025 : numéro de l'article « partie double » (921-1 dans la version 2024, conservé avec mention de la version) ; existence maintenue du « système abrégé » (cite du plan de comptes 2026) ; formulation « comptes imprimés en caractères normaux = plan de comptes minimal » (fiche ue9-02).
- URL non recontrôlées faute de quota (identifiants plausibles, conservés) : R. 123-175 (LEGIARTI000006257948), R. 123-181 (LEGIARTI000030927431), R. 123-190 (LEGIARTI000030927465), L. 123-25 (LEGIARTI000028556295), L. 233-21 (LEGIARTI000006229310), D. 123-200 (LEGIARTI000049216681), décret 2024-152, arrêté du 26 décembre 2023, ordonnance 2009-79, fichiers PDF anc.gouv.fr, programme BO ESR.
- Fiches ue9-03, ue9-04, ue9-05, ue9-07, ue9-08 : moins de 6 URL ont pu être confirmées par recherche (quota) ; les URL CGI, Code du travail et CSS restent `null`.
