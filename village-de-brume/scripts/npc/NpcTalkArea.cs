using Godot;
using System;

namespace VillageDeBrume;

/// <summary>Zone d'interaction d'un PNJ : Interact est délégué au PNJ.</summary>
public partial class NpcTalkArea : Interactable
{
    public Action<Node3D>? InteractCallback { get; set; }

    public override void Interact(Node3D player) => InteractCallback?.Invoke(player);
}
