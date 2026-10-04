using Godot;
using System;

namespace VillageDeBrume;

/// <summary>
/// Personnage jouable : déplacement 4 directions sur le plan (x, z), direction
/// regardée, sonde d'interaction devant lui (E). Bloqué pendant un dialogue.
/// </summary>
public partial class Player : CharacterBody3D
{
    public event Action<Interactable?>? FocusChanged;

    private const float Speed = 5f;

    public CharacterVisual Visual { get; private set; } = null!;
    public bool IsMoving { get; private set; }
    public Interactable? Focused { get; private set; }

    private CharacterVisual.Facing _facing = CharacterVisual.Facing.Down;
    public CharacterVisual.Facing FacingDirection
    {
        get => _facing;
        set
        {
            _facing = value;
            if (Visual != null) Visual.FacingDirection = value;
            UpdateProbe();
        }
    }

    private Area3D _probe = null!;
    private CollisionShape3D _probeShape = null!;

    public override void _Ready()
    {
        Visual = GetNode<CharacterVisual>("Visual");
        Visual.FacingDirection = _facing;
        _probe = new Area3D { Name = "InteractionProbe", CollisionLayer = 0, CollisionMask = 4, Monitorable = false };
        _probeShape = new CollisionShape3D { Shape = new BoxShape3D() };
        _probe.AddChild(_probeShape);
        AddChild(_probe);
        UpdateProbe();
    }

    public override void _PhysicsProcess(double delta)
    {
        Vector2 input = Vector2.Zero;
        if (!DialogueManager.Instance.IsActive)
            input = new Vector2(Input.GetAxis("move_left", "move_right"), Input.GetAxis("move_up", "move_down"));
        // Déplacement strictement en 4 directions : si deux axes sont pressés,
        // on garde l'axe de la direction actuelle.
        if (input.X != 0f && input.Y != 0f)
        {
            if (_facing is CharacterVisual.Facing.Left or CharacterVisual.Facing.Right) input.Y = 0f;
            else input.X = 0f;
        }
        input = input.Normalized();

        Velocity = new Vector3(input.X, 0f, input.Y) * Speed;
        MoveAndSlide();
        GlobalPosition = new Vector3(GlobalPosition.X, 0f, GlobalPosition.Z);

        IsMoving = input != Vector2.Zero;
        if (IsMoving)
            FacingDirection = CharacterVisual.FacingFromInput(input, _facing);
        Visual.Animate((float)delta, IsMoving);
        UpdateFocus();
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (DialogueManager.Instance.IsActive)
            return;
        if (@event.IsActionPressed("interact") && Focused != null)
        {
            Focused.Interact(this);
            GetViewport().SetInputAsHandled();
        }
    }

    public void Face(CharacterVisual.Facing direction) => FacingDirection = direction;

    public void FaceTowards(Vector3 target) => FacingDirection = CharacterVisual.FacingTowards(GlobalPosition, target);

    /// <summary>Place la sonde d'interaction devant le personnage.</summary>
    private void UpdateProbe()
    {
        if (_probeShape == null)
            return;
        var box = (BoxShape3D)_probeShape.Shape;
        Vector3 dir = CharacterVisual.ToVector(_facing);
        bool alongZ = dir.Z != 0f;
        box.Size = alongZ ? new Vector3(0.75f, 1.5f, 1.5f) : new Vector3(1.5f, 1.5f, 0.75f);
        _probe.Position = dir * (alongZ ? 1.25f : 1.1f) + new Vector3(0, 0.75f, alongZ ? 0f : -0.4f);
    }

    private void UpdateFocus()
    {
        Interactable? best = null;
        float bestDist = float.PositiveInfinity;
        foreach (var area in _probe.GetOverlappingAreas())
        {
            if (area is not Interactable inter)
                continue;
            float d = GlobalPosition.DistanceSquaredTo(inter.GlobalPosition);
            if (d < bestDist) { bestDist = d; best = inter; }
        }
        if (best != Focused)
        {
            Focused = best;
            FocusChanged?.Invoke(Focused);
        }
    }
}
