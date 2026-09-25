"""Un document produit n'est lisible que par celui qui l'a produit.

Le classeur d'analyse porte la population : noms, matricules, montants
individuels. Cree au masque par defaut, il naissait en « -rw-r--r-- » —
lisible par tout compte de la machine. Sans consequence sur un poste
personnel ; sur un serveur de rebond, un bureau partage ou un dossier
synchronise, c'est une copie du fichier de paie accessible a qui passe.

Ces tests portent sur les permissions POSIX. Sous Windows, seul le bit de
lecture seule repond a « chmod » et la protection vient des droits NTFS du
dossier : ils y sont ignores plutot que faux.
"""

import json
import os
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, make_row
from hr_insight.io import restrict_to_owner
from hr_insight.io.xlsx_writer import write_workbook

posix_seulement = unittest.skipUnless(
    os.name == "posix", "permissions POSIX")


@posix_seulement
class TestTheHelperItself(unittest.TestCase):

    def test_it_takes_read_away_from_everyone_else(self):
        dossier = tempfile.mkdtemp()
        chemin = os.path.join(dossier, "document.txt")
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write("contenu")
        os.chmod(chemin, 0o644)
        restrict_to_owner(chemin)
        mode = stat.S_IMODE(os.stat(chemin).st_mode)
        self.assertEqual(mode, 0o600, oct(mode))

    def test_it_returns_the_path_so_it_can_wrap_a_return(self):
        dossier = tempfile.mkdtemp()
        chemin = os.path.join(dossier, "document.txt")
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write("contenu")
        self.assertEqual(restrict_to_owner(chemin), chemin)

    def test_a_failure_never_costs_the_document(self):
        """Un systeme de fichiers sans permissions ne doit pas faire perdre
        le document : le document vaut mieux que son masque."""
        self.assertEqual(restrict_to_owner("/introuvable/nulle/part.txt"),
                         "/introuvable/nulle/part.txt")


@posix_seulement
class TestEveryProducedDocumentIsPrivate(unittest.TestCase):
    """Le controle porte sur la sortie reelle, non sur l'intention."""

    @classmethod
    def setUpClass(cls):
        from hr_insight.core.config import load_configuration
        from hr_insight.core.export import export_excel
        from hr_insight.core.pipeline import AnalysisRequest, run_analysis
        from hr_insight.core.reporting import write_report
        from hr_insight.core.slides import (build_deck, build_summary,
                                            write_slides_html)
        from hr_insight.core.traceability import write_manifest

        cls.directory = tempfile.mkdtemp()
        source = os.path.join(cls.directory, "population.xlsx")
        write_workbook(source, [("Population", [HEADERS]
                                 + [make_row(rang) for rang in range(40)])])
        config_dir = os.path.join(cls.directory, "config")
        from hr_insight.core.config import write_default_configuration
        write_default_configuration(config_dir)
        config = load_configuration(config_dir)
        resultat = run_analysis(AnalysisRequest(source_path=source,
                                                config_dir=config_dir))
        sortie = os.path.join(cls.directory, "sortie")
        os.makedirs(sortie, exist_ok=True)
        export_excel(resultat.payload, resultat.filtered, config,
                     os.path.join(sortie, "analyse.xlsx"), resultat.table,
                     resultat.mapping)
        write_report(resultat.payload, os.path.join(sortie, "r.html"))
        write_slides_html(build_deck(resultat.payload), resultat.payload,
                          os.path.join(sortie, "s.html"))
        write_slides_html(build_summary(resultat.payload), resultat.payload,
                          os.path.join(sortie, "y.html"))
        write_manifest(resultat.payload.get("manifest", {}),
                       os.path.join(sortie, "m.json"))
        cls.sortie = sortie

    def test_no_produced_file_is_readable_by_others(self):
        produits = sorted(os.listdir(self.sortie))
        self.assertGreaterEqual(len(produits), 5)
        ouverts = []
        for nom in produits:
            mode = stat.S_IMODE(os.stat(os.path.join(self.sortie,
                                                     nom)).st_mode)
            if mode & (stat.S_IRGRP | stat.S_IROTH):
                ouverts.append(f"{nom} ({oct(mode)})")
        self.assertEqual(ouverts, [],
                         "ces documents portent la population et sont "
                         "lisibles par d'autres comptes")


if __name__ == "__main__":
    unittest.main()
