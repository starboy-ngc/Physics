# Cartes de notions : ue4-06 (Impôts locaux, droits d'enregistrement, IFI et procédures fiscales)

*16 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-06.fiche.json` et d'elle seule. Elles respectent le contrat (section 8) : une question par carte, aucun calcul, aucun chiffre millésimé, et chaque carte s'appuie sur un ou deux items de fiche (`base`) dont elle recopie `src` et `url`.
2. **Relectures de fidélité** : trois passes successives ont contrôlé les cartes contre le texte (`t` et `cite`) des items de la fiche, sans aucune recherche. Elles ont vérifié que chaque carte dit ce que dit la fiche, sans plus, et qu'elle respecte la forme exigée par le contrat.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a vérifié les points suivants :
   - **Exactitude** : chaque carte est-elle juste au regard du droit en vigueur au 16 octobre 2026 (CGI, LPF, BOFiP, Constitution) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne dit pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle qu'attendrait un correcteur du DCG, et la seule réponse juste possible ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**
4. **Recherches** : 3 recherches, le maximum permis, limitées à legifrance.gouv.fr et bofip.impots.gouv.fr (détail plus bas). La première confirme une carte, la deuxième lève une incohérence signalée dans la fiche, la troisième corrige une référence de la fiche.

Validation : `node validate.js data/ue4/ue4-06.cartes.json` renvoie « ✓ data/ue4/ue4-06.cartes.json (cartes, 35 (8 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k36, sans k06) |
| Définition (`def`) | 8 (k01, k02, k13, k16, k19, k29, k30, k34) |
| Compréhension (`comp`) | 27 |
| Cartes corrigées par les relectures de fidélité | 10 (k05, k10, k14, k19, k21, k26, k28, k33, k34, k35) |
| Cartes ajoutées par les relectures de fidélité | 1 (k35) |
| Cartes corrigées par la relecture d'exactitude | 7 (k04, k05, k09, k10, k23, k24, k32) |
| Cartes supprimées | 1 (k06, par la relecture d'exactitude) |
| Cartes ajoutées par la relecture d'exactitude | 1 (k36) |

Le numéro k06 est désormais vacant. Conformément au contrat, les cartes ne sont pas renumérotées et l'identifiant ne sera pas réutilisé.

**Couverture de la fiche** :

- **Définitions** : 5 items sur 5 ont une carte (#0 k02, #1 k01, #2 k19, #3 k13, #4 k16 et k17).
- **Règles essentielles** : 17 des 18 items stables ont une carte. La relecture d'exactitude couvre désormais #13 (art. 1758 A) et la partie « défaut ou retard de déclaration » de #14 (art. 1728) avec k36.
- **Points de vigilance** : 8 items sur 8 ont une carte (k07, k24, k33, k27, k10, k21, k22, k31).

**Items de la fiche sans carte** :

- **Items millésimés**, qui ne peuvent pas donner de carte :
  - Règles essentielles#1 (CVAE : seuils et taux) ;
  - Chiffres et seuils#1 (taxe sur les salaires 2026) et #2 (taux maximal de la CVAE) ;
  - Ce qui a changé récemment#0, #1, #3 et #4 (lois de finances pour 2025 et 2026 : CVAE, droits de mutation d'immeubles, pacte Dutreil).
- **Chiffres et seuils#0** (barème de l'IFI) : l'item est stable, mais il ne contient que des tranches et des taux. Une carte serait du par-cœur sur des chiffres.
- **Ce qui a changé récemment#2** (nouvelle rédaction de l'art. 1447, I) : sa carte k06 a été supprimée (voir plus bas). Le contenu de la règle reste porté par k03, qui cite la rédaction en vigueur (« entités non dotées de la personnalité morale »).
- **Règles essentielles#3** (exonération de taxe foncière des constructions nouvelles) : le jeu atteint le plafond de 35 cartes. Aucune carte restante n'était assez faible pour lui céder sa place, et la règle est secondaire au regard du programme de l'UE 4.

## Corrections des relectures de fidélité

Trois passes ont eu lieu. Elles ont contrôlé 34, puis 35, puis 35 cartes, sans rien supprimer. Elles ont fait 12 corrections sur 10 cartes et ajouté k35.

| Passe | Cible | Problème | Correction |
|---|---|---|---|
| 1 | k10 | La question (« Quelles conditions un employeur doit-il remplir à la fois… ») donnait d'avance le point clé de la vigilance (Points de vigilance#4) : les deux conditions sont cumulatives. | « à la fois » est retiré de la question. La réponse ne change pas. |
| 1 | k19 | La réponse disait « interprétation formellement admise par l'administration ». Elle perdait la condition d'antériorité de Définitions#2 (« dès lors que cette interprétation avait été formellement admise »). | La réponse reprend la fiche : « …par un redevable de bonne foi, dès lors que cette interprétation avait été formellement admise par l'administration. » |
| 1 | k21 | La question était ambiguë. On pouvait y répondre « celle formellement admise » ou « les instructions publiées » (k19), au lieu de la règle visée (seule la dernière interprétation compte). | Nouvelle question : « Lorsque l'administration a successivement admis plusieurs interprétations d'un texte, laquelle le contribuable peut-il invoquer au titre de l'article L. 80 A du LPF ? » |
| 1 | k28 | La question (« Quelles majorations l'article 1729 prévoit-il… ») appelait un simple rappel de taux. | La question porte sur la règle : « Comment la majoration pour insuffisance de déclaration (CGI, art. 1729) est-elle graduée selon le comportement du contribuable ? » |
| 1 | k34 | Dans la réponse, « s'il le demande » n'avait pas d'antécédent. Il manquait aussi la condition de la citation de Règles essentielles#18 : préciser le montant ou les bases du dégrèvement. | Réponse réécrite : demande expresse dans la réclamation, avec le montant ou les bases du dégrèvement, garanties au-delà d'un montant fixé par décret, suspension de l'exigibilité et de la prescription. |
| 1 | k35 (ajout) | Règles essentielles#10 (durée des contrôles, LPF, art. L. 12 et L. 52) n'avait aucune carte. | Carte `comp` : trois mois pour une vérification sur place sous les limites du régime simplifié, six mois en cas de graves irrégularités. La réponse la distingue de l'examen contradictoire de la situation fiscale personnelle. |
| 2 | k26 | La question ne disait pas que les seuils de l'article L. 57 A sont des seuils de chiffre d'affaires. La réponse liait à tort le délai de soixante jours et la motivation du rejet. | Question : « …d'une entreprise vérifiée sous les seuils de chiffre d'affaires de l'article L. 57 A du LPF ? ». La réponse sépare les deux règles. |
| 2 | k34 | « dégrèvement demandé » résumait la citation de la fiche. | La réponse reprend les termes de la fiche : « dégrèvement auquel il estime avoir droit » (70 mots). |
| 2 | k35 | La question ne retenait que le chiffre d'affaires. La fiche vise « le chiffre d'affaires ou les recettes ». | « …lorsque le chiffre d'affaires ou les recettes de l'entreprise n'excèdent pas les limites du régime simplifié d'imposition ? » |
| 3 | k05 | La question était mal tournée : « Quel régime la CFE prévoit-elle… ». | « Comment la cotisation foncière des entreprises (CFE) s'applique-t-elle à une entreprise nouvellement créée ? » |
| 3 | k14 | L'abattement de 100 000 € par enfant et par ascendant, règle principale de Règles essentielles#7, n'avait aucune carte. | Ajout du contraste : « …alors que chaque enfant et chaque ascendant bénéficie d'un abattement de 100 000 € sur sa part. » |
| 3 | k26 | La réponse rattachait l'obligation de motiver un rejet aux seules entreprises sous les seuils de l'article L. 57 A, alors qu'elle vaut pour toute rectification contradictoire. | « …comme dans toute rectification contradictoire, si elle les rejette, sa réponse est motivée. » |
| 3 | k33 | La seconde phrase ne servait qu'à une anecdote datée (« en 2025 »). | Rappel du point de comparaison (droit commun) et du champ (impôts directs locaux et taxes annexes). Règles essentielles#17 ajouté en second item de base. |

Les passes 1 et 3 ont signalé une incohérence apparente entre Règles essentielles#13 (art. 1758 A, « portée à 20 % ») et #14 (art. 1728, 10 % dans les trente jours d'une mise en demeure). La relecture d'exactitude l'a levée (recherche n° 2).

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k06 (supprimée) | La carte demandait quelle modification la loi de finances pour 2026 avait apportée à l'art. 1447, I : « entités » au lieu de « sociétés » non dotées de la personnalité morale. C'était un doublon de k03, qui cite déjà la nouvelle rédaction, et du par-cœur sur un mot du texte. Elle laissait en outre croire à un élargissement de la liste des redevables, alors que l'administration y voit une clarification conforme à l'intention du législateur. Enfin, l'item de base attribue la mesure à l'art. 55 de la loi, alors que le BOFiP la rattache à l'art. 56. | Carte supprimée. Sa place sert à k36. | BOFiP ACTU-2026-00056 ; BOI-IF-CFE-10-10-20-20260429 (recherche n° 3) |
| k36 (ajout) | Règles essentielles#13 n'avait aucune carte, ni la partie « défaut ou retard de déclaration » de #14 (art. 1728), pourtant classique au DCG. Les relectures de fidélité s'en étaient abstenues à cause de l'incohérence apparente entre les deux items. | Carte `comp`, bases Règles essentielles#14 et #13. Q : « Comment la majoration pour défaut ou retard de déclaration prévue par l'article 1728 du CGI est-elle graduée ? ». R : « 10 % sans mise en demeure ou si la déclaration est déposée dans les trente jours d'une mise en demeure ; 40 % au-delà ; 80 % en cas de découverte d'une activité occulte. Pour la déclaration d'impôt sur le revenu, le taux applicable est celui de l'article 1758 A : 10 %, porté à 20 % en cas de dépôt dans les trente jours d'une mise en demeure. » | CGI, art. 1728, 1 et 1758 A ; BOI-CF-INF-20-10-10 ; ACTU-2017-00070 (recherche n° 2) |
| k24 | « Lorsque les déclarations n'ont pas été déposées… et que l'activité n'a pas été portée à la connaissance d'un organisme compétent, ou lorsqu'il s'agit d'une activité illicite » pouvait se lire ainsi : une activité illicite serait occulte même si les déclarations ont été déposées. Or l'article L. 169 exige dans tous les cas le défaut de dépôt des déclarations, puis l'une des deux conditions. | « Lorsque le contribuable n'a pas déposé ses déclarations dans le délai légal et, soit n'a pas porté son activité à la connaissance d'un organisme compétent, soit s'est livré à une activité illicite. » La seconde phrase ne change pas. | LPF, art. L. 169, 2e alinéa (« et soit … soit … ») ; connaissance du texte, non recherché |
| k10 | « Quelles conditions un employeur doit-il remplir pour être dispensé de la taxe sur les salaires ? » n'était pas délimité. D'autres réponses justes étaient possibles : exonérations de certains employeurs publics, franchise lorsque le montant annuel de la taxe est faible. | « Au regard de la TVA, à quelles conditions un employeur est-il dispensé de la taxe sur les salaires ? ». La réponse ne change pas. | CGI, art. 231, 1 |
| k09 | La réponse ne donnait que la fraction de rémunérations retenue selon le rapport d'assujettissement. Elle ne disait ni que l'assiette, ce sont les rémunérations versées, ni que l'employeur qui n'est pas du tout soumis à la TVA est taxé sur la totalité. | « Les rémunérations versées, pour la fraction correspondant au rapport entre le chiffre d'affaires non soumis à la TVA et le chiffre d'affaires total, soit leur totalité pour un employeur qui n'est pas du tout soumis à la TVA. » | CGI, art. 231, 1 ; fiche, Règles essentielles#4 |
| k23 | La question demandait le délai de reprise sans réserve. La parenthèse « (dixième année en cas d'activité occulte) » présentait ce cas comme la seule exception, alors que l'article L. 169 en prévoit d'autres (comptes ou trusts étrangers non déclarés, par exemple). | Question : « En règle générale, jusqu'à quand… ? ». Réponse : « (dixième année, notamment, en cas d'activité occulte) ». | LPF, art. L. 169 |
| k32 | « la réclamation préalable qui ouvre tout contentieux fiscal » englobait le contentieux du recouvrement, qui obéit à d'autres délais (LPF, art. L. 281). La réponse attendue est le délai de droit commun de la réclamation contre une imposition. | « Dans quel délai de droit commun le contribuable doit-il présenter la réclamation préalable par laquelle il conteste une imposition ? ». La réponse ne change pas. | LPF, art. L. 190, R*196-1 et L. 281 |
| k05 | « …à une entreprise nouvellement créée » appelait une réponse ouverte : base au 31 décembre de l'année de création, exonérations de zone… La règle visée porte sur deux années précises. | « Comment la cotisation foncière des entreprises (CFE) s'applique-t-elle à une entreprise l'année de sa création et l'année suivante ? ». La réponse ne change pas. | CGI, art. 1478, II |
| k04 | « c'est-à-dire l'avant-dernière année » ne disait pas de quelle année : la période de référence est l'avant-dernière année précédant celle de l'imposition. | « …c'est-à-dire l'avant-dernière année précédant celle de l'imposition. » | CGI, art. 1467 A |

**Cartes contrôlées et maintenues** :

- **Prise de position lors d'un contrôle (k20)** : la recherche n° 1 confirme que la garantie de l'article L. 80 A couvre la position prise sur les points du contrôle, « y compris tacitement en ne rectifiant pas certains points examinés » (intitulé du BOI-CF-PGR-30-25). La carte est exacte.
- **CFE (k03)** : la recherche n° 3 confirme que l'article 1447, I vise, depuis le 21 février 2026, « les personnes physiques ou morales, les entités non dotées de la personnalité morale ou les fiduciaires ».
- **Autres cartes de fond** : les cartes suivantes sont conformes aux textes en vigueur.
  - k01 (article 34 de la Constitution) ; k02 (composition de la CET, abrogation de l'article 1447-0 au 1er janvier 2030).
  - k07, k08 (taxes foncières : redevable, base).
  - k11, k12 (droits sur les cessions de droits sociaux et de fonds de commerce).
  - k13 à k18 (droits de mutation à titre gratuit, conjoint et partenaire de PACS, rappel des donations, IFI).
  - k19, k21, k22, k31 (garantie contre les changements de doctrine).
  - k25 à k27 (rectification contradictoire, délai de soixante jours de l'article L. 57 A).
  - k28 à k30 (majorations de l'article 1729, intérêt de retard, abus de droit).
  - k33, k34, k35 (réclamation contre un impôt local, sursis de paiement, durée des contrôles).
- **Doublons apparents** : plusieurs paires de cartes portent sur le même item, mais chacune interroge un angle distinct.
  - k03, k04 et k05 : redevables, base et création d'entreprise (CFE) ;
  - k09 et k10 : assiette et conditions de dispense de la taxe sur les salaires ;
  - k14 et k15 : exonération du conjoint et abattement en ligne directe, puis rappel des donations ;
  - k16 et k17 : définition de l'IFI, puis son champ territorial ;
  - k25 et k26 : délai de réponse du contribuable, puis silence de l'administration ;
  - k28 et k36 : insuffisance de déclaration (art. 1729), puis défaut ou retard (art. 1728) ;
  - k32 et k33 : réclamation de droit commun, puis réclamation contre un impôt local.
- **Chiffres stables** : chaque chiffre cité fait partie d'une règle et la question porte sur la règle, ce que le contrat (section 8) admet. Sont dans ce cas :
  - les taux de 0,1 %, 3 % et 5 % et l'abattement de 23 000 € sur les droits sociaux (k11) ;
  - l'abattement de 100 000 € et le délai de quinze ans (k14, k15) ;
  - le seuil de 1 300 000 € et l'abattement de 30 % (k16, k18) ;
  - les taux de 10 %, 20 %, 40 % et 80 % (k28, k36) ;
  - le taux de 0,20 % par mois (k29) ;
  - les délais de trente et soixante jours, trois et six mois (k25, k26, k35).

  Aucune carte ne cite un barème ou un seuil millésimé (CVAE, taxe sur les salaires, barème de l'IFI).

## Recherches faites

1. **Prise de position tacite lors d'un contrôle** (domaines legifrance.gouv.fr et bofip.impots.gouv.fr ; LPF, art. L. 80 A, et BOI-CF-PGR-30-25-20200311).
   - Confirmé : la garantie couvre la position prise sur les points du contrôle, y compris tacitement, en ne rectifiant pas certains points examinés. Elle s'applique aux contrôles dont les avis sont adressés à compter du 1er janvier 2019.
   - Le BOFiP ajoute deux précisions. La garantie ne vaut que pour les points couverts par l'avis et réellement examinés, l'administration disposant de toutes les informations utiles. Elle suppose aussi que le contribuable ait exposé toute sa situation.
   - Conséquence : k20 est maintenue.
2. **Articulation des articles 1758 A et 1728 du CGI** (domaines bofip.impots.gouv.fr et legifrance.gouv.fr ; BOI-CF-INF-20-10-10, ACTU-2017-00070, CGI, art. 1758 A et 1728).
   - Confirmé : depuis le 1er janvier 2017 (loi n° 2016-1918 du 29 décembre 2016, art. 20), la majoration de l'article 1758 A pour la déclaration d'impôt sur le revenu est de 10 %. Elle est portée à 20 % en cas de dépôt dans les trente jours d'une mise en demeure.
   - Elle est exclusive de la majoration de 10 % du a du 1 de l'article 1728 (art. 1758 A, III). Elle ne s'applique pas quand jouent les b et c du 1 de l'article 1728 (40 % et 80 %) ou l'article 1729.
   - Avant 2017, les deux majorations de 10 % se cumulaient.
   - Conséquence : Règles essentielles#13 et #14 ne se contredisent pas ; #13 décrit le régime propre à l'impôt sur le revenu. La carte k36 est ajoutée.
3. **Rédaction de l'article 1447, I du CGI** (domaines legifrance.gouv.fr et bofip.impots.gouv.fr ; article 1447 en vigueur, BOI-IF-CFE-10-10-20-20260429, ACTU-2026-00056).
   - Confirmé : depuis le 21 février 2026, le texte vise les « entités non dotées de la personnalité morale » au lieu des « sociétés ».
   - La modification vient de l'article **56** de la loi n° 2026-103 du 19 février 2026, et non de l'article 55.
   - Selon le BOFiP, elle clarifie le champ de la CFE sans l'étendre. Exemples d'entités visées : organismes de copropriété, régies sans personnalité morale, autorités administratives indépendantes, fondations universitaires, fonds d'investissement.
   - Conséquence : k03 est maintenue ; k06 est supprimée.

## Points à reprendre dans la fiche

- **Ce qui a changé récemment#2 (champ de la CFE)** :
  - le titre et `src` attribuent la nouvelle rédaction de l'article 1447, I à l'article 55 de la loi n° 2026-103. Le BOFiP (ACTU-2026-00056) la rattache à l'**article 56** (recherche n° 3) ;
  - l'item devrait préciser que l'administration y voit une clarification, sans extension du champ de la CFE ;
  - l'URL Légifrance de la version en vigueur depuis le 21 février 2026 est LEGIARTI000053544997, alors que la fiche cite LEGIARTI000023380872 (même remarque pour Règles essentielles#0).
- **Règles essentielles#13 et #14 (majorations)** : l'incohérence signalée par les relectures de fidélité n'en est pas une. Il faudrait l'écrire dans la fiche. Pour la déclaration d'impôt sur le revenu, la majoration de l'article 1758 A (10 %, ou 20 % en cas de dépôt dans les trente jours d'une mise en demeure) **remplace** celle de 10 % du a du 1 de l'article 1728 (art. 1758 A, III, depuis le 1er janvier 2017 ; recherche n° 2). L'item #14 pourrait le dire en une incise.
- **Points de vigilance#1 (activité occulte)** : la formule « lorsque les déclarations n'ont pas été déposées dans le délai légal et que l'activité n'a pas été portée à la connaissance d'un organisme compétent, ou lorsqu'il s'agit d'une activité illicite » est à reprendre sur le texte de l'article L. 169. Le texte dit : le contribuable « n'a pas déposé dans le délai légal les déclarations qu'il était tenu de souscrire **et soit** n'a pas fait connaître son activité […], **soit** s'est livré à une activité illicite ». Ce point vient de la connaissance du texte et n'a pas été recherché. La carte k24 est corrigée.
- **Règles essentielles#6 (fonds de commerce)**, à vérifier : l'article 719 semble préciser que l'assiette s'entend « à la seule exception des marchandises neuves garnissant le fonds ». Cette exclusion avait été retirée de la fiche faute de texte dans les résultats de recherche. Ce point vient de la connaissance du texte et n'a pas été recherché. La carte k12, qui énumère seulement les éléments compris dans l'assiette, reste exacte.
- **Règles essentielles#12 (prise de position lors d'un contrôle)**, facultatif : on peut ajouter les limites que pose le BOFiP (BOI-CF-PGR-30-25 ; recherche n° 1). La garantie ne couvre que les points compris dans l'avis et réellement examinés, l'administration disposant de toutes les informations utiles, et elle suppose que le contribuable a exposé toute sa situation.

## Classement des exercices

Classement automatique des exercices QCM, QCM multiples et classements (tri) du chapitre selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 22 (18 QCM, 3 QCM multiples, 1 classement) |
| `calcul` (montant, taux, prorata, délai) | 3 (QCM) |
| `chiffre` (rappel d'un chiffre millésimé) | 1 (QCM) |
| **Total** | 26 |

Les classements concordent : aucun désaccord n'a eu à être tranché. Les 9 exercices de calcul du chapitre (type `calc`) sont de nature `calcul` par construction et n'entrent pas dans ce classement.

Seuls les 22 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
