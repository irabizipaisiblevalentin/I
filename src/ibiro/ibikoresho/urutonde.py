"""Urutonde — Ikoresho ry'urutonde (list)."""

from __future__ import annotations

from typing import List, Any, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class IkintuUrutonde:
    """Ikintu mu rutonde."""

    inyandiko: str
    agaciro: Any

    def __init__(ibi: "IkintuUrutonde", inyandiko: str, agaciro: Any = None):
        ibi.inyandiko = inyandiko
        ibi.agaciro = agaciro


class Urutonde(Ikoresho):
    """Urutonde — Igikoresho cya list.

    Urutonde rukoreshwa kwerekana ibintu
    mu buryo bw'urutonde.
    """

    ibintu: List[IkintuUrutonde]

    def __init__(ibi: "Urutonde", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "urutonde"
        super().__init__(indangamuntu_ya)
        ibi.ibintu = []

    def kongera(ibi: "Urutonde", ikintu: IkintuUrutonde):
        """Kongera ikintu mu rutonde."""
        ibi.ibintu.append(ikintu)

    def kuraho(ibi: "Urutonde", ikintu: IkintuUrutonde):
        """Kuraho ikintu mu rutonde."""
        if ikintu in ibi.ibintu:
            ibi.ibintu.remove(ikintu)

    @property
    def umubare(ibi: "Urutonde") -> int:
        return len(ibi.ibintu)
