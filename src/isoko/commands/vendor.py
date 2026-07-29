"""isoko vendor — Vendor dependencies into the project."""

from __future__ import annotations

import os
import shutil

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.lockfile import find_lockfile, load_lockfile
from isoko.cache import PackageCache


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("vendor", help="Vendor dependencies locally")
    p.add_argument("--directory", "-d", default="vendor",
                   help="Vendor directory (default: vendor)")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    vendor_dir = os.path.join(project_dir, getattr(args, "directory", "vendor"))

    output.header(f"Vendoring dependencies for {m.full_name}")

    lock_path = find_lockfile()
    if not lock_path:
        output.error("no lock file found. Run 'isoko install' first.")
        return 1

    lock = load_lockfile(lock_path)
    if not lock:
        return 1

    cache = PackageCache()
    os.makedirs(vendor_dir, exist_ok=True)

    vendored = 0
    for name, entry in lock.entries.items():
        pkg_dir = cache.get(name, entry.version)
        if pkg_dir is None:
            output.warning(f"  {name}@{entry.version}: not in cache, skipping")
            continue

        dest = os.path.join(vendor_dir, name)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(pkg_dir, dest)
        vendored += 1
        output.info(f"  {name}@{entry.version}")

    output.success(f"Vendored {vendored} package(s) into {os.path.relpath(vendor_dir, project_dir)}/")
    return 0
