using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Zone jouable 2D sur grille (village, base). Construit sa carte à partir d'un
/// plan ASCII, pose les décors, connaît ses points d'apparition, ses portes
/// (case -> zone) et ses interactions (case -> objet).
/// Les enfants sont triés en Y : l'origine de chaque sprite est à sa base.
/// </summary>
public abstract partial class Zone : Node2D
{
    public abstract string ZoneName { get; }
    public GridMap Map { get; private set; } = null!;
    public Dictionary<string, Vector2I> Spawns { get; } = new();
    public Dictionary<Vector2I, (string zone, string spawn)> Doors { get; } = new();
    public Dictionary<Vector2I, IGridInteractable> Interactables { get; } = new();

    public Rect2 Bounds => new(0, 0, Map.Width * Art.Tile, Map.Height * Art.Tile);

    public override void _Ready()
    {
        YSortEnabled = true;
        Map = new GridMap { Name = "Map", ZIndex = -1 };
        AddChild(Map);
        Build();
        Map.QueueRedraw();
    }

    /// <summary>Construit la zone (plan, décors, portes...).</summary>
    protected abstract void Build();

    public Vector2I GetSpawn(string name)
    {
        if (Spawns.TryGetValue(name, out var t))
            return t;
        GD.PushWarning($"Zone '{ZoneName}' : point d'apparition '{name}' introuvable.");
        return new Vector2I(Map.Width / 2, Map.Height / 2);
    }

    public IGridInteractable? GetInteractable(Vector2I tile) =>
        Interactables.TryGetValue(tile, out var i) ? i : null;

    /// <summary>
    /// Charge un plan ASCII. Légende du sol : '.' herbe, 'd' herbe sombre,
    /// ':' chemin, '#' pavés, '~' eau, 'w' bord d'eau, '*' fleurs, '=' plancher,
    /// 'W' mur, 'U' haut de mur, 'r' tapis, 'm' paillasson, 'x' vide.
    /// 's' rivage (mer/sable), 'S' sable.
    /// Décors (sur herbe) : 'T' arbre, 't' buisson, 'o' rocher, 'F' barrière, 'R' roseaux,
    /// 'P' palissade, 'L' lanterne, 'C' caisse, 'B' tonneau.
    /// </summary>
    protected void LoadLayout(string[] rows)
    {
        int h = rows.Length, w = rows[0].Length;
        Map.Init(w, h);
        var rng = new RandomNumberGenerator { Seed = 4242 };
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                var t = new Vector2I(x, y);
                char c = x < rows[y].Length ? rows[y][x] : 'x';
                TileId ground = c switch
                {
                    '.' or 'T' or 't' or 'o' or 'F' or 'R' or 'P' or 'L' or 'C' or 'B' => rng.Randf() < 0.75f ? TileId.Grass : rng.Randf() < 0.5f ? TileId.GrassB : TileId.GrassC,
                    's' => TileId.Shore,
                    'S' => TileId.Sand,
                    'd' => TileId.GrassDark,
                    ':' => TileId.Path,
                    '#' => (x + y) % 2 == 0 ? TileId.Plaza : TileId.PlazaB,
                    '~' => TileId.Water,
                    'w' => TileId.WaterEdge,
                    '*' => TileId.Flower,
                    '=' => (x + y) % 2 == 0 ? TileId.Floor : TileId.FloorB,
                    'W' => TileId.Wall,
                    'U' => TileId.WallTop,
                    'r' => TileId.Rug,
                    'm' => TileId.Mat,
                    _ => TileId.Void,
                };
                Map.SetGround(t, ground);
                if (c is '~' or 'w' or 's' or 'W' or 'U' or 'x')
                    Map.Block(t);
                switch (c)
                {
                    case 'T': AddProp($"Tree_{x}_{y}", Art.Tree(), t, new Vector2I(1, 1)); break;
                    case 't': AddProp($"Bush_{x}_{y}", Art.Bush(), t, new Vector2I(1, 1)); break;
                    case 'o': AddProp($"Rock_{x}_{y}", Art.Rock(), t, new Vector2I(1, 1)); break;
                    case 'F': AddProp($"Fence_{x}_{y}", Art.Fence(), t, new Vector2I(1, 1)); break;
                    case 'R': AddProp($"Reeds_{x}_{y}", Art.Reeds(), t, new Vector2I(1, 1), false); break;
                    case 'P': AddProp($"Palisade_{x}_{y}", Art.Palisade(), t, new Vector2I(1, 1)); break;
                    case 'L': AddProp($"Lantern_{x}_{y}", Art.LanternPost(), t, new Vector2I(1, 1)); break;
                    case 'C': AddProp($"Crate_{x}_{y}", Art.Crate(), t, new Vector2I(1, 1)); break;
                    case 'B': AddProp($"Barrel_{x}_{y}", Art.Barrel(), t, new Vector2I(1, 1)); break;
                }
            }
    }

    protected PropNode AddProp(string name, Texture2D texture, Vector2I origin, Vector2I footprint, bool blocks = true)
    {
        var prop = PropNode.Create(name, texture, origin, footprint, blocks);
        AddChild(prop);
        if (blocks)
            Map.BlockRect(origin, footprint);
        return prop;
    }

    protected void AddDoor(Vector2I tile, string targetZone, string targetSpawn) => Doors[tile] = (targetZone, targetSpawn);

    protected void AddInteractable(Vector2I tile, IGridInteractable interactable) => Interactables[tile] = interactable;
}
