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
    sub = command.add_subparsers(dest="action", required=False)
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


def main_menu() -> int:
    print("\nAI Manager")
    print("Manage profiles, quotas, skills, and failover.\n")
    choice = select_option("What would you like to do?", ["create", "add", "view", "delete", "quota", "skills", "exit"])
    if choice == "exit":
        print("Goodbye.")
        return 0
    if choice == "create":
        return main(["setup"])
    if choice == "view":
        return main(["list"])
    if choice == "quota":
        return main(["quota"])
    if choice == "add":
        return main(["add", input("Profile name: ").strip()])
    if choice == "delete":
        return main(["remove", input("Profile name to delete: ").strip()])
    policy = select_option("Skill sharing mode:", ["all", "selected", "separate"])
    skills = []
    if policy == "selected":
        skills = [item.strip() for item in input("Skill names (comma-separated): ").split(",") if item.strip()]
    return main(["policy", policy, "--skills", *skills])


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.action is None:
        return main_menu()
    if args.action == "setup":
        interactive = any(value is None for value in (args.provider, args.count, args.base_name, args.future_additions, args.policy))
        if not args.provider:
            args.provider = select_option("Choose AI provider", ["codex", "agy", "other"], step=1, total=5)
            if args.provider == "other":
                args.provider = input("Custom agent type: ").strip()
        if not args.count:
            while True:
                try:
                    args.count = int(input("Step 2 of 5 — How many profiles? ").strip())
                    if args.count > 0:
                        break
                except ValueError:
                    pass
                print("Enter a positive whole number.")
        if args.count < 1:
            raise ValueError("count must be positive")
        base = args.base_name
        if not base:
            base = input(f"Step 3 of 5 — Profile name prefix [{args.provider.lower()}]: ").strip() or args.provider.lower()
        config = default_config(args.provider)
        future = args.future_additions
        if future is None:
            future = select_option("Will you add more profiles later?", ["yes", "no"], step=4, total=5)
        config["future_additions"] = future in {"y", "yes"}
        for index in range(args.count):
            add_account(config, base if index == 0 else f"{base}{index + 1}")
        policy = args.policy
        if policy is None:
            policy = select_option("How should skills be shared?", ["all", "selected", "separate"], step=5, total=5)
        skills_path = args.skills_path
        skills = args.skills
        if policy == "selected" and not skills:
            skills = [item for item in input("Selected skill names (comma-separated): ").split(",") if item.strip()]
        set_skill_policy(config, policy, skills_path, skills)
        if interactive:
            print("\nConfiguration preview")
            print(f"  Provider: {config['provider']}")
            print(f"  Profiles: {', '.join(account['name'] for account in config['accounts'])}")
            print(f"  Add more later: {'yes' if config['future_additions'] else 'no'}")
            print(f"  Skill sharing: {policy}")
            confirmation = select_option("Create this configuration?", ["create", "cancel"])
            if confirmation == "cancel":
                print("Cancelled; no files were changed.")
                return 0
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
