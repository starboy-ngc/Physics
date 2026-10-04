extends SceneTree
## Capture d'écran de chaque zone (nécessite un affichage, ex. xvfb-run) :
##   godot --path . -s tests/screenshot_test.gd -- /dossier/de/sortie

const ZONES := [
	["house_player", "start"],
	["village", "from_house_player"],
	["village", "start"],
	["bakery", "entrance"],
	["house_jeanne", "entrance"],
	["house_martin", "entrance"],
]

var _game: Node
var _out_dir := "user://screenshots"
var _frame := 0
var _index := -1


func _initialize() -> void:
	_game = root.get_node("Game")
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		_out_dir = args[0]
	DirAccess.make_dir_recursive_absolute(_out_dir)
	root.add_child(load("res://scenes/main/Main.tscn").instantiate())


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame % 20 == 10 and _index + 1 < ZONES.size():
		_index += 1
		_game.change_zone(ZONES[_index][0], ZONES[_index][1], true)
	elif _frame % 20 == 0 and _index >= 0:
		var img := root.get_viewport().get_texture().get_image()
		var path := "%s/%02d_%s_%s.png" % [_out_dir, _index, ZONES[_index][0], ZONES[_index][1]]
		img.save_png(path)
		print("[shot] ", path)
		if _index + 1 >= ZONES.size():
			quit(0)
			return true
	return false
