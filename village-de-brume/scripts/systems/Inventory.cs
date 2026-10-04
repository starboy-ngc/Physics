using Godot;
using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace VillageDeBrume;

/// <summary>Définition d'un objet (data/items/items.json).</summary>
public class ItemDef
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("name")] public string Name { get; set; } = "";
    [JsonPropertyName("description")] public string Description { get; set; } = "";
    [JsonPropertyName("stackable")] public bool Stackable { get; set; } = true;
    /// <summary>Prix d'achat ; 0 = ni achetable ni vendable.</summary>
    [JsonPropertyName("price")] public int Price { get; set; }
    [JsonIgnore] public int SellPrice => Price / 2;
}

public class ItemStack
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("count")] public int Count { get; set; } = 1;
}

internal class ItemsFile
{
    [JsonPropertyName("items")] public List<ItemDef> Items { get; set; } = new();
    [JsonPropertyName("starting_inventory")] public List<ItemStack> StartingInventory { get; set; } = new();
    [JsonPropertyName("starting_coins")] public int StartingCoins { get; set; }
}

/// <summary>
/// Autoload "Inventory" : définitions d'objets et inventaire du joueur.
/// Le moteur est seul à modifier l'inventaire (Add / Remove) ; l'IA ne pourra
/// que proposer (règle 19). Sera sauvegardé à l'étape « sauvegarde ».
/// </summary>
public partial class Inventory : Node
{
    public static Inventory Instance { get; private set; } = null!;
    private const string ItemsPath = "res://data/items/items.json";

    public event Action? Changed;

    public Dictionary<string, ItemDef> Definitions { get; } = new();
    /// <summary>Piles dans l'ordre d'acquisition.</summary>
    public List<ItemStack> Stacks { get; } = new();
    /// <summary>Objets confiés au dépôt (Jeanne).</summary>
    public List<ItemStack> Storage { get; } = new();
    public int Coins { get; private set; }

    public override void _EnterTree()
    {
        Instance = this;
    }

    public override void _Ready()
    {
        if (!FileAccess.FileExists(ItemsPath))
        {
            GD.PushWarning($"Fichier d'objets introuvable : {ItemsPath}");
            return;
        }
        ItemsFile? file = null;
        try
        {
            file = JsonSerializer.Deserialize<ItemsFile>(FileAccess.GetFileAsString(ItemsPath),
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true, AllowTrailingCommas = true });
        }
        catch (JsonException e)
        {
            GD.PushError($"Fichier d'objets invalide : {e.Message}");
        }
        if (file == null)
            return;
        foreach (var def in file.Items)
            Definitions[def.Id] = def;
        foreach (var stack in file.StartingInventory)
            Add(stack.Id, stack.Count);
        Coins = file.StartingCoins;
    }

    // --- Pièces ----------------------------------------------------------------

    public void AddCoins(int amount)
    {
        Coins = Math.Max(0, Coins + amount);
        Changed?.Invoke();
    }

    public bool SpendCoins(int amount)
    {
        if (amount < 0 || Coins < amount)
            return false;
        Coins -= amount;
        Changed?.Invoke();
        return true;
    }

    /// <summary>Achat auprès d'un marchand : vérifie les pièces, ajoute l'objet.</summary>
    public bool Buy(string id, int price)
    {
        if (GetDef(id) == null || !SpendCoins(price))
            return false;
        Add(id, 1);
        return true;
    }

    /// <summary>Vente d'une unité au prix de revente de l'objet.</summary>
    public bool Sell(string id)
    {
        var def = GetDef(id);
        if (def == null || def.Price <= 0 || !Remove(id, 1))
            return false;
        AddCoins(def.SellPrice);
        return true;
    }

    // --- Dépôt -----------------------------------------------------------------

    public bool Deposit(string id, int count = 1)
    {
        if (!Remove(id, count))
            return false;
        AddTo(Storage, id, count);
        Changed?.Invoke();
        return true;
    }

    public bool Withdraw(string id, int count = 1)
    {
        if (!RemoveFrom(Storage, id, count))
            return false;
        Add(id, count);
        return true;
    }

    public int StoredCount(string id)
    {
        int total = 0;
        foreach (var s in Storage)
            if (s.Id == id) total += s.Count;
        return total;
    }

    public ItemDef? GetDef(string id) => Definitions.TryGetValue(id, out var d) ? d : null;

    public int Count(string id)
    {
        int total = 0;
        foreach (var s in Stacks)
            if (s.Id == id) total += s.Count;
        return total;
    }

    public bool Add(string id, int count = 1)
    {
        if (GetDef(id) == null || count <= 0)
        {
            GD.PushWarning($"Inventory.Add : objet inconnu '{id}'");
            return false;
        }
        AddTo(Stacks, id, count);
        Changed?.Invoke();
        return true;
    }

    public bool Remove(string id, int count = 1)
    {
        if (!RemoveFrom(Stacks, id, count))
            return false;
        Changed?.Invoke();
        return true;
    }

    private void AddTo(List<ItemStack> list, string id, int count)
    {
        var def = GetDef(id)!;
        if (def.Stackable)
        {
            var existing = list.Find(s => s.Id == id);
            if (existing != null) existing.Count += count;
            else list.Add(new ItemStack { Id = id, Count = count });
        }
        else
        {
            for (int i = 0; i < count; i++)
                list.Add(new ItemStack { Id = id, Count = 1 });
        }
    }

    private static bool RemoveFrom(List<ItemStack> list, string id, int count)
    {
        int have = 0;
        foreach (var s in list) if (s.Id == id) have += s.Count;
        if (have < count || count <= 0)
            return false;
        for (int i = list.Count - 1; i >= 0 && count > 0; i--)
        {
            if (list[i].Id != id) continue;
            int take = Math.Min(count, list[i].Count);
            list[i].Count -= take;
            count -= take;
            if (list[i].Count <= 0) list.RemoveAt(i);
        }
        return true;
    }
}
