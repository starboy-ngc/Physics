# Architecture — Compensation Analytics Engine

Version du moteur : **1.0.0** (V1 / MVP).

## 1. Principe directeur

Le logiciel est un **moteur d'analyse paramétrable**, pas un fichier Excel figé.
Chaque étape du pipeline est un module découplé qui ne connaît que la structure
de données produite par l'étape précédente.

```
IMPORT ─▶ CONTRÔLE ─▶ NORMALISATION ─▶ PARAMÉTRAGE ─▶ MOTEUR DE CALCUL
      ─▶ ANALYSE ─▶ VISUALISATION ─▶ RESTITUTION ─▶ EXPORT
```

## 2. Décision structurante : zéro dépendance externe

Le moteur n'importe **que la bibliothèque standard Python**. En particulier :

| Besoin | Solution retenue | Solution écartée |
|---|---|---|
| Lecture XLSX/XLSM | `zipfile` + `xml.etree` (`io/tabular.py`) | openpyxl, pandas |
| Écriture XLSX | Génération OOXML directe (`io/xlsx_writer.py`) | xlsxwriter |
| Statistiques | `statistics_engine.py` | numpy, scipy |
| Graphiques | SVG généré côté moteur | matplotlib, plotly, Chart.js |
| Restitution | HTML autoportant + impression navigateur | wkhtmltopdf, reportlab |
| Configuration | JSON (`config/*.json`) | YAML (dépendance), SQLite (binaire) |

Conséquences : aucune DLL tierce, aucun binaire à faire homologuer, aucune
chaîne d'approvisionnement logicielle à surveiller, packaging trivial.

## 3. Modules

```
compensation_analytics/
├── version.py              Version MAJOR.MINOR.PATCH portée par les restitutions
├── cli.py                  Pilotage (une IHM utiliserait les mêmes appels)
├── io/
│   ├── tabular.py          Lecture CSV / XLSX / XLSM → Table (brut)
│   └── xlsx_writer.py      Écriture XLSX multi-onglets
└── core/
    ├── errors.py           Erreurs métier (message utilisateur / détail technique)
    ├── config.py           Chargement + fusion des paramètres
    ├── mapping.py          Colonnes source → champs normalisés
    ├── normalize.py        Table → Population (Employee)
    ├── quality.py          Data Quality Check
    ├── statistics_engine.py Formules — source unique de vérité
    ├── metrics.py          Indicateurs métier + règles de confidentialité
    ├── segmentation.py     Filtres combinables, découpage par dimension
    ├── reporting.py        Restitution HTML + SVG
    ├── export.py           Export Excel / CSV
    ├── logging_setup.py    Log technique sans donnée personnelle
    ├── traceability.py     Manifeste de reproductibilité
    └── pipeline.py         Orchestration
```

**Règle de dépendance** : `io` ne connaît pas `core` ; `core.statistics_engine`
ne connaît rien ; `metrics` ne connaît que `statistics_engine`, `normalize` et
`config` ; `reporting` et `export` ne connaissent que le dictionnaire de
résultat. Aucune formule n'est dupliquée hors de `statistics_engine`.

## 4. Couche pivot

```
Fichier RH ─▶ Table (brut) ─▶ MappingResult ─▶ Population[Employee] ─▶ payload
```

`Employee` est le contrat interne. Changer de format d'import n'affecte que
`io/tabular.py` et `config/population_mapping.json` ; ajouter une analyse
n'affecte que `metrics.py`.

## 5. Sécurité et conformité IT

| Contrainte | Mise en œuvre |
|---|---|
| Aucune sortie réseau | Aucun `socket`, `urllib`, `requests` dans le code ; restitution HTML sans `http://`, `<script src>`, `<link>` ni `@import` (vérifié par test) |
| Aucun processus enfant | Aucun `subprocess`, `os.system`, Shell ou PowerShell |
| Aucun code dynamique | Aucun `eval`/`exec` ; les filtres sont des structures de données interprétées par comparaison |
| Aucun droit administrateur | Écriture limitée au dossier de sortie choisi par l'utilisateur ; aucune écriture registre |
| Fichiers temporaires | Le moteur n'en crée pas ; il écrit uniquement les livrables demandés |
| Données personnelles | Jamais dans les logs ni dans les messages d'erreur ; export individuel désactivé par défaut ; identifiants hachés SHA-256 |
| Dépendances | Zéro. `pip install` n'est jamais requis |

## 6. Confidentialité — petits effectifs

`privacy_parameters.json`, appliqué dans `metrics.py` (donc impossible à
contourner depuis un écran) :

| Paramètre | Défaut | Effet |
|---|---|---|
| `min_headcount_publish` | 5 | En deçà, les indicateurs sont masqués |
| `min_headcount_warning` | 10 | En deçà, avertissement d'interprétation |
| `min_headcount_chart` | 10 | En deçà, graphiques désactivés |
| `anonymise_identifiers` | true | Matricule remplacé par une empreinte SHA-256 tronquée |

## 7. Formulation des résultats

Une valeur hors bornes interquartiles est présentée comme
**« Situation atypique à analyser »**, jamais comme une anomalie RH : le
critère est statistique, la lecture est contextuelle (marché, métier,
historique, performance). Un test vérifie que la chaîne « anomalie RH »
n'apparaît pas dans la restitution.

L'écart-type reste calculé et exporté comme statistique technique, mais n'est
pas présenté en KPI de pilotage : les ratios de dispersion (Q3/Q1, P90/P10,
moyenne/médiane) sont les indicateurs mis en avant.

## 8. Percentiles

Méthode inclusive à interpolation linéaire (type 7), identique à
`PERCENTILE.INCLUSIVE` d'Excel et au défaut de numpy : un contrôle refait sous
Excel par l'équipe C&B donne exactement la même valeur. Les valeurs de
référence sont figées dans `tests/test_statistics.py`.

## 9. Traçabilité

Chaque analyse produit un manifeste JSON : moteur, version, date, nom et
empreinte SHA-256 du fichier source, effectif, filtres, intégralité des
paramètres. Il contient l'empreinte du fichier, jamais son contenu — donc
aucune donnée personnelle.

## 10. Performance

Mesures sur population fictive (`python3 tools/benchmark.py`), poste Linux
conteneurisé, secondes :

| Effectif | Import | Normalisation | Qualité | Calculs | Restitution | Total | HTML | RAM |
|---|---|---|---|---|---|---|---|---|
| 1 000 | 0,08 | 0,01 | 0,00 | 0,02 | 0,01 | **0,12** | 0,2 Mo | 24 Mo |
| 10 000 | 0,87 | 0,10 | 0,02 | 0,31 | 0,07 | **1,37** | 1,3 Mo | 55 Mo |
| 50 000 | 5,04 | 0,56 | 0,22 | 1,88 | 0,02 | **7,72** | 0,7 Mo | 164 Mo |
| 100 000 | 9,85 | 1,45 | 0,25 | 4,20 | 0,03 | **15,78** | 0,7 Mo | 310 Mo |

Comportement linéaire. **Seuil identifié** : au-delà de ~50 000 salariés,
l'import XLSX (parsing XML) domine et l'analyse dépasse les 10 secondes ;
au-delà de ~200 000, la population entièrement en mémoire deviendrait
contraignante sur un poste à 8 Go.

Un premier plafond a déjà été traité : sans garde-fou, le nuage de points
produisait 100 000 cercles SVG et un HTML de 12,8 Mo (navigateur inutilisable).
`chart_parameters.scatter_max_points` (5 000 par défaut) applique un
échantillonnage systématique à pas constant — déterministe, donc reproductible
et traçable — et l'échantillonnage est signalé dans la restitution.

Leviers si le seuil doit être repoussé (V3) : import CSV plutôt que XLSX
(≈10× plus rapide), lecture en flux sans matérialiser le tableau brut,
pré-agrégation par segment.

## 10 bis. Empreinte des livrables

L'export Excel et le manifeste restent de taille modeste quel que soit
l'effectif : ils contiennent des agrégats, pas la population — sauf activation
explicite de `export_parameters.include_individual_data`.

## 11. Feuille de route

| Version | Périmètre | État |
|---|---|---|
| V0 — PoC | Import, contrôle, KPI, tableau | ✅ |
| V1 — MVP | Paramétrage, filtres, percentiles, ratios, nuage de points, export Excel | ✅ |
| V2 — Enterprise | Logs, versioning, tests, traçabilité, packaging, PDF | 🟡 partiel (logs, versioning, tests, traçabilité faits ; packaging et PDF natif à faire) |
| V3 — Optimisation | Performance, IHM, segmentation avancée, automatisation | ⬜ |

### Extensions prévues sans réécriture du cœur

Chacune s'ajoute comme fonction de `metrics.py` + section de `reporting.py` +
paramètres dédiés, sans toucher au pipeline : égalité salariale, promotions,
augmentations, variable, compa-ratio, positionnement en grille, budget
salarial, évolution N/N-1.

## 12. Packaging (V2, à faire)

Cible : dossier autonome, sans installation ni droits administrateur, sans
Python sur le poste. Le choix zéro-dépendance rend l'exercice simple :

1. `python -m zipapp` → un `.pyz` unique (nécessite encore un interpréteur) ;
2. distribution Windows embarquable (`python-x.y.z-embed-amd64`) + le `.pyz`,
   lancé par un raccourci — aucune installation, aucune écriture registre ;
3. PyInstaller `--onedir` si un exécutable unique est exigé — à évaluer avec
   l'IT, un binaire non signé étant souvent plus suspect qu'un dossier de
   fichiers lisibles.

L'option 2 est recommandée : rien à compiler, contenu auditable par l'IT.

## 13. Interface graphique (V3)

Non implémentée. Le parcours cible (Importer → Vérifier → Paramétrer →
Analyser → Explorer → Restituer → Exporter) est déjà porté par la CLI et par la
restitution HTML. Une IHM ultérieure appellera `pipeline.run_analysis` sans
dupliquer la moindre règle. Tkinter (livré avec Python, sans dépendance) est le
candidat le plus cohérent avec les contraintes IT.
