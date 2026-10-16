# Cartes de notions : ue3-03 (Exécution du contrat : durée du travail, rémunération, pouvoir de l'employeur, suspension)

15 octobre 2026. Fichier : `data/ue3/ue3-03.cartes.json`. Fiche de référence : `data/ue3/ue3-03.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`) dont elle reprend `src` et `url`. Une passe antérieure (commit 461075e) a supprimé k21 et k31 et ajouté k36 et k37. Les identifiants supprimés ne sont pas réutilisés.
2. **Relecture de fidélité, en deux passages.** La fiche est le seul juge de cette relecture, faite sans recherche web. Chaque passage a contrôlé les 35 cartes.
   - **Premier passage** : 3 cartes corrigées (k17, k20, k27), aucune suppression, aucun ajout.
   - **Reprise** : 1 carte corrigée (k03), aucune suppression, aucun ajout.
3. **Relecture d'exactitude, en deux passages.** Chaque passage a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code du travail, Code civil et jurisprudence de la chambre sociale. Il a vérifié trois points :
   - chaque question n'appelle qu'une seule réponse, celle qu'attendrait un correcteur du DCG ;
   - une règle qui connaît des exceptions est délimitée ;
   - le jeu ne contient ni doublon ni carte triviale.

   **Premier passage** : 9 cartes corrigées (k04, k10, k14, k22, k25, k26, k27, k35, k36), aucune suppression, aucun ajout.
   **Reprise** (ce passage) : relecture indépendante du fichier issu de la reprise de fidélité. 2 cartes corrigées (k05, k35), aucune suppression, aucun ajout.
4. **Recherches.**
   - Premier passage : 3 recherches WebSearch sur les 3 autorisées (legifrance.gouv.fr, service-public.fr). La première portait sur le décret n° 2026-503 du 12 juin 2026 (visite de reprise), les deux autres sur le congé supplémentaire de naissance.
   - Reprise : 1 recherche sur les 3 autorisées (legifrance.gouv.fr, service-public.fr). Elle porte sur le seul point resté « à confirmer » : l'application dans le temps du décret n° 2026-503.

`node validate.js data/ue3/ue3-03.cartes.json` : ✓ (35 cartes, 6 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 6 de définition (`def` : k01, k07, k14, k15, k24, k30) et 29 de compréhension (`comp`). Les identifiants k21 et k31 restent libres.
- **Définitions** : les 5 items ont chacun une carte (k01, k07, k15, k24, k30).
- **Règles essentielles** : 18 items sur 19 ont une carte. Celui qui n'en a pas :
  - **#18** (sanctions administratives en matière de durée du travail et de salaire). La règle est déjà travaillée dans les cartes k26 et k27 du chapitre ue3-01.

  Points d'items couverts seulement en partie :
  - **#14** : la reprise du paiement du salaire un mois après l'examen de reprise (L. 1226-4) n'a pas de carte.
  - **#16** et **#17** : les durées du congé de maternité et du congé de paternité et d'accueil de l'enfant n'ont pas de carte. Les cartes k28 et k29 portent sur la protection contre la rupture.
- **Ce qui a changé récemment** : 5 items sur 6 ont une carte. **#5** (partage de la valeur : prime de partage de la valeur et dispositif expérimental de la loi n° 2023-1107) n'en a pas.
- **Points de vigilance** : les 4 items ont chacun une carte (k32, k33, k03, k34).
- **Chiffres et seuils** :
  - **#2** a une carte (k32).
  - **#0**, **#1** (SMIC 2026 et 2025) et **#4** (indemnisation du congé supplémentaire de naissance en 2026) n'en ont pas : ce sont des chiffres millésimés, exclus par le contrat.
  - **#3** (prescription de deux ans) n'est pas cité dans `base`, mais son contenu est repris dans les réponses de k33 et k34.
- Le jeu est au plafond de 35 cartes. Pour couvrir Règles essentielles#18, Ce qui a changé récemment#5 ou les durées des congés de maternité et de paternité, il faudrait supprimer une carte. Aucune n'est un doublon ou une carte sans intérêt :
  - k02 (taux légaux de majoration à défaut d'accord) et k03 (primauté de l'accord d'entreprise sur l'accord de branche) posent deux questions distinctes ;
  - k08 (acquisition des congés pendant un arrêt) et k09 (report des congés non pris) aussi ;
  - les quatre cartes sur la procédure disciplinaire (k16, k17, k18, k37) portent chacune sur une règle distincte.

## Corrections de la première relecture (fidélité à la fiche)

### Reprise

Le résultat transmis par la reprise est tronqué dans sa partie « validation ». La correction qu'il détaille est reprise ci-dessous.

| cible | problème | correction |
|---|---|---|
| k03 | La question offrait un choix entre deux options (« quel accord prévaut entre l'accord d'entreprise et l'accord de branche ? »). Elle contenait la réponse parmi deux propositions et se devinait à pile ou face. | Question reformulée : « Pour fixer le taux de majoration des heures supplémentaires, comment s'articulent l'accord d'entreprise et l'accord de branche ? ». La réponse est inchangée et reste fidèle à Points de vigilance#2 : l'accord d'entreprise prévaut, même moins favorable, dans la limite du plancher légal de 10 %, parce que la matière ne relève pas des domaines réservés à la branche. |

La reprise a aussi relevé quatre items de la fiche à reprendre : Règles essentielles#14, Règles essentielles#15 avec Ce qui a changé récemment#2, Ce qui a changé récemment#0 et Règles essentielles#6. Ils sont repris dans la dernière section.

### Premier passage

| cible | problème | correction |
|---|---|---|
| k17 | La question parlait d'« un fait fautif » sans dire de qui : elle n'était pas tout à fait autosuffisante. | Question : « Au-delà de quel délai un fait fautif du salarié ne peut-il plus, à lui seul, donner lieu à des poursuites disciplinaires ? ». La réponse est inchangée. |
| k20 | La réponse disait seulement « Il est réputé avoir accepté la modification ». Elle omettait la condition posée par la fiche (Règles essentielles#11) : « à défaut de réponse dans ce délai ». | La réponse commence par « À défaut de réponse dans le délai imparti, il est réputé avoir accepté la modification. » Elle précise ensuite le délai : un mois à compter de la réception de la proposition, faite par lettre recommandée avec avis de réception (quinze jours en redressement ou liquidation judiciaire). |
| k27 | La réponse faisait conclure la visite de préreprise elle-même, et non le médecin du travail. Elle s'écartait ainsi de Règles essentielles#15 et de Ce qui a changé récemment#2. | La conclusion est rendue au médecin du travail (« le médecin du travail a conclu qu'aucun aménagement n'était nécessaire »). La liste des absences est resserrée pour rester sous 70 mots. La relecture d'exactitude a ensuite revu cette carte (voir ci-dessous). |

## Corrections de la relecture d'exactitude

### Reprise : corrections de ce passage

| cible | problème | correction | source |
|---|---|---|---|
| k05 | La question présentait le repos quotidien de 11 heures et le repos dominical comme toujours garantis. L'article L. 3131-1 réserve pourtant les cas des articles L. 3131-2 et L. 3131-3 (dérogations par accord collectif ou, à défaut, en cas de surcroît d'activité) et l'urgence. Le repos dominical connaît aussi de nombreuses dérogations. La carte k04, sur les durées maximales, était déjà délimitée par « En principe » : les deux cartes n'étaient pas cohérentes. | Question délimitée : « En principe, quels temps de repos et de pause minimaux le Code du travail garantit-il au salarié ? ». La réponse est inchangée : la fiche ne traite pas des dérogations. | C. trav., art. L. 3131-1 à L. 3131-3 ; L. 3132-3 et L. 3132-12 |
| k35 | Deux problèmes. **1.** La question (« Comment le salarié peut-il prendre le congé… ? ») était trop ouverte : « en prévenant l'employeur » ou « par lettre recommandée » auraient aussi été des réponses justes. **2.** La limite de 9 mois était présentée comme absolue. Or la fiche elle-même prévoit une règle transitoire : pour un enfant né entre le 1er janvier et le 30 juin 2026, le délai court à compter du 1er juillet 2026. Ce délai est aussi prolongé quand le congé de maternité, de paternité ou d'adoption est allongé. Le « en principe » ne visait que le délai de prévenance. | Question resserrée sur ce que la réponse donne : « Quelle durée, quel fractionnement et quels délais s'appliquent au congé supplémentaire de naissance du salarié, en vigueur depuis le 1er juillet 2026 ? ». La seconde phrase de la réponse est réécrite pour que « En principe » porte sur les deux délais : « En principe, le congé débute au plus tard 9 mois après la naissance ou l'arrivée de l'enfant, et le salarié prévient l'employeur au moins un mois avant son début. » | Ce qui a changé récemment#0 (règle transitoire) ; C. trav., art. L. 1225-46-2 et s., D. 1225-11-4 ; recherches n° 2 et 3 du premier passage |

Les 33 autres cartes ont été contrôlées sans changement dans ce passage, dont les cartes revues aux passages précédents :
- **k03** (nouvelle question) : exacte (L. 2253-3 et L. 3121-33), sans réponse dans la question et sans doublon avec k02.
- **k27** : la mention « Pour les arrêts de travail délivrés depuis le 15 juin 2026 » est confirmée par la recherche de ce passage (voir ci-dessous).

Aucune carte ne contient de calcul ni de chiffre millésimé. Les dates de réforme de k08, k09, k22, k27 et k35 situent le changement ; ce ne sont pas des chiffres annuels. Les chiffres stables de k02, k04, k05, k07 et k17 font partie de la règle interrogée.

### Premier passage

| cible | problème | correction | source |
|---|---|---|---|
| k04 | La question demandait « les » durées maximales fixées par le Code du travail. La réponse ne donne que les maxima de principe et leurs dérogations par accord. Le Code admet aussi des dérogations administratives : inspecteur du travail ou urgence pour la durée quotidienne, jusqu'à 60 heures par semaine en cas de circonstances exceptionnelles. | Question délimitée : « En principe, quelles durées maximales de travail quotidienne et hebdomadaire le Code du travail impose-t-il ? ». La réponse est inchangée : la fiche ne traite pas des dérogations administratives. | C. trav., art. L. 3121-18 à L. 3121-21 |
| k10 | La question (« Quelles règles encadrent la période et la durée de prise des congés payés ? ») était ambiguë. « Durée » pouvait appeler la durée totale du congé (30 jours ouvrables), alors que la réponse porte sur la période de prise et sur le fractionnement. | Question : « Que prévoit le Code du travail sur la période de prise des congés payés et sur leur fractionnement ? ». La réponse est inchangée. | C. trav., art. L. 3141-13, L. 3141-17, L. 3141-18 et L. 3141-23 |
| k14 | La réponse disait que le règlement intérieur « entre en vigueur un mois après les formalités de publicité ». Or il entre en vigueur à la date qu'il indique, qui doit être postérieure d'un mois au moins à ces formalités. | La réponse dit qu'il « ne peut entrer en vigueur qu'un mois au moins après les formalités de publicité » (66 mots). | C. trav., art. L. 1321-4 (loi n° 2026-403, art. 5) ; citation de Ce qui a changé récemment#3 |
| k22 | Selon l'arrêt cité par la fiche, le licenciement est sans cause réelle et sérieuse quand l'accord comporte des dispositions étrangères à ses objets **et modifiant le contrat**. Cette seconde condition manquait dans la question (alignement sur la carte k17 du chapitre ue3-01). | Question : « Que vaut le licenciement pour refus de clauses d'un accord de performance collective modifiant le contrat sans porter sur la durée du travail, la rémunération ou la mobilité interne ? ». La réponse est inchangée. | Cass. soc., 28 mai 2026, n° 24-19.461 et s. (citation de Ce qui a changé récemment#1) ; C. trav., art. L. 2254-2 |
| k25 | L'avis du CSE était présenté comme toujours requis. Les articles L. 1226-2 et L. 1226-10 le prévoient seulement « lorsqu'il existe » (pas de CSE en dessous de onze salariés). | « après avis du CSE lorsqu'il existe » (65 mots). | C. trav., art. L. 1226-2 et L. 1226-10 |
| k26 | La réponse ne vaut qu'en principe. Selon l'article L. 1226-14, alinéa 2, ces indemnités ne sont pas dues si l'employeur établit que le refus du reclassement par le salarié est abusif. La fiche ne mentionne pas cette exception. | Question délimitée : « En principe, quelles indemnités ouvre le licenciement d'un salarié pour inaptitude d'origine professionnelle ? ». La réponse est inchangée. | C. trav., art. L. 1226-14 |
| k27 | La dispense de visite de reprise était datée « depuis le 15 juin 2026 ». Or, selon la recherche n° 1, le décret n° 2026-503 ne s'applique qu'aux arrêts de travail délivrés à compter du lendemain de sa publication (JO du 14 juin 2026). La carte était donc trop large pour une reprise après un arrêt antérieur. | « Pour les arrêts de travail délivrés depuis le 15 juin 2026, elle n'est pas requise si… ». Deux mots retirés pour rester à 70 mots : « Congé de maternité, maladie professionnelle, … » ; « le médecin a conclu » (le médecin du travail est nommé dans la question). | Décret n° 2026-503 du 12 juin 2026 ; C. trav., art. R. 4624-31 ; recherche n° 1 |
| k35 | Le délai de prévenance réduit à quinze jours était présenté comme acquis dès que le congé suit immédiatement le congé de paternité ou d'adoption. L'article D. 1225-11-4 exige en outre que le congé débute dans le mois suivant la naissance ou l'arrivée de l'enfant. Le délai d'un mois est aussi un minimum. | La phrase devient « Le salarié prévient en principe l'employeur au moins un mois avant le début du congé. » La condition supplémentaire n'est pas dans la fiche, si bien que l'exception est seulement signalée par « en principe » (55 mots). La reprise a de nouveau revu cette carte (voir ci-dessus). | C. trav., art. D. 1225-11-4 (décret n° 2026-419 du 30 mai 2026) ; recherches n° 2 et 3 |
| k36 | Selon l'article L. 3252-2, le plafonnement par le barème joue « sous réserve des dispositions relatives aux pensions alimentaires » : le prélèvement direct au titre d'une pension alimentaire peut porter sur l'intégralité de la rémunération (L. 3252-5). La réponse ne valait donc qu'en principe. | Question délimitée : « En principe, dans quelles limites les sommes dues au salarié à titre de rémunération peuvent-elles être saisies ou cédées ? ». La réponse est inchangée : la somme égale au RSA forfaitaire est laissée au salarié « dans tous les cas ». | C. trav., art. L. 3252-2 et L. 3252-5 |

## Recherches faites

### Reprise (ce passage)

1 recherche sur les 3 autorisées.

1. WebSearch, `allowed_domains` : legifrance.gouv.fr et service-public.fr. Requête : « décret n° 2026-503 du 12 juin 2026 visite de reprise préreprise arrêts de travail délivrés à compter entrée en vigueur ».
   - **Confirmé.** Le décret n° 2026-503 du 12 juin 2026, « relatif aux modalités des visites de préreprise et de reprise », a été publié au JORF n° 0138 du 14 juin 2026. Il entre en vigueur le lendemain de sa publication et **s'applique aux arrêts de travail délivrés à compter du 15 juin 2026**. La carte k27 est exacte sur ce point. C'est le second résultat concordant, après la recherche n° 1 du premier passage.
   - **Confirmé.** L'article R. 4624-31 dispense de visite de reprise lorsque le salarié a bénéficié d'une visite de préreprise dans les trente jours précédant la reprise effective et que le médecin du travail a conclu qu'aucune mesure d'aménagement, d'adaptation ou de transformation du poste, ni aucun aménagement du temps de travail, n'était nécessaire. La dispense ne joue pas si le médecin du travail, l'employeur ou le salarié demande la visite.
   - **Relevé, sans effet sur les cartes.** L'article R. 4624-30 prévoit désormais que l'employeur est informé de l'organisation de la visite de préreprise, même sans recommandation du médecin du travail, sauf opposition du salarié. Le décret modifie aussi les articles R. 717-17 et R. 717-17-1 du Code rural et de la pêche maritime (régime agricole).
   - **Limite.** Le texte intégral du décret n'a pas été lu : seuls la notice Légifrance et les résultats de recherche l'ont été.
   - Sources : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054248175 ; https://www.legifrance.gouv.fr/jorf/jo/2026/06/14/0138 ; https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000045369250/ ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045676894

La correction de k05 s'appuie sur le texte de l'article L. 3131-1 (« sauf dans les cas prévus aux articles L. 3131-2 et L. 3131-3 ou en cas d'urgence »). Celle de k35 s'appuie sur la fiche elle-même (règle transitoire) et sur les recherches n° 2 et 3 du premier passage. Aucune autre recherche n'était nécessaire.

### Premier passage

3 recherches sur les 3 autorisées.

1. WebSearch, `allowed_domains` : legifrance.gouv.fr. Requête : « décret n° 2026-503 du 12 juin 2026 visite de reprise visite de préreprise R. 4624-31 aucun aménagement ».
   - **Confirmé.** Le décret existe et a été publié au JO du 14 juin 2026. Il modifie R. 4624-30 et R. 4624-31. La visite de reprise n'est pas requise après une visite de préreprise dans les trente jours précédant la reprise, lorsque le médecin du travail a conclu qu'aucune mesure d'aménagement, d'adaptation ou de transformation du poste, ni aucun aménagement du temps de travail, n'était nécessaire. Elle redevient requise à la demande du médecin, de l'employeur ou du travailleur. R. 4624-31 est en vigueur dans cette version depuis le 15 juin 2026.
   - **Précisé.** Le texte s'applique aux arrêts de travail délivrés à compter du 15 juin 2026 (carte k27).
   - Sources : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054248175 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045676892 ; https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000045369250/
2. WebSearch, `allowed_domains` : service-public.fr et legifrance.gouv.fr. Requête : « congé supplémentaire de naissance salarié 1er juillet 2026 durée un ou deux mois fractionnement délai 9 mois prévenir employeur ».
   - **Confirmé** (carte k35) : un ou deux mois au choix, deux périodes d'un mois en cas de fractionnement, début dans les neuf mois suivant la naissance ou l'arrivée de l'enfant, prévenance d'au moins un mois.
   - **Signalé.** Les règles de prévenance (D. 1225-11-4) viennent du décret n° 2026-419 du 30 mai 2026, que la fiche ne cite pas. Le délai de neuf mois est prolongé lorsque la durée du congé de maternité, de paternité ou d'adoption est elle-même augmentée.
   - Sources : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000053271681/ ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054153815
3. WebSearch, `allowed_domains` : legifrance.gouv.fr. Requête : « article D1225-11-4 code du travail congé supplémentaire de naissance délai quinze jours suit immédiatement congé de paternité et d'accueil de l'enfant ».
   - **Confirmé.** Le délai de prévenance est ramené à quinze jours si deux conditions sont réunies : le congé suit immédiatement le congé de paternité et d'accueil de l'enfant ou le congé d'adoption, et il débute dans le mois suivant la naissance ou l'arrivée de l'enfant.
   - **Confirmé aussi.** L'information se fait par lettre recommandée avec avis de réception ou par remise contre récépissé (D. 1225-11-5). Ces dispositions sont en vigueur depuis le 15 juin 2026.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054159979 ; https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000054159502/

Vérifications faites sans recherche, avec des données du dépôt :
- `data/FAITS-CONFIRMES.md` : loi n° 2026-403, art. 5 (L. 1321-4 ne vise plus les formalités de dépôt, depuis le 28 mai 2026). La carte k14 est exacte sur ce point.
- `data/ue3/rapports/ue3-03.md` et `ue3-01-cartes.md` : arrêt Cass. soc., 28 mai 2026, n° 24-19.461 et s., avec sa citation confirmée mot pour mot. La carte k22 est exacte.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#15 et Ce qui a changé récemment#2** (décret n° 2026-503), relevés par les deux relectures.
   - Le décret s'applique aux arrêts de travail délivrés à compter du 15 juin 2026. La mention « Depuis le 15 juin 2026 » est trop large et devrait devenir « Pour les arrêts de travail délivrés à compter du 15 juin 2026 ». Deux recherches concordent sur ce point ; le texte intégral n'a pas été lu.
   - La conclusion du médecin porte aussi sur l'absence d'aménagement du temps de travail.
2. **Ce qui a changé récemment#0** (congé supplémentaire de naissance), relevé par les deux relectures.
   - Le délai de quinze jours suppose aussi que le congé débute dans le mois suivant la naissance ou l'arrivée de l'enfant.
   - Le délai d'un mois est un minimum (« au moins un mois avant le début du congé »).
   - Le délai de neuf mois est prolongé lorsque le congé de maternité, de paternité ou d'adoption est allongé.
   - Le `src` devrait citer l'article D. 1225-11-4 et le décret n° 2026-419 du 30 mai 2026 (les décrets n° 2026-425 et 2026-426 portent sur l'indemnisation).
3. **Règles essentielles#14** (inaptitude et reclassement), relevé par les deux relectures.
   - L'avis du CSE est requis « lorsqu'il existe ».
   - Le reclassement dans le groupe se limite aux entreprises situées sur le territoire national.
   - Les indemnités de l'article L. 1226-14 ne sont pas dues si l'employeur établit que le refus du reclassement par le salarié est abusif (al. 2).
4. **Règles essentielles#6** (saisie des rémunérations), relevé par les deux relectures.
   - Ajouter la réserve des pensions alimentaires (L. 3252-2 et L. 3252-5) : le prélèvement direct peut porter sur l'intégralité de la rémunération, sous réserve de la somme égale au RSA forfaitaire.
   - Ajouter que les seuils sont « affectés d'un correctif pour toute personne à charge ».
5. **Ce qui a changé récemment#3** (règlement intérieur). La formule « entre en vigueur un mois après les formalités de publicité » est à remplacer par : « à la date qu'il indique, postérieure d'un mois au moins aux formalités de publicité ».
6. **Règles essentielles#1** (complément, pas une erreur). Les durées maximales et les repos sont donnés sans leurs dérogations :
   - dérogation de l'inspecteur du travail et cas d'urgence pour la durée quotidienne (L. 3121-18) ;
   - jusqu'à 60 heures par semaine sur autorisation administrative en cas de circonstances exceptionnelles (L. 3121-21) ;
   - repos quotidien de 11 heures « sauf dans les cas prévus aux articles L. 3131-2 et L. 3131-3 ou en cas d'urgence » (L. 3131-1), et dérogations au repos dominical (L. 3132-12 et s.). Ce point est relevé par ce passage.
7. **Ce qui a changé récemment#1** (complément). Le `t` pourrait reprendre la condition « et modifiant son contrat de travail », qui ne figure que dans la citation.

## Classement des exercices

Le classement automatique porte sur les 22 exercices QCM, QCM multiples et classements du chapitre : 19 QCM, 2 QCM multiples et 1 classement. Les 6 exercices de calcul (`calc`) n'en font pas partie.

| nature | nombre |
|---|---|
| notion | 19 |
| calcul | 2 |
| chiffre | 1 |

Aucun désaccord entre les classements. Les trois exercices qui ne sont pas de nature notion sortent des révisions espacées :
- **#11** (chiffre) : SMIC horaire brut en 2025. La notion de SMIC reste révisée par la carte k07.
- **#15** (calcul) : date limite d'engagement des poursuites disciplinaires. La règle des deux mois reste révisée par la carte k17.
- **#21** (calcul) : salarié déclaré inapte, ni reclassé ni licencié après un mois. La règle de reprise du salaire (L. 1226-4, Règles essentielles#14) n'a pas de carte.

Les 19 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes.
