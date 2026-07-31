"""uam — Unified Application Model for the I Programming Language.

The UAM enables writing a single application codebase that deploys
to web (urubuga), desktop (ibiro), and mobile (mobile) platforms.
"""

from __future__ import annotations

import enum
import os
import sys
from typing import Any, Dict, Optional

__version__ = "1.0.0"


class PlatformTarget(enum.Enum):
    """Target platform for a UAM application."""

    URUBUGA = "web"
    IBIRO = "desktop"
    MOBILE = "mobile"


def detect_platform() -> PlatformTarget:
    """Auto-detect the current platform from the execution environment.

    Returns:
        The detected PlatformTarget.
    """
    if "I_PLATFORM" in os.environ:
        value = os.environ["I_PLATFORM"].lower()
        if value in ("web", "urubuga"):
            return PlatformTarget.URUBUGA
        if value in ("desktop", "ibiro"):
            return PlatformTarget.IBIRO
        if value in ("mobile",):
            return PlatformTarget.MOBILE

    try:
        import platform as _platform
        system = _platform.system()
        if system in ("Linux", "Darwin", "Windows"):
            return PlatformTarget.IBIRO
    except ImportError:
        pass

    try:
        import sysconfig
        if sysconfig.get_platform().startswith("ios") or "android" in sysconfig.get_platform():
            return PlatformTarget.MOBILE
    except ImportError:
        pass

    return PlatformTarget.URUBUGA


from uam.porogaramu.porogaramu import UAMApplication

from uam.inyandikorwande.inyandikorwande import ComponentRegistry, ComponentDefinition

from uam.kubaka.kubaka import UAMBuildSystem, BuildConfig, PlatformManifest

__all__ = [
    "UAMApplication",
    "PlatformTarget",
    "ComponentRegistry",
    "ComponentDefinition",
    "UAMBuildSystem",
    "BuildConfig",
    "PlatformManifest",
    "detect_platform",
]


class _ImportLoader:
    """Registers .i extension support for importing I language modules."""

    @staticmethod
    def load_module(fullname: str, path: Optional[str] = None) -> Optional[Any]:
        return None


def _register_i_extension() -> None:
    """Register .i extension for import support."""
    if hasattr(sys, "meta_path"):
        loader = _ImportLoader()

        class _IFinder:
            def find_spec(self, fullname: str, path: Optional[list] = None,
                          target: Optional[Any] = None) -> Optional[Any]:
                return None

        sys.meta_path.insert(0, _IFinder())


_register_i_extension()
