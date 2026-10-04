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

from hr_analytics.version import __version__                      # noqa: E402

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

#: Arborescences reprises du dépôt.
ARBRES = (("hr_analytics", "hr_analytics"), ("config", "config"),
          ("docs", "docs"))

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
    # -municode : le point d'entrée est wWinMain, donc les chemins Windows
    # en Unicode. -mwindows : pas de fenêtre de console derrière l'outil.
    subprocess.run([compilateur, "-O2", "-municode", "-mwindows",
                    "-o", cible, source], check=True)
    _dire("  lanceur : compilé")
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
            shutil.copytree(origine, os.path.join(runtime, nom),
                            dirs_exist_ok=True)
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
    shutil.copy2(
        os.path.join(ROOT, "packaging", "windows", f"python{PYTHON_TAG}._pth"),
        os.path.join(runtime, f"python{PYTHON_TAG}._pth"))


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
    shutil.copy2(os.path.join(ROOT, "packaging", "windows", "LISEZ-MOI.txt"),
                 os.path.join(destination, "LISEZ-MOI.txt"))
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
    icone = os.path.join(fenetre, "marque.ico")
    if not os.path.isfile(icone):
        _dire("  icone : dessin de la marque")
        from tools.render_icon import main as dessiner
        dessiner(["--sortie", icone])
    objet = os.path.join(destination, "icone.o")
    subprocess.run([ressources, "-I", fenetre,
                    os.path.join(fenetre, "icone.rc"), "-o", objet],
                   check=True)
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
    archive = os.path.join(sortie, f"HR-Insight-{__version__}-windows.zip")
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
