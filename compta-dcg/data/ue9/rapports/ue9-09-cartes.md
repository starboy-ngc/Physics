# Cartes de notions : ue9-09 (Organisation comptable et documents de synthèse)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-09.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte (`t` et `cite`) des items de la fiche : mêmes conditions, mêmes exceptions, même vocabulaire juridique. Elle n'a fait aucune recherche web. Elle a contrôlé 35 cartes et en a corrigé cinq ; elle n'en a ni supprimé ni ajouté. Le résultat transmis de cette relecture s'interrompt dans la rubrique « recherches » (le texte reçu s'arrête sur « chaque carte a été comparée au ») : ses éventuels points de fiche ne sont donc pas connus.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, LPF, CGI, BOFiP, ordonnance n° 2009-79, PCG modifié par le règlement ANC n° 2022-06) ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ou purement mécaniques.

   Elle a aussi vérifié l'absence de calcul, d'écriture chiffrée et de chiffre millésimé. Une seule recherche a été faite, limitée à legifrance.gouv.fr (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-09.cartes.json` : ✓ (35 cartes, 13 déf.).

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. Aucun identifiant n'a été supprimé : la série k01 à k35 est continue.
- **Répartition : 13 cartes `def` et 22 cartes `comp`.**
- **Couverture de la fiche.** Les 7 items de « Définitions » ont chacun au moins une carte. Les 17 « Règles essentielles » sont toutes couvertes, sauf #15, qui est millésimée. Les 4 « Points de vigilance » ont chacun leur carte de compréhension. Dans « Chiffres et seuils », les items stables #2 et #3 ont leur carte. Dans « Ce qui a changé récemment », les items #0, #2 et #5 ont leur carte.
- **Items de fiche sans carte :**
  - **Règles essentielles#15** (liasse fiscale, formulaire 2065-SD, majoration de 0,2 %). L'item est millésimé 2026.
  - **Chiffres et seuils#0 et #1** (délais de conservation de 2026, seuils des micro, petites et moyennes entreprises). Ils sont millésimés. La règle stable d'appréciation des seuils est portée par k28, et la réforme du délai fiscal par k32.
  - **Ce qui a changé récemment#3 et #4** (décret n° 2024-152 relevant les seuils, calendrier de la facturation électronique). Ils sont millésimés.
  - **Ce qui a changé récemment#1, #6 et #7** (règlement n° 2023-03, coordination avec le n° 2022-06 dans le règlement des CSE ; compte 791 maintenu pour les concessions d'aménagement ; compte 6454 renommé « Cotisations à France Travail »). Ces items sont stables mais secondaires, et le jeu atteint déjà le maximum de 35 cartes. Les intitulés de comptes relèvent des cartes du plan comptable, qui entrent elles aussi dans les révisions espacées.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres qui restent sont stables et font partie d'une règle : douze mois, une fois par mois, un mois ou deux mois, deux exercices consécutifs, six puis dix ans (k32). Les dates citées (2009, 2016, 2022, 2023, 2024, 2025, 2026, 2027) sont des dates de textes ou d'entrée en vigueur.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-09-k02 | La réponse présentait « bilan, compte de résultat et annexe » comme valable pour tout commerçant. Or la fiche (Règles essentielles#13) dispense d'annexe les micro-entreprises, sauf celles qui gèrent des titres. Une exception oubliée rendait donc la réponse fausse pour une micro-entreprise. | La question vise désormais l'article L. 123-12 et ne porte que sur le principe (« en principe »). La réponse mentionne la dispense d'annexe des micro-entreprises et son exception (sociétés qui gèrent des titres). La base devient Définitions#1 et Règles essentielles#13 ; `src` et `url` restent ceux de Définitions#1. |
| ue9-09-k08 | La question « comment les mouvements… sont-ils enregistrés au livre-journal ? » acceptait une autre réponse juste tirée du cours (« en partie double »), différente de celle attendue. | La question devient « dans quel ordre les mouvements… sont-ils enregistrés au livre-journal ? ». La réponse est inchangée : chronologiquement, opération par opération et jour par jour. |
| ue9-09-k21 | La question « quels écarts donnent lieu à une écriture ? » acceptait aussi « les erreurs de l'entreprise », que la fiche n'évoque pas. Par ailleurs, la réponse omettait « à leur date » pour les chèques et remises déjà enregistrés. | La question porte maintenant sur les mouvements non communs au compte 512 et au relevé que l'entreprise doit enregistrer. Dans la réponse, « déjà enregistrés à leur date » est rétabli, comme dans la fiche. |
| ue9-09-k22 | Défaut de couverture : la première phrase de Règles essentielles#12 sur le bilan (actif et passif décrits séparément, capitaux propres apparaissant distinctement) n'avait aucune carte. Le jeu compte déjà 35 cartes, le maximum du validateur, donc aucune carte ne pouvait être ajoutée. | La carte couvre maintenant la structure des deux documents. Pour le bilan : actif et passif décrits séparément, capitaux propres distincts. Pour le compte de résultat, le contenu d'origine est conservé : classement par différence entre éléments du résultat courant et résultat exceptionnel, selon le modèle ANC. La base reste Règles essentielles#12. |
| ue9-09-k30 | La parenthèse « le règlement n° 2025-05 maintient le compte 791… », placée après « suppression des transferts de charges », suppose que le compte 791 correspond aux transferts de charges. La fiche ne le dit nulle part : c'est une connaissance extérieure. De plus, ce règlement n'est pas un apport du règlement 2022-06, sur lequel porte la question. | La parenthèse est retirée et la base se limite à Ce qui a changé récemment#0 ; `src` et `url` sont inchangés. La réponse liste les quatre apports du règlement 2022-06 tels que la fiche les donne. |

La première relecture n'a supprimé ni ajouté aucune carte.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-09-k08 | **Vrai seulement dans un cas non dit.** La question disait que les mouvements sont enregistrés « au livre-journal » opération par opération et jour par jour. C'est vrai sans journaux auxiliaires. Mais lorsqu'un commerçant en tient, ce qui est le cas courant, l'enregistrement opération par opération se fait dans les journaux auxiliaires : le livre-journal ne reçoit alors que leurs centralisations, au moins mensuelles (k09). | La question ne nomme plus le livre-journal : « Selon le Code de commerce, dans quel ordre un commerçant enregistre-t-il les mouvements affectant le patrimoine de son entreprise ? ». La réponse précise « au livre-journal ou dans ses journaux auxiliaires ». La base (Règles essentielles#0 et #1), `src` et `url` sont inchangés. | C. com., art. L. 123-12 et R. 123-174 à R. 123-176 ; Règles essentielles#1 |
| ue9-09-k19 | **Vrai seulement en principe.** « Seul le bénéfice réalisé à la date de clôture peut être inscrit » omet l'exception de l'article L. 123-21, alinéa 2. Après inventaire, on peut inscrire le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, lorsque sa réalisation est certaine et que le bénéfice global peut être évalué avec une sécurité suffisante. La fiche n'en parle pas : la carte ne peut donc pas l'ajouter. | « En principe, seul le bénéfice réalisé à la date de clôture peut être inscrit dans les comptes annuels. » Le reste de la carte est inchangé. La délimitation est la même que celle de la carte k11 du chapitre ue9-07. | C. com., art. L. 123-21 |
| ue9-09-k24 | **Exception incomplète.** La réponse donnait la gestion de titres comme seule exception à la dispense d'annexe des micro-entreprises. Or l'article L. 123-16-2 écarte aussi de cet allègement certaines entités : établissements de crédit et sociétés de financement, entreprises d'assurance et de réassurance, notamment. La fiche ue9-01 (C. com., art. L. 123-16-2) le dit ; la fiche ue9-09 ne le dit pas pour l'annexe. | « Les micro-entreprises, sauf **notamment** celles dont l'activité consiste à gérer des titres de participations et de valeurs mobilières. » La réponse ne se présente plus comme exhaustive, sans rien ajouter d'extérieur à la fiche. | C. com., art. L. 123-16-1 et L. 123-16-2 ; fiche ue9-01 |
| ue9-09-k02 | **Même défaut et doublon partiel.** La seconde phrase, ajoutée par la première relecture, redisait la dispense d'annexe avec la seule exception de la gestion de titres. C'était la même exception incomplète que k24, et la même information que k24. | La seconde phrase devient « Les micro-entreprises sont toutefois, sauf exceptions, dispensées d'annexe. » La carte signale la dispense sans répéter k24, qui porte le détail. | C. com., art. L. 123-12, L. 123-16-1 et L. 123-16-2 |
| ue9-09-k29 | **Restriction trompeuse et précision hors question.** La réponse ajoutait : « dans les sociétés par actions, en cas de refus d'approbation, une copie de la délibération est déposée dans le même délai ». Ce n'est pas faux pour les sociétés par actions (L. 232-23). Mais la formule laisse croire que la règle leur est propre, alors que l'article L. 232-22 paraît prévoir la même chose pour les SARL. La phrase ne répondait de toute façon pas à la question, qui porte sur le délai. Par ailleurs, le rapport des commissaires aux comptes n'est déposé que si la société en a. | Phrase sur le refus d'approbation retirée. Nouvelle réponse : « Dans le mois qui suit leur approbation, ou dans les deux mois lorsque le dépôt est effectué par voie électronique. Les comptes annuels sont déposés accompagnés notamment, le cas échéant, du rapport des commissaires aux comptes. » | C. com., art. L. 232-22 et L. 232-23 |
| ue9-09-k30 | **Ambiguïté.** La question « Quels changements le règlement n° 2022-06 apporte-t-il… ? » admettait d'autres réponses justes que les quatre attendues. Par exemple, les cessions d'immobilisations sont désormais classées en exploitation (657 / 757) ou en financier (6671 / 7671), et la quote-part de subvention d'investissement virée au résultat passe en 747 (fiche ue9-01). | « Quels sont les **principaux** changements apportés par le règlement ANC n° 2022-06 pour les exercices ouverts à compter du 1er janvier 2025 ? ». La réponse (quatre apports, selon la fiche) est inchangée. | Règlement ANC n° 2022-06 ; fiche ue9-01 |

Aucune carte n'a été supprimée ni ajoutée dans cette relecture.

Les 29 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- Code de commerce : L. 123-12, L. 123-13, L. 123-14, L. 123-17, L. 123-19 à L. 123-23, L. 123-16 et L. 123-16-1 (appréciation sur deux exercices consécutifs), L. 123-25, L. 232-25 et L. 233-21 ; R. 123-172 à R. 123-177, R. 123-190, R. 123-192 et R. 123-193 ;
- ordonnance n° 2009-79, art. 1er (version issue de l'ordonnance n° 2023-1142) et art. 4 (homologation) ;
- PCG, art. 121-1 (définition de la comptabilité) et 121-5 (permanence des méthodes) ; règlement n° 2022-06 (présomption d'événement inhabituel) ;
- LPF, art. L. 47 A (FEC) et L. 102 B (passage de six à dix ans par la loi n° 2026-534) : ces deux points avaient été recoupés par les recherches de la relecture finale de la fiche (`rapports/ue9-09.md`, recherches 1, 2 et 8). Aucune nouvelle recherche n'était donc nécessaire.

Cartes examinées sans être modifiées :
- **k35** (comptes consolidés). Ma mémoire du texte donnait un renvoi aux « deuxième et troisième alinéas » de L. 123-14. La recherche a confirmé la rédaction de la fiche (« premier et deuxième alinéas ») : la carte est exacte.
- **k15** (permanence des méthodes). La réponse cite les deux exceptions du PCG (changement de réglementation, changement à l'initiative de l'entité) sans dire que ce dernier doit être justifié. Le cadre est cependant posé par la première phrase : « sauf cas exceptionnels, afin de donner une image fidèle ». La carte n'induit donc pas en erreur.
- **k26** (petites et moyennes entreprises). « Demander que leur seul compte de résultat ne soit pas rendu public » reprend le vocabulaire de la fiche. La carte est conservée, la règle n'étant pas déformée.
- **k02, k23 et k24** (annexe). Les trois cartes se recoupent sur l'annexe, mais leurs questions sont distinctes : la composition des comptes annuels, le rôle de l'annexe, les entreprises dispensées. Après la retouche de k02, le détail de la dispense n'est plus porté que par k24.
- **k17 et k18** (L. 123-20), **k13 et k14** (L. 123-14), **k30 et k31** (règlement n° 2022-06). Chaque paire repose sur le même item mais pose deux questions différentes : un principe d'un côté, son effet ou sa mise en œuvre de l'autre.
- **k05 et k33** (livres obligatoires). La seconde phrase de k33 redit k05, mais la carte porte une règle distincte : le sort des données d'inventaire depuis la suppression du livre d'inventaire.

## Recherches

Une seule recherche WebSearch a été faite, limitée à `legifrance.gouv.fr`.

1. **« Code de commerce article L233-21 comptes consolidés réguliers sincères "alinéas de l'article L. 123-14" »** (legifrance.gouv.fr). Résultat : la page de l'article L. 233-21 sur Légifrance (LEGIARTI000006229310), en vigueur depuis le 21 septembre 2000. Elle confirme deux points :
   - les comptes consolidés doivent être réguliers et sincères et donner une image fidèle du patrimoine, de la situation financière et du résultat de l'ensemble consolidé ;
   - « Il est fait application, le cas échéant, des dispositions prévues aux premier et deuxième alinéas de l'article L. 123-14. »

   La carte k35 et l'item Points de vigilance#3 sont donc exacts.

Aucune autre recherche n'a été jugée nécessaire. Les autres points étaient établis par les citations officielles de la fiche, par le rapport de relecture finale de la fiche (`rapports/ue9-09.md`, 11 recherches) et par la fiche ue9-01 (C. com., art. L. 123-16-2).

## Points à reprendre dans la fiche

1. **Règles essentielles#13 (dispense d'annexe).** L'item ne mentionne que l'exception des sociétés de gestion de titres. Il omet que l'article L. 123-16-2 écarte aussi de cet allègement certaines entités : établissements de crédit et sociétés de financement, entreprises d'assurance et de réassurance, notamment. La fiche ue9-01 le dit ; il faudrait aligner ue9-09. Les cartes k02 et k24 sont délimitées en attendant (« sauf exceptions », « sauf notamment »).
2. **Règles essentielles#9 (C. com., art. L. 123-21).** « Seul le bénéfice réalisé à la date de clôture peut être inscrit » se lit comme une règle sans exception. Or l'alinéa 2 permet d'inscrire, après inventaire, le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, lorsque sa réalisation est certaine et que le bénéfice global peut être évalué avec une sécurité suffisante. Le même point est relevé pour ue9-07 (Règles essentielles#7). La carte k19 est délimitée par « en principe ».
3. **Chiffres et seuils#3 (dépôt au greffe), à vérifier.** Le dépôt d'une copie de la délibération en cas de refus d'approbation y est présenté comme propre aux sociétés par actions (L. 232-23). L'article L. 232-22 paraît prévoir la même règle pour les SARL, à vérifier sur Légifrance. Il faudrait alors écrire « dans les SARL et les sociétés par actions », ou ne pas restreindre. Par ailleurs, la formule « avec notamment le rapport des commissaires aux comptes » gagnerait à préciser « le cas échéant ». La carte k29 ne reprend plus la règle du refus d'approbation.

## Classement des exercices

Le classement automatique des 22 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 19 | oui |
| `calcul` | 0 | non |
| `chiffre` | 3 | non |

Aucun désaccord n'a été relevé entre les classeurs. Les 19 exercices de nature `notion` entrent dans les révisions espacées avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 3 exercices de nature `chiffre` (rappel d'un chiffre millésimé) restent dans le chapitre mais ne sont pas proposés en révision. Le chapitre ne comporte aucun exercice de calcul parmi ces types.
