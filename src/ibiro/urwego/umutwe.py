"""Inyuma Umutwe — Headless platform backend for testing."""

from __future__ import annotations

from typing import Tuple, Optional

from ibiro.urwego.shingiro import Inyuma


class InyumaUmutwe(Inyuma):
    """Inyuma Umutwe — Headless backend for testing/CI."""

    _duporo: str = ""

    def inyuma_urwego(ibi) -> str:
        return "Headless"

    def ingano_ikiganiro(ibi) -> Tuple[int, int]:
        return (1920, 1080)

    def shaka_muri_duporo(ibi) -> Optional[str]:
        return ibi._duporo or None

    def shira_muri_duporo(ibi, inyandiko: str) -> bool:
        ibi._duporo = inyandiko
        return True

    def menyesha(ibi, umutwe: str, inyandiko: str) -> bool:
        return True

    def wiga_urwego(ibi) -> str:
        return "headless"
