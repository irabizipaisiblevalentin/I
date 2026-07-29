"""I Developer Platform CLI bridge — registers isoko idev subcommands."""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    try:
        from isoko.ideveloper.itegeko import register_subcommands, genda
        register_subcommands(subparsers)
    except ImportError:
        pass


def run(args: argparse.Namespace) -> int:
    from isoko.ideveloper.itegeko import genda
    return genda(args)
