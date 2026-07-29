"""Ibizamini by'Urwego — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.urwego.shingiro import Inyuma
from ibiro.urwego.umutwe import InyumaUmutwe
from ibiro.urwego.menya import menya_urwego, kora_inyuma


class TestInyumaUmutwe:
    def test_kora(self):
        inyuma = InyumaUmutwe()
        assert isinstance(inyuma, Inyuma)

    def test_shaka_muri_duporo(self):
        inyuma = InyumaUmutwe()
        amakuru = inyuma.shaka_muri_duporo()
        assert amakuru is None

    def test_shira_muri_duporo(self):
        inyuma = InyumaUmutwe()
        igisubizo = inyuma.shira_muri_duporo("ikizamini")
        assert igisubizo is True

    def test_ingano_ikiganiro(self):
        inyuma = InyumaUmutwe()
        w, h = inyuma.ingano_ikiganiro()
        assert w == 1920
        assert h == 1080

    def test_wiga_urwego(self):
        inyuma = InyumaUmutwe()
        izina = inyuma.inyuma_urwego()
        assert izina == "Headless"

    def test_tangiza_garura_bool(self):
        inyuma = InyumaUmutwe()
        igisubizo = inyuma.tangiza()
        assert igisubizo is True

    def test_rirarika_garura_int(self):
        inyuma = InyumaUmutwe()
        igisubizo = inyuma.rirarika()
        assert isinstance(igisubizo, int)

    def test_hagarika(self):
        inyuma = InyumaUmutwe()
        inyuma.hagarika()


class TestMenya:
    def test_menya_urwego(self):
        urwego = menya_urwego()
        assert urwego in ("windows", "linux", "darwin", "headless")

    def test_kora_inyuma(self):
        inyuma = kora_inyuma()
        assert isinstance(inyuma, Inyuma)
