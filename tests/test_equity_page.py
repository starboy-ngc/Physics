"""Le comparatif femmes / hommes : six blocs, un poste en tête.

Ce qui est vérifié ici n'est pas qu'une méthode ne lève pas, mais que la
page dit la même chose que le moteur : les mêmes effectifs, les mêmes
quartiles, le même périmètre quand on choisit un poste. Une page qui
compterait pour son propre compte finirait par contredire les documents.

Ces tests exigent un affichage ; ils sont ignorés automatiquement sans lui.
Aucune donnée RH réelle.
"""

import csv
import os
import sys
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

POSTES = ("Comptable", "Technicien", "Chef de projet")


@needs_display
class EquityCase(unittest.TestCase):
    """Une fenêtre, un fichier chargé, l'analyse faite, l'onglet ouvert."""

    import tempfile

    def setUp(self):
        import tempfile

        from hr_analytics.ui.app import Application
        from tests.test_window_workflow import Dialogs

        self.directory = tempfile.mkdtemp()
        chemin = os.path.join(self.directory, "p.csv")
        # Une colonne « Poste » : c'est sur elle que la page compare, et
        # les colonnes de base n'en portent pas.
        with open(chemin, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste"])
            for index in range(120):
                writer.writerow(make_row(
                    index, salary=30000 + (index % 20) * 500,
                    gender="F" if index % 2 else "H")
                    + [POSTES[index % 3]])
        self.app = Application()
        self.app.geometry("1400x900+0+0")
        self.app.update()
        with Dialogs(open_path=chemin):
            self.app.choose_file()
        self.app.update()
        self.app.run_analysis()
        limite = time.time() + 90
        while self.app.result is None and time.time() < limite:
            self.app.update()
            time.sleep(0.02)
        self.assertIsNotNone(self.app.result, "l'analyse n'a pas abouti")
        for _ in range(20):
            self.app.update()
            time.sleep(0.01)
        self.app.tabbar.select("equite")
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def lignes(self, arbre):
        return [arbre.item(item)["values"] for item in arbre.get_children()]

    def choisir(self, poste):
        self.app.equity_job.set(poste)
        self.app._show_equity_scope()
        self.app.update()


class TestTheWholePageAnswers(EquityCase):
    def test_every_block_is_filled_without_a_choice(self):
        """La page arrive complète : elle porte alors sur tout le monde."""
        self.assertTrue(self.lignes(self.app.equity_people))
        self.assertTrue(self.app.equity_pyramid.rows)
        self.assertTrue(self.app.equity_scatter.points)
        self.assertTrue(self.lignes(self.app.equity_stats))
        self.assertTrue(self.app.equity_box.rows)
        self.assertTrue(self.lignes(self.app.equity_recap))
        self.assertTrue(self.lignes(self.app.equity_list))

    def test_the_job_list_comes_from_the_file(self):
        propositions = list(self.app.equity_job.cget("values"))
        self.assertEqual(propositions[0], self.app.EQUITY_ALL)
        for poste in POSTES:
            self.assertIn(poste, propositions)

    def test_the_headcounts_match_the_engine(self):
        """Les effectifs affichés sont ceux du moteur, pas un comptage
        refait par la fenêtre."""
        from hr_analytics.core import metrics

        lignes = {str(ligne[0]): ligne for ligne in
                  self.lignes(self.app.equity_people)}
        femmes = sum(1 for employee in self.app.result.filtered
                     if metrics._sex_of(employee, self.app.result.config)
                     == "female")
        self.assertEqual(int(lignes["Effectif"][1]), femmes)
        self.assertEqual(int(lignes["Effectif"][3]),
                         len(self.app.result.filtered))


class TestChoosingAJob(EquityCase):
    def test_the_scope_follows_the_chosen_job(self):
        self.choisir(POSTES[0])
        attendu = sum(1 for employee in self.app.result.filtered
                      if str(employee.value(self.app._equity_field) or "")
                      == POSTES[0])
        self.assertIn(f"{attendu} salariés",
                      self.app.equity_scope_note.cget("text"))
        lignes = {str(ligne[0]): ligne for ligne in
                  self.lignes(self.app.equity_people)}
        self.assertEqual(int(lignes["Effectif"][3]), attendu)

    def test_the_box_shows_one_pair_whatever_the_choice(self):
        """Un tableau qui décrit un poste à côté d'un graphique qui en
        trace trente-neuf ferait lire deux choses dans deux colonnes
        voisines."""
        self.assertEqual(len(self.app.equity_box.rows), 1)
        self.choisir(POSTES[1])
        self.assertEqual(len(self.app.equity_box.rows), 1)
        self.assertEqual(str(self.app.equity_box.rows[0]["segment"]),
                         POSTES[1])

    def test_the_recap_covers_every_job_whatever_the_choice(self):
        """C'est lui qui permet de situer le poste qu'on regarde : le
        restreindre au poste retenu le viderait de son emploi."""
        avant = len(self.lignes(self.app.equity_recap))
        self.choisir(POSTES[0])
        self.assertEqual(len(self.lignes(self.app.equity_recap)), avant)
        self.assertGreaterEqual(avant, len(POSTES))

    def test_the_people_list_narrows_to_the_chosen_job(self):
        self.choisir(POSTES[2])
        colonnes = self.app._equity_columns
        rang = colonnes.index("job_title")
        postes = {str(ligne[rang]) for ligne in
                  self.lignes(self.app.equity_list)}
        self.assertEqual(postes, {POSTES[2]})

    def test_the_people_list_holds_every_employee_of_the_scope(self):
        """Ce n'est pas un classement : c'est la liste de ceux dont les
        chiffres de la page sont faits."""
        self.choisir(POSTES[1])
        attendu = sum(1 for employee in self.app.result.filtered
                      if str(employee.value(self.app._equity_field) or "")
                      == POSTES[1])
        self.assertEqual(len(self.lignes(self.app.equity_list)), attendu)

    def test_the_columns_come_from_the_configuration(self):
        """Ajouter « Direction » ou retirer l'établissement ne demande
        aucune modification du code."""
        from hr_analytics.core.pay_equity import people_columns

        declarees = [colonne["field"] for colonne
                     in people_columns(self.app.configuration)]
        self.assertEqual(self.app._equity_columns, declarees)
        intitules = [self.app.equity_list.heading(nom)["text"]
                     for nom in self.app.equity_list.cget("columns")]
        attendus = [colonne["label"].upper() for colonne
                    in people_columns(self.app.configuration)]
        self.assertEqual(intitules, attendus)

    def test_the_engine_carries_no_name(self):
        """Le moteur ne transporte jamais d'identité : c'est ce qui garantit
        qu'aucun document produit ne peut en porter."""
        from hr_analytics.core.pay_equity import people_rows

        bloc = people_rows(self.app.result.filtered, self.app.result.config)
        texte = " ".join(str(valeur) for ligne in bloc["rows"]
                         for valeur in ligne["values"].values())
        self.assertNotIn("NOM", texte)
        self.assertNotIn("PRENOM", texte)

    def test_going_back_to_all_restores_the_whole_population(self):
        self.choisir(POSTES[0])
        self.choisir(self.app.EQUITY_ALL)
        lignes = {str(ligne[0]): ligne for ligne in
                  self.lignes(self.app.equity_people)}
        self.assertEqual(int(lignes["Effectif"][3]),
                         len(self.app.result.filtered))


class TestTheScatterOfThisPage(EquityCase):
    def test_the_axes_are_the_ones_of_the_other_page(self):
        """Une seconde liste de champs aurait fini par différer."""
        from hr_analytics.core import metrics

        attendus = [axis["label"] for axis
                    in metrics.scatter_axes(self.app.configuration)]
        self.assertEqual(list(self.app.equity_x.cget("values")), attendus)
        self.assertEqual(list(self.app.equity_y.cget("values")), attendus)

    def test_changing_an_axis_recomputes_the_cloud(self):
        from hr_analytics.core import metrics

        champs = [axis["field"] for axis
                  in metrics.scatter_axes(self.app.configuration)]
        avant = self.app.equity_scatter.dataset.get("x_field")
        autre = next(i for i, champ in enumerate(champs) if champ != avant)
        self.app.equity_x.current(autre)
        self.app._reaxis_equity()
        self.app.update()
        self.assertEqual(self.app.equity_scatter.dataset.get("x_field"),
                         champs[autre])

    def test_the_reset_gives_back_the_configured_axes(self):
        self.app.equity_x.current(2)
        self.app._reaxis_equity()
        self.app._reset_equity_scatter()
        self.app.update()
        self.assertEqual(
            self.app.equity_scatter.dataset.get("x_field"),
            self.app.configuration.get("chart_parameters.scatter_x"))

    def test_the_cloud_is_coloured_by_sex_and_not_by_business_unit(self):
        """Un comparatif femmes / hommes colorié par BU ne compare rien."""
        self.assertEqual(
            self.app.equity_scatter.dataset.get("color_field"),
            self.app.configuration.get("pay_equity_parameters.gender_field"))

    def test_the_two_colours_are_those_of_the_rest_of_the_page(self):
        from hr_analytics.ui import theme

        teintes = set(self.app.equity_scatter.series.values())
        self.assertIn(theme.FEMALE, teintes)
        self.assertIn(theme.MALE, teintes)

    def test_the_legend_names_the_two_sexes_in_plain_words(self):
        """« F » et « H » sont les écritures du fichier ; la page dit
        « Femmes » et « Hommes » partout ailleurs."""
        textes = []
        for case in self.app.equity_legend.winfo_children():
            for enfant in case.winfo_children():
                try:
                    textes.append(str(enfant.cget("text")))
                except Exception:
                    pass
        self.assertIn("Femmes", textes)
        self.assertIn("Hommes", textes)
        # Les femmes en premier, comme dans la pyramide et les boîtes.
        self.assertLess(textes.index("Femmes"), textes.index("Hommes"))


class TestWhatTheStatsSay(EquityCase):
    def test_the_quartiles_match_the_engine(self):
        """Le tableau de gauche lit le même découpage que la boîte de
        droite : deux chiffres qui se contrediraient à l'écran seraient
        pires que l'un des deux seul."""
        from hr_analytics.core.pay_equity import population_breakdown
        from hr_analytics.core.reporting import format_money

        bloc = population_breakdown(self.app.result.filtered,
                                    self.app.result.config)
        colonnes = {c["key"]: c for c in bloc["columns"]}
        lignes = {str(ligne[0]): ligne for ligne in
                  self.lignes(self.app.equity_stats)}
        attendu = format_money(colonnes["female"]["salary"]["median"], "EUR")
        self.assertEqual(str(lignes["Médiane (P50)"][1]), attendu)

    def test_a_column_below_the_threshold_says_masked(self):
        """Un poste où trois femmes côtoient vingt hommes publie la colonne
        des hommes et tait celle des femmes : c'est la seule qui
        désignerait quelqu'un."""
        from hr_analytics.core.pay_equity import category_breakdown

        poste = POSTES[0]
        bloc = category_breakdown(self.app.result.filtered,
                                  self.app.result.config,
                                  self.app._equity_field, poste)
        self.choisir(poste)
        masquees = {c["key"] for c in bloc["columns"] if c["masked"]}
        if not masquees:
            self.skipTest("aucune colonne masquée sur ce jeu d'essai")
        lignes = self.lignes(self.app.equity_stats)
        self.assertTrue(any("masqué" in str(valeur)
                            for ligne in lignes for valeur in ligne))

    def test_the_gap_is_stated_rather_than_left_to_arithmetic(self):
        """Et sur une seule ligne : les trois phrases se repliaient sur deux
        ou trois lignes dans une demi-colonne, et le tableau se mettait à
        flotter au-dessus d'un paragraphe."""
        note = self.app.equity_stats_note.cget("text")
        self.assertIn("Écart moyenne", note)
        self.assertIn("médiane", note)
        self.assertNotIn(".", note.replace("...", ""))
