using Godot;

namespace VillageDeBrume;

/// <summary>
/// Tout ce avec quoi le joueur peut interagir en appuyant sur E.
/// Le joueur détecte les Interactable devant lui (couche 3) et affiche
/// « E — Prompt ». Les sous-classes redéfinissent Interact().
/// </summary>
public partial class Interactable : Area3D
{
    [Export] public string Prompt { get; set; } = "Examiner";
    [Export] public Vector3 Size { get; set; } = new(1f, 1.5f, 1.25f);
    [Export] public Vector3 Offset { get; set; } = new(0, 0.75f, -0.5f);

    public override void _Ready()
    {
        CollisionLayer = 4;
        CollisionMask = 0;
        Monitoring = false;
        Monitorable = true;
        Materials.BoxCollider(this, Size, Offset);
    }

    /// <summary>Appelé par le joueur. À redéfinir.</summary>
    public virtual void Interact(Node3D player) { }
}
