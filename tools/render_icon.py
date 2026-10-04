#!/usr/bin/env python3
"""Produit l'icone Windows de l'outil : une etoile, en fichier .ico.

    python3 tools/render_icon.py --sortie packaging/windows/etoile.ico

L'etoile est decrite par une formule et non par des pixels : elle est donc
nette a chaque taille, de 16 a 256 points, sans qu'aucune ne soit le
reduction floue d'une autre. Windows choisit la taille qu'il lui faut selon
l'endroit — barre des taches, explorateur, grandes icones.

Aucune bibliotheque d'images : le PNG s'ecrit avec zlib, le conteneur .ico
avec struct. Ce sont les deux seules choses dont ces formats ont besoin.
"""

from __future__ import annotations

import argparse
import math
import os
import struct
import sys
import zlib

#: Tailles qu'un .ico doit porter pour que Windows n'ait jamais a
#: reechantillonner. 256 est la plus grande qu'il sache lire.
TAILLES = (16, 20, 24, 32, 40, 48, 64, 128, 256)

#: Les deux teintes du dessin. Elles viennent de la palette de l'outil :
#: l'icone et la fenetre qu'elle ouvre doivent se reconnaitre.
ENCRE = (0x1F, 0x3A, 0x55)          # bleu d'ardoise, le fond du jeton
ETOILE = (0xFF, 0xFF, 0xFF)         # l'etoile elle-meme

#: Rayon interne de l'etoile, en part du rayon externe. 0,382 est le rapport
#: de l'etoile a cinq branches reguliere — celle qu'on dessine d'un trait
#: sans lever la main. Plus grand, les branches s'epaississent et le dessin
#: perd sa pointe ; plus petit, elles deviennent des aiguilles illisibles a
#: seize pixels.
CREUX = 0.382

#: Echantillons par cote d'un pixel. Le bord d'une branche est oblique :
#: sans ce lissage, il monte en escalier. Quatre par quatre suffisent — a
#: huit la difference ne se voit plus, et le calcul quadruple.
FINESSE = 4


def sommets(rayon: float, centre: float, branches: int = 5) -> list:
    """Les dix sommets de l'etoile, externes et internes en alternance.

    La premiere pointe regarde vers le haut : une etoile posee de travers
    se remarque immediatement, meme de qui ne saurait pas dire pourquoi.
    """
    points = []
    for rang in range(branches * 2):
        angle = -math.pi / 2 + rang * math.pi / branches
        longueur = rayon if rang % 2 == 0 else rayon * CREUX
        points.append((centre + longueur * math.cos(angle),
                       centre + longueur * math.sin(angle)))
    return points


def dedans(x: float, y: float, polygone: list) -> bool:
    """Le point est-il dans le polygone ? Lancer de rayon, parite."""
    compte = 0
    nombre = len(polygone)
    for rang in range(nombre):
        x1, y1 = polygone[rang]
        x2, y2 = polygone[(rang + 1) % nombre]
        if (y1 > y) != (y2 > y):
            coupe = x1 + (y - y1) / (y2 - y1) * (x2 - x1)
            if x < coupe:
                compte += 1
    return compte % 2 == 1


def dessiner(taille: int) -> bytes:
    """Rend l'etoile a la taille demandee, en pixels RGBA bruts.

    Le jeton est un disque : une icone carree se confond avec les tuiles
    du bureau, un disque se reconnait de loin.
    """
    polygone = sommets(taille * 0.40, taille / 2.0)
    rayon_jeton = taille / 2.0 - max(taille * 0.02, 0.5)
    centre = taille / 2.0
    pixels = bytearray()
    pas = 1.0 / FINESSE
    for y in range(taille):
        for x in range(taille):
            jeton = 0
            etoile = 0
            for sy in range(FINESSE):
                for sx in range(FINESSE):
                    px = x + (sx + 0.5) * pas
                    py = y + (sy + 0.5) * pas
                    if (px - centre) ** 2 + (py - centre) ** 2 > rayon_jeton ** 2:
                        continue
                    jeton += 1
                    if dedans(px, py, polygone):
                        etoile += 1
            total = FINESSE * FINESSE
            if jeton == 0:
                pixels += bytes((0, 0, 0, 0))
                continue
            # L'etoile se pose sur le jeton : la couleur du pixel est leur
            # melange, et l'opacite celle du jeton.
            part = etoile / jeton
            couleur = tuple(round(ENCRE[canal] * (1 - part)
                                  + ETOILE[canal] * part) for canal in range(3))
            pixels += bytes(couleur) + bytes((round(255 * jeton / total),))
    return bytes(pixels)


def png(taille: int, pixels: bytes) -> bytes:
    """Encode en PNG, sans bibliotheque d'images."""
    lignes = bytearray()
    largeur = taille * 4
    for y in range(taille):
        lignes.append(0)                       # filtre « aucun »
        lignes += pixels[y * largeur:(y + 1) * largeur]

    def bloc(nom: bytes, contenu: bytes) -> bytes:
        corps = nom + contenu
        return (struct.pack(">I", len(contenu)) + corps
                + struct.pack(">I", zlib.crc32(corps) & 0xFFFFFFFF))

    entete = struct.pack(">IIBBBBB", taille, taille, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", entete)
            + bloc(b"IDAT", zlib.compress(bytes(lignes), 9))
            + bloc(b"IEND", b""))


def ico(images: list) -> bytes:
    """Assemble les images en un conteneur .ico.

    Chaque entree est un PNG complet : Windows le lit tel quel depuis
    Vista, et c'est ce qui permet de porter la taille 256 sans que le
    fichier pese plusieurs megaoctets.
    """
    entete = struct.pack("<HHH", 0, 1, len(images))
    annuaire = b""
    corps = b""
    decalage = len(entete) + 16 * len(images)
    for taille, donnees in images:
        # 0 veut dire 256 : le champ ne tient que sur un octet.
        octet = 0 if taille >= 256 else taille
        annuaire += struct.pack("<BBBBHHII", octet, octet, 0, 0, 1, 32,
                                len(donnees), decalage)
        corps += donnees
        decalage += len(donnees)
    return entete + annuaire + corps


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sortie", default="etoile.ico")
    parser.add_argument("--png", help="ecrit aussi un PNG de cette taille",
                        type=int)
    args = parser.parse_args(argv)

    images = [(taille, png(taille, dessiner(taille))) for taille in TAILLES]
    with open(args.sortie, "wb") as flux:
        flux.write(ico(images))
    print(f"{args.sortie}  ({os.path.getsize(args.sortie)} octets, "
          f"{len(images)} tailles)")
    if args.png:
        chemin = os.path.splitext(args.sortie)[0] + ".png"
        with open(chemin, "wb") as flux:
            flux.write(png(args.png, dessiner(args.png)))
        print(f"{chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
