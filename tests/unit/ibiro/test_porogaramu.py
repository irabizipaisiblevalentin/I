"""Ibizamini bya Porogaramu — IBIRO."""

from __future__ import annotations

import pytest
from ibiro import umubare_verisiyo, Porogaramu


def test_ibiro_itanzwe():
    assert Porogaramu is not None


def test_umubare_verisiyo():
    assert isinstance(umubare_verisiyo, str)
    assert umubare_verisiyo == "0.1.0"


class TestPorogaramu:
    def test_itangira(self):
        p = Porogaramu("porogaramu-ya", "ikizamini.org")
        assert p.izina == "porogaramu-ya"
        assert p.umuryango == "ikizamini.org"

    def test_itangira_mburabura(self):
        p = Porogaramu("porogaramu-ya", "ikizamini.org")
        assert p.uyobore_idirishya is not None

    def test_genda_garura_int(self):
        p = Porogaramu("porogaramu-ya", "ikizamini.org")
        igisubizo = p.genda()
        assert isinstance(igisubizo, int)
