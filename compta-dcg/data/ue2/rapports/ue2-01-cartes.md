# Cartes de notions : ue2-01 (L'entreprise en société : contrat, personnalité morale, associés et dirigeants)

16 octobre 2026. Fichier : `data/ue2/ue2-01.cartes.json`. Fiche de référence : `data/ue2/ue2-01.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 34 cartes (k01 à k34) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relectures de fidélité.** Trois passes successives ont contrôlé les cartes au regard de la seule fiche, sans recherche web. Elles ont corrigé 17 cartes différentes (k05, k06, k08, k10, k11, k12, k14, k15, k17, k18, k22, k25, k27, k29, k31, k34 et k35, certaines à plusieurs reprises), ajouté k35, et retiré k36, créée puis abandonnée par une passe interrompue. Le détail figure plus bas.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 16 octobre 2026 (Code civil, Code de commerce, livre des procédures fiscales, jurisprudence de la Cour de cassation). Il a aussi vérifié que chaque question n'appelle qu'une seule réponse juste, et il a recherché les doublons et les cartes sans intérêt. Bilan : 6 cartes corrigées (k01, k03, k15, k20, k31, k34), 1 suppression (k32), aucun ajout.
4. **Recherches.** 3 recherches WebSearch sur les 3 autorisées, toutes sur legifrance.gouv.fr, consacrées à la réforme des nullités (ordonnance n° 2025-229 du 12 mars 2025) : triple test, causes de nullité de la société, prescription.

`node validate.js data/ue2/ue2-01.cartes.json` : ✓ (34 cartes, 6 déf.).

## Bilan

- **34 cartes** : 6 de définition (`def`) et 28 de compréhension (`comp`). Les identifiants k32 (supprimée par la relecture d'exactitude) et k36 (retirée lors des relectures de fidélité) sont libres et ne doivent pas être réutilisés.
- Chaque item des sections « Définitions » (#0 à #5), « Règles essentielles » (#0 à #14) et « Ce qui a changé récemment » (#0 à #4) a au moins une carte.
- **Items de la fiche sans carte :**
  - **Chiffres et seuils#4** (droit de partage de 2,50 %) : une carte se réduirait au rappel d'un taux fiscal, relevé plusieurs fois ces dernières années.
  - **Points de vigilance#4** (exclusion des pactes d'associés, traités en UE 1 du DSCG) : consigne de programme, pas une règle de droit.
- **Contenu couvert en partie :** Points de vigilance#0 (abus de minorité) n'est plus couvert que pour sa sanction (k33). La carte sur ses conditions (k32) a été supprimée, car la fiche les donne de façon incomplète (voir « Points à reprendre dans la fiche »).

## Corrections des relectures de fidélité (fiche seule)

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | k05 | Type « def » pour une question de moment (« À partir de quand… ? ») ; « droit des contrats et obligations » au lieu de « droit applicable aux contrats et obligations ». | Type « comp » ; règle générale introduite par « Plus largement » ; formule de Définitions#2 reprise. |
| 1 | k08 | « Éléments d'identification » des statuts : classement absent de la fiche, qui coupait la liste de l'art. 1835 en deux. | Question sur toutes les mentions des statuts ; réponse : la liste complète et l'exigence d'un écrit. |
| 1 | k35 (ajoutée) | La seconde moitié de Règles essentielles#13 (clause contraire à une disposition impérative non sanctionnée par la nullité) n'avait pas de carte. | Carte `comp` : la clause est réputée non écrite, la société n'est pas annulée. |
| 2 | k08 | Une passe interrompue avait découpé la liste de l'art. 1835 entre k08 et une nouvelle k36, et supprimé k35 pour rester sous le plafond. | Liste complète rétablie dans k08. |
| 2 | k10 | Le recto (« actes accomplis au nom d'une société ») suggérait la réponse. | « Qui est tenu des obligations nées des actes passés pour une société en formation, avant son immatriculation ? » |
| 2 | k15 | Les statuts peuvent déroger à la répartition légale : « ça dépend des statuts » restait une réponse juste. | Question limitée à l'absence de dérogation statutaire. |
| 2 | k18 | Charge de la preuve non dite ; « limitant ses pouvoirs » ambigu. | « à moins qu'elle ne prouve… » ; « les clauses statutaires limitant les pouvoirs du gérant sont inopposables aux tiers ». |
| 2 | k27 | Reprenait le contenu de k35, alors supprimée ; doublon une fois k35 rétablie. | Réponse recentrée sur les deux seules causes de nullité de la société. |
| 2 | k36 (retirée) | Créée par la passe interrompue pour une moitié de la liste de l'art. 1835 ; sa création avait servi à supprimer k35. | Retirée ; k35 rétablie sous son identifiant. |
| 2 | k11, k14, k29, k31, k34 | Corrections de la passe interrompue (« Trois voies », questions de k29 et k31, phrase sur la lecture des statuts). | Vérifiées et conservées. |
| 3 | k06 | Question générale, alors que la règle (nature, numéraire, industrie) est celle de l'art. 1843-3. | « Selon l'article 1843-3 du Code civil, … ? » |
| 3 | k08 | Question ouverte aux mentions propres à certaines formes sociales. | « Selon l'article 1835 du Code civil, … ? » |
| 3 | k12 | La reprise présentée comme le but de l'acte, alors que la commune intention porte sur deux points. | « …que l'acte soit conclu au nom ou pour le compte de la société en formation et que celle-ci puisse ensuite reprendre les engagements souscrits ». |
| 3 | k17 | Cadre non nommé : d'autres formes sociales connaissent d'autres sanctions du défaut de libération. | « Selon le Code civil, … ? » |
| 3 | k22 | La règle ne vaut pas pour les formes qui admettent l'associé unique (EURL, SASU). | « Selon l'article 1844-5 du Code civil, … ? » |
| 3 | k25 | La dissolution d'une société à associé unique personne morale entraîne une transmission universelle sans liquidation. | « Lorsqu'une société dissoute est mise en liquidation, … ? » |
| 3 | k35 | Le recto présentait la règle du « réputé non écrit » comme une nouveauté de 2025. | Rattachement temporel retiré du recto. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k01 | La réponse paraphrasait l'article 1832 (« l'économie qui en résulte ») alors que le texte dit « qui pourra en résulter », formule citée par Définitions#0. | « …en vue de partager le bénéfice ou de profiter de l'économie qui pourra en résulter ». | C. civ., art. 1832 (citation de Définitions#0) |
| k03 | « Uniquement sur le patrimoine professionnel » : le cantonnement n'est pas absolu. Hors de la fiche, la loi permet au fisc et aux organismes sociaux d'agir sur les deux patrimoines (impôt sur le revenu, prélèvements sociaux, taxe foncière de la résidence principale ; fraude ou inobservation grave et répétée des obligations fiscales ou sociales). | « <b>En principe, sur le seul patrimoine professionnel</b>, sauf sûreté conventionnelle ou renonciation. » Les exceptions ne sont pas écrites sur la carte, faute d'appui dans la fiche ; point 1 à reprendre. | C. com., art. L. 526-22 ; LPF, art. L. 273 B ; CSS, art. L. 133-4-7 (connaissance du relecteur, non vérifiée par recherche) |
| k15 | Pour les actions de SA, la règle est différente : le vote appartient à l'usufruitier dans les assemblées ordinaires et au nu-propriétaire dans les assemblées extraordinaires. Une personne qui pense à une SA ou à une SAS pouvait donner cette réponse. | Question délimitée : « Selon l'article 1844 du Code civil, en l'absence de dérogation statutaire, à qui appartient le droit de vote attaché à des parts sociales démembrées ? ». Réponse inchangée. | C. civ., art. 1844, al. 3 et 4 ; C. com., art. L. 225-110 |
| k20 | La question visait la responsabilité « envers la société ou les tiers ». Envers les tiers, la jurisprudence n'engage la responsabilité personnelle du gérant que pour une faute séparable de ses fonctions (faute intentionnelle d'une particulière gravité, incompatible avec l'exercice normal des fonctions). Une simple faute de gestion ne suffit pas, comme l'enseignent la leçon et l'exercice n° 19 du chapitre. | Question limitée à la responsabilité envers la société : « Pour quels faits les gérants de SARL engagent-ils leur responsabilité civile envers la société ? ». Réponse inchangée ; point 2 à reprendre. | C. com., art. L. 223-22 ; Cass. com., 20 mai 2003, n° 99-17.092 (Seusse) |
| k31 | Dans les sociétés commerciales, la prorogation est une modification des statuts décidée selon les règles du Code de commerce (assemblée générale extraordinaire en SA, majorité de l'article L. 223-30 en SARL). La règle « unanimité, ou majorité prévue pour la modification des statuts si ceux-ci le prévoient » est celle du Code civil. | Question délimitée : « Selon l'article 1844-6 du Code civil, comment les associés décident-ils de proroger la société avant l'expiration de sa durée ? ». Réponse inchangée. | C. civ., art. 1834 et 1844-6 ; C. com., art. L. 223-30 et L. 225-96 |
| k32 (supprimée) | Conditions de l'abus de minorité incomplètes. La carte les réduisait à une attitude « contraire à l'intérêt général de la société » qui vise « à favoriser son propre intérêt ». L'arrêt exige une attitude qui interdit la réalisation d'une opération essentielle pour la société, adoptée dans l'unique dessein de favoriser ses propres intérêts au détriment de l'ensemble des autres associés. Une personne qui apprend la carte donnerait à l'examen une définition fausse par défaut. La fiche ne permet pas de la compléter. | Carte supprimée ; l'identifiant k32 reste libre. La sanction (arrêt Flandin) reste couverte par k33. Point 3 à reprendre ; une carte pourra être recréée sous un nouvel identifiant une fois l'item complété. | Cass. com., 9 mars 1993, n° 91-14.685 (Flandin) ; Cass. com., 15 juillet 1992, n° 90-17.216 (Six) |
| k34 | « La société civile continue avec les héritiers ou légataires, sauf clause statutaire d'agrément » : l'article 1870 admet aussi la clause de dissolution et la continuation avec les seuls associés survivants. | « …sauf clause contraire des statuts, comme une clause d'agrément ». | C. civ., art. 1870 |

Les autres cartes ont été contrôlées sans changement : k02, k04 à k14, k16 à k19, k21 à k30, k33 et k35. Les règles de la réforme des nullités (k27 à k30, k35) ont été confirmées par les recherches.

## Recherches faites

3 recherches sur les 3 autorisées, toutes avec `allowed_domains` : legifrance.gouv.fr.

1. Requête « article 1844-12-1 code civil nullité décision grief influence sur le sens de la décision conséquences excessives intérêt social ».
   - **Confirmé.** L'article 1844-12-1, issu de l'ordonnance n° 2025-229 et en vigueur depuis le 1er octobre 2025, ne permet de prononcer la nullité d'une décision que si le demandeur justifie d'un grief, si l'irrégularité a eu une influence sur le sens de la décision et si les conséquences de la nullité pour l'intérêt social ne sont pas excessives. Le rapport au Président de la République parle de « triple test ». Certains régimes spéciaux sont écartés, d'où la réserve « sauf lorsqu'un texte en écarte l'application ». L'ancien article 1844-12 est abrogé.
   - Effet : k28 confirmée.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051317310/2025-10-27 ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316022
2. Requête « article 1844-10 code civil "ne peut résulter que" incapacité de tous les fondateurs nombre minimal de deux associés ordonnance 2025-229 ».
   - **Confirmé.** « La nullité de la société ne peut résulter que de l'incapacité de tous les fondateurs ou de la violation des dispositions fixant un nombre minimal de deux associés. » « Sauf si la loi en dispose autrement, la violation des statuts ne constitue pas une cause de nullité. » Le nouvel article 1844-10-1 prévoit que la nullité de tous les apports entraîne la dissolution de la société.
   - Effet : k27, k30 et k35 confirmées.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051322322 ; https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051317279/2025-04-29
3. Requête « article 1844-14 code civil actions en nullité de la société se prescrivent par deux ans à compter du jour où la nullité est encourue ».
   - **Confirmé.** Le délai passe de trois à deux ans pour les actions en nullité de la société, des apports et des décisions postérieures (version de trois ans en vigueur du 1er juillet 1978 au 1er octobre 2025). La réserve des règles spéciales (fusion, scission, modification du capital) est maintenue.
   - Effet : k29 confirmée.
   - Sources : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006444195 ; https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051316108

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Définitions#1** (entrepreneur individuel). Les seules exceptions citées au cantonnement des créanciers professionnels sont la sûreté conventionnelle et la renonciation. Il manque les exceptions fiscales et sociales, à vérifier avant d'écrire. Selon le LPF, art. L. 273 B, l'impôt sur le revenu, les prélèvements sociaux et la taxe foncière de la résidence principale sont recouvrables sur les deux patrimoines, ainsi que les impositions en cas de manœuvres frauduleuses ou d'inobservation grave et répétée des obligations fiscales. Le CSS, art. L. 133-4-7, prévoit une règle comparable pour les cotisations sociales. Une fois l'item complété, k03 pourra citer ces exceptions au lieu de « En principe ».
2. **Règles essentielles#9** (responsabilité civile des gérants). L'item ne dit pas qu'envers les tiers, la responsabilité personnelle du gérant suppose une faute séparable de ses fonctions (Cass. com., 20 mai 2003, n° 99-17.092). La leçon et l'exercice n° 19 le disent. C'est pour cela que la question de k20 a été limitée à la responsabilité envers la société.
3. **Points de vigilance#0** (abus de minorité). La définition est incomplète, comme l'avaient déjà signalé les trois relectures de fidélité. L'arrêt Flandin (comme l'arrêt Six du 15 juillet 1992) vise une attitude « contraire à l'intérêt général de la société en ce qu'elle interdit la réalisation d'une opération essentielle pour celle-ci, et dans l'unique dessein de favoriser [ses] propres intérêts au détriment de l'ensemble des autres associés ». La relecture d'exactitude a supprimé k32 pour cette raison. Il faut aussi vérifier, sur le texte de l'arrêt, la phrase « le caractère systématique du blocage ne suffit pas ».
4. **Règles essentielles#6** (retard de libération). `src` indique « C. civ., art. 1843-3, al. 4 ». La règle des intérêts de plein droit paraît figurer à l'alinéa 5 : l'alinéa 3 traite de l'apport en propriété, l'alinéa 4 de l'apport en jouissance et l'alinéa 6 de l'apport en industrie. Point à vérifier. La carte k17 recopie la référence de l'item.
5. **Chiffres et seuils#0** (prorogation). L'item présente la règle de l'article 1844-6 sans dire que, dans la SA et la SARL, la prorogation suit les règles de modification des statuts du Code de commerce. La question de k31 a été limitée au Code civil pour cette raison.
6. **Chiffres et seuils#3** (rappel des relectures de fidélité). L'url se termine par `/2000-09-21` : elle renvoie à une version datée de l'article L. 223-23, et non à la version consolidée. k21 la recopie.
7. **Chiffres et seuils#4** (rappel des relectures de fidélité). Le droit de partage de 2,50 % est marqué « stable », alors que ce taux a été relevé plusieurs fois. Il faudrait le marquer millésimé.

## Classement des exercices

Le classement automatique porte sur les 25 exercices QCM, QCM multiples et classements du chapitre (20 QCM, 4 QCM multiples, 1 classement) :

| nature | nombre |
|---|---|
| notion | 25 |
| calcul | 0 |
| chiffre | 0 |

Aucun désaccord entre les classements. Les 25 exercices entrent donc dans les révisions espacées, avec les 34 cartes. Les 3 exercices de calcul du chapitre (n° 5 et 6 : part de bénéfice d'un associé ; n° 21 : somme reçue par un associé à la liquidation) sont des exercices de type `calc`, hors du champ du classement et des révisions espacées. Le seul chiffre présent dans un exercice de nature notion, la durée maximale de 99 ans (n° 22), est stable et fait partie de la règle.
