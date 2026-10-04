extends CanvasLayer
## Interface en jeu, construite en code (résolution 256x192) :
##  - invite « E — Parler » quand le joueur est face à un Interactable ;
##  - boîte de dialogue en bas de l'écran, choix navigables au clavier.

const BOX_HEIGHT := 60
const MARGIN := 4
const COLOR_BG := Color("f8f4ea")
const COLOR_BORDER := Color("3a3a5a")
const COLOR_TEXT := Color("2a2a3a")
const COLOR_NAME := Color("8c3a2c")
const COLOR_SELECTED := Color("2a5aa0")

var _prompt: Label
var _box: PanelContainer
var _name_label: Label
var _text_label: Label
var _choices_box: PanelContainer
var _choices_list: VBoxContainer
var _choice_index := 0
var _choices: PackedStringArray = []
var _player: Player


func _ready() -> void:
	layer = 10
	_build_prompt()
	_build_dialogue_box()
	DialogueManager.dialogue_started.connect(_on_dialogue_started)
	DialogueManager.node_changed.connect(_on_node_changed)
	DialogueManager.dialogue_ended.connect(_on_dialogue_ended)
	_box.visible = false
	_choices_box.visible = false
	_prompt.visible = false


func bind_player(player: Player) -> void:
	_player = player
	player.focus_changed.connect(_on_focus_changed)


func _unhandled_input(event: InputEvent) -> void:
	if not DialogueManager.is_active:
		return
	# La touche qui a lancé le dialogue ne doit pas aussi le faire avancer.
	if Engine.get_process_frames() == DialogueManager.started_frame:
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		if _choices.is_empty():
			DialogueManager.advance()
		else:
			DialogueManager.choose(_choice_index)
		get_viewport().set_input_as_handled()
	elif not _choices.is_empty():
		if event.is_action_pressed("move_up") or event.is_action_pressed("ui_up"):
			_choice_index = wrapi(_choice_index - 1, 0, _choices.size())
			_refresh_choices()
			get_viewport().set_input_as_handled()
		elif event.is_action_pressed("move_down") or event.is_action_pressed("ui_down"):
			_choice_index = wrapi(_choice_index + 1, 0, _choices.size())
			_refresh_choices()
			get_viewport().set_input_as_handled()


# --- Construction -----------------------------------------------------------

func _make_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = COLOR_BG
	style.border_color = COLOR_BORDER
	style.set_border_width_all(2)
	style.set_corner_radius_all(2)
	style.set_content_margin_all(5)
	return style


func _build_prompt() -> void:
	var panel := PanelContainer.new()
	panel.name = "PromptPanel"
	panel.add_theme_stylebox_override("panel", _make_style())
	panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	panel.position = Vector2(0, 192 - 22)
	panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_prompt = Label.new()
	_prompt.add_theme_font_size_override("font_size", 9)
	_prompt.add_theme_color_override("font_color", COLOR_TEXT)
	panel.add_child(_prompt)
	add_child(panel)
	_prompt = panel.get_child(0)
	# Le panneau se cache avec son label
	_prompt.visibility_changed.connect(func(): panel.visible = _prompt.visible)


func _build_dialogue_box() -> void:
	_box = PanelContainer.new()
	_box.name = "DialogueBox"
	_box.add_theme_stylebox_override("panel", _make_style())
	_box.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_box.offset_left = MARGIN
	_box.offset_right = -MARGIN
	_box.offset_top = -BOX_HEIGHT - MARGIN
	_box.offset_bottom = -MARGIN
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 1)
	_name_label = Label.new()
	_name_label.add_theme_font_size_override("font_size", 9)
	_name_label.add_theme_color_override("font_color", COLOR_NAME)
	_text_label = Label.new()
	_text_label.add_theme_font_size_override("font_size", 9)
	_text_label.add_theme_color_override("font_color", COLOR_TEXT)
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(_name_label)
	vbox.add_child(_text_label)
	_box.add_child(vbox)
	add_child(_box)

	# Boîte des choix, au-dessus de la boîte de dialogue, à droite.
	_choices_box = PanelContainer.new()
	_choices_box.name = "ChoicesBox"
	_choices_box.add_theme_stylebox_override("panel", _make_style())
	_choices_box.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_choices_box.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_choices_box.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_choices_box.position = Vector2(256 - MARGIN, 192 - BOX_HEIGHT - MARGIN - 2)
	_choices_list = VBoxContainer.new()
	_choices_list.add_theme_constant_override("separation", 0)
	_choices_box.add_child(_choices_list)
	add_child(_choices_box)


# --- Réactions --------------------------------------------------------------

func _on_focus_changed(interactable: Interactable) -> void:
	if interactable == null or DialogueManager.is_active:
		_prompt.visible = false
	else:
		_prompt.text = "E — " + interactable.prompt
		_prompt.visible = true


func _on_dialogue_started(_speaker: String) -> void:
	_prompt.visible = false
	_box.visible = true


func _on_node_changed(speaker: String, text: String, choices: PackedStringArray) -> void:
	_name_label.text = speaker
	_name_label.visible = speaker != ""
	_text_label.text = text
	_choices = choices
	_choice_index = 0
	_refresh_choices()


func _on_dialogue_ended(_id: String) -> void:
	_box.visible = false
	_choices_box.visible = false
	if _player != null:
		_on_focus_changed(_player.focused)


func _refresh_choices() -> void:
	for c in _choices_list.get_children():
		c.queue_free()
	_choices_box.visible = not _choices.is_empty()
	for i in _choices.size():
		var l := Label.new()
		l.add_theme_font_size_override("font_size", 9)
		l.text = ("> " if i == _choice_index else "  ") + _choices[i]
		l.add_theme_color_override("font_color", COLOR_SELECTED if i == _choice_index else COLOR_TEXT)
		_choices_list.add_child(l)
	# Repositionner après resize (ancrage bas-droite, croissance vers le haut/gauche)
	_choices_box.reset_size()
	_choices_box.position = Vector2(256 - MARGIN - _choices_box.size.x, 192 - BOX_HEIGHT - MARGIN - 2 - _choices_box.size.y)
