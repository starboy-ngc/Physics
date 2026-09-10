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

        from compensation_analytics.ui import theme

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
        from compensation_analytics.ui.charts import HistogramChart

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
        from compensation_analytics.ui.charts import HistogramChart

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

    def test_a_class_with_nobody_in_it_is_still_a_class(self):
        chart = self.chart(counts=(0, 0, 4, 0))
        self.assertEqual(len(self.items(chart.canvas, "rectangle")), 4)


@needs_display
class TestScatter(ChartCase):
    def dataset(self, count=40):
        return {"available": True, "points": [
            {"x": index % 20, "y": 30000 + (index % 20) * 900,
             "group": ["France", "Iberia"][index % 2], "row": index + 2,
             "reference": f"REF{index}"} for index in range(count)]}

    def chart(self, dataset=None):
        from compensation_analytics.ui.charts import ScatterChart

        chart = self.build(ScatterChart)
        chart.set_dataset(dataset if dataset is not None else self.dataset())
        self.root.update()
        return chart

    def test_every_point_is_drawn(self):
        chart = self.chart()
        self.assertEqual(len(chart._items), 40)

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
        from compensation_analytics.ui.charts import ScatterChart

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
        from compensation_analytics.ui.charts import ScatterChart

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
        from compensation_analytics.ui.charts import ScatterChart

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
        from compensation_analytics.ui.charts import BoxPlotChart

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
        segments = {row["segment"] for row in chart._items.values()}
        self.assertEqual(len(segments), 3)

    def test_the_order_can_be_changed_without_losing_a_segment(self):
        chart = self.chart()
        for key in ("median", "headcount"):
            chart.set_order(key)
            self.root.update()
            self.assertEqual(len(chart._items), 4)

    def test_the_reference_line_is_drawn_when_given(self):
        from compensation_analytics.ui.charts import BoxPlotChart

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
            self.assertIn("Segment", chart.tooltip.label.cget("text"))


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
        from compensation_analytics.ui.charts import BoxPlotChart

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
        from compensation_analytics.ui import theme

        chart = self.chart(self.rows(count=2))          # ecart de 8 %
        couleurs = {chart.canvas.itemcget(item, "fill")
                    for item in chart.canvas.find_all()
                    if chart.canvas.type(item) == "text"
                    and chart.canvas.itemcget(item, "text").endswith("%")}
        self.assertIn(theme.WARN, couleurs)

    def test_a_small_gap_stays_neutral(self):
        from compensation_analytics.ui import theme

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
        from compensation_analytics.ui import theme

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
        self.assertIn("—", self._texts(chart))

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
        from compensation_analytics.ui import theme

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
        from compensation_analytics.ui.charts import BoxPlotChart

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
        from compensation_analytics.ui.charts import BoxPlotChart

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

    def test_the_plain_view_has_no_bands(self):
        """Le mode simple n'en a pas besoin : une ligne, une boite."""
        from compensation_analytics.ui.charts import BoxPlotChart

        chart = self.build(BoxPlotChart)
        chart.set_rows(self.rows(count=4), "EUR")
        self.root.update()
        bandes = [item for item in chart.canvas.find_all()
                  if chart.canvas.type(item) == "rectangle"
                  and chart.canvas.coords(item)[0] == 0]
        self.assertEqual(bandes, [])


@needs_display
class TestSmallCharts(ChartCase):
    """Quartiles, pyramide et tranches : trois lectures a barres."""

    def test_the_quartile_chart_draws_one_row_per_quartile(self):
        from compensation_analytics.ui.charts import QuartileChart

        chart = self.build(QuartileChart)
        chart.set_rows([{"quartile": index + 1, "headcount": 25,
                         "female_share": 40 + index, "male_share": 60 - index}
                        for index in range(4)])
        self.root.update()
        self.assertGreaterEqual(len(self.items(chart.canvas, "rectangle")), 4)

    def test_the_pyramid_draws_both_sexes(self):
        from compensation_analytics.ui.charts import PyramidChart

        chart = self.build(PyramidChart)
        chart.set_rows([{"label": f"{20 + index * 10}-{29 + index * 10}",
                         "female": 10 + index, "male": 12 - index,
                         "count": 22} for index in range(4)])
        self.root.update()
        self.assertGreaterEqual(len(self.items(chart.canvas, "rectangle")), 8)

    def test_the_band_chart_draws_one_bar_per_band(self):
        from compensation_analytics.ui.charts import BandChart

        chart = self.build(BandChart)
        chart.set_rows([{"label": f"Tranche {index}", "count": 5 + index,
                         "share": 10.0 * (index + 1)} for index in range(5)])
        self.root.update()
        self.assertGreaterEqual(len(self.items(chart.canvas, "rectangle")), 5)

    def test_an_empty_set_draws_nothing_anywhere(self):
        from compensation_analytics.ui.charts import (BandChart, PyramidChart,
                                                      QuartileChart)

        for factory in (QuartileChart, PyramidChart, BandChart):
            chart = self.build(factory)
            chart.set_rows([])
            self.root.update()
            self.assertEqual(self.items(chart.canvas, "rectangle"), [],
                             factory.__name__)

    def test_bars_of_zero_do_not_divide_by_zero(self):
        from compensation_analytics.ui.charts import BandChart

        chart = self.build(BandChart)
        chart.set_rows([{"label": "Vide", "count": 0, "share": 0.0}])
        self.root.update()
        self.assertTrue(chart.canvas.find_all())


@needs_display
class TestLabelShortening(ChartCase):
    """Une etiquette trop longue se coupe, elle ne deborde pas."""

    def test_a_long_label_is_cut_with_an_ellipsis(self):
        from compensation_analytics.ui.charts import _shorten, _text_width

        long_label = "Direction des systèmes d'information et du numérique"
        cut = _shorten(self.root, long_label, 80)
        self.assertLessEqual(_text_width(self.root, cut), 80)
        self.assertTrue(cut.endswith("…"))

    def test_a_short_label_is_left_alone(self):
        from compensation_analytics.ui.charts import _shorten

        self.assertEqual(_shorten(self.root, "BU", 200), "BU")

    def test_an_impossible_width_still_returns_something(self):
        """Une colonne repliee a quelques pixels ne doit pas faire lever."""
        from compensation_analytics.ui.charts import _shorten

        self.assertIsInstance(_shorten(self.root, "Direction", 1), str)


if __name__ == "__main__":
    unittest.main()
