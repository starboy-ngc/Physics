"""Le parcours complet dans la fenetre, du fichier aux documents.

L'interface est la voie que prendra l'utilisateur : elle merite d'etre
parcourue en entier une fois — choisir un fichier, voir la qualite, filtrer,
analyser, produire les documents —, et surtout d'etre poussee dans ses
chemins d'echec, qui sont ceux que personne ne voit venir : un fichier
refuse, un dossier ou l'on n'a pas le droit d'ecrire, une analyse qui tombe
sur une erreur technique.

Les boites de dialogue du systeme sont remplacees le temps du test : ce sont
elles, et elles seules, qui empechent de derouler ce parcours sans main
humaine.

Ces tests exigent un affichage ; ils sont ignores automatiquement sans lui.
Aucune donnee RH reelle.
"""

import csv
import glob
import json
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


class Dialogs:
    """Remplace les boites du systeme, et retient ce qu'on leur a demande."""

    def __init__(self, open_path="", directory=""):
        self.open_path = open_path
        self.directory = directory
        self.errors = []
        self.infos = []
        self.warnings = []

    def __enter__(self):
        from compensation_analytics.ui import app as module

        self.saved = (module.filedialog.askopenfilename,
                      module.filedialog.askdirectory,
                      module.messagebox.showerror,
                      module.messagebox.showinfo,
                      module.messagebox.showwarning)
        module.filedialog.askopenfilename = lambda **_k: self.open_path
        module.filedialog.askdirectory = lambda **_k: self.directory
        module.messagebox.showerror = lambda title, message, **_k: \
            self.errors.append((title, message))
        module.messagebox.showinfo = lambda title, message, **_k: \
            self.infos.append((title, message))
        module.messagebox.showwarning = lambda title, message, **_k: \
            self.warnings.append((title, message))
        return self

    def __exit__(self, *_exception):
        from compensation_analytics.ui import app as module

        (module.filedialog.askopenfilename, module.filedialog.askdirectory,
         module.messagebox.showerror, module.messagebox.showinfo,
         module.messagebox.showwarning) = self.saved


@needs_display
class WindowCase(unittest.TestCase):
    def setUp(self):
        from compensation_analytics.ui.app import Application

        self.directory = tempfile.mkdtemp()
        self.app = Application()
        self.app.geometry("1280x800+0+0")
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def source(self, name="p.csv", rows=40, salary=lambda i: 40000 + i * 250,
               extra_headers=(), extra=lambda i: ()):
        path = os.path.join(self.directory, name)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + list(extra_headers))
            for index in range(rows):
                writer.writerow(list(make_row(
                    index, salary=salary(index),
                    business_unit=["France", "Iberia"][index % 2],
                    grade=f"G{3 + index % 4}",
                    gender="F" if index % 2 else "H")) + list(extra(index)))
        return path

    def load(self, path=None):
        with Dialogs(open_path=path or self.source()) as dialogs:
            self.app.choose_file()
        self.app.update()
        return dialogs

    def analyse(self):
        self.app.run_analysis()
        limit = time.time() + 60
        while self.app.result is None and time.time() < limit:
            self.app.update()
            time.sleep(0.02)
        for _ in range(20):
            self.app.update()
            time.sleep(0.01)
        self.assertIsNotNone(self.app.result, "l'analyse n'a pas abouti")


class TestOpeningAFile(WindowCase):
    def test_the_file_is_read_and_announced(self):
        self.load()
        self.assertEqual(len(self.app.population), 40)
        self.assertIn("40 salariés", self.app.source_label.cget("text"))

    def test_the_recognised_columns_are_counted(self):
        self.load()
        self.assertIn("colonnes reconnues", self.app.mapping_label.cget("text"))

    def test_an_unrecognised_column_points_at_the_settings(self):
        """C'est la reponse a « pourquoi ma colonne n'apparait pas ? »."""
        self.load(self.source("extra.csv", extra_headers=["Prime de panier"],
                              extra=lambda index: [100 + index]))
        self.assertIn("Paramètres", self.app.mapping_label.cget("text"))

    def test_the_quality_tab_comes_up_first(self):
        """On regarde la qualite du fichier avant de le croire."""
        self.load()
        self.assertEqual(self.app.tabbar.active, "qualite")

    def test_cancelling_the_dialog_changes_nothing(self):
        with Dialogs(open_path=""):
            self.app.choose_file()
        self.assertIsNone(self.app.population)

    def test_an_unreadable_file_is_refused_with_a_message(self):
        path = os.path.join(self.directory, "vide.csv")
        open(path, "w", encoding="utf-8").close()
        dialogs = self.load(path)
        self.assertTrue(dialogs.errors)
        self.assertIn("Import impossible", dialogs.errors[0][0])
        self.assertIsNone(self.app.population)

    def test_a_file_without_the_required_column_is_refused(self):
        path = os.path.join(self.directory, "sans-salaire.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Matricule;BU\nE1;France\n")
        dialogs = self.load(path)
        self.assertTrue(dialogs.errors)
        self.assertIsNone(self.app.population)

    def test_loading_a_second_file_replaces_the_first(self):
        self.load()
        self.load(self.source("second.csv", rows=12))
        self.assertEqual(len(self.app.population), 12)


class TestRunningTheAnalysis(WindowCase):
    def test_the_figures_reach_the_screen(self):
        self.load()
        self.analyse()
        self.assertEqual(self.app.result.payload["population"]["headcount"], 40)
        self.assertIn("40 salariés", self.app.status.cget("text"))

    def test_a_filter_narrows_the_analysis(self):
        self.load()
        self.app.filter_vars["business_unit"].set("France")
        self.app.update()
        self.analyse()
        self.assertEqual(self.app.result.payload["population"]["headcount"], 20)
        self.assertIn("France", self.app.status.cget("text"))

    def test_the_export_button_wakes_up_only_after_an_analysis(self):
        self.load()
        self.assertIn("disabled", self.app.export_button.state())
        self.analyse()
        self.assertNotIn("disabled", self.app.export_button.state())

    def test_a_small_population_masks_the_pages_and_says_why(self):
        self.load(self.source("petit.csv", rows=4))
        self.analyse()
        self.assertIn("masquée", self.app.status.cget("text"))
        self.assertTrue(self.app.notice.winfo_manager())

    def test_a_technical_failure_is_reported_without_any_detail(self):
        """Le texte d'une exception Python peut citer la cellule qui l'a
        provoquee, donc une donnee RH."""
        self.load()
        from compensation_analytics.ui import app as module

        original = module.run_analysis

        def explode(_request):
            raise ZeroDivisionError("salaire de DUPONT Marie : 0")

        module.run_analysis = explode
        try:
            with Dialogs() as dialogs:
                self.app.run_analysis()
                limit = time.time() + 20
                while not dialogs.errors and time.time() < limit:
                    self.app.update()
                    time.sleep(0.02)
        finally:
            module.run_analysis = original
        self.assertTrue(dialogs.errors)
        message = dialogs.errors[0][1]
        self.assertIn("ZeroDivisionError", message)
        self.assertNotIn("DUPONT", message)

    def test_a_business_refusal_shows_its_own_message(self):
        self.load()
        from compensation_analytics.core.errors import ConfigError
        from compensation_analytics.ui import app as module

        original = module.run_analysis
        module.run_analysis = lambda _r: (_ for _ in ()).throw(
            ConfigError("Période inconnue.", technical="x"))
        try:
            with Dialogs() as dialogs:
                self.app.run_analysis()
                limit = time.time() + 20
                while not dialogs.errors and time.time() < limit:
                    self.app.update()
                    time.sleep(0.02)
        finally:
            module.run_analysis = original
        self.assertIn("Période inconnue.", dialogs.errors[0][1])


class TestProducingDocuments(WindowCase):
    def output(self, name="sortie"):
        path = os.path.join(self.directory, name)
        os.makedirs(path, exist_ok=True)
        return path

    def test_every_document_is_written(self):
        self.load()
        self.analyse()
        out = self.output()
        with Dialogs(directory=out) as dialogs:
            self.app.export_documents()
        names = sorted(os.path.basename(p) for p in glob.glob(f"{out}/*"))
        for expected in ("restitution", "synthese", "slides", "analyse",
                         "manifeste"):
            self.assertTrue(any(n.startswith(expected) for n in names),
                            f"{expected} absent de {names}")
        self.assertTrue(dialogs.infos)

    def test_the_chosen_outputs_alone_are_written(self):
        self.load()
        self.analyse()
        for key in ("rapport", "synthese", "slides"):
            self.app.output_vars[key].set(False)
        out = self.output("un-seul")
        with Dialogs(directory=out):
            self.app.export_documents()
        names = sorted(os.path.basename(p) for p in glob.glob(f"{out}/*"))
        self.assertTrue(any(n.endswith(".xlsx") for n in names))
        self.assertFalse(any(n.endswith(".pdf") for n in names))

    def test_the_manifest_is_written_whatever_the_choice(self):
        self.load()
        self.analyse()
        for variable in self.app.output_vars.values():
            variable.set(False)
        out = self.output("manifeste-seul")
        with Dialogs(directory=out):
            self.app.export_documents()
        self.assertTrue(glob.glob(os.path.join(out, "manifeste-*.json")))

    def test_cancelling_writes_nothing(self):
        self.load()
        self.analyse()
        out = self.output("annule")
        with Dialogs(directory=""):
            self.app.export_documents()
        self.assertEqual(os.listdir(out), [])

    def test_a_destination_that_cannot_be_written_is_reported(self):
        """Un dossier verrouille, un chemin qui n'est pas un dossier, un
        disque plein : l'ecriture echoue, et il faut le dire plutot que de
        laisser croire que les documents sont produits."""
        self.load()
        self.analyse()
        not_a_folder = os.path.join(self.directory, "ceci-est-un-fichier")
        with open(not_a_folder, "w", encoding="utf-8") as handle:
            handle.write("x")
        with Dialogs(directory=not_a_folder) as dialogs:
            self.app.export_documents()
        self.assertTrue(dialogs.errors)
        self.assertIn("droit d'y écrire", dialogs.errors[0][1])
        self.assertFalse(dialogs.infos)

    def test_exporting_before_analysing_does_nothing(self):
        self.load()
        out = self.output("trop-tot")
        with Dialogs(directory=out):
            self.app.export_documents()
        self.assertEqual(os.listdir(out), [])


class TestSettingsRoundTrip(WindowCase):
    def test_saved_settings_are_applied_without_restarting(self):
        """Une colonne qui vient d'etre declaree n'a jamais ete lue : le
        fichier doit etre relu, sinon ses valeurs manquent jusqu'a la
        prochaine ouverture."""
        path = self.source("extra.csv", extra_headers=["Prime de panier"],
                           extra=lambda index: [100 + index])
        self.load(path)
        self.assertNotIn("variable_pay", self.app.mapping.field_to_index)
        config_dir = os.path.join(self.directory, "config")
        os.makedirs(config_dir, exist_ok=True)
        from compensation_analytics.core.config import write_configuration
        from compensation_analytics.ui.settings import build_mapping_section

        assignments = {header: "" for header in self.app.headers}
        assignments["Prime de panier"] = "variable_pay"
        for header, field_name in (("Matricule", "employee_id"),
                                   ("Salaire de base", "base_salary")):
            assignments[header] = field_name
        section = build_mapping_section(
            self.app.configuration.section("population_mapping"),
            assignments, {}, 60)
        written = write_configuration(config_dir, "population_mapping", section)
        self.app._settings_saved(config_dir, written)
        self.app.update()
        self.assertIn("variable_pay", self.app.mapping.field_to_index)
        self.assertIn("Paramètres enregistrés", self.app.status.cget("text"))

    def test_a_broken_configuration_is_reported_and_changes_nothing(self):
        self.load()
        before = self.app.configuration.get(
            "privacy_parameters.min_headcount_publish")
        broken = os.path.join(self.directory, "casse")
        os.makedirs(broken, exist_ok=True)
        with open(os.path.join(broken, "privacy_parameters.json"), "w",
                  encoding="utf-8") as handle:
            handle.write("{ ceci n'est pas du JSON")
        with Dialogs() as dialogs:
            self.app._settings_saved(broken, "x.json")
        self.assertTrue(dialogs.errors)
        self.assertEqual(
            self.app.configuration.get(
                "privacy_parameters.min_headcount_publish"), before)

    def test_the_settings_window_opens_with_the_loaded_columns(self):
        self.load()
        self.app.open_settings()
        self.app.update()
        opened = [child for child in self.app.winfo_children()
                  if child.winfo_class() == "Toplevel"]
        self.assertTrue(opened)
        for window in opened:
            window.destroy()


class TestTheDispersionDefaults(WindowCase):
    """Ce que l'onglet Dispersion propose sans qu'on ait rien touche."""

    def _load_with_positions(self):
        return self.load(self.source(
            "postes.csv", rows=120, extra_headers=["Poste"],
            extra=lambda index: [["Comptable", "Technicien",
                                  "Chef de projet"][index % 3]]))

    def test_the_position_is_the_dimension_offered_first(self):
        """C'est l'axe sur lequel une comparaison de remuneration se fait le
        plus souvent. La BU arrivait en tete parce qu'elle est declaree en
        premier, ce qui n'est pas une raison."""
        self._load_with_positions()
        self.analyse()
        self.assertEqual(self.app.box_choice.get(), "Poste")

    def test_the_sort_is_by_headcount(self):
        self._load_with_positions()
        self.analyse()
        self.assertEqual(self.app.box_order.get(), "Effectif décroissant")
        self.assertEqual(self.app.boxplot.order, "headcount")

    def test_the_biggest_segment_comes_first(self):
        self._load_with_positions()
        self.analyse()
        effectifs = [row.get("headcount") or 0
                     for row in self.app.boxplot._drawable()]
        self.assertEqual(effectifs, sorted(effectifs, reverse=True))

    def test_a_file_without_positions_falls_back(self):
        """Le champ n'est pas ecrit en dur : sans colonne de poste, la
        premiere dimension disponible fait l'affaire."""
        self.load()
        self.analyse()
        self.assertTrue(self.app.box_choice.get())
        self.assertNotEqual(self.app.box_choice.get(), "")

    def test_the_alert_threshold_reaches_the_chart(self):
        from tests.support import make_config

        self._load_with_positions()
        self.analyse()
        self.assertEqual(
            self.app.boxplot.alert,
            self.app.configuration.get(
                "pay_equity_parameters.gap_alert_threshold"))


class TestThemeAndIdentities(WindowCase):
    def test_changing_the_colour_dimension_regroups_the_cloud(self):
        """Le regroupement est refait par le moteur, pas par l'interface :
        les couleurs de l'ecran et celles du document restent identiques."""
        self.load()
        self.analyse()
        before = set(self.app.scatter.dataset.get("groups") or [])
        wanted = next(index for index, field in
                      enumerate(self.app._colour_fields) if field == "grade")
        self.app.colour_choice.current(wanted)
        self.app._recolour()
        self.app.update()
        after = set(self.app.scatter.dataset.get("groups") or [])
        self.assertNotEqual(after, before)
        self.assertTrue(after)

    def test_recolouring_before_an_analysis_does_nothing(self):
        self.load()
        self.app._recolour()
        self.assertEqual(self.app.scatter.points, [])

    def test_the_identity_index_is_built_from_the_loaded_file(self):
        self.load()
        self.analyse()
        self.assertTrue(self.app._identities)
        row = next(iter(self.app._identities))
        self.assertIn("NOM", self.app._identity_of(row))

    def test_no_identity_is_kept_when_the_setting_says_no(self):
        from tests.support import make_config

        self.load()
        self.app.configuration = make_config(
            {"privacy_parameters.show_identities_on_screen": False})
        self.analyse()
        self.assertEqual(self.app._identities, {})
        self.assertEqual(self.app._identity_of(2), "")

    def test_an_unknown_row_has_no_identity(self):
        self.load()
        self.analyse()
        self.assertEqual(self.app._identity_of(999999), "")
        self.assertEqual(self.app._identity_of(None), "")


if __name__ == "__main__":
    unittest.main()
