"""isoko login — Authenticate with the registry."""

from __future__ import annotations

import json
import os

from isoko import output


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("login", help="Login to registry")
    p.add_argument("--registry", default="https://registry.i-lang.dev",
                   help="Registry URL")
    p.add_argument("--token", help="Auth token (skips interactive prompt)")


def run(args) -> int:
    registry_url = getattr(args, "registry", "https://registry.i-lang.dev")
    token = getattr(args, "token", None)

    output.header("Login to Registry")

    if not token:
        try:
            token = input("  Enter registry token: ").strip()
        except (EOFError, KeyboardInterrupt):
            output.error("Login cancelled")
            return 1

    if not token:
        output.error("token is required")
        return 1

    config_path = os.path.join(os.path.expanduser("~"), ".isoko", "config.json")
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    registries = config.setdefault("registries", {})
    registries[registry_url] = {"token": token}

    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # Restrict the credentials file (and its directory) to the current user.
    # On Windows os.chmod is largely a no-op, which is acceptable because
    # ACL-based protection is enforced by the account profile directory.
    try:
        os.chmod(config_dir, 0o700)
        os.chmod(config_path, 0o600)
    except OSError:
        pass

    output.success(f"Logged in to {registry_url}")
    return 0
