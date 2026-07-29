"""isoko new — Create a new I project from a template."""

from __future__ import annotations

import os
import sys
from typing import List, Optional

from isoko import output
from isoko.templates import list_templates, render_template


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("new", help="Create a new I project")
    p.add_argument("name", help="Project name")
    p.add_argument("-t", "--template", default="console",
                   help="Template to use (default: console)")
    p.add_argument("-o", "--output", default=".",
                   help="Output directory (default: current)")
    p.add_argument("--list-templates", action="store_true",
                   help="List available templates")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    if getattr(args, "list_templates", False):
        templates = list_templates()
        if getattr(args, "json", False):
            output.print_json(templates)
        else:
            output.header("Available Templates")
            for t in templates:
                output.label_value(t["name"], t["description"])
        return 0

    name = args.name
    template_name = getattr(args, "template", "console")
    out_dir = getattr(args, "output", ".")

    project_dir = os.path.join(out_dir, name)
    if os.path.exists(project_dir):
        output.error(f"directory already exists: {project_dir}")
        return 1

    try:
        files = render_template(template_name, name, project_dir)
    except ValueError as e:
        output.error(str(e))
        return 1
    except Exception as e:
        output.error(f"failed to create project: {e}")
        return 1

    output.success(f"Created project '{name}' using template '{template_name}'")
    output.dim(f"  Location: {os.path.abspath(project_dir)}")
    output.dim(f"  Files created: {len(files)}")
    for f in files:
        rel = os.path.relpath(f, project_dir)
        output.info(rel)

    output.dim(f"\n  Next steps:")
    output.dim(f"    cd {name}")
    output.dim(f"    isoko build")
    return 0
