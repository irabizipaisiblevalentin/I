"""Ubugenzuzi — Visual inspector."""

from __future__ import annotations

from typing import List, Dict, Any
from ibiro.ibikoresho.ikoresho import Ikoresho


class Ubugenzuzi:
    """Ubugenzuzi — Visual inspector.

    Ubugenzuzi bugaragaza imiterere y'igiti
    cy'ibikoresho (widget tree) mu buryo
    bworoshye.
    """

    _umuzi: Ikoresho

    def __init__(ibi: "Ubugenzuzi", umuzi: Ikoresho):
        ibi._umuzi = umuzi

    def kora_igiti(ibi: "Ubugenzuzi") -> List[Dict[str, Any]]:
        """Kora igiti cy'ibikoresho.

        Returns:
            List[Dict]: Igiti cy'ibikoresho
        """
        igisubizo = []
        ibi._kwagura(ibi._umuzi, igisubizo, 0)
        return igisubizo

    def _kwagura(ibi: "Ubugenzuzi", ikoresho: Ikoresho, igisubizo: List, urwego: int):
        ibintu = {
            "indangamuntu": ikoresho.indangamuntu,
            "imiterere": ikoresho.imiterere.izina,
            "abana": [],
            "urwego": urwego,
        }
        igisubizo.append(ibintu)
        for umwana in ikoresho.abana:
            ibi._kwagura(umwana, ibintu["abana"], urwego + 1)
