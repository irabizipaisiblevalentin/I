"""Porogaramu — Ishingiro rya porogaramu ya IBIRO.

Iki modulu gikubiyemo Porogaramu nyamukuru ikoreshwa
mu gutangiza no gucunga porogaramu za desktop.
"""

from __future__ import annotations

from typing import Optional

from ibiro.idirishya import UyoboreIdirishya
from ibiro.urwego.menya import kora_inyuma


class Porogaramu:
    """Porogaramu nyamukuru ya IBIRO.

    Iyi niyo nzinga rya porogaramu. Ikora, icunga amadirishya,
    kandi iha urwego rwo gukora porogaramu za desktop.

    Ibiranga:
        izina: Izina rya porogaramu
        umuryango: Izina ry'umuryango cyangwa org
        uyobore_idirishya: Uyobore w'amadirishya
    """

    izina: str
    umuryango: str
    uyobore_idirishya: UyoboreIdirishya
    _inyuma: Optional["Inyuma"]

    def __init__(ibi: "Porogaramu", izina: str, umuryango: str) -> None:
        """Tangiza porogaramu nshya.

        Arguments:
            izina: Izina rya porogaramu
            umuryango: Izina ry'umuryango
        """
        ibi.izina = izina
        ibi.umuryango = umuryango
        ibi.uyobore_idirishya = UyoboreIdirishya()
        ibi._inyuma = None

    @property
    def inyuma(ibi: "Porogaramu") -> "Inyuma":
        """Shaka cyangwa kora inyuma ya porogaramu."""
        if ibi._inyuma is None:
            ibi._inyuma = kora_inyuma()
        return ibi._inyuma

    def genda(ibi: "Porogaramu") -> int:
        """Tangiza porogaramu.

        Iyi methodo itangiza porogaramu kandi igakora
        ibikorwa byayo by'ibanze.

        Returns:
            int: Kode y'isohoka (0 = neza)
        """
        inyuma = ibi.inyuma
        inyuma.tangiza()
        igisubizo = inyuma.rirarika()
        return igisubizo

    def gerereza(ibi: "Porogaramu", indangamuntu: str, **igenamiterere):
        """Gerereza porogaramu mu nzego.
        
        Iyi methodo ikoreshwa mugihe porogaramu ikeneye
        kujya mu nzego zitandukanye (run, build, package, etc.).
        
        Arguments:
            indangamuntu: Indangamuntu y'urwego
            **igenamiterere: Igenamiterere ry'urwego
        """
        pass
