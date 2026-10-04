using Godot;

namespace VillageDeBrume;

/// <summary>
/// Zone de passage : quand le joueur est dessus, il change de zone.
/// Utilisée par les bâtiments (entrée) et par les intérieurs (sortie).
/// </summary>
public partial class Door : Area3D
{
    [Export] public string TargetZone { get; set; } = "";
    [Export] public string TargetSpawn { get; set; } = "entrance";
    /// <summary>Emprise au sol (x, z).</summary>
    [Export] public Vector2 Size { get; set; } = new(1.25f, 1f);
    /// <summary>Dessine un paillasson (sorties d'intérieur).</summary>
    [Export] public bool DrawMat { get; set; } = false;

    public override void _Ready()
    {
        CollisionLayer = 0;
        CollisionMask = 2; // couche "player"
        Materials.BoxCollider(this, new Vector3(Size.X, 1f, Size.Y), new Vector3(0, 0.5f, 0));
        if (DrawMat)
        {
            Materials.Box(this, new Vector3(Size.X, 0.04f, Size.Y), new Vector3(0, 0.02f, 0), Materials.Flat(new Color("3b2a1a")), "Mat");
            Materials.Box(this, new Vector3(Size.X - 0.3f, 0.05f, Size.Y - 0.3f), new Vector3(0, 0.02f, 0), Materials.Flat(new Color("6b4a2a")), "MatInner");
        }
    }

    /// <summary>
    /// Vérification à chaque tick physique (et non seulement sur BodyEntered) :
    /// si le joueur arrive sur la porte pendant le délai anti-rebond et reste
    /// dessus, la porte doit quand même se déclencher à la fin du délai.
    /// </summary>
    public override void _PhysicsProcess(double delta)
    {
        if (TargetZone == "" || !HasOverlappingBodies() || !Game.Instance.CanUseDoor())
            return;
        foreach (var body in GetOverlappingBodies())
        {
            if (body is Player)
            {
                Game.Instance.RequestZoneChange(TargetZone, TargetSpawn);
                return;
            }
        }
    }
}
