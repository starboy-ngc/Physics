using Godot;

namespace VillageDeBrume;

/// <summary>
/// Scène principale : joueur persistant, conteneur de zones, interfaces.
/// Le jeu commence dans la base. Reçoit les actions demandées par les
/// dialogues (boutique, dépôt) et ouvre l'interface voulue.
/// </summary>
public partial class Main : Node
{
    public static Main? Instance { get; private set; }
    private ShopUI _shop = null!;
    private StorageUI _storage = null!;
    private BankUI _bank = null!;

    public override void _Ready()
    {
        var zoneRoot = GetNode<Node2D>("WorldContainer/World/ZoneRoot");
        var player = GetNode<Player>("WorldContainer/World/Player");
        var ui = GetNode<GameUI>("GameUI");
        _shop = GetNode<ShopUI>("ShopUI");
        _storage = GetNode<StorageUI>("StorageUI");
        _bank = GetNode<BankUI>("BankUI");
        Instance = this;
        ui.BindPlayer(player);
        DialogueManager.Instance.ActionRequested += OnDialogueAction;
        Game.Instance.Setup(zoneRoot, player);
        _ = Game.Instance.ChangeZone("home", "start", true);
    }

    public override void _ExitTree()
    {
        DialogueManager.Instance.ActionRequested -= OnDialogueAction;
        Instance = null;
    }

    /// <summary>Exécute une action de jeu (boutique, dépôt, banque) demandée par un dialogue ou un objet.</summary>
    public void RunAction(string action, string speakerId) => OnDialogueAction(action, speakerId);

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
            case "bank":
                _bank.Open();
                break;
            default:
                GD.PushWarning($"Action de dialogue inconnue : '{action}'");
                break;
        }
    }
}
