#!/usr/bin/env python3
"""Éprouve la stabilité d'affichage de la fenêtre.

    python3 tools/check_layout.py            # passage complet
    python3 tools/check_layout.py --rapide   # la bande critique seulement

Une page qui se redispose peut ne jamais se poser. Le cas vu en vrai :
l'accord de la vue d'ensemble agrandissait les graphiques pour remplir la
hauteur, ce qui faisait apparaître l'ascenseur, qui prenait seize pixels
de large, ce qui redemandait un accord, qui rendait la place — et ainsi
de suite, cent fois par seconde. La fenêtre tremblait, et finissait par
ne plus répondre du tout.

Cet outil cherche ce défaut-là, et il le cherche en mesurant :

1. *Est-ce que ça se pose ?* Après chaque changement de page ou de
   taille, on laisse une seconde, puis on compte ce qui bouge encore. Une
   page posée ne produit plus rien.
2. *Est-ce que la file d'affichage se vide ?* Une boucle serrée empêche
   « update() » de rendre la main : une alarme l'attrape.
3. *Est-ce que le chemin compte ?* Agrandir la fenêtre puis la ramener à
   sa taille doit redonner exactement la même page. Sinon, une mesure
   quelque part ne part pas d'une base fixe.

Il demande un affichage : sous Linux sans écran, « xvfb-run -a python3
tools/check_layout.py » suffit. Rien n'est écrit nulle part — la
configuration est prise dans un dossier temporaire.
"""

from __future__ import annotations

import argparse
import collections
import os
import signal
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

#: Au-delà de ce nombre de bascules d'ascenseur avant de se poser, la page
#: s'agite : ce n'est pas encore une boucle, mais ce n'est plus un simple
#: ajustement.
AGITATION = 20

#: Temps laissé à la page pour se poser, puis temps d'observation. Une
#: bascule qui survient dans la seconde d'observation est un symptôme :
#: plus personne ne touche à rien.
POSE = 0.6
OBSERVATION = 1.0

#: Au-delà, « update() » est considéré comme bloqué par une boucle.
BLOCAGE = 6.0


class Boucle(Exception):
    """La file d'affichage ne se vide pas."""


def _compter_les_ascenseurs():
    """Remplace « pack » et « pack_forget » par des versions qui comptent."""
    from tkinter import ttk

    compte = collections.Counter()
    pack, forget = ttk.Scrollbar.pack, ttk.Scrollbar.pack_forget

    def _pack(self, *args, **kwargs):
        compte.update(["pack"])
        return pack(self, *args, **kwargs)

    def _forget(self, *args, **kwargs):
        compte.update(["forget"])
        return forget(self, *args, **kwargs)

    ttk.Scrollbar.pack, ttk.Scrollbar.pack_forget = _pack, _forget
    return compte


class Banc:
    """Une fenêtre chargée d'un fichier d'essai, et de quoi l'éprouver."""

    def __init__(self, lignes: int = 400):
        self.compte = _compter_les_ascenseurs()
        from hr_analytics.core.config import write_default_configuration
        import tools.generate_sample_population as population

        dossier = tempfile.mkdtemp()
        self.source = os.path.join(dossier, "population.xlsx")
        sys.argv = ["", "--rows", str(lignes), "--seed", "11",
                    "--output", self.source, "--clean"]
        population.main()
        reglages = tempfile.mkdtemp()
        write_default_configuration(reglages)

        from hr_analytics.ui.app import Application

        signal.signal(signal.SIGALRM, self._alarme)
        self.app = Application(config_dir=reglages)
        self.incidents = []
        self.essais = 0
        self.app.report_callback_exception = lambda *exc: self.incidents.append(
            f"exception : {exc[0].__name__}: {exc[1]}")

    @staticmethod
    def _alarme(_signum, _frame):
        raise Boucle("la file d'affichage ne se vide pas")

    def battre(self, secondes: float) -> None:
        fin = time.time() + secondes
        while time.time() < fin:
            signal.setitimer(signal.ITIMER_REAL, BLOCAGE)
            try:
                self.app.update()
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0.0)
            time.sleep(0.005)

    def charger(self) -> None:
        from hr_analytics.ui import app as module

        ouvrir = module.filedialog.askopenfilename
        module.filedialog.askopenfilename = lambda **_k: self.source
        try:
            self.app.geometry("1400x900+0+0")
            self.app.update()
            self.app.choose_file()
            self.app.update()
        finally:
            module.filedialog.askopenfilename = ouvrir
        self.analyser()

    def analyser(self) -> None:
        self.app.run_analysis()
        limite = time.time() + 180
        while self.app.result is None and time.time() < limite:
            self.app.update()
            time.sleep(0.02)
        self.battre(0.4)

    # ----------------------------------------------------------- epreuves

    def eprouver(self, largeur: int, hauteur: int, onglet: str) -> None:
        """Pose la page à cette taille, puis regarde si elle bouge encore."""
        self.app.geometry(f"{largeur}x{hauteur}+0+0")
        # On arrive toujours d'un autre onglet : c'est le geste qui révèle.
        self.app.tabbar.select("qualite")
        self.battre(0.25)
        self.compte.clear()
        try:
            self.app.tabbar.select(onglet)
            self.battre(POSE)
            avant = sum(self.compte.values())
            self.battre(OBSERVATION)
            apres = sum(self.compte.values()) - avant
        except Boucle:
            signal.setitimer(signal.ITIMER_REAL, 0.0)
            self._dire("BOUCLE ", f"{largeur}x{hauteur} {onglet}")
            return
        self.essais += 1
        if apres:
            self._dire("TREMBLE", f"{largeur}x{hauteur} {onglet} : {avant} "
                                  f"bascule(s) puis {apres} de plus")
        elif avant > AGITATION:
            self._dire("AGITE  ", f"{largeur}x{hauteur} {onglet} : {avant} "
                                  f"bascules avant de se poser")

    def aller_retour(self, depart: str, ailleurs: str) -> None:
        """La même taille doit redonner la même page, quel que soit le
        chemin parcouru pour y revenir."""
        self.app.geometry(depart + "+0+0")
        self.battre(POSE)
        avant = self._etat()
        for _ in range(2):
            self.app.geometry(ailleurs + "+0+0")
            self.battre(0.5)
            self.app.geometry(depart + "+0+0")
            self.battre(0.5)
        self.essais += 1
        if self._etat() != avant:
            ecarts = [couple for couple in zip(avant, self._etat())
                      if couple[0] != couple[1]][:3]
            self._dire("CHEMIN ", f"{depart} <-> {ailleurs} : {ecarts}")

    def _etat(self):
        """Les tailles posées et les écarts entre blocs de la page."""
        from hr_analytics.ui.charts import PieChart, PyramidChart, ScaleChart

        mesures = []
        for cadre in getattr(self.app, "_overview_frames", []):
            for graphique in self.app._of_type(cadre, PyramidChart):
                mesures.append(("pyramide", graphique.ROW))
            for graphique in self.app._of_type(cadre, PieChart):
                mesures.append(("anneau", graphique.RADIUS))
            for graphique in self.app._of_type(cadre, ScaleChart):
                mesures.append(("echelle", graphique.HEIGHT))
            for bloc in cadre.winfo_children():
                if bloc.winfo_manager():
                    mesures.append(("ecart",
                                    str(bloc.pack_info().get("pady", ""))))
        return mesures

    def equipe(self, direct: bool = False):
        """Choisit l'équipe la plus courte qui publie encore : c'est elle
        qui laisse le plus de place à redistribuer, donc celle qui révèle."""
        if not self.app._team_keys:
            return None
        rangs = sorted(((nom, self.app._team_rows[cle])
                        for nom, cle in self.app._team_keys.items()),
                       key=lambda item: item[1]["direct"])
        nom, rang = next(((n, r) for n, r in rangs if 5 <= r["direct"] <= 12),
                         rangs[-1])
        self.app.team_var.set(nom)
        self.app.team_direct_var.set(direct)
        self.app.update()
        self.analyser()
        return rang

    def _dire(self, genre: str, detail: str) -> None:
        self.incidents.append(f"{genre} {detail}")
        print(f"  {genre} {detail}", flush=True)

    def onglets(self):
        return [cle for cle in ("population", "organigramme", "graphique",
                                "equite")
                if self.app.tabbar._visible.get(cle, True)]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rapide", action="store_true",
                        help="la bande critique seulement")
    parser.add_argument("--lignes", type=int, default=400)
    args = parser.parse_args(argv)

    banc = Banc(args.lignes)
    banc.charger()
    pas = 30 if args.rapide else 10
    print("Équipe réduite — la page la plus courte :", flush=True)
    rang = banc.equipe(direct=True)
    if rang:
        print(f"  ligne directe de {rang['direct']} salariés", flush=True)
        for hauteur in range(880, 1030, pas):
            for onglet in banc.onglets():
                banc.eprouver(1700, hauteur, onglet)
    print("Fichier entier — tous les onglets ouverts :", flush=True)
    banc.app.team_direct_var.set(False)
    banc.app.team_var.set(list(banc.app.team_choice.cget("values"))[0])
    banc.app.update()
    banc.analyser()
    largeurs = range(1120, 1520, 40 if args.rapide else 20)
    for largeur in largeurs:
        for onglet in banc.onglets():
            banc.eprouver(largeur, 900, onglet)
    if not args.rapide:
        for hauteur in range(700, 1060, 30):
            for onglet in banc.onglets():
                banc.eprouver(1400, hauteur, onglet)
    print("Aller-retour de taille :", flush=True)
    banc.app.tabbar.select("population")
    for ailleurs in ("1900x1050", "1180x700", "1700x960"):
        banc.aller_retour("1400x900", ailleurs)

    print(f"\n{banc.essais} épreuves, {len(banc.incidents)} incident(s).",
          flush=True)
    banc.app.destroy()
    return 1 if banc.incidents else 0


if __name__ == "__main__":
    raise SystemExit(main())
