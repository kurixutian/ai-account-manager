from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderAdapter:
    name: str
    config_dir: str = ""
    skill_dir: str = ""

    def launch_command(self, command: list[str]) -> list[str]:
        if not command:
            raise ValueError("launch command cannot be empty")
        return list(command)


class CodexAdapter(ProviderAdapter):
    def __init__(self, paths: dict[str, Any] | None = None):
        paths = paths or {}
        super().__init__("codex", paths.get("config_dir", ""), paths.get("skill_dir", ""))


class AgyAdapter(ProviderAdapter):
    def __init__(self, paths: dict[str, Any] | None = None):
        paths = paths or {}
        super().__init__("agy", paths.get("config_dir", ""), paths.get("skill_dir", ""))


class GenericAdapter(ProviderAdapter):
    def __init__(self, name: str, paths: dict[str, Any]):
        super().__init__(name, paths.get("config_dir", ""), paths.get("skill_dir", ""))


def get_adapter(name: str, paths: dict[str, Any] | None = None) -> ProviderAdapter:
    normalized = name.strip().lower()
    if normalized == "codex":
        return CodexAdapter(paths)
    if normalized == "agy":
        return AgyAdapter(paths)
    return GenericAdapter(normalized, paths or {})

