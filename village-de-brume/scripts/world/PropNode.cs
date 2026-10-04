using Godot;

namespace VillageDeBrume;

/// <summary>
/// Élément de décor posé sur la grille : une texture ou un assemblage de
/// cellules d'atlas, une emprise bloquée (en tuiles) et une origine au bas de
/// l'emprise pour le tri en Y.
/// </summary>
public partial class PropNode : Node2D
{
    public Vector2I Origin { get; private set; }
    public Vector2I Footprint { get; private set; }

    /// <summary>Décor fait d'une seule texture, centrée sur l'emprise, bas aligné.</summary>
    public static PropNode FromTexture(string name, Texture2D texture, Vector2I origin, Vector2I footprint)
    {
        var node = Create(name, origin, footprint);
        node.AddChild(new Sprite2D
        {
            Texture = texture,
            Centered = false,
            Offset = new Vector2(-texture.GetWidth() / 2f, -texture.GetHeight()),
            TextureFilter = TextureFilterEnum.Nearest,
        });
        return node;
    }

    /// <summary>Décor composé de cellules d'atlas ; les cellules du bas s'alignent sur le bas de l'emprise.</summary>
    public static PropNode FromComposite(string name, Art.Composite composite, Vector2I origin, Vector2I footprint)
    {
        var node = Create(name, origin, footprint);
        float left = -footprint.X * Art.Tile / 2f;
        float top = -composite.Height * Art.Tile;
        foreach (var (cell, dx, dy, flip) in composite.Cells)
        {
            node.AddChild(new Sprite2D
            {
                Texture = cell.Atlas,
                RegionEnabled = true,
                RegionRect = cell.Region,
                Centered = false,
                Offset = new Vector2(left + dx * Art.Tile, top + dy * Art.Tile),
                FlipH = flip,
                TextureFilter = TextureFilterEnum.Nearest,
            });
        }
        return node;
    }

    private static PropNode Create(string name, Vector2I origin, Vector2I footprint)
    {
        return new PropNode
        {
            Name = name,
            Origin = origin,
            Footprint = footprint,
            Position = new Vector2(origin.X * Art.Tile + footprint.X * Art.Tile / 2f, (origin.Y + footprint.Y) * Art.Tile),
        };
    }
}
