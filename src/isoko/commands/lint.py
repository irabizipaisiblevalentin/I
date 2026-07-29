"""isoko lint — Lint I source code."""

from __future__ import annotations

import os
import re
import sys
from typing import List, Tuple

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("lint", help="Lint source code")
    p.add_argument("path", nargs="?", help="File or directory to lint")
    p.add_argument("--fix", action="store_true",
                   help="Automatically fix issues")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    manifest_path = find_manifest()
    path = getattr(args, "path", None)
    fix_mode = getattr(args, "fix", False)

    if path:
        target = path
    elif manifest_path:
        m = load_manifest(manifest_path)
        target = os.path.join(os.path.dirname(manifest_path), m.lib or "lib")
    else:
        target = "."

    output.header(f"Linting {target}")

    files = _find_i_files(target)
    if not files:
        output.warning("no .i files found")
        return 0

    total_issues = 0
    for f in files:
        issues = _lint_file(f)
        total_issues += len(issues)
        for severity, line, col, msg in issues:
            loc = f"{os.path.basename(f)}:{line}"
            if severity == "error":
                output.error(f"{loc}: {msg}")
            elif severity == "warning":
                output.warning(f"{loc}: {msg}")
            else:
                output.info(f"{loc}: {msg}")

    if total_issues == 0:
        output.success("No lint issues found")
        return 0
    else:
        output.error(f"Found {total_issues} issue(s)")
        return 1


def _lint_file(path: str) -> List[Tuple[str, int, int, str]]:
    """Lint a single .i file and return issues."""
    issues = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return [("error", 0, 0, f"cannot read file: {path}")]

    for i, line in enumerate(lines, 1):
        stripped = line.rstrip()

        # Trailing whitespace
        if stripped != line.rstrip("\n") and stripped:
            if line.rstrip("\n") != line.rstrip():
                issues.append(("info", i, len(stripped), "trailing whitespace"))

        # Long lines (> 120 chars)
        if len(line.rstrip()) > 120:
            issues.append(("warning", i, 120, "line exceeds 120 characters"))

        # Tab characters
        if "\t" in line:
            issues.append(("warning", i, 0, "use spaces instead of tabs"))

        # Debug statements
        if re.match(r"^\s*andika\s*\(\s*\"DEBUG", stripped):
            issues.append(("warning", i, 0, "possible debug statement left in code"))

    return issues


def _find_i_files(path: str) -> List[str]:
    if os.path.isfile(path) and path.endswith(".i"):
        return [path]
    if not os.path.isdir(path):
        return []
    files = []
    for root, _, fnames in os.walk(path):
        for f in fnames:
            if f.endswith(".i"):
                files.append(os.path.join(root, f))
    return sorted(files)
