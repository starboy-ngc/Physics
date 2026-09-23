"""Aucun indicateur publie sans le moyen de le refaire.

Le classeur d'export a une raison d'etre precise : permettre a une equipe
C&B de reprendre chaque chiffre et d'en retrouver la valeur. Un agregat
ecrit sans sa formule demande de croire l'outil sur parole — et c'est
exactement ce que ce classeur existe pour ne pas demander.

Ce test ne surveille pas une liste d'indicateurs connus : il enumere ce que
l'analyse publie, et echoue sur tout nombre qu'aucune formule du classeur
ne reproduit. Un indicateur ajoute demain sans sa formule le fera echouer
sans qu'il faille y penser.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import build_population, make_config, make_row
from tests.support_spreadsheet import Workbook, FormulaError
from hr_insight.core import metrics, pay_equity
from hr_insight.core.export import build_sheets
from hr_insight.io.xlsx_writer import Formula


#: Valeurs qui ne sont pas des indicateurs mais des reglages recopies dans
#: le resultat. Elles n'ont pas de formule parce qu'elles n'ont pas de
#: calcul : elles viennent du fichier de configuration.
REGLAGES = {"threshold"}


def _population(taille=60):
    population = build_population([make_row(rang) for rang in range(taille)])
    for rang, salarie in enumerate(population.employees):
        salarie.gender = "F" if rang % 2 else "H"
        salarie.fte = 0.8 if (rang % 2 and rang % 3) else 1.0
        salarie.base_salary = 40000.0 + rang * 250
        # Une part variable nulle pour quelques-uns : zero est une valeur,
        # et un masque qui l'ecarterait fausserait la moyenne.
        salarie.variable_pay = 0.0 if rang % 7 == 0 else 1500.0 + rang * 10
    return population


class IndicatorCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        donnees = make_config().as_dict()
        donnees["export_parameters"]["include_individual_data"] = True
        from hr_insight.core.config import Configuration

        cls.config = Configuration(donnees)
        cls.population = _population()
        cls.payload = {
            "population": metrics.calculate_population_metrics(
                cls.population, cls.config),
            "salary": metrics.calculate_salary_metrics(
                cls.population, cls.config),
            "distribution": metrics.calculate_distribution_metrics(
                cls.population, cls.config),
            "pay_equity": pay_equity.calculate_pay_equity(
                cls.population, cls.config),
            "manifest": {},
            "quality": {},
            "segments": [],
        }
        cls.sheets = build_sheets(cls.payload, cls.population, cls.config)

    def _formules(self):
        for nom, lignes in self.sheets:
            for numero, ligne in enumerate(lignes, start=1):
                for colonne, cellule in enumerate(ligne, start=1):
                    if isinstance(cellule, Formula):
                        yield nom, numero, colonne, cellule


class TestEveryPublishedNumberHasAFormula(IndicatorCase):

    def _publies(self):
        """Les indicateurs numeriques que l'analyse publie."""
        blocs = {
            "population": self.payload["population"],
            "salary": self.payload["salary"],
            "salary.full_time": self.payload["salary"].get("full_time") or {},
            "salary.dispersion": (self.payload["salary"].get("dispersion")
                                  or {}),
            "pay_equity": self.payload["pay_equity"],
        }
        for bloc in ("pay", "variable", "full_time"):
            blocs[f"pay_equity.{bloc}"] = (
                self.payload["pay_equity"].get(bloc) or {})
        for nom, contenu in blocs.items():
            for cle, valeur in sorted(contenu.items()):
                if cle in REGLAGES or isinstance(valeur, bool) or \
                        not isinstance(valeur, (int, float)):
                    continue
                yield nom, cle, float(valeur)

    def test_no_indicator_is_published_without_its_formula(self):
        refaites = [float(cellule.value) for _n, _l, _c, cellule
                    in self._formules()
                    if isinstance(cellule.value, (int, float))]
        orphelins = []
        for nom, cle, valeur in self._publies():
            if not any(abs(valeur - refaite) <= max(1e-6, abs(valeur) * 1e-9)
                       for refaite in refaites):
                orphelins.append(f"{nom}.{cle} = {valeur}")
        self.assertEqual(
            orphelins, [],
            "Ces indicateurs sont publiés sans qu'aucune formule du "
            "classeur ne les reproduise : ils demandent de croire l'outil "
            "sur parole.")


class TestEveryFormulaGivesBackItsValue(IndicatorCase):
    """Porter une formule ne suffit pas : elle doit rendre le chiffre."""

    def test_the_workbook_recomputes_what_it_claims(self):
        classeur = Workbook(self.sheets)
        desaccords = []
        for nom, numero, colonne, cellule in self._formules():
            if cellule.value is None:
                continue
            try:
                obtenu = classeur.evaluate(cellule.expression, nom)
            except FormulaError as erreur:
                desaccords.append(f"{nom} L{numero}C{colonne} : {erreur}")
                continue
            if isinstance(obtenu, str):
                if obtenu == "":
                    continue
                desaccords.append(f"{nom} L{numero}C{colonne} : « {obtenu} »")
                continue
            attendu = float(cellule.value)
            if abs(float(obtenu) - attendu) > max(1e-6, abs(attendu) * 1e-9):
                desaccords.append(
                    f"{nom} L{numero}C{colonne} : {attendu} ≠ {obtenu} "
                    f"[{cellule.expression[:60]}]")
        self.assertEqual(desaccords, [])


class TestTheArrayFormulasAreMarkedAsSuch(IndicatorCase):
    """« MEDIAN(IF(...)) » ecrite en formule ordinaire ne rend pas une
    erreur : elle rend un autre nombre, qui depend de la ligne ou elle se
    trouve. Verifie sous LibreOffice : 15 ou 0 au lieu de 5, selon la
    ligne. Un chiffre faux sur la feuille qui sert a verifier est pire
    qu'une absence de feuille."""

    def test_no_matrix_formula_is_written_as_an_ordinary_one(self):
        from hr_insight.core.formulas import needs_array

        manquantes = [
            f"{nom} L{numero}C{colonne} : {cellule.expression[:50]}"
            for nom, numero, colonne, cellule in self._formules()
            if needs_array(cellule.expression) and not cellule.array]
        self.assertEqual(manquantes, [])


if __name__ == "__main__":
    unittest.main()
