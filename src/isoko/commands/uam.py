"""uam command module for the isoko CLI.

Delegates to the UAM platform CLI module.
"""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    """Register the uam command parser."""
    from uam.cli import kongera_iyobokamana
    kongera_iyobokamana(subparsers)


def run(args: argparse.Namespace) -> int:
    """Execute the uam command."""
    from uam.cli import genda as uam_genda
    return uam_genda(args)
