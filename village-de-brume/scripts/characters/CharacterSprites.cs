using Godot;

namespace VillageDeBrume;

/// <summary>
/// Planche de sprites d'un personnage, générée en code : 4 directions (lignes :
/// bas, haut, gauche, droite) × 3 poses (colonnes : repos, pas 1, pas 2),
/// cellules de 24x24 px, pieds à la ligne FeetRow. Dessinée en haute résolution
/// (formes arrondies) puis réduite en pixel art avec contour.
/// Fournit aussi le portrait 32x32 pour les boîtes de dialogue.
/// </summary>
public static class CharacterSprites
{
    public const int Cell = 24;
    public const int FeetRow = 22;
    private const int Hi = 6;            // facteur de dessin haute résolution
    private const float Unit = Cell * Hi / 36f; // 36 px logiques -> une cellule

    private static readonly Color Outline = Art.Outline;

    public static ImageTexture Build(Color tunic, Color hair, Color skin, Color pants)
    {
        int cellHi = Cell * Hi;
        var hi = PixelArt.NewImage(cellHi * 3, cellHi * 4);
        for (int facing = 0; facing < 4; facing++)
            for (int pose = 0; pose < 3; pose++)
                DrawCharacter(hi, pose * cellHi + cellHi / 2, facing * cellHi + Mathf.RoundToInt((FeetRow + 1) * Hi),
                    (Facing)facing, pose - 1, tunic, hair, skin, pants);
        return ImageTexture.CreateFromImage(Pixelize(hi, Cell * 3, Cell * 4));
    }

    /// <summary>Portrait buste 32x32 sur fond uni.</summary>
    public static ImageTexture BuildPortrait(Color tunic, Color hair, Color skin, Color background)
    {
        int size = 32 * Hi;
        var hi = PixelArt.NewImage(size, size);
        PixelArt.Rect(hi, 0, 0, size, size, background);
        float u = size / 32f;
        // Épaules
        PixelArt.Ellipse(hi, 16 * u, 36 * u, 14 * u, 10 * u, tunic);
        PixelArt.EllipseOutline(hi, 16 * u, 36 * u, 14 * u, 10 * u, Outline);
        // Cou et tête
        PixelArt.Rect(hi, Mathf.RoundToInt(13.5f * u), Mathf.RoundToInt(22 * u), Mathf.RoundToInt(5 * u), Mathf.RoundToInt(5 * u), skin.Darkened(0.1f));
        PixelArt.Ellipse(hi, 16 * u, 15 * u, 9.5f * u, 10.5f * u, skin);
        PixelArt.Ellipse(hi, 16 * u, 9.5f * u, 9.2f * u, 5.5f * u, hair);
        PixelArt.Rect(hi, Mathf.RoundToInt(6.5f * u), Mathf.RoundToInt(9 * u), Mathf.RoundToInt(2.5f * u), Mathf.RoundToInt(7 * u), hair);
        PixelArt.Rect(hi, Mathf.RoundToInt(23 * u), Mathf.RoundToInt(9 * u), Mathf.RoundToInt(2.5f * u), Mathf.RoundToInt(7 * u), hair);
        PixelArt.EllipseOutline(hi, 16 * u, 15 * u, 9.5f * u, 10.5f * u, Outline);
        // Yeux et bouche
        PixelArt.Ellipse(hi, 12.5f * u, 16.5f * u, 1.3f * u, 1.8f * u, Outline);
        PixelArt.Ellipse(hi, 19.5f * u, 16.5f * u, 1.3f * u, 1.8f * u, Outline);
        PixelArt.Put(hi, Mathf.RoundToInt(12 * u), Mathf.RoundToInt(16 * u), Colors.White);
        PixelArt.Rect(hi, Mathf.RoundToInt(14.5f * u), Mathf.RoundToInt(21 * u), Mathf.RoundToInt(3 * u), Mathf.RoundToInt(0.8f * u), skin.Darkened(0.4f));
        var lo = (Image)hi.Duplicate();
        lo.Resize(32, 32, Image.Interpolation.Bilinear);
        return ImageTexture.CreateFromImage(lo);
    }

    /// <summary>Réduction + seuil d'alpha + contour : rendu pixel art net.</summary>
    private static Image Pixelize(Image hi, int w, int h)
    {
        var lo = (Image)hi.Duplicate();
        lo.Resize(w, h, Image.Interpolation.Bilinear);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                var c = lo.GetPixel(x, y);
                lo.SetPixel(x, y, c.A < 0.45f ? new Color(0, 0, 0, 0) : new Color(c.R, c.G, c.B, 1f));
            }
        // Contour cellule par cellule (évite les fuites entre cellules)
        for (int cy = 0; cy < 4; cy++)
            for (int cx = 0; cx < 3; cx++)
            {
                var cell = lo.GetRegion(new Rect2I(cx * Cell, cy * Cell, Cell, Cell));
                PixelArt.Outline(cell, Outline);
                lo.BlitRect(cell, new Rect2I(0, 0, Cell, Cell), new Vector2I(cx * Cell, cy * Cell));
            }
        return lo;
    }

    public enum Facing { Down, Up, Left, Right }

    // --- Dessin haute résolution (coordonnées logiques : 36 px = 1 cellule) ----

    private static void R(Image img, int ox, int oy, float x, float y, float w, float h, Color c) =>
        PixelArt.Rect(img, ox + Mathf.RoundToInt(x * Unit), oy + Mathf.RoundToInt(y * Unit), Mathf.RoundToInt(w * Unit), Mathf.RoundToInt(h * Unit), c);

    private static void E(Image img, int ox, int oy, float cx, float cy, float rx, float ry, Color c) =>
        PixelArt.Ellipse(img, ox + cx * Unit, oy + cy * Unit, rx * Unit, ry * Unit, c);

    private static void DrawCharacter(Image img, int ox, int oy, Facing facing, int step,
        Color tunic, Color hair, Color skin, Color pants)
    {
        float bob = step >= 0 ? -0.5f : 0f;
        bool side = facing is Facing.Left or Facing.Right;
        Color belt = tunic.Darkened(0.45f);
        Color boots = pants.Darkened(0.35f);

        // Jambes
        float leftH = 10f - (step == 1 ? 2.5f : 0f);
        float rightH = 10f - (step == 0 ? 2.5f : 0f);
        float legW = side ? 3.4f : 3.6f;
        float lx = side ? -2.8f : -4.2f, rx = side ? -0.6f : 0.6f;
        R(img, ox, oy, lx, -10f, legW, leftH, pants);
        R(img, ox, oy, rx, -10f, legW, rightH, pants);
        R(img, ox, oy, lx, -10f + leftH - 2.2f, legW, 2.2f, boots);
        R(img, ox, oy, rx, -10f + rightH - 2.2f, legW, 2.2f, boots);

        // Buste
        float bw = side ? 8f : 11f;
        E(img, ox, oy, 0f, -16f + bob, bw / 2f, 6.5f, tunic);
        R(img, ox, oy, -bw / 2f, -16f + bob, bw, 6.5f, tunic);
        R(img, ox, oy, -bw / 2f + 0.8f, -14.5f + bob, bw - 1.6f, 1.2f, belt);
        if (side)
            R(img, ox, oy, -1.6f, -19.5f + bob, 3.2f, 7.5f, tunic.Darkened(0.18f));
        else
        {
            R(img, ox, oy, -bw / 2f - 2.2f, -20f + bob, 2.4f, 7.5f, tunic.Darkened(0.12f));
            R(img, ox, oy, bw / 2f - 0.2f, -20f + bob, 2.4f, 7.5f, tunic.Darkened(0.12f));
            E(img, ox, oy, -bw / 2f - 1f, -12.3f + bob, 1.2f, 1.3f, skin);
            E(img, ox, oy, bw / 2f + 1f, -12.3f + bob, 1.2f, 1.3f, skin);
        }

        // Cou et tête
        R(img, ox, oy, -1.2f, -23f + bob, 2.4f, 2f, skin.Darkened(0.12f));
        float hcy = -26.5f + bob;
        float hrx = side ? 4.2f : 4.8f, hry = 4.8f;
        E(img, ox, oy, 0f, hcy, hrx, hry, skin);
        switch (facing)
        {
            case Facing.Up:
                E(img, ox, oy, 0f, hcy - 0.4f, hrx - 0.2f, hry - 0.4f, hair);
                break;
            case Facing.Down:
                E(img, ox, oy, 0f, hcy - 2.4f, hrx - 0.1f, 2.6f, hair);
                R(img, ox, oy, -hrx + 0.2f, hcy - 2.4f, 1.4f, 3f, hair);
                R(img, ox, oy, hrx - 1.6f, hcy - 2.4f, 1.4f, 3f, hair);
                R(img, ox, oy, -2.2f, hcy + 0.4f, 1.2f, 1.6f, Outline);
                R(img, ox, oy, 1.0f, hcy + 0.4f, 1.2f, 1.6f, Outline);
                break;
            case Facing.Left:
                E(img, ox, oy, 0.6f, hcy - 2.2f, hrx - 0.1f, 2.6f, hair);
                R(img, ox, oy, 0.4f, hcy - 2f, hrx - 0.3f, 3.6f, hair);
                R(img, ox, oy, -3.0f, hcy + 0.4f, 1.2f, 1.6f, Outline);
                break;
            case Facing.Right:
                E(img, ox, oy, -0.6f, hcy - 2.2f, hrx - 0.1f, 2.6f, hair);
                R(img, ox, oy, -hrx + 0.1f, hcy - 2f, hrx - 0.3f, 3.6f, hair);
                R(img, ox, oy, 1.8f, hcy + 0.4f, 1.2f, 1.6f, Outline);
                break;
        }
    }

    // --- Aides de direction (grille : haut = -y, bas = +y) ----------------------

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
