using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Le Village de Brume : herbe en tuiles, arbres en bordure (placés
/// automatiquement), sortie vers la forêt sur le bord droit (étape 5).
/// </summary>
public partial class Village : Zone
{
    private const float Tile = 16f;

    [Export] public bool BorderTrees { get; set; } = true;
    /// <summary>Rectangle (en pixels) sans arbre de bordure : ouverture vers la forêt.</summary>
    [Export] public Rect2 ExitGap { get; set; } = new(700, 250, 80, 90);

    private static readonly Color GrassA = new("6fae4e");
    private static readonly Color GrassB = new("68a548");
    private static readonly Color GrassMark = new("5a9440");
    private static readonly Color GrassLight = new("86c25f");

    public override void _Ready()
    {
        base._Ready();
        if (BorderTrees)
            PlaceBorderTrees();
    }

    private void PlaceBorderTrees()
    {
        var treeScene = GD.Load<PackedScene>("res://scenes/world/props/Tree.tscn");
        var rng = new RandomNumberGenerator { Seed = 1234 };
        var holder = new Node2D { Name = "BorderTrees", YSortEnabled = true };
        AddChild(holder);

        var positions = new List<Vector2>();
        for (float x = Bounds.Position.X + 40f; x <= Bounds.End.X - 40f; x += 48f)
        {
            positions.Add(new Vector2(x, Bounds.Position.Y + 60f));
            positions.Add(new Vector2(x, Bounds.End.Y - 16f));
        }
        for (float y = Bounds.Position.Y + 88f; y <= Bounds.End.Y - 64f; y += 48f)
        {
            positions.Add(new Vector2(Bounds.Position.X + 40f, y));
            positions.Add(new Vector2(Bounds.End.X - 40f, y));
        }

        foreach (var p in positions)
        {
            if (ExitGap.HasPoint(p))
                continue;
            var tree = treeScene.Instantiate<TreeProp>();
            tree.Position = p + new Vector2(rng.RandfRange(-6f, 6f), rng.RandfRange(-4f, 4f));
            tree.CanopyRadius = rng.RandfRange(12f, 16f);
            holder.AddChild(tree);
        }
    }

    public override void _Draw()
    {
        // Herbe en damier discret de tuiles 16x16, avec petites marques.
        int cols = Mathf.CeilToInt(Bounds.Size.X / Tile);
        int rows = Mathf.CeilToInt(Bounds.Size.Y / Tile);
        for (int ty = 0; ty < rows; ty++)
        {
            for (int tx = 0; tx < cols; tx++)
            {
                Vector2 origin = Bounds.Position + new Vector2(tx, ty) * Tile;
                DrawRect(new Rect2(origin, new Vector2(Tile, Tile)), (tx + ty) % 2 == 0 ? GrassA : GrassB);
                int k = (tx * 7 + ty * 13) % 5;
                DrawRect(new Rect2(origin + new Vector2(2 + k, 4), new Vector2(2, 2)), GrassMark);
                DrawRect(new Rect2(origin + new Vector2(9 - k, 11), new Vector2(2, 2)), GrassMark);
                if ((tx * 3 + ty * 5) % 11 == 0)
                    DrawRect(new Rect2(origin + new Vector2(6, 7), new Vector2(3, 2)), GrassLight);
            }
        }
    }
}
