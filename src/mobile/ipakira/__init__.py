"""ipakira — Packaging / Build modules for the I mobile platform.

Provides build configuration, signing, minification, and
store-ready package generation for Android and iOS.
"""

from __future__ import annotations

from mobile.ipakira.ipakira import (
    BuildConfig,
    BuildMode,
    Ipakira,
    PackageFormat,
)

__all__ = [
    "BuildConfig",
    "BuildMode",
    "Ipakira",
    "PackageFormat",
]
