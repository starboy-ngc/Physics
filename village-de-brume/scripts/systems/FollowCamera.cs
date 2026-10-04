using Godot;

namespace VillageDeBrume;

/// <summary>
/// Caméra 2.5D : perspective inclinée vers le bas, suit le joueur avec un
/// lissage, et reste dans les limites de la zone (centrée si la zone est plus
/// petite que la vue). Porte aussi l'environnement (fond, lumière ambiante).
/// </summary>
public partial class FollowCamera : Camera3D
{
    public const float DefaultPitch = 55f;
    [Export] public float PitchDegrees { get; set; } = DefaultPitch;
    [Export] public float Distance { get; set; } = 13f;
    [Export] public float SmoothSpeed { get; set; } = 8f;
    /// <summary>Étendue visible au sol depuis le point visé (côtés, vers la caméra, vers le fond).</summary>
    [Export] public float MarginSide { get; set; } = 7.5f;
    [Export] public float MarginNear { get; set; } = 5.2f;
    [Export] public float MarginFar { get; set; } = 8.5f;

    public Node3D? Target { get; set; }

    private Rect2 _bounds = new(0, 0, 48, 36);
    private Vector3 _focus;

    public override void _Ready()
    {
        Fov = 48f;
        KeepAspect = KeepAspectEnum.Height;
        Near = 0.5f;
        Far = 80f;
        Environment = new Godot.Environment
        {
            BackgroundMode = Godot.Environment.BGMode.Color,
            BackgroundColor = new Color("7b857f"),
            AmbientLightSource = Godot.Environment.AmbientSource.Color,
            AmbientLightColor = new Color(0.70f, 0.74f, 0.76f),
            AmbientLightEnergy = 0.6f,
            // Brume légère : le fond de la vue se fond dans le gris du ciel.
            FogEnabled = true,
            FogLightColor = new Color("8d9892"),
            FogLightEnergy = 1.0f,
            FogDensity = 0.012f,
            FogSkyAffect = 1.0f,
        };
    }

    public void SetBounds(Rect2 bounds) => _bounds = bounds;

    /// <summary>Se place immédiatement sur la cible (changement de zone).</summary>
    public void Snap()
    {
        _focus = ClampedTarget();
        Apply();
    }

    public override void _Process(double delta)
    {
        if (Target == null)
            return;
        Vector3 wanted = ClampedTarget();
        float t = 1f - Mathf.Exp(-SmoothSpeed * (float)delta);
        _focus = _focus.Lerp(wanted, t);
        Apply();
    }

    private Vector3 ClampedTarget()
    {
        Vector3 p = Target?.GlobalPosition ?? Vector3.Zero;
        float minX = _bounds.Position.X + MarginSide, maxX = _bounds.End.X - MarginSide;
        float minZ = _bounds.Position.Y + MarginFar, maxZ = _bounds.End.Y - MarginNear;
        float x = minX <= maxX ? Mathf.Clamp(p.X, minX, maxX) : _bounds.GetCenter().X;
        float z = minZ <= maxZ ? Mathf.Clamp(p.Z, minZ, maxZ) : _bounds.GetCenter().Y;
        return new Vector3(x, 0f, z);
    }

    private void Apply()
    {
        float pitch = Mathf.DegToRad(PitchDegrees);
        var offset = new Vector3(0f, Distance * Mathf.Sin(pitch), Distance * Mathf.Cos(pitch));
        GlobalPosition = _focus + offset;
        LookAt(_focus, Vector3.Up);
    }
}
