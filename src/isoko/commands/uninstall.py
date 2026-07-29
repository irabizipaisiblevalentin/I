"""isoko uninstall — Uninstall a package."""

from __future__ import annotations

import json
import os

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.lockfile import find_lockfile, load_lockfile, save_lockfile


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("uninstall", help="Uninstall a package")
    p.add_argument("packages", nargs="+", help="Packages to uninstall")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    packages = getattr(args, "packages", [])
    manifest_path = find_manifest()

    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    removed = 0

    for pkg in packages:
        found = False

        # Remove from regular dependencies
        if pkg in m.dependencies:
            del m.dependencies[pkg]
            found = True

        # Remove from dev dependencies
        if pkg in m.dev_dependencies:
            del m.dev_dependencies[pkg]
            found = True

        # Remove from build dependencies
        if pkg in m.build_dependencies:
            del m.build_dependencies[pkg]
            found = True

        # Remove from optional dependencies
        if pkg in m.optional_dependencies:
            del m.optional_dependencies[pkg]
            found = True

        if found:
            output.success(f"Removed {pkg} from {m.full_name}")
            removed += 1
        else:
            output.warning(f"{pkg} is not a dependency of {m.name}")

    # Save updated manifest
    if removed > 0:
        from isoko.commands.init import _write_toml
        _write_toml(m, manifest_path)

        # Update lock file
        lock_path = find_lockfile(project_dir)
        if lock_path:
            lock = load_lockfile(lock_path)
            if lock:
                for pkg in packages:
                    lock.remove(pkg)
                save_lockfile(lock, lock_path)

        output.info(f"Removed {removed} package(s)")

    return 0
