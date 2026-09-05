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

from compensation_analytics.core.config import (Configuration, DEFAULTS,
                                                load_configuration,
                                                write_configuration)
from compensation_analytics.core.errors import ConfigError
from compensation_analytics.core.segmentation import (dimensions, filter_fields,
                                                      max_filter_values,
                                                      segment_fields)

try:
    import tkinter  # noqa: F401
    HAS_TK = True
except ImportError:
    HAS_TK = False


def configuration(**overrides):
    data = json.loads(json.dumps(DEFAULTS))
    data["population_mapping"].update(overrides)
    return Configuration(data)


class TestDimensionFlags(unittest.TestCase):
    def test_a_dimension_without_flags_serves_both_uses(self):
        """La configuration ecrite avant l'existence des drapeaux doit
        continuer de se comporter exactement comme avant."""
        config = configuration(dimensions=[{"field": "grade", "label": "Grade"}])
        entry = dimensions(config)[0]
        self.assertTrue(entry["filter"])
        self.assertTrue(entry["segment"])
        self.assertEqual(filter_fields(config), ["grade"])
        self.assertEqual(segment_fields(config), ["grade"])

    def test_a_dimension_can_be_a_filter_only(self):
        config = configuration(dimensions=[
            {"field": "site", "label": "Établissement", "segment": False},
            {"field": "grade", "label": "Grade"},
        ])
        self.assertEqual(filter_fields(config), ["site", "grade"])
        self.assertEqual(segment_fields(config), ["grade"])

    def test_a_dimension_can_be_an_axis_only(self):
        config = configuration(dimensions=[
            {"field": "job", "label": "Métier", "filter": False}])
        self.assertEqual(filter_fields(config), [])
        self.assertEqual(segment_fields(config), ["job"])

    def test_a_bare_string_still_declares_a_dimension(self):
        config = configuration(dimensions=["grade"])
        self.assertEqual(filter_fields(config), ["grade"])
        self.assertEqual(segment_fields(config), ["grade"])


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
        from compensation_analytics.core.config import default_config_dir
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
        from compensation_analytics.ui.settings import build_mapping_section
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
        from compensation_analytics.ui.settings import IGNORED
        section = self._build(
            current={"fields": {}, "dimensions": []},
            assignments={"Commentaire libre": IGNORED},
            dimension_flags={}, limit=60)
        self.assertEqual(section["fields"], {})

    def test_a_new_column_creates_its_field(self):
        section = self._build(
            current={"fields": {}, "dimensions": []},
            assignments={"Direction": "direction"},
            dimension_flags={"direction": {"label": "Direction", "filter": True,
                                           "segment": True}},
            limit=60)
        self.assertEqual(section["fields"]["direction"], ["Direction"])
        self.assertEqual(section["dimensions"],
                         [{"field": "direction", "label": "Direction"}])

    def test_only_restrictive_flags_are_written(self):
        """Une entree sans drapeau se lit comme "les deux usages" : les
        ecrire tous rendrait le fichier illisible a la main."""
        section = self._build(
            current={"fields": {}, "dimensions": []}, assignments={},
            dimension_flags={
                "grade": {"label": "Grade", "filter": True, "segment": True},
                "site": {"label": "Site", "filter": True, "segment": False},
            }, limit=60)
        self.assertEqual(section["dimensions"], [
            {"field": "grade", "label": "Grade"},
            {"field": "site", "label": "Site", "segment": False},
        ])

    def test_a_field_used_for_neither_is_not_a_dimension(self):
        section = self._build(
            current={"fields": {}, "dimensions": []}, assignments={},
            dimension_flags={"fte": {"label": "ETP", "filter": False,
                                     "segment": False}}, limit=60)
        self.assertEqual(section["dimensions"], [])

    def test_a_dimension_the_window_never_shows_is_preserved(self):
        """Un champ nominatif declare a la main n'apparait pas dans la
        fenetre. Le supprimer parce qu'elle ne l'affiche pas ferait perdre
        un parametrage sans le dire."""
        section = self._build(
            current={"fields": {},
                     "dimensions": [{"field": "last_name", "label": "Nom"}]},
            assignments={},
            dimension_flags={"grade": {"label": "Grade", "filter": True,
                                       "segment": True}}, limit=60)
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
        from compensation_analytics.ui.settings import suggest_field_name
        self.assertEqual(suggest_field_name("Direction régionale", []),
                         "direction_regionale")
        self.assertEqual(suggest_field_name("N° de poste", []), "n_de_poste")

    def test_a_collision_is_suffixed(self):
        from compensation_analytics.ui.settings import suggest_field_name
        self.assertEqual(suggest_field_name("Grade", ["grade"]), "grade_2")

    def test_a_name_never_starts_with_a_digit(self):
        from compensation_analytics.ui.settings import suggest_field_name
        self.assertFalse(suggest_field_name("2024", [])[0].isdigit())


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestPrivacyOfTheDimensionList(unittest.TestCase):
    def test_nominative_fields_are_never_offered_as_an_axis(self):
        """Segmenter par nom produirait des groupes d'une personne et
        ferait entrer une identite dans une restitution."""
        from compensation_analytics.ui.settings import candidate_dimensions
        offered = candidate_dimensions(load_configuration())
        for field_name in ("last_name", "first_name", "employee_id",
                           "birth_date"):
            self.assertNotIn(field_name, offered)

    def test_computed_fields_are_never_offered_as_a_column(self):
        """Aucune colonne du fichier ne porte l'age : il est calcule."""
        from compensation_analytics.ui.settings import candidate_fields
        offered = candidate_fields(load_configuration())
        for field_name in ("age_years", "age_band", "tenure_band"):
            self.assertNotIn(field_name, offered)

    def test_computed_fields_remain_available_as_an_axis(self):
        from compensation_analytics.ui.settings import candidate_dimensions
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
        from compensation_analytics.io.xlsx_writer import write_workbook
        self.directory = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.directory, "config")
        self.source = os.path.join(self.directory, "population.xlsx")
        write_workbook(self.source, [("Population",
            [HEADERS + ["Direction"]] +
            [make_row(index) + [["Nord", "Sud", "Export"][index % 3]]
             for index in range(30)])])

    def test_a_column_the_tool_never_saw_becomes_a_filter(self):
        from compensation_analytics.core.pipeline import load_population
        from compensation_analytics.core.segmentation import (apply_filters,
                                                              build_filters)
        from compensation_analytics.ui.settings import build_mapping_section

        base = load_configuration()
        self.assertNotIn("direction", filter_fields(base))

        section = build_mapping_section(
            base.section("population_mapping"),
            assignments={"Direction": "direction"},
            dimension_flags={"direction": {"label": "Direction",
                                           "filter": True, "segment": False}},
            limit=60)
        write_configuration(self.config_dir, "population_mapping", section)

        config = load_configuration(self.config_dir)
        self.assertIn("direction", filter_fields(config))
        self.assertNotIn("direction", segment_fields(config))

        population, mapping, _ = load_population(self.source, config)
        self.assertEqual(mapping.unknown_columns, [])
        selected = apply_filters(population, build_filters(
            [{"field": "direction", "operator": "eq", "value": "Sud"}], config))
        self.assertEqual(len(selected), 10)

    def test_the_columns_already_recognised_keep_working(self):
        """Declarer une colonne ne doit pas defaire le mapping existant."""
        from compensation_analytics.core.pipeline import load_population
        from compensation_analytics.ui.settings import build_mapping_section

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


if __name__ == "__main__":
    unittest.main()


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
        from compensation_analytics.core.config import CONFIG_FILES

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
        from compensation_analytics.core.config import CONFIG_FILES

        for name in CONFIG_FILES:
            self.assertIsNotNone(self._shipped(name), f"{name}.json absent")
