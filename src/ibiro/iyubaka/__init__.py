"""Iyubaka — Gupakira porogaramu (packaging).

Iki modulu gikubiyemo uburyo bwo gupakira
porogaramu ya IBIRO kugirango igendeswe
ahandi (AppImage, Flatpak, MSI, DMG, etc.).
"""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional


class ImiterereIyubaka(Enum):
    """Imiterere y'iyubaka."""
    UBUNTU = auto()
    FLATPAK = auto()
    SNAP = auto()
    DEB = auto()
    EXE = auto()
    MSI = auto()
    APP = auto()
    DMG = auto()


class IgenamiterereIyubaka:
    """Igenamiterere ry'iyubaka."""

    izina: str
    verisiyo: str
    umuyobozi: str
    imiterere: List[ImiterereIyubaka]
    ikimenyetso: str

    def __init__(
        ibi: "IgenamiterereIyubaka",
        izina: str = "porogaramu",
        verisiyo: str = "0.1.0",
        umuyobozi: str = ".",
        imiterere: List[ImiterereIyubaka] = None,
        ikimenyetso: str = "",
    ):
        ibi.izina = izina
        ibi.verisiyo = verisiyo
        ibi.umuyobozi = umuyobozi
        ibi.imiterere = imiterere or [ImiterereIyubaka.UBUNTU]
        ibi.ikimenyetso = ikimenyetso


class Umubaka:
    """Umubaka — Package builder."""

    _igenamiterere: IgenamiterereIyubaka

    def __init__(ibi: "Umubaka", igenamiterere: IgenamiterereIyubaka):
        ibi._igenamiterere = igenamiterere

    def kubaka(ibi: "Umubaka", imiterere: ImiterereIyubaka) -> bool:
        """Kubaka porogaramu.

        Arguments:
            imiterere: Imiterere y'iyubaka

        Returns:
            bool: Byakunze cyangwa oya
        """
        return True
