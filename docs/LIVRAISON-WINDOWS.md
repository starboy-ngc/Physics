# Livrer l'outil sous Windows, à des utilisateurs sans Python

Le besoin : un utilisateur RH double-clique un fichier, la fenêtre s'ouvre.
Il n'installe rien, ne tape rien, et n'a pas à savoir que Python existe. Son
équipe informatique doit pouvoir homologuer le paquet sans le lancer.

## Ce qui est livré

Un dossier, et rien d'autre.

```
HR Insight\
  HR Insight.exe     le programme à lancer
  LISEZ-MOI.txt
  config\            les réglages, en texte, modifiables au bloc-notes
  hr_insight\        le code de l'outil, lisible
  runtime\           l'interpréteur Python privé de l'outil
  docs\              guides, audits, et le source du lanceur
  population-*.xlsx  jeux d'essai, sans aucune donnée réelle
```

Il se pose où l'on veut — disque local, clé USB, partage réseau — et se
désinstalle en le supprimant. Rien dans le registre, rien dans `%TEMP%`,
rien dans `Program Files`, aucun droit administrateur.

Environ 49 Mo déployés, 16 Mo compressés.

## Pourquoi pas un exécutable « un seul fichier »

PyInstaller, cx_Freeze et semblables replient tout dans un `.exe` unique.
C'est séduisant et c'était le premier réflexe. Trois raisons de ne pas le
faire ici :

1. **Un tel fichier se décompresse dans `%TEMP%` au démarrage et s'exécute
   depuis là.** C'est le comportement même qu'une protection de poste
   sanctionne, et la cause la plus fréquente des blocages en entreprise.
   Un outil que l'antivirus met en quarantaine le premier lundi n'est pas
   livré.
2. **Le code y devient illisible.** Un outil qui traite des rémunérations
   doit pouvoir être relu par l'équipe qui l'homologue. Ici `hr_insight\`
   est du Python en clair, et le lanceur tient en une centaine de lignes de
   C fournies dans `docs\lanceur.c`.
3. **La configuration se retrouverait dans l'archive**, donc dans un dossier
   temporaire recréé à chaque lancement. Les réglages de l'utilisateur
   seraient perdus d'une session à l'autre — exactement ce que la page
   Paramètres existe pour éviter.

Le dossier livré n'a aucun de ces trois défauts.

## Le lanceur

`HR Insight.exe` fait une chose : démarrer `runtime\pythonw.exe` sur
`-I -m hr_insight`, avec le dossier de l'outil pour répertoire de travail.

- **Aucun chemin en dur.** Tout se déduit de `GetModuleFileNameW` :
  l'emplacement du lanceur. Le dossier se déplace et se copie sans être
  reparamétré.
- **Aucun interpréteur du poste n'est cherché.** Ni `PATH`, ni registre, ni
  variable d'environnement. L'interpréteur employé est celui du dossier.
- **`-I`, mode isolé.** Aucun paquet installé ailleurs, aucune variable
  d'environnement, aucun répertoire de l'utilisateur ne peut s'inviter dans
  l'analyse. Deux postes font le même calcul.
- **Aucune fenêtre de console**, pas même une fraction de seconde.
- **Chaque échec est expliqué**, en français, dans une boîte de dialogue.

### Une tentative abandonnée, et pourquoi

La première version chargeait `python312.dll` dans son propre processus et
appelait `Py_Main` : aucun processus fils, un seul programme dans l'arbre.
Élégant sur le papier. **Elle ne démarrait pas.**

Le lanceur est compilé avec mingw, `python312.dll` avec le compilateur de
Microsoft : chacun embarque sa propre bibliothèque C. Chargée en DLL, celle
de Python n'a pas de descripteurs d'entrée et de sortie standard, et
l'initialisation s'arrête sur `can't initialize sys standard streams`. Poser
les poignées Windows avec `SetStdHandle` n'y change rien — ce n'est pas ce
que la bibliothèque C regarde ; `freopen` non plus, puisqu'il agit sur
*l'autre* bibliothèque C.

C'est une leçon qui mérite d'être écrite : **l'élégance supposée d'un
mécanisme ne se constate qu'en l'exécutant.** Le défaut n'était visible
d'aucune relecture.

On démarre donc `pythonw.exe`, comme le fait toute application Python sous
Windows. L'arbre des processus montre `HR Insight.exe` puis `pythonw.exe` :
c'est lisible, et plus honnête qu'un interpréteur caché dans le lanceur.

## Composer le paquet

```
python3 tools/build_windows.py --sortie dist --telecharger
```

Depuis Linux comme depuis Windows. Deux outils sont nécessaires :

| Outil | Paquet Debian/Ubuntu | À quoi il sert |
|---|---|---|
| `x86_64-w64-mingw32-gcc` | `mingw-w64` | compile le lanceur |
| `msiextract` | `msitools` | ouvre les composants de python.org |

`--telecharger` récupère cinq composants officiels sur python.org :
`core`, `exe`, `lib`, `tcltk`, `ucrt`. Si l'on dispose déjà d'un Python
Windows extrait, `--runtime <dossier>` l'emploie et rien n'est téléchargé.

**Le piège à connaître :** la distribution « embeddable » de python.org — le
`.zip` de 11 Mo qu'on trouve en premier — **ne contient pas tkinter**. Ni le
paquet NuGet. L'outil ne démarrerait pas. Les composants individuels, eux,
portent `tcltk.msi`, et c'est pour cela que le script passe par eux.

Sont volontairement laissés de côté : `pip`, `doc`, `test`, `dev`. L'outil
n'installe rien, ne compile rien, et n'a pas à embarquer la suite de tests de
CPython chez l'utilisateur. La bibliothèque standard est en outre allégée de
`test`, `idlelib`, `lib2to3`, `ensurepip`, `turtledemo`, `distutils`,
`pydoc_data` et `site-packages`.

## Pour l'équipe informatique

- **Rien n'est installé** : pas de registre, pas de service, pas de tâche
  planifiée, aucune écriture hors du dossier.
- **Aucune connexion sortante.** L'outil ne sait pas ouvrir de socket.
- **Rien n'est décompressé dans `%TEMP%`** au démarrage.
- **Le code est lisible**, Python en clair et C commenté. Rien n'est
  compilé ni obscurci, hors le lanceur dont le source est livré à côté.
- **L'interpréteur est officiel**, repris tel quel des composants publiés
  par python.org. `docs\EMPREINTES-RUNTIME.txt` donne le SHA-256 de chaque
  fichier livré : la vérification ne demande pas de nous croire.
- **L'interpréteur est isolé** par `runtime\python312._pth`, un fichier de
  trois lignes lisible au bloc-notes.

## Ce qui a été vérifié, et comment

L'environnement de développement est Linux. Le paquet Windows y a été
**exécuté** sous Wine, et non seulement composé :

| Vérification | Résultat |
|---|---|
| L'interpréteur privé démarre | CPython 3.12.7 |
| `sys.path` est celui du `._pth`, et rien d'autre | 3 entrées |
| tkinter se charge et ouvre une fenêtre | Tk 8.6 |
| `default_config_dir()` trouve le `config\` du dossier | oui |
| Analyse complète en ligne de commande, 900 salariés | 7 documents |
| Le lanceur ouvre la fenêtre | capture à l'appui |
| Parcours complet dans la fenêtre : analyse, 5 onglets, export | 7 documents, aucun incident |

**Ce que Wine ne remplace pas.** Il reste à vérifier sur un vrai poste : le
comportement des antivirus et des protections de poste, la signature de
code, les droits NTFS d'un partage réseau, le rendu des polices, et les
chemins de plus de 260 caractères. Ce sont les cinq points à éprouver lors
d'un premier déploiement.

## Le fichier unique

Demandé après coup, et livré : `HR Insight.exe`, 16 Mo, **un seul fichier**,
portant la marque de l'outil.

```
python3 tools/build_windows.py --sortie dist --runtime <python> --exe
```

### Comment il marche

L'exécutable porte, repliée derrière son propre code, une archive CAB
contenant tout le dossier. Un pied de douze octets — une marque, la taille
de la charge, son empreinte — permet au lanceur de la retrouver en se
relisant lui-même.

Au premier lancement, il la dépose dans
`%LOCALAPPDATA%\HR Insight\<empreinte>\` et démarre l'outil. Aux lancements
suivants il trouve le dépôt en place et démarre directement.

Trois détails qui comptent :

- **Le dépôt est dans `%LOCALAPPDATA%`, pas dans `%TEMP%`.** `%TEMP%` est
  effacé, surveillé de près, et souvent interdit d'exécution par stratégie
  de groupe. `LOCALAPPDATA` est l'endroit prévu pour cela.
- **Le dossier de version porte l'empreinte de la charge.** Deux versions
  ne peuvent pas se mélanger, et la même version ne se réextrait jamais.
- **La configuration vit au-dessus des versions**, dans
  `%LOCALAPPDATA%\HR Insight\config\`. Une mise à jour ne la remet pas à
  zéro — c'était le troisième défaut reproché aux exécutables repliés.

C'est **Windows lui-même** qui déplie l'archive (`SetupIterateCabinetW`).
Aucune bibliothèque de décompression n'est embarquée : rien à auditer de ce
côté, rien qui puisse être vulnérable.

### Un second défaut trouvé en exécutant

Le lanceur lisait les vingt derniers octets du fichier pour y trouver son
pied. **Signer l'exécutable ajoute la signature après la charge** : le pied
n'est alors plus à la fin, et le programme signé refusait de démarrer. Le
lanceur cherche désormais la marque à rebours dans le dernier méga-octet.

Comme pour l'impasse de `Py_Main`, aucune relecture ne montrait ce défaut.
Il a fallu signer, lancer, et regarder.

### Ce qu'il coûte, et que le dossier ne coûte pas

**Un exécutable qui écrit d'autres exécutables sur le disque puis les lance
est exactement le motif qu'une protection de poste surveille.** Le dossier
livré à côté ne fait rien de tel. Aucune astuce ne supprime ce coût : il est
inhérent au fichier unique.

Les deux formes sont produites par la même commande. Si le fichier unique
est bloqué sur un poste, le dossier fonctionne sans rien changer d'autre.

## Signature de code

```
python3 tools/build_windows.py --sortie dist --runtime <python> --exe \
    --certificat certificat.pem --cle cle.pem
```

Depuis Linux, `osslsigncode` signe le PE ; depuis Windows, `signtool` fait
la même chose. **La clé privée n'est pas dans ce dépôt et ne doit jamais y
entrer.** Elle appartient à celui qui signe.

Un certificat auto-signé se fabrique ainsi :

```
openssl req -x509 -utf8 -newkey rsa:3072 -keyout cle.pem -out certificat.pem \
    -sha256 -days 1095 -nodes \
    -subj "/CN=Prénom Nom/O=Prénom Nom/C=FR" \
    -addext "keyUsage=digitalSignature" \
    -addext "extendedKeyUsage=codeSigning"
```

### Ce qu'une signature auto-signée fait, et ne fait pas

**Elle fait :** le fichier porte un nom d'éditeur lisible dans ses
propriétés ; toute modification ultérieure du fichier invalide la signature,
ce qui est une vraie garantie d'intégrité ; et surtout, elle devient une
**vraie** garantie dès que l'informatique dépose le certificat dans le
magasin « Éditeurs approuvés » du parc, par stratégie de groupe. C'est
l'usage normal d'un certificat interne, et c'est là que tout change.

**Elle ne fait pas :** elle ne supprime pas l'avertissement SmartScreen. Ce
dernier ne regarde pas la validité de la signature mais la **réputation** du
fichier et de l'éditeur — réputation qu'un certificat auto-signé n'a pas, et
qu'un certificat commercial ne gagne qu'après un certain volume de
téléchargements. Un exécutable signé par un éditeur inconnu reste un
exécutable signé par un éditeur inconnu.

Il faut même le dire franchement : sur certains postes, une signature
d'éditeur non reconnu est traitée avec **plus** de méfiance qu'une absence
de signature, parce que c'est le motif d'un programme qui cherche à se
donner l'air légitime.

### Ce qui marche vraiment

Une seule chose : que l'informatique connaisse le fichier avant
l'utilisateur. Trois voies, par ordre d'efficacité.

1. **Déposer le certificat dans « Éditeurs approuvés »** par stratégie de
   groupe. La signature devient alors une vraie autorisation, et tout ce qui
   est signé par cette clé passe.
2. **Inscrire l'empreinte SHA-256 du fichier** dans les exceptions de
   l'antivirus et du contrôle applicatif (AppLocker, WDAC).
3. **Distribuer par un canal interne déjà approuvé** — partage, outil de
   déploiement —, ce qui dispense de SmartScreen.

Sans l'une de ces trois, l'utilisateur verra un avertissement, et dans un
parc verrouillé le fichier sera simplement bloqué — **quelle que soit la
signature.**
