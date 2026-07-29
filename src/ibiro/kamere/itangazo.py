"""Itangazo — Native notifications."""

from __future__ import annotations

from ibiro.urwego.menya import kora_inyuma


class UyoboreItangazo:
    """Uyobore Itangazo — Notification manager."""

    _inyuma = None

    def __init__(ibi: "UyoboreItangazo"):
        ibi._inyuma = kora_inyuma()

    def menyesha(ibi: "UyoboreItangazo", umutwe: str, inyandiko: str) -> bool:
        """Tanga imenyekanisha.

        Arguments:
            umutwe: Umutwe w'imenyesha
            inyandiko: Inyandiko y'imenyesha

        Returns:
            bool: Byakunze cyangwa oya
        """
        return ibi._inyuma.menyesha(umutwe, inyandiko)
