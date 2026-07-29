"""random — Random number generation for the I language.

Provides a deterministic, seedable PRNG with uniform, normal, and
discrete distributions, plus utilities for shuffling and sampling.
"""

from __future__ import annotations

import random as _random
from typing import Any, List, Optional, Sequence, TypeVar, Union


T = TypeVar("T")


class Random:
    """Seedable random number generator."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = _random.Random(seed)

    # Uniform distributions

    def random(self) -> float:
        """Random float in [0.0, 1.0)."""
        return self._rng.random()

    def uniform(self, low: float, high: float) -> float:
        """Random float in [low, high)."""
        return self._rng.uniform(low, high)

    # Integer distributions

    def rand_int(self, low: int, high: int) -> int:
        """Random integer in [low, high] (inclusive)."""
        return self._rng.randint(low, high)

    def rand_range(self, start: int, stop: int, step: int = 1) -> int:
        """Random choice from range(start, stop, step)."""
        return self._rng.randrange(start, stop, step)

    # Distributions

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Gaussian (normal) distribution."""
        return self._rng.gauss(mu, sigma)

    def expovariate(self, lambd: float) -> float:
        """Exponential distribution."""
        return self._rng.expovariate(lambd)

    def triangular(self, low: float = 0.0, high: float = 1.0, mode: Optional[float] = None) -> float:
        """Triangular distribution."""
        return self._rng.triangular(low, high, mode)

    # Sequence operations

    def choice(self, seq: Sequence[T]) -> T:
        """Random element from sequence."""
        return self._rng.choice(seq)

    def choices(self, seq: Sequence[T], k: int = 1) -> List[T]:
        """Random elements with replacement."""
        return self._rng.choices(seq, k=k)

    def sample(self, seq: Sequence[T], k: int = 1) -> List[T]:
        """Random elements without replacement."""
        return self._rng.sample(seq, k=k)

    def shuffle(self, lst: List[Any]) -> None:
        """Shuffle list in place."""
        self._rng.shuffle(lst)

    def shuffled(self, seq: Sequence[T]) -> List[T]:
        """Return shuffled copy."""
        lst = list(seq)
        self._rng.shuffle(lst)
        return lst

    # Weighted

    def weighted_choice(self, items: Sequence[T], weights: Sequence[float]) -> T:
        """Weighted random choice."""
        return self._rng.choices(items, weights=weights, k=1)[0]

    # Boolean

    def coin_flip(self, probability: float = 0.5) -> bool:
        """Random boolean with given probability of True."""
        return self._rng.random() < probability

    def boolean(self) -> bool:
        """Random boolean (50/50)."""
        return self._rng.random() < 0.5

    # Seed

    def get_state(self) -> tuple:
        """Get internal state for reproducibility."""
        return self._rng.getstate()

    def set_state(self, state: tuple) -> None:
        """Set internal state."""
        self._rng.setstate(state)


# Module-level default generator
_default = Random()


def random() -> float:
    """Random float in [0.0, 1.0)."""
    return _default.random()


def uniform(low: float, high: float) -> float:
    """Random float in [low, high)."""
    return _default.uniform(low, high)


def rand_int(low: int, high: int) -> int:
    """Random integer in [low, high] (inclusive)."""
    return _default.rand_int(low, high)


def choice(seq: Sequence[T]) -> T:
    """Random element from sequence."""
    return _default.choice(seq)


def choices(seq: Sequence[T], k: int = 1) -> List[T]:
    """Random elements with replacement."""
    return _default.choices(seq, k=k)


def sample(seq: Sequence[T], k: int = 1) -> List[T]:
    """Random elements without replacement."""
    return _default.sample(seq, k=k)


def shuffle(lst: List[Any]) -> None:
    """Shuffle list in place."""
    _default.shuffle(lst)


def shuffled(seq: Sequence[T]) -> List[T]:
    """Return shuffled copy."""
    return _default.shuffled(seq)


def coin_flip(probability: float = 0.5) -> bool:
    """Random boolean with probability of True."""
    return _default.coin_flip(probability)


def gauss(mu: float = 0.0, sigma: float = 1.0) -> float:
    """Gaussian distribution."""
    return _default.gauss(mu, sigma)


def seed(value: int) -> None:
    """Seed the default generator."""
    _default.set_state(_random.Random(value).getstate())
