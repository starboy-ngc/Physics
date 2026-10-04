class_name CharacterVisual
extends Node2D
## Dessin d'un personnage (joueur ou PNJ) : proportions « tête large » façon
## RPG portable, contour sombre, 4 directions, marche en 2 poses.
## Origine aux pieds. Les couleurs sont paramétrables par personnage.

enum Facing { DOWN, UP, LEFT, RIGHT }

@export var tunic_color: Color = Color("3a6ea5")
@export var hair_color: Color = Color("5a3a22")
@export var skin_color: Color = Color("f1c9a5")
@export var pants_color: Color = Color("2a2a3a")

const COLOR_OUTLINE := Color("1e1e2e")
const COLOR_SHADOW := Color(0, 0, 0, 0.25)
const WALK_ANIM_FPS := 8.0

var facing: Facing = Facing.DOWN:
	set(v):
		facing = v
		queue_redraw()
var is_moving := false
var _walk_time := 0.0


func animate(delta: float, moving: bool) -> void:
	is_moving = moving
	if moving:
		_walk_time += delta
	else:
		_walk_time = 0.0
	queue_redraw()


func _draw() -> void:
	var step := int(_walk_time * WALK_ANIM_FPS) % 2 if is_moving else -1
	var bob := -1 if step >= 0 else 0  # léger rebond pendant la marche

	# Ombre
	draw_rect(Rect2(-7, -2, 14, 3), COLOR_SHADOW)

	# Jambes
	var left_h := 7 - (3 if step == 1 else 0)
	var right_h := 7 - (3 if step == 0 else 0)
	draw_rect(Rect2(-5, -7, 4, left_h), pants_color)
	draw_rect(Rect2(1, -7, 4, right_h), pants_color)
	draw_rect(Rect2(-5, -7, 4, left_h), COLOR_OUTLINE, false, 1.0)
	draw_rect(Rect2(1, -7, 4, right_h), COLOR_OUTLINE, false, 1.0)

	# Corps
	var body := Rect2(-6, -15 + bob, 12, 9)
	draw_rect(body, tunic_color)
	draw_rect(body, COLOR_OUTLINE, false, 1.0)
	# Bras
	if facing == Facing.LEFT or facing == Facing.RIGHT:
		draw_rect(Rect2(-2, -13 + bob, 4, 6), tunic_color.darkened(0.2))
	else:
		draw_rect(Rect2(-8, -13 + bob, 2, 6), skin_color)
		draw_rect(Rect2(6, -13 + bob, 2, 6), skin_color)

	# Tête (large, façon RPG portable)
	var head := Rect2(-7, -26 + bob, 14, 12)
	draw_rect(head, skin_color)
	draw_rect(head, COLOR_OUTLINE, false, 1.0)

	# Cheveux et yeux selon la direction
	var hy := head.position.y
	match facing:
		Facing.UP:
			draw_rect(Rect2(-7, hy, 14, 9), hair_color)
		Facing.DOWN:
			draw_rect(Rect2(-7, hy, 14, 4), hair_color)
			draw_rect(Rect2(-7, hy + 4, 2, 3), hair_color)
			draw_rect(Rect2(5, hy + 4, 2, 3), hair_color)
			draw_rect(Rect2(-4, hy + 6, 2, 3), COLOR_OUTLINE)
			draw_rect(Rect2(2, hy + 6, 2, 3), COLOR_OUTLINE)
		Facing.LEFT:
			draw_rect(Rect2(-7, hy, 14, 4), hair_color)
			draw_rect(Rect2(-1, hy, 8, 8), hair_color)
			draw_rect(Rect2(-5, hy + 6, 2, 3), COLOR_OUTLINE)
		Facing.RIGHT:
			draw_rect(Rect2(-7, hy, 14, 4), hair_color)
			draw_rect(Rect2(-7, hy, 8, 8), hair_color)
			draw_rect(Rect2(3, hy + 6, 2, 3), COLOR_OUTLINE)
	draw_rect(head, COLOR_OUTLINE, false, 1.0)


static func facing_from_vector(v: Vector2, current: Facing) -> Facing:
	if v.y > 0.0:
		return Facing.DOWN
	if v.y < 0.0:
		return Facing.UP
	if v.x > 0.0:
		return Facing.RIGHT
	if v.x < 0.0:
		return Facing.LEFT
	return current


static func facing_from_string(s: String) -> Facing:
	match s.to_lower():
		"up": return Facing.UP
		"left": return Facing.LEFT
		"right": return Facing.RIGHT
		_: return Facing.DOWN
