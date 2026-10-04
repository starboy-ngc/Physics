using Godot;

namespace VillageDeBrume;

/// <summary>
/// Intérieur d'une maison en 2.5D : sol en planches, mur du fond en papier
/// peint, murs latéraux, muret devant (ouvert vers la caméra).
/// Les meubles sont des Prop placés dans la scène ; la sortie est un Door.
/// </summary>
public partial class Interior : Zone
{
    [Export] public Color FloorColor { get; set; } = new("c89a62");
    [Export] public Color WallColor { get; set; } = new("e6d5b8");

    private const float WallHeight = 2.5f;
    private const float WallDepth = 0.5f;

    protected override void BuildGround()
    {
        AddFloor(Bounds, 0f, Materials.Textured("planks" + FloorColor.ToHtml(), Bounds.Size, () => Materials.Planks(FloorColor), 2f), "Floor");

        float w = Bounds.Size.X, d = Bounds.Size.Y;
        float x0 = Bounds.Position.X, z0 = Bounds.Position.Y;
        var walls = new Node3D { Name = "Walls" };
        AddChild(walls);
        var paper = Materials.Textured("paper" + WallColor.ToHtml(), new Vector2(w, WallHeight), () => Materials.Wallpaper(WallColor), 1f);
        var plain = Materials.Flat(WallColor.Darkened(0.15f));
        var plinth = Materials.Flat(WallColor.Darkened(0.4f));

        // Mur du fond : occupe la bande WallTop (épaisseur), face visible côté caméra.
        float back = Mathf.Max(WallTop, WallDepth);
        Materials.Box(walls, new Vector3(w + 2 * WallDepth, WallHeight, back), new Vector3(x0 + w / 2f, WallHeight / 2f, z0 + back / 2f), paper, "BackWall");
        Materials.Box(walls, new Vector3(w, 0.35f, 0.06f), new Vector3(x0 + w / 2f, 0.175f, z0 + back + 0.03f), plinth, "Plinth");
        // Murs latéraux (hors de la zone jouable)
        Materials.Box(walls, new Vector3(WallDepth, WallHeight, d), new Vector3(x0 - WallDepth / 2f, WallHeight / 2f, z0 + d / 2f), plain, "LeftWall");
        Materials.Box(walls, new Vector3(WallDepth, WallHeight, d), new Vector3(x0 + w + WallDepth / 2f, WallHeight / 2f, z0 + d / 2f), plain, "RightWall");
        // Muret devant, bas pour laisser voir la pièce
        Materials.Box(walls, new Vector3(w + 2 * WallDepth, 0.6f, WallDepth), new Vector3(x0 + w / 2f, 0.3f, z0 + d + WallDepth / 2f), plain, "FrontWall");
    }
}
