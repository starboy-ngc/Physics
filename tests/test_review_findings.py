"""Les constats de la revue de code du 9 octobre, pinglés.

Chacun a ete corrige le jour meme ; ces essais empechent le retour de
ce que la revue a trouve : un modele qui gardait des notions qu'il ne
livre plus, un nom de champ qui atteignait sa mecanique interne, une
tranche du bas doublee, et les menues choses listees ci-dessous.
"""
import unittest

from tests.support import build_population, make_config, make_row

from hr_analytics.core.errors import ConfigError
from hr_analytics.core.normalize import Employee, close_the_bottom


class TestTheModelKnowsOnlyWhatItComputesWith(unittest.TestCase):
    def test_no_organisation_attribute_survives_on_the_model(self):
        salarie = Employee(row_number=2)
        for nom in ("business_unit", "country", "site", "job", "job_title",
                    "job_family", "annexe", "groupe", "coefficient", "status"):
            self.assertFalse(hasattr(salarie, nom), nom)

    def test_a_declared_notion_lives_in_extra_and_reads_back(self):
        salarie = Employee(row_number=2)
        salarie.assign("site", "Nantes")
        self.assertEqual(salarie.extra["site"], "Nantes")
        self.assertEqual(salarie.value("site"), "Nantes")

    def test_an_internal_name_never_reaches_the_mechanics(self):
        """« extra » ecrit a la main dans le fichier de parametres : la
        valeur se range dans extra, elle ne remplace pas extra."""
        salarie = Employee(row_number=2)
        for nom in ("extra", "issues", "anonymous_id", "row_number"):
            salarie.assign(nom, "x")
        self.assertIsInstance(salarie.extra, dict)
        self.assertIsInstance(salarie.issues, list)
        self.assertEqual(salarie.row_number, 2)
        self.assertEqual(salarie.extra["issues"], "x")

    def test_a_declared_numeric_notion_is_typed_like_before(self):
        """Le coefficient n'est plus un champ du modele : declare
        numerique, il reste un nombre, et un filtre « 230 » le trouve."""
        from hr_analytics.core.segmentation import Filter, apply_filters

        config = make_config()
        self.assertIn("coefficient", config.get("population_mapping.numeric"))
        rows = [make_row(i) + [] for i in range(4)]
        population = build_population(rows, config)
        for index, salarie in enumerate(population.employees):
            salarie.assign("coefficient", 230.0 if index % 2 else 250.0)
        retenus = apply_filters(population, [Filter("coefficient", "eq", "230")])
        self.assertEqual(len(retenus), 2)


class TestTheBottomBandIsClosedOnce(unittest.TestCase):
    def test_a_band_already_open_at_the_bottom_is_left_alone(self):
        bandes = [{"label": "<20", "min": None, "max": 20},
                  {"label": "20-29", "min": 20, "max": 30}]
        self.assertEqual(close_the_bottom(bandes), bandes)

    def test_a_non_numeric_minimum_is_a_readable_error(self):
        with self.assertRaises(ConfigError) as caught:
            close_the_bottom([{"label": "20-29", "min": "20 ans", "max": 30}])
        self.assertIn("20-29", str(caught.exception))
        self.assertIn("20 ans", str(caught.exception))

    def test_a_split_starting_above_zero_still_gets_its_floor(self):
        bandes = close_the_bottom([{"label": "20-29", "min": 20, "max": 30}])
        self.assertEqual(bandes[0]["label"], "<20")
        self.assertEqual(len(bandes), 2)


class TestTheTeamTableNamesTheDeclaredJob(unittest.TestCase):
    def test_the_job_column_follows_the_field_it_is_given(self):
        from hr_analytics.core.hierarchy import Tree, team_rows

        config = make_config()
        rows = [make_row(0, employee_id="M1")] + [
            make_row(i, employee_id=f"E{i}") for i in range(1, 4)]
        population = build_population(rows, config)
        for salarie in population.employees:
            salarie.assign("manager", "" if salarie.employee_id == "M1" else "M1")
            salarie.assign("metier", "Direction" if salarie.employee_id == "M1"
                           else "Atelier")
        arbre = Tree(population)
        avec = {row["manager"]: row for row in
                team_rows(population, arbre, job_field="metier")}
        self.assertEqual(avec["M1"]["job"], "Direction")
        sans = {row["manager"]: row for row in team_rows(population, arbre)}
        self.assertEqual(sans["M1"]["job"], "")


class TestTheOrganigramUsesTheDeclaredJob(unittest.TestCase):
    def test_the_first_filled_declared_notion_names_the_boxes(self):
        """Le repli de l'organigramme etait une copie affaiblie de celui de
        la page des ecarts, et finissait sur « job », un champ que l'outil
        ne livre plus : les cases lisaient « - »."""
        from hr_analytics.core import org
        from hr_analytics.core.hierarchy import Tree

        config = make_config({
            "pay_equity_parameters.category_field": "",
            "population_mapping.dimensions": [
                {"field": "site", "label": "Site"},
                {"field": "metier", "label": "Métier"}],
        })
        rows = [make_row(0, employee_id="M1")] + [
            make_row(i, employee_id=f"E{i}") for i in range(1, 4)]
        population = build_population(rows, config)
        for salarie in population.employees:
            salarie.assign("manager", "" if salarie.employee_id == "M1" else "M1")
            salarie.assign("metier", "Direction" if salarie.employee_id == "M1"
                           else "Atelier")
        arbre = Tree(population)
        racine = org.chart_nodes(arbre, "M1", config)
        self.assertEqual(racine["job"], "Direction")
        lignes = org.member_rows(arbre, "M1", config)
        self.assertTrue(any("Atelier" in str(valeur)
                            for ligne in lignes for valeur in ligne.values()))


if __name__ == "__main__":
    unittest.main()
