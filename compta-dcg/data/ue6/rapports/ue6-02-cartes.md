# Cartes de notions : ue6-02 (Bilan fonctionnel, ratios et rentabilité)

*15 octobre 2026*

Fichier : `data/ue6/ue6-02.cartes.json`. Fiche de référence : `data/ue6/ue6-02.fiche.json` (non modifiée, mise à jour du 14 octobre 2026). Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été écrites à partir de la seule fiche du chapitre. Elles respectent la section 8 du contrat :
   - une seule question par carte ;
   - aucun calcul ni chiffre millésimé ;
   - chaque carte repose sur un ou deux items de la fiche (`base`), dont elle recopie `src` et `url`.

   La version enregistrée avant cette reprise comptait 30 cartes. Les cartes k19 et k20 avaient été supprimées lors d'une précédente relecture d'exactitude.
2. **Relecture de fidélité.** Un premier relecteur a contrôlé 30 cartes par rapport à la fiche. Il en a corrigé 6 et en a ajouté une (k33).
3. **Relecture d'exactitude.** C'est la présente relecture, faite par un second relecteur indépendant. Il a contrôlé les 31 cartes sur quatre points :
   - **Exactitude** au 15 octobre 2026 : Code de commerce, Code monétaire et financier, CGI, PCG modifié par le règlement ANC n° 2022-06.
   - **Ambiguïté** : la réponse attendue est-elle celle d'un correcteur du DCG ? Une autre réponse juste serait-elle possible ?
   - **Doublons et cartes sans intérêt.**
   - **Absence de calcul et de chiffre millésimé.**

   Quand l'item de fiche était lui-même en cause, la fiche n'a pas été touchée. La carte a été corrigée pour rester exacte tout en restant portée par ses items de base, et l'item est signalé plus bas.
4. **Recherches.** Une seule recherche web a été faite, limitée à anc.gouv.fr (détail plus bas). Les autres points ont été vérifiés avec le plan comptable du dépôt (`data/pcg/`).

Validation : `node validate.js data/ue6/ue6-02.cartes.json` renvoie « ✓ data/ue6/ue6-02.cartes.json (cartes, 30 (9 déf.)) ».

## Bilan

| Indicateur | Valeur |
|---|---|
| Cartes contrôlées | 31 |
| Cartes au final | 30 |
| Définition (`def`) | 9 |
| Compréhension (`comp`) | 21 |
| Corrigées par la relecture d'exactitude | 6 (k06, k09, k16, k17, k26, k27) |
| Supprimées | 1 (k33) |
| Ajoutées | 0 |
| Identifiants libres | k19, k20, k33 (pas de renumérotation) |

Chacun des huit items de la section « Définitions » a au moins une carte. Les « Règles essentielles » sont toutes couvertes, sauf la n° 11.

**Items de la fiche sans carte**

- **Règles essentielles#11 et Ce qui a changé récemment#3** : retraitements automatisés de la Banque de France. La carte k33 a été supprimée (voir plus bas) et l'item #3 est douteux.
- **Chiffres et seuils#2** : taux normal de l'IS, qui peut changer d'une loi de finances à l'autre.
- **Chiffres et seuils#3** : repère Insee millésimé 2021.
- **Ce qui a changé récemment#2** : calendrier du programme, sans notion à retenir.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis s'arrête au milieu de la raison de l'ajout de k33. La ligne k33 a été reconstituée à partir du fichier.

| Cible | Problème | Correction |
|---|---|---|
| k03 | Le « donc » inversait la logique de Règles essentielles#1 : il présentait la valeur brute des actifs comme une conséquence de la raison donnée, alors que la fiche pose les deux règles côte à côte. La seconde phrase reprenait aussi en partie la question. | Nouvelle réponse : « Parce qu'ils représentent une ressource conservée par l'entreprise. Ils sont ajoutés aux ressources stables avec les provisions, tandis que les immobilisations et l'actif circulant sont retenus pour leur valeur brute. » |
| k17 | La réponse (13 mots) était jugée trop pauvre et ne citait pas les comptes que nomme Règles essentielles#8. | Ajout de la phrase : « Depuis le PCG 2025, les intérêts courus sur emprunts sont enregistrés aux comptes 1618, 1638 ou 1648 selon la nature de l'emprunt (avant 2025 : 1688). » |
| k21 | La carte donne la définition des ratios de délais clients et fournisseurs de la Banque de France : c'est une définition. | Type changé de `comp` en `def`. |
| k22 | L'exemple « créances clients et chiffre d'affaires tous deux TTC » venait d'une connaissance extérieure à la fiche (Points de vigilance#2). | Nouvelle réponse : « Que le numérateur et le dénominateur sont exprimés sur la même base (TTC ou HT). C'est la règle d'homogénéité des ratios de rotation à respecter, à l'examen, avant toute conversion en jours. » |
| k26 | La réponse omettait l'impôt, alors que Règles essentielles#14 écrit la rentabilité financière après impôt. | Seconde phrase : « L'écart Re − i, multiplié par le rapport dettes / capitaux propres, s'ajoute alors à Re ; le total, diminué de l'IS au taux normal, donne la rentabilité financière après impôt. » |
| k27 | « Incorporelles et corporelles » ne figure pas dans la fiche (Ce qui a changé récemment#1). | Retour à la formule de la fiche, « les cessions d'immobilisations passent en exploitation », et ajout de « (bilan, compte de résultat, annexe) ». Le relecteur a signalé le problème de fond dans les points de fiche. |
| k33 (ajout) | Règles essentielles#11 n'avait pas de carte. *(Raison tronquée dans le résultat transmis.)* | Carte `comp` sur les postes visés par les retraitements automatisés de la Banque de France. Base : Règles essentielles#11 et Ce qui a changé récemment#3. |

## Corrections de la relecture d'exactitude

| Cible | Problème | Correction | Source |
|---|---|---|---|
| k06 | La trésorerie nette était définie comme les seules disponibilités moins le compte 519. Cette définition est incomplète : dans l'analyse usuelle, la trésorerie active comprend aussi les VMP. Elle contredisait aussi k12, selon laquelle le bilan fonctionnel ajoute les effets escomptés non échus à la trésorerie passive. | Nouvelle réponse : « La trésorerie active, notamment les disponibilités, diminuée de la trésorerie passive : concours bancaires courants et soldes créditeurs de banques (compte 519), auxquels le bilan fonctionnel ajoute les effets escomptés non échus. » Base : Définitions#4 et Règles essentielles#4 (`src` et `url` inchangés). | Fiche : Définitions#4 et Règles essentielles#4 ; cohérence avec k12 |
| k09 | L'article L. 313-7, 2°, ne vise que les biens immobiliers **à usage professionnel**. La carte visait tous les biens immobiliers. | Nouvelle réponse : « … de matériel d'outillage ou de biens immobiliers à usage professionnel… ». Le reste est inchangé. | C. mon. fin., art. L. 313-7, 1° et 2° |
| k16 | Lors d'une augmentation de capital, le minimum du quart ne porte que sur la valeur nominale. La prime d'émission doit, elle, être libérée en totalité à la souscription. La question parlait des « apports en numéraire » : si l'apport comprend une prime, « le quart au moins » devenait inexact. | La question est délimitée : « Dans une SA, quelle fraction minimale de la valeur nominale des actions de numéraire doit être libérée à la constitution et lors d'une augmentation de capital ? ». La réponse est inchangée. | C. com., art. L. 225-3 et L. 225-144 |
| k17 | Deux problèmes. (1) La question citait le compte 5186, absent du plan de comptes du PCG : les intérêts courus à payer vont en 5181, et ceux des concours bancaires courants en 5198. (2) La phrase ajoutée par la première relecture laissait croire que tous les intérêts courus sur emprunts vont en 1618, 1638 ou 1648 et que le compte 1688 a disparu. Or il subsiste pour les autres emprunts et dettes assimilées (Ce qui a changé récemment#0). Cette phrase répétait en outre k18 (1648 au lieu de 1688). | Nouvelle question, sans numéro de compte : « Comment le bilan fonctionnel classe-t-il les intérêts courus non échus sur emprunts et les intérêts courus à payer sur concours bancaires ? ». Nouvelle réponse : « Ils sont retirés des dettes financières, où les range le bilan comptable, et classés en dettes hors exploitation. » | Plan comptable du dépôt : `classe5.json` (518, 5181, 5188, 519, 5198) et `classe1.json` (1648, 1688) ; fiche : Ce qui a changé récemment#0 |
| k26 | « Diminué de l'IS au taux normal » n'est vrai que pour une société qui ne bénéficie pas du taux réduit des PME sur la première tranche de bénéfice. | Nouvelle formulation : « … le total, net de l'impôt sur les sociétés, donne la rentabilité financière après impôt ». La condition (Re > i) ne change pas, et la carte ne cite aucun taux. | CGI, art. 219, I (taux normal et taux réduit des PME) |
| k27 | Deux problèmes. (1) La formule « les cessions d'immobilisations passent en exploitation », rétablie par la première relecture, est fausse pour les immobilisations financières, dont les cessions relèvent du résultat financier (6671 et 7671). Seules les immobilisations incorporelles et corporelles passent en exploitation (657 et 757). (2) La question « Pourquoi le règlement… modifie-t-il la lecture du résultat d'exploitation ? » admettait d'autres réponses justes : la nouvelle définition du résultat exceptionnel et le classement de la quote-part des subventions d'investissement en 747 modifient aussi ce résultat. | Nouvelle question : « Dans quel résultat le règlement ANC n° 2022-06 classe-t-il les cessions d'immobilisations incorporelles et corporelles ? ». Nouvelle réponse : « En résultat d'exploitation, pour les exercices ouverts à compter du 1er janvier 2025 : la lecture du résultat d'exploitation utilisé dans la rentabilité économique en est modifiée. Ce règlement modernise les états financiers (bilan, compte de résultat, annexe). » | Règlement ANC n° 2022-06 ; plan comptable du dépôt : `classe6b.json` et `classe7b.json` (657, 757, 6671, 7671) |
| k33 (supprimée) | k33 reprend la carte k20, déjà supprimée lors de la précédente relecture d'exactitude. C'est une liste à apprendre par cœur, tirée d'une note méthodologique interne de la Banque de France : un correcteur du DCG ne l'attend pas, et on ne peut pas la retrouver par raisonnement. La seconde phrase (« au niveau de chaque entreprise des groupes à tête française ») mélange deux items et décrit mal la procédure. Enfin, Ce qui a changé récemment#3 est douteux (« depuis 2025 » non établi, pas d'URL). | Carte supprimée. L'identifiant reste libre. | Contrat §8 ; fiche : Règles essentielles#11 et Ce qui a changé récemment#3 |

**Cartes contrôlées et maintenues sans changement** : k01 à k05, k07, k08, k10 à k15, k18, k21 à k25, k28 à k32.

- k04, k05, k07 et k08 renvoient au « tableau de financement du PCG ». La recherche n° 1 confirme que la version du PCG au 1er janvier 2025 contient toujours un chapitre consacré au tableau de financement.
- k18 (1648 au lieu de 1688) ne fait plus doublon avec k17, puisque la phrase sur les comptes a été retirée de k17.
- k32 recoupe en partie k02 et k28. Elle est gardée parce qu'elle est la seule carte à opposer les deux bilans.

## Recherches faites

Une recherche sur les trois autorisées.

1. `règlement ANC 2022-06 système développé tableau de financement supprimé PCG` (domaine anc.gouv.fr). Les résultats confirment que le PCG au 1er janvier 2025 comporte toujours un chapitre I « Tableau de financement ». D'après le résumé de la recherche, ce tableau est exigé des entités soumises aux articles L. 232-2 et L. 612-2 du Code de commerce. Rien n'indique que le règlement n° 2022-06 l'ait supprimé. Les cartes k04, k05, k07 et k08 sont donc maintenues. Pages consultées :
   - [Règlement ANC n° 2022-06](https://www.anc.gouv.fr/reglement-ndeg-2022-06-du-4-novembre-2022)
   - [PCG, version au 1er janvier 2025](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/PCG--1er-janvier-2025.pdf)

Les autres points ont été vérifiés sans recherche :

- **Plan comptable du dépôt** :
  - 518 « Intérêts courus » (5181 à payer, 5188 à recevoir) et 5198 « Intérêts courus sur concours bancaires courants » ; aucun compte 5186 ;
  - 1648 pour les intérêts courus sur emprunts bancaires, 1688 réduit aux autres emprunts et dettes assimilées ;
  - 657 et 757 pour les immobilisations incorporelles et corporelles, 6671 et 7671 pour les immobilisations financières.
- **Connaissance des textes** : C. mon. fin., art. L. 313-7 ; C. com., art. L. 225-3 et L. 225-144 ; CGI, art. 219, I.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Ce qui a changé récemment#1.** « Les cessions d'immobilisations passent en exploitation » doit être limité aux immobilisations incorporelles et corporelles (657 et 757). Les cessions d'immobilisations financières relèvent du résultat financier (6671 et 7671).
2. **Ce qui a changé récemment#3.** Rien n'établit le « depuis 2025 » : la date d'édition de la note (avril 2025) ne prouve pas que les retraitements datent de 2025. L'item n'a pas d'URL, répète Règles essentielles#11 et décrit mal la procédure (« groupes à tête française »). À vérifier ou à retirer.
3. **Règles essentielles#8.** Le compte 5186 n'existe pas dans le plan de comptes du PCG. Les intérêts courus à payer vont en 5181, et ceux des concours bancaires courants en 5198. La même erreur figure dans la fiche ue6-06 (5186 et 5187 au lieu de 5181 et 5188).
4. **Règles essentielles#14.** L'item est marqué `stable`, mais il contient une formule chiffrée et le taux de l'IS de 25 %. Or l'économie d'impôt ne se calcule au taux normal qu'au-delà de la tranche au taux réduit des PME. À reformuler sans taux.
5. **Chiffres et seuils#2.** Le taux normal de l'IS (25 %) est fixé par la loi de finances. Il devrait être marqué millésimé, et non `stable`.
6. **Chiffres et seuils#1 et Règles essentielles#7.** Deux corrections :
   - le « surplus » à libérer dans les cinq ans y est assimilé au compte 109, alors que la part appelée et non versée relève du compte 4562 ;
   - les fractions minimales (moitié, quart) portent sur la **valeur nominale** des actions de numéraire. Lors d'une augmentation de capital, la prime d'émission est libérée en totalité à la souscription (C. com., art. L. 225-144).
7. **Définitions#4.** La trésorerie nette y est réduite aux disponibilités moins le compte 519. Il manque les VMP en trésorerie active. L'item contredit aussi Règles essentielles#4, qui ajoute les effets escomptés non échus à la trésorerie passive.
8. **Définitions#5.** L'article L. 313-7, 2°, vise les biens immobiliers **à usage professionnel**. Le texte précise en outre que le bailleur « en demeure propriétaire » et que le prix tient compte « au moins pour partie » des loyers versés.
9. **Définitions#3.** Sous le titre « Besoin en fonds de roulement », l'item range la variation « trésorerie » parmi les composantes du BFR. Il faudrait dire que la seconde partie du tableau de financement distingue les variations du BFR (exploitation, hors exploitation) et la variation de la trésorerie.

## Classement des exercices

Un classement automatique a porté sur les 18 exercices de type QCM, QCM multiple et classement du chapitre :

| Nature | Nombre |
|---|---|
| notion | 13 |
| calcul | 5 |
| chiffre | 0 |

**Désaccord tranché.** L'exercice **#22** (« Une entreprise a une rentabilité économique de 5 % et emprunte à 7 %. Quel est l'effet de l'endettement sur sa rentabilité financière ? ») a été classé notion par un classement et calcul par l'autre. Il est retenu en **calcul** et sort donc des révisions espacées. La notion qu'il illustre (un levier n'est favorable que si la rentabilité économique dépasse le taux de la dette) reste révisée par la carte k26.

Les 13 exercices de nature notion entrent dans les révisions espacées, avec les 30 cartes.
