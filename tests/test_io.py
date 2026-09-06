"""Tests d'import/export : CSV, XLSX, mapping, robustesse des formats."""

import datetime as _dt
import os
import tempfile
import unittest

from tests.support import build_population, make_config, make_row
from compensation_analytics.core.errors import ImportError_, MappingError
from compensation_analytics.core.mapping import ensure_required, resolve_mapping
from compensation_analytics.core.normalize import (
    has_ambiguous_separator, parse_number)
from compensation_analytics.io.tabular import read_table
from compensation_analytics.io.xlsx_writer import write_workbook


# Classeur minimal ou les lignes 3 a 6 sont absentes, comme Excel les omet.
_SHEET_WITH_GAP = (
    '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org'
    '/spreadsheetml/2006/main"><sheetData>'
    '<row r="1"><c r="A1" t="inlineStr"><is><t>Matricule</t></is></c>'
    '<c r="B1" t="inlineStr"><is><t>Salaire de base</t></is></c></row>'
    '<row r="2"><c r="A2" t="inlineStr"><is><t>M1</t></is></c>'
    '<c r="B2"><v>50000</v></c></row>'
    '<row r="7"><c r="A7" t="inlineStr"><is><t>M2</t></is></c>'
    '<c r="B7"><v>60000</v></c></row>'
    '</sheetData></worksheet>')
_WORKBOOK = (
    '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org'
    '/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org'
    '/officeDocument/2006/relationships"><sheets><sheet name="Feuille" '
    'sheetId="1" r:id="rId1"/></sheets></workbook>')
_WORKBOOK_RELS = (
    '<?xml version="1.0"?><Relationships xmlns="http://schemas.'
    'openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
_ROOT_RELS = (
    '<?xml version="1.0"?><Relationships xmlns="http://schemas.'
    'openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
_CONTENT_TYPES = (
    '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org'
    '/package/2006/content-types"><Default Extension="rels" ContentType='
    '"application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.'
    'openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application'
    '/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')


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
            ["Matricule", "Salaire de base", "Date d'entrée"],
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

    def test_rows_omitted_by_excel_keep_the_numbering(self):
        """Excel n'ecrit pas les lignes vides : il saute de la ligne 2 a la
        ligne 7. Lues a la suite, les donnees se decalaient et le controle
        qualite renvoyait l'utilisateur a une ligne qui n'etait pas celle a
        corriger — inexploitable sur un fichier de cinq mille salaries.
        """
        import zipfile

        path = self._path("trous.xlsx")
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
            archive.writestr("_rels/.rels", _ROOT_RELS)
            archive.writestr("xl/workbook.xml", _WORKBOOK)
            archive.writestr("xl/_rels/workbook.xml.rels", _WORKBOOK_RELS)
            archive.writestr("xl/worksheets/sheet1.xml", _SHEET_WITH_GAP)

        table = read_table(path)
        self.assertEqual(table.headers, ["Matricule", "Salaire de base"])
        # Ligne 2 du classeur, puis quatre lignes vides, puis la ligne 7.
        self.assertEqual(table.rows[0][0], "M1")
        self.assertEqual(table.rows[5][0], "M2")
        self.assertEqual(len(table.rows), 6)

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


class TestNumbersAreReadOrRefused(unittest.TestCase):
    """Une cellule qui n'est pas un nombre doit etre refusee, jamais rabotee.

    Le defaut corrige : la lecture supprimait tout caractere non chiffre.
    "1E+05" devenait 105, "50k" devenait 50 et "5O000" — la lettre O frappee
    a la place du zero — devenait 5 000. La valeur passait pour un salaire
    plausible et le controle qualite annoncait CONFORME : une remuneration
    fausse, sans la moindre alerte.
    """

    def test_a_cell_that_is_not_a_number_is_refused(self):
        for text in ("1e5", "1E+05", "50k", "5O000", "12 mois", "N/A50000",
                     "environ 50000", "sans objet", "-", ".", "1 200 F CFA x"):
            self.assertIsNone(parse_number(text), text)

    def test_the_usual_writings_are_still_read(self):
        for text, expected in (("45000", 45000.0), ("45 000,50", 45000.5),
                               ("45,000.50", 45000.5), ("1.234.567,89",
                                                        1234567.89),
                               ("50000.75", 50000.75), ("0,800", 0.8),
                               ("-12500", -12500.0), ("+12500", 12500.0)):
            self.assertEqual(parse_number(text), expected, text)

    def test_currency_symbols_and_codes_are_tolerated(self):
        for text in ("1 200 €", "1200 EUR", "EUR 1200", "1200eur",
                     "1\u00a0200\u00a0€", "1200 CHF"):
            self.assertEqual(parse_number(text), 1200.0, text)

    def test_a_repeated_separator_can_only_be_thousands(self):
        """"1.234.567" n'a qu'une lecture possible. La version precedente la
        refusait, et toute une colonne partait en « non numerique »."""
        self.assertEqual(parse_number("1.234.567"), 1234567.0)
        self.assertEqual(parse_number("1,234,567"), 1234567.0)

    def test_accounting_parentheses_carry_the_sign(self):
        """"(1 200)" vaut -1 200 en ecriture comptable. Lu 1 200, il
        inversait le signe d'une regularisation."""
        self.assertEqual(parse_number("(1200)"), -1200.0)
        self.assertEqual(parse_number("(1 200,50)"), -1200.5)

    def test_a_single_separator_stays_ambiguous_and_is_reported(self):
        """"45.000" vaut 45 000 en France et 45,0 ailleurs : la lecture
        decimale est retenue, et l'ambiguite signalee — pas devinee."""
        self.assertEqual(parse_number("45.000"), 45.0)
        self.assertTrue(has_ambiguous_separator("45.000"))
        self.assertFalse(has_ambiguous_separator("1.234.567"))

    def test_a_refused_cell_is_counted_as_not_numeric(self):
        """Refuser sans le dire reviendrait a perdre la colonne en silence."""
        config = make_config()
        rows = [make_row(i, salary=40000) for i in range(10)]
        rows.append(make_row(99, salary="1E+05"))
        population = build_population(rows, config)
        self.assertIn("base_salary:not_numeric",
                      population.employees[-1].issues)


class TestAWorkbookStaysReadable(unittest.TestCase):
    """Un classeur illisible fait perdre l'export entier, pas une cellule."""

    def test_a_control_character_does_not_corrupt_the_workbook(self):
        """Un export mainframe peut porter une tabulation verticale ou une
        cloche. Ecrites telles quelles, elles produisaient un XML invalide
        et Excel refusait le classeur en entier."""
        import xml.dom.minidom as minidom
        import zipfile

        path = os.path.join(tempfile.mkdtemp(), "controle.xlsx")
        write_workbook(path, [("Feuille", [
            ["Libellé", "Valeur"],
            ["cloche" + chr(7) + "interne", 1],
            ["saut" + chr(11) + "vertical", 2],
            ["tabulation\treelle", 3],
        ])])
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith((".xml", ".rels")):
                    minidom.parseString(archive.read(name))
            sheet = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
        # La tabulation est licite en XML : elle, on la garde.
        self.assertIn("\t", sheet)
        self.assertNotIn(chr(7), sheet)

    def test_a_text_cell_never_becomes_a_formula(self):
        """Une valeur commencant par « = » venue d'un fichier RH ne doit pas
        s'executer a l'ouverture du classeur."""
        import zipfile

        path = os.path.join(tempfile.mkdtemp(), "formule.xlsx")
        write_workbook(path, [("Feuille", [["Libellé"], ["=1+1"],
                                           ["=cmd|'/c calc'!A1"]])])
        with zipfile.ZipFile(path) as archive:
            sheet = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertNotIn("<f>", sheet)


if __name__ == "__main__":
    unittest.main()
