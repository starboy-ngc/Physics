extends Zone
## Le Village de Brume : herbe, arbres en bordure (placés automatiquement),
## sortie vers la forêt sur le bord droit (zone ajoutée à l'étape 5).

const TREE_SCENE := preload("res://scenes/world/props/Tree.tscn")

@export var border_trees: bool = true
## Rectangle (en pixels) sans arbre de bordure : ouverture vers la forêt.
@export var exit_gap: Rect2 = Rect2(700, 250, 80, 90)

const COLOR_GRASS_DARK := Color("4f8a3c")
const COLOR_GRASS_LIGHT := Color("7ab35c")


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
	super()
	# Touffes d'herbe déterministes pour casser l'uniformité.
	var rng := RandomNumberGenerator.new()
	rng.seed = 42
	for i in 180:
		var p := bounds.position + Vector2(rng.randf() * bounds.size.x, rng.randf() * bounds.size.y)
		var c := COLOR_GRASS_DARK if rng.randf() < 0.6 else COLOR_GRASS_LIGHT
		draw_rect(Rect2(p, Vector2(2, 2)), c)
		draw_rect(Rect2(p + Vector2(3, -2), Vector2(2, 2)), c)
