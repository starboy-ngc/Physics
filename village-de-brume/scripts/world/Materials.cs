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
        // Herbe sombre et désaturée, variations douces, quelques brins plus foncés.
        var a = new Color("5a7345"); var b = new Color("566e42"); var c = new Color("5e7849");
        var blade = new Color("46593a"); var dry = new Color("6e7d4e");
        var rng = new RandomNumberGenerator { Seed = 7 };
        for (int y = 0; y < 32; y++)
            for (int x = 0; x < 32; x++)
            {
                float n = rng.Randf();
                img.SetPixel(x, y, n < 0.5f ? a : n < 0.8f ? b : c);
            }
        for (int i = 0; i < 14; i++)
        {
            int x = rng.RandiRange(0, 31), y = rng.RandiRange(0, 30);
            img.SetPixel(x, y, blade); img.SetPixel(x, y + 1, blade);
        }
        for (int i = 0; i < 5; i++)
            img.SetPixel(rng.RandiRange(0, 31), rng.RandiRange(0, 31), dry);
        return img;
    }

    public static Image Dirt()
    {
        var img = Image.CreateEmpty(32, 32, true, Image.Format.Rgba8);
        // Terre battue : brun-gris, quelques cailloux.
        var a = new Color("847358"); var b = new Color("7d6d53"); var c = new Color("8a7a60");
        var pebble = new Color("9a8f7a"); var dark = new Color("6b5d46");
        var rng = new RandomNumberGenerator { Seed = 11 };
        for (int y = 0; y < 32; y++)
            for (int x = 0; x < 32; x++)
            {
                float n = rng.Randf();
                img.SetPixel(x, y, n < 0.45f ? a : n < 0.8f ? b : c);
            }
        for (int i = 0; i < 6; i++)
        {
            int x = rng.RandiRange(0, 30), y = rng.RandiRange(0, 30);
            img.FillRect(new Rect2I(x, y, 2, 2), pebble);
            img.SetPixel(x, y + 1, dark);
        }
        return img;
    }

    public static Image Stone()
    {
        var img = Image.CreateEmpty(32, 32, true, Image.Format.Rgba8);
        // Pavés gris irréguliers, joints sombres.
        var tones = new[] { new Color("7f7d75"), new Color("868379"), new Color("77756d"), new Color("8c8a80") };
        var joint = new Color("57564f");
        var rng = new RandomNumberGenerator { Seed = 5 };
        for (int ty = 0; ty < 2; ty++)
            for (int tx = 0; tx < 2; tx++)
            {
                int ox = tx * 16, oy = ty * 16;
                // deux pavés par tuile, décalés une rangée sur deux
                int split = ty == 0 ? 7 : 9;
                img.FillRect(new Rect2I(ox, oy, 16, 16), tones[rng.RandiRange(0, 3)]);
                img.FillRect(new Rect2I(ox + split, oy, 16 - split, 16), tones[rng.RandiRange(0, 3)]);
                img.FillRect(new Rect2I(ox, oy, 16, 1), joint);
                img.FillRect(new Rect2I(ox, oy, 1, 16), joint);
                img.FillRect(new Rect2I(ox + split, oy, 1, 16), joint);
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
        // Ardoises : rangées fines, légère variation de teinte.
        var rng = new RandomNumberGenerator { Seed = 3 };
        for (int y = 0; y < 16; y++)
            for (int x = 0; x < 16; x++)
                img.SetPixel(x, y, rng.Randf() < 0.5f ? roof : roof.Lightened(0.06f));
        for (int y = 0; y < 16; y += 4)
        {
            img.FillRect(new Rect2I(0, y, 16, 1), roof.Darkened(0.35f));
            int off = (y / 4) % 2 == 0 ? 0 : 4;
            for (int x = off; x < 16; x += 8)
                img.FillRect(new Rect2I(x, y, 1, 4), roof.Darkened(0.25f));
        }
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
