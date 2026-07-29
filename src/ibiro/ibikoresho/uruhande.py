"""Uruhande — Ikoresho rwa sidebar."""

from __future__ import annotations

from typing import List, Callable, Any, Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class IkintuUruhande:
    """Ikintu mu ruhande."""

    inyandiko: str
    ikimenyetso: str
    indangamuntu: str
    rikora: Optional[Callable[..., Any]]

    def __init__(ibi: "IkintuUruhande", inyandiko: str = "", ikimenyetso: str = "", indangamuntu: str = "", rikora: Optional[Callable[..., Any]] = None):
        ibi.inyandiko = inyandiko
        ibi.ikimenyetso = ikimenyetso
        ibi.indangamuntu = indangamuntu or f"uruhande_{len(inyandiko)}"
        ibi.rikora = rikora


class Uruhande(Ikoresho):
    """Uruhande — Igikoresho cya sidebar.

    Uruhande rugaragaza ibintu ku ruhande
    rw'idirishya.
    """

    ibintu: List[IkintuUruhande]

    def __init__(ibi: "Uruhande", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "uruhande"
        super().__init__(indangamuntu_ya)
        ibi.ibintu = []

    def kongera(ibi: "Uruhande", ikintu: IkintuUruhande):
        ibi.ibintu.append(ikintu)
