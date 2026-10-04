using Godot;

namespace VillageDeBrume;

/// <summary>Ce avec quoi le joueur peut interagir en appuyant sur E face à la case.</summary>
public interface IGridInteractable
{
    string Prompt { get; }
    void Interact(Player player);
}

/// <summary>Objet examinable : affiche un message.</summary>
public class Examinable : IGridInteractable
{
    public string Prompt { get; }
    public string Text { get; }
    public Examinable(string prompt, string text) { Prompt = prompt; Text = text; }
    public void Interact(Player player) => GameUI.Instance?.ShowNotice(Text, 3f);
}

/// <summary>Comptoir d'un étal : parler au marchand (PNJ) qui se tient derrière.</summary>
public class Counter : IGridInteractable
{
    public string Prompt => "Parler";
    public string OwnerId { get; }
    public Counter(string ownerId) { OwnerId = ownerId; }

    public void Interact(Player player)
    {
        if (NpcManager.Instance.Instances.TryGetValue(OwnerId, out var npc))
            npc.Interact(player);
    }
}
