# Cartes de notions : ue4-03 (Les bénéfices industriels et commerciaux)

*15 octobre 2026*

## Méthode

1. **Rédaction depuis la fiche** : les cartes ont été écrites à partir de la fiche documentaire `data/ue4/ue4-03.fiche.json`, et d'elle seule. Elles suivent le contrat (section 8) :
   - une question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de fiche (`base`), dont elle recopie `src` et `url`.
2. **Relecture de fidélité** : un premier relecteur a contrôlé les 35 cartes. Son seul juge était le texte des items de la fiche. Il a vérifié que chaque carte dit ce que dit la fiche, sans rien y ajouter, et respecte la forme du contrat. Il n'a fait aucune recherche.
3. **Relecture d'exactitude** (la présente) : un second relecteur, indépendant, a repris les 35 cartes sous quatre angles :
   - **Exactitude** : la carte est-elle juste au regard du droit en vigueur au 15 octobre 2026 (CGI, BOFiP, PCG modifié par le règlement ANC 2022-06) ? Est-elle fausse, périmée, ou vraie seulement dans un cas particulier qu'elle ne dit pas ?
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG, et la seule juste ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand une correction ajoute une précision, celle-ci reste dans le vocabulaire de la fiche et, si possible, figure déjà ailleurs dans la fiche.
4. **Recherches** : une seule, limitée à legifrance.gouv.fr et bofip.impots.gouv.fr (détail plus bas). Les autres points ont été tranchés sans recherche, à partir de la fiche et du texte connu des articles.

Validation : `node validate.js data/ue4/ue4-03.cartes.json` renvoie ✓ (35 cartes, dont 6 de définition). Toutes les questions comptent de 6 à 30 mots et toutes les réponses de 8 à 70 mots.

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes au final | 35 (k01 à k35, sans trou) |
| Définition (`def`) | 6 |
| Compréhension (`comp`) | 29 |
| Cartes corrigées par la relecture de fidélité | 4 (k05, k16, k30, k31) |
| Cartes corrigées par la relecture d'exactitude | 4 (k05, k16, k29, k31) |
| Cartes supprimées | 0 |
| Cartes ajoutées | 0 (le jeu est au plafond de 35) |

**Items de la fiche sans carte** :

- **Items millésimés**, exclus par le contrat :
  - Définitions#3 (RSI, avec les seuils 2025 et 2026-2028) ;
  - Chiffres et seuils#0 (seuils des régimes BIC) et #2 (plus-values professionnelles, avec le taux 2025 des prélèvements sociaux) ;
  - Ce qui a changé récemment#0 (seuils 2026-2028), #1 (loi du 19 novembre 2024 sur les meublés de tourisme), #3 (fonds commerciaux), #4 (LFSS 2026 et plus-values à long terme) et #5 (assiette sociale des indépendants).
- **Chiffres et seuils#1** (plafonds d'amortissement des véhicules de tourisme) : l'item est stable, mais il ne contient que des montants par tranche d'émissions. En tirer une carte reviendrait à apprendre des chiffres par cœur. La règle elle-même est couverte par k13 et k14.

Chaque item stable des sections suivantes porte au moins une carte :

- Définitions (5 sur 5) ;
- Règles essentielles (17 sur 17) ;
- Points de vigilance (6 sur 6) ;
- Ce qui a changé récemment (son seul item stable, #2).

Points de vigilance#5 (renvoi de l'article 209, I à l'IS) n'est couvert qu'en partie, par k09 (rémunération des dirigeants).

## Corrections de la première relecture (fidélité)

Le premier relecteur a contrôlé 35 cartes et en a corrigé 4. Il n'en a supprimé ni ajouté aucune.

| Cible | Problème | Correction |
|---|---|---|
| k05 | La réponse contenait des précisions absentes de la fiche (Définitions#2) : « 71 % pour la fourniture de logement hors location meublée » et « 50 % pour la location meublée ». Le relecteur y a vu une connaissance extérieure, puisque le rattachement de la location meublée à 50 % ne figure que dans un item millésimé. | Réponse ramenée au texte de la fiche : « 71 % pour les ventes, 50 % pour les prestations de services et 30 % pour les meublés de tourisme non classés. Le bénéfice est égal au chiffre d'affaires diminué de l'abattement, qui ne peut être inférieur à 305 €. » |
| k16 | La parenthèse « (matériels et outillages industriels notamment) » était une connaissance extérieure. Elle remplaçait la condition de la fiche (Règles essentielles#6), « biens d'équipement normalement utilisés dans les entreprises industrielles », qui avait disparu de la réponse. | Rétablissement de la condition « biens d'équipement normalement utilisés dans les entreprises industrielles, acquis neufs, durée normale d'au moins trois ans, catégories de l'annexe II ». Les exclusions reprennent les termes de Points de vigilance#2 (« véhicules de tourisme, mobilier de bureau notamment »). |
| k30 | La question contenait une partie de la réponse : elle parlait de « transmission d'une entreprise individuelle », alors que la réponse attendue est « transmission d'une entreprise individuelle ou d'une branche complète d'activité… ». | Nouvelle question : « À quelles conditions l'article 238 quindecies du CGI exonère-t-il les plus-values professionnelles réalisées lors d'une transmission d'activité ? ». Dans la réponse, « lors de » devient « pour » ; le reste, fidèle à Règles essentielles#13, ne change pas. |
| k31 | Deux ajouts étaient jugés extérieurs à la fiche. La question limitait le champ au « loueur en meublé professionnel », alors que Ce qui a changé récemment#2 parle de « location meublée » au micro-BIC sans cette distinction. La réponse ajoutait « professionnelle » à « plus-value ». | Nouvelle question : « Pour une location meublée relevant du micro-BIC, comment les amortissements sont-ils pris en compte, y compris pour la plus-value professionnelle de cession de l'immeuble ? ». La réponse reprend mot pour mot le texte de l'item. |

## Corrections de la relecture d'exactitude

Trois de ces corrections (k05, k16, k31) portent sur des cartes que la relecture de fidélité venait de ramener au texte de la fiche. Ce texte reste en retrait du droit en vigueur. Chaque correction rétablit l'exactitude avec le moins d'ajouts possible, dans le vocabulaire de la fiche. L'item en cause est signalé plus bas.

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k05 | « 71 % pour les ventes, 50 % pour les prestations de services » est incomplet, et faux pour deux cas. La catégorie à 71 % de l'article 50-0, 1 vise aussi la **fourniture de logement** : un hôtelier, prestataire de services au sens courant, en aurait déduit à tort 50 %. À l'inverse, la location meublée est exclue de cette catégorie et relève de 50 %, sauf les meublés de tourisme non classés (30 %). La fiche dit d'ailleurs déjà cette répartition (catégories « ventes, fourniture de logement » et « autres activités » ; meublés classés et chambres d'hôtes à 50 % « comme les autres locations meublées »), mais seulement dans des items millésimés, qui ne peuvent pas servir de base. | « **71 % pour les ventes et la fourniture de logement hors location meublée ; 50 % pour les prestations de services et les autres activités, y compris la location meublée, sauf 30 % pour les meublés de tourisme non classés.** Le bénéfice est égal au chiffre d'affaires diminué de l'abattement, qui ne peut être inférieur à 305 €. » La base reste Définitions#2. | CGI, art. 50-0, 1 (1°, 1° bis et 2°), texte connu, non recherché ici ; fiche, Chiffres et seuils#0, Définitions#3 et Ce qui a changé récemment#1 |
| k16 | La réponse s'ouvrait sur « les biens d'équipement normalement utilisés dans les entreprises industrielles », présentés comme une condition cumulative. Or le critère décisif est l'appartenance aux catégories de l'annexe II (art. 22), qui comprennent aussi des biens utilisés hors de l'industrie, comme les machines de bureau ou les immeubles et matériels des entreprises hôtelières. Lue telle quelle, la carte réservait le dégressif à l'industrie. | « **Les biens d'équipement acquis neufs, dont la durée normale d'utilisation est d'au moins trois ans et qui figurent dans les catégories de l'annexe II**, pour l'essentiel des biens normalement utilisés dans les entreprises industrielles. » Les exclusions de Points de vigilance#2 suivent sans changement. La formule de la fiche est conservée, mais elle décrit les biens au lieu de poser une condition. Bases inchangées (Règles essentielles#6 et Points de vigilance#2). | CGI, art. 39 A, 1 ; CGI, ann. II, art. 22 (liste des catégories connue, non recherchée ici) ; fiche, Points de vigilance#2 |
| k29 | À la question « À quelles conditions… », la réponse omettait une condition légale : l'activité doit avoir été exercée **à titre professionnel** pendant au moins cinq ans. Une activité BIC non professionnelle, à laquelle l'exploitant ne participe pas personnellement, ne bénéficie pas de l'exonération de l'article 151 septies. | « **Une activité exercée à titre professionnel pendant au moins cinq ans et des recettes limitées** : … ». Pour rester sous 70 mots, « des recettes sous les limites légales » devient « des recettes limitées ». Le reste ne change pas. Bases inchangées (Règles essentielles#12 et Chiffres et seuils#3). | BOI-BIC-PVMV-40-10-10-20 ; BOI-BA-BASE-20-20-30-20 (version du 23 juillet 2025) (recherche n° 1) |
| k31 | La question, « Pour une location meublée relevant du micro-BIC, … y compris pour la plus-value professionnelle de cession de l'immeuble ? », laissait entendre que toute location meublée au micro-BIC dégage une plus-value professionnelle. Or le régime des plus-values professionnelles (art. 39 duodecies, source de l'item) ne joue que pour le loueur professionnel. Les plus-values du loueur non professionnel, cas le plus courant, relèvent des plus-values des particuliers (BOI-BIC-CHAMP-40-20). | Nouvelle question : « Au régime micro-BIC, comment les amortissements d'un immeuble donné en location meublée sont-ils pris en compte, y compris **lorsque** sa plus-value de cession relève du régime professionnel ? ». Le « lorsque » rend la condition explicite sans introduire de notion absente de la fiche. La réponse, copiée de l'item, ne change pas. | CGI, art. 39 duodecies (source de l'item) ; BOI-BIC-CHAMP-40-20 |

**Cartes contrôlées et maintenues** (31 cartes sans changement) :

- **Rattachement des produits (k02, k03)** : k02 nuance déjà la règle de l'achèvement des prestations par « en principe » et par les prestations continues. Les deux cartes se recoupent sur ce point, mais l'une définit la créance acquise et l'autre classe les produits par exercice : pas de doublon à supprimer.
- **Véhicules de tourisme (k13, k14)** : les cartes sont exactes. L'exception des véhicules nécessaires à l'activité en raison même de son objet (taxis, auto-écoles, loueurs) n'est pas citée. Il s'agit d'un cas marginal, et k12 enseigne déjà la clause « nécessaires à son activité » de l'article 39, 4.
- **Provisions (k21, k22)** : les cartes sont exactes. Les provisions pour retraite et celles pour indemnités de licenciement économique ne sont pas déductibles. Celles qui couvrent un licenciement pour un autre motif le sont.
- **Déficits (k33)** : la carte est exacte, mais elle ne donne pas la durée de report des déficits BIC non professionnels autres que ceux de la location meublée (voir les points de fiche).
- **Doublons apparents** : plusieurs paires de cartes reposent sur les mêmes items, mais chacune interroge un angle distinct. Aucune fusion n'est nécessaire.

  | Cartes | Angles interrogés |
  |---|---|
  | k04 / k05 | champ du micro-BIC ; abattements |
  | k06 / k07 | méthode du 2058-A ; exigence de comptabilisation |
  | k13 / k14 | véhicule acquis ; véhicule loué |
  | k16 / k17 / k35 | biens éligibles au dégressif ; comptabilisation du dérogatoire ; coefficients |
  | k18 / k19 | règle de l'amortissement minimal ; sanction |
  | k23 / k24 | reprise d'une provision déduite ; reprise d'une provision réintégrée |
  | k25 / k26 | plus-values ; moins-values à court terme |
- **Chiffres stables** : plusieurs cartes citent des chiffres fixés par la loi ou par la doctrine, sans révision annuelle. Dans chaque cas, la question porte sur la règle, ce que le contrat admet. Aucune carte ne cite un seuil révisé tous les trois ans ni le taux des prélèvements sociaux.
  - k05 : 71, 50 et 30 % ; 305 € ;
  - k15 : 500 € ;
  - k28 : 12,8 % ;
  - k29 : seuils de l'article 151 septies ;
  - k30 : seuils de l'article 238 quindecies ;
  - k34 : 6,8 points ;
  - k35 : coefficients du dégressif.

## Recherches faites

1. **CGI, art. 151 septies : condition d'exercice de l'activité** (domaines legifrance.gouv.fr et bofip.impots.gouv.fr).
   - Confirmé : l'exonération suppose une activité exercée **à titre professionnel** depuis au moins cinq ans. Seules les périodes d'exercice à titre professionnel comptent, et la durée s'apprécie activité par activité (BOI-BIC-PVMV-40-10-10-20 ; BOI-BA-BASE-20-20-30-20, version du 23 juillet 2025).
   - Confirmé aussi : les recettes s'apprécient sur la moyenne hors taxes des deux années civiles précédant la clôture de l'exercice de réalisation. La condition de cinq ans ne s'applique pas aux plus-values d'expropriation ou d'indemnités d'assurance.
   - Conséquence : k29 est corrigée.

Aucune autre recherche n'a été faite. Pour k05 (catégories de l'article 50-0) et k16 (catégories de l'annexe II, art. 22), le texte est connu et la fiche elle-même va dans le même sens. Le quota de recherche est partagé : il est resté inutilisé pour ces points.

## Points à reprendre dans la fiche

- **Définitions#2 (micro-BIC)** : l'abattement de 71 % vise les ventes **et la fourniture de logement**, hors location meublée. Celui de 50 % vise les prestations de services **et les autres activités**, y compris la location meublée (meublés de tourisme classés, chambres d'hôtes). Ces précisions ne figurent aujourd'hui que dans des items millésimés (Définitions#3, Chiffres et seuils#0, Ce qui a changé récemment#1) : il faudrait les reprendre dans cet item stable. La relecture de fidélité a supprimé de la carte ces précisions justes ; si l'item était complété, les deux relectures ne se contrediraient plus.
- **Règles essentielles#6 (dégressif)** : « réservé aux biens d'équipement normalement utilisés dans les entreprises industrielles » laisse croire à une restriction par secteur. Le critère est l'appartenance aux catégories de l'article 22 de l'annexe II. Ces catégories comprennent aussi, sauf erreur, les machines de bureau et les immeubles et matériels des entreprises hôtelières : liste à vérifier sur Légifrance avant de reformuler l'item.
- **Règles essentielles#12 et Chiffres et seuils#3 (art. 151 septies)** : il faut ajouter que l'activité doit avoir été exercée **à titre professionnel** pendant au moins cinq ans (BOI-BIC-PVMV-40-10-10-20).
  - Les deux items ne décrivent pas de la même façon la catégorie à 250 000 € : « vente de marchandises, … ou fourniture de logement » dans l'un, « vente de marchandises » seule dans l'autre. Il faudrait les harmoniser.
- **Ce qui a changé récemment#2 (location meublée et amortissements)** : ce point a été relevé par les deux relectures. L'item devrait préciser que la règle du court terme, à hauteur des amortissements réputés compris dans l'abattement, ne joue que lorsque la plus-value relève du régime professionnel, c'est-à-dire pour le loueur en meublé professionnel. Les plus-values du loueur non professionnel relèvent des articles 150 U et suivants (BOI-BIC-CHAMP-40-20).
  - La réforme de la loi de finances pour 2025 pourrait aussi y figurer : pour le loueur non professionnel, les amortissements déduits sont désormais pris en compte dans la plus-value privée. Article et exceptions à vérifier.
- **Définitions#1 (créance acquise)** : la phrase « pour les prestations de services, le produit n'est imposable que si la créance est acquise et la prestation achevée » devrait être nuancée par « en principe ». Les prestations continues et les prestations discontinues à échéances successives sont rattachées au fur et à mesure de leur exécution (Règles essentielles#0).
- **Définitions#3 (régime simplifié d'imposition)** : l'item mêle une définition stable et des seuils millésimés. Il faudrait le scinder :
  - un item stable : le RSI s'applique au-delà des seuils du micro-BIC et jusqu'aux limites de l'article 302 septies A bis, révisées tous les trois ans ; au-delà, c'est le régime réel normal ;
  - les montants, qui figurent déjà dans Chiffres et seuils#0.
- **Règles essentielles#14 (déficit BIC)** : l'item ne donne pas la durée de report des déficits BIC non professionnels autres que ceux de la location meublée non professionnelle. Il s'agit, semble-t-il, de l'année et des six années suivantes (art. 156, I-1° bis) : à vérifier sur Légifrance.

## Classement des exercices

Classement automatique, selon leur nature, des exercices QCM, QCM multiples et classements (tri) du chapitre :

| Nature | Nombre |
|---|---|
| `notion` (définition, règle, qualification, sans calcul) | 15 |
| `calcul` (montant, taux, prorata, délai) | 3 |
| `chiffre` (rappel d'un chiffre millésimé) | 3 |
| **Total** | 21 |

Aucun désaccord n'a été relevé. Seuls les 15 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus.
