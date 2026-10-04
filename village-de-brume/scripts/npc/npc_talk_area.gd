extends Interactable
## Zone d'interaction d'un PNJ. `interact` est un Callable fourni par le PNJ.

var interact_callback: Callable


func interact(player: Node2D) -> void:
	if interact_callback.is_valid():
		interact_callback.call(player)
