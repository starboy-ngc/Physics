# Audit de sécurité IT — HR Insight 1.0.0

*Conduit le 25 septembre 2026 sur la branche
`claude/compensation-analytics-local-8mbxy0`.*

Trois questions, et rien d'autre : **l'outil dépend-il de quelque chose
d'extérieur ? peut-il faire sortir des données ? peut-on lui faire faire
autre chose que son travail ?**

Méthode : rien n'est accordé au code sur la foi de ce qu'il déclare. Les
dépendances sont lues dans les imports, pas dans un fichier de
dépendances ; les interdits sont vérifiés par une sonde d'exécution
(PEP 578) qui voit chaque socket, chaque processus, chaque compilation de
chaîne, chaque écriture — l'interpréteur ne ment pas sur ce qu'on lui
demande.

---

## 1. Verdict

| Question | Réponse | Preuve |
|---|---|---|
| Dépendance externe ? | **aucune** | 31 modules, tous de la bibliothèque standard |
| Accès réseau ? | **aucun** | 0 événement socket/urllib/http sur le parcours complet |
| Processus, shell ? | **aucun** | 0 événement subprocess/exec/spawn/fork |
| Code dynamique ? | **aucun venant de l'outil** | 272 événements, tous de l'interpréteur |
| Registre, DLL, `ctypes` ? | **aucun** | 0 événement |
| Écritures hors dossier de sortie ? | **aucune** | 16 écritures, toutes confinées |
| Lectures hors périmètre ? | **aucune** | 106 lectures, 0 ailleurs, 0 dans le répertoire personnel |
| Documents rappelant l'extérieur ? | **aucun** | 0 lien distant, 0 script externe, 0 action PDF |
| Secret en dur ? | **aucun** | recherche sur 37 fichiers |

**Un défaut trouvé et corrigé** : les documents produits naissaient
lisibles par tout compte de la machine (§4.3).
**Un point d'attention majeur, par conception** : le classeur emporte
désormais le fichier RH entier (§4.1).

---

## 2. Dépendances — ce que le code appelle

Les 37 fichiers du paquet n'importent que la bibliothèque standard :

```
__future__ argparse base64 collections copy csv dataclasses datetime
functools gc hashlib html json logging math operator os queue re secrets
struct sys threading time tkinter typing unicodedata xml.etree zipfile zlib
```

**0 module hors bibliothèque standard.** Aucun `requirements.txt`, aucun
`setup.py`, aucun `pyproject.toml`, aucun verrou de dépendances : il n'y a
rien à résoudre, donc rien à télécharger, donc aucune chaîne
d'approvisionnement à homologuer.

L'archive livrée contient 66 entrées, dont un `.pyz` de 53 entrées qui ne
porte que `hr_insight/` et `config/`. Aucun `.exe`, `.dll`, `.so`, `.msi`.
Les deux `.bat` sont des lanceurs : ils cherchent l'interpréteur Python
installé et lancent le `.pyz`. Ils ne téléchargent rien, n'élèvent aucun
privilège, ne touchent pas au registre.

---

## 3. Ce que le processus fait réellement

Sonde PEP 578 sur le parcours complet — import, lecture du fichier,
analyse, classeur, restitution, slides, manifeste — puis le même parcours
**fenêtre ouverte**, tous les onglets parcourus et quatre postes dépliés.

| | moteur | interface |
|---|---|---|
| Réseau | **0** | **0** |
| Processus, shell | **0** | **0** |
| `ctypes`, registre, `pickle` | **0** | **0** |
| Import hors bibliothèque standard | **0** | **0** |
| Fichier temporaire | — | **0** |
| Écritures hors dossier de sortie | **0** | **0** |

### Le code dynamique, regardé de près

La sonde relève 272 événements `compile`/`exec`/`marshal.loads`. Une
alerte brute les compterait comme du code dynamique. La pile d'appel dit
d'où ils viennent :

| Origine | Nombre | Ce que c'est |
|---|---|---|
| **Code de l'outil** | **0** | — |
| Machinerie d'import | 147 | lecture du bytecode des modules |
| Bibliothèque standard | 125 | `typing` et `dataclasses` qui évaluent des annotations |

**Aucune chaîne venue du fichier RH n'est compilée ni exécutée.** C'est la
distinction qui compte : l'interpréteur compile le code de l'outil, comme
pour tout programme Python ; l'outil, lui, ne compile rien.

---

## 4. Sortie de données

### 4.1 Ce que chaque document emporte — le point d'attention

Mesuré sur une population de 600 salariés, en cherchant dans chaque
document les 600 noms, 600 prénoms, 600 matricules et 599 salaires
individuels du fichier :

| Document | Au réglage livré | Réglages coupés |
|---|---|---|
| `analyse.xlsx` | **600 noms · 600 prénoms · 600 matricules · 599 salaires** | aucune donnée nominative |
| `restitution.html` | aucune donnée individuelle | aucune |
| `slides.html` | aucune donnée individuelle | aucune |
| `synthese.html` | aucune donnée individuelle | aucune |
| `manifeste.json` | aucune donnée individuelle | aucune |

**Le classeur est une copie du fichier de paie.** C'est voulu — il existe
pour qu'une équipe C&B refasse chaque calcul, et une vérification sans les
valeurs n'en est pas une — mais c'est de loin la plus grande surface de
sortie de l'outil, et elle est active **par défaut**.

Ce que cela implique :

- Le classeur ne se transmet pas comme une restitution. Sa première page
  le dit en toutes lettres.
- Les trois autres documents, eux, peuvent circuler : ils ne portent
  aucune identité.
- Deux réglages rendent le classeur purement agrégé :
  `export_parameters.include_individual_data` et `include_source_file`.

**C'est une décision de gouvernance, pas un défaut technique.** Elle
mérite d'être reprise si le classeur doit sortir de l'équipe C&B.

### 4.2 Les documents rappellent-ils l'extérieur ?

La fuite la plus discrète n'est pas ce que l'outil envoie, c'est ce que le
*lecteur* appelle en ouvrant le document. Inspection de chaque fichier, et
de chaque pièce des archives :

| Recherche | Résultat |
|---|---|
| Référence `http(s)` hors espaces de noms OOXML | **0** |
| `src` ou feuille de style distante | **0** |
| `<iframe>`, `<embed>`, `<object>` | **0** |
| `@import` CSS | **0** |
| `/URI`, `/JavaScript`, `/OpenAction`, `/Launch` dans les PDF | **0** |
| Lien externe ou `externalLink` Excel | **0** |
| Entité XML externe | **0** |

Les 17 adresses trouvées dans le code sont **toutes** des espaces de noms
XML OOXML (`schemas.openxmlformats.org`) : des identifiants de format,
jamais déréférencés — la sonde le confirme, zéro accès réseau.

Un seul script figure dans les documents HTML : 18 lignes d'info-bulle,
inline. Il n'emploie ni `innerHTML`, ni `eval`, ni `fetch`, ni
`XMLHttpRequest`, ni stockage local — uniquement `textContent`, le puits
sûr.

### 4.3 Les documents étaient lisibles par tous — corrigé

**Défaut trouvé.** Créés au masque par défaut, les documents naissaient en
`-rw-r--r--`. Sans conséquence sur un poste personnel ; sur un serveur de
rebond, un bureau partagé ou un dossier synchronisé, le classeur — qui
porte 600 noms — était lisible par tout compte de la machine.

Les cinq écritures passent désormais par `restrict_to_owner()` :
`-rw-------`. Sous Windows, seul le bit de lecture seule répond à `chmod`
et la protection vient des droits NTFS du dossier : l'appel y est sans
effet plutôt que faux. Un échec ne coûte jamais le document.

→ `tests/test_documents_are_private.py` (4 tests), dont un qui énumère
tous les fichiers produits et échoue si l'un est lisible par un autre
compte.

### 4.4 Le journal technique

Sur une analyse complète de 600 salariés : **7 lignes** de journal, au
format `timestamp | module | action | statut | durée | compteurs`.
Recherche des 1 800 identités et des 599 montants individuels du fichier
dans tout ce que le journal a écrit : **aucun**.

### 4.5 L'anonymisation

| Contrôle | Résultat |
|---|---|
| Longueur d'une référence | 12 caractères |
| Collisions sur 2 000 identifiants | **0** |
| Sel tiré au hasard | oui, 32 caractères |
| Matricule lisible dans sa référence | **non** |
| Le sel change le résultat | oui |

---

## 5. Ce qu'on peut faire faire à l'outil

### 5.1 Injection depuis le fichier RH

Un intitulé de poste vient d'un SIRH ; personne ne le relit. Huit charges
introduites dans la colonne « Poste » d'un fichier de 60 salariés, puis
recherche de chacune dans tous les documents produits :

| Charge | Restitution HTML | Slides | Classeur |
|---|---|---|---|
| `<script>fetch(…)</script>` | échappée | échappée | texte |
| `"><img src=x onerror=…>` | échappée | échappée | texte |
| `<svg/onload=alert(1)>` | échappée | échappée | texte |
| `' onmouseover='alert(1)` | échappée | échappée | texte |
| `</td></tr><tr><td>` | échappée | échappée | texte |
| `=cmd\|'/c calc'!A1` | échappée | échappée | **cellule texte** |
| `@SUM(1+1)*cmd\|…` | échappée | échappée | **cellule texte** |
| Entité XML externe | échappée | échappée | texte |

**Aucun code actif ne ressort.** Les charges sont présentes — c'est
normal, ce sont des données — mais échappées : `&lt;script&gt;`.

Les charges de type formule (`=cmd|…`) sont écrites en `t="inlineStr"`,
c'est-à-dire en **cellule de texte**. Excel ne les exécute pas : une
formule vit dans un élément `<f>`, jamais dans une chaîne. Et l'outil
**n'exporte jamais de CSV** — format où un `=` en tête serait, lui,
interprété à l'ouverture. CSV n'est qu'un format d'entrée.

### 5.2 La porte d'entrée de Tk — refermée, revérifiée

Tk lit et *exécute* un `~/.Tk.py` à la création d'une fenêtre (CPython
issue 16248). Rejoué ici avec un faux répertoire personnel piégé : le
fichier n'est pas exécuté, `readprofile` reste neutralisée.

### 5.3 Analyse statique

Sur 37 fichiers du paquet et les outils annexes :

| Recherche | Résultat |
|---|---|
| `eval`, `exec`, `os.system`, `popen`, `spawn`, `fork` | **0** |
| `subprocess`, `socket`, `urllib`, `requests`, `ctypes`, `winreg` | **0** |
| `pickle`, `marshal`, `shelve` | **0** |
| `importlib`, `runpy`, `pty` | **0** |
| Introspection (`__globals__`, `__subclasses__`, `__code__`) | **0** |
| Secret, jeton, mot de passe en dur | **0** |

---

## 6. Ce que cet audit n'a pas couvert

- **Windows.** Tout a été mesuré sous Linux. Les permissions NTFS, le
  comportement des lanceurs `.bat` et le rendu de la fenêtre y restent non
  vérifiés.
- **Le compte privilégié.** Le banc tourne en `root` : un refus lié aux
  droits de fichier ne s'y manifeste pas.
- **L'interpréteur lui-même.** L'outil n'a aucune dépendance, mais il
  s'exécute sur le Python du poste — dont la version et l'intégrité sont
  du ressort de l'IT.
- **Le transport.** Ce que devient un document une fois produit — messagerie,
  partage réseau, clé USB — sort du périmètre de l'outil.

---

## 7. Recommandations

| Ordre | Point | Pourquoi |
|---|---|---|
| 1 | **Arbitrer la sortie nominative du classeur** (§4.1) | seule surface de sortie réelle, active par défaut |
| 2 | Vérifier les droits NTFS du dossier de sortie sous Windows | `chmod` n'y protège pas |
| 3 | Banc Windows | angle mort sur la cible réelle |
| 4 | Interpréteur embarqué | supprime la dépendance au Python du poste |
