class_name TreeProp
extends StaticBody2D
## Arbre : tronc, feuillage en trois nuances avec contour. Origine au pied.

@export var canopy_radius: float = 14.0:
	set(v):
		canopy_radius = v
		queue_redraw()

const COLOR_TRUNK := Color("7a4e2a")
const COLOR_TRUNK_DARK := Color("4e3018")
const COLOR_CANOPY := Color("3f8a3a")
const COLOR_CANOPY_DARK := Color("2f6a2c")
const COLOR_CANOPY_LIGHT := Color("66b154")
const COLOR_OUTLINE := Color("1e3a1a")


func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	var shape := CollisionShape2D.new()
	var cs := CircleShape2D.new()
	cs.radius = 6.0
	shape.shape = cs
	shape.position = Vector2(0, -4)
	add_child(shape)


func _draw() -> void:
	draw_rect(Rect2(-6, -2, 12, 3), Color(0, 0, 0, 0.2))
	draw_rect(Rect2(-3, -18, 6, 18), COLOR_TRUNK)
	draw_rect(Rect2(-3, -18, 2, 18), COLOR_TRUNK_DARK)
	var r := canopy_radius
	var c := Vector2(0, -18 - r * 0.7)
	# Contour puis deux couches de feuillage, et une boule claire en haut à gauche
	draw_circle(c, r + 1.5, COLOR_OUTLINE)
	draw_circle(c, r, COLOR_CANOPY_DARK)
	draw_circle(c + Vector2(-r * 0.15, -r * 0.2), r * 0.85, COLOR_CANOPY)
	draw_circle(c + Vector2(-r * 0.35, -r * 0.4), r * 0.4, COLOR_CANOPY_LIGHT)
	draw_circle(c + Vector2(r * 0.3, -r * 0.1), r * 0.25, COLOR_CANOPY_LIGHT.darkened(0.1))
