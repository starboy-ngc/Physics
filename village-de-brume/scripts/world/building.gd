class_name Building
extends StaticBody2D
## Maison vue de l'extérieur. L'origine est au milieu du bas des murs.
## La porte (Door) est créée automatiquement devant le bâtiment si
## `door_target_zone` est renseigné.

@export var size: Vector2 = Vector2(96, 80):
	set(v):
		size = v
		queue_redraw()
@export var wall_color: Color = Color("d9c7a3"):
	set(v):
		wall_color = v
		queue_redraw()
@export var roof_color: Color = Color("8c4a3c"):
	set(v):
		roof_color = v
		queue_redraw()
@export var label: String = "":
	set(v):
		label = v
		queue_redraw()
@export var door_target_zone: String = ""
@export var door_target_spawn: String = "entrance"

const ROOF_HEIGHT := 28.0
const DOOR_SIZE := Vector2(16, 24)
const COLOR_OUTLINE := Color("2a1f17")
const COLOR_DOOR := Color("4a3220")
const COLOR_WINDOW := Color("7fb2d9")
const COLOR_SIGN := Color("b08a5c")


func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	var shape := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	shape.shape = rs
	shape.position = Vector2(0, -size.y / 2.0)
	add_child(shape)

	if door_target_zone != "" and not Engine.is_editor_hint():
		var door := Door.new()
		door.name = "Door"
		door.target_zone = door_target_zone
		door.target_spawn = door_target_spawn
		door.size = Vector2(14, 8)
		door.position = Vector2(0, 6)
		add_child(door)


func _draw() -> void:
	var w := size.x
	var h := size.y
	var walls := Rect2(-w / 2.0, -h, w, h)

	# Murs
	draw_rect(walls, wall_color)
	# Toit (trapèze)
	var roof := PackedVector2Array([
		Vector2(-w / 2.0 - 6.0, -h),
		Vector2(w / 2.0 + 6.0, -h),
		Vector2(w / 2.0 - 10.0, -h - ROOF_HEIGHT),
		Vector2(-w / 2.0 + 10.0, -h - ROOF_HEIGHT),
	])
	draw_colored_polygon(roof, roof_color)
	draw_polyline(roof + PackedVector2Array([roof[0]]), COLOR_OUTLINE, 1.0)
	# Bord du toit
	draw_rect(Rect2(-w / 2.0 - 6.0, -h - 2.0, w + 12.0, 4.0), roof_color.darkened(0.25))

	# Fenêtres
	var win := Vector2(12, 12)
	draw_rect(Rect2(-w / 2.0 + 14.0, -h + 20.0, win.x, win.y), COLOR_WINDOW)
	draw_rect(Rect2(w / 2.0 - 26.0, -h + 20.0, win.x, win.y), COLOR_WINDOW)
	draw_rect(Rect2(-w / 2.0 + 14.0, -h + 20.0, win.x, win.y), COLOR_OUTLINE, false, 1.0)
	draw_rect(Rect2(w / 2.0 - 26.0, -h + 20.0, win.x, win.y), COLOR_OUTLINE, false, 1.0)

	# Porte
	draw_rect(Rect2(-DOOR_SIZE.x / 2.0, -DOOR_SIZE.y, DOOR_SIZE.x, DOOR_SIZE.y), COLOR_DOOR)
	draw_rect(Rect2(2.0, -DOOR_SIZE.y / 2.0, 2.0, 2.0), Color("e0c060"))  # poignée

	# Contour des murs
	draw_rect(walls, COLOR_OUTLINE, false, 1.0)

	# Enseigne au-dessus de la porte
	if label != "":
		var font := ThemeDB.fallback_font
		var sign_rect := Rect2(-30.0, -DOOR_SIZE.y - 16.0, 60.0, 12.0)
		draw_rect(sign_rect, COLOR_SIGN)
		draw_rect(sign_rect, COLOR_OUTLINE, false, 1.0)
		draw_string(font, Vector2(sign_rect.position.x, sign_rect.end.y - 3.0), label,
			HORIZONTAL_ALIGNMENT_CENTER, sign_rect.size.x, 8, COLOR_OUTLINE)
