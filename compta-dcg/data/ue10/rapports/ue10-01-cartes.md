# Cartes de notions : ue10-01 (Cadre conceptuel, normalisation et profession comptable)

Date : 16 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-01.fiche.json` (mise à jour du 14 octobre 2026), selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). `src` et `url` sont copiés depuis le premier de ces items.
2. **Relectures de fidélité.** Trois passes successives ont comparé chaque carte à ses items de base. Le texte de la fiche était leur seul juge : elles n'ont fait aucune recherche web. Elles ont corrigé 13 cartes, dont 3 à deux reprises (k21, k25, k30), sans suppression ni ajout (voir le premier tableau).
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 16 octobre 2026 : Code de commerce, ordonnances n° 45-2138, 2009-79 et 2023-1142, PCG modifié par les règlements ANC n° 2018-01, 2022-06 et 2023-03 ;
   - l'ambiguïté pédagogique : la réponse attendue est-elle celle d'un correcteur du DCG, une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a fait 3 recherches WebSearch, restreintes à `legifrance.gouv.fr` et `anc.gouv.fr` (voir « Recherches »).
4. **Validation.** `node validate.js data/ue10/ue10-01.cartes.json` : ✓ (35 cartes, dont 10 déf.).

## Bilan

- **Nombre de cartes : 35** (k01 à k25 et k27 à k36). La carte k26 a été supprimée ; son identifiant reste vide, sans renumérotation. k36 est nouvelle.
- **Répartition : 10 cartes `def` et 25 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 7 items de « Définitions » ont chacun au moins une carte : #0 k12, #1 k01, #2 k06, #3 k04, #4 k19 et k21, #5 k16 et k17, #6 k30, k31 et k32.
  - Les 18 « Règles essentielles » ont désormais toutes au moins une carte. Règles essentielles#14 (désignation d'un commissaire aux comptes dans les groupes, art. L. 821-43), seule règle sans carte jusqu'ici, est couverte par k36.
  - « Ce qui a changé récemment » : #0 k34, #1 k35, #3 k05, #4 k30.
  - « Points de vigilance » : #2 k08, #4 k33, #5 k03.
- **Items de fiche sans carte :**
  - Chiffres et seuils#0 et #1, Ce qui a changé récemment#2, Points de vigilance#1 : millésimés, le contrat leur interdit de donner une carte.
  - Chiffres et seuils#2 (rotation dans les entités d'intérêt public) : chiffres stables, mais item à reprendre dans la fiche (voir plus bas).
  - Ce qui a changé récemment#5 (programme et modalités de l'épreuve du DCG) : sans intérêt pour la mémorisation des notions.
  - Points de vigilance#0 (changement de méthode, d'estimation, correction d'erreur) : son contenu est entièrement porté par k22, k23, k24 et k25, depuis la suppression de k26.
  - Points de vigilance#3 (anciens articles L. 823-x devenus L. 821-40 et suivants) : son fond figure au verso de k05.
- **Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé.** Les seuls chiffres sont stables et font partie d'une règle (six exercices, trois exercices, deux seuils sur trois, tiers du capital). Les dates citées sont celles de textes ou de leur entrée en vigueur.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | ue10-01-k01 | La question en contenait deux (« Qu'est-ce que l'ANC et quel est son rôle ? »). | Question ramenée à « Qu'est-ce que l'Autorité des normes comptables (ANC) ? ». Réponse inchangée. |
| 1 | ue10-01-k02 | Formulation familière et vague (« Que faut-il pour que… »). | « Quelle formalité conditionne la publication au Journal officiel des règlements adoptés par l'Autorité des normes comptables (ANC) ? ». Réponse inchangée. |
| 1 | ue10-01-k09 | La dérogation à trois exercices (k10) rendait « trois exercices » aussi juste que « six ». | La question commence par « En principe, … ». |
| 1 | ue10-01-k21 | « Quel est le régime du passage à une méthode de référence ? » appelait plusieurs réponses. | « Selon le PCG, quelles sont les deux particularités du passage d'une entité à une méthode de référence ? ». |
| 1 | ue10-01-k25 | La question supposait que la correction passe toujours par le résultat ; le verso s'écartait de la fiche (« les corrections significatives figurent… »). | Nouvelle question sur l'exercice de correction ; verso : « L'incidence des corrections significatives est présentée sur une ligne séparée… ». |
| 1 | ue10-01-k28 | « Au-delà des mentions obligatoires prévues par le Code de commerce » était imprécis, R. 123-195 faisant partie du Code. | « Outre les informations obligatoires prévues notamment aux articles L. 123-13 à L. 123-21 du Code de commerce, que comporte l'annexe des comptes annuels ? ». |
| 1 | ue10-01-k30 | La question laissait croire que tout le résultat exceptionnel est lié à un événement majeur et inhabituel, alors que les écritures d'origine purement fiscale y figurent aussi. | « Selon le PCG 2025, à quel type d'événement des produits et charges doivent-ils être directement liés pour relever du résultat exceptionnel ? ». |
| 2 | ue10-01-k22 | « Si cet effet ne peut être calculé de façon objective » visait l'effet en général, la fiche vise l'effet à l'ouverture. | « Si l'effet à l'ouverture ne peut être calculé de façon objective, le changement est appliqué de manière prospective ». |
| 2 | ue10-01-k27 | « Même s'ils ne sont connus qu'après la clôture » généralisait la période ; « passifs nés » n'est pas le vocabulaire du texte. | Verso aligné sur Règles essentielles#10 : passifs « qui ont pris naissance… même s'ils ne sont connus qu'entre la date de clôture et celle de l'établissement des comptes ». |
| 2 | ue10-01-k30 | Seul l'art. 513-5 était cité, alors que le règlement ANC n° 2026-03 reprend la définition à l'art. 531-5 pour les exercices ouverts à compter du 1er janvier 2027 ; Ce qui a changé récemment#4 n'avait pas de carte. | Verso complété par la reprise à l'art. 531-5 ; base [Définitions#6, Ce qui a changé récemment#4]. |
| 3 | ue10-01-k16 | Question de 31 mots (maximum 30). | Question raccourcie à 28 mots ; réponse inchangée. |
| 3 | ue10-01-k25 | La question (« dans les comptes de quel exercice… ») et la réponse (résultat ou capitaux propres) ne correspondaient pas ; « méthode non admise » au lieu de « méthode comptable non admise ». | « Selon le PCG, où comptabilise-t-on la correction d'une erreur, d'une omission matérielle ou d'une interprétation erronée ? » ; « méthode comptable non admise ». |
| 3 | ue10-01-k21 | La question restait vague (« elle conduit à une meilleure information financière » était aussi une réponse juste). | « Selon le PCG, quelles règles s'appliquent au passage d'une entité à une méthode de référence, quant à sa justification et à sa réversibilité ? ». |
| 3 | ue10-01-k07 | « En raison de sa taille » pouvait viser la taille du groupe ; la désignation sous les seuils à la demande d'associés détenant le tiers du capital n'avait pas de carte. | Question bornée (« hors règles propres aux groupes ») ; verso complété par la demande motivée des associés représentant au moins le tiers du capital. |
| 3 | ue10-01-k05 | « Réorganise les règles de désignation, de mandat et de certification » ne reprenait pas la fiche. | L'ordonnance « place, à compter du 1er janvier 2024, les règles de désignation, de mandat et de certification des commissaires aux comptes aux articles L. 821-40 et suivants du Code de commerce ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-01-k01 | Le verso affirmait que l'ANC « donne un avis sur tout projet de disposition législative ou réglementaire applicable aux personnes tenues d'établir des documents comptables ». C'est trop large : l'article 1er de l'ordonnance n° 2009-79, dans sa version en vigueur depuis le 1er janvier 2024, limite cet avis aux projets élaborés par les autorités nationales « contenant des mesures de nature comptable ou prévoyant la publication par les entreprises d'informations sur les enjeux environnementaux, sociaux ou de gouvernance ». La restriction n'est pas dans la fiche, la carte ne peut donc pas la reprendre. | Phrase sur l'avis retirée. Le verso garde ce qui est exact et dans la fiche : l'ANC « établit, sous forme de règlements, les prescriptions comptables générales et sectorielles que doivent respecter les personnes soumises à l'obligation légale d'établir des documents comptables conformes aux normes de la comptabilité privée » (citation de l'item) et participe à l'élaboration des normes comptables européennes et internationales. 49 mots. Base, `src` et `url` inchangés. | Ordonnance n° 2009-79, art. 1er (recherche 1) ; Définitions#1 |
| ue10-01-k26 | Doublon. La carte demandait de distinguer changement de méthode, changement d'estimation et correction d'erreur ; ses trois réponses reprenaient mot pour mot celles de k22 (effet rétrospectif, report à nouveau), k23 (exercice en cours et exercices futurs) et k25 (résultat de l'exercice de constatation, sauf capitaux propres). | Carte supprimée. Son identifiant reste vide. Points de vigilance#0 reste couvert en substance par k22 à k25. | PCG, art. 122-3, 122-5 et 122-6 |
| ue10-01-k36 (ajoutée) | Règles essentielles#14 (désignation d'un commissaire aux comptes dans les groupes) était la seule règle essentielle sans carte. k07 (« hors règles propres aux groupes ») et k10 (« premier ou dernier alinéas de l'article L. 821-43 ») y renvoient sans la poser. | Nouvelle carte `comp` : « Selon l'article L. 821-43 du Code de commerce, quand une personne ou entité qui contrôle une ou plusieurs sociétés doit-elle désigner au moins un commissaire aux comptes ? ». Verso : lorsque l'ensemble qu'elle forme avec les sociétés contrôlées dépasse les seuils pour deux des trois critères, sauf si elle est elle-même contrôlée par une entité qui a désigné un commissaire aux comptes ; les sociétés contrôlées qui dépassent des seuils propres fixés par décret en désignent aussi un. Base [Règles essentielles#14]. | C. com., art. L. 821-43 ; Règles essentielles#14 |
| ue10-01-k27 | La question en posait deux (« Comment traite-t-on un passif…, et un événement postérieur… ? »), contre la règle « une seule question ». « Connu avant l'établissement des comptes » ne bornait pas non plus la période au-delà de la clôture. | Question : « Selon le Code de commerce et le PCG, comment les événements survenus ou connus entre la clôture et l'établissement des comptes annuels sont-ils pris en compte ? ». Verso : « Selon leur lien avec la situation à la clôture », puis les deux règles de Règles essentielles#10 (passifs nés au cours de l'exercice ou d'un exercice antérieur pris en compte ; événements sans lien direct prépondérant avec une situation existant à la clôture : information dans l'annexe). 62 mots. | C. com., art. L. 123-20, al. 3 ; PCG, art. 513-4 ; Règles essentielles#10 |

Les 31 autres cartes ont été jugées exactes au 16 octobre 2026 et sans ambiguïté qui justifie une retouche. Points contrôlés :

- **k25 (correction d'erreur)** : la présentation de l'incidence des corrections significatives « sur une ligne séparée du compte de résultat, en dehors du résultat courant, ou, le cas échéant, sur une ligne séparée du report à nouveau » est bien celle de l'art. 122-6 du PCG au 1er janvier 2026 (recherche 2). Le renvoi au résultat courant vise désormais l'art. 821-2.
- **k30, k31, k32 (résultat exceptionnel)** : le règlement ANC n° 2026-03 contient bien un art. 531-5 dont le texte reprend celui de l'art. 513-5 (événement majeur et inhabituel, présomption de caractère inhabituel, aides et indemnités en résultat d'exploitation) (recherche 3). La mention de k30 est donc exacte.
- **k02** : homologation par arrêtés conjoints des trois ministres (ordonnance n° 2009-79, art. 4).
- **k03** : L. 233-24 ne dispense des règles nationales que pour les comptes consolidés ; les comptes individuels restent établis selon les règles françaises.
- **k04, k05** : H2A, certification des informations en matière de durabilité par les commissaires aux comptes et les organismes tiers indépendants (ordonnance n° 2023-1142). Le recoupement de k05 avec k04 (changement de nom du H3C) est accessoire : les deux cartes posent des questions distinctes.
- **k07, k08, k09, k10, k11** : L. 227-9-1, L. 821-44, L. 821-46 et L. 821-53. Les questions délimitent leur champ (« hors règles propres aux groupes », « en principe »).
- **k12 à k18** : L. 123-12 à L. 123-20 et R. 123-178. k12 énonce la règle générale ; l'exception des micro-entreprises est l'objet de k29, bornée à L. 123-16-1.
- **k19 à k24** : PCG, art. 121-5, 122-1 à 122-5 (méthodes de référence, conditions du changement à l'initiative de l'entité, effet rétrospectif après impôt, changement d'estimation).
- **k33 à k35** : règlements ANC n° 2022-06 et 2023-03. k35 ne donne que l'intitulé du compte 757, seul intitulé qui figure sans ambiguïté dans la fiche.
- **Doublons** : k23 et k24 (même item, définition puis exception), k19 et k21, k16 et k17, k30 à k32 posent chacun une question distincte.

## Recherches

Trois recherches WebSearch ont été faites, chacune restreinte à un domaine officiel.

1. **« ordonnance 2009-79 article 1 Autorité des normes comptables donne un avis sur toute disposition législative ou réglementaire contenant des mesures de nature comptable »** (`legifrance.gouv.fr`). Le texte consolidé en vigueur depuis le 1er janvier 2024 (modifié par l'ordonnance n° 2023-1142) prévoit que l'ANC « donne un avis sur tout projet de disposition législative ou réglementaire applicable aux personnes mentionnées au 1°, élaboré par les autorités nationales, contenant des mesures de nature comptable ou prévoyant la publication par les entreprises d'informations sur les enjeux environnementaux, sociaux ou de gouvernance ». Conséquence : correction de k01. Source : [ordonnance n° 2009-79, version consolidée](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000020137892).
2. **« PCG article 122-6 corrections d'erreurs incidence ligne séparée compte de résultat report à nouveau »** (`anc.gouv.fr`). L'art. 122-6 du PCG au 1er janvier 2026 confirme : comptabilisation dans le résultat de l'exercice de constatation sauf écriture imputée directement sur les capitaux propres ; adoption d'une méthode comptable non admise assimilée à une erreur ; incidence des corrections significatives sur une ligne séparée du compte de résultat, en dehors du résultat courant (art. 821-2), ou sur une ligne séparée du report à nouveau. k25 est exacte. Sources : [PCG au 1er janvier 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/Recueils/PCG_janvier2026/PCG--1er-janvier-2026.pdf), [note de présentation du règlement ANC n° 2018-01](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2018/Reglt_2018_01_note-de-presentation.pdf).
3. **« règlement ANC 2026-03 article 531-5 résultat exceptionnel événement majeur et inhabituel produits des ventes »** (`anc.gouv.fr`). Le texte du règlement n° 2026-03 du 6 mars 2026 contient un art. 531-5 identique, à la numérotation près, à l'art. 513-5 : produits et charges directement liés à un événement majeur et inhabituel, définition de l'événement majeur, présomption de caractère inhabituel, aides et indemnités en résultat d'exploitation. k30 à k33 sont exactes ; le doute relevé dans `POINTS-OUVERTS.md` (rubrique ue10-03) sur ce numéro est levé. Source : [règlement ANC n° 2026-03](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2026/2026%20homologu%C3%A9/2026_03-JO.pdf).

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée (`maj` du 14 octobre 2026). Le point 1 est nouveau ; les points 2 à 5 reprennent ceux des relectures de fidélité, que cette relecture confirme.

1. **Définitions#1 (ANC).** L'item dit que l'ANC « donne un avis sur tout projet de disposition législative ou réglementaire applicable aux personnes tenues d'établir des documents comptables ». Le texte en vigueur limite cet avis aux projets élaborés par les autorités nationales « contenant des mesures de nature comptable ou prévoyant la publication par les entreprises d'informations sur les enjeux environnementaux, sociaux ou de gouvernance » (recherche 1). Il faut ajouter ces deux conditions, dont la seconde, issue de l'ordonnance n° 2023-1142, est nouvelle. La carte k01 a été ramenée à ce qui est sûr.
2. **Définitions#6 (résultat exceptionnel).** « Seuls les produits et charges directement liés à un événement majeur et inhabituel y sont comptabilisés » contredit Ce qui a changé récemment#0, qui y classe aussi les écritures d'origine purement fiscale. Le mot « seuls » est à nuancer.
3. **Ce qui a changé récemment#1.** « Comptes 657 et 757 « Produits des cessions d'immobilisations incorporelles et corporelles » » rattache l'intitulé aux deux comptes. Il ne vaut que pour le 757 ; le 657 est intitulé « Valeurs comptables des immobilisations incorporelles et corporelles cédées » (CONTRAT, section 4). L'item devrait donner les deux intitulés.
4. **Chiffres et seuils#2 (entités d'intérêt public).** L'item ne mentionne que les durées de 10 et 24 ans. Il semble omettre la prolongation possible après une procédure d'appel d'offres (16 ans en droit français, en application du règlement (UE) n° 537/2014). Point à vérifier sur L. 821-45, qui n'a pas fait l'objet d'une recherche ici.
5. **Points de vigilance#5.** L'URL est encore au format ancien de Légifrance (`legifrance.gouv.fr/affichCodeArticle.do?…`, sans www). Elle est à moderniser ; la carte k03 la copie à l'identique, comme le contrat l'exige.

## Classement des exercices

Le chapitre compte 26 exercices, dont 23 QCM, QCM multiples ou classements (16 QCM, 5 QCM multiples, 2 classements) et 3 calculs (`calc`). Le classement automatique des 23 premiers donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 22 | oui |
| `calcul` | 0 | — |
| `chiffre` | 1 | non |

Les classeurs n'ont relevé aucun désaccord.

- Les 22 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable.
- L'exercice de nature `chiffre` est le QCM sur les seuils de nomination d'un commissaire aux comptes dans une SAS « en 2025 ». Il reste dans le chapitre, mais il n'est pas proposé en révision.
- Les 3 exercices `calc` sont de nature `calcul` par construction et restent hors des révisions espacées.
