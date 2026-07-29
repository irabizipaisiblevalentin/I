"""math — Mathematical functions and constants for the I language.

Provides the standard mathematical functions and constants.
All functions handle edge cases (division by zero, overflow) gracefully.
"""

from __future__ import annotations

import math as _math
from typing import List, Optional, Sequence, Tuple, Union


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PI = _math.pi          # 3.141592653589793
E = _math.e            # 2.718281828459045
TAU = _math.tau        # 6.283185307179586 (2π)
INFINITY = float("inf")
NAN = float("nan")
PHI = (1 + _math.sqrt(5)) / 2  # Golden ratio ~ 1.618

# Integer limits
MAX_INT = 2**63 - 1
MIN_INT = -(2**63)


# ---------------------------------------------------------------------------
# Basic arithmetic
# ---------------------------------------------------------------------------

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def sub(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def mul(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def div(a: float, b: float) -> float:
    """Divide a by b. Raises ValueError on division by zero."""
    if b == 0:
        raise ValueError("division by zero / kubura zeru")
    return a / b


def idiv(a: float, b: float) -> int:
    """Integer division (floor). Raises ValueError on division by zero."""
    if b == 0:
        raise ValueError("division by zero / kubura zeru")
    return a // b


def mod(a: float, b: float) -> float:
    """Modulo. Raises ValueError on division by zero."""
    if b == 0:
        raise ValueError("division by zero / kubura zeru")
    return a % b


def pow(base: float, exp: float) -> float:
    """Raise base to the power exp."""
    return base ** exp


def sqrt(x: float) -> float:
    """Square root. Raises ValueError for negative input."""
    if x < 0:
        raise ValueError("square root of negative / ikibago")
    return _math.sqrt(x)


def cbrt(x: float) -> float:
    """Cube root (works for negative values)."""
    if x >= 0:
        return x ** (1 / 3)
    return -((-x) ** (1 / 3))


# ---------------------------------------------------------------------------
# Rounding
# ---------------------------------------------------------------------------

def abs(x: float) -> float:
    """Absolute value."""
    return _math.fabs(x)


def floor(x: float) -> int:
    """Floor (round toward negative infinity)."""
    return _math.floor(x)


def ceil(x: float) -> int:
    """Ceiling (round toward positive infinity)."""
    return _math.ceil(x)


def round_to(x: float, decimals: int = 0) -> float:
    """Round to *decimals* decimal places."""
    if decimals == 0:
        return float(round(x))
    factor = 10 ** decimals
    return round(x * factor) / factor


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value between low and high."""
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b at parameter t."""
    return a + (b - a) * t


# ---------------------------------------------------------------------------
# Logarithms and exponentials
# ---------------------------------------------------------------------------

def ln(x: float) -> float:
    """Natural logarithm. Raises ValueError for x <= 0."""
    if x <= 0:
        raise ValueError("logarithm of non-positive / isaburo")
    return _math.log(x)


def log(x: float, base: float = _math.e) -> float:
    """Logarithm with arbitrary base."""
    if x <= 0:
        raise ValueError("logarithm of non-positive / isaburo")
    if base <= 0 or base == 1:
        raise ValueError("base must be positive and != 1")
    return _math.log(x, base)


def log2(x: float) -> float:
    """Base-2 logarithm."""
    if x <= 0:
        raise ValueError("logarithm of non-positive / isaburo")
    return _math.log2(x)


def log10(x: float) -> float:
    """Base-10 logarithm."""
    if x <= 0:
        raise ValueError("logarithm of non-positive / isaburo")
    return _math.log10(x)


def exp(x: float) -> float:
    """e raised to the power x."""
    return _math.exp(x)


def exp2(x: float) -> float:
    """2 raised to the power x."""
    return 2 ** x


# ---------------------------------------------------------------------------
# Trigonometric
# ---------------------------------------------------------------------------

def sin(x: float) -> float:
    """Sine (radians)."""
    return _math.sin(x)


def cos(x: float) -> float:
    """Cosine (radians)."""
    return _math.cos(x)


def tan(x: float) -> float:
    """Tangent (radians)."""
    return _math.tan(x)


def asin(x: float) -> float:
    """Arcsine. Domain: [-1, 1]."""
    if x < -1 or x > 1:
        raise ValueError("asin domain error / ikibago")
    return _math.asin(x)


def acos(x: float) -> float:
    """Arccosine. Domain: [-1, 1]."""
    if x < -1 or x > 1:
        raise ValueError("acos domain error / ikibago")
    return _math.acos(x)


def atan(x: float) -> float:
    """Arctangent."""
    return _math.atan(x)


def atan2(y: float, x: float) -> float:
    """Two-argument arctangent."""
    return _math.atan2(y, x)


def degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return _math.degrees(radians)


def radians(deg: float) -> float:
    """Convert degrees to radians."""
    return _math.radians(deg)


# ---------------------------------------------------------------------------
# Hyperbolic
# ---------------------------------------------------------------------------

def sinh(x: float) -> float:
    return _math.sinh(x)


def cosh(x: float) -> float:
    return _math.cosh(x)


def tanh(x: float) -> float:
    return _math.tanh(x)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def sum(values: Sequence[float]) -> float:
    """Sum of values."""
    return _math.fsum(values)


def product(values: Sequence[float]) -> float:
    """Product of all values."""
    result = 1.0
    for v in values:
        result *= v
    return result


def mean(values: Sequence[float]) -> float:
    """Arithmetic mean. Raises ValueError for empty sequence."""
    if not values:
        raise ValueError("empty sequence / imimerere iri ubusa")
    return _math.fsum(values) / len(values)


def median(values: Sequence[float]) -> float:
    """Median value. Raises ValueError for empty sequence."""
    if not values:
        raise ValueError("empty sequence / imimerere iri ubusa")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    return s[mid]


def variance(values: Sequence[float], population: bool = True) -> float:
    """Variance. population=True for population, False for sample."""
    if len(values) < (1 if population else 2):
        raise ValueError("insufficient data / amakuru aritagenda")
    m = mean(values)
    sq = sum((x - m) ** 2 for x in values)
    denom = len(values) if population else len(values) - 1
    return sq / denom


def stdev(values: Sequence[float], population: bool = True) -> float:
    """Standard deviation."""
    return _math.sqrt(variance(values, population))


def min_val(values: Sequence[float]) -> float:
    """Minimum value."""
    if not values:
        raise ValueError("empty sequence / imimerere iri ubusa")
    return min(values)


def max_val(values: Sequence[float]) -> float:
    """Maximum value."""
    if not values:
        raise ValueError("empty sequence / imimerere iri ubusa")
    return max(values)


# ---------------------------------------------------------------------------
# Number theory
# ---------------------------------------------------------------------------

def gcd(a: int, b: int) -> int:
    """Greatest common divisor."""
    return _math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    return _math.lcm(a, b)


def factorial(n: int) -> int:
    """Factorial. Raises ValueError for negative."""
    if n < 0:
        raise ValueError("factorial of negative / ikibago")
    return _math.factorial(n)


def is_prime(n: int) -> bool:
    """Check if n is prime."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def primes_up_to(n: int) -> List[int]:
    """List all primes <= n using sieve of Eratosthenes."""
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]


def fibonacci(n: int) -> int:
    """Nth Fibonacci number. fibonacci(0)=0, fibonacci(1)=1."""
    if n < 0:
        raise ValueError("negative index / ikibago")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
