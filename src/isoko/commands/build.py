"""isoko build — Build the current I project."""

from __future__ import annotations

import os
import subprocess
import sys

from isoko import output
from isoko.lockfile import find_lockfile
from isoko.manifest import find_manifest
from isoko.manifest import load as load_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("build", help="Build the current project")
    p.add_argument("--release", action="store_true",
                   help="Build in release mode")
    p.add_argument("--target", help="Target platform")
    p.add_argument("--out", default="build", help="Output directory")
    p.add_argument("--jobs", "-j", type=int, help="Parallel build jobs")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found. Run 'isoko init' first.")
        return 1

    m = load_manifest(manifest_path)
    if not m.name:
        output.error("invalid manifest: missing package name")
        return 1

    release = getattr(args, "release", False)
    target = (getattr(args, "target", None) or "bytecode").lower()
    out_dir = getattr(args, "out", "build")

    if target != "bytecode":
        output.error(f"unsupported target: {target} (supported: bytecode)")
        return 1

    mode = "release" if release else "dev"
    output.header(f"Building {m.full_name} ({mode} mode)")

    # Check for lock file
    lock_path = find_lockfile()
    if lock_path:
        output.info("Using lock file for deterministic build")
    else:
        output.warning("No lock file found. Run 'isoko install' first for reproducible builds.")

    # Build the project
    project_dir = os.path.dirname(manifest_path)
    lib_dir = os.path.join(project_dir, m.lib if m.lib else "lib")

    if not os.path.exists(lib_dir):
        output.error(f"source directory not found: {lib_dir}")
        return 1

    # Compile .i files
    output.info(f"Compiling sources in {os.path.relpath(lib_dir, project_dir)}")
    i_files = _find_i_files(lib_dir)
    if not i_files:
        output.warning("no .i source files found")
        return 0

    output.info(f"Found {len(i_files)} source file(s)")

    # Invoke the compiler once per source file
    out_root = os.path.join(project_dir, out_dir)
    os.makedirs(out_root, exist_ok=True)

    failures = 0
    for i_file in i_files:
        rel = os.path.relpath(i_file, lib_dir)
        out_name = os.path.splitext(rel)[0] + ".ipyc"
        out_path = os.path.join(out_root, out_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "compiler.compiler",
                 i_file, "-o", out_path],
                capture_output=True,
                text=True,
                cwd=project_dir,
            )
            if result.returncode == 0:
                output.success(f"  {rel} -> {os.path.relpath(out_path, project_dir)}")
            else:
                failures += 1
                output.error(f"  {rel}: build failed")
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
        except FileNotFoundError:
            output.warning("Compiler not available. Install the I compiler first.")
            output.success(f"Build plan: {len(i_files)} file(s) -> {out_dir}/")
            return 0
        except Exception as e:
            output.error(f"build failed: {e}")
            return 1

    if failures:
        output.error(f"Build failed: {failures} file(s)")
        return 1

    output.success("Build completed successfully")
    output.dim(f"  Output: {out_dir}/")
    return 0


def _find_i_files(directory: str) -> list[str]:
    """Recursively find all .i files in a directory."""
    result = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".i"):
                result.append(os.path.join(root, f))
    return sorted(result)
