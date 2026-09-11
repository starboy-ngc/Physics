"""Ecran d'accueil : le temps que l'outil se construise.

Ouvrir la fenetre principale demande deux dixiemes de seconde ici, et
davantage sur un poste charge : lire la configuration, poser le theme,
mesurer les polices, construire une dizaine de pages et leurs graphiques.
Sans rien a l'ecran pendant ce temps, l'outil parait ne pas demarrer.

L'ecran montre donc ce qui se passe reellement — chaque etape est annoncee
au moment ou elle commence —, et il reste affiche un temps minimal
parametrable : la construction est trop rapide pour qu'on ait le temps de
lire quoi que ce soit, et une marque qui clignote ne se voit pas. Ce
temps-la est assume, et il se regle a zero pour qui n'en veut pas.

Un clic passe l'ecran.
"""

from __future__ import annotations

import time
import tkinter as tk
import tkinter.font as tkfont
from typing import Callable, List, Optional

from ..core import palette
from ..version import ENGINE_NAME, PUBLISHER, __version__
from . import logo
from . import theme
from .progress import LoadingBar

#: Le nom et la maison viennent de « version.py », ou ils sont ecrits une
#: seule fois : la fenetre, les documents et le manifeste doivent nommer
#: l'outil de la meme facon.
PRODUCT = ENGINE_NAME
TAGLINE = "Analyse de rémunération · local et hors ligne"


class Splash(tk.Toplevel):
    """Fenetre sans cadre, centree, le temps du demarrage."""

    WIDTH, HEIGHT = 580, 424
    #: Cadre du symbole. Une aurore s'inscrit mal dans un carre : il y
    #: resterait deux bandes vides.
    LOGO = 236
    LOGO_HEIGHT = 160
    #: Largeur du filet d'avancement. Plus etroit que l'ecran : une barre
    #: qui va d'un bord a l'autre appartient a la fenetre, pas a la marque.
    BAR_WIDTH = 300
    #: Images d'une ondulation complete, et cadence.
    FRAMES = 24
    FRAME_MS = 70
    #: Images calculees d'un coup entre deux battements : elles arrivent
    #: pendant que l'ecran est deja la, plutot que de le retarder.
    CHUNK = 2

    def __init__(self, master: tk.Misc, fonts: theme.Fonts):
        super().__init__(master, background=theme.INK)
        self.overrideredirect(True)
        self.configure(highlightthickness=1,
                       highlightbackground=palette.mix(theme.INK,
                                                       theme.CANVAS, 0.22))
        self.skipped = False
        self.clair = palette.mix(theme.INK, theme.CANVAS, 0.62)
        self.discret = palette.mix(theme.INK, theme.CANVAS, 0.38)
        self._centre()

        grand = tkfont.Font(root=self, family=fonts.family,
                            size=theme.SIZE_TITLE + 15)
        petite = (fonts.family, theme.SIZE_SMALL)
        minuscule = (fonts.family, theme.SIZE_LABEL)

        # Le symbole ne suit pas le theme : une marque qui change de
        # couleur avec un reglage d'affichage n'est plus une marque.
        self.symbole = logo.Aurora(self.LOGO, self.FRAMES,
                                   height=self.LOGO_HEIGHT)
        self._images: List[tk.PhotoImage] = []
        self._frame = 0
        self._next_ms = 0.0
        self.symbole_vu = tk.Label(self, background=theme.INK)
        self.symbole_vu.pack(pady=(34, 14))
        # La premiere image suffit a montrer l'ecran ; les vingt-trois
        # autres arrivent pendant qu'il est deja la.
        self._render_next()
        self._show(0)

        tk.Label(self, text=PRODUCT, background=theme.INK,
                 foreground=theme.CANVAS, font=grand).pack()
        tk.Label(self, text=TAGLINE, background=theme.INK,
                 foreground=self.clair, font=petite).pack(pady=(6, 0))

        piste = tk.Frame(self, background=theme.INK, width=self.BAR_WIDTH,
                         height=30)
        piste.pack(pady=(30, 0))
        piste.pack_propagate(False)
        self.bar = LoadingBar(piste, ground=theme.INK,
                              track=palette.mix(theme.INK, theme.CANVAS, 0.16),
                              fill=palette.mix(theme.ACCENT, theme.CANVAS, 0.5),
                              ink=self.clair)
        self.bar.pack(fill="x")
        self.bar.start("Démarrage")

        pied = tk.Frame(self, background=theme.INK, height=22)
        pied.pack(side="bottom", fill="x", padx=22, pady=(0, 18))
        pied.pack_propagate(False)
        tk.Label(pied, text=f"Version {__version__}", background=theme.INK,
                 foreground=self.discret, font=minuscule).pack(side="right")
        # La maison au centre : c'est une signature, pas une mention legale.
        maison = tk.Label(pied, text=PUBLISHER.upper(), background=theme.INK,
                          foreground=self.discret, font=minuscule)
        maison.place(relx=0.5, rely=0.5, anchor="center")

        self.bind("<Button-1>", lambda _e: self.skip())
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda _e: self.skip())

    # ------------------------------------------------------------- cadre

    def _centre(self) -> None:
        ecran_l = self.winfo_screenwidth()
        ecran_h = self.winfo_screenheight()
        x = (ecran_l - self.WIDTH) // 2
        y = (ecran_h - self.HEIGHT) // 2
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{max(y, 0)}")

    # ----------------------------------------------------------- symbole

    def _render_next(self) -> bool:
        """Calcule l'image suivante. Rend faux quand la rotation est
        complete."""
        if len(self._images) >= self.FRAMES:
            return False
        self._images.append(tk.PhotoImage(
            master=self, data=self.symbole.frame(len(self._images))))
        return True

    def _show(self, index: int) -> None:
        if index < len(self._images):
            self.symbole_vu.configure(image=self._images[index])

    # ------------------------------------------------------------ vie

    def announce(self, label: str, fraction: float) -> None:
        self.bar.announce(label, fraction)

    def tick(self) -> None:
        """Un battement : la barre avance, l'aurore ondule.

        Tant que l'ondulation n'est pas complete, le battement sert a la
        calculer — une image par passage, pour ne jamais bloquer l'ecran
        plus d'une douzaine de millisecondes d'affilee.
        """
        self.bar.step()
        if self._render_next():
            return
        maintenant = time.perf_counter() * 1000
        if maintenant >= self._next_ms:
            self._frame = (self._frame + 1) % self.FRAMES
            self._show(self._frame)
            self._next_ms = maintenant + self.FRAME_MS

    def skip(self) -> None:
        self.skipped = True

    def close(self) -> None:
        self.bar.stop()
        self.destroy()


def show(master: tk.Misc, fonts: theme.Fonts) -> Optional[Splash]:
    """Ouvre l'ecran d'accueil, ou rien si l'affichage le refuse."""
    try:
        accueil = Splash(master, fonts)
    except tk.TclError:                                 # pragma: no cover
        return None
    accueil.update()
    return accueil
