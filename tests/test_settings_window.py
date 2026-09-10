"""La fenetre de parametrage : ce qu'elle refuse d'enregistrer.

C'est l'ecran qui decide de la lecture du fichier. Une erreur de mapping ne
provoque aucun message a l'analyse : elle change les chiffres. Deux colonnes
posees sur un meme champ, un champ obligatoire detache, un seuil a zero —
chacun de ces cas rend une analyse plausible et fausse. Ils doivent etre
refuses ici, avec une phrase qui dit quoi corriger.

Ces tests exigent un affichage ; ils sont ignores automatiquement sans lui.
Aucune donnee RH reelle.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import make_config

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

HEADERS = ["Matricule", "Nom", "Sexe", "BU", "Grade", "Salaire de base",
           "Prime de panier"]


@needs_display
class SettingsCase(unittest.TestCase):
    def setUp(self):
        import tkinter as tk

        from compensation_analytics.ui import theme
        from compensation_analytics.ui.settings import SettingsWindow
        from compensation_analytics.ui.theme import Fonts

        self.directory = tempfile.mkdtemp()
        self.root = tk.Tk()
        self.root.withdraw()
        theme.install(self.root) if hasattr(theme, "install") else None
        self.configuration = make_config()
        self.window = SettingsWindow(self.root, self.configuration,
                                     self.directory, Fonts(self.root), headers=HEADERS)
        self.root.update()

    def tearDown(self):
        try:
            self.window.destroy()
        except Exception:                              # deja detruite
            pass
        self.root.destroy()

    def assign(self, header, field_name):
        self.window.assignments[header].set(field_name)


class TestColumnAssignment(SettingsCase):
    def test_the_file_columns_are_offered(self):
        for header in HEADERS:
            self.assertIn(header, self.window.assignments)

    def test_the_recognised_columns_start_assigned(self):
        self.assertEqual(self.window.assignments["Matricule"].get(),
                         "employee_id")
        self.assertEqual(self.window.assignments["Salaire de base"].get(),
                         "base_salary")

    def test_an_unrecognised_column_starts_ignored(self):
        """Elle doit paraitre a l'ecran pour qu'on puisse la rattacher, mais
        n'entre dans rien tant qu'on ne l'a pas fait."""
        from compensation_analytics.ui.settings import IGNORED

        self.assertEqual(self.window.assignments["Prime de panier"].get(),
                         IGNORED)

    def test_a_sound_screen_produces_a_section(self):
        section = self.window.collect()
        self.assertIn("fields", section)
        self.assertIn("employee_id", section["fields"])
        self.assertIn("Matricule", section["fields"]["employee_id"])

    def test_an_ignored_column_stays_out_of_the_section(self):
        section = self.window.collect()
        for aliases in section["fields"].values():
            self.assertNotIn("Prime de panier", aliases)

    def test_a_column_can_be_attached_to_another_field(self):
        self.assign("Prime de panier", "variable_pay")
        section = self.window.collect()
        self.assertIn("Prime de panier", section["fields"]["variable_pay"])


class TestRefusals(SettingsCase):
    def test_two_columns_on_one_field_are_refused(self):
        """L'une ecraserait l'autre en silence, et l'analyse porterait sur
        la mauvaise."""
        from compensation_analytics.core.errors import CompensationError

        self.assign("Prime de panier", "base_salary")
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("Salaire de base", caught.exception.message)
        self.assertIn("Prime de panier", caught.exception.message)

    def test_detaching_a_required_field_is_refused(self):
        """Un champ obligatoire garde volontiers d'autres orthographes,
        prevues pour d'autres fichiers : ce qui compte est qu'une colonne
        *de ce fichier* le porte."""
        from compensation_analytics.core.errors import CompensationError
        from compensation_analytics.ui.settings import IGNORED

        self.assign("Matricule", IGNORED)
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("employee_id", caught.exception.message)

    def test_an_ignored_column_stops_being_an_alias(self):
        """L'ecran disait « ignoree » et la colonne restait declaree dans
        les parametres : l'analyse suivante la relisait, sans que rien ne le
        signale. Une fenetre de reglage qui n'obtient pas ce qu'elle affiche
        ne sert a rien."""
        from compensation_analytics.ui.settings import IGNORED

        self.assign("Grade", IGNORED)
        section = self.window.collect()
        for name, aliases in section["fields"].items():
            self.assertNotIn("Grade", aliases, name)

    def test_the_other_spellings_of_a_field_are_kept(self):
        """« Employee ID » vise un autre fichier : detacher la colonne de
        celui-ci ne doit pas l'effacer."""
        from compensation_analytics.ui.settings import IGNORED

        self.assign("Matricule", IGNORED)
        self.assign("Nom", "employee_id")
        section = self.window.collect()
        self.assertIn("Employee ID", section["fields"]["employee_id"])
        self.assertNotIn("Matricule", section["fields"]["employee_id"])

    def test_a_non_numeric_threshold_is_refused(self):
        from compensation_analytics.core.errors import CompensationError

        self.window.limit_var.set("beaucoup")
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("entier", caught.exception.message)

    def test_a_threshold_of_zero_is_refused_with_its_reason(self):
        from compensation_analytics.core.errors import CompensationError

        self.window.limit_var.set("0")
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("au moins 1", caught.exception.message)

    def test_a_negative_threshold_is_refused(self):
        from compensation_analytics.core.errors import CompensationError

        self.window.limit_var.set("-5")
        with self.assertRaises(CompensationError):
            self.window.collect()

    def test_spaces_around_the_threshold_are_tolerated(self):
        self.window.limit_var.set("  40  ")
        self.assertEqual(self.window.collect()["max_filter_values"], 40)


class TestDimensionFlags(SettingsCase):
    def test_a_dimension_can_be_renamed(self):
        self.window.rows["grade"]["label"].set("Niveau")
        section = self.window.collect()
        labels = {entry["field"]: entry["label"]
                  for entry in section["dimensions"]}
        self.assertEqual(labels["grade"], "Niveau")

    def test_a_dimension_can_be_withdrawn(self):
        self.window.rows["grade"]["declared"].set(False)
        section = self.window.collect()
        self.assertNotIn("grade", [entry["field"]
                                   for entry in section["dimensions"]])

    def test_a_field_can_become_a_dimension(self):
        self.window.rows["status"]["declared"].set(True)
        section = self.window.collect()
        self.assertIn("status", [entry["field"]
                                 for entry in section["dimensions"]])


class TestSaving(SettingsCase):
    def test_saving_writes_a_readable_file(self):
        self.window.save()
        path = os.path.join(self.directory, "population_mapping.json")
        self.assertTrue(os.path.isfile(path))
        with open(path, encoding="utf-8") as handle:
            self.assertIn("fields", json.load(handle))

    def test_what_is_saved_is_what_the_screen_showed(self):
        self.window.rows["grade"]["label"].set("Niveau")
        section = self.window.collect()
        self.window.save()
        with open(os.path.join(self.directory, "population_mapping.json"),
                  encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["dimensions"],
                             section["dimensions"])

    def test_the_saved_file_can_be_loaded_back(self):
        from compensation_analytics.core.config import load_configuration

        self.window.rows["grade"]["label"].set("Niveau")
        self.window.save()
        reloaded = load_configuration(self.directory)
        labels = {entry["field"]: entry["label"]
                  for entry in reloaded.get("population_mapping.dimensions")}
        self.assertEqual(labels["grade"], "Niveau")

    def test_a_refused_screen_writes_nothing(self):
        """La saisie ne doit pas se perdre, et le fichier ne doit pas
        recevoir la moitie d'un reglage."""
        import tkinter.messagebox as messagebox

        self.assign("Prime de panier", "base_salary")
        warned = []
        original = messagebox.showwarning
        messagebox.showwarning = lambda *args, **kwargs: warned.append(args)
        try:
            self.window.save()
        finally:
            messagebox.showwarning = original
        self.assertTrue(warned)
        self.assertFalse(os.path.isfile(
            os.path.join(self.directory, "population_mapping.json")))


class TestCreatingAField(SettingsCase):
    """Rattacher une colonne a un champ qui n'existe pas encore.

    C'est ce qui permet d'analyser une notion propre a l'entreprise — une
    prime maison, un dispositif local — sans toucher au code.
    """

    def _answer(self, text):
        """Remplace la boite de saisie du systeme."""
        from compensation_analytics.ui import settings as module

        saved = module.simpledialog.askstring
        module.simpledialog.askstring = lambda *_a, **_k: text
        self.addCleanup(setattr, module.simpledialog, "askstring", saved)

    def _warnings(self):
        from compensation_analytics.ui import settings as module

        caught = []
        saved = module.messagebox.showwarning
        module.messagebox.showwarning = lambda *args, **kwargs: caught.append(args)
        self.addCleanup(setattr, module.messagebox, "showwarning", saved)
        return caught

    def _create(self, header="Prime de panier"):
        from compensation_analytics.ui.settings import NEW_FIELD

        box = self.window._boxes[list(self.window.assignments).index(header)]
        self.window.assignments[header].set(NEW_FIELD)
        self.window._chose(header, box)
        self.window.update()
        return box

    def test_a_new_field_is_created_and_assigned(self):
        self._answer("prime_panier")
        self._create()
        self.assertEqual(self.window.assignments["Prime de panier"].get(),
                         "prime_panier")
        section = self.window.collect()
        self.assertIn("Prime de panier", section["fields"]["prime_panier"])

    def test_the_new_field_becomes_a_dimension(self):
        self._answer("prime_panier")
        self._create()
        section = self.window.collect()
        self.assertIn("prime_panier",
                      [entry["field"] for entry in section["dimensions"]])

    def test_the_name_is_made_writable_on_the_command_line(self):
        """Sans accent ni espace : il s'ecrit aussi en ligne de commande."""
        self._answer("Prime de Panier été")
        self._create()
        name = self.window.assignments["Prime de panier"].get()
        self.assertTrue(name.isascii(), name)
        self.assertNotIn(" ", name)

    def test_an_existing_name_is_refused_rather_than_duplicated(self):
        warned = self._warnings()
        self._answer("base_salary")
        self._create()
        self.assertTrue(warned)
        from compensation_analytics.ui.settings import IGNORED

        self.assertEqual(self.window.assignments["Prime de panier"].get(),
                         IGNORED)

    def test_cancelling_leaves_the_column_ignored(self):
        from compensation_analytics.ui.settings import IGNORED

        self._answer(None)
        self._create()
        self.assertEqual(self.window.assignments["Prime de panier"].get(),
                         IGNORED)

    def test_the_new_field_is_offered_to_every_other_column(self):
        self._answer("prime_panier")
        box = self._create()
        for other in self.window._boxes:
            self.assertIn("prime_panier", other.cget("values"))


class TestSavingWhenTheFolderRefuses(SettingsCase):
    """Un poste verrouille est le cas nominal, pas l'exception.

    Le dossier de configuration peut etre en lecture seule : plutot que de
    perdre la saisie, la fenetre propose d'en choisir un autre.
    """

    def _dialogs(self, retry, chosen):
        from compensation_analytics.ui import settings as module

        asked = []
        saved = (module.messagebox.askretrycancel,
                 module.filedialog.askdirectory)
        module.messagebox.askretrycancel = lambda *a, **k: (asked.append(a)
                                                            or retry)
        module.filedialog.askdirectory = lambda *a, **k: chosen
        self.addCleanup(
            lambda: (setattr(module.messagebox, "askretrycancel", saved[0]),
                     setattr(module.filedialog, "askdirectory", saved[1])))
        return asked

    def _lock(self):
        """Un chemin qui n'est pas un dossier : l'ecriture y echoue."""
        blocked = os.path.join(self.directory, "verrou")
        with open(blocked, "w", encoding="utf-8") as handle:
            handle.write("x")
        self.window.config_dir = blocked
        return blocked

    def test_another_folder_is_offered_and_used(self):
        self._lock()
        elsewhere = os.path.join(self.directory, "ailleurs")
        os.makedirs(elsewhere, exist_ok=True)
        asked = self._dialogs(retry=True, chosen=elsewhere)
        self.window.save()
        self.assertTrue(asked)
        self.assertTrue(os.path.isfile(
            os.path.join(elsewhere, "population_mapping.json")))

    def test_declining_keeps_the_screen_open_and_writes_nothing(self):
        blocked = self._lock()
        self._dialogs(retry=False, chosen="")
        self.window.save()
        self.assertTrue(os.path.isfile(blocked))
        self.assertTrue(self.window.winfo_exists())

    def test_cancelling_the_folder_choice_writes_nothing(self):
        self._lock()
        self._dialogs(retry=True, chosen="")
        self.window.save()
        self.assertTrue(self.window.winfo_exists())

    def test_the_caller_is_told_where_the_settings_went(self):
        """La fenetre principale doit relire le fichier depuis le bon
        dossier, qui n'est pas forcement celui qu'elle avait."""
        elsewhere = os.path.join(self.directory, "ailleurs2")
        os.makedirs(elsewhere, exist_ok=True)
        self._lock()
        self._dialogs(retry=True, chosen=elsewhere)
        told = []
        self.window.on_saved = lambda directory, path: told.append(directory)
        self.window.save()
        self.assertEqual(told, [elsewhere])


@needs_display
class TestWithoutAFile(unittest.TestCase):
    """La fenetre s'ouvre aussi avant tout import."""

    def test_it_says_what_to_do_rather_than_showing_an_empty_list(self):
        import tkinter as tk

        from compensation_analytics.ui.settings import SettingsWindow
        from compensation_analytics.ui.theme import Fonts

        root = tk.Tk()
        root.withdraw()
        window = SettingsWindow(root, make_config(), tempfile.mkdtemp(),
                                Fonts(root), headers=[])
        root.update()
        texts = []

        def walk(widget):
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    texts.append(child.cget("text"))
                walk(child)

        walk(window)
        self.assertTrue(any("Chargez un fichier" in text for text in texts))
        self.assertEqual(window.assignments, {})
        window.destroy()
        root.destroy()


if __name__ == "__main__":
    unittest.main()
