"""Tests des restitutions paysage (slides HTML et PDF natif)."""

import datetime as _dt
import os
import re
import tempfile
import unittest
import zlib

from tests.support import REFERENCE_DATE, build_population, make_config, make_row
from tests.test_privacy_and_pipeline import build_source
from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.core.slides import (build_deck, build_summary,
                                                render_slides_html,
                                                write_slides_html, write_slides_pdf)
from compensation_analytics.io.pdf_writer import (Document, encode_text,
                                                  text_width, truncate)


def analysis_payload(directory, **kwargs):
    source = build_source(directory)
    return run_analysis(AnalysisRequest(
        source_path=source, reference_date=REFERENCE_DATE, **kwargs
    )).payload


class TestDeckStructure(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.payload = analysis_payload(self.directory, segments=["business_unit"])

    def test_summary_is_a_single_landscape_page(self):
        summary = build_summary(self.payload)
        self.assertEqual(len(summary), 1)
        kinds = {block.kind for block in summary[0].blocks}
        self.assertIn("kpis", kinds)

    def test_deck_opens_with_a_cover_and_closes_with_methodology(self):
        deck = build_deck(self.payload)
        self.assertEqual(deck[0].kind, "cover")
        self.assertEqual(deck[-1].kind, "closing")
        self.assertIn("Methodologie", deck[-1].title)

    def test_deck_covers_the_expected_sections(self):
        titles = " | ".join(slide.title for slide in build_deck(self.payload))
        for expected in ("Qualite des donnees", "Population", "Remuneration",
                         "Distribution", "Anciennete et remuneration"):
            self.assertIn(expected, titles)

    def test_one_slide_per_segment_dimension(self):
        payload = analysis_payload(self.directory, segments=["business_unit", "grade"])
        titles = [slide.title for slide in build_deck(payload)]
        self.assertIn("Analyse par bu", titles)
        self.assertIn("Analyse par grade", titles)

    def test_masked_population_produces_no_salary_slide(self):
        config = make_config({"privacy_parameters.min_headcount_publish": 50})
        population = build_population([make_row(i) for i in range(6)], config)
        from compensation_analytics.core import metrics
        payload = {
            "title": "Test", "quality": {}, "manifest": {},
            "population": metrics.calculate_population_metrics(population, config),
            "salary": metrics.calculate_salary_metrics(population, config),
            "distribution": metrics.calculate_distribution_metrics(population, config),
            "scatter": metrics.scatter_dataset(population, config),
            "segments": [],
        }
        titles = [slide.title for slide in build_deck(payload)]
        self.assertNotIn("Remuneration", titles)
        self.assertNotIn("Population", titles)


class TestSlidesHtml(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.payload = analysis_payload(self.directory, segments=["business_unit"])
        self.html = render_slides_html(build_deck(self.payload), self.payload)

    def test_no_network_reference(self):
        for pattern in ("http://", "https://", "<script src", "<link ", "@import"):
            self.assertNotIn(pattern, self.html)

    def test_landscape_print_rules(self):
        self.assertIn("@page", self.html)
        self.assertIn("1280px 720px", self.html)
        self.assertIn("page-break-after", self.html)

    def test_no_personal_data(self):
        self.assertNotIn("NOM0", self.html)
        self.assertNotIn("PRENOM0", self.html)

    def test_one_section_per_slide(self):
        deck = build_deck(self.payload)
        self.assertEqual(self.html.count('<section class="slide'), len(deck))


class TestPdfPrimitives(unittest.TestCase):
    def test_text_width_matches_helvetica_metrics(self):
        # "iii" est nettement plus etroit que "WWW" : la table est bien lue.
        self.assertLess(text_width("iii", 10), text_width("WWW", 10))
        self.assertAlmostEqual(text_width(" ", 10), 2.78, places=2)

    def test_truncate_respects_the_available_width(self):
        text = "Un libelle beaucoup trop long pour la colonne"
        result = truncate(text, 9, 60)
        self.assertTrue(result.endswith("..."))
        self.assertLessEqual(text_width(result, 9), 60)

    def test_truncate_leaves_short_text_untouched(self):
        self.assertEqual(truncate("Court", 9, 200), "Court")

    def test_accents_are_preserved_and_typography_is_folded(self):
        # WinAnsi couvre les accents : ils passent tels quels. Seuls les
        # caracteres typographiques hors jeu (apostrophe courbe, tiret cadratin)
        # sont replies vers un equivalent imprimable.
        self.assertEqual(encode_text("l’ancienneté — 5 %"), "l'ancienneté - 5 %")

    def test_characters_outside_winansi_are_replaced(self):
        self.assertEqual(encode_text("中文"), "??")

    def test_document_is_a_valid_pdf(self):
        path = os.path.join(tempfile.mkdtemp(), "t.pdf")
        document = Document()
        for _ in range(3):
            page = document.add_page()
            page.text(50, 500, "Test")
        document.save(path)
        data = open(path, "rb").read()
        self.assertTrue(data.startswith(b"%PDF-"))
        self.assertTrue(data.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"/Count 3", data)


class TestPdfDocument(unittest.TestCase):
    """Le PDF est ecrit octet par octet : sa structure doit etre verifiee."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.payload = analysis_payload(self.directory, segments=["business_unit"])
        self.deck = build_deck(self.payload)
        self.path = write_slides_pdf(
            self.deck, self.payload, os.path.join(self.directory, "deck.pdf")
        )
        self.data = open(self.path, "rb").read()

    def test_cross_reference_table_points_at_real_objects(self):
        start = int(re.search(rb"startxref\s+(\d+)", self.data).group(1))
        self.assertEqual(self.data[start:start + 4], b"xref")
        offsets = re.findall(rb"(\d{10}) 00000 n", self.data[start:])
        self.assertTrue(offsets)
        for offset in offsets:
            position = int(offset)
            self.assertRegex(self.data[position:position + 20], rb"^\d+ 0 obj")

    def test_page_count_matches_the_deck(self):
        self.assertIn(f"/Count {len(self.deck)}".encode(), self.data)

    def test_landscape_media_box(self):
        box = re.search(rb"/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]", self.data)
        self.assertIsNotNone(box)
        self.assertGreater(float(box.group(1)), float(box.group(2)))

    def test_content_streams_are_readable(self):
        streams = []
        for match in re.finditer(rb"(?<!end)stream\r?\n", self.data):
            begin = match.end()
            end = self.data.index(b"\nendstream", begin)
            streams.append(zlib.decompress(self.data[begin:end]).decode("latin-1"))
        self.assertEqual(len(streams), len(self.deck))
        joined = "\n".join(streams)
        self.assertIn("Remuneration", joined)
        self.assertIn("BT", joined)

    def test_no_personal_data_in_the_pdf(self):
        streams = b""
        for match in re.finditer(rb"(?<!end)stream\r?\n", self.data):
            begin = match.end()
            end = self.data.index(b"\nendstream", begin)
            streams += zlib.decompress(self.data[begin:end])
        self.assertNotIn(b"NOM0", streams)
        self.assertNotIn(b"PRENOM0", streams)

    def test_only_base_fonts_are_used(self):
        self.assertIn(b"/BaseFont /Helvetica", self.data)
        self.assertNotIn(b"/FontFile", self.data)  # aucune police embarquee


class TestSummaryOutputs(unittest.TestCase):
    def test_summary_html_and_pdf_are_written(self):
        directory = tempfile.mkdtemp()
        payload = analysis_payload(directory)
        summary = build_summary(payload)
        html = write_slides_html(summary, payload,
                                 os.path.join(directory, "s.html"))
        pdf = write_slides_pdf(summary, payload, os.path.join(directory, "s.pdf"))
        self.assertGreater(os.path.getsize(html), 1000)
        self.assertGreater(os.path.getsize(pdf), 500)
        self.assertIn(b"/Count 1", open(pdf, "rb").read())


if __name__ == "__main__":
    unittest.main()
