"""Les cinq commandes en ligne, et toutes leurs options.

Un outil qui doit tourner sur un poste verrouille sera souvent pilote par la
ligne de commande — c'est la voie qui ne demande ni tkinter ni droits
particuliers. Deux commandes sur cinq (« mapping », « config ») n'avaient
aucun test, ni le choix des sorties, ni le code de retour.

Aucune donnee RH reelle.
"""

import contextlib
import glob
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, make_row
from compensation_analytics.cli import main as cli_main


def run(argv):
    """Execute la commande et rend (code, sortie standard, sortie erreur)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli_main(argv)
    return code, out.getvalue(), err.getvalue()


class CommandCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.logs = os.path.join(self.directory, "logs")

    def source(self, name="p.csv", headers=None, rows=None, extra=()):
        import csv

        path = os.path.join(self.directory, name)
        headers = list(headers if headers is not None else HEADERS) + list(extra)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(headers)
            for index in range(rows if rows is not None else 40):
                writer.writerow(list(make_row(
                    index, salary=40000 + index * 250,
                    business_unit=["France", "Iberia"][index % 2],
                    grade=f"G{3 + index % 4}",
                    gender="F" if index % 2 else "H")))
        return path

    def produced(self, folder):
        return sorted(os.path.basename(path)
                      for path in glob.glob(os.path.join(folder, "*")))


class TestAnalyse(CommandCase):
    def test_the_default_run_produces_every_document(self):
        out = os.path.join(self.directory, "sortie")
        code, text, _ = run(["--logs", self.logs, "analyse", self.source(),
                             "--sortie", out])
        self.assertEqual(code, 0)
        names = self.produced(out)
        for expected in ("restitution", "synthese", "slides", "analyse",
                         "manifeste"):
            self.assertTrue(any(name.startswith(expected) for name in names),
                            f"{expected} absent de {names}")
        self.assertIn("Effectif analysé", text)

    def test_one_output_can_be_asked_for_alone(self):
        out = os.path.join(self.directory, "un")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "excel"])
        names = self.produced(out)
        self.assertTrue(any(name.endswith(".xlsx") for name in names))
        self.assertFalse(any(name.endswith(".pdf") for name in names))

    def test_several_outputs_can_be_combined(self):
        out = os.path.join(self.directory, "deux")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "excel", "--restitution", "synthese"])
        names = self.produced(out)
        self.assertTrue(any(name.endswith(".xlsx") for name in names))
        self.assertTrue(any(name.startswith("synthese") for name in names))
        self.assertFalse(any(name.startswith("slides") for name in names))

    def test_the_manifest_is_always_written(self):
        """Sans lui, aucune analyse n'est refaisable a l'identique."""
        out = os.path.join(self.directory, "trois")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "excel"])
        manifests = glob.glob(os.path.join(out, "manifeste-*.json"))
        self.assertEqual(len(manifests), 1)
        with open(manifests[0], encoding="utf-8") as handle:
            manifest = json.load(handle)
        self.assertIn("effectif_analyse", manifest)
        self.assertIn("empreinte_source", manifest)

    def test_a_filter_narrows_the_population(self):
        out = os.path.join(self.directory, "filtre")
        _code, text, _ = run(["--logs", self.logs, "analyse", self.source(),
                              "--sortie", out, "--restitution", "excel",
                              "--filtre", "business_unit=France"])
        self.assertIn("20 salariés", text)

    def test_a_comparison_is_carried_to_the_workbook(self):
        out = os.path.join(self.directory, "comparaison")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "excel", "--filtre", "business_unit=France",
             "--comparer", "business_unit=Iberia",
             "--libelle-comparaison", "Espagne"])
        import zipfile

        workbook = glob.glob(os.path.join(out, "*.xlsx"))[0]
        with zipfile.ZipFile(workbook) as archive:
            content = archive.read("xl/workbook.xml").decode("utf-8")
        self.assertIn("Comparaison", content)

    def test_a_chosen_segment_is_recorded(self):
        out = os.path.join(self.directory, "segment")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "excel", "--segment", "grade"])
        manifest = glob.glob(os.path.join(out, "manifeste-*.json"))[0]
        with open(manifest, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["segments_analyses"], ["grade"])

    def test_a_title_reaches_the_report(self):
        out = os.path.join(self.directory, "titre")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "rapport", "--titre", "Revue annuelle"])
        report = glob.glob(os.path.join(out, "restitution-*.html"))[0]
        with open(report, encoding="utf-8") as handle:
            self.assertIn("Revue annuelle", handle.read())

    def test_an_unknown_field_stops_the_run_with_a_readable_message(self):
        code, _text, err = run(["--logs", self.logs, "analyse", self.source(),
                                "--filtre", "salaire=1"])
        self.assertEqual(code, 2)
        self.assertIn("salaire", err)

    def test_an_unknown_segment_stops_the_run(self):
        code, _text, err = run(["--logs", self.logs, "analyse", self.source(),
                                "--segment", "inexistant"])
        self.assertEqual(code, 2)
        self.assertIn("inexistant", err)

    def test_the_manifest_records_the_reference_date(self):
        """Elle decide de tous les ages et de toutes les anciennetes :
        sans elle, une analyse rejouee un an plus tard donne d'autres
        tranches et personne ne sait pourquoi."""
        out = os.path.join(self.directory, "date")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "excel", "--date-reference", "2030-01-01"])
        manifest = glob.glob(os.path.join(out, "manifeste-*.json"))[0]
        with open(manifest, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["date_reference"], "2030-01-01")

    def test_without_a_reference_date_the_day_used_is_recorded(self):
        """Le manifeste porte la date effectivement employee, jamais un
        libelle vague : c'est elle qu'il faudra redonner pour rejouer."""
        import datetime as _dt

        out = os.path.join(self.directory, "sansdate")
        run(["--logs", self.logs, "analyse", self.source(), "--sortie", out,
             "--restitution", "excel"])
        manifest = glob.glob(os.path.join(out, "manifeste-*.json"))[0]
        with open(manifest, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["date_reference"],
                             _dt.date.today().isoformat())

    def test_a_malformed_reference_date_is_refused(self):
        code, _text, err = run(["--logs", self.logs, "analyse", self.source(),
                                "--date-reference", "01/01/2030"])
        self.assertEqual(code, 2)
        self.assertIn("AAAA-MM-JJ", err)


class TestControle(CommandCase):
    def test_a_sound_file_returns_zero(self):
        code, text, _ = run(["--logs", self.logs, "controle", self.source()])
        self.assertEqual(code, 0)
        self.assertIn("CONFORME", text)

    def test_the_json_form_is_machine_readable(self):
        _code, text, _ = run(["--logs", self.logs, "controle", self.source(),
                              "--json"])
        report = json.loads(text)
        self.assertIn("statut", report)
        self.assertIn("constats", report)

    def test_a_blocking_file_returns_one(self):
        """Le code de retour est ce qu'un ordonnanceur lit : 1 pour des
        anomalies bloquantes, 2 pour une erreur d'execution."""
        path = os.path.join(self.directory, "salaire-vide.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            import csv as _csv

            writer = _csv.writer(handle, delimiter=";")
            writer.writerow(HEADERS)
            for index in range(10):
                writer.writerow(list(make_row(index, salary=None)))
        code, text, _ = run(["--logs", self.logs, "controle", path])
        self.assertEqual(code, 1)
        self.assertIn("CORRECTIONS REQUISES", text)

    def test_a_missing_required_column_returns_two(self):
        """Ce n'est pas une anomalie de donnees : le fichier ne peut pas
        etre lu du tout."""
        path = os.path.join(self.directory, "sans-salaire.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Matricule;BU\nE1;France\n")
        code, _text, err = run(["--logs", self.logs, "controle", path])
        self.assertEqual(code, 2)
        self.assertIn("Salaire", err)


class TestMapping(CommandCase):
    def test_recognised_columns_are_listed(self):
        _code, text, _ = run(["--logs", self.logs, "mapping", self.source()])
        self.assertIn("base_salary", text)
        self.assertIn("Salaire de base", text)

    def test_declared_dimensions_are_shown_present_or_absent(self):
        _code, text, _ = run(["--logs", self.logs, "mapping", self.source()])
        self.assertIn("Dimensions d'analyse", text)
        self.assertIn("grade", text)

    def test_unrecognised_columns_are_named(self):
        """C'est la reponse a « pourquoi ma colonne n'apparait pas ? »."""
        path = self.source("avec-extra.csv", extra=["Prime de panier"])
        _code, text, _ = run(["--logs", self.logs, "mapping", path])
        self.assertIn("Prime de panier", text)
        self.assertIn("non reconnues", text)

    def test_a_missing_required_column_returns_one(self):
        path = os.path.join(self.directory, "sans-matricule.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Nom;Salaire de base\nX;40000\n")
        code, text, _ = run(["--logs", self.logs, "mapping", path])
        self.assertEqual(code, 1)
        self.assertIn("obligatoires manquantes", text)
        self.assertIn("employee_id", text)


class TestConfig(CommandCase):
    def test_every_settings_file_is_written(self):
        folder = os.path.join(self.directory, "parametres")
        code, text, _ = run(["--logs", self.logs, "config", "--dossier", folder])
        self.assertEqual(code, 0)
        self.assertIn(folder, text)
        written = self.produced(folder)
        self.assertIn("population_mapping.json", written)
        self.assertIn("privacy_parameters.json", written)

    def test_what_is_written_can_be_read_back(self):
        """Une configuration ecrite puis relue doit donner exactement les
        memes reglages : sinon l'utilisateur qui l'edite part d'un faux."""
        from compensation_analytics.core.config import load_configuration

        folder = os.path.join(self.directory, "aller-retour")
        run(["--logs", self.logs, "config", "--dossier", folder])
        self.assertEqual(load_configuration(folder).as_dict(),
                         load_configuration().as_dict())

    def test_the_written_files_are_valid_json(self):
        folder = os.path.join(self.directory, "json")
        run(["--logs", self.logs, "config", "--dossier", folder])
        for name in self.produced(folder):
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                self.assertIsInstance(json.load(handle), dict, name)

    def test_an_analysis_can_use_the_written_configuration(self):
        folder = os.path.join(self.directory, "utilisee")
        run(["--logs", self.logs, "config", "--dossier", folder])
        out = os.path.join(self.directory, "avec-config")
        code, _text, _ = run(["--logs", self.logs, "analyse", self.source(),
                              "--config", folder, "--sortie", out,
                              "--restitution", "excel"])
        self.assertEqual(code, 0)


class TestParserItself(CommandCase):
    def test_the_version_is_offered(self):
        with self.assertRaises(SystemExit) as caught:
            run(["--version"])
        self.assertEqual(caught.exception.code, 0)

    def test_an_unknown_command_is_refused(self):
        with self.assertRaises(SystemExit) as caught:
            run(["inexistant", "fichier.csv"])
        self.assertEqual(caught.exception.code, 2)

    def test_a_missing_file_is_refused_with_a_readable_message(self):
        code, _text, err = run(["--logs", self.logs, "controle",
                                os.path.join(self.directory, "absent.csv")])
        self.assertEqual(code, 2)
        self.assertIn("introuvable", err)

    def test_the_technical_log_is_written_where_asked(self):
        run(["--logs", self.logs, "controle", self.source()])
        self.assertTrue(glob.glob(os.path.join(self.logs, "*.log")))

    def test_the_technical_log_carries_no_personal_data(self):
        """Ni nom, ni matricule, ni salaire individuel — jamais."""
        run(["--logs", self.logs, "analyse", self.source(),
             "--sortie", os.path.join(self.directory, "j"),
             "--restitution", "excel", "--filtre", "business_unit=France"])
        content = ""
        for path in glob.glob(os.path.join(self.logs, "*.log")):
            with open(path, encoding="utf-8") as handle:
                content += handle.read()
        self.assertTrue(content)
        for forbidden in ("NOM", "PRENOM", "E00001", "France", "40000"):
            self.assertNotIn(forbidden, content, forbidden)


if __name__ == "__main__":
    unittest.main()
