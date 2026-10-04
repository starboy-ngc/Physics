using Godot;

namespace VillageDeBrume;

/// <summary>
/// Rectangle de sol décoratif (chemin de terre, place pavée). Pas de collision.
/// Dessiné en tuiles 16x16 avec une bordure légèrement plus sombre.
/// </summary>
public partial class GroundPatch : Node2D
{
    private Rect2 _rect = new(0, 0, 32, 32);
    [Export] public Rect2 Rect { get => _rect; set { _rect = value; QueueRedraw(); } }
    private int _kind;
    [Export(PropertyHint.Enum, "dirt,stone")] public int Kind { get => _kind; set { _kind = value; QueueRedraw(); } }

    private const float Tile = 16f;
    private static readonly Color Dirt = new("d2b07a");
    private static readonly Color DirtB = new("c9a66e");
    private static readonly Color DirtEdge = new("a88752");
    private static readonly Color Stone = new("b9b6aa");
    private static readonly Color StoneB = new("adaa9e");
    private static readonly Color StoneEdge = new("8a877c");

    public override void _Draw()
    {
        Color baseA = Kind == 0 ? Dirt : Stone;
        Color baseB = Kind == 0 ? DirtB : StoneB;
        Color edge = Kind == 0 ? DirtEdge : StoneEdge;
        int cols = Mathf.CeilToInt(Rect.Size.X / Tile);
        int rows = Mathf.CeilToInt(Rect.Size.Y / Tile);
        for (int ty = 0; ty < rows; ty++)
        {
            for (int tx = 0; tx < cols; tx++)
            {
                Vector2 origin = Rect.Position + new Vector2(tx, ty) * Tile;
                Rect2 tile = new Rect2(origin, new Vector2(Tile, Tile)).Intersection(Rect);
                DrawRect(tile, (tx + ty) % 2 == 0 ? baseA : baseB);
                if (Kind == 1)
                {
                    DrawRect(new Rect2(tile.Position, new Vector2(tile.Size.X, 1)), edge);
                    DrawRect(new Rect2(tile.Position, new Vector2(1, tile.Size.Y)), edge);
                }
                else
                {
                    int k = (tx * 5 + ty * 3) % 4;
                    DrawRect(new Rect2(origin + new Vector2(3 + k * 2, 5 + k), new Vector2(2, 2)), edge);
                }
            }
        }
        DrawRect(Rect, edge, false, 1f);
    }
}
