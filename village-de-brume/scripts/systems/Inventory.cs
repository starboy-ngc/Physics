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
        var def = GetDef(id);
        if (def == null || count <= 0)
        {
            GD.PushWarning($"Inventory.Add : objet inconnu '{id}'");
            return false;
        }
        if (def.Stackable)
        {
            var existing = Stacks.Find(s => s.Id == id);
            if (existing != null) existing.Count += count;
            else Stacks.Add(new ItemStack { Id = id, Count = count });
        }
        else
        {
            for (int i = 0; i < count; i++)
                Stacks.Add(new ItemStack { Id = id, Count = 1 });
        }
        Changed?.Invoke();
        return true;
    }

    public bool Remove(string id, int count = 1)
    {
        if (Count(id) < count)
            return false;
        for (int i = Stacks.Count - 1; i >= 0 && count > 0; i--)
        {
            if (Stacks[i].Id != id) continue;
            int take = Math.Min(count, Stacks[i].Count);
            Stacks[i].Count -= take;
            count -= take;
            if (Stacks[i].Count <= 0) Stacks.RemoveAt(i);
        }
        Changed?.Invoke();
        return true;
    }
}
