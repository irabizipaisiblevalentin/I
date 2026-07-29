from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Optional

from .ikoresho import Ikoresho


class KeyboardType(Enum):
    DEFAULT = "default"
    EMAIL = "email"
    NUMBER = "number"
    PHONE = "phone"
    URL = "url"
    DECIMAL = "decimal"


class Ifishi(Ikoresho):
    """Form input component for collecting user text input.

    Supports labels, validation, error display, keyboard type
    configuration, password obscuring, and change/submit callbacks.

    Attributes:
        value: Current text value.
        placeholder: Placeholder text when the field is empty.
        label: Label displayed above the input.
        helper_text: Persistent helper text below the input.
        error_text: Error message displayed on validation failure.
        enabled: Whether the input accepts user interaction.
        read_only: Whether the input is read-only.
        on_change: Callback invoked with the new value on each change.
        on_submit: Callback invoked when the user submits the field.
        keyboard_type: Virtual keyboard type hint.
        obscure_text: Whether text should be masked (password mode).
        max_length: Maximum number of characters allowed.
        autofocus: Whether the field should autofocus on mount.
        validator: Optional callable that returns an error string or
            None when the value is valid.
    """

    def __init__(
        self,
        value: str = "",
        placeholder: str = "",
        label: str = "",
        helper_text: str = "",
        error_text: str = "",
        enabled: bool = True,
        read_only: bool = False,
        on_change: Optional[Callable[[str], Any]] = None,
        on_submit: Optional[Callable[[str], Any]] = None,
        keyboard_type: KeyboardType = KeyboardType.DEFAULT,
        obscure_text: bool = False,
        max_length: Optional[int] = None,
        autofocus: bool = False,
        validator: Optional[Callable[[str], Optional[str]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(enabled=enabled, **kwargs)
        self._value: str = value
        self._placeholder: str = placeholder
        self._label: str = label
        self._helper_text: str = helper_text
        self._error_text: str = error_text
        self._read_only: bool = read_only
        self._on_change: Optional[Callable[[str], Any]] = on_change
        self._on_submit: Optional[Callable[[str], Any]] = on_submit
        self._keyboard_type: KeyboardType = keyboard_type
        self._obscure_text: bool = obscure_text
        self._max_length: Optional[int] = max_length
        self._autofocus: bool = autofocus
        self._validator: Optional[Callable[[str], Optional[str]]] = validator

    # --- Properties ---

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        self._value = new_value

    @property
    def placeholder(self) -> str:
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        self._placeholder = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def helper_text(self) -> str:
        return self._helper_text

    @helper_text.setter
    def helper_text(self, value: str) -> None:
        self._helper_text = value

    @property
    def error_text(self) -> str:
        return self._error_text

    @error_text.setter
    def error_text(self, value: str) -> None:
        self._error_text = value

    @property
    def read_only(self) -> bool:
        return self._read_only

    @read_only.setter
    def read_only(self, value: bool) -> None:
        self._read_only = value

    @property
    def on_change(self) -> Optional[Callable[[str], Any]]:
        return self._on_change

    @on_change.setter
    def on_change(self, value: Optional[Callable[[str], Any]]) -> None:
        self._on_change = value

    @property
    def on_submit(self) -> Optional[Callable[[str], Any]]:
        return self._on_submit

    @on_submit.setter
    def on_submit(self, value: Optional[Callable[[str], Any]]) -> None:
        self._on_submit = value

    @property
    def keyboard_type(self) -> KeyboardType:
        return self._keyboard_type

    @keyboard_type.setter
    def keyboard_type(self, value: KeyboardType) -> None:
        self._keyboard_type = value

    @property
    def obscure_text(self) -> bool:
        return self._obscure_text

    @obscure_text.setter
    def obscure_text(self, value: bool) -> None:
        self._obscure_text = value

    @property
    def max_length(self) -> Optional[int]:
        return self._max_length

    @max_length.setter
    def max_length(self, value: Optional[int]) -> None:
        self._max_length = value

    @property
    def autofocus(self) -> bool:
        return self._autofocus

    @autofocus.setter
    def autofocus(self, value: bool) -> None:
        self._autofocus = value

    @property
    def validator(self) -> Optional[Callable[[str], Optional[str]]]:
        return self._validator

    @validator.setter
    def validator(self, value: Optional[Callable[[str], Optional[str]]]) -> None:
        self._validator = value

    # --- Methods ---

    def set_value(self, value: str) -> None:
        if self._max_length is not None and len(value) > self._max_length:
            value = value[: self._max_length]
        self._value = value
        if self._on_change is not None:
            self._on_change(value)

    def set_error(self, error: str) -> None:
        self._error_text = error

    def validate(self) -> bool:
        if self._validator is None:
            return True
        error = self._validator(self._value)
        if error is not None:
            self._error_text = error
            return False
        self._error_text = ""
        return True

    def focus(self) -> None:
        pass

    def clear(self) -> None:
        self._value = ""
        self._error_text = ""

    def render(self) -> dict[str, Any]:
        return {
            "type": "Ifishi",
            "value": self._value,
            "placeholder": self._placeholder,
            "label": self._label,
            "helper_text": self._helper_text,
            "error_text": self._error_text,
            "read_only": self._read_only,
            "keyboard_type": self._keyboard_type.value,
            "obscure_text": self._obscure_text,
            "max_length": self._max_length,
            "autofocus": self._autofocus,
            "enabled": self._enabled,
            "visible": self._visible,
        }


class IfishiAgasanduku(Ifishi):
    """TextField – single-line text input."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IfishiAgasanduku"
        return base


class IfishiGikoni(Ifishi):
    """TextArea – multi-line text input area.

    Attributes:
        min_lines: Minimum number of visible lines.
        max_lines: Maximum number of visible lines before scrolling.
    """

    def __init__(
        self,
        min_lines: int = 3,
        max_lines: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._min_lines: int = max(1, min_lines)
        self._max_lines_input: Optional[int] = max_lines

    @property
    def min_lines(self) -> int:
        return self._min_lines

    @min_lines.setter
    def min_lines(self, value: int) -> None:
        self._min_lines = max(1, value)

    @property
    def max_lines(self) -> Optional[int]:
        return self._max_lines_input

    @max_lines.setter
    def max_lines(self, value: Optional[int]) -> None:
        self._max_lines_input = value

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IfishiGikoni"
        base["min_lines"] = self._min_lines
        base["max_lines"] = self._max_lines_input
        return base


class IfishiPassword(Ifishi):
    """Password input field with obscuring enabled by default."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("obscure_text", True)
        super().__init__(**kwargs)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IfishiPassword"
        return base


class IfishiEmail(Ifishi):
    """Email input field with email keyboard type and validation."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("keyboard_type", KeyboardType.EMAIL)
        kwargs.setdefault("placeholder", "email@example.com")
        super().__init__(**kwargs)

    @staticmethod
    def _default_email_validator(value: str) -> Optional[str]:
        if "@" not in value or "." not in value:
            return "Andika imeli ikoreshwa"
        return None

    def validate(self) -> bool:
        if self._validator is None:
            error = self._default_email_validator(self._value)
            if error is not None:
                self._error_text = error
                return False
            return True
        return super().validate()

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IfishiEmail"
        return base


class IfishiPhone(Ifishi):
    """Phone number input field with phone keyboard type."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("keyboard_type", KeyboardType.PHONE)
        kwargs.setdefault("placeholder", "+250 7XX XXX XXX")
        super().__init__(**kwargs)

    @staticmethod
    def _default_phone_validator(value: str) -> Optional[str]:
        cleaned = "".join(c for c in value if c.isdigit())
        if len(cleaned) < 10:
            return "Andika numero yashyize"
        return None

    def validate(self) -> bool:
        if self._validator is None:
            error = self._default_phone_validator(self._value)
            if error is not None:
                self._error_text = error
                return False
            return True
        return super().validate()

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IfishiPhone"
        return base
