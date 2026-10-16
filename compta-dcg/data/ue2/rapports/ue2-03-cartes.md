# Cartes de notions : ue2-03 (La SA et la SAS)

15 octobre 2026. Fichier : `data/ue2/ue2-03.cartes.json`. Fiche de référence : `data/ue2/ue2-03.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Le premier relecteur a contrôlé les 35 cartes au regard de la fiche et en a corrigé 7 (k02, k09, k11, k22, k27, k28, k31). Il n'a fait ni suppression ni ajout.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code de commerce, Code civil, Code monétaire et financier et Code de la sécurité sociale. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse, et il a recherché les doublons. Bilan : 4 cartes corrigées (k04, k07, k09, k28), sans suppression ni ajout. La correction de k28 retire une phrase que la première relecture avait ajoutée : la règle qu'elle reprenait est abrogée depuis le 1er octobre 2025.
4. **Recherches.** 3 recherches WebSearch sur 3 autorisées, toutes sur legifrance.gouv.fr : article L. 227-9 après l'ordonnance n° 2025-229, article L. 227-15 et article L. 225-42.

`node validate.js data/ue2/ue2-03.cartes.json` : ✓ (35 cartes, 6 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 6 de définition (`def` : k01, k03, k09, k18, k20, k23) et 29 de compréhension (`comp`). Les identifiants k01 à k35 se suivent sans trou.
- Chaque item des sections « Définitions » et « Règles essentielles » a au moins une carte.
- **Items de la fiche sans carte :**
  - **Chiffres et seuils#0** (capital minimal de 37 000 €) : k21 dit que l'article L. 224-2 (capital minimal) ne s'applique pas à la SAS. Aucune carte ne porte sur le montant lui-même.
  - **Chiffres et seuils#1 et #6** (nombre d'associés, d'administrateurs, de membres du directoire et de directeurs généraux délégués ; 5 % du capital, plus de 10 % des droits de vote, deux ans) : ces chiffres sont repris dans k01, k03, k04, k06, k08, k09 et k17, sans être cités dans `base`.
  - **Chiffres et seuils#2** (limites d'âge et cumul des mandats) : ce sont des règles supplétives chiffrées. Le jeu étant au plafond de 35 cartes, il n'y a pas de place pour une carte supplémentaire.
  - **Chiffres et seuils#4** et **Ce qui a changé récemment#2** (seuils du commissaire aux comptes) : items millésimés, exclus des cartes.
  - **Chiffres et seuils#5** (droits d'enregistrement de 0,1 %, 3 % et 5 %) : une carte se réduirait au rappel de taux fiscaux.
  - **Ce qui a changé récemment#3** (renumérotation des articles relatifs au commissaire aux comptes) : une carte se réduirait au rappel de numéros d'articles.
  - **Points de vigilance#4** (périmètre d'examen) : c'est un point de programme, pas une règle de droit.
- **Contenus couverts en partie :** cinq points de la fiche n'ont pas de carte :
  - la durée des fonctions des administrateurs (Règles essentielles#1) ;
  - les quorums de l'AGO et de l'AGE, les assemblées spéciales et le changement de nationalité (Règles essentielles#6 et #7) ;
  - la prescription de l'action en responsabilité (Règles essentielles#10) ;
  - l'application de l'article L. 225-43 aux dirigeants de SAS (Règles essentielles#15) ;
  - la sanction des décisions prises en violation de l'article L. 227-9 (Règles essentielles#12). Cette sanction est abrogée (voir ci-dessous).

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la première relecture est tronqué au milieu de la ligne k31. La fin de cette ligne a été complétée en comparant le fichier avec sa version commitée (commit 95746d3).

| cible | problème | correction |
|---|---|---|
| k09 | La définition ne citait qu'une exclusion, celle des opérations courantes conclues à des conditions normales, et pouvait laisser croire qu'elle était la seule. Elle omettait la seconde exclusion de la fiche (Définitions#3) : les conventions entre deux sociétés dont l'une détient la totalité du capital de l'autre. Citer les deux en toutes lettres aurait porté la réponse au-delà de 70 mots. | « en sont exclues » devient « en sont notamment exclues ». La réponse fait 60 mots. Les deux exclusions restent détaillées dans k11. |
| k11 | Le verbe « restent libres » ne vient pas de la fiche, qui écrit « Sont exclues ». Le contrat demande de garder le vocabulaire juridique de la fiche. | La question se termine désormais par « échappent pourtant à ce régime ? » (24 mots). Réponse inchangée. |
| k02 | Couverture : aucune carte ne portait sur l'interdiction des apports en industrie dans la SA (Règles essentielles#0). Le jeu est déjà au plafond de 35 cartes. | Ajout d'une précision tirée du même item : « Les apports en industrie, eux, ne peuvent pas être représentés par des actions de SA. » La réponse passe à 42 mots. Base, src et url inchangés. |
| k22 | Couverture : aucune carte ne portait sur les actions inaliénables que la SAS peut émettre en rémunération d'apports en industrie (Règles essentielles#11). C'est le pendant de la règle de la SA. | Ajout tiré du même item : « Ses statuts peuvent en revanche prévoir l'émission d'actions inaliénables résultant d'apports en industrie. » La réponse passe à 55 mots. |
| k27 | Couverture : aucune carte ne portait sur les règles de la SAS à associé unique (Règles essentielles#12). | Ajout d'une phrase tirée de cet item, qui est la base de la carte : « Dans la SAS à associé unique, celui-ci approuve les comptes dans les six mois de la clôture, ne peut déléguer ses pouvoirs, et ses décisions sont répertoriées dans un registre. » La réponse fait 68 mots. |
| k28 | Couverture : aucune carte ne portait sur la sanction des décisions prises en violation des règles des décisions collectives obligatoires (Règles essentielles#12). | Ajout tiré du même item : « Les décisions prises en violation de ces règles peuvent être annulées à la demande de tout intéressé. » La réponse passait à 42 mots. **Phrase retirée ensuite par la relecture d'exactitude** (voir ci-dessous). |
| k31 | Une passe précédente, interrompue, avait déjà corrigé cette carte ; la correction a été trouvée non commitée dans l'arbre de travail. L'ancienne question était fermée, à réponse oui ou non : « peut-il être privé du droit de voter… ? ». | Correction gardée après contrôle. La question porte désormais sur le sort de la stipulation statutaire qui prive de son droit de vote l'associé dont l'exclusion dépend d'une décision collective. La réponse commence par « Elle est réputée non écrite (Cass. com., 29 mai 2024) ». Elle ajoute que l'associé reste en droit de participer à la décision et de voter (C. civ., art. 1844). |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k28 | La phrase « Les décisions prises en violation de ces règles peuvent être annulées à la demande de tout intéressé » reprenait le quatrième alinéa de l'article L. 227-9. L'article 42 de l'ordonnance n° 2025-229 du 12 mars 2025 a supprimé cet alinéa, applicable jusqu'au 1er octobre 2025. Depuis, la nullité des décisions relève des articles 1844-10 à 1844-17 du Code civil. Pour la violation des règles statutaires, elle relève de l'article L. 227-20-1 : la nullité n'est encourue que si les statuts la prévoient. La phrase énonçait donc une règle abrogée. | Phrase retirée. La réponse revient à : « La fusion, la scission, la dissolution et la transformation. Pour le reste, les statuts déterminent les décisions qui doivent être prises collectivement par les associés. » (25 mots). Base inchangée. Le régime actuel de la nullité reste traité par k33. | Ordonnance n° 2025-229 du 12 mars 2025, art. 42 et 70 ; C. com., art. L. 227-9 et L. 227-20-1 ; recherche n° 1 |
| k04 | « Celui-ci peut être assisté d'un à cinq directeurs généraux délégués » rattachait les directeurs généraux délégués au seul directeur général distinct du président. Or, lorsque le président du conseil assume la direction générale, les dispositions relatives au directeur général lui sont applicables. Le PDG peut donc lui aussi être assisté de directeurs généraux délégués. | « Dans les deux formules, celui qui assume la direction générale peut être assisté d'un à cinq directeurs généraux délégués. » (44 mots) | C. com., art. L. 225-51-1 et L. 225-53 |
| k07 | « Pour quels faits… engagent-ils leur responsabilité ? » admettait une autre réponse juste : les infractions pénales propres aux dirigeants de SA (abus de biens sociaux, distribution de dividendes fictifs…). Or le verso ne porte que sur la responsabilité civile de l'article L. 225-251. | Question délimitée : « … engagent-ils leur responsabilité civile ? ». Réponse inchangée. | C. com., art. L. 225-251 et L. 225-253 |
| k09 | La définition vise le directeur général, les directeurs généraux délégués et les administrateurs, donc la SA à conseil d'administration. Or la question visait toute SA. Dans la SA à directoire et conseil de surveillance, les conventions réglementées sont celles passées avec un membre du directoire ou du conseil de surveillance. Le verso n'était donc vrai que pour l'une des deux formes, sans que la question le dise. | Question délimitée : « Qu'est-ce qu'une convention réglementée dans une société anonyme (SA) à conseil d'administration ? » (13 mots). Réponse inchangée. | C. com., art. L. 225-38 et L. 225-86 |

Les autres cartes ont été contrôlées sans changement : k01 à k03, k05, k06, k08, k10 à k27 et k29 à k35. Points examinés sans modification :

- **k13** (sanctions des conventions réglementées) et **k29** (nullité des cessions faites en violation des clauses statutaires de SAS) : l'ordonnance n° 2025-229 n'a modifié ni l'article L. 225-42 ni l'article L. 227-15 (recherches n° 2 et 3).
- **k33** : la recherche n° 1 confirme le contenu de l'article L. 227-20-1.
- **k17** : dans les sociétés cotées, le droit de vote double est de droit, sauf clause contraire des statuts. Les conditions de libération et d'inscription nominative depuis deux ans au nom du même actionnaire restent les mêmes. La carte est donc exacte en l'état.
- **k05 et k24** : elles posent la même règle de l'acte étranger à l'objet social, mais pour deux dirigeants différents (directeur général de SA, président de SAS). La comparaison étant utile, ce n'est pas un doublon.
- **k09 et k11** : elles se recoupent sur l'exclusion des opérations courantes. Chacune a sa propre question (la définition et les exclusions).

## Recherches faites

3 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr.

1. Requête « article L227-9 code de commerce décisions prises en violation annulées à la demande de tout intéressé ordonnance 2025-229 ».
   - **Infirmé (règle abrogée).** Dans sa version en vigueur du 1er janvier 2009 au 1er octobre 2025, l'article L. 227-9 prévoyait que les décisions prises en violation de ses dispositions pouvaient être annulées à la demande de tout intéressé. L'article 42 de l'ordonnance n° 2025-229 supprime ce quatrième alinéa. Le rapport au Président de la République le confirme : l'article 42 supprime la nullité textuelle des décisions prises en violation des règles relatives aux décisions collectives de SAS.
   - L'article L. 227-20-1 permet aux statuts de prévoir la nullité des décisions prises en violation des règles qu'ils fixent. L'action relève des articles 1844-10 à 1844-17 du Code civil. Le tout est applicable depuis le 1er octobre 2025 (art. 70).
   - Effet : correction de k28 ; k33 confirmée ; point 1 à reprendre dans la fiche.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000019291762/ ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316108 ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316022
2. Requête « article L227-15 code de commerce cession effectuée en violation des clauses statutaires est nulle version en vigueur ».
   - **Confirmé.** L'article L. 227-15 n'a pas été modifié depuis le 21 septembre 2000 : toute cession effectuée en violation des clauses statutaires est nulle.
   - Selon Cass. com., 21 juin 2023, n° 21-25.952, cette nullité ne vise que les cessions librement consenties. Elle ne s'applique ni à l'exclusion ni à la cession forcée qui en découle.
   - Effet : k29 exacte.
   - Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006227152
3. Requête « article L225-42 code de commerce conventions conclues sans autorisation préalable du conseil d'administration peuvent être annulées conséquences dommageables version en vigueur 2025 ».
   - **Confirmé.** L'article L. 225-42 est en vigueur dans sa rédaction issue de la loi n° 2019-486 du 22 mai 2019 : les conventions conclues sans autorisation préalable peuvent être annulées si elles ont eu des conséquences dommageables pour la société.
   - L'action se prescrit par trois ans à compter de la convention ou, si elle a été dissimulée, de sa révélation. La nullité peut être couverte par un vote de l'assemblée intervenant sur rapport spécial du commissaire aux comptes ou, à défaut, du président du conseil.
   - Effet : k13 exacte.
   - Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038610414/2026-05-16

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#12** (SAS : décisions collectives obligatoires). La dernière phrase, « Les décisions prises en violation de ces règles peuvent être annulées à la demande de tout intéressé », reprend le quatrième alinéa de l'article L. 227-9. L'article 42 de l'ordonnance n° 2025-229 a supprimé cet alinéa, applicable jusqu'au 1er octobre 2025 (recherche n° 1). Il faut retirer cette phrase ou la remplacer par le régime actuel : articles 1844-10 à 1844-17 du Code civil et, pour la violation des règles statutaires, article L. 227-20-1. La même règle abrogée figure dans la leçon du chapitre (`data/ue2/ue2-03.json`, `lecon[5]` « La SAS : liberté statutaire encadrée », qui cite « L. 227-9, dernier alinéa ») : elle est à corriger au même titre.
2. **Ce qui a changé récemment#0** (complément). L'item pourrait mentionner que l'ordonnance n° 2025-229 a supprimé la nullité textuelle de l'article L. 227-9 (art. 42).
3. **Règles essentielles#2** (direction générale). Dans « le directeur général, qui peut être assisté d'un à cinq directeurs généraux délégués », la relative ne vise que le directeur général distinct du président. Or les directeurs généraux délégués peuvent aussi assister le président qui assume la direction générale, auquel s'appliquent les dispositions relatives au directeur général (L. 225-51-1 et L. 225-53). Une précision suffit.
4. **Définitions#3** (conventions réglementées de la SA). L'item énumère le directeur général, les directeurs généraux délégués et les administrateurs : il ne vaut que pour la SA à conseil d'administration. Dans la SA à directoire et conseil de surveillance, l'article L. 225-86 vise les membres du directoire et du conseil de surveillance. L'item pourrait le préciser.
5. **Règles essentielles#8** (droit de vote double, complément mineur). Dans les sociétés dont les actions sont admises aux négociations sur un marché réglementé, le droit de vote double est de droit, sauf clause contraire des statuts (C. com., art. L. 22-10-46). L'item ne présente que l'attribution par les statuts ou par une assemblée générale extraordinaire, qui est le régime de la SA non cotée.

## Classement des exercices

Le classement automatique porte sur les 26 exercices QCM, QCM multiples et classements du chapitre (23 QCM, 2 QCM multiples, 1 classement) :

| nature | nombre |
|---|---|
| notion | 23 |
| calcul | 2 |
| chiffre | 1 |

Aucun désaccord entre les classements. Les exercices qui sortent des révisions espacées sont les suivants :

- **calcul** (2 QCM) :
  - #6 : nombre maximal d'administrateurs de plus de 70 ans dans un conseil de neuf membres ;
  - #16 : adoption d'une résolution d'AGO à partir d'un décompte de voix, avec abstentions.
- **chiffre** (1 QCM) : #19 (seuils de désignation du commissaire aux comptes applicables aux exercices ouverts depuis 2024, millésimés).

La base de calcul des majorités (#16) et la désignation du commissaire aux comptes (#19) restent révisées par les cartes k16 et k34. La limite d'âge des administrateurs (#6) n'a pas de carte (Chiffres et seuils#2). Les 23 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes. L'exercice #21 (QCM multiple sur les décisions collectives obligatoires de SAS) reste exact : il ne porte que sur l'alinéa 2 de l'article L. 227-9, toujours en vigueur.
