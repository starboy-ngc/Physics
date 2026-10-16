# Cartes de notions : ue9-03 (Achats, ventes et TVA)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-03.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`). Ses champs `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Elle compare chaque carte au seul texte (`t` et `cite`) des items de la fiche : mêmes conditions, mêmes exceptions, même vocabulaire juridique. Elle ne fait aucune recherche web. Elle s'est faite en deux tours :
   - le premier tour a contrôlé 35 cartes et en a corrigé sept (voir l'historique plus bas) ;
   - la reprise a contrôlé les 35 cartes et n'en a corrigé, supprimé ou ajouté aucune.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, vérifie quatre points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 : CGI et son annexe II, Code de commerce, BOFiP, PCG modifié par le règlement ANC n° 2022-06 ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ou purement mécaniques ;
   - l'absence de calcul, d'écriture chiffrée et de chiffre millésimé.

   Elle s'est aussi faite en deux tours. Le premier tour a corrigé cinq cartes (voir l'historique). La reprise, objet de ce rapport, en a corrigé neuf. Aucun des deux tours n'a fait de recherche web (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-03.cartes.json` : ✓ (35 cartes, 8 déf.).

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. Aucune carte n'a été supprimée ni ajoutée, et aucun identifiant n'est vide.
- **Répartition : 8 cartes `def` et 27 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte.
  - Les 15 « Règles essentielles » sont toutes couvertes sauf la #13.
  - Les 5 « Points de vigilance » ont chacun leur carte de compréhension.
  - Dans « Ce qui a changé récemment », les items #0, #1, #2, #3, #4 et #6 ont leur carte.
- **Items de fiche sans carte :**
  - **Règles essentielles#13** (CA3 mensuelle, ou trimestrielle sous 4 000 € de taxe annuelle). L'item est millésimé 2026 et repose sur un seuil chiffré.
  - **Chiffres et seuils#0** (taux de TVA). Une carte se réduirait à réciter des taux.
  - **Chiffres et seuils#2 et #3** (acomptes du régime simplifié, seuils de la franchise en base). Ils sont millésimés.
  - **Chiffres et seuils#4** (conservation des pièces pendant dix ans, C. com., art. L. 123-22). La règle est stable, mais le jeu atteint déjà 35 cartes. Elle a sa carte dans le chapitre ue9-01 (k36).
  - **Chiffres et seuils#5** (conservation fiscale de six ans, LPF, art. L. 102 B). La version citée par la fiche s'arrête au 1er janvier 2027 (voir « Points à reprendre dans la fiche »).
  - **Ce qui a changé récemment#5** (abandon du seuil unique de la franchise en base). L'item est millésimé.
  - **Ce qui a changé récemment#7** (abonnements d'électricité et de gaz au taux normal). La règle tient tout entière dans un taux.
- **Ni calcul ni chiffre millésimé.**
  - Les seuls chiffres sont stables et font partie d'une règle : soixante jours et quarante-cinq jours fin de mois (k35).
  - Les dates citées sont des dates d'entrée en vigueur : 1er janvier 2023 (k05, k07), 1er septembre 2026 et 1er septembre 2027 (k30), 1er janvier 2027 (k32, k34).
  - Les écritures de k16, k17 et k19 nomment les comptes sans aucun montant.

## Corrections de la première relecture (fidélité à la fiche)

### Reprise

| cible | problème | correction |
|---|---|---|
| (aucune) | Les 35 cartes ont été comparées une à une au texte (`t` et `cite`) de leurs items de base. Chaque affirmation du verso se retrouve dans la fiche, avec ses conditions et ses exceptions : option pour les débits, conditions des débours, « lorsque le vendeur paie le transporteur », remboursement « dans les conditions fixées par décret », « si ce délai est expressément stipulé ». | Aucune. Le fichier n'a pas été modifié (git diff vide). Aucune carte n'a été supprimée ni ajoutée. |

La reprise a aussi noté deux reformulations un peu en deçà de la lettre de la fiche, mais pas infidèles. La première est k34 (« articles du CGI relatifs à la TVA »). Le texte transmis s'interrompt avant la seconde. La reprise a enfin signalé des points de la fiche, repris plus bas.

### Historique : premier tour

| cible | problème | correction |
|---|---|---|
| ue9-03-k09 | « Notamment » en tête de réponse affirmait l'existence d'autres cas de facturation obligatoire, dont la fiche (Règles essentielles#2) ne dit rien. | « Notamment » supprimé ; la réponse reprend la liste de la fiche. |
| ue9-03-k17 | « compte d'achat (compte 60) » au lieu de « (classe 60) », terme de la fiche (Règles essentielles#6). | Remplacé par « (classe 60) ». La relecture d'exactitude est ensuite revenue sur ce point (voir plus bas). |
| ue9-03-k19 | « compte de produit (compte 70) » au lieu de « (classe 70) » (Règles essentielles#7). | Remplacé par « (classe 70) ». La relecture d'exactitude est ensuite revenue sur ce point. |
| ue9-03-k22 | « notamment » devant les coûts directement attribuables, absent de la fiche (Règles essentielles#9). | « , notamment, » supprimé. |
| ue9-03-k31 | La réponse abrégeait la nature des opérations en « (biens, services ou les deux) ». | Retour au vocabulaire de la fiche : « (livraisons de biens, prestations de services ou les deux) ». |
| ue9-03-k34 | « les articles du CGI restent applicables » : la fiche ne vise que les articles relatifs à la TVA. | « les articles du CGI relatifs à la TVA restent applicables ». |
| ue9-03-k35 | La question et la réponse ajoutaient des précisions absentes de la fiche (« deux professionnels », « en règle générale », « par dérogation »). | Précisions retirées. La relecture d'exactitude a ensuite délimité le champ de la question (voir plus bas). |

## Corrections de la relecture d'exactitude

### Reprise (cette passe)

Les six premières corrections portent sur un même point : la péremption prochaine des renvois au CGI. L'ordonnance n° 2025-1247 du 17 décembre 2025 transfère la TVA dans le code des impositions sur les biens et services. L'ordonnance n° 2026-671 a reporté son entrée en vigueur au 1er janvier 2027 (fiche, Ce qui a changé récemment#6). Dans deux mois et demi, les questions qui rattachent la règle à un article du CGI renverront donc à un texte abrogé. Or les candidats de la session 2027 (programme de l'arrêté du 4 août 2025) réviseront ces cartes après cette date. Le contrat demande des cartes durables (section 3, point 2). Dans les six cas, seule la question change : les règles de fond ne bougent pas et le verso reste identique. Les champs `src`, copiés de la fiche, gardent leurs références au CGI, exactes à ce jour.

| cible | problème | correction | source |
|---|---|---|---|
| ue9-03-k01 | **Renvoi bientôt périmé.** « selon l'article 256 du CGI » : l'article est abrogé au 1er janvier 2027. Le renvoi délimitait aussi la réponse, puisque les importations et les acquisitions intracommunautaires sont également imposables. | « En règle générale, quelles opérations sont imposables à la TVA ? ». « En règle générale » délimite le champ comme le faisait le renvoi. Réponse inchangée. | CGI, art. 256, I ; ordonnances n° 2025-1247 et n° 2026-671, art. 17 (fiche, Ce qui a changé récemment#6) |
| ue9-03-k02 | **Renvoi bientôt périmé.** « au sens de l'article 256 A du CGI » : la définition de l'assujetti est unique, donc le renvoi ne délimitait rien. | « Qu'est-ce qu'un assujetti à la TVA ? ». Réponse inchangée. | CGI, art. 256 A ; idem |
| ue9-03-k14 | **Renvoi bientôt périmé.** « Selon l'article 267 du CGI ». En outre, « les réductions de prix » n'avait pas la précision de la fiche, qui parle de réductions « consenties directement aux clients ». | « Comment traite-t-on, dans la base d'imposition à la TVA, les réductions de prix consenties aux clients et les frais accessoires ? ». Réponse inchangée. | CGI, art. 267, I et II (citation de Règles essentielles#5) |
| ue9-03-k10 et ue9-03-k11 | **Renvoi bientôt inexact.** « Selon le CGI » servait à distinguer les mentions fiscales des mentions du Code de commerce (k33). Les règles de facturation de la TVA quittent le CGI au 1er janvier 2027, et la numérotation qui remplacera l'ann. II, art. 242 nonies A n'est pas connue. | « Au titre de la réglementation de la TVA, quelles mentions d'une facture… ? ». La distinction avec k33 (« Au titre du Code de commerce ») est conservée. Dans k11, « son prix et la TVA » devient « son prix et la taxe », pour éviter la répétition. Réponses inchangées. | CGI, ann. II, art. 242 nonies A, I ; `POINTS-OUVERTS.md` (ue4-05, point 3) |
| ue9-03-k12 | **Renvoi bientôt périmé.** « au regard des règles de facturation du CGI » : l'art. 289 est abrogé au 1er janvier 2027 (fiche, `textes`). | « Qu'est-ce qu'un avoir au regard des règles de facturation de la TVA ? ». Réponse inchangée. | CGI, art. 289, I-5 ; fiche, `textes` (art. 289) |
| ue9-03-k20 | **Vrai seulement dans un cas non dit.** La réponse disait : « La TVA transite par les comptes de tiers 445 […] : elle n'est ni une charge ni un produit pour l'assujetti. » C'est vrai de la TVA collectée et de la TVA déductible. La TVA non récupérable, elle, est une charge ou un élément du coût : k22 rappelle que les taxes non récupérables entrent dans le coût d'acquisition. La question ne porte que sur une vente, donc sur la seule TVA collectée. | « La TVA collectée transite par les comptes de tiers 445 « État – Taxes sur le chiffre d'affaires » : elle n'est pas un produit pour l'assujetti. » La réponse reste dans les limites de Règles essentielles#7, qu'elle restreint au cas de la question. | PCG, art. 213-8 (Règles essentielles#9 : « taxes non récupérables ») ; plan de comptes du PCG, comptes 445 et 44571 |
| ue9-03-k21 | **Une autre réponse juste était possible.** À « Comment traite-t-on un escompte de règlement figurant sur une facture de marchandises… ? », on pouvait répondre : il est déduit du coût d'acquisition des stocks. L'art. 213-31 du PCG déduit en effet les escomptes de règlement pour évaluer les stocks (fiches ue9-06 et ue10-04). La réponse attendue porte, elle, sur l'enregistrement en 665 et 765. | « Comment comptabilise-t-on un escompte de règlement figurant sur une facture de marchandises ou de services ? ». Réponse inchangée. | PCG, art. 213-31 (fiche ue9-06, Règles essentielles#5 ; fiche ue10-04, Règles essentielles#0) ; plan de comptes du PCG, comptes 665 et 765 |
| ue9-03-k23 | **Contraste ambigu.** « Il est déduit du coût d'acquisition (pas de compte 765), contrairement à l'escompte obtenu sur un achat de biens ou de services. » La phrase pouvait se lire ainsi : l'escompte obtenu sur un achat de biens n'est pas déduit du coût. Pour les stocks, c'est faux (PCG, art. 213-31). Le contraste ne vaut que pour l'enregistrement au compte 765. | « <b>Il est déduit du coût d'acquisition</b> de l'immobilisation : il n'est pas enregistré au compte 765, contrairement à l'escompte obtenu sur un achat de biens ou de services. » Le contraste porte désormais sur le compte, comme dans Points de vigilance#2. Base, `src` et `url` sont inchangés. | PCG, art. 213-8 et 213-31 ; plan de comptes du PCG, compte 765 |

Aucune carte n'a été supprimée ni ajoutée dans cette passe. Rien n'a été renuméroté.

Remarque hors chapitre : les cartes ue4-05-k01 et k02 rattachent encore leur question aux articles 256 et 256 A du CGI. Le relecteur de ce chapitre pourra appliquer la même correction.

Les 26 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Points vérifiés :

- **k03 et k04** (fait générateur, exigibilité). Elles reposent sur le même item, mais définissent deux notions distinctes.
- **k05 à k07** (exigibilité, naissance du droit à déduction). Les réponses donnent la règle générale des opérations internes, y compris les acomptes sur livraisons de biens encaissés depuis le 1er janvier 2023 (CGI, art. 269, 2-a et 2-c ; art. 271, I). L'autoliquidation et les échanges intracommunautaires sortent du programme de l'UE 9.
- **k08 et k09** (facture). La condition de possession de la facture et le cas général de l'art. 289, I-1 sont exacts ; k09 est délimitée par « En règle générale ».
- **k13, k15 et k16** (réductions et avoirs). Elles sont conformes au plan de comptes : 609, 709, 665 et 765 ; avoir de retour enregistré à l'inverse de la facture.
- **k17 et k19** (achat et vente décrits en mots). « Compte d'achat 60 » et « compte de produit 70 » sont exacts. 607 et 707 seraient plus précis pour des marchandises, mais la fiche ne cite pas 607 à cet endroit.
- **k18** (TVA sur immobilisations en 44562). Exacte : la CA3 isole cette TVA.
- **k22** (prix d'achat d'une immobilisation). La réponse ne prétend plus énumérer tout le coût d'acquisition.
- **k24** (frais de port). Les comptes 6241, 6242 et 7085 figurent bien au plan de comptes 2026 (`data/pcg/classe6a.json` et `classe7a.json`).
- **k25** (acomptes). La carte est délimitée aux commandes de marchandises, ce qui écarte les acomptes sur immobilisations (237 et 238).
- **k26 et k27** (TVA à décaisser, crédit de TVA). Les comptes 44551 et 44567 sont exacts, ainsi que le remboursement « dans les conditions fixées par décret ».
- **k28** (refacturation en 708). La réponse est conforme à l'art. 512-1 du PCG modifié et à l'art. L. 123-19 du Code de commerce.
- **k29** (débours, CGI, art. 267, II). Exacte.
- **k30 à k32 et k34** (facturation électronique, nouvelles mentions, fin du régime simplifié, recodification). Les dates et reports viennent de la fiche, vérifiée par recherche le 15 octobre 2026 (rapports ue9-03 et ue4-05). k31 ne date pas les mentions, ce qui évite le point non tranché de l'adresse de livraison (`POINTS-OUVERTS.md`, ue9-03, point 2).
- **k33 et k35** (Code de commerce). k33 donne les mentions de règlement de l'art. L. 441-9, I. k35 est délimitée par « Entre professionnels » et « en principe ».

Doublons : les paires qui se recoupent posent chacune deux questions distinctes. k13 et k21 opposent la définition au traitement. k19 et k20 opposent le comment au pourquoi. k22 et k23 opposent la règle au piège. Aucune fusion n'est justifiée.

### Historique : premier tour

| cible | problème | correction | source |
|---|---|---|---|
| ue9-03-k17 et ue9-03-k19 | « Compte d'achat (classe 60) » et « compte de produit (classe 70) » : une classe du PCG se désigne par un seul chiffre. | « compte d'achat 60 » (k17) ; « compte de produit 70 » (k19). | PCG, art. 1121-1 (plan de comptes, classes 6 et 7) |
| ue9-03-k09 | Sans « notamment », la réponse se présentait comme la liste complète des opérations à facturer. Or l'art. 289, I-1 vise aussi d'autres opérations. | La question est délimitée par « En règle générale ». | CGI, art. 289, I-1 |
| ue9-03-k22 | La liste des éléments du coût d'acquisition se présentait comme complète, alors qu'elle omet le démantèlement. | La question porte sur le prix d'achat et sur ce qu'on en déduit. | PCG, art. 213-8 |
| ue9-03-k25 | 4091 ne vaut que pour les commandes d'exploitation. Sur une immobilisation, l'acompte va en 237 ou 238. | La question est délimitée par « Pour une commande de marchandises ». | Plan de comptes 2026, comptes 237, 238 et 4091 |
| ue9-03-k35 | Champ non délimité : la règle générale entre professionnels connaît des délais propres. | La question est délimitée par « Entre professionnels » et « en principe ». | C. com., art. L. 441-10, I, et L. 441-11 |

## Recherches

Aucune recherche WebSearch n'a été faite dans cette passe, pas plus qu'au premier tour. Aucune correction ne reposait sur un doute réel :

- **Péremption des renvois au CGI.** Le calendrier de la recodification (ordonnance n° 2025-1247 ; report au 1er janvier 2027 par l'ordonnance n° 2026-671, art. 17) a été vérifié par recherche le 15 octobre 2026 lors des passes des fiches ue9-03 et ue4-05.
- **Escompte et coût d'acquisition des stocks.** La règle est déjà sourcée dans deux fiches de ce dépôt : ue9-06, Règles essentielles#5, et ue10-04, Règles essentielles#0 (PCG, art. 213-30 et 213-31).
- **TVA non récupérable.** Elle est incluse dans le coût d'acquisition selon PCG, art. 213-8, cité dans la fiche (Règles essentielles#9).
- **Comptes cités.** Ils ont été contrôlés sur le plan de comptes 2026 du dépôt (`data/pcg/`).

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée. Points relevés dans cette passe :

1. **Règles essentielles#7 (« elle n'est ni une charge ni un produit pour l'assujetti »).** C'est vrai de la TVA collectée et de la TVA déductible, pas de la TVA non récupérable, qui est une charge ou un élément du coût (Règles essentielles#9 cite les « taxes non récupérables »). Il faudrait écrire « la TVA collectée et la TVA déductible ne sont ni des charges ni des produits pour l'assujetti ».
2. **Points de vigilance#2 (escompte sur immobilisation).** « contrairement à l'escompte obtenu sur un achat de biens ou de services » ne vaut que pour l'enregistrement au compte 765. Pour l'évaluation des stocks, l'art. 213-31 du PCG déduit aussi les escomptes de règlement du coût d'acquisition (fiches ue9-06 et ue10-04). Il faudrait écrire « …contrairement à l'escompte obtenu sur un achat de biens ou de services, enregistré au compte 765 ».

Points déjà signalés par les relectures précédentes et toujours visibles dans la fiche :

3. **Règles essentielles#6 et #7 (« classe 60 », « classe 70 »).** Le terme est impropre : une classe du PCG se désigne par un seul chiffre. Il faudrait écrire « compte 60 » et « compte 70 ».
4. **Points de vigilance#4 (« Lien DSCG/UE4 »).** L'étiquette paraît fausse : l'UE 4 du DSCG est « Comptabilité et audit ». Le droit à déduction relève de l'UE 4 du DCG (Droit fiscal) et, au DSCG, de l'UE 1 (Gestion juridique, fiscale et sociale).
5. **Chiffres et seuils#5 (LPF, art. L. 102 B).** L'item est marqué « stable », mais il cite une version bornée « du 1er janvier 2023 au 1er janvier 2027 ». Il faudrait dire ce qui change au 1er janvier 2027, ou retirer la borne.
6. **Ce qui a changé récemment#4.** L'item est marqué « stable », mais contient des seuils chiffrés (1 000 000 € et 1 100 000 €) qui relèvent du millésimé. La carte k32 les évite.
7. **Ce qui a changé récemment#6 et renvois au CGI dans toute la fiche (art. 256, 256 A, 267, 269, 271, 289 ; ann. II, art. 242 nonies A).** Au 1er janvier 2027, la recodification dans le code des impositions sur les biens et services rendra ces renvois historiques. Les questions des cartes n'en dépendent plus (k01, k02, k10, k11, k12 et k14 corrigées dans cette passe). Il faudra en revanche mettre à jour les champs `src` de la fiche, puis ceux des cartes, qui en sont la copie.
8. **Règles essentielles#2 (CGI, art. 289, I-1).** L'item ne traite que du cas général, sans le dire. Le texte vise aussi d'autres opérations, comme les ventes à distance et les livraisons intracommunautaires exonérées.
9. **Règles essentielles#9 (PCG, art. 213-8).** L'item omet l'estimation initiale des coûts de démantèlement, d'enlèvement et de restauration du site.
10. **Définitions#5 (compte 4091).** Ce compte ne vaut que pour les commandes d'exploitation. L'acompte sur une commande d'immobilisation va en 237 ou 238.
11. **Chiffres et seuils#1 (délais de paiement).** L'item devrait préciser plusieurs points :
    - il s'agit de la règle générale entre professionnels (C. com., art. L. 441-10, I) ;
    - les quarante-cinq jours fin de mois supposent aussi l'absence d'abus manifeste à l'égard du créancier ;
    - il existe des délais propres (facture périodique, art. L. 441-11).
12. **Règles essentielles#10 (frais de port à l'achat).** L'item présente 6241 comme la seule imputation possible. Or les frais de transport peuvent aussi être incorporés au coût d'achat, comme frais accessoires.

## Classement des exercices

Le classement automatique porte sur les 17 exercices QCM, QCM multiples et de classement du chapitre : 14 QCM, 3 QCM multiples, aucun classement. Il donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 12 | oui |
| `calcul` | 5 | non |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé entre les classeurs.

- Les 12 exercices de nature `notion` (10 QCM et 2 QCM multiples) entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable.
- Les 5 exercices de nature `calcul` (4 QCM et 1 QCM multiple) restent dans le chapitre, mais ne sont pas proposés en révision.
- Les 11 autres exercices du chapitre (4 calculs et 7 écritures, tous de nature `calcul`) n'entrent pas dans ce classement.
