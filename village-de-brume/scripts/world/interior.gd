extends Zone
## Intérieur d'une maison : sol en planches, mur du fond avec plinthe,
## bordure. Les meubles sont des Prop placés dans la scène ; la sortie est un Door.

@export var floor_color: Color = Color("c89a62")
@export var wall_color: Color = Color("e6d5b8")

const COLOR_OUTLINE := Color("2a1f17")


func _draw() -> void:
	# Sol : planches horizontales de 16 px, alternance de deux teintes
	var y := bounds.position.y
	var i := 0
	while y < bounds.end.y:
		var c := floor_color if i % 2 == 0 else floor_color.darkened(0.06)
		draw_rect(Rect2(bounds.position.x, y, bounds.size.x, 16.0), c)
		draw_rect(Rect2(bounds.position.x, y, bounds.size.x, 1.0), floor_color.darkened(0.25))
		# Jointures décalées une planche sur deux
		var x := bounds.position.x + (24.0 if i % 2 == 0 else 56.0)
		while x < bounds.end.x:
			draw_rect(Rect2(x, y + 2.0, 1.0, 12.0), floor_color.darkened(0.2))
			x += 64.0
		y += 16.0
		i += 1
	# Mur du fond : papier peint rayé + plinthe
	var wall := Rect2(bounds.position, Vector2(bounds.size.x, wall_top))
	draw_rect(wall, wall_color)
	var sx := bounds.position.x
	while sx < bounds.end.x:
		draw_rect(Rect2(sx, wall.position.y, 4.0, wall_top - 6.0), wall_color.darkened(0.06))
		sx += 16.0
	draw_rect(Rect2(wall.position.x, wall.end.y - 6.0, wall.size.x, 6.0), wall_color.darkened(0.35))
	draw_rect(Rect2(wall.position.x, wall.end.y - 6.0, wall.size.x, 1.0), COLOR_OUTLINE)
	# Bordure de la pièce
	draw_rect(bounds, COLOR_OUTLINE, false, 2.0)
