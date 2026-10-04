using Godot;

namespace VillageDeBrume.Tests;

/// <summary>
/// Hub : parle à Émile, choisit « Qu'est-ce que tu vends ? », la boutique
/// s'ouvre après le texte ; achète une pomme, vend un pain ; puis le dépôt de
/// Jeanne : dépose la lettre, la retire. Vérifie pièces, inventaire, verrou.
/// </summary>
public partial class HubTest : TestBase
{
    protected override string Tag => "hub";
    private int _phase;
    private int _phaseStart;
    private ShopUI Shop => GetNode<ShopUI>("Main/ShopUI");
    private StorageUI Storage => GetNode<StorageUI>("Main/StorageUI");

    protected override void Step()
    {
        var inv = Inventory.Instance;
        var player = Game.Player;
        int off = Frame - _phaseStart;
        switch (_phase)
        {
            case 0:
                _ = Game.ChangeZone("village", "near_emile", true);
                if (inv.Coins != 300) Fail($"pièces de départ : {inv.Coins}");
                Next();
                break;
            case 1: // avancer vers l'étal jusqu'à l'invite
                HoldOnly("move_up");
                if (player.Focused is Counter) { ReleaseAll(); Next(); }
                else if (off > 300) Finish($"comptoir non détecté (case {player.Tile})");
                break;
            case 2: // E : dialogue, premier choix = boutique
                if (Dialogue.IsActive) Next();
                else if (off % 5 == 0) PressOnce("interact");
                else if (off > 60) Finish("le dialogue n'a pas démarré");
                break;
            case 3: // valider le 1er choix (boutique), puis avancer -> action
                if (off == 4) PressOnce("interact");
                if (off == 12) PressOnce("interact");
                if (Shop.IsOpen) { Log("boutique ouverte après le dialogue"); Next(); }
                else if (off > 60) Finish($"la boutique ne s'est pas ouverte (dialogue actif : {Dialogue.IsActive})");
                break;
            case 4: // acheter l'entrée n°2 (pomme)
                if (off == 1 && !player.Locked) Fail("le joueur devrait être immobilisé pendant la boutique");
                if (off == 2) PressOnce("move_down");
                if (off == 6) PressOnce("interact");
                if (off == 10)
                {
                    if (inv.Count("apple") != 1 || inv.Coins != 285) Fail($"achat raté : pommes={inv.Count("apple")} pièces={inv.Coins}");
                    else Log("pomme achetée, 285 pièces");
                    PressOnce("move_right"); // onglet Vendre
                }
                if (off == 14) PressOnce("move_down"); // 2e entrée : la lettre (invendable) -> on descend encore
                if (off == 18) PressOnce("move_down"); // 3e : pain
                if (off == 22) PressOnce("interact");
                if (off == 26)
                {
                    if (inv.Count("bread") != 1 || inv.Coins != 290) Fail($"vente ratée : pains={inv.Count("bread")} pièces={inv.Coins}");
                    else Log("pain vendu, 290 pièces");
                    PressOnce("menu"); // fermer
                }
                if (off == 30)
                {
                    if (Shop.IsOpen || player.Locked) Fail("la boutique ne s'est pas fermée");
                    Next();
                }
                break;
            case 5: // dépôt direct (l'accès par dialogue est le même mécanisme que la boutique)
                Storage.Open();
                if (off == 0) break;
                Next();
                break;
            case 6:
                if (off == 2) PressOnce("move_down"); // 2e pile : lettre
                if (off == 6) PressOnce("interact");
                if (off == 10)
                {
                    if (inv.Count("letter") != 0 || inv.StoredCount("letter") != 1) Fail("dépôt de la lettre raté");
                    else Log("lettre déposée");
                    PressOnce("move_right"); // Retirer
                }
                if (off == 14) PressOnce("interact");
                if (off == 18)
                {
                    if (inv.Count("letter") != 1 || inv.StoredCount("letter") != 0) Fail("retrait de la lettre raté");
                    else Log("lettre retirée");
                    PressOnce("menu");
                }
                if (off == 22)
                {
                    if (Storage.IsOpen || player.Locked) Fail("le dépôt ne s'est pas fermé");
                    Finish();
                }
                break;
        }
    }

    private void Next() { _phase++; _phaseStart = Frame; }
}
