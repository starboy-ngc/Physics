# Cartes de notions : ue2-06 (Entreprises en difficulté et droit pénal des affaires)

16 octobre 2026. Fichier : `data/ue2/ue2-06.cartes.json`. Fiche de référence : `data/ue2/ue2-06.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Deux passes successives ont confronté les 35 cartes au texte de leurs items de base, sans recherche web (la consigne de ces passes l'excluait). La première a corrigé 6 cartes (k01, k07, k08, k13, k16, k29). La seconde a corrigé 4 cartes (k08, k13, k25, k27) et vérifié 2 corrections reprises d'une passe interrompue (k07, k14). Aucune suppression ni aucun ajout.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 16 octobre 2026 : Code de commerce (livre VI, droit pénal des sociétés, commissariat aux comptes réorganisé par l'ordonnance n° 2023-1142), Code civil, Code pénal, Code de procédure pénale. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse, celle qu'attendrait un correcteur du DCG, et il a recherché les doublons et les cartes sans intérêt. Cette relecture s'est faite en deux temps. Une première passe, interrompue avant son compte rendu, a corrigé 6 cartes (k13, k15, k18, k24, k27, k28). La reprise a relu ces 6 corrections, qu'elle a gardées, puis les 29 autres cartes, et elle en a corrigé 2 de plus (k17, k20). Bilan : 8 cartes corrigées, aucune suppression et aucun ajout.
4. **Recherches.** 3 recherches WebSearch sur les 3 autorisées, toutes faites lors de la première passe et limitées à legifrance.gouv.fr : sauvegarde accélérée et cessation des paiements (C. com., art. L. 628-1), sûretés nulles en période suspecte (art. L. 632-1), réunion des patrimoines de l'entrepreneur individuel (art. L. 621-2). La reprise n'en a fait aucune : ses deux corrections reposent sur la lettre d'articles stables (art. L. 641-3 et L. 641-9).

`node validate.js data/ue2/ue2-06.cartes.json` : ✓ (35 cartes, 15 déf.).

## Bilan

- **35 cartes**, soit le maximum prévu par le contrat : 15 de définition (`def`) et 20 de compréhension (`comp`). Les identifiants k01 à k35 se suivent sans trou.
- Chaque item des sections « Définitions » (#0 à #4) et « Règles essentielles » (#0 à #16) a au moins une carte.
- **Items de la fiche sans carte :**
  - **Chiffres et seuils#0, #1, #2 et #3** : délais, durées, seuils fixés par décret et peines. Les seuils de la liquidation simplifiée et des classes (#2) relèvent d'un décret et sont exclus. Les délais et peines stables sont repris dans des cartes de règle (k06, k13, k17, k27, k33), sans que ces items soient cités dans `base`.
  - **Chiffres et seuils#6** : délit d'initié et amende des personnes morales. Le quintuple figure dans k25 ; le délit d'initié n'a pas de carte.
  - **Ce qui a changé récemment#2** (tribunaux des activités économiques), **#4** (réforme des nullités du droit des sociétés, à distinguer des nullités de la période suspecte) et **#5** (loi n° 2026-403 du 26 mai 2026, suppression de peines d'emprisonnement aux articles L. 242-10 et L. 247-1).
  - **Points de vigilance#3** (renumérotation des articles sur le commissaire aux comptes) : son contenu est repris par k34, fondée sur Ce qui a changé récemment#3. **Points de vigilance#4** (deux programmes) : rien à mémoriser sous forme de carte.
- **Contenus couverts en partie :**
  - les alertes de l'associé non gérant de SARL, des actionnaires de SA et du comité social et économique (Règles essentielles#1) ;
  - l'ouverture du redressement sur assignation d'un créancier ou requête du ministère public et le report de la date de cessation des paiements (Règles essentielles#4) ;
  - les conditions de la liquidation judiciaire simplifiée et les trois cas de clôture (Règles essentielles#6).

  En ajouter une carte imposerait une suppression : le jeu est au plafond de 35, et aucune carte n'est fausse, sans intérêt ni en doublon.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | k01 | La réponse commençait par « L'impossibilité » et perdait le genre de la définition (« situation du débiteur »). | Définition reprise mot pour mot de L. 631-1, puis la réserve sur les réserves de crédit et les moratoires. |
| 1 | k07 | L'envoi en copie au président du tribunal de l'écrit invitant à faire délibérer le conseil (Règles essentielles#0) manquait. | Réponse resserrée à 70 mots avec les quatre étapes de l'alerte du commissaire aux comptes dans la SA. |
| 1 | k08 | « Quel pouvoir le président du tribunal détient-il… » admettait d'autres réponses justes (mandat ad hoc, conciliation). | Question centrée sur ce qu'il peut faire à l'égard des dirigeants ; réponse : il peut les convoquer. |
| 1 | k13 | La question offrait un choix entre deux procédures et donnait ainsi la réponse. | Question en « pourquoi » ; réponse fondée sur les conditions d'ouverture de chaque procédure et sur l'obligation de demander un redressement ou une liquidation sous quarante-cinq jours. |
| 1 | k16 | « Actions tendant au paiement d'une somme d'argent » simplifiait le texte. | Formulation de Règles essentielles#7 rétablie : « tendant à la condamnation du débiteur au paiement d'une somme d'argent ». |
| 1 | k29 | La précision « pour chaque exercice » manquait dans la définition des comptes infidèles. | Précision réintroduite. |
| 2 | k08 | « Dont la continuité d'exploitation est compromise » durcissait la condition de la fiche. | Question : société « dont les difficultés sont de nature à compromettre la continuité de l'exploitation ». Réponse inchangée. |
| 2 | k13 | La seconde phrase était approximative sur la condition (absence de demande de conciliation) et sur le point de départ du délai. | « S'il n'a pas demandé de conciliation, il doit demander un redressement ou une liquidation judiciaire dans les quarante-cinq jours qui suivent la cessation des paiements… ». |
| 2 | k25 | La restriction propre aux collectivités territoriales était trop elliptique. | Vocabulaire exact rétabli : infractions commises dans l'exercice d'activités susceptibles de faire l'objet de conventions de délégation de service public. |
| 2 | k27 | « Puni des mêmes peines que l'abus de biens sociaux » était inexact face à l'abus de biens sociaux aggravé ; le point de vigilance sur la peine de l'abus de confiance n'apparaissait pas. | « Comme abus de confiance, infraction punie, comme l'abus de biens sociaux, de cinq ans d'emprisonnement et de 375 000 € d'amende », puis les sociétés visées par les articles du Code de commerce. |
| 2 | k07 | Correction reprise d'une passe interrompue : l'ancienne question ne nommait pas le fait déclencheur et la fin de la réponse était vague. | Vérifiée et gardée : la question nomme les faits de nature à compromettre la continuité de l'exploitation ; la réponse finit par l'information du président du tribunal si les décisions prises n'assurent pas la continuité. |
| 2 | k14 | Correction reprise d'une passe interrompue : l'ancienne réponse ne disait pas que les actes annulables doivent être accomplis à compter de la date de cessation des paiements. | Vérifiée et gardée : « Les autres paiements de dettes échues et les actes à titre onéreux accomplis à compter de cette date peuvent être annulés… ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k13 | « La sauvegarde est réservée au débiteur qui n'est pas en cessation des paiements » n'est vrai que de la sauvegarde de droit commun. La cessation des paiements ne fait pas obstacle à l'ouverture d'une sauvegarde accélérée si elle ne précédait pas de plus de quarante-cinq jours la demande de conciliation. Un débiteur qui demande une conciliation peut donc ensuite obtenir une sauvegarde accélérée. | Question et réponse visent la « sauvegarde de droit commun ». Seconde phrase resserrée (« Sans demande de conciliation, il doit demander… dans les quarante-cinq jours suivant la cessation des paiements »), même sens, 68 mots. | C. com., art. L. 620-1, L. 611-4 et L. 628-1 ; recherche n° 1 (Points de vigilance#2, Règles essentielles#4) |
| k15 | « Les sûretés (hypothèque, nantissement, gage) » reprend l'ancienne énumération de l'article L. 632-1, I, 6°. Le texte en vigueur vise les sûretés réelles conventionnelles (et les droits de rétention conventionnels) constituées pour dettes antérieurement contractées. | « les sûretés réelles conventionnelles (hypothèque, nantissement, gage) constituées pour des dettes antérieurement contractées ». Le « notamment » initial est gardé ; le reste est inchangé. | C. com., art. L. 632-1, I, 6° ; recherche n° 2 (Règles essentielles#5) |
| k18 | « En procédure collective » englobait la liquidation judiciaire, qui ne comporte pas de plan ni de vote de classes, et la sauvegarde accélérée, qui suppose un projet de plan soutenu par les parties affectées et obéit à un régime propre. La réponse (au-delà de seuils ou à la demande du débiteur) ne vaut pas pour toutes. | Question délimitée : « Dans une sauvegarde de droit commun ou un redressement judiciaire, dans quels cas les parties affectées sont-elles réparties en classes… ? ». Réponse inchangée. | C. com., art. L. 626-29 et s., L. 631-19 et L. 628-1 (Règles essentielles#7, Ce qui a changé récemment#0) |
| k24 | « Sur son seul patrimoine professionnel », sans réserve, est trop absolu. L'article L. 621-2 permet de réunir à la procédure les autres patrimoines du débiteur en cas de confusion, de manquement grave aux règles de séparation ou de fraude. La seconde phrase répétait en outre la première. | « <b>En principe</b>, sur son seul patrimoine professionnel. Cette règle, issue de la loi en faveur de l'activité professionnelle indépendante, s'applique depuis le 15 mai 2022 (titre VIII bis du livre VI du Code de commerce). » Aucune règle nouvelle au verso. | Loi n° 2022-172 du 14 février 2022 ; C. com., art. L. 621-2 et L. 526-22 ; recherche n° 3 (Ce qui a changé récemment#1) |
| k27 | « Ne visent que les dirigeants de SARL, de SA, de SCA et de SAS » était plus fort que la fiche (qui dit « visent ») et inexact à la lettre : les dispositions pénales de la SA s'appliquent aussi à la société européenne. | « Les articles du Code de commerce qui répriment l'abus de biens sociaux visent les dirigeants, de droit ou de fait, de SARL, de SA, de SCA et de SAS, non ceux de SNC ou de société civile. » Première phrase inchangée. | C. com., art. L. 241-3, L. 242-6, L. 243-1, L. 244-1 et L. 244-5 (Points de vigilance#0, Règles essentielles#10) |
| k28 | « Qu'est-ce qu'un dividende fictif ? » appelait pour toute réponse un renvoi à l'article L. 232-12. Un correcteur du DCG attendrait la substance (dividende sans bénéfice distribuable…), que la fiche ne donne pas : la réponse attendue n'était pas celle de l'examen. | Question : « En quoi consiste le délit de répartition de dividendes fictifs reproché aux dirigeants d'une SARL ou d'une SA ? ». Réponse : la répartition entre les associés, par les dirigeants, de dividendes fictifs en l'absence d'inventaire ou au moyen d'inventaires frauduleux ; est fictif tout dividende distribué en violation de L. 232-12. Type `def` conservé. | C. com., art. L. 232-12, L. 241-3, 2° et L. 242-6, 1° (Règles essentielles#11) |
| k17 (reprise) | La question (« que risque le créancier antérieur qui ne déclare pas sa créance au mandataire judiciaire », posée « dans une procédure collective ») supposait que la déclaration se fait toujours entre les mains du mandataire judiciaire. En liquidation judiciaire, les créanciers déclarent leurs créances au liquidateur. | Mention « au mandataire judiciaire » retirée de la question : « Dans une procédure collective, que risque le créancier antérieur qui ne déclare pas sa créance dans le délai légal ? ». La réponse (pas d'admission aux répartitions et aux dividendes sauf relevé de forclusion, délai courant de la publication au BODACC) vaut pour les trois procédures et ne change pas. | C. com., art. L. 622-24, L. 622-26 et L. 641-3 (Règles essentielles#7) |
| k20 (reprise) | « Ses droits et actions sont exercés par le liquidateur » était trop large. Le dessaisissement ne porte que sur les droits et actions du débiteur concernant son patrimoine ; le débiteur garde l'exercice de ses droits propres (droits attachés à sa personne, recours contre le jugement de liquidation). | « Ses droits et actions concernant son patrimoine sont exercés par le liquidateur, qui procède aux opérations de liquidation et à la vérification des créances. » Le reste de la carte est inchangé. | C. com., art. L. 641-9, I (Règles essentielles#6) |

Les 6 premières lignes viennent de la première passe ; la reprise les a relues et gardées. Les lignes marquées « reprise » sont les corrections de la reprise.

Les 27 autres cartes ont été contrôlées sans changement : k01 à k12, k14, k16, k19, k21 à k23, k25, k26 et k29 à k35. En particulier :
- **k07** (alerte du commissaire aux comptes dans la SA) suit l'article L. 234-1 dans ses quatre phases.
- **k09** reprend exactement les deux voies de l'article L. 611-8 (constatation par le président, homologation par le tribunal et ses trois conditions).
- **k10** (privilège de « new money ») est juste dans les termes de la fiche. Il ne mentionne pas l'exclusion des apports consentis par les associés lors d'une augmentation de capital, que la fiche ne donne pas ; la question, qui porte sur les « créanciers », ne l'appelle pas.
- **k11** reprend les conditions de l'article L. 628-1 telles que la fiche les donne : conciliation en cours, projet de plan susceptible d'un soutien suffisamment large, comptes certifiés ou établis par un expert-comptable.
- **k14** et **k15** ne font pas doublon : la première porte sur les paiements, la seconde sur les autres actes nuls de droit. De même, **k02** et **k13** se recoupent sur la condition d'ouverture de la sauvegarde, mais k13 l'oppose à celle de la conciliation et ajoute l'obligation de demander un redressement ou une liquidation.
- **k19** (juge-commissaire et mandataire judiciaire) : le mandataire judiciaire n'est désigné qu'en sauvegarde et en redressement, le liquidateur tenant ce rôle en liquidation. La question porte sur le rôle du mandataire lui-même et n'appelle qu'une réponse : elle est gardée.
- **k21** : la liste des exceptions à l'absence de reprise des poursuites est introduite par « notamment » ; « créance née d'une infraction dont le débiteur a été reconnu coupable » rend fidèlement l'exception pénale du I de l'article L. 643-11.
- **k33** (révélation des faits délictueux, `comp`) et **k34** (délit d'entrave, `def`) sont à jour de l'ordonnance n° 2023-1142 (article L. 821-6, 3°, pour l'entrave).
- **k35** reprend exactement l'article 9-1 du Code de procédure pénale (infraction occulte, infraction dissimulée, plafond de douze ans pour les délits).

## Recherches faites

3 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr, toutes faites lors de la première passe de la relecture d'exactitude. La reprise n'en a fait aucune.

1. Requête « article L628-1 code de commerce sauvegarde accélérée cessation des paiements ne fait pas obstacle quarante-cinq jours conciliation ».
   - **Confirmé.** La cessation des paiements ne fait pas obstacle à l'ouverture d'une sauvegarde accélérée si elle ne précédait pas depuis plus de quarante-cinq jours la demande d'ouverture de la conciliation (art. L. 628-1). Le ministère public peut demander qu'il soit mis fin à la procédure si ce délai était dépassé (art. L. 628-5).
   - Effet : k13 et k18 délimitées à la sauvegarde de droit commun ; Points de vigilance#2 à reprendre.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000044052816 ; https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000005634379/LEGISCTA000022954557/
2. Requête « article L632-1 code de commerce nullités période suspecte "toute sûreté réelle conventionnelle" dettes antérieurement contractées ».
   - **Confirmé.** Le 6° du I de l'article L. 632-1 (rédaction en vigueur depuis le 15 mai 2022) vise toute sûreté réelle conventionnelle ou tout droit de rétention conventionnel constitués sur les biens ou droits du débiteur pour dettes antérieurement contractées, à moins qu'ils ne remplacent une sûreté antérieure d'une nature et d'une assiette au moins équivalentes. Une exception vise aussi la cession de créances professionnelles faite en exécution d'un contrat-cadre antérieur.
   - Effet : k15 alignée sur ce vocabulaire ; Règles essentielles#5 à reprendre.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045178091 ; https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000005634379/LEGISCTA000006146112/
3. Requête « article L621-2 code de commerce entrepreneur individuel réunion des patrimoines manquement grave L526-22 fraude procédure étendue ».
   - **Confirmé.** L'article L. 621-2 permet d'étendre la procédure en cas de confusion des patrimoines ou de fictivité de la personne morale, et de réunir à la procédure les autres patrimoines du débiteur en cas de confusion, de manquement grave aux règles de séparation ou de fraude. L'article L. 526-22 distingue patrimoine professionnel et patrimoine personnel de l'entrepreneur individuel.
   - **Non confirmé dans le détail.** La rédaction consolidée exacte du renvoi (L. 526-22 ou ancien L. 526-13) n'a pas pu être lue dans les résultats.
   - Effet : k24 dit « en principe » ; Ce qui a changé récemment#1 à reprendre.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045178127 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045168684/2022-05-15 ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000045167536

Aucune recherche n'a été faite pour k17, k20, k27 et k28. Ces corrections reposent sur la lettre d'articles stables (C. com., art. L. 641-3 et L. 641-9 ; art. L. 244-5 ; art. L. 232-12 et L. 241-3) et se bornent à retirer une restriction ou une prémisse trop large, ou à recentrer la question sur ce que la fiche dit.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Points de vigilance#2** (cessation des paiements récente). « Pas une sauvegarde, réservée au débiteur qui n'est pas en cessation des paiements » vaut pour la sauvegarde de droit commun (art. L. 620-1). La sauvegarde accélérée peut être ouverte au débiteur en cessation des paiements si cette situation ne précédait pas de plus de quarante-cinq jours la demande de conciliation (art. L. 628-1 ; art. L. 628-5 pour le contrôle du ministère public). L'item devrait le préciser ; Règles essentielles#3 pourrait le mentionner à propos de la sauvegarde accélérée.
2. **Règles essentielles#5** (nullités de la période suspecte). « Les sûretés (hypothèque, nantissement, gage) » reprend l'ancienne rédaction du 6° du I de l'article L. 632-1. La rédaction en vigueur vise les sûretés réelles conventionnelles et les droits de rétention conventionnels constitués pour dettes antérieurement contractées. Elle excepte la sûreté qui remplace une sûreté antérieure d'une nature et d'une assiette au moins équivalentes, ainsi que la cession de créances professionnelles faite en exécution d'un contrat-cadre antérieur à la cessation des paiements.
3. **Ce qui a changé récemment#1** (entrepreneur individuel). « Ne portent que sur son patrimoine professionnel » énonce le principe. L'article L. 621-2 permet de réunir à la procédure les autres patrimoines du débiteur en cas de confusion, de manquement grave aux règles de séparation ou de fraude. Il faut ajouter « en principe » et, si possible, cette exception après lecture de la rédaction consolidée de l'article.
4. **Règles essentielles#6** (liquidation judiciaire). « Ses droits et actions étant exercés par le liquidateur » est trop large : l'article L. 641-9, I, vise les droits et actions du débiteur « concernant son patrimoine », le débiteur gardant l'exercice de ses droits propres. Ajouter « concernant son patrimoine ».
5. **Règles essentielles#7** (situation des créanciers antérieurs), précision facultative. « Les créanciers déclarent leurs créances au mandataire judiciaire » vaut en sauvegarde et en redressement ; en liquidation judiciaire, ils les déclarent au liquidateur (art. L. 641-3).

## Classement des exercices

Le chapitre compte 30 exercices. Le classement automatique porte sur les 26 QCM, QCM multiples et classements : **24 de nature `notion`**, **2 de nature `calcul`**, **aucun de nature `chiffre`**. Les 4 exercices à saisie numérique (`calc` : délai de déclaration de cessation des paiements, durée maximale de la période d'observation, retard d'une déclaration de créance, amende maximale d'une personne morale) sont des calculs par nature.

Un désaccord a été arbitré :
- **Exercice #23** (détournements dissimulés en 2016, découverts en 2025 : l'action publique est-elle prescrite ?) : `notion` ou `calcul` → **`calcul`**. Il faut décompter le délai de prescription à partir de dates pour répondre.

L'autre QCM de nature `calcul` est l'exercice #12 (date limite du report de la date de cessation des paiements, à décompter depuis le jugement d'ouverture). Seuls les 24 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes.
