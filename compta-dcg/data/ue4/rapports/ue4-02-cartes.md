# Cartes de notions : ue4-02 (Les revenus catégoriels de l'IR)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-02.fiche.json` et d'elle seule. Elles respectent le contrat (section 8) : une question par carte, aucun calcul, aucun chiffre millésimé, et chaque carte s'appuie sur un ou deux items de fiche (`base`) dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : un premier relecteur a contrôlé les 35 cartes. Il a vérifié que chaque carte dit ce que dit la fiche, sans plus, et qu'elle respecte la forme exigée par le contrat.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a vérifié les points suivants :
   - **Exactitude** : chaque carte est-elle juste au regard du droit en vigueur au 15 octobre 2026 (CGI, BOFiP, Code du travail, Code de la sécurité sociale, Code de la construction et de l'habitation) ? Une carte vraie seulement dans un cas particulier non dit est traitée comme inexacte.
   - **Ambiguïté** : la réponse attendue est-elle celle qu'attendrait un correcteur du DCG, et la seule réponse juste possible ?
   - **Doublons et cartes triviales.**
   - **Absence de calcul et de chiffre millésimé.**
4. **Recherches** : 1 recherche sur les 3 permises, limitée à legifrance.gouv.fr et bofip.impots.gouv.fr (détail plus bas).

Validation : `node validate.js data/ue4/ue4-02.cartes.json` renvoie ✓ (34 cartes, dont 8 de définition).

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 34 (k01 à k35, sans k10) |
| Définition (`def`) | 8 |
| Compréhension (`comp`) | 26 |
| Cartes corrigées par la relecture d'exactitude | 6 (k07, k09, k20, k27, k32, k33) |
| Cartes supprimées | 1 (k10, fusionnée dans k09) |
| Cartes ajoutées | 0 |

**Couverture** : chacun des six items de la section « Définitions » a au moins une carte. Il en va de même des quinze règles essentielles, des six points de vigilance et du seul item stable de « Ce qui a changé récemment » (#4, loueurs en meublé non professionnels).

**Items de la fiche sans carte** :

- **Chiffres et seuils #0, #1, #2, #4, #5, #6 et #7** : ces items sont millésimés. Ils portent sur les limites de la déduction de 10 % et de l'abattement sur les pensions, le brut équivalent du plafond des heures supplémentaires, le taux global du PFU, les seuils du micro-foncier et du déficit foncier, les seuils micro 2026-2028 et le meublé de tourisme non classé.
- **Chiffres et seuils #3** : les seuils de revenu fiscal de référence qui ouvrent la dispense du prélèvement forfaitaire non libératoire sont stables. Une carte sur ces seuils n'interrogerait pourtant que des montants à apprendre par cœur. La règle de dispense est couverte par k14 (« seuils légaux »).
- **Ce qui a changé récemment #0 à #3** : ces items sont millésimés. Ils portent sur la réforme du micro-BIC des meublés, l'actualisation des seuils micro, la hausse de la CSG par la LFSS 2026, ainsi que l'échéance et la majoration de l'abattement fixe du dirigeant.
- **Règles essentielles #7, en partie** : la majoration de la limite d'imputation à 21 400 € n'a plus de carte. C'est une mesure temporaire (voir k20).

## Corrections de la première relecture (fidélité)

Le premier relecteur a contrôlé 35 cartes. Le résultat transmis s'interrompt au milieu de la ligne k33. La fin de la ligne k33 et les lignes k03 et k05 ont donc été reconstituées à partir de l'écart entre la version initiale du fichier (commit f3776ee) et la version relue.

| Cible | Problème | Correction |
|---|---|---|
| k03 (reconstituée) | La question employait le sigle « IR » sans le développer. | La question dit « à l'impôt sur le revenu ». |
| k05 (reconstituée) | La question au singulier (« Quelle est la conséquence ») annonçait une seule conséquence, alors que la réponse en donne deux. L'impôt concerné n'était pas nommé. | Nouvelle question : « Quelles sont les conséquences, pour un salarié, de la renonciation à la déduction forfaitaire de 10 % sur ses salaires à l'impôt sur le revenu ? ». |
| k07 | La question « Quelles indemnités de licenciement sont exonérées en totalité ? » laissait une autre réponse juste : une indemnité qui ne dépasse pas l'indemnité légale ou conventionnelle est elle aussi exonérée en totalité (Règles essentielles#2). | La question est délimitée : « …exonérées en totalité d'impôt sur le revenu, quel que soit leur montant ? ». La réponse attendue reste les indemnités du plan de sauvegarde de l'emploi (PSE) et celles du licenciement irrégulier ou sans cause réelle et sérieuse. |
| k08 | La réponse parlait de « prestations versées en capital », alors que la fiche (Règles essentielles#3) parle de « prestations de retraite versées en capital ». | La réponse dit « Les prestations de retraite versées en capital soumises, sur option, au prélèvement forfaitaire de 7,5 %… ». |
| k15 | Le sigle PFU n'était pas développé dans la question, qui n'était donc pas compréhensible seule. | La question dit « par rapport au prélèvement forfaitaire unique ». |
| k20 | La limite de 10 700 € était dite « relevée à hauteur des dépenses de rénovation énergétique », sans plafond : on pouvait croire à une majoration sans limite. La fiche (Règles essentielles#7) dit « portée jusqu'à 21 400 € ». | Réponse réécrite en 69 mots, avec la limite « portée jusqu'à 21 400 € à hauteur des dépenses de rénovation énergétique faisant passer le logement d'une classe E, F ou G à une classe A à D ». Cette phrase a ensuite été retirée par la relecture d'exactitude (voir plus bas). |
| k24 | La question disait que « la première cession… est exonérée de plus-value immobilière ». C'est en réalité la plus-value qui est exonérée, pas la cession. | Nouvelle question : « À quelles conditions la plus-value réalisée lors de la première cession d'un logement autre que la résidence principale est-elle exonérée ? ». |
| k32 | « réintégration des amortissements déduits depuis la loi de finances pour 2025 » pouvait se lire « seuls les amortissements déduits depuis 2025 sont réintégrés ». La fiche (Ce qui a changé récemment#4) dit au contraire que tous les amortissements admis en déduction sont réintégrés, pour les cessions faites depuis le 15 février 2025. | La réponse dit « avec, depuis la loi de finances pour 2025, réintégration des amortissements déduits ». |
| k33 (fin reconstituée) | La question « modifie-t-elle la plus-value immobilière » était imprécise, puisque la réponse porte sur le calcul de la plus-value (prix d'acquisition minoré des amortissements). | La question dit « modifie-t-elle le calcul de la plus-value immobilière d'un loueur en meublé non professionnel ? ». |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k07 | La réponse présentait comme complète la liste des indemnités allouées par le juge : licenciement irrégulier ou sans cause réelle et sérieuse. L'article 80 duodecies, 1, 1° du CGI renvoie à d'autres indemnités du Code du travail, en particulier celle du licenciement nul (art. L. 1235-3-1) et l'indemnité forfaitaire de conciliation (art. L. 1235-1). Un étudiant qui citerait le licenciement nul aurait raison. | La réponse dit maintenant « celles allouées par le juge, **notamment** pour un licenciement irrégulier ou sans cause réelle et sérieuse ». La base reste Règles essentielles#2. | CGI, art. 80 duodecies, 1, 1° (connaissances générales, non recherché) |
| k09 et k10 | Doublon : toute la réponse de k10 (âge du crédirentier à l'entrée en jouissance, fraction invariable) était déjà dans la réponse de k09 (« fixée une fois pour toutes selon l'âge du crédirentier à l'entrée en jouissance »). | Les deux cartes sont fusionnées dans k09 : « fixée selon l'âge du crédirentier à la date d'entrée en jouissance, non l'âge atteint l'année d'imposition, puis invariable », suivie des quatre fractions. Base : Définitions#4 et Points de vigilance#4. **k10 est supprimée.** | Fiche, Définitions#4 et Points de vigilance#4 ; CGI, art. 158, 6 |
| k20 | La phrase « La limite est portée jusqu'à 21 400 €… » présentait comme permanente une dérogation temporaire. La majoration ne vise que les dépenses de rénovation énergétique payées entre le 1er janvier 2023 et le 31 décembre 2027 (Chiffres et seuils#5), ce que Règles essentielles#7 ne dit pas. La date ne pouvait pas être ajoutée, car une carte ne peut pas reposer sur un item millésimé. | La question est délimitée : « Hors majoration pour travaux de rénovation énergétique, comment s'impute un déficit foncier constaté au régime réel d'imposition des revenus fonciers ? ». La réponse s'en tient à la règle permanente : imputation sur le revenu global dans la limite de 10 700 € par an, hors intérêts d'emprunt ; report du surplus et des intérêts sur les revenus fonciers des dix années suivantes. | CGI, art. 156, I-3° ; fiche, Chiffres et seuils#5 |
| k27 | La question « À quelles conditions principales… » admettait d'autres réponses justes, absentes de la réponse : cession de la totalité des titres ou de plus de 50 % des droits, détention d'au moins 25 % des droits pendant cinq ans, cessation de toute fonction dans la société, qualité de PME. La fiche ne cite elle-même ses conditions qu'avec un « notamment ». | La question porte sur les seules durées : « Quelles durées le dirigeant de PME partant à la retraite doit-il respecter (détention des titres, fonctions de direction, départ en retraite) pour bénéficier de l'abattement fixe ? ». La réponse donne un an, cinq ans continus et deux ans avant ou après la cession. Elle ajoute « Ce ne sont pas les seules conditions de l'abattement ». | CGI, art. 150-0 D ter, I (connaissances générales) ; fiche, Règles essentielles#11 |
| k32 et k33 | La minoration du prix d'acquisition par les amortissements était présentée sans exception. Or l'article 150 VB en vigueur exclut certains amortissements de cette minoration et vise des résidences à public spécifique (art. L. 631-12 et L. 631-13 du CCH : étudiants, jeunes en formation, personnes de plus de 65 ans). | k33 commence par « En principe, le prix d'acquisition retenu est minoré… ». k32 dit « réintégration en principe des amortissements déduits ». Aucune exception n'est détaillée, car la fiche n'en mentionne pas. | CGI, art. 150 VB, III, issu de la loi n° 2025-127 du 14 février 2025, art. 84 (recherche n° 1) |

**Cartes contrôlées et maintenues** :

- **Chiffres stables** : plusieurs cartes citent des chiffres fixés par la loi, sans indexation annuelle, et chaque question porte sur la règle. Le contrat (section 8) les admet. Il s'agit de :
  - k04 (7 500 €, depuis 2022) ;
  - k06 (six fois le plafond annuel de la sécurité sociale, une règle et non un montant) ;
  - k09 (fractions de la rente selon l'âge) ;
  - k12, k13 et k35 (12,8 %) ;
  - k17 (6,8 points, inchangés par la LFSS 2026 selon la fiche) ;
  - k19 (15 000 €) ;
  - k20 et k21 (10 700 €) ;
  - k25 (50 000 €, de 2 % à 6 %) ;
  - k26 (500 000 €) ;
  - k28 et k29 (34 %, 87 % et 305 €) ;
  - k31 (50 % et 30 %).
- **Abattement fixe du dirigeant (k26)** : le dispositif est lui-même temporaire, puisqu'il vise les cessions réalisées jusqu'au 31 décembre 2031 (Ce qui a changé récemment#3, millésimé). La carte ne le présente pas comme permanent, et son échéance dépasse l'horizon des révisions. La carte est maintenue.
- **Doublons apparents** : plusieurs groupes de cartes portent sur des items voisins, mais chaque carte interroge un angle distinct :
  - k12, k13 et k35 : le PFU comme mode d'imposition, le prélèvement non libératoire comme acompte, puis la distinction entre les deux, qui est une confusion classique ;
  - k01 et k02 : le champ de la catégorie, puis la détermination du net imposable ;
  - k02, k05 et k34 : le net imposable, la renonciation à la déduction de 10 % et ses modalités ;
  - k20 et k21 : l'imputation du déficit, puis l'ordre d'imputation ;
  - k26 et k27 : l'avantage, puis ses conditions ;
  - k32 et k33 : le régime applicable, puis la modification du calcul.
- **k22 et l'exercice #18** : les deux portent sur la même règle, l'exonération après 22 ans pour l'impôt sur le revenu et après 30 ans pour les prélèvements sociaux. Le classement automatique range l'exercice #18 parmi les calculs, car son explication refait le cumul des abattements. La carte, elle, ne demande que les durées énoncées par Points de vigilance#2 et n'exige aucun calcul. Elle est maintenue.

## Recherches faites

1. **CGI, art. 150 VB, III : minoration du prix d'acquisition par les amortissements du loueur en meublé non professionnel** (domaines legifrance.gouv.fr et bofip.impots.gouv.fr).
   - Confirmé : dans la version en vigueur (Légifrance, LEGIARTI000051202577), le prix d'acquisition est en principe réduit des amortissements admis en déduction. Ceux qui se rattachent aux dépenses retenues au 4° du II du même article sont exclus de cette réduction.
   - Le texte vise aussi les résidences des articles L. 631-12 et L. 631-13 du CCH, destinées aux étudiants, aux moins de trente ans en formation ou en stage, aux apprentis et aux personnes de plus de 65 ans.
   - L'extrait n'a pas permis de lire l'alinéa en entier, ni de confirmer un renvoi à l'article L. 631-8 du CCH ou aux établissements pour personnes âgées.
   - Cette recherche a conduit à corriger k32 et k33.

## Points à reprendre dans la fiche

- **Ce qui a changé récemment#4 et Points de vigilance#5** : la minoration du prix d'acquisition par les amortissements est présentée sans exception. L'article 150 VB, III en vigueur exclut les amortissements liés aux dépenses retenues au 4° du II et vise les résidences des articles L. 631-12 et L. 631-13 du CCH (étudiants, jeunes en formation, plus de 65 ans). Une passe antérieure avait retiré l'exclusion des résidences de services faute de confirmation. Elle est à rétablir après lecture de l'alinéa sur Légifrance.
- **Règles essentielles#2** : la liste des indemnités exonérées en totalité est incomplète. L'article 80 duodecies, 1, 1° du CGI renvoie aussi aux articles L. 1235-1 (indemnité forfaitaire de conciliation), L. 1235-3-1 (licenciement nul) et L. 1235-11 à L. 1235-13 du Code du travail. Les indemnités de rupture conventionnelle collective sont elles aussi exonérées en totalité, mais il ne s'agit pas d'un licenciement. Ce point vient de connaissances générales et n'a pas été recherché : à vérifier.
- **Règles essentielles#7** : la majoration à 21 400 € est présentée sans son caractère temporaire, alors que les dates ne figurent que dans Chiffres et seuils#5, item millésimé. Il faudrait préciser « pour les dépenses payées entre le 1er janvier 2023 et le 31 décembre 2027 », ou déplacer la majoration dans « Chiffres et seuils ».
- **Règles essentielles#11** : les conditions de l'abattement fixe sont incomplètes, même si le « notamment » rend l'item exact. Il manque la cession de la totalité des titres ou de plus de 50 % des droits, la détention d'au moins 25 % des droits pendant cinq ans, la cessation de toute fonction dans la société et la qualité de PME. Faute de ces précisions, la carte k27 a dû être limitée aux durées. Ce point vient de connaissances générales : à vérifier.

## Classement des exercices

Classement automatique des exercices QCM, QCM multiples et classements (tri) du chapitre selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 13 |
| `calcul` (montant, taux, prorata, délai) | 8 |
| `chiffre` (rappel d'un chiffre millésimé) | 0 |
| **Total** | 21 |

Un désaccord a été relevé. L'exercice #18 est un QCM sur la durée de détention qui ouvre l'exonération des plus-values immobilières : 22 ans pour l'impôt sur le revenu, 30 ans pour les prélèvements sociaux. Une passe l'a classé `notion`, l'autre `calcul`, et c'est `calcul` qui a été retenu, son explication refaisant le cumul des abattements annuels. La règle reste révisée par la carte k22.

Seuls les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 34 cartes ci-dessus.
