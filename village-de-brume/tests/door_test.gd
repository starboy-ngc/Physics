extends SceneTree
## Test des portes, sans fenêtre :
##   godot --headless --path . -s tests/door_test.gd
## Le joueur part de sa maison, marche vers le bas jusqu'à la porte de sortie
## et doit se retrouver dans le village. Puis il remonte et doit rentrer.

var _game: Node
var _frame := 0
var _phase := 0
var _phase_start := 0


func _initialize() -> void:
	_game = root.get_node_or_null("Game")
	if _game == null:
		push_error("[door] autoload Game introuvable")
		quit(1)
		return
	Engine.max_fps = 60  # les délais du jeu sont en temps réel
	root.add_child(load("res://scenes/main/Main.tscn").instantiate())


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	match _phase:
		0:
			# Marcher vers le bas depuis le point "start" de la maison (x=96) :
			# on se décale d'abord vers la porte (x=128) puis on descend.
			var p: Player = _game.player
			if p.global_position.x < 127.0:
				_press_only("move_right")
			else:
				_press_only("move_down")
			if _game.current_zone_id == "village":
				_release_all()
				print("[door] sortie de la maison OK -> %s, joueur=%s" % [_game.current_zone_id, p.global_position])
				_phase = 1
				_phase_start = _frame
			elif _frame - _phase_start > 600:
				return _finish("le joueur n'a pas atteint la porte de sortie (pos %s)" % p.global_position)
		1:
			# Attendre la fin de la transition (fondu).
			if _frame - _phase_start > 30:
				_phase = 2
				_phase_start = _frame
		2:
			_press_only("move_up")
			if _game.current_zone_id == "house_player":
				_release_all()
				print("[door] retour dans la maison OK, joueur=%s" % (_game.player as Player).global_position)
				return _finish("")
			elif _frame - _phase_start > 600:
				return _finish("le joueur n'a pas pu rentrer dans la maison")
	return false


func _press_only(action: String) -> void:
	for a in ["move_up", "move_down", "move_left", "move_right"]:
		if a == action:
			Input.action_press(a)
		else:
			Input.action_release(a)


func _release_all() -> void:
	_press_only("")


func _finish(error: String) -> bool:
	if error == "":
		print("[door] OK")
		quit(0)
	else:
		push_error("[door] ECHEC : " + error)
		quit(1)
	return true
