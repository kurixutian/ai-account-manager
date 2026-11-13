import unittest

from ai_account_manager.providers import GenericAdapter, get_adapter


class ProviderTests(unittest.TestCase):
    def test_known_provider_and_custom_paths(self):
        adapter = get_adapter("codex", {"config_dir": "/tmp/codex", "skill_dir": "/tmp/skills"})
        self.assertEqual(adapter.name, "codex")
        self.assertEqual(adapter.config_dir, "/tmp/codex")
        self.assertEqual(adapter.skill_dir, "/tmp/skills")

    def test_generic_adapter_requires_explicit_paths(self):
        adapter = GenericAdapter("other", {"config_dir": "/x", "skill_dir": "/y"})
        self.assertEqual(adapter.launch_command(["agent"]), ["agent"])


if __name__ == "__main__":
    unittest.main()
