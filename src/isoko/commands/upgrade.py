"""isoko upgrade — Upgrade dependencies to latest versions (breaking changes allowed)."""

from __future__ import annotations

import os

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.resolver import Resolver, ConflictError
from isoko.lockfile import LockFile, LockEntry, save_lockfile, find_lockfile
from isoko.registry import RegistryClient, RegistryConfig


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("upgrade", help="Upgrade to latest versions")
    p.add_argument("packages", nargs="*",
                   help="Specific packages to upgrade")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    target_packages = getattr(args, "packages", [])

    output.header(f"Upgrading dependencies for {m.full_name}")

    # Widen version constraints to latest
    all_deps = [m.dependencies, m.dev_dependencies, m.build_dependencies]
    upgraded = []

    for deps in all_deps:
        for name, spec in list(deps.items()):
            if target_packages and name not in target_packages:
                continue
            old_spec = spec
            deps[name] = ">=0.0.0"
            upgraded.append((name, old_spec, deps[name]))

    if not upgraded:
        output.warning("no packages to upgrade")
        return 0

    for name, old, new in upgraded:
        output.info(f"  {name}: {old} -> {new}")

    # Re-resolve
    config = RegistryConfig()
    registry = RegistryClient(config)

    try:
        resolver = Resolver(registry)
        resolved = resolver.resolve(m)

        lock = LockFile(m.name)
        for name, node in resolved.items():
            lock.add(LockEntry(
                name=name,
                version=str(node.version),
                source="registry",
            ))

        lock_path = os.path.join(project_dir, "ilang.lock")
        save_lockfile(lock, lock_path)

        # Save updated manifest
        from isoko.commands.init import _write_toml
        _write_toml(m, manifest_path)

        output.success(f"Upgraded {len(upgraded)} package(s)")
    except ConflictError as e:
        output.error(str(e))
        return 1

    return 0
