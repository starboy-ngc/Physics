using Godot;

namespace VillageDeBrume.Tests;

/// <summary>
/// Le joueur part de sa maison, marche jusqu'à la porte de sortie et doit se
/// retrouver dans le village ; puis il remonte et doit rentrer.
/// </summary>
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
                // Depuis "start" (x=96) : se décaler vers la porte (x=128) puis descendre.
                HoldOnly(p.GlobalPosition.X < 127f ? "move_right" : "move_down");
                if (Game.CurrentZoneId == "village")
                {
                    ReleaseAll();
                    Log($"sortie de la maison OK -> village, joueur={p.GlobalPosition}");
                    _phase = 1;
                    _phaseStart = Frame;
                }
                else if (Frame - _phaseStart > 600)
                    Finish($"le joueur n'a pas atteint la porte de sortie (pos {p.GlobalPosition})");
                break;
            case 1:
                // Attendre la fin de la transition (fondu).
                if (Frame - _phaseStart > 30)
                {
                    _phase = 2;
                    _phaseStart = Frame;
                }
                break;
            case 2:
                HoldOnly("move_up");
                if (Game.CurrentZoneId == "house_player")
                {
                    ReleaseAll();
                    Log($"retour dans la maison OK, joueur={p.GlobalPosition}");
                    Finish();
                }
                else if (Frame - _phaseStart > 600)
                    Finish("le joueur n'a pas pu rentrer dans la maison");
                break;
        }
    }
}
