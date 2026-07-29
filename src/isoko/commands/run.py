"""isoko run — Run an I program."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import List, Optional

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("run", help="Run an I program")
    p.add_argument("file", nargs="?", help="File to run")
    p.add_argument("--release", action="store_true",
                   help="Run in release mode")
    p.add_argument("--args", nargs="*", default=[],
                   help="Arguments to pass to the program")


def run(args) -> int:
    manifest_path = find_manifest()
    file_path = getattr(args, "file", None)
    extra_args = getattr(args, "args", []) or []

    if not file_path and manifest_path:
        m = load_manifest(manifest_path)
        file_path = m.scripts.get("run")
        if not file_path:
            lib = m.lib or "lib"
            default_entry = os.path.join(
                os.path.dirname(manifest_path), lib, f"{m.name}.i"
            )
            if os.path.exists(default_entry):
                file_path = default_entry

    if not file_path:
        output.error("no file specified and no default entry point found")
        return 1

    if not os.path.exists(file_path):
        output.error(f"file not found: {file_path}")
        return 1

    output.info(f"Running {os.path.basename(file_path)}")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "vm.virtual_machine", file_path] + extra_args,
            cwd=os.path.dirname(os.path.abspath(file_path)),
        )
        return result.returncode
    except FileNotFoundError:
        output.error("VM not available. Run 'isoko build' first.")
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        output.error(f"execution failed: {e}")
        return 1
