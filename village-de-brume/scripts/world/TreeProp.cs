using Godot;

namespace VillageDeBrume;

/// <summary>Arbre : tronc, feuillage en trois nuances avec contour. Origine au pied.</summary>
public partial class TreeProp : StaticBody2D
{
    private float _canopyRadius = 14f;
    [Export] public float CanopyRadius { get => _canopyRadius; set { _canopyRadius = value; QueueRedraw(); } }

    private static readonly Color Trunk = new("7a4e2a");
    private static readonly Color TrunkDark = new("4e3018");
    private static readonly Color Canopy = new("3f8a3a");
    private static readonly Color CanopyDark = new("2f6a2c");
    private static readonly Color CanopyLight = new("66b154");
    private static readonly Color Outline = new("1e3a1a");

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        AddChild(new CollisionShape2D
        {
            Shape = new CircleShape2D { Radius = 6f },
            Position = new Vector2(0, -4),
        });
    }

    public override void _Draw()
    {
        DrawRect(new Rect2(-6, -2, 12, 3), new Color(0, 0, 0, 0.2f));
        DrawRect(new Rect2(-3, -18, 6, 18), Trunk);
        DrawRect(new Rect2(-3, -18, 2, 18), TrunkDark);
        float r = CanopyRadius;
        var c = new Vector2(0, -18 - r * 0.7f);
        DrawCircle(c, r + 1.5f, Outline);
        DrawCircle(c, r, CanopyDark);
        DrawCircle(c + new Vector2(-r * 0.15f, -r * 0.2f), r * 0.85f, Canopy);
        DrawCircle(c + new Vector2(-r * 0.35f, -r * 0.4f), r * 0.4f, CanopyLight);
        DrawCircle(c + new Vector2(r * 0.3f, -r * 0.1f), r * 0.25f, CanopyLight.Darkened(0.1f));
    }
}
