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
        self.assertIn("hr_insight/cli.py", names)
        self.assertIn("__main__.py", names)
        self.assertFalse([name for name in names if "__pycache__" in name],
                         "aucun cache compilé ne doit être distribué")


#: Ce qu'une revue de paquet cherche d'abord dans du code Python : une
#: execution dynamique, un processus fils, un acces reseau, un effacement
#: recursif. Le livrable n'en cite aucun — c'est ce qui permet de le dire
#: sans avoir a l'exécuter.
MOTIFS_SENSIBLES = (r"\beval\(", r"\bexec\(", r"subprocess", r"os\.system",
                    r"os\.popen", r"shutil\.rmtree", r"\bsocket\b",
                    r"\burllib\b", r"\brequests\b")


class TestTheDeliveredPackageIsReviewable(unittest.TestCase):
    """L'archive livrée, telle que l'IT la recevra."""

    @classmethod
    def setUpClass(cls):
        import tempfile
        from tools.build_archive import build_tree
        cls.directory = tempfile.mkdtemp()
        cls.tree = build_tree(os.path.join(cls.directory, "hr-insight"))

    def _sources(self):
        for dossier, _d, fichiers in os.walk(self.tree):
            for nom in fichiers:
                if nom.endswith(".py"):
                    chemin = os.path.join(dossier, nom)
                    with open(chemin, encoding="utf-8") as handle:
                        yield os.path.relpath(chemin, self.tree), handle.read()

    def test_no_sensitive_call_anywhere_in_the_delivery(self):
        import re
        trouvés = []
        for chemin, source in self._sources():
            for motif in MOTIFS_SENSIBLES:
                if re.search(motif, source):
                    trouvés.append(f"{chemin} : {motif}")
        self.assertEqual(trouvés, [], "motifs sensibles dans le livrable")

    def test_the_build_script_does_not_ship_itself(self):
        """Il fabrique l'archive : une fois faite, il ne sert a personne,
        et il etait le seul fichier livre a effacer des dossiers."""
        livrés = [chemin for chemin, _ in self._sources()]
        self.assertNotIn(os.path.join("tools", "build_archive.py"), livrés)

    def test_the_sample_generators_do_ship(self):
        """Ils produisent des jeux d'essai sans donnée réelle : c'est par
        eux qu'une équipe RH prend l'outil en main."""
        livrés = [chemin for chemin, _ in self._sources()]
        self.assertIn(os.path.join("tools", "generate_sample_population.py"),
                      livrés)

    def test_the_tool_itself_is_complete(self):
        livrés = [chemin for chemin, _ in self._sources()]
        for attendu in ("cli.py", os.path.join("core", "pipeline.py"),
                        os.path.join("ui", "app.py")):
            self.assertIn(os.path.join("hr_insight", attendu), livrés)


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
