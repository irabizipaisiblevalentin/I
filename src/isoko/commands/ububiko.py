"""ububiko command module for the isoko CLI.

Delegates to the UBUBIKO data platform CLI module.
"""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    """Register the ububiko command parser."""
    from ububiko.itegeko import kongera_iyobokamana
    kongera_iyobokamana(subparsers)


def run(args: argparse.Namespace) -> int:
    """Execute the ububiko command."""
    from ububiko.itegeko import genda as ububiko_genda
    return ububiko_genda(args)
