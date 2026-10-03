"""L'organigramme : la structure d'une equipe, et la liste de ses salaries.

Aucune donnee RH reelle : les matricules sont des lettres, les montants des
nombres ronds.

Trois choses tiennent ce fichier, et ce sont les trois par lesquelles un
organigramme peut mentir.

La premiere est le **rattachement sous filtre**. Un filtre retire des
salaries de tous les onglets ; s'il retire un chef de service, ses trente
subordonnes ne doivent ni disparaitre, ni se retrouver detaches. Ils se
rattachent au premier responsable encore present au-dessus d'eux, et
l'effectif affiche reste celui que les autres onglets comptent.

La deuxieme est le **seuil de confidentialite**. Un organigramme qui
afficherait la mediane d'une equipe de trois serait le chemin le plus court
vers le salaire du voisin.

La troisieme est l'**identite**. Elle n'entre pas dans les donnees : la case
et la ligne portent un matricule, et c'est la fenetre qui y rapproche un nom,
a l'ecran et seulement si le parametrage l'y autorise.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_insight.core import org
from hr_insight.core.hierarchy import Tree
from hr_insight.core.normalize import Employee, Population
from tests.support import make_config


def make(links, salaire=40000):
    """Population minimale : (matricule, matricule du manager)."""
    return Population([
        Employee(row_number=index + 1, employee_id=key, manager=parent,
                 job="Poste", gender="F" if index % 2 else "H",
                 tenure_years=5.0, base_salary=salaire + index * 1000)
        for index, (key, parent) in enumerate(links)
    ])


#: D encadre deux chefs, C1 et C2, qui portent chacun quatre collaborateurs.
#: Un effectif qui passe le seuil de publication par branche.
LIENS = ([("D", ""), ("C1", "D"), ("C2", "D")]
         + [(f"A{index}", "C1") for index in range(6)]
         + [(f"B{index}", "C2") for index in range(6)])
ÉQUIPE = make(LIENS)


class OrgCase(unittest.TestCase):
    def setUp(self):
        self.tree = Tree(ÉQUIPE)
        self.config = make_config()

    def nodes(self, **kwargs):
        return org.chart_nodes(self.tree, "D", self.config, **kwargs)

    def rows(self, **kwargs):
        return org.member_rows(self.tree, "D", self.config, **kwargs)


class TestTheStructure(OrgCase):
    """Ce que le dessin montre : les responsables, et le compte des autres."""

    def test_only_managers_get_a_box(self):
        """Quinze personnes, trois cases. Une case par salarie rendrait le
        dessin illisible, et la structure y disparaitrait."""
        racine = self.nodes()
        self.assertEqual(racine["manager"], "D")
        self.assertEqual([enfant["manager"] for enfant in racine["children"]],
                         ["C1", "C2"])
        for enfant in racine["children"]:
            self.assertEqual(enfant["children"], [])

    def test_those_without_a_team_are_counted_under_their_manager(self):
        """Ils ne disparaissent pas : ils sont comptes."""
        racine = self.nodes()
        par_cle = {enfant["manager"]: enfant for enfant in racine["children"]}
        self.assertEqual(par_cle["C1"]["individuals"], 6)
        self.assertEqual(par_cle["C1"]["direct"], 6)
        self.assertEqual(par_cle["C1"]["total"], 6)

    def test_the_root_carries_the_whole_team(self):
        racine = self.nodes()
        self.assertEqual(racine["total"], 14)
        self.assertEqual(racine["direct"], 2)
        # Ses deux rattaches directs encadrent : aucun n'est compte en chip.
        self.assertEqual(racine["individuals"], 0)

    def test_direct_only_stops_at_the_first_level(self):
        """« Equipe directe seulement » analyse deux personnes : dessiner les
        douze autres tromperait sur la population analysee."""
        racine = self.nodes(direct_only=True)
        self.assertEqual(racine["children"], [])
        self.assertEqual(racine["individuals"], 2)
        self.assertEqual(racine["total"], 2)

    def test_an_unknown_manager_draws_nothing(self):
        self.assertIsNone(org.chart_nodes(self.tree, "INCONNU", self.config))
        self.assertEqual(org.member_rows(self.tree, "INCONNU", self.config),
                         [])


class TestTheListOfPeople(OrgCase):
    """Ce que la liste nomme, et dans quel ordre."""

    def test_everyone_in_the_team_has_a_line(self):
        lignes = self.rows()
        self.assertEqual(len(lignes), 15)
        self.assertEqual(lignes[0]["employee_id"], "D")
        self.assertEqual(lignes[0]["level"], 0)

    def test_the_order_follows_the_tree_and_not_the_alphabet(self):
        """Chaque responsable est suivi de son equipe : c'est l'ordre dans
        lequel se lit un organigramme, et il porte le rattachement sans
        qu'on ait a relire une colonne."""
        cles = [ligne["employee_id"] for ligne in self.rows()]
        self.assertEqual(cles[0], "D")
        self.assertEqual(cles[1], "C1")
        self.assertEqual(cles[2:8], [f"A{index}" for index in range(6)])
        self.assertEqual(cles[8], "C2")

    def test_each_line_says_what_it_carries(self):
        ligne = next(row for row in self.rows() if row["employee_id"] == "C1")
        self.assertEqual(ligne["manager"], "D")
        self.assertEqual(ligne["manages"], 6)
        self.assertEqual(ligne["team"], 6)
        self.assertEqual(ligne["level"], 1)

    def test_no_name_ever_reaches_the_rows(self):
        """L'identite n'est pas dans les donnees : c'est ce qui garantit
        qu'aucun document produit ne peut en porter."""
        for ligne in self.rows():
            for valeur in ligne.values():
                self.assertNotIn("NOM", str(valeur))
            self.assertNotIn("identity", ligne)


class TestTheFiltersApplyHereToo(OrgCase):
    """Le point par lequel un organigramme ment le plus facilement.

    Les autres onglets comptent la population filtree. Un organigramme qui
    montrerait encore les salaries ecartes ferait mentir l'effectif affiche
    a cote de lui.
    """

    def keep_without(self, *absents):
        return {employee.employee_id for employee in ÉQUIPE
                if employee.employee_id not in absents}

    def test_a_filtered_out_employee_leaves_the_chart(self):
        lignes = self.rows(keep=self.keep_without("A0", "A1"))
        cles = [ligne["employee_id"] for ligne in lignes]
        self.assertNotIn("A0", cles)
        self.assertEqual(len(lignes), 13)

    def test_a_filtered_out_manager_does_not_detach_his_team(self):
        """C1 retire, ses six collaborateurs restent — rattaches a D.

        Sans ce rattrapage, ils deviendraient des racines orphelines : le
        dessin perdrait six personnes que l'onglet d'a cote compte toujours.
        """
        keep = self.keep_without("C1")
        lignes = self.rows(keep=keep)
        self.assertEqual(len(lignes), 14)
        for index in range(6):
            ligne = next(row for row in lignes
                         if row["employee_id"] == f"A{index}")
            self.assertEqual(ligne["manager"], "D")
            self.assertEqual(ligne["level"], 1)
        racine = self.nodes(keep=keep)
        self.assertEqual(racine["total"], 13)
        self.assertEqual([enfant["manager"] for enfant in racine["children"]],
                         ["C2"])
        # Les six rattaches sont comptes sous la case de D, pas perdus.
        self.assertEqual(racine["individuals"], 6)

    def test_the_headcount_matches_what_was_analysed(self):
        keep = self.keep_without("C1", "B0")
        resume = org.summary(self.nodes(keep=keep), self.rows(keep=keep))
        self.assertEqual(resume["headcount"], len(keep))

    def test_the_chosen_manager_stays_the_root_even_if_filtered_out(self):
        """L'equipe demandee reste celle qu'on voit. Mais il n'est pas
        compte dans un effectif dont il ne fait plus partie."""
        keep = self.keep_without("D")
        lignes = self.rows(keep=keep)
        self.assertEqual(lignes[0]["employee_id"], "D")
        self.assertTrue(lignes[0]["out_of_scope"])
        self.assertFalse(any(ligne["out_of_scope"] for ligne in lignes[1:]))
        self.assertEqual(org.summary(self.nodes(keep=keep), lignes)["headcount"],
                         14)


class TestConfidentiality(OrgCase):
    """Un organigramme ne doit pas devenir le chemin vers le salaire du
    voisin."""

    def test_a_team_below_the_threshold_shows_its_size_and_not_its_pay(self):
        petite = make([("P", ""), ("Q", "P"), ("R", "P")])
        arbre = Tree(petite)
        racine = org.chart_nodes(arbre, "P", self.config)
        self.assertEqual(racine["total"], 2)
        self.assertIsNone(racine["amount"])
        self.assertTrue(racine["masked"])

    def test_individual_amounts_fall_with_the_team(self):
        petite = make([("P", ""), ("Q", "P"), ("R", "P")])
        lignes = org.member_rows(Tree(petite), "P", self.config)
        self.assertEqual(len(lignes), 3)
        self.assertTrue(all(ligne["amount"] is None for ligne in lignes))
        self.assertTrue(all(ligne["masked"] for ligne in lignes))

    def test_a_team_above_the_threshold_publishes_its_median(self):
        racine = self.nodes()
        self.assertFalse(racine["masked"])
        self.assertIsNotNone(racine["amount"])

    def test_the_threshold_is_the_configured_one(self):
        """Il n'est pas ecrit dans ce module : il vient du parametrage, et
        un seuil releve doit faire tomber une mediane qui passait."""
        strict = make_config({"privacy_parameters.min_headcount_publish": 20})
        racine = org.chart_nodes(self.tree, "D", strict)
        self.assertTrue(racine["masked"])
        self.assertIsNone(racine["amount"])

    def test_without_any_working_time_the_amounts_are_the_paid_ones(self):
        """La colonne du temps de travail n'est pas obligatoire.

        Exiger un ETP pour publier masquerait toute la page sur un fichier
        qui n'en porte pas — c'est-a-dire faute d'une donnee absente, et non
        au nom d'un seuil. On retombe sur le montant verse, et la page
        l'annonce plutot que de laisser croire a une base qu'elle n'applique
        pas. C'est la regle de la page des ecarts.
        """
        population = make([("M", "")] + [(f"T{index}", "M")
                                         for index in range(6)])
        for employee in population:
            employee.fte = None
            employee.base_salary = 30000
        racine = org.chart_nodes(Tree(population), "M", self.config)
        self.assertFalse(racine["full_time"])
        self.assertEqual(racine["amount"], 30000)

    def test_an_unknown_working_time_leaves_the_calculation(self):
        """Des que le temps de travail est connu quelque part, le supposer
        plein ailleurs serait l'erreur meme que ce calcul corrige."""
        population = make([("M", "")] + [(f"T{index}", "M")
                                         for index in range(8)])
        for index, employee in enumerate(population):
            employee.base_salary = 30000
            employee.fte = None if index > 5 else 1.0
        racine = org.chart_nodes(Tree(population), "M", self.config)
        self.assertTrue(racine["full_time"])
        self.assertEqual(racine["amount"], 30000)

    def test_the_median_is_computed_on_full_time_amounts(self):
        """Comme partout ailleurs : la mediane d'une equipe ou l'on travaille
        a 80 % ne veut rien dire autrement."""
        population = make([("M", "")] + [(f"T{index}", "M")
                                         for index in range(6)], salaire=0)
        for employee in population:
            employee.base_salary = 20000
            employee.fte = 0.5
        racine = org.chart_nodes(Tree(population), "M", self.config)
        self.assertEqual(racine["amount"], 40000)


class TestTheSummary(OrgCase):
    def test_it_counts_levels_managers_and_span(self):
        resume = org.summary(self.nodes(), self.rows())
        self.assertEqual(resume["headcount"], 15)
        self.assertEqual(resume["levels"], 3)
        self.assertEqual(resume["managers"], 3)
        # D encadre 2, C1 et C2 en encadrent 6 chacun.
        self.assertAlmostEqual(resume["span"], (2 + 6 + 6) / 3)

    def test_a_team_without_any_manager_has_no_span(self):
        seul = make([("S", "")])
        resume = org.summary(org.chart_nodes(Tree(seul), "S", self.config),
                             org.member_rows(Tree(seul), "S", self.config))
        self.assertIsNone(resume["span"])
        self.assertEqual(resume["levels"], 1)


if __name__ == "__main__":
    unittest.main()
