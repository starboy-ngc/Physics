using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace VillageDeBrume;

/// <summary>Fiche d'un PNJ (data/npcs/*.json).</summary>
public class NpcData
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("name")] public string Name { get; set; } = "???";
    [JsonPropertyName("role")] public string Role { get; set; } = "";
    [JsonPropertyName("personality")] public List<string> Personality { get; set; } = new();
    [JsonPropertyName("appearance")] public Dictionary<string, string> Appearance { get; set; } = new();
    [JsonPropertyName("location")] public NpcLocation Location { get; set; } = new();
    [JsonPropertyName("wander_radius")] public float WanderRadius { get; set; }
    [JsonPropertyName("dialogue")] public string Dialogue { get; set; } = "";
    /// <summary>Objets en vente (prix pris dans la définition de l'objet sauf si précisé).</summary>
    [JsonPropertyName("shop")] public List<ShopEntry>? Shop { get; set; }
}

public class ShopEntry
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("price")] public int? Price { get; set; }
}

public class NpcLocation
{
    [JsonPropertyName("zone")] public string Zone { get; set; } = "";
    [JsonPropertyName("position")] public float[] Position { get; set; } = { 0, 0 };
    [JsonPropertyName("facing")] public string Facing { get; set; } = "down";
}
