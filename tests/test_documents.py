"""Les documents produits, dans toutes leurs configurations.

Trois sections ne paraissent que sur demande — les situations atypiques, la
comparaison de deux populations, la droite de tendance — et aucune n'etait
jamais rendue par les tests. Une section qui ne s'affiche que chez
l'utilisateur est une section qui casse chez l'utilisateur.

Le SVG et le PDF sont relus comme un lecteur le ferait : un document qui
n'ouvre pas ne vaut pas mieux qu'un document absent.

Aucune donnee RH reelle.
"""

import csv
import os
import re
import sys
import tempfile
import unittest
from xml.etree import ElementTree

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, make_row
from compensation_analytics.core import slides as _slides
from compensation_analytics.core.config import write_default_configuration
from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.core.reporting import render_report
from compensation_analytics.core.segmentation import Filter


class DocumentCase(unittest.TestCase):
    """Une analyse riche : atypiques, comparaison, tendance."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "p.csv")
        with open(cls.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste"])
            for index in range(60):
                writer.writerow(list(make_row(
                    index, salary=38000 + index * 300,
                    business_unit=["France", "Iberia"][index % 2],
                    grade=f"G{3 + index % 4}", tenure=index % 25,
                    gender="F" if index % 2 else "H"))
                    + [["Comptable", "Technicien"][(index // 2) % 2]])
            # Deux situations tres au-dessus : le critere interquartile les
            # repere, et la section « atypiques » parait enfin.
            for index in (900, 901):
                writer.writerow(list(make_row(index, salary=400000))
                                + ["Comptable"])
        cls.config_dir = os.path.join(cls.directory, "config")
        write_default_configuration(cls.config_dir)
        import json

        target = os.path.join(cls.config_dir, "chart_parameters.json")
        with open(target, encoding="utf-8") as handle:
            settings = json.load(handle)
        settings["show_trend_line"] = True
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False)
        cls.result = run_analysis(AnalysisRequest(
            source_path=cls.source, config_dir=cls.config_dir,
            filters=[Filter("business_unit", "eq", "France")],
            comparison_filters=[Filter("business_unit", "eq", "Iberia")],
            comparison_label="Espagne"))
        cls.payload = cls.result.payload
        cls.report = render_report(cls.payload)
        cls.deck = _slides.build_deck(cls.payload)
        cls.summary = _slides.build_summary(cls.payload)


class TestTheAnalysisIsRichEnough(DocumentCase):
    """Sans quoi les tests suivants ne prouveraient rien."""

    def test_there_are_outliers(self):
        self.assertTrue(self.payload["distribution"]["outliers"])

    def test_there_is_a_comparison(self):
        self.assertIn("comparison", self.payload)

    def test_there_is_a_trend_line(self):
        self.assertIsNotNone(self.payload["scatter"].get("trend"))


class TestReport(DocumentCase):
    def test_the_outlier_section_names_no_one(self):
        """Elle designe des salaries : seule la reference anonyme y entre."""
        self.assertIn("Position", self.report)
        matricules = {employee.employee_id
                      for employee in self.result.filtered}
        for matricule in list(matricules)[:20]:
            self.assertNotIn(f">{matricule}<", self.report)

    def test_the_outlier_section_says_it_is_statistical(self):
        """« Repere par un critere statistique, pas par un jugement RH » :
        c'est ce qui empeche de lire ce tableau comme une liste de fautifs."""
        self.assertIn("critère statistique", self.report)

    def test_the_comparison_section_carries_both_labels(self):
        self.assertIn("Comparaison de populations", self.report)
        self.assertIn("Espagne", self.report)

    def test_the_trend_line_is_drawn(self):
        self.assertIn("stroke-dasharray", self.report)

    def test_every_svg_is_well_formed(self):
        """Un SVG casse ne fait pas d'erreur : il ne s'affiche pas."""
        drawings = re.findall(r"<svg.*?</svg>", self.report, re.S)
        self.assertGreaterEqual(len(drawings), 2)
        for drawing in drawings:
            ElementTree.fromstring(drawing)

    def test_the_document_reaches_nothing_outside_itself(self):
        """Il porte un script — une bulle au survol —, et c'est tres bien :
        il est local et n'appelle rien. Ce qu'il ne doit jamais faire, c'est
        aller chercher quoi que ce soit ailleurs. Un rapport RH ouvert hors
        ligne doit s'afficher entier, et n'annoncer sa lecture a personne."""
        for pattern in ("<img", "src=", "http://", "https://", "@import",
                        "fetch(", "XMLHttpRequest", "WebSocket", "import(",
                        "navigator.send"):
            self.assertNotIn(pattern, self.report, pattern)

    def test_the_scope_is_stated(self):
        """« 30 salaries » se lit tout autrement selon le perimetre."""
        self.assertIn("France", self.report)


class TestSlides(DocumentCase):
    def test_the_deck_has_an_outlier_slide(self):
        titles = [slide.title for slide in self.deck]
        self.assertTrue(any("atypique" in title.lower() for title in titles),
                        titles)

    def test_the_deck_has_a_comparison_slide(self):
        titles = [slide.title for slide in self.deck]
        self.assertIn("Comparaison de populations", titles)

    def test_the_summary_stays_short(self):
        """La fiche standard est faite pour etre lue en entier."""
        self.assertLessEqual(len(self.summary), 4)
        self.assertLess(len(self.summary), len(self.deck))

    def test_every_slide_has_a_title(self):
        for slide in self.deck + self.summary:
            self.assertTrue(slide.title.strip())

    def test_the_html_renders_every_slide(self):
        from compensation_analytics.core.slides import _html_escape

        html = _slides.render_slides_html(self.deck, self.payload)
        for slide in self.deck:
            self.assertIn(_html_escape(slide.title), html)

    def test_the_html_reaches_nothing_outside_itself(self):
        html = _slides.render_slides_html(self.deck, self.payload)
        for pattern in ("<img", "src=", "http://", "https://", "@import",
                        "fetch(", "XMLHttpRequest", "WebSocket", "import(",
                        "navigator.send"):
            self.assertNotIn(pattern, html, pattern)


class TestPdf(DocumentCase):
    def pdf(self, slides, name):
        path = os.path.join(self.directory, name)
        _slides.write_slides_pdf(slides, self.payload, path)
        with open(path, "rb") as handle:
            return handle.read()

    def test_the_deck_pdf_opens(self):
        raw = self.pdf(self.deck, "deck.pdf")
        self.assertTrue(raw.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", raw[-32:])

    def test_it_has_one_page_per_slide(self):
        raw = self.pdf(self.deck, "pages.pdf")
        self.assertEqual(len(re.findall(rb"/Type\s*/Page[^s]", raw)),
                         len(self.deck))
        self.assertEqual(int(re.search(rb"/Count\s+(\d+)", raw).group(1)),
                         len(self.deck))

    def test_the_cross_reference_table_matches_the_objects(self):
        """C'est ce qu'un lecteur PDF verifie en premier : une table
        decalee d'un octet et le fichier est declare corrompu."""
        raw = self.pdf(self.deck, "xref.pdf")
        start = int(re.search(rb"startxref\s+(\d+)", raw).group(1))
        self.assertEqual(raw[start:start + 4], b"xref")
        declared = int(re.search(rb"xref\s+0\s+(\d+)", raw[start:]).group(1))
        self.assertEqual(raw.count(b" obj"), declared - 1)

    def test_every_object_offset_points_at_its_object(self):
        raw = self.pdf(self.deck, "offsets.pdf")
        start = int(re.search(rb"startxref\s+(\d+)", raw).group(1))
        table = raw[start:].split(b"\n")
        for line in table[2:]:
            found = re.match(rb"^(\d{10}) (\d{5}) n", line)
            if not found:
                continue
            offset = int(found.group(1))
            self.assertRegex(raw[offset:offset + 20], rb"^\d+ 0 obj")

    def test_the_summary_pdf_opens_too(self):
        raw = self.pdf(self.summary, "resume.pdf")
        self.assertTrue(raw.startswith(b"%PDF-"))
        self.assertGreater(len(raw), 1000)

    def test_an_accented_label_survives(self):
        """« Ancienneté », « Rémunération » : un encodage rate les remplace
        par des carres, et le document part quand meme."""
        raw = self.pdf(self.summary, "accents.pdf")
        self.assertNotIn(b"\xef\xbf\xbd", raw)


class TestMaskedDocuments(unittest.TestCase):
    """Sous le seuil, les documents doivent rester lisibles et vides."""

    @classmethod
    def setUpClass(cls):
        directory = tempfile.mkdtemp()
        source = os.path.join(directory, "petit.csv")
        with open(source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(HEADERS)
            for index in range(3):
                writer.writerow(list(make_row(index, salary=40000 + index)))
        cls.directory = directory
        cls.result = run_analysis(AnalysisRequest(source_path=source))

    def test_the_report_is_produced_and_says_why_it_is_empty(self):
        report = render_report(self.result.payload)
        self.assertIn("<html", report.lower())
        self.assertIn("effectif", report.lower())

    def test_no_figure_slips_through(self):
        report = render_report(self.result.payload)
        self.assertNotIn("40 000", report)

    def test_the_slides_are_produced_all_the_same(self):
        deck = _slides.build_deck(self.result.payload)
        self.assertTrue(deck)
        path = os.path.join(self.directory, "petit.pdf")
        _slides.write_slides_pdf(deck, self.result.payload, path)
        with open(path, "rb") as handle:
            self.assertTrue(handle.read().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
