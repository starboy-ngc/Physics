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

- Provisions pour charges : les comptes 153 à 158 sont remplacés par la racine `152` : `1521` pensions et obligations similaires, `1522` restructurations, `1523` impôts, `1524` renouvellement des immobilisations (concessionnaires), `1525` gros entretien ou grandes révisions (ex-1572), `1526` provisions pour remise en état, `1527` autres provisions pour charges (ex-158). Le compte `151` (provisions pour risques : 1511 litiges, 1514 amendes et pénalités, 1515 pertes de change, 1516 pertes sur contrats, 1518 autres) demeure.
- Intérêts courus sur emprunts : le compte `1688` est presque entièrement supprimé ; les intérêts courus sont enregistrés par nature : `1618` (emprunts obligataires convertibles), `1638` (autres emprunts obligataires), `1648` (emprunts auprès des établissements de crédit). `1688` ne subsiste que pour les intérêts courus sur autres emprunts et dettes assimilées.
- Un chapitre qui parle d'intérêts courus sur un emprunt bancaire utilise donc `1648` (en signalant « avant 2025 : 1688 »).

## 7. Fiche documentaire par chapitre (`data/<ue>/<id>.fiche.json`)

Objectif : une fiche de cours de référence, **entièrement sourcée sur des textes officiels**, à jour, que l'étudiant lit avant la leçon et les exercices. On n'invente pas de cours : tout énoncé de la fiche est rattaché à un texte officiel précis ; si aucun texte officiel ne peut être trouvé, l'énoncé n'est pas écrit.

Sources officielles admises (le champ `url` doit pointer vers l'un de ces domaines, ou être `null`) : legifrance.gouv.fr (codes, lois, décrets, jurisprudence), bofip.impots.gouv.fr, impots.gouv.fr, anc.gouv.fr (PCG, règlements ANC), economie.gouv.fr, service-public.fr et entreprendre.service-public.fr, urssaf.fr, ameli.fr, francetravail.fr, travail-emploi.gouv.fr, securite-sociale.fr, enseignementsup-recherche.gouv.fr et bulletin-officiel.education.gouv.fr (programmes), education.gouv.fr, agirc-arrco.fr, amf-france.org, banque-france.fr, insee.fr, inpi.fr, infogreffe.fr, formalites.entreprises.gouv.fr, douane.gouv.fr, journal-officiel.gouv.fr, conseil-constitutionnel.fr, courdecassation.fr, conseil-etat.fr, cncc.fr, experts-comptables.fr, h2a.fr (Haute autorité de l'audit), info-retraite.fr (GIP Union Retraite), lassuranceretraite.fr (CNAV), unedic.org.

Méthode obligatoire : les pages officielles ne peuvent pas être ouvertes depuis cet environnement (WebFetch et curl bloqués). On utilise **WebSearch avec `allowed_domains`** restreint aux domaines ci-dessus (ex. `["legifrance.gouv.fr"]`, `["bofip.impots.gouv.fr"]`, `["urssaf.fr","service-public.fr"]`) : les résultats donnent l'URL officielle exacte et des extraits du texte. Règles :
- Une `url` n'est écrite que si elle est apparue telle quelle dans un résultat de recherche. **Jamais d'URL reconstituée ou devinée** (en particulier aucun identifiant LEGIARTI/LEGITEXT/PGP inventé). Sinon `url: null` et `src` reste précis (l'application construit alors un lien de recherche Légifrance).
- `cite` (facultatif) : extrait **verbatim** du texte officiel tel que restitué par le résultat de recherche, entre guillemets français, 1 à 3 phrases. Jamais une reformulation.
- Chiffres annuels (SMIC, PASS, barèmes, seuils, taux) : `fiab` « millésimé 20xx », l'année dans le texte, source officielle de l'année (urssaf.fr, bofip, service-public, legifrance).
- Au moins 12 recherches par chapitre ; chaque chiffre ou seuil est recoupé par au moins une source officielle.

Format (JSON strict, indentation 1 espace) :
```json
{
 "id": "ue2-02",
 "maj": "2026-10-14",
 "programme": { "ref": "Arrêté du 4 août 2025, annexe 1 (DCG, UE2 Droit des affaires), BO ESR n° 32 du 28 août 2025 ; arrêté du 13 février 2019 pour la session 2026", "url": "https://www.enseignementsup-recherche.gouv.fr/fr/bo/2025/Hebdo32/MENS2523324A", "points": ["Les points du programme officiel couverts par ce chapitre, dans les termes du programme"] },
 "textes": [ { "ref": "C. com., art. L. 223-14", "objet": "Cession de parts à des tiers : agrément", "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006223059", "version": "en vigueur (dernière modification : loi n° 2019-744 du 19 juillet 2019)" } ],
 "sections": [
  { "h": "Définitions", "items": [ { "t": "<b>Société</b> : contrat par lequel deux ou plusieurs personnes affectent des biens ou leur industrie à une entreprise commune…", "cite": "« La société est instituée par deux ou plusieurs personnes qui conviennent par un contrat d'affecter à une entreprise commune des biens ou leur industrie en vue de partager le bénéfice ou de profiter de l'économie qui pourra en résulter. »", "src": "C. civ., art. 1832", "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006444002", "fiab": "stable" } ] },
  { "h": "Règles essentielles", "items": [] },
  { "h": "Chiffres et seuils", "items": [] },
  { "h": "Ce qui a changé récemment", "items": [] },
  { "h": "Points de vigilance", "items": [] }
 ]
}
```
- `programme.points` : 3 à 8 points, repris du programme officiel (annexe de l'arrêté), pas inventés.
- `textes` : 5 à 15 textes de référence du chapitre, avec objet et version.
- `sections` : les cinq sections ci-dessus, dans cet ordre. 20 à 40 items au total ; « Règles essentielles » est la plus fournie (10 à 20 items). « Ce qui a changé récemment » liste les réformes 2023-2026 utiles (lois de finances, LFSS, ordonnances, règlement ANC 2022-06, décret 2024-152…) avec date et source. « Points de vigilance » : pièges d'examen et liens avec le DSCG, chacun rattaché à un texte.
- Chaque item : `t` (HTML limité aux balises du contrat, 1 à 4 phrases, formulation fidèle au texte), `src` (référence précise), `url` (officielle ou null), `fiab`, `cite` facultatif.
- Valider : `node validate.js data/<ue>/<id>.fiche.json`.

## 8. Cartes de notions (`data/<ue>/<id>.cartes.json`) — révisions espacées

Objectif : un jeu de cartes recto/verso « à la Anki » pour mémoriser les **définitions** et **comprendre les règles** du chapitre. Les révisions espacées (demain, 2, 5, 10, 20, 30 jours, puis chaque mois) ne portent que sur ces notions : **aucun calcul**, aucune écriture, aucun chiffre millésimé. La personne lit la question, formule sa réponse de tête, retourne la carte puis indique honnêtement si elle savait.

Règle d'or : **une carte ne dit rien que la fiche documentaire ne dise déjà.** Chaque carte repose sur un ou deux items de la fiche du chapitre (`base`), eux-mêmes sourcés sur un texte officiel. On n'invente pas de cours ; on reformule fidèlement, en plus court.

```json
{
 "id": "ue2-02",
 "maj": "2026-10-15",
 "cartes": [
  {
   "id": "ue2-02-k01",
   "type": "def",
   "q": "Qu'est-ce qu'une société à responsabilité limitée (SARL) ?",
   "r": "Une société instituée par une ou plusieurs personnes qui ne supportent les pertes qu'à concurrence de leurs apports.",
   "base": ["Définitions#0"],
   "src": "C. com., art. L. 223-1",
   "url": "https://www.legifrance.gouv.fr/…",
   "fiab": "stable"
  }
 ]
}
```

- `id` : `<id du chapitre>-kNN` (k01, k02…), unique et définitif (la progression de la personne y est attachée : ne jamais renuméroter une carte existante ; une carte supprimée laisse un trou).
- `type` : `def` (définition d'une notion, d'un acte, d'un document, d'un compte, d'un organe) ou `comp` (compréhension : condition, effet, sanction, distinction entre deux notions, rôle, raison d'être d'une règle, qualification d'une situation sans calcul).
- `q` (recto) : une seule question, 6 à 30 mots, terminée par « ? », compréhensible sans contexte (nommer la forme sociale, l'impôt, le contrat… dont on parle), qui ne contient pas la réponse. Une seule réponse attendue ; si la règle a des exceptions, la question en délimite le champ.
- `r` (verso) : la réponse, 8 à 70 mots, 1 à 3 phrases. HTML limité à `b i br ul li`. Commence par l'élément de réponse essentiel (mis en `<b>` si utile), puis la précision qui aide à retenir. Fidèle au texte de la fiche : mêmes conditions, mêmes exceptions, même vocabulaire juridique.
- `base` : 1 ou 2 références `"<Titre de section>#<index>"` vers les items de la fiche (index à partir de 0) qui fondent la réponse.
- `src` et `url` : **copiés à l'identique** depuis le premier item de `base` (`url` : la même URL officielle ou `null`). Jamais d'URL nouvelle.
- `fiab` : toujours `stable`. Les items millésimés (SMIC, PASS, barèmes, seuils annuels, taux de l'année) ne donnent pas de carte.
- Interdits : calcul à faire (montant, taux appliqué, prorata, délai à décompter à partir de dates), écriture comptable chiffrée, question piège, question « par cœur » sur un chiffre annuel. Un chiffre **stable** qui fait partie d'une règle (100 associés au plus dans une SARL, majorité des deux tiers) est admis quand la question porte sur la règle.
- Volume : 15 à 35 cartes par chapitre ; au moins 5 `def` et 5 `comp`. Chaque item de la section « Définitions » donne au moins une carte ; les « Règles essentielles » sont largement couvertes ; « Points de vigilance » et « Ce qui a changé récemment » donnent des cartes de compréhension.
- Valider : `node validate.js data/<ue>/<id>.cartes.json` (le validateur relit la fiche voisine pour contrôler `base`, `src` et `url`).

Les exercices des chapitres portent aussi un champ `nature` : `notion` (définition, règle, qualification, choix d'un compte, classement, sans calcul), `calcul` (il faut calculer : montant, taux, prorata, délai à décompter) ou `chiffre` (rappel d'un chiffre millésimé). Seuls les QCM, QCM multiples et classements de nature `notion` entrent dans les révisions espacées, avec les cartes et les comptes du plan comptable (intitulé et rôle, comptes supprimés exclus).

## 9. Rappels courts (`data/ue1/<id>.rappel.json`) — UE1 Fondamentaux du droit

L'UE1 n'a ni exercices ni cartes : chaque chapitre est une **page de rappels** (l'essentiel à retenir avant le
DSCG), tirée de la fiche documentaire vérifiée du chapitre (`<id>.fiche.json`, qui reste la référence et n'est pas
affichée). Règle d'or : **un rappel ne dit rien que la fiche ne dise déjà**, et ne s'appuie pas sur un item que le
rapport du chapitre (`rapports/<id>.md`) signale comme non vérifié.

```json
{
 "id": "ue1-01", "ue": "UE1", "ordre": 1, "title": "La règle de droit et ses sources", "maj": "2026-10-19",
 "resume": "Une phrase : ce que la page permet de se remettre en tête.",
 "rappels": [
  { "t": "<b>Hiérarchie des normes</b> : …", "base": ["Règles essentielles#3"], "src": "Constitution, art. 55", "url": "https://www.legifrance.gouv.fr/…" }
 ]
}
```

- 8 à 14 rappels, 650 mots au plus pour la page ; chaque rappel : 12 à 55 mots, une ou deux phrases, commence par
  la notion en `<b>` ; HTML limité à `b i`.
- `base` : 1 à 3 items de la fiche (`<section>#<index>`, index à partir de 0) ; `src` et `url` copiés à
  l'identique depuis le premier item de base (`url` null si l'item n'en a pas). Aucun item millésimé.
- Ordre : celui d'une révision rapide (définitions, règles essentielles, pièges), en couvrant les points
  du programme du chapitre.
- Validation : `node validate.js data/ue1/<id>.rappel.json`.
