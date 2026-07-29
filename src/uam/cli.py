"""cli — UAM command-line interface for isoko integration.

Provides subcommands for project creation, building, running,
component management, diagnostics, and analysis.

Usage:
    isoko uam new <name>
    isoko uam build --target web|desktop|mobile|all
    isoko uam run --target web|desktop|mobile
    isoko uam add <path>
    isoko uam override <name> --platform web|desktop|mobile
    isoko uam doctor
    isoko uam analyze
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from typing import Any, Dict, List, Optional

from uam import PlatformTarget, detect_platform
from uam.porogaramu.porogaramu import UAMApplication
from uam.inyandikorwande.inyandikorwande import ComponentRegistry
from uam.kubaka.kubaka import UAMBuildSystem, BuildConfig
from uam.kubaka.itunganya import ProjectAnalyzer


def add_subparser(subparsers: Any) -> None:
    """Register UAM CLI commands with an argparse subparser group.

    Args:
        subparsers: Subparser object from argparse.
    """
    parser = subparsers.add_parser("uam", help="Unified Application Model commands")
    uam_sub = parser.add_subparsers(dest="uam_command", required=True)

    # isoko uam new
    new_parser = uam_sub.add_parser("new", help="Create a new UAM project")
    new_parser.add_argument("name", type=str, help="Project name")
    new_parser.add_argument("--output", "-o", type=str, default=".",
                            help="Output directory")

    # isoko uam build
    build_parser = uam_sub.add_parser("build", help="Build for platform")
    build_parser.add_argument("--target", "-t", type=str, default="web",
                              choices=["web", "desktop", "mobile", "all"],
                              help="Target platform")
    build_parser.add_argument("--output", "-o", type=str, default="dist",
                              help="Output directory")

    # isoko uam run
    run_parser = uam_sub.add_parser("run", help="Run on platform")
    run_parser.add_argument("--target", "-t", type=str, default="",
                            choices=["web", "desktop", "mobile", ""],
                            help="Target platform")

    # isoko uam add
    add_parser = uam_sub.add_parser("add", help="Add component to ui/")
    add_parser.add_argument("path", type=str, help="Component name or path")

    # isoko uam override
    override_parser = uam_sub.add_parser("override",
                                         help="Create platform override")
    override_parser.add_argument("name", type=str, help="Component name")
    override_parser.add_argument("--platform", "-p", type=str, required=True,
                                 choices=["web", "desktop", "mobile"],
                                 help="Target platform")

    # isoko uam doctor
    uam_sub.add_parser("doctor", help="Diagnose project structure")

    # isoko uam analyze
    uam_sub.add_parser("analyze", help="Analyze cross-platform coverage")


def run(args: argparse.Namespace) -> Dict[str, Any]:
    """Dispatch to the appropriate UAM command handler.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Result dictionary.

    Raises:
        ValueError: If the command is unknown.
    """
    command = getattr(args, "uam_command", "")
    if command == "new":
        return _cmd_new(args.name, args.output)
    elif command == "build":
        return _cmd_build(args.target, args.output)
    elif command == "run":
        return _cmd_run(args.target)
    elif command == "add":
        return _cmd_add(args.path)
    elif command == "override":
        platform = PlatformTarget(args.platform)
        return _cmd_override(args.name, platform)
    elif command == "doctor":
        return _cmd_doctor()
    elif command == "analyze":
        return _cmd_analyze()
    else:
        raise ValueError(f"Unknown UAM command: {command}")


def _cmd_new(name: str, output: str = ".") -> Dict[str, Any]:
    """Create a new UAM project with full directory structure.

    Args:
        name: Project name.
        output: Parent output directory.

    Returns:
        Result dictionary with project path and created files.
    """
    project_dir = os.path.abspath(os.path.join(output, name))
    created: List[str] = []

    directories = [
        "shared/logic",
        "shared/models",
        "shared/validation",
        "shared/services",
        "shared/networking",
        "shared/database",
        "shared/state",
        "ui/components",
        "ui/screens",
        "ui/layouts",
        "ui/navigation",
        "ui/theme",
        "web/components",
        "web/layouts",
        "web/public",
        "desktop/components",
        "desktop/menus",
        "desktop/windows",
        "mobile/components",
        "mobile/screens",
    ]

    for d in directories:
        full_path = os.path.join(project_dir, d)
        os.makedirs(full_path, exist_ok=True)
        created.append(full_path)

    config = {
        "name": name,
        "version": "0.1.0",
        "author": "",
        "shared_dirs": ["shared", "ui"],
        "platforms": ["web", "desktop", "mobile"],
        "output": "dist",
    }

    config_path = os.path.join(project_dir, "uam.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(_yaml_dumps(config))
    created.append(config_path)

    ilang_config = {
        "name": name,
        "version": "0.1.0",
        "type": "application",
    }
    ilang_path = os.path.join(project_dir, "ilang.json")
    with open(ilang_path, "w", encoding="utf-8") as f:
        json.dump(ilang_config, f, indent=2)
    created.append(ilang_path)

    entry_files = {
        "web/main.i": f'// {name} — web entry point\nimport uam\n\nuam.run()\n',
        "desktop/main.i": f'// {name} — desktop entry point\nimport uam\n\nuam.run()\n',
        "mobile/main.i": f'// {name} — mobile entry point\nimport uam\n\nuam.run()\n',
    }
    for rel_path, content in entry_files.items():
        full_path = os.path.join(project_dir, rel_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        created.append(full_path)

    return {
        "success": True,
        "project": name,
        "directory": project_dir,
        "created": created,
    }


def _cmd_build(target: str, output: str) -> Dict[str, Any]:
    """Build the UAM project for the specified target.

    Args:
        target: Platform target string ("web", "desktop", "mobile", "all").
        output: Output directory.

    Returns:
        Build result dictionary.
    """
    platforms = [PlatformTarget(t) for t in
                 (["web", "desktop", "mobile"] if target == "all" else [target])]
    results: Dict[str, Any] = {}

    for pt in platforms:
        builder = UAMBuildSystem(pt)
        config_path = os.path.join(".", "uam.yaml")
        if os.path.isfile(config_path):
            builder.load_config(config_path)
        builder.output_dir = output

        if pt == PlatformTarget.URUBUGA:
            result = builder.build_web(output)
        elif pt == PlatformTarget.IBIRO:
            result = builder.build_desktop(output)
        elif pt == PlatformTarget.MOBILE:
            result = builder.build_mobile(output)

        results[pt.value] = result

    return {
        "success": True,
        "target": target,
        "results": results,
    }


def _cmd_run(target: str) -> Dict[str, Any]:
    """Run the UAM application.

    Args:
        target: Platform target string.

    Returns:
        Result dictionary.
    """
    pt = PlatformTarget(target) if target else detect_platform()

    config: BuildConfig = BuildConfig()
    config_path = "uam.yaml"
    if os.path.isfile(config_path):
        import yaml as _yaml
        with open(config_path, "r") as f:
            data = _yaml.safe_load(f) or {}
        config.name = data.get("name", "uam-app")
        config.version = data.get("version", "0.1.0")

    app = UAMApplication(config.name, config.version, pt)
    app.run()

    return {
        "success": True,
        "target": pt.value,
        "name": config.name,
    }


def _cmd_add(path: str) -> Dict[str, Any]:
    """Add a new component to the ui/components/ directory.

    Args:
        path: Component name or path.

    Returns:
        Result dictionary.
    """
    name = os.path.basename(path).rsplit(".", 1)[0]
    ui_dir = os.path.join(".", "ui", "components")
    os.makedirs(ui_dir, exist_ok=True)

    dest_path = os.path.join(ui_dir, f"{name}.i")
    if os.path.isfile(dest_path):
        return {"success": False, "error": f"Component '{name}' already exists"}

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(f'// {name} component\n\n')

    return {
        "success": True,
        "component": name,
        "path": dest_path,
    }


def _cmd_override(name: str, platform: PlatformTarget) -> Dict[str, Any]:
    """Create a platform-specific override for a component.

    Args:
        name: Component name.
        platform: Target platform.

    Returns:
        Result dictionary.
    """
    platform_dir_map = {
        PlatformTarget.URUBUGA: "web",
        PlatformTarget.IBIRO: "desktop",
        PlatformTarget.MOBILE: "mobile",
    }
    dir_name = platform_dir_map[platform]
    override_dir = os.path.join(".", dir_name, "components")
    os.makedirs(override_dir, exist_ok=True)

    dest_path = os.path.join(override_dir, f"{name}.i")
    if os.path.isfile(dest_path):
        return {
            "success": False,
            "error": f"Override '{name}' for {platform.value} already exists",
        }

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(f'// {name} — {platform.value} override\n\n')

    return {
        "success": True,
        "component": name,
        "platform": platform.value,
        "path": dest_path,
    }


def _cmd_doctor() -> Dict[str, Any]:
    """Diagnose the UAM project structure.

    Returns:
        Diagnostic result dictionary.
    """
    builder = UAMBuildSystem()
    validation = builder.validate()

    checks = validation.get("checks", {})
    issues = validation.get("issues", [])

    registry = ComponentRegistry()
    has_components = os.path.isdir("ui/components")

    return {
        "success": True,
        "healthy": validation.get("valid", False) and not issues,
        "project": os.path.basename(os.getcwd()),
        "checks": checks,
        "issues": issues,
        "has_components": has_components,
    }


def _cmd_analyze() -> Dict[str, Any]:
    """Analyze cross-platform coverage.

    Returns:
        Analysis result dictionary.
    """
    analyzer = ProjectAnalyzer()
    stats = analyzer.analyze_project()
    shared_pct = analyzer.calculate_shared_percentage()
    unresolved = analyzer.find_unresolved_components()
    orphans = analyzer.find_orphan_overrides()
    report = analyzer.generate_report()

    return {
        "success": True,
        "report": report,
        "stats": stats,
        "shared_percentage": shared_pct,
        "unresolved_components": unresolved,
        "orphan_overrides": orphans,
    }


def _yaml_dumps(data: Dict[str, Any]) -> str:
    """Serialize a dictionary to YAML format without pyyaml dependency.

    Args:
        data: Dictionary to serialize.

    Returns:
        YAML string.
    """
    lines: List[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines) + "\n"
