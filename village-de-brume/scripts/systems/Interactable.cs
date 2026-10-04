using Godot;

namespace VillageDeBrume;

/// <summary>
/// Tout ce avec quoi le joueur peut interagir en appuyant sur E.
/// Le joueur détecte les Interactable devant lui (couche 3) et affiche
/// « E — Prompt ». Les sous-classes redéfinissent Interact().
/// </summary>
public partial class Interactable : Area2D
{
    [Export] public string Prompt { get; set; } = "Examiner";
    [Export] public Vector2 Size { get; set; } = new(16, 20);
    [Export] public Vector2 Offset { get; set; } = new(0, -8);

    public override void _Ready()
    {
        CollisionLayer = 4;
        CollisionMask = 0;
        Monitoring = false;
        Monitorable = true;
        var shape = new CollisionShape2D
        {
            Shape = new RectangleShape2D { Size = Size },
            Position = Offset,
        };
        AddChild(shape);
    }

    /// <summary>Appelé par le joueur. À redéfinir.</summary>
    public virtual void Interact(Node2D player) { }
}
