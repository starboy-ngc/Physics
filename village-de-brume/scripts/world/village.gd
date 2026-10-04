extends Zone
## Le Village de Brume : herbe en tuiles, arbres en bordure (placés
## automatiquement), sortie vers la forêt sur le bord droit (étape 5).

const TREE_SCENE := preload("res://scenes/world/props/Tree.tscn")
const TILE := 16.0

@export var border_trees: bool = true
## Rectangle (en pixels) sans arbre de bordure : ouverture vers la forêt.
@export var exit_gap: Rect2 = Rect2(700, 250, 80, 90)

const COLOR_GRASS_A := Color("6fae4e")
const COLOR_GRASS_B := Color("68a548")
const COLOR_GRASS_MARK := Color("5a9440")
const COLOR_GRASS_LIGHT := Color("86c25f")


func _ready() -> void:
	super()
	if border_trees:
		_place_border_trees()


func _place_border_trees() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 1234
	var holder := Node2D.new()
	holder.name = "BorderTrees"
	holder.y_sort_enabled = true
	add_child(holder)

	var positions: Array[Vector2] = []
	var x := bounds.position.x + 40.0
	while x <= bounds.end.x - 40.0:
		positions.append(Vector2(x, bounds.position.y + 60.0))
		positions.append(Vector2(x, bounds.end.y - 16.0))
		x += 48.0
	var y := bounds.position.y + 88.0
	while y <= bounds.end.y - 64.0:
		positions.append(Vector2(bounds.position.x + 40.0, y))
		positions.append(Vector2(bounds.end.x - 40.0, y))
		y += 48.0

	for p in positions:
		if exit_gap.has_point(p):
			continue
		var tree := TREE_SCENE.instantiate()
		tree.position = p + Vector2(rng.randf_range(-6.0, 6.0), rng.randf_range(-4.0, 4.0))
		tree.canopy_radius = rng.randf_range(12.0, 16.0)
		holder.add_child(tree)


func _draw() -> void:
	# Herbe en damier discret de tuiles 16x16, avec petites marques.
	var cols := int(ceil(bounds.size.x / TILE))
	var rows := int(ceil(bounds.size.y / TILE))
	for ty in rows:
		for tx in cols:
			var origin := bounds.position + Vector2(tx, ty) * TILE
			var c := COLOR_GRASS_A if (tx + ty) % 2 == 0 else COLOR_GRASS_B
			draw_rect(Rect2(origin, Vector2(TILE, TILE)), c)
			# Deux brins par tuile, placés de façon déterministe.
			var k := (tx * 7 + ty * 13) % 5
			draw_rect(Rect2(origin + Vector2(2 + k, 4), Vector2(2, 2)), COLOR_GRASS_MARK)
			draw_rect(Rect2(origin + Vector2(9 - k, 11), Vector2(2, 2)), COLOR_GRASS_MARK)
			if (tx * 3 + ty * 5) % 11 == 0:
				draw_rect(Rect2(origin + Vector2(6, 7), Vector2(3, 2)), COLOR_GRASS_LIGHT)
