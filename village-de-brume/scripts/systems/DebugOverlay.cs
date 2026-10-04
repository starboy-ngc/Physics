using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Autoload "DebugOverlay" : panneau de debug (touche F3).
/// Les lignes DAY / TIME seront alimentées à l'étape 3 (WorldTime).
/// </summary>
public partial class DebugOverlay : CanvasLayer
{
    private Label _label = null!;

    public override void _Ready()
    {
        Layer = 100;
        Visible = false;
        var panel = new PanelContainer
        {
            Position = new Vector2(8, 8),
            SelfModulate = new Color(1, 1, 1, 0.85f),
        };
        _label = new Label();
        _label.AddThemeFontSizeOverride("font_size", 8);
        panel.AddChild(_label);
        AddChild(panel);
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event.IsActionPressed("debug_toggle"))
            Visible = !Visible;
    }

    public override void _Process(double delta)
    {
        if (!Visible)
            return;
        var game = Game.Instance;
        var lines = new List<string>
        {
            "DAY: - (étape 3)",
            "TIME: - (étape 3)",
            "PLAYER POSITION:",
        };
        if (game.Player != null)
        {
            lines.Add($"TILE: {game.Player.Tile.X}, {game.Player.Tile.Y}");
            lines.Add($"FACING: {game.Player.Facing}");
        }
        lines.Add("CURRENT LOCATION:");
        lines.Add(game.CurrentZone?.ZoneName ?? "-");
        lines.Add("NPC:");
        var npcs = NpcManager.Instance;
        foreach (var id in npcs.Npcs.Keys)
        {
            string here = npcs.Instances.ContainsKey(id) ? "*" : " ";
            lines.Add($"{here} {npcs.GetNpcName(id)}  LOCATION: {npcs.GetZoneOf(id)}");
        }
        lines.Add($"DIALOGUE: {(DialogueManager.Instance.IsActive ? "actif" : "-")}");
        lines.Add($"FPS: {Engine.GetFramesPerSecond()}");
        _label.Text = string.Join("\n", lines);
    }
}
