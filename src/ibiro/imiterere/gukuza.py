"""Gukuza — Imiterere yo gukuza (scroll)."""

from __future__ import annotations

from ibiro.imiterere.shingiro import Imiterere


class Gukuza(Imiterere):
    """Gukuza — Imiterere ya scroll.

    Gukuza gutanga ubushobozi bwo gukuza
    ibikoresho iyo birenze ingano.
    """

    icyerekezo: str  # horizontal, vertical, byose
    x: int
    y: int

    def __init__(ibi: "Gukuza", icyerekezo: str = "vertical", indangamuntu: str = "", x: int = 0, y: int = 0):
        indangamuntu_ya = indangamuntu or "gukuza"
        super().__init__(indangamuntu_ya)
        ibi.icyerekezo = icyerekezo
        ibi.x = x
        ibi.y = y
