using Godot;

namespace VillageDeBrume;

/// <summary>La maison du joueur : lit, table, et les coffres qui servent de rangement.</summary>
public partial class Home : Zone
{
    public override string ZoneName => "Maison";

    private static readonly string[] Layout =
    {
        "xUUUUUUUUUUx",
        "xWWWWWWWWWWx",
        "x==========x",
        "x==========x",
        "x====rr====x",
        "x====rr====x",
        "x==========x",
        "x==========x",
        "x=====m====x",
        "xxxxxxxxxxxx",
    };

    protected override void Build()
    {
        LoadLayout(Layout);
        AddProp("Bed", Art.BedTexture(), new Vector2I(1, 2), new Vector2I(1, 2));
        AddInteractable(new Vector2I(1, 2), new Examinable("Dormir", "Pas maintenant. Les lumières n'attendent pas."));
        AddInteractable(new Vector2I(1, 3), new Examinable("Dormir", "Pas maintenant. Les lumières n'attendent pas."));
        AddProp("Table", Art.Table(), new Vector2I(5, 2), new Vector2I(1, 1));
        AddProp("Stool", Art.Stool(), new Vector2I(6, 2), new Vector2I(1, 1));
        AddProp("Barrel", Art.Barrel(), new Vector2I(1, 7), new Vector2I(1, 1));
        AddProp("ChestA", Art.Chest(), new Vector2I(8, 2), new Vector2I(1, 1));
        AddProp("ChestB", Art.Chest(), new Vector2I(9, 2), new Vector2I(1, 1));
        AddInteractable(new Vector2I(8, 2), new StorageChest());
        AddInteractable(new Vector2I(9, 2), new StorageChest());
        AddDoor(new Vector2I(6, 8), "orion", "from_home");
        Spawns["start"] = new Vector2I(4, 6);
        Spawns["entrance"] = new Vector2I(6, 7);
    }
}
