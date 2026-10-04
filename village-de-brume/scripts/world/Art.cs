using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>Identifiants des tuiles de sol (atlas généré par Art).</summary>
public enum TileId
{
    Void, Grass, GrassB, GrassC, GrassDark, Path, Plaza, PlazaB, Water, WaterEdge, Flower,
    Floor, FloorB, WallTop, Wall, Rug, Mat, Shore, Sand, Count
}

/// <summary>
/// Tout le pixel art du jeu, généré en code (aucun asset externe) : atlas de
/// tuiles 16x16 et sprites de décor. Palette vive façon RPG portable.
/// </summary>
public static class Art
{
    public const int Tile = 16;

    public static readonly Color Outline = new("2b2a3a");
    private static readonly Dictionary<string, ImageTexture> Cache = new();
    private static ImageTexture? _atlas;

    // --- Atlas de tuiles ---------------------------------------------------------

    public static ImageTexture TileAtlas => _atlas ??= BuildAtlas();

    public static Rect2 TileRegion(TileId id) => new((int)id * Tile, 0, Tile, Tile);

    private static ImageTexture BuildAtlas()
    {
        var img = PixelArt.NewImage(Tile * (int)TileId.Count, Tile);
        var rng = new RandomNumberGenerator { Seed = 99 };
        for (int i = 0; i < (int)TileId.Count; i++)
            PixelArt.Blit(img, PaintTile((TileId)i, rng), i * Tile, 0);
        return ImageTexture.CreateFromImage(img);
    }

    private static Image PaintTile(TileId id, RandomNumberGenerator rng)
    {
        var t = PixelArt.NewImage(Tile, Tile);
        switch (id)
        {
            case TileId.Void:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("14192a"));
                break;
            case TileId.Grass:
            case TileId.GrassB:
            case TileId.GrassC:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("7ec850"));
                for (int i = 0; i < 5; i++)
                {
                    int x = rng.RandiRange(0, 14), y = rng.RandiRange(0, 14);
                    PixelArt.Put(t, x, y, new Color("5aa33c")); PixelArt.Put(t, x + 1, y + 1, new Color("5aa33c"));
                }
                for (int i = 0; i < 3; i++)
                    PixelArt.Put(t, rng.RandiRange(0, 15), rng.RandiRange(0, 15), new Color("9ad860"));
                break;
            case TileId.GrassDark:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("5fa83e"));
                for (int i = 0; i < 6; i++)
                    PixelArt.Put(t, rng.RandiRange(0, 15), rng.RandiRange(0, 15), new Color("4b8c30"));
                break;
            case TileId.Path:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("e9d9a3"));
                for (int i = 0; i < 4; i++)
                    PixelArt.Rect(t, rng.RandiRange(0, 14), rng.RandiRange(0, 14), 2, 1, new Color("d2bf84"));
                PixelArt.Put(t, rng.RandiRange(0, 15), rng.RandiRange(0, 15), new Color("f4e8bc"));
                break;
            case TileId.Plaza:
            case TileId.PlazaB:
                PixelArt.Rect(t, 0, 0, 16, 16, id == TileId.Plaza ? new Color("8e949c") : new Color("868c94"));
                PixelArt.Rect(t, 0, 0, 16, 1, new Color("656b74"));
                PixelArt.Rect(t, 0, 0, 1, 16, new Color("656b74"));
                PixelArt.Rect(t, 8, 8, 1, 8, new Color("656b74"));
                PixelArt.Rect(t, 0, 8, 16, 1, new Color("656b74"));
                PixelArt.Rect(t, 1, 1, 7, 1, new Color("a6acb4"));
                PixelArt.Rect(t, 9, 9, 6, 1, new Color("a6acb4"));
                if (rng.Randf() < 0.3f) PixelArt.Rect(t, rng.RandiRange(2, 12), rng.RandiRange(2, 12), 2, 1, new Color("6f8a52"));
                break;
            case TileId.Water:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("3f86c8"));
                PixelArt.Rect(t, 2, 4, 5, 1, new Color("7fbce8"));
                PixelArt.Rect(t, 9, 11, 4, 1, new Color("7fbce8"));
                PixelArt.Rect(t, 5, 13, 3, 1, new Color("2f6aa8"));
                break;
            case TileId.Shore:
                // Mer en haut, plage de sable sombre en bas (rivage au nord du village)
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("3f86c8"));
                PixelArt.Rect(t, 0, 8, 16, 2, new Color("cfe6f4"));
                PixelArt.Rect(t, 0, 10, 16, 6, new Color("b9ad8a"));
                PixelArt.Rect(t, 3, 12, 2, 1, new Color("9a8e6c"));
                PixelArt.Rect(t, 10, 14, 2, 1, new Color("9a8e6c"));
                break;
            case TileId.Sand:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("b9ad8a"));
                for (int i = 0; i < 4; i++)
                    PixelArt.Rect(t, rng.RandiRange(0, 14), rng.RandiRange(0, 14), 2, 1, new Color("9a8e6c"));
                break;
            case TileId.WaterEdge:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("58a8f0"));
                PixelArt.Rect(t, 0, 0, 16, 2, new Color("7ec850"));
                PixelArt.Rect(t, 0, 2, 16, 1, new Color("3f7f2e"));
                PixelArt.Rect(t, 0, 3, 16, 2, new Color("3d8ad8"));
                PixelArt.Rect(t, 3, 9, 4, 1, new Color("9ad0ff"));
                break;
            case TileId.Flower:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("7ec850"));
                foreach (var (fx, fy, c) in new[] { (3, 3, "f0e060"), (10, 6, "f08890"), (5, 11, "ffffff"), (12, 12, "f0e060") })
                {
                    PixelArt.Rect(t, fx, fy, 2, 2, new Color(c));
                    PixelArt.Put(t, fx, fy + 2, new Color("3f7f2e"));
                }
                break;
            case TileId.Floor:
            case TileId.FloorB:
                PixelArt.Rect(t, 0, 0, 16, 16, id == TileId.Floor ? new Color("c89a62") : new Color("c09258"));
                PixelArt.Rect(t, 0, 0, 16, 1, new Color("9a7040"));
                PixelArt.Rect(t, 0, 8, 16, 1, new Color("9a7040"));
                PixelArt.Put(t, id == TileId.Floor ? 5 : 11, 3, new Color("9a7040"));
                PixelArt.Put(t, id == TileId.Floor ? 12 : 3, 11, new Color("9a7040"));
                break;
            case TileId.WallTop:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("6a5a7a"));
                PixelArt.Rect(t, 0, 14, 16, 2, new Color("4a3e58"));
                break;
            case TileId.Wall:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("e6d5b8"));
                PixelArt.Rect(t, 0, 0, 16, 1, new Color("b8a888"));
                PixelArt.Rect(t, 0, 12, 16, 4, new Color("8a6a4a"));
                PixelArt.Rect(t, 0, 12, 16, 1, new Color("5a4030"));
                PixelArt.Rect(t, 4, 2, 1, 9, new Color("d6c4a4"));
                PixelArt.Rect(t, 11, 2, 1, 9, new Color("d6c4a4"));
                break;
            case TileId.Rug:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("b04848"));
                PixelArt.Stroke(t, 1, 1, 14, 14, new Color("e8c060"));
                PixelArt.Rect(t, 6, 6, 4, 4, new Color("d85858"));
                break;
            case TileId.Mat:
                PixelArt.Rect(t, 0, 0, 16, 16, new Color("c89a62"));
                PixelArt.Rect(t, 1, 3, 14, 10, new Color("6a4a2a"));
                PixelArt.Rect(t, 3, 5, 10, 6, new Color("8a6a3a"));
                break;
        }
        return t;
    }

    // --- Sprites de décor ---------------------------------------------------------

    public static ImageTexture Get(string key, System.Func<Image> painter)
    {
        if (Cache.TryGetValue(key, out var tex))
            return tex;
        tex = ImageTexture.CreateFromImage(painter());
        Cache[key] = tex;
        return tex;
    }

    /// <summary>Arbre rond, 32x40, tronc en bas au centre.</summary>
    public static ImageTexture Tree() => Get("tree", () =>
    {
        var img = PixelArt.NewImage(32, 40);
        PixelArt.Ellipse(img, 16, 37, 10, 3, new Color(0, 0, 0, 0.25f));
        PixelArt.Rect(img, 13, 24, 6, 14, new Color("8a5a2a"));
        PixelArt.Rect(img, 13, 24, 2, 14, new Color("6a4020"));
        PixelArt.Ellipse(img, 16, 16, 15, 14, new Color("2f7a2c"));
        PixelArt.Ellipse(img, 15, 14, 12, 11, new Color("3f9a3a"));
        PixelArt.Ellipse(img, 11, 10, 6, 5, new Color("66c352"));
        PixelArt.Ellipse(img, 21, 17, 4, 3, new Color("66c352"));
        PixelArt.Outline(img, new Color("1e3d1c"));
        return img;
    });

    public static ImageTexture Bush() => Get("bush", () =>
    {
        var img = PixelArt.NewImage(16, 14);
        PixelArt.Ellipse(img, 8, 8, 7, 5, new Color("3f9a3a"));
        PixelArt.Ellipse(img, 6, 6, 4, 3, new Color("66c352"));
        PixelArt.Outline(img, new Color("1e3d1c"));
        return img;
    });

    public static ImageTexture Rock() => Get("rock", () =>
    {
        var img = PixelArt.NewImage(16, 14);
        PixelArt.Ellipse(img, 8, 8, 7, 5, new Color("9a9a9a"));
        PixelArt.Ellipse(img, 6, 6, 4, 3, new Color("c0c0c0"));
        PixelArt.Outline(img, new Color("3a3a4a"));
        return img;
    });

    /// <summary>Puits 32x40.</summary>
    public static ImageTexture Well() => Get("well", () =>
    {
        var img = PixelArt.NewImage(32, 40);
        PixelArt.Ellipse(img, 16, 37, 13, 3, new Color(0, 0, 0, 0.25f));
        PixelArt.Rect(img, 4, 22, 24, 14, new Color("9a9a9a"));
        PixelArt.Rect(img, 4, 22, 24, 3, new Color("c0c0c0"));
        PixelArt.Rect(img, 8, 25, 16, 6, new Color("58a8f0"));
        PixelArt.Rect(img, 8, 25, 16, 1, new Color("3d8ad8"));
        PixelArt.Rect(img, 4, 33, 24, 3, new Color("6a6a6a"));
        PixelArt.Rect(img, 6, 8, 3, 16, new Color("8a5a2a"));
        PixelArt.Rect(img, 23, 8, 3, 16, new Color("8a5a2a"));
        for (int y = 0; y < 8; y++)
            PixelArt.Rect(img, 4 + (7 - y) * 12 / 7, y + 1, 24 - (7 - y) * 24 / 7, 1, y % 2 == 0 ? new Color("c8503c") : new Color("9a3a2c"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Façade de la base 64x56 (4x3 tuiles), porte en bas au centre.</summary>
    public static ImageTexture House() => Get("house", () =>
    {
        var img = PixelArt.NewImage(64, 56);
        // Toit
        // Toit de tourbe (herbe), bord en bois
        for (int y = 0; y < 22; y++)
        {
            int inset = (21 - y) * 6 / 21;
            PixelArt.Rect(img, inset, y, 64 - 2 * inset, 1, y % 4 == 0 ? new Color("5a9a3c") : new Color("6fae48"));
        }
        for (int i = 0; i < 14; i++)
            PixelArt.Put(img, 6 + (i * 37) % 52, 3 + (i * 11) % 17, new Color("4b8c30"));
        PixelArt.Rect(img, 0, 22, 64, 3, new Color("6a4020"));
        // Murs en planches
        PixelArt.Rect(img, 4, 25, 56, 31, new Color("b88a58"));
        for (int y = 29; y < 56; y += 6)
            PixelArt.Rect(img, 4, y, 56, 1, new Color("8a5a2a"));
        PixelArt.Rect(img, 4, 50, 56, 6, new Color("8a6a4a"));
        PixelArt.Rect(img, 4, 25, 2, 31, new Color("6a4020"));
        PixelArt.Rect(img, 58, 25, 2, 31, new Color("6a4020"));
        // Fenêtres
        foreach (int wx in new[] { 10, 44 })
        {
            PixelArt.Rect(img, wx, 31, 10, 9, new Color("78c8f0"));
            PixelArt.Rect(img, wx + 1, 32, 3, 3, new Color("ffffff"));
            PixelArt.Stroke(img, wx, 31, 10, 9, new Color("6a4020"));
            PixelArt.Rect(img, wx - 1, 40, 12, 2, new Color("8a5a2a"));
        }
        // Porte (tuile du milieu-gauche : x 24..40)
        PixelArt.Rect(img, 25, 34, 14, 22, new Color("6a4020"));
        PixelArt.Rect(img, 27, 36, 10, 8, new Color("8a5a2a"));
        PixelArt.Put(img, 36, 46, new Color("f0d060"));
        PixelArt.Stroke(img, 24, 33, 16, 23, new Color("3a2a1a"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Étal 48x56 : auvent rayé en haut, poteaux, comptoir en bas. Le marchand se place entre les deux.</summary>
    public static ImageTexture Stall(Color accent) => Get("stall" + accent.ToHtml(), () =>
    {
        var img = PixelArt.NewImage(48, 56);
        // Auvent rayé avec bord festonné
        for (int x = 0; x < 48; x++)
        {
            bool stripe = (x / 6) % 2 == 0;
            PixelArt.Rect(img, x, 0, 1, 12, stripe ? accent : new Color("f8f0e0"));
            int scallop = (x % 6 == 0 || x % 6 == 5) ? 0 : 2;
            PixelArt.Rect(img, x, 12, 1, scallop, stripe ? accent : new Color("f8f0e0"));
        }
        PixelArt.Rect(img, 0, 0, 48, 1, accent.Darkened(0.4f));
        // Poteaux
        PixelArt.Rect(img, 1, 12, 3, 44, new Color("8a5a2a"));
        PixelArt.Rect(img, 44, 12, 3, 44, new Color("8a5a2a"));
        PixelArt.Rect(img, 1, 12, 1, 44, new Color("6a4020"));
        PixelArt.Rect(img, 44, 12, 1, 44, new Color("6a4020"));
        // Comptoir
        PixelArt.Rect(img, 0, 40, 48, 16, new Color("a0703c"));
        PixelArt.Rect(img, 0, 40, 48, 3, new Color("c89a5a"));
        PixelArt.Rect(img, 0, 52, 48, 4, new Color("6a4020"));
        PixelArt.Rect(img, 0, 43, 48, 1, new Color("6a4020"));
        // Marchandises posées
        PixelArt.Rect(img, 8, 36, 8, 5, new Color("f0d060"));
        PixelArt.Rect(img, 20, 35, 8, 6, new Color("e86060"));
        PixelArt.Rect(img, 32, 36, 8, 5, new Color("78c0f0"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Tableau d'affichage 16x26.</summary>
    public static ImageTexture Board() => Get("board", () =>
    {
        var img = PixelArt.NewImage(16, 26);
        PixelArt.Rect(img, 2, 18, 2, 8, new Color("6a4020"));
        PixelArt.Rect(img, 12, 18, 2, 8, new Color("6a4020"));
        PixelArt.Rect(img, 0, 2, 16, 17, new Color("a0703c"));
        PixelArt.Rect(img, 0, 2, 16, 2, new Color("6a4020"));
        PixelArt.Rect(img, 3, 6, 5, 6, new Color("f8f0e0"));
        PixelArt.Rect(img, 9, 8, 4, 6, new Color("f0e0b0"));
        PixelArt.Rect(img, 4, 8, 3, 1, new Color("8a8a8a"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Portail 32x32 entre deux piliers.</summary>
    public static ImageTexture Gate() => Get("gate", () =>
    {
        var img = PixelArt.NewImage(32, 32);
        PixelArt.Rect(img, 0, 2, 6, 30, new Color("9a9a9a"));
        PixelArt.Rect(img, 26, 2, 6, 30, new Color("9a9a9a"));
        PixelArt.Rect(img, 0, 2, 6, 3, new Color("c0c0c0"));
        PixelArt.Rect(img, 26, 2, 6, 3, new Color("c0c0c0"));
        PixelArt.Rect(img, 6, 10, 20, 22, new Color("8a5a2a"));
        PixelArt.Rect(img, 15, 10, 2, 22, new Color("5a3a1a"));
        PixelArt.Rect(img, 6, 16, 20, 2, new Color("5a3a1a"));
        PixelArt.Rect(img, 6, 24, 20, 2, new Color("5a3a1a"));
        PixelArt.Rect(img, 0, 0, 32, 3, new Color("7a7a7a"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    public static ImageTexture Fence() => Get("fence", () =>
    {
        var img = PixelArt.NewImage(16, 16);
        PixelArt.Rect(img, 2, 4, 3, 12, new Color("c89a5a"));
        PixelArt.Rect(img, 11, 4, 3, 12, new Color("c89a5a"));
        PixelArt.Rect(img, 0, 7, 16, 2, new Color("a0703c"));
        PixelArt.Rect(img, 0, 12, 16, 2, new Color("a0703c"));
        PixelArt.Outline(img, new Color("5a3a1a"));
        return img;
    });

    public static ImageTexture Bed() => Get("bed", () =>
    {
        var img = PixelArt.NewImage(16, 26);
        PixelArt.Rect(img, 0, 0, 16, 26, new Color("8a5a2a"));
        PixelArt.Rect(img, 1, 2, 14, 6, new Color("f8f0e0"));
        PixelArt.Rect(img, 1, 9, 14, 15, new Color("c84848"));
        PixelArt.Rect(img, 1, 9, 14, 2, new Color("e86060"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    public static ImageTexture Chest() => Get("chest", () =>
    {
        var img = PixelArt.NewImage(16, 14);
        PixelArt.Rect(img, 1, 2, 14, 12, new Color("a0703c"));
        PixelArt.Rect(img, 1, 2, 14, 5, new Color("6a4020"));
        PixelArt.Rect(img, 7, 6, 2, 3, new Color("f0d060"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    public static ImageTexture Table() => Get("table", () =>
    {
        var img = PixelArt.NewImage(32, 18);
        PixelArt.Rect(img, 2, 10, 3, 8, new Color("6a4020"));
        PixelArt.Rect(img, 27, 10, 3, 8, new Color("6a4020"));
        PixelArt.Rect(img, 0, 2, 32, 9, new Color("c89a5a"));
        PixelArt.Rect(img, 0, 9, 32, 2, new Color("a0703c"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Tente de toile 32x32, ouverture devant.</summary>
    public static ImageTexture Tent(Color cloth) => Get("tent" + cloth.ToHtml(), () =>
    {
        var img = PixelArt.NewImage(32, 32);
        for (int y = 2; y < 28; y++)
        {
            int half = 2 + (y - 2) * 14 / 26;
            PixelArt.Rect(img, 16 - half, y, half * 2, 1, (y / 3) % 2 == 0 ? cloth : cloth.Darkened(0.12f));
        }
        PixelArt.Rect(img, 0, 28, 32, 3, cloth.Darkened(0.35f));
        PixelArt.Rect(img, 15, 0, 2, 4, new Color("6a4020"));
        // Ouverture sombre
        for (int y = 14; y < 29; y++)
        {
            int half = (y - 14) * 5 / 15 + 1;
            PixelArt.Rect(img, 16 - half, y, half * 2, 1, new Color("3a2a2a"));
        }
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Longue-vue sur trépied 16x28.</summary>
    public static ImageTexture Telescope() => Get("telescope", () =>
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

    /// <summary>Lanterne sur poteau 16x28.</summary>
    public static ImageTexture LanternPost() => Get("lantern", () =>
    {
        var img = PixelArt.NewImage(16, 28);
        PixelArt.Rect(img, 7, 10, 2, 18, new Color("6a4020"));
        PixelArt.Rect(img, 5, 2, 6, 9, new Color("4a4a52"));
        PixelArt.Rect(img, 6, 3, 4, 7, new Color("f8c040"));
        PixelArt.Rect(img, 7, 5, 2, 3, new Color("ffe890"));
        PixelArt.Rect(img, 4, 1, 8, 1, new Color("4a4a52"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    public static ImageTexture Crate() => Get("crate", () =>
    {
        var img = PixelArt.NewImage(16, 16);
        PixelArt.Rect(img, 1, 3, 14, 13, new Color("b08a4a"));
        PixelArt.Stroke(img, 1, 3, 14, 13, new Color("6a4020"));
        PixelArt.Rect(img, 1, 9, 14, 1, new Color("6a4020"));
        PixelArt.Rect(img, 8, 3, 1, 13, new Color("6a4020"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    public static ImageTexture Barrel() => Get("barrel", () =>
    {
        var img = PixelArt.NewImage(16, 18);
        PixelArt.Ellipse(img, 8, 9, 6, 8, new Color("a0703c"));
        PixelArt.Rect(img, 3, 5, 10, 1, new Color("4a4a52"));
        PixelArt.Rect(img, 3, 12, 10, 1, new Color("4a4a52"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    /// <summary>Palissade de rondins 16x20.</summary>
    public static ImageTexture Palisade() => Get("palisade", () =>
    {
        var img = PixelArt.NewImage(16, 20);
        for (int i = 0; i < 4; i++)
        {
            int x = i * 4;
            PixelArt.Rect(img, x, 2 + (i % 2), 4, 18, i % 2 == 0 ? new Color("8a5a2a") : new Color("9a6a3a"));
            PixelArt.Rect(img, x + 1, 0 + (i % 2), 2, 3, new Color("b08a4a"));
        }
        PixelArt.Rect(img, 0, 9, 16, 2, new Color("6a4020"));
        PixelArt.Outline(img, Outline);
        return img;
    });

    public static ImageTexture Reeds() => Get("reeds", () =>
    {
        var img = PixelArt.NewImage(16, 16);
        foreach (int x in new[] { 3, 7, 12 })
        {
            PixelArt.Rect(img, x, 4, 1, 12, new Color("4b8c30"));
            PixelArt.Rect(img, x - 1, 2, 3, 4, new Color("8a5a2a"));
        }
        return img;
    });
}
