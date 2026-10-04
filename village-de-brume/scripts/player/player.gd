class_name Player
extends CharacterBody2D
## Personnage jouable : déplacement 4 directions, direction regardée,
## sonde d'interaction devant lui (E). Bloqué pendant un dialogue.

signal focus_changed(interactable: Interactable)

const SPEED := 80.0
const Facing := CharacterVisual.Facing

var facing: Facing = Facing.DOWN:
	set(v):
		facing = v
		if visual != null:
			visual.facing = v
		_update_probe()
var is_moving := false
var focused: Interactable = null

var _probe: Area2D
var _probe_shape: CollisionShape2D

@onready var camera: Camera2D = $Camera2D
@onready var visual: CharacterVisual = $Visual


func _ready() -> void:
	visual.facing = facing
	_probe = Area2D.new()
	_probe.name = "InteractionProbe"
	_probe.collision_layer = 0
	_probe.collision_mask = 4
	_probe.monitorable = false
	_probe_shape = CollisionShape2D.new()
	_probe_shape.shape = RectangleShape2D.new()
	_probe.add_child(_probe_shape)
	add_child(_probe)
	_update_probe()


func _physics_process(delta: float) -> void:
	var input := Vector2.ZERO
	if not DialogueManager.is_active:
		input = Vector2(
			Input.get_axis("move_left", "move_right"),
			Input.get_axis("move_up", "move_down")
		)
	# Déplacement strictement en 4 directions : si deux axes sont pressés,
	# on garde l'axe de la direction actuelle.
	if input.x != 0.0 and input.y != 0.0:
		if facing == Facing.LEFT or facing == Facing.RIGHT:
			input.y = 0.0
		else:
			input.x = 0.0
	input = input.normalized()

	velocity = input * SPEED
	move_and_slide()

	is_moving = input != Vector2.ZERO
	if is_moving:
		facing = CharacterVisual.facing_from_vector(input, facing)
	visual.animate(delta, is_moving)
	_update_focus()


func _unhandled_input(event: InputEvent) -> void:
	if DialogueManager.is_active:
		return
	if event.is_action_pressed("interact") and focused != null:
		focused.interact(self)
		get_viewport().set_input_as_handled()


func face(direction: Facing) -> void:
	facing = direction


func face_towards(target: Vector2) -> void:
	var d := target - global_position
	if abs(d.x) > abs(d.y):
		facing = Facing.RIGHT if d.x > 0.0 else Facing.LEFT
	else:
		facing = Facing.DOWN if d.y > 0.0 else Facing.UP


## Place la sonde d'interaction devant le personnage.
func _update_probe() -> void:
	if _probe_shape == null:
		return
	var rs := _probe_shape.shape as RectangleShape2D
	match facing:
		Facing.DOWN:
			rs.size = Vector2(12, 24)
			_probe.position = Vector2(0, 12)
		Facing.UP:
			rs.size = Vector2(12, 24)
			_probe.position = Vector2(0, -22)
		Facing.LEFT:
			rs.size = Vector2(24, 12)
			_probe.position = Vector2(-18, -8)
		Facing.RIGHT:
			rs.size = Vector2(24, 12)
			_probe.position = Vector2(18, -8)


func _update_focus() -> void:
	var best: Interactable = null
	var best_dist := INF
	for area in _probe.get_overlapping_areas():
		if area is Interactable:
			var d := global_position.distance_squared_to(area.global_position)
			if d < best_dist:
				best_dist = d
				best = area
	if best != focused:
		focused = best
		focus_changed.emit(focused)
