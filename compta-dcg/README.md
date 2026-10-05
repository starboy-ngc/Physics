# Débit Crédit — réviser le DCG pour aborder le DSCG

Application web autonome (un seul fichier HTML, fonctionne hors ligne) : six matières, leçons complètes,
1 168 exercices corrigés (QCM, QCM à réponses multiples, calculs, classements, écritures au journal),
test quotidien, révisions espacées, plan comptable général 2025 commenté compte par compte (606 comptes),
jeu de progression (« l'expédition vers les aurores »).

## Utiliser

Téléchargez `dist/DebitCredit.html` et ouvrez-le avec un navigateur (double-clic). Aucune installation,
aucun serveur. La progression est gardée dans le navigateur ; un code de sauvegarde permet de la transférer.

## Contenu

| Matière | Chapitres | Exercices |
|---|---|---|
| UE9 Comptabilité | 9 | 232 |
| UE10 Comptabilité approfondie | 8 | 229 |
| UE2 Droit des sociétés et des affaires | 7 | 203 |
| UE3 Droit social | 6 | 171 |
| UE4 Droit fiscal | 6 | 176 |
| UE6 Finance d'entreprise | 6 | 157 |

Référentiel : PCG 2025 (règlement ANC n° 2022-06), droit et fiscalité 2025-2026. Les chiffres qui changent
chaque année (SMIC, PASS, barème de l'IR, seuils) sont datés dans l'énoncé et signalés « chiffres 2025 ».

## Méthode de production et de vérification

- `data/CONTRAT.md` : format JSON, règles de qualité, changements PCG 2025 confirmés.
- `data/plan.json` : les 42 chapitres et leur contenu attendu.
- `data/<ue>/*.json` : un fichier par chapitre ; `data/pcg/*.json` : le plan comptable commenté.
- Chaque chapitre a été rédigé puis relu par un relecteur indépendant chargé de chercher l'erreur
  (recalcul de tous les calculs, vérification des écritures, recoupement des chiffres par recherche web),
  qui a corrigé ou supprimé tout point douteux.
- `validate.js` vérifie la structure (réponses valides, écritures équilibrées, comptes 675/775 bannis…) ;
  `check-accounts.js` croise les comptes utilisés avec le plan commenté.
- `node build.js` assemble `src/index.html` et les données en `dist/DebitCredit.html`.
