using Godot;

namespace VillageDeBrume;

/// <summary>
/// Personnage non joueur. Ses données (nom, apparence, dialogue, position)
/// viennent d'un fichier JSON chargé par NpcManager ; ce noeud n'est que la
/// présence physique du PNJ dans la zone courante.
/// Déplacements simples : MoveTo() vers un point (utilisé par les horaires
/// à l'étape 3) et, optionnellement, une petite errance autour d'un point.
/// </summary>
public partial class Npc : CharacterBody3D
{
    private const float Speed = 3f;

    public string NpcId { get; private set; } = "";
    public string DisplayName { get; private set; } = "???";
    public string DialoguePath { get; private set; } = "";
    public float WanderRadius { get; private set; }
    public Vector3 HomePosition { get; private set; }

    public CharacterVisual Visual { get; private set; } = null!;
    public NpcTalkArea TalkArea { get; private set; } = null!;

    private CharacterVisual.Facing _facing = CharacterVisual.Facing.Down;
    public CharacterVisual.Facing FacingDirection
    {
        get => _facing;
        set { _facing = value; if (Visual != null) Visual.FacingDirection = value; }
    }

    private Vector3 _target;
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
        Visual.Rebuild();
    }

    public void MoveTo(Vector3 target)
    {
        _target = new Vector3(target.X, 0f, target.Z);
        _hasTarget = true;
        _blockedTime = 0f;
    }

    public void Stop()
    {
        _hasTarget = false;
        Velocity = Vector3.Zero;
    }

    public void FaceTowards(Vector3 point) => FacingDirection = CharacterVisual.FacingTowards(GlobalPosition, point);

    public override void _PhysicsProcess(double delta)
    {
        float dt = (float)delta;
        if (_talking)
        {
            Velocity = Vector3.Zero;
            Visual.Animate(dt, false);
            return;
        }

        if (!_hasTarget && WanderRadius > 0f)
        {
            _wanderTimer -= dt;
            if (_wanderTimer <= 0f)
            {
                _wanderTimer = _rng.RandfRange(2f, 5f);
                var offset = new Vector3(_rng.RandfRange(-1f, 1f), 0f, _rng.RandfRange(-1f, 1f)) * WanderRadius;
                // Errance en lignes droites (4 directions) : on ne garde qu'un axe.
                if (Mathf.Abs(offset.X) > Mathf.Abs(offset.Z)) offset.Z = 0f; else offset.X = 0f;
                MoveTo(HomePosition + offset);
            }
        }

        bool moving = false;
        if (_hasTarget)
        {
            Vector3 toTarget = _target - GlobalPosition;
            toTarget.Y = 0f;
            if (toTarget.Length() < 0.15f)
            {
                Stop();
            }
            else
            {
                // Un axe à la fois : d'abord le plus long.
                Vector3 dir = Vector3.Zero;
                if (Mathf.Abs(toTarget.X) > 0.08f) dir.X = Mathf.Sign(toTarget.X);
                else dir.Z = Mathf.Sign(toTarget.Z);
                Velocity = dir * Speed;
                Vector3 before = GlobalPosition;
                MoveAndSlide();
                GlobalPosition = new Vector3(GlobalPosition.X, 0f, GlobalPosition.Z);
                moving = true;
                FacingDirection = CharacterVisual.FacingFromInput(new Vector2(dir.X, dir.Z), _facing);
                if (GlobalPosition.DistanceTo(before) < 0.005f)
                {
                    _blockedTime += dt;
                    if (_blockedTime > 0.5f)
                        Stop(); // obstacle : on abandonne cette destination
                }
            }
        }
        if (!moving)
            Velocity = Vector3.Zero;
        Visual.Animate(dt, moving);
    }

    /// <summary>Lance le dialogue de ce PNJ (appelé par la zone de parole ou par un test).</summary>
    public void OnInteract(Node3D player)
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
