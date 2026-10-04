class_name DialogueData
extends RefCounted
## Un dialogue statique chargé depuis un fichier JSON.
##
## Format :
## {
##   "id": "emile_intro",
##   "start": "start",
##   "nodes": {
##     "start": {"text": "Bonjour.", "choices": [{"text": "Salut", "next": "a"}]},
##     "a":     {"text": "...", "next": "b"},
##     "b":     {"text": "Au revoir."}        <- pas de "next" : fin du dialogue
##   }
## }

var id: String = ""
var start_node: String = "start"
var nodes: Dictionary = {}


static func load_from_file(path: String) -> DialogueData:
	if not FileAccess.file_exists(path):
		push_error("Dialogue introuvable : %s" % path)
		return null
	var text := FileAccess.get_file_as_string(path)
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Dialogue invalide (JSON) : %s" % path)
		return null
	var data := DialogueData.new()
	data.id = str(parsed.get("id", path.get_file().get_basename()))
	data.start_node = str(parsed.get("start", "start"))
	data.nodes = parsed.get("nodes", {})
	if not data.nodes.has(data.start_node):
		push_error("Dialogue '%s' : noeud de départ '%s' absent." % [data.id, data.start_node])
		return null
	return data


func has_node(node_id: String) -> bool:
	return nodes.has(node_id)


func get_node_data(node_id: String) -> Dictionary:
	return nodes.get(node_id, {})
