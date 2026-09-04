"""Non-regression : les resultats historiques doivent rester stables.

Le jeu de reference est une population fictive a graine fixe. Toute
modification du moteur qui change une valeur publiee fait echouer ce test :
il faut alors justifier l'ecart et regenerer la base de reference avec
`python3 tests/test_regression.py --regenerate`.
"""

import datetime as _dt
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.core.pipeline import AnalysisRequest, run_analysis
from compensation_analytics.io.xlsx_writer import write_workbook
from tools.generate_sample_population import HEADERS, build_rows

BASELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "fixtures", "regression_baseline.json")
REFERENCE_DATE = _dt.date(2025, 1, 1)
SEED = 20240101
ROWS = 1500
TOLERANCE = 1e-6


def build_snapshot():
    """Execute le pipeline sur le jeu de reference et extrait les valeurs cles."""
    directory = tempfile.mkdtemp()
    source = os.path.join(directory, "référence.xlsx")
    rows = build_rows(ROWS, SEED, REFERENCE_DATE, defects=False)
    write_workbook(source, [("Population", [HEADERS] + rows)])

    result = run_analysis(AnalysisRequest(
        source_path=source, reference_date=REFERENCE_DATE,
        segments=["business_unit", "grade", "gender"],
    ))
    payload = result.payload
    salary = payload["salary"]
    population = payload["population"]
    snapshot = {
        "effectif": population["headcount"],
        "age_moyen": population["age_mean"],
        "age_median": population["age_median"],
        "anciennete_moyenne": population["tenure_mean"],
        "anciennete_mediane": population["tenure_median"],
        "masse_salariale": salary["payroll"],
        "salaire_moyen": salary["mean"],
        "salaire_median": salary["median"],
        "p10": salary["p10"], "p25": salary["p25"], "p50": salary["p50"],
        "p75": salary["p75"], "p90": salary["p90"],
        "min": salary["min"], "max": salary["max"],
        "dispersion": salary["dispersion"],
        "qualite_statut": payload["quality"]["statut"],
        "nb_atypiques": len(payload["distribution"]["outliers"]),
        "tendance_r2": payload["scatter"]["trend"]["r_squared"],
        "segments": {
            segment["field"]: {
                row["segment"]: [row["headcount"], row["salary"].get("median")]
                for row in segment["rows"]
            }
            for segment in payload["segments"]
        },
    }
    return snapshot


def _compare(testcase, expected, actual, path=""):
    if isinstance(expected, dict):
        testcase.assertEqual(set(expected), set(actual), f"clés differentes en {path}")
        for key in expected:
            _compare(testcase, expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        testcase.assertEqual(len(expected), len(actual), f"longueur differente en {path}")
        for index, item in enumerate(expected):
            _compare(testcase, item, actual[index], f"{path}[{index}]")
    elif isinstance(expected, float) and isinstance(actual, (int, float)):
        testcase.assertAlmostEqual(expected, actual, delta=abs(expected) * TOLERANCE + 1e-9,
                                   msg=f"écart sur {path}")
    else:
        testcase.assertEqual(expected, actual, f"écart sur {path}")


class TestRegression(unittest.TestCase):
    def test_results_match_the_reference_baseline(self):
        with open(BASELINE_PATH, encoding="utf-8") as handle:
            expected = json.load(handle)
        _compare(self, expected, build_snapshot())

    def test_baseline_contains_no_personal_data(self):
        with open(BASELINE_PATH, encoding="utf-8") as handle:
            content = handle.read()
        self.assertNotIn("NOM0", content)
        self.assertNotIn("PRENOM0", content)
        self.assertNotIn("E00", content)


def regenerate():
    os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
    with open(BASELINE_PATH, "w", encoding="utf-8") as handle:
        json.dump(build_snapshot(), handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"Base de référence regeneree : {BASELINE_PATH}")


if __name__ == "__main__":
    if "--regenerate" in sys.argv:
        regenerate()
    else:
        unittest.main()
