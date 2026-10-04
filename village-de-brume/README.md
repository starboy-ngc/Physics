# Village de Brume — prototype RPG (Godot 4.3 .NET, C#)

Petit RPG d'exploration en **2.5D** : décor en volumes 3D simples vu par une
caméra en perspective inclinée, personnages en sprites 2D tournés vers la
caméra. Rendu lissé à la résolution de la fenêtre (anticrénelage 4x) ; la
grille de mise en page de l'interface est en 256×192. Ce dossier est un projet
Godot complet, écrit en **C#**.

Prérequis :

- **Godot 4.3 .NET** (la version « .NET » sur godotengine.org, pas la standard) ;
- le **SDK .NET 8** (dotnet.microsoft.com). Godot le détecte automatiquement.

## État : ÉTAPE 2 — interactions, PNJ, dialogues statiques

Format visuel (2.5D, façon RPG de console portable) :

- le sol est le plan y = 0 ; 1 unité monde = 1 tuile de 16 px ; le village fait 48×36 ;
- la caméra (`FollowCamera`) est inclinée de 55°, suit le joueur et reste dans
  les limites de la zone (centrée dans les petites pièces) ;
- maisons, meubles, arbres et puits sont des volumes (boîtes, prismes,
  cylindres, sphères) avec des couleurs unies ou de petites textures pixel
  générées en code (`Materials.cs`) ;
- les personnages sont des `Sprite3D` face caméra dont la planche
  (4 directions × 3 poses, formes arrondies, 64 px par unité) est générée en
  code (`CharacterSprites.cs`) ;
- rendu 3D à la résolution de la fenêtre avec MSAA 4x, textures filtrées.
Direction artistique originale, aucun asset externe.

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
- debug (F3) : liste des PNJ et leur zone, état du dialogue ;
- menu (Échap ou Tab) : met le jeu en pause ; onglets Inventaire (objets,
  quantités, description), Carnet (réservé à l'intrigue), Quitter ;
- inventaire (`Inventory`, autoload) : définitions dans `data/items/items.json`,
  inventaire de départ, piles pour les objets empilables.

Contenu de l'étape 1 :

- scène principale (`scenes/main/Main.tscn`) avec un joueur persistant, la
  caméra et la lumière ;
- village (4 maisons, place pavée, puits, chemins, arbres, panneau vers la forêt) ;
- 4 intérieurs (maison du joueur avec lit, table, chaise, coffre ; boulangerie ;
  maison de Jeanne ; maison de Martin) ;
- joueur : déplacement 4 directions sur le plan, direction regardée, marche animée ;
- caméra 2.5D qui suit le joueur, limitée aux bords de la zone ;
- collisions 3D : murs, meubles, arbres, puits, bords de carte ;
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
| Se déplacer (8 directions) | Flèches, ou ZQSD / WASD (touches physiques, fonctionne en AZERTY) |
| Menu / inventaire | Échap ou Tab ; haut/bas pour choisir, droite ou E pour entrer, gauche pour revenir |
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
godot --headless --path . tests/MenuTest.tscn      # menu, inventaire, pause
```

Chaque test doit afficher `OK` et se terminer avec le code 0.

## Organisation

```
scenes/
  main/Main.tscn            scène de départ : ZoneRoot + Player + FollowCamera + GameUI
  player/Player.tscn        CharacterBody3D + Visual (sprite face caméra)
  npc/NPC.tscn              PNJ générique (rempli depuis data/npcs)
  ui/GameUI.tscn            invite d'interaction + boîte de dialogue
  world/Village.tscn        le village (instances de props + points d'apparition)
  world/interiors/*.tscn    les 4 intérieurs
  world/props/*.tscn        Building, Door, Tree, Well, GroundPatch, Prop (volumes 3D)
scripts/
  systems/Game.cs           autoload Game : registre des zones, changement de zone
  systems/FollowCamera.cs   caméra 2.5D (inclinaison, suivi, limites, environnement)
  systems/DialogueManager.cs   autoload DialogueManager (événements C#)
  systems/DialogueData.cs   chargement/validation d'un dialogue JSON (System.Text.Json)
  systems/Interactable.cs   base Interactable (Area3D, couche 3)
  systems/DebugOverlay.cs   autoload DebugOverlay (F3)
  systems/Main.cs           démarrage dans la maison du joueur
  npc/Npc.cs, NpcTalkArea.cs, NpcManager.cs, NpcData.cs   PNJ et autoload NpcManager
  characters/CharacterVisual.cs   sprite face caméra + ombre (joueur et PNJ)
  characters/CharacterSprites.cs  génération de la planche de sprites
  ui/GameUI.cs              interface en jeu (invite, dialogue)
  ui/MenuUI.cs              menu pause : inventaire, carnet, quitter
  systems/Inventory.cs      autoload Inventory : objets et inventaire du joueur
  player/Player.cs          déplacement, direction, sonde d'interaction
  world/Zone.cs             base Zone : nom, limites (x, z), murs invisibles, Spawns
  world/Village.cs          sol d'herbe + arbres de bordure (générés)
  world/Interior.cs         sol en planches, murs, mur du fond
  world/Building.cs         maison en volumes (crée sa porte)
  world/Door.cs             zone de passage vers une autre zone
  world/Materials.cs        matériaux et textures procédurales partagés
  world/Prop.cs, TreeProp.cs, Well.cs, GroundPatch.cs   décor en volumes
data/npcs/*.json            fiches PNJ (nom, apparence, position, dialogue)
data/dialogues/*.json       dialogues statiques
data/items/items.json       objets et inventaire de départ
tests/                      tests headless (scènes + scripts C#, base TestBase.cs)
VillageDeBrume.csproj / .sln   projet .NET (généré par Godot, versionné)
docs/screenshots/           captures de référence
```

Les graphismes sont construits en code : aucun asset externe pour l'instant,
le dossier `assets/` est prêt pour accueillir de vrais modèles et sprites.

## Ajouter une zone (pour les étapes suivantes)

1. Créer une scène dont la racine a le script `Zone.cs` (ou un dérivé) avec
   `ZoneName` et `Bounds` (x, z en unités), un noeud `Spawns` contenant des `Marker3D`.
2. L'enregistrer dans `Game.Zones` (`scripts/systems/Game.cs`).
3. Placer une `Door` (ou un `Building` avec `DoorTargetZone`) qui pointe
   vers son identifiant et un nom de spawn.

## Ajouter un PNJ

1. Créer `data/npcs/<id>.json` sur le modèle d'`emile.json` (zone, position
   [x, z] en unités, couleurs, `wander_radius`, chemin du dialogue).
2. Créer `data/dialogues/<id>.json` : des noeuds avec `text`, et soit `next`,
   soit `choices` (liste de `{text, next}`). Un noeud sans `next` termine.
3. C'est tout : `NpcManager` charge le dossier au démarrage.
