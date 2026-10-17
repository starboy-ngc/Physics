# Cartes de notions : ue4-04 (L'impôt sur les sociétés)

*16 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-04.fiche.json`, et d'elle seule. Elles suivent le contrat (section 8) :
   - une question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : trois passes successives ont contrôlé les 35 cartes. Leur seul juge était le texte (`t` et `cite`) des items de la fiche. Elles ont vérifié que chaque carte dit ce que dit la fiche, sans rien y ajouter, et respecte la forme du contrat. Aucune recherche n'a été faite à ce stade.
3. **Relecture d'exactitude** : un second relecteur, indépendant, a repris les 35 cartes sous quatre angles :
   - **Exactitude** : la carte est-elle juste au regard du droit en vigueur au 16 octobre 2026 (CGI, BOFiP, PCG modifié par le règlement ANC 2022-06) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne dit pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG, et la seule juste ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Cette relecture s'est faite en deux temps. Une première passe a corrigé cinq cartes (k04, k13, k18, k20, k30). La reprise, présentée ici, a relu de nouveau les 35 cartes, y compris ces cinq corrections. Elle a maintenu quatre corrections, refait celle de k30, qui s'écartait de la fiche sans raison valable, et resserré la question de k07. Quand une correction ajoute une précision, celle-ci reste dans le vocabulaire de la fiche. L'item de fiche en cause est alors signalé plus bas, et la fiche n'est pas modifiée.
4. **Recherches** : trois pour la reprise, le maximum permis, limitées à legifrance.gouv.fr et bofip.impots.gouv.fr (détail plus bas). Les autres points ont été tranchés sans recherche, à partir de la fiche et du texte connu des articles.

Validation : `node validate.js data/ue4/ue4-04.cartes.json` renvoie « ✓ data/ue4/ue4-04.cartes.json (cartes, 35 (7 déf.)) ». Toutes les questions comptent de 6 à 30 mots et toutes les réponses de 8 à 70 mots.

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k35, sans trou) |
| Définition (`def`) | 7 (k01, k03, k09, k12, k19, k29, k34) |
| Compréhension (`comp`) | 28 |
| Cartes corrigées par les relectures de fidélité | 8 (k13, k15, k19, k24, k31, k32, k33, k34) |
| Cartes corrigées par la relecture d'exactitude | 6 (k04, k13, k18, k20 en première passe ; k07 et k30 lors de la reprise) |
| Cartes supprimées | 0 |
| Cartes ajoutées | 0 (le jeu est au plafond de 35) |

**Couverture des items de la fiche** :

- **Définitions** : les 5 items ont au moins une carte. #0 : k01, k02, k05 ; #1 : k03, k04 ; #2 : k09 ; #3 : k12, k13 ; #4 : k19.
- **Règles essentielles** : les 16 items stables ont au moins une carte. Règles essentielles#16 (crédit d'impôt recherche) n'est que la seconde base de k35, qui porte sur le crédit d'impôt innovation.
- **Ce qui a changé récemment** : les 4 items stables ont une carte. #2 : k16 ; #3 : k35 ; #5 : k25 ; #6 : k32.
- **Points de vigilance** : 4 items sur 5. #0 : k14 ; #1 : k20 ; #2 : k26 ; #3 : k27.
- **Chiffres et seuils#0** (taux de l'IS) : k24 et k20.

**Items de la fiche sans carte** :

- **Items millésimés**, exclus par le contrat :
  - Règles essentielles#13 (limites des régimes d'imposition pour 2026 à 2028) ;
  - Chiffres et seuils#4 et #5 (taux maximal des intérêts de comptes courants, 2025 et 2026) ;
  - Ce qui a changé récemment#0 et #1 (contribution exceptionnelle des grandes entreprises) et #4 (LFSS 2026, prélèvements sociaux).
- **Items stables sans carte propre** :
  - Chiffres et seuils#1 (contribution sociale : taux, abattement, conditions d'exonération). La règle d'imputation est couverte par k27.
  - Chiffres et seuils#2 (plafonds d'amortissement des véhicules de tourisme). L'item ne contient que des montants ; la règle est couverte par k17.
  - Chiffres et seuils#3 (dispense du prélèvement de 12,8 %). L'item ne contient que des seuils de revenu ; k33 mentionne la dispense.
  - Points de vigilance#4 (abattement fixe du dirigeant qui part à la retraite).
- **Parties d'items non couvertes**, faute de place :
  - Règles essentielles#1, seconde partie : option des SA, SAS et SARL jeunes et non cotées pour le régime des sociétés de personnes (art. 239 bis AB) ;
  - Règles essentielles#3, dernière phrase : notion de créance acquise ;
  - Règles essentielles#4, dernière phrase : imposition du gérant majoritaire de SARL selon les règles des traitements et salaires ;
  - Règles essentielles#15, dernière phrase : imputation des déficits antérieurs à l'entrée dans le groupe sur le seul bénéfice propre ;
  - Règles essentielles#16 : le crédit d'impôt recherche lui-même.

  Si une place se libère, la carte sur le gérant majoritaire de SARL (Règles essentielles#4) est la plus attendue au DCG.

## Corrections des relectures de fidélité

Trois passes ont contrôlé chacune les 35 cartes. Elles n'ont supprimé ni ajouté aucune carte. Quand une carte a été reprise par plusieurs passes, seule la dernière rédaction subsiste.

| Passe | Cible | Problème | Correction |
|---|---|---|---|
| 1 | k15 | La réponse disait que les intérêts « ne sont déductibles que » jusqu'au taux moyen des établissements de crédit. Elle oubliait l'exception de Règles essentielles#5 : pour les sommes avancées par une entreprise liée ou associée, la société peut déduire jusqu'au taux d'un établissement financier indépendant, si elle le justifie. | Ajout de cette faculté (68 mots). Correction reprise par la passe 2. |
| 1 | k19 | La question portait sur la distinction entre plus-value à court terme et à long terme : c'était une carte de compréhension, typée `def`. | Nouvelle question : « Qu'est-ce qu'une plus-value à court terme au sens du Code général des impôts ? ». Type `def` conservé ; réponse réécrite au singulier, fidèle à Définitions#4. |
| 1 | k24 | « Le taux réduit d'impôt sur les sociétés » laissait une autre réponse juste : la fiche cite aussi le taux de 0 % des plus-values sur titres de participation. | La question vise « le taux réduit de 15 % » (chiffre stable de Chiffres et seuils#0). Réponse inchangée. |
| 1 | k31 | Les quatre acomptes étaient présentés comme dus par toute société, sans la dispense de Règles essentielles#12. | Ajout : « Sont dispensées d'acomptes les sociétés nouvelles pour leur premier exercice et celles dont l'IS de référence n'excède pas 3 000 €. » |
| 1 | k33 | « Comment sont imposés les dividendes… » admettait deux réponses : le PFU de 12,8 % (impôt sur le revenu) ou le PFU global avec les prélèvements sociaux. | La question précise « … sont-ils imposés à l'impôt sur le revenu ? ». Réponse inchangée. |
| 1 | k34 | La définition omettait les conditions propres à la société mère (soumise à l'IS, non détenue à 95 % au moins par une autre personne morale soumise à l'IS). | Réponse réécrite avec ces conditions. Reprise par les passes 2 et 3. |
| 2 | k13 | La question bornait la liste aux opérations « au profit de ses associés », alors que la fiche ne rattache aux associés que les avances et prêts. | Nouvelle question : « Quelles opérations d'une société le Code général des impôts considère-t-il notamment comme des revenus distribués (art. 111) ? ». |
| 2 | k15 | La réponse étendait le taux de marché aux entreprises associées sans la condition de date de la fiche, approchait les 70 mots et doublonnait k16. | La question exclut les avances d'une entreprise liée ou associée. La réponse ne garde que la règle générale : capital entièrement libéré, taux plafond, excédent réintégré (53 mots). Le régime des entreprises liées et associées reste couvert par k16. |
| 2 | k34 | « Se constitue seule redevable » effaçait le caractère optionnel du régime ; « ses filiales détenues à 95 % » s'écartait du texte. | « Peut se constituer seule redevable… », « les sociétés qu'elle détient à 95 % au moins », « l'option vaut cinq exercices ». |
| 2 | (fichier) | Date de mise à jour. | `maj` passe à 2026-10-16. |
| 3 | k32 | « Comment l'impôt sur les bénéfices est-il comptabilisé ? » était trop ouvert : une réponse par comptes (695 / 444), absente de la fiche, était possible. | La question demande « à quel exercice et à quel taux » l'impôt est comptabilisé selon l'article 515-1 du PCG réécrit par le règlement ANC n° 2026-04. La réponse est reprise de Ce qui a changé récemment#6. |
| 3 | k34 | La réponse comptait 71 mots et mêlait à la définition la règle des déficits antérieurs à l'entrée dans le groupe. | Réponse ramenée à 68 mots, limitée à la définition (régime optionnel, détention de 95 % au moins, condition propre à la mère, option pour cinq exercices). |

La passe 2 a aussi signalé un point de fiche (Points de vigilance#1, « taxée au taux normal ») ; il est repris plus bas.

## Corrections de la relecture d'exactitude

### Corrections de la reprise

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k30 | La première passe d'exactitude avait remplacé le montant de la créance donné par la fiche (« égale à l'IS acquitté sur le bénéfice ainsi absorbé ») par « évaluée aux taux de l'IS de l'exercice déficitaire ». Cette formule est inexacte. L'excédent d'impôt fait naître une créance **d'égal montant**, c'est-à-dire l'impôt effectivement payé sur le bénéfice d'imputation. Le BOFiP précise d'ailleurs que, si ce bénéfice a été imposé pour partie au taux réduit, le déficit s'impute d'abord sur la fraction imposée au taux normal. Cette règle n'aurait aucun sens si le taux de l'exercice déficitaire s'appliquait. La carte n'était donc plus portée par sa base, et elle était fausse dès que le taux avait changé entre les deux exercices. | « **Une créance sur le Trésor, égale à l'IS acquitté sur le bénéfice ainsi absorbé** ; elle est utilisable pour payer l'IS des exercices clos au cours des cinq années suivantes et remboursée au terme de ce délai, ou par anticipation, sur demande, en cas de conciliation, de sauvegarde, de redressement ou de liquidation judiciaires. » (54 mots). La mention « sur demande » est conservée, car la loi ouvre à l'entreprise la faculté de demander ce remboursement. Base inchangée (Règles essentielles#11). | CGI, art. 220 quinquies, I ; BOI-IS-DEF-20-20 et BOI-IS-DEF-20-10 (recherche n° 1) |
| k07 | « Comment un entrepreneur individuel relevant d'un régime réel peut-il être soumis à l'IS ? » admettait une autre réponse juste : apporter son entreprise à une société soumise à l'IS (SASU, EURL ayant opté). Ce n'est pas la réponse attendue. | Nouvelle question : « **Sans constituer de société**, comment un entrepreneur individuel relevant d'un régime réel peut-il être soumis à l'impôt sur les sociétés ? » (21 mots). Réponse inchangée (option pour l'assimilation à une EURL ou à une EARL). | CGI, art. 1655 sexies ; fiche, Règles essentielles#2 |

### Corrections de la première passe, contrôlées et maintenues

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k20 | « Taxée au taux normal » est faux pour une PME éligible : la plus-value, comprise dans le résultat, profite du taux réduit de 15 % dans la limite du plafond de bénéfice. La passe 2 de fidélité avait relevé le point sans corriger la carte. | « **Elle est comprise dans le résultat de l'exercice et imposée aux taux de droit commun de l'IS** (taux normal ou, dans sa limite, taux réduit des PME) : … ». Chiffres et seuils#0 devient la seconde base ; `src` et `url` restent ceux de Points de vigilance#1. | CGI, art. 219, I et I-b ; fiche, Chiffres et seuils#0 |
| k18 | La réponse omettait une condition attendue par un correcteur du DCG : la perte ou la charge provisionnée doit être **elle-même déductible**. Par exemple, une provision pour amende fiscale n'est pas déductible. | « … pertes ou charges nettement précisées, **elles-mêmes déductibles**, que des événements en cours rendent probables… ». La reprise a vérifié la seconde phrase de la carte : la non-déductibilité des provisions pour indemnités de licenciement économique est confirmée (recherche n° 3). | CGI, art. 39, 1-5° ; BOI-BIC-PROV-20-10 ; BOI-BIC-PROV-30-20-10-20 |
| k13 | Les avances et prêts consentis aux associés ne sont réputés distribués que **sauf preuve contraire** : c'est une présomption simple. | « Les avances ou prêts consentis aux associés **(sauf preuve contraire)**, … ». | CGI, art. 111, a |
| k04 | La liste était présentée comme exhaustive, alors que d'autres structures relèvent du régime des sociétés de personnes (groupements d'intérêt économique, sociétés de fait). | La réponse commence par « **Notamment** aux commandités… ». | CGI, art. 8, 238 bis L et 239 quater |

### Cartes contrôlées et maintenues sans changement (29 cartes)

- **Charges réintégrées (k11, k13, k14)** : la recherche n° 2 confirme que les intérêts excédentaires de comptes courants d'associés, comme les rémunérations excessives et les avantages occultes, sont exclus de l'abattement de 40 % (BOI-RPPM-RCM-20-10-30-10). k14 est exacte. La rémunération excessive apparaît dans les trois cartes, mais chacune interroge un angle distinct : la condition de déduction (k11), la liste de l'article 111 (k13) et la double conséquence fiscale (k14). Aucune fusion n'est nécessaire.
- **Taux réduit des PME (k24, k25, k26)** : exacts au regard de l'article 219, I-b et de CE, 13 mars 2025, n° 481538. k26 énonce la règle d'adaptation de la limite à la durée de l'exercice sans rien faire calculer ; le contrat l'admet.
- **Véhicules de tourisme (k17)** : la carte est exacte. L'exception des véhicules nécessaires à l'activité en raison même de son objet (taxis, auto-écoles, loueurs) n'est pas citée. C'est un cas marginal, et la carte ne devient pas fausse pour autant.
- **Régime mère-fille (k22, k23)** : les cartes sont exactes. La quote-part de 1 % vaut aussi pour certaines filiales établies dans l'Union européenne qui rempliraient les conditions de l'intégration si elles étaient françaises. k23 ne vise que le groupe intégré, ce qui est vrai, mais incomplet.
- **Textes récents (k16, k32, k35)** : l'extension aux entreprises associées de la déduction au taux de marché (loi n° 2026-103, art. 14), la réécriture de l'article 515-1 du PCG par le règlement ANC n° 2026-04 et la réforme du crédit d'impôt innovation par la loi de finances pour 2025 sont reprises de la fiche, qui cite le BOFiP et le texte du règlement. La question de k35 vise ce qu'a changé la loi de finances pour 2025 : elle reste exacte même si le dispositif évolue ensuite.
- **Paiement de l'IS (k31)** : les acomptes sont calculés sur le dernier exercice clos. Les très grandes entreprises, qui doivent ajuster le dernier acompte sur l'IS estimé de l'exercice en cours, ne sont pas citées. Le cas sort du programme et la fiche ne le mentionne pas.
- **Doublons apparents** : plusieurs paires de cartes reposent sur le même item, mais chacune interroge un angle distinct.

  | Cartes | Angles interrogés |
  |---|---|
  | k01 / k02 | définition de l'IS ; sociétés soumises de plein droit |
  | k03 / k04 | translucidité fiscale ; entités concernées |
  | k05 / k06 | option de la SARL de famille ; renonciation à l'option pour l'IS |
  | k12 / k13 | définition générale (art. 109) ; présomptions de l'article 111 |
  | k15 / k16 | règle générale des comptes courants ; taux de marché pour les entreprises liées et associées |
  | k22 / k23 | conditions du régime mère-fille ; effet |
  | k29 / k30 | report en arrière ; créance qui en naît |
- **Chiffres stables** : plusieurs cartes citent des chiffres fixés par la loi, sans révision annuelle. Dans chaque cas, la question porte sur la règle, ce que le contrat admet :
  - k14 et k33 : abattement de 40 % ; k33 : 12,8 % ;
  - k21 : 12 % ; k22 et k23 : 5 % et 1 % ;
  - k24 : 15 %, 10 millions d'euros, 75 % ;
  - k27 : 3,3 % ;
  - k28 et k29 : 1 000 000 € ;
  - k31 : 3 000 € ;
  - k34 : 95 % ;
  - k35 : 20 %, 30 % et 400 000 €.

## Recherches faites

Trois recherches ont été faites lors de la reprise, limitées à legifrance.gouv.fr et bofip.impots.gouv.fr.

1. **CGI, art. 220 quinquies : montant de la créance de report en arrière.**
   - Résultat : selon BOI-IS-DEF-20-20 (version du 2 février 2022), l'excédent d'impôt fait naître une créance d'égal montant, qui correspond à l'impôt acquitté sur le bénéfice d'imputation. Selon BOI-IS-DEF-20-10, quand ce bénéfice a été imposé pour partie au taux réduit, le déficit s'impute d'abord sur la fraction imposée au taux normal.
   - Conséquence : la formule de la fiche est exacte ; celle que la première passe avait mise dans k30 ne l'est pas. k30 est corrigée et le point de fiche correspondant de la première passe est retiré.
2. **Intérêts excédentaires de comptes courants et abattement de 40 %.**
   - Résultat : BOI-RPPM-RCM-20-10-30-10 exclut de l'abattement les intérêts excédentaires de comptes courants d'associés.
   - Conséquence : Points de vigilance#0 et k14 sont exacts.
3. **CGI, art. 39, 1-5° : provisions pour indemnités de licenciement économique.**
   - Résultat : ces provisions ne sont pas déductibles des résultats des exercices clos à compter du 15 octobre 1997, que le licenciement économique soit individuel ou collectif (BOI-BIC-PROV-30-20-10-20).
   - Conséquence : la seconde phrase de k18 est exacte.

## Points à reprendre dans la fiche

- **Règles essentielles#11 (report en arrière)** : « le remboursement est anticipé en cas de conciliation… » laisse croire à un remboursement automatique. L'entreprise **peut demander** le remboursement anticipé de sa créance non utilisée (art. 220 quinquies, I). Le montant de la créance (« égale à l'IS acquitté sur le bénéfice ainsi absorbé ») est exact : la première passe d'exactitude proposait de le remplacer, et cette proposition est retirée.
- **Points de vigilance#1 (plus-values des sociétés à l'IS)** : point déjà relevé par la passe 2 de fidélité. « Taxée au taux normal » est à remplacer par « taxée aux taux de droit commun de l'IS » : une PME éligible bénéficie du taux réduit sur la fraction de bénéfice qui y ouvre droit, plus-value comprise.
- **Règles essentielles#7 (provisions)** : il faut ajouter la condition selon laquelle la perte ou la charge provisionnée doit être **elle-même déductible** (BOI-BIC-PROV-20-10). k18 la mentionne déjà.
- **Définitions#3 (revenus distribués)** : les avances, prêts ou acomptes consentis aux associés ne sont réputés distribués que **sauf preuve contraire** (art. 111, a). k13 le mentionne déjà.
- **Définitions#1 (sociétés de personnes)** : la liste devrait être introduite par « notamment ». Elle omet par exemple les groupements d'intérêt économique (art. 239 quater) et les sociétés de fait (art. 238 bis L).

## Classement des exercices

Classement automatique, selon leur nature, des exercices QCM, QCM multiples et classements (tri) du chapitre :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 13 |
| `calcul` (montant, taux, prorata, délai) | 5 |
| `chiffre` (rappel d'un chiffre millésimé) | 1 |
| **Total** | 19 |

Deux désaccords ont été relevés entre les classements, et tranchés en faveur de `calcul` :

- **Exercice #1** : imposition du bénéfice d'une SNC réparti entre deux associés. Il demande un montant ; il est classé `calcul`.
- **Exercice #4** : rémunération jugée excessive du président d'une SAS. La réponse suppose un chiffrage ; il est classé `calcul`.

Les autres exercices de nature `calcul` sont #10 (IS d'une SARL éligible au taux réduit), #21 (date du solde pour une clôture au 30 juin, délai à décompter) et #22 (montant d'un crédit d'impôt recherche). L'exercice #14 (seuil de chiffre d'affaires de la contribution exceptionnelle des grandes entreprises) est de nature `chiffre`.

Seuls les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus. Les 8 exercices de type `calc` du chapitre, tous de nature `calcul`, n'entrent pas dans ce classement.
