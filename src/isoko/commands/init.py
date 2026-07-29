"""isoko init — Initialize a new I project in the current directory."""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

from isoko import output
from isoko.manifest import Manifest, save


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("init", help="Initialize a new I project")
    p.add_argument("--name", help="Package name (default: directory name)")
    p.add_argument("--template", default="console",
                   help="Template to use")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    cwd = os.getcwd()
    name = getattr(args, "name", None) or os.path.basename(cwd)

    existing = os.path.join(cwd, "ilang.toml")
    if os.path.exists(existing):
        output.error("ilang.toml already exists in this directory")
        return 1

    m = Manifest()
    m.name = name
    m.version = "0.1.0"
    m.description = f"{name} — an I project"
    m.license = "MIT"

    toml_path = os.path.join(cwd, "ilang.toml")
    _write_toml(m, toml_path)

    # Create directory structure
    lib_dir = os.path.join(cwd, "lib")
    os.makedirs(lib_dir, exist_ok=True)

    entry = os.path.join(lib_dir, f"{name}.i")
    if not os.path.exists(entry):
        with open(entry, "w", encoding="utf-8") as f:
            f.write(f"# {name} — Entry point\nandika(\"Hello, World!\")\n")

    tests_dir = os.path.join(cwd, "tests")
    os.makedirs(tests_dir, exist_ok=True)

    output.success(f"Initialized project '{name}'")
    output.dim(f"  Created ilang.toml")
    output.dim(f"  Created lib/{name}.i")
    output.dim(f"  Created tests/")
    return 0


def _write_toml(m: Manifest, path: str) -> None:
    lines = []
    lines.append("[package]")
    lines.append(f'name = "{m.name}"')
    lines.append(f'version = "{m.version}"')
    lines.append(f'description = "{m.description}"')
    lines.append(f'license = "{m.license}"')
    if m.authors:
        lines.append("authors = [")
        for a in m.authors:
            if isinstance(a, dict):
                lines.append(f'  {{name = "{a.get("name","")}", email = "{a.get("email","")}"}}')
            else:
                lines.append(f'  "{a}"')
        lines.append("]")
    if m.keywords:
        kw = ", ".join(f'"{k}"' for k in m.keywords)
        lines.append(f"keywords = [{kw}]")
    if m.engines:
        lines.append("[engines]")
        for k, v in m.engines.items():
            lines.append(f'{k} = "{v}"')

    if m.dependencies:
        lines.append("\n[dependencies]")
        for k, v in m.dependencies.items():
            lines.append(f'{k} = "{v}"')
    if m.dev_dependencies:
        lines.append("\n[dev-dependencies]")
        for k, v in m.dev_dependencies.items():
            lines.append(f'{k} = "{v}"')

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
