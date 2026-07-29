"""Inkingi — Imiterere y'inkingi (column)."""

from __future__ import annotations

from ibiro.imiterere.shingiro import Imiterere, Icyerekezo, Guringaniza


class Inkingi(Imiterere):
    """Inkingi — Imiterere ihagaze (vertical).

    Inkingi ishyira ibikoresho mu buryo
    buhagaze (vertical layout).
    """

    kwagura: bool

    def __init__(ibi: "Inkingi", indangamuntu: str = "", kwagura: bool = False, guringaniza: Guringaniza = Guringaniza.ITANGIRA):
        super().__init__(indangamuntu=indangamuntu, icyerekezo=Icyerekezo.VERTICAL, guringaniza=guringaniza)
        ibi.kwagura = kwagura
