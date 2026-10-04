class_name Door
extends Area2D
## Zone de passage : quand le joueur marche dessus, il change de zone.
## Utilisée par les bâtiments (entrée) et par les intérieurs (sortie).

@export var target_zone: String = ""
@export var target_spawn: String = "entrance"
@export var size: Vector2 = Vector2(20, 16)
## Dessine un paillasson / une ouverture (utile pour les sorties d'intérieur).
@export var draw_mat: bool = false


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2  # couche "player"
	var shape := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	shape.shape = rs
	add_child(shape)


## Vérification à chaque tick physique (et non seulement sur body_entered) :
## si le joueur arrive sur la porte pendant le délai anti-rebond et reste
## dessus, la porte doit quand même se déclencher à la fin du délai.
func _physics_process(_delta: float) -> void:
	if target_zone == "" or not has_overlapping_bodies():
		return
	if not Game.can_use_door():
		return
	for body in get_overlapping_bodies():
		if body is Player:
			Game.request_zone_change(target_zone, target_spawn)
			return


func _draw() -> void:
	if not draw_mat:
		return
	var rect := Rect2(-size / 2.0, size)
	draw_rect(rect, Color("3b2a1a"))
	draw_rect(rect.grow(-3), Color("6b4a2a"))
