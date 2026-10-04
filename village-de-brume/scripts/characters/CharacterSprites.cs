using Godot;

namespace VillageDeBrume;

/// <summary>
/// Génère en code la planche de sprites d'un personnage (aucun asset externe) :
/// 4 directions (lignes : bas, haut, gauche, droite) × 3 poses (colonnes :
/// repos, pas 1, pas 2), cellules de 32x32 px, pieds à la ligne 30.
/// Proportions « tête large » façon RPG portable, contour sombre.
/// </summary>
public static class CharacterSprites
{
    public const int Cell = 32;
    public const int FeetRow = 30;
    private static readonly Color Outline = new("1e1e2e");

    public static ImageTexture Build(Color tunic, Color hair, Color skin, Color pants)
    {
        var img = Image.CreateEmpty(Cell * 3, Cell * 4, false, Image.Format.Rgba8);
        img.Fill(new Color(0, 0, 0, 0));
        for (int facing = 0; facing < 4; facing++)
            for (int pose = 0; pose < 3; pose++)
                DrawCharacter(img, pose * Cell + Cell / 2, facing * Cell + FeetRow,
                    (CharacterVisual.Facing)facing, pose - 1, tunic, hair, skin, pants);
        return ImageTexture.CreateFromImage(img);
    }

    /// <summary>Dessine un personnage dont les pieds sont en (ox, oy). step : -1 repos, 0/1 marche.</summary>
    private static void DrawCharacter(Image img, int ox, int oy, CharacterVisual.Facing facing, int step,
        Color tunic, Color hair, Color skin, Color pants)
    {
        void Fill(int x, int y, int w, int h, Color c) => img.FillRect(new Rect2I(ox + x, oy + y, w, h), c);
        void Stroke(int x, int y, int w, int h, Color c)
        {
            Fill(x, y, w, 1, c); Fill(x, y + h - 1, w, 1, c);
            Fill(x, y, 1, h, c); Fill(x + w - 1, y, 1, h, c);
        }

        int bob = step >= 0 ? -1 : 0;

        // Jambes
        int leftH = 7 - (step == 1 ? 3 : 0);
        int rightH = 7 - (step == 0 ? 3 : 0);
        Fill(-5, -7, 4, leftH, pants); Stroke(-5, -7, 4, leftH, Outline);
        Fill(1, -7, 4, rightH, pants); Stroke(1, -7, 4, rightH, Outline);

        // Corps
        Fill(-6, -15 + bob, 12, 9, tunic);
        Stroke(-6, -15 + bob, 12, 9, Outline);
        if (facing is CharacterVisual.Facing.Left or CharacterVisual.Facing.Right)
        {
            Fill(-2, -13 + bob, 4, 6, tunic.Darkened(0.2f));
        }
        else
        {
            Fill(-8, -13 + bob, 2, 6, skin);
            Fill(6, -13 + bob, 2, 6, skin);
        }

        // Tête
        int hy = -26 + bob;
        Fill(-7, hy, 14, 12, skin);
        switch (facing)
        {
            case CharacterVisual.Facing.Up:
                Fill(-7, hy, 14, 9, hair);
                break;
            case CharacterVisual.Facing.Down:
                Fill(-7, hy, 14, 4, hair);
                Fill(-7, hy + 4, 2, 3, hair);
                Fill(5, hy + 4, 2, 3, hair);
                Fill(-4, hy + 6, 2, 3, Outline);
                Fill(2, hy + 6, 2, 3, Outline);
                break;
            case CharacterVisual.Facing.Left:
                Fill(-7, hy, 14, 4, hair);
                Fill(-1, hy, 8, 8, hair);
                Fill(-5, hy + 6, 2, 3, Outline);
                break;
            case CharacterVisual.Facing.Right:
                Fill(-7, hy, 14, 4, hair);
                Fill(-7, hy, 8, 8, hair);
                Fill(3, hy + 6, 2, 3, Outline);
                break;
        }
        Stroke(-7, hy, 14, 12, Outline);
    }
}
