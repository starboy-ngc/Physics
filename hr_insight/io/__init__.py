"""Lecture/ecriture de fichiers, sans dependance externe.

Les formats XLSX sont lus et ecrits directement (zipfile + XML de la
bibliotheque standard). Aucun composant tiers, aucune DLL, aucun binaire
supplementaire a faire homologuer par l'IT.
"""

from __future__ import annotations

import os
import stat


def restrict_to_owner(path: str) -> str:
    """Retire aux autres utilisateurs le droit de lire un document produit.

    Un classeur d'analyse porte la population : noms, matricules, montants
    individuels. Cree au masque par defaut, il naissait lisible par tout
    compte de la machine — sans consequence sur un poste personnel, mais
    un serveur de rebond, un bureau partage ou un dossier synchronise en
    font une copie du fichier de paie accessible a qui passe.

    L'ecriture se fait d'abord, la restriction ensuite : on ne peut pas
    poser un masque sur un fichier qui n'existe pas encore, et un
    changement de masque global affecterait tout ce que le processus ecrit
    par ailleurs.

    Sous Windows, seul le bit de lecture seule repond a « chmod » ; la
    protection y vient des droits NTFS du dossier. L'appel n'y nuit pas et
    n'y sert a rien : il est sans effet plutot que faux. Un echec — systeme
    de fichiers sans permissions, montage en lecture seule — n'interrompt
    jamais la production du document : le document vaut mieux que son
    masque.
    """
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return path
