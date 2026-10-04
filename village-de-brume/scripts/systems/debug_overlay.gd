extends CanvasLayer
## Autoload "DebugOverlay" : panneau de debug (touche F3).
## Les lignes DAY / TIME seront alimentées à l'étape 3 (WorldTime).

var _label: Label


func _ready() -> void:
	layer = 100
	visible = false
	var panel := PanelContainer.new()
	panel.position = Vector2(8, 8)
	panel.self_modulate = Color(1, 1, 1, 0.85)
	_label = Label.new()
	_label.add_theme_font_size_override("font_size", 10)
	panel.add_child(_label)
	add_child(panel)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("debug_toggle"):
		visible = not visible


func _process(_delta: float) -> void:
	if not visible:
		return
	var lines: PackedStringArray = []
	lines.append("DAY: - (étape 3)")
	lines.append("TIME: - (étape 3)")
	lines.append("PLAYER POSITION:")
	if Game.player != null:
		lines.append("X: %d" % int(Game.player.global_position.x))
		lines.append("Y: %d" % int(Game.player.global_position.y))
		lines.append("FACING: %s" % Player.Facing.keys()[Game.player.facing])
	lines.append("CURRENT LOCATION:")
	lines.append(Game.current_zone.zone_name if Game.current_zone != null else "-")
	lines.append("FPS: %d" % Engine.get_frames_per_second())
	_label.text = "\n".join(lines)
