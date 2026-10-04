using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>Identifiants des tuiles de sol.</summary>
public enum TileId
{
    Void, Grass, GrassDark, Path, Plaza, Water, Shore, Sand, Flower,
    Floor, WallTop, Wall, Rug, Mat, Count
}

/// <summary>Une cellule de sprite : un atlas et un index de tuile 16x16.</summary>
public readonly record struct Cell(Texture2D Atlas, int Index)
{
    public Rect2 Region => new((Index % Art.Columns) * Art.Tile, (Index / Art.Columns) * Art.Tile, Art.Tile, Art.Tile);
}

/// <summary>
/// Accès aux graphismes : packs Kenney (CC0, voir assets/kenney/README.md)
/// complétés par quelques tuiles générées en code (eau, rivage, tapis...).
/// Les sols « terre » et « pavés » se raccordent automatiquement avec
/// l'herbe (blocs 3x3 du pack).
/// </summary>
public static class Art
{
    public const int Tile = 16;
    public const int Columns = 12;
    public static readonly Color Outline = new("2b2a3a");

    public static Texture2D Town { get; } = GD.Load<Texture2D>("res://assets/kenney/tiny-town/tilemap_packed.png");
    public static Texture2D Dungeon { get; } = GD.Load<Texture2D>("res://assets/kenney/tiny-dungeon/tilemap_packed.png");
    public static Texture2D Farm { get; } = GD.Load<Texture2D>("res://assets/kenney/tiny-farm/tilemap_packed.png");

    private static ImageTexture? _generated;
    private static readonly Dictionary<string, ImageTexture> Cache = new();

    // --- Tuiles Tiny Town utiles ---------------------------------------------------
    // Terre (bloc 3x3 avec bord d'herbe) et variantes de centre ; pavés (bloc 3x3).
    private static readonly int[] DirtBlob = { 12, 13, 14, 24, 25, 26, 36, 37, 38 };
    private static readonly int[] DirtCenters = { 25, 25, 25, 39, 40, 41, 42 };
    private static readonly int[] StoneBlob = { 96, 97, 98, 108, 109, 110, 120, 121, 122 };

    /// <summary>Tuiles générées (eau, rivage, tapis, paillasson, vide), 16 px chacune, en ligne.</summary>
    private enum Gen { Void, Water, Shore, Rug, Mat, Count }

    private static ImageTexture Generated => _generated ??= BuildGenerated();

    private static ImageTexture BuildGenerated()
    {
        var img = PixelArt.NewImage(Tile * (int)Gen.Count, Tile);
        var rng = new RandomNumberGenerator { Seed = 99 };
        for (int i = 0; i < (int)Gen.Count; i++)
        {
            var t = PixelArt.NewImage(Tile, Tile);
            switch ((Gen)i)
            {
                case Gen.Void:
                    PixelArt.Rect(t, 0, 0, 16, 16, new Color("14192a"));
                    break;
                case Gen.Water:
                    PixelArt.Rect(t, 0, 0, 16, 16, new Color("4a9ad6"));
                    PixelArt.Rect(t, 2, 4, 5, 1, new Color("8fcbf0"));
                    PixelArt.Rect(t, 9, 11, 4, 1, new Color("8fcbf0"));
                    PixelArt.Rect(t, 5, 13, 3, 1, new Color("3b7fb8"));
                    break;
                case Gen.Shore:
                    PixelArt.Rect(t, 0, 0, 16, 16, new Color("4a9ad6"));
                    PixelArt.Rect(t, 0, 9, 16, 2, new Color("d9eefb"));
                    PixelArt.Rect(t, 0, 11, 16, 5, new Color("e0b575"));
                    PixelArt.Rect(t, 4, 13, 2, 1, new Color("c99a5c"));
                    PixelArt.Rect(t, 11, 14, 2, 1, new Color("c99a5c"));
                    break;
                case Gen.Rug:
                    PixelArt.Rect(t, 0, 0, 16, 16, new Color("b04848"));
                    PixelArt.Stroke(t, 1, 1, 14, 14, new Color("e8c060"));
                    PixelArt.Rect(t, 6, 6, 4, 4, new Color("d85858"));
                    break;
                case Gen.Mat:
                    PixelArt.Rect(t, 0, 0, 16, 16, new Color("e0b575"));
                    PixelArt.Rect(t, 1, 3, 14, 10, new Color("6a4a2a"));
                    PixelArt.Rect(t, 3, 5, 10, 6, new Color("8a6a3a"));
                    break;
            }
            PixelArt.Blit(img, t, i * Tile, 0);
        }
        return ImageTexture.CreateFromImage(img);
    }

    private static (Texture2D tex, Rect2 region) GenCell(Gen g) => (Generated, new Rect2((int)g * Tile, 0, Tile, Tile));

    /// <summary>Masque de voisinage pour l'auto-raccord : N=1, S=2, W=4, E=8 (voisin du même sol).</summary>
    public static int BlobIndex(int mask)
    {
        bool n = (mask & 1) != 0, s = (mask & 2) != 0, w = (mask & 4) != 0, e = (mask & 8) != 0;
        int row = !n ? 0 : !s ? 2 : 1;
        int col = !w ? 0 : !e ? 2 : 1;
        return row * 3 + col;
    }

    /// <summary>Texture et région à dessiner pour une case de sol.</summary>
    public static (Texture2D tex, Rect2 region) GroundCell(TileId id, int mask, int variant)
    {
        switch (id)
        {
            case TileId.Grass:
                return (Town, new Cell(Town, variant % 10 < 8 ? 0 : variant % 10 < 9 ? 1 : 2).Region);
            case TileId.GrassDark:
                return (Town, new Cell(Town, 43).Region);
            case TileId.Flower:
                return (Town, new Cell(Town, 2).Region);
            case TileId.Path:
            {
                int blob = BlobIndex(mask);
                int idx = blob == 4 ? DirtCenters[variant % DirtCenters.Length] : DirtBlob[blob];
                return (Town, new Cell(Town, idx).Region);
            }
            case TileId.Sand:
                return (Town, new Cell(Town, DirtCenters[variant % DirtCenters.Length]).Region);
            case TileId.Plaza:
                return (Town, new Cell(Town, StoneBlob[BlobIndex(mask)]).Region);
            case TileId.Floor:
                return (Dungeon, new Cell(Dungeon, variant % 4 == 0 ? 49 : 48).Region);
            case TileId.WallTop:
                return (Dungeon, new Cell(Dungeon, 40).Region);
            case TileId.Wall:
                return (Dungeon, new Cell(Dungeon, 57).Region);
            case TileId.Water: return GenCell(Gen.Water);
            case TileId.Shore: return GenCell(Gen.Shore);
            case TileId.Rug: return GenCell(Gen.Rug);
            case TileId.Mat: return GenCell(Gen.Mat);
            default: return GenCell(Gen.Void);
        }
    }

    // --- Sprites composés de cellules (décor) ---------------------------------------

    /// <summary>Un décor : des cellules placées sur une grille locale (dx, dy en tuiles), origine en haut à gauche.</summary>
    public record Composite(List<(Cell cell, int dx, int dy, bool flip)> Cells, int Width, int Height)
    {
        public static Composite Single(Texture2D atlas, int index) => new(new() { (new Cell(atlas, index), 0, 0, false) }, 1, 1);

        public static Composite Column(Texture2D atlas, params int[] topToBottom)
        {
            var list = new List<(Cell, int, int, bool)>();
            for (int i = 0; i < topToBottom.Length; i++)
                list.Add((new Cell(atlas, topToBottom[i]), 0, i, false));
            return new Composite(list, 1, topToBottom.Length);
        }

        public static Composite Grid(Texture2D atlas, int width, params int[] rowMajor)
        {
            var list = new List<(Cell, int, int, bool)>();
            for (int i = 0; i < rowMajor.Length; i++)
                if (rowMajor[i] >= 0)
                    list.Add((new Cell(atlas, rowMajor[i]), i % width, i / width, false));
            return new Composite(list, width, (rowMajor.Length + width - 1) / width);
        }
    }

    public static Composite Tree() => Composite.Column(Town, 4, 16);
    public static Composite AutumnTree() => Composite.Column(Town, 3, 15);
    public static Composite Pine() => Composite.Column(Farm, 3, 15);
    public static Composite Bush() => Composite.Single(Town, 5);
    public static Composite Mushrooms() => Composite.Single(Town, 29);
    public static Composite Rock() => Composite.Single(Farm, 89);
    public static Composite Fence() => Composite.Single(Town, 81);
    public static Composite Palisade() => Composite.Single(Town, 59);
    public static Composite Sign() => Composite.Single(Town, 83);
    public static Composite Crate() => Composite.Single(Town, 103);
    public static Composite Barrel() => Composite.Single(Town, 106);
    public static Composite Well() => Composite.Single(Farm, 73);
    public static Composite Torch() => Composite.Single(Dungeon, 125);
    public static Composite Chest() => Composite.Single(Dungeon, 89);
    public static Composite Table() => Composite.Single(Dungeon, 72);
    public static Composite Stool() => Composite.Single(Dungeon, 73);
    public static Composite HayBale() => Composite.Single(Farm, 96);
    public static Composite Reeds() => Composite.Single(Farm, 80);

    /// <summary>Maison du joueur : toit d'ardoise et murs de bois de Tiny Town (4 x 3), porte sur la 3e colonne.</summary>
    public static Composite House() => Composite.Grid(Town, 4,
        48, 49, 49, 50,
        60, 61, 61, 62,
        72, 73, 85, 75);

    /// <summary>Grange à toit vert de Tiny Farm (3 x 5), réserve de Cassegrain.</summary>
    public static Composite Barn() => Composite.Grid(Farm, 3,
        93, 94, 95,
        105, 106, 107,
        117, 118, 119,
        102, 103, 104,
        126, 127, 128);

    /// <summary>Auvent d'étal : une rangée de toit (orange ou gris) de Tiny Town.</summary>
    public static Composite Awning(bool grey) => grey ? Composite.Grid(Town, 3, 48, 49, 50) : Composite.Grid(Town, 3, 52, 53, 54);

    /// <summary>Comptoir d'étal : barrière horizontale sur 3 cases.</summary>
    public static Composite CounterRow() => Composite.Grid(Town, 3, 80, 81, 82);

    public static Composite Tent() => Composite.Grid(Town, 2, 63, 63);

    // --- Textures générées encore nécessaires ------------------------------------------

    public static ImageTexture Get(string key, System.Func<Image> painter)
    {
        if (Cache.TryGetValue(key, out var tex)) return tex;
        tex = ImageTexture.CreateFromImage(painter());
        Cache[key] = tex;
        return tex;
    }

    /// <summary>Tente de toile 32x32 (pas d'équivalent dans les packs), style contour sombre.</summary>
    public static ImageTexture TentTexture(Color cloth) => Get("tent" + cloth.ToHtml(), () =>
    {
        var img = PixelArt.NewImage(32, 32);
        for (int y = 2; y < 28; y++)
        {
            int half = 2 + (y - 2) * 14 / 26;
            PixelArt.Rect(img, 16 - half, y, half * 2, 1, (y / 3) % 2 == 0 ? cloth : cloth.Darkened(0.12f));
        }
        PixelArt.Rect(img, 0, 28, 32, 3, cloth.Darkened(0.35f));
        PixelArt.Rect(img, 15, 0, 2, 4, new Color("6a4020"));
        for (int y = 14; y < 29; y++)
        {
            int half = (y - 14) * 5 / 15 + 1;
            PixelArt.Rect(img, 16 - half, y, half * 2, 1, new Color("3a2a2a"));
        }
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Longue-vue sur trépied 16x28.</summary>
    public static ImageTexture TelescopeTexture() => Get("telescope", () =>
    {
        var img = PixelArt.NewImage(16, 28);
        PixelArt.Rect(img, 7, 14, 2, 14, new Color("6a4020"));
        PixelArt.Rect(img, 3, 18, 2, 10, new Color("6a4020"));
        PixelArt.Rect(img, 11, 18, 2, 10, new Color("6a4020"));
        for (int i = 0; i < 10; i++)
            PixelArt.Rect(img, 2 + i, 12 - i, 3, 3, i < 4 ? new Color("c8a050") : new Color("b08a3a"));
        PixelArt.Rect(img, 12, 2, 3, 3, new Color("e8d070"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    public static ImageTexture BedTexture() => Get("bed", () =>
    {
        var img = PixelArt.NewImage(16, 26);
        PixelArt.Rect(img, 0, 0, 16, 26, new Color("8a5a2a"));
        PixelArt.Rect(img, 1, 2, 14, 6, new Color("f8f0e0"));
        PixelArt.Rect(img, 1, 9, 14, 15, new Color("c84848"));
        PixelArt.Rect(img, 1, 9, 14, 2, new Color("e86060"));
        PixelArt.Outline(img, Outline);
        return img;
    });
}
