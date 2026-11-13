import argparse
import json
import shlex
from pathlib import Path

from .account_manager import add_account, choose_available_account, launch_account, remove_account
from .config_manager import default_config, load_config, save_config, validate_config
from .quota_manager import refresh_quotas
from .prompts import select_option
from .skill_manager import set_skill_policy


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(prog="ai-manager")
    sub = command.add_subparsers(dest="action", required=True)
    setup = sub.add_parser("setup")
    setup.add_argument("--provider")
    setup.add_argument("--count", type=int)
    setup.add_argument("--base-name")
    setup.add_argument("--future-additions", choices=["yes", "no"])
    setup.add_argument("--policy", choices=["all", "selected", "separate"])
    setup.add_argument("--skills-path", default="")
    setup.add_argument("--skills", nargs="*", default=[])
    setup.add_argument("--output", default="ai-agents.json")
    setup.add_argument("--dry-run", action="store_true")
    for name in ("list", "validate", "quota", "launch"):
        item = sub.add_parser(name)
        item.add_argument("--config", default="ai-agents.json")
    add = sub.add_parser("add")
    add.add_argument("name")
    add.add_argument("--command", nargs="*")
    add.add_argument("--config", default="ai-agents.json")
    remove = sub.add_parser("remove")
    remove.add_argument("name")
    remove.add_argument("--config", default="ai-agents.json")
    policy = sub.add_parser("policy")
    policy.add_argument("policy", choices=["all", "selected", "separate"])
    policy.add_argument("--path", default="")
    policy.add_argument("--skills", nargs="*", default=[])
    policy.add_argument("--config", default="ai-agents.json")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.action == "setup":
        if not args.provider:
            args.provider = select_option("AI agent type:", ["codex", "agy", "other"])
            if args.provider == "other":
                args.provider = input("Custom agent type: ").strip()
        if not args.count:
            args.count = int(input("How many accounts? "))
        if args.count < 1:
            raise ValueError("count must be positive")
        base = args.base_name
        if not base:
            base = input(f"Base account name [{args.provider.lower()}]: ").strip() or args.provider.lower()
        config = default_config(args.provider)
        future = args.future_additions
        if future is None:
            future = select_option("Will you add more accounts later?", ["yes", "no"])
        config["future_additions"] = future in {"y", "yes"}
        for index in range(args.count):
            add_account(config, base if index == 0 else f"{base}{index + 1}")
        policy = args.policy
        if policy is None:
            policy = select_option("Skill sharing:", ["all", "selected", "separate"])
        skills_path = args.skills_path
        skills = args.skills
        if policy == "selected" and not skills:
            skills = [item for item in input("Shared skill names (comma-separated): ").split(",") if item.strip()]
        set_skill_policy(config, policy, skills_path, skills)
        if args.dry_run:
            print("dry-run: would write " + str(Path(args.output)))
        else:
            save_config(args.output, config)
            print(f"created {args.output}")
        return 0
    config_path = getattr(args, "config", "ai-agents.json")
    config = load_config(config_path)
    if args.action == "list":
        for account in config["accounts"]:
            quota = account.get("quota", {})
            print(f"{account['name']}: {quota.get('status', 'unknown')} reset={quota.get('reset_at', 'unknown')}")
    elif args.action == "validate":
        validate_config(config)
        print("valid")
    elif args.action == "quota":
        refresh_quotas(config)
        save_config(config_path, config)
        for account in config["accounts"]:
            print(json.dumps({"name": account["name"], **account["quota"]}))
    elif args.action == "launch":
        refresh_quotas(config)
        account = choose_available_account(config)
        print("launching " + account["name"] + ": " + shlex.join(account["command"]))
        launch_account(account)
    elif args.action == "add":
        add_account(config, args.name, args.command)
        save_config(config_path, config)
    elif args.action == "remove":
        remove_account(config, args.name)
        save_config(config_path, config)
    elif args.action == "policy":
        set_skill_policy(config, args.policy, args.path, args.skills)
        save_config(config_path, config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
