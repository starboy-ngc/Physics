using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Mobilier et petits objets (lit, table, chaise, coffre, four, panneau...).
/// Origine au milieu du bas de l'objet (tri en Y). Collision = emprise dessinée.
/// </summary>
public partial class Prop : StaticBody2D
{
    private string _kind = "table";
    [Export(PropertyHint.Enum, "bed,table,chair,chest,oven,counter,shelf,barrel,sign")]
    public string Kind { get => _kind; set { _kind = value; QueueRedraw(); } }
    private string _signText = "";
    /// <summary>Texte du panneau (Kind = "sign").</summary>
    [Export] public string SignText { get => _signText; set { _signText = value; QueueRedraw(); } }

    private static readonly Dictionary<string, Vector2> Sizes = new()
    {
        ["bed"] = new(32, 48), ["table"] = new(40, 24), ["chair"] = new(14, 16),
        ["chest"] = new(24, 18), ["oven"] = new(40, 40), ["counter"] = new(64, 20),
        ["shelf"] = new(32, 40), ["barrel"] = new(16, 20), ["sign"] = new(24, 28),
    };

    private static readonly Color Wood = new("8a5a2b");
    private static readonly Color WoodDark = new("5c3a1a");
    private static readonly Color WoodLight = new("b08a5c");
    private static readonly Color Cloth = new("c9544a");
    private static readonly Color Sheet = new("e8e2d0");
    private static readonly Color Stone = new("8f8f88");
    private static readonly Color Fire = new("e8903a");
    private static readonly Color Metal = new("c8b060");
    private static readonly Color Herb = new("5a9a4e");
    private static readonly Color Bread = new("d9a05a");
    private static readonly Color Outline = new("2a1f17");

    public Vector2 GetSize() => Sizes.TryGetValue(Kind, out var s) ? s : new Vector2(16, 16);

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        Vector2 s = GetSize();
        bool sign = Kind == "sign";
        AddChild(new CollisionShape2D
        {
            // Le panneau ne bloque que par son poteau ; le reste bloque entièrement.
            Shape = new RectangleShape2D { Size = sign ? new Vector2(6, 6) : s },
            Position = sign ? new Vector2(0, -3) : new Vector2(0, -s.Y / 2f),
        });
    }

    public override void _Draw()
    {
        Vector2 s = GetSize();
        var r = new Rect2(-s.X / 2f, -s.Y, s.X, s.Y);
        switch (Kind)
        {
            case "bed":
                DrawRect(r, Wood);
                DrawRect(new Rect2(r.Position.X + 2, r.Position.Y + 10, s.X - 4, s.Y - 12), Cloth);
                DrawRect(new Rect2(r.Position.X + 2, r.Position.Y + 2, s.X - 4, 8), Sheet);
                break;
            case "table":
                DrawRect(r, WoodLight);
                DrawRect(new Rect2(r.Position.X, r.End.Y - 6, s.X, 6), WoodDark);
                break;
            case "chair":
                DrawRect(new Rect2(r.Position.X, r.Position.Y, s.X, 6), WoodDark);
                DrawRect(new Rect2(r.Position.X, r.Position.Y + 6, s.X, s.Y - 6), Wood);
                break;
            case "chest":
                DrawRect(r, Wood);
                DrawRect(new Rect2(r.Position.X, r.Position.Y, s.X, 6), WoodDark);
                DrawRect(new Rect2(-2, r.Position.Y + 6, 4, 4), Metal);
                break;
            case "oven":
                DrawRect(r, Stone);
                DrawRect(new Rect2(-10, r.Position.Y + 18, 20, 12), Outline);
                DrawRect(new Rect2(-8, r.Position.Y + 20, 16, 8), Fire);
                break;
            case "counter":
                DrawRect(r, WoodLight);
                DrawRect(new Rect2(r.Position.X, r.End.Y - 8, s.X, 8), WoodDark);
                for (int i = 0; i < 3; i++)
                    DrawRect(new Rect2(r.Position.X + 6 + i * 18, r.Position.Y + 3, 12, 6), Bread);
                break;
            case "shelf":
                DrawRect(r, Wood);
                for (int i = 0; i < 3; i++)
                {
                    float y = r.Position.Y + 8 + i * 12;
                    DrawRect(new Rect2(r.Position.X + 2, y, s.X - 4, 2), WoodDark);
                    DrawRect(new Rect2(r.Position.X + 4, y - 6, 6, 6), Herb);
                    DrawRect(new Rect2(r.Position.X + 14, y - 6, 6, 6), Bread);
                }
                break;
            case "barrel":
                DrawRect(r, Wood);
                DrawRect(new Rect2(r.Position.X, r.Position.Y + 4, s.X, 2), WoodDark);
                DrawRect(new Rect2(r.Position.X, r.End.Y - 6, s.X, 2), WoodDark);
                break;
            case "sign":
                DrawRect(new Rect2(-2, -14, 4, 14), WoodDark);
                var plank = new Rect2(r.Position.X, r.Position.Y, s.X, 14);
                DrawRect(plank, WoodLight);
                DrawRect(plank, Outline, false, 1f);
                if (SignText != "")
                    DrawString(ThemeDB.FallbackFont, new Vector2(plank.Position.X, plank.End.Y - 3f), SignText,
                        HorizontalAlignment.Center, plank.Size.X, 8, Outline);
                return;
        }
        DrawRect(r, Outline, false, 1f);
    }
}
