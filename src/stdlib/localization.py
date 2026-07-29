"""localization — Internationalization (i18n) for the I language.

Provides message translation, locale management, and pluralization.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


class Locale:
    """Locale configuration."""

    def __init__(self, language: str = "en", region: str = "",
                 currency: str = "USD", decimal_sep: str = ".",
                 thousands_sep: str = ",", date_fmt: str = "%Y-%m-%d") -> None:
        self.language = language
        self.region = region
        self.currency = currency
        self.decimal_sep = decimal_sep
        self.thousands_sep = thousands_sep
        self.date_fmt = date_fmt

    @property
    def code(self) -> str:
        if self.region:
            return f"{self.language}-{self.region}"
        return self.language

    def __repr__(self) -> str:
        return f"Locale({self.code!r})"


# Predefined locales
EN = Locale("en", currency="USD")
RW = Locale("rw", currency="RWF")
FR = Locale("fr", currency="EUR", decimal_sep=",", thousands_sep=" ")
ES = Locale("es", currency="EUR", decimal_sep=",", thousands_sep=".")
DE = Locale("de", currency="EUR", decimal_sep=",", thousands_sep=".")
JA = Locale("ja", currency="JPY")


class Translator:
    """Message translator with pluralization."""

    def __init__(self, locale: Locale) -> None:
        self.locale = locale
        self._messages: Dict[str, Dict[str, str]] = {}
        self._current_lang = locale.language

    def add(self, key: str, translations: Dict[str, str]) -> None:
        """Add translations for a key. Keys are language codes."""
        self._messages[key] = translations

    def translate(self, key: str, **kwargs: str) -> str:
        """Translate a key with optional interpolation."""
        lang_msgs = self._messages.get(key, {})
        template = lang_msgs.get(self._current_lang, key)
        if kwargs:
            return template.format(**kwargs)
        return template

    def t(self, key: str, **kwargs: str) -> str:
        """Short alias for translate."""
        return self.translate(key, **kwargs)

    def plural(self, key: str, count: int, **kwargs: str) -> str:
        """Translate with pluralization (supports {count} placeholder)."""
        plural_key = f"{key}_plural" if count != 1 else f"{key}_singular"
        lang_msgs = self._messages.get(key, {})
        template = lang_msgs.get(plural_key, lang_msgs.get(key, key))
        kwargs["count"] = str(count)
        return template.format(**kwargs)

    def set_language(self, lang: str) -> None:
        self._current_lang = lang


def format_number(value: float, locale: Locale = EN, decimals: int = 2) -> str:
    """Format number according to locale."""
    int_part = int(abs(value))
    frac_part = round(abs(value) - int_part, decimals)
    int_str = ""
    s = str(int_part)
    for i, ch in enumerate(reversed(s)):
        if i > 0 and i % 3 == 0:
            int_str = locale.thousands_sep + int_str
        int_str = ch + int_str
    if value < 0:
        int_str = "-" + int_str
    if decimals > 0:
        frac_str = f"{frac_part:.{decimals}f}"[2:]
        return int_str + locale.decimal_sep + frac_str
    return int_str


def format_currency(value: float, locale: Locale = EN) -> str:
    """Format number as currency."""
    formatted = format_number(value, locale, decimals=2)
    return f"{locale.currency} {formatted}"
