"""isoko info — Show package information."""

from __future__ import annotations

from isoko import output
from isoko.registry import RegistryClient, RegistryConfig


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("info", help="Show package info")
    p.add_argument("package", help="Package name")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    package = args.package
    json_mode = getattr(args, "json", False)

    output.header(f"Package: {package}")

    config = RegistryConfig()
    registry = RegistryClient(config)

    try:
        meta = registry.get_package(package, "latest")
    except Exception:
        meta = None

    if not meta:
        output.error(f"package not found: {package}")
        return 1

    if json_mode:
        output.print_json(meta)
        return 0

    output.label_value("Name", meta.get("name", package))
    output.label_value("Version", meta.get("version", "unknown"))
    output.label_value("Description", meta.get("description", ""))
    if meta.get("license"):
        output.label_value("License", meta["license"])
    if meta.get("author"):
        output.label_value("Author", meta["author"])
    if meta.get("repository"):
        output.label_value("Repository", meta["repository"])

    deps = meta.get("dependencies", {})
    if deps:
        output.header("Dependencies")
        for name, spec in deps.items():
            output.info(f"  {name} {spec}")

    return 0
