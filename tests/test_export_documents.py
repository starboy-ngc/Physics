"""Ce que les quatre documents d'export portent, et dans quel ordre.

Quatre fichiers sortent d'une analyse : un rapport detaille en HTML, une
synthese d'une page, une vue detaillee paysage et un classeur. Ils se
partagent le travail, et ce partage est une decision — pas un effet de
l'ordre dans lequel le code a ete ecrit. Ce module le fixe.

Aucune donnee RH reelle.
"""

import csv
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, make_row
from hr_analytics.core.config import write_default_configuration
from hr_analytics.core.export import build_sheets
from hr_analytics.core.pipeline import AnalysisRequest, run_analysis
from hr_analytics.core.reporting import boxplot_svg, pyramid_svg
from hr_analytics.core.statistics_engine import describe, dispersion


class TestTheGapToTheMedian(unittest.TestCase):
    """L'ecart de chaque borne a la mediane est calcule par le moteur.

    Il est publie et non laisse au lecteur : une synthese qui donne Q1 et
    la mediane sans leur ecart demande une division a chaque lecture, et
    deux lecteurs la font rarement de la meme facon.
    """

    def setUp(self):
        self.stats = describe([float(value) for value in range(100, 200)])
        self.dispersion = dispersion(self.stats)

    def test_the_four_bounds_carry_their_gap(self):
        for cle in ("p10_to_median", "q1_to_median",
                    "q3_to_median", "p90_to_median"):
            self.assertIn(cle, self.dispersion)

    def test_below_the_median_the_gap_is_negative(self):
        self.assertLess(self.dispersion["p10_to_median"], 0)
        self.assertLess(self.dispersion["q1_to_median"], 0)

    def test_above_the_median_the_gap_is_positive(self):
        self.assertGreater(self.dispersion["q3_to_median"], 0)
        self.assertGreater(self.dispersion["p90_to_median"], 0)

    def test_the_gap_is_a_share_of_the_median(self):
        mediane = self.stats["median"]
        attendu = (self.stats["p75"] - mediane) / mediane
        self.assertAlmostEqual(self.dispersion["q3_to_median"], attendu)

    def test_a_median_at_zero_gives_no_gap_rather_than_a_crash(self):
        """Une population ou plus de la moitie des salaires sont absents
        ou nuls amenait une division par zero."""
        plat = dispersion(describe([0.0, 0.0, 0.0, 0.0, 0.0]))
        self.assertIsNone(plat["q3_to_median"])


class TestWorkbookOrder(unittest.TestCase):
    """Le classeur s'ouvre sur ce qui calcule, pas sur la matiere premiere."""

    #: Les onglets qui portent les valeurs d'ou tout part. Ils ferment le
    #: classeur : on y descend quand un resultat surprend.
    MATIERE = ("Fichier importé", "Colonnes lues", "Données individuelles")

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        source = os.path.join(cls.directory, "population.csv")
        with open(source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste"])
            for index in range(60):
                writer.writerow(list(make_row(
                    index, salary=30000 + (index % 25) * 800,
                    gender="F" if index % 2 else "H"))
                    + [["Comptable", "Technicien"][index % 2]])
        config_dir = os.path.join(cls.directory, "config")
        write_default_configuration(config_dir)
        cls.result = run_analysis(AnalysisRequest(source_path=source,
                                                  config_dir=config_dir))
        data = cls.result.config.as_dict()
        data["export_parameters"]["include_individual_data"] = True
        data["export_parameters"]["include_source_file"] = True
        from hr_analytics.core.config import Configuration
        cls.names = [nom for nom, _ in build_sheets(
            cls.result.payload, cls.result.filtered, Configuration(data),
            table=cls.result.table, mapping=cls.result.mapping)]

    def test_the_raw_material_closes_the_workbook(self):
        for nom in self.MATIERE:
            self.assertIn(nom, self.names)
        premier = min(self.names.index(nom) for nom in self.MATIERE)
        # Apres le premier onglet de matiere premiere, il n'y a plus
        # qu'eux : rien qui calcule ne se glisse derriere.
        self.assertEqual(set(self.names[premier:]), set(self.MATIERE))

    def test_every_control_sheet_comes_before_it(self):
        """Une formule se lit avant les lignes qu'elle additionne."""
        premier = min(self.names.index(nom) for nom in self.MATIERE)
        controles = [nom for nom in self.names
                     if nom.startswith("Contrôle") or nom == "Formules"]
        self.assertTrue(controles)
        for nom in controles:
            self.assertLess(self.names.index(nom), premier, nom)

    def test_the_summary_still_opens_the_workbook(self):
        self.assertEqual(self.names[0], "Synthèse")


class TestBoxPlotDrawing(unittest.TestCase):
    """La boite a moustaches, telle qu'elle sort du moteur."""

    SALAIRE = {"min": 18000.0, "p10": 22000.0, "p25": 26000.0,
               "median": 31000.0, "p75": 37000.0, "p90": 46000.0,
               "max": 950000.0}

    def test_nothing_is_drawn_without_the_five_marks(self):
        for manquant in ("p10", "p25", "median", "p75", "p90"):
            partiel = {cle: valeur for cle, valeur in self.SALAIRE.items()
                       if cle != manquant}
            self.assertEqual(boxplot_svg(partiel, "EUR"), "", manquant)

    def test_the_scale_stops_at_the_whiskers(self):
        """Un maximum a 950 000 EUR ne doit pas aplatir la boite : il est
        dit en texte, il n'est pas dessine."""
        svg = boxplot_svg(self.SALAIRE, "EUR", width=400, height=180)
        self.assertIn("maximum", svg)
        self.assertNotIn('x="950000', svg)

    def test_the_five_marks_are_all_named(self):
        svg = boxplot_svg(self.SALAIRE, "EUR", width=400, height=180)
        for nom in ("P10", "Q1", "Médiane", "Q3", "P90"):
            self.assertIn(f">{nom}<", svg)

    def test_the_whiskers_use_a_colour_the_stylesheet_defines(self):
        """Une variable CSS absente de la feuille ne peint rien : les
        moustaches disparaissaient sans que rien ne le signale."""
        from hr_analytics.core import slides
        svg = boxplot_svg(self.SALAIRE, "EUR", width=400, height=180)
        feuille = slides._slide_css()
        for variable in set(re.findall(r"var\((--[\w-]+)\)", svg)):
            self.assertIn(f"{variable}:", feuille, variable)

    def test_a_flat_population_still_draws(self):
        plat = dict.fromkeys(self.SALAIRE, 30000.0)
        self.assertTrue(boxplot_svg(plat, "EUR", width=400, height=180))


class TestPyramidDrawing(unittest.TestCase):
    """La pyramide femmes / hommes."""

    BANDES = [{"label": "20-29", "count": 12, "female": 5, "male": 7},
              {"label": "30-39", "count": 30, "female": 18, "male": 12},
              {"label": "40-49", "count": 0, "female": 0, "male": 0}]

    def test_nothing_is_drawn_without_a_single_band(self):
        self.assertEqual(pyramid_svg([]), "")

    def test_an_empty_band_takes_no_room(self):
        svg = pyramid_svg(self.BANDES, width=300, height=160)
        self.assertNotIn(">40-49<", svg)

    def test_each_side_is_counted_at_the_end_of_its_wing(self):
        svg = pyramid_svg(self.BANDES, width=300, height=160)
        for valeur in ("5", "7", "18", "12"):
            self.assertIn(f">{valeur}<", svg)

    def test_both_wings_share_one_scale(self):
        """Deux echelles feraient paraitre egales deux colonnes qui ne le
        sont pas — c'est precisement la comparaison que le dessin sert."""
        svg = pyramid_svg([{"label": "A", "count": 3, "female": 1, "male": 2}],
                          width=300, height=160)
        largeurs = [float(valeur) for valeur in
                    re.findall(r'<rect[^>]*width="([\d.]+)"', svg)]
        self.assertEqual(len(largeurs), 2)
        self.assertAlmostEqual(largeurs[1] / largeurs[0], 2.0, places=5)


if __name__ == "__main__":
    unittest.main()
