using Godot;
using System;
using System.Collections.Generic;

namespace VillageDeBrume;

/// <summary>
/// Autoload "DialogueManager" : déroule un DialogueData noeud par noeud.
/// Indépendant des PNJ et de l'interface : l'UI écoute les événements,
/// le joueur consulte IsActive pour se bloquer.
/// </summary>
public partial class DialogueManager : Node
{
    public static DialogueManager Instance { get; private set; } = null!;

    public event Action<string>? DialogueStarted;
    public event Action<string, string, IReadOnlyList<string>>? NodeChanged;
    public event Action<string>? DialogueEnded;
    /// <summary>Action demandée par un noeud (nom de l'action, identifiant du locuteur).</summary>
    public event Action<string, string>? ActionRequested;

    public bool IsActive { get; private set; }
    /// <summary>Frame à laquelle le dialogue a démarré (l'UI ignore la touche de cette frame).</summary>
    public ulong StartedFrame { get; private set; } = ulong.MaxValue;

    private DialogueData? _data;
    private string _speaker = "";
    public string SpeakerId { get; private set; } = "";
    private DialogueNode? _node;

    public override void _EnterTree()
    {
        Instance = this;
    }

    public bool Start(DialogueData? data, string speaker, string speakerId = "")
    {
        if (IsActive || data == null)
            return false;
        _data = data;
        _speaker = speaker;
        SpeakerId = speakerId;
        IsActive = true;
        StartedFrame = Engine.GetProcessFrames();
        DialogueStarted?.Invoke(speaker);
        Goto(data.StartNode);
        return true;
    }

    public IReadOnlyList<string> CurrentChoices()
    {
        var list = new List<string>();
        if (_node?.Choices != null)
            foreach (var c in _node.Choices)
                list.Add(c.Text);
        return list;
    }

    /// <summary>Avance au noeud suivant (si le noeud courant n'a pas de choix).</summary>
    public void Advance()
    {
        if (!IsActive || _node == null || _node.HasChoices)
            return;
        Follow(_node.Next);
    }

    /// <summary>Valide le choix d'index donné.</summary>
    public void Choose(int index)
    {
        if (!IsActive || _node?.Choices == null)
            return;
        if (index < 0 || index >= _node.Choices.Count)
            return;
        Follow(_node.Choices[index].Next);
    }

    public void End()
    {
        if (!IsActive)
            return;
        string endedId = _data!.Id;
        IsActive = false;
        _data = null;
        _node = null;
        DialogueEnded?.Invoke(endedId);
    }

    private void Follow(string? next)
    {
        string? action = _node?.Action;
        if (!string.IsNullOrEmpty(action))
        {
            // Un noeud avec action termine le dialogue, puis le moteur exécute l'action.
            string speakerId = SpeakerId;
            End();
            ActionRequested?.Invoke(action, speakerId);
            return;
        }
        if (string.IsNullOrEmpty(next) || next == "end")
            End();
        else
            Goto(next);
    }

    private void Goto(string nodeId)
    {
        if (_data == null || !_data.HasNode(nodeId))
        {
            GD.PushError($"Dialogue '{_data?.Id}' : noeud '{nodeId}' introuvable, fin forcée.");
            End();
            return;
        }
        _node = _data.GetNode(nodeId);
        NodeChanged?.Invoke(_speaker, _node.Text, CurrentChoices());
    }
}
