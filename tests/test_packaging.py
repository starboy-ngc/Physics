"""L'archive distribuee doit se comporter comme le code source.

Une archive n'est pas qu'un fichier a copier : c'est ce que l'utilisateur
lance reellement. Un ecart entre elle et les sources ne se voit qu'apres
livraison, quand il est le plus couteux.
"""

import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestTheLauncher(unittest.TestCase):
    def test_the_entry_point_passes_the_exit_code_on(self):
        """`zipapp -m` genere un lanceur qui appelle main() sans retransmettre
        sa valeur : tout code de sortie serait perdu, et "controle" ne
        pourrait plus signaler d'anomalie bloquante a un traitement par lot.
        """
        from tools.build_archive import LAUNCHER
        self.assertIn("sys.exit(main())", LAUNCHER)


class TestTheBuiltArchive(unittest.TestCase):
    """Construction reelle, puis execution : le seul test qui prouve que le
    livrable fonctionne."""

    @classmethod
    def setUpClass(cls):
        from tools.build_archive import build_pyz
        cls.directory = tempfile.mkdtemp()
        cls.pyz = build_pyz(os.path.join(cls.directory, "outil.pyz"))
        from tools.generate_sample_population import write_population
        cls.clean = write_population(
            os.path.join(cls.directory, "propre.xlsx"), rows=60, clean=True)
        cls.faulty = write_population(
            os.path.join(cls.directory, "defauts.xlsx"), rows=60, clean=False)

    def _run(self, *arguments):
        return subprocess.run([sys.executable, self.pyz, *arguments],
                              capture_output=True, text=True,
                              cwd=self.directory)

    def test_the_archive_runs_at_all(self):
        completed = self._run("--version")
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_a_clean_population_passes_the_quality_check(self):
        completed = self._run("controle", self.clean)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("CONFORME", completed.stdout)

    def test_a_faulty_population_reports_a_failing_exit_code(self):
        """C'est ce code que lit un traitement par lot pour s'arreter."""
        completed = self._run("controle", self.faulty)
        self.assertEqual(completed.returncode, 1, completed.stdout)

    def test_an_unreadable_file_does_not_report_success(self):
        completed = self._run("analyse", "absent.xlsx")
        self.assertNotEqual(completed.returncode, 0)

    def test_the_archive_carries_its_own_configuration(self):
        """Lancee depuis un dossier vide, l'archive doit rester parametree :
        sinon l'utilisateur croit avoir perdu ses reglages."""
        completed = self._run("mapping", self.clean)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("business_unit", completed.stdout)

    def test_the_archive_is_a_readable_zip(self):
        """L'IT doit pouvoir en lire l'integralite du code sans l'executer."""
        import zipfile
        with zipfile.ZipFile(self.pyz) as bundle:
            names = bundle.namelist()
        self.assertIn("compensation_analytics/cli.py", names)
        self.assertIn("__main__.py", names)
        self.assertFalse([name for name in names if "__pycache__" in name],
                         "aucun cache compilé ne doit être distribué")


class TestWhatIsShipped(unittest.TestCase):
    def test_the_launchers_referenced_by_the_build_exist(self):
        """Une entree manquante serait silencieusement ignoree a la copie."""
        from tools.build_archive import FILES
        for source, _target in FILES:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, source)), source)

    def test_no_real_population_is_ever_copied_into_the_archive(self):
        """Les jeux de demonstration sont generes, jamais repris d'un
        fichier existant : aucune donnee RH reelle ne peut se glisser dans
        un livrable."""
        from tools import build_archive
        with open(build_archive.__file__, encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("write_population", source)
        for name, _target in build_archive.FILES:
            self.assertFalse(name.endswith((".xlsx", ".csv")), name)

if __name__ == "__main__":
    unittest.main()
