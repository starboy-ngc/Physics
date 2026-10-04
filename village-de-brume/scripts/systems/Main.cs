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
        var zoneRoot = GetNode<Node3D>("ZoneRoot");
        var player = GetNode<Player>("Player");
        var camera = GetNode<FollowCamera>("FollowCamera");
        var ui = GetNode<GameUI>("GameUI");
        ui.BindPlayer(player);
        AddChild(new DirectionalLight3D
        {
            Name = "Sun",
            RotationDegrees = new Vector3(-55, -35, 0),
            LightEnergy = 0.7f,
            ShadowEnabled = true,
        });
        Game.Instance.Setup(zoneRoot, player, camera);
        _ = Game.Instance.ChangeZone("house_player", "start", true);
    }
}
