using Godot;

namespace VillageDeBrume;

/// <summary>
/// Maison vue de l'extérieur en 3/4 : toit vu de dessus (deux pans), avancée
/// de toit, murs, porte, fenêtres, enseigne. L'origine est au milieu du bas
/// des murs. La porte (Door) est créée automatiquement devant le bâtiment.
/// </summary>
public partial class Building : StaticBody2D
{
    private Vector2 _size = new(96, 72);
    [Export] public Vector2 Size { get => _size; set { _size = value; QueueRedraw(); } }
    private Color _wallColor = new("e9dcc0");
    [Export] public Color WallColor { get => _wallColor; set { _wallColor = value; QueueRedraw(); } }
    private Color _roofColor = new("b0503e");
    [Export] public Color RoofColor { get => _roofColor; set { _roofColor = value; QueueRedraw(); } }
    private string _label = "";
    [Export] public string Label { get => _label; set { _label = value; QueueRedraw(); } }
    [Export] public string DoorTargetZone { get; set; } = "";
    [Export] public string DoorTargetSpawn { get; set; } = "entrance";

    private const float RoofHeight = 36f;
    private const float RoofOverhang = 8f;
    private static readonly Vector2 DoorSize = new(16, 26);
    private static readonly Color Outline = new("2a1f17");
    private static readonly Color DoorColor = new("5a3a22");
    private static readonly Color DoorFrame = new("8a6a4a");
    private static readonly Color Window = new("8fc6e8");
    private static readonly Color WindowDark = new("4a7aa8");
    private static readonly Color Sign = new("c9a66e");
    private static readonly Color Step = new("a8a49a");

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        AddChild(new CollisionShape2D
        {
            Shape = new RectangleShape2D { Size = Size },
            Position = new Vector2(0, -Size.Y / 2f),
        });

        if (DoorTargetZone != "" && !Engine.IsEditorHint())
        {
            AddChild(new Door
            {
                Name = "Door",
                TargetZone = DoorTargetZone,
                TargetSpawn = DoorTargetSpawn,
                Size = new Vector2(14, 8),
                Position = new Vector2(0, 6),
            });
        }
    }

    public override void _Draw()
    {
        float w = Size.X, h = Size.Y;
        var walls = new Rect2(-w / 2f, -h, w, h);

        // Ombre portée au sol
        DrawRect(new Rect2(-w / 2f - 2f, -3f, w + 4f, 5f), new Color(0, 0, 0, 0.18f));

        // Murs + soubassement + ombre sous l'avancée du toit
        DrawRect(walls, WallColor);
        DrawRect(new Rect2(walls.Position.X, walls.End.Y - 6f, w, 6f), WallColor.Darkened(0.3f));
        DrawRect(new Rect2(walls.Position.X, walls.Position.Y, w, 5f), WallColor.Darkened(0.2f));

        // Toit : deux pans vus de dessus
        float top = -h - RoofHeight;
        float left = -w / 2f - RoofOverhang;
        float right = w / 2f + RoofOverhang;
        float ridgeY = top + 6f;
        var panLeft = new[] { new Vector2(left, -h + 4f), new Vector2(0, -h + 4f), new Vector2(0, ridgeY), new Vector2(left + 10f, top) };
        var panRight = new[] { new Vector2(0, -h + 4f), new Vector2(right, -h + 4f), new Vector2(right - 10f, top), new Vector2(0, ridgeY) };
        DrawColoredPolygon(panLeft, RoofColor.Lightened(0.08f));
        DrawColoredPolygon(panRight, RoofColor.Darkened(0.12f));
        // Tuiles : lignes horizontales
        for (float ty = -h; ty > top + 8f; ty -= 6f)
        {
            float t = (ty - (-h + 4f)) / (top - (-h + 4f));
            float inset = 10f * t;
            DrawLine(new Vector2(left + inset, ty), new Vector2(right - inset, ty), RoofColor.Darkened(0.3f), 1f);
        }
        // Faîtage, bord du toit, contour
        DrawRect(new Rect2(left + 10f, top - 2f, w + 2f * RoofOverhang - 20f, 3f), RoofColor.Darkened(0.4f));
        DrawRect(new Rect2(left, -h + 2f, right - left, 3f), RoofColor.Darkened(0.45f));
        DrawPolyline(new[] { new Vector2(left, -h + 4f), new Vector2(left + 10f, top), new Vector2(right - 10f, top), new Vector2(right, -h + 4f) }, Outline, 1f);

        // Fenêtres
        var win = new Vector2(14, 12);
        foreach (float wx in new[] { -w / 2f + 12f, w / 2f - 12f - win.X })
        {
            var r = new Rect2(wx, -h + 26f, win.X, win.Y);
            DrawRect(r, Window);
            DrawRect(new Rect2(r.Position + new Vector2(2, 2), new Vector2(4, 3)), Colors.White);
            DrawRect(new Rect2(r.Position.X, r.GetCenter().Y, win.X, 1), WindowDark);
            DrawRect(new Rect2(r.GetCenter().X, r.Position.Y, 1, win.Y), WindowDark);
            DrawRect(r, Outline, false, 1f);
            DrawRect(new Rect2(r.Position.X - 1f, r.End.Y, win.X + 2f, 2f), WallColor.Darkened(0.4f));
        }

        // Porte avec encadrement, et marche devant
        var door = new Rect2(-DoorSize.X / 2f, -DoorSize.Y, DoorSize.X, DoorSize.Y);
        DrawRect(door.Grow(2f), DoorFrame);
        DrawRect(door, DoorColor);
        DrawRect(new Rect2(door.Position.X + 2f, door.Position.Y + 2f, DoorSize.X - 4f, 6f), DoorColor.Lightened(0.15f));
        DrawRect(new Rect2(3f, -DoorSize.Y / 2f, 2f, 2f), new Color("e0c060"));
        DrawRect(door.Grow(2f), Outline, false, 1f);
        var step = new Rect2(-DoorSize.X / 2f - 3f, 0f, DoorSize.X + 6f, 4f);
        DrawRect(step, Step);
        DrawRect(step, Outline, false, 1f);

        // Contour des murs
        DrawRect(walls, Outline, false, 1f);

        // Enseigne
        if (Label != "")
        {
            var signRect = new Rect2(-30f, -h + 8f, 60f, 12f);
            DrawRect(signRect, Sign);
            DrawRect(signRect, Outline, false, 1f);
            DrawString(ThemeDB.FallbackFont, new Vector2(signRect.Position.X, signRect.End.Y - 3f), Label,
                HorizontalAlignment.Center, signRect.Size.X, 8, Outline);
        }
    }
}
