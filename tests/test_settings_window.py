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

HEADERS = ["Matricule", "Nom", "Sexe", "BU", "Groupe", "Salaire de base",
           "Prime de panier"]


@needs_display
class SettingsCase(unittest.TestCase):
    def setUp(self):
        import tkinter as tk

        from hr_analytics.ui import theme
        from hr_analytics.ui.settings import SettingsWindow
        from hr_analytics.ui.theme import Fonts

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

    def choose(self, header, role):
        """Pose un role et declenche ce que la liste declenche a l'ecran.

        `assign` ne fait qu'ecrire la variable ; les roles qui creent un
        champ — organisation, montant — passent par la reaction de la
        liste, et c'est elle que ces tests doivent exercer."""
        self.assign(header, role)
        boîte = self.window._boxes[HEADERS.index(header)]
        self.window._chose(header, boîte)


class TestAnAmountColumn(SettingsCase):
    """Une prime maison se déclare à l'écran, et non au bloc-notes.

    Une colonne creee depuis l'ecran devenait toujours un axe de texte :
    une prime n'avait aucun moyen de devenir une colonne chiffree sans
    ouvrir le fichier de parametres.
    """

    def test_it_becomes_a_numeric_money_field(self):
        from hr_analytics.ui.settings import MONTANT

        self.choose("Prime de panier", MONTANT)
        section = self.window.collect()
        champs = [nom for nom, alias in section["fields"].items()
                  if "Prime de panier" in alias]
        self.assertEqual(len(champs), 1)
        self.assertIn(champs[0], section["numeric"])
        self.assertIn(champs[0], section["money"])

    def test_it_is_not_offered_as_an_axis(self):
        from hr_analytics.ui.settings import MONTANT

        self.choose("Prime de panier", MONTANT)
        section = self.window.collect()
        self.assertNotIn("prime_de_panier",
                         [entrée["field"] for entrée in section["dimensions"]])
        self.assertFalse(self.window.dimension_vars["Prime de panier"].get())

    def test_the_column_stops_being_flagged_as_unattached(self):
        from hr_analytics.ui import theme
        from hr_analytics.ui.settings import MONTANT

        self.choose("Prime de panier", MONTANT)
        étiquette = self.window._labels_widgets["Prime de panier"]
        self.assertNotEqual(str(étiquette.cget("foreground")), theme.WARN)

    def test_an_organisation_column_stays_a_text_axis(self):
        """Le role d'a cote n'a pas bouge : il reste un axe, et il
        n'entre ni dans les nombres ni dans les montants."""
        from hr_analytics.ui.settings import ORGANISATION

        self.choose("Prime de panier", ORGANISATION)
        section = self.window.collect()
        self.assertIn("prime_de_panier",
                      [entrée["field"] for entrée in section["dimensions"]])
        self.assertNotIn("prime_de_panier", section["money"])


class TestColumnAssignment(SettingsCase):
    def test_the_file_columns_are_offered(self):
        for header in HEADERS:
            self.assertIn(header, self.window.assignments)

    def test_the_recognised_columns_start_assigned(self):
        """La liste montre un libelle, le reglage garde le nom technique.

        « employee_id » ne dit rien a qui n'a pas ecrit le logiciel ; c'est
        pourtant ce nom-la qui s'enregistre, et qui s'ecrit en ligne de
        commande.
        """
        champ = self.window._field_of
        self.assertEqual(champ(self.window.assignments["Matricule"].get()),
                         "employee_id")
        self.assertEqual(
            champ(self.window.assignments["Salaire de base"].get()),
            "base_salary")
        self.assertEqual(self.window.assignments["Matricule"].get(),
                         "Matricule")

    def test_an_unrecognised_column_starts_ignored(self):
        """Elle doit paraitre a l'ecran pour qu'on puisse la rattacher, mais
        n'entre dans rien tant qu'on ne l'a pas fait."""
        from hr_analytics.ui.settings import IGNORED

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
        from hr_analytics.core.errors import CompensationError

        self.assign("Prime de panier", "base_salary")
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("Salaire de base", caught.exception.message)
        self.assertIn("Prime de panier", caught.exception.message)

    def test_detaching_the_analysed_pay_is_refused(self):
        """Un champ obligatoire garde volontiers d'autres orthographes,
        prevues pour d'autres fichiers : ce qui compte est qu'une colonne
        *de ce fichier* le porte.

        L'ecran applique la regle du moteur et non la liste brute, qui est
        vide par defaut : sans cela il aurait laisse detacher la colonne
        de remuneration pour n'echouer qu'a l'analyse suivante.
        """
        from hr_analytics.core.errors import CompensationError
        from hr_analytics.ui.settings import IGNORED

        self.assign("Salaire de base", IGNORED)
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("Salaire de base", caught.exception.message)
        self.assertNotIn("base_salary", caught.exception.message)

    def test_detaching_an_identifier_is_allowed(self):
        """Le matricule n'est plus exige : un fichier anonymise en amont
        reste analysable, et l'ecran ne doit pas l'interdire."""
        from hr_analytics.ui.settings import IGNORED

        self.assign("Matricule", IGNORED)
        section = self.window.collect()
        self.assertNotIn("Matricule",
                         section["fields"].get("employee_id", []))

    def test_an_ignored_column_stops_being_an_alias(self):
        """L'ecran disait « ignoree » et la colonne restait declaree dans
        les parametres : l'analyse suivante la relisait, sans que rien ne le
        signale. Une fenetre de reglage qui n'obtient pas ce qu'elle affiche
        ne sert a rien."""
        from hr_analytics.ui.settings import IGNORED

        self.assign("Groupe", IGNORED)
        section = self.window.collect()
        for name, aliases in section["fields"].items():
            self.assertNotIn("Groupe", aliases, name)

    def test_the_other_spellings_of_a_field_are_kept(self):
        """« Employee ID » vise un autre fichier : detacher la colonne de
        celui-ci ne doit pas l'effacer."""
        from hr_analytics.ui.settings import IGNORED

        self.assign("Matricule", IGNORED)
        self.assign("Nom", "employee_id")
        section = self.window.collect()
        self.assertIn("Employee ID", section["fields"]["employee_id"])
        self.assertNotIn("Matricule", section["fields"]["employee_id"])

    def test_a_non_numeric_threshold_is_refused(self):
        from hr_analytics.core.errors import CompensationError

        self.window.limit_var.set("beaucoup")
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("entier", caught.exception.message)

    def test_a_threshold_of_zero_is_refused_with_its_reason(self):
        from hr_analytics.core.errors import CompensationError

        self.window.limit_var.set("0")
        with self.assertRaises(CompensationError) as caught:
            self.window.collect()
        self.assertIn("au moins 1", caught.exception.message)

    def test_a_negative_threshold_is_refused(self):
        from hr_analytics.core.errors import CompensationError

        self.window.limit_var.set("-5")
        with self.assertRaises(CompensationError):
            self.window.collect()

    def test_spaces_around_the_threshold_are_tolerated(self):
        self.window.limit_var.set("  40  ")
        self.assertEqual(self.window.collect()["max_filter_values"], 40)


class TestDimensionFlags(SettingsCase):
    def test_a_dimension_can_be_renamed(self):
        self.window.rows["groupe"]["label"].set("Niveau")
        section = self.window.collect()
        labels = {entry["field"]: entry["label"]
                  for entry in section["dimensions"]}
        self.assertEqual(labels["groupe"], "Niveau")

    def test_a_dimension_can_be_withdrawn(self):
        self.window.rows["groupe"]["declared"].set(False)
        section = self.window.collect()
        self.assertNotIn("groupe", [entry["field"]
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
        self.window.rows["groupe"]["label"].set("Niveau")
        section = self.window.collect()
        self.window.save()
        with open(os.path.join(self.directory, "population_mapping.json"),
                  encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["dimensions"],
                             section["dimensions"])

    def test_the_saved_file_can_be_loaded_back(self):
        from hr_analytics.core.config import load_configuration

        self.window.rows["groupe"]["label"].set("Niveau")
        self.window.save()
        reloaded = load_configuration(self.directory)
        labels = {entry["field"]: entry["label"]
                  for entry in reloaded.get("population_mapping.dimensions")}
        self.assertEqual(labels["groupe"], "Niveau")

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
        from hr_analytics.ui import settings as module

        saved = module.simpledialog.askstring
        module.simpledialog.askstring = lambda *_a, **_k: text
        self.addCleanup(setattr, module.simpledialog, "askstring", saved)

    def _warnings(self):
        from hr_analytics.ui import settings as module

        caught = []
        saved = module.messagebox.showwarning
        module.messagebox.showwarning = lambda *args, **kwargs: caught.append(args)
        self.addCleanup(setattr, module.messagebox, "showwarning", saved)
        return caught

    def _create(self, header="Prime de panier"):
        from hr_analytics.ui.settings import NEW_FIELD

        box = self.window._boxes[list(self.window.assignments).index(header)]
        self.window.assignments[header].set(NEW_FIELD)
        self.window._chose(header, box)
        self.window.update()
        return box

    def test_a_new_field_is_created_and_assigned(self):
        self._answer("prime_panier")
        self._create()
        self.assertEqual(
            self.window._field_of(
                self.window.assignments["Prime de panier"].get()),
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
        name = self.window._field_of(
            self.window.assignments["Prime de panier"].get())
        self.assertTrue(name.isascii(), name)
        self.assertNotIn(" ", name)

    def test_an_existing_name_is_refused_rather_than_duplicated(self):
        warned = self._warnings()
        self._answer("base_salary")
        self._create()
        self.assertTrue(warned)
        from hr_analytics.ui.settings import IGNORED

        self.assertEqual(self.window.assignments["Prime de panier"].get(),
                         IGNORED)

    def test_cancelling_leaves_the_column_ignored(self):
        from hr_analytics.ui.settings import IGNORED

        self._answer(None)
        self._create()
        self.assertEqual(self.window.assignments["Prime de panier"].get(),
                         IGNORED)

    def test_the_new_field_is_offered_to_every_other_column(self):
        """Deux colonnes d'un meme fichier doivent pouvoir parler de la
        meme chose : le champ cree est propose partout, sous son libelle."""
        self._answer("prime_panier")
        self._create()
        for other in self.window._boxes:
            self.assertIn("Prime de panier", other.cget("values"))
        self.assertEqual(self.window._field_of("Prime de panier"),
                         "prime_panier")


class TestSavingWhenTheFolderRefuses(SettingsCase):
    """Un poste verrouille est le cas nominal, pas l'exception.

    Le dossier de configuration peut etre en lecture seule : plutot que de
    perdre la saisie, la fenetre propose d'en choisir un autre.
    """

    def _dialogs(self, retry, chosen):
        from hr_analytics.ui import settings as module

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

        from hr_analytics.ui.settings import SettingsWindow
        from hr_analytics.ui.theme import Fonts

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


@needs_display
class TestTheColumnsAreVisible(SettingsCase):
    """Le bloc des colonnes doit avoir la place de se montrer.

    Il ne l'avait pas : empile entre quatre sections de hauteur fixe, il
    recevait ce qui restait — deux pixels, intitule compris. La fonction
    existait, elle etait introuvable. Ce test mesure ce que la fenetre
    montre, et non ce qu'elle contient.
    """

    def test_the_columns_block_has_room(self):
        self.window.update()
        self.assertGreater(self.window._columns_card.winfo_height(), 200,
                           "le bloc des colonnes est écrasé")

    def test_every_column_has_a_visible_row(self):
        self.window.update()
        for header in HEADERS:
            with self.subTest(colonne=header):
                self.assertIn(header, self.window.assignments)
                self.assertIn(header, self.window.dimension_vars)


@needs_display
class TestTheFourSections(SettingsCase):
    """Quatre sujets, quatre pages.

    Les cinq sections s'empilaient dans une seule colonne défilante : pour
    changer un seuil de confidentialité, il fallait traverser vingt-deux
    lignes de colonnes et deux paragraphes sur l'export. On ne cherchait
    pas un réglage, on le retrouvait.
    """

    def test_each_subject_has_its_own_page(self):
        from hr_analytics.ui.settings import SettingsWindow

        attendues = {clef for clef, _l in SettingsWindow.SECTIONS}
        self.assertEqual(set(self.window.pages), attendues)

    def test_only_one_page_is_shown_at_a_time(self):
        self.window.update()
        montrees = [clef for clef, cadre in self.window.pages.items()
                    if cadre.winfo_manager()]
        self.assertEqual(montrees, ["colonnes"])

    def test_the_window_opens_on_the_columns(self):
        """C'est la première chose qu'on vient y faire."""
        self.assertEqual(self.window.tabbar.active, "colonnes")

    def test_changing_section_swaps_the_page(self):
        self.window.tabbar.select("confidentialite")
        self.window.update()
        montrees = [clef for clef, cadre in self.window.pages.items()
                    if cadre.winfo_manager()]
        self.assertEqual(montrees, ["confidentialite"])

    def test_each_section_says_where_it_is_saved(self):
        """Savoir où part un réglage fait partie du réglage."""
        from hr_analytics.ui.settings import SettingsWindow

        for clef, _intitule in SettingsWindow.SECTIONS:
            with self.subTest(section=clef):
                self.window.tabbar.select(clef)
                self.window.update()
                self.assertIn(SettingsWindow.FICHIERS[clef],
                              self.window.origin.cget("text"))

    def test_every_setting_survives_the_split(self):
        """Les contrôles existent toujours, quelle que soit la page
        affichée : les répartir ne doit en perdre aucun."""
        for nom in ("threshold_var", "warning_var", "chart_var",
                    "identities_var", "individual_var", "audit_var",
                    "theme_var"):
            with self.subTest(reglage=nom):
                self.assertTrue(hasattr(self.window, nom))

    def test_the_section_titles_do_not_repeat_the_tab(self):
        """« CONFIDENTIALITÉ » sous l'onglet « Confidentialité » est du
        bruit : l'onglet nomme déjà la page."""
        self.window.tabbar.select("confidentialite")
        self.window.update()
        textes = []

        def parcourir(widget):
            for enfant in widget.winfo_children():
                try:
                    textes.append(str(enfant.cget("text")))
                except Exception:
                    pass
                parcourir(enfant)

        parcourir(self.window.pages["confidentialite"])
        self.assertNotIn("CONFIDENTIALITÉ", textes)


@needs_display
class TestTheRoleOfAColumn(SettingsCase):
    """Une colonne, un rôle, une case : le geste tient en une ligne."""

    def _box_of(self, header: str):
        rang = [nom for nom in HEADERS if str(nom).strip()].index(header)
        return self.window._boxes[rang]

    def test_organisation_makes_a_column_an_axis_and_a_filter(self):
        """« Organisation » fait tout : le champ, son libelle, sa case.

        C'est le cas courant — direction, etablissement, revue du
        personnel. Il demandait deux ecrans et un nom technique ; il
        demande un choix.
        """
        from hr_analytics.ui.settings import ORGANISATION

        colonne = "Prime de panier"
        self.window.assignments[colonne].set(ORGANISATION)
        self.window._chose(colonne, self._box_of(colonne))
        section = self.window.collect()
        champ = self.window._field_of(self.window.assignments[colonne].get())
        self.assertEqual(champ, "prime_de_panier")
        # La colonne devient l'alias du champ : l'association tient d'un
        # fichier a l'autre.
        self.assertIn(colonne, section["fields"][champ])
        # Et le champ est propose comme axe et comme filtre, sous le
        # libelle du fichier.
        déclarées = {entry["field"]: entry["label"]
                     for entry in section["dimensions"]}
        self.assertEqual(déclarées.get(champ), colonne)

    def test_unticking_a_column_withdraws_its_field(self):
        """La case de la ligne commande l'etat du champ, sans doublon."""
        self.window.dimension_vars["Groupe"].set(False)
        self.window.update()
        section = self.window.collect()
        self.assertNotIn("groupe",
                         [entry["field"] for entry in section["dimensions"]])

    def test_ticking_a_column_proposes_its_field(self):
        """Une colonne dont le champ n'etait pas propose le devient."""
        self.window.dimension_vars["Nom"].set(False)   # etat de depart net
        self.window.dimension_vars["BU"].set(False)
        self.window.update()
        self.window.dimension_vars["BU"].set(True)
        self.window.update()
        section = self.window.collect()
        self.assertIn("business_unit",
                      [entry["field"] for entry in section["dimensions"]])

    def test_a_field_carried_by_a_column_is_not_offered_twice(self):
        """Deux cases pour une decision finissent par se contredire."""
        libellés = [enfant.winfo_children()[0].get()
                    for enfant in self.window._dimension_area.winfo_children()]
        self.assertNotIn("Groupe", libellés)
        # Mais l'age, qu'aucune colonne ne porte, s'y trouve.
        self.assertTrue(any("ge" in str(libellé) for libellé in libellés),
                        libellés)


@needs_display
class TestTheFirstValuesAreShown(unittest.TestCase):
    """Voir ce que porte une colonne vaut mieux que lire son intitule."""

    def setUp(self):
        from hr_analytics.core.config import load_configuration
        from hr_analytics.ui.app import Application
        from hr_analytics.ui.settings import SettingsWindow

        self.app = Application()
        self.window = SettingsWindow(
            self.app, load_configuration(), tempfile.mkdtemp(),
            self.app.fonts, headers=["Matricule", "Direction"],
            samples=[["E001", "Nord"], ["E002", "Sud"], ["E003", "Nord"]])
        self.window.update()

    def tearDown(self):
        self.window.destroy()
        self.app.destroy()

    def test_the_distinct_values_are_shown(self):
        self.assertEqual(self.window._sample_of(1), "Nord · Sud")

    def test_a_long_value_is_cut_rather_than_pushing_the_row(self):
        self.window.samples = [["x" * 200, "y" * 200]]
        self.assertLessEqual(len(self.window._sample_of(0)), 44)
        self.assertTrue(self.window._sample_of(0).endswith("…"))

    def test_a_column_without_values_shows_nothing(self):
        self.window.samples = [["E001"], ["E002"]]
        self.assertEqual(self.window._sample_of(1), "")


@needs_display
class TestTheWarningFades(SettingsCase):
    """L'ambre dit « rattachée à rien ». Elle doit s'éteindre au moment où
    la colonne est rattachée — sinon l'écran alerte sur ce qui vient d'être
    réglé."""

    def _colour_of(self, header: str) -> str:
        return self.window._labels_widgets[header].cget("foreground")

    def test_an_unmapped_column_is_flagged(self):
        from hr_analytics.ui import theme

        self.assertEqual(self._colour_of("Prime de panier"), theme.WARN)
        self.assertEqual(self._colour_of("Groupe"), theme.INK_SOFT)

    def test_mapping_it_turns_the_flag_off(self):
        from hr_analytics.ui import theme
        from hr_analytics.ui.settings import ORGANISATION

        rang = [nom for nom in HEADERS
                if str(nom).strip()].index("Prime de panier")
        self.window.assignments["Prime de panier"].set(ORGANISATION)
        self.window._chose("Prime de panier", self.window._boxes[rang])
        self.window.update()
        self.assertEqual(self._colour_of("Prime de panier"), theme.INK_SOFT)

    def test_ignoring_a_column_flags_it_again(self):
        from hr_analytics.ui import theme
        from hr_analytics.ui.settings import IGNORED

        rang = [nom for nom in HEADERS if str(nom).strip()].index("Groupe")
        self.window.assignments["Groupe"].set(IGNORED)
        self.window._chose("Groupe", self.window._boxes[rang])
        self.window.update()
        self.assertEqual(self._colour_of("Groupe"), theme.WARN)


@needs_display
class TestTheThreeHeadcountThresholds(SettingsCase):
    """Trois seuils, et non un seul affiché sur trois en service.

    Un utilisateur qui pose « 5 » dans l'écran et voit un groupe de huit
    sans boîte à moustaches ne peut pas deviner qu'un second seuil, à dix,
    gouverne les graphiques : il conclut que le réglage ne marche pas. Les
    trois sont donc à l'écran, nommés par ce qu'ils décident.
    """

    def labels(self):
        import tkinter as tk

        textes = []

        def marcher(widget):
            for enfant in widget.winfo_children():
                if isinstance(enfant, tk.Label):
                    textes.append(enfant.cget("text"))
                marcher(enfant)

        marcher(self.window)
        return " ".join(textes)

    def written(self):
        with open(os.path.join(self.directory, "privacy_parameters.json"),
                  encoding="utf-8") as handle:
            return json.load(handle)

    def test_the_three_are_offered(self):
        for variable, chemin, defaut in (
                (self.window.threshold_var,
                 "privacy_parameters.min_headcount_publish", 5),
                (self.window.warning_var,
                 "privacy_parameters.min_headcount_warning", 10),
                (self.window.chart_var,
                 "privacy_parameters.min_headcount_chart", 10)):
            self.assertEqual(variable.get(),
                             str(self.configuration.number(
                                 chemin, defaut, minimum=1, integer=True)))

    def test_each_one_says_what_it_decides(self):
        joint = self.labels()
        self.assertIn("Ne rien calculer en dessous de", joint)
        self.assertIn("Avertir sur l'interprétation en dessous de", joint)
        self.assertIn("Ne pas tracer de graphique en dessous de", joint)

    def test_the_two_sided_rule_is_written_down(self):
        """La réponse à « j'ai mis 5 et il m'en demande plus » : une
        comparaison F/H demande le seuil de chaque côté, donc le double."""
        joint = self.labels()
        self.assertIn("DE CHAQUE CÔTÉ", joint)
        self.assertIn("Organigramme", joint)

    def test_the_three_are_written_to_the_file(self):
        self.window.threshold_var.set("7")
        self.window.warning_var.set("14")
        self.window.chart_var.set("21")
        self.window.save()
        écrit = self.written()
        self.assertEqual(écrit["min_headcount_publish"], 7)
        self.assertEqual(écrit["min_headcount_warning"], 14)
        self.assertEqual(écrit["min_headcount_chart"], 21)

    def test_an_unreadable_entry_keeps_the_value_in_place(self):
        """Un seuil protège des personnes : il ne se perd pas sur une
        frappe."""
        avant = self.configuration.number(
            "privacy_parameters.min_headcount_chart", 10, minimum=1,
            integer=True)
        self.window.chart_var.set("beaucoup")
        self.window.save()
        self.assertEqual(self.written()["min_headcount_chart"], avant)


@needs_display
class TestOrderingTheFilters(unittest.TestCase):
    """L'ordre des filtres était celui du fichier de configuration, c'est-à-
    dire celui d'origine : personne ne range ses filtres en éditant un
    JSON. Or celui qu'on emploie tous les jours doit être en haut, et ce
    qui est en haut dépend du métier de chacun."""

    def setUp(self):
        import shutil

        from hr_analytics.ui.app import Application

        self.directory = tempfile.mkdtemp()
        racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(self.directory, "config")
        shutil.copytree(os.path.join(racine, "config"), self.config_dir)
        self.app = Application(config_dir=self.config_dir)
        self.app.update()

    def tearDown(self):
        # Les fenetres avant l'application : detruire l'application
        # d'abord laisse les Toplevel sans interpreteur.
        for fenetre in getattr(self, "_ouvertes", []):
            if fenetre.winfo_exists():
                fenetre.destroy()
        self.app.destroy()

    def _fenetre(self):
        from hr_analytics.ui.settings import SettingsWindow

        fenetre = SettingsWindow(self.app, self.app.configuration,
                                 self.config_dir, self.app.fonts)
        self.app.update()
        self._ouvertes = getattr(self, "_ouvertes", []) + [fenetre]
        return fenetre

    def test_a_dimension_can_be_moved_down(self):
        fenetre = self._fenetre()
        avant = list(fenetre.rows)
        fenetre._move_dimension(avant[0], 1)
        self.app.update()
        apres = list(fenetre.rows)
        self.assertEqual(apres[0], avant[1])
        self.assertEqual(apres[1], avant[0])
        self.assertEqual(sorted(apres), sorted(avant), "un champ a disparu")

    def test_a_dimension_can_be_moved_up(self):
        fenetre = self._fenetre()
        avant = list(fenetre.rows)
        fenetre._move_dimension(avant[2], -1)
        self.app.update()
        self.assertEqual(list(fenetre.rows)[1], avant[2])

    def test_the_ends_of_the_list_hold(self):
        """Monter le premier ou descendre le dernier ne doit rien casser."""
        fenetre = self._fenetre()
        avant = list(fenetre.rows)
        fenetre._move_dimension(avant[0], -1)
        fenetre._move_dimension(avant[-1], 1)
        self.app.update()
        self.assertEqual(list(fenetre.rows), avant)

    def test_the_new_order_reaches_the_saved_settings(self):
        """Déplacer sans que l'ordre arrive au fichier ne servirait à
        rien : c'est lui que la fenêtre relit pour ranger ses filtres."""
        from hr_analytics.core.config import load_configuration
        from hr_analytics.core.segmentation import dimension_fields

        fenetre = self._fenetre()
        avant = list(fenetre.rows)
        # Un champ coché, qu'on remonte en tête.
        coche = next(nom for nom in avant if fenetre.rows[nom]["declared"].get())
        while list(fenetre.rows).index(coche) > 0:
            fenetre._move_dimension(coche, -1)
        self.app.update()
        fenetre.save()
        self.app.update()
        relu = load_configuration(self.config_dir)
        self.assertEqual(dimension_fields(relu)[0], coche)
