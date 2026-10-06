#!/usr/bin/env python3
"""Cherche le code mort : ce qui est defini et que plus rien n'appelle.

    python3 tools/find_dead_code.py

Deux listes, et elles ne veulent pas dire la meme chose.

« Reference nulle part » : plus rien n'y touche, pas meme un test. C'est
du code mort, et il peut partir.

« Reference seulement par les tests » : le code existe, il est teste, et
aucun ecran ni aucun document ne l'appelle. Ce n'est PAS du code mort —
c'est une fonctionnalite debranchee. La supprimer detruit du travail ; la
garder laisse croire qu'elle sert. Les deux se decident, elles ne se
devinent pas.

La reference dans une chaine de caracteres compte : l'interface Tk designe
des rappels par leur nom, et la configuration nomme des champs. Compter
large produit des faux negatifs ; compter etroit supprimerait du code
vivant. On compte large.
"""
import ast, os, collections

PAQUET = "hr_analytics"
ZONES = {"paquet": [PAQUET], "outils": ["tools"], "tests": ["tests"]}

def fichiers(racines):
    for racine in racines:
        for d, _s, fs in os.walk(racine):
            if "__pycache__" in d:
                continue
            for n in sorted(fs):
                if n.endswith(".py"):
                    yield os.path.join(d, n)

definitions = {}
for chemin in fichiers([PAQUET]):
    arbre = ast.parse(open(chemin, encoding="utf-8").read(), chemin)
    for noeud in arbre.body:
        if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions[noeud.name] = (chemin, noeud.lineno, "fonction")
        elif isinstance(noeud, ast.ClassDef):
            definitions[noeud.name] = (chemin, noeud.lineno, "classe")
        elif isinstance(noeud, ast.Assign):
            for c in noeud.targets:
                if isinstance(c, ast.Name) and c.id.isupper():
                    definitions[c.id] = (chemin, noeud.lineno, "constante")

refs = collections.defaultdict(lambda: collections.Counter())
for zone, racines in ZONES.items():
    for chemin in fichiers(racines):
        texte = open(chemin, encoding="utf-8").read()
        arbre = ast.parse(texte, chemin)
        for noeud in ast.walk(arbre):
            nom = None
            if isinstance(noeud, ast.Name):
                nom = noeud.id
            elif isinstance(noeud, ast.Attribute):
                nom = noeud.attr
            elif isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef,
                                    ast.ClassDef)):
                continue          # la definition elle-meme ne compte pas
            elif isinstance(noeud, (ast.Import, ast.ImportFrom)):
                for a in noeud.names:
                    refs[a.name.split(".")[-1]][zone] += 1
                    if a.asname:
                        refs[a.asname][zone] += 1
                continue
            elif isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
                for mot in noeud.value.replace(".", " ").replace(",", " ").split():
                    refs[mot][zone] += 1
                continue
            if nom:
                refs[nom][zone] += 1
        # Les affectations de constantes ne comptent pas comme emploi.
        for noeud in arbre.body:
            if isinstance(noeud, ast.Assign):
                for c in noeud.targets:
                    if isinstance(c, ast.Name):
                        refs[c.id][zone] -= 1

morts, tests_seuls = [], []
for nom, (chemin, ligne, genre) in sorted(definitions.items()):
    if nom.startswith("__"):
        continue
    e = refs[nom]
    vivant = e["paquet"] + e["outils"]
    if vivant <= 0 and e["tests"] <= 0:
        morts.append((chemin, ligne, genre, nom))
    elif vivant <= 0:
        tests_seuls.append((chemin, ligne, genre, nom, e["tests"]))

print(f"definitions examinees : {len(definitions)}")
print(f"\n=== REFERENCE NULLE PART, tests compris ({len(morts)})")
for c, l, g, n in morts:
    print(f"  {c}:{l}  {g:9} {n}")
print(f"\n=== REFERENCE SEULEMENT PAR LES TESTS ({len(tests_seuls)})")
for c, l, g, n, t in tests_seuls:
    print(f"  {c}:{l}  {g:9} {n}")
