"""Garde-fous de securite verifies sur le code source lui-meme.

Ces tests echouent si une evolution future reintroduit une construction
interdite par les contraintes IT / cyber du projet.
"""

import ast
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE = os.path.join(ROOT, "compensation_analytics")

FORBIDDEN_IMPORTS = {
    "socket", "ssl", "http", "urllib", "urllib3", "requests", "ftplib",
    "smtplib", "telnetlib", "xmlrpc", "subprocess", "ctypes", "winreg",
    "multiprocessing", "pickle", "marshal", "shelve",
}
# Appels nus interdits (execution de code construit dynamiquement).
FORBIDDEN_NAMES = {"eval", "exec", "compile", "__import__"}
# Appels sur attribut interdits (creation de processus). `re.compile` etant
# legitime, `compile` n'est surveille que sous sa forme nue.
FORBIDDEN_ATTRIBUTES = {"system", "popen", "spawnl", "spawnv", "execv", "fork"}


def source_files():
    for base, _, names in os.walk(PACKAGE):
        for name in names:
            if name.endswith(".py"):
                yield os.path.join(base, name)


class TestNoForbiddenConstructs(unittest.TestCase):
    def test_no_network_or_process_imports(self):
        for path in source_files():
            with open(path, encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=path)
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".")[0]]
                for name in names:
                    self.assertNotIn(
                        name, FORBIDDEN_IMPORTS,
                        f"import interdit \"{name}\" dans {os.path.relpath(path, ROOT)}",
                    )

    def test_no_dynamic_code_execution(self):
        for path in source_files():
            with open(path, encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=path)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                target = node.func
                if isinstance(target, ast.Name):
                    name, forbidden = target.id, FORBIDDEN_NAMES
                elif isinstance(target, ast.Attribute):
                    name, forbidden = target.attr, FORBIDDEN_ATTRIBUTES
                else:
                    continue
                self.assertNotIn(
                    name, forbidden,
                    f"appel interdit \"{name}\" dans {os.path.relpath(path, ROOT)}",
                )

    def test_no_third_party_dependency(self):
        """Le moteur ne doit importer que la bibliotheque standard."""
        import sys
        standard = set(sys.stdlib_module_names)
        for path in source_files():
            with open(path, encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level:  # import relatif interne
                        continue
                    modules = [node.module.split(".")[0]] if node.module else []
                else:
                    continue
                for module in modules:
                    if module == "compensation_analytics":
                        continue
                    self.assertIn(
                        module, standard,
                        f"dependance externe \"{module}\" dans "
                        f"{os.path.relpath(path, ROOT)}",
                    )


if __name__ == "__main__":
    unittest.main()


class TestCommandLineInterfaceStaysAscii(unittest.TestCase):
    """Les noms d'options, de sous-commandes et les valeurs acceptees restent
    en ASCII.

    Les libelles affiches sont accentues, mais une option nommee
    `--date-référence` obligerait l'utilisateur a taper un accent dans un
    terminal, casserait les scripts existants et depend de la configuration
    clavier du poste. Ce test a ete ajoute apres avoir introduit deux fois
    l'erreur.
    """

    def _parser_strings(self):
        import argparse
        from compensation_analytics.cli import build_parser

        names, choices = [], []

        def walk(parser):
            for action in parser._actions:
                names.extend(action.option_strings)
                if action.choices:
                    for choice in action.choices:
                        if isinstance(choice, str):
                            choices.append(choice)
                        if isinstance(action.choices, dict):  # sous-commandes
                            walk(action.choices[choice])
        walk(build_parser())
        return names, choices

    def test_option_names_are_ascii(self):
        names, _ = self._parser_strings()
        self.assertTrue(names)
        for name in names:
            self.assertTrue(name.isascii(), f"option non ASCII : {name}")

    def test_subcommands_and_accepted_values_are_ascii(self):
        _, choices = self._parser_strings()
        self.assertIn("analyse", choices)
        self.assertIn("controle", choices)
        self.assertIn("synthese", choices)
        for choice in choices:
            self.assertTrue(choice.isascii(), f"valeur non ASCII : {choice}")

    def test_generated_file_names_are_ascii(self):
        """Les noms de fichiers produits circulent par courriel et par partage
        reseau : ils restent en ASCII."""
        import inspect
        from compensation_analytics import cli
        source = inspect.getsource(cli.command_analyse)
        for pattern in ("restitution-", "synthese-", "slides-", "analyse-",
                        "manifeste-"):
            self.assertIn(pattern, source)
