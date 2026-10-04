class_name Prop
extends StaticBody2D
## Mobilier et petits objets (lit, table, chaise, coffre, four, panneau...).
## Origine au milieu du bas de l'objet (tri en Y). Collision = emprise dessinée.

@export_enum("bed", "table", "chair", "chest", "oven", "counter", "shelf", "barrel", "sign") var kind: String = "table":
	set(v):
		kind = v
		queue_redraw()
## Texte du panneau (kind = "sign").
@export var sign_text: String = "":
	set(v):
		sign_text = v
		queue_redraw()

const SIZES := {
	"bed": Vector2(32, 48),
	"table": Vector2(40, 24),
	"chair": Vector2(14, 16),
	"chest": Vector2(24, 18),
	"oven": Vector2(40, 40),
	"counter": Vector2(64, 20),
	"shelf": Vector2(32, 40),
	"barrel": Vector2(16, 20),
	"sign": Vector2(24, 28),
}

const COLOR_WOOD := Color("8a5a2b")
const COLOR_WOOD_DARK := Color("5c3a1a")
const COLOR_WOOD_LIGHT := Color("b08a5c")
const COLOR_CLOTH := Color("c9544a")
const COLOR_SHEET := Color("e8e2d0")
const COLOR_STONE := Color("8f8f88")
const COLOR_FIRE := Color("e8903a")
const COLOR_METAL := Color("c8b060")
const COLOR_HERB := Color("5a9a4e")
const COLOR_OUTLINE := Color("2a1f17")


func get_size() -> Vector2:
	return SIZES.get(kind, Vector2(16, 16))


func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	var s := get_size()
	var shape := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	# Le panneau ne bloque que par son poteau ; le reste bloque entièrement.
	rs.size = Vector2(6, 6) if kind == "sign" else s
	shape.shape = rs
	shape.position = Vector2(0, -3) if kind == "sign" else Vector2(0, -s.y / 2.0)
	add_child(shape)


func _draw() -> void:
	var s := get_size()
	var r := Rect2(-s.x / 2.0, -s.y, s.x, s.y)
	match kind:
		"bed":
			draw_rect(r, COLOR_WOOD)
			draw_rect(Rect2(r.position.x + 2, r.position.y + 10, s.x - 4, s.y - 12), COLOR_CLOTH)
			draw_rect(Rect2(r.position.x + 2, r.position.y + 2, s.x - 4, 8), COLOR_SHEET)
		"table":
			draw_rect(r, COLOR_WOOD_LIGHT)
			draw_rect(Rect2(r.position.x, r.end.y - 6, s.x, 6), COLOR_WOOD_DARK)
		"chair":
			draw_rect(Rect2(r.position.x, r.position.y, s.x, 6), COLOR_WOOD_DARK)
			draw_rect(Rect2(r.position.x, r.position.y + 6, s.x, s.y - 6), COLOR_WOOD)
		"chest":
			draw_rect(r, COLOR_WOOD)
			draw_rect(Rect2(r.position.x, r.position.y, s.x, 6), COLOR_WOOD_DARK)
			draw_rect(Rect2(-2, r.position.y + 6, 4, 4), COLOR_METAL)
		"oven":
			draw_rect(r, COLOR_STONE)
			draw_rect(Rect2(-10, r.position.y + 18, 20, 12), COLOR_OUTLINE)
			draw_rect(Rect2(-8, r.position.y + 20, 16, 8), COLOR_FIRE)
		"counter":
			draw_rect(r, COLOR_WOOD_LIGHT)
			draw_rect(Rect2(r.position.x, r.end.y - 8, s.x, 8), COLOR_WOOD_DARK)
			# Pains
			for i in 3:
				draw_rect(Rect2(r.position.x + 6 + i * 18, r.position.y + 3, 12, 6), Color("d9a05a"))
		"shelf":
			draw_rect(r, COLOR_WOOD)
			for i in 3:
				var y := r.position.y + 8 + i * 12
				draw_rect(Rect2(r.position.x + 2, y, s.x - 4, 2), COLOR_WOOD_DARK)
				draw_rect(Rect2(r.position.x + 4, y - 6, 6, 6), COLOR_HERB)
				draw_rect(Rect2(r.position.x + 14, y - 6, 6, 6), Color("d9a05a"))
		"barrel":
			draw_rect(r, COLOR_WOOD)
			draw_rect(Rect2(r.position.x, r.position.y + 4, s.x, 2), COLOR_WOOD_DARK)
			draw_rect(Rect2(r.position.x, r.end.y - 6, s.x, 2), COLOR_WOOD_DARK)
		"sign":
			draw_rect(Rect2(-2, -14, 4, 14), COLOR_WOOD_DARK)
			var plank := Rect2(r.position.x, r.position.y, s.x, 14)
			draw_rect(plank, COLOR_WOOD_LIGHT)
			draw_rect(plank, COLOR_OUTLINE, false, 1.0)
			if sign_text != "":
				draw_string(ThemeDB.fallback_font, Vector2(plank.position.x, plank.end.y - 3.0), sign_text,
					HORIZONTAL_ALIGNMENT_CENTER, plank.size.x, 8, COLOR_OUTLINE)
			return
	draw_rect(r, COLOR_OUTLINE, false, 1.0)
