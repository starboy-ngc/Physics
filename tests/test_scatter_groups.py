"""Le nuage colore par une dimension nombreuse.

Colorier par « Poste » demande une couleur par poste : la serie
categorielle en compte dix, un fichier en compte quarante. Sans regle,
la dixieme modalite reprenait la couleur de la premiere — deux postes
sans rapport devenaient le meme — et la legende disparaissait au-dela de
seize entrees, laissant un nuage colore que plus rien n'expliquait.

Les modalites les plus nombreuses gardent leur couleur, les autres sont
regroupees sous une seule, neutre. Ce qui est verifie ici : qu'aucun
point ne disparaisse, qu'aucune couleur ne serve deux fois, que le
regroupement ne se confonde avec aucune modalite reelle, et que la
modalite d'origine reste lisible au survol.

Aucune donnee RH reelle.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from compensation_analytics.core import metrics, palette


def dataset(counts, maximum=None):
    """Nuage colore par la BU, avec l'effectif demande par modalite."""
    overrides = {"chart_parameters.scatter_color_by": "business_unit"}
    if maximum is not None:
        overrides["chart_parameters.scatter_max_groups"] = maximum
    config = make_config(overrides)
    rows = []
    index = 0
    for name, effectif in counts.items():
        for _ in range(effectif):
            rows.append(make_row(index, business_unit=name,
                                 tenure=index % 20, salary=30000 + index))
            index += 1
    return metrics.scatter_dataset(build_population(rows, config), config)


class TestGroupsStayReadable(unittest.TestCase):

    def test_a_short_dimension_is_left_alone(self):
        data = dataset({"France": 12, "Iberia": 8})
        self.assertIsNone(data["other_label"])
        self.assertEqual(data["groups"], ["France", "Iberia"])

    def test_modalities_are_ordered_by_headcount(self):
        """La premiere couleur va a la modalite la plus nombreuse : c'est
        celle qu'on cherche des yeux."""
        data = dataset({"Petite": 5, "Grande": 30, "Moyenne": 12})
        self.assertEqual(data["groups"], ["Grande", "Moyenne", "Petite"])

    def test_equal_headcounts_keep_a_stable_order(self):
        """Deux analyses du meme fichier doivent rendre les memes
        couleurs : a effectif egal, l'ordre alphabetique tranche."""
        premier = dataset({"Bravo": 10, "Alpha": 10, "Charlie": 10})
        second = dataset({"Charlie": 10, "Alpha": 10, "Bravo": 10})
        self.assertEqual(premier["groups"], ["Alpha", "Bravo", "Charlie"])
        self.assertEqual(premier["groups"], second["groups"])

    def test_the_tail_is_collapsed_into_one_modality(self):
        data = dataset({f"BU{index:02d}": 20 - index for index in range(15)},
                       maximum=9)
        self.assertEqual(len(data["groups"]), 10)
        self.assertEqual(data["groups"][-1], data["other_label"])
        self.assertIn("6 valeurs", data["other_label"])

    def test_no_point_is_lost_by_the_collapse(self):
        counts = {f"BU{index:02d}": 20 - index for index in range(15)}
        data = dataset(counts, maximum=9)
        self.assertEqual(len(data["points"]), sum(counts.values()))
        self.assertEqual(sum(data["group_counts"].values()),
                         sum(counts.values()))

    def test_the_collapsed_modality_stays_legible_on_the_point(self):
        """Seule la couleur est mise en commun : le point sait toujours de
        quelle modalite il vient, et le survol la nomme."""
        data = dataset({f"BU{index:02d}": 20 - index for index in range(15)},
                       maximum=9)
        regroupes = [point for point in data["points"]
                     if point["group"] == data["other_label"]]
        self.assertTrue(regroupes)
        self.assertTrue(all(point["group_label"].startswith("BU")
                            for point in regroupes))

    def test_named_modalities_are_drawn_after_the_grouped_ones(self):
        """Quatre cents points gris traces en dernier recouvriraient les
        modalites nommees, qui sont justement le sujet."""
        data = dataset({f"BU{index:02d}": 20 - index for index in range(15)},
                       maximum=9)
        rangs = [index for index, point in enumerate(data["points"])
                 if point["group"] == data["other_label"]]
        self.assertEqual(rangs, list(range(len(rangs))))

    def test_a_modality_already_named_autres_is_not_absorbed(self):
        """Le regroupement doit rester distinct d'une modalite du fichier
        qui porterait le meme nom, sinon il l'avale en silence."""
        counts = {f"BU{index:02d}": 30 - index for index in range(9)}
        counts["Autres (3 valeurs)"] = 1
        counts["Reste A"] = 1
        counts["Reste B"] = 1
        data = dataset(counts, maximum=9)
        self.assertNotEqual(data["other_label"], "Autres (3 valeurs)")
        self.assertEqual(data["group_counts"][data["other_label"]], 3)

    def test_the_limit_can_be_lifted_by_configuration(self):
        """Le seuil est un parametre, pas une regle ecrite dans le code."""
        counts = {f"BU{index:02d}": 20 - index for index in range(15)}
        self.assertIsNone(dataset(counts, maximum=0)["other_label"])
        self.assertEqual(len(dataset(counts, maximum=12)["groups"]), 13)

    def test_the_shipped_limit_fits_the_colour_series(self):
        """Neuf modalites nommees et un regroupement occupent exactement
        les dix couleurs de la serie."""
        self.assertEqual(metrics.DEFAULT_MAX_GROUPS + 1,
                         palette.SERIES_COUNT)


class TestColoursAreNeverReused(unittest.TestCase):
    """La couleur vient d'une seule fonction, partagee par les quatre
    supports : ecran, HTML, SVG et PDF."""

    def test_each_modality_gets_its_own_colour(self):
        groups = [f"BU{index}" for index in range(9)] + ["Autres (30 valeurs)"]
        couleurs = palette.series_map(groups, palette.THEMES["ardoise"].palette.series,
                                      other="Autres (30 valeurs)",
                                      neutral="#999999")
        nommees = [couleurs[group] for group in groups[:-1]]
        self.assertEqual(len(set(nommees)), len(nommees))

    def test_the_grouping_takes_the_neutral_and_no_series_colour(self):
        serie = palette.THEMES["ardoise"].palette.series
        groups = [f"BU{index}" for index in range(9)] + ["Autres"]
        couleurs = palette.series_map(groups, serie, other="Autres",
                                      neutral="#999999")
        self.assertEqual(couleurs["Autres"], "#999999")
        self.assertNotIn("#999999", serie)

    def test_without_a_grouping_the_series_is_used_in_order(self):
        serie = palette.THEMES["ardoise"].palette.series
        couleurs = palette.series_map(["A", "B", "C"], serie)
        self.assertEqual([couleurs[key] for key in ("A", "B", "C")],
                         list(serie[:3]))


class TestDocumentsShowTheSameGrouping(unittest.TestCase):
    """Le meme nuage doit se lire de la meme facon sur les trois supports."""

    def setUp(self):
        self.data = dataset(
            {f"BU{index:02d}": 20 - index for index in range(15)}, maximum=9)

    def test_the_html_legend_names_the_grouping(self):
        from compensation_analytics.core import reporting

        legende = reporting._legend(self.data)
        self.assertIn(self.data["other_label"], legende)
        self.assertIn("var(--muted)", legende)

    def test_the_svg_paints_the_grouping_in_the_neutral(self):
        from compensation_analytics.core import reporting

        svg = reporting.scatter_svg(self.data, "EUR")
        self.assertIn('fill="var(--muted)"', svg)

    def test_the_svg_tooltip_names_the_real_modality(self):
        from compensation_analytics.core import reporting

        svg = reporting.scatter_svg(self.data, "EUR")
        self.assertIn("BU14", svg)

    def test_the_pdf_legend_draws_every_modality(self):
        from compensation_analytics.core import slides
        from compensation_analytics.io.pdf_writer import Document

        document = Document()
        page = document.add_page()
        hauteur = slides._draw_legend(page, self.data, 40, 500, 760)
        self.assertGreater(hauteur, 0)


if __name__ == "__main__":
    unittest.main()
