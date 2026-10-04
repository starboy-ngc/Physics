extends Zone
## Intérieur d'une maison : sol en planches, mur du fond, bordure.
## Les meubles sont des Prop placés dans la scène ; la sortie est un Door.

@export var floor_color: Color = Color("c89a62")
@export var wall_color: Color = Color("e6d5b8")

const COLOR_PLANK := Color("b3864f")
const COLOR_OUTLINE := Color("2a1f17")


func _draw() -> void:
	# Sol
	draw_rect(bounds, floor_color)
	var y := bounds.position.y + 16.0
	while y < bounds.end.y:
		draw_line(Vector2(bounds.position.x, y), Vector2(bounds.end.x, y), COLOR_PLANK, 1.0)
		y += 16.0
	# Mur du fond
	draw_rect(Rect2(bounds.position, Vector2(bounds.size.x, wall_top)), wall_color)
	draw_rect(Rect2(bounds.position.x, bounds.position.y + wall_top - 4.0, bounds.size.x, 4.0), wall_color.darkened(0.35))
	# Bordure de la pièce
	draw_rect(bounds, COLOR_OUTLINE, false, 2.0)
