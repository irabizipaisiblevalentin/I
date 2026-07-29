"""Ikirundo — Imiterere y'ikirundo (stack)."""

from __future__ import annotations

from ibiro.imiterere.shingiro import Imiterere


class Ikirundo(Imiterere):
    """Ikirundo — Imiterere ya stack (overlay).

    Ikirundo gishyira ibikoresho hejuru y'ibindi
    (stack/overlay layout).
    """

    def __init__(ibi: "Ikirundo", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "ikirundo"
        super().__init__(indangamuntu_ya)
