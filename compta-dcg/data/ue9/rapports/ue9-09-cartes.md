# Cartes de notions : ue9-09 (Organisation comptable et documents de synthèse)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-09.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte des items de la fiche : mêmes conditions, mêmes exceptions, même vocabulaire juridique. Elle n'a fait aucune recherche web. Elle a contrôlé 35 cartes et en a corrigé deux (k08 et k22), sans en supprimer ni en ajouter.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié les points suivants :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : Code de commerce, LPF, CGI, BOFiP, ordonnance n° 2009-79, PCG modifié par le règlement ANC n° 2022-06 ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, ou une autre réponse juste était-elle possible ?
   - les doublons, les cartes sans intérêt et les cartes purement mécaniques ;
   - l'absence de calcul, d'écriture chiffrée et de chiffre millésimé.

   Le jeu relu intégrait déjà les retouches d'une passe d'exactitude antérieure : « en principe » pour k19, « sauf notamment » pour k24, « sauf exceptions » pour k02, la phrase sur le refus d'approbation retirée de k29, « principaux » pour k30. Cette relecture les a contrôlées et conservées.
4. **Recherches.** Une seule recherche WebSearch a été faite, limitée à `legifrance.gouv.fr`, sur l'article L. 232-25 du Code de commerce (voir « Recherches »).
5. **Validation.** `node validate.js data/ue9/ue9-09.cartes.json` → « ✓ data/ue9/ue9-09.cartes.json (cartes, 35 (13 déf.)) ».

## Bilan

- **Nombre de cartes : 35**, le maximum du contrat. Il y a 13 cartes `def` et 22 cartes `comp`.
- **Identifiants.** k35 est supprimée et laisse un trou. k36 est ajoutée. Aucune carte n'a été renumérotée.
- **Couverture de la fiche :**
  - Définitions : les 7 items ont chacun au moins une carte (k01 à k07).
  - Règles essentielles : les 17 items sont couverts, sauf #15, qui est millésimé. #12 a désormais deux cartes : k22 pour le bilan et le compte de résultat, k36 pour l'ordre des rubriques du passif.
  - Chiffres et seuils : les items stables #2 et #3 sont couverts (k28 et k29).
  - Ce qui a changé récemment : les items #0, #2 et #5 sont couverts (k30, k31, k03 et k32).
  - Points de vigilance : les items #0, #1 et #2 sont couverts (k33, k25 et k34).
- **Items de fiche sans carte :**
  - **Règles essentielles#15** (liasse fiscale) : item millésimé 2026.
  - **Chiffres et seuils#0 et #1** (délais de conservation en 2026, seuils de taille) : items millésimés. La règle stable d'appréciation des seuils est portée par k28, la réforme du délai fiscal par k32.
  - **Ce qui a changé récemment#3 et #4** (décret n° 2024-152, calendrier de la facturation électronique) : items millésimés.
  - **Ce qui a changé récemment#1, #6 et #7** (règlements ANC n° 2023-03, 2025-05 et 2026-03) : items stables mais secondaires, sans place sous le plafond de 35 cartes. Les intitulés de comptes (791, 6454) relèvent des cartes du plan comptable.
  - **Points de vigilance#3** (comptes consolidés, C. com., art. L. 233-21) : sa carte k35 est supprimée (voir ci-dessous). Il s'agit d'un lien vers le DSCG, hors du programme de l'UE 9.
- **Calculs et chiffres.** Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres restants sont stables et font partie d'une règle : douze mois, une fois par mois, un ou deux mois, deux exercices consécutifs, six puis dix ans (k32).
- **Version déjà construite.** L'identifiant k35 figure encore dans `dist/DebitCredit.html`. La prochaine construction le retirera, et une éventuelle progression attachée à k35 sera perdue.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-09-k22 | La question « comment le bilan et le compte de résultat sont-ils structurés ? » était trop ouverte. On pouvait y répondre juste par autre chose que le verso, par exemple par l'ordre des postes du passif. Cet ordre figure aussi dans l'item Règles essentielles#12, mais pas dans la réponse. | Nouvelle question : « Selon le Code de commerce, que doivent faire apparaître respectivement le bilan et le compte de résultat d'un commerçant ? ». La réponse ne change pas : actif et passif décrits séparément, capitaux propres distincts, puis résultat courant et résultat exceptionnel par différence, selon le modèle de l'ANC. |
| ue9-09-k08 | « au livre-journal ou dans ses journaux auxiliaires » était une inférence légèrement extérieure. La fiche (Règles essentielles#1) dit seulement que le livre-journal est détaillé en journaux auxiliaires. | Reformulé en « au livre-journal (ou dans les journaux auxiliaires qui le détaillent) », qui reprend le texte de Règles essentielles#1. |

La première relecture n'a supprimé ni ajouté aucune carte.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-09-k22 | **Ambiguïté restante.** « Que doit faire apparaître le compte de résultat ? » admet une autre réponse juste et très attendue : « le bénéfice ou la perte de l'exercice, par différence » (C. com., art. L. 123-13). La fiche ne la donne pas et le verso ne la contient pas. | Nouvelle question : « Selon le Code de commerce, que doit faire apparaître distinctement le bilan d'un commerçant, et quels niveaux de résultat son compte de résultat doit-il dégager par différence ? ». La réponse attendue est alors celle du verso : les capitaux propres, puis les éléments du résultat courant et le résultat exceptionnel. Réponse, base, `src` et `url` inchangés. | C. com., art. L. 123-13 et R. 123-192 ; Règles essentielles#12 |
| ue9-09-k28 | **Ambiguïté.** À « Comment s'apprécie la catégorie de micro, petite ou moyenne entreprise ? », un candidat répond naturellement et justement : « selon trois critères (total du bilan, chiffre d'affaires net, effectif), en ne dépassant pas deux des trois seuils ». Ce n'est pas la réponse attendue, qui porte sur l'exercice de référence et la règle des deux exercices consécutifs. | Nouvelle question : « Selon le Code de commerce, à quelle condition le fait de dépasser ou de cesser de dépasser les seuils de micro, petite ou moyenne entreprise a-t-il une incidence ? ». Nouvelle réponse : « **Le franchissement de deux des trois seuils doit se produire pendant deux exercices consécutifs.** La catégorie s'apprécie au titre du dernier exercice comptable clos et sur une base annuelle. » Base, `src` et `url` inchangés. | C. com., art. L. 123-16 et L. 123-16-1 ; Chiffres et seuils#2 |
| ue9-09-k26 | **Vrai seulement en principe.** La carte présentait la confidentialité du compte de résultat comme ouverte à toutes les petites entreprises. Or l'article L. 232-25 l'interdit aux sociétés mentionnées à l'article L. 123-16-2 et aux sociétés appartenant à un groupe au sens de l'article L. 233-16. La fiche ne le dit pas : la carte ne peut pas détailler ces exceptions. | « Les petites entreprises peuvent, **sauf exceptions**, demander que leur seul compte de résultat ne soit pas rendu public ». La partie sur les moyennes entreprises est inchangée. Base, `src` et `url` inchangés. | C. com., art. L. 232-25 (recherche 1) |
| ue9-09-k03 | **Réponse non exhaustive.** La question demandait « les missions » de l'ANC, mais la réponse n'en reprend que trois. L'article 1er de l'ordonnance n° 2009-79 en compte d'autres, par exemple la coordination des travaux théoriques et méthodologiques en matière comptable. | « Quelles sont les **principales** missions de l'ANC… ? ». Réponse inchangée. | Ordonnance n° 2009-79, art. 1er |
| ue9-09-k35 | **Quasi-doublon et hors programme.** Pour les comptes consolidés, la réponse (régularité, sincérité, image fidèle, par renvoi à L. 123-14) répète celle de k13 pour les comptes annuels. Le seul apport est l'article L. 233-21, que la fiche présente comme un « lien DSCG » : la consolidation n'est pas au programme de l'UE 9. | **Carte supprimée.** Le point de vigilance #3 reste dans la fiche. | C. com., art. L. 233-21 ; programme DCG UE 9 |
| ue9-09-k36 (ajout) | **Lacune de couverture.** L'ordre des grandes rubriques du passif (Règles essentielles#12) est une notion centrale du DCG. Il n'avait pas de carte faute de place, ce que la première relecture avait signalé. | Nouvelle carte `comp` : « Selon le Code de commerce, dans quel ordre le passif du bilan d'un commerçant présente-t-il ses grandes rubriques ? ». Réponse : « **Successivement les capitaux propres, les autres fonds propres, les provisions, les dettes**, puis les comptes de régularisation et écarts de conversion. » Base : Règles essentielles#12. `src` et `url` sont copiés de cet item. | C. com., art. L. 123-13 et R. 123-190 ; Règles essentielles#12 |

Les 30 autres cartes sont jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points suivants ont été examinés sans modification :

- **k05** (livres obligatoires). Le régime fiscal des micro-entreprises allège les obligations des personnes physiques qui y sont placées (C. com., art. L. 123-28). La question reprend toutefois la lettre de l'article R. 123-173 (« tout commerçant tient obligatoirement… »), et c'est la réponse qu'un correcteur attend. Un correcteur n'en attendrait pas d'autre.
- **k08** (ordre d'enregistrement). L'article R. 123-174 permet aussi de récapituler sur une pièce justificative unique les mouvements de même nature réalisés au même lieu et le même jour. La question porte sur l'ordre (chronologique), qui reste exact. Carte conservée dans la version de la première relecture.
- **k15** (permanence des méthodes). La réponse cite les deux exceptions du PCG sans dire que le changement à l'initiative de l'entité doit être justifié. La première phrase (« sauf cas exceptionnels, afin de donner une image fidèle ») pose ce cadre ; la fiche ne va pas au-delà.
- **k19** (indépendance des exercices). « En principe » couvre l'alinéa 2 de l'article L. 123-21 (bénéfice sur une opération partiellement exécutée).
- **k02, k23 et k24** (annexe). Les questions sont distinctes : composition des comptes annuels, rôle de l'annexe, entreprises dispensées. « Sauf exceptions » et « sauf notamment » couvrent les entités de l'article L. 123-16-2, que la fiche ne cite pas pour l'annexe.
- **k25** (confidentialité des micro-entreprises). Les deux exceptions sont exactes (L. 123-16-2 et sociétés de gestion de titres) ; la règle « ne dispense pas du dépôt » aussi.
- **k27** (FEC) et **k32** (L. 102 B, de six à dix ans). Ces cartes sont conformes aux recherches de la relecture finale de la fiche (`rapports/ue9-09.md`, recherches 1, 2 et 8). Aucune nouvelle recherche n'était nécessaire.
- **k13 et k14, k17 et k18, k30 et k31, k08 et k09.** Dans chaque paire, les deux cartes reposent sur le même item mais posent deux questions différentes : principe et effet, ou règle et mise en œuvre.
- **k22 et k36.** Elles reposent sur le même item (Règles essentielles#12) mais ne se recoupent pas : la première porte sur le contenu du bilan et du compte de résultat, la seconde sur l'ordre des rubriques du passif.

## Recherches

Une seule recherche WebSearch a été faite (quota : 3), avec `allowed_domains` limité à `legifrance.gouv.fr`.

1. **« Code de commerce article L232-25 petites entreprises "compte de résultat qu'elles déposent ne sera pas rendu public" groupe L. 233-16 »** (legifrance.gouv.fr). Résultat : la page de l'article L. 232-25 (LEGIARTI000038611013, version en vigueur depuis le 24 mai 2019, issue de la loi n° 2019-486 dite PACTE). Elle confirme trois points :
   - les petites entreprises au sens de l'article L. 123-16 peuvent demander que leur compte de résultat ne soit pas rendu public. Les sociétés mentionnées à l'article L. 123-16-2 en sont exclues, de même que les sociétés appartenant à un groupe au sens de l'article L. 233-16 ;
   - les micro-entreprises peuvent déclarer que leurs comptes annuels ne seront pas rendus publics ;
   - les moyennes entreprises peuvent rendre publique une présentation simplifiée de leur bilan et de leur annexe.

   Cette recherche fonde la correction de k26. Elle confirme aussi le verbe « demander » de la fiche pour les petites entreprises, qui est conservé.

## Points à reprendre dans la fiche

1. **Règles essentielles#14 et Points de vigilance#1 (L. 232-25, petites entreprises).** La faculté de ne pas rendre public le compte de résultat est présentée sans exception. Or l'article L. 232-25 en écarte les sociétés mentionnées à l'article L. 123-16-2 et les sociétés appartenant à un groupe au sens de l'article L. 233-16 (recherche 1). La carte k26 est délimitée par « sauf exceptions » en attendant.
2. **Règles essentielles#13 (dispense d'annexe).** Seule l'exception des sociétés de gestion de titres est citée, sans renvoi à l'article L. 123-16-2, alors que l'item #14 y renvoie. Les cartes k02 et k24 sont délimitées (« sauf exceptions », « sauf notamment »).
3. **Règles essentielles#9 (C. com., art. L. 123-21).** « Seul le bénéfice réalisé à la date de clôture peut être inscrit » se lit comme une règle sans exception. Or l'alinéa 2 permet d'inscrire le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, à certaines conditions. La carte k19 garde « en principe ».
4. **Chiffres et seuils#3 (dépôt au greffe), à vérifier.** Le dépôt d'une copie de la délibération en cas de refus d'approbation y est présenté comme propre aux sociétés par actions (L. 232-23), alors que l'article L. 232-22 paraît prévoir la même règle pour les SARL. Par ailleurs, « avec notamment le rapport des commissaires aux comptes » gagnerait à préciser « le cas échéant ». La carte k29 ne reprend plus la règle du refus d'approbation.
5. **Définitions#4 (livres obligatoires), à envisager.** L'item pourrait signaler que les personnes physiques placées sous le régime fiscal des micro-entreprises (C. com., art. L. 123-28) bénéficient d'obligations allégées. L'item de vigilance #2 cite déjà cet article.
6. **Ce qui a changé récemment#1, #6 et #7** (règlements ANC n° 2023-03, 2025-05 et 2026-03) : ces items n'ont pas de carte, faute de place sous le plafond de 35. Le point relevé par la première relecture sur Règles essentielles#12 (ordre du passif) est en revanche réglé par la nouvelle carte k36.

## Classement des exercices

Le classement automatique des 22 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 19 | oui |
| `calcul` | 0 | non |
| `chiffre` | 3 | non |

Aucun désaccord n'a été relevé entre les classeurs. Les 19 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 3 exercices de nature `chiffre` (rappel d'un chiffre millésimé) restent dans le chapitre mais ne sont pas proposés en révision. Aucun de ces exercices ne demande de calcul.
