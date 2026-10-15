# Cartes de notions : ue9-07 (Clôture : régularisations et résultat)

Date : 15 octobre 2026.

## Méthode

1. **Rédaction depuis la fiche.** Les cartes ont été rédigées à partir de la seule fiche documentaire `ue9-07.fiche.json`, selon le contrat (section 8). Chaque carte repose sur un ou deux items de la fiche (`base`), et `src` et `url` sont copiés depuis le premier de ces items.
2. **Relecture de fidélité.** Une première relecture a vérifié que chaque carte disait la même chose que la fiche : mêmes conditions, mêmes exceptions, même vocabulaire. Elle a contrôlé 34 cartes, en a corrigé plusieurs et en a ajouté une (k35).
3. **Relecture d'exactitude.** Une seconde relecture, indépendante, a vérifié trois points :
   - l'exactitude en droit et en comptabilité au 15 octobre 2026 (Code de commerce, CGI, BOFiP, PCG modifié par les règlements ANC n° 2022-06 et 2026-04) ;
   - l'ambiguïté pédagogique : un correcteur du DCG attendrait-il cette réponse, et une autre réponse juste était-elle possible ?
   - les doublons et les cartes sans intérêt ou purement mécaniques.

   Elle a aussi vérifié l'absence de calcul, d'écriture à passer et de chiffre millésimé. Deux recherches ont été faites sur des sites officiels (voir « Recherches »).
4. **Validation.** `node validate.js data/ue9/ue9-07.cartes.json` : ✓ (34 cartes, 10 déf.).

## Bilan

- **Nombre de cartes : 34.** Il y en avait 34 après la rédaction. La première relecture en a ajouté une (k35) et la seconde en a supprimé une (k13), sans renumérotation : l'identifiant k13 reste vide.
- **Répartition : 10 cartes `def` et 24 cartes `comp`.**
- **Couverture de la fiche.** Les 6 items de « Définitions » ont chacun au moins une carte. Les 17 « Règles essentielles » sont toutes couvertes sauf une (voir ci-dessous). Les 5 « Points de vigilance » ont chacun leur carte de compréhension.
- **Items de fiche sans carte :**
  - **Règles essentielles#3** (écriture des produits à recevoir). Sa carte k13 a été supprimée. Son contenu reste révisé par k04 (comptes 4181, 4482, 439, 467) et par k12 (TVA au compte 44587).
  - **Chiffres et seuils#0** (réserve légale : un vingtième, un dixième). Même règle que Règles essentielles#13, déjà portée par k27.
  - **Chiffres et seuils#2 et #3** (taux de l'IS, plafond du taux réduit et son prorata). Ils sont millésimés et appellent un calcul : ils ne donnent pas de carte.
  - **Ce qui a changé récemment#2** (renumérotation des comptes de régularisation entre les plans 2024 et 2026). Une carte n'y serait qu'un exercice de mémoire sur des numéros. Les comptes en vigueur sont déjà révisés par k02 et k04, et par les comptes du plan comptable.
  - **Ce qui a changé récemment#3, #5 et #6** (règlement ANC n° 2026-04, contribution exceptionnelle des grandes entreprises, seuils des petites entreprises). Ils sont millésimés. La règle stable de l'article 515-1 du PCG reste portée par k23 et k24.
- Aucune carte ne demande de calcul ni ne repose sur un chiffre millésimé. Les chiffres qui restent (un vingtième, un dixième, neuf mois, dates d'échéance de l'IS) sont stables et font partie d'une règle. Les années citées (2025, ordonnance de 2025, CE 2025) sont des dates d'entrée en vigueur ou de décision.

## Corrections de la première relecture (fidélité à la fiche)

| cible | problème | correction |
|---|---|---|
| ue9-07-k10 | La question (« que faire d'un passif […] connu seulement après la clôture ? ») appelait presque un oui ou un non. Elle ne bornait pas non plus la période : L. 123-20 ne vise pas un passif connu après l'établissement des comptes. | Nouvelle question : « Selon le principe de prudence du Code de commerce, quels passifs doivent être pris en compte dans les comptes de l'exercice ? ». Verso : les passifs nés au cours de l'exercice ou d'un exercice antérieur, même s'ils ne sont connus qu'entre la date de clôture et celle de l'établissement des comptes (citation de Règles essentielles#1). |
| ue9-07-k24 | La question ne nommait pas le référentiel. Sans contexte, on ne savait pas qu'il s'agit de la règle comptable de l'article 515-1 du PCG. | La question commence désormais par « Selon le PCG, ». Le verso est inchangé. |
| ue9-07-k26 | La règle des quatre acomptes a une exception, que la fiche donne en Chiffres et seuils#4 : impôt de référence n'excédant pas 3 000 €, ou premier exercice. La question ne délimitait pas son champ, si bien que la réponse était fausse pour une société dispensée. | Question : « Hors cas de dispense d'acomptes, selon quel calendrier une société soumise à l'impôt sur les sociétés (IS) paie-t-elle cet impôt ? ». La base devient [Règles essentielles#12, Chiffres et seuils#4] ; `src` et `url` sont inchangés. |
| ue9-07-k28 | La question contenait la réponse (« proche du dixième du capital »). Elle généralisait aussi à « une société » une règle propre aux SARL et aux sociétés par actions. | Question : « Dans une SARL ou une société par actions, à quoi la dotation obligatoire à la réserve légale est-elle limitée quand la réserve approche de son plafond ? ». Le verso, fidèle à Points de vigilance#1, est inchangé. |
| ue9-07-k33 | La question en posait deux (quel compte on débite, vers quels comptes on répartit). Elle était aussi formulée comme une écriture plutôt que comme un choix de comptes. | Question unique : « Lors de l'affectation du bénéfice d'une société, entre quels comptes le solde du compte 120 est-il réparti ? ». Verso : réserves (1061, 1063, 1068), 457 et 110. |
| ue9-07-k35 (ajoutée) | La règle stable de mise en paiement des dividendes (Chiffres et seuils#1, C. com., art. L. 232-13) n'avait pas de carte. | Question : délai de mise en paiement des dividendes selon l'article L. 232-13. Verso : dans un délai maximal de neuf mois après la clôture de l'exercice, prolongeable par décision de justice. Chiffre stable faisant partie d'une règle, sans calcul. |

Le résultat transmis de la première relecture s'arrête au milieu de la correction de k33. Le tableau reprend tout ce qui a été reçu ; l'état de k33 est celui du fichier.

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| ue9-07-k26 | **Inexact pour le cas le plus courant.** Le verso fixait le solde de l'IS au « 15 du quatrième mois qui suit la clôture », sans exception. Pour un exercice clos le 31 décembre, ce serait le 15 avril. Or le solde est dû le 15 mai de l'année suivante, et c'est une exception, pas une illustration. Le verso décrivait aussi la base de calcul des acomptes, ce qui sort de la question (« selon quel calendrier ») et reste inexact pour les grandes entreprises, dont le dernier acompte est modulé. | Verso limité au calendrier, avec l'exception : quatre acomptes au plus tard les 15 mars, 15 juin, 15 septembre et 15 décembre ; puis le solde au plus tard le 15 du quatrième mois qui suit la clôture, sauf exercice clos le 31 décembre (15 mai de l'année suivante). Base, `src` et `url` sont inchangés ; la date du 15 mai figure déjà dans Règles essentielles#12. | CGI, art. 1668, 2 ; BOFiP, IS – Modalités de paiement du solde (BOI-IS-DECLA-20-20) ; impots.gouv.fr, « Imposition des résultats » |
| ue9-07-k11 | La question présentait comme absolue la règle des seuls bénéfices réalisés. L'alinéa 2 de L. 123-21 admet pourtant, après inventaire, le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, lorsque sa réalisation est certaine et que le bénéfice global peut être évalué avec une sécurité suffisante. | La question délimite son champ : « En principe, selon le Code de commerce, quels bénéfices peuvent être inscrits dans les comptes annuels d'un exercice ? ». Le verso, fidèle à la fiche, est inchangé. | C. com., art. L. 123-21 |
| ue9-07-k13 (supprimée) | « Comment comptabilise-t-on […] une facture client à établir ? » demandait une écriture à passer, ce que l'objectif des cartes exclut (aucune écriture). C'était aussi un doublon : le compte 4181 est déjà demandé par k04 et le compte 44587 par k12. | Supprimée, sans renumérotation. L'item Règles essentielles#3 reste sans carte propre ; son contenu est révisé par k04 et k12. | Plan de comptes 2026 (PCG, art. 1121-1) |
| ue9-07-k14 | « Quelle écriture constate […] les intérêts courus non échus ? » demandait une écriture à passer. L'intérêt de la carte est le choix du compte depuis la refonte du plan de comptes (1648 au lieu de 16884). | Question devenue un choix de compte : « Depuis le plan de comptes issu du règlement ANC n° 2022-06, sur quel compte porte-t-on les intérêts courus non échus d'un emprunt bancaire ? ». Verso : sur le compte 1648 (avant 2025 : 16884), en contrepartie de la charge d'intérêts (661) ; le compte 1688 ne sert plus qu'aux autres emprunts et dettes assimilées. Base, `src` et `url` sont inchangés. | Règlement ANC n° 2022-06 ; plan de comptes 2026, comptes 1648 et 1688 |
| ue9-07-k23 | La question en posait deux (« à quel exercice et à quel taux »). | Question unique sur le taux : « Selon l'article 515-1 du PCG, quel taux applique-t-on pour comptabiliser l'impôt sur les bénéfices de l'exercice ? ». Verso : le taux en vigueur à la date de clôture ; le rattachement à l'exercice au titre duquel l'entreprise est redevable devient la précision. La carte fait pendant à k24 (taux modifié par un vote après la clôture). | PCG, art. 515-1 (règlement ANC n° 2026-04) |

Les 29 autres cartes ont été jugées exactes au 15 octobre 2026 et sans ambiguïté qui justifie une retouche. Les points vérifiés sont les suivants :
- C. com., art. L. 123-12, L. 123-13, L. 123-20, L. 232-10 (y compris la suppression de la nullité textuelle par l'ordonnance n° 2025-229), L. 232-11, L. 232-12, L. 232-13, L. 241-3 et L. 242-6 ;
- CGI, art. 38, 2 bis (k17) ;
- PCG, art. 513-1, 513-2 et 513-5 (règlement n° 2022-06 : événement majeur et inhabituel ; écritures d'origine fiscale maintenues en 687 / 787) ;
- comptes de régularisation du plan 2026 (408, 4282, 4286, 4382, 4386, 4481, 468, 4181, 4482, 439, 467, 486, 487, 44586, 44587) et comptes d'affectation (120, 129, 1061, 1063, 1068, 110, 119, 457, 444, 695) ;
- CE, 13 mars 2025, n° 481538 (k25).

Trois cartes ont été examinées sans être modifiées :
- **k15 et k16** (charges et produits constatés d'avance). Leur verso cite les comptes, mais il commence par l'effet à retenir (la fraction est retirée des charges ou des produits, hors taxes). Ce sont des cartes de compréhension, pas des écritures chiffrées.
- **k28.** Sa seconde phrase répète la base du prélèvement déjà donnée par k27. Cette redite aide à mémoriser le piège et ne rend pas la carte inexacte.

## Recherches

Deux recherches WebSearch ont été faites, limitées à des sites officiels.

1. **« solde de l'impôt sur les sociétés 15 du quatrième mois clôture 31 décembre 15 mai »** (bofip.impots.gouv.fr, impots.gouv.fr, legifrance.gouv.fr). Résultat : le solde est dû au plus tard le 15 du quatrième mois qui suit la clôture. Si l'exercice est clos le 31 décembre, ou si aucun exercice n'est clos dans l'année, il est dû le 15 mai de l'année suivante. La règle est confirmée par impots.gouv.fr (« Imposition des résultats »), par le BOFiP (« IS – Modalités de paiement du solde ») et par la notice du relevé de solde n° 2572. Elle fonde la correction de k26.
2. **« règlement ANC 2026-04 impôt sur les bénéfices article 515-1 PCG taux en vigueur date de clôture »** (anc.gouv.fr, legifrance.gouv.fr). Résultat : le règlement n° 2026-04 du 4 mai 2026 a été homologué par l'arrêté du 12 août 2026 (JORFTEXT000054791025). L'article 515-1 du PCG prévoit bien que le taux à appliquer est celui en vigueur à la date de clôture. Une modification votée après la clôture affecte l'exercice du vote. Cette règle figurait déjà dans le PCG au 1er janvier 2025, ce qui justifie la mention `stable` des items. Les cartes k23 et k24 sont confirmées.

Aucune autre recherche n'a été jugée nécessaire. L'alinéa 2 de L. 123-21 (bénéfice à l'avancement) relève du texte constant du Code de commerce.

## Points à reprendre dans la fiche

1. **Règles essentielles#12 (paiement de l'IS).** La parenthèse « (le 15 mai de l'année suivante pour un exercice clos le 31 décembre) » se lit comme une illustration de la règle du 15 du quatrième mois. C'est en réalité une exception : pour une clôture au 31 décembre, le 15 du quatrième mois serait le 15 avril. Il faudrait écrire : « au plus tard le 15 du quatrième mois qui suit la clôture ; par exception, le 15 mai de l'année suivante si l'exercice est clos le 31 décembre ou si aucun exercice n'est clos au cours de l'année » (CGI, art. 1668, 2 ; BOI-IS-DECLA-20-20).
2. **Règles essentielles#12 (acomptes).** « Calculés sur le bénéfice du dernier exercice clos » n'est pas exact pour les grandes entreprises. Leur dernier acompte est modulé selon l'impôt estimé de l'exercice en cours (CGI, art. 1668, 1). L'item devrait réserver ce cas, ou s'en tenir au calendrier.
3. **Règles essentielles#7 (bénéfices réalisés).** L'item omet l'alinéa 2 de L. 123-21 : après inventaire, peut être inscrit le bénéfice réalisé sur une opération partiellement exécutée et acceptée par le cocontractant, lorsque sa réalisation est certaine et que le bénéfice global peut être évalué avec une sécurité suffisante. Sans cette précision, l'item se lit comme une règle sans exception.

Remarque hors fiche : la leçon du chapitre (`ue9-07.json`, paragraphe sur la balance après inventaire et l'IS) reprend la même parenthèse : « le 15 du quatrième mois suivant la clôture (15 mai pour une clôture au 31 décembre) ». Elle appelle la même correction que le point 1.

## Classement des exercices

Le classement automatique des 16 exercices QCM, QCM multiples et de classement du chapitre donne :

| nature | nombre | révisions espacées |
|---|---|---|
| `notion` | 10 | oui |
| `calcul` | 6 | non |
| `chiffre` | 0 | — |

Aucun désaccord n'a été relevé entre les classeurs. Les 10 exercices de nature `notion` entrent dans les révisions espacées avec les 34 cartes ci-dessus et les comptes du plan comptable. Les 6 exercices de nature `calcul` restent dans le chapitre mais ne sont pas proposés en révision. C'est l'objectif fixé pour ces révisions : des définitions et de la compréhension, pas de calcul.
