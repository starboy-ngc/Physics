# Cartes de notions : ue4-04 (L'impôt sur les sociétés)

*16 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-04.fiche.json`, et d'elle seule. Elles suivent le contrat (section 8) :
   - une question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : trois passes successives ont contrôlé les 35 cartes. Leur seul juge était le texte (`t` et `cite`) des items de la fiche. Elles ont vérifié que chaque carte dit ce que dit la fiche, sans rien y ajouter, et respecte la forme du contrat. Aucune recherche n'a été faite à ce stade.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a repris les 35 cartes sous quatre angles :
   - **Exactitude** : la carte est-elle juste au regard du droit en vigueur au 16 octobre 2026 (CGI, BOFiP, PCG modifié par le règlement ANC 2022-06) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne dit pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG, et la seule juste ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand une correction ajoute une précision, celle-ci reste dans le vocabulaire de la fiche. L'item de fiche en cause est alors signalé plus bas, et la fiche n'est pas modifiée.
4. **Recherches** : trois, le maximum permis, limitées à legifrance.gouv.fr, bofip.impots.gouv.fr, impots.gouv.fr et economie.gouv.fr (détail plus bas). Les autres points ont été tranchés sans recherche, à partir de la fiche et du texte connu des articles.

Validation : `node validate.js data/ue4/ue4-04.cartes.json` renvoie « ✓ data/ue4/ue4-04.cartes.json (cartes, 35 (7 déf.)) ». Toutes les questions comptent de 6 à 30 mots et toutes les réponses de 8 à 70 mots.

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k35, sans trou) |
| Définition (`def`) | 7 (k01, k03, k09, k12, k19, k29, k34) |
| Compréhension (`comp`) | 28 |
| Cartes corrigées par les relectures de fidélité | 8 (k13, k15, k19, k24, k31, k32, k33, k34) |
| Cartes corrigées par la relecture d'exactitude | 5 (k04, k13, k18, k20, k30) |
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

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k30 | « Une créance égale à l'IS acquitté sur le bénéfice ainsi absorbé » est inexact. La loi fixe la créance au produit du déficit reporté en arrière par le taux de l'IS **de l'exercice déficitaire**, et non à l'impôt réellement payé sur le bénéfice d'imputation. Les deux montants diffèrent dès que le taux a changé entre les deux exercices. Par ailleurs, en cas de procédure collective ou de conciliation, le remboursement anticipé n'est pas automatique : il doit être **demandé**, et il est opéré sous déduction d'un intérêt. | « **Une créance sur le Trésor, correspondant à l'excédent d'impôt antérieurement versé et évaluée aux taux de l'IS de l'exercice déficitaire** ; elle est utilisable pour payer l'IS des exercices clos au cours des cinq années suivantes et remboursée au terme de ce délai, ou par anticipation, sur demande, en cas de conciliation, de sauvegarde, de redressement ou de liquidation judiciaires. » Le pluriel « aux taux » couvre la part imposée au taux réduit. Aucun calcul n'est demandé. Base inchangée (Règles essentielles#11). | CGI, art. 220 quinquies, I ; BOI-IS-DEF-20-20 (recherche n° 1) |
| k20 | « Taxée au taux normal » est faux pour une PME éligible : la plus-value, comprise dans le résultat, profite du taux réduit de 15 % dans la limite du plafond de bénéfice. Le point avait déjà été relevé par la passe 2 de fidélité, sans correction de la carte. | « **Elle est comprise dans le résultat de l'exercice et imposée aux taux de droit commun de l'IS** (taux normal ou, dans sa limite, taux réduit des PME) : … ». La suite ne change pas. Chiffres et seuils#0 (taux de l'IS, item stable) devient la seconde base ; `src` et `url` restent ceux de Points de vigilance#1. | CGI, art. 219, I et I-b ; fiche, Chiffres et seuils#0 |
| k18 | À la question « À quelles conditions… », la réponse omettait une condition classique, attendue par un correcteur du DCG : la perte ou la charge provisionnée doit être **elle-même déductible**. Par exemple, une provision pour amende fiscale n'est pas déductible, même si la charge est probable et nettement précisée. | « … en vue de faire face à des pertes ou charges nettement précisées, **elles-mêmes déductibles**, que des événements en cours rendent probables… » (55 mots). Base inchangée (Règles essentielles#7). | CGI, art. 39, 1-5° ; BOI-BIC-PROV-20-10 (doctrine connue, non recherchée ici) |
| k13 | Les avances et prêts consentis aux associés ne sont considérés comme distribués que **sauf preuve contraire** : c'est une présomption simple, que la société peut renverser. Sans cette précision, la carte présente comme irréfragable une simple présomption. | « Les avances ou prêts consentis aux associés **(sauf preuve contraire)**, les rémunérations et avantages occultes, et la fraction des rémunérations jugée excessive. » La suite ne change pas. | CGI, art. 111, a (texte connu, non recherché ici) |
| k04 | La liste était présentée comme exhaustive. D'autres structures relèvent aussi du régime des sociétés de personnes : par exemple les groupements d'intérêt économique (art. 239 quater) et les sociétés de fait (art. 238 bis L). | La réponse commence par « **Notamment** aux commandités… ». Le reste ne change pas. | CGI, art. 8, 238 bis L et 239 quater (textes connus, non recherchés ici) |

**Cartes contrôlées et maintenues** (30 cartes sans changement) :

- **Taux réduit des PME (k24, k25, k26)** : la recherche n° 2 n'a trouvé aucune modification par la loi de finances pour 2026 du seuil de 10 millions d'euros ni du plafond de bénéfice. k26 énonce la règle d'adaptation de la limite à la durée de l'exercice sans rien faire calculer ; elle reste admise par le contrat.
- **Crédit d'impôt innovation (k35)** : la recherche n° 3 confirme que l'article 244 quater B, dans sa rédaction issue de la loi n° 2026-103 du 19 février 2026, fixe toujours le taux à 20 % pour les dépenses du k du II. Le dispositif n'a pas été supprimé.
- **Véhicules de tourisme (k17)** : la carte est exacte. L'exception des véhicules nécessaires à l'activité en raison même de son objet (taxis, auto-écoles, loueurs) n'est pas citée. C'est un cas marginal, et la carte ne devient pas fausse pour autant ; même choix que pour le chapitre ue4-03.
- **Régime mère-fille (k22, k23)** : les cartes sont exactes. La quote-part de 1 % vaut aussi pour certaines filiales établies dans l'Union européenne qui rempliraient les conditions de l'intégration si elles étaient françaises. k23 ne vise que le groupe intégré, ce qui est vrai, mais incomplet.
- **Charges réintégrées (k11, k13, k14)** : la rémunération excessive apparaît dans les trois cartes. Chacune interroge un angle distinct : la condition de déduction (k11), la liste de l'article 111 (k13), la double conséquence fiscale (k14). Aucune fusion n'est nécessaire.
- **Textes récents non recherchés (k16, k32)** : l'extension aux entreprises associées de la déduction au taux de marché (loi n° 2026-103, art. 14) et la réécriture de l'article 515-1 du PCG par le règlement ANC n° 2026-04 sont reprises de la fiche, qui cite le BOFiP et le texte du règlement. Le quota de recherche a été réservé aux points de droit plus douteux.
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

1. **CGI, art. 220 quinquies : montant de la créance de report en arrière** (domaines legifrance.gouv.fr et bofip.impots.gouv.fr).
   - Confirmé : la créance est égale au produit du déficit imputé en arrière par le taux de l'IS applicable à l'exercice déficitaire. Lorsque le bénéfice d'imputation a été imposé en partie au taux réduit des PME, le déficit s'impute d'abord sur la fraction imposée au taux normal (BOI-IS-DEF-20-20).
   - Confirmé aussi : en cas de conciliation, de sauvegarde, de redressement ou de liquidation judiciaires, l'entreprise **peut demander** le remboursement anticipé de la créance non utilisée, sous déduction d'un intérêt.
   - Conséquence : k30 est corrigée.
2. **Taux réduit de 15 % des PME et loi de finances pour 2026** (domaines bofip.impots.gouv.fr, impots.gouv.fr et legifrance.gouv.fr).
   - Aucune source officielle n'indique de modification du seuil de chiffre d'affaires de 10 millions d'euros ni du plafond de bénéfice. La position de l'administration après CE, 13 mars 2025, n° 481538, Sté TDA, est confirmée.
   - Conséquence : k24, k25 et k26 sont maintenues.
3. **Crédit d'impôt innovation et loi de finances pour 2026** (domaines bofip.impots.gouv.fr, legifrance.gouv.fr, economie.gouv.fr et impots.gouv.fr).
   - Confirmé : l'article 244 quater B, modifié par la loi n° 2026-103 du 19 février 2026, fixe toujours à 20 % le taux du crédit pour les dépenses mentionnées au k du II. La prorogation jusqu'au 31 décembre 2027 par la loi de finances pour 2025 est confirmée par ACTU-2025-00105.
   - Non établi : l'objet exact de la modification apportée à l'article par la loi de finances pour 2026 (art. 42). Rien n'indique qu'elle touche le taux ou le plafond.
   - Conséquence : k35 est maintenue.

## Points à reprendre dans la fiche

- **Règles essentielles#11 (report en arrière)** : « une créance égale à l'IS acquitté sur le bénéfice ainsi absorbé » est à remplacer. La créance est égale au produit du déficit reporté par le taux de l'IS **de l'exercice déficitaire** (art. 220 quinquies, I ; BOI-IS-DEF-20-20). Par ailleurs, « le remboursement est anticipé » est à remplacer par « l'entreprise peut demander le remboursement anticipé, sous déduction d'un intérêt ».
- **Points de vigilance#1 (plus-values des sociétés à l'IS)** : point déjà relevé par la passe 2 de fidélité. « Taxée au taux normal » est à remplacer par « taxée aux taux de droit commun de l'IS » : une PME éligible bénéficie du taux réduit sur la fraction de bénéfice qui y ouvre droit, plus-value comprise.
- **Règles essentielles#7 (provisions)** : il faut ajouter la condition selon laquelle la perte ou la charge provisionnée doit être **elle-même déductible** (BOI-BIC-PROV-20-10).
- **Définitions#3 (revenus distribués)** : les avances, prêts ou acomptes consentis aux associés ne sont réputés distribués que **sauf preuve contraire** (art. 111, a).
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

Seuls les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus. Les 8 exercices de type `calc` du chapitre, tous de nature `calcul`, n'entrent pas dans ce classement.
