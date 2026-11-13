import os
from typing import Any


def set_skill_policy(config: dict[str, Any], policy: str, path: str = "", names: list[str] | None = None) -> None:
    if policy not in {"all", "selected", "separate"}:
        raise ValueError("policy must be all, selected, or separate")
    selected = [name.strip() for name in (names or []) if name.strip()]
    if policy == "selected" and not selected:
        raise ValueError("selected policy requires at least one skill")
    config["skills"] = {"policy": policy, "path": os.path.abspath(os.path.expanduser(path)) if path else "", "names": selected}

