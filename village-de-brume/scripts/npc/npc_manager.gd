extends Node
## Autoload "NpcManager" : charge les fiches PNJ (data/npcs/*.json) et fait
## apparaître, dans chaque zone chargée, les PNJ qui s'y trouvent.
## Les PNJ ne sont pas placés dans les scènes de zone : leur position est une
## donnée de jeu (aujourd'hui fixe, demain calculée par les horaires).

const NPC_DIR := "res://data/npcs"
const NPC_SCENE := preload("res://scenes/npc/NPC.tscn")

## id -> fiche (Dictionary issu du JSON)
var npcs: Dictionary = {}
## id -> {"zone": String, "position": Vector2, "facing": String}
var locations: Dictionary = {}
## id -> instance NPC dans la zone courante (ou absente)
var instances: Dictionary = {}


func _ready() -> void:
	_load_all()
	Game.zone_changed.connect(_on_zone_changed)


func _load_all() -> void:
	npcs.clear()
	locations.clear()
	var dir := DirAccess.open(NPC_DIR)
	if dir == null:
		push_warning("Dossier PNJ introuvable : %s" % NPC_DIR)
		return
	var files := dir.get_files()
	files.sort()
	for f in files:
		if not f.ends_with(".json"):
			continue
		var path := NPC_DIR + "/" + f
		var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(parsed) != TYPE_DICTIONARY or not parsed.has("id"):
			push_error("Fiche PNJ invalide : %s" % path)
			continue
		var id := str(parsed["id"])
		npcs[id] = parsed
		var loc: Dictionary = parsed.get("location", {})
		var pos: Array = loc.get("position", [0, 0])
		locations[id] = {
			"zone": str(loc.get("zone", "")),
			"position": Vector2(float(pos[0]), float(pos[1])),
			"facing": str(loc.get("facing", "down")),
		}


func get_npc_name(id: String) -> String:
	return str(npcs.get(id, {}).get("name", id))


func get_zone_of(id: String) -> String:
	return str(locations.get(id, {}).get("zone", ""))


func _on_zone_changed(zone: Zone) -> void:
	instances.clear()
	for id in npcs:
		var loc: Dictionary = locations[id]
		if loc["zone"] != Game.current_zone_id:
			continue
		var npc: NPC = NPC_SCENE.instantiate()
		npc.name = "NPC_" + id
		npc.position = loc["position"]
		npc.facing = CharacterVisual.facing_from_string(loc["facing"])
		zone.add_child(npc)
		npc.apply_data(npcs[id])
		instances[id] = npc
