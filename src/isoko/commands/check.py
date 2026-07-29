"""isoko check — Check project for common issues."""

from __future__ import annotations

import os
import sys
from typing import List, Tuple

from isoko import output
from isoko.manifest import Manifest, load as load_manifest, find_manifest
from isoko.lockfile import find_lockfile, load_lockfile
from isoko import security


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("check", help="Check project for issues")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    issues: List[Tuple[str, str]] = []

    output.header(f"Checking {m.full_name}")

    # Check manifest
    if not m.name:
        issues.append(("error", "package name is empty"))
    if not m.version:
        issues.append(("error", "package version is empty"))

    # Check source directory
    lib_dir = os.path.join(project_dir, m.lib or "lib")
    if not os.path.exists(lib_dir):
        issues.append(("warning", f"source directory not found: {m.lib or 'lib'}"))
    else:
        i_files = [f for f in os.listdir(lib_dir) if f.endswith(".i")]
        if not i_files:
            issues.append(("warning", "no .i source files found"))

    # Check tests
    tests_dir = os.path.join(project_dir, "tests")
    if not os.path.exists(tests_dir):
        issues.append(("info", "no tests directory"))
    else:
        test_files = [f for f in os.listdir(tests_dir) if f.endswith(".i")]
        if not test_files:
            issues.append(("info", "no test files found"))

    # Check lock file
    lock_path = find_lockfile()
    if lock_path:
        lf = load_lockfile(lock_path)
        if lf:
            output.info(f"Lock file: {len(lf.entries)} locked packages")
    else:
        issues.append(("info", "no lock file (run 'isoko install' to create one)"))

    # Check dependency versions
    for name, spec in m.dependencies.items():
        if not spec or spec == "*":
            issues.append(("warning", f"dependency '{name}' has no version constraint"))

    # Print results
    if not issues:
        output.success("No issues found")
        return 0

    for severity, msg in issues:
        if severity == "error":
            output.error(msg)
        elif severity == "warning":
            output.warning(msg)
        else:
            output.info(msg)

    errors = sum(1 for s, _ in issues if s == "error")
    return 1 if errors > 0 else 0
