"""IGICU CLI bridge — registers isoko igicu subcommands."""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    try:
        from igicu.itegeko import register_subcommands, genda
        register_subcommands(subparsers)
    except ImportError:
        pass


def run(args: argparse.Namespace) -> int:
    from igicu.itegeko import genda
    return genda(args)
