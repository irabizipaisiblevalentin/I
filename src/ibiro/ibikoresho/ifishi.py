"""Ifishi — Ikoresho rya form.

Iki modulu gikubiyemo ifishi, umurima w'ifishi,
n'ubugenzuzi bw'ifishi.
"""

from __future__ import annotations

from typing import List, Callable, Any, Dict, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class UmurimaIfishi:
    """Umurima w'ifishi — Field mu ifishi."""

    urufunguzo: str
    ikimenyetso: str
    agaciro: Any
    ubwoko: type

    def __init__(ibi: "UmurimaIfishi", urufunguzo: str, ikimenyetso: str = "", agaciro: Any = None, ubwoko: type = str):
        ibi.urufunguzo = urufunguzo
        ibi.ikimenyetso = ikimenyetso
        ibi.agaciro = agaciro
        ibi.ubwoko = ubwoko


class UbugenzuziIfishi:
    """Ubugenzuzi bw'ifishi — Form validator."""

    amategeko: Dict[str, Callable[[Any], bool]]

    def __init__(ibi: "UbugenzuziIfishi"):
        ibi.amategeko = {}

    def kongera_itegeko(ibi: "UbugenzuziIfishi", urufunguzo: str, igenzura: Callable[[Any], bool]):
        ibi.amategeko[urufunguzo] = igenzura

    def genzura(ibi: "UbugenzuziIfishi", amakuru: Dict[str, Any]) -> bool:
        for urufunguzo, agaciro in amakuru.items():
            if urufunguzo in ibi.amategeko:
                if not ibi.amategeko[urufunguzo](agaciro):
                    return False
        return True


class Ifishi(Ikoresho):
    """Ifishi — Igikoresho cya form.

    Ifishi ikoreshwa gukusanya amakuru
    aturutse ku mukoresha.
    """

    imirima: List[UmurimaIfishi]
    ubugenzuzi: UbugenzuziIfishi

    def __init__(ibi: "Ifishi", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "ifishi"
        super().__init__(indangamuntu_ya)
        ibi.imirima = []
        ibi.ubugenzuzi = UbugenzuziIfishi()

    def kongera_umurima(ibi: "Ifishi", umurima: UmurimaIfishi):
        ibi.imirima.append(umurima)

    def gusubiza(ibi: "Ifishi") -> Dict[str, Any]:
        igisubizo = {}
        for umurima in ibi.imirima:
            igisubizo[umurima.urufunguzo] = umurima.agaciro
        return igisubizo

    def genzura(ibi: "Ifishi") -> bool:
        amakuru = ibi.gusubiza()
        return ibi.ubugenzuzi.genzura(amakuru)
