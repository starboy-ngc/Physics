using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>Dépôt : onglet Déposer (inventaire -> dépôt) et Retirer (dépôt -> inventaire), une unité par validation.</summary>
public partial class StorageUI : ListPanelUI
{
    protected override string Title => "Dépôt de Jeanne";
    protected override string[] Tabs => new[] { "Déposer", "Retirer" };
    protected override string Header => $"{Inventory.Instance.Storage.Count} pile(s) au dépôt";

    protected override List<Entry> GetEntries()
    {
        var inv = Inventory.Instance;
        var list = new List<Entry>();
        foreach (var s in TabIndex == 0 ? inv.Stacks : inv.Storage)
        {
            var def = inv.GetDef(s.Id);
            if (def == null) continue;
            list.Add(new Entry(def.Name, s.Count > 1 ? $"x{s.Count}" : "", true, def.Description));
        }
        return list;
    }

    protected override void Confirm(int index)
    {
        var inv = Inventory.Instance;
        if (TabIndex == 0)
        {
            var stack = inv.Stacks[index];
            Feedback(inv.Deposit(stack.Id) ? $"Déposé : {inv.GetDef(stack.Id)?.Name}." : "Impossible.");
        }
        else
        {
            var stack = inv.Storage[index];
            Feedback(inv.Withdraw(stack.Id) ? $"Retiré : {inv.GetDef(stack.Id)?.Name}." : "Impossible.");
        }
    }
}
