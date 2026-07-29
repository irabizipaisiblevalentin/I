"""Tests for isoko.ideveloper.isi_yose — Globalisation."""

from __future__ import annotations

from isoko.ideveloper.isi_yose import GlobalisationManager, SUPPORTED_LOCALES


def test_globalisation_init():
    gm = GlobalisationManager()
    assert len(gm.get_supported_locales()) == 12


def test_supported_locales_include_rw():
    locales = {l["locale"] for l in SUPPORTED_LOCALES}
    assert "rw" in locales
    assert "en" in locales


def test_add_translation():
    gm = GlobalisationManager()
    assert gm.add_translation("fr", "welcome", "Bienvenue") is True
    assert gm.add_translation("nonexistent", "key", "val") is False


def test_get_translation():
    gm = GlobalisationManager()
    gm.add_translation("es", "hello", "Hola")
    assert gm.get_translation("es", "hello") == "Hola"
    assert gm.get_translation("es", "nonexistent") is None


def test_add_mirror():
    gm = GlobalisationManager()
    mirror = gm.add_mirror("europe", "https://eu.i-lang.org")
    assert mirror["region"] == "europe"
    assert len(gm.get_mirrors()) == 1


def test_region_for_locale():
    gm = GlobalisationManager()
    assert gm.get_region_for_locale("rw") == "africa"
    assert gm.get_region_for_locale("en") == "global"


def test_local_communities():
    gm = GlobalisationManager()
    assert gm.register_local_community("rw", "I Rwanda", "https://rw.i-lang.org") is True
    assert gm.register_local_community("nonexistent", "N/A", "") is False
    communities = gm.get_local_communities("rw")
    assert len(communities) == 1


def test_accessibility_features():
    gm = GlobalisationManager()
    features = gm.get_accessibility_features()
    assert features["screen_reader_support"] is True
    assert features["keyboard_navigation"] is True


def test_offline_learning():
    gm = GlobalisationManager()
    offline = gm.get_offline_learning()
    assert offline["available"] is True
    assert "PDF" in offline["formats"]


def test_low_bandwidth_mode():
    gm = GlobalisationManager()
    lb = gm.get_low_bandwidth_mode()
    assert lb["available"] is True
    assert "text_only" in lb["features"]
