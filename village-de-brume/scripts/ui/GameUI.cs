using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Interface en jeu (256x192) : boîte de dialogue bleu nuit en bas avec
/// portrait du locuteur, boîte de choix à droite avec curseur, invite
/// d'interaction discrète et message temporaire en haut.
/// </summary>
public partial class GameUI : CanvasLayer
{
    public static GameUI? Instance { get; private set; }

    public static readonly Color BoxBg = new("1c2d70");
    public static readonly Color BoxBgDark = new("142252");
    public static readonly Color BoxBorder = new("f0f0ff");
    public static readonly Color Text = new("ffffff");
    public static readonly Color NameColor = new("f8e070");
    public static readonly Color Cursor = new("ffffff");
    public static readonly Color PortraitBg = new("3a5a9a");

    private const int BoxHeight = 44;
    private const int Margin = 4;

    private PanelContainer _promptPanel = null!;
    private Label _prompt = null!;
    private PanelContainer _noticePanel = null!;
    private Label _notice = null!;
    private float _noticeTimer;
    private PanelContainer _box = null!;
    private RichTextLabel _textLabel = null!;
    private PanelContainer _portraitFrame = null!;
    private TextureRect _portrait = null!;
    private PanelContainer _choicesBox = null!;
    private VBoxContainer _choicesList = null!;
    private int _choiceIndex;
    private IReadOnlyList<string> _choices = new List<string>();
    private string _speaker = "";
    private Player? _player;
    private readonly Dictionary<string, ImageTexture> _portraits = new();

    public int ChoiceIndex => _choiceIndex;
    public IReadOnlyList<string> Choices => _choices;

    public override void _Ready()
    {
        Instance = this;
        Layer = 10;
        BuildPrompt();
        BuildNotice();
        BuildDialogueBox();
        var dm = DialogueManager.Instance;
        dm.DialogueStarted += OnDialogueStarted;
        dm.NodeChanged += OnNodeChanged;
        dm.DialogueEnded += OnDialogueEnded;
        _box.Visible = false;
        _portraitFrame.Visible = false;
        _choicesBox.Visible = false;
        _promptPanel.Visible = false;
    }

    public override void _ExitTree()
    {
        Instance = null;
        var dm = DialogueManager.Instance;
        dm.DialogueStarted -= OnDialogueStarted;
        dm.NodeChanged -= OnNodeChanged;
        dm.DialogueEnded -= OnDialogueEnded;
    }

    public void BindPlayer(Player player)
    {
        _player = player;
        player.FocusChanged += OnFocusChanged;
    }

    public void ShowNotice(string text, float seconds = 2f)
    {
        _notice.Text = text;
        _noticePanel.Visible = true;
        _noticeTimer = seconds;
        _noticePanel.ResetSize();
        _noticePanel.Position = new Vector2(128 - _noticePanel.Size.X / 2f, 6);
    }

    public override void _Process(double delta)
    {
        if (_noticeTimer > 0f)
        {
            _noticeTimer -= (float)delta;
            if (_noticeTimer <= 0f) _noticePanel.Visible = false;
        }
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        var dm = DialogueManager.Instance;
        if (!dm.IsActive || GetTree().Paused)
            return;
        if (Engine.GetProcessFrames() == dm.StartedFrame)
            return;
        if (@event.IsActionPressed("interact") || @event.IsActionPressed("ui_accept"))
        {
            if (_choices.Count == 0) dm.Advance();
            else dm.Choose(_choiceIndex);
            GetViewport().SetInputAsHandled();
        }
        else if (_choices.Count > 0)
        {
            if (@event.IsActionPressed("move_up") || @event.IsActionPressed("ui_up"))
            { _choiceIndex = Mathf.Wrap(_choiceIndex - 1, 0, _choices.Count); RefreshChoices(); GetViewport().SetInputAsHandled(); }
            else if (@event.IsActionPressed("move_down") || @event.IsActionPressed("ui_down"))
            { _choiceIndex = Mathf.Wrap(_choiceIndex + 1, 0, _choices.Count); RefreshChoices(); GetViewport().SetInputAsHandled(); }
        }
    }

    // --- Construction -------------------------------------------------------

    /// <summary>Boîte bleu nuit à double bordure (claire puis sombre), façon RPG portable.</summary>
    public static StyleBoxFlat MakeBoxStyle(int margin = 4)
    {
        var style = new StyleBoxFlat { BgColor = BoxBg, BorderColor = BoxBorder };
        style.SetBorderWidthAll(1);
        style.SetCornerRadiusAll(2);
        style.SetContentMarginAll(margin);
        style.ShadowColor = BoxBgDark;
        style.ShadowSize = 1;
        return style;
    }

    public static Label MakeLabel(string text, int size, Color color)
    {
        var l = new Label { Text = text };
        l.AddThemeFontSizeOverride("font_size", size);
        l.AddThemeColorOverride("font_color", color);
        return l;
    }

    private void BuildPrompt()
    {
        _promptPanel = new PanelContainer { Name = "PromptPanel" };
        _promptPanel.AddThemeStyleboxOverride("panel", MakeBoxStyle(3));
        _prompt = MakeLabel("", 8, Text);
        _promptPanel.AddChild(_prompt);
        AddChild(_promptPanel);
    }

    private void BuildNotice()
    {
        _noticePanel = new PanelContainer { Name = "NoticePanel", Visible = false };
        _noticePanel.AddThemeStyleboxOverride("panel", MakeBoxStyle(3));
        _notice = MakeLabel("", 8, Text);
        _noticePanel.AddChild(_notice);
        AddChild(_noticePanel);
    }

    private void BuildDialogueBox()
    {
        _box = new PanelContainer { Name = "DialogueBox" };
        _box.AddThemeStyleboxOverride("panel", MakeBoxStyle(5));
        _box.SetAnchorsPreset(Control.LayoutPreset.BottomWide);
        _box.OffsetLeft = Margin;
        _box.OffsetRight = -Margin;
        _box.OffsetTop = -BoxHeight - Margin;
        _box.OffsetBottom = -Margin;
        _textLabel = new RichTextLabel { BbcodeEnabled = true, ScrollActive = false, FitContent = false };
        _textLabel.AddThemeFontSizeOverride("normal_font_size", 8);
        _textLabel.AddThemeColorOverride("default_color", Text);
        _textLabel.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        _box.AddChild(_textLabel);
        AddChild(_box);

        // Portrait au-dessus de la boîte, à gauche
        _portraitFrame = new PanelContainer { Name = "Portrait" };
        _portraitFrame.AddThemeStyleboxOverride("panel", MakeBoxStyle(2));
        _portraitFrame.Position = new Vector2(Margin + 2, 192 - BoxHeight - Margin - 40);
        _portrait = new TextureRect { CustomMinimumSize = new Vector2(32, 32), TextureFilter = CanvasItem.TextureFilterEnum.Nearest };
        _portraitFrame.AddChild(_portrait);
        AddChild(_portraitFrame);

        // Choix : à droite, au-dessus de la boîte
        _choicesBox = new PanelContainer { Name = "ChoicesBox" };
        _choicesBox.AddThemeStyleboxOverride("panel", MakeBoxStyle(4));
        _choicesList = new VBoxContainer();
        _choicesList.AddThemeConstantOverride("separation", 0);
        _choicesBox.AddChild(_choicesList);
        AddChild(_choicesBox);
    }

    // --- Réactions ----------------------------------------------------------

    private void OnFocusChanged(IGridInteractable? interactable)
    {
        if (interactable == null || interactable.Prompt == "" || DialogueManager.Instance.IsActive)
        {
            _promptPanel.Visible = false;
            return;
        }
        _prompt.Text = "E  " + interactable.Prompt;
        _promptPanel.Visible = true;
        _promptPanel.ResetSize();
        _promptPanel.Position = new Vector2(128 - _promptPanel.Size.X / 2f, 192 - 20);
    }

    private void OnDialogueStarted(string speaker)
    {
        _promptPanel.Visible = false;
        _box.Visible = true;
        _speaker = speaker;
        var tex = GetPortrait(DialogueManager.Instance.SpeakerId);
        _portrait.Texture = tex;
        _portraitFrame.Visible = tex != null;
    }

    private ImageTexture? GetPortrait(string npcId)
    {
        if (string.IsNullOrEmpty(npcId) || !NpcManager.Instance.Npcs.TryGetValue(npcId, out var data))
            return null;
        if (_portraits.TryGetValue(npcId, out var cached))
            return cached;
        Color Get(string key, string fallback) => data.Appearance.TryGetValue(key, out var v) ? new Color(v) : new Color(fallback);
        var tex = CharacterSprites.BuildPortrait(Get("tunic", "3a6ea5"), Get("hair", "5a3a22"), Get("skin", "f1c9a5"), PortraitBg);
        _portraits[npcId] = tex;
        return tex;
    }

    private void OnNodeChanged(string speaker, string text, IReadOnlyList<string> choices)
    {
        string safe = text.Replace("[", "[lb]");
        _textLabel.Text = speaker != "" ? $"[color=#{NameColor.ToHtml(false)}]{speaker}:[/color] {safe}" : safe;
        _choices = choices;
        _choiceIndex = 0;
        RefreshChoices();
    }

    private void OnDialogueEnded(string id)
    {
        _box.Visible = false;
        _portraitFrame.Visible = false;
        _choicesBox.Visible = false;
        if (_player != null) OnFocusChanged(_player.Focused);
    }

    private void RefreshChoices()
    {
        // Retirer immédiatement les anciens libellés : QueueFree seul les laisse
        // compter dans la taille minimale jusqu'à la frame suivante.
        foreach (var c in _choicesList.GetChildren()) { _choicesList.RemoveChild(c); c.QueueFree(); }
        _choicesBox.Visible = _choices.Count > 0;
        for (int i = 0; i < _choices.Count; i++)
            _choicesList.AddChild(MakeLabel((i == _choiceIndex ? "▶ " : "   ") + _choices[i], 8, Text));
        _choicesBox.Size = _choicesBox.GetCombinedMinimumSize();
        _choicesBox.Position = new Vector2(256 - Margin - _choicesBox.Size.X, 192 - BoxHeight - Margin - 2 - _choicesBox.Size.Y);
    }
}
