"""L'onglet « Fiche salarié » et l'import d'historique.

Aucune donnée réelle : la population et l'historique sont fabriqués ici.
"""

import csv
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
class TestTheEmployeeSheet(unittest.TestCase):
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

    def _population(self, nombre=20):
        chemin = os.path.join(self.directory, "population.csv")
        with open(chemin, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(["Matricule", "Nom", "Prénom", "Sexe", "Métier",
                             "Poste", "Salaire de base", "Temps de travail"])
            for rang in range(nombre):
                writer.writerow([f"M{rang}", f"Nom{rang}", f"Prénom{rang}",
                                 "F" if rang % 2 else "H", "Exploitation",
                                 "Exploitant", 2000 + rang * 25, "100"])
        return chemin

    def _historique(self):
        chemin = os.path.join(self.directory, "historique.csv")
        with open(chemin, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(["Matricule", "Période", "Salaire annuel",
                             "Primes", "Rémunération totale", "Performance"])
            for rang in range(20):
                for annee, salaire in ((2023, 24000), (2024, 25000)):
                    writer.writerow([f"M{rang}", str(annee),
                                     salaire + rang * 100, 500,
                                     salaire + rang * 100 + 500,
                                     "A" if rang % 3 else "B"])
        return chemin

    def _charger(self, roles=None):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        with Dialogs(open_path=self._historique()):
            self.app.choose_history()
        self.app.update()
        fenetre = self.app.history_window
        self._ouvertes.append(fenetre)
        defaut = {"Salaire annuel": "montant", "Primes": "montant",
                  "Rémunération totale": "ignoree",
                  "Performance": "ignoree"}
        for colonne, role in (roles or defaut).items():
            if colonne in fenetre._roles:
                fenetre._roles[colonne].set(role)
        fenetre.save()
        self.app.update()
        return fenetre

    def _personne(self, matricule="M3"):
        for _libelle, personne in self.app.fiche_page.picker._entrees:
            if str(personne.value("employee_id")) == matricule:
                return personne
        raise AssertionError(matricule)

    # --------------------------------------------------------------- essais

    def test_the_sheet_lives_as_soon_as_the_population_does(self):
        """Elle n'attend ni l'analyse ni l'historique, seulement
        quelqu'un à montrer."""
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        self.assertTrue(self.app.tabbar._visible.get("fiche", False))
        self.assertEqual(len(self.app.fiche_page.picker._entrees), 20)

    def test_without_a_chosen_person_the_screen_says_what_it_waits_for(self):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        self.assertIn("Cherchez",
                      self.app.fiche_page.identity.cget("text"))

    def test_searching_narrows_to_the_matches(self):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        picker = self.app.fiche_page.picker
        picker._cherche.set("M12")
        self.app.update()
        self.assertEqual([libelle for libelle, _p in picker._vus][:1],
                         [l for l, _p in picker._entrees
                          if "M12" in l][:1])
        picker._cherche.set("zzz-introuvable")
        self.app.update()
        self.assertEqual(picker._vus, [])
        self.assertIn("aucune", picker.count.cget("text"))

    def test_the_matricule_is_always_on_the_identity_line(self):
        """C'est lui qui fait le lien avec l'historique."""
        self._charger()
        page = self.app.fiche_page
        page._choisir(self._personne("M3"))
        self.app.update()
        self.assertIn("M3", page.identity.cget("text"))

    def test_the_standing_is_the_ratio_to_the_median_of_the_job(self):
        self._charger()
        page = self.app.fiche_page
        page._choisir(self._personne("M0"))
        self.app.update()
        self.assertIn("Rapport à la médiane",
                      page.standing_figures.cget("text"))
        self.assertIn("Exploitant", page.standing_note.cget("text"))

    def test_a_job_too_small_publishes_nothing(self):
        """Comparer quelqu'un à trois collègues, c'est publier la
        rémunération de ces trois-là à travers la sienne."""
        with Dialogs(open_path=self._population(nombre=3)):
            self.app.choose_file()
        self.app.update()
        page = self.app.fiche_page
        page._choisir(page.picker._entrees[0][1])
        self.app.update()
        self.assertIn("publier", page.standing_note.cget("text"))
        self.assertEqual(page.standing_figures.cget("text"), "")

    def test_the_history_gives_one_line_per_period(self):
        self._charger()
        page = self.app.fiche_page
        page._choisir(self._personne("M3"))
        self.app.update()
        periodes = [page.history.item(i)["values"]
                    for i in page.history.get_children()]
        self.assertEqual([str(l[0]) for l in periodes], ["2023", "2024"])

    def test_the_sheet_holds_nothing_about_people_review(self):
        """Elle ne traite que de rémunération : deux choses posées côte à
        côte finissent par s'expliquer l'une l'autre dans la tête du
        lecteur, et rien ici ne le permet."""
        self.assertFalse(hasattr(self.app.fiche_page, "appraisals"))

    def test_a_column_classed_ignored_is_not_summed(self):
        """Une colonne qui porte déjà un total compterait deux fois."""
        self._charger()
        page = self.app.fiche_page
        page._choisir(self._personne("M0"))
        self.app.update()
        premier = page.history.item(page.history.get_children()[0])["values"]
        # 24 000 de salaire + 500 de primes, le total déclaré ignoré.
        self.assertIn("24 500", str(premier[1]))

    def test_classing_that_total_as_an_amount_doubles_it(self):
        """Le témoin de l'essai précédent : sans lui, il prouverait
        seulement qu'un nombre s'affiche."""
        self._charger(roles={"Salaire annuel": "montant",
                             "Primes": "montant",
                             "Rémunération totale": "montant",
                             "Performance": "ignoree"})
        page = self.app.fiche_page
        page._choisir(self._personne("M0"))
        self.app.update()
        premier = page.history.item(page.history.get_children()[0])["values"]
        self.assertIn("49 000", str(premier[1]))

    def test_the_change_is_shown_in_amount_and_in_share(self):
        self._charger()
        page = self.app.fiche_page
        page._choisir(self._personne("M0"))
        self.app.update()
        lignes = [page.history.item(i)["values"]
                  for i in page.history.get_children()]
        self.assertEqual(str(lignes[0][2]), "—")
        self.assertIn("+1 000", str(lignes[1][2]))
        self.assertIn("%", str(lignes[1][3]))

    def test_the_roles_are_kept_for_the_next_time(self):
        import json

        self._charger()
        chemin = os.path.join(self.config_dir, "career_parameters.json")
        with open(chemin, encoding="utf-8") as fichier:
            section = json.load(fichier)
        self.assertEqual(section["columns"]["Rémunération totale"], "ignoree")
        self.assertEqual(section["columns"]["Performance"], "ignoree")

    def test_a_matricule_without_history_says_so(self):
        self._charger()
        page = self.app.fiche_page
        page._history = {}
        page._choisir(self._personne("M3"))
        self.app.update()
        self.assertIn("Aucun historique", page.history_note.cget("text"))

    def test_the_reconciliation_is_on_screen(self):
        self._charger()
        texte = self.app.fiche_page.source.cget("text")
        self.assertIn("historique.csv", texte)
        self.assertIn("périodes", texte)
        self.assertIn("2023", texte)


class TestTheSheetNeverExports(unittest.TestCase):
    """Une fiche est nominative : elle vit à l'écran, et rien n'en sort.

    L'essai lit le code plutôt que l'écran : c'est une promesse de
    conception, et elle doit casser si quelqu'un ajoute un bouton."""

    def test_no_export_path_exists_in_the_sheet(self):
        # Le fichier se lit sur le disque plutot que de s'importer :
        # l'essai porte sur son texte, et il doit valoir meme la ou
        # tkinter n'est pas installe.
        chemin = os.path.join(RACINE, "hr_analytics", "ui", "fiche.py")
        with open(chemin, encoding="utf-8") as fichier:
            source = fichier.read()
        for interdit in ("asksaveasfilename", "write_workbook",
                         "export_excel", "askdirectory"):
            self.assertNotIn(interdit, source, interdit)


if __name__ == "__main__":
    unittest.main()


@unittest.skipIf(_sans_ecran(), "pas d'écran")
class TestTheScreenBeforeAnyoneIsChosen(TestTheEmployeeSheet):
    """Deux intertitres surmontant du vide se lisent comme une panne."""

    def test_the_two_columns_wait_for_a_person(self):
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        page = self.app.fiche_page
        self.assertFalse(page.body.winfo_manager())
        page._choisir(page.picker._entrees[0][1])
        self.app.update()
        self.assertTrue(page.body.winfo_manager())

    def test_the_matches_do_not_push_the_page_down(self):
        """Packée, la liste poussait l'écran entier vers le bas à chaque
        frappe : elle se pose par-dessus."""
        with Dialogs(open_path=self._population()):
            self.app.choose_file()
        self.app.update()
        page = self.app.fiche_page
        page._choisir(page.picker._entrees[0][1])
        self.app.update()
        avant = page.body.winfo_y()
        page.picker._cherche.set("M1")
        self.app.update()
        self.assertEqual(page.picker.liste.winfo_manager(), "place")
        self.assertEqual(page.body.winfo_y(), avant)
        page.picker._cherche.set("")
        self.app.update()
        self.assertEqual(page.picker.liste.winfo_manager(), "")
