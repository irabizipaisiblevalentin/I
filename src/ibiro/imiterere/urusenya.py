"""Urusenya — Imiterere y'urusenya (grid)."""

from __future__ import annotations

from typing import Dict, Tuple

from ibiro.imiterere.shingiro import Imiterere


class Urusenya(Imiterere):
    """Urusenya — Imiterere ya grid.

    Urusenya rushyira ibikoresho mu buryo
    bw'urusenya rufite imirongo n'inkingi.
    """

    imirongo: int
    inkingi: int
    ibikoresho_mu_rusenya: Dict[str, Tuple[int, int]]

    def __init__(ibi: "Urusenya", imirongo: int = 2, inkingi: int = 2, indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "urusenya"
        super().__init__(indangamuntu_ya)
        ibi.imirongo = imirongo
        ibi.inkingi = inkingi
        ibi.ibikoresho_mu_rusenya = {}

    def shyira(ibi: "Urusenya", ikoresho, umurongo: int = 0, inkingi: int = 0):
        """Shyira igikoresho mu rusenya."""
        ibi.kongera(ikoresho)
        ibi.ibikoresho_mu_rusenya[ikoresho.indangamuntu] = (umurongo, inkingi)
