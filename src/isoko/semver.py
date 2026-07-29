"""semver — Semantic Versioning implementation for isoko.

Implements SemVer 2.0.0 with range matching, comparison, and resolution.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple


class Version:
    """A semantic version: MAJOR.MINOR.PATCH[-prerelease][+build]."""

    __slots__ = ("major", "minor", "patch", "prerelease", "build")
    _PATTERN = re.compile(
        r"^(\d+)\.(\d+)\.(\d+)"
        r"(?:-([a-zA-Z0-9.]+))?"
        r"(?:\+([a-zA-Z0-9.]+))?$"
    )

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0,
                 prerelease: Optional[str] = None, build: Optional[str] = None) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

    @classmethod
    def parse(cls, s: str) -> Version:
        """Parse a version string. Raises ValueError on invalid format."""
        m = cls._PATTERN.match(s.strip())
        if not m:
            raise ValueError(f"invalid version: {s!r}")
        return cls(
            major=int(m.group(1)),
            minor=int(m.group(2)),
            patch=int(m.group(3)),
            prerelease=m.group(4),
            build=m.group(5),
        )

    @classmethod
    def try_parse(cls, s: str) -> Optional[Version]:
        try:
            return cls.parse(s)
        except ValueError:
            return None

    @property
    def tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    @property
    def is_prerelease(self) -> bool:
        return self.prerelease is not None

    def _prerelease_parts(self) -> List:
        if self.prerelease is None:
            return None  # None sorts after any list in our comparison
        parts = []
        for p in self.prerelease.split("."):
            try:
                parts.append((0, int(p)))
            except ValueError:
                parts.append((1, p))
        return parts

    def _cmp_key(self) -> Tuple:
        pre = self._prerelease_parts()
        # Versions WITHOUT prerelease have higher precedence
        # Use a tuple where None (no prerelease) is sorted after any list
        if pre is None:
            pre_key = (1,)  # Greater than any prerelease
        else:
            pre_key = (0,) + tuple(pre)
        return (self.major, self.minor, self.patch, pre_key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.tuple == other.tuple and self.prerelease == other.prerelease

    def __lt__(self, other: Version) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() < other._cmp_key()

    def __le__(self, other: Version) -> bool:
        return self == other or self < other

    def __gt__(self, other: Version) -> bool:
        return not self <= other

    def __ge__(self, other: Version) -> bool:
        return not self < other

    def __hash__(self) -> int:
        return hash(self.tuple + (self.prerelease,))

    def __str__(self) -> str:
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            s += f"-{self.prerelease}"
        if self.build:
            s += f"+{self.build}"
        return s

    def __repr__(self) -> str:
        return f"Version({self})"


class Range:
    """A version range expression (e.g. '>=1.0.0 <2.0.0', '^1.0.0', '~1.2.0')."""

    __slots__ = ("_predicates",)

    def __init__(self, spec: str) -> None:
        self._predicates = self._parse(spec.strip())

    @staticmethod
    def _parse(spec: str) -> list:
        predicates = []
        spec = spec.strip()
        if not spec:
            return [lambda v: True]

        # Handle ^ (caret) — compatible with version
        if spec.startswith("^"):
            ver = Version.parse(spec[1:])
            if ver.major != 0:
                predicates.append(lambda v, _ver=ver: v >= _ver and v < Version(_ver.major + 1, 0, 0))
            elif ver.minor != 0:
                predicates.append(lambda v, _ver=ver: v >= _ver and v < Version(0, _ver.minor + 1, 0))
            else:
                predicates.append(lambda v, _ver=ver: v >= _ver and v < Version(0, 0, _ver.patch + 1))
            return predicates

        # Handle ~ (tilde) — approximately equivalent
        if spec.startswith("~"):
            ver = Version.parse(spec[1:])
            predicates.append(lambda v, _ver=ver: v >= _ver and v < Version(_ver.major, _ver.minor + 1, 0))
            return predicates

        # Handle * (any)
        if spec == "*":
            return [lambda v: True]

        # Handle comma-separated ranges (intersection)
        if "," in spec:
            for part in spec.split(","):
                predicates.extend(Range._parse(part.strip()))
            return predicates

        # Handle space-separated range (intersection)
        if " " in spec:
            for part in spec.split():
                predicates.extend(Range._parse(part.strip()))
            return predicates

        # Handle comparators: >=, <=, >, <, =, ==
        for op in (">=", "<=", "!=", "==", ">", "<", "="):
            if spec.startswith(op):
                ver = Version.parse(spec[len(op):])
                if op in ("=", "=="):
                    predicates.append(lambda v, _ver=ver: v == _ver)
                elif op == ">=":
                    predicates.append(lambda v, _ver=ver: v >= _ver)
                elif op == "<=":
                    predicates.append(lambda v, _ver=ver: v <= _ver)
                elif op == ">":
                    predicates.append(lambda v, _ver=ver: v > _ver)
                elif op == "<":
                    predicates.append(lambda v, _ver=ver: v < _ver)
                elif op == "!=":
                    predicates.append(lambda v, _ver=ver: v != _ver)
                return predicates

        # Handle x-ranges: 1.x, 1.*.* , 1.2.*
        if "x" in spec or "X" in spec or spec.endswith(".*"):
            parts = spec.replace("x", "*").replace("X", "*").split(".")
            if len(parts) == 1:
                predicates.append(lambda v, _maj=int(parts[0]): v.major == _maj)
            elif len(parts) == 2 and parts[1] == "*":
                predicates.append(lambda v, _maj=int(parts[0]): v.major == _maj)
            elif len(parts) == 3 and parts[2] == "*":
                predicates.append(lambda v, _maj=int(parts[0]), _min=int(parts[1]):
                                  v.major == _maj and v.minor == _min)
            return predicates

        # Plain version — exact match
        ver = Version.parse(spec)
        predicates.append(lambda v, _ver=ver: v == _ver)
        return predicates

    def satisfies(self, version: Version) -> bool:
        """Check if a version satisfies this range."""
        return all(p(version) for p in self._predicates)

    def __str__(self) -> str:
        return f"Range({len(self._predicates)} predicates)"

    def __repr__(self) -> str:
        return f"Range()"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_version(s: str) -> Version:
    return Version.parse(s)


def parse_range(s: str) -> Range:
    return Range(s)


def max_satisfying(versions: List[Version], spec: str) -> Optional[Version]:
    """Find the highest version satisfying a range spec."""
    r = Range(spec)
    candidates = [v for v in versions if r.satisfies(v) and not v.is_prerelease]
    if not candidates:
        candidates = [v for v in versions if r.satisfies(v)]
    return max(candidates) if candidates else None


def min_satisfying(versions: List[Version], spec: str) -> Optional[Version]:
    """Find the lowest version satisfying a range spec."""
    r = Range(spec)
    candidates = [v for v in versions if r.satisfies(v)]
    return min(candidates) if candidates else None


def sort_versions(versions: List[Version], descending: bool = False) -> List[Version]:
    """Sort versions in ascending or descending order."""
    return sorted(versions, reverse=descending)
