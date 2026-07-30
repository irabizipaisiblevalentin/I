"""
Platform detection for native compilation targets.
"""

from __future__ import annotations

import platform
from enum import Enum

from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind


class Platform(Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"


def detect_platform() -> Platform:
    system = platform.system().lower()
    if system == "linux":
        return Platform.LINUX
    if system == "darwin":
        return Platform.MACOS
    if system == "windows":
        return Platform.WINDOWS
    raise RuntimeError(f"Unsupported platform: {system}")


def detect_architecture() -> str:
    machine = platform.machine().lower()
    arch_map: dict[str, str] = {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "x64": "x86_64",
        "i386": "x86_32",
        "i686": "x86_32",
        "x86": "x86_32",
        "arm64": "arm64",
        "aarch64": "arm64",
        "armv8l": "arm64",
        "armv8b": "arm64",
        "arm": "arm32",
        "armv7l": "arm32",
        "riscv64": "riscv64",
        "riscv32": "riscv32",
    }
    return arch_map.get(machine, machine)


def detect_target() -> TargetDescription:
    arch = detect_architecture()
    detect_platform()

    kind_map: dict[str, TargetKind] = {
        "x86_64": TargetKind.X86_64,
        "x86_32": TargetKind.X86_32,
        "arm64": TargetKind.ARM64,
        "arm32": TargetKind.ARM32,
        "riscv64": TargetKind.RISCV64,
        "riscv32": TargetKind.RISCV32,
        "wasm32": TargetKind.WASM32,
        "wasm64": TargetKind.WASM64,
    }

    kind = kind_map.get(arch, TargetKind.X86_64)
    bits = 64 if "64" in arch else 32
    triple = host_triple()

    return TargetDescription(kind=kind, bits=bits, triple=triple)


def is_windows() -> bool:
    return detect_platform() == Platform.WINDOWS


def is_linux() -> bool:
    return detect_platform() == Platform.LINUX


def is_macos() -> bool:
    return detect_platform() == Platform.MACOS


def host_triple() -> str:
    arch = platform.machine().lower()
    system = platform.system().lower()

    if arch in ("amd64", "x86_64", "x64"):
        arch_str = "x86_64"
    elif arch in ("i386", "i686"):
        arch_str = "i686"
    elif arch in ("arm64", "aarch64"):
        arch_str = "aarch64"
    elif arch in ("arm", "armv7l"):
        arch_str = "armv7"
    elif arch == "riscv64":
        arch_str = "riscv64"
    else:
        arch_str = arch

    os_map: dict[str, str] = {
        "linux": "unknown-linux-gnu",
        "darwin": "apple-darwin",
        "windows": "pc-windows-msvc",
    }

    os_str = os_map.get(system, "unknown-unknown")
    return f"{arch_str}-{os_str}"
