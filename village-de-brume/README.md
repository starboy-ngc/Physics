# Orion — prototype RPG (Godot 4.3 .NET, C#)

Petit RPG dans le format des « Mystery Dungeon » de console portable : **2D
vue de dessus sur grille de 16 px**, déplacement case par case, village-hub
(échoppe, armurerie, banque, maison avec coffres, camp de départ), boîtes de
dialogue bleu nuit avec portrait. Les donjons viendront se brancher sur ce hub.
L'univers est décrit dans `docs/UNIVERS.md`. Ce dossier est un projet Godot
complet, écrit en **C#**.

Prérequis :

- **Godot 4.3 .NET** (la version « .NET » sur godotengine.org, pas la standard) ;
- le **SDK .NET 8** (dotnet.microsoft.com). Godot le détecte automatiquement.

## Contenu

- **Orion** (`Orion.cs`) : la mer au nord, la place de basalte autour du puits,
  l'échoppe de Birna (alimentation : acheter / vendre en KP), la banque de
  Solveig (déposer / retirer des KP), l'armurerie de Gunnar (équipement), la
  maison au sud, et à l'est le camp de Cassegrain (tentes, longue-vue, Eyvind)
  devant la palissade, future porte des expéditions. Kári, l'ami, traîne près
  de la maison.
- **Maison** (`Home.cs`) : lit, table, et deux coffres qui servent de rangement
  (ranger / prendre) ; le paillasson ramène sur la place.
- **PNJ** : fiches `data/npcs/*.json` (nom, couleurs, case, dialogue, stock),
  dialogues `data/dialogues/*.json` (noeuds, choix, action `shop` / `storage`).
- **Menu** (Échap / Tab) : inventaire avec KP, carnet (réservé), quitter.
- **Rendu** : monde en pixel art 256×192 (sous-viewport agrandi en pixels
  entiers), interface dessinée à la résolution de la fenêtre.
- **Graphismes** : packs **Kenney** (CC0) Tiny Town, Tiny Farm et Tiny
  Dungeon dans `assets/kenney/` (voir le README de ce dossier). Les sols terre
  et pavés se raccordent automatiquement avec l'herbe. Quelques éléments sans
  équivalent dans les packs (eau, tente, longue-vue, lit) sont générés en code.
  Les personnages sont les sprites 16 px de Tiny Dungeon (index `sprite` dans
  `data/npcs/*.json`), retournés vers la gauche et sautillant en marchant.

## Lancer

1. Ouvrir Godot 4.3 .NET → *Importer* → choisir `project.godot`.
2. **F5** : Godot compile le C# puis lance le jeu dans la base.

| Action | Touches |
|---|---|
| Se déplacer (case par case, 8 directions) | Flèches, ou ZQSD / WASD (touches physiques) |
| Parler / examiner / avancer le dialogue | E (ou Entrée), face à la case |
| Choisir une réponse | Haut / Bas puis E |
| Menu | Échap ou Tab ; haut/bas, droite ou E pour entrer, gauche pour revenir |
| Échoppe / armurerie / banque | Parler à Birna, Gunnar ou Solveig (face au comptoir), choisir l'option ; gauche/droite change d'onglet, E valide, Échap ferme |
| Coffres | E face à un coffre de la maison : ranger / prendre |
| Sortir de la maison | Marcher sur le paillasson |
| Debug | F3 |

## Tester sans fenêtre

```bash
dotnet build
godot --headless --path . tests/SmokeTest.tscn     # zones, apparitions, PNJ
godot --headless --path . tests/DoorTest.tscn      # maison <-> place par le paillasson
godot --headless --path . tests/DialogueTest.tscn  # parler à Birna, choix, fin
godot --headless --path . tests/MenuTest.tscn      # menu, inventaire, pause
godot --headless --path . tests/HubTest.tscn       # échoppe, banque, coffres
```

Chaque test affiche `OK` et se termine avec le code 0. Captures : lancer
`tests/ScreenshotTest.tscn` avec un affichage (`xvfb-run` sous Linux).

## Organisation

```
scenes/main/Main.tscn       WorldContainer/World (sous-viewport 256x192 : ZoneRoot, Player) + interfaces
scenes/ui/*.tscn            GameUI, MenuUI, ShopUI, StorageUI
scripts/
  systems/Game.cs           autoload : registre des zones, changement de zone, caméra
  systems/DialogueManager.cs, DialogueData.cs   dialogues (événements, actions)
  systems/Inventory.cs      autoload : objets, pièces, inventaire, dépôt
  systems/DebugOverlay.cs   autoload (F3)
  systems/Main.cs           démarrage, répartition des actions de dialogue
  world/Art.cs, PixelArt.cs  accès aux atlas Kenney, auto-raccord, compléments générés
  world/GridMap.cs          grille : sol, cases bloquées, occupants
  world/Zone.cs             base des zones : plan ASCII, décors, portes, interactions
  world/Orion.cs, Home.cs   les deux zones
  world/PropNode.cs, Interactables.cs  décor posé sur la grille ; comptoir, coffre, objet examinable
  characters/GridEntity.cs  personnage sur grille (pas, animation, ombre)
  characters/CharacterSprites.cs   directions sur la grille
  player/Player.cs          entrées, interaction, portes
  npc/Npc.cs, NpcManager.cs, NpcData.cs   PNJ et autoload NpcManager
  ui/GameUI.cs              dialogue (portrait, choix), invite, message
  ui/ListPanelUI.cs, ShopUI.cs, StorageUI.cs, BankUI.cs, MenuUI.cs
data/npcs, data/dialogues, data/items
tests/                      tests headless (scènes + C#, base TestBase.cs)
docs/screenshots/           captures de référence
```

## Ajouter une zone

1. Créer une classe héritant de `Zone` avec un plan ASCII (voir la légende dans
   `Zone.LoadLayout`), des `Spawns`, des `AddDoor` et `AddInteractable`.
2. L'enregistrer dans `Game.Zones`.

## Ajouter un PNJ

1. `data/npcs/<id>.json` : zone, case `[x, y]`, `sprite` (index Tiny Dungeon),
   `wander_radius` (en cases), dialogue, éventuellement `shop`.
2. `data/dialogues/<id>.json` : noeuds `text` + `next` ou `choices` ; un noeud
   peut porter `action` (`shop`, `storage`, `bank`).

## Crédits

Graphismes : [Kenney](https://kenney.nl) — Tiny Town, Tiny Farm, Tiny Dungeon
(CC0 1.0). Merci à lui ; un don ou un crédit est apprécié mais non requis.
