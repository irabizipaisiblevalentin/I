"""isoko clean — Clean build artifacts."""

from __future__ import annotations

import os
import shutil

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("clean", help="Clean build artifacts")
    p.add_argument("--all", action="store_true",
                   help="Also clean cache and dependencies")
    p.add_argument("--target", default="build",
                   help="Build directory to clean")


def run(args) -> int:
    manifest_path = find_manifest()
    project_dir = os.path.dirname(manifest_path) if manifest_path else os.getcwd()
    clean_all = getattr(args, "all", False)
    target = getattr(args, "target", "build")

    output.header("Cleaning")

    # Clean build directory
    build_dir = os.path.join(project_dir, target)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        output.success(f"Removed {target}/")
    else:
        output.dim(f"  {target}/ not found, skipping")

    # Clean __pycache__ dirs
    cleaned = 0
    for root, dirs, _ in os.walk(project_dir):
        if "__pycache__" in dirs:
            pycache = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache)
            cleaned += 1
    if cleaned:
        output.success(f"Removed {cleaned} __pycache__ directory(ies)")

    if clean_all:
        # Clean lock file
        lock_path = os.path.join(project_dir, "ilang.lock")
        if os.path.exists(lock_path):
            os.remove(lock_path)
            output.success("Removed ilang.lock")

        # Clean dependencies
        deps_dir = os.path.join(project_dir, ".isoko")
        if os.path.exists(deps_dir):
            shutil.rmtree(deps_dir)
            output.success("Removed .isoko/")

    output.success("Clean complete")
    return 0
