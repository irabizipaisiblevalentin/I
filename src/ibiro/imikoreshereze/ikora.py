"""Ikora — Reactive state management."""

from __future__ import annotations

from typing import List, Callable, Any, Optional, Generic, TypeVar

T = TypeVar("T")


class Ikora(Generic[T]):
    """Ikora — Reactive property.

    Iyi property iha abasirikare amenyekanisha
    iyo agaciro kahindutse.
    """

    _agaciro: T
    _abasirikare: List[Callable[[T], None]]

    def __init__(ibi: "Ikora", agaciro: T):
        ibi._agaciro = agaciro
        ibi._abasirikare = []

    @property
    def agaciro(ibi: "Ikora") -> T:
        return ibi._agaciro

    @agaciro.setter
    def agaciro(ibi: "Ikora", agaciro_nshya: T):
        ibi._agaciro = agaciro_nshya
        ibi._menyesha()

    def ku_mpinduka(ibi: "Ikora", umusirikare: Callable[[T], None]):
        """Shira umusirikare uzabona impinduka."""
        ibi._abasirikare.append(umusirikare)

    def _menyesha(ibi: "Ikora"):
        for umusirikare in ibi._abasirikare:
            umusirikare(ibi._agaciro)


class Ibaze(Generic[T]):
    """Ibaze — Computed property.

    Iyi property ibarwa ukoresheje izindi property.
    """

    _ibarwa: Callable[[], T]
    _agaciro: T

    def __init__(ibi: "Ibaze", ibarwa: Callable[[], T], ibikorwa: List[Ikora] = None):
        ibi._ibarwa = ibarwa
        ibi._agaciro = ibarwa()
        if ibikorwa:
            for ikora in ibikorwa:
                ikora.ku_mpinduka(lambda _: ibi._subiramo())

    @property
    def agaciro(ibi: "Ibaze") -> T:
        return ibi._agaciro

    def _subiramo(ibi: "Ibaze"):
        ibi._agaciro = ibi._ibarwa()


class Icyegeranyo(Generic[T]):
    """Icyegeranyo — Observable collection."""

    _ibintu: List[T]
    _abasirikare: List[Callable[[List[T]], None]]

    def __init__(ibi: "Icyegeranyo", ibintu: List[T] = None):
        ibi._ibintu = list(ibintu) if ibintu else []
        ibi._abasirikare = []

    def kongera(ibi: "Icyegeranyo", ikintu: T):
        ibi._ibintu.append(ikintu)
        ibi._menyesha()

    def kuraho(ibi: "Icyegeranyo", ikintu: T):
        if ikintu in ibi._ibintu:
            ibi._ibintu.remove(ikintu)
            ibi._menyesha()

    @property
    def byose(ibi: "Icyegeranyo") -> List[T]:
        return list(ibi._ibintu)

    def __len__(ibi: "Icyegeranyo") -> int:
        return len(ibi._ibintu)

    def __iter__(ibi: "Icyegeranyo"):
        return iter(ibi._ibintu)

    def _menyesha(ibi: "Icyegeranyo"):
        for umusirikare in ibi._abasirikare:
            umusirikare(ibi._ibintu)
