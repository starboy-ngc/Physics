"""Aucun tiret cadratin dans ce que l'outil montre ou livre.

Le tiret long servait d'incise partout : dans les phrases de l'ecran,
dans les documents produits, dans les guides. Il a ete retire a la
demande de l'utilisatrice, qui le trouvait inutile et laid. Ce test
l'empeche de revenir par une phrase ajoutee sans y penser.

Les docstrings et les commentaires du code ne sont pas des textes
montres : ils ne sont pas concernes. La table de remplacement du PDF,
qui traduit un tiret venu d'un fichier en trait court, doit le nommer :
elle fait exception.
"""
import ast
import glob
import os
import unittest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIRET = "—"

#: Le seul module ou le tiret a sa place : il y est traduit, pas affiche.
EXCEPTION = os.path.join("hr_analytics", "io", "pdf_writer.py")


def _docstrings(tree: ast.AST) -> set:
    """Les noeuds de docstring, a ne pas inspecter."""
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                ids.add(id(body[0].value))
    return ids


def strings_with_a_dash(path: str):
    """Les chaines du module qui portent un tiret cadratin, hors docstrings."""
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    skip = _docstrings(tree)
    return sorted({node.lineno for node in ast.walk(tree)
                   if isinstance(node, ast.Constant)
                   and isinstance(node.value, str)
                   and TIRET in node.value and id(node) not in skip})


class TestNoEmDashInWhatIsShown(unittest.TestCase):
    def test_the_package_strings_carry_none(self):
        fautifs = {}
        for path in sorted(glob.glob(os.path.join(RACINE, "hr_analytics",
                                                  "**", "*.py"),
                                     recursive=True)):
            if path.endswith(EXCEPTION):
                continue
            lignes = strings_with_a_dash(path)
            if lignes:
                fautifs[os.path.relpath(path, RACINE)] = lignes
        self.assertEqual(fautifs, {})

    def test_the_documents_carry_none(self):
        fautifs = {}
        chemins = ([os.path.join(RACINE, "README.md")]
                   + glob.glob(os.path.join(RACINE, "docs", "*.md"))
                   + glob.glob(os.path.join(RACINE, "docs", "*.html"))
                   + glob.glob(os.path.join(RACINE, "config", "*.json")))
        for path in sorted(chemins):
            with open(path, encoding="utf-8") as handle:
                texte = handle.read()
            if TIRET in texte:
                fautifs[os.path.relpath(path, RACINE)] = texte.count(TIRET)
        self.assertEqual(fautifs, {})


if __name__ == "__main__":
    unittest.main()
