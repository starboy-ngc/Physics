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
        Materials.Cylinder(this, 1.0f, 0.9f, new Vector3(0, 0.45f, 0), Materials.Flat(new Color("6f6e68")), "Rim");
        Materials.Cylinder(this, 0.75f, 0.92f, new Vector3(0, 0.45f, 0), Materials.Flat(new Color("2b4150")), "Water");
        var wood = Materials.Flat(new Color("4a3b2e"));
        Materials.Box(this, new Vector3(0.15f, 2.1f, 0.15f), new Vector3(-0.85f, 1.05f, 0), wood, "PostL");
        Materials.Box(this, new Vector3(0.15f, 2.1f, 0.15f), new Vector3(0.85f, 1.05f, 0), wood, "PostR");
        // Petit toit pointu à quatre pans, posé sur les poteaux.
        var roof = new MeshInstance3D
        {
            Name = "Roof",
            Mesh = new CylinderMesh { TopRadius = 0f, BottomRadius = 1.35f, Height = 0.9f, RadialSegments = 4 },
            MaterialOverride = Materials.Flat(new Color("4e5560")),
            Position = new Vector3(0, 2.45f, 0),
            RotationDegrees = new Vector3(0, 45, 0),
        };
        AddChild(roof);
    }
}
