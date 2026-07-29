"""Gupakira — Hot reloader."""

from __future__ import annotations

from typing import Set, Callable, Any
import os
import time


class Gupakira:
    """Gupakira — Hot reloader.

    Gupakira gicunga amadosiye ya porogaramu
    maze igihe ahindutse igasubiramo porogaramu.
    """

    _amadosiye: Set[str]
    _ibihe: dict
    _iruka: bool
    _ku_mpinduka: Callable[..., Any]

    def __init__(ibi: "Gupakira", ku_mpinduka: Callable[..., Any] = None):
        ibi._amadosiye = set()
        ibi._ibihe = {}
        ibi._iruka = False
        ibi._ku_mpinduka = ku_mpinduka or (lambda **kw: None)

    def kongera_dosiye(ibi: "Gupakira", inzira: str):
        """Kongera dosiye yo kureba."""
        ibi._amadosiye.add(inzira)
        if os.path.exists(inzira):
            ibi._ibihe[inzira] = os.path.getmtime(inzira)

    def tangiza(ibi: "Gupakira"):
        """Tangiza gupakira (hot reload)."""
        ibi._iruka = True

    def kureka(ibi: "Gupakira"):
        """Kureka gupakira."""
        ibi._iruka = False

    def reba(ibi: "Gupakira"):
        """Reba niba amadosiye yahindutse."""
        if not ibi._iruka:
            return
        for inzira in ibi._amadosiye:
            if os.path.exists(inzira):
                igihe = os.path.getmtime(inzira)
                if inzira in ibi._ibihe and ibi._ibihe[inzira] != igihe:
                    ibi._ibihe[inzira] = igihe
                    ibi._ku_mpinduka(inzira=inzira)
