"""La page Pay Transparency, telle qu'on s'en sert.

C'est la page ou l'on decide : quel poste porte l'ecart, combien il coute a
rattraper, et sur quelles variables les deux sexes different. Ses reglages —
l'axe, l'axe croise, l'ordre, la fiche d'un poste — sont autant de facons de
se tromper de lecture. Aucun n'etait verifie.

Une regle tient toute la page : les seuils de confidentialite viennent du
moteur, jamais de la vue. Un poste sans les deux sexes en nombre suffisant
doit rester masque quel que soit le reglage.

Ces tests exigent un affichage ; ils sont ignores automatiquement sans lui.
Aucune donnee RH reelle.
"""

import csv
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, make_row

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
    _display_answers(), "aucun affichage disponible (test d'interface ignoré)")

POSTES = ["Comptable", "Technicien", "Chef de projet"]


@needs_display
class PayTransparencyCase(unittest.TestCase):
    """Une population ou l'ecart existe et se laisse publier."""

    def setUp(self):
        from compensation_analytics.ui.app import Application

        self.directory = tempfile.mkdtemp()
        self.source = os.path.join(self.directory, "p.csv")
        with open(self.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste"])
            for index in range(120):
                poste = POSTES[index % 3]
                femme = (index // 3) % 2 == 0
                # Un ecart net et volontaire, pour qu'il y ait quelque chose
                # a lire : les femmes 8 % en dessous, a poste egal.
                base = 40000 + POSTES.index(poste) * 9000
                writer.writerow(list(make_row(
                    index, salary=round(base * (0.92 if femme else 1.0)),
                    gender="F" if femme else "H",
                    business_unit=["France", "Iberia"][index % 2],
                    grade=f"G{4 + (index // 6) % 2}")) + [poste])
        self.app = Application()
        self.app.geometry("1400x900+0+0")
        self.app.update()
        from compensation_analytics.core.pipeline import load_population

        population, mapping, table = load_population(self.source,
                                                     self.app.configuration)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app.headers = list(table.headers)
        self.app._populate_filters()
        self.app.run_analysis()
        limit = time.time() + 60
        while self.app.result is None and time.time() < limit:
            self.app.update()
            time.sleep(0.02)
        for _ in range(20):
            self.app.update()
            time.sleep(0.01)
        self.assertIsNotNone(self.app.result)
        self.app.tabbar.select("equite")
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def categories(self):
        return [item["category"] for item in self.app._categories]

    def select(self, position=0):
        children = self.app.category_tree.get_children()
        self.app.category_tree.selection_set(children[position])
        self.app.update()


class TestTheList(PayTransparencyCase):
    def test_the_list_holds_one_line_per_position(self):
        self.assertEqual(sorted(self.categories()), sorted(POSTES))

    def test_the_axis_can_be_changed(self):
        wanted = self.app._category_fields.index("grade")
        self.app.category_choice.current(wanted)
        self.app._show_categories()
        self.app.update()
        self.assertTrue(all(value.startswith("G")
                            for value in self.categories()), self.categories())

    def test_two_axes_can_be_crossed(self):
        """« Poste + Grade » : un comptable senior G5 et un comptable senior
        G7 ne font pas le meme travail, et les confondre dilue l'ecart."""
        wanted = self.app._category_fields.index("grade")
        self.app.category_cross.current(wanted + 1)
        self.app._show_categories()
        self.app.update()
        self.assertTrue(any(" · " in value for value in self.categories()),
                        self.categories())

    def test_the_sex_is_never_offered_as_an_axis(self):
        """Croiser l'ecart entre sexes par le sexe donnerait des categories
        d'un seul sexe, toutes masquees."""
        self.assertNotIn("gender", self.app._category_fields)

    def test_each_order_reorders_without_losing_anything(self):
        from compensation_analytics.ui.app import CATEGORY_ORDERS

        for position in range(len(CATEGORY_ORDERS)):
            self.app.category_order.current(position)
            self.app._show_categories()
            self.app.update()
            self.assertEqual(sorted(self.categories()), sorted(POSTES),
                             CATEGORY_ORDERS[position][0])

    def test_ordering_by_name_is_alphabetical(self):
        from compensation_analytics.ui.app import CATEGORY_ORDERS

        position = [key for key, _label in CATEGORY_ORDERS].index("name")
        self.app.category_order.current(position)
        self.app._show_categories()
        self.app.update()
        self.assertEqual(self.categories(), sorted(POSTES, key=str.lower))

    def test_ordering_by_headcount_puts_the_largest_first(self):
        from compensation_analytics.ui.app import CATEGORY_ORDERS

        position = [key for key, _label in CATEGORY_ORDERS].index("headcount")
        self.app.category_order.current(position)
        self.app._show_categories()
        self.app.update()
        counts = [item["female_count"] + item["male_count"]
                  for item in self.app._categories]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_an_unpublishable_category_stays_at_the_bottom(self):
        """Sa place dans un classement par ecart serait arbitraire, puisque
        l'ecart n'est precisement pas connu."""
        published = [item.get("published") for item in self.app._categories]
        self.assertEqual(published, sorted(published, reverse=True))


class TestTheProfile(PayTransparencyCase):
    def test_selecting_a_position_fills_its_card(self):
        self.select()
        self.assertTrue(self.app.profile_title.cget("text"))
        self.assertIn(self.app.profile_title.cget("text"), POSTES)

    def test_the_card_compares_the_declared_variables(self):
        """Plusieurs variables, pas seulement le salaire de base : c'est ce
        qui permet de voir d'ou vient un ecart."""
        self.select()
        lignes = self.app.profile_tree.get_children()
        self.assertGreaterEqual(len(lignes), 3)
        libelles = [self.app.profile_tree.item(ligne)["values"][0]
                    for ligne in lignes]
        self.assertIn("Salaire de base", libelles)

    def test_the_card_shows_both_sexes(self):
        self.select()
        headings = [self.app.profile_tree.heading(column)["text"]
                    for column in self.app.profile_tree["columns"]]
        joined = " ".join(headings).lower()
        self.assertIn("femme", joined)
        self.assertIn("homme", joined)

    def test_changing_the_selection_changes_the_card(self):
        self.select(0)
        first = self.app.profile_title.cget("text")
        self.select(1)
        self.assertNotEqual(self.app.profile_title.cget("text"), first)

    def test_changing_the_axis_moves_the_card_to_the_new_axis(self):
        """La fiche d'un poste n'a plus de sens quand la liste montre des
        grades : la laisser affichee ferait lire un ecart sous un mauvais
        intitule. Elle suit donc l'axe."""
        self.select()
        self.assertIn(self.app.profile_title.cget("text"), POSTES)
        wanted = self.app._category_fields.index("grade")
        self.app.category_choice.current(wanted)
        self.app._show_categories()
        self.app.update()
        titre = self.app.profile_title.cget("text")
        self.assertNotIn(titre, POSTES)
        self.assertIn(titre, self.categories())

    def test_the_card_carries_no_name(self):
        self.select()
        lignes = [self.app.profile_tree.item(ligne)["values"]
                  for ligne in self.app.profile_tree.get_children()]
        texte = " ".join(str(value) for ligne in lignes for value in ligne)
        self.assertNotIn("NOM", texte)


class TestTheHeader(PayTransparencyCase):
    def test_the_overall_gap_is_shown(self):
        texts = self._kpi_texts()
        self.assertTrue(any("global" in text.lower() for text in texts), texts)

    def _kpi_texts(self):
        found = []

        def walk(widget):
            for child in widget.winfo_children():
                if isinstance(child, tkinter.Label):
                    found.append(child.cget("text"))
                walk(child)

        walk(self.app.equity_frame)
        return found

    def test_the_header_follows_the_axis(self):
        """L'ecart d'un axe se retrouvait au-dessus de la liste d'un
        autre."""
        before = self._kpi_texts()
        wanted = self.app._category_fields.index("grade")
        self.app.category_choice.current(wanted)
        self.app._show_categories()
        self.app.update()
        self.assertNotEqual(self._kpi_texts(), before)

    def test_the_structure_effect_is_named(self):
        """L'ecart global moins l'ecart a poste comparable : c'est ce qui
        distingue « on paie moins » de « elles occupent d'autres postes »."""
        texts = " ".join(self._kpi_texts()).lower()
        self.assertIn("structure", texts)


@needs_display
class TestWithoutAnyGap(unittest.TestCase):
    """Un fichier sans sexe renseigne : la page doit le dire, pas mentir."""

    def setUp(self):
        from compensation_analytics.ui.app import Application

        directory = tempfile.mkdtemp()
        self.source = os.path.join(directory, "sans-sexe.csv")
        with open(self.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(HEADERS)
            for index in range(30):
                writer.writerow(list(make_row(index, gender="",
                                              salary=40000 + index * 100)))
        self.app = Application()
        self.app.update()
        from compensation_analytics.core.pipeline import load_population

        population, mapping, table = load_population(self.source,
                                                     self.app.configuration)
        self.app.source_path = self.source
        self.app.population = population
        self.app.mapping = mapping
        self.app.headers = list(table.headers)
        self.app._populate_filters()
        self.app.run_analysis()
        limit = time.time() + 60
        while self.app.result is None and time.time() < limit:
            self.app.update()
            time.sleep(0.02)
        for _ in range(10):
            self.app.update()
            time.sleep(0.01)

    def tearDown(self):
        self.app.destroy()

    def test_the_tab_disappears_or_explains_itself(self):
        payload = self.app.result.payload["pay_equity"]
        self.assertFalse(payload.get("available"))
        self.assertTrue(payload.get("warning"))

    def test_no_figure_is_invented(self):
        self.assertEqual(self.app._categories, [])


if __name__ == "__main__":
    unittest.main()
