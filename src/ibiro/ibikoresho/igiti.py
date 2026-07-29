"""Igiti — Ikoresho ry'igiti (tree).

Iki modulu gikubiyemo igiti n'ikinyabiziga cy'igiti.
"""

from __future__ import annotations

from typing import List, Any, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class IkinyabizigaIgiti:
    """Ikinyabiziga cy'igiti — Umwana w'igiti."""

    inyandiko: str
    indangamuntu: str
    abana: List["IkinyabizigaIgiti"]
    amakuru: Any

    def __init__(ibi: "IkinyabizigaIgiti", inyandiko: str, indangamuntu: str = "", amakuru: Any = None):
        ibi.inyandiko = inyandiko
        ibi.indangamuntu = indangamuntu or f"kinyabiziga_{len(inyandiko)}"
        ibi.abana = []
        ibi.amakuru = amakuru

    def kongera(ibi: "IkinyabizigaIgiti", umwana: "IkinyabizigaIgiti"):
        ibi.abana.append(umwana)

    @property
    def afite_abana(ibi: "IkinyabizigaIgiti") -> bool:
        return len(ibi.abana) > 0


class Igiti(Ikoresho):
    """Igiti — Igikoresho cya tree.

    Igiti gikoreshwa kwerekana imiterere
    y'ibintu ifite amashami (hierarchical).
    """

    imizi: List[IkinyabizigaIgiti]

    def __init__(ibi: "Igiti", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "igiti"
        super().__init__(indangamuntu_ya)
        ibi.imizi = []

    def kongera_umuzi(ibi: "Igiti", ikinyabiziga: IkinyabizigaIgiti):
        """Kongera ikinyabiziga nk'umuzi."""
        ibi.imizi.append(ikinyabiziga)
