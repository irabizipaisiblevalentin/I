"""isoko install — Install dependencies."""

from __future__ import annotations

import os
import sys
from typing import Dict

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.resolver import Resolver, ConflictError
from isoko.lockfile import LockFile, LockEntry, load_lockfile, save_lockfile, find_lockfile, create_from_resolved
from isoko.cache import PackageCache
from isoko.registry import RegistryClient, RegistryConfig


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("install", help="Install dependencies")
    p.add_argument("packages", nargs="*",
                   help="Packages to install (empty = install from manifest)")
    p.add_argument("--locked", action="store_true",
                   help="Only install from lock file")
    p.add_argument("--offline", action="store_true",
                   help="Install from cache only")
    p.add_argument("--registry", help="Registry URL")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path and not getattr(args, "packages", []):
        output.error("no ilang.toml found. Run 'isoko init' first.")
        return 1

    target_packages = getattr(args, "packages", [])
    locked = getattr(args, "locked", False)
    offline = getattr(args, "offline", False)
    registry_url = getattr(args, "registry", None)

    project_dir = os.path.dirname(manifest_path) if manifest_path else os.getcwd()

    if manifest_path:
        m = load_manifest(manifest_path)
        output.header(f"Installing dependencies for {m.full_name}")
    else:
        m = None
        output.header("Installing packages")

    # Load/create lock file
    lock_path = find_lockfile(project_dir)
    lock = load_lockfile(lock_path) if lock_path else None
    if lock is None:
        lock = LockFile(m.name if m else "project")

    # Set up registry and cache
    config = RegistryConfig(
        url=registry_url or "https://registry.i-lang.dev",
        offline=offline,
    )
    registry = RegistryClient(config)
    cache = PackageCache()

    if target_packages:
        # Install specific packages
        for pkg_spec in target_packages:
            name, version_spec = _parse_pkg_spec(pkg_spec)
            output.info(f"Installing {name}@{version_spec}")
            result = _install_package(name, version_spec, registry, cache, lock)
            if not result:
                output.error(f"Failed to install {name}")
                return 1
            output.success(f"Installed {name}@{result}")
    elif locked:
        # Install from lock file only
        if not lock:
            output.error("no lock file found")
            return 1
        output.info(f"Installing {len(lock.entries)} locked package(s)")
        for name, entry in lock.entries.items():
            result = _install_package(name, entry.version, registry, cache, lock)
            if result:
                output.info(f"  {name}@{result}")
    elif m:
        # Resolve all dependencies
        output.info("Resolving dependencies...")
        try:
            resolver = Resolver(registry)
            resolved = resolver.resolve(m)

            # Update lock file
            lock.project_name = m.name
            for name, node in resolved.items():
                lock.add(LockEntry(
                    name=name,
                    version=str(node.version),
                    source="registry",
                    dependencies={k: v for k, v in node.deps.items() if k in resolved},
                ))

            # Save lock file
            new_lock_path = os.path.join(project_dir, "ilang.lock")
            save_lockfile(lock, new_lock_path)

            # Download and cache
            ordered = resolver.topological_sort(resolved)
            total = len(ordered)
            output.info(f"Resolved {total} package(s)")

            for i, node in enumerate(ordered):
                downloading = not cache.has(node.name, str(node.version))
                if downloading:
                    output.downloading(node.name, str(node.version))
                result = _install_package(
                    node.name, str(node.version), registry, cache, lock
                )
                if result:
                    status = "cached" if not downloading else "installed"
                    output.dim(f"    {node.name}@{node.version} ({status})")

            output.success(f"Installed {total} package(s)")
            output.dim(f"  Lock file: ilang.lock")

        except ConflictError as e:
            output.error(str(e))
            for conflict in e.conflicts:
                output.dim(f"  - {conflict}")
            return 1
    else:
        output.error("no manifest or packages specified")
        return 1

    return 0


def _parse_pkg_spec(spec: str):
    if "@" in spec:
        name, version = spec.rsplit("@", 1)
        return name, version or "*"
    if "/" in spec:
        parts = spec.split("/")
        return parts[0], parts[1] if len(parts) > 1 else "*"
    return spec, "*"


def _install_package(name: str, version: str, registry, cache, lock):
    """Install a single package. Returns actual version or None."""
    from isoko.semver import Version, max_satisfying

    if cache.has(name, version):
        cache_path = cache.get(name, version)
        return version

    try:
        versions = registry.get_versions(name)
        if not versions:
            return None
        resolved = max_satisfying(versions, version)
        if not resolved:
            return None
        ver_str = str(resolved)

        data = registry.download(name, ver_str)
        if data:
            tarball_path = cache.put_tarball(name, ver_str, data)
            return ver_str
    except Exception:
        pass
    return None
