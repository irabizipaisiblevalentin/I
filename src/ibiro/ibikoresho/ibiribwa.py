"""Ibiribwa — Ibikoresho by'ibiribwa (menu).

Iki modulu gikubiyemo ibiribwa, ikintu c'ibiribwa,
umurongo w'ibiribwa, n'ibiribwa by'ibanga.
"""

from __future__ import annotations

from typing import List, Callable, Any, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class IkintuIbiribwa:
    """Ikintu mu biribwa."""

    inyandiko: str
    indangamuntu: str
    rikora: Optional[Callable[..., Any]]
    nubwo_bishoboka: bool

    def __init__(
        ibi: "IkintuIbiribwa",
        inyandiko: str,
        indangamuntu: str = "",
        rikora: Optional[Callable[..., Any]] = None,
        nubwo_bishoboka: bool = True,
    ):
        ibi.inyandiko = inyandiko
        ibi.indangamuntu = indangamuntu
        ibi.rikora = rikora
        ibi.nubwo_bishoboka = nubwo_bishoboka


class Ibiribwa(Ikoresho):
    """Ibiribwa — Igikoresho cya menu."""

    ibintu: List[IkintuIbiribwa]
    inyandiko: str

    def __init__(ibi: "Ibiribwa", inyandiko: str = "", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or f"ibiribwa_{len(inyandiko)}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko
        ibi.ibintu = []

    def kongera(ibi: "Ibiribwa", ikintu: IkintuIbiribwa):
        ibi.ibintu.append(ikintu)


class UmurongoIbiribwa(Ikoresho):
    """Umurongo w'Ibiribwa — Menu bar."""

    ibiribwa: List[Ibiribwa]

    def __init__(ibi: "UmurongoIbiribwa", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "umurongo_ibiribwa"
        super().__init__(indangamuntu_ya)
        ibi.ibiribwa = []

    def kongera(ibi: "UmurongoIbiribwa", ibiribwa: Ibiribwa):
        ibi.ibiribwa.append(ibiribwa)


class IbiribwaByibanga(Ikoresho):
    """Ibiribwa By'ibanga — Context menu."""

    ibintu: List[IkintuIbiribwa]

    def __init__(ibi: "IbiribwaByibanga", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "ibiribwa_byibanga"
        super().__init__(indangamuntu_ya)
        ibi.ibintu = []

    def kongera(ibi: "IbiribwaByibanga", ikintu: IkintuIbiribwa):
        ibi.ibintu.append(ikintu)

    def kwerekana(ibi: "IbiribwaByibanga", x: int = 0, y: int = 0):
        """Kwerekana ibiribwa by'ibanga."""
        pass
