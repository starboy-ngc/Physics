class_name Interactable
extends Area2D
## Tout ce avec quoi le joueur peut interagir en appuyant sur E.
## Le joueur détecte les Interactable devant lui (couche 3) et affiche
## « E — <prompt> ». Les sous-classes redéfinissent `interact()`.

@export var prompt: String = "Examiner"
@export var size: Vector2 = Vector2(16, 20)
@export var offset: Vector2 = Vector2(0, -8)


func _ready() -> void:
	collision_layer = 4
	collision_mask = 0
	monitoring = false
	monitorable = true
	var shape := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	shape.shape = rs
	shape.position = offset
	add_child(shape)


## Appelé par le joueur. À redéfinir.
func interact(_player: Node2D) -> void:
	pass
