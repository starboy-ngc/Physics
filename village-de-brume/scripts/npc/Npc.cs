using Godot;

namespace VillageDeBrume;

/// <summary>
/// Personnage non joueur. Ses données (nom, apparence, dialogue, position)
/// viennent d'un fichier JSON chargé par NpcManager ; ce noeud n'est que la
/// présence physique du PNJ dans la zone courante.
/// Déplacements simples : MoveTo() vers un point (utilisé par les horaires
/// à l'étape 3) et, optionnellement, une petite errance autour d'un point.
/// </summary>
public partial class Npc : CharacterBody2D
{
    private const float Speed = 50f;

    public string NpcId { get; private set; } = "";
    public string DisplayName { get; private set; } = "???";
    public string DialoguePath { get; private set; } = "";
    public float WanderRadius { get; private set; }
    public Vector2 HomePosition { get; private set; }

    public CharacterVisual Visual { get; private set; } = null!;
    public NpcTalkArea TalkArea { get; private set; } = null!;

    private CharacterVisual.Facing _facing = CharacterVisual.Facing.Down;
    public CharacterVisual.Facing FacingDirection
    {
        get => _facing;
        set { _facing = value; if (Visual != null) Visual.FacingDirection = value; }
    }

    private Vector2 _target;
    private bool _hasTarget;
    private float _wanderTimer;
    private float _blockedTime;
    private bool _talking;
    private readonly RandomNumberGenerator _rng = new();

    public override void _Ready()
    {
        Visual = GetNode<CharacterVisual>("Visual");
        TalkArea = GetNode<NpcTalkArea>("TalkArea");
        Visual.FacingDirection = _facing;
        HomePosition = GlobalPosition;
        _rng.Seed = (ulong)NpcId.GetHashCode();
        _wanderTimer = _rng.RandfRange(1f, 3f);
        TalkArea.Prompt = "Parler";
        TalkArea.InteractCallback = OnInteract;
    }

    /// <summary>Applique une fiche PNJ. À appeler après l'ajout à l'arbre.</summary>
    public void ApplyData(NpcData data)
    {
        NpcId = data.Id;
        DisplayName = data.Name;
        DialoguePath = data.Dialogue;
        WanderRadius = data.WanderRadius;
        _rng.Seed = (ulong)NpcId.GetHashCode();
        if (data.Appearance.TryGetValue("tunic", out var tunic)) Visual.TunicColor = new Color(tunic);
        if (data.Appearance.TryGetValue("hair", out var hair)) Visual.HairColor = new Color(hair);
        if (data.Appearance.TryGetValue("skin", out var skin)) Visual.SkinColor = new Color(skin);
        if (data.Appearance.TryGetValue("pants", out var pants)) Visual.PantsColor = new Color(pants);
        Visual.QueueRedraw();
    }

    public void MoveTo(Vector2 target)
    {
        _target = target;
        _hasTarget = true;
        _blockedTime = 0f;
    }

    public void Stop()
    {
        _hasTarget = false;
        Velocity = Vector2.Zero;
    }

    public void FaceTowards(Vector2 point) =>
        FacingDirection = CharacterVisual.FacingTowards(GlobalPosition, point);

    public override void _PhysicsProcess(double delta)
    {
        float dt = (float)delta;
        if (_talking)
        {
            Velocity = Vector2.Zero;
            Visual.Animate(dt, false);
            return;
        }

        if (!_hasTarget && WanderRadius > 0f)
        {
            _wanderTimer -= dt;
            if (_wanderTimer <= 0f)
            {
                _wanderTimer = _rng.RandfRange(2f, 5f);
                var offset = new Vector2(_rng.RandfRange(-1f, 1f), _rng.RandfRange(-1f, 1f)) * WanderRadius;
                // Errance en lignes droites (4 directions) : on ne garde qu'un axe.
                if (Mathf.Abs(offset.X) > Mathf.Abs(offset.Y)) offset.Y = 0f; else offset.X = 0f;
                MoveTo(HomePosition + offset);
            }
        }

        bool moving = false;
        if (_hasTarget)
        {
            Vector2 toTarget = _target - GlobalPosition;
            if (toTarget.Length() < 2f)
            {
                Stop();
            }
            else
            {
                // Un axe à la fois : d'abord le plus long.
                Vector2 dir = Vector2.Zero;
                if (Mathf.Abs(toTarget.X) > 1f) dir.X = Mathf.Sign(toTarget.X);
                else dir.Y = Mathf.Sign(toTarget.Y);
                Velocity = dir * Speed;
                Vector2 before = GlobalPosition;
                MoveAndSlide();
                moving = true;
                FacingDirection = CharacterVisual.FacingFromVector(dir, _facing);
                if (GlobalPosition.DistanceTo(before) < 0.1f)
                {
                    _blockedTime += dt;
                    if (_blockedTime > 0.5f)
                        Stop(); // obstacle : on abandonne cette destination
                }
            }
        }
        if (!moving)
            Velocity = Vector2.Zero;
        Visual.Animate(dt, moving);
    }

    /// <summary>Lance le dialogue de ce PNJ (appelé par la zone de parole ou par un test).</summary>
    public void OnInteract(Node2D player)
    {
        if (string.IsNullOrEmpty(DialoguePath))
            return;
        var data = DialogueData.LoadFromFile(DialoguePath);
        if (data == null)
            return;
        if (DialogueManager.Instance.Start(data, DisplayName))
        {
            _talking = true;
            Stop();
            FaceTowards(player.GlobalPosition);
            if (player is Player p)
                p.FaceTowards(GlobalPosition);
            DialogueManager.Instance.DialogueEnded += OnDialogueEnded;
        }
    }

    private void OnDialogueEnded(string id)
    {
        DialogueManager.Instance.DialogueEnded -= OnDialogueEnded;
        _talking = false;
    }

    public override void _ExitTree()
    {
        DialogueManager.Instance.DialogueEnded -= OnDialogueEnded;
    }
}
