"""Umurongo — Imiterere y'umurongo (row)."""

from __future__ import annotations

from ibiro.imiterere.shingiro import Imiterere, Icyerekezo, Guringaniza


class Umurongo(Imiterere):
    """Umurongo — Imiterere itambika (horizontal).

    Umurongo ushyira ibikoresho mu buryo
    butambitse (horizontal layout).
    """

    kwizinga: bool

    def __init__(ibi: "Umurongo", indangamuntu: str = "", kwizinga: bool = False, guringaniza: Guringaniza = Guringaniza.ITANGIRA):
        super().__init__(indangamuntu=indangamuntu, icyerekezo=Icyerekezo.HORIZONTAL, guringaniza=guringaniza)
        ibi.kwizinga = kwizinga
