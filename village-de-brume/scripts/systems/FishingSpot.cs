using Godot;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Zone de pêche autour d'un plan d'eau. Interaction en plusieurs temps :
///   Idle -> (E) Waiting : la ligne est lancée, un bouchon flotte
///   Waiting -> Bite : après un délai aléatoire, « Ça mord ! »
///   Bite -> (E dans le temps imparti) prise ajoutée à l'inventaire, sinon raté.
/// (E) pendant l'attente remonte la ligne. Le joueur est immobilisé pendant la pêche.
/// </summary>
public partial class FishingSpot : Interactable
{
    public enum FishingState { Idle, Waiting, Bite, Result }

    /// <summary>Délai avant la touche (secondes), tiré au hasard entre les deux bornes.</summary>
    [Export] public Vector2 BiteDelayRange { get; set; } = new(2f, 6f);
    /// <summary>Temps laissé au joueur pour ferrer.</summary>
    [Export] public float BiteWindow { get; set; } = 1.1f;
    [Export] public string RequiredItem { get; set; } = "rod";

    public FishingState State { get; private set; } = FishingState.Idle;
    public string? LastCatch { get; private set; }

    /// <summary>Table des prises : identifiant d'objet et poids.</summary>
    private static readonly (string id, int weight)[] CatchTable =
    {
        ("roach", 45), ("perch", 30), ("carp", 15), ("boot", 10),
    };

    private readonly RandomNumberGenerator _rng = new();
    private Player? _player;
    private float _timer;
    private MeshInstance3D? _bobber;
    private Label3D? _alert;

    public override void _Ready()
    {
        base._Ready();
        Prompt = "Pêcher";
        _rng.Randomize();
    }

    public override void Interact(Node3D player)
    {
        if (player is not Player p || State != FishingState.Idle)
            return;
        if (!Inventory.Instance.Definitions.ContainsKey(RequiredItem) || Inventory.Instance.Count(RequiredItem) == 0)
        {
            GameUI.Instance?.ShowNotice("Il te faudrait une canne à pêche.");
            return;
        }
        _player = p;
        p.Locked = true;
        p.FaceTowards(GlobalPosition);
        ShowBobber(p);
        State = FishingState.Waiting;
        _timer = _rng.RandfRange(BiteDelayRange.X, BiteDelayRange.Y);
        SetPrompt("Remonter la ligne");
        GameUI.Instance?.ShowNotice("Tu lances ta ligne...", 1.5f);
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (State is FishingState.Idle or FishingState.Result || !@event.IsActionPressed("interact"))
            return;
        GetViewport().SetInputAsHandled();
        if (State == FishingState.Waiting)
        {
            Finish("Tu remontes la ligne.");
        }
        else if (State == FishingState.Bite)
        {
            string id = PickCatch();
            Inventory.Instance.Add(id, 1);
            LastCatch = id;
            string name = Inventory.Instance.GetDef(id)?.Name ?? id;
            Finish(id == "boot" ? $"Tu remontes... une {name.ToLower()}." : $"Tu as attrapé : {name} !");
        }
    }

    public override void _Process(double delta)
    {
        if (State == FishingState.Idle)
            return;
        _timer -= (float)delta;
        switch (State)
        {
            case FishingState.Waiting:
                if (_bobber != null)
                    _bobber.Position = _bobber.Position with { Y = 0.1f + Mathf.Sin((float)Time.GetTicksMsec() / 300f) * 0.03f };
                if (_timer <= 0f)
                {
                    State = FishingState.Bite;
                    _timer = BiteWindow;
                    if (_bobber != null) _bobber.Position = _bobber.Position with { Y = -0.1f };
                    if (_alert != null) _alert.Visible = true;
                    SetPrompt("Ferrer !");
                    GameUI.Instance?.ShowNotice("Ça mord !", BiteWindow);
                }
                break;
            case FishingState.Bite:
                if (_timer <= 0f)
                    Finish("Le poisson s'est échappé.");
                break;
            case FishingState.Result:
                if (_timer <= 0f)
                {
                    State = FishingState.Idle;
                    SetPrompt("Pêcher");
                }
                break;
        }
    }

    private void Finish(string message)
    {
        HideBobber();
        if (_player != null)
            _player.Locked = false;
        GameUI.Instance?.ShowNotice(message, 2f);
        State = FishingState.Result;
        _timer = 0.6f; // petit délai avant de pouvoir relancer
        SetPrompt("");
    }

    private void SetPrompt(string prompt)
    {
        Prompt = prompt;
        _player?.RefreshFocus();
    }

    private string PickCatch()
    {
        int total = 0;
        foreach (var (_, w) in CatchTable) total += w;
        int roll = _rng.RandiRange(1, total);
        foreach (var (id, w) in CatchTable)
        {
            roll -= w;
            if (roll <= 0) return id;
        }
        return CatchTable[0].id;
    }

    // --- Visuel : bouchon sur l'eau et « ! » au-dessus du joueur ---------------

    private void ShowBobber(Player p)
    {
        Vector3 dir = CharacterVisual.ToVector(p.FacingDirection);
        Vector3 at = p.GlobalPosition + dir * 2.2f;
        _bobber = new MeshInstance3D
        {
            Name = "Bobber",
            Mesh = new SphereMesh { Radius = 0.16f, Height = 0.32f, RadialSegments = 8, Rings = 4 },
            MaterialOverride = Materials.Flat(new Color("d8503f")),
            TopLevel = true,
        };
        AddChild(_bobber);
        _bobber.GlobalPosition = new Vector3(at.X, 0.1f, at.Z);
        _alert = new Label3D
        {
            Name = "Alert",
            Text = "!",
            FontSize = 64,
            PixelSize = 0.012f,
            Modulate = new Color("f0e2b4"),
            OutlineModulate = new Color("23222a"),
            OutlineSize = 12,
            Billboard = BaseMaterial3D.BillboardModeEnum.Enabled,
            NoDepthTest = true,
            Visible = false,
            TopLevel = true,
        };
        AddChild(_alert);
        _alert.GlobalPosition = p.GlobalPosition + new Vector3(0, 2.6f, 0);
    }

    private void HideBobber()
    {
        _bobber?.QueueFree();
        _alert?.QueueFree();
        _bobber = null;
        _alert = null;
    }
}
