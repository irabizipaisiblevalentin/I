"""Inyuma Darwin — macOS platform backend."""

from __future__ import annotations

import sys
import subprocess
from typing import Tuple, Optional

from typing import Optional

from ibiro.urwego.shingiro import Inyuma
from ibiro.urwego.itara import Itara
from ibiro.urwego.muyoboro import Muyoboro


class InyumaDarwin(Inyuma):
    """Inyuma Darwin — macOS backend using pbpaste/pbcopy + web renderer."""

    def inyuma_urwego(ibi) -> str:
        return "macOS"

    def ingano_ikiganiro(ibi) -> Tuple[int, int]:
        try:
            igisubizo = subprocess.run(
                ["osascript", "-e", "tell application \"Finder\" to get bounds of window of desktop"],
                capture_output=True, text=True,
            )
            ibice = igisubizo.stdout.strip().split(", ")
            if len(ibice) >= 4:
                return (int(ibice[2]), int(ibice[3]))
            return (1440, 900)
        except Exception:
            return (1440, 900)

    def shaka_muri_duporo(ibi) -> Optional[str]:
        try:
            igisubizo = subprocess.run(["pbpaste"], capture_output=True, text=True)
            return igisubizo.stdout if igisubizo.returncode == 0 else None
        except Exception:
            return None

    def shira_muri_duporo(ibi, inyandiko: str) -> bool:
        try:
            subprocess.run(["pbcopy"], input=inyandiko, text=True)
            return True
        except Exception:
            return False

    def menyesha(ibi, umutwe: str, inyandiko: str) -> bool:
        try:
            igisubizo = subprocess.run(
                ["osascript", "-e", f'display notification "{inyandiko}" with title "{umutwe}"'],
                capture_output=True,
            )
            return igisubizo.returncode == 0
        except Exception:
            return False

    def wiga_urwego(ibi) -> str:
        return sys.platform

    _itara: Optional[Itara]
    _muyoboro: Optional[Muyoboro]

    def __init__(ibi: "InyumaDarwin"):
        ibi._itara = None
        ibi._muyoboro = None

    def tangiza(ibi, **igenamiterere) -> bool:
        ikoresho = igenamiterere.get("ikoresho")
        if ikoresho is None:
            return False
        ibi._itara = Itara()
        ibi._muyoboro = Muyoboro(ibi._itara, ikoresho)
        return ibi._muyoboro.tangiza()

    def rirarika(ibi) -> int:
        if ibi._muyoboro:
            return ibi._muyoboro.rirarika()
        return 0

    def hagarika(ibi) -> None:
        if ibi._muyoboro:
            ibi._muyoboro.hagarika()
