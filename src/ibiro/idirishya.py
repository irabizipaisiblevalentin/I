"""Idirishya — Icungamiterere ry'amadirishya.

Iki modulu gikubiyemo ibintu byose bijyanye n'amadirishya:
imiterere, uburyo, n'ubuyobozii.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ibiro.ibikoresho.ikoresho import Ikoresho


class ImiterereIdirishya(Enum):
    """Imiterere y'idirishya."""
    KUREMWE = auto()
    KWEREKANWE = auto()
    HISHWE = auto()
    KININIWE = auto()
    KIGABANYIJWE = auto()
    FUNGWE = auto()


class UburyoIdirishya(Enum):
    """Uburyo bw'idirishya."""
    GASANZWE = auto()
    IBANZE = auto()
    YUZURA = auto()


class IgenamiterereIdirishya:
    """Igenamiterere ry'idirishya.

    Iri genamiterere ritanga ibiranga byose by'idirishya
    nk'ubugari, uburebure, ibara, n'ibindi.
    """

    umutwe: str
    ubugari: int
    uburebure: int
    hagahinduka: bool
    hagafunga: bool
    hagakinira: bool
    icyerekezo: str
    ibara: str

    def __init__(
        ibi: "IgenamiterereIdirishya",
        umutwe: str = "IBIRO",
        ubugari: int = 800,
        uburebure: int = 600,
        hagahinduka: bool = True,
        hagafunga: bool = True,
        hagakinira: bool = True,
        icyerekezo: str = "center",
        ibara: str = "#ffffff",
    ) -> None:
        ibi.umutwe = umutwe
        ibi.ubugari = ubugari
        ibi.uburebure = uburebure
        ibi.hagahinduka = hagahinduka
        ibi.hagafunga = hagafunga
        ibi.hagakinira = hagakinira
        ibi.icyerekezo = icyerekezo
        ibi.ibara = ibara


class Idirishya:
    """Idirishya nyamukuru.

    Idirishya ni ikintu cy'ibanze mu rugendo rwa porogaramu ya desktop.
    Rifite imiterere, uburyo, abana, n'ibikorwa.
    """

    indangamuntu: str
    igenamiterere: IgenamiterereIdirishya
    imiterere: ImiterereIdirishya
    uburyo: UburyoIdirishya
    abana: List["Idirishya"]
    umubyeyi: Optional["Idirishya"]
    ibintu: Dict[str, object]
    ikoresho_nyamukuru: Optional["Ikoresho"]

    def __init__(
        ibi: "Idirishya",
        indangamuntu: str,
        umutwe: str = "IBIRO",
        ubugari: int = 800,
        uburebure: int = 600,
    ) -> None:
        ibi.indangamuntu = indangamuntu
        ibi.igenamiterere = IgenamiterereIdirishya(
            umutwe=umutwe, ubugari=ubugari, uburebure=uburebure
        )
        ibi.imiterere = ImiterereIdirishya.KUREMWE
        ibi.uburyo = UburyoIdirishya.GASANZWE
        ibi.abana = []
        ibi.umubyeyi = None
        ibi.ibintu = {}
        ibi.ikoresho_nyamukuru = None

    @property
    def kaboneka(ibi: "Idirishya") -> bool:
        """Ese idirishya riraboneka?"""
        return ibi.imiterere == ImiterereIdirishya.KWEREKANWE

    def kwerekana(ibi: "Idirishya") -> "Idirishya":
        """Kwerekana idirishya."""
        ibi.imiterere = ImiterereIdirishya.KWEREKANWE
        return ibi

    def guhisha(ibi: "Idirishya") -> None:
        """Guhisha idirishya."""
        ibi.imiterere = ImiterereIdirishya.HISHWE

    def kingura(ibi: "Idirishya") -> None:
        """Kingura idirishya (fullscreen)."""
        ibi.uburyo = UburyoIdirishya.YUZURA

    def gabanura(ibi: "Idirishya") -> None:
        """Gabanura idirishya."""
        ibi.uburyo = UburyoIdirishya.GASANZWE

    def funga(ibi: "Idirishya") -> None:
        """Funga idirishya."""
        ibi.imiterere = ImiterereIdirishya.FUNGWE
        ibi.abana = []
        ibi.ibintu = {}

    def shyira_ikoresho_nyamukuru(ibi: "Idirishya", ikoresho: "Ikoresho") -> None:
        """Shyira igikoresho nyamukuru muri idirishya."""
        ibi.ikoresho_nyamukuru = ikoresho

    def shyira_umwana(ibi: "Idirishya", umwana: "Idirishya") -> "Idirishya":
        """Shyira idirishya nk'umwana.

        Arguments:
            umwana: Idirishya rizaba umwana

        Returns:
            Idirishya: Ibi (chain)
        """
        ibi.abana.append(umwana)
        umwana.umubyeyi = ibi
        return ibi

    def kuraho_umwana(ibi: "Idirishya", umwana: "Idirishya") -> None:
        """Kuraho umwana."""
        if umwana in ibi.abana:
            ibi.abana.remove(umwana)
            umwana.umubyeyi = None

    def shaka_kubw_indangamuntu(ibi: "Idirishya", indangamuntu: str) -> Optional["Idirishya"]:
        """Shaka idirishya ukoresheje indangamuntu.

        Arguments:
            indangamuntu: Indangamuntu y'idirishya

        Returns:
            Optional[Idirishya]: Idirishya risanzwe cyangwa None
        """
        for umwana in ibi.abana:
            if umwana.indangamuntu == indangamuntu:
                return umwana
            if umwana.abana:
                igisubizo = umwana.shaka_kubw_indangamuntu(indangamuntu)
                if igisubizo:
                    return igisubizo
        return None

    def shyira_ikintu(ibi: "Idirishya", urufunguzo: str, ikintu: object) -> None:
        """Shyira ikintu mu idirishya."""
        ibi.ibintu[urufunguzo] = ikintu

    def ikintu(ibi: "Idirishya", urufunguzo: str, mburabura: object = None) -> object:
        """Shaka ikintu mu idirishya."""
        return ibi.ibintu.get(urufunguzo, mburabura)


class UyoboreIdirishya:
    """Uyobore w'amadirishya.

    Uyu niwe uyobora amadirishya yose ya porogaramu.
    Acunga irema, gufungura, no gufunga amadirishya.
    """

    amadirishya: Dict[str, Idirishya]

    def __init__(ibi: "UyoboreIdirishya") -> None:
        ibi.amadirishya = {}

    def kora_idirishya(ibi: "UyoboreIdirishya", indangamuntu: str, **igenamiterere) -> Idirishya:
        """Kora idirishya rishya.

        Arguments:
            indangamuntu: Indangamuntu ry'idirishya
            **igenamiterere: Igenamiterere ry'idirishya

        Returns:
            Idirishya: Idirishya rishya
        """
        idirishya = Idirishya(indangamuntu, **igenamiterere)
        ibi.amadirishya[indangamuntu] = idirishya
        return idirishya

    def idirishya(ibi: "UyoboreIdirishya", indangamuntu: str) -> Optional[Idirishya]:
        """Shaka idirishya.

        Arguments:
            indangamuntu: Indangamuntu ry'idirishya

        Returns:
            Optional[Idirishya]: Idirishya cyangwa None
        """
        return ibi.amadirishya.get(indangamuntu, None)

    def funga_idirishya(ibi: "UyoboreIdirishya", indangamuntu: str) -> None:
        """Funga idirishya.

        Arguments:
            indangamuntu: Indangamuntu ry'idirishya
        """
        if indangamuntu in ibi.amadirishya:
            ibi.amadirishya[indangamuntu].funga()
            del ibi.amadirishya[indangamuntu]

    def funga_mpine(ibi: "UyoboreIdirishya") -> None:
        """Funga amadirishya yose."""
        for indangamuntu, idirishya in ibi.amadirishya.items():
            idirishya.funga()
        ibi.amadirishya.clear()

    @property
    def umubare(ibi: "UyoboreIdirishya") -> int:
        """Umubare w'amadirishya."""
        return len(ibi.amadirishya)
