"""Ububiko — Application store."""

from __future__ import annotations

from typing import Dict, Any, Optional


class UbubikoPorogaramu:
    """Ububiko Porogaramu — Application store.

    Ububiko ni ahantu hamwe ha bikwa amakuru
    ya porogaramu yose.
    """

    _amakuru: Dict[str, Any]

    def __init__(ibi: "UbubikoPorogaramu"):
        ibi._amakuru = {}

    def shira(ibi: "UbubikoPorogaramu", urufunguzo: str, agaciro: Any):
        """Shira agaciro mu bubiko."""
        ibi._amakuru[urufunguzo] = agaciro

    def shaka(ibi: "UbubikoPorogaramu", urufunguzo: str, mburabura: Any = None) -> Any:
        """Shaka agaciro mu bubiko."""
        return ibi._amakuru.get(urufunguzo, mburabura)

    def afite(ibi: "UbubikoPorogaramu", urufunguzo: str) -> bool:
        """Ese urufunguzo rubaho?"""
        return urufunguzo in ibi._amakuru

    def kuraho(ibi: "UbubikoPorogaramu", urufunguzo: str):
        """Kuraho agaciro."""
        if urufunguzo in ibi._amakuru:
            del ibi._amakuru[urufunguzo]

    def kira(ibi: "UbubikoPorogaramu"):
        """Kira ububiko."""
        ibi._amakuru.clear()

    @property
    def byose(ibi: "UbubikoPorogaramu") -> Dict[str, Any]:
        """Shaka amakuru yose."""
        return dict(ibi._amakuru)
