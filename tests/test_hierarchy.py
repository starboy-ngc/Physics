"""Arbre hierarchique reconstruit depuis la seule colonne « manager ».

Aucune donnee RH reelle : les matricules sont des lettres.

Deux verites tiennent ce fichier. La premiere est que l'equipe *totale*
d'un responsable n'est pas son equipe directe : c'est d'elle qu'il repond,
et elle ne se lit sur aucune colonne. La seconde est qu'un fichier de paie
mal tenu ne doit jamais figer l'outil — un cycle « A encadre B qui encadre
A » ferait tourner sans fin toute descente dans l'arbre.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compensation_analytics.core.hierarchy import (
    Tree, team_population, team_rows,
)
from compensation_analytics.core.normalize import Employee, Population


def make(links, salary=40000):
    """Population minimale : (matricule, matricule du manager)."""
    return Population([
        Employee(row_number=index + 1, employee_id=key, manager=parent,
                 job="Poste", base_salary=salary)
        for index, (key, parent) in enumerate(links)
    ])


#: A encadre B et C ; B encadre D et E ; D encadre F.
SANE = make([("A", ""), ("B", "A"), ("C", "A"),
             ("D", "B"), ("E", "B"), ("F", "D")])


class TestTeams(unittest.TestCase):
    def setUp(self):
        self.tree = Tree(SANE)

    def test_direct_team_is_the_line_below(self):
        self.assertEqual([person.employee_id for person in
                          self.tree.direct("B")], ["D", "E"])

    def test_total_team_goes_down_to_the_last_level(self):
        """La distinction qui justifie le module : B encadre deux personnes
        directement, trois en tout."""
        self.assertEqual(sorted(person.employee_id for person in
                                self.tree.total("B")), ["D", "E", "F"])

    def test_the_top_manager_carries_everyone(self):
        self.assertEqual(len(self.tree.total("A")), 5)

    def test_someone_without_a_team_has_none(self):
        self.assertEqual(self.tree.total("F"), [])

    def test_an_unknown_identifier_yields_nothing(self):
        self.assertEqual(self.tree.direct("INCONNU"), [])
        self.assertEqual(self.tree.total("INCONNU"), [])

    def test_managers_are_those_with_at_least_one_report(self):
        self.assertEqual(self.tree.managers(), ["A", "B", "D"])

    def test_depth_counts_from_the_top(self):
        self.assertEqual([self.tree.depth(key) for key in "ABDF"],
                         [1, 2, 3, 4])

    def test_the_line_reads_from_the_top_down(self):
        self.assertEqual(self.tree.line("F"), ["A", "B", "D", "F"])

    def test_the_summary_describes_a_sound_file(self):
        self.assertEqual(self.tree.summary(), {
            "employees": 6, "managers": 3, "roots": 1, "depth": 4,
            "unknown_managers": [], "cycles": [], "duplicates": [],
        })


class TestTeamPopulation(unittest.TestCase):
    """Ce qui est effectivement analyse quand on demande « l'equipe de X »."""

    def setUp(self):
        self.tree = Tree(SANE)

    def _ids(self, **kwargs):
        population = team_population(SANE, self.tree, "B", **kwargs)
        return sorted(person.employee_id for person in population)

    def test_the_manager_is_part_of_the_team_by_default(self):
        """« La remuneration de l'equipe de B » comprend celle de B."""
        self.assertEqual(self._ids(), ["B", "D", "E", "F"])

    def test_the_manager_can_be_left_out(self):
        self.assertEqual(self._ids(include_manager=False), ["D", "E", "F"])

    def test_the_direct_team_stops_one_level_below(self):
        self.assertEqual(self._ids(direct_only=True), ["B", "D", "E"])

    def test_the_result_is_analysable_like_any_population(self):
        population = team_population(SANE, self.tree, "B")
        self.assertEqual(population.source_name, SANE.source_name)
        self.assertEqual(population.mapped_fields, SANE.mapped_fields)


class TestTeamRows(unittest.TestCase):
    def test_each_manager_gets_its_two_headcounts(self):
        rows = {row["manager"]: row for row in team_rows(SANE, Tree(SANE))}
        self.assertEqual(sorted(rows), ["A", "B", "D"])
        self.assertEqual((rows["B"]["direct"], rows["B"]["total"]), (2, 3))
        self.assertEqual((rows["A"]["direct"], rows["A"]["total"]), (2, 5))

    def test_the_list_reads_from_the_top(self):
        self.assertEqual([row["manager"] for row in
                          team_rows(SANE, Tree(SANE))], ["A", "B", "D"])

    def test_an_unknown_key_is_skipped_rather_than_raising(self):
        rows = team_rows(SANE, Tree(SANE), keys=["B", "INCONNU"])
        self.assertEqual([row["manager"] for row in rows], ["B"])


class TestBrokenFiles(unittest.TestCase):
    """Un export incoherent est frequent. Il ne doit jamais faire lever."""

    def test_a_cycle_is_broken_and_named(self):
        tree = Tree(make([("X", "Y"), ("Y", "X")]))
        self.assertEqual(tree.cycles, ["X", "Y"])
        self.assertEqual(sorted(tree.roots), ["X", "Y"])

    def test_reading_a_cycle_terminates(self):
        """Sans rupture, total() et line() tourneraient sans fin."""
        tree = Tree(make([("X", "Y"), ("Y", "X"), ("Z", "X")]))
        self.assertEqual([person.employee_id for person in tree.total("X")],
                         ["Z"])
        self.assertEqual(tree.line("X"), ["X"])

    def test_a_cycle_member_is_a_root_at_every_reading(self):
        """Le defaut corrige : la construction declarait X racine, mais
        depth() suivait encore la colonne du fichier et repondait 2."""
        tree = Tree(make([("X", "Y"), ("Y", "X")]))
        self.assertEqual(tree.depth("X"), 1)

    def test_someone_managing_themselves_becomes_a_root(self):
        tree = Tree(make([("W", "W")]))
        self.assertEqual(tree.roots, ["W"])
        self.assertEqual(tree.depth("W"), 1)

    def test_an_absent_manager_is_reported_and_the_report_kept(self):
        """Mieux vaut un arbre a plusieurs racines qu'un salarie perdu."""
        tree = Tree(make([("A", ""), ("Z", "ABSENT")]))
        self.assertEqual(tree.summary()["unknown_managers"], ["ABSENT"])
        self.assertIn("Z", tree.roots)
        self.assertIn("Z", tree.employees)

    def test_a_repeated_identifier_is_reported_and_counted_once(self):
        tree = Tree(make([("A", ""), ("A", "")]))
        self.assertEqual(tree.summary()["duplicates"], ["A"])
        self.assertEqual(tree.summary()["employees"], 1)

    def test_a_row_without_an_identifier_is_ignored(self):
        tree = Tree(make([("A", ""), ("", "A")]))
        self.assertEqual(list(tree.employees), ["A"])

    def test_an_empty_population_has_an_empty_tree(self):
        self.assertEqual(Tree(Population([])).summary()["employees"], 0)

    def test_a_file_without_the_column_is_flat(self):
        """La colonne n'est pas obligatoire : tout le monde est racine."""
        tree = Tree(make([("A", ""), ("B", ""), ("C", "")]))
        self.assertEqual(tree.managers(), [])
        self.assertEqual(len(tree.roots), 3)
        self.assertEqual(tree.summary()["depth"], 1)


class TestScale(unittest.TestCase):
    def test_a_deep_chain_is_read_without_recursion(self):
        """Mille niveaux : une descente recursive depasserait la pile."""
        links = [("N0", "")] + [(f"N{i}", f"N{i - 1}") for i in range(1, 1000)]
        tree = Tree(make(links))
        self.assertEqual(tree.depth("N999"), 1000)
        self.assertEqual(len(tree.total("N0")), 999)


if __name__ == "__main__":
    unittest.main()
