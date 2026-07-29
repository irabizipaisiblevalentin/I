"""Umweru — Ikoresho rya tabs."""

from __future__ import annotations

from typing import List

from ibiro.ibikoresho.ikoresho import Ikoresho


class Akabati(Ikoresho):
    """Akabati — Tab imwe."""

    umutwe: str
    ibiyirimo: Ikoresho

    def __init__(ibi: "Akabati", umutwe: str = "", ibiyirimo: Ikoresho = None, indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or f"akabati_{len(umutwe)}"
        super().__init__(indangamuntu_ya)
        ibi.umutwe = umutwe
        ibi.ibiyirimo = ibiyirimo or Ikoresho(f"{indangamuntu_ya}_ibiyirimo")


class Umweru(Ikoresho):
    """Umweru — Igikoresho cya tabs.

    Umweru ukoreshwa kwerekana ibintu
    mu buryo bw'umweru utandukanye.
    """

    amabati: List[Akabati]
    akabati_gukina: int

    def __init__(ibi: "Umweru", indangamuntu: str = ""):
        indangamuntu_ya = indangamuntu or "umweru"
        super().__init__(indangamuntu_ya)
        ibi.amabati = []
        ibi.akabati_gukina = 0

    def kongera(ibi: "Umweru", akabati: Akabati):
        ibi.amabati.append(akabati)

    def hitamo(ibi: "Umweru", indangamuntu: int):
        """Hitamo akabati."""
        if 0 <= indangamuntu < len(ibi.amabati):
            ibi.akabati_gukina = indangamuntu

    @property
    def akabati_kiriho(ibi: "Umweru") -> Akabati:
        return ibi.amabati[ibi.akabati_gukina]
