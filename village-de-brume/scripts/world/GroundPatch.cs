using Godot;

namespace VillageDeBrume;

/// <summary>
/// Rectangle de sol décoratif (chemin de terre, place pavée), posé juste
/// au-dessus de l'herbe. Pas de collision. Rect en unités monde (x, z).
/// </summary>
public partial class GroundPatch : Node3D
{
    [Export] public Rect2 Rect { get; set; } = new(0, 0, 2, 2);
    [Export(PropertyHint.Enum, "dirt,stone")] public int Kind { get; set; } = 0;

    public override void _Ready()
    {
        var mat = Kind == 0
            ? Materials.Textured("dirt", Rect.Size, Materials.Dirt, 2f)
            : Materials.Textured("stone", Rect.Size, Materials.Stone, 2f);
        AddChild(new MeshInstance3D
        {
            Name = "Patch",
            Mesh = new PlaneMesh { Size = Rect.Size },
            MaterialOverride = mat,
            Position = new Vector3(Rect.GetCenter().X, Kind == 0 ? 0.015f : 0.03f, Rect.GetCenter().Y),
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        });
    }
}
