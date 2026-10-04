# Étude de faisabilité : RogueEssence pour Orion

Date : octobre 2026. Question : faut-il basculer Orion sur RogueEssence (le
moteur de « Pokémon Mystery Dungeon: Origins ») ou continuer sur notre base
Godot C# en y intégrant RogueElements ?

## Ce qui a été vérifié ici

- **Sources récupérées** : RogueEssence (moteur), RogueElements (génération de
  donjons), PMDC (le jeu exécutable : moteur + système de combat), PMDODump
  (générateur de données de PMDO). Tous sous licence MIT, en C# / .NET 8.
- **Compilation** : RogueElements et RogueEssence compilent sans erreur avec
  notre SDK .NET 8. Bonne nouvelle : même outillage que notre projet.
- **Exécution** : non testée ici. Le jeu a besoin des bibliothèques natives FNA
  (SDL2, FNA3D, FAudio), que les sites de téléchargement bloqués ne permettent
  pas de récupérer, et d'un dossier d'assets de base (interface, polices,
  données) que seul PMDO fournit, avec ses graphismes Pokémon.

## Comment un jeu est construit sur RogueEssence

| Élément | Comment on le fabrique | Observation |
|---|---|---|
| Donjons | Code C# dans un « générateur de données » qui décrit chaque étage avec RogueElements, puis export vers le dossier Data | Le fichier des donjons de PMDO fait 5 800 lignes ; puissant mais dense |
| Hub (cartes « ground ») | Code C# avec positions en pixels, ou l'éditeur graphique Avalonia | L'éditeur est la voie confortable, sur ton PC |
| PNJ, boutiques, cinématiques | Scripts Lua | Les boutiques existent déjà dans PMDO, à adapter |
| Créatures | Données (stats, formes, capacités, types, croissance) + planche de sprites au format PMD (AnimData.xml : repos, marche, attaque, blessure, sommeil… en 8 directions) | **C'est le poste de coût principal** : chaque créature demande des dizaines d'images |
| Combat | Fourni par PMDC : types, capacités avec PP, talents, niveaux, équipe | Très « Pokémon » ; simplifier demande de modifier PMDC |
| Objets, statuts, éléments | À redéfinir dans le générateur de données | Travail de contenu classique |

## Ce que coûterait Orion sur RogueEssence

1. Mise en place : compiler le moteur, assembler un dossier d'assets de base
   sans contenu Pokémon (interface, polices, menus) : 1 à 2 sessions.
2. Hub Orion : carte, cinq PNJ, échoppe, armurerie, banque, coffres :
   1 à 2 sessions, en réutilisant les scripts de boutique de PMDO.
3. Créatures : une dizaine au minimum, chacune avec données et planche
   d'animations 8 directions. Sans artiste, c'est le mur. Nos sprites Kenney
   à une pose ne conviennent pas à ce format.
4. Donjons : une session par direction (vallée, plateaux, glaciers…).
5. Combat : accepter le système PMD tel quel, ou le réduire en touchant au
   code de PMDC.

À cela s'ajoutent : l'abandon de la base Godot (hub, interface, tests),
l'éditeur Avalonia comme outil quotidien, et une documentation de fans.

## Ce que coûterait la voie Godot + RogueElements

- RogueElements compile seul et peut être référencé par notre projet Godot
  comme une bibliothèque : la partie difficile (salles, couloirs, escaliers,
  placement des créatures et objets) est fournie.
- Reste à écrire : la boucle tour par tour, les créatures et leur IA, les
  objets en donjon, la faim, l'arrivée et le retour à Cassegrain. Ordre de
  grandeur : 3 à 4 sessions pour un premier donjon jouable.
- On garde tout l'existant, et on choisit nos règles de combat (plus simples
  que les types et PP de Pokémon, sauf si tu les veux).
- Les sprites restent le poste de coût commun aux deux voies, mais notre
  format (une pose, retournement) est bien moins exigeant pour démarrer.

## Verdict

**Continuer sur Godot C# et intégrer RogueElements pour les donjons.**

RogueEssence n'a de sens que si l'objectif est un clone complet de Pokémon
Mystery Dungeon (types, capacités, talents, niveaux, équipe, sauvetages) et
si l'on accepte le coût de production des planches de sprites PMD. Dans ce
cas, le moteur apporte énormément. Pour Orion tel que décrit (aventure
chaleureuse, village-hub, expéditions, créatures originales), la voie Godot
garde le contrôle, réutilise ce qui existe, et emprunte à RogueEssence
exactement ce qui est difficile : la génération des étages.

Pour sentir le moteur, le plus simple reste de télécharger PMDO sur
https://github.com/audinowho/PMDODump/releases et d'y jouer un quart d'heure.
