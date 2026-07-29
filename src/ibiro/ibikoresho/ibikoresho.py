"""Ibikoresho — Urutonde rw'ibikoresho (toolbar)."""

from __future__ import annotations

from typing import List, Callable, Any, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class Igikoresho:
    """Igikoresho mu rutonde rw'ibikoresho."""

    inyandiko: str
    ikimenyetso: str
    rikora: Optional[Callable[..., Any]]

    def __init__(ibi: "Igikoresho", inyandiko: str = "", ikimenyetso: str = "", rikora: Optional[Callable[..., Any]] = None):
        ibi.inyandiko = inyandiko
        ibi.ikimenyetso = ikimenyetso
        ibi.rikora = rikora


class UrutondeIbikoresho(Ikoresho):
    """Urutonde rw'ibikoresho — Igikoresho cya toolbar."""

    ibikoresho: List[Igikoresho]

    def __init__(ibi: "UrutondeIbikoresho", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "urutonde_ibikoresho"
        super().__init__(indangamuntu_ya)
        ibi.ibikoresho = []

    def kongera(ibi: "UrutondeIbikoresho", igikoresho: Igikoresho):
        ibi.ibikoresho.append(igikoresho)

    def kuraho(ibi: "UrutondeIbikoresho", igikoresho: Igikoresho):
        if igikoresho in ibi.ibikoresho:
            ibi.ibikoresho.remove(igikoresho)
