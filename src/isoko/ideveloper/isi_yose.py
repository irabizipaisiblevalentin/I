"""I Developer Platform — Globalisation (Isi Yose)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import LocalisedContent


SUPPORTED_LOCALES = [
    {"locale": "en", "name": "English", "is_rtl": False},
    {"locale": "es", "name": "Spanish", "is_rtl": False},
    {"locale": "fr", "name": "French", "is_rtl": False},
    {"locale": "de", "name": "German", "is_rtl": False},
    {"locale": "zh", "name": "Chinese", "is_rtl": False},
    {"locale": "ja", "name": "Japanese", "is_rtl": False},
    {"locale": "ko", "name": "Korean", "is_rtl": False},
    {"locale": "ar", "name": "Arabic", "is_rtl": True},
    {"locale": "pt", "name": "Portuguese", "is_rtl": False},
    {"locale": "ru", "name": "Russian", "is_rtl": False},
    {"locale": "hi", "name": "Hindi", "is_rtl": False},
    {"locale": "rw", "name": "Kinyarwanda", "is_rtl": False},
]


class GlobalisationManager:
    def __init__(self):
        self._localised: Dict[str, LocalisedContent] = {}
        self._locales = {l["locale"]: l for l in SUPPORTED_LOCALES}
        self._mirrors: List[Dict[str, str]] = []
        self._communities: Dict[str, List[Dict[str, Any]]] = {}

    def get_supported_locales(self) -> List[Dict[str, Any]]:
        return list(self._locales.values())

    def add_translation(self, locale: str, key: str, value: str) -> bool:
        if locale not in self._locales:
            return False
        if locale not in self._localised:
            self._localised[locale] = LocalisedContent(locale=locale, is_rtl=self._locales[locale]["is_rtl"])
        self._localised[locale].translations[key] = value
        return True

    def get_translation(self, locale: str, key: str) -> Optional[str]:
        content = self._localised.get(locale)
        return content.translations.get(key) if content else None

    def add_mirror(self, region: str, url: str) -> Dict[str, str]:
        mirror = {"region": region, "url": url}
        self._mirrors.append(mirror)
        return mirror

    def get_mirrors(self) -> List[Dict[str, str]]:
        return list(self._mirrors)

    def get_region_for_locale(self, locale: str) -> str:
        region_map = {
            "en": "global", "es": "americas", "fr": "emea", "de": "emea",
            "zh": "apac", "ja": "apac", "ko": "apac", "ar": "emea",
            "pt": "americas", "ru": "emea", "hi": "apac", "rw": "africa",
        }
        return region_map.get(locale, "global")

    def register_local_community(self, locale: str, name: str, url: str) -> bool:
        if locale not in self._locales:
            return False
        self._communities.setdefault(locale, []).append({"name": name, "url": url})
        return True

    def get_local_communities(self, locale: str) -> List[Dict[str, Any]]:
        return self._communities.get(locale, [])

    def get_accessibility_features(self) -> Dict[str, Any]:
        return {
            "screen_reader_support": True,
            "high_contrast_mode": True,
            "font_size_adjustment": True,
            "keyboard_navigation": True,
            "captioning": True,
            "simplified_layout": True,
        }

    def get_offline_learning(self) -> Dict[str, Any]:
        return {
            "available": True,
            "formats": ["PDF", "EPUB", "ZIP"],
            "content_types": ["documentation", "courses", "tutorials"],
            "max_size_mb": 500,
        }

    def get_low_bandwidth_mode(self) -> Dict[str, Any]:
        return {
            "available": True,
            "features": ["text_only", "compressed_images", "lazy_loading", "minified_assets"],
            "target_bandwidth_kbps": 50,
        }
