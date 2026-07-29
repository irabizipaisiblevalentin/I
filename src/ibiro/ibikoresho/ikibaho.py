"""Ikibaho — Ikoresho rya status bar."""

from __future__ import annotations

from typing import List

from ibiro.ibikoresho.ikoresho import Ikoresho


class IgiceIkibaho:
    """Igice cy'ikibaho — Status bar section."""

    inyandiko: str
    ubugari: int

    def __init__(ibi: "IgiceIkibaho", inyandiko: str = "", ubugari: int = 100):
        ibi.inyandiko = inyandiko
        ibi.ubugari = ubugari


class Ikibaho(Ikoresho):
    """Ikibaho — Igikoresho cya status bar.

    Ikibaho kigaragaza amakuru ajyanye
    n'imiterere ya porogaramu.
    """

    ibice: List[IgiceIkibaho]

    def __init__(ibi: "Ikibaho", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "ikibaho"
        super().__init__(indangamuntu_ya)
        ibi.ibice = []

    def kongera_igice(ibi: "Ikibaho", igice: IgiceIkibaho):
        ibi.ibice.append(igice)

    def shira_inyandiko(ibi: "Ikibaho", inyandiko: str):
        """Shira inyandiko mu gice cya mbere."""
        if ibi.ibice:
            ibi.ibice[0].inyandiko = inyandiko
