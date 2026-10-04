using Godot;

namespace VillageDeBrume;

/// <summary>
/// La place du village : étang au nord, étals (boutique, dépôt) de part et
/// d'autre du chemin, tableau des requêtes, puits au centre de la place pavée,
/// base du joueur au sud, portail de l'est (futurs donjons).
/// </summary>
public partial class Village : Zone
{
    public override string ZoneName => "Place de Brume";

    private static readonly string[] Layout =
    {
        "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
        "T..........wwwwwwwwww..........T",
        "T.t.......R~~~~~~~~~~R.......t.T",
        "T.........R~~~~~~~~~~R.........T",
        "T...*......~~~~~~~~~~......*...T",
        "T..............::..............T",
        "T...t..........::..........t...T",
        "T..............::..............T",
        "T........######::######........T",
        "T.*......##############......*.T",
        "T........##############........T",
        "T........##############:::::::.T",
        "T.t......##############:::::::.T",
        "T........##############........T",
        "T........##############........T",
        "T........######::######.......tT",
        "T....t.........::.........*....T",
        "T..............::..............T",
        "T.*............::..........t...T",
        "T..............::..............T",
        "T...t..........::....*.........T",
        "T..............::..............T",
        "T...*..........::.......t......T",
        "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
    };

    protected override void Build()
    {
        LoadLayout(Layout);

        // Puits au centre de la place (2x2)
        AddProp("Well", Art.Well(), new Vector2I(15, 11), new Vector2I(2, 2));

        // Étals : le marchand se tient sur la case au-dessus du comptoir (3 cases).
        AddStall("StallEmile", new Vector2I(9, 7), new Color("e05048"), "emile");
        AddStall("StallJeanne", new Vector2I(20, 7), new Color("48a860"), "jeanne");

        // Tableau des requêtes, gardé par Martin
        AddProp("Board", Art.Board(), new Vector2I(12, 6), new Vector2I(1, 1));
        AddInteractable(new Vector2I(12, 6), new Examinable("Lire", "Tableau des requêtes : rien pour l'instant. Martin le surveille."));

        // Base du joueur (4x3), la porte est la case du bas au centre-gauche
        AddProp("House", Art.House(), new Vector2I(14, 18), new Vector2I(4, 3));
        var door = new Vector2I(15, 20);
        Map.Block(door, false);
        AddDoor(door, "base", "entrance");

        // Portail de l'est (2x2), verrouillé
        AddProp("Gate", Art.Gate(), new Vector2I(29, 10), new Vector2I(2, 2));
        AddInteractable(new Vector2I(29, 10), new Examinable("Pousser", "Le portail est verrouillé. Derrière, la forêt, et les galeries dont parle Martin."));
        AddInteractable(new Vector2I(30, 10), new Examinable("Pousser", "Le portail est verrouillé. Derrière, la forêt, et les galeries dont parle Martin."));

        Spawns["start"] = new Vector2I(15, 14);
        Spawns["from_base"] = new Vector2I(15, 21);
        Spawns["near_emile"] = new Vector2I(10, 10);
        Spawns["near_jeanne"] = new Vector2I(21, 10);
    }

    private void AddStall(string name, Vector2I counter, Color accent, string ownerId)
    {
        // Texture 48x56 : auvent en haut, comptoir sur la rangée `counter` (3 cases).
        AddProp(name, Art.Stall(accent), counter, new Vector2I(3, 1));
        for (int i = 0; i < 3; i++)
            AddInteractable(counter + new Vector2I(i, 0), new Counter(ownerId));
    }
}
