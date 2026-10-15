# Cartes de notions : ue6-02 (Bilan fonctionnel, ratios et rentabilité)

15 octobre 2026. Fichier : `data/ue6/ue6-02.cartes.json`. Fiche de référence : `data/ue6/ue6-02.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 31 cartes (k01 à k31) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Le premier relecteur a vérifié les 31 cartes contre la fiche. Il en a corrigé 5 et ajouté une (k32).
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 32 cartes au regard du droit et des normes en vigueur au 15 octobre 2026 (Code de commerce, Code monétaire et financier, CGI, PCG modifié par le règlement ANC n° 2022-06). Il a aussi vérifié que chaque question n'appelle qu'une seule réponse, et il a écarté les doublons et les cartes purement mécaniques. Bilan : 8 cartes corrigées, 2 supprimées, aucun ajout.
4. **Recherches.** Aucune recherche web n'a été faite : aucun point ne laissait de doute réel. Les vérifications ont porté sur des données du dépôt, déjà vérifiées :
   - plan comptable `data/pcg/` : comptes 657, 757, 6671, 7671, 1648, 1688, 152 et 4562 ;
   - rapport `data/ue9/rapports/ue9-03.md` : L. 441-10 n'a pas été modifié par la loi n° 2026-403, et les règles des 60 jours et des 45 jours fin de mois sont confirmées.

`node validate.js data/ue6/ue6-02.cartes.json` : ✓ (30 cartes, 8 déf.).

## Bilan

- **30 cartes** : 8 de définition (`def`) et 22 de compréhension (`comp`). Les identifiants k19 et k20 sont libres (cartes supprimées, sans renumérotation).
- Chaque item de la section « Définitions » a au moins une carte.
- **Items de la fiche sans carte :**
  - Règles essentielles#11 et Ce qui a changé récemment#3 : retraitements automatisés de la Banque de France. La carte k20 est supprimée (voir ci-dessous) et l'item #3 est douteux.
  - Chiffres et seuils#2 : taux normal de l'IS, chiffre susceptible de changer.
  - Chiffres et seuils#3 : repère Insee millésimé 2021.
  - Ce qui a changé récemment#2 : calendrier du programme, sans notion à retenir.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| k15 | Réponse plus large que la fiche : le compte 109 y était « la part des apports en numéraire souscrits qui reste à libérer ». La SA n'était pas nommée. | « Parce qu'il ne constitue pas encore une ressource. Dans une SA, il correspond au surplus des apports en numéraire, au-delà de la fraction libérée à la souscription, qui doit être libéré dans les cinq ans. » |
| k20 | Les produits et charges financiers manquaient, alors que Règles essentielles#11 les cite. Le mot « notamment » masquait ce trou. | Liste complète : dettes financières, capitaux propres, produits et charges financiers, trésorerie active, participations. |
| k22 | Question trop ouverte (« Quelle précaution prendre… ») : d'autres réponses justes étaient possibles. | Question resserrée : « Avant de convertir en jours un ratio de rotation clients ou fournisseurs, que faut-il vérifier sur ses deux termes ? » Réponse : même base (TTC ou HT). |
| k26 | La réponse donnait la formule chiffrée de l'effet de levier après impôt et le taux de l'IS de 25 %. Cela pousse au calcul et repose sur un taux susceptible de changer. | Réponse limitée à la condition (Re supérieure à i) et au mécanisme. Base réduite à Règles essentielles#14. |
| k09 | La définition du crédit-bail omettait que le bien n'est pas à l'actif du locataire (Définitions#5). | Phrase ajoutée en fin de réponse. |
| k32 (ajout) | Opposition entre le bilan financier et le bilan fonctionnel, notion centrale absente du jeu. | Carte `comp` fondée sur Règles essentielles#13 et Définitions#1. |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k05 | La question portait sur les variations « pour analyser le besoin en fonds de roulement », mais la réponse attendue incluait la variation « trésorerie », qui ne fait pas partie du BFR. Un étudiant qui répondait « exploitation et hors exploitation » avait raison mais semblait incomplet. | Question : « Quelles variations du besoin en fonds de roulement la seconde partie du tableau de financement du PCG distingue-t-elle ? » Réponse : exploitation et hors exploitation ; la variation « trésorerie » s'y ajoute mais ne relève pas du BFR. Base complétée par Règles essentielles#0. | PCG, chapitre « Tableau de financement » |
| k11 | La réponse opposait deux traitements sans dire pourquoi le ratio est flatté. | Le mécanisme est explicité : le financement par crédit-bail n'apparaît pas dans les dettes. | C. mon. fin., art. L. 313-7 ; Banque de France, Bulletin n° 220/1 |
| k15 | La réponse assimilait le compte 109 à tout le surplus à libérer dans les cinq ans. Or la fraction appelée et non versée sort du 109 pour le compte 4562 (capital appelé, non versé). | « … c'est la part des apports en numéraire, au-delà de la fraction libérée à la souscription, que la société n'a pas encore appelée ; ce surplus doit être libéré dans les cinq ans. » | Plan de comptes PCG, comptes 109 et 4562 ; C. com., art. L. 225-3 |
| k19 (supprimée) | Rappel d'un numéro de compte (racine 152 des provisions pour charges), sans lien avec l'analyse fonctionnelle. Le jeu des comptes du plan comptable, qui entre déjà dans les révisions, contient ce compte. La nouveauté « Ce qui a changé récemment#0 » reste couverte par k18. | Carte supprimée. | Contrat §8 (pas de carte purement mécanique) |
| k20 (supprimée) | Liste à apprendre par cœur, tirée d'une note interne de la Banque de France : un correcteur du DCG n'attend pas cette réponse, et rien ne permet de la retrouver par raisonnement. L'item « Ce qui a changé récemment#3 » est en outre douteux (voir ci-dessous). | Carte supprimée. | Contrat §8 ; programme de l'UE6 |
| k22 | La seconde phrase (dettes fournisseurs rapportées aux achats retraités du crédit-bail) répétait la carte k21. | Réponse recentrée sur l'homogénéité TTC/HT, avec un exemple : créances clients et chiffre d'affaires, tous deux TTC. | Banque de France, définition des ratios |
| k23 | L. 441-10 fixe la règle générale. D'autres délais existent pour certains secteurs (transport, denrées périssables…), mais la question ne délimitait pas son champ. | Question : « Selon la règle générale de l'article L. 441-10 du Code de commerce, quels délais de paiement s'appliquent entre professionnels ? » Le lien avec le crédit clients et le crédit fournisseurs passe dans la réponse. | C. com., art. L. 441-10 (texte inchangé en 2026, cf. rapport ue9-03) |
| k27 | « Les cessions d'immobilisations passent en exploitation » n'est vrai que pour les immobilisations incorporelles et corporelles (657/757). Avec le règlement ANC n° 2022-06, les cessions d'immobilisations financières passent en résultat financier (6671/7671). | Réponse : « les cessions d'immobilisations incorporelles et corporelles passent en exploitation ». | Règlement ANC n° 2022-06 ; plan de comptes PCG 2025, comptes 657, 757, 6671, 7671 |
| k32 | La réponse reprenait mot pour mot celle de k28 (« coupure à un an tirée de l'état des échéances de l'annexe »). | Réponse réduite à l'opposition des deux classements (liquidité et exigibilité avec coupure à un an, contre valeurs brutes par cycles). | PCG, annexe ; PCG, modèle de bilan |

Les autres cartes ont été contrôlées sans changement (k01 à k04, k06 à k10, k12 à k14, k16 à k18, k21, k24 à k26, k28 à k31).

## Recherches faites

Aucune (0 sur 3 autorisées). Les points vérifiés l'ont été avec des données du dépôt, déjà vérifiées :
- Plan comptable du dépôt (`data/pcg/classe1.json`, `classe4.json`, `classe6b.json`, `classe7b.json`) :
  - 1648 « intérêts courus sur emprunts auprès des établissements de crédit » ; 1688 réduit aux autres emprunts ;
  - 657/757 pour les immobilisations incorporelles et corporelles, 6671/7671 pour les immobilisations financières ;
  - 4562 pour le capital appelé non versé.
- Rapport `data/ue9/rapports/ue9-03.md`, recherche n° 11 : aucune modification de L. 441-10 par la loi n° 2026-403 ; délais de 60 jours et de 45 jours fin de mois confirmés.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Ce qui a changé récemment#1.** « Les cessions d'immobilisations passent en exploitation » : à restreindre aux immobilisations incorporelles et corporelles (657/757). Les cessions d'immobilisations financières relèvent du résultat financier (6671/7671).
2. **Ce qui a changé récemment#3.** « Depuis 2025 » : seule la date d'édition de la note méthodologique (avril 2025) appuie cette mention, et cette date ne prouve pas que les retraitements datent de 2025. L'item n'a pas d'URL et répète Règles essentielles#11 : à vérifier ou à retirer.
3. **Règles essentielles#14.** L'item est marqué `stable`, mais il contient une formule chiffrée et le taux de l'IS de 25 %, que la fiche donne déjà en Chiffres et seuils#2. Par ailleurs, l'économie d'impôt sur les intérêts n'est calculée au taux normal qu'au-delà de la tranche au taux réduit des PME. À reformuler sans taux.
4. **Chiffres et seuils#2.** Le taux normal de l'IS (25 %) est un taux fixé par la loi de finances, susceptible de changer. Il devrait être marqué millésimé, pas `stable`.
5. **Chiffres et seuils#1 et Règles essentielles#7.** Le « surplus » à libérer dans les cinq ans y est assimilé au compte 109. Or le 109 ne retient que la part non encore appelée : la part appelée et non versée relève du compte 4562, comme le dit la leçon du chapitre.
6. **Définitions#4.** La trésorerie nette y est définie par les seules disponibilités. Dans l'analyse fonctionnelle usuelle du DCG, la trésorerie active comprend aussi les valeurs mobilières de placement, et la fiche ue6-06 les assimile à de la trésorerie. À préciser.

## Classement des exercices

Le classement automatique des exercices QCM, QCM multiples et de classement du chapitre (18 exercices) donne :

| nature | nombre |
|---|---|
| notion | 13 |
| calcul | 5 |
| chiffre | 0 |

Un désaccord a été tranché : **#22** (« Une entreprise a une rentabilité économique de 5 % et emprunte à 7 %. Quel est l'effet de l'endettement sur sa rentabilité financière ? »), classé notion par un classement et calcul par l'autre, est retenu en **calcul**. L'exercice sort donc des révisions espacées. La notion qu'il illustre (levier favorable seulement si la rentabilité économique dépasse le taux de la dette) reste révisée par la carte k26. Les 13 exercices de nature notion entrent dans les révisions espacées, avec les 30 cartes.
