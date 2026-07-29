"""isoko logout — Logout from the registry."""

from __future__ import annotations

import json
import os

from isoko import output


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("logout", help="Logout from registry")
    p.add_argument("--registry", default="https://registry.i-lang.dev",
                   help="Registry URL")


def run(args) -> int:
    registry_url = getattr(args, "registry", "https://registry.i-lang.dev")

    config_path = os.path.join(os.path.expanduser("~"), ".isoko", "config.json")
    if not os.path.exists(config_path):
        output.warning("Not logged in")
        return 0

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        output.warning("Not logged in")
        return 0

    registries = config.get("registries", {})
    if registry_url in registries:
        del registries[registry_url]
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        output.success(f"Logged out from {registry_url}")
    else:
        output.warning(f"Not logged in to {registry_url}")

    return 0
