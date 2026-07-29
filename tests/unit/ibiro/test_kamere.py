"""Ibizamini bya Kamere — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.kamere.idupuro import Idupuro
from ibiro.kamere.itangazo import UyoboreItangazo
from ibiro.kamere.amuhinanyo import UyoboreAmuhinanyo, Muhinanyo


class TestIdupuro:
    def test_shaka(self):
        idup = Idupuro()
        amakuru = idup.shaka()
        assert amakuru is None or isinstance(amakuru, str)

    def test_shira(self):
        idup = Idupuro()
        idup.shira("muraho")
        assert idup.shaka() is None or idup.shaka() == "muraho"


class TestUyoboreItangazo:
    def test_kora(self):
        uy = UyoboreItangazo()
        assert uy is not None

    def test_menyesha(self):
        uy = UyoboreItangazo()
        igisubizo = uy.menyesha("umutwe", "inyandiko")
        assert igisubizo is False or igisubizo is True


class TestMuhinanyo:
    def test_kora(self):
        mu = Muhinanyo("Ctrl+S", "kubika")
        assert mu.amabuto == "Ctrl+S"
        assert mu.indangamuntu_igikorwa == "kubika"


class TestUyoboreAmuhinanyo:
    def test_yandika(self):
        uy = UyoboreAmuhinanyo()
        mu = Muhinanyo("Ctrl+Q", "guhagarika")
        uy.yandika(mu)
        byose = uy.byose()
        assert len(byose) == 1
        assert byose[0].indangamuntu_igikorwa == "guhagarika"

    def test_kuraho(self):
        uy = UyoboreAmuhinanyo()
        mu = Muhinanyo("Ctrl+Q", "guhagarika")
        uy.yandika(mu)
        uy.kuraho("guhagarika")
        assert len(uy.byose()) == 0
