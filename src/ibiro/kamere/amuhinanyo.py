"""Amuhinanyo — Keyboard shortcuts."""

from __future__ import annotations

from typing import List, Dict, Optional, Callable, Any


class Muhinanyo:
    """Muhinanyo — Keyboard shortcut."""

    amabuto: str
    indangamuntu_igikorwa: str
    rikora: Optional[Callable[..., Any]]

    def __init__(ibi: "Muhinanyo", amabuto: str, indangamuntu_igikorwa: str = "", rikora: Optional[Callable[..., Any]] = None):
        ibi.amabuto = amabuto
        ibi.indangamuntu_igikorwa = indangamuntu_igikorwa
        ibi.rikora = rikora


class UyoboreAmuhinanyo:
    """Uyobore Amuhinanyo — Shortcut manager."""

    _amuhinanyo: Dict[str, Muhinanyo]

    def __init__(ibi: "UyoboreAmuhinanyo"):
        ibi._amuhinanyo = {}

    def yandika(ibi: "UyoboreAmuhinanyo", muhinanyo: Muhinanyo):
        """Yandika muhinanyo mushya."""
        ibi._amuhinanyo[muhinanyo.indangamuntu_igikorwa] = muhinanyo

    def kuraho(ibi: "UyoboreAmuhinanyo", indangamuntu_igikorwa: str):
        """Kuraho muhinanyo."""
        if indangamuntu_igikorwa in ibi._amuhinanyo:
            del ibi._amuhinanyo[indangamuntu_igikorwa]

    def byose(ibi: "UyoboreAmuhinanyo") -> List[Muhinanyo]:
        """Shaka amuhinanyo yose."""
        return list(ibi._amuhinanyo.values())
