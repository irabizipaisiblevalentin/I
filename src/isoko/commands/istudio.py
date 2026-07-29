"""I STUDIO CLI bridge — registers isoko istudio subcommands."""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    try:
        from istudio.itegeko import register_subcommands, genda
        register_subcommands(subparsers)
    except ImportError:
        pass


def run(args: argparse.Namespace) -> int:
    from istudio.itegeko import genda
    return genda(args)
