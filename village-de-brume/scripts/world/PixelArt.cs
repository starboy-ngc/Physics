using Godot;

namespace VillageDeBrume;

/// <summary>Primitives de dessin pixel sur une Image (coordonnées entières, écriture protégée).</summary>
public static class PixelArt
{
    public static Image NewImage(int w, int h)
    {
        var img = Image.CreateEmpty(w, h, false, Image.Format.Rgba8);
        img.Fill(new Color(0, 0, 0, 0));
        return img;
    }

    public static void Put(Image img, int x, int y, Color c)
    {
        if (x >= 0 && y >= 0 && x < img.GetWidth() && y < img.GetHeight())
            img.SetPixel(x, y, c);
    }

    public static void Rect(Image img, int x, int y, int w, int h, Color c)
    {
        for (int py = y; py < y + h; py++)
            for (int px = x; px < x + w; px++)
                Put(img, px, py, c);
    }

    public static void Stroke(Image img, int x, int y, int w, int h, Color c)
    {
        Rect(img, x, y, w, 1, c); Rect(img, x, y + h - 1, w, 1, c);
        Rect(img, x, y, 1, h, c); Rect(img, x + w - 1, y, 1, h, c);
    }

    /// <summary>Ellipse pleine de centre (cx, cy) et rayons (rx, ry), en pixels.</summary>
    public static void Ellipse(Image img, float cx, float cy, float rx, float ry, Color c)
    {
        for (int py = Mathf.FloorToInt(cy - ry); py <= Mathf.CeilToInt(cy + ry); py++)
            for (int px = Mathf.FloorToInt(cx - rx); px <= Mathf.CeilToInt(cx + rx); px++)
            {
                float nx = (px + 0.5f - cx) / rx, ny = (py + 0.5f - cy) / ry;
                if (nx * nx + ny * ny <= 1f)
                    Put(img, px, py, c);
            }
    }

    /// <summary>Contour d'ellipse (épaisseur 1 px).</summary>
    public static void EllipseOutline(Image img, float cx, float cy, float rx, float ry, Color c)
    {
        for (int py = Mathf.FloorToInt(cy - ry) - 1; py <= Mathf.CeilToInt(cy + ry) + 1; py++)
            for (int px = Mathf.FloorToInt(cx - rx) - 1; px <= Mathf.CeilToInt(cx + rx) + 1; px++)
            {
                float nx = (px + 0.5f - cx) / rx, ny = (py + 0.5f - cy) / ry;
                float d = nx * nx + ny * ny;
                float ix = (px + 0.5f - cx) / (rx - 1f), iy = (py + 0.5f - cy) / (ry - 1f);
                if (d <= 1f && ix * ix + iy * iy > 1f)
                    Put(img, px, py, c);
            }
    }

    /// <summary>Contour 1 px autour des pixels opaques (pour les sprites).</summary>
    public static void Outline(Image img, Color c)
    {
        int w = img.GetWidth(), h = img.GetHeight();
        var src = (Image)img.Duplicate();
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                if (src.GetPixel(x, y).A > 0f) continue;
                bool near = false;
                foreach (var (dx, dy) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                {
                    int nx = x + dx, ny = y + dy;
                    if (nx >= 0 && ny >= 0 && nx < w && ny < h && src.GetPixel(nx, ny).A > 0f) { near = true; break; }
                }
                if (near) img.SetPixel(x, y, c);
            }
    }

    public static void Blit(Image dst, Image src, int x, int y)
    {
        dst.BlitRect(src, new Rect2I(0, 0, src.GetWidth(), src.GetHeight()), new Vector2I(x, y));
    }

    public static void BlendBlit(Image dst, Image src, int x, int y)
    {
        dst.BlendRect(src, new Rect2I(0, 0, src.GetWidth(), src.GetHeight()), new Vector2I(x, y));
    }
}
