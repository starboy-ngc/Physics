class_name Building
extends StaticBody2D
## Maison vue de l'extérieur en 3/4 : toit vu de dessus (deux pans), avancée
## de toit, murs, porte, fenêtres, enseigne. L'origine est au milieu du bas
## des murs. La porte (Door) est créée automatiquement devant le bâtiment.

@export var size: Vector2 = Vector2(96, 72):
	set(v):
		size = v
		queue_redraw()
@export var wall_color: Color = Color("e9dcc0"):
	set(v):
		wall_color = v
		queue_redraw()
@export var roof_color: Color = Color("b0503e"):
	set(v):
		roof_color = v
		queue_redraw()
@export var label: String = "":
	set(v):
		label = v
		queue_redraw()
@export var door_target_zone: String = ""
@export var door_target_spawn: String = "entrance"

const ROOF_HEIGHT := 36.0
const ROOF_OVERHANG := 8.0
const DOOR_SIZE := Vector2(16, 26)
const COLOR_OUTLINE := Color("2a1f17")
const COLOR_DOOR := Color("5a3a22")
const COLOR_DOOR_FRAME := Color("8a6a4a")
const COLOR_WINDOW := Color("8fc6e8")
const COLOR_WINDOW_DARK := Color("4a7aa8")
const COLOR_SIGN := Color("c9a66e")
const COLOR_STEP := Color("a8a49a")


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

	# Ombre portée au sol
	draw_rect(Rect2(-w / 2.0 - 2.0, -3.0, w + 4.0, 5.0), Color(0, 0, 0, 0.18))

	# Murs + soubassement
	draw_rect(walls, wall_color)
	draw_rect(Rect2(walls.position.x, walls.end.y - 6.0, w, 6.0), wall_color.darkened(0.3))
	# Ombre sous l'avancée du toit
	draw_rect(Rect2(walls.position.x, walls.position.y, w, 5.0), wall_color.darkened(0.2))

	# Toit : deux pans vus de dessus (gauche plus clair, droite plus sombre)
	var top := -h - ROOF_HEIGHT
	var left := -w / 2.0 - ROOF_OVERHANG
	var right := w / 2.0 + ROOF_OVERHANG
	var ridge_y := top + 6.0
	var pan_left := PackedVector2Array([
		Vector2(left, -h + 4.0), Vector2(0, -h + 4.0), Vector2(0, ridge_y), Vector2(left + 10.0, top),
	])
	var pan_right := PackedVector2Array([
		Vector2(0, -h + 4.0), Vector2(right, -h + 4.0), Vector2(right - 10.0, top), Vector2(0, ridge_y),
	])
	draw_colored_polygon(pan_left, roof_color.lightened(0.08))
	draw_colored_polygon(pan_right, roof_color.darkened(0.12))
	# Tuiles : lignes horizontales
	var ty := -h
	while ty > top + 8.0:
		var t := (ty - (-h + 4.0)) / (top - (-h + 4.0))
		var inset := 10.0 * t
		draw_line(Vector2(left + inset, ty), Vector2(right - inset, ty), roof_color.darkened(0.3), 1.0)
		ty -= 6.0
	# Faîtage et bord du toit
	draw_rect(Rect2(left + 10.0, top - 2.0, w + 2.0 * ROOF_OVERHANG - 20.0, 3.0), roof_color.darkened(0.4))
	draw_rect(Rect2(left, -h + 2.0, right - left, 3.0), roof_color.darkened(0.45))
	draw_polyline(PackedVector2Array([Vector2(left, -h + 4.0), Vector2(left + 10.0, top), Vector2(right - 10.0, top), Vector2(right, -h + 4.0)]), COLOR_OUTLINE, 1.0)

	# Fenêtres
	var win := Vector2(14, 12)
	for wx in [-w / 2.0 + 12.0, w / 2.0 - 12.0 - win.x]:
		var r := Rect2(wx, -h + 26.0, win.x, win.y)
		draw_rect(r, COLOR_WINDOW)
		draw_rect(Rect2(r.position + Vector2(2, 2), Vector2(4, 3)), Color.WHITE)
		draw_rect(Rect2(r.position.x, r.get_center().y, win.x, 1), COLOR_WINDOW_DARK)
		draw_rect(Rect2(r.get_center().x, r.position.y, 1, win.y), COLOR_WINDOW_DARK)
		draw_rect(r, COLOR_OUTLINE, false, 1.0)
		draw_rect(Rect2(r.position.x - 1.0, r.end.y, win.x + 2.0, 2.0), wall_color.darkened(0.4))  # rebord

	# Porte avec encadrement, et marche devant
	var door := Rect2(-DOOR_SIZE.x / 2.0, -DOOR_SIZE.y, DOOR_SIZE.x, DOOR_SIZE.y)
	draw_rect(door.grow(2.0), COLOR_DOOR_FRAME)
	draw_rect(door, COLOR_DOOR)
	draw_rect(Rect2(door.position.x + 2.0, door.position.y + 2.0, DOOR_SIZE.x - 4.0, 6.0), COLOR_DOOR.lightened(0.15))
	draw_rect(Rect2(3.0, -DOOR_SIZE.y / 2.0, 2.0, 2.0), Color("e0c060"))
	draw_rect(door.grow(2.0), COLOR_OUTLINE, false, 1.0)
	draw_rect(Rect2(-DOOR_SIZE.x / 2.0 - 3.0, 0.0, DOOR_SIZE.x + 6.0, 4.0), COLOR_STEP)
	draw_rect(Rect2(-DOOR_SIZE.x / 2.0 - 3.0, 0.0, DOOR_SIZE.x + 6.0, 4.0), COLOR_OUTLINE, false, 1.0)

	# Contour des murs
	draw_rect(walls, COLOR_OUTLINE, false, 1.0)

	# Enseigne
	if label != "":
		var font := ThemeDB.fallback_font
		var sign_rect := Rect2(-30.0, -h + 8.0, 60.0, 12.0)
		draw_rect(sign_rect, COLOR_SIGN)
		draw_rect(sign_rect, COLOR_OUTLINE, false, 1.0)
		draw_string(font, Vector2(sign_rect.position.x, sign_rect.end.y - 3.0), label,
			HORIZONTAL_ALIGNMENT_CENTER, sign_rect.size.x, 8, COLOR_OUTLINE)
