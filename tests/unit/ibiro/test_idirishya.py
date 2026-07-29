"""Ibizamini by'Idirishya — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.idirishya import Idirishya, IgenamiterereIdirishya, UyoboreIdirishya, ImiterereIdirishya, UburyoIdirishya


class TestIgenamiterereIdirishya:
    def test_mburabura(self):
        ig = IgenamiterereIdirishya()
        assert ig.umutwe == "IBIRO"
        assert ig.ubugari == 800
        assert ig.uburebure == 600

    def test_byihariye(self):
        ig = IgenamiterereIdirishya(umutwe="Ikizamini", ubugari=1024, uburebure=768, hagahinduka=False)
        assert ig.umutwe == "Ikizamini"
        assert ig.ubugari == 1024
        assert ig.uburebure == 768
        assert not ig.hagahinduka


class TestIdirishya:
    def test_kora(self):
        id = Idirishya("ikizamini", umutwe="Idirishya rya Ikizamini")
        assert id.indangamuntu == "ikizamini"
        assert id.igenamiterere.umutwe == "Idirishya rya Ikizamini"

    def test_kwerekana_guhisha(self):
        id = Idirishya("ikizamini")
        assert not id.kaboneka
        id.kwerekana()
        assert id.kaboneka
        id.guhisha()
        assert not id.kaboneka

    def test_kwerekana_garura_idirishya(self):
        id = Idirishya("ikizamini")
        igisubizo = id.kwerekana()
        assert igisubizo is id

    def test_gufunga(self):
        id = Idirishya("ikizamini")
        id.kwerekana()
        id.funga()
        assert id.imiterere == ImiterereIdirishya.FUNGWE

    def test_kingura(self):
        id = Idirishya("ikizamini")
        id.kingura()
        assert id.uburyo == UburyoIdirishya.YUZURA

    def test_gabanura(self):
        id = Idirishya("ikizamini")
        id.kingura()
        id.gabanura()
        assert id.uburyo == UburyoIdirishya.GASANZWE


class TestUyoboreIdirishya:
    def test_kora_idirishya(self):
        uy = UyoboreIdirishya()
        id = uy.kora_idirishya("id1")
        assert id.indangamuntu == "id1"
        assert "id1" in uy.amadirishya

    def test_shaka_idirishya(self):
        uy = UyoboreIdirishya()
        uy.kora_idirishya("id1")
        id = uy.idirishya("id1")
        assert id is not None

    def test_shaka_idirishya_ntiboneka(self):
        uy = UyoboreIdirishya()
        assert uy.idirishya("ntibaho") is None

    def test_gufunga_idirishya(self):
        uy = UyoboreIdirishya()
        uy.kora_idirishya("id1")
        uy.funga_idirishya("id1")
        assert "id1" not in uy.amadirishya

    def test_gufunga_mpine(self):
        uy = UyoboreIdirishya()
        uy.kora_idirishya("id1")
        uy.kora_idirishya("id2")
        uy.funga_mpine()
        assert len(uy.amadirishya) == 0
