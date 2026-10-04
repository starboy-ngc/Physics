using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Panneau générique : un titre, des onglets (gauche/droite), une liste
/// d'entrées (haut/bas), une description et une ligne d'aide. E valide
/// l'entrée, Échap ferme. Le joueur est immobilisé pendant l'ouverture.
/// Les sous-classes fournissent les onglets, les entrées et l'action de validation.
/// </summary>
public abstract partial class ListPanelUI : CanvasLayer
{
    protected static readonly Color Bg = new Color("1b1d22", 0.94f);
    protected static readonly Color Border = new("6b665c");
    protected static readonly Color Text = new("e3ded2");
    protected static readonly Color Muted = new("8d887c");
    protected static readonly Color Accent = new("d2a65a");
    protected static readonly Color Selected = new("f0e2b4");
    protected static readonly Color SelectedBg = new Color("d2a65a", 0.22f);

    public record Entry(string Label, string Right, bool Enabled, string Description);

    public bool IsOpen { get; private set; }
    public int TabIndex { get; protected set; }
    public int Index { get; protected set; }

    protected abstract string Title { get; }
    protected abstract string[] Tabs { get; }
    protected abstract List<Entry> GetEntries();
    protected abstract void Confirm(int index);
    protected virtual string Header => "";
    protected virtual string Hint => "Haut/Bas choisir · Gauche/Droite onglet · E valider · Échap fermer";

    private PanelContainer _panel = null!;
    private Label _title = null!;
    private Label _header = null!;
    private HBoxContainer _tabsRow = null!;
    private VBoxContainer _list = null!;
    private Label _description = null!;
    private Label _hint = null!;
    private Label _feedback = null!;
    private float _feedbackTimer;

    public override void _Ready()
    {
        Layer = 15;
        Build();
        Visible = false;
    }

    public void Open()
    {
        IsOpen = true;
        Visible = true;
        TabIndex = 0;
        Index = 0;
        Game.Instance.Player.Locked = true;
        OnOpened();
        Refresh();
    }

    public void Close()
    {
        IsOpen = false;
        Visible = false;
        Game.Instance.Player.Locked = false;
        OnClosed();
    }

    protected virtual void OnOpened() { }
    protected virtual void OnClosed() { }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (!IsOpen)
            return;
        bool handled = true;
        var entries = GetEntries();
        if (@event.IsActionPressed("menu"))
            Close();
        else if (@event.IsActionPressed("move_up") || @event.IsActionPressed("ui_up"))
            Index = entries.Count == 0 ? 0 : Mathf.Wrap(Index - 1, 0, entries.Count);
        else if (@event.IsActionPressed("move_down") || @event.IsActionPressed("ui_down"))
            Index = entries.Count == 0 ? 0 : Mathf.Wrap(Index + 1, 0, entries.Count);
        else if (@event.IsActionPressed("move_left") || @event.IsActionPressed("ui_left"))
        { TabIndex = Mathf.Wrap(TabIndex - 1, 0, Tabs.Length); Index = 0; }
        else if (@event.IsActionPressed("move_right") || @event.IsActionPressed("ui_right"))
        { TabIndex = Mathf.Wrap(TabIndex + 1, 0, Tabs.Length); Index = 0; }
        else if (@event.IsActionPressed("interact") || @event.IsActionPressed("ui_accept"))
        {
            if (Index < entries.Count && entries[Index].Enabled)
                Confirm(Index);
        }
        else
            handled = false;
        if (handled)
        {
            GetViewport().SetInputAsHandled();
            if (IsOpen) Refresh();
        }
    }

    public override void _Process(double delta)
    {
        if (_feedbackTimer > 0f)
        {
            _feedbackTimer -= (float)delta;
            if (_feedbackTimer <= 0f) _feedback.Text = "";
        }
    }

    protected void Feedback(string text)
    {
        _feedback.Text = text;
        _feedbackTimer = 2f;
    }

    // --- Construction ---------------------------------------------------------

    protected static Label MakeLabel(string text, int size, Color color)
    {
        var l = new Label { Text = text };
        l.AddThemeFontSizeOverride("font_size", size);
        l.AddThemeColorOverride("font_color", color);
        return l;
    }

    private void Build()
    {
        var dim = new ColorRect { Color = new Color(0, 0, 0, 0.4f), MouseFilter = Control.MouseFilterEnum.Ignore };
        dim.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        AddChild(dim);

        _panel = new PanelContainer();
        var style = new StyleBoxFlat { BgColor = Bg, BorderColor = Border };
        style.SetBorderWidthAll(1);
        style.SetCornerRadiusAll(1);
        style.SetContentMarginAll(6);
        _panel.AddThemeStyleboxOverride("panel", style);
        _panel.Position = new Vector2(20, 10);
        _panel.CustomMinimumSize = new Vector2(216, 172);
        _panel.Size = new Vector2(216, 172);
        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 2);
        var top = new HBoxContainer();
        _title = MakeLabel("", 10, Accent);
        _title.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _header = MakeLabel("", 9, Selected);
        top.AddChild(_title);
        top.AddChild(_header);
        _tabsRow = new HBoxContainer();
        _tabsRow.AddThemeConstantOverride("separation", 8);
        _list = new VBoxContainer();
        _list.AddThemeConstantOverride("separation", 1);
        _list.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        _description = MakeLabel("", 8, Text);
        _description.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _description.CustomMinimumSize = new Vector2(0, 26);
        _feedback = MakeLabel("", 8, Accent);
        _hint = MakeLabel("", 7, Muted);
        _hint.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _title.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _panel.ClipContents = true;
        vbox.AddChild(top);
        vbox.AddChild(_tabsRow);
        vbox.AddChild(_list);
        vbox.AddChild(_description);
        vbox.AddChild(_feedback);
        vbox.AddChild(_hint);
        _panel.AddChild(vbox);
        AddChild(_panel);
    }

    protected void Refresh()
    {
        _title.Text = Title;
        _header.Text = Header;
        _hint.Text = Hint;
        foreach (var c in _tabsRow.GetChildren()) c.QueueFree();
        for (int i = 0; i < Tabs.Length; i++)
            _tabsRow.AddChild(MakeLabel((i == TabIndex ? "[ " : "  ") + Tabs[i] + (i == TabIndex ? " ]" : "  "), 9, i == TabIndex ? Selected : Muted));
        foreach (var c in _list.GetChildren()) c.QueueFree();
        var entries = GetEntries();
        if (entries.Count == 0)
            _list.AddChild(MakeLabel("(rien)", 9, Muted));
        Index = entries.Count == 0 ? 0 : Mathf.Clamp(Index, 0, entries.Count - 1);
        for (int i = 0; i < entries.Count; i++)
        {
            bool sel = i == Index;
            var row = new PanelContainer();
            var rs = new StyleBoxFlat { BgColor = sel ? SelectedBg : new Color(0, 0, 0, 0) };
            rs.SetContentMarginAll(1);
            rs.ContentMarginLeft = 4;
            row.AddThemeStyleboxOverride("panel", rs);
            var h = new HBoxContainer();
            Color c = !entries[i].Enabled ? Muted : sel ? Selected : Text;
            var name = MakeLabel((sel ? "> " : "  ") + entries[i].Label, 9, c);
            name.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            h.AddChild(name);
            h.AddChild(MakeLabel(entries[i].Right, 9, c));
            row.AddChild(h);
            _list.AddChild(row);
        }
        _description.Text = entries.Count > 0 ? entries[Index].Description : "";
    }
}
