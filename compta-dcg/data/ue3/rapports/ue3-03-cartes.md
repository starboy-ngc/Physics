# Cartes de notions : ue3-03 (Exécution du contrat : durée du travail, rémunération, pouvoir de l'employeur, suspension)

15 octobre 2026. Fichier : `data/ue3/ue3-03.cartes.json`. Fiche de référence : `data/ue3/ue3-03.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`) et reprend leurs `src` et `url`. Une passe antérieure (commit 461075e) a supprimé k21 et k31 et ajouté k36 et k37. Leurs identifiants ne sont pas réutilisés.
2. **Relecture de fidélité.** Le premier relecteur a contrôlé les 35 cartes au regard de la fiche, seul juge pour cette passe, sans recherche web. Il en a corrigé 3 (k17, k20, k27), sans suppression ni ajout, et a fixé `maj` au 2026-10-16.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code du travail, Code civil et jurisprudence de la chambre sociale. Il a vérifié trois points :
   - chaque question n'appelle qu'une seule réponse ;
   - une règle qui connaît des exceptions est délimitée ;
   - le jeu ne contient ni doublon ni carte triviale.

   Bilan : 9 cartes corrigées, aucune suppression, aucun ajout.
4. **Recherches.** 3 recherches WebSearch sur les 3 autorisées (legifrance.gouv.fr, service-public.fr) :
   - le décret n° 2026-503 du 12 juin 2026 sur la visite de reprise, signalé comme « point non tranché » dans `rapports/ue3-03.md` ;
   - le congé supplémentaire de naissance (deux recherches).

   Le texte intégral du décret n° 2026-503 n'a pas pu être lu : la page Légifrance est inaccessible depuis cet environnement.

`node validate.js data/ue3/ue3-03.cartes.json` : ✓ (35 cartes, 6 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 6 de définition (`def`) et 29 de compréhension (`comp`). Les identifiants k21 et k31 restent libres.
- **Définitions** : les 5 items ont chacun une carte (k01, k07, k15, k24, k30).
- **Règles essentielles** : 18 items sur 19 ont une carte. Ceux qui n'en ont pas :
  - **#18** (sanctions administratives en matière de durée du travail et de salaire). La règle est déjà travaillée dans les cartes k26 et k27 du chapitre ue3-01.
  - Un point de **#14** n'a pas de carte : la reprise du paiement du salaire un mois après l'examen de reprise (L. 1226-4).
- **Ce qui a changé récemment** : 5 items sur 6 ont une carte. **#5** (partage de la valeur : prime de partage de la valeur et dispositif expérimental de la loi n° 2023-1107) n'en a pas.
- **Points de vigilance** : les 4 items ont chacun une carte (k32, k33, k03, k34).
- **Chiffres et seuils** :
  - **#2** a une carte (k32).
  - **#0**, **#1** (SMIC 2026 et 2025) et **#4** (indemnisation du congé supplémentaire de naissance en 2026) n'en ont pas : ce sont des chiffres millésimés, exclus par le contrat.
  - **#3** (prescription de deux ans) n'est pas cité dans `base`, mais son contenu est repris dans les réponses de k33 et k34.
- Le jeu est au plafond de 35 cartes. Pour couvrir Règles essentielles#18 ou Ce qui a changé récemment#5, il faudrait supprimer une carte. Aucune n'est un doublon ou une carte sans intérêt : les quatre cartes sur la procédure disciplinaire (k16, k17, k18, k37), par exemple, portent chacune sur une règle distincte.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la première relecture est tronqué dans sa partie « validation ». Les trois corrections qu'il détaille sont reprises ci-dessous.

| cible | problème | correction |
|---|---|---|
| k17 | La question parlait d'« un fait fautif » sans dire de qui : elle n'était pas tout à fait autosuffisante. | Question : « Au-delà de quel délai un fait fautif du salarié ne peut-il plus, à lui seul, donner lieu à des poursuites disciplinaires ? ». La réponse est inchangée. |
| k20 | La réponse disait seulement « Il est réputé avoir accepté la modification ». Elle omettait la condition posée par la fiche (Règles essentielles#11) : « à défaut de réponse dans ce délai ». | La réponse commence par « À défaut de réponse dans le délai imparti, il est réputé avoir accepté la modification. » Elle précise ensuite le délai : un mois à compter de la réception de la proposition, faite par lettre recommandée avec avis de réception (quinze jours en redressement ou liquidation judiciaire). |
| k27 | La réponse faisait conclure la visite de préreprise elle-même, et non le médecin du travail. Elle s'écartait ainsi de Règles essentielles#15 et de Ce qui a changé récemment#2. | La conclusion est rendue au médecin du travail (« le médecin du travail a conclu qu'aucun aménagement n'était nécessaire »). La liste des absences est resserrée pour rester sous 70 mots. La relecture d'exactitude a ensuite revu cette carte (voir ci-dessous). |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k04 | La question demandait « les » durées maximales fixées par le Code du travail. La réponse ne donne que les maxima de principe et leurs dérogations par accord. Le Code admet aussi des dérogations administratives : inspecteur du travail ou urgence pour la durée quotidienne, jusqu'à 60 heures par semaine en cas de circonstances exceptionnelles. | Question délimitée : « En principe, quelles durées maximales de travail quotidienne et hebdomadaire le Code du travail impose-t-il ? ». La réponse est inchangée : la fiche ne traite pas des dérogations administratives. | C. trav., art. L. 3121-18 à L. 3121-21 |
| k10 | La question (« Quelles règles encadrent la période et la durée de prise des congés payés ? ») était ambiguë. « Durée » pouvait appeler la durée totale du congé (30 jours ouvrables), alors que la réponse porte sur la période de prise et sur le fractionnement. | Question : « Que prévoit le Code du travail sur la période de prise des congés payés et sur leur fractionnement ? ». La réponse est inchangée. | C. trav., art. L. 3141-13, L. 3141-17, L. 3141-18 et L. 3141-23 |
| k14 | La réponse disait que le règlement intérieur « entre en vigueur un mois après les formalités de publicité ». Or il entre en vigueur à la date qu'il indique, qui doit être postérieure d'un mois au moins à ces formalités. | La réponse dit qu'il « ne peut entrer en vigueur qu'un mois au moins après les formalités de publicité » (66 mots). | C. trav., art. L. 1321-4 (loi n° 2026-403, art. 5) ; citation de Ce qui a changé récemment#3 |
| k22 | Selon l'arrêt cité par la fiche, le licenciement est sans cause réelle et sérieuse quand l'accord comporte des dispositions étrangères à ses objets **et modifiant le contrat**. Cette seconde condition manquait dans la question (alignement sur la carte k17 du chapitre ue3-01). | Question : « Que vaut le licenciement pour refus de clauses d'un accord de performance collective modifiant le contrat sans porter sur la durée du travail, la rémunération ou la mobilité interne ? ». La réponse est inchangée. | Cass. soc., 28 mai 2026, n° 24-19.461 et s. (citation de Ce qui a changé récemment#1) ; C. trav., art. L. 2254-2 |
| k25 | L'avis du CSE était présenté comme toujours requis. Les articles L. 1226-2 et L. 1226-10 le prévoient seulement « lorsqu'il existe » (pas de CSE en dessous de onze salariés). | « après avis du CSE lorsqu'il existe » (65 mots). | C. trav., art. L. 1226-2 et L. 1226-10 |
| k26 | La réponse ne vaut qu'en principe. Selon l'article L. 1226-14, alinéa 2, ces indemnités ne sont pas dues si l'employeur établit que le refus du reclassement par le salarié est abusif. La fiche ne mentionne pas cette exception. | Question délimitée : « En principe, quelles indemnités ouvre le licenciement d'un salarié pour inaptitude d'origine professionnelle ? ». La réponse est inchangée. | C. trav., art. L. 1226-14 |
| k27 | La dispense de visite de reprise était datée « depuis le 15 juin 2026 ». Or, selon la recherche n° 1, le décret n° 2026-503 ne s'applique qu'aux arrêts de travail délivrés à compter du lendemain de sa publication (JO du 14 juin 2026). La carte était donc trop large pour une reprise après un arrêt antérieur. | « Pour les arrêts de travail délivrés depuis le 15 juin 2026, elle n'est pas requise si… ». Deux mots retirés pour rester à 70 mots : « Congé de maternité, maladie professionnelle, … » ; « le médecin a conclu » (le médecin du travail est nommé dans la question). | Décret n° 2026-503 du 12 juin 2026 ; C. trav., art. R. 4624-31 ; recherche n° 1 |
| k35 | Le délai de prévenance réduit à quinze jours était présenté comme acquis dès que le congé suit immédiatement le congé de paternité ou d'adoption. L'article D. 1225-11-4 exige en outre que le congé débute dans le mois suivant la naissance ou l'arrivée de l'enfant. Le délai d'un mois est aussi un minimum. | La phrase devient « Le salarié prévient en principe l'employeur au moins un mois avant le début du congé. » La condition supplémentaire n'est pas dans la fiche, si bien que l'exception est seulement signalée par « en principe » (55 mots). | C. trav., art. D. 1225-11-4 (décret n° 2026-419 du 30 mai 2026) ; recherches n° 2 et 3 |
| k36 | Selon l'article L. 3252-2, le plafonnement par le barème joue « sous réserve des dispositions relatives aux pensions alimentaires » : le prélèvement direct au titre d'une pension alimentaire peut porter sur l'intégralité de la rémunération (L. 3252-5). La réponse ne valait donc qu'en principe. | Question délimitée : « En principe, dans quelles limites les sommes dues au salarié à titre de rémunération peuvent-elles être saisies ou cédées ? ». La réponse est inchangée : la somme égale au RSA forfaitaire est laissée au salarié « dans tous les cas ». | C. trav., art. L. 3252-2 et L. 3252-5 |

Les 26 autres cartes ont été contrôlées sans changement : k01 à k03, k05 à k09, k11 à k13, k15 à k20, k23, k24, k28 à k30, k32 à k34 et k37. Aucune ne contient de calcul ni de chiffre millésimé. Les dates de réforme figurent dans k08, k09, k22, k27 et k35 pour situer le changement ; ce ne sont pas des chiffres annuels.

## Recherches faites

3 recherches sur les 3 autorisées.

1. WebSearch, `allowed_domains` : legifrance.gouv.fr. Requête : « décret n° 2026-503 du 12 juin 2026 visite de reprise visite de préreprise R. 4624-31 aucun aménagement ».
   - **Confirmé.** Le décret existe et a été publié au JO du 14 juin 2026. Il modifie R. 4624-30 et R. 4624-31. La visite de reprise n'est pas requise après une visite de préreprise dans les trente jours précédant la reprise, lorsque le médecin du travail a conclu qu'aucune mesure d'aménagement, d'adaptation ou de transformation du poste, ni aucun aménagement du temps de travail, n'était nécessaire. Elle redevient requise à la demande du médecin, de l'employeur ou du travailleur. R. 4624-31 est en vigueur dans cette version depuis le 15 juin 2026.
   - **Précisé.** Le texte s'applique aux arrêts de travail délivrés à compter du 15 juin 2026 (carte k27).
   - **Non vérifié.** Le texte intégral du décret n'a pas été lu (page Légifrance inaccessible), et un seul résultat donne la règle d'application dans le temps.
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

1. **Règles essentielles#15 et Ce qui a changé récemment#2** (décret n° 2026-503).
   - Le décret s'applique aux arrêts de travail délivrés à compter du 15 juin 2026 : la mention « depuis le 15 juin 2026 » est trop large.
   - La conclusion du médecin porte aussi sur l'absence d'aménagement du temps de travail.
   - À reconfirmer sur le texte intégral : un seul résultat de recherche.
2. **Ce qui a changé récemment#0** (congé supplémentaire de naissance).
   - Le délai de quinze jours suppose aussi que le congé débute dans le mois suivant la naissance ou l'arrivée de l'enfant.
   - Le délai d'un mois est un minimum (« au moins un mois avant le début du congé »).
   - Le délai de neuf mois est prolongé lorsque le congé de maternité, de paternité ou d'adoption est allongé.
   - Le `src` devrait citer l'article D. 1225-11-4 et le décret n° 2026-419 du 30 mai 2026 (les décrets n° 2026-425 et 2026-426 portent sur l'indemnisation).
3. **Règles essentielles#14** (inaptitude et reclassement).
   - L'avis du CSE est requis « lorsqu'il existe ».
   - Le reclassement dans le groupe se limite aux entreprises situées sur le territoire national.
   - Les indemnités de l'article L. 1226-14 ne sont pas dues si l'employeur établit que le refus du reclassement par le salarié est abusif (al. 2).
4. **Règles essentielles#6** (saisie des rémunérations).
   - Ajouter la réserve des pensions alimentaires (L. 3252-2 et L. 3252-5) : le prélèvement direct peut porter sur l'intégralité de la rémunération, sous réserve de la somme égale au RSA forfaitaire.
   - Ajouter les seuils « affectés d'un correctif pour toute personne à charge ».
5. **Ce qui a changé récemment#3** (règlement intérieur). La formule « entre en vigueur un mois après les formalités de publicité » est à remplacer par : « à la date qu'il indique, postérieure d'un mois au moins aux formalités de publicité ».
6. **Règles essentielles#1** (complément, pas une erreur). Les durées maximales sont données sans les dérogations administratives :
   - dérogation de l'inspecteur du travail et cas d'urgence pour la durée quotidienne (L. 3121-18) ;
   - jusqu'à 60 heures par semaine sur autorisation administrative en cas de circonstances exceptionnelles (L. 3121-21).
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
