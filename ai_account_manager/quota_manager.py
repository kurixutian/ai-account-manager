import json
import subprocess
from datetime import datetime
from typing import Any


def normalize_quota(result: dict[str, Any]) -> dict[str, Any]:
    status = result.get("status", "unknown")
    if status not in {"available", "exhausted", "unknown"}:
        raise ValueError("quota status must be available, exhausted, or unknown")
    normalized = {"status": status, "remaining": result.get("remaining"), "limit": result.get("limit"), "reset_at": result.get("reset_at")}
    normalized["checked_at"] = result.get("checked_at") or datetime.now().astimezone().isoformat()
    return normalized


def check_quota(account: dict[str, Any]) -> dict[str, Any]:
    command = account.get("quota_command", [])
    if not command:
        return normalize_quota(account.get("quota", {"status": "unknown"}))
    completed = subprocess.run(command, check=True, capture_output=True, text=True, shell=False)
    return normalize_quota(json.loads(completed.stdout))


def refresh_quotas(config: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for account in config["accounts"]:
        try:
            account["quota"] = check_quota(account)
        except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError) as exc:
            account["quota"] = normalize_quota({"status": "unknown", "error": str(exc)})
        results.append(account["quota"])
    return results

