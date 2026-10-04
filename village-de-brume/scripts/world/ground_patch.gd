class_name GroundPatch
extends Node2D
## Rectangle de sol décoratif (chemin de terre, place pavée). Pas de collision.

@export var rect: Rect2 = Rect2(0, 0, 32, 32):
	set(v):
		rect = v
		queue_redraw()
@export_enum("dirt", "stone") var kind: int = 0:
	set(v):
		kind = v
		queue_redraw()

const COLOR_DIRT := Color("b08a5c")
const COLOR_DIRT_DARK := Color("9a7549")
const COLOR_STONE := Color("9a9a93")
const COLOR_STONE_DARK := Color("82827c")


func _draw() -> void:
	match kind:
		0:
			draw_rect(rect, COLOR_DIRT)
			# Quelques cailloux déterministes
			var rng := RandomNumberGenerator.new()
			rng.seed = int(rect.position.x * 31 + rect.position.y * 17)
			var count := int(rect.get_area() / 400.0)
			for i in count:
				var p := rect.position + Vector2(rng.randf() * (rect.size.x - 2.0), rng.randf() * (rect.size.y - 2.0))
				draw_rect(Rect2(p, Vector2(2, 2)), COLOR_DIRT_DARK)
		1:
			draw_rect(rect, COLOR_STONE)
			var x := rect.position.x
			while x <= rect.end.x:
				draw_line(Vector2(x, rect.position.y), Vector2(x, rect.end.y), COLOR_STONE_DARK, 1.0)
				x += 16.0
			var y := rect.position.y
			while y <= rect.end.y:
				draw_line(Vector2(rect.position.x, y), Vector2(rect.end.x, y), COLOR_STONE_DARK, 1.0)
				y += 16.0
