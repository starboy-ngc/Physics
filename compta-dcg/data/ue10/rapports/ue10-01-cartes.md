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

   Elle s'est faite en deux temps. Une première passe a corrigé k01 et k27, supprimé k26 et ajouté k36, avec 3 recherches. Une reprise a ensuite relu les 35 cartes de l'état obtenu, revérifié ces quatre modifications, puis corrigé k04 et k07, avec 2 recherches. Les 5 recherches sont restreintes à `legifrance.gouv.fr` ou `anc.gouv.fr` (voir « Recherches »).
4. **Validation.** `node validate.js data/ue10/ue10-01.cartes.json` : ✓ (35 cartes, dont 10 déf.).

## Bilan

- **Nombre de cartes : 35** (k01 à k25 et k27 à k36). La carte k26 a été supprimée ; son identifiant reste vide, sans renumérotation. k36 est nouvelle.
- **Répartition : 10 cartes `def` et 25 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 7 items de « Définitions » ont chacun au moins une carte : #0 k12, #1 k01, #2 k06, #3 k04, #4 k19 et k21, #5 k16 et k17, #6 k30, k31 et k32.
  - Les 18 « Règles essentielles » ont toutes au moins une carte. Règles essentielles#14 (désignation d'un commissaire aux comptes dans les groupes, art. L. 821-43) est couverte par k36.
  - « Ce qui a changé récemment » : #0 k34, #1 k35, #3 k05, #4 k30.
  - « Points de vigilance » : #2 k08, #4 k33, #5 k03.
- **Items de fiche sans carte :**
  - Chiffres et seuils#0 et #1, Ce qui a changé récemment#2, Points de vigilance#1 : ces items sont millésimés, et le contrat leur interdit de donner une carte.
  - Chiffres et seuils#2 (rotation dans les entités d'intérêt public) : ses chiffres sont stables, mais l'item est à reprendre dans la fiche (voir plus bas).
  - Ce qui a changé récemment#5 (programme et modalités de l'épreuve du DCG) : sans intérêt pour la mémorisation des notions.
  - Points de vigilance#0 (changement de méthode, d'estimation, correction d'erreur) : depuis la suppression de k26, son contenu est entièrement porté par k22, k23, k24 et k25.
  - Points de vigilance#3 (anciens articles L. 823-x devenus L. 821-40 et suivants) : son fond figure au verso de k05.
  - Règles essentielles#3, seconde phrase (biens fongibles : coût moyen pondéré ou « premier entré, premier sorti ») et Règles essentielles#13, dernière phrase (désignation demandée en justice par des associés représentant au moins le dixième du capital) : seules ces deux parties d'items n'ont pas de carte.
- **Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé.** Les seuls chiffres sont stables et font partie d'une règle : six exercices, trois exercices, deux seuils sur trois, tiers du capital. Les dates citées sont celles de textes ou de leur entrée en vigueur.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | ue10-01-k01 | La question en contenait deux (« Qu'est-ce que l'ANC et quel est son rôle ? »). | Question ramenée à « Qu'est-ce que l'Autorité des normes comptables (ANC) ? ». Réponse inchangée. |
| 1 | ue10-01-k02 | Formulation familière et vague (« Que faut-il pour que… »). | « Quelle formalité conditionne la publication au Journal officiel des règlements adoptés par l'Autorité des normes comptables (ANC) ? ». Réponse inchangée. |
| 1 | ue10-01-k09 | La dérogation à trois exercices (k10) rendait « trois exercices » aussi juste que « six ». | La question commence par « En principe, … ». |
| 1 | ue10-01-k21 | « Quel est le régime du passage à une méthode de référence ? » appelait plusieurs réponses. | « Selon le PCG, quelles sont les deux particularités du passage d'une entité à une méthode de référence ? ». |
| 1 | ue10-01-k25 | La question supposait que la correction passe toujours par le résultat. Le verso s'écartait de la fiche (« les corrections significatives figurent… »). | Nouvelle question sur l'exercice de correction. Verso : « L'incidence des corrections significatives est présentée sur une ligne séparée… ». |
| 1 | ue10-01-k28 | « Au-delà des mentions obligatoires prévues par le Code de commerce » était imprécis, puisque R. 123-195 fait lui-même partie du Code. | « Outre les informations obligatoires prévues notamment aux articles L. 123-13 à L. 123-21 du Code de commerce, que comporte l'annexe des comptes annuels ? ». |
| 1 | ue10-01-k30 | La question laissait croire que tout le résultat exceptionnel est lié à un événement majeur et inhabituel. Or les écritures d'origine purement fiscale y figurent aussi. | « Selon le PCG 2025, à quel type d'événement des produits et charges doivent-ils être directement liés pour relever du résultat exceptionnel ? ». |
| 2 | ue10-01-k22 | « Si cet effet ne peut être calculé de façon objective » visait l'effet en général ; la fiche vise l'effet à l'ouverture. | « Si l'effet à l'ouverture ne peut être calculé de façon objective, le changement est appliqué de manière prospective ». |
| 2 | ue10-01-k27 | « Même s'ils ne sont connus qu'après la clôture » généralisait la période. « Passifs nés » n'est pas le vocabulaire du texte. | Verso aligné sur Règles essentielles#10 : passifs « qui ont pris naissance… même s'ils ne sont connus qu'entre la date de clôture et celle de l'établissement des comptes ». |
| 2 | ue10-01-k30 | Seul l'art. 513-5 était cité. Or le règlement ANC n° 2026-03 reprend la définition à l'art. 531-5 pour les exercices ouverts à compter du 1er janvier 2027. Ce qui a changé récemment#4 n'avait pas de carte. | Verso complété par la reprise à l'art. 531-5. Base : [Définitions#6, Ce qui a changé récemment#4]. |
| 3 | ue10-01-k16 | Question de 31 mots (maximum 30). | Question raccourcie à 28 mots. Réponse inchangée. |
| 3 | ue10-01-k25 | La question (« dans les comptes de quel exercice… ») et la réponse (résultat ou capitaux propres) ne correspondaient pas. Le verso disait « méthode non admise » au lieu de « méthode comptable non admise ». | « Selon le PCG, où comptabilise-t-on la correction d'une erreur, d'une omission matérielle ou d'une interprétation erronée ? ». Verso : « méthode comptable non admise ». |
| 3 | ue10-01-k21 | La question restait vague : « elle conduit à une meilleure information financière » était aussi une réponse juste. | « Selon le PCG, quelles règles s'appliquent au passage d'une entité à une méthode de référence, quant à sa justification et à sa réversibilité ? ». |
| 3 | ue10-01-k07 | « En raison de sa taille » pouvait viser la taille du groupe. La désignation sous les seuils à la demande d'associés détenant le tiers du capital n'avait pas de carte. | Question bornée (« hors règles propres aux groupes »). Verso complété par la demande motivée des associés représentant au moins le tiers du capital. |
| 3 | ue10-01-k05 | « Réorganise les règles de désignation, de mandat et de certification » ne reprenait pas la fiche. | L'ordonnance « place, à compter du 1er janvier 2024, les règles de désignation, de mandat et de certification des commissaires aux comptes aux articles L. 821-40 et suivants du Code de commerce ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-01-k01 (1re passe) | Le verso disait que l'ANC « donne un avis sur tout projet de disposition législative ou réglementaire applicable aux personnes tenues d'établir des documents comptables ». C'est trop large. L'article 1er de l'ordonnance n° 2009-79, en vigueur depuis le 1er janvier 2024, limite cet avis aux projets élaborés par les autorités nationales « contenant des mesures de nature comptable ou prévoyant la publication par les entreprises d'informations sur les enjeux environnementaux, sociaux ou de gouvernance ». Cette restriction n'est pas dans la fiche, la carte ne peut donc pas la reprendre. | Phrase sur l'avis retirée. Le verso garde ce qui est exact et figure dans la fiche : l'ANC établit, sous forme de règlements, les prescriptions comptables générales et sectorielles que doivent respecter les personnes soumises à l'obligation légale d'établir des documents comptables conformes aux normes de la comptabilité privée, et elle participe à l'élaboration des normes comptables européennes et internationales. Base, `src` et `url` inchangés. | Ordonnance n° 2009-79, art. 1er (recherche 1) ; Définitions#1 |
| ue10-01-k26 (1re passe) | Doublon. La carte demandait de distinguer changement de méthode, changement d'estimation et correction d'erreur. Ses trois réponses reprenaient mot pour mot celles de k22, k23 et k25. | Carte supprimée ; son identifiant reste vide. Points de vigilance#0 reste couvert en substance par k22 à k25. | PCG, art. 122-3, 122-5 et 122-6 |
| ue10-01-k36 (ajoutée, 1re passe) | Règles essentielles#14 (désignation d'un commissaire aux comptes dans les groupes) était la seule règle essentielle sans carte. k07 (« hors règles propres aux groupes ») et k10 (« premier ou dernier alinéas de l'article L. 821-43 ») y renvoient sans la poser. | Nouvelle carte `comp` : « Selon l'article L. 821-43 du Code de commerce, quand une personne ou entité qui contrôle une ou plusieurs sociétés doit-elle désigner au moins un commissaire aux comptes ? ». Verso : quand l'ensemble qu'elle forme avec les sociétés contrôlées dépasse les seuils pour deux des trois critères, sauf si elle est elle-même contrôlée par une entité qui a désigné un commissaire aux comptes ; les sociétés contrôlées qui dépassent des seuils propres fixés par décret en désignent aussi un. | C. com., art. L. 821-43 ; Règles essentielles#14 |
| ue10-01-k27 (1re passe) | La question en posait deux (« Comment traite-t-on un passif…, et un événement postérieur… ? »), contre la règle « une seule question ». | Question : « Selon le Code de commerce et le PCG, comment les événements survenus ou connus entre la clôture et l'établissement des comptes annuels sont-ils pris en compte ? ». Verso : « Selon leur lien avec la situation à la clôture », puis les deux règles de Règles essentielles#10. | C. com., art. L. 123-20, al. 3 ; PCG, art. 513-4 ; Règles essentielles#10 |
| ue10-01-k07 (reprise) | Le verso disait que, « depuis la loi PACTE, ces seuils sont les mêmes quelle que soit la forme de la société ». C'est vrai seulement des sociétés commerciales, et la carte ne le disait pas. Les sociétés civiles ayant une activité économique relèvent de l'article L. 612-1 : leurs seuils sont fixés par décret en Conseil d'État et diffèrent de ceux de D. 221-5. Le décret n° 2019-514, lui, ne vise que les sociétés commerciales. | Incise supprimée, car elle était accessoire : la carte porte sur la SAS. Le verso garde les seuils de D. 221-5 et la désignation à la demande motivée d'associés représentant au moins le tiers du capital. Il passe de 69 à 51 mots. Base inchangée. | C. com., art. L. 227-9-1 et L. 612-1 ; décret n° 2019-514 (recherche 5) ; Règles essentielles#13 |
| ue10-01-k04 (reprise) | « Qu'est-ce que la Haute autorité de l'audit (H2A) ? » admettait une autre réponse juste : « l'autorité publique indépendante qui supervise les commissaires aux comptes ». La carte attendait seulement « le nouveau nom du H3C ». | Question : « De quelle autorité la Haute autorité de l'audit (H2A) est-elle le nouveau nom depuis l'ordonnance n° 2023-1142 du 6 décembre 2023 ? ». Verso : « <b>Du Haut Conseil du commissariat aux comptes (H3C)</b>, renommé compte tenu de l'extension de ses missions à la supervision des auditeurs des informations en matière de durabilité. La H2A succède au H3C dans ses droits et obligations depuis le 1er janvier 2024. » Type `def`, base, `src` et `url` inchangés. | Ordonnance n° 2023-1142, art. 32 et 40 ; Définitions#3 |

Les 29 autres cartes ont été jugées exactes au 16 octobre 2026, et aucune ambiguïté ne justifiait de les retoucher. Points contrôlés :

- **k02** : homologation par arrêtés conjoints des trois ministres (ordonnance n° 2009-79, art. 4).
- **k03** : L. 233-24 ne dispense des règles nationales que pour les comptes consolidés ; les comptes individuels restent établis selon les règles françaises.
- **k05** : certification des informations en matière de durabilité par les commissaires aux comptes et les organismes tiers indépendants (ordonnance n° 2023-1142). Les reports de calendrier et la réduction du champ de la CSRD décidés depuis 2025 ne changent pas qui peut certifier. Le verso rappelle le changement de nom du H3C, mais la question de k05 reste distincte de celle de k04.
- **k06** : définition de l'expert-comptable (ordonnance n° 45-2138, art. 2).
- **k08, k09, k10, k11** : L. 227-9-1 (appréciation à la clôture), L. 821-44, L. 821-46 et L. 821-53. Les questions délimitent leur champ (« en principe »).
- **k12 à k18** : L. 123-12 à L. 123-20 et R. 123-178. k12 énonce la règle générale. L'exception des micro-entreprises fait l'objet de k29, dont le champ est borné à L. 123-16-1.
- **k19 à k25** : PCG, art. 121-5 et 122-1 à 122-6. Ils couvrent les méthodes de référence, les conditions d'un changement à l'initiative de l'entité, l'irréversibilité du passage à une méthode de référence et l'effet rétrospectif après impôt. S'y ajoutent le changement d'estimation et la correction d'erreur ; la ligne séparée hors résultat courant de k25 a été confirmée par la recherche 2.
- **k28, k29** : R. 123-195 et L. 123-16-1.
- **k30 à k34** : la recherche 4 a confirmé le texte de l'art. 513-5 du PCG au 1er janvier 2026 : événement majeur, présomption de caractère inhabituel et aides reçues en compensation de charges d'exploitation classées en résultat d'exploitation. Elle a aussi confirmé que les produits et charges ultérieurs restent en résultat exceptionnel « jusqu'à l'extinction de ces conséquences » (k33) et que les écritures d'origine purement fiscale vont en résultat exceptionnel (k34). La recherche 3 a confirmé la reprise du texte à l'art. 531-5 par le règlement ANC n° 2026-03 (k30).
- **k35** : comptes 657 et 757 depuis le règlement ANC n° 2023-03. Seul l'intitulé du 757 est donné, car c'est le seul que la fiche énonce sans ambiguïté.
- **k36** : L. 821-43, revérifiée.
- **Doublons** : les paires k23 et k24 (définition, puis exception), k19 et k21, k16 et k17, k07, k08 et k36, k04 et k05, et la série k30 à k34 posent chacune des questions distinctes.

## Recherches

Cinq recherches WebSearch ont été faites, chacune restreinte à un domaine officiel. Les trois premières datent de la première passe d'exactitude, les deux dernières de sa reprise.

1. **« ordonnance 2009-79 article 1 Autorité des normes comptables donne un avis sur toute disposition législative ou réglementaire contenant des mesures de nature comptable »** (`legifrance.gouv.fr`). Dans le texte consolidé en vigueur depuis le 1er janvier 2024, l'avis porte sur les projets élaborés par les autorités nationales « contenant des mesures de nature comptable ou prévoyant la publication par les entreprises d'informations sur les enjeux environnementaux, sociaux ou de gouvernance ». Conséquence : correction de k01. Source : [ordonnance n° 2009-79, version consolidée](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000020137892).
2. **« PCG article 122-6 corrections d'erreurs incidence ligne séparée compte de résultat report à nouveau »** (`anc.gouv.fr`). L'art. 122-6 du PCG au 1er janvier 2026 confirme la règle : correction dans le résultat de l'exercice de constatation, sauf écriture imputée directement sur les capitaux propres ; l'adoption d'une méthode comptable non admise est traitée comme une erreur ; l'incidence des corrections significatives figure sur une ligne séparée. k25 est exacte. Source : [PCG au 1er janvier 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/Recueils/PCG_janvier2026/PCG--1er-janvier-2026.pdf).
3. **« règlement ANC 2026-03 article 531-5 résultat exceptionnel événement majeur et inhabituel produits des ventes »** (`anc.gouv.fr`). Le règlement n° 2026-03 du 6 mars 2026 contient un art. 531-5 qui reprend l'art. 513-5, à la numérotation près. k30 est exacte. Source : [règlement ANC n° 2026-03](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2026/2026%20homologu%C3%A9/2026_03-JO.pdf).
4. **« règlement ANC 2022-06 article 513-5 résultat exceptionnel événement majeur inhabituel extinction des conséquences exercices ultérieurs »** (`anc.gouv.fr`). Le texte de l'art. 513-5 confirme quatre règles :
   - la présomption de caractère inhabituel (« lorsqu'un même évènement ne s'est pas produit au cours des derniers exercices comptables et qu'il est peu probable qu'il se reproduise au cours des prochains exercices comptables ») ;
   - le classement des produits et charges ultérieurs en résultat exceptionnel « jusqu'à l'extinction de ces conséquences » ;
   - le classement en résultat d'exploitation des aides, remboursements et indemnités reçus en compensation de charges d'exploitation ;
   - le classement en résultat exceptionnel des écritures d'origine purement fiscale.

   k31 à k34 sont exactes. Sources : [règlement ANC n° 2022-06](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2022/R2022_06/R2022_06.pdf), [version commentée](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2022/R2022_06/R2022_06_version-commentee.pdf), [PCG au 1er janvier 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/PCG--1er-janvier-2026.pdf).
5. **« article D. 612-5 code de commerce personnes morales de droit privé non commerçantes ayant une activité économique commissaire aux comptes seuils… »** (`legifrance.gouv.fr`). L'article L. 612-1 soumet les personnes morales de droit privé non commerçantes ayant une activité économique, dont les sociétés civiles, à un régime distinct de désignation du commissaire aux comptes. Leurs seuils sont fixés par décret en Conseil d'État (articles R. 612-1 et suivants). Le décret n° 2019-514, qui a harmonisé les seuils après la loi PACTE, vise les sociétés commerciales. La recherche n'a pas restitué les montants en vigueur de ce régime distinct, et la carte n'en cite aucun. Conséquence : correction de k07 et point 6 ci-dessous. Sources : [C. com., art. R. 612-1 à R. 612-7](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000005634379/LEGISCTA000006146267/), [décret n° 2019-514](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038505937).

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée (`maj` du 14 octobre 2026). Le point 6 est nouveau. Le point 1 vient de la première passe d'exactitude. Les points 2 à 5 reprennent ceux des relectures de fidélité, que la relecture d'exactitude confirme.

1. **Définitions#1 (ANC).** L'item dit que l'ANC « donne un avis sur tout projet de disposition législative ou réglementaire applicable aux personnes tenues d'établir des documents comptables ». Le texte en vigueur limite cet avis aux projets élaborés par les autorités nationales « contenant des mesures de nature comptable ou prévoyant la publication par les entreprises d'informations sur les enjeux environnementaux, sociaux ou de gouvernance » (recherche 1). L'item doit ajouter ces deux conditions. La carte k01 a été ramenée à ce qui est sûr.
2. **Définitions#6 (résultat exceptionnel).** « Seuls les produits et charges directement liés à un événement majeur et inhabituel y sont comptabilisés » contredit Ce qui a changé récemment#0, qui y classe aussi les écritures d'origine purement fiscale (confirmé par la recherche 4). Le mot « seuls » est à nuancer.
3. **Ce qui a changé récemment#1.** « Comptes 657 et 757 « Produits des cessions d'immobilisations incorporelles et corporelles » » rattache l'intitulé aux deux comptes. Il ne vaut que pour le 757. Le 657 s'intitule « Valeurs comptables des immobilisations incorporelles et corporelles cédées » (CONTRAT, section 4). L'item devrait donner les deux intitulés.
4. **Chiffres et seuils#2 (entités d'intérêt public).** L'item ne mentionne que les durées de 10 et 24 ans. Il semble omettre la prolongation possible après une procédure d'appel d'offres (16 ans, en application du règlement (UE) n° 537/2014). Le point est à vérifier sur L. 821-45, qui n'a pas fait l'objet d'une recherche ici.
5. **Points de vigilance#5.** L'URL est encore au format ancien de Légifrance (`legifrance.gouv.fr/affichCodeArticle.do?…`, sans www). Elle est à moderniser. La carte k03 la copie à l'identique, comme le contrat l'exige.
6. **Règles essentielles#13 (désignation du commissaire aux comptes).** « Depuis la loi PACTE, ces seuils sont les mêmes quelle que soit la forme de la société » est trop général. L'harmonisation vaut pour les sociétés commerciales (SA, SAS, SARL, SNC, SCS). Les sociétés civiles ayant une activité économique relèvent de l'article L. 612-1 et de seuils propres (recherche 5). Il faut écrire « quelle que soit la forme de la société commerciale ». La carte k07 n'en dit plus rien.

## Classement des exercices

Le chapitre compte 26 exercices :

- 23 QCM, QCM multiples ou classements (16 QCM, 5 QCM multiples, 2 classements) ;
- 3 calculs (`calc`).

Le classement automatique des 23 premiers donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 22 | oui |
| `calcul` | 0 | — |
| `chiffre` | 1 | non |

Les classeurs n'ont relevé aucun désaccord.

- Les 22 exercices de nature `notion` (15 QCM, 5 QCM multiples, 2 classements) entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable.
- L'exercice de nature `chiffre` est le QCM sur les seuils de nomination d'un commissaire aux comptes dans une SAS « en 2025 ». Il reste dans le chapitre, mais il n'est pas proposé en révision.
- Les 3 exercices `calc` sont de nature `calcul` par construction et restent hors des révisions espacées.
