extends Node
## Autoload "Game" : gère les zones (village, intérieurs) et le passage du joueur
## de l'une à l'autre. C'est le seul endroit qui connaît la liste des zones.
##
## Le joueur est un noeud unique qui persiste : il est simplement déplacé
## (re-parenté) dans la zone courante, afin d'être trié en Y avec le décor.

signal zone_changed(zone: Zone)

## Identifiant de zone -> scène. Ajouter ici toute nouvelle zone (forêt, etc.).
const ZONES := {
	"village": "res://scenes/world/Village.tscn",
	"house_player": "res://scenes/world/interiors/HousePlayer.tscn",
	"bakery": "res://scenes/world/interiors/Bakery.tscn",
	"house_jeanne": "res://scenes/world/interiors/HouseJeanne.tscn",
	"house_martin": "res://scenes/world/interiors/HouseMartin.tscn",
}

const FADE_TIME := 0.15
## Délai pendant lequel les portes sont ignorées après une transition
## (évite de ressortir immédiatement par la porte que l'on vient de franchir).
const DOOR_COOLDOWN := 0.4

var player: Player
var current_zone: Zone
var current_zone_id: String = ""

var _zone_root: Node
var _transitioning := false
var _door_cooldown := 0.0
var _fade: ColorRect


func _ready() -> void:
	var layer := CanvasLayer.new()
	layer.name = "FadeLayer"
	layer.layer = 50
	_fade = ColorRect.new()
	_fade.name = "Fade"
	_fade.color = Color(0, 0, 0, 0)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(_fade)
	add_child(layer)


func _process(delta: float) -> void:
	if _door_cooldown > 0.0:
		_door_cooldown -= delta


## Appelé une fois par la scène principale.
func setup(zone_root: Node, p_player: Player) -> void:
	_zone_root = zone_root
	player = p_player


func is_ready() -> bool:
	return _zone_root != null and player != null


func can_use_door() -> bool:
	return is_ready() and not _transitioning and _door_cooldown <= 0.0 and current_zone != null


## Demande de changement de zone depuis une porte (contexte physique).
## Le changement réel est différé pour ne pas modifier l'arbre pendant la
## simulation physique.
func request_zone_change(zone_id: String, spawn_name: String) -> void:
	if not can_use_door():
		return
	_transitioning = true
	change_zone.call_deferred(zone_id, spawn_name, false)


## Change de zone avec un fondu (ou instantanément). Peut être attendu (await).
func change_zone(zone_id: String, spawn_name: String, instant: bool = false) -> void:
	if not is_ready():
		push_error("Game.change_zone appelé avant Game.setup().")
		_transitioning = false
		return
	if not ZONES.has(zone_id):
		push_error("Zone inconnue : '%s'" % zone_id)
		_transitioning = false
		return
	_transitioning = true
	if not instant:
		await _fade_to(1.0)
	_load_zone(zone_id, spawn_name)
	if not instant:
		await _fade_to(0.0)
	_door_cooldown = DOOR_COOLDOWN
	_transitioning = false


func _load_zone(zone_id: String, spawn_name: String) -> void:
	# 1. Retirer le joueur de l'ancienne zone et libérer celle-ci.
	if player.get_parent() != null:
		player.get_parent().remove_child(player)
	if current_zone != null:
		# Libération immédiate (et non queue_free) : sinon les collisions de
		# l'ancienne zone coexistent une frame avec la nouvelle et repoussent
		# le joueur. Cette fonction n'est jamais appelée pendant la physique.
		_zone_root.remove_child(current_zone)
		current_zone.free()
		current_zone = null

	# 2. Instancier la nouvelle zone.
	var scene: PackedScene = load(ZONES[zone_id])
	var zone := scene.instantiate() as Zone
	if zone == null:
		push_error("La scène '%s' n'est pas une Zone." % ZONES[zone_id])
		return
	_zone_root.add_child(zone)
	current_zone = zone
	current_zone_id = zone_id

	# 3. Placer le joueur dans la zone, au point d'apparition demandé.
	zone.add_child(player)
	player.global_position = zone.get_spawn_position(spawn_name)
	player.velocity = Vector2.ZERO
	player.face(Player.Facing.DOWN if spawn_name != "entrance" else Player.Facing.UP)

	# 4. Caméra : limites de la zone, sans glissement depuis l'ancienne position.
	_apply_camera_limits(zone)
	player.camera.make_current()
	player.camera.reset_smoothing()

	zone_changed.emit(zone)


## Les limites de la caméra épousent la zone. Si la zone est plus petite que
## l'écran (intérieurs), les limites sont centrées sur la zone pour qu'elle
## apparaisse au milieu de l'écran.
func _apply_camera_limits(zone: Zone) -> void:
	var cam := player.camera
	var view: Vector2 = player.get_viewport_rect().size / cam.zoom
	var b := zone.bounds
	var left := b.position.x
	var right := b.end.x
	var top := b.position.y
	var bottom := b.end.y
	if b.size.x < view.x:
		var cx := b.get_center().x
		left = cx - view.x / 2.0
		right = cx + view.x / 2.0
	if b.size.y < view.y:
		var cy := b.get_center().y
		top = cy - view.y / 2.0
		bottom = cy + view.y / 2.0
	cam.limit_left = int(floor(left))
	cam.limit_right = int(ceil(right))
	cam.limit_top = int(floor(top))
	cam.limit_bottom = int(ceil(bottom))


func _fade_to(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade, "color:a", alpha, FADE_TIME)
	await tween.finished
