"""isoko doc — Generate documentation for I project."""

from __future__ import annotations

import os
import re
import sys
from typing import Dict, List

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("doc", help="Generate documentation")
    p.add_argument("--output", "-o", default="docs",
                   help="Output directory (default: docs)")
    p.add_argument("--format", choices=["html", "markdown", "json"],
                   default="markdown", help="Output format")
    p.add_argument("--serve", action="store_true",
                   help="Serve documentation locally")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    out_dir = getattr(args, "output", "docs")
    fmt = getattr(args, "format", "markdown")
    serve = getattr(args, "serve", False)

    output.header(f"Generating documentation for {m.full_name}")

    lib_dir = os.path.join(project_dir, m.lib or "lib")
    i_files = _find_i_files(lib_dir) if os.path.exists(lib_dir) else []

    output.info(f"Found {len(i_files)} source file(s)")

    docs = _extract_docs(i_files, m)

    if serve:
        output.info("Documentation server not yet implemented")
        return 0

    out_path = os.path.join(project_dir, out_dir)
    os.makedirs(out_path, exist_ok=True)

    if fmt == "markdown":
        _write_markdown(docs, out_path, m)
    elif fmt == "json":
        import json
        path = os.path.join(out_path, "api.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2)
        output.info(f"Written to {path}")
    elif fmt == "html":
        _write_markdown(docs, out_path, m)
        output.info("HTML generation not yet implemented, wrote Markdown")

    output.success(f"Documentation generated in {out_dir}/")
    return 0


def _extract_docs(files: List[str], manifest) -> Dict:
    docs = {
        "project": manifest.name,
        "version": manifest.version,
        "description": manifest.description,
        "modules": [],
    }

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")

        module_doc = {
            "file": os.path.basename(path),
            "description": "",
            "functions": [],
        }

        # Extract top-level comments as module doc
        comment_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                comment_lines.append(stripped.lstrip("# ").strip())
            elif stripped and not stripped.startswith("#"):
                break
        module_doc["description"] = "\n".join(comment_lines)

        # Extract function-like patterns
        func_pattern = re.compile(r"umurimo\s+(\w+)\s*\(")
        for i, line in enumerate(lines):
            m = func_pattern.search(line)
            if m:
                module_doc["functions"].append({
                    "name": m.group(1),
                    "line": i + 1,
                })

        docs["modules"].append(module_doc)

    return docs


def _write_markdown(docs: Dict, out_dir: str, manifest) -> None:
    lines = [
        f"# {docs['project']}",
        f"",
        f"Version: {docs['version']}",
        f"",
        f"{docs['description']}",
        f"",
        f"## Modules",
        f"",
    ]

    for mod in docs["modules"]:
        lines.append(f"### {mod['file']}")
        lines.append(f"")
        if mod["description"]:
            lines.append(mod["description"])
            lines.append(f"")
        if mod["functions"]:
            lines.append(f"**Functions:**")
            lines.append(f"")
            for fn in mod["functions"]:
                lines.append(f"- `{fn['name']}` (line {fn['line']})")
            lines.append(f"")

    path = os.path.join(out_dir, "API.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    output.info(f"Written to {path}")


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
