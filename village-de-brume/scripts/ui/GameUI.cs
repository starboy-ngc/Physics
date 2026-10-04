using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Interface en jeu, construite en code (résolution 256x192) :
/// invite « E — Parler » quand le joueur est face à un Interactable ;
/// boîte de dialogue en bas de l'écran, choix navigables au clavier.
/// </summary>
public partial class GameUI : CanvasLayer
{
    public static GameUI? Instance { get; private set; }

    private const int BoxHeight = 60;
    private const int Margin = 4;
    private static readonly Color Bg = new Color("1b1d22", 0.93f);
    private static readonly Color Border = new("6b665c");
    private static readonly Color Text = new("e3ded2");
    private static readonly Color NameColor = new("d2a65a");
    private static readonly Color Selected = new("f0e2b4");

    private PanelContainer _promptPanel = null!;
    private Label _prompt = null!;
    private PanelContainer _box = null!;
    private Label _nameLabel = null!;
    private Label _textLabel = null!;
    private PanelContainer _choicesBox = null!;
    private VBoxContainer _choicesList = null!;
    private int _choiceIndex;
    private IReadOnlyList<string> _choices = new List<string>();
    private Player? _player;
    private PanelContainer _noticePanel = null!;
    private Label _notice = null!;
    private float _noticeTimer;

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
        _choicesBox.Visible = false;
        _promptPanel.Visible = false;
    }

    /// <summary>Message court en haut de l'écran (pêche, objets ramassés...).</summary>
    public void ShowNotice(string text, float seconds = 2f)
    {
        _notice.Text = text;
        _noticePanel.Visible = true;
        _noticeTimer = seconds;
        _noticePanel.ResetSize();
        _noticePanel.Position = new Vector2(128 - _noticePanel.Size.X / 2f, 8);
    }

    public override void _Process(double delta)
    {
        if (_noticeTimer > 0f)
        {
            _noticeTimer -= (float)delta;
            if (_noticeTimer <= 0f)
                _noticePanel.Visible = false;
        }
    }

    private void BuildNotice()
    {
        _noticePanel = new PanelContainer { Name = "NoticePanel", Visible = false };
        _noticePanel.AddThemeStyleboxOverride("panel", MakeStyle());
        _notice = MakeLabel(Selected);
        _noticePanel.AddChild(_notice);
        AddChild(_noticePanel);
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

    public override void _UnhandledInput(InputEvent @event)
    {
        var dm = DialogueManager.Instance;
        if (!dm.IsActive || GetTree().Paused)
            return;
        // La touche qui a lancé le dialogue ne doit pas aussi le faire avancer.
        if (Engine.GetProcessFrames() == dm.StartedFrame)
            return;
        if (@event.IsActionPressed("interact") || @event.IsActionPressed("ui_accept"))
        {
            if (_choices.Count == 0)
                dm.Advance();
            else
                dm.Choose(_choiceIndex);
            GetViewport().SetInputAsHandled();
        }
        else if (_choices.Count > 0)
        {
            if (@event.IsActionPressed("move_up") || @event.IsActionPressed("ui_up"))
            {
                _choiceIndex = Mathf.Wrap(_choiceIndex - 1, 0, _choices.Count);
                RefreshChoices();
                GetViewport().SetInputAsHandled();
            }
            else if (@event.IsActionPressed("move_down") || @event.IsActionPressed("ui_down"))
            {
                _choiceIndex = Mathf.Wrap(_choiceIndex + 1, 0, _choices.Count);
                RefreshChoices();
                GetViewport().SetInputAsHandled();
            }
        }
    }

    // --- Construction -------------------------------------------------------

    private static StyleBoxFlat MakeStyle()
    {
        var style = new StyleBoxFlat { BgColor = Bg, BorderColor = Border };
        style.SetBorderWidthAll(1);
        style.SetCornerRadiusAll(1);
        style.SetContentMarginAll(5);
        return style;
    }

    private static Label MakeLabel(Color color)
    {
        var l = new Label();
        l.AddThemeFontSizeOverride("font_size", 9);
        l.AddThemeColorOverride("font_color", color);
        return l;
    }

    private void BuildPrompt()
    {
        _promptPanel = new PanelContainer { Name = "PromptPanel" };
        _promptPanel.AddThemeStyleboxOverride("panel", MakeStyle());
        _promptPanel.SetAnchorsPreset(Control.LayoutPreset.CenterBottom);
        _promptPanel.Position = new Vector2(0, 192 - 22);
        _promptPanel.GrowHorizontal = Control.GrowDirection.Both;
        _prompt = MakeLabel(Text);
        _promptPanel.AddChild(_prompt);
        AddChild(_promptPanel);
    }

    private void BuildDialogueBox()
    {
        _box = new PanelContainer { Name = "DialogueBox" };
        _box.AddThemeStyleboxOverride("panel", MakeStyle());
        _box.SetAnchorsPreset(Control.LayoutPreset.BottomWide);
        _box.OffsetLeft = Margin;
        _box.OffsetRight = -Margin;
        _box.OffsetTop = -BoxHeight - Margin;
        _box.OffsetBottom = -Margin;
        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 1);
        _nameLabel = MakeLabel(NameColor);
        _textLabel = MakeLabel(Text);
        _textLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _textLabel.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        vbox.AddChild(_nameLabel);
        vbox.AddChild(_textLabel);
        _box.AddChild(vbox);
        AddChild(_box);

        // Boîte des choix, au-dessus de la boîte de dialogue, à droite.
        _choicesBox = new PanelContainer { Name = "ChoicesBox" };
        _choicesBox.AddThemeStyleboxOverride("panel", MakeStyle());
        _choicesList = new VBoxContainer();
        _choicesList.AddThemeConstantOverride("separation", 0);
        _choicesBox.AddChild(_choicesList);
        AddChild(_choicesBox);
    }

    // --- Réactions ----------------------------------------------------------

    private void OnFocusChanged(Interactable? interactable)
    {
        if (interactable == null || interactable.Prompt == "" || DialogueManager.Instance.IsActive)
        {
            _promptPanel.Visible = false;
        }
        else
        {
            _prompt.Text = "E — " + interactable.Prompt;
            _promptPanel.Visible = true;
        }
    }

    private void OnDialogueStarted(string speaker)
    {
        _promptPanel.Visible = false;
        _box.Visible = true;
    }

    private void OnNodeChanged(string speaker, string text, IReadOnlyList<string> choices)
    {
        _nameLabel.Text = speaker;
        _nameLabel.Visible = speaker != "";
        _textLabel.Text = text;
        _choices = choices;
        _choiceIndex = 0;
        RefreshChoices();
    }

    private void OnDialogueEnded(string id)
    {
        _box.Visible = false;
        _choicesBox.Visible = false;
        if (_player != null)
            OnFocusChanged(_player.Focused);
    }

    private void RefreshChoices()
    {
        foreach (var c in _choicesList.GetChildren())
            c.QueueFree();
        _choicesBox.Visible = _choices.Count > 0;
        for (int i = 0; i < _choices.Count; i++)
        {
            var l = MakeLabel(i == _choiceIndex ? Selected : Text);
            l.Text = (i == _choiceIndex ? "> " : "  ") + _choices[i];
            _choicesList.AddChild(l);
        }
        // Repositionner en bas à droite, au-dessus de la boîte de dialogue.
        _choicesBox.ResetSize();
        _choicesBox.Position = new Vector2(
            256 - Margin - _choicesBox.Size.X,
            192 - BoxHeight - Margin - 2 - _choicesBox.Size.Y);
    }
}
