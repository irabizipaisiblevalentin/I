"""testing — Test framework for the I language.

Provides a lightweight test runner with assertions and test discovery.
"""

from __future__ import annotations

import sys
import time
import traceback
from typing import Any, Callable, Dict, List, Optional


class TestResult:
    """Result of a single test."""
    __slots__ = ("name", "passed", "error", "duration_ms")

    def __init__(self, name: str, passed: bool, error: str = "", duration_ms: float = 0) -> None:
        self.name = name
        self.passed = passed
        self.error = error
        self.duration_ms = duration_ms

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.name} ({self.duration_ms:.1f}ms)"


class TestSuite:
    """A collection of test cases."""

    def __init__(self, name: str = "suite") -> None:
        self.name = name
        self._tests: List[tuple] = []  # (name, fn)

    def add(self, name: str, fn: Callable) -> None:
        self._tests.append((name, fn))

    def run(self) -> List[TestResult]:
        results: List[TestResult] = []
        for name, fn in self._tests:
            start = time.perf_counter()
            try:
                fn()
                elapsed = (time.perf_counter() - start) * 1000
                results.append(TestResult(name, True, duration_ms=elapsed))
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                error = f"{type(e).__name__}: {e}"
                results.append(TestResult(name, False, error, elapsed))
        return results


class TestRunner:
    """Test runner with reporting."""

    def __init__(self) -> None:
        self._suites: List[TestSuite] = []

    def suite(self, name: str) -> TestSuite:
        s = TestSuite(name)
        self._suites.append(s)
        return s

    def run(self) -> List[TestResult]:
        all_results: List[TestResult] = []
        for suite in self._suites:
            results = suite.run()
            all_results.extend(results)
        self._report(all_results)
        return all_results

    def _report(self, results: List[TestResult]) -> None:
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        total_ms = sum(r.duration_ms for r in results)
        print(f"\n{'='*60}")
        print(f"Results: {passed} passed, {failed} failed, {len(results)} total ({total_ms:.1f}ms)")
        if failed:
            print(f"\nFailed tests:")
            for r in results:
                if not r.passed:
                    print(f"  {r.name}: {r.error}")
        print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

def assert_equal(actual: Any, expected: Any, msg: str = "") -> None:
    if actual != expected:
        raise AssertionError(f"{msg}: expected {expected!r}, got {actual!r}" if msg else f"expected {expected!r}, got {actual!r}")


def assert_not_equal(actual: Any, expected: Any, msg: str = "") -> None:
    if actual == expected:
        raise AssertionError(f"{msg}: values are equal: {actual!r}" if msg else f"values are equal: {actual!r}")


def assert_true(value: Any, msg: str = "") -> None:
    if not value:
        raise AssertionError(f"{msg}: expected truthy, got {value!r}" if msg else f"expected truthy, got {value!r}")


def assert_false(value: Any, msg: str = "") -> None:
    if value:
        raise AssertionError(f"{msg}: expected falsy, got {value!r}" if msg else f"expected falsy, got {value!r}")


def assert_raises(exc_type: Type, fn: Callable, *args: Any, **kwargs: Any) -> None:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__} to be raised")


def assert_in(item: Any, collection: Any, msg: str = "") -> None:
    if item not in collection:
        raise AssertionError(f"{msg}: {item!r} not in {collection!r}" if msg else f"{item!r} not in {collection!r}")


def assert_is_none(value: Any, msg: str = "") -> None:
    if value is not None:
        raise AssertionError(f"{msg}: expected None, got {value!r}" if msg else f"expected None, got {value!r}")


def assert_is_not_none(value: Any, msg: str = "") -> None:
    if value is None:
        raise AssertionError(f"{msg}: expected not None" if msg else "expected not None")
