"""SISITEMU CLI bridge — registers isoko sisitemu subcommands."""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    try:
        from sisitemu.itegeko_sisitemu import register_subcommands, genda
        register_subcommands(subparsers)
    except ImportError:
        pass


def run(args: argparse.Namespace) -> int:
    from sisitemu.itegeko_sisitemu import genda
    return genda(args)
