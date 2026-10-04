using Godot;

namespace VillageDeBrume;

/// <summary>Directions sur la grille et aides associées (haut = -y, bas = +y).</summary>
public static class CharacterSprites
{
    public enum Facing { Down, Up, Left, Right }

    public static Facing FacingFromDelta(Vector2I d, Facing current)
    {
        if (d.Y > 0) return Facing.Down;
        if (d.Y < 0) return Facing.Up;
        if (d.X > 0) return Facing.Right;
        if (d.X < 0) return Facing.Left;
        return current;
    }

    public static Facing FacingFromString(string s) => s.ToLowerInvariant() switch
    {
        "up" => Facing.Up,
        "left" => Facing.Left,
        "right" => Facing.Right,
        _ => Facing.Down,
    };

    public static Vector2I ToDelta(Facing f) => f switch
    {
        Facing.Up => new Vector2I(0, -1),
        Facing.Down => new Vector2I(0, 1),
        Facing.Left => new Vector2I(-1, 0),
        _ => new Vector2I(1, 0),
    };
}
