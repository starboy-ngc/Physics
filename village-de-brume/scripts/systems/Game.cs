using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VillageDeBrume;

/// <summary>
/// Autoload "Game" : gère les zones (village, intérieurs) et le passage du joueur
/// de l'une à l'autre. C'est le seul endroit qui connaît la liste des zones.
/// Le joueur est un noeud unique qui persiste : il est simplement déplacé
/// (re-parenté) dans la zone courante, afin d'être trié en Y avec le décor.
/// </summary>
public partial class Game : Node
{
    public static Game Instance { get; private set; } = null!;

    /// <summary>Identifiant de zone -> scène. Ajouter ici toute nouvelle zone.</summary>
    public static readonly Dictionary<string, string> Zones = new()
    {
        ["village"] = "res://scenes/world/Village.tscn",
        ["house_player"] = "res://scenes/world/interiors/HousePlayer.tscn",
        ["bakery"] = "res://scenes/world/interiors/Bakery.tscn",
        ["house_jeanne"] = "res://scenes/world/interiors/HouseJeanne.tscn",
        ["house_martin"] = "res://scenes/world/interiors/HouseMartin.tscn",
    };

    private const float FadeTime = 0.15f;
    /// <summary>Délai pendant lequel les portes sont ignorées après une transition.</summary>
    private const float DoorCooldown = 0.4f;

    public event Action<Zone>? ZoneChanged;

    public Player Player { get; private set; } = null!;
    public Zone? CurrentZone { get; private set; }
    public string CurrentZoneId { get; private set; } = "";

    private Node? _zoneRoot;
    private bool _transitioning;
    private float _doorCooldown;
    private ColorRect _fade = null!;

    public override void _EnterTree()
    {
        Instance = this;
    }

    public override void _Ready()
    {
        var layer = new CanvasLayer { Name = "FadeLayer", Layer = 50 };
        _fade = new ColorRect
        {
            Name = "Fade",
            Color = new Color(0, 0, 0, 0),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        _fade.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        layer.AddChild(_fade);
        AddChild(layer);
    }

    public override void _Process(double delta)
    {
        if (_doorCooldown > 0f)
            _doorCooldown -= (float)delta;
    }

    /// <summary>Appelé une fois par la scène principale.</summary>
    public void Setup(Node zoneRoot, Player player)
    {
        _zoneRoot = zoneRoot;
        Player = player;
    }

    public bool IsReady => _zoneRoot != null && Player != null;

    public bool CanUseDoor() => IsReady && !_transitioning && _doorCooldown <= 0f && CurrentZone != null;

    /// <summary>
    /// Demande de changement de zone depuis une porte (contexte physique).
    /// Le changement réel est différé pour ne pas modifier l'arbre pendant la
    /// simulation physique.
    /// </summary>
    public void RequestZoneChange(string zoneId, string spawnName)
    {
        if (!CanUseDoor())
            return;
        _transitioning = true;
        Callable.From(() => { _ = ChangeZone(zoneId, spawnName, false); }).CallDeferred();
    }

    /// <summary>Change de zone avec un fondu (ou instantanément).</summary>
    public async Task ChangeZone(string zoneId, string spawnName, bool instant = false)
    {
        if (!IsReady)
        {
            GD.PushError("Game.ChangeZone appelé avant Game.Setup().");
            _transitioning = false;
            return;
        }
        if (!Zones.ContainsKey(zoneId))
        {
            GD.PushError($"Zone inconnue : '{zoneId}'");
            _transitioning = false;
            return;
        }
        _transitioning = true;
        if (!instant)
            await FadeTo(1f);
        LoadZone(zoneId, spawnName);
        if (!instant)
            await FadeTo(0f);
        _doorCooldown = DoorCooldown;
        _transitioning = false;
    }

    private void LoadZone(string zoneId, string spawnName)
    {
        // 1. Retirer le joueur de l'ancienne zone et libérer celle-ci.
        Player.GetParent()?.RemoveChild(Player);
        if (CurrentZone != null)
        {
            // Libération immédiate (et non QueueFree) : sinon les collisions de
            // l'ancienne zone coexistent une frame avec la nouvelle et repoussent
            // le joueur. Cette méthode n'est jamais appelée pendant la physique.
            _zoneRoot!.RemoveChild(CurrentZone);
            CurrentZone.Free();
            CurrentZone = null;
        }

        // 2. Instancier la nouvelle zone.
        var scene = GD.Load<PackedScene>(Zones[zoneId]);
        if (scene.Instantiate() is not Zone zone)
        {
            GD.PushError($"La scène '{Zones[zoneId]}' n'est pas une Zone.");
            return;
        }
        _zoneRoot!.AddChild(zone);
        CurrentZone = zone;
        CurrentZoneId = zoneId;

        // 3. Placer le joueur dans la zone, au point d'apparition demandé.
        zone.AddChild(Player);
        Player.GlobalPosition = zone.GetSpawnPosition(spawnName);
        Player.Velocity = Vector2.Zero;
        Player.Face(spawnName != "entrance" ? CharacterVisual.Facing.Down : CharacterVisual.Facing.Up);

        // 4. Caméra : limites de la zone, sans glissement depuis l'ancienne position.
        ApplyCameraLimits(zone);
        Player.Camera.MakeCurrent();
        Player.Camera.ResetSmoothing();

        ZoneChanged?.Invoke(zone);
    }

    /// <summary>
    /// Les limites de la caméra épousent la zone. Si la zone est plus petite que
    /// l'écran (intérieurs), les limites sont centrées sur la zone.
    /// </summary>
    private void ApplyCameraLimits(Zone zone)
    {
        var cam = Player.Camera;
        Vector2 view = Player.GetViewportRect().Size / cam.Zoom;
        Rect2 b = zone.Bounds;
        float left = b.Position.X, right = b.End.X, top = b.Position.Y, bottom = b.End.Y;
        if (b.Size.X < view.X)
        {
            float cx = b.GetCenter().X;
            left = cx - view.X / 2f;
            right = cx + view.X / 2f;
        }
        if (b.Size.Y < view.Y)
        {
            float cy = b.GetCenter().Y;
            top = cy - view.Y / 2f;
            bottom = cy + view.Y / 2f;
        }
        cam.LimitLeft = Mathf.FloorToInt(left);
        cam.LimitRight = Mathf.CeilToInt(right);
        cam.LimitTop = Mathf.FloorToInt(top);
        cam.LimitBottom = Mathf.CeilToInt(bottom);
    }

    private async Task FadeTo(float alpha)
    {
        var tween = CreateTween();
        tween.TweenProperty(_fade, "color:a", alpha, FadeTime);
        await ToSignal(tween, Tween.SignalName.Finished);
    }
}
