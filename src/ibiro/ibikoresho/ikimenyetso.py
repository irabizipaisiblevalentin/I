"""Ikimenyetso — Ibikoresho by'ikimenyetso.

Iki modulu gikubiyemo ikimenyetso, umutwe,
paragarafu, n'ihuza.
"""

from __future__ import annotations

from typing import Optional

from ibiro.ibikoresho.ikoresho import Ikoresho


class Ikimenyetso(Ikoresho):
    """Ikimenyetso — Igikoresho cyo kwerekana inyandiko.

    Ikimenyetso kigaragaza inyandiko ku rwego rwa desktop.
    Gikoreshwa mugushyiraho amagambo, utumenyetso, n'ibindi.
    """

    inyandiko: str

    def __init__(
        ibi: "Ikimenyetso",
        inyandiko: str = "",
        indangamuntu: str = "",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"ikimenyetso_{len(inyandiko)}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko


class Umutwe(Ikoresho):
    """Umutwe — Ikimenyetso gikomeye (heading).

    Umutwe ni ikimenyetso gifite inyandiko nini
    ikoreshwa nk'umutwe w'igice cyangwa urupapuro.
    """

    inyandiko: str
    urwego: int

    def __init__(
        ibi: "Umutwe",
        inyandiko: str = "",
        indangamuntu: str = "",
        urwego: int = 1,
    ) -> None:
        indangamuntu_ya = indangamuntu or f"umutwe_{urwego}_{len(inyandiko)}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko
        ibi.urwego = urwego


class Paragarafu(Ikoresho):
    """Paragarafu — Ikimenyetso cya paragarafu.

    Paragarafu ikoreshwa mugushyiraho inyandiko ndende.
    """

    inyandiko: str

    def __init__(
        ibi: "Paragarafu",
        inyandiko: str = "",
        indangamuntu: str = "",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"paragarafu_{len(inyandiko)}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko


class Ihuza(Ikoresho):
    """Ihuza — Ikimenyetso gifite ihuza (link).

    Ihuza rikoreshwa mugushyiraho linki
    ijyana ahantu hatandukanye.
    """

    inyandiko: str
    inzira: str

    def __init__(
        ibi: "Ihuza",
        inyandiko: str = "",
        inzira: str = "",
        indangamuntu: str = "",
    ) -> None:
        indangamuntu_ya = indangamuntu or f"ihuza_{len(inyandiko)}"
        super().__init__(indangamuntu_ya)
        ibi.inyandiko = inyandiko
        ibi.inzira = inzira

    def kanda(ibi: "Ihuza") -> None:
        """Kanda kuri ihuza."""
        ibi.tereza("gukanda", inzira=ibi.inzira)
