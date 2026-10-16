# Cartes de notions : ue9-03 (Achats, ventes et TVA)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-03.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a comparé chaque carte au seul texte (`t` et `cite`) des items de la fiche : mêmes conditions, mêmes exceptions, même vocabulaire juridique. Elle n'a fait aucune recherche web. Elle a contrôlé 35 cartes et en a corrigé sept, sans suppression ni ajout.
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (CGI et son annexe II, Code de commerce, BOFiP, PCG modifié par le règlement ANC n° 2022-06) ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ou purement mécaniques.

   Elle a aussi vérifié l'absence de calcul, d'écriture chiffrée et de chiffre millésimé. Elle n'a fait aucune recherche web (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-03.cartes.json` : ✓ (35 cartes, 8 déf.).

## Bilan

- **Nombre de cartes : 35**, le maximum prévu par le contrat. Aucun identifiant n'est vide : aucune carte n'a été supprimée.
- **Répartition : 8 cartes `def` et 27 cartes `comp`.**
- **Couverture de la fiche.**
  - Les 6 items de « Définitions » ont chacun au moins une carte.
  - Les 15 « Règles essentielles » sont toutes couvertes sauf la #13 (voir ci-dessous).
  - Les 5 « Points de vigilance » ont chacun leur carte de compréhension.
  - Dans « Ce qui a changé récemment », les items #0, #1, #2, #3, #4 et #6 ont leur carte.
- **Items de fiche sans carte :**
  - **Règles essentielles#13** (CA3 mensuelle, ou trimestrielle sous 4 000 € de taxe annuelle). L'item est millésimé 2026 et repose sur un seuil chiffré.
  - **Chiffres et seuils#0** (taux de TVA). Une carte se réduirait à réciter des taux.
  - **Chiffres et seuils#2 et #3** (acomptes du régime simplifié, seuils de la franchise en base). Ils sont millésimés.
  - **Chiffres et seuils#4** (conservation des pièces pendant dix ans, C. com., art. L. 123-22). C'est une règle stable, mais le jeu atteint déjà le maximum de 35 cartes.
  - **Chiffres et seuils#5** (conservation fiscale de six ans, LPF, art. L. 102 B). La version citée est bornée au 1er janvier 2027 (voir « Points à reprendre dans la fiche »).
  - **Ce qui a changé récemment#5** (franchise en base : abandon du seuil unique). L'item est millésimé.
  - **Ce qui a changé récemment#7** (abonnements d'électricité et de gaz au taux normal). La règle tient tout entière dans un taux.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres qui restent sont stables et font partie d'une règle : soixante jours et quarante-cinq jours fin de mois (k35). Les dates citées sont des dates d'entrée en vigueur : 1er janvier 2023 (k05, k07), 1er septembre 2026 et 1er septembre 2027 (k30), 1er janvier 2027 (k32, k34).

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-03-k09 | La réponse commençait par « Notamment », ce qui affirme l'existence d'autres cas de facturation obligatoire. La fiche (Règles essentielles#2) n'en dit rien : c'est une connaissance extérieure. | « Notamment » est supprimé. La réponse reprend maintenant la liste de la fiche : « <b>Les livraisons de biens et prestations de services qu'il effectue pour un autre assujetti ou pour une personne morale non assujettie</b>, ainsi que les acomptes… » |
| ue9-03-k17 | La réponse écrivait « compte d'achat (compte 60) », alors que la fiche (Règles essentielles#6) dit « (classe 60) ». | Remplacé par « (classe 60) », comme dans la fiche. |
| ue9-03-k19 | La réponse écrivait « compte de produit (compte 70) », alors que la fiche (Règles essentielles#7) dit « (classe 70) ». | Remplacé par « (classe 70) », comme dans la fiche. |
| ue9-03-k22 | La réponse ajoutait « notamment » devant les coûts directement attribuables. Ce mot n'est pas dans la fiche (Règles essentielles#9, PCG art. 213-8) et laisse croire à d'autres éléments du coût. | « , notamment, » est supprimé : « On ajoute les droits de douane et taxes non récupérables et les coûts directement attribuables… ». |
| ue9-03-k31 | La réponse abrégeait « la nature des opérations » en « (biens, services ou les deux) ». La fiche (Ce qui a changé récemment#2) emploie les termes « livraisons de biens » et « prestations de services ». | Le vocabulaire de la fiche est rétabli : « (livraisons de biens, prestations de services ou les deux) ». |
| ue9-03-k34 | La réponse disait « les articles du CGI restent applicables » jusqu'au 31 décembre 2026. La fiche parle seulement des articles du CGI qui portent sur la TVA (« les articles du CGI cités dans cette fiche ») : la formule généralisait à tout le CGI. | Remplacé par « les articles du CGI relatifs à la TVA restent applicables ». |
| ue9-03-k35 | La question ajoutait deux précisions absentes de la fiche (Chiffres et seuils#1) : « deux professionnels » et « en règle générale ». La réponse ajoutait « par dérogation », qui n'y figure pas non plus. | La question devient « Selon le Code de commerce, quel délai de paiement maximal les parties peuvent-elles convenir pour régler une facture ? ». « par dérogation » est retiré de la réponse : « Soixante jours à compter de la date d'émission de la facture, ou quarante-cinq jours fin de mois si ce délai est expressément stipulé. » |

La première relecture n'a supprimé ni ajouté aucune carte.

## Corrections de la relecture d'exactitude

Trois de ces corrections reviennent en partie sur la première relecture (k17, k19 et k35). Elles ne réintroduisent aucun contenu absent de la fiche. Pour k17 et k19, elles corrigent un terme impropre que la fiche contient elle-même. Pour k35, elles délimitent le champ de la question, comme le contrat l'exige lorsqu'une règle a des exceptions.

| cible | problème | correction | source |
|---|---|---|---|
| ue9-03-k17 et ue9-03-k19 | **Terme impropre.** « Compte d'achat (classe 60) » et « compte de produit (classe 70) » : dans le PCG, une classe est désignée par un seul chiffre (classe 6, classe 7). 60 et 70 sont des comptes à deux chiffres : 60 « Achats (sauf 603) », 70 « Ventes de produits fabriqués, prestations de services, marchandises ». La première relecture avait repris le terme de la fiche, qui est lui-même inexact. | « Débit du compte d'achat 60 pour le montant hors taxes » (k17) ; « Crédit du compte de produit 70 pour le montant hors taxes collectées » (k19). Le reste des deux cartes est inchangé. | PCG, art. 1121-1 (plan de comptes 2026 : classes 6 et 7, comptes 60 et 70) ; `data/pcg/classe6a.json` et `classe7a.json` |
| ue9-03-k09 | **Vrai seulement dans le cas général, sans le dire.** Sans « notamment », la réponse se présente comme la liste complète des opérations à facturer. Or l'art. 289, I-1 du CGI vise aussi d'autres opérations, comme les ventes à distance (art. 258 A et 258 B) et les livraisons intracommunautaires exonérées, y compris envers des non-assujettis. La fiche ne cite que le cas général : la carte ne peut pas ajouter les autres. | La question délimite son champ : « En règle générale, pour quelles opérations un assujetti à la TVA doit-il s'assurer qu'une facture est émise ? ». La réponse, fidèle à Règles essentielles#2, est inchangée. | CGI, art. 289, I-1 |
| ue9-03-k22 | **Liste présentée comme complète, à tort.** La question demandait « qu'ajoute-t-on » au prix d'achat pour obtenir le coût d'acquisition. Une fois « notamment » retiré, la réponse se présentait comme exhaustive. Or l'art. 213-8 du PCG ajoute un troisième élément, l'estimation initiale des coûts de démantèlement, d'enlèvement et de restauration du site. La fiche ne le mentionne pas. | La question porte sur ce que la fiche cite mot pour mot, le prix d'achat : « Selon le PCG, que comprend le prix d'achat retenu dans le coût d'acquisition d'une immobilisation corporelle, et qu'en déduit-on ? ». Réponse : « <b>Il comprend les droits de douane et taxes non récupérables ; on en déduit les remises, rabais commerciaux et escomptes de règlement.</b> Le coût d'acquisition y ajoute les coûts directement attribuables engagés pour mettre l'actif en place et en état de fonctionner. » La réponse ne prétend plus énumérer tout le coût. Base, `src` et `url` sont inchangés. | PCG, art. 213-8 |
| ue9-03-k25 | **Vrai seulement dans un cas non dit.** « Un acompte versé à un fournisseur » est une créance en 4091 pour une commande de biens ou de services d'exploitation. Versé sur une commande d'immobilisation, il va en 237 ou 238 et figure à l'actif parmi les immobilisations. | La question délimite son champ : « Pour une commande de marchandises, comment le PCG qualifie-t-il l'acompte reçu d'un client et l'acompte versé à un fournisseur ? ». La réponse est inchangée. | Plan de comptes 2026, comptes 237, 238 et 4091 ; `data/pcg/classe2.json` et `classe4.json` |
| ue9-03-k35 | **Champ non délimité.** Le plafond de soixante jours, ou de quarante-cinq jours fin de mois, est la règle générale des délais convenus entre professionnels (C. com., art. L. 441-10, I). Il ne vaut pas pour la vente à un consommateur. Il connaît aussi des délais propres : quarante-cinq jours pour une facture périodique, délais spéciaux de l'art. L. 441-11 (denrées périssables, transport…). Sans délimitation, une autre réponse juste était possible selon le secteur. | Question : « Entre professionnels, quel délai de paiement maximal le Code de commerce permet-il en principe de convenir pour régler une facture ? ». La réponse, fidèle à Chiffres et seuils#1, est inchangée. | C. com., art. L. 441-10, I, et L. 441-11 |

Aucune carte n'a été supprimée ni ajoutée dans cette relecture.

Les 29 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- CGI, art. 256, I et 256 A ; art. 267, I et II (frais accessoires, réductions de prix, débours) ; art. 269, 2-a et 2-c (exigibilité, acomptes sur livraisons de biens encaissés depuis le 1er janvier 2023) ; art. 271, I, II et IV ; art. 289, I-5 ;
- CGI, ann. II, art. 242 nonies A, y compris les nouvelles mentions issues du décret n° 2024-1195 ;
- C. com., art. L. 441-9, I ;
- PCG, art. 512-1 dans la rédaction du règlement n° 2022-06, et compte 708 pour les refacturations ;
- plan de comptes 2026 : 401, 411, 4091, 4191, 44551, 44562, 44566, 44567, 44571, 609, 6241, 6242, 665, 707, 709, 7085 et 765.

Cartes examinées sans être modifiées :
- **k03 et k04** (fait générateur, exigibilité). Elles reposent sur le même item, mais définissent deux notions. Le rappel du fait générateur dans k04 sert la distinction entre les deux.
- **k05 et k06** (exigibilité). Les réponses donnent la règle générale des opérations internes, celle qu'attend le correcteur du DCG. Les régimes propres aux échanges intracommunautaires et à l'autoliquidation sortent du programme de l'UE 9. L'exemple de k06 (facture de juin payée en juillet) situe une période de déclaration ; il ne demande aucun calcul.
- **k10 et k11** (mentions fiscales). Elles commencent par « Notamment », comme l'item de la fiche (« comporte notamment »). C'est exact : la liste de l'art. 242 nonies A est plus longue, avec le SIREN depuis la réforme (k31) et le numéro de TVA du client dans certains cas.
- **k13 et k21, k14 et k21, k19 et k20, k22 et k23.** Les réponses se recoupent en partie, mais chaque paire pose deux questions distinctes : définition et traitement, base de TVA et comptabilisation, comment et pourquoi, règle et piège. k23 porte le piège classique de l'escompte sur immobilisation, à opposer à k21 (compte 765).
- **k21** (escompte sur achat de biens ou de services en 765). C'est le traitement du plan de comptes que les sujets du DCG attendent ; la carte ne dit rien de l'évaluation des stocks.
- **k24** (frais de port). La question porte sur les comptes que le plan « consacre » au transport : 6241, 6242 et 7085 sont la bonne réponse. L'item de fiche passe sous silence l'incorporation possible des frais de transport au coût d'achat (point signalé ci-dessous).
- **k16, k17, k19** (écritures décrites en mots). Elles nomment les comptes mouvementés sans aucun montant : ce sont des cartes de compréhension, pas des écritures chiffrées.
- **k30, k32 et k34** (facturation électronique, fin du régime simplifié, recodification). Les dates et le report au 1er janvier 2027 par l'ordonnance n° 2026-671 ont été confirmés par recherche le 15 octobre 2026 lors des passes de vérification des fiches ue9-03 et ue4-05 (`rapports/ue9-03.md` ; `data/ue4/rapports/ue4-05.md`, recherches 4 et 6). Aucune nouvelle recherche n'a été jugée nécessaire.
- **k31** (nouvelles mentions). La carte ne date pas l'entrée en vigueur des mentions. Elle évite ainsi le point non tranché de la fiche : les pages officielles ne s'accordent pas sur l'échéance de l'adresse de livraison.

## Recherches

Aucune recherche WebSearch n'a été faite. Les corrections reposent sur des règles bien établies, sans doute réel sur le fond :
- composition de l'art. 289, I-1 du CGI ;
- éléments du coût d'acquisition (PCG, art. 213-8) ;
- comptes 237 et 238 ;
- champ des art. L. 441-10 et L. 441-11 du Code de commerce ;
- nomenclature des classes du PCG.

Les points d'actualité (régime simplifié, recodification, facturation électronique) avaient déjà été vérifiés par recherche le 15 octobre 2026, lors des passes des fiches ue9-03 et ue4-05.

## Points à reprendre dans la fiche

1. **Règles essentielles#6 et #7 (« classe 60 », « classe 70 »).** Le terme est impropre : une classe du PCG est désignée par un seul chiffre. Il faut écrire « le compte d'achat (compte 60) » et « le compte de produit (compte 70) ». Pour des marchandises, on peut préciser 607 et 707, comme le fait déjà l'item #7.
2. **Règles essentielles#2 (art. 289, I-1).** L'item se lit comme la liste complète des opérations à facturer. Or le texte vise aussi d'autres opérations, comme les ventes à distance (art. 258 A et 258 B) et les livraisons intracommunautaires exonérées. Il faudrait écrire « notamment » ou parler de cas général.
3. **Règles essentielles#9 (PCG, art. 213-8).** L'item omet le troisième élément du coût d'acquisition : l'estimation initiale des coûts de démantèlement, d'enlèvement et de restauration du site. Sans lui, l'item se lit comme une définition complète du coût d'acquisition.
4. **Définitions#5 (acompte versé à un fournisseur).** Le compte 4091 ne vaut que pour les commandes d'exploitation. Un acompte versé sur une commande d'immobilisation va en 237 ou 238 et figure parmi les immobilisations. L'item devrait le préciser, au moins par « sur une commande de biens ou de services d'exploitation ».
5. **Chiffres et seuils#1 (délais de paiement).** L'item devrait dire qu'il s'agit de la règle générale entre professionnels (C. com., art. L. 441-10, I) et compléter deux points :
   - la dérogation des quarante-cinq jours fin de mois suppose aussi que ce délai ne constitue pas un abus manifeste à l'égard du créancier ;
   - il existe des délais propres : quarante-cinq jours pour une facture périodique, délais spéciaux de l'art. L. 441-11.
6. **Règles essentielles#10 (frais de port à l'achat).** L'item présente le compte 6241 comme la seule imputation. Or l'entreprise peut aussi incorporer les frais de transport au coût d'achat, comme frais accessoires (compte 60, avec récapitulation possible en 608). Il faudrait au moins le mentionner.
7. **Chiffres et seuils#5 (LPF, art. L. 102 B), point de la première relecture que je partage.** L'item est marqué fiab « stable », mais il cite une version « en vigueur du 1er janvier 2023 au 1er janvier 2027 ». Il faudrait soit dire ce qui change au 1er janvier 2027, soit retirer la borne si le délai de six ans est maintenu. Le résultat transmis de la première relecture s'interrompt au milieu de ce point : le texte reçu s'arrête sur « mais il précise « ve ».

## Classement des exercices

Le classement automatique porte sur les 17 exercices QCM, QCM multiples et de classement du chapitre (14 QCM, 3 QCM multiples, aucun classement). Il donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 12 | oui |
| `calcul` | 5 | non |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé entre les classeurs. Les 12 exercices de nature `notion` entrent dans les révisions espacées, avec les 35 cartes ci-dessus et les comptes du plan comptable. Les 5 exercices de nature `calcul` restent dans le chapitre mais ne sont pas proposés en révision. Les 11 autres exercices (4 calculs et 7 écritures) n'entrent pas dans ce classement.
