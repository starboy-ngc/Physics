# Cartes de notions : ue9-05 (Immobilisations et amortissements)

Date : 16 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `data/ue9/ue9-05.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items. Une passe antérieure avait supprimé k31 (schéma de l'écriture de sortie du bien) et ajouté k36 (passage du dégressif au linéaire).
2. **Relectures de fidélité.** Trois relectures successives ont comparé les cartes au seul texte de la fiche (`t` et `cite`), sans recherche web. Elles ont vérifié les conditions, les exceptions et le vocabulaire. Elles ont corrigé treize fois des cartes (k03, k04, k05, k08, k14, k19, k21 deux fois, k23 trois fois, k29, k36) et ajouté k35 (coûts d'emprunt). Elles n'ont rien supprimé. Le jeu comptait alors 35 cartes.
3. **Passe d'exactitude interrompue.** Une première relecture d'exactitude a modifié le fichier : ses changements figurent dans l'historique du dépôt (commit a349c08). Elle n'a laissé ni rapport ni résultat. Ses corrections ont été reconstituées en comparant le fichier avant et après elle. Elle a fusionné k23 dans k22, supprimé k23, k24 et k34, et retouché k18, k19, k30 et k33. Ses motifs ont été déduits des changements. Cette reprise a revu chacune de ces corrections et les juge exactes.
4. **Relecture d'exactitude (cette reprise).** Une relecture indépendante a contrôlé les 32 cartes restantes sous quatre angles :
   - l'exactitude en droit et en comptabilité au 16 octobre 2026 : Code de commerce, CGI et annexe II, BOFiP, PCG modifié par le règlement ANC n° 2022-06, plan de comptes 2026 ;
   - l'ambiguïté pédagogique : la réponse est-elle celle qu'attendrait un correcteur du DCG, et une autre réponse juste serait-elle possible ?
   - les doublons et les cartes sans intérêt, dans le chapitre et avec les autres chapitres, puisque les révisions espacées les mélangent ;
   - l'absence de calcul et de chiffre millésimé.

   Elle a corrigé trois cartes (k08, k28, k32). Elle n'en a supprimé ni ajouté aucune.
5. **Recherches.** Deux recherches WebSearch ont été faites, l'une limitée à bofip.impots.gouv.fr, l'autre à anc.gouv.fr (voir « Recherches »).
6. **Validation.** `node validate.js data/ue9/ue9-05.cartes.json` répond « ✓ data/ue9/ue9-05.cartes.json (cartes, 32 (10 déf.)) ». Le champ `maj` vaut « 2026-10-16 ».

## Bilan

- **Nombre de cartes : 32.** Il y en avait 35 après les relectures de fidélité. La passe d'exactitude interrompue en a retiré trois.
- **Répartition : 10 cartes `def` et 22 cartes `comp`.**
  - Les cartes `def` sont k01, k02, k03, k04, k08, k11, k13, k15, k20 et k27.
  - Les questions font de 8 à 25 mots, les réponses de 22 à 67 mots.
- **Identifiants vides.** k23, k24, k31 et k34 ont été supprimés. Ils ne seront jamais réutilisés. Aucune carte n'a été renumérotée.
- **Couverture de la fiche.**
  - Les 7 items de « Définitions » ont chacun au moins une carte : #0 k01, #1 k02, #2 k04, #3 k03, #4 k27, #5 k13, #6 k22.
  - 16 des 17 « Règles essentielles » sont couvertes, dont deux seulement en seconde base : #10 (k19 et k36) et #13 (k30). La seule sans carte est #14.
  - 5 des 6 « Points de vigilance » sont couverts : #0 k30, #1 k18, #2 k08 et k10, #3 k21, #4 k19.
  - Dans « Ce qui a changé récemment », #0 (k32), #1 (k33) et #2 (k05) sont couverts.
  - « Chiffres et seuils#2 » est couvert en seconde base par k27 : la présomption au-delà de 10 % est un chiffre stable qui fait partie de la règle.
- **Items de fiche sans carte.**
  - **Règles essentielles#14** (plus-value latente non comptabilisée). L'ancienne k24 doublait ue9-06-k09, qui pose la même question avec « en principe ». La règle est aussi portée par ue9-01-k21 et ue10-01-k18.
  - **Points de vigilance#5** (plus-values à court et à long terme, CGI, art. 39 duodecies). L'ancienne k34 doublait ue10-03-k29 presque mot pour mot, ainsi que ue4-03-k25 et ue4-04-k19. La règle est fiscale et relève de l'UE4.
  - **Chiffres et seuils#0** (coefficients 1,25 / 1,75 / 2,25). La règle « taux linéaire multiplié par un coefficient » est portée par k36. Les valeurs ont leurs cartes en ue10-03-k36 et ue4-03-k35.
  - **Chiffres et seuils#1** (tolérance pour les biens de faible valeur). Elle est déjà portée par ue10-02-k34, ue10-02-k35 et ue4-03-k15. Une quatrième carte n'apporterait rien.
  - **Chiffres et seuils#3 et #4, Ce qui a changé récemment#3.** Ces items sont millésimés.
  - **Ce qui a changé récemment#4** (règlement ANC n° 2026-03, art. 531-5). Le numéro de l'article reste à confirmer (voir les points de fiche). Le règlement a sa carte en ue9-01-k31.
  - **Règles essentielles#13** (schéma de la cession). Il n'a pas de carte propre depuis la suppression de k31. Les comptes 657, 757, 6671 et 7671 restent portés par k29, k30 et k32. Les trois étapes ont leur carte en ue10-03-k35.
- **Ni calcul ni chiffre millésimé.**
  - Les seuls chiffres sont stables et font partie d'une règle : 12 mois (k03), trois ans (k19), dix ans (k26) et 10 % (k27).
  - La date du 1er janvier 2024 (k05) est une date d'application de texte.
  - k17 et k28 citent les comptes d'une dotation, sans montant. Il s'agit d'un choix de comptes : le contrat n'interdit que l'écriture chiffrée.

## Corrections des relectures de fidélité

Ces corrections viennent de `/tmp/claude-0/-home-user-Physics/0c1ae91b-4280-5a9a-9821-a2c381198d71/scratchpad/v1/ue9-05.json`. Chaque relecture a contrôlé 34 ou 35 cartes.

| passe | cible | problème | correction |
|---|---|---|---|
| 1 | ue9-05-k04 | La réponse disait « les solutions informatiques ». Définitions#2 parle des « dépenses d'acquisition ou de création de solutions informatiques ». | Reprise du texte exact de la fiche. |
| 1 | ue9-05-k19 | La question admettait d'autres réponses justes : les immeubles d'habitation, les chantiers et les locaux professionnels sont eux aussi exclus du dégressif (Règles essentielles#10). | La question exclut ces biens de son champ (« Hormis… »). Réponse resserrée : biens d'occasion, durée normale d'utilisation inférieure à trois ans, voitures de tourisme, amortis en linéaire, et rappel de la liste de l'annexe II. La passe d'exactitude a ensuite retouché la question (voir plus bas). |
| 1 | ue9-05-k21 | La question parlait de « l'excédent d'amortissement dégressif fiscal » sans dire sur quoi portait cet excédent. | La question précise l'excédent sur l'amortissement comptable. La passe 3 l'a ensuite réécrite. |
| 1 | ue9-05-k23 | La question ne nommait pas son cadre normatif. | « Selon le PCG, que constate la dépréciation d'un élément d'actif ? » La carte a ensuite été fusionnée dans k22. |
| 1 | ue9-05-k35 (ajoutée) | Règles essentielles#5 (coûts d'emprunt, PCG, art. 213-9) n'avait pas de carte. | Carte `comp` : les coûts d'emprunt sont soit incorporés au coût de l'actif, soit comptabilisés en charges, et la méthode retenue s'applique à tous les actifs éligibles. |
| 2 | ue9-05-k03 | « soit, selon le commentaire de l'ANC… » pouvait se lire comme une alternative. | « c'est-à-dire », conformément à Définitions#3. |
| 2 | ue9-05-k05 | La question parlait des « règles du PCG sur les logiciels et les sites internet ». La fiche dit seulement « les règles sur les logiciels et les sites internet ». | « Par quel dispositif le règlement ANC n° 2023-05 remplace-t-il les règles sur les logiciels et les sites internet ? » |
| 2 | ue9-05-k08 | Le verso écrivait « des coûts directement attribuables » au lieu de « de tous les coûts ». Le second item de base (Points de vigilance#2 : l'escompte ne passe pas en produit) n'était pas repris. | « augmenté de tous les coûts directement attribuables ». Ajout de « L'escompte de règlement obtenu ne passe donc pas en produit. » |
| 2 | ue9-05-k23 | « Celle-ci » pouvait désigner la valeur actuelle ou la valeur nette comptable. | « La valeur nette comptable est alors ramenée à la valeur d'inventaire… » |
| 2 | ue9-05-k29 | « Quels comptes enregistrent la cession d'une immobilisation financière ? » admettait aussi 462, la trésorerie ou 261. | « Quels comptes de charges et de produits… ». La seule réponse est alors 6671 et 7671. |
| 3 | ue9-05-k14 | La question admettait « le linéaire » comme réponse juste mais incomplète. | « Selon le PCG, quel critère détermine le mode d'amortissement à retenir pour une immobilisation ? » La réponse commence par le rythme de consommation des avantages économiques attendus. |
| 3 | ue9-05-k21 | La question contenait le cœur de la réponse. | « Pourquoi le compte 28 n'enregistre-t-il pas la part de l'amortissement dégressif qui excède l'amortissement comptable ? » |
| 3 | ue9-05-k23 | La précision « que la dépréciation soit définitive ou non » venait du Code de commerce, alors que la question citait le seul PCG. | « Selon le PCG et le Code de commerce… » La carte a ensuite été fusionnée dans k22. |
| 3 | ue9-05-k36 | Aucune carte ne portait la règle « taux dégressif = taux linéaire × coefficient » (Règles essentielles#10). | Règles essentielles#10 ajouté en seconde base. La dernière phrase rappelle que l'annuité dégressive est calculée sur la valeur résiduelle au taux linéaire multiplié par un coefficient. |

## Corrections de la relecture d'exactitude

### Corrections appliquées par la passe interrompue (reconstituées, revues et confirmées)

Les motifs ci-dessous sont déduits des changements, faute de résultat transmis.

| cible | problème | correction | source |
|---|---|---|---|
| ue9-05-k22 et k23 (fusion) | **Doublons.** L'ancienne k22 (« Comment le PCG définit-il la valeur actuelle d'un actif ? ») doublait ue9-06-k06 et ue10-03-k13. k23 (« que constate la dépréciation d'un élément d'actif ? ») reprenait presque mot pour mot ue9-06-k05. Les deux cartes reposaient sur le même item. | Une seule carte `comp`, k22 : « Selon le PCG, à quelle valeur compare-t-on la valeur nette comptable d'une immobilisation pour savoir s'il faut la déprécier ? » Réponse : la valeur actuelle, plus élevée de la valeur vénale et de la valeur d'usage ; dépréciation et retour à la valeur d'inventaire, que la dépréciation soit définitive ou non. k23 est supprimée. | PCG, art. 214-5 et 214-6 ; C. com., art. L. 123-18 (Définitions#6) |
| ue9-05-k24 (supprimée) | **Doublon.** « Comment traite-t-on la plus-value constatée entre la valeur d'inventaire d'une immobilisation et sa valeur d'entrée ? » est la question de ue9-06-k09. Celle-ci est en outre mieux bornée (« en principe »), alors que k24 taisait la réévaluation, que l'article L. 123-18 prévoit dans son dernier alinéa. | Supprimée, sans renumérotation. | C. com., art. L. 123-18 et L. 123-21 (Règles essentielles#14) |
| ue9-05-k34 (supprimée) | **Doublon d'une règle fiscale.** La qualification des plus-values (art. 39 duodecies) est portée par ue10-03-k29, presque mot pour mot, et par ue4-03-k25 et ue4-04-k19. Dans ce chapitre, Points de vigilance#5 n'est qu'un renvoi vers l'UE4 et le DSCG. | Supprimée, sans renumérotation. | CGI, art. 39 duodecies (Points de vigilance#5) |
| ue9-05-k18 | **Question de récitation.** « Que prévoit l'article L. 123-20… ? » appelait la phrase du texte, déjà apprise avec ue9-01-k20. | Question de qualification : « Une entreprise dont le bénéfice est absent ou insuffisant peut-elle différer la dotation aux amortissements de ses immobilisations pour améliorer son résultat ? » Verso : « Non : les amortissements sont obligatoires », puis l'article. | C. com., art. L. 123-20 (Points de vigilance#1) |
| ue9-05-k19 | **Champ trop étroit.** « Quels biens d'une entreprise industrielle… » laissait croire que la règle ne vise que les entreprises industrielles. Or l'éligibilité au dégressif dépend surtout de la nature du bien, c'est-à-dire de la liste de l'annexe II. | « quels biens d'équipement sont exclus de l'amortissement dégressif fiscal ? », comme dans l'article 39 A. Réponse inchangée. La recherche n° 1 a confirmé l'exclusion des voitures de tourisme. | CGI, art. 39 A ; CGI, ann. II, art. 22 (Points de vigilance#4, Règles essentielles#10) |
| ue9-05-k30 | **Imprécision.** « l'amortissement de l'exercice » : la règle de Points de vigilance#0 (dotation jusqu'à la date de cession) est une règle comptable. L'amortissement fiscal (dégressif, dérogatoire) a ses propres règles pour l'exercice de cession, que la fiche ne traite pas. | « l'amortissement comptable de l'exercice ». | PCG, art. 214-13 (Points de vigilance#0) |
| ue9-05-k33 | **Règle présentée comme absolue.** Le même item ne garde en exploitation, lorsque l'événement est majeur et inhabituel, que les indemnités qui compensent des charges d'exploitation. Toute indemnité d'assurance ne va donc pas au 7587. | « comment est en principe comptabilisée… ». Réponse inchangée. | Règlement ANC n° 2022-06 ; PCG, art. 513-5 (Ce qui a changé récemment#1) |

### Corrections de cette reprise

| cible | problème | correction | source |
|---|---|---|---|
| ue9-05-k08 | **Vrai seulement dans un cas particulier non dit.** À la question « De quoi se compose le coût d'acquisition… ? », le verso donnait une composition fermée : le prix d'achat « augmenté de tous les coûts directement attribuables ». Or, lorsqu'une obligation de démantèlement ou de remise en état du site existe, son estimation initiale entre aussi dans le coût d'entrée, en contrepartie d'une provision. La fiche n'en parle pas. | « <b>augmenté notamment de tous les coûts directement attribuables</b> ». La composition n'est plus présentée comme exhaustive, et la carte n'ajoute rien que la fiche ne dise. Le verso fait 67 mots. `src`, `url` et `base` sont inchangés. Le point est signalé dans la fiche. | PCG, art. 213-8 (Règles essentielles#2) ; règles du PCG sur les coûts de démantèlement (article à confirmer dans le recueil 2026) |
| ue9-05-k28 | **Carte sans intérêt et en doublon.** Au recto « Selon le PCG, comment constate-t-on la perte de valeur de titres immobilisés ? », la réponse « par une dépréciation » se devine. Elle double aussi ue9-06-k22, qui donne les comptes 296 et 297 pour la moins-value latente des titres immobilisés. Le seul apport propre du chapitre, l'absence d'amortissement des titres, ne venait qu'après. | Nouvelle question de distinction (25 mots) : « Selon le PCG, en quoi le traitement à l'inventaire des titres de participation et autres titres immobilisés diffère-t-il de celui d'une immobilisation corporelle amortissable ? » Verso : « <b>Les titres ne sont pas amortis</b> : leur perte de valeur n'est constatée que par une dépréciation (comptes 296 et 297), alors que l'immobilisation corporelle amortissable fait l'objet, chaque exercice, d'une dotation aux amortissements (débit 6811, crédit 28). » La base devient [Règles essentielles#16, Règles essentielles#9]. `src` et `url` restent ceux de #16. | PCG, art. 221-1 ; plan de comptes 2026, comptes 28, 296, 297 et 6811 (Règles essentielles#16 et #9) |
| ue9-05-k32 | **Règle présentée comme absolue.** « Dans quel résultat figure la cession d'une immobilisation corporelle ou incorporelle ? » ne prévoit pas d'exception. Or la carte rappelle elle-même que le résultat exceptionnel garde les produits et charges directement liés à un événement majeur et inhabituel. ue9-01-k33 pose d'ailleurs la même question avec « En principe ». | « …dans quel résultat figure <i>en principe</i> la cession… ». La réponse, la base, `src` et `url` sont inchangés. | Règlement ANC n° 2022-06 ; PCG, art. 513-5 (Ce qui a changé récemment#0) |

### Cartes jugées exactes et conservées

Cette reprise n'a pas retouché 29 cartes : k01 à k07, k09 à k22, k25 à k27, k29, k30, k33, k35 et k36. Elles ont été jugées exactes au 16 octobre 2026 et sans ambiguïté qui justifie une retouche. Points contrôlés :

- **Code de commerce.**
  - Art. L. 123-18 : valeurs d'entrée, dépréciation définitive ou non.
  - Art. L. 123-20 : amortissements même sans bénéfice.
  - Art. R. 123-178 : coût d'acquisition et coût de production.
  - Art. R. 123-181 : actif immobilisé.
  - Art. R. 123-184 : participations, présomption au-delà de 10 %.
- **PCG.**
  - Art. 211-1, 211-5 et 211-6 : actif, immobilisations incorporelles et corporelles. L'interprétation de l'ANC (utilisation de plus de 12 mois) est confirmée par la recherche n° 2.
  - Art. 212-1 : conditions de comptabilisation.
  - Art. 213-8 : frais d'acquisition et méthode de référence, frais de formation.
  - Art. 213-9 : coûts d'emprunt.
  - Art. 213-14 et 213-15 : coût de production, sous-activité exclue.
  - Art. 214-1 à 214-4, 214-13 et 214-14 : montant amortissable, valeur résiduelle significative et mesurable, mode d'amortissement, révision prospective.
  - Art. 214-3, 214-15 et 214-19 : fonds commercial non amorti par présomption, test au moins une fois par exercice, amortissement sur dix ans à défaut de durée fiable, option des petites entreprises, dépréciation jamais reprise.
  - Art. 221-1 : titres.
  - Règlements ANC n° 2022-06 et 2023-05.
- **CGI et BOFiP.**
  - Art. 39 A et annexe II, art. 22 et 23 : biens exclus du dégressif, point de départ au premier jour du mois d'acquisition.
  - BOI-BIC-AMT-20-20-30 : temps couru en jours ou en mois, passage au linéaire.
- **Plan de comptes 2026.** Comptes 145, 205, 207, 28, 296, 297, 657, 757, 6671, 7671, 6811, 68725, 78725, 721, 722 et 7587.

Cartes examinées et conservées malgré un recoupement :

- **k01 et ue9-01-k02 ; k02 et ue9-01-k04.**
  - Ces cartes posent la même question (définition de l'actif, définition de l'actif immobilisé) avec la même réponse.
  - k01 et k02 sont pourtant conservées : le contrat exige une carte au moins par item de « Définitions » (#0 et #1).
  - Reformuler k02 autour de la « destination » du bien la ferait doubler ue9-01-k05.
  - Ce doublon est à trancher au niveau de l'UE9 : il faudra garder une seule carte de chaque paire.
- **k29, k32 et ue9-01-k33.**
  - ue9-01-k33 réunit les deux réponses : cession d'une immobilisation incorporelle ou corporelle en exploitation, d'une immobilisation financière en résultat financier.
  - k29 et k32 sont conservées, parce que les cessions d'immobilisations sont un point du programme de ce chapitre (`programme.points`). C'est plutôt ue9-01-k33 qui serait à retirer.
  - La dernière phrase de k32 (résultat exceptionnel réservé aux événements majeurs et inhabituels et aux écritures fiscales) recoupe ue9-01-k24 et ue9-07-k19.
- **k22, ue9-06-k05 et ue9-06-k06.** k22 réunit la valeur actuelle et la dépréciation. Elle est conservée comme seule carte de Définitions#6, sous une forme `comp` (« à quelle valeur compare-t-on… »).
- **k08, ue9-03-k22 et ue9-03-k23.** ue9-03 interroge le prix d'achat et l'escompte. k08 donne la composition complète du coût d'acquisition dans le chapitre consacré aux immobilisations.
- **k20 et k21.** k20 définit les amortissements dérogatoires et donne leurs comptes. k21 explique pourquoi l'excédent fiscal ne passe pas au compte 28 et laisse la valeur nette comptable intacte.
- **k04 et k05.** k04 définit l'immobilisation incorporelle (Définitions#2). k05 porte sur le changement de 2023 (Ce qui a changé récemment#2).
- **Recoupements avec l'UE10.** L'UE10 reprend les mêmes notions de façon plus approfondie. Exemples : k16 et ue10-03-k08, k19 et ue10-03-k07, k20 et ue10-03-k11/k12, k33 et ue10-03-k28, k36 et ue10-03-k37, k27 et ue10-05-k01, k35 et ue10-02-k12, k09 et ue10-02-k08. Ces cartes sont conservées, parce que l'UE9 doit couvrir son propre programme. Si les révisions espacées mélangent les deux UE, ces paires seront à arbitrer d'ensemble.

## Recherches

Deux recherches WebSearch ont été faites, chacune limitée à un site officiel.

1. **« BOI-BIC-AMT-20-20-20 amortissement dégressif véhicules de tourisme exclus transport public de voyageurs »** (bofip.impots.gouv.fr).
   - Résultats : [BOI-BIC-AMT-20-20-20](https://bofip.impots.gouv.fr/bofip/4684-PGP.html/identifiant=BOI-BIC-AMT-20-20-20-20120912) (biens concernés), [BOI-BIC-AMT-20-20-20-10](https://bofip.impots.gouv.fr/bofip/4698-PGP.html/identifiant=BOI-BIC-AMT-20-20-20-10-20120912) et [BOI-BIC-AMT-20-20](https://bofip.impots.gouv.fr/bofip/4682-PGP.html/identifiant=BOI-BIC-AMT-20-20-20120912).
   - Un passage du BOFiP indique : « Les voitures de tourisme demeurent exclues du champ d'application de l'amortissement dégressif ». Les extraits restitués datent de la version de 2012. Aucune exception au profit du transport public de voyageurs n'a été trouvée.
   - Conclusion : k19 est exacte ; aucune réserve « en principe » n'est nécessaire sur les voitures de tourisme.
2. **« PCG article 211-6 immobilisation corporelle "au-delà de l'exercice en cours" durée supérieure à 12 mois commentaire »** (anc.gouv.fr).
   - Résultat : le [recueil des normes comptables françaises au 1er janvier 2026](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/Recueils/PCG_janvier2026/Recueil-PCG-Janvier-2026.pdf).
   - Selon le commentaire de l'ANC, les termes « au-delà de l'exercice en cours » de l'article 211-6 « doivent être interprétées comme une utilisation d'une durée supérieure à 12 mois ». Le texte intégral du commentaire n'a pas été restitué.
   - Conclusion : k03 est exacte. Le doute signalé par la deuxième relecture de fidélité sur Définitions#3 est levé.

Aucune autre recherche n'a été jugée nécessaire :

- **k08** (coûts de démantèlement). La correction se borne à ne plus présenter la composition comme fermée. Elle n'affirme rien de nouveau.
- **k32.** « En principe » est une réserve prudente, cohérente avec la carte elle-même et avec ue9-01-k33.
- **Autres points.** Ils relèvent de textes constants (Code de commerce, CGI et annexe II) ou du plan de comptes 2026 restitué dans `data/pcg`. La passe interrompue n'a laissé aucune trace d'éventuelles recherches.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#2 (coût d'acquisition).**
   - La composition est présentée comme complète : prix d'achat et coûts directement attribuables.
   - Le PCG intègre aussi au coût d'entrée d'une immobilisation corporelle l'estimation initiale des coûts de démantèlement, d'enlèvement et de remise en état du site, lorsqu'une obligation existe. Ces coûts ont pour contrepartie une provision.
   - Il faudrait le mentionner, avec l'article du recueil 2026 (à confirmer), ou écrire « comprend notamment ». La carte k08 a été corrigée en conséquence.
2. **Définitions#3 (12 mois).**
   - Le commentaire de l'ANC est confirmé par la recherche n° 2.
   - On peut ajouter un champ `cite` : « au-delà de l'exercice en cours » de l'article 211-6 doivent être interprétées comme une utilisation d'une durée supérieure à 12 mois. L'extrait est à recopier mot pour mot dans le recueil.
3. **Points de vigilance#5 (art. 39 duodecies).** Ce point vient des relectures de fidélité.
   - La parenthèse « (entreprises relevant de l'impôt sur le revenu) » est placée en fin de phrase. On ne sait pas si elle vise toute la règle ou seulement la seconde branche.
   - Pour les sociétés à l'IS, le régime du long terme ne vise plus, sauf cas particuliers, que certains titres (CGI, art. 219, I-a quater ; voir ue4-04-k20).
   - Il faudrait placer la précision en tête : « Pour les entreprises relevant de l'impôt sur le revenu, … ». La carte k34 est supprimée.
4. **Ce qui a changé récemment#0 (cession en résultat d'exploitation).**
   - L'item est formulé sans réserve.
   - Il faudrait préciser « en principe », ou indiquer le sort d'une cession directement liée à un événement majeur et inhabituel, puisque le même item réserve à ces événements le résultat exceptionnel.
   - La carte k32 porte désormais cette réserve.
5. **Règles essentielles#10 (dégressif, « entreprises industrielles »).**
   - L'item reprend la lettre de l'article 39 A.
   - Une phrase pourrait préciser que l'éligibilité dépend surtout de la nature du bien, c'est-à-dire de son inscription sur la liste de l'annexe II, art. 22. Les termes exacts sont à prendre dans le BOI-BIC-AMT-20-20-20-10.
   - La question de k19 parle désormais de « biens d'équipement ».
6. **Définitions#4 et Chiffres et seuils#2.** Ce point vient des relectures de fidélité.
   - L'URL Légifrance est à l'ancien format (`affichCodeArticle.do?…idArticle=LEGIARTI000006258148`).
   - Il faudrait la remplacer par `https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006258148`, puis reporter le changement dans k27.
7. **Ce qui a changé récemment#4 (règlement ANC n° 2026-03).** Ce point vient des relectures de fidélité et de `POINTS-OUVERTS.md`. Le renvoi à l'article 531-5 du PCG, alors que les autres items citent l'article 513-5, reste à confirmer.

## Classement des exercices

Le chapitre compte 26 exercices. Le classement automatique porte sur les 17 exercices `qcm`, `multi` et `tri` : 13 `qcm`, 4 `multi` et aucun `tri`. Les 9 autres (5 `calc`, 4 `ecriture`) n'entrent pas dans les révisions espacées.

| nature | nombre | exercices (index dans `exercices`) | révisions espacées |
|---|---|---|---|
| `notion` | 11 | n° 0, 7, 10, 13, 16, 17, 18, 19, 20, 21 et 22 | oui |
| `calcul` | 6 | n° 12 (coût d'acquisition chiffré), 14 (dotation complémentaire avant cession), 15 (dotation dégressive de la première année), 23 (affirmations sur un logiciel amorti en linéaire, dotations à calculer), 24 (passage du dégressif au linéaire) et 25 (résultat de cession) | non |
| `chiffre` | 0 | — | non |

Aucun désaccord n'a été relevé. Les natures enregistrées dans `data/ue9/ue9-05.json` concordent avec ce classement. Seuls les 11 exercices de nature `notion` entrent dans les révisions espacées, avec les 32 cartes et les comptes du plan comptable.
