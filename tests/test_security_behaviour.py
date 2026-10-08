"""Ce que l'outil fait d'une donnee hostile, et non ce que le code declare.

Les garde-fous statiques (aucun `eval`, aucun import reseau, aucune
dependance externe) sont verifies ailleurs, sur le source. Ils ne disent
rien de ce qui se passe quand une colonne « Poste » contient une balise, une
formule, ou un retour a la ligne — or c'est ce qui arrive : un libelle de
poste est saisi a la main, un fichier de paie transite par des mains
nombreuses, et les documents produits, eux, circulent.

Aucune donnee RH reelle.
"""

import csv
import glob
import json
import os
import re
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import write_test_configuration
from tests.support import CONFIG_DIR
from tests.support import HEADERS, make_row
from hr_analytics.core import slides as _slides
from hr_analytics.core.config import (load_configuration,
                                                write_default_configuration)
from hr_analytics.core.export import export_excel
from hr_analytics.core.logging_setup import configure_logging, log_event
from hr_analytics.core.normalize import anonymise, anonymisation_salt
from hr_analytics.core.pipeline import AnalysisRequest, run_analysis
from hr_analytics.core.reporting import render_report

#: Ce qu'un libelle saisi a la main peut contenir de plus genant.
TRAPS = [
    "<script>alert(1)</script>",
    "\"><img src=x onerror=alert(1)>",
    "=cmd|'/c calc'!A1",
    "@SUM(1+1)*cmd",
    "Chef (de) projet \\ antislash",
    "ligne1\nligne2",
    "'; DROP TABLE --",
    "&lt;deja&gt; echappe",
]


class HostileFileCase(unittest.TestCase):
    """Une analyse complete sur un fichier dont chaque libelle est piege."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "piege.csv")
        with open(cls.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste"])
            for index in range(40):
                writer.writerow(list(make_row(
                    index, salary=40000 + index * 500,
                    gender="F" if index % 2 else "H",
                    business_unit=TRAPS[index % len(TRAPS)],
                    # La CSP porte aussi un piege : c'est elle que la
                    # synthese affiche, et un document ne se verifie que
                    # sur les champs qu'il montre reellement.
                    status=TRAPS[(index + 5) % len(TRAPS)]))
                    + [TRAPS[(index + 3) % len(TRAPS)]])
        cls.config_dir = os.path.join(cls.directory, "config")
        write_test_configuration(cls.config_dir)
        target = os.path.join(cls.config_dir, "export_parameters.json")
        with open(target, encoding="utf-8") as handle:
            settings = json.load(handle)
        settings["include_individual_data"] = True
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False)
        cls.result = run_analysis(AnalysisRequest(source_path=cls.source,
                                                  config_dir=cls.config_dir))

    def documents(self):
        deck = _slides.build_deck(self.result.payload)
        summary = _slides.build_summary(self.result.payload)
        return {
            "restitution": render_report(self.result.payload),
            "slides": _slides.render_slides_html(deck, self.result.payload),
            "synthèse": _slides.render_slides_html(summary, self.result.payload),
        }


class TestHtmlDocuments(HostileFileCase):
    """Les documents HTML s'ouvrent dans un navigateur, en local."""

    def test_no_tag_from_the_file_survives_as_markup(self):
        for name, document in self.documents().items():
            self.assertNotIn("<script>alert(1)</script>", document, name)
            self.assertNotIn("<img src=x", document, name)

    def test_the_dangerous_text_is_shown_escaped(self):
        """Il doit rester lisible : le masquer laisserait croire a une
        colonne vide."""
        for name, document in self.documents().items():
            self.assertIn("&lt;script&gt;", document, name)

    def test_quotes_are_escaped_too(self):
        """Une valeur posee dans un attribut sortirait de ses guillemets."""
        for name, document in self.documents().items():
            self.assertNotIn("\"><img", document, name)

    def test_an_already_escaped_value_is_not_double_read(self):
        """« &lt;deja&gt; » doit s'afficher tel quel, et non redevenir une
        balise."""
        for name, document in self.documents().items():
            self.assertNotIn("<deja>", document, name)

    def test_no_document_reaches_the_network(self):
        for name, document in self.documents().items():
            for pattern in ("http://", "https://", "//cdn", "src=\"//"):
                self.assertNotIn(pattern, document, f"{name} : {pattern}")

    def test_no_document_carries_a_name(self):
        for name, document in self.documents().items():
            self.assertNotIn("NOM0", document, name)
            self.assertNotIn("PRENOM0", document, name)


def _display_answers() -> bool:
    try:
        import tkinter
    except ImportError:                                # pragma: no cover
        return False
    if not os.environ.get("DISPLAY"):
        return False
    try:
        racine = tkinter.Tk()
    except tkinter.TclError:                           # pragma: no cover
        return False
    racine.destroy()
    return True


@unittest.skipUnless(_display_answers(),
                     "aucun affichage disponible (test d'interface ignoré)")
class TestTheWindowRefusesTheProfilesOfTk(unittest.TestCase):
    """Tk execute, a la creation de sa fenetre, « ~/.Tk.py » et
    « ~/.Tk.tcl » s'ils existent.

    C'est du code Python et du code Tcl arbitraires, pris dans le repertoire
    personnel : quiconque peut y deposer un fichier fait executer ce qu'il
    veut au demarrage de l'outil. CPython connait le defaut (issue 16248) et
    ne l'evite qu'avec le drapeau « -E », inutilisable pour un programme
    lance d'un double-clic.

    Le defaut a ete constate ici avant d'etre corrige : les deux fichiers
    s'executaient.
    """

    def setUp(self):
        self.maison = tempfile.mkdtemp()
        self.temoin = os.path.join(self.maison, "execute.txt")
        with open(os.path.join(self.maison, ".Tk.py"), "w",
                  encoding="utf-8") as fichier:
            fichier.write("open(%r, 'w').write('python')\n" % self.temoin)
        with open(os.path.join(self.maison, ".Tk.tcl"), "w",
                  encoding="utf-8") as fichier:
            fichier.write('set f [open "%s.tcl" w]; puts $f "tcl"; close $f\n'
                          % self.temoin)

    def test_a_profile_dropped_in_the_home_directory_is_not_executed(self):
        import tkinter

        from hr_analytics.ui.app import Application

        ancien = os.environ.get("HOME")
        os.environ["HOME"] = self.maison
        try:
            app = Application(splash=False)
            app.update()
            app.destroy()
        finally:
            if ancien is None:
                del os.environ["HOME"]
            else:
                os.environ["HOME"] = ancien
        self.assertFalse(os.path.exists(self.temoin),
                         "le profil Python de Tk a été exécuté")
        self.assertFalse(os.path.exists(self.temoin + ".tcl"),
                         "le profil Tcl de Tk a été exécuté")

    def test_the_guard_is_on_the_window_itself(self):
        """La parade doit tenir dans la classe, et non dans un lanceur : un
        outil qui ne se protege que lance d'une certaine facon ne se protege
        pas."""
        import tkinter

        from hr_analytics.ui.app import Application

        self.assertIsNot(Application.readprofile, tkinter.Tk.readprofile)


class TestWorkbook(HostileFileCase):
    def setUp(self):
        self.path = os.path.join(self.directory, "c.xlsx")
        export_excel(self.result.payload, self.result.filtered,
                     self.result.config, self.path)
        with zipfile.ZipFile(self.path) as archive:
            self.xml = "".join(
                archive.read(name).decode("utf-8")
                for name in archive.namelist() if name.endswith(".xml"))

    def test_a_value_starting_with_a_sign_never_becomes_a_formula(self):
        """« =cmd|'/c calc'!A1 » dans une cellule de poste : ecrit comme
        formule, il s'executerait a l'ouverture du classeur."""
        for expression in ("=cmd", "@SUM", "cmd|"):
            self.assertNotIn(f"<f>{expression}", self.xml)

    def test_the_only_formulas_are_the_ones_the_tool_writes(self):
        # Les formules matricielles portent des attributs : les ignorer
        # laissait hors du controle toutes celles qui recalculent un
        # segment, c'est-a-dire la plupart.
        written = set(re.findall(r"<f[^>]*>[-(]*([A-Z]+)", self.xml))
        allowed = {"SUM", "SUMPRODUCT", "ABS", "IF", "COUNT", "COUNTA",
                   "COUNTIFS", "AVERAGE", "MEDIAN", "MIN", "MAX",
                   "PERCENTILE", "STDEV", "DATE", "ISBLANK", "OR",
                   "B", "E", "H", "J"}
        self.assertTrue(written)
        for name in written:
            self.assertIn(name, allowed, name)

    def test_the_trapped_text_is_kept_as_text(self):
        self.assertIn("=cmd|'/c calc'!A1", self.xml)

    def test_the_workbook_can_be_read_back(self):
        """Preuve qu'aucun caractere n'a corrompu l'archive."""
        from hr_analytics.io.tabular import read_table

        table = read_table(self.path, "Population")
        self.assertTrue(table.rows)


class TestPdfDocuments(HostileFileCase):
    def test_every_pdf_is_well_formed(self):
        """Une parenthese ou un antislash non protege coupe une chaine PDF
        et rend le fichier illisible."""
        for name, builder in (("slides", _slides.build_deck),
                              ("synthèse", _slides.build_summary)):
            path = os.path.join(self.directory, f"{name}.pdf")
            _slides.write_slides_pdf(builder(self.result.payload),
                                     self.result.payload, path)
            with open(path, "rb") as handle:
                raw = handle.read()
            self.assertTrue(raw.startswith(b"%PDF-"), name)
            self.assertIn(b"%%EOF", raw[-32:], name)
            self.assertIn(b"/Root", raw, name)
            self.assertGreater(len(raw), 1000, name)


class TestTechnicalLog(unittest.TestCase):
    """Un journal auquel on peut faire dire n'importe quoi ne prouve rien."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        configure_logging(self.directory)

    def content(self):
        text = ""
        for path in glob.glob(os.path.join(self.directory, "*.log")):
            with open(path, encoding="utf-8") as handle:
                text += handle.read()
        return text

    def test_one_event_is_one_line(self):
        log_event("test", "action", detail="ligne1\nligne2 | FAUX")
        self.assertEqual(len(self.content().strip().splitlines()), 1)

    def test_a_carriage_return_cannot_erase_the_line(self):
        log_event("test", "action", detail="visible\rcache")
        self.assertIn("visible cache", self.content())

    def test_every_field_is_protected_not_only_the_detail(self):
        log_event("mod\nule", "act\nion", status="OK\nKO", detail="-")
        self.assertEqual(len(self.content().strip().splitlines()), 1)

    def test_the_line_keeps_its_shape(self):
        log_event("import", "read_table", status="OK", detail="rows=10")
        line = self.content().strip()
        self.assertEqual(len(line.split(" | ")), 6)


class TestAnonymousReference(unittest.TestCase):
    """La reference publiee ne doit pas rendre le matricule."""

    def test_the_salt_is_required(self):
        """Sans sel obligatoire, la fonction retombait sur une constante du
        code — c'est-a-dire sur aucun secret du tout."""
        with self.assertRaises(TypeError):
            anonymise("E00042")

    def test_two_runs_give_two_references_by_default(self):
        """Le reglage par defaut tire un sel au hasard a chaque analyse :
        un matricule vit dans un espace minuscule, et un sel connu le
        rendait retrouvable en un centieme de seconde."""
        config = load_configuration(CONFIG_DIR)
        self.assertNotEqual(anonymisation_salt(config),
                            anonymisation_salt(config))

    def test_a_declared_salt_makes_references_stable(self):
        """Pour suivre une situation d'une periode a la suivante, sur un
        poste dont on detient la configuration."""
        from tests.support import make_config

        config = make_config(
            {"privacy_parameters.anonymisation_salt": "sel-du-poste"})
        self.assertEqual(anonymisation_salt(config), "sel-du-poste")
        self.assertEqual(anonymisation_salt(config), "sel-du-poste")

    def test_brute_force_over_the_identifier_space_fails(self):
        """La reference est publiee ; le sel ne l'est pas."""
        salt = anonymisation_salt(load_configuration(CONFIG_DIR))
        target = anonymise("E04217", salt)
        for index in range(5000):
            self.assertNotEqual(anonymise(f"E{index:05d}", "un-autre-sel"),
                                target)

    def test_the_salt_never_reaches_a_produced_document(self):
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "p.csv")
        with open(source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(HEADERS)
            for index in range(20):
                writer.writerow(list(make_row(index)))
        config_dir = os.path.join(directory, "config")
        write_test_configuration(config_dir)
        target = os.path.join(config_dir, "privacy_parameters.json")
        with open(target, encoding="utf-8") as handle:
            settings = json.load(handle)
        settings["anonymisation_salt"] = "SEL-SECRET-DU-POSTE"
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False)
        result = run_analysis(AnalysisRequest(source_path=source,
                                              config_dir=config_dir))
        document = render_report(result.payload)
        self.assertNotIn("SEL-SECRET", document)
        self.assertNotIn("SEL-SECRET", json.dumps(result.payload, default=str))


class TestFileSystemReach(unittest.TestCase):
    """L'outil n'ecrit que la ou on le lui demande."""

    def test_reading_a_file_writes_nothing_beside_it(self):
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "p.csv")
        with open(source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(HEADERS)
            for index in range(10):
                writer.writerow(list(make_row(index)))
        from hr_analytics.io.tabular import read_table

        read_table(source)
        self.assertEqual(os.listdir(directory), ["p.csv"])

    def test_a_missing_configuration_folder_falls_back_on_the_defaults(self):
        """Un poste verrouille peut refuser l'ecriture : l'outil doit
        marcher sans jamais avoir ecrit sa configuration."""
        config = load_configuration(os.path.join(tempfile.mkdtemp(), "absent"))
        self.assertEqual(config.get("privacy_parameters.min_headcount_publish"),
                         5)


if __name__ == "__main__":
    unittest.main()


class TestAHostileWorkbookNeverGetsParsed(unittest.TestCase):
    """Un classeur arrive par courriel. Les trois pièges connus de ce
    format sont donc à écarter avant d'analyser quoi que ce soit.

    Ces essais partent d'un classeur **valide**, produit par l'outil
    lui-même, dont un seul morceau est remplacé. Une première version
    fabriquait les classeurs de toutes pièces : ils étaient mal formés
    ailleurs, l'analyseur les refusait pour cette raison-là, et les essais
    passaient au vert sans jamais atteindre la garde qu'ils prétendaient
    vérifier.
    """

    def setUp(self):
        from hr_analytics.io.xlsx_writer import write_workbook
        self.directory = tempfile.mkdtemp()
        self.base = os.path.join(self.directory, "base.xlsx")
        write_workbook(self.base, [("Population",
                                    [["Nom", "Salaire"], ["A", 1000]])])
        with zipfile.ZipFile(self.base) as archive:
            self.sheet = next(nom for nom in archive.namelist()
                              if "worksheets" in nom)
            self.saine = archive.read(self.sheet).decode("utf-8")

    def _rebuild(self, nom, feuille=None, extra=()):
        chemin = os.path.join(self.directory, nom)
        with zipfile.ZipFile(self.base) as src, \
                zipfile.ZipFile(chemin, "w", zipfile.ZIP_DEFLATED) as out:
            for info in src.infolist():
                contenu = src.read(info.filename)
                if feuille is not None and info.filename == self.sheet:
                    contenu = feuille.encode("utf-8")
                out.writestr(info.filename, contenu)
            for interne, donnees in extra:
                out.writestr(interne, donnees)
        return chemin

    def _corps(self, suffixe=""):
        return self.saine.split("?>", 1)[1].replace(
            "</sheetData>", f"{suffixe}</sheetData>")

    def test_the_healthy_workbook_still_reads(self):
        """Sans ce témoin, les essais qui suivent prouveraient seulement
        que l'outil refuse tout."""
        from hr_analytics.io.tabular import read_table
        self.assertEqual(len(read_table(self.base).rows), 1)

    def test_an_entity_bomb_in_the_sheet_is_refused(self):
        """Dix entités s'appelant l'une l'autre sur neuf niveaux font d'un
        fichier de deux kilo-octets dix gigaoctets à l'expansion.

        libexpat s'en défend depuis sa version 2.6 — mais cette défense
        appartient à la bibliothèque du poste, pas à l'outil. C'est la
        déclaration de type elle-même qui est refusée, et c'est la seule
        protection qui voyage avec le code.
        """
        from hr_analytics.core.errors import CompensationError
        from hr_analytics.io.tabular import read_table
        niveaux = 9
        doctype = ('<?xml version="1.0"?>\n<!DOCTYPE x [\n'
                   '<!ENTITY a0 "aaaaaaaaaa">\n'
                   + "".join(f'<!ENTITY a{rang} "{("&a%d;" % (rang - 1)) * 10}">\n'
                             for rang in range(1, niveaux + 1))
                   + ']>\n')
        corps = self._corps(
            f'<row r="9"><c r="A9" t="inlineStr"><is><t>&a{niveaux};</t>'
            '</is></c></row>')
        chemin = self._rebuild("bombe.xlsx", doctype + corps)
        self.assertLess(os.path.getsize(chemin), 10 * 1024)
        with self.assertRaises(CompensationError) as piege:
            read_table(chemin)
        self.assertIn("doctype", piege.exception.technical.lower())

    def test_an_external_entity_in_the_sheet_is_refused(self):
        """« file:///etc/passwd » dans une cellule : le classeur lirait le
        poste et recopierait ce qu'il y trouve dans l'analyse."""
        from hr_analytics.core.errors import CompensationError
        from hr_analytics.io.tabular import read_table
        doctype = ('<?xml version="1.0"?><!DOCTYPE x '
                   '[<!ENTITY secret SYSTEM "file:///etc/passwd">]>')
        corps = self._corps('<row r="9"><c r="A9" t="inlineStr"><is>'
                            '<t>&secret;</t></is></c></row>')
        with self.assertRaises(CompensationError) as piege:
            read_table(self._rebuild("xxe.xlsx", doctype + corps))
        self.assertIn("doctype", piege.exception.technical.lower())

    def test_a_zip_bomb_is_refused_on_its_announced_size(self):
        """Un demi-giga-octet dans un onglet, pour quelques kilo-octets sur
        le disque. Il est refusé sans être lu."""
        from hr_analytics.core.errors import CompensationError
        from hr_analytics.io.tabular import read_table
        from hr_analytics.io.tabular import DEFAULT_MAX_UNCOMPRESSED
        gonflee = self.saine + "<!--" + "A" * (4 * 1024 * 1024) + "-->"
        chemin = self._rebuild("bombe-zip.xlsx", gonflee)
        # Quelques kilo-octets sur le disque pour quatre méga-octets lus.
        self.assertLess(os.path.getsize(chemin), 64 * 1024)
        with self.assertRaises(CompensationError) as piege:
            read_table(chemin, max_uncompressed=1024 * 1024)
        self.assertIn("too large", piege.exception.technical.lower())
        # Le plafond d'origine reste assez haut pour un vrai classeur :
        # l'essai ci-dessus abaisse le plafond, il ne le suppose pas bas.
        self.assertGreaterEqual(DEFAULT_MAX_UNCOMPRESSED, 128 * 1024 * 1024)
        self.assertEqual(len(read_table(chemin).rows), 1)

    def test_a_member_pointing_outside_the_folder_writes_nothing(self):
        """Le lecteur n'extrait rien : il lit les morceaux qu'il nomme. Un
        membre « ../../.. » est donc inerte, et le classeur se lit."""
        from hr_analytics.io.tabular import read_table
        cible = os.path.join(self.directory, "evade.txt")
        interne = "../" * 8 + cible.lstrip("/")
        chemin = self._rebuild("traversee.xlsx",
                               extra=[(interne, b"evade")])
        self.assertEqual(len(read_table(chemin).rows), 1)
        self.assertFalse(os.path.exists(cible))

    def test_the_guard_does_not_blind_the_progress_bar(self):
        """La lecture d'un classeur montre son avancement, et l'avancement
        se mesure sur la position dans l'onglet. Le flux rendu par la
        garde doit donc la rendre comme le flux d'origine — faute de quoi
        l'import d'un gros fichier se fait sans un geste à l'écran."""
        from hr_analytics.io import tabular
        with zipfile.ZipFile(self.base) as archive:
            flux = tabular._without_doctype(archive, self.sheet)
            try:
                self.assertEqual(flux.tell(), 0)
                flux.read(10)
                self.assertEqual(flux.tell(), 10)
                reste = flux.read()
                self.assertEqual(flux.tell(), 10 + len(reste))
                self.assertEqual(flux.tell(), len(self.saine.encode("utf-8")))
            finally:
                flux.close()

    def test_the_sheet_is_still_read_as_a_stream(self):
        """La garde inspecte le début de l'onglet. Elle ne doit pas pour
        autant le charger entier : c'est la seule protection qui tienne
        contre un classeur de plusieurs centaines de méga-octets."""
        import io as _io
        from hr_analytics.io import tabular
        with zipfile.ZipFile(self.base) as archive:
            flux = tabular._without_doctype(archive, self.sheet)
            try:
                self.assertIsInstance(flux, _io.RawIOBase)
                self.assertEqual(flux.read(), self.saine.encode("utf-8"))
            finally:
                flux.close()
