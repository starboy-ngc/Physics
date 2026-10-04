using Godot;

namespace VillageDeBrume;

/// <summary>
/// Personnage non joueur sur la grille. Ses données viennent d'un JSON chargé
/// par NpcManager. Errance optionnelle autour de sa case d'origine ;
/// dialogue quand le joueur lui parle (directement ou via un comptoir).
/// </summary>
public partial class Npc : GridEntity, IGridInteractable
{
    public string NpcId { get; private set; } = "";
    public string DisplayName { get; private set; } = "???";
    public string DialoguePath { get; private set; } = "";
    public int WanderRadius { get; private set; }
    public Vector2I HomeTile { get; private set; }
    public string Prompt => "Parler";

    private readonly RandomNumberGenerator _rng = new();
    private float _wanderTimer;
    private bool _talking;
    private CharacterSprites.Facing _homeFacing;

    public void ApplyData(NpcData data)
    {
        NpcId = data.Id;
        DisplayName = data.Name;
        DialoguePath = data.Dialogue;
        WanderRadius = Mathf.RoundToInt(data.WanderRadius);
        _rng.Seed = (ulong)NpcId.GetHashCode();
        _wanderTimer = _rng.RandfRange(1f, 3f);
        SpriteIndex = data.Sprite;
        RebuildSprite();
    }

    public void SetHome(Vector2I tile, CharacterSprites.Facing facing)
    {
        HomeTile = tile;
        _homeFacing = facing;
    }

    public override void _Process(double delta)
    {
        if (!_talking && !IsMoving && WanderRadius > 0)
        {
            _wanderTimer -= (float)delta;
            if (_wanderTimer <= 0f)
            {
                _wanderTimer = _rng.RandfRange(1.5f, 4f);
                var dirs = new[] { new Vector2I(1, 0), new Vector2I(-1, 0), new Vector2I(0, 1), new Vector2I(0, -1) };
                var d = dirs[_rng.RandiRange(0, 3)];
                var target = Tile + d;
                if (Mathf.Abs(target.X - HomeTile.X) <= WanderRadius && Mathf.Abs(target.Y - HomeTile.Y) <= WanderRadius)
                    TryStep(d);
            }
        }
        base._Process(delta);
    }

    public void Interact(Player player)
    {
        if (string.IsNullOrEmpty(DialoguePath))
            return;
        var data = DialogueData.LoadFromFile(DialoguePath);
        if (data == null)
            return;
        if (DialogueManager.Instance.Start(data, DisplayName, NpcId))
        {
            _talking = true;
            FaceTowards(player.Tile);
            player.FaceTowards(Tile);
            DialogueManager.Instance.DialogueEnded += OnDialogueEnded;
        }
    }

    private void OnDialogueEnded(string id)
    {
        DialogueManager.Instance.DialogueEnded -= OnDialogueEnded;
        _talking = false;
        if (WanderRadius == 0)
            Facing = _homeFacing;
    }

    public override void _ExitTree()
    {
        DialogueManager.Instance.DialogueEnded -= OnDialogueEnded;
    }
}
