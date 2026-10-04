"""Point d'entree du paquet : « python -m hr_insight » ouvre l'outil.

Sans ce fichier, le paquet ne pouvait pas se lancer par « -m » — Python
repondait « hr_insight is a package and cannot be directly executed ». Il
fallait connaitre le module interne a viser, ce qui n'est ni devinable ni
stable : le lanceur Windows, l'archive .pyz et un utilisateur curieux
pointent desormais tous la meme porte.

Sans argument, la fenetre s'ouvre. Avec des arguments, c'est la ligne de
commande qui repond — « python -m hr_insight analyse population.xlsx »
fait la meme chose que la commande dediee.
"""

from .cli import main

raise SystemExit(main())
