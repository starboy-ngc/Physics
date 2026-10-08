"""L'archive distribuee doit se comporter comme le code source.

Une archive n'est pas qu'un fichier a copier : c'est ce que l'utilisateur
lance reellement. Un ecart entre elle et les sources ne se voit qu'apres
livraison, quand il est le plus couteux.
"""

import os
import re
import shutil
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
        # Les dimensions declarees ne se lisent que si la configuration
        # embarquee est trouvee : sans elle, la liste serait vide.
        self.assertIn("tenure_band", completed.stdout)
        self.assertIn("base_salary", completed.stdout)

    def test_the_archive_is_a_readable_zip(self):
        """L'IT doit pouvoir en lire l'integralite du code sans l'executer."""
        import zipfile
        with zipfile.ZipFile(self.pyz) as bundle:
            names = bundle.namelist()
        self.assertIn("hr_analytics/cli.py", names)
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
        cls.tree = build_tree(os.path.join(cls.directory, "hr-analytics"))

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

    def test_the_sample_generators_do_not_ship(self):
        """Un outil mis à disposition d'un service RH n'a pas besoin de
        population inventée : il en reçoit une le jour même. Les
        générateurs restent au dépôt, où la suite de tests s'appuie sur
        eux."""
        livrés = [chemin for chemin, _ in self._sources()]
        for generateur in ("generate_sample_population.py",
                           "generate_realistic_population.py"):
            self.assertNotIn(os.path.join("tools", generateur), livrés)

    def test_no_demonstration_workbook_ships(self):
        """Un classeur aux noms vraisemblables posé dans un livrable RH se
        lit comme une fuite par qui l'ouvre sans contexte."""
        classeurs = []
        for dossier, _d, fichiers in os.walk(self.tree):
            classeurs += [nom for nom in fichiers if nom.endswith(".xlsx")]
        self.assertEqual(classeurs, [])

    def test_the_tool_itself_is_complete(self):
        livrés = [chemin for chemin, _ in self._sources()]
        for attendu in ("cli.py", os.path.join("core", "pipeline.py"),
                        os.path.join("ui", "app.py")):
            self.assertIn(os.path.join("hr_analytics", attendu), livrés)


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

    #: Les deux lanceurs, et non le seul premier. Celui qu'on livre
    #: aujourd'hui est « lanceur-unique.c » : les controles ne portaient
    #: pas sur lui, et retirer son « -I » ne faisait echouer aucun essai.
    LANCEURS = ("lanceur.c", "lanceur-unique.c")

    @classmethod
    def setUpClass(cls):
        cls.sources = {}
        for nom in cls.LANCEURS:
            chemin = os.path.join(ROOT, "packaging", "windows", nom)
            with open(chemin, encoding="utf-8") as handle:
                cls.sources[nom] = handle.read()

    def test_each_starts_the_interpreter_of_its_own_folder(self):
        """Ni le PATH, ni le registre, ni une variable d'environnement :
        l'interpréteur employé est celui du dossier, et lui seul."""
        for nom, source in self.sources.items():
            self.assertIn("GetModuleFileNameW", source, nom)
            self.assertIn("runtime\\\\pythonw.exe", source, nom)

    def test_each_runs_the_tool_in_isolated_mode(self):
        """Aucun paquet installé ailleurs sur le poste ne peut entrer dans
        l'analyse : deux postes font le même calcul."""
        for nom, source in self.sources.items():
            self.assertIn("-I -m hr_analytics", source, nom)

    def test_neither_opens_a_console_window(self):
        for nom, source in self.sources.items():
            self.assertIn("CREATE_NO_WINDOW", source, nom)

    def test_each_explains_every_failure_in_french(self):
        """Un lanceur qui disparaît sans un mot ne laisse personne
        comprendre : il parle par boîte de message, jamais par la console.

        Le contrôle cherchait la chaîne « printf », qui se trouve aussi au
        milieu de « wsprintfW » — une fonction de mise en forme de chaîne,
        sans rapport avec la console. Il cherche donc les appels eux-mêmes.
        """
        import re

        console = re.compile(r"\b(?:printf|fprintf|sprintf|puts|fputs)\s*\(")
        for nom, source in self.sources.items():
            self.assertGreaterEqual(source.count("erreur(L\""), 3, nom)
            self.assertIsNone(console.search(source), nom)
            self.assertNotIn("stdio.h", source, nom)

    def test_neither_reaches_for_anything_outside_its_folder(self):
        for nom, source in self.sources.items():
            for interdit in ("URLDownload", "WinHttp", "InternetOpen",
                             "RegCreateKey", "RegSetValue", "ShellExecute",
                             "system(", "WinExec"):
                self.assertNotIn(interdit, source, f"{nom} : {interdit}")

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


class TestTheNetworkStackIsRemoved(unittest.TestCase):
    """L'interpréteur livré ne porte pas de quoi ouvrir une connexion.

    L'outil n'importe aucun module réseau — d'autres tests le vérifient sur
    le source. Celui-ci vérifie l'étape d'après : que le Python embarqué
    parte sans sa pile réseau, pour qu'une équipe qui homologue le paquet
    n'ait pas à nous croire sur parole.
    """

    def _runtime_postiche(self):
        """Une arborescence qui ressemble à un Python Windows extrait."""
        racine = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, racine, True)
        for dossier in ("DLLs", "Lib", os.path.join("Lib", "urllib"),
                        os.path.join("Lib", "http"),
                        os.path.join("Lib", "email"),
                        os.path.join("Lib", "ctypes"),
                        os.path.join("Lib", "multiprocessing"),
                        os.path.join("Lib", "sqlite3"),
                        os.path.join("Lib", "zoneinfo")):
            os.makedirs(os.path.join(racine, dossier), exist_ok=True)
        for chemin in ("DLLs/_socket.pyd", "DLLs/_ssl.pyd", "DLLs/select.pyd",
                       "DLLs/_hashlib.pyd", "libssl-3.dll",
                       "libcrypto-3.dll", "Lib/socket.py", "Lib/ssl.py",
                       "Lib/pathlib.py", "Lib/urllib/parse.py",
                       "Lib/urllib/request.py", "Lib/http/client.py",
                       "Lib/email/message.py",
                       "DLLs/_ctypes.pyd", "DLLs/_multiprocessing.pyd",
                       "DLLs/_sqlite3.pyd", "DLLs/_wmi.pyd",
                       "DLLs/winsound.pyd", "DLLs/pyexpat.pyd",
                       "DLLs/_elementtree.pyd", "DLLs/_tkinter.pyd",
                       "DLLs/_decimal.pyd", "DLLs/_bz2.pyd", "DLLs/_lzma.pyd",
                       "DLLs/_uuid.pyd", "DLLs/_zoneinfo.pyd",
                       "Lib/decimal.py", "Lib/_pydecimal.py", "Lib/uuid.py",
                       "Lib/zoneinfo/__init__.py",
                       "Lib/subprocess.py", "Lib/ctypes/__init__.py",
                       "Lib/multiprocessing/__init__.py",
                       "Lib/sqlite3/__init__.py", "Lib/zipfile.py"):
            with open(os.path.join(racine, *chemin.split("/")), "wb") as flux:
                flux.write(b"x")
        return racine

    def test_the_socket_module_is_what_decides(self):
        """Sans « _socket.pyd », aucun code Python ne peut ouvrir de
        connexion, quelle que soit la bibliothèque qui le demanderait."""
        from tools.build_windows import RESEAU_DLLS

        self.assertIn("_socket.pyd", RESEAU_DLLS)
        self.assertIn("_ssl.pyd", RESEAU_DLLS)

    def test_it_takes_the_network_stack_and_leaves_the_rest(self):
        from tools.build_windows import reseau_a_retirer

        racine = self._runtime_postiche()
        retires = {os.path.relpath(chemin, racine).replace(os.sep, "/")
                   for chemin in reseau_a_retirer(racine)}
        for parti in ("DLLs/_socket.pyd", "DLLs/_ssl.pyd", "DLLs/select.pyd",
                      "libssl-3.dll", "Lib/socket.py", "Lib/ssl.py",
                      "Lib/http", "Lib/email", "Lib/urllib/request.py"):
            self.assertIn(parti, retires, parti)
        # Gardés : les empreintes SHA-256 et l'anonymisation en dépendent,
        # et « pathlib » importe « urllib.parse » pour écrire une URL.
        for reste in ("DLLs/_hashlib.pyd", "libcrypto-3.dll",
                      "Lib/urllib/parse.py", "Lib/pathlib.py"):
            self.assertNotIn(reste, retires, reste)

    def test_removing_it_really_removes_it(self):
        from tools.build_windows import retirer_reseau

        racine = self._runtime_postiche()
        retirer_reseau(racine)
        for parti in ("DLLs/_socket.pyd", "Lib/http", "Lib/ssl.py"):
            self.assertFalse(os.path.exists(os.path.join(racine,
                                                         *parti.split("/"))),
                             parti)
        self.assertTrue(os.path.exists(os.path.join(racine, "DLLs",
                                                    "_hashlib.pyd")))
        self.assertTrue(os.path.exists(os.path.join(racine, "Lib", "urllib",
                                                    "parse.py")))

    def test_ctypes_is_what_decides(self):
        """Sans « _ctypes.pyd », aucun code Python ne peut appeler une
        fonction de Windows qui ne lui soit pas déjà exposée.

        Le retrait de « subprocess » et de « _multiprocessing.pyd » retire
        les bibliothèques, pas la capacité : « os.system », « os.popen »
        et « _winapi.CreateProcess » sont compilés dans « python312.dll »
        et y restent. Le commentaire du module le dit, et ce test vérifie
        qu'il continue de le dire — une liste de retrait qui promet plus
        qu'elle ne tient est pire que pas de liste du tout.
        """
        import inspect

        from tools import build_windows
        from tools.build_windows import CAPACITES_DLLS, CAPACITES_LIB

        self.assertIn("_ctypes.pyd", CAPACITES_DLLS)
        self.assertIn("_multiprocessing.pyd", CAPACITES_DLLS)
        self.assertIn("subprocess.py", CAPACITES_LIB)
        source = inspect.getsource(build_windows)
        self.assertIn("CE QUE CE RETRAIT NE FAIT PAS", source)
        self.assertIn("_winapi.CreateProcess", source)

    def test_the_tcl_build_system_and_its_registry_bridge_are_dropped(self):
        """Trouvailles d'audit : « reg1.3 » donne à du code Tcl le droit
        d'écrire dans la base de registre, dans un outil qui affirme n'y
        jamais toucher ; « dde1.4 » ouvre un canal entre applications que
        les protections de poste surveillent ; « nmake » porte un
        « nmakehlp.exe » compilé et non signé, à l'intérieur du produit."""
        from tools.build_windows import TCL_INUTILE

        for parti in ("reg1.3", "dde1.4", "nmake", "tix8.4.3", "*.lib"):
            self.assertIn(parti, TCL_INUTILE, parti)

    def test_it_takes_the_unused_powers_and_leaves_what_the_tool_needs(self):
        """« Non utilisé » est une propriété du code d'aujourd'hui, que la
        relecture doit refaire à chaque version. « Absent » est une
        propriété du livrable, et elle se constate en listant un dossier.
        """
        from tools.build_windows import capacites_a_retirer

        racine = self._runtime_postiche()
        retires = {os.path.relpath(chemin, racine).replace(os.sep, "/")
                   for chemin in capacites_a_retirer(racine)}
        for parti in ("DLLs/_ctypes.pyd", "DLLs/_multiprocessing.pyd",
                      "DLLs/_sqlite3.pyd", "DLLs/_wmi.pyd",
                      "DLLs/winsound.pyd", "Lib/subprocess.py",
                      "Lib/ctypes", "Lib/multiprocessing", "Lib/sqlite3"):
            self.assertIn(parti, retires, parti)
        # Partent aussi : les trois modules natifs que l'interpréteur livré
        # ne charge jamais — mesuré sur une analyse complète.
        for parti in ("DLLs/_decimal.pyd", "DLLs/_uuid.pyd",
                      "DLLs/_zoneinfo.pyd", "Lib/zoneinfo"):
            self.assertIn(parti, retires, parti)
        # Gardés : la lecture d'un .xlsx, la fenêtre, et les deux modules de
        # décompression que « zipfile » importe. Gardés aussi, les modules
        # Python que d'autres importent : « statistics » et « fractions »
        # demandent « decimal », « wave » demande « uuid ». Ils marchent
        # sans leur accélérateur natif, en plus lent.
        for reste in ("DLLs/pyexpat.pyd", "DLLs/_elementtree.pyd",
                      "DLLs/_tkinter.pyd",
                      "DLLs/_hashlib.pyd", "DLLs/_bz2.pyd", "DLLs/_lzma.pyd",
                      "Lib/zipfile.py", "Lib/decimal.py",
                      "Lib/_pydecimal.py", "Lib/uuid.py"):
            self.assertNotIn(reste, retires, reste)

    def test_removing_the_powers_really_removes_them(self):
        from tools.build_windows import retirer_capacites

        racine = self._runtime_postiche()
        retirer_capacites(racine)
        for parti in ("DLLs/_ctypes.pyd", "Lib/subprocess.py", "Lib/ctypes"):
            self.assertFalse(os.path.exists(os.path.join(racine,
                                                         *parti.split("/"))),
                             parti)
        for reste in ("DLLs/pyexpat.pyd", "DLLs/_tkinter.pyd",
                      "Lib/zipfile.py"):
            self.assertTrue(os.path.exists(os.path.join(racine,
                                                        *reste.split("/"))),
                            reste)

    def test_nothing_the_tool_imports_is_on_a_removal_list(self):
        """La preuve que les deux listes ne peuvent pas emporter une pièce
        dont l'outil a besoin : elles sont confrontées à ce qu'il importe
        vraiment, relevé dans le code et non recopié à la main."""
        import ast

        from tools.build_windows import (CAPACITES_DLLS, CAPACITES_LIB,
                                         RESEAU_DLLS, RESEAU_LIB)

        paquet = os.path.join(ROOT, "hr_analytics")
        importes = set()
        for dossier, _sous, fichiers in os.walk(paquet):
            if "__pycache__" in dossier:
                continue
            for nom in fichiers:
                if not nom.endswith(".py"):
                    continue
                with open(os.path.join(dossier, nom), encoding="utf-8") as flux:
                    arbre = ast.parse(flux.read())
                for noeud in ast.walk(arbre):
                    if isinstance(noeud, ast.Import):
                        importes.update(a.name.split(".")[0]
                                        for a in noeud.names)
                    elif isinstance(noeud, ast.ImportFrom) and not noeud.level:
                        if noeud.module:
                            importes.add(noeud.module.split(".")[0])
        self.assertIn("zipfile", importes, "le relevé n'a rien relevé")
        retires = {nom[:-4] if nom.endswith((".pyd", ".dll")) else nom
                   for nom in RESEAU_DLLS + CAPACITES_DLLS}
        retires |= {os.path.basename(nom).removesuffix(".py")
                    for nom in RESEAU_LIB + CAPACITES_LIB}
        # « urllib » reste : seul « urllib.parse » est gardé, et le relevé
        # ne descend pas jusqu'au sous-module.
        for nom in sorted(importes & retires):
            self.assertEqual(nom, "urllib",
                             f"l'outil importe « {nom} », qui est retiré")

    def test_the_fingerprint_sheet_says_what_was_taken_out(self):
        """Ce qui est retiré doit être écrit : une liste de hachages qui
        tait les absences ne prouve rien."""
        import inspect

        from tools import build_windows

        source = inspect.getsource(build_windows.empreintes)
        self.assertIn("RESEAU_DLLS", source)
        self.assertIn("Pile reseau retiree", source)


class TestTheMarkIcon(unittest.TestCase):
    """L'icône est dessinée par une formule, pas posée en pixels."""

    @classmethod
    def setUpClass(cls):
        chemin = os.path.join(ROOT, "packaging", "windows", "marque.ico")
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

    def test_it_draws_the_very_mark_the_window_shows(self):
        """Un outil n'a qu'une identité : l'icône du raccourci ne recopie
        pas la marque de la fenêtre, elle l'appelle."""
        import inspect

        from hr_analytics.ui import logo
        from tools import render_icon

        source = inspect.getsource(render_icon.dessiner)
        self.assertIn("logo.jeton_pixels", source)
        # Le noyau est plein, le coin du cadre est vide : la marque ne
        # touche pas son bord.
        self.assertLess(logo.distance(0.5, 0.5), 0)
        self.assertGreater(logo.distance(0.01, 0.02), 0)

    def test_the_mark_is_white_on_the_slate_token(self):
        """Une icône de raccourci se pose sur n'importe quel fond de
        bureau : elle porte le sien."""
        from hr_analytics.ui.logo import JETON_FOND as ENCRE
        from hr_analytics.ui.logo import JETON_MARQUE as MARQUE
        from tools.render_icon import dessiner

        pixels = dessiner(64)

        def point(x, y):
            return tuple(pixels[(y * 64 + x) * 4:(y * 64 + x) * 4 + 4])

        self.assertEqual(point(32, 32)[3], 255, "le jeton est plein")
        self.assertEqual(point(0, 0)[3], 0, "le coin reste transparent")
        # Au centre : le noyau, donc du blanc franc. Au ras du bord du
        # jeton : l'ardoise.
        self.assertEqual(point(32, 32)[:3], MARQUE, "pas de noyau")
        self.assertEqual(point(32, 4)[:3], ENCRE)

    def test_the_mark_keeps_its_air_inside_the_token(self):
        """Une icône qui remplit son jeton se lit comme une pastille, pas
        comme un symbole : la marque s'arrête bien avant le bord."""
        from hr_analytics.ui import logo

        pixels = logo.jeton_pixels(64)

        def point(x, y):
            return tuple(pixels[(y * 64 + x) * 4:(y * 64 + x) * 4 + 4])

        # L'anneau entre la marque et le bord du jeton : de l'ardoise
        # pleine, sur toute la couronne. Le rayon se déduit du dessin — le
        # bras le plus long, plus son épaisseur — et non d'un nombre
        # recopié qui survivrait au prochain réglage.
        import math
        portee = 64 * logo.JETON_EMPRISE * (logo.BRAS_FIN + logo.TRAIT_FIN)
        bord = 32 - max(64 * 0.02, 0.5)
        rayon = portee + 2
        self.assertLess(rayon, bord - 1, "la marque ne laisse aucun air")
        for degres in range(0, 360, 15):
            angle = math.radians(degres)
            x = int(32 + rayon * math.cos(angle))
            y = int(32 + rayon * math.sin(angle))
            self.assertEqual(point(x, y)[:3], logo.JETON_FOND,
                             "la marque touche le bord du jeton")


class TestTheFolderLauncherCarriesTheMark(unittest.TestCase):
    """Le dossier Windows et l'exécutable unique sont deux livrables : une
    icône posée sur un seul laisse l'autre avec celle de mingw."""

    def test_both_launchers_are_linked_against_the_icon(self):
        import inspect

        from tools import build_windows

        for fabrique in (build_windows.compiler_lanceur,
                         build_windows.compiler_stub):
            source = inspect.getsource(fabrique)
            self.assertIn("compiler_icone(destination)", source,
                          f"{fabrique.__name__} ne pose pas l'icône")
            self.assertIn("objet", source.split("subprocess.run")[1],
                          f"{fabrique.__name__} ne lie pas la ressource")

    def test_the_package_carries_one_state_and_not_two(self):
        """Un audit de septembre livré à côté du dossier du jour le
        contredit sur ce qui a changé depuis. Un lecteur de sécurité qui
        trouve deux affirmations contraires dans le même paquet ne sait
        pas laquelle croire, et il a raison."""
        from tools.build_windows import DOCS_NON_LIVRES

        for nom in DOCS_NON_LIVRES:
            chemin = os.path.join(ROOT, "docs", nom)
            self.assertTrue(os.path.isfile(chemin),
                            f"{nom} devrait rester au dépôt")
            with open(chemin, encoding="utf-8") as flux:
                tete = "".join(flux.readlines()[:12])
            self.assertIn("Document historique", tete,
                          f"{nom} ne se signale pas comme dépassé")
        # Le dossier courant, lui, est livré. Le relevé de dépendances
        # aussi : c'est la première pièce qu'une revue réclame.
        self.assertNotIn("DOSSIER-RSSI.md", DOCS_NON_LIVRES)
        self.assertNotIn("GUIDE_UTILISATEUR.md", DOCS_NON_LIVRES)
        self.assertNotIn("DEPENDANCES.md", DOCS_NON_LIVRES)

    def test_every_dated_audit_stays_at_the_repository(self):
        """Un audit daté décrit un état révolu : il ne part pas avec le
        paquet, mais il ne disparaît pas non plus."""
        import glob

        from tools.build_windows import DOCS_NON_LIVRES

        for chemin in glob.glob(os.path.join(ROOT, "docs", "AUDIT-*.md")):
            self.assertIn(os.path.basename(chemin), DOCS_NON_LIVRES,
                          f"{os.path.basename(chemin)} partirait dans le paquet")


class TestTheOperatingManual(unittest.TestCase):
    """Le mode opératoire voyage avec l'outil, et se lit hors ligne.

    Un mode operatoire qui ne suit pas l'outil est un mode operatoire que
    personne ne retrouve. Et il part chez un service RH : il ne doit porter
    aucune donnee reelle, ni rien aller chercher sur un reseau.
    """

    CHEMIN = os.path.join(ROOT, "docs", "MODE-OPERATOIRE.html")

    def setUp(self):
        if not os.path.isfile(self.CHEMIN):
            self.skipTest("mode opératoire absent")
        with open(self.CHEMIN, encoding="utf-8") as source:
            self.page = source.read()

    def test_it_ships_with_the_package(self):
        """Il est dans « docs », et rien ne l'exclut de la livraison."""
        from tools.build_windows import DOCS_NON_LIVRES

        self.assertNotIn("MODE-OPERATOIRE.html", DOCS_NON_LIVRES)

    def test_it_fetches_nothing_from_a_network(self):
        """Une police ou une feuille de style distante ferait d'un document
        hors ligne un document qui ne s'affiche qu'en ligne."""
        externes = re.findall(r'(?:src|href)="(?!#|data:)([^"]+)"', self.page)
        self.assertEqual(externes, [])
        for protocole in ("http://", "https://", "//cdn"):
            self.assertNotIn(protocole, self.page)

    def test_the_screenshots_travel_inside_the_page(self):
        """Un dossier d'images a cote se perd a la premiere transmission."""
        self.assertGreaterEqual(self.page.count("data:image/png;base64,"), 10)

    def test_it_carries_no_real_population(self):
        """Les captures sont faites sur une population inventee, et le
        document le dit."""
        from tests.test_privacy_and_pipeline import (
            TestNoRealCompanyLeaksIntoTheSource as temoin)

        for nom in temoin.RETIREES:
            self.assertNotIn(nom, self.page)
        self.assertIn("population inventée", self.page)
