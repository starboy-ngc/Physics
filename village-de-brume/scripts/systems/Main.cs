using Godot;

namespace VillageDeBrume;

/// <summary>
/// Scène principale : contient le joueur (persistant), le conteneur de zones
/// et l'interface. Le jeu commence dans la maison du joueur.
/// </summary>
public partial class Main : Node
{
    public override void _Ready()
    {
        var zoneRoot = GetNode<Node2D>("ZoneRoot");
        var player = GetNode<Player>("Player");
        var ui = GetNode<GameUI>("GameUI");
        ui.BindPlayer(player);
        Game.Instance.Setup(zoneRoot, player);
        _ = Game.Instance.ChangeZone("house_player", "start", true);
    }
}
