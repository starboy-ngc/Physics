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
        from hr_insight.ui.app import Application

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
        from hr_insight.core.pipeline import load_population

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
        """Retient une barre du graphique, comme un clic dessus.

        La liste a cede la place a un graphique : la selection ne passe
        plus par un « Treeview » mais par le graphique lui-meme. Ce que ces
        tests verifient — quelle fiche s'ouvre, ce qu'elle montre — n'a pas
        change.
        """
        self.app.category_value.set(
            self.app._categories[position]["category"])
        self.app._show_profile()
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
        from hr_insight.ui.app import CATEGORY_ORDERS

        for position in range(len(CATEGORY_ORDERS)):
            self.app.category_order.current(position)
            self.app._show_categories()
            self.app.update()
            self.assertEqual(sorted(self.categories()), sorted(POSTES),
                             CATEGORY_ORDERS[position][0])

    def test_ordering_by_name_is_alphabetical(self):
        from hr_insight.ui.app import CATEGORY_ORDERS

        position = [key for key, _label in CATEGORY_ORDERS].index("name")
        self.app.category_order.current(position)
        self.app._show_categories()
        self.app.update()
        self.assertEqual(self.categories(), sorted(POSTES, key=str.lower))

    def test_ordering_by_headcount_puts_the_largest_first(self):
        from hr_insight.ui.app import CATEGORY_ORDERS

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

    def test_the_card_holds_the_whole_pay_analysis(self):
        """La fiche ne compare plus deux moyennes : elle pose l'analyse
        complete de la remuneration du poste — extremes, quartiles,
        mediane, moyenne, dispersion."""
        self.select()
        libelles = [self.app.profile_tree.item(ligne)["values"][0]
                    for ligne in self.app.profile_tree.get_children()]
        for attendu in ("Minimum", "Q1 (P25)", "Médiane (P50)", "Moyenne",
                        "Q3 (P75)", "Maximum", "DISPERSION"):
            self.assertIn(attendu, libelles, attendu)

    def test_the_card_shows_three_columns(self):
        """Femmes, hommes, et l'ensemble. Sans la troisieme, on ne sait pas
        si un ecart tient a un groupe tire vers le bas ou l'autre vers le
        haut."""
        self.select()
        intitules = [self.app.profile_tree.heading(colonne)["text"]
                     for colonne in self.app.profile_tree["columns"]]
        self.assertEqual([texte.title() for texte in intitules[1:]],
                         ["Femmes", "Hommes", "Global"])
        valeurs = [self.app.profile_tree.item(ligne)["values"]
                   for ligne in self.app.profile_tree.get_children()]
        for ligne in valeurs:
            self.assertEqual(len(ligne), 4)

    def test_changing_the_selection_changes_the_card(self):
        self.select(0)
        first = self.app.profile_title.cget("text")
        self.select(1)
        self.assertNotEqual(self.app.profile_title.cget("text"), first)

    def test_with_no_selection_the_page_shows_the_overview(self):
        """Sans poste choisi, la page repond a « ou faut-il regarder ? »
        plutot que d'ouvrir une fiche au hasard."""
        from hr_insight.ui.app import ALL_CATEGORIES

        self.app.category_value.set(ALL_CATEGORIES)
        self.app._show_profile()
        self.app.update()
        self.assertEqual(self.app.overview_block.winfo_manager(), "pack")
        self.assertFalse(self.app.detail_block.winfo_manager())
        self.assertTrue(self.app.gap_chart.rows)

    def test_choosing_a_position_replaces_the_overview(self):
        """Une seule question a la fois : le detail prend la place de la
        vue d'ensemble, il ne s'y ajoute pas."""
        self.select()
        self.assertEqual(self.app.detail_block.winfo_manager(), "pack")
        self.assertFalse(self.app.overview_block.winfo_manager())

    def test_a_group_below_the_threshold_is_not_calculated(self):
        """« On ne met pas les calculs en dessous de cinq. » Chaque colonne
        est masquee pour elle-meme : un poste ou vingt hommes cotoient
        trois femmes garde les colonnes Hommes et Global."""
        from hr_insight.core.pay_equity import category_breakdown

        breakdown = category_breakdown(
            self.app.result.filtered, self.app.result.config,
            self.app._axis(), self.app.category_value.get())
        seuil = breakdown["threshold"]
        for colonne in breakdown["columns"]:
            with self.subTest(colonne=colonne["label"]):
                if colonne["headcount"] < seuil:
                    self.assertTrue(colonne["masked"])
                    self.assertNotIn("salary", colonne)
                else:
                    self.assertFalse(colonne["masked"])

    def test_changing_the_axis_returns_to_the_overview(self):
        """La fiche d'un poste n'a plus de sens quand la page montre des
        grades : la laisser affichee ferait lire un ecart sous un mauvais
        intitule.

        Elle ne se deplace pas vers un grade pris au hasard : changer
        d'axe, c'est changer de question, et la page revient a « ou faut-il
        regarder ? ». Choisir a la place de l'utilisateur serait lui faire
        lire une fiche qu'il n'a pas demandee.
        """
        self.select()
        self.assertIn(self.app.profile_title.cget("text"), POSTES)
        wanted = self.app._category_fields.index("grade")
        self.app.category_choice.current(wanted)
        self.app._show_categories()
        self.app.update()
        self.assertEqual(self.app.overview_block.winfo_manager(), "pack")
        self.assertFalse(self.app.detail_block.winfo_manager())
        # Et les grades sont proposes au choix, a la place des postes.
        propositions = list(self.app.category_value.cget("values"))
        self.assertTrue(set(propositions) & set(self.categories()))
        self.assertFalse(set(propositions) & set(POSTES))

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
        from hr_insight.ui.app import Application

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
        from hr_insight.core.pipeline import load_population

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


@needs_display
class TestTheThresholdIsReachableAndBinding(PayTransparencyCase):
    """Le seuil decide de ce que la page montre ou tait.

    Il vivait dans un fichier JSON, ou personne ne va le chercher. Il se
    regle maintenant dans la fenetre — et surtout, il agit : le relever
    doit masquer des colonnes qui s'affichaient.
    """

    def test_raising_the_threshold_masks_more_columns(self):
        from hr_insight.core.config import Configuration
        from hr_insight.core.pay_equity import category_breakdown

        poste = self.app._categories[0]["category"]
        donnees = self.app.result.config.as_dict()

        donnees["privacy_parameters"]["min_headcount_publish"] = 1
        bas = category_breakdown(self.app.result.filtered,
                                 Configuration(donnees),
                                 self.app._axis(), poste)
        donnees["privacy_parameters"]["min_headcount_publish"] = 500
        haut = category_breakdown(self.app.result.filtered,
                                  Configuration(donnees),
                                  self.app._axis(), poste)

        self.assertTrue(all(not c["masked"] for c in bas["columns"]))
        self.assertTrue(all(c["masked"] for c in haut["columns"]))
        self.assertFalse(haut["published"])
        self.assertIn("500", haut["warning"])

    def test_the_settings_window_offers_the_threshold(self):
        import tkinter as tk
        from hr_insight.ui.settings import SettingsWindow

        fenetre = SettingsWindow(self.app, self.app.configuration,
                                 self.app.config_dir, self.app.fonts,
                                 list(self.app.headers or []))
        self.app.update()
        try:
            self.assertEqual(
                fenetre.threshold_var.get(),
                str(self.app.configuration.number(
                    "privacy_parameters.min_headcount_publish", 5,
                    minimum=1, integer=True)))
            textes = []

            def marcher(widget):
                for enfant in widget.winfo_children():
                    if isinstance(enfant, tk.Label):
                        textes.append(enfant.cget("text"))
                    marcher(enfant)

            marcher(fenetre)
            joint = " ".join(textes)
            self.assertIn("Ne rien calculer en dessous de", joint)
        finally:
            fenetre.destroy()


@needs_display
class TestTheFullTimeBasisOnScreen(unittest.TestCase):
    """Un fichier avec temps de travail : ce que la page compare, et l'annonce.

    Le fichier de la classe precedente n'a pas de colonne de temps de
    travail — la page y compare donc les montants verses, et le dit. Ici le
    fichier en a une, et les femmes sont a 80 % payees 80 % : l'ecart verse
    est de vingt pour cent, l'ecart reel est nul. La page ne doit pas
    montrer le premier.
    """

    def setUp(self):
        import time

        from hr_insight.ui.app import Application
        from hr_insight.core.pipeline import load_population

        self.directory = tempfile.mkdtemp()
        self.source = os.path.join(self.directory, "temps.csv")
        with open(self.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste", "Temps de travail"])
            for index in range(120):
                poste = POSTES[index % 3]
                femme = (index // 3) % 2 == 0
                base = 40000 + POSTES.index(poste) * 9000 + (index % 5) * 300
                # Les femmes a 80 %, payees exactement 80 % : aucun ecart a
                # temps de travail egal, vingt pour cent sur les montants
                # verses. Sauf sur le dernier poste, ou s'ajoute un vrai
                # ecart de dix pour cent.
                réel = base * (0.9 if poste == POSTES[2] and femme else 1.0)
                writer.writerow(list(make_row(
                    index, salary=round(réel * (0.8 if femme else 1.0)),
                    gender="F" if femme else "H")) +
                    [poste, "0,8" if femme else "1"])
        self.app = Application()
        self.app.geometry("1400x900+0+0")
        self.app.update()
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
        self.assertIsNotNone(self.app.result)
        self.app.tabbar.select("equite")
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def _rows(self):
        return {row["category"]: row for row in self.app.gap_chart.rows}

    def test_the_page_says_what_it_compares(self):
        texte = self.app.profile_subtitle.cget("text")
        self.assertIn("temps plein", texte)
        self.assertIn("salaire de base", texte.lower())

    def test_a_part_time_gap_is_not_shown_as_an_inequality(self):
        """Vingt pour cent sur les montants verses, zero a temps egal."""
        lignes = self._rows()
        for poste in POSTES[:2]:
            with self.subTest(poste=poste):
                self.assertAlmostEqual(lignes[poste]["gap"], 0.0, places=6)
                self.assertFalse(lignes[poste]["significant"])

    def test_the_real_gap_is_shown_and_comes_first(self):
        lignes = self._rows()
        vrai = lignes[POSTES[2]]
        self.assertAlmostEqual(vrai["gap"], 10.0, places=6)
        self.assertTrue(vrai["significant"])
        # Le classement ouvre sur l'ecart que le hasard n'explique pas.
        self.assertEqual(self.app.gap_chart.rows[0]["category"], POSTES[2])

    def test_the_card_shows_the_probability_of_chance(self):
        self.app.category_value.set(POSTES[2])
        self.app._show_profile()
        self.app.update()
        textes = []

        def marcher(widget):
            import tkinter as tk

            for enfant in widget.winfo_children():
                if isinstance(enfant, tk.Label):
                    textes.append(enfant.cget("text"))
                marcher(enfant)

        marcher(self.app.profile_kpis)
        self.assertTrue(any("hasard" in str(texte).lower()
                            for texte in textes), textes)
        # La colonne des femmes porte la mediane a temps plein : celle du
        # montant verse vaudrait 80 % de celle-la, et se lirait comme un
        # ecart de vingt pour cent la ou il en est dix.
        from hr_insight.core.pay_equity import category_breakdown

        fiche = category_breakdown(self.app.result.filtered,
                                   self.app.result.config,
                                   self.app._axis(), POSTES[2])
        femmes = next(c for c in fiche["columns"] if c["key"] == "female")
        hommes = next(c for c in fiche["columns"] if c["key"] == "male")
        self.assertAlmostEqual(
            femmes["salary"]["median"] / hommes["salary"]["median"], 0.9,
            places=2)
        affichée = {ligne[0]: ligne for ligne in
                    (self.app.profile_tree.item(line, "values")
                     for line in self.app.profile_tree.get_children())
                    }["Médiane (P50)"][1]
        self.assertIn(str(int(femmes["salary"]["median"] // 1000)),
                      affichée.replace("\u202f", " ").replace(" ", ""))

    def test_the_card_names_the_basis(self):
        self.app.category_value.set(POSTES[0])
        self.app._show_profile()
        self.app.update()
        self.assertIn("temps plein",
                      self.app.profile_subtitle.cget("text"))
