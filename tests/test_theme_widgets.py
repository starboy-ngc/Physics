"""Les petits mecanismes de l'interface : bulles, molette, cases a cocher.

Ils ne portent aucun chiffre, mais ils portent tout le reste : une bulle
qui reste affichee par-dessus une fenetre fermee, une molette qui fait
defiler la mauvaise zone, une case qui ne bascule pas au clic sur son
libelle. Ce sont les defauts qu'aucun rapport de bug ne decrit precisement,
et qu'on ne voit qu'en les essayant.

Ces tests exigent un affichage ; ils sont ignores automatiquement sans lui.
Aucune donnee RH reelle.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import tkinter
    HAS_TK = True
except ImportError:                                    # pragma: no cover
    HAS_TK = False


def _display_answers() -> bool:
    if not (HAS_TK and os.environ.get("DISPLAY")):
        return False
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        return False
    root.destroy()
    return True


needs_display = unittest.skipUnless(
    _display_answers(), "aucun affichage disponible (test d'interface ignoré)")


class Event:
    def __init__(self, x=0, y=0, delta=0, num=0):
        self.x, self.y = x, y
        self.x_root, self.y_root = x, y
        self.delta, self.num = delta, num


@needs_display
class WidgetCase(unittest.TestCase):
    def setUp(self):
        import tkinter as tk

        self.root = tk.Tk()
        self.root.geometry("800x600+0+0")
        self.root.update()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass


class TestCheckRow(WidgetCase):
    """Une case a cocher dessinee plutot que celle du theme."""

    def build(self, value=False):
        from compensation_analytics.ui.theme import CheckRow, Fonts

        variable = tkinter.BooleanVar(value=value)
        row = CheckRow(self.root, "Équipe directe seulement", variable,
                       Fonts(self.root))
        row.pack()
        self.root.update()
        return row, variable

    def test_a_click_toggles_it(self):
        row, variable = self.build()
        row._toggle()
        self.assertTrue(variable.get())
        row._toggle()
        self.assertFalse(variable.get())

    def test_it_starts_in_the_state_it_is_given(self):
        _row, variable = self.build(value=True)
        self.assertTrue(variable.get())

    def test_the_label_is_part_of_the_target(self):
        """Cliquer sur le texte doit cocher : viser un carre de quinze
        pixels est une exigence inutile."""
        row, variable = self.build()
        row.text.event_generate("<Button-1>", x=2, y=2)
        self.root.update()
        self.assertTrue(variable.get())

    def test_the_drawn_box_is_a_target_too(self):
        row, variable = self.build()
        row.box.event_generate("<Button-1>", x=2, y=2)
        self.root.update()
        self.assertTrue(variable.get())


class TestHints(WidgetCase):
    """Les bulles d'aide, qui survivent a la fenetre qui les porte."""

    def build(self):
        from compensation_analytics.ui.theme import Fonts, Hints

        return Hints(self.root, Fonts(self.root))

    def test_a_bubble_appears_and_carries_the_text(self):
        import tkinter as tk

        hints = self.build()
        label = tk.Label(self.root, text="Effectif")
        label.pack()
        self.root.update()
        hints._show(label, ["Nombre de salariés retenus."])
        self.root.update()
        self.assertIsNotNone(hints.window)
        shown = " ".join(line.cget("text") for line in hints.lines
                         if line.winfo_manager())
        self.assertIn("salariés", shown)

    def test_a_second_shorter_text_does_not_leave_the_first_behind(self):
        import tkinter as tk

        hints = self.build()
        label = tk.Label(self.root, text="x")
        label.pack()
        self.root.update()
        hints._show(label, ["Premier paragraphe.", "Second paragraphe."])
        self.root.update()
        hints._show(label, ["Un seul."])
        self.root.update()
        shown = " ".join(line.cget("text") for line in hints.lines
                         if line.winfo_manager())
        self.assertNotIn("Second", shown)

    def test_hiding_withdraws_the_bubble(self):
        import tkinter as tk

        hints = self.build()
        label = tk.Label(self.root, text="x")
        label.pack()
        self.root.update()
        hints._show(label, ["Texte."])
        hints.hide()
        self.root.update()
        self.assertEqual(hints.window.state(), "withdrawn")

    def test_a_destroyed_widget_shows_nothing(self):
        """La bulle est differee : la fenetre peut avoir disparu entre le
        survol et l'affichage."""
        import tkinter as tk

        hints = self.build()
        label = tk.Label(self.root, text="x")
        label.pack()
        self.root.update()
        label.destroy()
        hints._show(label, ["Texte."])
        self.assertIsNone(hints.window)

    def test_hiding_twice_is_harmless(self):
        hints = self.build()
        hints.hide()
        hints.hide()


class TestWheelScrolling(WidgetCase):
    """La molette agit sur la zone survolee, et seulement si elle defile."""

    def build(self, content_height=2000):
        import tkinter as tk

        from compensation_analytics.ui.theme import bind_wheel

        canvas = tk.Canvas(self.root, height=200)
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        tk.Frame(inner, height=content_height, width=200).pack()
        self.root.update()
        canvas.configure(scrollregion=(0, 0, 200, content_height))
        self.root.update()
        bind_wheel(canvas, self.root)
        return canvas

    def _scroll(self, canvas, delta):
        x = canvas.winfo_rootx() + 10
        y = canvas.winfo_rooty() + 10
        canvas.event_generate("<MouseWheel>", delta=delta, x=10, y=10,
                              rootx=x, rooty=y)
        self.root.update()

    def test_content_taller_than_the_frame_scrolls(self):
        canvas = self.build()
        before = canvas.yview()[0]
        self._scroll(canvas, -120)
        self.assertGreaterEqual(canvas.yview()[0], before)

    def test_content_that_fits_never_scrolls(self):
        """Sinon la page tremble sous la molette sans jamais bouger."""
        canvas = self.build(content_height=50)
        self._scroll(canvas, -120)
        self.assertEqual(canvas.yview(), (0.0, 1.0))


class TestFontChoice(unittest.TestCase):
    @needs_display
    def test_a_family_is_always_returned(self):
        """Aucune des familles souhaitees n'est garantie presente : sur un
        poste qui n'en a aucune, il faut quand meme une police — celle du
        systeme, plutot qu'un nom que Tk ne saura pas resoudre."""
        import tkinter as tk

        from compensation_analytics.ui.theme import pick_family

        root = tk.Tk()
        try:
            chosen = pick_family(root)
            self.assertTrue(chosen)
            self.assertIsInstance(chosen, str)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
