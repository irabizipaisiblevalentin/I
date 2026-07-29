"""Imbonerahamwe — Ikoresho ry'imbonerahamwe."""

from __future__ import annotations

from typing import List, Any, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class InkingiImbonerahamwe:
    """Inkingi y'imbonerahamwe."""

    umutwe: str
    urufunguzo: str
    ubugari: int

    def __init__(ibi: "InkingiImbonerahamwe", umutwe: str, urufunguzo: str, ubugari: int = 100):
        ibi.umutwe = umutwe
        ibi.urufunguzo = urufunguzo
        ibi.ubugari = ubugari


class UmurongoImbonerahamwe:
    """Umurongo w'imbonerahamwe."""

    amakuru: dict
    indangamuntu: str

    def __init__(ibi: "UmurongoImbonerahamwe", amakuru: dict, indangamuntu: str = ""):
        ibi.amakuru = amakuru
        ibi.indangamuntu = indangamuntu


class Imbonerahamwe(Ikoresho):
    """Imbonerahamwe — Igikoresho cya table.

    Imbonerahamwe ikoreshwa mugushyiraho amakuru
    mu buryo bw'imbonerahamwe ifite inkingi n'imirongo.
    """

    inkingi: List[InkingiImbonerahamwe]
    imirongo: List[UmurongoImbonerahamwe]

    def __init__(ibi: "Imbonerahamwe", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "imbonerahamwe"
        super().__init__(indangamuntu_ya)
        ibi.inkingi = []
        ibi.imirongo = []

    def kongera_inkingi(ibi: "Imbonerahamwe", inkingi: InkingiImbonerahamwe):
        """Kongera inkingi."""
        ibi.inkingi.append(inkingi)

    def kongera_umurongo(ibi: "Imbonerahamwe", umurongo: UmurongoImbonerahamwe):
        """Kongera umurongo."""
        ibi.imirongo.append(umurongo)

    def kuraho_umurongo(ibi: "Imbonerahamwe", umurongo: UmurongoImbonerahamwe):
        """Kuraho umurongo."""
        if umurongo in ibi.imirongo:
            ibi.imirongo.remove(umurongo)

    @property
    def umubare_imirongo(ibi: "Imbonerahamwe") -> int:
        """Umubare w'imiringo."""
        return len(ibi.imirongo)
