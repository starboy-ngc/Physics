class_name NPC
extends CharacterBody2D
## Personnage non joueur. Ses données (nom, apparence, dialogue, position)
## viennent d'un fichier JSON chargé par NpcManager ; ce noeud n'est que la
## présence physique du PNJ dans la zone courante.
##
## Déplacements simples : `move_to()` vers un point (utilisé par les horaires
## à l'étape 3) et, optionnellement, une petite errance autour d'un point.

const SPEED := 50.0
const Facing := CharacterVisual.Facing

var npc_id: String = ""
var display_name: String = "???"
var dialogue_path: String = ""
var wander_radius: float = 0.0
var home_position: Vector2

var facing: Facing = Facing.DOWN:
	set(v):
		facing = v
		if visual != null:
			visual.facing = v

var _target: Vector2
var _has_target := false
var _wander_timer := 0.0
var _blocked_time := 0.0
var _talking := false
var _rng := RandomNumberGenerator.new()

@onready var visual: CharacterVisual = $Visual
@onready var talk_area = $TalkArea


func _ready() -> void:
	visual.facing = facing
	home_position = global_position
	_rng.seed = hash(npc_id)
	_wander_timer = _rng.randf_range(1.0, 3.0)
	talk_area.prompt = "Parler"
	talk_area.interact_callback = _on_interact


## Applique un dictionnaire de données (voir data/npcs/*.json).
func apply_data(data: Dictionary) -> void:
	npc_id = str(data.get("id", npc_id))
	display_name = str(data.get("name", display_name))
	dialogue_path = str(data.get("dialogue", ""))
	wander_radius = float(data.get("wander_radius", 0.0))
	var look: Dictionary = data.get("appearance", {})
	if visual == null:
		await ready
	if look.has("tunic"):
		visual.tunic_color = Color(str(look["tunic"]))
	if look.has("hair"):
		visual.hair_color = Color(str(look["hair"]))
	if look.has("skin"):
		visual.skin_color = Color(str(look["skin"]))
	if look.has("pants"):
		visual.pants_color = Color(str(look["pants"]))
	visual.queue_redraw()


func move_to(target: Vector2) -> void:
	_target = target
	_has_target = true
	_blocked_time = 0.0


func stop() -> void:
	_has_target = false
	velocity = Vector2.ZERO


func face_towards(point: Vector2) -> void:
	var d := point - global_position
	if abs(d.x) > abs(d.y):
		facing = Facing.RIGHT if d.x > 0.0 else Facing.LEFT
	else:
		facing = Facing.DOWN if d.y > 0.0 else Facing.UP


func _physics_process(delta: float) -> void:
	if _talking:
		velocity = Vector2.ZERO
		visual.animate(delta, false)
		return

	if not _has_target and wander_radius > 0.0:
		_wander_timer -= delta
		if _wander_timer <= 0.0:
			_wander_timer = _rng.randf_range(2.0, 5.0)
			var offset := Vector2(_rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0)) * wander_radius
			# Errance en lignes droites (4 directions) : on ne garde qu'un axe.
			if abs(offset.x) > abs(offset.y):
				offset.y = 0.0
			else:
				offset.x = 0.0
			move_to(home_position + offset)

	var moving := false
	if _has_target:
		var to_target := _target - global_position
		if to_target.length() < 2.0:
			stop()
		else:
			# Un axe à la fois : d'abord le plus long.
			var dir := Vector2.ZERO
			if abs(to_target.x) > 1.0:
				dir.x = sign(to_target.x)
			else:
				dir.y = sign(to_target.y)
			velocity = dir * SPEED
			var before := global_position
			move_and_slide()
			moving = true
			facing = CharacterVisual.facing_from_vector(dir, facing)
			if global_position.distance_to(before) < 0.1:
				_blocked_time += delta
				if _blocked_time > 0.5:
					stop()  # obstacle : on abandonne cette destination
	if not moving:
		velocity = Vector2.ZERO
	visual.animate(delta, moving)


func _on_interact(player: Node2D) -> void:
	if dialogue_path == "":
		return
	var data := DialogueData.load_from_file(dialogue_path)
	if data == null:
		return
	if DialogueManager.start(data, display_name):
		_talking = true
		stop()
		face_towards(player.global_position)
		if player is Player:
			player.face_towards(global_position)
		DialogueManager.dialogue_ended.connect(_on_dialogue_ended, CONNECT_ONE_SHOT)


func _on_dialogue_ended(_id: String) -> void:
	_talking = false
