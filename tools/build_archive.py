"""Construit l'archive de distribution.

La construction d'un livrable ne doit pas vivre dans l'historique d'un
terminal : ce script est la seule definition de ce que contient l'archive,
et il est rejouable a l'identique.

    python3 tools/build_archive.py --sortie dist

Rien n'est telecharge, aucun outil externe n'est appele : la bibliotheque
standard suffit (zipapp, zipfile), conformement au principe d'une chaine
verifiable de bout en bout par une DSI.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import shutil
import sys
import zipapp
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from compensation_analytics.version import __version__  # noqa: E402

#: `zipapp -m` produit un lanceur qui appelle main() sans retransmettre sa
#: valeur : tous les codes de sortie seraient perdus dans l'archive, et
#: "controle" ne pourrait plus signaler d'anomalie bloquante a un script.
LAUNCHER = '''# -*- coding: utf-8 -*-
"""Point d'entree de l'archive.

sys.exit transmet le code de retour : c'est lui qui permet a un traitement
par lot de savoir qu'un controle qualite a echoue.
"""
import sys

from compensation_analytics.cli import main

sys.exit(main())
'''

#: Ce que l'archive contient, en plus du code : dossier source -> destination.
TREES = (("compensation_analytics", "compensation_analytics"),
         ("config", "config"),
         ("tools", "tools"),
         ("docs", "docs"))

FILES = (("packaging/lancer.bat", "lancer.bat"),
         ("packaging/lancer.sh", "lancer.sh"),
         ("packaging/analyser-demo.bat", "analyser-demo.bat"),
         ("packaging/analyser-demo.sh", "analyser-demo.sh"),
         ("packaging/LISEZ-MOI.txt", "LISEZ-MOI.txt"),
         ("README.md", "README.md"))

#: Le .pyz n'embarque que ce qui est necessaire a l'execution.
BUNDLED = ("compensation_analytics", "config")


def _clean(path: str) -> None:
    """Retire ce qui n'a pas a etre distribue."""
    for folder, directories, names in os.walk(path):
        for name in list(directories):
            if name in ("__pycache__", ".git"):
                shutil.rmtree(os.path.join(folder, name))
                directories.remove(name)
        for name in names:
            if name.endswith((".pyc", ".pyo")):
                os.remove(os.path.join(folder, name))


def build_pyz(destination: str) -> str:
    """Assemble l'outil en un fichier unique, lisible comme un ZIP."""
    staging = destination + ".build"
    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging)
    for name in BUNDLED:
        shutil.copytree(os.path.join(ROOT, name), os.path.join(staging, name))
    _clean(staging)
    with open(os.path.join(staging, "__main__.py"), "w", encoding="utf-8") as handle:
        handle.write(LAUNCHER)
    zipapp.create_archive(staging, destination,
                          interpreter="/usr/bin/env python3")
    shutil.rmtree(staging)
    return destination


def build_tree(destination: str) -> str:
    """Compose l'arborescence livree."""
    shutil.rmtree(destination, ignore_errors=True)
    os.makedirs(destination)
    for source, target in TREES:
        origin = os.path.join(ROOT, source)
        if os.path.isdir(origin):
            shutil.copytree(origin, os.path.join(destination, target))
    for source, target in FILES:
        origin = os.path.join(ROOT, source)
        if os.path.isfile(origin):
            shutil.copy2(origin, os.path.join(destination, target))
    _clean(destination)
    build_pyz(os.path.join(destination, "compensation-analytics.pyz"))
    for name in ("lancer.sh", "analyser-demo.sh"):
        path = os.path.join(destination, name)
        if os.path.isfile(path):
            os.chmod(path, 0o755)
    return destination


def build_populations(destination: str, rows: int, seed: int) -> None:
    """Genere les jeux de demonstration.

    Ils sont produits ici, et jamais copies d'ailleurs : aucune donnee RH
    reelle ne peut ainsi se retrouver dans une archive.
    """
    from tools.generate_sample_population import write_population

    write_population(os.path.join(destination, "population-demo.xlsx"),
                     rows=rows, seed=seed, clean=True)
    write_population(
        os.path.join(destination, "population-demo-avec-defauts.xlsx"),
        rows=rows, seed=seed, clean=False)

    # Un troisieme jeu, pour regarder l'outil comme on le regardera en vrai :
    # patronymes plausibles, grille de remuneration qui tient debout, et des
    # anomalies toutes non bloquantes — l'analyse se lance, et l'on voit ce
    # que le controle signale sans qu'il refuse de travailler.
    from tools.generate_realistic_population import construire
    from compensation_analytics.io.xlsx_writer import write_workbook
    from tools.generate_realistic_population import HEADERS as ENTETES

    lignes, _anomalies = construire(900, 20260910, _dt.date.today())
    write_workbook(os.path.join(destination, "population-realiste.xlsx"),
                   [("Population", [ENTETES] + lignes)])


def zip_tree(tree: str, archive: str) -> str:
    """Compresse l'arborescence, chemins relatifs au dossier livre."""
    parent = os.path.dirname(os.path.abspath(tree))
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for folder, _directories, names in os.walk(tree):
            for name in sorted(names):
                path = os.path.join(folder, name)
                bundle.write(path, os.path.relpath(path, parent))
    return archive


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sortie", default="dist")
    parser.add_argument("--lignes", type=int, default=2000)
    parser.add_argument("--graine", type=int, default=20260905)
    args = parser.parse_args(argv)

    os.makedirs(args.sortie, exist_ok=True)
    tree = os.path.join(args.sortie, "compensation-analytics")
    build_tree(tree)
    build_populations(tree, args.lignes, args.graine)
    archive = os.path.join(args.sortie,
                           f"compensation-analytics-{__version__}.zip")
    zip_tree(tree, archive)
    size = os.path.getsize(archive) / 1024
    print(f"{archive}  ({size:.0f} Ko)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
