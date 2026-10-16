# Cartes de notions : ue4-02 (Les revenus catégoriels de l'IR)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été écrites à partir de la seule fiche documentaire `data/ue4/ue4-02.fiche.json`, selon le contrat (section 8). Chaque carte pose une seule question, sans calcul ni chiffre millésimé. Elle s'appuie sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`. Le premier jet comptait 35 cartes (k01 à k35).
2. **Passe antérieure.** Une première relecture de fidélité, puis une première relecture d'exactitude, ont déjà corrigé le jeu (voir « Passes antérieures »). Lors de cette passe, k10 a été fusionnée dans k09 et supprimée. Son identifiant reste libre.
3. **Relecture de fidélité de la reprise.** Le premier relecteur a contrôlé les 34 cartes au regard de la fiche. Il en a corrigé 3 (k07, k09, k32) et a ajouté k36.
4. **Relecture d'exactitude de la reprise** (la présente). Un second relecteur, indépendant, a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 (CGI, BOFiP, Code du travail, Code de la sécurité sociale). Il a vérifié :
   - **l'exactitude** : une carte vraie seulement dans un cas particulier non dit est traitée comme inexacte ;
   - **l'ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG, et la seule réponse juste possible ?
   - **les doublons et les cartes triviales** ;
   - **l'absence de calcul et de chiffre millésimé**.
5. **Recherches.** Aucune recherche WebSearch n'a été faite lors de la présente relecture, faute de doute réel sur le fond. Les corrections ne portent que sur la délimitation des questions. La passe antérieure avait fait une recherche (voir « Recherches faites »).

Validation : `node validate.js data/ue4/ue4-02.cartes.json` renvoie ✓ (35 cartes, dont 8 de définition).

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k36, sans k10) |
| Définition (`def`) | 8 (k01, k02, k11, k13, k19, k28, k29, k31) |
| Compréhension (`comp`) | 27 |
| Corrigées par la relecture de fidélité de la reprise | 3 (k07, k09, k32) |
| Ajoutées par la relecture de fidélité de la reprise | 1 (k36) |
| Corrigées par la relecture d'exactitude de la reprise | 6 (k01, k11, k15, k18, k27, k30) |
| Supprimées lors de la reprise | 0 (k10 avait été supprimée lors de la passe antérieure) |

**Couverture.** Les six items de « Définitions » ont chacun au moins une carte. C'est aussi le cas des quinze items de « Règles essentielles », des six points de vigilance et du seul item stable de « Ce qui a changé récemment » (#4, loueurs en meublé non professionnels, carte k33).

**Items de la fiche sans carte :**

- **Chiffres et seuils #0 à #7.** Ces items sont millésimés, à l'exception de #3. Celui-ci donne les seuils de revenu fiscal de référence qui ouvrent la dispense du prélèvement forfaitaire non libératoire. Ils sont stables, mais une carte n'interrogerait que des montants à apprendre par cœur. La règle de dispense est couverte par k14 (« seuils légaux »).
- **Ce qui a changé récemment #0 à #3.** Ces items sont millésimés : réforme du micro-BIC des meublés, seuils micro 2026-2028, hausse de la CSG par la LFSS 2026, échéance et majoration de l'abattement fixe du dirigeant.
- **Règles essentielles #7, en partie.** La majoration de la limite d'imputation du déficit foncier à 21 400 € est une mesure temporaire. Ses dates ne figurent que dans un item millésimé (Chiffres et seuils#5). La carte k20 l'écarte expressément.

## Corrections de la première relecture (fidélité)

Le premier relecteur a contrôlé 34 cartes. Le résultat transmis s'interrompt au milieu de la ligne k36. La fin de cette ligne a été reconstituée à partir du fichier relu.

| Cible | Problème | Correction |
|---|---|---|
| k07 | La réponse disait « celles allouées par le juge, notamment pour un licenciement irrégulier ou sans cause réelle et sérieuse ». Ce « notamment » laissait entendre d'autres cas d'exonération totale, que la fiche ne mentionne pas (Règles essentielles#2 : seulement le PSE, le licenciement irrégulier et le licenciement sans cause réelle et sérieuse). Retirer simplement le mot aurait rendu la carte inexacte, car la question appelait une liste complète. Or l'article 80 duodecies vise aussi d'autres cas, comme le licenciement nul. | La question délimite désormais le champ au lieu d'appeler une liste : « Quel est le régime d'impôt sur le revenu des indemnités de licenciement versées dans le cadre d'un plan de sauvegarde de l'emploi ? ». Réponse : « Elles sont exonérées en totalité, sans la limite applicable aux autres indemnités de licenciement. Il en va de même des indemnités allouées par le juge pour un licenciement irrégulier ou sans cause réelle et sérieuse. » La carte s'en tient au texte de la fiche et ne prétend plus être exhaustive. |
| k09 | La question « Comment une rente viagère à titre onéreux est-elle imposée à l'impôt sur le revenu ? » admettait une autre réponse juste tirée de la fiche. Règles essentielles#6 range en effet ces rentes parmi les revenus du patrimoine soumis au barème, avec CSG déductible. | La question porte sur le seul point visé : « Comment est fixée la fraction imposable d'une rente viagère à titre onéreux à l'impôt sur le revenu ? ». Réponse : selon l'âge du crédirentier à la date d'entrée en jouissance de la rente, et non l'âge atteint l'année d'imposition, puis fraction invariable : 70 %, 50 %, 40 % ou 30 %. La base (Définitions#4 et Points de vigilance#4), `src` et `url` sont inchangés. |
| k32 | La réponse ajoutait « réintégration en principe des amortissements déduits ». Le qualificatif « en principe » ne figure dans aucun item de base (Points de vigilance#5 et Règles essentielles#13). Ce point faisait en outre doublon avec k33, qui porte sur la minoration du prix d'acquisition. | La réponse s'en tient au régime demandé : « Celui des plus-values immobilières des particuliers. Parmi les loueurs en meublé, seul le loueur professionnel relève des plus-values professionnelles. » La réintégration des amortissements reste traitée par k33. |
| k36 (ajoutée ; fin reconstituée) | Une clause de Règles essentielles#13 n'avait aucune carte. Pour les plus-values professionnelles, l'abattement du micro-BIC est réputé tenir compte des amortissements pratiqués selon le mode linéaire. | Nouvelle carte `comp`. Question : « Pour la plus-value professionnelle d'un loueur en meublé professionnel imposé au micro-BIC, comment les amortissements sont-ils pris en compte ? ». Réponse : l'abattement forfaitaire du micro-BIC est réputé tenir compte des amortissements linéaires ; le loueur non professionnel relève des plus-values immobilières des particuliers. Base : Règles essentielles#13 ; `src` et `url` copiés de cet item. |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k01 | La question « Quelles rémunérations relèvent de la catégorie des traitements et salaires ? » appelait une réponse complète. Or le critère du travail subordonné n'est que le principe : l'article 80 ter range aussi dans cette catégorie la rémunération de dirigeants qui ne sont pas subordonnés (président et directeur général de SA, président de SAS, gérant minoritaire de SARL). Le chapitre le rappelle d'ailleurs dans l'exercice de classement. | La question est délimitée : « Quelles rémunérations relèvent, en principe, de la catégorie des traitements et salaires à l'impôt sur le revenu ? ». La réponse (fiche Définitions#0) est inchangée. | CGI, art. 79 et 80 ter (connaissances générales) ; fiche Définitions#0 |
| k11 | La question « Quels revenus regroupe la catégorie des RCM ? » appelait une liste complète, alors que la réponse donne deux familles. Un étudiant pouvait citer à bon droit d'autres revenus, comme les produits des contrats d'assurance-vie et de capitalisation, sans retrouver la réponse attendue. | Question resserrée : « Quelles sont les deux grandes familles de revenus de capitaux mobiliers (RCM) à l'impôt sur le revenu ? ». La réponse (revenus distribués, produits de placements à revenu fixe) est inchangée. | Fiche Définitions#2 ; CGI, art. 108 s. et 118 s. (connaissances générales) |
| k15 | La question « Quels avantages l'option pour le barème procure-t-elle par rapport au PFU ? » admettait une autre réponse juste, absente du verso : l'imposition au taux marginal, plus favorable au contribuable faiblement imposé. Un correcteur du DCG l'accepterait. | La question vise les mécanismes de la réponse : « Quels abattement et déductions l'option globale pour le barème progressif ouvre-t-elle, par rapport au prélèvement forfaitaire unique, dans l'imposition des dividendes ? ». La réponse (abattement de 40 %, déduction des frais, CSG déductible) est inchangée. | Fiche Règles essentielles#5 ; CGI, art. 158, 3-2° et 200 A |
| k18 | La carte présentait l'absence de retrait pendant cinq ans comme la condition de l'exonération, sans réserve. Or un retrait avant cinq ans en cas de licenciement, d'invalidité ou de mise à la retraite anticipée n'entraîne pas la clôture du plan, et le gain n'est pas imposable. La carte était donc vraie en principe seulement. | Question délimitée : « En principe, à quelle condition les produits et plus-values d'un plan d'épargne en actions (PEA) sont-ils exonérés d'impôt sur le revenu ? ». La réponse est inchangée. Les exceptions ne sont pas détaillées, faute d'item dans la fiche. | CGI, art. 150-0 A, II-2 et 157, 5° bis (connaissances générales, à vérifier) ; fiche Règles essentielles#12 |
| k27 | La parenthèse « (détention des titres, fonctions de direction, départ en retraite) » laissait une seconde réponse juste pour la détention. L'article 150-0 D ter exige aussi la détention d'au moins 25 % des droits pendant les cinq années précédant la cession. Un étudiant répondant « cinq ans de détention » avait donc raison, sans retrouver « un an ». | La question vise l'ancienneté des titres cédés : « Pour l'abattement fixe du dirigeant de PME partant à la retraite, quelles durées s'appliquent à l'ancienneté des titres cédés, à la fonction de direction et au départ en retraite ? ». La réponse dit « Titres cédés détenus depuis au moins un an », le reste est inchangé. Elle rappelle toujours que ce ne sont pas les seules conditions. | CGI, art. 150-0 D ter (connaissances générales) ; fiche Règles essentielles#11 |
| k30 | Le seuil de recettes n'est que la condition de principe du micro-BNC. L'article 102 ter exclut certains contribuables du régime, quel que soit le montant de leurs recettes. La question « Quand… relève-t-il du micro-BNC ? » présentait le seuil comme suffisant. | Question délimitée : « Quand un titulaire de bénéfices non commerciaux relève-t-il en principe du régime micro-BNC plutôt que de la déclaration contrôlée ? ». La réponse est inchangée. | CGI, art. 102 ter (connaissances générales) ; fiche Règles essentielles#14 |

**Cartes contrôlées et maintenues :**

- **Exactitude confirmée** pour k02 à k09, k12 à k14, k16, k17, k19 à k26, k28, k29, k31 à k36. En particulier :
  - k07 et k32, telles que corrigées par la relecture de fidélité, ne disent plus rien d'inexact ;
  - k33 garde son « En principe » : l'article 150 VB, III exclut certains amortissements et certaines résidences de la minoration (voir « Points à reprendre dans la fiche ») ;
  - la nouvelle carte k36 est exacte : l'article 50-0 répute l'abattement micro représentatif des amortissements linéaires pour le calcul des plus-values professionnelles. Un loueur en meublé professionnel peut relever du micro-BIC.
- **Chiffres stables.** Plusieurs cartes citent des chiffres fixés par la loi, sans indexation annuelle, et chaque question porte sur la règle. Le contrat (section 8) les admet :
  - k04 (7 500 €) et k06 (six fois le plafond annuel de la sécurité sociale, une règle et non un montant) ;
  - k09 (fractions de la rente selon l'âge), k12, k13 et k35 (12,8 %), k17 (6,8 points, inchangés par la LFSS 2026) ;
  - k19 (15 000 €), k20 et k21 (10 700 €), k25 (50 000 €, de 2 % à 6 %), k26 (500 000 €) ;
  - k28, k29 et k31 (34 %, 87 %, 305 €, 50 % et 30 %).
- **Dates.** k33 cite le 15 février 2025, date d'entrée en vigueur, qui n'est pas un chiffre millésimé.
- **Doublons apparents.** Plusieurs cartes portent sur les mêmes items, mais chacune interroge un angle distinct :
  - k12, k13 et k35 : le PFU comme mode d'imposition, le prélèvement non libératoire comme acompte, puis la distinction entre les deux, qui est une confusion classique ;
  - k02, k05 et k34 : le net imposable, la renonciation à la déduction de 10 %, puis ses modalités ;
  - k20 et k21 : l'imputation du déficit foncier, puis l'ordre d'imputation ;
  - k26 et k27 : l'avantage, puis ses conditions de durée ;
  - k32, k33 et k36 : le régime applicable au loueur non professionnel, la minoration du prix d'acquisition, puis le traitement des amortissements au micro-BIC du loueur professionnel. La seconde phrase de k36 recoupe k32, mais elle sert de contraste et la question est différente.
- **k19 (micro-foncier).** Certains logements relevant de dispositifs particuliers sont exclus du régime, et l'option pour le réel reste possible. La carte de définition reprend la définition de la fiche, que retient le DCG. Elle est maintenue.
- **k22 et l'exercice #18.** Les deux portent sur la même règle : exonération après 22 ans pour l'impôt sur le revenu, après 30 ans pour les prélèvements sociaux. La carte ne demande que les durées énoncées par Points de vigilance#2, sans aucun calcul. Elle est maintenue.

## Recherches faites

**Lors de la présente relecture :** aucune. Les six corrections portent sur la délimitation des questions et ne changent aucune réponse sur le fond. Les points de droit sur lesquels elles s'appuient sans recherche sont signalés « à vérifier » dans la section suivante quand ils touchent la fiche.

**Lors de la passe antérieure :** une recherche, limitée à legifrance.gouv.fr et bofip.impots.gouv.fr.

1. **CGI, art. 150 VB, III : minoration du prix d'acquisition par les amortissements du loueur en meublé non professionnel.**
   - Confirmé : dans la version en vigueur (LEGIARTI000051202577), le prix d'acquisition est en principe réduit des amortissements admis en déduction. Ceux qui se rattachent aux dépenses retenues au 4° du II sont exclus de cette réduction.
   - Le texte vise aussi les résidences des articles L. 631-12 et L. 631-13 du Code de la construction et de l'habitation (étudiants, jeunes en formation, personnes âgées).
   - Cette recherche avait conduit à introduire « En principe » dans k33.

## Passes antérieures

Pour mémoire, les corrections faites avant la reprise. Leur état actuel figure dans le fichier des cartes.

| Passe | Cible | Correction |
|---|---|---|
| Fidélité | k03, k15 | Sigles « IR » et « PFU » développés dans la question. |
| Fidélité | k05 | Question au pluriel (« Quelles sont les conséquences ») ; impôt nommé. |
| Fidélité | k08 | « prestations de retraite versées en capital », comme dans la fiche. |
| Fidélité | k24 | La question porte sur l'exonération de la plus-value, non de la cession. |
| Fidélité | k33 | La question porte sur le calcul de la plus-value. |
| Exactitude | k09 et k10 | Doublon : k10 fusionnée dans k09, puis supprimée. |
| Exactitude | k20 | La majoration temporaire à 21 400 € est écartée par la question (« Hors majoration pour travaux de rénovation énergétique »). |
| Exactitude | k27 | La question est limitée aux durées ; la réponse rappelle que ce ne sont pas les seules conditions. |
| Exactitude | k33 | « En principe » ajouté (exceptions de l'article 150 VB, III). |

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

**Nouveaux points (présente relecture) :**

1. **Définitions#5 et Règles essentielles#13 : minimum de 305 €.** La fiche ne rattache le minimum d'abattement de 305 € qu'au micro-BA. Or il vaut aussi pour le micro-BNC (CGI, art. 102 ter, 1) et pour le micro-BIC (art. 50-0, 1), comme le dit d'ailleurs la leçon du chapitre pour le micro-BNC. Les cartes k28 et k31 restent exactes, car elles ne nient pas ce minimum, mais elles ne peuvent pas le citer tant que la fiche ne le dit pas. Connaissances générales, à vérifier.
2. **Règles essentielles#12 (PEA).** L'item ne mentionne pas les retraits anticipés sans clôture ni imposition, en cas de licenciement, d'invalidité ou de mise à la retraite anticipée. C'est pourquoi k18 a été délimitée par « En principe ». Connaissances générales, à vérifier.
3. **Définitions#0 (traitements et salaires).** L'item ne mentionne pas les dirigeants non subordonnés dont la rémunération est imposée dans cette catégorie (CGI, art. 80 ter : président et directeur général de SA, président de SAS, gérant minoritaire de SARL). D'où la délimitation de k01.
4. **Règles essentielles#14 (micro-BNC).** L'item présente le seuil de recettes comme seule condition. L'article 102 ter exclut pourtant certains contribuables du régime, quel que soit le montant de leurs recettes (par exemple, semble-t-il, les officiers publics et ministériels). À vérifier sur Légifrance avant de compléter l'item.

**Points relevés lors de la passe antérieure, toujours d'actualité :**

5. **Ce qui a changé récemment#4 et Points de vigilance#5.** La minoration du prix d'acquisition par les amortissements est présentée sans exception. Or l'article 150 VB, III exclut les amortissements liés aux dépenses retenues au 4° du II et vise les résidences des articles L. 631-12 et L. 631-13 du CCH. Par ailleurs, la formule de Points de vigilance#5 (« réintégration des amortissements déduits depuis la loi de finances pour 2025 ») peut se lire « seuls les amortissements déduits depuis 2025 ». Il faudrait écrire « depuis la loi de finances pour 2025, réintégration des amortissements déduits ».
6. **Règles essentielles#2.** La liste des indemnités exonérées en totalité est incomplète. L'article 80 duodecies, 1, 1° renvoie aussi aux articles L. 1235-1 (indemnité forfaitaire de conciliation), L. 1235-3-1 (licenciement nul) et L. 1235-11 à L. 1235-13 du Code du travail. Connaissances générales, à vérifier.
7. **Règles essentielles#7.** La majoration à 21 400 € est présentée sans son caractère temporaire. Ses dates (dépenses payées du 1er janvier 2023 au 31 décembre 2027) ne figurent que dans Chiffres et seuils#5. Il faudrait les reprendre dans l'item ou déplacer la majoration dans « Chiffres et seuils ».
8. **Règles essentielles#11.** Les conditions de l'abattement fixe sont incomplètes, même si le « notamment » rend l'item exact. Il manque la cession de la totalité des titres ou de plus de 50 % des droits, la détention d'au moins 25 % des droits pendant cinq ans, la cessation de toute fonction dans la société et la qualité de PME. C'est la condition de 25 % pendant cinq ans qui a obligé à resserrer encore la question de k27. Connaissances générales, à vérifier.

## Classement des exercices

Classement automatique des exercices QCM, QCM multiples et classements (tri) du chapitre selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 13 |
| `calcul` (montant, taux, prorata, délai) | 8 |
| `chiffre` (rappel d'un chiffre millésimé) | 0 |
| **Total** | 21 |

**Désaccord.** Un seul désaccord a été relevé, sur l'exercice #18. C'est un QCM sur la durée de détention qui ouvre l'exonération des plus-values immobilières : 22 ans pour l'impôt sur le revenu, 30 ans pour les prélèvements sociaux. Une passe l'a classé `notion`, l'autre `calcul`. C'est `calcul` qui a été retenu, car son explication refait le cumul des abattements annuels. La règle reste révisée par la carte k22.

Seuls les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
