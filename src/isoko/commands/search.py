"""isoko search — Search for packages in the registry."""

from __future__ import annotations

from isoko import output
from isoko.registry import RegistryClient, RegistryConfig


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("search", help="Search for packages")
    p.add_argument("query", help="Search query")
    p.add_argument("--limit", "-n", type=int, default=20,
                   help="Maximum results")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")


def run(args) -> int:
    query = args.query
    limit = getattr(args, "limit", 20)
    json_mode = getattr(args, "json", False)

    output.header(f"Searching for '{query}'")

    config = RegistryConfig()
    registry = RegistryClient(config)

    try:
        results = registry.search(query, limit)
    except Exception as e:
        output.error(f"search failed: {e}")
        return 1

    if not results:
        output.info("No packages found")
        return 0

    if json_mode:
        output.print_json(results)
        return 0

    output.info(f"Found {len(results)} package(s)\n")
    for pkg in results:
        name = pkg.get("name", "unknown")
        version = pkg.get("latest_version", "?")
        desc = pkg.get("description", "")
        output.label_value(name, f"v{version} — {desc}")

    return 0
