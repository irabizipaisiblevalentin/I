"""UBWENGE CLI bridge — registers isoko ubwenge subcommands."""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    try:
        from ubwenge.itegeko import register_subcommands, genda
        register_subcommands(subparsers)
    except ImportError:
        pass


def run(args: argparse.Namespace) -> int:
    from ubwenge.itegeko import genda
    return genda(args)
