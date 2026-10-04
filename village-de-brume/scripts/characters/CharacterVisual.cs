using Godot;

namespace VillageDeBrume;

/// <summary>
/// Présence visuelle d'un personnage en 2.5D : un Sprite3D tourné vers la
/// caméra (planche générée par CharacterSprites) et une ombre ronde au sol.
/// Origine aux pieds. 1 unité monde = 16 px de sprite.
/// </summary>
public partial class CharacterVisual : Node3D
{
    public enum Facing { Down, Up, Left, Right }

    [Export] public Color TunicColor { get; set; } = new("3a6ea5");
    [Export] public Color HairColor { get; set; } = new("5a3a22");
    [Export] public Color SkinColor { get; set; } = new("f1c9a5");
    [Export] public Color PantsColor { get; set; } = new("2a2a3a");

    private const float WalkAnimFps = 8f;
    private const float PixelSize = 1f / 16f;

    private Sprite3D _sprite = null!;
    private Facing _facing = Facing.Down;
    private float _walkTime;

    public Facing FacingDirection
    {
        get => _facing;
        set { _facing = value; UpdateFrame(); }
    }
    public bool IsMoving { get; private set; }

    public override void _Ready()
    {
        _sprite = new Sprite3D
        {
            Name = "Sprite",
            Hframes = 3,
            Vframes = 4,
            PixelSize = PixelSize,
            Billboard = BaseMaterial3D.BillboardModeEnum.Enabled,
            TextureFilter = BaseMaterial3D.TextureFilterEnum.Nearest,
            AlphaCut = SpriteBase3D.AlphaCutMode.Discard,
            Shaded = false,
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
            // Le sprite est un panneau face caméra centré sur ce point. On le monte
            // pour que, à l'écran, la ligne des pieds (30) tombe exactement sur
            // l'origine au sol : 14 px « vers le haut de l'écran » = 14 px / cos(pitch) en hauteur monde.
            Position = new Vector3(0, (CharacterSprites.FeetRow - CharacterSprites.Cell / 2f) * PixelSize / Mathf.Cos(Mathf.DegToRad(FollowCamera.DefaultPitch)), 0),
        };
        AddChild(_sprite);
        var shadow = new MeshInstance3D
        {
            Name = "Shadow",
            Mesh = new CylinderMesh { TopRadius = 0.45f, BottomRadius = 0.45f, Height = 0.02f, RadialSegments = 10 },
            MaterialOverride = Materials.Flat(new Color(0, 0, 0, 0.28f)),
            Position = new Vector3(0, 0.012f, 0),
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
        AddChild(shadow);
        Rebuild();
    }

    /// <summary>Régénère la planche de sprites avec les couleurs courantes.</summary>
    public void Rebuild()
    {
        if (_sprite == null)
            return;
        _sprite.Texture = CharacterSprites.Build(TunicColor, HairColor, SkinColor, PantsColor);
        UpdateFrame();
    }

    public void Animate(float delta, bool moving)
    {
        IsMoving = moving;
        _walkTime = moving ? _walkTime + delta : 0f;
        UpdateFrame();
    }

    private void UpdateFrame()
    {
        if (_sprite == null)
            return;
        int pose = IsMoving ? 1 + (int)(_walkTime * WalkAnimFps) % 2 : 0;
        _sprite.Frame = (int)_facing * 3 + pose;
    }

    // --- Aides de direction (monde : haut = -Z, bas = +Z, gauche = -X, droite = +X)

    public static Facing FacingFromInput(Vector2 v, Facing current)
    {
        if (v.Y > 0f) return Facing.Down;
        if (v.Y < 0f) return Facing.Up;
        if (v.X > 0f) return Facing.Right;
        if (v.X < 0f) return Facing.Left;
        return current;
    }

    public static Facing FacingFromString(string s) => s.ToLowerInvariant() switch
    {
        "up" => Facing.Up,
        "left" => Facing.Left,
        "right" => Facing.Right,
        _ => Facing.Down,
    };

    public static Facing FacingTowards(Vector3 from, Vector3 target)
    {
        float dx = target.X - from.X, dz = target.Z - from.Z;
        if (Mathf.Abs(dx) > Mathf.Abs(dz))
            return dx > 0f ? Facing.Right : Facing.Left;
        return dz > 0f ? Facing.Down : Facing.Up;
    }

    public static Vector3 ToVector(Facing f) => f switch
    {
        Facing.Up => new Vector3(0, 0, -1),
        Facing.Down => new Vector3(0, 0, 1),
        Facing.Left => new Vector3(-1, 0, 0),
        _ => new Vector3(1, 0, 0),
    };
}
