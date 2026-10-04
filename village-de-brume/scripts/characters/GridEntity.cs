using Godot;

namespace VillageDeBrume;

/// <summary>
/// Personnage sur la grille (joueur, PNJ) : case courante, direction, sprite
/// animé et déplacement case par case en glissant. L'origine est aux pieds,
/// au bas de la case ; le tri en Y des zones s'appuie dessus.
/// </summary>
public partial class GridEntity : Node2D
{
    public const float StepTime = 0.16f; // secondes par case

    public Vector2I Tile { get; private set; }
    public Zone? Zone { get; private set; }
    public bool IsMoving { get; private set; }

    public Color TunicColor { get; set; } = new("3a6ea5");
    public Color HairColor { get; set; } = new("5a3a22");
    public Color SkinColor { get; set; } = new("f1c9a5");
    public Color PantsColor { get; set; } = new("2a2a3a");

    private CharacterSprites.Facing _facing = CharacterSprites.Facing.Down;
    public CharacterSprites.Facing Facing
    {
        get => _facing;
        set { _facing = value; UpdateFrame(); }
    }

    protected Sprite2D Sprite { get; private set; } = null!;
    private Vector2 _from, _to;
    private float _progress;
    private float _walkTime;
    private Vector2I _previousTile;

    public override void _Ready()
    {
        Sprite = new Sprite2D
        {
            Name = "Sprite",
            Centered = false,
            Offset = new Vector2(-CharacterSprites.Cell / 2f, -(CharacterSprites.FeetRow + 1)),
            Hframes = 3,
            Vframes = 4,
            TextureFilter = TextureFilterEnum.Nearest,
        };
        AddChild(Sprite);
        RebuildSprite();
    }

    public void RebuildSprite()
    {
        if (Sprite == null) return;
        Sprite.Texture = CharacterSprites.Build(TunicColor, HairColor, SkinColor, PantsColor);
        UpdateFrame();
    }

    public override void _Draw()
    {
        // Ombre au sol
        DrawSetTransform(Vector2.Zero, 0f, new Vector2(1f, 0.45f));
        DrawCircle(new Vector2(0, -4), 6f, new Color(0, 0, 0, 0.22f));
    }

    /// <summary>Place l'entité sur une case d'une zone (sans animation).</summary>
    public void PlaceAt(Zone zone, Vector2I tile, CharacterSprites.Facing? facing = null)
    {
        Zone?.Map.SetOccupant(Tile, null);
        Zone = zone;
        Tile = tile;
        IsMoving = false;
        Position = GridMap.TileToWorld(tile);
        zone.Map.SetOccupant(tile, this);
        if (facing.HasValue) Facing = facing.Value;
        UpdateFrame();
    }

    public void Detach()
    {
        Zone?.Map.SetOccupant(Tile, null);
        Zone = null;
    }

    /// <summary>Tente un pas vers `delta` (4 ou 8 directions). Oriente toujours le personnage.</summary>
    public bool TryStep(Vector2I delta)
    {
        if (Zone == null || IsMoving || delta == Vector2I.Zero)
            return false;
        Facing = CharacterSprites.FacingFromDelta(delta, Facing);
        var target = Tile + delta;
        if (!Zone.Map.IsWalkable(target, this))
            return false;
        // En diagonale, les deux cases orthogonales doivent être libres (pas de coin coupé).
        if (delta.X != 0 && delta.Y != 0 &&
            (!Zone.Map.IsWalkable(Tile + new Vector2I(delta.X, 0), this) || !Zone.Map.IsWalkable(Tile + new Vector2I(0, delta.Y), this)))
            return false;
        _previousTile = Tile;
        Tile = target;
        Zone.Map.SetOccupant(target, this);
        _from = Position;
        _to = GridMap.TileToWorld(target);
        _progress = 0f;
        IsMoving = true;
        return true;
    }

    public override void _Process(double delta)
    {
        if (IsMoving)
        {
            _progress += (float)delta / StepTime;
            _walkTime += (float)delta;
            if (_progress >= 1f)
            {
                Position = _to;
                IsMoving = false;
                Zone?.Map.SetOccupant(_previousTile, Zone.Map.GetOccupant(_previousTile) == this ? null : Zone.Map.GetOccupant(_previousTile));
                OnStepFinished();
            }
            else
                Position = _from.Lerp(_to, _progress);
        }
        else
            _walkTime = 0f;
        UpdateFrame();
    }

    protected virtual void OnStepFinished() { }

    public void FaceTowards(Vector2I tile)
    {
        var d = tile - Tile;
        if (Mathf.Abs(d.X) > Mathf.Abs(d.Y)) d.Y = 0; else d.X = 0;
        Facing = CharacterSprites.FacingFromDelta(d, Facing);
    }

    private void UpdateFrame()
    {
        if (Sprite == null) return;
        int pose = IsMoving ? 1 + (int)(_walkTime * 8f) % 2 : 0;
        Sprite.Frame = (int)_facing * 3 + pose;
    }
}
