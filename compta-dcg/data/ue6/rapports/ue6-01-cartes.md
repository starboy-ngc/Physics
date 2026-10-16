# Cartes de notions : ue6-01 (Lire les comptes : SIG, CAF et retraitements)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche.** Les cartes sont écrites à partir de la seule fiche documentaire `data/ue6/ue6-01.fiche.json`. Elles suivent la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité.** Un premier relecteur a vérifié que chaque carte dit ce que dit la fiche, sans rien ajouter, et qu'elle respecte la forme exigée.
3. **Relecture d'exactitude** (la présente relecture). Un second relecteur, indépendant, a contrôlé chaque carte sur quatre points :
   - **Exactitude** : la carte est-elle juste au regard du droit et des normes en vigueur au 15 octobre 2026 (Code de commerce, Code du travail, PCG modifié par le règlement ANC n° 2022-06) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne précise pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse, juste, serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Aucun calcul, aucun chiffre millésimé.**

   Quand l'item de fiche lui-même est en cause, la fiche n'est pas modifiée. La carte est corrigée pour rester à la fois exacte et portée par ses items de base, et l'item est signalé plus bas.
4. **Recherches.** Trois recherches ont été faites, limitées au site anc.gouv.fr (détail plus bas). Le téléchargement direct du PCG au format PDF a été refusé par le proxy réseau.

Validation : `node validate.js data/ue6/ue6-01.cartes.json` renvoie « ✓ (cartes, 35 (13 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées | 35 |
| Cartes au final | 35 (k01 à k35, sans trou) |
| Définition (`def`) | 13 |
| Compréhension (`comp`) | 22 |
| Corrigées par la relecture d'exactitude | 6 (k10, k11, k18, k22, k28, k34), dont k10 pour sa seule base |
| Supprimées | 0 |
| Ajoutées | 0 |

Les huit items de la section « Définitions » ont chacun au moins une carte. Les seize « Règles essentielles » sont toutes couvertes : Règles essentielles#3 est désormais portée par k10.

**Items de la fiche sans carte**, tous écartés volontairement :

- **Chiffres et seuils #0 à #4** (taux d'IS, taux réduit des PME, seuil de participation, repère Insee 2021, modalités de l'épreuve). Ce sont des chiffres millésimés ou des données sans notion à retenir. La règle du seuil de cinquante salariés est déjà traitée par Règles essentielles#12.
- **Ce qui a changé récemment #2 à #5** (programme 2025, arrêt CE *Sté TDA*, contribution exceptionnelle sur les bénéfices, loi de finances pour 2026). Ces items sont millésimés ou étrangers aux SIG et à la CAF.
- **Points de vigilance #5** (lien avec le DSCG). Ce n'est pas une notion.

**Doublons examinés et conservés**, chaque carte interrogeant un angle distinct :

- k05 et k06 : début et fin de la cascade des SIG ;
- k15, k16 et k26 : comptes utilisés, catégorie de résultat, neutralisation dans la CAF ;
- k24 et k25 : ce qu'on ajoute et ce qu'on retranche dans la méthode additive ;
- k12 et k14 : définition du taux de marge, puis distinction avec la rentabilité économique.

k34 fait la synthèse de k15 à k18. Elle est gardée parce qu'elle est la seule carte fondée sur Ce qui a changé récemment#0.

## Corrections de la première relecture (fidélité)

Le résultat transmis s'arrête au milieu de la ligne k34. Les lignes k11 et k14 ont été reconstituées à partir des différences du fichier avec la version précédente.

| Cible | Problème | Correction |
|---|---|---|
| k18 | La réponse disait que le résultat exceptionnel « comprend notamment » les charges et produits d'un événement majeur et inhabituel. La fiche (Définitions#5) écrit « ne comprend que » : la carte faisait d'une liste limitative une liste ouverte. | La réponse devient « il ne comprend que les charges et produits découlant d'un événement majeur et inhabituel, ainsi que les écritures d'origine purement fiscale », avec « de l'entreprise » ajouté comme dans la fiche. |
| k22 | L'ajout « comme tout produit non encaissable ou charge non décaissable » ne figure pas dans la fiche. Il est en outre faux, car il range les produits des cessions parmi les produits non encaissables, alors que la fiche les exclut au titre de « hors cessions d'immobilisations ». | Nouvelle réponse : « Les dotations, les reprises, les produits des cessions et les valeurs comptables des éléments cédés. Partant de l'excédent brut d'exploitation, la CAF se détermine par différence entre produits encaissables et charges décaissables, hors cessions d'immobilisations. » (Règles essentielles#7 et Définitions#6) |
| k28 | La réponse ajoutait « sommes distribuables, notamment du bénéfice distribuable » et « comptes annuels », absents de la fiche. La question parlait de « société commerciale », ce que la fiche ne dit pas. | Question : « Selon l'article L. 232-12 du Code de commerce, qu'est-ce qu'un dividende ? ». Réponse alignée sur Définitions#7 : « La part du bénéfice distribuable attribuée aux associés par l'assemblée générale, après approbation des comptes. » |
| k16 | La question donnait les choix (exploitation, financier ou exceptionnel), donc contenait la réponse : c'était un QCM déguisé. Une version intermédiaire, « d'une immobilisation » sans précision, aurait englobé les immobilisations financières. Or la fiche les fait passer par 6671 et 7671, et la règle 657/757 ne vise que les immobilisations incorporelles et corporelles. | Question : « Depuis le PCG 2025, dans quelle catégorie de charges et de produits du compte de résultat classe-t-on la plus ou moins-value de cession d'une immobilisation incorporelle ou corporelle ? ». Réponse : « En exploitation : elle fait partie du résultat d'exploitation (comptes 657 et 757). » Le rappel des sujets antérieurs à 2025 (675/775, résultat exceptionnel) est conservé. |
| k34 | La question affirmait que les trois changements du règlement 2022-06 « déplacent des charges ou des produits du résultat exceptionnel vers l'exploitation ». La fiche ne dit pas où vont les éléments qui sortent du résultat exceptionnel du fait de sa nouvelle définition. | Question : « Quels sont les trois changements du règlement ANC n° 2022-06 qui modifient le calcul des soldes intermédiaires de gestion et de la CAF ? ». La réponse reprend les termes de la fiche (Ce qui a changé récemment#0). |
| k11 | « (charges financières) » et « du fait de sa place dans la cascade » n'étaient pas dans la fiche *(reconstitué)*. | Question : « De quels éléments l'excédent brut d'exploitation (EBE) d'une entreprise est-il indépendant ? ». La réponse reprend Définitions#3 et Règles essentielles#3. |
| k14 | Le connecteur « donc » présentait comme une conséquence ce que la fiche pose comme un constat distinct *(reconstitué)*. | Suppression de « donc ». |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k18 | La réponse « il **ne comprend que** » deux catégories (événement majeur et inhabituel, écritures d'origine purement fiscale) est inexacte. L'article 513-5 du PCG, issu du règlement 2022-06, classe aussi en résultat exceptionnel les changements de méthode comptabilisés en résultat pour des raisons fiscales et certaines corrections d'erreurs. Le retour à « notamment » avait été refusé à juste titre, parce qu'il ouvre une liste que la fiche ferme. | La réponse devient « Depuis le PCG 2025, il est **recentré sur** les charges et produits découlant d'un événement majeur et inhabituel et sur les écritures d'origine purement fiscale ». Elle n'affirme plus que la liste est limitative et n'ajoute rien qui soit absent de Définitions#5. | Recherche n° 1 (règlement ANC n° 2022-06, version commentée ; PCG au 1er janvier 2025, art. 513-5) |
| k11 | « L'EBE est indépendant du financement » n'est vrai que pour les charges financières. Les charges de crédit-bail, comptées dans les autres achats et charges externes, réduisent la valeur ajoutée et l'EBE du tableau du PCG. C'est précisément la raison du retraitement de la Banque de France. La carte était donc vraie seulement dans un cas qu'elle ne précisait pas. | La réponse attendue reste la même (amortissement, financement, impôt sur les bénéfices). Elle est complétée par : « Réserve : les charges de crédit-bail, comptées dans les autres achats et charges externes du tableau du PCG, pèsent sur l'EBE ; la méthode de la Banque de France les retraite. » La base devient Définitions#3 et Règles essentielles#10 ; `src` et `url` sont inchangés. | Fiche : Définitions#3, Règles essentielles#10 |
| k10 | Ce n'est pas une erreur. Comme Règles essentielles#3 n'est plus en base de k11, il fallait qu'elle reste portée par une carte. | Règles essentielles#3, qui contient la même formule de l'EBE, est ajoutée en second item de base. Le texte est inchangé. | Fiche : Règles essentielles#3 |
| k22 | La question « Quels éléments la méthode soustractive exclut-elle ? » appelle une liste complète. Or la quote-part des subventions d'investissement virée au résultat (747) est aussi écartée, puisque c'est un produit non encaissable que la méthode additive retranche (Règles essentielles#8). Un correcteur du DCG l'attendrait dans la liste. La fiche ne l'indique pas pour la méthode soustractive, et la relecture de fidélité avait refusé de l'ajouter. | La question est délimitée : « …quels éléments liés aux amortissements, dépréciations, provisions et cessions d'immobilisations sont exclus ? ». Dans ce champ, la liste de la fiche est complète. Réponse : dotations et reprises, produits des cessions et valeurs comptables des éléments cédés. | PCG, modèle de tableau de la CAF ; fiche : Règles essentielles#7 et #8 |
| k28 | La question attribuait à l'article L. 232-12 la formule « part du **bénéfice** distribuable ». Ce texte vise les « **sommes** distribuables » : « Après approbation des comptes annuels et constatation de l'existence de sommes distribuables, l'assemblée générale détermine la part attribuée aux associés sous forme de dividende ». Ces sommes peuvent comprendre des réserves dont l'assemblée a la disposition (L. 232-11, al. 2). | Question : « En droit des sociétés, qu'est-ce qu'un dividende ? ». La réponse de la fiche est conservée : c'est la définition usuelle des manuels, mais elle n'est plus présentée comme la lettre de l'article. L'item de fiche est signalé. | C. com., art. L. 232-11 et L. 232-12 |
| k34 | « Les trois changements… qui modifient le calcul des SIG et de la CAF » laisse croire qu'il n'y en a que trois. Le règlement 2022-06 supprime aussi les comptes de transferts de charges (79), ce qui modifie lui aussi le modèle de CAF soustractive. La formule « cessions d'immobilisations en exploitation » laissait par ailleurs penser que les immobilisations financières suivent la même règle, alors qu'elles passent par 6671 et 7671. | Question : « Quels sont les trois changements de classement des charges et produits, issus du règlement ANC n° 2022-06, qui modifient les soldes intermédiaires de gestion et la CAF ? ». Réponse : nouvelle définition du résultat exceptionnel ; passage en exploitation des cessions d'immobilisations **incorporelles et corporelles** (657 / 757) ; quote-part de subvention en 747. La base devient Ce qui a changé récemment#0 et Règles essentielles#4. | Fiche : Ce qui a changé récemment#0, Règles essentielles#4 ; règlement ANC n° 2022-06 |

**Cartes contrôlées et maintenues sans changement**

- k04 (définition du chiffre d'affaires). Le règlement ANC n° 2026-03 (recherche n° 3) déplace cette définition à l'article 521-3 pour les exercices ouverts à compter du 1er janvier 2027. Il en garde la substance (« affaires réalisées par l'entité avec les tiers dans le cadre de son activité normale et courante »), donc la carte reste juste aujourd'hui comme demain.
- k19 et k20 (critère de l'événement majeur et inhabituel, présomption d'événement inhabituel). Leur contenu est confirmé par la recherche n° 1.

## Recherches faites

1. **Contenu du résultat exceptionnel selon le règlement ANC n° 2022-06** (domaine anc.gouv.fr).
   - **Confirmé.** L'article 513-5 du PCG classe en résultat exceptionnel les produits et charges directement liés à un événement majeur et inhabituel, ainsi que les écritures d'origine purement fiscale.
   - **Confirmé aussi.** La version consolidée au 1er janvier 2025 y ajoute les changements de méthode passés en résultat en raison de règles fiscales et certaines corrections d'erreurs.
   - **Confirmés également** : la présomption d'événement inhabituel (« ne s'est pas produit au cours des derniers exercices et peu probable qu'il se reproduise ») et la notion d'événement majeur.
   - **Conséquence** : correction de k18 ; k19 et k20 sont maintenues.
2. **Les tableaux des SIG et de la CAF dans le PCG 2025** (titre IX « Autres documents », domaine anc.gouv.fr).
   - **Confirmé.** Le titre IX existe dans les versions 2025 et 2026 du PCG, et son chapitre I est le tableau de financement. La mention de k30 reste donc juste.
   - **Non confirmé.** Le maintien, dans ce titre, des modèles de tableau des SIG et de détermination de la CAF n'a pas pu être vérifié. Le téléchargement du PDF a été refusé par le proxy.
   - **Conséquence** : les cartes sur les SIG et la CAF sont maintenues, car elles reprennent les notions enseignées au DCG. Le point est signalé plus bas.
3. **Règlement ANC n° 2026-03 du 6 mars 2026** (comptabilisation des produits des ventes, domaine anc.gouv.fr).
   - **Confirmé.** Le règlement est homologué. Il s'applique aux exercices ouverts à compter du 1er janvier 2027, avec application anticipée possible.
   - **Confirmé aussi.** La définition du chiffre d'affaires passe à l'article 521-3, en substance inchangée.
   - **Non résolu.** Les dates de publication au Journal officiel divergent selon les sources (3 juin ou 3 septembre 2026).
   - **Conséquence** : k04 est maintenue ; l'item de fiche est signalé.

## Points à reprendre dans la fiche

- **Définitions#5 et Règles essentielles#5.** Les formules « ne comprend que » et « ne retient que » (événement majeur et inhabituel, écritures d'origine purement fiscale) sont incomplètes.
  - L'article 513-5 du PCG range aussi en résultat exceptionnel les changements de méthode comptabilisés en résultat pour des raisons fiscales et certaines corrections d'erreurs.
  - La référence « PCG, art. 512-4 » est à remplacer par « PCG, art. 513-5 ».
- **Définitions#7.** Le dividende y est défini comme la « part du bénéfice distribuable », avec l'article L. 232-12 pour source. Or ce texte vise les « sommes distribuables », et l'assemblée peut distribuer des réserves dont elle a la disposition (L. 232-11, al. 2).
- **Règles essentielles#7.** La liste des éléments exclus de la CAF soustractive omet la quote-part des subventions d'investissement virée au résultat (747). La méthode additive de Règles essentielles#8 la retranche pourtant : les deux items ne sont pas cohérents.
- **Définitions#3 et Règles essentielles#3.** L'indépendance de l'EBE à l'égard du financement est à nuancer pour le crédit-bail, dont les charges figurent dans les charges externes. Il faudrait renvoyer à Règles essentielles#10.
- **Ce qui a changé récemment#0.** Les trois changements cités ne sont pas les seuls qui touchent les SIG et la CAF. Le règlement 2022-06 supprime aussi les comptes de transferts de charges (79). Il faudrait le mentionner, ou écrire « notamment ».
- **Ce qui a changé récemment (item à ajouter) et Définitions#1.**
  - Le règlement ANC n° 2026-03 du 6 mars 2026 (produits des ventes) est homologué et s'applique aux exercices ouverts à compter du 1er janvier 2027.
  - La définition du chiffre d'affaires passe à l'article 521-3 du PCG ; la numérotation d'autres articles change aussi (le résultat exceptionnel serait repris à l'article 531-5, à vérifier).
  - La date de publication au Journal officiel est à vérifier (3 juin ou 3 septembre 2026 selon les sources).
- **À vérifier.** La présence, dans le PCG 2025 (titre IX « Autres documents »), des modèles de tableau des soldes intermédiaires de gestion et de détermination de la CAF, que plusieurs items citent comme source. Seul le tableau de financement y a été confirmé.

## Classement des exercices

Les exercices QCM, QCM multiples et classements (tri) du chapitre ont été classés automatiquement selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, choix d'un compte, sans calcul) | 12 |
| `calcul` (montant, taux, prorata, délai à décompter) | 4 |
| `chiffre` (rappel d'un chiffre millésimé) | 0 |
| **Total** | 16 |

Aucun désaccord n'a été relevé. Seuls les 12 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
