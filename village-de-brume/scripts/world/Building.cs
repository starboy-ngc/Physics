using Godot;

namespace VillageDeBrume;

/// <summary>
/// Maison en volumes : murs (boîte), toit à deux pans (prisme), porte,
/// fenêtres, enseigne. L'origine est au milieu de la façade, au sol ; la
/// façade regarde +Z (vers la caméra). La porte (Door) est créée devant.
/// </summary>
public partial class Building : StaticBody3D
{
    /// <summary>Emprise au sol (largeur x, profondeur z).</summary>
    [Export] public Vector2 Size { get; set; } = new(6f, 4.5f);
    [Export] public float WallHeight { get; set; } = 2.6f;
    [Export] public Color WallColor { get; set; } = new("e9dcc0");
    [Export] public Color RoofColor { get; set; } = new("b0503e");
    [Export] public string Label { get; set; } = "";
    [Export] public string DoorTargetZone { get; set; } = "";
    [Export] public string DoorTargetSpawn { get; set; } = "entrance";

    private const float RoofHeight = 1.7f;
    private const float RoofOverhang = 0.5f;

    public override void _Ready()
    {
        CollisionLayer = 1;
        CollisionMask = 0;
        float w = Size.X, d = Size.Y, h = WallHeight;
        float zc = -d / 2f; // centre de l'emprise (la façade est en z = 0)

        Materials.BoxCollider(this, new Vector3(w, h, d), new Vector3(0, h / 2f, zc));

        // Murs + soubassement
        Materials.Box(this, new Vector3(w, h, d), new Vector3(0, h / 2f, zc), Materials.Flat(WallColor), "Walls");
        Materials.Box(this, new Vector3(w + 0.1f, 0.3f, d + 0.1f), new Vector3(0, 0.15f, zc), Materials.Flat(WallColor.Darkened(0.3f)), "Base");

        // Toit : prisme à deux pans, faîtage parallèle à la façade (axe X)
        var roof = new MeshInstance3D
        {
            Name = "Roof",
            Mesh = new PrismMesh { Size = new Vector3(d + 2 * RoofOverhang, RoofHeight, w + 2 * RoofOverhang), LeftToRight = 0.5f },
            MaterialOverride = Materials.Textured("roof" + RoofColor.ToHtml(), new Vector2(w + 1, d + 1), () => Materials.RoofTiles(RoofColor), 1f),
            Position = new Vector3(0, h + RoofHeight / 2f, zc),
            RotationDegrees = new Vector3(0, 90, 0),
        };
        AddChild(roof);
        // Avancée de toit (bord sombre) le long de la façade et de l'arrière
        Materials.Box(this, new Vector3(w + 2 * RoofOverhang, 0.12f, d + 2 * RoofOverhang), new Vector3(0, h - 0.06f, zc), Materials.Flat(RoofColor.Darkened(0.45f)), "Eaves");

        // Porte avec encadrement, et marche devant
        var doorMat = Materials.Flat(new Color("5a3a22"));
        Materials.Box(this, new Vector3(1.2f, 1.75f, 0.08f), new Vector3(0, 0.875f, 0.04f), Materials.Flat(new Color("8a6a4a")), "DoorFrame");
        Materials.Box(this, new Vector3(1.0f, 1.6f, 0.1f), new Vector3(0, 0.8f, 0.06f), doorMat, "Door");
        Materials.Box(this, new Vector3(0.12f, 0.12f, 0.12f), new Vector3(0.3f, 0.85f, 0.1f), Materials.Flat(new Color("e0c060")), "Knob");
        Materials.Box(this, new Vector3(1.6f, 0.15f, 0.6f), new Vector3(0, 0.075f, 0.3f), Materials.Flat(new Color("a8a49a")), "Step");

        // Fenêtres
        var glass = Materials.Flat(new Color("8fc6e8"));
        var frame = Materials.Flat(WallColor.Darkened(0.4f));
        foreach (float x in new[] { -w / 2f + 1.3f, w / 2f - 1.3f })
        {
            Materials.Box(this, new Vector3(1.0f, 0.85f, 0.08f), new Vector3(x, 1.55f, 0.04f), frame, "WindowFrame");
            Materials.Box(this, new Vector3(0.85f, 0.7f, 0.1f), new Vector3(x, 1.55f, 0.05f), glass, "Window");
            Materials.Box(this, new Vector3(0.06f, 0.7f, 0.12f), new Vector3(x, 1.55f, 0.06f), frame, "WindowBar");
            Materials.Box(this, new Vector3(0.85f, 0.06f, 0.12f), new Vector3(x, 1.55f, 0.06f), frame, "WindowBar2");
        }

        // (Pas d'enseigne : illisible en 256x192. Le nom de la maison viendra
        // des dialogues et du debug.)

        // Porte (zone de passage) devant la façade
        if (DoorTargetZone != "" && !Engine.IsEditorHint())
        {
            AddChild(new Door
            {
                Name = "Door",
                TargetZone = DoorTargetZone,
                TargetSpawn = DoorTargetSpawn,
                Size = new Vector2(1.0f, 0.6f),
                Position = new Vector3(0, 0, 0.45f),
            });
        }
    }
}
