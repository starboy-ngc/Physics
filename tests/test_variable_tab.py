"""L'onglet « Variable » et l'écran des éléments.

Aucune donnée réelle : la population et le fichier d'éléments sont
fabriqués ici.
"""

import csv
import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import tkinter as tk
    HAS_TK = True
except ImportError:  # pragma: no cover
    HAS_TK = False

if HAS_TK:
    from tests.test_window_workflow import Dialogs

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sans_ecran():
    if not HAS_TK:
        return True
    try:
        racine = tk.Tk()
    except tk.TclError:
        return True
    racine.destroy()
    return False


@unittest.skipIf(_sans_ecran(), "pas d'écran")
class TestTheVariableTab(unittest.TestCase):
    """L'onglet n'existe que si un fichier d'éléments a été chargé : son
    absence n'a rien à expliquer tant que personne n'a rien demandé."""

    def setUp(self):
        from hr_analytics.ui.app import Application

        self.directory = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.directory, "config")
        shutil.copytree(os.path.join(RACINE, "config"), self.config_dir)
        self.app = Application(config_dir=self.config_dir)
        self.app.update()
        self._ouvertes = []

    def tearDown(self):
        for fenetre in self._ouvertes:
            if fenetre.winfo_exists():
                fenetre.destroy()
        self.app.destroy()
        shutil.rmtree(self.directory, ignore_errors=True)

    # ------------------------------------------------------------ fichiers

    def _population(self, nombre=40):
        chemin = os.path.join(self.directory, "population.csv")
        with open(chemin, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(["Matricule", "Sexe", "Métier", "Salaire de base",
                             "Date d'entrée", "Temps de travail",
                             "Date d'extraction"])
            for rang in range(nombre):
                writer.writerow([
                    f"M{rang}", "F" if rang % 2 else "H",
                    "Conduite" if rang % 2 else "Quai",
                    2000 + rang * 10,
                    "2015-01-01" if rang else "2026-05-01",
                    "100", "2026-06-30"])
        return chemin

    def _elements(self, avec_date=True):
        chemin = os.path.join(self.directory, "elements.csv")
        with open(chemin, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            entete = ["Matricule", "Libellé", "Montant"]
            if avec_date:
                entete.append("Date")
            writer.writerow(entete)
            for rang in range(30):
                ligne = [f"M{rang}", "Prime de résultat", 600 + rang * 5]
                if avec_date:
                    ligne.append("2026-03-10")
                writer.writerow(ligne)
                frais = [f"M{rang}", "Indemnités de déplacement", 300]
                if avec_date:
                    frais.append("2026-02-01")
                writer.writerow(frais)
        return chemin

    def _charger(self, avec_date=True, natures=None):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        with Dialogs(open_path=self._elements(avec_date)):
            self.app.choose_elements()
        self.app.update()
        fenetre = self.app.elements_window
        self._ouvertes.append(fenetre)
        for intitule, nature in (natures or
                                 {"Indemnités de déplacement": "exclu"}).items():
            fenetre._natures[intitule].set(nature)
        fenetre.save()
        self.app.update()
        return fenetre

    # --------------------------------------------------------------- essais

    def test_the_tab_is_absent_until_a_second_file_is_loaded(self):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        self.assertFalse(self.app.tabbar._visible.get("variable", False))
        self._charger()
        self.assertTrue(self.app.tabbar._visible.get("variable", False))

    def test_the_period_offered_is_the_year_before_the_extraction(self):
        """Les bornes observées sont celles des versements, pas celles de
        la période : elles sous-estiment presque toujours."""
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        with Dialogs(open_path=self._elements()):
            self.app.choose_elements()
        self.app.update()
        fenetre = self.app.elements_window
        self._ouvertes.append(fenetre)
        # L'extraction est au 30/06/2026 : les douze mois clos qui la
        # precedent vont du 01/06/2025 au 31/05/2026.
        self.assertEqual(fenetre._du.get(), "01/06/2025")
        self.assertEqual(fenetre._au.get(), "31/05/2026")

    def test_the_labels_of_the_file_are_offered_not_invented(self):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        with Dialogs(open_path=self._elements()):
            self.app.choose_elements()
        self.app.update()
        fenetre = self.app.elements_window
        self._ouvertes.append(fenetre)
        self.assertEqual(sorted(fenetre._labels),
                         ["Indemnités de déplacement", "Prime de résultat"])

    def test_a_short_period_says_what_it_hides(self):
        """En deçà de douze mois, une prime annuelle versée hors de la
        fenêtre n'apparaît pas."""
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        with Dialogs(open_path=self._elements()):
            self.app.choose_elements()
        self.app.update()
        fenetre = self.app.elements_window
        self._ouvertes.append(fenetre)
        fenetre._du.set("01/01/2026")
        fenetre._au.set("30/06/2026")
        self.app.update()
        self.assertIn("douze mois", fenetre.note.cget("text"))

    def test_an_unreadable_date_refuses_to_apply(self):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        with Dialogs(open_path=self._elements()):
            self.app.choose_elements()
        self.app.update()
        fenetre = self.app.elements_window
        self._ouvertes.append(fenetre)
        fenetre._du.set("hier")
        fenetre.save()
        self.app.update()
        self.assertTrue(fenetre.winfo_exists(), "la fenêtre s'est fermée")
        self.assertIn("jj/mm/aaaa", fenetre.feedback.cget("text"))

    def test_the_reconciliation_is_on_screen_not_in_a_log(self):
        """Un total de primes dont on ignore sur qui il porte n'est pas un
        chiffre."""
        self._charger()
        texte = self.app.variable_page.source.cget("text")
        self.assertIn("elements.csv", texte)
        self.assertIn("rapprochés", texte)
        self.assertIn("01/06/2025", texte)

    def test_someone_hired_during_the_period_is_set_aside_and_said(self):
        self._charger()
        compte = self.app.package_reconciliation
        self.assertEqual(compte.late_entrants, 1)
        self.assertIn("mis de côté", self.app.variable_page.source.cget("text"))

    def test_an_excluded_element_is_shown_but_counts_nowhere(self):
        self._charger()
        page = self.app.variable_page
        page.choice.set("Quai")
        page.refresh()
        self.app.update()
        lignes = [page.elements.item(i)["values"]
                  for i in page.elements.get_children()]
        par_nom = {str(l[0]): l for l in lignes}
        self.assertIn("Indemnités de déplacement", par_nom)
        self.assertEqual(str(par_nom["Indemnités de déplacement"][1]), "Exclu")
        self.assertEqual(str(par_nom["Indemnités de déplacement"][3]), "—")

    def test_the_natures_are_kept_for_the_next_time(self):
        import json

        self._charger()
        chemin = os.path.join(self.config_dir, "package_parameters.json")
        with open(chemin, encoding="utf-8") as fichier:
            section = json.load(fichier)
        self.assertEqual(section["natures"]["Indemnités de déplacement"],
                         "exclu")

    def test_the_tab_holds_a_job_without_a_second_import(self):
        self._charger()
        page = self.app.variable_page
        self.assertIn(page.choice.get(), ("Quai", "Conduite"))
        self.assertIn("salariés", page.headcount.cget("text"))

    def test_a_file_without_dates_still_works(self):
        """La plupart des extractions de paie n'en portent pas : c'est la
        période déclarée qui fait foi."""
        self._charger(avec_date=False)
        self.assertEqual(self.app.package_reconciliation.out_of_period, 0)
        self.assertGreater(self.app.package_reconciliation.matched, 0)


if __name__ == "__main__":
    unittest.main()


class TestANatureTypedByHandIsChecked(unittest.TestCase):
    """Le fichier de paramètres se modifie au bloc-notes : une nature
    inventée doit se voir, et non faire retomber tous les éléments sur
    « variable » sans que rien ne le dise."""

    def test_an_unknown_nature_is_refused_by_name(self):
        from hr_analytics.core.config import load_configuration
        from hr_analytics.core.errors import ConfigError
        from hr_analytics.core.package import nature_rules

        config = load_configuration()
        config._data["package_parameters"]["natures"] = {
            "Prime de résultat": "bonus"}
        with self.assertRaises(ConfigError) as refus:
            nature_rules(config)
        self.assertIn("bonus", refus.exception.message)
        self.assertIn("Prime de résultat", refus.exception.message)

    def test_the_natures_come_back_normalised(self):
        from hr_analytics.core.config import load_configuration
        from hr_analytics.core.package import nature_rules

        config = load_configuration()
        config._data["package_parameters"]["natures"] = {
            "Indemnités de Déplacement": "exclu"}
        self.assertEqual(nature_rules(config),
                         {"indemnites de deplacement": "exclu"})


@unittest.skipIf(_sans_ecran(), "pas d'écran")
class TestTheCompositionSaysWhatItShows(unittest.TestCase):
    """Le libellé disait « mensuelle » et montrait douze mois de salaire :
    on lisait un salaire annuel comme un salaire de mois."""

    def setUp(self):
        from hr_analytics.ui.theme import Fonts
        from hr_analytics.ui.variable import VariablePage

        self.root = tk.Tk()
        self.root.withdraw()
        from hr_analytics.ui import theme
        self.fonts = Fonts(self.root)
        theme.apply(self.root, self.fonts)
        self.page = VariablePage(self.root, self.fonts)

    def tearDown(self):
        self.root.destroy()

    def test_the_note_names_the_period_not_a_month(self):
        import datetime as dt

        from hr_analytics.core.config import load_configuration
        from hr_analytics.core.package import Period

        self.page.show([], [], load_configuration(),
                       Period(dt.date(2025, 1, 1), dt.date(2025, 12, 31)), {})
        texte = self.page.composition_note.cget("text")
        self.assertIn("sur la période", texte)
        self.assertIn("12,0 mois", texte)
        self.assertNotIn("mensuelle", texte)


@unittest.skipIf(_sans_ecran(), "pas d'écran")
class TestTheNatureListFollowsTheValue(unittest.TestCase):
    """Une liaison à sens unique laissait la liste montrer « Variable »
    sur un élément qu'on venait de classer autrement."""

    def setUp(self):
        import datetime as dt

        from hr_analytics.core.package import Period
        from hr_analytics.ui import theme
        from hr_analytics.ui.theme import Fonts
        from hr_analytics.ui.variable import ElementsWindow

        self.root = tk.Tk()
        self.root.withdraw()
        fonts = Fonts(self.root)
        theme.apply(self.root, fonts)
        self.fenetre = ElementsWindow(
            self.root, fonts, ["Prime de résultat", "Indemnités"], {}, None,
            None, dt.date(2026, 6, 30), lambda _p, _n: None)

    def tearDown(self):
        self.root.destroy()

    def _affiche(self, intitule):
        for ligne in self.fenetre.winfo_children():
            for widget in self._tous(ligne):
                if widget.winfo_class() == "TCombobox":
                    voisins = widget.master.winfo_children()
                    titres = [w.cget("text") for w in voisins
                              if "text" in w.keys()]
                    if intitule in titres:
                        return widget.get()
        return None

    def _tous(self, widget):
        yield widget
        for enfant in widget.winfo_children():
            yield from self._tous(enfant)

    def test_setting_the_value_updates_the_list(self):
        self.assertEqual(self._affiche("Indemnités"), "Variable")
        self.fenetre._natures["Indemnités"].set("exclu")
        self.root.update()
        self.assertEqual(self._affiche("Indemnités"), "Exclu")
        self.assertEqual(self.fenetre.collect()["Indemnités"], "exclu")
