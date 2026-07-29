"""Kunyerera — Ikoresho rya slider."""

from __future__ import annotations

from ibiro.ibikoresho.ikoresho import Ikoresho


class Kunyerera(Ikoresho):
    """Kunyerera — Igikoresho cya slider.

    Kunyerera gikoreshwa guhitamo agaciro
    mu nzira y'ikunyerera.
    """

    agaciro: float
    ntoya: float
    nini: float
    intambwe: float

    def __init__(
        ibi: "Kunyerera",
        indangamuntu: str = "",
        agaciro: float = 50.0,
        ntoya: float = 0.0,
        nini: float = 100.0,
        intambwe: float = 1.0,
    ):
        indangamuntu_ya = indangamuntu or f"kunyerera_{len(indangamuntu)}"
        super().__init__(indangamuntu_ya)
        ibi.agaciro = agaciro
        ibi.ntoya = ntoya
        ibi.nini = nini
        ibi.intambwe = intambwe
