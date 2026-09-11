"""Produit le logo — la galaxie — en image PNG, a la taille demandee.

L'outil calcule sa galaxie a chaque ouverture, a la taille de son ecran
d'accueil. Ce script sert a en tirer une image : une planche pour une
presentation, une icone, une vignette d'intranet. Il n'est appele par rien
dans l'outil et n'y ajoute aucune dependance — c'est le meme module de
rendu, avec une taille differente.

    python3 tools/render_logo.py --taille 1024 --sortie logo.png
    python3 tools/render_logo.py --taille 256 --fond "#141f2a"
    python3 tools/render_logo.py --taille 512 --theme prune

Sans « --fond », le fond reste transparent : le logo se pose alors sur ce
qu'on veut. La rotation est fixe ; « --image » choisit l'angle parmi les
vingt-quatre d'un tour.
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

#: Or du bulbe. Il ne suit pas le theme : c'est la couleur du logo.
CORE = (255, 226, 170)
#: Nombre d'images d'une rotation complete, comme a l'ecran d'accueil.
TURN = 24


def _lignes(data: bytes, size: int):
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
    largeur = size * 4 + 1
    return [brut[y * largeur + 1:(y + 1) * largeur] for y in range(size)]


def _sur_fond(lignes, size: int, fond) -> list:
    """Compose le logo sur un aplat opaque."""
    rouge, vert, bleu = fond
    composees = []
    for source in lignes:
        ligne = bytearray(size * 4)
        for x in range(size):
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
    parser.add_argument("--taille", type=int, default=512,
                        help="cote de l'image en pixels (defaut : 512)")
    parser.add_argument("--sortie", default="logo.png",
                        help="fichier PNG a ecrire")
    parser.add_argument("--fond", default=None,
                        help="couleur de fond, « #141f2a » par exemple ; "
                             "sans elle le fond reste transparent")
    parser.add_argument("--theme", default="ardoise",
                        help="theme dont vient la couleur des bras")
    parser.add_argument("--image", type=int, default=0,
                        help=f"angle de rotation, de 0 a {TURN - 1}")
    args = parser.parse_args(argv)

    accent = palette.by_name(args.theme).accent
    froid = palette._rgb(palette.mix(accent, "#ffffff", 0.45))
    galaxie = logo.Galaxy(args.taille, TURN, cold=froid, warm=CORE)
    lignes = _lignes(galaxie.frame(args.image % TURN), args.taille)
    if args.fond:
        lignes = _sur_fond(lignes, args.taille, palette._rgb(args.fond))
    data = raster.image_data(args.taille, args.taille, lignes, 6)
    with open(args.sortie, "wb") as fichier:
        fichier.write(base64.b64decode(data))
    poids = os.path.getsize(args.sortie) / 1024
    print(f"{args.sortie} — {args.taille}x{args.taille}, {poids:.0f} Ko, "
          f"{len(galaxie.stars)} etoiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
