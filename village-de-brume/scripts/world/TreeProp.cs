using Godot;

namespace VillageDeBrume;

/// <summary>
/// Arbre : feuillu (sphères sombres) ou sapin (cônes empilés). Origine au pied.
/// </summary>
public partial class TreeProp : StaticBody3D
{
    [Export] public float CanopyRadius { get; set; } = 0.9f;
    [Export(PropertyHint.Enum, "round,pine")] public string Kind { get; set; } = "round";

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        AddChild(new CollisionShape3D
        {
            Shape = new CylinderShape3D { Radius = 0.4f, Height = 2f },
            Position = new Vector3(0, 1f, 0),
        });
        var trunk = Materials.Flat(new Color("4d3626"));
        float r = CanopyRadius;
        if (Kind == "pine")
        {
            Materials.Cylinder(this, 0.16f, 1.0f, new Vector3(0, 0.5f, 0), trunk, "Trunk");
            var needles = Materials.Flat(new Color("2f4a33"));
            var needlesLight = Materials.Flat(new Color("3a5a3c"));
            float y = 0.9f;
            foreach (var (radius, height) in new[] { (r * 1.05f, 1.4f), (r * 0.8f, 1.3f), (r * 0.5f, 1.1f) })
            {
                var cone = new MeshInstance3D
                {
                    Name = "Cone",
                    Mesh = new CylinderMesh { TopRadius = 0f, BottomRadius = radius, Height = height, RadialSegments = 10 },
                    MaterialOverride = radius > r * 0.6f ? needles : needlesLight,
                    Position = new Vector3(0, y + height / 2f, 0),
                };
                AddChild(cone);
                y += height * 0.55f;
            }
        }
        else
        {
            Materials.Cylinder(this, 0.2f, 1.4f, new Vector3(0, 0.7f, 0), trunk, "Trunk");
            Materials.Sphere(this, r, new Vector3(0, 1.4f + r * 0.8f, 0), Materials.Flat(new Color("3b5637")), "Canopy");
            Materials.Sphere(this, r * 0.7f, new Vector3(-r * 0.35f, 1.4f + r * 1.2f, r * 0.25f), Materials.Flat(new Color("48653f")), "CanopyLight");
            Materials.Sphere(this, r * 0.55f, new Vector3(r * 0.45f, 1.4f + r * 0.9f, -r * 0.2f), Materials.Flat(new Color("34503a")), "CanopyDark");
        }
    }
}
