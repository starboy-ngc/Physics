# Contrat de contenu — Débit Crédit (révision DCG → DSCG)

Ce document fixe le format et les règles de qualité de tout contenu produit pour l'application.
Public : adulte qui reprend le DSCG et dont les bases du DCG sont floues. Niveau visé : DCG (sessions 2026 et programme réformé 2027).
Langue : français, orthographe soignée, typographie française (espaces avant « : ; ? ! », guillemets « »), chiffres avec espace comme séparateur de milliers (4 800) et virgule décimale (12,5 %).

## 1. Un chapitre = un fichier JSON

Chemin : `/home/user/Physics/compta-dcg/data/<ue>/<id>.json` (ex. `data/ue4/ue4-03.json`). JSON strict, UTF-8, sans commentaire ni virgule finale.
Valider avec : `node /home/user/Physics/compta-dcg/validate.js /home/user/Physics/compta-dcg/data/<ue>/<id>.json` — le fichier doit passer sans erreur.

```json
{
  "id": "ue4-03",
  "ue": "UE4",
  "ordre": 3,
  "title": "Les bénéfices industriels et commerciaux",
  "resume": "Une phrase qui dit ce que le chapitre apprend.",
  "duree": "50 min",
  "niveau": 2,
  "lecon": [
    { "h": "Titre de section", "html": "<p>…</p><ul><li>…</li></ul>" },
    { "h": "Titre", "html": "<p>…</p>", "entry": [ { "a": "607", "d": 4000, "c": 0 }, { "a": "401", "d": 0, "c": 4000 } ], "lib": "Libellé de l'écriture" }
  ],
  "sources": [ { "ref": "CGI, art. 39, 1", "note": "Conditions générales de déduction des charges" } ],
  "exercices": [ … ]
}
```

- `lecon` : 5 à 8 sections, 80 à 220 mots chacune, qui couvrent tout le contenu attendu du chapitre (voir `plan.json`). Une fiche de cours complète, pas un résumé.
  Balises autorisées dans `html` : `p ul ol li b i code br table thead tbody tr th td` et `<div class="note">…</div>` (encadré « règle à retenir », 1 à 2 par chapitre) et `<span class="mono">…</span>` pour les nombres. Aucune autre balise, aucun attribut autre que `class` sur div/span.
  `entry` (facultatif, surtout UE9/UE10) : un exemple d'écriture, équilibrée (total débit = total crédit), `a` = numéro de compte PCG 2025 en chaîne.
- `sources` : 3 à 10 références précises (article de code, règlement ANC, BOFiP, norme) utilisées par la leçon.
- `niveau` : 1 (fondamental), 2 (intermédiaire), 3 (approfondi).

## 2. Les exercices

22 à 30 exercices par chapitre. Répartition : au moins 60 % de `qcm` + `multi` ; le reste en `calc`, `tri`, `ecriture` selon la matière (les écritures surtout en UE9 et UE10 ; au moins 2 `calc` dans chaque chapitre, y compris en droit : délais, seuils, majorités, indemnités). Progression du facile au difficile. Chaque exercice porte `niveau` 1-3, `src` et `fiab`.

Champs communs : `type`, `q` (énoncé complet et autosuffisant : toutes les données nécessaires y figurent), `why` (explication de 2 à 5 phrases qui justifie la réponse, montre le calcul quand il y en a un, et cite la source ; elle doit aussi dire pourquoi les distracteurs principaux sont faux quand ce n'est pas évident), `src` (référence précise, ex. « C. com., art. L. 223-2 », « CGI, art. 219, I-b », « PCG art. 214-1 », « C. trav., art. L. 1234-1 »), `fiab` (« stable » si la règle ne dépend pas d'un millésime, sinon « millésimé 2025 » ou « millésimé 2026 »), `niveau`.

Types :
- `qcm` : `opts` 4 options (5 max), `a` index de l'unique bonne réponse. Une seule réponse défendable ; distracteurs plausibles et clairement faux ; jamais « toutes les réponses » / « aucune ». Formulation sans indice (pas d'option nettement plus longue que les autres).
- `multi` : QCM à réponses multiples comme dans les banques de questions DCG. `opts` 4 à 6 options, `a` tableau de 2 à 4 index corrects. L'énoncé précise « plusieurs réponses possibles ».
- `calc` : `a` nombre (réponse), `unit` (« € », « % », « jours », « mois »… ou ""), `tol` tolérance absolue (par défaut 0,5 ; mettre 1 pour les montants arrondis à l'euro si plusieurs arrondis sont acceptables). Un seul nombre attendu. Préciser l'arrondi attendu dans l'énoncé.
- `tri` : `cats` 2 à 7 catégories, `items` 4 à 10 paires `[libellé, indexCatégorie]`. Chaque item n'appartient qu'à une seule catégorie.
- `ecriture` : `palette` 4 à 8 numéros de comptes (les bons + 1 à 3 distracteurs crédibles), `sol` tableau d'au moins une solution ; chaque solution est une liste de lignes `{ "a": "607", "d": 4000, "c": 0 }` équilibrée. `lib` libellé. Si plusieurs présentations sont admises (ex. deux lignes 431 ou une seule), les lister toutes dans `sol`. Les comptes utilisés doivent exister dans le PCG 2025.

## 3. Règles de fond : zéro erreur

1. Droit et normes en vigueur en 2025-2026 : Code de commerce, Code civil, Code du travail, Code de la sécurité sociale, CGI, BOFiP, PCG (règlement ANC n° 2014-03 consolidé, modifié par le règlement ANC n° 2022-06 applicable aux exercices ouverts à compter du 1er janvier 2025).
2. Privilégier les mécanismes et règles durables. Quand un chiffre annuel est indispensable (SMIC, PASS, barème de l'IR, seuils de régimes, plafonds micro, taux réduit d'IS et son plafond, seuils de commissariat aux comptes, seuil de franchise de TVA…), le dater dans l'énoncé (« en 2025 ») et marquer `fiab` « millésimé 2025 ». Ne jamais présenter un chiffre daté comme intemporel.
3. En cas de doute sur un chiffre, un seuil ou une règle : vérifier par recherche web (WebSearch) sur des sources fiables (legifrance, bofip.impots.gouv.fr, service-public.fr, urssaf.fr, anc.gouv.fr, revues professionnelles reconnues) ; si le doute subsiste, ne pas poser la question. Une question incertaine est supprimée, pas devinée.
4. Pas de question piège sur une subtilité controversée ; pas de question dont la réponse dépend d'une doctrine discutée.
5. Les énoncés de calcul doivent être entièrement résolubles avec les données fournies et donner exactement `a` (recalculer avant d'écrire).

## 4. PCG 2025 (règlement ANC n° 2022-06) — à appliquer partout

- Cessions d'immobilisations incorporelles et corporelles : `657` Valeurs comptables des immobilisations incorporelles et corporelles cédées et `757` Produits des cessions d'immobilisations incorporelles et corporelles. Les comptes `675` et `775` n'existent plus. Immobilisations financières : `667` / `767` (6671 valeurs comptables des immobilisations financières cédées ; 6673/7673 pour les VMP).
- Le résultat exceptionnel est limité aux événements majeurs et inhabituels (règlement 2022-06). Les cessions d'immobilisations et les subventions d'investissement ne sont plus exceptionnelles. Charges exceptionnelles : compte `678` (avec subdivisions libres) ; dotations/reprises exceptionnelles `6875` / `7875`.
- Les transferts de charges (`791`, `796`, `797`) sont supprimés : refacturations en `708`, remboursements de charges de personnel en `649`, indemnités d'assurance en `7587`.
- Quote-part de subvention d'investissement virée au résultat : compte `747` (plus `777`). Vérifier par recherche avant d'utiliser tout autre compte modifié par la réforme (comptes de provisions notamment).
- Un seul plan de comptes (comptes obligatoires et facultatifs) remplace les systèmes abrégé/développé.
- Quand un manuel ancien utilise un compte supprimé, la leçon peut le signaler en une phrase (« avant 2025 : 675/775 ») pour aider la personne qui a appris avec ces comptes.

## 5. Style

- Ton direct, phrases courtes, exemples chiffrés réalistes, noms d'entreprises fictifs neutres.
- Une leçon enseigne : définition, règle, exemple, piège classique, lien avec le DSCG quand il existe.
- `why` ne se contente jamais de « la réponse est B » : elle explique.

## 6. Compléments PCG 2025 confirmés (recoupés par deux sources le 5 octobre 2026)

- Provisions pour charges : les comptes 153 à 158 sont remplacés par la racine `152` : `1521` pensions et obligations similaires, `1522` restructurations, `1523` impôts, `1524` renouvellement des immobilisations (concessionnaires), `1525` gros entretien ou grandes révisions (ex-1572), `1526` autres provisions pour charges. Le compte `151` (provisions pour risques : 1511 litiges, 1514 amendes et pénalités, 1515 pertes de change, 1516 pertes sur contrats, 1518 autres) demeure.
- Intérêts courus sur emprunts : le compte `1688` est presque entièrement supprimé ; les intérêts courus sont enregistrés par nature : `1618` (emprunts obligataires convertibles), `1638` (autres emprunts obligataires), `1648` (emprunts auprès des établissements de crédit). `1688` ne subsiste que pour les intérêts courus sur autres emprunts et dettes assimilées.
- Un chapitre qui parle d'intérêts courus sur un emprunt bancaire utilise donc `1648` (en signalant « avant 2025 : 1688 »).
