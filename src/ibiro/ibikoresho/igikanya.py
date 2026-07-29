"""Igikanya — Ikoresho rya canvas.

Iki modulu gikubiyemo igikanya n'ibishushanyo.
"""

from __future__ import annotations

from typing import List, Any

from ibiro.ibikoresho.ikoresho import Ikoresho


class Ishushanyo:
    """Ishushanyo shingiro."""

    x: float
    y: float
    ibara: str

    def __init__(ibi: "Ishushanyo", x: float = 0, y: float = 0, ibara: str = "#000000"):
        ibi.x = x
        ibi.y = y
        ibi.ibara = ibara


class Agasanduku(Ishushanyo):
    """Agasanduku — Rectangle."""

    ubugari: float
    uburebure: float
    uruziga: float

    def __init__(ibi: "Agasanduku", x: float = 0, y: float = 0, ubugari: float = 100, uburebure: float = 100, ibara: str = "#000000", uruziga: float = 0):
        super().__init__(x, y, ibara)
        ibi.ubugari = ubugari
        ibi.uburebure = uburebure
        ibi.uruziga = uruziga


class Umuzingiti(Ishushanyo):
    """Umuzingiti — Circle."""

    radiyo: float

    def __init__(ibi: "Umuzingiti", x: float = 0, y: float = 0, radiyo: float = 50, ibara: str = "#000000"):
        super().__init__(x, y, ibara)
        ibi.radiyo = radiyo


class Umurongo(Ishushanyo):
    """Umurongo — Line."""

    x2: float
    y2: float
    ubugari: float

    def __init__(ibi: "Umurongo", x: float = 0, y: float = 0, x2: float = 100, y2: float = 100, ibara: str = "#000000", ubugari: float = 1):
        super().__init__(x, y, ibara)
        ibi.x2 = x2
        ibi.y2 = y2
        ibi.ubugari = ubugari


class Inzira(Ishushanyo):
    """Inzira — Path."""

    amasoko: List[tuple]

    def __init__(ibi: "Inzira", amasoko: List[tuple] = None, ibara: str = "#000000"):
        super().__init__(0, 0, ibara)
        ibi.amasoko = amasoko or []


class IshushanyoInyandiko(Ishushanyo):
    """Ishushanyo ry'inyandiko — Text shape."""

    inyandiko: str
    ingano: int

    def __init__(ibi: "IshushanyoInyandiko", inyandiko: str = "", x: float = 0, y: float = 0, ibara: str = "#000000", ingano: int = 14):
        super().__init__(x, y, ibara)
        ibi.inyandiko = inyandiko
        ibi.ingano = ingano


class Igikanya(Ikoresho):
    """Igikanya — Igikoresho cya canvas.

    Igikanya gikoreshwa gushushanyaho
    ibishushanyo nk' agasanduku, umuzingiti, n'ibindi.
    """

    ibishushanyo: List[Ishushanyo]

    def __init__(ibi: "Igikanya", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "igikanya"
        super().__init__(indangamuntu_ya)
        ibi.ibishushanyo = []

    def kongera(ibi: "Igikanya", ishushanyo: Ishushanyo):
        ibi.ibishushanyo.append(ishushanyo)

    def kuraho(ibi: "Igikanya", ishushanyo: Ishushanyo):
        if ishushanyo in ibi.ibishushanyo:
            ibi.ibishushanyo.remove(ishushanyo)

    def kira(ibi: "Igikanya"):
        """Kira igikanya (clear canvas)."""
        ibi.ibishushanyo = []
