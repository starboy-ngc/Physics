using Godot;
using System.Collections.Generic;

namespace VillageDeBrume.Tests;

/// <summary>
/// Base des tests headless. Chaque test est une scène (tests/*.tscn) lancée avec :
///   godot --headless --path . tests/NomDuTest.tscn
/// Le test charge la scène principale, pilote le jeu frame par frame et
/// termine avec le code 0 (OK) ou 1 (échec).
/// </summary>
public abstract partial class TestBase : Node
{
    protected Game Game => Game.Instance;
    protected DialogueManager Dialogue => DialogueManager.Instance;
    protected int Frame { get; private set; }
    protected int Failures { get; private set; }
    protected abstract string Tag { get; }

    private readonly List<string> _toRelease = new();
    private bool _done;

    public override void _Ready()
    {
        Engine.MaxFps = 60; // les délais du jeu sont en temps réel
        AddChild(GD.Load<PackedScene>("res://scenes/main/Main.tscn").Instantiate());
        Log("scène principale chargée");
    }

    public override void _Process(double delta)
    {
        if (_done)
            return;
        Frame++;
        ReleasePending();
        if (Frame < 3)
            return;
        Step();
    }

    /// <summary>Appelé à chaque frame à partir de la 3e.</summary>
    protected abstract void Step();

    protected void Log(string msg) => GD.Print($"[{Tag}] {msg}");

    protected void Fail(string msg)
    {
        Failures++;
        GD.PushError($"[{Tag}] {msg}");
    }

    protected void Finish(string error = "")
    {
        if (_done)
            return;
        _done = true;
        if (error != "")
            Fail(error);
        if (Failures == 0)
            Log("OK");
        else
            Log($"ECHEC — {Failures} problème(s)");
        GetTree().Quit(Failures == 0 ? 0 : 1);
    }

    /// <summary>Appui à cette frame, relâchement à la frame suivante (comme une vraie touche).</summary>
    protected void PressOnce(string action)
    {
        Input.ParseInputEvent(new InputEventAction { Action = action, Pressed = true });
        _toRelease.Add(action);
    }

    private void ReleasePending()
    {
        foreach (var action in _toRelease)
            Input.ParseInputEvent(new InputEventAction { Action = action, Pressed = false });
        _toRelease.Clear();
    }

    protected static void HoldOnly(string action)
    {
        foreach (var a in new[] { "move_up", "move_down", "move_left", "move_right" })
        {
            if (a == action) Input.ActionPress(a);
            else Input.ActionRelease(a);
        }
    }

    protected static void ReleaseAll() => HoldOnly("");
}
