"""Ce que l'outil exige d'un fichier, et ce qu'il laisse paramétrer.

C'est sur ce point que tout repose : un fichier RH n'a pas deux fois les
memes en-tetes, et l'outil ne peut pas imposer les siens. Ce module tient
la promesse en la verifiant plutot qu'en la declarant — une colonne
metier inconnue du modele, un fichier qui ne porte que la remuneration
totale, un CSV enregistre par Excel en France.

Aucune donnee RH reelle.
"""

import csv
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import make_config
from hr_insight.core.config import Configuration, write_default_configuration
from hr_insight.core.errors import MappingError
from hr_insight.core.export import build_sheets
from hr_insight.core.mapping import (ensure_required, required_fields,
                                     resolve_mapping)
from hr_insight.core.pipeline import AnalysisRequest, run_analysis
from hr_insight.core.segmentation import field_label, filterable_fields


class TestWhatIsTrulyRequired(unittest.TestCase):
    """Une seule colonne, et elle n'est pas nommee dans le code."""

    def test_the_analysed_pay_field_is_required(self):
        config = make_config()
        self.assertIn("base_salary", required_fields(config))

    def test_it_follows_the_setting_rather_than_a_name(self):
        """Analyser la remuneration totale ne doit pas exiger un salaire
        de base que le fichier ne porte pas."""
        config = make_config({
            "salary_parameters.analysis_field": "total_compensation"})
        exiges = required_fields(config)
        self.assertIn("total_compensation", exiges)
        self.assertNotIn("base_salary", exiges)

    def test_an_identifier_is_no_longer_demanded(self):
        """Sans matricule, le suivi des doublons n'est pas possible — le
        controle qualite le dit, et l'analyse se poursuit. Un fichier
        anonymise en amont reste analysable."""
        self.assertNotIn("employee_id", required_fields(make_config()))

    def test_an_organisation_can_add_its_own_discipline(self):
        config = make_config({
            "population_mapping.required": ["employee_id", "site"]})
        exiges = required_fields(config)
        for champ in ("employee_id", "site", "base_salary"):
            self.assertIn(champ, exiges)

    def test_the_message_names_the_column_not_the_field(self):
        """« base_salary » n'apprend rien a qui cherche sa colonne dans un
        fichier de paie."""
        config = make_config()
        mapping = resolve_mapping(["Matricule", "BU"], config)
        with self.assertRaises(MappingError) as caught:
            ensure_required(mapping, config)
        message = caught.exception.message
        self.assertIn("Salaire de base", message)
        self.assertNotIn("base_salary", message)

    def test_the_message_lists_every_accepted_spelling(self):
        config = make_config()
        mapping = resolve_mapping(["Matricule"], config)
        with self.assertRaises(MappingError) as caught:
            ensure_required(mapping, config)
        self.assertIn("Base salary", caught.exception.message)


class TestMoneyColumnsAreDeclared(unittest.TestCase):
    """Les colonnes de montant et leurs libelles viennent du mapping."""

    def test_a_label_is_the_spelling_the_user_declared(self):
        config = make_config({"population_mapping.fields": {
            "employee_id": ["Matricule"], "base_salary": ["Fixe annuel"]}})
        self.assertEqual(field_label(config, "base_salary"), "Fixe annuel")

    def test_a_dimension_keeps_the_label_it_gives_itself(self):
        """« BU » reste « BU » meme si la colonne s'appelle
        « Business Unit » : une dimension se nomme pour l'analyse."""
        self.assertEqual(field_label(make_config(), "business_unit"), "BU")

    def test_an_undeclared_field_falls_back_to_its_own_name(self):
        self.assertEqual(field_label(make_config(), "inconnu"), "inconnu")


class ConfiguredFileCase(unittest.TestCase):
    """Un fichier aux en-tetes maison, analyse par declaration seule."""

    HEADERS = ["Ident", "Civilite", "Naissance", "Entree", "Entite",
               "Emploi", "Convention collective", "Package",
               "Prime ancienneté"]

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "maison.csv")
        with open(cls.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(cls.HEADERS)
            for index in range(80):
                writer.writerow([
                    f"X{index:04d}", "F" if index % 2 else "H",
                    "1985-03-04", "2015-06-01",
                    ["Alpha", "Beta"][index % 2],
                    ["Comptable", "Technicien"][index % 2],
                    ["Syntec", "Métallurgie"][index % 2],
                    38000 + index * 300, 500 + index * 10])
        cls.config_dir = os.path.join(cls.directory, "config")
        write_default_configuration(cls.config_dir)
        chemin = os.path.join(cls.config_dir, "population_mapping.json")
        with open(chemin, encoding="utf-8") as handle:
            mapping = json.load(handle)
        # Rien que ce que le fichier porte, sous ses propres intitules.
        mapping["fields"] = {
            "employee_id": ["Ident"], "gender": ["Civilite"],
            "birth_date": ["Naissance"], "hire_date": ["Entree"],
            "business_unit": ["Entite"], "job_title": ["Emploi"],
            "convention": ["Convention collective"],
            "total_compensation": ["Package"],
            "seniority_bonus": ["Prime ancienneté"],
        }
        mapping["numeric"] = ["total_compensation", "seniority_bonus"]
        mapping["money"] = ["total_compensation", "seniority_bonus"]
        mapping["dimensions"] = [
            {"field": "business_unit", "label": "Entité"},
            {"field": "convention", "label": "Convention"},
            {"field": "gender", "label": "Sexe"},
        ]
        with open(chemin, "w", encoding="utf-8") as handle:
            json.dump(mapping, handle, ensure_ascii=False)
        chemin = os.path.join(cls.config_dir, "salary_parameters.json")
        with open(chemin, encoding="utf-8") as handle:
            salary = json.load(handle)
        salary["analysis_field"] = "total_compensation"
        with open(chemin, "w", encoding="utf-8") as handle:
            json.dump(salary, handle, ensure_ascii=False)
        cls.result = run_analysis(AnalysisRequest(source_path=cls.source,
                                                  config_dir=cls.config_dir))


class TestAForeignFileIsFullyAnalysed(ConfiguredFileCase):

    def test_every_column_is_recognised(self):
        self.assertEqual(self.result.mapping.unknown_columns, [])

    def test_the_analysis_runs_on_the_declared_field(self):
        salary = self.result.payload["salary"]
        self.assertEqual(salary["field"], "total_compensation")
        self.assertEqual(salary["field_label"], "Package")

    def test_a_column_unknown_to_the_model_becomes_a_segment(self):
        """« Convention collective » n'existe nulle part dans le code."""
        labels = [segment["label"]
                  for segment in self.result.payload["segments"]]
        self.assertIn("Convention", labels)

    def test_that_column_is_filterable_too(self):
        self.assertIn("convention", filterable_fields(self.result.config))

    def test_its_values_are_counted(self):
        segment = [item for item in self.result.payload["segments"]
                   if item["label"] == "Convention"][0]
        self.assertEqual(
            sorted((row["segment"], row["headcount"])
                   for row in segment["rows"]),
            [("Métallurgie", 40), ("Syntec", 40)])

    def test_the_workbook_names_the_columns_as_the_file_does(self):
        données = self.result.config.as_dict()
        données["export_parameters"]["include_individual_data"] = True
        feuilles = dict(build_sheets(
            self.result.payload, self.result.filtered,
            Configuration(données), table=self.result.table,
            mapping=self.result.mapping))
        entêtes = feuilles["Données individuelles"][0]
        self.assertIn("Package", entêtes)
        self.assertIn("Prime ancienneté", entêtes)
        # Aucun libelle francais ecrit dans le code ne doit survivre a un
        # fichier qui nomme ses colonnes autrement.
        self.assertNotIn("Salaire de base", entêtes)

    def test_a_sheet_is_written_for_the_new_dimension(self):
        feuilles = dict(build_sheets(self.result.payload,
                                     self.result.filtered,
                                     self.result.config))
        self.assertIn("Seg Convention", feuilles)


if __name__ == "__main__":
    unittest.main()
