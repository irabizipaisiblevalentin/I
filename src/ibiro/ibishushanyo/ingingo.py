"""Ingingo — Icungamiterere ry'ingingo (theme)."""

from __future__ import annotations

from enum import Enum, auto
from typing import Dict, Optional

from ibiro.ibishushanyo.ibara import Ibara


class IngingoZubatswe(Enum):
    """Ingingo zubatswe muri IBIRO."""
    URUMURI = auto()
    UMIJIMA = auto()
    IMWERU_NINI = auto()


class Ingingo:
    """Ingingo — Theme ya IBIRO.

    Ingingo itanga amabara n'imiterere
    ya porogaramu yose.
    """

    izina: str
    amabara: Dict[str, Ibara]
    ibindi: Dict

    def __init__(ibi: "Ingingo", izina: str = "urumuri"):
        ibi.izina = izina
        ibi.amabara = {}
        ibi.ibindi = {}

    def shira_ibara(ibi: "Ingingo", izina: str, ibara: Ibara):
        ibi.amabara[izina] = ibara

    def ibara(ibi: "Ingingo", izina: str, mburabura: Optional[Ibara] = None) -> Optional[Ibara]:
        return ibi.amabara.get(izina, mburabura)


class UyoboreIngingo:
    """Uyobore w'ingingo — Theme manager."""

    _ingingo_kiriho: Optional[Ingingo] = None
    _ingingo_zubatswe: Dict[IngingoZubatswe, Ingingo] = {}

    @classmethod
    def ingingo_zubatswe(cls, ubwoko: IngingoZubatswe) -> Ingingo:
        """Shaka ingingo zubatswe."""
        if ubwoko not in cls._ingingo_zubatswe:
            ingingo = Ingingo(izina=ubwoko.name.lower())
            if ubwoko == IngingoZubatswe.URUMURI:
                ingingo.shira_ibara("inyuma", Ibara.kuva_hex("#ffffff"))
                ingingo.shira_ibara("imbere", Ibara.kuva_hex("#000000"))
                ingingo.shira_ibara("byibanze", Ibara.kuva_hex("#0078d4"))
            elif ubwoko == IngingoZubatswe.UMIJIMA:
                ingingo.shira_ibara("inyuma", Ibara.kuva_hex("#1e1e1e"))
                ingingo.shira_ibara("imbere", Ibara.kuva_hex("#ffffff"))
                ingingo.shira_ibara("byibanze", Ibara.kuva_hex("#0078d4"))
            cls._ingingo_zubatswe[ubwoko] = ingingo
        return cls._ingingo_zubatswe[ubwoko]

    @classmethod
    def shira_kiriho(cls, ingingo: Ingingo):
        cls._ingingo_kiriho = ingingo

    @classmethod
    def kiriho(cls) -> Ingingo:
        if cls._ingingo_kiriho is None:
            cls._ingingo_kiriho = cls.ingingo_zubatswe(IngingoZubatswe.URUMURI)
        return cls._ingingo_kiriho
