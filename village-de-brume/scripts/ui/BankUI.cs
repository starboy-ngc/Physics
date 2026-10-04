using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>Banque de Solveig : déposer ou retirer des KP par paliers.</summary>
public partial class BankUI : ListPanelUI
{
    private static readonly int[] Amounts = { 10, 50, 100, 500 };

    protected override string Title => "Banque d'Orion";
    protected override string[] Tabs => new[] { "Déposer", "Retirer" };
    protected override string Header => $"{Inventory.Instance.Coins} KP sur toi · {Inventory.Instance.BankBalance} KP en banque";

    protected override List<Entry> GetEntries()
    {
        var inv = Inventory.Instance;
        var list = new List<Entry>();
        int available = TabIndex == 0 ? inv.Coins : inv.BankBalance;
        foreach (int a in Amounts)
            list.Add(new Entry($"{a} KP", "", available >= a, TabIndex == 0 ? "Confier des KP à Solveig." : "Reprendre des KP."));
        list.Add(new Entry("Tout", $"{available} KP", available > 0, TabIndex == 0 ? "Tout déposer." : "Tout retirer."));
        return list;
    }

    protected override void Confirm(int index)
    {
        var inv = Inventory.Instance;
        int amount = index < Amounts.Length ? Amounts[index] : (TabIndex == 0 ? inv.Coins : inv.BankBalance);
        bool ok = TabIndex == 0 ? inv.DepositCoins(amount) : inv.WithdrawCoins(amount);
        Feedback(ok ? (TabIndex == 0 ? $"Déposé : {amount} KP." : $"Retiré : {amount} KP.") : "Montant indisponible.");
    }
}
