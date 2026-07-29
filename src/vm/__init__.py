"""I Virtual Machine (IVM) — Production-quality bytecode VM for the I Programming Language.

The IVM is the official execution engine and reference runtime.
"""
from __future__ import annotations

from vm.vm_config import VMConfig
from vm.vm_context import VMContext
from vm.vm_instance import VMInstance

__all__ = ["VMConfig", "VMContext", "VMInstance"]
