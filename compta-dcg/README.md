# Débit Crédit — réviser le DCG pour aborder le DSCG

Application web autonome (un seul fichier HTML, fonctionne hors ligne) : six matières, une fiche documentaire
sourcée sur les textes officiels pour chaque chapitre, leçons complètes,
1 168 exercices corrigés (QCM, QCM à réponses multiples, calculs, classements, écritures au journal),
test quotidien, révisions espacées sur 1 436 cartes de notions (définitions et compréhension, sans calcul) avec
plateau d'avancement par thème, plan comptable général 2025 commenté
compte par compte (612 comptes), jeu de progression (« l'expédition vers les aurores ») et 69 succès à débloquer (bronze, argent, or) dans six catégories :
régularité, précision, maîtrise, matières, exploration et expédition.

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

## Révisions espacées

Les révisions espacées (le principe d'Anki) ne portent que sur les **définitions et la compréhension**, jamais
sur des calculs :

- des **cartes de notions** recto/verso, rédigées à partir des fiches documentaires : chaque carte renvoie aux
  items de la fiche dont elle est tirée et à leur texte officiel. On répond de tête, on retourne la carte, puis
  on indique si on savait (« Je savais » ou « Je ne savais pas ») ;
- les **QCM et classements de compréhension** des chapitres, ceux qui ne demandent aucun calcul (champ
  `nature` = `notion`, classement fait par deux relecteurs indépendants ; en cas de désaccord, la question est
  écartée) ;
- les **comptes du plan comptable** en vigueur : intitulé et rôle (les comptes supprimés en 2025 sont exclus).

Les calculs et les écritures se travaillent dans les exercices des chapitres et dans le test du jour.

Chaque notion avance sur une échelle de rappel :

| Marche | Demain | 2 jours | 5 jours | 10 jours | 20 jours | 30 jours | Chaque mois |
|---|---|---|---|---|---|---|---|

- notion nouvelle réussie : elle revient dans 2 jours ; ratée : elle revient demain ;
- bonne réponse le jour où elle est due (ou après) : une marche vers la droite ; la dernière marche se répète chaque mois ;
- erreur : une marche vers la gauche, et la notion revient selon le délai de cette marche (une erreur à « 10 jours » la ramène à « 5 jours ») ;
- une bonne réponse donnée avant l'échéance (en refaisant un chapitre, par exemple) ne fait pas monter la notion.

L'onglet Révisions affiche le plateau d'avancement (nombre de notions sur chaque marche) pour l'ensemble, pour
chaque matière et pour le plan comptable, avec le détail par chapitre ou par classe de comptes, la part de notions
mémorisées (10 jours et plus), la réussite sur 30 jours, la tendance sur 7 jours, la charge des 14 prochains jours
et la courbe de réussite sur 30 jours. Les nouvelles notions arrivent en alternant les thèmes, en commençant par
les chapitres déjà ouverts ; leur nombre par jour se règle de 0 à 30 (10 par défaut). Chaque chapitre a aussi un
onglet « Notions » qui liste ses cartes et lance une séance limitée au chapitre.

## Fiches documentaires

Chaque chapitre ouvre sur une fiche documentaire (`data/<ue>/<id>.fiche.json`) : programme officiel couvert
(arrêté du 4 août 2025 pour la session 2027, arrêté du 13 février 2019 pour la session 2026), textes de
référence, puis définitions, règles essentielles, chiffres et seuils, réformes récentes et points de vigilance.
Chaque énoncé porte sa source (article de code, BOFiP, règlement ANC, page URSSAF ou service-public) et, quand
il a pu être confirmé, le lien direct vers le texte officiel et un extrait verbatim. Un énoncé qui ne peut être
rattaché à un texte officiel n'est pas écrit. L'onglet « Fiches » permet une recherche plein texte.

Limite : les sites officiels ne sont pas joignables depuis l'environnement de production ; les liens et extraits
proviennent de recherches restreintes aux domaines officiels, jamais d'URL reconstituées. `check-fiches.js`
contrôle la présence des fiches, l'absence de formulations hésitantes et la couverture en liens.
Chaque fiche a été relue à charge par un relecteur distinct, avec des recherches sur les domaines officiels
(13 à 16 recherches par fiche lors de la passe finale) ; les rapports sont dans `data/<ue>/rapports/<id>.md`.
Les points qui n'ont pas pu être confirmés ne figurent pas comme affirmations dans les fiches ; ils sont
regroupés dans `data/POINTS-OUVERTS.md` pour une vérification humaine. `data/FAITS-CONFIRMES.md` liste les
faits récents confirmés (PASS et SMIC 2026, LFSS 2026, loi n° 2026-403, règlements ANC 2026…).

## Méthode de production et de vérification

- `data/CONTRAT.md` : format JSON, règles de qualité, changements PCG 2025 confirmés.
- `data/plan.json` : les 42 chapitres et leur contenu attendu.
- `data/<ue>/*.json` : un fichier par chapitre ; `data/pcg/*.json` : le plan comptable commenté.
- Chaque chapitre a été rédigé puis relu par un relecteur indépendant chargé de chercher l'erreur
  (recalcul de tous les calculs, vérification des écritures, recoupement des chiffres par recherche web),
  qui a corrigé ou supprimé tout point douteux.
- Cartes de notions (`data/<ue>/<id>.cartes.json`) : rédigées depuis la fiche du chapitre, puis relues deux fois
  par des relecteurs indépendants (fidélité à la fiche, puis exactitude juridique et comptable avec recherche
  sur les sites officiels). Un rapport par chapitre : `data/<ue>/rapports/<id>-cartes.md`. Les items de fiche
  jugés ambigus ou incomplets par ces relecteurs sont listés dans `data/FICHES-A-REPRENDRE.md`.
- Nature des exercices (`nature` : notion, calcul ou chiffre) : classement par deux agents indépendants ; une
  question n'entre dans les révisions espacées que si les deux la jugent sans calcul.
- `validate.js` vérifie la structure (réponses valides, écritures équilibrées, comptes 675/775 bannis…) ;
  `check-accounts.js` croise les comptes utilisés avec le plan commenté.
- `node build.js` assemble `src/index.html` et les données en `dist/DebitCredit.html`.
