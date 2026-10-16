# Cartes de notions : ue6-04 (Choix d'investissement : actualisation, VAN, TRI)

*15 octobre 2026*

Fichier : `data/ue6/ue6-04.cartes.json`. Fiche de référence : `data/ue6/ue6-04.fiche.json` (non modifiée, mise à jour du 14 octobre 2026). Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 34 cartes (k01 à k34) ont été écrites à partir de la seule fiche du chapitre, dans le cadre de la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité.** Un premier relecteur vérifie que chaque carte dit ce que dit la fiche, sans rien ajouter, et qu'elle respecte la forme exigée. Il ne fait aucune recherche web.
3. **Relecture d'exactitude.** Un second relecteur, indépendant, contrôle chaque carte sur quatre points :
   - **Exactitude** au 15 octobre 2026 : CGI, Code monétaire et financier et Code de la consommation (taux effectif global), PCG modifié par le règlement ANC n° 2022-06, programme de l'UE6 applicable à partir de la session 2027.
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse juste serait-elle possible ?
   - **Doublons et cartes sans intérêt**, y compris la carte dont la réponse donne celle d'une autre carte.
   - **Aucun calcul, aucun chiffre millésimé.**

   Quand l'item de fiche lui-même est en cause, la fiche n'est pas modifiée. La carte est corrigée pour rester à la fois exacte et portée par ses items de base, et l'item est signalé plus bas.
4. **Deux cycles de relecture.**
   - **Cycle précédent.** La relecture de fidélité a corrigé six cartes et supprimé k32 et k33. La relecture d'exactitude a corrigé k04, k07, k18, k27, k28 et k29, après une recherche sur legifrance.gouv.fr. Il restait 32 cartes (rappel plus bas).
   - **Reprise (ce rapport).** Une nouvelle relecture de fidélité a contrôlé les 32 cartes et en a corrigé quatre (k06, k07, k18, k28). Elle a notamment retiré de k07 et de k18 deux phrases ajoutées au cycle précédent, que la fiche ne porte pas. La relecture d'exactitude a ensuite recontrôlé les 32 cartes. Elle en a corrigé sept (k05, k14, k21, k23, k26, k30, k31) et a supprimé k34, fusionnée dans k23. Elle n'a rien ajouté.
5. **Recherches.** Aucune lors de la reprise (détail plus bas).

Validation : `node validate.js data/ue6/ue6-04.cartes.json` renvoie « ✓ data/ue6/ue6-04.cartes.json (cartes, 31 (14 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées (reprise) | 32 |
| Cartes au final | 31 |
| Définition (`def`) | 14 |
| Compréhension (`comp`) | 17 |
| Corrigées par la relecture de fidélité (reprise) | 4 (k06, k07, k18, k28) |
| Corrigées par la relecture d'exactitude (reprise) | 7 (k05, k14, k21, k23, k26, k30, k31) |
| Supprimées / ajoutées (reprise) | 1 (k34) / 0 |
| Identifiants libres | k32, k33, k34 (pas de renumérotation) |

Les neuf items de la section « Définitions » et les onze « Règles essentielles » ont tous au moins une carte. Les points de vigilance #0 à #3 et le changement récent #0 donnent des cartes de compréhension (k07, k12, k15, k18, k25, k26).

**Items de la fiche sans carte**, tous écartés volontairement :

- **Chiffres et seuils#0 et #1** : taux normal de l'IS et taux réduit des PME (millésimé 2025). Ce sont des taux fixés par la loi de finances, exclus des révisions espacées.
- **Chiffres et seuils#3** : modalités de l'épreuve de l'UE6, sans notion à retenir.
- **Ce qui a changé récemment#1** : calendrier du programme. La carte k33, qui le portait, a été supprimée au cycle précédent.
- **Ce qui a changé récemment#2, #3 et #4** : taux réduit d'IS et contribution exceptionnelle sur les bénéfices des grandes entreprises. Ces items sont millésimés (2025 ou 2026).
- **Points de vigilance#4** : prérequis du programme du DSCG. La carte k32, qui le portait, a été supprimée au cycle précédent.

## Corrections de la première relecture (fidélité à la fiche, reprise)

Résultat : 32 cartes contrôlées, 4 corrigées, aucune supprimée ni ajoutée, aucune recherche web. Le résultat transmis s'arrête au milieu de son premier point de fiche (« Définitions#1 : la définition du taux effectif global est attr… ») ; ce point rejoint le n° 1 de la liste plus bas.

| Cible | Problème | Correction |
|---|---|---|
| k07 | La dernière phrase de la réponse (« Une TVA non déductible serait, elle, un coût du projet. ») n'est portée par aucun des items de base (Points de vigilance#0, Règles essentielles#0). Ces deux items disent seulement que la TVA est déductible et n'est pas un coût. La phrase venait d'une connaissance extérieure. | Phrase supprimée. Nouvelle réponse : « <b>Parce qu'elle est déductible</b> : ce n'est pas un coût, on raisonne hors taxes. Elle n'affecte que le BFR si le sujet le précise. » La question garde « en principe », ce qui délimite le champ sans rien affirmer de plus. Base, `src` et `url` inchangés. |
| k18 | La seconde phrase de la réponse (« Avec la valeur vénale, elle sert à déterminer la valeur actuelle de l'actif (la plus élevée des deux), que l'on compare à sa valeur nette comptable. ») ne figure ni dans Points de vigilance#3 ni dans Définitions#2 : c'est une connaissance extérieure à la fiche. Le mot « test » de la question restait par ailleurs implicite. | Q : « En comptabilité, à quel test portant sur les immobilisations sert la valeur d'usage définie par le PCG ? » R : « <b>Au test de dépréciation des immobilisations.</b> Déterminée, dans la généralité des cas, en fonction des flux nets de trésorerie attendus, elle constitue la base comptable de l'évaluation d'un investissement par ses flux. » Tout le contenu vient de PV#3 et Déf.#2. La phrase de PV#3 sur la VAN négative, jugée inexacte par la relecture précédente, n'a pas été reprise. Base, `src` et `url` inchangés. |
| k28 | La précision « capitalisés jusqu'à la fin du projet » n'est pas dans Règles essentielles#7, qui dit seulement « à un taux de réinvestissement explicite ». La question visait aussi deux notions à la fois (« la VAN globale (ou le TRI global) »), avec une réponse au singulier (« Un critère »). | Q : « Dans la VAN globale et le TRI global d'un projet d'investissement, comment les flux intermédiaires sont-ils traités ? » R : « <b>Ils sont capitalisés à un taux de réinvestissement explicite.</b> Ces deux critères, comme l'annuité équivalente, servent à départager les projets d'investissement. » Le type passe de `def` à `comp`, puisque la question porte sur le traitement des flux. Base, `src` et `url` inchangés. |
| k06 | Le type était faux. « De quoi se compose l'investissement initial » demande la définition d'une notion par ses composantes. Ce n'est ni une condition, ni un effet, ni une raison d'être. La carte k11, construite de la même façon (flux net de trésorerie d'exploitation), est déjà en `def`. | Le type passe de `comp` à `def`. Question, réponse, base, `src` et `url` inchangés. |

## Corrections de la relecture d'exactitude (reprise)

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k05 | Doublon partiel. La dernière phrase (« Il entre, hors taxes, dans l'investissement initial du projet, avec l'augmentation du BFR d'exploitation induite ») donnait mot pour mot la réponse de k06 (composantes de l'investissement initial). Revoir k05 donnait donc k06. | Phrase retirée. Réponse : « <b>Le prix d'achat</b>, après déduction des remises et des taxes récupérables, <b>augmenté de tous les coûts directement attribuables</b> engagés pour mettre l'actif en place et en état de fonctionner. » La définition reste conforme à l'article 213-8 du PCG. Base réduite à Définitions#3 (`src` et `url` inchangés). | PCG, art. 213-8 ; contrat §8 (doublons) |
| k14 | Doublon partiel. La seconde phrase (« enregistrée pour son prix en 757 et la valeur comptable sortie en 657 ») donnait la réponse de k15, qui porte précisément sur le passage des cessions en 657 / 757 avec le règlement ANC n° 2022-06. La raison du flux net d'impôt restait, elle, peu expliquée. | Réponse : « <b>La valeur résiduelle nette d'impôt</b> : la plus-value de cession, égale au prix de cession diminué de la valeur comptable du bien, est imposable. » Le contenu vient de Règles essentielles#3 (prix en 757, valeur comptable en 657, plus-value imposable). Question, base, `src` et `url` inchangés. | CGI, art. 39 duodecies ; fiche, Règles essentielles#3 |
| k21 | Vraie seulement dans un cas non dit. Entre projets exclusifs, on ne retient le projet de VAN la plus élevée que si cette VAN est positive. Si toutes les VAN sont négatives, aucun projet n'est acceptable. | Réponse : « <b>Celui dont la VAN est la plus élevée</b>, à condition qu'elle soit positive. Chaque VAN est calculée au coût du capital. » La condition vient du même item (Règles essentielles#5 : projet acceptable si VAN positive). | Fiche, Règles essentielles#5 |
| k23 et k34 (k34 supprimée) | Doublon. k34 (« Selon le critère du TRI, à quelle condition un projet est-il acceptable ? ») et k20 (même question selon le critère de la VAN) avaient la même réponse, l'équivalence entre VAN positive, TRI supérieur au coût du capital et indice de profitabilité supérieur à 1, simplement énoncée dans un autre ordre. k22 redonne en outre l'équivalence avec l'indice. | La règle de décision du TRI rejoint la carte de définition du TRI. Réponse de k23 : « <b>Le taux d'actualisation pour lequel la VAN est nulle.</b> Un projet est acceptable si son TRI est supérieur au coût du capital. Sans calculatrice financière, le TRI s'encadre entre deux taux puis s'estime par interpolation linéaire. » Base : Définitions#6 et Règles essentielles#5 (`src` et `url` de Définitions#6, inchangés). k34 est supprimée ; l'identifiant reste libre. | Contrat §8 (doublons, fusion) ; fiche, Règles essentielles#5 |
| k26 | Doublon partiel. La seconde phrase (« en capitalisant les flux intermédiaires à un taux de réinvestissement explicite ») donnait la réponse de k28, qui porte sur le traitement des flux intermédiaires dans la VAN globale et le TRI global. | Réponse : « <b>Un réinvestissement des flux au TRI lui-même.</b> C'est cette hypothèse que la VAN globale corrige. » Base réduite à Points de vigilance#1, qui porte toute la réponse (`src` et `url` inchangés). | Contrat §8 (doublons) ; fiche, Points de vigilance#1 |
| k30 | Doublon partiel. La seconde phrase écrivait la relation (1 + nominal) = (1 + réel) × (1 + inflation), qui est la réponse même de k29. | Seconde phrase : « Les deux approches donnent la même VAN si le taux nominal, le taux réel et l'inflation respectent la relation multiplicative qui les lie. » La règle d'actualisation (euros courants au taux nominal, euros constants au taux réel) ne change pas. | Contrat §8 (doublons) ; fiche, Règles essentielles#8 et Définitions#8 |
| k31 | Question sur le contenu d'un programme (« quels outils le programme de l'UE6 prévoit-il ? »), du même type que k32 et k33, supprimées au cycle précédent. La réponse, une liste de trois outils hétérogènes, dépendait en outre du programme de 2019, abrogé à compter de la session 2027 (fiche, `textes`). Enfin, l'analyse de sensibilité n'est pas propre à l'avenir probabilisable. | Q : « En avenir probabilisable, quels paramètres statistiques de la VAN des scénarios calcule-t-on pour prendre en compte le risque d'un projet d'investissement ? » R : « <b>Son espérance et son écart-type.</b> On recourt aussi à un arbre de décision pour les choix séquentiels et à une analyse de sensibilité des hypothèses. » Une seule réponse attendue (un correcteur admettra la variance pour l'écart-type). Base, `src` et `url` inchangés. | Fiche, Règles essentielles#9 et `textes` (arrêté du 13 février 2019 abrogé à compter de la session 2027) |

**Cartes contrôlées et maintenues sans changement** : k01 à k04, k06 à k13, k15 à k20, k22, k24, k25, k27 à k29 (24 cartes). Les corrections de la relecture de fidélité sont acceptées :

- **k07.** La TVA grevant une immobilisation n'est pas toujours déductible : véhicules de transport de personnes, activités exonérées, coefficient de déduction partiel (CGI, ann. II, art. 206). La question garde « en principe », ce qui suffit à la rendre exacte. L'item de fiche reste signalé.
- **k18.** La réponse ne reprend plus la phrase inexacte de Points de vigilance#3. Elle reste juste : le test de dépréciation compare la valeur nette comptable à la valeur actuelle, plus élevée de la valeur vénale et de la valeur d'usage (PCG, art. 214-5 et 214-6).
- **k28.** La VAN globale capitalise les flux intermédiaires jusqu'à l'horizon du projet, puis actualise cette valeur acquise ; la réponse, plus brève, reste exacte.

Quatre autres cartes appellent une remarque :

- **k04** recopie, comme le contrat l'impose, le `src` de Définitions#1 (« C. mon. fin., art. R. 314-2 et R. 314-3 »), erroné (voir le n° 1 plus bas). La question, resserrée au cycle précédent, reste juste : c'est le calcul actuariel (du taux de période, pour un crédit professionnel) qui assure l'égalité entre sommes prêtées et versements. La même remarque vaut pour le `src` de k23.
- **k09 et k11.** L'économie d'impôt sur les dotations suppose une entreprise globalement imposable, hypothèse du DCG. Les cartes ne citent aucun taux d'IS chiffré.
- **k10.** Les coefficients du dégressif (1,25, 1,75 et 2,25) sont ceux de l'article 39 A, 1 du CGI, inchangés depuis la fin de la majoration temporaire de 2009-2010. Ils font partie de la règle : la carte reste admise.
- **k20 et k22.** Après la suppression de k34, l'équivalence complète entre VAN positive, TRI supérieur au coût du capital et indice de profitabilité supérieur à 1 n'est plus énoncée que dans k20 (règle de la VAN). La règle du TRI figure dans k23 (définition du TRI), celle de l'indice dans k22 (définition de l'indice). L'équivalence suppose un projet classique (décaissement initial puis encaissements), cadre du DCG.

## Rappel du cycle précédent

| Cible | Correction |
|---|---|
| k01, k02, k03 | Retrait des phrases sur le programme du DSCG, sans lien avec la notion (relecture de fidélité). |
| k04 | Question resserrée sur l'égalité qu'assure le calcul actuariel du taux effectif global, sans nom de code (relecture d'exactitude, après recherche sur legifrance.gouv.fr). |
| k05 | Dernière phrase réécrite pour ne pas réduire l'investissement initial au coût d'acquisition (relecture de fidélité) ; retirée lors de la reprise. |
| k07 | « En principe » ajouté à la question (relecture d'exactitude). |
| k14 | Question limitée au flux retenu (relecture de fidélité). |
| k18 | Retrait de la phrase sur la VAN négative d'un actif en service (relecture d'exactitude). |
| k27, k28 | Retrait des informations sur le programme (relecture d'exactitude). |
| k29 | Question recentrée sur la relation entre taux nominal, taux réel et inflation (relectures de fidélité et d'exactitude). |
| k32, k33 | Supprimées : questions sur le contenu des programmes, sans notion à retenir (relecture de fidélité). |

## Recherches faites

**Reprise : aucune recherche** (0 sur les 3 autorisées). Aucun point n'a laissé de doute réel :

- le taux effectif global avait déjà été vérifié au cycle précédent ;
- les autres points relèvent de textes connus et stables : CGI, art. 39, 1-2°, 39 A, 39 duodecies, 271 et ann. II, art. 206 ; PCG, art. 213-8, 214-5, 214-6 et 214-13 ; règlement ANC n° 2022-06 ;
- les corrections de la reprise tiennent pour l'essentiel aux doublons et à l'ambiguïté, et se règlent avec la fiche.

**Cycle précédent : une recherche**, limitée à legifrance.gouv.fr (`code monétaire et financier R. 314-2 taux effectif global proportionnel au taux de période calculé actuariellement`). Elle a établi trois points :

- l'article R. 314-2 relève du Code de la consommation ;
- l'article R. 313-1 du Code monétaire et financier y renvoie pour le taux effectif global ;
- pour les crédits professionnels, le TEG est proportionnel au taux de période, et c'est ce taux de période qui est calculé actuariellement.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Définitions#1, Définitions#6 (`src`) et la liste `textes`.** La référence « C. mon. fin., art. R. 314-2 et R. 314-3 » est erronée. Les règles de calcul du taux effectif global figurent aux articles R. 314-1 à R. 314-14 du **Code de la consommation** (issus du décret n° 2016-884 du 29 juin 2016, que la fiche cite d'ailleurs), auxquels renvoie l'article R. 313-1 du Code monétaire et financier. Pour les crédits professionnels, le TEG n'est pas lui-même « calculé actuariellement » : il est proportionnel au taux de période, et c'est ce taux de période qui est calculé actuariellement. Les cartes k04 et k23 recopient ce `src` erroné, comme le contrat l'impose.
2. **Points de vigilance#3.** « Une VAN négative d'un actif en service signale une dépréciation possible » est inexact. Le test compare la valeur nette comptable à la valeur actuelle, c'est-à-dire à la plus élevée de la valeur vénale et de la valeur d'usage (PCG, art. 214-5 et 214-6). Aucune carte ne reprend plus cette phrase.
3. **Règles essentielles#0 et Points de vigilance#0.** La TVA est dite déductible sans réserve. Il faudrait ajouter « en principe » et rappeler que la TVA exclue du droit à déduction (véhicules de transport de personnes, activités exonérées, coefficient de déduction) reste un coût, inclus dans le coût d'acquisition (PCG, art. 213-8 : « taxes non récupérables »).
4. **Chiffres et seuils#0 et Règles essentielles#1.** Le taux normal de l'IS (25 %) est fixé par la loi de finances. Ces items sont marqués `stable` alors qu'ils contiennent ce taux : il faudrait les marquer millésimés, ou retirer le taux de Règles essentielles#1.
5. **Définitions#5, Définitions#6, Règles essentielles#4, #5 et #9 (`src` et `url`).** Ces items citent l'arrêté du 13 février 2019, que la fiche dit elle-même abrogé à compter de la session 2027. Au 15 octobre 2026, la prochaine session est celle de 2027 : il faudrait les rattacher à l'annexe 1 de l'arrêté du 4 août 2025, et vérifier que la liste des outils de prise en compte du risque (Règles essentielles#9 : espérance et écart-type, arbre de décision, analyse de sensibilité) figure bien dans ce programme.
6. **Ce qui a changé récemment#2 (à vérifier).** La conclusion « un projet porté par une filiale de groupe est donc imposé au taux normal » est trop générale. Le taux réduit dépend aussi du capital, qui doit être entièrement libéré et détenu pour 75 % au moins par des personnes physiques ou par des sociétés remplissant les mêmes conditions (CGI, art. 219, I-b). L'appréciation du chiffre d'affaires au niveau du groupe vise les groupes au sens de l'article 223 A. Une filiale n'est donc pas imposée au taux normal du seul fait de son appartenance à un groupe. La portée exacte de la décision du Conseil d'État citée n'a pas été vérifiée. Aucune carte ne repose sur cet item.

## Classement des exercices

Un classement automatique a porté sur les 18 exercices de type QCM, QCM multiple et classement du chapitre. Les 10 exercices `calc` sont par nature des calculs et n'en font pas partie.

| Nature | Nombre |
|---|---|
| notion | 11 (8 QCM, 2 QCM multiples, 1 classement) |
| calcul | 7 (QCM) |
| chiffre | 0 |

**Désaccords** : aucun. Les deux classements concordent sur les 18 exercices.

Les 11 exercices de nature notion entrent dans les révisions espacées, avec les 31 cartes.
