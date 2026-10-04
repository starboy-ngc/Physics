using Godot;
using System.Collections.Generic;
using System.Text.Json;

namespace VillageDeBrume;

/// <summary>
/// Autoload "NpcManager" : charge les fiches PNJ (data/npcs/*.json) et fait
/// apparaître, dans chaque zone chargée, les PNJ qui s'y trouvent.
/// Les PNJ ne sont pas placés dans les scènes de zone : leur position est une
/// donnée de jeu (aujourd'hui fixe, demain calculée par les horaires).
/// </summary>
public partial class NpcManager : Node
{
    public static NpcManager Instance { get; private set; } = null!;

    private const string NpcDir = "res://data/npcs";
    private PackedScene _npcScene = null!;

    /// <summary>id -> fiche</summary>
    public Dictionary<string, NpcData> Npcs { get; } = new();
    /// <summary>id -> emplacement courant</summary>
    public Dictionary<string, NpcLocation> Locations { get; } = new();
    /// <summary>id -> instance dans la zone courante (si présent)</summary>
    public Dictionary<string, Npc> Instances { get; } = new();

    private static readonly JsonSerializerOptions Options = new()
    {
        PropertyNameCaseInsensitive = true,
        AllowTrailingCommas = true,
    };

    public override void _EnterTree()
    {
        Instance = this;
    }

    public override void _Ready()
    {
        _npcScene = GD.Load<PackedScene>("res://scenes/npc/NPC.tscn");
        LoadAll();
        Game.Instance.ZoneChanged += OnZoneChanged;
    }

    private void LoadAll()
    {
        Npcs.Clear();
        Locations.Clear();
        using var dir = DirAccess.Open(NpcDir);
        if (dir == null)
        {
            GD.PushWarning($"Dossier PNJ introuvable : {NpcDir}");
            return;
        }
        var files = new List<string>(dir.GetFiles());
        files.Sort();
        foreach (var f in files)
        {
            if (!f.EndsWith(".json"))
                continue;
            string path = $"{NpcDir}/{f}";
            NpcData? data = null;
            try
            {
                data = JsonSerializer.Deserialize<NpcData>(FileAccess.GetFileAsString(path), Options);
            }
            catch (JsonException e)
            {
                GD.PushError($"Fiche PNJ invalide : {path} — {e.Message}");
            }
            if (data == null || string.IsNullOrEmpty(data.Id))
            {
                GD.PushError($"Fiche PNJ invalide : {path}");
                continue;
            }
            Npcs[data.Id] = data;
            Locations[data.Id] = data.Location;
        }
    }

    public string GetNpcName(string id) => Npcs.TryGetValue(id, out var d) ? d.Name : id;

    public string GetZoneOf(string id) => Locations.TryGetValue(id, out var l) ? l.Zone : "";

    private void OnZoneChanged(Zone zone)
    {
        Instances.Clear();
        foreach (var (id, data) in Npcs)
        {
            var loc = Locations[id];
            if (loc.Zone != Game.Instance.CurrentZoneId)
                continue;
            var npc = _npcScene.Instantiate<Npc>();
            npc.Name = "NPC_" + id;
            npc.Position = new Vector2(loc.Position[0], loc.Position[1]);
            npc.FacingDirection = CharacterVisual.FacingFromString(loc.Facing);
            zone.AddChild(npc);
            npc.ApplyData(data);
            Instances[id] = npc;
        }
    }
}
