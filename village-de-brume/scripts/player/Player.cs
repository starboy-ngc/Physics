using Godot;
using System;

namespace VillageDeBrume;

/// <summary>
/// Personnage jouable : déplacement 4 directions, direction regardée,
/// sonde d'interaction devant lui (E). Bloqué pendant un dialogue.
/// </summary>
public partial class Player : CharacterBody2D
{
    public event Action<Interactable?>? FocusChanged;

    private const float Speed = 80f;

    public Camera2D Camera { get; private set; } = null!;
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

    private Area2D _probe = null!;
    private CollisionShape2D _probeShape = null!;

    public override void _Ready()
    {
        Camera = GetNode<Camera2D>("Camera2D");
        Visual = GetNode<CharacterVisual>("Visual");
        Visual.FacingDirection = _facing;

        _probe = new Area2D
        {
            Name = "InteractionProbe",
            CollisionLayer = 0,
            CollisionMask = 4,
            Monitorable = false,
        };
        _probeShape = new CollisionShape2D { Shape = new RectangleShape2D() };
        _probe.AddChild(_probeShape);
        AddChild(_probe);
        UpdateProbe();
    }

    public override void _PhysicsProcess(double delta)
    {
        Vector2 input = Vector2.Zero;
        if (!DialogueManager.Instance.IsActive)
        {
            input = new Vector2(
                Input.GetAxis("move_left", "move_right"),
                Input.GetAxis("move_up", "move_down"));
        }
        // Déplacement strictement en 4 directions : si deux axes sont pressés,
        // on garde l'axe de la direction actuelle.
        if (input.X != 0f && input.Y != 0f)
        {
            if (_facing is CharacterVisual.Facing.Left or CharacterVisual.Facing.Right)
                input.Y = 0f;
            else
                input.X = 0f;
        }
        input = input.Normalized();

        Velocity = input * Speed;
        MoveAndSlide();

        IsMoving = input != Vector2.Zero;
        if (IsMoving)
            FacingDirection = CharacterVisual.FacingFromVector(input, _facing);
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

    public void FaceTowards(Vector2 target) =>
        FacingDirection = CharacterVisual.FacingTowards(GlobalPosition, target);

    /// <summary>Place la sonde d'interaction devant le personnage.</summary>
    private void UpdateProbe()
    {
        if (_probeShape == null)
            return;
        var rs = (RectangleShape2D)_probeShape.Shape;
        switch (_facing)
        {
            case CharacterVisual.Facing.Down:
                rs.Size = new Vector2(12, 24);
                _probe.Position = new Vector2(0, 12);
                break;
            case CharacterVisual.Facing.Up:
                rs.Size = new Vector2(12, 24);
                _probe.Position = new Vector2(0, -22);
                break;
            case CharacterVisual.Facing.Left:
                rs.Size = new Vector2(24, 12);
                _probe.Position = new Vector2(-18, -8);
                break;
            case CharacterVisual.Facing.Right:
                rs.Size = new Vector2(24, 12);
                _probe.Position = new Vector2(18, -8);
                break;
        }
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
            if (d < bestDist)
            {
                bestDist = d;
                best = inter;
            }
        }
        if (best != Focused)
        {
            Focused = best;
            FocusChanged?.Invoke(Focused);
        }
    }
}
