using Godot;

namespace VillageDeBrume;

/// <summary>Interactable qui affiche simplement un message (panneau, tableau, portail...).</summary>
public partial class ExamineArea : Interactable
{
    public string Text { get; set; } = "";

    public override void Interact(Node3D player)
    {
        if (Text != "")
            GameUI.Instance?.ShowNotice(Text, 3f);
    }
}
