#!/usr/bin/env python3
"""isoko — I Language Package Manager & Ecosystem CLI.

isoko is the official command-line interface for the entire I ecosystem.
It manages packages, workspaces, dependencies, registries, and the
complete developer workflow for the I programming language.
"""

from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path

from isoko import __version__, output
from isoko.commands import (
    new, init, build, run, test, bench,
    check, fmt, lint, doc, publish,
    install, uninstall, update, upgrade,
    search, info, login, logout, cache,
    doctor, clean, verify, audit, vendor,
    graph, tree, workspace, self_update,
)
from isoko.commands import urubugs
from isoko.commands import ibiro as ibiro_commands
from isoko.commands import mobile as mobile_commands
from isoko.commands import uam as uam_commands
from isoko.commands import ububiko as ububiko_commands
from isoko.commands import ubwenge as ubwenge_commands
from isoko.commands import imikino as imikino_commands
from isoko.commands import igicu as igicu_commands
from isoko.commands import istudio as istudio_commands
from isoko.commands import ideveloper as ideveloper_commands

COMMANDS = {
    "new": new,
    "init": init,
    "build": build,
    "run": run,
    "test": test,
    "bench": bench,
    "check": check,
    "fmt": fmt,
    "lint": lint,
    "doc": doc,
    "publish": publish,
    "install": install,
    "uninstall": uninstall,
    "update": update,
    "upgrade": upgrade,
    "search": search,
    "info": info,
    "login": login,
    "logout": logout,
    "cache": cache,
    "doctor": doctor,
    "clean": clean,
    "verify": verify,
    "audit": audit,
    "vendor": vendor,
    "graph": graph,
    "tree": tree,
    "workspace": workspace,
    "self-update": self_update,
    "urubuga": urubugs,
    "ibiro": ibiro_commands,
    "mobile": mobile_commands,
    "uam": uam_commands,
    "ububiko": ububiko_commands,
    "ubwenge": ubwenge_commands,
    "imikino": imikino_commands,
    "igicu": igicu_commands,
    "istudio": istudio_commands,
    "idev": ideveloper_commands,
}


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="isoko",
        description="I Language Package Manager & Ecosystem CLI",
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Commands:\n"
            "  isoko new <name>        Create a new project\n"
            "  isoko init              Initialize project in current directory\n"
            "  isoko install           Install dependencies\n"
            "  isoko build             Build the project\n"
            "  isoko run [file]        Run an I program\n"
            "  isoko test              Run tests\n"
            "  isoko search <query>    Search for packages\n"
            "  isoko publish           Publish a package\n"
            "  isoko doctor            Diagnose issues\n"
            "  isoko urubuga           Web framework commands\n"
            "  isoko mobile              Mobile framework commands\n"
            "  isoko uam                 Unified Application Model commands\n"
            "  isoko ububiko             Data platform commands\n"
            "  isoko ubwenge             AI platform commands\n"
            "  isoko imikino             Game engine commands\n"
            "  isoko igicu               Cloud platform commands\n"
            "  isoko istudio             I STUDIO IDE platform commands\n"
            "  isoko idev                I Developer Platform commands\n"
            "\n"
            "Run 'isoko <command> --help' for more information on a command.\n"
        ),
    )

    parser.add_argument(
        "--version", "-V", action="version",
        version=f"isoko {__version__}",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress non-error output",
    )
    parser.add_argument(
        "--color", choices=["auto", "always", "never"], default="auto",
        help="Color output mode (default: auto)",
    )
    parser.add_argument(
        "--json", "-j", action="store_true",
        dest="json_output",
        help="Output in JSON format",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND",
    )

    for name, module in COMMANDS.items():
        if hasattr(module, "add_subparser"):
            module.add_subparser(subparsers)

    return parser


def main(argv=None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    # Configure color
    color_mode = getattr(args, "color", "auto")
    if color_mode == "always":
        output.set_color(True)
    elif color_mode == "never":
        output.set_color(False)

    if not args.command:
        parser.print_help()
        return 0

    module = COMMANDS.get(args.command)
    if module is None:
        output.error(f"unknown command: {args.command}")
        output.dim(f"  Run 'isoko --help' for available commands")

        # Suggest similar commands
        import difflib
        matches = difflib.get_close_matches(args.command, COMMANDS.keys(), n=3, cutoff=0.4)
        if matches:
            output.dim(f"  Did you mean: {', '.join(matches)}?")
        return 1

    if not hasattr(module, "run"):
        output.error(f"command '{args.command}' is not implemented yet")
        return 1

    try:
        return module.run(args)
    except KeyboardInterrupt:
        output.error("\nInterrupted")
        return 130
    except Exception as e:
        output.error(f"{args.command}: {e}")
        if getattr(args, "verbose", False):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
