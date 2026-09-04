"""Tests de bout en bout : confidentialite, tracabilite, restitution, export.

Ces tests verifient les contraintes non negociables du produit : traitement
local, absence de donnee personnelle dans les logs et la restitution, absence
de reference reseau dans les fichiers produits.
"""

import glob
import logging
import os
import re
import tempfile
import unittest

from tests.support import HEADERS, REFERENCE_DATE, make_row
from compensation_analytics.cli import main as cli_main, parse_filter
from compensation_analytics.core.errors import DataQualityError
from compensation_analytics.core.export import export_excel
from compensation_analytics.core.logging_setup import configure_logging
from compensation_analytics.core.normalize import anonymise
from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.core.reporting import render_report
from compensation_analytics.io.tabular import read_table
from compensation_analytics.io.xlsx_writer import write_workbook
from compensation_analytics.version import __version__


def build_source(directory, rows=None):
    rows = rows or [make_row(i, salary=35000 + (i % 40) * 900,
                             business_unit=["France", "DACH", "Iberia"][i % 3],
                             grade=["G3", "G5", "G7"][i % 3],
                             gender=["F", "H"][i % 2],
                             age=28 + i % 30, tenure=i % 18)
                    for i in range(120)]
    path = os.path.join(directory, "population.xlsx")
    write_workbook(path, [("Population", [HEADERS] + rows)])
    return path


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source = build_source(self.directory)

    def _run(self, **kwargs):
        request = AnalysisRequest(source_path=self.source,
                                  reference_date=REFERENCE_DATE, **kwargs)
        return run_analysis(request)

    def test_end_to_end_produces_all_sections(self):
        result = self._run(segments=["business_unit", "grade"])
        payload = result.payload
        for key in ("quality", "population", "salary", "distribution",
                    "scatter", "segments", "manifest"):
            self.assertIn(key, payload)
        self.assertEqual(payload["population"]["headcount"], 120)
        self.assertEqual(len(payload["segments"]), 2)

    def test_filters_reduce_the_analysed_population(self):
        from compensation_analytics.core.segmentation import build_filters
        result = self._run(filters=build_filters([
            {"field": "business_unit", "operator": "eq", "value": "France"}
        ]))
        self.assertLess(len(result.filtered), len(result.population))
        self.assertGreater(len(result.filtered), 0)

    def test_critical_findings_block_unless_accepted(self):
        rows = [make_row(i, salary=40000) for i in range(20)]
        rows.append(make_row(0, salary=40000))  # doublon de matricule
        source = os.path.join(self.directory, "defect.xlsx")
        write_workbook(source, [("Population", [HEADERS] + rows)])
        request = AnalysisRequest(source_path=source, reference_date=REFERENCE_DATE)
        with self.assertRaises(DataQualityError):
            run_analysis(request)
        request.ignore_quality_errors = True
        self.assertEqual(len(run_analysis(request).population), 21)

    def test_manifest_supports_reproduction(self):
        manifest = self._run().payload["manifest"]
        self.assertEqual(manifest["version"], __version__)
        self.assertEqual(len(manifest["empreinte_source"]), 64)
        self.assertIn("parametres", manifest)
        self.assertIn("percentile_parameters", manifest["parametres"])
        self.assertNotIn("NOM0", str(manifest))


class TestPrivacy(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source = build_source(self.directory)
        self.result = run_analysis(AnalysisRequest(
            source_path=self.source, reference_date=REFERENCE_DATE,
            segments=["business_unit"],
        ))

    def test_anonymisation_is_stable_and_not_the_raw_identifier(self):
        first, second = anonymise("E00042"), anonymise("E00042")
        self.assertEqual(first, second)
        self.assertNotIn("E00042", first)
        self.assertNotEqual(anonymise("E00042"), anonymise("E00043"))

    def test_report_contains_no_names(self):
        html = render_report(self.result.payload)
        self.assertNotIn("NOM0", html)
        self.assertNotIn("PRENOM0", html)

    def test_report_has_no_network_reference(self):
        html = render_report(self.result.payload)
        for pattern in ("http://", "https://", "<script src", "<link ", "@import"):
            self.assertNotIn(pattern, html)

    def test_report_uses_neutral_wording_for_atypical_cases(self):
        html = render_report(self.result.payload)
        self.assertNotIn("anomalie RH", html)
        if self.result.payload["distribution"]["outliers"]:
            self.assertIn("Situation atypique a analyser", html)

    def test_technical_log_excludes_personal_data(self):
        log_dir = tempfile.mkdtemp()
        configure_logging(log_dir)
        run_analysis(AnalysisRequest(source_path=self.source,
                                     reference_date=REFERENCE_DATE))
        for handler in logging.getLogger("compensation_analytics").handlers:
            handler.flush()
        with open(os.path.join(log_dir, "technical.log"), encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("read_table", content)
        self.assertNotIn("NOM0", content)
        self.assertNotIn("PRENOM0", content)
        self.assertFalse(re.search(r"\bE000\d\d\b", content))

    def test_individual_data_is_not_exported_by_default(self):
        path = os.path.join(self.directory, "export.xlsx")
        export_excel(self.result.payload, self.result.filtered,
                     self.result.config, path)
        import zipfile
        with zipfile.ZipFile(path) as archive:
            content = b"".join(archive.read(name) for name in archive.namelist()
                               if name.startswith("xl/worksheets"))
        self.assertNotIn(b"NOM0", content)

    def test_individual_export_requires_explicit_configuration(self):
        from compensation_analytics.core.config import Configuration
        data = self.result.config.as_dict()
        data["export_parameters"]["include_individual_data"] = True
        path = os.path.join(self.directory, "export_full.xlsx")
        export_excel(self.result.payload, self.result.filtered,
                     Configuration(data), path)
        names = [name for name, _ in _sheet_names(path)]
        self.assertIn("Donnees individuelles", names)


def _sheet_names(path):
    import zipfile
    from xml.etree import ElementTree
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    return [(node.get("name"), node.get("sheetId"))
            for node in root.iter(f"{namespace}sheet")]


class TestExportArtifacts(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source = build_source(self.directory)

    def test_excel_export_is_readable_by_the_importer(self):
        result = run_analysis(AnalysisRequest(
            source_path=self.source, reference_date=REFERENCE_DATE,
            segments=["business_unit"],
        ))
        path = os.path.join(self.directory, "analyse.xlsx")
        export_excel(result.payload, result.filtered, result.config, path)
        table = read_table(path)
        self.assertEqual(table.headers, ["Element", "Valeur"])
        self.assertIn("Version", [row[0] for row in table.rows])


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source = build_source(self.directory)

    def test_filter_expressions(self):
        self.assertEqual(parse_filter("business_unit=France"),
                         {"field": "business_unit", "operator": "eq", "value": "France"})
        self.assertEqual(parse_filter("grade=G5|G6")["operator"], "in")
        self.assertEqual(parse_filter("base_salary>=50000")["operator"], "gte")

    def test_analyse_command_writes_expected_files(self):
        output = os.path.join(self.directory, "sortie")
        code = cli_main([
            "analyse", self.source, "--sortie", output,
            "--date-reference", REFERENCE_DATE.isoformat(),
            "--segment", "grade",
        ])
        self.assertEqual(code, 0)
        self.assertTrue(glob.glob(os.path.join(output, "restitution-*.html")))
        self.assertTrue(glob.glob(os.path.join(output, "analyse-*.xlsx")))
        self.assertTrue(glob.glob(os.path.join(output, "manifeste-*.json")))

    def test_readable_error_when_column_is_missing(self):
        path = os.path.join(self.directory, "sans_salaire.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Matricule;BU\nE1;France\n")
        self.assertEqual(cli_main(["controle", path]), 2)


if __name__ == "__main__":
    unittest.main()
