"""Ikarita — Ikoresho rya card."""

from __future__ import annotations

from ibiro.ibikoresho.ikoresho import Ikoresho


class Ikarita(Ikoresho):
    """Ikarita — Igikoresho cya card.

    Ikarita ikoreshwa kwerekana amakuru
    mu buryo bw'ikarita ifite umutwe, umubiri, n'ikirenge.
    """

    umutwe: Ikoresho
    umubiri: Ikoresho
    ikirenge: Ikoresho

    def __init__(ibi: "Ikarita", indangamuntu: str = "", umutwe: Ikoresho = None, umubiri: Ikoresho = None, ikirenge: Ikoresho = None):
        indangamuntu_ya = indangamuntu or "ikarita"
        super().__init__(indangamuntu_ya)
        ibi.umutwe = umutwe or Ikoresho(f"{indangamuntu_ya}_umutwe")
        ibi.umubiri = umubiri or Ikoresho(f"{indangamuntu_ya}_umubiri")
        ibi.ikirenge = ikirenge or Ikoresho(f"{indangamuntu_ya}_ikirenge")
        ibi.kongera(ibi.umutwe)
        ibi.kongera(ibi.umubiri)
        ibi.kongera(ibi.ikirenge)
