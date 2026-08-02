"""Tests for istudio.desktop.theme — palettes."""

from __future__ import annotations

from src.istudio.desktop.theme import PALETTES, get_palette, theme_names
from src.istudio.ibikoreshingiro import EditorTheme


def test_all_themes_have_palettes():
    for theme in EditorTheme:
        if theme == EditorTheme.CUSTOM:
            continue
        assert theme in PALETTES
        palette = PALETTES[theme]
        assert palette["bg"]
        assert palette["fg"]
        assert palette["syntax.keyword"]
        assert palette["diagnostic.error"]


def test_get_palette_returns_copy():
    palette = get_palette(EditorTheme.DARK)
    palette["bg"] = "mutated"
    assert PALETTES[EditorTheme.DARK]["bg"] != "mutated"


def test_theme_names_mapping():
    names = theme_names()
    assert names["dark"] == EditorTheme.DARK
    assert names["light"] == EditorTheme.LIGHT
    assert len(names) == len(EditorTheme)


def test_unknown_theme_falls_back_to_dark():
    palette = get_palette(EditorTheme.CUSTOM)
    assert palette == PALETTES[EditorTheme.DARK]
