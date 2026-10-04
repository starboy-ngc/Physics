using Godot;

namespace VillageDeBrume.Tests;

/// <summary>
/// Va au bord de l'étang, lance la ligne (E), attend la touche, ferre (E) :
/// une prise doit arriver dans l'inventaire et le joueur doit être libéré.
/// </summary>
public partial class FishingTest : TestBase
{
    protected override string Tag => "fishing";
    private int _phase;
    private int _phaseStart;
    private int _stacksBefore;
    private FishingSpot? _spot;

    protected override void Step()
    {
        var player = Game.Player;
        switch (_phase)
        {
            case 0:
                _ = Game.ChangeZone("village", "near_pond", true);
                _spot = Game.CurrentZone!.GetNode<Pond>("Pond").Spot;
                _spot.BiteDelayRange = new Vector2(0.4f, 0.4f); // test rapide et déterministe
                if (Inventory.Instance.Count("rod") == 0) Fail("pas de canne à pêche au départ");
                _phase = 1; _phaseStart = Frame;
                break;
            case 1:
                HoldOnly("move_up"); // vers l'étang (-Z)
                if (player.Focused is FishingSpot)
                {
                    ReleaseAll();
                    Log($"invite : E — {player.Focused.Prompt}");
                    _stacksBefore = Inventory.Instance.Stacks.Count;
                    _phase = 2; _phaseStart = Frame;
                }
                else if (Frame - _phaseStart > 300)
                    Finish($"l'étang n'est pas détecté (pos {player.GlobalPosition})");
                break;
            case 2:
                PressOnce("interact");
                _phase = 3; _phaseStart = Frame;
                break;
            case 3:
                if (_spot!.State == FishingSpot.FishingState.Waiting && !player.Locked) Fail("le joueur devrait être immobilisé");
                if (_spot.State == FishingSpot.FishingState.Bite)
                {
                    Log("ça mord, on ferre");
                    PressOnce("interact");
                    _phase = 4; _phaseStart = Frame;
                }
                else if (Frame - _phaseStart > 240)
                    Finish($"pas de touche (état {_spot.State})");
                break;
            case 4:
                if (_spot!.LastCatch != null)
                {
                    int caught = Inventory.Instance.Count(_spot.LastCatch);
                    Log($"prise : {Inventory.Instance.GetDef(_spot.LastCatch)?.Name} (x{caught})");
                    if (caught < 1) Fail("la prise n'est pas dans l'inventaire");
                    if (player.Locked) Fail("le joueur est resté immobilisé");
                    Finish();
                }
                else if (Frame - _phaseStart > 60)
                    Finish("le ferrage n'a rien donné");
                break;
        }
    }
}
