"""isoko doctor — Diagnose common issues."""

from __future__ import annotations

import os
import platform
import shutil
import sys

from isoko import output


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("doctor", help="Diagnose project issues")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    output.header("isoko doctor")

    checks = []
    errors = 0
    warnings = 0

    # Python version
    py_ver = sys.version.split()[0]
    checks.append(("Python", py_ver, "ok" if sys.version_info >= (3, 8) else "error"))
    if sys.version_info < (3, 8):
        errors += 1

    # Platform
    checks.append(("Platform", platform.platform(), "ok"))

    # isoko version
    from isoko import __version__
    checks.append(("isoko", __version__, "ok"))

    # ilang.toml
    from isoko.manifest import find_manifest
    manifest_path = find_manifest()
    if manifest_path:
        checks.append(("ilang.toml", manifest_path, "ok"))
    else:
        checks.append(("ilang.toml", "not found", "warning"))
        warnings += 1

    # Lock file
    from isoko.lockfile import find_lockfile
    lock_path = find_lockfile()
    if lock_path:
        checks.append(("ilang.lock", lock_path, "ok"))
    else:
        checks.append(("ilang.lock", "not found", "info"))

    # Compiler
    try:
        import compiler
        checks.append(("compiler", "available", "ok"))
    except ImportError:
        checks.append(("compiler", "not found", "warning"))
        warnings += 1

    # VM
    try:
        import vm
        checks.append(("vm", "available", "ok"))
    except ImportError:
        checks.append(("vm", "not found", "warning"))
        warnings += 1

    # stdlib
    try:
        import stdlib
        checks.append(("stdlib", "available", "ok"))
    except ImportError:
        checks.append(("stdlib", "not found", "info"))

    # Cache directory
    cache_dir = os.path.join(os.path.expanduser("~"), ".isoko", "cache")
    if os.path.exists(cache_dir):
        checks.append(("cache", cache_dir, "ok"))
    else:
        checks.append(("cache", "not initialized", "info"))

    # Network connectivity
    checks.append(("network", "connectivity not tested", "info"))

    # Print results
    for name, detail, status in checks:
        if status == "ok":
            output.success(f"{name}: {detail}")
        elif status == "error":
            output.error(f"{name}: {detail}")
            errors += 1
        elif status == "warning":
            output.warning(f"{name}: {detail}")
        else:
            output.info(f"{name}: {detail}")

    output.header("Summary")
    output.label_value("Errors", str(errors))
    output.label_value("Warnings", str(warnings))

    if errors == 0:
        output.success("All checks passed")
    else:
        output.error(f"{errors} error(s) found")

    return 1 if errors > 0 else 0
