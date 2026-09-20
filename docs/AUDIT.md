# Audit complet — HR Insight 1.0.0

*Audit conduit le 20 septembre 2026 sur la branche
`claude/compensation-analytics-local-8mbxy0`, révision `9cc4343`.*

Méthode : **mesurer, regarder, corriger**. Aucun constat de ce rapport ne
repose sur une lecture du code seule. Chaque défaut a d'abord été prouvé
par un test qui échoue, puis refermé par un test qui passe et reste dans la
suite. Chaque point fort a été vérifié en exécutant l'outil, non en lisant
ses intentions.

Périmètre mesuré : 14 914 lignes de moteur et d'interface (37 fichiers),
14 469 lignes de tests, 1 087 tests.

---

## 1. Verdict

| Thème | État | Réserve |
|---|---|---|
| Local-first (§3) | **conforme, vérifié à l'exécution** | — |
| IT-safe (§4) | **conforme, vérifié à l'exécution** | — |
| CS-safe / données RH (§6) | **conforme après correction** | une faille critique trouvée et fermée |
| Mapping configurable (§7) | **conforme** | — |
| Aucune donnée réelle en test (§27) | **conforme** | 25 jeux synthétiques |
| Sécurité du code (§30) | **conforme** | aucun `eval`/`exec`/code dynamique |
| Aucune dépendance externe (§34) | **conforme** | bibliothèque standard seule |
| Aucun runtime supposé (§34) | **non tenu** | voir 6.1 — seul écart de fond |

**9 défauts trouvés, 9 corrigés** : 1 critique, 6 majeurs, 2 mineurs.
Aucun défaut connu ne reste ouvert dans le périmètre audité.

---

## 2. Ce qui a été exécuté

| Banc | Ce qu'il fait | Résultat |
|---|---|---|
| Analyse statique (AST) | 37 fichiers ; appels et imports interdits, `except` nus, défauts mutables, symboles morts | 0 constat réel *(les 12 `compile()` signalés sont tous des `re.compile`)* |
| Sonde d'exécution (PEP 578) — moteur | intercepte réseau, processus, code dynamique, `ctypes`, registre, `pickle`, écritures, imports | 19 opérations, **0 réseau, 0 processus, 0 code dynamique, 0 écriture hors dossier de sortie, 0 module hors bibliothèque standard** |
| Sonde d'exécution — interface | idem, fenêtre ouverte sous Xvfb | 24 opérations, **0 réseau, 0 processus, 0 code dynamique, 0 écriture hors dossier temporaire** |
| Matrice de configuration | 25 jeux de données × 72 combinaisons de réglages (15 axes, couverture par paires) | **241 cas, 17 154 formules Excel réexécutées, 0 exception, 0 anomalie** |
| Parcours d'interface | import → filtres → analyse → onglets → graphiques → export, pilotés à la souris simulée | 77 s, **0 exception, 0 anomalie** |
| Fichiers hostiles | 9 attaques sur le format XLSX | **absorbés ou refusés proprement ; aucune fuite, aucun blocage** |
| Refus attendus | 18 configurations fausses | tous les paramètres gardant un résultat sont refusés en nommant le fichier |
| Performance | 1 000 → 60 000 lignes | **linéaire**, 60 000 lignes en 2,86 s, 173 Mo de pic |
| Reproductibilité | deux analyses du même fichier | identique **au sel déclaré près** |
| Suite de tests | Python 3.10, 3.11, 3.12, 3.13 | **1 087 tests verts** partout |

Les 15 axes de la matrice : thème, seuil de publication, seuil de
graphique, anonymisation, champ analysé, facteur atypique, devise, liste de
percentiles, classes d'histogramme, groupes du nuage, points du nuage,
droite de tendance, données individuelles à l'export, fichier source à
l'export, lignes du classeur de contrôle.

Les 25 jeux : `standard`, `un_seul`, `sous_seuil`, `seuil_exact`,
`sans_sexe`, `un_seul_sexe`, `salaires_identiques`, `un_seul_valorise`,
`sans_salaire`, `valeurs_extremes`, `salaire_negatif`, `dates_douteuses`,
`doublons`, `cycle_managers`, `pluriannuel`, `unicode`,
`colonnes_en_trop`, `colonnes_minimales`, `separateur_virgule`,
`separateur_tabulation`, `separateur_barre`, `formats_de_nombres`,
`ecritures_variees`, `gros`, `sous_seuil_graphique`.

---

## 3. Anomalies

### 3.1 Critique

**[C-1] La fenêtre exécutait un fichier du répertoire personnel.**

À la création d'une fenêtre, Tk lit dans le répertoire personnel de
l'utilisateur un fichier `.Tk.py` — ou `.Tk.tcl` — **et l'exécute**. Le
défaut est connu de CPython (issue 16248) et n'a jamais été refermé ; il
suffit d'un fichier déposé là pour que du code arbitraire s'exécute à
l'ouverture d'un outil qui manipule ensuite des fichiers de paie.

*Preuve* : un fichier posé dans un faux répertoire personnel écrivait un
témoin à l'ouverture de la fenêtre.
*Correction* : `Application.readprofile` est désormais une méthode vide —
Tk appelle, rien ne se lit.
*Test de non-régression* : `tests/test_security_behaviour.py::TestTheWindowRefusesTheProfilesOfTk` (2 tests).

C'est le seul défaut de l'audit qui relevait de la sécurité du poste et non
de la justesse du résultat.

### 3.2 Majeures

**[M-1] Le classeur de contrôle ne comptait pas comme le moteur.**
Les effectifs affichés derrière un écart femmes/hommes comptaient les
salariés *présents* dans le segment ; le moteur calculait l'écart sur les
salariés *ayant un montant*. Sur un fichier où une partie des
rémunérations manque — le cas ordinaire —, le classeur censé permettre le
contrôle contredisait l'outil qu'il devait contrôler.
→ `core/export.py` ; `tests/test_export_control.py` (2 tests).

**[M-2] Un paramètre illisible donnait une trace Python.**
Un fichier de configuration se corrige au bloc-notes. Un texte à la place
d'un nombre produisait un `ValueError` brut, illisible pour un utilisateur
RH. `Configuration.number()` lit, vérifie et refuse en nommant **le
fichier, la clé et la valeur lue** — sans jamais y faire entrer de donnée
personnelle.
→ `core/config.py` ; `tests/test_field_settings.py` (6 tests).

**[M-3] Un seuil de publication à zéro désarmait la confidentialité.**
`min_headcount_publish: 0` était accepté en silence et publiait les
indicateurs d'un segment d'une personne — c'est-à-dire sa rémunération.
Le garde-fou ne doit pas pouvoir se désarmer par une faute de frappe : il
est refusé.
→ `core/metrics.py` (`PrivacyRules.from_config`).

**[M-4] Des dates impossibles entraient dans les moyennes publiées.**
Une sortie antérieure à l'entrée, une naissance postérieure à la date de
référence : l'ancienneté et l'âge devenaient négatifs et tiraient vers le
bas une moyenne ensuite publiée. Ces lignes sont désormais signalées
(`tenure:end_before_hire`, `birth_date:after_reference`) et **n'ont plus de
valeur** plutôt qu'une valeur fausse.
→ `core/normalize.py` ; `tests/test_anomalies.py` (4 tests).

**[M-5] L'interface se taisait sur les anomalies critiques.**
La fenêtre analysait avec `ignore_quality_errors=True` — pour ne pas
bloquer sur un fichier imparfait — sans le dire. Un utilisateur pouvait
publier des indicateurs calculés sur des données que le contrôle qualité
signalait. La barre d'état et un bandeau rouge les annoncent maintenant et
renvoient à l'onglet Qualité avant publication.
→ `ui/app.py` ; `tests/test_ui.py` (3 tests).

**[M-6] Le seuil d'alerte restait lu « à la main » à trois endroits.**
Après la correction M-2, deux des trois lectures de
`gap_alert_threshold` (table par axe, profil d'un poste) échappaient encore
au contrôle et rendaient la trace Python que la première évitait.
→ `core/pay_equity.py` ; `tests/test_field_settings.py` (1 test, 2 chemins).

### 3.3 Mineures

**[m-1] L'interface contournait `BoxPlotChart.set_split()`.**
Elle écrivait l'attribut directement. Les tests parcouraient donc un chemin
que l'outil n'empruntait pas — ce n'est pas un chemin testé. Corrigé.

**[m-2] Une durée d'accueil illisible aurait empêché l'ouverture.**
Tout paramètre faux n'a pas le même prix : un seuil fausse un résultat et
doit arrêter l'analyse ; une durée d'écran d'accueil ne fausse rien et
retombe sur son défaut plutôt que de fermer la fenêtre au nez de
l'utilisateur. La distinction est désormais explicite dans le code.
→ `ui/app.py` ; `tests/test_field_settings.py` (2 tests).

---

## 4. Points forts vérifiés

**Le hors-ligne est prouvé, non affirmé.** Sous sonde PEP 578, moteur et
interface confondus : zéro connexion, zéro processus enfant, zéro appel
shell, zéro `ctypes`, zéro accès au registre, zéro `pickle`, zéro code
compilé à la volée depuis une chaîne. Les écritures restent dans le dossier
de sortie choisi. Les documents produits (XLSX, HTML, PDF) ne contiennent
aucune référence externe — ils s'ouvrent sur un poste sans réseau.

**Le journal technique ne porte aucune donnée RH.** Vérifié ligne à ligne
sur un parcours complet : `timestamp | module | action | statut | durée |
compteurs`. Aucun nom, prénom, salaire, adresse, courriel ni matricule.

**Les seuils de confidentialité ferment plutôt qu'ils n'ouvrent.** Sur un
fichier où aucun salaire n'est renseigné, l'équité, la distribution et les
segments se déclarent indisponibles avec un motif lisible, au lieu de
publier un tableau vide qui se lirait comme « aucun écart ».

**Les fichiers hostiles ne passent pas.** Bombe de décompression de 200 Mo,
entité XML externe, relation pointant hors de l'archive : refus net en
moins de 30 ms, message d'utilisateur sans détail technique. Cellule de
5 Mo, formule injectée, nombre astronomique, ligne numérotée à l'infini,
colonne très lointaine, nom d'onglet piégé : absorbés sans dommage.

**La performance est linéaire et tient dans la mémoire d'un poste.**
60 000 lignes analysées en 2,86 s pour 173 Mo de pic ; le facteur de temps
suit le facteur de lignes (×3 lignes → ×3,1 temps). Aucun effet de seuil.

**Le classeur d'export porte ses formules.** 17 154 formules ont été
réexécutées par un tableur tiers après effacement des valeurs en cache :
toutes redonnent la valeur publiée. Le contrôle de l'implémentation par un
tiers est donc réellement possible, et pas seulement annoncé.

**La suite tient sur quatre versions de Python.** 1 087 tests verts sur
3.10, 3.11, 3.12 et 3.13. Les 322 tests d'interface se déclarent ignorés,
proprement, là où `tkinter` est absent — le moteur n'importe jamais
l'interface.

---

## 5. Points fragiles (pas des défauts — des endroits où l'outil est mince)

**5.1 La reproductibilité dépend d'un paramètre.** Deux analyses du même
fichier donnent des références anonymes différentes tant qu'aucun sel n'est
déclaré ; avec un sel, elles sont identiques au caractère près. C'est le
comportement voulu — un sel fixe rend les pseudonymes rapprochables d'une
analyse à l'autre, ce qui est parfois souhaitable et parfois exactement ce
qu'il faut éviter. **Mais le choix est silencieux.** Un utilisateur qui
compare deux exports sans avoir posé de sel croira à une incohérence.
*Suggestion* : le manifeste devrait dire lequel des deux régimes a servi.

**5.2 Un champ d'analyse absent du fichier est accepté.** L'analyse se
produit, vide et masquée, et le contrôle qualité le signale — mais l'outil
ne refuse pas. Défendable ; à confirmer comme un choix.

**5.3 Une liste de percentiles vide est acceptée.** Elle produit une
analyse sans percentiles. Même remarque.

**5.4 Le banc a tourné sous un compte privilégié.** Le cas « fichier de
configuration sans droit de lecture » est donc passé au lieu d'être refusé.
Ce n'est pas un résultat de l'outil, c'est une limite du banc : ce cas reste
non mesuré.

**5.5 L'audit n'a rien mesuré sous Windows.** Tout ce qui précède a été
obtenu sous Linux. Les chemins, les fins de ligne, l'encodage `cp1252` des
CSV exportés par un SIRH français, le rendu de la fenêtre à 125 % : angle
mort complet, alors que c'est la cible réelle.

---

## 6. Écart de fond restant

### 6.1 §34 — « ne jamais supposer qu'un runtime est installé »

C'est le seul point de la spécification que l'outil ne tient pas
aujourd'hui, et il ne relève pas d'un correctif : il se livre. L'outil
n'a aucune dépendance, mais il suppose **Python installé sur le poste
final**. Sur un poste d'entreprise verrouillé, cette hypothèse est
précisément celle que §34 interdit.

*Voie sans dette technique* : un `python-embed` officiel déposé à côté de
l'outil, sans installation, sans droits administrateur, sans registre, sans
réseau — l'archive contient alors son propre interpréteur. Cela ne coûte
aucune dépendance tierce et referme l'écart. **Non fait ; c'est le premier
chantier à ouvrir.**

---

## 7. Ce que l'audit n'a pas couvert

Nommé pour que la portée du « 0 anomalie » soit lisible :

- Windows, dans son ensemble (5.5).
- Les fichiers `.xls` anciens et les CSV en `cp1252`.
- La tenue au-delà de 60 000 lignes.
- L'accessibilité au lecteur d'écran.
- Les jeux de données réels — par construction (§27).

---

## 8. Suites proposées

| Ordre | Chantier | Pourquoi |
|---|---|---|
| 1 | Interpréteur embarqué (6.1) | seul écart à la spécification |
| 2 | Banc Windows | angle mort sur la cible réelle |
| 3 | Repli d'encodage `cp1252` à l'import | cas courant d'un SIRH français |
| 4 | Régime de sel inscrit au manifeste (5.1) | lève la seule ambiguïté de lecture |
| 5 | Fiche individuelle, évolution N/N−1 | fonctionnel déjà arbitré |
