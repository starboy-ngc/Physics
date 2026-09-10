"""Conversions, tranches et configuration : la ou une erreur ne se voit pas.

Un import qui refuse un fichier se remarque. Un import qui lit « 45.000 »
comme 45,0 ne se remarque jamais : il rend une analyse plausible et fausse.
Ce fichier tient les conversions une par une, puis les tranches d'age et
d'anciennete — qui decident du decoupage de toutes les pyramides —, puis le
chargement des parametres, y compris quand le poste refuse d'ecrire.

Aucune donnee RH reelle.
"""

import datetime as _dt
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.support import HEADERS, REFERENCE_DATE, build_population, make_config, make_row
from compensation_analytics.core.config import (Configuration, DEFAULTS,
                                                default_config_dir,
                                                load_configuration,
                                                write_configuration,
                                                write_default_configuration)
from compensation_analytics.core.errors import ConfigError
from compensation_analytics.core.normalize import (band_for, extend_open_band,
                                                   parse_date, parse_number,
                                                   period_key)


class TestParsingNumbers(unittest.TestCase):
    """Une cellule qui n'est pas un nombre est refusee, jamais rabotee."""

    def test_the_plain_forms(self):
        for value, expected in ((42, 42.0), (42.5, 42.5), ("42", 42.0),
                                ("42.5", 42.5), (" 42 ", 42.0)):
            self.assertEqual(parse_number(value), expected, repr(value))

    def test_the_french_forms(self):
        for value in ("45 000,50", "45 000,50", "45.000,50"):
            self.assertEqual(parse_number(value), 45000.50, repr(value))

    def test_the_english_forms(self):
        self.assertEqual(parse_number("45,000.50"), 45000.50)
        self.assertEqual(parse_number("45000.50"), 45000.50)

    def test_a_currency_sign_is_tolerated(self):
        for value in ("45 000 €", "€45000", "45000 EUR", "45000 USD",
                      "£45000", "45 000"):
            self.assertEqual(parse_number(value), 45000.0, repr(value))

    def test_a_repeated_separator_must_group_by_three(self):
        """« 1.234.567 » est un nombre ; « 1.2.3.4 » n'en est pas un. La
        forme acceptee autorisait n'importe quel groupement et retirait
        ensuite les points : un numero de version tombe dans une colonne de
        salaires devenait 1 234."""
        self.assertEqual(parse_number("1.234.567"), 1234567.0)
        self.assertEqual(parse_number("1,234,567"), 1234567.0)
        for value in ("1.2.3.4", "1.23.456", "12.34.567", "1,2,3"):
            self.assertIsNone(parse_number(value), repr(value))

    def test_a_lone_separator_before_three_digits_stays_ambiguous(self):
        """« 12.345 » vaut 12 345 en francais et 12,345 en anglais. La
        lecture decimale est retenue, et le controle qualite la signale
        plutot que de deviner en silence."""
        self.assertEqual(parse_number("12.345"), 12.345)
        self.assertEqual(parse_number("12,345"), 12.345)

    def test_the_ambiguity_is_reported_to_the_quality_check(self):
        from compensation_analytics.core.quality import run_quality_check
        from compensation_analytics.core.mapping import resolve_mapping
        from compensation_analytics.core.normalize import normalise_table

        config = make_config()
        mapping = resolve_mapping(list(HEADERS), config)
        people = normalise_table(list(HEADERS), [make_row(1, salary="45.000")],
                                 mapping, config, source_name="t",
                                 reference_date=REFERENCE_DATE)
        report = run_quality_check(people, mapping, config)
        self.assertTrue(any("ambiguous_separator" in finding.code
                            for finding in report.findings))

    def test_accounting_parentheses_mean_negative(self):
        self.assertEqual(parse_number("(1 200)"), -1200.0)
        self.assertEqual(parse_number("(1200,50)"), -1200.50)

    def test_a_percentage_is_refused_rather_than_guessed(self):
        """« 80 % » dans une colonne de temps de travail vaut-il 80 ou
        0,8 ? Deviner ferait un equivalent temps plein faux, et rien ne le
        dirait. La cellule est refusee et signalee au controle qualite, qui
        la designe par son numero de ligne."""
        self.assertIsNone(parse_number("80 %"))

    def test_what_is_not_a_number_is_refused(self):
        """La version qui supprimait tout caractere non chiffre lisait
        « 1E+05 » comme 105, « 50k » comme 50 et « 5O000 » — la lettre O
        frappee a la place du zero — comme 5 000. La cellule passait pour un
        montant plausible, sans la moindre alerte."""
        for value in ("1E+05", "50k", "5O000", "12 mois", "N/A", "#DIV/0!",
                      "quarante", "-", "..", "1.2.3.4"):
            self.assertIsNone(parse_number(value), repr(value))

    def test_nothing_is_nothing(self):
        for value in (None, "", "   "):
            self.assertIsNone(parse_number(value))

    def test_a_boolean_is_never_a_number(self):
        """« Cadre = Oui » ne vaut pas 1 dans une moyenne de salaires."""
        self.assertIsNone(parse_number(True))
        self.assertIsNone(parse_number(False))


class TestParsingDates(unittest.TestCase):
    def test_a_date_stays_itself(self):
        self.assertEqual(parse_date(_dt.date(2020, 3, 1)), _dt.date(2020, 3, 1))

    def test_a_datetime_loses_only_its_time(self):
        self.assertEqual(parse_date(_dt.datetime(2020, 3, 1, 14, 30)),
                         _dt.date(2020, 3, 1))

    def test_the_written_forms(self):
        for value in ("2020-03-01", "01/03/2020", "01-03-2020",
                      "2020-03-01T09:00:00", "2020-03-01 09:00"):
            self.assertEqual(parse_date(value), _dt.date(2020, 3, 1),
                             repr(value))

    def test_an_excel_serial_becomes_a_date(self):
        self.assertEqual(parse_date(45000), _dt.date(2023, 3, 15))

    def test_an_impossible_serial_is_refused_rather_than_raising(self):
        self.assertIsNone(parse_date(10 ** 12))

    def test_what_is_not_a_date_is_refused(self):
        for value in (None, "", "   ", "pas une date", "32/13/2020"):
            self.assertIsNone(parse_date(value), repr(value))


class TestPeriodKeys(unittest.TestCase):
    """L'ordre des periodes decide de celle qui est analysee par defaut."""

    def test_years_sort_as_years(self):
        self.assertEqual(sorted(["2026", "2024", "2025"], key=period_key),
                         ["2024", "2025", "2026"])

    def test_months_sort_inside_their_year(self):
        self.assertEqual(
            sorted(["2025-12", "2024-03", "2025-01"], key=period_key),
            ["2024-03", "2025-01", "2025-12"])

    def test_a_date_sorts_with_the_months(self):
        self.assertEqual(sorted(["2025-06-30", "2025-01-15"], key=period_key),
                         ["2025-01-15", "2025-06-30"])

    def test_a_label_that_is_not_a_date_sorts_last_and_alphabetically(self):
        """Sinon « Budget » passerait pour la periode la plus recente et
        serait analyse par defaut."""
        ordered = sorted(["Budget", "2025", "Réel"], key=period_key)
        self.assertEqual(ordered[0], "2025")
        self.assertEqual(ordered[1:], ["Budget", "Réel"])


class TestBands(unittest.TestCase):
    """Les tranches decident du decoupage de toutes les pyramides."""

    BANDS = [{"label": "20-29", "min": 20, "max": 29, "max_inclusive": True},
             {"label": "30-39", "min": 30, "max": 39, "max_inclusive": True},
             {"label": "60+", "min": 60, "max": None}]

    def test_a_value_lands_in_its_band(self):
        self.assertEqual(band_for(25, self.BANDS), "20-29")
        self.assertEqual(band_for(39, self.BANDS), "30-39")

    def test_the_open_band_catches_everything_above(self):
        self.assertEqual(band_for(95, self.BANDS), "60+")

    def test_a_value_between_two_bands_lands_nowhere(self):
        """Un trou dans le decoupage doit se voir, et non se combler tout
        seul dans la tranche voisine."""
        self.assertEqual(band_for(45, self.BANDS), "")

    def test_nothing_lands_nowhere(self):
        self.assertEqual(band_for(None, self.BANDS), "")
        self.assertEqual(band_for(25, []), "")

    def test_an_open_band_is_extended_to_cover_the_values(self):
        extended = extend_open_band(self.BANDS, 82, 10, "{low}-{high}",
                                    "{low}+", 10)
        self.assertGreater(len(extended), len(self.BANDS))
        self.assertEqual(band_for(82, extended)[:2], "80")

    def test_a_fully_bounded_set_is_left_alone(self):
        bounded = [{"label": "A", "min": 0, "max": 10}]
        self.assertEqual(extend_open_band(bounded, 99, 10, "{low}-{high}",
                                          "{low}+", 10), bounded)

    def test_a_band_without_a_floor_is_left_alone(self):
        odd = [{"label": "?", "min": None, "max": None}]
        self.assertEqual(extend_open_band(odd, 99, 10, "{low}-{high}",
                                          "{low}+", 10), odd)

    def test_the_extension_stops_at_the_declared_limit(self):
        """Une valeur aberrante — un age de 900 ans — ne doit pas produire
        quatre-vingt-dix tranches. La limite porte sur les tranches
        engendrees, celles du decoupage declare restant intactes."""
        kept = len(self.BANDS) - 1
        extended = extend_open_band(self.BANDS, 900, 10, "{low}-{high}",
                                    "{low}+", 6)
        self.assertEqual(len(extended), kept + 6 + 1)
        self.assertTrue(extended[-1]["max"] is None)

    def test_the_bands_actually_used_travel_with_the_population(self):
        """Tout ce qui les affiche doit les lire la, et non relire le
        fichier de parametres : la derniere tranche a pu etre prolongee."""
        people = build_population([make_row(index, age=30 + index)
                                   for index in range(5)])
        self.assertTrue(people.age_bands)
        self.assertTrue(people.tenure_bands)


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def test_the_defaults_load_without_any_file(self):
        config = load_configuration(os.path.join(self.directory, "absent"))
        self.assertEqual(config.get("privacy_parameters.min_headcount_publish"),
                         5)

    def test_a_written_configuration_is_read_back_identically(self):
        write_default_configuration(self.directory)
        self.assertEqual(load_configuration(self.directory).as_dict(),
                         load_configuration().as_dict())

    def test_a_file_overrides_only_what_it_declares(self):
        write_default_configuration(self.directory)
        path = os.path.join(self.directory, "privacy_parameters.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"min_headcount_publish": 12}, handle)
        config = load_configuration(self.directory)
        self.assertEqual(config.get("privacy_parameters.min_headcount_publish"),
                         12)
        self.assertEqual(config.get("privacy_parameters.min_headcount_chart"),
                         10)

    def test_a_broken_file_is_refused_by_its_name(self):
        """« Expecting value: line 1 column 3 » ne dit pas quel fichier
        rouvrir."""
        write_default_configuration(self.directory)
        with open(os.path.join(self.directory, "salary_parameters.json"), "w",
                  encoding="utf-8") as handle:
            handle.write("{ ceci n'est pas du JSON")
        with self.assertRaises(ConfigError) as caught:
            load_configuration(self.directory)
        self.assertIn("salary_parameters.json", caught.exception.message)

    def test_a_file_that_is_not_an_object_is_refused(self):
        write_default_configuration(self.directory)
        with open(os.path.join(self.directory, "salary_parameters.json"), "w",
                  encoding="utf-8") as handle:
            json.dump([1, 2, 3], handle)
        with self.assertRaises(ConfigError) as caught:
            load_configuration(self.directory)
        self.assertIn("objet", caught.exception.message)

    def test_an_unknown_section_is_refused_with_its_name(self):
        with self.assertRaises(ConfigError) as caught:
            load_configuration().section("parametres_inconnus")
        self.assertIn("parametres_inconnus", caught.exception.message)

    def test_an_unknown_setting_falls_back_on_the_default_given(self):
        config = load_configuration()
        self.assertEqual(config.get("privacy_parameters.inexistant", 7), 7)
        self.assertEqual(config.get("section.inexistante.profonde", "x"), "x")
        self.assertIsNone(config.get("privacy_parameters.inexistant"))

    def test_a_folder_that_refuses_writing_is_reported(self):
        """Un poste verrouille est le cas nominal, pas l'exception."""
        blocked = os.path.join(self.directory, "fichier")
        with open(blocked, "w", encoding="utf-8") as handle:
            handle.write("x")
        with self.assertRaises(ConfigError) as caught:
            write_configuration(blocked, "privacy_parameters", {"a": 1})
        self.assertIn("écriture", caught.exception.message)

    def test_writing_leaves_no_temporary_file_behind(self):
        """L'ecriture passe par un fichier temporaire puis un remplacement :
        une coupure ne doit pas laisser un fichier de parametres a moitie
        ecrit, ni un residu."""
        write_configuration(self.directory, "privacy_parameters",
                            dict(DEFAULTS["privacy_parameters"]))
        written = os.listdir(self.directory)
        self.assertEqual(written, ["privacy_parameters.json"])

    def test_every_declared_file_has_a_default(self):
        from compensation_analytics.core.config import CONFIG_FILES

        for name in CONFIG_FILES:
            self.assertIn(name, DEFAULTS, name)
            self.assertIsInstance(DEFAULTS[name], dict, name)

    def test_the_default_folder_is_an_absolute_path(self):
        self.assertTrue(os.path.isabs(default_config_dir()))

    def test_a_configuration_can_be_built_from_a_plain_dictionary(self):
        config = Configuration({"privacy_parameters": {"min_headcount_publish": 3}})
        self.assertEqual(config.get("privacy_parameters.min_headcount_publish"),
                         3)


if __name__ == "__main__":
    unittest.main()
