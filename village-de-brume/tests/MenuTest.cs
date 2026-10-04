using Godot;

namespace VillageDeBrume.Tests;

/// <summary>Ouvre le menu, parcourt l'inventaire, revient et ferme ; le jeu doit être en pause pendant ce temps.</summary>
public partial class MenuTest : TestBase
{
    protected override string Tag => "menu";
    private int _phase;
    private MenuUI Menu => GetNode<MenuUI>("Main/MenuUI");

    protected override void Step()
    {
        if (Frame % 6 != 0)
            return;
        var inv = Inventory.Instance;
        switch (_phase)
        {
            case 0:
                if (inv.Stacks.Count < 3) Fail($"inventaire de départ incomplet ({inv.Stacks.Count} piles)");
                if (inv.Count("bread") != 2) Fail("le pain devrait être empilé x2");
                PressOnce("menu");
                break;
            case 1:
                if (!Menu.IsOpen) { Finish("le menu ne s'est pas ouvert"); return; }
                if (!GetTree().Paused) Fail("le jeu n'est pas en pause");
                Log("menu ouvert, jeu en pause");
                PressOnce("interact"); // entrer dans l'inventaire
                break;
            case 2:
                if (!Menu.InContent) Fail("l'inventaire n'a pas pris le focus");
                PressOnce("move_down");
                break;
            case 3:
                if (Menu.ItemIndex != 1) Fail($"index d'objet attendu 1, obtenu {Menu.ItemIndex}");
                Log($"objet sélectionné : {inv.GetDef(inv.Stacks[Menu.ItemIndex].Id)?.Name}");
                PressOnce("move_left"); // retour aux onglets
                break;
            case 4:
                if (Menu.InContent) Fail("le retour aux onglets a échoué");
                PressOnce("move_down");
                break;
            case 5:
                if (Menu.TabIndex != 1) Fail($"onglet attendu 1, obtenu {Menu.TabIndex}");
                PressOnce("menu"); // fermer
                break;
            case 6:
                if (Menu.IsOpen) Fail("le menu ne s'est pas fermé");
                if (GetTree().Paused) Fail("le jeu est resté en pause");
                Log("menu fermé, jeu repris");
                Finish();
                return;
        }
        _phase++;
    }
}
