# Dépendances : HR Analytics 1.0.0

*Relevé du 8 octobre 2026, révision `d4ec4c1`. Lu dans le paquet livré et
dans le code, jamais dans un fichier de déclaration.*

Ce document répond à une question de revue : **qu'est-ce qui entre dans ce
produit, et d'où cela vient-il ?** Il distingue trois niveaux, parce qu'ils
n'appellent pas la même vérification :

1. ce que **le code de l'outil** importe ;
2. ce que **l'interpréteur embarqué** apporte avec lui ;
3. ce que **les bibliothèques natives** de cet interpréteur contiennent.

---

## 1. Dépendances du code : aucune

**Aucune bibliothèque tierce.** Les 40 fichiers Python du paquet n'importent
que la bibliothèque standard, 32 modules, relevés dans l'arbre syntaxique :

```
__future__  argparse  base64  collections  copy  csv  dataclasses
datetime  functools  gc  hashlib  html  io  json  logging  math
operator  os  queue  re  secrets  stat  struct  sys  threading  time
tkinter  typing  unicodedata  xml  zipfile  zlib
```

Il n'existe dans le dépôt **ni `requirements.txt`, ni `setup.py`, ni
`pyproject.toml`, ni `Pipfile`, ni `poetry.lock`, ni `setup.cfg`.** Rien à
résoudre, donc rien à télécharger, donc **aucune chaîne d'approvisionnement
logicielle à surveiller** : pas de dépendance transitive, pas de CVE à suivre
sur un paquet tiers, pas de registre à atteindre pour construire.

Ce que cela coûte : les formats de sortie sont écrits à la main. Le PDF en
opérateurs graphiques (`io/pdf_writer.py`), le `.xlsx` en archive ZIP et XML
(`io/xlsx_writer.py`), le PNG en zlib (`ui/raster.py`). C'est plus de code à
tenir, et c'est le prix de la colonne de gauche.

---

## 2. L'interpréteur embarqué

| | |
|---|---|
| **Produit** | CPython 3.12.7, amd64 |
| **Origine** | composants officiels de python.org, repris **tels quels** |
| **Composants** | `core.msi`, `exe.msi`, `lib.msi`, `tcltk.msi`, `ucrt.msi` |
| **Licence** | PSF License Agreement (`runtime/LICENSE.txt`, livré) |
| **Empreintes** | SHA-256 de chaque fichier dans `docs/EMPREINTES-RUNTIME.txt` |

Aucun binaire n'est recompilé : le service informatique peut comparer chaque
fichier à ce que publie python.org, empreinte par empreinte. Ce qui est
retiré l'est **par suppression de fichiers**, jamais par modification.

Retiré de la bibliothèque standard : `test`, `idlelib`, `lib2to3`,
`ensurepip`, `turtledemo`, `distutils`, `site-packages`, `__pycache__`,
`pydoc_data`, plus la pile réseau et les capacités listées en
`DOSSIER-RSSI.md` §4 et §5.

Le paquet livré contient **60 binaires** : 40 façades `api-ms-win-*` de
l'Universal CRT de Microsoft, et 20 fichiers réels.

---

## 3. Bibliothèques natives embarquées

Ce sont les seuls morceaux de code tiers du produit. Toutes arrivent **par
CPython**, aucune n'a été ajoutée. Les versions sont lues dans les binaires
livrés.

| Bibliothèque | Version | Fichier livré | Rôle | Licence |
|---|---|---|---|---|
| **Tcl/Tk** | 8.6.13 | `tcl86t.dll`, `tk86t.dll`, `_tkinter.pyd` | la fenêtre, les tableaux, les graphiques | BSD-like (Tcl/Tk) |
| **OpenSSL (libcrypto seul)** | 3.0.15, 3 sept. 2024 | `libcrypto-3.dll`, `_hashlib.pyd` | SHA-256 : empreinte du fichier source, anonymisation des références | Apache 2.0 |
| **zlib** | 1.2.13 | `zlib1.dll` | lecture et écriture des archives `.xlsx`, compression des PNG | zlib |
| **libexpat** | 2.6.3 | `pyexpat.pyd` | lecture du XML d'un classeur | MIT |
| **bzip2** | 1.0.8, 13 juil. 2019 | `_bz2.pyd` | membres d'archive compressés en bzip2 | BSD-like |
| **liblzma** | fournie avec CPython | `_lzma.pyd` | membres d'archive compressés en LZMA | domaine public |
| **Universal CRT** | Windows | 40 × `api-ms-win-*.dll` | bibliothèque C de Microsoft | Microsoft |

**libmpdec n'est plus là.** Elle arrivait par `_decimal.pyd`, au motif qu'elle
portait les montants. La mesure du §4 a démenti : l'outil calcule en
flottants, et ce module n'était jamais chargé. Il a été retiré, avec
`_uuid.pyd` et `_zoneinfo.pyd`, jamais chargés non plus.

> **`libcrypto-3.dll` sera relevée par une revue, et c'est normal.** C'est la
> moitié **cryptographie** d'OpenSSL, dont `_hashlib` a besoin pour le
> SHA-256. **`libssl-3.dll`, la moitié TLS, est absente du paquet** : il n'y
> a pas de pile TLS, et donc rien pour ouvrir une connexion chiffrée.

Pas de `libffi` : `_ctypes` a été retiré, et sa bibliothèque avec lui. Pas de
`sqlite3.dll` : retirée également.

---

## 4. Ce qui est chargé pour de vrai

Mesuré en lançant **l'interpréteur livré** sur une analyse complète : lecture
du fichier, calculs, les sept documents, et l'import de la fenêtre. Huit
modules natifs sont chargés, et ce sont exactement les huit qui restent :

```
_bz2.pyd   _elementtree.pyd   _hashlib.pyd   _lzma.pyd
_queue.pyd   _tkinter.pyd   pyexpat.pyd   unicodedata.pyd
```

`_bz2` et `_lzma` surprennent : l'outil ne compresse rien en bzip2 ni en
LZMA. C'est `zipfile` qui les importe à son propre chargement, pour savoir
lire un membre d'archive qui emploierait ces méthodes. Ils sont donc des
dépendances réelles du paquet, pas du code métier. `_queue` sert à la
fenêtre, qui fait passer l'avancement du calcul d'un fil à l'autre par une
file.

**Trois modules natifs ont été retirés parce que la mesure les a trouvés
inertes** : `_decimal.pyd` (et avec lui libmpdec), `_uuid.pyd`,
`_zoneinfo.pyd`. Aucun module de l'outil n'importe `decimal`, `uuid` ni
`zoneinfo`.

Les modules Python qui les accompagnent restent : `decimal.py` et
`_pydecimal.py` parce que `statistics`, `fractions` et `_pylong` les
importent, ils continuent de fonctionner, en version Python pure et plus
lente ; `uuid.py` parce que `wave.py` l'importe. Le paquet reste cohérent :
vérifié en lançant l'interpréteur livré, qui importe encore `decimal`,
`statistics`, `fractions` et `uuid` sans erreur et produit les sept
documents.

> **Un effet de bord qui va dans le bon sens.** Sans `_uuid.pyd`, sans
> `ctypes` et sans `subprocess`, `uuid.getnode()` n'a plus aucun moyen de
> lire l'adresse matérielle de la carte réseau : il rend un nombre tiré au
> hasard. Constaté sur l'interpréteur livré : deux appels successifs rendent
> deux valeurs différentes, et le bit « multicast » qui marque un tirage au
> hasard est levé.

---

## 5. Dépendances de construction, et d'essai

**Pour construire le livrable Windows** : un compilateur C croisé
(`x86_64-w64-mingw32-gcc`) pour le lanceur, dont le source est livré
(`docs/lanceur.c`, 300 lignes lisibles), et les archives officielles de
python.org. Rien d'autre.

**Pour exécuter la suite de tests** : rien. Les 1 583 essais emploient
`unittest`, de la bibliothèque standard. Pas de `pytest`, pas de `tox`, pas
de `coverage` : donc pas d'environnement à reconstituer pour rejouer les
contrôles.

**Pour l'outillage du dépôt** (`tools/`) : rien non plus. L'analyseur de code
mort, l'inspecteur de PE et les générateurs de population d'essai sont écrits
sur la bibliothèque standard. Aucun de ces outils ne part avec le paquet, et
aucun classeur de démonstration non plus.

---

## 6. Résumé pour une revue

| Question | Réponse |
|---|---|
| Bibliothèques tierces dans le code | **0** |
| Fichier de dépendances | **aucun** |
| Dépendances transitives | **aucune** |
| Bibliothèques natives embarquées | **6**, toutes apportées par CPython |
| Dont pile TLS | **aucune** (`libssl` absente) |
| Dont accès base de données | **aucun** (`sqlite3` retirée) |
| Dont appel système générique | **aucun** (`libffi` / `_ctypes` retirés) |
| Origine des binaires | **python.org**, repris tels quels, empreintes fournies |
| Dépendances de construction | un compilateur C croisé |
| Dépendances d'essai | **aucune** |
