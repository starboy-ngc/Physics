using Godot;
using System.Collections.Generic;

namespace VillageDeBrume.Tests;

/// <summary>
/// Va dans la boulangerie, marche vers Émile, appuie sur E, descend d'un cran
/// dans les choix, valide, puis avance jusqu'à la fin du dialogue.
/// </summary>
public partial class DialogueTest : TestBase
{
    protected override string Tag => "dialogue";
    private int _phase;
    private int _phaseStart;
    private int _nodesSeen;
    private int _choicesSeen;
    private bool _passingSeen;

    public override void _Ready()
    {
        base._Ready();
        Dialogue.NodeChanged += OnNode;
    }

    private void OnNode(string speaker, string text, IReadOnlyList<string> choices)
    {
        _nodesSeen++;
        if (choices.Count > 0)
            _choicesSeen++;
        if (text.StartsWith("Alors bienvenue"))
            _passingSeen = true;
        string excerpt = text.Length > 40 ? text[..40] : text;
        Log($"{speaker} : {excerpt}  (choix: {choices.Count})");
    }

    protected override void Step()
    {
        var player = Game.Player;
        switch (_phase)
        {
            case 0:
                _ = Game.ChangeZone("village", "near_emile", true);
                _phase = 1;
                _phaseStart = Frame;
                break;
            case 1:
                HoldOnly("move_up"); // vers l'étal d'Émile (-Z)
                if (player.Focused is NpcTalkArea)
                {
                    ReleaseAll();
                    Log($"invite : E — {player.Focused.Prompt}");
                    _phase = 2;
                    _phaseStart = Frame;
                }
                else if (Frame - _phaseStart > 300)
                    Finish($"aucun Interactable détecté (pos {player.GlobalPosition})");
                break;
            case 2:
                if (Dialogue.IsActive)
                {
                    Log("dialogue démarré");
                    _phase = 3;
                    _phaseStart = Frame;
                }
                else if (Frame - _phaseStart > 60)
                    Finish("le dialogue n'a pas démarré");
                else if ((Frame - _phaseStart) % 5 == 0)
                    PressOnce("interact");
                break;
            case 3:
                int off = Frame - _phaseStart;
                if (off % 10 == 4)
                {
                    if (!Dialogue.IsActive)
                    {
                        if (_nodesSeen >= 3 && _choicesSeen >= 1 && !player.IsMoving && _passingSeen)
                            Finish();
                        else
                            Finish($"dialogue incomplet ({_nodesSeen} noeuds, 2e choix vu : {_passingSeen})");
                        return;
                    }
                    // Tester la navigation : descendre d'un cran avant de valider.
                    if (Dialogue.CurrentChoices().Count > 0)
                        PressOnce("move_down");
                    else
                        PressOnce("interact");
                }
                else if (off % 10 == 8 && Dialogue.IsActive && Dialogue.CurrentChoices().Count > 0)
                    PressOnce("interact");
                if (off > 600)
                    Finish("le dialogue ne se termine pas");
                break;
        }
    }
}
