"""Aucun reglage declare ne doit rester sans effet.

Quatre clefs se laissaient regler sans que rien ne change : une methode de
percentile, une methode de detection des atypiques, une annualisation sur
l'ETP, et un « log_personal_data ». La derniere etait la plus trompeuse —
elle donnait a croire que journaliser des donnees personnelles etait une
option, alors que c'est une impossibilite. La troisieme etait la plus
couteuse : un utilisateur la mettant a « true » aurait publie des ecarts
qu'il croyait ramenes au temps plein.

Ce test ne surveille pas ces quatre-la. Il surveille la famille : toute
clef ajoutee aux defauts sans etre lue par le code le fait echouer.
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_insight.core.config import DEFAULTS

RACINE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "hr_insight")
#: Fichier ou les defauts sont ecrits : leur propre declaration ne compte
#: pas comme une lecture.
DECLARATION = os.path.join(RACINE, "core", "config.py")


def sources():
    for base, dossiers, noms in os.walk(RACINE):
        dossiers[:] = [d for d in dossiers if d != "__pycache__"]
        for nom in sorted(noms):
            if nom.endswith(".py"):
                yield os.path.join(base, nom)


class TestEverySettingIsRead(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.textes = {}
        for chemin in sources():
            contenu = open(chemin, encoding="utf-8").read()
            if chemin == DECLARATION:
                # On retire le bloc des defauts : une clef n'est pas « lue »
                # par le fait d'y figurer. La borne est la premiere
                # declaration de premier niveau qui suit — « class
                # Configuration ». Si elle disparaissait, le decoupage
                # rendrait le fichier entier et le controle deviendrait
                # decoratif : le test s'en assure lui-meme.
                debut = contenu.find("DEFAULTS: Dict[str, Any] = {")
                fin = contenu.find("\nclass Configuration", debut)
                assert debut >= 0 and fin > debut, (
                    "le bloc DEFAULTS n'a pas pu être isolé dans config.py")
                contenu = contenu[:debut] + contenu[fin:]
            cls.textes[chemin] = contenu

    def _lue(self, cle):
        # Nom cite tel quel, ou construit par f-string (f"{section}.auto_extend").
        motif = re.compile(r'["\'][^"\']*\b' + re.escape(cle) + r'\b[^"\']*["\']')
        return any(motif.search(texte) for texte in self.textes.values())

    def test_no_declared_setting_is_inert(self):
        inertes = []
        for section, contenu in DEFAULTS.items():
            if not isinstance(contenu, dict):
                continue
            for cle in contenu:
                if not self._lue(cle):
                    inertes.append(f"{section}.{cle}")
        self.assertEqual(
            inertes, [],
            "Ces réglages se laissent modifier sans que rien ne change. "
            "Un réglage inerte ment à celui qui le règle : implémentez-le, "
            "ou retirez-le.")


if __name__ == "__main__":
    unittest.main()
