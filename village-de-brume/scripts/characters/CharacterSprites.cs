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
    public const int Cell = 32;
    public const int FeetRow = 30;

    private static readonly Color Outline = new("2a2a3a");

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
                img.SetPixel(ox + x0 + px, oy + y0 + py, edge ? outline!.Value : fill);
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
                img.SetPixel(ox + px, oy + py, edge ? outline!.Value : fill);
            }
    }

    /// <summary>Dessine un personnage dont les pieds sont en (ox, oy) pixels texture.</summary>
    private static void DrawCharacter(Image img, int ox, int oy, CharacterVisual.Facing facing, int step,
        Color tunic, Color hair, Color skin, Color pants)
    {
        float bob = step >= 0 ? -0.5f : 0f;
        bool side = facing is CharacterVisual.Facing.Left or CharacterVisual.Facing.Right;

        // Jambes (deux petits rectangles arrondis, alternance pendant la marche)
        float leftH = 7f - (step == 1 ? 2.5f : 0f);
        float rightH = 7f - (step == 0 ? 2.5f : 0f);
        RoundRect(img, ox, oy, -5f, -7f, 4.2f, leftH, 1.2f, pants, Outline);
        RoundRect(img, ox, oy, 0.8f, -7f, 4.2f, rightH, 1.2f, pants, Outline);

        // Corps : tunique arrondie, légèrement plus large aux épaules
        RoundRect(img, ox, oy, -6.5f, -15.5f + bob, 13f, 10f, 3f, tunic, Outline);
        if (side)
            RoundRect(img, ox, oy, -2f, -13.5f + bob, 4f, 6.5f, 1.5f, tunic.Darkened(0.2f), null);
        else
        {
            Ellipse(img, ox, oy, -7.2f, -10f + bob, 1.4f, 3.2f, skin, Outline);
            Ellipse(img, ox, oy, 7.2f, -10f + bob, 1.4f, 3.2f, skin, Outline);
        }

        // Tête : ellipse large, cheveux en calotte
        float hcx = 0f, hcy = -21f + bob;
        Ellipse(img, ox, oy, hcx, hcy, 7.5f, 6.5f, skin, Outline);
        switch (facing)
        {
            case CharacterVisual.Facing.Up:
                Ellipse(img, ox, oy, hcx, hcy - 0.5f, 7.0f, 6.0f, hair, null);
                break;
            case CharacterVisual.Facing.Down:
                Ellipse(img, ox, oy, hcx, hcy - 2.5f, 7.0f, 3.6f, hair, null);
                Rect(img, ox, oy, -7f, hcy - 2.5f, 1.8f, 4f, hair);
                Rect(img, ox, oy, 5.2f, hcy - 2.5f, 1.8f, 4f, hair);
                Ellipse(img, ox, oy, -2.8f, hcy + 1.2f, 1.0f, 1.5f, Outline, null);
                Ellipse(img, ox, oy, 2.8f, hcy + 1.2f, 1.0f, 1.5f, Outline, null);
                break;
            case CharacterVisual.Facing.Left:
                Ellipse(img, ox, oy, hcx + 1f, hcy - 2.3f, 6.8f, 3.8f, hair, null);
                Rect(img, ox, oy, 1f, hcy - 2f, 6f, 5f, hair);
                Ellipse(img, ox, oy, -4f, hcy + 1.2f, 1.0f, 1.5f, Outline, null);
                break;
            case CharacterVisual.Facing.Right:
                Ellipse(img, ox, oy, hcx - 1f, hcy - 2.3f, 6.8f, 3.8f, hair, null);
                Rect(img, ox, oy, -7f, hcy - 2f, 6f, 5f, hair);
                Ellipse(img, ox, oy, 4f, hcy + 1.2f, 1.0f, 1.5f, Outline, null);
                break;
        }
        // Contour de la tête repassé par-dessus les cheveux
        Ellipse(img, ox, oy, hcx, hcy, 7.5f, 6.5f, new Color(0, 0, 0, 0), Outline);
    }
}
