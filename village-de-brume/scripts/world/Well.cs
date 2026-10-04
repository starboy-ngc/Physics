using Godot;

namespace VillageDeBrume;

/// <summary>Puits de la place centrale. Origine au bas de la margelle.</summary>
public partial class Well : StaticBody2D
{
    private static readonly Color Stone = new("8f8f88");
    private static readonly Color StoneDark = new("5c5c58");
    private static readonly Color Water = new("2f5f8f");
    private static readonly Color Wood = new("6b4a2a");
    private static readonly Color Roof = new("8c4a3c");
    private static readonly Color Outline = new("2a2a2a");

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        AddChild(new CollisionShape2D
        {
            Shape = new RectangleShape2D { Size = new Vector2(32, 20) },
            Position = new Vector2(0, -8),
        });
    }

    public override void _Draw()
    {
        DrawRect(new Rect2(-16, -18, 32, 18), Stone);
        DrawRect(new Rect2(-16, -18, 32, 18), Outline, false, 1f);
        DrawRect(new Rect2(-12, -16, 24, 8), Water);
        DrawRect(new Rect2(-16, -4, 32, 4), StoneDark);
        DrawRect(new Rect2(-14, -44, 3, 28), Wood);
        DrawRect(new Rect2(11, -44, 3, 28), Wood);
        var roof = new[] { new Vector2(-20, -42), new Vector2(20, -42), new Vector2(0, -56) };
        DrawColoredPolygon(roof, Roof);
        DrawPolyline(new[] { roof[0], roof[1], roof[2], roof[0] }, Outline, 1f);
    }
}
