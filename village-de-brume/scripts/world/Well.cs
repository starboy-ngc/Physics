using Godot;

namespace VillageDeBrume;

/// <summary>Puits de la place centrale : margelle, eau, deux poteaux et petit toit.</summary>
public partial class Well : StaticBody3D
{
    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        AddChild(new CollisionShape3D
        {
            Shape = new CylinderShape3D { Radius = 1.1f, Height = 2f },
            Position = new Vector3(0, 1f, 0),
        });
        Materials.Cylinder(this, 1.0f, 0.9f, new Vector3(0, 0.45f, 0), Materials.Flat(new Color("8f8f88")), "Rim");
        Materials.Cylinder(this, 0.75f, 0.92f, new Vector3(0, 0.45f, 0), Materials.Flat(new Color("2f5f8f")), "Water");
        var wood = Materials.Flat(new Color("6b4a2a"));
        Materials.Box(this, new Vector3(0.15f, 2.0f, 0.15f), new Vector3(-0.85f, 1.0f, 0), wood, "PostL");
        Materials.Box(this, new Vector3(0.15f, 2.0f, 0.15f), new Vector3(0.85f, 1.0f, 0), wood, "PostR");
        var roof = new MeshInstance3D
        {
            Name = "Roof",
            Mesh = new PrismMesh { Size = new Vector3(1.3f, 0.6f, 2.2f), LeftToRight = 0.5f },
            MaterialOverride = Materials.Flat(new Color("8c4a3c")),
            Position = new Vector3(0, 2.3f, 0),
            RotationDegrees = new Vector3(0, 90, 0),
        };
        AddChild(roof);
    }
}
