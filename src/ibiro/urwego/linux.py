"""Inyuma Linux — Linux platform backend."""

from __future__ import annotations

import sys
import subprocess
from typing import Tuple, Optional

from typing import Optional

from ibiro.urwego.shingiro import Inyuma
from ibiro.urwego.itara import Itara
from ibiro.urwego.muyoboro import Muyoboro


class InyumaLinux(Inyuma):
    """Inyuma Linux — Linux backend using xclip/notify-send + web renderer."""

    def inyuma_urwego(ibi) -> str:
        return "Linux"

    def ingano_ikiganiro(ibi) -> Tuple[int, int]:
        try:
            igisubizo = subprocess.run(["xrandr", "--current"], capture_output=True, text=True)
            for umurongo in igisubizo.stdout.splitlines():
                if "*" in umurongo and "connected" not in umurongo:
                    ibice = umurongo.strip().split()
                    for igice in ibice:
                        if "x" in igice:
                            ubugari, uburebure = igice.split("x")
                            return (int(ubugari), int(uburebure[0:4]))
            return (1920, 1080)
        except Exception:
            return (1920, 1080)

    def shaka_muri_duporo(ibi) -> Optional[str]:
        try:
            igisubizo = subprocess.run(["xclip", "-o", "-selection", "clipboard"], capture_output=True, text=True)
            return igisubizo.stdout if igisubizo.returncode == 0 else None
        except Exception:
            return None

    def shira_muri_duporo(ibi, inyandiko: str) -> bool:
        try:
            subprocess.run(["xclip", "-selection", "clipboard"], input=inyandiko, text=True)
            return True
        except Exception:
            return False

    def menyesha(ibi, umutwe: str, inyandiko: str) -> bool:
        try:
            subprocess.run(["notify-send", umutwe, inyandiko])
            return True
        except Exception:
            return False

    def wiga_urwego(ibi) -> str:
        return sys.platform

    _itara: Optional[Itara]
    _muyoboro: Optional[Muyoboro]

    def __init__(ibi: "InyumaLinux"):
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
