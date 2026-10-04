extends Node
## Scène principale : contient le joueur (persistant), le conteneur de zones
## et l'interface. Le jeu commence dans la maison du joueur.

@onready var zone_root: Node2D = $ZoneRoot
@onready var player: Player = $Player
@onready var ui: CanvasLayer = $GameUI


func _ready() -> void:
	ui.bind_player(player)
	Game.setup(zone_root, player)
	Game.change_zone("house_player", "start", true)
