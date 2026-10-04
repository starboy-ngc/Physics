using Godot;

namespace VillageDeBrume;

/// <summary>
/// Intérieur d'une maison : sol en planches, mur du fond avec plinthe, bordure.
/// Les meubles sont des Prop placés dans la scène ; la sortie est un Door.
/// </summary>
public partial class Interior : Zone
{
    [Export] public Color FloorColor { get; set; } = new("c89a62");
    [Export] public Color WallColor { get; set; } = new("e6d5b8");

    private static readonly Color Outline = new("2a1f17");

    public override void _Draw()
    {
        // Sol : planches horizontales de 16 px, alternance de deux teintes
        int i = 0;
        for (float y = Bounds.Position.Y; y < Bounds.End.Y; y += 16f, i++)
        {
            Color c = i % 2 == 0 ? FloorColor : FloorColor.Darkened(0.06f);
            DrawRect(new Rect2(Bounds.Position.X, y, Bounds.Size.X, 16f), c);
            DrawRect(new Rect2(Bounds.Position.X, y, Bounds.Size.X, 1f), FloorColor.Darkened(0.25f));
            for (float x = Bounds.Position.X + (i % 2 == 0 ? 24f : 56f); x < Bounds.End.X; x += 64f)
                DrawRect(new Rect2(x, y + 2f, 1f, 12f), FloorColor.Darkened(0.2f));
        }
        // Mur du fond : papier peint rayé + plinthe
        var wall = new Rect2(Bounds.Position, new Vector2(Bounds.Size.X, WallTop));
        DrawRect(wall, WallColor);
        for (float sx = Bounds.Position.X; sx < Bounds.End.X; sx += 16f)
            DrawRect(new Rect2(sx, wall.Position.Y, 4f, WallTop - 6f), WallColor.Darkened(0.06f));
        DrawRect(new Rect2(wall.Position.X, wall.End.Y - 6f, wall.Size.X, 6f), WallColor.Darkened(0.35f));
        DrawRect(new Rect2(wall.Position.X, wall.End.Y - 6f, wall.Size.X, 1f), Outline);
        // Bordure de la pièce
        DrawRect(Bounds, Outline, false, 2f);
    }
}
