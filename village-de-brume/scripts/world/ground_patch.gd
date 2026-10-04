class_name GroundPatch
extends Node2D
## Rectangle de sol décoratif (chemin de terre, place pavée). Pas de collision.
## Dessiné en tuiles 16x16 avec une bordure légèrement plus sombre.

@export var rect: Rect2 = Rect2(0, 0, 32, 32):
	set(v):
		rect = v
		queue_redraw()
@export_enum("dirt", "stone") var kind: int = 0:
	set(v):
		kind = v
		queue_redraw()

const TILE := 16.0
const COLOR_DIRT := Color("d2b07a")
const COLOR_DIRT_B := Color("c9a66e")
const COLOR_DIRT_EDGE := Color("a88752")
const COLOR_STONE := Color("b9b6aa")
const COLOR_STONE_B := Color("adaa9e")
const COLOR_STONE_EDGE := Color("8a877c")


func _draw() -> void:
	var base_a := COLOR_DIRT if kind == 0 else COLOR_STONE
	var base_b := COLOR_DIRT_B if kind == 0 else COLOR_STONE_B
	var edge := COLOR_DIRT_EDGE if kind == 0 else COLOR_STONE_EDGE
	var cols := int(ceil(rect.size.x / TILE))
	var rows := int(ceil(rect.size.y / TILE))
	for ty in rows:
		for tx in cols:
			var origin := rect.position + Vector2(tx, ty) * TILE
			var tile := Rect2(origin, Vector2(TILE, TILE)).intersection(rect)
			draw_rect(tile, base_a if (tx + ty) % 2 == 0 else base_b)
			if kind == 1:
				# Joints des pavés
				draw_rect(Rect2(tile.position, Vector2(tile.size.x, 1)), edge)
				draw_rect(Rect2(tile.position, Vector2(1, tile.size.y)), edge)
			else:
				var k := (tx * 5 + ty * 3) % 4
				draw_rect(Rect2(origin + Vector2(3 + k * 2, 5 + k), Vector2(2, 2)), edge)
	# Bordure
	draw_rect(rect, edge, false, 1.0)
