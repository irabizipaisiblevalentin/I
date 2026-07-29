"""localization — Localization and internationalization.

Provides multi-language support with translation loading,
locale detection, pluralization, and formatting.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Union


class Locale:
    """Represents a locale with language and region."""
    __slots__ = ("language", "region", "script")

    def __init__(self, language: str = "en", region: str = "",
                 script: str = "") -> None:
        self.language = language.lower()
        self.region = region.upper()
        self.script = script

    @classmethod
    def parse(cls, locale_str: str) -> "Locale":
        parts = locale_str.replace("-", "_").split("_")
        lang = parts[0] if parts else "en"
        region = parts[1] if len(parts) > 1 else ""
        script = parts[2] if len(parts) > 2 else ""
        return cls(lang, region, script)

    @property
    def code(self) -> str:
        parts = [self.language]
        if self.region:
            parts.append(self.region)
        if self.script:
            parts.append(self.script)
        return "_".join(parts)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Locale):
            return NotImplemented
        return self.code == other.code

    def __hash__(self) -> int:
        return hash(self.code)

    def __repr__(self) -> str:
        return f"Locale({self.code})"


class TranslationStore:
    """In-memory store for translation strings."""

    def __init__(self) -> None:
        self._translations: Dict[str, Dict[str, str]] = {}

    def add_translations(self, locale: Union[str, Locale],
                         translations: Dict[str, str]) -> None:
        code = locale.code if isinstance(locale, Locale) else locale
        store = self._translations.setdefault(code, {})
        store.update(translations)

    def get(self, locale: Union[str, Locale], key: str,
            default: str = "") -> str:
        code = locale.code if isinstance(locale, Locale) else locale
        store = self._translations.get(code, {})
        return store.get(key, default)

    def has(self, locale: Union[str, Locale], key: str) -> bool:
        code = locale.code if isinstance(locale, Locale) else locale
        return key in self._translations.get(code, {})

    def keys(self, locale: Union[str, Locale]) -> List[str]:
        code = locale.code if isinstance(locale, Locale) else locale
        return list(self._translations.get(code, {}).keys())

    def locales(self) -> List[str]:
        return list(self._translations.keys())

    def merge(self, locale: Union[str, Locale],
              translations: Dict[str, str]) -> None:
        self.add_translations(locale, translations)

    def clear(self) -> None:
        self._translations.clear()


class Localizer:
    """High-level localization interface."""

    def __init__(self, default_locale: Union[str, Locale] = "en") -> None:
        if isinstance(default_locale, str):
            self._default_locale = Locale.parse(default_locale)
        else:
            self._default_locale = default_locale
        self._current_locale = self._default_locale
        self._store = TranslationStore()
        self._formatters: Dict[str, Callable] = {}

    @property
    def locale(self) -> Locale:
        return self._current_locale

    @locale.setter
    def locale(self, value: Union[str, Locale]) -> None:
        if isinstance(value, str):
            self._current_locale = Locale.parse(value)
        else:
            self._current_locale = value

    @property
    def store(self) -> TranslationStore:
        return self._store

    def t(self, key: str, default: str = "", **kwargs: Any) -> str:
        """Translate a key with optional interpolation."""
        text = self._store.get(self._current_locale, key, default or key)
        if kwargs:
            text = self._interpolate(text, kwargs)
        return text

    def translate(self, key: str, locale: Union[str, Locale],
                  default: str = "", **kwargs: Any) -> str:
        text = self._store.get(locale, key, default or key)
        if kwargs:
            text = self._interpolate(text, kwargs)
        return text

    def plural(self, key: str, count: int, default: str = "",
               **kwargs: Any) -> str:
        plural_key = f"{key}{'_one' if count == 1 else '_other'}"
        text = self._store.get(self._current_locale, plural_key,
                               self._store.get(self._current_locale, key, default or key))
        text = text.replace("{count}", str(count))
        if kwargs:
            text = self._interpolate(text, kwargs)
        return text

    def register_formatter(self, name: str, formatter: Callable) -> None:
        self._formatters[name] = formatter

    def format(self, key: str, formatter: str, **kwargs: Any) -> str:
        text = self.t(key, **kwargs)
        if formatter in self._formatters:
            return self._formatters[formatter](text, **kwargs)
        return text

    def load_json(self, path: str, locale: Optional[Union[str, Locale]] = None) -> bool:
        import json
        if not os.path.isfile(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                loc = locale or Locale.parse(os.path.splitext(os.path.basename(path))[0])
                self._store.add_translations(loc, data)
                return True
        except (json.JSONDecodeError, OSError):
            pass
        return False

    def has_key(self, key: str) -> bool:
        return self._store.has(self._current_locale, key)

    def available_keys(self) -> List[str]:
        return self._store.keys(self._current_locale)

    def available_locales(self) -> List[str]:
        return self._store.locales()

    def _interpolate(self, text: str, kwargs: Dict[str, Any]) -> str:
        for k, v in kwargs.items():
            text = text.replace(f"{{{k}}}", str(v))
        return text
