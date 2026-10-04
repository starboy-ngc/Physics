# Village de Brume — prototype RPG (Godot 4.3, GDScript)

Petit RPG d'exploration en vue 3/4 du dessus. Ce dossier est un projet Godot
complet : ouvrir `project.godot` avec **Godot 4.3** (ou plus récent en 4.x).

## État : ÉTAPE 1 — fondations

Contenu de cette étape :

- scène principale (`scenes/main/Main.tscn`) avec un joueur persistant ;
- village (4 maisons, place pavée, puits, chemins, arbres, panneau vers la forêt) ;
- 4 intérieurs (maison du joueur avec lit, table, chaise, coffre ; boulangerie ;
  maison de Jeanne ; maison de Martin) ;
- joueur : déplacement 4 directions, direction regardée, animation de marche simple ;
- caméra qui suit le joueur, limitée aux bords de la zone (centrée dans les petites pièces) ;
- collisions : murs, meubles, arbres, puits, bords de carte ;
- portes : on entre/sort en marchant dessus, avec un fondu ;
- panneau de debug (**F3**).

Pas encore : PNJ, dialogues, interaction `E`, temps, forêt (étapes suivantes).

## Lancer

1. Ouvrir Godot 4.3 → *Importer* → choisir `project.godot`.
2. Appuyer sur **F5** (lancer le projet).

Contrôles :

| Action | Touches |
|---|---|
| Se déplacer | Flèches, ou ZQSD / WASD (touches physiques, fonctionne en AZERTY) |
| Entrer / sortir d'une maison | Marcher sur la porte |
| Panneau de debug | F3 |
| Interagir | E (réservé pour l'étape 2) |

## Tester sans fenêtre (optionnel)

```bash
godot --headless --path . -s tests/smoke_test.gd   # visite toutes les zones
godot --headless --path . -s tests/door_test.gd    # entrée / sortie par les portes
```

Les deux doivent afficher `OK` et se terminer avec le code 0.

## Organisation

```
scenes/
  main/Main.tscn            scène de départ : ZoneRoot + Player
  player/Player.tscn        CharacterBody2D + Camera2D
  world/Village.tscn        le village (instances de props + points d'apparition)
  world/interiors/*.tscn    les 4 intérieurs
  world/props/*.tscn        Building, Door, Tree, Well, GroundPatch, Prop
scripts/
  systems/game.gd           autoload Game : registre des zones, changement de zone, caméra
  systems/debug_overlay.gd  autoload DebugOverlay (F3)
  systems/main.gd           démarrage dans la maison du joueur
  player/player.gd          déplacement, direction, dessin du personnage
  world/zone.gd             base Zone : nom, limites, murs invisibles, Spawns
  world/village.gd          herbe + arbres de bordure (générés)
  world/interior.gd         sol en planches + mur du fond
  world/building.gd         maison extérieure (crée sa porte)
  world/door.gd             zone de passage vers une autre zone
  world/prop.gd, tree.gd, well.gd, ground_patch.gd   décor dessiné en code
tests/                      tests headless
docs/screenshots/           captures de référence
```

Les graphismes sont dessinés en code (`_draw`) : aucun asset externe pour
l'instant, le dossier `assets/` est prêt pour les remplacer plus tard.

## Ajouter une zone (pour les étapes suivantes)

1. Créer une scène dont la racine a le script `zone.gd` (ou un dérivé) avec
   `zone_name` et `bounds`, un noeud `Spawns` contenant des `Marker2D`.
2. L'enregistrer dans `Game.ZONES` (`scripts/systems/game.gd`).
3. Placer une `Door` (ou un `Building` avec `door_target_zone`) qui pointe
   vers son identifiant et un nom de spawn.
