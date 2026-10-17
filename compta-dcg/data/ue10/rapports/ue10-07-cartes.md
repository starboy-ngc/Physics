# Cartes de notions : ue10-07 (Impôt sur les bénéfices, participation, subventions et abandons de créances)

Date : 16 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-07.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`) ; `src` et `url` sont copiés depuis le premier de ces items.
2. **Relectures de fidélité à la fiche.** Trois passes successives, sans recherche web, ont comparé chaque carte au texte de ses items de base. Elles ont corrigé 19 fois des cartes (certaines cartes à plusieurs reprises) et ajouté k34 et k35 pour couvrir deux règles essentielles. Elles n'ont rien supprimé.
3. **Relecture d'exactitude (la présente).** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 16 octobre 2026 : Code du travail, Code de la sécurité sociale, CGI et BOFiP, PCG modifié par le règlement ANC n° 2022-06 ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Une première exécution de cette relecture, interrompue, avait déjà fusionné k17 dans k16, resserré k21, ajouté k36 et retouché k11 et k13. Ces changements ont été relus et conservés, sauf k13, reprise pour rester fidèle à la fiche. La présente exécution a corrigé k13, k14 et k34. Elle a fait 3 recherches, restreintes aux sites officiels (voir « Recherches »).
4. **Validation.** `node validate.js data/ue10/ue10-07.cartes.json` : ✓ (35 cartes, dont 9 déf.).

## Bilan

- **Nombre de cartes : 35** (plafond du contrat). L'identifiant k17 reste vide, sans renumérotation.
- **Répartition : 9 cartes `def` et 26 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte : #0 k01 et k02, #1 k03 (et k16), #2 k04, #3 k05, #4 k06 et k07, #5 k08.
  - Toutes les « Règles essentielles » stables sont couvertes : #1 k09 et k10, #2 k11 et k34, #3 k12, #5 k13 et k14, #7 k15, #8 k16 et k35, #9 k18, #10 k19, #11 k20, #12 k36, #13 k22 et k23, #14 k24, #15 k26 et k27, #16 k28 et k29, #17 k30, #18 k31.
  - « Points de vigilance » : #0 k12, #1 k19, #2 k21, #3 k25, #4 k33, #5 k10.
  - « Ce qui a changé récemment » : #0 k27, #3 k32.
  - « Chiffres et seuils » : #1 k09, #2 k34, #4 k13 et k14.
- **Items de fiche sans carte :**
  - Règles essentielles #0 (taux de l'IS), #4 (CIR et CII) et #6 (contribution exceptionnelle) ; Chiffres et seuils #0, #3, #5 et #6 ; Ce qui a changé récemment #1, #2, #4 et #5. Tous sont millésimés : le contrat leur interdit de donner une carte. La règle de l'article 515-1 du PCG (Ce qui a changé récemment#4) est portée par Définitions#0, item stable (k02).
  - Points de vigilance#5, première moitié (régime des sociétés mères et quote-part de frais et charges). L'item est un renvoi au DSCG ; le jeu étant au plafond de 35 cartes, seule la seconde moitié (contribution sociale) a une carte (k10).
- **Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé.** Les chiffres présents sont stables et font partie d'une règle : 3,3 %, 763 000 € et 7 630 000 € (contribution sociale), 3 000 € (dispense d'acomptes), 1 000 000 € et cinq exercices (carry-back), cinquante salariés et cinq années civiles (participation), 5 % des capitaux propres (formule légale), 20 % des salaires et trois quarts du plafond de la sécurité sociale (intéressement), dix ans (subventions), onze salariés, trois exercices et 1 % (loi du 29 novembre 2023). La formule de la réserve spéciale de participation figure au verso de k03 comme définition, sans calcul à faire.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | ue10-07-k09 | La réponse se résumait à deux chiffres, sans dire ce qu'est la contribution. | Réponse ouverte par « Une contribution assise sur l'impôt sur les sociétés », puis les chiffres stables (3,3 %, abattement de 763 000 €) et le compte 6952. |
| 1 | ue10-07-k10 | Première base Points de vigilance#5, dont la source cite l'article 216 (sans rapport) ; question vague. | Base [Règles essentielles#1, Points de vigilance#5] ; question « Qu'est-ce qui ne peut pas être imputé sur la contribution sociale sur l'IS (CGI, art. 235 ter ZC) ? ». |
| 1 | ue10-07-k19 | Exception oubliée : la réserve constituée avant la clôture de l'exercice de référence peut, sous conditions, être déduite de cet exercice. | Question bornée par « En principe » ; exception ajoutée. |
| 1 | ue10-07-k20 | « Intéressement versé » contredisait la réponse (charge à payer). | Question sur l'intéressement « dû » en application d'un accord. |
| 1 | ue10-07-k24 | Question sans précision sur l'immobilisation ; réponse fausse pour une immobilisation non amortissable. | Question sur le régime optionnel de l'article 42 septies ; réponse couvrant biens amortissables, non amortissables et cession (exception de l'article 151 octies). |
| 1 | ue10-07-k28 | Aides consenties dans le cadre d'un accord L. 611-8 ou d'une procédure collective présentées comme déductibles sans limite. | Ajout : non commerciales, elles ne sont déductibles que dans certaines limites (détaillées par k29). |
| 1 | ue10-07-k30 | Condition « société mère au sens de l'article 145 » absente. | Condition ajoutée dans la question. |
| 1 | ue10-07-k31 | Question visant tous les abandons de créances, alors que seuls ceux de l'activité normale et courante sont classés selon leur nature. | Question bornée à l'« abandon de créance relevant de l'activité normale et courante ». |
| 1 | ue10-07-k34 (ajoutée) | Règles essentielles#2 (dispense d'acomptes) sans carte. | Carte sur la dispense (IS de référence n'excédant pas 3 000 €, premier exercice d'activité). |
| 1 | ue10-07-k35 (ajoutée) | Règles essentielles#8 (accord dérogatoire) sans carte. | Carte : avantages au moins équivalents, plafonds de l'article L. 3324-2. |
| 2 | ue10-07-k09 | Exonération des petites entreprises absente. | Exonération ajoutée (chiffre d'affaires inférieur à 7 630 000 €, capital libéré et détenu à 75 % par des personnes physiques) ; base Règles essentielles#1 et Chiffres et seuils#1. |
| 2 | ue10-07-k14 | Le remboursement ne visait pas seulement la fraction non utilisée de la créance. | « La fraction non utilisée est remboursée à l'issue de ce délai » ; Chiffres et seuils#4 ajouté en base. |
| 2 | ue10-07-k28 | Fin de réponse incorrecte ; impôt visé non précisé dans la question. | Question « Pour l'impôt sur les bénéfices… » ; fin de réponse réécrite. |
| 2 | ue10-07-k29 | « Déductible chez le créancier » laissait flou le cadre fiscal. | « … déductible du résultat imposable du créancier ? ». |
| 2 | ue10-07-k15 | Formulation éloignée de la fiche sur l'article L. 130-1 du CSS. | Reprise de « mentionnée au II de l'article L. 130-1 du Code de la sécurité sociale ». |
| 2 | ue10-07-k34 | Seuil et date du solde aussi détaillés dans Chiffres et seuils#2. | Chiffres et seuils#2 ajouté en second item de base. |
| 3 | ue10-07-k02 | Contributions dites « présentées » au lieu de « comptabilisées » dans la rubrique « Impôts sur les bénéfices ». | Vocabulaire de l'article 515-1 repris. |
| 3 | ue10-07-k11 | « Reposent sur » au lieu de « calculés sur » le dernier exercice clos. | Vocabulaire de la fiche repris. |
| 3 | ue10-07-k14 | Question trop ouverte (« Que devient la créance… ? ») ; cessibilité sans son cadre. | Question « Comment l'entreprise utilise-t-elle la créance… ? » ; cessibilité « dans les conditions des articles L. 313-23 et suivants du Code monétaire et financier ». |
| 3 | ue10-07-k26 | « Classe 74 » : une classe du PCG se désigne par un seul chiffre. | « Compte 74 ». |
| 3 | ue10-07-k31 | « Classes 65 / 75 » et « 66 / 76 » : même impropriété. | « Comptes 65 / 75 » et « comptes 66 / 76 ». |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-07-k16 et ue10-07-k17 (supprimée) | Exécution interrompue. Les deux cartes découpaient une même liste : k16 demandait les capitaux propres « hors provisions », k17 les provisions. Ce doublon artificiel rendait k16 incomplète sans sa jumelle. | k16 donne la liste complète des capitaux propres (capital, primes, réserves, report à nouveau, provisions ayant supporté l'impôt, provisions réglementées) et précise que la réserve spéciale de participation n'y figure pas. k17 est supprimée, son identifiant laissé vide. | C. trav., art. D. 3324-4 ; Règles essentielles#8 |
| ue10-07-k21 | Exécution interrompue. « Quelles sont les différences essentielles entre l'intéressement et la participation ? » admettait bien d'autres réponses justes : formule de calcul, mise en place, régime social, indisponibilité. | Question limitée au caractère obligatoire et à l'exercice de déduction fiscale. Les plafonds de l'intéressement passent sur une carte propre (k36). Base réduite à Points de vigilance#2. | CGI, art. 237 ter A et 237 bis A ; Points de vigilance#2 |
| ue10-07-k36 (ajoutée) | Exécution interrompue. Après le resserrement de k21, Règles essentielles#12 (plafonds de l'intéressement) n'avait plus de carte. | Carte sur le plafond global (20 % des salaires bruts, augmenté le cas échéant de la rémunération des dirigeants bénéficiaires) et le plafond individuel (trois quarts du plafond annuel moyen de la sécurité sociale). C'est une règle stable, sans montant annuel. | C. trav., art. L. 3314-8 ; Règles essentielles#12 |
| ue10-07-k11 | Exécution interrompue. La règle « calculés sur le dernier exercice clos » souffre des exceptions, dont le dernier acompte des grandes entreprises, ajusté sur l'impôt estimé de l'exercice en cours. | Question bornée par « En principe ». Réponse inchangée. | CGI, art. 1668 ; Règles essentielles#2 |
| ue10-07-k13 | L'exécution interrompue avait ajouté « dans la limite de la fraction non distribuée de ce bénéfice ». C'est exact (CGI, art. 220 quinquies, recherche 2), mais absent de la fiche, qui ne parle que du « bénéfice de l'exercice précédent » et du « bénéfice d'imputation ». La carte n'était donc plus fidèle. | « Le déficit de l'exercice est imputé sur le bénéfice de l'exercice précédent (bénéfice d'imputation), dans la limite de 1 000 000 €. Il en naît une créance sur le Trésor égale à l'IS antérieurement versé sur ce bénéfice d'imputation. » C'est exact et fidèle, sans laisser croire que tout le bénéfice est imputable. La fiche est signalée. | CGI, art. 220 quinquies (recherche 2) ; Règles essentielles#5 ; Chiffres et seuils#4 |
| ue10-07-k14 | « Elle l'impute sur l'IS des cinq exercices suivants ; la fraction non utilisée est remboursée à l'issue de ce délai » est le principe. Une entreprise en sauvegarde, redressement ou liquidation judiciaire peut demander le remboursement anticipé de la créance non utilisée. | Question bornée par « En principe ». Réponse inchangée. | CGI, art. 220 quinquies, I ; Règles essentielles#5 |
| ue10-07-k34 | « Dans les autres cas, quatre acomptes trimestriels sont dus, le solde étant versé au plus tard le 15 du quatrième mois… » rattachait la date limite aux seules sociétés qui versent des acomptes. Or une société dispensée paie aussi tout son impôt à cette date. | « Sinon, quatre acomptes trimestriels sont dus. Dans tous les cas, l'impôt restant dû est versé au plus tard le 15 du quatrième mois suivant la clôture. » Le reste est inchangé (44 mots). | CGI, art. 1668, 1 ; Règles essentielles#2 ; Chiffres et seuils#2 |

Les 28 autres cartes ont été jugées exactes au 16 octobre 2026, sans ambiguïté qui justifie une retouche. Les points contrôlés sont les suivants.

**Impôt sur les sociétés**
- k01 et k02 : comptes 444, 695, 6951, 6952 et 6954 du plan de comptes 2026, et article 515-1 du PCG réécrit par le règlement ANC n° 2026-04. La recherche 3 a confirmé que ce règlement existe sur le site de l'ANC.
- k09 et k10 : CGI, art. 235 ter ZC. Ni les crédits d'impôt de toute nature ni la créance de carry-back ne sont imputables sur la contribution sociale.
- k12 : la recherche 3 confirme que la FAQ CNCC-CNOEC sur le règlement ANC n° 2022-06 enregistre les crédits d'impôt imputables sur l'IS au crédit du compte 695. La carte attribue expressément cette position à la FAQ.
- k33 : la recherche 1 confirme la décision du Conseil d'État (13 mars 2025, n° 481538, Sté TDA). Le chiffre d'affaires s'apprécie au niveau du groupe qui détient la société, qu'il soit fiscalement intégré ou non. L'actualité d'impots.gouv.fr citée par la fiche le confirme.

**Participation et intéressement**
- k03, k16 et k35 : C. trav., art. L. 3324-1, L. 3324-2 et D. 3324-4.
- k04 : C. trav., art. L. 3312-1. La mention « en principe par accord » couvre la décision unilatérale permise aux petites entreprises.
- k15 : C. trav., art. L. 3322-1 s. et L. 3322-5, CSS, art. L. 130-1.
- k18 et k19 : comptes 691 et 4284 ; CGI, art. 237 bis A.
- k20, k21 et k36 : CGI, art. 237 ter A ; C. trav., art. L. 3314-8.
- k32 : loi n° 2023-1107, art. 5.

**Subventions**
- k05, k22, k23 et k25 : PCG, art. 312-1.
- k24 : CGI, art. 42 septies.
- k26 et k27 : comptes 741, 742 et 747. Les anciens comptes 7715 et 777 relevaient du résultat exceptionnel.

**Abandons de créances**
- k06 et k07 : BOI-BIC-BASE-50-10.
- k28 et k29 : CGI, art. 39, 13.
- k30 : CGI, art. 216 A.
- k08 et k31 : PCG, art. 513-5.

**Doublons.** Plusieurs cartes se recouvrent en partie, mais chacune pose une question distincte :
- k04, k15 et k21 : la définition de l'intéressement, le champ de l'obligation de participation, puis la distinction entre les deux dispositifs ;
- k19 et k21 : le principe de déduction de la participation, puis la comparaison avec l'intéressement ;
- k22, k23, k24 et k25 : la reprise comptable (bien amortissable, bien non amortissable), l'étalement fiscal, puis l'écart entre les deux ;
- k28 et k29 : les aides déductibles, puis la limite des aides non commerciales ;
- k08, k27 et k31 : la définition du résultat exceptionnel, puis ses conséquences pour les subventions et les abandons de créances.

Seul le doublon k16 / k17 a donné lieu à une fusion.

## Recherches

Trois recherches WebSearch, restreintes aux sites officiels :

1. **impots.gouv.fr, bofip.impots.gouv.fr, legifrance.gouv.fr, conseil-etat.fr : « taux réduit impôt sur les sociétés chiffre d'affaires groupe Conseil d'État 13 mars 2025 TDA ».**
   - Dans la décision CE, 13 mars 2025, n° 481538, Sté TDA, le chiffre d'affaires de la société qui détient la PME s'apprécie en tenant compte de l'ensemble du groupe, intégré ou non.
   - L'actualité d'impots.gouv.fr en tire la règle reprise par la fiche. k33 est confirmée.
   - Sources : [CE, 13 mars 2025, n° 481538](https://www.conseil-etat.fr/fr/arianeweb/CE/decision/2025-03-13/481538), [Légifrance, CETATEXT000051328719](https://www.legifrance.gouv.fr/ceta/id/CETATEXT000051328719), [impots.gouv.fr, « Taux réduit d'IS : le critère du chiffre d'affaires revu pour les entreprises appartenant à des groupes »](https://www.impots.gouv.fr/actualite/taux-reduit-dimpot-sur-les-societes-le-critere-du-chiffre-daffaires-revu-pour-les).
2. **legifrance.gouv.fr, bofip.impots.gouv.fr : « article 220 quinquies CGI report en arrière déficit "fraction non distribuée" bénéfice 1 000 000 € ».**
   - Le déficit est imputable sur le bénéfice de l'exercice précédent, dans la limite de la fraction non distribuée de ce bénéfice et de 1 000 000 €.
   - Le bénéfice d'imputation exclut aussi la fraction ayant donné lieu à un impôt payé au moyen de crédits d'impôt, ainsi que, depuis la loi de finances pour 2022 (art. 15), au moyen de réductions d'impôt.
   - La créance s'impute sur l'IS des cinq exercices suivants ; le solde est remboursé à l'issue de ce délai.
   - k13 est reformulée et la fiche signalée.
   - Sources : [CGI, art. 220 quinquies](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000053560738), [BOI-IS-DEF-20-10](https://bofip.impots.gouv.fr/bofip/5645-PGP.html/identifiant=BOI-IS-DEF-20-10-20230621), [BOI-IS-DEF-20-20](https://bofip.impots.gouv.fr/bofip/5647-PGP.html/identifiant=BOI-IS-DEF-20-20-20220202), [ACTU-2021-00302](https://bofip.impots.gouv.fr/bofip/13409-PGP.html/ACTU-2021-00302).
3. **anc.gouv.fr, cncc.fr, experts-comptables.fr, bofip.impots.gouv.fr : « crédit d'impôt recherche comptabilisation compte 695 diminution impôt sur les bénéfices règlement ANC 2022-06 FAQ ».**
   - La FAQ CNCC-CNOEC sur le règlement ANC n° 2022-06 enregistre les crédits d'impôt imputables sur l'IS au crédit du compte 695.
   - Le règlement ANC n° 2026-04 traite aussi des crédits d'impôt imputables sur l'IS, CIR compris. Dans les comptes individuels, il les comptabilise en diminution de l'impôt sur les bénéfices.
   - En revanche, le BOFiP (BOI-BIC-RICI-10-10-50, 2021) mentionne encore un crédit au compte 699 « Produits – Crédit d'impôt recherche ».
   - k12 est confirmée.
   - Sources : [FAQ CNCC-CNOEC, règlement ANC n° 2022-06](https://doc.cncc.fr/docs/faq-questions-reponses-relatives/attachments/faq-cncc-cnoec-reglement-n2022-06-relatif-a-la-modernisation-des-etats-financiers-plan-de-comptes-et-ecritures-comptables), [règlement ANC n° 2026-04, recueil](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2026/2026%20homologu%C3%A9/REGLT_2026_04_-recueil.pdf), [BOI-BIC-RICI-10-10-50](https://bofip.impots.gouv.fr/bofip/4669-PGP.html/identifiant=BOI-BIC-RICI-10-10-50-20210713).

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Les points 1 à 3 sont nouveaux ; les points 4 à 7 viennent des relectures de fidélité et restent d'actualité.

1. **Règles essentielles#5 et Chiffres et seuils#4 (carry-back).** Le déficit n'est imputable que sur la **fraction non distribuée** du bénéfice de l'exercice précédent. Le bénéfice d'imputation exclut aussi les bénéfices exonérés et ceux dont l'impôt a été payé au moyen de crédits ou de réductions d'impôt (CGI, art. 220 quinquies ; BOI-IS-DEF-20-10 ; recherche 2). « Dans la limite du plus faible du bénéfice de l'exercice précédent et de 1 000 000 € » est donc incomplet. La carte k13 s'en tient au « bénéfice d'imputation ».
2. **Règles essentielles#5 (carry-back), à compléter.** L'item ne mentionne pas le remboursement anticipé de la créance non utilisée, que peut demander une entreprise en sauvegarde, redressement ou liquidation judiciaire (CGI, art. 220 quinquies, I). La carte k14 dit « En principe ».
3. **Règles essentielles#3 et Points de vigilance#0 (crédits d'impôt).** Le règlement ANC n° 2026-04 traite expressément des crédits d'impôt imputables sur l'IS, CIR compris (recherche 3). Il pourrait être cité à côté de la FAQ CNCC-CNOEC. La fiche pourrait aussi signaler que le BOFiP (BOI-BIC-RICI-10-10-50) et des ouvrages antérieurs utilisent le compte 699.
4. **Définitions#0 et Ce qui a changé récemment#4 (article 515-1 du PCG).** Le même contenu est marqué « stable » dans le premier item et « millésimé 2026 » dans le second. La date d'application du règlement ANC n° 2026-04 n'est pas indiquée (relecture de fidélité 1).
5. **Règles essentielles#15 et #18.** « Classe 74 », « classes 65 / 75 » et « classes 66 / 76 » : ce sont des comptes, pas des classes (relecture de fidélité 3).
6. **Chiffres et seuils#3, à vérifier.** Le « taux de 60 % outre-mer » du CII n'apparaît pas dans Règles essentielles#4 et paraît antérieur à la baisse du taux de droit commun à 20 % par la loi de finances pour 2025 (relectures de fidélité 1 à 3). Aucune carte ne repose sur cet item millésimé.
7. **Références à harmoniser.**
   - Règles essentielles#5 et Chiffres et seuils#4 renvoient à deux versions différentes du BOFiP.
   - Définitions#5 et Règles essentielles#13 renvoient au PCG au 1er janvier 2025, et Définitions#3 au PCG au 1er janvier 2026 pour le même article 312-1 (relectures de fidélité 1 et 2).

## Classement des exercices

Le classement automatique des exercices du chapitre (QCM, QCM multiples et classements) donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 18 | oui |
| `calcul` | 1 | non |
| `chiffre` | 0 | non |

Les classeurs n'ont relevé aucun désaccord.
- Le seul QCM de nature `calcul` demande la reprise annuelle au compte 747 d'une subvention d'investissement finançant une machine amortie en linéaire. Il reste dans le chapitre mais sort des révisions espacées.
- Les 10 autres exercices du chapitre (calculs et écritures) relèvent par nature du calcul.
- Les 18 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable.
