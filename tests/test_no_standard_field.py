"""Aucun champ d'organisation n'est livre d'office.

Ni BU, ni etablissement, ni metier, ni poste, ni statut : ce qu'un fichier
porte en propre se declare depuis l'ecran « Associer les colonnes », et
c'est l'utilisateur qui dit ensuite laquelle de ses notions sert de poste
pour les ecarts, laquelle fait le camembert, laquelle colore le nuage. Ne
restent dans la configuration livree que les champs avec lesquels le
moteur calcule.

Les essais, eux, declarent les notions dont ils ont besoin dans
`tests/config_essai`, comme un utilisateur l'aurait fait.
"""
import json
import os
import unittest

from tests.support import (CONFIG_DIR, HEADERS, build_population,
                           make_config, make_row)

from hr_analytics.core.config import (CONFIG_FILES, DEFAULTS, Configuration,
                                      load_configuration)

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Les champs avec lesquels le moteur calcule. Tout autre champ est une
#: notion d'organisation, et n'a rien a faire dans la configuration livree.
MODELE = {"employee_id", "last_name", "first_name", "gender", "birth_date",
          "hire_date", "leave_date", "period", "manager", "fte",
          "base_salary", "variable_pay", "total_compensation"}


def _usine() -> Configuration:
    return load_configuration(None)


class TestTheDeliveredConfigurationCarriesNoOrganisation(unittest.TestCase):
    def test_only_the_model_fields_are_delivered(self):
        champs = set(DEFAULTS["population_mapping"]["fields"])
        self.assertEqual(champs - MODELE, set())
        self.assertIn("base_salary", champs)
        self.assertIn("gender", champs)

    def test_the_only_delivered_dimensions_are_computed(self):
        dims = [d["field"] for d in DEFAULTS["population_mapping"]["dimensions"]]
        self.assertEqual(dims, ["gender", "age_band", "tenure_band"])

    def test_no_setting_names_an_organisation_field(self):
        self.assertEqual(DEFAULTS["pay_equity_parameters"]["category_field"], "")
        self.assertEqual(DEFAULTS["chart_parameters"]["csp_field"], "")
        self.assertEqual(DEFAULTS["chart_parameters"]["scatter_color_by"], "")
        colonnes = [c["field"] for c in
                    DEFAULTS["pay_equity_parameters"]["people_columns"]]
        self.assertEqual(set(colonnes) - MODELE, set())
        self.assertEqual(set(DEFAULTS["population_mapping"]["numeric"]) - MODELE,
                         set())

    def test_the_delivered_files_say_the_same(self):
        for name in CONFIG_FILES:
            with open(os.path.join(RACINE, "config", f"{name}.json"),
                      encoding="utf-8") as handle:
                self.assertEqual(json.load(handle), DEFAULTS[name], name)

    def test_the_test_fixture_declares_organisation_fields(self):
        """Sans quoi les essais de filtres et de segments ne testeraient
        rien : c'est elle qui joue l'utilisateur qui a declare ses champs."""
        essai = load_configuration(CONFIG_DIR)
        champs = set(essai.get("population_mapping.fields"))
        self.assertTrue({"business_unit", "groupe", "status"} <= champs)


class TestTheEngineFallsBackOnWhatIsDeclared(unittest.TestCase):
    def rows(self):
        return [make_row(i, gender="F" if i % 2 else "H",
                         business_unit=["Nord", "Sud"][i % 2],
                         groupe=f"G{i % 3}") for i in range(40)]

    def test_an_empty_category_takes_the_first_declared_organisation(self):
        from hr_analytics.core.pay_equity import category_field

        config = make_config({"pay_equity_parameters.category_field": ""})
        population = build_population(self.rows(), config)
        self.assertEqual(category_field(population, config), "business_unit")

    def test_a_category_the_file_does_not_carry_falls_back_too(self):
        from hr_analytics.core.pay_equity import category_field

        config = make_config({"pay_equity_parameters.category_field":
                              "job_title"})
        population = build_population(self.rows(), config)
        self.assertEqual(category_field(population, config), "business_unit")

    def test_without_any_organisation_the_category_is_empty_and_said(self):
        from hr_analytics.core.pay_equity import (NO_CATEGORY_WARNING,
                                                  calculate_pay_equity,
                                                  category_field)

        config = _usine()
        population = build_population(self.rows(), config)
        self.assertEqual(category_field(population, config), "")
        bloc = calculate_pay_equity(population, config)
        self.assertEqual(bloc["category_field"], "")
        self.assertEqual(bloc["categories"], [])
        self.assertEqual(bloc["category_warning"], NO_CATEGORY_WARNING)
        self.assertIn("Associer les colonnes", NO_CATEGORY_WARNING)

    def test_declared_organisation_fields_join_the_people_list(self):
        from hr_analytics.core.pay_equity import people_columns

        champs = [c["field"] for c in people_columns(make_config())]
        self.assertIn("business_unit", champs)
        self.assertIn("status", champs)
        # Avant les montants, apres l'identite.
        self.assertLess(champs.index("business_unit"),
                        champs.index("base_salary"))
        self.assertLess(champs.index("gender"), champs.index("business_unit"))
        usine = [c["field"] for c in people_columns(_usine())]
        self.assertEqual(usine, ["last_name", "first_name", "gender",
                                 "base_salary"])

    def test_a_declared_notion_the_file_does_not_carry_has_no_column(self):
        """Une colonne vide sur toute la hauteur n'apprend rien."""
        from hr_analytics.core.pay_equity import people_rows

        config = make_config()
        rows = [make_row(i, groupe="", business_unit=["Nord", "Sud"][i % 2])
                for i in range(20)]
        colonnes = [c["field"] for c in
                    people_rows(build_population(rows, config), config)["columns"]]
        self.assertIn("business_unit", colonnes)
        self.assertNotIn("groupe", colonnes)
        self.assertIn("last_name", colonnes)

    def test_no_pie_without_a_declared_field(self):
        from hr_analytics.core.metrics import calculate_population_metrics

        population = build_population(self.rows(), _usine())
        bloc = calculate_population_metrics(population, _usine())
        self.assertEqual(bloc["csp_split"], [])
        self.assertEqual(bloc["csp_label"], "")
        config = make_config({"chart_parameters.csp_field": "groupe"})
        bloc = calculate_population_metrics(build_population(self.rows(), config),
                                            config)
        self.assertEqual({p["label"] for p in bloc["csp_split"]},
                         {"G0", "G1", "G2"})

    def test_the_scatter_colours_by_the_first_declared_organisation(self):
        from hr_analytics.core.metrics import (default_colour_field,
                                               scatter_dataset)

        config = make_config({"chart_parameters.scatter_color_by": ""})
        population = build_population(self.rows(), config)
        self.assertEqual(default_colour_field(config), "business_unit")
        self.assertEqual(scatter_dataset(population, config)["color_field"],
                         "business_unit")
        self.assertEqual(default_colour_field(_usine()), "gender")
        self.assertEqual(scatter_dataset(population, _usine())["color_field"],
                         "gender")

    def test_a_file_with_undeclared_columns_still_analyses(self):
        """Les colonnes BU, Groupe, Statut ne sont plus reconnues d'office :
        elles restent a associer, et l'analyse tourne sans elles."""
        from hr_analytics.core.mapping import resolve_mapping

        mapping = resolve_mapping(HEADERS, _usine())
        self.assertNotIn("business_unit", mapping.field_to_index)
        self.assertIn("base_salary", mapping.field_to_index)
        self.assertTrue({"BU", "Groupe", "Statut"} <= set(mapping.unknown_columns))


if __name__ == "__main__":
    unittest.main()
