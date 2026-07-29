"""Ikiganiro — Ibikoresho by'ikiganiro (dialog).

Iki modulu gikubiyemo ikiganiro, ikiganiro butumwa,
ikiganiro dosiye, n'ikiganiro ibara.
"""

from __future__ import annotations

from typing import Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class Ikiganiro(Ikoresho):
    """Ikiganiro — Igikoresho cya dialog."""

    umutwe: str
    inyandiko: str
    ubugari: int
    uburebure: int

    def __init__(
        ibi: "Ikiganiro",
        umutwe: str = "",
        inyandiko: str = "",
        indangamuntu: str = "",
        ubugari: int = 400,
        uburebure: int = 300,
    ):
        indangamuntu_ya = indangamuntu or f"ikiganiro_{len(umutwe)}"
        super().__init__(indangamuntu_ya)
        ibi.umutwe = umutwe
        ibi.inyandiko = inyandiko
        ibi.ubugari = ubugari
        ibi.uburebure = uburebure


class IkiganiroButumwa(Ikiganiro):
    """Ikiganiro Butumwa — Dialog y'ubutumwa."""

    urwego: str  # amakuru, ikosa, iburira, intsinzi

    def __init__(
        ibi: "IkiganiroButumwa",
        umutwe: str = "",
        inyandiko: str = "",
        urwego: str = "amakuru",
        indangamuntu: str = "",
    ):
        super().__init__(umutwe=umutwe, inyandiko=inyandiko, indangamuntu=indangamuntu, ubugari=350, uburebure=200)
        ibi.urwego = urwego


class IkiganiroDosiye(Ikiganiro):
    """Ikiganiro Dosiye — Dialog yo guhitamo dosiye."""

    ubwoko: str  # gufungura, kubika
    icyunguruzo: str

    def __init__(
        ibi: "IkiganiroDosiye",
        ubwoko: str = "gufungura",
        icyunguruzo: str = "",
        indangamuntu: str = "",
    ):
        super().__init__(umutwe="Hitamo Dosiye", indangamuntu=indangamuntu, ubugari=600, uburebure=400)
        ibi.ubwoko = ubwoko
        ibi.icyunguruzo = icyunguruzo


class IkiganiroIbara(Ikiganiro):
    """Ikiganiro Ibara — Dialog yo guhitamo ibara."""

    ibara: str

    def __init__(ibi: "IkiganiroIbara", indangamuntu: str = ""):
        super().__init__(umutwe="Hitamo Ibara", indangamuntu=indangamuntu, ubugari=500, uburebure=400)
        ibi.ibara = "#ffffff"
