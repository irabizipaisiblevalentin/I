"""
Result and Option Types

Provides functional-style result and option types for safe error handling
without exceptions for recoverable errors.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Successful result value."""

    value: T

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass(frozen=True)
class Err(Generic[E]):
    """Error result value."""

    error: E

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


Result = Union[Ok[T], Err[E]]


def is_ok(result: Result[T, Any]) -> bool:
    """Check if result is Ok."""
    return isinstance(result, Ok)


def is_err(result: Result[Any, E]) -> bool:
    """Check if result is Err."""
    return isinstance(result, Err)


def unwrap(result: Result[T, Any]) -> T:
    """
    Unwrap result, raising ValueError if Err.

    Args:
        result: Result to unwrap

    Returns:
        Inner value

    Raises:
        ValueError: If result is Err
    """
    if isinstance(result, Ok):
        return result.value
    raise ValueError(f"Called unwrap on Err: {result.error}")


def unwrap_or(result: Result[T, Any], default: T) -> T:
    """
    Unwrap result or return default.

    Args:
        result: Result to unwrap
        default: Default value

    Returns:
        Inner value or default
    """
    if isinstance(result, Ok):
        return result.value
    return default


def unwrap_or_else(result: Result[T, Any], fallback: Callable[[Any], T]) -> T:
    """
    Unwrap result or compute fallback.

    Args:
        result: Result to unwrap
        fallback: Function to compute default from error

    Returns:
        Inner value or fallback result
    """
    if isinstance(result, Ok):
        return result.value
    return fallback(result.error)


def map(result: Result[T, E], fn: Callable[[T], U]) -> Result[U, E]:
    """
    Apply function to Ok value.

    Args:
        result: Result to map
        fn: Mapping function

    Returns:
        Mapped result
    """
    if isinstance(result, Ok):
        return Ok(fn(result.value))
    return result


def map_err(result: Result[T, E], fn: Callable[[E], Any]) -> Result[T, Any]:
    """
    Apply function to Err value.

    Args:
        result: Result to map
        fn: Error mapping function

    Returns:
        Mapped result
    """
    if isinstance(result, Err):
        return Err(fn(result.error))
    return result


def and_then(result: Result[T, E], fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
    """
    Chain result-producing functions.

    Args:
        result: Result to chain
        fn: Function producing a new result

    Returns:
        Chained result
    """
    if isinstance(result, Ok):
        return fn(result.value)
    return result


def or_else(result: Result[T, E], fn: Callable[[E], Result[T, Any]]) -> Result[T, Any]:
    """
    Recover from error with alternative result.

    Args:
        result: Result to recover
        fn: Recovery function

    Returns:
        Recovered result
    """
    if isinstance(result, Err):
        return fn(result.error)
    return result


def try_all(results: Sequence[Result[T, E]]) -> Result[list[T], list[E]]:
    """
    Collect all Ok values or first Err.

    Args:
        results: Sequence of results

    Returns:
        List of all values or list of all errors
    """
    values: list[T] = []
    errors: list[E] = []
    for r in results:
        if isinstance(r, Ok):
            values.append(r.value)
        else:
            errors.append(r.error)
    if errors:
        return Err(errors)
    return Ok(values)


def partition(results: Sequence[Result[T, E]]) -> tuple[list[T], list[E]]:
    """
    Separate results into ok values and errors.

    Args:
        results: Sequence of results

    Returns:
        Tuple of (ok_values, errors)
    """
    values: list[T] = []
    errors: list[E] = []
    for r in results:
        if isinstance(r, Ok):
            values.append(r.value)
        else:
            errors.append(r.error)
    return values, errors


@dataclass(frozen=True)
class Some(Generic[T]):
    """Optional value."""

    value: T

    def __repr__(self) -> str:
        return f"Some({self.value!r})"


@dataclass(frozen=True)
class Nothing:
    """Absence of value."""

    def __repr__(self) -> str:
        return "Nothing"


Option = Union[Some[T], Nothing]


def is_some(option: Option[Any]) -> bool:
    """Check if option is Some."""
    return isinstance(option, Some)


def is_nothing(option: Option[Any]) -> bool:
    """Check if option is Nothing."""
    return isinstance(option, Nothing)


__all__ = [
    "Ok",
    "Err",
    "Result",
    "is_ok",
    "is_err",
    "unwrap",
    "unwrap_or",
    "unwrap_or_else",
    "map",
    "map_err",
    "and_then",
    "or_else",
    "try_all",
    "partition",
    "Some",
    "Nothing",
    "Option",
    "is_some",
    "is_nothing",
]
