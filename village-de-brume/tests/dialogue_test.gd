extends SceneTree
## Test d'interaction et de dialogue, sans fenêtre :
##   godot --headless --path . -s tests/dialogue_test.gd
## Va dans la boulangerie, marche vers Émile, appuie sur E, parcourt le
## dialogue (choix puis suites) jusqu'à la fin.

var _game: Node
var _frame := 0
var _phase := 0
var _phase_start := 0
var _nodes_seen := 0
var _choices_seen := 0
## Le test descend d'un cran dans les choix : la branche « Je ne fais que passer » doit apparaître.
var _passing_seen := false


func _initialize() -> void:
	Engine.max_fps = 60
	_game = root.get_node("Game")
	root.add_child(load("res://scenes/main/Main.tscn").instantiate())
	root.get_node("DialogueManager").node_changed.connect(_on_node)


func _on_node(speaker: String, text: String, choices: PackedStringArray) -> void:
	_nodes_seen += 1
	if not choices.is_empty():
		_choices_seen += 1
	if text.begins_with("Passer ?"):
		_passing_seen = true
	print("[dialogue] %s : %s  (choix: %d)" % [speaker, text.left(40), choices.size()])


func _process(_delta: float) -> bool:
	_frame += 1
	_release_pending()
	if _frame < 3:
		return false
	var player = _game.player
	var dm := root.get_node("DialogueManager")
	match _phase:
		0:
			_game.change_zone("bakery", "entrance", true)
			_phase = 1
			_phase_start = _frame
		1:
			# Monter vers le comptoir ; Émile est derrière.
			Input.action_press("move_up")
			if player.focused != null:
				Input.action_release("move_up")
				print("[dialogue] invite : E — %s" % player.focused.prompt)
				_phase = 2
				_phase_start = _frame
			elif _frame - _phase_start > 300:
				return _finish("aucun Interactable détecté (pos %s)" % player.global_position)
		2:
			if dm.is_active:
				print("[dialogue] dialogue démarré")
				_phase = 3
				_phase_start = _frame
			elif _frame - _phase_start > 60:
				return _finish("le dialogue n'a pas démarré")
			elif (_frame - _phase_start) % 5 == 0:
				_press_once("interact")
		3:
			# Avancer / choisir toutes les 10 frames jusqu'à la fin.
			if (_frame - _phase_start) % 10 == 4:
				if not dm.is_active:
					if _nodes_seen >= 3 and _choices_seen >= 1 and not player.is_moving and _passing_seen:
						return _finish("")
					return _finish("dialogue incomplet (%d noeuds, 2e choix vu : %s)" % [_nodes_seen, _passing_seen])
				# Tester la navigation dans les choix : descendre d'un cran avant de valider.
				if not dm.current_choices().is_empty():
					_press_once("move_down")
				else:
					_press_once("interact")
			elif (_frame - _phase_start) % 10 == 8 and dm.is_active and not dm.current_choices().is_empty():
				_press_once("interact")
			if _frame - _phase_start > 600:
				return _finish("le dialogue ne se termine pas")
	return false


var _to_release: Array[String] = []


## Appui à cette frame, relâchement à la frame suivante (comme une vraie touche).
func _press_once(action: String) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	_to_release.append(action)


func _release_pending() -> void:
	for action in _to_release:
		var up := InputEventAction.new()
		up.action = action
		up.pressed = false
		Input.parse_input_event(up)
	_to_release.clear()


func _finish(error: String) -> bool:
	if error == "":
		print("[dialogue] OK — %d noeuds vus, %d avec choix" % [_nodes_seen, _choices_seen])
		quit(0)
	else:
		push_error("[dialogue] ECHEC : " + error)
		quit(1)
	return true
