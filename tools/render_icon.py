#!/usr/bin/env python3
"""Produit l'icone Windows de l'outil : la marque, en fichier .ico.

    python3 tools/render_icon.py --sortie packaging/windows/marque.ico

C'est le meme dessin que celui de l'ecran d'accueil — la galaxie —, pose
en blanc sur un jeton rond : une icone de raccourci
doit tenir sur n'importe quel fond de bureau, la ou la marque de la
fenetre connait le sien. La forme vient de « hr_analytics.ui.logo », pas
d'une copie : un outil n'a qu'une identite, et une identite recopiee
diverge.

La marque est decrite par une formule et non par des pixels : elle est
donc nette a chaque taille, de 16 a 256 points, sans qu'aucune ne soit la
reduction floue d'une autre. Windows choisit la taille qu'il lui faut
selon l'endroit — barre des taches, explorateur, grandes icones.

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_analytics.ui import logo

#: Tailles qu'un .ico doit porter pour que Windows n'ait jamais a
#: reechantillonner. 256 est la plus grande qu'il sache lire.
TAILLES = (16, 20, 24, 32, 40, 48, 64, 128, 256)

#: Les deux teintes du dessin. Elles viennent de la palette de l'outil :
#: l'icone et la fenetre qu'elle ouvre doivent se reconnaitre.
ENCRE = (0x1F, 0x3A, 0x55)          # bleu d'ardoise, le fond du jeton
MARQUE = (0xFF, 0xFF, 0xFF)         # la marque elle-meme

#: Part du jeton occupee par la marque, en largeur. La galaxie est ronde
#: comme le jeton : elle doit donc rester nettement plus petite que lui,
#: sans quoi ses bras viennent toucher le bord.
EMPRISE = 0.80

#: Echantillons par cote d'un pixel pour le bord du jeton. Quatre par
#: quatre suffisent — a huit la difference ne se voit plus, et le calcul
#: quadruple. La marque, elle, a sa distance signee : son bord est exact.
FINESSE = 4


def dessiner(taille: int) -> bytes:
    """Rend l'icone a la taille demandee, en pixels RGBA bruts.

    Le jeton est un disque : une icone carree se confond avec les tuiles
    du bureau, un disque se reconnait de loin.
    """
    centre = taille / 2.0
    rayon_jeton = centre - max(taille * 0.02, 0.5)
    emprise = taille * EMPRISE
    pixel = 1.0 / emprise
    pixels = bytearray()
    pas = 1.0 / FINESSE
    for y in range(taille):
        for x in range(taille):
            jeton = 0
            for sy in range(FINESSE):
                for sx in range(FINESSE):
                    px = x + (sx + 0.5) * pas - centre
                    py = y + (sy + 0.5) * pas - centre
                    if px * px + py * py <= rayon_jeton * rayon_jeton:
                        jeton += 1
            total = FINESSE * FINESSE
            if jeton == 0:
                pixels += bytes((0, 0, 0, 0))
                continue
            # La marque vit dans un cadre de largeur 1 dont la ligne
            # mediane est a 0,5 : on y ramene le point avant de lui
            # demander sa distance.
            part = _couverture(
                logo.distance((x + 0.5 - centre) / emprise + 0.5,
                              (y + 0.5 - centre) / emprise + 0.5), pixel)
            couleur = tuple(round(ENCRE[canal] * (1 - part)
                                  + MARQUE[canal] * part) for canal in range(3))
            pixels += bytes(couleur) + bytes((round(255 * jeton / total),))
    return bytes(pixels)


def _couverture(distance: float, pixel: float) -> float:
    """Part d'un pixel couverte, d'apres sa distance au bord de la forme."""
    part = 0.5 - distance / pixel
    return 0.0 if part <= 0.0 else (1.0 if part >= 1.0 else part)


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
    parser.add_argument("--sortie", default="marque.ico")
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
