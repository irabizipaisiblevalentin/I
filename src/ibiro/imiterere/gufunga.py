"""Gufunga — Imiterere yo gufunga (dock)."""

from __future__ import annotations

from enum import Enum, auto

from ibiro.imiterere.shingiro import Imiterere


class UmwanyaGufunga(Enum):
    """Umwanya wo gufunga (dock position)."""
    HEJURU = auto()
    HASI = auto()
    IBUMOSO = auto()
    IBURYO = auto()
    HAGATI = auto()


class Gufunga(Imiterere):
    """Gufunga — Imiterere yo gufunga (dock layout).

    Gufunga gushyira ibikoresho ku mpande
    z'idirishya (top, bottom, left, right, center).
    """

    umwanya: UmwanyaGufunga

    def __init__(ibi: "Gufunga", umwanya: UmwanyaGufunga = UmwanyaGufunga.HAGATI, indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "gufunga"
        super().__init__(indangamuntu_ya)
        ibi.umwanya = umwanya
