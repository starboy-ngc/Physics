# HR Analytics : dossier pour le RSSI

**Version 1.0.0 · commit `981ea10` · 9 octobre 2026**

Ce document est destiné à une revue de sécurité. Il décrit ce que le logiciel
est, ce qu'il fait, ce qu'il ne peut pas faire, et **comment le vérifier
sans nous croire sur parole**. Chaque affirmation est suivie du moyen de la
contrôler sur le livrable lui-même.

---

## 1. En une page

| | |
|---|---|
| **Nature** | Application de bureau, poste de travail Windows. Analyse de rémunération à partir d'un fichier RH (.xlsx, .xlsm, .csv) |
| **Exécution** | Locale, hors ligne. Aucun serveur, aucun service, aucun compte |
| **Installation** | Aucune. Décompression d'un dossier, ou un fichier .exe autonome. Aucun droit administrateur |
| **Registre Windows** | Aucune écriture, aucune lecture par l'outil (§5.1) |
| **Réseau** | Aucun. La pile réseau est **absente** de l'interpréteur livré |
| **Dépendances tierces** | Aucune. Bibliothèque standard Python uniquement |
| **Données** | Restent sur le poste. Rien n'est transmis, mis en cache ailleurs, ni envoyé |
| **Taille** | 23 880 lignes de Python, 40 fichiers, 51 suites de tests (25 810 lignes) |
| **Interpréteur** | CPython 3.12.7 (amd64), repris tel quel de python.org, puis allégé |
| **Signature** | Le livrable fourni n'est **pas** signé (voir §9) |

---

## 2. Ce que le logiciel fait

L'utilisateur choisit un fichier de population RH. L'outil le lit, en contrôle
la qualité, calcule des indicateurs (effectifs, âges, anciennetés, médianes et
percentiles de rémunération, dispersion, écarts femmes/hommes), les affiche, et
produit des documents : un rapport HTML, une synthèse d'une page (HTML + PDF),
une vue détaillée (HTML + PDF) et un classeur Excel.

Tout se passe dans la mémoire du processus et dans deux dossiers : celui de la
configuration et celui que l'utilisateur désigne pour les documents.

---

## 3. Dépendances : il n'y en a pas

**L'affirmation.** Le code n'importe aucune bibliothèque hors de la
bibliothèque standard de Python. Pas de `pip`, pas de `requirements.txt`, rien
à télécharger, aucune chaîne d'approvisionnement logicielle à surveiller.

**Les 34 modules standard employés**, et rien d'autre (relevé du
9 octobre 2026 par analyse syntaxique des 40 fichiers) :

```
__future__  argparse  base64  collections  copy  csv  dataclasses  datetime
functools   gc        hashlib html  io  json  logging  math  operator  os
queue  re  secrets  stat  struct  sys  threading  time  tkinter  tkinter.font
traceback   typing    unicodedata  xml.etree  zipfile  zlib
```

**La subtilité qui mérite d'être comprise.** Les formats produits ne viennent
d'aucune bibliothèque : le PDF est écrit directement en opérateurs graphiques
PostScript (`io/pdf_writer.py`), le .xlsx en archive ZIP et XML
(`io/xlsx_writer.py`), le PNG en zlib (`ui/raster.py`). C'est plus de code à
écrire, mais c'est **la raison pour laquelle il n'y a rien à auditer en
dehors de ce dépôt** : pas de ReportLab, pas d'openpyxl, pas de Pillow, pas de
pandas, donc aucune CVE tierce à suivre, aucune mise à jour transitive à
appliquer dans l'urgence.

**Comment le vérifier.** Un test de la suite (`tests/test_security.py::
test_no_third_party_dependency`) parcourt l'arbre syntaxique de chaque fichier
et échoue si un import ne se résout pas dans la bibliothèque standard. Il
tourne à chaque exécution de la suite. Indépendamment :

```
python3 - <<'EOF'
import ast, os, sys
std = set(sys.stdlib_module_names)
for d, _s, fs in os.walk("hr_analytics"):
    for f in (n for n in fs if n.endswith(".py")):
        for x in ast.walk(ast.parse(open(os.path.join(d, f)).read())):
            noms = ([a.name for a in x.names] if isinstance(x, ast.Import)
                    else [x.module] if isinstance(x, ast.ImportFrom)
                    and not x.level and x.module else [])
            for n in noms:
                if n.split(".")[0] not in std:
                    print("TIERS :", f, n)
EOF
```

---

## 4. Réseau : la capacité est absente, pas seulement inutilisée

C'est le point le plus important du dossier, et il demande qu'on distingue
deux affirmations de force très différentes.

**« Le code n'ouvre pas de connexion »** est une propriété du code
d'aujourd'hui. Elle se vérifie par lecture, et la lecture est à refaire à
chaque version.

**« Le code ne peut pas ouvrir de connexion »** est une propriété du
livrable. Elle se constate en listant un dossier, et elle tient quoi qu'on
écrive ensuite.

Nous fournissons la seconde. L'interpréteur Python livré est amputé de sa pile
réseau :

| Retiré | Effet |
|---|---|
| `_socket.pyd` | **La pièce qui décide.** Sans elle, aucun code Python ne peut ouvrir de connexion, quelle que soit la bibliothèque qui le demanderait |
| `_ssl.pyd`, `libssl-3.dll` | Plus de TLS |
| `select.pyd`, `_asyncio.pyd`, `_overlapped.pyd` | Plus de boucle d'événements réseau |
| `socket.py`, `ssl.py`, `selectors.py`, `socketserver.py` | |
| `ftplib`, `smtplib`, `poplib`, `imaplib`, `telnetlib`, `nntplib` | |
| `http/`, `email/`, `xmlrpc/`, `asyncio/`, `wsgiref/` | |
| `urllib/request.py`, `error.py`, `response.py`, `robotparser.py` | |
| `webbrowser.py`, `cgi.py`, `cgitb.py` | |

**Volontairement gardés**, et pourquoi : `libcrypto-3.dll` et `_hashlib.pyd`
servent aux empreintes SHA-256 et à l'anonymisation, ni l'un ni l'autre
n'ouvre quoi que ce soit ; `urllib/parse.py`, que `pathlib` importe pour
écrire un chemin sous forme d'URL, est un analyseur de chaînes sans aucune
fonction d'accès.

**Comment le vérifier**, sur le livrable, en trois secondes :

```
dir "HR Analytics\runtime\DLLs\_socket.pyd"     → introuvable
"HR Analytics\runtime\python.exe" -I -c "import socket"
                                                → ModuleNotFoundError
```

Constaté sur le livrable de cette version, interpréteur embarqué, sous
Windows :

```
absent  : socket       -> No module named 'socket'
absent  : ssl          -> No module named 'ssl'
```

---

## 5. Processus, appel système, base locale : également absents

Le même raisonnement est appliqué aux autres capacités que l'outil n'utilise
jamais. Elles sont retirées de l'interpréteur livré :

| Retiré | Ce que cela interdit |
|---|---|
| `_ctypes.pyd`, `ctypes/`, `libffi-8.dll` | **La pièce qui décide pour l'appel système.** Sans elle, aucun code Python ne peut appeler une fonction de Windows qui ne lui soit pas déjà exposée |
| `subprocess.py`, `_multiprocessing.pyd`, `multiprocessing/`, `concurrent/` | Les bibliothèques de lancement de processus. **Attention : cela ne retire pas la capacité, voir §5.1** |
| `_sqlite3.pyd`, `sqlite3/`, `sqlite3.dll` | Aucune base locale |
| `_wmi.pyd` | Aucune interrogation WMI du poste |
| `_msi.pyd` | Aucun accès à l'API d'installation |
| `winsound.pyd` | |
| `pdb.py`, `bdb.py`, `pydoc.py`, `idlelib/`, `lib2to3/`, `ensurepip/`, `venv/`, `distutils/` | Débogueur et outillage de développement |

**Gardés**, et pourquoi : `pyexpat.pyd` et `_elementtree.pyd` lisent le XML
d'un .xlsx ; `_hashlib.pyd` calcule les SHA-256 ; `_decimal.pyd` porte les
montants ; `_tkinter.pyd` est la fenêtre ; `_bz2.pyd` et `_lzma.pyd` sont
importés par `zipfile` à son chargement.

**La garde qui empêche ce retrait de casser l'outil.** Un test
(`tests/test_packaging.py::test_nothing_the_tool_imports_is_on_a_removal_list`)
relève par analyse syntaxique **ce que le code importe réellement** et le
confronte aux deux listes de retrait. Aucune pièce retirée ne peut être une
pièce dont l'outil a besoin, et un import ajouté demain qui toucherait à l'une
d'elles ferait échouer la suite.

### 5.1 Ce que ce retrait ne fait PAS : correction d'une affirmation

**Cet audit a invalidé une affirmation que nous avions écrite.** Nous avions
dit que le retrait de `subprocess` et de `_multiprocessing.pyd` rendait le
lancement d'un programme impossible. **C'est faux, et le contrôle le montre en
trente secondes :**

```
_winapi expose : ['CreateProcess', 'CreateFile', 'CreateNamedPipe',
                  'OpenProcess', 'VirtualQuerySize', 'CreateJunction']
os.system  : True      os.popen   : True
os.startfile : True    os.spawnv  : True
winreg     : lecture du registre POSSIBLE
CreateProcess : A LANCE UN PROCESSUS
```

`os.system`, `os.popen`, `os.spawnv`, `os.startfile`, `_winapi.CreateProcess`,
`winreg`, `mmap` et `pickle` sont **compilés dans `python312.dll`**. Supprimer
des fichiers `.py` et `.pyd` ne les atteint pas. Nous l'avons vérifié en
lançant réellement un processus depuis l'interpréteur livré.

**Pourquoi nous ne les retirons pas.** Il faudrait recompiler CPython, donc
renoncer à livrer les binaires de python.org tels quels, et donc renoncer à
la vérification par empreinte (§9.3). Entre une capacité de moins et une
provenance contrôlable, nous choisissons la provenance : elle se vérifie,
l'autre se croirait sur parole.

**Ce que le retrait apporte réellement**, et qui n'est pas rien :

- `_ctypes` est parti, et c'est **la** pièce qui compte : sans elle, aucun code
  Python ne peut appeler une fonction arbitraire de Windows. C'est la
  différence entre « les quelques appels que Python expose » et « toute
  l'API Win32 ».
- Les chemins **confortables** sont fermés : il n'y a plus de bibliothèque
  haut niveau, plus de base locale, plus de WMI.
- Surtout, **aucun de ces appels n'est fait par l'outil**, ce qui est prouvé
  statiquement (analyse syntaxique) et dynamiquement (exécution complète avec
  ces appels instrumentés : 0 tentative, §6).

### 5.2 Le réseau, lui, est bel et bien fermé

La différence est structurelle, et elle mérite d'être comprise : la pile
réseau vit dans **`_socket.pyd`, un fichier séparé**, et **aucune primitive de
socket n'est compilée dans `python312.dll`**. Vérifié sur le livrable :

```
socket, _socket, ssl, _ssl, asyncio, http, urllib.request : tous absents
os.*     contenant « sock » : aucun
_winapi.* réseau            : aucun (ConnectNamedPipe est du tube local)
ctypes                      : absent, aucun appel direct à ws2_32
```

Sans `_socket` et sans `ctypes` pour appeler `ws2_32` directement, **il
n'existe aucun chemin vers le réseau depuis Python**. C'est l'affirmation
forte du dossier, et c'est la seule que nous formulons ainsi.

**Vérifié sur le livrable**, pas seulement sur la liste. Sous Windows, avec
l'interpréteur livré :

```
absent  : ctypes          -> No module named 'ctypes'
absent  : subprocess      -> No module named 'subprocess'
absent  : multiprocessing -> No module named 'multiprocessing'
absent  : sqlite3         -> No module named 'sqlite3'
```

et, dans la même session, l'outil lit un fichier de 400 salariés, produit ses
sept documents, et ouvre sa fenêtre.

---

## 6. Aucune commande shell, aucun outil externe

**L'affirmation.** Le code n'appelle jamais le shell, ne lance aucun
processus, ne cherche aucun exécutable sur le poste, n'exécute aucun code
construit à l'exécution.

**Contrôle statique.** Un scan de l'arbre syntaxique des 40 fichiers livrés
cherche `eval`, `exec`, `compile`, `__import__`, `os.system`, `os.popen`,
`os.spawn*`, `os.exec*`, `os.startfile`, `subprocess.*` :

> 13 occurrences de `compile`, **toutes `re.compile`** (expressions
> régulières), vérifiées une par une. Aucune autre.

Aucun `eval`, aucun `exec`, aucun `__import__` dynamique, aucun `pickle`,
aucun `marshal` : donc aucune désérialisation de code.

**Contrôle dynamique.** Une analyse complète (lecture du fichier, calculs,
six documents produits) a été exécutée avec `os.system`, `os.popen`,
`subprocess.Popen`, `subprocess.run`, `socket.connect`, `connect_ex`,
`create_connection`, `getaddrinfo` et `gethostbyname` tous interceptés et
instrumentés :

> **0 tentative.**

C'est la différence entre « je ne trouve pas d'appel en lisant » et « rien
n'a appelé en tournant ». Les deux ont été faits.

**Le seul endroit où `subprocess` apparaît dans le dépôt** est
`tools/build_windows.py`, l'outil de fabrication du paquet, qui invoque le
compilateur croisé. Il ne fait pas partie du livrable : un test
(`test_the_build_script_never_ships`) refuse qu'il y entre.

---

## 7. Le traitement des fichiers reçus

Un fichier de population arrive souvent par courriel. C'est la seule entrée
non maîtrisée du logiciel, donc la seule surface d'attaque réelle. Trois
pièges connus du format .xlsx sont écartés **avant** toute analyse.

### 7.1 Bombe à entités (« billion laughs »)

Dix entités XML s'appelant l'une l'autre sur neuf niveaux transforment deux
kilo-octets en dix gigaoctets à l'expansion ; le processus meurt avant d'avoir
pu dire quoi que ce soit.

La parade est de refuser la **déclaration de type de document** elle-même. Un
.xlsx n'en porte jamais : la spécification OOXML ne l'autorise pas, et aucun
tableur n'en écrit. Dans un fichier reçu, c'en est un signe suffisant.

> **Subtilité à connaître.** libexpat se défend seule depuis sa version 2.6, et
> la version livrée en bénéficie. Mais cette défense appartient à la
> bibliothèque, pas à l'outil : elle ne voyagerait pas avec le code sur un
> poste resté sur une version antérieure. Refuser la déclaration est la seule
> protection qui tienne quelle que soit la bibliothèque trouvée.

**Cet audit a trouvé un trou ici, et il a été corrigé** (commit `1fa81dc`). La
garde s'appliquait au classeur et à la table des chaînes partagées, mais pas à
**l'onglet** : le seul morceau lu en flux, et justement celui qu'un fichier
reçu contrôle vraiment. Une bombe posée dans l'onglet passait la garde et
n'était arrêtée que par libexpat. L'onglet est désormais vérifié lui aussi,
sans cesser d'être lu en flux : seize kilo-octets de prologue sont relus, une
déclaration de type précède obligatoirement l'élément racine, puis un flux
qui reprend où il en était est rendu à l'analyseur. Un onglet de 60 000 lignes
se lit toujours sans que la mémoire du processus bouge.

### 7.2 Entité externe (XXE)

`<!ENTITY secret SYSTEM "file:///etc/passwd">` dans une cellule ferait lire le
poste par le classeur et recopier le résultat dans l'analyse. Même parade,
même garde, et une vérification qui l'exerce vraiment.

### 7.3 Bombe ZIP

Un demi-giga-octet dans un onglet pour quelques kilo-octets sur le disque. La
taille annoncée dans l'en-tête est vérifiée d'abord, c'est elle qui évite de
lire quoi que ce soit, puis la lecture elle-même est bornée, parce qu'un
en-tête peut mentir. Plafond par défaut : 512 Mo décompressés.

### 7.4 Traversée de chemin

Un membre d'archive nommé `../../../../tmp/evade.txt` est inerte : le lecteur
**n'extrait rien**, il lit les morceaux qu'il nomme. Vérifié : le classeur se
lit normalement et aucun fichier n'apparaît hors du dossier.

### 7.5 Injection de formule dans le classeur produit

Une cellule du fichier source contenant `=cmd|'/c calc'!A1` serait, recopiée
telle quelle dans le classeur d'analyse, exécutée par Excel à l'ouverture chez
le destinataire. L'outil écrit ces valeurs **en texte**, jamais en formule.
Les seules formules du classeur produit sont celles que l'outil écrit
lui-même, pour que les chiffres soient recalculables.

### 7.6 État de ces défenses

Les cinq sont couvertes par des tests qui construisent les fichiers hostiles
et les soumettent vraiment à l'outil.

> **Subtilité méthodologique, qui vaut pour toute revue de ce type.** Une
> première version de ces essais fabriquait les classeurs de toutes pièces.
> Ils étaient mal formés *ailleurs* (un attribut de namespace manquant), donc
> l'analyseur les refusait pour cette raison-là, et les essais passaient au
> vert **sans jamais atteindre la garde qu'ils prétendaient vérifier**. Les
> essais partent maintenant d'un classeur valide produit par l'outil, dont un
> seul morceau est remplacé : ce qui échoue ensuite ne peut venir que de ce
> morceau. Un test témoin vérifie d'abord que le classeur sain se lit, faute de
> quoi les autres prouveraient seulement que l'outil refuse tout.

---

## 8. Données personnelles

### 8.1 Où elles vont

| Sortie | Contient des identités ? |
|---|---|
| Rapport HTML | **Non** : mesuré |
| Synthèse HTML / PDF | **Non** : mesuré |
| Vue détaillée HTML / PDF | **Non** : mesuré |
| Journal technique | **Non** : mesuré |
| Messages d'erreur techniques | **Non** : par construction (§8.2) |
| Classeur Excel | **Oui, par conception** : c'est l'onglet de matière première, ce pour quoi il existe |

**Mesure.** Les 597 identités présentes dans un fichier d'essai (noms,
prénoms, matricules) ont été cherchées, en mots entiers, dans chaque sortie :
**aucune fuite hors du classeur**.

> **Subtilité de méthode.** Une première mesure, par sous-chaîne, signalait une
> fuite du prénom « Anne » dans le rapport. C'était « Anne**xe** », le nom de la
> dimension de classification. Une recherche par sous-chaîne produit des faux
> positifs qui discréditent le contrôle ; la mesure a été refaite sur mots
> entiers.

### 8.2 Les messages d'erreur

Chaque erreur porte deux textes : un message pour l'utilisateur, et un détail
technique pour le journal. Le détail technique ne contient **jamais** de
valeur issue du fichier : il nomme le champ, le code, la ligne, jamais le
contenu. Les constats de qualité désignent les lignes par leur numéro
(« ligne 73 »), pas par le salarié.

### 8.3 Seuils de confidentialité

Trois seuils, paramétrables, et nommés par ce qu'ils décident :

| Réglage | Défaut | Effet |
|---|---|---|
| Ne rien calculer en dessous de | 5 | Aucun chiffre publié pour un groupe plus petit |
| Avertir sur l'interprétation en dessous de | 10 | Les chiffres restent publiés, avec une mise en garde |
| Ne pas tracer de graphique en dessous de | 10 | Histogramme, nuage et boîte à moustaches retirés |

> **Subtilité à expliquer en comité.** Le troisième seuil existe séparément
> parce que ces trois graphiques **placent une marque par salarié** : sur un
> nuage de huit points, celui en haut à droite est identifiable par quiconque
> connaît l'équipe. Un tableau d'agrégats ne désigne personne, même sur huit.
> Par ailleurs, une comparaison femmes/hommes exige le seuil de publication
> **de chaque côté** : avec 5, il faut 5 femmes *et* 5 hommes, donc au moins
> 10 personnes, et un groupe de 8 reste sans écart publié.

Une section masquée **dit pourquoi elle l'est**, à l'écran comme dans les
documents : une section qui disparaît sans un mot laisse un lecteur incapable
de savoir s'il manque un chiffre ou s'il n'y en avait pas.

### 8.4 Anonymisation

Les identifiants peuvent être remplacés par une référence stable. Le sel
d'anonymisation est un paramètre de configuration ; il est **retiré** de tout
ce qui est publié et remplacé par « (non publié) ». Le fichier de
configuration qui le porte ne doit pas être transmis avec les documents : le
guide utilisateur le dit à l'endroit où le réglage se fait.

### 8.5 Droits des fichiers produits

Un classeur d'analyse porte la population. Créé au masque par défaut, il
naîtrait lisible par tout compte de la machine : sans conséquence sur un poste
personnel, mais un serveur de rebond, un bureau partagé ou un dossier
synchronisé en feraient une copie du fichier de paie accessible à qui passe.
Chaque document produit est donc restreint à son propriétaire après écriture.

> **Subtilité Windows.** Sous Windows, seul le bit « lecture seule » répond à
> `chmod` ; la protection y vient des droits NTFS du dossier. L'appel y est
> sans effet plutôt que faux, et son échec n'interrompt jamais la production
> du document. **À dire explicitement au RSSI :** sur Windows, la protection
> des documents produits repose sur les droits NTFS du dossier de destination,
> pas sur le logiciel. Si les documents sont écrits dans un partage, ce sont
> les ACL du partage qui décident.

### 8.6 Ce qu'un nom de colonne peut atteindre

Le fichier reçu décide de deux choses dans le modèle de données : la valeur
d'un champ, et, si l'utilisateur déclare une colonne comme nouveau champ
depuis la page Paramètres, le **nom** de ce champ.

Ce nom n'atteint que les champs déclarés par le modèle. Tout le reste part
dans un dictionnaire de débordement, où l'outil sait le lire. Une colonne
nommée « Value », « Assign » ou « Identity » ne peut donc rien remplacer :
elle est rangée à côté du modèle, jamais dessus.

> **Ce n'était pas le cas, et l'audit du 8 octobre 2026 l'a trouvé.** Le
> contrôle portait sur `hasattr`, vrai pour tout ce que l'objet porte : y
> compris ses propres méthodes. Une colonne « Value » remplaçait la méthode
> `value()`, et l'analyse tombait quelques lignes plus loin sur
> « 'str' object is not callable », sans que rien ne désigne la colonne.
>
> Rien n'était exécuté : le modèle n'appelle jamais ce qu'il reçoit, et une
> chaîne posée à la place d'une méthode ne fait qu'échouer à l'appel suivant.
> C'était un défaut de robustesse, pas une faille. Il est corrigé des deux
> côtés : le modèle n'écrit que dans ses champs déclarés, et la page
> Paramètres refuse un nom que l'outil emploie déjà.

Depuis l'audit du 9 octobre 2026, deux règles de plus. Le modèle ne porte
plus aucun champ d'organisation (BU, établissement, métier, poste, statut) :
tout ce que l'utilisateur déclare vit dans le dictionnaire de débordement,
et un nom de colonne ne peut donc atteindre que les champs avec lesquels
l'outil calcule. Et les quatre noms internes du modèle (`row_number`,
`issues`, `anonymous_id`, `extra`) sont refusés au chargement du
paramétrage, avec un message qui les nomme : un fichier écrit à la main ne
peut plus y écrire. Un nom de colonne ne rejoint par ailleurs un champ que
par une orthographe écrite dans sa liste, jamais par son nom technique.

---

## 9. Le livrable Windows

### 9.1 Deux formes

- **Le dossier** (`HR-Analytics-1.0.0-windows.zip`, 13,5 Mo) : tout est sur
  le disque, lisible, à côté du lanceur. Rien n'est caché.
- **Le fichier unique** (`HR Analytics.exe`, 13,4 Mo) : le même dossier replié
  dans une archive CAB accolée au lanceur.

### 9.2 Ce que le lanceur fait, et ce qu'il ne fait pas

Le lanceur est un programme C de quelques dizaines de lignes
(`packaging/windows/lanceur.c`, livré en source dans `docs/`). Il démarre
l'interpréteur Python du sous-dossier `runtime`, en mode isolé (`-I`), et lui
demande d'ouvrir l'outil.

Ce qu'il ne fait **pas**, et pourquoi c'est écrit :

- **Aucun interpréteur du poste n'est cherché.** Ni le PATH, ni le registre,
  ni une variable d'environnement : l'interpréteur employé est celui du
  dossier, et lui seul. Deux postes font donc le même calcul, quoi qu'ils aient
  installé par ailleurs.
- **Aucun chemin n'est écrit en dur.** Tout se déduit de l'emplacement du
  lanceur. Le dossier se déplace, se copie sur une clé, se pose sur un partage.
- **Le mode isolé** empêche tout paquet installé ailleurs sur le poste, toute
  variable d'environnement et tout répertoire utilisateur de s'inviter dans
  l'analyse.

> **Subtilité du fichier unique, à signaler au RSSI.** La forme .exe
> **décompresse son contenu avant de l'exécuter**, ce qui est le comportement
> que certaines protections de poste sanctionnent. La forme dossier ne le fait
> pas : tout y est déjà sur le disque. **Si votre politique interdit
> l'exécution depuis un emplacement temporaire, livrez la forme dossier.**

### 9.3 Provenance de l'interpréteur

CPython 3.12.7 (amd64) est repris tel quel des composants officiels de
python.org. Le fichier `docs/EMPREINTES-RUNTIME.txt` livré dans le paquet
donne le **SHA-256 de chaque fichier** de l'interpréteur, avec son chemin
relatif, ainsi que la liste de ce qui a été retiré. Une équipe informatique
peut donc vérifier que le Python livré est bien celui de python.org, fichier
par fichier, sans avoir à nous croire.

### 9.4 Signature Authenticode

**Le livrable fourni n'est pas signé.** SmartScreen avertira au premier
lancement. L'outil de fabrication accepte un certificat et une clé
(`--certificat`, `--cle`) ; la signature est à faire avec **votre** certificat
d'éditeur, et la clé privée ne doit jamais entrer dans le dépôt. C'est le
point à traiter avant un déploiement large.

---

## 9 bis. Détection comportementale (CrowdStrike Falcon et équivalents)

Un EDR ne lit pas une signature : il note des comportements. Cette section
traite ce qu'il regarde, avec les mesures prises sur le livrable.

### 9 bis.1 Caractéristiques des binaires

| Mesure | Lanceur du dossier | Exécutable unique |
|---|---|---|
| ASLR (`DYNAMICBASE` + `HIGH_ENTROPY_VA`) | **oui** | **oui** |
| DEP (`NX_COMPAT`) | **oui** | **oui** |
| Control Flow Guard (`GUARD_CF`) | non | non |
| Bloc de version (éditeur, produit, version) | **oui** | **oui** |
| Chemins de compilation laissés dans le binaire | **aucun** | **aucun** |
| Sous-système | GUI | GUI |
| Signature Authenticode | aucune (§9.4) | aucune (§9.4) |

**`GUARD_CF` absent** : la chaîne de compilation croisée mingw-w64 ne
l'émet pas. C'est une limite de l'outillage, pas un choix. Elle se relève en
revue ; elle n'est pas bloquante pour un programme de 9 Ko de code qui
n'analyse aucune entrée réseau.

**Le bloc de version était absent, et il a été ajouté pendant cet audit.** Un
exécutable sans éditeur, sans nom de produit et sans numéro de version est une
anomalie en soi : les moteurs de détection comportementale s'en servent comme
d'un signal parmi d'autres. Il est désormais généré à partir de
`hr_analytics/version.py`, de sorte que les deux numéros ne puissent pas
diverger.

### 9 bis.2 Table d'import : ce que les lanceurs savent appeler

C'est la mesure la plus parlante pour un analyste. Table complète du lanceur
du dossier, **19 fonctions de KERNEL32, 1 de USER32**, et rien d'autre :

```
CloseHandle          CreateProcessW       DeleteCriticalSection
EnterCriticalSection GetExitCodeProcess   GetFileAttributesW
GetLastError         GetModuleFileNameW   GetStartupInfoW
InitializeCriticalSection                 LeaveCriticalSection
SetUnhandledExceptionFilter               Sleep
TlsGetValue          VirtualProtect       VirtualQuery
WaitForSingleObject  lstrcatW             lstrcpynW
MessageBoxW (USER32)
```

L'exécutable unique y ajoute `CreateFileW`, `ReadFile`, `WriteFile`,
`DeleteFileW`, `GetFileSizeEx`, `SetFilePointerEx`, `HeapAlloc`, `HeapFree`,
`GetProcessHeap` (lire sa charge et la déposer), `SetupIterateCabinetW`
(déplier le CAB, par Windows lui-même), et `SHGetFolderPathW`,
`SHCreateDirectoryExW`, `SHFileOperationW` (trouver et créer le dépôt).

Ce que cette table **ne contient pas**, et qui est l'essentiel :

| Absent | Ce que cela écarte |
|---|---|
| `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread` | Injection de code dans un autre processus |
| `SetWindowsHookEx` | Interception clavier, injection par hook |
| `LoadLibraryA/W`, `GetProcAddress` | **Résolution dynamique d'API** : le signal le plus net d'un chargeur malveillant |
| `RegCreateKey*`, `RegSetValue*` | Persistance par registre |
| `WSAStartup`, `InternetOpen*`, `URLDownloadToFile` | Toute sortie réseau |
| `AdjustTokenPrivileges`, `OpenProcessToken` | Élévation de privilège |
| `IsDebuggerPresent`, `CheckRemoteDebuggerPresent` | Anti-analyse |
| `WinExec`, `ShellExecute*` | Lancement opaque |

`VirtualProtect` et `VirtualQuery` sont présents : ils ne sont **pas** appelés
par notre code, vérifié, aucune occurrence dans les deux sources C, mais par
le démarrage de la bibliothèque C de mingw (relocalisation pseudo-PE). C'est
le cas de tout binaire produit par cette chaîne.

### 9 bis.3 Provenance des binaires livrés

**59 des 60 binaires du paquet portent leur signature Authenticode d'origine**
(Python Software Foundation, Tcl). Le seul non signé est notre lanceur.

C'est une conséquence directe d'un choix : les binaires de python.org sont
repris **tels quels**, jamais recompilés ni modifiés. Un EDR qui voit
`python312.dll`, `_tkinter.pyd` et les 55 autres signés par la PSF a devant
lui des fichiers qu'il connaît déjà, souvent déjà en liste d'autorisation.

> Le compte est passé de 63 à 60 le 8 octobre 2026 : trois modules natifs que
> l'interpréteur livré ne chargeait jamais, `_decimal.pyd` et sa
> bibliothèque libmpdec, `_uuid.pyd`, `_zoneinfo.pyd`, ont été retirés. Voir
> `DEPENDANCES.md` §4. Recompté le 9 octobre 2026 en parcourant le dossier
> `runtime` livré : 57 fichiers `.pyd` et `.dll`, dont les 40 façades
> `api-ms-win-*`.

**Trois trouvailles de cet audit, corrigées :** le paquet contenait
`reg1.3` (extension registre de Tcl, dans un outil qui affirme ne pas
toucher au registre), `dde1.4` (canal DDE, voie connue de mouvement latéral)
et `nmake/x86_64-w64-mingw32-nmakehlp.exe` (**un exécutable compilé, non
signé, inconnu, à l'intérieur du produit** : exactement ce qu'un antivirus
relève). Ils sont retirés, avec `tix` et les bibliothèques d'import. Avant :
5 binaires non signés. Après : 1, le nôtre.

### 9 bis.4 Comportement à l'exécution

**L'arbre des processus.** `HR Analytics.exe` → `pythonw.exe`, et rien
d'autre. Un lanceur qui démarre un interpréteur est un motif qu'un EDR note.
Il est **lisible** plutôt que caché : une version précédente chargeait
`python312.dll` dans son propre processus pour n'avoir aucun processus fils ;
elle ne démarrait pas (bibliothèques C incompatibles entre mingw et MSVC), et
un interpréteur dissimulé dans le lanceur aurait de toute façon été plus
suspect que deux processus nommés.

**Le dépôt de l'exécutable unique.** Il va dans `%LOCALAPPDATA%`, **pas dans
`%TEMP%`** : `%TEMP%` est effacé, surveillé de près, et souvent interdit
d'exécution par stratégie de groupe. Le dépôt porte une empreinte de son
contenu dans son nom, de sorte qu'une version différente s'installe à côté au
lieu d'écraser l'ancienne à moitié ; la configuration vit au-dessus et survit
aux mises à jour. L'extraction n'a lieu **qu'une fois**.

**Le CAB est déplié par Windows lui-même** (`SetupIterateCabinetW`). Aucune
bibliothèque de décompression n'est embarquée : rien à auditer de ce côté,
rien qui puisse être vulnérable.

**Pas de persistance.** Aucune clé `Run`, aucune tâche planifiée, aucun
service, rien dans le dossier Démarrage. Le lanceur n'a aucune API de registre
dans sa table d'import, et l'outil n'importe jamais `winreg`.

### 9 bis.5 Ce qui sera relevé malgré tout, et la réponse

Soyons francs : trois choses feront réagir un analyste, et aucune astuce ne
les supprime.

**1. Un exécutable qui écrit des exécutables puis les lance.** C'est le motif
que surveille toute protection de poste, et c'est ce que fait la forme fichier
unique. **La forme dossier ne le fait pas du tout** : tout y est déjà sur le
disque. *Si votre politique est stricte sur ce point, livrez la forme
dossier : c'est la réponse, et elle ne coûte rien.*

**2. Un interpréteur de script exécutant du code depuis un emplacement
inscriptible par l'utilisateur.** Vrai pour la forme fichier unique (dépôt
dans `%LOCALAPPDATA%`). La forme dossier posée dans `C:\Program Files` ou sur
un partage en lecture seule l'évite entièrement.

**3. Une surcharge de 12,8 Mo d'entropie 7,97/8 derrière 9 Ko de code.**
C'est le CAB, qui est compressé : une entropie élevée est la signature d'un
contenu compressé, et les analyseurs la rapprochent d'un empaqueteur. La forme
dossier n'a pas de surcharge du tout.

**Les trois pointent vers la même recommandation : pour un déploiement en
parc, livrez la forme dossier.** Le fichier unique est fait pour le cas où un
utilisateur doit se débrouiller seul avec un seul fichier.

### 9 bis.6 Pour constituer une exception, si elle est nécessaire

Ce que votre équipe Falcon demandera, et où le trouver :

| Demandé | Où |
|---|---|
| SHA-256 de chaque fichier livré | `docs/EMPREINTES-RUNTIME.txt`, dans le paquet |
| Éditeur / produit / version | Propriétés du fichier (bloc de version, §9 bis.1) |
| Arbre de processus attendu | `HR Analytics.exe` → `pythonw.exe` (§9 bis.4) |
| Chemins écrits | Dépôt `%LOCALAPPDATA%`, dossier de documents choisi |
| Destinations réseau attendues | **aucune** |
| Code source | Livré dans le paquet, lanceur C compris |

Une exception par **empreinte** (AppLocker, WDAC, liste d'autorisation Falcon)
est préférable à une exception par chemin : elle ne survit pas à une
modification du binaire, et les empreintes sont déjà fournies.

## 10. Ce qui a été vérifié pour cette version

| Contrôle | Résultat |
|---|---|
| Suite de tests, Python 3.12, interface comprise | **1 801 tests, 0 échec** (9 octobre 2026) |
| Même suite sur Python 3.10, 3.11, 3.13 | **0 échec** (701 ignorés : interface) |
| Revue de code de la semaine du 2 au 9 octobre | **15 constats, 15 corrigés, chacun pinglé par un essai** (`AUDIT-2026-10-09.md`) |
| Revue fonctionnelle de bout en bout | **21 fonctionnalités, 0 en échec** |
| Stabilité d'affichage (onglets × tailles × parcours) | **129 épreuves, 0 incident** |
| Scan syntaxique : imports et appels sensibles | **0 hors `re.compile`** |
| Imports hors bibliothèque standard | **0** |
| Analyse complète avec réseau et processus instrumentés | **0 tentative** |
| Fichiers hostiles (5 attaques) | **5 refusées ou inertes** |
| Fuite d'identité hors classeur (597 identités cherchées) | **0** |
| Identité du fichier réel retrouvée dans le journal (400 cherchées) | **0** |
| Nom de colonne atteignant autre chose qu'un champ déclaré | **aucun** (§8.6) |
| Interpréteur livré, sous Windows : `socket`, `ssl`, `ctypes`, `subprocess`, `multiprocessing`, `sqlite3` | **6 absents** |
| Modules natifs chargés sur une analyse complète | **8**, et le paquet n'en porte plus que 8 |
| Chemin vers le réseau depuis Python (tous recensés) | **aucun** |
| Primitives d'injection, de persistance ou de réseau dans les lanceurs | **aucune** (§9 bis.2) |
| ASLR, DEP, bloc de version sur les deux lanceurs | **présents** |
| Chemins de compilation laissés dans les binaires | **aucun** |
| Binaires du paquet portant leur signature d'origine | **59 sur 60** |
| Analyse complète sous Windows avec l'interpréteur allégé | **7 documents produits, fenêtre ouverte** |

**Six défauts ont été trouvés et corrigés pendant ces audits**, et ils sont
listés ici parce qu'un dossier de sécurité qui ne dit que les bonnes nouvelles
n'a aucune valeur :

1. **La garde contre les déclarations de type XML ne s'appliquait pas à
   l'onglet** (§7.1) : le seul morceau qu'un fichier reçu contrôle vraiment.
2. **Le correctif du point 1 a introduit une régression** : le flux rendu à
   l'analyseur ne savait plus dire sa position, ce qui aveuglait la barre
   d'avancement. La suite l'a attrapée avant livraison.
3. **Le paquet contenait l'extension registre de Tcl**, dans un outil qui
   affirme ne pas toucher au registre, ainsi qu'un canal DDE et un exécutable
   de compilation non signé (§9 bis.3).
4. **Les lanceurs n'avaient pas de bloc de version** : ni éditeur, ni produit,
   ni numéro, une anomalie en soi pour un moteur comportemental (§9 bis.1).
5. **Nous avions écrit une affirmation fausse** : que le retrait de
   `subprocess` rendait impossible le lancement d'un programme. Un contrôle
   l'a démentie en lançant réellement un processus. Corrigée en §5.1.
6. **Une colonne du fichier pouvait écraser une méthode du modèle de
   données** (§8.6). Pas une exécution de code, rien n'appelle ce qui est
   reçu, mais un arrêt sur un message incompréhensible, sur un nom de
   colonne qui n'a rien d'exotique. Audit du 8 octobre 2026.

---

## 11. Questions que pose habituellement une revue

**« Le logiciel se met-il à jour ? »** Non. Il n'a aucun mécanisme de mise à
jour, donc aucun canal entrant. Une nouvelle version est un nouveau dossier.

**« Y a-t-il de la télémétrie ? »** Non, et la capacité est absente (§4).

**« Où écrit-il ? »** Dans son dossier de configuration et dans le dossier que
l'utilisateur désigne pour les documents. Nulle part ailleurs. Pas de `%APPDATA%`
imposé, pas de registre, pas de service.

**« Que se passe-t-il si le fichier RH est corrompu ou piégé ? »** Il est
refusé avec un message en français, et le détail technique part dans le
journal sans aucune donnée du fichier (§7, §8.2).

**« Le code est-il lisible ? »** Oui, et c'est délibéré : le paquet Python est
livré en source dans le dossier Windows, à côté du lanceur, dont le source C
est également livré. 21 272 lignes commentées en français, 48 suites de tests.

**« Quelle est la surface d'attaque réelle ? »** Un fichier tableur choisi par
l'utilisateur sur son poste. C'est tout : pas de port ouvert, pas de service,
pas d'entrée réseau, pas d'élévation de privilège, pas d'écriture système.

---

## 12. Recommandations avant déploiement

1. **Signer l'exécutable** avec votre certificat d'éditeur (§9.4), sans quoi
   SmartScreen avertira chaque utilisateur.
2. **Choisir la forme de livraison** selon votre politique d'exécution depuis
   un emplacement temporaire (§9.2).
3. **Décider du dossier de destination** des documents produits : sur Windows,
   ce sont ses ACL qui protègent les classeurs, pas le logiciel (§8.5).
4. **Vérifier les trois seuils de confidentialité** avec la DRH avant le
   premier usage : les valeurs par défaut (5 / 10 / 10) sont prudentes mais
   relèvent d'une décision d'entreprise (§8.3).
5. **Ne pas transmettre le fichier de configuration** avec les documents s'il
   porte un sel d'anonymisation (§8.4).
