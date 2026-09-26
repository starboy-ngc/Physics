"""Ce qui se passe pendant l'analyse, pendant qu'elle se passe.

Une analyse de cent mille lignes demande une dizaine de secondes. Jusqu'ici
la fenetre ne montrait qu'un filet de six pixels dans la colonne de gauche,
et la page restait sur « Aucune analyse » : rien ne bougeait la ou le regard
etait, et l'attente paraissait une panne.

Ce panneau prend la place des pages le temps du calcul et montre trois
choses, toutes vraies :

1. *L'etape en cours*, telle que le moteur l'annonce — les libelles viennent
   de `pipeline.stage_labels()`, jamais d'une liste recopiee ici : une
   etape ajoutee au moteur apparait sans qu'on y pense, et aucune etape
   affichee ne peut manquer au calcul.
2. *Celles qui sont faites*, et celles qui restent. C'est ce qui transforme
   une attente opaque en une attente bornee.
3. *Le temps ecoule*, qui avance meme quand une etape est longue et muette.

Et le symbole ondule, pour la meme raison qu'il ondule a l'ouverture : un
ecran parfaitement immobile pendant dix secondes se lit comme un ecran
fige. L'ondulation est calculee une image a la fois, entre deux releves de
la file, pour ne jamais retarder ni le calcul ni le trace.

Le panneau n'apparait qu'apres un court delai : sur un fichier de mille
lignes, l'analyse dure moins qu'un clignement, et un panneau qui
apparaitrait pour disparaitre aussitot serait un defaut d'affichage, pas une
information.
"""

from __future__ import annotations

import time
import tkinter as tk
from typing import List, Sequence

from . import logo
from . import theme
from .progress import LoadingBar


class WorkPanel(tk.Frame):
    """Le panneau d'attente : l'etape, les etapes, le temps, le symbole."""

    #: Cadre du symbole. Plus petit qu'a l'accueil : il accompagne ici, il
    #: ne se presente pas.
    LOGO_WIDTH, LOGO_HEIGHT = 168, 112
    #: Images d'une ondulation complete, et cadence.
    FRAMES = 20
    FRAME_MS = 80
    #: Largeur du filet d'avancement.
    BAR_WIDTH = 460

    def __init__(self, master: tk.Widget, fonts: theme.Fonts,
                 steps: Sequence[str] = ()):
        super().__init__(master, background=theme.CANVAS)
        self.fonts = fonts
        self.steps = list(steps)
        self._started = 0.0
        self._frame = 0
        self._next_ms = 0.0
        self._images: List[tk.PhotoImage] = []
        self._symbole = logo.Aurora(self.LOGO_WIDTH, self.FRAMES,
                                    height=self.LOGO_HEIGHT)
        self._done: List[str] = []
        self.current = ""

        centre = tk.Frame(self, background=theme.CANVAS)
        centre.place(relx=0.5, rely=0.42, anchor="center")
        self.symbole_vu = tk.Label(centre, background=theme.CANVAS)
        self.symbole_vu.pack()
        self._render_next()
        self._show(0)

        self.titre = tk.Label(centre, text="Analyse en cours",
                              background=theme.CANVAS, foreground=theme.INK,
                              font=fonts.title)
        self.titre.pack(pady=(14, 2))
        self.etape = tk.Label(centre, text="", background=theme.CANVAS,
                              foreground=theme.MUTED, font=fonts.body)
        self.etape.pack()

        piste = tk.Frame(centre, background=theme.CANVAS,
                         width=self.BAR_WIDTH, height=26)
        piste.pack(pady=(18, 6))
        piste.pack_propagate(False)
        self.bar = LoadingBar(piste, ground=theme.CANVAS)
        self.bar.pack(fill="x")

        self.liste = tk.Frame(centre, background=theme.CANVAS)
        self.liste.pack(pady=(10, 0))
        self._lignes: dict = {}
        self._build_steps()

        self.chrono = tk.Label(centre, text="", background=theme.CANVAS,
                               foreground=theme.FAINT, font=fonts.small)
        self.chrono.pack(pady=(14, 0))

        # Les images sont liberees a la destruction du panneau, sur le fil
        # qui les a creees et tant que l'interpreteur Tk existe encore.
        # Laissees au ramasse-miettes, elles peuvent etre collectees depuis
        # le fil de calcul — il alloue, donc il declenche des passages du
        # ramasse-miettes — et « PhotoImage.__del__ » appelle alors Tcl
        # depuis le mauvais fil. Tcl n'y repond pas par une exception : il
        # abandonne le processus entier.
        self.bind("<Destroy>", self._forget_images, add="+")

    def _forget_images(self, event=None) -> None:
        if event is not None and event.widget is not self:
            return
        try:
            self.symbole_vu.configure(image="")
        except tk.TclError:                             # pragma: no cover
            pass
        self._images = []

    # ------------------------------------------------------------ etapes

    def _build_steps(self) -> None:
        for child in self.liste.winfo_children():
            child.destroy()
        self._lignes = {}
        for étape in self.steps:
            ligne = tk.Label(self.liste, text=f"    {étape}",
                             background=theme.CANVAS, foreground=theme.FAINT,
                             font=self.fonts.small, anchor="w", width=34)
            ligne.pack(anchor="w")
            self._lignes[étape] = ligne

    def _repaint_steps(self) -> None:
        """Faites, en cours, a venir : trois etats, trois tons.

        Le marqueur est un point median et une fleche simple — deux signes
        qu'une police de systeme porte partout, la ou une coche ou une puce
        pleine s'affichent en carre vide sur un poste mal dote.
        """
        for étape, ligne in self._lignes.items():
            if étape == self.current:
                ligne.configure(text=f"  > {étape}", foreground=theme.INK,
                                font=self.fonts.small_bold)
            elif étape in self._done:
                ligne.configure(text=f"  · {étape}", foreground=theme.MUTED,
                                font=self.fonts.small)
            else:
                ligne.configure(text=f"    {étape}", foreground=theme.FAINT,
                                font=self.fonts.small)

    # -------------------------------------------------------------- vie

    def start(self) -> None:
        self._started = time.perf_counter()
        self._done = []
        self.current = ""
        self._repaint_steps()
        self.etape.configure(text="Préparation")
        self.chrono.configure(text="")
        self.bar.start("Préparation")

    def announce(self, label: str, fraction: float) -> None:
        """Une etape commence. Les precedentes sont donc finies."""
        self.bar.announce(label, fraction)
        if label != self.current:
            if self.current and self.current not in self._done:
                self._done.append(self.current)
            # Une etape annoncee alors qu'une autre a ete sautee — un
            # fichier sans segment, par exemple — clot quand meme celles
            # qui la precedent : la liste ne doit pas garder une etape en
            # attente derriere l'etape en cours.
            if label in self.steps:
                rang = self.steps.index(label)
                for précédente in self.steps[:rang]:
                    if précédente not in self._done:
                        self._done.append(précédente)
            self.current = label
            self._repaint_steps()
        self.etape.configure(text=label)

    def tick(self) -> None:
        """Un battement : le symbole ondule, le chronometre avance.

        Tant que l'ondulation n'est pas complete, le battement sert a la
        calculer — une image par passage, pour ne jamais bloquer le trace
        plus de quelques millisecondes d'affilee.
        """
        if self._started:
            écoulé = time.perf_counter() - self._started
            self.chrono.configure(
                text=f"{écoulé:.0f} s".replace(".", ",") if écoulé >= 1
                else "")
        if self._render_next():
            return
        maintenant = time.perf_counter() * 1000
        if maintenant >= self._next_ms:
            self._frame = (self._frame + 1) % self.FRAMES
            self._show(self._frame)
            self._next_ms = maintenant + self.FRAME_MS

    def finish(self) -> None:
        for étape in self.steps:
            if étape not in self._done:
                self._done.append(étape)
        self.current = ""
        self._repaint_steps()
        self.bar.stop()

    # ---------------------------------------------------------- symbole

    def _render_next(self) -> bool:
        """Calcule l'image suivante. Faux quand l'ondulation est complete."""
        if len(self._images) >= self.FRAMES:
            return False
        try:
            self._images.append(tk.PhotoImage(
                master=self, data=self._symbole.frame(len(self._images))))
        except tk.TclError:                             # pragma: no cover
            # Un affichage qui refuse l'image ne doit pas faire echouer une
            # analyse : le panneau se passe de symbole.
            self._images.append(tk.PhotoImage(master=self, width=1, height=1))
        return True

    def _show(self, index: int) -> None:
        if index < len(self._images):
            self.symbole_vu.configure(image=self._images[index])
