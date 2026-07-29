"""isoko workspace — Manage workspace configuration."""

from __future__ import annotations

import json
import os

from isoko import output
from isoko.workspace import Workspace


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("workspace", help="Manage workspace")
    sub = p.add_subparsers(dest="ws_cmd")
    sub.add_parser("init", help="Initialize a workspace")
    sub.add_parser("list", help="List workspace packages")
    sub.add_parser("info", help="Show workspace info")
    p.add_argument("action", nargs="?", default="info",
                   help="Workspace action")


def run(args) -> int:
    action = getattr(args, "ws_cmd", None) or getattr(args, "action", "info")
    cwd = os.getcwd()

    if action == "init":
        return _init_workspace(cwd)
    elif action == "list":
        return _list_workspace(cwd)
    elif action == "info":
        return _show_workspace(cwd)
    else:
        output.error(f"unknown workspace action: {action}")
        return 1


def _init_workspace(directory: str) -> int:
    ws_path = os.path.join(directory, "ilang-workspace.json")
    if os.path.exists(ws_path):
        output.error("workspace already initialized")
        return 1

    ws = Workspace(directory)
    ws.config.members = ["packages/*"]
    ws.config.exclude = ["node_modules", "build", "vendor"]
    ws.save()

    os.makedirs(os.path.join(directory, "packages"), exist_ok=True)

    output.success("Workspace initialized")
    output.dim(f"  Config: ilang-workspace.json")
    output.dim(f"  Packages directory: packages/")
    return 0


def _list_workspace(directory: str) -> int:
    ws = Workspace(directory)
    if not ws.is_workspace():
        output.error("not a workspace (no ilang-workspace.json)")
        return 1

    ws.load()
    output.header(f"Workspace Packages ({len(ws.packages)})")
    for name, pkg in ws.packages.items():
        ver = pkg.manifest.version if pkg.manifest else "?"
        output.info(f"  {name}@{ver} ({os.path.relpath(pkg.path, directory)})")

    return 0


def _show_workspace(directory: str) -> int:
    ws = Workspace(directory)
    if not ws.is_workspace():
        output.warning("Not a workspace directory")
        return 0

    ws.load()
    output.header("Workspace Configuration")
    output.label_value("Root", ws.root)
    output.label_value("Members", ", ".join(ws.config.members))

    if ws.config.exclude:
        output.label_value("Exclude", ", ".join(ws.config.exclude))

    output.label_value("Packages", str(len(ws.packages)))
    return 0
