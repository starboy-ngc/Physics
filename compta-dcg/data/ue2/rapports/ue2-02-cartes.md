# Cartes de notions : ue2-02 (La SARL et l'EURL)

15 octobre 2026. Fichier : `data/ue2/ue2-02.cartes.json`. Fiche de référence : `data/ue2/ue2-02.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Le premier relecteur a contrôlé les 35 cartes au regard de la fiche et en a corrigé 11 (k03, k05, k07, k09, k12, k13, k20, k25, k27, k29, k31). Il n'a fait ni suppression ni ajout.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code de commerce, Code civil, Code de la sécurité sociale et CGI. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse, et il a recherché les doublons. Bilan : 7 cartes corrigées (k08, k12, k18, k19, k21, k23, k32), 1 suppression (k17) et 1 ajout (k36). Le jeu a ensuite fait l'objet d'une seconde vérification indépendante lors de la reprise du travail. Elle a confirmé les corrections précédentes, a délimité la question de k08 et n'a fait aucune nouvelle recherche.
4. **Recherches.** 3 recherches WebSearch, toutes sur legifrance.gouv.fr, sur 3 autorisées : article L. 223-14 (condition de détention de deux ans), article L. 223-25 (renvoi à L. 223-29 pour la révocation du gérant) et article L. 223-29 (seconde consultation).

`node validate.js data/ue2/ue2-02.cartes.json` : ✓ (35 cartes, 6 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 6 de définition (`def`) et 29 de compréhension (`comp`). L'identifiant k17 est libre (carte supprimée) ; la nouvelle carte porte l'identifiant k36.
- Chaque item des sections « Définitions » et « Règles essentielles » a au moins une carte.
- **Items de la fiche sans carte :**
  - **Chiffres et seuils#0, #1, #3 et #6** (100 associés, 1/5 puis 5 ans, majorités, six mois) : leur contenu est repris dans les réponses de k04, k05, k15, k16, k22, k19 et k29, sans être cité dans `base`.
  - **Chiffres et seuils#4** et **Ce qui a changé récemment#2** (seuils du commissaire aux comptes) : items millésimés, exclus des cartes.
  - **Chiffres et seuils#5** (droits d'enregistrement de 3 %, 0,1 % et 5 %) : une carte se réduirait au rappel de taux fiscaux, et l'exemple de l'administration est un calcul.
  - **Ce qui a changé récemment#1** (renumérotation des articles relatifs au commissaire aux comptes) : une carte se réduirait au rappel de numéros d'articles.
  - **Points de vigilance#0** (base de calcul des majorités) : sa carte k17 a été supprimée comme doublon de k15 et k16 (voir ci-dessous).
  - **Points de vigilance#4** (lien avec l'UE 10 et le DSCG) : point de programme, pas une règle de droit.
- **Contenus couverts en partie :** la dérogation pour l'incorporation de bénéfices ou de réserves (Règles essentielles#8), la durée du mandat du commissaire aux comptes (Règles essentielles#15) et les règles propres à l'EURL pour le commissaire aux apports (Règles essentielles#3) n'ont pas de carte. Le jeu atteint le plafond de 35 cartes : un ajout imposerait une suppression.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la première relecture est tronqué au milieu de la ligne k27. La fin de la ligne k27 et les lignes k29 et k31 ont été complétées en comparant le fichier avec sa version précédente (commits f3776ee et 609a3b1).

| cible | problème | correction |
|---|---|---|
| k03 | La question en posait deux (« comment est fixé… et en quels titres est-il divisé »). | Remplacée par une question unique : « Comment le capital social d'une SARL est-il fixé et divisé ? ». Réponse inchangée. |
| k05 | La réponse s'ouvrait sur un fragment sans sujet (« Au moins un cinquième de leur montant… »). | Nouvelle ouverture reprenant le libellé cité dans la fiche : « Les parts représentant des apports en numéraire doivent être libérées d'au moins un cinquième de leur montant à la constitution ». Le reste est inchangé. |
| k07 | « Sinon » laissait entendre que le commissaire aux apports n'intervient que si les conditions de dispense manquent, alors que les associés peuvent aussi ne pas s'en dispenser. | « Sinon » remplacé par « À défaut de dispense ». |
| k09 | Deux questions en une (« qui peut être gérant et par qui est-il nommé »). | Question réduite à « Qui peut être gérant d'une SARL ? ». La nomination (par les associés, dans les statuts ou par un acte postérieur) est gardée comme précision dans la même phrase. |
| k12 | La question « par qui et à quelle majorité » appelait deux réponses, et « par qui » en a deux (associés, tribunaux). La réponse réduisait aussi le renvoi de la fiche aux conditions de majorité de l'article L. 223-29 à « associés représentant plus de la moitié des parts ». | Question : « Comment le gérant d'une SARL peut-il être révoqué ? ». La réponse reprend mot pour mot la formule de la fiche : « dans les conditions de majorité de l'article L. 223-29 (plus de la moitié des parts sociales) », et précise « décidée sans juste motif ». La relecture d'exactitude a ensuite revu cette carte (voir ci-dessous). |
| k13 | « ne possèdent pas ensemble » restait obscur : la règle de la cogérance de la fiche manquait. | Ajout : « En cogérance, la majorité s'apprécie sur les parts de l'ensemble des gérants » (Points de vigilance#1). Réponse de 67 mots. |
| k20 | La question « De quels moyens d'information sur la gestion disposent les associés ? » était trop ouverte : une personne qui connaît son cours pouvait répondre juste autrement (communication des documents, par exemple). | Le champ est délimité : « Quels moyens le Code de commerce donne-t-il aux associés d'une SARL pour interroger le gérant ou faire contrôler une opération de gestion ? ». Réponse inchangée. |
| k25 | « Conventions passées avec une SARL » ne nommait pas les cocontractants. | Remplacé par « conventions entre une SARL et ses gérants ou associés », comme dans Règles essentielles#11. |
| k27 | Il manquait l'exception propre à l'EURL de Règles essentielles#11 (la convention conclue avec l'associé unique est seulement mentionnée au registre des décisions). | Exception EURL ajoutée en fin de réponse ; phrase sur la procédure resserrée (« puis elle statue sans que l'intéressé vote ni que ses parts comptent pour le quorum et la majorité »). |
| k29 | La réponse ne disait pas que la dispense de rapport de gestion ne vient pas de l'article L. 223-31 (piège signalé par Points de vigilance#3). | Ajout : « L'article L. 223-31 ne prévoit que cela : la dispense de rapport de gestion résulte de l'article L. 232-1 et bénéficie, sauf exceptions, aux sociétés commerciales qui sont des micro-entreprises ou des petites entreprises ». Base complétée par Points de vigilance#3. |
| k31 | L'option pour l'impôt sur les sociétés était présentée sans sa faculté de renonciation, que donne Points de vigilance#2. | Ajout : renonciation possible jusqu'au cinquième exercice suivant ; sans renonciation dans ce délai, l'option devient irrévocable. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k08 | La question visait tous les apports en nature non évalués. Or la responsabilité solidaire des associés pendant cinq ans ne porte que sur les apports faits à la constitution (le verso dit d'ailleurs « lors de la constitution de la société »). Pour les apports faits lors d'une augmentation de capital, l'article L. 223-33 désigne d'autres personnes responsables. | Question délimitée : « Quelle responsabilité pèse sur les associés d'une SARL lorsque les apports en nature faits à la constitution n'ont pas été évalués par un commissaire aux apports ? ». Réponse inchangée. | C. com., art. L. 223-9 (Règles essentielles#3) |
| k12 | L'article L. 223-25 renvoie aux « conditions de l'article L. 223-29 », qui comprennent la seconde consultation à la majorité des votes émis, sauf clause contraire des statuts. La parenthèse « (plus de la moitié des parts sociales) » ne retenait que la règle de première consultation et laissait croire qu'elle vaut toujours pour la révocation. | Parenthèse retirée : « Par décision des associés prise dans les conditions de majorité des décisions ordinaires de l'article L. 223-29, à moins que les statuts ne prévoient une majorité plus forte ». Base complétée par Règles essentielles#6 (décisions ordinaires, dont la seconde consultation). Le reste est inchangé. | C. com., art. L. 223-25 et L. 223-29 ; recherches n° 2 et 3 |
| k17 (supprimée) | Doublon : la base de calcul des majorités (totalité des parts pour la décision ordinaire, parts des associés présents ou représentés pour la décision extraordinaire) est déjà la réponse de k15 et de k16. Le plafond de 35 cartes empêchait aussi d'ajouter k36 sans suppression. | Carte supprimée. L'identifiant k17 reste libre. | C. com., art. L. 223-29 et L. 223-30 |
| k18 | « Quelles décisions des associés exigent l'unanimité ? » admettait d'autres réponses justes absentes du verso : désignation du commissaire aux apports et dispense de ce commissaire (futurs associés), option des SARL antérieures à 2005 pour le nouveau régime des quorums. | Question délimitée : « Quelles modifications des statuts d'une SARL exigent l'unanimité des associés ? ». Réponse inchangée (nationalité, augmentation des engagements, transformation en SNC, SCS, SCA ou SAS). | C. com., art. L. 223-30, L. 223-43 et L. 227-3 |
| k19 | Deux questions en une (« dans quel délai et sous quelle forme »). La forme était aussi incomplète : l'article L. 223-27 admet, si les statuts le prévoient, une décision résultant du consentement de tous les associés exprimé dans un acte, que la fiche ne mentionne pas. | Question unique, centrée sur la réforme : « Quelle exception à la consultation écrite des associés de SARL la loi du 13 juin 2024 a-t-elle supprimée ? ». Réponse : l'approbation des comptes annuels, jusque-là réservée à l'assemblée ; depuis le 14 septembre 2024, les statuts peuvent prévoir une consultation écrite, y compris électronique. Le délai de six mois (sauf prolongation par décision de justice) reste en précision. | C. com., art. L. 223-26 et L. 223-27 ; loi n° 2024-537 du 13 juin 2024, art. 18 |
| k21 | « Dans quels cas une SARL doit-elle désigner un commissaire aux comptes ? » appelait une liste que le verso ne donne pas en entier : depuis la loi PACTE, une SARL peut aussi y être tenue au titre d'un groupe (société qui en contrôle d'autres). La fiche n'en parle pas. | Question délimitée au critère de taille : « Quand la taille d'une SARL l'oblige-t-elle à désigner un commissaire aux comptes ? ». Réponse inchangée sur le fond (deux des trois seuils à la clôture ; nomination en justice à la demande d'associés représentant au moins le dixième du capital). | C. com., art. L. 223-35 |
| k23 | L'article L. 223-14 prive de l'obligation de rachat (al. 3) et de la cession libre à l'expiration du délai (al. 5) l'associé qui détient ses parts depuis moins de deux ans, sauf succession, liquidation de communauté entre époux ou donation à un conjoint, un ascendant ou un descendant. La réponse présentait ces deux règles sans réserve. La fiche ne mentionne pas cette condition. | « En principe » ajouté en tête de réponse. La condition de deux ans n'est pas écrite sur la carte, car la fiche ne la donne pas ; elle est signalée ci-dessous comme point à reprendre. | C. com., art. L. 223-14 ; recherche n° 1 |
| k32 | La question attribuait l'option pour l'assimilation à une EURL à la loi du 14 février 2022. Or l'article 1655 sexies du CGI qui l'organise paraît issu de la loi de finances pour 2022 ; le doute n'a pas été levé faute de recherche disponible. | Question sans rattachement à une loi : « Comment un entrepreneur individuel peut-il relever de l'impôt sur les sociétés sans créer de société ? ». Réponse : en optant pour l'assimilation à une EURL, et ainsi pour l'impôt sur les sociétés. La loi du 14 février 2022 reste citée pour le double patrimoine, qu'elle a bien créé (art. L. 526-22). | C. com., art. L. 526-22 ; CGI, art. 1655 sexies |
| k36 (ajoutée) | La prescription de l'action en responsabilité contre le gérant, classique au DCG, n'avait pas de carte : k14 ne porte que sur les cas de responsabilité. | Nouvelle carte `comp` : « Dans quel délai se prescrit l'action en responsabilité contre le gérant d'une SARL ? ». Réponse : trois ans à compter du fait dommageable ou, s'il a été dissimulé, de sa révélation ; dix ans lorsque le fait est qualifié crime. Base : Règles essentielles#12 ; `src` et `url` copiés de cet item. | C. com., art. L. 223-23 |

Les autres cartes ont été contrôlées sans changement : k01 à k07, k09 à k11, k13 à k16, k20, k22, k24 à k31, k33 à k35.

## Recherches faites

3 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr.

1. Requête « article L. 223-14 code de commerce associé cédant ne peut se prévaloir s'il ne possède ses parts depuis au moins deux ans ».
   - **Confirmé.** Sauf en cas de succession, de liquidation de communauté de biens entre époux ou de donation au profit d'un conjoint, d'un ascendant ou d'un descendant, l'associé cédant ne peut se prévaloir des troisième et cinquième alinéas (rachat obligatoire, cession initialement prévue) s'il ne détient ses parts depuis au moins deux ans. Toute clause contraire est réputée non écrite. L'article L. 223-16 rend L. 223-14 applicable aux clauses limitant la cessibilité entre associés, les statuts pouvant réduire la majorité ou abréger les délais.
   - Effet : correction de k23 ; point 1 à reprendre dans la fiche.
   - Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006223059
2. Requête « article L223-25 code de commerce gérant peut être révoqué par décision des associés dans les conditions de l'article L. 223-29 ».
   - **Confirmé.** « Le gérant peut être révoqué par décision des associés dans les conditions de l'article L. 223-29, à moins que les statuts prévoient une majorité plus forte. » Dommages-intérêts si la révocation est décidée sans juste motif ; révocation judiciaire pour cause légitime à la demande de tout associé. Le résultat signale aussi une règle spéciale pour la SARL qui exploite une entreprise de presse (révocation aux trois quarts du capital), sans intérêt pour le DCG.
   - Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006223152
3. Requête « article L223-29 code de commerce décisions adoptées associés représentant plus de la moitié des parts sociales seconde fois majorité des votes émis ».
   - **Confirmé.** Première consultation : associés représentant plus de la moitié des parts sociales. À défaut, et sauf stipulation contraire des statuts, seconde consultation à la majorité des votes émis, quel que soit le nombre des votants (version en vigueur depuis le 21 juillet 2019). Le résultat ne montre aucune exception propre à la révocation du gérant.
   - Effet : correction de k12 ; point 2 à reprendre dans la fiche. k15 est exacte.
   - Source : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038799356

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#9** (cession à un tiers). Il manque la condition de détention de deux ans de l'article L. 223-14 : sauf succession, liquidation de communauté de biens entre époux ou donation à un conjoint, un ascendant ou un descendant, l'associé cédant qui détient ses parts depuis moins de deux ans ne peut ni exiger le rachat de ses parts après un refus d'agrément ni réaliser la cession initialement prévue (recherche n° 1). Une fois l'item complété, k23 pourra donner la condition au lieu de « En principe ».
2. **Règles essentielles#5** (révocation du gérant), et par suite **Chiffres et seuils#3** si l'on y ajoute la révocation. La parenthèse « (plus de la moitié des parts sociales) » réduit le renvoi de l'article L. 223-25 à la première consultation. L'article L. 223-29 prévoit aussi une seconde consultation à la majorité des votes émis, sauf clause contraire des statuts (recherches n° 2 et 3). Il faut soit retirer la parenthèse, soit dire, source à l'appui, si la seconde consultation s'applique à la révocation.
3. **Ce qui a changé récemment#5** (à vérifier). L'option de l'entrepreneur individuel pour l'assimilation à une EURL (CGI, art. 1655 sexies) est attribuée à la loi n° 2022-172 du 14 février 2022. Cet article paraît avoir été créé par la loi n° 2021-1900 du 30 décembre 2021 de finances pour 2022 (art. 13). Point non vérifié, faute de recherche disponible : il faut confirmer l'origine de l'article avant de la citer. L'item omet aussi une condition de l'article 1655 sexies : l'option n'est ouverte qu'à l'entrepreneur individuel soumis à un régime réel d'imposition, ce qui exclut le micro-entrepreneur. Ce point est également à vérifier. La carte k32, qui demande « comment » et non « à quelles conditions », reste exacte en l'état.
4. **Règles essentielles#13** (complément). L'article L. 223-27 permet aussi aux statuts de prévoir que les décisions résultent du consentement de tous les associés exprimé dans un acte. Depuis la loi du 13 juin 2024, cette faculté ne paraît plus exclure l'approbation des comptes. L'item pourrait le mentionner.
5. **Définitions#4** (complément mineur). L'interdiction des emprunts, découverts, cautions et avals (L. 223-21) ne s'applique pas, lorsque la société exploite un établissement financier, aux opérations courantes de ce commerce conclues à des conditions normales. Cette exception est absente de l'item. Elle ne change pas la carte k26 pour un examen du DCG.
6. **Règles essentielles#15** (complément mineur). La SARL peut aussi être tenue de désigner un commissaire aux comptes au titre d'un groupe : c'est le cas d'une société qui en contrôle d'autres, lorsque l'ensemble dépasse les seuils. L'item ne vise que le critère de taille propre à la société. C'est pourquoi la question de k21 a été délimitée.

## Classement des exercices

Le classement automatique porte sur les 24 exercices QCM, QCM multiples et classements du chapitre (21 QCM, 2 QCM multiples, 1 classement) :

| nature | nombre |
|---|---|
| notion | 17 |
| calcul | 6 |
| chiffre | 1 |

Aucun désaccord entre les classements. Les exercices qui sortent des révisions espacées :
- **calcul** (6 QCM) : #4 (dispense de commissaire aux apports à partir de montants d'apports), #7 et #8 (statut social du gérant à partir de pourcentages de parts), #11 (majorité ordinaire à partir d'un nombre de voix), #17 (agrément réputé acquis à partir de dates), #22 (date limite d'approbation des comptes) ;
- **chiffre** (1 QCM) : #21 (seuils de désignation du commissaire aux comptes en vigueur, millésimés).

Les notions qu'ils illustrent restent révisées par les cartes k07, k13, k15, k22, k19 et k21. Les 17 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes.
