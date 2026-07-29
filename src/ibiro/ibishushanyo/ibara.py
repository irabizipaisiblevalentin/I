"""Ibara — Icungamiterere ry'ibara."""

from __future__ import annotations

from typing import Tuple


class Ibara:
    """Ibara — Igikoresho cy'ibara.

    Ibara rikoreshwa mugushyiraho amabara
    mu bikoresho byose bya IBIRO.
    """

    r: int
    g: int
    b: int
    a: int

    def __init__(ibi: "Ibara", r: int = 0, g: int = 0, b: int = 0, a: int = 255):
        ibi.r = max(0, min(255, r))
        ibi.g = max(0, min(255, g))
        ibi.b = max(0, min(255, b))
        ibi.a = max(0, min(255, a))

    @classmethod
    def kuva_hex(cls, hex_ibara: str) -> "Ibara":
        """Kora ibara ukoresheje hexadecimal string."""
        hex_ibara = hex_ibara.lstrip("#")
        if len(hex_ibara) == 3:
            hex_ibara = "".join(c * 2 for c in hex_ibara)
        if len(hex_ibara) == 6:
            r, g, b = int(hex_ibara[0:2], 16), int(hex_ibara[2:4], 16), int(hex_ibara[4:6], 16)
            return cls(r, g, b)
        elif len(hex_ibara) == 8:
            r, g, b, a = int(hex_ibara[0:2], 16), int(hex_ibara[2:4], 16), int(hex_ibara[4:6], 16), int(hex_ibara[6:8], 16)
            return cls(r, g, b, a)
        return cls(0, 0, 0)

    @classmethod
    def kuva_rgb(cls, r: int, g: int, b: int) -> "Ibara":
        return cls(r, g, b)

    @classmethod
    def kuva_hsl(cls, h: float, s: float, l: float) -> "Ibara":
        """Kora ibara ukoresheje HSL values."""
        s /= 100
        l /= 100
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return cls(int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

    def kuri_hex(ibi: "Ibara") -> str:
        """Hindura ibara kuri hex string."""
        return f"#{ibi.r:02x}{ibi.g:02x}{ibi.b:02x}"

    def kuri_tuple(ibi: "Ibara") -> Tuple[int, int, int]:
        return (ibi.r, ibi.g, ibi.b)

    def kuri_tuple_rgba(ibi: "Ibara") -> Tuple[int, int, int, int]:
        return (ibi.r, ibi.g, ibi.b, ibi.a)


class Amabara:
    """Amabara — Amabara y'ibanze y'IBIRO."""

    CYERA = Ibara.kuva_hex("#ffffff")
    UMUKARA = Ibara.kuva_hex("#000000")
    UMUTUKU = Ibara.kuva_hex("#ff0000")
    UBURURU = Ibara.kuva_hex("#0000ff")
    ICYATSI = Ibara.kuva_hex("#00ff00")
    UMUHABURA = Ibara.kuva_hex("#ffff00")
    UKIBONDO = Ibara.kuva_hex("#00ffff")
    MAGENTA = Ibara.kuva_hex("#ff00ff")
    IMYEYERE = Ibara.kuva_hex("#00000000",)
    IMWERU = Ibara.kuva_hex("#808080")
    IKIGINA = Ibara.kuva_hex("#800000")
    IBIHIHI = Ibara.kuva_hex("#008000")
    UMUKOBE = Ibara.kuva_hex("#000080")
    UMUSAYA = Ibara.kuva_hex("#ffa500"),
    UMUTUKU_UMUKOBE = Ibara.kuva_hex("#800080")
