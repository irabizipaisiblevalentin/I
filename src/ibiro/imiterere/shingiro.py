"""Shingiro ry'imiterere — Layout base."""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class Guringaniza(Enum):
    """Uburyo bwo guringaniza (alignment)."""
    ITANGIRA = auto()
    HAGATI = auto()
    IHERERO = auto()
    KURAMBURA = auto()


class Icyerekezo(Enum):
    """Icyerekezo cy'imiterere (direction)."""
    HORIZONTAL = auto()
    VERTICAL = auto()


class Imiterere(Ikoresho):
    """Imiterere — Ishingiro ry'imiterere yose.

    Imiterere ni ikintu gishyiraho ibikoresho
    mu buryo bw'imbonera.
    """

    icyerekezo: Icyerekezo
    guringaniza: Guringaniza

    def __init__(ibi: "Imiterere", indangamuntu: str = "", icyerekezo: Icyerekezo = Icyerekezo.VERTICAL, guringaniza: Guringaniza = Guringaniza.ITANGIRA):
        indangamuntu_ya = indangamuntu or "imiterere"
        super().__init__(indangamuntu_ya)
        ibi.icyerekezo = icyerekezo
        ibi.guringaniza = guringaniza
