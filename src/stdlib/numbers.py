"""numbers — Numeric types, parsing, and conversion for the I language.

Provides integer, float, and rational number operations with safe
overflow handling and parsing utilities.
"""

from __future__ import annotations

import fractions
from typing import Optional, Union


Number = Union[int, float]


# ---------------------------------------------------------------------------
# Type checks
# ---------------------------------------------------------------------------

def is_int(value: object) -> bool:
    """Check if value is an integer."""
    return isinstance(value, int) and not isinstance(value, bool)


def is_float(value: object) -> bool:
    """Check if value is a float."""
    return isinstance(value, float)


def is_number(value: object) -> bool:
    """Check if value is a number (int or float)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_bool(value: object) -> bool:
    """Check if value is a boolean."""
    return isinstance(value, bool)


def is_rational(value: object) -> bool:
    """Check if value is a fractions.Fraction."""
    return isinstance(value, fractions.Fraction)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_int(s: str, base: int = 10) -> int:
    """Parse string to integer. Raises ValueError on failure."""
    return int(s, base)


def parse_float(s: str) -> float:
    """Parse string to float. Raises ValueError on failure."""
    return float(s)


def try_parse_int(s: str, base: int = 10) -> Optional[int]:
    """Parse string to int, return None on failure."""
    try:
        return int(s, base)
    except (ValueError, TypeError):
        return None


def try_parse_float(s: str) -> Optional[float]:
    """Parse string to float, return None on failure."""
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def to_int(value: object, default: int = 0) -> int:
    """Convert value to int. Returns default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value: object, default: float = 0.0) -> float:
    """Convert value to float. Returns default on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def to_rational(numerator: int, denominator: int) -> fractions.Fraction:
    """Create a rational number from numerator and denominator."""
    return fractions.Fraction(numerator, denominator)


# ---------------------------------------------------------------------------
# Rounding and precision
# ---------------------------------------------------------------------------

def snap(value: Number, step: Number) -> Number:
    """Snap value to nearest multiple of step."""
    if step == 0:
        return value
    return round(value / step) * step


def precision(value: float, places: int) -> float:
    """Round to *places* decimal places."""
    if places == 0:
        return float(round(value))
    factor = 10 ** places
    return round(value * factor) / factor


# ---------------------------------------------------------------------------
# Range utilities
# ---------------------------------------------------------------------------

def in_range(value: Number, low: Number, high: Number) -> bool:
    """Return True if low <= value <= high."""
    return low <= value <= high


def clamp(value: Number, low: Number, high: Number) -> Number:
    """Clamp value between low and high."""
    return max(low, min(high, value))


def map_range(
    value: Number,
    from_low: Number,
    from_high: Number,
    to_low: Number,
    to_high: Number,
) -> float:
    """Map value from one range to another."""
    if from_high == from_low:
        return float(to_low)
    t = (value - from_low) / (from_high - from_low)
    return to_low + t * (to_high - to_low)


# ---------------------------------------------------------------------------
# Sign and magnitude
# ---------------------------------------------------------------------------

def sign(x: Number) -> int:
    """Return -1, 0, or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def abs_val(x: Number) -> Number:
    """Absolute value."""
    return abs(x)


def min_of(*args: Number) -> Number:
    """Return the minimum of arguments."""
    if not args:
        raise ValueError("no arguments / ntakintu")
    return min(args)


def max_of(*args: Number) -> Number:
    """Return the maximum of arguments."""
    if not args:
        raise ValueError("no arguments / ntakintu")
    return max(args)
