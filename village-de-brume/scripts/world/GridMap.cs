using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Grille de la zone : sol (tuiles dessinées), cases bloquées (décor) et
/// occupants (personnages). Toute la logique de déplacement passe par ici :
/// pas de moteur physique, une case est libre ou non.
/// </summary>
public partial class GridMap : Node2D
{
    public int Width { get; private set; }
    public int Height { get; private set; }

    private TileId[,] _ground = new TileId[0, 0];
    private bool[,] _blocked = new bool[0, 0];
    private readonly Dictionary<Vector2I, Node> _occupants = new();

    public void Init(int width, int height)
    {
        Width = width;
        Height = height;
        _ground = new TileId[width, height];
        _blocked = new bool[width, height];
        _occupants.Clear();
        QueueRedraw();
    }

    public bool InBounds(Vector2I t) => t.X >= 0 && t.Y >= 0 && t.X < Width && t.Y < Height;

    public TileId GetGround(Vector2I t) => InBounds(t) ? _ground[t.X, t.Y] : TileId.Void;

    public void SetGround(Vector2I t, TileId id)
    {
        if (InBounds(t)) _ground[t.X, t.Y] = id;
    }

    public bool IsBlocked(Vector2I t) => !InBounds(t) || _blocked[t.X, t.Y];

    public void Block(Vector2I t, bool blocked = true)
    {
        if (InBounds(t)) _blocked[t.X, t.Y] = blocked;
    }

    public void BlockRect(Vector2I origin, Vector2I size, bool blocked = true)
    {
        for (int y = 0; y < size.Y; y++)
            for (int x = 0; x < size.X; x++)
                Block(origin + new Vector2I(x, y), blocked);
    }

    public Node? GetOccupant(Vector2I t) => _occupants.TryGetValue(t, out var n) ? n : null;

    public void SetOccupant(Vector2I t, Node? node)
    {
        if (node == null) _occupants.Remove(t);
        else _occupants[t] = node;
    }

    /// <summary>Case franchissable pour `who` : dans la carte, non bloquée, libre (ou occupée par lui-même).</summary>
    public bool IsWalkable(Vector2I t, Node? who = null)
    {
        if (IsBlocked(t)) return false;
        var occ = GetOccupant(t);
        return occ == null || occ == who;
    }

    public static Vector2 TileToWorld(Vector2I t) => new(t.X * Art.Tile + Art.Tile / 2f, t.Y * Art.Tile + Art.Tile);

    public static Vector2I WorldToTile(Vector2 p) => new(Mathf.FloorToInt(p.X / Art.Tile), Mathf.FloorToInt((p.Y - 1) / Art.Tile));

    /// <summary>Masque des voisins du même type (N=1, S=2, W=4, E=8) ; hors carte compte comme identique.</summary>
    private int NeighborMask(int x, int y)
    {
        var id = _ground[x, y];
        bool Same(int nx, int ny) => !InBounds(new Vector2I(nx, ny)) || _ground[nx, ny] == id || IsKin(id, _ground[nx, ny]);
        return (Same(x, y - 1) ? 1 : 0) | (Same(x, y + 1) ? 2 : 0) | (Same(x - 1, y) ? 4 : 0) | (Same(x + 1, y) ? 8 : 0);
    }

    /// <summary>Sols qui se raccordent sans bord entre eux (terre et sable, par exemple).</summary>
    private static bool IsKin(TileId a, TileId b) =>
        (a is TileId.Path or TileId.Sand) && (b is TileId.Path or TileId.Sand or TileId.Shore or TileId.Plaza);

    public override void _Draw()
    {
        for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
            {
                int variant = (x * 7 + y * 13 + x * y) % 97;
                var (tex, region) = Art.GroundCell(_ground[x, y], NeighborMask(x, y), variant);
                DrawTextureRectRegion(tex, new Rect2(x * Art.Tile, y * Art.Tile, Art.Tile, Art.Tile), region);
            }
    }
}
