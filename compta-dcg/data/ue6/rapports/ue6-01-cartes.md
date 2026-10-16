# Cartes de notions : ue6-01 (Lire les comptes : SIG, CAF et retraitements)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue6/ue6-01.fiche.json` et d'elle seule. Elles respectent le contrat (section 8) : une question par carte, aucun calcul, aucun chiffre millésimé, et chaque carte s'appuie sur un ou deux items de fiche (`base`) dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : un premier relecteur a contrôlé que chaque carte dit ce que dit la fiche, sans plus, et qu'elle respecte la forme exigée par le contrat.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a vérifié les points suivants :
   - **Exactitude** : chaque carte est-elle juste au regard du droit et des normes en vigueur au 15 octobre 2026 (Code de commerce, PCG modifié par le règlement ANC n° 2022-06) ?
   - **Ambiguïté** : la réponse attendue est-elle la seule réponse juste possible ?
   - **Doublons et cartes triviales.**
   - **Absence de calcul et de chiffre millésimé.**
4. **Recherches** : 3 recherches limitées au site anc.gouv.fr (détail plus bas). Il n'a pas été possible de télécharger directement les PDF de l'ANC (échec de la résolution DNS).

Validation : `node validate.js data/ue6/ue6-01.cartes.json` renvoie ✓ (35 cartes, dont 13 de définition).

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k35, sans trou) |
| Définition (`def`) | 13 |
| Compréhension (`comp`) | 22 |
| Cartes supprimées | 0 |
| Cartes ajoutées | 1 (k35, ajoutée par la relecture de fidélité) |

**Items de la fiche sans carte**, tous écartés volontairement :

- **Chiffres et seuils #0 à #4** : taux d'IS, taux réduit des PME, seuil de participation, repère Insee 2021 et modalités de l'épreuve. Ce sont des chiffres millésimés ou des données sans lien avec une notion du chapitre.
- **Ce qui a changé récemment #2 à #5** : programme 2025, arrêt CE *Sté TDA*, contribution exceptionnelle sur les bénéfices et loi de finances pour 2026. Ces items sont millésimés ou hors du sujet SIG/CAF.
- **Points de vigilance #5** : lien avec le DSCG, ce n'est pas une notion.

Les huit items de la section « Définitions » ont chacun au moins une carte.

## Corrections de la première relecture (fidélité)

| Cible | Problème | Correction |
|---|---|---|
| k11 | La question en posait deux (« De quels éléments l'EBE est-il indépendant, et pourquoi ? »). | Nouvelle question unique : « De quels éléments l'excédent brut d'exploitation (EBE) est-il indépendant, du fait de sa place dans la cascade des soldes intermédiaires de gestion ? ». La réponse est inchangée (Définitions#3, Règles essentielles#3). |
| k14 | Typée « comp », la carte posait en fait une question de définition. La réponse reprenait le point de vigilance déjà écrit dans la question. | Elle devient une vraie question de distinction : « Selon l'Insee, à quoi l'EBE est-il rapporté pour mesurer d'une part le taux de marge, d'autre part la rentabilité économique ? ». Réponse : la valeur ajoutée pour l'un ; les immobilisations brutes corporelles et incorporelles plus le BFR pour l'autre. Base : Points de vigilance#1 et Définitions#4. |
| k16 | Question ambiguë : la ligne « plus-values et moins-values sur cessions » du tableau des SIG ou le résultat courant avant impôts étaient aussi des réponses justes. | Le choix est délimité : « Depuis le PCG 2025, à quel niveau de résultat (exploitation, financier ou exceptionnel) appartient la plus ou moins-value de cession d'une immobilisation corporelle ? ». |
| k22 | La seconde phrase (« produits encaissables et charges décaissables ») ne reposait pas sur Règles essentielles#7 seul. | Définitions#6 est ajouté en second item de base. |
| k33 | La règle générale de l'Insee était appliquée au chiffre d'affaires d'une entreprise. | Nouvelle question : « Selon l'Insee, en quoi se décompose une évolution en valeur, comme celle du chiffre d'affaires ? ». |
| k35 (ajout) | La règle essentielle #14 (partage de la valeur ajoutée, au programme de l'UE6) n'avait pas de carte propre : k12 ne reprend que le taux de marge. | Carte « def » ajoutée : « Dans le partage de la valeur ajoutée selon l'Insee, que comprend la rémunération des salariés ? ». |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k18 | « Depuis le PCG 2025, il **ne comprend plus que** les charges et produits d'un événement majeur et inhabituel et les écritures d'origine purement fiscale » : c'est inexact. L'article 513-5 du PCG, issu du règlement 2022-06, classe aussi en résultat exceptionnel les changements de méthode comptabilisés en résultat en application de règles fiscales et les corrections d'erreurs (sauf celles d'une écriture imputée en capitaux propres). | La phrase devient « il comprend **notamment** les charges et produits découlant d'un événement majeur et inhabituel, ainsi que les écritures d'origine purement fiscale ». | Règlement ANC n° 2022-06 et sa version commentée (recherche n° 2) ; plan de comptes du dépôt (comptes 67/678 et 77/778, comptes transitoires 672/772) |
| k22 | La liste des éléments exclus par la méthode soustractive était incomplète. Le modèle du PCG écarte aussi la quote-part des subventions d'investissement virée au résultat (747), qui est un produit non encaissable. | La réponse ajoute « comme tout produit non encaissable ou charge non décaissable », ce qui reste dans le champ de Définitions#6. | PCG, modèle de tableau de la CAF ; fiche Définitions#6 et Règles essentielles#8 |
| k28 | « Part du **bénéfice** distribuable » est trop étroit. L'article L. 232-12 vise les **sommes distribuables**, qui peuvent comprendre des réserves dont l'assemblée a la disposition (L. 232-11, al. 2). | Nouvelle réponse : « La part des sommes distribuables, notamment du bénéfice distribuable, que l'assemblée générale attribue aux associés, après approbation des comptes annuels ». | C. com., art. L. 232-11 et L. 232-12 |
| k11 | « Indépendant du financement » n'est vrai que pour les charges financières. Les redevances de crédit-bail, classées en charges externes, pèsent sur la VA et l'EBE ; c'est d'ailleurs ce que la Banque de France retraite (k31). | La réponse précise « du financement (charges financières) ». | Fiche Règles essentielles#3 et #10 |
| k13 | La question « Avec quels ratios des manuels… » admettait d'autres réponses justes, par exemple le taux de marge nette. | Question délimitée : « Dans les sujets de DCG, quels deux « taux de marge » ne faut-il pas confondre avec le taux de marge de l'Insee ? ». | Fiche Définitions#4, Points de vigilance#0 |
| k19 | La carte était presque tautologique : la question disait « liés à un événement », la réponse « ceux qui en découlent directement ». | La carte interroge désormais le critère : « …à quel critère reconnaît-on qu'une charge ou un produit découle directement d'un événement majeur et inhabituel ? ». Réponse : il n'aurait pas été constaté en l'absence de cet événement. | Fiche Règles essentielles#5 |
| k21 | La définition était purement procédurale (« un solde déterminé à partir de l'EBE »). Un correcteur du DCG attend la nature de la CAF. | Nouvelle réponse : « Un surplus monétaire potentiel : produits encaissables moins charges décaissables, hors cessions d'immobilisations », puis le mode de détermination et de vérification du PCG. Points de vigilance#4 est ajouté en base (`src` et `url` inchangés). | Fiche Définitions#6, Points de vigilance#4 |
| k34 | Question ouverte (« Quelles modifications… changent la construction des SIG et de la CAF ? ») : la suppression des transferts de charges (791, 796, 797) par le même règlement était aussi une réponse juste. | La question est délimitée aux trois changements qui déplacent des charges ou des produits du résultat exceptionnel vers l'exploitation. Règles essentielles#6 (747, produit d'exploitation) est ajouté en base. | Fiche Ce qui a changé récemment#0, Règles essentielles#6 ; règlement ANC n° 2022-06 |

Aucune carte n'a été supprimée ni ajoutée lors de cette relecture. Les doublons partiels (k05/k06, k15/k16/k26, k24/k25) sont conservés car chaque carte interroge un angle distinct : ordre de la cascade, comptes, niveau de résultat, neutralisation dans la CAF, ajouts et retranchements.

## Recherches faites

1. **Le tableau des SIG, de la CAF et le tableau de financement dans le règlement 2022-06** (domaine anc.gouv.fr).
   - Confirmé : le tableau de financement est maintenu dans le titre IX « Autres documents », obligatoire pour les entités visées par les articles L. 232-2 et L. 612-2 du Code de commerce. La mention de k30 reste donc exacte.
   - Non confirmé : le maintien des modèles de tableau des SIG et de la CAF dans le PCG 2025.
2. **Le contenu du résultat exceptionnel selon le règlement 2022-06** (domaine anc.gouv.fr).
   - L'article 513-5 du PCG retient trois catégories : les charges et produits directement liés à un événement majeur et inhabituel ; les écritures d'origine purement fiscale ; les changements de méthode comptabilisés en résultat à cause de règles fiscales et les corrections d'erreurs, sauf celles qui corrigent une écriture imputée en capitaux propres.
   - Est confirmée la présomption d'événement inhabituel (k20) : l'événement ne s'est pas produit récemment et il est peu probable qu'il se reproduise.
   - Ces résultats ont conduit à corriger k18.
3. **Les articles du PCG au 1er janvier 2025 relatifs aux modèles de SIG et de CAF** (domaine anc.gouv.fr).
   - Recherche non concluante : l'article correspondant n'a pas été trouvé. Une réponse à une consultation de l'ANC évoque une demande de clarification de la définition des SIG et de la CAF.
   - Les cartes sur les SIG et la CAF sont maintenues, car elles reprennent les notions enseignées au DCG. La référence de la fiche au « modèle de tableau du PCG » reste à vérifier sur le recueil.

## Points à reprendre dans la fiche

- **Définitions#5 et Règles essentielles#5** : les formules « ne comprend que » et « ne retient que » (événement majeur et inhabituel, écritures d'origine purement fiscale) sont incomplètes.
  - L'article 513-5 du PCG range aussi en résultat exceptionnel les changements de méthode comptabilisés en résultat pour des raisons fiscales et les corrections d'erreurs, sauf celles d'écritures imputées en capitaux propres.
  - La référence « PCG, art. 512-4 » est probablement à remplacer par « PCG, art. 513-5 », à vérifier sur le recueil.
- **Définitions#7** : le dividende y est défini comme la « part du bénéfice distribuable ». L'article L. 232-12 du Code de commerce vise les « sommes distribuables », et l'assemblée peut distribuer des réserves (L. 232-11, al. 2).
- **Règles essentielles#7** : la liste des éléments exclus de la CAF soustractive omet la quote-part des subventions d'investissement virée au résultat (747).
- **Définitions#3 et Règles essentielles#3** : l'indépendance de l'EBE à l'égard du financement est à nuancer pour le crédit-bail, dont les redevances sont en charges externes. Il faudrait renvoyer au retraitement de Règles essentielles#10.
- **À vérifier** : la présence, dans le PCG 2025, des modèles de tableau des soldes intermédiaires de gestion et de détermination de la CAF, que citent plusieurs items comme source.

## Classement des exercices

Classement automatique des exercices QCM, QCM multiples et classements (tri) du chapitre selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 12 |
| `calcul` (montant, taux, prorata, délai) | 4 |
| `chiffre` (rappel d'un chiffre millésimé) | 0 |
| **Total** | 16 |

Aucun désaccord n'a été relevé. Seuls les 12 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
