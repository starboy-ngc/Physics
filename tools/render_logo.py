"""Produit le logo — l'aurore — en image PNG, a la taille demandee.

L'outil calcule son symbole a chaque ouverture, a la taille de son ecran
d'accueil. Ce script sert a en tirer une image : une planche pour une
presentation, une icone, une vignette d'intranet. Il n'est appele par rien
dans l'outil et n'y ajoute aucune dependance — c'est le meme module de
rendu, avec une taille differente.

    python3 tools/render_logo.py --largeur 1024 --sortie logo.png
    python3 tools/render_logo.py --largeur 256 --fond "#141f2a"

Sans « --fond », le fond reste transparent : le logo se pose alors sur ce
qu'on veut. Le dessin est le meme a toutes les tailles — il est decrit par
une formule, non par des pixels.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.core import palette
from compensation_analytics.ui import logo, raster

#: Proportion du cadre : un rideau d'aurore s'inscrit mal dans un carre.
#: Cette hauteur laisse la meme marge de tous les cotes.
RATIO = 0.68


def _lignes(data: bytes, largeur: int, hauteur: int):
    """Relit le PNG produit : RVBA, sans filtrage de ligne."""
    png = base64.b64decode(data)
    corps = b""
    position = 8
    while position < len(png):
        taille = int.from_bytes(png[position:position + 4], "big")
        if png[position + 4:position + 8] == b"IDAT":
            corps += png[position + 8:position + 8 + taille]
        position += 12 + taille
    brut = zlib.decompress(corps)
    ligne = largeur * 4 + 1
    return [brut[y * ligne + 1:(y + 1) * ligne] for y in range(hauteur)]


def _sur_fond(lignes, largeur: int, fond) -> list:
    """Compose le logo sur un aplat opaque."""
    rouge, vert, bleu = fond
    composees = []
    for source in lignes:
        ligne = bytearray(largeur * 4)
        for x in range(largeur):
            r, g, b, a = source[x * 4:x * 4 + 4]
            part = a / 255.0
            ligne[x * 4] = int(r * part + rouge * (1 - part))
            ligne[x * 4 + 1] = int(g * part + vert * (1 - part))
            ligne[x * 4 + 2] = int(b * part + bleu * (1 - part))
            ligne[x * 4 + 3] = 255
        composees.append(ligne)
    return composees


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--largeur", type=int, default=512,
                        help="largeur de l'image en pixels (defaut : 512)")
    parser.add_argument("--hauteur", type=int, default=None,
                        help="hauteur ; par defaut 68 %% de la largeur")
    parser.add_argument("--sortie", default="logo.png",
                        help="fichier PNG a ecrire")
    parser.add_argument("--fond", default=None,
                        help="couleur de fond, « #141f2a » par exemple ; "
                             "sans elle le fond reste transparent")
    args = parser.parse_args(argv)

    hauteur = args.hauteur or int(round(args.largeur * RATIO))
    symbole = logo.Aurora(args.largeur, height=hauteur)
    lignes = _lignes(symbole.frame(0), args.largeur, hauteur)
    if args.fond:
        lignes = _sur_fond(lignes, args.largeur, palette._rgb(args.fond))
    data = raster.image_data(args.largeur, hauteur, lignes, 6)
    with open(args.sortie, "wb") as fichier:
        fichier.write(base64.b64decode(data))
    poids = os.path.getsize(args.sortie) / 1024
    print(f"{args.sortie} — {args.largeur}x{hauteur}, {poids:.0f} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
