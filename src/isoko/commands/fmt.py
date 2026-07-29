"""isoko fmt — Format I source code."""

from __future__ import annotations

import os
import sys
from typing import List

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("fmt", help="Format source code")
    p.add_argument("path", nargs="?", help="File or directory to format")
    p.add_argument("--check", action="store_true",
                   help="Check formatting without modifying files")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    manifest_path = find_manifest()
    path = getattr(args, "path", None)
    check_mode = getattr(args, "check", False)

    if path:
        target = path
    elif manifest_path:
        m = load_manifest(manifest_path)
        target = os.path.join(os.path.dirname(manifest_path), m.lib or "lib")
    else:
        target = "."

    output.header(f"{'Checking' if check_mode else 'Formatting'} {target}")

    files = _find_i_files(target)
    if not files:
        output.warning("no .i files found")
        return 0

    output.info(f"Found {len(files)} .i file(s)")

    formatted = 0
    needs_format = 0

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                original = fh.read()
            formatted_text = _format_i_code(original)
            if original != formatted_text:
                needs_format += 1
                if not check_mode:
                    with open(f, "w", encoding="utf-8") as fh:
                        fh.write(formatted_text)
                    output.info(f"Formatted {os.path.basename(f)}")
                else:
                    output.warning(f"Needs formatting: {f}")
            else:
                formatted += 1
        except Exception as e:
            output.error(f"Failed to process {f}: {e}")

    if check_mode:
        if needs_format == 0:
            output.success("All files are properly formatted")
            return 0
        else:
            output.error(f"{needs_format} file(s) need formatting")
            return 1
    else:
        output.success(f"Formatted {formatted} file(s), {needs_format} changed")
        return 0


def _format_i_code(code: str) -> str:
    """Basic I code formatter."""
    lines = code.split("\n")
    result = []
    indent = 0
    indent_str = "    "

    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append("")
            continue

        # Decrease indent for block-end keywords
        if stripped.startswith("iherezo") or stripped.startswith("end"):
            indent = max(0, indent - 1)

        formatted_line = indent_str * indent + stripped
        result.append(formatted_line)

        # Increase indent for block-start keywords
        if stripped.endswith(":"):
            indent += 1

    return "\n".join(result) + "\n"


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
