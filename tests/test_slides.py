"""Tests des restitutions paysage (slides HTML et PDF natif)."""

import os
import re
import tempfile
import unittest

from tests.support import CONFIG_DIR
import zlib

from tests.support import (REFERENCE_DATE, build_population, make_config,
                           make_row)
from tests.test_privacy_and_pipeline import build_source
from hr_analytics.core.pipeline import AnalysisRequest, run_analysis
from hr_analytics.core.reporting import format_money
from hr_analytics.core.slides import (build_deck, build_summary,
                                                render_slides_html,
                                                write_slides_html, write_slides_pdf)
from hr_analytics.io.pdf_writer import (Document, encode_text,
                                                  text_width, truncate)


def analysis_payload(directory, **kwargs):
    source = build_source(directory)
    return run_analysis(AnalysisRequest(config_dir=CONFIG_DIR, 
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

    def test_deck_opens_with_a_cover(self):
        deck = build_deck(self.payload)
        self.assertEqual(deck[0].kind, "cover")

    def test_the_deck_never_closes_on_a_traceability_page(self):
        """Elle répétait ce que la garde porte déjà — fichier source, date,
        périmètre — et une empreinte que le manifeste écrit à côté des
        documents. Une page de fin qui répète allonge le jeu, rien de
        plus."""
        deck = build_deck(self.payload)
        for diapositive in deck:
            self.assertNotIn("Traçabilité", diapositive.title)
        rendu = render_slides_html(deck, self.payload)
        self.assertNotIn("Empreinte SHA-256", rendu)

    def test_the_cover_never_says_what_the_user_already_knows(self):
        """« traitement local, hors ligne » : l'utilisateur vient de lancer
        l'outil sur son poste. Une garde dit d'où vient l'analyse, pas ce
        que l'outil est."""
        garde = build_deck(self.payload)[0]
        textes = [ligne for bloc in garde.blocks if bloc.kind == "text"
                  for ligne in bloc.payload]
        self.assertFalse([ligne for ligne in textes if "hors ligne" in ligne])
        self.assertTrue([ligne for ligne in textes
                         if ligne.startswith("Fichier source")])

    def test_deck_covers_the_expected_sections(self):
        titles = " | ".join(slide.title for slide in build_deck(self.payload))
        # Le titre du nuage suit les deux axes, qui se parametrent : ecrit
        # en dur, il annoncait « Anciennete et remuneration » quel que soit
        # ce que le dessin montrait.
        for expected in ("Population", "Pyramide des âges",
                         "Pyramide d'ancienneté", "Rémunération",
                         "Distribution", "Salaire de base et ancienneté"):
            self.assertIn(expected, titles)
        # Pas de planche « Qualité des données » : le contrôle se lit à
        # l'écran avant de produire quoi que ce soit, et il est fait quand
        # le document part.
        self.assertNotIn("Qualité des données", titles)

    def test_a_segment_below_the_threshold_is_not_a_row_of_dashes(self):
        """Une ligne masquée n'avait que son effectif et quatre tirets, et
        elle prenait la place d'un segment publiable : la planche s'arrête
        à douze lignes."""
        payload = analysis_payload(self.directory, segments=["business_unit"])
        segment = payload["segments"][0]
        segment["rows"].append({
            "segment": "SegmentMinuscule", "headcount": 2, "masked": True,
            "salary": {}})
        titres = {slide.title: slide for slide in build_deck(payload)}
        planche = titres["Analyse par bu"]
        libelles = [ligne[0] for ligne in planche.blocks[0].payload["rows"]]
        self.assertNotIn("SegmentMinuscule", libelles)

    def test_a_dimension_with_nothing_publishable_opens_no_board(self):
        payload = analysis_payload(self.directory, segments=["business_unit"])
        for row in payload["segments"][0]["rows"]:
            row["masked"] = True
        titres = [slide.title for slide in build_deck(payload)]
        self.assertNotIn("Analyse par bu", titres)

    def test_the_payroll_says_what_it_is_the_sum_of(self):
        """« Masse salariale » tout court laissait croire à un coût complet,
        primes et charges comprises. Le libellé suit le champ analysé, et
        vient du mapping — pas du code."""
        from hr_analytics.core.reporting import payroll_label

        self.assertEqual(payroll_label({"field_label": "Salaire de base"}),
                         "Masse salariale (salaire de base)")
        self.assertEqual(payroll_label({"field_label": "Rémunération totale"}),
                         "Masse salariale (rémunération totale)")
        # Sans libellé déclaré, rien n'est inventé.
        self.assertEqual(payroll_label({}), "Masse salariale")

    def test_one_slide_per_segment_dimension(self):
        payload = analysis_payload(self.directory, segments=["business_unit", "groupe"])
        titles = [slide.title for slide in build_deck(payload)]
        self.assertIn("Analyse par bu", titles)
        self.assertIn("Analyse par groupe", titles)

    def test_a_masked_population_keeps_its_boards_but_no_figure(self):
        """Masquer n'est pas supprimer.

        Les planches disparaissaient entierement : le lecteur d'un document
        ou manquent la population et la remuneration ne peut pas savoir
        s'il manque un chiffre ou s'il n'y en avait pas. Elles restent, sans
        aucune valeur, et portent la raison que le moteur a ecrite.
        """
        config = make_config({"privacy_parameters.min_headcount_publish": 50})
        population = build_population([make_row(i) for i in range(6)], config)
        from hr_analytics.core import metrics
        payload = {
            "title": "Test", "quality": {}, "manifest": {},
            "population": metrics.calculate_population_metrics(population, config),
            "salary": metrics.calculate_salary_metrics(population, config),
            "distribution": metrics.calculate_distribution_metrics(population, config),
            "scatter": metrics.scatter_dataset(population, config),
            "segments": [],
        }
        planches = build_deck(payload)
        titres = [planche.title for planche in planches]
        self.assertIn("Population", titres)
        self.assertIn("Salaire de base", titres)
        for planche in planches:
            if planche.title not in ("Population", "Salaire de base"):
                continue
            # Rien d'autre que du texte : ni indicateur, ni tableau, ni
            # graphique. Aucune valeur masquee ne peut donc fuir.
            self.assertEqual({bloc.kind for bloc in planche.blocks}, {"text"})
            lignes = [ligne for bloc in planche.blocks
                      for ligne in bloc.payload]
            self.assertTrue(any("masqué" in ligne.lower() for ligne in lignes),
                            planche.title)


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
        with open(path, "rb") as handle:
            data = handle.read()
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
        with open(self.path, "rb") as handle:
            self.data = handle.read()

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
        self.assertIn("Rémunération", joined)
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
        with open(pdf, "rb") as handle:
            self.assertIn(b"/Count 1", handle.read())


class TestReadability(unittest.TestCase):
    """Defauts de lecture reperes en regardant les vues produites."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.config = make_config()

    def _segment(self, field_name, rows, overrides=None):
        from hr_analytics.core import metrics
        config = make_config(overrides) if overrides else self.config
        population = build_population(rows, config)
        return metrics.calculate_segment_metrics(population, config, field_name)

    def test_ordinal_segments_follow_their_scale_not_headcount(self):
        # G1 a un effectif plus faible que G2 : un tri par population placerait
        # G2 en tete et rendrait la progression salariale illisible.
        rows = ([make_row(i, groupe="G2", salary=30000) for i in range(20)]
                + [make_row(100 + i, groupe="G1", salary=25000) for i in range(6)]
                + [make_row(200 + i, groupe="G3", salary=40000) for i in range(10)])
        segment = self._segment("groupe", rows)
        self.assertEqual([row["segment"] for row in segment["rows"]],
                         ["G1", "G2", "G3"])

    def test_band_segments_follow_the_configured_order(self):
        rows = ([make_row(i, age=25) for i in range(5)]
                + [make_row(100 + i, age=55) for i in range(20)]
                + [make_row(200 + i, age=35) for i in range(12)])
        labels = [row["segment"] for row in self._segment("age_band", rows)["rows"]]
        self.assertEqual(labels, ["20-29", "30-39", "50-59"])

    def test_non_ordinal_segments_read_alphabetically(self):
        """Devant cinquante-sept établissements, un classement par effectif
        se lit comme un désordre : on cherche un nom, et on parcourt la
        colonne entière."""
        rows = ([make_row(i, business_unit="DACH") for i in range(5)]
                + [make_row(100 + i, business_unit="France") for i in range(20)])
        labels = [row["segment"] for row in self._segment("business_unit", rows)["rows"]]
        self.assertEqual(labels, ["DACH", "France"])

    def test_the_headcount_order_stays_available(self):
        """Les deux ordres répondent à des questions différentes — « lequel
        est-ce ? » et « lequel pèse ? » — et c'est au lecteur de dire
        laquelle il se pose."""
        rows = ([make_row(i, business_unit="DACH") for i in range(5)]
                + [make_row(100 + i, business_unit="France") for i in range(20)])
        segment = self._segment(
            "business_unit", rows,
            overrides={"chart_parameters.segment_order": "effectif_decroissant"})
        self.assertEqual([row["segment"] for row in segment["rows"]],
                         ["France", "DACH"])

    def test_accents_do_not_send_a_segment_to_the_end(self):
        """« Édition » se range entre « Diffusion » et « Expédition », et non
        après « Zone » comme le fait un tri brut sur les points de code."""
        rows = []
        for index, nom in enumerate(("Zone", "Édition", "Diffusion",
                                     "Expédition")):
            rows += [make_row(index * 100 + step, business_unit=nom)
                     for step in range(5)]
        labels = [row["segment"]
                  for row in self._segment("business_unit", rows)["rows"]]
        self.assertEqual(labels, ["Diffusion", "Édition", "Expédition", "Zone"])

class TestResponsiveSlides(unittest.TestCase):
    """La page garde une geometrie fixe mais doit tenir dans un ecran etroit.

    Sans mise a l'echelle, un jeu de slides de 1280 px imposait un defilement
    horizontal en dessous de ~1400 px de fenetre.
    """

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.payload = analysis_payload(self.directory, segments=["business_unit"])
        self.deck = build_deck(self.payload)
        self.html = render_slides_html(self.deck, self.payload)

    def test_each_page_sits_in_an_elastic_frame(self):
        self.assertEqual(self.html.count('<div class="frame">'), len(self.deck))

    def test_page_geometry_stays_fixed(self):
        # C'est ce qui garantit que l'ecran, l'impression et le PDF montrent
        # la meme chose : on met a l'echelle, on ne reagence pas. La hauteur
        # est un minimum et non un plafond : une planche trop pleine
        # s'allonge, elle ne se coupe pas.
        self.assertIn("width:1280px;min-height:720px", self.html)

    def test_nothing_is_ever_clipped(self):
        """Une hauteur fixe et « overflow:hidden » faisaient disparaitre le
        bas des tableaux longs : le lecteur voyait une page propre, sans
        savoir qu'il lui manquait quatre lignes."""
        geometrie = self.html[self.html.index(".slide{"):]
        self.assertNotIn("overflow:hidden", geometrie[:geometrie.index("}")])

    def test_scale_drives_both_the_frame_and_the_page(self):
        self.assertIn("min-height:calc(720px * var(--slide-scale,1))",
                      self.html)
        self.assertIn("transform:scale(var(--slide-scale,1))", self.html)

    def test_scale_is_computed_and_capped_at_one(self):
        self.assertIn("Math.min(1,frame.clientWidth/1280)", self.html)
        self.assertIn("window.addEventListener('resize',fit)", self.html)

    def test_printing_resets_the_scale(self):
        printing = self.html[self.html.index("@media print"):]
        self.assertIn("--slide-scale:1 !important", printing)
        self.assertIn(".frame{width:1280px;min-height:720px", printing)

    def test_behaviour_without_javascript_is_the_previous_one(self):
        # La valeur de repli est 1 : sans JavaScript, la page s'affiche a sa
        # taille reelle plutot que de disparaitre.
        self.assertIn("var(--slide-scale,1)", self.html)


class TestSummaryComposition(unittest.TestCase):
    """La synthese simplifiee tient sur une page et ne porte que ce qui a
    ete demande : effectifs, age et anciennete, les deux pyramides, la
    repartition par CSP, la dispersion de base et sa boite a moustaches.

    Pas de nuage de points : il demande de la hauteur pour que la
    dispersion verticale se lise, et la page n'en a plus. Il garde sa
    propre planche dans la vue detaillee.
    """

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.payload = analysis_payload(self.directory)
        self.summary = build_summary(self.payload)[0]

    def _charts(self):
        return [block.payload["type"] for block in self.summary.blocks
                if block.kind == "chart"]

    def test_the_summary_is_a_single_page(self):
        self.assertEqual(len(build_summary(self.payload)), 1)

    def test_the_two_pyramids_and_the_donut_are_the_charts(self):
        """Pas de boîte à moustaches sous le tableau à trois colonnes : elle
        y redessinerait la seule colonne « Ensemble », que le lecteur vient
        de lire chiffre par chiffre, au prix d'un tiers de la page."""
        self.assertEqual(self._charts(), ["pyramid", "pyramid", "donut"])

    def test_each_column_says_how_many_people_it_counts(self):
        """« 2 041 EUR » chez les femmes et « 1 943 EUR » chez les hommes se
        comparaient sans qu'on sache si l'un porte sur sept cent
        quatre-vingt-huit personnes ou sur douze — et un P10 calculé sur
        douze personnes ne se lit pas comme un P10."""
        tableau = [block for block in self.summary.blocks
                   if block.kind == "table"][0]
        premiere = tableau.payload["rows"][0]
        self.assertEqual(premiere[0], "Effectif")
        bornes = self.payload["pay_equity"]["bounds_by_sex"]
        self.assertIn(str(bornes["female"]["headcount"]),
                      premiere[1].replace("\u202f", "").replace(" ", ""))

    def test_the_dispersion_is_detached_from_what_precedes_it(self):
        """Collée aux pyramides, elle se lisait avec elles comme un seul
        pavé."""
        tableau = [block for block in self.summary.blocks
                   if block.kind == "table"][0]
        self.assertGreater(tableau.space, 0)
        rendu = render_slides_html([self.summary], self.payload)
        self.assertIn("margin-top:", rendu)

    def test_no_scatter_on_the_summary(self):
        self.assertNotIn("scatter", self._charts())

    def test_headcount_age_and_tenure_open_the_page(self):
        bands = [b for b in self.summary.blocks if b.kind == "kpis"]
        self.assertEqual(len(bands), 1)
        labels = [item["label"] for item in bands[0].payload["items"]]
        for attendu in ("Effectif", "Âge médian", "Ancienneté médiane",
                        "Salaire médian"):
            self.assertIn(attendu, labels)
        # Les médianes seules. Une moyenne d'âge posée à côté de sa médiane
        # fait deux chiffres à deux ans l'un de l'autre, et le lecteur
        # arbitre entre les deux au lieu de lire la page. Les moyennes
        # restent dans la vue détaillée, où il y a la place de les comparer.
        self.assertNotIn("Âge moyen", labels)
        self.assertNotIn("Ancienneté moyenne", labels)

    def test_the_csp_split_is_published_as_a_ring(self):
        """En anneau plutôt qu'en tableau : des parts se comparent à l'œil
        quand elles sont des arcs. Le nombre et la part restent écrits
        dans la légende — le dessin range la même information, il n'en
        retire aucune."""
        rendered = render_slides_html([self.summary], self.payload)
        self.assertIn("Répartition par", rendered)
        anneau = [block for block in self.summary.blocks
                  if block.kind == "chart"
                  and block.payload["type"] == "donut"]
        self.assertEqual(len(anneau), 1)
        parts = anneau[0].payload["parts"]
        self.assertTrue(parts)
        for part in parts:
            self.assertIn(str(part["label"]), rendered)
            self.assertIn(f">{int(part['count'])}<", rendered)
        # L'effectif total au centre : c'est ce que le trou de l'anneau
        # sert à porter.
        self.assertIn("salariés</text>", rendered)

    def test_the_basic_dispersion_names_its_four_bounds(self):
        rendered = render_slides_html([self.summary], self.payload)
        for label in ("P10", "Q1 (P25)", "Q3 (P75)", "P90"):
            self.assertIn(label, rendered)

    def test_each_bound_is_read_on_three_columns(self):
        """Un écart de médianes modeste peut cacher deux distributions de
        formes différentes : deux groupes peuvent se croiser à la médiane
        et diverger aux extrêmes. Les trois colonnes le montrent."""
        rendered = render_slides_html([self.summary], self.payload)
        for intitulé in ("Femmes", "Hommes", "Ensemble"):
            self.assertIn(f"<th>{intitulé}</th>", rendered)
        bornes = self.payload["pay_equity"]["bounds_by_sex"]
        for sexe in ("female", "male"):
            self.assertIn(format_money(bornes[sexe]["p10"], "EUR"), rendered)
        # Et l'ensemble reste la colonne de référence : c'est de sa médiane
        # que parle l'écart.
        self.assertIn(format_money(self.payload["salary"]["p10"], "EUR"),
                      rendered)

    def test_a_masked_sex_takes_its_whole_column_away(self):
        """Une colonne « Femmes » remplie de tirets ne dirait pas pourquoi
        elle est vide. Sous le seuil, le tableau reprend sa forme simple
        plutôt que de promettre ce qu'il ne tient pas."""
        payload = dict(self.payload)
        equity = dict(payload["pay_equity"])
        bornes = dict(equity["bounds_by_sex"])
        bornes["female"] = {"headcount": 3, "masked": True,
                            "warning": "Effectif insuffisant."}
        equity["bounds_by_sex"] = bornes
        payload["pay_equity"] = equity
        rendered = render_slides_html(build_summary(payload), payload)
        self.assertNotIn("<th>Femmes</th>", rendered)
        self.assertIn("<th>Valeur</th>", rendered)
        self.assertIn("Écart à la médiane", rendered)

    def test_each_bound_carries_its_gap_to_the_median(self):
        """Le montant seul ne dit pas de combien la borne s'ecarte ; l'ecart
        seul ne dit pas de quel montant on parle. Les deux vont ensemble.

        Le tableau prend toute la largeur dès qu'il porte les deux sexes :
        l'intitulé s'écrit alors en entier."""
        rendered = render_slides_html([self.summary], self.payload)
        self.assertIn("Écart à la médiane", rendered)
        self.assertRegex(rendered, r"[+−]\d+\s*%")
        # La médiane ne s'écarte pas d'elle-même : un tiret au milieu de la
        # colonne se lisait comme une donnée manquante.
        self.assertIn("référence", rendered)

    def test_the_expert_ratios_stay_out_of_the_summary(self):
        rendered = render_slides_html([self.summary], self.payload)
        for label in ("Q3 / Q1", "P90 / P10", "Coefficient de variation"):
            self.assertNotIn(label, rendered)

    def test_a_pyramid_without_any_sex_is_not_drawn(self):
        """Une pyramide dont aucune tranche n'est ventilee par sexe n'est
        pas une pyramide : c'est un cadre vide. Elle se retire."""
        payload = dict(self.payload)
        population = dict(payload["population"])
        population["age_bands"] = [
            dict(row, female=0, male=0) for row in population["age_bands"]]
        payload["population"] = population
        charts = [block.payload["type"]
                  for block in build_summary(payload)[0].blocks
                  if block.kind == "chart"]
        self.assertEqual(charts, ["pyramid", "donut"])

    def test_without_the_two_sexes_the_boxplot_comes_back(self):
        """Sans ventilation par sexe, le tableau est maigre et la forme,
        elle, apprend quelque chose : la boîte se pose à côté."""
        payload = dict(self.payload)
        equity = dict(payload["pay_equity"])
        equity["bounds_by_sex"] = {}
        payload["pay_equity"] = equity
        resume = build_summary(payload)[0]
        charts = [block.payload["type"] for block in resume.blocks
                  if block.kind == "chart"]
        self.assertIn("boxplot", charts)
        largeurs = {block.title: block.width for block in resume.blocks
                    if block.kind in ("table", "chart")}
        self.assertEqual(largeurs["Dispersion des rémunérations"], "half")
        self.assertEqual(largeurs["Boîte à moustaches"], "half")

    def test_the_boxplot_goes_when_the_percentiles_do(self):
        payload = dict(self.payload)
        payload["salary"] = {cle: valeur
                             for cle, valeur in self.payload["salary"].items()
                             if cle not in ("p10", "p25", "p75", "p90")}
        charts = [block.payload["type"]
                  for block in build_summary(payload)[0].blocks
                  if block.kind == "chart"]
        self.assertNotIn("boxplot", charts)

    def test_coverage_is_announced_only_when_incomplete(self):
        """Une couverture partielle change la lecture de tous les montants :
        elle est dite en tete de page. A 100 % elle n'apprend rien."""
        self.assertNotIn("renseignées", self.summary.subtitle)
        partial = dict(self.payload)
        partial["salary"] = dict(self.payload["salary"], coverage=82.0)
        subtitle = build_summary(partial)[0].subtitle
        self.assertIn("82,0 %", subtitle)
        self.assertIn("renseignées", subtitle)


class TestNoRSquaredInDocuments(unittest.TestCase):
    """Ni le R2, ni la droite de tendance ne figurent dans les restitutions.

    Le R2 demandait une explication pour etre lu, et sans cette explication
    il n'apportait rien. La pente chiffree est partie avec lui : annoncee
    seule, sur une population melangeant tous les grades, elle affirmerait
    un lien que rien n'etaye. La droite elle-meme a suivi, pour la meme
    raison — tracee sans son R2, elle affirme une tendance sans permettre
    d'en juger la solidite.

    Le calcul demeure disponible dans `statistics_engine.linear_regression`
    et se reactive par configuration, au meme titre que l'ecart-type : une
    statistique technique, pas un indicateur publie.
    """

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.payload = analysis_payload(self.directory, segments=["business_unit"])

    def test_absent_from_the_detailed_report(self):
        from hr_analytics.core.reporting import render_report
        html = render_report(self.payload)
        self.assertNotIn("R2", html)
        self.assertNotIn("R²", html)
        self.assertNotIn("par année d'ancienneté", html)

    def test_absent_from_the_slides(self):
        html = render_slides_html(build_deck(self.payload), self.payload)
        self.assertNotIn("R2", html)
        self.assertNotIn("R²", html)

    def test_absent_from_the_pdf(self):
        path = write_slides_pdf(build_deck(self.payload), self.payload,
                                os.path.join(self.directory, "d.pdf"))
        with open(path, "rb") as handle:
            data = handle.read()
        streams = b""
        for match in re.finditer(rb"(?<!end)stream\r?\n", data):
            begin = match.end()
            streams += zlib.decompress(data[begin:data.index(b"\nendstream", begin)])
        self.assertNotIn(b"R2", streams)

    def test_the_trend_line_is_no_longer_drawn(self):
        self.assertIsNone(self.payload["scatter"].get("trend"))
        svg = render_slides_html(build_deck(self.payload), self.payload)
        self.assertNotIn("stroke-dasharray", svg)

    def test_the_statistic_remains_available_to_the_engine(self):
        """Retiree de la restitution, la regression reste calculable : on ne
        supprime pas une formule parce qu'on cesse de la publier."""
        from hr_analytics.core import statistics_engine as stats
        trend = stats.linear_regression([1.0, 2.0, 3.0], [10.0, 20.0, 30.0])
        self.assertIn("r_squared", trend)

class TestTheComparisonReadsTheSameEverywhere(unittest.TestCase):
    """Le rapport et les slides doivent porter le meme tableau.

    La mise en forme des lignes etait ecrite deux fois. Une nature de valeur
    ajoutee par le moteur n'aurait ete honoree que d'un cote, et le meme
    fichier aurait produit deux comparaisons differentes selon le support.
    """

    COMPARAISON = {
        "left_label": "France", "right_label": "Hors France",
        "rows": [
            {"indicator": "Effectif", "kind": "int", "left": 120,
             "right": 80, "gap_percent": 50.0},
            {"indicator": "Salaire médian", "kind": "money", "left": 48000.0,
             "right": 45000.0, "gap_percent": 6.7},
            {"indicator": "Ancienneté", "kind": "years", "left": 7.4,
             "right": 5.1, "gap_percent": 45.1},
            {"indicator": "Q3 / Q1", "kind": "ratio", "left": 1.42,
             "right": 1.51, "gap_percent": -6.0},
        ],
    }

    def test_the_two_renderers_format_identically(self):
        from hr_analytics.core.reporting import comparison_rows

        rows = comparison_rows(self.COMPARAISON, "EUR")
        self.assertEqual(rows[0][1], "120")
        self.assertIn("EUR", rows[1][1])
        self.assertEqual(rows[3][1], "1,42")
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(len(row), 4)

    def test_an_unknown_kind_falls_back_without_raising(self):
        """Le moteur peut ajouter une nature : la restitution ne doit pas
        s'arreter dessus, des deux cotes de la meme facon."""
        from hr_analytics.core.reporting import comparison_rows

        inconnu = {"left_label": "A", "right_label": "B", "rows": [
            {"indicator": "Nouveau", "kind": "quelque_chose", "left": 3.14159,
             "right": 2.71828, "gap_percent": 13.5}]}
        rows = comparison_rows(inconnu, "EUR")
        self.assertEqual(rows[0][1], "3,14")
        self.assertEqual(rows[0][2], "2,72")


class TestPayTransparencyReachesTheDocuments(unittest.TestCase):
    """L'analyse d'equite n'existait qu'a l'ecran.

    La directive 2023/970 porte precisement sur la *publication* de ces
    indicateurs : les calculer sans jamais pouvoir les transmettre revenait
    a s'arreter juste avant ce qu'on demande a l'outil.
    """

    def _analysis(self):
        from tests.support import build_population, make_config, make_row
        from hr_analytics.core.pay_equity import calculate_pay_equity
        from hr_analytics.core import metrics

        # Le jeu de test n'a pas de colonne « Poste » : la categorie de la
        # directive est portee par le groupe, ce qui emprunte exactement le
        # meme chemin de calcul.
        config = make_config({"pay_equity_parameters.category_field": "groupe"})
        lignes = ([("G5", "F", 90000)] * 12 + [("G5", "H", 100000)] * 12
                  + [("G7", "F", 45000)] * 12 + [("G7", "H", 50000)] * 12)
        rows = [make_row(index, salary=salaire, gender=sexe, groupe=groupe)
                for index, (groupe, sexe, salaire) in enumerate(lignes)]
        population = build_population(rows, config)
        return {
            "title": "essai",
            "quality": {},
            "population": metrics.calculate_population_metrics(population,
                                                               config),
            "salary": metrics.calculate_salary_metrics(population, config),
            "distribution": metrics.calculate_distribution_metrics(population,
                                                                   config),
            "scatter": metrics.scatter_dataset(population, config),
            "segments": [],
            "pay_equity": calculate_pay_equity(population, config),
            "manifest": {},
        }

    def test_the_report_leaves_the_gaps_to_the_screen(self):
        """Le comparatif se lit sur la page « Écarts F/H », qui le porte en
        entier et demande d'être interrogé — on change d'axe, on filtre un
        poste, on survole. Une section figée n'en gardait que l'écorce."""
        from hr_analytics.core.reporting import render_report

        html = render_report(self._analysis())
        self.assertNotIn("Écarts de rémunération femmes / hommes", html)
        for absent in ("Écart global", "Effet de structure",
                       "Répartition par quartile"):
            self.assertNotIn(absent, html, absent)

    def test_the_deck_leaves_them_too(self):
        from hr_analytics.core.slides import build_deck

        titres = [slide.title for slide in build_deck(self._analysis())]
        self.assertNotIn("Écarts femmes / hommes", titres)
        self.assertFalse([t for t in titres if t.startswith("Écart par")],
                         titres)

    def test_a_masked_category_is_never_detailed_in_a_document(self):
        """Un document circule : une categorie sous le seuil n'y entre pas
        plus que dans l'interface."""
        from hr_analytics.core.reporting import render_report

        analysis = self._analysis()
        analysis["pay_equity"]["categories"].append({
            "category": "CategorieMinuscule", "published": False,
            "female_count": 2, "male_count": 1, "mean_gap": None,
            "median_gap": None, "female_median": 91000.0,
            "male_median": 99000.0, "at_stake": None,
            "above_threshold": False,
        })
        html = render_report(analysis)
        # La catégorie ne tient plus une ligne de « masqué » répété : elle
        # ne paraît pas du tout. Ce qui compte n'a pas change — aucun de ses
        # montants ne sort.
        self.assertNotIn("CategorieMinuscule", html)
        self.assertNotIn("91 000", html)
        self.assertNotIn("99 000", html)


if __name__ == "__main__":
    unittest.main()


class TestAnAxisKeptOutOfTheDocuments(unittest.TestCase):
    """La restitution et les slides reçoivent le résultat tel que
    `exported_payload` le rend : sans les segments des axes tenus hors des
    documents, et avec tout le reste."""

    def setUp(self):
        import json
        import shutil

        from tests.support import write_test_configuration

        self.directory = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.directory, "config")
        write_test_configuration(self.config_dir)
        chemin = os.path.join(self.config_dir, "export_parameters.json")
        with open(chemin, encoding="utf-8") as handle:
            données = json.load(handle)
        données["excluded_dimensions"] = ["groupe"]
        with open(chemin, "w", encoding="utf-8") as handle:
            json.dump(données, handle, ensure_ascii=False)
        result = run_analysis(AnalysisRequest(
            config_dir=self.config_dir, source_path=build_source(self.directory),
            reference_date=REFERENCE_DATE))
        from hr_analytics.core.export import exported_payload

        self.entier = result.payload
        self.payload = exported_payload(result.payload, result.config)

    def test_the_deck_has_no_slide_for_it(self):
        titres = [slide.title for slide in build_deck(self.payload)]
        self.assertFalse(any("groupe" in t.lower() for t in titres), titres)
        self.assertTrue(any("bu" in t.lower() for t in titres), titres)

    def test_the_report_has_no_section_for_it(self):
        from hr_analytics.core.reporting import write_report

        chemin = write_report(self.payload,
                              os.path.join(self.directory, "r.html"))
        with open(chemin, encoding="utf-8") as handle:
            html = handle.read()
        self.assertNotIn("G5", html)
        self.assertIn("DACH", html)

    def test_the_whole_result_still_carries_it(self):
        """Le témoin : sans le filtre, la planche existe."""
        titres = [slide.title for slide in build_deck(self.entier)]
        self.assertTrue(any("groupe" in t.lower() for t in titres), titres)
