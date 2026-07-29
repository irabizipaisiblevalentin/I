"""isoko verify — Verify package integrity."""

from __future__ import annotations

import os

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.lockfile import find_lockfile, load_lockfile
from isoko.cache import PackageCache, verify_cached
from isoko import security


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("verify", help="Verify package integrity")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    output.header(f"Verifying {m.full_name}")

    lock_path = find_lockfile()
    if not lock_path:
        output.warning("no lock file found. Nothing to verify.")
        return 0

    lock = load_lockfile(lock_path)
    if not lock or not lock.entries:
        output.warning("lock file is empty")
        return 0

    cache = PackageCache()
    verified = 0
    failed = 0
    missing = 0

    for name, entry in lock.entries.items():
        if not cache.has(name, entry.version):
            output.warning(f"{name}@{entry.version}: not cached")
            missing += 1
            continue

        if verify_cached(cache, name, entry.version):
            verified += 1
            output.success(f"{name}@{entry.version}")
        else:
            failed += 1
            output.error(f"{name}@{entry.version}: checksum mismatch")

    output.header("Summary")
    output.label_value("Verified", str(verified))
    output.label_value("Failed", str(failed))
    output.label_value("Missing", str(missing))

    return 1 if failed > 0 else 0
