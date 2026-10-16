# Cartes de notions : ue10-06 (Capitaux propres : constitution, augmentation, réduction, affectation)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-06.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). `src` et `url` sont copiés depuis le premier de ces items.
2. **Premier cycle de relecture** (commit 95746d3). Ce cycle comprenait une relecture de fidélité puis une relecture d'exactitude, avec 3 recherches restreintes à anc.gouv.fr. Il a supprimé k25, doublon de k24 : l'identifiant k25 reste vide, sans renumérotation. Il a aussi retouché k03, k13, k16, k17, k20, k21, k24 et k31.
3. **Relecture de fidélité (reprise).** Une passe interrompue avait réintroduit dans les cartes des éléments que la relecture d'exactitude avait écartés. La nouvelle relecture de fidélité a contrôlé les 34 cartes, corrigé les cartes concernées et ajouté k36. Elle n'a fait aucune recherche web.
4. **Relecture d'exactitude (reprise).** Une seconde relecture, indépendante, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, Code civil, CGI et BOFiP, PCG modifié par les règlements ANC n° 2018-01, 2022-06 et 2024-07 ;
   - l'ambiguïté pédagogique : une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a fait une seule recherche, restreinte à legifrance.gouv.fr (voir « Recherches »).
5. **Validation.** `node validate.js data/ue10/ue10-06.cartes.json` : ✓ (35 cartes, dont 6 déf.).

## Bilan

- **Nombre de cartes : 35.** La reprise a ajouté k36. L'identifiant k25 reste vide.
- **Répartition : 6 cartes `def` et 29 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 5 items de « Définitions » ont chacun au moins une carte.
  - 18 des 19 « Règles essentielles » servent de base à au moins une carte. Règles essentielles#10 (réduction non motivée par des pertes) en fonde trois, qui ne se recouvrent pas :
    - k19 : qui peut former opposition, et dans quel délai ;
    - k20 : ce qui distingue cette réduction de la réduction motivée par des pertes ;
    - k36 : le rachat d'actions en vue de leur annulation.
  - Les 6 « Points de vigilance » sont tous couverts.
  - « Chiffres et seuils » : les items #0, #1 et #2 sont couverts (k11, k05, k21).
  - « Ce qui a changé récemment » : les items #0, #1, #3 et #4 sont couverts (k22, k17, k34, k03).
- **Items de fiche sans carte :**
  - Règles essentielles#2 (augmentation de capital en numéraire dans la SA). Son contenu est entièrement porté par k11 (Chiffres et seuils#0, Points de vigilance#0) et par k12 (Points de vigilance#1).
  - Chiffres et seuils#3 (PFU et seuils de dispense, « millésimé 2025 »).
  - Chiffres et seuils#4 (taux limite des intérêts de comptes courants, « millésimé 2026 »).
  - Ce qui a changé récemment#2 (prélèvements sociaux 2026, « millésimé 2026 »).

  Les trois derniers sont millésimés : le contrat leur interdit de donner une carte.
- **Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé.**
  - Les chiffres qui figurent sur les cartes sont stables et font partie d'une règle : fractions de libération (1/5, 1/2, 1/4), 30 000 € (D. 223-6-1, inchangé depuis 2010), 1 % du total du bilan (décret n° 2023-657), 5 % et 10 % de la réserve légale, délais légaux.
  - Les dates citées sont celles de textes ou de leur entrée en vigueur.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la relecture de fidélité s'arrête au milieu de la ligne k31. Les lignes marquées (*) ont été reconstituées par comparaison du fichier avec le commit 95746d3.

| cible | problème | correction |
|---|---|---|
| ue10-06-k03 | Une passe interrompue avait réintroduit au verso la date d'application « exercices ouverts à compter du 1er janvier 2026 ». La fiche porte bien cette date, mais la relecture d'exactitude précédente l'a contestée : une recherche sur anc.gouv.fr donne le 1er janvier 2025. La réponse n'en a pas besoin. | Date retirée. Nouveau verso : « Les « autres fonds propres », que le règlement distingue des dettes. Comme les subventions d'investissement et les provisions réglementées, ils sont exclus de la situation nette. » La base reste [Ce qui a changé récemment#4, Définitions#0]. |
| ue10-06-k06 | Le verso oubliait que les fondateurs se dispensent du commissaire aux apports « sous leur responsabilité ». Il omettait aussi « déjà » (actifs déjà évalués à la juste valeur dans les six mois). À 70 mots, il était à la limite. | Verso réécrit en 68 mots, dans cet ordre : le rôle (apprécier, sous sa responsabilité, la valeur des apports en nature et des avantages particuliers), la désignation (unanimité des fondateurs, à défaut le juge), puis la dispense « sous leur responsabilité » dans les deux cas de L. 225-8-1, avec « déjà évalués ». |
| ue10-06-k16 | Deux versions de la question posaient problème. Celle de la passe interrompue admettait une autre réponse juste, « en charges », que le verso ne donnait pas en premier. Celle de HEAD (« plutôt que de les comptabiliser en charges ») présentait la comptabilisation directe en charges comme une option, ce que la fiche ne dit pas. | Nouvelle question : « Selon l'article 212-9 du PCG, à quels postes du bilan une société peut-elle inscrire ou imputer ses frais d'augmentation de capital ? ». Elle n'appelle qu'une réponse. Verso : « À l'actif en frais d'établissement, ou par imputation sur les primes d'émission et de fusion ; en cas d'insuffisance de la prime, ils sont comptabilisés en charges », puis le piège de la « méthode préférentielle » (règlement ANC n° 2018-01). |
| ue10-06-k18 | Aucune carte ne couvrait la règle propre à la SARL de Règles essentielles#9 (réduction autorisée par les associés aux conditions de modification des statuts, L. 223-34). | Phrase ajoutée au verso : « Dans la SARL, elle est autorisée par les associés statuant aux conditions de modification des statuts. » La question (principe d'égalité des actionnaires dans la SA) ne change pas. 43 mots. |
| ue10-06-k31 | La passe interrompue avait remis l'intitulé « 442 État – impôts et taxes recouvrables sur des tiers ». C'est bien le texte de la fiche, mais la relecture d'exactitude l'a jugé périmé : le compte 442 regroupe aujourd'hui les impôts recouvrés pour le compte de l'État (subdivisions 4421 à 4423). | Intitulé retiré, réponse limitée à ce qui est sûr : « Au crédit du compte 442. » (*) La suite reprend l'item de la fiche : le prélèvement est opéré par l'établissement payeur et versé au Trésor dans les quinze premiers jours du mois qui suit le paiement des revenus ; il est imputable sur l'impôt sur le revenu, l'excédent étant restitué. |
| ue10-06-k33 (*) | La question ne disait pas qui verse les intérêts. Le verso omettait le contrôle « compte par compte » de Règles essentielles#17. | Question : « À quelles conditions les intérêts versés par une société sur les comptes courants d'associés sont-ils, en principe, fiscalement déductibles ? ». Verso complété par « et le contrôle s'opère compte par compte ». |
| ue10-06-k35 (*) | La question était mal construite (« quelle condition exige une augmentation… »). Le verso, sur la SARL, s'écartait du texte de la fiche (« l'incorporation est décidée »). | Question : « … à quelle condition une augmentation de capital par majoration du nominal des actions est-elle possible… ? ». Le verso reprend la fiche : « la décision d'incorporer bénéfices ou réserves est prise par les associés représentant au moins la moitié des parts ». |
| ue10-06-k36 (*, ajoutée) | Aucune carte ne couvrait le rachat d'actions en vue de leur annulation (L. 225-207, Règles essentielles#10). | Carte ajoutée : quelle opération l'assemblée qui décide une réduction non motivée par des pertes peut autoriser le conseil d'administration ou le directoire à réaliser. Réponse : « l'achat d'un nombre déterminé d'actions pour les annuler ». Le verso rappelle aussi le droit d'opposition. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-06-k03 | Le verso « Comme les subventions d'investissement et les provisions réglementées, ils sont exclus de la situation nette » est vrai à la lettre, mais il induit en erreur. Les subventions d'investissement et les provisions réglementées font partie des capitaux propres et sont seulement retranchées pour obtenir la situation nette. Les autres fonds propres, eux, ne font pas partie des capitaux propres : ils forment une rubrique distincte. Le rapprochement peut faire croire le contraire, une confusion classique au DCG. | Verso : « Les « autres fonds propres », que le règlement distingue des dettes. Ils ne font pas non plus partie des capitaux propres tels que le PCG les définit : ils forment une rubrique distincte et sont exclus de la situation nette. » (41 mots). La date d'application reste absente. La base [Ce qui a changé récemment#4, Définitions#0] porte tout le verso : « rubrique à part entière du bilan », définition des capitaux propres qui ne cite pas les autres fonds propres, exclusion de la situation nette. `src` et `url` ne changent pas. | Ce qui a changé récemment#4 ; Définitions#0 ; PCG, classe 1 |
| ue10-06-k19 | La question vise la SA et la SARL, et le verso donnait pour les deux formes deux éléments propres à la SA (L. 225-205) : le droit d'opposition du représentant de la masse des obligataires, et l'interdiction de commencer les opérations « avant qu'il ait été statué en première instance sur l'opposition ». L'article L. 223-34 (SARL) ne mentionne que les créanciers dont la créance est antérieure au dépôt au greffe du procès-verbal. Pour la SARL, il interdit seulement de commencer les opérations pendant le délai d'opposition. | Verso : « Les créanciers dont la créance est antérieure au dépôt au greffe du procès-verbal et, dans la SA, le représentant de la masse des obligataires, dans le délai fixé par décret (vingt jours dans la SA, un mois dans la SARL). Les opérations de réduction ne peuvent commencer pendant ce délai ni, dans la SA, avant qu'il ait été statué en première instance sur l'opposition. » (64 mots). La question, la base, `src` et `url` ne changent pas. | C. com., art. L. 223-34, L. 225-205, R. 223-35 et R. 225-152 (recherche 1) ; Règles essentielles#10 |

Les 33 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points suivants ont été contrôlés.

**Ajouts de la reprise**
- k06 : rôle du commissaire aux apports, désignation à l'unanimité des fondateurs ou par le juge, dispenses de L. 225-8-1.
- k16 : la question n'appelle qu'une réponse (frais d'établissement ou imputation sur les primes) et le verso ne dit rien de faux sur les charges.
- k18 : le complément sur la SARL est conforme à L. 223-34, confirmé par la recherche 1.
- k31 : compte 442 sans intitulé.
- k33 : conditions de l'article 39, 1-3° du CGI.
- k35 : L. 225-130 et L. 223-30.
- k36 : L. 225-207, toujours en vigueur pour la SA. La question délimite son champ.

**Doublons**
- k19, k20 et k36 portent tous trois sur Règles essentielles#10, mais chacun pose une question distincte : qui s'oppose et dans quel délai, ce qui distingue les deux réductions, le rachat en vue de l'annulation.
- Il en va de même pour k21 et k22 (première puis seconde étape de la procédure des capitaux propres inférieurs à la moitié du capital), k09 et k10, k26 et k27, et k28 et k29.

**Cartes du cycle précédent, inchangées**
- Définition des capitaux propres ; comptes 1011, 1012, 1013 et 109.
- Libération à la constitution : L. 223-7 et L. 225-3.
- Commissaire aux apports dans la SARL : L. 223-9 et D. 223-6-1.
- Frais de constitution : PCG, art. 212-9.
- Prime d'émission et DPS : L. 225-132, L. 225-135 et L. 225-144.
- Libération lors d'une augmentation de capital : L. 225-131, L. 225-144 et L. 223-32.
- Apport en nature : L. 225-147.
- Actionnaire défaillant : L. 228-27 et L. 228-28.
- Nullité d'une augmentation de capital : L. 225-149-4, délimité à la règle générale.
- Capitaux propres inférieurs à la moitié du capital : L. 223-42 et L. 225-248, loi n° 2023-171.
- Distribution : L. 232-10 à L. 232-13 et R. 232-17.
- Prélèvement de l'article 117 quater et prélèvements sociaux.
- Loi n° 2026-103 (art. 212 du CGI).

## Recherches

Une seule recherche WebSearch a été faite, restreinte à `legifrance.gouv.fr` :

1. **« article L223-34 code de commerce réduction du capital SARL opposition créanciers représentant de la masse ».**
   - L'article L. 223-34 (SARL) réserve le droit d'opposition aux créanciers dont la créance est antérieure à la date de dépôt au greffe du procès-verbal de délibération. Il ne mentionne pas le représentant de la masse des obligataires, qui figure à l'article L. 225-205 (SA).
   - En SARL, les opérations de réduction ne peuvent commencer pendant le délai d'opposition. La règle « ni avant qu'il ait été statué en première instance » est propre à la SA.
   - L'article R. 223-35 fixe le délai d'opposition à un mois en SARL.
   - Le résultat confirme aussi que la réduction est autorisée par l'assemblée des associés statuant aux conditions de modification des statuts (k18).

   Ces constats ont conduit à corriger k19. Sources : [C. com., art. L. 223-34](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006223287/), [art. R. 223-35](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006260591), [sous-section L. 225-204 à L. 225-205](https://www.legifrance.gouv.fr/codes/id/LEGISCTA000006178841), [art. R. 225-152](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006261604).

Aucune autre recherche n'a été faite. Les autres points avaient été établis lors de la relecture de la fiche (`rapports/ue10-06.md`) et du premier cycle de relecture des cartes (3 recherches sur anc.gouv.fr). Ils n'appelaient pas de doute réel.

## Points à reprendre dans la fiche

Le point 1 est nouveau. Les points 2 à 6, relevés par le premier cycle, restent d'actualité : la fiche n'a pas été modifiée depuis (`maj` du 14 octobre 2026).

1. **Règles essentielles#10.** L'item attribue à la SA et à la SARL un régime d'opposition unique, mais deux éléments ne valent que pour la SA (L. 225-205) :
   - le droit d'opposition du représentant de la masse des obligataires ;
   - la règle selon laquelle les opérations ne peuvent commencer « avant qu'il ait été statué en première instance sur cette opposition » (citation de l'item).

   L'article L. 223-34 ne vise que les créanciers antérieurs au dépôt du procès-verbal, et il interdit seulement de commencer les opérations pendant le délai d'opposition. Il faudrait distinguer les deux formes.
2. **Ce qui a changé récemment#4, et l'entrée « textes » du PCG.**
   - Date d'application du règlement ANC n° 2024-07 : la fiche indique les exercices ouverts à compter du 1er janvier 2026, une recherche sur anc.gouv.fr le 1er janvier 2025. Il faut vérifier sur le texte publié au JO et sur l'arrêté d'homologation, dont la date (26 décembre 2025 dans la fiche) reste à confirmer.
   - La formule « qui deviennent une rubrique à part entière » exagère la nouveauté : la rubrique « autres fonds propres » existait déjà (C. com., art. R. 123-190) et le règlement en affirme le statut.
3. **Définitions#0 (précision).** La phrase « La situation nette exclut les subventions d'investissement, les provisions réglementées et les autres fonds propres » met sur le même plan des éléments des capitaux propres et une rubrique qui n'en fait pas partie. Il faudrait préciser que les autres fonds propres ne font pas partie des capitaux propres.
4. **Règles essentielles#16.** L'intitulé « 442 État – impôts et taxes recouvrables sur des tiers » est périmé. Le compte 442 regroupe les impôts recouvrés pour le compte de l'État, avec les subdivisions 4421, 4422 (prélèvements forfaitaires non libératoires) et 4423 (retenues et prélèvements sur les distributions). Il faut reprendre l'intitulé exact sur le plan de comptes 2026. Hors fiche, `data/pcg/classe4.json` porte le même intitulé périmé.
5. **Règles essentielles#11 (et Chiffres et seuils#2).** La phrase « les associés décident s'il y a lieu à dissolution anticipée » ne vaut littéralement que pour la SARL (L. 223-42). Dans la SA (L. 225-248), le conseil d'administration ou le directoire doit convoquer l'AGE dans les quatre mois.
6. **Ce qui a changé récemment#1, et Règles essentielles#18 avec Points de vigilance#5.**
   - Ce qui a changé récemment#1 : l'item ne décrit pas les cas que l'article L. 225-149-4 réserve (« dans tous les autres cas »).
   - Règles essentielles#18 et Points de vigilance#5 : la fiche gagnerait à dire si la comptabilisation directe en charges des frais d'augmentation de capital reste possible. L'exercice 12 du chapitre l'admet.

## Classement des exercices

Le chapitre compte 19 exercices de type QCM, QCM multiple ou classement. Leur classement automatique donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 18 | oui |
| `calcul` | 1 | non |
| `chiffre` | 0 | — |

Les classeurs n'ont relevé aucun désaccord.
- Les 18 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable.
- L'exercice de nature `calcul` est un QCM. Il reste dans le chapitre, mais il n'est pas proposé en révision.
