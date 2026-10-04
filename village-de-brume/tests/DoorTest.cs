using Godot;

namespace VillageDeBrume.Tests;

/// <summary>Depuis la base, marche jusqu'au paillasson : arrivée au village ; puis remonte dans la base.</summary>
public partial class DoorTest : TestBase
{
    protected override string Tag => "door";
    private int _phase;
    private int _phaseStart;

    protected override void Step()
    {
        var p = Game.Player;
        switch (_phase)
        {
            case 0:
                // "start" = (4,6) ; le paillasson est en (6,8) : droite puis bas.
                HoldOnly(p.Tile.X < 6 ? "move_right" : "move_down");
                if (Game.CurrentZoneId == "orion")
                {
                    ReleaseAll();
                    Log($"sortie de la maison OK -> village, case={p.Tile}");
                    _phase = 1; _phaseStart = Frame;
                }
                else if (Frame - _phaseStart > 600) Finish($"le joueur n'a pas atteint la sortie (case {p.Tile})");
                break;
            case 1:
                if (Frame - _phaseStart > 30) { _phase = 2; _phaseStart = Frame; }
                break;
            case 2:
                HoldOnly("move_up");
                if (Game.CurrentZoneId == "home")
                {
                    ReleaseAll();
                    Log($"retour dans la maison OK, case={p.Tile}");
                    Finish();
                }
                else if (Frame - _phaseStart > 600) Finish("le joueur n'a pas pu rentrer dans la maison");
                break;
        }
    }
}
