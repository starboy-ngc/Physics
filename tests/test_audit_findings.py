"""Les défauts trouvés à l'audit, et ce qui les empêche de revenir.

Trois constats, trois mécaniques différentes : une bombe à entités dans
un classeur, un réglage effacé par l'enregistrement d'un autre, une page
vide qui ne disait pas pourquoi.

Aucune donnée RH réelle.
"""

import json
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_analytics.core.errors import ImportError_
from hr_analytics.io.tabular import read_table

try:
    import tkinter
    HAS_TK = True
except ImportError:                                    # pragma: no cover
    HAS_TK = False


def _classeur(chemin: str, partagees: str) -> str:
    """Un .xlsx minimal dont on choisit le fichier de chaînes partagées."""
    with zipfile.ZipFile(chemin, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0"?><workbook xmlns="http://schemas.'
            'openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://'
            'schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="F1" sheetId="1" r:id="rId1"/></sheets>'
            '</workbook>')
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0"?><Relationships xmlns="http://schemas.'
            'openxmlformats.org/package/2006/relationships"><Relationship '
            'Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr("xl/sharedStrings.xml", partagees)
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<?xml version="1.0"?><worksheet xmlns="http://schemas.'
            'openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
            '<row r="1"><c r="A1" t="s"><v>0</v></c></row></sheetData>'
            '</worksheet>')
    return chemin


class TestTheEntityBomb(unittest.TestCase):
    """Un kilo-octet qui en réclame un milliard à l'ouverture.

    Les versions récentes de libexpat s'en défendent seules. Mais cette
    défense appartient à la bibliothèque du poste et non à l'outil : un
    poste resté sur une version plus ancienne ne l'a pas. Le refus de la
    déclaration de type voyage, lui, avec le code.
    """

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def _bombe(self, niveaux: int) -> str:
        lignes = ['<!ENTITY n0 "' + "A" * 100 + '">']
        for rang in range(1, niveaux):
            lignes.append(f'<!ENTITY n{rang} "' + f"&n{rang - 1};" * 10 + '">')
        return ('<?xml version="1.0"?>\n<!DOCTYPE sst [\n'
                + "\n".join(lignes) + "\n]>\n"
                '<sst xmlns="http://schemas.openxmlformats.org/'
                f'spreadsheetml/2006/main" count="1"><si><t>&n{niveaux - 1};'
                "</t></si></sst>")

    def test_a_workbook_with_a_doctype_is_refused(self):
        chemin = _classeur(os.path.join(self.directory, "bombe.xlsx"),
                           self._bombe(8))
        with self.assertRaises(ImportError_) as pris:
            read_table(chemin)
        self.assertIn("déclaration de type", pris.exception.message)

    def test_the_refusal_costs_nothing_to_establish(self):
        """Le fichier pèse un kilo-octet : il est refusé sur sa seule
        déclaration, sans que rien ne soit développé."""
        chemin = _classeur(os.path.join(self.directory, "petite.xlsx"),
                           self._bombe(3))
        self.assertLess(os.path.getsize(chemin), 4096)
        with self.assertRaises(ImportError_):
            read_table(chemin)

    def test_a_workbook_without_a_doctype_still_opens(self):
        """Le refus ne doit pas fermer la porte aux classeurs ordinaires."""
        chemin = _classeur(
            os.path.join(self.directory, "normal.xlsx"),
            '<?xml version="1.0"?><sst xmlns="http://schemas.openxmlformats'
            '.org/spreadsheetml/2006/main" count="1"><si><t>Matricule</t>'
            "</si></sst>")
        table = read_table(chemin)
        self.assertEqual(table.headers, ["Matricule"])

    def test_the_message_tells_the_user_what_to_do(self):
        chemin = _classeur(os.path.join(self.directory, "b.xlsx"),
                           self._bombe(5))
        with self.assertRaises(ImportError_) as pris:
            read_table(chemin)
        message = pris.exception.message
        self.assertIn("Excel", message)
        self.assertNotIn("expat", message.lower())
        self.assertNotIn("ParseError", message)


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestSavingKeepsWhatItDoesNotKnow(unittest.TestCase):
    """Enregistrer les colonnes effaçait la durée de l'écran d'accueil.

    La page invite à éditer ces fichiers au bloc-notes ; elle ne peut pas
    effacer ensuite ce qu'on y a écrit. Les sections « confidentialité »
    et « export » étaient relues puis complétées ; celle du thème était
    remplacée par la seule valeur que l'écran connaît.
    """

    def test_the_theme_section_is_completed_not_replaced(self):
        import inspect
        from hr_analytics.ui import settings

        source = inspect.getsource(settings.SettingsWindow.save)
        for section in ("theme_parameters", "privacy_parameters",
                        "export_parameters"):
            début = source.index(f'"{section}"')
            # Chaque section doit être relue avant d'être réécrite.
            self.assertIn(f'section("{section}")', source,
                          f"{section} est réécrite sans être relue")
            self.assertGreater(début, 0)

    def test_an_unknown_key_survives_a_save(self):
        """Le contrôle qui compte : un réglage que l'écran ignore est
        toujours là après l'enregistrement."""
        from hr_analytics.core.config import (Configuration, load_configuration,
                                            write_configuration)

        directory = tempfile.mkdtemp()
        from hr_analytics.core.config import write_default_configuration
        write_default_configuration(directory)
        chemin = os.path.join(directory, "theme_parameters.json")
        with open(chemin, encoding="utf-8") as handle:
            avant = json.load(handle)
        avant["splash_seconds"] = 7.5
        with open(chemin, "w", encoding="utf-8") as handle:
            json.dump(avant, handle, ensure_ascii=False)

        configuration = load_configuration(directory)
        # Le geste de `save()`, isolé : relire la section, poser le thème.
        thème = dict(configuration.section("theme_parameters"))
        thème["theme"] = "auroral"
        write_configuration(directory, "theme_parameters", thème)

        with open(chemin, encoding="utf-8") as handle:
            après = json.load(handle)
        self.assertEqual(après.get("splash_seconds"), 7.5)
        self.assertEqual(après.get("theme"), "auroral")


@unittest.skipUnless(HAS_TK, "tkinter absent")
class TestTheEmptyOrgTabSpeaks(unittest.TestCase):
    """Une page vide sans un mot ne se distingue pas d'une page en panne."""

    def setUp(self):
        if not os.environ.get("DISPLAY"):
            self.skipTest("aucun affichage")
        import tkinter as tk
        try:
            racine = tk.Tk()
        except tk.TclError:                            # pragma: no cover
            self.skipTest("affichage indisponible")
        racine.destroy()
        self.directory = tempfile.mkdtemp()

    def _fenêtre(self, source):
        import time
        from hr_analytics.ui import app as module
        from hr_analytics.ui.app import Application

        sauvé = module.filedialog.askopenfilename
        module.filedialog.askopenfilename = lambda **k: source
        fenêtre = Application()
        fenêtre.geometry("1200x800+0+0")
        fenêtre.update()
        try:
            fenêtre.choose_file()
            fenêtre.update()
            fenêtre.run_analysis()
            limite = time.time() + 60
            while fenêtre.result is None and time.time() < limite:
                fenêtre.update()
                time.sleep(0.02)
            for _ in range(25):
                fenêtre.update()
                time.sleep(0.01)
            fenêtre.tabbar.select("organigramme")
            for _ in range(20):
                fenêtre.update()
                time.sleep(0.01)
            return fenêtre, fenêtre.org_note.cget("text")
        finally:
            module.filedialog.askopenfilename = sauvé

    def _fichier(self, nom, manager=True):
        import csv
        from tests.support import HEADERS, make_row

        chemin = os.path.join(self.directory, nom)
        with open(chemin, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS)
                            + (["Manager"] if manager else []))
            for rang in range(40):
                ligne = list(make_row(rang, salary=40000 + rang * 200,
                                      gender="F" if rang % 2 else "H"))
                if manager:
                    ligne.append("" if rang == 0 else f"E{(rang % 3):05d}")
                writer.writerow(ligne)
        return chemin

    def test_a_file_without_a_manager_column_says_so(self):
        """Le dessin n'attend pas un clic : il attend une colonne."""
        fenêtre, texte = self._fenêtre(self._fichier("sans.csv", manager=False))
        try:
            self.assertIn("Aucun rattachement", texte)
            self.assertIn("Manager", texte)
        finally:
            fenêtre.destroy()

    def test_a_file_with_one_invites_the_choice(self):
        """La hiérarchie est là ; il manque seulement de dire quelle
        équipe dessiner."""
        fenêtre, texte = self._fenêtre(self._fichier("avec.csv"))
        try:
            self.assertIn("responsable", texte.lower())
            self.assertIn("équipe", texte.lower())
        finally:
            fenêtre.destroy()

    def test_the_page_is_never_blank_and_silent(self):
        for nom, manager in (("a.csv", True), ("b.csv", False)):
            fenêtre, texte = self._fenêtre(self._fichier(nom, manager=manager))
            try:
                self.assertTrue(texte.strip(),
                                f"page vide et muette pour {nom}")
            finally:
                fenêtre.destroy()


if __name__ == "__main__":
    unittest.main()
