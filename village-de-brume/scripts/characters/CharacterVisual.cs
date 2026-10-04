using Godot;

namespace VillageDeBrume;

/// <summary>
/// Dessin d'un personnage (joueur ou PNJ) : proportions « tête large » façon
/// RPG portable, contour sombre, 4 directions, marche en 2 poses.
/// Origine aux pieds. Les couleurs sont paramétrables par personnage.
/// </summary>
public partial class CharacterVisual : Node2D
{
    public enum Facing { Down, Up, Left, Right }

    [Export] public Color TunicColor { get; set; } = new("3a6ea5");
    [Export] public Color HairColor { get; set; } = new("5a3a22");
    [Export] public Color SkinColor { get; set; } = new("f1c9a5");
    [Export] public Color PantsColor { get; set; } = new("2a2a3a");

    private static readonly Color Outline = new("1e1e2e");
    private static readonly Color Shadow = new(0, 0, 0, 0.25f);
    private const float WalkAnimFps = 8f;

    private Facing _facing = Facing.Down;
    public Facing FacingDirection
    {
        get => _facing;
        set { _facing = value; QueueRedraw(); }
    }

    public bool IsMoving { get; private set; }
    private float _walkTime;

    public void Animate(float delta, bool moving)
    {
        IsMoving = moving;
        _walkTime = moving ? _walkTime + delta : 0f;
        QueueRedraw();
    }

    public override void _Draw()
    {
        int step = IsMoving ? (int)(_walkTime * WalkAnimFps) % 2 : -1;
        int bob = step >= 0 ? -1 : 0;

        // Ombre
        DrawRect(new Rect2(-7, -2, 14, 3), Shadow);

        // Jambes
        int leftH = 7 - (step == 1 ? 3 : 0);
        int rightH = 7 - (step == 0 ? 3 : 0);
        DrawRect(new Rect2(-5, -7, 4, leftH), PantsColor);
        DrawRect(new Rect2(1, -7, 4, rightH), PantsColor);
        DrawRect(new Rect2(-5, -7, 4, leftH), Outline, false, 1f);
        DrawRect(new Rect2(1, -7, 4, rightH), Outline, false, 1f);

        // Corps
        var body = new Rect2(-6, -15 + bob, 12, 9);
        DrawRect(body, TunicColor);
        DrawRect(body, Outline, false, 1f);
        // Bras
        if (_facing is Facing.Left or Facing.Right)
        {
            DrawRect(new Rect2(-2, -13 + bob, 4, 6), TunicColor.Darkened(0.2f));
        }
        else
        {
            DrawRect(new Rect2(-8, -13 + bob, 2, 6), SkinColor);
            DrawRect(new Rect2(6, -13 + bob, 2, 6), SkinColor);
        }

        // Tête
        var head = new Rect2(-7, -26 + bob, 14, 12);
        DrawRect(head, SkinColor);
        float hy = head.Position.Y;
        switch (_facing)
        {
            case Facing.Up:
                DrawRect(new Rect2(-7, hy, 14, 9), HairColor);
                break;
            case Facing.Down:
                DrawRect(new Rect2(-7, hy, 14, 4), HairColor);
                DrawRect(new Rect2(-7, hy + 4, 2, 3), HairColor);
                DrawRect(new Rect2(5, hy + 4, 2, 3), HairColor);
                DrawRect(new Rect2(-4, hy + 6, 2, 3), Outline);
                DrawRect(new Rect2(2, hy + 6, 2, 3), Outline);
                break;
            case Facing.Left:
                DrawRect(new Rect2(-7, hy, 14, 4), HairColor);
                DrawRect(new Rect2(-1, hy, 8, 8), HairColor);
                DrawRect(new Rect2(-5, hy + 6, 2, 3), Outline);
                break;
            case Facing.Right:
                DrawRect(new Rect2(-7, hy, 14, 4), HairColor);
                DrawRect(new Rect2(-7, hy, 8, 8), HairColor);
                DrawRect(new Rect2(3, hy + 6, 2, 3), Outline);
                break;
        }
        DrawRect(head, Outline, false, 1f);
    }

    public static Facing FacingFromVector(Vector2 v, Facing current)
    {
        if (v.Y > 0f) return Facing.Down;
        if (v.Y < 0f) return Facing.Up;
        if (v.X > 0f) return Facing.Right;
        if (v.X < 0f) return Facing.Left;
        return current;
    }

    public static Facing FacingFromString(string s) => s.ToLowerInvariant() switch
    {
        "up" => Facing.Up,
        "left" => Facing.Left,
        "right" => Facing.Right,
        _ => Facing.Down,
    };

    /// <summary>Direction pour regarder `target` depuis `from` (axe dominant).</summary>
    public static Facing FacingTowards(Vector2 from, Vector2 target)
    {
        Vector2 d = target - from;
        if (Mathf.Abs(d.X) > Mathf.Abs(d.Y))
            return d.X > 0f ? Facing.Right : Facing.Left;
        return d.Y > 0f ? Facing.Down : Facing.Up;
    }
}
