import unittest

from ai_account_manager.prompts import move_selection, render_menu


class PromptTests(unittest.TestCase):
    def test_arrow_selection_wraps(self):
        self.assertEqual(move_selection(0, "down", 3), 1)
        self.assertEqual(move_selection(0, "up", 3), 2)
        self.assertEqual(move_selection(2, "down", 3), 0)

    def test_unknown_key_keeps_selection(self):
        self.assertEqual(move_selection(1, "x", 3), 1)

    def test_render_menu_explains_step_and_selected_option(self):
        rendered = render_menu("Choose provider", ["Codex", "Agy"], 0, step=1, total=4)
        self.assertIn("Step 1 of 4", rendered)
        self.assertIn("> Codex", rendered)
        self.assertIn("↑ ↓ Navigate", rendered)


if __name__ == "__main__":
    unittest.main()
