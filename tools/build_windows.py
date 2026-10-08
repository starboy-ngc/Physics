#!/usr/bin/env python3
"""Compose le paquet Windows : un dossier, un exécutable, rien à installer.

    python3 tools/build_windows.py --sortie dist

Le paquet produit tient dans un dossier que l'utilisateur pose où il veut.
Il double-clique « HR Analytics.exe » ; aucun Python n'a besoin d'exister sur
son poste, parce que l'outil apporte le sien dans « runtime ».

Pourquoi pas un exécutable « un seul fichier » (PyInstaller et semblables) :

  1. Un tel fichier se décompresse dans %TEMP% au démarrage et s'exécute
     depuis là. C'est le comportement même qu'une protection de poste
     sanctionne, et la cause la plus fréquente des blocages en entreprise.
  2. Le code y devient illisible. Un outil qui traite des rémunérations doit
     pouvoir être relu par l'équipe informatique qui l'homologue.
  3. La configuration se retrouverait à l'intérieur de l'archive, dans un
     dossier temporaire recréé à chaque lancement : les réglages de
     l'utilisateur seraient perdus d'une session à l'autre.

Le dossier livré n'a aucun de ces trois défauts.

L'interpréteur vient des paquets officiels de python.org, repris tels quels.
Deux façons de le fournir :

  --runtime <dossier>   un Python Windows déjà extrait (dossier contenant
                        python312.dll, Lib\\, DLLs\\, tcl\\)
  --telecharger         récupère les composants officiels et les extrait
                        (demande msiextract, paquet « msitools »)

Le lanceur est compilé depuis « packaging/windows/lanceur.c » par la chaîne
croisée mingw-w64 (paquet « mingw-w64 »), ou repris tel quel s'il a déjà été
compilé ailleurs.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import zipfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from hr_analytics.version import ENGINE_NAME, PUBLISHER, __version__                      # noqa: E402

#: Version de CPython embarquée. Changer ces deux lignes suffit à suivre une
#: version plus récente — avec la ligne correspondante de `lanceur.c`.
PYTHON_VERSION = "3.12.7"
PYTHON_TAG = "312"

#: Composants officiels nécessaires. « core » porte l'interpréteur, « exe »
#: les exécutables, « lib » la bibliothèque standard, « tcltk » l'interface
#: graphique, « ucrt » la bibliothèque C de Microsoft redistribuable.
#: Volontairement absents : « pip », « doc », « test », « dev » — l'outil
#: n'installe rien, ne compile rien, et n'a pas à embarquer sa propre suite
#: de tests chez l'utilisateur.
COMPOSANTS = ("core", "exe", "lib", "tcltk", "ucrt")

BASE_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/amd64"

#: Ce qui sort de la bibliothèque standard embarquée. Rien de tout cela ne
#: sert à l'outil, et chaque ligne retirée est une ligne de moins à relire
#: pour qui homologue le paquet.
LIB_INUTILE = ("test", "idlelib", "lib2to3", "ensurepip", "turtledemo",
               "distutils", "site-packages", "__pycache__", "pydoc_data")

#: La pile réseau de la bibliothèque standard. L'outil ne l'importe nulle
#: part — un test le vérifie sur le source, et un relevé des modules
#: effectivement chargés par une analyse complète le confirme —, mais la
#: laisser dans le paquet obligerait l'équipe qui l'homologue à nous croire
#: sur parole. Retirée, la question ne se pose plus : la capacité n'est pas
#: là.
#:
#: « _socket.pyd » est la pièce qui décide : sans elle, aucun code Python
#: ne peut ouvrir de connexion, quelle que soit la bibliothèque qui le
#: demanderait. Le reste part pour que personne n'ait à le relire.
#:
#: Volontairement gardés : « libcrypto-3.dll » et « _hashlib.pyd », qui
#: servent aux empreintes SHA-256 et à l'anonymisation, et
#: « urllib/parse.py », que « pathlib » importe pour écrire un chemin en
#: URL — ni l'un ni l'autre n'ouvre quoi que ce soit.
RESEAU_DLLS = ("_socket.pyd", "_ssl.pyd", "select.pyd", "_asyncio.pyd",
               "_overlapped.pyd", "libssl-3.dll")
RESEAU_LIB = ("socket.py", "ssl.py", "selectors.py", "socketserver.py",
              "ftplib.py", "smtplib.py", "poplib.py", "imaplib.py",
              "telnetlib.py", "nntplib.py", "webbrowser.py", "cgi.py",
              "cgitb.py", "http", "email", "xmlrpc", "asyncio", "wsgiref",
              os.path.join("urllib", "request.py"),
              os.path.join("urllib", "error.py"),
              os.path.join("urllib", "response.py"),
              os.path.join("urllib", "robotparser.py"))

#: Ce qui part de l'arborescence Tcl/Tk. Trois de ces pièces sont des
#: trouvailles d'audit, et elles valent d'être nommées :
#:
#:   « reg1.3 » est l'extension registre de Tcl. Elle donne à du code Tcl
#:   le droit de lire et d'écrire la base de registre — dans un outil qui
#:   affirme n'y jamais toucher. L'affirmation et le contenu du paquet se
#:   contredisaient.
#:
#:   « dde1.4 » est l'extension DDE, un canal de communication entre
#:   applications Windows que les protections de poste surveillent de
#:   près : c'est une voie connue de mouvement latéral.
#:
#:   « nmake » est le système de compilation de Tcl, avec un
#:   « nmakehlp.exe » compilé — un exécutable non signé, inconnu, à
#:   l'intérieur du produit. C'est exactement ce qu'un antivirus relève.
#:
#: Le reste est du poids mort : « tix » est une bibliothèque de widgets
#: que l'outil n'emploie pas (et que Python a retirée en 3.13), les
#: « .lib » sont des bibliothèques d'import qui ne servent qu'à compiler,
#: les « .sh » configurent une compilation sous Unix.
TCL_INUTILE = ("nmake", "reg1.3", "dde1.4", "tix8.4.3",
               "*.lib", "*.sh", "*.c", "*.vc")

#: Ce qui part ensuite : les capacités que l'outil n'utilise jamais, et
#: qu'un poste n'a aucune raison de lui prêter.
#:
#: Le raisonnement est le même que pour le réseau. L'analyse statique du
#: code montre qu'aucune n'est importée — mais « non utilisé » est une
#: propriété du code d'aujourd'hui, que la relecture doit refaire à chaque
#: version. « Absent » est une propriété du livrable, et elle se constate
#: en listant un dossier.
#:
#: « _ctypes.pyd » est la pièce qui décide pour l'appel système : sans
#: elle, aucun code Python ne peut appeler une fonction de Windows qui ne
#: lui soit pas déjà exposée. C'est elle qui compte vraiment.
#:
#: CE QUE CE RETRAIT NE FAIT PAS, et qu'il ne faut pas prétendre.
#: Retirer « subprocess.py » et « _multiprocessing.pyd » retire les
#: bibliothèques, pas la capacité : « os.system », « os.popen »,
#: « os.spawnv », « os.startfile » et « _winapi.CreateProcess » sont
#: compilés dans « python312.dll » et y restent. Vérifié en lançant
#: vraiment un processus depuis l'interpréteur livré. Il en va de même de
#: « winreg », « mmap » et « pickle ».
#:
#: Les retirer demanderait de recompiler CPython — et donc de renoncer à
#: livrer les binaires de python.org tels quels, que le service
#: informatique peut vérifier empreinte par empreinte. Entre une capacité
#: de moins et une provenance vérifiable, la provenance vaut mieux : elle
#: se contrôle, l'autre se croirait sur parole.
#:
#: Le réseau, lui, est bel et bien fermé, et pour une raison de structure :
#: la pile réseau vit dans « _socket.pyd », un fichier séparé, et aucune
#: primitive de socket n'est compilée dans « python312.dll ». Sans
#: « _socket » et sans « ctypes » pour appeler « ws2_32 » directement, il
#: n'existe aucun chemin vers le réseau depuis Python. Vérifié aussi.
#:
#: Volontairement gardés : « pyexpat.pyd » (lecture du XML d'un .xlsx),
#: « _elementtree.pyd » (idem), « _hashlib.pyd » (SHA-256),
#: « _tkinter.pyd » (la fenêtre), « _bz2.pyd » et « _lzma.pyd » (zipfile
#: les demande à son propre import). Cette liste a été établie en
#: *mesurant* : l'interpréteur livré a été lancé sur une analyse complète,
#: et ce sont les sept modules natifs qu'il charge.
#:
#: « _decimal.pyd » y figurait, au motif qu'il portait les montants. La
#: mesure a démenti : l'outil calcule en flottants, et ce module n'est
#: jamais chargé. Il part avec « _uuid.pyd » et « _zoneinfo.pyd », jamais
#: chargés non plus — trois bibliothèques natives de moins dans un paquet
#: dont chaque binaire doit se justifier.
#:
#: Les modules Python qui les accompagnent restent, eux : « decimal.py »
#: et « _pydecimal.py » parce que « statistics », « fractions » et
#: « _pylong » les importent et doivent continuer de fonctionner, en
#: version Python pure et plus lente ; « uuid.py » parce que « wave.py »
#: l'importe. Sans « _uuid.pyd », sans « ctypes » et sans « subprocess »,
#: « uuid.getnode() » ne peut plus lire l'adresse matérielle de la carte
#: réseau : il rend un nombre tiré au hasard.
CAPACITES_DLLS = ("_ctypes.pyd", "_ctypes_test.pyd", "_multiprocessing.pyd",
                  "_msi.pyd", "_wmi.pyd", "_sqlite3.pyd", "winsound.pyd",
                  "_testcapi.pyd", "_testbuffer.pyd",
                  "_testinternalcapi.pyd", "_testimportmultiple.pyd",
                  "sqlite3.dll", "libffi-8.dll",
                  "_decimal.pyd", "_uuid.pyd", "_zoneinfo.pyd")
CAPACITES_LIB = ("subprocess.py", "multiprocessing", "concurrent", "ctypes",
                 "sqlite3", "shelve.py", "dbm", "pty.py", "tty.py",
                 "pdb.py", "bdb.py", "pydoc.py", "pydoc_data",
                 "antigravity.py", "turtle.py", "turtledemo",
                 "idlelib", "lib2to3", "ensurepip", "venv", "distutils",
                 "zoneinfo")

#: Arborescences reprises du dépôt.
ARBRES = (("hr_analytics", "hr_analytics"), ("config", "config"),
          ("docs", "docs"))

#: Documents qui restent au depot et ne sont pas livres : les audits
#: dates. Ce sont des releves d'etat a une revision donnee, et ils ont
#: leur valeur — ils montrent que l'outil a ete mis en defaut plusieurs
#: fois plutot qu'une. Mais un audit de septembre livre a cote du dossier
#: du jour le contredit sur ce qui a change depuis : le manifeste qui
#: n'existe plus, le LISEZ-MOI retire, la capacite de lancer un processus
#: qui s'est averee subsister. Un lecteur de securite qui trouve deux
#: affirmations contraires dans le meme paquet ne sait pas laquelle croire,
#: et il a raison. Le paquet ne porte donc qu'un etat : celui du jour.
DOCS_NON_LIVRES = ("AUDIT.md", "AUDIT-2026-09-26.md", "AUDIT-2026-10-04.md",
                   "AUDIT-2026-10-08.md", "AUDIT-SECURITE-IT.md")

#: Outils de fabrication de jeux d'essai : ils produisent des populations
#: fictives, et c'est par eux qu'une équipe prend l'outil en main.
OUTILS = ("__init__.py", "generate_sample_population.py",
          "generate_realistic_population.py")


def _dire(message: str) -> None:
    print(message, flush=True)


def telecharger_runtime(cible: str) -> str:
    """Récupère les composants officiels et les extrait."""
    import urllib.request

    if shutil.which("msiextract") is None:
        raise SystemExit(
            "msiextract est introuvable. Installez le paquet « msitools », "
            "ou fournissez un interpréteur déjà extrait avec --runtime.")
    msi = os.path.join(cible, "_msi")
    os.makedirs(msi, exist_ok=True)
    extrait = os.path.join(cible, "_python")
    shutil.rmtree(extrait, ignore_errors=True)
    os.makedirs(extrait)
    for nom in COMPOSANTS:
        chemin = os.path.join(msi, f"{nom}.msi")
        if not os.path.isfile(chemin):
            _dire(f"  téléchargement de {nom}.msi")
            urllib.request.urlretrieve(f"{BASE_URL}/{nom}.msi", chemin)
        subprocess.run(["msiextract", "-C", extrait, chemin],
                       check=True, stdout=subprocess.DEVNULL)
    return extrait


def compiler_icone(destination: str) -> str:
    """Compile la marque en ressource Windows, prête à être liée.

    C'est elle que l'explorateur, le bureau et la barre des tâches
    montrent. Un lanceur compilé sans elle porte l'icône que mingw lui
    donne par défaut — celle que l'utilisateur voit ne vient alors pas de
    l'outil, et aucune reprise de la marque ne la change.
    """
    fenetre = os.path.join(ROOT, "packaging", "windows")
    ressources = shutil.which("x86_64-w64-mingw32-windres")
    if ressources is None:
        raise SystemExit(
            "x86_64-w64-mingw32-windres est nécessaire. Installez le "
            "paquet « mingw-w64 ».")
    icone = os.path.join(fenetre, "marque.ico")
    if not os.path.isfile(icone):
        _dire("  icône : dessin de la marque")
        from tools.render_icon import main as dessiner
        dessiner(["--sortie", icone])
    # Le bloc de version est écrit ici, à partir de « version.py », et non
    # recopié à la main dans le .rc : deux numéros de version dans un même
    # produit finissent toujours par diverger.
    script = os.path.join(destination, "ressources.rc")
    with open(script, "w", encoding="utf-8") as flux:
        flux.write(_ressources())
    objet = os.path.join(destination, "icone.o")
    subprocess.run([ressources, "-I", fenetre, script, "-o", objet],
                   check=True)
    os.remove(script)
    return objet


#: Le script de ressources, écrit à chaque fabrication. Un exécutable sans
#: bloc de version n'a ni éditeur, ni nom de produit, ni numéro affiché
#: dans ses propriétés. C'est une anomalie en soi : un logiciel légitime en
#: porte un, et les moteurs de détection comportementale s'en servent comme
#: d'un signal parmi d'autres. En poser un ne prouve rien — mais ne pas en
#: poser se remarque.
#:
#: 0x40C / 1200 : français, Unicode. 0x40004 : Windows NT, version de
#: diffusion. 0x1 : application.
RESSOURCES = """/* Ressources du lanceur : l'icone, et ce que Windows
 * affiche dans les proprietes du fichier.
 *
 * ECRIT PAR « build_windows.py » a partir de « hr_analytics/version.py ».
 * Ne pas modifier a la main : il est refait a chaque fabrication.
 *
 * Le premier identifiant numerique est celui que l'explorateur retient
 * pour l'icone du fichier. */
1 ICON "marque.ico"

1 VERSIONINFO
FILEVERSION {quadruple}
PRODUCTVERSION {quadruple}
FILEOS 0x40004L
FILETYPE 0x1L
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040C04B0"
        BEGIN
            VALUE "CompanyName", "{editeur}"
            VALUE "FileDescription", "{produit} - analyse de remuneration"
            VALUE "FileVersion", "{version}"
            VALUE "InternalName", "{produit}"
            VALUE "OriginalFilename", "{produit}.exe"
            VALUE "ProductName", "{produit}"
            VALUE "ProductVersion", "{version}"
            VALUE "Comments", "Traitement local, hors ligne."
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x40C, 1200
    END
END
"""


def _ressources() -> str:
    """Le script de ressources, rempli depuis la version de l'outil."""
    nombres = [int(n) for n in __version__.split(".")] + [0, 0, 0]
    return RESSOURCES.format(
        quadruple=",".join(str(n) for n in nombres[:3] + [0]),
        version=__version__, produit=ENGINE_NAME, editeur=PUBLISHER)


def compiler_lanceur(destination: str) -> str:
    """Compile le lanceur, ou reprend celui qui a déjà été compilé."""
    source = os.path.join(ROOT, "packaging", "windows", "lanceur.c")
    deja = os.path.join(ROOT, "packaging", "windows", "HR Analytics.exe")
    cible = os.path.join(destination, "HR Analytics.exe")
    compilateur = shutil.which("x86_64-w64-mingw32-gcc")
    if compilateur is None:
        if os.path.isfile(deja):
            _dire("  lanceur : repris tel quel (pas de chaîne croisée ici)")
            shutil.copy2(deja, cible)
            return cible
        raise SystemExit(
            "x86_64-w64-mingw32-gcc est introuvable. Installez le paquet "
            "« mingw-w64 », ou placez un lanceur déjà compilé dans "
            "packaging/windows/HR Analytics.exe.")
    objet = compiler_icone(destination)
    # -municode : le point d'entrée est wWinMain, donc les chemins Windows
    # en Unicode. -mwindows : pas de fenêtre de console derrière l'outil.
    subprocess.run([compilateur, "-O2", "-municode", "-mwindows",
                    "-o", cible, source, objet], check=True)
    os.remove(objet)
    _dire("  lanceur : compilé, icône comprise")
    return cible


def poser_runtime(extrait: str, destination: str) -> None:
    """Copie l'interpréteur, allégé de ce qui ne sert pas."""
    runtime = os.path.join(destination, "runtime")
    os.makedirs(runtime, exist_ok=True)
    for nom in sorted(os.listdir(extrait)):
        origine = os.path.join(extrait, nom)
        if nom in ("Lib", "DLLs", "tcl", "include", "libs", "Scripts"):
            continue
        if os.path.isfile(origine):
            shutil.copy2(origine, os.path.join(runtime, nom))
    for nom in ("DLLs", "tcl"):
        origine = os.path.join(extrait, nom)
        if os.path.isdir(origine):
            exclus = shutil.ignore_patterns(*TCL_INUTILE) if nom == "tcl" else None
            shutil.copytree(origine, os.path.join(runtime, nom),
                            ignore=exclus, dirs_exist_ok=True)
    source_lib = os.path.join(extrait, "Lib")
    cible_lib = os.path.join(runtime, "Lib")
    shutil.copytree(source_lib, cible_lib,
                    ignore=shutil.ignore_patterns(*LIB_INUTILE),
                    dirs_exist_ok=True)
    for dossier, sous, fichiers in os.walk(cible_lib):
        for nom in list(sous):
            if nom == "__pycache__":
                shutil.rmtree(os.path.join(dossier, nom))
                sous.remove(nom)
        for nom in fichiers:
            if nom.endswith((".pyc", ".pyo")):
                os.remove(os.path.join(dossier, nom))
    retires = retirer_reseau(runtime)
    _dire(f"  pile réseau retirée ({len(retires)} éléments)")
    otes = retirer_capacites(runtime)
    _dire(f"  processus, appel système et base locale retirés "
          f"({len(otes)} éléments)")
    shutil.copy2(
        os.path.join(ROOT, "packaging", "windows", f"python{PYTHON_TAG}._pth"),
        os.path.join(runtime, f"python{PYTHON_TAG}._pth"))


def a_retirer(runtime: str, dlls, lib) -> list:
    """Ce qui serait retiré de cet interpréteur, sans rien toucher.

    Séparé de la suppression pour être vérifiable : un test lui soumet une
    arborescence postiche et lit ce qu'elle rendrait.
    """
    trouves = []
    for nom in dlls:
        for dossier in (runtime, os.path.join(runtime, "DLLs")):
            chemin = os.path.join(dossier, nom)
            if os.path.exists(chemin):
                trouves.append(chemin)
    for nom in lib:
        chemin = os.path.join(runtime, "Lib", nom)
        if os.path.exists(chemin):
            trouves.append(chemin)
    return trouves


def retirer(runtime: str, dlls, lib) -> list:
    """Retire ces pièces, et rend la liste de ce qui est parti."""
    partis = []
    for chemin in a_retirer(runtime, dlls, lib):
        if os.path.isdir(chemin):
            shutil.rmtree(chemin)
        else:
            os.remove(chemin)
        partis.append(os.path.relpath(chemin, runtime))
    return partis


def reseau_a_retirer(runtime: str) -> list:
    """Ce que la pile réseau laisserait partir de cet interpréteur."""
    return a_retirer(runtime, RESEAU_DLLS, RESEAU_LIB)


def capacites_a_retirer(runtime: str) -> list:
    """Ce que les capacités inutilisées laisseraient partir."""
    return a_retirer(runtime, CAPACITES_DLLS, CAPACITES_LIB)


def retirer_reseau(runtime: str) -> list:
    """Retire la pile réseau de l'interpréteur embarqué."""
    return retirer(runtime, RESEAU_DLLS, RESEAU_LIB)


def retirer_capacites(runtime: str) -> list:
    """Retire les capacités que l'outil n'utilise jamais."""
    return retirer(runtime, CAPACITES_DLLS, CAPACITES_LIB)


def empreintes(destination: str) -> str:
    """Écrit l'empreinte de chaque fichier de l'interpréteur embarqué.

    C'est ce qui permet à une équipe informatique de vérifier que le Python
    livré est bien celui de python.org, sans avoir à nous croire.
    """
    runtime = os.path.join(destination, "runtime")
    lignes = [
        "EMPREINTES DE L'INTERPRETEUR EMBARQUE",
        "=" * 38,
        "",
        f"CPython {PYTHON_VERSION} (amd64), repris tel quel des composants",
        f"officiels publies sur {BASE_URL}.",
        "",
        "Composants repris : " + ", ".join(f"{n}.msi" for n in COMPOSANTS),
        "Retires de la bibliotheque standard : " + ", ".join(LIB_INUTILE),
        "Retires de Tcl/Tk : " + ", ".join(TCL_INUTILE),
        "",
        "Pile reseau retiree, de sorte que la capacite ne soit pas",
        "seulement inutilisee mais absente : "
        + ", ".join(RESEAU_DLLS + RESEAU_LIB),
        "",
        "Processus, appel systeme et base locale retires, pour la meme",
        "raison : " + ", ".join(CAPACITES_DLLS + CAPACITES_LIB),
        "",
        "SHA-256 de chaque fichier livre, chemin relatif au dossier :",
        "",
    ]
    for dossier, _sous, fichiers in sorted(os.walk(runtime)):
        for nom in sorted(fichiers):
            chemin = os.path.join(dossier, nom)
            with open(chemin, "rb") as flux:
                empreinte = hashlib.sha256(flux.read()).hexdigest()
            relatif = os.path.relpath(chemin, destination).replace(os.sep, "\\")
            lignes.append(f"{empreinte}  {relatif}")
    cible = os.path.join(destination, "docs", "EMPREINTES-RUNTIME.txt")
    os.makedirs(os.path.dirname(cible), exist_ok=True)
    with open(cible, "w", encoding="utf-8", newline="\r\n") as flux:
        flux.write("\n".join(lignes) + "\n")
    return cible


def composer(destination: str, extrait: str) -> str:
    """Assemble le dossier livré."""
    shutil.rmtree(destination, ignore_errors=True)
    os.makedirs(destination)
    for source, cible in ARBRES:
        origine = os.path.join(ROOT, source)
        if source == "docs":
            shutil.copytree(origine, os.path.join(destination, cible),
                            ignore=shutil.ignore_patterns(*DOCS_NON_LIVRES),
                            dirs_exist_ok=True)
            continue
        if os.path.isdir(origine):
            shutil.copytree(origine, os.path.join(destination, cible),
                            ignore=shutil.ignore_patterns("__pycache__",
                                                          "*.pyc"))
    outils = os.path.join(destination, "tools")
    os.makedirs(outils)
    for nom in OUTILS:
        origine = os.path.join(ROOT, "tools", nom)
        if os.path.isfile(origine):
            shutil.copy2(origine, os.path.join(outils, nom))
    # Pas de « LISEZ-MOI.txt » a la racine du dossier. Il disait quoi
    # double-cliquer et ou poser le dossier — ce que l'utilisateur a deja
    # fait quand il le lit. Le guide utilisateur, lui, reste dans « docs ».
    shutil.copy2(os.path.join(ROOT, "packaging", "windows", "lanceur.c"),
                 os.path.join(destination, "docs", "lanceur.c"))
    compiler_lanceur(destination)
    poser_runtime(extrait, destination)
    _dire("  populations de démonstration")
    from tools.build_archive import build_populations
    build_populations(destination, rows=400, seed=20260910)
    empreintes(destination)
    return destination


#: Marque posee en fin d'executable, juste avant la taille de la charge.
#: Elle distingue un lanceur qui porte son paquet d'un lanceur nu.
MARQUE = b"HRANALYT"


def compiler_stub(destination: str) -> str:
    """Compile le lanceur a fichier unique, icone comprise."""
    fenetre = os.path.join(ROOT, "packaging", "windows")
    compilateur = shutil.which("x86_64-w64-mingw32-gcc")
    ressources = shutil.which("x86_64-w64-mingw32-windres")
    if compilateur is None or ressources is None:
        raise SystemExit(
            "x86_64-w64-mingw32-gcc et -windres sont necessaires. "
            "Installez le paquet « mingw-w64 ».")
    objet = compiler_icone(destination)
    stub = os.path.join(destination, "stub.exe")
    subprocess.run([compilateur, "-O2", "-municode", "-mwindows",
                    os.path.join(fenetre, "lanceur-unique.c"), objet,
                    "-lsetupapi", "-lshell32", "-lole32", "-o", stub],
                   check=True)
    os.remove(objet)
    return stub


def fabriquer_cab(dossier: str, archive: str) -> str:
    """Replie l'arborescence en une archive CAB.

    C'est Windows qui la depliera — SetupIterateCabinetW, presente depuis
    toujours. Aucune bibliotheque de decompression n'est donc embarquee
    dans le lanceur : rien a auditer de ce cote, rien qui puisse etre
    vulnerable.
    """
    if shutil.which("gcab") is None:
        raise SystemExit(
            "gcab est introuvable. Installez le paquet « gcab », ou "
            "composez le dossier plutot que le fichier unique.")
    fichiers = []
    for courant, _sous, noms in os.walk(dossier):
        for nom in noms:
            chemin = os.path.join(courant, nom)
            fichiers.append(os.path.relpath(chemin, dossier))
    fichiers.sort()
    # -c : creer ; -z : compresser. Les chemins sont relatifs au dossier,
    # et c'est sous ces chemins que Windows les depliera.
    subprocess.run(["gcab", "-c", "-z", archive] + fichiers,
                   check=True, cwd=dossier)
    return archive


def coudre(stub: str, cab: str, cible: str) -> str:
    """Pose l'archive a la suite du lanceur, et signe la couture.

    Un executable Windows ignore ce qui suit son dernier octet utile : on
    peut donc lui accrocher n'importe quoi sans l'abimer. Le lanceur, lui,
    se relit et retrouve sa charge grace au pied pose a la toute fin.
    """
    with open(stub, "rb") as flux:
        code = flux.read()
    with open(cab, "rb") as flux:
        charge = flux.read()
    empreinte = zlib.crc32(charge) & 0xFFFFFFFF
    pied = MARQUE + struct.pack("<q", len(charge)) + struct.pack("<I",
                                                                 empreinte)
    with open(cible, "wb") as flux:
        flux.write(code)
        flux.write(charge)
        flux.write(pied)
    return cible


def signer(executable: str, certificat: str, cle: str,
           mot_de_passe: str = "") -> str:
    """Signe l'executable, si l'on a fourni de quoi le faire.

    La signature n'est pas produite ici : la cle privee appartient a celui
    qui signe et n'a rien a faire dans un depot de code.
    """
    if shutil.which("osslsigncode") is None:
        raise SystemExit(
            "osslsigncode est introuvable. Installez le paquet du meme nom, "
            "ou signez sur un poste Windows avec signtool.")
    signe = executable + ".signe"
    commande = ["osslsigncode", "sign", "-certs", certificat, "-key", cle,
                "-n", "HR Analytics", "-h", "sha256",
                "-in", executable, "-out", signe]
    if mot_de_passe:
        commande += ["-pass", mot_de_passe]
    subprocess.run(commande, check=True, stdout=subprocess.DEVNULL)
    os.replace(signe, executable)
    return executable


def zipper(dossier: str, archive: str) -> str:
    base = os.path.basename(dossier)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as sortie:
        for dossier_courant, _sous, fichiers in sorted(os.walk(dossier)):
            for nom in sorted(fichiers):
                chemin = os.path.join(dossier_courant, nom)
                relatif = os.path.relpath(chemin, dossier)
                sortie.write(chemin, os.path.join(base, relatif))
    return archive


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sortie", default="dist",
                        help="dossier où écrire le paquet")
    parser.add_argument("--runtime",
                        help="interpréteur Windows déjà extrait")
    parser.add_argument("--telecharger", action="store_true",
                        help="récupère les composants officiels de python.org")
    parser.add_argument("--exe", action="store_true",
                        help="compose aussi un exécutable unique")
    parser.add_argument("--certificat",
                        help="certificat de signature (PEM ou SPC)")
    parser.add_argument("--cle", help="clé privée de signature")
    parser.add_argument("--mot-de-passe", default="",
                        help="mot de passe de la clé, s'il y en a un")
    args = parser.parse_args(argv)

    sortie = os.path.abspath(args.sortie)
    os.makedirs(sortie, exist_ok=True)
    if args.runtime:
        extrait = os.path.abspath(args.runtime)
        if not os.path.isfile(os.path.join(extrait,
                                           f"python{PYTHON_TAG}.dll")):
            raise SystemExit(
                f"{extrait} ne ressemble pas a un Python Windows extrait "
                f"(python{PYTHON_TAG}.dll introuvable).")
    elif args.telecharger:
        _dire("Interpréteur :")
        extrait = telecharger_runtime(sortie)
    else:
        raise SystemExit("Indiquez --runtime <dossier> ou --telecharger.")

    _dire("Composition :")
    dossier = composer(os.path.join(sortie, "HR Analytics"), extrait)
    archive = os.path.join(sortie, f"HR-Analytics-{__version__}-windows.zip")
    zipper(dossier, archive)
    produits = [archive]

    if args.exe:
        _dire("Exécutable unique :")
        stub = compiler_stub(sortie)
        _dire("  lanceur compilé, icône comprise")
        cab = os.path.join(sortie, "paquet.cab")
        fabriquer_cab(dossier, cab)
        _dire(f"  archive repliée ({os.path.getsize(cab) // 1024} Ko)")
        unique = os.path.join(sortie, "HR Analytics.exe")
        coudre(stub, cab, unique)
        os.remove(stub)
        os.remove(cab)
        if args.certificat and args.cle:
            signer(unique, args.certificat, args.cle, args.mot_de_passe)
            _dire("  signé")
        else:
            _dire("  NON SIGNÉ — SmartScreen avertira au premier lancement")
        produits.append(unique)

    _dire(f"\n{dossier}")
    for chemin in produits:
        _dire(f"{chemin}  ({os.path.getsize(chemin) // 1024} Ko)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
