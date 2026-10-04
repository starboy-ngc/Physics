using Godot;
using System;

namespace VillageDeBrume;

/// <summary>
/// Personnage jouable : déplacement case par case (8 directions), interaction
/// avec la case devant lui (E), portes franchies en marchant dessus.
/// Bloqué pendant un dialogue ou une interface.
/// </summary>
public partial class Player : GridEntity
{
    public event Action<IGridInteractable?>? FocusChanged;

    public Camera2D Camera { get; private set; } = null!;
    public IGridInteractable? Focused { get; private set; }
    /// <summary>Immobilisé par une interface (boutique, dépôt...). Le dialogue a son propre verrou.</summary>
    public bool Locked { get; set; }

    public bool CanAct => !Locked && !DialogueManager.Instance.IsActive;

    public override void _Ready()
    {
        base._Ready();
        Camera = GetNode<Camera2D>("Camera2D");
    }

    public override void _Process(double delta)
    {
        if (!IsMoving && CanAct)
        {
            var d = new Vector2I(
                (Input.IsActionPressed("move_right") ? 1 : 0) - (Input.IsActionPressed("move_left") ? 1 : 0),
                (Input.IsActionPressed("move_down") ? 1 : 0) - (Input.IsActionPressed("move_up") ? 1 : 0));
            if (d != Vector2I.Zero)
                TryStep(d);
        }
        base._Process(delta);
        UpdateFocus();
        if (CanAct && !IsMoving && Focused != null && Input.IsActionJustPressed("interact"))
            Focused.Interact(this);
    }

    protected override void OnStepFinished()
    {
        if (Zone != null && Zone.Doors.TryGetValue(Tile, out var door))
            Game.Instance.RequestZoneChange(door.zone, door.spawn);
    }

    /// <summary>Case visée : celle devant le personnage.</summary>
    public Vector2I FacingTile => Tile + CharacterSprites.ToDelta(Facing);

    public void RefreshFocus() => FocusChanged?.Invoke(Focused);

    private void UpdateFocus()
    {
        IGridInteractable? best = null;
        if (Zone != null && !IsMoving)
        {
            var ahead = FacingTile;
            best = Zone.GetInteractable(ahead) ?? Zone.Map.GetOccupant(ahead) as IGridInteractable;
        }
        if (best != Focused)
        {
            Focused = best;
            FocusChanged?.Invoke(Focused);
        }
    }
}
