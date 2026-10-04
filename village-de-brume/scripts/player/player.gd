class_name Player
extends CharacterBody2D
## Personnage jouable : déplacement 4 directions, direction regardée,
## animation de marche simple (dessinée en code, sans asset pour le prototype).
## L'origine du noeud est aux pieds du personnage (tri en Y).

enum Facing { DOWN, UP, LEFT, RIGHT }

const SPEED := 90.0
const WALK_ANIM_FPS := 8.0

const COLOR_OUTLINE := Color("1e1e2e")
const COLOR_TUNIC := Color("3a6ea5")
const COLOR_SKIN := Color("f1c9a5")
const COLOR_HAIR := Color("5a3a22")
const COLOR_SHADOW := Color(0, 0, 0, 0.25)

var facing: Facing = Facing.DOWN
var is_moving := false

var _walk_time := 0.0

@onready var camera: Camera2D = $Camera2D


func _physics_process(delta: float) -> void:
	var input := Vector2(
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
		_update_facing(input)
		_walk_time += delta
	else:
		_walk_time = 0.0
	queue_redraw()


func face(direction: Facing) -> void:
	facing = direction
	queue_redraw()


func _update_facing(input: Vector2) -> void:
	if input.y > 0.0:
		facing = Facing.DOWN
	elif input.y < 0.0:
		facing = Facing.UP
	elif input.x > 0.0:
		facing = Facing.RIGHT
	elif input.x < 0.0:
		facing = Facing.LEFT


func _draw() -> void:
	var step := int(_walk_time * WALK_ANIM_FPS) % 2 if is_moving else -1

	# Ombre au sol
	draw_rect(Rect2(-6, -2, 12, 3), COLOR_SHADOW)

	# Jambes (alternance pendant la marche)
	var left_h := 6 - (2 if step == 1 else 0)
	var right_h := 6 - (2 if step == 0 else 0)
	draw_rect(Rect2(-5, -6, 4, left_h), COLOR_OUTLINE)
	draw_rect(Rect2(1, -6, 4, right_h), COLOR_OUTLINE)

	# Corps
	draw_rect(Rect2(-6, -14, 12, 9), COLOR_TUNIC)
	draw_rect(Rect2(-6, -14, 12, 9), COLOR_OUTLINE, false, 1.0)

	# Tête
	draw_rect(Rect2(-5, -23, 10, 9), COLOR_SKIN)
	draw_rect(Rect2(-5, -23, 10, 9), COLOR_OUTLINE, false, 1.0)

	# Cheveux et yeux selon la direction regardée
	match facing:
		Facing.UP:
			draw_rect(Rect2(-5, -23, 10, 7), COLOR_HAIR)
		Facing.DOWN:
			draw_rect(Rect2(-5, -23, 10, 3), COLOR_HAIR)
			draw_rect(Rect2(-3, -18, 2, 2), COLOR_OUTLINE)
			draw_rect(Rect2(1, -18, 2, 2), COLOR_OUTLINE)
		Facing.LEFT:
			draw_rect(Rect2(-5, -23, 10, 3), COLOR_HAIR)
			draw_rect(Rect2(-1, -23, 6, 6), COLOR_HAIR)
			draw_rect(Rect2(-4, -18, 2, 2), COLOR_OUTLINE)
		Facing.RIGHT:
			draw_rect(Rect2(-5, -23, 10, 3), COLOR_HAIR)
			draw_rect(Rect2(-5, -23, 6, 6), COLOR_HAIR)
			draw_rect(Rect2(2, -18, 2, 2), COLOR_OUTLINE)
