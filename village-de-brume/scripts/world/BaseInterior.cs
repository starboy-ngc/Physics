using Godot;

namespace VillageDeBrume;

/// <summary>La base du joueur : une petite pièce avec lit, coffre, table et tapis.</summary>
public partial class BaseInterior : Zone
{
    public override string ZoneName => "Ma base";

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
        AddProp("Bed", Art.Bed(), new Vector2I(1, 2), new Vector2I(1, 2));
        AddProp("Chest", Art.Chest(), new Vector2I(9, 2), new Vector2I(1, 1));
        AddInteractable(new Vector2I(9, 2), new Examinable("Ouvrir", "Le coffre est vide. Il servira à ranger le butin des expéditions."));
        AddProp("Table", Art.Table(), new Vector2I(5, 2), new Vector2I(2, 1));
        AddInteractable(new Vector2I(1, 2), new Examinable("Dormir", "Pas maintenant. Le temps passera à l'étape suivante."));
        AddInteractable(new Vector2I(1, 3), new Examinable("Dormir", "Pas maintenant. Le temps passera à l'étape suivante."));
        AddDoor(new Vector2I(6, 8), "village", "from_base");
        Spawns["start"] = new Vector2I(4, 6);
        Spawns["entrance"] = new Vector2I(6, 7);
    }
}
