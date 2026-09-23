"""Aucune identite dans un document produit, quel que soit le reglage.

Le moteur affirmait cette garantie en commentaire. Elle etait fausse : trois
chemins y menaient — le segment, la dimension declaree a la main, la couleur
du nuage — et le premier se prenait en une option de ligne de commande, sur
la configuration livree, sans rien modifier.

Ces tests ne verifient pas trois correctifs : ils verifient la garantie. Une
quatrieme porte ferait echouer le dernier test sans qu'il faille y penser.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from hr_insight.core import metrics, segmentation
from hr_insight.core.config import Configuration
from hr_insight.core.errors import ConfigError

NOM = "Marchetti"


def population_nominative(taille=40):
    population = build_population([make_row(i) for i in range(taille)])
    for rang, salarie in enumerate(population.employees):
        salarie.last_name = f"{NOM}{rang}"
        salarie.first_name = f"Prenom{rang}"
    return population


class TestThePersonalFieldsAreNamedOnce(unittest.TestCase):

    def test_the_default_list_holds_even_without_configuration(self):
        """Une liste « personal » retiree du fichier ne doit pas desarmer la
        protection : l'omission serait le moyen le plus simple de la lever."""
        donnees = make_config().as_dict()
        donnees["population_mapping"].pop("personal", None)
        champs = segmentation.personal_fields(Configuration(donnees))
        for attendu in ("last_name", "first_name", "birth_date", "employee_id"):
            self.assertIn(attendu, champs)

    def test_a_configuration_may_add_but_not_remove(self):
        donnees = make_config().as_dict()
        donnees["population_mapping"]["personal"] = ["matricule_interne"]
        champs = segmentation.personal_fields(Configuration(donnees))
        self.assertIn("matricule_interne", champs)
        self.assertIn("last_name", champs)


class TestNoIdentityEntersAResult(unittest.TestCase):

    def test_a_personal_field_is_refused_as_a_segment(self):
        config = make_config()
        for champ in ("last_name", "first_name", "employee_id"):
            with self.subTest(champ=champ):
                with self.assertRaises(ConfigError) as leve:
                    segmentation.validate_segments([champ], config)
                self.assertIn("nominatif", str(leve.exception))

    def test_a_collective_field_stays_a_segment(self):
        """Le garde-fou ne doit pas emporter l'usage normal."""
        config = make_config()
        self.assertEqual(segmentation.validate_segments(["grade"], config),
                         ["grade"])

    def test_a_personal_field_is_refused_as_a_declared_dimension(self):
        """La fenetre de parametrage l'ecartait deja ; le fichier, non."""
        donnees = make_config().as_dict()
        donnees["population_mapping"]["dimensions"].append(
            {"field": "last_name", "label": "Nom"})
        with self.assertRaises(ConfigError) as leve:
            segmentation.dimensions(Configuration(donnees))
        self.assertIn("nominatif", str(leve.exception))

    def test_a_personal_field_is_refused_as_the_scatter_colour(self):
        donnees = make_config().as_dict()
        donnees["chart_parameters"]["scatter_color_by"] = "last_name"
        with self.assertRaises(ConfigError) as leve:
            metrics.scatter_dataset(population_nominative(),
                                    Configuration(donnees))
        self.assertIn("nominatif", str(leve.exception))

    def test_a_personal_filter_works_but_never_writes_its_value(self):
        """Filtrer sur un matricule verifie un dossier — c'est une promesse
        du LISEZ-MOI. Ce libelle part dans le manifeste : il retient le
        champ, jamais la valeur."""
        config = make_config()
        filtres = segmentation.build_filters(
            [{"field": "last_name", "operator": "eq", "value": f"{NOM}7"}],
            config)
        libelle = segmentation.describe_filters(filtres, config)
        self.assertNotIn(NOM, libelle)
        self.assertIn("last_name", libelle)
        self.assertIn(segmentation.Filter.HIDDEN_VALUE, libelle)

    def test_a_collective_filter_keeps_its_value(self):
        config = make_config()
        filtres = segmentation.build_filters(
            [{"field": "grade", "operator": "eq", "value": "G5"}], config)
        self.assertIn("G5", segmentation.describe_filters(filtres, config))


class TestTheWholeResultIsSweptForNames(unittest.TestCase):
    """Le filet, plutot que la liste des trous connus."""

    def test_no_surname_survives_anywhere_in_a_full_analysis(self):
        from hr_insight.core import pay_equity

        population = population_nominative()
        config = make_config()
        morceaux = {
            "population": metrics.calculate_population_metrics(population, config),
            "salaire": metrics.calculate_salary_metrics(population, config),
            "nuage": metrics.scatter_dataset(population, config),
            "equite": pay_equity.calculate_pay_equity(population, config),
        }
        for champ in segmentation.dimension_fields(config):
            morceaux[f"segment:{champ}"] = metrics.calculate_segment_metrics(
                population, config, champ)
        for nom, morceau in morceaux.items():
            with self.subTest(morceau=nom):
                self.assertNotIn(NOM, json.dumps(morceau, default=str,
                                                 ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
