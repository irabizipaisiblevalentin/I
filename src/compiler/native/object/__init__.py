"""
Object file generation for native compilation targets.
"""

from __future__ import annotations

from compiler.native.object.elf import ELFWriter
from compiler.native.object.macho import MachOWriter
from compiler.native.object.pe import PEWriter

__all__ = [
    "ELFWriter",
    "PEWriter",
    "MachOWriter",
]
