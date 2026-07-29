"""Kwitabira — Imiterere yikwitabira (responsive)."""

from __future__ import annotations

from typing import Dict

from ibiro.imiterere.shingiro import Imiterere


class Kwitabira(Imiterere):
    """Kwitabira — Imiterere ikwitabira (responsive).

    Kwitabira gusimbura imiterere iburiro
    mu gihe ingano y'idirishya ihindutse.
    """

    imirongo_ingenzi: Dict[str, int]

    def __init__(ibi: "Kwitabira", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "kwitabira"
        super().__init__(indangamuntu_ya)
        ibi.imirongo_ingenzi = {
            "ntoya": 480,
            "hagati": 768,
            "nini": 1024,
        }
