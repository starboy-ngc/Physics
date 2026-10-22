# Objectif DSCG — réviser le DCG pour viser le DSCG

Application web autonome (un seul fichier HTML, fonctionne hors ligne) : six matières complètes et des pages de
rappels pour l'UE1, une fiche documentaire sourcée sur les textes officiels pour chaque chapitre, leçons complètes,
1 165 exercices corrigés (QCM, QCM à réponses multiples, calculs, classements, écritures au journal),
test quotidien réparti sur plusieurs matières, révisions espacées sur 1 423 cartes de notions (définitions et
compréhension, sans calcul), plan comptable général 2025 commenté compte par compte (612 comptes), les annales
officielles des cinq dernières sessions et les sujets zéro du programme 2027 en composition chronométrée, et une
analyse détaillée des performances. Chaque matière garde une couleur d'identité, toujours accompagnée de son code.

## Utiliser

Téléchargez `dist/DebitCredit.html` et ouvrez-le avec un navigateur (double-clic). Aucune installation,
aucun serveur. La progression est gardée dans le navigateur ; un code de sauvegarde permet de la transférer.

## Contenu

| Matière | Chapitres | Exercices |
|---|---|---|
| UE9 Comptabilité | 9 | 232 |
| UE10 Comptabilité approfondie | 8 | 228 |
| UE2 Droit des sociétés et des affaires | 7 | 203 |
| UE3 Droit social | 6 | 170 |
| UE4 Droit fiscal | 6 | 175 |
| UE6 Finance d'entreprise | 6 | 157 |
| UE1 Fondamentaux du droit | 7 pages de rappels (126 rappels) | — |

Référentiel : PCG 2025 (règlement ANC n° 2022-06), droit et fiscalité 2025-2026. Les chiffres qui changent
chaque année (SMIC, PASS, barème de l'IR, seuils) sont datés dans l'énoncé et signalés « chiffres 2025 ».

## Journée de travail

L'accueil propose chaque jour une séance en trois temps, sur plusieurs matières :

1. **Notions à revoir** : les révisions espacées dues, puis les nouvelles notions, en alternant les matières.
2. **Test du jour** : 20 questions ; les révisions dues d'abord, puis une question par matière à tour de rôle
   (les matières du programme du jour en premier), en reprenant d'abord les questions ratées.
3. **Cours du jour** : un chapitre dans trois matières, en rotation (celles qui n'ont pas été travaillées depuis le
   plus longtemps passent en premier), plus une page de rappels de l'UE1.

## Analyse des performances

Chaque réponse est enregistrée (heure, juste ou fausse, temps de réponse, marche des révisions espacées). La page
Analyse en tire, sur 7, 30 ou 90 jours ou depuis le début :

- une synthèse (réussite et évolution par rapport à la période précédente, volume, notions mémorisées, couverture
  des exercices, temps médian par question) ;
- des priorités calculées (révisions en retard, erreurs à reprendre, chapitres fragiles, matières délaissées,
  format de question le plus faible, rythme insuffisant pour la date d'examen, annales) ;
- le diagnostic par matière (réussite, tendance, couverture, mémorisation, temps médian, dernière séance) ;
- l'évolution de la réussite sur 7 jours glissants, par matière, et le volume de travail ;
- les points faibles : chapitres, formats de question, nature (notion ou calcul), niveau, questions les plus ratées,
  avec une séance « Mes erreurs » ;
- la mémoire : taux de rappel selon l'intervalle de révision et plateau des notions ;
- la régularité (calendrier, réussite selon le moment de la journée), les tests du jour et les annales.

## Questions sur les articles

Les questions qui demandaient le numéro d'un article ou le nom d'un texte, ou l'inverse (« que prévoit
l'article… ? »), ont été supprimées ; celles qui citaient un article en simple contexte ont été reformulées sans la
référence, la réponse restant la même et la source restant citée dans l'explication. Détail :
`data/QUESTIONS-ARTICLES.md`.

## UE1 : pages de rappels

L'UE1 Fondamentaux du droit se révise par des **rappels courts**, sans exercices ni cartes : une page par chapitre
(8 à 18 rappels, 850 mots au plus), dans l'onglet Cours. Chaque rappel est tiré d'un item de la fiche documentaire
du chapitre (`data/ue1/<id>.fiche.json`, vérifiée sur les textes officiels) et renvoie à son texte (Code civil,
Code de procédure civile, Code de commerce, Constitution, jurisprudence de la Cour de cassation). Format :
`data/CONTRAT.md`, section 9 ; fichiers `data/ue1/<id>.rappel.json`. Programme : annexe 1 de l'arrêté du
4 août 2025 (session 2027).

## Annales

Réviser › Annales : pour chaque matière, les sujets des sessions 2022 à 2026 (pages du CRCF, qui publie sujets et
éléments de corrigé), les rapports du jury du SIEC (2022 à 2025) et le sujet zéro du programme 2027 avec son corrigé
(guide pédagogique du ministère, juillet 2026). Le mode composition lance un chronomètre sur la durée officielle
(3 heures), avec pause ; la note sur 20 que l'on s'attribue avec le corrigé est enregistrée. Les sujets s'ouvrent
en ligne. Sources du catalogue : `data/ANNALES.md`.

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

L'onglet Réviser affiche le plateau d'avancement (nombre de notions sur chaque marche) pour l'ensemble, pour
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
- `data/plan.json` : les 42 chapitres, les 7 chapitres de rappels de l'UE1 et leur contenu attendu.
- `data/<ue>/*.json` : un fichier par chapitre ; `data/pcg/*.json` : le plan comptable commenté.
- Chaque chapitre a été rédigé puis relu par un relecteur indépendant chargé de chercher l'erreur
  (recalcul de tous les calculs, vérification des écritures, recoupement des chiffres par recherche web),
  qui a corrigé ou supprimé tout point douteux.
- Cartes de notions (`data/<ue>/<id>.cartes.json`) : rédigées depuis la fiche du chapitre, puis relues deux fois
  par des relecteurs indépendants (fidélité à la fiche, puis exactitude juridique et comptable avec recherche
  sur les sites officiels). Un rapport par chapitre : `data/<ue>/rapports/<id>-cartes.md`. Les items de fiche
  jugés ambigus ou incomplets par ces relecteurs sont listés dans `data/FICHES-A-REPRENDRE.md`.
- UE1 : fiches rédigées avec recherches restreintes aux sites officiels, relues, puis contre-vérifiées item par item
  (passe dédiée avec recherches) ; rappels rédigés depuis ces fiches, puis relus deux fois (fidélité à la fiche,
  puis exactitude juridique). Les items restés non vérifiés ne donnent pas de rappel. Rapports :
  `data/ue1/rapports/<id>.md`.
- Nature des exercices (`nature` : notion, calcul ou chiffre) : classement par deux agents indépendants ; une
  question n'entre dans les révisions espacées que si les deux la jugent sans calcul.
- `validate.js` vérifie la structure (réponses valides, écritures équilibrées, comptes 675/775 bannis…) ;
  `check-accounts.js` croise les comptes utilisés avec le plan commenté.
- `node build.js` assemble `src/index.html` et les données en `dist/DebitCredit.html`.
