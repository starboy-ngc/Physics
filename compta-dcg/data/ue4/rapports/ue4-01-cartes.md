# Cartes de notions : ue4-01 (Introduction au droit fiscal et mécanismes généraux de l'impôt sur le revenu)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-01.fiche.json` et d'elle seule. Elles respectent le contrat (section 8) : une question par carte, aucun calcul, aucun chiffre millésimé, et chaque carte s'appuie sur un ou deux items de fiche (`base`) dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : un premier relecteur a contrôlé les 35 cartes. Il a vérifié que chaque carte dit ce que dit la fiche, sans plus, et qu'elle respecte la forme exigée par le contrat.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a vérifié les points suivants :
   - **Exactitude** : chaque carte est-elle juste au regard du droit en vigueur au 15 octobre 2026 (Constitution, DDHC, LOLF, CGI, LPF, BOFiP, jurisprudence du Conseil d'État) ?
   - **Ambiguïté** : la réponse attendue est-elle celle qu'attendrait un correcteur du DCG, et la seule réponse juste possible ?
   - **Doublons et cartes triviales.**
   - **Absence de calcul et de chiffre millésimé.**
4. **Recherches** : 2 recherches sur les 3 permises, limitées à legifrance.gouv.fr, bofip.impots.gouv.fr et service-public.fr (détail plus bas).

Validation : `node validate.js data/ue4/ue4-01.cartes.json` renvoie ✓ (35 cartes, dont 9 de définition).

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k35, sans trou) |
| Définition (`def`) | 9 |
| Compréhension (`comp`) | 26 |
| Cartes supprimées | 0 |
| Cartes ajoutées | 0 |

**Items de la fiche sans carte** : tous sont millésimés et ne peuvent donc pas donner de carte.

- **Règles essentielles #5, #9 et #10** : plafond d'imputation des déficits fonciers, plafonnement du quotient familial, décote avec son exemple chiffré.
- **Chiffres et seuils #0 à #4 et #6** : barème 2026, décote 2026, taux minimum des non-résidents, plafond de la pension alimentaire, plafond des dons à 75 %, CDHR.
- **Ce qui a changé récemment #1 à #4** : CDHR, indexation du barème par la loi de finances pour 2026, relèvement du plafond des dons à 75 %, hausse de la CSG par la LFSS 2026.
- **Points de vigilance #4** : rappel de dater les chiffres millésimés.

Chacun des six items de la section « Définitions » a au moins une carte. Les dix-sept règles essentielles stables ont toutes au moins une carte. Il en va de même des quatre points de vigilance stables, du seul item stable de « Ce qui a changé récemment » (#0, taux individualisé) et de Chiffres et seuils #5 (CEHR, seuils et taux non indexés).

Le jeu atteint le plafond de 35 cartes fixé par le contrat. Aucun ajout n'était donc possible sans suppression, et aucune carte n'a mérité d'être supprimée.

## Corrections de la première relecture (fidélité)

Le premier relecteur a contrôlé 35 cartes. Le résultat transmis s'interrompt au milieu de la ligne k19. La ligne k27 a donc été reconstituée à partir de l'écart entre les versions du fichier.

| Cible | Problème | Correction |
|---|---|---|
| k05 | La réponse oubliait « d'impositions antérieures ». Dans « le redevable a appliqué ses instructions ou circulaires », le « ses » se lisait comme renvoyant au redevable et non à l'administration. | La réponse dit désormais « Aucun rehaussement d'impositions antérieures ne peut être opéré… ». Elle ajoute « lorsque le redevable a appliqué un texte selon l'interprétation que l'administration avait fait connaître par ses instructions ou circulaires publiées (BOFiP) et non rapportées à la date des opérations », comme dans Définitions#3. |
| k06 | La question en « Pourquoi … ne crée-t-elle pas de droit » donnait déjà la notion à retenir. Elle admettait aussi une autre réponse juste, le principe de légalité (Constitution, art. 34), qui n'est pas celle de la fiche. | Nouvelle question, à réponse unique : « Selon le Conseil d'État, quel pouvoir l'article L. 80 A du LPF confère-t-il à l'administration fiscale lorsqu'elle publie sa doctrine ? ». Réponse : « Aucun pouvoir réglementaire : il ne lui permet pas de déroger à la loi, et la doctrine ne crée pas de droit. Seule la dernière interprétation formellement admise peut être invoquée. » (Points de vigilance#0) |
| k12 | La question « Qu'est-ce que le foyer fiscal soumis à imposition commune » était circulaire : la réponse répétait « font l'objet d'une imposition commune ». La définition passait aussi sous silence les cas d'imposition distincte que prévoit Définitions#5. | Question : « Selon l'article 6 du CGI, quelles personnes forment le foyer fiscal soumis à imposition commune à l'impôt sur le revenu, et sur quels revenus ? ». Réponse : les personnes mariées et les partenaires de PACS, sur leurs revenus, ceux de leurs enfants et ceux des personnes à charge, sauf cas d'imposition distincte (séparation, abandon du domicile conjugal, option l'année du mariage ou du PACS). |
| k13 | La question citait « article 6, 4 du CGI », alors que la fiche ne rattache pas ces cas à cet alinéa (sa `src` dit seulement « art. 6, 1, 4 et 5 »). Elle laissait aussi ouverte une seconde réponse juste : l'option pour l'imposition distincte l'année du mariage ou du PACS. | Question : « En dehors de l'option ouverte l'année du mariage ou du PACS, dans quels cas des époux sont-ils imposés distinctement à l'impôt sur le revenu ? ». La réponse est inchangée et fidèle à Définitions#5. |
| k19 | La réponse ajoutait « dans la limite d'un plafond revalorisé chaque année », ce que l'item de base Règles essentielles#6 ne dit pas. Cette affirmation ne figure que dans des items millésimés, qui ne peuvent pas servir de base. | Passage supprimé. Réponse : « Pour un montant tenant compte de l'état de fortune du débiteur et des besoins du bénéficiaire, et seulement si l'enfant n'est pas rattaché au foyer fiscal. La pension déduite est imposable chez l'enfant. » |
| k27 (reconstituée) | La question ne précisait pas quels organismes ouvrent droit au taux de 75 %. | La question est complétée par « (repas, soins, logement) ». La réponse ajoute une phrase sur les organismes visés : ceux qui fournissent gratuitement des repas ou des soins aux personnes en difficulté ou qui favorisent leur logement. |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k13 | La question (« En dehors de l'option ouverte l'année du mariage ou du PACS… ») admettait encore une autre réponse juste : l'année du divorce, de la séparation ou de la rupture du PACS, où chacun est imposé séparément. La fiche n'en parle pas, mais un étudiant pouvait la donner à bon droit. | La question vise désormais les seules situations de vie séparée en cours de mariage : « Dans quels cas des époux qui vivent séparément, sans être divorcés, sont-ils imposés distinctement à l'impôt sur le revenu ? ». La réponse (les trois cas de Définitions#5) est inchangée. | Fiche Définitions#5 ; CGI, art. 6 |
| k19 | Après la première relecture, la question « Dans quelles conditions… est-elle déductible ? » appelait une liste complète. La réponse taisait pourtant le plafond légal de déduction, une condition essentielle que la fiche mentionne ailleurs (Chiffres et seuils#3, Points de vigilance#4). La carte laissait ainsi croire qu'il n'y a pas de plafond. | La question est délimitée sans donner de chiffre : « Hors plafond, d'après quels éléments s'apprécie le montant déductible d'une pension alimentaire versée à un enfant majeur non rattaché au foyer fiscal ? ». Réponse : l'état de fortune du débiteur et les besoins du bénéficiaire ; la pension déduite est imposable chez l'enfant ; aucune déduction si l'enfant est rattaché. La base reste Règles essentielles#6. | CGI, art. 156, II-2° ; fiche Règles essentielles#6, Chiffres et seuils#3 |
| k27 | La phrase ajoutée par la première relecture (« Il vise les organismes qui fournissent gratuitement des repas ou des soins… ou favorisent leur logement ») se lisait comme la liste complète des bénéficiaires du taux de 75 %. Or l'article 200 du CGI vise aussi les organismes qui accompagnent les victimes de violence domestique ou contribuent à leur relogement. | Phrase supprimée. La carte ne porte plus que sur l'articulation des taux : 75 % dans un plafond spécifique, 66 % au-delà, et la fraction à 75 % n'entre pas dans la limite de 20 %. La question garde « (repas, soins, logement) », qui décrit sans prétendre à l'exhaustivité. | CGI, art. 200, 1 ter (recherche n° 2) |
| k31 | La question « Que se passe-t-il lorsqu'un salarié ne communique pas son taux… ? » admettait une autre réponse juste, absente de la fiche : le contribuable doit alors verser lui-même un complément à l'administration si le taux neutre est inférieur à son taux personnel. Elle supposait aussi à tort que le salarié transmet lui-même son taux à l'employeur. | Question : « Quel taux de prélèvement à la source l'employeur applique-t-il au salarié qui a choisi de ne pas lui faire connaître son taux personnalisé ? ». Réponse : « Un taux neutre (grille par défaut) », déterminé uniquement en fonction du montant de la rémunération versée ; l'option ne concerne que la personne qui l'a prise. | CGI, art. 204 H ; fiche Règles essentielles#15 |
| k33 | La réponse limitait la garantie des prises de position tacites à la vérification de comptabilité et à l'examen contradictoire de la situation fiscale personnelle. L'article L. 80 A du LPF vise aussi l'**examen** de comptabilité. | La liste devient illustrative : « La garantie vise les points d'un contrôle tel qu'une vérification de comptabilité ou un examen contradictoire de la situation fiscale personnelle, pour les contrôles dont l'avis est adressé à compter du 1er janvier 2019. » La carte ne nomme pas l'examen de comptabilité, que la fiche ne mentionne pas (voir plus bas). | LPF, art. L. 80 A, issu de la loi n° 2018-727 du 10 août 2018 (recherche n° 1) |

**Cartes contrôlées et maintenues** :

- **Doublons apparents** : k01/k02, k05/k33, k06/k07, k12/k13/k14, k24/k25/k28 et k31/k35 portent sur les mêmes items, mais chaque carte interroge un angle distinct. On trouve ainsi Constitution et LOLF, doctrine publiée et prise de position tacite, portée de la doctrine et abus de droit, composition du foyer, cas d'imposition distincte et option, réduction, crédit et plafonnement, taux neutre et modulation.
- **Chiffres stables** : k25 (plafonnement global), k26 (66 % et 20 %), k29 (CEHR) et k32 (majoration de 10 % ou 20 %) citent des chiffres fixés par la loi, sans indexation annuelle, et chaque question porte sur la règle. Le contrat (section 8) les admet.
- **Date d'entrée en vigueur** : k30 cite la date du 1er septembre 2025. C'est une date d'entrée en vigueur, pas un chiffre millésimé.
- **CSG déductible (k20)** : la fraction de 6,8 points reste exacte après la LFSS 2026, comme l'indique la fiche.

## Recherches faites

1. **LPF, art. L. 80 A : prise de position tacite sur les points d'un contrôle** (domaine legifrance.gouv.fr).
   - Confirmé : la garantie, issue de la loi du 10 août 2018, joue pour les contrôles dont l'avis est adressé à compter du 1er janvier 2019.
   - Elle vise l'administration qui a pris position sur les points du contrôle, y compris tacitement, dès lors qu'elle a pu se prononcer en connaissance de cause. Elle s'applique dans le cadre d'un examen ou d'une vérification de comptabilité ou d'un examen contradictoire de la situation fiscale personnelle.
   - Cette recherche a conduit à corriger k33.
2. **CGI, art. 200, 1 ter : réduction d'impôt de 75 % pour les dons** (domaines legifrance.gouv.fr, bofip.impots.gouv.fr, service-public.fr).
   - Confirmé : le taux de 75 % vise les organismes sans but lucratif qui fournissent gratuitement des repas ou des soins aux personnes en difficulté ou qui favorisent leur logement.
   - Le texte de l'article 200 mentionne aussi les organismes d'intérêt général qui, à titre principal et gratuitement, accompagnent les victimes de violence domestique ou contribuent à leur relogement.
   - Le BOFiP (BOI-IR-RICI-250-30, version du 6 juillet 2026) applique le 1 ter dans sa rédaction issue de la loi de finances pour 2026.
   - Cette recherche a conduit à corriger k27. L'extrait n'a pas permis de lire le paragraphe en entier : le point est signalé à vérifier.

## Points à reprendre dans la fiche

- **Définitions#3** : l'énumération « (vérification de comptabilité, examen contradictoire de la situation fiscale personnelle) » est incomplète. Le texte de l'article L. 80 A du LPF vise aussi l'examen de comptabilité (« dans le cadre d'un examen ou d'une vérification de comptabilité ou d'un examen contradictoire de la situation fiscale personnelle »).
- **Règles essentielles#11** : la liste des organismes ouvrant droit au taux de 75 % omet ceux qui accompagnent les victimes de violence domestique ou contribuent à leur relogement (CGI, art. 200, 1 ter). Le libellé exact est à vérifier sur la rédaction issue de la loi de finances pour 2026.
- **Règles essentielles#6** : l'item omet deux règles stables de l'article 156, II-2° du CGI.
  - La pension doit répondre aux conditions des articles 205 à 211 du Code civil (obligation alimentaire).
  - La déduction est plafonnée, pour un enfant majeur, au montant de l'abattement prévu par l'article 196 B, revalorisé chaque année. Seul le montant de ce plafond est millésimé, pas son principe.
  - Faute de ces précisions dans un item stable, la carte k19 a dû être délimitée par « Hors plafond ».
- **Règles essentielles#15** : l'item omet une contrepartie de l'option pour le taux neutre. Si ce taux conduit à un prélèvement inférieur à celui du taux personnalisé, le contribuable verse lui-même un complément à l'administration (CGI, art. 204 H). Le point vient de connaissances générales, il n'a pas été recherché : à vérifier.
- **Définitions#5** : l'item ne mentionne pas l'imposition distincte l'année du divorce, de la séparation ou de la rupture du PACS (CGI, art. 6, à vérifier sur le paragraphe exact). Le point vient lui aussi de connaissances générales et n'a pas été recherché.

## Classement des exercices

Classement automatique des exercices QCM, QCM multiples et classements (tri) du chapitre selon leur nature :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 19 |
| `calcul` (montant, taux, prorata, délai) | 1 |
| `chiffre` (rappel d'un chiffre millésimé) | 1 |
| **Total** | 21 |

Aucun désaccord n'a été relevé. Seuls les 19 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
