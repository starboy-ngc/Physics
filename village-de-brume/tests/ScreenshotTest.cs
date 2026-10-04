using Godot;

namespace VillageDeBrume.Tests;

/// <summary>
/// Capture d'écran de chaque situation (nécessite un affichage, ex. xvfb-run) :
///   godot --path . tests/ScreenshotTest.tscn -- /dossier/de/sortie
/// </summary>
public partial class ScreenshotTest : TestBase
{
    protected override string Tag => "shot";
    private static readonly (string zone, string spawn)[] Shots =
    {
        ("home", "start"), ("orion", "from_home"), ("orion", "start"), ("orion", "dialogue"),
        ("orion", "shop"), ("orion", "cassegrain"), ("orion", "eyvind"), ("orion", "menu"),
    };
    private string _outDir = "user://screenshots";
    private int _index = -1;

    public override void _Ready()
    {
        base._Ready();
        var args = OS.GetCmdlineUserArgs();
        if (args.Length > 0) _outDir = args[0];
        DirAccess.MakeDirRecursiveAbsolute(_outDir);
    }

    protected override void Step()
    {
        var menu = GetNode<MenuUI>("Main/MenuUI");
        var shop = GetNode<ShopUI>("Main/ShopUI");
        if (Frame % 20 == 10 && _index + 1 < Shots.Length)
        {
            _index++;
            var (zone, spawn) = Shots[_index];
            switch (spawn)
            {
                case "dialogue":
                    _ = Game.ChangeZone("orion", "near_birna", true);
                    Game.Player.PlaceAt(Game.CurrentZone!, new Vector2I(10, 8), CharacterSprites.Facing.Up);
                    if (Game.CurrentZone!.GetNodeOrNull<Npc>("NPC_birna") is { } npc) npc.Interact(Game.Player);
                    break;
                case "shop":
                    shop.OpenFor(NpcManager.Instance.Npcs["birna"]);
                    break;
                case "eyvind":
                    _ = Game.ChangeZone("orion", "cassegrain", true);
                    if (Game.CurrentZone!.GetNodeOrNull<Npc>("NPC_eyvind") is { } eyvind) eyvind.Interact(Game.Player);
                    break;
                case "menu":
                    _ = Game.ChangeZone("orion", "start", true);
                    menu.Open();
                    break;
                default:
                    _ = Game.ChangeZone(zone, spawn, true);
                    break;
            }
        }
        else if (Frame % 20 == 0 && _index >= 0)
        {
            var img = GetViewport().GetTexture().GetImage();
            string path = $"{_outDir}/{_index:00}_{Shots[_index].zone}_{Shots[_index].spawn}.png";
            img.SavePng(path);
            Log(path);
            if (Shots[_index].spawn == "shop") shop.Close();
            if (Dialogue.IsActive && (_index + 1 >= Shots.Length || Shots[_index + 1].spawn != "shop")) Dialogue.End();
            if (menu.IsOpen) menu.Close();
            if (_index + 1 >= Shots.Length) Finish();
        }
    }
}
