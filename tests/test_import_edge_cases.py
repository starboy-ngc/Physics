"""Ce que la couche d'import fait des fichiers reels — et des mauvais.

Un fichier de paie n'est jamais celui du manuel : lignes vides au milieu,
colonnes mises en forme jusqu'au bout de la feuille, chaines partagees,
booleens, cellules en erreur, onglets multiples. Ces cas ne se decouvrent
pas en production : ils s'ecrivent ici.

Les classeurs sont fabriques a la main, sans passer par le redacteur XLSX de
l'outil : un lecteur teste avec son propre ecrivain ne teste que leur accord.
Aucune donnee RH reelle.
"""

import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.core.errors import ImportError_
from compensation_analytics.io.tabular import read_table

NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
RELS = 'xmlns="http://schemas.openxmlformats.org/package/2006/relationships"'


def sheet(body: str) -> str:
    return f'<worksheet {NS}><sheetData>{body}</sheetData></worksheet>'


def row(number: int, *cells: str) -> str:
    return f'<row r="{number}">{"".join(cells)}</row>'


def cell(reference: str, value=None, kind=None, style=None) -> str:
    attributes = f' r="{reference}"'
    if kind:
        attributes += f' t="{kind}"'
    if style is not None:
        attributes += f' s="{style}"'
    if value is None:
        return f"<c{attributes}/>"
    if kind == "inlineStr":
        return f"<c{attributes}><is><t>{value}</t></is></c>"
    return f"<c{attributes}><v>{value}</v></c>"


class WorkbookBuilder:
    """Classeur XLSX minimal, ecrit a la main."""

    def __init__(self, directory: str):
        self.directory = directory

    def write(self, name: str, sheets, shared=None, styles=None,
              omit_sheets=False, extra=None) -> str:
        path = os.path.join(self.directory, name)
        entries = [(label, xml) for label, xml in sheets]
        declared = "".join(
            f'<sheet name="{label}" sheetId="{index + 1}" '
            f'r:id="rId{index + 1}"/>'
            for index, (label, _xml) in enumerate(entries))
        links = "".join(
            f'<Relationship Id="rId{index + 1}" Type="http://schemas.'
            f'openxmlformats.org/officeDocument/2006/relationships/worksheet"'
            f' Target="worksheets/sheet{index + 1}.xml"/>'
            for index in range(len(entries)))
        extra = dict(extra or {})
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            def put(member, content):
                # « extra » remplace le membre standard plutot que de s'y
                # ajouter : une archive a deux membres de meme nom n'est
                # plus un classeur, et le test ne prouverait rien.
                archive.writestr(member, extra.pop(member, content))

            put("[Content_Types].xml", "<Types/>")
            put(
                "_rels/.rels",
                f'<Relationships {RELS}><Relationship Id="rId1" Type="http://'
                'schemas.openxmlformats.org/officeDocument/2006/relationships'
                '/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            put(
                "xl/workbook.xml",
                '<workbook xmlns="http://schemas.openxmlformats.org/'
                'spreadsheetml/2006/main" xmlns:r="http://schemas.'
                'openxmlformats.org/officeDocument/2006/relationships">'
                + ("" if omit_sheets else f"<sheets>{declared}</sheets>")
                + "</workbook>")
            put("xl/_rels/workbook.xml.rels",
                f"<Relationships {RELS}>{links}</Relationships>")
            for index, (_label, xml) in enumerate(entries):
                put(f"xl/worksheets/sheet{index + 1}.xml", xml)
            if shared is not None:
                put("xl/sharedStrings.xml", shared)
            if styles is not None:
                put("xl/styles.xml", styles)
            for member, content in extra.items():
                archive.writestr(member, content)
        return path


class ImportCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.builder = WorkbookBuilder(self.directory)

    def csv(self, name: str, text: str, encoding="utf-8") -> str:
        path = os.path.join(self.directory, name)
        with open(path, "w", encoding=encoding, newline="") as handle:
            handle.write(text)
        return path


class TestCsvSeparators(ImportCase):
    """Le separateur se devine : personne ne le declare."""

    def test_semicolon_is_read(self):
        table = read_table(self.csv("a.csv", "Matricule;Salaire\nE1;40000\n"))
        self.assertEqual(table.headers, ["Matricule", "Salaire"])
        self.assertEqual(table.rows, [["E1", "40000"]])

    def test_comma_is_read(self):
        table = read_table(self.csv("b.csv", "Matricule,Salaire\nE1,40000\n"))
        self.assertEqual(table.headers, ["Matricule", "Salaire"])

    def test_tabulation_is_read(self):
        table = read_table(self.csv("c.csv", "Matricule\tSalaire\nE1\t40000\n"))
        self.assertEqual(table.headers, ["Matricule", "Salaire"])

    def test_pipe_is_read(self):
        table = read_table(self.csv("d.csv", "Matricule|Salaire\nE1|40000\n"))
        self.assertEqual(table.headers, ["Matricule", "Salaire"])

    def test_a_single_column_falls_back_to_the_comma(self):
        """Rien a renifler : le repli ne doit pas lever."""
        table = read_table(self.csv("e.csv", "Matricule\nE1\nE2\n"))
        self.assertEqual(table.headers, ["Matricule"])
        self.assertEqual(len(table.rows), 2)

    def test_the_byte_order_mark_is_not_glued_to_the_first_header(self):
        """Excel ecrit un BOM : sans le retirer, « Matricule » ne
        correspond plus a rien et le fichier parait sans matricule."""
        table = read_table(self.csv("f.csv", "﻿Matricule;Salaire\nE1;1\n"))
        self.assertEqual(table.headers[0], "Matricule")

    def test_a_quoted_separator_stays_inside_its_cell(self):
        table = read_table(self.csv(
            "g.csv", 'Matricule;Poste\nE1;"Comptable; senior"\n'))
        self.assertEqual(table.rows[0][1], "Comptable; senior")

    def test_a_quoted_newline_stays_inside_its_cell(self):
        table = read_table(self.csv(
            "h.csv", 'Matricule;Poste\nE1;"Comptable\nsenior"\nE2;Chef\n'))
        self.assertEqual(len(table.rows), 2)
        self.assertIn("\n", table.rows[0][1])


class TestCsvRefusals(ImportCase):
    def test_an_empty_file_is_refused_with_a_readable_message(self):
        with self.assertRaises(ImportError_) as caught:
            read_table(self.csv("vide.csv", ""))
        self.assertIn("vide", caught.exception.message.lower())

    def test_a_file_that_is_not_utf8_names_the_remedy(self):
        """Le cas le plus frequent en France : un CSV enregistre en
        Windows-1252. Le message doit dire quoi faire, pas « codec »."""
        path = os.path.join(self.directory, "cp1252.csv")
        with open(path, "wb") as handle:
            handle.write("Matricule;Établissement\nE1;Siège\n".encode("cp1252"))
        with self.assertRaises(ImportError_) as caught:
            read_table(path)
        self.assertIn("UTF-8", caught.exception.message)
        self.assertIn("Excel", caught.exception.message)

    def test_a_missing_file_is_refused(self):
        with self.assertRaises(ImportError_):
            read_table(os.path.join(self.directory, "absent.csv"))

    def test_an_unknown_extension_is_refused_with_the_accepted_list(self):
        with self.assertRaises(ImportError_) as caught:
            read_table(self.csv("feuille.ods", "Matricule;Salaire\nE1;1\n"))
        self.assertIn(".xlsx", caught.exception.message)
        self.assertIn(".csv", caught.exception.message)

    def test_a_txt_file_is_read_as_a_csv(self):
        """Un export texte a separateur est un CSV qui s'ignore."""
        table = read_table(self.csv("notes.txt", "Matricule;Salaire\nE1;1\n"))
        self.assertEqual(table.headers, ["Matricule", "Salaire"])


class TestRaggedRows(ImportCase):
    """Les lignes courtes et longues, des deux formats."""

    def test_a_short_row_is_completed(self):
        table = read_table(self.csv("a.csv", "A;B;C\n1;2\n"))
        self.assertEqual(table.rows[0], ["1", "2", ""])

    def test_a_row_longer_than_the_header_is_trimmed(self):
        """Les cellules au-dela du dernier intitule ne correspondent a
        aucun champ : les garder n'apporte rien."""
        table = read_table(self.csv("b.csv", "A;B\n1;2;3;4\n"))
        self.assertEqual(table.rows[0], ["1", "2"])

    def test_a_column_without_a_header_is_dropped(self):
        table = read_table(self.csv("c.csv", "A;;C\n1;2;3\n"))
        self.assertEqual(table.headers, ["A", "C"])
        self.assertEqual(table.rows[0], ["1", "3"])


class TestCellTypes(ImportCase):
    """Les six ecritures de cellule d'un classeur Excel."""

    def _read(self, body, **kwargs):
        path = self.builder.write("t.xlsx", [("P", sheet(body))], **kwargs)
        return read_table(path)

    def test_a_shared_string_is_resolved(self):
        table = self._read(
            row(1, cell("A1", 0, "s")) + row(2, cell("A2", 1, "s")),
            shared=f'<sst {NS}><si><t>Matricule</t></si>'
                   '<si><t>E1</t></si></sst>')
        self.assertEqual(table.headers, ["Matricule"])
        self.assertEqual(table.rows[0], ["E1"])

    def test_a_shared_string_out_of_range_becomes_empty(self):
        """Un index qui depasse la table ne doit pas lever : le classeur
        est incoherent, l'import doit continuer."""
        table = self._read(
            row(1, cell("A1", 0, "s"), cell("B1", "Reste", "inlineStr"))
            + row(2, cell("A2", 99, "s"), cell("B2", "ok", "inlineStr")),
            shared=f'<sst {NS}><si><t>Matricule</t></si></sst>')
        self.assertEqual(table.rows[0], ["", "ok"])

    def test_a_rich_text_string_is_concatenated(self):
        """Une chaine mise en forme par morceaux se lit d'un bloc."""
        table = self._read(
            row(1, cell("A1", 0, "s")),
            shared=f'<sst {NS}><si><r><t>Matri</t></r>'
                   '<r><t>cule</t></r></si></sst>')
        self.assertEqual(table.headers, ["Matricule"])

    def test_an_inline_string_is_read(self):
        table = self._read(row(1, cell("A1", "Matricule", "inlineStr")))
        self.assertEqual(table.headers, ["Matricule"])

    def test_an_empty_inline_string_is_read(self):
        table = self._read(
            row(1, cell("A1", "Matricule", "inlineStr"),
                cell("B1", "Reste", "inlineStr"))
            + row(2, '<c r="A2" t="inlineStr"/>',
                  cell("B2", "ok", "inlineStr")))
        self.assertEqual(table.rows[0], ["", "ok"])

    def test_a_cached_formula_value_is_read(self):
        """L'outil lit la valeur calculee, jamais la formule."""
        table = self._read(row(1, cell("A1", "Total", "str"))
                           + row(2, cell("A2", "45000", "str")))
        self.assertEqual(table.rows[0], ["45000"])

    def test_a_boolean_becomes_a_boolean(self):
        table = self._read(row(1, cell("A1", "Cadre", "inlineStr"))
                           + row(2, cell("A2", 1, "b"))
                           + row(3, cell("A3", 0, "b")))
        self.assertEqual(table.rows, [[True], [False]])

    def test_an_error_cell_keeps_its_text(self):
        """#DIV/0! doit rester lisible : le controle qualite le signalera
        comme non numerique, avec son numero de ligne."""
        table = self._read(row(1, cell("A1", "Salaire", "inlineStr"))
                           + row(2, cell("A2", "#DIV/0!", "e")))
        self.assertEqual(table.rows[0], ["#DIV/0!"])

    def test_an_empty_cell_is_empty(self):
        table = self._read(row(1, cell("A1", "A", "inlineStr"),
                               cell("B1", "B", "inlineStr"))
                           + row(2, cell("A2"), cell("B2", 1)))
        self.assertEqual(table.rows[0], ["", 1])

    def test_a_whole_number_stays_whole(self):
        """« 45000.0 » affiche en matricule ferait un identifiant faux."""
        table = self._read(row(1, cell("A1", "N", "inlineStr"))
                           + row(2, cell("A2", "45000")))
        self.assertEqual(table.rows[0], [45000])
        self.assertIsInstance(table.rows[0][0], int)

    def test_a_decimal_stays_decimal(self):
        table = self._read(row(1, cell("A1", "N", "inlineStr"))
                           + row(2, cell("A2", "0.8")))
        self.assertEqual(table.rows[0], [0.8])

    def test_a_non_numeric_value_without_type_is_kept_as_text(self):
        table = self._read(row(1, cell("A1", "N", "inlineStr"))
                           + row(2, cell("A2", "N/A")))
        self.assertEqual(table.rows[0], ["N/A"])


class TestDates(ImportCase):
    """Une date Excel est un nombre : sans le style, c'est 45 000."""

    def _read(self, body, styles):
        path = self.builder.write("d.xlsx", [("P", sheet(body))],
                                  styles=styles)
        return read_table(path)

    def test_a_builtin_date_style_gives_a_date(self):
        import datetime as _dt

        table = self._read(
            row(1, cell("A1", "Date", "inlineStr"))
            + row(2, cell("A2", "45000", style=0)),
            styles=f'<styleSheet {NS}><cellXfs><xf numFmtId="14"/>'
                   '</cellXfs></styleSheet>')
        self.assertEqual(table.rows[0][0], _dt.date(2023, 3, 15))

    def test_a_custom_date_format_gives_a_date(self):
        import datetime as _dt

        table = self._read(
            row(1, cell("A1", "Date", "inlineStr"))
            + row(2, cell("A2", "45000", style=0)),
            styles=f'<styleSheet {NS}>'
                   '<numFmts><numFmt numFmtId="166" formatCode="dd/mm/yyyy"/>'
                   '</numFmts><cellXfs><xf numFmtId="166"/></cellXfs>'
                   '</styleSheet>')
        self.assertEqual(table.rows[0][0], _dt.date(2023, 3, 15))

    def test_a_currency_format_is_not_a_date(self):
        """« #,##0 [$€-40C] » contient un mois si on lit trop vite : le
        crochet et les guillemets doivent etre retires avant de chercher."""
        table = self._read(
            row(1, cell("A1", "Montant", "inlineStr"))
            + row(2, cell("A2", "45000", style=0)),
            styles=f'<styleSheet {NS}><numFmts>'
                   '<numFmt numFmtId="166" formatCode="#,##0 [$&#8364;-40C]"/>'
                   '</numFmts><cellXfs><xf numFmtId="166"/></cellXfs>'
                   '</styleSheet>')
        self.assertEqual(table.rows[0][0], 45000)

    def test_an_impossible_serial_stays_a_number(self):
        """Une date hors calendrier ne fait pas lever l'import."""
        table = self._read(
            row(1, cell("A1", "Date", "inlineStr"))
            + row(2, cell("A2", "99999999")),
            styles=f'<styleSheet {NS}><cellXfs><xf numFmtId="14"/>'
                   '</cellXfs></styleSheet>')
        self.assertEqual(table.rows[0][0], 99999999)

    def test_a_workbook_without_styles_reads_numbers(self):
        path = self.builder.write("s.xlsx", [("P", sheet(
            row(1, cell("A1", "N", "inlineStr")) + row(2, cell("A2", "1"))))])
        self.assertEqual(read_table(path).rows[0][0], 1)


class TestSheetGeometry(ImportCase):
    """La geometrie de la feuille : trous, colonnes creuses, lignes vides."""

    def _read(self, body, **kwargs):
        path = self.builder.write("g.xlsx", [("P", sheet(body))], **kwargs)
        return read_table(path)

    def test_a_sparse_row_keeps_its_columns_aligned(self):
        """La cellule C2 doit rester sous l'intitule C, meme si A2 et B2
        n'existent pas dans le fichier."""
        table = self._read(
            row(1, cell("A1", "A", "inlineStr"), cell("B1", "B", "inlineStr"),
                cell("C1", "C", "inlineStr"))
            + row(2, cell("C2", "ici", "inlineStr")))
        self.assertEqual(table.rows[0], ["", "", "ici"])

    def test_an_omitted_empty_row_is_restored(self):
        """Excel n'ecrit pas les lignes vides : sans les restituer, le
        controle qualite renvoie a une ligne qui n'est pas la bonne."""
        table = self._read(
            row(1, cell("A1", "A", "inlineStr"))
            + row(2, cell("A2", "un", "inlineStr"))
            + row(5, cell("A5", "quatre", "inlineStr")))
        self.assertEqual([value for (value,) in table.rows],
                         ["un", "", "", "quatre"])

    def test_a_ghost_row_number_does_not_fill_memory(self):
        """Une ligne annoncee au milliard releve du fichier fabrique :
        mieux vaut une numerotation decalee qu'un million de lignes."""
        table = self._read(
            row(1, cell("A1", "A", "inlineStr"))
            + row(999999999, cell("A999999999", "loin", "inlineStr")))
        self.assertLess(len(table.rows), 100)

    def test_trailing_empty_rows_are_dropped(self):
        table = self._read(
            row(1, cell("A1", "A", "inlineStr"))
            + row(2, cell("A2", "un", "inlineStr"))
            + row(3, cell("A3")) + row(4, cell("A4")))
        self.assertEqual(len(table.rows), 1)

    def test_a_stray_cell_at_the_far_right_costs_nothing(self):
        """Le defaut corrige : une ligne mise en forme jusqu'au bout de la
        feuille — frequent dans un export RH — portait un fichier de 5 000
        lignes a 16 384 colonnes, 82 millions de cellules, 1,3 Go de
        memoire et dix secondes. Une colonne sans intitule ne peut
        correspondre a aucun champ : elle est ecartee des l'import."""
        table = self._read(
            row(1, cell("A1", "Matricule", "inlineStr"), cell("XFD1", style=3))
            + row(2, cell("A2", "E1", "inlineStr")))
        self.assertEqual(table.headers, ["Matricule"])
        self.assertEqual(len(table.rows[0]), 1)

    def test_a_cell_without_a_reference_lands_after_the_previous_one(self):
        table = self._read(
            row(1, cell("A1", "A", "inlineStr"), cell("B1", "B", "inlineStr"))
            + '<row r="2"><c t="inlineStr"><is><t>un</t></is></c>'
              '<c t="inlineStr"><is><t>deux</t></is></c></row>')
        self.assertEqual(table.rows[0], ["un", "deux"])

    def test_an_empty_sheet_is_refused(self):
        with self.assertRaises(ImportError_) as caught:
            self._read("")
        self.assertIn("aucune donnée", caught.exception.message)


class TestWorkbookStructure(ImportCase):
    def test_a_named_sheet_is_chosen(self):
        path = self.builder.write("m.xlsx", [
            ("Premier", sheet(row(1, cell("A1", "A", "inlineStr"))
                              + row(2, cell("A2", "un", "inlineStr")))),
            ("Second", sheet(row(1, cell("A1", "Z", "inlineStr"))
                             + row(2, cell("A2", "deux", "inlineStr")))),
        ])
        self.assertEqual(read_table(path, "Second").headers, ["Z"])
        self.assertEqual(read_table(path).headers, ["A"])

    def test_an_unknown_sheet_is_refused_with_the_list(self):
        path = self.builder.write("m.xlsx", [
            ("Premier", sheet(row(1, cell("A1", "A", "inlineStr")))),
            ("Second", sheet(row(1, cell("A1", "Z", "inlineStr")))),
        ])
        with self.assertRaises(ImportError_) as caught:
            read_table(path, "Troisieme")
        self.assertIn("Premier", caught.exception.message)
        self.assertIn("Second", caught.exception.message)

    def test_a_workbook_without_sheets_is_refused(self):
        path = self.builder.write(
            "n.xlsx", [("P", sheet(row(1, cell("A1", "A", "inlineStr"))))],
            omit_sheets=True)
        with self.assertRaises(ImportError_) as caught:
            read_table(path)
        self.assertIn("aucun onglet", caught.exception.message)

    def test_a_file_that_is_not_a_zip_is_refused(self):
        path = os.path.join(self.directory, "faux.xlsx")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("ceci n'est pas un classeur")
        with self.assertRaises(ImportError_) as caught:
            read_table(path)
        self.assertIn("Excel", caught.exception.message)

    def test_a_truncated_workbook_is_refused(self):
        path = self.builder.write(
            "tronque.xlsx", [("P", sheet(row(1, cell("A1", "A", "inlineStr"))))])
        with open(path, "r+b") as handle:
            handle.truncate(200)
        with self.assertRaises(ImportError_):
            read_table(path)

    def test_a_workbook_with_broken_xml_is_refused(self):
        path = self.builder.write("casse.xlsx", [("P", "<worksheet><sheetData")])
        with self.assertRaises(ImportError_) as caught:
            read_table(path)
        self.assertIn("Excel", caught.exception.message)

    def test_an_xlsm_file_is_read_like_an_xlsx(self):
        """Un classeur a macros s'importe : l'outil n'execute rien."""
        path = self.builder.write(
            "macros.xlsm", [("P", sheet(row(1, cell("A1", "A", "inlineStr"))
                                        + row(2, cell("A2", "un", "inlineStr"))))],
            extra={"xl/vbaProject.bin": b"\x00\x01macro"})
        self.assertEqual(read_table(path).headers, ["A"])


class TestHostileWorkbooks(ImportCase):
    """Un classeur peut venir d'ailleurs que du service paie."""

    def test_expanding_entities_are_refused(self):
        """« Billion laughs » : neuf entites imbriquees suffisent a saturer
        la memoire d'un lecteur XML naif."""
        entities = "".join(
            f'<!ENTITY e{i} "{"&e%d;" % (i - 1) * 10}">' if i
            else '<!ENTITY e0 "AAAAAAAAAA">' for i in range(9))
        path = self.builder.write(
            "bombe.xlsx", [("P", sheet(row(1, cell("A1", 0, "s"))))],
            shared=f'<!DOCTYPE sst [{entities}]><sst {NS}>'
                   '<si><t>&e8;</t></si></sst>')
        with self.assertRaises(ImportError_):
            read_table(path)

    def test_an_external_entity_is_refused(self):
        """Sans refus, le classeur ferait lire /etc/passwd a l'outil et en
        placerait le contenu dans une cellule."""
        path = self.builder.write(
            "xxe.xlsx", [("P", sheet(row(1, cell("A1", 0, "s"))))],
            shared='<!DOCTYPE sst [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
                   f'<sst {NS}><si><t>&xxe;</t></si></sst>')
        with self.assertRaises(ImportError_):
            read_table(path)

    def test_a_worksheet_outside_the_archive_is_not_followed(self):
        """Un chemin relatif remontant hors de l'archive ne doit pas
        atteindre le disque."""
        path = self.builder.write(
            "traversee.xlsx", [("P", sheet(row(1, cell("A1", "A", "inlineStr"))))],
            extra={"xl/_rels/workbook.xml.rels":
                   f'<Relationships {RELS}><Relationship Id="rId1" Type='
                   '"http://schemas.openxmlformats.org/officeDocument/2006/'
                   'relationships/worksheet" Target="../../../etc/passwd"/>'
                   '</Relationships>'})
        with self.assertRaises(ImportError_):
            read_table(path)


if __name__ == "__main__":
    unittest.main()
