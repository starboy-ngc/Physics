using Godot;

namespace VillageDeBrume;

/// <summary>
/// Élément de décor posé sur la grille : une texture, une emprise bloquée
/// (en tuiles) et une origine au bas de l'emprise pour le tri en Y.
/// </summary>
public partial class PropNode : Node2D
{
    public Vector2I Origin { get; private set; }
    public Vector2I Footprint { get; private set; }

    public static PropNode Create(string name, Texture2D texture, Vector2I origin, Vector2I footprint, bool blocks = true, Vector2I? drawOffset = null)
    {
        var node = new PropNode { Name = name, Origin = origin, Footprint = footprint };
        float w = footprint.X * Art.Tile;
        node.Position = new Vector2(origin.X * Art.Tile + w / 2f, (origin.Y + footprint.Y) * Art.Tile);
        var sprite = new Sprite2D
        {
            Texture = texture,
            Centered = false,
            Offset = new Vector2(-texture.GetWidth() / 2f, -texture.GetHeight()) + (drawOffset ?? Vector2I.Zero),
            TextureFilter = TextureFilterEnum.Nearest,
        };
        node.AddChild(sprite);
        node.Set("blocks", blocks);
        return node;
    }
}
