"""Inyandiko — Ibikoresho byo kwinjiza inyandiko.

Iki modulu gikubiyemo inyandiko, ikibanza inyandiko,
inyandiko ibanga, inyandiko gushaka, n'umubare.
"""

from __future__ import annotations

from typing import Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class Inyandiko(Ikoresho):
    """Inyandiko — Igikoresho cyo kwinjiza inyandiko.

    Inyandiko ni igikoresho cya texte cyo kwinjiza
    inyandiko nkeyi.
    """

    agaciro: str
    ikimenyetso: str

    def __init__(
        ibi: "Inyandiko",
        indangamuntu: str = "",
        agaciro: str = "",
        ikimenyetso: str = "",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"inyandiko_{len(indangamuntu)}"
        super().__init__(indangamuntu_ya)
        ibi.agaciro = agaciro
        ibi.ikimenyetso = ikimenyetso


class IkibanzaInyandiko(Ikoresho):
    """Ikibanza Inyandiko — Igikoresho cyo kwinjiza inyandiko nyinshi.

    Ikibanza inyandiko ni igikoresho cya texte cyo kwinjiza
    inyandiko nyinshi (textarea).
    """

    agaciro: str

    def __init__(
        ibi: "IkibanzaInyandiko",
        indangamuntu: str = "",
        agaciro: str = "",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"ikibanza_inyandiko_{len(indangamuntu)}"
        super().__init__(indangamuntu_ya)
        ibi.agaciro = agaciro


class InyandikoIbanga(Ikoresho):
    """Inyandiko Ibanga — Igikoresho cyo kwinjiza ibanga.

    Inyandiko ibanga ikoreshwa mugushyiraho
    amagambo y'ibanga (password).
    """

    agaciro: str

    def __init__(
        ibi: "InyandikoIbanga",
        indangamuntu: str = "",
        agaciro: str = "",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"ibanga_{len(indangamuntu)}"
        super().__init__(indangamuntu_ya)
        ibi.agaciro = agaciro


class InyandikoGushaka(Ikoresho):
    """Inyandiko Gushaka — Igikoresho cyo gushaka.

    Inyandiko gushaka ikoreshwa mugushaka
    amakuru muri porogaramu.
    """

    agaciro: str

    def __init__(
        ibi: "InyandikoGushaka",
        indangamuntu: str = "",
        agaciro: str = "",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"gushaka_{len(indangamuntu)}"
        super().__init__(indangamuntu_ya)
        ibi.agaciro = agaciro


class Umubare(Ikoresho):
    """Umubare — Igikoresho cyo kwinjiza umubare.

    Umubare ni igikoresho cyo kwinjiza
    umubare (number input).
    """

    agaciro: float
    ntoya: float
    nini: float

    def __init__(
        ibi: "Umubare",
        indangamuntu: str = "",
        agaciro: float = 0.0,
        ntoya: float = float("-inf"),
        nini: float = float("inf"),
    ) -> None:
        indangamuntu_ya = indangamuntu or f"umubare_{len(indangamuntu)}"
        super().__init__(indangamuntu_ya)
        ibi.agaciro = agaciro
        ibi.ntoya = ntoya
        ibi.nini = nini
