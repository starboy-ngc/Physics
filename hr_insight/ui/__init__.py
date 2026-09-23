"""Interface graphique locale, construite sur tkinter.

tkinter est livre avec Python : aucune dependance supplementaire, aucun
telechargement, aucun droit administrateur. L'interface ne contient aucune
regle de calcul — elle appelle `core.pipeline`, exactement comme la ligne de
commande.

Le moteur, lui, n'importe jamais ce paquet : il reste utilisable sans
interface, et une installation depourvue de tkinter continue de fonctionner
en ligne de commande.
"""
