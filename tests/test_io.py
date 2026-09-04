"""Tests d'import/export : CSV, XLSX, mapping, robustesse des formats."""

import datetime as _dt
import os
import tempfile
import unittest

from tests.support import make_config
from compensation_analytics.core.errors import ImportError_, MappingError
from compensation_analytics.core.mapping import ensure_required, resolve_mapping
from compensation_analytics.io.tabular import read_table
from compensation_analytics.io.xlsx_writer import write_workbook


class TestReaders(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def _path(self, name):
        return os.path.join(self.directory, name)

    def test_csv_semicolon(self):
        path = self._path("p.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Matricule;Salaire de base\nE1;40000\nE2;50000\n")
        table = read_table(path)
        self.assertEqual(table.headers, ["Matricule", "Salaire de base"])
        self.assertEqual(table.row_count, 2)

    def test_csv_comma(self):
        path = self._path("p2.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Matricule,Salaire de base\nE1,40000\nE2,50000\n")
        self.assertEqual(read_table(path).row_count, 2)

    def test_csv_with_bom(self):
        path = self._path("p3.csv")
        with open(path, "w", encoding="utf-8-sig") as handle:
            handle.write("Matricule;Salaire de base\nE1;40000\n")
        self.assertEqual(read_table(path).headers[0], "Matricule")

    def test_xlsx_round_trip_preserves_types(self):
        path = self._path("p.xlsx")
        write_workbook(path, [("Population", [
            ["Matricule", "Salaire de base", "Date d'entree"],
            ["E1", 40000.5, _dt.date(2019, 3, 15)],
            ["E2", 51000, _dt.date(2021, 11, 2)],
        ])])
        table = read_table(path)
        self.assertEqual(table.headers[0], "Matricule")
        self.assertAlmostEqual(table.rows[0][1], 40000.5)
        self.assertEqual(table.rows[0][2], _dt.date(2019, 3, 15))

    def test_xlsx_named_sheet(self):
        path = self._path("multi.xlsx")
        write_workbook(path, [
            ("Notice", [["Info"], ["ignorer"]]),
            ("Population", [["Matricule"], ["E1"]]),
        ])
        self.assertEqual(read_table(path, sheet="Population").headers, ["Matricule"])

    def test_unknown_sheet_gives_readable_error(self):
        path = self._path("multi2.xlsx")
        write_workbook(path, [("Population", [["Matricule"], ["E1"]])])
        with self.assertRaises(ImportError_) as caught:
            read_table(path, sheet="Absent")
        self.assertIn("introuvable", caught.exception.message)

    def test_missing_file_gives_readable_error(self):
        with self.assertRaises(ImportError_) as caught:
            read_table(self._path("nope.xlsx"))
        self.assertIn("introuvable", caught.exception.message)

    def test_unsupported_extension(self):
        path = self._path("p.docx")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("x")
        with self.assertRaises(ImportError_) as caught:
            read_table(path)
        self.assertIn("non pris en charge", caught.exception.message)

    def test_corrupted_xlsx_gives_readable_error(self):
        path = self._path("broken.xlsx")
        with open(path, "wb") as handle:
            handle.write(b"not a zip file")
        with self.assertRaises(ImportError_) as caught:
            read_table(path)
        self.assertIn("Excel", caught.exception.message)


class TestMapping(unittest.TestCase):
    def test_accent_and_case_insensitive(self):
        config = make_config()
        mapping = resolve_mapping(
            ["MATRICULE", "salaire de base", "Famille Métier"], config
        )
        self.assertEqual(mapping.field_to_index["employee_id"], 0)
        self.assertEqual(mapping.field_to_index["base_salary"], 1)
        self.assertEqual(mapping.field_to_index["job_family"], 2)

    def test_unknown_columns_are_listed_not_fatal(self):
        config = make_config()
        mapping = resolve_mapping(["Matricule", "Salaire de base", "Zone"], config)
        self.assertEqual(mapping.unknown_columns, ["Zone"])
        ensure_required(mapping, config)

    def test_missing_required_column_message_is_business_readable(self):
        config = make_config()
        mapping = resolve_mapping(["Matricule", "BU"], config)
        with self.assertRaises(MappingError) as caught:
            ensure_required(mapping, config)
        message = caught.exception.message
        self.assertIn("Salaire de base", message)
        self.assertNotIn("KeyError", message)
        self.assertNotIn("base_salary", message)

    def test_mapping_is_configurable_not_hardcoded(self):
        config = make_config({"population_mapping.fields": {
            "employee_id": ["ID interne"],
            "base_salary": ["Fixe annuel"],
        }})
        mapping = resolve_mapping(["ID interne", "Fixe annuel"], config)
        self.assertEqual(sorted(mapping.field_to_index), ["base_salary", "employee_id"])

    def test_duplicate_columns_are_reported(self):
        config = make_config()
        mapping = resolve_mapping(["Matricule", "Salaire de base", "Matricule"], config)
        self.assertEqual(len(mapping.duplicate_columns), 1)


if __name__ == "__main__":
    unittest.main()
