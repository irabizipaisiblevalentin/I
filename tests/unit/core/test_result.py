"""
Tests for Result and Option types.
"""

import pytest

from src.compiler.core.result import (
    Ok,
    Err,
    Some,
    Nothing,
    is_ok,
    is_err,
    unwrap,
    unwrap_or,
    unwrap_or_else,
    map,
    map_err,
    and_then,
    or_else,
    try_all,
    partition,
    is_some,
    is_nothing,
)


class TestResult:
    """Tests for Result type."""

    def test_ok_creation(self):
        result = Ok(42)
        assert is_ok(result)
        assert not is_err(result)

    def test_err_creation(self):
        result = Err("error")
        assert is_err(result)
        assert not is_ok(result)

    def test_unwrap_ok(self):
        assert unwrap(Ok(42)) == 42

    def test_unwrap_err_raises(self):
        with pytest.raises(ValueError):
            unwrap(Err("fail"))

    def test_unwrap_or_ok(self):
        assert unwrap_or(Ok(42), 0) == 42

    def test_unwrap_or_err(self):
        assert unwrap_or(Err("fail"), 0) == 0

    def test_unwrap_or_else_ok(self):
        assert unwrap_or_else(Ok(42), lambda e: 0) == 42

    def test_unwrap_or_else_err(self):
        assert unwrap_or_else(Err("fail"), lambda e: len(e)) == 4

    def test_map_ok(self):
        result = map(Ok(21), lambda x: x * 2)
        assert result == Ok(42)

    def test_map_err(self):
        result = map(Err(21), lambda x: x * 2)
        assert result == Err(21)

    def test_map_err_ok(self):
        result = map_err(Ok(42), lambda e: str(e))
        assert result == Ok(42)

    def test_map_err_err(self):
        result = map_err(Err(42), lambda e: str(e))
        assert result == Err("42")

    def test_and_then_ok(self):
        result = and_then(Ok(21), lambda x: Ok(x * 2))
        assert result == Ok(42)

    def test_and_then_err(self):
        result = and_then(Err("fail"), lambda x: Ok(x * 2))
        assert result == Err("fail")

    def test_or_else_err(self):
        result = or_else(Err("fail"), lambda e: Ok(len(e)))
        assert result == Ok(4)

    def test_or_else_ok(self):
        result = or_else(Ok(42), lambda e: Ok(0))
        assert result == Ok(42)

    def test_try_all_ok(self):
        results = [Ok(1), Ok(2), Ok(3)]
        combined = try_all(results)
        assert combined == Ok([1, 2, 3])

    def test_try_all_err(self):
        results = [Ok(1), Err("e1"), Ok(3), Err("e2")]
        combined = try_all(results)
        assert is_err(combined)

    def test_partition(self):
        results = [Ok(1), Err("e1"), Ok(2), Err("e2")]
        oks, errs = partition(results)
        assert oks == [1, 2]
        assert errs == ["e1", "e2"]

    def test_repr_ok(self):
        assert repr(Ok(42)) == "Ok(42)"

    def test_repr_err(self):
        assert repr(Err("x")) == "Err('x')"


class TestOption:
    """Tests for Option type."""

    def test_some_creation(self):
        opt = Some(42)
        assert is_some(opt)
        assert not is_nothing(opt)

    def test_nothing_creation(self):
        opt = Nothing()
        assert is_nothing(opt)
        assert not is_some(opt)

    def test_repr_some(self):
        assert repr(Some(42)) == "Some(42)"

    def test_repr_nothing(self):
        assert repr(Nothing()) == "Nothing"
