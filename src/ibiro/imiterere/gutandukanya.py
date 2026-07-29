"""Gutandukanya — Imiterere yo gutandukanya (split)."""

from __future__ import annotations

from ibiro.imiterere.shingiro import Imiterere, Icyerekezo


class Gutandukanya(Imiterere):
    """Gutandukanya — Imiterere ya split view.

    Gutandukanya bigabanya idirishya mu bice
    bibiri (horizontal cyangwa vertical).
    """

    icyerekezo: Icyerekezo
    igipimo: float

    def __init__(ibi: "Gutandukanya", icyerekezo: Icyerekezo = Icyerekezo.HORIZONTAL, igipimo: float = 0.5, indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "gutandukanya"
        super().__init__(indangamuntu_ya, icyerekezo=icyerekezo)
        ibi.icyerekezo = icyerekezo
        ibi.igipimo = igipimo
