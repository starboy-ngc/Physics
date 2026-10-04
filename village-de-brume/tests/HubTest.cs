using Godot;

namespace VillageDeBrume.Tests;

/// <summary>
/// Hub d'Orion : boutique de Birna par le dialogue (achat, vente), banque de
/// Solveig (dépôt, retrait de KP), coffres de la maison (ranger, prendre).
/// </summary>
public partial class HubTest : TestBase
{
    protected override string Tag => "hub";
    private int _phase;
    private int _phaseStart;
    private ShopUI Shop => GetNode<ShopUI>("Main/ShopUI");
    private StorageUI Storage => GetNode<StorageUI>("Main/StorageUI");
    private BankUI Bank => GetNode<BankUI>("Main/BankUI");

    protected override void Step()
    {
        var inv = Inventory.Instance;
        var player = Game.Player;
        int off = Frame - _phaseStart;
        switch (_phase)
        {
            case 0:
                _ = Game.ChangeZone("orion", "near_birna", true);
                if (inv.Coins != 300) Fail($"KP de départ : {inv.Coins}");
                Next();
                break;
            case 1: // vers le comptoir de Birna
                HoldOnly("move_up");
                if (player.Focused is Counter) { ReleaseAll(); Next(); }
                else if (off > 300) Finish($"comptoir non détecté (case {player.Tile})");
                break;
            case 2:
                if (Dialogue.IsActive) Next();
                else if (off % 5 == 0) PressOnce("interact");
                else if (off > 60) Finish("le dialogue n'a pas démarré");
                break;
            case 3: // 1er choix = boutique, puis le texte -> action
                if (off == 4) PressOnce("interact");
                if (off == 12) PressOnce("interact");
                if (Shop.IsOpen) { Log("échoppe ouverte après le dialogue"); Next(); }
                else if (off > 60) Finish($"l'échoppe ne s'est pas ouverte (dialogue actif : {Dialogue.IsActive})");
                break;
            case 4: // acheter la 2e entrée (pomme), vendre un pain
                if (off == 1 && !player.Locked) Fail("le joueur devrait être immobilisé pendant la boutique");
                if (off == 2) PressOnce("move_down");
                if (off == 6) PressOnce("interact");
                if (off == 10)
                {
                    if (inv.Count("apple") != 2 || inv.Coins != 285) Fail($"achat raté : pommes={inv.Count("apple")} KP={inv.Coins}");
                    else Log("pomme achetée, 285 KP");
                    PressOnce("move_right"); // Vendre
                }
                if (off == 14) PressOnce("move_down"); // 2e pile : pain
                if (off == 18) PressOnce("interact");
                if (off == 22)
                {
                    if (inv.Count("bread") != 1 || inv.Coins != 290) Fail($"vente ratée : pains={inv.Count("bread")} KP={inv.Coins}");
                    else Log("pain vendu, 290 KP");
                    PressOnce("menu");
                }
                if (off == 26)
                {
                    if (Shop.IsOpen || player.Locked) Fail("l'échoppe ne s'est pas fermée");
                    Next();
                }
                break;
            case 5: // banque par l'action de dialogue
                Main.Instance!.RunAction("bank", "solveig");
                if (!Bank.IsOpen) { Finish("la banque ne s'est pas ouverte"); return; }
                Next();
                break;
            case 6:
                if (off == 2) PressOnce("move_down"); // 50 KP
                if (off == 6) PressOnce("interact");
                if (off == 10)
                {
                    if (inv.Coins != 240 || inv.BankBalance != 50) Fail($"dépôt raté : KP={inv.Coins} banque={inv.BankBalance}");
                    else Log("50 KP déposés");
                    PressOnce("move_right"); // Retirer
                }
                if (off == 14) PressOnce("interact"); // 10 KP
                if (off == 18)
                {
                    if (inv.Coins != 250 || inv.BankBalance != 40) Fail($"retrait raté : KP={inv.Coins} banque={inv.BankBalance}");
                    else Log("10 KP retirés");
                    PressOnce("menu");
                }
                if (off == 22) { if (Bank.IsOpen) Fail("la banque ne s'est pas fermée"); Next(); }
                break;
            case 7: // coffres de la maison
                _ = Game.ChangeZone("home", "start", true);
                Game.Player.PlaceAt(Game.CurrentZone!, new Vector2I(8, 3), CharacterSprites.Facing.Up);
                Next();
                break;
            case 8:
                if (off == 2)
                {
                    if (player.Focused is not StorageChest) Fail($"le coffre n'est pas visé ({player.Focused})");
                    PressOnce("interact");
                }
                if (off == 6)
                {
                    if (!Storage.IsOpen) { Finish("le coffre ne s'est pas ouvert"); return; }
                    PressOnce("interact"); // ranger la 1re pile (carte)
                }
                if (off == 10)
                {
                    if (inv.Count("map") != 0 || inv.StoredCount("map") != 1) Fail("rangement de la carte raté");
                    else Log("carte rangée dans le coffre");
                    PressOnce("move_right");
                }
                if (off == 14) PressOnce("interact");
                if (off == 18)
                {
                    if (inv.Count("map") != 1) Fail("reprise de la carte ratée");
                    else Log("carte reprise");
                    PressOnce("menu");
                }
                if (off == 22) { if (Storage.IsOpen || player.Locked) Fail("le coffre ne s'est pas fermé"); Finish(); }
                break;
        }
    }

    private void Next() { _phase++; _phaseStart = Frame; }
}
