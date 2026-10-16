# Cartes de notions : ue6-02 (Bilan fonctionnel, ratios et rentabilité)

*15 octobre 2026*

Fichier : `data/ue6/ue6-02.cartes.json`. Fiche de référence : `data/ue6/ue6-02.fiche.json`, mise à jour du 14 octobre 2026, non modifiée. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été écrites à partir de la seule fiche du chapitre. Elles suivent la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.

   Le jeu avait déjà connu un premier cycle de relecture, dont la version est enregistrée dans le dépôt. Ce cycle avait supprimé k19, k20 et k33. La présente reprise est partie de ces 30 cartes.
2. **Relecture de fidélité.** Un premier relecteur a comparé les 30 cartes à la fiche. Il en a corrigé deux (k09 et k21), sans rien supprimer ni ajouter.
3. **Relecture d'exactitude.** C'est la présente relecture, faite par un second relecteur indépendant. Il a contrôlé les 30 cartes sur quatre points :
   - **Exactitude** au 15 octobre 2026 : Code de commerce, Code monétaire et financier, CGI, PCG modifié par le règlement ANC n° 2022-06. La carte est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne précise pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse juste serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand l'item de fiche était lui-même en cause, la fiche n'a pas été modifiée. La carte a été corrigée pour rester exacte tout en restant portée par ses items de base, et l'item est signalé plus bas.
4. **Recherches.** Aucune recherche web n'a été faite (voir plus bas). Les numéros de comptes ont été contrôlés avec le plan comptable du dépôt (`data/pcg/classe1.json` et `data/pcg/classe5.json`).

Validation : `node validate.js data/ue6/ue6-02.cartes.json` renvoie « ✓ data/ue6/ue6-02.cartes.json (cartes, 30 (9 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées | 30 |
| Cartes au final | 30 |
| Définition (`def`) | 9 |
| Compréhension (`comp`) | 21 |
| Corrigées par la relecture de fidélité | 2 (k09, k21) |
| Corrigées par la relecture d'exactitude | 4 (k06, k08, k17, k22) |
| Supprimées | 0 |
| Ajoutées | 0 |
| Identifiants libres | k19, k20, k33 (pas de renumérotation) |

Chacun des huit items de la section « Définitions » a au moins une carte. Les « Règles essentielles » sont toutes couvertes, sauf la n° 11. Les six « Points de vigilance » ont chacun une carte.

**Items de la fiche sans carte**, tous écartés volontairement :

- **Règles essentielles#11 et Ce qui a changé récemment#3** : retraitements automatisés de la Banque de France. C'est une liste à apprendre par cœur, tirée d'une note méthodologique interne, qu'un correcteur du DCG n'attend pas. L'item #3 est en outre douteux (voir les points à reprendre).
- **Chiffres et seuils#2** : taux normal de l'IS, fixé par la loi de finances et donc susceptible de changer.
- **Chiffres et seuils#3** : repère Insee millésimé 2021.
- **Ce qui a changé récemment#2** : calendrier du programme, sans notion à retenir.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis s'arrête au milieu de sa liste de points de fiche (« La carte k17 ne cite aucun num… »). Les deux corrections de cartes, elles, sont complètes.

| Cible | Problème | Correction |
|---|---|---|
| k09 | La réponse disait « biens immobiliers à usage professionnel ». Or Définitions#5 dit seulement « biens immobiliers » : la précision vient de l'extérieur de la fiche (art. L. 313-7, 2°). Reprendre le texte de la fiche aurait rendu l'énumération trop large, donc fausse. | L'énumération des biens est retirée. Nouvelle réponse : « <b>Une opération de location</b> qui donne au locataire <b>la possibilité d'acquérir le bien loué</b> moyennant un prix convenu tenant compte des versements effectués à titre de loyers. Le bien n'est pas à l'actif du locataire. » Chaque phrase vient de Définitions#5. |
| k21 | La question « Comment la Banque de France exprime-t-elle les délais de paiement des clients et des fournisseurs ? » admettait une réponse juste mais incomplète (« en jours »). Elle pouvait aussi être confondue avec les délais légaux de l'art. L. 441-10, qui ont leur propre carte (k23). | Nouvelle question : « Selon la Banque de France, en jours de quelles grandeurs exprime-t-on les créances clients et les dettes fournisseurs ? ». La réponse, fidèle à Règles essentielles#9, est inchangée. |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k06 | La réponse rattachait le compte 519 à la fois aux concours bancaires courants et aux soldes créditeurs de banques. Le compte 519 est intitulé « Concours bancaires courants » ; un solde créditeur de banque (découvert) est le solde créditeur du compte 512 lui-même. | La parenthèse est déplacée : « … diminuée de la trésorerie passive : concours bancaires courants (compte 519) et soldes créditeurs de banques, auxquels le bilan fonctionnel ajoute les effets escomptés non échus. » Rien d'autre ne change. | Plan comptable du dépôt, `classe5.json` (512, 519, 5191, 5193, 5198) ; fiche : Définitions#4 |
| k08 | Même confusion dans la question : « les concours bancaires courants et soldes créditeurs de banques (compte 519) ». | Nouvelle question : « Où le bilan fonctionnel classe-t-il les concours bancaires courants (compte 519) et les soldes créditeurs de banques ? ». La réponse (en trésorerie passive, hors dettes financières) est inchangée. | Plan comptable du dépôt, `classe5.json` ; fiche : Règles essentielles#2 |
| k17 | La question portait aussi sur les intérêts courus à payer sur concours bancaires. Ces intérêts sont enregistrés au compte 5198, sous-compte du 519 « Concours bancaires courants », et présentés avec ces concours. Les classer en dettes hors exploitation, alors que les concours eux-mêmes vont en trésorerie passive, n'est pas une règle établie : c'est un choix d'analyse discuté (contrat, §3.4). Seul le reclassement des intérêts courus non échus sur emprunts en dettes hors exploitation est la règle usuelle. | Question resserrée : « Comment le bilan fonctionnel classe-t-il les intérêts courus non échus sur emprunts ? ». La réponse (retirés des dettes financières, où les range le bilan comptable, et classés en dettes hors exploitation) est inchangée et reste portée par Règles essentielles#8. | Plan comptable du dépôt, `classe5.json` (518, 5181, 519, 5198) et `classe1.json` (1648, 1688) ; contrat, §3.4 |
| k22 | La question « que faut-il vérifier sur ses deux termes ? » admettait d'autres réponses justes : même période de référence, réintégration des effets escomptés non échus dans les créances, choix des postes retenus. La réponse attendue (même base TTC ou HT) n'était donc pas la seule défendable. La seconde phrase reprenait en outre la question. | Nouvelle question : « Avant de convertir en jours un ratio de rotation clients ou fournisseurs, que faut-il vérifier quant à la TVA dans son numérateur et son dénominateur ? ». Nouvelle réponse : « <b>Qu'ils sont exprimés sur la même base, TTC ou HT.</b> C'est la règle d'homogénéité des ratios de rotation, à respecter à l'examen avant toute conversion en jours. » | Fiche : Points de vigilance#2 |

**Cartes contrôlées et maintenues sans changement** : k01 à k05, k07, k09 à k16, k18, k21, k23 à k32. Points examinés :

- **k09** (version issue de la relecture de fidélité) : exacte. Elle ne reprend pas la liste des biens ni la mention « au moins pour partie » de l'art. L. 313-7, mais elle n'affirme rien de faux et contient l'élément que le correcteur attend (location assortie d'une faculté d'achat tenant compte des loyers).
- **k15 et k16** : la fraction minimale (moitié à la constitution, quart lors d'une augmentation de capital) est bien délimitée à la valeur nominale des actions de numéraire (C. com., art. L. 225-3 et L. 225-144). Le délai de cinq ans pour le surplus est exact.
- **k18** : le compte 1648 pour les intérêts courus sur emprunts bancaires et le maintien du 1688 pour les autres emprunts et dettes assimilées sont conformes au plan comptable du dépôt et au contrat (§6).
- **k23** : la règle générale de l'art. L. 441-10 (trente jours à défaut de clause, plafond de soixante jours après l'émission de la facture ou de quarante-cinq jours fin de mois) est exacte. La question écarte les délais propres à certains secteurs (art. L. 441-11).
- **k26** : la carte dit « net de l'impôt sur les sociétés » sans citer de taux. Elle reste donc vraie quel que soit le taux applicable, taux réduit des PME compris.
- **k27** : la limitation aux immobilisations incorporelles et corporelles (657 et 757) est exacte ; les cessions d'immobilisations financières relèvent du résultat financier (667 et 767).
- **k29 et k31** : conformes aux art. L. 631-1 et L. 232-11 du Code de commerce.

**Doublons examinés et conservés**, chaque carte interrogeant un angle distinct :

- k06, k08 et k12 : définition de la trésorerie nette, classement des concours bancaires hors des dettes financières, double retraitement des effets escomptés non échus ;
- k15 et k16 : raison de la déduction du compte 109, puis fractions minimales de libération ;
- k02 et k32 : définition du bilan fonctionnel, puis opposition avec le bilan financier ;
- k29 et k30 : définition légale de la cessation des paiements, puis cas de l'entreprise bénéficiaire.

## Recherches faites

Aucune recherche web, sur les trois autorisées. Aucun point ne laissait de doute réel :

- les numéros et intitulés de comptes ont été vérifiés dans le plan comptable du dépôt (`data/pcg/`) ;
- les textes en cause (C. mon. fin., art. L. 313-7 ; C. com., art. L. 225-3, L. 225-144, L. 232-11, L. 441-10 et L. 631-1 ; CGI, art. 219) n'ont pas été modifiés sur les points que portent les cartes ;
- le maintien d'un chapitre « Tableau de financement » dans le PCG au 1er janvier 2025 avait déjà été vérifié par recherche sur anc.gouv.fr lors du cycle de relecture précédent.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Les points 1 à 6 reprennent ceux de la relecture de fidélité, complétés ; les points 7 à 9 viennent de la relecture d'exactitude.

1. **Définitions#5 (crédit-bail).** L'art. L. 313-7, 2°, ne vise que les biens immobiliers **à usage professionnel**. Le texte précise aussi que les biens sont achetés en vue de la location par une entreprise qui « en demeure propriétaire », et que le prix tient compte « au moins pour partie » des loyers versés. À compléter ; la carte k09 ne cite plus la liste des biens en attendant.
2. **Définitions#4 (trésorerie nette).** Trois corrections :
   - la trésorerie active y est réduite aux disponibilités, sans les valeurs mobilières de placement ;
   - l'item ne parle pas des effets escomptés non échus, que Règles essentielles#4 ajoute à la trésorerie passive ;
   - le compte 519 y est rattaché aux soldes créditeurs de banques, alors qu'il ne recouvre que les concours bancaires courants (un découvert est le solde créditeur du 512).
3. **Définitions#3.** Sous le titre « Besoin en fonds de roulement », l'item range la variation « trésorerie » parmi les variations du BFR. Il faudrait la présenter à part, comme le fait Règles essentielles#0.
4. **Ce qui a changé récemment#1.** « Les cessions d'immobilisations passent en exploitation » doit être limité aux immobilisations incorporelles et corporelles (657 et 757). Les cessions d'immobilisations financières relèvent du résultat financier (667 et 767), comme le dit le contrat (§4).
5. **Règles essentielles#8.** Deux problèmes :
   - le compte 5186 n'existe pas dans le plan de comptes : les intérêts courus à payer vont en 5181, ceux des concours bancaires courants en 5198 (la liste des `textes` de la fiche cite aussi 5186) ;
   - le classement des intérêts courus sur concours bancaires en dettes hors exploitation n'est pas une règle établie, puisque ces intérêts sont un sous-compte du 519, classé en trésorerie passive. Mieux vaut limiter l'item aux intérêts courus non échus sur emprunts.
6. **Ce qui a changé récemment#3.** Rien n'établit le « depuis 2025 » : la date d'édition de la note (avril 2025) ne prouve pas que les retraitements datent de 2025. L'item n'a pas d'URL, répète Règles essentielles#11 et décrit mal la procédure (« groupes à tête française »). À vérifier ou à retirer.
7. **Règles essentielles#2.** Même rattachement inexact du compte 519 aux soldes créditeurs de banques qu'en Définitions#4.
8. **Règles essentielles#14 et Chiffres et seuils#2.** Le taux de l'IS de 25 % est fixé par la loi de finances : ces items devraient être marqués millésimés, et non `stable`. La formule (1 − 0,25) ne vaut qu'au taux normal, pas pour la fraction de bénéfice imposée au taux réduit des PME (CGI, art. 219, I). À reformuler sans taux dans les Règles essentielles.
9. **Règles essentielles#7 et Chiffres et seuils#1.** Deux corrections :
   - les fractions minimales (moitié, quart) portent sur la **valeur nominale** des actions de numéraire ; lors d'une augmentation de capital, la prime d'émission est libérée en totalité à la souscription (C. com., art. L. 225-144) ;
   - le « surplus » à libérer dans les cinq ans y est assimilé au compte 109, alors que la part appelée et non versée relève du compte 4562.

## Classement des exercices

Un classement automatique a porté sur les 18 exercices du chapitre de type QCM, QCM multiple et classement :

| Nature | Nombre |
|---|---|
| notion | 13 |
| calcul | 5 |
| chiffre | 0 |

**Désaccord tranché.** L'exercice **#22** (« Une entreprise a une rentabilité économique de 5 % et emprunte à 7 %. Quel est l'effet de l'endettement sur sa rentabilité financière ? ») a été classé notion par un classement et calcul par l'autre. Il est retenu en **calcul** et sort donc des révisions espacées. La notion qu'il illustre (le levier n'est favorable que si la rentabilité économique dépasse le taux de la dette) reste révisée par la carte k26.

Les 13 exercices de nature notion entrent dans les révisions espacées, avec les 30 cartes.
