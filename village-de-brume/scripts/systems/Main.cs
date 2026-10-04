using Godot;

namespace VillageDeBrume;

/// <summary>
/// Scène principale : joueur persistant, conteneur de zones, caméra, lumière,
/// interfaces. Le jeu commence dans la maison du joueur. Reçoit les actions
/// demandées par les dialogues (boutique, dépôt) et ouvre l'interface voulue.
/// </summary>
public partial class Main : Node
{
    private ShopUI _shop = null!;
    private StorageUI _storage = null!;

    public override void _Ready()
    {
        var zoneRoot = GetNode<Node3D>("ZoneRoot");
        var player = GetNode<Player>("Player");
        var camera = GetNode<FollowCamera>("FollowCamera");
        var ui = GetNode<GameUI>("GameUI");
        _shop = GetNode<ShopUI>("ShopUI");
        _storage = GetNode<StorageUI>("StorageUI");
        ui.BindPlayer(player);
        AddChild(new DirectionalLight3D
        {
            Name = "Sun",
            RotationDegrees = new Vector3(-50, -30, 0),
            LightColor = new Color(0.96f, 0.94f, 0.88f),
            LightEnergy = 0.55f,
            ShadowEnabled = true,
        });
        DialogueManager.Instance.ActionRequested += OnDialogueAction;
        Game.Instance.Setup(zoneRoot, player, camera);
        _ = Game.Instance.ChangeZone("house_player", "start", true);
    }

    public override void _ExitTree()
    {
        DialogueManager.Instance.ActionRequested -= OnDialogueAction;
    }

    private void OnDialogueAction(string action, string speakerId)
    {
        switch (action)
        {
            case "shop":
                if (NpcManager.Instance.Npcs.TryGetValue(speakerId, out var merchant) && merchant.Shop != null)
                    _shop.OpenFor(merchant);
                else
                    GD.PushWarning($"Action 'shop' : '{speakerId}' n'a pas de boutique.");
                break;
            case "storage":
                _storage.Open();
                break;
            default:
                GD.PushWarning($"Action de dialogue inconnue : '{action}'");
                break;
        }
    }
}
