class_name TreeProp
extends StaticBody2D
## Arbre simple. Origine au pied du tronc ; seule la base du tronc bloque.

@export var canopy_radius: float = 14.0:
	set(v):
		canopy_radius = v
		queue_redraw()

const COLOR_TRUNK := Color("6b4a2a")
const COLOR_CANOPY := Color("3f7d3a")
const COLOR_CANOPY_LIGHT := Color("5a9a4e")
const COLOR_OUTLINE := Color("1e2e1a")


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
	draw_rect(Rect2(-5, -2, 10, 3), Color(0, 0, 0, 0.2))
	draw_rect(Rect2(-3, -18, 6, 18), COLOR_TRUNK)
	var c := Vector2(0, -18 - canopy_radius * 0.6)
	draw_circle(c, canopy_radius + 1.0, COLOR_OUTLINE)
	draw_circle(c, canopy_radius, COLOR_CANOPY)
	draw_circle(c + Vector2(-canopy_radius * 0.3, -canopy_radius * 0.3), canopy_radius * 0.45, COLOR_CANOPY_LIGHT)
