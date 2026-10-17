# Cartes de notions : ue10-03 (Amortissements, dépréciations et sortie des immobilisations)

Date : 16 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-03.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relectures de fidélité.** Trois relectures successives ont vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elles n'ont fait aucune recherche web, le seul juge étant le texte de la fiche. Leurs corrections figurent plus bas.
3. **Relecture d'exactitude.** Une dernière relecture, indépendante des précédentes, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 16 octobre 2026 : Code de commerce, CGI et BOFiP, Code monétaire et financier, PCG modifié par le règlement ANC n° 2022-06, et règlement ANC n° 2026-03, applicable aux exercices ouverts à compter du 1er janvier 2027 ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Les 35 cartes ont été relues une à une, en les confrontant à la fiche et aux textes. Deux cartes ont été corrigées (k05 et k08). Aucune n'a été supprimée ni ajoutée.
4. **Recherches.** Une seule recherche web a été faite, sur bofip.impots.gouv.fr (voir « Recherches »).
5. **Validation.** La commande `node validate.js data/ue10/ue10-03.cartes.json` renvoie ✓ : 35 cartes, dont 8 définitions.

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. Les identifiants k26 et k33 ont été supprimés lors d'une passe antérieure : leurs questions (prix de cession d'une immobilisation corporelle ; crédit-bail dans les comptes consolidés) recoupaient k25 et k31. Ils restent des trous et n'ont pas été réutilisés. Aucune carte n'a été renumérotée.
- **Répartition : 8 cartes `def` et 27 cartes `comp`.**
- **Couverture de la fiche :**
  - les 5 items de « Définitions » ont chacun au moins une carte : #0 → k01 ; #1 → k13, k14, k15 ; #2 → k16 ; #3 → k11 ; #4 → k30, k31 ;
  - les « Règles essentielles » stables (#0 à #13 et #15 à #17) sont toutes couvertes ;
  - les 7 « Points de vigilance » sont tous couverts, par des cartes de compréhension ;
  - dans « Ce qui a changé récemment », les items stables #0, #1 et #2 sont couverts (k27, k25, k34) ;
  - dans « Chiffres et seuils », les items #0 (coefficients du dégressif, k36) et #2 (fonds commercial sur dix ans, k24) sont couverts.
- **Items de fiche sans carte :**
  - **Règles essentielles#14** (fiscalité du fonds commercial), **Chiffres et seuils#3 et #4**, **Ce qui a changé récemment#3 et #4** : items millésimés (2024 ou 2026), exclus par le contrat ;
  - **Chiffres et seuils#1** : exemple chiffré de taux dégressif, donc un calcul ;
  - **Règles essentielles#17, seconde phrase** (autres personnes morales et commerçants personnes physiques : loyers distincts au compte de résultat, redevances restant à supporter en annexe) : seule la partie relative aux sociétés commerciales a une carte (k32). Le plafond de 35 cartes est atteint.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les seuls chiffres sont stables et font partie de la règle : coefficients 1,25, 1,75 et 2,25, dix ans pour le fonds commercial, deux ans et trois ans, dates d'application des règlements ANC.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | ue10-03-k03 | « Quel mode d'amortissement l'entité doit-elle retenir ? » appelait aussi « le mode linéaire », réponse juste mais incomplète, alors que la réponse attendue est le critère de choix. | Question reformulée : « Selon le PCG, que doit traduire le mode d'amortissement retenu pour un actif amortissable ? ». La réponse commence par le rythme de consommation des avantages économiques attendus, puis rappelle que le linéaire s'applique à défaut (Règles essentielles#0). |
| 1 | ue10-03-k05 | « Ailleurs » était imprécis, et « l'écart d'amortissement » s'éloignait du texte de Points de vigilance#0. | Remplacé par « pour les autres, … l'écart entre amortissement fiscal et amortissement comptable passe par les amortissements dérogatoires », selon le texte de la fiche. |
| 1 | ue10-03-k07 | Le champ de la question n'était fixé que par le renvoi « selon l'annexe II du CGI ». On pouvait répondre juste en citant les exclusions de l'art. 39 A (immeubles d'habitation, chantiers, locaux). | Question reformulée pour écarter les exclusions de l'art. 39 A. La réponse est inchangée : biens d'occasion, durée normale d'utilisation inférieure à trois ans. |
| 1 | ue10-03-k16 | Le pronom « celle-ci » pouvait renvoyer à la valeur actuelle ou à la valeur nette comptable. | « La valeur nette comptable est alors ramenée à la valeur d'inventaire à la clôture, que la dépréciation soit définitive ou non » (Définitions#2). |
| 1 | ue10-03-k17 | Le pronom de « si elle ne peut être déterminée isolément » avait un référent ambigu, ce qui brouillait la règle du groupe d'actifs. | Réécrit : la valeur actuelle de l'actif ou, si celle de l'actif pris isolément ne peut être déterminée, celle du groupe d'actifs auquel il appartient (Règles essentielles#9). |
| 1 | ue10-03-k25 | La fin elliptique « utilisent encore 675/775 » collait à la définition par un point-virgule. | Phrase à part : « Les sujets antérieurs à 2025 utilisent encore 675/775 » (Ce qui a changé récemment#1). |
| 1 | ue10-03-k34 | La question affirmait sans réserve que les exercices 2025 et 2026 relèvent du PCG issu du règlement n° 2022-06, alors que le règlement n° 2026-03 peut être appliqué par anticipation. | La question commence par « Sauf application anticipée, … ». La réponse précise l'objet du règlement n° 2026-03 (Ce qui a changé récemment#2). |
| 1 | ue10-03-k35 (ajout) | Règle non couverte : les trois étapes de la comptabilisation d'une cession. | Carte de compréhension sans montant : dotation complémentaire jusqu'à la date de cession et reprise du solde du 145, enregistrement du prix (462 et 757), sortie du bien (28x, 657 et 2x). Base : Points de vigilance#4 et Règles essentielles#15. |
| 2 | ue10-03-k06 | « Quels biens peuvent être amortis selon le mode dégressif… ? » présentait l'art. 39 A comme une condition suffisante, alors que les biens d'occasion et ceux de durée inférieure à trois ans sont exclus (Règles essentielles#5). | Question reformulée avec le mot de la fiche, « réservé », qui exprime une condition nécessaire : « Selon l'article 39 A du CGI, à quelle catégorie de biens l'amortissement dégressif fiscal est-il réservé ? ». |
| 2 | ue10-03-k07 | « Quels biens sont exclus » appelait plusieurs réponses justes (par exemple les biens qui ne sont pas des biens d'équipement). | Question limitée aux biens d'équipement. La réponse reste : biens d'occasion, durée normale d'utilisation inférieure à trois ans. |
| 2 | ue10-03-k11 | Apposition bancale qui s'éloignait de la formulation de la fiche. | Seconde phrase alignée sur Définitions#3 : « Ce sont des écritures d'origine purement fiscale, classées en résultat exceptionnel par le PCG 2025. » |
| 2 | ue10-03-k17 | La carte disait que le test compare la valeur nette comptable de l'actif à la valeur actuelle du groupe d'actifs, ce que la fiche ne dit pas. | La valeur nette comptable est comparée à la valeur actuelle de l'actif ; si celle de l'actif pris isolément ne peut être déterminée, on détermine celle du groupe d'actifs auquel il appartient (Règles essentielles#9). |
| 2 | ue10-03-k37 | « En effet » ajoutait un lien de causalité absent de la fiche (Règles essentielles#4). | Dernière phrase réduite à « L'annuité dégressive s'applique à la valeur résiduelle. » |
| 3 | ue10-03-k05 | La précision « l'excédent de l'amortissement fiscal sur l'amortissement comptable est constaté en amortissements dérogatoires » venait de Définitions#3, qui n'est pas en base. | Remplacée par la formulation de Points de vigilance#0 : « l'écart entre amortissement fiscal et amortissement comptable passe alors par les amortissements dérogatoires ». |
| 3 | ue10-03-k27 | « Comprend désormais » était plus faible que la fiche, pour laquelle le résultat exceptionnel « est réservé » à ces seuls éléments. | « Le résultat exceptionnel est désormais réservé aux produits et charges directement liés à un événement majeur et inhabituel et aux écritures d'origine purement fiscale, comme les amortissements dérogatoires. » |
| 3 | ue10-03-k31 | La question ne demandait que le traitement dans les comptes individuels, alors que la réponse traitait aussi les comptes consolidés. | Nouvelle question : « En quoi le traitement d'un contrat de crédit-bail chez le preneur diffère-t-il entre ses comptes individuels et les comptes consolidés établis selon le règlement ANC n° 2020-01 ? ». Réponse inchangée. |

Les relectures de fidélité n'ont supprimé aucune carte. La première a ajouté k35 et contrôlé 34 cartes ; les deux suivantes en ont contrôlé 35.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-03-k05 | « L'écart entre amortissement fiscal et amortissement comptable passe alors par les amortissements dérogatoires » n'est vrai que dans un sens. Les dérogatoires sont des provisions réglementées dotées quand l'amortissement fiscal excède l'amortissement comptable, puis reprises. Quand la durée d'utilisation comptable est plus courte que la durée d'usage, l'amortissement comptable excède d'emblée l'amortissement fiscal : aucun dérogatoire ne peut être constitué (le compte 145 ne peut être débiteur). | La fin de la réponse délimite le cas : « l'écart passe alors par les amortissements dérogatoires lorsque l'amortissement fiscal excède l'amortissement comptable ». La carte reste portée par Règles essentielles#2 et Points de vigilance#0. La restriction reprend Définitions#3 et Règles essentielles#7. | PCG, art. 214-13 ; compte 145 ; Définitions#3 et Règles essentielles#7 de la fiche |
| ue10-03-k08 | Le point de départ « premier jour du mois d'acquisition » vise le bien acquis ; pour un bien que l'entreprise fabrique pour elle-même, la référence n'est pas l'acquisition. D'autre part, « la date d'acquisition est celle de l'accord sur la chose et le prix » n'est qu'un principe : le transfert de propriété peut être retardé (chose future, clause contraire). | Question délimitée : « Pour un bien acquis, en quoi le point de départ… ? ». La dernière phrase devient : « la date d'acquisition est en principe celle de l'accord sur la chose et le prix, même si la livraison et le paiement interviennent plus tard », comme dans Points de vigilance#1. « Donc » est retiré pour rester sous 70 mots. | BOI-BIC-AMT-20-20-30 (Points de vigilance#1, Règles essentielles#4) ; C. civ., art. 1583 |

Les 33 autres cartes ont été jugées exactes au 16 octobre 2026, sans ambiguïté qui justifie une retouche. La relecture a notamment vérifié :

- **PCG, art. 214-1 à 214-19** : définition de l'amortissement et du montant amortissable (valeur résiduelle significative et mesurable), mode linéaire à défaut de mode mieux adapté, révision prospective du plan, option des petites entreprises pour la durée d'usage (immobilisations non décomposables), valeur actuelle, vénale et d'usage, définition de la dépréciation, indices de perte de valeur à considérer au minimum, groupe d'actifs, effet prospectif de la dépréciation sur la base amortissable, reprise des dépréciations sauf pour le fonds commercial, présomption de durée non limitée du fonds commercial avec test annuel, amortissement sur dix ans à défaut de durée fiable, option des petites entreprises.
- **CGI, art. 39 A, 39 B et 39 duodecies ; ann. II, art. 22** : biens d'équipement éligibles au dégressif et exclusions, coefficients, amortissement minimal et perte définitive du droit à déduction, souplesse de l'appréciation selon le BOFiP, passage à l'annuité linéaire, qualification des plus-values des entreprises à l'impôt sur le revenu.
- **Plan de comptes 2026 et art. 513-5** : comptes 145, 68725, 78725, 462, 657, 757 et 7587 ; classement des cessions en résultat d'exploitation ; résultat exceptionnel réservé à l'événement majeur et inhabituel et aux écritures d'origine purement fiscale ; indemnités compensant des charges d'exploitation maintenues en exploitation.
- **Crédit-bail** : CMF, art. L. 313-7 et R. 313-14 ; PCG, art. 212-5 ; règlement ANC n° 2020-01, art. 272-2.

Doublons examinés et conservés : k25 (comptes 657 et 757) et k35 (trois étapes de la cession) se recoupent sur les numéros de comptes, mais l'une interroge le choix des comptes et l'autre la chronologie, avec la dotation complémentaire et la reprise du 145 ; k18 et k19 séparent les indices internes et externes ; k06 et k36 reposent sur le même item mais portent l'une sur les biens éligibles, l'autre sur la formation des taux.

## Recherches

Une recherche WebSearch, limitée à bofip.impots.gouv.fr :

1. « BOI-BIC-AMT-20-20-10 amortissement dégressif entreprises concernées entreprises industrielles biens d'équipement ». Résultat : BOI-BIC-AMT-20-20-10-20120912 (https://bofip.impots.gouv.fr/bofip/4748-PGP.html/identifiant=BOI-BIC-AMT-20-20-10-20120912). Le régime dégressif est ouvert aux entreprises passibles de l'impôt sur les sociétés quelle que soit la nature de leur activité et aux entreprises imposées à l'impôt sur le revenu dans la catégorie des BIC. Les entreprises commerciales qui possèdent des immobilisations identiques à celles des entreprises industrielles y sont admises dans les mêmes conditions. Le dernier alinéa de l'art. 22 de l'annexe II exclut les biens déjà usagés. La carte k06, qui ne demande que la catégorie de biens « selon l'article 39 A », reste exacte. Le point concerne la fiche (voir ci-dessous).

Aucune autre recherche : le point de k05 (sens unique des dérogatoires) découle de la nature même d'une provision réglementée, et celui de k08 du texte de la fiche (« même si la livraison et le paiement interviennent plus tard »).

## Points à reprendre dans la fiche

1. **Règles essentielles#3 (amortissement dégressif).** Relevé par la première et la troisième relecture de fidélité, confirmé par la recherche ci-dessus. L'item reprend la lettre de l'art. 39 A : « acquis ou fabriqués par les entreprises industrielles ». Selon BOI-BIC-AMT-20-20-10, le régime est ouvert aux sociétés à l'IS quelle que soit leur activité, aux entreprises à l'IR dans la catégorie des BIC, et aux entreprises commerciales pour des immobilisations identiques à celles des entreprises industrielles. Il faudrait ajouter cette précision doctrinale, avec la liste des biens éligibles de l'art. 22 de l'annexe II.
2. **Points de vigilance#0.** Deux points.
   - « L'écart entre amortissement fiscal et amortissement comptable passe par les amortissements dérogatoires » n'est vrai que lorsque l'amortissement fiscal excède l'amortissement comptable (relevé par la relecture d'exactitude). Il faudrait écrire : « l'excédent de l'amortissement fiscal sur l'amortissement comptable est constaté en amortissements dérogatoires ».
   - « Seules les petites entreprises peuvent aligner les deux durées » est trop absolu (relevé par la deuxième relecture de fidélité). Mieux vaut : « seules les petites entreprises peuvent retenir d'office la durée d'usage ».
3. **Points de vigilance#1 et Règles essentielles#4.** Le point de départ « premier jour du mois d'acquisition » ne vise que les biens acquis. Il faudrait indiquer le point de départ retenu pour les biens fabriqués par l'entreprise (à vérifier dans BOI-BIC-AMT-20-20-30, non recherché ici) et écrire « en principe » devant la date de l'accord sur la chose et le prix.
4. **Règles essentielles#4 (calcul du dégressif).** Relevé par la troisième relecture de fidélité. « Valeur résiduelle » y désigne la valeur restant à amortir, alors que Règles essentielles#0 l'emploie au sens du PCG (valeur de fin d'utilisation déduite du montant amortissable). Il faudrait préciser le sens retenu en #4. La carte k37 garde pour cela la glose « (valeur restant à amortir) ».
5. **Ce qui a changé récemment#1.** Relevé par la deuxième relecture de fidélité. Les comptes 757 (cessions) et 756 (gains de change commerciaux) sont rangés sous le règlement ANC n° 2023-03, alors qu'ils découlent du plan de comptes du règlement n° 2022-06. La rédaction peut laisser croire que c'est le règlement n° 2023-03 qui les a créés. À vérifier et à clarifier.
6. **Règles essentielles#14.** Relevé par la deuxième relecture de fidélité. L'item est millésimé 2026, alors que le principe de non-déductibilité de l'amortissement du fonds commercial (CGI, art. 39, 1-2°) est stable. Un item stable qui isole ce principe de la dérogation temporaire permettrait une carte.

## Classement des exercices

Le chapitre compte 19 exercices QCM, QCM multiples ou de classement. Leur classement automatique donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 13 | oui |
| `calcul` | 5 | non |
| `chiffre` | 1 | non |

Un désaccord entre classeurs a été arbitré : l'exercice #17, classé `notion` par l'un et `chiffre` par l'autre, est retenu en `chiffre`. Les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Les exercices de nature `calcul` et `chiffre` restent dans le chapitre, mais ne sont pas proposés en révision.
