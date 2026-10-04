extends Node
## Autoload "DialogueManager" : déroule un DialogueData noeud par noeud.
## Indépendant des PNJ et de l'interface : l'UI écoute les signaux,
## le joueur consulte `is_active` pour se bloquer.

signal dialogue_started(speaker: String)
signal node_changed(speaker: String, text: String, choices: PackedStringArray)
signal dialogue_ended(dialogue_id: String)

var is_active := false
## Frame à laquelle le dialogue a démarré (l'UI ignore la touche de cette frame).
var started_frame := -1

var _data: DialogueData
var _speaker: String = ""
var _node_id: String = ""
var _node: Dictionary = {}


func start(data: DialogueData, speaker: String) -> bool:
	if is_active or data == null:
		return false
	_data = data
	_speaker = speaker
	is_active = true
	started_frame = Engine.get_process_frames()
	dialogue_started.emit(speaker)
	_goto(data.start_node)
	return true


func current_choices() -> PackedStringArray:
	var out: PackedStringArray = []
	for c in _node.get("choices", []):
		out.append(str(c.get("text", "...")))
	return out


## Avance au noeud suivant (si le noeud courant n'a pas de choix).
func advance() -> void:
	if not is_active or not current_choices().is_empty():
		return
	var next := str(_node.get("next", ""))
	if next == "" or next == "end":
		end()
	else:
		_goto(next)


## Valide le choix d'index `index`.
func choose(index: int) -> void:
	if not is_active:
		return
	var choices: Array = _node.get("choices", [])
	if index < 0 or index >= choices.size():
		return
	var next := str(choices[index].get("next", ""))
	if next == "" or next == "end":
		end()
	else:
		_goto(next)


func end() -> void:
	if not is_active:
		return
	var ended_id := _data.id
	is_active = false
	_data = null
	_node = {}
	_node_id = ""
	dialogue_ended.emit(ended_id)


func _goto(node_id: String) -> void:
	if not _data.has_node(node_id):
		push_error("Dialogue '%s' : noeud '%s' introuvable, fin forcée." % [_data.id, node_id])
		end()
		return
	_node_id = node_id
	_node = _data.get_node_data(node_id)
	node_changed.emit(_speaker, str(_node.get("text", "")), current_choices())
