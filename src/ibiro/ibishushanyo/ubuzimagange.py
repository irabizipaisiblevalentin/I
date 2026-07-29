"""Ubuzimagange — Icungamiterere ry'ubuzimagange (animation)."""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Callable, Any

from ibiro.ibikoresho.ikoresho import Ikoresho


class UmurongoUbuzimagange(Enum):
    """Umurongo w'ubuzimagange (animation curve)."""
    LINEARI = auto()
    MWIZERERANYI = auto()
    KURIYO = auto()
    KURIYO_KURE = auto()
    IKUBITI = auto()


class Ubuzimagange:
    """Ubuzimagange — Animation.

    Ubuzimagange bukoreshwa guhindura agaciro
    k'igikoresho mu gihe.
    """

    indangamuntu_igikoresho: str
    umutungo: str
    kuva: float
    kugeza: float
    igihe: float
    umurongo: UmurongoUbuzimagange

    def __init__(
        ibi: "Ubuzimagange",
        indangamuntu_igikoresho: str,
        umutungo: str,
        kuva: float = 0.0,
        kugeza: float = 1.0,
        igihe: float = 1.0,
        umurongo: UmurongoUbuzimagange = UmurongoUbuzimagange.LINEARI,
    ):
        ibi.indangamuntu_igikoresho = indangamuntu_igikoresho
        ibi.umutungo = umutungo
        ibi.kuva = kuva
        ibi.kugeza = kugeza
        ibi.igihe = igihe
        ibi.umurongo = umurongo


class ItsindaUbuzimagange:
    """Itsinda ry'ubuzimagange — Animation group."""

    ubuzimagange: List[Ubuzimagange]

    def __init__(ibi: "ItsindaUbuzimagange"):
        ibi.ubuzimagange = []

    def kongera(ibi: "ItsindaUbuzimagange", ubuzimagange: Ubuzimagange):
        ibi.ubuzimagange.append(ubuzimagange)


class MoteriUbuzimagange:
    """Moteri y'ubuzimagange — Animation engine."""

    _iruka: List[Ubuzimagange]

    def __init__(ibi: "MoteriUbuzimagange"):
        ibi._iruka = []

    def gucuranga(ibi: "MoteriUbuzimagange", ubuzimagange: Ubuzimagange):
        """Tangiza ubuzimagange."""
        ibi._iruka.append(ubuzimagange)
