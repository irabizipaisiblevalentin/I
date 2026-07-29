"""Ikoresho — Ishingiro ry'ibikoresho byose.

Iki modulu gikubiyemo Ikoresho, ari cyo shingiro
ry'ibikoresho byose bya IBIRO.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional, Set, Callable, Any, Dict


class ImiterereIkoresho(Enum):
    """Imiterere y'igikoresho."""
    KUREMWE = auto()
    KWEGERANYIJWE = auto()
    KWEREKANWE = auto()
    HISHWE = auto()
    HEREKEYE = auto()
    BYANGIJWE = auto()


class IkirangaIkoresho(Enum):
    """Ibiranga by'igikoresho."""
    HARI_INYIGITI = auto()
    NTIBISHOBOKA = auto()
    IHISHIJWE = auto()
    IHITAMO = auto()
    RIRAKORA = auto()
    RIRAKUZWA = auto()


class ImiterereshingiroIkoresho:
    """Imiterere y'igikoresho (style).

    Iyi miterere itanga ibara, umupaka, n'ibindi
    biranga igikoresho.
    """

    ibara_inyuma: str
    ibara_imbere: str
    ubugari_umupaka: int
    ibara_umupaka: str
    uruziga: int
    byinyuranyo: int
    impande: int

    def __init__(
        ibi: "ImiterereshingiroIkoresho",
        ibara_inyuma: str = "imyeyere",
        ibara_imbere: str = "#000000",
        ubugari_umupaka: int = 0,
        ibara_umupaka: str = "imyeyere",
        uruziga: int = 0,
        byinyuranyo: int = 0,
        impande: int = 0,
    ) -> None:
        ibi.ibara_inyuma = ibara_inyuma
        ibi.ibara_imbere = ibara_imbere
        ibi.ubugari_umupaka = ubugari_umupaka
        ibi.ibara_umupaka = ibara_umupaka
        ibi.uruziga = uruziga
        ibi.byinyuranyo = byinyuranyo
        ibi.impande = impande


class Ikoresho:
    """Ikoresho shingiro.

    Iki ni cyo kintu cy'ibanze mu bikoresho byose bya IBIRO.
    Gifite indangamuntu, imiterere, ibiranga, abana, n'ibindi.
    """

    indangamuntu: str
    imiterere: ImiterereIkoresho
    ibiranga: Set[IkirangaIkoresho]
    imiterereshingiro: ImiterereshingiroIkoresho
    abana: List["Ikoresho"]
    umubyeyi: Optional["Ikoresho"]
    amakuru: Dict[str, Any]
    ibikorwa: Dict[str, Callable[..., Any]]

    def __init__(ibi: "Ikoresho", indangamuntu: str) -> None:
        ibi.indangamuntu = indangamuntu
        ibi.imiterere = ImiterereIkoresho.KUREMWE
        ibi.ibiranga = set()
        ibi.imiterereshingiro = ImiterereshingiroIkoresho()
        ibi.abana = []
        ibi.umubyeyi = None
        ibi.amakuru = {}
        ibi.ibikorwa = {}

    def kongera(ibi: "Ikoresho", umwana: "Ikoresho") -> "Ikoresho":
        """Kongera umwana.

        Arguments:
            umwana: Ikoresho kizaba umwana

        Returns:
            Ikoresho: ibi (chain)
        """
        ibi.abana.append(umwana)
        umwana.umubyeyi = ibi
        return ibi

    def kuraho(ibi: "Ikoresho", umwana: "Ikoresho") -> None:
        """Kuraho umwana."""
        if umwana in ibi.abana:
            ibi.abana.remove(umwana)
            umwana.umubyeyi = None

    def shaka_kubw_indangamuntu(ibi: "Ikoresho", indangamuntu: str) -> Optional["Ikoresho"]:
        """Shaka igikoresho ukoresheje indangamuntu.

        Arguments:
            indangamuntu: Indangamuntu y'igikoresho

        Returns:
            Optional[Ikoresho]: Igikoresho cyangwa None
        """
        for umwana in ibi.abana:
            if umwana.indangamuntu == indangamuntu:
                return umwana
            if umwana.abana:
                igisubizo = umwana.shaka_kubw_indangamuntu(indangamuntu)
                if igisubizo:
                    return igisubizo
        return None

    def shira_ikiranga(ibi: "Ikoresho", ikiranga: IkirangaIkoresho) -> None:
        """Shira ikiranga kuri iki gikoresho."""
        ibi.ibiranga.add(ikiranga)

    def kuraho_ikiranga(ibi: "Ikoresho", ikiranga: IkirangaIkoresho) -> None:
        """Kuraho ikiranga."""
        ibi.ibiranga.discard(ikiranga)

    def afite_ikiranga(ibi: "Ikoresho", ikiranga: IkirangaIkoresho) -> bool:
        """Ese igikoresho gifite iki kiranga?"""
        return ikiranga in ibi.ibiranga

    def shira_ikintu(ibi: "Ikoresho", ubwoko: str, umuyoboro: Callable[..., Any]) -> None:
        """Shira ikintu (event handler)."""
        ibi.ibikorwa[ubwoko] = umuyoboro

    def tereza(ibi: "Ikoresho", ubwoko: str, **amakuru: Any) -> None:
        """Tereza ikintu (event).

        Arguments:
            ubwoko: Ubwoko bw'ikintu
            **amakuru: Amakuru y'ikintu
        """
        umuyoboro = ibi.ibikorwa.get(ubwoko)
        if umuyoboro:
            umuyoboro(**amakuru)

    def shira_muri_amakuru(ibi: "Ikoresho", urufunguzo: str, agaciro: Any) -> None:
        """Shira agaciro mu makuru."""
        ibi.amakuru[urufunguzo] = agaciro

    def shaka_muri_amakuru(ibi: "Ikoresho", urufunguzo: str, mburabura: Any = None) -> Any:
        """Shaka agaciro mu makuru."""
        return ibi.amakuru.get(urufunguzo, mburabura)
