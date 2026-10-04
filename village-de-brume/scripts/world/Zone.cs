using Godot;

namespace VillageDeBrume;

/// <summary>
/// Base de toute zone jouable (village, intérieur...) en 2.5D.
/// Le sol est le plan y = 0 ; Bounds est le rectangle (x, z) de la zone en
/// unités monde (1 unité = 1 tuile de 16 px). Les points d'apparition sont
/// des Marker3D enfants d'un noeud "Spawns".
/// </summary>
public partial class Zone : Node3D
{
    [Export] public string ZoneName { get; set; } = "Zone";
    [Export] public Rect2 Bounds { get; set; } = new(0, 0, 48, 36);
    /// <summary>Bande infranchissable au fond (-Z) : mur du fond des intérieurs.</summary>
    [Export] public float WallTop { get; set; } = 0f;
    /// <summary>Bande infranchissable sur les côtés et devant (+Z).</summary>
    [Export] public float WallSides { get; set; } = 0f;

    private const float WallThickness = 2f;
    private const float WallHeight = 4f;

    public override void _Ready()
    {
        BuildBoundaries();
        BuildGround();
    }

    public Vector3 GetSpawnPosition(string spawnName)
    {
        var marker = GetNodeOrNull<Node3D>("Spawns/" + spawnName);
        if (marker == null)
        {
            GD.PushWarning($"Zone '{ZoneName}' : point d'apparition '{spawnName}' introuvable, centre utilisé.");
            Vector2 c = Bounds.GetCenter();
            return new Vector3(c.X, 0f, c.Y);
        }
        Vector3 p = marker.GlobalPosition;
        return new Vector3(p.X, 0f, p.Z);
    }

    /// <summary>Le sol de la zone. Redéfini par les zones concrètes.</summary>
    protected virtual void BuildGround() { }

    /// <summary>Murs invisibles tout autour de la zone jouable.</summary>
    private void BuildBoundaries()
    {
        var body = new StaticBody3D { Name = "Boundaries", CollisionLayer = 1, CollisionMask = 0 };
        var inner = new Rect2(
            Bounds.Position + new Vector2(WallSides, WallTop),
            Bounds.Size - new Vector2(WallSides * 2f, WallTop + WallSides));
        float t = WallThickness, h = WallHeight;
        AddWall(body, new Rect2(inner.Position.X - t, inner.Position.Y - t, inner.Size.X + 2f * t, t));
        AddWall(body, new Rect2(inner.Position.X - t, inner.End.Y, inner.Size.X + 2f * t, t));
        AddWall(body, new Rect2(inner.Position.X - t, inner.Position.Y, t, inner.Size.Y));
        AddWall(body, new Rect2(inner.End.X, inner.Position.Y, t, inner.Size.Y));
        AddChild(body);

        void AddWall(StaticBody3D b, Rect2 r) =>
            Materials.BoxCollider(b, new Vector3(r.Size.X, h, r.Size.Y), new Vector3(r.GetCenter().X, h / 2f, r.GetCenter().Y));
    }

    /// <summary>Plan texturé horizontal couvrant `rect` (x, z) à la hauteur y.</summary>
    protected MeshInstance3D AddFloor(Rect2 rect, float y, Material mat, string name)
    {
        var mi = new MeshInstance3D
        {
            Name = name,
            Mesh = new PlaneMesh { Size = rect.Size },
            MaterialOverride = mat,
            Position = new Vector3(rect.GetCenter().X, y, rect.GetCenter().Y),
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
        AddChild(mi);
        return mi;
    }
}
