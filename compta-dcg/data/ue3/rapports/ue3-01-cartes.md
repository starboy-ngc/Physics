# Cartes de notions : ue3-01 (Sources du droit social et institutions)

15 octobre 2026. Fichier : `data/ue3/ue3-01.cartes.json`. Fiche de référence : `data/ue3/ue3-01.fiche.json`. Contrat : `data/CONTRAT.md`, section 8.

## Méthode

1. **Rédaction depuis la fiche.** 35 cartes (k01 à k35) ont été rédigées à partir des items de la fiche, sans calcul ni chiffre millésimé. Chaque carte repose sur un ou deux items (`base`), dont elle reprend `src` et `url`.
2. **Relecture de fidélité.** Le premier relecteur a contrôlé les 35 cartes au regard de la fiche et en a corrigé 7 (k01, k16, k17, k26, k28, k32, k33). Il n'a fait ni suppression ni ajout.
3. **Relecture d'exactitude.** Le second relecteur a contrôlé les 35 cartes au regard du droit en vigueur au 15 octobre 2026 : Code du travail, Code de l'organisation judiciaire, Code de la sécurité sociale, Préambule de 1946 et jurisprudence de la Cour de cassation. Il a aussi vérifié que chaque question n'appelle qu'une seule réponse, et il a recherché les doublons. Bilan : 8 cartes corrigées, aucune suppression, aucun ajout.
4. **Recherches.** Une recherche WebSearch sur legifrance.gouv.fr, sur 3 autorisées, a porté sur l'article L. 8115-1. Deux points ont été vérifiés avec des données du dépôt déjà vérifiées :
   - `data/FAITS-CONFIRMES.md` : loi n° 2026-403, art. 5, et article R. 1321-2 toujours en vigueur au 14 octobre 2026 (cartes k22 et k23) ;
   - rapport `data/ue3/rapports/ue3-01.md`, recherche n° 2 : arrêt Cass. soc., 28 mai 2026, n° 24-19.461 et s. (cartes k16 et k17).

`node validate.js data/ue3/ue3-01.cartes.json` : ✓ (35 cartes, 9 déf.).

## Bilan

- **35 cartes**, le maximum prévu par le contrat : 9 de définition (`def`) et 26 de compréhension (`comp`). Aucun identifiant libre.
- Chaque item des sections « Définitions », « Règles essentielles », « Ce qui a changé récemment » et « Points de vigilance » a au moins une carte.
- **Items de la fiche sans carte** (tous dans « Chiffres et seuils ») :
  - **#1** (salaires, 3 ans) et **#3** (rupture conventionnelle, 12 mois) : leur contenu est repris dans les réponses de k34 et k35, sans être cité dans `base`.
  - **#4** (taux de ressort du conseil de prud'hommes, 5 000 €) : montant fixé par décret, déjà modifié en 2020. Une carte se réduirait au rappel d'un montant.
  - **#5** (délit d'obstacle, 1 an et 37 500 €) : rappel d'un quantum de peine.
  - **#8** (visite d'information et de prévention) : délais de santé au travail, en marge des sources du droit social.

  Le jeu atteint le plafond de 35 cartes : un ajout imposerait une suppression.

## Corrections de la première relecture (fidélité à la fiche)

Le résultat transmis par la première relecture est tronqué après k32. Les lignes k32 et k33 ont été complétées d'après la comparaison du fichier avec sa version précédente.

| cible | problème | correction |
|---|---|---|
| k01 | La question parlait des droits garantis « aux travailleurs ». La fiche (Définitions#4) ne dit pas cela pour la liberté syndicale de l'al. 6 : la question généralisait. | Question reformulée : « Quels droits sociaux le Préambule de la Constitution du 27 octobre 1946 garantit-il en ses alinéas 6, 7 et 8 ? ». La réponse est inchangée. |
| k16 | Le recto demandait ce qui se passe quand le salarié refuse, mais le verso commençait par le délai pour refuser, ce qui ne répond pas à la question. La réponse ajoutait aussi la réserve « dès lors que l'accord s'en tient à… », une inférence que la fiche ne formule pas ainsi. | Le verso commence par l'élément essentiel : l'employeur a deux mois à compter du refus pour licencier, pour un motif spécifique qui constitue une cause réelle et sérieuse. Il reprend l'exception telle que la fiche la donne : si l'accord comporte des dispositions étrangères à ses objets et modifie le contrat, le licenciement est sans cause réelle et sérieuse. Question précisée (« refuse par écrit »). Base : Règles essentielles#9 et Ce qui a changé récemment#2. |
| k17 | La question ne délimitait pas son champ : la condition « et modifiant son contrat » n'apparaissait qu'au verso. Le sigle APC n'était pas développé. | Condition « et modifiant son contrat » ajoutée à la question. Le verso commence par « Il est sans cause réelle et sérieuse », avec « accord de performance collective » en toutes lettres. |
| k26 | Question trop vague (« Comment fonctionne le régime… ? »), à laquelle plusieurs réponses justes étaient possibles. Les manquements visés n'étaient pas donnés. | Question recentrée : « Quelle autorité peut sanctionner par une amende administrative certains manquements au Code du travail, et à quelles conditions ? ». Le verso nomme le directeur régional de l'économie, de l'emploi, du travail et des solidarités, donne les conditions (rapport d'un agent de contrôle, absence de poursuites pénales), liste les manquements de la fiche et rappelle le recours devant le tribunal administratif. |
| k28 | La fiche dit que le conseil de prud'hommes n'est pas compétent « notamment » en matière d'AT/MP. La parenthèse « (accidents du travail, maladies professionnelles) » présentait ces litiges comme les seules exceptions, ce qui est inexact. La réponse était à la limite des 70 mots. | « notamment » rétabli : « hors litiges attribués par la loi à une autre juridiction (notamment accidents du travail et maladies professionnelles) ». Réponse resserrée. |
| k32 | La réponse présentait comme complète la liste des litiges du pôle social. Elle omettait les litiges du Code du travail (L. 4163-17) que mentionne Règles essentielles#15. | « notamment » ajouté devant la liste des litiges du pôle social. |
| k33 | Les délais de 2 ans et de 12 mois étaient donnés sans leurs exceptions, comme s'ils valaient pour toute action. | Exceptions ajoutées (dommage corporel, salaire, discrimination, harcèlement). Base complétée par Points de vigilance#1. La relecture d'exactitude a ensuite revu cette carte (voir ci-dessous). |

## Corrections de la relecture d'exactitude

| cible | problème | correction | source |
|---|---|---|---|
| k03 | L'article L. 2231-1 pose le principe. Dans les entreprises dépourvues de délégué syndical, un accord peut aussi être conclu avec des élus ou des salariés mandatés, ou approuvé par le personnel. Sans délimitation, la question appelait une réponse vraie seulement dans le cas général. | Question : « En principe, qui sont les parties à une convention ou à un accord collectif de travail selon l'article L. 2231-1 du Code du travail ? ». La réponse est inchangée : la fiche ne traite pas des modes dérogatoires. | C. trav., art. L. 2231-1 ; L. 2232-21 et suivants |
| k08 | La règle de 1988 (« seul le plus favorable est accordé ») était présentée comme valable pour tout concours de conventions. Depuis les ordonnances de 2017, ce sont les trois blocs qui règlent le rapport entre branche et entreprise. Dans le bloc 3, l'accord d'entreprise prévaut, même s'il est moins favorable. | Question : « Selon la jurisprudence de l'assemblée plénière de 1988, comment se règle un concours de conventions collectives applicables à un même salarié ? ». La réponse donne la règle de non-cumul et de comparaison avantage par avantage. Elle ajoute qu'entre branche et entreprise, l'équivalence s'apprécie par ensemble de garanties dans les blocs 1 et 2, et que l'accord d'entreprise prime dans le bloc 3. Base complétée par Règles essentielles#3. | Cass. ass. plén., 18 mars 1988, n° 84-40.083 ; C. trav., art. L. 2253-1 à L. 2253-3 |
| k16 | Le membre de phrase « le salarié dispose d'un mois pour refuser par écrit » répétait k15. Il ne répondait pas à la question, qui pose déjà le refus écrit. | Membre de phrase retiré. La réponse garde le principe (deux mois pour licencier, motif spécifique constituant une cause réelle et sérieuse) et l'exception jurisprudentielle de 2026. | C. trav., art. L. 2254-2 ; Cass. soc., 28 mai 2026 |
| k25 | La question « De quels pouvoirs les agents de contrôle disposent-ils dans les établissements ? » était trop ouverte. D'autres réponses justes, absentes du verso, étaient possibles : communication de documents, arrêt temporaire de travaux, mises en demeure. | Question : « Où les agents de contrôle de l'inspection du travail ont-ils un droit d'entrée, et quelle limite s'applique aux locaux habités ? ». Le verso commence par le droit d'entrée et sa limite (accord des occupants). Identité, registres et procès-verbaux restent en précision. | C. trav., art. L. 8113-1 et suivants ; L. 4731-1 |
| k26 | La liste des manquements était présentée comme complète. Or l'article L. 8115-1 vise aussi l'obligation de décompte de la durée du travail (L. 3171-2), comme l'a confirmé la recherche. La mention du document unique faisait en outre doublon avec k27. | « notamment » ajouté devant la liste des manquements. Le document unique est laissé à k27. Réponse de 67 mots. | C. trav., art. L. 8115-1 (3° : L. 3171-2) ; recherche n° 1 |
| k27 | Même liste présentée comme complète, sans le décompte de la durée du travail. La question nommait « la loi du 25 juin 2026 », dont le numéro et la date ne figuraient que dans un seul résultat (rapport de la fiche, « Points non tranchés »). La date de version du 27 juin 2026 est, elle, confirmée par deux résultats. | Question : « Quel manquement l'amende administrative de l'article L. 8115-1 du Code du travail sanctionne-t-elle aussi depuis le 27 juin 2026 ? ». La réponse précise que l'absence de document unique s'ajoute aux manquements déjà visés, « notamment » ceux qu'elle cite. | C. trav., art. L. 8115-1 (version en vigueur depuis le 27 juin 2026) ; rapport `ue3-01.md` |
| k33 | Après la première relecture, la réponse reprenait les exceptions, qui sont la réponse entière de k35 : doublon. | Question délimitée (« En principe, quels délais… ? »). Réponse limitée aux deux délais et à leurs points de départ ; les exceptions restent dans k35. Base ramenée à Chiffres et seuils#0. | C. trav., art. L. 1471-1 |
| k35 | La discrimination figurait parmi les exceptions sans le délai qui s'applique à la place. L'item Chiffres et seuils#2 (5 ans) n'avait aucune carte. | Ajout de « (5 ans à compter de sa révélation, L. 1134-5) ». Base complétée par Chiffres et seuils#2. Réponse de 67 mots. | C. trav., art. L. 1471-1, al. 3, et L. 1134-5 |

Les autres cartes ont été contrôlées sans changement : k01, k02, k04 à k07, k09 à k15, k17 à k24, k28 à k32 et k34.

## Recherches faites

1 recherche sur les 3 autorisées.

1. WebSearch, `allowed_domains` : legifrance.gouv.fr, requête « article L. 8115-1 code du travail amende administrative décompte de la durée de travail L. 3171-2 durées maximales repos ».
   - **Confirmé.** La liste des manquements passibles d'une amende administrative comprend les durées maximales du travail (L. 3121-18 à L. 3121-25), les repos et l'obligation de décompte de la durée du travail de l'article L. 3171-2.
   - **Non vérifié.** Le résultat ne restitue pas la version de 2026, si bien que l'ajout du document unique n'a pas été vérifié de nouveau. Il est repris de la fiche, où deux résultats le confirment.
   - Sources : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000032375395/ et https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037312991

Vérifications faites sans recherche, avec des données du dépôt :
- `data/FAITS-CONFIRMES.md` : suppression des mots « de dépôt et » dans L. 1321-4 (loi n° 2026-403, art. 5, en vigueur le 28 mai 2026) et maintien de R. 1321-2 (dépôt au greffe) au 14 octobre 2026. Les cartes k22 et k23 sont exactes.
- `data/ue3/rapports/ue3-01.md`, recherche n° 2 : arrêt Cass. soc., 28 mai 2026, n° 24-19.461 et s. (FS-B+R), avec son URL et sa citation. Les cartes k16 et k17 sont exactes.

## Points à reprendre dans la fiche

La fiche n'a pas été modifiée.

1. **Règles essentielles#14 et Ce qui a changé récemment#4.** La liste des manquements passibles d'une amende administrative (L. 8115-1) omet l'obligation de décompte de la durée du travail (L. 3171-2), confirmée par la recherche n° 1. Il faut la compléter ou la faire précéder de « notamment ».
2. **Ce qui a changé récemment#4** (ainsi que `src` de Règles essentielles#14 et l'entrée de `textes`). Le numéro et la date de la « loi n° 2026-534 du 25 juin 2026 » ne reposent que sur un seul résultat, comme le signale déjà le rapport de la fiche. Ils sont à reconfirmer.
3. **Points de vigilance#3.** La règle de 1988 (non-cumul, seul le plus favorable est accordé) est donnée sans limite. Seuls les blocs 1 et 2 sont mentionnés pour l'articulation entre branche et entreprise. Il faut préciser que, dans le bloc 3, l'accord d'entreprise prévaut sur la branche même s'il est moins favorable (L. 2253-3).
4. **Définitions#1** (complément, pas une erreur). L'item ne donne que le principe de L. 2231-1. Il pourrait signaler les modes de conclusion propres aux entreprises dépourvues de délégué syndical : élus, salariés mandatés, approbation par le personnel (L. 2232-21 et suivants).

## Classement des exercices

Le classement automatique porte sur les 25 exercices QCM, QCM multiples et classements du chapitre (20 QCM, 3 QCM multiples, 2 classements) :

| nature | nombre |
|---|---|
| notion | 23 |
| calcul | 2 |
| chiffre | 0 |

Aucun désaccord entre les classements. Les deux exercices de nature calcul sortent des révisions espacées :
- **#6** : date d'entrée en vigueur d'un règlement intérieur ;
- **#20** : date limite pour contester un licenciement.

Les notions qu'ils illustrent restent révisées par les cartes k23 (entrée en vigueur un mois après les formalités de publicité) et k33 (prescription de 12 mois pour la rupture). Les 23 exercices de nature notion entrent dans les révisions espacées, avec les 35 cartes.
