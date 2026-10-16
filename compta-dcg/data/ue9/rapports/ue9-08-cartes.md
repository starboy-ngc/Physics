# Cartes de notions : ue9-08 (Financement, placements, subventions et effets de commerce)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-08.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte (`t` et `cite`) des items de la fiche. Elle n'a fait aucune recherche web. Elle a contrôlé 35 cartes et en a corrigé une (k20), sans suppression ni ajout.
3. **Relecture d'exactitude (reprise).** Une seconde relecture, indépendante, a repris les 35 cartes une à une, sous l'angle d'un expert-comptable et juriste au 15 octobre 2026. Elle a vérifié trois points :
   - l'exactitude en droit et en comptabilité (Code de commerce, CGI, BOFiP, PCG modifié par les règlements ANC n° 2022-06 et n° 2024-07) : rien de faux, de périmé, ou de vrai seulement dans un cas particulier non dit ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt, y compris avec les cartes des autres chapitres de l'UE9 (ue9-01, ue9-02, ue9-04, ue9-06, ue9-07), puisque toutes les cartes se retrouvent dans les mêmes révisions espacées.

   Elle a aussi vérifié qu'aucune carte ne demande de calcul, d'écriture chiffrée ni de chiffre millésimé. Elle a fait deux recherches WebSearch, limitées à legifrance.gouv.fr et anc.gouv.fr (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-08.cartes.json` : ✓ (35 cartes, 7 déf.).

**Historique.** Ce jeu a déjà connu une première série de relectures :
- une relecture de fidélité antérieure avait corrigé k21, k22, k24 et k28 ;
- une relecture d'exactitude antérieure avait corrigé k19, k31, k33, k11, k27, k17, k24, k02 et k04, avec une recherche sur l'article 260 B du CGI.

Ces corrections sont présentes dans le fichier. La présente reprise les a relues et les conserve. Elle précise encore k11 et k27 (voir plus bas).

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. Aucune carte n'a été supprimée ni ajoutée. Aucune n'a été renumérotée.
- **Répartition : 7 cartes `def` et 28 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte. Définitions#4 en a deux (lettre de change et billet à ordre).
  - Les 18 « Règles essentielles » sont toutes couvertes.
  - Les 6 « Points de vigilance » ont chacun leur carte de compréhension.
  - Dans « Ce qui a changé récemment », les items #0 à #5 ont leur carte.
- **Items de fiche sans carte :**
  - **Chiffres et seuils#2** (inventaire au moins une fois tous les douze mois). C'est une règle générale de tenue des comptes. Son lien avec ce chapitre, le rattachement des intérêts courus, est porté par k09.
  - **Ce qui a changé récemment#6** (recodification de la TVA par l'ordonnance n° 2025-1247). L'item porte sur la numérotation des articles, pas sur une règle de fond. Une carte n'aurait demandé qu'une date. La même ordonnance a déjà sa carte dans ue9-04 (k08).
- **Chiffres et dates.** Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres restants sont stables et font partie d'une règle : un dixième, dix années. Les années citées sont des références de textes ou des dates d'entrée en vigueur : règlements n° 2022-06 et n° 2024-07, loi n° 2024-537, 1er janvier 2025, 14 mars 2025, 1er janvier 2026.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-08-k20 | La question rattachait les deux virements à l'acceptation : « l'acceptation d'une lettre de change entraîne… chez le client tiré et chez le fournisseur tireur ». Or Règles essentielles#9 ne nomme l'acceptation que chez le tiré : « chez le client (tiré), l'acceptation vire la dette de 401 à 403 ». Chez le tireur, la fiche dit seulement que « la créance passe de 411 à 413 », sans donner le fait générateur. La carte ajoutait donc une affirmation absente de la fiche. | Nouvelle question : « Pour une lettre de change acceptée, quels virements de comptes enregistrent le client tiré et le fournisseur tireur ? » (17 mots). Nouvelle réponse, qui reprend la structure de la fiche : « **Chez le client tiré, l'acceptation vire la dette du 401 au 403 « Fournisseurs – Effets à payer »** ; chez le fournisseur tireur, la créance passe du 411 au 413 « Clients – Effets à recevoir ». » La base, `src` et `url` sont inchangés. |

La première relecture n'a supprimé ni ajouté aucune carte. Elle n'a fait aucune recherche web : son seul juge était le texte (`t` et `cite`) des items de la fiche.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-08-k10 | **Ambiguïté, inexact par sous-entendu.** La question demandait « selon quel critère » le PCG répartit depuis 2022-06 les intérêts courus, avec la réponse « par nature de dette ». Elle laissait croire que le critère avait changé. Or les anciens sous-comptes du 1688 suivaient déjà la nature de la dette (16884 pour les emprunts bancaires, comme le dit la fiche). Ce qui a changé, c'est le compte, plus le critère. Un candidat pouvait aussi répondre « par nature » en pensant à l'ancien plan, et avoir juste. | Nouvelle question : « Depuis le règlement ANC n° 2022-06, dans quels comptes le PCG enregistre-t-il les intérêts courus sur emprunts, auparavant regroupés dans les sous-comptes du 1688 ? » (24 mots). Nouvelle réponse : « **Dans les comptes 1618, 1638 et 1648, selon la nature de la dette** : pour les emprunts bancaires, le 1648 remplace ainsi le 16884. Le compte 1688 ne subsiste que pour les intérêts courus sur autres emprunts et dettes assimilées. » La base, `src` et `url` sont inchangés. | Ce qui a changé récemment#2 ; plan de comptes 2026 ; contrat, section 6 |
| ue9-08-k11 | **Vrai seulement dans un cas non dit.** La fin de la réponse disait « une commission facturée avec TVA relève de cette option ». Or l'article 261 C, 1° exclut le recouvrement de créances de l'exonération : une commission qui le rémunère peut être taxable de plein droit, sans option. D'autres services bancaires ne sont pas non plus exonérés. Toute commission avec TVA ne vient donc pas de l'option. | Fin de la réponse remplacée par : « Mais un établissement bancaire peut opter pour la taxation des opérations exonérées qu'il désigne, par exemple ses commissions, qui sont alors facturées avec TVA. » La question, déjà délimitée par « en principe », la base, `src` et `url` sont inchangés. | CGI, art. 261 C, 1° (exception du recouvrement de créances, reprise par la carte elle-même) et 260 B (Règles essentielles#2) |
| ue9-08-k27 | **Ambiguïté.** La réponse opposait le coût d'entrée, converti « au cours du jour de l'opération », aux créances et dettes, converties « sur la base du dernier cours du change ». Ainsi juxtaposée, la phrase laissait croire que la dette envers le fournisseur du bien est comptabilisée dès l'origine à un autre cours que le bien. En réalité, la différence n'apparaît qu'à la clôture : la dette est alors convertie au dernier cours, le coût d'entrée ne l'est pas. | Seconde phrase : « Les créances et dettes en monnaies étrangères, elles, sont converties à la date de clôture sur la base du dernier cours du change. » Base complétée par Définitions#5 (conversion « à la date de clôture » et écarts de conversion). `src` et `url`, copiés depuis Règles essentielles#15, sont inchangés. | PCG, art. 420-1 et 420-5 (Règles essentielles#15 et Définitions#5, citation de l'article 420-5) |

Aucune carte n'a été supprimée ni ajoutée dans cette relecture.

Les 32 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Points vérifiés :
- **Code de commerce** :
  - L. 123-13 (k09) ; L. 123-18, L. 123-19 et L. 123-21 (k14, k29) ;
  - L. 511-1 et L. 512-1 (k05, k06, k34) ; L. 511-17 et l'engagement du tiré par l'acceptation (k21) ;
  - L. 511-1-1 et L. 512-1-1 (k32, entrée en vigueur au 14 mars 2025 confirmée par la recherche 2).
- **CGI** :
  - art. 42 septies (k18, k19 : imposition l'année d'attribution sans option ; étalement sur option ; solde imposable à la cession) ;
  - art. 38, 4 (k29 : écarts de conversion pris en compte dans le résultat imposable) ;
  - art. 261 C, 1° et 260 B (k11, k23), exacts au 15 octobre 2026 mais abrogés au 1er janvier 2027.
- **PCG** :
  - art. 213-8, 221-1 et 222-1 (k12 : option indépendante pour les frais d'acquisition des titres) ;
  - art. 221-6 et 222-1 (k14 : cours moyen du dernier mois pour les titres cotés) ;
  - art. 312-1 (k04, k16) ; art. 420-1, 420-5 et 420-6 (k07, k27, k28) ; art. 513-5 (k31).
- **Règlement ANC n° 2024-07** (k33) : avances conditionnées dans les « autres fonds propres », application aux exercices ouverts à compter du 1er janvier 2026, application anticipée possible (recherche 1).
- **Plan de comptes 2026** : 164, 661, 6611, 1618, 1638, 1648 (avant 2025 : 16884), 1688, 50, 503, 506, 590, 6866, 6671, 7671, 6673, 7673, 764, 74, 741, 742, 747, 131, 139, 441, 401, 403, 411, 413, 416, 5113, 5114, 6616, 627, 665, 275, 165, 476, 477, 1515, 656, 756, 666 et 766.

Cartes examinées sans être modifiées :
- **k09 et les cartes voisines** (intérêts courus). k09 recoupe ue9-04-k30 (raison du rattachement) et ue9-07-k14 (compte 1648). Elle est conservée parce qu'elle porte la règle d'inventaire propre à ce chapitre (Règles essentielles#1, point « intérêts courus » du programme). k10, corrigée, porte désormais sur le seul changement de comptes, sans répéter la règle de rattachement.
- **k01 et k08** (emprunt). La réponse de k01 rappelle la ventilation capital / intérêts que k08 demande. Mais les questions sont distinctes : la définition de l'emprunt indivis d'un côté, le piège de l'annuité de l'autre.
- **k20** (lettre de change acceptée), dans la rédaction de la première relecture. Chez le tireur, le virement de 411 à 413 a lieu en pratique à la création de l'effet ou à son retour accepté. La carte ne rattache plus ce virement à l'acceptation : elle est exacte.
- **k23** (« sans TVA »). Le principe d'exonération des intérêts d'escompte est délimité par k11 (« en principe »). La mention de k23 reprend Règles essentielles#12 et suit la présentation attendue au DCG.
- **k33 et ue9-02-k29** (autres fonds propres). Les réponses se recoupent. k33 est conservée parce qu'elle part du financement par avances conditionnées, qui relève de ce chapitre.
- **k28 et k29** (change latent). La dernière phrase de k28 annonce le traitement du gain latent, que k29 détaille, avec en plus le retraitement fiscal. Les questions sont distinctes.

## Recherches

Deux recherches WebSearch ont été faites, sur trois autorisées.

1. **« arrêté 26 décembre 2025 homologation règlement ANC n° 2024-07 autres fonds propres exercices ouverts »** (legifrance.gouv.fr, anc.gouv.fr). Résultats : [arrêté du 26 décembre 2025 (JORFTEXT000053174797)](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053174797), [page du règlement ANC n° 2024-07](https://www.anc.gouv.fr/reglement-anc-ndeg2024-07) et [version publiée au JO](https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Reglements/2024/R2024-07/REGLT_2024_07_JO.pdf). Ils confirment trois points :
   - l'homologation par arrêté du 26 décembre 2025, publié au JO du 27 décembre 2025 ;
   - l'objet du règlement selon l'ANC : « affirmer le statut de la rubrique « autres fonds propres » » ;
   - son application : « aux comptes afférents aux exercices ouverts à compter du 1er janvier 2026 », avec application anticipée possible dès sa publication. Par exception, « les dispositions prévues aux 1 et 2 de l'article 4 du présent règlement s'appliquent aux exercices ouverts à compter du 1er janvier 2025 ».

   La carte k33 est donc exacte.
2. **« article L. 511-1-1 code de commerce lettre de change forme électronique loi 2024-537 entrée en vigueur »** (legifrance.gouv.fr). Résultat : [C. com., art. L. 511-1-1 (LEGIARTI000049712602)](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049712602), en vigueur depuis le 14 mars 2025. L'article est créé par la loi n° 2024-537 du 13 juin 2024 et renvoie aux conditions des articles 15 et 16 de cette loi. L'entrée en vigueur est fixée par décret, au plus tard neuf mois après la promulgation. La carte k32 est donc exacte.

Aucune recherche n'a été faite sur k11 : la correction retire une affirmation trop absolue sans en ajouter, et la réserve du recouvrement de créances figure déjà dans la carte et dans la fiche. Les autres points de fond s'appuient sur les citations officielles de la fiche, sur son rapport de relecture (`rapports/ue9-08.md`) et sur le contrat (section 6, comptes 1618, 1638, 1648 et 1688).

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Points relevés par la première relecture (fidélité) :
1. **Règles essentielles#15 (PCG, art. 420-1).** L'item dit seulement que le coût d'entrée est converti « au cours du jour de l'opération ». Il ne mentionne pas le cas d'un achat couvert, où l'on retient le cours de couverture. La carte k27 délimite pourtant sa question par « en l'absence de couverture de change ». Il faut compléter l'item, ou vérifier la restriction, pour que la carte repose entièrement sur la fiche.
2. **Règles essentielles#11 contre Règles essentielles#2.** L'item #11 inscrit systématiquement une TVA facturée par la banque sur la commission d'encaissement (débit 44566). L'item #2 ne prévoit cette TVA que si l'établissement a opté pour la taxation (CGI, art. 260 B). Le `src` de l'item #11 ne cite ni le compte 44566 ni le compte 512. La liste « textes » de la fiche n'a pas non plus le 44566.
3. **Règles essentielles#9.** Le fait générateur du virement de 411 à 413 chez le tireur n'est pas indiqué (création de l'effet ou retour de l'effet accepté). La phrase, construite en parallèle avec l'acceptation chez le tiré, invite à rattacher les deux virements à l'acceptation.
4. **Règles essentielles#2 et Ce qui a changé récemment#6.** Les articles 261 C et 260 B du CGI, cités comme sources, sont abrogés à compter du 1er janvier 2027 (ordonnance n° 2025-1247). Les `src` des cartes k11 et k23, copiés depuis ces items, deviendront périmés quand la fiche sera mise à jour avec la nouvelle codification.

Points relevés par la relecture d'exactitude :

5. **Règles essentielles#2 (TVA et banque).** « Une commission facturée avec TVA relève de cette option » est trop absolu. Le recouvrement de créances est exclu de l'exonération par l'article 261 C, 1° : une commission qui le rémunère peut être taxable de plein droit, sans option. L'item devrait écrire « une commission peut être facturée avec TVA en vertu de cette option » et réserver ce cas. Ce point avait déjà été relevé par la relecture d'exactitude antérieure. Il est à rapprocher du point 2.
6. **Règles essentielles#15 (dernier cours du change).** L'item juxtapose le coût d'entrée, au cours du jour, et les créances et dettes, au « dernier cours du change ». Il ne dit pas que cette seconde conversion s'apprécie à la clôture. Il peut faire croire qu'une dette fournisseur est enregistrée dès l'origine à un autre cours que le bien acheté. La carte k27 s'appuie désormais aussi sur Définitions#5, qui le précise. L'item gagnerait à ajouter « à la clôture », comme l'article 420-5 le fait dans sa seconde phrase.
7. **Ce qui a changé récemment#5 (règlement ANC n° 2024-07).** La recherche 1 confirme la date d'application. Elle donne aussi deux éléments que l'item ne reprend pas :
   - l'objet du règlement selon l'ANC, « affirmer le statut de la rubrique « autres fonds propres » ». C'est plus juste que « il fait des autres fonds propres une rubrique à part entière », car la rubrique figurait déjà aux modèles de bilan des articles 821-1 et 822-1 ;
   - l'exception des 1 et 2 de l'article 4, applicables dès les exercices ouverts à compter du 1er janvier 2025.

   L'item pourrait reprendre la formule de l'ANC, citer l'exception et donner l'URL de la version publiée au JO.
8. **Rappels de la relecture d'exactitude antérieure, toujours d'actualité.**
   - Ce qui a changé récemment#3 : « le résultat exceptionnel est réservé… » est trop absolu. Le règlement n° 2022-06 y maintient aussi les écritures d'origine fiscale (687 / 787) et certaines corrections d'erreurs.
   - Définitions#3 : la formule « subvention qui finance une immobilisation acquise ou créée au moyen de la subvention » est circulaire. Elle pourrait devenir « subvention qui finance l'acquisition ou la création d'une immobilisation », comme dans la carte k04.

## Classement des exercices

Le classement automatique porte sur les 18 exercices QCM, QCM multiples et de classement du chapitre. Il donne le résultat suivant :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 13 | oui |
| `calcul` | 5 | non |
| `chiffre` | 0 | — |

**Un désaccord** a été relevé entre les classeurs :
- **Exercice #23** (traite escomptée revenue impayée, montants à reconstituer) : un classeur proposait `notion`, l'autre `calcul`. Il est classé `calcul`. C'est cohérent : il faut additionner le nominal et les frais pour choisir la bonne écriture.

Les 13 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 5 exercices de nature `calcul` (#5, #9, #23, #27, #29) restent dans le chapitre mais ne sont pas proposés en révision.
