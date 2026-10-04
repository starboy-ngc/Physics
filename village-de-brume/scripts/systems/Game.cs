using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VillageDeBrume;

/// <summary>
/// Autoload "Game" : gère les zones et le passage du joueur de l'une à l'autre.
/// Le joueur est un noeud unique qui persiste : il est re-parenté dans la zone
/// courante (tri en Y) et placé sur une case d'apparition.
/// </summary>
public partial class Game : Node
{
    public static Game Instance { get; private set; } = null!;

    /// <summary>Identifiant de zone -> fabrique. Ajouter ici toute nouvelle zone.</summary>
    public static readonly Dictionary<string, Func<Zone>> Zones = new()
    {
        ["village"] = () => new Village(),
        ["base"] = () => new BaseInterior(),
    };

    private const float FadeTime = 0.15f;
    private const float DoorCooldown = 0.3f;

    public event Action<Zone>? ZoneChanged;

    public Player Player { get; private set; } = null!;
    public Zone? CurrentZone { get; private set; }
    public string CurrentZoneId { get; private set; } = "";

    private Node? _zoneRoot;
    private bool _transitioning;
    private float _doorCooldown;
    private ColorRect _fade = null!;

    public override void _EnterTree() => Instance = this;

    public override void _Ready()
    {
        var layer = new CanvasLayer { Name = "FadeLayer", Layer = 50 };
        _fade = new ColorRect { Name = "Fade", Color = new Color(0, 0, 0, 0), MouseFilter = Control.MouseFilterEnum.Ignore };
        _fade.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        layer.AddChild(_fade);
        AddChild(layer);
    }

    public override void _Process(double delta)
    {
        if (_doorCooldown > 0f) _doorCooldown -= (float)delta;
    }

    public void Setup(Node zoneRoot, Player player)
    {
        _zoneRoot = zoneRoot;
        Player = player;
    }

    public bool IsReady => _zoneRoot != null && Player != null;
    public bool CanUseDoor() => IsReady && !_transitioning && _doorCooldown <= 0f && CurrentZone != null;

    /// <summary>Demande de changement de zone (porte franchie). Différé pour sortir de la boucle de déplacement.</summary>
    public void RequestZoneChange(string zoneId, string spawnName)
    {
        if (!CanUseDoor()) return;
        _transitioning = true;
        Callable.From(() => { _ = ChangeZone(zoneId, spawnName, false); }).CallDeferred();
    }

    public async Task ChangeZone(string zoneId, string spawnName, bool instant = false)
    {
        if (!IsReady) { GD.PushError("Game.ChangeZone appelé avant Game.Setup()."); _transitioning = false; return; }
        if (!Zones.ContainsKey(zoneId)) { GD.PushError($"Zone inconnue : '{zoneId}'"); _transitioning = false; return; }
        _transitioning = true;
        if (!instant) await FadeTo(1f);
        LoadZone(zoneId, spawnName);
        if (!instant) await FadeTo(0f);
        _doorCooldown = DoorCooldown;
        _transitioning = false;
    }

    private void LoadZone(string zoneId, string spawnName)
    {
        Player.Detach();
        Player.GetParent()?.RemoveChild(Player);
        if (CurrentZone != null)
        {
            _zoneRoot!.RemoveChild(CurrentZone);
            CurrentZone.Free();
            CurrentZone = null;
        }
        var zone = Zones[zoneId]();
        zone.Name = zoneId;
        _zoneRoot!.AddChild(zone);
        CurrentZone = zone;
        CurrentZoneId = zoneId;

        zone.AddChild(Player);
        Player.PlaceAt(zone, zone.GetSpawn(spawnName), spawnName == "entrance" ? CharacterSprites.Facing.Up : CharacterSprites.Facing.Down);

        ApplyCameraLimits(zone);
        Player.Camera.MakeCurrent();
        Player.Camera.ResetSmoothing();
        ZoneChanged?.Invoke(zone);
    }

    /// <summary>Les limites de la caméra épousent la zone, centrées si la zone est plus petite que l'écran.</summary>
    private void ApplyCameraLimits(Zone zone)
    {
        var cam = Player.Camera;
        Vector2 view = Player.GetViewportRect().Size / cam.Zoom;
        Rect2 b = zone.Bounds;
        float left = b.Position.X, right = b.End.X, top = b.Position.Y, bottom = b.End.Y;
        if (b.Size.X < view.X) { float cx = b.GetCenter().X; left = cx - view.X / 2f; right = cx + view.X / 2f; }
        if (b.Size.Y < view.Y) { float cy = b.GetCenter().Y; top = cy - view.Y / 2f; bottom = cy + view.Y / 2f; }
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
