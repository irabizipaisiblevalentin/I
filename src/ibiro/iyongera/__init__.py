"""Iyongera — Iyongera rya porogaramu (plugins).

Iki modulu gikubiyemo uburyo bwo kongera
ibintu mu IBIRO ukoresheje plugin system.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any


class Iyongera(ABC):
    """Iyongera — Plugin base class."""

    izina: str
    verisiyo: str

    def __init__(ibi: "Iyongera", izina: str = "", verisiyo: str = "0.1.0"):
        ibi.izina = izina
        ibi.verisiyo = verisiyo

    @abstractmethod
    def tangiza(ibi) -> bool:
        """Tangiza iyongera."""
        ...

    @abstractmethod
    def gupakira(ibi) -> bool:
        """Gupakira iyongera."""
        ...


class IyongeraPorogaramu(Iyongera):
    """Iyongera Porogaramu — App plugin."""

    def tangiza(ibi) -> bool:
        return True

    def gupakira(ibi) -> bool:
        return True


class IyongeraIngingo(Iyongera):
    """Iyongera Ingingo — Theme plugin."""

    amabara: Dict[str, str]

    def __init__(ibi: "IyongeraIngingo", izina: str = "", verisiyo: str = "0.1.0", amabara: Dict[str, str] = None):
        super().__init__(izina, verisiyo)
        ibi.amabara = amabara or {}

    def tangiza(ibi) -> bool:
        return True

    def gupakira(ibi) -> bool:
        return True


class IyongeraIkoresho(Iyongera):
    """Iyongera Ikoresho — Widget plugin."""

    def tangiza(ibi) -> bool:
        return True

    def gupakira(ibi) -> bool:
        return True


class IyongeraUrurimi(Iyongera):
    """Iyongera Ururimi — Language pack."""

    ururimi: str
    amagambo: Dict[str, str]

    def __init__(ibi: "IyongeraUrurimi", izina: str = "", verisiyo: str = "0.1.0", ururimi: str = "", amagambo: Dict[str, str] = None):
        super().__init__(izina, verisiyo)
        ibi.ururimi = ururimi
        ibi.amagambo = amagambo or {}

    def tangiza(ibi) -> bool:
        return True

    def gupakira(ibi) -> bool:
        return True
