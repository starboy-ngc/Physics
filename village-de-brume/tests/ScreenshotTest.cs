using Godot;

namespace VillageDeBrume.Tests;

/// <summary>
/// Capture d'écran de chaque zone (nécessite un affichage, ex. xvfb-run) :
///   godot --path . tests/ScreenshotTest.tscn -- /dossier/de/sortie
/// </summary>
public partial class ScreenshotTest : TestBase
{
    protected override string Tag => "shot";

    private static readonly (string zone, string spawn)[] Shots =
    {
        ("house_player", "start"),
        ("village", "from_house_player"),
        ("village", "start"),
        ("bakery", "entrance"),
        ("bakery", "dialogue"),
        ("village", "fishing"),
        ("village", "menu"),
        ("house_jeanne", "entrance"),
        ("house_martin", "entrance"),
    };

    private string _outDir = "user://screenshots";
    private int _index = -1;

    public override void _Ready()
    {
        base._Ready();
        var args = OS.GetCmdlineUserArgs();
        if (args.Length > 0)
            _outDir = args[0];
        DirAccess.MakeDirRecursiveAbsolute(_outDir);
    }

    protected override void Step()
    {
        if (Frame % 20 == 10 && _index + 1 < Shots.Length)
        {
            _index++;
            var (zone, spawn) = Shots[_index];
            if (spawn == "fishing")
            {
                _ = Game.ChangeZone("village", "near_pond", true);
                Game.Player.GlobalPosition = new Vector3(30, 0, 31.8f);
                Game.Player.Face(CharacterVisual.Facing.Up);
                Game.CurrentZone!.GetNode<Pond>("Pond").Spot.Interact(Game.Player);
            }
            else if (spawn == "menu")
            {
                _ = Game.ChangeZone("village", "start", true);
                GetNode<MenuUI>("Main/MenuUI").Open();
            }
            else if (spawn == "dialogue")
            {
                // Même zone : on déclenche le dialogue avec le PNJ présent.
                if (Game.CurrentZone?.GetNodeOrNull<Npc>("NPC_emile") is { } npc)
                {
                    Game.Player.GlobalPosition = new Vector3(9, 0, 7);
                    Game.Player.Face(CharacterVisual.Facing.Up);
                    npc.OnInteract(Game.Player);
                }
            }
            else
                _ = Game.ChangeZone(zone, spawn, true);
        }
        else if (Frame % 20 == 0 && _index >= 0)
        {
            if (Dialogue.IsActive && (_index + 1 >= Shots.Length || Shots[_index + 1].spawn != "dialogue"))
                Dialogue.End();
            var menu = GetNode<MenuUI>("Main/MenuUI");
            if (menu.IsOpen && Shots[_index].spawn != "menu")
                menu.Close();
            var img = GetViewport().GetTexture().GetImage();
            string path = $"{_outDir}/{_index:00}_{Shots[_index].zone}_{Shots[_index].spawn}.png";
            img.SavePng(path);
            Log(path);
            if (menu.IsOpen) menu.Close();
            if (_index + 1 >= Shots.Length)
                Finish();
        }
    }
}
