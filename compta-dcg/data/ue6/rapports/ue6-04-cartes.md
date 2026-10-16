# Cartes de notions : ue6-04 (Choix d'investissement : actualisation, VAN, TRI)

*15 octobre 2026*

Fichier : `data/ue6/ue6-04.cartes.json`. Fiche de référence : `data/ue6/ue6-04.fiche.json` (non modifiée, mise à jour du 14 octobre 2026). Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 34 cartes (k01 à k34) ont été écrites à partir de la seule fiche du chapitre, dans le cadre de la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité.** Un premier relecteur a contrôlé les 34 cartes par rapport à la fiche. Il en a corrigé 6, en a supprimé 2 (k32 et k33) et a mis à jour la date `maj`.
3. **Relecture d'exactitude.** C'est la présente relecture, faite par un second relecteur indépendant. Il a contrôlé les 32 cartes restantes sur quatre points :
   - **Exactitude** au 15 octobre 2026 : CGI, Code de la consommation et Code monétaire et financier (taux effectif global), PCG modifié par le règlement ANC n° 2022-06.
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse juste serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand l'item de fiche était lui-même en cause, la fiche n'a pas été touchée. La carte a été corrigée pour rester exacte tout en restant portée par ses items de base, et l'item est signalé plus bas.
4. **Recherches.** Une seule recherche web a été faite, limitée à legifrance.gouv.fr (détail plus bas).

Validation : `node validate.js data/ue6/ue6-04.cartes.json` renvoie « ✓ data/ue6/ue6-04.cartes.json (cartes, 32 (14 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes rédigées | 34 |
| Cartes contrôlées par la relecture d'exactitude | 32 |
| Cartes au final | 32 |
| Définition (`def`) | 14 |
| Compréhension (`comp`) | 18 |
| Corrigées par la relecture d'exactitude | 6 (k04, k07, k18, k27, k28, k29) |
| Supprimées par la relecture d'exactitude | 0 |
| Ajoutées | 0 |
| Identifiants libres | k32, k33 (pas de renumérotation) |

Chacun des neuf items de la section « Définitions » a au moins une carte. Les onze « Règles essentielles » sont toutes couvertes.

**Items de la fiche sans carte**

- **Chiffres et seuils#0 et #1** : taux normal de l'IS et taux réduit des PME (millésimé 2025). Ce sont des taux fixés par la loi de finances, exclus des révisions.
- **Chiffres et seuils#3** : modalités de l'épreuve de l'UE6, sans notion à retenir.
- **Ce qui a changé récemment#1** : calendrier du programme. La carte k33, qui le portait, a été supprimée par la première relecture.
- **Ce qui a changé récemment#2, #3 et #4** : taux réduit d'IS et contribution exceptionnelle sur les bénéfices des grandes entreprises. Ces items sont millésimés (2025 ou 2026).
- **Points de vigilance#4** : prérequis du programme du DSCG. La carte k32, qui le portait, a été supprimée par la première relecture.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis s'arrête au milieu de la raison de la suppression de k32 (« L'identifiant… »). La suppression de k33 n'y figure donc pas : elle a été reconstituée à partir de l'historique du fichier.

| Cible | Problème | Correction |
|---|---|---|
| k01 | Une phrase de la réponse portait sur le programme du DSCG (« range ce lien entre la valeur et le temps parmi les acquis attendus de l'UE6 ») et non sur la notion. Elle n'aidait pas à retenir la définition de la capitalisation. | Phrase supprimée. Réponse : « Calculer la valeur acquise d'un capital C placé n périodes au taux i, soit C × (1 + i)^n. » |
| k02 | Même problème que k01 : une phrase portait sur le programme du DSCG et non sur l'actualisation. | Phrase supprimée. Réponse : « Calculer la valeur aujourd'hui d'un flux futur F, soit F × (1 + i)^−n. » |
| k03 | La réponse reprenait la mention du programme du DSCG, une méta-information qui n'est pas la réponse attendue. | Réponse réduite à « Le coût du capital, c'est-à-dire le coût moyen pondéré des ressources. » |
| k05 | La réponse se terminait par « C'est le montant de l'investissement initial, hors taxes. » (reprise de Définitions#3). Lue seule, cette phrase laissait croire que l'investissement initial se réduit au coût d'acquisition, alors que Règles essentielles#0 y ajoute l'augmentation du BFR d'exploitation. Elle contredisait donc k06. | Dernière phrase : « Il entre, hors taxes, dans l'investissement initial du projet, avec l'augmentation du BFR d'exploitation induite. » Base : Définitions#3 et Règles essentielles#0 (`src` et `url` inchangés). |
| k14 | La question en contenait deux (« Quel flux retient-on … et pourquoi ? »). | Question : « Au titre de la valeur résiduelle d'un bien cédé en fin de projet d'investissement, quel flux retient-on ? ». Réponse inchangée : le flux (valeur résiduelle nette d'impôt), puis la raison (plus-value imposable). |
| k29 | Faute d'accord : l'Insee (l'Institut) est masculin. | Question : « Comment l'Insee décompose-t-il une évolution en valeur ? » (la carte a ensuite été reformulée par la relecture d'exactitude). |
| k32 (supprimée) | La carte demandait quels acquis de l'UE6 le programme du DSCG pose en prérequis (Points de vigilance#4). C'est une question sur le contenu d'un programme, sans notion à définir ni règle à comprendre. *(Raison tronquée dans le résultat transmis.)* | Carte supprimée. L'identifiant reste libre. |
| k33 (supprimée) | *(Absente du résultat transmis ; reconstituée à partir de l'historique.)* La carte demandait quel texte fixe le programme de l'UE6 à compter de la session 2027 (Ce qui a changé récemment#1). C'est aussi une question sur un programme, sans notion à retenir. | Carte supprimée. L'identifiant reste libre. |
| fichier | La date `maj` n'était pas à jour après les modifications. | `maj` passe à 2026-10-16. |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k04 | Deux problèmes. (1) La question attribuait la définition du taux effectif global au Code monétaire et financier. Or les règles de calcul figurent aux articles R. 314-1 à R. 314-14 du **Code de la consommation**, auxquels renvoie l'article R. 313-1 du Code monétaire et financier. (2) La réponse présentait le TEG comme « un taux calculé actuariellement ». Pour les crédits professionnels, le TEG est en fait proportionnel au taux de période : c'est le taux de période qui est calculé actuariellement, puis multiplié par le rapport entre l'année et la période. La question « qu'est-ce que le TEG ? » admettait en outre d'autres réponses justes, par exemple le coût total du crédit, frais compris. | Nouvelle question, sans nom de code : « Quelle égalité le calcul actuariel du taux effectif global d'un prêt assure-t-il ? ». Nouvelle réponse : « L'égalité entre les sommes prêtées et l'ensemble des versements dus par l'emprunteur, selon la méthode des intérêts composés. C'est la logique du TRI : le taux qui égalise la valeur actuelle des flux et le montant investi. » `src` reste celui de la fiche (Définitions#1), qui est signalé plus bas. | C. consom., art. R. 314-2 ; C. mon. fin., art. R. 313-1 (recherche n° 1) |
| k07 | Réponse vraie seulement dans le cas général non dit. La TVA grevant une immobilisation n'est pas toujours déductible : véhicules conçus pour transporter des personnes, activités exonérées, coefficient de déduction partiel. Dans ces cas, la TVA non récupérable fait partie du coût d'acquisition. La question présupposait une exclusion sans réserve. | Question : « Pourquoi la TVA grevant une immobilisation est-elle **en principe** exclue de l'investissement initial et des flux d'un projet d'investissement ? ». Ajout, en fin de réponse : « Une TVA non déductible serait, elle, un coût du projet. » Base inchangée : Points de vigilance#0 et Règles essentielles#0. | CGI, art. 271 et ann. II, art. 206 ; PCG, art. 213-8 (taxes non récupérables incluses dans le coût d'acquisition) ; fiche : Définitions#3 |
| k18 | La phrase « Une VAN négative d'un actif en service signale ainsi une dépréciation possible » est inexacte. Le test de dépréciation compare la valeur nette comptable à la valeur actuelle, c'est-à-dire à la plus élevée de la valeur vénale et de la valeur d'usage. Il ne compare pas des flux futurs au coût d'origine de l'actif. Un actif peut avoir une « VAN » négative par rapport à son coût d'origine sans être déprécié, si les flux attendus couvrent sa valeur nette comptable ou si sa valeur vénale est plus élevée. | Nouvelle réponse : « Au test de dépréciation des immobilisations. Avec la valeur vénale, elle sert à déterminer la valeur actuelle de l'actif (la plus élevée des deux), que l'on compare à sa valeur nette comptable. » Base : Points de vigilance#3 et Définitions#2 (`src` et `url` inchangés). | PCG, art. 214-6 (valeur actuelle, valeur vénale, valeur d'usage) |
| k27 | La seconde phrase (« Le programme la prévoit… ») était une information sur le programme, du même type que celles que la première relecture a retirées de k01 à k03. | Seconde phrase : « Elle sert à départager des projets de durées différentes. » | Fiche : Règles essentielles#7 |
| k28 | Même méta-information sur le programme. La définition ne disait pas jusqu'à quand les flux intermédiaires sont capitalisés. | Réponse : « Un critère dans lequel les flux intermédiaires sont capitalisés jusqu'à la fin du projet à un taux de réinvestissement explicite. Il sert à départager les projets d'investissement. » | Fiche : Règles essentielles#7 |
| k29 | La question (« Comment l'Insee décompose-t-il une évolution en valeur ? ») portait sur une convention statistique qu'un correcteur du DCG n'interroge pas. La relation utile au chapitre ne venait qu'en appendice de la réponse, sans être écrite. | Nouvelle question : « Quelle relation lie le taux nominal, le taux réel et le taux d'inflation ? ». Nouvelle réponse : « (1 + taux nominal) = (1 + taux réel) × (1 + inflation). C'est la décomposition de l'Insee, où l'indice de valeur est égal à l'indice de volume multiplié par l'indice de prix. » La carte vise l'erreur classique de l'addition des taux. Base inchangée : Définitions#8, qui énonce cette relation. | Fiche : Définitions#8 |

**Cartes contrôlées et maintenues sans changement** : k01 à k03, k05, k06, k08 à k17, k19 à k26, k30, k31 et k34.

- **k10.** Les coefficients du dégressif (1,25, 1,75 et 2,25) sont ceux de l'article 39 A, 1 du CGI. Ils sont stables depuis la fin de la majoration temporaire de 2009-2010 et font partie de la règle. La carte reste admise.
- **k11.** La carte ne cite aucun taux d'IS chiffré.
- **k20, k22 et k34.** Ces cartes énoncent l'équivalence VAN positive, TRI supérieur au coût du capital et indice de profitabilité supérieur à 1, chacune à partir d'un critère différent. Elles ne posent pas la même question. L'équivalence suppose un projet classique (décaissement initial puis encaissements), qui est le cadre du DCG.
- **k14 et k15** se recoupent sur les comptes 657 et 757, mais l'une porte sur le flux à retenir, l'autre sur l'apport du règlement ANC n° 2022-06.
- **k26.** L'hypothèse de réinvestissement au TRI est la réponse attendue au DCG ; la fiche la rattache au programme (VAN globale, TRI global).

## Recherches faites

Une recherche sur les trois autorisées.

1. `code monétaire et financier R. 314-2 taux effectif global proportionnel au taux de période calculé actuariellement` (domaine legifrance.gouv.fr). Les résultats établissent trois points :
   - L'article R. 314-2 relève du **Code de la consommation** (chapitre IV, articles R. 314-1 à D. 314-29) et non du Code monétaire et financier.
   - L'article R. 313-1 du Code monétaire et financier renvoie, pour le taux effectif global, aux articles R. 314-1 à R. 314-14 du Code de la consommation.
   - Selon le texte, « le taux de période est calculé actuariellement, à partir d'une période unitaire correspondant à la périodicité des versements effectués par l'emprunteur ». Pour les crédits professionnels, le TEG s'obtient en multipliant le taux de période par le rapport entre la durée de l'année civile et celle de la période unitaire.

   Ces résultats fondent la correction de k04 et le point n° 1 ci-dessous. Pages consultées :
   - [C. mon. fin., art. R. 313-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000047256405)
   - [C. consom., art. R. 314-2](https://legifrance.gouv.fr/affichCodeArticle.do?cidTexte=LEGITEXT000006069565&dateTexte=20161001&idArticle=LEGIARTI000032807606)
   - [C. consom., chapitre IV, art. R. 314-1 à D. 314-29](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006069565/LEGISCTA000032807598/2019-12-27/)

Les autres points ont été vérifiés sans recherche, à partir des textes connus : CGI, art. 39 A, 1, 219, I-b, 271 et ann. II, art. 206 ; PCG, art. 213-8 et 214-6.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Définitions#1, Définitions#6 (`src`) et la liste `textes`.** La référence « C. mon. fin., art. R. 314-2 et R. 314-3 » est erronée. Les règles de calcul du taux effectif global figurent aux articles R. 314-1 à R. 314-14 du **Code de la consommation**, auxquels renvoie l'article R. 313-1 du Code monétaire et financier. Par ailleurs, pour les crédits professionnels, le TEG n'est pas lui-même « calculé actuariellement » : il est proportionnel au taux de période, et c'est ce taux de période qui est calculé actuariellement. Les cartes k04 et k23 recopient ce `src` erroné, comme le contrat l'impose.
2. **Points de vigilance#3.** « Une VAN négative d'un actif en service signale une dépréciation possible » est inexact. Le test compare la valeur nette comptable à la valeur actuelle, c'est-à-dire à la plus élevée de la valeur vénale et de la valeur d'usage (PCG, art. 214-6).
3. **Règles essentielles#0 et Points de vigilance#0.** La TVA est dite déductible sans réserve. Il faudrait ajouter « en principe » et rappeler que la TVA exclue du droit à déduction (véhicules de transport de personnes, activités exonérées, coefficient de déduction) reste un coût, incluse dans le coût d'acquisition (PCG, art. 213-8 : « taxes non récupérables »).
4. **Chiffres et seuils#0 et Règles essentielles#1.** Le taux normal de l'IS (25 %) est fixé par la loi de finances. Ces items sont marqués `stable` alors qu'ils contiennent ce taux : il faudrait les marquer millésimés, ou retirer le taux de Règles essentielles#1. La même remarque a été faite pour la fiche ue6-02.
5. **Ce qui a changé récemment#2 (à vérifier).** La conclusion « un projet porté par une filiale de groupe est donc imposé au taux normal » est trop générale. Le taux réduit dépend aussi du capital, qui doit être entièrement libéré et détenu pour 75 % au moins par des personnes physiques ou par des sociétés remplissant les mêmes conditions (CGI, art. 219, I-b). L'appréciation du chiffre d'affaires au niveau du groupe vise les groupes fiscaux au sens de l'article 223 A. Une filiale n'est donc pas imposée au taux normal du seul fait de son appartenance à un groupe. La portée exacte de la décision du Conseil d'État citée n'a pas été vérifiée. Aucune carte ne repose sur cet item.

## Classement des exercices

Un classement automatique a porté sur les 18 exercices de type QCM, QCM multiple et classement du chapitre (les 10 exercices `calc` sont par nature des calculs) :

| Nature | Nombre |
|---|---|
| notion | 11 (8 QCM, 2 QCM multiples, 1 classement) |
| calcul | 7 (QCM) |
| chiffre | 0 |

**Désaccords** : aucun. Les deux classements concordent sur les 18 exercices.

Les 11 exercices de nature notion entrent dans les révisions espacées, avec les 32 cartes.
