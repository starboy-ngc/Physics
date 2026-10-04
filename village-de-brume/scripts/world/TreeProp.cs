using Godot;

namespace VillageDeBrume;

/// <summary>Arbre : tronc cylindrique et feuillage en deux sphères. Origine au pied.</summary>
public partial class TreeProp : StaticBody3D
{
    [Export] public float CanopyRadius { get; set; } = 0.9f;

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        AddChild(new CollisionShape3D
        {
            Shape = new CylinderShape3D { Radius = 0.4f, Height = 2f },
            Position = new Vector3(0, 1f, 0),
        });
        float r = CanopyRadius;
        Materials.Cylinder(this, 0.18f, 1.3f, new Vector3(0, 0.65f, 0), Materials.Flat(new Color("7a4e2a")), "Trunk");
        Materials.Sphere(this, r, new Vector3(0, 1.3f + r * 0.8f, 0), Materials.Flat(new Color("3f8a3a")), "Canopy");
        Materials.Sphere(this, r * 0.6f, new Vector3(-r * 0.3f, 1.3f + r * 1.25f, r * 0.2f), Materials.Flat(new Color("66b154")), "CanopyLight");
    }
}
