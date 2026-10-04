extends Node
## Scène principale : contient le joueur (persistant) et le conteneur de zones.
## Le jeu commence dans la maison du joueur.

@onready var zone_root: Node2D = $ZoneRoot
@onready var player: Player = $Player


func _ready() -> void:
	Game.setup(zone_root, player)
	Game.change_zone("house_player", "start", true)
