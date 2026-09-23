"""Graduations d'axes.

Un axe gradue par simple division de l'etendue affiche les valeurs qui
tombent : « 4 284 EUR », « 38 758 EUR », ou une anciennete de « -0,6 an ».
Ce sont des nombres exacts, mais illisibles — et une anciennete negative
n'existe pas.

Les graduations sont donc posees sur des valeurs rondes, choisies dans la
progression 1 / 2 / 5 x 10^n, et toujours entieres : ni decimale, ni pas
inferieur a l'unite. Le pas retenu vaut au moins dix des que l'etendue le
permet, ce qui donne 0 / 10 / 20 / 30 pour une anciennete, et
25 000 / 50 000 / 75 000 pour une remuneration.

Ce module est partage par l'interface, le rapport HTML et le PDF : les
trois doivent graduer leurs axes de la meme facon, sans quoi le meme
graphique se lirait differemment selon le support.
"""

from __future__ import annotations

import math
from typing import List

#: Progression des pas admis. 2,5 n'est retenu qu'au-dela de l'unite, ou il
#: donne 25, 250, 25 000 : au-dessous il produirait des graduations a virgule.
_FACTORS = (1, 2, 2.5, 5, 10)


def nice_step(span: float, count: int = 4) -> int:
    """Pas entier « rond » decoupant `span` en environ `count` intervalles.

    Le pas retenu est le plus proche de la cible, et non le premier
    au-dessus : arrondir systematiquement vers le haut donnait deux
    graduations la ou il en fallait cinq.
    """
    if span <= 0 or count < 1:
        return 1
    raw = span / count
    magnitude = 10.0 ** math.floor(math.log10(raw))
    candidates = []
    for scale in (magnitude, magnitude * 10):
        for factor in _FACTORS:
            step = factor * scale
            # Les pas fractionnaires sont ecartes : une graduation a virgule
            # n'a pas de sens sur une anciennete ni sur une remuneration.
            if step >= 1 and abs(step - round(step)) < 1e-9:
                candidates.append(int(round(step)))
    if not candidates:
        return 1
    return min(set(candidates), key=lambda step: abs(math.log(step / raw)))


def nice_ticks(low: float, high: float, count: int = 4) -> List[float]:
    """Valeurs rondes a graduer entre `low` et `high`, bornes comprises.

    Seules les graduations reellement contenues dans l'etendue sont
    rendues : rien n'est extrapole hors des donnees affichees.
    """
    if not (high > low):
        return [float(round(low))]
    step = nice_step(high - low, count)
    first = math.ceil(low / step) * step
    ticks: List[float] = []
    value = float(first)
    # La tolerance absorbe l'erreur d'arrondi qui, sinon, ferait sauter la
    # derniere graduation quand elle tombe pile sur la borne.
    while value <= high + step * 1e-9:
        ticks.append(value)
        value += step
    if not ticks:
        # Etendue plus etroite que le pas : on gradue le milieu, arrondi.
        ticks = [float(round((low + high) / 2))]
    return ticks


def positions(ticks: List[float], low: float, high: float,
              length: float) -> List[float]:
    """Distance de chaque graduation depuis l'origine de l'axe."""
    span = (high - low) or 1.0
    return [(value - low) / span * length for value in ticks]
