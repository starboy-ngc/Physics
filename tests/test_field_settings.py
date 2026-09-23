"""Parametrage des champs : ce que la fenetre ecrit dans la configuration.

La composition de la section est une fonction pure, testee sans ouvrir la
moindre fenetre : ce qui compte est le fichier produit, pas l'ecran qui l'a
saisi. Les tests d'interface, eux, restent ignores sans affichage.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from hr_insight.core.config import (Configuration, DEFAULTS,
                                    write_default_configuration,
                                                load_configuration,
                                                write_configuration)
from hr_insight.core.errors import ConfigError
from hr_insight.core.segmentation import (dimension_fields,
                                                      dimensions,
                                                      max_filter_values)

try:
    import tkinter  # noqa: F401
    HAS_TK = True
except ImportError:
    HAS_TK = False


def configuration(**overrides):
    data = json.loads(json.dumps(DEFAULTS))
    data["population_mapping"].update(overrides)
    return Configuration(data)


class TestDeclaredDimensions(unittest.TestCase):
    """Une dimension sert partout de la meme facon.

    Les drapeaux qui dissociaient « propose en filtre » de « propose comme
    axe » ont ete retires : sur onze dimensions livrees, aucune ne les
    distinguait. Deux notions la ou une suffit ne se paient qu'en confusion.
    """

    def test_a_declared_dimension_is_available_everywhere(self):
        config = configuration(dimensions=[{"field": "grade", "label": "Grade"}])
        self.assertEqual(dimension_fields(config), ["grade"])
        self.assertEqual(dimensions(config),
                         [{"field": "grade", "label": "Grade"}])

    def test_a_bare_string_still_declares_a_dimension(self):
        config = configuration(dimensions=["grade"])
        self.assertEqual(dimension_fields(config), ["grade"])

    def test_an_undeclared_field_is_offered_nowhere(self):
        config = configuration(dimensions=[{"field": "grade", "label": "Grade"}])
        self.assertNotIn("site", dimension_fields(config))


class TestFilterValueLimit(unittest.TestCase):
    def test_the_limit_has_a_default(self):
        self.assertEqual(max_filter_values(configuration()), 60)

    def test_the_limit_is_configurable(self):
        self.assertEqual(max_filter_values(configuration(max_filter_values=8)), 8)

    def test_an_unusable_limit_is_refused_with_a_readable_message(self):
        """Zero ne proposerait plus aucun filtre, sans que rien ne l'explique."""
        for bad in (0, -3):
            with self.assertRaises(ConfigError) as raised:
                max_filter_values(configuration(max_filter_values=bad))
            self.assertIn("au moins 1", str(raised.exception))
        with self.assertRaises(ConfigError):
            max_filter_values(configuration(max_filter_values="beaucoup"))


class TestWritingConfiguration(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def test_a_written_section_is_read_back_identically(self):
        section = {"fields": {"employee_id": ["Matricule"],
                              "base_salary": ["Salaire"]},
                   "dimensions": [{"field": "grade", "label": "Grade"}],
                   "required": ["employee_id", "base_salary"]}
        write_configuration(self.directory, "population_mapping", section)
        reloaded = load_configuration(self.directory)
        self.assertEqual(reloaded.get("population_mapping.dimensions"),
                         section["dimensions"])

    def test_an_unknown_section_is_refused(self):
        with self.assertRaises(ConfigError):
            write_configuration(self.directory, "parametres_inventes", {})

    def test_no_partial_file_is_left_behind(self):
        """L'ecriture passe par un fichier temporaire renomme : aucun
        ".tmp" ne doit survivre a une ecriture reussie."""
        write_configuration(self.directory, "population_mapping", {"fields": {}})
        self.assertEqual(
            [name for name in os.listdir(self.directory) if name.endswith(".tmp")],
            [])


class TestWhereTheConfigurationLives(unittest.TestCase):
    """Ou le parametrage est lu et ecrit quand rien n'est impose.

    Un simple "config" relatif designe le repertoire courant : lance depuis
    ailleurs, l'outil repartait sur les defauts embarques sans le dire, et
    le parametrage enregistre semblait perdu.
    """

    def setUp(self):
        from hr_insight.core.config import default_config_dir
        self.resolve = default_config_dir
        self.previous = os.getcwd()
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        os.chdir(self.previous)

    def test_a_config_folder_here_is_used(self):
        """Un parametrage par dossier de travail reste possible."""
        os.makedirs(os.path.join(self.directory, "config"))
        os.chdir(self.directory)
        self.assertEqual(os.path.realpath(self.resolve()),
                         os.path.realpath(os.path.join(self.directory, "config")))

    def test_otherwise_the_folder_beside_the_tool_is_used(self):
        os.chdir(self.directory)
        resolved = self.resolve()
        self.assertEqual(os.path.basename(resolved), "config")
        # Il accompagne l'outil, pas le repertoire de lancement.
        self.assertNotEqual(os.path.realpath(os.path.dirname(resolved)),
                            os.path.realpath(self.directory))

    def test_the_resolved_folder_is_always_absolute(self):
        """Un chemin relatif changerait de sens au moindre changement de
        repertoire courant, et l'enregistrement atterrirait ailleurs."""
        os.chdir(self.directory)
        self.assertTrue(os.path.isabs(self.resolve()))


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestComposingTheSection(unittest.TestCase):
    """La composition ne demande pas d'affichage : seul l'import le demande."""

    def _build(self, **kwargs):
        from hr_insight.ui.settings import build_mapping_section
        return build_mapping_section(**kwargs)

    def test_an_assigned_column_becomes_the_first_alias(self):
        """C'est ce qui rend l'association durable : le fichier suivant,
        avec le meme en-tete, sera reconnu sans reparametrage."""
        section = self._build(
            current={"fields": {"business_unit": ["BU", "Business Unit"]},
                     "dimensions": []},
            assignments={"Direction": "business_unit"},
            dimension_flags={}, limit=60)
        self.assertEqual(section["fields"]["business_unit"][0], "Direction")
        # Les alias existants sont conserves : d'autres fichiers en dependent.
        self.assertIn("Business Unit", section["fields"]["business_unit"])

    def test_reassigning_the_same_column_does_not_duplicate_it(self):
        section = self._build(
            current={"fields": {"grade": ["Grade"]}, "dimensions": []},
            assignments={"Grade": "grade"}, dimension_flags={}, limit=60)
        self.assertEqual(section["fields"]["grade"].count("Grade"), 1)

    def test_an_ignored_column_declares_nothing(self):
        from hr_insight.ui.settings import IGNORED
        section = self._build(
            current={"fields": {}, "dimensions": []},
            assignments={"Commentaire libre": IGNORED},
            dimension_flags={}, limit=60)
        self.assertEqual(section["fields"], {})

    def test_a_new_column_creates_its_field(self):
        section = self._build(
            current={"fields": {}, "dimensions": []},
            assignments={"Direction": "direction"},
            dimension_flags={"direction": {"label": "Direction",
                                           "declared": True}},
            limit=60)
        self.assertEqual(section["fields"]["direction"], ["Direction"])
        self.assertEqual(section["dimensions"],
                         [{"field": "direction", "label": "Direction"}])

    def test_a_declared_dimension_is_written_plainly(self):
        """Le fichier reste lisible a la main : un champ, un libelle."""
        section = self._build(
            current={"fields": {}, "dimensions": []}, assignments={},
            dimension_flags={
                "grade": {"label": "Grade", "declared": True},
                "site": {"label": "Site", "declared": True},
            }, limit=60)
        self.assertEqual(section["dimensions"], [
            {"field": "grade", "label": "Grade"},
            {"field": "site", "label": "Site"},
        ])

    def test_an_unchecked_field_is_not_a_dimension(self):
        section = self._build(
            current={"fields": {}, "dimensions": []}, assignments={},
            dimension_flags={"fte": {"label": "ETP", "declared": False}},
            limit=60)
        self.assertEqual(section["dimensions"], [])

    def test_a_dimension_the_window_never_shows_is_preserved(self):
        """Un champ nominatif declare a la main n'apparait pas dans la
        fenetre. Le supprimer parce qu'elle ne l'affiche pas ferait perdre
        un parametrage sans le dire."""
        section = self._build(
            current={"fields": {},
                     "dimensions": [{"field": "last_name", "label": "Nom"}]},
            assignments={},
            dimension_flags={"grade": {"label": "Grade", "declared": True}},
            limit=60)
        self.assertIn({"field": "last_name", "label": "Nom"},
                      section["dimensions"])

    def test_the_limit_is_carried_into_the_section(self):
        section = self._build(current={"fields": {}, "dimensions": []},
                              assignments={}, dimension_flags={}, limit=25)
        self.assertEqual(section["max_filter_values"], 25)


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestFieldNameSuggestion(unittest.TestCase):
    def test_a_header_becomes_an_ascii_field_name(self):
        """Les noms de champ s'ecrivent en ligne de commande : un accent y
        serait une source d'erreur de saisie, pas un confort."""
        from hr_insight.ui.settings import suggest_field_name
        self.assertEqual(suggest_field_name("Direction régionale", []),
                         "direction_regionale")
        self.assertEqual(suggest_field_name("N° de poste", []), "n_de_poste")

    def test_a_collision_is_suffixed(self):
        from hr_insight.ui.settings import suggest_field_name
        self.assertEqual(suggest_field_name("Grade", ["grade"]), "grade_2")

    def test_a_name_never_starts_with_a_digit(self):
        from hr_insight.ui.settings import suggest_field_name
        self.assertFalse(suggest_field_name("2024", [])[0].isdigit())


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestPrivacyOfTheDimensionList(unittest.TestCase):
    def test_nominative_fields_are_never_offered_as_an_axis(self):
        """Segmenter par nom produirait des groupes d'une personne et
        ferait entrer une identite dans une restitution."""
        from hr_insight.ui.settings import candidate_dimensions
        offered = candidate_dimensions(load_configuration())
        for field_name in ("last_name", "first_name", "employee_id",
                           "birth_date"):
            self.assertNotIn(field_name, offered)

    def test_computed_fields_are_never_offered_as_a_column(self):
        """Aucune colonne du fichier ne porte l'age : il est calcule."""
        from hr_insight.ui.settings import candidate_fields
        offered = candidate_fields(load_configuration())
        for field_name in ("age_years", "age_band", "tenure_band"):
            self.assertNotIn(field_name, offered)

    def test_computed_fields_remain_available_as_an_axis(self):
        from hr_insight.ui.settings import candidate_dimensions
        offered = candidate_dimensions(load_configuration())
        self.assertIn("age_band", offered)
        self.assertIn("tenure_band", offered)


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestTheWholeRoundTrip(unittest.TestCase):
    """De la colonne inconnue au filtre applique, sans toucher au code.

    C'est la promesse du parametrage : declarer une notion metier absente
    du modele ne doit demander aucune modification du logiciel.
    """

    def setUp(self):
        from tests.support import HEADERS, make_row
        from hr_insight.io.xlsx_writer import write_workbook
        self.directory = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.directory, "config")
        self.source = os.path.join(self.directory, "population.xlsx")
        write_workbook(self.source, [("Population",
            [HEADERS + ["Direction"]] +
            [make_row(index) + [["Nord", "Sud", "Export"][index % 3]]
             for index in range(30)])])

    def test_a_column_the_tool_never_saw_becomes_a_filter(self):
        from hr_insight.core.pipeline import load_population
        from hr_insight.core.segmentation import (apply_filters,
                                                              build_filters)
        from hr_insight.ui.settings import build_mapping_section

        base = load_configuration()
        self.assertNotIn("direction", dimension_fields(base))

        section = build_mapping_section(
            base.section("population_mapping"),
            assignments={"Direction": "direction"},
            dimension_flags={"direction": {"label": "Direction",
                                           "declared": True}},
            limit=60)
        write_configuration(self.config_dir, "population_mapping", section)

        config = load_configuration(self.config_dir)
        self.assertIn("direction", dimension_fields(config))

        population, mapping, _ = load_population(self.source, config)
        self.assertEqual(mapping.unknown_columns, [])
        selected = apply_filters(population, build_filters(
            [{"field": "direction", "operator": "eq", "value": "Sud"}], config))
        self.assertEqual(len(selected), 10)

    def test_the_columns_already_recognised_keep_working(self):
        """Declarer une colonne ne doit pas defaire le mapping existant."""
        from hr_insight.core.pipeline import load_population
        from hr_insight.ui.settings import build_mapping_section

        base = load_configuration()
        section = build_mapping_section(
            base.section("population_mapping"),
            assignments={"Direction": "direction", "BU": "business_unit"},
            dimension_flags={}, limit=60)
        write_configuration(self.config_dir, "population_mapping", section)
        population, mapping, _ = load_population(
            self.source, load_configuration(self.config_dir))
        self.assertIn("base_salary", mapping.field_to_index)
        self.assertIn("business_unit", mapping.field_to_index)
        self.assertEqual(len(population), 30)


class TestShippedConfigurationMatchesTheDefaults(unittest.TestCase):
    """Les fichiers livres materialisent les defauts embarques.

    Le piege : un fichier livre surcharge le defaut. Changer une valeur dans
    DEFAULTS sans toucher le JSON n'a donc aucun effet chez l'utilisateur —
    et rien ne le signale. C'est exactement ce qui est arrive a
    `show_trend_line`, laisse a vrai dans le fichier alors que le defaut
    etait passe a faux : la droite de tendance continuait d'etre tracee.
    """

    def _shipped(self, name):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "config", f"{name}.json")
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    def _differences(self, prefix, expected, actual, found):
        if isinstance(expected, dict) and isinstance(actual, dict):
            for key in sorted(set(expected) | set(actual)):
                self._differences(f"{prefix}.{key}" if prefix else key,
                                  expected.get(key, "<absent>"),
                                  actual.get(key, "<absent>"), found)
        elif expected != actual:
            found.append(f"{prefix} : défaut {expected!r}, livré {actual!r}")

    def test_no_shipped_value_contradicts_its_default(self):
        from hr_insight.core.config import CONFIG_FILES

        problems = []
        for name in CONFIG_FILES:
            shipped = self._shipped(name)
            if shipped is None:
                continue
            self._differences("", DEFAULTS[name], shipped, problems)
        self.assertEqual(problems, [], "\n".join([""] + problems))

    def test_every_section_is_shipped(self):
        """Un fichier manquant prive l'utilisateur des reglages qu'il
        contient : il ne saurait meme pas qu'ils existent."""
        from hr_insight.core.config import CONFIG_FILES

        for name in CONFIG_FILES:
            self.assertIsNotNone(self._shipped(name), f"{name}.json absent")

if __name__ == "__main__":
    unittest.main()


class TestNumericSettingsAreCheckedWhenRead(unittest.TestCase):
    """Un fichier de parametres se corrige au bloc-notes.

    Il s'y glisse un texte a la place d'un nombre, un zero la ou il faut au
    moins un. Le premier donnait une trace Python illisible ; le second,
    pire, une analyse silencieusement fausse — un seuil de publication a
    zero publie les indicateurs d'un segment d'une personne, c'est-a-dire sa
    remuneration.
    """

    def _config(self, **reglages):
        from hr_insight.core.config import Configuration

        donnees = make_config().as_dict()
        for chemin, valeur in reglages.items():
            section, cle = chemin.split(".", 1)
            donnees.setdefault(section, {})[cle] = valeur
        return Configuration(donnees)

    def test_a_word_where_a_number_belongs_is_refused_by_name(self):
        from hr_insight.core.errors import ConfigError
        from hr_insight.core.metrics import PrivacyRules

        config = self._config(**{
            "privacy_parameters.min_headcount_publish": "beaucoup"})
        with self.assertRaises(ConfigError) as leve:
            PrivacyRules.from_config(config)
        message = str(leve.exception)
        self.assertIn("min_headcount_publish", message)
        self.assertIn("beaucoup", message)
        self.assertIn("privacy_parameters.json", message)

    def test_a_publication_threshold_below_one_is_refused(self):
        """Le garde-fou ne doit pas pouvoir se desarmer par une faute de
        frappe."""
        from hr_insight.core.errors import ConfigError
        from hr_insight.core.metrics import PrivacyRules

        for valeur in (0, -3):
            with self.subTest(valeur=valeur):
                config = self._config(**{
                    "privacy_parameters.min_headcount_publish": valeur})
                with self.assertRaises(ConfigError):
                    PrivacyRules.from_config(config)

    def test_impossible_chart_settings_are_refused(self):
        from hr_insight.core import metrics
        from hr_insight.core.errors import ConfigError

        population = build_population([make_row(i) for i in range(30)])
        for chemin, valeur in (("chart_parameters.histogram_bins", 0),
                               ("chart_parameters.histogram_bins", -7),
                               ("salary_parameters.outlier_factor", 0),
                               ("salary_parameters.outlier_factor", -1.5)):
            with self.subTest(chemin=chemin, valeur=valeur):
                config = self._config(**{chemin: valeur})
                with self.assertRaises(ConfigError):
                    metrics.calculate_distribution_metrics(population, config)

    def test_a_missing_setting_still_falls_back_on_its_default(self):
        """Le controle ne doit pas transformer un fichier incomplet en
        refus : ce qui manque garde sa valeur d'origine."""
        from hr_insight.core.config import Configuration
        from hr_insight.core.metrics import PrivacyRules

        donnees = make_config().as_dict()
        donnees["privacy_parameters"].pop("min_headcount_publish", None)
        regles = PrivacyRules.from_config(Configuration(donnees))
        self.assertEqual(regles.min_publish, 5)

    def test_a_number_written_as_text_is_accepted(self):
        """« 5 » ecrit entre guillemets reste un cinq : refuser la forme
        quand le fond est juste ferait un outil tatillon."""
        from hr_insight.core.metrics import PrivacyRules

        regles = PrivacyRules.from_config(self._config(**{
            "privacy_parameters.min_headcount_publish": "7"}))
        self.assertEqual(regles.min_publish, 7)

    def test_a_gap_threshold_written_as_text_is_refused_by_name(self):
        """Le seuil d'alerte se lit a trois endroits — le tableau global, la
        table par axe, le profil d'un poste. Il doit y etre refuse de la
        meme facon, sans qu'un chemin encore lu « a la main » ne laisse
        passer une trace Python la ou les deux autres nomment le fichier."""
        from hr_insight.core import pay_equity

        population = build_population([make_row(i) for i in range(40)])
        config = self._config(**{
            "pay_equity_parameters.gap_alert_threshold": "cinq"})
        for appel in (lambda: pay_equity.calculate_pay_equity(population,
                                                              config),
                      lambda: pay_equity.calculate_category_gaps(
                          population, config, "grade")):
            with self.subTest(appel=appel):
                with self.assertRaises(ConfigError) as leve:
                    appel()
                self.assertIn("gap_alert_threshold", str(leve.exception))


class TestACosmeticSettingNeverBlocksTheWindow(unittest.TestCase):
    """Tout parametre illisible n'a pas le meme prix.

    Un seuil de publication faux fausse un resultat : il doit arreter
    l'analyse. Une duree d'ecran d'accueil fausse ne fausse rien — refuser
    d'ouvrir la fenetre pour elle couterait a l'utilisateur bien plus que
    le defaut ne lui coute.
    """

    def _duree(self, valeur):
        from hr_insight.ui.app import Application

        donnees = make_config().as_dict()
        donnees.setdefault("theme_parameters", {})["splash_seconds"] = valeur
        faux = type("Faux", (), {
            "configuration": Configuration(donnees),
            "SPLASH_SECONDS": Application.SPLASH_SECONDS,
            "_splash_seconds": Application._splash_seconds,
        })()
        return faux._splash_seconds()

    @unittest.skipUnless(HAS_TK, "tkinter absent")
    def test_an_unreadable_duration_falls_back_on_the_default(self):
        from hr_insight.ui.app import Application

        self.assertEqual(self._duree("longtemps"),
                         float(Application.SPLASH_SECONDS))

    @unittest.skipUnless(HAS_TK, "tkinter absent")
    def test_a_duration_of_zero_stays_zero(self):
        """Zero est un reglage, non une faute : il retire l'ecran
        d'accueil, et le defaut ne doit pas le reintroduire."""
        self.assertEqual(self._duree(0), 0.0)

    def test_the_publication_threshold_is_offered_in_the_settings(self):
        """« On ne met pas les calculs en dessous de cinq. »

        Le seuil vivait dans un fichier JSON, ou personne ne va le
        chercher, alors que c'est lui qui decide de ce que la page des
        ecarts affiche ou tait. Il se regle desormais dans la fenetre.
        """
        import json

        from hr_insight.core.config import load_configuration

        dossier = tempfile.mkdtemp()
        write_default_configuration(dossier)
        config = load_configuration(dossier)
        privacy = dict(config.section("privacy_parameters"))
        privacy["min_headcount_publish"] = 12
        write_configuration(dossier, "privacy_parameters", privacy)

        relu = load_configuration(dossier)
        self.assertEqual(
            relu.number("privacy_parameters.min_headcount_publish", 5,
                        minimum=1, integer=True), 12)
        # Et le reglage d'ecran, qui partage la section, survit.
        self.assertIn("show_identities_on_screen",
                      json.load(open(os.path.join(
                          dossier, "privacy_parameters.json"),
                          encoding="utf-8")))
