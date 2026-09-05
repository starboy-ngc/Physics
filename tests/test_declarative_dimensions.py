"""Une dimension metier doit s'ajouter par configuration, sans code.

C'est la condition pour que les modules a venir (equipe, manager, direction)
se branchent sans reecrire le coeur.
"""

import datetime as _dt
import os
import tempfile
import unittest

from compensation_analytics.core.config import Configuration, load_configuration
from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.core.reporting import render_report
from compensation_analytics.core.segmentation import (apply_filters, build_filters,
                                                      dimension_fields, split_by)
from compensation_analytics.io.xlsx_writer import write_workbook

REFERENCE = _dt.date(2026, 1, 1)
HEADERS = ["Matricule", "BU", "Métier", "Equipe", "Salaire de base", "Date d'entrée"]
TEAMS = ["Team Alpha", "Team Beta", "Team Gamma"]


def make_source(directory):
    rows = [
        [f"E{i:04d}", "France", "Developpeur", TEAMS[i % 3],
         40000 + i * 300, _dt.date(2018, 1, 1)]
        for i in range(45)
    ]
    path = os.path.join(directory, "population.xlsx")
    write_workbook(path, [("Population", [HEADERS] + rows)])
    return path


def config_with_team():
    """Configuration declarant une dimension absente du modele normalise."""
    data = load_configuration().as_dict()
    data["population_mapping"]["fields"]["team"] = ["Equipe", "Team"]
    data["population_mapping"]["dimensions"].append(
        {"field": "team", "label": "Equipe"}
    )
    return Configuration(data)


class TestDeclarativeDimension(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source = make_source(self.directory)
        self.config = config_with_team()

    def _population(self):
        from compensation_analytics.core.pipeline import load_population
        population, _, _ = load_population(self.source, self.config,
                                           reference_date=REFERENCE)
        return population

    def test_declared_dimension_is_recognised(self):
        self.assertIn("team", dimension_fields(self.config))

    def test_values_are_read_into_the_normalised_model(self):
        population = self._population()
        self.assertEqual(population.employees[0].value("team"), "Team Alpha")

    def test_dimension_is_filterable(self):
        population = self._population()
        filters = build_filters(
            [{"field": "team", "operator": "eq", "value": "Team Alpha"}], self.config
        )
        self.assertEqual(len(apply_filters(population, filters)), 15)

    def test_dimension_is_segmentable(self):
        groups = split_by(self._population(), "team")
        self.assertEqual(sorted(groups), TEAMS)

    def test_full_analysis_with_the_declared_dimension(self):
        directory = os.path.join(self.directory, "config")
        os.makedirs(directory, exist_ok=True)
        import json
        with open(os.path.join(directory, "population_mapping.json"),
                  "w", encoding="utf-8") as handle:
            json.dump({
                "fields": {"team": ["Equipe"]},
                "dimensions": self.config.get("population_mapping.dimensions"),
            }, handle, ensure_ascii=False)
        result = run_analysis(AnalysisRequest(
            source_path=self.source, config_dir=directory,
            reference_date=REFERENCE, segments=["team"],
        ))
        segment = result.payload["segments"][0]
        self.assertEqual(segment["field"], "team")
        self.assertEqual(segment["label"], "Equipe")
        self.assertEqual({row["segment"] for row in segment["rows"]}, set(TEAMS))
        html = render_report(result.payload)
        self.assertIn("Equipe", html)
        self.assertIn("Team Alpha", html)

    def test_unknown_dimension_still_rejected(self):
        from compensation_analytics.core.errors import ConfigError
        with self.assertRaises(ConfigError):
            build_filters([{"field": "direction", "operator": "eq", "value": "X"}],
                          self.config)


if __name__ == "__main__":
    unittest.main()


class TestJobTitleIsAvailable(unittest.TestCase):
    """Le poste est l'axe de comparaison le plus courant en remuneration :
    il doit etre livre reconnu, filtrable et analysable."""

    def setUp(self):
        from compensation_analytics.core.config import load_configuration
        self.config = load_configuration()

    def test_the_column_is_recognised_under_its_usual_names(self):
        from compensation_analytics.core.mapping import resolve_mapping
        for header in ("Poste", "poste", "Intitulé de poste", "Job title",
                       "Position"):
            mapping = resolve_mapping(["Matricule", "Salaire de base", header],
                                      self.config)
            self.assertIn("job_title", mapping.field_to_index, header)
            self.assertEqual(mapping.unknown_columns, [], header)

    def test_it_is_both_a_filter_and_an_axis(self):
        from compensation_analytics.core.segmentation import (filter_fields,
                                                              segment_fields)
        self.assertIn("job_title", filter_fields(self.config))
        self.assertIn("job_title", segment_fields(self.config))

    def test_it_is_distinct_from_the_occupation(self):
        """"Metier" et "Poste" sont deux notions : le second precise le
        premier d'un niveau de responsabilite."""
        from compensation_analytics.core.segmentation import dimension_label
        self.assertEqual(dimension_label(self.config, "job"), "Métier")
        self.assertEqual(dimension_label(self.config, "job_title"), "Poste")


class TestTheSamplePopulationCarriesPositions(unittest.TestCase):
    def test_positions_stay_under_the_filter_limit(self):
        """Au-dela de la limite, le poste disparaitrait des listes
        deroulantes sans que rien ne le signale."""
        from tools.generate_sample_population import (HEADERS, build_rows,
                                                      column)
        from compensation_analytics.core.config import load_configuration
        from compensation_analytics.core.segmentation import max_filter_values
        import datetime

        rows = build_rows(2000, 20260905, datetime.date(2026, 1, 1),
                          defects=False)
        positions = {row[column("Poste")] for row in rows}
        self.assertLessEqual(len(positions), max_filter_values(
            load_configuration()))
        self.assertGreater(len(positions), 20, "trop peu de postes pour "
                                               "que la comparaison ait du sens")

    def test_a_position_refines_its_occupation(self):
        from tools.generate_sample_population import (build_rows, column)
        import datetime

        rows = build_rows(400, 1, datetime.date(2026, 1, 1), defects=False)
        for row in rows:
            self.assertTrue(row[column("Poste")].startswith(row[column("Métier")]))

    def test_the_defects_still_target_the_intended_columns(self):
        """Les defauts visaient des indices ecrits en dur : inserer une
        colonne les decalait, et le generateur corrompait la mauvaise."""
        from tools.generate_sample_population import build_rows, column
        import datetime

        rows = build_rows(200, 7, datetime.date(2026, 1, 1), defects=True)
        salary = column("Salaire de base")
        self.assertEqual(rows[3][salary], "")
        self.assertEqual(rows[5][salary], -1500)
        self.assertEqual(rows[11][salary], 950000)
        self.assertGreater(rows[7][column("Date de naissance")],
                           datetime.date(2026, 1, 1))
        self.assertLess(rows[9][column("Date de sortie")],
                        rows[9][column("Date d'entrée")])
