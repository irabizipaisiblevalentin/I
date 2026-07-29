"""isoko update — Update dependencies to latest compatible versions."""

from __future__ import annotations

import os

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.resolver import Resolver, ConflictError
from isoko.lockfile import LockFile, LockEntry, load_lockfile, save_lockfile, find_lockfile
from isoko.cache import PackageCache
from isoko.registry import RegistryClient, RegistryConfig


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("update", help="Update dependencies")
    p.add_argument("packages", nargs="*",
                   help="Specific packages to update (empty = update all)")
    p.add_argument("--registry", help="Registry URL")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    target_packages = getattr(args, "packages", [])
    registry_url = getattr(args, "registry", None)

    output.header(f"Updating dependencies for {m.full_name}")

    config = RegistryConfig(url=registry_url or "https://registry.i-lang.dev")
    registry = RegistryClient(config)
    cache = PackageCache()

    # Filter to target packages if specified
    all_deps = dict(m.dependencies)
    all_deps.update(m.dev_dependencies)
    all_deps.update(m.build_dependencies)

    if target_packages:
        for pkg in target_packages:
            if pkg not in all_deps:
                output.warning(f"{pkg} is not a dependency")
                continue

    # Resolve updated versions
    try:
        resolver = Resolver(registry)
        resolved = resolver.resolve(m)

        # Create updated lock file
        lock = LockFile(m.name)
        for name, node in resolved.items():
            lock.add(LockEntry(
                name=name,
                version=str(node.version),
                source="registry",
                dependencies={k: v for k, v in node.deps.items() if k in resolved},
            ))

        lock_path = os.path.join(project_dir, "ilang.lock")
        save_lockfile(lock, lock_path)

        output.success(f"Updated {len(resolved)} package(s)")
        output.dim(f"  Lock file: ilang.lock")

        for name, node in resolved.items():
            output.info(f"  {name}@{node.version}")

    except ConflictError as e:
        output.error(str(e))
        for c in e.conflicts:
            output.dim(f"  - {c}")
        return 1

    return 0
