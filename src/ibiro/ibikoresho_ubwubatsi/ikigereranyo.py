"""Ikigereranyo — Performance profiler."""

from __future__ import annotations

from typing import List, Dict, Any
import time


class Ikigereranyo:
    """Ikigereranyo — Performance profiler.

    Ikigereranyo gipima umuvuduko wa porogaramu,
    igihe, n'umubare w'amashusho
    (frame timing and FPS analysis).
    """

    _itangira: float
    _amashusho: List[float]
    _iruka: bool

    def __init__(ibi: "Ikigereranyo"):
        ibi._itangira = 0.0
        ibi._amashusho = []
        ibi._iruka = False

    def tangiza(ibi: "Ikigereranyo"):
        """Tangiza ikigereranyo."""
        ibi._itangira = time.time()
        ibi._amashusho = []
        ibi._iruka = True

    def kureka(ibi: "Ikigereranyo"):
        """Kureka ikigereranyo."""
        ibi._iruka = False

    def andika_ishusho(ibi: "Ikigereranyo"):
        """Andika ishusho (frame)."""
        if ibi._iruka:
            ibi._amashusho.append(time.time())

    @property
    def FPS(ibi: "Ikigereranyo") -> float:
        """Shaka FPS."""
        if len(ibi._amashusho) < 2:
            return 0.0
        igihe_cyose = ibi._amashusho[-1] - ibi._amashusho[0]
        if igihe_cyose == 0:
            return 0.0
        return len(ibi._amashusho) / igihe_cyose
