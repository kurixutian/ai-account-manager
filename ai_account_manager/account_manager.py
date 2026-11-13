import re
import subprocess
from typing import Any


def account_names(config: dict[str, Any]) -> list[str]:
    return [account["name"] for account in config["accounts"]]


def next_name(config: dict[str, Any], base: str) -> str:
    base = base.strip()
    if not base:
        raise ValueError("account name cannot be empty")
    if base not in account_names(config):
        return base
    index = 2
    while f"{base}{index}" in account_names(config):
        index += 1
    return f"{base}{index}"


def add_account(config: dict[str, Any], name: str, command: list[str] | None = None) -> dict[str, Any]:
    candidate = name.strip()
    if not candidate or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", candidate):
        raise ValueError("account name must use letters, numbers, dot, underscore, or hyphen")
    if candidate in account_names(config):
        if candidate[-1].isdigit():
            raise ValueError(f"account already exists: {candidate}")
        candidate = next_name(config, candidate)
    account = {"name": candidate, "command": list(command or []), "quota": {"status": "unknown"}}
    config["accounts"].append(account)
    return account


def remove_account(config: dict[str, Any], name: str) -> None:
    before = len(config["accounts"])
    config["accounts"] = [account for account in config["accounts"] if account["name"] != name]
    if len(config["accounts"]) == before:
        raise ValueError(f"account not found: {name}")


def choose_available_account(config: dict[str, Any]) -> dict[str, Any]:
    for account in config["accounts"]:
        if account.get("quota", {}).get("status") == "available":
            return account
    raise RuntimeError("no account with confirmed available quota")


def launch_account(account: dict[str, Any], runner=None) -> None:
    command = account.get("command", [])
    if not command:
        raise ValueError(f"no launch command configured for {account['name']}")
    (runner or (lambda args: subprocess.Popen(args, shell=False)))(list(command))

