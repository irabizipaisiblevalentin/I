"""mobile command module for the isoko CLI.

Delegates to the MOBILE platform CLI module (Kinyarwanda API).
"""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> None:
    """Register the mobile command parser."""
    from mobile.itegeko.amategeko import kongera_iyobokamana
    kongera_iyobokamana(subparsers)


def run(args: argparse.Namespace) -> int:
    """Execute the mobile command."""
    from mobile.itegeko.amategeko import genda as mobile_genda
    return mobile_genda(args)
