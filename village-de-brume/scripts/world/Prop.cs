using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Mobilier et petits objets en volumes simples (lit, table, chaise, coffre,
/// four, comptoir, étagère, tonneau, panneau). Origine au milieu de la face
/// avant, au sol (comme les bâtiments) : l'objet s'étend vers -Z.
/// </summary>
public partial class Prop : StaticBody3D
{
    [Export(PropertyHint.Enum, "bed,table,chair,chest,oven,counter,shelf,barrel,sign,stall,board,gate")]
    public string Kind { get; set; } = "table";
    /// <summary>Texte du panneau (Kind = "sign").</summary>
    [Export] public string SignText { get; set; } = "";
    /// <summary>Si renseigné, l'objet est examinable (E) et affiche ce message.</summary>
    [Export(PropertyHint.MultilineText)] public string ExamineText { get; set; } = "";
    [Export] public string ExaminePrompt { get; set; } = "Examiner";
    /// <summary>Couleur d'accent (toile de l'étal...).</summary>
    [Export] public Color Accent { get; set; } = new("7a4a46");

    /// <summary>Emprise (largeur x, profondeur z) et hauteur par type.</summary>
    private static readonly Dictionary<string, Vector3> Sizes = new()
    {
        ["bed"] = new(2f, 0.7f, 3f), ["table"] = new(2.5f, 0.9f, 1.5f), ["chair"] = new(0.9f, 1.1f, 1f),
        ["chest"] = new(1.5f, 0.8f, 1.1f), ["oven"] = new(2.5f, 2.0f, 2.5f), ["counter"] = new(4f, 1.0f, 1.25f),
        ["shelf"] = new(2f, 2.4f, 1f), ["barrel"] = new(1f, 1.25f, 1f), ["sign"] = new(1.5f, 1.6f, 0.4f),
        ["stall"] = new(4f, 2.6f, 1.6f), ["board"] = new(3f, 2.2f, 0.4f), ["gate"] = new(4f, 3f, 0.6f),
    };

    private static readonly Color Wood = new("6e4e32");
    private static readonly Color WoodDark = new("4a3324");
    private static readonly Color WoodLight = new("8f7352");

    public Vector3 GetSize() => Sizes.TryGetValue(Kind, out var s) ? s : new Vector3(1, 1, 1);

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        Vector3 s = GetSize();
        float w = s.X, h = s.Y, d = s.Z;
        var c = new Vector3(0, h / 2f, -d / 2f); // centre du volume

        if (Kind == "sign")
            Materials.BoxCollider(this, new Vector3(0.4f, 1f, 0.4f), new Vector3(0, 0.5f, -0.2f));
        else if (Kind == "stall")
            Materials.BoxCollider(this, new Vector3(w, 1f, 0.9f), new Vector3(0, 0.5f, -0.45f)); // seul le comptoir bloque
        else
            Materials.BoxCollider(this, s, c);

        if (ExamineText != "")
        {
            AddChild(new ExamineArea
            {
                Name = "Examine",
                Prompt = ExaminePrompt,
                Text = ExamineText,
                Size = new Vector3(w + 1.2f, 1.5f, d + 1.2f),
                Offset = new Vector3(0, 0.75f, -d / 2f),
            });
        }

        switch (Kind)
        {
            case "bed":
                Materials.Box(this, new Vector3(w, 0.35f, d), new Vector3(0, 0.175f, -d / 2f), Materials.Flat(Wood), "Frame");
                Materials.Box(this, new Vector3(w - 0.2f, 0.3f, d - 0.2f), new Vector3(0, 0.5f, -d / 2f), Materials.Flat(new Color("7a4a46")), "Blanket");
                Materials.Box(this, new Vector3(w - 0.4f, 0.25f, 0.7f), new Vector3(0, 0.6f, -d + 0.5f), Materials.Flat(new Color("cfc7b6")), "Pillow");
                Materials.Box(this, new Vector3(w, 0.9f, 0.15f), new Vector3(0, 0.45f, -d + 0.075f), Materials.Flat(WoodDark), "Headboard");
                break;
            case "table":
                Materials.Box(this, new Vector3(w, 0.12f, d), new Vector3(0, h - 0.06f, -d / 2f), Materials.Flat(WoodLight), "Top");
                foreach (var (lx, lz) in new[] { (-1f, -1f), (1f, -1f), (-1f, 1f), (1f, 1f) })
                    Materials.Box(this, new Vector3(0.15f, h, 0.15f), new Vector3(lx * (w / 2f - 0.15f), h / 2f, -d / 2f + lz * (d / 2f - 0.15f)), Materials.Flat(WoodDark), "Leg");
                break;
            case "chair":
                Materials.Box(this, new Vector3(w, 0.1f, d), new Vector3(0, 0.5f, -d / 2f), Materials.Flat(Wood), "Seat");
                Materials.Box(this, new Vector3(w, h, 0.12f), new Vector3(0, h / 2f, -d + 0.06f), Materials.Flat(WoodDark), "Back");
                Materials.Box(this, new Vector3(0.1f, 0.5f, 0.1f), new Vector3(-w / 2f + 0.1f, 0.25f, -0.1f), Materials.Flat(WoodDark), "Leg");
                Materials.Box(this, new Vector3(0.1f, 0.5f, 0.1f), new Vector3(w / 2f - 0.1f, 0.25f, -0.1f), Materials.Flat(WoodDark), "Leg2");
                break;
            case "chest":
                Materials.Box(this, new Vector3(w, h * 0.7f, d), new Vector3(0, h * 0.35f, -d / 2f), Materials.Flat(Wood), "Body");
                Materials.Box(this, new Vector3(w, h * 0.3f, d), new Vector3(0, h * 0.85f, -d / 2f), Materials.Flat(WoodDark), "Lid");
                Materials.Box(this, new Vector3(0.25f, 0.25f, 0.08f), new Vector3(0, h * 0.6f, 0.04f), Materials.Flat(new Color("8f8255")), "Lock");
                break;
            case "oven":
                Materials.Box(this, s, c, Materials.Flat(new Color("6f6e68")), "Body");
                Materials.Box(this, new Vector3(1.2f, 0.8f, 0.1f), new Vector3(0, 0.8f, 0.05f), Materials.Flat(new Color("2a1f17")), "Mouth");
                Materials.Box(this, new Vector3(1.0f, 0.5f, 0.12f), new Vector3(0, 0.75f, 0.06f), Materials.Flat(new Color("c8742c")), "Fire");
                Materials.Box(this, new Vector3(0.8f, 0.8f, 0.8f), new Vector3(0, h + 0.4f, -d / 2f), Materials.Flat(new Color("55544f")), "Chimney");
                break;
            case "counter":
                Materials.Box(this, new Vector3(w, h, d), c, Materials.Flat(WoodDark), "Body");
                Materials.Box(this, new Vector3(w + 0.1f, 0.1f, d + 0.1f), new Vector3(0, h - 0.05f, -d / 2f), Materials.Flat(WoodLight), "Top");
                for (int i = 0; i < 3; i++)
                    Materials.Box(this, new Vector3(0.7f, 0.3f, 0.45f), new Vector3(-1.2f + i * 1.2f, h + 0.15f, -d / 2f), Materials.Flat(new Color("b58a4c")), "Bread");
                break;
            case "shelf":
                Materials.Box(this, s, c, Materials.Flat(Wood), "Body");
                for (int i = 0; i < 3; i++)
                {
                    float y = 0.6f + i * 0.7f;
                    Materials.Box(this, new Vector3(w - 0.2f, 0.06f, d), new Vector3(0, y, -d / 2f + 0.02f), Materials.Flat(WoodDark), "Board");
                    Materials.Box(this, new Vector3(0.35f, 0.35f, 0.3f), new Vector3(-0.5f, y + 0.2f, -0.2f), Materials.Flat(new Color("4f6f45")), "Herb");
                    Materials.Box(this, new Vector3(0.35f, 0.35f, 0.3f), new Vector3(0.3f, y + 0.2f, -0.2f), Materials.Flat(new Color("b58a4c")), "Jar");
                }
                break;
            case "barrel":
                Materials.Cylinder(this, w / 2f, h, c, Materials.Flat(Wood), "Body");
                Materials.Cylinder(this, w / 2f + 0.03f, 0.1f, new Vector3(0, 0.25f, -d / 2f), Materials.Flat(WoodDark), "Ring");
                Materials.Cylinder(this, w / 2f + 0.03f, 0.1f, new Vector3(0, h - 0.3f, -d / 2f), Materials.Flat(WoodDark), "Ring2");
                break;
            case "sign":
                Materials.Cylinder(this, 0.08f, 1.0f, new Vector3(0, 0.5f, -0.2f), Materials.Flat(WoodDark), "Post");
                Materials.Box(this, new Vector3(w + 0.5f, 0.8f, 0.1f), new Vector3(0, 1.25f, -0.2f), Materials.Flat(WoodLight), "Plank");
                if (SignText != "")
                    AddChild(new Label3D
                    {
                        Text = SignText,
                        FontSize = 32,
                        PixelSize = 0.02f,
                        Modulate = new Color("2a1f17"),
                        Position = new Vector3(0, 1.25f, -0.14f),
                        Shaded = false,
                        TextureFilter = BaseMaterial3D.TextureFilterEnum.Nearest,
                    });
                break;
            case "stall":
                // Comptoir devant, deux poteaux à l'arrière reliés par une bannière :
                // pas d'auvent, pour que le marchand reste visible sous la caméra inclinée.
                Materials.Box(this, new Vector3(w, 1.0f, 0.9f), new Vector3(0, 0.5f, -0.45f), Materials.Flat(WoodDark), "Counter");
                Materials.Box(this, new Vector3(w + 0.1f, 0.1f, 1.0f), new Vector3(0, 1.0f, -0.45f), Materials.Flat(WoodLight), "CounterTop");
                for (int i = 0; i < 3; i++)
                    Materials.Box(this, new Vector3(0.5f, 0.3f, 0.4f), new Vector3(-1.2f + i * 1.2f, 1.2f, -0.45f), Materials.Flat(i == 1 ? new Color("8f7352") : new Color("b58a4c")), "Goods");
                foreach (float px in new[] { -w / 2f + 0.15f, w / 2f - 0.15f })
                    Materials.Box(this, new Vector3(0.14f, 3.0f, 0.14f), new Vector3(px, 1.5f, -d + 0.1f), Materials.Flat(WoodDark), "PostBack");
                Materials.Box(this, new Vector3(w, 0.7f, 0.08f), new Vector3(0, 2.6f, -d + 0.1f), Materials.Flat(Accent), "Banner");
                Materials.Box(this, new Vector3(w, 0.08f, 0.12f), new Vector3(0, 2.97f, -d + 0.1f), Materials.Flat(WoodDark), "BannerRail");
                break;
            case "board":
                // Tableau d'affichage sur deux pieds, quelques feuilles
                Materials.Box(this, new Vector3(0.14f, 2.2f, 0.14f), new Vector3(-w / 2f + 0.2f, 1.1f, -0.2f), Materials.Flat(WoodDark), "LegL");
                Materials.Box(this, new Vector3(0.14f, 2.2f, 0.14f), new Vector3(w / 2f - 0.2f, 1.1f, -0.2f), Materials.Flat(WoodDark), "LegR");
                Materials.Box(this, new Vector3(w, 1.4f, 0.12f), new Vector3(0, 1.5f, -0.2f), Materials.Flat(Wood), "Panel");
                Materials.Box(this, new Vector3(w + 0.1f, 0.12f, 0.2f), new Vector3(0, 2.25f, -0.2f), Materials.Flat(WoodDark), "Cap");
                Materials.Box(this, new Vector3(0.6f, 0.5f, 0.03f), new Vector3(-0.9f, 1.6f, -0.12f), Materials.Flat(new Color("d8d2c0")), "Paper");
                Materials.Box(this, new Vector3(0.6f, 0.5f, 0.03f), new Vector3(0.4f, 1.4f, -0.12f), Materials.Flat(new Color("cfc7b6")), "Paper2");
                break;
            case "gate":
                // Portail en bois entre deux piliers de pierre
                var stone = Materials.Flat(new Color("6f6e68"));
                Materials.Box(this, new Vector3(0.8f, 3.0f, 0.8f), new Vector3(-w / 2f + 0.4f, 1.5f, -0.3f), stone, "PillarL");
                Materials.Box(this, new Vector3(0.8f, 3.0f, 0.8f), new Vector3(w / 2f - 0.4f, 1.5f, -0.3f), stone, "PillarR");
                Materials.Box(this, new Vector3(w - 1.6f, 2.2f, 0.15f), new Vector3(0, 1.1f, -0.3f), Materials.Flat(WoodDark), "Doors");
                Materials.Box(this, new Vector3(0.1f, 2.2f, 0.2f), new Vector3(0, 1.1f, -0.3f), Materials.Flat(new Color("3a2e24")), "Seam");
                Materials.Box(this, new Vector3(w, 0.3f, 0.5f), new Vector3(0, 3.05f, -0.3f), stone, "Lintel");
                for (int i = 0; i < 2; i++)
                    Materials.Box(this, new Vector3(w - 1.6f, 0.12f, 0.2f), new Vector3(0, 0.6f + i * 1.0f, -0.2f), Materials.Flat(new Color("4a3b2e")), "Crossbar");
                break;
            default:
                Materials.Box(this, s, c, Materials.Flat(Wood), "Body");
                break;
        }
    }
}
