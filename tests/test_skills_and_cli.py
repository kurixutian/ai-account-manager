import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from ai_account_manager.account_manager import add_account, choose_available_account, launch_account
from ai_account_manager.cli import main
from ai_account_manager.config_manager import default_config
from ai_account_manager.skill_manager import set_skill_policy


class SkillsQuotaCliTests(unittest.TestCase):
    def test_policy_normalizes_path_and_selected_skills(self):
        config = default_config("codex")
        set_skill_policy(config, "selected", "/tmp/shared", ["pdf", "testing"])
        self.assertEqual(config["skills"]["policy"], "selected")
        self.assertEqual(config["skills"]["names"], ["pdf", "testing"])
        self.assertTrue(config["skills"]["path"].endswith("shared"))

    def test_exhausted_account_fails_over_and_preserves_reset(self):
        config = default_config("codex")
        add_account(config, "first")
        add_account(config, "second")
        config["accounts"][0]["quota"] = {"status": "exhausted", "remaining": 0, "reset_at": "2026-12-01T09:00:00+08:00"}
        config["accounts"][1]["quota"] = {"status": "available", "remaining": 5, "reset_at": "2026-12-02T09:00:00+08:00"}
        chosen = choose_available_account(config)
        self.assertEqual(chosen["name"], "second")
        self.assertEqual(config["accounts"][0]["quota"]["reset_at"], "2026-12-01T09:00:00+08:00")

    def test_unknown_quota_does_not_launch(self):
        config = default_config("codex")
        add_account(config, "first")
        with self.assertRaisesRegex(RuntimeError, "no account with confirmed available quota"):
            choose_available_account(config)

    def test_dry_run_does_not_create_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(["setup", "--provider", "codex", "--count", "1", "--base-name", "codex", "--future-additions", "yes", "--policy", "separate", "--output", str(path), "--dry-run"])
            self.assertEqual(result, 0)
            self.assertFalse(path.exists())
            self.assertIn("dry-run", output.getvalue().lower())

    def test_launch_uses_explicit_argument_list(self):
        account = {"name": "first", "command": ["agent-cli", "--profile", "first"]}
        calls = []
        launch_account(account, runner=lambda command: calls.append(command))
        self.assertEqual(calls, [["agent-cli", "--profile", "first"]])

    def test_plain_command_opens_main_menu(self):
        with patch("ai_account_manager.cli.select_option", return_value="exit"), redirect_stdout(io.StringIO()) as output:
            result = main([])
        self.assertEqual(result, 0)
        self.assertIn("AI Manager", output.getvalue())


if __name__ == "__main__":
    unittest.main()
