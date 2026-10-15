# Rapport : comptes de tiers « charges à payer / produits à recevoir » (sous-classes 42, 43, 44)

Passe transversale du 15/10/2026. Objet : aligner le plan commenté et les chapitres sur le plan de comptes PCG 2025 de l'ANC (règlement ANC n° 2022-06), structure reprise dans le plan 2026.

## Nomenclature établie

| Compte | Plan 2024 | Plan 2025 (et 2026) |
|---|---|---|
| 425 | Personnel – Avances et acomptes | Personnel – Avances et acomptes et autres comptes débiteurs |
| 428 | Personnel – Charges à payer et produits à recevoir | Personnel – Charges à payer |
| 4282 / 4284 / 4286 | Dettes provisionnées pour congés à payer / pour participation / Autres charges à payer | Maintenus, mêmes intitulés |
| 4287 | Produits à recevoir | Absent du plan 2025 (supprimé) |
| 438 | Organismes sociaux – Charges à payer et produits à recevoir | Organismes sociaux – Charges à payer |
| 4382 / 4386 | Charges sociales sur congés à payer / Autres charges à payer | Maintenus |
| 4387 | Produits à recevoir | Absent (supprimé) |
| 439 | n'existait pas | Organismes sociaux – Produits à recevoir (créé) |
| 448 | État – Charges à payer et produits à recevoir | Même intitulé |
| 4481 | n'existait pas | État – Charges à payer (créé) |
| 44811 | n'existait pas | Charges fiscales sur congés à payer (ex-4482) |
| 44812 | n'existait pas | Charges à payer (ex-4486) |
| 4482 | Charges fiscales sur congés à payer | État – Produits à recevoir (changement de sens, ex-4487) |
| 4486 | Charges à payer | Absent (supprimé ; remplacé par 44812) |
| 4487 | Produits à recevoir | Absent (supprimé ; remplacé par 4482) |

Sources : plan de comptes PCG 2025 (https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/Plan-de-comptes-PCG-2025.pdf), plan 2024 (https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/Recueils/PCG_Janvier2024/Plan-de_comptes_PCG-2024.pdf), plan 2026 (https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/Plan-de-comptes-2026.pdf), règlement ANC n° 2022-06 (https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2022/R2022_06/R2022_06.pdf).

## Corrections

| Fichier | Cible | Ancien | Nouveau | Source |
|---|---|---|---|---|
| data/pcg/classe4.json | 42 (explication, pcg2025) | 425 « avances » ; pcg2025 null | 425 « avances, acomptes et autres créances sur le personnel » ; pcg2025 : 428 réservé aux charges à payer, 4287 supprimé, 425 renommé | Plans 2024 et 2025 |
| data/pcg/classe4.json | 425 (intitulé, explication, pcg2025) | « Personnel – Avances et acomptes » | « Personnel – Avances et acomptes et autres comptes débiteurs » ; pcg2025 « Renommé… » | Plan 2025 ; R2022-06 |
| data/pcg/classe4.json | 428 (intitulé, explication, pcg2025) | « Personnel – Charges à payer et produits à recevoir », 4287 cité, « 4287 à l'actif » | « Personnel – Charges à payer » ; 4282, 4284, 4286 seulement ; pcg2025 « Renommé… 4287 supprimée » | Plan 2025 |
| data/pcg/classe4.json | 4287 (ajouté) | absent du plan commenté | Listé comme supprimé : « Supprimé par le règlement ANC 2022-06 ; utiliser 425… » | Plans 2024 et 2025 |
| data/pcg/classe4.json | 43 (explication, pcg2025) | 438 seulement ; pcg2025 null | 438 et 439 (439 à l'actif) ; pcg2025 : 4387 supprimé, 439 créé | Plan 2025 |
| data/pcg/classe4.json | 438 (intitulé, explication, pcg2025) | « Organismes sociaux – Charges à payer et produits à recevoir », 4387 cité | « Organismes sociaux – Charges à payer » ; 4382, 4386 ; renvoi au 439 | Plan 2025 |
| data/pcg/classe4.json | 4387 (ajouté) | absent | Listé comme supprimé : « Supprimé… ; utiliser 439 » ; exemple avant/après (4387/791 → 439/649) | Plans 2024 et 2025 |
| data/pcg/classe4.json | 439 (ajouté) | absent | « Organismes sociaux – Produits à recevoir », sens D, pcg2025 « Créé… en remplacement du 4387 » ; exemple 439 D 1 200 / 649 C 1 200 | Plans 2025 et 2026 |
| data/pcg/classe4.json | 44 (pcg2025) | null | Restructuration du 448 (4481, 44811, 44812, 4482 ; 4486 et 4487 supprimés) | Plan 2025 |
| data/pcg/classe4.json | 448 (sens, explication, exemple, piège, pcg2025) | sens C ; 4482 congés, 4486, 4487 ; exemple 6312 / 4486 | sens D/C ; 4481 (44811, 44812) et 4482 produits à recevoir ; exemple 63512 D / 44812 C ; pcg2025 « Subdivisions réorganisées… » | Plan 2025 |
| data/pcg/classe4.json | 4481 (ajouté) | absent | « État – Charges à payer », pcg2025 « Créé… (ex-4482 et 4486) » | Plan 2025 |
| data/pcg/classe4.json | 44811 (ajouté) | absent | « Charges fiscales sur congés à payer », exemple 633 D 400 / 44811 C 400, pcg2025 « Créé… en remplacement du 4482 » | Plan 2025 |
| data/pcg/classe4.json | 44812 (ajouté) | absent | « Charges à payer », exemple 63511 D 1 500 / 44812 C 1 500, pcg2025 « Créé… en remplacement du 4486 » | Plan 2025 |
| data/pcg/classe4.json | 4482 (intitulé, sens, explication, exemple, piège, pcg2025) | « Charges fiscales sur congés à payer », sens C, exemple 633 / 4482 | « État – Produits à recevoir », sens D, exemple 4482 D 600 / 63512 C 600 ; pcg2025 « Changement de sens… » | Plans 2024 et 2025 |
| data/pcg/classe4.json | 4486 (explication, exemple, piège, pcg2025) | compte présenté comme en vigueur | « Supprimé par le règlement ANC 2022-06 ; utiliser 44812… » ; exemple avant/après | Plan 2025 |
| data/pcg/classe4.json | 4487 (explication, exemple, piège, pcg2025) | compte présenté comme en vigueur | « Supprimé par le règlement ANC 2022-06 ; utiliser 4482 État – Produits à recevoir » ; exemple avant/après | Plan 2025 |
| data/pcg/classe6a.json | 631 (explication) | « par le crédit du 447 ou du 4486 » | « 447 ou, à la clôture, du 44812 État – Charges à payer (44811 pour les taxes afférentes aux congés à payer ; avant 2025 : 4486 et 4482) » | Plan 2025 |
| data/pcg/classe6b.json | 649 (explication) | « par le débit du 431, du 4387 ou du 512 » | « 431, du 439 Organismes sociaux – Produits à recevoir (avant 2025 : 4387) ou du 512 » | Plan 2025 |
| data/pcg/classe6b.json | 699 (explication) | « par le débit du 444 (ou du 4487) » | « par le débit du 444 » (4487 supprimé ; la créance de report en arrière est une créance d'impôt sur les bénéfices) | Plan 2025 |
| data/ue10/ue10-05.json | lecon[5] (charge à payer) | « (408, 4286, 4486) » | « (408, 4286, 44812) » | Plan 2025 |
| data/ue9/ue9-07.json | lecon[2] (produits à recevoir) | État : débit 441 seulement | Ajout : dégrèvement notifié en 4482 État – Produits à recevoir (avant 2025 : 4487) ; indemnités journalières à recevoir en 439 (avant 2025 : 4387), crédit 649 | Plan 2025 |
| data/ue9/ue9-07.json | sources[2].note | liste sans 439 ni 4482 | 439 et 4482 ajoutés | Plan 2025 |
| data/ue9/ue9-07.fiche.json | Définitions[2] (produit à recevoir) | État : « compte 448 » | 4482 « État – Produits à recevoir » ; organismes sociaux 439 ; src complétée | Plans 2025 et 2026 |
| data/ue9/ue9-07.fiche.json | Règles essentielles[3] (produits à recevoir) | « pour l'État, du compte 448 » | 439 (organismes sociaux) et 4482 (État) ; src complétée | Plans 2025 et 2026 |
| data/ue9/ue9-07.fiche.json | Ce qui a changé récemment[2] | 428, 438, 4481, 44811 | Ajout : 4287 supprimé, 439 (ex-4387), 44812 (ex-4486), 4482 (ex-4487) ; src complétée | Plans 2024, 2025 et 2026 ; R2022-06 |
| data/ue9/ue9-07.fiche.json | textes[6].objet | liste sans 439, 44812, 4482 | 439, 44812 et 4482 ajoutés | Plan 2026 |
| data/ue9/ue9-04.fiche.json | Règles essentielles[7] (acompte) | 425 « Personnel – Avances et acomptes » ; src « plan de comptes » | « Personnel – Avances et acomptes et autres comptes débiteurs » ; src « plan de comptes 2025 (PCG, art. 1121-1) » | Plan 2025 |

## Vérifié sans changement

- data/ue10/ue10-07.json et sa fiche : 4284 et 4286 (participation, intéressement) existent dans le plan 2025 ; écritures, palettes et solutions inchangées.
- data/ue9/ue9-07.json : 4282, 4286, 4382, 4386, 4481, 44811 déjà alignés lors de la relecture précédente ; aucun exercice n'utilise de compte supprimé ; aucune réponse modifiée.
- data/ue10/ue10-05.json, exercice 22 : palette avec 4286, compte maintenu ; réponse inchangée.
- Les autres occurrences relevées par grep (n° 428048 d'une décision du CE, identifiants LEGIARTI, montants 4 439 €, 7 448) ne sont pas des comptes.
- Aucune réponse d'exercice n'utilisait 4287, 4387, 4482 (ancien sens), 4486 ou 4487 : aucune réponse n'a changé.

## Contrôles

- `node validate.js` : classe4.json (119 comptes), classe6a.json, classe6b.json, ue10-05.json, ue9-07.json, ue9-07.fiche.json, ue9-04.fiche.json passent.
- `node check-accounts.js` : « Tous les comptes utilisés existent dans le plan commenté » (612 comptes).
- `node check-fiches.js` : aucun problème.

## Recherches (11 WebSearch, allowed_domains anc.gouv.fr, une fois anc.gouv.fr + legifrance.gouv.fr)

1. 4282 / 4382 dans le plan 2025 : 428 « Personnel - Charges à payer », 438 « Organismes sociaux - Charges à payer », 44811 sous 4481 (2025) contre 4482 (2024).
2. 4284, 4286, 4287 : 4282, 4284, 4286 sous 428 en 2025 ; 4287 absent (présent en 2024).
3. Règlement 2022-06 et 4287 / 4387 : extrait du règlement limité à 4282, 4284, 4286 et à des charges à payer pour le 438.
4. 438 / 4386 / 439 : 439 « Organismes sociaux - Produits à recevoir » dans le plan 2025, 4387 en 2024.
5. 429 « Personnel - Produits à recevoir » : aucun résultat ; 439 et 4482 visibles dans l'extrait 2025.
6. Version commentée R2022-06 et 4287 : 2026 limite 428 à 4282, 4284, 4286.
7. 425 : « Personnel - Avances et acomptes et autres comptes débiteurs » en 2025 et 2026 (« Personnel - Avances et acomptes » en 2024).
8. 448 : 4481 « État - Charges à payer » (44811, 44812) et 4482 « État - Produits à recevoir » dans le plan 2025.
9. 439 dans le plan 2026 : confirmé, aussi présent dans R2022_06.pdf.
10. R2022-06, 425 et 428 : intitulés 425, 428 et 4286 confirmés dans le texte du règlement.
11. R2022-06 et 44811 / 4482 : 44811 confirmé ; 4482 « État-Produits à recevoir » repris dans un arrêté distinct (HLM), sans valeur pour le PCG général.

## Points de vigilance

- 4287 → 425 : le plan 2025 ne contient plus de compte de produits à recevoir du personnel. Le renvoi au 425 se fonde sur son nouvel intitulé (« … et autres comptes débiteurs ») ; aucun résultat ne restitue une phrase du règlement qui l'énonce expressément. Le pcg2025 du 4287 le formule comme un renvoi au compte débiteur du personnel.
- 4482 dans le plan 2026 : la structure 4481 / 44811 est confirmée pour 2026, mais aucun résultat n'a restitué explicitement le libellé 4482 du plan 2026 (il l'est pour le plan 2025).
- Le contrôle `check-accounts.js` ne détecte pas l'emploi de 4482 dans son ancien sens (le compte existe toujours) : tout nouveau contenu sur les congés payés doit utiliser 44811 pour les charges fiscales.
- Les fichiers `dist/` n'ont pas été reconstruits.
