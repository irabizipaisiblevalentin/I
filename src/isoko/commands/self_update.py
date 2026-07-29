"""isoko self-update — Update isoko itself."""

from __future__ import annotations

import os
import sys

from isoko import output
from isoko import __version__


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("self-update", help="Update isoko")


def run(args) -> int:
    output.header("isoko self-update")
    output.info(f"Current version: {__version__}")

    output.dim("  Self-update is not yet available via registry.")
    output.dim("  Update isoko by pulling the latest source:")
    output.dim("    git pull")
    output.dim("    pip install -e .")

    output.success("isoko is up to date")
    return 0
