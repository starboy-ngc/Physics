using Godot;

namespace VillageDeBrume;

/// <summary>
/// Génère en code la planche de sprites d'un personnage (aucun asset externe) :
/// 4 directions (lignes : bas, haut, gauche, droite) × 3 poses (colonnes :
/// repos, pas 1, pas 2). Dessin vectoriel simple (rectangles arrondis et
/// ellipses) rastérisé à Scale fois la grille de 16 px par unité monde.
/// </summary>
public static class CharacterSprites
{
    /// <summary>Pixels de texture par pixel « logique » (16 px logiques = 1 unité monde).</summary>
    public const int Scale = 4;
    /// <summary>Taille d'une cellule en pixels logiques ; les pieds sont à la ligne FeetRow.</summary>
    public const int Cell = 36;
    public const int FeetRow = 34;

    private static readonly Color Outline = new("23222a");

    public static ImageTexture Build(Color tunic, Color hair, Color skin, Color pants)
    {
        int cell = Cell * Scale;
        var img = Image.CreateEmpty(cell * 3, cell * 4, true, Image.Format.Rgba8);
        img.Fill(new Color(0, 0, 0, 0));
        for (int facing = 0; facing < 4; facing++)
            for (int pose = 0; pose < 3; pose++)
                DrawCharacter(img, pose * cell + cell / 2, facing * cell + FeetRow * Scale,
                    (CharacterVisual.Facing)facing, pose - 1, tunic, hair, skin, pants);
        img.GenerateMipmaps();
        return ImageTexture.CreateFromImage(img);
    }

    // --- Primitives (coordonnées logiques, flottantes) -----------------------

    private static void Put(Image img, int x, int y, Color c)
    {
        if (x >= 0 && y >= 0 && x < img.GetWidth() && y < img.GetHeight())
            img.SetPixel(x, y, c);
    }

    private static void Rect(Image img, int ox, int oy, float x, float y, float w, float h, Color c)
    {
        img.FillRect(new Rect2I(ox + Mathf.RoundToInt(x * Scale), oy + Mathf.RoundToInt(y * Scale),
            Mathf.RoundToInt(w * Scale), Mathf.RoundToInt(h * Scale)), c);
    }

    /// <summary>Rectangle à coins arrondis (rayon r en pixels logiques), avec contour.</summary>
    private static void RoundRect(Image img, int ox, int oy, float x, float y, float w, float h, float r, Color fill, Color? outline)
    {
        int x0 = Mathf.RoundToInt(x * Scale), y0 = Mathf.RoundToInt(y * Scale);
        int ww = Mathf.RoundToInt(w * Scale), hh = Mathf.RoundToInt(h * Scale);
        float rr = r * Scale;
        for (int py = 0; py < hh; py++)
            for (int px = 0; px < ww; px++)
            {
                float d = CornerDistance(px + 0.5f, py + 0.5f, ww, hh, rr);
                if (d > 0f) continue;
                bool edge = outline.HasValue && d > -Scale;
                Put(img, ox + x0 + px, oy + y0 + py, edge ? outline!.Value : fill);
            }
    }

    /// <summary>Distance signée au bord d'un rectangle arrondi (négatif = intérieur).</summary>
    private static float CornerDistance(float px, float py, float w, float h, float r)
    {
        float cx = Mathf.Clamp(px, r, w - r), cy = Mathf.Clamp(py, r, h - r);
        float dx = px - cx, dy = py - cy;
        return Mathf.Sqrt(dx * dx + dy * dy) - r;
    }

    private static void Ellipse(Image img, int ox, int oy, float cx, float cy, float rx, float ry, Color fill, Color? outline)
    {
        int x0 = Mathf.FloorToInt((cx - rx) * Scale), x1 = Mathf.CeilToInt((cx + rx) * Scale);
        int y0 = Mathf.FloorToInt((cy - ry) * Scale), y1 = Mathf.CeilToInt((cy + ry) * Scale);
        for (int py = y0; py <= y1; py++)
            for (int px = x0; px <= x1; px++)
            {
                float nx = (px + 0.5f - cx * Scale) / (rx * Scale), ny = (py + 0.5f - cy * Scale) / (ry * Scale);
                float d = nx * nx + ny * ny;
                if (d > 1f) continue;
                float inner = (rx * Scale - Scale) / (rx * Scale);
                bool edge = outline.HasValue && d > inner * inner;
                if (!edge && fill.A <= 0f) continue; // remplissage transparent = contour seul
                Put(img, ox + px, oy + py, edge ? outline!.Value : fill);
            }
    }

    /// <summary>Dessine un personnage dont les pieds sont en (ox, oy) pixels texture.
    /// Proportions adultes (environ 5 têtes), silhouette fine, détails discrets.</summary>
    private static void DrawCharacter(Image img, int ox, int oy, CharacterVisual.Facing facing, int step,
        Color tunic, Color hair, Color skin, Color pants)
    {
        float bob = step >= 0 ? -0.5f : 0f;
        bool side = facing is CharacterVisual.Facing.Left or CharacterVisual.Facing.Right;
        Color belt = tunic.Darkened(0.45f);
        Color boots = pants.Darkened(0.35f);

        // Jambes : fines, alternance pendant la marche ; bottes sombres
        float leftH = 10f - (step == 1 ? 2.5f : 0f);
        float rightH = 10f - (step == 0 ? 2.5f : 0f);
        float legW = side ? 3.2f : 3.4f;
        float lx = side ? -2.6f : -4.0f, rx = side ? -0.4f : 0.6f;
        RoundRect(img, ox, oy, lx, -10f, legW, leftH, 1.0f, pants, Outline);
        RoundRect(img, ox, oy, rx, -10f, legW, rightH, 1.0f, pants, Outline);
        Rect(img, ox, oy, lx + 0.6f, -10f + leftH - 2.2f, legW - 1.2f, 1.6f, boots);
        Rect(img, ox, oy, rx + 0.6f, -10f + rightH - 2.2f, legW - 1.2f, 1.6f, boots);

        // Buste : tunique longue légèrement évasée, ceinture
        float bw = side ? 7.5f : 10f;
        RoundRect(img, ox, oy, -bw / 2f, -21.5f + bob, bw, 12.5f, 2.2f, tunic, Outline);
        Rect(img, ox, oy, -bw / 2f + 0.8f, -14.5f + bob, bw - 1.6f, 1.2f, belt);
        if (side)
        {
            RoundRect(img, ox, oy, -1.6f, -19.5f + bob, 3.2f, 7.5f, 1.3f, tunic.Darkened(0.18f), Outline);
        }
        else
        {
            RoundRect(img, ox, oy, -bw / 2f - 2.2f, -20f + bob, 2.4f, 7.5f, 1.1f, tunic.Darkened(0.12f), Outline);
            RoundRect(img, ox, oy, bw / 2f - 0.2f, -20f + bob, 2.4f, 7.5f, 1.1f, tunic.Darkened(0.12f), Outline);
            Ellipse(img, ox, oy, -bw / 2f - 1f, -12.3f + bob, 1.1f, 1.2f, skin, Outline);
            Ellipse(img, ox, oy, bw / 2f + 1f, -12.3f + bob, 1.1f, 1.2f, skin, Outline);
        }

        // Cou et tête : ovale modéré (environ 1/5 de la hauteur)
        Rect(img, ox, oy, -1.2f, -23f + bob, 2.4f, 2f, skin.Darkened(0.12f));
        float hcx = 0f, hcy = -26.2f + bob;
        float hrx = side ? 3.6f : 4.0f, hry = 4.4f;
        Ellipse(img, ox, oy, hcx, hcy, hrx, hry, skin, Outline);
        switch (facing)
        {
            case CharacterVisual.Facing.Up:
                Ellipse(img, ox, oy, hcx, hcy - 0.4f, hrx - 0.3f, hry - 0.5f, hair, null);
                break;
            case CharacterVisual.Facing.Down:
                Ellipse(img, ox, oy, hcx, hcy - 2.2f, hrx - 0.2f, 2.3f, hair, null);
                Rect(img, ox, oy, -hrx + 0.3f, hcy - 2.2f, 1.2f, 2.6f, hair);
                Rect(img, ox, oy, hrx - 1.5f, hcy - 2.2f, 1.2f, 2.6f, hair);
                Rect(img, ox, oy, -1.9f, hcy + 0.4f, 1.0f, 1.2f, Outline);
                Rect(img, ox, oy, 0.9f, hcy + 0.4f, 1.0f, 1.2f, Outline);
                Rect(img, ox, oy, -1.0f, hcy + 2.6f, 2.0f, 0.6f, skin.Darkened(0.35f));
                break;
            case CharacterVisual.Facing.Left:
                Ellipse(img, ox, oy, hcx + 0.6f, hcy - 2.0f, hrx - 0.2f, 2.4f, hair, null);
                Rect(img, ox, oy, 0.6f, hcy - 1.8f, hrx - 0.4f, 3.4f, hair);
                Rect(img, ox, oy, -2.6f, hcy + 0.4f, 1.0f, 1.2f, Outline);
                break;
            case CharacterVisual.Facing.Right:
                Ellipse(img, ox, oy, hcx - 0.6f, hcy - 2.0f, hrx - 0.2f, 2.4f, hair, null);
                Rect(img, ox, oy, -hrx + 0.2f, hcy - 1.8f, hrx - 0.4f, 3.4f, hair);
                Rect(img, ox, oy, 1.6f, hcy + 0.4f, 1.0f, 1.2f, Outline);
                break;
        }
        // Contour de la tête repassé par-dessus les cheveux
        Ellipse(img, ox, oy, hcx, hcy, hrx, hry, new Color(0, 0, 0, 0), Outline);
    }
}
