class_name Well
extends StaticBody2D
## Puits de la place centrale. Origine au bas de la margelle.

const COLOR_STONE := Color("8f8f88")
const COLOR_STONE_DARK := Color("5c5c58")
const COLOR_WATER := Color("2f5f8f")
const COLOR_WOOD := Color("6b4a2a")
const COLOR_ROOF := Color("8c4a3c")
const COLOR_OUTLINE := Color("2a2a2a")


func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	var shape := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(32, 20)
	shape.shape = rs
	shape.position = Vector2(0, -8)
	add_child(shape)


func _draw() -> void:
	# Margelle
	draw_rect(Rect2(-16, -18, 32, 18), COLOR_STONE)
	draw_rect(Rect2(-16, -18, 32, 18), COLOR_OUTLINE, false, 1.0)
	draw_rect(Rect2(-12, -16, 24, 8), COLOR_WATER)
	draw_rect(Rect2(-16, -4, 32, 4), COLOR_STONE_DARK)
	# Poteaux et petit toit
	draw_rect(Rect2(-14, -44, 3, 28), COLOR_WOOD)
	draw_rect(Rect2(11, -44, 3, 28), COLOR_WOOD)
	var roof := PackedVector2Array([
		Vector2(-20, -42), Vector2(20, -42), Vector2(0, -56),
	])
	draw_colored_polygon(roof, COLOR_ROOF)
	draw_polyline(roof + PackedVector2Array([roof[0]]), COLOR_OUTLINE, 1.0)
