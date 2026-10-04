using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Menu du jeu (Échap / Tab) : met le jeu en pause et propose plusieurs
/// onglets. Navigation clavier : haut/bas pour choisir, droite ou E pour
/// entrer dans un onglet, gauche ou Échap pour revenir, Échap pour fermer.
/// Onglets : Inventaire (objets et description), Carnet (à venir), Quitter.
/// </summary>
public partial class MenuUI : CanvasLayer
{
    private static readonly Color Bg = new Color("1b1d22", 0.94f);
    private static readonly Color Border = new("6b665c");
    private static readonly Color Text = new("e3ded2");
    private static readonly Color Muted = new("8d887c");
    private static readonly Color Selected = new("f0e2b4");
    private static readonly Color SelectedBg = new Color("d2a65a", 0.22f);

    private enum Column { Tabs, Content }
    private readonly string[] _tabs = { "Inventaire", "Carnet", "Quitter" };

    public bool IsOpen { get; private set; }
    public int TabIndex { get; private set; }
    public int ItemIndex { get; private set; }
    public bool InContent => _column == Column.Content;

    private Column _column = Column.Tabs;
    private ColorRect _dim = null!;
    private PanelContainer _tabsPanel = null!;
    private VBoxContainer _tabsList = null!;
    private PanelContainer _contentPanel = null!;
    private VBoxContainer _contentList = null!;
    private Label _title = null!;
    private Label _description = null!;
    private Label _hint = null!;

    public override void _Ready()
    {
        Layer = 20;
        ProcessMode = ProcessModeEnum.Always; // actif pendant la pause
        Build();
        SetOpen(false);
        Inventory.Instance.Changed += Refresh;
    }

    public override void _ExitTree()
    {
        Inventory.Instance.Changed -= Refresh;
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (!IsOpen)
        {
            if (@event.IsActionPressed("menu") && !DialogueManager.Instance.IsActive)
            {
                Open();
                GetViewport().SetInputAsHandled();
            }
            return;
        }

        bool handled = true;
        if (@event.IsActionPressed("menu"))
        {
            if (_column == Column.Content) { _column = Column.Tabs; Refresh(); }
            else Close();
        }
        else if (@event.IsActionPressed("move_up") || @event.IsActionPressed("ui_up"))
            Move(-1);
        else if (@event.IsActionPressed("move_down") || @event.IsActionPressed("ui_down"))
            Move(1);
        else if (@event.IsActionPressed("move_right") || @event.IsActionPressed("ui_right")
                 || @event.IsActionPressed("interact") || @event.IsActionPressed("ui_accept"))
            Enter();
        else if (@event.IsActionPressed("move_left") || @event.IsActionPressed("ui_left"))
        {
            if (_column == Column.Content) { _column = Column.Tabs; Refresh(); }
        }
        else
            handled = false;
        if (handled)
            GetViewport().SetInputAsHandled();
    }

    public void Open()
    {
        TabIndex = 0;
        ItemIndex = 0;
        _column = Column.Tabs;
        SetOpen(true);
        Refresh();
    }

    public void Close() => SetOpen(false);

    private void SetOpen(bool open)
    {
        IsOpen = open;
        Visible = open;
        GetTree().Paused = open;
    }

    private void Move(int delta)
    {
        if (_column == Column.Tabs)
            TabIndex = Mathf.Wrap(TabIndex + delta, 0, _tabs.Length);
        else if (TabIndex == 0 && Inventory.Instance.Stacks.Count > 0)
            ItemIndex = Mathf.Wrap(ItemIndex + delta, 0, Inventory.Instance.Stacks.Count);
        Refresh();
    }

    private void Enter()
    {
        if (_column == Column.Content)
            return;
        switch (TabIndex)
        {
            case 0:
                if (Inventory.Instance.Stacks.Count > 0)
                {
                    _column = Column.Content;
                    ItemIndex = Mathf.Clamp(ItemIndex, 0, Inventory.Instance.Stacks.Count - 1);
                }
                break;
            case 1:
                break; // Carnet : à venir (intrigue, étape 5)
            case 2:
                GetTree().Quit();
                return;
        }
        Refresh();
    }

    // --- Construction ---------------------------------------------------------

    private static StyleBoxFlat MakeStyle(Color bg)
    {
        var style = new StyleBoxFlat { BgColor = bg, BorderColor = Border };
        style.SetBorderWidthAll(1);
        style.SetCornerRadiusAll(1);
        style.SetContentMarginAll(6);
        return style;
    }

    private static Label MakeLabel(string text, int size, Color color)
    {
        var l = new Label { Text = text };
        l.AddThemeFontSizeOverride("font_size", size);
        l.AddThemeColorOverride("font_color", color);
        return l;
    }

    private void Build()
    {
        _dim = new ColorRect { Color = new Color(0, 0, 0, 0.55f), MouseFilter = Control.MouseFilterEnum.Ignore };
        _dim.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        AddChild(_dim);

        // Colonne des onglets (gauche)
        _tabsPanel = new PanelContainer();
        _tabsPanel.AddThemeStyleboxOverride("panel", MakeStyle(Bg));
        _tabsPanel.Position = new Vector2(8, 8);
        _tabsPanel.Size = new Vector2(70, 176);
        _tabsList = new VBoxContainer();
        _tabsList.AddThemeConstantOverride("separation", 2);
        _tabsPanel.AddChild(_tabsList);
        AddChild(_tabsPanel);

        // Panneau de contenu (droite)
        _contentPanel = new PanelContainer();
        _contentPanel.AddThemeStyleboxOverride("panel", MakeStyle(Bg));
        _contentPanel.Position = new Vector2(84, 8);
        _contentPanel.Size = new Vector2(164, 176);
        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 2);
        _title = MakeLabel("", 10, Selected);
        _contentList = new VBoxContainer();
        _contentList.AddThemeConstantOverride("separation", 1);
        _contentList.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        _description = MakeLabel("", 8, Text);
        _description.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _description.CustomMinimumSize = new Vector2(0, 40);
        _hint = MakeLabel("", 7, Muted);
        vbox.AddChild(_title);
        vbox.AddChild(_contentList);
        vbox.AddChild(_description);
        vbox.AddChild(_hint);
        _contentPanel.AddChild(vbox);
        AddChild(_contentPanel);
    }

    // --- Rafraîchissement -----------------------------------------------------

    private void Refresh()
    {
        if (!IsOpen)
            return;
        foreach (var c in _tabsList.GetChildren()) c.QueueFree();
        foreach (var c in _contentList.GetChildren()) c.QueueFree();

        for (int i = 0; i < _tabs.Length; i++)
        {
            bool sel = i == TabIndex;
            var row = new PanelContainer();
            row.AddThemeStyleboxOverride("panel", RowStyle(sel && _column == Column.Tabs));
            row.AddChild(MakeLabel((sel ? "> " : "  ") + _tabs[i], 9, sel ? Selected : Text));
            _tabsList.AddChild(row);
        }

        switch (TabIndex)
        {
            case 0:
                _title.Text = "Inventaire";
                var stacks = Inventory.Instance.Stacks;
                if (stacks.Count == 0)
                    _contentList.AddChild(MakeLabel("(vide)", 9, Muted));
                for (int i = 0; i < stacks.Count; i++)
                {
                    var def = Inventory.Instance.GetDef(stacks[i].Id);
                    string name = def?.Name ?? stacks[i].Id;
                    bool sel = _column == Column.Content && i == ItemIndex;
                    var row = new PanelContainer();
                    row.AddThemeStyleboxOverride("panel", RowStyle(sel));
                    var h = new HBoxContainer();
                    var nameLabel = MakeLabel((sel ? "> " : "  ") + name, 9, sel ? Selected : Text);
                    nameLabel.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
                    h.AddChild(nameLabel);
                    h.AddChild(MakeLabel(stacks[i].Count > 1 ? $"x{stacks[i].Count}" : "", 9, Muted));
                    row.AddChild(h);
                    _contentList.AddChild(row);
                }
                if (_column == Column.Content && stacks.Count > 0)
                {
                    var def = Inventory.Instance.GetDef(stacks[ItemIndex].Id);
                    _description.Text = def?.Description ?? "";
                    _hint.Text = "Gauche / Échap : retour";
                }
                else
                {
                    _description.Text = "";
                    _hint.Text = "Droite / E : parcourir les objets";
                }
                break;
            case 1:
                _title.Text = "Carnet";
                _contentList.AddChild(MakeLabel("Rien à noter pour l'instant.", 9, Muted));
                _description.Text = "Les rumeurs du village s'inscriront ici.";
                _hint.Text = "Échap : fermer";
                break;
            case 2:
                _title.Text = "Quitter";
                _contentList.AddChild(MakeLabel("Quitter le jeu ?", 9, Text));
                _description.Text = "La progression n'est pas encore sauvegardée.";
                _hint.Text = "E : quitter    Échap : fermer";
                break;
        }
    }

    private static StyleBoxFlat RowStyle(bool selected)
    {
        var s = new StyleBoxFlat { BgColor = selected ? SelectedBg : new Color(0, 0, 0, 0) };
        s.SetCornerRadiusAll(2);
        s.SetContentMarginAll(2);
        s.ContentMarginLeft = 4;
        return s;
    }
}
