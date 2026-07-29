"""Itangazo — Ibikoresho by'itangazo (notification)."""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class UrwegoImenyekanisha(Enum):
    """Urwego rw'imenyesha."""
    AMAKURU = auto()
    INTSINZI = auto()
    IBURIRA = auto()
    IKOSA = auto()


class Imenyekanisha:
    """Imenyekanisha — Notification."""

    umutwe: str
    inyandiko: str
    urwego: UrwegoImenyekanisha

    def __init__(ibi: "Imenyekanisha", umutwe: str = "", inyandiko: str = "", urwego: UrwegoImenyekanisha = UrwegoImenyekanisha.AMAKURU):
        ibi.umutwe = umutwe
        ibi.inyandiko = inyandiko
        ibi.urwego = urwego


class Itangazo(Ikoresho):
    """Itangazo — Igikoresho cya notification banner."""

    imenyesha: Optional[Imenyekanisha]
    kaboneka: bool

    def __init__(ibi: "Itangazo", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "itangazo"
        super().__init__(indangamuntu_ya)
        ibi.imenyesha = None
        ibi.kaboneka = False

    def kwerekana(ibi: "Itangazo", imenyekanisha: Imenyekanisha):
        ibi.imenyesha = imenyekanisha
        ibi.kaboneka = True

    def guhisha(ibi: "Itangazo"):
        ibi.kaboneka = False
        ibi.imenyesha = None
