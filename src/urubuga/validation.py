"""validation — Request validation system.

Provides field validation, schema validation, and custom validators
for incoming request data.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Type, Union


class ValidationError:
    """A single validation error."""
    __slots__ = ("field", "message", "code")

    def __init__(self, field: str, message: str, code: str = "invalid") -> None:
        self.field = field
        self.message = message
        self.code = code

    def to_dict(self) -> Dict[str, str]:
        return {"field": self.field, "message": self.message, "code": self.code}


class ValidationResult:
    """Result of validation."""
    __slots__ = ("is_valid", "errors", "_data")

    def __init__(self, is_valid: bool = True,
                 errors: Optional[List[ValidationError]] = None,
                 data: Optional[Dict[str, Any]] = None) -> None:
        self.is_valid = is_valid
        self.errors = errors or []
        self._data = data or {}

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

    def add_error(self, field: str, message: str,
                  code: str = "invalid") -> None:
        self.is_valid = False
        self.errors.append(ValidationError(field, message, code))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
        }


class Field:
    """A validated field definition."""
    __slots__ = ("name", "field_type", "required", "default", "validators",
                 "label", "description", "min_length", "max_length",
                 "pattern", "min_value", "max_value", "choices", "custom")

    def __init__(self, name: str, field_type: str = "string",
                 required: bool = True, default: Any = None,
                 validators: Optional[List[Callable]] = None,
                 label: str = "", description: str = "",
                 min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 pattern: Optional[str] = None,
                 min_value: Optional[Union[int, float]] = None,
                 max_value: Optional[Union[int, float]] = None,
                 choices: Optional[List[Any]] = None,
                 custom: Optional[Callable] = None) -> None:
        self.name = name
        self.field_type = field_type
        self.required = required
        self.default = default
        self.validators = validators or []
        self.label = label or name
        self.description = description
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.min_value = min_value
        self.max_value = max_value
        self.choices = choices
        self.custom = custom


class Schema:
    """A validation schema containing fields."""

    def __init__(self, name: str = "",
                 fields: Optional[List[Field]] = None) -> None:
        self.name = name
        self._fields: Dict[str, Field] = {}
        if fields:
            for f in fields:
                self._fields[f.name] = f

    def add_field(self, field: Field) -> None:
        self._fields[field.name] = field

    def field(self, name: str, **kwargs: Any) -> None:
        self._fields[name] = Field(name, **kwargs)

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(data=data)
        cleaned = {}

        for name, field in self._fields.items():
            value = data.get(name)

            if value is None:
                if field.required:
                    if field.default is not None:
                        value = field.default
                    else:
                        result.add_error(name, f"{field.label} is required",
                                         "required")
                        continue
                else:
                    value = field.default

            if value is None:
                cleaned[name] = None
                continue

            cleaned[name] = value

            type_error = self._validate_type(name, value, field)
            if type_error:
                result.add_error(name, type_error)
                continue

            range_error = self._validate_range(name, value, field)
            if range_error:
                result.add_error(name, range_error)
                continue

            pattern_error = self._validate_pattern(name, value, field)
            if pattern_error:
                result.add_error(name, pattern_error)
                continue

            choices_error = self._validate_choices(name, value, field)
            if choices_error:
                result.add_error(name, choices_error)
                continue

            for validator in field.validators:
                try:
                    error = validator(value)
                    if error:
                        result.add_error(name, str(error))
                except Exception as e:
                    result.add_error(name, str(e))

            if field.custom:
                try:
                    import inspect
                    sig = inspect.signature(field.custom)
                    if len(sig.parameters) >= 2:
                        error = field.custom(value, data)
                    else:
                        error = field.custom(value)
                    if error:
                        result.add_error(name, str(error))
                except Exception as e:
                    result.add_error(name, str(e))

        result._data = cleaned
        return result

    def _validate_type(self, name: str, value: Any,
                       field: Field) -> Optional[str]:
        type_map = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "list": list,
            "dict": dict,
        }
        expected = type_map.get(field.field_type)
        if expected and not isinstance(value, expected):
            return f"{field.label} must be a {field.field_type}"
        return None

    def _validate_range(self, name: str, value: Any,
                        field: Field) -> Optional[str]:
        if isinstance(value, str):
            if field.min_length is not None and len(value) < field.min_length:
                return f"{field.label} must be at least {field.min_length} characters"
            if field.max_length is not None and len(value) > field.max_length:
                return f"{field.label} must be at most {field.max_length} characters"
        if isinstance(value, (int, float)):
            if field.min_value is not None and value < field.min_value:
                return f"{field.label} must be at least {field.min_value}"
            if field.max_value is not None and value > field.max_value:
                return f"{field.label} must be at most {field.max_value}"
        return None

    def _validate_pattern(self, name: str, value: Any,
                          field: Field) -> Optional[str]:
        if field.pattern and isinstance(value, str):
            if not re.match(field.pattern, value):
                return f"{field.label} format is invalid"
        return None

    def _validate_choices(self, name: str, value: Any,
                          field: Field) -> Optional[str]:
        if field.choices and value not in field.choices:
            allowed = ", ".join(str(c) for c in field.choices)
            return f"{field.label} must be one of: {allowed}"
        return None


def required(value: Any) -> Optional[str]:
    if not value and value != 0:
        return "This field is required"
    return None


def email(value: Any) -> Optional[str]:
    if isinstance(value, str) and not re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
        return "Invalid email address"
    return None


def url(value: Any) -> Optional[str]:
    if isinstance(value, str) and not re.match(
            r"^https?://", value):
        return "Invalid URL"
    return None


def min_length(n: int) -> Callable:
    def validator(value: Any) -> Optional[str]:
        if isinstance(value, str) and len(value) < n:
            return f"Must be at least {n} characters"
        return None
    return validator


def max_length(n: int) -> Callable:
    def validator(value: Any) -> Optional[str]:
        if isinstance(value, str) and len(value) > n:
            return f"Must be at most {n} characters"
        return None
    return validator


def one_of(choices: List[Any]) -> Callable:
    def validator(value: Any) -> Optional[str]:
        if value not in choices:
            return f"Must be one of: {', '.join(str(c) for c in choices)}"
        return None
    return validator
