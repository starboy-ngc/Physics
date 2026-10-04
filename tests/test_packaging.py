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


class TestTheWindowsLauncher(unittest.TestCase):
    """Le lanceur Windows : ce qu'il fait, et ce qu'il ne fait pas.

    Il n'est pas compilable ici — sa compilation demande une chaîne
    croisée —, mais son source est le livrable, et il doit rester lisible
    par qui homologue le paquet.
    """

    @classmethod
    def setUpClass(cls):
        chemin = os.path.join(ROOT, "packaging", "windows", "lanceur.c")
        with open(chemin, encoding="utf-8") as handle:
            cls.source = handle.read()

    def test_it_starts_the_interpreter_of_its_own_folder(self):
        """Ni le PATH, ni le registre, ni une variable d'environnement :
        l'interpréteur employé est celui du dossier, et lui seul."""
        self.assertIn("GetModuleFileNameW", self.source)
        self.assertIn("runtime\\\\pythonw.exe", self.source)

    def test_it_runs_the_tool_in_isolated_mode(self):
        """Aucun paquet installé ailleurs sur le poste ne peut entrer dans
        l'analyse : deux postes font le même calcul."""
        self.assertIn("-I -m hr_insight", self.source)

    def test_it_opens_no_console_window(self):
        self.assertIn("CREATE_NO_WINDOW", self.source)

    def test_it_explains_every_failure_in_french(self):
        """Un lanceur qui disparaît sans un mot ne laisse personne
        comprendre."""
        self.assertGreaterEqual(self.source.count("erreur(L\""), 3)
        self.assertNotIn("printf", self.source)

    def test_it_reaches_for_nothing_outside_its_folder(self):
        for interdit in ("URLDownload", "WinHttp", "InternetOpen",
                         "RegCreateKey", "RegSetValue", "ShellExecute",
                         "system(", "WinExec"):
            self.assertNotIn(interdit, self.source, interdit)

    def test_the_path_file_keeps_the_interpreter_isolated(self):
        chemin = os.path.join(ROOT, "packaging", "windows", "python312._pth")
        with open(chemin, encoding="utf-8") as handle:
            lignes = [l.strip() for l in handle
                      if l.strip() and not l.startswith("#")]
        self.assertEqual(lignes, ["Lib", "DLLs", ".."])


class TestTheWindowsBuild(unittest.TestCase):
    """Ce que le script de composition promet."""

    @classmethod
    def setUpClass(cls):
        from tools import build_windows
        cls.module = build_windows

    def test_it_takes_only_the_components_it_needs(self):
        """Ni pip, ni la documentation, ni la suite de tests de CPython :
        l'outil n'installe rien et n'a pas à les embarquer."""
        self.assertEqual(set(self.module.COMPOSANTS),
                         {"core", "exe", "lib", "tcltk", "ucrt"})
        for absent in ("pip", "doc", "test", "dev"):
            self.assertNotIn(absent, self.module.COMPOSANTS)

    def test_tcltk_is_taken_because_the_tool_has_a_window(self):
        """L'oubli le plus facile : la distribution « embeddable » de
        python.org ne porte pas tkinter, et l'outil ne démarrerait pas."""
        self.assertIn("tcltk", self.module.COMPOSANTS)

    def test_the_standard_library_is_trimmed(self):
        for retiré in ("test", "idlelib", "ensurepip", "site-packages"):
            self.assertIn(retiré, self.module.LIB_INUTILE)

    def test_the_build_script_never_ships(self):
        from tools.build_archive import OUTILS_EXCLUS
        self.assertIn("build_windows.py", OUTILS_EXCLUS)


class TestTheSingleFileLauncher(unittest.TestCase):
    """Le lanceur à fichier unique : ce qu'il fait, et ce qu'il coûte."""

    @classmethod
    def setUpClass(cls):
        chemin = os.path.join(ROOT, "packaging", "windows",
                              "lanceur-unique.c")
        with open(chemin, encoding="utf-8") as handle:
            cls.source = handle.read()

    def test_it_deposits_in_the_profile_not_in_temp(self):
        """%TEMP% est effacé, surveillé de près, et souvent interdit
        d'exécution par stratégie de groupe."""
        self.assertIn("CSIDL_LOCAL_APPDATA", self.source)
        self.assertNotIn("GetTempPath", self.source)

    def test_windows_unfolds_the_archive_itself(self):
        """Aucune bibliothèque de décompression embarquée : rien à
        auditer de ce côté, rien qui puisse être vulnérable."""
        self.assertIn("SetupIterateCabinetW", self.source)
        for embarque in ("inflate", "zlib", "lzma", "BZ2"):
            self.assertNotIn(embarque, self.source, embarque)

    def test_the_footer_is_searched_and_never_assumed(self):
        """Signer un exécutable ajoute la signature APRÈS la charge : lire
        les derniers octets refusait net tout exécutable signé."""
        self.assertIn("FENETRE_RECHERCHE", self.source)
        self.assertIn("rang--", self.source)

    def test_the_deposit_is_named_after_the_payload(self):
        """Deux versions ne peuvent pas se mélanger, et la même version ne
        se réextrait jamais."""
        self.assertIn("empreinte", self.source)
        self.assertIn("%08x", self.source)

    def test_the_configuration_outlives_the_versions(self):
        """Elle vit au-dessus du dossier de version : une mise à jour ne
        la remet pas à zéro."""
        indice_config = self.source.index("\\\\config")
        indice_depot = self.source.index("wsprintfW(numero")
        self.assertGreater(indice_config, indice_depot)

    def test_the_cost_of_a_single_file_is_written_down(self):
        """Le défaut d'un fichier unique doit être lisible par qui relit
        le code, pas seulement connu de qui l'a écrit."""
        self.assertIn("protection de poste", self.source)

    def test_it_reaches_for_nothing_outside_the_machine(self):
        for interdit in ("URLDownload", "WinHttp", "InternetOpen",
                         "RegCreateKey", "RegSetValue", "WinExec"):
            self.assertNotIn(interdit, self.source, interdit)


class TestTheStarIcon(unittest.TestCase):
    """L'icône est dessinée par une formule, pas posée en pixels."""

    @classmethod
    def setUpClass(cls):
        chemin = os.path.join(ROOT, "packaging", "windows", "etoile.ico")
        if not os.path.isfile(chemin):
            raise unittest.SkipTest("icône absente")
        with open(chemin, "rb") as handle:
            cls.donnees = handle.read()

    def test_it_is_a_real_icon_container(self):
        import struct
        reserve, genre, nombre = struct.unpack("<HHH", self.donnees[:6])
        self.assertEqual((reserve, genre), (0, 1))
        self.assertGreaterEqual(nombre, 5)

    def test_every_size_windows_asks_for_is_there(self):
        import struct
        _r, _g, nombre = struct.unpack("<HHH", self.donnees[:6])
        tailles = set()
        for rang in range(nombre):
            entree = struct.unpack("<BBBBHHII",
                                   self.donnees[6 + 16 * rang:22 + 16 * rang])
            tailles.add(entree[0] or 256)
        for attendue in (16, 32, 48, 256):
            self.assertIn(attendue, tailles)

    def test_each_size_is_drawn_and_not_rescaled(self):
        """Une icône de 16 pixels réduite depuis 256 est illisible : chaque
        taille est rendue pour elle-même."""
        from tools.render_icon import dessiner
        petite = dessiner(16)
        grande = dessiner(32)
        self.assertEqual(len(petite), 16 * 16 * 4)
        self.assertEqual(len(grande), 32 * 32 * 4)

    def test_the_star_points_upward(self):
        """Une étoile posée de travers se remarque, même de qui ne saurait
        pas dire pourquoi."""
        from tools.render_icon import sommets
        points = sommets(rayon=10.0, centre=10.0)
        premier = points[0]
        self.assertAlmostEqual(premier[0], 10.0, places=6)
        self.assertLess(premier[1], 10.0)
