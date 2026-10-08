"""Les graphiques, traces pour de bon et relus sur le canevas.

Un graphique n'est verifiable qu'en le dessinant : ce qui compte n'est pas
qu'une methode ne leve pas, mais qu'il y ait autant de barres que de
classes, que la plus haute soit celle du plus grand effectif, qu'aucune
etiquette ne sorte du cadre, et qu'un segment sous le seuil ne soit pas
trace du tout. Les objets poses sur le canevas se relisent : c'est cette
lecture qui sert d'assertion ici.

Ces tests exigent un affichage ; ils sont ignores automatiquement sans lui.
Aucune donnee RH reelle.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import tkinter
    HAS_TK = True
except ImportError:                                    # pragma: no cover
    HAS_TK = False


def _display_answers() -> bool:
    if not (HAS_TK and os.environ.get("DISPLAY")):
        return False
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        return False
    root.destroy()
    return True


needs_display = unittest.skipUnless(
    _display_answers(), "aucun affichage disponible (test de tracé ignoré)")


class Motion:
    """Evenement de souris minimal, pour appeler les gestionnaires."""

    def __init__(self, x, y, delta=0, num=0):
        self.x, self.y = x, y
        self.x_root, self.y_root = x + 100, y + 100
        self.delta, self.num = delta, num


class ChartCase(unittest.TestCase):
    """Une fenetre, un graphique, une taille imposee et un trace force."""

    WIDTH, HEIGHT = 900, 500

    def setUp(self):
        import tkinter as tk

        from hr_analytics.ui import theme

        self.root = tk.Tk()
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+0+0")
        theme.use(None) if hasattr(theme, "use") else None
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def build(self, factory):
        chart = factory(self.root)
        chart.pack(fill="both", expand=True)
        self.root.update()
        chart.canvas.configure(width=self.WIDTH - 40, height=self.HEIGHT - 40)
        self.root.update()
        return chart

    def items(self, canvas, kind=None):
        return [item for item in canvas.find_all()
                if kind is None or canvas.type(item) == kind]

    def texts(self, canvas):
        return [canvas.itemcget(item, "text")
                for item in self.items(canvas, "text")]


@needs_display
class TestHistogram(ChartCase):
    def bins(self, counts):
        return {"available": True, "bins": [
            {"lower": 30000 + index * 5000, "upper": 35000 + index * 5000,
             "count": count} for index, count in enumerate(counts)]}

    def chart(self, counts=(3, 12, 25, 9, 2)):
        from hr_analytics.ui.charts import HistogramChart

        chart = self.build(HistogramChart)
        chart.set_distribution(self.bins(counts))
        self.root.update()
        return chart

    def test_one_bar_per_class(self):
        chart = self.chart()
        bars = [item for item in self.items(chart.canvas, "rectangle")]
        self.assertEqual(len(bars), 5)

    def test_the_tallest_bar_is_the_largest_class(self):
        chart = self.chart()
        heights = []
        for item in self.items(chart.canvas, "rectangle"):
            x1, y1, x2, y2 = chart.canvas.coords(item)
            heights.append((x1, y2 - y1))
        heights.sort()
        tallest = max(range(len(heights)), key=lambda i: heights[i][1])
        self.assertEqual(tallest, 2)             # la classe a 25 salaries

    def test_nothing_is_drawn_outside_the_canvas(self):
        chart = self.chart()
        width = chart.canvas.winfo_width()
        height = chart.canvas.winfo_height()
        for item in self.items(chart.canvas, "rectangle"):
            x1, y1, x2, y2 = chart.canvas.coords(item)
            self.assertGreaterEqual(round(x1), 0)
            self.assertLessEqual(round(x2), width)
            self.assertGreaterEqual(round(y1), 0)
            self.assertLessEqual(round(y2), height)

    def test_an_empty_distribution_says_so_instead_of_drawing(self):
        from hr_analytics.ui.charts import HistogramChart

        chart = self.build(HistogramChart)
        chart.set_distribution({"available": False, "bins": [],
                                "warning": "Effectif insuffisant"})
        self.root.update()
        self.assertEqual(self.items(chart.canvas, "rectangle"), [])
        self.assertIn("Effectif insuffisant", " ".join(self.texts(chart.canvas)))

    def test_hovering_a_bar_shows_its_class(self):
        chart = self.chart()
        item = self.items(chart.canvas, "rectangle")[2]
        x1, y1, x2, y2 = chart.canvas.coords(item)
        chart._on_motion(Motion(int((x1 + x2) / 2), int((y1 + y2) / 2)))
        self.root.update()
        self.assertIsNotNone(chart.tooltip.window)
        self.assertIn("25", chart.tooltip.label.cget("text"))

    def test_leaving_the_chart_hides_the_bubble(self):
        chart = self.chart()
        item = self.items(chart.canvas, "rectangle")[0]
        x1, y1, x2, y2 = chart.canvas.coords(item)
        chart._on_motion(Motion(int((x1 + x2) / 2), int((y1 + y2) / 2)))
        chart.tooltip.hide()
        self.root.update()
        self.assertEqual(chart.tooltip.window.state(), "withdrawn")

    def test_a_single_class_does_not_divide_by_zero(self):
        chart = self.chart(counts=(7,))
        self.assertEqual(len(self.items(chart.canvas, "rectangle")), 1)

    def test_both_axes_are_named_and_nothing_else_is(self):
        """Sous le cadre, le nom de la grandeur ; contre le bord gauche,
        « Effectif ». Une phrase decrivant le graphique tenait cette place
        et laissait les deux axes anonymes."""
        from hr_analytics.ui.charts import HistogramChart

        chart = self.build(HistogramChart)
        distribution = dict(self.bins((3, 12, 25, 9, 2)),
                            label="Salaire de base")
        chart.set_distribution(distribution)
        self.root.update()
        textes = self.texts(chart.canvas)
        self.assertIn("Salaire de base", textes)
        self.assertIn("Effectif", textes)
        self.assertFalse([ligne for ligne in textes
                          if "par classe de" in ligne])

    def test_the_axis_takes_the_name_the_mapping_gives_the_column(self):
        """Le titre ne doit pas etre ecrit en dur : il suit le champ
        analyse, qui n'est pas toujours le salaire de base."""
        from hr_analytics.ui.charts import HistogramChart

        chart = self.build(HistogramChart)
        chart.set_distribution(dict(self.bins((2, 5)),
                                    label="Rémunération annuelle"))
        self.root.update()
        self.assertIn("Rémunération annuelle", self.texts(chart.canvas))

    def test_a_class_with_nobody_in_it_is_still_a_class(self):
        chart = self.chart(counts=(0, 0, 4, 0))
        self.assertEqual(len(self.items(chart.canvas, "rectangle")), 4)


@needs_display
class TestHistogramBackToBack(ChartCase):
    """Femmes au-dessus, hommes au-dessous, sur les memes classes."""

    def distribution(self, femmes=(1, 8, 14, 3, 0), hommes=(0, 4, 11, 12, 5),
                     available=True):
        bins = [{"lower": 30000 + index * 5000, "upper": 35000 + index * 5000,
                 "count": femmes[index] + hommes[index]}
                for index in range(len(femmes))]
        return {"available": True, "bins": bins, "sex_split": {
            "available": available,
            "warning": None if available else "Effectif insuffisant "
                                             "pour séparer femmes et hommes",
            "female_counts": list(femmes) if available else [],
            "male_counts": list(hommes) if available else [],
            "female_count": sum(femmes), "male_count": sum(hommes),
            "female_chartable": available, "male_chartable": available,
            "female_median": 41000.0, "male_median": 48000.0,
            "unknown_count": 0,
        }}

    def chart(self, **kwargs):
        from hr_analytics.ui.charts import HistogramChart

        chart = self.build(HistogramChart)
        chart.set_distribution(self.distribution(**kwargs))
        chart.set_split(True)
        self.root.update()
        return chart

    def test_the_back_to_back_view_names_its_axes_too(self):
        """La legende du haut dit deja quelle moitie est laquelle : le bas
        du cadre nomme la grandeur, et ne redit pas la legende."""
        chart = self.chart()
        textes = self.texts(chart.canvas)
        self.assertIn("Effectif", textes)
        self.assertIn("FEMMES ▲", textes)
        self.assertFalse([ligne for ligne in textes
                          if "au-dessous" in ligne])

    def bars(self, chart):
        """Les barres seules : le fond d'une etiquette est un rectangle lui
        aussi, et il ne se compte pas comme un effectif."""
        return [chart.canvas.coords(item)
                for item in self.items(chart.canvas, "rectangle")
                if "plate" not in chart.canvas.gettags(item)]

    def test_one_bar_per_class_and_per_sex(self):
        chart = self.chart()
        # Neuf classes renseignees sur dix : une classe vide ne se dessine pas.
        self.assertEqual(len(self.bars(chart)), 8)

    def test_the_two_halves_sit_on_either_side_of_the_middle(self):
        chart = self.chart()
        middles = [(coords[1] + coords[3]) / 2 for coords in self.bars(chart)]
        self.assertTrue(any(value < chart.canvas.winfo_height() / 2
                            for value in middles))
        self.assertTrue(any(value > chart.canvas.winfo_height() / 2
                            for value in middles))

    def test_the_bars_stay_inside_the_frame(self):
        """Le defaut a corriger : la hauteur se partage entre deux moities,
        et la calculer sur le cadre entier faisait deborder les plus hautes."""
        chart = self.chart()
        height = chart.canvas.winfo_height()
        width = chart.canvas.winfo_width()
        for x1, y1, x2, y2 in self.bars(chart):
            self.assertGreaterEqual(round(y1), 0)
            self.assertLessEqual(round(y2), height)
            self.assertGreaterEqual(round(x1), 0)
            self.assertLessEqual(round(x2), width)

    def test_a_tall_class_does_not_cross_the_middle(self):
        """La barre la plus haute d'un cote reste de son cote : sinon elle
        se lirait comme un effectif de l'autre sexe."""
        chart = self.chart(femmes=(0, 0, 40, 0, 0), hommes=(0, 0, 0, 0, 1))
        bars = sorted(self.bars(chart), key=lambda c: c[3] - c[1])
        tallest = bars[-1]
        self.assertLess(tallest[3], chart.canvas.winfo_height() / 2 + 4)

    def test_the_two_sides_share_the_same_scale(self):
        """Un effectif deux fois plus grand donne une barre deux fois plus
        haute, de quelque cote qu'il soit."""
        chart = self.chart(femmes=(0, 0, 20, 0, 0), hommes=(0, 0, 10, 0, 0))
        bars = sorted(self.bars(chart), key=lambda c: c[3] - c[1])
        petite, grande = bars[0], bars[-1]
        self.assertAlmostEqual((grande[3] - grande[1]) / (petite[3] - petite[1]),
                               2.0, places=1)

    def test_each_median_is_drawn_and_named(self):
        chart = self.chart()
        self.assertEqual(
            len([text for text in self.texts(chart.canvas)
                 if text.startswith("méd.")]), 2)

    def test_the_header_says_which_half_is_which(self):
        chart = self.chart()
        joined = " ".join(self.texts(chart.canvas))
        self.assertIn("FEMMES", joined)
        self.assertIn("HOMMES", joined)

    def test_hovering_names_the_sex(self):
        chart = self.chart()
        item = self.items(chart.canvas, "rectangle")[0]
        x1, y1, x2, y2 = chart.canvas.coords(item)
        chart._on_motion(Motion(int((x1 + x2) / 2), int((y1 + y2) / 2)))
        self.root.update()
        text = chart.tooltip.label.cget("text")
        self.assertTrue("femmes" in text or "hommes" in text)

    def test_a_refused_split_falls_back_to_the_whole_population(self):
        chart = self.chart(available=False)
        self.assertFalse(chart.may_split())
        self.assertIn("Effectif insuffisant", chart.split_warning())
        # Une barre par classe renseignee, et non deux : l'histogramme
        # d'ensemble, comme si le bouton n'avait pas ete coche.
        self.assertEqual(len(self.bars(chart)), 5)

    def test_going_back_to_the_whole_population_redraws_it(self):
        chart = self.chart()
        chart.set_split(False)
        self.root.update()
        self.assertEqual(len(self.bars(chart)), 5)
        self.assertNotIn("FEMMES", " ".join(self.texts(chart.canvas)))


@needs_display
class TestTheWithheldSegmentsPointSomewhereReal(ChartCase):
    """Le pied renvoyait a « l'onglet Segments », qui n'existe plus.

    Une phrase qui envoie l'utilisateur chercher un onglet absent est pire
    qu'une phrase absente : elle le fait douter de ce qu'il voit.
    """

    def test_the_note_names_a_place_that_exists(self):
        from hr_analytics.ui.charts import BoxPlotChart

        chart = self.build(BoxPlotChart)
        rows = [{"segment": f"Poste {index}", "headcount": 30,
                 "chartable": True, "masked": False,
                 "salary": {"p10": 30000.0, "p25": 34000.0, "median": 38000.0,
                            "p75": 42000.0, "p90": 46000.0}}
                for index in range(4)]
        # Publiable, mais pas tracable : c'est exactement le cas que le
        # pied compte.
        rows.append({"segment": "Direction", "headcount": 7,
                     "chartable": False, "masked": False,
                     "salary": {"median": 60000.0}})
        chart.set_rows(rows, "EUR")
        self.root.update()
        pied = " ".join(chart.footer.itemcget(item, "text")
                        for item in chart.footer.find_all()
                        if chart.footer.type(item) == "text")
        self.assertIn("1 segment(s) trop peu nombreux", pied)
        self.assertNotIn("onglet Segments", pied)


@needs_display
class TestTheDispersionColumns(ChartCase):
    """La colonne chiffrée de droite, et ce qui la coiffe."""

    def rows(self, spreads=(1.10, 1.45, 1.95)):
        """Des segments dont l'ouverture de grille est posée, pas devinée."""
        built = []
        for index, ratio in enumerate(spreads):
            q1 = 30000.0
            q3 = q1 * ratio
            built.append({
                "segment": f"Poste {index}", "headcount": 40 - index,
                "chartable": True, "masked": False,
                "salary": {"p10": q1 * 0.9, "p25": q1, "median": (q1 + q3) / 2,
                           "p75": q3, "p90": q3 * 1.1,
                           "dispersion": {"q3_over_q1": ratio}},
            })
        return built

    def chart(self, **kwargs):
        from hr_analytics.ui.charts import BoxPlotChart

        chart = self.build(BoxPlotChart)
        chart.set_rows(self.rows(), "EUR", **kwargs)
        self.root.update()
        return chart

    def head(self, chart):
        return " ".join(chart.header.itemcget(item, "text")
                        for item in chart.header.find_all()
                        if chart.header.type(item) == "text")

    def test_the_median_is_the_only_figure_on_the_right(self):
        """L'ouverture de grille (Q3/Q1) y tenait une seconde colonne. Elle
        redisait ce que la boîte montre — la largeur de la boîte *est*
        l'intervalle Q1-Q3 — et elle poussait les médianes loin des
        libellés."""
        chart = self.chart()
        entete = self.head(chart)
        self.assertIn("MÉDIANE", entete)
        self.assertIn("EFF.", entete)
        self.assertNotIn("OUVERTURE", entete)
        self.assertFalse([texte for texte in self.texts(chart.canvas)
                          if texte.startswith("×")])

    def test_the_spread_sort_goes_with_its_column(self):
        """Un tri qu'aucune colonne ne montre se lit comme un désordre."""
        chart = self.chart()
        cles = [key for key, _l in chart.orders()]
        self.assertNotIn("spread", cles)
        self.assertEqual(cles, ["moteur", "median_asc", "median",
                                "headcount", "alphabetique"])

    def test_the_split_mode_offers_its_own_sort(self):
        """« Écart F/H » n'existe pas en mode simple."""
        chart = self.chart()
        self.assertNotIn("gap", [key for key, _l in chart.orders()])
        chart.set_split(True)
        self.assertIn("gap", [key for key, _l in chart.orders()])


@needs_display
class TestTheNarrowPyramid(ChartCase):
    """Une colonne etroite dessine une pyramide reduite, pas rien du tout."""

    def chart(self, largeur):
        """La pyramide dans une colonne de largeur imposée : c'est la
        largeur reçue, et non celle demandée, qui décide du tracé."""
        import tkinter as tk

        from hr_analytics.ui.charts import PyramidChart

        colonne = tk.Frame(self.root, width=largeur, height=240)
        colonne.pack_propagate(False)
        colonne.pack()
        chart = PyramidChart(colonne)
        chart.pack(fill="both", expand=True)
        self.root.update()
        chart.set_rows([
            {"label": "60+", "count": 20, "female": 8, "male": 12},
            {"label": "50-59", "count": 40, "female": 18, "male": 22},
            {"label": "<20", "count": 6, "female": 2, "male": 4},
        ])
        self.root.update()
        return chart

    def test_a_column_of_one_hundred_and_eighty_five_pixels_still_draws(self):
        """Une pyramide entierement vide, sans un mot : on ne savait pas si
        la donnee manquait ou le dessin."""
        chart = self.chart(185)
        self.assertTrue(chart.canvas.find_all())

    def test_a_column_too_narrow_for_its_labels_draws_nothing(self):
        """En dessous de ses propres besoins, elle se tait plutot que de
        superposer les libelles et les barres."""
        chart = self.chart(90)
        self.assertEqual(chart.canvas.find_all(), ())


@needs_display
class TestTheScatterDots(ChartCase):
    """De vrais ronds, et un point choisi qui grossit sans se déguiser."""

    def chart(self):
        from hr_analytics.ui.charts import ScatterChart

        chart = self.build(ScatterChart)
        chart.set_dataset({
            "available": True,
            "x_axis": {"field": "tenure_years", "label": "Ancienneté",
                       "kind": "years"},
            "y_axis": {"field": "base_salary", "label": "Salaire de base",
                       "kind": "money"},
            "color_by": "business_unit",
            "points": [{"x": 1.0 + i, "y": 30000.0 + i * 500, "group": "France",
                        "row": i} for i in range(12)],
        }, "EUR")
        self.root.update()
        return chart

    def test_the_chosen_dot_keeps_its_colour_and_grows(self):
        """Il virait au rouge et portait un cerne : deux signaux pour dire
        une chose, et le rouge mentait sur sa population."""
        from hr_analytics.ui.charts import ScatterChart

        chart = self.chart()
        ordinaire = chart._dot("#c26b3f", False)
        choisi = chart._dot("#c26b3f", True)
        self.assertEqual(ordinaire.width(), ScatterChart.DOT)
        self.assertEqual(choisi.width(), ScatterChart.DOT_SELECTED)
        # Même teinte au centre : c'est le même point, en plus gros.
        milieu = ScatterChart.DOT_SELECTED // 2
        self.assertEqual(choisi.get(milieu, milieu)[:3],
                         ordinaire.get(ScatterChart.DOT // 2,
                                       ScatterChart.DOT // 2)[:3])

    def test_no_ring_surrounds_the_chosen_dot(self):
        """Un cerne d'encre ferait, sur le bord, une teinte étrangère à la
        couleur du point."""
        from hr_analytics.ui.charts import ScatterChart

        chart = self.chart()
        choisi = chart._dot("#c26b3f", True)
        milieu = ScatterChart.DOT_SELECTED // 2
        coeur = choisi.get(milieu, milieu)[:3]
        # Le pixel juste à l'intérieur du bord reste dans la teinte du
        # point, et ne vire pas vers l'encre.
        bord = choisi.get(1, milieu)[:3]
        self.assertLess(abs(bord[0] - coeur[0]) + abs(bord[1] - coeur[1])
                        + abs(bord[2] - coeur[2]), 200)

    def test_the_edge_is_graded_rather_than_stepped(self):
        """Un vrai rond a des bords dégradés ; un octogone a des marches.

        Le dégradé vit dans le canal alpha, que `PhotoImage.get` ne rend
        pas : il se vérifie donc là où il est produit, sur le pochoir.
        """
        from hr_analytics.ui import raster
        from hr_analytics.ui.charts import ScatterChart

        taille = ScatterChart.DOT
        pochoir = raster.Raster(taille)
        pochoir.paint(raster._circle(taille / 2.0, taille / 2.0 - 0.5),
                      (47, 93, 138), samples=ScatterChart.DOT_SAMPLES)
        ligne = pochoir.pixels[taille // 2]
        couvertures = {round(pixel[3], 3) for pixel in ligne}
        partielles = [c for c in couvertures if 0.0 < c < 1.0]
        self.assertTrue(partielles,
                        "aucun pixel de bord partiellement couvert : "
                        "le bord est franc, donc crénelé")

    def test_the_sampling_actually_reaches_the_pixels(self):
        """Monter l'échantillonnage doit changer l'image, sinon le réglage
        ne fait rien."""
        from hr_analytics.ui import raster
        from hr_analytics.ui.charts import ScatterChart

        grossier = raster.disc(ScatterChart.DOT, (47, 93, 138), samples=2)
        fin = raster.disc(ScatterChart.DOT, (47, 93, 138),
                          samples=ScatterChart.DOT_SAMPLES)
        self.assertNotEqual(grossier, fin)


@needs_display
class TestThePyramidLayout(ChartCase):
    """Tranches à gauche, effectifs au bout de leur barre."""

    def chart(self):
        from hr_analytics.ui.charts import PyramidChart

        chart = self.build(PyramidChart)
        chart.set_rows([
            {"label": "20-29", "female": 43, "male": 34},
            {"label": "30-39", "female": 122, "male": 143},
            {"label": "40-49", "female": 174, "male": 191},
        ])
        self.root.update()
        return chart

    def placés(self, chart):
        return {chart.canvas.itemcget(item, "text"):
                chart.canvas.coords(item)
                for item in self.items(chart.canvas, "text")}

    def test_the_bands_sit_on_the_left_edge(self):
        """Elles occupaient la gouttière centrale, où elles séparaient les
        deux ailes au lieu de les laisser se répondre."""
        chart = self.chart()
        for libellé in ("20-29", "30-39", "40-49"):
            self.assertLess(self.placés(chart)[libellé][0], 20, libellé)

    def test_each_count_sits_at_the_end_of_its_bar(self):
        """À une colonne fixe, le nombre flottait loin d'une barre courte."""
        chart = self.chart()
        textes = self.placés(chart)
        barres = [chart.canvas.coords(item)
                  for item in self.items(chart.canvas, "rectangle")]
        # La plus longue aile femme est celle de 174 : son nombre doit en
        # toucher le bout, donc être plus à gauche que celui de 43.
        self.assertLess(textes["174"][0], textes["43"][0])
        self.assertGreater(textes["191"][0], textes["34"][0])
        self.assertTrue(barres)

    def test_the_two_wings_share_one_scale(self):
        """Sans quoi une aile deux fois plus courte représenterait le même
        effectif."""
        chart = self.chart()
        largeurs = sorted(c[2] - c[0]
                          for c in (chart.canvas.coords(item)
                                    for item in self.items(chart.canvas,
                                                           "rectangle")))
        # 191 est le sommet : 43 doit faire 43/191 de sa longueur.
        self.assertAlmostEqual(largeurs[0] / largeurs[-1], 34 / 191, places=1)


@needs_display
class TestTheScaleEnds(ChartCase):
    """Le minimum et le maximum, au-dessus et non sur le tracé."""

    def chart(self):
        from hr_analytics.ui.charts import ScaleChart

        chart = self.build(ScaleChart)
        chart.set_salary({
            "min": 0.0, "max": 8017.0, "p10": 1922.0, "p25": 2167.0,
            "p50": 2588.0, "median": 2588.0, "p75": 3090.0, "p90": 3861.0,
            "published_percentiles": [
                {"key": "p10", "label": "P10"}, {"key": "p25", "label": "Q1"},
                {"key": "p50", "label": "Médiane"},
                {"key": "p75", "label": "Q3"}, {"key": "p90", "label": "P90"}],
        }, "EUR")
        self.root.update()
        return chart

    def test_the_ends_are_above_the_scale(self):
        """Posés à la hauteur du trait, ils s'écrivaient par-dessus."""
        chart = self.chart()
        hauteurs = {chart.canvas.itemcget(item, "text"):
                    chart.canvas.coords(item)[1]
                    for item in self.items(chart.canvas, "text")}
        bornes = [y for texte, y in hauteurs.items()
                  if texte.startswith(("min ", "max "))]
        self.assertEqual(len(bornes), 2)
        boîte = [chart.canvas.coords(item)
                 for item in self.items(chart.canvas, "rectangle")]
        self.assertTrue(boîte)
        for y in bornes:
            self.assertLess(y, boîte[0][1], "la borne touche la boîte")

    def test_the_ends_are_on_a_single_line(self):
        """Sur deux lignes, ils mordaient sur la rangée des percentiles."""
        chart = self.chart()
        textes = [chart.canvas.itemcget(item, "text")
                  for item in self.items(chart.canvas, "text")]
        bornes = [t for t in textes if t.startswith(("min ", "max "))]
        self.assertEqual(len(bornes), 2)
        for borne in bornes:
            self.assertNotIn("\n", borne)


@needs_display
class TestScatter(ChartCase):
    def dataset(self, count=40):
        return {"available": True, "points": [
            {"x": index % 20, "y": 30000 + (index % 20) * 900,
             "group": ["France", "Iberia"][index % 2], "row": index + 2,
             "reference": f"REF{index}"} for index in range(count)]}

    def chart(self, dataset=None):
        from hr_analytics.ui.charts import ScatterChart

        chart = self.build(ScatterChart)
        chart.set_dataset(dataset if dataset is not None else self.dataset())
        self.root.update()
        return chart

    def test_every_point_is_drawn(self):
        chart = self.chart()
        self.assertEqual(len(chart._items), 40)

    def test_both_axes_are_named(self):
        """L'abscisse etait nommee, l'ordonnee non — et c'est elle qui porte
        la remuneration dans la lecture par defaut."""
        chart = self.chart(dict(
            self.dataset(),
            x_axis={"label": "Ancienneté", "kind": "years"},
            y_axis={"label": "Salaire de base", "kind": "money"}))
        textes = self.texts(chart.canvas)
        self.assertIn("Ancienneté (années)", textes)
        self.assertIn("Salaire de base", textes)

    def test_an_axis_of_years_is_graduated_every_five(self):
        """Graduée 0, 10, 20, 30, une ancienneté se lit « vers 15 » là où
        l'on voudrait « 14 ou 16 » : une carrière se situe à cinq ans près,
        et c'est le pas de toutes les tranches de l'outil."""
        chart = self.chart(dict(self.dataset(),
                                x_axis={"label": "Ancienneté", "kind": "years"}))
        textes = self.texts(chart.canvas)
        for graduation in ("0", "5", "10", "15"):
            self.assertIn(graduation, textes)

    def test_a_very_long_axis_of_years_falls_back_on_round_values(self):
        """Au-delà d'une quinzaine de graduations, le pas de cinq
        encombrerait : les valeurs rondes reprennent."""
        points = [{"x": index * 2, "y": 30000 + index * 100, "group": "A",
                   "row": index, "reference": str(index)} for index in range(50)]
        chart = self.chart({"available": True, "points": points,
                            "x_axis": {"label": "Ancienneté", "kind": "years"}})
        graduations = [t for t in self.texts(chart.canvas)
                       if t.isdigit() and int(t) <= 98]
        self.assertLess(len(graduations), 14)
        self.assertNotIn("5", graduations)

    def test_a_money_axis_keeps_its_round_values(self):
        """Le pas de cinq n'a de sens que pour des années : un montant de
        0 à 60 se gradue 0, 20, 40, 60, et non de cinq en cinq, même quand
        treize graduations tiendraient."""
        points = [{"x": index % 20, "y": index * 3, "group": "A",
                   "row": index, "reference": str(index)} for index in range(21)]
        chart = self.chart({"available": True, "points": points,
                            "x_axis": {"label": "Ancienneté", "kind": "years"},
                            "y_axis": {"label": "Salaire", "kind": "money"}})
        montants = [t for t in self.texts(chart.canvas) if "EUR" in t]
        self.assertIn("20 EUR", montants)
        self.assertNotIn("5 EUR", montants)

    def test_hiding_a_group_removes_its_points(self):
        chart = self.chart()
        chart.toggle_group("France")
        self.root.update()
        self.assertEqual(len(chart.visible_points()), 20)
        self.assertEqual(len(chart._items), 20)

    def test_showing_the_group_again_brings_them_back(self):
        chart = self.chart()
        chart.toggle_group("France")
        chart.toggle_group("France")
        self.root.update()
        self.assertEqual(len(chart._items), 40)

    def test_zooming_never_drops_a_point_from_the_data(self):
        """Le zoom ne change que la fenetre affichee : les donnees ne sont
        jamais filtrees a l'insu de l'utilisateur."""
        chart = self.chart()
        chart._zoom(200, 200, 0.5)
        self.root.update()
        self.assertEqual(len(chart.points), 40)
        self.assertEqual(len(chart.visible_points()), 40)

    def test_a_double_click_restores_the_whole_view(self):
        chart = self.chart()
        before = chart._view
        chart._zoom(200, 200, 0.5)
        chart.reset_view()
        self.assertEqual(chart._view, before)

    def test_clicking_a_point_selects_it_and_names_it(self):
        chosen = []
        from hr_analytics.ui.charts import ScatterChart

        chart = self.build(lambda master: ScatterChart(master,
                                                       on_select=chosen.append))
        chart.identify = lambda row: f"SALARIE {row}"
        chart.set_dataset(self.dataset())
        self.root.update()
        item = next(iter(chart._items))
        x, y = chart.canvas.coords(item)[:2]
        chart._on_click(Motion(int(x), int(y)))
        self.root.update()
        self.assertTrue(chosen)
        self.assertIsNotNone(chart.selected)

    def test_the_chart_holds_no_identity_of_its_own(self):
        """Il en demande une au moment de l'afficher, et n'en recoit aucune
        dans son jeu de donnees."""
        chart = self.chart()
        self.assertIsNone(chart.identify)
        for point in chart.points:
            self.assertNotIn("name", point)

    def test_hovering_a_point_shows_the_identity_when_offered(self):
        chart = self.chart()
        chart.identify = lambda row: "DUPONT Marie"
        item = next(iter(chart._items))
        x, y = chart.canvas.coords(item)[:2]
        chart._on_motion(Motion(int(x) + 2, int(y) + 2))
        self.root.update()
        if chart.tooltip.window is not None:
            self.assertIn("DUPONT", chart.tooltip.label.cget("text"))

    def test_a_grouped_point_still_names_its_own_modality(self):
        """Le regroupement met les couleurs en commun, pas les identites :
        le survol doit nommer le poste, pas « Autres »."""
        chart = self.chart({"available": True, "other_label": "Autres (3 valeurs)",
                            "groups": ["France", "Autres (3 valeurs)"],
                            "points": [
            {"x": 5, "y": 40000, "group": "Autres (3 valeurs)",
             "group_label": "Iberia", "row": 2, "reference": "REF1"}]})
        item = next(iter(chart._items))
        x, y = chart.canvas.coords(item)[:2]
        chart._on_motion(Motion(int(x) + 2, int(y) + 2))
        self.root.update()
        if chart.tooltip.window is not None:
            texte = chart.tooltip.label.cget("text")
            self.assertIn("Iberia", texte)
            self.assertNotIn("Autres", texte)

    def test_the_grouping_is_drawn_in_the_neutral_and_not_in_the_series(self):
        """Deux postes sans rapport devenaient la meme couleur quand la
        serie se recyclait ; le regroupement, lui, ne doit ressembler a
        aucune modalite."""
        from hr_analytics.core import palette
        from hr_analytics.ui import theme

        groups = [f"BU{index}" for index in range(9)] + ["Autres (30 valeurs)"]
        couleurs = palette.series_map(groups, theme.ACTIVE.series,
                                      other="Autres (30 valeurs)",
                                      neutral=theme.FAINT)
        self.assertEqual(couleurs["Autres (30 valeurs)"], theme.FAINT)
        nommees = [couleurs[group] for group in groups[:-1]]
        self.assertEqual(len(set(nommees)), 9)

    def test_an_empty_dataset_says_so(self):
        chart = self.chart({"available": False, "points": [],
                            "warning": "Effectif insuffisant"})
        self.assertIn("Effectif insuffisant",
                      " ".join(self.texts(chart.canvas)))

    def test_a_single_point_does_not_collapse_the_scale(self):
        chart = self.chart({"available": True, "points": [
            {"x": 5, "y": 40000, "group": "France", "row": 2}]})
        self.assertEqual(len(chart._items), 1)


@needs_display
class TestScatterExploration(ChartCase):
    """Le nuage est explorable : deplacement, zoom, selection, tendance.

    « Le zoom et le deplacement ne changent que la fenetre affichee : les
    donnees ne sont jamais filtrees a l'insu de l'utilisateur. » C'est la
    promesse de ce graphique, et elle se verifie.
    """

    def chart(self, trend=False, count=40):
        from hr_analytics.ui.charts import ScatterChart

        dataset = {"available": True, "points": [
            {"x": index % 20, "y": 30000 + (index % 20) * 900,
             "group": ["France", "Iberia"][index % 2], "row": index + 2,
             "reference": f"REF{index}"} for index in range(count)]}
        if trend:
            dataset["trend"] = {"slope": 900.0, "intercept": 30000.0}
        chart = self.build(ScatterChart)
        chart.set_dataset(dataset)
        self.root.update()
        return chart

    def _empty_spot(self, chart):
        """Un point du canevas ou il n'y a aucun salarie."""
        return (chart.canvas.winfo_width() - 5, 5)

    def test_the_trend_line_is_drawn_when_the_engine_gives_one(self):
        """Elle vient du moteur : l'interface ne calcule aucune
        regression, elle trace celle qu'on lui donne."""
        chart = self.chart()
        plain = len(chart.canvas.find_all())
        chart.dataset["trend"] = {"slope": 900.0, "intercept": 30000.0}
        chart.redraw()
        self.root.update()
        self.assertEqual(len(chart.canvas.find_all()), plain + 1)

    def test_dragging_moves_the_window_and_keeps_every_point(self):
        chart = self.chart()
        before = chart._view
        x, y = self._empty_spot(chart)
        chart._on_click(Motion(x, y))
        chart._on_drag(Motion(x - 60, y + 40))
        self.root.update()
        self.assertNotEqual(chart._view, before)
        self.assertEqual(len(chart.points), 40)

    def test_dragging_without_having_pressed_does_nothing(self):
        chart = self.chart()
        before = chart._view
        chart._on_drag(Motion(10, 10))
        self.assertEqual(chart._view, before)

    def test_the_wheel_zooms_both_ways(self):
        chart = self.chart()
        full = chart._view
        chart._on_wheel(Motion(200, 200, delta=120))
        zoomed = chart._view
        self.assertLess(zoomed[1] - zoomed[0], full[1] - full[0])
        chart._on_wheel(Motion(200, 200, delta=-120))
        self.assertGreater(chart._view[1] - chart._view[0],
                           zoomed[1] - zoomed[0])

    def test_zooming_out_far_enough_shows_everything_again(self):
        chart = self.chart()
        full = chart._view
        for _ in range(12):
            chart._zoom(200, 200, 1.2)
        self.assertEqual(chart._view, full)

    def test_zooming_in_stops_before_the_window_collapses(self):
        chart = self.chart()
        for _ in range(60):
            chart._zoom(200, 200, 1 / 1.2)
        width = chart._view[1] - chart._view[0]
        self.assertGreater(width, 0)
        self.assertEqual(len(chart.visible_points()), 40)

    def test_zooming_an_empty_chart_does_nothing(self):
        from hr_analytics.ui.charts import ScatterChart

        chart = self.build(ScatterChart)
        chart.set_dataset({"available": False, "points": []})
        chart._zoom(100, 100, 0.5)
        self.assertIsNone(chart._view)

    def test_clicking_a_point_then_the_same_point_unselects_it(self):
        chart = self.chart()
        item = next(iter(chart._items))
        x, y = chart.canvas.coords(item)[:2]
        chart._on_click(Motion(int(x), int(y)))
        self.assertIsNotNone(chart.selected)
        chart._on_click(Motion(int(x), int(y)))
        self.assertIsNone(chart.selected)

    def test_moving_over_empty_space_hides_the_bubble(self):
        chart = self.chart()
        item = next(iter(chart._items))
        x, y = chart.canvas.coords(item)[:2]
        chart._on_motion(Motion(int(x), int(y)))
        chart._on_motion(Motion(*self._empty_spot(chart)))
        self.root.update()
        if chart.tooltip.window is not None:
            self.assertEqual(chart.tooltip.window.state(), "withdrawn")

    def test_the_bubble_falls_back_on_the_anonymous_reference(self):
        """Sans resolveur d'identite — le reglage decoche —, le graphique
        n'a que la reference, et c'est tout ce qu'il doit montrer."""
        chart = self.chart()
        self.assertIsNone(chart.identify)
        point = next(iter(chart._items.values()))
        self.assertEqual(chart._label_of(point), point["reference"])

    def test_no_bubble_while_dragging(self):
        """Une bulle qui suit la souris pendant un deplacement rend le
        geste illisible."""
        chart = self.chart()
        chart._drag = (10, 10, chart._view)
        item = next(iter(chart._items))
        x, y = chart.canvas.coords(item)[:2]
        chart._on_motion(Motion(int(x), int(y)))
        self.root.update()
        if chart.tooltip.window is not None:
            self.assertNotEqual(chart.tooltip.window.state(), "normal")


@needs_display
class TestBoxPlot(ChartCase):
    def rows(self, count=4, chartable=True, sex=False):
        made = []
        for index in range(count):
            salary = {"median": 40000 + index * 2000,
                      "p25": 36000 + index * 2000,
                      "p75": 46000 + index * 2000,
                      "p10": 32000 + index * 2000,
                      "p90": 52000 + index * 2000, "count": 30}
            row = {"segment": f"Segment {index}", "headcount": 30,
                   "masked": False, "chartable": chartable, "salary": salary}
            if sex:
                row.update({
                    "female": dict(salary, median=salary["median"] - 1500),
                    "male": dict(salary, median=salary["median"] + 1500),
                    "female_count": 15, "male_count": 15,
                    "female_chartable": True, "male_chartable": True,
                    "sex_chartable": True})
            made.append(row)
        return made

    def chart(self, rows=None, split=False):
        from hr_analytics.ui.charts import BoxPlotChart

        chart = self.build(BoxPlotChart)
        if split:
            chart.set_split(True)
        chart.set_rows(rows if rows is not None else self.rows())
        self.root.update()
        return chart

    def test_one_box_per_segment(self):
        chart = self.chart()
        self.assertEqual(len(chart._items), 4)

    def test_a_segment_below_the_chart_threshold_is_not_drawn(self):
        """Le drapeau vient du moteur, et son absence vaut refus."""
        rows = self.rows()
        del rows[1]["chartable"]
        chart = self.chart(rows)
        self.assertEqual(len(chart._items), 3)

    def test_a_masked_segment_is_never_drawn(self):
        rows = self.rows()
        rows[0]["masked"] = True
        chart = self.chart(rows)
        self.assertEqual(len(chart._items), 3)

    def test_nothing_drawable_gives_a_sentence_and_no_box(self):
        chart = self.chart(self.rows(chartable=False))
        self.assertEqual(len(chart._items), 0)
        self.assertIn("insuffisant", " ".join(self.texts(chart.canvas)))

    def test_no_segment_at_all_says_so(self):
        chart = self.chart([])
        self.assertIn("Aucun segment", " ".join(self.texts(chart.canvas)))

    def test_the_split_draws_two_boxes_per_segment(self):
        plain = self.chart(self.rows(sex=True))
        split = self.chart(self.rows(sex=True), split=True)
        self.assertGreater(len(split.canvas.find_all()),
                           len(plain.canvas.find_all()))

    def test_a_segment_without_both_sexes_leaves_the_split(self):
        rows = self.rows(sex=True)
        rows[0]["sex_chartable"] = False
        chart = self.chart(rows, split=True)
        segments = {row["segment"] for row, _moitié in chart._items.values()}
        self.assertEqual(len(segments), 3)

    def test_the_order_can_be_changed_without_losing_a_segment(self):
        chart = self.chart()
        for key in ("median", "headcount"):
            chart.set_order(key)
            self.root.update()
            self.assertEqual(len(chart._items), 4)

    def test_the_reference_line_is_drawn_when_given(self):
        from hr_analytics.ui.charts import BoxPlotChart

        chart = self.build(BoxPlotChart)
        chart.set_rows(self.rows(), reference=45000)
        self.root.update()
        with_line = len(chart.canvas.find_all())
        chart.set_rows(self.rows(), reference=None)
        self.root.update()
        self.assertGreater(with_line, len(chart.canvas.find_all()))

    def test_the_canvas_shrinks_to_its_content(self):
        """Le pied de graphique se collait au bas du cadre : la legende des
        abscisses se retrouvait tres loin sous la derniere boite."""
        chart = self.chart(self.rows(count=2))
        needed = int(chart.canvas.cget("height"))
        self.assertLess(needed, self.HEIGHT)

    def test_hovering_a_box_shows_its_figures(self):
        chart = self.chart()
        item = next(iter(chart._items))
        x, y = chart.canvas.coords(item)[:2]
        chart._on_motion(Motion(int(x) + 1, int(y) + 1))
        self.root.update()
        if chart.tooltip.window is not None:
            self.assertIn("Segment", chart.tooltip.texte())


@needs_display
class TestSplitPresentation(ChartCase):
    """Ce que le dedoublement doit montrer, et qu'il ne montrait pas.

    Cocher « distinguer femmes / hommes » repond a une question precise :
    de combien les deux medianes different, et sur quels effectifs. Rien de
    tout cela n'etait lisible — l'ecart n'etait chiffre nulle part, les
    effectifs par sexe non plus, et les deux boites d'un segment etaient
    aussi eloignees l'une de l'autre que de celles du voisin.
    """

    def rows(self, count=6, femmes=20, hommes=25, ecart=True):
        made = []
        for index in range(count):
            mediane = 40000 + index * 1500
            femme = {"median": mediane * (0.92 if ecart else 1.0),
                     "p25": mediane * 0.85, "p75": mediane * 1.05,
                     "p10": mediane * 0.78, "p90": mediane * 1.15,
                     "count": femmes}
            homme = {"median": mediane, "p25": mediane * 0.9,
                     "p75": mediane * 1.12, "p10": mediane * 0.82,
                     "p90": mediane * 1.25, "count": hommes}
            made.append({
                "segment": f"Poste {index}", "headcount": femmes + hommes,
                "masked": False, "chartable": True,
                "salary": dict(homme, median=mediane),
                "female": femme, "male": homme,
                "female_count": femmes, "male_count": hommes,
                "female_chartable": True, "male_chartable": True,
                "sex_chartable": True,
                "median_gap": (homme["median"] - femme["median"])
                / homme["median"] * 100.0,
            })
        return made

    def chart(self, rows=None, alert=5.0):
        from hr_analytics.ui.charts import BoxPlotChart

        chart = self.build(BoxPlotChart)
        chart.set_split(True)
        chart.set_rows(rows if rows is not None else self.rows(), "EUR",
                       alert=alert)
        self.root.update()
        return chart

    def _texts(self, chart):
        return [chart.canvas.itemcget(item, "text")
                for item in chart.canvas.find_all()
                if chart.canvas.type(item) == "text"]

    def test_the_gap_is_written_out(self):
        """Il fallait comparer deux traits verticaux a l'oeil, ce que
        personne ne fait a un pour cent pres."""
        textes = self._texts(self.chart())
        self.assertTrue(any(text.endswith("%") and text.startswith("+")
                            for text in textes), textes)

    def test_the_gap_carries_its_sign(self):
        chart = self.chart(self.rows(count=2))
        ecarts = [text for text in self._texts(chart) if text.endswith("%")]
        self.assertTrue(all(text[0] in "+-" for text in ecarts), ecarts)

    def test_the_gap_uses_the_french_decimal_comma(self):
        ecarts = [text for text in self._texts(self.chart())
                  if text.endswith("%")]
        self.assertTrue(all("," in text for text in ecarts), ecarts)

    def test_a_gap_beyond_the_threshold_is_coloured(self):
        from hr_analytics.ui import theme

        chart = self.chart(self.rows(count=2))          # ecart de 8 %
        couleurs = {chart.canvas.itemcget(item, "fill")
                    for item in chart.canvas.find_all()
                    if chart.canvas.type(item) == "text"
                    and chart.canvas.itemcget(item, "text").endswith("%")}
        self.assertIn(theme.WARN, couleurs)

    def test_a_small_gap_stays_neutral(self):
        from hr_analytics.ui import theme

        chart = self.chart(self.rows(count=2, ecart=False))
        couleurs = {chart.canvas.itemcget(item, "fill")
                    for item in chart.canvas.find_all()
                    if chart.canvas.type(item) == "text"
                    and chart.canvas.itemcget(item, "text").endswith("%")}
        self.assertNotIn(theme.WARN, couleurs)
        self.assertNotIn(theme.CRIT, couleurs)

    def test_the_threshold_comes_from_the_configuration(self):
        """Il etait ecrit en dur dans le graphique alors qu'il existe deja
        en parametre : deux endroits pour une meme regle, c'est un des deux
        qui finit faux."""
        from hr_analytics.ui import theme

        def couleurs(alert):
            chart = self.chart(self.rows(count=2), alert=alert)
            return {chart.canvas.itemcget(item, "fill")
                    for item in chart.canvas.find_all()
                    if chart.canvas.type(item) == "text"
                    and chart.canvas.itemcget(item, "text").endswith("%")}

        self.assertIn(theme.WARN, couleurs(5.0))       # ecart de 8 %
        self.assertNotIn(theme.WARN, couleurs(20.0))

    def test_an_unknown_gap_is_a_dash_and_never_a_zero(self):
        """Un zero se lirait « pas de difference », quand la verite est
        « on n'a pas le droit de le dire »."""
        rows = self.rows(count=2)
        rows[0]["median_gap"] = None
        chart = self.chart(rows)
        textes = self._texts(chart)
        self.assertIn("-", textes)
        self.assertFalse([t for t in textes if t.endswith("%")
                          and t.strip("+-") in ("0 %", "0,0 %")])

    def test_both_headcounts_are_shown(self):
        """Cinq femmes en face de cent vingt hommes ne se lisent pas comme
        deux boites de meme poids."""
        chart = self.chart(self.rows(count=2, femmes=7, hommes=113))
        textes = self._texts(chart)
        self.assertIn("7", textes)
        self.assertIn("113", textes)

    def test_the_two_headcounts_never_overlap(self):
        """Empiles a la hauteur de chaque boite, ils se chevauchaient des
        que la ligne se resserrait."""
        chart = self.chart(self.rows(count=14, femmes=39, hommes=31))
        hauteurs = [chart.canvas.coords(item)[1]
                    for item in chart.canvas.find_all()
                    if chart.canvas.type(item) == "text"
                    and chart.canvas.itemcget(item, "text") in ("39", "31")]
        self.assertTrue(hauteurs)
        for niveau in set(hauteurs):
            # Les deux nombres d'un meme segment partagent leur ligne.
            self.assertEqual(hauteurs.count(niveau), 2)

    def test_each_headcount_wears_the_colour_of_its_sex(self):
        from hr_analytics.ui import theme

        chart = self.chart(self.rows(count=2, femmes=7, hommes=113))
        couleurs = {chart.canvas.itemcget(item, "text"):
                    chart.canvas.itemcget(item, "fill")
                    for item in chart.canvas.find_all()
                    if chart.canvas.type(item) == "text"}
        self.assertEqual(couleurs["7"], theme.FEMALE)
        self.assertEqual(couleurs["113"], theme.MALE)

    def test_the_pair_is_tighter_than_the_gap_between_segments(self):
        """C'est ce qui la fait lire comme une paire : a l'ecartement
        precedent, les deux boites d'un segment etaient aussi eloignees
        l'une de l'autre que de celles du voisin."""
        chart = self.chart(self.rows(count=4))
        boites = sorted(chart.canvas.coords(item)[1]
                        for item in chart.canvas.find_all()
                        if chart.canvas.type(item) == "rectangle"
                        and chart.canvas.coords(item)[2]
                        - chart.canvas.coords(item)[0] < 400)
        self.assertEqual(len(boites), 8)
        dans = [boites[index + 1] - boites[index]
                for index in range(0, len(boites), 2)]
        entre = [boites[index + 2] - boites[index + 1]
                 for index in range(0, len(boites) - 2, 2)]
        self.assertLess(max(dans), min(entre))

    def test_the_row_is_taller_when_split(self):
        """Dix-sept pixels ont ete mesures pour une seule boite : deux
        boites et leurs effectifs n'y tiennent pas."""
        from hr_analytics.ui.charts import BoxPlotChart

        self.assertGreater(BoxPlotChart.ROW_SPLIT_MIN, BoxPlotChart.ROW_MIN)

    def test_the_boxes_sit_inside_their_row(self):
        """Les boites etaient tracees douze pixels au-dessus des traits
        qu'elles sont censees couper : l'origine verticale valait 14 en dur
        quand la grille part de « pad_t »."""
        chart = self.chart(self.rows(count=3))
        bandes = [chart.canvas.coords(item)
                  for item in chart.canvas.find_all()
                  if chart.canvas.type(item) == "rectangle"
                  and chart.canvas.coords(item)[0] == 0]
        self.assertTrue(bandes)
        boites = [chart.canvas.coords(item)
                  for item in chart.canvas.find_all()
                  if chart.canvas.type(item) == "rectangle"
                  and chart.canvas.coords(item)[0] > 0]
        for haut, bas in ((bande[1], bande[3]) for bande in bandes):
            dedans = [boite for boite in boites
                      if haut <= (boite[1] + boite[3]) / 2 <= bas]
            # Une bande couvre un segment : ses deux boites, jamais une.
            self.assertIn(len(dedans), (0, 2), (haut, bas))

    def test_the_reading_key_is_never_cut_off(self):
        """La phrase se renvoie a la ligne quand la fenetre se resserre, et
        quand on dedouble — la legende des deux teintes lui prend de la
        largeur. Mesure faite, jusqu'a vingt-trois pixels de texte etaient
        coupes par le bas : c'est-a-dire la phrase qui explique le
        graphique."""
        from hr_analytics.ui.charts import BoxPlotChart

        for largeur in (1200, 1000, 900, 800, 700):
            self.root.geometry(f"{largeur}x520+0+0")
            self.root.update()
            chart = self.build(BoxPlotChart)
            chart.set_split(True)
            chart.set_rows(self.rows(count=6), "EUR", reference=45000)
            self.root.update()
            contenu = chart.footer.bbox("all")
            if contenu is None:
                continue
            self.assertLessEqual(contenu[3], chart.footer.winfo_height(),
                                 f"pied coupé à {largeur} px")
            chart.destroy()

    def test_the_plain_view_is_banded_too(self):
        """Le mode simple en a besoin depuis qu'il porte deux colonnes.

        La bande n'existait qu'en mode dédoublé, au motif qu'il a deux fois
        plus de lignes. Mais c'est en mode simple que l'œil doit relier un
        libellé à un nombre situé à l'autre bout de l'écran, et c'est là
        qu'il perd sa ligne.
        """
        from hr_analytics.ui.charts import BoxPlotChart

        chart = self.build(BoxPlotChart)
        chart.set_rows(self.rows(count=4), "EUR")
        self.root.update()
        bandes = [item for item in chart.canvas.find_all()
                  if chart.canvas.type(item) == "rectangle"
                  and chart.canvas.coords(item)[0] == 0]
        # Une ligne sur deux : quatre segments, deux bandes.
        self.assertEqual(len(bandes), 2)


@needs_display
class TestSmallCharts(ChartCase):
    """Quartiles, pyramide et tranches : trois lectures a barres."""


    def test_the_pyramid_draws_both_sexes(self):
        from hr_analytics.ui.charts import PyramidChart

        chart = self.build(PyramidChart)
        chart.set_rows([{"label": f"{20 + index * 10}-{29 + index * 10}",
                         "female": 10 + index, "male": 12 - index,
                         "count": 22} for index in range(4)])
        self.root.update()
        self.assertGreaterEqual(len(self.items(chart.canvas, "rectangle")), 8)

    def test_the_band_chart_draws_one_bar_per_band(self):
        from hr_analytics.ui.charts import BandChart

        chart = self.build(BandChart)
        chart.set_rows([{"label": f"Tranche {index}", "count": 5 + index,
                         "share": 10.0 * (index + 1)} for index in range(5)])
        self.root.update()
        self.assertGreaterEqual(len(self.items(chart.canvas, "rectangle")), 5)

    def test_an_empty_set_draws_nothing_anywhere(self):
        from hr_analytics.ui.charts import BandChart, PyramidChart

        for factory in (PyramidChart, BandChart):
            chart = self.build(factory)
            chart.set_rows([])
            self.root.update()
            self.assertEqual(self.items(chart.canvas, "rectangle"), [],
                             factory.__name__)

    def test_bars_of_zero_do_not_divide_by_zero(self):
        from hr_analytics.ui.charts import BandChart

        chart = self.build(BandChart)
        chart.set_rows([{"label": "Vide", "count": 0, "share": 0.0}])
        self.root.update()
        self.assertTrue(chart.canvas.find_all())


@needs_display
class TestLabelShortening(ChartCase):
    """Une etiquette trop longue se coupe, elle ne deborde pas."""

    def test_a_long_label_is_cut_with_an_ellipsis(self):
        from hr_analytics.ui.charts import _shorten, _text_width

        long_label = "Direction des systèmes d'information et du numérique"
        cut = _shorten(self.root, long_label, 80)
        self.assertLessEqual(_text_width(self.root, cut), 80)
        self.assertTrue(cut.endswith("…"))

    def test_a_short_label_is_left_alone(self):
        from hr_analytics.ui.charts import _shorten

        self.assertEqual(_shorten(self.root, "BU", 200), "BU")

    def test_an_impossible_width_still_returns_something(self):
        """Une colonne repliee a quelques pixels ne doit pas faire lever."""
        from hr_analytics.ui.charts import _shorten

        self.assertIsInstance(_shorten(self.root, "Direction", 1), str)


if __name__ == "__main__":
    unittest.main()




@needs_display
class TestOrgChart(ChartCase):
    """L'organigramme, relu case par case sur le canevas.

    Ce que le dessin promet et qu'il faut verifier : une case par
    responsable et une seule, un compte pour ceux qui n'encadrent personne,
    chaque parent centre sur ses enfants, et un trait de rattachement par
    case — sans quoi une case flotte sans qu'on sache de qui elle releve.
    """

    def noeud(self, cle, enfants=(), individus=0, montant=50000.0, total=10):
        return {"manager": cle, "row": 1, "job": "Poste", "level": 0,
                "direct": len(enfants) + individus, "total": total,
                "individuals": individus, "amount": montant,
                "own_amount": montant, "masked": False,
                "full_time": True, "children": list(enfants)}

    def chart(self, racine=None):
        from hr_analytics.ui.charts import OrgChart

        chart = self.build(OrgChart)
        chart.set_tree(racine if racine is not None else self.arbre())
        self.root.update()
        return chart

    def arbre(self):
        """D encadre deux chefs et quatre personnes sans equipe.

        Le melange est le cas interessant : les deux chefs font une case,
        les quatre autres un compte. Un responsable qui n'encadrerait que
        des collaborateurs n'a pas de compte a part — sa propre case porte
        deja leur nombre.
        """
        return self.noeud("D", enfants=[self.noeud("C1"), self.noeud("C2")],
                          individus=4, total=10)

    def boxes(self, chart):
        """Cases pleines, le compte des collaborateurs excepte."""
        return [item for item in self.items(chart.canvas, "rectangle")
                if not chart.canvas.itemcget(item, "dash")]

    def test_one_box_per_manager(self):
        chart = self.chart()
        self.assertEqual(len(self.boxes(chart)), 3)

    def test_those_without_a_team_are_a_counted_chip(self):
        chart = self.chart()
        pointillés = [item for item in self.items(chart.canvas, "rectangle")
                      if chart.canvas.itemcget(item, "dash")]
        self.assertEqual(len(pointillés), 1)
        self.assertIn("4 collaborateurs", self.texts(chart.canvas))

    def test_a_manager_of_nobody_but_collaborators_gets_no_chip(self):
        """Sa case porte deja leur nombre : un compte a cote le dirait deux
        fois, et ajouterait un niveau qui n'existe pas."""
        chart = self.chart(self.noeud("C", individus=6, total=6))
        self.assertEqual([item for item in self.items(chart.canvas, "rectangle")
                          if chart.canvas.itemcget(item, "dash")], [])

    def test_a_parent_sits_above_the_middle_of_its_children(self):
        """Un parent decale se lit comme s'il relevait d'une seule branche.

        Le compte des collaborateurs est un enfant comme un autre : le
        parent se centre sur l'ensemble, lui compris.
        """
        chart = self.chart()
        parent, enfants = None, []
        for item in self.items(chart.canvas, "rectangle"):
            coords = chart.canvas.coords(item)
            noeud = chart._items.get(item)
            if noeud and noeud.get("manager") == "D":
                parent = coords
            else:
                enfants.append(coords)
        self.assertIsNotNone(parent)
        self.assertEqual(len(enfants), 3)
        gauche = min(coords[0] for coords in enfants)
        droite = max(coords[2] for coords in enfants)
        self.assertAlmostEqual((parent[0] + parent[2]) / 2,
                               (gauche + droite) / 2, delta=2)

    def test_each_child_is_joined_to_its_parent(self):
        """Deux cases et un compte sous D : trois traits, pas un de moins.
        Une case sans trait flotte sans qu'on sache de qui elle releve."""
        chart = self.chart()
        self.assertEqual(len(self.items(chart.canvas, "line")), 3)

    def test_a_masked_amount_is_written_and_not_left_blank(self):
        """Une case vide se lit comme une donnee absente, pas comme un
        seuil de confidentialite."""
        racine = self.noeud("S", montant=None, total=3)
        racine["masked"] = True
        chart = self.chart(racine)
        self.assertIn("montant masqué", self.texts(chart.canvas))

    def test_the_box_carries_the_manager_own_pay_not_the_team_median(self):
        """C'est de lui qu'on parle en regardant sa case. La mediane de son
        equipe est dans l'info-bulle, ou elle ne coute pas une ligne."""
        racine = self.noeud("S", total=9)
        racine["own_amount"] = 88000.0
        racine["amount"] = 41000.0
        chart = self.chart(racine)
        textes = self.texts(chart.canvas)
        self.assertTrue(any("88" in texte for texte in textes))
        self.assertFalse(any("41" in texte for texte in textes))
        # Les deux se lisent au survol, et la mediane y est nommee.
        bulle = chart._label(racine)
        self.assertIn("88", bulle)
        self.assertIn("médiane de l'équipe", bulle)

    def test_without_a_team_it_says_what_it_waits_for(self):
        from hr_analytics.ui.charts import OrgChart

        chart = self.build(OrgChart)
        chart.set_tree(None)
        self.root.update()
        self.assertTrue(any("étape 3" in texte
                            for texte in self.texts(chart.canvas)))

    def test_a_chosen_box_is_the_only_one_marked(self):
        chart = self.chart()
        chart.select("C1")
        self.root.update()
        épais = [item for item in self.boxes(chart)
                 if float(chart.canvas.itemcget(item, "width")) > 1]
        self.assertEqual(len(épais), 1)
        self.assertEqual(chart._items[épais[0]]["manager"], "C1")

    def test_the_identity_comes_from_the_window_and_not_from_the_data(self):
        chart = self.chart()
        self.assertIn("D", self.texts(chart.canvas))
        chart.identify = lambda key: {"D": "MARTIN Claire"}.get(key, key)
        chart.redraw()
        self.root.update()
        self.assertIn("MARTIN Claire", self.texts(chart.canvas))

    def test_a_long_name_is_cut_and_never_written_over_its_neighbour(self):
        chart = self.chart()
        chart.identify = lambda key: "NOM-TRÈS-LONG-QUI-DÉBORDE " * 3
        chart.redraw()
        self.root.update()
        for item in self.items(chart.canvas, "text"):
            x1, _y1, x2, _y2 = chart.canvas.bbox(item)
            self.assertLessEqual(x2 - x1, chart.BOX_W)


@needs_display
class TestPieChart(ChartCase):
    """Le camembert de répartition, relu part par part."""

    def parts(self, *couples):
        return [{"label": libelle, "count": nombre}
                for libelle, nombre in couples]

    def chart(self, parts=None, total=None, maximum=6):
        from hr_analytics.ui.charts import PieChart

        parts = parts if parts is not None else self.parts(
            ("Ouvrier / Employé", 589), ("Agent de maîtrise", 250),
            ("Cadre", 59))
        chart = self.build(PieChart)
        chart.set_parts(parts, total if total is not None
                        else sum(p["count"] for p in parts), maximum=maximum)
        self.root.update()
        return chart

    def arcs(self, chart):
        """L'anneau est une image, pas une suite d'arcs : Tk ne lisse pas
        ses arcs, et leurs bords faisaient un escalier. Les parts se
        relisent donc sur l'objet, et le dessin sur l'image."""
        return self.items(chart.canvas, "image")

    def test_one_slice_per_value(self):
        chart = self.chart()
        self.assertEqual(len(chart.slices), 3)
        # Un seul objet dessine, et c'est l'anneau entier.
        self.assertEqual(len(self.arcs(chart)), 1)

    def test_the_slices_close_the_circle(self):
        """Un camembert dont les parts ne totalisent pas un tour est un
        camembert faux, et rien ne le signale a l'oeil."""
        chart = self.chart()
        total = sum(n for _l, n in chart.slices)
        self.assertEqual(total, sum(p["count"] for p in self.parts(
            ("Ouvrier / Employé", 589), ("Agent de maîtrise", 250),
            ("Cadre", 59))))

    def test_the_ring_is_drawn_smooth(self):
        """Le defaut qui se voyait en premier : le canevas Tk ne lisse pas
        ses arcs. L'anneau est donc une image antialiasee, comme les points
        du nuage, et ses bords portent des pixels intermediaires."""
        import base64

        from hr_analytics.ui import raster

        png = base64.b64decode(raster.ring(60, 18, [(0.5, (0, 0, 0)),
                                                    (0.5, (255, 255, 255))]))
        self.assertTrue(png.startswith(b"\x89PNG"))
        # Une image lissee porte des opacites intermediaires ; un trace a
        # l'emporte-piece n'aurait que 0 et 255.
        chart = self.chart()
        self.assertIsNotNone(chart._image)
        self.assertEqual(chart._image.width(), 2 * chart.RADIUS)

    def test_the_biggest_slice_comes_first(self):
        """L'ordre des parts n'est pas celui du fichier : on lit la plus
        grosse d'abord."""
        chart = self.chart(self.parts(("Petit", 10), ("Gros", 200),
                                      ("Moyen", 90)))
        self.assertEqual([l for l, _n in chart.slices],
                         ["Gros", "Moyen", "Petit"])

    def test_the_tail_is_grouped_beyond_the_limit(self):
        """Un camembert a quinze parts ne se lit plus, et les plus petites
        n'ont meme plus la place d'un libelle."""
        chart = self.chart(self.parts(*[(f"V{index}", 100 - index)
                                        for index in range(10)]), maximum=4)
        self.assertEqual(len(chart.slices), 5)
        self.assertTrue(chart.slices[-1][0].startswith("Autres (6 valeurs)"))
        # Le regroupement vaut la somme de ce qu'il regroupe : rien ne se
        # perd en route.
        self.assertEqual(chart.slices[-1][1],
                         sum(100 - index for index in range(4, 10)))

    def test_the_grouping_never_takes_a_real_colour(self):
        """Sinon il se lirait comme une modalite de plus."""
        from hr_analytics.core import palette
        from hr_analytics.ui import theme

        chart = self.chart(self.parts(*[(f"V{index}", 10) for index in
                                        range(8)]), maximum=3)
        couleurs = palette.series_map([l for l, _n in chart.slices],
                                      theme.ACTIVE.series,
                                      other=chart.other, neutral=theme.FAINT)
        self.assertEqual(list(couleurs.values()).count(theme.FAINT), 1)
        self.assertEqual(couleurs[chart.other], theme.FAINT)

    def test_the_centre_carries_the_headcount(self):
        """Il serait sinon a chercher ailleurs."""
        chart = self.chart(total=898)
        self.assertIn("898", self.texts(chart.canvas))
        self.assertIn("salariés", self.texts(chart.canvas))

    def test_the_legend_gives_the_count_and_the_share(self):
        """Lus dans le camembert ils se devinent ; ecrits, ils se citent."""
        textes = " ".join(self.texts(self.chart(total=898).canvas))
        self.assertIn("Cadre", textes)
        self.assertIn("59", textes)
        self.assertIn("7 %", textes)
        # Sans decimale : une part d'effectif a 6,6 % suggere une exactitude
        # que l'arrondi d'un comptage n'a pas.
        self.assertNotIn("6,6 %", textes)

    def test_a_value_at_zero_takes_no_slice(self):
        """Une part nulle dessinerait un arc d'angle nul et occuperait une
        ligne de legende pour ne rien dire."""
        chart = self.chart(self.parts(("Présent", 10), ("Absent", 0)))
        self.assertEqual([l for l, _n in chart.slices], ["Présent"])

    def test_the_hovered_slice_is_found_by_its_angle(self):
        """L'anneau est une seule image : le survol ne se lit plus sur
        l'objet pointe, il se calcule. C'est la meme trigonometrie que le
        trace, donc la meme part."""
        chart = self.chart()
        centre_x = 4 + chart.RADIUS
        centre_y = chart.winfo_height() / 2
        rayon = (chart.RADIUS + chart.HOLE) / 2
        # Juste a droite de midi : la premiere part, la plus grosse.
        self.assertEqual(chart._slice_at(centre_x + 4, centre_y - rayon)[0],
                         chart.slices[0][0])
        # Au centre, dans le trou : aucune part.
        self.assertIsNone(chart._slice_at(centre_x, centre_y))
        # Hors de l'anneau : aucune part.
        self.assertIsNone(chart._slice_at(centre_x + chart.RADIUS + 20,
                                          centre_y))

    def test_an_empty_breakdown_says_so_instead_of_drawing(self):
        chart = self.chart(self.parts())
        self.assertEqual(self.arcs(chart), [])
        self.assertIn("Aucune valeur renseignée.", self.texts(chart.canvas))

    def test_a_long_label_never_runs_into_its_count(self):
        """La legende tient dans une colonne etroite : mesuree, pas devinee."""
        chart = self.chart(self.parts(
            ("Catégorie au libellé interminable qui déborde", 10),
            ("Courte", 5)))
        canvas = chart.canvas
        for item in self.items(canvas, "text"):
            x1, _y1, x2, _y2 = canvas.bbox(item)
            self.assertLessEqual(x2, canvas.winfo_width() + 1)


@needs_display
class TestScaleChart(ChartCase):
    """L'échelle de rémunération, dessinée plutôt que tabulée."""

    def salary(self, **extra):
        base = {"min": 0.0, "p10": 30000.0, "p25": 38000.0,
                "median": 45000.0, "p50": 45000.0, "p75": 57000.0,
                "p90": 70000.0, "max": 1050000.0,
                "published_percentiles": [
                    {"key": "p10", "label": "P10"},
                    {"key": "p25", "label": "Q1 (P25)"},
                    {"key": "p50", "label": "Médiane (P50)"},
                    {"key": "p75", "label": "Q3 (P75)"},
                    {"key": "p90", "label": "P90"}]}
        base.update(extra)
        return base

    def chart(self, **extra):
        from hr_analytics.ui.charts import ScaleChart

        chart = self.build(ScaleChart)
        chart.set_salary(self.salary(**extra), "EUR")
        self.root.update()
        return chart

    def test_the_extremes_do_not_command_the_scale(self):
        """Un salarié à zéro et un contrat à un million écraseraient les
        neuf dixièmes de l'effectif sur un centimètre. Le cadrage s'arrête
        aux percentiles publiés ; les extrêmes se lisent aux deux bouts."""
        chart = self.chart()
        points = chart.points()
        self.assertEqual(points[0][2], 30000.0)
        self.assertEqual(points[-1][2], 70000.0)
        textes = " ".join(self.texts(chart.canvas))
        self.assertIn("min", textes)
        self.assertIn("max", textes)

    def test_the_box_is_the_central_half(self):
        chart = self.chart()
        boites = self.items(chart.canvas, "rectangle")
        self.assertEqual(len(boites), 1)
        x1, _y1, x2, _y2 = chart.canvas.coords(boites[0])
        self.assertLess(x1, x2)

    def test_it_draws_only_the_published_percentiles(self):
        """Le moteur calcule toujours P10 à P90 pour les ratios de
        dispersion, mais les tracer tous reviendrait à publier ce que
        l'utilisateur a retiré."""
        chart = self.chart(published_percentiles=[
            {"key": "p25", "label": "Q1 (P25)"},
            {"key": "p50", "label": "Médiane (P50)"},
            {"key": "p75", "label": "Q3 (P75)"}])
        self.assertEqual([clef for clef, _l, _v in chart.points()],
                         ["p25", "p50", "p75"])
        textes = " ".join(self.texts(chart.canvas))
        self.assertNotIn("P10", textes)
        self.assertNotIn("P90", textes)

    def test_without_both_quartiles_no_box_is_drawn(self):
        """Une boîte à un seul bord ne veut rien dire."""
        chart = self.chart(published_percentiles=[
            {"key": "p10", "label": "P10"},
            {"key": "p50", "label": "Médiane (P50)"},
            {"key": "p90", "label": "P90"}])
        self.assertEqual(self.items(chart.canvas, "rectangle"), [])

    def test_the_amounts_alternate_rows_so_they_never_collide(self):
        """Sur une grille resserrée, deux percentiles voisins tombent à
        quelques pixels l'un de l'autre."""
        chart = self.chart(p10=44000.0, p25=44500.0, median=45000.0,
                           p50=45000.0, p75=45500.0, p90=46000.0)
        boites = []
        for item in self.items(chart.canvas, "text"):
            texte = chart.canvas.itemcget(item, "text")
            if "EUR" in texte and "\n" not in texte:
                boites.append(chart.canvas.bbox(item))
        rangees = {bbox[1] for bbox in boites}
        self.assertGreaterEqual(len(rangees), 2)
        for rangee in rangees:
            sur_la_rangee = sorted(b for b in boites if b[1] == rangee)
            for premier, second in zip(sur_la_rangee, sur_la_rangee[1:]):
                self.assertLessEqual(premier[2], second[0] + 1)

    def test_a_masked_population_says_so_instead_of_drawing(self):
        from hr_analytics.ui.charts import ScaleChart

        chart = self.build(ScaleChart)
        chart.set_salary({"masked": True}, "EUR")
        self.root.update()
        self.assertIn("Les percentiles ne sont pas publiés pour cet effectif.",
                      self.texts(chart.canvas))


@needs_display
class TestTheScatterNeverShowsImpossibleValues(ChartCase):
    """Un repère qui commence sous zéro montre un quart de cadre où aucune
    donnée ne peut exister.

    La marge qui écarte les points extrêmes des bords ouvrait le cadre de
    part et d'autre sans réserve. Une rémunération, une ancienneté, un âge
    ne sont jamais négatifs.
    """

    def test_a_positive_quantity_never_opens_below_zero(self):
        from hr_analytics.ui.charts import _axis_bounds

        bas, haut = _axis_bounds(0.0, 8000.0)
        self.assertEqual(bas, 0.0)
        self.assertGreater(haut, 8000.0)

    def test_the_margin_is_kept_away_from_zero(self):
        """La règle ne vaut que pour franchir zéro : caler l'origine à zéro
        sur des salaires de 25 000 à 80 000 écraserait le nuage dans son
        tiers supérieur, et c'est justement leur écart qu'on regarde."""
        from hr_analytics.ui.charts import _axis_bounds

        bas, haut = _axis_bounds(25000.0, 80000.0)
        self.assertGreater(bas, 20000.0)
        self.assertLess(bas, 25000.0)
        self.assertGreater(haut, 80000.0)

    def test_a_quantity_that_crosses_zero_keeps_its_margin(self):
        """Une variation peut être négative : la règle ne s'applique qu'aux
        grandeurs qui ne le sont jamais."""
        from hr_analytics.ui.charts import _axis_bounds

        bas, haut = _axis_bounds(-5.0, 5.0)
        self.assertLess(bas, -5.0)
        self.assertGreater(haut, 5.0)

    def test_a_flat_series_still_gets_a_frame(self):
        """Tous au même montant : sans marge, le cadre serait d'épaisseur
        nulle et la division par son étendue lèverait."""
        from hr_analytics.ui.charts import _axis_bounds

        bas, haut = _axis_bounds(42.0, 42.0)
        self.assertLess(bas, haut)

    def test_the_drawn_chart_starts_at_the_origin(self):
        from hr_analytics.ui.charts import ScatterChart

        chart = self.build(ScatterChart)
        chart.set_dataset({
            "available": True,
            "points": [{"x": float(index), "y": float(index) * 100,
                        "group": "A", "row": index, "reference": str(index)}
                       for index in range(20)],
            "groups": ["A"], "trend": None,
            "x_axis": {"label": "Ancienneté", "kind": "years"},
            "y_axis": {"label": "Salaire de base", "kind": "money"}}, "EUR")
        self.root.update()
        x_min, _x_max, y_min, _y_max = chart._bounds
        self.assertEqual(x_min, 0.0)
        self.assertEqual(y_min, 0.0)

    def _chart(self):
        from hr_analytics.ui.charts import ScatterChart

        chart = self.build(ScatterChart)
        chart.set_dataset({
            "available": True,
            "points": [{"x": float(index), "y": float(index) * 100,
                        "group": "A", "row": index, "reference": str(index)}
                       for index in range(20)],
            "groups": ["A"], "trend": None,
            "x_axis": {"label": "Ancienneté", "kind": "years"},
            "y_axis": {"label": "Salaire de base", "kind": "money"}}, "EUR")
        self.root.update()
        return chart

    def test_dragging_never_shows_negative_values(self):
        """Le cadrage d'origine ne franchissait pas zéro, mais le
        déplacement promenait la fenêtre où il voulait : on se retrouvait à
        regarder des anciennetés négatives."""
        chart = self._chart()
        chart._drag = (500, 300, chart._view)

        class Glissement:
            x, y = 900, 60

        chart._on_drag(Glissement())
        self.root.update()
        x_min, _x_max, y_min, _y_max = chart._view
        self.assertGreaterEqual(x_min, 0.0)
        self.assertGreaterEqual(y_min, 0.0)

    def test_dragging_keeps_the_zoom_level(self):
        """On translate plutôt qu'on ne rogne : rogner changerait le niveau
        de zoom sous les doigts de l'utilisateur."""
        chart = self._chart()
        avant = chart._view
        largeur = avant[1] - avant[0]
        chart._drag = (500, 300, avant)

        class Glissement:
            x, y = 900, 60

        chart._on_drag(Glissement())
        self.root.update()
        self.assertAlmostEqual(chart._view[1] - chart._view[0], largeur,
                               places=6)

    def test_zooming_never_shows_negative_values(self):
        chart = self._chart()
        for _ in range(6):
            chart._zoom(120, 40, 1.15)
            self.root.update()
        self.assertGreaterEqual(chart._view[0], 0.0)
        self.assertGreaterEqual(chart._view[2], 0.0)

    def test_a_quantity_that_can_be_negative_keeps_its_freedom(self):
        """Une variation peut être négative : le plancher n'existe que pour
        les grandeurs qui ne le sont jamais."""
        from hr_analytics.ui.charts import ScatterChart

        chart = self.build(ScatterChart)
        chart.set_dataset({
            "available": True,
            "points": [{"x": float(index) - 10, "y": float(index) - 10,
                        "group": "A", "row": index, "reference": str(index)}
                       for index in range(20)],
            "groups": ["A"], "trend": None}, "EUR")
        self.root.update()
        self.assertEqual(chart._floors, (None, None))


@needs_display
class TestTheBoxTooltipNamesItsHalf(ChartCase):
    """Survoler la boîte des femmes donnait les chiffres de l'ensemble : la
    boîte ne retenait pas de quelle moitié elle était. On lisait donc, sous
    un curseur posé sur une moitié, les bornes de l'autre mêlées aux
    siennes — et il fallait deviner.

    La bulle rend une structure — titre, colonnes, lignes, colonne
    marquée — et c'est la grille qui l'aligne. Elle était composée en
    texte à chasse fixe, et toute sa lisibilité dépendait d'une police
    que personne ne lit volontiers."""

    def setUp(self):
        from hr_analytics.ui.charts import BoxPlotChart

        super().setUp()
        self.chart = self.build(BoxPlotChart)

    def _ligne(self):
        def bloc(base):
            return {"p10": base, "p25": base + 500, "median": base + 1000,
                    "p75": base + 1800, "p90": base + 2600,
                    "masked": False}
        return {"segment": "Toute la population", "headcount": 300,
                "salary": bloc(30000), "female": bloc(28000),
                "male": bloc(32000), "female_count": 120, "male_count": 180,
                "female_chartable": True, "male_chartable": True,
                "chartable": True, "sex_chartable": True, "masked": False,
                "median_gap": 12.5}

    def _cellules(self, bulle):
        return [cellule for _intitule, cellules in bulle["lignes"]
                for cellule in cellules]

    def test_each_box_remembers_which_half_it_is(self):
        self.chart.set_split(True)
        self.chart.set_rows([self._ligne()], "EUR")
        self.root.update()
        moitiés = {moitié for _row, moitié in self.chart._items.values()}
        self.assertEqual(moitiés, {"female", "male"})

    def _survoler(self, canvas, x, y):
        class Ev:
            pass
        ev = Ev()
        ev.x, ev.y = int(x), int(y)
        return ev

    def test_the_gap_gutter_explains_itself(self):
        """« +12,4 % » se lit comme un fait, mais un fait sur quoi ? Le
        texte est celui du glossaire : l'écran et le rapport parlent du
        même calcul."""
        self.chart.set_split(True)
        self.chart.set_rows([self._ligne()], "EUR")
        self.root.update()
        largeur = self.chart.canvas.winfo_width()
        self.chart._on_motion(self._survoler(self.chart.canvas, largeur - 10, 40))
        self.root.update()
        texte = self.chart.tooltip.texte()
        self.assertIn("Écart F/H", texte)
        self.assertIn("Médiane des hommes", texte)
        self.assertIn("Calcul :", texte)

    def test_the_header_word_explains_itself_too(self):
        self.chart.set_split(True)
        self.chart.set_rows([self._ligne()], "EUR")
        self.root.update()
        largeur = self.chart.canvas.winfo_width()
        self.chart._on_header_motion(
            self._survoler(self.chart.header, largeur - 10, 12))
        self.root.update()
        self.assertIn("Écart F/H", self.chart.tooltip.texte())
        self.chart._on_header_motion(self._survoler(self.chart.header, 20, 12))
        self.root.update()
        self.assertEqual(self.chart.tooltip.window.state(), "withdrawn")

    def test_without_the_split_the_gutter_is_an_ordinary_place(self):
        self.chart.set_split(False)
        self.chart.set_rows([self._ligne()], "EUR")
        self.root.update()
        largeur = self.chart.canvas.winfo_width()
        self.chart._on_motion(self._survoler(self.chart.canvas, largeur - 10, 40))
        self.root.update()
        self.assertNotIn("Médiane des hommes", self.chart.tooltip.texte())

    def test_the_tooltip_carries_all_three_columns(self):
        bulle = self.chart._bulle(self._ligne(), "female")
        self.assertEqual(bulle["colonnes"], ["Ensemble", "Femmes", "Hommes"])
        # Les trois médianes, et pas une seule répétée trois fois.
        from hr_analytics.core.reporting import format_money

        mediane = dict(bulle["lignes"])["Médiane"]
        self.assertEqual(mediane, [format_money(base, "EUR")
                                   for base in (31000, 29000, 33000)])

    def test_the_hovered_column_is_marked(self):
        ligne = self._ligne()
        self.assertEqual(self.chart._bulle(ligne, "female")["marque"], 1)
        self.assertEqual(self.chart._bulle(ligne, "male")["marque"], 2)
        # Le groupe entier survolé marque sa propre colonne.
        self.assertEqual(self.chart._bulle(ligne, None)["marque"], 0)

    def test_the_headcounts_open_the_table(self):
        """L'effectif se lit avant les bornes, et non après : un P10 calculé
        sur douze personnes ne se lit pas comme un P10."""
        bulle = self.chart._bulle(self._ligne(), "female")
        intitule, cellules = bulle["lignes"][0]
        self.assertEqual(intitule, "Effectif")
        self.assertEqual(cellules, ["300", "120", "180"])

    def test_the_bounds_climb_the_scale(self):
        """Du bas de la distribution vers le haut : c'est le sens d'une
        échelle de rémunération, celui de la boîte lue de gauche à droite,
        et celui de tous les tableaux de l'outil."""
        bulle = self.chart._bulle(self._ligne(), "female")
        self.assertEqual([intitule for intitule, _c in bulle["lignes"][1:]],
                         ["P10", "Q1", "Médiane", "Q3", "P90"])

    def test_a_masked_half_leaves_its_column_out(self):
        """Un côté sous le seuil de publication n'a pas de colonne : une
        colonne de tirets laisserait croire qu'on a mesuré."""
        ligne = self._ligne()
        ligne["female"] = {"masked": True}
        bulle = self.chart._bulle(ligne, None)
        self.assertEqual(bulle["colonnes"], ["Ensemble", "Hommes"])
        self.assertTrue(all(len(cellules) == 2
                            for _i, cellules in bulle["lignes"]))

    def test_nothing_publishable_gives_no_tooltip(self):
        ligne = self._ligne()
        for cle in ("salary", "female", "male"):
            ligne[cle] = {"masked": True}
        self.assertIsNone(self.chart._bulle(ligne, None))

    def _montrer(self, moitie="female"):
        self.chart.tooltip.show_table(self.chart._bulle(self._ligne(), moitie),
                                      100, 100)
        self.root.update()
        return self.chart.tooltip

    def test_the_columns_line_up_by_the_grid(self):
        """Trois colonnes de montants qui ne s'alignent pas ne se comparent
        pas. L'alignement tient à la grille, et plus à une police à chasse
        fixe : chaque cellule d'une même colonne finit au même pixel."""
        bulle = self._montrer()
        bords = {}
        for enfant in bulle.table.winfo_children():
            infos = enfant.grid_info()
            colonne = int(infos.get("column", 0))
            if colonne == 0 or int(infos.get("row", 0)) < 2:
                continue
            bords.setdefault(colonne, set()).add(
                enfant.winfo_x() + enfant.winfo_width())
        self.assertEqual(len(bords), 3)
        for colonne, droites in bords.items():
            self.assertEqual(len(droites), 1,
                             f"colonne {colonne} : bords {droites}")

    def test_the_tooltip_is_dark_on_light(self):
        """Blanche sur fond sombre et en petit corps, elle ne se lisait
        pas sans se pencher."""
        from hr_analytics.ui import theme

        bulle = self._montrer()
        self.assertEqual(bulle.table.cget("background"), theme.CANVAS)
        encres = {enfant.cget("foreground")
                  for enfant in bulle.table.winfo_children()}
        self.assertIn(theme.INK, encres)

    def test_the_hovered_column_shows_in_the_accent_colour(self):
        from hr_analytics.ui import theme

        bulle = self._montrer("male")
        entetes = {enfant.cget("text"): enfant.cget("foreground")
                   for enfant in bulle.table.winfo_children()
                   if int(enfant.grid_info().get("row", 0)) == 1}
        self.assertEqual(entetes["Hommes"], theme.ACCENT)
        self.assertNotEqual(entetes["Femmes"], theme.ACCENT)

    def test_the_tooltip_is_not_rebuilt_on_every_pixel(self):
        """Le survol envoie un événement par pixel ; vingt étiquettes
        refaites à chaque fois se voient."""
        bulle = self._montrer()
        avant = tuple(bulle.table.winfo_children())
        bulle.show_table(self.chart._bulle(self._ligne(), "female"), 101, 101)
        self.root.update()
        self.assertEqual(tuple(bulle.table.winfo_children()), avant)

    def test_the_tooltip_stays_on_the_screen(self):
        """Posée à droite d'une boîte proche du bord, elle sortait de
        l'écran, et c'est la colonne survolée — la dernière — qu'on
        perdait."""
        bulle = self.chart.tooltip
        bulle.show_table(self.chart._bulle(self._ligne(), "male"),
                         self.root.winfo_screenwidth() - 20, 100)
        self.root.update()
        droite = bulle.window.winfo_x() + bulle.window.winfo_reqwidth()
        self.assertLessEqual(droite, self.root.winfo_screenwidth())
        self.assertLess(bulle.window.winfo_x(),
                        self.root.winfo_screenwidth() - 20)

    def test_the_text_rendering_says_what_the_eye_reads(self):
        texte = self._montrer().texte()
        for attendu in ("Toute la population", "Ensemble", "Effectif",
                        "Médiane", "300"):
            self.assertIn(attendu, texte)


@needs_display
class TestVerticalBoxPlot(ChartCase):
    """Les boîtes dressées : une colonne par catégorie.

    L'autre presentation des memes chiffres. La remuneration en ordonnee,
    les categories cote a cote : c'est la lecture classique d'une
    distribution comparee, et elle dit d'un regard ce qui se superpose et
    ce qui ne se superpose pas.
    """

    def rows(self, count=4, chartable=True, labels=None):
        made = []
        for index in range(count):
            salary = {"median": 40000 + index * 2000,
                      "p25": 36000 + index * 2000,
                      "p75": 46000 + index * 2000,
                      "p10": 32000 + index * 2000,
                      "p90": 52000 + index * 2000, "count": 30}
            made.append({
                "segment": (labels[index] if labels
                            else f"Catégorie {index}"),
                "headcount": 30 + index, "masked": False,
                "chartable": chartable, "salary": salary})
        return made

    def chart(self, rows=None, **kwargs):
        from hr_analytics.ui.charts import VerticalBoxPlotChart

        chart = self.build(VerticalBoxPlotChart)
        chart.set_rows(rows if rows is not None else self.rows(), **kwargs)
        self.root.update()
        return chart

    def rectangles(self, chart):
        return self.items(chart.canvas, "rectangle")

    def test_one_box_per_category(self):
        chart = self.chart()
        self.assertEqual(len(chart._items), 4)

    def test_a_category_below_the_chart_threshold_is_not_drawn(self):
        """Le drapeau vient du moteur, et son absence vaut refus : une
        regle de confidentialite ne se decide pas dans un graphique."""
        rows = self.rows()
        del rows[1]["chartable"]
        self.assertEqual(len(self.chart(rows)._items), 3)

    def test_a_masked_category_is_never_drawn(self):
        rows = self.rows()
        rows[0]["masked"] = True
        self.assertEqual(len(self.chart(rows)._items), 3)

    def test_nothing_drawable_gives_a_sentence_and_no_box(self):
        chart = self.chart(self.rows(chartable=False))
        self.assertEqual(len(chart._items), 0)
        self.assertIn("insuffisant", " ".join(self.texts(chart.canvas)))

    def test_no_category_at_all_says_so(self):
        chart = self.chart([])
        self.assertIn("Aucun segment", " ".join(self.texts(chart.canvas)))

    def test_the_value_axis_is_named_by_the_engine(self):
        """Le paragraphe 7 interdit d'ecrire le nom d'un champ dans le
        code : l'axe porte ce que la configuration a designe comme champ
        d'analyse, et le moteur le transmet."""
        chart = self.chart(value_label="Salaire de base")
        self.assertIn("Salaire de base", self.texts(chart.axis))

    def test_the_axis_shows_the_scale(self):
        chart = self.chart()
        montants = [texte for texte in self.texts(chart.axis) if "EUR" in texte]
        self.assertGreaterEqual(len(montants), 2)

    def test_the_headcount_is_written_under_each_box(self):
        """Une boite tracee sur douze salaries a la meme allure qu'une
        boite tracee sur quatre cents."""
        chart = self.chart()
        textes = self.texts(chart.canvas)
        for effectif in ("30", "31", "32", "33"):
            self.assertIn(effectif, textes)

    def test_each_category_is_named(self):
        chart = self.chart()
        textes = self.texts(chart.canvas)
        for index in range(4):
            self.assertIn(f"Catégorie {index}", textes)

    def test_the_columns_fill_the_width(self):
        """Plafonner la colonne laissait quatre boites serrees a gauche
        devant la moitie d'un ecran vide."""
        chart = self.chart()
        centres = sorted((chart.canvas.coords(item)[0]
                          + chart.canvas.coords(item)[2]) / 2
                         for item in chart._items)
        largeur = chart.canvas.winfo_width()
        self.assertGreater(centres[-1], largeur * 0.6)

    def test_many_categories_make_the_zone_scroll(self):
        """Ecarter des categories faute de place reviendrait a cacher une
        partie de la reponse : la zone defile."""
        chart = self.chart(self.rows(count=40))
        region = [float(value)
                  for value in chart.canvas.cget("scrollregion").split()]
        self.assertGreater(region[2], chart.canvas.winfo_width())
        self.assertEqual(len(chart._items), 40)

    def test_short_labels_stay_upright(self):
        chart = self.chart(self.rows(labels=["Nord", "Sud", "Est", "Ouest"]))
        angles = {chart.canvas.itemcget(item, "angle")
                  for item in self.items(chart.canvas, "text")
                  if chart.canvas.itemcget(item, "text") == "Nord"}
        self.assertEqual(angles, {"0.0"})

    def test_labels_that_do_not_fit_are_tilted(self):
        """Dresses a la verticale, on lit un nom a la fois en tournant la
        tete ; inclines, la serie se parcourt."""
        chart = self.chart(self.rows(count=30))
        angles = {chart.canvas.itemcget(item, "angle")
                  for item in self.items(chart.canvas, "text")
                  if chart.canvas.itemcget(item, "text").startswith("Catégorie")}
        self.assertEqual(angles, {"45.0"})

    def test_the_reference_line_is_drawn_when_given(self):
        """La mediane d'ensemble, en pointilles : un repere dessine se lit
        mieux qu'un montant a comparer de tete avec douze boites."""
        chart = self.chart()
        self.assertEqual(self.dashed(chart), 0)
        chart.set_rows(self.rows(), reference=45000)
        self.root.update()
        self.assertEqual(self.dashed(chart), 1)

    def dashed(self, chart):
        return sum(1 for item in self.items(chart.canvas, "line")
                   if chart.canvas.itemcget(item, "dash"))

    def test_the_order_can_be_changed_without_losing_a_category(self):
        chart = self.chart()
        for key in ("median", "headcount"):
            chart.set_order(key)
            self.root.update()
            self.assertEqual(len(chart._items), 4)

    def test_the_withheld_categories_are_announced(self):
        rows = self.rows(count=5)
        del rows[4]["chartable"]
        chart = self.chart(rows)
        self.assertIn("1 catégorie(s) trop peu nombreuse(s)",
                      " ".join(self.texts(chart.footer)))

    def test_hovering_a_box_gives_its_figures(self):
        from hr_analytics.ui.charts import VerticalBoxPlotChart

        chart = self.chart()
        item = next(iter(chart._items))
        x1, y1, x2, y2 = chart.canvas.coords(item)
        chart._on_motion(Motion(int((x1 + x2) / 2), int((y1 + y2) / 2)))
        self.root.update()
        self.assertIsNotNone(chart.tooltip.window)
        self.assertIn("Médiane", chart.tooltip.texte())

    def test_it_reads_the_same_rows_as_the_lying_boxes(self):
        """Un chiffre affiche a deux endroits doit venir du meme calcul :
        les deux presentations partagent leurs regles, et non une copie."""
        from hr_analytics.ui.charts import BoxPlotChart, VerticalBoxPlotChart

        rows = self.rows(count=6)
        del rows[2]["chartable"]
        rows[4]["masked"] = True
        couchees = self.build(BoxPlotChart)
        couchees.set_rows(rows)
        dressees = self.build(VerticalBoxPlotChart)
        dressees.set_rows(rows)
        # Les deux s'ouvrent sur un ordre different — c'est voulu, et c'est
        # une autre regle. Sous le meme tri, elles doivent retenir les
        # memes lignes, dans le meme ordre.
        for graphique in (couchees, dressees):
            graphique.set_order("median")
        self.root.update()
        self.assertEqual([row["segment"] for row in couchees._drawable()],
                         [row["segment"] for row in dressees._drawable()])


@needs_display
class TestTheOrderOfTheColumns(ChartCase):
    """L'ordre des catégories en abscisse.

    Une abscisse peut etre une echelle — un coefficient, une tranche
    d'age, un niveau G1..G8 — et le moteur sait la ranger : tranches dans
    l'ordre declare, echelles numerotees dans l'ordre des nombres, le
    reste dans l'ordre choisi a l'onglet Apparence. Le graphique rangeait
    tout par effectif decroissant, ce qui defait la progression meme qu'on
    vient lire.
    """

    def rows(self, segments, effectifs=None, medianes=None):
        faites = []
        for index, nom in enumerate(segments):
            mediane = (medianes[index] if medianes
                       else 40000 + index * 1000)
            faites.append({
                "segment": nom,
                "headcount": (effectifs[index] if effectifs else 30 + index),
                "masked": False, "chartable": True,
                "salary": {"median": mediane, "p25": mediane - 4000,
                           "p75": mediane + 4000, "p10": mediane - 8000,
                           "p90": mediane + 8000, "count": 30}})
        return faites

    def chart(self, rows, ordre=None):
        from hr_analytics.ui.charts import VerticalBoxPlotChart

        graphique = self.build(VerticalBoxPlotChart)
        if ordre:
            graphique.set_order(ordre)
        graphique.set_rows(rows)
        self.root.update()
        return graphique

    def ordre_trace(self, graphique):
        """Les segments dans l'ordre ou les colonnes sont posees."""
        colonnes = sorted(
            ((graphique.canvas.coords(item)[0], ligne["segment"])
             for item, (ligne, _moitié) in graphique._items.items()))
        return [nom for _x, nom in colonnes]

    #: Une echelle : l'ordre des nombres n'est ni l'alphabetique — « 100,
    #: 1000, 110 » — ni l'effectif.
    ECHELLE = ["100", "110", "120", "200"]

    def test_the_engine_order_is_the_default(self):
        graphique = self.chart(self.rows(self.ECHELLE, effectifs=[5, 90, 9, 50]))
        self.assertEqual(graphique.order, "moteur")
        self.assertEqual(self.ordre_trace(graphique), self.ECHELLE)

    def test_the_engine_order_does_not_resort(self):
        """Le moteur a range les lignes avant de les passer : le graphique
        les rend telles quelles, et c'est le seul moyen de retrouver une
        tranche d'âge dans l'ordre des tranches."""
        lignes = self.rows(["50-59", "40-49", "30-39", "20-29"],
                           effectifs=[12, 80, 40, 95])
        graphique = self.chart(lignes)
        self.assertEqual(self.ordre_trace(graphique),
                         ["50-59", "40-49", "30-39", "20-29"])

    def test_the_headcount_order_is_still_available(self):
        graphique = self.chart(self.rows(self.ECHELLE,
                                         effectifs=[5, 90, 9, 50]),
                               ordre="headcount")
        self.assertEqual(self.ordre_trace(graphique), ["110", "200", "120", "100"])

    def test_the_rising_median_draws_a_staircase(self):
        """La présentation classique d'une distribution comparée : on voit
        d'un trait où se situe chaque catégorie."""
        lignes = self.rows(["A", "B", "C"], medianes=[50000, 30000, 40000])
        graphique = self.chart(lignes, ordre="median_asc")
        self.assertEqual(self.ordre_trace(graphique), ["B", "C", "A"])

    def test_the_falling_median_answers_the_other_question(self):
        lignes = self.rows(["A", "B", "C"], medianes=[50000, 30000, 40000])
        graphique = self.chart(lignes, ordre="median")
        self.assertEqual(self.ordre_trace(graphique), ["A", "C", "B"])

    def test_the_alphabetical_order_ignores_accents_and_case(self):
        """« Édition » se range entre « Diffusion » et « Expédition », et
        non après « Zone » comme le fait un tri brut sur les points de
        code."""
        lignes = self.rows(["Zone", "expédition", "Édition", "Diffusion"])
        graphique = self.chart(lignes, ordre="alphabetique")
        self.assertEqual(self.ordre_trace(graphique),
                         ["Diffusion", "Édition", "expédition", "Zone"])

    def test_an_unknown_order_falls_back_on_the_default(self):
        graphique = self.chart(self.rows(self.ECHELLE), ordre="n_importe_quoi")
        self.assertEqual(graphique.order, "moteur")

    def test_the_two_presentations_open_on_their_own_order(self):
        """Dressée, l'abscisse peut être une échelle ; couchée, on cherche
        d'abord ce qui pèse dans une liste de quarante postes."""
        from hr_analytics.ui.charts import BoxPlotChart, VerticalBoxPlotChart

        self.assertEqual(VerticalBoxPlotChart.DEFAUT, "moteur")
        self.assertEqual(BoxPlotChart.DEFAUT, "headcount")

    def test_every_offered_order_is_applied(self):
        """Le témoin : une entrée de la liste qu'aucune branche ne traite
        rendrait les lignes inchangées, et la liste mentirait."""
        from hr_analytics.ui.charts import VerticalBoxPlotChart

        # Effectifs et medianes choisis pour que les cinq ordres donnent
        # cinq rangements differents : sans cela, deux entrees se
        # confondraient par hasard et le temoin ne temoignerait de rien.
        lignes = self.rows(["Zone", "Alpha", "Mu"], effectifs=[90, 10, 50],
                           medianes=[40000, 30000, 50000])
        graphique = self.chart(lignes)
        rendus = {}
        for cle, _libelle in VerticalBoxPlotChart.ORDERS:
            graphique.set_order(cle)
            self.root.update()
            rendus[cle] = tuple(self.ordre_trace(graphique))
            self.assertEqual(len(rendus[cle]), 3, cle)
        self.assertEqual(len(set(rendus.values())), len(rendus), rendus)
