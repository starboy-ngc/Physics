"""Le classeur de contrôle : le fichier importé, et chaque chiffre refait.

Un classeur d'agregats demande de croire l'outil sur parole. Celui-ci ne le
demande plus : il emporte le fichier tel qu'il a ete lu, les salaries
retenus, et une formule par chiffre publie. La promesse est verifiable, donc
elle se verifie — non en relisant le texte des formules, mais en les
executant sur les onglets du classeur (`tests/support_spreadsheet.py`).

C'est ce test qui a trouve le defaut du critere « <2 ans » : une tranche
d'anciennete dont le libelle commence par un signe est lue par COUNTIFS
comme une comparaison, et le tableur comptait trois cent vingt-sept
salaries la ou l'outil en voyait quarante-quatre.

Aucune donnee RH reelle.
"""

import csv
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, make_row
from tests.support_spreadsheet import Workbook
from compensation_analytics.core.config import (Configuration,
                                                write_default_configuration)
from compensation_analytics.core.export import build_sheets
from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.io.xlsx_writer import Formula


class ControlCase(unittest.TestCase):
    """Une analyse complete, exportee avec son dossier de verification."""

    ROWS = 90

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        cls.source = os.path.join(cls.directory, "population.csv")
        with open(cls.source, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(list(HEADERS) + ["Poste"])
            for index in range(cls.ROWS):
                writer.writerow(list(make_row(
                    index, salary=30000 + (index % 30) * 900,
                    business_unit=["France", "Iberia"][index % 2],
                    grade=f"G{3 + index % 3}",
                    gender="F" if index % 2 else "H",
                    age=25 + index % 35,
                    # Des anciennetes etalees : les tranches « <2 ans » et
                    # « >10 ans » doivent etre peuplees, ce sont elles dont
                    # le libelle piege un critere de tableur.
                    tenure=(index % 18) / 1.4))
                    + [["Comptable", "Technicien", "Ingénieur"][index % 3]])
        cls.config_dir = os.path.join(cls.directory, "config")
        write_default_configuration(cls.config_dir)
        cls.result = run_analysis(AnalysisRequest(
            source_path=cls.source, config_dir=cls.config_dir))

    def sheets(self, individual=True, source=True, overrides=None):
        data = self.result.config.as_dict()
        data["export_parameters"]["include_individual_data"] = individual
        data["export_parameters"]["include_source_file"] = source
        for path, value in (overrides or {}).items():
            section, key = path.split(".")
            data[section][key] = value
        return build_sheets(self.result.payload, self.result.filtered,
                            Configuration(data), table=self.result.table,
                            mapping=self.result.mapping)

    def named(self, sheets):
        return {name: rows for name, rows in sheets}


class TestEveryFormulaHoldsUp(ControlCase):
    """Toutes les formules du classeur, executees sur ses propres onglets."""

    def setUp(self):
        self.book = self.sheets()
        self.tableur = Workbook(self.book)

    def _verdicts(self):
        for name, rows in self.book:
            for r, ligne in enumerate(rows, start=1):
                for c, cellule in enumerate(ligne):
                    if not isinstance(cellule, Formula):
                        continue
                    yield name, r, c, cellule

    def test_the_workbook_really_carries_its_formulas(self):
        self.assertGreater(sum(1 for _ in self._verdicts()), 500)

    def test_every_formula_returns_what_the_tool_wrote(self):
        """La verification qui porte tout le reste : chaque formule,
        executee sur les donnees du classeur, doit rendre la valeur que
        l'outil a calculee."""
        ecarts = []
        for name, row, column, cellule in self._verdicts():
            if cellule.value is None:
                continue
            obtenu = self.tableur.evaluate(cellule.expression, name)
            attendu = float(cellule.value)
            if abs(float(obtenu) - attendu) > max(1e-6, abs(attendu) * 1e-9):
                ecarts.append((name, row, column, attendu, obtenu,
                               cellule.expression))
        self.assertEqual(ecarts[:4], [], f"{len(ecarts)} formules en écart")

    def test_the_gap_columns_are_all_zero(self):
        """La colonne « Écart » est celle qu'un lecteur regarde en premier :
        elle doit valoir zero partout, y compris apres recalcul."""
        for name in ("Contrôle", "Contrôle segments",
                     "Contrôle Pay Transparency"):
            rows = self.named(self.book)[name]
            colonne = rows[0].index("Écart")
            for index, ligne in enumerate(rows[1:], start=2):
                if len(ligne) <= colonne or not isinstance(ligne[colonne],
                                                           Formula):
                    continue
                obtenu = self.tableur.evaluate(ligne[colonne].expression, name)
                self.assertAlmostEqual(float(obtenu), 0.0, places=6,
                                       msg=f"{name} ligne {index}")

    def test_a_band_named_with_a_sign_is_counted_as_text(self):
        """« <2 ans » ne doit pas etre lu comme « moins de 2 ».

        Le defaut etait silencieux : le classeur annoncait un effectif faux
        et l'ecart passait pour une erreur de l'outil.
        """
        rows = self.named(self.book)["Contrôle"]
        lignes = [ligne for ligne in rows
                  if ligne and str(ligne[0]).startswith("<2 ans — effectif")]
        self.assertTrue(lignes, "la tranche « <2 ans » doit être peuplée")
        formule = lignes[0][2]
        self.assertNotIn('"<2 ans"', formule.expression.replace('="<2 ans"',
                                                                ""))
        self.assertEqual(
            float(self.tableur.evaluate(formule.expression, "Contrôle")),
            float(lignes[0][1]))


class TestTheImportedFileTravelsWithIt(ControlCase):

    def test_the_sheet_repeats_the_file_line_for_line(self):
        sheets = self.named(self.sheets())
        source = sheets["Fichier importé"]
        self.assertEqual(list(source[0]), list(self.result.table.headers))
        self.assertEqual(len(source), self.result.table.row_count + 1)
        self.assertEqual(list(source[1]), list(self.result.table.rows[0]))

    def test_a_line_number_leads_back_to_the_imported_line(self):
        """La ligne 7 de l'onglet est la ligne 7 du fichier : c'est ce qui
        permet de remonter d'un salarie a sa ligne d'origine."""
        sheets = self.named(self.sheets())
        source = sheets["Fichier importé"]
        individual = sheets["Données individuelles"]
        colonne = individual[0].index("Ligne source")
        for ligne in individual[1:4]:
            numero = ligne[colonne]
            attendu = source[numero - 1]
            self.assertEqual(str(attendu[0]),
                             str(self.result.table.rows[numero - 2][0]))

    def test_the_columns_read_are_named_with_their_letter(self):
        sheets = self.named(self.sheets())
        rows = sheets["Colonnes lues"]
        champs = {ligne[0]: ligne for ligne in rows[1:] if ligne}
        self.assertIn("base_salary", champs)
        self.assertEqual(champs["base_salary"][1],
                         self.result.mapping.field_to_column["base_salary"])
        self.assertTrue(champs["base_salary"][2].isalpha())

    def test_a_file_too_large_is_named_instead_of_copied(self):
        """Recopier trois cent mille lignes produirait un classeur que le
        tableur met des minutes a ouvrir, pour une verification que
        personne ne fera a la main."""
        sheets = self.named(self.sheets(
            overrides={"export_parameters.source_max_rows": 10}))
        source = sheets["Fichier importé"]
        self.assertEqual(len(source), 1)
        self.assertIn("source_max_rows", source[0][0])


class TestTheControlNeverBreaksTheThreshold(ControlCase):
    """Un controle qui recalculerait un segment masque le publierait.

    Le classeur porte les valeurs : rien n'empeche techniquement d'ecrire
    la mediane d'un segment de trois personnes. C'est la regle qui
    l'interdit, et elle doit valoir ici comme partout ailleurs.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        haut = os.path.join(cls.directory, "config-seuil")
        write_default_configuration(haut)
        chemin = os.path.join(haut, "privacy_parameters.json")
        with open(chemin, encoding="utf-8") as handle:
            privacy = json.load(handle)
        # Un seuil que la plupart des segments ne franchissent pas : c'est
        # le cas qui compte, et il ne se rencontre pas avec le seuil
        # d'origine sur cette population.
        privacy["min_headcount_publish"] = 40
        with open(chemin, "w", encoding="utf-8") as handle:
            json.dump(privacy, handle, ensure_ascii=False)
        cls.masque = run_analysis(AnalysisRequest(
            source_path=cls.source, config_dir=haut))

    def _control(self):
        data = self.masque.config.as_dict()
        data["export_parameters"]["include_individual_data"] = True
        sheets = self.named(build_sheets(
            self.masque.payload, self.masque.filtered, Configuration(data)))
        return sheets["Contrôle segments"]

    def test_a_masked_segment_says_so_instead_of_recomputing(self):
        rows = self._control()
        masques = [ligne for ligne in rows[1:]
                   if len(ligne) > 2 and "masqués" in str(ligne[2])]
        self.assertTrue(masques)
        for ligne in masques:
            self.assertEqual(len(ligne), 3)

    def test_only_the_headcount_is_recomputed_for_a_masked_segment(self):
        rows = self._control()
        masques = {ligne[1] for ligne in rows[1:]
                   if len(ligne) > 2 and "masqués" in str(ligne[2])}
        self.assertTrue(masques)
        for ligne in rows[1:]:
            if len(ligne) > 2 and ligne[1] in masques:
                self.assertTrue(str(ligne[2]) == "Effectif"
                                or str(ligne[2]).startswith("Indicateurs "
                                                            "masqués"),
                                ligne[2])

    def test_a_category_where_one_sex_is_short_is_not_recomputed(self):
        data = self.masque.config.as_dict()
        data["export_parameters"]["include_individual_data"] = True
        sheets = self.named(build_sheets(
            self.masque.payload, self.masque.filtered, Configuration(data)))
        rows = sheets.get("Contrôle Pay Transparency") or []
        masques = {ligne[0] for ligne in rows[1:]
                   if len(ligne) > 1 and "masqués" in str(ligne[1])}
        self.assertTrue(masques)
        for ligne in rows[1:]:
            if len(ligne) > 1 and ligne[0] in masques:
                self.assertTrue(str(ligne[1]).startswith("Effectif")
                                or str(ligne[1]).startswith("Indicateurs "
                                                            "masqués"),
                                ligne[1])


class TestTheControlIsAnExplicitChoice(ControlCase):
    """Un controle se fait sur des valeurs, et les valeurs sont nominatives."""

    def test_without_individual_data_there_is_no_control(self):
        noms = [name for name, _ in self.sheets(individual=False)]
        for onglet in ("Fichier importé", "Données individuelles",
                       "Contrôle", "Contrôle segments"):
            self.assertNotIn(onglet, noms)

    def test_the_source_file_alone_is_not_enough(self):
        """Cocher le fichier importe sans les donnees individuelles ne
        produit rien : la case du classeur de controle suppose l'autre."""
        noms = [name for name, _ in self.sheets(individual=False, source=True)]
        self.assertNotIn("Fichier importé", noms)

    def test_the_individual_data_alone_still_controls(self):
        noms = [name for name, _ in self.sheets(individual=True, source=False)]
        self.assertNotIn("Fichier importé", noms)
        self.assertIn("Contrôle", noms)

    def test_no_name_reaches_the_workbook_by_default(self):
        """Le tableau importe voyage avec le resultat : il ne doit pas pour
        autant entrer dans le classeur sans qu'on l'ait demande."""
        sheets = self.sheets(individual=False, source=False)
        texte = " ".join(str(cell) for _name, rows in sheets
                         for ligne in rows for cell in ligne)
        self.assertNotIn("NOM0", texte)
        self.assertNotIn("PRENOM0", texte)

    def test_the_imported_file_is_what_carries_the_names(self):
        """Et il le fait en clair : c'est la contrepartie assumee du
        controle, pas un effet de bord a decouvrir."""
        sheets = self.named(self.sheets())
        texte = " ".join(str(cell) for ligne in sheets["Fichier importé"]
                         for cell in ligne)
        self.assertIn("NOM0", texte)
        autres = " ".join(str(cell) for name, rows in self.sheets()
                          for ligne in rows for cell in ligne
                          if name != "Fichier importé")
        self.assertNotIn("NOM0", autres)

    def test_the_shipped_setting_stays_off(self):
        from compensation_analytics.core.config import DEFAULTS

        self.assertFalse(DEFAULTS["export_parameters"]["include_source_file"])
        self.assertFalse(
            DEFAULTS["export_parameters"]["include_individual_data"])


class TestALargePopulationStaysOpenable(ControlCase):
    """Mille formules matricielles lisant chacune cent mille lignes
    feraient un classeur qui met des minutes a s'ouvrir : l'outil aurait
    l'air en panne au moment precis ou on veut le verifier."""

    def _sheets(self):
        return self.named(self.sheets(
            overrides={"export_parameters.control_max_rows": 10}))

    def test_the_segment_control_says_why_it_is_not_posed(self):
        rows = self._sheets()["Contrôle segments"]
        self.assertEqual(len(rows), 1)
        self.assertIn("control_max_rows", rows[0][0])

    def test_the_overall_control_is_still_posed(self):
        """Une centaine de formules sur une colonne : le tableur les refait
        instantanement, quelle que soit la taille du fichier."""
        rows = self._sheets()["Contrôle"]
        formules = [cell for ligne in rows for cell in ligne
                    if isinstance(cell, Formula)]
        self.assertGreater(len(formules), 20)

    def test_the_derived_columns_fall_back_to_their_value(self):
        rows = self._sheets()["Données individuelles"]
        age = rows[1][rows[0].index("Âge")]
        self.assertNotIsInstance(age, Formula)
        self.assertIsInstance(age, float)

    def test_nothing_is_dropped_from_the_individual_sheet(self):
        rows = self._sheets()["Données individuelles"]
        self.assertEqual(len(rows) - 1, len(self.result.filtered))


class TestTheMethodSheet(ControlCase):
    """Les controles prouvent l'accord ; celui-ci dit ce qui est calcule."""

    def test_it_is_always_there_even_without_individual_data(self):
        self.assertIn("Formules",
                      [name for name, _ in self.sheets(individual=False)])

    def test_it_names_the_percentile_method_and_the_directive(self):
        rows = self.named(self.sheets())["Formules"]
        texte = " ".join(str(cell) for ligne in rows for cell in ligne)
        self.assertIn("type 7", texte)
        self.assertIn("2023/970", texte)
        self.assertIn("365,2425", texte)
        self.assertIn("n−1", texte)


class TestDerivedColumnsCarryTheirRule(ControlCase):

    def test_age_and_tenure_are_written_as_formulas(self):
        rows = self.named(self.sheets())["Données individuelles"]
        entetes = rows[0]
        age = rows[1][entetes.index("Âge")]
        anciennete = rows[1][entetes.index("Ancienneté")]
        self.assertIsInstance(age, Formula)
        self.assertIn("365.2425", age.expression)
        self.assertIn("DATE(", anciennete.expression)

    def test_the_tenure_stops_at_the_leave_date(self):
        """Une anciennete qui courrait jusqu'a la date de reference pour un
        salarie sorti serait fausse — et la formule doit le montrer."""
        rows = self.named(self.sheets())["Données individuelles"]
        entetes = rows[0]
        anciennete = rows[1][entetes.index("Ancienneté")]
        sortie = entetes.index("Date de sortie")
        lettre = ""
        index = sortie + 1
        while index:
            index, reste = divmod(index - 1, 26)
            lettre = chr(ord("A") + reste) + lettre
        self.assertIn(f'IF({lettre}2=""', anciennete.expression)


if __name__ == "__main__":
    unittest.main()
