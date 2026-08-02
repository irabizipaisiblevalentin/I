"""vm — Virtual machine utilities for the I language.

Provides access to the IVM runtime from the standard library.
"""

from __future__ import annotations

import sys
import os
from typing import Any, Optional


def version() -> str:
    """Return the IVM version."""
    return "1.0.0"


def create_vm(config: Optional[Any] = None) -> Any:
    """Create a new VM instance."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from vm import VMConfig, VMInstance
    return VMInstance(config or VMConfig())


def run_source(source: str, config: Optional[Any] = None) -> Any:
    """Compile and execute I source code."""
    vm = create_vm(config)
    return vm.run_source(source)


def run_bytecode(chunk: Any, config: Optional[Any] = None) -> Any:
    """Execute a bytecode chunk."""
    vm = create_vm(config)
    return vm.execute(chunk)


def format_report(vm: Any) -> str:
    """Get execution report from a VM instance."""
    return vm.format_report()
