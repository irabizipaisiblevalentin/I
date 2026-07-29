"""ibiro command module for the isoko CLI.

Delegates to the IBIRO desktop platform CLI module (Kinyarwanda API).
"""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    """Register the ibiro command parser."""
    from ibiro.itegeko.amategeko import kongera_iyobokamana
    kongera_iyobokamana(subparsers)


def run(args: argparse.Namespace) -> int:
    """Execute the ibiro command."""
    from ibiro.itegeko.amategeko import genda as ibiro_genda
    return ibiro_genda(args)
