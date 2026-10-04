using Godot;

namespace VillageDeBrume.Tests;

/// <summary>Visite les zones et vérifie le placement du joueur et des PNJ sur la grille.</summary>
public partial class SmokeTest : TestBase
{
    protected override string Tag => "smoke";
    private static readonly (string zone, string spawn)[] Steps =
    {
        ("orion", "from_home"), ("orion", "near_birna"), ("orion", "cassegrain"), ("home", "entrance"), ("orion", "start"),
    };
    private int _step;

    protected override void Step()
    {
        if (Frame % 5 != 0) return;
        if (_step == 0)
        {
            if (NpcManager.Instance.Npcs.Count == 0) Fail("aucune fiche PNJ chargée");
            CheckZone("home", "start");
        }
        if (_step < Steps.Length)
        {
            var (zone, spawn) = Steps[_step];
            _ = Game.ChangeZone(zone, spawn, true);
            CheckZone(zone, spawn);
            _step++;
            return;
        }
        Log($"{Steps.Length + 1} zones visitées");
        Finish();
    }

    private void CheckZone(string zoneId, string spawnName)
    {
        var zone = Game.CurrentZone;
        if (zone == null || Game.CurrentZoneId != zoneId) { Fail($"zone attendue '{zoneId}', obtenue '{Game.CurrentZoneId}'"); return; }
        var player = Game.Player;
        if (player.GetParent() != zone) Fail($"le joueur n'est pas dans la zone '{zoneId}'");
        var expected = zone.GetSpawn(spawnName);
        if (player.Tile != expected) Fail($"case du joueur {player.Tile} != spawn {expected} dans '{zoneId}'");
        if (zone.Map.IsBlocked(player.Tile)) Fail($"le joueur apparaît sur une case bloquée dans '{zoneId}'");
        if (zone.Map.GetOccupant(player.Tile) != player) Fail("le joueur n'occupe pas sa case");
        foreach (var id in NpcManager.Instance.Npcs.Keys)
        {
            bool expectedHere = NpcManager.Instance.GetZoneOf(id) == zoneId;
            bool present = zone.GetNodeOrNull("NPC_" + id) != null;
            if (expectedHere != present) Fail($"PNJ '{id}' : attendu={expectedHere} présent={present} dans '{zoneId}'");
        }
        Log($"{zoneId,-8} spawn={spawnName,-12} case={player.Tile}");
    }
}
