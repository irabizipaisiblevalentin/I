"""isoko graph — Show dependency graph."""

from __future__ import annotations

import json
import os

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.lockfile import find_lockfile, load_lockfile


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("graph", help="Show dependency graph")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")
    p.add_argument("--dot", action="store_true",
                   help="Output as DOT graph")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    json_mode = getattr(args, "json", False)
    dot_mode = getattr(args, "dot", False)

    output.header(f"Dependency graph for {m.full_name}")

    lock_path = find_lockfile()
    if not lock_path:
        output.warning("no lock file found")
        return 0

    lock = load_lockfile(lock_path)
    if not lock:
        return 0

    if json_mode:
        data = {
            name: {
                "version": entry.version,
                "dependencies": entry.dependencies,
            }
            for name, entry in lock.entries.items()
        }
        output.print_json(data)
        return 0

    if dot_mode:
        print("digraph dependencies {")
        for name, entry in lock.entries.items():
            for dep in entry.dependencies:
                if dep in lock.entries:
                    print(f'  "{name}" -> "{dep}";')
        print("}")
        return 0

    # Print as tree
    output.info(f"{m.name}@{m.version}")
    all_deps = dict(m.dependencies)
    all_deps.update(m.dev_dependencies)
    all_deps.update(m.build_dependencies)

    _print_graph(m.name, lock, set(), 0)
    return 0


def _print_graph(name: str, lock, visited: set, depth: int) -> None:
    entry = lock.get(name)
    if not entry:
        return
    if name in visited:
        output.dim("  " * (depth + 1) + f"(circular: {name})")
        return
    visited.add(name)

    for dep_name in entry.dependencies:
        dep_entry = lock.get(dep_name)
        prefix = "  " * (depth + 1)
        if dep_entry:
            output.dim(f"{prefix}{dep_name}@{dep_entry.version}")
            _print_graph(dep_name, lock, visited, depth + 1)
        else:
            output.dim(f"{prefix}{dep_name} (not resolved)")
