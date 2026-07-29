"""Ibizamini by'Imiterere — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.imiterere.shingiro import Imiterere, Guringaniza, Icyerekezo
from ibiro.imiterere.umurongo import Umurongo
from ibiro.imiterere.inkingi import Inkingi
from ibiro.imiterere.urusenya import Urusenya
from ibiro.imiterere.ikirundo import Ikirundo
from ibiro.ibikoresho.ikoresho import Ikoresho


class TestImiterere:
    def test_kongera_ikoresho(self):
        im = Imiterere()
        ik = Ikoresho("ik1")
        im.kongera(ik)
        assert ik in im.abana

    def test_kuraho_ikoresho(self):
        im = Imiterere()
        ik = Ikoresho("ik1")
        im.kongera(ik)
        im.kuraho(ik)
        assert ik not in im.abana


class TestUmurongo:
    def test_kora(self):
        um = Umurongo()
        assert um.icyerekezo == Icyerekezo.HORIZONTAL

    def test_kongera_ibiri(self):
        um = Umurongo()
        um.kongera(Ikoresho("a"))
        um.kongera(Ikoresho("b"))
        assert len(um.abana) == 2


class TestInkingi:
    def test_kora(self):
        ink = Inkingi()
        assert ink.icyerekezo == Icyerekezo.VERTICAL

    def test_kongera_ikoresho(self):
        ink = Inkingi()
        ink.kongera(Ikoresho("a"))
        assert len(ink.abana) == 1


class TestUrusenya:
    def test_kora(self):
        ur = Urusenya(imirongo=3, inkingi=4)
        assert ur.imirongo == 3
        assert ur.inkingi == 4

    def test_shyira_ikoresho(self):
        ur = Urusenya(imirongo=2, inkingi=2)
        ik = Ikoresho("ik1")
        ur.shyira(ik, umurongo=0, inkingi=0)
        assert ik in ur.abana


class TestIkirundo:
    def test_kora(self):
        ik = Ikirundo()
        ik.kongera(Ikoresho("a"))
        ik.kongera(Ikoresho("b"))
        assert len(ik.abana) == 2
