"""Guhuza — Binding state management."""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Callable, Optional

from ibiro.imikoreshereze.ikora import Ikora


class UburyoGuhuza(Enum):
    """Uburyo bwo guhuza (binding mode)."""
    INZIRA_IMWE = auto()
    INZIRA_EKUBILI = auto()
    INSHA_IMWE = auto()


class Guhuza:
    """Guhuza — Binding between properties.

    Guhuza guhuza property ebyiri kugirango
    impinduka imwe igire izindi.
    """

    inkomoko: Ikora
    iyihererezo: Ikora
    uburyo: UburyoGuhuza
    hindura: Optional[Callable[[Any], Any]]

    def __init__(
        ibi: "Guhuza",
        inkomoko: Ikora,
        iyihererezo: Ikora,
        uburyo: UburyoGuhuza = UburyoGuhuza.INZIRA_IMWE,
        hindura: Optional[Callable[[Any], Any]] = None,
    ):
        ibi.inkomoko = inkomoko
        ibi.iyihererezo = iyihererezo
        ibi.uburyo = uburyo
        ibi.hindura = hindura

    def ghuza(ibi: "Guhuza"):
        """Ghuza agaciro k'inkomoko kuri iyihererezo."""
        agaciro = ibi.inkomoko.agaciro
        if ibi.hindura:
            agaciro = ibi.hindura(agaciro)
        ibi.iyihererezo.agaciro = agaciro

    def _ku_mpinduka_inkomoko(ibi: "Guhuza", agaciro: Any):
        agaciro_hinduwe = ibi.hindura(agaciro) if ibi.hindura else agaciro
        ibi.iyihererezo.agaciro = agaciro_hinduwe

    def _ku_mpinduka_iyihererezo(ibi: "Guhuza", agaciro: Any):
        ibi.inkomoko.agaciro = agaciro

    @property
    def run(ibi: "Guhuza") -> "Guhuza":
        """Tangiza guhuza."""
        ibi.ghuza()
        ibi.inkomoko.ku_mpinduka(ibi._ku_mpinduka_inkomoko)
        if ibi.uburyo == UburyoGuhuza.INZIRA_EKUBILI:
            ibi.iyihererezo.ku_mpinduka(ibi._ku_mpinduka_iyihererezo)
        return ibi


class Uhuza:
    """Uhuza — Binder (manager of bindings)."""

    _guhuza_byose: list

    def __init__(ibi: "Uhuza"):
        ibi._guhuza_byose = []

    def huza(ibi: "Uhuza", inkomoko: Ikora, iyihererezo: Ikora, uburyo: UburyoGuhuza = UburyoGuhuza.INZIRA_IMWE, hindura: Callable = None) -> Guhuza:
        """Huuza property ebyiri."""
        guhuza = Guhuza(inkomoko, iyihererezo, uburyo, hindura)
        ibi._guhuza_byose.append(guhuza)
        return guhuza
