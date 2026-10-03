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
        from hr_insight.ui import app as module

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
        from hr_insight.ui import app as module

        (module.filedialog.askopenfilename, module.filedialog.askdirectory,
         module.messagebox.showerror, module.messagebox.showinfo,
         module.messagebox.showwarning) = self.saved


@needs_display
class WindowCase(unittest.TestCase):
    def setUp(self):
        from hr_insight.ui.app import Application

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
        from hr_insight.ui import app as module

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
        from hr_insight.core.errors import ConfigError
        from hr_insight.ui import app as module

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
        from hr_insight.core.config import write_configuration
        from hr_insight.ui.settings import build_mapping_section

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
        from hr_insight.ui.settings import SettingsWindow

        fenêtre = SettingsWindow(
            self.app, self.app.configuration, self.directory, self.app.fonts,
            headers=self.app.headers, on_saved=self.app._settings_saved,
            samples=getattr(self.app, "_samples", None))
        fenêtre.update()
        return fenêtre

    def test_the_window_is_enough_to_declare_a_column(self):
        from hr_insight.ui.settings import ORGANISATION

        self.load(self._fichier())
        # Au depart, ces colonnes ne sont pas reconnues.
        self.assertIn("non reconnue", self.app.mapping_label.cget("text"))
        self.assertNotIn("Direction",
                         [self.app.filter_labels[field]
                          for field in self.app.filter_vars]
                         if hasattr(self.app, "filter_labels")
                         else list(self.app.filter_vars))

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
        self.assertIn("direction", self.app.filter_vars)
        self.assertIn("revue_du_personnel", self.app.filter_vars)
        self.assertNotIn("non reconnue", self.app.mapping_label.cget("text"))

        # 3. Et l'analyse sait grouper par elles.
        self.analyse()
        from hr_insight.core.pay_equity import calculate_category_gaps

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
        from hr_insight.ui.settings import ORGANISATION

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
        self.app.tabbar.select("equite")
        self.app.update()
        self.assertIn("direction", self.app._category_fields)
        self.assertIn("Direction",
                      list(self.app.category_choice.cget("values")))


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
        from hr_insight.ui.app import CHARTS, TABS

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
        from hr_insight.core.config import Configuration

        self.app.configuration = Configuration(données)
        self.app._reset_scatter()
        self.app.update()
        self.assertEqual(self.app.scatter.dataset["x_field"], "age_years")
        self.assertEqual(self.app.scatter.dataset["y_field"], "variable_pay")
