"""Buto — Ibikoresho bya buto.

Iki modulu gikubiyemo buto, buto gucunga,
buto radiyo, n'agakobisi.
"""

from __future__ import annotations

from typing import Optional, Callable, Any

from ibiro.ibikoresho.ikoresho import Ikoresho, IkirangaIkoresho


class Buto(Ikoresho):
    """Buto — Igikoresho cyo gukanda.

    Buto ni igikoresho gikoreshwa mugukora igikorwa
    iyo cyakanishije.
    """

    inyandiko: str
    rikora: Optional[Callable[..., Any]]

    def __init__(
        ibi: "Buto",
        inyandiko: str,
        indangamuntu: str = "",
        rikora: Optional[Callable[..., Any]] = None,
    ) -> None:
        indangamuntu_ya = indangamuntu or f"buto_{inyandiko[:8]}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko
        ibi.rikora = rikora
        ibi.shira_ikintu("gukanda", ibi.gukanda)

    def gukanda(ibi: "Buto", **amakuru: Any) -> None:
        """Gukanda kuri buto.

        Iyi methodo ikora iyo buto ikanishije.
        """
        if ibi.rikora:
            ibi.rikora(**amakuru)

    def basha(ibi: "Buto") -> None:
        """Basha buto."""
        ibi.kuraho_ikiranga(IkirangaIkoresho.NTIBISHOBOKA)

    def basha_ntibishoboka(ibi: "Buto") -> None:
        """Basha buto ntishoboka."""
        ibi.shira_ikiranga(IkirangaIkoresho.NTIBISHOBOKA)


class ButoGucunga(Ikoresho):
    """Buto Gucunga — Buto ifite imiterere ya toggle.

    Iyi buto ihindura imiterere yayo iyo ikanishije.
    Ishobora kuba iri ku mwanya cyangwa iri hasi.
    """

    inyandiko: str
    iri_ku_mwanya: bool

    def __init__(
        ibi: "ButoGucunga",
        inyandiko: str,
        indangamuntu: str = "",
        iri_ku_mwanya: bool = False,
    ) -> None:
        indangamuntu_ya = indangamuntu or f"gucunga_{inyandiko[:8]}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko
        ibi.iri_ku_mwanya = iri_ku_mwanya

    def gucunga(ibi: "ButoGucunga") -> None:
        """Gucunga imiterere ya toggle."""
        ibi.iri_ku_mwanya = not ibi.iri_ku_mwanya

    @property
    def toggled(ibi: "ButoGucunga") -> bool:
        """Ese buto iri ku mwanya?"""
        return ibi.iri_ku_mwanya


class ButoRadiyo(Ikoresho):
    """Buto Radiyo — Buto ya radiyo.

    Muri itsinda, buto imwe gusa ishobora guhitamo.
    """

    inyandiko: str
    ihitamo: bool
    itsinda: str

    def __init__(
        ibi: "ButoRadiyo",
        inyandiko: str,
        indangamuntu: str = "",
        ihitamo: bool = False,
        itsinda: str = "mburabura",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"radiyo_{inyandiko[:8]}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko
        ibi.ihitamo = ihitamo
        ibi.itsinda = itsinda
        if ihitamo:
            ibi.shira_ikiranga(IkirangaIkoresho.IHITAMO)

    @property
    def yahitamo(ibi: "ButoRadiyo") -> bool:
        """Ese buto radiyo yarahitamo?"""
        return ibi.ihitamo

    def hitamo(ibi: "ButoRadiyo") -> None:
        """Hitamo iyi buto radiyo."""
        ibi.ihitamo = True
        ibi.shira_ikiranga(IkirangaIkoresho.IHITAMO)

    def kuraho_ihitamo(ibi: "ButoRadiyo") -> None:
        """Kuraho ihitamo."""
        ibi.ihitamo = False
        ibi.kuraho_ikiranga(IkirangaIkoresho.IHITAMO)


class Akabokisi(Ikoresho):
    """Akabokisi — Igikoresho cyo guhitamo (checkbox).

    Akabokisi gakoreshwa muguhitamo ibintu byinshi.
    Gashobora kuba gafite ikimenyetso cyangwa nta cyo gifite.
    """

    inyandiko: str
    ikemye: bool

    def __init__(
        ibi: "Akabokisi",
        inyandiko: str,
        indangamuntu: str = "",
        ikemye: bool = False,
    ) -> None:
        indangamuntu_ya = indangamuntu or f"akabokisi_{inyandiko[:8]}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko
        ibi.ikemye = ikemye

    def gucunga(ibi: "Akabokisi") -> None:
        """Gucunga akabokisi."""
        ibi.ikemye = not ibi.ikemye

    @property
    def yikemye(ibi: "Akabokisi") -> bool:
        """Ese akabokisi gafite ikimenyetso?"""
        return ibi.ikemye
