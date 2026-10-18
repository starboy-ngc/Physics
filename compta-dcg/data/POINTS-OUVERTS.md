# Points restés ouverts après relecture des fiches (15 octobre 2026)

Ces points n'ont pas pu être confirmés par une source officielle restituée par la recherche. Ils ne figurent pas comme affirmations dans les fiches (retirés, ou formulés sans le détail incertain) ; ils sont listés ici pour une vérification humaine sur Légifrance ou le site de l'ANC.

## ue9-01

- **Texte intégral en vigueur de L. 123-13.** La phrase « L'annexe complète et commente… » est restituée dans la version 2000 et dans une version de la section datée du 27 décembre 2018, donc postérieure à 2016. La page de la version en vigueur ne la restitue pas en entier. La phrase n'est donc pas citée en `cite`.
- **Autres exclusions éventuelles de L. 123-16-2.** Les résultats restituent les établissements financiers et les organismes d'assurance et de prévoyance. Ils ne disent pas si l'article vise aussi les sociétés cotées ou les entités faisant appel à la générosité du public : la fiche ne mentionne plus ces catégories.
- **Hors périmètre.** `check-accounts.js` s'arrête sur les fichiers `.fiche.json`, qui n'ont pas de `lecon`. L'erreur est antérieure aux deux passes.

## ue9-02

- **Points du programme (`programme.points`).** L'annexe 1 de l'arrêté du 4 août 2025 n'est pas restituée pour l'UE 9. Un résultat indique que le programme de 2019 (BO ESR n° 26) comporte une partie sur le principe de la partie double, sans en donner le libellé.
- **Date de la version de L. 123-22.** Elle n'est pas restituée. La fiche indique « en vigueur ».

## ue9-03

2. **Calendrier des nouvelles mentions des factures.** La fiche suit Légifrance (art. 242 nonies A, décret n° 2024-1195) : les mentions s'appliquent depuis le 1er septembre 2026, et au 1er septembre 2027 pour les PME et microentreprises. Les pages officielles ne concordent pas entre elles :
   - economie.gouv.fr présente les quatre mentions comme applicables dès le 1er septembre 2026 ;
   - le tableau de l'art. 41 septies D (impots.gouv.fr) rattache l'adresse de livraison à l'échéance du 1er septembre 2027.
3. **URL au niveau de l'article.** Pour L. 441-9, L. 441-10 et l'art. 287, la fiche pointe vers les sections Légifrance sans date, qui affichent la version en vigueur. Les identifiants d'article restitués (L. 441-10 : LEGIARTI000038414392 ; L. 441-9 : LEGIARTI000038414397) ne sont pas datés dans les résultats, et rien ne montre qu'il s'agit de la dernière version.
4. **Avis ANC n° 2025-01.** Le rattachement des refacturations au compte 708 n'est restitué qu'en résumé. La fiche ne cite donc pas l'avis entre guillemets.

## ue9-04

- **Calendrier de la recodification de la TVA.**
  - L'art. 49 de l'ordonnance n° 2025-1247 fixe son entrée en vigueur au 1er septembre 2026.
  - Légifrance date du 1er janvier 2027 l'abrogation des dispositions TVA du CGI. Cette date est restituée par la note de l'art. 261 et par la recherche du rapport ue9-08 sur l'art. 261 C.
  - Les numéros CIBS des exonérations de l'octroi de crédits (ancien 261 C, 1°) et des timbres-poste (ancien 261 C, 3°) n'ont pas été trouvés.
- **Extrait de l'art. 512-1 (règlement 2022-06).** La recherche 4 confirme la suppression, mais pas mot pour mot. L'extrait est conservé sur la foi de la relecture du 14 octobre.
- **Règlement ANC n° 2026-04.** Sa date d'application n'est pas tranchée : exercices en cours au 4 septembre 2026, ou exercices ouverts à compter du 1er janvier 2027. Son effet éventuel sur les comptes 444 et 695 n'est pas connu non plus. La fiche n'en parle pas.
- **L. 136-1-1 (LFSS 2026).** Le contenu de la modification du 31 décembre 2025 n'est pas restitué. La fiche n'en reprend que le I et les frais professionnels.

## ue9-05

- **Règlement ANC n° 2019-09.** Le rattachement de l'option sur les frais de formation à ce règlement repose toujours sur le nom du fichier officiel de l'ANC. La règle elle-même est restituée mot pour mot.

## ue9-06

- **Numéro de l'article « prix et perspectives de vente ».** La phrase est restituée dans le PCG au 1er janvier 2025, mais sans numéro. L'art. 214-22, qui la portait en 2014, a une autre rédaction dans les versions 2024 et 2026. La fiche s'appuie donc sur le BOFiP et sur l'art. 214-6, et le chapitre ne cite plus l'art. 214-22.
- **Article du code des impositions sur les biens et services qui reprend l'art. 272 au 1er janvier 2027.** Non identifié. La fiche s'en tient au BOFiP : les renvois au CGI valent renvois aux articles du nouveau code qui les reprennent.
  - leçon 5 : « valeur d'utilité (ce que l'entreprise accepterait de payer pour les acquérir) » ;
  - leçon 4 : « certificat d'irrécouvrabilité ».

## ue9-07

- Plan de comptes 2026 : le sous-compte des produits à recevoir de l'État (4482 ou autre) et ceux des produits à recevoir envers le personnel et les organismes sociaux ne sont pas restitués. La fiche s'en tient au compte 448 pour l'État. On ne sait pas non plus si 4481 et 44811 viennent du plan 2025 ou du plan 2026 : la fiche dit « plan 2024 : 4482 ». À reprendre dans le plan local `data/pcg/classe4.json`, qui garde 4482, 4486 et 4487 et les intitulés 2024 de 428, 438 et 448. La fiche et le chapitre `ue10-05` utilisent aussi ces comptes. Ces fichiers ne relèvent pas de cette relecture.
- URL conservées sur la foi du contrôle de corpus de la passe précédente, non revues dans les résultats de cette passe : R. 123-190 (LEGIARTI000030927465), L. 232-10 (LEGIARTI000051322888 ; le résultat de cette passe donne aussi la page LEGIARTI000006229005, qui affiche la version en vigueur), L. 123-12, L. 123-13, L. 123-20, L. 123-21, L. 232-11, L. 232-13 et l'arrêt TDA (impots.gouv.fr). Les PDF du PCG au 1er janvier 2026, du plan de comptes 2026 et du règlement n° 2022-06 sont, eux, apparus dans les résultats de cette passe.
- Taux réduit de 15 % : l'extrait de l'art. 219 restitué dans cette passe est tronqué avant le taux. Le chiffre repose sur la passe précédente et sur le BOI-IS-LIQ-20-20.
- Ordonnance n° 2025-229, art. 62 : les éventuelles phrases ajoutées à L. 232-10 ne sont pas restituées. La suppression de la formule de nullité est confirmée par le texte en vigueur.
- Points du programme (annexe 1 de l'arrêté du 4 août 2025) : non restitués (guide pédagogique DCG de juillet 2026, UE 9 à partir de la p. 502, non lisible) ; conservés tels quels.

## ue9-08

- **Reprise comptable du solde de subvention à la cession du bien.** Seule la règle fiscale (art. 42 septies, BOFiP) est restituée. L'exercice 29 (réponse : 16 000 €, `src` incluant l'art. 42 septies) est conservé.
- **Effets escomptés non échus en engagements hors bilan** (leçon 5, exercice 22). Seul un arrêté de 2010 homologuant d'autres règlements a été restitué ; l'article du PCG n'a pas été retrouvé. Le chapitre n'est pas modifié.
- **Versions en vigueur au CGI.** Pour l'art. 42 septies, seule la version de 2009 de Légifrance est restituée ; la fiche renvoie au BOFiP du 28 juin 2023. Pour l'art. 38, 4, l'URL de la version en vigueur n'est pas restituée : l'item renvoie à L. 123-21.
- **Points du programme** (annexe 1 de l'arrêté du 4 août 2025) : les intitulés ne sont pas restitués par les résultats. Ils sont conservés, comme dans les autres fiches UE9.

## ue9-09

- **CGI, art. 289 bis.** L'URL Légifrance trouvée (LEGIARTI000046195635) ne permet pas d'établir la version en vigueur après les lois de finances pour 2024 à 2026. L'entrée des textes reste à `url: null`, et l'item s'appuie sur economie.gouv.fr.
- **Chapitre, lecon[6] et exercices[21].** Le délai de dépôt de la liasse (« deuxième jour ouvré suivant le 1er mai », quinze jours supplémentaires) n'a pas été recoupé. Le texte est conservé faute de contradiction.
- **Chapitre, exercices[10].** « Sans blanc ni altération » est rattaché à R. 123-173 ; la fiche l'établit sur L. 123-22. Le texte est conservé, faute de pouvoir vérifier la rédaction de R. 123-173 sur ce point.

## ue10-01

- Leçon §4 et exercice 15 : je n'ai pas pu confirmer, dans le PCG au 1er janvier 2026, la mention d'une « information comparative pro forma » en annexe en cas de changement de méthode. Les recueils antérieurs la contiennent. Rien ne la contredit, donc elle est conservée telle quelle.
- Leçon §6 et exercice 20 : la numérotation des articles du PCG sur l'annexe (« art. 831-1 s. ») après le règlement ANC n° 2022-06 n'a pas été recoupée, pas plus que les libellés « annexe abrégée / annexe simplifiée ». Ces points sont laissés en l'état.
- Leçon §5 et exercice 19 : la règle selon laquelle un événement postérieur qui remet en cause la continuité d'exploitation conduit à établir les comptes en valeurs liquidatives n'a pas été trouvée dans un texte officiel restitué. Elle n'est pas contredite, et la fiche ne la reprend pas.
- Règlement ANC n° 2026-03 : les résultats établissent que l'article 531-5 reprend la définition du résultat exceptionnel. Ils ne détaillent pas le sort de l'article 513-4 à partir de 2027. La fiche cite 513-4 pour les exercices ouverts avant le 1er janvier 2027.

## ue10-02

2. **Durée maximale de cinq ans pour les frais de développement.** Elle apparaît sur la page Légifrance de R. 123-187, avec un doute sur la version, et la fiche la rattache aussi au PCG, art. 214-3. Le texte exact de l'alinéa (« dans des cas exceptionnels » ou non) n'a pas été restitué.
5. **Longueur de la leçon 1.** Elle compte 249 mots, au-delà des 220 du contrat, et n'a pas été modifiée.

## ue10-03

- **Indemnité pour destruction totale ou vol** (757 ou 7587, à compter de 2027). Cette distinction figure dans le projet de règlement soumis à consultation. Le texte définitif du règlement ANC n° 2026-03 n'a pas été restitué sur ce point. La fiche s'en tient au compte 7587, conforme au plan de comptes 2026.
- **Renumérotation de l'art. 513-5 en 531-5** (règlement 2026-03, exercices ouverts à compter de 2027), reprise de la relecture précédente. Les recherches confirment l'objet du règlement (produits des ventes, cessions d'immobilisations), mais pas ce numéro.
- **Règlement 2020-01, art. 272-2** : cet article est restitué dans la version consolidée 2024. Sa numérotation dans le recueil 2026 n'a pas été restituée.

## ue10-04

2. **Étalement pour les emprunts en devises finançant une immobilisation dans le pays de la devise** (leçon 5, exercice 23, option 2). Les résultats sur l'art. 420-6 (versions 2025 et 2026) ne mentionnent que l'instrument de couverture et la position globale de change. Le cas n'a été ni confirmé ni infirmé. La réponse est inchangée, faute de texte qui la contredise.
3. **Article de la règle de sous-activité pour les immobilisations produites.** Un résultat attribue cette règle à l'art. 213-18 du recueil 2026. La fiche garde l'art. 213-15, retenu par ue10-02 et ue9-05.
4. **Art. 622-7.** La règle « la décision d'adopter la méthode à l'avancement porte sur tous les contrats en cours » a été restituée dans la version 2014. Sa rédaction dans le recueil 2026 n'a pas été affichée.
5. **Extrait de l'art. 213-9** (« Deux méthodes comptables sont donc autorisées… »). Il est repris du corpus de la fiche ue9-05 et n'a pas été restitué de nouveau dans ce passage.
7. **Points du programme.** Ils n'ont pas été recoupés mot pour mot avec l'annexe de l'arrêté du 4 août 2025.

## ue10-05

- **Version 2026 de certains articles du PCG.** Les extraits des art. 212-10, 212-11 et 221-7 viennent de versions consolidées antérieures (2016 à 2025). L'art. 222-1 au 1er janvier 2026 renvoie toujours à l'art. 221-7, qui existe donc encore. L'art. 323-2 (meilleure estimation) est restitué dans la version 2025 seulement.
- **Leçon « Provisions réglementées et fiscalité des provisions ».** La condition « la charge couverte doit être elle-même déductible » et l'exclusion des provisions pour propre assureur ne sont pas restituées (déjà relevé à la première passe pour la fiche). La leçon est inchangée.
- **Références « PCG, titre IX » du chapitre.** Elles sont conservées, par cohérence avec les autres chapitres de l'UE 10 (le plan de comptes figure à l'art. 1121-1 depuis le règlement n° 2022-06).
- **Modalités de l'épreuve n° 10.** Elles restent hors de la fiche, faute de résultats concordants.

## ue10-06

- Montant réglementaire du seuil unitaire d'apport en nature pour la dispense de commissaire aux apports en SAS (L. 227-1) : il n'a pas été trouvé. La fiche et la leçon ne citent donc pas de chiffre pour la SAS.

## ue10-07

- Contenu exact de la modification de l'article L. 3324-1 du Code du travail par l'article 42 de la loi n° 2026-103 : les résultats confirment la modification (version en vigueur au 1er janvier 2026) et le maintien de la formule de la RSP, pas le détail du changement ; la fiche ne dit rien de plus.
- Sous-compte exact d'un abandon de créance commercial sous le PCG 2025 (658 dans le chapitre) : seul le classement en résultat d'exploitation (classe 65/75) est établi par les textes trouvés ; le chapitre conserve 658, cohérent avec ce classement.
- Comptes du chapitre non recoupés avec le plan 2026 mais non contredits : 4246, 1661, 4286, 7587, 664.
- Leçon §4 : « entre dans le calcul de la valeur ajoutée pour la participation si elle compense un prix » n'a pas été recoupé avec l'art. D. 3324-2 ; laissé en l'état faute de texte contraire.
- Date d'application du taux de 20 % du CII (1er janvier ou 16 février 2025, selon les pages officielles) : la fiche ne mentionne pas de date.

## ue10-08

- LPF, art. L. 102 B : Légifrance fait courir la version actuelle (six ans) jusqu'au 1er janvier 2027, mais le contenu de la version suivante n'a pas été restitué. La fiche date le délai de six ans de 2026.
- NEP 315 révisée : seules trois des cinq composantes ont été restituées mot pour mot, plus la mention du système d'information. Les activités de contrôle n'apparaissent pas dans les extraits, d'où le « dont » de la fiche.

## ue2-01

- **Numéro du BO du programme 2019.** Une annexe porte l'en-tête « Bulletin officiel n° 25 du 20-6-2019 ». La passe ue2-02 a trouvé la page de l'arrêté sous « Hebdo26 », et les autres fiches citent le n° 26. La fiche ne donne plus de numéro de BO pour ce programme.
- **Intitulé exact du point 2.5 du programme 2025.** Seul son contenu a été restitué ; la fiche le donne sans guillemets.
- **Libellé exact de l'art. 1844-10, al. 1, et de l'art. 1844-10-1.** Ils n'ont pas été restitués mot pour mot : pas de citation. Le contenu (« incapacité de tous les fondateurs », nombre minimal de deux associés ; régime de la nullité des apports) vient des résumés des résultats.
- **Troisième voie de reprise.** La reprise par décision des associés après l'immatriculation, à la majorité sauf clause contraire, n'a pas été restituée dans cette passe. Elle est conservée sans précision de majorité par forme sociale.
- **Arrêts non recoupés par recherche :**
  - Cass. com., 9 février 1999, n° 96-17.661 (droit de vote) : rattachement conservé à côté de l'art. 1844, al. 1er.
  - Cass. com., 12 février 2025, n° 23-22.414 : énoncé écrit d'après le résumé du résultat, texte intégral non lu.
  - Un résultat résume l'arrêt du même jour n° 22-18.295 dans un sens qui paraît contraire au n° 22-12.865 (nullité de l'acte non expressément conclu pour la société). Il n'est pas repris.
- **URL datées conservées faute de mieux :** L. 223-23 (vue au 21 septembre 2000, version unique en vigueur). Pour 1843, seule une vue datée est apparue : la fiche renvoie au chapitre Ier.
- **Art. 1844-15 et 1844-16** (leçon, exercice 27) : une nouvelle version de 1844-15 existe (LEGIARTI000051322352), mais son texte n'a pas été restitué. Rien ne contredit la leçon (absence de rétroactivité, inopposabilité aux tiers de bonne foi).
- **L. 526-22 modifié par la loi n° 2024-42** : repris de la passe ue2-07, non recherché dans cette passe.
- **Loi de finances pour 2026 (loi n° 2026-103) et art. 746 du CGI** : pas de recherche dédiée dans cette passe ; la version en vigueur depuis le 1er janvier 2021 a été confirmée le même jour par la passe ue2-05.

## ue2-02

- **Numéro du BO du programme 2019.** La page officielle de l'arrêté du 13 février 2019 est publiée sous « Hebdo26 » (ESRS1900135A), ce qui justifie la mention « BO ESR n° 26 ». Mais une annexe PDF de cet arrêté porte l'en-tête « Bulletin officiel n° 25 du 20-6-2019 ». La date du 27 juin 2019 n'a pas été relue.
- **Point « Appliquer le cadre juridique à une situation professionnelle » (85 heures)** : non relu sur l'annexe. Il concorde toutefois avec le total de 150 heures et avec la numérotation 3.x.
- **L. 232-1 en vigueur.** La référence aux micro-entreprises et petites entreprises « au sens de L. 230-1 » (loi n° 2025-391) vient du résumé d'un résultat Légifrance. L'URL de l'article dans sa version en vigueur n'est pas apparue : la fiche renvoie au chapitre II du titre III du livre II. L'art. 6 de la loi n° 2026-403 ajouterait une mention sur le mécénat au rapport de gestion ; non retenu faute de texte restitué.
- **Rédaction exacte de L. 223-27 en vigueur.** La substitution de mots par l'art. 18 de la loi n° 2024-537 est établie, mais le texte consolidé n'a pas été restitué mot pour mot (maintien de l'acte unanime, formule sur la voie électronique). D'où l'absence de `cite`.
- **L. 223-26 en vigueur depuis le 1er janvier 2025** : le texte modificatif n'a pas été identifié.
- **CSS, art. L. 311-3** : une URL d'article est apparue (LEGIARTI000046805349), mais rien n'établit qu'il s'agit de la version en vigueur. L'entrée `textes` reste à `null` ; l'item renvoie à la page Urssaf.
- **Énoncés écrits d'après la lettre de textes stables, sans extrait restitué dans ce passage :**
  - L. 223-4, L. 223-9 al. 3, L. 223-21 (représentants légaux), L. 223-25, L. 223-36, L. 223-43 ;
  - L. 232-22 (deux mois par voie électronique).
- **Leçon, tableau final** : « ni faire d'offre au public de titres financiers ». D'après un résultat, L. 223-11 réserverait l'offre visée au 1° de l'article L. 411-2 du Code monétaire et financier. Non modifié, faute de texte restitué.

## ue2-03

- **Portée de la consultation écrite du conseil (L. 225-37, loi n° 2024-537).** Les résultats ne disent pas si la loi l'a ouverte à toutes les décisions du conseil ou à certaines seulement. La fiche s'en tient à la faculté statutaire et au droit d'opposition de chaque administrateur.
- **Arrêt du 29 mai 2024 (n° 22-13.158).** L'URL n'est apparue qu'avec des paramètres de recherche. Elle n'est pas reprise, et l'item renvoie à l'arrêt de 2007.
- **Contenu propre de L. 821-40.** Il n'a pas été restitué. La fiche ne lui rattache plus les seuils de désignation obligatoire.
- **L. 225-20.** Un résultat montre une version datée du 6 janvier 2027 (LEGIARTI000051322412). Une modification future du régime du représentant permanent n'est donc pas exclue ; elle n'a pas été examinée.
- **Programme 2019.** L'intitulé « sociétés anonymes (forme classique et à directoire), sociétés par actions simplifiées (pluripersonnelle et unipersonnelle) » n'a pas été relu dans cette passe.
- **Leçon, non modifiée faute de texte établi par la fiche :**
  - CAC obligatoire pour une SA « cotée » ;
  - directoire « de 2 à 5 membres » (le minimum de deux ne figure pas dans L. 225-58) ;
  - vote double de plein droit dans les sociétés cotées (loi Florange).
- **Fiche ue2-01** (hors de cette fiche) : l'art. 1844-10 y reste rattaché à deux identifiants différents (LEGIARTI000051322322 et LEGIARTI000051317310). La fiche ue2-03 utilise désormais l'URL du JORF de l'ordonnance.

## ue2-04

  - economie.gouv.fr : plafond de 35 % des droits de vote des associés non salariés ;
  - Bpifrance Création, hors liste du contrat : 51 % et 65 %.
- **SEL (item « Sociétés d'exercice libéral » et leçon, § 3).** Restent à recouper sur un article précis de l'ordonnance n° 2023-77 :
  - la détention de plus de la moitié du capital et des droits de vote ;
  - la responsabilité de chaque associé pour ses actes professionnels ;
  - l'obligation d'information annuelle de l'ordre, le délai d'un an de mise en conformité et l'élargissement des SPFPL (leçon).
- **Restent sans URL** (4 items) : L. 121-2, L. 526-22, CGI art. 206 (1, 1 bis et 4), 239 quater, BOI-IS-CHAMP-10-50-10. L'exercice 18 cite BOI-IS-CHAMP-10-50-10-20, référence non contrôlée.
- **Énoncés à recouper** : loi n° 47-1775, art. 1er (une voix par membre coopérateur) ; loi n° 78-763, art. 1er (définition de la SCOP) ; loi n° 87-571, art. 18 (fondation).
- **Prescription de deux ans** (ordonnance n° 2025-229, art. 1844-14). Elle est reprise des fiches ue2-02, ue2-05 et ue2-06, mais n'a pas été restituée par une recherche de cette passe.
- **Actualité non examinée** (budget atteint) :
  - loi n° 2026-403 du 26 mai 2026 ;
  - lois de finances pour 2025 et 2026 ;
  - montant 2026 de la franchise des activités lucratives accessoires (CGI, art. 206, 1 bis). La fiche le décrit sans chiffre, comme « seuil annuel indexé ».
- **Exercice 11** : rattachement de la SCM (« ordonnance n° 2023-77 ; C. civ., art. 1845 ») non contrôlé.
- **Points du programme** (`programme.points`) : non relus sur le texte officiel.

## ue2-05

- **Fusion simplifiée à 100 % (L. 236-11) et seuil de 5 %.** La recherche a restitué le seuil de 5 % dans L. 236-11-1 (régime des 90 %), mais pas dans L. 236-11. Le résumé du résultat affirme même qu'il n'y figure pas. La fiche (Règles / Fusion simplifiée) et l'exercice 20 l'appliquent aussi au cas de détention à 100 %, conformément à la rédaction de L. 236-11 antérieure à 2023. À contrôler sur l'article en vigueur.
- **Transformation.**
  - Attestation des capitaux propres par le commissaire à la transformation : elle figure dans R. 224-3 (version 2007-2021). La rédaction actuelle de R. 224-3 n'a pas été restituée. La leçon (section 4) l'attribue à L. 224-3 ; la fiche ne la reprend pas.
  - L. 225-244 (rapport du commissaire aux comptes de la SA qui se transforme) : non recherché, conservé de la passe 1.
- **BOFiP BOI-ENR-AVS-30-20-10.** Seule la version du 7 juin 2018 est apparue. L'existence d'une version plus récente n'a pas été contrôlée. L'assiette retenue (actif net partagé) découle aussi de la lettre de l'art. 747 du CGI.
- **Sanction de L. 225-131 dans la SA** après l'ordonnance n° 2025-229 (art. L. 225-149-3 et L. 225-149-4) : non déterminée. La fiche n'affirme pas de nullité pour la SA.
- **Ordonnance n° 2025-229.** Le champ exact du triple test (art. 1844-12-1) et les cas réservés par L. 225-149-4 (« dans tous les autres cas ») n'ont pas été recherchés.
- **L. 223-42 et L. 225-248, premier délai.** Le montant de la réduction possible pendant le premier délai (« du montant des pertes non imputées sur les réserves », selon la leçon, section 3) n'a pas été restitué mot pour mot.
- **URL reprises des passes ue10.** L. 225-131 (LEGIARTI000039260253), L. 225-130, L. 225-132, L. 225-144, L. 225-204, L. 821-53, D. 221-5, la section L. 821-40 et suivants, et le JORF de l'ordonnance n° 2025-229 n'ont pas été recherchés de nouveau dans cette passe. L. 237-21 (trois ans) n'a pas d'URL confirmée.
- **Leçon, section 7.** Rotation, révocation, récusation par 5 % des associés, expertise de gestion (10 % et 5 %) : non vérifiés. Ces règles ne figurent pas dans la fiche.
- **Programme.** Les points de `programme.points` n'ont pas été relus sur le texte de l'arrêté.

## ue2-06

- **L. 628-1 (sauvegarde accélérée).** La condition de comptes certifiés par un commissaire aux comptes ou établis par un expert-comptable est reprise dans la fiche, la leçon et l'exercice 10. Elle n'a pas été recoupée dans la rédaction issue de l'ordonnance n° 2021-1193. Le délai de L. 628-8 est, lui, confirmé.
- **Loi n° 2026-403, art. 26.** Les résultats montrent la modification de L. 242-10 et de L. 247-1. L'URL de L. 241-3 restituée (LEGIARTI000028312103) laisse penser que l'abus de biens sociaux n'est pas modifié, mais le texte intégral de l'art. 26 n'a pas été lu.
- **Énoncés stables écrits d'après la lettre des textes, sans recoupement par recherche :**
  - nullités de la période suspecte (L. 632-1 et L. 632-2) ;
  - L. 622-7, L. 622-21, L. 622-24, L. 622-26 et R. 622-24 (deux mois, relevé de forclusion de six mois) ;
  - L. 653-1 à L. 653-11 ;
  - C. pr. pén., art. 8 et 9-1 ;
  - C. pén., art. 121-2 et 131-38 (sans URL).
- **Leçon et exercice 17, sans item dans la fiche :**
  - durée de six mois, plus trois, de la liquidation simplifiée (L. 644-5) ;
  - seuil de 15 000 € du rétablissement professionnel (R. 645-1).
- **Mandat ad hoc « non en cessation des paiements »** (leçon, exercice 5). Cette condition ne figure pas dans L. 611-3. Elle est laissée telle quelle, faute de texte établi qui la contredise.
- **Programme 2025.** L'intitulé exact de la compétence de 85 heures est donné de deux façons : « Appliquer le cadre juridique à une situation professionnelle » par les autres fiches, « appliquer le cadre juridique adapté… » par le résumé d'un résultat. La fiche garde la formulation commune aux fiches de l'UE 2.

## ue2-07

1. **Loi n° 2026-403, paiement mensuel.** Les résultats ne rattachent pas expressément la mensualisation à un numéro d'article. L'article L. 145-32-1, créé en 2026 en tête de la section « Du loyer », est le plus probable. La fiche cite donc la section entière. Les numéros des articles de la loi (résultats : art. 30 et art. 62) ne sont pas identifiés.
3. **URL de CGI, art. 1684 (LEGIARTI000033812284).** Le résultat restitue la règle des 30 jours. Il ne précise pas que cet identifiant est la dernière version.
4. **L. 141-21 depuis l'ordonnance n° 2023-393.** Le délai de dix jours et la déclaration au greffe ont été restitués pour la version 2019-2023. Le texte modifié n'a pas été lu en entier, et la nature de la modification n'est pas connue. La fiche ne reprend pas l'exception des fusions et scissions.
5. **Énoncés toujours sans extrait restitué :**
   - C. com., art. L. 110-3, L. 123-7 (présomption de commercialité), L. 123-24, L. 141-22, L. 142-1 al. 2 ;
   - C. com., art. L. 145-5, L. 145-16, L. 145-33, L. 145-48 ;
   - C. com., art. L. 210-1, L. 210-6, L. 526-27, R. 526-27 ;
   - CPI, art. L. 712-1 ; C. civ., art. 413-8.
6. **Programme 2025, sous-partie 2.3.** L'intitulé exact n'est toujours pas restitué.

## ue3-01

- **URL des passes précédentes non reconfirmées** (23 URL Légifrance non datées, forme `article_lc` ou `section_lc`). Elles sont conservées, faute de recherche disponible : par exemple L. 2221-2, L. 2251-1, L. 2253-1, L. 1321-3, L. 1411-1, L. 1423-1, L. 1454-1, L. 1471-1, L. 3245-1, L. 1134-5, L. 1237-14, L. 2262-14, L. 8112-1, L. 8113-1, L. 8114-1, loi n° 2018-217 et ordonnance n° 2017-1385. Leurs citations n'ont pas été restituées dans ce passage.

## ue3-02

- Loi n° 2023-171, article 19 : le numéro d'article et la date du 9 septembre 2023 (fin des périodes d'essai plus longues des accords de branche antérieurs au 26 juin 2008) ne sont pas restitués par mes résultats. Ils sont cohérents avec la leçon et l'exercice 2.
- `programme.points` : intitulés repris de la fiche initiale (identiques à ceux de ue3-03), non recoupés par une recherche dans ce passage.
- L. 1222-9 : la présomption d'accident du travail en télétravail est tronquée dans l'extrait Légifrance obtenu. Elle reste rattachée à l'article. Version : l'URL renvoie à la rédaction de 2023, dont le texte modificatif n'est pas identifié.
- URL de L. 2254-2 (LEGIARTI000037385300) : elle n'est pas reproduite littéralement dans un rapport. Le rapport ue3-03 atteste toutefois que toutes les URL de sa fiche, dont celle-ci, sont apparues dans ses résultats.

## ue3-03

- Décret n° 2026-503 du 12 juin 2026 (R. 4624-31, dispense de visite de reprise) : numéro, date d'entrée en vigueur (15 juin 2026) et contenu sont tirés d'un seul résultat Légifrance, sans le texte intégral du décret.
- Congé supplémentaire de naissance : le rattachement à la LFSS 2026 (loi n° 2025-1403) n'est pas restitué mot pour mot par le résultat. Il est cohérent avec la création de la section L. 1225-46-2 à L. 1225-46-7 et avec la date du 1er juillet 2026.
- Parties de la leçon que la fiche ne couvre pas (aménagement du temps de travail, travail de nuit, jours fériés, congés pour événements familiaux, congé sabbatique, CPF et participation forfaitaire) : non revérifiées dans ce passage. Sources de l'exercice 17 (Cass. soc. 10 mai 1999 ; 3 juin 2003) également non revérifiées.
- Énoncés de la fiche que je n'ai pas recoupés par une recherche dans ce passage, mais qui sont conformes aux textes cités : L. 3231-6 (fixation au 1er janvier), L. 1311-2 (seuil de 50 salariés), R. 3252-5 (fraction insaisissable), décret n° 2024-951 (SMIC 2025).

## ue3-04

- **L. 1237-5, « soixante-neuvième anniversaire inclus »** : le résultat ne restitue qu'en paraphrase la limite du 69e anniversaire. La fiche n'écrit donc plus « 70 ans d'office ». Le chapitre (note de source, leçon et exercice 17) garde « 70 ans d'office », qui découle de cette limite ; il n'a pas été modifié.
- **Contrat de valorisation de l'expérience** : les conditions d'éligibilité au-delà de l'âge (inscription comme demandeur d'emploi, par exemple) et les décrets d'application n'ont pas été recherchés.
- **Assurance chômage 2026, allocataires de 55 ans et plus** : les durées après une rupture conventionnelle varient selon les résultats (20,5 mois ou autre). Elles ne sont pas reprises.
- **Seuil de 1 000 salariés du congé de reclassement (L. 1233-71)** : il n'a pas été recoupé dans ce passage. La leçon le cite (« CSP, entreprises de moins de 1 000 salariés ») ; la fiche renvoie à L. 1233-71 sans le chiffrer.
- **Cass. soc., 11 mai 2022, n° 21-14.490** (sources du chapitre) : arrêt non recherché, cohérent avec l'arrêt du 9 avril 2025 cité par la fiche.

## ue3-05

- **Périodicité de la négociation sur les salariés expérimentés (L. 2242-2-1)** : le texte du code et la page du ministère divergent (trois ans contre quatre ans). La fiche et le chapitre ne donnent donc pas de périodicité. Selon le ministère, le volet « branche » (L. 2241-14-1) attend ses décrets d'application ; son contenu n'a pas été restitué.
- **L. 2122-5 (8 % dans la branche)** : l'URL de l'article est apparue, mais le seuil n'a pas été restitué mot pour mot. Le 8 % national et interprofessionnel (L. 2122-9) l'a été.
- **Loi n° 2026-403, art. 22** : la page de Bercy annonce aussi un délai minimal d'information préalable « réduit d'un mois » et des sanctions allégées. La formulation est ambiguë et ces points n'ont pas été repris.
- **Énoncés stables non recoupés dans ce passage** (conformes aux textes cités, sans URL propre) :
  - grève : L. 2511-1, L. 2512-2 (préavis de cinq jours dans les services publics) et L. 2522-1 à L. 2524-1 ;
  - négociation sans délégué syndical : L. 2232-21 à L. 2232-26 (détail des seuils) ;
  - articulation branche-entreprise : nombre de matières des blocs 1 et 2 (L. 2253-1 et L. 2253-2) ;
  - leçon et exercice 9 : heures de délégation (R. 2314-1) ;
  - leçon : forfait social de 20 %, index (75 points, trois ans, 1 %) et généralisation du CSE au 1er janvier 2020.

## ue3-06

- **Génération 1965** : la durée d'assurance requise après la suspension (171 trimestres, par déduction du décalage d'un trimestre) n'apparaît pas explicitement dans les résultats. La fiche ne l'indique donc pas.
- **Parts salariales vieillesse 2026** (6,90 % et 0,40 %) : non restituées par les résultats. La fiche ne donne que les taux patronaux 2026 ; les exercices millésimés 2025 restent exacts.
- **Contenu de fond du décret n° 2026-866 du 16 septembre 2026** (durée maximale dérogatoire d'indemnisation) : seuls l'intitulé et la date d'application (arrêts prescrits à compter du 15 octobre 2026) sont repris.
- **Leçon « Assurance chômage »** : la condition d'affiliation de 36 mois à partir de 55 ans et les durées maximales de 18, 22,5 et 27 mois n'ont pas été reconfirmées par recherche. La fiche reste générale (« salariés les plus âgés »).

## ue4-01

1. **CDHR, qualificatif du déficit.** Les résultats décrivent le terme comme un « déficit du budget général » inférieur à 3 % du PIB, constaté par le projet de loi relatif aux résultats de la gestion. Le passage n'a pas été restitué mot pour mot, et la formule usuelle est « déficit public ». La fiche écrit donc « un déficit inférieur à 3 % du PIB », sans qualificatif.
2. **Déficit foncier de 21 400 €.** La fin de période au 31 décembre 2027 est confirmée par impots.gouv.fr et economie.gouv.fr. Le texte qui a prorogé la date initiale du 31 décembre 2025 n'a pas été identifié. La fiche ne le nomme pas et cite le texte d'origine (LFR 2022, art. 12).
4. **Non-résidents et conventions.** La phrase selon laquelle le taux minimum ne vise que les revenus imposables en France selon la convention vient d'impots.gouv.fr (passe précédente). Elle n'a pas été revérifiée dans cette passe.

## ue4-02

1. **Micro-BA 2026-2028 (129 200 €).** Le montant repose sur l'exemple du BOI-BA-BASE-15-10 du 19 août 2026, sur le calcul d'actualisation et sur la cohérence avec 203 100 € et 83 600 €.
   - Un résumé de recherche attribue 120 000 € à un tableau « 2026 à 2028 » du BOFiP. Le même résumé est contradictoire : il qualifie 129 200 € de « limite antérieure », alors que 129 200 € est supérieur à 120 000 €.
   - Une prochaine passe pourra chercher le seuil RSI agricole (391 000 € ou 421 000 €), qui permettrait de recouper.
2. **Déficit foncier de 21 400 €.** La prorogation jusqu'au 31 décembre 2027 est confirmée par economie.gouv.fr et la brochure IR 2026, mais l'article de loi qui la prévoit n'a pas été identifié.
   - Le chapitre l'attribue à la « LF 2026 ». Cette attribution est plausible et n'a pas été modifiée ; la fiche ne la reprend pas.
   - Un résultat qualifie le relèvement d'« option » ; la fiche ne tranche pas ce point et garde une formulation neutre.
---

## ue4-03

1. **Incohérence avec la fiche ue4-02.** La fiche ue4-02 (section « Ce qui a changé ») affirme que le BOFiP du 19 août 2026 « retient pour 2026 à 2028 » 188 700 € et 77 700 €. Cette affirmation repose sur des résumés du BOI-BAREME-000044 qui se contredisent (recherche 1 de cette passe). economie.gouv.fr donne 203 100 € / 83 600 € et 945 000 € / 286 000 € pour 2026-2028 (recherches 2 et 3), comme la fiche ue4-03 et la fiche ue4-05. La fiche ue4-02 et son chapitre sont à aligner par leur relecteur.
2. **Identifiants Légifrance non confirmés comme derniers.** Art. 151 septies : seul l'identifiant de 2018 (LEGIARTI000036591469) apparaît dans les résultats ; l'URL BOFiP est conservée. Art. 39 A (LEGIARTI000037987291) et art. 39 quindecies (LEGIARTI000036428314) : non revérifiés dans cette passe.
3. **BOFiP sur la rémunération de l'exploitant (1022-PGP).** Un résumé de recherche indique que cette page mentionne encore la limite de 17 500 € pour les non-adhérents. La fiche s'appuie sur le texte de l'art. 154 (Légifrance), qui ne la contient plus depuis le 1er janvier 2019.

## ue4-04

- **Leçon, points hors fiche non recherchés** (quota atteint) : rémunération des administrateurs (art. 210 sexies : 5 %, 457 €), réduction d'impôt mécénat (art. 238 bis : 60 %, 40 % au-delà de 2 M€, 20 000 € ou 5 ‰), perte du report déficitaire en cas de changement d'activité réelle (art. 221, 5). Non modifiés ; à recouper lors d'une prochaine passe.
- **SARL de famille (art. 239 bis AA)** : seule la page BOFiP est apparue, sans extrait ; la règle (option sans limite de durée) reste fondée sur le texte de l'article.
- **CE, 13 mars 2025, Sté TDA, date limite de régularisation (20 mai 2026)** : reprise de la passe précédente, non recherchée de nouveau.

## ue4-05

1. **Art. 287 et 289 bis du CGI, URL Légifrance en vigueur.** L'item « Acomptes du régime simplifié » garde `url: null` ; sa citation est verbatim. Un résultat donne l'identifiant LEGIARTI000038049500 (« B : Déclarations de recettes (Article 287) »). Rien ne montre qu'il s'agit de la version en vigueur, donc il n'est pas utilisé.
3. **Numérotation CIBS à compter du 1er janvier 2027.** Le BOFiP signale que les références aux anciens articles du CGI restent opérantes pendant une période transitoire, prolongée par l'ordonnance n° 2026-671. Les numéros des nouveaux articles du CIBS qui remplacent les art. 256 à 293 F ne sont pas repris dans la fiche, faute d'extrait les donnant.
4. **Fondement réglementaire des nouvelles mentions des factures.** Les extraits officiels (impots.gouv.fr, economie.gouv.fr) donnent les quatre mentions et la date du 1er septembre 2026. Ils ne citent pas le texte qui les insère à l'ann. II, art. 242 nonies A. La src renvoie donc à cet article et à la page de la DGFiP.

## ue4-06

- **Art. 1727.** Légifrance affiche une version en vigueur jusqu'au 1er janvier 2027 ; la version suivante n'a pas été trouvée, et la loi n° 2026-103 ne modifie que l'art. 1727 A. La fiche ne retient que des règles de la version en vigueur (0,20 % par mois, point de départ, réduction de 50 %).
- **Cotisation minimum de CFE.** Deux jeux de montants figurent sur Légifrance (247 € à 589 € / 7 669 € et 250 € à 597 € / 7 769 €) sans que les résultats permettent d'en dater l'application. Les montants ont été retirés de la leçon ; la fiche n'en contient pas.
- **Taxe sur les salaires 2025.** La page economie.gouv.fr indique une tranche « jusqu'à 18 258 € » et la passe précédente 18 259 € (BOFiP). Le chapitre garde 18 259 € (limites 2025 rappelées et exercice 8) ; le résultat de l'exercice 8 (2 760 €) est le même avec l'une ou l'autre limite.
- **Abattement des associations (taxe sur les salaires) 2026.** Non recherché ; la leçon garde le montant 2025, présenté comme tel.


## UE1 Fondamentaux du droit (fiches contre-vérifiées le 18 octobre 2026)

Items des fiches UE1 dont la vérification n'a pas restitué le texte officiel mot pour mot (fond parfois confirmé). Aucun ne sert de base à une page de rappels : le rédacteur et les relecteurs des rappels les ont écartés.

### ue1-01

- Définitions#3 et Vigilance#1 : TFUE, art. 288 (repose sur la recherche 15 de la rédaction, eur-lex)
- Définitions#5 : Constitution, art. 61-1 (recherche 12 de la rédaction)
- Règles#6 et Chiffres#3 : Constitution, art. 37, al. 2 (recherche 7 de la rédaction)
- Règles#10 : Jacques Vabre (recherche 9 de la rédaction)
- Règles#11 : Nicolo (recherche 10 de la rédaction)
- Règles#13 et Chiffres#1 : Constitution, art. 61 (recherche 13 de la rédaction)
- Changements#1, Changements#2 et programme.points : arrêté du 4 août 2025 et guide pédagogique de juillet 2026 (recherches 1 à 3 de la rédaction ; URL du guide ajoutée par la relecture)
- Règles#14 : « ou constitue le fondement des poursuites » et « dans les motifs et le dispositif » (art. 23-2) non restitués mot pour mot
- Règles#9 : ordre « pour chaque accord ou traité » non restitué mot pour mot (fond confirmé)
- Règles#4 : formule exacte de l'art. 5 non restituée (fond confirmé)
- Règles#8 : fin de la compétence administrative après ratification (CE, 13 juin 2018) non restituée
- Vigilance#5 : bonnes mœurs « désuètes » selon le rapport au Président, non restitué
- Changements#0 : date du Congrès (4 mars 2024) non restituée

### ue1-02

- Définitions#4 (CPC, art. 1442)
- Règles essentielles#0 (CPC, art. 32 et 122)
- Règles essentielles#1 (CPC, art. 123 et 125, exception ajoutée par la relecture)
- Règles essentielles#3 (COJ, art. L. 213-4-2 à L. 213-4-7, « aux fins d'habitation » ajouté par la relecture)
- Chiffres et seuils#2 (décret n° 80-533, 1 500 €)
- Ce qui a changé récemment#0 (fusion TI-TGI, décret n° 2019-966, « chambre de proximité » de l'art. L. 212-8 ; seul le passage de 4 000 € à 5 000 € est confirmé)
- Points de vigilance#2 (Cass. 1re civ., 5 septembre 2018, n° 17-13.837)
- Points de vigilance#3 (Cass. 1re civ., 10 juin 2015, n° 14-15.608)
- Points de vigilance#5 (C. civ., art. 1359, al. 2, ajouté par la relecture)
- programme.points[2] (conditions de l'action en justice, attribuées par un résultat à l'annexe de 2019)

### ue1-03

- 1) Capacité : les libellés du programme 2025 sont confirmés mot pour mot (« Analyser la capacité d'une personne à accomplir un acte juridique dans une situation donnée », capacité de jouissance et d'exercice, actes d'administration, conservatoires et de disposition, tutelle et curatelle, sanctions), mais leur point de rattachement (2.1 ou autre) n'a pas été restitué. 2) Point 2.3 : son contenu n'est connu qu'en paraphrase, d'où la mention « objet ». 3) Décret du 16 août 1901 : il prévoit l'insertion d'un extrait de la déclaration au Journal officiel, mais le numéro de l'article n'a pas été restitué. La fiche cite son chapitre Ier. D'après un résultat Légifrance, la phrase sur l'insertion au JO a disparu de l'art. 5 de la loi de 1901 depuis l'ordonnance n° 2015-904. 4) Art. 413-8 (mineur émancipé commerçant) : non recherché, l'item s'en tient à l'art. 413-6. 5) La contradiction sur le point 2.2 relevée par le rédacteur sort du périmètre de cette fiche et n'a pas été traitée. Suppressions : les trois items sur l'absence et la disparition (art. 88, 112, 122, 128), exclues par le programme 2025 (« La disparition ou l'absence des personnes physiques sont exclues »), ainsi que le texte correspondant. Erreurs de fond corrigées : jurisprudence mal attribuée (Cass. 3e civ., 16 février 2022, citée pour l'extinction de l'usufruit), arrêt introuvable (Cass. 1re civ., 8 février 2017), définition tronquée de l'acte de disposition, et exceptions omises (art. 1196 mise en demeure, art. 1253 réserve agricole L. 311-1-1, art. 1844 dérogation statutaire, art. 618 abus de jouissance, publicité des associations). Fichiers : /home/user/Physics/compta-dcg/data/ue1/ue1-03.fiche.json et /home/user/Physics/compta-dcg/data/ue1/rapports/ue1-03.md (section « Relecture »).

### ue1-04

- Règles#1 (L. 123-33, guichet unique) : repris de la passe ue2-07
- Règles#2 (L. 526-22, al. 3, créanciers professionnels) : alinéa non restitué dans cette passe
- Règles#7 (L. 526-27, transfert universel)
- Règles#9 et #10 (C. civ., art. 214, 215, 223)
- Règles#13 et #14, Points de vigilance#2 et #3 (C. civ., art. 1413 à 1415, 1421, 1424) : recherches du rédacteur seulement
- Règles#17 (art. 515-4) : condition du montant cumulé des emprunts non restituée pour le PACS ; « aux conditions fixées par l'article » maintenu
- Changé#1 (extinction de l'EIRL, loi n° 2022-172, art. 6 ; décret n° 2022-709)
- Points de vigilance#5 (guide pédagogique DSCG 2026)
- Art. 1397 : homologation « du tribunal du domicile des époux » dans la version en vigueur (résultat ambigu ; l'énoncé dit « du tribunal »)
- Art. 1404, al. 1 (biens à caractère personnel) non restitué mot pour mot ; art. 515-5-1 non restitué ; décret n° 2022-725 non recherché ; termes exacts des points du programme 2025

### ue1-05

- Définitions#0 : lettre de l'art. 1101 non restituée dans cette passe
- Ce qui a changé récemment#0 : ordonnance n° 2016-131, art. 9, al. 2 (« y compris pour leurs effets légaux et pour les dispositions d'ordre public ») et Cass. 3e civ., 4 octobre 2018, n° 17-24.287
- Ce qui a changé récemment#3 : portée de Cass. com., 26 janvier 2022, n° 20-16.782
- Points de vigilance#3 : formule « la résolution est privée de tout effet » (Cass. com., 1er juin 2022, n° 20-21.551)
- Règles essentielles#3 : lettre de l'art. 1112 (seul son caractère interprétatif est confirmé)
- Règles essentielles#17 : lettre des art. 1219 et 1221
- Règles essentielles#10 : art. 1137, al. 3 confirmé seulement indirectement, pas de cite
- Formulations du rapport au Président pour les art. 1101 et 1170
- Lacunes de la rédaction : obligations de moyens et de résultat, art. 2061, CPC art. 48, art. 2367, art. 1220, art. 1231-6 et 1344

### ue1-06

- Définitions#0, 2e phrase (art. 1582, al. 2)
- Définitions#5 (art. 1589)
- Règles#0 (art. 1583)
- Règles#3 (art. 1603, 1604 et 1625)
- Règles#7 (art. 1165)
- Chiffres#3, dernière phrase (art. 1589-1)
- Chiffres#4 (art. 1590, arrhes)
- Ce qui a changé récemment#0 (ordonnance n° 2016-131)
- Ce qui a changé récemment#1 (loi n° 2018-287, art. 16, I, repris de ue1-05)

### ue1-07

- Règles essentielles#3 Chronopost (Cass. com., 22 octobre 1996, n° 93-18.632)
- Règles essentielles#11 Abus de fonctions (Cass. ass. plén., 19 mai 1988)
- Règles essentielles#13 Infraction intentionnelle du préposé (Cass. ass. plén., 14 décembre 2001)
- Chiffres et seuils#0 Place dans le programme 2025 (150 h, blocs 35/55/60 h, 15 h) et libellés de programme.points
- Chiffres et seuils#1 Gage des créanciers personnels limité au bénéfice du dernier exercice clos (L. 526-22)
- Chiffres et seuils#3 Prescription de cinq ans (art. 2224) : cite repris d'un résultat d'un autre agent
- Points de vigilance#4 Cass. civ. 1re, 14 mai 2009 et arrêt de 2001
- Ce qui a changé récemment#1 : précision « même si la résidence de l'enfant a été fixée chez un seul d'entre eux », qui va au-delà du cite
- Restitutions mot pour mot manquantes : numérotation « al. 5 » de l'art. 1242 (version du 25 juin 2025), texte de l'art. 1241 (contenu confirmé), attendu Faurecia (principe confirmé)
