using Godot;

namespace VillageDeBrume;

/// <summary>
/// Base de toute zone jouable (village, intérieur de maison...).
/// Une zone connaît son nom, ses limites Bounds (caméra + murs invisibles)
/// et ses points d'apparition : des Marker2D enfants d'un noeud "Spawns".
/// Les enfants sont triés en Y (vue 3/4) : l'origine de chaque élément doit
/// être à sa base (pieds, bas des murs, pied du tronc...).
/// </summary>
public partial class Zone : Node2D
{
    [Export] public string ZoneName { get; set; } = "Zone";
    [Export] public Rect2 Bounds { get; set; } = new(0, 0, 768, 576);
    [Export] public Color GroundColor { get; set; } = new("5f9e4a");
    /// <summary>Zone infranchissable en haut (mur du fond des intérieurs).</summary>
    [Export] public float WallTop { get; set; } = 0f;
    /// <summary>Zone infranchissable sur les côtés et en bas.</summary>
    [Export] public float WallSides { get; set; } = 0f;

    private const float WallThickness = 32f;

    public override void _Ready()
    {
        YSortEnabled = true;
        BuildBoundaries();
    }

    public Vector2 GetSpawnPosition(string spawnName)
    {
        var marker = GetNodeOrNull<Node2D>("Spawns/" + spawnName);
        if (marker == null)
        {
            GD.PushWarning($"Zone '{ZoneName}' : point d'apparition '{spawnName}' introuvable, centre utilisé.");
            return Bounds.GetCenter();
        }
        return marker.GlobalPosition;
    }

    /// <summary>Murs invisibles tout autour de la zone jouable.</summary>
    private void BuildBoundaries()
    {
        var body = new StaticBody2D { Name = "Boundaries", CollisionLayer = 1, CollisionMask = 0 };
        var inner = new Rect2(
            Bounds.Position + new Vector2(WallSides, WallTop),
            Bounds.Size - new Vector2(WallSides * 2f, WallTop + WallSides));
        float t = WallThickness;
        AddWall(body, new Rect2(inner.Position.X - t, inner.Position.Y - t, inner.Size.X + 2f * t, t));
        AddWall(body, new Rect2(inner.Position.X - t, inner.End.Y, inner.Size.X + 2f * t, t));
        AddWall(body, new Rect2(inner.Position.X - t, inner.Position.Y, t, inner.Size.Y));
        AddWall(body, new Rect2(inner.End.X, inner.Position.Y, t, inner.Size.Y));
        AddChild(body);
    }

    private static void AddWall(StaticBody2D body, Rect2 rect)
    {
        body.AddChild(new CollisionShape2D
        {
            Shape = new RectangleShape2D { Size = rect.Size },
            Position = rect.GetCenter(),
        });
    }

    public override void _Draw()
    {
        DrawRect(Bounds, GroundColor);
    }
}
