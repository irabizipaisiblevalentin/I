"""Idupuro — Clipboard integration."""

from __future__ import annotations

from typing import Optional

from ibiro.urwego.menya import kora_inyuma


class Idupuro:
    """Idupuro — Clipboard.

    Idupuro rikoreshwa gushyiraho no gukurura
    amakuru mu dupuro rwa sisitemu.
    """

    _inyuma = None

    def __init__(ibi: "Idupuro"):
        ibi._inyuma = kora_inyuma()

    def shaka(ibi: "Idupuro") -> Optional[str]:
        """Shaka amakuru mu dupuro.

        Returns:
            Optional[str]: Inyandiko mu dupuro cyangwa None
        """
        return ibi._inyuma.shaka_muri_duporo()

    def shira(ibi: "Idupuro", inyandiko: str) -> bool:
        """Shira inyandiko mu dupuro.

        Arguments:
            inyandiko: Inyandiko yo gushyira mu dupuro

        Returns:
            bool: Byakunze cyangwa oya
        """
        return ibi._inyuma.shira_muri_duporo(inyandiko)
