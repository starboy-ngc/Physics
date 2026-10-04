using Godot;

namespace VillageDeBrume;

/// <summary>
/// Zone de passage : quand le joueur est dessus, il change de zone.
/// Utilisée par les bâtiments (entrée) et par les intérieurs (sortie).
/// </summary>
public partial class Door : Area2D
{
    [Export] public string TargetZone { get; set; } = "";
    [Export] public string TargetSpawn { get; set; } = "entrance";
    [Export] public Vector2 Size { get; set; } = new(20, 16);
    /// <summary>Dessine un paillasson (utile pour les sorties d'intérieur).</summary>
    [Export] public bool DrawMat { get; set; } = false;

    public override void _Ready()
    {
        CollisionLayer = 0;
        CollisionMask = 2; // couche "player"
        AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = Size } });
    }

    /// <summary>
    /// Vérification à chaque tick physique (et non seulement sur BodyEntered) :
    /// si le joueur arrive sur la porte pendant le délai anti-rebond et reste
    /// dessus, la porte doit quand même se déclencher à la fin du délai.
    /// </summary>
    public override void _PhysicsProcess(double delta)
    {
        if (TargetZone == "" || !HasOverlappingBodies())
            return;
        if (!Game.Instance.CanUseDoor())
            return;
        foreach (var body in GetOverlappingBodies())
        {
            if (body is Player)
            {
                Game.Instance.RequestZoneChange(TargetZone, TargetSpawn);
                return;
            }
        }
    }

    public override void _Draw()
    {
        if (!DrawMat)
            return;
        var rect = new Rect2(-Size / 2f, Size);
        DrawRect(rect, new Color("3b2a1a"));
        DrawRect(rect.Grow(-3f), new Color("6b4a2a"));
    }
}
