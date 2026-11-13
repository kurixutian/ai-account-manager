import json
import os
import tempfile
from pathlib import Path
from typing import Any


def default_config(provider: str) -> dict[str, Any]:
    return {
        "version": 1,
        "provider": provider.strip().lower(),
        "future_additions": True,
        "accounts": [],
        "skills": {"policy": "separate", "path": "", "names": []},
    }


def validate_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict) or config.get("version") != 1:
        raise ValueError("unsupported configuration")
    if not isinstance(config.get("provider"), str) or not config["provider"].strip():
        raise ValueError("provider must be a non-empty string")
    accounts = config.get("accounts")
    if not isinstance(accounts, list):
        raise ValueError("accounts must be a list")
    names = [item.get("name") for item in accounts if isinstance(item, dict)]
    if len(names) != len(accounts) or any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError("each account needs a name")
    if len(names) != len(set(names)):
        raise ValueError("duplicate account names")
    skills = config.get("skills")
    if not isinstance(skills, dict) or skills.get("policy") not in {"all", "selected", "separate"}:
        raise ValueError("invalid skill policy")
    if not isinstance(skills.get("names", []), list):
        raise ValueError("skill names must be a list")


def save_config(path: str | Path, config: dict[str, Any]) -> None:
    validate_config(config)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_config(path: str | Path) -> dict[str, Any]:
    try:
        config = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read configuration: {exc}") from exc
    validate_config(config)
    return config


def export_config(path: str | Path, config: dict[str, Any]) -> None:
    save_config(path, config)


def import_config(path: str | Path) -> dict[str, Any]:
    return load_config(path)

