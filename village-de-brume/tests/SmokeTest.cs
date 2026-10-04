using Godot;

namespace VillageDeBrume.Tests;

/// <summary>Visite toutes les zones et vérifie le placement du joueur et des PNJ.</summary>
public partial class SmokeTest : TestBase
{
    protected override string Tag => "smoke";

    private static readonly (string zone, string spawn)[] Steps =
    {
        ("village", "from_house_player"),
        ("bakery", "entrance"),
        ("village", "from_bakery"),
        ("house_jeanne", "entrance"),
        ("village", "from_house_jeanne"),
        ("house_martin", "entrance"),
        ("village", "from_house_martin"),
        ("house_player", "entrance"),
    };

    private int _step;

    protected override void Step()
    {
        if (Frame % 5 != 0)
            return;
        if (_step == 0)
        {
            if (NpcManager.Instance.Npcs.Count == 0)
                Fail("aucune fiche PNJ chargée");
            CheckZone("house_player", "start");
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
        if (zone == null || Game.CurrentZoneId != zoneId)
        {
            Fail($"zone attendue '{zoneId}', obtenue '{Game.CurrentZoneId}'");
            return;
        }
        var player = Game.Player;
        if (player.GetParent() != zone)
            Fail($"le joueur n'est pas dans la zone '{zoneId}'");
        Vector2 expected = zone.GetSpawnPosition(spawnName);
        if (player.GlobalPosition.DistanceTo(expected) > 0.5f)
            Fail($"position du joueur {player.GlobalPosition} != spawn {expected} dans '{zoneId}'");
        if (!zone.Bounds.HasPoint(player.GlobalPosition))
            Fail($"le joueur est hors des limites de '{zoneId}'");
        if (zone.GetNodeOrNull("Boundaries") == null)
            Fail($"pas de murs invisibles dans '{zoneId}'");
        foreach (var id in NpcManager.Instance.Npcs.Keys)
        {
            bool expectedHere = NpcManager.Instance.GetZoneOf(id) == zoneId;
            bool present = zone.GetNodeOrNull("NPC_" + id) != null;
            if (expectedHere != present)
                Fail($"PNJ '{id}' : attendu={expectedHere} présent={present} dans '{zoneId}'");
        }
        Log($"{zoneId,-14} spawn={spawnName,-18} joueur={player.GlobalPosition}");
    }
}
