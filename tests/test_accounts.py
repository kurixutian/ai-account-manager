import json
import tempfile
import unittest
from pathlib import Path

from ai_account_manager.account_manager import add_account, account_names, remove_account
from ai_account_manager.config_manager import default_config, load_config, save_config, validate_config


class AccountTests(unittest.TestCase):
    def test_add_generates_suffixes_and_rejects_duplicates(self):
        config = default_config("codex")
        add_account(config, "codex")
        add_account(config, "codex")
        self.assertEqual(account_names(config), ["codex", "codex2"])
        with self.assertRaises(ValueError):
            add_account(config, "codex2")

    def test_atomic_persistence_and_invalid_import(self):
        config = default_config("codex")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            save_config(path, config)
            self.assertEqual(load_config(path)["provider"], "codex")
            path.write_text(json.dumps({"bad": True}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)

    def test_remove_preserves_other_accounts(self):
        config = default_config("codex")
        add_account(config, "one")
        add_account(config, "two")
        remove_account(config, "one")
        self.assertEqual(account_names(config), ["two"])
        validate_config(config)


if __name__ == "__main__":
    unittest.main()
