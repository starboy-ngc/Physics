using Godot;

namespace VillageDeBrume;

/// <summary>
/// Orion, le village-hub : la mer au nord, la place de basalte autour du puits,
/// l'échoppe de Birna, la banque de Solveig et l'armurerie de Gunnar au nord de
/// la place, la maison au sud, et à l'est le camp de Cassegrain (tentes,
/// longue-vue, Eyvind) devant la palissade.
/// </summary>
public partial class Orion : Zone
{
    public override string ZoneName => "Orion";

    private static readonly string[] Layout =
    {
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "ssssssssssssssssssssssssssssssss",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "T.oB...........................T",
        "T.............L.......L.......PT",
        "T..............................PT",
        "T..............................PT",
        "T........##############......t.PT",
        "T.*......##############.........T",
        "T........##############..L..C..PT",
        "T........##############:::::::..T",
        "T.t......##############:::::::..T",
        "T........##############..C..B..PT",
        "T........##############........PT",
        "T........######::######...t....PT",
        "T....t.........::.........*....PT",
        "T.t............::..............PT",
        "T.*............::..........t...PT",
        "T..............::....*.........PT",
        "T...t..........::..............PT",
        "T......*.......::.......t......PT",
        "T..............::..............PT",
        "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
    };

    protected override void Build()
    {
        LoadLayout(Layout);

        // Puits au centre de la place
        AddProp("Well", Art.Well(), new Vector2I(15, 11), new Vector2I(2, 2));

        // Étals au nord de la place : le marchand se tient sur la case au-dessus du comptoir.
        AddStall("StallBirna", new Vector2I(9, 7), new Color("e05048"), "birna");
        AddStall("StallSolveig", new Vector2I(14, 7), new Color("3a6ab8"), "solveig");
        AddStall("StallGunnar", new Vector2I(19, 7), new Color("6a6a72"), "gunnar");

        // Maison (4x3), la porte est la case du bas au centre-gauche
        AddProp("House", Art.House(), new Vector2I(14, 18), new Vector2I(4, 3));
        var door = new Vector2I(15, 20);
        Map.Block(door, false);
        AddDoor(door, "home", "entrance");

        // Cassegrain : tentes, longue-vue, et l'ouverture de la palissade (verrouillée)
        AddProp("TentA", Art.Tent(new Color("c8a060")), new Vector2I(25, 7), new Vector2I(2, 2));
        AddProp("TentB", Art.Tent(new Color("a06040")), new Vector2I(28, 14), new Vector2I(2, 2));
        AddProp("Telescope", Art.Telescope(), new Vector2I(28, 10), new Vector2I(1, 1));
        AddInteractable(new Vector2I(28, 10), new Examinable("Regarder", "La longue-vue de l'Orion. Au nord, des hauteurs blanches. À l'est, la vallée. Et la nuit, les lumières."));
        AddInteractable(new Vector2I(31, 11), new Examinable("Passer", "L'ouverture de la palissade. Eyvind : « Pas encore. Quand tu seras prêt, je te le dirai. »"));
        AddInteractable(new Vector2I(31, 12), new Examinable("Passer", "L'ouverture de la palissade. Eyvind : « Pas encore. Quand tu seras prêt, je te le dirai. »"));
        Map.Block(new Vector2I(31, 11));
        Map.Block(new Vector2I(31, 12));

        Spawns["start"] = new Vector2I(15, 14);
        Spawns["from_home"] = new Vector2I(15, 21);
        Spawns["near_birna"] = new Vector2I(10, 10);
        Spawns["near_solveig"] = new Vector2I(15, 10);
        Spawns["near_gunnar"] = new Vector2I(20, 10);
        Spawns["cassegrain"] = new Vector2I(26, 12);
    }

    private void AddStall(string name, Vector2I counter, Color accent, string ownerId)
    {
        AddProp(name, Art.Stall(accent), counter, new Vector2I(3, 1));
        for (int i = 0; i < 3; i++)
            AddInteractable(counter + new Vector2I(i, 0), new Counter(ownerId));
    }
}
