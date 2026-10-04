# Village de Brume — prototype RPG (Godot 4.3 .NET, C#)

Petit RPG d'exploration en vue 3/4 du dessus. Ce dossier est un projet Godot
complet, écrit en **C#**.

Prérequis :

- **Godot 4.3 .NET** (la version « .NET » sur godotengine.org, pas la standard) ;
- le **SDK .NET 8** (dotnet.microsoft.com). Godot le détecte automatiquement.

## État : ÉTAPE 2 — interactions, PNJ, dialogues statiques

Format visuel : résolution interne 256×192 (façon console portable), agrandie
par un facteur entier, tuiles de 16 px, personnages d'environ 24 px.
Direction artistique originale, tout est dessiné en code.

Contenu de l'étape 2 :

- interaction : quand un `Interactable` est devant le joueur, l'invite
  « E — Parler » s'affiche ; E lance l'action ;
- PNJ (`scenes/npc/NPC.tscn`) : apparence, position et dialogue viennent des
  fiches `data/npcs/*.json`, chargées par l'autoload `NpcManager` qui fait
  apparaître chaque PNJ dans sa zone ;
- déplacements simples des PNJ : `move_to()` (utilisé par les horaires à
  l'étape 3) et petite errance optionnelle (`wander_radius`) ;
- système de dialogue indépendant des PNJ : `DialogueData` (JSON),
  `DialogueManager` (autoload, déroule les noeuds), `GameUI` (boîte de
  dialogue, choix navigables avec haut/bas, validation E) ;
- trois PNJ : Émile (boulangerie), Jeanne (sa maison), Martin (place du village) ;
- debug (F3) : liste des PNJ et leur zone, état du dialogue.

Contenu de l'étape 1 :

- scène principale (`scenes/main/Main.tscn`) avec un joueur persistant ;
- village (4 maisons, place pavée, puits, chemins, arbres, panneau vers la forêt) ;
- 4 intérieurs (maison du joueur avec lit, table, chaise, coffre ; boulangerie ;
  maison de Jeanne ; maison de Martin) ;
- joueur : déplacement 4 directions, direction regardée, animation de marche simple ;
- caméra qui suit le joueur, limitée aux bords de la zone (centrée dans les petites pièces) ;
- collisions : murs, meubles, arbres, puits, bords de carte ;
- portes : on entre/sort en marchant dessus, avec un fondu ;
- panneau de debug (**F3**).

Pas encore : temps et horaires (étape 3), relations et mémoire (étape 4),
forêt (étape 5), IA (étape 6+).

## Lancer

1. Ouvrir Godot 4.3 .NET → *Importer* → choisir `project.godot`.
2. Appuyer sur **F5** : Godot compile le projet C# puis lance le jeu.

En ligne de commande : `dotnet build` dans ce dossier compile le projet.

Contrôles :

| Action | Touches |
|---|---|
| Se déplacer | Flèches, ou ZQSD / WASD (touches physiques, fonctionne en AZERTY) |
| Entrer / sortir d'une maison | Marcher sur la porte |
| Panneau de debug | F3 |
| Parler / avancer le dialogue | E (ou Entrée) |
| Choisir une réponse | Haut / Bas puis E |

## Tester sans fenêtre (optionnel)

```bash
dotnet build
godot --headless --path . tests/SmokeTest.tscn     # visite toutes les zones
godot --headless --path . tests/DoorTest.tscn      # entrée / sortie par les portes
godot --headless --path . tests/DialogueTest.tscn  # parler à Émile, choix, fin
```

Chaque test doit afficher `OK` et se terminer avec le code 0.

## Organisation

```
scenes/
  main/Main.tscn            scène de départ : ZoneRoot + Player
  player/Player.tscn        CharacterBody2D + Visual + Camera2D
  npc/NPC.tscn              PNJ générique (rempli depuis data/npcs)
  ui/GameUI.tscn            invite d'interaction + boîte de dialogue
  world/Village.tscn        le village (instances de props + points d'apparition)
  world/interiors/*.tscn    les 4 intérieurs
  world/props/*.tscn        Building, Door, Tree, Well, GroundPatch, Prop
scripts/
  systems/Game.cs           autoload Game : registre des zones, changement de zone, caméra
  systems/DialogueManager.cs   autoload DialogueManager (événements C#)
  systems/DialogueData.cs   chargement/validation d'un dialogue JSON (System.Text.Json)
  systems/Interactable.cs   base Interactable (Area2D, couche 3)
  systems/DebugOverlay.cs   autoload DebugOverlay (F3)
  systems/Main.cs           démarrage dans la maison du joueur
  npc/Npc.cs, NpcTalkArea.cs, NpcManager.cs, NpcData.cs   PNJ et autoload NpcManager
  characters/CharacterVisual.cs   dessin partagé joueur / PNJ
  ui/GameUI.cs              interface en jeu
  player/Player.cs          déplacement, direction, sonde d'interaction
  world/Zone.cs             base Zone : nom, limites, murs invisibles, Spawns
  world/Village.cs          herbe + arbres de bordure (générés)
  world/Interior.cs         sol en planches + mur du fond
  world/Building.cs         maison extérieure (crée sa porte)
  world/Door.cs             zone de passage vers une autre zone
  world/Prop.cs, TreeProp.cs, Well.cs, GroundPatch.cs   décor dessiné en code
data/npcs/*.json            fiches PNJ (nom, apparence, position, dialogue)
data/dialogues/*.json       dialogues statiques
tests/                      tests headless (scènes + scripts C#, base TestBase.cs)
VillageDeBrume.csproj / .sln   projet .NET (généré par Godot, versionné)
docs/screenshots/           captures de référence
```

Les graphismes sont dessinés en code (`_Draw`) : aucun asset externe pour
l'instant, le dossier `assets/` est prêt pour les remplacer plus tard.

## Ajouter une zone (pour les étapes suivantes)

1. Créer une scène dont la racine a le script `Zone.cs` (ou un dérivé) avec
   `ZoneName` et `Bounds`, un noeud `Spawns` contenant des `Marker2D`.
2. L'enregistrer dans `Game.Zones` (`scripts/systems/Game.cs`).
3. Placer une `Door` (ou un `Building` avec `DoorTargetZone`) qui pointe
   vers son identifiant et un nom de spawn.

## Ajouter un PNJ

1. Créer `data/npcs/<id>.json` sur le modèle d'`emile.json` (zone, position,
   couleurs, `wander_radius`, chemin du dialogue).
2. Créer `data/dialogues/<id>.json` : des noeuds avec `text`, et soit `next`,
   soit `choices` (liste de `{text, next}`). Un noeud sans `next` termine.
3. C'est tout : `NpcManager` charge le dossier au démarrage.
