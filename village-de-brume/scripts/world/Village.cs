using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Le Village de Brume : sol d'herbe texturé, arbres en bordure (placés
/// automatiquement), ouverture vers la forêt sur le bord droit (étape 5).
/// </summary>
public partial class Village : Zone
{
    [Export] public bool BorderTrees { get; set; } = true;
    /// <summary>Rectangle (x, z) sans arbre de bordure : ouverture vers la forêt.</summary>
    [Export] public Rect2 ExitGap { get; set; } = new(43.75f, 15.6f, 5f, 5.6f);

    protected override void BuildGround()
    {
        AddFloor(Bounds, 0f, Materials.Textured("grass", Bounds.Size, Materials.Grass, 2f), "Grass");
    }

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
        var holder = new Node3D { Name = "BorderTrees" };
        AddChild(holder);

        var positions = new List<Vector2>();
        for (float x = Bounds.Position.X + 2.5f; x <= Bounds.End.X - 2.5f; x += 3f)
        {
            positions.Add(new Vector2(x, Bounds.Position.Y + 2.5f));
            positions.Add(new Vector2(x, Bounds.End.Y - 1.5f));
        }
        for (float z = Bounds.Position.Y + 5.5f; z <= Bounds.End.Y - 4f; z += 3f)
        {
            positions.Add(new Vector2(Bounds.Position.X + 2.5f, z));
            positions.Add(new Vector2(Bounds.End.X - 2.5f, z));
        }

        foreach (var p in positions)
        {
            if (ExitGap.HasPoint(p))
                continue;
            var tree = treeScene.Instantiate<TreeProp>();
            tree.Position = new Vector3(p.X + rng.RandfRange(-0.4f, 0.4f), 0f, p.Y + rng.RandfRange(-0.25f, 0.25f));
            tree.CanopyRadius = rng.RandfRange(0.8f, 1.05f);
            tree.Kind = rng.Randf() < 0.6f ? "pine" : "round";
            holder.AddChild(tree);
        }
    }
}
