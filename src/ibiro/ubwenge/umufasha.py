"""Umufasha — AI assistant integration."""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional


class UruhatoUmufasha(Enum):
    """Uruhato rw'umufasha."""
    SISITEMU = auto()
    UMUKORESHA = auto()
    UMUFASHA = auto()


class UbutumwaUmufasha:
    """Ubutumwa bw'umufasha."""

    uruhato: UruhatoUmufasha
    ibiyirimo: str

    def __init__(ibi: "UbutumwaUmufasha", uruhato: UruhatoUmufasha, ibiyirimo: str):
        ibi.uruhato = uruhato
        ibi.ibiyirimo = ibiyirimo


class Umufasha:
    """Umufasha — AI assistant.

    Umufasha afasha mu gukora inshingano
    za porogaramu akoresheje ubwenge bw'ikoranabuhanga.
    """

    _amakuru: List[UbutumwaUmufasha]

    def __init__(ibi: "Umufasha"):
        ibi._amakuru = []

    def kongera_ubutumwa(ibi: "Umufasha", ubutumwa: UbutumwaUmufasha):
        ibi._amakuru.append(ubutumwa)

    def igisubizo(ibi: "Umufasha", ubutumwa: str) -> Optional[str]:
        """Shaka igisubizo ku butumwa."""
        return None
