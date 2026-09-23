"""Barre de chargement : une progression qui ne s'arrete jamais.

Une barre saccadee n'est pas un detail d'esthetique. Pendant une analyse
longue — dix secondes de lecture sur un fichier de cent mille lignes —, elle
est le seul signe que l'outil travaille. Une barre qui se fige trois fois
par seconde donne l'impression inverse, et c'est l'impression qui decide si
l'on attend ou si l'on tue la fenetre.

Trois choix la rendent fluide, et aucun n'est cosmetique.

1. *La position se calcule sur le temps, jamais sur le nombre d'images.*
   Une barre qui avance d'un cran par image ralentit quand le fil principal
   est preempte ; celle-ci est la ou l'horloge dit qu'elle doit etre. Une
   image tardive fait un pas plus grand, pas un arret.

2. *Elle avance meme sans nouvelle.* Le moteur annonce des etapes ; entre
   deux annonces, la barre continue vers un objectif legerement en avant,
   en ralentissant. Elle ne depasse pas l'annonce suivante de plus d'un
   souffle, et ne recule jamais.

3. *Elle ne recule jamais*, meme si l'annonce suivante est en retrait de ce
   qui est deja montre : elle attend que le calcul la rattrape.
"""

from __future__ import annotations

import math
import time
import tkinter as tk
from typing import Callable, Optional

from . import theme
from .theme import SIZE_SMALL, pick_family


class LoadingBar(tk.Frame):
    """Barre d'avancement, dessinee et animee par l'horloge."""

    #: Epaisseur du trait. Une barre de chargement n'est pas un graphique :
    #: elle doit se voir sans rien peser.
    HEIGHT = 6
    #: Intervalle demande entre deux images. Le fil principal ne le tiendra
    #: pas toujours — c'est precisement pourquoi la position se calcule sur
    #: le temps ecoule et non sur le nombre d'images.
    FRAME_MS = 16
    #: Constante de temps de l'approche, en secondes : au bout d'elle, les
    #: deux tiers du chemin restant sont faits. Plus courte, la barre saute
    #: a chaque annonce ; plus longue, elle traine derriere le calcul.
    TAU = 0.20
    #: De combien la barre a le droit d'anticiper l'annonce en cours. Sans
    #: cette avance, une etape opaque de deux secondes — la normalisation —
    #: laisserait la barre parfaitement immobile : quatre arrets visibles
    #: par analyse, dont un de deux secondes et demie.
    LOOKAHEAD = 0.08
    #: Temps de montee de cette avance. Elle repart de zero a chaque
    #: annonce — la barre rejoint alors franchement ce que le moteur dit —
    #: puis croit lentement tant que rien n'arrive. C'est ce qui fait qu'une
    #: etape muette avance encore, de plus en plus doucement, au lieu de se
    #: figer.
    CREEP_TAU = 2.5
    #: Jamais tout a fait pleine avant la fin : une barre au bout depuis
    #: trois secondes est un outil qui a l'air bloque.
    CEILING = 0.995

    def __init__(self, master: tk.Widget, ground: Optional[str] = None,
                 clock: Callable[[], float] = time.perf_counter,
                 track: Optional[str] = None, fill: Optional[str] = None,
                 ink: Optional[str] = None):
        # Les couleurs sont celles du theme par defaut, mais l'ecran
        # d'accueil pose la meme barre sur un fond sombre : un filet gris
        # clair y disparaitrait.
        self.ground = ground or theme.GROUND
        self.track = track or theme.LINE
        self.fill = fill or theme.ACCENT
        self.ink = ink or theme.MUTED
        super().__init__(master, background=self.ground)
        petite = (pick_family(self), SIZE_SMALL)
        self.clock = clock
        self.canvas = tk.Canvas(self, height=self.HEIGHT,
                                background=self.ground, highlightthickness=0)
        self.canvas.pack(fill="x")
        self.caption = tk.Label(self, text="", background=self.ground,
                                foreground=self.ink, anchor="w",
                                font=petite)
        self.percent = tk.Label(self, text="", background=self.ground,
                                foreground=self.ink, anchor="e",
                                font=petite)
        self.caption.pack(side="left", pady=(4, 0))
        self.percent.pack(side="right", pady=(4, 0))
        self._track = self.canvas.create_rectangle(
            0, 0, 0, self.HEIGHT, fill=self.track, outline="")
        self._fill = self.canvas.create_rectangle(
            0, 0, 0, self.HEIGHT, fill=self.fill, outline="")
        self._target = 0.0
        self._shown = 0.0
        self._last = self.clock()
        self._announced = self._last
        self._job: Optional[str] = None
        self._running = False

    # --------------------------------------------------------------- vie

    def start(self, label: str = "") -> None:
        self._target = 0.0
        self._shown = 0.0
        self._last = self.clock()
        self._announced = self._last
        self._running = True
        self.announce(label, 0.0)
        self._schedule()

    def announce(self, label: str, fraction: float) -> None:
        """Nouvelle etape et part faite, telles que le moteur les rapporte."""
        nouvelle = min(max(float(fraction), self._target), 1.0)
        if nouvelle > self._target:
            # L'avance repart de zero : ce que le moteur vient de dire est su,
            # il n'y a plus rien a deviner.
            self._announced = self.clock()
        self._target = nouvelle
        self.caption.configure(text=label)

    def finish(self) -> None:
        """Termine le trait avant de disparaitre.

        Une barre qui s'efface a quatre-vingt-seize pour cent laisse le
        sentiment d'un travail interrompu. Le calcul est fini : le trait
        doit l'etre aussi, et il reste visible le temps que les resultats
        s'affichent.
        """
        self._target = 1.0
        self._shown = 1.0
        self.caption.configure(text="Analyse terminée")
        self._draw()
        self.update_idletasks()

    def stop(self) -> None:
        self._running = False
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def destroy(self) -> None:
        """Une image encore en attente s'executerait apres la fermeture, et
        Tk se plaindrait d'une commande qui n'existe plus."""
        self.stop()
        super().destroy()

    # ------------------------------------------------------------ image

    def _schedule(self) -> None:
        self._job = self.after(self.FRAME_MS, self._tick)

    def _tick(self) -> None:
        if not self._running:
            return
        self.step()
        self._schedule()

    def step(self) -> None:
        """Une image : avance selon le temps reellement ecoule."""
        maintenant = self.clock()
        ecoule = max(maintenant - self._last, 0.0)
        self._last = maintenant
        attente = max(maintenant - self._announced, 0.0)
        avance = self.LOOKAHEAD * (1.0 - math.exp(-attente / self.CREEP_TAU))
        objectif = min(self._target + avance, self.CEILING)
        if self._target >= 1.0:
            objectif = 1.0
        if objectif > self._shown:
            # Approche exponentielle : la part du chemin restant faite ne
            # depend que du temps ecoule, jamais du nombre d'appels.
            part = 1.0 - math.exp(-ecoule / self.TAU)
            self._shown += (objectif - self._shown) * part
        self._draw()

    def _draw(self) -> None:
        largeur = self.canvas.winfo_width()
        if largeur < 2:
            return
        self.canvas.coords(self._track, 0, 0, largeur, self.HEIGHT)
        self.canvas.coords(self._fill, 0, 0, largeur * self._shown,
                           self.HEIGHT)
        self.percent.configure(text=f"{int(self._shown * 100)} %")

    # --------------------------------------------------------- lecture

    @property
    def shown(self) -> float:
        return self._shown

    @property
    def target(self) -> float:
        return self._target
