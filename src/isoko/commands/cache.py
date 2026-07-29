"""isoko cache — Manage the package cache."""

from __future__ import annotations

import os

from isoko import output
from isoko.cache import PackageCache, CacheConfig


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("cache", help="Manage package cache")
    sub = p.add_subparsers(dest="cache_cmd")
    sub.add_parser("list", help="List cached packages")
    sub.add_parser("clean", help="Remove all cached packages")
    sub.add_parser("size", help="Show cache size")
    sub.add_parser("verify", help="Verify cache integrity")
    p.add_argument("action", nargs="?", default="list",
                   help="Cache action")


def run(args) -> int:
    action = getattr(args, "cache_cmd", None) or getattr(args, "action", "list")
    cache = PackageCache()

    if action == "list":
        packages = cache.list_packages()
        if not packages:
            output.info("Cache is empty")
            return 0
        output.header(f"Cached Packages ({len(packages)})")
        for entry in packages:
            size_mb = entry.size / (1024 * 1024)
            output.info(f"  {entry.name}@{entry.version} ({size_mb:.1f} MB)")

    elif action == "clean":
        count = cache.clear()
        output.success(f"Removed {count} cached package(s)")

    elif action == "size":
        stats = cache.stats()
        output.header("Cache Statistics")
        output.label_value("Packages", str(stats["total_packages"]))
        output.label_value("Total Size", f"{stats['total_size_mb']:.1f} MB")
        output.label_value("Location", stats["cache_dir"])

    elif action == "verify":
        from isoko.cache import verify_cached
        packages = cache.list_packages()
        ok = 0
        for entry in packages:
            if verify_cached(cache, entry.name, entry.version):
                ok += 1
            else:
                output.error(f"  {entry.name}@{entry.version}: checksum mismatch")
        output.success(f"Verified {ok}/{len(packages)} packages")

    else:
        output.error(f"unknown cache action: {action}")
        return 1

    return 0
