extends SceneTree
## Test de fumée, sans fenêtre :
##   godot --headless --path . -s tests/smoke_test.gd
## Charge la scène principale, visite toutes les zones dans l'ordre d'un
## parcours de jeu et vérifie que le joueur apparaît au bon endroit.

const STEPS := [
	["village", "from_house_player"],
	["bakery", "entrance"],
	["village", "from_bakery"],
	["house_jeanne", "entrance"],
	["village", "from_house_jeanne"],
	["house_martin", "entrance"],
	["village", "from_house_martin"],
	["house_player", "entrance"],
]

var _game: Node
var _frame := 0
var _step := 0
var _failures := 0


func _initialize() -> void:
	_game = root.get_node_or_null("Game")
	if _game == null:
		push_error("[smoke] autoload Game introuvable")
		quit(1)
		return
	var main: Node = load("res://scenes/main/Main.tscn").instantiate()
	root.add_child(main)
	print("[smoke] scène principale chargée")


func _process(_delta: float) -> bool:
	_frame += 1
	# Laisser quelques frames entre chaque changement pour que la physique tourne.
	if _frame % 5 != 0:
		return false
	if _step == 0:
		_check_zone("house_player", "start")
	if _step < STEPS.size():
		var step: Array = STEPS[_step]
		_game.change_zone(step[0], step[1], true)
		_check_zone(step[0], step[1])
		_step += 1
		return false
	if _failures == 0:
		print("[smoke] OK — %d zones visitées sans erreur" % (STEPS.size() + 1))
	else:
		print("[smoke] ECHEC — %d problème(s)" % _failures)
	quit(1 if _failures > 0 else 0)
	return true


func _check_zone(zone_id: String, spawn_name: String) -> void:
	var zone: Zone = _game.current_zone
	if zone == null or _game.current_zone_id != zone_id:
		_fail("zone attendue '%s', obtenue '%s'" % [zone_id, _game.current_zone_id])
		return
	if (_game.player as Player).get_parent() != zone:
		_fail("le joueur n'est pas dans la zone '%s'" % zone_id)
	var expected: Vector2 = zone.get_spawn_position(spawn_name)
	if (_game.player as Player).global_position.distance_to(expected) > 0.5:
		_fail("position du joueur %s != spawn %s dans '%s'" % [(_game.player as Player).global_position, expected, zone_id])
	if not zone.bounds.has_point((_game.player as Player).global_position):
		_fail("le joueur est hors des limites de '%s'" % zone_id)
	if zone.get_node_or_null("Boundaries") == null:
		_fail("pas de murs invisibles dans '%s'" % zone_id)
	print("[smoke] %-14s spawn=%-18s joueur=%s" % [zone_id, spawn_name, (_game.player as Player).global_position])


func _fail(msg: String) -> void:
	_failures += 1
	push_error("[smoke] " + msg)
