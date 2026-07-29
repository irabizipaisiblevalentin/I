"""Shingiro ry'urwego — Platform backend base."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Optional


class Inyuma(ABC):
    """Inyuma — Platform backend abstract.

    Iki ni cyo shingiro cy'inyuma ya porogaramu
    (abstract base class for platform backends).
    """

    @abstractmethod
    def inyuma_urwego(ibi) -> str:
        """Shaka izina ry'inyuma."""
        ...

    @abstractmethod
    def ingano_ikiganiro(ibi) -> Tuple[int, int]:
        """Shaka ingano y'ikiganiro (screen size)."""
        ...

    @abstractmethod
    def shaka_muri_duporo(ibi) -> Optional[str]:
        """Shaka amakuru mu dupuro (clipboard)."""
        ...

    @abstractmethod
    def shira_muri_duporo(ibi, inyandiko: str) -> bool:
        """Shira amakuru mu dupuro."""
        ...

    @abstractmethod
    def menyesha(ibi, umutwe: str, inyandiko: str) -> bool:
        """Tanga imenyekanisha."""
        ...

    @abstractmethod
    def wiga_urwego(ibi) -> str:
        """Shaka izina ry'urwego."""
        ...

    def tangiza(ibi, **igenamiterere) -> bool:
        """Tangiza inyuma — start the platform backend.

        Iyi methodo itangiza inyuma ya porogaramu
        (seriveri HTTP, mainloop, etc.).

        Arguments:
            **igenamiterere: Igenamiterere ry'itangizwa

        Returns:
            bool: True niba byagenze neza
        """
        return True

    def rirarika(ibi) -> int:
        """Rirarika mainloop.

        Iyi methodo ikora mainloop ya porogaramu
        kugeza igihe cyo guhagarika.

        Returns:
            int: Kode y'isohoka (0 = neza)
        """
        return 0

    def hagarika(ibi) -> None:
        """Hagarika inyuma — stop the platform backend."""
        pass
