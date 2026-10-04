using Godot;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace VillageDeBrume;

/// <summary>Un choix proposé au joueur dans un noeud de dialogue.</summary>
public class DialogueChoice
{
    [JsonPropertyName("text")] public string Text { get; set; } = "...";
    [JsonPropertyName("next")] public string? Next { get; set; }
}

/// <summary>Un noeud : une réplique, puis soit une suite, soit des choix. Sans suite = fin.</summary>
public class DialogueNode
{
    [JsonPropertyName("text")] public string Text { get; set; } = "";
    [JsonPropertyName("next")] public string? Next { get; set; }
    [JsonPropertyName("choices")] public List<DialogueChoice>? Choices { get; set; }

    [JsonIgnore] public bool HasChoices => Choices != null && Choices.Count > 0;
}

/// <summary>
/// Un dialogue statique chargé depuis un fichier JSON (voir data/dialogues/*.json).
/// </summary>
public class DialogueData
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("start")] public string StartNode { get; set; } = "start";
    [JsonPropertyName("nodes")] public Dictionary<string, DialogueNode> Nodes { get; set; } = new();

    private static readonly JsonSerializerOptions Options = new()
    {
        PropertyNameCaseInsensitive = true,
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
    };

    public static DialogueData? LoadFromFile(string path)
    {
        if (!FileAccess.FileExists(path))
        {
            GD.PushError($"Dialogue introuvable : {path}");
            return null;
        }
        DialogueData? data;
        try
        {
            data = JsonSerializer.Deserialize<DialogueData>(FileAccess.GetFileAsString(path), Options);
        }
        catch (JsonException e)
        {
            GD.PushError($"Dialogue invalide (JSON) : {path} — {e.Message}");
            return null;
        }
        if (data == null)
            return null;
        if (string.IsNullOrEmpty(data.Id))
            data.Id = path.GetFile().GetBaseName();
        if (!data.Nodes.ContainsKey(data.StartNode))
        {
            GD.PushError($"Dialogue '{data.Id}' : noeud de départ '{data.StartNode}' absent.");
            return null;
        }
        return data;
    }

    public bool HasNode(string id) => Nodes.ContainsKey(id);
    public DialogueNode GetNode(string id) => Nodes[id];
}
