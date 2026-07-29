"""Tests for UFA localization system."""

import json
import os
import tempfile

import pytest
from ufa.localization import Localizer, Locale, TranslationStore


class TestLocale:
    def test_parse(self):
        loc = Locale.parse("en_US")
        assert loc.language == "en"
        assert loc.region == "US"

    def test_code(self):
        loc = Locale("rw", "RW")
        assert loc.code == "rw_RW"

    def test_equality(self):
        assert Locale("en") == Locale("en")
        assert Locale("en") != Locale("fr")

    def test_hash(self):
        assert hash(Locale("en")) == hash(Locale("en"))

    def test_repr(self):
        assert "en" in repr(Locale("en"))


class TestTranslationStore:
    def test_add_get(self):
        store = TranslationStore()
        store.add_translations("en", {"hello": "Hello"})
        assert store.get("en", "hello") == "Hello"

    def test_missing_key(self):
        store = TranslationStore()
        assert store.get("en", "missing", "default") == "default"

    def test_has(self):
        store = TranslationStore()
        store.add_translations("en", {"x": "1"})
        assert store.has("en", "x")
        assert not store.has("en", "y")

    def test_keys(self):
        store = TranslationStore()
        store.add_translations("en", {"a": "1", "b": "2"})
        assert set(store.keys("en")) == {"a", "b"}

    def test_locales(self):
        store = TranslationStore()
        store.add_translations("en", {"a": "1"})
        store.add_translations("rw", {"a": "1"})
        assert set(store.locales()) == {"en", "rw"}

    def test_clear(self):
        store = TranslationStore()
        store.add_translations("en", {"a": "1"})
        store.clear()
        assert store.locales() == []


class TestLocalizer:
    def test_translate(self):
        loc = Localizer()
        loc.store.add_translations("en", {"hello": "Hello"})
        assert loc.t("hello") == "Hello"

    def test_interpolation(self):
        loc = Localizer()
        loc.store.add_translations("en", {"greeting": "Hello {name}"})
        assert loc.t("greeting", name="World") == "Hello World"

    def test_set_locale(self):
        loc = Localizer()
        loc.store.add_translations("en", {"x": "English"})
        loc.store.add_translations("fr", {"x": "French"})
        loc.locale = "fr"
        assert loc.t("x") == "French"

    def test_plural(self):
        loc = Localizer()
        loc.store.add_translations("en", {
            "item_one": "{count} item",
            "item_other": "{count} items",
        })
        assert loc.plural("item", 1) == "1 item"
        assert loc.plural("item", 5) == "5 items"

    def test_translate_with_locale(self):
        loc = Localizer()
        loc.store.add_translations("en", {"x": "E"})
        loc.store.add_translations("fr", {"x": "F"})
        assert loc.translate("x", "fr") == "F"

    def test_has_key(self):
        loc = Localizer()
        loc.store.add_translations("en", {"a": "1"})
        assert loc.has_key("a")
        assert not loc.has_key("b")

    def test_available_keys(self):
        loc = Localizer()
        loc.store.add_translations("en", {"a": "1", "b": "2"})
        assert set(loc.available_keys()) == {"a", "b"}

    def test_available_locales(self):
        loc = Localizer()
        loc.store.add_translations("en", {"a": "1"})
        loc.store.add_translations("rw", {"a": "1"})
        assert set(loc.available_locales()) == {"en", "rw"}

    def test_load_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         delete=False) as f:
            json.dump({"hello": "Muraho"}, f)
            f.flush()
            path = f.name
        try:
            loc = Localizer()
            result = loc.load_json(path, "rw")
            assert result
            loc.locale = "rw"
            assert loc.t("hello") == "Muraho"
        finally:
            os.unlink(path)

    def test_load_json_missing(self):
        loc = Localizer()
        assert not loc.load_json("/nonexistent.json")

    def test_register_formatter(self):
        loc = Localizer()
        loc.register_formatter("upper", lambda text, **kw: text.upper())
        loc.store.add_translations("en", {"x": "hello"})
        result = loc.format("x", "upper")
        assert result == "HELLO"

    def test_default_locale(self):
        loc = Localizer("fr")
        assert loc.locale.language == "fr"
