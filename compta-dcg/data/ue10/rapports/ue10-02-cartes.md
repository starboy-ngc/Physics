# Cartes de notions : ue10-02 (Immobilisations incorporelles et corporelles : entrée et évaluation)

Date : 16 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue10-02.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Trois relectures successives ont vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elles n'ont fait aucune recherche web ; le seul juge était le texte de la fiche.
3. **Relecture d'exactitude.** Une relecture indépendante, menée comme celle d'un expert-comptable et juriste, a vérifié quatre points :
   - l'exactitude en droit et en comptabilité au 16 octobre 2026 : Code de commerce, CGI et BOFiP, PCG modifié par les règlements ANC n° 2018-01, 2019-09, 2020-09, 2022-06 et 2023-05 ;
   - l'ambiguïté pédagogique : la réponse attendue est-elle celle d'un correcteur du DCG, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ;
   - l'absence de calcul et de chiffre millésimé.

   Cette relecture s'est faite en deux temps. Un premier passage a corrigé k05, k26 et k36, supprimé k19 et ajouté k38 ; il a été interrompu avant la rédaction du rapport. Après la reprise, un second passage a relu de nouveau les 35 cartes une à une, en les confrontant à la fiche et aux textes, et a corrigé k21, k25, k28, k29 et k37.
4. **Recherches.** Le second passage a fait 3 recherches WebSearch limitées aux sites officiels (anc.gouv.fr, legifrance.gouv.fr, bofip.impots.gouv.fr). Le premier passage n'a laissé aucune trace de recherche.
5. **Validation.** La commande `node validate.js data/ue10/ue10-02.cartes.json` renvoie ✓ : 35 cartes, dont 8 définitions. La date `maj` est le 2026-10-16.

## Bilan

- **Nombre de cartes : 35** (le maximum admis par le validateur). Les identifiants k06 et k11 (supprimés avant les relectures) et k19 (supprimé par la relecture d'exactitude) restent libres ; rien n'a été renuméroté.
- **Répartition : 8 cartes `def` et 27 cartes `comp`.**
- **Couverture de la fiche :**
  - les 5 items de « Définitions » ont chacun au moins une carte (#0 k01 ; #1 k02 et k03 ; #2 k13 ; #3 k28 ; #4 k17 et k18) ;
  - les 19 « Règles essentielles » sont toutes couvertes ;
  - « Chiffres et seuils » : #0 (k34), #2 (k38) et #3 (k32) sont couverts ;
  - « Ce qui a changé récemment » : #0 (k30) et #1 (k33) sont couverts ;
  - « Points de vigilance » : #0, #1, #2, #4, #5, #7 et #9 sont couverts.
- **Items de fiche sans carte :**
  - **Chiffres et seuils#1** (délais d'amortissement des frais de constitution, d'augmentation de capital et d'établissement) : son contenu est repris par k25, dont la base est Règles essentielles#16 et #17 ;
  - **Points de vigilance#3, #6 et #8** : remarques d'historique ou de vocabulaire sur les anciens manuels et l'ancienne numérotation du PCG, qui n'appellent pas de carte de compréhension.

  Le contrat n'exige une carte que pour chaque item de « Définitions ».
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les seuls chiffres sont stables et font partie d'une règle : tolérance de 500 € HT (doctrine BOFiP inchangée), cinq ans, un dixième. Les dates citées sont des dates de textes ou d'entrée en vigueur.

## Corrections des relectures de fidélité

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | ue10-02-k04 | La question « à quelles conditions une immobilisation est-elle inscrite à l'actif » admettait aussi les conditions de définition d'un actif (identifiable, contrôlé…), alors que la réponse ne portait que sur les conditions de comptabilisation de l'art. 212-1. | La question demande désormais « quelles conditions de comptabilisation doivent être réunies ». Le verso reformule les deux conditions cumulatives : avantages économiques futurs probables et évaluation fiable du coût ou de la valeur. |
| 1 | ue10-02-k07 | La règle essentielle #4 (option de rattachement des frais externes de formation au coût d'acquisition, règlement ANC n° 2019-09) n'avait pas de carte, et le plafond de 35 cartes empêchait d'en ajouter une. | Ajout au verso : « Les frais externes de formation nécessaires à sa mise en service peuvent, sur option, y être rattachés. » Base : Règles essentielles#2 et #4. |
| 1 | ue10-02-k08 | « Sur option, ils sont rattachés… ou comptabilisés en charges » laissait croire que l'option imposait le rattachement. | « Ils peuvent, sur option, être rattachés au coût d'acquisition ou comptabilisés en charges. » |
| 1 | ue10-02-k13 | La question ne précisait pas l'article : une réponse tirée du PCG (art. 213-14 et 213-15) était aussi recevable. | La question vise « le Code de commerce (art. R. 123-178) ». |
| 1 | ue10-02-k16 | La question parlait seulement de « gros entretien », alors que la fiche vise « gros entretien et grandes révisions ». | La question mentionne « gros entretien ou de grandes révisions ». |
| 1 | ue10-02-k19 | La question demandait les conditions d'activation des frais de développement, mais le verso renvoyait seulement à « l'ensemble des critères de l'article 212-3 » sans les énumérer. | Ajout de la liste des critères de Règles essentielles#10. (La carte a ensuite été supprimée par la relecture d'exactitude, voir plus bas.) |
| 1 | ue10-02-k29 | « Quelles limites encadrent… » était vague et appelait plusieurs réponses justes. | Nouvelle question sur les conditions d'activation d'une solution informatique créée en interne ; le verso énumérait les critères de l'art. 611-3. (Reprise ensuite par la relecture d'exactitude.) |
| 2 | ue10-02-k15 | La réponse paraphrasait la fiche (« une utilisation différente des autres éléments »). | Reprise du texte de Règles essentielles#8 : « Lorsque, dès l'origine, un ou plusieurs éléments constitutifs de l'actif ont des utilisations différentes. » |
| 2 | ue10-02-k17 | Typographie : « a posteriori » en romain. | `<i>a posteriori</i>`. |
| 2 | ue10-02-k24 | La question admettait une autre réponse juste : la liste du PCG (frais de constitution, de transformation, de premier établissement, art. 212-9). | « Comment l'article R. 123-186 du Code de commerce définit-il les dépenses pouvant figurer à l'actif au poste « frais d'établissement » ? » |
| 2 | ue10-02-k25 | Règles essentielles#17 (C. com., art. L. 232-9 : frais de constitution amortis avant toute distribution de bénéfices) n'avait aucune carte. | Ajout de Règles essentielles#17 en second élément de base et d'une phrase au verso, réserve de l'art. L. 232-15, al. 2 comprise. |
| 3 | ue10-02-k32 | La réponse omettait les dérogations prévues par Règles essentielles#15, que la carte jumelle k31 mentionne. | Ajout : « Des dérogations peuvent être admises lorsque des circonstances particulières le justifient. » |

Les relectures de fidélité n'ont supprimé ni ajouté aucune carte. La première a signalé un point de fiche (date d'homologation du règlement ANC n° 2022-06), levé par la relecture d'exactitude (voir « Points à reprendre dans la fiche »).

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue10-02-k05 (1er passage) | « Suivant la façon dont elle entre dans le patrimoine » ne délimitait pas le champ de la question : d'autres modes d'entrée (apport en nature, par exemple) n'étaient pas couverts par la réponse, qui ne cite que trois cas. | La question énumère les trois cas visés : « … une immobilisation acquise à titre onéreux, produite par l'entité, ou acquise à titre gratuit ou par voie d'échange ? ». Réponse inchangée. | PCG, art. 213-1 ; C. com., art. L. 123-18 (Règles essentielles#1) |
| ue10-02-k19 (supprimée, 1er passage) | Doublon de k36 : les deux cartes demandaient les conditions d'activation des frais de développement de l'art. 212-3. | Supprimée. Sa dernière phrase (« À défaut, … en charges lorsqu'ils sont encourus ») et sa base Points de vigilance#2 sont reprises dans k36. L'identifiant k19 n'est pas réutilisé. | PCG, art. 212-3 (Règles essentielles#10, Points de vigilance#2) |
| ue10-02-k26 (1er passage) | « Comment peuvent être traités les frais d'augmentation de capital… ? » : un correcteur attend aussi leur comptabilisation directe en charges, que la réponse ne citait qu'en cas d'insuffisance de la prime. | La question est limitée aux postes du bilan : « Selon l'article 212-9 du PCG, à quels postes du bilan une société peut-elle inscrire ou imputer ses frais d'augmentation de capital, de fusion et de scission ? ». | PCG, art. 212-9 (Règles essentielles#16) |
| ue10-02-k36 (1er passage) | Fusion avec k19. | Ajout au verso : « À défaut, les frais de développement sont comptabilisés en charges lorsqu'ils sont encourus. » Base : Règles essentielles#10 et Points de vigilance#2. | PCG, art. 212-3 |
| ue10-02-k38 (ajoutée, 1er passage) | Chiffres et seuils#2 (amortissement des frais de développement) n'avait aucune carte. Règle stable, que seul ce chapitre traite ; la suppression de k19 libérait une place. | Nouvelle carte : « Selon le Code de commerce et le PCG, sur quelle durée sont amortis les frais de développement inscrits à l'actif ? » Verso : durée d'utilisation estimée des projets, justifiée dans l'annexe ; à défaut d'estimation fiable, cinq ans au plus. | C. com., art. R. 123-187 ; PCG, art. 214-3 (Chiffres et seuils#2) |
| ue10-02-k21 | « En comptes individuels français, seul le PCG s'applique » est inexact pris à la lettre : le Code de commerce (art. L. 123-18, R. 123-178, R. 123-186, R. 123-187…) s'applique aussi aux comptes individuels. Même correction que pour ue10-04-k33. | « En comptes individuels français, c'est le PCG, et non les IFRS, qui s'applique. » | C. com., art. L. 233-24 (Points de vigilance#9) ; C. com., art. R. 123-178 (Définitions#2) |
| ue10-02-k25 | Doublon partiel de k20 : la question demandait la méthode de référence pour les frais de constitution, déjà demandée par k20. La règle d'amortissement (plan, cinq ans au plus, avant toute distribution) n'était qu'au verso et n'était jamais demandée. | Question recentrée : « Selon le PCG et le Code de commerce, comment sont amortis les frais de constitution, de transformation et de premier établissement inscrits à l'actif ? ». Verso : plan et cinq ans au plus, puis la règle de l'art. L. 232-9 avec sa réserve, puis le rappel que la comptabilisation en charges est la méthode de référence. Même base. | PCG, art. 212-9 ; C. com., art. R. 123-187 et L. 232-9 (Règles essentielles#16 et #17) |
| ue10-02-k28 | « Porteuse d'avantages économiques futurs et utilisée au-delà d'un exercice, elle constitue une immobilisation incorporelle » pouvait se lire comme visant toute solution utilisée par l'entité, même sans qu'elle en ait le contrôle. La fiche précise « pour l'entité ». | « Porteuse d'avantages économiques futurs pour l'entité et utilisée au-delà d'un exercice… » | PCG, art. 611-1 et suivants, règlement ANC n° 2023-05 (Définitions#3) |
| ue10-02-k29 | La carte présentait comme exhaustive la liste des critères cumulatifs de l'art. 611-3 (« Outre la faisabilité technique, quels critères… ») : intention, capacité, avantages économiques futurs probables, évaluation fiable. Or le texte du règlement ANC n° 2023-05 vise aussi la disponibilité des ressources techniques et financières nécessaires pour achever la solution (recherche 1). Un étudiant qui citait ce critère était contredit par le verso. | Question : « Selon le PCG, quels critères doivent être réunis pour inscrire à l'actif le coût de production d'une solution informatique créée en interne ? ». Verso : « L'ensemble des critères cumulatifs de l'article 611-3, parmi lesquels… » suivi des cinq critères de la fiche. La liste n'est plus présentée comme fermée et reste portée par la fiche, qui est à reprendre. | Règlement ANC n° 2023-05, art. 611-3 (anc.gouv.fr, recherche 1) ; Règles essentielles#13 |
| ue10-02-k37 | La question contenait presque sa réponse : « que deviennent les dotations excédentaires » appelle « elles sont réintégrées ». La règle de fond (fiscalement, ces dépenses demeurent des charges et sortent du champ de l'art. 15 bis de l'annexe II) n'était pas demandée. | Question : « Sur le plan fiscal, comment sont traitées les dépenses de gros entretien ou de grandes révisions lorsque l'entreprise retient en comptabilité l'approche par composant ? ». Verso : « Elles demeurent des charges » (hors art. 15 bis de l'annexe II), réintégration extra-comptable des dotations excédentaires, provision déductible dans les conditions de l'art. 39, 1-5° du CGI. | BOI-BIC-CHG-20-20-20 ; CGI, art. 39, 1-5° (Points de vigilance#4) |

Les 26 autres cartes ont été jugées exactes au 16 octobre 2026, sans ambiguïté qui justifie une retouche et sans doublon. Ont notamment été vérifiés :

- **PCG :** définitions de l'actif et des immobilisations (art. 211-1, 211-5, 211-6) ; conditions de comptabilisation (art. 212-1) ; évaluation initiale au coût (art. 213-1) ; composition du coût d'acquisition, option sur les frais d'acquisition et frais de formation (art. 213-8) ; coûts d'emprunt des actifs éligibles (art. 213-9) ; sous-activité (art. 213-14, 213-15 et 213-32) ; composants et gros entretien (art. 214-9 et 214-10) ; recherche et développement, éléments créés en interne, fonds commercial (art. 212-3) ; frais d'établissement (art. 212-9) ; subventions d'investissement (art. 312-1) ; compte 747 (règlement ANC n° 2022-06).
- **Code de commerce :** art. L. 123-18, R. 123-178, R. 123-186, R. 123-187 (blocage des distributions) et L. 232-9.
- **BOFiP :** alignement fiscal et irrévocabilité de l'option sur les frais d'acquisition (k09, k10, confirmés par la recherche 3) ; tolérance de 500 € HT et ses exclusions (k34, k35).
- **Règlement ANC n° 2023-05 :** application aux exercices ouverts à compter du 1er janvier 2024 (k30, confirmée par la recherche 1).
- **Lien DSCG :** IAS 23 et IAS 38 rendent obligatoires l'incorporation des coûts d'emprunt des actifs qualifiés et l'activation des frais de développement qui remplissent les critères (k21).

## Recherches

Trois recherches WebSearch, limitées aux sites officiels, ont été faites au second passage.

1. **anc.gouv.fr** : « règlement ANC 2023-05 solutions informatiques article 611-3 critères faisabilité technique intention d'achever ressources exercices ouverts à compter ». Le résultat principal est le texte du règlement (`R2023_05.pdf`). Il établit trois points :
   - l'article 6 rend le règlement applicable aux exercices ouverts à compter du 1er janvier 2024, ce qui confirme k30 ;
   - les critères cumulatifs d'activation d'une solution créée comprennent, outre ceux que cite la fiche, la disponibilité des ressources techniques et financières nécessaires pour achever le développement, d'où la correction de k29 ;
   - la règle sur le coût de production figure à l'art. 611-4 du règlement, mais à l'art. 611-5 du recueil PCG au 1er janvier 2026.
2. **legifrance.gouv.fr** : « arrêté portant homologation du règlement n° 2022-06 du 4 novembre 2022 ». Le résultat est l'« Arrêté du 26 décembre 2023 portant homologation des règlements n° 2022-06 du 4 novembre 2022, n° 2023-01 du 12 mai 2023, […] n° 2023-05 du 10 novembre 2023, […] de l'Autorité des normes comptables ». La date d'homologation donnée par la fiche est donc exacte, pour le règlement n° 2022-06 comme pour le règlement n° 2023-05. Le résumé des résultats évoque aussi un arrêté du 26 décembre 2025 (homologation des règlements n° 2024-07 et 2025-05) qui mentionnerait l'abrogation du règlement n° 2022-06 ; la portée de cette mention n'a pas pu être établie.
3. **bofip.impots.gouv.fr** : « BOI-BIC-CHG-20-20-10 frais d'acquisition immobilisations option irrévocable ». Le résultat (version du 9 janvier 2019) confirme quatre points :
   - l'option est exercée par la seule comptabilisation ;
   - aucune option fiscale ne peut différer de l'option comptable ;
   - l'option est irrévocable et s'applique à toutes les immobilisations corporelles et incorporelles acquises ;
   - une option distincte vaut pour les titres.

   Le BOFiP admet toutefois une révision de l'option lorsque les règles comptables autorisent un changement de méthode. Les cartes k09 et k10 sont conservées telles quelles, car elles reprennent l'énoncé du BOFiP.

## Points à reprendre dans la fiche

1. **Règles essentielles#13** (base de k29). La liste des critères cumulatifs de l'art. 611-3 paraît incomplète. D'après le texte du règlement ANC n° 2023-05 (recherche 1), il faut ajouter :
   - la disponibilité des ressources techniques, financières et autres nécessaires pour achever le développement ;
   - la démonstration de l'existence d'un marché, ou de l'utilité de la solution pour un usage interne.

   À vérifier sur le texte verbatim, puis à compléter. Il faut aussi vérifier la source « PCG, art. 611-3 et 611-4 » : dans le recueil au 1er janvier 2026, la règle du coût de production figurerait à l'art. 611-5. Une fois la fiche corrigée, k29 pourra énumérer tous les critères sans « parmi lesquels ».
2. **Points de vigilance#9** (base de k21). « En comptes individuels français, seul le PCG s'applique » exclut à tort le Code de commerce. Il faudrait écrire : « en comptes individuels, les règles françaises (Code de commerce et PCG) s'appliquent, et non les IFRS ». La même remarque a été faite pour ue10-04 (Points de vigilance#5).
3. **Règles essentielles#6 et Points de vigilance#0** (bases de k09 et k10). L'option sur les frais d'acquisition est bien « irrévocable », mais le BOFiP admet sa révision lorsque les règles comptables autorisent un changement de méthode (recherche 3). Cette nuance pourrait être ajoutée, avec le paragraphe exact du BOI-BIC-CHG-20-20-10.
4. **Ce qui a changé récemment#1 et liste « textes » (règlement ANC n° 2022-06).**
   - Le point relevé par la première relecture de fidélité est **levé** : la date d'homologation du 26 décembre 2023 est exacte (recherche 2).
   - Reste à vérifier la mention, dans un arrêté du 26 décembre 2025, d'une abrogation du règlement n° 2022-06. Il s'agit probablement d'une abrogation formelle après intégration au PCG. Cela ne change rien aux comptes 657, 747, 757 et 152 cités par la carte k33.

## Classement des exercices

Le chapitre compte 28 exercices. Les 19 QCM, QCM multiples et classements ont été classés automatiquement :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 16 | oui |
| `calcul` | 3 | non |
| `chiffre` | 0 | — |

Les classeurs ont eu un seul désaccord, sur l'exercice #23 : un QCM qui demande la valeur d'inscription à l'actif d'une machine de 100 000 € financée à 30 % par une subvention d'investissement. L'un des classeurs le voyait comme `notion`, l'autre comme `calcul` ; la nature retenue est `calcul`, puisque l'énoncé chiffré demande un montant. Les 16 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 3 QCM de nature `calcul` et les 9 exercices `calc` et `ecriture` restent dans le chapitre, mais ne sont pas proposés en révision.
