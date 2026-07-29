"""Inyuma Windows — Windows platform backend.

Ikoresha Muyoboro (HTTP server + browser) kugirango
yerekane idirishya ry'ukuri.
"""

from __future__ import annotations

import sys
import subprocess
import ctypes
from typing import Tuple, Optional

from ibiro.urwego.shingiro import Inyuma
from ibiro.urwego.itara import Itara
from ibiro.urwego.muyoboro import Muyoboro


class InyumaWindows(Inyuma):
    """Inyuma Windows — Windows backend using ctypes + web renderer.

    Ikoresha Muyoboro kugirango yerekane porogaramu
    mu mushakisha wa web.
    """

    _itara: Optional[Itara]
    _muyoboro: Optional[Muyoboro]

    def __init__(ibi: "InyumaWindows"):
        ibi._itara = None
        ibi._muyoboro = None

    def inyuma_urwego(ibi) -> str:
        return "Windows"

    def ingano_ikiganiro(ibi) -> Tuple[int, int]:
        try:
            user32 = ctypes.windll.user32
            return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        except Exception:
            return (1920, 1080)

    def shaka_muri_duporo(ibi) -> Optional[str]:
        try:
            igisubizo = subprocess.run(
                ["powershell", "-command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=5
            )
            inyandiko = igisubizo.stdout.strip()
            return inyandiko if inyandiko else None
        except Exception:
            return None

    def shira_muri_duporo(ibi, inyandiko: str) -> bool:
        try:
            subprocess.run(
                ["powershell", "-command", f"Set-Clipboard -Value '{inyandiko}'"],
                capture_output=True, timeout=5
            )
            return True
        except Exception:
            return False

    def menyesha(ibi, umutwe: str, inyandiko: str) -> bool:
        try:
            subprocess.run(
                ["powershell", "-command",
                 f"New-BurntToastNotification -Text '{umutwe}', '{inyandiko}'"],
                capture_output=True, timeout=5
            )
            return True
        except Exception:
            return False

    def wiga_urwego(ibi) -> str:
        return sys.platform

    def tangiza(ibi, **igenamiterere) -> bool:
        """Tangiza inyuma — start the HTTP server and open browser."""
        ikoresho = igenamiterere.get("ikoresho")
        if ikoresho is None:
            return False
        ibi._itara = Itara()
        ibi._muyoboro = Muyoboro(ibi._itara, ikoresho)
        return ibi._muyoboro.tangiza()

    def rirarika(ibi) -> int:
        """Rirarika mainloop."""
        if ibi._muyoboro:
            return ibi._muyoboro.rirarika()
        return 0

    def hagarika(ibi) -> None:
        """Hagarika seriveri."""
        if ibi._muyoboro:
            ibi._muyoboro.hagarika()
