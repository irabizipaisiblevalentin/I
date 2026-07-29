"""Ishusho — Ikoresho ry'ishusho (image)."""

from __future__ import annotations

from ibiro.ibikoresho.ikoresho import Ikoresho


class Ishusho(Ikoresho):
    """Ishusho — Igikoresho cyo kwerekana ishusho."""

    inkomoko: str
    ubugari: int
    uburebure: int

    def __init__(ibi: "Ishusho", inkomoko: str = "", indangamuntu: str = "", ubugari: int = 100, uburebure: int = 100):
        indangamuntu_ya = indangamuntu or f"ishusho_{len(inkomoko)}"
        super().__init__(indangamuntu_ya)
        ibi.inkomoko = inkomoko
        ibi.ubugari = ubugari
        ibi.uburebure = uburebure
