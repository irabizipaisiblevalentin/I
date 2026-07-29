"""isoko tree — Show dependency tree."""

from __future__ import annotations

import os

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.lockfile import find_lockfile, load_lockfile


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("tree", help="Show dependency tree")
    p.add_argument("--depth", "-d", type=int, default=-1,
                   help="Maximum depth (-1 for unlimited)")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    depth = getattr(args, "depth", -1)
    json_mode = getattr(args, "json", False)

    lock_path = find_lockfile()
    if not lock_path:
        output.warning("no lock file found")
        return 0

    lock = load_lockfile(lock_path)
    if not lock:
        return 0

    if json_mode:
        tree = _build_tree(m.name, lock, set())
        output.print_json(tree)
        return 0

    output.header(f"{m.name}@{m.version}")
    all_deps = dict(m.dependencies)
    all_deps.update(m.dev_dependencies)
    all_deps.update(m.build_dependencies)

    deps_list = sorted(all_deps.keys())
    for i, dep in enumerate(deps_list):
        is_last = (i == len(deps_list) - 1)
        entry = lock.get(dep)
        ver = entry.version if entry else "?"
        connector = "└── " if is_last else "├── "
        output.info(f"{connector}{dep}@{ver}")
        if depth != 0:
            _print_tree(dep, lock, set(), 1, is_last, depth)

    return 0


def _print_tree(name: str, lock, visited: set, indent: int, is_last: bool, max_depth: int) -> None:
    entry = lock.get(name)
    if not entry:
        return
    if name in visited:
        prefix = "    " * indent
        output.dim(f"{prefix}{'└── ' if is_last else '├── '}(circular)")
        return
    visited.add(name)

    deps = sorted(entry.dependencies.keys())
    for i, dep in enumerate(deps):
        dep_is_last = (i == len(deps) - 1)
        prefix = "    " * indent
        connector = "└── " if dep_is_last else "├── "
        dep_entry = lock.get(dep)
        ver = dep_entry.version if dep_entry else "?"
        output.dim(f"{prefix}{connector}{dep}@{ver}")
        if max_depth < 0 or indent < max_depth:
            _print_tree(dep, lock, visited, indent + 1, dep_is_last, max_depth)


def _build_tree(name: str, lock, visited: set) -> dict:
    entry = lock.get(name)
    if not entry:
        return {"name": name, "version": "unknown"}
    if name in visited:
        return {"name": name, "version": entry.version, "circular": True}
    visited.add(name)
    children = []
    for dep in entry.dependencies:
        children.append(_build_tree(dep, lock, visited))
    return {
        "name": name,
        "version": entry.version,
        "dependencies": children,
    }
