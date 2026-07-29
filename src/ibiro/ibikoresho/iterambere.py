"""Iterambere — Ibikoresho by'iterambere (progress)."""

from __future__ import annotations

from ibiro.ibikoresho.ikoresho import Ikoresho


class Iterambere(Ikoresho):
    """Iterambere — Igikoresho cya progress bar."""

    agaciro: float
    nini: float

    def __init__(ibi: "Iterambere", indangamuntu: str = "", agaciro: float = 0.0, nini: float = 100.0):
        indangamuntu_ya = indangamuntu or f"iterambere_{len(indangamuntu)}"
        super().__init__(indangamuntu_ya)
        ibi.agaciro = agaciro
        ibi.nini = nini

    @property
    def ijanisha(ibi: "Iterambere") -> float:
        """Ijanisha ry'iterambere."""
        if ibi.nini == 0:
            return 0.0
        return (ibi.agaciro / ibi.nini) * 100.0


class Uruziga(Ikoresho):
    """Uruziga — Igikoresho cya spinner.

    Uruziga rugaragaza ko porogaramu
    iri gukora ikintu.
    """

    riratera: bool

    def __init__(ibi: "Uruziga", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "uruziga"
        super().__init__(indangamuntu_ya)
        ibi.riratera = True
