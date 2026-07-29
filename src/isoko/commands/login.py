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

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    output.success(f"Logged in to {registry_url}")
    return 0
