using Godot;

namespace VillageDeBrume;

/// <summary>
/// Étang : plan d'eau ovale, berge boueuse, roseaux ; infranchissable.
/// Porte une zone de pêche (FishingSpot) tout autour de la berge.
/// Origine au centre, au sol ; Size = emprise (x, z).
/// </summary>
public partial class Pond : StaticBody3D
{
    [Export] public Vector2 Size { get; set; } = new(7f, 4.5f);

    public FishingSpot Spot { get; private set; } = null!;

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        float w = Size.X, d = Size.Y;
        // Collision légèrement plus petite que l'ovale pour laisser approcher la berge.
        Materials.BoxCollider(this, new Vector3(w - 0.6f, 1f, d - 0.6f), new Vector3(0, 0.5f, 0));

        AddDisc("Bank", w / 2f + 0.6f, d / 2f + 0.6f, 0.012f, Materials.Flat(new Color("5c5242")));
        var water = Materials.Flat(new Color(0.23f, 0.34f, 0.40f, 0.92f));
        AddDisc("Water", w / 2f, d / 2f, 0.03f, water);
        AddDisc("WaterLight", w / 2f - 0.9f, d / 2f - 0.7f, 0.035f, Materials.Flat(new Color(0.30f, 0.42f, 0.47f, 0.6f)));

        // Roseaux sur la berge
        var reed = Materials.Flat(new Color("4f6a3a"));
        var rng = new RandomNumberGenerator { Seed = 21 };
        for (int i = 0; i < 14; i++)
        {
            float a = rng.RandfRange(0f, Mathf.Tau);
            var pos = new Vector3(Mathf.Cos(a) * (w / 2f + 0.25f), 0f, Mathf.Sin(a) * (d / 2f + 0.25f));
            float h = rng.RandfRange(0.7f, 1.2f);
            Materials.Cylinder(this, 0.04f, h, pos + new Vector3(0, h / 2f, 0), reed, "Reed");
            if (rng.Randf() < 0.5f)
                Materials.Cylinder(this, 0.05f, h * 0.8f, pos + new Vector3(0.12f, h * 0.4f, 0.08f), reed, "Reed2");
        }

        Spot = new FishingSpot
        {
            Name = "FishingSpot",
            Size = new Vector3(w + 1.4f, 1.5f, d + 1.4f),
            Offset = new Vector3(0, 0.75f, 0),
        };
        AddChild(Spot);
    }

    private void AddDisc(string name, float rx, float rz, float y, Material mat)
    {
        AddChild(new MeshInstance3D
        {
            Name = name,
            Mesh = new CylinderMesh { TopRadius = 1f, BottomRadius = 1f, Height = 0.02f, RadialSegments = 32 },
            MaterialOverride = mat,
            Position = new Vector3(0, y, 0),
            Scale = new Vector3(rx, 1f, rz),
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        });
    }
}
