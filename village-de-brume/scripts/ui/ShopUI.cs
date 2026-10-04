using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>Boutique d'un marchand : onglet Acheter (stock du PNJ) et Vendre (inventaire du joueur).</summary>
public partial class ShopUI : ListPanelUI
{
    private string _merchantName = "Boutique";
    private List<ShopEntry> _stock = new();

    protected override string Title => _merchantName;
    protected override string[] Tabs => new[] { "Acheter", "Vendre" };
    protected override string Header => $"{Inventory.Instance.Coins} KP";

    public void OpenFor(NpcData merchant)
    {
        _merchantName = $"Étal de {merchant.Name}";
        _stock = merchant.Shop ?? new List<ShopEntry>();
        Open();
    }

    private int PriceOf(ShopEntry e) => e.Price ?? Inventory.Instance.GetDef(e.Id)?.Price ?? 0;

    protected override List<Entry> GetEntries()
    {
        var inv = Inventory.Instance;
        var list = new List<Entry>();
        if (TabIndex == 0)
        {
            foreach (var e in _stock)
            {
                var def = inv.GetDef(e.Id);
                if (def == null) continue;
                int price = PriceOf(e);
                list.Add(new Entry(def.Name, $"{price} KP", inv.Coins >= price, def.Description));
            }
        }
        else
        {
            foreach (var s in inv.Stacks)
            {
                var def = inv.GetDef(s.Id);
                if (def == null) continue;
                string right = def.Price > 0 ? $"{def.SellPrice} KP" + (s.Count > 1 ? $" x{s.Count}" : "") : "—";
                list.Add(new Entry(def.Name, right, def.Price > 0, def.Price > 0 ? def.Description : "Cet objet ne se vend pas."));
            }
        }
        return list;
    }

    protected override void Confirm(int index)
    {
        var inv = Inventory.Instance;
        if (TabIndex == 0)
        {
            var e = _stock[index];
            var def = inv.GetDef(e.Id)!;
            Feedback(inv.Buy(e.Id, PriceOf(e)) ? $"Acheté : {def.Name}." : "Pas assez de KP.");
        }
        else
        {
            var stack = inv.Stacks[index];
            var def = inv.GetDef(stack.Id)!;
            Feedback(inv.Sell(stack.Id) ? $"Vendu : {def.Name} (+{def.SellPrice} KP)." : "Impossible de vendre cet objet.");
        }
    }
}
