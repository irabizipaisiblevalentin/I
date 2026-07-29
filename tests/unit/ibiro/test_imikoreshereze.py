"""Ibizamini by'Imikoreshereze — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.imikoreshereze.ikora import Ikora, Ibaze, Icyegeranyo
from ibiro.imikoreshereze.guhuza import Guhuza, UburyoGuhuza
from ibiro.imikoreshereze.ububiko import UbubikoPorogaramu


class TestIkora:
    def test_kora(self):
        ik = Ikora(42)
        assert ik.agaciro == 42

    def test_shira_agaciro(self):
        ik = Ikora(0)
        ik.agaciro = 10
        assert ik.agaciro == 10

    def test_ku_mpinduka(self):
        ibintu = []
        ik = Ikora(0)
        ik.ku_mpinduka(lambda v: ibintu.append(v))
        ik.agaciro = 5
        assert ibintu == [5]


class TestIbaze:
    def test_ibarwa(self):
        a = Ikora(2)
        b = Ikora(3)
        total = Ibaze(lambda: a.agaciro + b.agaciro, [a, b])
        assert total.agaciro == 5


class TestIcyegeranyo:
    def test_kongera(self):
        ic = Icyegeranyo()
        ic.kongera("a")
        assert len(ic) == 1

    def test_kuraho(self):
        ic = Icyegeranyo([1, 2, 3])
        ic.kuraho(2)
        assert list(ic) == [1, 3]


class TestUbubikoPorogaramu:
    def test_kora(self):
        ub = UbubikoPorogaramu()
        assert ub is not None

    def test_shira_shaka(self):
        ub = UbubikoPorogaramu()
        ub.shira("urufunguzo", "agaciro")
        assert ub.shaka("urufunguzo") == "agaciro"

    def test_afite(self):
        ub = UbubikoPorogaramu()
        assert not ub.afite("ntibaho")
        ub.shira("a", 1)
        assert ub.afite("a")

    def test_kuraho(self):
        ub = UbubikoPorogaramu()
        ub.shira("x", 1)
        ub.kuraho("x")
        assert not ub.afite("x")

    def test_kira(self):
        ub = UbubikoPorogaramu()
        ub.shira("a", 1)
        ub.shira("b", 2)
        ub.kira()
        assert not ub.afite("a")
        assert not ub.afite("b")
