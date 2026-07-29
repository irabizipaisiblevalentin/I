"""Menya — Platform detection."""

from __future__ import annotations

import platform
import sys

from ibiro.urwego.shingiro import Inyuma


def menya_urwego() -> str:
    """Menya urwego rwa porogaramu (platform detection).

    Returns:
        str: windows, linux, darwin, cyangwa headless
    """
    sisitemu = platform.system().lower()
    if sisitemu == "windows":
        return "windows"
    elif sisitemu == "linux":
        return "linux"
    elif sisitemu == "darwin":
        return "darwin"
    return "headless"


def kora_inyuma() -> Inyuma:
    """Kora inyuma ikwiye kuri uru rwego.

    Returns:
        Inyuma: Inyuma ya porogaramu
    """
    urwego = menya_urwego()
    if urwego == "windows":
        from ibiro.urwego.windows import InyumaWindows
        return InyumaWindows()
    elif urwego == "linux":
        from ibiro.urwego.linux import InyumaLinux
        return InyumaLinux()
    elif urwego == "darwin":
        from ibiro.urwego.darwin import InyumaDarwin
        return InyumaDarwin()
    else:
        from ibiro.urwego.umutwe import InyumaUmutwe
        return InyumaUmutwe()
