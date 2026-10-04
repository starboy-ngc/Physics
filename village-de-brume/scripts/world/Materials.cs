using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Matériaux et textures procédurales partagés (aucun asset externe).
/// Les textures sont de petites images pixel (16 px = 1 unité monde) répétées.
/// </summary>
public static class Materials
{
    private static readonly Dictionary<Color, StandardMaterial3D> ColorCache = new();
    private static readonly Dictionary<string, StandardMaterial3D> TextureCache = new();

    /// <summary>Matériau uni, mat.</summary>
    public static StandardMaterial3D Flat(Color color)
    {
        if (ColorCache.TryGetValue(color, out var m))
            return m;
        m = new StandardMaterial3D { AlbedoColor = color, Roughness = 1f, Metallic = 0f };
        if (color.A < 1f)
            m.Transparency = BaseMaterial3D.TransparencyEnum.Alpha;
        ColorCache[color] = m;
        return m;
    }

    /// <summary>Matériau texturé (filtre « nearest », répétition par unité monde).</summary>
    public static StandardMaterial3D Textured(string key, Vector2 worldSize, System.Func<Image> painter, float tileUnits)
    {
        string cacheKey = $"{key}:{worldSize}";
        if (TextureCache.TryGetValue(cacheKey, out var m))
            return m;
        var image = painter();
        // Agrandissement (voisin le plus proche) puis mipmaps : motif net, bords adoucis.
        image.Resize(image.GetWidth() * 4, image.GetHeight() * 4, Image.Interpolation.Nearest);
        image.GenerateMipmaps();
        m = new StandardMaterial3D
        {
            AlbedoTexture = ImageTexture.CreateFromImage(image),
            TextureFilter = BaseMaterial3D.TextureFilterEnum.LinearWithMipmapsAnisotropic,
            TextureRepeat = true,
            Roughness = 1f,
            Metallic = 0f,
            Uv1Scale = new Vector3(worldSize.X / tileUnits, worldSize.Y / tileUnits, 1f),
        };
        TextureCache[cacheKey] = m;
        return m;
    }

    // --- Peintres de textures (32x32 px = 2x2 tuiles de 16 px) ----------------

    public static Image Grass()
    {
        var img = Image.CreateEmpty(32, 32, true, Image.Format.Rgba8);
        var a = new Color("6fae4e"); var b = new Color("68a548");
        var mark = new Color("5a9440"); var light = new Color("86c25f");
        for (int ty = 0; ty < 2; ty++)
            for (int tx = 0; tx < 2; tx++)
            {
                int ox = tx * 16, oy = ty * 16;
                img.FillRect(new Rect2I(ox, oy, 16, 16), (tx + ty) % 2 == 0 ? a : b);
                int k = (tx * 7 + ty * 13) % 5;
                img.FillRect(new Rect2I(ox + 2 + k, oy + 4, 2, 2), mark);
                img.FillRect(new Rect2I(ox + 9 - k, oy + 11, 2, 2), mark);
                if ((tx + ty) == 0)
                    img.FillRect(new Rect2I(ox + 6, oy + 7, 3, 2), light);
            }
        return img;
    }

    public static Image Dirt()
    {
        var img = Image.CreateEmpty(32, 32, true, Image.Format.Rgba8);
        var a = new Color("d2b07a"); var b = new Color("c9a66e"); var edge = new Color("a88752");
        for (int ty = 0; ty < 2; ty++)
            for (int tx = 0; tx < 2; tx++)
            {
                int ox = tx * 16, oy = ty * 16;
                img.FillRect(new Rect2I(ox, oy, 16, 16), (tx + ty) % 2 == 0 ? a : b);
                int k = (tx * 5 + ty * 3) % 4;
                img.FillRect(new Rect2I(ox + 3 + k * 2, oy + 5 + k, 2, 2), edge);
            }
        return img;
    }

    public static Image Stone()
    {
        var img = Image.CreateEmpty(32, 32, true, Image.Format.Rgba8);
        var a = new Color("b9b6aa"); var b = new Color("adaa9e"); var edge = new Color("8a877c");
        for (int ty = 0; ty < 2; ty++)
            for (int tx = 0; tx < 2; tx++)
            {
                int ox = tx * 16, oy = ty * 16;
                img.FillRect(new Rect2I(ox, oy, 16, 16), (tx + ty) % 2 == 0 ? a : b);
                img.FillRect(new Rect2I(ox, oy, 16, 1), edge);
                img.FillRect(new Rect2I(ox, oy, 1, 16), edge);
            }
        return img;
    }

    public static Image Planks(Color floor)
    {
        var img = Image.CreateEmpty(64, 32, true, Image.Format.Rgba8);
        for (int row = 0; row < 2; row++)
        {
            int oy = row * 16;
            img.FillRect(new Rect2I(0, oy, 64, 16), row == 0 ? floor : floor.Darkened(0.06f));
            img.FillRect(new Rect2I(0, oy, 64, 1), floor.Darkened(0.25f));
            int joint = row == 0 ? 24 : 56;
            img.FillRect(new Rect2I(joint, oy + 2, 1, 12), floor.Darkened(0.2f));
        }
        return img;
    }

    public static Image Wallpaper(Color wall)
    {
        var img = Image.CreateEmpty(16, 16, true, Image.Format.Rgba8);
        img.FillRect(new Rect2I(0, 0, 16, 16), wall);
        img.FillRect(new Rect2I(0, 0, 4, 16), wall.Darkened(0.06f));
        return img;
    }

    public static Image RoofTiles(Color roof)
    {
        var img = Image.CreateEmpty(16, 16, true, Image.Format.Rgba8);
        img.FillRect(new Rect2I(0, 0, 16, 16), roof);
        img.FillRect(new Rect2I(0, 0, 16, 1), roof.Darkened(0.3f));
        img.FillRect(new Rect2I(0, 8, 16, 1), roof.Darkened(0.3f));
        img.FillRect(new Rect2I(8, 0, 1, 8), roof.Darkened(0.2f));
        img.FillRect(new Rect2I(0, 8, 1, 8), roof.Darkened(0.2f));
        return img;
    }

    // --- Aides de construction ---------------------------------------------

    public static MeshInstance3D Box(Node parent, Vector3 size, Vector3 center, Material mat, string name = "Box")
    {
        var mi = new MeshInstance3D
        {
            Name = name,
            Mesh = new BoxMesh { Size = size },
            MaterialOverride = mat,
            Position = center,
        };
        parent.AddChild(mi);
        return mi;
    }

    public static MeshInstance3D Cylinder(Node parent, float radius, float height, Vector3 center, Material mat, string name = "Cylinder")
    {
        var mi = new MeshInstance3D
        {
            Name = name,
            Mesh = new CylinderMesh { TopRadius = radius, BottomRadius = radius, Height = height, RadialSegments = 12 },
            MaterialOverride = mat,
            Position = center,
        };
        parent.AddChild(mi);
        return mi;
    }

    public static MeshInstance3D Sphere(Node parent, float radius, Vector3 center, Material mat, string name = "Sphere")
    {
        var mi = new MeshInstance3D
        {
            Name = name,
            Mesh = new SphereMesh { Radius = radius, Height = radius * 2f, RadialSegments = 12, Rings = 6 },
            MaterialOverride = mat,
            Position = center,
        };
        parent.AddChild(mi);
        return mi;
    }

    public static CollisionShape3D BoxCollider(Node parent, Vector3 size, Vector3 center)
    {
        var cs = new CollisionShape3D { Shape = new BoxShape3D { Size = size }, Position = center };
        parent.AddChild(cs);
        return cs;
    }
}
