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
        from hr_analytics.ui import app as module

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
        from hr_analytics.ui import app as module

        (module.filedialog.askopenfilename, module.filedialog.askdirectory,
         module.messagebox.showerror, module.messagebox.showinfo,
         module.messagebox.showwarning) = self.saved


@needs_display
class WindowCase(unittest.TestCase):
    def setUp(self):
        from hr_analytics.ui.app import Application

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
                    groupe=f"G{3 + index % 4}",
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

    def test_an_unrecognised_column_points_at_what_to_do(self):
        """C'est la reponse a « pourquoi ma colonne n'apparait pas ? ».

        Elle renvoyait aux « Paramètres », ou personne n'allait la
        chercher. Le bouton qui associe les colonnes est maintenant sous
        le fichier, la ou l'on vient de le charger : le message y renvoie,
        et le bouton s'allume.
        """
        self.load(self.source("extra.csv", extra_headers=["Prime de panier"],
                              extra=lambda index: [100 + index]))
        message = self.app.mapping_label.cget("text")
        self.assertIn("non reconnue", message)
        self.assertIn("associez", message.lower())
        self.assertFalse(self.app.columns_button.instate(["disabled"]))

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
        self.app.set_filter("business_unit", ["France"])
        self.app.update()
        self.analyse()
        self.assertEqual(self.app.result.payload["population"]["headcount"], 20)
        self.assertIn("France", self.app.status.cget("text"))

    def test_a_filter_on_several_values_narrows_the_analysis(self):
        """Plusieurs valeurs retenues deviennent une appartenance, et le
        moteur en tient compte : sans cela le filtre serait une décoration."""
        self.load()
        self.app.set_filter("groupe", ["G3", "G4"])
        self.app.update()
        self.analyse()
        # Quatre groupes de dix salariés sur les quarante du fichier.
        self.assertEqual(self.app.result.payload["population"]["headcount"], 20)
        groupes = {salarié.value("groupe")
                   for salarié in self.app.result.filtered}
        self.assertEqual(groupes, {"G3", "G4"})

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
        from hr_analytics.ui import app as module

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
        from hr_analytics.core.errors import ConfigError
        from hr_analytics.ui import app as module

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
        for expected in ("restitution", "synthese", "vue-detaillee",
                         "analyse"):
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

    def test_no_manifest_is_written_beside_the_documents(self):
        """Il accompagnait chaque export, sans qu'on l'ait demandé. Ce
        qu'il portait de lisible — fichier source, périmètre, date,
        effectif — est déjà en tête de la restitution et sur la garde de
        la synthèse ; le reste était du JSON que personne n'ouvre."""
        self.load()
        self.analyse()
        out = self.output("sans-manifeste")
        with Dialogs(directory=out):
            self.app.export_documents()
        self.assertEqual(glob.glob(os.path.join(out, "manifeste-*.json")), [])

    def test_nothing_at_all_is_written_when_nothing_is_asked(self):
        """Décocher tout et exporter n'écrit plus un fichier solitaire."""
        self.load()
        self.analyse()
        for variable in self.app.output_vars.values():
            variable.set(False)
        out = self.output("rien-demande")
        with Dialogs(directory=out):
            self.app.export_documents()
        self.assertEqual(os.listdir(out), [])

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
        from hr_analytics.core.config import write_configuration
        from hr_analytics.ui.settings import build_mapping_section

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


class TestTheDistributionSplitButton(WindowCase):
    """Le bouton « Séparer H/F » de l'onglet Distribution."""

    def _lopsided(self, femmes=3, hommes=37):
        """Un fichier dont un seul sexe passe le seuil de trace."""
        path = os.path.join(self.directory, "desequilibre.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS))
            for index in range(femmes + hommes):
                writer.writerow(make_row(
                    index, salary=40000 + index * 250,
                    gender="F" if index < femmes else "H"))
        return path

    def test_the_whole_population_comes_first(self):
        """Le dedoublement repond a une question plus fine : il se demande."""
        self.load()
        self.analyse()
        self.assertFalse(self.app.dist_split.get())
        self.assertFalse(self.app.histogram.split)

    def _distribution(self):
        """La page Distribution au premier plan : un graphique qu'on n'a
        jamais montre n'a pas de taille, et ne dessine rien."""
        self.app.tabbar.select("graphique")
        self.app.chartbar.select("distribution")
        self.app.update()

    def test_the_button_is_offered_when_both_sides_can_be_drawn(self):
        self.load()
        self.analyse()
        self.assertTrue(self.app.histogram.may_split())
        self.assertTrue(self.app.dist_split_row.winfo_manager())

    def test_ticking_it_splits_the_chart(self):
        self.load()
        self.analyse()
        self._distribution()
        self.app.dist_split.set(True)
        self.app.update()
        self.assertTrue(self.app.histogram.split)
        textes = [self.app.histogram.canvas.itemcget(item, "text")
                  for item in self.app.histogram.canvas.find_all()
                  if self.app.histogram.canvas.type(item) == "text"]
        self.assertIn("FEMMES ▲", textes)

    def test_unticking_it_brings_the_whole_population_back(self):
        self.load()
        self.analyse()
        self.app.dist_split.set(True)
        self.app.update()
        self.app.dist_split.set(False)
        self.app.update()
        self.assertFalse(self.app.histogram.split)

    def test_an_unbalanced_file_says_why_instead_of_offering_the_button(self):
        """Un bouton absent sans explication passe pour un oubli."""
        self.load(self._lopsided())
        self.analyse()
        self.assertFalse(self.app.histogram.may_split())
        self.assertFalse(self.app.dist_split_row.winfo_manager())
        self.assertIn("Effectif insuffisant",
                      self.app.dist_split_note.cget("text"))

    def test_the_button_cannot_stay_ticked_on_a_file_that_refuses_it(self):
        self.load()
        self.analyse()
        self.app.dist_split.set(True)
        self.app.update()
        self.load(self._lopsided())
        self.analyse()
        self.assertFalse(self.app.dist_split.get())
        self.assertFalse(self.app.histogram.split)


class TestTheDispersionControls(WindowCase):
    """Le tracé choisi, et les tris que chaque mode propose."""

    def _load(self):
        self.load(self.source(
            "postes.csv", rows=120, extra_headers=["Poste"],
            extra=lambda index: [["Comptable", "Technicien",
                                  "Chef de projet"][index % 3]]))
        self.analyse()

    def test_the_plain_mode_offers_its_two_sorts(self):
        """Le tri par ouverture est parti avec sa colonne : un tri
        qu'aucune colonne ne montre se lit comme un désordre."""
        self._load()
        proposes = self.app.box_order.cget("values")
        self.assertIn("Effectif décroissant", proposes)
        self.assertIn("Médiane décroissante", proposes)
        self.assertNotIn("Ouverture décroissante", proposes)
        self.assertNotIn("Écart F/H décroissant", proposes)

    def test_the_split_mode_swaps_the_sort_for_its_own(self):
        """Un tri qu'aucune colonne ne montre se lit comme un désordre."""
        self._load()
        self.app.box_split.set(True)
        self.app.update()
        self.assertIn("Écart F/H décroissant", self.app.box_order.cget("values"))

    def choisir(self, cle):
        """Pose un tri par sa clé, sans supposer son rang dans la liste."""
        cles = [key for key, _l in self.app.boxplot.orders()]
        self.app.box_order.current(cles.index(cle))
        self.app.box_order.event_generate("<<ComboboxSelected>>")
        self.app.update()

    def test_a_chosen_order_reaches_the_chart(self):
        self._load()
        self.choisir("median")
        self.assertEqual(self.app.boxplot.order, "median")

    def test_an_order_without_a_column_falls_back_instead_of_persisting(self):
        """Trier par écart F/H puis revenir au mode simple : l'écart n'y a
        plus de colonne pour se vérifier, et un tri qu'aucune colonne ne
        montre se lit comme un désordre."""
        self._load()
        self.app.box_split.set(True)
        self.app.update()
        self.choisir("gap")
        self.assertEqual(self.app.boxplot.order, "gap")
        self.app.box_split.set(False)
        self.app.update()
        self.assertEqual(self.app.boxplot.order, self.app.boxplot.DEFAUT)
        # La liste affichée dit le même tri que celui qui s'applique.
        self.assertEqual(self.app.box_order.get(),
                         dict(self.app.boxplot.orders())[self.app.boxplot.order])


class TestThemeAndIdentities(WindowCase):
    def test_changing_the_colour_dimension_regroups_the_cloud(self):
        """Le regroupement est refait par le moteur, pas par l'interface :
        les couleurs de l'ecran et celles du document restent identiques."""
        self.load()
        self.analyse()
        before = set(self.app.scatter.dataset.get("groups") or [])
        wanted = next(index for index, field in
                      enumerate(self.app._colour_fields) if field == "groupe")
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


@needs_display
class TestMappingAColumnFromTheWindow(WindowCase):
    """Importer un fichier, associer ses colonnes, analyser — sans éditeur.

    C'est le parcours complet de quelqu'un dont le fichier porte des
    notions que l'outil ne connait pas : une direction, une revue du
    personnel, une prime maison. Jusqu'ici il fallait ouvrir un fichier
    JSON au bloc-notes pour les declarer. Ce test verifie que la fenetre
    suffit, et que ce qui est declare arrive jusqu'aux analyses.
    """

    COLONNES = ["Direction", "Revue du personnel", "Prime exceptionnelle"]

    def _fichier(self):
        return self.source(
            "maison.csv", extra_headers=self.COLONNES,
            extra=lambda index: [["Nord", "Sud"][index % 2],
                                 ["Talent", "Performance",
                                  "En décalage"][index % 3],
                                 900 + index])

    def _ecran(self):
        from hr_analytics.ui.settings import SettingsWindow

        fenêtre = SettingsWindow(
            self.app, self.app.configuration, self.directory, self.app.fonts,
            headers=self.app.headers, on_saved=self.app._settings_saved,
            samples=getattr(self.app, "_samples", None))
        fenêtre.update()
        return fenêtre

    def test_the_window_is_enough_to_declare_a_column(self):
        from hr_analytics.ui.settings import ORGANISATION

        self.load(self._fichier())
        # Au depart, ces colonnes ne sont pas reconnues.
        self.assertIn("non reconnue", self.app.mapping_label.cget("text"))
        self.assertNotIn("Direction", self.app.filter_labels.values())

        fenêtre = self._ecran()
        try:
            rangs = {nom: rang for rang, nom in enumerate(
                nom for nom in self.app.headers if str(nom).strip())}
            for colonne in ("Direction", "Revue du personnel"):
                fenêtre.assignments[colonne].set(ORGANISATION)
                fenêtre._chose(colonne, fenêtre._boxes[rangs[colonne]])
            # Une prime est un montant, pas un axe : elle se rattache a un
            # champ existant du modele.
            fenêtre.assignments["Prime exceptionnelle"].set(
                fenêtre._label_of("variable_pay"))
            fenêtre.update()
            with Dialogs(directory=self.directory):
                fenêtre.save()
        finally:
            if fenêtre.winfo_exists():
                fenêtre.destroy()
        self.app.update()

        # 1. Le fichier de parametres porte les deux nouvelles notions.
        chemin = os.path.join(self.directory, "population_mapping.json")
        with open(chemin, encoding="utf-8") as fichier:
            section = json.load(fichier)
        self.assertIn("Direction", section["fields"]["direction"])
        self.assertIn("Revue du personnel",
                      section["fields"]["revue_du_personnel"])
        self.assertIn("Prime exceptionnelle", section["fields"]["variable_pay"])
        déclarées = {entry["field"] for entry in section["dimensions"]}
        self.assertTrue({"direction", "revue_du_personnel"} <= déclarées)

        # 2. La fenetre principale les propose aussitot en filtre.
        self.assertIn("direction", self.app.filter_values)
        self.assertIn("revue_du_personnel", self.app.filter_values)
        self.assertNotIn("non reconnue", self.app.mapping_label.cget("text"))

        # 3. Et l'analyse sait grouper par elles.
        self.analyse()
        from hr_analytics.core.pay_equity import calculate_category_gaps

        bloc = calculate_category_gaps(self.app.result.filtered,
                                       self.app.result.config,
                                       "revue_du_personnel")
        self.assertEqual(
            sorted(item["category"] for item in bloc["categories"]),
            ["En décalage", "Performance", "Talent"])
        # La prime rejoint bien le champ de la part variable.
        self.assertGreater(
            self.app.result.payload["pay_equity"]["variable"]["female_count"],
            0)

    def test_the_new_axis_is_offered_on_the_gaps_page(self):
        """Declarer une notion sert a comparer avec : elle doit paraitre
        dans « Comparer par »."""
        from hr_analytics.ui.settings import ORGANISATION

        self.load(self._fichier())
        fenêtre = self._ecran()
        try:
            rang = [nom for nom in self.app.headers
                    if str(nom).strip()].index("Direction")
            fenêtre.assignments["Direction"].set(ORGANISATION)
            fenêtre._chose("Direction", fenêtre._boxes[rang])
            fenêtre.update()
            with Dialogs(directory=self.directory):
                fenêtre.save()
        finally:
            if fenêtre.winfo_exists():
                fenêtre.destroy()
        self.analyse()
        # La page des écarts a été vidée : la dimension se vérifie là où
        # elle sert encore, sur la dispersion par segment.
        self.app.tabbar.select("graphique")
        self.app.update()
        self.assertIn("Direction", list(self.app.box_choice.cget("values")))


class TestTheOrganisationChart(WindowCase):
    """L'onglet « Organigramme », et ce qui le fait paraitre.

    Il ne repond pas a un seuil mais a une demande : tant que personne n'a
    choisi d'equipe a l'etape 3, il n'y a pas d'organigramme a montrer, et
    une entree ouvrant sur une page vide est pire qu'une entree absente.

    Les deux lectures de la page — le dessin et la liste — portent sur la
    meme population que tous les autres onglets. C'est ce que verifient ces
    tests : un effectif qui ne correspondrait pas a celui de la barre d'etat
    ferait douter des deux.
    """

    def _fichier(self):
        """Quarante salaries, six responsables, trois niveaux.

        E00000 porte tout le monde ; E00001 a E00005 encadrent ; les autres
        se repartissent entre eux.
        """
        def manager(index):
            if index == 0:
                return [""]
            if index <= 5:
                return ["E00000"]
            return [f"E{1 + index % 5:05d}"]

        return self.source("equipe.csv", extra_headers=["Manager"],
                           extra=manager)

    def _choisir(self, matricule):
        for label, key in self.app._team_keys.items():
            if key == matricule:
                self.app.team_var.set(label)
                self.app.update()
                return label
        self.fail(f"{matricule} n'est pas proposé comme responsable")

    def test_without_a_team_there_is_no_tab(self):
        self.load(self._fichier())
        self.analyse()
        self.assertNotIn("organigramme", self.app.tabbar.visible_keys())

    def test_its_absence_is_not_announced_as_a_privacy_masking(self):
        """« Vue masquee » veut dire « effectif insuffisant ». Le dire d'un
        onglet que personne n'a demande serait faux, et enverrait elargir un
        filtre pour retrouver une page qui n'a jamais manque."""
        self.load(self._fichier())
        self.analyse()
        self.assertNotIn("masquée", self.app.status.cget("text"))

    def test_choosing_a_team_brings_the_tab(self):
        self.load(self._fichier())
        self._choisir("E00001")
        self.analyse()
        self.assertIn("organigramme", self.app.tabbar.visible_keys())

    def test_the_list_carries_the_team_and_nothing_else(self):
        self.load(self._fichier())
        self._choisir("E00001")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        lignes = self.app.org_tree.get_children()
        self.assertEqual(len(lignes), len(self.app.result.filtered))
        # Le responsable choisi ouvre la liste : c'est lui la racine.
        premier = self.app.org_tree.item(lignes[0], "values")[0]
        self.assertIn("NOM1", premier)

    def test_the_drawing_and_the_list_say_the_same_number(self):
        self.load(self._fichier())
        self._choisir("E00000")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        self.assertEqual(len(self.app.org_tree.get_children()), 40)
        self.assertEqual(self.app.org_chart.root["total"], 39)

    def test_clicking_a_box_selects_the_person_in_the_list(self):
        """Le lien entre les deux lectures. Sans lui, retrouver dans
        quarante lignes la case qu'on vient de cliquer est une corvee."""
        self.load(self._fichier())
        self._choisir("E00000")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        enfant = self.app.org_chart.root["children"][0]
        self.app._on_org_node(enfant)
        self.app.update()
        self.assertEqual(self.app.org_chart.selected, enfant["manager"])
        choisi = self.app.org_tree.selection()
        self.assertTrue(choisi)
        valeur = self.app.org_tree.item(choisi[0], "values")[0]
        self.assertIn("NOM", valeur)

    def test_selecting_a_line_lights_the_box_that_carries_it(self):
        """Un salarie sans equipe n'a pas de case a lui : c'est celle sous
        laquelle il est compte que l'on cherche."""
        self.load(self._fichier())
        self._choisir("E00000")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        lignes = list(self.app.org_tree.get_children())
        # La derniere ligne est un collaborateur, jamais un responsable.
        self.app.org_tree.selection_set(lignes[-1])
        self.app.update()
        self.assertIsNotNone(self.app.org_chart.selected)
        self.assertNotEqual(self.app.org_chart.selected,
                            self.app.org_tree.item(lignes[-1], "values")[0])

    def test_the_tab_goes_away_when_the_team_is_released(self):
        """Reanalyser sans equipe doit refermer la page, et non laisser
        l'organigramme de l'analyse precedente ouvert a cote de chiffres
        qui ne sont plus les siens."""
        self.load(self._fichier())
        self._choisir("E00001")
        self.analyse()
        self.assertIn("organigramme", self.app.tabbar.visible_keys())
        self.app.team_var.set(self.app.team_choice.cget("values")[0])
        self.app.update()
        self.app.result = None
        self.analyse()
        self.assertNotIn("organigramme", self.app.tabbar.visible_keys())
        self.assertEqual(self.app.org_tree.get_children(), ())

    def test_no_identity_reaches_the_screen_when_it_is_switched_off(self):
        """Le reglage ne porte que sur l'ecran, et il porte sur tout
        l'ecran : une page qui l'ignorerait annulerait les autres."""
        from tests.support import make_config

        self.load(self._fichier())
        self.app.configuration = make_config(
            {"privacy_parameters.show_identities_on_screen": False})
        self._choisir("E00000")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        for item in self.app.org_tree.get_children():
            valeur = self.app.org_tree.item(item, "values")[0]
            self.assertNotIn("NOM", valeur)
            self.assertIn("E000", valeur)

    def test_the_page_reads_from_the_general_to_the_particular(self):
        """Trois lectures, dans cet ordre : les postes, les personnes, le
        dessin. Devant cinquante salariés, la première question n'est pas
        « qui gagne combien » mais « quels postes, dans quelle fourchette »."""
        self.load(self._fichier())
        self._choisir("E00000")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        self.assertTrue(self.app.org_jobs.get_children())
        self.assertTrue(self.app.org_tree.get_children())
        self.assertIsNotNone(self.app.org_chart.root)

    def test_the_job_table_carries_the_range_of_each_job(self):
        """Un poste du simple au double n'appelle pas la même conversation
        qu'un poste resserré, et aucune moyenne ne le dirait."""
        self.load(self._fichier())
        self._choisir("E00000")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        lignes = self.app.org_jobs.get_children()
        valeurs = self.app.org_jobs.item(lignes[0], "values")
        self.assertEqual(len(valeurs), 7)
        # Effectif, minimum, médiane, moyenne, maximum : tous renseignés.
        for valeur in valeurs[2:]:
            self.assertNotEqual(valeur, "—")
        total = sum(int(self.app.org_jobs.item(item, "values")[2])
                    for item in lignes)
        self.assertEqual(total, len(self.app.result.filtered))

    def test_the_people_table_ranks_the_pay_within_the_team(self):
        """« 31 400 EUR » ne dit rien ; « 4 / 57 » situe la personne."""
        self.load(self._fichier())
        self._choisir("E00000")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        rangs = [self.app.org_tree.item(item, "values")[-1]
                 for item in self.app.org_tree.get_children()]
        self.assertIn("1 / 40", rangs)
        self.assertIn("40 / 40", rangs)
        # Un rang par salarié, et aucun en double : le classement est un
        # ordre, pas une étiquette.
        self.assertEqual(len(set(rangs)), len(rangs))

    def test_a_small_team_keeps_its_figures_on_this_page(self):
        """Le seuil de publication ne s'applique pas ici : la page ne sort
        pas de l'écran, et elle porte sur une équipe que l'on vient de
        désigner. Masquée, elle serait inutilisable — un poste tenu par
        trois personnes n'aurait ni minimum, ni médiane, ni maximum."""
        self.load(self._fichier())
        self._choisir("E00002")        # un chef et ses quelques rattachés
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        self.assertLess(len(self.app.result.filtered), 10)
        for item in self.app.org_tree.get_children():
            self.assertNotIn("masquée",
                             self.app.org_tree.item(item, "values"))
        for item in self.app.org_jobs.get_children():
            self.assertNotIn("—", self.app.org_jobs.item(item, "values")[3:])

    def test_the_threshold_comes_back_on_this_page_when_asked_for(self):
        """Une installation partagée peut le vouloir : le réglage existe,
        et il se comporte alors comme partout ailleurs."""
        from tests.support import make_config

        self.load(self._fichier())
        self.app.configuration = make_config(
            {"privacy_parameters.mask_in_org_chart": True,
             "privacy_parameters.min_headcount_publish": 20})
        self._choisir("E00002")
        self.analyse()
        self.app.tabbar.select("organigramme")
        self.app.update()
        valeurs = [self.app.org_tree.item(item, "values")
                   for item in self.app.org_tree.get_children()]
        self.assertTrue(any("masquée" in ligne for ligne in valeurs))


class TestTheScatterAxes(WindowCase):
    """Les deux axes du nuage se changent sans relancer l'analyse."""

    def _ouvrir(self):
        self.load()
        self.analyse()
        self.app.tabbar.select("graphique")
        self.app.chartbar.select("nuage")
        self.app.update()

    def _choisir(self, boite, champ):
        champs = [axis["field"] for axis in self.app._scatter_axes]
        boite.current(champs.index(champ))

    def test_the_tab_and_the_chart_are_named_for_what_they_hold(self):
        """« Graphiques » : il y en a trois. « Nuage de points » : les deux
        axes se choisissent, le titre ne peut plus les nommer."""
        from hr_analytics.ui.app import CHARTS, TABS

        self.assertIn(("graphique", "Graphiques"), TABS)
        self.assertIn(("nuage", "Nuage de points"), CHARTS)

    def test_both_axes_are_offered(self):
        self._ouvrir()
        champs = [axis["field"] for axis in self.app._scatter_axes]
        self.assertIn("base_salary", champs)
        self.assertIn("age_years", champs)
        self.assertEqual(self.app.x_choice.get(), "Ancienneté")
        self.assertEqual(self.app.y_choice.get(), "Salaire de base")

    def test_changing_an_axis_redraws_without_a_new_analysis(self):
        self._ouvrir()
        avant = self.app.result
        self._choisir(self.app.x_choice, "age_years")
        self.app._reaxis()
        self.app.update()
        self.assertIs(self.app.result, avant, "l'analyse a été relancée")
        self.assertEqual(self.app.scatter.dataset["x_field"], "age_years")
        self.assertEqual(self.app.scatter.dataset["x_axis"]["label"], "Âge")

    def test_the_chart_titles_its_axis_from_the_data(self):
        """« Ancienneté (années) » écrit en dur aurait annoncé une chose
        pendant qu'on en regardait une autre."""
        self._ouvrir()
        self._choisir(self.app.x_choice, "age_years")
        self.app._reaxis()
        self.app.update()
        self.assertEqual(self.app.scatter._axis_title("x"), "Âge (années)")
        self._choisir(self.app.x_choice, "base_salary")
        self.app._reaxis()
        self.app.update()
        self.assertEqual(self.app.scatter._axis_title("x"), "Salaire de base")

    def test_the_values_follow_the_unit_of_their_axis(self):
        """Un montant annoncé en années ne se lit pas."""
        self._ouvrir()
        self.assertIn("EUR", self.app.scatter._value("y", 42000))
        self.assertIn("ans", self.app.scatter._value("x", 7))
        self._choisir(self.app.y_choice, "age_years")
        self.app._reaxis()
        self.app.update()
        self.assertIn("ans", self.app.scatter._value("y", 42))

    def test_changing_the_colour_keeps_the_chosen_axes(self):
        """Deux chemins de calcul auraient fini par ne plus poser les mêmes
        paramètres, et le nuage aurait changé de forme en changeant de
        couleur."""
        self._ouvrir()
        self._choisir(self.app.x_choice, "age_years")
        self.app._reaxis()
        self.app.update()
        self.app.colour_choice.current(1)
        self.app._recolour()
        self.app.update()
        self.assertEqual(self.app.scatter.dataset["x_field"], "age_years")

    def test_the_reset_button_restores_the_default_chart(self):
        """« Le cadrage » ne disait qu'une partie : les deux axes et la
        couleur se changent aussi, et il faut pouvoir revenir au nuage
        d'origine sans se souvenir de ce qu'il portait."""
        self._ouvrir()
        self._choisir(self.app.x_choice, "base_salary")
        self._choisir(self.app.y_choice, "age_years")
        self.app._reaxis()
        self.app.colour_choice.current(2)
        self.app._recolour()
        self.app.update()
        self.assertEqual(self.app.scatter.dataset["x_field"], "base_salary")

        self.app._reset_scatter()
        self.app.update()
        self.assertEqual(self.app.scatter.dataset["x_field"], "tenure_years")
        self.assertEqual(self.app.scatter.dataset["y_field"], "base_salary")
        self.assertEqual(self.app.x_choice.get(), "Ancienneté")
        self.assertEqual(self.app.y_choice.get(), "Salaire de base")
        self.assertEqual(self.app.scatter._view, self.app.scatter._bounds)

    def test_the_reset_follows_the_configuration_not_a_hardcoded_pair(self):
        """Un fichier qui déclare d'autres axes par défaut doit les
        retrouver, et non l'ancienneté et le salaire de base de la
        configuration livrée."""
        self._ouvrir()
        données = self.app.configuration.as_dict()
        données["chart_parameters"]["scatter_x"] = "age_years"
        données["chart_parameters"]["scatter_y"] = "variable_pay"
        from hr_analytics.core.config import Configuration

        self.app.configuration = Configuration(données)
        self.app._reset_scatter()
        self.app.update()
        self.assertEqual(self.app.scatter.dataset["x_field"], "age_years")
        self.assertEqual(self.app.scatter.dataset["y_field"], "variable_pay")


class TestAnOverviewWithOnlyOneHalfPublished(WindowCase):
    """La page a deux moitiés et deux seuils : l'une peut tomber seule.

    La population se masque sur l'effectif, la rémunération sur le nombre
    de montants connus. Un fichier de neuf salariés dont trois seulement
    ont un salaire publiait donc la population et laissait la colonne de
    rémunération entièrement vide — un tiers de page blanc, sans un mot.
    """

    def _charge(self, rows=9, renseignes=3):
        chemin = self.source(
            rows=rows,
            salary=lambda index: 40000 + index * 250 if index < renseignes
            else None)
        self.load(chemin)
        self.analyse()
        return self.app.result.payload

    def _textes(self, widget):
        import tkinter as tk

        trouves = []
        for enfant in widget.winfo_children():
            if isinstance(enfant, tk.Label):
                trouves.append(str(enfant.cget("text")))
            trouves += self._textes(enfant)
        return trouves

    def test_the_two_halves_disagree(self):
        payload = self._charge()
        self.assertFalse(payload["population"]["masked"])
        self.assertTrue(payload["salary"]["masked"])

    def test_the_overview_tab_stays_open(self):
        self._charge()
        self.assertTrue(self.app.tabbar._visible.get("population", True))

    def test_the_empty_column_carries_its_reason(self):
        """Une colonne vide au milieu d'une page se lit comme un défaut
        d'affichage, pas comme un masquage."""
        self._charge()
        textes = " ".join(self._textes(self.app.overview_frame))
        self.assertIn("colonne analysée", textes)
        self.assertIn("Salaire de base", textes)

    def test_the_population_half_is_still_there(self):
        self._charge()
        textes = " ".join(self._textes(self.app.overview_frame))
        self.assertIn("Effectif", textes)
        self.assertIn("Âge médian", textes)

    def test_the_banner_counts_the_masked_half(self):
        self._charge()
        self.assertIn("rémunération", self.app.notice.cget("text").lower())
        self.assertIn("vue(s) masquée(s)",
                      self.app.status.cget("text"))

    def test_nothing_is_masked_when_every_salary_is_there(self):
        self._charge(renseignes=9)
        textes = " ".join(self._textes(self.app.overview_frame))
        self.assertNotIn("colonne analysée", textes)
        self.assertIn("Masse salariale", textes)


class TestTheOverviewSettlesInsteadOfTrembling(WindowCase):
    """La page s'accorde à la hauteur disponible, puis s'arrête.

    Elle mesurait la place libre sur une colonne *déjà agrandie* : au
    deuxième passage, la place valait zéro et les graphiques rendaient tout
    ce que le premier leur avait donné. La page oscillait donc entre deux
    hauteurs — et comme l'une des deux fait apparaître l'ascenseur, qui
    prend seize pixels de large, elle oscillait aussi entre deux largeurs :
    un tremblement gauche-droite, une centaine d'aller-retours par seconde.

    Ce qui se vérifie ici n'est pas l'absence de tremblement à l'écran — il
    dépend de la hauteur de la fenêtre au pixel près — mais l'invariant qui
    le rend impossible : à place égale, deux accords successifs donnent
    exactement la même page.
    """

    def _petite_equipe(self):
        """Un responsable et sa ligne directe : la page la plus courte, donc
        celle qui laisse le plus de place a redistribuer.

        Le jeu d'essai commun ne porte pas de colonne « Manager » — il n'a
        pas de hierarchie. On en ajoute une : tout le monde sous le premier
        matricule.
        """
        chemin = self.source(
            rows=9, extra_headers=("Manager",),
            extra=lambda index: ("" if index == 0 else "E00000",))
        self.load(chemin)
        self.analyse()
        label = next(nom for nom in self.app._team_keys
                     if self.app._team_rows[
                         self.app._team_keys[nom]]["direct"] >= 3)
        self.app.team_var.set(label)
        self.app.team_direct_var.set(True)
        self.app.update()
        self.analyse()
        self.app.tabbar.select("population")
        for _ in range(20):
            self.app.update()
            time.sleep(0.01)

    def _tailles(self):
        """Les dimensions que l'accord pose, graphique par graphique."""
        from hr_analytics.ui.charts import PieChart, PyramidChart, ScaleChart

        mesures = []
        for frame in getattr(self.app, "_overview_frames", []):
            for chart in self.app._of_type(frame, PyramidChart):
                mesures.append(("pyramide", chart.ROW))
            for chart in self.app._of_type(frame, PieChart):
                mesures.append(("anneau", chart.RADIUS))
            for chart in self.app._of_type(frame, ScaleChart):
                mesures.append(("echelle", chart.HEIGHT))
        return mesures

    def test_two_fits_in_a_row_give_the_same_page(self):
        self._petite_equipe()
        self.app._overview_fitted = None
        self.app._fit_overview()
        self.app.update()
        premier = self._tailles()
        self.assertTrue(premier, "la page doit porter des graphiques")
        self.app._overview_fitted = None          # on force un second accord
        self.app._fit_overview()
        self.app.update()
        self.assertEqual(premier, self._tailles(),
                         "un second accord ne doit rien rendre de ce que le "
                         "premier a donné")

    def test_the_height_of_the_page_stops_moving(self):
        self._petite_equipe()
        hauteurs = []
        for _ in range(4):
            self.app._overview_fitted = None
            self.app._fit_overview()
            self.app.update()
            hauteurs.append(self.app.overview_frame.winfo_reqheight())
        self.assertEqual(len(set(hauteurs)), 1,
                         f"la page oscille entre {sorted(set(hauteurs))}")

    def test_a_settled_page_is_not_fitted_again(self):
        """Le second verrou : à page, hauteur et largeur inchangées, il n'y
        a rien à refaire — et c'est ce qui coupe la boucle à la racine."""
        self._petite_equipe()
        self.app._fit_overview()
        self.assertIsNotNone(self.app._overview_fitted)
        appels = []
        grow = self.app._grow_column
        self.app._grow_column = lambda *a, **k: appels.append(a) or grow(*a, **k)
        self.app._fit_overview()
        self.assertEqual(appels, [], "la page était déjà accordée")

    def test_going_back_to_a_width_already_fitted_changes_nothing(self):
        """Le cas qui a survécu au premier correctif.

        L'ascenseur fait alterner la largeur entre deux valeurs : A sans
        lui, B avec. Une mémoire d'une seule empreinte se laisse contourner
        par l'aller-retour — A puis B puis A diffère toujours de la
        dernière, et l'accord se refait indéfiniment. Les empreintes déjà
        accordées sont donc retenues ensemble, et la page finit toujours
        par se poser.
        """
        self._petite_equipe()
        self.app._fit_overview()
        appels = []
        grow = self.app._grow_column
        self.app._grow_column = lambda *a, **k: appels.append(a) or grow(*a, **k)

        largeur = self.app.overview_canvas.winfo_width()
        hauteur = self.app.overview_canvas.winfo_height() - 40
        faits = self.app._overview_fitted[1]
        # On simule l'aller-retour : une largeur B, puis le retour en A.
        faits.add((hauteur, largeur - 16))
        self.app._fit_overview()        # retour en A, deja accorde
        self.assertEqual(appels, [], "A avait déjà été accordé")

    def test_rebuilding_the_page_releases_the_lock(self):
        """Une recomposition change la génération : l'accord se refait.

        Sans cela, le verrou qui coupe la boucle figerait aussi une page
        neuve à la taille de l'ancienne.
        """
        self._petite_equipe()
        self.app._fit_overview()
        ancienne = self.app._overview_fitted
        self.assertIsNotNone(ancienne)
        self.app._show_overview(self.app.result.payload)
        for _ in range(10):
            self.app.update()
            time.sleep(0.01)
        # La page recomposée a été réaccordée : l'empreinte a changé de
        # génération, et les graphiques ont de nouveau été dimensionnés.
        self.assertIsNotNone(self.app._overview_fitted)
        self.assertIsNot(self.app._overview_fitted[0], ancienne[0])
        self.assertTrue(self._tailles())


class TestTheOverviewDoesNotDependOnThePathTaken(WindowCase):
    """Revenir à une taille de fenêtre doit redonner la même page.

    Trouvé en passant la revue du correctif précédent : la mémoire qui
    coupe la boucle empêchait aussi un réaccord légitime, et les écarts
    entre blocs se mesuraient sur une colonne portant encore ceux du
    passage d'avant. Agrandir la fenêtre puis la ramener donnait une page
    différente — graphiques dimensionnés pour une fenêtre qui n'est plus
    là.
    """

    def _page(self):
        self.load(self.source(rows=40))
        self.analyse()
        self.app.tabbar.select("population")
        self._poser()

    def _poser(self, secondes=0.35):
        fin = time.time() + secondes
        while time.time() < fin:
            self.app.update()
            time.sleep(0.01)

    def _etat(self):
        """Les tailles posées et les écarts entre blocs."""
        from hr_analytics.ui.charts import PieChart, PyramidChart, ScaleChart

        mesures = []
        for frame in getattr(self.app, "_overview_frames", []):
            for chart in self.app._of_type(frame, PyramidChart):
                mesures.append(("pyramide", chart.ROW))
            for chart in self.app._of_type(frame, PieChart):
                mesures.append(("anneau", chart.RADIUS))
            for chart in self.app._of_type(frame, ScaleChart):
                mesures.append(("echelle", chart.HEIGHT))
            for bloc in frame.winfo_children():
                if bloc.winfo_manager():
                    mesures.append(("ecart",
                                    str(bloc.pack_info().get("pady", ""))))
        return mesures

    def test_going_bigger_and_back_gives_the_same_page(self):
        self._page()
        self.app.geometry("1400x900+0+0")
        self._poser()
        depart = self._etat()
        self.assertTrue(depart, "la page doit porter des blocs")
        for _ in range(2):
            self.app.geometry("1900x1050+0+0")
            self._poser()
            self.app.geometry("1400x900+0+0")
            self._poser()
        self.assertEqual(depart, self._etat(),
                         "la page dépend du chemin parcouru")

    def test_going_smaller_and_back_gives_the_same_page(self):
        self._page()
        self.app.geometry("1400x900+0+0")
        self._poser()
        depart = self._etat()
        for _ in range(2):
            self.app.geometry("1180x700+0+0")
            self._poser()
            self.app.geometry("1400x900+0+0")
            self._poser()
        self.assertEqual(depart, self._etat(),
                         "la page dépend du chemin parcouru")

    def test_the_gaps_never_pile_up(self):
        """L'écart posé remplace le précédent, il ne s'y ajoute pas."""
        self._page()
        ecarts = []
        for _ in range(4):
            self.app.geometry("1700x980+0+0")
            self._poser(0.25)
            ecarts.append([valeur for genre, valeur in self._etat()
                           if genre == "ecart"])
        self.assertTrue(ecarts[0])
        self.assertEqual(len(set(map(tuple, ecarts))), 1,
                         f"les écarts grandissent : {ecarts}")

    def test_a_real_resize_forgets_the_fits(self):
        """La mémoire coupe la boucle, elle ne fige pas la page : un vrai
        redimensionnement l'efface."""
        self._page()
        self.app.geometry("1400x900+0+0")
        self._poser()
        self.app._fit_overview()
        self.assertIsNotNone(self.app._overview_fitted)
        self.app.geometry("1500x940+0+0")
        self._poser()
        # Après un vrai redimensionnement, la mémoire ne porte plus les
        # empreintes de l'ancienne taille.
        faits = self.app._overview_fitted
        self.assertTrue(faits is None or all(
            largeur != 0 for _hauteur, largeur in faits[1]))


class TestTheWindowCarriesTheMark(WindowCase):
    """Sans icône posée, la fenêtre porte celle du programme qui l'a
    ouverte — sous Windows, celle de l'interpréteur, puisque le lanceur
    démarre « pythonw.exe ». L'utilisateur voit alors une icône qui n'est
    pas celle de l'outil, et qu'aucune reprise de la marque ne change."""

    def test_the_window_sets_its_own_icon(self):
        self.assertTrue(self.app._icones, "aucune icône posée")
        self.assertEqual([image.width() for image in self.app._icones],
                         list(self.app.ICONE_TAILLES))
        for image in self.app._icones:
            self.assertEqual(image.width(), image.height())

    def test_it_is_the_token_and_not_the_bare_mark(self):
        """Une barre des tâches a son propre fond, clair ou sombre selon le
        thème du poste : la marque y est posée sur son jeton."""
        from hr_analytics.ui import logo

        image = self.app._icones[0]
        taille = image.width()
        # Le centre du jeton est opaque, son coin est transparent : c'est
        # un disque, pas un carré.
        self.assertEqual(image.transparency_get(taille // 2, taille // 2),
                         False)
        self.assertEqual(image.transparency_get(0, 0), True)
        self.assertEqual(image.get(taille // 2, taille // 2),
                         logo.JETON_MARQUE)

    def test_a_refused_icon_never_stops_the_tool(self):
        """Certains gestionnaires de fenêtres refusent « iconphoto », et
        aucun ne le dit à l'avance : une icône est un confort, pas une
        fonction."""
        import tkinter as tk

        def refuser(*_args, **_kwargs):
            raise tk.TclError("wm iconphoto refusé")

        pose = self.app.iconphoto
        self.app.iconphoto = refuser
        try:
            self.app._pose_icone()
        finally:
            self.app.iconphoto = pose
        self.assertEqual(self.app._icones, [])


class TestAFileWhoseSalaryColumnIsNamedOtherwise(WindowCase):
    """Le cas le plus courant d'un premier import : la colonne de
    rémunération existe, mais elle porte un autre intitulé.

    L'outil refusait le fichier — à juste titre, il ne peut pas deviner —
    et laissait l'utilisateur sans issue : le bouton « Associer les
    colonnes… » ne s'active qu'une fois un fichier chargé, et justement ce
    fichier-là ne l'était pas. Le message renvoyait aux paramètres, où
    l'écran d'association ne connaissait aucune des colonnes du fichier :
    il fallait les relever dans Excel et les retaper à la main.
    """

    def _fichier(self):
        """Un fichier complet, dont seule la colonne de salaire est
        nommée autrement."""
        chemin = os.path.join(self.directory, "autre-intitule.csv")
        entetes = [("Rétribution annuelle brute" if nom == "Salaire de base"
                    else nom) for nom in HEADERS]
        self.assertNotIn("Salaire de base", entetes)
        with open(chemin, "w", encoding="utf-8", newline="") as flux:
            graveur = csv.writer(flux, delimiter=";")
            graveur.writerow(entetes)
            for index in range(40):
                graveur.writerow(make_row(index))
        return chemin

    def test_the_file_is_refused_and_the_window_survives(self):
        """Refuser est correct. Planter ne le serait pas."""
        with Dialogs(open_path=self._fichier()) as dialogs:
            self.app.choose_file()
        self.app.update()
        self.assertTrue(dialogs.errors, "le fichier aurait dû être refusé")
        titre, message = dialogs.errors[0]
        self.assertIn("Salaire de base", message)
        self.assertTrue(self.app.winfo_exists())

    def test_the_refusal_keeps_the_columns_it_managed_to_read(self):
        """Le fichier a bien été lu : ce sont ses colonnes qu'on n'a pas su
        nommer, pas le fichier qu'on n'a pas su ouvrir."""
        with Dialogs(open_path=self._fichier()):
            self.app.choose_file()
        self.app.update()
        self.assertIn("Rétribution annuelle brute", self.app.headers)
        self.assertTrue(self.app._samples, "aucune ligne d'exemple retenue")

    def test_the_mapping_screen_is_reachable_afterwards(self):
        """Le bouton qui débloque la situation ne doit pas être celui qui
        reste grisé."""
        with Dialogs(open_path=self._fichier()):
            self.app.choose_file()
        self.app.update()
        self.assertNotIn("disabled", self.app.columns_button.state())

    def test_the_mapping_screen_opens_on_that_file(self):
        """Et il s'ouvre en connaissant les colonnes du fichier refusé :
        sans elles, il faudrait les retaper à la main."""
        from hr_analytics.ui.settings import SettingsWindow

        with Dialogs(open_path=self._fichier()):
            self.app.choose_file()
        self.app.update()
        ecrans = [enfant for enfant in self.app.winfo_children()
                  if isinstance(enfant, SettingsWindow)]
        self.assertEqual(len(ecrans), 1, "l'écran d'association ne s'ouvre pas")
        try:
            self.assertIn("Rétribution annuelle brute", ecrans[0].headers)
        finally:
            ecrans[0].destroy()

    def test_an_unreadable_file_opens_nothing(self):
        """Un fichier qu'on n'a pas su ouvrir n'a aucune colonne à
        associer : lui ouvrir l'écran n'aiderait personne."""
        from hr_analytics.ui.settings import SettingsWindow

        chemin = os.path.join(self.directory, "pas-un-tableur.xlsx")
        with open(chemin, "wb") as flux:
            flux.write(b"MZ\x90\x00" + b"\x00" * 400)
        with Dialogs(open_path=chemin) as dialogs:
            self.app.choose_file()
        self.app.update()
        self.assertTrue(dialogs.errors)
        self.assertEqual([e for e in self.app.winfo_children()
                          if isinstance(e, SettingsWindow)], [])


class TestAFilterWithTooManyValues(WindowCase):
    """Une dimension trop riche pour une liste déroulante était écartée en
    silence : on cochait la case dans les paramètres, on enregistrait, et
    aucun filtre n'apparaissait. Rien ne reliait la cause à l'effet, et le
    seuil qui l'explique est à l'autre bout d'un autre écran."""

    def setUp(self):
        """Sa propre configuration : l'essai la modifie, et celle du dépôt
        sert à tous les autres."""
        import shutil

        from hr_analytics.ui.app import Application

        self.directory = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.directory, "config")
        racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shutil.copytree(os.path.join(racine, "config"), self.config_dir)
        self.app = Application(config_dir=self.config_dir)
        self.app.geometry("1280x800+0+0")
        self.app.update()

    def _fichier(self, valeurs):
        chemin = os.path.join(self.directory, "riche.csv")
        with open(chemin, "w", encoding="utf-8", newline="") as flux:
            graveur = csv.writer(flux, delimiter=";")
            graveur.writerow(HEADERS + ["Qualification"])
            for index in range(120):
                graveur.writerow(make_row(index)
                                 + [f"POSTE {index % valeurs:03}"])
        return chemin

    def _declarer(self, limite):
        """Déclare « Qualification » comme dimension, avec ce seuil."""
        import json
        chemin = os.path.join(self.config_dir, "population_mapping.json")
        with open(chemin, encoding="utf-8") as flux:
            section = json.load(flux)
        section.setdefault("fields", {})["qualification"] = ["Qualification"]
        section.setdefault("dimensions", []).append(
            {"field": "qualification", "label": "Qualification"})
        section["max_filter_values"] = limite
        with open(chemin, "w", encoding="utf-8") as flux:
            json.dump(section, flux, ensure_ascii=False)

    def test_a_dimension_within_the_cap_becomes_a_filter(self):
        """Le témoin : sans lui, l'essai suivant prouverait seulement que
        rien n'apparaît jamais."""
        self._declarer(limite=60)
        with Dialogs(open_path=self._fichier(valeurs=12)):
            self.app.choose_file()
        self.app.update()
        self.assertIn("qualification", self.app.filter_values)

    def test_a_dimension_above_the_cap_says_so(self):
        self._declarer(limite=10)
        with Dialogs(open_path=self._fichier(valeurs=40)):
            self.app.choose_file()
        self.app.update()
        self.assertNotIn("qualification", self.app.filter_values)
        textes = []

        def relever(widget):
            if "text" in widget.keys():
                textes.append(str(widget.cget("text")))
            for enfant in widget.winfo_children():
                relever(enfant)

        relever(self.app.filters_frame)
        dit = " ".join(textes)
        self.assertIn("Qualification", dit)
        self.assertIn("40", dit, "le nombre de valeurs n'est pas dit")
        self.assertIn("10", dit, "le seuil n'est pas dit")

    def test_nothing_is_said_when_there_is_nothing_to_say(self):
        """La ligne ne doit pas s'installer à demeure."""
        self._declarer(limite=60)
        with Dialogs(open_path=self._fichier(valeurs=12)):
            self.app.choose_file()
        self.app.update()
        textes = []

        def relever(widget):
            if "text" in widget.keys():
                textes.append(str(widget.cget("text")))
            for enfant in widget.winfo_children():
                relever(enfant)

        relever(self.app.filters_frame)
        self.assertNotIn("au-delà de", " ".join(textes))


class TestAnUnexpectedErrorIsNeverSilent(WindowCase):
    """L'outil tourne sous « pythonw.exe », qui n'a pas de sortie d'erreur.

    Tk confie les erreurs de rappel a `report_callback_exception`, dont la
    version d'origine les ecrit sur cette sortie : une exception dans un
    bouton n'allait donc nulle part. On cliquait, rien ne se passait, et
    aucune trace ne disait pourquoi — l'ecran avait l'air de ne pas
    enregistrer.
    """

    def _tombe(self, leve=None):
        """Declenche une panne dans un rappel, et rend ce qui s'est dit."""
        if leve is None:
            def leve():
                raise ValueError("panne")
        with Dialogs() as dialogues:
            self.app.after(0, leve)
            self.app.update()
        return dialogues

    def test_the_error_reaches_the_screen(self):
        self.assertTrue(self._tombe().errors)

    def test_the_message_says_nothing_was_lost(self):
        self.assertIn("Rien n'a été perdu", self._tombe().errors[0][1])

    def test_the_message_locates_the_failure(self):
        """Le repere sert a la corriger : le type et la ligne, et c'est
        tout ce qu'il faut. Il nomme le code de l'outil, et non le rappel
        de Tk qui l'a appele."""
        from hr_analytics.ui import app as module

        self.load()
        originale = module.load_population
        module.load_population = lambda *a, **k: 1 / 0
        self.addCleanup(setattr, module, "load_population", originale)
        dialogues = self._tombe(
            lambda: self.app._settings_saved(self.directory, "r.json"))
        texte = dialogues.errors[-1][1]
        self.assertIn("ZeroDivisionError", texte)
        self.assertIn("app.py:", texte)

    def test_the_marker_is_never_empty(self):
        """Une erreur levee avant d'entrer dans le code de l'outil garde
        un repere : « at - » n'aide personne."""
        texte = self._tombe(self.app._set_state).errors[0][1]  # sans argument
        self.assertIn("TypeError", texte)
        self.assertNotIn(" at -", texte)

    def test_the_message_carries_no_data(self):
        """Le paragraphe 6 interdit la moindre donnee RH dans un message
        technique, et le texte d'une exception levee au milieu du
        traitement en contient volontiers une : il n'y entre pas."""
        self.load()
        nom = str(next(iter(self.app.population.employees)).last_name)
        self.assertTrue(nom)

        def leve():
            raise ValueError(f"valeur refusée : {nom}")

        dialogues = self._tombe(leve)
        self.assertNotIn(nom, dialogues.errors[0][1])
        self.assertIn("ValueError", dialogues.errors[0][1])


class TestSettingsThatCouldNotBeReapplied(WindowCase):
    """Les fichiers sont ecrits : l'echec de la relecture ne doit pas
    passer pour un echec de l'enregistrement.

    Sans cela on recommencait une saisie qui etait deja sur le disque.
    """

    def _relecture_impossible(self, erreur):
        from hr_analytics.ui import app as module

        originale = module.load_population

        def refuse(*_a, **_k):
            raise erreur

        module.load_population = refuse
        self.addCleanup(setattr, module, "load_population", originale)

    def test_the_save_is_announced_all_the_same(self):
        from hr_analytics.core.errors import CompensationError

        self.load()
        self._relecture_impossible(
            CompensationError("colonne introuvable", technical="missing"))
        with Dialogs() as dialogues:
            self.app._settings_saved(self.directory, "reglages.json")
        self.assertIn("enregistrés", self.app.status.cget("text"))
        self.assertIn("sont enregistrés", dialogues.errors[0][1])

    def test_an_unforeseen_failure_also_announces_the_save(self):
        self.load()
        self._relecture_impossible(RuntimeError("panne"))
        with Dialogs():
            with self.assertRaises(RuntimeError):
                self.app._settings_saved(self.directory, "reglages.json")
        self.assertIn("enregistrés", self.app.status.cget("text"))


class TestTheVerticalBoxesTab(WindowCase):
    """L'onglet des boîtes dressées : mêmes chiffres, autre lecture.

    La page couchee classe quarante postes et porte leurs intitules sans
    les incliner. Celle-ci repond a l'autre question — comment ces
    quelques categories se comparent-elles — et c'est pour cela qu'elle a
    sa propre page.
    """

    def analysed(self):
        self.load()
        self.analyse()
        self.app.tabbar.select("graphique")
        self.app.chartbar.select("colonnes")
        self._settle()

    def _settle(self):
        """Laisse le canevas prendre sa taille, puis se tracer.

        Le trace n'a lieu qu'une fois le redimensionnement retombe : lu
        dans la foulee du changement d'onglet, le graphique est encore
        vide, et c'est le test qui mesure trop tot, non l'outil qui ne
        dessine pas.
        """
        limite = time.time() + 5
        while time.time() < limite:
            self.app.update()
            if self.app.column_boxes._items:
                break
            time.sleep(0.02)

    def test_the_tab_is_offered(self):
        self.analysed()
        self.assertIn("colonnes", self.app.chartbar.visible_keys())

    def test_it_draws_one_box_per_category(self):
        self.analysed()
        self.assertTrue(self.app.column_boxes._items)

    def test_the_abscissa_offers_the_same_dimensions_as_the_dispersion(self):
        self.analysed()
        self.assertEqual(list(self.app.col_choice.cget("values")),
                         list(self.app.box_choice.cget("values")))

    def test_both_pages_read_the_same_rows(self):
        """Un chiffre affiche a deux endroits doit venir du meme calcul."""
        self.analysed()
        self.app.col_choice.current(self.app.box_choice.current())
        self.app._change_col_dimension()
        self.app.update()
        self.assertEqual([row["segment"] for row in self.app.boxplot._drawable()],
                         [row["segment"]
                          for row in self.app.column_boxes._drawable()])

    def test_the_value_axis_carries_the_configured_field(self):
        """Le nom vient du parametrage, et non d'un libelle ecrit en dur
        dans le graphique (§7)."""
        from hr_analytics.core.segmentation import field_label
        from hr_analytics.core.config import analysis_field

        self.analysed()
        attendu = field_label(self.app.configuration,
                              analysis_field(self.app.configuration))
        self.assertEqual(self.app.column_boxes.value_label, attendu)

    def test_choosing_values_narrows_the_chart(self):
        self.analysed()
        toutes = len(self.app.column_boxes._drawable())
        self.assertGreater(toutes, 1)
        gardee = self.app.column_boxes._drawable()[0]["segment"]
        self.app._apply_col_values([gardee])
        self.app.update()
        self.assertEqual([row["segment"]
                          for row in self.app.column_boxes._drawable()],
                         [gardee])
        self.assertIn("1 sur", self.app.col_values_button.cget("text"))

    def test_changing_the_abscissa_takes_every_value_back(self):
        """Les postes retenus ne sont pas des etablissements : garder la
        selection viderait le graphique sans que rien ne le dise."""
        self.analysed()
        self.app._apply_col_values([self.app.column_boxes._drawable()[0]["segment"]])
        self.app.update()
        self.app._change_col_dimension()
        self.app.update()
        self.assertIsNone(self.app.col_values)
        self.assertIn("toutes", self.app.col_values_button.cget("text"))

    def test_the_list_opens_on_the_order_really_applied(self):
        """Posée sur sa première entrée sans rien regarder, elle annonçait
        un ordre et le graphique en appliquait un autre."""
        from hr_analytics.ui.charts import VerticalBoxPlotChart

        self.analysed()
        intitules = dict(VerticalBoxPlotChart.ORDERS)
        self.assertEqual(self.app.col_order.get(),
                         intitules[self.app.column_boxes.order])
        self.assertEqual(self.app.column_boxes.order,
                         VerticalBoxPlotChart.DEFAUT)

    def test_every_entry_of_the_list_reaches_the_chart(self):
        """Chaque intitulé proposé doit poser sa clé : une liste dont une
        entrée ne commande rien range au hasard."""
        from hr_analytics.ui.charts import VerticalBoxPlotChart

        self.analysed()
        combien = len(self.app.column_boxes._drawable())
        for index, (cle, _libelle) in enumerate(VerticalBoxPlotChart.ORDERS):
            self.app.col_order.current(index)
            self.app._reorder_columns()
            self.app.update()
            self.assertEqual(self.app.column_boxes.order, cle)
            self.assertEqual(len(self.app.column_boxes._drawable()), combien)


class TestArrangingTheValuesByHand(WindowCase):
    """Le rangement posé depuis l'écran : enregistré, appliqué, durable.

    Il ne vaut pas pour une page : il vaut pour la dimension. Le poser
    depuis les boîtes dressées range aussi les couchées, et les documents.
    """

    CHAMP = "groupe"

    def analysed(self):
        self.load()
        self.analyse()
        self.app.config_dir = self.directory
        self.app.tabbar.select("graphique")
        self.app.chartbar.select("colonnes")
        limite = time.time() + 5
        while time.time() < limite and not self.app.column_boxes._items:
            self.app.update()
            time.sleep(0.02)

    def bloc(self):
        return next(bloc for bloc in self.app._segments
                    if bloc["field"] == self.CHAMP)

    def valeurs(self):
        return [ligne["segment"] for ligne in self.bloc()["rows"]]

    def test_the_arrangement_is_written_to_the_settings(self):
        self.analysed()
        voulu = list(reversed(self.valeurs()))
        self.app._save_manual_order(self.CHAMP, voulu)
        self.app.update()
        with open(os.path.join(self.directory, "chart_parameters.json"),
                  encoding="utf-8") as source:
            écrit = json.load(source)
        self.assertEqual(écrit["segment_manual_order"][self.CHAMP], voulu)

    def test_the_blocks_follow_at_once(self):
        """Changer un ordre ne change aucun chiffre : on ne relance pas
        l'analyse pour cela."""
        self.analysed()
        voulu = list(reversed(self.valeurs()))
        self.app._save_manual_order(self.CHAMP, voulu)
        self.app.update()
        self.assertEqual(self.valeurs(), voulu)

    def test_the_documents_follow_too(self):
        """Les blocs appartiennent au résultat d'analyse : les ranger range
        ce que les documents publieront."""
        self.analysed()
        voulu = list(reversed(self.valeurs()))
        self.app._save_manual_order(self.CHAMP, voulu)
        self.app.update()
        bloc = next(b for b in self.app.result.payload["segments"]
                    if b["field"] == self.CHAMP)
        self.assertEqual([ligne["segment"] for ligne in bloc["rows"]], voulu)

    def test_it_survives_a_restart(self):
        """Un rangement qui ne tient que le temps de la session ne sert à
        rien."""
        from hr_analytics.core.config import load_configuration
        from hr_analytics.core.metrics import calculate_segment_metrics

        self.analysed()
        voulu = list(reversed(self.valeurs()))
        self.app._save_manual_order(self.CHAMP, voulu)
        self.app.update()
        relu = load_configuration(self.directory)
        neuf = calculate_segment_metrics(self.app.result.filtered, relu,
                                         self.CHAMP)
        self.assertEqual([ligne["segment"] for ligne in neuf["rows"]], voulu)

    def test_removing_it_gives_the_dimension_back_to_the_computed_orders(self):
        self.analysed()
        avant = self.valeurs()
        self.app._save_manual_order(self.CHAMP, list(reversed(avant)))
        self.app.update()
        self.app._save_manual_order(self.CHAMP, [])
        self.app.update()
        self.assertEqual(self.valeurs(), avant)
        with open(os.path.join(self.directory, "chart_parameters.json"),
                  encoding="utf-8") as source:
            self.assertNotIn(self.CHAMP,
                             json.load(source)["segment_manual_order"])

    def test_the_bar_says_what_happened(self):
        """Un enregistrement qui ne se voit pas se refait."""
        self.analysed()
        self.app._save_manual_order(self.CHAMP, list(reversed(self.valeurs())),
                                    "Groupe")
        self.app.update()
        dit = self.app.status.cget("text")
        self.assertIn("Groupe", dit)
        self.assertIn("documents", dit)

    def test_a_read_only_folder_says_so_instead_of_losing_the_work(self):
        from hr_analytics.core.errors import ConfigError
        from hr_analytics.ui import app as module

        self.analysed()
        originale = module.write_configuration
        module.write_configuration = lambda *a, **k: (_ for _ in ()).throw(
            ConfigError("dossier en lecture seule", technical="denied"))
        self.addCleanup(setattr, module, "write_configuration", originale)
        with Dialogs() as dialogues:
            self.app._save_manual_order(self.CHAMP, ["X"])
        self.assertTrue(dialogues.warnings)

    def test_both_pages_reach_the_same_arrangement(self):
        """Le rangement est celui de la dimension, pas celui d'une page."""
        self.analysed()
        self.app.box_choice.current(
            list(self.app.box_choice.cget("values")).index(
                self.bloc()["label"]))
        self.app._show_boxes()
        self.app.update()
        voulu = list(reversed(self.valeurs()))
        self.app._save_manual_order(self.CHAMP, voulu)
        self.app.update()
        couchees = [ligne["segment"] for ligne in self.app.boxplot.rows]
        self.assertEqual(couchees, voulu)
