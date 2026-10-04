class_name Zone
extends Node2D
## Base de toute zone jouable (village, intérieur de maison...).
## Une zone connaît :
##  - son nom (affiché dans le debug) ;
##  - ses limites `bounds` (caméra + murs invisibles) ;
##  - ses points d'apparition : des Marker2D enfants d'un noeud "Spawns".
## Les enfants sont triés en Y (vue 3/4) : l'origine de chaque élément doit
## être à sa base (pieds, bas des murs, pied du tronc...).

@export var zone_name: String = "Zone"
@export var bounds: Rect2 = Rect2(0, 0, 768, 576)
@export var ground_color: Color = Color("5f9e4a")
## Zone infranchissable en haut (mur du fond des intérieurs).
@export var wall_top: float = 0.0
## Zone infranchissable sur les côtés et en bas.
@export var wall_sides: float = 0.0

const WALL_THICKNESS := 32.0


func _ready() -> void:
	y_sort_enabled = true
	_build_boundaries()


func get_spawn_position(spawn_name: String) -> Vector2:
	var marker := get_node_or_null("Spawns/" + spawn_name) as Node2D
	if marker == null:
		push_warning("Zone '%s' : point d'apparition '%s' introuvable, centre utilisé." % [zone_name, spawn_name])
		return bounds.get_center()
	return marker.global_position


## Murs invisibles tout autour de la zone jouable.
func _build_boundaries() -> void:
	var body := StaticBody2D.new()
	body.name = "Boundaries"
	body.collision_layer = 1
	body.collision_mask = 0
	var inner := Rect2(
		bounds.position + Vector2(wall_sides, wall_top),
		bounds.size - Vector2(wall_sides * 2.0, wall_top + wall_sides)
	)
	var t := WALL_THICKNESS
	_add_wall(body, Rect2(inner.position.x - t, inner.position.y - t, inner.size.x + 2.0 * t, t))
	_add_wall(body, Rect2(inner.position.x - t, inner.end.y, inner.size.x + 2.0 * t, t))
	_add_wall(body, Rect2(inner.position.x - t, inner.position.y, t, inner.size.y))
	_add_wall(body, Rect2(inner.end.x, inner.position.y, t, inner.size.y))
	add_child(body)


func _add_wall(body: StaticBody2D, rect: Rect2) -> void:
	var shape := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = rect.size
	shape.shape = rs
	shape.position = rect.get_center()
	body.add_child(shape)


func _draw() -> void:
	draw_rect(bounds, ground_color)
